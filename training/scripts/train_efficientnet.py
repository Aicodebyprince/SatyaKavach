"""
SatyaKavach — EfficientNet-B4 Deepfake Detector Training
Fine-tunes EfficientNet-B4 on FaceForensics++ / synthetic dataset.

Usage:
    python -m training.scripts.train_efficientnet --dataset synthetic --epochs 25
    python -m training.scripts.train_efficientnet --dataset faceforensicspp --epochs 25
"""
import os
import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torch.cuda.amp import autocast, GradScaler

from training.configs.train_config import (
    EfficientNetConfig, DATASETS_DIR, MODELS_DIR, BACKEND_MODELS_DIR
)
from training.scripts.download_datasets import (
    DeepfakeDataset, get_train_transforms, get_val_transforms
)


def get_model(num_classes: int = 2, pretrained: bool = True):
    """Load EfficientNet-B4 with transfer learning head."""
    try:
        import torchvision.models as models
    except ImportError:
        os.system("pip install torchvision")
        import torchvision.models as models

    if pretrained:
        weights = models.EfficientNet_B4_Weights.IMAGENET1K_V1
        model = models.efficientnet_b4(weights=weights)
    else:
        model = models.efficientnet_b4(weights=None)

    # Replace classifier head for binary deepfake detection
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(in_features, 256),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.2),
        nn.Linear(256, num_classes),
    )

    return model


def train_one_epoch(model, loader, criterion, optimizer, scaler, device, use_amp=True, accum_steps=1):
    """Train for one epoch with optional mixed precision and gradient accumulation."""
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0
    optimizer.zero_grad(set_to_none=True)

    for batch_idx, (images, labels) in enumerate(loader):
        images, labels = images.to(device), labels.to(device)
        is_accum_last = (batch_idx + 1) % accum_steps == 0 or (batch_idx + 1) == len(loader)

        if use_amp and device.type == "cuda":
            with autocast():
                outputs = model(images)
                loss = criterion(outputs, labels) / accum_steps
            scaler.scale(loss).backward()
        else:
            outputs = model(images)
            loss = criterion(outputs, labels) / accum_steps
            loss.backward()

        if is_accum_last:
            if use_amp and device.type == "cuda":
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                scaler.step(optimizer)
                scaler.update()
            else:
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
            optimizer.zero_grad(set_to_none=True)

        total_loss += loss.item() * accum_steps * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

        if (batch_idx + 1) % 20 == 0:
            print(f"    Batch {batch_idx+1}/{len(loader)} | Loss: {loss.item() * accum_steps:.4f} | Acc: {100.*correct/total:.1f}%")

    return total_loss / total, 100. * correct / total


