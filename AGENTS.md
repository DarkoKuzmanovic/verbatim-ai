# AGENTS.md

This file contains essential information for coding agents working with the Verbatim AI project. It complements the README.md by providing technical details, build steps, and conventions specifically for AI agents.

## Project Overview

Verbatim AI is a FastAPI-based web application that extracts YouTube transcripts and formats them using AI. The application consists of a Python backend with vanilla HTML/CSS/JavaScript frontend.

## Development Setup

### Prerequisites

- Python 3.11+
- OpenRouter API key (required for AI formatting)

### Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY

# Run development server
python main.py
# Or: uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Run production server
python start.py
# Or: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Project Architecture

### Core Components

1. **FastAPI Application** (`main.py`)
   - Main application entry point
   - API endpoints for transcript fetching and formatting
   - Development server runs on port 8001
   - Production server runs on port 8000

2. **Configuration** (`config.py`)
   - Uses Pydantic Settings for environment variable management
   - Validates BASE_PATH format (must start with "/" if not empty, cannot end with "/")
   - Handles OpenRouter API configuration

3. **YouTube Integration** (`utils/youtube.py`)
   - `YouTubeTranscriptFetcher` class handles video ID extraction and transcript fetching
   - Supports multiple YouTube URL formats
   - Prioritizes English transcripts, falls back to any available language
   - Returns JSON-formatted transcript data

4. **LLM Integration** (`utils/llm.py`)
   - `LLMFormatter` class handles AI-powered transcript formatting
   - Supports chunking for long transcripts (splits at 40,000 characters)
   - Uses OpenRouter API with configurable models
   - Default model: `anthropic/claude-3.5-sonnet`

5. **Startup Script** (`start.py`)
   - Production startup script with dependency checking
   - Automatically installs missing dependencies
   - Validates .env file existence
   - Provides user-friendly startup messages

### API Endpoints

- `GET /` - Serves main HTML interface
- `POST /api/transcript` - Fetches YouTube transcript
- `POST /api/format` - Formats transcript with AI
- `GET /health` - Health check endpoint
- `GET /api/test` - Debugging endpoint

### Request/Response Models

```python
class TranscriptRequest(BaseModel):
    youtube_url: str

class FormatRequest(BaseModel):
    raw_transcript: str
    model: Optional[str] = None
    api_key: Optional[str] = None
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key | None | Yes |
| `BASE_PATH` | Deployment sub-path | "" | No |
| `OPENROUTER_BASE_URL` | API base URL | "<https://openrouter.ai/api/v1>" | No |
| `DEFAULT_MODEL` | AI model to use | "anthropic/claude-3.5-sonnet" | No |
| `MAX_TRANSCRIPT_LENGTH` | Max transcript length before chunking | 50000 | No |
| `REQUEST_TIMEOUT` | API request timeout (seconds) | 240 | No |

## File Structure Conventions

```tree
verbatim-ai/
├── api/
│   └── index.py          # Vercel deployment entry point
├── docs/
│   └── DEPLOYMENT.md     # Deployment documentation
├── utils/
│   ├── __init__.py       # Package initialization
│   ├── youtube.py        # YouTube transcript functionality
│   └── llm.py            # LLM formatting functionality
├── static/
│   ├── index.html        # Main frontend
│   ├── script.js         # Frontend JavaScript
│   ├── beer-layout.css   # Custom CSS
│   └── icons/            # UI icons
├── config.py             # Configuration management
├── main.py               # Development server
├── start.py              # Production startup script
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── deploy.sh             # Nginx config generator
└── update.sh             # Production update script
```

## Coding Conventions

### Python

- Use FastAPI for all API endpoints
- Use Pydantic models for request/response validation
- Implement comprehensive error handling with try/catch blocks
- Use async/await for I/O operations
- Follow PEP 8 style guidelines
- Use type hints for all function signatures

### Error Handling

- All API endpoints should return appropriate error responses
- Use structured error messages with user-friendly descriptions
- Log errors with appropriate severity levels
- Handle YouTube API errors specifically (no transcript, video unavailable, etc.)

### Logging

- Use Python's logging module
- Set appropriate log levels (INFO, WARNING, ERROR)
- Include context in log messages (video IDs, error types, etc.)

## Testing

### Manual Testing

1. Test transcript fetching with various YouTube URL formats
2. Test AI formatting with different transcript lengths
3. Test error scenarios (invalid URLs, missing transcripts, API failures)
4. Test both development and production startup scripts

### Health Check

Access `/health` endpoint to verify:

- Application status
- OpenRouter API configuration

## Deployment

### Development

- Use `python main.py` for development server (port 8001)
- Enable auto-reload with `--reload` flag

### Production

- Use `python start.py` for production server (port 8000)
- Ensure all environment variables are set
- Use `update.sh` for automated updates in production

### Nginx Configuration

- Use `deploy.sh` to generate appropriate Nginx configuration
- Ensure proxy timeouts are set to 300s for long AI processing
- Configure BASE_PATH appropriately for sub-path deployments

## Common Issues and Solutions

### YouTube Transcript Issues

- Some videos may not have transcripts available
- Private videos or age-restricted content may be inaccessible
- Try different language codes if English transcript fails

### AI Formatting Issues

- Long transcripts are automatically chunked at 40,000 characters
- Increase `REQUEST_TIMEOUT` for very long transcripts
- Verify OpenRouter API key is valid and has sufficient credits

### Deployment Issues

- Ensure BASE_PATH is correctly formatted (starts with "/", doesn't end with "/")
- Check Nginx proxy timeouts for long-running AI requests
- Verify all dependencies are installed in production

## Dependencies

Key dependencies and their purposes:

- `fastapi>=0.104.1` - Web framework
- `uvicorn>=0.24.0` - ASGI server
- `youtube-transcript-api>=0.6.2` - YouTube transcript fetching
- `httpx>=0.25.2` - HTTP client for API calls
- `pydantic>=2.3.0` - Data validation
- `pydantic-settings` - Environment variable management
- `python-dotenv>=1.0.0` - .env file support
- `mangum>=0.17.0` - AWS Lambda adapter (for Vercel deployment)

## Security Considerations

- API keys should never be exposed in client-side code
- Validate all user inputs, especially YouTube URLs
- Implement rate limiting for API endpoints in production
- Use HTTPS in production deployments
- Sanitize transcript data before processing with AI

## Performance Optimization

- Transcript chunking for long content (>50,000 characters)
- Async operations for all I/O bound tasks
- Connection pooling for HTTP requests
- Consider caching for frequently accessed transcripts
- Optimize Nginx configuration for proxy timeouts
