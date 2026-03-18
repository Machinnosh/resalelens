"""
Import scraped resale data into Supabase and calculate PRR predictions.
"""
import json
import re
import statistics
from datetime import date
from pathlib import Path

from supabase import create_client

# --- Config ---
SUPABASE_URL = "https://pbnepwydakpcrlinqjgk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBibmVwd3lkYWtwY3JsaW5xamdrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4MTY5MTIsImV4cCI6MjA4OTM5MjkxMn0.rHcJ0xd3MAbLKfQ5jVYTvwqY8W0GoUMhIDNsdGr9Pq4"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TODAY = date.today().isoformat()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================
# 1. Load brands & products from Supabase
# =========================================================
print("Loading brands and products from Supabase...")
brands_resp = supabase.table("brands").select("*").execute()
brands = brands_resp.data
print(f"  Loaded {len(brands)} brands")

products_resp = supabase.table("products").select("*, brands(name, name_ja)").execute()
products = products_resp.data
print(f"  Loaded {len(products)} products")

# Build lookup: brand_id -> brand row
brand_map = {b["id"]: b for b in brands}

# Build matching keywords for each product
# We'll match on: brand name_ja (without dots/middle-dots) + model keywords
MODEL_KEYWORDS = {
    "birkin": ["バーキン", "birkin"],
    "kelly": ["ケリー", "kelly"],
    "constance": ["コンスタンス", "constance"],
    "picotin": ["ピコタン", "picotin"],
    "garden-party": ["ガーデンパーティ", "garden party"],
    "azap": ["アザップ", "azap"],
    "bearn": ["ベアン", "bearn"],
    "dogon": ["ドゴン", "dogon"],
    "classic-flap": ["フラップ", "classic flap", "マトラッセ", "matelasse"],
    "boy-chanel": ["ボーイ", "boy"],
    "deauville": ["ドーヴィル", "deauville"],
    "camellia-wallet": ["カメリア", "camellia"],
    "matelasse-compact": ["マトラッセ", "matelasse", "コンパクト"],
    "matelasse-long-wallet": ["マトラッセ", "matelasse", "長財布"],
    "neverfull": ["ネヴァーフル", "neverfull"],
    "speedy": ["スピーディ", "speedy"],
    "alma": ["アルマ", "alma"],
    "capucines": ["カプシーヌ", "capucines"],
    "zippy-wallet": ["ジッピー", "zippy"],
    "portefeuille-victorine": ["ヴィクトリーヌ", "victorine"],
    "portefeuille-sarah": ["サラ", "sarah", "ポルトフォイユ"],
    "gg-marmont": ["マーモント", "marmont"],
    "gg-marmont-wallet": ["マーモント", "marmont", "財布", "wallet"],
    "dionysus": ["ディオニュソス", "dionysus"],
    "submariner": ["サブマリーナ", "submariner"],
    "daytona": ["デイトナ", "daytona"],
    "datejust": ["デイトジャスト", "datejust"],
    "gmt-master-ii": ["GMTマスター", "gmt-master", "gmt master"],
    "explorer": ["エクスプローラー", "explorer"],
    "speedmaster": ["スピードマスター", "speedmaster"],
    "seamaster-300": ["シーマスター", "seamaster"],
    "aqua-terra": ["アクアテラ", "aqua terra"],
    "constellation": ["コンステレーション", "constellation"],
    "galleria": ["ガレリア", "galleria"],
    "saffiano-wallet": ["サフィアーノ", "saffiano", "財布"],
    "re-nylon": ["リナイロン", "re-nylon", "re nylon"],
    "lady-dior": ["レディディオール", "レディ ディオール", "lady dior"],
    "saddle": ["サドル", "saddle"],
    "book-tote": ["ブックトート", "ブック トート", "book tote"],
    "baguette": ["バゲット", "baguette"],
    "peekaboo": ["ピーカブー", "peekaboo"],
    "luggage": ["ラゲージ", "luggage"],
    "belt-bag": ["ベルトバッグ", "ベルト バッグ", "belt bag"],
    "loulou": ["ルル", "loulou"],
    "sac-de-jour": ["サック・ド・ジュール", "サックドジュール", "sac de jour"],
    "hourglass": ["アワーグラス", "hourglass"],
    "city": ["シティ", "city"],
    "cassette": ["カセット", "cassette"],
    "jodie": ["ジョディ", "jodie"],
    "santos": ["サントス", "santos"],
    "tank": ["タンク", "tank"],
    "ballon-bleu": ["バロンブルー", "バロン ブルー", "ballon bleu"],
    "panthere": ["パンテール", "panthere"],
    "tabby": ["タビー", "tabby"],
    "willow": ["ウィロウ", "willow"],
    "long-zip": ["ロング ジップ", "ロングジップ", "long zip"],
    "sam": ["サム", "sam"],
    "margaux": ["マルゴー", "margaux"],
    "jet-set": ["ジェットセット", "ジェット セット", "jet set"],
    "mercer": ["マーサー", "mercer"],
    "1927": ["1927"],
    "babylon": ["バビロン", "babylon"],
}

