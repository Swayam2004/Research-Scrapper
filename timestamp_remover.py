import os
import re
import logging
from pathlib import Path

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def remove_timestamps(file_path):
    # Remove all timestamp patterns (_YYYYMMDD_HHMMSS)
    base_name = re.sub(r'(_\d{8}_\d{6})+', '', file_path.stem)
    return f"{base_name}{file_path.suffix}"

def process_directory(directory):
    logger = setup_logging()
    directory = Path(directory)
    
    for file_path in directory.glob('*.pdf'):
        try:
            new_name = remove_timestamps(file_path)
            if new_name != file_path.name:
                file_path.rename(directory / new_name)
                logger.info(f"Renamed: {file_path.name} -> {new_name}")
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python timestamp_remover.py <directory_path>")
        sys.exit(1)
    
    process_directory(sys.argv[1])
