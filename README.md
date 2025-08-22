# Verbatim AI

A web-based tool that extracts YouTube video transcripts and formats them into clean, readable documents using AI.

## Features

- Extract raw transcripts from YouTube videos
- AI-powered formatting with summaries and key topics
- Clean, responsive web interface
- Copy-to-clipboard functionality
- Comprehensive error handling

## Setup

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
   ```bash
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the application**:
   Open your browser and go to [http://localhost:8000](http://localhost:8000)

## Usage

1. Paste a YouTube video URL into the input field
2. Click "Get Transcript" to fetch the raw transcript
3. Click "Format with AI" to process the transcript with AI
4. Use the copy buttons to copy either the raw or formatted transcript

## API Endpoints

- `GET /` - Main web interface
- `POST /api/transcript` - Fetch YouTube transcript
- `POST /api/format` - Format transcript with AI
- `GET /health` - Health check

## Error Handling

The application handles various error scenarios:
- Invalid YouTube URLs
- Videos without available transcripts
- API configuration issues
- Network connectivity problems
- Rate limiting and timeouts

## Tech Stack

- **Backend**: FastAPI, Python
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **APIs**: YouTube Transcript API, OpenRouter API
- **AI Model**: Claude 3.5 Sonnet (via OpenRouter)