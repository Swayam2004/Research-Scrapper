# Research Scrapper & Search Engine

## Overview
A Python-based project for scraping, converting, and processing research documents. It includes functionality for batch processing Markdown files, search capabilities, and a web interface for exploring research papers.

## Features
- Scrape research papers from multiple sources
- Filter and categorize collected data
- Export data in various formats (CSV, JSON, etc.)
- User-friendly interface
- Full-text search across research papers using BM25 algorithm
- Web interface for browsing and searching papers
- FastAPI backend with efficient paper indexing
- View original PDFs and summaries through web interface
- View relevance scores for search results

## Project Structure
- [requirements.txt](/requirements.txt) – Lists Python dependencies
- [file-converters](/file-converters/) – Scripts like markdown_to_pdf.py and pdf_to_markdown.py
- [folder-manipulation](/folder-manipulation/) – Scripts for organizing and managing files (e.g., file-grouper.py)
- [gemini_processor.py](/gemini_processor.py) – Defines the GeminiProcessor class for interacting with Gemini APIs
- [gemini_batch_process_markdowns.py](/gemini_batch_process_markdowns.py) – Provides batch processing of Markdown files
- [scrappers](/scrappers/) – Additional scrapers (e.g., beautiful-science-scrapper.py)
- [search-engine](/search-engine/) – Search functionality and web interface
  - [app/](/search-engine/app/) – FastAPI web application
  - [engine.py](/search-engine/engine.py) – BM25 search implementation
  - [crawler.py](/search-engine/crawler.py) – Document indexing and processing

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
### Processing Papers
- Run [gemini_batch_process_markdowns.py](/gemini_batch_process_markdowns.py) to process all Markdown files in a directory:

1. Run the application:
    ```bash
    python gemini_batch_process_markdowns.py /path/to/markdowns
    ```
2. Follow the on-screen instructions to *start* scraping.
3. Check logs to see status messages and errors.

### Search Engine & Web Interface
1. Index and serve papers:
```bash
cd search-engine
python -m app --data-path "/path/to/papers/index.parquet"
```
2. Access the web interface:
- Open http://localhost:8000 in your browser
- Search through papers using keywords
- View original PDFs and summaries
- Browse all available papers


## Contact
For any questions or suggestions, please contact us at [swayam1223@gmail.com](mailto:swayam1223@gmail.com).
