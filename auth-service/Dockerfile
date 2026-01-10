# -------- Base image --------
    FROM python:3.13-slim

    # -------- System deps --------
    RUN apt-get update && apt-get install -y \
        build-essential \
        && rm -rf /var/lib/apt/lists/*
    
    # -------- Environment --------
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    # -------- Workdir --------
    WORKDIR /app
    
    # -------- Dependencies --------
    # Poetry
    RUN pip install --no-cache-dir poetry
    
    COPY pyproject.toml poetry.lock* ./
    RUN poetry config virtualenvs.create false \
        && poetry install --no-interaction --no-ansi --only main
    
    # -------- App code --------
    COPY app ./app
    COPY alembic ./alembic
    
    # -------- Expose --------
    EXPOSE 8000
    
    # -------- Run --------
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    