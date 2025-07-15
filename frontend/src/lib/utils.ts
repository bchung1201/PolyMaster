import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { format, formatDistance, parseISO, isValid } from 'date-fns'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPrice(price: number | string): string {
  const numPrice = typeof price === 'string' ? parseFloat(price) : price
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  }).format(numPrice)
}

export function formatPercentage(value: number | string): string {
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 2,
  }).format(numValue)
}

export function formatNumber(value: number | string): string {
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(numValue)
}

export function formatCompactNumber(value: number | string): string {
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    compactDisplay: 'short',
  }).format(numValue)
}

export function formatDate(date: string | Date): string {
  if (!date) return 'Unknown'
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    
    if (!isValid(dateObj)) {
      return 'Invalid date'
    }
    
    return format(dateObj, 'MMM dd, yyyy')
  } catch (error) {
    console.warn('Error formatting date:', error, 'Date value:', date)
    return 'Invalid date'
  }
}

export function formatDateTime(date: string | Date): string {
  if (!date) return 'Unknown'
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    
    if (!isValid(dateObj)) {
      return 'Invalid date'
    }
    
    return format(dateObj, 'MMM dd, yyyy HH:mm')
  } catch (error) {
    console.warn('Error formatting date:', error, 'Date value:', date)
    return 'Invalid date'
  }
}

export function formatRelativeTime(date: string | Date): string {
  if (!date) return 'No end date'
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    
    if (!isValid(dateObj)) {
      return 'No end date'
    }
    
    return formatDistance(dateObj, new Date(), { addSuffix: true })
  } catch (error) {
    console.warn('Error formatting date:', error, 'Date value:', date)
    return 'No end date'
  }
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

export function getMarketStatusColor(active: boolean, funded: boolean): string {
  if (active && funded) return 'text-green-600'
  if (active && !funded) return 'text-yellow-600'
  return 'text-gray-600'
}

export function getMarketStatusText(active: boolean, funded: boolean): string {
  if (active && funded) return 'Active'
  if (active && !funded) return 'Pending'
  return 'Inactive'
}

export function getCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    politics: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    sports: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    crypto: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    entertainment: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    tech: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    economy: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    climate: 'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200',
    health: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
    other: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
  }
  return colors[category] || colors.other
}

export function getCategoryIcon(category: string): string {
  const icons: Record<string, string> = {
    politics: '🏛️',
    sports: '⚽',
    crypto: '₿',
    entertainment: '🎬',
    tech: '💻',
    economy: '💰',
    climate: '🌍',
    health: '🏥',
    other: '📊',
  }
  return icons[category] || icons.other
}

export function parsePriceArray(priceString: string): number[] {
  try {
    const parsed = JSON.parse(priceString)
    return Array.isArray(parsed) ? parsed.map(p => parseFloat(p)) : []
  } catch {
    return []
  }
}

export function parseOutcomeArray(outcomeString: string): string[] {
  try {
    const parsed = JSON.parse(outcomeString)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function calculateProbability(price: number): number {
  return price * 100
}

export function calculateImpliedOdds(price: number): string {
  const probability = price * 100
  const odds = probability / (100 - probability)
  return odds.toFixed(2)
}

export function debounce<T extends (...args: any[]) => void>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}

export function throttle<T extends (...args: any[]) => void>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0
  return (...args: Parameters<T>) => {
    const now = Date.now()
    if (now - lastCall >= delay) {
      lastCall = now
      func(...args)
    }
  }
}

export function generateId(): string {
  return Math.random().toString(36).substr(2, 9)
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text)
}

export function downloadAsJson(data: any, filename: string): void {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: 'application/json',
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function isValidUrl(string: string): boolean {
  try {
    new URL(string)
    return true
  } catch {
    return false
  }
}

export function extractDomain(url: string): string {
  try {
    return new URL(url).hostname
  } catch {
    return ''
  }
}

export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-green-600'
  if (confidence >= 0.6) return 'text-yellow-600'
  return 'text-red-600'
}

export function getConfidenceText(confidence: number): string {
  if (confidence >= 0.8) return 'High'
  if (confidence >= 0.6) return 'Medium'
  return 'Low'
}

export function formatVolume(volume: number): string {
  if (volume >= 1000000) {
    return `$${(volume / 1000000).toFixed(1)}M`
  } else if (volume >= 1000) {
    return `$${(volume / 1000).toFixed(1)}K`
  }
  return formatPrice(volume)
}

export function calculateSpreadPercentage(spread: number): number {
  return spread * 100
}

export function getPriceChangeColor(change: number): string {
  if (change > 0) return 'text-green-600'
  if (change < 0) return 'text-red-600'
  return 'text-gray-600'
}

export function formatPriceChange(change: number): string {
  const prefix = change > 0 ? '+' : ''
  return `${prefix}${change.toFixed(2)}%`
}