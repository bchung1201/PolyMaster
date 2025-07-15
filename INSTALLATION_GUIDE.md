# 📦 PolyAgent Web Installation Guide

## 🎯 **Quick Install (Recommended)**

### **1. Backend Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### **2. Frontend Dependencies**
```bash
cd frontend
npm install
```

### **3. Python Requirements (if missing)**
```bash
# If you need to install Python dependencies individually
pip install fastapi uvicorn python-dotenv pydantic pydantic-settings
pip install openai langchain langchain-openai langchain-community langchain-core
pip install newsapi-python tavily-python chromadb
pip install web3 py-clob-client py-order-utils
pip install spacy scikit-learn numpy pandas
pip install httpx aiohttp requests
pip install colorama typer devtools
pip install pytest pytest-asyncio
```

### **4. System Dependencies**
```bash
# spaCy language model (required for NLP)
python -m spacy download en_core_web_sm

# Node.js version (if you need to install/update)
# Visit: https://nodejs.org/ or use nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install --lts
nvm use --lts
```

## 🔧 **Detailed Installation**

### **Backend Python Environment**

#### **Option A: Using pip (Recommended)**
```bash
cd backend

# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(fastapi|openai|langchain|web3)"
```

#### **Option B: Using conda**
```bash
cd backend

# Create conda environment
conda create -n polyagent python=3.11
conda activate polyagent

# Install packages
pip install -r requirements.txt
```

#### **Option C: Using virtual environment**
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
```

### **Frontend Node.js Environment**

#### **Option A: Using npm (Default)**
```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm list --depth=0
```

#### **Option B: Using yarn**
```bash
cd frontend

# Install yarn if not available
npm install -g yarn

# Install dependencies
yarn install
```

#### **Option C: Using pnpm**
```bash
cd frontend

# Install pnpm if not available
npm install -g pnpm

# Install dependencies
pnpm install
```

## 🛠 **System Requirements**

### **Minimum Requirements:**
- **Python:** 3.9+ (3.11 recommended)
- **Node.js:** 18+ (20 LTS recommended)
- **npm:** 9+
- **Memory:** 4GB RAM minimum
- **Storage:** 2GB free space

### **Recommended Setup:**
- **Python:** 3.11
- **Node.js:** 20 LTS
- **npm:** 10+
- **Memory:** 8GB+ RAM
- **Storage:** 5GB+ free space

## 📋 **Package Verification**

### **Backend Package Check**
```bash
cd backend
python3 -c "
import sys
packages = [
    'fastapi', 'uvicorn', 'pydantic', 'openai', 'langchain',
    'web3', 'httpx', 'numpy', 'pandas', 'spacy'
]

missing = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError:
        missing.append(pkg)
        print(f'❌ {pkg}')

if missing:
    print(f'\n📦 Install missing: pip install {\" \".join(missing)}')
else:
    print('\n🎉 All backend packages installed!')
"
```

### **Frontend Package Check**
```bash
cd frontend
npm list --depth=0 2>/dev/null | grep -E "(react|next|typescript|tailwindcss)" || echo "❌ Some packages missing"
```

### **spaCy Model Check**
```bash
python3 -c "
import spacy
try:
    nlp = spacy.load('en_core_web_sm')
    print('✅ spaCy English model installed')
except OSError:
    print('❌ spaCy model missing - run: python -m spacy download en_core_web_sm')
"
```

## 🚨 **Troubleshooting Common Issues**

### **Backend Issues**

#### **1. Python Version Issues**
```bash
# Check Python version
python3 --version

# If < 3.9, install newer version:
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
# Windows: Download from python.org
```

#### **2. Pip Installation Issues**
```bash
# Upgrade pip
python3 -m pip install --upgrade pip

# Clear pip cache
pip cache purge

# Install with no cache
pip install --no-cache-dir -r requirements.txt
```

#### **3. Web3 Installation Issues**
```bash
# On macOS, you might need:
brew install gmp

# On Ubuntu:
sudo apt-get install libgmp-dev

# Then reinstall web3
pip uninstall web3
pip install web3
```

#### **4. spaCy Model Issues**
```bash
# Download English model
python -m spacy download en_core_web_sm

# If download fails, try:
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

### **Frontend Issues**

#### **1. Node.js Version Issues**
```bash
# Check Node.js version
node --version

# Install/update Node.js using nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install --lts
nvm use --lts
```

#### **2. npm Installation Issues**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Try with legacy peer deps
npm install --legacy-peer-deps
```

#### **3. Permission Issues (Linux/macOS)**
```bash
# Fix npm permissions
sudo chown -R $(whoami) ~/.npm
sudo chown -R $(whoami) /usr/local/lib/node_modules

# Or use nvm instead of system Node.js
```

### **Memory Issues**
```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max_old_space_size=4096"

# For npm install issues
npm install --max_old_space_size=4096
```

## 🎯 **Installation Scripts**

### **Complete Setup Script (Linux/macOS)**
```bash
#!/bin/bash
# save as install.sh

echo "🚀 Installing PolyAgent Web..."

# Backend
echo "📦 Installing backend dependencies..."
cd backend
pip3 install --upgrade pip
pip3 install -r requirements.txt
python3 -m spacy download en_core_web_sm

# Frontend
echo "🎨 Installing frontend dependencies..."
cd ../frontend
npm install

echo "✅ Installation complete!"
echo "Next steps:"
echo "1. Create backend/.env file"
echo "2. cd backend && python3 app.py"
echo "3. cd frontend && npm run dev"
```

### **Complete Setup Script (Windows)**
```batch
@echo off
echo Installing PolyAgent Web...

echo Installing backend dependencies...
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm

echo Installing frontend dependencies...
cd ..\frontend
npm install

echo Installation complete!
echo Next steps:
echo 1. Create backend\.env file
echo 2. cd backend && python app.py
echo 3. cd frontend && npm run dev
pause
```

## 🔍 **Verify Installation**

### **Run Complete Verification**
```bash
# Run the quick test script
python3 quick_test.py

# If that passes, you're ready to go!
```

### **Manual Verification**
```bash
# 1. Test backend imports
cd backend
python3 -c "from agents.ai.executor import Executor; print('Backend OK')"

# 2. Test frontend build
cd ../frontend
npm run build

# 3. Test API startup
cd ../backend
timeout 10s python3 app.py &
sleep 5
curl http://localhost:8000/health
```

## 📝 **Installation Summary**

### **Minimum Installation (5 minutes):**
1. `cd backend && pip install -r requirements.txt`
2. `python -m spacy download en_core_web_sm`
3. `cd ../frontend && npm install`
4. `python3 quick_test.py` to verify

### **Complete Installation (10 minutes):**
1. Set up virtual environment
2. Install all dependencies
3. Download language models
4. Verify installation
5. Create .env file
6. Test full application

### **Production Installation:**
1. Use Docker (if you want containerization)
2. Set up reverse proxy (nginx)
3. Configure environment variables
4. Set up monitoring
5. Enable HTTPS

Your PolyAgent Web application will be ready to run! 🎉