def validate(model, loader, criterion, device):
    """Validate and return loss + accuracy."""
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    accuracy = 100. * correct / total
    
    # Compute per-class metrics
    import numpy as np
    preds = np.array(all_preds)
    lbls = np.array(all_labels)
    
    tp = ((preds == 1) & (lbls == 1)).sum()
    fp = ((preds == 1) & (lbls == 0)).sum()
    fn = ((preds == 0) & (lbls == 1)).sum()
    tn = ((preds == 0) & (lbls == 0)).sum()
    
    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)
    f1 = 2 * precision * recall / (precision + recall + 1e-8)

    return total_loss / total, accuracy, {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "confusion_matrix": {"tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn)}
    }


def export_to_onnx(model, output_path: Path, image_size: int = 224):
    """Export trained model to ONNX for fast inference."""
    model.eval()
    dummy = torch.randn(1, 3, image_size, image_size).to(next(model.parameters()).device)
    
    torch.onnx.export(
        model, dummy, str(output_path),
        input_names=["image"],
        output_names=["logits"],
        dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=17,
    )
    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"  ONNX exported: {output_path} ({size_mb:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Train EfficientNet-B4 for deepfake detection")
    parser.add_argument("--dataset", type=str, default="synthetic",
                       choices=["synthetic", "faceforensicspp", "celebdf"],
                       help="Dataset to train on")
    parser.add_argument("--dataset-path", type=str, default=None,
                       help="Custom dataset path (must have real/ and fake/ subdirs)")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--accum-steps", type=int, default=4,
                        help="Gradient accumulation steps (effective batch = batch_size * accum_steps)")
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--no-amp", action="store_true", help="Disable mixed precision")
    args = parser.parse_args()

    config = EfficientNetConfig()
    config.epochs = args.epochs
    config.batch_size = args.batch_size
    config.gradient_accumulation_steps = args.accum_steps
    config.learning_rate = args.lr
    config.image_size = args.image_size

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if device.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

    # Dataset
    if args.dataset_path:
        data_root = Path(args.dataset_path)
    elif args.dataset == "synthetic":
        data_root = DATASETS_DIR / "synthetic"
        if not data_root.exists():
            print("Synthetic dataset not found. Creating...")
            from training.scripts.download_datasets import create_synthetic_dataset
            create_synthetic_dataset(data_root, num_images=5000)
    else:
        data_root = DATASETS_DIR / args.dataset

    print(f"Dataset: {data_root}")

    # Check for balanced dataset splits first, fall back to combined
    balanced_dir = DATASETS_DIR / "balanced"
    if (balanced_dir / "train" / "real").exists() and (balanced_dir / "train" / "fake").exists():
        print(f"Using balanced dataset from {balanced_dir}")
        train_dataset = DeepfakeDataset(balanced_dir / "train", transform=get_train_transforms(config.image_size))
        val_dataset = DeepfakeDataset(balanced_dir / "val", transform=get_val_transforms(config.image_size))
        test_dataset = DeepfakeDataset(balanced_dir / "test", transform=get_val_transforms(config.image_size))
    else:
        print(f"Using combined dataset from {data_root}")
        full_dataset = DeepfakeDataset(data_root, transform=get_train_transforms(config.image_size))
        total = len(full_dataset)
        train_size = int(0.8 * total)
        val_size = int(0.1 * total)
        test_size = total - train_size - val_size
        train_dataset, val_dataset, test_dataset = random_split(
            full_dataset, [train_size, val_size, test_size],
            generator=torch.Generator().manual_seed(42)
        )
        val_dataset.dataset = DeepfakeDataset(data_root, transform=get_val_transforms(config.image_size))
        test_dataset.dataset = DeepfakeDataset(data_root, transform=get_val_transforms(config.image_size))

    print(f"Train: {len(train_dataset)} | Val: {len(val_dataset)} | Test: {len(test_dataset)}")
    print(f"Effective batch size: {config.batch_size} x {config.gradient_accumulation_steps} = {config.batch_size * config.gradient_accumulation_steps}")

    train_loader = DataLoader(
        train_dataset, batch_size=config.batch_size, shuffle=True,
        num_workers=0, pin_memory=(device.type == "cuda")
    )
    val_loader = DataLoader(
        val_dataset, batch_size=config.batch_size, shuffle=False,
        num_workers=0, pin_memory=(device.type == "cuda")
    )

    # Model
    print("\nLoading EfficientNet-B4...")
    model = get_model(num_classes=config.num_classes, pretrained=config.pretrained)
    model = model.to(device)
    
    param_count = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Parameters: {param_count:,} total, {trainable:,} trainable")

    # Loss, optimizer, scheduler
    criterion = nn.CrossEntropyLoss(label_smoothing=config.label_smoothing)
    optimizer = optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    
    if config.scheduler == "cosine":
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.epochs - config.warmup_epochs)
    elif config.scheduler == "plateau":
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", patience=3, factor=0.5)
    else:
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

    scaler = GradScaler() if (device.type == "cuda" and not args.no_amp) else None
    use_amp = scaler is not None

    # Training loop
    config.output_dir.mkdir(parents=True, exist_ok=True)
    best_val_acc = 0.0
    best_metrics = {}
    patience_counter = 0
    history = []

    print(f"\nTraining EfficientNet-B4 for {config.epochs} epochs...")
    print("=" * 60)

    for epoch in range(config.epochs):
        epoch_start = time.time()
        print(f"\nEpoch {epoch+1}/{config.epochs} (lr: {optimizer.param_groups[0]['lr']:.6f})")

        # Warmup: freeze backbone for first few epochs
        if epoch < config.warmup_epochs:
            for param in model.features.parameters():
                param.requires_grad = False
            print("  [Warmup] Backbone frozen")
        else:
            for param in model.features.parameters():
                param.requires_grad = True

        # Train
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, scaler, device, use_amp,
            accum_steps=config.gradient_accumulation_steps
        )

        # Validate
        val_loss, val_acc, val_metrics = validate(model, val_loader, criterion, device)

        epoch_time = time.time() - epoch_start

        print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.1f}%")
        print(f"  Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.1f}%")
        print(f"  Precision: {val_metrics['precision']:.3f} | Recall: {val_metrics['recall']:.3f} | F1: {val_metrics['f1']:.3f}")
        print(f"  Time: {epoch_time:.1f}s")

        # Scheduler step
        if isinstance(scheduler, optim.lr_scheduler.ReduceLROnPlateau):
            scheduler.step(val_acc)
        elif epoch >= config.warmup_epochs:
            scheduler.step()

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_metrics = val_metrics
            patience_counter = 0
            
            torch.save({
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "epoch": epoch,
                "val_acc": val_acc,
                "val_metrics": val_metrics,
                "config": {
                    "model_name": config.model_name,
                    "num_classes": config.num_classes,
                    "image_size": config.image_size,
                },
            }, config.output_dir / "best_model.pth")
            print(f"  ★ New best model saved (val_acc: {val_acc:.1f}%)")
        else:
            patience_counter += 1
            if patience_counter >= config.early_stopping_patience:
                print(f"\n  Early stopping at epoch {epoch+1} (no improvement for {config.early_stopping_patience} epochs)")
                break

        history.append({
            "epoch": epoch + 1,
            "train_loss": train_loss,
            "train_acc": train_acc,
            "val_loss": val_loss,
            "val_acc": val_acc,
            "metrics": val_metrics,
            "lr": optimizer.param_groups[0]["lr"],
            "time": epoch_time,
        })

    # Save training history
    with open(config.output_dir / "training_history.json", "w") as f:
        json.dump(history, f, indent=2)

    # Export best model to ONNX
    print("\n" + "=" * 60)
    print("Exporting best model to ONNX...")
    checkpoint = torch.load(config.output_dir / "best_model.pth", map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    export_to_onnx(model, config.output_dir / "efficientnet_b4_deepfake.onnx", config.image_size)

    # Copy PyTorch model + ONNX to backend model weights
    BACKEND_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy2(
        config.output_dir / "efficientnet_b4_deepfake.onnx",
        BACKEND_MODELS_DIR / "efficientnet_b4_deepfake.onnx"
    )
    shutil.copy2(
        config.output_dir / "best_model.pth",
        BACKEND_MODELS_DIR / "best_efficientnet.pth"
    )
    print(f"  Copied ONNX to: {BACKEND_MODELS_DIR / 'efficientnet_b4_deepfake.onnx'}")
    print(f"  Copied PyTorch to: {BACKEND_MODELS_DIR / 'best_efficientnet.pth'}")

    # Save metrics
    with open(config.output_dir / "metrics.json", "w") as f:
        json.dump({
            "best_val_acc": best_val_acc,
            "best_metrics": best_metrics,
            "epochs_trained": len(history),
            "total_time": sum(h["time"] for h in history),
        }, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"TRAINING COMPLETE")
    print(f"{'=' * 60}")
    print(f"Best Val Accuracy: {best_val_acc:.1f}%")
    print(f"Precision: {best_metrics.get('precision', 0):.3f}")
    print(f"Recall: {best_metrics.get('recall', 0):.3f}")
    print(f"F1 Score: {best_metrics.get('f1', 0):.3f}")
    print(f"Model saved to: {config.output_dir}")


if __name__ == "__main__":
    main()
