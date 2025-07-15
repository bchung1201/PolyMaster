'use client'

import { createContext, useContext, useEffect, useState } from 'react'

// WebSocket Context
interface WebSocketContextType {
  ws: WebSocket | null
  connected: boolean
  subscribe: (type: string) => void
  unsubscribe: (type: string) => void
}

const WebSocketContext = createContext<WebSocketContextType | null>(null)

export function useWebSocket() {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}

function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'
    
    try {
      const socket = new WebSocket(wsUrl)
      
      socket.onopen = () => {
        console.log('WebSocket connected')
        setConnected(true)
      }
      
      socket.onclose = () => {
        console.log('WebSocket disconnected')
        setConnected(false)
      }
      
      socket.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnected(false)
      }
      
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('WebSocket message:', data)
          
          // Handle different message types
          if (data.type === 'market_update') {
            // Dispatch market update event
            window.dispatchEvent(new CustomEvent('market_update', { detail: data.data }))
          } else if (data.type === 'news_update') {
            // Dispatch news update event
            window.dispatchEvent(new CustomEvent('news_update', { detail: data.data }))
          } else if (data.type === 'ai_analysis_complete') {
            // Dispatch AI analysis complete event
            window.dispatchEvent(new CustomEvent('ai_analysis_complete', { detail: data }))
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      setWs(socket)
      
      return () => {
        socket.close()
      }
    } catch (error) {
      console.error('Error creating WebSocket:', error)
    }
  }, [])

  const subscribe = (type: string) => {
    if (ws && connected) {
      ws.send(JSON.stringify({ type: `subscribe_${type}` }))
    }
  }

  const unsubscribe = (type: string) => {
    if (ws && connected) {
      ws.send(JSON.stringify({ type: `unsubscribe_${type}` }))
    }
  }

  return (
    <WebSocketContext.Provider value={{ ws, connected, subscribe, unsubscribe }}>
      {children}
    </WebSocketContext.Provider>
  )
}

// Theme Context
interface ThemeContextType {
  theme: 'light' | 'dark'
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | null>(null)

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')

  useEffect(() => {
    const saved = localStorage.getItem('theme') as 'light' | 'dark'
    if (saved) {
      setTheme(saved)
    } else {
      // Default to dark mode, but respect system preference if it's explicitly light
      const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches
      setTheme(prefersLight ? 'light' : 'dark')
    }
  }, [])

  useEffect(() => {
    localStorage.setItem('theme', theme)
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

// Combined Providers
export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <WebSocketProvider>
        {children}
      </WebSocketProvider>
    </ThemeProvider>
  )
}