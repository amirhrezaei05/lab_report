from pathlib import Path

from PIL import Image


SUPPORTED_IMAGE_FORMATS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}


def load_image(path: str | Path) -> Image.Image:
    """
    Load an image from disk and convert it to RGB.

    Parameters
    ----------
    path:
        Path to the image file.

    Returns
    -------
    PIL.Image.Image
        Loaded RGB image.

    Raises
    ------
    FileNotFoundError
        If the image does not exist.

    ValueError
        If the file format is not supported.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Image not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    if path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
        raise ValueError(
            f"Unsupported image format: {path.suffix}"
        )

    with Image.open(path) as image:
        return image.convert("RGB")