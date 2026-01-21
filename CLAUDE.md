# Claude Code Project Guide

A pipeline to scrape, transcribe, and summarize short-form videos from TikTok into actionable insights.

## Quick Start

Open this project with Claude Code and run:

```
/start
```

This will:
1. Check and set up your environment
2. Explain all available commands
3. Guide you through using the project

**No API keys required!** Everything runs locally or through Claude Code.

## Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Set up the project and see all available commands |
| `/bulk` | Transcribe ALL videos from a TikTok profile |
| `/transcribe` | Transcribe specific video URL(s) you paste |
| `/accounts` | Switch profiles, add multiple accounts, process several |
| `/skillify` | Turn a summary into a reusable Claude skill |

### `/start` - First Time Setup

Run this first! It will:
- Check prerequisites (Python, yt-dlp, ffmpeg)
- Create virtual environment
- Install dependencies
- Run tests to verify installation
- Explain how to use the project

### `/bulk` - Process Entire Profile

Transcribe all videos from a TikTok profile:

1. Run `/bulk`
2. Paste the profile URL (e.g., `https://www.tiktok.com/@agentic.james`)
3. Choose how many videos to process (all or a specific number)
4. Claude Code downloads, transcribes, and summarizes everything

### `/transcribe` - Process Specific Videos

Transcribe one or more specific videos:

1. Run `/transcribe`
2. Paste the video URL(s):
   ```
   https://www.tiktok.com/@username/video/123456789
   https://www.tiktok.com/@username/video/987654321
   ```
3. Claude Code processes each video

**Tip**: You can also just paste TikTok URLs directly without running a command - Claude Code will automatically transcribe them.

### `/accounts` - Manage Multiple Profiles

Switch between TikTok accounts or process multiple:

1. Run `/accounts`
2. Choose: switch, add, list, remove, or process multiple
3. Profiles are saved to `accounts.json`

### `/skillify` - Create Claude Skills

Turn summaries into reusable Claude skills:

1. Run `/skillify`
2. Select a summary (or paste content)
3. Claude Code researches the topic for additional depth
4. Choose where to save (global `~/.claude/skills/` or project-local)
5. Get a properly formatted skill file

Great for building a personal knowledge base from video content!

## Output Structure

```
transcripts/
├── {video_id}.txt           # Raw transcripts with metadata

summaries/
├── INDEX.md                 # Master index of all summaries
├── agentic-engineering/
│   └── {video_id}.md
├── context-management/
│   └── {video_id}.md
└── prompt-engineering/
    └── {video_id}.md
```

## Manual CLI Usage

For advanced users who prefer command line:

```bash
# Activate environment
source .venv/bin/activate

# Process videos (download + transcribe only, no summarization)
scrape-videos "https://www.tiktok.com/@username" --limit 5

# Process single video
scrape-videos "https://www.tiktok.com/@username" --single "https://www.tiktok.com/@username/video/123"
```

## Project Structure

```
.claude/skills/
├── start/SKILL.md      # /start command
├── bulk/SKILL.md       # /bulk command
├── transcribe/SKILL.md # /transcribe command
├── accounts/SKILL.md   # /accounts command
└── skillify/SKILL.md   # /skillify command

src/short_form_scraper/
├── cli.py              # CLI entry point
├── config.py           # Configuration
├── models.py           # Data models
├── scraper/            # TikTok URL extraction
├── downloader/         # Audio download
├── transcriber/        # Whisper transcription
├── summarizer/         # API-based summarization (optional)
├── organizer/          # File organization
└── pipeline/           # Orchestration
```

## Environment Variables (Optional)

All settings have defaults. Customize in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL` | `base` | tiny/base/small/medium/large |
| `OUTPUT_DIR` | `./output` | Transcripts and audio location |
| `STATE_DIR` | `./state` | Processing state location |
| `SKIP_EXISTING` | `true` | Skip already processed videos |

## Testing

```bash
source .venv/bin/activate
pytest tests/unit/ -v
```

## Prerequisites

- Python 3.10+
- yt-dlp (`brew install yt-dlp`)
- ffmpeg (`brew install ffmpeg`)

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
Use smaller model: edit `.env` and set `WHISPER_MODEL=tiny`
