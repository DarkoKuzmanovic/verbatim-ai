from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import from parent directory
import sys
sys.path.append('..')
from config import Config
from utils.youtube import YouTubeTranscriptFetcher
from utils.llm import LLMFormatter

app = FastAPI(title="Verbatim AI", description="YouTube Transcription and AI Formatting Tool")

# Initialize services
youtube_fetcher = YouTubeTranscriptFetcher()
llm_formatter = LLMFormatter()

# Pydantic models
class TranscriptRequest(BaseModel):
    youtube_url: str

class TranscriptResponse(BaseModel):
    success: bool
    transcript: Optional[str] = None
    error: Optional[str] = None

class FormatRequest(BaseModel):
    raw_transcript: str
    model: Optional[str] = None

class FormatResponse(BaseModel):
    success: bool
    formatted_transcript: Optional[str] = None
    error: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve a simple HTML page for Vercel"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Verbatim AI</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
            input, button { padding: 10px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 15px; background: white; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Verbatim AI</h1>
            <p>YouTube Transcription and AI Formatting Tool</p>
            
            <div>
                <h3>Get Transcript</h3>
                <input type="text" id="youtubeUrl" placeholder="Enter YouTube URL" style="width: 300px;">
                <button onclick="getTranscript()">Get Transcript</button>
                <div id="transcriptResult" class="result" style="display: none;"></div>
            </div>
            
            <div>
                <h3>Format Transcript</h3>
                <textarea id="rawTranscript" placeholder="Paste raw transcript here" rows="5" style="width: 100%; box-sizing: border-box;"></textarea><br>
                <button onclick="formatTranscript()">Format with AI</button>
                <div id="formatResult" class="result" style="display: none;"></div>
            </div>
        </div>
        
        <script>
            async function getTranscript() {
                const url = document.getElementById('youtubeUrl').value;
                const resultDiv = document.getElementById('transcriptResult');
                
                if (!url) {
                    alert('Please enter a YouTube URL');
                    return;
                }
                
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = 'Fetching transcript...';
                
                try {
                    const response = await fetch('/api/transcript', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ youtube_url: url })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        resultDiv.innerHTML = `<h4>Transcript:</h4><pre>${data.transcript}</pre>`;
                        document.getElementById('rawTranscript').value = data.transcript;
                    } else {
                        resultDiv.innerHTML = `<h4>Error:</h4><p>${data.error}</p>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<h4>Error:</h4><p>${error.message}</p>`;
                }
            }
            
            async function formatTranscript() {
                const transcript = document.getElementById('rawTranscript').value;
                const resultDiv = document.getElementById('formatResult');
                
                if (!transcript) {
                    alert('Please enter a transcript to format');
                    return;
                }
                
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = 'Formatting transcript...';
                
                try {
                    const response = await fetch('/api/format', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ raw_transcript: transcript })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        resultDiv.innerHTML = `<h4>Formatted Transcript:</h4><pre>${data.formatted_transcript}</pre>`;
                    } else {
                        resultDiv.innerHTML = `<h4>Error:</h4><p>${data.error}</p>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<h4>Error:</h4><p>${error.message}</p>`;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/transcript", response_model=TranscriptResponse)
async def get_transcript(request: TranscriptRequest):
    """Fetch transcript from YouTube video"""
    logger.info(f"Received transcript request for URL: {request.youtube_url}")
    
    try:
        # Extract video ID
        video_id = youtube_fetcher.extract_video_id(request.youtube_url)
        logger.info(f"Extracted video ID: {video_id}")
        
        if not video_id:
            return TranscriptResponse(
                success=False,
                error="Invalid YouTube URL. Please provide a valid YouTube video URL."
            )
        
        # Fetch transcript
        transcript, error = youtube_fetcher.get_transcript(video_id)
        
        if error:
            logger.error(f"Transcript fetch failed: {error}")
            return TranscriptResponse(success=False, error=error)
        
        logger.info("Transcript fetched successfully")
        return TranscriptResponse(success=True, transcript=transcript)
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return TranscriptResponse(success=False, error=error_msg)

@app.post("/api/format", response_model=FormatResponse)
async def format_transcript(request: FormatRequest):
    """Format transcript using LLM"""
    logger.info("Received format request")
    
    try:
        # Validate configuration
        if not Config.validate_config():
            return FormatResponse(
                success=False,
                error="API configuration is missing. Please check your environment variables."
            )
        
        # Check transcript length
        if len(request.raw_transcript) > Config.MAX_TRANSCRIPT_LENGTH:
            return FormatResponse(
                success=False,
                error=f"Transcript too long. Maximum length is {Config.MAX_TRANSCRIPT_LENGTH} characters."
            )
        
        # Format transcript
        formatted_transcript, error = await llm_formatter.format_transcript(
            request.raw_transcript,
            model=request.model or Config.DEFAULT_MODEL
        )
        
        if error:
            logger.error(f"Formatting failed: {error}")
            return FormatResponse(success=False, error=error)
        
        logger.info("Transcript formatted successfully")
        return FormatResponse(success=True, formatted_transcript=formatted_transcript)
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return FormatResponse(success=False, error=error_msg)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "verbatim-ai",
        "config_valid": Config.validate_config()
    }

# This is required for Vercel deployment
handler = app