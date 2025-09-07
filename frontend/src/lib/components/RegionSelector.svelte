<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { api, type Channel } from '$lib/api/client';
  import { getSubdomainFromUrl, setSubdomainParam } from '$lib/utils';
  
  export let selectedSubdomain: string = getSubdomainFromUrl() || '';
  export let selectedChannel: Channel | null = null;
  
  const dispatch = createEventDispatcher<{
    change: { subdomain: string; channel: Channel | null }
  }>();
  
  let allChannels: Channel[] = [];
  let availableSubdomains: Array<{ subdomain: string; channel: Channel; displayName: string; icon: string }> = [];
  let loading = true;
  let error: string | null = null;
  
  function getSubdomainIcon(subdomain: string, channelName: string): string {
    const sub = subdomain.toLowerCase();
    const name = channelName.toLowerCase();
    
    // Pool-specific icons
    if (name.includes('pool')) {
      const poolNum = name.match(/pool\s*#?(\d+)/);
      if (poolNum) {
        const icons = ['🏊‍♀️', '🏊‍♂️', '🏊', '🌊', '💧', '🔵'];
        return icons[(parseInt(poolNum[1]) - 1) % icons.length];
      }
      return '🏊‍♂️';
    }
    
    // Common subdomain patterns
    if (sub.includes('default') || sub.includes('main') || sub.includes('www')) return '🌐';
    if (sub.includes('premium') || sub.includes('vip')) return '👑';
    if (sub.includes('business') || sub.includes('pro')) return '💼';
    if (sub.includes('enterprise') || sub.includes('gold')) return '🥇';
    if (sub.includes('platinum') || sub.includes('ultimate')) return '💎';
    if (sub.includes('moscow') || sub.includes('msk')) return '🏢';
    if (sub.includes('spb') || sub.includes('piter')) return '🏛️';
    if (sub.includes('pool')) return '🏊‍♂️';
    
    return '🌍';
  }
  
  function getSubdomainDisplayName(subdomain: string, channel: Channel): string {
    const icon = getSubdomainIcon(subdomain, channel.name);
    
    // Create a readable display name
    let displayName = subdomain;
    
    // Add channel context if subdomain is generic
    if (['default', 'main', 'www'].includes(subdomain.toLowerCase())) {
      displayName = `${displayName} (${channel.name})`;
    } else if (subdomain.includes('pool') && channel.name.includes('Pool')) {
      // For pool subdomains, show more descriptive name
      displayName = `${channel.name} - ${subdomain}`;
    } else {
      // For other subdomains, capitalize first letter
      displayName = subdomain.charAt(0).toUpperCase() + subdomain.slice(1);
      // Add channel name in parentheses for context
      displayName = `${displayName} (${channel.name})`;
    }
    
    return `${icon} ${displayName}`;
  }
  
  function extractSubdomainsFromChannels(channels: Channel[]) {
    const subdomainList: Array<{ subdomain: string; channel: Channel; displayName: string; icon: string }> = [];
    
    for (const channel of channels) {
      const channelSubdomains: string[] = [];
      
      // Extract subdomains from metadata
      for (const meta of channel.metadata || []) {
        if (meta.key === 'subdomains' || meta.key === 'subdomain') {
          const subdomains = meta.value.split(',').map(s => s.trim()).filter(s => s);
          channelSubdomains.push(...subdomains);
        }
      }
      
      // Fallback to channel slug if no subdomains in metadata
      if (channelSubdomains.length === 0) {
        channelSubdomains.push(channel.slug);
      }
      
      // Add each subdomain to the list
      for (const subdomain of channelSubdomains) {
        const displayName = getSubdomainDisplayName(subdomain, channel);
        const icon = getSubdomainIcon(subdomain, channel.name);
        
        subdomainList.push({
          subdomain,
          channel,
          displayName,
          icon
        });
      }
    }
    
    return subdomainList;
  }
  
  function handleSubdomainChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    const newSubdomain = target.value;
    
    // Find the channel for this subdomain
    const subdomainData = availableSubdomains.find(s => s.subdomain === newSubdomain);
    const newChannel = subdomainData?.channel || null;
    
    selectedSubdomain = newSubdomain;
    selectedChannel = newChannel;
    
    // Update URL parameter
    setSubdomainParam(newSubdomain);
    
    dispatch('change', { 
      subdomain: newSubdomain, 
      channel: newChannel 
    });
  }
  
  async function loadSubdomains() {
    try {
      loading = true;
      error = null;
      
      // Load all channels first
      allChannels = await api.getChannels();
      
      // Extract all subdomains with their associated channels
      availableSubdomains = extractSubdomainsFromChannels(allChannels);
      
      // Sort subdomains for better UX
      availableSubdomains.sort((a, b) => {
        // Pool channels first, then others
        if (a.channel.name.includes('Pool') && !b.channel.name.includes('Pool')) return -1;
        if (!a.channel.name.includes('Pool') && b.channel.name.includes('Pool')) return 1;
        return a.displayName.localeCompare(b.displayName);
      });
      
      // Auto-select first subdomain if none selected or current selection is invalid
      if (availableSubdomains.length > 0) {
        const currentIsValid = availableSubdomains.some(s => s.subdomain === selectedSubdomain);
        
        if (!selectedSubdomain || !currentIsValid) {
          const firstSubdomain = availableSubdomains[0];
          selectedSubdomain = firstSubdomain.subdomain;
          selectedChannel = firstSubdomain.channel;
          setSubdomainParam(selectedSubdomain);
          
          dispatch('change', { 
            subdomain: selectedSubdomain, 
            channel: selectedChannel 
          });
        } else {
          // Update selectedChannel based on current subdomain
          const subdomainData = availableSubdomains.find(s => s.subdomain === selectedSubdomain);
          if (subdomainData) {
            selectedChannel = subdomainData.channel;
            dispatch('change', { 
              subdomain: selectedSubdomain, 
              channel: selectedChannel 
            });
          }
        }
      }
      
    } catch (err) {
      console.error('Failed to load subdomains:', err);
      error = 'Failed to load regions';
    } finally {
      loading = false;
    }
  }
  
  onMount(() => {
    loadSubdomains();
  });
