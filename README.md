# Short-Form Video Transcriber

Scrape, transcribe, and summarize short-form videos from TikTok into organized, actionable insights.

**Works with Claude Code** - No API keys required for the full workflow!

## Features

- **Scrape** video URLs from TikTok profiles using yt-dlp
- **Download** and extract audio from videos
- **Transcribe** audio to text using OpenAI Whisper (runs locally)
- **Summarize** transcripts using Claude Code (via `/start` command)
- **Organize** output into topic-named folders

## Quick Start with Claude Code

1. Clone the repository:
   ```bash
   git clone https://github.com/grandamenium/short-form-video-transcriber.git
   cd short-form-video-transcriber
   ```

2. Open with Claude Code and run:
   ```
   /start
   ```

That's it! The `/start` command will:
- Set up your Python environment
- Install all dependencies
- Run tests to verify everything works
- Guide you through processing videos
- Create organized summaries

## Output Structure

```
transcripts/
├── {video_id}.txt           # Raw transcripts

summaries/
├── INDEX.md                 # Master index of all summaries
├── agentic-engineering/
│   └── {video_id}.md
├── context-management/
│   └── {video_id}.md
└── prompt-engineering/
    └── {video_id}.md
```

## Prerequisites

- **Python 3.10+**
- **yt-dlp** - `brew install yt-dlp` or `pip install yt-dlp`
- **ffmpeg** - `brew install ffmpeg`
- **Claude Code** - For the `/start` orchestration

## Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template (optional)
cp .env.example .env

# Run tests
pytest tests/unit/ -v
```

## CLI Usage

For manual processing without Claude Code:

```bash
# Process videos (downloads and transcribes only)
scrape-videos "https://www.tiktok.com/@username" --limit 5

# Test with a single video
scrape-videos "https://www.tiktok.com/@username" --single "https://www.tiktok.com/@username/video/123456"
```

## Configuration (Optional)

All settings have sensible defaults. Customize in `.env`:

```bash
# Whisper model size (tiny, base, small, medium, large)
WHISPER_MODEL=base

# Output directories
OUTPUT_DIR=./output
STATE_DIR=./state

# Skip already processed videos
SKIP_EXISTING=true
```

## How It Works

1. **Scraping**: Uses yt-dlp to extract video metadata from TikTok profiles
2. **Downloading**: Extracts audio as MP3 using yt-dlp
3. **Transcription**: Runs OpenAI Whisper locally (no API needed)
4. **Summarization**: Claude Code analyzes transcripts and extracts:
   - Topic classification
   - One-sentence summary
   - Key actionable tips
   - Additional context

## Project Structure

```
src/short_form_scraper/
├── cli.py              # Command-line interface
├── config.py           # Settings management
├── models.py           # Data models
├── scraper/            # TikTok URL extraction
├── downloader/         # Audio download
├── transcriber/        # Whisper transcription
├── summarizer/         # API-based summarization (optional)
├── organizer/          # File organization
└── pipeline/           # Orchestration

.claude/
└── skills/
    └── start/          # /start command definition
```

## Running Tests

```bash
# Unit tests (fast, no network)
pytest tests/unit/ -v

# All tests
pytest -v
```

## Troubleshooting

### "yt-dlp not found"
```bash
brew install yt-dlp  # macOS
pip install yt-dlp   # any platform
```

### "ffmpeg not found"
```bash
brew install ffmpeg  # macOS
# See https://ffmpeg.org/download.html for other platforms
```

### Slow transcription
Use a smaller Whisper model:
```bash
# In .env
WHISPER_MODEL=tiny
```

### Rate limiting
TikTok may rate limit requests. Solutions:
- Add delays between videos
- Use cookies from a logged-in browser session

## License

MIT

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloading
- [OpenAI Whisper](https://github.com/openai/whisper) - Transcription
- [Claude Code](https://claude.ai/code) - Orchestration and summarization
