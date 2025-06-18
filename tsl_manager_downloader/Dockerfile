# Use the official slim Python 3.11 base image
FROM python:3.11-slim

# Install system dependencies:
# - ca-certificates: ensures HTTPS requests can verify SSL certificates
# - cleanup removes unnecessary files to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

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

# Copy the rest of the application source code into the container
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Define the default command to run the application
CMD ["python", "downloader.py"]
