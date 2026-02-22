# Stage 1: Build React Frontend
FROM node:20-alpine as build
WORKDIR /app
COPY stock-ai-app/package*.json ./
RUN npm ci --quiet
COPY stock-ai-app/ ./
RUN npm run build

# Stage 2: Python Backend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for HMM and Chronos (including git for the github repo)
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies using uv
COPY requirements.txt .
RUN pip install uv && \
    uv pip install --system --no-cache "numpy<2.0.0" && \
    uv pip install --system --no-cache torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu && \
    uv pip install --system --no-cache -r requirements.txt

# Copy application files
COPY server.py .
COPY backend/ ./backend/

# Copy built frontend from Stage 1
COPY --from=build /app/dist ./static

# Set environment
ENV PORT=8080
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
ENV OMP_NUM_THREADS=1

# Run command
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
