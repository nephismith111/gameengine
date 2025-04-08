FROM ubuntu:24.04

WORKDIR /app

# Set noninteractive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    python3 \
    python3-pip \
    python3-dev \
    python3-full

# Copy requirements and install dependencies
# Use --break-system-packages since we're in a container
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy project files
COPY . .

# Expose ports
EXPOSE 8000
EXPOSE 8080

# Command to run
CMD ["python3", "project/gameengine/manage.py", "runserver", "0.0.0.0:8000"]
