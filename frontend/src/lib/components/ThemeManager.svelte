<script lang="ts">
  import { onMount } from 'svelte';
  import { resolvedTheme } from '$lib/stores/theme';
  import { browser } from '$app/environment';

  // Apply theme class to document element
  $: if (browser && $resolvedTheme) {
    const htmlElement = document.documentElement;
    if ($resolvedTheme === 'dark') {
      htmlElement.classList.add('dark');
    } else {
      htmlElement.classList.remove('dark');
    }
  }

  onMount(() => {
    // Prevent flash of unstyled content by applying theme immediately
    const htmlElement = document.documentElement;
    
    // Check if theme is already applied (from SSR or previous visit)
    if (!htmlElement.classList.contains('dark') && $resolvedTheme === 'dark') {
      htmlElement.classList.add('dark');
    } else if (htmlElement.classList.contains('dark') && $resolvedTheme === 'light') {
      htmlElement.classList.remove('dark');
    }
  });
</script>

<!-- This component doesn't render anything visible -->
