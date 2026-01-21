"""Configuration management using pydantic-settings."""

import shutil
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys (optional - only required for summarization)
    anthropic_api_key: Optional[str] = None

    # Paths
    yt_dlp_path: Optional[str] = None
    output_dir: Path = Path("./output")
    state_dir: Path = Path("./state")

    # Whisper Settings
    whisper_model: str = "base"

    # Claude Settings
    claude_model: str = "claude-sonnet-4-20250514"

    # Processing
    skip_existing: bool = True

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    def get_yt_dlp_path(self) -> str:
        """Get yt-dlp path, auto-detecting if not configured."""
        if self.yt_dlp_path:
            return self.yt_dlp_path

        # Try to find yt-dlp in PATH
        yt_dlp = shutil.which("yt-dlp")
        if yt_dlp:
            return yt_dlp

        # Common locations
        common_paths = [
            "/opt/homebrew/bin/yt-dlp",
            "/usr/local/bin/yt-dlp",
            "/usr/bin/yt-dlp",
        ]
        for path in common_paths:
            if Path(path).exists():
                return path

        raise FileNotFoundError(
            "yt-dlp not found. Install it with: brew install yt-dlp or pip install yt-dlp"
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
