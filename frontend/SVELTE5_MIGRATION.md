# Svelte 5 Migration Guide

This project is prepared for Svelte 5 but uses compatible syntax for Node 18 development.
When fully migrated to Node 22+/24.7.0+, components can use modern runes.

## Modern Svelte 5 Syntax Examples

### State Management
```typescript
// Old Svelte 4
let count = 0;
let doubled = count * 2;
$: tripled = count * 3;

// New Svelte 5 runes
let count = $state(0);
let doubled = $derived(count * 2);
let tripled = $derived(count * 3);
```

### Effects
```typescript
// Old Svelte 4
$: {
  console.log('count changed:', count);
}

// New Svelte 5
$effect(() => {
  console.log('count changed:', count);
});
```

### Props
```typescript
// Old Svelte 4
export let title: string;
export let optional = 'default';

// New Svelte 5
interface Props {
  title: string;
  optional?: string;
}

let { title, optional = 'default' }: Props = $props();
```

### Example Component Migration

#### Current (Svelte 4 compatible):
```svelte
<script lang="ts">
  let isOpen = false;
  
  function toggle() {
    isOpen = !isOpen;
  }
</script>

{#if isOpen}
  <div>Content</div>
{/if}
<button on:click={toggle}>Toggle</button>
```

#### Future (Svelte 5 runes):
```svelte
<script lang="ts">
  let isOpen = $state(false);
  
  function toggle() {
    isOpen = !isOpen;
  }
</script>

{#if isOpen}
  <div>Content</div>
{/if}
<button onclick={toggle}>Toggle</button>
```

## Migration Steps (When on Node 22+/24.7.0+)

1. **Update package.json engines**:
   ```json
   "engines": {
     "node": "^22.12 || >=24.7.0"
   }
   ```

2. **Migrate state variables**: `let x = value` → `let x = $state(value)`

3. **Migrate reactive declarations**: `$: y = x * 2` → `let y = $derived(x * 2)`

4. **Migrate effects**: `$: { ... }` → `$effect(() => { ... })`

5. **Update event handlers**: `on:click` → `onclick` (optional)

6. **Migrate props**: `export let x` → `let { x } = $props()`

## Benefits of Svelte 5

- **Better performance**: More efficient reactivity
- **Improved TypeScript**: Better type inference
- **Cleaner syntax**: Less magic, more explicit
- **Better tree-shaking**: Smaller bundle sizes
- **Future-proof**: Long-term support

## Current Status

✅ SvelteKit 5 dependencies installed
✅ Compatible syntax used for Node 18 development  
✅ Ready for runes migration when on Node 22+/24.7.0+
⏳ Waiting for Node version upgrade for full runes usage
