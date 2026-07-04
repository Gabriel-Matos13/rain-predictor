---
title: Santo Domingo Rain Predictor API
emoji: ☔
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Santo Domingo Rain Predictor — API

FastAPI backend that serves rain-probability predictions for Santo Domingo from a
logistic-regression model, using Open-Meteo weather data.

- `POST /predict` — body `{"date": "YYYY-MM-DD"}` → rain probability. Past dates are
  scored from recorded weather; future dates (≤16 days) are scored from a live
  Open-Meteo forecast fetched server-side.
- `GET /health` — health check.
- Interactive docs at `/docs`.

Source & full project: https://github.com/Gabriel-Matos13/rain-predictor
