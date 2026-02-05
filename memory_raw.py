import json
import os
from datetime import datetime
from openai import OpenAI
from config import OPENROUTER_API_KEY

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

MEMORY_FILE = f"{DATA_DIR}/memory.json"

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def should_remember(text: str) -> bool:
    """
    Простая эвристика + LLM-фильтр позже.
    Сейчас — максимально безопасно.
    """
    keywords = [
        "всегда", "постоянно", "я такой", "мне трудно",
        "я хочу", "я боюсь", "я чувствую", "моя цель"
    ]
    t = text.lower()
    return any(k in t for k in keywords)


def remember(user_id: int, role: str, text: str):
    if not should_remember(text):
        return

    memory = load_memory()
    memory.append({
        "user_id": user_id,
        "role": role,
        "text": text,
        "time": datetime.now().isoformat()
    })
    save_memory(memory)


def recall(user_id: int, limit: int = 5):
    memory = load_memory()
    user_mem = [m for m in memory if m["user_id"] == user_id]
    return user_mem[-limit:]
