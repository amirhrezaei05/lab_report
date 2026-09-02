

import ollama

client = ollama.Client(
    host="http://127.0.0.1:11434"
)

response = client.chat(
    model="qwen2.5:latest",
    messages=[
        {
            "role": "user",
            "content": "hello"
        }
    ]
)

print(response.message.content)