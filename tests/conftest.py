"""Shared pytest fixtures."""

import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from short_form_scraper.models import VideoMetadata


@pytest.fixture
def mock_settings(tmp_path, monkeypatch):
    """Provide test settings with temp directories."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "output"))
    monkeypatch.setenv("STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("WHISPER_MODEL", "tiny")

    # Clear cached settings
    from short_form_scraper.config import get_settings

    get_settings.cache_clear()

    yield

    # Clear again after test
    get_settings.cache_clear()


@pytest.fixture
def sample_metadata():
    """Sample video metadata for testing."""
    return VideoMetadata(
        id="7597629199486029070",
        url="https://www.tiktok.com/@agentic.james/video/7597629199486029070",
        title="Top 3 tips to become an agentic engineer!",
        description="1) 90% effort in planning phase...",
        duration=76,
        timestamp=datetime(2024, 6, 15, 12, 0, 0),
        view_count=477,
        like_count=27,
    )


@pytest.fixture
def sample_transcript():
    """Sample transcript for testing."""
    return """Today I want to share three tips for becoming an agentic engineer.
First, spend 90% of your effort in the planning phase.
Second, set up your project in an agent-centric way.
Third, always include validation and testing loops.
These three things will dramatically improve your success rate with AI coding assistants."""


@pytest.fixture
def sample_yt_dlp_json():
    """Sample yt-dlp JSON output."""
    return {
        "id": "7597629199486029070",
        "webpage_url": "https://www.tiktok.com/@agentic.james/video/7597629199486029070",
        "title": "Top 3 tips to become an agentic engineer!",
        "description": "1) 90% effort in planning phase...",
        "duration": 76,
        "timestamp": 1718452800,
        "view_count": 477,
        "like_count": 27,
    }


@pytest.fixture
def mock_yt_dlp_path():
    """Mock yt-dlp path."""
    with patch("shutil.which", return_value="/usr/local/bin/yt-dlp"):
        yield "/usr/local/bin/yt-dlp"


@pytest.fixture
def temp_audio_file(tmp_path):
    """Create a temporary audio file for testing."""
    audio_path = tmp_path / "test_audio.mp3"
    # Create a minimal valid file (actual audio not needed for unit tests)
    audio_path.write_bytes(b"fake audio content")
    return audio_path
