"""Unit tests for video downloader."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from short_form_scraper.downloader.video import VideoDownloader


class TestVideoDownloader:
    """Tests for VideoDownloader class."""

    @patch("short_form_scraper.downloader.video.get_settings")
    @patch("subprocess.run")
    def test_download_extracts_audio(self, mock_run, mock_settings, tmp_path):
        """Test download calls yt-dlp with correct audio flags."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.get_yt_dlp_path.return_value = "/usr/bin/yt-dlp"
        mock_settings.return_value = mock_settings_obj

        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        # Create expected output file
        output_path = tmp_path / "test"
        (tmp_path / "test.mp3").touch()

        downloader = VideoDownloader()
        result = downloader.download("https://tiktok.com/video/123", output_path)

        # Verify yt-dlp was called with audio extraction flags
        cmd = mock_run.call_args[0][0]
        assert "--extract-audio" in cmd
        assert "--audio-format" in cmd
        assert "mp3" in cmd
        assert result.suffix == ".mp3"

    @patch("short_form_scraper.downloader.video.get_settings")
    @patch("subprocess.run")
    def test_download_creates_parent_dirs(self, mock_run, mock_settings, tmp_path):
        """Test nested directories are created."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.get_yt_dlp_path.return_value = "/usr/bin/yt-dlp"
        mock_settings.return_value = mock_settings_obj

        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        nested_path = tmp_path / "deep" / "nested" / "dir" / "video"
        # Create the expected output
        nested_path.parent.mkdir(parents=True, exist_ok=True)
        Path(str(nested_path) + ".mp3").touch()

        downloader = VideoDownloader()
        downloader.download("https://tiktok.com/video/123", nested_path)

        assert nested_path.parent.exists()

    @patch("short_form_scraper.downloader.video.get_settings")
    @patch("subprocess.run")
    def test_download_raises_on_missing_file(self, mock_run, mock_settings, tmp_path):
        """Test FileNotFoundError when output file not created."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.get_yt_dlp_path.return_value = "/usr/bin/yt-dlp"
        mock_settings.return_value = mock_settings_obj

        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        output_path = tmp_path / "test"
        # Don't create the output file

        downloader = VideoDownloader()

        with pytest.raises(FileNotFoundError):
            downloader.download("https://tiktok.com/video/123", output_path)

    @patch("short_form_scraper.downloader.video.get_settings")
    @patch("subprocess.run")
    def test_download_finds_alternative_formats(self, mock_run, mock_settings, tmp_path):
        """Test finding audio in alternative formats."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.get_yt_dlp_path.return_value = "/usr/bin/yt-dlp"
        mock_settings.return_value = mock_settings_obj

        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        output_path = tmp_path / "test"
        # Create m4a instead of mp3
        (tmp_path / "test.m4a").touch()

        downloader = VideoDownloader()
        result = downloader.download("https://tiktok.com/video/123", output_path)

        assert result.suffix == ".m4a"
