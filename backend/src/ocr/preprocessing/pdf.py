from pathlib import Path

import pymupdf

def pdf_to_images(
    pdf_path: str | Path,
    output_dir: str | Path,
    dpi: int = 300,
) -> list[Path]:
    """
    Convert each page of a PDF into a PNG image.

    Parameters
    ----------
    pdf_path:
        Path to the PDF file.

    output_dir:
        Directory where page images will be saved.

    dpi:
        Resolution used for rendering PDF pages.

    Returns
    -------
    list[Path]
        Paths to generated page images.

    Raises
    ------
    FileNotFoundError
        If the PDF does not exist.

    ValueError
        If the input is not a PDF or DPI is invalid.
    """

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if not pdf_path.is_file():
        raise ValueError(
            f"Path is not a file: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a PDF file, got: {pdf_path.suffix}"
        )

    if dpi <= 0:
        raise ValueError(
            "DPI must be greater than zero."
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = pymupdf.open(pdf_path)

    scale = dpi / 72
    matrix = pymupdf.Matrix(scale, scale)

    output_paths: list[Path] = []

    try:
        for page_number, page in enumerate(
            document,
            start=1,
        ):
            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False,
            )

            output_path = (
                output_dir
                / f"{pdf_path.stem}_page_{page_number:03d}.png"
            )

            pixmap.save(output_path)

            output_paths.append(output_path)

    finally:
        document.close()

    return output_paths