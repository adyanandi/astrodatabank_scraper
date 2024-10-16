import json
import os
import re
import time
import hashlib
import requests
import csv
import joblib
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from random_user_agent.user_agent import UserAgent
from joblib import Parallel, delayed
from random_user_agent.params import SoftwareName, OperatingSystem
import sqlite3

# Configure random-user-agent
software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value]

# Initialize the UserAgent object with the software and operating system configurations
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

# Function to generate headers dynamically
def generate_headers():
    return {
        'User-Agent': user_agent_rotator.get_random_user_agent(),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com/'
    }

# Function to hash the filename based on URL
def hash_filename(url):
    hasher = hashlib.sha256()
    hasher.update(url.encode('utf-8'))
    return hasher.hexdigest()

# Function to extract categories
def extract_categories(soup):
    categories = []
    categories_section = soup.find('span', id='Categories')
    
    if categories_section:
        categories_list = categories_section.find_next('ul')
        if categories_list:
            li_elements = categories_list.find_all('li')
            for li in li_elements:
                categories.append(li.text.strip())
    return categories



def extract_section_text(soup, section_id):
    section = soup.find('span', {'id': section_id})
    if section:
        section_parent = section.find_parent(['h2', 'h3', 'h4'])
        if section_parent:
            
            next_node = section_parent.find_next_sibling()
            section_text = []
            
        
            while next_node and next_node.name not in ['h2', 'h3', 'h4']:
                if next_node.name == 'p':  
                    section_text.append(next_node.get_text(strip=True))
                elif next_node.name == 'ul':  
                    list_items = next_node.find_all('li')
                    for item in list_items:
                        section_text.append(item.get_text(strip=True))
                next_node = next_node.find_next_sibling()
            
            return '\n'.join(section_text)
    return ''


def extract_relationships(soup):
    return extract_section_text(soup, 'Relationships')

def extract_events(soup):
    return extract_section_text(soup, 'Events')


