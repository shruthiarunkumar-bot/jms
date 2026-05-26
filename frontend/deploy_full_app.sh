#!/bin/bash

echo "🚀 Deploying Complete JobMatch AI Application..."

# Backend
echo "📦 Setting up backend..."
cd backend

# Create required directories
mkdir -p data uploads

# Ensure correct Python version
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD=python3.11
elif command -v python3.12 &> /dev/null; then
    PYTHON_CMD=python3.12
else
    echo "❌ Python 3.11 or 3.12 required"
    exit 1
fi

# Setup venv
rm -rf venv
$PYTHON_CMD -m venv venv
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"

echo "✅ Backend ready"

# Start backend in background
echo "🚀 Starting backend server..."
python -m app.main &
BACKEND_PID=$!

cd ..

# Frontend
echo "📦 Setting up frontend..."
cd frontend

# Install dependencies
npm install

echo "✅ Frontend ready"
echo "🚀 Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Application deployed successfully!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/docs"
echo ""
echo "To stop servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"

# Wait
wait
