FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gdal-bin libgdal-dev git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY scripts /app/scripts
COPY configs /app/configs
COPY db /app/db

RUN pip install --upgrade pip && pip install -e ".[dev]"

CMD ["python", "scripts/run_pipeline.py", "--config", "configs/base.yaml", "--stage", "validate"]
