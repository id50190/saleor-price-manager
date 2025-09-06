<script lang="ts">
  import { onMount } from 'svelte';
  import { api, type Channel, type PriceCalculation } from '$lib/api/client';
  import { channels, loading, error, calculation } from '$lib/stores/channels';
  import { API_BASE_URL, API_ENDPOINTS } from '$lib/config';
  import ChannelCard from './ChannelCard.svelte';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import ErrorMessage from './ErrorMessage.svelte';

  async function fetchChannels() {
    try {
      loading.set(true);
      error.set(null);
      
      const data = await api.getChannels();
      channels.set(data);
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

  // Load channels on component mount
  onMount(() => {
    fetchChannels();
  });
</script>

<div>
  <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">📊 Channel Management</h2>
  
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
          on:click={fetchChannels}
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
  
  {#if $calculation}
    <div class="channel-card mt-8 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-700">
      <h3 class="text-lg font-semibold text-green-900 dark:text-green-100 mb-4">🧮 Price Calculation Result</h3>
      <div class="space-y-2">
        <p><strong>Base Price:</strong> <span class="font-mono">${$calculation.base_price}</span></p>
        <p><strong>Markup:</strong> <span class="font-mono">{$calculation.markup_percent}%</span></p>
        <p><strong>Final Price:</strong> 
          <span class="text-xl font-bold text-primary-600 dark:text-primary-400 font-mono">${$calculation.final_price}</span>
        </p>
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
