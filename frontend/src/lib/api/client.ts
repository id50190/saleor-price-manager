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
  async getChannels(): Promise<Channel[]> {
    const response = await fetch(API_ENDPOINTS.CHANNELS);
    return handleResponse<Channel[]>(response);
  },

  async updateMarkup(markup: MarkupUpdate): Promise<{ success: boolean; markup: MarkupUpdate }> {
    const response = await fetch(API_ENDPOINTS.CHANNEL_MARKUP, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(markup)
    });
    return handleResponse<{ success: boolean; markup: MarkupUpdate }>(response);
  },

  async calculatePrice(request: PriceCalculationRequest): Promise<PriceCalculation> {
    const response = await fetch(API_ENDPOINTS.PRICE_CALCULATE, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    });
    return handleResponse<PriceCalculation>(response);
  },

  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(API_ENDPOINTS.HEALTH);
    return handleResponse<{ status: string }>(response);
  }
};

export { ApiError };
