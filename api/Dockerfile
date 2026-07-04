FROM python:3.11-slim

WORKDIR /app

COPY api/requirements.txt api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt

COPY api/ api/
COPY model/ model/
COPY data/santo_domingo_historical.csv data/santo_domingo_historical.csv

RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

WORKDIR /app/api

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
