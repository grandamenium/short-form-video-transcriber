"""Unit tests for Claude summarizer."""

from unittest.mock import MagicMock, patch

import pytest

from short_form_scraper.models import VideoMetadata
from short_form_scraper.summarizer.claude import ClaudeSummarizer


class TestClaudeSummarizer:
    """Tests for ClaudeSummarizer class."""

    @patch("short_form_scraper.summarizer.claude.get_settings")
    @patch("anthropic.Anthropic")
    def test_summarize_extracts_topic(self, mock_anthropic, mock_settings, sample_metadata):
        """Test topic extraction from Claude response."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.anthropic_api_key = "test-key"
        mock_settings_obj.claude_model = "claude-sonnet-4-20250514"
        mock_settings.return_value = mock_settings_obj

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text="TOPIC: agentic-engineering-tips\n\n## Summary\nTest summary about engineering."
            )
        ]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        summarizer = ClaudeSummarizer()
        topic, summary = summarizer.summarize("transcript text here", sample_metadata)

        assert topic == "agentic-engineering-tips"
        assert "Summary" in summary

    @patch("short_form_scraper.summarizer.claude.get_settings")
    @patch("anthropic.Anthropic")
    def test_extract_topic_cleans_input(self, mock_anthropic, mock_settings):
        """Test topic extraction cleans and normalizes input."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.anthropic_api_key = "test-key"
        mock_settings_obj.claude_model = "claude-sonnet-4-20250514"
        mock_settings.return_value = mock_settings_obj

        summarizer = ClaudeSummarizer()

        # Test various formats
        test_cases = [
            ("TOPIC: My Topic Here", "my-topic-here"),
            ("TOPIC: already-kebab-case", "already-kebab-case"),
            ("TOPIC:   extra  spaces  ", "extra-spaces"),
            ("topic: lowercase", "lowercase"),
            ("TOPIC: With--Double--Dashes", "with-double-dashes"),
            ("TOPIC: Special!@#Chars", "specialchars"),
        ]

        for input_text, expected in test_cases:
            result = summarizer._extract_topic(input_text)
            assert result == expected, f"Failed for input: {input_text}"

    @patch("short_form_scraper.summarizer.claude.get_settings")
    @patch("anthropic.Anthropic")
    def test_extract_topic_fallback(self, mock_anthropic, mock_settings):
        """Test fallback to 'uncategorized' when no topic found."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.anthropic_api_key = "test-key"
        mock_settings_obj.claude_model = "claude-sonnet-4-20250514"
        mock_settings.return_value = mock_settings_obj

        summarizer = ClaudeSummarizer()

        # No TOPIC line
        result = summarizer._extract_topic("Just some text without a topic line")
        assert result == "uncategorized"

        # Empty TOPIC
        result = summarizer._extract_topic("TOPIC: \n\nMore content")
        assert result == "uncategorized"

    @patch("short_form_scraper.summarizer.claude.get_settings")
    @patch("anthropic.Anthropic")
    def test_summarize_includes_metadata_in_prompt(
        self, mock_anthropic, mock_settings, sample_metadata
    ):
        """Test that video metadata is included in the prompt."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.anthropic_api_key = "test-key"
        mock_settings_obj.claude_model = "claude-sonnet-4-20250514"
        mock_settings.return_value = mock_settings_obj

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="TOPIC: test\n\n## Summary\nTest")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        summarizer = ClaudeSummarizer()
        summarizer.summarize("transcript", sample_metadata)

        # Check the message content
        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs["messages"]
        user_content = messages[0]["content"]

        assert sample_metadata.title in user_content
        assert str(sample_metadata.duration) in user_content

    @patch("short_form_scraper.summarizer.claude.get_settings")
    @patch("anthropic.Anthropic")
    def test_batch_summarize(self, mock_anthropic, mock_settings, sample_metadata):
        """Test batch summarization of multiple transcripts."""
        mock_settings_obj = MagicMock()
        mock_settings_obj.anthropic_api_key = "test-key"
        mock_settings_obj.claude_model = "claude-sonnet-4-20250514"
        mock_settings.return_value = mock_settings_obj

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="TOPIC: batch-test\n\n## Summary\nTest")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        summarizer = ClaudeSummarizer()

        items = [
            ("transcript 1", sample_metadata),
            ("transcript 2", sample_metadata),
        ]

        results = summarizer.batch_summarize(items)

        assert len(results) == 2
        assert all(topic == "batch-test" for topic, _ in results)
