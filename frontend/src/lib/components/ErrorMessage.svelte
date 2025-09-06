<script lang="ts">
  export let message: string;
</script>

<div class="error-message">
  <h3 class="text-lg font-semibold mb-2">❌ Error</h3>
  <p class="mb-4">{message}</p>
  <slot />
</div>
