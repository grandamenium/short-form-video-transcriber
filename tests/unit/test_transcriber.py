"""Unit tests for Whisper transcriber."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from short_form_scraper.transcriber.whisper import WhisperTranscriber


class TestWhisperTranscriber:
    """Tests for WhisperTranscriber class."""

    @patch("short_form_scraper.transcriber.whisper.get_settings")
    @patch("whisper.load_model")
    def test_lazy_model_loading(self, mock_load, mock_settings):
        """Test model loads only on first access."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.whisper_model = "base"
        mock_settings.return_value = mock_settings_obj

        transcriber = WhisperTranscriber()

        # Model should not be loaded yet
        assert transcriber._model is None
        mock_load.assert_not_called()

        # Access model property
        _ = transcriber.model

        # Now it should be loaded
        mock_load.assert_called_once_with("base")

    @patch("short_form_scraper.transcriber.whisper.get_settings")
    @patch("whisper.load_model")
    def test_transcribe_returns_text(self, mock_load, mock_settings, tmp_path):
        """Test transcribe returns text from whisper result."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.whisper_model = "base"
        mock_settings.return_value = mock_settings_obj

        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "  Hello world  "}
        mock_load.return_value = mock_model

        # Create a test audio file
        audio_path = tmp_path / "test.mp3"
        audio_path.touch()

        transcriber = WhisperTranscriber()
        result = transcriber.transcribe(audio_path)

        assert result == "Hello world"  # Should be stripped

    @patch("short_form_scraper.transcriber.whisper.get_settings")
    def test_transcribe_raises_on_missing_file(self, mock_settings):
        """Test FileNotFoundError for missing audio file."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.whisper_model = "base"
        mock_settings.return_value = mock_settings_obj

        transcriber = WhisperTranscriber()

        with pytest.raises(FileNotFoundError):
            transcriber.transcribe(Path("/nonexistent/audio.mp3"))

    @patch("short_form_scraper.transcriber.whisper.get_settings")
    @patch("whisper.load_model")
    def test_transcribe_with_timestamps(self, mock_load, mock_settings, tmp_path):
        """Test transcription with segment timestamps."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.whisper_model = "base"
        mock_settings.return_value = mock_settings_obj

        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "Hello world",
            "segments": [
                {"start": 0.0, "end": 2.0, "text": "  Hello  "},
                {"start": 2.0, "end": 4.0, "text": "  world  "},
            ],
        }
        mock_load.return_value = mock_model

        audio_path = tmp_path / "test.mp3"
        audio_path.touch()

        transcriber = WhisperTranscriber()
        segments = transcriber.transcribe_with_timestamps(audio_path)

        assert len(segments) == 2
        assert segments[0]["text"] == "Hello"  # Stripped
        assert segments[0]["start"] == 0.0
        assert segments[1]["text"] == "world"

    @patch("short_form_scraper.transcriber.whisper.get_settings")
    @patch("whisper.load_model")
    def test_model_cached(self, mock_load, mock_settings):
        """Test model is cached after first load."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.whisper_model = "base"
        mock_settings.return_value = mock_settings_obj

        mock_model = MagicMock()
        mock_load.return_value = mock_model

        transcriber = WhisperTranscriber()

        # Access model multiple times
        _ = transcriber.model
        _ = transcriber.model
        _ = transcriber.model

        # Should only load once
        mock_load.assert_called_once()
