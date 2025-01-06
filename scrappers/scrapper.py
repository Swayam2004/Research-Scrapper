from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

PATH = "/usr/local/bin/chromedriver"

service = webdriver.ChromeService(executable_path=PATH)
options = webdriver.ChromeOptions()
options.add_argument("enable-automation")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-extensions")
options.add_argument("--dns-prefetch-disable")
options.add_argument("--disable-gpu")
options.add_argument('--headless=new')

driver = webdriver.Chrome(options=options, service=service, keep_alive=True)

driver.get("https://hoopshype.com/salaries/players/")

df = pd.DataFrame(columns=["Player", "Salary", "Year"])  # creates master dataframe

for yr in range(1990, 2019):
    page_num = str(yr) + "-" + str(yr + 1) + "/"
    url = "https://hoopshype.com/salaries/players/" + page_num
    driver.get(url)

    players = driver.find_elements(by=By.CLASS_NAME, value="name")
    salaries = driver.find_elements(by=By.CLASS_NAME, value="hh-salaries-sorted")

    players_list = []
    for p in range(len(players)):
        players_list.append(players[p].text)

    salaries_list = []
    for s in range(len(salaries)):
        salaries_list.append(salaries[s].text)

    data_tuples = list(
        zip(players_list[1:], salaries_list[1:])
    )  # list of each players name and salary paired together
    temp_df = pd.DataFrame(
        data_tuples, columns=["Player", "Salary"]
    )  # creates dataframe of each tuple in list
    temp_df["Year"] = yr  # adds season beginning year to each dataframe
    df = pd.concat([df, temp_df], ignore_index=True)  # appends to master dataframe

    print(page_num + "DONE!!!")

df.to_csv("players.csv")

driver.close()
