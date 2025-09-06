# Troubleshooting Guide

## File Watch Limit Issues

If you see `OS file watch limit reached` errors, increase the system limits:

### Linux (Ubuntu/Debian)

```bash
# Temporary fix (until reboot)
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Or increase limits permanently
echo 'fs.inotify.max_user_watches=524288' | sudo tee -a /etc/sysctl.conf
echo 'fs.inotify.max_user_instances=256' | sudo tee -a /etc/sysctl.conf
echo 'fs.inotify.max_queued_events=32768' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### macOS

```bash
# Install watchman for better file watching
brew install watchman

# Or increase limits
echo 'kern.maxfiles=65536' | sudo tee -a /etc/sysctl.conf
echo 'kern.maxfilesperproc=32768' | sudo tee -a /etc/sysctl.conf
```

### Alternative Solutions

1. **Use polling instead of native watching**:
   ```bash
   export VITE_USE_POLLING=true
   ./START_FRONTEND
   ```

2. **Reduce watched files** (already configured in vite.config.ts):
   ```javascript
   server: {
     fs: {
       allow: ['..', '.']
     }
   }
   ```

3. **Exclude node_modules from watching**:
   ```bash
   echo 'node_modules/' >> .watchmanconfig
   ```

## Port Conflicts

If ports are already in use:

```bash
# Check what's using the ports
lsof -ti:3000
lsof -ti:8000

# Kill processes if needed
kill -9 $(lsof -ti:3000)
kill -9 $(lsof -ti:8000)

# Or use different ports
export PORT=3001
export APPLICATION_PORT=8001
./BANG
```

## SvelteKit Issues

### TSConfig Warnings

```bash
# Regenerate SvelteKit files
cd frontend
npm run check
# This runs svelte-kit sync automatically
```

### Build Issues

```bash
# Clear all caches and reinstall
cd frontend
rm -rf node_modules .svelte-kit
npm install
npm run build
```

### Node Version Issues

```bash
# Check current version
node --version

# For development: Node 18+ is fine
# For production: Need Node 22.x or 24.7.0+

# Using nvm (recommended)
nvm install 22
nvm use 22
```

## Backend Issues

### Python Environment

```bash
# Recreate virtual environment
rm -rf env
./DEPLOY
```

### Rust Module

```bash
# Rebuild Rust module
./BUILD
```

### Redis Connection

```bash
# Start Redis
sudo systemctl start redis

# Or use Docker
docker run -d -p 6379:6379 redis:7.0

# Application works without Redis too
```

## Performance Issues

### Memory Usage

```bash
# Limit Node.js memory
export NODE_OPTIONS="--max-old-space-size=4096"

# For Vite dev server
export VITE_DISABLE_DEV_OVERLAY=true
```

### Build Performance

```bash
# Use multiple cores
export VITE_BUILD_THREADS=4

# Disable source maps in development
export VITE_DEV_SOURCEMAP=false
```

## Quick Fixes

### Complete Reset

```bash
# Stop all processes
ps aux | grep -E '(uvicorn|vite|node)' | awk '{print $2}' | xargs kill -9

# Clean everything
rm -rf frontend/node_modules frontend/.svelte-kit
rm -rf env __pycache__ .pytest_cache

# Rebuild
./DEPLOY
./BANG
```

### Minimal Startup

```bash
# Start only backend
START_FRONTEND=false ./BANG

# Start only frontend (in another terminal)
./START_FRONTEND
```

---

**If issues persist, check logs and create a GitHub issue with:**
- OS and versions (node --version, python --version)
- Full error output
- Steps to reproduce
