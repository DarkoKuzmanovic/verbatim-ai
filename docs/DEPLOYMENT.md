# Deployment Guide

## Quick Start (Local Development)

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Add your OpenRouter API key to `.env`
4. Run: `python start.py`
5. Access: <http://localhost:8000>

## Production Deployment Options

### Option 1: Root Path Deployment (Recommended for beginners)

Deploy at domain root (e.g., `example.com/`)

**Configuration:**

```bash
# .env
BASE_PATH=""
REQUEST_TIMEOUT=240
```

**Nginx config:**

```nginx
location / {
    proxy_pass http://localhost:8000/;
    proxy_read_timeout 300s;
}
```

### Option 2: Sub-Path Deployment

Deploy at a sub-path (e.g., `example.com/verbatim-ai/`)

**Configuration:**

```bash
# .env
BASE_PATH="/verbatim-ai"
REQUEST_TIMEOUT=240
```

**Nginx config:**

```nginx
location /verbatim-ai/ {
    proxy_pass http://localhost:8000/verbatim-ai/;
    proxy_read_timeout 300s;
}

location /static/ {
    proxy_pass http://localhost:8000/verbatim-ai/static/;
}
```

### Required Nginx Timeout Settings

For AI processing to work, add these to your nginx location block:

```nginx
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
proxy_read_timeout 300s;
```

## Automated Update Process

The [`update.sh`](../update.sh) script is the recommended way to update the production server. This script automates the deployment process and includes health checks to ensure the update was successful.

### Using the Update Script

```bash
# Make the script executable
chmod +x update.sh

# Run the update
./update.sh
```

### What the Script Does

The update script performs the following operations:

1. **Stashes local changes** - Any uncommitted changes are automatically stashed
2. **Pulls latest changes** - Fetches updates from the `origin/main` branch
3. **Updates dependencies** - If [`requirements.txt`](../requirements.txt) has changed
4. **Checks for new environment variables** - Compares [`.env.example`](../.env.example) with your current [`.env`](../.env) file
5. **Restarts the application** - Stops any running uvicorn processes and starts a new one
6. **Performs health checks** - Verifies the application is running locally and publicly accessible

### Configuration

The script is configured for the production environment at `/var/www/app.quz.ma/verbatim-ai`. You may need to update the `APP_DIR` variable in the script to match your deployment directory.

## Vercel Deployment

No changes needed - `api/index.py` handles this automatically.
