import { dev } from '$app/environment';

// API Configuration
export const API_BASE_URL = 
  typeof window !== 'undefined' && window.location.hostname !== 'localhost' 
    ? `http://${window.location.hostname}:8000`  // Production/deployed
    : import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';  // Development

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
