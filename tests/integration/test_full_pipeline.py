"""Integration tests for full pipeline with multiple videos.

These tests are marked as 'slow' and require a real API key.
Run with: pytest -m slow
"""

import os
from pathlib import Path

import pytest

from short_form_scraper.config import Settings
from short_form_scraper.pipeline.runner import PipelineRunner


# Skip if no API key available
pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set - integration tests require real API key",
    ),
]


@pytest.mark.integration
class TestFullPipeline:
    """Test full pipeline with multiple videos."""

    TEST_PROFILE = "https://www.tiktok.com/@agentic.james"

    @pytest.fixture
    def pipeline_settings(self, tmp_path):
        """Create settings with temp directories."""
        return Settings(
            anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
            output_dir=tmp_path / "output",
            state_dir=tmp_path / "state",
            whisper_model="tiny",
            skip_existing=True,
        )

    def test_processes_multiple_videos(self, pipeline_settings, tmp_path):
        """Test processing 3 videos."""
        runner = PipelineRunner(self.TEST_PROFILE, pipeline_settings)

        results = runner.run(limit=3)

        # Should have attempted 3 videos
        assert len(results) == 3

        # At least 2 should succeed (allow one failure for network issues)
        success_count = sum(1 for r in results if r.status.value == "complete")
        assert success_count >= 2, f"Only {success_count}/3 videos succeeded"

        # Check that topics are organized
        output_dir = tmp_path / "output"
        topic_dirs = [d for d in output_dir.iterdir() if d.is_dir()]
        assert len(topic_dirs) >= 1, "No topic directories created"

        # Check index was created
        index_file = output_dir / "INDEX.md"
        assert index_file.exists(), "Index file not created"

        print(f"\n{'='*50}")
        print(f"Processed {len(results)} videos")
        print(f"Success: {success_count}")
        print(f"Topics created: {[d.name for d in topic_dirs]}")
        print(f"{'='*50}")

    def test_handles_failures_gracefully(self, pipeline_settings):
        """Test that pipeline continues after individual video failures."""
        runner = PipelineRunner(self.TEST_PROFILE, pipeline_settings)

        # Process videos - even if some fail, others should succeed
        results = runner.run(limit=2)

        # Verify we got results for all attempted videos
        assert len(results) == 2

        # Check that failures have error messages
        for result in results:
            if result.status.value == "failed":
                assert result.error is not None
                assert len(result.error) > 0

    def test_different_topics_organized_separately(self, pipeline_settings, tmp_path):
        """Test that videos with different topics go to different folders."""
        runner = PipelineRunner(self.TEST_PROFILE, pipeline_settings)

        results = runner.run(limit=5)

        # Get unique topics from successful results
        topics = set(
            r.topic for r in results if r.status.value == "complete" and r.topic
        )

        if len(topics) > 1:
            # If we have multiple topics, verify they're in different folders
            output_dir = tmp_path / "output"
            for topic in topics:
                topic_dir = output_dir / topic
                assert topic_dir.exists(), f"Topic directory missing: {topic}"
                assert topic_dir.is_dir()

            print(f"Topics created: {topics}")
