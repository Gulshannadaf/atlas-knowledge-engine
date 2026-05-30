#!/bin/bash
# =============================================================================
# Atlas - Development Setup Script
# =============================================================================

set -e

echo "🚀 Setting up Atlas development environment..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys"
fi

# Start infrastructure services
echo "🐳 Starting infrastructure services..."
cd docker
docker compose up -d postgres redis qdrant
cd ..

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Setup backend
echo "🐍 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cd ..

# Setup frontend
echo "📦 Setting up frontend..."
cd frontend
npm install
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start development:"
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "Or use Docker:"
echo "  cd docker && docker compose up"
echo ""
