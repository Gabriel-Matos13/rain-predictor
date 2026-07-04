"""Loads the trained model once at import time and scores feature vectors."""

import json
from datetime import date as date_type
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd

MODEL_DIR = Path(__file__).resolve().parent.parent / "model"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_model = joblib.load(MODEL_DIR / "model.pkl")

with open(MODEL_DIR / "feature_config.json") as f:
    _feature_config = json.load(f)

FEATURE_COLUMNS = _feature_config["feature_columns"]
RAIN_THRESHOLD_MM = _feature_config["rain_threshold_mm"]

_WEATHER_COLUMNS = [c for c in FEATURE_COLUMNS if c not in ("month_sin", "month_cos")]

_historical_df = pd.read_csv(DATA_DIR / "santo_domingo_historical.csv", parse_dates=["date"])
_historical_df.index = _historical_df["date"].dt.date


def lookup_cached_day(requested_date: date_type) -> Optional[dict]:
    """Return recorded weather for a date already present in the cached CSV, if any."""
    if requested_date not in _historical_df.index:
        return None
    row = _historical_df.loc[requested_date]
    return {col: float(row[col]) for col in _WEATHER_COLUMNS}


def build_feature_vector(weather_values: dict, requested_date: date_type) -> pd.DataFrame:
    month = requested_date.month
    features = {
        **weather_values,
        "month_sin": np.sin(2 * np.pi * month / 12),
        "month_cos": np.cos(2 * np.pi * month / 12),
    }
    return pd.DataFrame([[features[col] for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)


def predict_rain_probability(weather_values: dict, requested_date: date_type) -> float:
    X = build_feature_vector(weather_values, requested_date)
    return float(_model.predict_proba(X)[0, 1])
