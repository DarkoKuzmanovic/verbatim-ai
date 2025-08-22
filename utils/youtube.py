import re
import logging
from typing import Optional, Tuple
from youtube_transcript_api import YouTubeTranscriptApi

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeTranscriptFetcher:
    """Handle YouTube video transcript fetching"""
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract YouTube video ID from various URL formats"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def get_transcript(video_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetch transcript for a YouTube video using the correct API
        Returns: (transcript_text, error_message)
        """
        logger.info(f"Attempting to fetch transcript for video ID: {video_id}")
        
        try:
            # Create an instance of YouTubeTranscriptApi
            ytt_api = YouTubeTranscriptApi()
            
            # First, try to list available transcripts
            try:
                transcript_list = ytt_api.list(video_id)
                logger.info(f"Available transcripts for {video_id}:")
                for transcript in transcript_list:
                    logger.info(f"  - Language: {transcript.language_code} ({transcript.language}), Generated: {transcript.is_generated}")
            except Exception as list_error:
                logger.warning(f"Could not list transcripts: {str(list_error)}")
            
            # Try to fetch the transcript (prioritize English, then any available language)
            try:
                # Try English first
                fetched_transcript = ytt_api.fetch(video_id, languages=['en', 'en-US'])
            except:
                # If English not available, try any available language
                fetched_transcript = ytt_api.fetch(video_id)
            
            # Convert to raw data format
            transcript_data = fetched_transcript.to_raw_data()
            
            logger.info(f"Successfully fetched transcript with {len(transcript_data)} segments")
            
            # Format as pretty-printed string for display
            import json
            raw_transcript_str = json.dumps(transcript_data, indent=2, ensure_ascii=False)
            
            return raw_transcript_str, None
            
        except Exception as e:
            error_msg = f"Error fetching transcript for {video_id}: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            
            # Check for specific error types and provide user-friendly messages
            if "No transcripts" in str(e) or "TranscriptsDisabled" in str(e):
                return None, "No transcript found for this video. The video may not have captions available."
            elif "VideoUnavailable" in str(e) or "unavailable" in str(e).lower():
                return None, "Video is unavailable or does not exist."
            else:
                return None, f"Error fetching transcript: {str(e)}"