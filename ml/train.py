"""ResaleLens ML Training Pipeline - LightGBM PRR Predictor."""

import json
import logging
from pathlib import Path

import lightgbm as lgb
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from sklearn.model_selection import TimeSeriesSplit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)


class ResalePRRPredictor:
    """LightGBM model for predicting Price Retention Ratio."""

    def __init__(self):
        self.model = None
        self.params = {
            "objective": "regression",
            "metric": "mae",
            "learning_rate": 0.05,
            "num_leaves": 31,
            "feature_fraction": 0.8,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "verbose": -1,
        }

    def train(self, X_train, y_train, X_val, y_val):
        lgb_train = lgb.Dataset(X_train, y_train)
        lgb_val = lgb.Dataset(X_val, y_val, reference=lgb_train)

        self.model = lgb.train(
            self.params,
            lgb_train,
            num_boost_round=1000,
            valid_sets=[lgb_val],
            callbacks=[lgb.early_stopping(50), lgb.log_evaluation(100)],
        )

        y_pred = self.model.predict(X_val)
        mae = mean_absolute_error(y_val, y_pred)
        mape = mean_absolute_percentage_error(y_val, y_pred)
        logger.info(f"Validation MAE: {mae:.4f}, MAPE: {mape:.2%}")
        return {"mae": mae, "mape": mape}

    def predict(self, X):
        if self.model is None:
            raise RuntimeError("Model not trained or loaded")
        return self.model.predict(X)

    def save(self, path=None):
        path = path or str(MODEL_DIR / "luxury_prr.txt")
        self.model.save_model(path)
        logger.info(f"Model saved to {path}")

    def load(self, path=None):
        path = path or str(MODEL_DIR / "luxury_prr.txt")
        self.model = lgb.Booster(model_file=path)
        logger.info(f"Model loaded from {path}")

    def feature_importance(self):
        if self.model is None:
            return {}
        names = self.model.feature_name()
        importances = self.model.feature_importance(importance_type="gain")
        return dict(sorted(zip(names, importances), key=lambda x: -x[1]))


class FeatureBuilder:
    """Build feature matrix from raw transaction data."""

    PRODUCT_FEATURES = [
        "new_price", "days_since_release", "brand_encoded",
        "item_type", "model_encoded", "size_encoded",
        "material_encoded", "is_classic_model", "brand_tier",
    ]
    MARKET_FEATURES = [
        "transaction_volume_30d", "listing_count_active",
        "median_price_30d", "price_stddev_30d", "price_trend_30d",
    ]
    TEMPORAL_FEATURES = ["month_of_year", "is_bonus_season"]

    @staticmethod
    def build(df: pd.DataFrame) -> pd.DataFrame:
        """Build features from transaction DataFrame."""
        features = pd.DataFrame()

        # Product features
        features["new_price"] = df["new_price"]
        features["days_since_release"] = (
            pd.to_datetime("today") - pd.to_datetime(df["release_date"])
        ).dt.days
        features["brand_encoded"] = df["brand"].astype("category").cat.codes
        features["item_type"] = df["item_type"].astype("category").cat.codes
        features["model_encoded"] = df["model"].astype("category").cat.codes
        features["is_classic_model"] = df["is_classic_model"].astype(int)
        features["brand_tier"] = df["brand_tier"]

        # Temporal
        features["month_of_year"] = pd.to_datetime(df["sold_date"]).dt.month
        features["is_bonus_season"] = features["month_of_year"].isin([6, 7, 12]).astype(int)

        return features


def evaluate_model(model: ResalePRRPredictor, X, y, n_splits=5):
    """Time series cross-validation evaluation."""
    tscv = TimeSeriesSplit(n_splits=n_splits)
    results = []

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
        y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]

        metrics = model.train(X_tr, y_tr, X_te, y_te)
        y_pred = model.predict(X_te)

        results.append({
            "fold": fold,
            "mae": metrics["mae"],
            "mape": metrics["mape"],
            "within_5pct": (abs(y_te - y_pred) < 0.05).mean(),
            "within_10pct": (abs(y_te - y_pred) < 0.10).mean(),
        })
        logger.info(f"Fold {fold}: MAE={metrics['mae']:.4f}, MAPE={metrics['mape']:.2%}")

    results_df = pd.DataFrame(results)
    logger.info(f"\n=== Cross-Validation Results ===\n{results_df.describe()}")
    return results_df


if __name__ == "__main__":
    logger.info("ResaleLens ML Training Pipeline")
    logger.info("Waiting for scraped data to begin training...")
    logger.info("Run scrapers first: python -m scrapers.mercari")
