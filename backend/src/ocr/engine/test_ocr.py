from src.ocr.engine import EasyOCREngine


IMAGE = "/home/amir-hossein/Documents/Capture3-768x715.jpg"


def main():

    print("Starting OCR test...")

    engine = EasyOCREngine()

    print("Running OCR...")

    result = engine.recognize(
        IMAGE
    )

    print("OCR result:")
    print(result)


if __name__ == "__main__":
    main()