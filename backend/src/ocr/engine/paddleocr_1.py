
from paddleocr import TextDetection
from .base import OCREngine
from pathlib import Path


class PaddleOCREngine(OCREngine):

    def __init__(self):
        self.ocr = TextDetection(model_name="PP-OCRv6_medium_det_safetensors")

    def recognize(
        self,
        image_path: str | Path,
    ) -> dict:

        result = self.ocr.predict(
            str(image_path)
        )

        return result
