"""
SatyaKavach — Download Real Datasets for Training
Downloads: 140k Real-and-Fake-Faces + Celeb-DF v2
Saves to training/datasets/ in real/ and fake/ subdirectories.
"""

import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from training.configs.train_config import DATASETS_DIR

DATASET_140k = "TheKernel01/140k-Real-and-Fake-Faces"
DATASET_CELEBDF = "thenewsupercell/celeb-df-image-dataset"


def download_split(dataset_name: str, split: str, output_dir: Path, label_map: dict, max_images: int = None):
    """Download a dataset split and save images to output_dir/real/ and output_dir/fake/."""
    from datasets import load_dataset

    (output_dir / "real").mkdir(parents=True, exist_ok=True)
    (output_dir / "fake").mkdir(parents=True, exist_ok=True)

    ds = load_dataset(dataset_name, split=split, streaming=True)

    real_count = 0
    fake_count = 0
    start = time.time()

    for i, sample in enumerate(ds):
        if max_images and i >= max_images:
            break

        label = sample["label"]
        class_name = label_map[label]
        image = sample["image"]

        target_dir = output_dir / class_name
        filename = f"{dataset_name.replace('/', '_')}_{split}_{i:06d}.jpg"
        image.save(target_dir / filename, quality=92)

        if class_name == "real":
            real_count += 1
        else:
            fake_count += 1

        if (i + 1) % 500 == 0:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed
            print(f"  [{dataset_name}/{split}] {i+1} images ({rate:.0f}/s) | real={real_count} fake={fake_count}")

    return real_count, fake_count


def main():
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    output_dir = DATASETS_DIR / "combined"
    print(f"Saving to: {output_dir}")
    print("=" * 60)

    # 140k dataset: label 0=real, 1=fake
    print("\n1. Downloading 140k Real-and-Fake-Faces...")
    print("-" * 40)
    r1, f1 = download_split(
        DATASET_140k, "train", output_dir,
        label_map={0: "real", 1: "fake"},
    )
    r1v, f1v = download_split(
        DATASET_140k, "validation", output_dir,
        label_map={0: "real", 1: "fake"},
    )
    r1t, f1t = download_split(
        DATASET_140k, "test", output_dir,
        label_map={0: "real", 1: "fake"},
    )
    print(f"  140k: real={r1+r1v+r1t}, fake={f1+f1v+f1t}")

    # Celeb-DF: label 0=Fake, 1=Real
    print("\n2. Downloading Celeb-DF v2 image dataset...")
    print("-" * 40)
    r2, f2 = download_split(
        DATASET_CELEBDF, "train", output_dir,
        label_map={0: "fake", 1: "real"},
    )
    r2v, f2v = download_split(
        DATASET_CELEBDF, "validation", output_dir,
        label_map={0: "fake", 1: "real"},
    )
    r2t, f2t = download_split(
        DATASET_CELEBDF, "test", output_dir,
        label_map={0: "fake", 1: "real"},
    )
    print(f"  Celeb-DF: real={r2+r2v+r2t}, fake={f2+f2v+f2t}")

    total_real = r1 + r1v + r1t + r2 + r2v + r2t
    total_fake = f1 + f1v + f1t + f2 + f2v + f2t
    print("=" * 60)
    print(f"DOWNLOAD COMPLETE")
    print(f"  Total real: {total_real}")
    print(f"  Total fake: {total_fake}")
    print(f"  Total: {total_real + total_fake}")
    print(f"  Location: {output_dir}")


if __name__ == "__main__":
    main()