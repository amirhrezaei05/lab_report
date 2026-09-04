import ollama
import json

from pathlib import Path 
input_path = Path(
    "/home/amir-hossein/lab-to-care-platform/backend/data/ocr_output/ocr_result.json"
)


with open(
    input_path,
    "r",
    encoding="utf-8"
) as f:
    ocr_json = json.load(f)


def structure_lab_report(ocr_json):

    prompt = f"""
شما یک سیستم استخراج اطلاعات آزمایش پزشکی هستید.

وظیفه:
تبدیل OCR گزارش آزمایش به JSON ساختاریافته.

قوانین:
- فقط اطلاعات موجود را استخراج کن.
- هیچ تفسیر پزشکی انجام نده.
- هیچ تشخیص بیماری نده.
- اطلاعات جدید اضافه نکن.
- خروجی فقط JSON معتبر باشد.

فرمت خروجی:

{{
"patient": {{
"name": null,
"age": null,
"gender": null,
"date": null
}},

"tests":[
{{
"name":"",
"value":"",
"unit":"",
"reference_range":"",
"section":""
}}
]
}}

OCR:

{json.dumps(
    ocr_json,
    ensure_ascii=False,
    indent=2
)}
"""


    response = ollama.chat(
        model="llama3.1:latest",
        messages=[
            {
                "role":"system",
                "content":"You are a medical data extraction assistant."
            },
            {
                "role":"user",
                "content":prompt
            }
        ],
        options={
            "temperature":0
        }
    )


    result = response["message"]["content"]

    return json.loads(result)

structured_json = structure_lab_report(ocr_json)


# project data folder
output_path = Path(
    "data/structured_lab.json"
)

# create folder if it does not exist
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
        structured_json,
        f,
        indent=4,
        ensure_ascii=False
    )


print(f"Saved to: {output_path}")

