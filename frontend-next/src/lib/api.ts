/**
 * API client for interacting with the Railway backend.
 */

import { Campaign, Prospect, ReferenceClient, SearchParams } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://looklike-nearby-production.up.railway.app';

interface ApiError {
  message: string;
  code?: string;
  details?: unknown;
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
      const headers = new Headers({
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string>),
      });

      if (this.token) {
        headers.set('Authorization', `Bearer ${this.token}`);
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
        credentials: 'include',
        mode: 'cors',
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
  async login(password: string): Promise<ApiResponse<{ access_token: string; token_type: string; message: string }>> {
    const response = await this.request<{ access_token: string; token_type: string; message: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ password }),
    });

    if (response.data?.access_token) {
      this.token = response.data.access_token;
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', response.data.access_token);
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
    return this.request<ReferenceClient[]>('/reference-clients');
  }

  async createReferenceClient(data: Omit<ReferenceClient, 'id' | 'created_at' | 'updated_at'>) {
    return this.request<ReferenceClient>('/reference-clients', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Prospects & Search
  async searchProspects(params: SearchParams) {
    const queryParams = new URLSearchParams();
    
    if (params.reference_client_id) {
      queryParams.append('reference_client_id', params.reference_client_id.toString());
    }
    if (params.radius_meters) {
      queryParams.append('radius_meters', params.radius_meters.toString());
    }
    if (params.custom_address) {
      queryParams.append('custom_address', params.custom_address);
    }
    if (params.filters) {
      if (params.filters.business_type) {
        queryParams.append('business_type', params.filters.business_type);
      }
      if (params.filters.min_rating) {
        queryParams.append('min_rating', params.filters.min_rating.toString());
      }
      if (params.filters.max_price_level) {
        queryParams.append('max_price_level', params.filters.max_price_level.toString());
      }
      if (params.filters.open_now) {
        queryParams.append('open_now', params.filters.open_now.toString());
      }
    }
    
    return this.request<Prospect[]>(`/search?${queryParams.toString()}`);
  }

  async getProspect(id: number) {
    return this.request<Prospect>(`/prospects/${id}`);
  }

  // Campaigns
  async getCampaigns() {
    return this.request<Campaign[]>('/campaigns');
  }

  async createCampaign(data: Omit<Campaign, 'id' | 'created_at' | 'updated_at'>) {
    return this.request<Campaign>('/campaigns', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async addProspectToCampaign(campaignId: number, prospectId: number, data: { status: string; notes?: string }) {
    return this.request(`/campaigns/${campaignId}/prospects/${prospectId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

// Export singleton instance
export const api = new ApiClient();