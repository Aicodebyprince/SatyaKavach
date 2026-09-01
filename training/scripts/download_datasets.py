"""
SatyaKavach — Dataset Download & Preparation
Downloads FaceForensics++ and Celeb-DF v2 for deepfake detection training.

Usage:
    python -m training.scripts.download_datasets
"""
import os
import sys
import shutil
import hashlib
import argparse
import zipfile
import tarfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import torch
import torch.utils.data

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from training.configs.train_config import (
    DATASETS_DIR, DatasetConfig, BACKEND_MODELS_DIR
)


def download_file(url: str, dest: Path, desc: str = "") -> bool:
    """Download a file with progress indicator."""
    try:
        import requests
    except ImportError:
        os.system("pip install requests")
        import requests

    print(f"  Downloading {desc or url}...")
    try:
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))

        dest.parent.mkdir(parents=True, exist_ok=True)
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = (downloaded / total) * 100
                    print(f"\r  {pct:.1f}% ({downloaded // 1024 // 1024}MB/{total // 1024 // 1024}MB)", end="", flush=True)
        print()
        return True
    except Exception as e:
        print(f"  Failed: {e}")
        return False


def create_synthetic_dataset(output_dir: Path, num_images: int = 5000):
    """
    Create a synthetic deepfake training dataset for quick training.
    
    Real datasets (FaceForensics++, Celeb-DF) are 10-50GB and require
    manual download agreements. This creates a synthetic dataset with:
    - Real images: solid colors, gradients, noise patterns
    - Fake images: with deliberate artifacts (blur, noise, edge anomalies)
    
    Use this for快速验证 the training pipeline, then switch to real datasets.
    """
    try:
        from PIL import Image, ImageFilter, ImageDraw
        import numpy as np
    except ImportError:
        os.system("pip install Pillow numpy")
        from PIL import Image, ImageFilter, ImageDraw
        import numpy as np

    real_dir = output_dir / "real"
    fake_dir = output_dir / "fake"
    real_dir.mkdir(parents=True, exist_ok=True)
    fake_dir.mkdir(parents=True, exist_ok=True)

    print(f"Creating synthetic dataset ({num_images} images)...")

    for i in range(num_images):
        # Create a base image with random patterns
        img_array = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        
        # Add some structure (circles, rectangles)
        img = Image.fromarray(img_array)
        draw = ImageDraw.Draw(img)
        
        # Random shapes
        for _ in range(3):
            x1, y1 = np.random.randint(0, 180, 2)
            x2, y2 = x1 + np.random.randint(20, 80), y1 + np.random.randint(20, 80)
            color = tuple(np.random.randint(0, 256, 3))
            if np.random.random() > 0.5:
                draw.ellipse([x1, y1, x2, y2], fill=color)
            else:
                draw.rectangle([x1, y1, x2, y2], fill=color)

        if i < num_images // 2:
            # REAL: Clean, sharp images
            img.save(real_dir / f"real_{i:05d}.jpg", quality=95)
        else:
            # FAKE: Add manipulation artifacts
            fake_img = img.copy()
            
            # Artifact type 1: Gaussian blur (simulates face blending)
            if np.random.random() > 0.5:
                fake_img = fake_img.filter(ImageFilter.GaussianBlur(radius=2))
            
            # Artifact type 2: Noise injection
            if np.random.random() > 0.5:
                noise = np.random.normal(0, 25, (224, 224, 3)).astype(np.int16)
                noisy = np.clip(np.array(fake_img).astype(np.int16) + noise, 0, 255).astype(np.uint8)
                fake_img = Image.fromarray(noisy)
            
            # Artifact type 3: Color channel shift
            if np.random.random() > 0.5:
                arr = np.array(fake_img)
                shift = np.random.randint(-20, 20)
                arr[:, :, 0] = np.clip(arr[:, :, 0].astype(int) + shift, 0, 255).astype(np.uint8)
                fake_img = Image.fromarray(arr)
            
            fake_img.save(fake_dir / f"fake_{i:05d}.jpg", quality=85)

        if (i + 1) % 500 == 0:
            print(f"  Generated {i + 1}/{num_images} images")

    print(f"Dataset created: {real_dir} ({num_images//2} real), {fake_dir} ({num_images//2} fake)")
    return real_dir, fake_dir


class DeepfakeDataset(torch.utils.data.Dataset):
    """
    Generic deepfake dataset loader.
    Expects directory structure:
        root/
            real/  (authentic images)
            fake/  (manipulated images)
    """
    def __init__(self, root: Path, transform=None):
        self.root = Path(root)
        self.transform = transform
        self.samples = []

        for label_dir, label in [("real", 0), ("fake", 1)]:
            dir_path = self.root / label_dir
            if dir_path.exists():
                for img_path in dir_path.glob("*.jpg"):
                    self.samples.append((str(img_path), label))
                for img_path in dir_path.glob("*.png"):
                    self.samples.append((str(img_path), label))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        from PIL import Image
        path, label = self.samples[idx]
        image = Image.open(path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label


def get_train_transforms(image_size: int = 224):
    """Training data augmentations."""
    try:
        import torchvision.transforms as T
    except ImportError:
        os.system("pip install torchvision")
        import torchvision.transforms as T

    return T.Compose([
        T.Resize((image_size, image_size)),
        T.RandomHorizontalFlip(p=0.5),
        T.RandomVerticalFlip(p=0.1),
        T.RandomRotation(15),
        T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1, hue=0.05),
        T.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def get_val_transforms(image_size: int = 224):
    """Validation/test data transforms (no augmentation)."""
    try:
        import torchvision.transforms as T
    except ImportError:
        import torchvision.transforms as T

    return T.Compose([
        T.Resize((image_size, image_size)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download/prepare deepfake datasets")
    parser.add_argument("--synthetic", action="store_true", help="Create synthetic dataset for quick testing")
    parser.add_argument("--num-images", type=int, default=5000, help="Number of synthetic images")
    args = parser.parse_args()

    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    if args.synthetic:
        create_synthetic_dataset(DATASETS_DIR / "synthetic", args.num_images)
    else:
        print("=" * 60)
        print("FaceForensics++ Dataset")
        print("=" * 60)
        print("To download FaceForensics++:")
        print("  1. Go to https://github.com/ondyari/FaceForensics")
        print("  2. Follow the download instructions (requires agreement)")
        print(f"  3. Extract to: {DatasetConfig.ffpp_dir}")
        print()
        print("=" * 60)
        print("Celeb-DF v2 Dataset")
        print("=" * 60)
        print("To download Celeb-DF v2:")
        print("  1. Go to https://cse.buffalo.edu/~siweilyu/celeb-deepfakeforensics.html")
        print("  2. Fill out the request form")
        print(f"  3. Extract to: {DatasetConfig.celebdf_dir}")
        print()
        print("For quick testing, run with --synthetic flag:")
        print("  python -m training.scripts.download_datasets --synthetic")
