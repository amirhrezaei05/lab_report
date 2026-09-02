import easyocr
from pathlib import Path
from .base import OCREngine


class EasyOCREngine(OCREngine):

    def __init__(self):
        self.reader = easyocr.Reader(
            ['en'],
            gpu=False
        )

    def recognize(
        self,
        image_path: str | Path
    ):

        result = self.reader.readtext(
            str(image_path)
        )

        return result