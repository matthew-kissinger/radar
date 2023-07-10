import requests
import urllib.parse
from flask import current_app

def search_brave(search_term):
    headers = {"Accept": "application/json", "X-Subscription-Token": current_app.config["BRAVE_SEARCH_API_KEY"]}
    query = urllib.parse.quote(search_term)
    response = requests.get(f"https://api.search.brave.com/res/v1/web/search?q={query}", headers=headers)
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
