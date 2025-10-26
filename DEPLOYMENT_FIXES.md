# Deployment Flexibility Guide

This document explains the issues we encountered during deployment and provides solutions to make the application work in various deployment scenarios.

---

## Issues Found During Deployment

### 1. Hardcoded Paths in Frontend

**Problem:** The frontend code assumed the app runs at root path `/`

**Files affected:**
- `static/script.js` (lines 459, 514)
- `static/index.html` (multiple lines)

**What broke:**
- API calls: `/api/transcript` → Should be `/verbatim-ai/api/transcript`
- Static files: `/static/...` → Should be `/verbatim-ai/static/...`

**Why it matters:**
When deploying at a sub-path (e.g., `app.quz.ma/verbatim-ai/`), all absolute paths starting with `/` point to the domain root, not the app root.

---

### 2. Missing Environment Configuration Files

**Problem:** No `.env.example` file in repository

**What broke:**
- `start.py` referenced `.env.example` but file didn't exist
- New users don't know what environment variables to configure
- No guidance on where to get API keys

---

### 3. Timeout Configuration Too Short

**Problem:** 30-second timeout insufficient for AI API calls

**What broke:**
- AI formatting requests timed out (504 Gateway Timeout)
- Long transcripts couldn't be processed

---

### 4. Nginx/Reverse Proxy Configuration Not Documented

**Problem:** No guidance for reverse proxy deployment

**What broke:**
- Static file routing
- API endpoint routing
- Timeout configurations

---

## Solutions for Maximum Flexibility

### Solution 1: Dynamic Base Path Detection

**Add to `static/script.js` at the top:**

```javascript
class VerbatimAI {
    constructor() {
        // Auto-detect base path from current URL
        this.basePath = this.detectBasePath();
        this.initializeElements();
        this.bindEvents();
        // ... rest of constructor
    }

    detectBasePath() {
        // Get the base path from the current page URL
        const path = window.location.pathname;

        // If we're at /verbatim-ai/, extract that
        // If we're at root /, use empty string
        const match = path.match(/^(\/[^\/]+)?\//);

        if (match && match[1]) {
            return match[1]; // Returns '/verbatim-ai' or similar
        }
        return ''; // Returns empty string for root deployment
    }

    async fetchTranscript(url) {
        // ... existing code ...
        const response = await fetch(`${this.basePath}/api/transcript`, {
            // ... rest of fetch
        });
    }

    async formatTranscript(rawTranscript) {
        // ... existing code ...
        const response = await fetch(`${this.basePath}/api/format`, {
            // ... rest of fetch
        });
    }
}
```

**Alternative: Use Configuration Variable**

Add to `static/index.html` before loading script.js:

```html
<script>
    // Set base path for API calls
    // For root deployment: window.APP_BASE_PATH = '';
    // For sub-path: window.APP_BASE_PATH = '/verbatim-ai';
    window.APP_BASE_PATH = '/verbatim-ai';
</script>
<script src="/static/script.js"></script>
```

Then in `script.js`:
```javascript
const BASE_PATH = window.APP_BASE_PATH || '';
fetch(`${BASE_PATH}/api/transcript`, ...)
```

---

### Solution 2: Use Relative Paths (Simplest)

**Change API calls to relative paths:**

```javascript
// Instead of absolute paths:
fetch('/api/transcript', ...)  // ❌ Breaks with sub-paths

// Use relative paths:
fetch('api/transcript', ...)   // ✅ Works anywhere
```

**Note:** This requires serving the HTML from the same path as the API endpoints.

---

### Solution 3: Configuration-Based Deployment

**Add to `config.py`:**

```python
class Config:
    # ... existing config ...

    # Deployment configuration
    BASE_PATH: str = os.getenv("BASE_PATH", "")  # "" for root, "/verbatim-ai" for sub-path
    BACKEND_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "240"))

    @classmethod
    def get_base_path(cls) -> str:
        """Get the base path for URL construction"""
        return cls.BASE_PATH.rstrip('/')
```

**Update `main.py`:**

```python
from config import Config

# Create app with configurable root_path
app = FastAPI(
    title="Verbatim AI",
    description="YouTube Transcription and AI Formatting Tool",
    root_path=Config.get_base_path()  # Dynamic base path
)

# Conditionally mount sub-app or use main app
if Config.BASE_PATH:
    # Sub-path deployment
    sub_app = FastAPI(title="Verbatim AI")
    # ... add routes to sub_app ...
    app.mount(Config.BASE_PATH, sub_app)
else:
    # Root deployment - add routes directly to app
    # ... add routes to app ...
```

