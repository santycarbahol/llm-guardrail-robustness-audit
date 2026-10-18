"""Backend-agnostic model client. Configure via .env (see .env.example)."""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = OpenAI(
    base_url=os.environ["MODEL_BASE_URL"],
    api_key=os.environ.get("MODEL_API_KEY", "EMPTY"),
)
MODEL_NAME = os.environ["MODEL_NAME"]


def chat(system: str, user: str, temperature: float = 0.0) -> str:
    resp = _client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""
