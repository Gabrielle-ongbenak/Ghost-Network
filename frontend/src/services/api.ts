import { dashboardStats, countryBreakdown, mockListings, networkNodes, networkEdges, platformBreakdown } from "../data/mockData"

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

async function fetchOrFallback<T>(endpoint: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      signal: AbortSignal.timeout(3000),
    })
    if (!response.ok) throw new Error(`API error: ${response.status}`)
    return await response.json()
  } catch (error) {
    console.warn(`Could not reach ${endpoint}, using mock data.`, error)
    return fallback
  }
}

export const api = {
  getDashboardStats: () => fetchOrFallback("/api/dashboard/stats", dashboardStats),
  getCountryBreakdown: () => fetchOrFallback("/api/dashboard/countries", countryBreakdown),
  getPlatformBreakdown: () => fetchOrFallback("/api/dashboard/platforms", platformBreakdown),
  getListings: () => fetchOrFallback("/api/listings", mockListings),
  getNetworkNodes: () => fetchOrFallback("/api/network/nodes", networkNodes),
  getNetworkEdges: () => fetchOrFallback("/api/network/edges", networkEdges),
}