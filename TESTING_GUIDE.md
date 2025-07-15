# 🧪 PolyAgent Web Testing Guide

## 📋 **Step-by-Step Testing Instructions**

### **Phase 1: Environment Setup**

#### **1.1 Backend Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

**Expected output:** All packages install without errors

#### **1.2 Frontend Dependencies**
```bash
cd frontend
npm install
```

**Expected output:** Dependencies install successfully

#### **1.3 Environment Variables**
Create `backend/.env` file:
```bash
# Required for basic functionality
OPENAI_API_KEY=your_openai_api_key_here
DRY_RUN=true

# Optional (for full functionality)
POLYGON_WALLET_PRIVATE_KEY=your_wallet_private_key
CLOB_API_KEY=your_clob_api_key
CLOB_SECRET=your_clob_secret
CLOB_PASS_PHRASE=your_clob_passphrase
NEWSAPI_API_KEY=your_news_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### **Phase 2: Import Testing (Critical)**

#### **2.1 Test Core Agent Imports**
```bash
cd backend
python3 -c "
try:
    from agents.ai.executor import Executor
    print('✅ AI Executor import: SUCCESS')
except Exception as e:
    print(f'❌ AI Executor import: FAILED - {e}')

try:
    from agents.data.polymarket.client import Polymarket
    print('✅ Polymarket Client import: SUCCESS')
except Exception as e:
    print(f'❌ Polymarket Client import: FAILED - {e}')

try:
    from agents.models.schemas import SimpleMarket, SimpleEvent
    print('✅ Data Models import: SUCCESS')
except Exception as e:
    print(f'❌ Data Models import: FAILED - {e}')

try:
    from agents.trading.trader import Trader
    print('✅ Trading Module import: SUCCESS')
except Exception as e:
    print(f'❌ Trading Module import: FAILED - {e}')
"
```

**Expected output:** All imports should show SUCCESS

#### **2.2 Test Service Layer Imports**
```bash
cd backend
python3 -c "
try:
    from services.polymarket_service import PolymarketService
    print('✅ Polymarket Service import: SUCCESS')
except Exception as e:
    print(f'❌ Polymarket Service import: FAILED - {e}')

try:
    from services.ai_service import AIService
    print('✅ AI Service import: SUCCESS')
except Exception as e:
    print(f'❌ AI Service import: FAILED - {e}')

try:
    from services.trading_service import TradingService
    print('✅ Trading Service import: SUCCESS')
except Exception as e:
    print(f'❌ Trading Service import: FAILED - {e}')

try:
    from services.news_service import NewsService
    print('✅ News Service import: SUCCESS')
except Exception as e:
    print(f'❌ News Service import: FAILED - {e}')
"
```

**Expected output:** All services should import successfully

#### **2.3 Test API Imports**
```bash
cd backend
python3 -c "
try:
    from api.v1.endpoints.markets import router
    print('✅ Markets API import: SUCCESS')
except Exception as e:
    print(f'❌ Markets API import: FAILED - {e}')

try:
    from api.v1.models.requests.base import GetMarketsRequest
    print('✅ API Models import: SUCCESS')
except Exception as e:
    print(f'❌ API Models import: FAILED - {e}')
"
```

### **Phase 3: Service Functionality Testing**

#### **3.1 Test Core AI Functionality**
```bash
cd backend
python3 -c "
import os
os.environ['DRY_RUN'] = 'true'

try:
    from agents.ai.executor import Executor
    executor = Executor()
    print('✅ AI Executor initialization: SUCCESS')
    print(f'✅ Model: {executor.llm.model_name}')
    print(f'✅ Token limit: {executor.token_limit}')
except Exception as e:
    print(f'❌ AI Executor test: FAILED - {e}')
"
```

**Expected output:** Should show GPT-4o-mini model with 128000 token limit

#### **3.2 Test CLI Functionality**
```bash
cd backend/scripts/python
python3 cli.py --help
```

**Expected output:** CLI help menu should display without errors

### **Phase 4: Backend API Testing**

#### **4.1 Start Backend Server**
```bash
cd backend
python3 app.py
```

**Expected output:**
```
🚀 Starting PolyAgent Web...
✅ PolyAgent Web started successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

#### **4.2 Test API Health Check**
In a new terminal:
```bash
curl http://localhost:8000/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "polymarket": true,
    "trading": true,
    "news": true,
    "ai": true
  }
}
```

#### **4.3 Test API Documentation**
Open browser: http://localhost:8000/docs

**Expected:** Interactive API documentation should load

