#!/usr/bin/env python3
"""
Quick test script for PolyAgent Web
Run this to verify your refactoring worked correctly
"""

import sys
import os
import traceback

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")
    
    tests = [
        ("AI Executor", "from agents.ai.executor import Executor"),
        ("Polymarket Client", "from agents.data.polymarket.client import Polymarket"),
        ("Data Models", "from agents.models.schemas import SimpleMarket, SimpleEvent"),
        ("Trading Module", "from agents.trading.trader import Trader"),
        ("Polymarket Service", "from services.polymarket_service import PolymarketService"),
        ("AI Service", "from services.ai_service import AIService"),
        ("Trading Service", "from services.trading_service import TradingService"),
        ("News Service", "from services.news_service import NewsService"),
        ("Markets API", "from api.v1.endpoints.markets import router"),
        ("API Models", "from api.v1.models.requests.base import GetMarketsRequest"),
    ]
    
    passed = 0
    failed = 0
    
    for name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {name}: SUCCESS")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: FAILED - {e}")
            failed += 1
    
    print(f"\n📊 Import Results: {passed} passed, {failed} failed")
    return failed == 0

def test_core_functionality():
    """Test core functionality"""
    print("\n🔧 Testing core functionality...")
    
    try:
        # Set dry run mode
        os.environ['DRY_RUN'] = 'true'
        
        # Test AI Executor
        from agents.ai.executor import Executor
        executor = Executor()
        print(f"✅ AI Executor initialized with model: {executor.llm.model_name}")
        print(f"✅ Token limit: {executor.token_limit}")
        
        # Test Polymarket client
        from agents.data.polymarket.client import Polymarket
        polymarket = Polymarket()
        print(f"✅ Polymarket client initialized")
        print(f"✅ Wallet address: {polymarket.wallet_address[:10]}..." if polymarket.wallet_address else "No wallet configured")
        
        # Test Services
        from services.polymarket_service import PolymarketService
        service = PolymarketService()
        print("✅ Polymarket service initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Core functionality test failed: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

def test_api_models():
    """Test API models"""
    print("\n📝 Testing API models...")
    
    try:
        from api.v1.models.requests.base import GetMarketsRequest, MarketCategory
        from api.v1.models.responses.base import MarketResponse
        
        # Test request model
        request = GetMarketsRequest(limit=10, category=MarketCategory.POLITICS)
        print("✅ Request models work")
        
        # Test response model
        response_data = {
            "id": 1,
            "question": "Test market?",
            "end": "2024-12-31",
            "description": "Test description",
            "active": True,
            "funded": True,
            "rewardsMinSize": 1.0,
            "rewardsMaxSpread": 0.1,
            "spread": 0.05,
            "outcomes": '["Yes", "No"]',
            "outcome_prices": '[0.5, 0.5]',
            "clob_token_ids": "123,456",
            "category": "politics"
        }
        response = MarketResponse(**response_data)
        print("✅ Response models work")
        
        return True
        
    except Exception as e:
        print(f"❌ API models test failed: {e}")
        return False

def check_environment():
    """Check environment setup"""
    print("\n🌍 Checking environment...")
    
    required_files = [
        "backend/app.py",
        "backend/agents/ai/executor.py",
        "backend/services/polymarket_service.py",
        "frontend/package.json",
        "frontend/src/app/page.tsx"
    ]
    
    missing = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
        else:
            print(f"✅ {file_path} exists")
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    
    # Check for .env file
    if os.path.exists("backend/.env"):
        print("✅ Environment file exists")
    else:
        print("⚠️  No .env file found - you'll need to create one")
    
    return True

def main():
    """Run all tests"""
    print("🚀 PolyAgent Web Quick Test")
    print("=" * 50)
    
    # Change to project root
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Add backend to Python path
    backend_path = os.path.abspath("backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    all_passed = True
    
    # Run tests
    all_passed &= check_environment()
    all_passed &= test_imports()
    all_passed &= test_core_functionality()
    all_passed &= test_api_models()
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. Create backend/.env file with your API keys")
        print("2. cd backend && python app.py")
        print("3. cd frontend && npm run dev")
        print("4. Open http://localhost:3000")
    else:
        print("❌ SOME TESTS FAILED!")
        print("\nCheck the errors above and fix any import issues.")
        print("Make sure you ran the migration script correctly.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())