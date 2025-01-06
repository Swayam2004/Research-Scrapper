#!/usr/bin/env python3
import google.generativeai as genai
import os
from pathlib import Path
import argparse
import logging
from typing import Optional


class GeminiProcessor:
    def __init__(self, api_key: str):
        """Initialize Gemini API with the provided API key."""
        self.api_key = api_key
        genai.configure(api_key=self.api_key)

        # Configure the model
        self.model = genai.GenerativeModel("gemini-pro")

        # Setup logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def read_markdown_file(self, file_path: str) -> str:
        """Read content from a markdown file."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {str(e)}")
            raise

    def process_markdown(self, input_markdown: str, prompt_markdown: str) -> str:
        """Process markdown content using Gemini API."""
        try:
            # Combine prompt and input content
            combined_prompt = (
                f"Using the following guidelines:\n\n{prompt_markdown}\n\n"
                f"Please summarize this research paper:\n\n{input_markdown}"
            )

            # Generate response
            response = self.model.generate_content(combined_prompt)

            # Check if response was blocked
            if response.prompt_feedback.block_reason:
                raise Exception(
                    f"Response blocked: {response.prompt_feedback.block_reason}"
                )

            return response.text

        except Exception as e:
            logging.error(f"Error processing with Gemini API: {str(e)}")
            raise

    def save_markdown(self, content: str, output_path: str):
        """Save processed content to a markdown file."""
        try:
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(content)
            logging.info(f"Successfully saved output to {output_path}")
        except Exception as e:
            logging.error(f"Error saving output file: {str(e)}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Process markdown files using Gemini API"
    )
    parser.add_argument("input_file", help="Path to input markdown file")
    parser.add_argument(
        "--prompt",
        default="gemini_prompt.md",
        help="Path to prompt markdown file (default: gemini_prompt.md)",
    )
    parser.add_argument("--output", "-o", help="Output markdown file path (optional)")
    parser.add_argument(
        "--api-key", help="Gemini API key (optional, can use GEMINI_API_KEY env var)"
    )
    args = parser.parse_args()

    try:
        # Get API key from argument or environment variable
        api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "No API key provided. Use --api-key or set GEMINI_API_KEY environment variable"
            )

        # Initialize processor
        processor = GeminiProcessor(api_key)

        # Read input files
        input_content = processor.read_markdown_file(args.input_file)
        prompt_content = processor.read_markdown_file(args.prompt)

        # Process content
        logging.info("Processing markdown with Gemini API...")
        output_content = processor.process_markdown(input_content, prompt_content)

        # Determine output path
        if args.output:
            output_path = args.output
        else:
            input_path = Path(args.input_file)
            output_path = input_path.with_stem(
                f"{input_path.stem}_summary"
            ).with_suffix(".md")

        # Save output
        processor.save_markdown(output_content, output_path)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
