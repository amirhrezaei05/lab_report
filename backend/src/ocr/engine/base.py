from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class OCREngine(ABC):

    @abstractmethod
    def recognize(
        self,
        image_path: str | Path,
    ) -> Any:
        """
        Run OCR on an image.

        Parameters
        ----------
        image_path:
            Path to input image.

        Returns
        -------
        Any
            Raw OCR result returned by the concrete OCR engine.
        """
        raise NotImplementedError