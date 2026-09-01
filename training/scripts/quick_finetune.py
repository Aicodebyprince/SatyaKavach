"""
SatyaKavach - Quick Fine-Tune for Hackathon
Fine-tunes on a small subset (2000 images) for fast improvement.
"""
import os
import sys
import time
import json
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from torchvision import transforms
from PIL import Image

BACKEND_MODELS_DIR = PROJECT_ROOT / "backend" / "app" / "services" / "ai" / "model_weights"
DATASETS_DIR = PROJECT_ROOT / "training" / "datasets" / "combined"


class SimpleDeepfakeDataset(torch.utils.data.Dataset):
    """Load real/fake images from combined/ directory."""
    def __init__(self, root_dir, transform=None, max_per_class=1000):
        self.transform = transform
        self.samples = []
        
        real_dir = Path(root_dir) / "real"
        fake_dir = Path(root_dir) / "fake"
        
        real_files = sorted(os.listdir(real_dir))[:max_per_class]
        fake_files = sorted(os.listdir(fake_dir))[:max_per_class]
        
        for f in real_files:
            self.samples.append((str(real_dir / f), 0))  # 0 = real
        for f in fake_files:
            self.samples.append((str(fake_dir / f), 1))  # 1 = fake
        
        print(f"  Loaded {len(self.samples)} images ({len(real_files)} real, {len(fake_files)} fake)")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label


