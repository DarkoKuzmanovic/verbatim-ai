import httpx
import json
import logging
from typing import Optional, Tuple, List
from config import Config

logger = logging.getLogger(__name__)

class LLMFormatter:
    """Handle LLM-based transcript formatting using OpenRouter API"""
    
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = Config.OPENROUTER_BASE_URL
        self.model = Config.DEFAULT_MODEL
        
    def _get_formatting_prompt(self, raw_transcript: str) -> str:
        """Generate the formatting prompt with the raw transcript"""
        return f"""You are an expert in text formatting. Your task is to take the raw transcript data below (which contains timing information and text segments) and transform it into clean, readable, and well-formatted text.

**CRITICAL: You must format ALL the provided text completely. Do not stop partway through. Do not ask if you should continue. Process the entire transcript data provided.**

**Instructions:**

1. **Extract Text Only:** From the JSON data provided, extract only the "text" content from each segment, ignoring the timing information.
2. **Add Punctuation and Capitalization:** Add proper punctuation (periods, commas, question marks, exclamation marks) and capitalize the beginning of sentences and proper nouns.
3. **Create Natural Flow:** Combine the text segments into natural, flowing sentences and paragraphs.
4. **Create Logical Paragraphs:** Break the text into logical paragraphs based on topic changes or natural breaks in conversation.
5. **Fix Grammar:** Correct any obvious grammatical errors while preserving the speaker's voice and style.
6. **Complete Processing:** Format ALL segments in the provided data. Do not stop until you have processed every single text segment.
7. **No Meta-Commentary:** Do not include any notes about continuing, asking for permission, or explaining what you're doing. Just provide the formatted text.

**Raw Transcript Data:**

{raw_transcript}

**Output Requirements:** 
- Process every single text segment from the JSON data
- Provide only the clean, formatted text with proper punctuation, capitalization, and paragraph breaks
- Do not include headings, summaries, bullet points, or any meta-commentary
- Complete the entire formatting task in this response
"""
    
    def _split_transcript_into_chunks(self, raw_transcript: str, max_chunk_size: int = 40000) -> List[str]:
        """
        Split the raw transcript JSON into manageable chunks while preserving JSON structure
        """
        try:
            # Parse the JSON to get the transcript segments
            transcript_data = json.loads(raw_transcript)
            
            chunks = []
            current_chunk = []
            current_size = 0
            
            for segment in transcript_data:
                segment_json = json.dumps(segment, ensure_ascii=False)
                segment_size = len(segment_json)
                
                # If adding this segment would exceed the limit, save current chunk and start new one
                if current_size + segment_size > max_chunk_size and current_chunk:
                    chunk_json = json.dumps(current_chunk, indent=2, ensure_ascii=False)
                    chunks.append(chunk_json)
                    current_chunk = []
                    current_size = 0
                
                current_chunk.append(segment)
                current_size += segment_size
            
            # Add the last chunk if it has content
            if current_chunk:
                chunk_json = json.dumps(current_chunk, indent=2, ensure_ascii=False)
                chunks.append(chunk_json)
            
            logger.info(f"Split transcript into {len(chunks)} chunks")
            return chunks
            
        except json.JSONDecodeError:
            # If it's not valid JSON, split by character count
            logger.warning("Raw transcript is not valid JSON, falling back to character-based splitting")
            chunks = []
            for i in range(0, len(raw_transcript), max_chunk_size):
                chunks.append(raw_transcript[i:i + max_chunk_size])
            return chunks

    def _get_chunk_formatting_prompt(self, chunk_transcript: str, chunk_number: int, total_chunks: int) -> str:
        """Generate the formatting prompt for a specific chunk"""
        chunk_info = f"(Chunk {chunk_number} of {total_chunks})" if total_chunks > 1 else ""
        
        return f"""You are an expert in text formatting. Your task is to take the raw transcript data below and transform it into clean, readable, and well-formatted text.

**CRITICAL: You must format ALL the provided text in this chunk completely. Do not stop partway through. Do not ask if you should continue. Process every single text segment in this chunk.**

**Instructions:**

1. **Extract Text Only:** From the JSON data provided, extract only the "text" content from each segment, ignoring the timing information.
2. **Add Punctuation and Capitalization:** Add proper punctuation (periods, commas, question marks, exclamation marks) and capitalize the beginning of sentences and proper nouns.
3. **Create Natural Flow:** Combine the text segments into natural, flowing sentences and paragraphs.
4. **Create Logical Paragraphs:** Break the text into logical paragraphs based on topic changes or natural breaks in conversation.
5. **Fix Grammar:** Correct any obvious grammatical errors while preserving the speaker's voice and style.
6. **Complete Processing:** Format ALL segments in this chunk. Do not stop until you have processed every single text segment.
7. **Chunk Processing:** This is {chunk_info}. Format this chunk as if it's a continuous part of a larger transcript. Do not add introductions or conclusions specific to this chunk.
8. **No Meta-Commentary:** Do not include any notes about continuing, asking for permission, or explaining what you're doing. Just provide the formatted text.

**Raw Transcript Data {chunk_info}:**

{chunk_transcript}

**Output Requirements:** 
- Process every single text segment from this chunk's JSON data
- Provide only the clean, formatted text with proper punctuation, capitalization, and paragraph breaks
- Do not include headings, summaries, bullet points, or any meta-commentary
- Complete the entire chunk formatting task in this response
- Do not ask to continue or provide partial results
"""

    async def _format_single_chunk(self, chunk: str, chunk_number: int, total_chunks: int) -> Tuple[Optional[str], Optional[str]]:
        """Format a single chunk of transcript"""
        try:
            prompt = self._get_chunk_formatting_prompt(chunk, chunk_number, total_chunks)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "Verbatim AI"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 4000,
                        "temperature": 0.3
                    },
                    timeout=Config.REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    formatted_text = result["choices"][0]["message"]["content"]
                    return formatted_text, None
                else:
                    error_detail = response.text
                    return None, f"API error ({response.status_code}): {error_detail}"
                    
        except httpx.TimeoutException:
            return None, f"Request timed out for chunk {chunk_number}."
        except Exception as e:
            return None, f"Error formatting chunk {chunk_number}: {str(e)}"

    async def format_transcript(self, raw_transcript: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Format transcript using OpenRouter API with chunking support for long transcripts
        Returns: (formatted_text, error_message)
        """
        if not self.api_key:
            return None, "OpenRouter API key not configured"
        
        try:
            # Check if we need to split the transcript
            if len(raw_transcript) <= Config.MAX_TRANSCRIPT_LENGTH:
                # Process as single chunk
                logger.info("Processing transcript as single chunk")
                prompt = self._get_formatting_prompt(raw_transcript)
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "http://localhost:8000",
                            "X-Title": "Verbatim AI"
                        },
                        json={
                            "model": self.model,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            "max_tokens": 4000,
                            "temperature": 0.3
                        },
                        timeout=Config.REQUEST_TIMEOUT
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        formatted_text = result["choices"][0]["message"]["content"]
                        return formatted_text, None
                    else:
                        error_detail = response.text
                        return None, f"API error ({response.status_code}): {error_detail}"
            else:
                # Process in chunks
                logger.info(f"Transcript too long ({len(raw_transcript)} chars), splitting into chunks")
                chunks = self._split_transcript_into_chunks(raw_transcript)
                formatted_chunks = []
                
                for i, chunk in enumerate(chunks, 1):
                    logger.info(f"Processing chunk {i} of {len(chunks)}")
                    formatted_chunk, error = await self._format_single_chunk(chunk, i, len(chunks))
                    
                    if error:
                        return None, f"Error processing chunk {i}: {error}"
                    
                    formatted_chunks.append(formatted_chunk)
                
                # Combine all formatted chunks
                combined_result = "\n\n".join(formatted_chunks)
                logger.info(f"Successfully processed all {len(chunks)} chunks")
                return combined_result, None
                
        except httpx.TimeoutException:
            return None, "Request timed out. Please try again."
        except Exception as e:
            return None, f"Error formatting transcript: {str(e)}"