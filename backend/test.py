# test_proxyapi.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("PROXYAPI_TOKEN"),
    base_url="https://api.proxyapi.ru/openai/v1"
)

# Тест embeddings
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=["Привет, как дела?"]
)
print("Embeddings OK:", len(response.data[0].embedding))

# Тест chat
completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Скажи 'привет'"}]
)
print("Chat OK:", completion.choices[0].message.content)
