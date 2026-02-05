import os
import json
from datetime import datetime, timedelta
from openai import OpenAI
from config import OPENROUTER_API_KEY

RAW_DIR = "data/user_prompt_memory/raw"
DAILY_DIR = "data/user_prompt_memory/daily"

os.makedirs(DAILY_DIR, exist_ok=True)

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

def build_daily_from_raw(date: str):
    raw_path = os.path.join(RAW_DIR, f"{date}.json")
    if not os.path.exists(raw_path):
        return None

    with open(raw_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    raw_text = "\n".join(raw["items"])

    prompt = f"""
На основе логов за день сформируй КОРОТКИЙ daily-промт для ИИ-ассистента.

Правила:
- только факты о пользователе
- цели, стиль общения, важные предпочтения
- без диалогов
- 5–10 пунктов
- пиши жёстко и структурировано

Логи дня:
{raw_text}
"""

    resp = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.3,
        max_tokens=400
    )

    daily_text = resp.choices[0].message.content.strip()

    daily_path = os.path.join(DAILY_DIR, f"{date}.txt")
    with open(daily_path, "w", encoding="utf-8") as f:
        f.write(daily_text)

    return daily_text


def load_today_daily() -> str:
    today = datetime.now().date()
    path = os.path.join(DAILY_DIR, f"{today}.txt")
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()
