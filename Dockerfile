# Use Python 3.9 slim image for smaller size
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies including FFmpeg and curl
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port (Render typically uses 10000)
EXPOSE 10000

# Set environment variables
ENV FLASK_ENV=production
ENV LOG_LEVEL=INFO
ENV PYTHONUNBUFFERED=1

# Run the application (PORT will be set by Render)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 1 --timeout 300 --max-requests 100 --max-requests-jitter 10 app:app"]
