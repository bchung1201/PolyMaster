#!/bin/bash
# PolyAgent Web Auto-Installer
# Run with: chmod +x install.sh && ./install.sh

set -e  # Exit on any error

echo "🚀 PolyAgent Web Auto-Installer"
echo "================================"

# Check if we're in the right directory
if [[ ! -d "backend" || ! -d "frontend" ]]; then
    echo "❌ Please run this script from the project root directory"
    echo "   (where backend/ and frontend/ folders are located)"
    exit 1
fi

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.9"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "✅ Python $python_version (compatible)"
else
    echo "❌ Python $python_version is too old. Need Python 3.9+"
    echo "   Please install a newer Python version"
    exit 1
fi

# Check Node.js version
echo "📦 Checking Node.js version..."
if command -v node >/dev/null 2>&1; then
    node_version=$(node --version)
    echo "✅ Node.js $node_version"
else
    echo "❌ Node.js not found. Please install Node.js 18+"
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Install backend dependencies
echo ""
echo "📚 Installing backend dependencies..."
cd backend

# Upgrade pip
echo "   Upgrading pip..."
python3 -m pip install --upgrade pip --quiet

# Install requirements (skip TensorFlow which isn't used)
echo "   Installing Python packages..."
if pip3 install -r requirements-minimal.txt --quiet; then
    echo "✅ Backend packages installed (minimal set)"
elif pip3 install -r requirements.txt --constraint <(echo "tensorflow==999.999.999") --quiet; then
    echo "✅ Backend packages installed (skipped TensorFlow)"
else
    echo "❌ Failed to install backend packages"
    echo "   Try running manually: cd backend && pip install -r requirements-minimal.txt"
    echo "   Or see TENSORFLOW_TROUBLESHOOTING.md for help"
    exit 1
fi

# Download spaCy model
echo "   Downloading spaCy English model..."
if python3 -m spacy download en_core_web_sm --quiet >/dev/null 2>&1; then
    echo "✅ spaCy model downloaded"
else
    echo "⚠️  spaCy model download failed (you can install it later)"
fi

# Install frontend dependencies
echo ""
echo "🎨 Installing frontend dependencies..."
cd ../frontend

# Install npm packages
echo "   Installing npm packages..."
if npm install --silent >/dev/null 2>&1; then
    echo "✅ Frontend packages installed"
else
    echo "❌ Failed to install frontend packages"
    echo "   Try running manually: cd frontend && npm install"
    exit 1
fi

# Create .env file if it doesn't exist
echo ""
echo "⚙️  Setting up environment..."
cd ../backend

if [[ ! -f ".env" ]]; then
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        echo "✅ Created .env file from template"
        echo "   📝 Remember to add your API keys to backend/.env"
    else
        cat > .env << 'EOF'
# PolyAgent Web Environment Variables
OPENAI_API_KEY=your_openai_api_key_here
DRY_RUN=true
POLYGON_WALLET_PRIVATE_KEY=
CLOB_API_KEY=
CLOB_SECRET=
CLOB_PASS_PHRASE=
NEWSAPI_API_KEY=
TAVILY_API_KEY=
EOF
        echo "✅ Created basic .env file"
        echo "   📝 Remember to add your API keys to backend/.env"
    fi
else
    echo "✅ .env file already exists"
fi

# Run verification test
echo ""
echo "🧪 Running verification tests..."
cd ..

if python3 quick_test.py; then
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Add your API keys to backend/.env (at minimum: OPENAI_API_KEY)"
    echo "2. Start the backend:"
    echo "   cd backend && python3 app.py"
    echo "3. Start the frontend (in a new terminal):"
    echo "   cd frontend && npm run dev"
    echo "4. Open http://localhost:3000 in your browser"
    echo ""
    echo "🔑 Required API keys:"
    echo "   - OPENAI_API_KEY (required for AI features)"
    echo "   - Others are optional for full functionality"
    echo ""
else
    echo ""
    echo "⚠️  Installation completed but tests failed"
    echo "   Check the errors above and run: python3 quick_test.py"
    echo "   Most likely you need to add API keys to backend/.env"
fi