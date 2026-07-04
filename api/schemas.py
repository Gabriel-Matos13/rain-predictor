from datetime import date as date_type

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    date: date_type = Field(
        ...,
        description="Date to predict rain for, in Santo Domingo (YYYY-MM-DD).",
        examples=["2026-07-10"],
    )


class PredictResponse(BaseModel):
    date: date_type
    rain_probability: float = Field(..., ge=0.0, le=1.0)
    will_rain: bool
    source: str = Field(
        ..., description="'historical' if scored from recorded weather, 'forecast' if scored from a live forecast"
    )
    rain_threshold_mm: float
