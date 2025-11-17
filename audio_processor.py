"""
Audio processing module.
Handles audio extraction from video files using ffmpeg.
"""

import os
import tempfile
import ffmpeg
from typing import Optional


def extract_audio(video_path: str, video_id: str) -> Optional[str]:
    """
    Extract audio from video file and convert to WAV format.
    
    Args:
        video_path: Path to the video file
        video_id: Video ID for naming the output file
        
    Returns:
        Path to extracted audio file or None if extraction failed
    """
    try:
        if not os.path.exists(video_path):
            print(f"Error: Video file not found: {video_path}")
            return None
        
        print("Extracting audio from video...")
        
        # Create temporary audio file
        temp_dir = tempfile.gettempdir()
        audio_path = os.path.join(temp_dir, f"wistia_{video_id}_audio.wav")
        
        # Use ffmpeg to extract audio
        # Convert to WAV format (uncompressed, widely supported)
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(stream, audio_path, acodec='pcm_s16le', ac=1, ar='16000')
        
        # Suppress ffmpeg output unless there's an error
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path) / (1024 * 1024)  # Size in MB
            print(f"Audio extracted successfully: {audio_path} ({file_size:.2f} MB)")
            return audio_path
        else:
            print("Error: Audio file was not created")
            return None
            
    except ffmpeg.Error as e:
        print(f"Error extracting audio with ffmpeg: {e.stderr.decode() if e.stderr else str(e)}")
        print("\nMake sure ffmpeg is installed and available in your PATH.")
        return None
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None


def cleanup_files(*file_paths: str) -> None:
    """
    Clean up temporary files.
    
    Args:
        *file_paths: Variable number of file paths to delete
    """
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up: {file_path}")
        except Exception as e:
            print(f"Warning: Could not delete {file_path}: {e}")

