<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Channel } from '$lib/api/client';

  export let channel: Channel;

  const dispatch = createEventDispatcher<{
    updateMarkup: { channelId: string; markup: number };
    calculatePrice: { channelId: string; basePrice: number };
  }>();

  let markupInput = '';
  let priceInput = '';
  let isUpdating = false;
  let isCalculating = false;
  let updateError = '';
  let calculateError = '';

  async function handleUpdateMarkup() {
    if (!markupInput.trim()) return;
    
    const markup = parseFloat(markupInput);
    if (isNaN(markup) || markup < 0 || markup > 1000) {
      updateError = 'Please enter a valid markup between 0 and 1000';
      return;
    }

    try {
      isUpdating = true;
      updateError = '';
      dispatch('updateMarkup', { channelId: channel.id, markup });
      markupInput = ''; // Clear input after successful update
    } catch (error) {
      updateError = error instanceof Error ? error.message : 'Failed to update markup';
    } finally {
      isUpdating = false;
    }
  }

  async function handleCalculatePrice() {
    if (!priceInput.trim()) return;
    
    const basePrice = parseFloat(priceInput);
    if (isNaN(basePrice) || basePrice < 0) {
      calculateError = 'Please enter a valid price greater than 0';
      return;
    }

    try {
      isCalculating = true;
      calculateError = '';
      dispatch('calculatePrice', { channelId: channel.id, basePrice });
    } catch (error) {
      calculateError = error instanceof Error ? error.message : 'Failed to calculate price';
    } finally {
      isCalculating = false;
    }
  }

  function handleMarkupKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      handleUpdateMarkup();
    }
  }

  function handlePriceKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      handleCalculatePrice();
    }
  }
</script>

<div class="channel-card">
  <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">🏠 {channel.name}</h3>
  <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1 mb-6">
    <p><strong class="text-gray-900 dark:text-gray-100">Slug:</strong> <code class="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-xs text-gray-900 dark:text-gray-100">{channel.slug}</code></p>
    <p><strong class="text-gray-900 dark:text-gray-100">Current Markup:</strong> 
      <span class="font-semibold text-primary-600 dark:text-primary-400">{channel.markup_percent}%</span>
    </p>
  </div>
  
  <!-- Update Markup Form -->
  <div class="markup-form">
    <label for="markup-{channel.id}" class="text-sm font-medium text-gray-700 dark:text-gray-300 min-w-fit">
      Update Markup:
    </label>
    <input 
      id="markup-{channel.id}"
      type="number" 
      class="markup-input" 
      class:border-red-500={updateError}
      class:dark:border-red-400={updateError}
      bind:value={markupInput}
      placeholder="15.5"
      step="0.1"
      min="0"
      max="1000"
      disabled={isUpdating}
      on:keydown={handleMarkupKeydown}
    />
    <span class="text-sm text-gray-500 dark:text-gray-400">%</span>
    <button 
      class="update-btn disabled:opacity-50 disabled:cursor-not-allowed"
      class:bg-gray-400={isUpdating}
      class:dark:bg-gray-600={isUpdating}
      disabled={isUpdating || !markupInput.trim()}
      on:click={handleUpdateMarkup}
    >
      {#if isUpdating}
        <div class="flex items-center space-x-2">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          <span>Saving...</span>
        </div>
      {:else}
        💾 Update
      {/if}
    </button>
  </div>
  {#if updateError}
    <p class="text-red-600 dark:text-red-400 text-sm mt-2">{updateError}</p>
  {/if}
  
  <!-- Test Price Calculation Form -->
  <div class="markup-form">
    <label for="price-{channel.id}" class="text-sm font-medium text-gray-700 dark:text-gray-300 min-w-fit">
      Test Price Calculation:
    </label>
    <input 
      id="price-{channel.id}"
      type="number" 
      class="markup-input"
      class:border-red-500={calculateError}
      class:dark:border-red-400={calculateError}
      bind:value={priceInput}
      placeholder="100.00"
      step="0.01"
      min="0"
      disabled={isCalculating}
      on:keydown={handlePriceKeydown}
    />
    <span class="text-sm text-gray-500 dark:text-gray-400">$</span>
    <button 
      class="update-btn disabled:opacity-50 disabled:cursor-not-allowed"
      class:bg-gray-400={isCalculating}
      class:dark:bg-gray-600={isCalculating}
      disabled={isCalculating || !priceInput.trim()}
      on:click={handleCalculatePrice}
    >
      {#if isCalculating}
        <div class="flex items-center space-x-2">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          <span>Calculating...</span>
        </div>
      {:else}
        🧮 Calculate
      {/if}
    </button>
  </div>
  {#if calculateError}
    <p class="text-red-600 dark:text-red-400 text-sm mt-2">{calculateError}</p>
  {/if}
</div>
