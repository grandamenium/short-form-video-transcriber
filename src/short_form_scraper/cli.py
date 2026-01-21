"""Command-line interface for the video transcriber."""

import argparse
import sys
from pathlib import Path

from .config import Settings
from .pipeline.runner import PipelineRunner


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Scrape, transcribe, and summarize short-form videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all videos from a TikTok profile
  scrape-videos "https://www.tiktok.com/@username"

  # Process only the first 5 videos
  scrape-videos "https://www.tiktok.com/@username" --limit 5

  # Test with a single video
  scrape-videos "https://www.tiktok.com/@username" --single "https://www.tiktok.com/@username/video/123456"

  # Use a specific whisper model
  scrape-videos "https://www.tiktok.com/@username" --whisper-model large
        """,
    )

    parser.add_argument(
        "profile_url",
        help="TikTok or Instagram profile URL",
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of videos to process",
    )

    parser.add_argument(
        "--single",
        metavar="URL",
        help="Process only this single video URL (for testing)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory (default: ./output)",
    )

    parser.add_argument(
        "--whisper-model",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)",
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset processing state and reprocess all videos",
    )

    parser.add_argument(
        "--no-skip",
        action="store_true",
        help="Don't skip already processed videos",
    )

    args = parser.parse_args()

    # Build settings overrides
    settings_kwargs = {}

    if args.output:
        settings_kwargs["output_dir"] = args.output

    if args.whisper_model:
        settings_kwargs["whisper_model"] = args.whisper_model

    if args.no_skip:
        settings_kwargs["skip_existing"] = False

    # Create settings
    try:
        if settings_kwargs:
            settings = Settings(**settings_kwargs)
        else:
            settings = Settings()
    except Exception as e:
        print(f"Error loading settings: {e}")
        print("Make sure you have a .env file with ANTHROPIC_API_KEY set")
        sys.exit(1)

    # Create and run pipeline
    runner = PipelineRunner(args.profile_url, settings)

    if args.reset:
        runner.reset_state()

    results = runner.run(limit=args.limit, single_video_url=args.single)

    # Print summary
    if results:
        success = sum(1 for r in results if r.status.value == "complete")
        failed = sum(1 for r in results if r.status.value == "failed")
        print(f"\n{'='*50}")
        print(f"Complete: {success} processed, {failed} failed")

        if failed > 0:
            print("\nFailed videos:")
            for r in results:
                if r.status.value == "failed":
                    print(f"  - {r.metadata.id}: {r.error}")
    else:
        print("\nNo new videos to process (all already done)")


if __name__ == "__main__":
    main()
