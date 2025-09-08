# Use official Python runtime as base image
FROM python:3.11-slim

# Install system dependencies including Graphviz
RUN apt-get update && \
    apt-get install -y \
    graphviz \
    graphviz-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads outputs

# Expose port
EXPOSE 5000

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
