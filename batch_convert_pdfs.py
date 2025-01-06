#!/usr/bin/env python3
import os
import glob
import logging
import subprocess
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


class BatchPDFConverter:
    def __init__(self, input_dir: str):
        """Initialize the batch converter with input directory."""
        self.input_dir = Path(input_dir)
        self.temp_dir = self.input_dir / "temp"

        # Create temp directory if it doesn't exist
        self.temp_dir.mkdir(exist_ok=True)

        # Setup rich logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)],
        )
        self.logger = logging.getLogger("batch_converter")
        self.console = Console()

    def get_pdf_files(self) -> list:
        """Get list of all PDF files in the input directory."""
        return list(self.input_dir.glob("*.pdf"))

    def convert_single_pdf(self, pdf_path: Path, progress) -> bool:
        """Convert a single PDF file to markdown."""
        try:
            # Create unique output filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.temp_dir / f"{pdf_path.stem}_{timestamp}.md"

            # Prepare and execute the conversion command
            command = [
                "python",
                "pdf_to_markdown.py",
                str(pdf_path),
                "-o",
                str(output_path),
            ]

            task_id = progress.add_task(
                f"[cyan]Converting {pdf_path.name}...", total=100
            )

            # Run the conversion
            self.logger.info(f"Converting: {pdf_path.name}")
            result = subprocess.run(command, capture_output=True, text=True, check=True)

            progress.update(task_id, completed=100, visible=False)
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error converting {pdf_path.name}: {e.stderr}")
            progress.update(task_id, completed=100, visible=False)
            return False

        except Exception as e:
            self.logger.error(f"Unexpected error converting {pdf_path.name}: {e}")
            progress.update(task_id, completed=100, visible=False)
            return False

    def process_all_pdfs(self):
        """Process all PDF files in the input directory."""
        pdf_files = self.get_pdf_files()

        if not pdf_files:
            self.logger.info("No PDF files found in the input directory.")
            return

        self.logger.info(f"Found {len(pdf_files)} PDF files to convert.")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
            console=self.console,
        ) as progress:
            # Add overall progress bar
            overall_task = progress.add_task(
                "[magenta]Converting all PDFs...", total=len(pdf_files)
            )

            # Process each PDF file
            successful = 0
            failed = 0

            for pdf_file in pdf_files:
                if self.convert_single_pdf(pdf_file, progress):
                    successful += 1
                else:
                    failed += 1
                progress.update(overall_task, advance=1)

            # Print summary
            self.logger.info("\nConversion Summary:")
            self.logger.info(f"Successfully converted: {successful}")
            self.logger.info(f"Failed conversions: {failed}")
            self.logger.info(f"Output directory: {self.temp_dir}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Batch convert PDF files to Markdown")
    parser.add_argument("input_dir", help="Directory containing PDF files")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: Directory '{args.input_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    converter = BatchPDFConverter(args.input_dir)
    converter.process_all_pdfs()


if __name__ == "__main__":
    main()
