import requests
import urllib.parse
from flask import current_app
import re

def search_brave(search_term):
    headers = {"Accept": "application/json", "X-Subscription-Token": current_app.config["BRAVE_SEARCH_API_KEY"]}
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    match = url_pattern.search(search_term)
    if match is None:
        raise ValueError(f"No URL found in search_term: {search_term}")
    url = match.group(0)
    
    response = requests.get(url, headers=headers)
    print(f"Response status code from Brave API: {response.status_code}")  
    if response.status_code == 200:
        response_json = response.json()
        print(f"Response JSON from Brave API: {response_json}")  
        try:
            return response_json['web']
        except KeyError:
            return None
    else:
        return None

