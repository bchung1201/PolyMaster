# PolyAgent Web Frontend

Modern React frontend for the PolyAgent prediction market platform.

## Technology Stack

- **Next.js 14** with App Router
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **SWR** for data fetching
- **WebSocket** for real-time updates

## Features

- **Real-time market data** with WebSocket connections
- **Interactive dashboard** with market overview
- **AI-powered insights** and trading recommendations
- **News integration** with market relevance
- **Responsive design** for all devices
- **Dark/light theme** support

## Project Structure

```
frontend/
├── app/                       # Next.js 14 app directory
│   ├── layout.tsx            # Root layout
│   ├── page.tsx              # Dashboard page
│   ├── providers.tsx         # React context providers
│   └── globals.css           # Global styles
├── components/               # React components
│   └── ui/                   # Reusable UI components
│       ├── button.tsx        # Button component
│       ├── card.tsx          # Card component
│       └── badge.tsx         # Badge component
├── lib/                      # Utility functions
│   ├── api.ts               # API client
│   └── utils.ts             # Helper functions
├── package.json             # Dependencies
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── postcss.config.js        # PostCSS configuration
```

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set environment variables:
```bash
# Create .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

3. Run development server:
```bash
npm run dev
```

## API Integration

The frontend communicates with the backend through:

- **REST API calls** for data fetching and mutations
- **WebSocket connections** for real-time updates
- **SWR hooks** for data caching and revalidation
- **Error handling** with toast notifications

## Real-time Features

- **Market price updates** via WebSocket
- **News feed updates** with live articles
- **AI analysis streaming** for real-time insights
- **Trading notifications** for order status