<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { getSubdomainFromUrl, setSubdomainParam, extractSubdomainsFromChannels, getChannelDisplayName } from '$lib/utils';
  import { api, type Channel } from '$lib/api/client';
  
  export let selectedChannel: Channel | null = null;
  export let selectedSubdomain: string = getSubdomainFromUrl() || '';
  
  const dispatch = createEventDispatcher<{
    change: { subdomain: string }
  }>();
  
  let availableSubdomains: string[] = [];
  
  // Extract subdomains from the selected channel
  function updateAvailableSubdomains() {
    if (!selectedChannel) {
      availableSubdomains = [];
      selectedSubdomain = '';
      return;
    }
    
    const channelSubdomains: string[] = [];
    
    for (const meta of selectedChannel.metadata || []) {
      if (meta.key === 'subdomains' || meta.key === 'subdomain') {
        const subdomains = meta.value.split(',').map(s => s.trim()).filter(s => s);
        channelSubdomains.push(...subdomains);
      }
    }
    
    // Fallback to channel slug if no subdomains in metadata
    if (channelSubdomains.length === 0) {
      channelSubdomains.push(selectedChannel.slug);
    }
    
    availableSubdomains = [...new Set(channelSubdomains)]; // Remove duplicates
    
    // Auto-select first subdomain if current selection is not available
    if (availableSubdomains.length > 0 && !availableSubdomains.includes(selectedSubdomain)) {
      selectedSubdomain = availableSubdomains[0];
      setSubdomainParam(selectedSubdomain);
      dispatch('change', { subdomain: selectedSubdomain });
    }
  }
  
  // React to channel changes
  $: if (selectedChannel) {
    updateAvailableSubdomains();
  } else {
    // Clear subdomain when no channel selected
    availableSubdomains = [];
    if (selectedSubdomain) {
      selectedSubdomain = '';
      setSubdomainParam('');
      dispatch('change', { subdomain: '' });
    }
  }
  
  function getSubdomainDisplayName(subdomain: string): string {
    // Add icons for pool subdomains
    const iconMap: Record<string, string> = {
      // Pool #1 subdomains
      'pool1': '🏊‍♀️',
      'premium': '👑',
      'vip': '⭐',
      
      // Pool #2 subdomains
      'pool2': '🏊‍♂️',
      'business': '💼',
      'pro': '📈',
      
      // Pool #3 subdomains
      'pool3': '🏊',
      'enterprise': '🏢',
      'gold': '🥇',
      
      // Pool #4 subdomains
      'pool4': '🌊',
      'platinum': '💎',
      'ultimate': '🏆'
    };
    
    const icon = iconMap[subdomain.toLowerCase()] || '🌍';
    return `${icon} ${subdomain}`;
  }
  
  function handleSubdomainChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    const newSubdomain = target.value;
    
    selectedSubdomain = newSubdomain;
    setSubdomainParam(newSubdomain);
    
    dispatch('change', { subdomain: newSubdomain });
  }
  
  // Initialize URL parameter on mount
  function initializeUrlParam() {
    if (typeof window !== 'undefined' && selectedSubdomain && !getSubdomainFromUrl()) {
      setSubdomainParam(selectedSubdomain);
    }
  }
  
  $: if (selectedSubdomain) {
    initializeUrlParam();
  }
</script>

<div class="subdomain-selector">
  <label for="subdomain-select" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
    🌍 Step 2: Select Subdomain for {selectedChannel?.name || 'selected pool'}:
  </label>
  
  {#if !selectedChannel}
    <div class="text-gray-500 text-sm p-3 bg-gray-100 dark:bg-gray-700 rounded-md">
      ⚠️ Please select a pool/channel first (Step 1)
    </div>
  {:else if availableSubdomains.length === 0}
    <div class="text-yellow-600 text-sm p-3 bg-yellow-100 dark:bg-yellow-900/20 rounded-md">
      ⚠️ No subdomains configured for {selectedChannel.name}
    </div>
  {:else}
    <select 
      id="subdomain-select"
      bind:value={selectedSubdomain}
      on:change={handleSubdomainChange}
      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
    >
      <option value="">Choose subdomain for {selectedChannel.name}...</option>
      {#each availableSubdomains as subdomain}
        <option value={subdomain}>
          {getSubdomainDisplayName(subdomain)}
        </option>
      {/each}
    </select>
  {/if}
  
  <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
    💡 URL parameter: <code class="bg-gray-100 dark:bg-gray-800 px-1 rounded">?subdomain={selectedSubdomain}</code>
    {#if selectedChannel}
      <span class="ml-2">• Channel: {selectedChannel.name}</span>
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
