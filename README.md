# Astro Data Scraper: Automated Web Scraping from Astro-Databank

The Astro Data Scraper is a web scraping tool designed to extract structured information from the Astro-Databank website, a renowned source for astrological profiles, biographies, and research data. This tool automates the collection of key details such as names, birth dates, birth locations, time zones, and other biographical data. The scraped data is efficiently stored in JSON files and an SQLite database for easy access, analysis, and further processing.


## Features

- **Automated Data Extraction:**
Automatically scrapes biographical and astrological data from the Astro-Databank website, reducing manual effort.
- **Storage Options:**
Saves scraped data in JSON files for easy analysis and in SQLite databases for efficient querying and further use.
- **Live Previews:**
Displays real-time previews of the scraped data as it’s being collected, helping users monitor progress and spot issues immediately.
- **Headless Browser Support:**
Utilizes Selenium WebDriver for headless browsing, improving performance and allowing scraping without opening a visible browser window.
- **Configurable ChromeDriver Handler:**
Ensures the scraper works independently with automatic ChromeDriver handling, eliminating the need for manual installation or updates.
- **Cross-Platform Compatibility:**
Works on Windows, macOS, and Linux, providing seamless performance across various operating systems.


## Tech Stack

- **Python –** Main programming language for scraping and data extraction.
- **Selenium –** Automates web browser interaction for scraping dynamic content.
- **BeautifulSoup –** Parses HTML and extracts relevant content from Astro-Databank pages.
- **Requests –** Sends HTTP requests to fetch webpage content.
- **Joblib –** Manages parallel processing to enhance scraping efficiency.
- **Random User Agent –** Rotates user agents to avoid detection while scraping.
- **SQLite –** Stores extracted data in a lightweight relational database.

- **Hashlib –** Generates unique hashes for data validation or duplicate detection.
- **Time & OS –** Used for delays, scheduling, and interacting with the system environment.



## Installation

1.**Clone the repository**:
```bash
  git clone https://github.com/adyanandi/astrodatabank_scraper
  cd astrodatabank_scraper
```
2. **Install Dependencies :**
```bash
    pip install -r requirements.txt

```
3. **Download and set up the WebDriver** :
     
->      Download **ChromeDriver** (or the appropriate WebDriver for your browser).
    
## Usage/Examples
This project consists of two main scripts that handle the scraping process. Here’s how to use them:

**Step 1: Extract Links using link_scraper.py**

The link_scraper.py collects all relevant links from the Astro-Databank website and stores them in links.csv. Here's an example of how you run it:
```bash
  python link_scraper.py
```
**Step 2: Extract Data from Links using astro_scraper.py**

Use the astro_scraper.py to scrape detailed data from the links saved in links.csv.

```bash
python astro_scraper.py
```
