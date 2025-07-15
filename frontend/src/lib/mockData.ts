import type { Market, NewsArticle } from './api'

// Generate realistic mock markets with current dates
export const generateMockMarkets = (): Market[] => {
  const now = new Date()
  const futureDate = (days: number) => {
    const date = new Date(now)
    date.setDate(date.getDate() + days)
    return date.toISOString()
  }

  return [
    {
      id: 1,
      question: "Will Bitcoin reach $100,000 by the end of 2024?",
      end: futureDate(90),
      description: "Prediction market on whether Bitcoin will reach $100,000 USD by December 31, 2024",
      active: true,
      funded: true,
      rewardsMinSize: 100,
      rewardsMaxSpread: 0.1,
      spread: 0.03,
      outcomes: "Yes,No",
      outcome_prices: "0.72,0.28",
      clob_token_ids: "crypto_btc_100k",
      category: "crypto"
    },
    {
      id: 2,
      question: "Will Donald Trump win the 2024 U.S. Presidential Election?",
      end: futureDate(180),
      description: "Will Donald Trump be elected as the 46th President of the United States in the 2024 election?",
      active: true,
      funded: true,
      rewardsMinSize: 50,
      rewardsMaxSpread: 0.05,
      spread: 0.02,
      outcomes: "Yes,No",
      outcome_prices: "0.51,0.49",
      clob_token_ids: "politics_trump_2024",
      category: "politics"
    },
    {
      id: 3,
      question: "Will Tesla stock price exceed $300 in Q1 2024?",
      end: futureDate(45),
      description: "Will Tesla (TSLA) stock close above $300 USD at any point during Q1 2024?",
      active: true,
      funded: true,
      rewardsMinSize: 25,
      rewardsMaxSpread: 0.08,
      spread: 0.04,
      outcomes: "Yes,No",
      outcome_prices: "0.38,0.62",
      clob_token_ids: "stocks_tsla_300",
      category: "tech"
    },
    {
      id: 4,
      question: "Will the Chiefs win Super Bowl 2025?",
      end: futureDate(120),
      description: "Will the Kansas City Chiefs win Super Bowl LIX in 2025?",
      active: true,
      funded: true,
      rewardsMinSize: 20,
      rewardsMaxSpread: 0.12,
      spread: 0.06,
      outcomes: "Yes,No",
      outcome_prices: "0.22,0.78",
      clob_token_ids: "sports_chiefs_sb25",
      category: "sports"
    },
    {
      id: 5,
      question: "Will a major AI breakthrough be announced by Google in 2024?",
      end: futureDate(200),
      description: "Will Google announce a significant AI breakthrough or new AI model in 2024?",
      active: true,
      funded: true,
      rewardsMinSize: 30,
      rewardsMaxSpread: 0.15,
      spread: 0.07,
      outcomes: "Yes,No",
      outcome_prices: "0.65,0.35",
      clob_token_ids: "tech_google_ai_2024",
      category: "tech"
    },
    {
      id: 6,
      question: "Will Ethereum reach $5,000 by June 2024?",
      end: futureDate(75),
      description: "Will Ethereum (ETH) reach $5,000 USD by June 30, 2024?",
      active: true,
      funded: true,
      rewardsMinSize: 40,
      rewardsMaxSpread: 0.09,
      spread: 0.05,
      outcomes: "Yes,No",
      outcome_prices: "0.42,0.58",
      clob_token_ids: "crypto_eth_5k",
      category: "crypto"
    },
    {
      id: 7,
      question: "Will Apple release a VR headset in 2024?",
      end: futureDate(150),
      description: "Will Apple announce and release a VR/AR headset product in 2024?",
      active: true,
      funded: true,
      rewardsMinSize: 35,
      rewardsMaxSpread: 0.11,
      spread: 0.08,
      outcomes: "Yes,No",
      outcome_prices: "0.78,0.22",
      clob_token_ids: "tech_apple_vr_2024",
      category: "tech"
    },
    {
      id: 8,
      question: "Will there be a recession in the US in 2024?",
      end: futureDate(250),
      description: "Will the United States enter an official recession in 2024?",
      active: true,
      funded: true,
      rewardsMinSize: 50,
      rewardsMaxSpread: 0.06,
      spread: 0.03,
      outcomes: "Yes,No",
      outcome_prices: "0.31,0.69",
      clob_token_ids: "econ_us_recession_2024",
      category: "politics"
    },
    {
      id: 9,
      question: "Will Netflix stock outperform the S&P 500 in 2024?",
      end: futureDate(280),
      description: "Will Netflix (NFLX) stock outperform the S&P 500 index in 2024?",
      active: true,
      funded: true,
      rewardsMinSize: 25,
      rewardsMaxSpread: 0.10,
      spread: 0.05,
      outcomes: "Yes,No",
      outcome_prices: "0.54,0.46",
      clob_token_ids: "entertainment_nflx_2024",
      category: "entertainment"
    },
    {
      id: 10,
      question: "Will SpaceX successfully land humans on Mars by 2026?",
      end: futureDate(400),
      description: "Will SpaceX successfully complete a crewed mission to Mars by December 31, 2026?",
      active: true,
      funded: true,
      rewardsMinSize: 100,
      rewardsMaxSpread: 0.20,
      spread: 0.12,
      outcomes: "Yes,No",
      outcome_prices: "0.15,0.85",
      clob_token_ids: "tech_spacex_mars_2026",
      category: "tech"
    },
    {
      id: 11,
      question: "Will FIFA World Cup 2026 be the most watched ever?",
      end: futureDate(500),
      description: "Will the 2026 FIFA World Cup break all-time viewership records?",
      active: true,
      funded: true,
      rewardsMinSize: 20,
      rewardsMaxSpread: 0.08,
      spread: 0.04,
      outcomes: "Yes,No",
      outcome_prices: "0.68,0.32",
      clob_token_ids: "sports_fifa_2026_viewers",
      category: "sports"
    },
    {
      id: 12,
      question: "Will a new record for global temperature be set in 2024?",
      end: futureDate(300),
      description: "Will 2024 set a new record for highest global average temperature?",
      active: true,
      funded: true,
      rewardsMinSize: 30,
      rewardsMaxSpread: 0.07,
      spread: 0.03,
      outcomes: "Yes,No",
      outcome_prices: "0.73,0.27",
      clob_token_ids: "climate_temp_record_2024",
      category: "other"
    },
    {
      id: 13,
      question: "Will China's GDP growth exceed 5% in 2024?",
      end: futureDate(320),
      description: "Will China's GDP growth rate exceed 5% for the full year 2024?",
      active: true,
      funded: true,
      rewardsMinSize: 40,
      rewardsMaxSpread: 0.06,
      spread: 0.02,
      outcomes: "Yes,No",
      outcome_prices: "0.61,0.39",
      clob_token_ids: "econ_china_gdp_2024",
      category: "politics"
    },
    {
      id: 14,
      question: "Will a major streaming service acquire a traditional TV network in 2024?",
      end: futureDate(180),
      description: "Will a major streaming platform acquire a traditional television network in 2024?",
      active: true,
      funded: true,
      rewardsMinSize: 35,
      rewardsMaxSpread: 0.09,
      spread: 0.05,
      outcomes: "Yes,No",
      outcome_prices: "0.44,0.56",
      clob_token_ids: "entertainment_streaming_acquisition",
      category: "entertainment"
    },
    {
      id: 15,
      question: "Will autonomous vehicles be approved for widespread use in California by 2025?",
      end: futureDate(365),
      description: "Will fully autonomous vehicles receive approval for widespread public use in California by end of 2025?",
      active: true,
      funded: true,
      rewardsMinSize: 50,
      rewardsMaxSpread: 0.13,
      spread: 0.08,
      outcomes: "Yes,No",
      outcome_prices: "0.37,0.63",
      clob_token_ids: "tech_autonomous_cars_ca",
      category: "tech"
    },
    {
      id: 16,
      question: "Will Dogecoin reach $1 by end of 2024?",
      end: futureDate(280),
      description: "Will Dogecoin (DOGE) reach $1.00 USD by December 31, 2024?",
      active: true,
      funded: true,
      rewardsMinSize: 15,
      rewardsMaxSpread: 0.15,
      spread: 0.10,
      outcomes: "Yes,No",
      outcome_prices: "0.18,0.82",
      clob_token_ids: "crypto_doge_1dollar",
      category: "crypto"
    },
    {
      id: 17,
      question: "Will the Lakers make the NBA playoffs in 2024?",
      end: futureDate(60),
      description: "Will the Los Angeles Lakers qualify for the 2024 NBA playoffs?",
      active: true,
      funded: true,
      rewardsMinSize: 25,
      rewardsMaxSpread: 0.08,
      spread: 0.04,
      outcomes: "Yes,No",
      outcome_prices: "0.69,0.31",
      clob_token_ids: "sports_lakers_playoffs_2024",
      category: "sports"
    },
    {
      id: 18,
      question: "Will a major tech company announce a quantum computing breakthrough in 2024?",
      end: futureDate(240),
      description: "Will IBM, Google, Microsoft, or Amazon announce a significant quantum computing breakthrough in 2024?",
      active: true,
      funded: true,
      rewardsMinSize: 45,
      rewardsMaxSpread: 0.12,
      spread: 0.07,
      outcomes: "Yes,No",
      outcome_prices: "0.58,0.42",
      clob_token_ids: "tech_quantum_breakthrough",
      category: "tech"
    },
    {
      id: 19,
      question: "Will gas prices average above $4/gallon in the US in 2024?",
      end: futureDate(300),
      description: "Will the average price of gasoline in the United States exceed $4.00 per gallon for the year 2024?",
      active: true,
      funded: true,
      rewardsMinSize: 20,
      rewardsMaxSpread: 0.09,
      spread: 0.05,
      outcomes: "Yes,No",
      outcome_prices: "0.41,0.59",
      clob_token_ids: "econ_gas_prices_2024",
      category: "other"
    },
    {
      id: 20,
      question: "Will Taylor Swift announce a new album in 2024?",
      end: futureDate(200),
      description: "Will Taylor Swift officially announce a new studio album for release in 2024?",
      active: true,
      funded: true,
      rewardsMinSize: 15,
      rewardsMaxSpread: 0.10,
      spread: 0.06,
      outcomes: "Yes,No",
      outcome_prices: "0.76,0.24",
      clob_token_ids: "entertainment_taylor_swift_album",
      category: "entertainment"
    }
  ]
}

