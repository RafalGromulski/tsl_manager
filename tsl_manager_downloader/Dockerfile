# Use the official slim Python 3.11 base image
FROM python:3.11-slim

# Install system dependencies:
# - ca-certificates: required for SSL verification in HTTPS requests
# - curl: optional tool for diagnostics or healthchecks
# - update-ca-certificates: ensures certificates are current
# - cleanup removes unnecessary files to reduce image size
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

# Copy only the dependency definition file first for efficient Docker layer caching
COPY requirements.in .

# Upgrade pip, Install pip-tools, compile requirements.txt, and install dependencies
RUN pip install --no-cache-dir --upgrade pip pip-tools && \
    pip-compile requirements.in && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Copy the custom entrypoint script and ensure it is executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' --home /app celeryuser &&  \
    chown -R celeryuser:celeryuser /app

# Switch to the non-root user
USER celeryuser

# Set the container entrypoint to the custom script
ENTRYPOINT ["/app/entrypoint.sh"]
