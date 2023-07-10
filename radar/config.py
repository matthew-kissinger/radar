import os
from dotenv import load_dotenv

load_dotenv() 

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")
    BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
    SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
