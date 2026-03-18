"""Celery tasks for ML model training and prediction updates."""

import logging
import os

from celery import Celery

logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
app = Celery("resalelens", broker=REDIS_URL, backend=REDIS_URL)


@app.task(name="tasks.ml_tasks.retrain_model")
def retrain_model():
    """Retrain LightGBM model with latest transaction data."""
    import pandas as pd
    from supabase import create_client

    logger.info("Starting model retrain")

    supabase_url = os.environ.get("EXPO_PUBLIC_SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    supabase = create_client(supabase_url, supabase_key)

    # Fetch transaction data
    transactions = supabase.table("resale_transactions").select(
        "*, products(*, brands(*))"
    ).order("sold_date", desc=True).limit(10000).execute()

    if not transactions.data or len(transactions.data) < 50:
        logger.warning(f"Not enough data for training: {len(transactions.data or [])} records")
        return {"status": "skipped", "reason": "insufficient_data"}

    # TODO: Build features and train model once sufficient data collected
    # For now, generate predictions from aggregate statistics

    logger.info(f"Loaded {len(transactions.data)} transactions")

    # Calculate simple PRR per product
    products = supabase.table("products").select("id, new_price, brand_id, item_type, is_classic_model").execute()

    predictions_saved = 0
    for product in products.data:
        if not product.get("new_price"):
            continue

        product_id = product["id"]
        new_price = product["new_price"]

        # Get transactions for this product
        product_transactions = [
            t for t in transactions.data if t.get("product_id") == product_id
        ]

        if len(product_transactions) < 3:
            continue

        # Simple PRR calculation
        prices = [t["sold_price"] for t in product_transactions]
        median_price = sorted(prices)[len(prices) // 2]
        prr = median_price / new_price if new_price > 0 else 0

        # Score based on PRR
        if prr >= 1.0:
            score = min(99, int(80 + (prr - 1.0) * 100))
        else:
            score = max(1, int(prr * 80))

        confidence = "high" if len(product_transactions) >= 20 else (
            "medium" if len(product_transactions) >= 5 else "low"
        )

        try:
            supabase.table("resale_predictions").upsert({
                "product_id": product_id,
                "resale_score": score,
                "prr_1year": round(prr, 4),
                "prr_3year": round(prr * 0.85, 4),
                "prr_6month": round(prr * 1.05, 4),
                "actual_cost_1year": int(new_price * (1 - prr)),
                "confidence": confidence,
                "transaction_count": len(product_transactions),
                "model_version": "simple-v1",
                "decay_curve": [
                    {"month": 0, "prr": 1.0},
                    {"month": 6, "prr": round(prr * 1.05, 2)},
                    {"month": 12, "prr": round(prr, 2)},
                    {"month": 24, "prr": round(prr * 0.92, 2)},
                    {"month": 36, "prr": round(prr * 0.85, 2)},
                ],
            }, on_conflict="product_id").execute()
            predictions_saved += 1
        except Exception as e:
            logger.warning(f"Failed to save prediction for {product_id}: {e}")

    logger.info(f"Model retrain complete: {predictions_saved} predictions updated")
    return {"status": "complete", "predictions_saved": predictions_saved}