# Size keywords for distinguishing sizes
SIZE_KEYWORDS = {
    "25": ["25"],
    "28": ["28"],
    "30": ["30"],
    "32": ["32"],
    "35": ["35"],
    "18": ["18"],
    "22": ["22"],
    "BB": ["BB", "bb"],
    "PM": ["PM", "pm"],
    "GM": ["GM", "gm"],
    "MM": ["MM", "mm"],
    "スモール": ["スモール", "small", "ミニ", "mini", "ナノ", "nano"],
    "ミディアム": ["ミディアム", "medium", "ミドル"],
    "ジャンボ": ["ジャンボ", "jumbo"],
}


def normalize_brand_name(name_ja: str) -> str:
    """Remove middle dots and spaces for matching."""
    return name_ja.replace("・", "").replace("　", "").replace(" ", "").lower()


def normalize_title(title: str) -> str:
    """Normalize title for matching."""
    return title.replace("　", " ").lower()


def match_product(title: str, products: list) -> dict | None:
    """
    Match a scraped item title to a product.
    Returns the best matching product or None.
    """
    title_norm = normalize_title(title)
    title_upper = title  # Keep original for case-sensitive checks

    candidates = []
    for p in products:
        brand = brand_map.get(p["brand_id"])
        if not brand:
            continue

        # Check brand name in title
        brand_name_ja = brand["name_ja"]
        brand_name_en = brand["name"]
        brand_ja_norm = normalize_brand_name(brand_name_ja)

        # Match brand (Japanese or English)
        title_brand_check = normalize_brand_name(title)
        brand_matched = (
            brand_ja_norm in title_brand_check
            or brand_name_en.lower() in title_norm
        )
        # Special cases
        if brand_name_en == "Hermès":
            brand_matched = brand_matched or "hermes" in title_norm or "エルメス" in title
        if brand_name_en == "Louis Vuitton":
            brand_matched = brand_matched or "ルイヴィトン" in title_brand_check or "louis vuitton" in title_norm or "vuitton" in title_norm
        if brand_name_en == "CHANEL":
            brand_matched = brand_matched or "シャネル" in title or "chanel" in title_norm
        if brand_name_en == "Omega":
            brand_matched = brand_matched or "オメガ" in title or "omega" in title_norm

        if not brand_matched:
            continue

        # Check model keywords
        model = p.get("model", "")
        keywords = MODEL_KEYWORDS.get(model, [])
        model_matched = False
        for kw in keywords:
            if kw.lower() in title_norm or kw in title_upper:
                model_matched = True
                break

        if not model_matched:
            continue

        # Score by size match
        size = p.get("size", "") or ""
        product_name = p.get("name", "")
        size_score = 0

        # Try to match size from product name
        # Extract size indicators from product name
        for size_key, size_kws in SIZE_KEYWORDS.items():
            # Check if this size is in the product name
            if size_key in product_name or size_key == size:
                for skw in size_kws:
                    if skw in title_upper or skw.lower() in title_norm:
                        size_score = 10
                        break

        candidates.append((p, size_score))

    if not candidates:
        return None

    # Sort by size_score descending; pick best match
    candidates.sort(key=lambda x: x[1], reverse=True)

    # If multiple candidates and top ones have same score, pick based on specificity
    # For CHANEL classic-flap vs matelasse-wallet, etc. - prefer the one whose model keywords appear more
    best_score = candidates[0][1]
    top_candidates = [c for c in candidates if c[1] == best_score]

    if len(top_candidates) == 1:
        return top_candidates[0][0]

    # If we have size info, try more specific match
    # Otherwise just return the first one
    return top_candidates[0][0]


# =========================================================
# 2. Read JSON files
# =========================================================
print("\nReading scraped JSON files...")


