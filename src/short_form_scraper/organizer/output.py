"""Output organization into topic folders."""

from pathlib import Path
from typing import Optional

from ..models import VideoResult


class OutputOrganizer:
    """Organize outputs into topic-based folders."""

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize organizer.

        Args:
            output_dir: Custom output directory. Uses settings if not provided.
        """
        if output_dir is None:
            from ..config import get_settings
            self.output_dir = get_settings().output_dir
        else:
            self.output_dir = output_dir

    def organize(self, result: VideoResult) -> dict[str, Path]:
        """Move/save files to topic folder.

        Args:
            result: VideoResult with transcript and summary.

        Returns:
            Dict mapping file type to path.
        """
        if not result.topic:
            result.topic = "uncategorized"

        topic_dir = self.output_dir / result.topic
        topic_dir.mkdir(parents=True, exist_ok=True)

        paths = {}

        # Save transcript
        if result.transcript:
            transcript_path = topic_dir / f"transcript_{result.metadata.id}.txt"
            transcript_path.write_text(result.transcript, encoding="utf-8")
            paths["transcript"] = transcript_path

        # Save summary
        if result.summary:
            summary_path = topic_dir / f"summary_{result.metadata.id}.md"

            # Add metadata header to summary
            header = f"""---
video_id: {result.metadata.id}
title: {result.metadata.title}
url: {result.metadata.url}
duration: {result.metadata.duration}s
---

"""
            full_content = header + result.summary
            summary_path.write_text(full_content, encoding="utf-8")
            paths["summary"] = summary_path

        # Move audio if exists
        if result.audio_path and result.audio_path.exists():
            audio_dest = topic_dir / f"audio_{result.metadata.id}{result.audio_path.suffix}"
            result.audio_path.rename(audio_dest)
            paths["audio"] = audio_dest

        return paths

    def create_index(self) -> Path:
        """Create an index file listing all summaries.

        Returns:
            Path to the index file.
        """
        index_content = ["# Video Summaries Index\n"]

        for topic_dir in sorted(self.output_dir.iterdir()):
            if not topic_dir.is_dir():
                continue

            index_content.append(f"\n## {topic_dir.name.replace('-', ' ').title()}\n")

            for summary_file in sorted(topic_dir.glob("summary_*.md")):
                # Read first few lines to get title
                content = summary_file.read_text(encoding="utf-8")
                lines = content.split("\n")

                title = "Untitled"
                for line in lines:
                    if line.startswith("title:"):
                        title = line.split(":", 1)[1].strip()
                        break

                rel_path = summary_file.relative_to(self.output_dir)
                index_content.append(f"- [{title}]({rel_path})")

        index_path = self.output_dir / "INDEX.md"
        index_path.write_text("\n".join(index_content), encoding="utf-8")

        return index_path
