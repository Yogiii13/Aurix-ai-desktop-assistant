import logging
import webbrowser
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class WebActions:
    def __init__(self):
        self.google_search_url = "https://www.google.com/search?q="

    def search(self, query: str, num_results: int = 5) -> None:
        """
        Open the default web browser with the search query.
        """
        search_url = f"{self.google_search_url}{query.replace(' ', '+')}"
        webbrowser.open(search_url)
        logger.info(f"Opened browser for search: {search_url}")
        return None

    def scrape_webpage(self, url):
        """
        Scrape the content of a webpage and return the text.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            return text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping webpage {url}: {e}")
            return ""