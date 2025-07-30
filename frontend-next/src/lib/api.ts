/**
 * API client for interacting with the Railway backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://looklike-nearby-production.up.railway.app';

interface ApiError {
  message: string;
  code?: string;
  details?: any;
}

interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}

/**
 * Generic API client with error handling and authentication.
 */
class ApiClient {
  private token: string | null = null;

  constructor() {
    // Check for token in localStorage on client side
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...options.headers,
      };

      if (this.token) {
        headers['Authorization'] = `Bearer ${this.token}`;
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const error = await response.json();
        return { error };
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return {
        error: {
          message: 'Network error occurred',
          details: error,
        },
      };
    }
  }

  // Authentication
  async login(password: string): Promise<ApiResponse<{ token: string }>> {
    const response = await this.request<{ token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ password }),
    });

    if (response.data?.token) {
      this.token = response.data.token;
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', response.data.token);
      }
    }

    return response;
  }

  async logout(): Promise<void> {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Reference Clients
  async getReferenceClients() {
    return this.request<any[]>('/reference-clients');
  }

  async createReferenceClient(data: any) {
    return this.request('/reference-clients', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Prospects & Search
  async searchProspects(params: any) {
    const queryString = new URLSearchParams(params).toString();
    return this.request<any[]>(`/search?${queryString}`);
  }

  async getProspect(id: number) {
    return this.request<any>(`/prospects/${id}`);
  }

  // Campaigns
  async getCampaigns() {
    return this.request<any[]>('/campaigns');
  }

  async createCampaign(data: any) {
    return this.request('/campaigns', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async addProspectToCampaign(campaignId: number, prospectId: number, data: any) {
    return this.request(`/campaigns/${campaignId}/prospects/${prospectId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

// Export singleton instance
export const api = new ApiClient();