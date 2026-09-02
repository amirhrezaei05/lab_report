import numpy as np
import json


def normalize_easyocr_result(result):

    blocks = []

    for idx, item in enumerate(result):

        bbox, text, confidence = item

        # convert numpy values to normal python numbers
        bbox = np.array(bbox).tolist()

        x_values = [point[0] for point in bbox]
        y_values = [point[1] for point in bbox]

        x_min = min(x_values)
        y_min = min(y_values)

        x_max = max(x_values)
        y_max = max(y_values)


        blocks.append(
            {
                "id": idx,

                "text": text,

                "confidence": float(confidence),

                "bbox": {
                    "x_min": int(x_min),
                    "y_min": int(y_min),
                    "x_max": int(x_max),
                    "y_max": int(y_max)
                },

                "center": {
                    "x": int((x_min+x_max)/2),
                    "y": int((y_min+y_max)/2)
                }
            }
        )

    return {
        "blocks": blocks
    }

from src.ocr.engine.easyocr import EasyOCREngine
ocr = EasyOCREngine()

IMAGE = "/home/amir-hossein/Documents/Capture3-768x715.jpg"
result = ocr.recognize(IMAGE)

res = normalize_easyocr_result(result)
from pathlib import Path
import json


output_path = Path(
    "/home/amir-hossein/lab-to-care-platform/backend/data/ocr_output/ocr_result.json"
)

output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)


with open(
    output_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        res,
        f,
        indent=4,
        ensure_ascii=False
    )


print(f"Saved to: {output_path}")