import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	define: {
		// Pass APPLICATION_HOST and APPLICATION_PORT to frontend as VITE_ vars
		'import.meta.env.VITE_APPLICATION_HOST': JSON.stringify(process.env.APPLICATION_HOST || '127.0.0.1'),
		'import.meta.env.VITE_APPLICATION_PORT': JSON.stringify(process.env.APPLICATION_PORT || '8000'),
	},
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
