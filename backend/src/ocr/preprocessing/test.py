from pathlib import Path

from src.ocr.preprocessing import load_image, preprocess


INPUT_IMAGE = Path(
    "/home/amir-hossein/Documents/Capture3-768x715.jpg"
)

OUTPUT_DIR = Path(
    "data/processed/preprocessing_test"
)


def main() -> None:

    # Create output directory
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Check input
    if not INPUT_IMAGE.exists():
        raise FileNotFoundError(
            f"Image not found: {INPUT_IMAGE}"
        )

    if not INPUT_IMAGE.is_file():
        raise ValueError(
            f"Input path is not a file: {INPUT_IMAGE}"
        )

    print(f"Processing: {INPUT_IMAGE}")

    # Load
    image = load_image(INPUT_IMAGE)

    print(f"Original size: {image.size}")
    print(f"Original mode: {image.mode}")

    # Preprocess
    processed = preprocess(
        image,
        grayscale=True,
        scale=1.0,
        contrast=None,
        apply_denoise=False,
    )

    print(f"Processed size: {processed.size}")
    print(f"Processed mode: {processed.mode}")

    # Save
    output_path = (
        OUTPUT_DIR
        / f"{INPUT_IMAGE.stem}_processed.png"
    )

    processed.save(output_path)

    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()