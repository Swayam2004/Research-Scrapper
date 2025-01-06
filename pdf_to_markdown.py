#!/usr/bin/env python3
import argparse
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import fitz  # PyMuPDF


class PDFToMarkdown:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.markdown_content = []
        self.header_sizes = {}
        self.previous_block_type = None

        # Setup logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

        # Constants for text analysis
        self.MIN_LINE_LENGTH = 40  # Minimum characters for a paragraph
        self.PARAGRAPH_SPACE_THRESHOLD = (
            5  # Points of space to consider paragraph break
        )

    def analyze_font_statistics(self) -> Dict[float, Dict]:
        """Analyze font statistics across the document."""
        font_stats = defaultdict(
            lambda: {"count": 0, "is_bold": 0, "avg_length": 0, "samples": []}
        )

        for page in self.doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" not in block:
                    continue

                for line in block["lines"]:
                    for span in line["spans"]:
                        size = round(span["size"], 1)
                        text = span["text"].strip()
                        if len(text) > 1:
                            font_stats[size]["count"] += 1
                            font_stats[size]["is_bold"] += (
                                1 if "bold" in span.get("font", "").lower() else 0
                            )
                            font_stats[size]["avg_length"] += len(text)
                            if len(font_stats[size]["samples"]) < 5:
                                font_stats[size]["samples"].append(text)

        # Calculate averages
        for stats in font_stats.values():
            if stats["count"] > 0:
                stats["avg_length"] /= stats["count"]
                stats["is_bold"] = stats["is_bold"] / stats["count"] > 0.5

        return font_stats

    def detect_document_structure(self):
        """Analyze the document to detect font sizes for different heading levels."""
        font_stats = self.analyze_font_statistics()

        # Sort fonts by frequency and size
        sorted_fonts = sorted(font_stats.items(), key=lambda x: (-x[1]["count"], -x[0]))

        # Identify the main body text size (most frequent)
        self.body_font_size = sorted_fonts[0][0]

        # Identify heading sizes (larger than body text, less frequent)
        heading_candidates = [
            (size, stats)
            for size, stats in font_stats.items()
            if size > self.body_font_size
            and stats["count"] < font_stats[self.body_font_size]["count"] * 0.5
        ]

        # Sort heading candidates by size
        heading_candidates.sort(key=lambda x: -x[0])

        # Assign heading levels
        for i, (size, _) in enumerate(heading_candidates[:3]):
            self.header_sizes[size] = i + 1

    def is_heading(self, text: str, font_size: float, is_bold: bool) -> int:
        """Determine if text is a heading and return heading level."""
        if not text.strip():
            return 0

        # Common heading patterns
        heading_patterns = [
            r"^(?:chapter|section|\d+\.)\s+\w+",
            r"^(abstract|introduction|methodology|results|discussion|conclusion|references)$",
            r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,4}$",
        ]

        # Check if font size matches heading sizes
        level = self.header_sizes.get(round(font_size, 1), 0)

        # If it's a larger font or bold and matches heading patterns
        if (level or (is_bold and font_size >= self.body_font_size)) and any(
            re.match(pattern, text.strip(), re.IGNORECASE)
            for pattern in heading_patterns
        ):
            return level or min(self.header_sizes.values())

        return 0

    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove multiple spaces and normalize whitespace
        text = re.sub(r"\s+", " ", text)

        # Fix common OCR issues
        text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")
        text = text.replace("−", "-").replace("…", "...")

        # Fix broken words at line breaks
        text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)

        # Fix common punctuation issues
        text = re.sub(r"\s+([.,;:!?])", r"\1", text)

        return text.strip()

    def process_block(self, block, prev_block) -> Tuple[str, str]:
        """Process a text block and determine its type."""
        if "lines" not in block:
            return "", "empty"

        text_lines = []
        block_type = "paragraph"
        current_font_size = 0
        is_bold = False

        for line in block["lines"]:
            line_text = ""
            for span in line["spans"]:
                current_font_size = round(span["size"], 1)
                is_bold = "bold" in span.get("font", "").lower()
                text = self.clean_text(span["text"])

                if text:
                    # Check for heading
                    heading_level = self.is_heading(text, current_font_size, is_bold)
                    if heading_level:
                        return f"{'#' * heading_level} {text}", "heading"

                    # Check for list items
                    if re.match(r"^\s*[\•\-]\s+", text):
                        return f"- {text.lstrip('•').strip()}", "list"
                    if re.match(r"^\s*\d+\.\s+", text):
                        return text, "list"

                    line_text += text + " "

            if line_text:
                text_lines.append(line_text.strip())

        # Join lines and determine if it's a paragraph
        text = " ".join(text_lines)
        if not text:
            return "", "empty"

        return text, block_type

    def convert(self) -> str:
        """Convert PDF to Markdown."""
        logging.info(f"Converting {self.pdf_path} to Markdown...")

        # First pass: analyze document structure
        self.detect_document_structure()

        # Second pass: convert content
        processed_blocks = []
        previous_block_type = None

        for page_num, page in enumerate(self.doc, 1):
            logging.info(f"Processing page {page_num}/{len(self.doc)}")
            blocks = page.get_text("dict")["blocks"]

            for i, block in enumerate(blocks):
                prev_block = blocks[i - 1] if i > 0 else None
                text, block_type = self.process_block(block, prev_block)

                if text:
                    # Add appropriate spacing
                    if processed_blocks:
                        if block_type == "heading" or previous_block_type == "heading":
                            processed_blocks.append("")
                        elif block_type != "list" or previous_block_type != "list":
                            processed_blocks.append("")

                    processed_blocks.append(text)
                    previous_block_type = block_type

        return "\n".join(processed_blocks)


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF research paper to Markdown"
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output", "-o", help="Output markdown file path (optional)")
    args = parser.parse_args()

    try:
        converter = PDFToMarkdown(args.pdf_path)
        markdown_content = converter.convert()

        # Determine output path
        if args.output:
            output_path = args.output
        else:
            pdf_path = Path(args.pdf_path)
            output_path = pdf_path.with_suffix(".md")

        # Write output
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        logging.info(f"Successfully converted PDF to Markdown: {output_path}")

    except Exception as e:
        logging.error(f"Error converting PDF: {str(e)}")
        raise


if __name__ == "__main__":
    main()
