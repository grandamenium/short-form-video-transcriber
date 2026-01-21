"""Video downloader using yt-dlp."""

import subprocess
from pathlib import Path

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..config import get_settings


class VideoDownloader:
    """Download videos and extract audio using yt-dlp."""

    def __init__(self, settings=None):
        """Initialize downloader.

        Args:
            settings: Optional settings object. If not provided, loads from environment.
        """
        if settings is None:
            self.settings = get_settings()
        else:
            self.settings = settings

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(subprocess.CalledProcessError),
    )
    def download(self, url: str, output_path: Path) -> Path:
        """Download video and extract audio.

        Args:
            url: Video URL to download.
            output_path: Base path for output file (extension will be added).

        Returns:
            Path to the downloaded audio file.

        Raises:
            FileNotFoundError: If download fails or audio not found.
            subprocess.CalledProcessError: If yt-dlp fails.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # yt-dlp output template - will add extension automatically
        output_template = str(output_path.with_suffix(""))

        cmd = [
            self.settings.get_yt_dlp_path(),
            "-o",
            f"{output_template}.%(ext)s",
            "--extract-audio",
            "--audio-format",
            "mp3",
            "--audio-quality",
            "0",
            "--no-playlist",
            url,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd, result.stdout, result.stderr
            )

        # Find the output file (yt-dlp might use different extension)
        audio_path = Path(f"{output_template}.mp3")
        if audio_path.exists():
            return audio_path

        # Check for other audio formats
        for ext in [".m4a", ".webm", ".opus", ".wav"]:
            alt_path = Path(f"{output_template}{ext}")
            if alt_path.exists():
                return alt_path

        raise FileNotFoundError(
            f"Expected audio at {audio_path} but file not found. "
            f"yt-dlp output: {result.stdout}"
        )

    def download_video(self, url: str, output_path: Path) -> Path:
        """Download video file (without audio extraction).

        Args:
            url: Video URL to download.
            output_path: Base path for output file.

        Returns:
            Path to the downloaded video file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_template = str(output_path.with_suffix(""))

        cmd = [
            self.settings.get_yt_dlp_path(),
            "-o",
            f"{output_template}.%(ext)s",
            "--no-playlist",
            url,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Find the output file
        for ext in [".mp4", ".webm", ".mkv"]:
            video_path = Path(f"{output_template}{ext}")
            if video_path.exists():
                return video_path

        raise FileNotFoundError(f"Video file not found after download")
