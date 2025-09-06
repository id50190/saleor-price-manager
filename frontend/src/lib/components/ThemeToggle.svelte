<script lang="ts">
  import { themeMode, type ThemeMode } from '$lib/stores/theme';

  const themes: { mode: ThemeMode; icon: string; label: string }[] = [
    { mode: 'light', icon: '☀️', label: 'Light' },
    { mode: 'dark', icon: '🌙', label: 'Dark' },
    { mode: 'system', icon: '🖥️', label: 'System' }
  ];

  let isOpen = false;

  function selectTheme(theme: ThemeMode) {
    themeMode.set(theme);
    isOpen = false;
  }

  function toggleDropdown() {
    isOpen = !isOpen;
  }

  // Close dropdown when clicking outside
  function handleClickOutside(event: MouseEvent) {
    const target = event.target as Element;
    if (!target.closest('.theme-toggle')) {
      isOpen = false;
    }
  }
</script>

<svelte:window on:click={handleClickOutside} />

<div class="theme-toggle relative">
  <button
    type="button"
    on:click={toggleDropdown}
    class="
      flex items-center gap-2 px-3 py-2 
      text-sm font-medium text-gray-700 dark:text-gray-200
      bg-white dark:bg-gray-800 
      border border-gray-300 dark:border-gray-600 
      rounded-lg shadow-sm
      hover:bg-gray-50 dark:hover:bg-gray-700
      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
      transition-colors
    "
    aria-label="Theme selector"
    aria-expanded={isOpen}
  >
    {#each themes as theme}
      {#if $themeMode === theme.mode}
        <span class="text-base">{theme.icon}</span>
        <span class="hidden sm:inline">{theme.label}</span>
      {/if}
    {/each}
    <svg 
      class="w-4 h-4 transition-transform {isOpen ? 'rotate-180' : ''}" 
      fill="none" 
      stroke="currentColor" 
      viewBox="0 0 24 24"
    >
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
    </svg>
  </button>

  {#if isOpen}
    <div class="
      absolute right-0 top-full mt-2 z-50
      min-w-[140px] py-1
      bg-white dark:bg-gray-800
      border border-gray-300 dark:border-gray-600
      rounded-lg shadow-lg
      ring-1 ring-black ring-opacity-5
    ">
      {#each themes as theme}
        <button
          type="button"
          on:click={() => selectTheme(theme.mode)}
          class="
            w-full px-3 py-2 text-left flex items-center gap-3
            text-sm text-gray-700 dark:text-gray-200
            hover:bg-gray-100 dark:hover:bg-gray-700
            {$themeMode === theme.mode ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300' : ''}
            first:rounded-t-md last:rounded-b-md
            transition-colors
          "
        >
          <span class="text-base">{theme.icon}</span>
          <span>{theme.label}</span>
          {#if $themeMode === theme.mode}
            <svg class="w-4 h-4 ml-auto" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          {/if}
        </button>
      {/each}
    </div>
  {/if}
</div>