def extract_data(url):
    data = {
        'data': {
            'biography': {},
            'relationships': {},
            'events': {},
            'source notes': {},
            'category': {}
        }
    }

    try:
        print(f"Attempting to load URL: {url}")
        headers = generate_headers()  
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        if response.status_code == 200:
            print(f"Page loaded successfully for: {url}")

            soup = BeautifulSoup(response.text, 'html.parser')

            full_html = soup.prettify()

            def get_element_text(selector):
                element = soup.select_one(selector)
                return element.get_text(strip=True) if element else ''

            
            data['Name'] = get_element_text('td:contains("Name") + td tr td:nth-child(1)')

            
            combined_date_time = get_element_text('td:contains("born on") + td')
            date_match = re.search(r"(\d{1,2}\s\w+\s\d{4})", combined_date_time)
            time_match = re.search(r"(\d{1,2}:\d{2})", combined_date_time)

            data['Date'] = date_match.group(1) if date_match else ''
            data['Time'] = time_match.group(1) if time_match else ''

          
            place_name = get_element_text('td:contains("Place") + td')
            if place_name:
               data['Place Name'] = place_name.split(',')[0].strip()
            else:
                data['Place Name'] = ''

            place_info = get_element_text('td:contains("Place") + td small')
            if place_info:
                coords = place_info.split(',')
                data['Latitude'] = coords[0].strip() if len(coords) > 0 else ''
                data['Longitude'] = coords[1].strip() if len(coords) > 1 else ''
            else:
                data['Latitude'] = ''
                data['Longitude'] = ''

            
            data['Timezone'] = get_element_text('td:contains("Timezone") + td')

            
            data['Data Source'] = get_element_text('td:contains("Data source") + td table td:nth-child(1)')
            data['Rodden Rating'] = get_element_text('td:contains("Data source") + td table td:nth-child(1) b')

           
            collector_element = soup.find('a', text='Collector')
            if collector_element:
                collector_link = collector_element.find_next('a')  
                data['Collector'] = collector_link.get_text(strip=True) if collector_link else ''
            else:
                data['Collector'] = ''

            
            data['data']['biography']['text'] = extract_section_text(soup, 'Biography')

              
            data['data']['relationships']['text'] = extract_relationships(soup)

            
            data['data']['events']['text'] = extract_events(soup)

            
            data['data']['source notes']['text'] = extract_section_text(soup, 'Source_Notes')

            data['data']['category'] = extract_categories(soup)

            


            

            
            json_data = {
                'URL': url,
                'Name': data['Name'],
                'Date': data['Date'],
                'Time': data['Time'],
                'Place Name': data['Place Name'],
                'Latitude': data['Latitude'],
                'Longitude': data['Longitude'],
                'Timezone': data['Timezone'],
                'Data Source': data['Data Source'],
                'Rodden Rating': data['Rodden Rating'],
                'Collector': data['Collector'],
                'HTML Content': full_html, 
                'data': data['data']
            }

            if not os.path.exists('jsonFile'):
                os.makedirs('jsonFile')
            if response.status_code == 200:
           
                print(f"Data saved for URL: {url}")
                return json_data

               
            else:
                print(f"Error: Received unexpected status code {response.status_code}")

    except requests.exceptions.Timeout:
        print(f"Timeout while loading URL: {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error accessing URL: {url} - {e}")
    finally:
        print(f"Extraction completed for URL: {url}")

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Create SQLite table for data, including HTML content
def create_table():
    conn = sqlite3.connect('as_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scraped_data (
            url TEXT,
            name TEXT,
            date TEXT,
            time TEXT,
            place_name TEXT,
            latitude TEXT,
            longitude TEXT,
            timezone TEXT,
            data_source TEXT,
            rodden_rating TEXT,
            collector TEXT,
            biography TEXT,
            relationships TEXT,
            events TEXT,
            source_notes TEXT,
            category TEXT,
            html_content TEXT  -- Store HTML content here
        )
    ''')
    conn.commit()
    conn.close()

# Insert the data, including HTML content
def insert_data(data):
    conn = sqlite3.connect('as_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO scraped_data (url, name, date, time, place_name, latitude, longitude, timezone, data_source, 
                                  rodden_rating, collector, biography, relationships, events, source_notes, category, html_content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['URL'], data['Name'], data['Date'], data['Time'], data['Place Name'], data['Latitude'], 
          data['Longitude'], data['Timezone'], data['Data Source'], data['Rodden Rating'], 
          data['Collector'], data['data']['biography']['text'], data['data']['relationships']['text'], 
          data['data']['events']['text'], data['data']['source notes']['text'], 
          ','.join(data['data']['category']), data['HTML Content']))
    
    conn.commit()
    conn.close()        

def process_links(csv_file, num_jobs=-1):  
    urls = []

    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  
        for row in reader:
            if len(row) >= 2:
                link_text = row[0].strip().strip('"')  
                url = row[1].strip().strip('"')  
                urls.append(url)
            else:
                print(f"Skipping malformed row: {row}")

   
    Parallel(n_jobs=num_jobs)(delayed(extract_data)(url) for url in urls)

if __name__ == "__main__":
    create_table()
    csv_file = 'links.csv'
    urls = []
    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  
        for row in reader:
            if len(row) >= 2:
                link_text = row[0].strip().strip('"') 
                url = row[1].strip().strip('"') 
                urls.append(url)
            else:
                print(f"Skipping malformed row: {row}")
   
    cores=int(joblib.cpu_count())*2  
    for i in range(0, len(urls), cores):
         try:
            data_jsons=Parallel(n_jobs=cores)(delayed(extract_data)(url) for url in urls[i:i+cores])
            for data in data_jsons:
                insert_data(data)
            
         except Exception as e:
            print(f"Error during parallel processing: {e}")    


