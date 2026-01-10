from http.client import responses

import requests
import json

OLLAMA_URL =  "http://127.0.0.1:11434/api/generate"

payload = {
    "model": "qwen2.5:7b",
    "prompt": "Hello!",
    "stream": False,
    "options": {
        "num_ctx": 2048
    }
}

response = requests.post(OLLAMA_URL, json=payload, timeout=120)

if response.status_code != 200:
    raise RuntimeError(f"Ollama Error: {response.text}")

data = response.json()
print(data["response"])