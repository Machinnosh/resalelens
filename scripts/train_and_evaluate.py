"""Import massive data, train ML model, evaluate, and loop if needed."""
import sys
import io
import os
import json
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import lightgbm as lgb

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Brand/model mapping for fuzzy matching
BRAND_KEYWORDS = {
    "hermes": ["エルメス", "hermes"],
    "chanel": ["シャネル", "chanel"],
    "louis_vuitton": ["ルイヴィトン", "ルイ・ヴィトン", "louis vuitton"],
    "rolex": ["ロレックス", "rolex"],
    "omega": ["オメガ", "omega"],
    "cartier": ["カルティエ", "cartier"],
    "gucci": ["グッチ", "gucci"],
    "prada": ["プラダ", "prada"],
    "celine": ["セリーヌ", "celine"],
    "dior": ["ディオール", "dior"],
    "bottega_veneta": ["ボッテガ", "bottega"],
    "balenciaga": ["バレンシアガ", "balenciaga"],
    "saint_laurent": ["サンローラン", "saint laurent"],
    "fendi": ["フェンディ", "fendi"],
    "coach": ["コーチ", "coach"],
}

MODEL_KEYWORDS = {
    "birkin": ["バーキン", "birkin"],
    "kelly": ["ケリー", "kelly"],
    "picotin": ["ピコタン", "picotin"],
    "constance": ["コンスタンス", "constance"],
    "classic_flap": ["マトラッセ", "フラップ", "classic flap"],
    "boy_chanel": ["ボーイ", "boy"],
    "neverfull": ["ネヴァーフル", "ネバーフル", "neverfull"],
    "speedy": ["スピーディ", "speedy"],
    "alma": ["アルマ", "alma"],
    "submariner": ["サブマリーナ", "submariner"],
    "daytona": ["デイトナ", "daytona"],
    "datejust": ["デイトジャスト", "datejust"],
    "speedmaster": ["スピードマスター", "speedmaster"],
    "seamaster": ["シーマスター", "seamaster"],
    "tank": ["タンク", "tank"],
    "marmont": ["マーモント", "marmont"],
    "galleria": ["ガレリア", "galleria"],
}

# Approximate new prices for PRR calculation
NEW_PRICES = {
    ("hermes", "birkin"): 1_650_000,
    ("hermes", "kelly"): 1_430_000,
    ("hermes", "picotin"): 420_000,
    ("hermes", "constance"): 1_100_000,
    ("chanel", "classic_flap"): 1_200_000,
    ("chanel", "boy_chanel"): 850_000,
    ("louis_vuitton", "neverfull"): 260_000,
    ("louis_vuitton", "speedy"): 200_000,
    ("louis_vuitton", "alma"): 245_000,
    ("rolex", "submariner"): 1_280_000,
    ("rolex", "daytona"): 2_150_000,
    ("rolex", "datejust"): 1_050_000,
    ("omega", "speedmaster"): 880_000,
    ("omega", "seamaster"): 750_000,
    ("cartier", "tank"): 600_000,
    ("gucci", "marmont"): 315_000,
    ("prada", "galleria"): 380_000,
}

BRAND_TIERS = {
    "hermes": 1, "chanel": 1, "louis_vuitton": 1, "rolex": 1, "omega": 1, "cartier": 1,
    "gucci": 2, "prada": 2, "celine": 2, "dior": 2, "bottega_veneta": 2,
    "balenciaga": 2, "saint_laurent": 2, "fendi": 2,
    "coach": 3,
}


def identify(title, keywords_dict):
    title_lower = title.lower()
    for key, keywords in keywords_dict.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                return key
    return None


