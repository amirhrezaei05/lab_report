from pathlib import Path

from paddleocr import PaddleOCR

from .base import OCREngine


class PaddleOCREngine(OCREngine):

    def __init__(self):
        self.ocr = PaddleOCR(
            lang="en",
            use_doc_orientation_classify=True,
            use_doc_unwarping=True,
            use_textline_orientation=True,
        )

    def recognize(
        self,
        image_path: str | Path,
    ) -> dict:

        result = self.ocr.predict(
            str(image_path)
        )

        return result