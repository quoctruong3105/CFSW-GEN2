# ============================
# Stage 1: Build Dependencies
# ============================
FROM python:3.10-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

RUN pip3 install --no-cache-dir flask \
    psycopg2-binary \
    python-dotenv \
    pika \
    requests \
    debugpy

# ============================
# Stage 2: Final
# ============================
FROM python:3.10-slim AS final

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

CMD ["python", "app.py"]
