<script lang="ts">
  import { onMount } from 'svelte';
  import { api, subdomainApi, type Channel, type PriceCalculation } from '$lib/api/client';
  import { channels, loading, error, calculation } from '$lib/stores/channels';
  import { API_BASE_URL, API_ENDPOINTS } from '$lib/config';
  import ChannelCard from './ChannelCard.svelte';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import ErrorMessage from './ErrorMessage.svelte';
  import SubdomainSelector from './SubdomainSelector.svelte';
  import { getSubdomainFromUrl } from '$lib/utils';

  let selectedSubdomain = getSubdomainFromUrl() || 'moscow';
  let filteredBySubdomain = false;

  async function fetchChannels(subdomain?: string) {
    try {
      loading.set(true);
      error.set(null);
      
      const data = await api.getChannels(subdomain);
      channels.set(data);
      filteredBySubdomain = !!subdomain;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      error.set(`Failed to fetch channels: ${errorMessage}`);
      console.error('Error fetching channels:', err);
    } finally {
      loading.set(false);
    }
  }

  async function updateMarkup(channelId: string, newMarkup: number) {
    try {
      await api.updateMarkup({
        channel_id: channelId,
        markup_percent: newMarkup
      });
      
      // Refresh channels list
      await fetchChannels();
      
      // Show success message (could be implemented with a toast store)
      console.log('✅ Markup updated successfully!');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      console.error('Error updating markup:', err);
      throw new Error(`Failed to update markup: ${errorMessage}`);
    }
  }

  async function calculatePrice(channelId: string, basePrice: number) {
    try {
      const result = await api.calculatePrice({
        product_id: 'demo_product',
        channel_id: channelId,
        base_price: basePrice
      });
      
      calculation.set(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      console.error('Error calculating price:', err);
      throw new Error(`Failed to calculate price: ${errorMessage}`);
    }
  }

  async function calculatePriceBySubdomain(basePrice: number, subdomain: string) {
    try {
      const result = await subdomainApi.calculatePriceBySubdomain(
        'demo_product',
        basePrice,
        subdomain
      );
      
      calculation.set(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      console.error('Error calculating price by subdomain:', err);
      throw new Error(`Failed to calculate price: ${errorMessage}`);
    }
  }

  function handleSubdomainChange(event: CustomEvent<{subdomain: string}>) {
    selectedSubdomain = event.detail.subdomain;
    fetchChannels(selectedSubdomain);
  }

  // Load channels on component mount
  onMount(() => {
    fetchChannels(selectedSubdomain);
  });
</script>

<div>
  <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">📊 Channel Management</h2>
  
  <SubdomainSelector 
    bind:selectedSubdomain
    on:change={handleSubdomainChange}
  />
  
  {#if $loading}
    <div class="flex justify-center items-center py-12">
      <LoadingSpinner />
      <span class="ml-3 text-gray-600 dark:text-gray-400">Loading channels...</span>
    </div>
  {:else if $error}
    <ErrorMessage message={$error}>
      <div class="mt-4">
        <p class="text-sm text-gray-600 dark:text-gray-400">Make sure the FastAPI backend is running on {API_BASE_URL}</p>
        <button 
          on:click={() => fetchChannels()}
          class="mt-2 px-4 py-2 bg-primary-500 dark:bg-primary-600 text-white rounded-md hover:bg-primary-600 dark:hover:bg-primary-700 transition-colors"
        >
          🔄 Retry
        </button>
      </div>
    </ErrorMessage>
  {:else if $channels.length === 0}
    <div class="text-center py-12">
      <p class="text-gray-500 dark:text-gray-400">No channels available</p>
    </div>
  {:else}
    <div class="grid gap-6">
      {#each $channels as channel (channel.id)}
        <ChannelCard 
          {channel} 
          on:updateMarkup={(event) => updateMarkup(event.detail.channelId, event.detail.markup)}
          on:calculatePrice={(event) => calculatePrice(event.detail.channelId, event.detail.basePrice)}
        />
      {/each}
    </div>
  {/if}
  
  {#if selectedSubdomain && filteredBySubdomain}
    <div class="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-700">
      <h3 class="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mb-3">🧪 Test Subdomain Price Calculation</h3>
      <div class="flex gap-3 items-end">
        <div class="flex-1">
          <label for="base-price-input" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Base Price ($)</label>
          <input 
            id="base-price-input"
            type="number" 
            step="0.01" 
            min="0"
            value={100}
            on:input={(e) => {
              const basePrice = parseFloat(e.currentTarget.value) || 100;
              calculatePriceBySubdomain(basePrice, selectedSubdomain);
            }}
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <button 
          on:click={() => calculatePriceBySubdomain(100, selectedSubdomain)}
          class="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded-md transition-colors"
        >
          Calculate for {selectedSubdomain}
        </button>
      </div>
    </div>
  {/if}
  
  {#if $calculation}
    <div class="channel-card mt-8 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-700">
      <h3 class="text-lg font-semibold text-green-900 dark:text-green-100 mb-4">🧮 Price Calculation Result</h3>
      <div class="space-y-2">
        <p><strong>Base Price:</strong> <span class="font-mono">${$calculation.base_price}</span></p>
        <p><strong>Markup:</strong> <span class="font-mono">{$calculation.markup_percent}%</span></p>
        <p><strong>Final Price:</strong> 
          <span class="text-xl font-bold text-primary-600 dark:text-primary-400 font-mono">${$calculation.final_price}</span>
        </p>
        <p class="text-sm text-gray-600 dark:text-gray-400"><strong>Channel ID:</strong> <code>{$calculation.channel_id}</code></p>
      </div>
    </div>
  {/if}
  
  <div class="mt-12 text-center text-sm text-gray-500 dark:text-gray-400">
    <p>💡 <strong>Demo Mode:</strong> Changes are simulated and won't persist</p>
    <p class="mt-2">🔗 
      <a href="{API_ENDPOINTS.DOCS}" target="_blank" rel="noopener noreferrer" 
         class="text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-300 underline">
        Open API Documentation
      </a>
    </p>
  </div>
</div>
