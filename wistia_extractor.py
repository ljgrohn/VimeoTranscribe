"""
Video extraction module.
Handles parsing Vimeo/Wistia URLs/IDs and downloading video files.
"""

import re
import requests
import tempfile
import os
import yt_dlp
from typing import Optional, Tuple


def extract_video_id(url_or_id: str) -> Optional[str]:
    """
    Extract video ID from URL or return the ID if already provided.
    Supports both Vimeo and Wistia URLs.
    
    Args:
        url_or_id: Video URL or video ID
        
    Returns:
        Video ID string or None if invalid
    """
    # If it's already just an ID (alphanumeric)
    if re.match(r'^[a-z0-9]{8,}$', url_or_id.lower()):
        return url_or_id.lower()
    
    # Extract from Vimeo URL patterns
    vimeo_patterns = [
        r'vimeo\.com/(\d+)',  # https://vimeo.com/123456789
        r'vimeo\.com/(\d+)/([a-z0-9]+)',  # https://vimeo.com/123456789/abc123def
        r'player\.vimeo\.com/video/(\d+)',  # https://player.vimeo.com/video/123456789
    ]
    
    for pattern in vimeo_patterns:
        match = re.search(pattern, url_or_id.lower())
        if match:
            # For Vimeo URLs with hash, use the numeric ID
            return match.group(1)
    
    # Extract from Wistia URL patterns
    wistia_patterns = [
        r'wistia\.com/medias/([a-z0-9]+)',
        r'wi\.st/([a-z0-9]+)',
        r'wistia\.net/embed/([a-z0-9]+)',
        r'medias/([a-z0-9]+)',
    ]
    
    for pattern in wistia_patterns:
        match = re.search(pattern, url_or_id.lower())
        if match:
            return match.group(1)
    
    return None


def is_vimeo_url(url_or_id: str) -> bool:
    """
    Check if the input is a Vimeo URL or ID.
    
    Args:
        url_or_id: Video URL or ID
        
    Returns:
        True if Vimeo, False otherwise
    """
    return 'vimeo.com' in url_or_id.lower() or re.match(r'^\d+$', url_or_id)


def download_video_with_ytdlp(video_url: str, video_id: str) -> Optional[str]:
    """
    Download video file using yt-dlp (supports Vimeo, Wistia, and many others).
    
    Args:
        video_url: Video URL
        video_id: Video ID (for naming)
        
    Returns:
        Path to downloaded video file or None if download failed
    """
    try:
        print(f"Downloading video with yt-dlp...")
        
        # Create temporary file path
        temp_dir = tempfile.gettempdir()
        video_path_template = os.path.join(temp_dir, f"video_{video_id}.%(ext)s")
        
        # Store the actual filename for later retrieval
        downloaded_filename = [None]
        
        def progress_hook(d):
            if d.get('status') == 'downloading':
                percent = d.get('_percent_str', 'N/A')
                print(f"\rDownloading: {percent}", end='')
            elif d.get('status') == 'finished':
                downloaded_filename[0] = d.get('filename')
        
        # Configure yt-dlp options
        # Try to use cookies from browser for authenticated videos (Vimeo, etc.)
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': video_path_template,
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [progress_hook],
        }
        
        # Try to get cookies from browser for Vimeo videos (helps with private/unlisted videos)
        if 'vimeo.com' in video_url.lower():
            # Try Chrome first (most common), fallback to Edge, then Firefox
            # yt-dlp will handle errors if cookies aren't available
            try:
                ydl_opts['cookiesfrombrowser'] = ('chrome',)
                print("Attempting to use cookies from Chrome browser...")
            except:
                try:
                    ydl_opts['cookiesfrombrowser'] = ('edge',)
                    print("Attempting to use cookies from Edge browser...")
                except:
                    try:
                        ydl_opts['cookiesfrombrowser'] = ('firefox',)
                        print("Attempting to use cookies from Firefox browser...")
                    except:
                        # Continue without cookies if none are available
                        pass
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Download the video
            ydl.download([video_url])
            
            # Get the filename from the progress hook or prepare it
            if downloaded_filename[0] and os.path.exists(downloaded_filename[0]):
                print(f"\nVideo downloaded successfully: {downloaded_filename[0]}")
                return downloaded_filename[0]
            
            # Fallback: try to find the file by pattern
            # Extract info to get expected filename
            try:
                info = ydl.extract_info(video_url, download=False)
                expected_filename = ydl.prepare_filename(info)
                if os.path.exists(expected_filename):
                    print(f"\nVideo downloaded successfully: {expected_filename}")
                    return expected_filename
            except:
                pass
            
            # Last resort: search for files matching our pattern
            pattern_base = os.path.join(temp_dir, f"video_{video_id}")
            for ext in ['.mp4', '.webm', '.mkv', '.m4a', '.mov']:
                potential_file = pattern_base + ext
                if os.path.exists(potential_file):
                    print(f"\nVideo downloaded successfully: {potential_file}")
                    return potential_file
            
            return None
        
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if 'login' in error_msg.lower() or 'authentication' in error_msg.lower() or 'cookies' in error_msg.lower():
            print(f"\nError: This video requires authentication/login.")
            print(f"\nFor Vimeo videos that require login, you have a few options:")
            print(f"1. Use yt-dlp with cookies from your browser:")
            print(f"   yt-dlp --cookies-from-browser chrome {video_url}")
            print(f"2. Export cookies from your browser and use:")
            print(f"   yt-dlp --cookies cookies.txt {video_url}")
            print(f"\nAlternatively, if this is a private/unlisted video, make sure you're logged in")
            print(f"to Vimeo in your browser and export the cookies.")
            return None
        else:
            print(f"\nError downloading video with yt-dlp: {e}")
            return None
    except Exception as e:
        print(f"\nError downloading video with yt-dlp: {e}")
        # Don't print full traceback for known errors
        if 'login' not in str(e).lower() and 'authentication' not in str(e).lower():
            import traceback
            traceback.print_exc()
        return None


