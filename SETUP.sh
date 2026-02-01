#!/bin/bash

# QUICK START GUIDE
# Run this script to set up everything automatically

echo "=========================================="
echo "Stock Investment Planner - Quick Setup"
echo "=========================================="
echo

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Found: $PYTHON_VERSION"
else
    echo "✗ Python 3 not found!"
    echo "  Install from: https://www.python.org/downloads/"
    exit 1
fi

# Check Ollama
echo
echo "Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
    
    # Check if running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo "✓ Ollama is running"
    else
        echo "⚠ Ollama is not running"
        echo "  Start it with: ollama serve"
        echo "  (or start the Ollama app on Mac/Windows)"
    fi
else
    echo "✗ Ollama not found!"
    echo "  Install from: https://ollama.com"
    exit 1
fi

# Check Git
echo
echo "Checking Git..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo "✓ Found: $GIT_VERSION"
else
    echo "⚠ Git not found (optional, needed for GitHub Pages)"
    echo "  Install from: https://git-scm.com"
fi

# Install Python packages
echo
echo "Installing Python dependencies..."
if pip install -r requirements.txt --break-system-packages 2>/dev/null || pip install -r requirements.txt; then
    echo "✓ Dependencies installed"
else
    echo "✗ Failed to install dependencies"
    echo "  Try: pip install -r requirements.txt"
    exit 1
fi

# Pull Ollama model
echo
echo "Checking Ollama model..."
MODEL="deepseek-r1:8b"

if ollama list | grep -q "$MODEL"; then
    echo "✓ Model $MODEL is ready"
else
    echo "⚠ Model $MODEL not found"
    read -p "Pull model now? This will download ~5GB (y/n): " PULL_MODEL
    
    if [ "$PULL_MODEL" = "y" ]; then
        echo "Pulling $MODEL..."
        ollama pull "$MODEL"
        echo "✓ Model downloaded"
    else
        echo "You can pull it later with: ollama pull $MODEL"
    fi
fi

# Create directories
echo
echo "Creating directories..."
mkdir -p reports stock-reports-github
echo "✓ Directories created"

# Test the system
echo
echo "=========================================="
echo "Running system tests..."
echo "=========================================="
echo

echo "1. Testing Ollama connection..."
python3 ollama_utils.py

echo
echo "2. Testing data fetching..."
python3 data_fetcher.py

# All done!
echo
echo "=========================================="
echo "Setup Complete! 🎉"
echo "=========================================="
echo
echo "Next steps:"
echo
echo "1. Configure your stocks:"
echo "   → Edit config.py"
echo "   → Change STOCKS = [\"GOOGL\"] to your preferred stocks"
echo
echo "2. Run your first analysis:"
echo "   → python3 run_analysis.py"
echo
echo "3. View the results:"
echo "   → Open stock-reports-github/index.html in your browser"
echo
echo "4. (Optional) Deploy to GitHub Pages:"
echo "   → bash setup_github.sh"
echo "   → bash deploy_to_github.sh"
echo
echo "5. (Optional) Set up automation:"
echo "   → python3 scheduler.py"
echo
echo "For full instructions, see README.md"
echo

read -p "Run first analysis now? (y/n): " RUN_NOW

if [ "$RUN_NOW" = "y" ]; then
    echo
    echo "Running analysis..."
    python3 run_analysis.py
    
    echo
    echo "Opening report in browser..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open stock-reports-github/index.html
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open stock-reports-github/index.html 2>/dev/null || echo "Open stock-reports-github/index.html in your browser"
    else
        echo "Open stock-reports-github/index.html in your browser"
    fi
fi

echo
echo "Happy investing! 📈💰"
echo
