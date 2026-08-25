from PIL import Image, ImageEnhance, ImageFilter


def to_grayscale(
    image: Image.Image,
) -> Image.Image:
    """
    Convert an image to grayscale.
    """

    return image.convert("L")


def resize_image(
    image: Image.Image,
    scale: float = 1.0,
) -> Image.Image:
    """
    Resize an image by a scaling factor.

    Parameters
    ----------
    image:
        Input image.

    scale:
        Scaling factor.

    Returns
    -------
    PIL.Image.Image
        Resized image.
    """

    if scale <= 0:
        raise ValueError(
            "Scale must be greater than zero."
        )

    width, height = image.size

    new_size = (
        int(width * scale),
        int(height * scale),
    )

    return image.resize(
        new_size,
        Image.Resampling.LANCZOS,
    )


def enhance_contrast(
    image: Image.Image,
    factor: float = 1.2,
) -> Image.Image:
    """
    Adjust image contrast.

    factor = 1.0 → unchanged
    factor > 1.0 → increased contrast
    factor < 1.0 → decreased contrast
    """

    if factor <= 0:
        raise ValueError(
            "Contrast factor must be greater than zero."
        )

    enhancer = ImageEnhance.Contrast(image)

    return enhancer.enhance(factor)


def denoise(
    image: Image.Image,
    kernel_size: int = 3,
) -> Image.Image:
    """
    Apply a median filter for light denoising.

    Median filtering can remove small noise
    while preserving edges reasonably well.
    """

    if kernel_size not in {3, 5, 7}:
        raise ValueError(
            "kernel_size must be 3, 5, or 7."
        )

    return image.filter(
        ImageFilter.MedianFilter(
            size=kernel_size
        )
    )