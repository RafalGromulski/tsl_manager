# Use the official slim Python 3.13 base image
FROM python:3.13-slim

# Set environment variables to optimize Python behavior and pip:
# - PYTHONUNBUFFERED: Ensures logs are sent straight to terminal (useful for debugging)
# - PYTHONDONTWRITEBYTECODE: Prevents creation of .pyc files, keeping the image cleaner
# - PIP_NO_CACHE_DIR: Disables pip's cache to reduce image size
# - PIP_DISABLE_PIP_VERSION_CHECK: Speeds up builds by skipping pip version checks
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies (optional: uncomment if cron is required)
#RUN apt-get update  \
#    && apt-get install -y cron  \
#    && apt-get clean  \
#    && rm -rf /var/lib/apt/lists/*

# Create required directories for application runtime
# - /code/tsl_manager_downloader/data: application-specific storage
# - /var/log: system log directory
# - Create empty log files for Django and cron
RUN mkdir -p /code/tsl_manager_downloader/data &&  \
    mkdir -p /var/log  \
    && touch /var/log/django_cron.log /var/log/cron.log

# Define a mount point for persistent data storage (optional, currently commented out)
# VOLUME /code/tsl_crldownloader/data

# Set the working directory inside the container
WORKDIR /code

# Copy and install Python dependencies from requirements file
# Keeping this in a separate layer helps Docker cache it effectively
COPY requirements.txt .
RUN pip install --upgrade pip  \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code into the container
COPY . .

# Ensure the entrypoint script is executable
RUN chmod +x ./entrypoint.sh

# Expose the default port the app listens on
EXPOSE 8000

# Run the entrypoint script as the container's main process
ENTRYPOINT ["./entrypoint.sh"]
