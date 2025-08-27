# Verbatim AI

A web-based tool that extracts YouTube video transcripts and formats them into clean, readable documents using AI. Easily deployable on any Linux VPS (Ubuntu/Apache).

## Features

- 🎥 Extract raw transcripts from YouTube videos
- 🤖 AI-powered formatting with summaries and key topics
- 🌐 Clean, responsive web interface with modern UI
- 📋 Copy-to-clipboard functionality
- ⚙️ Advanced settings with custom API keys and model selection
- 🎨 Dark theme with Material Design components
- 🛡️ Comprehensive error handling
- 🔧 Health check and debugging endpoints
- 💾 Local settings persistence

## Local Development Setup

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key**:

   - Copy `.env.example` to `.env`
   - Get your OpenRouter API key from [https://openrouter.ai/keys](https://openrouter.ai/keys)
   - Add your API key to `.env`:
     ```
     OPENROUTER_API_KEY=your_actual_api_key_here
     ```

3. **Run the application**:

   **Option A: Production startup (recommended)**:

   ```bash
   python start.py
   ```

   Or run directly:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

   **Option B: Development server**:

   ```bash
   python main.py
   ```

   Or using uvicorn directly:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

4. **Access the application**:
   - Production: Open your browser and go to [http://localhost:8000](http://localhost:8000)
   - Development: Open your browser and go to [http://localhost:8001](http://localhost:8001)

### Quick Deploy

### Manual Deployment

1. **Prepare for deployment**:

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy to your preferred platform**:

   - Set environment variable: `OPENROUTER_API_KEY`
   - Deploy as a standard Python web application

3. **Verify deployment**:
   - Test `/api/test` endpoint for basic functionality
   - Check `/health` endpoint for configuration status

## Usage

1. Paste a YouTube video URL into the input field
2. Click "Get Transcript" to fetch the raw transcript
3. Click "Format with AI" to process the transcript with AI
4. Use the copy buttons to copy either the raw or formatted transcript

## API Endpoints

### Main Interface

- `GET /` - Main web interface

### API Routes

- `POST /api/transcript` - Fetch YouTube transcript
  ```json
  {
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"
  }
  ```
- `POST /api/format` - Format transcript with AI
  ```json
  {
    "raw_transcript": "transcript text...",
    "model": "anthropic/claude-3.5-sonnet" // optional
  }
  ```

### Utility Endpoints

- `GET /health` - Health check and configuration status
- `GET /api/test` - Simple test endpoint for debugging

## Error Handling

The application handles various error scenarios:

- Invalid YouTube URLs
- Videos without available transcripts
- API configuration issues
- Network connectivity problems
- Rate limiting and timeouts

## Tech Stack

- **Backend**: FastAPI, Python 3.11
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **APIs**: YouTube Transcript API, OpenRouter API
- **AI Model**: Claude 3.5 Sonnet (via OpenRouter)

- **Dependencies**:
  - `fastapi>=0.104.1` - Modern web framework for building APIs
  - `uvicorn>=0.24.0` - ASGI web server for FastAPI
  - `youtube-transcript-api>=0.6.2` - YouTube transcript fetching
  - `httpx>=0.25.2` - HTTP client for API calls
  - `python-multipart>=0.0.6` - Multipart form data handling
  - `python-dotenv>=1.0.0` - Environment variable management
  - `mangum>=0.17.0` - AWS Lambda adapter for FastAPI
  - `asgiref>=3.7.2` - ASGI utilities

## Project Structure

```
├── api/
│   └── index.py          # FastAPI app entry point
├── utils/
│   ├── youtube.py         # YouTube transcript fetching
│   └── llm.py            # AI formatting logic
├── static/               # Static files (HTML, CSS, JS)
│   ├── index.html        # Main web interface
│   ├── script.js         # Frontend JavaScript
│   ├── beer-layout.css   # Custom CSS styles
│   └── icons/            # UI icons
├── logs/                 # Application logs
├── config.py             # Configuration management
├── main.py              # Development server (port 8001)
├── start.py             # Production startup script (port 8000)
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Environment Variables

| Variable                | Description                    | Required         |
| ----------------------- | ------------------------------ | ---------------- |
| `OPENROUTER_API_KEY`    | Your OpenRouter API key        | Yes              |
| `OPENROUTER_BASE_URL`   | OpenRouter API base URL        | No (has default) |
| `DEFAULT_MODEL`         | Default AI model to use        | No (has default) |
| `MAX_TRANSCRIPT_LENGTH` | Maximum transcript length      | No (has default) |
| `REQUEST_TIMEOUT`       | API request timeout in seconds | No (has default) |
