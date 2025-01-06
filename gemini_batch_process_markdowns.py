#!/usr/bin/env python3
import os
import glob
import shutil
import logging
import subprocess
from pathlib import Path
from datetime import datetime
import time
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)
from rich.console import Console
from rich.logging import RichHandler
import sys


class BatchMarkdownProcessor:
    def __init__(self, input_dir: str):
        """Initialize the batch processor with directory paths."""
        self.input_dir = Path(input_dir)
        self.done_dir = self.input_dir / "done"
        self.output_dir = self.input_dir / "output"

        # Create required directories if they don't exist
        for directory in [self.done_dir, self.output_dir]:
            directory.mkdir(exist_ok=True)

        # Setup rich logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)],
        )
        self.logger = logging.getLogger("markdown_processor")
        self.console = Console()

    def get_markdown_files(self) -> list:
        """Get list of all markdown files in the input directory."""
        return list(self.input_dir.glob("*.md"))

    def process_single_markdown(
        self, markdown_path: Path, prompt_path: Path, progress
    ) -> bool:
        """Process a single markdown file using Gemini."""
        try:
            # Create output filename
            output_filename = f"summary_{markdown_path.stem}.md"
            output_path = self.output_dir / output_filename
            done_path = self.done_dir / markdown_path.name

            # Prepare and execute the Gemini processing command
            command = [
                "python",
                "gemini_processor.py",
                str(markdown_path),
                "--prompt",
                str(prompt_path),
                "-o",
                str(output_path),
            ]

            task_id = progress.add_task(
                f"[cyan]Processing {markdown_path.name}...", total=100
            )

            # Run the processing
            self.logger.info(f"Processing: {markdown_path.name}")
            result = subprocess.run(command, capture_output=True, text=True, check=True)

            # Move processed file to done directory
            shutil.move(str(markdown_path), str(done_path))

            progress.update(task_id, completed=100, visible=False)
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error processing {markdown_path.name}: {e.stderr}")
            progress.update(task_id, completed=100, visible=False)
            return False

        except Exception as e:
            self.logger.error(f"Unexpected error processing {markdown_path.name}: {e}")
            progress.update(task_id, completed=100, visible=False)
            return False

    def process_all_markdowns(self, prompt_path: str):
        """Process all markdown files in the input directory."""
        markdown_files = self.get_markdown_files()

        if not markdown_files:
            self.logger.info("No markdown files found in the input directory.")
            return

        self.logger.info(f"Found {len(markdown_files)} markdown files to process.")

        # Verify prompt file exists
        prompt_path = Path(prompt_path)
        if not prompt_path.exists():
            self.logger.error(f"Prompt file not found: {prompt_path}")
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
            console=self.console,
        ) as progress:
            # Add overall progress bar
            overall_task = progress.add_task(
                "[magenta]Processing all markdown files...", total=len(markdown_files)
            )

            # Process each markdown file
            successful = 0
            failed = 0

            for md_file in markdown_files:
                if self.process_single_markdown(md_file, prompt_path, progress):
                    successful += 1
                else:
                    failed += 1
                progress.update(overall_task, advance=1)
                time.sleep(15)

            # Print summary
            self.logger.info("\nProcessing Summary:")
            self.logger.info(f"Successfully processed: {successful}")
            self.logger.info(f"Failed processing: {failed}")
            self.logger.info(f"Processed files moved to: {self.done_dir}")
            self.logger.info(f"Summaries saved to: {self.output_dir}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch process markdown files using Gemini"
    )
    parser.add_argument("input_dir", help="Directory containing markdown files")
    parser.add_argument(
        "--prompt",
        default="gemini_prompt.md",
        help="Path to prompt markdown file (default: gemini_prompt.md)",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: Directory '{args.input_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    processor = BatchMarkdownProcessor(args.input_dir)
    processor.process_all_markdowns(args.prompt)


if __name__ == "__main__":
    main()
