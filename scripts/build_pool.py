"""Build/refresh the psychology knowledge pool from Chinese Wikipedia.

Fetches article titles from Category:心理学 (and its immediate subcategories),
pulls a short summary for each via the Wikipedia REST summary API, and merges
new entries into data/pool.json (de-duplicated by title).
"""
import json
import time
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parent.parent
POOL_PATH = ROOT / "data" / "pool.json"

API_URL = "https://zh.wikipedia.org/w/api.php"
SUMMARY_URL = "https://zh.wikipedia.org/api/rest_v1/page/summary/{title}"
HEADERS = {"User-Agent": "dailypush-psychology-bot/1.0 (contact: nnilbig@gmail.com)"}

ROOT_CATEGORY = "Category:心理学"
MIN_EXTRACT_LEN = 40
MAX_TITLES = 300


def fetch_category_members(category, limit=500):
    titles = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": min(limit, 500),
        "format": "json",
    }
    resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    for member in data.get("query", {}).get("categorymembers", []):
        titles.append(member)
    return titles


def collect_titles():
    seen_pages = set()
    subcategories = []

    for member in fetch_category_members(ROOT_CATEGORY):
        title = member["title"]
        if title.startswith("Category:"):
            subcategories.append(title)
        elif member.get("ns") == 0:
            seen_pages.add(title)

    for subcat in subcategories[:20]:
        try:
            for member in fetch_category_members(subcat):
                if member.get("ns") == 0:
                    seen_pages.add(member["title"])
        except requests.RequestException:
            continue
        if len(seen_pages) >= MAX_TITLES:
            break

    return list(seen_pages)[:MAX_TITLES]


def fetch_summary(title):
    url = SUMMARY_URL.format(title=quote(title, safe=""))
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        return None
    data = resp.json()
    if data.get("type") == "disambiguation":
        return None
    extract = (data.get("extract") or "").strip()
    if len(extract) < MIN_EXTRACT_LEN:
        return None
    return {
        "title": data.get("title", title),
        "extract": extract,
        "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
    }


def load_pool():
    if POOL_PATH.exists():
        return json.loads(POOL_PATH.read_text(encoding="utf-8"))
    return []


def save_pool(pool):
    POOL_PATH.parent.mkdir(parents=True, exist_ok=True)
    POOL_PATH.write_text(
        json.dumps(pool, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main():
    pool = load_pool()
    existing_titles = {entry["title"] for entry in pool}

    candidate_titles = collect_titles()
    new_count = 0

    for title in candidate_titles:
        if title in existing_titles:
            continue
        entry = fetch_summary(title)
        time.sleep(0.2)
        if entry is None or entry["title"] in existing_titles:
            continue
        pool.append(entry)
        existing_titles.add(entry["title"])
        new_count += 1

    save_pool(pool)
    print(f"Pool size: {len(pool)} (added {new_count} new entries)")


if __name__ == "__main__":
    main()
