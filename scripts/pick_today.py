"""Pick today's psychology knowledge entry from the pool.

Uses a date-seeded, fixed shuffle of the pool so that:
- The result for a given date is always reproducible (safe to re-run).
- Every entry in the pool is shown once before any repeat.
"""
import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POOL_PATH = ROOT / "data" / "pool.json"
TODAY_PATH = ROOT / "data" / "today.json"
HISTORY_PATH = ROOT / "data" / "history.json"

EPOCH = date(2026, 1, 1)


def load_json(path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def pick_for_date(pool, target_date):
    if not pool:
        raise SystemExit("Pool is empty. Run build_pool.py first.")

    order = list(range(len(pool)))
    random.Random(len(pool)).shuffle(order)

    day_number = (target_date - EPOCH).days
    cycle_position = day_number % len(order)
    return pool[order[cycle_position]]


def main():
    pool = load_json(POOL_PATH, [])
    today = date.today()

    entry = pick_for_date(pool, today)
    today_record = {
        "date": today.isoformat(),
        "title": entry["title"],
        "extract": entry["extract"],
        "url": entry["url"],
    }
    save_json(TODAY_PATH, today_record)

    history = load_json(HISTORY_PATH, [])
    if not history or history[-1]["date"] != today_record["date"]:
        history.append(today_record)
        save_json(HISTORY_PATH, history)

    print(f"Today ({today_record['date']}): {today_record['title']}")


if __name__ == "__main__":
    main()
