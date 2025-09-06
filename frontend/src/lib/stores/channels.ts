import { writable, derived } from 'svelte/store';
import type { Channel, PriceCalculation } from '$lib/api/client';

export const channels = writable<Channel[]>([]);
export const loading = writable<boolean>(false);
export const error = writable<string | null>(null);
export const calculation = writable<PriceCalculation | null>(null);

// Derived store для получения канала по ID
export const getChannelById = derived(
  channels,
  ($channels) => (id: string) => $channels.find(channel => channel.id === id)
);

// Derived store для проверки есть ли каналы
export const hasChannels = derived(
  channels,
  ($channels) => $channels.length > 0
);

// Derived store для состояния загрузки без ошибок
export const isLoadingClean = derived(
  [loading, error],
  ([$loading, $error]) => $loading && !$error
);
