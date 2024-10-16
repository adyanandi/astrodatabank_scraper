from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import csv
import time
import platform
from urllib.parse import urljoin


def start_browser():
    
    driver_path = 'driver/chromedriver' if platform.system() != 'Windows' else 'driver/chromedriver.exe'

    
    service = Service(driver_path)
    
    
    chrome_options = webdriver.ChromeOptions()
    

    driver = webdriver.Chrome(service=service, options=chrome_options)
    

    wait = WebDriverWait(driver, 10)  
    
    return driver, wait

# scrape data from the current page
def scrape_page(driver, wait, page_url):
    driver.get(page_url)
    time.sleep(2)  

    #
    links = driver.find_elements(By.CSS_SELECTOR, 'div.mw-allpages-body a')
    page_data = []

    for link in links:
        link_text = link.text
        link_url = link.get_attribute('href')
        page_data.append((link_text, link_url))
    
    
    next_page_url = None
    
    try:
        
        nav_div = driver.find_element(By.CSS_SELECTOR, 'div.mw-allpages-nav')
        next_link_element = nav_div.find_element(By.PARTIAL_LINK_TEXT, 'Next page')
        
    
        next_page_url = next_link_element.get_attribute('href')
        next_page_url = urljoin(page_url, next_page_url)  
        print(f"Next page URL: {next_page_url}")  
    except NoSuchElementException:
        print("No next page link found.")  
    
    return page_data, next_page_url


def write_to_csv(data):
    with open('links.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)

# Main scraping
def scrape_multiple_pages(initial_url, max_pages=4):
    page_count = 0
    current_url = initial_url
    visited_urls = set()  

    while current_url and page_count < max_pages:
        if current_url in visited_urls:
            print(f"Already visited: {current_url}. Skipping.")
            break

        driver, wait = start_browser()  

        
        page_data, next_url = scrape_page(driver, wait, current_url)

        
        write_to_csv(page_data)

        driver.quit()  

        visited_urls.add(current_url)  

        
        if not next_url or next_url == current_url:
            print("No new page found or same page. Stopping.")
            break
        
        current_url = next_url
        page_count += 1

        print(f"Page {page_count} scraped. Moving to next page: {current_url}")
        time.sleep(2)  


initial_url = 'https://www.astro.com/wiki/astro-databank/index.php?title=Special:AllPages&from=1943+Frankford+Junction+derailment'


scrape_multiple_pages(initial_url, max_pages=2)

print("Scraping completed.")