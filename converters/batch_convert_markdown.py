#!/usr/bin/env python3
import os
import logging
from pathlib import Path
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)
from rich.console import Console
from rich.logging import RichHandler
from datetime import datetime
import sys
from markdown_to_pdf import convert_markdown_to_pdf


class BatchMarkdownConverter:
    def __init__(self, input_dir: str):
        """Initialize the batch converter with input directory."""
        self.input_dir = Path(input_dir)
        self.output_dir = self.input_dir / "pdf_output"

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)

        # Setup rich logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)],
        )
        self.logger = logging.getLogger("batch_converter")
        self.console = Console()

    def get_markdown_files(self) -> list:
        """Get list of all Markdown files in the input directory."""
        return list(self.input_dir.glob("*.md"))

    def convert_single_markdown(self, md_path: Path, progress) -> bool:
        """Convert a single Markdown file to PDF."""
        try:
            # Create unique output filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"{md_path.stem}_{timestamp}.pdf"

            task_id = progress.add_task(
                f"[cyan]Converting {md_path.name}...", total=100
            )

            # Run the conversion
            self.logger.info(f"Converting: {md_path.name}")
            convert_markdown_to_pdf(str(md_path), str(output_path))

            progress.update(task_id, completed=100, visible=False)
            return True

        except Exception as e:
            self.logger.error(f"Error converting {md_path.name}: {str(e)}")
            progress.update(task_id, completed=100, visible=False)
            return False

    def process_all_markdowns(self):
        """Process all Markdown files in the input directory."""
        md_files = self.get_markdown_files()

        if not md_files:
            self.logger.info("No Markdown files found in the input directory.")
            return

        self.logger.info(f"Found {len(md_files)} Markdown files to convert.")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
            console=self.console,
        ) as progress:
            # Add overall progress bar
            overall_task = progress.add_task(
                "[magenta]Converting all Markdown files...", total=len(md_files)
            )

            # Process each Markdown file
            successful = 0
            failed = 0

            for md_file in md_files:
                if self.convert_single_markdown(md_file, progress):
                    successful += 1
                else:
                    failed += 1
                progress.update(overall_task, advance=1)

            # Print summary
            self.logger.info("\nConversion Summary:")
            self.logger.info(f"Successfully converted: {successful}")
            self.logger.info(f"Failed conversions: {failed}")
            self.logger.info(f"Output directory: {self.output_dir}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Batch convert Markdown files to PDF")
    parser.add_argument("input_dir", help="Directory containing Markdown files")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: Directory '{args.input_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    converter = BatchMarkdownConverter(args.input_dir)
    converter.process_all_markdowns()


if __name__ == "__main__":
    main()
