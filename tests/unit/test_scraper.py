"""Unit tests for TikTok scraper."""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from short_form_scraper.scraper.tiktok import TikTokScraper


class TestTikTokScraper:
    """Tests for TikTokScraper class."""

    @patch("short_form_scraper.scraper.tiktok.get_settings")
    @patch("subprocess.Popen")
    def test_get_video_urls_parses_json(
        self, mock_popen, mock_settings, sample_yt_dlp_json
    ):
        """Test JSON parsing from yt-dlp output."""
        # Setup mock settings
        mock_settings_obj = MagicMock()
        mock_settings_obj.get_yt_dlp_path.return_value = "/usr/bin/yt-dlp"
        mock_settings.return_value = mock_settings_obj

        # Setup mock process
        mock_proc = MagicMock()
        mock_proc.stdout = iter([json.dumps(sample_yt_dlp_json) + "\n"])
        mock_proc.wait.return_value = 0
        mock_popen.return_value = mock_proc

        scraper = TikTokScraper("https://tiktok.com/@test")
        videos = list(scraper.get_video_urls())

        assert len(videos) == 1
        assert videos[0].id == "7597629199486029070"
        assert videos[0].duration == 76
        assert videos[0].title == "Top 3 tips to become an agentic engineer!"

    @patch("short_form_scraper.scraper.tiktok.get_settings")
    @patch("subprocess.Popen")
    def test_get_video_urls_with_limit(self, mock_popen, mock_settings):
        """Test limit parameter adds --playlist-items."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.get_yt_dlp_path.return_value = "/usr/bin/yt-dlp"
        mock_settings.return_value = mock_settings_obj

        mock_proc = MagicMock()
        mock_proc.stdout = iter([])
        mock_proc.wait.return_value = 0
        mock_popen.return_value = mock_proc

        scraper = TikTokScraper("https://tiktok.com/@test")
        list(scraper.get_video_urls(limit=5))

        # Check that --playlist-items was passed
        call_args = mock_popen.call_args[0][0]
        assert "--playlist-items" in call_args
        assert "1:5" in call_args

    @patch("short_form_scraper.scraper.tiktok.get_settings")
    @patch("subprocess.Popen")
    def test_handles_empty_output(self, mock_popen, mock_settings):
        """Test handling of empty yt-dlp output."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.get_yt_dlp_path.return_value = "/usr/bin/yt-dlp"
        mock_settings.return_value = mock_settings_obj

        mock_proc = MagicMock()
        mock_proc.stdout = iter([])
        mock_proc.wait.return_value = 0
        mock_popen.return_value = mock_proc

        scraper = TikTokScraper("https://tiktok.com/@test")
        videos = list(scraper.get_video_urls())

        assert len(videos) == 0

    @patch("short_form_scraper.scraper.tiktok.get_settings")
    @patch("subprocess.Popen")
    def test_handles_invalid_json(self, mock_popen, mock_settings):
        """Test handling of invalid JSON lines."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.get_yt_dlp_path.return_value = "/usr/bin/yt-dlp"
        mock_settings.return_value = mock_settings_obj

        mock_proc = MagicMock()
        mock_proc.stdout = iter(["invalid json\n", "\n", "also invalid\n"])
        mock_proc.wait.return_value = 0
        mock_popen.return_value = mock_proc

        scraper = TikTokScraper("https://tiktok.com/@test")
        videos = list(scraper.get_video_urls())

        assert len(videos) == 0

    @patch("short_form_scraper.scraper.tiktok.get_settings")
    @patch("subprocess.run")
    def test_get_single_video_metadata(
        self, mock_run, mock_settings, sample_yt_dlp_json
    ):
        """Test fetching metadata for a single video."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.get_yt_dlp_path.return_value = "/usr/bin/yt-dlp"
        mock_settings.return_value = mock_settings_obj

        mock_run.return_value = MagicMock(
            stdout=json.dumps(sample_yt_dlp_json),
            returncode=0,
        )

        scraper = TikTokScraper("https://tiktok.com/@test")
        metadata = scraper.get_single_video_metadata(
            "https://tiktok.com/@test/video/123"
        )

        assert metadata.id == "7597629199486029070"
        assert "--no-download" in mock_run.call_args[0][0]

    def test_parse_metadata_handles_missing_fields(self):
        """Test parsing metadata with missing optional fields."""
        scraper = TikTokScraper.__new__(TikTokScraper)

        minimal_data = {
            "id": "123",
            "url": "https://example.com",
        }

        metadata = scraper._parse_metadata(minimal_data)

        assert metadata.id == "123"
        assert metadata.url == "https://example.com"
        assert metadata.title == ""
        assert metadata.duration == 0
        assert metadata.timestamp is None
