#!/bin/bash

# GOLD FUNDAMENTAL MASTER - 24/7 VPS Deployment Script
set -e

echo "=================================================="
echo "🚀 GOLD FUNDAMENTAL MASTER - 24/7 VPS Deployment"
echo "=================================================="

# Update and install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker and Docker Compose..."
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg lsb-release
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

# Ensure .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️ Please edit .env with your real TELEGRAM_BOT_TOKEN and OPENROUTER_API_KEY if not in MOCK_MODE."
fi

# Build and launch Docker containers in detached mode (24/7 background)
echo "🐳 Building and starting Docker containers..."
docker compose down || true
docker compose up --build -d

echo "✅ System launched in background!"
echo "=================================================="
echo "📊 Status checks:"
echo "FastAPI Backend: http://localhost:8000/health"
echo "Telegram Mini App: http://localhost"
echo "=================================================="
