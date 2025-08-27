from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import os
import logging
from dotenv import load_dotenv
import sys
from pathlib import Path

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from config import Config
    from utils.youtube import YouTubeTranscriptFetcher
    from utils.llm import LLMFormatter
    logger.info("Successfully imported all modules")
except ImportError as e:
    logger.error(f"Import error: {e}")
    raise

app = FastAPI(title="Verbatim AI", description="YouTube Transcription and AI Formatting Tool")

# Create a sub-application for the /verbatim-ai path
sub_app = FastAPI(title="Verbatim AI", description="YouTube Transcription and AI Formatting Tool")

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
    api_key: Optional[str] = None

class FormatResponse(BaseModel):
    success: bool
    formatted_transcript: Optional[str] = None
    error: Optional[str] = None

@sub_app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the web interface"""
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
                        resultDiv.innerHTML = `<h4>Transcript:</h4><pre style="max-height: 300px; overflow-y: auto; white-space: pre-wrap;">${data.transcript}</pre>`;
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
                        resultDiv.innerHTML = `<h4>Formatted Transcript:</h4><pre style="max-height: 400px; overflow-y: auto; white-space: pre-wrap;">${data.formatted_transcript}</pre>`;
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

@sub_app.post("/api/transcript", response_model=TranscriptResponse)
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

@sub_app.post("/api/format", response_model=FormatResponse)
async def format_transcript(request: FormatRequest):
    """Format transcript using LLM"""
    logger.info("Received format request")
    
    try:
        # Validate configuration (either env or provided API key)
        if not Config.validate_config() and not request.api_key:
            return FormatResponse(
                success=False,
                error="No API key available. Please configure OPENROUTER_API_KEY or provide API key in settings."
            )
        
        # Check transcript length
        if len(request.raw_transcript) > Config.MAX_TRANSCRIPT_LENGTH:
            return FormatResponse(
                success=False,
                error=f"Transcript too long. Maximum length is {Config.MAX_TRANSCRIPT_LENGTH} characters."
            )
        
        # Create a new formatter instance if API key is provided
        if request.api_key:
            from utils.llm import LLMFormatter
            custom_formatter = LLMFormatter()
            custom_formatter.api_key = request.api_key
            if request.model:
                custom_formatter.model = request.model
            formatted_transcript, error = await custom_formatter.format_transcript(request.raw_transcript)
        else:
            # Use the default formatter
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

@sub_app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "verbatim-ai",
        "config_valid": Config.validate_config()
    }

@sub_app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {
        "message": "API is working!"
    }

# Mount the sub-application at /verbatim-ai path
app.mount("/verbatim-ai", sub_app)

# Redirect root to /verbatim-ai
@app.get("/")
async def redirect_to_verbatim():
    """Redirect root to verbatim-ai application"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/verbatim-ai/", status_code=301)

