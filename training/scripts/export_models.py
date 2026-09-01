"""
SatyaKavach - Export Pre-trained Models to ONNX
Exports ImageNet-pretrained EfficientNet-B4 and XceptionNet for deepfake detection.
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import torch
import torch.nn as nn

BACKEND_MODELS_DIR = PROJECT_ROOT / "backend" / "app" / "services" / "ai" / "model_weights"
BACKEND_MODELS_DIR.mkdir(parents=True, exist_ok=True)


def export_efficientnet():
    print("=" * 60)
    print("Exporting EfficientNet-B4...")
    print("=" * 60)

    import torchvision.models as models

    weights = models.EfficientNet_B4_Weights.IMAGENET1K_V1
    model = models.efficientnet_b4(weights=weights)

    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(in_features, 256),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.2),
        nn.Linear(256, 2),
    )

    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    output_path = BACKEND_MODELS_DIR / "efficientnet_b4_deepfake.onnx"
    dummy = torch.randn(1, 3, 224, 224).to(device)

    torch.onnx.export(
        model, dummy, str(output_path),
        input_names=["image"],
        output_names=["logits"],
        dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=17,
    )

    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"[OK] Exported: {output_path} ({size_mb:.1f} MB)")
    return output_path


def export_xception():
    print("\n" + "=" * 60)
    print("Exporting XceptionNet...")
    print("=" * 60)

    import timm

    model = timm.create_model("xception", pretrained=True, num_classes=2)
    model.eval()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    output_path = BACKEND_MODELS_DIR / "xception_deepfake.onnx"
    dummy = torch.randn(1, 3, 224, 224).to(device)

    torch.onnx.export(
        model, dummy, str(output_path),
        input_names=["image"],
        output_names=["logits"],
        dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=17,
    )

    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"[OK] Exported: {output_path} ({size_mb:.1f} MB)")
    return output_path


def test_inference():
    print("\n" + "=" * 60)
    print("Testing ONNX inference...")
    print("=" * 60)

    try:
        import onnxruntime as ort
    except ImportError:
        print("Installing onnxruntime...")
        os.system("pip install onnxruntime")
        import onnxruntime as ort

    import numpy as np

    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    dummy_input = np.random.randn(1, 3, 224, 224).astype(np.float32)

    for model_name in ["efficientnet_b4_deepfake.onnx", "xception_deepfake.onnx"]:
        model_path = BACKEND_MODELS_DIR / model_name
        if model_path.exists():
            session = ort.InferenceSession(str(model_path), providers=providers)
            input_name = session.get_inputs()[0].name
            outputs = session.run(None, {input_name: dummy_input})
            logits = outputs[0][0]
            probs = np.exp(logits) / np.exp(logits).sum()
            print(f"[OK] {model_name}: P(real)={probs[0]:.3f}, P(fake)={probs[1]:.3f}")
        else:
            print(f"[FAIL] {model_name}: NOT FOUND")


if __name__ == "__main__":
    print("SatyaKavach - Model Export")
    print(f"Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    export_efficientnet()
    export_xception()
    test_inference()

    print("\n" + "=" * 60)
    print("ALL MODELS EXPORTED SUCCESSFULLY")
    print(f"Location: {BACKEND_MODELS_DIR}")
    print("=" * 60)
