# -------- Base image --------
    FROM python:3.13-slim

    # -------- Environment --------
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    # -------- Workdir --------
    WORKDIR /app
    
    # -------- Dependencies --------
    RUN pip install --no-cache-dir poetry
    
    COPY pyproject.toml poetry.lock* ./
    RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --no-root

    # -------- App code --------
    COPY app ./app
    
    # -------- Expose --------
    EXPOSE 8000
    
    # -------- Run --------
    CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

    