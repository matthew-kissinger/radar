import requests
from bs4 import BeautifulSoup
import tiktoken
from flask import current_app

def get_page_content(url):
    headers = {"apikey": current_app.config["SCRAPER_API_KEY"]}
    try:
        response = requests.get(url, headers=headers, timeout=120) 
    except requests.exceptions.Timeout:
        print(f"Timeout occurred while trying to scrape {url}")
        return None
    print(f"Response status code: {response.status_code}") 
    if response.status_code == 200:
        print(f"Raw response text: {response.text[:500]}") 
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        page_content = ' '.join(soup.get_text().split())
        print(f"Extracted page content: {page_content[:100]}...") 
        tokenizer = tiktoken.get_encoding("cl100k_base")
        tokens = tokenizer.encode(page_content)
        if len(tokens) > 2000:
            excess = len(tokens) - 2000
            page_content = tokenizer.decode(tokens[:-excess])
        print(f"Page Content: {page_content[:100]}...")  
        return page_content
    else:
        return None
