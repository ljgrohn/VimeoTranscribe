"""
Main CLI application for Wistia video transcription.
"""

import os
import sys
from wistia_extractor import extract_and_download
from audio_processor import extract_audio, cleanup_files
from transcriber import transcribe_audio


def save_transcript(transcript: str, video_id: str) -> str:
    """
    Save transcript to a text file.
    
    Args:
        transcript: The transcript text
        video_id: Video ID for filename
        
    Returns:
        Path to saved transcript file
    """
    filename = f"transcript_{video_id}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(transcript)
        return filename
    except Exception as e:
        print(f"Error saving transcript: {e}")
        return ""


def main():
    """Main entry point for the CLI application."""
    print("=" * 60)
    print("Wistia Video Transcription Tool")
    print("=" * 60)
    print()
    
    # Get Wistia URL or video ID from user
    while True:
        video_input = input("Enter Wistia URL or video ID: ").strip()
        
        if not video_input:
            print("Please enter a valid Wistia URL or video ID.")
            continue
        
        break
    
    print()
    print("-" * 60)
    
    # Step 1: Extract video ID and download video
    video_id, video_path = extract_and_download(video_input)
    
    if not video_id or not video_path:
        print("\nFailed to download video. Exiting.")
        sys.exit(1)
    
    print("-" * 60)
    
    # Step 2: Extract audio from video
    audio_path = extract_audio(video_path, video_id)
    
    if not audio_path:
        cleanup_files(video_path)
        print("\nFailed to extract audio. Exiting.")
        sys.exit(1)
    
    print("-" * 60)
    
    # Step 3: Transcribe audio
    transcript = transcribe_audio(audio_path)
    
    # Clean up temporary files
    cleanup_files(video_path, audio_path)
    
    if not transcript:
        print("\nFailed to transcribe audio. Exiting.")
        sys.exit(1)
    
    print("-" * 60)
    print()
    
    # Step 4: Display and save transcript
    print("=" * 60)
    print("TRANSCRIPT")
    print("=" * 60)
    print()
    print(transcript)
    print()
    print("=" * 60)
    print()
    
    # Save transcript to file
    transcript_file = save_transcript(transcript, video_id)
    
    if transcript_file:
        print(f"Transcript saved to: {transcript_file}")
    else:
        print("Warning: Could not save transcript to file.")
    
    print()
    print("Done!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

