import requests
import json

class OllamaClient:
    def __init__(self, model="qwen2.5:7b-instruct-q4_K_M", context_size=2048):
        self.url = "http://127.0.0.1:11434/api/generate"
        self.model = model
        self.context_size = context_size

    def extract_contract_data(self, text: str) -> dict:
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")

        system_prompt = (
            "You are a contract analysis engine. "
            "Extract structured data from the text below. "
            "Respond ONLY in valid JSON. "
            "Do not explain. Do not add extra text. "
            "If a field is missing, set it to null."
        )

        user_prompt = f"""
Extract the following fields:
- parties
- effective_date
- termination_notice_days
- payment_amount
- governing_law

Text:
{text}
"""

        payload = {
            "model": self.model,
            "prompt": system_prompt + "\n" + user_prompt,
            "stream": False,
            "options": {
                "num_ctx": self.context_size,
                "temperature": 0,
                "num_batch": 128,


            }
        }

        response = requests.post(self.url, json=payload, timeout=120)

        if response.status_code != 200:
            raise RuntimeError(response.text)

        raw = response.json()["response"]

        # --- ROBUST JSON EXTRACTION ---
        start = raw.find("{")
        end = raw.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError(f"No valid JSON object found in output:\n{raw}")

        data = json.loads(raw[start:end + 1])
        elapsed_time = end - start
        return data, elapsed_time

    def ask(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(self.url, json=payload)
        response.raise_for_status()

        return response.json()["response"].strip()


