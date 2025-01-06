import json
import random
import time
from urllib.parse import quote

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def setup_driver():
    """
    Set up and return the Chrome WebDriver
    """

    PATH = "/usr/local/bin/chromedriver"
    service = webdriver.ChromeService(executable_path=PATH)

    options = webdriver.ChromeOptions()
    options.add_argument("/home/swayam/.config/google-chrome/Default")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=service, options=options, keep_alive=True)
    # driver.execute_script(
    #     "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    # )

    # def get_free_proxies(driver):
    #     driver.get("https://sslproxies.org")

    #     table = driver.find_element(By.TAG_NAME, "table")
    #     thead = table.find_element(By.TAG_NAME, "thead").find_elements(
    #         By.TAG_NAME, "th"
    #     )
    #     tbody = table.find_element(By.TAG_NAME, "tbody").find_elements(
    #         By.TAG_NAME, "tr"
    #     )

    #     headers = []
    #     for th in thead:
    #         headers.append(th.text.strip())

    #     proxies = []
    #     for tr in tbody:
    #         proxy_data = {}
    #         tds = tr.find_elements(By.TAG_NAME, "td")
    #         for i in range(len(headers)):
    #             proxy_data[headers[i]] = tds[i].text.strip()
    #         proxies.append(proxy_data)

    #     return proxies

    # free_proxies = get_free_proxies(driver)

    # print(free_proxies)

    return driver


def main():
    driver = setup_driver()

    try:
        cnt = 94

        url = "https://scholar.google.com/scholar?start=940&q=clean+cookstove&hl=en&as_sdt=0,5"
        driver.get(url)

        driver.implicitly_wait(10)

        time.sleep(60)
        while cnt <= 100:
            time.sleep(random.uniform(30, 40))

            anchor_list = driver.find_elements(by=By.CSS_SELECTOR, value="a")
            next_page_list = driver.find_elements(by=By.CLASS_NAME, value="gs_nma")

            for an in anchor_list:
                if "[PDF]" in an.text:
                    an.click()

                    if "scholar.google.com" not in driver.current_url:
                        time.sleep(5)
                        driver.back()

                    time.sleep(random.uniform(6, 7))

            print("Doing " + str(cnt))

            time.sleep(random.uniform(3, 5))

            [ele for ele in next_page_list if ele.text == str(cnt+1)][0].click()
            cnt += 1
    finally:
        pass


if __name__ == "__main__":
    main()
