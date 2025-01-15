FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Run unit tests during build
RUN pytest tests/unit

# Healthcheck to ensure the container is healthy
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl --silent --fail http://localhost:8000/health || exit 1

# Expose the port and run the application
EXPOSE 8000

# Start the app and then run integration tests after startup
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port 8000 & pytest tests/integration"]
