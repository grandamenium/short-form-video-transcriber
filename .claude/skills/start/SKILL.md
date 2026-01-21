---
name: start
description: Set up the project and learn how to use it. Run this first when opening the project.
user_invocable: true
---

# Short-Form Video Transcriber - Start

When the user runs `/start`, follow this workflow:

## Step 1: Welcome Message

Display this welcome message:

---

**Welcome to the Short-Form Video Transcriber!**

This project helps you:
- Scrape videos from TikTok profiles
- Transcribe audio to text using AI (Whisper)
- Create organized summaries by topic

Let me check if your environment is set up...

---

## Step 2: Environment Check

Run these checks:

```bash
# Check Python
python3 --version

# Check yt-dlp
which yt-dlp

# Check ffmpeg
which ffmpeg

# Check if venv exists
ls -la .venv/bin/activate 2>/dev/null || echo "NO_VENV"
```

### If prerequisites missing:

Tell the user what to install:
- **yt-dlp missing**: "Install with: `brew install yt-dlp` or `pip install yt-dlp`"
- **ffmpeg missing**: "Install with: `brew install ffmpeg`"

### If venv doesn't exist:

Create and set up the environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### If venv exists:

Verify it works:

```bash
source .venv/bin/activate
pytest tests/unit/ -v --tb=short 2>&1 | tail -5
```

## Step 3: Explain Available Commands

After setup is verified, explain the commands:

---

**Setup complete! Here's how to use this project:**

### Available Commands

| Command | What it does |
|---------|--------------|
| `/start` | You're here! Set up the project and see available commands |
| `/bulk` | Transcribe ALL videos from a TikTok profile |
| `/transcribe` | Transcribe specific video URL(s) you paste |
| `/accounts` | Switch profiles, add multiple accounts, process several at once |
| `/skillify` | Turn a summary into a reusable Claude skill |

### `/bulk` - Process Entire Profile

Use this when you want to transcribe all videos from someone's TikTok.

Just run `/bulk` and I'll ask you for:
1. The TikTok profile URL (e.g., `https://www.tiktok.com/@agentic.james`)
2. How many videos to process (all, or a specific number)

I'll then download, transcribe, and summarize each video automatically.

### `/transcribe` - Process Specific Videos

Use this when you have specific video URLs you want to transcribe.

Just run `/transcribe` and paste the URLs:
```
https://www.tiktok.com/@username/video/123456789
https://www.tiktok.com/@username/video/987654321
```

You can paste one URL or multiple URLs at once.

### `/accounts` - Manage Multiple Profiles

Want to scrape from different TikTok accounts? Use `/accounts` to:
- Switch to a different profile
- Add multiple profiles to your list
- Process several profiles at once
- Remove profiles you no longer need

Your saved profiles are stored in `accounts.json`.

### `/skillify` - Create Claude Skills from Summaries

Turn any summary into a reusable Claude skill! This command:
1. Takes a transcript summary you've created
2. Researches the topic with web search to add depth
3. Creates a properly formatted Claude skill file
4. Saves it to your skills directory (global or project-local)

Great for building a knowledge base from video content!

### Output

All commands create:
- `transcripts/` - Raw transcripts with metadata
- `summaries/` - Organized summaries grouped by topic
- `summaries/INDEX.md` - Master index of all content
- Skills created via `/skillify` go to your chosen directory

---

**What would you like to do?**
- Run `/bulk` to process an entire TikTok profile
- Run `/transcribe` to process specific video URLs
- Run `/skillify` to turn a summary into a Claude skill
- Or just paste some TikTok URLs and I'll transcribe them for you!

---

## Step 4: Handle User's Next Action

After explaining, wait for the user to either:
1. Run `/bulk` or `/transcribe`
2. Paste video URLs directly (treat this as running `/transcribe`)
3. Ask questions

If they paste URLs directly without a command, process them as if they ran `/transcribe`.

## Error Handling

If setup fails:
- Show clear error message
- Suggest specific fix
- Offer to retry

If tests fail:
- Show which tests failed
- Check if dependencies are installed correctly
- Suggest reinstalling with `pip install -e ".[dev]"`
