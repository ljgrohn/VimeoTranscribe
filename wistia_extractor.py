"""
Wistia video extraction module.
Handles parsing Wistia URLs/IDs and downloading video files.
"""

import re
import requests
import tempfile
import os
from typing import Optional, Tuple


def extract_video_id(url_or_id: str) -> Optional[str]:
    """
    Extract Wistia video ID from URL or return the ID if already provided.
    
    Args:
        url_or_id: Wistia URL or video ID
        
    Returns:
        Video ID string or None if invalid
    """
    # If it's already just an ID (alphanumeric, typically 10 chars)
    if re.match(r'^[a-z0-9]{10,}$', url_or_id.lower()):
        return url_or_id.lower()
    
    # Extract from various Wistia URL patterns
    patterns = [
        r'wistia\.com/medias/([a-z0-9]+)',
        r'wi\.st/([a-z0-9]+)',
        r'wistia\.net/embed/([a-z0-9]+)',
        r'medias/([a-z0-9]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id.lower())
        if match:
            return match.group(1)
    
    return None


def get_video_url(video_id: str) -> Optional[str]:
    """
    Fetch the direct video URL from Wistia's embed API.
    
    Args:
        video_id: Wistia video ID
        
    Returns:
        Direct video URL or None if not found
    """
    try:
        # Wistia's public embed API endpoint
        embed_url = f"https://fast.wistia.com/embed/medias/{video_id}.json"
        response = requests.get(embed_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract the highest quality video URL
        if 'media' in data and 'assets' in data['media']:
            assets = data['media']['assets']
            # Look for mp4 files, prefer higher quality
            video_assets = [a for a in assets if a.get('type') == 'original' or 
                          (a.get('type') == 'mp4' and 'url' in a)]
            
            if video_assets:
                # Sort by width/height if available, or take first
                video_assets.sort(key=lambda x: x.get('width', 0) or x.get('height', 0), reverse=True)
                return video_assets[0].get('url')
            
            # Fallback: try to find any video URL
            for asset in assets:
                if 'url' in asset and ('mp4' in asset.get('type', '') or 'original' in asset.get('type', '')):
                    return asset['url']
        
        # Alternative: try to get from iframe embed
        if 'media' in data and 'embed' in data['media']:
            embed_code = data['media']['embed']
            # Extract URL from embed code
            url_match = re.search(r'src=["\']([^"\']+)["\']', embed_code)
            if url_match:
                embed_src = url_match.group(1)
                # Try to get JSON from embed URL
                json_url = embed_src.replace('/embed/', '/embed/medias/').replace('.js', '.json')
                json_response = requests.get(json_url, timeout=10)
                if json_response.status_code == 200:
                    json_data = json_response.json()
                    if 'media' in json_data and 'assets' in json_data['media']:
                        assets = json_data['media']['assets']
                        for asset in assets:
                            if 'url' in asset:
                                return asset['url']
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching video URL: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error parsing Wistia API response: {e}")
        return None


def download_video(video_url: str, video_id: str) -> Optional[str]:
    """
    Download video file to a temporary location.
    
    Args:
        video_url: Direct URL to the video file
        video_id: Wistia video ID (for naming)
        
    Returns:
        Path to downloaded video file or None if download failed
    """
    try:
        print(f"Downloading video...")
        response = requests.get(video_url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        video_path = os.path.join(temp_dir, f"wistia_{video_id}.mp4")
        
        # Download with progress indication
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        if downloaded % (1024 * 1024) < 8192:  # Print every MB
                            print(f"Downloaded: {percent:.1f}%", end='\r')
        
        print(f"\nVideo downloaded successfully: {video_path}")
        return video_path
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading video: {e}")
        return None
    except IOError as e:
        print(f"Error saving video file: {e}")
        return None


def extract_and_download(video_input: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Main function to extract video ID and download video.
    
    Args:
        video_input: Wistia URL or video ID
        
    Returns:
        Tuple of (video_id, video_file_path) or (None, None) if failed
    """
    # Extract video ID
    video_id = extract_video_id(video_input)
    if not video_id:
        print(f"Error: Could not extract video ID from: {video_input}")
        return None, None
    
    print(f"Video ID: {video_id}")
    
    # Get video URL
    video_url = get_video_url(video_id)
    if not video_url:
        print(f"Error: Could not fetch video URL for ID: {video_id}")
        return None, None
    
    print(f"Video URL retrieved successfully")
    
    # Download video
    video_path = download_video(video_url, video_id)
    if not video_path:
        return video_id, None
    
    return video_id, video_path

