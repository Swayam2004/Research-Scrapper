import os
import shutil
from pathlib import Path
import logging
import re

def setup_logging():
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')

def create_base_structure(base_path):
    research_papers_dir = os.path.join(base_path, "Research Papers")
    os.makedirs(research_papers_dir, exist_ok=True)
    return research_papers_dir

def get_base_name_and_timestamp(filename):
    # Extract timestamp if present in summary files
    match = re.search(r'(.+?)(?:_\d{8}_\d{6})?\..*$', filename)
    return match.group(1) if match else None

def group_files(base_path):
    setup_logging()
    logger = logging.getLogger(__name__)
    
    paper_dir = os.path.join(base_path, "paper")
    markdown_dir = os.path.join(base_path, "markdown")
    pdf_dir = os.path.join(base_path, "pdf")
    
    research_papers_dir = create_base_structure(base_path)
    papers = [f for f in os.listdir(paper_dir) if f.endswith('.pdf')]
    
    for paper in papers:
        base_name = get_base_name_and_timestamp(paper)
        logger.info(f"Processing {base_name}")
        
        # Find corresponding markdown and PDF files
        markdown_files = [f for f in os.listdir(markdown_dir) 
                         if f.startswith(f"summary_{base_name}") and f.endswith('.md')]
        
        if not markdown_files:
            logger.warning(f"No markdown file found for {paper}")
            continue
        
        markdown_file = markdown_files[0]  # Take the first match
        timestamp_match = re.search(r'_(\d{8}_\d{6})', markdown_file)
        timestamp = timestamp_match.group(1) if timestamp_match else ""
        
        folder_name = f"{base_name}"
        paper_folder = os.path.join(research_papers_dir, folder_name)
        os.makedirs(paper_folder, exist_ok=True)
        
        try:
            # Copy original paper
            shutil.copy2(os.path.join(paper_dir, paper),
                        os.path.join(paper_folder, paper))
            
            # Copy markdown file
            shutil.copy2(os.path.join(markdown_dir, markdown_file),
                        os.path.join(paper_folder, markdown_file))
            
            # Copy PDF summary
            pdf_file = markdown_file.replace('.md', '.pdf')
            if os.path.exists(os.path.join(pdf_dir, pdf_file)):
                shutil.copy2(os.path.join(pdf_dir, pdf_file), os.path.join(paper_folder, pdf_file))

            logger.info(f"Successfully processed {folder_name}")
            
        except Exception as e:
            logger.error(f"Error processing {folder_name}: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python file-grouper.py <base_path>")
        sys.exit(1)
    
    base_path = sys.argv[1]
    group_files(base_path)