---

### Solution 4: Add Environment Configuration Files

**Create `.env.example` in repository root:**

```bash
# OpenRouter API Configuration
# Get your API key from: https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Deployment Configuration (optional)
# BASE_PATH="" for root deployment
# BASE_PATH="/verbatim-ai" for sub-path deployment
BASE_PATH=""

# Timeout Configuration (optional)
# Increase for longer AI processing times
REQUEST_TIMEOUT=240
```

**Update `.gitignore` to include:**
```
.env
.env.local
```

**But keep `.env.example` in git:**
```bash
git add -f .env.example
```

---

### Solution 5: Improve Timeout Configuration

**Update `config.py`:**

```python
class Config:
    # ... existing config ...

    # API settings with better defaults
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "240"))  # 4 minutes default
    MAX_TRANSCRIPT_LENGTH: int = int(os.getenv("MAX_TRANSCRIPT_LENGTH", "50000"))

    # Deployment configuration
    BASE_PATH: str = os.getenv("BASE_PATH", "")
```

---

### Solution 6: Add Deployment Documentation

**Create `docs/DEPLOYMENT.md`:**

```markdown
# Deployment Guide

## Quick Start (Local Development)

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Add your OpenRouter API key to `.env`
4. Run: `python start.py`
5. Access: http://localhost:8000

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
```

---

## Recommended Implementation Priority

### High Priority (Do These First)

1. **Add `.env.example` to repository**
   - Critical for new users
   - Documents required configuration
   - Prevents confusion

2. **Increase default timeout in `config.py`**
   - Change `REQUEST_TIMEOUT: int = 30` to `REQUEST_TIMEOUT: int = 240`
   - Prevents timeouts for most use cases

3. **Add deployment documentation**
   - Create `docs/DEPLOYMENT.md` with nginx examples
   - Document common deployment scenarios

### Medium Priority (Improves Flexibility)

4. **Add BASE_PATH configuration**
   - Add `BASE_PATH` to `config.py`
   - Makes sub-path deployment configurable
   - Update `main.py` to use it

5. **Make frontend paths dynamic**
   - Add base path detection to `script.js`
   - Update API calls to use dynamic paths

### Low Priority (Nice to Have)

6. **Add deployment helper script**
   - Create `deploy.sh` with common deployment tasks
   - Automate nginx configuration generation

7. **Add configuration validation**
   - Validate BASE_PATH format
   - Check for common misconfigurations

---

## Quick Fix for Current Deployment

If you want to keep the current deployment working at `/verbatim-ai/` but make it configurable:

**1. Add to `config.py`:**
```python
BASE_PATH: str = os.getenv("BASE_PATH", "/verbatim-ai")
```

**2. Update `main.py` line 24:**
```python
app = FastAPI(
    title="Verbatim AI",
    description="YouTube Transcription and AI Formatting Tool",
    root_path=Config.BASE_PATH
)
```

**3. Add to `static/script.js` at the top:**
```javascript
// Auto-detect base path from current URL
const BASE_PATH = window.location.pathname.split('/')[1] ? '/' + window.location.pathname.split('/')[1] : '';
```

**4. Update API calls in `script.js`:**
```javascript
// Line 459:
const response = await fetch(`${BASE_PATH}/api/transcript`, {

// Line 514:
const response = await fetch(`${BASE_PATH}/api/format`, {
```

This allows users to set `BASE_PATH=""` in `.env` for root deployment or `BASE_PATH="/verbatim-ai"` for sub-path deployment.

---

## Testing Your Changes

After implementing flexibility improvements, test these scenarios:

1. **Root deployment:** Set `BASE_PATH=""`, access at `http://localhost:8000/`
2. **Sub-path deployment:** Set `BASE_PATH="/app"`, access at `http://localhost:8000/app/`
3. **Vercel deployment:** Deploy to Vercel, should work at root automatically
4. **Nginx reverse proxy:** Test with and without sub-paths

---

## Summary

The main issues were:
- ❌ Hardcoded absolute paths in frontend (`/api/...`, `/static/...`)
- ❌ No environment configuration examples (`.env.example`)
- ❌ Timeout too short for AI processing (30s → 240s)
- ❌ Missing deployment documentation

The solutions:
- ✅ Make paths configurable via `BASE_PATH` environment variable
- ✅ Add `.env.example` to repository
- ✅ Increase default timeout to 240 seconds
- ✅ Document nginx configuration requirements
- ✅ Add deployment guide for common scenarios

**Most important:** Add `.env.example` and increase timeout - these are quick wins that help all users!
