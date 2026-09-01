"""
SatyaKavach — Build Balanced Dataset
Samples a balanced real/fake split from the downloaded combined dataset
and organizes into train/val/test directories for the training scripts.

Strategy (best accuracy for the time budget):
  - Balance classes 1:1 to prevent majority-class bias
  - Keep a large, diverse training set (40k real + 40k fake)
  - Hold out a clean, balanced test set (5k + 5k) never seen during training
"""

import random
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from training.configs.train_config import DATASETS_DIR

SEED = 42
SRC = DATASETS_DIR / "combined"
OUT = DATASETS_DIR / "balanced"

# Budgets (real, fake) per split — 10K/class train for 6GB GPU training
SPLITS = {
    "train": (10000, 10000),
    "val": (1000, 1000),
    "test": (1000, 1000),
}


def collect(src: Path, cls: str):
    d = src / cls
    return sorted(p for p in d.glob("*.jpg") if p.is_file())


def main():
    random.seed(SEED)

    real_files = collect(SRC, "real")
    fake_files = collect(SRC, "fake")
    print(f"Source: real={len(real_files)}, fake={len(fake_files)}")

    # Shuffle each class
    random.shuffle(real_files)
    random.shuffle(fake_files)

    real_ptr, fake_ptr = 0, 0
    totals = {"real": 0, "fake": 0}

    for split, (n_real, n_fake) in SPLITS.items():
        for cls, n in (("real", n_real), ("fake", n_fake)):
            src_list = real_files if cls == "real" else fake_files
            ptr = real_ptr if cls == "real" else fake_ptr
            chosen = src_list[ptr:ptr + n]
            if cls == "real":
                real_ptr += n
            else:
                fake_ptr += n

            out_dir = OUT / split / cls
            out_dir.mkdir(parents=True, exist_ok=True)
            for src_path in chosen:
                dst = out_dir / src_path.name
                if not dst.exists():
                    shutil.copy2(src_path, dst)
            totals[cls] += n
            print(f"  {split}/{cls}: {n} -> {out_dir}")

    print(f"\nBalanced dataset ready at {OUT}")
    print(f"  real total: {totals['real']}, fake total: {totals['fake']}")


if __name__ == "__main__":
    main()