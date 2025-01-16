# Research Scrapper

## Overview
A Python-based project for scraping, converting, and processing research documents. It includes functionality for batch processing Markdown files using Gemini APIs, PDF-to-Markdown converters, and more.

## Features
- Scrape research papers from multiple sources
- Filter and categorize collected data
- Export data in various formats (CSV, JSON, etc.)
- User-friendly interface

## Project Structure
- [requirements.txt](/requirements.txt) – Lists Python dependencies
- [file-converters](/file-converters/) – Scripts like markdown_to_pdf.py and pdf_to_markdown.py
- [folder-manipulation](/folder-manipulation/) – Scripts for organizing and managing files (e.g., file-grouper.py)
- [gemini_processor.py](/gemini_processor.py) – Defines the GeminiProcessor class for interacting with Gemini APIs
- [gemini_batch_process_markdowns.py](/gemini_batch_process_markdowns.py) – Provides batch processing of Markdown files
- [scrappers](/scrappers/) – Additional scrapers (e.g., beautiful-science-scrapper.py)

## Installation
To install the Research Scrapper, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/research-scrapper.git
    ```
2. Navigate to the project directory:
    ```bash
    cd research-scrapper
    ```
3. Create a virtual environment:
    ```bash
    python -m venv venv
    ```
4. Activate the virtual environment:
    - On Windows:
        ```bash
        venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
5. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
- Run [gemini_batch_process_markdowns.py](/gemini_batch_process_markdowns.py) to process all Markdown files in a directory:

1. Run the application:
    ```bash
    python gemini_batch_process_markdowns.py /path/to/markdowns
    ```
2. Follow the on-screen instructions to *start* scraping.
3. Check logs to see status messages and errors.


## Contact
For any questions or suggestions, please contact us at [swayam1223@gmail.com](mailto:swayam1223@gmail.com).
