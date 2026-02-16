# Stage 1: Build React Frontend
FROM node:18-alpine as build
WORKDIR /app
COPY stock-ai-app/package*.json ./
RUN npm ci
COPY stock-ai-app/ ./
RUN npm run build

# Stage 2: Python Backend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
# Install packages (using CPU-only torch to save space/time if possible, otherwise standard)
# We install numpy<2 first to ensure compatibility
RUN pip install "numpy<2.0.0" && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Set HF_HOME to a directory within /app so it persists
ENV HF_HOME=/app/model_cache
RUN mkdir -p /app/model_cache

# Copy and run model downloader
COPY backend/download_model.py .
RUN python download_model.py

# Copy backend code
COPY backend/app ./app

# Copy built frontend from Stage 1
COPY --from=build /app/dist ./static

# Expose port (Cloud Run uses 8080 by default, but we'll configure uvicorn to listen on $PORT)
ENV PORT=8080
EXPOSE 8080

# Run command
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
