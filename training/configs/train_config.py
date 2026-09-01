"""
SatyaKavach — Training Configuration
All hyperpaths, paths, and dataset settings in one place.
"""
from pathlib import Path
from dataclasses import dataclass, field

# ── Paths ────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TRAINING_DIR = PROJECT_ROOT / "training"
DATASETS_DIR = TRAINING_DIR / "datasets"
MODELS_DIR = TRAINING_DIR / "models"

# Where trained models get exported for the backend
BACKEND_MODELS_DIR = PROJECT_ROOT / "backend" / "app" / "services" / "ai" / "model_weights"


@dataclass
class DatasetConfig:
    """Settings for dataset download and preprocessing."""
    # FaceForensics++ (image deepfakes)
    ffpp_dir: Path = DATASETS_DIR / "faceforensicspp"
    ffpp_url: str = "https://github.com/ondyari/FaceForensics"
    ffpp_quality: str = "c40"  # c40 = compressed (more realistic), c0 = original
    ffpp_methods: list[str] = field(default_factory=lambda: [
        "Deepfakes", "Face2Face", "FaceSwap", "NeuralTextures"
    ])

    # Celeb-DF v2 (high-quality face swaps)
    celebdf_dir: Path = DATASETS_DIR / "celebdf"
    celebdf_url: str = "https://cse.buffalo.edu/~siweilyu/celeb-deepfakeforensics.html"

    # Image settings
    image_size: int = 224  # EfficientNet-B4 default input
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    num_workers: int = 4


@dataclass
class EfficientNetConfig:
    """EfficientNet-B4 training settings."""
    model_name: str = "efficientnet_b4"
    pretrained: bool = True
    num_classes: int = 2  # real vs fake
    epochs: int = 25
    batch_size: int = 8
    gradient_accumulation_steps: int = 4  # effective batch = 32
    learning_rate: float = 1e-4
    weight_decay: float = 1e-4
    scheduler: str = "cosine"  # cosine, step, plateau
    warmup_epochs: int = 3
    mixed_precision: bool = True  # FP16 for speed on Nvidia GPU
    label_smoothing: float = 0.1
    early_stopping_patience: int = 5
    save_best_only: bool = True
    output_dir: Path = MODELS_DIR / "efficientnet_b4"


@dataclass
class XceptionConfig:
    """XceptionNet training settings."""
    model_name: str = "xception"
    pretrained: bool = True
    num_classes: int = 2
    epochs: int = 30
    batch_size: int = 8
    gradient_accumulation_steps: int = 4  # effective batch = 32
    learning_rate: float = 1e-4
    weight_decay: float = 1e-4
    scheduler: str = "cosine"
    warmup_epochs: int = 3
    mixed_precision: bool = True
    label_smoothing: float = 0.1
    early_stopping_patience: int = 5
    save_best_only: bool = True
    output_dir: Path = MODELS_DIR / "xception"


@dataclass
class EnsembleConfig:
    """Ensemble fusion settings."""
    efficientnet_weight: float = 0.55  # Slightly higher — stronger model
    xception_weight: float = 0.45
    threshold: float = 0.5  # Above this = fake
    export_dir: Path = MODELS_DIR / "ensemble"
