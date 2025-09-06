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

export function setSubdomainParam(subdomain: string): void {
  if (typeof window === 'undefined') return;
  
  const url = new URL(window.location.href);
  if (subdomain) {
    url.searchParams.set('subdomain', subdomain);
  } else {
    url.searchParams.delete('subdomain');
  }
  
  // Use replaceState to update URL without navigation
  // Note: SvelteKit warns about this, but for URL parameters without routing it's acceptable
  window.history.replaceState({}, '', url.toString());
}

export function getAvailableSubdomains(): string[] {
  return ['moscow', 'spb', 'default'];
}
