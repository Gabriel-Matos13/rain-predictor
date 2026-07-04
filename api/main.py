from datetime import date as date_type

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import model_service
import weather
from schemas import PredictRequest, PredictResponse

app = FastAPI(title="Santo Domingo Rain Predictor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    requested_date = request.date
    today = date_type.today()

    if requested_date > today:
        horizon_days = (requested_date - today).days
        if horizon_days > weather.MAX_FORECAST_HORIZON_DAYS:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"{requested_date} is {horizon_days} days out; forecasts are only "
                    f"available up to {weather.MAX_FORECAST_HORIZON_DAYS} days ahead."
                ),
            )
        try:
            weather_values = weather.fetch_forecast_day(requested_date)
        except weather.WeatherLookupError as exc:
            raise HTTPException(status_code=502, detail=f"Could not retrieve forecast: {exc}") from exc
        source = "forecast"
    else:
        cached = model_service.lookup_cached_day(requested_date)
        if cached is not None:
            weather_values, source = cached, "historical"
        else:
            try:
                weather_values, source = weather.fetch_archive_day(requested_date), "historical"
            except weather.WeatherLookupError:
                # Very recent past dates may not have landed in the reanalysis
                # archive yet; the forecast API also serves recent-past days.
                try:
                    weather_values, source = weather.fetch_forecast_day(requested_date), "forecast"
                except weather.WeatherLookupError as exc:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Could not retrieve weather data for {requested_date}: {exc}",
                    ) from exc

    probability = model_service.predict_rain_probability(weather_values, requested_date)

    return PredictResponse(
        date=requested_date,
        rain_probability=round(probability, 4),
        will_rain=probability >= 0.5,
        source=source,
        rain_threshold_mm=model_service.RAIN_THRESHOLD_MM,
    )
