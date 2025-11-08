#!/bin/bash
# Setup script for RAG One

set -e

echo "🚀 Setting up RAG One..."

# Check Python version
echo "📋 Checking Python version..."
python3 --version || {
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
}

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "✅ Created .env file. Edit it if needed."
else
    echo "✅ .env file already exists"
fi

# Create directories
echo "📁 Creating data directories..."
mkdir -p data/documents
mkdir -p data/vector_store

# Make scripts executable
chmod +x run_cli.sh run_web.sh

# Test Ollama connection
echo ""
echo "🔍 Testing Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is accessible at http://localhost:11434"
    echo ""
    echo "Available models:"
    curl -s http://localhost:11434/api/tags | python3 -m json.tool 2>/dev/null || echo "Unable to parse models"
else
    echo "⚠️  Cannot connect to Ollama at http://localhost:11434"
    echo "   Make sure Ollama is running on Windows"
    echo "   You may need to configure OLLAMA_BASE_URL in .env"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Add documents to: data/documents/"
echo "3. Index documents: python -m src.cli index"
echo "4. Run CLI: python -m src.cli query -i"
echo "   Or run Web UI: streamlit run src/web_ui.py"
echo ""
echo "For detailed instructions, see README_DETAILED.md"
