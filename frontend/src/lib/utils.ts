// URL utilities for subdomain extraction
export function getSubdomainFromUrl(): string | null {
  if (typeof window === 'undefined') return null;
  
  // Check URL parameters first (?subdomain=moscow)
  const urlParams = new URLSearchParams(window.location.search);
  const subdomainParam = urlParams.get('subdomain');
  if (subdomainParam) {
    return subdomainParam;
  }
  
  // Check hostname for actual subdomain (moscow.example.com)
  const hostname = window.location.hostname;
  const parts = hostname.split('.');
  
  // If more than 2 parts and not localhost, assume first part is subdomain
  if (parts.length > 2 && hostname !== 'localhost') {
    return parts[0];
  }
  
  return null;
}

import { goto } from '$app/navigation';
import { page } from '$app/stores';

export function setSubdomainParam(subdomain: string): void {
  if (typeof window === 'undefined') return;
  
  const url = new URL(window.location.href);
  if (subdomain) {
    url.searchParams.set('subdomain', subdomain);
  } else {
    url.searchParams.delete('subdomain');
  }
  
  // Use SvelteKit navigation instead of direct history API
  goto(url.pathname + url.search, { replaceState: true, noScroll: true });
}

export function getAvailableSubdomains(): string[] {
  // Default subdomains - will be replaced by dynamic loading
  return ['moscow', 'spb', 'default'];
}

// Extract subdomains from channel metadata
export function extractSubdomainsFromChannels(channels: Array<{metadata?: Array<{key: string, value: string}>}>): string[] {
  const subdomains = new Set<string>();
  
  for (const channel of channels) {
    if (channel.metadata) {
      for (const meta of channel.metadata) {
        if (meta.key === 'subdomains' || meta.key === 'subdomain') {
          // Split comma-separated subdomains
          const channelSubdomains = meta.value.split(',').map(s => s.trim());
          channelSubdomains.forEach(sub => subdomains.add(sub));
        }
      }
    }
  }
  
  return Array.from(subdomains).sort();
}

// Get channel display name by subdomain
export function getChannelDisplayName(subdomain: string, channels: Array<{name: string, metadata?: Array<{key: string, value: string}>}>): string {
  for (const channel of channels) {
    if (channel.metadata) {
      for (const meta of channel.metadata) {
        if ((meta.key === 'subdomains' || meta.key === 'subdomain')) {
          const subdomains = meta.value.split(',').map(s => s.trim());
          if (subdomains.includes(subdomain)) {
            return channel.name;
          }
        }
      }
    }
  }
  return subdomain; // fallback to subdomain name
}