</script>

<div class="region-selector">
  <label for="region-select" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
    🌍 Select Region/Channel:
  </label>
  
  {#if loading}
    <div class="animate-pulse">
      <div class="h-10 bg-gray-200 dark:bg-gray-600 rounded-md"></div>
    </div>
    <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
      Loading available regions...
    </div>
  {:else if error}
    <div class="text-red-500 text-sm mb-2">
      ⚠️ {error}
    </div>
    <button 
      on:click={loadSubdomains}
      class="px-3 py-2 bg-red-500 hover:bg-red-600 text-white rounded-md text-sm transition-colors"
    >
      🔄 Retry
    </button>
  {:else if availableSubdomains.length === 0}
    <div class="text-yellow-600 text-sm p-3 bg-yellow-100 dark:bg-yellow-900/20 rounded-md">
      ⚠️ No regions/subdomains available
    </div>
  {:else}
    <select 
      id="region-select"
      bind:value={selectedSubdomain}
      on:change={handleSubdomainChange}
      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
    >
      <option value="">Select a region...</option>
      {#each availableSubdomains as subdomainData}
        <option value={subdomainData.subdomain}>
          {subdomainData.displayName}
        </option>
      {/each}
    </select>
    
    <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
      💡 {availableSubdomains.length} region{availableSubdomains.length === 1 ? '' : 's'} available
      {#if selectedSubdomain && selectedChannel}
        <br/>📊 Channel: <strong class="text-gray-900 dark:text-gray-100">{selectedChannel.name}</strong> 
        • Markup: <strong class="text-primary-600 dark:text-primary-400">{selectedChannel.markup_percent}%</strong>
        <br/>🌐 URL: <code class="bg-gray-100 dark:bg-gray-800 px-1 rounded">?subdomain={selectedSubdomain}</code>
      {/if}
    </div>
  {/if}
</div>

<style>
  .region-selector {
    margin-bottom: 1.5rem;
    padding: 1rem;
    background-color: rgb(249 250 251);
    border-radius: 0.5rem;
    border: 1px solid rgb(229 231 235);
  }
  
  :global(.dark) .region-selector {
    background-color: rgb(31 41 55 / 0.5);
    border-color: rgb(55 65 81);
  }
  
  select {
    transition: all 0.2s ease;
  }
  
  select:focus {
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
</style>
