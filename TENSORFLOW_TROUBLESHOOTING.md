# 🔧 TensorFlow Installation Troubleshooting

## 🎯 **Quick Solution: Skip TensorFlow (Recommended)**

**TensorFlow is NOT used in PolyAgent Web!** The requirements.txt includes it unnecessarily. 

### **Option 1: Use Minimal Requirements (Fastest)**
```bash
cd backend
pip install -r requirements-minimal.txt
python -m spacy download en_core_web_sm
```

This installs only the packages actually needed by PolyAgent Web.

### **Option 2: Install Without TensorFlow**
```bash
cd backend
# Install everything except TensorFlow packages
pip install --constraint <(grep -v -E "(tensorflow|tf-keras|keras|gymnasium)" requirements.txt) -r requirements.txt
```

### **Option 3: Skip TensorFlow in Original Requirements**
```bash
cd backend
pip install -r requirements.txt --constraint <(echo "tensorflow==999.999.999")
```

## 🐛 **If You Need TensorFlow (Advanced Users)**

### **macOS Solutions**

#### **Apple Silicon (M1/M2/M3):**
```bash
# Option A: Use conda (recommended for Apple Silicon)
conda install -c apple tensorflow-deps
pip install tensorflow-macos tensorflow-metal

# Option B: Use specific TensorFlow version
pip install tensorflow-macos==2.13.0
```

#### **Intel Mac:**
```bash
# Standard installation
pip install tensorflow==2.13.0

# If that fails, try older version
pip install tensorflow==2.12.0
```

### **Linux Solutions**

#### **Ubuntu/Debian:**
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-dev python3-pip build-essential

# Install TensorFlow
pip install tensorflow==2.13.0

# If CUDA issues:
pip install tensorflow-cpu==2.13.0
```

#### **CentOS/RHEL:**
```bash
# Install dependencies
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel

# Install TensorFlow
pip install tensorflow==2.13.0
```

### **Windows Solutions**

#### **Standard Windows:**
```bash
# Update pip first
python -m pip install --upgrade pip

# Install Visual C++ redistributable if needed
# Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

# Install TensorFlow
pip install tensorflow==2.13.0
```

#### **Windows with GPU:**
```bash
# Install CUDA toolkit first
# Download from: https://developer.nvidia.com/cuda-downloads

# Install TensorFlow with GPU support
pip install tensorflow[and-cuda]==2.13.0
```

### **Common TensorFlow Issues**

#### **1. Version Conflicts**
```bash
# Create fresh environment
python -m venv fresh_env
source fresh_env/bin/activate  # Windows: fresh_env\Scripts\activate
pip install --upgrade pip
pip install tensorflow==2.13.0
```

#### **2. Memory Issues**
```bash
# Increase swap space (Linux/macOS)
sudo swapon --show
# Add more swap if needed

# Limit TensorFlow memory growth
export TF_FORCE_GPU_ALLOW_GROWTH=true
```

#### **3. Python Version Issues**
TensorFlow 2.13+ requires Python 3.8-3.11
```bash
python --version
# If using Python 3.12+, downgrade to 3.11
```

#### **4. Protobuf Issues**
```bash
pip install protobuf==3.20.3
pip install --upgrade tensorflow
```

#### **5. numpy Compatibility**
```bash
pip install "numpy<1.25"
pip install tensorflow
```

## 🔍 **Verify Installation**

### **Test TensorFlow (if installed)**
```bash
python -c "
import tensorflow as tf
print('TensorFlow version:', tf.__version__)
print('GPU available:', tf.config.list_physical_devices('GPU'))
"
```

### **Test PolyAgent Without TensorFlow**
```bash
cd backend
python -c "
# Test that PolyAgent works without TensorFlow
from agents.ai.executor import Executor
from agents.data.polymarket.client import Polymarket
print('✅ PolyAgent works without TensorFlow!')
"
```

## 📊 **Performance Comparison**

### **With TensorFlow:**
- Installation time: 5-15 minutes
- Disk space: ~2GB
- Memory usage: ~500MB base
- Dependencies: 50+ packages

### **Without TensorFlow:**
- Installation time: 1-3 minutes
- Disk space: ~200MB
- Memory usage: ~100MB base
- Dependencies: 20+ packages

**Recommendation: Skip TensorFlow for PolyAgent Web!**

## 🎯 **Final Solution**

### **Quick Fix (2 minutes):**
```bash
cd backend

# Backup original requirements
cp requirements.txt requirements-full.txt

# Use minimal requirements
pip install -r requirements-minimal.txt
python -m spacy download en_core_web_sm

# Test that everything works
cd ..
python quick_test.py
```

### **If Quick Fix Works:**
```bash
# Start your application
cd backend && python app.py
# In new terminal: cd frontend && npm run dev
```

### **If You Still Need Full Requirements:**
```bash
# Try installing with specific TensorFlow version
pip install -r requirements.txt --constraint <(echo "tensorflow==2.13.0")
```

## 💡 **Why TensorFlow Was Included**

The original requirements.txt appears to be from a broader ML project that included:
- `gymnasium` - Reinforcement learning environments
- `tensorflow` - Deep learning framework
- `keras` - High-level neural network API

These are **not used** in the current PolyAgent Web codebase, which focuses on:
- Prediction market trading
- LLM integration (OpenAI)
- Web API development
- Real-time data processing

**Bottom line: You can safely skip TensorFlow for PolyAgent Web!** 🎉