"""TikTok profile scraper using yt-dlp."""

import json
import subprocess
from datetime import datetime
from typing import Iterator, Optional

from ..config import get_settings
from ..models import VideoMetadata


class TikTokScraper:
    """Extract video metadata from TikTok profile using yt-dlp."""

    def __init__(self, profile_url: str):
        """Initialize scraper with profile URL.

        Args:
            profile_url: TikTok profile URL (e.g., https://www.tiktok.com/@username)
        """
        self.profile_url = profile_url
        self.settings = get_settings()

    def get_video_urls(self, limit: Optional[int] = None) -> Iterator[VideoMetadata]:
        """Stream video metadata from profile.

        Args:
            limit: Maximum number of videos to fetch. None for all.

        Yields:
            VideoMetadata for each video found.
        """
        cmd = [
            self.settings.get_yt_dlp_path(),
            "--flat-playlist",
            "--dump-json",
            self.profile_url,
        ]
        if limit:
            cmd.extend(["--playlist-items", f"1:{limit}"])

        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                yield self._parse_metadata(data)
            except json.JSONDecodeError:
                continue

        proc.wait()

    def get_single_video_metadata(self, video_url: str) -> VideoMetadata:
        """Get metadata for a single video.

        Args:
            video_url: Direct URL to a TikTok video.

        Returns:
            VideoMetadata for the video.
        """
        cmd = [
            self.settings.get_yt_dlp_path(),
            "--dump-json",
            "--no-download",
            video_url,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return self._parse_metadata(data)

    def _parse_metadata(self, data: dict) -> VideoMetadata:
        """Parse yt-dlp JSON output into VideoMetadata.

        Args:
            data: JSON data from yt-dlp.

        Returns:
            Parsed VideoMetadata.
        """
        timestamp = None
        if data.get("timestamp"):
            try:
                timestamp = datetime.fromtimestamp(data["timestamp"])
            except (ValueError, OSError):
                pass

        return VideoMetadata(
            id=data.get("id", ""),
            url=data.get("webpage_url") or data.get("url", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            duration=data.get("duration", 0) or 0,
            timestamp=timestamp,
            view_count=data.get("view_count", 0) or 0,
            like_count=data.get("like_count", 0) or 0,
        )
