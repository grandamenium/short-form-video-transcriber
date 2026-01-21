"""Data models for the video processing pipeline."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class ProcessingStatus(str, Enum):
    """Status of video processing."""

    PENDING = "pending"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    SUMMARIZING = "summarizing"
    ORGANIZING = "organizing"
    COMPLETE = "complete"
    FAILED = "failed"


class VideoMetadata(BaseModel):
    """Metadata for a video from the platform."""

    id: str
    url: str
    title: str = ""
    description: str = ""
    duration: int = 0
    timestamp: Optional[datetime] = None
    view_count: int = 0
    like_count: int = 0

    model_config = {"frozen": False}


class VideoResult(BaseModel):
    """Result of processing a single video."""

    metadata: VideoMetadata
    audio_path: Optional[Path] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    topic: Optional[str] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    error: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}


class PipelineProgress(BaseModel):
    """Progress tracking for the pipeline."""

    total_videos: int
    current_index: int
    phase: str
    processed_ids: list[str]
