# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Verbatim AI** is a web-based YouTube transcription and AI formatting tool that allows users to:
1. Extract raw transcripts from YouTube videos using youtube-transcript-api
2. Format transcripts into clean, readable documents using LLM APIs (OpenRouter)

## Tech Stack

- **Frontend**: HTML5, CSS3 (Tailwind CSS), JavaScript
- **Backend**: Python with Flask or FastAPI
- **APIs**: 
  - youtube-transcript-api for transcript extraction
  - OpenRouter API for LLM-based text formatting

## Core Architecture

The application follows a simple client-server architecture:

1. **Frontend**: Single-page web interface with two main areas:
   - Left panel: Raw transcript display with copy functionality
   - Right panel: AI-formatted transcript display with copy functionality
   - Input field for YouTube URL and action buttons

2. **Backend**: Python web server that:
   - Serves the frontend static files
   - Handles YouTube URL processing and video ID extraction
   - Interfaces with youtube-transcript-api for transcript fetching
   - Manages OpenRouter API calls for transcript formatting

3. **Data Flow**:
   ```
   YouTube URL → Video ID extraction → Transcript fetch → Raw display
                                                      ↓
   User clicks "Format with AI" → OpenRouter API → Formatted display
   ```

## Key Features Implementation

### Transcript Fetching
- Use youtube-transcript-api to extract raw transcripts
- Handle multiple language availability
- Display raw transcript with proper error handling

### LLM Formatting
- Send raw transcript to OpenRouter API with predefined prompt
- Prompt structure includes:
  - Summary generation (3-5 sentences)
  - Key topics extraction (bulleted list)
  - Full transcript formatting with proper punctuation and paragraphs
  - Markdown formatting for output

### Error Handling Requirements
- Invalid YouTube URLs
- Transcript unavailability
- API connection errors
- Rate limiting and timeout handling

## Development Commands

### Setup and Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables (copy .env.example to .env and configure)
cp .env.example .env
```

### Running the Application
```bash
# Start the development server
python main.py

# Or using uvicorn directly with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Project Structure
```
verbatim-ai/
├── main.py (FastAPI application)
├── config.py (Configuration settings)
├── requirements.txt
├── utils/
│   ├── youtube.py (YouTube transcript fetching)
│   └── llm.py (OpenRouter API integration)
├── static/
│   ├── index.html (Main UI)
│   └── script.js (Frontend JavaScript)
├── .env.example (Environment configuration template)
└── README.md
```

## Future Development Notes

- The application should be designed for easy extension with features like:
  - Multiple language support
  - Different summary formats
  - Speaker diarization
  - Export functionality (txt, md files)
  - User account management

## API Integration

### YouTube Transcript API
- Use python library `youtube-transcript-api`
- Handle video ID extraction from various YouTube URL formats
- Implement fallback for when transcripts are unavailable

### OpenRouter API
- Use the predefined prompt from the PRD for consistent formatting
- Implement proper API key management and error handling
- Consider rate limiting and cost management

## UI/UX Requirements

- Clean, simple interface prioritizing usability
- Loading indicators for both transcript fetching and AI formatting
- Copy-to-clipboard functionality for both raw and formatted text
- Responsive design considerations
- Clear error messaging for various failure scenarios