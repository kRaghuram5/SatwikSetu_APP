import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import re

ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(ENV_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
if not OPENAI_BASE_URL:
    raise ValueError("OPENAI_BASE_URL is not set in the environment variables.")
if not OPENAI_MODEL:
    raise ValueError("OPENAI_MODEL is not set in the environment variables.")

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

completion = client.chat.completions.create(
    model=OPENAI_MODEL,
    messages=[
        {
            "role": "system",
            "content": (
                "You are an agricultural assistant. Always respond ONLY with a compact JSON object "
                "with these keys: \"disease\" (name), \"cure\" (immediate/long-term), \"prevent\" (short tip). "
                "The entire JSON string must be under 100 characters. No extra text."
            )
        },
        {"role": "user", "content": "Tomato late blight"}
    ],
    temperature=0.7
)

raw = completion.choices[0].message.content.strip()
# Strip markdown code fences if present
raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
parsed = json.loads(raw)
print(json.dumps(parsed, indent=2))