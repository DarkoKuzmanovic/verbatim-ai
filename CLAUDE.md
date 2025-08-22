# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Verbatim AI** is a web-based YouTube transcription and AI formatting tool built with FastAPI and designed for serverless deployment on Vercel. The application extracts YouTube video transcripts and formats them into clean, readable documents using AI.

## Development Commands

### Quick Start

```bash
# Install dependencies and run with one command
python start.py

# Manual setup
pip install -r requirements.txt
cp .env.example .env  # Configure OPENROUTER_API_KEY
python main.py
```

### Local Development

```bash
# Start development server with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Test Vercel-compatible version locally
cd api && python -c "from index import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"
```

### Deployment

```bash
# Deploy to Vercel
vercel --prod

# Test endpoints after deployment
curl https://your-app.vercel.app/health
curl https://your-app.vercel.app/api/test
```

## Architecture Overview

### Dual-Application Structure

The project maintains two FastAPI applications for different deployment scenarios:

1. **`main.py`**: Local development server with static file serving
2. **`api/index.py`**: Vercel-optimized serverless handler with embedded HTML

### Core Components

- **`config.py`**: Centralized configuration with environment variable management
- **`utils/youtube.py`**: YouTube video ID extraction and transcript fetching using youtube-transcript-api
- **`utils/llm.py`**: OpenRouter API integration with chunking support for long transcripts
- **`start.py`**: Development convenience script with dependency checking

### Key Design Patterns

**Lazy Initialization**: Services are initialized on-demand in the Vercel handler to avoid startup issues in serverless environments.

**Robust Import Handling**: The Vercel handler includes fallback import mechanisms using `importlib.util` to handle serverless deployment constraints.

**Chunking Strategy**: Long transcripts are automatically split into manageable chunks (40,000 characters) for LLM processing, preserving JSON structure.

## API Endpoints

### Main Routes

- `GET /` - Serves the web interface (embedded HTML in Vercel version)
- `POST /api/transcript` - Fetches YouTube transcript from URL
- `POST /api/format` - Formats transcript using AI (Claude 3.5 Sonnet via OpenRouter)

### Utility Routes

- `GET /health` - Health check with configuration validation
- `GET /api/test` - Simple test endpoint for debugging deployments

## Configuration

### Required Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)

### Optional Configuration (in config.py)

- `DEFAULT_MODEL`: AI model selection (default: "anthropic/claude-3.5-sonnet")
- `MAX_TRANSCRIPT_LENGTH`: Maximum transcript length (default: 50,000 chars)
- `REQUEST_TIMEOUT`: API request timeout (default: 30 seconds)

## Key Implementation Details

### YouTube Transcript Processing

The application extracts video IDs from various YouTube URL formats and fetches transcripts as JSON data with timing information. The raw transcript is returned as pretty-printed JSON for display.

### AI Formatting Strategy

Transcripts are formatted using a specialized prompt that:

- Extracts text content from JSON segments
- Adds proper punctuation and capitalization
- Creates logical paragraph breaks
- Maintains the speaker's natural voice and style

### Error Handling

Comprehensive error handling covers:

- Invalid YouTube URLs and video ID extraction failures
- Missing or disabled transcripts
- API configuration and connection issues
- Chunking failures and partial processing errors

## Deployment Architecture

### Ubuntu/Apache Configuration

- **Runtime**: Python 3.11+
- **App Server**: Gunicorn with Uvicorn workers
- **Reverse Proxy**: Apache with mod_proxy and mod_proxy_http
- **Static Files**: Served via Apache Alias from `/static/` directory
- **Entrypoint**: `main.py` for local, `api/index.py` for production

### Local vs Production Differences

- Local version serves static files from `/static/` directory
- Production version uses Apache for reverse proxy and static file serving
- Both versions share the same core API functionality through shared utils

## Development Workflow

When making changes:

1. Test locally using `python main.py` or `python start.py`
2. Test Vercel compatibility using the local Vercel test command
3. Verify environment variable configuration with `/health` endpoint
4. Deploy to Vercel and test all API endpoints
