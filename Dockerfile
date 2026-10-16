# Production Multi-Stage Dockerfile for LocalShare
FROM python:3.13-slim AS base

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_CONFIG=production

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create non-root system user for security
RUN useradd -m -u 1001 localshare && \
    mkdir -p /app/data && \
    chown -R localshare:localshare /app

USER localshare

# Expose HTTP port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start production server using Waitress
CMD ["python", "-m", "waitress", "--listen=0.0.0.0:5000", "wsgi:app"]
