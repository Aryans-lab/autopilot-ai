# NanoCorp Dockerfile
# Run your AI startup system anywhere!

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama (for completely free AI)
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY nanocorp/ ./nanocorp/
COPY setup.py README.md ./

# Create workspace
RUN mkdir -p /workspace

# Environment
ENV PYTHONUNBUFFERED=1
ENV OPENHANDS_SUPPRESS_BANNER=1

# Default command
CMD ["python", "-c", "from nanocorp import NanoCorpFree; print('NanoCorp ready!')"]

# Ports (for future web dashboard)
EXPOSE 8000 8080
