import time

import pandas as pd
import requests
from bs4 import BeautifulSoup


def clean_salary(salary_text):
    """Clean salary text by removing '$' and ',' characters"""
    return salary_text.replace("$", "").replace(",", "")


# Initialize master dataframe
df = pd.DataFrame(columns=["Player", "Salary", "Year"])

# Headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Loop through years
for yr in range(1990, 2019):
    page_num = f"{yr}-{yr + 1}/"
    url = f"https://hoopshype.com/salaries/players/{page_num}"

    # Add delay to be respectful to the server
    time.sleep(2)

    try:
        # Make the request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all player names and salaries
        # Update these selectors based on the actual HTML structure
        players = soup.find_all(class_="name")
        salaries = soup.find_all(class_="hh-salaries-sorted")

        # Extract text from elements
        players_list = [player.text.strip() for player in players[1:]]  # Skip header
        salaries_list = [
            clean_salary(salary.text.strip()) for salary in salaries[1:]
        ]  # Skip header

        # Create temporary dataframe
        data_tuples = list(zip(players_list, salaries_list))
        temp_df = pd.DataFrame(data_tuples, columns=["Player", "Salary"])
        temp_df["Year"] = yr

        # Append to master dataframe
        df = pd.concat([df, temp_df], ignore_index=True)

        print(f"{page_num} DONE!!!")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {page_num}: {e}")
        continue

# Save to CSV
df.to_csv("players.csv", index=False)
print("Scraping completed! Data saved to players.csv")
