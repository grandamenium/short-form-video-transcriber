"""Integration test for single video processing.

This is the CRITICAL test to run before processing the full profile.
It validates the entire pipeline works end-to-end on one video.
"""

import os
from pathlib import Path

import pytest

from short_form_scraper.config import Settings
from short_form_scraper.pipeline.runner import PipelineRunner


# Skip if no API key available
pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - integration tests require real API key",
)


@pytest.mark.integration
class TestSingleVideo:
    """Test full pipeline on ONE video before running full scrape."""

    # Use a known video URL from the profile
    TEST_PROFILE = "https://www.tiktok.com/@agentic.james"

    @pytest.fixture
    def pipeline_settings(self, tmp_path):
        """Create settings with temp directories."""
        return Settings(
            anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
            output_dir=tmp_path / "output",
            state_dir=tmp_path / "state",
            whisper_model="tiny",  # Use tiny model for faster tests
            skip_existing=True,
        )

    def test_single_video_pipeline_with_first_video(self, pipeline_settings, tmp_path):
        """Full E2E test - fetch first video from profile and process it."""
        runner = PipelineRunner(self.TEST_PROFILE, pipeline_settings)

        # Process just 1 video
        results = runner.run(limit=1)

        assert len(results) == 1
        result = results[0]

        # Verify all stages completed
        assert result.status.value == "complete", f"Pipeline failed: {result.error}"

        # Verify transcript exists and has content
        assert result.transcript is not None
        assert len(result.transcript) > 20, "Transcript too short"

        # Verify summary exists
        assert result.summary is not None
        assert len(result.summary) > 50, "Summary too short"

        # Verify topic was extracted
        assert result.topic is not None
        assert result.topic != "uncategorized", "Topic should be extracted"

        # Verify files exist in topic folder
        topic_dir = tmp_path / "output" / result.topic
        assert topic_dir.exists(), f"Topic directory not created: {topic_dir}"

        transcript_files = list(topic_dir.glob("transcript_*.txt"))
        assert len(transcript_files) == 1, "Transcript file not created"

        summary_files = list(topic_dir.glob("summary_*.md"))
        assert len(summary_files) == 1, "Summary file not created"

        # Verify summary has frontmatter
        summary_content = summary_files[0].read_text()
        assert "video_id:" in summary_content, "Summary missing video_id in frontmatter"

        print(f"\n{'='*50}")
        print(f"SUCCESS: Single video test passed!")
        print(f"Topic: {result.topic}")
        print(f"Transcript length: {len(result.transcript)} chars")
        print(f"Output: {topic_dir}")
        print(f"{'='*50}")


@pytest.mark.integration
class TestPipelineIdempotency:
    """Test that pipeline correctly skips already processed videos."""

    TEST_PROFILE = "https://www.tiktok.com/@agentic.james"

    @pytest.fixture
    def pipeline_settings(self, tmp_path):
        """Create settings with temp directories."""
        return Settings(
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", "test-key"),
            output_dir=tmp_path / "output",
            state_dir=tmp_path / "state",
            whisper_model="tiny",
            skip_existing=True,
        )

    @pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set",
    )
    def test_idempotency_skips_processed(self, pipeline_settings, tmp_path):
        """Test that re-running skips already processed videos."""
        runner = PipelineRunner(self.TEST_PROFILE, pipeline_settings)

        # First run - process 1 video
        results1 = runner.run(limit=1)
        assert len(results1) == 1
        assert results1[0].status.value == "complete"

        first_video_id = results1[0].metadata.id

        # Second run - should skip the same video
        runner2 = PipelineRunner(self.TEST_PROFILE, pipeline_settings)
        results2 = runner2.run(limit=1)

        # Second run should return empty (all skipped)
        assert len(results2) == 0, "Should skip already processed video"

        # Verify processed.json contains the video ID
        processed_file = tmp_path / "state" / "processed.json"
        assert processed_file.exists()
        import json
        processed_ids = json.loads(processed_file.read_text())
        assert first_video_id in processed_ids

    def test_reset_state_allows_reprocessing(self, pipeline_settings, tmp_path, monkeypatch):
        """Test that reset_state() clears processing history."""
        # Mock the actual processing to avoid API calls
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")

        runner = PipelineRunner(self.TEST_PROFILE, pipeline_settings)

        # Manually add a processed ID
        pipeline_settings.state_dir.mkdir(parents=True, exist_ok=True)
        processed_file = pipeline_settings.state_dir / "processed.json"
        processed_file.write_text('["test-video-id"]')

        assert processed_file.exists()

        # Reset state
        runner.reset_state()

        assert not processed_file.exists(), "Processed file should be deleted"
