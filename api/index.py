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

# Import from parent directory with robust error handling
import sys
import os
import importlib.util
import pathlib

# Add parent directory to path
parent_dir = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Initialize module variables
Config = None
YouTubeTranscriptFetcher = None
LLMFormatter = None

try:
    # Try direct imports first
    from config import Config
    from utils.youtube import YouTubeTranscriptFetcher
    from utils.llm import LLMFormatter
    logger.info("Successfully imported modules using direct imports")
except ImportError as e:
    logger.warning(f"Direct import failed: {e}. Trying fallback method...")
    try:
        # Fallback: Load modules using importlib
        config_spec = importlib.util.spec_from_file_location("config", parent_dir / "config.py")
        if config_spec and config_spec.loader:
            config_module = importlib.util.module_from_spec(config_spec)
            config_spec.loader.exec_module(config_module)
            Config = config_module.Config
        
        youtube_spec = importlib.util.spec_from_file_location("youtube", parent_dir / "utils" / "youtube.py")
        if youtube_spec and youtube_spec.loader:
            youtube_module = importlib.util.module_from_spec(youtube_spec)
            youtube_spec.loader.exec_module(youtube_module)
            YouTubeTranscriptFetcher = youtube_module.YouTubeTranscriptFetcher
        
        llm_spec = importlib.util.spec_from_file_location("llm", parent_dir / "utils" / "llm.py")
        if llm_spec and llm_spec.loader:
            llm_module = importlib.util.module_from_spec(llm_spec)
            llm_spec.loader.exec_module(llm_module)
            LLMFormatter = llm_module.LLMFormatter
        
        logger.info("Successfully imported modules using fallback method")
    except Exception as fallback_error:
        logger.error(f"Both import methods failed. Direct: {e}, Fallback: {fallback_error}")
        # Set dummy classes to prevent crashes
        class DummyConfig:
            @staticmethod
            def validate_config():
                return False
        class DummyFetcher:
            pass
        class DummyFormatter:
            pass
        Config = DummyConfig
        YouTubeTranscriptFetcher = DummyFetcher
        LLMFormatter = DummyFormatter

app = FastAPI(title="Verbatim AI", description="YouTube Transcription and AI Formatting Tool")

@app.on_event("startup")
async def startup_event():
    """Log startup information and check imports"""
    logger.info("Starting Verbatim AI API...")
    logger.info(f"Config available: {Config is not None}")
    logger.info(f"YouTubeTranscriptFetcher available: {YouTubeTranscriptFetcher is not None}")
    logger.info(f"LLMFormatter available: {LLMFormatter is not None}")
    if Config:
        logger.info(f"Config validation: {Config.validate_config()}")

# Initialize services lazily to avoid crashes
youtube_fetcher = None
llm_formatter = None

def get_youtube_fetcher():
    global youtube_fetcher
    if youtube_fetcher is None:
        try:
            if YouTubeTranscriptFetcher is None:
                raise HTTPException(status_code=500, detail="YouTube service not available - module import failed")
            youtube_fetcher = YouTubeTranscriptFetcher()
            logger.info("YouTube fetcher initialized successfully")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to initialize YouTube fetcher: {e}")
            raise HTTPException(status_code=500, detail=f"YouTube service initialization failed: {str(e)}")
    return youtube_fetcher

def get_llm_formatter():
    global llm_formatter
    if llm_formatter is None:
        try:
            if LLMFormatter is None:
                raise HTTPException(status_code=500, detail="LLM service not available - module import failed")
            llm_formatter = LLMFormatter()
            logger.info("LLM formatter initialized successfully")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to initialize LLM formatter: {e}")
            raise HTTPException(status_code=500, detail=f"LLM service initialization failed: {str(e)}")
    return llm_formatter

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
        # Get YouTube fetcher instance
        fetcher = get_youtube_fetcher()
        
        # Extract video ID
        video_id = fetcher.extract_video_id(request.youtube_url)
        logger.info(f"Extracted video ID: {video_id}")
        
        if not video_id:
            return TranscriptResponse(
                success=False,
                error="Invalid YouTube URL. Please provide a valid YouTube video URL."
            )
        
        # Fetch transcript
        transcript, error = fetcher.get_transcript(video_id)
        
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
        
        # Get LLM formatter instance
        formatter = get_llm_formatter()
        
        # Format transcript
        formatted_transcript, error = await formatter.format_transcript(
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
        "imports": {
            "config": Config is not None,
            "youtube_fetcher": YouTubeTranscriptFetcher is not None,
            "llm_formatter": LLMFormatter is not None
        },
        "config_valid": Config.validate_config() if Config else False,
        "environment": "vercel"
    }

@app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint for debugging"""
    return {
        "message": "API is working!",
        "timestamp": "2024-01-01",
        "environment": "vercel"
    }

# This is required for Vercel deployment
handler = app