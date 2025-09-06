<script lang="ts">
  import { onMount } from 'svelte';
  import { API_BASE_URL } from '$lib/config';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import ErrorMessage from './ErrorMessage.svelte';
  
  interface Product {
    id: string;
    name: string;
    slug: string;
    discounts: Array<{
      percent: number;
      cap: string;
      shedule: string;
      period?: {
        datetime_start: string;
        datetime_end: string;
      };
    }>;
    active_discount: any;
  }
  
  interface PriceCalculation {
    product_id: string;
    channel_id: string;
    base_price: string;
    markup_percent: string;
    discount_percent?: string;
    discount_applied: boolean;
    final_price: string;
    currency: string;
    active_discount?: any;
  }
  
  export let selectedSubdomain: string = 'moscow';
  
  let products: Product[] = [];
  let loading = false;
  let error: string | null = null;
  let priceCalculations: Record<string, PriceCalculation> = {};
  let basePrice = 100;
  
  async function fetchProducts() {
    try {
      loading = true;
      error = null;
      
      const response = await fetch(`${API_BASE_URL}/api/products/`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      products = await response.json();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      error = `Failed to fetch products: ${errorMessage}`;
      console.error('Error fetching products:', err);
    } finally {
      loading = false;
    }
  }
  
  async function calculatePriceForProduct(productId: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/prices/calculate-with-discounts?subdomain=${selectedSubdomain}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_id: productId,
          base_price: basePrice
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const calculation = await response.json();
      priceCalculations[productId] = calculation;
      priceCalculations = { ...priceCalculations }; // Trigger reactivity
    } catch (err) {
      console.error('Error calculating price for product:', err);
    }
  }
  
  function formatCron(cron: string): string {
    if (cron === '* * * * *') return 'Always active';
    if (cron === '0 9-17 * * 1-5') return 'Weekdays 9AM-5PM';
    return cron;
  }
  
  function formatDate(dateStr: string): string {
    try {
      const [datePart, timePart] = dateStr.split('T');
      const [day, month, year] = datePart.split('-');
      const [time] = timePart.split('Z');
      return `${day}/${month}/${year} ${time}`;
    } catch {
      return dateStr;
    }
  }
  
  // Load products on component mount
  onMount(() => {
    fetchProducts();
  });
  
  // Recalculate prices when subdomain changes
  $: if (selectedSubdomain) {
    priceCalculations = {};
  }
</script>

<div class="products-manager">
  <div class="header-section">
    <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">🛍️ Products & Discounts</h3>
    
    <div class="controls mb-4">
      <div class="price-input">
        <label for="base-price" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Test Base Price ($):
        </label>
        <input 
          id="base-price"
          type="number" 
          step="0.01" 
          min="0"
          bind:value={basePrice}
          class="w-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
        />
      </div>
    </div>
  </div>
  
  {#if loading}
    <div class="flex justify-center items-center py-8">
      <LoadingSpinner />
      <span class="ml-3 text-gray-600 dark:text-gray-400">Loading products...</span>
    </div>
  {:else if error}
    <ErrorMessage message={error}>
      <button 
        on:click={fetchProducts}
        class="mt-2 px-4 py-2 bg-primary-500 dark:bg-primary-600 text-white rounded-md hover:bg-primary-600 dark:hover:bg-primary-700 transition-colors"
      >
        🔄 Retry
      </button>
    </ErrorMessage>
  {:else if products.length === 0}
    <div class="text-center py-8">
      <p class="text-gray-500 dark:text-gray-400">No products found</p>
    </div>
  {:else}
    <div class="products-grid gap-6">
      {#each products as product (product.id)}
        <div class="product-card p-4 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800">
          <div class="product-header mb-3">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{product.name}</h4>
            <p class="text-sm text-gray-500 dark:text-gray-400">ID: <code class="text-xs">{product.id}</code></p>
          </div>
          
          <!-- Discounts Section -->
          <div class="discounts-section mb-4">
            <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              📋 Configured Discounts ({product.discounts.length})
            </h5>
            
            {#if product.discounts.length === 0}
              <p class="text-sm text-gray-500 dark:text-gray-400 italic">No discounts configured</p>
            {:else}
              <div class="space-y-2">
                {#each product.discounts as discount, index}
                  <div class="discount-item p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs">
                    <div class="flex justify-between items-center">
                      <span class="font-medium text-gray-900 dark:text-gray-100">
                        {discount.percent > 0 ? '+' : ''}{discount.percent}% 
                        <span class="text-gray-500">(cap: ${discount.cap})</span>
                      </span>
                      {#if product.active_discount && JSON.stringify(discount) === JSON.stringify(product.active_discount)}
                        <span class="bg-green-500 text-white px-2 py-1 rounded text-xs font-bold">ACTIVE</span>
                      {:else}
                        <span class="bg-gray-400 text-white px-2 py-1 rounded text-xs">inactive</span>
                      {/if}
                    </div>
                    <div class="mt-1 text-gray-600 dark:text-gray-300">
                      <div><strong class="text-gray-900 dark:text-gray-100">Schedule:</strong> {formatCron(discount.shedule)}</div>
                      {#if discount.period}
                        <div><strong class="text-gray-900 dark:text-gray-100">Period:</strong> {formatDate(discount.period.datetime_start)} - {formatDate(discount.period.datetime_end)}</div>
                      {/if}
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
          
          <!-- Price Testing Section -->
          <div class="price-testing">
            <button 
              on:click={() => calculatePriceForProduct(product.id)}
              class="w-full px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-md transition-colors text-sm"
            >
              🧮 Calculate Price for {selectedSubdomain}
            </button>
            
            {#if priceCalculations[product.id]}
              {@const calc = priceCalculations[product.id]}
              <div class="price-result mt-3 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded">
                <div class="text-sm space-y-1">
                  <div><strong class="text-gray-900 dark:text-gray-100">Base:</strong> <span class="font-mono">${calc.base_price}</span></div>
                  <div><strong class="text-gray-900 dark:text-gray-100">Channel Markup:</strong> <span class="font-mono">{calc.markup_percent}%</span></div>
                  {#if calc.discount_applied}
                    <div><strong class="text-gray-900 dark:text-gray-100">Discount:</strong> <span class="font-mono text-green-600">{calc.discount_percent}%</span></div>
                  {:else}
                    <div class="text-gray-500 dark:text-gray-400">No active discount</div>
                  {/if}
                  <div class="border-t pt-1 mt-2">
                    <strong class="text-gray-900 dark:text-gray-100">Final Price:</strong> 
                    <span class="text-lg font-bold text-green-600 font-mono">${calc.final_price}</span>
                  </div>
                </div>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .products-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  }
  
  .price-input {
    display: inline-block;
  }
</style>
