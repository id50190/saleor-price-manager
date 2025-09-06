<script lang="ts">
  import '../app.css';
  import ThemeManager from '$lib/components/ThemeManager.svelte';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
</script>

<ThemeManager />

<div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
  <!-- Theme toggle in top right corner -->
  <div class="absolute top-4 right-4 z-50">
    <ThemeToggle />
  </div>
  
  <slot />
</div>
