FROM python:3.12-slim

WORKDIR /app

# Install build essentials, curl, and git
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# ARG for GitHub repository URL (default value for local builds)
ARG GITHUB_REPO=https://github.com/bikramadhikari001/synthenic.git
ARG GITHUB_BRANCH=main

# Clone from GitHub if running in production, else use local files
RUN if [ "$FLASK_ENV" = "production" ] ; then \
        git clone --depth 1 -b $GITHUB_BRANCH $GITHUB_REPO . ; \
    fi

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (this will be skipped in production due to .dockerignore)
COPY . .

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
