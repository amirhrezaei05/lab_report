from PIL import Image

from .image import (
    denoise,
    enhance_contrast,
    resize_image,
    to_grayscale,
)


def preprocess(
    image: Image.Image,
    *,
    grayscale: bool = True,
    scale: float = 1.0,
    contrast: float | None = None,
    apply_denoise: bool = False,
    denoise_kernel: int = 3,
) -> Image.Image:
    """
    Preprocess an image for OCR.

    Parameters
    ----------
    image:
        Input PIL image.

    grayscale:
        Convert image to grayscale.

    scale:
        Image scaling factor.

    contrast:
        Contrast factor. If None, contrast is unchanged.

    apply_denoise:
        Whether to apply median denoising.

    denoise_kernel:
        Median filter kernel size.

    Returns
    -------
    PIL.Image.Image
        Preprocessed image.
    """

    result = image

    # 1. Grayscale
    if grayscale:
        result = to_grayscale(result)

    # 2. Resize
    if scale != 1.0:
        result = resize_image(
            result,
            scale=scale,
        )

    # 3. Contrast
    if contrast is not None:
        result = enhance_contrast(
            result,
            factor=contrast,
        )

    # 4. Denoising
    if apply_denoise:
        result = denoise(
            result,
            kernel_size=denoise_kernel,
        )

    return result