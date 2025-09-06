import { dev } from '$app/environment';

// API Configuration - respect exact environment configuration
// Priority: VITE_API_BASE_URL > constructed from APPLICATION_HOST > fallback to current hostname
const getApiBaseUrl = () => {
  // First priority: explicit API URL override
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // Second priority: use APPLICATION_HOST if available
  const host = import.meta.env.VITE_APPLICATION_HOST || '127.0.0.1';
  const port = import.meta.env.VITE_APPLICATION_PORT || '8000';
  
  // On client side, use configured host unless it's a bind-all address
  if (typeof window !== 'undefined') {
    if (host === '0.0.0.0' || host === '::') {
      // If backend binds to all interfaces, use current hostname for client
      return `http://${window.location.hostname}:${port}`;
    }
    return `http://${host}:${port}`;
  }
  
  // Server-side rendering fallback
  return `http://${host === '0.0.0.0' ? '127.0.0.1' : host}:${port}`;
};

export const API_BASE_URL = getApiBaseUrl();

// App Configuration
export const APP_CONFIG = {
  API_BASE_URL,
  API_TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT || '10000'),
  APP_TITLE: import.meta.env.VITE_APP_TITLE || 'Saleor Price Manager',
  IS_DEV: dev
};

// API Endpoints
export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/health`,
  DOCS: `${API_BASE_URL}/docs`,
  REDOC: `${API_BASE_URL}/redoc`,
  CHANNELS: `${API_BASE_URL}/api/channels/`,
  CHANNEL_MARKUP: `${API_BASE_URL}/api/channels/markup`,
  PRICE_CALCULATE: `${API_BASE_URL}/api/prices/calculate`
};
