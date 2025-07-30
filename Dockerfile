# Build stage for Python dependencies
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY . .

# Make sure scripts are executable
RUN chmod +x run.py

# Set ownership of the application directory
RUN chown -R app:app /app

USER app

# Expose port
EXPOSE 8080

# Set default port
ENV PORT=8080

# Run the application
CMD python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT