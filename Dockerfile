# TaskPin — Django app with ASGI/WebSocket support (Daphne)
#
# Build:  docker compose build
# Run:    see docker-compose.yml header comments (migrate manually before first use)

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Daphne serves HTTP + WebSockets via ASGI
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "taskpin.asgi:application"]
