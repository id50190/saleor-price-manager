# Production Deployment Guide

## Node.js Requirements

This SvelteKit 5 application requires **Node.js 22.x (LTS)** or **Node.js 24.7.0+** in production.

### Supported Platforms

#### Vercel
- ✅ **Node 22.x LTS** - [Official support](https://vercel.com/docs/functions/runtimes/node-js/node-js-versions)
- ✅ **Auto-detection** - Vercel automatically uses the correct version

#### Other Platforms
- ✅ **Node 24.7.0+** - Latest stable version
- ✅ **Node 22.12+** - LTS version

## Pre-deployment Checklist

### 1. Update package.json for production

```json
{
  "engines": {
    "node": "^22.12 || >=24.7.0"
  }
}
```

**Current Status**: Commented out for local development with Node 18

### 2. Verify SvelteKit 5 features work

```bash
npm run check    # TypeScript validation
npm run build    # Production build
npm run preview  # Test production build
```

### 3. Environment Variables

Ensure these are set in production:

```bash
# Frontend build
NODE_ENV=production

# API endpoints (adjust for your setup)
PUBLIC_API_URL=https://your-api.domain.com
PUBLIC_API_BASE_URL=https://your-api.domain.com
```

## Deployment Steps

### Vercel Deployment

1. **Connect repository** to Vercel
2. **Set Node version** (automatic for Node 22.x)
3. **Configure build commands**:
   ```bash
   # Build command
   npm run build
   
   # Output directory
   .svelte-kit/output
   ```
4. **Deploy**

### Manual Server Deployment

1. **Install Node 22.x/24.7.0+**:
   ```bash
   # Using Node Version Manager
   nvm install 22
   nvm use 22
   
   # Or download from nodejs.org
   ```

2. **Install dependencies**:
   ```bash
   npm ci --production
   ```

3. **Build application**:
   ```bash
   npm run build
   ```

4. **Start production server**:
   ```bash
   npm run preview
   # Or use a process manager like PM2
   ```

### Docker Deployment

```dockerfile
# Use Node 22 LTS
FROM node:22-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
```

## Performance Optimizations

### SvelteKit 5 Benefits
- **Smaller bundles**: Better tree-shaking
- **Faster builds**: Improved Vite integration
- **Better hydration**: More efficient client-side rendering
- **Enhanced SSR**: Improved server-side rendering

### Build Optimizations
```javascript
// vite.config.js
export default defineConfig({
  plugins: [sveltekit()],
  build: {
    minify: 'terser',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['svelte', '@sveltejs/kit']
        }
      }
    }
  }
});
```

## Monitoring & Debugging

### Error Tracking
- Add Sentry or similar error tracking
- Monitor Core Web Vitals
- Track bundle sizes

### Performance Monitoring
```javascript
// app.html - Add performance monitoring
<script>
  // Web Vitals tracking
  import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';
  
  getCLS(console.log);
  getFID(console.log);
  getFCP(console.log);
  getLCP(console.log);
  getTTFB(console.log);
</script>
```

## Troubleshooting

### Common Issues

1. **Node version mismatch**:
   ```bash
   # Check current version
   node --version
   
   # Should be 22.x or 24.7.0+
   ```

2. **Build failures**:
   ```bash
   # Clear cache
   rm -rf node_modules .svelte-kit
   npm install
   npm run build
   ```

3. **Runtime errors**:
   - Check browser console for client-side errors
   - Check server logs for SSR errors
   - Verify environment variables are set

### Support

- 📚 **SvelteKit Docs**: https://svelte.dev/docs/kit
- 🐛 **Issues**: Create GitHub issue with build logs
- 💬 **Community**: SvelteKit Discord/Reddit

---

**Ready for production with Node 22.x/24.7.0+ environments! 🚀**
