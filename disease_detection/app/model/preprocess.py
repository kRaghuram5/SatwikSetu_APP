"""Image preprocessing for MobileNetV2 disease detection.

Transform pipeline:
  Resize(256) -> CenterCrop(224) -> ToTensor -> Normalize(ImageNet stats)
"""

from io import BytesIO
from PIL import Image
from torchvision import transforms

# ImageNet normalization stats -- required for pretrained MobileNetV2
_IMAGENET_MEAN = [0.485, 0.456, 0.406]
_IMAGENET_STD  = [0.229, 0.224, 0.225]

# Inference transform
_inference_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(_IMAGENET_MEAN, _IMAGENET_STD),
])


def preprocess_image(image_bytes: bytes):
    """
    Preprocess raw image bytes into a model-ready tensor.

    Returns a 4-D tensor: [1, 3, 224, 224]
    """
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    tensor = _inference_transform(img)
    return tensor.unsqueeze(0)   # Add batch dimension


def _split_label(label: str) -> tuple[str, str]:
    """
    Split a PlantVillage class label into (crop, disease).

    Handles all separator variants:
      'Tomato___Late_blight'        -> ('Tomato', 'Late_blight')
      'Tomato__Tomato_mosaic_virus' -> ('Tomato', 'Tomato_mosaic_virus')
      'Tomato_healthy'              -> ('Tomato', 'healthy')
    """
    if "___" in label:
        parts = label.split("___", 1)
    elif "__" in label:
        parts = label.split("__", 1)
    else:
        parts = label.split("_", 1)

    return (parts[0], parts[1]) if len(parts) > 1 else (label, "Unknown")


def extract_crop_name(label: str) -> str:
    return _split_label(label)[0]


def extract_disease_name(label: str) -> str:
    return _split_label(label)[1]