def fine_tune_model(model_name="efficientnet", epochs=8, lr=3e-4, batch_size=32, max_images=2000):
    """Quick fine-tune a pre-trained model on deepfake dataset."""
    print("=" * 60)
    print(f"Quick Fine-Tune: {model_name} ({epochs} epochs, {max_images} images)")
    print("=" * 60)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    
    # Transforms
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    
    # Dataset
    print("\nLoading dataset...")
    full_dataset = SimpleDeepfakeDataset(DATASETS_DIR, transform=train_transform, max_per_class=max_images // 2)
    val_dataset = SimpleDeepfakeDataset(DATASETS_DIR, transform=val_transform, max_per_class=max_images // 2)
    
    total = len(full_dataset)
    train_size = int(0.8 * total)
    val_size = total - train_size
    
    train_dataset = Subset(full_dataset, list(range(train_size)))
    val_dataset = Subset(val_dataset, list(range(train_size, total)))
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    
    print(f"  Train: {train_size}, Val: {val_size}")
    
    # Load model
    print(f"\nLoading {model_name}...")
    if model_name == "efficientnet":
        import torchvision.models as models
        model = models.efficientnet_b4(weights=models.EfficientNet_B4_Weights.IMAGENET1K_V1)
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(0.3), nn.Linear(in_features, 256), nn.ReLU(), nn.Dropout(0.2), nn.Linear(256, 2)
        )
        output_name = "efficientnet_b4_deepfake.onnx"
    else:
        import timm
        model = timm.create_model("xception", pretrained=True, num_classes=2)
        output_name = "xception_deepfake.onnx"
    
    model = model.to(device)
    
    # Only fine-tune classifier head + last few layers
    # Freeze backbone, only train classifier
    if model_name == "efficientnet":
        for param in model.features.parameters():
            param.requires_grad = False
        for param in model.classifier.parameters():
            param.requires_grad = True
    else:
        # For xception, freeze all but last layers
        params = list(model.parameters())
        for param in params[:-10]:
            param.requires_grad = False
    
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"  Parameters: {total_params:,} total, {trainable:,} trainable")
    
    # Optimizer - higher LR since most layers frozen
    optimizer = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=lr, weight_decay=0.01)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    
    # Training
    best_acc = 0.0
    print(f"\nTraining for {epochs} epochs...")
    print("-" * 60)
    
    for epoch in range(epochs):
        start = time.time()
        
        # Train
        model.train()
        train_loss, correct, total = 0.0, 0, 0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_loss += loss.item() * images.size(0)
            _, pred = outputs.max(1)
            total += labels.size(0)
            correct += pred.eq(labels).sum().item()
        
        train_acc = 100. * correct / total
        train_loss /= total
        
        # Validate
        model.eval()
        val_loss, correct, total = 0.0, 0, 0
        all_preds, all_labels = [], []
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * images.size(0)
                _, pred = outputs.max(1)
                total += labels.size(0)
                correct += pred.eq(labels).sum().item()
                all_preds.extend(pred.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        val_acc = 100. * correct / total
        val_loss /= total
        elapsed = time.time() - start
        
        scheduler.step()
        
        # Metrics
        import numpy as np
        preds = np.array(all_preds)
        lbls = np.array(all_labels)
        tp = ((preds == 1) & (lbls == 1)).sum()
        fp = ((preds == 1) & (lbls == 0)).sum()
        fn = ((preds == 0) & (lbls == 1)).sum()
        precision = tp / (tp + fp + 1e-8)
        recall = tp / (tp + fn + 1e-8)
        f1 = 2 * precision * recall / (precision + recall + 1e-8)
        
        star = " *" if val_acc > best_acc else ""
        print(f"  Epoch {epoch+1}/{epochs} | Train: {train_acc:.1f}% | Val: {val_acc:.1f}% | P: {precision:.3f} R: {recall:.3f} F1: {f1:.3f} | {elapsed:.1f}s{star}")
        
        if val_acc > best_acc:
            best_acc = val_acc
            best_preds = preds.copy()
            best_labels = lbls.copy()
            torch.save(model.state_dict(), BACKEND_MODELS_DIR / f"best_{model_name}.pth")
    
    # Export to ONNX
    print("\nExporting to ONNX...")
    model.load_state_dict(torch.load(BACKEND_MODELS_DIR / f"best_{model_name}.pth", map_location=device))
    model.eval()
    dummy = torch.randn(1, 3, 224, 224).to(device)
    torch.onnx.export(
        model, dummy, str(BACKEND_MODELS_DIR / output_name),
        input_names=["image"], output_names=["logits"],
        dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=17,
    )
    
    # Copy to backend
    size_mb = (BACKEND_MODELS_DIR / output_name).stat().st_size / 1024 / 1024
    print(f"  Exported: {output_name} ({size_mb:.1f} MB)")
    
    # Cleanup temp file
    temp_path = BACKEND_MODELS_DIR / f"best_{model_name}.pth"
    if temp_path.exists():
        temp_path.unlink()
    
    # Final metrics
    tp = ((best_preds == 1) & (best_labels == 1)).sum()
    fp = ((best_preds == 1) & (best_labels == 0)).sum()
    fn = ((best_preds == 0) & (best_labels == 1)).sum()
    tn = ((best_preds == 0) & (best_labels == 0)).sum()
    
    print(f"\n{'=' * 60}")
    print(f"BEST VAL ACCURACY: {best_acc:.1f}%")
    print(f"Confusion: TP={tp} FP={fp} FN={fn} TN={tn}")
    print(f"{'=' * 60}")
    
    return best_acc


if __name__ == "__main__":
    print("SatyaKavach - Quick Fine-Tune for Hackathon")
    print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}\n")
    
    # Fine-tune EfficientNet (primary model)
    acc1 = fine_tune_model("efficientnet", epochs=8, lr=3e-4, batch_size=32, max_images=2000)
    
    # Fine-tune XceptionNet (secondary model)
    acc2 = fine_tune_model("xception", epochs=8, lr=3e-4, batch_size=32, max_images=2000)
    
    print(f"\n{'=' * 60}")
    print(f"FINAL RESULTS")
    print(f"  EfficientNet-B4: {acc1:.1f}%")
    print(f"  XceptionNet: {acc2:.1f}%")
    print(f"  Ensemble: {(acc1 + acc2) / 2:.1f}% (expected)")
    print(f"{'=' * 60}")
    print("DONE - Models exported to model_weights/")
