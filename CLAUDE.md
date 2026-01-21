# Claude Code Project Guide

A pipeline to scrape, transcribe, and summarize short-form videos from TikTok into actionable insights.

## Quick Start with /start Command

The easiest way to use this project is with the `/start` command which orchestrates everything:

```
/start
```

This will:
1. Set up the Python environment
2. Run tests to verify installation
3. Ask you for the TikTok profile to process
4. Download and transcribe videos
5. Analyze transcripts and create organized summaries

**No API keys required!** Claude Code handles the summarization directly.

## Manual Setup

If you prefer manual control:

```bash
# Clone and enter project
git clone https://github.com/grandamenium/short-form-video-transcriber.git
cd short-form-video-transcriber

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template (optional customization)
cp .env.example .env

# Run tests
pytest tests/unit/ -v
```

## Project Architecture

```
src/short_form_scraper/
├── cli.py              # CLI entry point
├── config.py           # Configuration (pydantic-settings)
├── models.py           # Data models
├── scraper/tiktok.py   # yt-dlp URL extraction
├── downloader/video.py # Audio download
├── transcriber/whisper.py  # Whisper transcription
├── summarizer/claude.py    # API-based summarization (optional)
├── organizer/output.py     # File organization
└── pipeline/runner.py      # Pipeline orchestration
```

## Data Flow

```
TikTok Profile URL
    │
    ▼ yt-dlp --flat-playlist
List[VideoMetadata]
    │
    ▼ yt-dlp -x --audio-format mp3
audio.mp3
    │
    ▼ whisper.transcribe()
transcript: str
    │
    ▼ Claude Code (via /start) OR Claude API
summaries/{topic}/summary_*.md
```

## Output Structure

After running `/start`:

```
transcripts/
├── {video_id}.txt      # Raw transcripts

summaries/
├── INDEX.md            # Master index
├── agentic-engineering/
│   └── {video_id}.md
├── context-management/
│   └── {video_id}.md
└── prompt-engineering/
    └── {video_id}.md
```

## Key Files

- **`pipeline/runner.py`** - Main orchestration logic
- **`config.py`** - Settings via environment variables (all optional)
- **`models.py`** - `VideoMetadata`, `VideoResult`
- **`.claude/skills/start/SKILL.md`** - The /start command definition

## Environment Variables (All Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL` | `base` | tiny/base/small/medium/large |
| `OUTPUT_DIR` | `./output` | Transcripts and audio location |
| `STATE_DIR` | `./state` | Processing state location |
| `SKIP_EXISTING` | `true` | Skip already processed videos |

## Testing

```bash
# Unit tests (no network)
pytest tests/unit/ -v

# Integration tests (requires network)
pytest tests/integration/ -v -s
```

## Common Tasks

### Process specific profile
```bash
scrape-videos "https://www.tiktok.com/@username" --limit 5
```

### Reset and reprocess
```bash
rm -rf state/ transcripts/ summaries/
/start
```

### Use larger Whisper model for better accuracy
Edit `.env`:
```
WHISPER_MODEL=large
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
```

### Slow transcription
Use smaller model: `WHISPER_MODEL=tiny`

## Dependencies

- **yt-dlp** - Video/audio downloading (install separately)
- **openai-whisper** - Local transcription (no API key)
- **ffmpeg** - Audio processing (install separately)
