# Multi-stage Dockerfile for Discord Bot with FastAPI + React UI

# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build for production
RUN npm run build

# Stage 2: Python Backend + Bot
FROM python:3.14-slim

LABEL maintainer=cyb3rgh05t
LABEL org.opencontainers.image.source=https://github.com/cyb3rgh05t/discord-bot

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy version file
COPY version.txt ./

# Copy application code
COPY . .

# Copy built frontend from Stage 1
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Expose API port
EXPOSE 5000

# Run the bot (FastAPI will start automatically if WEB_ENABLED=True)
CMD ["python", "bot.py"]
