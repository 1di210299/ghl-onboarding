/**
 * API client for backend endpoints
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ApiResponse<T> {
  data?: T
  error?: string
}

export interface ClientListResponse {
  clients: any[]
  total: number
  page: number
  page_size: number
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      })

      if (!response.ok) {
        const error = await response.json()
        return { error: error.detail || 'An error occurred' }
      }

      const data = await response.json()
      return { data }
    } catch (error) {
      console.error('API request failed:', error)
      return { error: 'Network error' }
    }
  }

  // Client endpoints
  async getClients(params: {
    tenant_id: string
    page?: number
    page_size?: number
    search?: string
    status?: string
    terminology?: string
  }): Promise<ApiResponse<ClientListResponse>> {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value))
      }
    })

    return this.request<ClientListResponse>(
      `/api/clients?${searchParams.toString()}`
    )
  }

  async getClient(clientId: string): Promise<ApiResponse<any>> {
    return this.request(`/api/clients/${clientId}`)
  }

  async updateClient(
    clientId: string,
    data: any
  ): Promise<ApiResponse<any>> {
    return this.request(`/api/clients/${clientId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteClient(clientId: string): Promise<ApiResponse<void>> {
    return this.request(`/api/clients/${clientId}`, {
      method: 'DELETE',
    })
  }

  // Onboarding endpoints
  async startOnboarding(data: {
    tenant_id: string
    practice_name?: string
  }): Promise<ApiResponse<any>> {
    return this.request('/api/onboarding/start', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async sendMessage(data: {
    session_id: string
    message: string
  }): Promise<ApiResponse<any>> {
    return this.request('/api/onboarding/message', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getOnboardingStatus(sessionId: string): Promise<ApiResponse<any>> {
    return this.request(`/api/onboarding/status/${sessionId}`)
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<any>> {
    return this.request('/health')
  }
}

export const apiClient = new ApiClient(API_URL)
