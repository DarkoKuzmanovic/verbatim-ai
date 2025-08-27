from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
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

from config import Config
from utils.youtube import YouTubeTranscriptFetcher
from utils.llm import LLMFormatter

app = FastAPI(title="Verbatim AI", description="YouTube Transcription and AI Formatting Tool")

# Create a sub-application for the /verbatim-ai path
sub_app = FastAPI(title="Verbatim AI", description="YouTube Transcription and AI Formatting Tool")

# Mount static files on sub-app
sub_app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
youtube_fetcher = YouTubeTranscriptFetcher()
llm_formatter = LLMFormatter()

# Pydantic models for request/response
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
    """Serve the main HTML page"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Static files not found</h1>", status_code=404)

@sub_app.post("/api/transcript", response_model=TranscriptResponse)
async def get_transcript(request: TranscriptRequest):
    """Fetch transcript from YouTube video"""
    logger.info(f"Received transcript request for URL: {request.youtube_url}")
    
    try:
        # Extract video ID
        video_id = youtube_fetcher.extract_video_id(request.youtube_url)
        logger.info(f"Extracted video ID: {video_id}")
        
        if not video_id:
            logger.warning(f"Could not extract video ID from URL: {request.youtube_url}")
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
        error_msg = f"Unexpected error in get_transcript: {type(e).__name__}: {str(e)}"
        logger.error(error_msg)
        return TranscriptResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

@sub_app.post("/api/format", response_model=FormatResponse)
async def format_transcript(request: FormatRequest):
    """Format transcript using LLM"""
    try:
        # Check if API key is configured (either in env or provided in request)
        if not Config.validate_config() and not request.api_key:
            return FormatResponse(
                success=False,
                error="No API key available. Please configure OPENROUTER_API_KEY or provide API key in settings."
            )
        
        # Create a new formatter instance if API key is provided
        if request.api_key:
            from utils.llm import LLMFormatter
            custom_formatter = LLMFormatter()
            custom_formatter.api_key = request.api_key
            if request.model:
                custom_formatter.model = request.model
                logger.info(f"Using custom model with custom API key: {request.model}")
            formatted_text, error = await custom_formatter.format_transcript(request.raw_transcript)
        else:
            # Use the default formatter
            if request.model:
                llm_formatter.model = request.model
                logger.info(f"Using custom model: {request.model}")
            formatted_text, error = await llm_formatter.format_transcript(request.raw_transcript)
        
        if error:
            return FormatResponse(success=False, error=error)
        
        return FormatResponse(success=True, formatted_transcript=formatted_text)
        
    except Exception as e:
        return FormatResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

@sub_app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "openrouter_configured": Config.validate_config()
    }

# Mount the sub-application at /verbatim-ai path
app.mount("/verbatim-ai", sub_app)

# Redirect root to /verbatim-ai
@app.get("/")
async def redirect_to_verbatim():
    """Redirect root to verbatim-ai application"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/verbatim-ai/", status_code=301)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)