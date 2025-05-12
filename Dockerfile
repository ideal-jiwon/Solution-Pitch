# Base image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy files to container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start the app with Gunicorn directly
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-8000}"]

