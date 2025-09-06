import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: parseInt(process.env.VITE_PORT || '3000'),
		host: process.env.VITE_HOST || '0.0.0.0',
		fs: {
			// Reduce file watching to prevent OS limits
			allow: ['..', '.']
		}
	},
	optimizeDeps: {
		// Exclude problematic deps from pre-bundling to reduce file watching
		exclude: ['@sveltejs/kit']
	}
});
