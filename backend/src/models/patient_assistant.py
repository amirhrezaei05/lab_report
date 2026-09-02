import ollama
import json 

from pathlib import Path

input_path= 


prompt = f"""

تو یک دستیار پزشکی برای توضیح ساده نتایج آزمایش به بیمار هستی.

وظیفه:
نتایج آزمایش را برای بیمار به زبان فارسی ساده توضیح بده.

قوانین مهم:

- از اصطلاحات پیچیده پزشکی استفاده نکن، یا اگر استفاده کردی توضیح بده.
- تشخیص قطعی بیماری نده.
- فقط توضیح بده که هر نتیجه چه مفهومی می‌تواند داشته باشد.
- بیمار را نترسان.
- اگر نتیجه خارج از محدوده طبیعی است، توضیح بده که ممکن است به چه دلایلی مرتبط باشد.
- توصیه کن برای تفسیر نهایی با پزشک مشورت شود.
- اطلاعات آزمایش را تغییر نده.

ساختار پاسخ:

1. خلاصه کلی وضعیت آزمایش

2. نتایج مهم:
   - نام آزمایش
   - مقدار شما
   - محدوده معمول
   - معنی ساده

3. چه مواردی ممکن است نیاز به پیگیری داشته باشند

4. پیشنهاد برای صحبت با پزشک


نتایج آزمایش:

{json.dumps(
    structured_lab,
    ensure_ascii=False,
    indent=2
)}

"""



import ollama 
prompt_1="hello "

response = ollama.chat(
    model="llama3.1",
    messages=[
        {
                "role":"system",
                                            "content":"You are a medical data extraction assistant."
        },
        {
            "role":"user",
            "content":prompt_1            }
    ],
    options={
        "temperature":0
    }
)


result = response["message"]["content"]
print(result)



