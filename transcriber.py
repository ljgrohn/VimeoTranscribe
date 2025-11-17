"""
AssemblyAI transcription module.
Handles audio transcription using AssemblyAI API.
"""

import os
import assemblyai as aai
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def setup_assemblyai() -> bool:
    """
    Set up AssemblyAI API key from environment variable or .env file.
    
    Returns:
        True if API key is set successfully, False otherwise
    """
    api_key = os.getenv('ASSEMBLYAI_API_KEY')
    
    if not api_key:
        print("Error: ASSEMBLYAI_API_KEY environment variable is not set.")
        print("Please set it using:")
        print("  Windows (PowerShell): $env:ASSEMBLYAI_API_KEY='your_key_here'")
        print("  macOS/Linux: export ASSEMBLYAI_API_KEY='your_key_here'")
        print("  Or create a .env file with: ASSEMBLYAI_API_KEY=your_key_here")
        return False
    
    aai.settings.api_key = api_key
    return True


def transcribe_audio(audio_path: str) -> Optional[str]:
    """
    Transcribe audio file using AssemblyAI.
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        Transcript text or None if transcription failed
    """
    try:
        if not os.path.exists(audio_path):
            print(f"Error: Audio file not found: {audio_path}")
            return None
        
        if not setup_assemblyai():
            return None
        
        print("Uploading audio to AssemblyAI...")
        print("Transcribing (this may take a few moments)...")
        
        # Create transcriber instance
        transcriber = aai.Transcriber()
        
        # Transcribe the audio file
        # The transcribe method handles upload, processing, and polling automatically
        transcript = transcriber.transcribe(audio_path)
        
        if transcript.status == aai.TranscriptStatus.error:
            print(f"Transcription error: {transcript.error}")
            return None
        
        if transcript.text:
            print("Transcription completed successfully!")
            return transcript.text
        else:
            print("Warning: Transcript is empty")
            return None
            
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

