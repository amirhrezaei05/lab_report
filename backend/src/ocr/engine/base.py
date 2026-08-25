from abc import ABC, abstractmethod
from pathlib import Path


class OCREngine(ABC):

    @abstractmethod
    def recognize(
        self,
        image_path: str | Path,
    ) -> dict:
        """
        Run OCR on an image.

        Parameters
        ----------
        image_path:
            Path to input image.

        Returns
        -------
        dict
            Raw OCR result.
        """
        pass