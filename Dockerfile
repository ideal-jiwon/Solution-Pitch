# Base image
FROM python:3.11

# Install required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add a non-root user
RUN useradd -m appuser
USER appuser

# Set working directory
WORKDIR /app

# Copy ONLY the correct subfolder
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start the app with Gunicorn directly
CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:8000"]