# Development Guide - Docker File Watching & Live Debugging

## Overview

Your Docker setup supports multiple approaches to live debugging and file watching. Here are the available options and how to use them.

## Current Setup Analysis

✅ **Already Configured:**

- Multi-stage Dockerfile with development target
- Uvicorn with `--reload` flag for hot reloading
- Volume mounts for live code changes
- `watchfiles` dependency installed

## Method 1: Docker Compose Watch (Recommended)

Docker Compose Watch is the modern, official solution for file watching in Docker development environments.

### Features Added:

- **sync+restart**: Syncs files and restarts the container when Python files change
- **rebuild**: Rebuilds the image when requirements.txt changes
- **Automatic ignore**: Ignores cache files and temporary files

### Usage:

```bash
# Start with file watching
docker compose --profile dev watch

# Alternative: Start then watch in separate terminal
docker compose --profile dev up -d
docker compose watch
```

### Watch Actions Configured:

1. **Python source files** (`./app` → `/app/app`):
   - Action: `sync+restart`
   - Triggers container restart when .py files change
   - Ignores `__pycache__`, `*.pyc`, `*.pyo`

2. **Environment file** (`.env` → `/app/.env`):
   - Action: `sync+restart`
   - Restarts when environment changes

3. **Requirements** (`requirements.txt`):
   - Action: `rebuild`
   - Rebuilds entire image when dependencies change

## Method 2: Standard Volume Mounts (Current Default)

Your existing setup uses volume mounts with uvicorn's built-in reload:

```bash
# Standard approach with volume mounts
docker compose --profile dev up
```

**How it works:**

- Volume mount: `.:/app:cached`
- Uvicorn flag: `--reload`
- Watches: `/app` directory
- Auto-reloads: When Python files change

## Method 3: Advanced Debugging with VS Code

For IDE debugging, you can also set up remote debugging:

### Dockerfile Enhancement for Debugging:

```dockerfile
# Add to development stage
RUN pip install debugpy

# Debug command
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8500", "--reload"]
```

### VS Code Launch Configuration:

```json
{
  "name": "Python: Remote Attach",
  "type": "python",
  "request": "attach",
  "connect": {
    "host": "localhost",
    "port": 5678
  },
  "pathMappings": [
    {
      "localRoot": "${workspaceFolder}",
      "remoteRoot": "/app"
    }
  ]
}
```

## File Watching Performance Tips

1. **Use .dockerignore**: Already configured to exclude:
   - `__pycache__/`, `*.pyc`, `*.pyo`
   - IDE files (`.vscode/`, `.idea/`)
   - OS files (`.DS_Store`, `Thumbs.db`)

2. **Volume Mount Optimization**:
   - Uses `:cached` flag for better performance on macOS/Windows
   - Linux has optimal performance by default

3. **Watch Scope**:
   - Docker Compose Watch only watches specified paths
   - Uvicorn reload watches entire `/app` directory

## Debugging Your Current Setup

### Verify File Watching is Active:

```bash
# Check container logs for reload messages
docker compose --profile dev logs -f mcp-api

# Expected output:
# INFO: Will watch for changes in these directories: ['/app']
# INFO: Started reloader process [1] using WatchFiles
```

### Test Live Reload:

1. Start the service:

   ```bash
   docker compose --profile dev watch
   ```

2. Edit a Python file in `./app/`

3. Watch logs - should see:
   ```
   INFO: Detected file changes, reloading...
   ```

### Common Issues & Solutions:

**Issue**: Files not syncing

- **Solution**: Check volume mounts and file permissions
- **Command**: `docker compose exec mcp-api ls -la /app`

**Issue**: Slow reload on Windows/macOS

- **Solution**: Ensure Docker Desktop uses WSL2 (Windows) or proper file sharing (macOS)

**Issue**: Container keeps restarting

- **Solution**: Check for syntax errors in Python files

## Performance Comparison

| Method           | Reload Speed | Resource Usage | Debug Support |
| ---------------- | ------------ | -------------- | ------------- |
| Compose Watch    | Fast         | Low            | Good          |
| Volume + uvicorn | Very Fast    | Low            | Excellent     |
| Remote Debug     | Medium       | Medium         | Best          |

## Recommended Workflow

1. **Daily Development**: Use `docker compose --profile dev watch`
2. **Debugging Sessions**: Add remote debugger setup
3. **Testing**: Use standard `docker compose --profile dev up`

## Environment Variables

Key variables for development:

```bash
# .env file
DOCKER_TARGET=development  # Use development stage
MCP_PORT=8500             # API port
HOST_PORT=8500            # Host port mapping
DEBUG=true                # Enable debug mode
```

## Next Steps

1. Try the new `docker compose --profile dev watch` command
2. Test file changes with live reload
3. Consider adding remote debugging if needed
4. Monitor performance and adjust watch patterns as needed

This setup provides excellent developer experience with minimal overhead!
