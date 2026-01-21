---
name: start
description: Orchestrate the full video transcription and summarization workflow. Use when setting up the project or processing videos.
user_invocable: true
---

# Short-Form Video Transcriber - Start Orchestration

This skill orchestrates the complete workflow for scraping, transcribing, and summarizing short-form videos using Claude Code.

## Workflow Steps

When the user invokes `/start`, execute the following steps in order:

### Step 1: Environment Check & Setup

1. Check if running in the project directory (`short-form-socials-scraping` or `short-form-video-transcriber`)
2. If not in project directory, inform user and exit
3. Check if virtual environment exists (`.venv/`)
4. If no venv, create it: `python -m venv .venv`
5. Activate venv and install dependencies: `pip install -e ".[dev]"`

### Step 2: Verify Installation

1. Run unit tests to verify installation: `pytest tests/unit/ -v`
2. If tests fail, report errors and stop
3. Confirm yt-dlp is available: `which yt-dlp`
4. If yt-dlp missing, instruct user to install: `brew install yt-dlp` or `pip install yt-dlp`

### Step 3: Get User Configuration

Ask the user:
1. **TikTok Profile URL**: What TikTok profile do you want to process? (default: https://www.tiktok.com/@agentic.james)
2. **Video Limit**: How many videos to process? (default: all, or specify a number like 5)

### Step 4: Scrape and Download Videos

1. Run the scraper to get video URLs:
   ```bash
   source .venv/bin/activate && python -c "
   from short_form_scraper.scraper.tiktok import TikTokScraper
   scraper = TikTokScraper('PROFILE_URL')
   videos = list(scraper.get_video_urls(limit=LIMIT))
   print(f'Found {len(videos)} videos')
   for v in videos:
       print(f'{v.id}: {v.title}')
   "
   ```

2. For each video, download and transcribe:
   ```bash
   source .venv/bin/activate && python -c "
   from short_form_scraper.scraper.tiktok import TikTokScraper
   from short_form_scraper.downloader.video import VideoDownloader
   from short_form_scraper.transcriber.whisper import WhisperTranscriber
   from pathlib import Path

   scraper = TikTokScraper('PROFILE_URL')
   downloader = VideoDownloader()
   transcriber = WhisperTranscriber()

   videos = list(scraper.get_video_urls(limit=LIMIT))

   for metadata in videos:
       print(f'Processing: {metadata.title}')

       # Download
       audio_path = downloader.download(metadata.url, Path(f'state/audio_{metadata.id}'))

       # Transcribe
       transcript = transcriber.transcribe(audio_path)

       # Save transcript
       transcript_dir = Path('transcripts')
       transcript_dir.mkdir(exist_ok=True)
       transcript_file = transcript_dir / f'{metadata.id}.txt'
       transcript_file.write_text(f'Title: {metadata.title}\\nURL: {metadata.url}\\n\\n{transcript}')
       print(f'Saved: {transcript_file}')
   "
   ```

### Step 5: Summarize Transcripts (Claude Code)

After transcripts are generated, YOU (Claude Code) will:

1. Read each transcript file from `transcripts/` directory
2. For each transcript, analyze and extract:
   - **Topic**: A descriptive 2-4 word kebab-case topic name
   - **Summary**: One-sentence summary of the main point
   - **Key Tips**: 3-5 actionable bullet points
   - **Details**: Additional context

3. Create organized output in `summaries/` directory:
   ```
   summaries/
   ├── {topic-name}/
   │   └── {video-id}.md
   ```

4. Each summary file should contain:
   ```markdown
   ---
   video_id: {id}
   title: {title}
   url: {url}
   topic: {topic}
   ---

   # {Title}

   ## Summary
   {one-sentence summary}

   ## Key Tips
   - {tip 1}
   - {tip 2}
   - {tip 3}

   ## Details
   {additional context}

   ## Full Transcript
   {original transcript}
   ```

5. Create an INDEX.md in summaries/ listing all summaries by topic

### Step 6: Report Results

After completion, report:
- Number of videos processed
- Number of transcripts created
- Number of summaries organized
- Topics identified
- Location of output files

## Error Handling

- If any step fails, report the error clearly
- Offer to retry or skip problematic videos
- Always save partial progress (transcripts saved immediately after creation)

## Example Invocation

User: `/start`

Claude Code:
1. Checks environment
2. Sets up venv if needed
3. Runs tests
4. Asks for profile URL and limit
5. Downloads and transcribes videos
6. Reads transcripts and creates summaries
7. Reports results
