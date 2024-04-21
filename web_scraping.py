"""===============================================================================================
This code scrapes the Purdue University Biological Sciences Department Faculty webpage, extracts the
links to each faculty member's page, extracts the text under headers "BIO" or "Professional Faculty Research",
and adds the faculty member's name and biography text to a database called faculty_database.db

The code uses BeautifulSoup for the scraping and SQLite for database-making.

19 April 2024
==============================================================================================="""

import subprocess
import sys

packages = ["beautifulsoup4", "requests"]

for package in packages:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Import everything else we need
import sqlite3
import requests
import uuid
from bs4 import BeautifulSoup
import re

# Database connection setup
conn = sqlite3.connect('faculty_database.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS faculty (
    id TEXT PRIMARY KEY,
    name TEXT,
    biography TEXT,
    UNIQUE(name, biography)
)
''')
conn.commit()

def get_html(url):
    """---------------------------------------------------------------------------------
    Fetches HTML content from the specified URL with proper UTF-8 encoding handling.
    ----------------------------------------------------------------------------------"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP issues
        response.encoding = 'utf-8'  # Ensure the response is treated as UTF-8 or else we get symbols
        return response.text
    except requests.RequestException as e:
        return None

def parse_faculty_links(html):
    """-----------------------------------------------------------------
    Parses faculty links from the main faculty directory page.
    -------------------------------------------------------------------"""
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    class_combinations = ['.clearfix .element a'] # All faculty links begin with .clearfix and .element
    base_url = "https://www.bio.purdue.edu"

    for class_combination in class_combinations:
        a_tags = soup.select(class_combination)
        for a in a_tags:
            href = a['href']
            if href.startswith('http'):
                full_url = href
            else:
                full_url = f"{base_url.rstrip('/')}/{href.lstrip('/')}"
            links.append(full_url) # Add links to our list of links
    return links

def clean_text(text):
    """--------------------------------------------------------------------------------------------
    Cleans up text by removing unwanted marks using regular expressions and handling UTF-8.
    ----------------------------------------------------------------------------------------------"""
    text = re.sub(r'[“”"‘’\'`]', '', text)
    return text

def extract_faculty_text(html):
    """-------------------------------------------------------------------------------------------
    Extracts relevant text content from a faculty member's page, cleans it, and compiles it.
    --------------------------------------------------------------------------------------------"""
    soup = BeautifulSoup(html, 'html.parser')
    headers = soup.find_all('h4')
    relevant_paragraphs = []
    allowed_headers = {'PROFESSIONAL FACULTY RESEARCH', 'BIO'}

    for header in headers:
        header_text = header.text.strip().upper()
        if header_text in allowed_headers:
            current_tag = header.find_next_sibling()
            while current_tag and current_tag.name != 'h4': # h4 is where biographies located. We want text below
                if current_tag.name == 'p':
                    cleaned_text = clean_text(current_tag.text.strip())
                    relevant_paragraphs.append(cleaned_text)
                current_tag = current_tag.find_next_sibling()
    return " ".join(relevant_paragraphs) # Add biography

def extract_faculty_details(html):
    """----------------------------------------------------------------------------------
    Extracts faculty name and cleaned biography text from individual faculty pages.
    -----------------------------------------------------------------------------------"""
    soup = BeautifulSoup(html, 'html.parser')
    name_tag = soup.find('h1')
    name = name_tag.text.strip().replace('\n', ' ').upper() if name_tag else "UNKNOWN"

    biography = extract_faculty_text(html)
    return name, biography

def main():
    """----------------------------------------------------------------------------------------
    Main function to handle the scraping process and database insertion.
    ------------------------------------------------------------------------------------------"""
    main_url = 'https://www.bio.purdue.edu/People/faculty/index.html'
    main_html = get_html(main_url)
    if main_html:
        faculty_links = parse_faculty_links(main_html)
        for faculty_url in faculty_links:
            faculty_html = get_html(faculty_url)
            if faculty_html:
                name, biography = extract_faculty_details(faculty_html)
                faculty_id = str(uuid.uuid4())
                try:
                    c.execute('INSERT INTO faculty (id, name, biography) VALUES (?, ?, ?)',
                              (faculty_id, name, biography))
                    conn.commit()
                except sqlite3.IntegrityError:
                    print(f"Duplicate entry not added for {name}.") # Tells us which ones it attempted to duplicate
    conn.close()

if __name__ == "__main__":
    main()
