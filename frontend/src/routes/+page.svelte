<script lang="ts">
  import PriceManager from '$lib/components/PriceManager.svelte';
  import { API_BASE_URL, API_ENDPOINTS } from '$lib/config';
</script>

<svelte:head>
  <title>Saleor Price Manager</title>
  <meta name="description" content="FastAPI microservice for dynamic multi-channel pricing in Saleor eCommerce" />
</svelte:head>

<div class="container">
  <div class="header">
    <h1>🚀 Saleor Price Manager</h1>
    <span class="demo-badge">DEMO MODE</span>
    <p class="text-gray-600 dark:text-gray-400 mt-4">FastAPI microservice for dynamic multi-channel pricing</p>
  </div>
  
  <div class="api-info">
    <h3 class="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">📡 API Information</h3>
    <div class="space-y-2 text-sm">
      <p><strong class="text-gray-900 dark:text-gray-100">Backend:</strong> <code class="bg-blue-100 dark:bg-blue-800 px-2 py-1 rounded text-gray-900 dark:text-gray-100">{API_BASE_URL}</code></p>
      <p><strong class="text-gray-900 dark:text-gray-100">Swagger UI:</strong> 
        <a href="{API_ENDPOINTS.DOCS}" target="_blank" rel="noopener noreferrer" 
           class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline">
          {API_ENDPOINTS.DOCS}
        </a>
      </p>
      <p><strong class="text-gray-900 dark:text-gray-100">ReDoc:</strong> 
        <a href="{API_ENDPOINTS.REDOC}" target="_blank" rel="noopener noreferrer" 
           class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline">
          {API_ENDPOINTS.REDOC}
        </a>
      </p>
      <p><strong class="text-gray-900 dark:text-gray-100">Health Check:</strong> 
        <a href="{API_ENDPOINTS.HEALTH}" target="_blank" rel="noopener noreferrer"
           class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline">
          {API_ENDPOINTS.HEALTH}
        </a>
      </p>
    </div>
  </div>

  <PriceManager />
</div>
