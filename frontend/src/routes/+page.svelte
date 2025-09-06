<script lang="ts">
  import PriceManager from '$lib/components/PriceManager.svelte';
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
      <p><strong>Backend:</strong> <code class="bg-blue-100 dark:bg-blue-800 px-2 py-1 rounded">http://localhost:8000</code></p>
      <p><strong>Swagger UI:</strong> 
        <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" 
           class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline">
          http://localhost:8000/docs
        </a>
      </p>
      <p><strong>Health Check:</strong> 
        <a href="http://localhost:8000/health" target="_blank" rel="noopener noreferrer"
           class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline">
          http://localhost:8000/health
        </a>
      </p>
    </div>
  </div>

  <PriceManager />
</div>