export const generateMockNews = (): NewsArticle[] => {
  const now = new Date()
  const hoursAgo = (hours: number) => {
    const date = new Date(now)
    date.setHours(date.getHours() - hours)
    return date.toISOString()
  }

  return [
    {
      title: "Bitcoin Surges Past $70,000 as Institutional Interest Grows",
      description: "Cryptocurrency markets rally as major institutions announce increased Bitcoin allocation strategies",
      url: "https://example.com/bitcoin-surge",
      urlToImage: "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=400",
      publishedAt: hoursAgo(2),
      content: "Bitcoin has reached new highs as institutional investors continue to show strong interest...",
      source: { id: "crypto-news", name: "Crypto News Daily" },
      author: "Sarah Chen",
      category: "crypto",
      relevance_score: 0.95
    },
    {
      title: "2024 Election Polls Show Tight Race in Key Battleground States",
      description: "Latest polling data reveals increasingly competitive races in swing states ahead of the election",
      url: "https://example.com/election-polls",
      urlToImage: "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=400",
      publishedAt: hoursAgo(4),
      content: "Recent polling suggests a highly competitive election landscape...",
      source: { id: "political-wire", name: "Political Wire" },
      author: "Michael Rodriguez",
      category: "politics",
      relevance_score: 0.92
    },
    {
      title: "Tesla Announces Major Battery Technology Breakthrough",
      description: "New battery technology promises 50% longer range and faster charging times",
      url: "https://example.com/tesla-battery",
      urlToImage: "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=400",
      publishedAt: hoursAgo(6),
      content: "Tesla has revealed a significant advancement in battery technology...",
      source: { id: "tech-crunch", name: "TechCrunch" },
      author: "Emma Thompson",
      category: "tech",
      relevance_score: 0.89
    },
    {
      title: "NFL Playoff Picture Becomes Clearer After Weekend Games",
      description: "Key victories and defeats reshape the playoff landscape with weeks remaining",
      url: "https://example.com/nfl-playoffs",
      urlToImage: "https://images.unsplash.com/photo-1566577739112-5180d4bf9390?w=400",
      publishedAt: hoursAgo(8),
      content: "This weekend's NFL games have significantly impacted playoff scenarios...",
      source: { id: "espn", name: "ESPN" },
      author: "David Wilson",
      category: "sports",
      relevance_score: 0.85
    },
    {
      title: "AI Chip Demand Drives Record Semiconductor Sales",
      description: "Growing AI applications fuel unprecedented demand for specialized processing chips",
      url: "https://example.com/ai-chip-demand",
      urlToImage: "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400",
      publishedAt: hoursAgo(10),
      content: "The semiconductor industry is experiencing record sales driven by AI...",
      source: { id: "semiconductor-today", name: "Semiconductor Today" },
      author: "Lisa Park",
      category: "tech",
      relevance_score: 0.88
    },
    {
      title: "Streaming Wars Heat Up with New Platform Launches",
      description: "Multiple entertainment companies announce new streaming services and exclusive content deals",
      url: "https://example.com/streaming-wars",
      urlToImage: "https://images.unsplash.com/photo-1522869635100-9f4c5e86aa37?w=400",
      publishedAt: hoursAgo(12),
      content: "The entertainment industry sees intensifying competition in streaming...",
      source: { id: "variety", name: "Variety" },
      author: "James Anderson",
      category: "entertainment",
      relevance_score: 0.82
    },
    {
      title: "Federal Reserve Signals Potential Interest Rate Changes",
      description: "Central bank officials hint at upcoming monetary policy adjustments based on economic indicators",
      url: "https://example.com/fed-rates",
      urlToImage: "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400",
      publishedAt: hoursAgo(14),
      content: "Federal Reserve officials have indicated potential changes to interest rates...",
      source: { id: "financial-times", name: "Financial Times" },
      author: "Robert Kim",
      category: "politics",
      relevance_score: 0.90
    },
    {
      title: "Space Tourism Industry Reaches New Milestone",
      description: "Private space companies successfully complete record number of civilian missions",
      url: "https://example.com/space-tourism",
      urlToImage: "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=400",
      publishedAt: hoursAgo(16),
      content: "The space tourism industry has achieved a significant milestone...",
      source: { id: "space-news", name: "Space News" },
      author: "Amanda Foster",
      category: "tech",
      relevance_score: 0.78
    }
  ]
}

export const mockMarkets = generateMockMarkets()
export const mockNews = generateMockNews()