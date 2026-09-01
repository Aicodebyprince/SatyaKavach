"""
SatyaKavach — Build Manifest (no file copying)
Creates train.csv / val.csv / test.csv pointing to original files
in combined/real/ and combined/fake/ — balanced 1:1 per split.
"""

import csv
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from training.configs.train_config import DATASETS_DIR

SEED = 42
SRC = DATASETS_DIR / "combined"
OUT = DATASETS_DIR / "manifest"

SPLITS = {
    "train": (10000, 10000),
    "val": (1000, 1000),
    "test": (1000, 1000),
}


def collect(src: Path, cls: str):
    d = src / cls
    return sorted(f.resolve() for f in d.iterdir() if f.suffix in (".jpg", ".png"))


def main():
    random.seed(SEED)
    OUT.mkdir(parents=True, exist_ok=True)

    real_files = collect(SRC, "real")
    fake_files = collect(SRC, "fake")
    print(f"Source: real={len(real_files)}, fake={len(fake_files)}")

    random.shuffle(real_files)
    random.shuffle(fake_files)

    real_ptr, fake_ptr = 0, 0

    for split, (n_real, n_fake) in SPLITS.items():
        rows = []
        for cls, n, label in (("real", n_real, "0"), ("fake", n_fake, "1")):
            src_list = real_files if cls == "real" else fake_files
            ptr = real_ptr if cls == "real" else fake_ptr
            chosen = src_list[ptr:ptr + n]
            if cls == "real":
                real_ptr += n
            else:
                fake_ptr += n
            for p in chosen:
                rows.append((str(p), label))
        random.shuffle(rows)

        csv_path = OUT / f"{split}.csv"
        with open(csv_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["filepath", "label"])
            w.writerows(rows)
        print(f"  {split}.csv: {len(rows)} rows ({csv_path})")

    print(f"\nManifest ready at {OUT}")


if __name__ == "__main__":
    main()