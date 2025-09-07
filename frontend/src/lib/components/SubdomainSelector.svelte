<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { getSubdomainFromUrl, setSubdomainParam, extractSubdomainsFromChannels, getChannelDisplayName } from '$lib/utils';
  import { api, type Channel } from '$lib/api/client';
  
  export let selectedSubdomain: string = getSubdomainFromUrl() || 'moscow';
  
  const dispatch = createEventDispatcher<{
    change: { subdomain: string }
  }>();
  
  let availableSubdomains: string[] = ['moscow', 'spb', 'default']; // fallback
  let channels: Channel[] = [];
  let loading = true;
  let error: string | null = null;
  
  function getSubdomainDisplayName(subdomain: string): string {
    const channelName = getChannelDisplayName(subdomain, channels);
    
    // Add icons for common subdomains
    const iconMap: Record<string, string> = {
      'default': '🌐',
      'main': '🌐', 
      'www': '🌐',
      'moscow': '🏢',
      'msk': '🏢',
      'ru-moscow': '🏢',
      'spb': '🏛️',
      'piter': '🏛️',
      'leningrad': '🏛️'
    };
    
    const icon = iconMap[subdomain.toLowerCase()] || '🌍';
    return `${icon} ${channelName}`;
  }
  
  function handleSubdomainChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    const newSubdomain = target.value;
    
    selectedSubdomain = newSubdomain;
    setSubdomainParam(newSubdomain);
    
    dispatch('change', { subdomain: newSubdomain });
  }
  
  async function loadChannelsAndSubdomains() {
    try {
      loading = true;
      error = null;
      
      channels = await api.getChannels();
      availableSubdomains = extractSubdomainsFromChannels(channels);
      
      // If current selectedSubdomain is not in the list, use the first available
      if (availableSubdomains.length > 0 && !availableSubdomains.includes(selectedSubdomain)) {
        selectedSubdomain = availableSubdomains[0];
        setSubdomainParam(selectedSubdomain);
        dispatch('change', { subdomain: selectedSubdomain });
      }
      
    } catch (err) {
      console.error('Failed to load channels:', err);
      error = 'Failed to load channels';
      // Keep fallback data
    } finally {
      loading = false;
    }
  }
  
  onMount(() => {
    loadChannelsAndSubdomains();
    
    // Initialize URL parameter if not set
    if (typeof window !== 'undefined' && !getSubdomainFromUrl()) {
      setSubdomainParam(selectedSubdomain);
    }
  });
</script>

<div class="subdomain-selector">
  <label for="subdomain-select" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
    🌎 Select Region/Channel:
  </label>
  
  {#if loading}
    <div class="animate-pulse">
      <div class="h-10 bg-gray-200 dark:bg-gray-600 rounded-md"></div>
    </div>
  {:else if error}
    <div class="text-red-500 text-sm mb-2">
      ⚠️ {error} (using fallback data)
    </div>
    <select 
      id="subdomain-select"
      bind:value={selectedSubdomain}
      on:change={handleSubdomainChange}
      class="w-full px-3 py-2 border border-red-300 dark:border-red-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
    >
      {#each availableSubdomains as subdomain}
        <option value={subdomain}>
          {getSubdomainDisplayName(subdomain)}
        </option>
      {/each}
    </select>
  {:else}
    <select 
      id="subdomain-select"
      bind:value={selectedSubdomain}
      on:change={handleSubdomainChange}
      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
    >
      {#each availableSubdomains as subdomain}
        <option value={subdomain}>
          {getSubdomainDisplayName(subdomain)}
        </option>
      {/each}
    </select>
  {/if}
  
  <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
    💡 URL parameter: <code class="bg-gray-100 dark:bg-gray-800 px-1 rounded">?subdomain={selectedSubdomain}</code>
    {#if channels.length > 0}
      <span class="ml-2">• {channels.length} channel{channels.length === 1 ? '' : 's'} available</span>
    {/if}
  </div>
</div>

<style>
  .subdomain-selector {
    margin-bottom: 1.5rem;
    padding: 1rem;
    background-color: rgb(249 250 251);
    border-radius: 0.5rem;
    border: 1px solid rgb(229 231 235);
  }
  
  :global(.dark) .subdomain-selector {
    background-color: rgb(31 41 55 / 0.5);
    border-color: rgb(55 65 81);
  }
</style>
