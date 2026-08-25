from src.ocr.engine import PaddleOCREngine


IMAGE = "/home/amir-hossein/Documents/Capture3-768x715.jpg"


def main():

    print("Starting OCR test...")

    engine = PaddleOCREngine()

    print("Running OCR...")

    result = engine.recognize(
        IMAGE
    )

    print("OCR result:")
    print(result)


if __name__ == "__main__":
    main()