"""Massive scraper - 10x data collection from multiple sources."""
import sys
import io
import os
import json
import time
import random
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import httpx
from bs4 import BeautifulSoup

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/129.0.0.0 Safari/537.36",
]

YAHOO_QUERIES = [
    "エルメス バーキン", "エルメス ケリー", "エルメス ピコタン", "エルメス コンスタンス",
    "エルメス ガーデンパーティ", "シャネル マトラッセ", "シャネル ボーイシャネル",
    "シャネル ドーヴィル", "ルイヴィトン ネヴァーフル", "ルイヴィトン スピーディ",
    "ルイヴィトン アルマ", "ルイヴィトン カプシーヌ", "グッチ マーモント バッグ",
    "プラダ ガレリア", "セリーヌ ラゲージ", "ディオール レディディオール",
    "ボッテガヴェネタ カセット", "バレンシアガ シティ", "サンローラン ルル",
    "フェンディ ピーカブー", "フェンディ バゲット", "コーチ タビー",
    "エルメス ベアン 財布", "シャネル マトラッセ 長財布", "シャネル カメリア 財布",
    "ルイヴィトン ジッピーウォレット", "ルイヴィトン ポルトフォイユ",
    "ロレックス サブマリーナ", "ロレックス デイトナ", "ロレックス デイトジャスト",
    "ロレックス GMTマスター", "ロレックス エクスプローラー",
    "オメガ スピードマスター", "オメガ シーマスター", "オメガ コンステレーション",
    "カルティエ タンク 時計", "カルティエ サントス", "カルティエ バロンブルー",
]


def scrape_yahoo(queries, pages_per_query=5):
    all_items = []
    with httpx.Client(timeout=20, follow_redirects=True) as client:
        for qi, query in enumerate(queries):
            query_items = []
            for page in range(pages_per_query):
                offset = page * 100 + 1
                url = f"https://auctions.yahoo.co.jp/search/search?p={query}&select=sold&n=100&b={offset}"
                try:
                    time.sleep(random.uniform(2, 3.5))
                    resp = client.get(url, headers={"User-Agent": random.choice(USER_AGENTS)})
                    if resp.status_code != 200:
                        break
                    soup = BeautifulSoup(resp.text, "html.parser")
                    products = soup.select(".Product")
                    if not products:
                        break
                    for p in products:
                        title_el = p.select_one(".Product__titleLink")
                        price_el = p.select_one(".Product__priceValue")
                        if not title_el or not price_el:
                            continue
                        price = int(re.sub(r'[^\d]', '', price_el.get_text()) or 0)
                        if price > 0:
                            query_items.append({
                                "title": title_el.get_text(strip=True),
                                "price": price,
                                "url": title_el.get("href", ""),
                                "source": "yahoo_auction",
                                "query": query,
                            })
                except Exception:
                    break
            all_items.extend(query_items)
            print(f"[Yahoo {qi+1}/{len(queries)}] {query}: {len(query_items)} (total: {len(all_items)})")
            if (qi + 1) % 10 == 0:
                with open(os.path.join(DATA_DIR, "yahoo_massive.json"), "w", encoding="utf-8") as f:
                    json.dump(all_items, f, ensure_ascii=False)
    return all_items


def scrape_aucfan(queries):
    all_items = []
    with httpx.Client(timeout=20, follow_redirects=True) as client:
        for qi, query in enumerate(queries):
            try:
                time.sleep(random.uniform(3, 5))
                resp = client.get(f"https://aucfan.com/search1/?q={query}&t=1", headers={"User-Agent": random.choice(USER_AGENTS)})
                if resp.status_code != 200:
                    print(f"[AucFan] {query}: {resp.status_code}")
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")
                for item in soup.select(".item, .l-itemCard, [class*='product'], [class*='item']"):
                    title_el = item.select_one("a, h3, [class*='title']")
                    price_el = item.select_one("[class*='price']")
                    if not title_el or not price_el:
                        continue
                    price = int(re.sub(r'[^\d]', '', price_el.get_text()) or 0)
                    if price > 0:
                        all_items.append({"title": title_el.get_text(strip=True), "price": price, "url": title_el.get("href", ""), "source": "aucfan", "query": query})
                print(f"[AucFan {qi+1}/{len(queries)}] {query}: total {len(all_items)}")
            except Exception as e:
                print(f"[AucFan] {query}: {e}")
    return all_items


def scrape_reclo(queries):
    all_items = []
    with httpx.Client(timeout=20, follow_redirects=True) as client:
        for qi, query in enumerate(queries):
            try:
                time.sleep(random.uniform(2, 4))
                resp = client.get(f"https://www.reclo.jp/search?keyword={query}", headers={"User-Agent": random.choice(USER_AGENTS)})
                if resp.status_code != 200:
                    print(f"[RECLO] {query}: {resp.status_code}")
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")
                for item in soup.select("[class*='product'], [class*='item'], article"):
                    title_el = item.select_one("a, h3, [class*='name']")
                    price_el = item.select_one("[class*='price']")
                    if not title_el or not price_el:
                        continue
                    price = int(re.sub(r'[^\d]', '', price_el.get_text()) or 0)
                    href = title_el.get("href", "")
                    if href and not href.startswith("http"):
                        href = f"https://www.reclo.jp{href}"
                    if price > 0:
                        all_items.append({"title": title_el.get_text(strip=True), "price": price, "url": href, "source": "reclo", "query": query})
                print(f"[RECLO {qi+1}/{len(queries)}] {query}: total {len(all_items)}")
            except Exception as e:
                print(f"[RECLO] {query}: {e}")
    return all_items


if __name__ == "__main__":
    print("=" * 50)
    print("MASSIVE SCRAPE - Target: 15,000+ items")
    print("=" * 50)

    yahoo_items = scrape_yahoo(YAHOO_QUERIES, pages_per_query=5)
    with open(os.path.join(DATA_DIR, "yahoo_massive.json"), "w", encoding="utf-8") as f:
        json.dump(yahoo_items, f, ensure_ascii=False)
    print(f"\nYahoo: {len(yahoo_items)} items")

    aucfan_items = scrape_aucfan(YAHOO_QUERIES[:15])
    with open(os.path.join(DATA_DIR, "aucfan_results.json"), "w", encoding="utf-8") as f:
        json.dump(aucfan_items, f, ensure_ascii=False)
    print(f"AucFan: {len(aucfan_items)} items")

    reclo_items = scrape_reclo(YAHOO_QUERIES[:10])
    with open(os.path.join(DATA_DIR, "reclo_results.json"), "w", encoding="utf-8") as f:
        json.dump(reclo_items, f, ensure_ascii=False)
    print(f"RECLO: {len(reclo_items)} items")

    total = len(yahoo_items) + len(aucfan_items) + len(reclo_items)
    print(f"\nGRAND TOTAL: {total} items")