#### **4.4 Test Markets Endpoint**
```bash
curl http://localhost:8000/api/markets?limit=2
```

**Expected output:** JSON response with market data (may take a few seconds)

#### **4.5 Test WebSocket Connection**
```bash
# Install wscat if needed: npm install -g wscat
wscat -c ws://localhost:8000/ws
```

**Expected:** WebSocket connection established, can send/receive messages

### **Phase 5: Frontend Testing**

#### **5.1 Build Test (TypeScript Validation)**
```bash
cd frontend
npm run build
```

**Expected output:** Build completes successfully without TypeScript errors

#### **5.2 Start Frontend Development Server**
```bash
cd frontend
npm run dev
```

**Expected output:**
```
Ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

#### **5.3 Test Frontend in Browser**
Open browser: http://localhost:3000

**Expected:**
- ✅ Dashboard loads without errors
- ✅ WebSocket connection indicator shows "Connected"
- ✅ Market cards display (even if with placeholder data)
- ✅ News section loads
- ✅ No console errors in browser dev tools

### **Phase 6: Integration Testing**

#### **6.1 Full Stack API Test**
With both backend and frontend running:

```bash
# Test markets API from frontend
curl http://localhost:3000/api/markets
```

**Expected:** Should proxy to backend and return market data

#### **6.2 WebSocket Real-time Test**
1. Open browser dev tools (F12)
2. Go to Network tab → WS (WebSocket)
3. Refresh the page
4. Should see WebSocket connection established

#### **6.3 End-to-End Manual Test**
1. ✅ Dashboard loads
2. ✅ Market data appears
3. ✅ News articles load
4. ✅ AI insights section shows
5. ✅ No error messages in UI
6. ✅ Real-time updates work (data refreshes)

### **Phase 7: Error Scenarios Testing**

#### **7.1 Test with Missing API Keys**
```bash
# Temporarily rename .env file
cd backend
mv .env .env.backup

# Start backend
python3 app.py
```

**Expected:** Backend should start but show warnings about missing API keys

#### **7.2 Test API Error Handling**
```bash
curl http://localhost:8000/api/markets/invalid_id
```

**Expected:** Proper error response (404 or 500 with error message)

## 🐛 **Common Issues & Solutions**

### **Import Errors**
```bash
# If you see: ModuleNotFoundError: No module named 'agents'
cd backend
export PYTHONPATH="$PWD:$PYTHONPATH"
python3 app.py
```

### **Missing Dependencies**
```bash
# If specific packages are missing:
pip install fastapi uvicorn openai langchain
```

### **WebSocket Connection Issues**
```bash
# Check if port 8000 is available:
lsof -i :8000

# Kill if needed:
kill -9 $(lsof -t -i:8000)
```

### **Frontend Build Issues**
```bash
# Clear Next.js cache:
cd frontend
rm -rf .next
npm run build
```

### **API Connection Issues**
```bash
# Check if backend is running:
curl http://localhost:8000/health

# Check CORS settings in app.py
```

## ✅ **Success Criteria**

### **Minimum Working State:**
- [ ] All imports work without errors
- [ ] Backend starts and health check passes
- [ ] Frontend builds and starts successfully
- [ ] Basic API endpoints respond
- [ ] Dashboard loads in browser

### **Full Functionality:**
- [ ] WebSocket real-time updates work
- [ ] Market data loads correctly
- [ ] News integration works
- [ ] AI analysis responds
- [ ] No console errors

### **Production Ready:**
- [ ] All environment variables configured
- [ ] Trading functionality works (dry run)
- [ ] Error handling works properly
- [ ] Performance is acceptable

## 🎯 **Quick Test Script**

Create this test script to run all tests at once:

```bash
#!/bin/bash
# save as test_polyagent.sh

echo "🧪 Testing PolyAgent Web..."

echo "1. Testing Python imports..."
cd backend
python3 -c "from agents.ai.executor import Executor; from services.polymarket_service import PolymarketService; print('✅ All imports successful')"

echo "2. Testing backend startup..."
timeout 10s python3 app.py &
sleep 5
curl -s http://localhost:8000/health && echo "✅ Backend health check passed" || echo "❌ Backend health check failed"

echo "3. Testing frontend build..."
cd ../frontend
npm run build > /dev/null 2>&1 && echo "✅ Frontend build successful" || echo "❌ Frontend build failed"

echo "🎉 Basic tests complete!"
```

Run with: `chmod +x test_polyagent.sh && ./test_polyagent.sh`