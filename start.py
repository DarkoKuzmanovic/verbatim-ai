#!/usr/bin/env python3
"""
Simple startup script for Verbatim AI
"""
import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if requirements are installed"""
    try:
        import fastapi
        import uvicorn
        import httpx
        from youtube_transcript_api import YouTubeTranscriptApi
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def check_env_file():
    """Check if .env file exists"""
    if not Path(".env").exists():
        print("⚠️  No .env file found!")
        print("📋 Please copy .env.example to .env and configure your OpenRouter API key")
        print("🔑 Get your API key from: https://openrouter.ai/keys")
        return False
    return True

def main():
    print("🚀 Starting Verbatim AI...")
    
    # Check dependencies
    if not check_requirements():
        print("\n📦 Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Check environment
    if not check_env_file():
        return
    
    # Load environment variables
    if Path(".env").exists():
        from dotenv import load_dotenv
        load_dotenv()
    
    print("✅ Starting server on http://localhost:8000")
    print("📋 Open your browser and navigate to http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Start the server
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()