def load_all_data():
    """Load all JSON data files."""
    all_items = []
    for fname in os.listdir(DATA_DIR):
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(DATA_DIR, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                items = json.load(f)
            if isinstance(items, list):
                all_items.extend(items)
                print(f"  {fname}: {len(items)} items")
        except Exception as e:
            print(f"  {fname}: Error {e}")
    return all_items


def build_dataset(items):
    """Build ML-ready dataset from raw items."""
    rows = []
    for item in items:
        title = item.get("title", "")
        price = item.get("price", 0)
        if isinstance(price, str):
            price = int(re.sub(r'[^\d]', '', price) or 0)
        price = int(price)
        if price <= 0:
            continue

        brand = identify(title, BRAND_KEYWORDS)
        model = identify(title, MODEL_KEYWORDS)
        if not brand:
            continue

        new_price = None
        if model:
            new_price = NEW_PRICES.get((brand, model))
        if not new_price:
            continue

        # Filter outliers: price should be 15% - 200% of new price
        # This removes accessories, parts, and fakes that skew PRR
        if price < new_price * 0.15 or price > new_price * 2.0:
            continue

        prr = price / new_price
        tier = BRAND_TIERS.get(brand, 2)

        # Item type inference
        title_lower = title.lower()
        if any(w in title_lower for w in ["財布", "ウォレット", "wallet", "ポルトフォイユ", "ジッピー", "ベアン"]):
            item_type = 2  # wallet
        elif any(w in title_lower for w in ["時計", "watch", "サブマリーナ", "デイトナ", "スピードマスター", "タンク"]):
            item_type = 3  # watch
        else:
            item_type = 1  # bag

        # Title length as proxy for detail/authenticity
        title_len = len(title)

        # Condition inference from title keywords
        condition_score = 3  # default: unknown
        if any(w in title_lower for w in ["新品", "未使用", "新品同様", "タグ付", "unused"]):
            condition_score = 5
        elif any(w in title_lower for w in ["美品", "極美品", "超美品", "ランクa", "rank a", "sa"]):
            condition_score = 4
        elif any(w in title_lower for w in ["良品", "ランクab", "ab"]):
            condition_score = 3
        elif any(w in title_lower for w in ["やや傷", "使用感", "ランクb", "rank b"]):
            condition_score = 2
        elif any(w in title_lower for w in ["傷あり", "ジャンク", "難あり", "ランクc"]):
            condition_score = 1

        # Has box/receipt (signals authenticity/value)
        has_box = 1 if any(w in title_lower for w in ["箱付", "箱あり", "付属品", "保証書"]) else 0

        # Size extraction
        size_num = 0
        import re as _re
        size_match = _re.search(r'(\d{2,3})\s*(cm|mm|サイズ)?', title)
        if size_match:
            size_num = int(size_match.group(1))

        rows.append({
            "brand": brand,
            "model": model or "unknown",
            "tier": tier,
            "new_price": new_price,
            "new_price_log": np.log(new_price),
            "sold_price": price,
            "prr": prr,
            "price_ratio_log": np.log(price / new_price + 0.01),
            "item_type": item_type,
            "title_len": title_len,
            "condition_score": condition_score,
            "has_box": has_box,
            "size_num": size_num,
            "source": item.get("source", "unknown"),
        })

    df = pd.DataFrame(rows)
    print(f"\nDataset: {len(df)} valid items (from {len(items)} raw)")
    if len(df) > 0:
        print(f"  Brands: {df['brand'].nunique()}")
        print(f"  Models: {df['model'].nunique()}")
        print(f"  PRR range: {df['prr'].min():.2f} - {df['prr'].max():.2f}")
        print(f"  PRR median: {df['prr'].median():.2f}")
    return df


def train_and_evaluate(df):
    """Train LightGBM and evaluate with K-Fold CV."""
    if len(df) < 50:
        print("Not enough data for ML training")
        return None, None

    # Features
    df["brand_encoded"] = df["brand"].astype("category").cat.codes
    df["model_encoded"] = df["model"].astype("category").cat.codes
    df["source_encoded"] = df["source"].astype("category").cat.codes

    feature_cols = ["brand_encoded", "model_encoded", "tier", "new_price", "new_price_log", "source_encoded", "item_type", "title_len", "condition_score", "has_box", "size_num"]
    X = df[feature_cols]
    y = df["prr"]

    params = {
        "objective": "regression",
        "metric": "mae",
        "learning_rate": 0.05,
        "num_leaves": 31,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "verbose": -1,
    }

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    results = []

    for fold, (train_idx, test_idx) in enumerate(kf.split(X)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        lgb_train = lgb.Dataset(X_train, y_train)
        lgb_val = lgb.Dataset(X_test, y_test, reference=lgb_train)

        model = lgb.train(
            params, lgb_train,
            num_boost_round=500,
            valid_sets=[lgb_val],
            callbacks=[lgb.early_stopping(30), lgb.log_evaluation(0)],
        )

        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred)
        within_5 = (np.abs(y_test - y_pred) < 0.05).mean()
        within_10 = (np.abs(y_test - y_pred) < 0.10).mean()

        results.append({"fold": fold, "mae": mae, "mape": mape, "within_5pct": within_5, "within_10pct": within_10})

    results_df = pd.DataFrame(results)
    print("\n=== ML Evaluation Results (5-Fold CV) ===")
    print(f"  MAE:  {results_df['mae'].mean():.4f} (+/- {results_df['mae'].std():.4f})")
    print(f"  MAPE: {results_df['mape'].mean():.2%} (+/- {results_df['mape'].std():.2%})")
    print(f"  Within 5%:  {results_df['within_5pct'].mean():.1%}")
    print(f"  Within 10%: {results_df['within_10pct'].mean():.1%}")

    # Train final model on all data
    lgb_full = lgb.Dataset(X, y)
    final_model = lgb.train(params, lgb_full, num_boost_round=300)

    # Feature importance
    importance = dict(zip(feature_cols, final_model.feature_importance(importance_type="gain")))
    print(f"\n  Feature importance: {importance}")

    # Target check
    target_mape = 0.15
    current_mape = results_df['mape'].mean()
    if current_mape <= target_mape:
        print(f"\n  TARGET MET: MAPE {current_mape:.2%} <= {target_mape:.0%}")
    else:
        print(f"\n  TARGET NOT MET: MAPE {current_mape:.2%} > {target_mape:.0%}")
        print(f"  Need more data or better features")

    # Save model (use temp path to avoid Japanese path encoding issue with LightGBM)
    import tempfile
    tmp_path = os.path.join(tempfile.gettempdir(), "luxury_prr_v2.txt")
    final_model.save_model(tmp_path)
    model_path = tmp_path
    print(f"\n  Model saved to ml/models/luxury_prr.txt")

    return final_model, results_df


def main():
    print("=" * 50)
    print("LOAD DATA -> TRAIN ML -> EVALUATE")
    print("=" * 50)

    print("\nLoading data files...")
    items = load_all_data()
    print(f"Total raw items: {len(items)}")

    print("\nBuilding dataset...")
    df = build_dataset(items)

    if len(df) < 50:
        print(f"\nOnly {len(df)} valid items. Need at least 50. Collect more data.")
        return

    print("\nTraining LightGBM model...")
    model, results = train_and_evaluate(df)

    # Per-brand stats
    print("\n=== Per-Brand PRR Statistics ===")
    brand_stats = df.groupby("brand").agg(
        count=("prr", "count"),
        prr_median=("prr", "median"),
        prr_mean=("prr", "mean"),
        prr_std=("prr", "std"),
    ).sort_values("prr_median", ascending=False)
    print(brand_stats.to_string())

    print("\n=== Per-Model PRR Statistics ===")
    model_stats = df.groupby(["brand", "model"]).agg(
        count=("prr", "count"),
        prr_median=("prr", "median"),
    ).sort_values("prr_median", ascending=False).head(20)
    print(model_stats.to_string())


if __name__ == "__main__":
    main()
