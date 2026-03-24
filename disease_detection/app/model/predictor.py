"""
Disease prediction engine using MobileNetV2.

"""

import logging

logger = logging.getLogger(__name__)

import torch

from app.model.preprocess import (
    preprocess_image,
    extract_crop_name,
    extract_disease_name,
)


class DiseasePredictor:
    """Crop disease classification using MobileNetV2."""

    def __init__(self, model_path: str = None):
        self.model = None
        self.classes = []
        self.device = torch.device("cpu")

        if not model_path:
            raise RuntimeError("MODEL_PATH is required for inference.")

        self._load_model(model_path)
        logger.info(f"MobileNetV2 loaded from {model_path} ({len(self.classes)} classes)")

    def _load_model(self, model_path: str):
        """
        Load fine-tuned MobileNetV2.

        Expects .pt format: {"model": <entire model>, "classes": [...]}
        The .pt contains the full model (architecture + weights)
    
        """
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)

        if not isinstance(checkpoint, dict) or "model" not in checkpoint:
            raise RuntimeError(
                'Checkpoint must contain "model" key with the entire model. '
                "Retrain with the updated mobilenet_transfer_learning.py to generate this format."
            )

        self.classes = checkpoint.get("classes", [])
        self.model = checkpoint["model"]
        self.model = self.model.to(self.device)
        self.model.eval()

    def predict(self, image_bytes: bytes, top_k: int = 3) -> dict:
        """
        Run disease classification on image bytes.

        Returns:
            {
              disease, crop, confidence, label,     -- top prediction
              top_predictions: [{class, crop, disease, confidence}, ...]
            }
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        tensor = preprocess_image(image_bytes).to(self.device)

        with torch.no_grad():
            outputs = self.model(tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            top_probs, top_indices = probs.topk(min(top_k, len(self.classes)))

        top_predictions = []
        for i in range(top_probs.shape[1]):
            idx = top_indices[0][i].item()
            cls = self.classes[idx] if idx < len(self.classes) else f"class_{idx}"
            top_predictions.append({
                "class":      cls,
                "crop":       extract_crop_name(cls),
                "disease":    extract_disease_name(cls),
                "confidence": round(top_probs[0][i].item(), 4),
            })

        best = top_predictions[0]
        return {
            "disease":         best["disease"],
            "crop":            best["crop"],
            "confidence":      best["confidence"],
            "label":           best["class"],
            "is_healthy":      best["disease"].lower() == "healthy",
            "top_predictions": top_predictions,
        }

# -- Singleton ---

_predictor: DiseasePredictor | None = None


def get_predictor() -> DiseasePredictor:
    global _predictor
    if _predictor is None:
        from app.config import get_dd_settings
        settings = get_dd_settings()
        _predictor = DiseasePredictor(model_path=settings.MODEL_PATH)
    return _predictor
