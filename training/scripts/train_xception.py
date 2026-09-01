"""
SatyaKavach — XceptionNet Deepfake Detector Training
Fine-tunes XceptionNet on FaceForensics++ / Celeb-DF / synthetic dataset.

Usage:
    python -m training.scripts.train_xception --dataset synthetic --epochs 30
"""
import os
import sys
import time
import json
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torch.cuda.amp import autocast, GradScaler

from training.configs.train_config import (
    XceptionConfig, DATASETS_DIR, MODELS_DIR, BACKEND_MODELS_DIR
)
from training.scripts.download_datasets import (
    DeepfakeDataset, get_train_transforms, get_val_transforms
)


def get_model(num_classes: int = 2, pretrained: bool = True):
    """Load XceptionNet with custom classification head."""
    try:
        import timm
    except ImportError:
        os.system("pip install timm")
        import timm

    model = timm.create_model("xception", pretrained=pretrained, num_classes=num_classes)
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
    """Validate and return loss + accuracy + metrics."""
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
    accuracy = 100. * correct / total

    return total_loss / total, accuracy, {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "confusion_matrix": {"tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn)}
    }


def export_to_onnx(model, output_path: Path, image_size: int = 224):
    """Export trained model to ONNX."""
    model.eval()
    device = next(model.parameters()).device
    dummy = torch.randn(1, 3, image_size, image_size).to(device)
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
    parser = argparse.ArgumentParser(description="Train XceptionNet for deepfake detection")
    parser.add_argument("--dataset", type=str, default="synthetic",
                       choices=["synthetic", "faceforensicspp", "celebdf"])
    parser.add_argument("--dataset-path", type=str, default=None)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--accum-steps", type=int, default=4,
                        help="Gradient accumulation steps (effective batch = batch_size * accum_steps)")
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--no-amp", action="store_true")
    args = parser.parse_args()

    config = XceptionConfig()
    config.epochs = args.epochs
    config.batch_size = args.batch_size
    config.gradient_accumulation_steps = args.accum_steps
    config.learning_rate = args.lr
    config.image_size = args.image_size

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
            print("Creating synthetic dataset...")
            from training.scripts.download_datasets import create_synthetic_dataset
            create_synthetic_dataset(data_root, num_images=5000)
    else:
        data_root = DATASETS_DIR / args.dataset

    print(f"Dataset: {data_root}")

    train_transforms = get_train_transforms(config.image_size)
    val_transforms = get_val_transforms(config.image_size)
    full_dataset = DeepfakeDataset(data_root, transform=train_transforms)

    total = len(full_dataset)
    train_size = int(0.8 * total)
    val_size = int(0.1 * total)
    test_size = total - train_size - val_size

    # Check for balanced dataset splits first
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

    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=config.batch_size, shuffle=False, num_workers=0)

    # Model
    print("\nLoading XceptionNet...")
    model = get_model(num_classes=config.num_classes, pretrained=config.pretrained)
    model = model.to(device)
    param_count = sum(p.numel() for p in model.parameters())
    print(f"Parameters: {param_count:,}")

    criterion = nn.CrossEntropyLoss(label_smoothing=config.label_smoothing)
    optimizer = optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.epochs - config.warmup_epochs)
    scaler = GradScaler() if (device.type == "cuda" and not args.no_amp) else None
    use_amp = scaler is not None

    config.output_dir.mkdir(parents=True, exist_ok=True)
    best_val_acc = 0.0
    best_metrics = {}
    patience_counter = 0
    history = []

    print(f"\nTraining XceptionNet for {config.epochs} epochs...")
    print("=" * 60)

    for epoch in range(config.epochs):
        epoch_start = time.time()
        print(f"\nEpoch {epoch+1}/{config.epochs} (lr: {optimizer.param_groups[0]['lr']:.6f})")

        # Warmup: freeze backbone
        if epoch < config.warmup_epochs:
            for param in model.parameters():
                param.requires_grad = False
            # Only train the final classifier
            for param in model.fc.parameters():
                param.requires_grad = True
            print("  [Warmup] Backbone frozen")
        else:
            for param in model.parameters():
                param.requires_grad = True

        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, scaler, device, use_amp,
                                                 accum_steps=config.gradient_accumulation_steps)
        val_loss, val_acc, val_metrics = validate(model, val_loader, criterion, device)
        epoch_time = time.time() - epoch_start

        print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.1f}%")
        print(f"  Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.1f}%")
        print(f"  P: {val_metrics['precision']:.3f} | R: {val_metrics['recall']:.3f} | F1: {val_metrics['f1']:.3f}")

        scheduler.step()

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_metrics = val_metrics
            patience_counter = 0
            torch.save({
                "model_state_dict": model.state_dict(),
                "epoch": epoch,
                "val_acc": val_acc,
                "val_metrics": val_metrics,
                "config": {"model_name": config.model_name, "num_classes": config.num_classes, "image_size": config.image_size},
            }, config.output_dir / "best_model.pth")
            print(f"  ★ Best model saved ({val_acc:.1f}%)")
        else:
            patience_counter += 1
            if patience_counter >= config.early_stopping_patience:
                print(f"\n  Early stopping at epoch {epoch+1}")
                break

        history.append({"epoch": epoch+1, "train_loss": train_loss, "train_acc": train_acc,
                        "val_loss": val_loss, "val_acc": val_acc, "metrics": val_metrics,
                        "lr": optimizer.param_groups[0]["lr"], "time": epoch_time})

    # Save history
    with open(config.output_dir / "training_history.json", "w") as f:
        json.dump(history, f, indent=2)

    # Export to ONNX
    print("\nExporting best model to ONNX...")
    checkpoint = torch.load(config.output_dir / "best_model.pth", map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    export_to_onnx(model, config.output_dir / "xception_deepfake.onnx", config.image_size)

    # Copy PyTorch + ONNX to backend
    BACKEND_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy2(config.output_dir / "xception_deepfake.onnx", BACKEND_MODELS_DIR / "xception_deepfake.onnx")
    shutil.copy2(config.output_dir / "best_model.pth", BACKEND_MODELS_DIR / "best_xception.pth")
    print(f"  Copied ONNX to: {BACKEND_MODELS_DIR / 'xception_deepfake.onnx'}")
    print(f"  Copied PyTorch to: {BACKEND_MODELS_DIR / 'best_xception.pth'}")

    with open(config.output_dir / "metrics.json", "w") as f:
        json.dump({"best_val_acc": best_val_acc, "best_metrics": best_metrics,
                    "epochs_trained": len(history)}, f, indent=2)

    print(f"\n{'='*60}")
    print(f"DONE — Best Val Acc: {best_val_acc:.1f}% | F1: {best_metrics.get('f1', 0):.3f}")
    print(f"Model: {config.output_dir}")


if __name__ == "__main__":
    main()
