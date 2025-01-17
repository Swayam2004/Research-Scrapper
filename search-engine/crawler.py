import argparse
import glob
import re
import pandas as pd
import asyncio
import aiofiles

def parse_markdown(content: str) -> str:
    """Clean and parse markdown content to extract plain text."""
    
    # Remove code blocks
    content = re.sub(r'```[\s\S]*?```', '', content)
    content = re.sub(r'`.*?`', '', content)
    
    # Extract text from links [text](url)
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
    
    # Remove headers (#)
    content = re.sub(r'#+\s*', '', content)
    
    # Remove bold/italic markers
    content = re.sub(r'[*_]{1,2}(.*?)[*_]{1,2}', r'\1', content)
    
    # Clean bullet points and numbered lists
    content = re.sub(r'^\s*[-*+]\s+', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*\d+\.\s+', '', content, flags=re.MULTILINE)
    
    # Remove empty lines and extra whitespace
    content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())
    
    return content

async def get_markdown_text(path) -> str:
    text = ""

    async with aiofiles.open(path, 'r') as f:
        text = await f.read()
    
    return text

async def process_single_path(path):
    idx = path.rfind("/")
    markdown_name = path[idx+1:].replace("summary_", "").replace(".md", "")
    
    content = await get_markdown_text(path)
    cleaned_content = parse_markdown(content)

    return (markdown_name, cleaned_content)


async def process_path(paths):
    tasks = [process_single_path(path) for path in paths]
    results = await asyncio.gather(*tasks)

    return results


def parse_args():
    parser = argparse.ArgumentParser(
        description="A crawler script for store research content",
    )
    parser.add_argument("feed_path", help="Directory containing the help files")
    return parser.parse_args()


async def async_main(feed_path):
    markdown_paths = glob.glob(f"{feed_path}/**/*.md", recursive=True)

    results = await process_path(markdown_paths)

    df = pd.DataFrame(results, columns=['name', 'content'])
    df.to_parquet("index.parquet", index=False)
    print("Saved to output parquet file")
    df.to_csv("index.csv", index=False)
    print("Saved to output CSV file")

def main(feed_path):
    asyncio.run(async_main(feed_path))

if __name__ == "__main__":
    args = parse_args()
    main(args.feed_path)
