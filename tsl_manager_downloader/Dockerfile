# Use the official slim Python 3.11 base image
FROM python:3.11-slim

# Install system dependencies:
# - ca-certificates: required for SSL verification (HTTPS)
# - curl: useful for diagnostics or healthchecks
# - procps: provides tools like ps/top (useful for debugging or monitoring)
# - Clean up afterwards to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl procps &&  \
    update-ca-certificates &&  \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables to optimize Python behavior and pip:
# - PYTHONUNBUFFERED: Ensures logs are sent straight to terminal (useful for debugging)
# - PYTHONDONTWRITEBYTECODE: Prevents creation of .pyc files, keeping the image cleaner
# - PIP_NO_CACHE_DIR: Disables pip's cache to reduce image size
# - PIP_DISABLE_PIP_VERSION_CHECK: Speeds up builds by skipping pip version checks
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory inside the container
WORKDIR /app

# Copy Python dependencies from requirements file
# Keeping this in a separate layer helps Docker cache it effectively
COPY requirements.in .

# Upgrade pip, Install pip-tools, compile requirements.txt, and install dependencies
# Uninstall pip-tools after build to reduce image size
RUN pip install --no-cache-dir --upgrade pip pip-tools && \
    pip-compile requirements.in && \
    pip install --no-cache-dir -r requirements.txt &&  \
    pip uninstall -y pip-tools

# Copy the rest of the application source code into the container
COPY . .

# Adding directories for Celery
RUN mkdir -p /app/logs /app/tsl_downloads /app/celerybeat-data
