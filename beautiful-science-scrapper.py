import json
import random
import time
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup


def create_session():
    """
    Create a session with browser-like headers and cookies
    """
    session = requests.Session()

    # More comprehensive browser-like headers
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "DNT": "1",
            "Cache-Control": "max-age=0",
        }
    )

    return session


def extract_article_info(article_element):
    """
    Extract article information from a single article element
    """
    # Extract title
    title_elem = article_element.find("a", class_="result-list-title-link")
    title = title_elem.get_text(strip=True) if title_elem else ""

    # Extract authors
    authors = []
    authors_list = article_element.find("ol", class_="Authors")
    if authors_list:
        authors = [
            author.get_text(strip=True)
            for author in authors_list.find_all("span", class_="author")
        ]

    # Extract journal and date
    journal_date = article_element.find("span", class_="srctitle-date-fields")
    journal = (
        journal_date.find("a").get_text(strip=True)
        if journal_date and journal_date.find("a")
        else ""
    )
    date = (
        journal_date.find_all("span")[-1].get_text(strip=True) if journal_date else ""
    )

    # Extract PDF link
    pdf_link = article_element.find("a", class_="download-link")
    pdf_url = pdf_link.get("href") if pdf_link else ""

    # Extract DOI
    doi = article_element.get("data-doi", "")

    return {
        "title": title,
        "authors": authors,
        "journal": journal,
        "publication_date": date,
        "doi": doi,
        "pdf_url": pdf_url,
    }


def get_articles_from_page(session, url):
    """
    Extract article information from a given ScienceDirect search results page
    """
    try:
        # Add a random delay between requests (3-7 seconds)
        time.sleep(random.uniform(3, 7))

        # Add random jitter to appear more human-like
        if random.random() < 0.2:  # 20% chance of a longer pause
            time.sleep(random.uniform(2, 5))

        response = session.get(url)
        response.raise_for_status()

        # Check if we're being redirected to the unsupported browser page
        if "unsupported_browser" in response.url:
            print(f"Warning: Detected as bot. Waiting longer before next request...")
            time.sleep(random.uniform(10, 15))
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        # Find all article elements
        articles = soup.find_all("li", class_="ResultItem")

        # Extract information from each article
        articles_info = []
        for article in articles:
            article_info = extract_article_info(article)
            if article_info["pdf_url"]:  # Only include articles with PDF links
                # Convert relative URLs to absolute URLs
                article_info["pdf_url"] = urljoin(url, article_info["pdf_url"])
                articles_info.append(article_info)

        return articles_info

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        # Add longer delay after error
        time.sleep(random.uniform(15, 20))
        return []


def main():
    # Base search parameters
    base_url = "https://www.sciencedirect.com/search"
    search_query = "clean cookstove"
    results_per_page = 100

    # Create session with browser-like headers
    session = create_session()

    # List to store all articles
    all_articles = []

    # Initialize retry counter
    max_retries = 3
    retry_delay = 30  # seconds

    # Iterate through pages (0 to 900 with step 100)
    for offset in range(0, 1000, 100):
        # Construct URL with proper encoding
        current_url = f"{base_url}?qs={quote(search_query)}&show={results_per_page}"
        if offset > 0:
            current_url += f"&offset={offset}"

        # Try multiple times if needed
        for retry in range(max_retries):
            print(
                f"Scraping page with offset {offset} (attempt {retry + 1}/{max_retries})..."
            )

            articles = get_articles_from_page(session, current_url)

            if articles:  # If we got some articles, break the retry loop
                all_articles.extend(articles)
                print(f"Found {len(articles)} articles with PDF links on this page")
                break
            elif retry < max_retries - 1:  # If not last retry
                print(
                    f"Retry {retry + 1} failed. Waiting {retry_delay} seconds before next attempt..."
                )
                time.sleep(retry_delay)
                retry_delay *= 2  # Double the delay for next retry
            else:
                print(
                    f"Failed to get articles after {max_retries} attempts. Moving to next page..."
                )

    # Save results to JSON file
    output_file = "sciencedirect_articles.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total_articles": len(all_articles),
                "query": search_query,
                "articles": all_articles,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"\nScraping completed! Found total {len(all_articles)} articles with PDF links"
    )
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()