def read_yahoo(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = []
    for query_key, query_data in data.get("queries", {}).items():
        for item in query_data.get("items", []):
            price = item.get("price")
            if price and isinstance(price, (int, float)) and price > 0:
                items.append({
                    "title": item.get("title", ""),
                    "price": int(price),
                    "url": item.get("url", ""),
                    "condition": None,
                    "sold_date": TODAY,
                    "source": "yahoo_auction",
                    "raw": item,
                })
    return items


def read_mercari(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = []
    for query_key, query_data in data.get("queries", {}).items():
        for item in query_data.get("items", []):
            price = item.get("price")
            if price and isinstance(price, (int, float)) and price > 0:
                sold_date = item.get("sold_date") or item.get("listed_date") or ""
                if sold_date:
                    sold_date = sold_date[:10]  # YYYY-MM-DD
                else:
                    sold_date = TODAY
                items.append({
                    "title": item.get("title", ""),
                    "price": int(price),
                    "url": item.get("url", ""),
                    "condition": item.get("condition"),
                    "sold_date": sold_date,
                    "source": "mercari",
                    "raw": item,
                })
    return items


def read_brandear(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = []
    for item in data:
        price_str = item.get("price", "")
        # Parse price like "～113,000円" or "4,300,000円"
        price_clean = re.sub(r"[～〜円,\s]", "", price_str)
        try:
            price = int(price_clean)
        except (ValueError, TypeError):
            continue
        if price <= 0:
            continue
        items.append({
            "title": item.get("title", ""),
            "price": price,
            "url": item.get("url", ""),
            "condition": item.get("condition"),
            "sold_date": TODAY,
            "source": "brandear",
            "raw": item,
        })
    return items


yahoo_items = read_yahoo(DATA_DIR / "yahoo_auction_results.json")
mercari_items = read_mercari(DATA_DIR / "mercari_results.json")
brandear_items = read_brandear(DATA_DIR / "brandear_results.json")

print(f"  Yahoo Auction: {len(yahoo_items)} items with valid prices")
print(f"  Mercari: {len(mercari_items)} items with valid prices")
print(f"  Brandear: {len(brandear_items)} items with valid prices")

all_items = yahoo_items + mercari_items + brandear_items
print(f"  Total: {len(all_items)} items")

# =========================================================
# 3. Match items to products
# =========================================================
print("\nMatching items to products...")
matched = []
unmatched = []
match_counts = {}  # product_id -> count

MAX_PRICE = 2_000_000_000  # PostgreSQL integer limit

for item in all_items:
    if item["price"] > MAX_PRICE:
        unmatched.append(item)
        continue
    product = match_product(item["title"], products)
    if product:
        pid = product["id"]
        matched.append({
            "product_id": pid,
            "source": item["source"],
            "sold_price": item["price"],
            "condition": item["condition"],
            "sold_date": item["sold_date"],
            "listing_url": item["url"],
            "raw_data": item["raw"],
        })
        match_counts[pid] = match_counts.get(pid, 0) + 1
    else:
        unmatched.append(item)

print(f"  Matched: {len(matched)} items")
print(f"  Unmatched: {len(unmatched)} items")
print(f"  Products with matches: {len(match_counts)}")

# Show top matched products
print("\n  Top matched products:")
product_name_map = {p["id"]: p["name"] for p in products}
for pid, cnt in sorted(match_counts.items(), key=lambda x: -x[1])[:15]:
    print(f"    {product_name_map.get(pid, pid)}: {cnt} items")

# Show sample unmatched
print("\n  Sample unmatched titles:")
for item in unmatched[:10]:
    print(f"    [{item['source']}] {item['title'][:80]}")

# =========================================================
# 4. Insert transactions into Supabase (batch)
# =========================================================
print(f"\nInserting {len(matched)} transactions into resale_transactions...")

BATCH_SIZE = 200
inserted_count = 0
for i in range(0, len(matched), BATCH_SIZE):
    batch = matched[i : i + BATCH_SIZE]
    resp = supabase.table("resale_transactions").insert(batch).execute()
    inserted_count += len(resp.data)
    print(f"  Batch {i // BATCH_SIZE + 1}: inserted {len(resp.data)} rows")

print(f"  Total inserted: {inserted_count}")

# =========================================================
# 5. Calculate predictions
# =========================================================
print("\nCalculating PRR predictions...")

# Get all transactions grouped by product
predictions = []
for product in products:
    pid = product["id"]
    new_price = product.get("new_price")
    if not new_price or new_price <= 0:
        continue

    # Get transactions for this product
    txn_resp = (
        supabase.table("resale_transactions")
        .select("sold_price")
        .eq("product_id", pid)
        .execute()
    )
    txns = txn_resp.data
    if not txns:
        continue

    prices = [t["sold_price"] for t in txns if t["sold_price"] and t["sold_price"] > 0]
    if not prices:
        continue

    median_price = statistics.median(prices)
    prr = median_price / new_price
    # Cap PRR at reasonable bounds
    prr = max(0.01, min(prr, 3.0))

    # Score: map PRR to 0-100 scale
    # PRR >= 1.0 -> 80-100 (holds/appreciates)
    # PRR 0.7-1.0 -> 50-80 (decent retention)
    # PRR 0.4-0.7 -> 25-50 (moderate loss)
    # PRR < 0.4 -> 0-25 (heavy loss)
    if prr >= 1.0:
        score = min(100, int(80 + (prr - 1.0) * 40))
    elif prr >= 0.7:
        score = int(50 + (prr - 0.7) / 0.3 * 30)
    elif prr >= 0.4:
        score = int(25 + (prr - 0.4) / 0.3 * 25)
    else:
        score = max(0, int(prr / 0.4 * 25))

    count = len(prices)
    if count >= 20:
        confidence = "high"
    elif count >= 5:
        confidence = "medium"
    else:
        confidence = "low"

    actual_cost_1year = max(0, int(new_price - median_price))

    # Simple decay curve (placeholder)
    decay_curve = {
        "6m": round(prr * 1.05, 3),  # slight premium short-term
        "1y": round(prr, 3),
        "2y": round(prr * 0.95, 3),
        "3y": round(prr * 0.90, 3),
    }

    predictions.append({
        "product_id": pid,
        "resale_score": score,
        "prr_6month": round(prr * 1.05, 4),
        "prr_1year": round(prr, 4),
        "prr_3year": round(prr * 0.90, 4),
        "actual_cost_1year": actual_cost_1year,
        "confidence": confidence,
        "transaction_count": count,
        "decay_curve": json.dumps(decay_curve),
        "model_version": "simple-prr-v1",
    })

print(f"  Predictions calculated for {len(predictions)} products")

# =========================================================
# 6. Upsert predictions via direct SQL (bypasses RLS)
# =========================================================
print("\nUpserting predictions into resale_predictions via REST RPC...")

import httpx

# Use the REST API with SQL via postgrest rpc or direct insert
# Since RLS blocks anon upsert on resale_predictions, we'll use
# supabase's rpc or try enabling insert policy. Let's use httpx + SQL endpoint.
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}

# Try upsert via PostgREST with Prefer header
url = f"{SUPABASE_URL}/rest/v1/resale_predictions"
upserted = 0
for pred in predictions:
    resp = httpx.post(url, json=pred, headers=HEADERS, timeout=30)
    if resp.status_code in (200, 201):
        upserted += 1
    else:
        # Try as a plain SQL via the management API is not available with anon key.
        # Let's print error and continue
        print(f"  Error upserting {product_name_map.get(pred['product_id'], '?')}: {resp.status_code} {resp.text[:200]}")
        break

if upserted < len(predictions):
    print(f"  PostgREST upsert blocked by RLS ({upserted}/{len(predictions)} succeeded)")
    print("  Falling back: printing SQL for manual execution...")
    # Generate SQL statements
    sql_parts = []
    for pred in predictions:
        decay = pred['decay_curve']
        sql_parts.append(
            f"INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version) "
            f"VALUES ('{pred['product_id']}', {pred['resale_score']}, {pred['prr_6month']}, {pred['prr_1year']}, {pred['prr_3year']}, {pred['actual_cost_1year']}, '{pred['confidence']}', {pred['transaction_count']}, '{decay}'::jsonb, '{pred['model_version']}') "
            f"ON CONFLICT (product_id) DO UPDATE SET "
            f"resale_score={pred['resale_score']}, prr_6month={pred['prr_6month']}, prr_1year={pred['prr_1year']}, prr_3year={pred['prr_3year']}, "
            f"actual_cost_1year={pred['actual_cost_1year']}, confidence='{pred['confidence']}', transaction_count={pred['transaction_count']}, "
            f"decay_curve='{decay}'::jsonb, model_version='{pred['model_version']}', updated_at=now();"
        )
    # Save SQL file
    sql_file = Path(__file__).resolve().parent / "upsert_predictions.sql"
    sql_file.write_text("\n".join(sql_parts), encoding="utf-8")
    print(f"  SQL saved to {sql_file}")
else:
    print(f"  Upserted {upserted} prediction rows")

# =========================================================
# 7. Summary
# =========================================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Total scraped items processed: {len(all_items)}")
print(f"Items matched to products:     {len(matched)} ({len(matched)/len(all_items)*100:.1f}%)")
print(f"Items unmatched:               {len(unmatched)} ({len(unmatched)/len(all_items)*100:.1f}%)")
print(f"Transactions inserted:         {inserted_count}")
print(f"Predictions created/updated:   {len(predictions)}")
print()
print("Predictions by confidence:")
high = sum(1 for p in predictions if p["confidence"] == "high")
med = sum(1 for p in predictions if p["confidence"] == "medium")
low = sum(1 for p in predictions if p["confidence"] == "low")
print(f"  High (>=20 txns):  {high}")
print(f"  Medium (>=5 txns): {med}")
print(f"  Low (<5 txns):     {low}")
print()
print("Top predictions by resale score:")
predictions.sort(key=lambda x: x["resale_score"], reverse=True)
for p in predictions[:10]:
    pname = product_name_map.get(p["product_id"], "?")
    print(f"  {pname}: score={p['resale_score']}, PRR_1y={p['prr_1year']:.2f}, txns={p['transaction_count']}, confidence={p['confidence']}")
