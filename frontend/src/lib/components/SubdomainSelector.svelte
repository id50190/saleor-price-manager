<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { getSubdomainFromUrl, setSubdomainParam, getAvailableSubdomains } from '$lib/utils';
  
  export let selectedSubdomain: string = getSubdomainFromUrl() || 'moscow';
  
  const dispatch = createEventDispatcher<{
    change: { subdomain: string }
  }>();
  
  const availableSubdomains = getAvailableSubdomains();
  
  const subdomainNames: Record<string, string> = {
    'default': '🌐 Default Channel',
    'moscow': '🏢 Moscow Store',
    'spb': '🏛️ SPb Store'
  };
  
  function handleSubdomainChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    const newSubdomain = target.value;
    
    selectedSubdomain = newSubdomain;
    setSubdomainParam(newSubdomain);
    
    dispatch('change', { subdomain: newSubdomain });
  }
  
  // Initialize URL parameter on mount
  if (typeof window !== 'undefined' && !getSubdomainFromUrl()) {
    setSubdomainParam(selectedSubdomain);
  }
</script>

<div class="subdomain-selector">
  <label for="subdomain-select" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
    🌎 Select Region/Channel:
  </label>
  <select 
    id="subdomain-select"
    bind:value={selectedSubdomain}
    on:change={handleSubdomainChange}
    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
  >
    {#each availableSubdomains as subdomain}
      <option value={subdomain}>
        {subdomainNames[subdomain] || subdomain}
      </option>
    {/each}
  </select>
  
  <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
    💡 URL parameter: <code class="bg-gray-100 dark:bg-gray-800 px-1 rounded">?subdomain={selectedSubdomain}</code>
  </div>
</div>

<style>
  .subdomain-selector {
    @apply mb-6 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700;
  }
</style>
