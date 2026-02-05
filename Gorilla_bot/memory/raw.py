import json
import os
from datetime import datetime

BASE_DIR = "data/user_prompt_memory/raw"
os.makedirs(BASE_DIR, exist_ok=True)

def _today_path():
    return os.path.join(BASE_DIR, f"{datetime.now().date()}.json")

def remember(text: str):
    path = _today_path()
    data = {"date": str(datetime.now().date()), "items": []}

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            pass

    data["items"].append(text)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