def extract_and_download(video_input: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Main function to extract video ID and download video.
    Supports Vimeo, Wistia, and other platforms via yt-dlp.
    
    Args:
        video_input: Video URL or video ID
        
    Returns:
        Tuple of (video_id, video_file_path) or (None, None) if failed
    """
    # Extract video ID for naming purposes
    video_id = extract_video_id(video_input)
    
    # If we can't extract ID, try using yt-dlp directly with the URL
    if not video_id:
        # Try to use the input as-is (might be a full URL)
        if 'http' in video_input or 'vimeo.com' in video_input.lower() or 'wistia.com' in video_input.lower():
            print(f"Attempting to download directly from URL...")
            video_path = download_video_with_ytdlp(video_input, "video")
            if video_path:
                # Try to extract ID from URL for naming
                extracted_id = extract_video_id(video_input)
                return extracted_id or "video", video_path
            else:
                print(f"Error: Could not download video from: {video_input}")
                return None, None
        else:
            print(f"Error: Could not extract video ID from: {video_input}")
            return None, None
    
    print(f"Video ID: {video_id}")
    
    # Determine if it's a Vimeo URL
    is_vimeo = is_vimeo_url(video_input)
    
    # For Vimeo or if we have a full URL, use yt-dlp
    if is_vimeo or 'http' in video_input:
        # Use the original input (full URL) for yt-dlp
        video_url = video_input if 'http' in video_input else f"https://vimeo.com/{video_id}"
        video_path = download_video_with_ytdlp(video_url, video_id)
    else:
        # For Wistia, try the old method first, fallback to yt-dlp
        try:
            # Wistia's public embed API endpoint
            embed_url = f"https://fast.wistia.com/embed/medias/{video_id}.json"
            response = requests.get(embed_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract the highest quality video URL
            video_url = None
            if 'media' in data and 'assets' in data['media']:
                assets = data['media']['assets']
                video_assets = [a for a in assets if a.get('type') == 'original' or 
                              (a.get('type') == 'mp4' and 'url' in a)]
                
                if video_assets:
                    video_assets.sort(key=lambda x: x.get('width', 0) or x.get('height', 0), reverse=True)
                    video_url = video_assets[0].get('url')
            
            if video_url:
                print(f"Video URL retrieved successfully")
                # Download using requests
                print(f"Downloading video...")
                response = requests.get(video_url, stream=True, timeout=30)
                response.raise_for_status()
                
                temp_dir = tempfile.gettempdir()
                video_path = os.path.join(temp_dir, f"wistia_{video_id}.mp4")
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                if downloaded % (1024 * 1024) < 8192:
                                    print(f"Downloaded: {percent:.1f}%", end='\r')
                
                print(f"\nVideo downloaded successfully: {video_path}")
            else:
                # Fallback to yt-dlp for Wistia
                video_url = f"https://fast.wistia.com/embed/medias/{video_id}"
                video_path = download_video_with_ytdlp(video_url, video_id)
        except Exception as e:
            # Fallback to yt-dlp if Wistia API fails
            print(f"Wistia API method failed, trying yt-dlp: {e}")
            video_url = video_input if 'http' in video_input else f"https://fast.wistia.com/embed/medias/{video_id}"
            video_path = download_video_with_ytdlp(video_url, video_id)
    
    if not video_path:
        return video_id, None
    
    return video_id, video_path

