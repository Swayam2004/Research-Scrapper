import markdown
from weasyprint import HTML, CSS
from pathlib import Path
import argparse
import sys
import time
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)


def convert_markdown_to_pdf(input_file: str, output_file: str = None) -> None:
    """
    Convert a Markdown file to PDF with enhanced formatting support.

    Args:
        input_file (str): Path to input Markdown file
        output_file (str): Path to output PDF file (optional)
    """
    input_path = Path(input_file)

    # If no output file specified, use same name with .pdf extension
    if not output_file:
        output_file = input_path.with_suffix(".pdf")

    # Create progress bars
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeRemainingColumn(),
    ) as progress:
        # Task for reading file
        read_task = progress.add_task("[cyan]Reading markdown file...", total=100)

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()
                progress.update(read_task, completed=100)
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
            return
        except Exception as e:
            print(f"Error reading file: {str(e)}", file=sys.stderr)
            return

        # Task for converting markdown to HTML
        convert_task = progress.add_task(
            "[green]Converting markdown to HTML...", total=100
        )

        # Convert markdown to HTML with extended features
        html_content = markdown.markdown(
            markdown_content,
            extensions=[
                "tables",
                "fenced_code",
                "codehilite",
                "attr_list",
                "def_list",
                "footnotes",
                "md_in_html",
                "toc",
            ],
        )

        # Add HTML wrapper with better structure
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Converted Document</title>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        # Enhanced CSS for better formatting
        css = CSS(
            string="""
            @page {
                margin: 2.5cm 2cm;
                @top-center {
                    content: "";
                }
                @bottom-center {
                    content: counter(page);
                    font-size: 10pt;
                }
            }
            
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 21cm;
                margin: 0 auto;
            }
            
            h1, h2, h3, h4, h5, h6 {
                color: #2c3e50;
                margin-top: 1.5em;
                margin-bottom: 0.5em;
                line-height: 1.2;
            }
            
            h1 { font-size: 24pt; }
            h2 { font-size: 20pt; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
            h3 { font-size: 16pt; }
            
            p {
                margin: 1em 0;
                text-align: justify;
            }
            
            ul, ol {
                margin: 1em 0;
                padding-left: 2em;
            }
            
            li {
                margin: 0.5em 0;
            }
            
            code {
                background-color: #f6f8fa;
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-family: "Courier New", Courier, monospace;
                font-size: 85%;
            }
            
            pre {
                background-color: #f6f8fa;
                padding: 1em;
                border-radius: 5px;
                overflow-x: auto;
                margin: 1em 0;
            }
            
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }
            
            th, td {
                border: 1px solid #ddd;
                padding: 8px 12px;
                text-align: left;
            }
            
            th {
                background-color: #f8f9fa;
                font-weight: bold;
            }
            
            tr:nth-child(even) {
                background-color: #f8f9fa;
            }
            
            blockquote {
                margin: 1em 0;
                padding-left: 1em;
                border-left: 4px solid #ddd;
                color: #666;
            }
            
            strong {
                color: #2c3e50;
                font-weight: 600;
            }
            
            img {
                max-width: 100%;
                height: auto;
                display: block;
                margin: 1em auto;
            }
            
            .footnote {
                font-size: 0.9em;
                color: #666;
                margin-top: 2em;
                border-top: 1px solid #eee;
                padding-top: 1em;
            }
        """
        )

        progress.update(convert_task, completed=100)

        # Task for generating PDF
        pdf_task = progress.add_task("[yellow]Generating PDF...", total=100)

        try:
            # Convert HTML to PDF
            HTML(string=html_content).write_pdf(output_file, stylesheets=[css])
            progress.update(pdf_task, completed=100)

            # Add small delay to show completion
            time.sleep(0.5)
            print(f"\nSuccessfully created PDF: {output_file}")

        except Exception as e:
            print(f"Error generating PDF: {str(e)}", file=sys.stderr)
            return


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown to PDF with enhanced formatting"
    )
    parser.add_argument("input_file", help="Input Markdown file")
    parser.add_argument("-o", "--output", help="Output PDF file (optional)")
    args = parser.parse_args()

    convert_markdown_to_pdf(args.input_file, args.output)


if __name__ == "__main__":
    main()
