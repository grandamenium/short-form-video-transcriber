"""Transcript summarization using Claude API."""

import anthropic

from ..config import get_settings
from ..models import VideoMetadata

SYSTEM_PROMPT = """You are summarizing transcripts of short-form videos about software engineering, AI, and Claude Code tips.

Your task is to extract actionable insights and organize them clearly.

For each transcript, provide:
1. A topic name (2-4 words, kebab-case, used for folder organization)
2. A one-sentence summary
3. Key actionable tips (bullet points)

Format your response EXACTLY like this:
TOPIC: topic-name-here

## Summary
One sentence summarizing the main point of the video.

## Key Tips
- First actionable tip or insight
- Second actionable tip or insight
- Third actionable tip or insight (if applicable)

## Details
Any additional context or explanation that would be helpful.

Guidelines:
- Topic should be specific and descriptive (e.g., "agentic-engineering-mindset", "context-window-management", "prompt-engineering-basics")
- Tips should be concrete and actionable, not vague
- Keep the summary concise but informative
- If the transcript is unclear or low quality, do your best to extract value"""


class ClaudeSummarizer:
    """Summarize transcripts using Claude API."""

    def __init__(self):
        """Initialize summarizer."""
        self.settings = get_settings()

        if not self.settings.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required for summarization. "
                "Get your API key from https://console.anthropic.com/ "
                "and set it in your .env file or environment."
            )

        self.client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)

    def summarize(self, transcript: str, metadata: VideoMetadata) -> tuple[str, str]:
        """Summarize transcript and extract topic.

        Args:
            transcript: The video transcript text.
            metadata: Video metadata for context.

        Returns:
            Tuple of (topic, full_summary).
        """
        user_content = f"""Video Title: {metadata.title}
Video Description: {metadata.description}
Duration: {metadata.duration} seconds

Transcript:
{transcript}"""

        response = self.client.messages.create(
            model=self.settings.claude_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )

        text = response.content[0].text
        topic = self._extract_topic(text)

        return topic, text

    def _extract_topic(self, text: str) -> str:
        """Extract topic from response.

        Args:
            text: Claude's response text.

        Returns:
            Extracted topic or 'uncategorized'.
        """
        for line in text.split("\n"):
            line = line.strip()
            if line.upper().startswith("TOPIC:"):
                topic = line.split(":", 1)[1].strip()
                # Clean up the topic
                topic = topic.lower().replace(" ", "-")
                # Remove any non-alphanumeric chars except hyphens
                topic = "".join(c for c in topic if c.isalnum() or c == "-")
                # Remove multiple consecutive hyphens
                while "--" in topic:
                    topic = topic.replace("--", "-")
                topic = topic.strip("-")
                if topic:
                    return topic

        return "uncategorized"

    def batch_summarize(
        self, items: list[tuple[str, VideoMetadata]]
    ) -> list[tuple[str, str]]:
        """Summarize multiple transcripts.

        Args:
            items: List of (transcript, metadata) tuples.

        Returns:
            List of (topic, summary) tuples.
        """
        results = []
        for transcript, metadata in items:
            try:
                topic, summary = self.summarize(transcript, metadata)
                results.append((topic, summary))
            except Exception as e:
                results.append(("error", f"Failed to summarize: {e}"))

        return results
