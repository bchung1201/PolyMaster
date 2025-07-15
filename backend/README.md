# PolyAgent Web Backend

AI-powered prediction market trading platform backend built with FastAPI.

## Architecture Overview

```
backend/
├── app.py                      # FastAPI main application
├── core/                       # Core utilities
│   ├── config.py              # Configuration management
│   └── websocket_manager.py   # Real-time WebSocket manager
├── services/                  # Business logic layer
│   ├── polymarket_service.py  # Polymarket API wrapper
│   ├── trading_service.py     # Trading logic
│   ├── news_service.py        # News integration
│   └── ai_service.py          # AI analysis
├── api/                       # API layer
│   ├── routes/                # API endpoints
│   │   ├── markets.py         # Market endpoints
│   │   ├── trading.py         # Trading endpoints
│   │   ├── news.py            # News endpoints
│   │   └── ai.py              # AI endpoints
│   └── models/                # Request/response models
│       ├── requests.py        # API request models
│       └── responses.py       # API response models
└── polyagent_legacy/          # Original CLI logic
    ├── application/           # Core trading logic
    ├── connectors/            # External API connectors
    ├── polymarket/            # Polymarket integration
    └── utils/                 # Utility functions
```

## Key Features

- **FastAPI with async support** for high performance
- **WebSocket real-time updates** for live market data
- **Service layer architecture** separating business logic
- **Complete API coverage** for all CLI functionality
- **Type safety** with Pydantic models
- **AI integration** with OpenAI GPT-4o-mini

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the application:
```bash
python app.py
```

## API Documentation

Once running, visit:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- WebSocket: ws://localhost:8000/ws

## Integration with Legacy Code

The new web backend wraps the existing CLI logic without modifying it:

- **Services layer** (`services/`) calls the original classes
- **API routes** (`api/routes/`) expose CLI functionality as REST endpoints
- **WebSocket manager** provides real-time updates
- **Original logic** in `polyagent_legacy/` remains unchanged