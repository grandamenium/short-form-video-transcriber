"""Pipeline orchestration for the full scrape-transcribe-summarize workflow."""

import json
from pathlib import Path
from typing import Optional

from ..config import Settings, get_settings
from ..downloader.video import VideoDownloader
from ..models import PipelineProgress, ProcessingStatus, VideoMetadata, VideoResult
from ..organizer.output import OutputOrganizer
from ..scraper.tiktok import TikTokScraper
from ..summarizer.claude import ClaudeSummarizer
from ..transcriber.whisper import WhisperTranscriber


class PipelineRunner:
    """Orchestrate the full video processing pipeline."""

    def __init__(
        self, profile_url: str, settings: Optional[Settings] = None
    ):
        """Initialize pipeline.

        Args:
            profile_url: TikTok profile URL to scrape.
            settings: Optional custom settings.
        """
        self.profile_url = profile_url
        self.settings = settings or get_settings()

        # Components (lazy initialized)
        self._scraper = None
        self._downloader = None
        self._transcriber = None
        self._summarizer = None
        self._organizer = None

        # State files
        self.progress_file = self.settings.state_dir / "progress.json"
        self.processed_file = self.settings.state_dir / "processed.json"

    @property
    def scraper(self) -> TikTokScraper:
        if self._scraper is None:
            self._scraper = TikTokScraper(self.profile_url)
        return self._scraper

    @property
    def downloader(self) -> VideoDownloader:
        if self._downloader is None:
            self._downloader = VideoDownloader()
        return self._downloader

    @property
    def transcriber(self) -> WhisperTranscriber:
        if self._transcriber is None:
            self._transcriber = WhisperTranscriber()
        return self._transcriber

    @property
    def summarizer(self) -> ClaudeSummarizer:
        if self._summarizer is None:
            self._summarizer = ClaudeSummarizer()
        return self._summarizer

    @property
    def organizer(self) -> OutputOrganizer:
        if self._organizer is None:
            self._organizer = OutputOrganizer(self.settings.output_dir)
        return self._organizer

    def run(
        self,
        limit: Optional[int] = None,
        single_video_url: Optional[str] = None,
    ) -> list[VideoResult]:
        """Run the full pipeline.

        Args:
            limit: Maximum number of videos to process.
            single_video_url: Process only this single video URL.

        Returns:
            List of VideoResult objects.
        """
        results = []

        # Ensure directories exist
        self.settings.state_dir.mkdir(parents=True, exist_ok=True)
        self.settings.output_dir.mkdir(parents=True, exist_ok=True)

        # Load existing progress for idempotency
        processed_ids = self._load_processed()

        # Get videos to process
        if single_video_url:
            videos = [self.scraper.get_single_video_metadata(single_video_url)]
        else:
            videos = list(self.scraper.get_video_urls(limit))

        print(f"Found {len(videos)} videos to process")

        for i, metadata in enumerate(videos):
            # Skip already processed (idempotency)
            if self.settings.skip_existing and metadata.id in processed_ids:
                print(f"[{i+1}/{len(videos)}] Skipping {metadata.id} (already processed)")
                continue

            result = self._process_video(metadata, i, len(videos), processed_ids)
            results.append(result)

        # Create index file
        if results:
            self.organizer.create_index()

        return results

    def _process_video(
        self,
        metadata: VideoMetadata,
        index: int,
        total: int,
        processed_ids: set[str],
    ) -> VideoResult:
        """Process a single video through the pipeline.

        Args:
            metadata: Video metadata.
            index: Current index in batch.
            total: Total videos in batch.
            processed_ids: Set of already processed IDs.

        Returns:
            VideoResult with processing outcome.
        """
        result = VideoResult(metadata=metadata)
        video_id = metadata.id
        title_preview = metadata.title[:40] + "..." if len(metadata.title) > 40 else metadata.title

        try:
            # Update progress
            self._save_progress(
                PipelineProgress(
                    total_videos=total,
                    current_index=index,
                    phase="processing",
                    processed_ids=list(processed_ids),
                )
            )

            # Step 1: Download
            print(f"[{index+1}/{total}] Downloading: {title_preview}")
            result.status = ProcessingStatus.DOWNLOADING
            temp_path = self.settings.state_dir / f"temp_{video_id}"
            result.audio_path = self.downloader.download(metadata.url, temp_path)

            # Step 2: Transcribe
            print(f"[{index+1}/{total}] Transcribing: {title_preview}")
            result.status = ProcessingStatus.TRANSCRIBING
            result.transcript = self.transcriber.transcribe(result.audio_path)

            # Step 3: Summarize
            print(f"[{index+1}/{total}] Summarizing: {title_preview}")
            result.status = ProcessingStatus.SUMMARIZING
            result.topic, result.summary = self.summarizer.summarize(
                result.transcript, metadata
            )

            # Step 4: Organize
            print(f"[{index+1}/{total}] Organizing into topic: {result.topic}")
            result.status = ProcessingStatus.ORGANIZING
            self.organizer.organize(result)

            # Mark complete
            result.status = ProcessingStatus.COMPLETE
            processed_ids.add(video_id)
            self._save_processed(processed_ids)

            print(f"[{index+1}/{total}] Complete: {title_preview} -> {result.topic}/")

        except Exception as e:
            result.status = ProcessingStatus.FAILED
            result.error = str(e)
            print(f"[{index+1}/{total}] FAILED: {title_preview} - {e}")

        return result

    def _load_processed(self) -> set[str]:
        """Load set of already processed video IDs."""
        if self.processed_file.exists():
            try:
                data = json.loads(self.processed_file.read_text())
                return set(data)
            except (json.JSONDecodeError, TypeError):
                return set()
        return set()

    def _save_processed(self, ids: set[str]) -> None:
        """Save set of processed video IDs."""
        self.settings.state_dir.mkdir(parents=True, exist_ok=True)
        self.processed_file.write_text(json.dumps(list(ids)))

    def _save_progress(self, progress: PipelineProgress) -> None:
        """Save current progress state."""
        self.settings.state_dir.mkdir(parents=True, exist_ok=True)
        self.progress_file.write_text(progress.model_dump_json(indent=2))

    def reset_state(self) -> None:
        """Reset all processing state (for re-running from scratch)."""
        if self.processed_file.exists():
            self.processed_file.unlink()
        if self.progress_file.exists():
            self.progress_file.unlink()
        print("State reset - all videos will be reprocessed")
