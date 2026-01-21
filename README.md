# Short-Form Video Transcriber

Scrape, transcribe, and summarize short-form videos from TikTok into organized, actionable insights.

**Works with Claude Code** - No API keys required!

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/grandamenium/short-form-video-transcriber.git
   cd short-form-video-transcriber
   ```

2. Open with Claude Code and run:
   ```
   /start
   ```

That's it! Claude Code will set everything up and explain how to use the project.

## Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Set up the project and see all available commands |
| `/bulk` | Transcribe ALL videos from a TikTok profile |
| `/transcribe` | Transcribe specific video URL(s) you paste |
| `/accounts` | Switch profiles, add multiple accounts, process several |
| `/skillify` | Turn a summary into a reusable Claude skill |

### `/bulk` - Process Entire Profile

Want to transcribe every video from a TikTok account?

1. Run `/bulk`
2. Paste the profile URL: `https://www.tiktok.com/@username`
3. Choose how many videos (all, or a specific number)
4. Wait while Claude Code processes everything

### `/transcribe` - Process Specific Videos

Have specific videos you want to transcribe?

1. Run `/transcribe`
2. Paste the URL(s):
   ```
   https://www.tiktok.com/@username/video/123456789
   https://www.tiktok.com/@username/video/987654321
   ```

**Pro tip**: You can also just paste TikTok URLs directly - Claude Code will automatically transcribe them!

### `/accounts` - Manage Multiple Profiles

Want to scrape from different TikTok accounts?

1. Run `/accounts`
2. Switch profiles, add new ones, or process multiple at once
3. Saved to `accounts.json`

### `/skillify` - Create Claude Skills

Turn your summaries into reusable Claude skills:

1. Run `/skillify`
2. Pick a summary or paste content
3. Claude Code researches the topic for additional depth
4. Choose where to save the skill
5. Get a formatted skill file for future use

Build a knowledge base from video content!

## Output

```
transcripts/
├── {video_id}.txt           # Raw transcripts

summaries/
├── INDEX.md                 # Master index
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
- **Claude Code** - For the slash commands

## Manual Setup (Optional)

If you prefer manual control:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/unit/ -v
```

## Configuration (Optional)

All settings have sensible defaults. Customize in `.env`:

```bash
WHISPER_MODEL=base     # tiny, base, small, medium, large
OUTPUT_DIR=./output
STATE_DIR=./state
SKIP_EXISTING=true
```

## How It Works

1. **Scraping**: Uses yt-dlp to get video metadata from TikTok
2. **Downloading**: Extracts audio as MP3
3. **Transcription**: Runs OpenAI Whisper locally (no API needed)
4. **Summarization**: Claude Code analyzes transcripts and creates organized summaries with:
   - Topic classification
   - Key actionable tips
   - Full transcript

## Project Structure

```
.claude/skills/
├── start/       # /start command
├── bulk/        # /bulk command
├── transcribe/  # /transcribe command
├── accounts/    # /accounts command
└── skillify/    # /skillify command

src/short_form_scraper/
├── scraper/     # TikTok URL extraction
├── downloader/  # Audio download
├── transcriber/ # Whisper transcription
└── ...
```

## Running Tests

```bash
source .venv/bin/activate
pytest tests/unit/ -v
```

## Troubleshooting

### "yt-dlp not found"
```bash
brew install yt-dlp  # macOS
pip install yt-dlp   # any platform
```

### "ffmpeg not found"
```bash
brew install ffmpeg
```

### Slow transcription
Use smaller model: `WHISPER_MODEL=tiny` in `.env`

## License

MIT

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloading
- [OpenAI Whisper](https://github.com/openai/whisper) - Transcription
- [Claude Code](https://claude.ai/code) - Orchestration
