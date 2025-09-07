import { API_BASE_URL, API_ENDPOINTS } from '$lib/config';

// Use centralized configuration

export interface Channel {
  id: string;
  name: string;
  slug: string;
  markup_percent: string;
  metadata?: Array<{ key: string; value: string }>;
}

export interface PriceCalculation {
  product_id: string;
  channel_id: string;
  base_price: string;
  markup_percent: string;
  final_price: string;
  currency?: string;
}

export interface MarkupUpdate {
  channel_id: string;
  markup_percent: number;
}

export interface PriceCalculationRequest {
  product_id: string;
  channel_id: string;
  base_price: number;
}

class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public response?: Response
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Create a fetch function that doesn't get intercepted by SvelteKit
const directFetch = typeof window !== 'undefined' ? window.fetch.bind(window) : fetch;

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text().catch(() => 'Unknown error');
    throw new ApiError(
      `HTTP error! status: ${response.status}, message: ${errorText}`,
      response.status,
      response
    );
  }

  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await response.json();
  }
  
  return (await response.text()) as unknown as T;
}

export const api = {
  async getChannels(subdomain?: string): Promise<Channel[]> {
    const url = subdomain 
      ? `${API_ENDPOINTS.CHANNELS}?subdomain=${encodeURIComponent(subdomain)}`
      : API_ENDPOINTS.CHANNELS;
    const response = await directFetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      mode: 'cors'
    });
    return handleResponse<Channel[]>(response);
  },

  async getChannelBySubdomain(subdomain: string): Promise<Channel | null> {
    const channels = await this.getChannels(subdomain);
    return channels.length > 0 ? channels[0] : null;
  },

  async updateMarkup(markup: MarkupUpdate): Promise<{ success: boolean; markup: MarkupUpdate }> {
    const response = await directFetch(API_ENDPOINTS.CHANNEL_MARKUP, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      mode: 'cors',
      body: JSON.stringify(markup)
    });
    return handleResponse<{ success: boolean; markup: MarkupUpdate }>(response);
  },

  async calculatePrice(request: PriceCalculationRequest): Promise<PriceCalculation> {
    const response = await directFetch(API_ENDPOINTS.PRICE_CALCULATE, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      mode: 'cors',
      body: JSON.stringify(request)
    });
    return handleResponse<PriceCalculation>(response);
  },

  async healthCheck(): Promise<{ status: string }> {
    const response = await directFetch(API_ENDPOINTS.HEALTH, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      },
      mode: 'cors'
    });
    return handleResponse<{ status: string }>(response);
  }
};

export { ApiError };


// Additional API methods for subdomain support
export const subdomainApi = {
  async calculatePriceBySubdomain(
    productId: string, 
    basePrice: number, 
    subdomain: string
  ): Promise<PriceCalculation> {
    const url = new URL(`${API_BASE_URL}/api/prices/calculate-by-subdomain`);
    url.searchParams.set('product_id', productId);
    url.searchParams.set('base_price', basePrice.toString());
    url.searchParams.set('subdomain', subdomain);
    
    const response = await directFetch(url.toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      mode: 'cors'
    });
    return handleResponse<PriceCalculation>(response);
  }
};
