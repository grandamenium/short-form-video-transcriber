"""Audio transcription using OpenAI Whisper."""

from pathlib import Path

import whisper

from ..config import get_settings


class WhisperTranscriber:
    """Transcribe audio using OpenAI Whisper."""

    def __init__(self):
        """Initialize transcriber."""
        self.settings = get_settings()
        self._model = None

    @property
    def model(self):
        """Lazy load whisper model."""
        if self._model is None:
            self._model = whisper.load_model(self.settings.whisper_model)
        return self._model

    def transcribe(self, audio_path: Path) -> str:
        """Transcribe audio file to text.

        Args:
            audio_path: Path to audio file.

        Returns:
            Transcribed text.

        Raises:
            FileNotFoundError: If audio file doesn't exist.
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        result = self.model.transcribe(str(audio_path))
        return result["text"].strip()

    def transcribe_with_timestamps(self, audio_path: Path) -> list[dict]:
        """Transcribe audio with segment timestamps.

        Args:
            audio_path: Path to audio file.

        Returns:
            List of segments with start, end, and text.
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        result = self.model.transcribe(str(audio_path))

        segments = []
        for segment in result.get("segments", []):
            segments.append(
                {
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip(),
                }
            )

        return segments
