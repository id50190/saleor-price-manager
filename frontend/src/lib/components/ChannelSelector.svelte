<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { api, type Channel } from '$lib/api/client';
  
  export let selectedChannelId: string | null = null;
  
  const dispatch = createEventDispatcher<{
    change: { channel: Channel | null }
  }>();
  
  let channels: Channel[] = [];
  let loading = true;
  let error: string | null = null;
  
  function getChannelIcon(channelName: string): string {
    const name = channelName.toLowerCase();
    if (name.includes('default')) return '🌐';
    if (name.includes('pln') || name.includes('poland')) return '🇵🇱';
    if (name.includes('pool') || name.includes('#')) return '🏊‍♂️';
    if (name.includes('moscow')) return '🇷🇺';
    if (name.includes('spb') || name.includes('petersburg')) return '🏛️';
    return '📊';
  }
  
  function handleChannelChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    const channelId = target.value;
    
    selectedChannelId = channelId || null;
    const selectedChannel = channels.find(c => c.id === channelId) || null;
    
    dispatch('change', { channel: selectedChannel });
  }
  
  async function loadChannels() {
    try {
      loading = true;
      error = null;
      
      channels = await api.getChannels();
      
      // If no channel selected and we have channels, select the first one
      if (!selectedChannelId && channels.length > 0) {
        selectedChannelId = channels[0].id;
        dispatch('change', { channel: channels[0] });
      }
      
    } catch (err) {
      console.error('Failed to load channels:', err);
      error = 'Failed to load channels';
    } finally {
      loading = false;
    }
  }
  
  onMount(() => {
    loadChannels();
  });
</script>

<div class="channel-selector">
  <label for="channel-select" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
    📊 Select Channel:
  </label>
  
  {#if loading}
    <div class="animate-pulse">
      <div class="h-10 bg-gray-200 dark:bg-gray-600 rounded-md"></div>
    </div>
  {:else if error}
    <div class="text-red-500 text-sm mb-2">
      ⚠️ {error}
    </div>
    <div class="text-gray-500 text-sm">Using fallback data</div>
  {:else}
    <select 
      id="channel-select"
      bind:value={selectedChannelId}
      on:change={handleChannelChange}
      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
    >
      <option value="">Select a channel...</option>
      {#each channels as channel}
        <option value={channel.id}>
          {getChannelIcon(channel.name)} {channel.name} ({channel.slug})
        </option>
      {/each}
    </select>
    
    <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
      💡 {channels.length} channel{channels.length === 1 ? '' : 's'} available
      {#if selectedChannelId}
        • Selected: {channels.find(c => c.id === selectedChannelId)?.name || 'Unknown'}
      {/if}
    </div>
  {/if}
</div>

<style>
  .channel-selector {
    margin-bottom: 1rem;
    padding: 1rem;
    background-color: rgb(243 244 246);
    border-radius: 0.5rem;
    border: 1px solid rgb(209 213 219);
  }
  
  :global(.dark) .channel-selector {
    background-color: rgb(17 24 39 / 0.5);
    border-color: rgb(55 65 81);
  }
</style>
