"""Build the psychology knowledge pool from 10 major psychologists' theories.

For each psychologist in PSYCHOLOGISTS, fetches their biography plus each of
their key theories/concepts from Chinese Wikipedia by exact article title
(titles below were verified by hand against zh.wikipedia.org so the pool
only contains genuinely relevant entries), and writes the full curated set
to data/pool.json. The curated list is the source of truth, so the pool
file is fully regenerated on every run.
"""
import json
import time
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parent.parent
POOL_PATH = ROOT / "data" / "pool.json"

SUMMARY_URL = "https://zh.wikipedia.org/api/rest_v1/page/summary/{title}"
HEADERS = {"User-Agent": "dailypush-psychology-bot/1.0 (contact: nnilbig@gmail.com)"}

MIN_EXTRACT_LEN = 30
REQUEST_DELAY = 0.2

# 10 位經典/知名心理學家:人物條目 + 代表理論/概念條目(皆為驗證過的確切維基標題)
PSYCHOLOGISTS = {
    "西格蒙德·佛洛伊德": [
        "西格蒙德·弗洛伊德", "精神分析学", "本我、自我与超我",
        "心理防卫机制", "恋母情结", "夢的解析", "性冲动",
    ],
    "卡爾·榮格": [
        "卡尔·荣格", "集体无意识", "分析心理学",
        "外向性与内向性", "人格面具", "心理陰影", "共時性",
    ],
    "讓·皮亞傑": [
        "尚·皮亞傑", "認知發展論", "基模 (心理學)", "物體恆存",
    ],
    "伯爾赫斯·斯金納": [
        "伯尔赫斯·弗雷德里克·斯金纳", "斯金纳箱", "操作制約", "行为主义 (心理学)",
    ],
    "亞伯拉罕·馬斯洛": [
        "亚伯拉罕·马斯洛", "马斯洛需求层次理论", "自我實現", "高峰体验",
    ],
    "卡爾·羅傑斯": [
        "卡爾·羅哲斯", "個人中心治療", "人本主义心理学", "自我概念",
    ],
    "阿爾伯特·班杜拉": [
        "阿尔波特·班杜拉", "社会认知理论", "自我效能", "波波玩偶实验",
    ],
    "伊凡·巴夫洛夫": [
        "伊萬·巴甫洛夫", "古典制約",
    ],
    "阿爾弗雷德·阿德勒": [
        "阿尔弗雷德·阿德勒", "自卑情结", "出生順序",
    ],
    "愛利克·艾瑞克森": [
        "爱利克·埃里克森", "埃里克森社会心理发展阶段", "身份认同",
    ],
}


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


def main():
    pool = []
    seen_titles = set()

    for psychologist, titles in PSYCHOLOGISTS.items():
        for title in titles:
            entry = fetch_summary(title)
            time.sleep(REQUEST_DELAY)
            if entry is None or entry["title"] in seen_titles:
                continue
            entry["psychologist"] = psychologist
            pool.append(entry)
            seen_titles.add(entry["title"])

    POOL_PATH.parent.mkdir(parents=True, exist_ok=True)
    POOL_PATH.write_text(
        json.dumps(pool, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Pool size: {len(pool)}")


if __name__ == "__main__":
    main()
