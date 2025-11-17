# Wistia Video Transcription Tool

A Python CLI tool that transcribes Wistia videos using AssemblyAI. Simply provide a Wistia URL or video ID, and get a transcript saved to a text file.

## Features

- Extract video from Wistia URLs or video IDs
- Automatic audio extraction from video files
- High-quality transcription using AssemblyAI
- Interactive command-line interface
- Automatic transcript file saving

## Requirements

- Python 3.7 or higher
- ffmpeg installed on your system
- AssemblyAI API key

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LJGROHN/VimeoTranscribe.git
   cd VimeoTranscribe
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install ffmpeg:**
   - **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `choco install ffmpeg`
   - **macOS:** `brew install ffmpeg`
   - **Linux:** `sudo apt-get install ffmpeg` or `sudo yum install ffmpeg`

5. **Set up your AssemblyAI API key:**
   ```bash
   # On Windows (PowerShell):
   $env:ASSEMBLYAI_API_KEY="your_api_key_here"
   
   # On macOS/Linux:
   export ASSEMBLYAI_API_KEY="your_api_key_here"
   ```
   
   Or create a `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   # Then edit .env and add your API key
   ```

## Usage

Run the script:
```bash
python main.py
```

The interactive CLI will prompt you to:
1. Enter a Wistia URL or video ID
2. Process the video (download → extract audio → transcribe)
3. Display the transcript
4. Automatically save the transcript to a file

### Example Inputs

- Wistia URL: `https://support.wistia.com/medias/26sk4lmiix`
- Video ID: `26sk4lmiix`
- Short URL: `https://wi.st/26sk4lmiix`

### Output

The transcript will be saved as `transcript_<video_id>.txt` in the current directory.

## Project Structure

```
VimeoTranscribe/
├── main.py                 # Main CLI entry point
├── wistia_extractor.py     # Wistia video download logic
├── audio_processor.py      # Audio extraction with ffmpeg
├── transcriber.py          # AssemblyAI integration
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variable file
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## How It Works

1. **Video Extraction:** Parses the Wistia URL/ID and fetches the video file from Wistia's API
2. **Audio Processing:** Extracts audio from the video using ffmpeg
3. **Transcription:** Uploads audio to AssemblyAI and retrieves the transcript
4. **Output:** Saves the transcript to a text file

## Error Handling

The tool handles:
- Invalid Wistia URLs/IDs
- Network errors
- Missing API keys
- ffmpeg errors
- AssemblyAI API errors

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

