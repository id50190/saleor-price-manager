import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

export type ThemeMode = 'light' | 'dark' | 'system';

// Create theme store with initial value from localStorage or system preference
function createThemeStore() {
  // Default to system theme
  let initialTheme: ThemeMode = 'system';
  
  if (browser) {
    // Try to get saved preference from localStorage
    const saved = localStorage.getItem('theme-preference') as ThemeMode;
    if (saved && ['light', 'dark', 'system'].includes(saved)) {
      initialTheme = saved;
    }
  }

  const { subscribe, set, update } = writable<ThemeMode>(initialTheme);

  return {
    subscribe,
    set: (theme: ThemeMode) => {
      if (browser) {
        localStorage.setItem('theme-preference', theme);
      }
      set(theme);
    },
    toggle: () => {
      update(current => {
        const newTheme = current === 'light' ? 'dark' : current === 'dark' ? 'system' : 'light';
        if (browser) {
          localStorage.setItem('theme-preference', newTheme);
        }
        return newTheme;
      });
    }
  };
}

export const themeMode = createThemeStore();

// Derived store that resolves 'system' to actual light/dark based on media query
export const resolvedTheme = derived(
  themeMode,
  ($themeMode, set) => {
    if (!browser) {
      set('light');
      return;
    }

    if ($themeMode === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      const updateSystemTheme = () => {
        set(mediaQuery.matches ? 'dark' : 'light');
      };
      
      updateSystemTheme();
      mediaQuery.addEventListener('change', updateSystemTheme);
      
      return () => {
        mediaQuery.removeEventListener('change', updateSystemTheme);
      };
    } else {
      set($themeMode);
    }
  },
  'light' // Default value
);

// Store for checking if dark mode is active
export const isDark = derived(
  resolvedTheme,
  ($resolvedTheme) => $resolvedTheme === 'dark'
);
