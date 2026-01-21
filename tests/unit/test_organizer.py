"""Unit tests for output organizer."""

from pathlib import Path

import pytest

from short_form_scraper.models import ProcessingStatus, VideoMetadata, VideoResult
from short_form_scraper.organizer.output import OutputOrganizer


class TestOutputOrganizer:
    """Tests for OutputOrganizer class."""

    def test_creates_topic_directory(self, tmp_path, sample_metadata):
        """Test topic folder is created."""
        organizer = OutputOrganizer(output_dir=tmp_path)

        result = VideoResult(
            metadata=sample_metadata,
            transcript="Test transcript",
            summary="Test summary",
            topic="my-test-topic",
            status=ProcessingStatus.COMPLETE,
        )

        organizer.organize(result)

        assert (tmp_path / "my-test-topic").exists()
        assert (tmp_path / "my-test-topic").is_dir()

    def test_saves_transcript(self, tmp_path, sample_metadata):
        """Test transcript file is written correctly."""
        organizer = OutputOrganizer(output_dir=tmp_path)

        result = VideoResult(
            metadata=sample_metadata,
            transcript="This is the transcript content.",
            summary="Summary here",
            topic="test-topic",
            status=ProcessingStatus.COMPLETE,
        )

        paths = organizer.organize(result)

        assert "transcript" in paths
        transcript_path = paths["transcript"]
        assert transcript_path.exists()
        assert transcript_path.read_text() == "This is the transcript content."
        assert transcript_path.name == f"transcript_{sample_metadata.id}.txt"

    def test_saves_summary_with_metadata(self, tmp_path, sample_metadata):
        """Test summary file includes YAML frontmatter."""
        organizer = OutputOrganizer(output_dir=tmp_path)

        result = VideoResult(
            metadata=sample_metadata,
            transcript="Transcript",
            summary="## Summary\nThis is the summary.",
            topic="test-topic",
            status=ProcessingStatus.COMPLETE,
        )

        paths = organizer.organize(result)

        assert "summary" in paths
        summary_content = paths["summary"].read_text()

        # Check frontmatter
        assert "---" in summary_content
        assert f"video_id: {sample_metadata.id}" in summary_content
        assert f"title: {sample_metadata.title}" in summary_content
        assert "## Summary" in summary_content

    def test_moves_audio_file(self, tmp_path, sample_metadata):
        """Test audio file is moved to topic folder."""
        organizer = OutputOrganizer(output_dir=tmp_path)

        # Create a source audio file
        source_audio = tmp_path / "source" / "audio.mp3"
        source_audio.parent.mkdir(parents=True)
        source_audio.write_text("fake audio")

        result = VideoResult(
            metadata=sample_metadata,
            audio_path=source_audio,
            transcript="Transcript",
            summary="Summary",
            topic="test-topic",
            status=ProcessingStatus.COMPLETE,
        )

        paths = organizer.organize(result)

        assert "audio" in paths
        assert paths["audio"].exists()
        assert not source_audio.exists()  # Should be moved, not copied

    def test_uses_uncategorized_for_missing_topic(self, tmp_path, sample_metadata):
        """Test fallback to 'uncategorized' when topic is None."""
        organizer = OutputOrganizer(output_dir=tmp_path)

        result = VideoResult(
            metadata=sample_metadata,
            transcript="Transcript",
            summary="Summary",
            topic=None,  # No topic
            status=ProcessingStatus.COMPLETE,
        )

        organizer.organize(result)

        assert (tmp_path / "uncategorized").exists()

    def test_create_index(self, tmp_path, sample_metadata):
        """Test index file creation."""
        organizer = OutputOrganizer(output_dir=tmp_path)

        # Create some test content
        result = VideoResult(
            metadata=sample_metadata,
            transcript="Transcript",
            summary="## Summary\nTest summary",
            topic="test-topic",
            status=ProcessingStatus.COMPLETE,
        )
        organizer.organize(result)

        # Create index
        index_path = organizer.create_index()

        assert index_path.exists()
        assert index_path.name == "INDEX.md"

        content = index_path.read_text()
        assert "# Video Summaries Index" in content
        assert "Test Topic" in content  # Topic name should be title-cased

    def test_handles_missing_transcript(self, tmp_path, sample_metadata):
        """Test handling when transcript is None."""
        organizer = OutputOrganizer(output_dir=tmp_path)

        result = VideoResult(
            metadata=sample_metadata,
            transcript=None,
            summary="Summary only",
            topic="test-topic",
            status=ProcessingStatus.COMPLETE,
        )

        paths = organizer.organize(result)

        assert "transcript" not in paths
        assert "summary" in paths
