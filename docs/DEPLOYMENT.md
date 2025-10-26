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

## Vercel Deployment

No changes needed - `api/index.py` handles this automatically.
