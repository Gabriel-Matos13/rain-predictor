"""Open-Meteo client for fetching daily weather values for Santo Domingo."""

from datetime import date as date_type

import requests

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

LATITUDE = 18.4861
LONGITUDE = -69.9312
TIMEZONE = "America/Santo_Domingo"

REQUEST_TIMEOUT_SECONDS = 10
MAX_FORECAST_HORIZON_DAYS = 16

# Open-Meteo daily response key -> internal feature name used by the trained model.
# wind_speed_10m_max is the current Open-Meteo name; the model was trained on a
# column named windspeed_10m_max (legacy alias, same underlying values).
DAILY_VAR_MAP = {
    "temperature_2m_max": "temperature_2m_max",
    "temperature_2m_min": "temperature_2m_min",
    "temperature_2m_mean": "temperature_2m_mean",
    "relative_humidity_2m_mean": "relative_humidity_2m_mean",
    "surface_pressure_mean": "surface_pressure_mean",
    "wind_speed_10m_max": "windspeed_10m_max",
}


class WeatherLookupError(Exception):
    """Raised when weather data for the requested date can't be retrieved."""


def _extract_daily_values(payload: dict, requested_date: date_type) -> dict:
    daily = payload.get("daily") or {}
    times = daily.get("time") or []
    target = requested_date.isoformat()
    if target not in times:
        raise WeatherLookupError(f"No weather data returned for {target}")
    idx = times.index(target)

    values = {}
    for api_key, feature_name in DAILY_VAR_MAP.items():
        series = daily.get(api_key)
        if not series or idx >= len(series) or series[idx] is None:
            raise WeatherLookupError(f"Missing '{api_key}' for {target}")
        values[feature_name] = series[idx]
    return values


def _fetch_daily(base_url: str, requested_date: date_type) -> dict:
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": requested_date.isoformat(),
        "end_date": requested_date.isoformat(),
        "daily": ",".join(DAILY_VAR_MAP.keys()),
        "timezone": TIMEZONE,
    }
    try:
        response = requests.get(base_url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise WeatherLookupError(f"Weather API request to {base_url} failed: {exc}") from exc
    return _extract_daily_values(response.json(), requested_date)


def fetch_archive_day(requested_date: date_type) -> dict:
    """Fetch recorded (reanalysis) weather for a past date."""
    return _fetch_daily(ARCHIVE_URL, requested_date)


def fetch_forecast_day(requested_date: date_type) -> dict:
    """Fetch forecast (or recent blended-observation) weather for a date.

    The forecast API also serves recent past days, so it doubles as a
    fallback for dates too recent to have landed in the reanalysis archive.
    """
    return _fetch_daily(FORECAST_URL, requested_date)
