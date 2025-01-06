import os
import glob
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import logging
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)
from rich.console import Console
from rich.logging import RichHandler


class PDFProcessor:
    def __init__(self, base_dir):
        """Initialize the processor with directory paths and logging."""
        self.base_dir = Path(base_dir)
        self.done_dir = self.base_dir / "done"
        self.output_dir = self.base_dir / "output"
        self.temp_dir = self.base_dir / "temp"

        # Create required directories
        for directory in [self.done_dir, self.output_dir, self.temp_dir]:
            directory.mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)],
        )
        self.logger = logging.getLogger("pdf_processor")
        self.console = Console()

    def get_pdf_files(self):
        """Get list of PDF files in the base directory."""
        return list(self.base_dir.glob("*.pdf"))

    def execute_command(self, command, description):
        """Execute a command and handle its output."""
        try:
            self.logger.info(f"Executing: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error in {description}: {e}")
            self.logger.error(f"Command output: {e.output}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error in {description}: {e}")
            return False

    def process_single_pdf(self, pdf_file, progress):
        """Process a single PDF file through the conversion pipeline."""
        try:
            file_name = pdf_file.stem

            # Create unique temporary and output files
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_markdown = self.temp_dir / f"{file_name}_{timestamp}.md"
            final_output = self.output_dir / f"{file_name}_summary_{timestamp}.md"

            # Step 1: Convert PDF to Markdown
            task_id = progress.add_task(
                f"[cyan]Converting {pdf_file.name} to Markdown...", total=100
            )

            success = self.execute_command(
                [
                    "python",
                    "pdf_to_markdown.py",
                    str(pdf_file),
                    "-o",
                    str(temp_markdown),
                ],
                "PDF to Markdown conversion",
            )

            if not success:
                progress.update(task_id, completed=100, visible=False)
                return False

            progress.update(task_id, completed=100, visible=False)

            # Step 2: Process with Gemini
            task_id = progress.add_task(
                f"[green]Processing {file_name} with Gemini...", total=100
            )

            success = self.execute_command(
                [
                    "python",
                    "gemini_processor.py",
                    str(temp_markdown),
                    "--prompt",
                    "gemini_prompt.md",
                    "-o",
                    str(final_output),
                ],
                "Gemini processing",
            )

            if not success:
                progress.update(task_id, completed=100, visible=False)
                return False

            progress.update(task_id, completed=100, visible=False)

            # Move PDF to done directory
            task_id = progress.add_task(
                f"[yellow]Moving {pdf_file.name} to done directory...", total=100
            )

            shutil.move(str(pdf_file), str(self.done_dir / pdf_file.name))

            # Clean up temporary markdown file
            if temp_markdown.exists():
                temp_markdown.unlink()

            progress.update(task_id, completed=100, visible=False)
            return True

        except Exception as e:
            self.logger.error(f"Error processing {pdf_file.name}: {e}")
            return False

    def process_all_pdfs(self):
        """Process all PDF files in the base directory."""
        pdf_files = self.get_pdf_files()

        if not pdf_files:
            self.logger.info("No PDF files found in the base directory.")
            return

        self.logger.info(f"Found {len(pdf_files)} PDF files to process.")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
            console=self.console,
        ) as progress:
            overall_task = progress.add_task(
                "[magenta]Processing all PDFs...", total=len(pdf_files)
            )

            for pdf_file in pdf_files:
                self.logger.info(f"\nProcessing: {pdf_file.name}")
                success = self.process_single_pdf(pdf_file, progress)

                if success:
                    self.logger.info(f"Successfully processed: {pdf_file.name}")
                else:
                    self.logger.error(f"Failed to process: {pdf_file.name}")

                progress.update(overall_task, advance=1)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Process PDF files through conversion pipeline"
    )
    parser.add_argument("directory", help="Base directory containing PDF files")
    args = parser.parse_args()

    processor = PDFProcessor(args.directory)
    processor.process_all_pdfs()


if __name__ == "__main__":
    main()
