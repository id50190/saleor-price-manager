# Uvicorn File Watching Optimization

## Overview
Optimized Uvicorn configuration to watch only necessary files for development, reducing resource usage and preventing unnecessary reloads.

## Configuration

### Environment Variables
```bash
# .env
UVICORN_WATCH_DIRS=app,.           # Directories to watch
UVICORN_WATCH_INCLUDES=*.py,requirements*.txt  # File patterns to include
```

### Watched Files
- ✅ `app/**/*.py` - Application Python files
- ✅ `main.py` - Main application entry
- ✅ `requirements*.txt` - Dependency files

### Excluded Files/Dirs
- ❌ `frontend/` - Frontend files (handled by Vite)
- ❌ `env/` - Virtual environment
- ❌ `.git/` - Git repository
- ❌ `node_modules/` - Node.js dependencies
- ❌ `__pycache__/` - Python cache
- ❌ `.pytest_cache/` - Test cache
- ❌ `htmlcov/` - Coverage reports
- ❌ `log/`, `run/` - Runtime directories
- ❌ `rust_modules/*/target/` - Rust build artifacts

## Watchman Integration
`.watchmanconfig` provides additional optimization for file system monitoring:

```json
{
  "ignore_dirs": [
    "frontend/node_modules",
    "frontend/.svelte-kit", 
    "env",
    "__pycache__",
    ".git"
  ]
}
```

## Performance Benefits
- 🚀 Faster startup time
- 🔋 Reduced CPU usage  
- 💾 Lower memory consumption
- 🎯 Focused file monitoring
- ⚡ Fewer unnecessary reloads

## Usage
The optimization is automatically applied when running:
```bash
./BANG  # Uses optimized file watching
```

## Customization
Override default settings in `.env`:
```bash
UVICORN_WATCH_DIRS=app,custom_module
UVICORN_WATCH_INCLUDES=*.py,*.yaml,config/*.json
```
