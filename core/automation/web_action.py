import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re
import logging
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class WebActions:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.ddg_search_url = "https://duckduckgo.com/html/"
        self.google_search_url = "https://www.google.com/search"
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        if not self.serpapi_key:
            logger.warning("SERPAPI_API_KEY not found in environment variables. SerpAPI will not be used.")

    def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search the web using DuckDuckGo and return a list of results.
        Each result is a dictionary with 'title', 'link', and 'snippet' keys.
        """
        if self.serpapi_key:
            logger.info("Using SerpAPI for search.")  # Add this line
            return self._search_serpapi(query, num_results)
        else:
            ddg_results = self._search_duckduckgo(query, num_results)
            if ddg_results:
                logger.info(f"Found {len(ddg_results)} results from DuckDuckGo")
                return ddg_results
            
            # If DuckDuckGo fails, try Google as fallback
            logger.info("DuckDuckGo search failed, trying Google")
            google_results = self._search_google(query, num_results)
            if google_results:
                logger.info(f"Found {len(google_results)} results from Google")
                return google_results
            
            # If both fail, return empty list
            logger.error("Both search engines failed to return results")
            return []

    def _search_duckduckgo(self, query, num_results=5):
        try:
            params = {'q': query}
            response = requests.get(self.ddg_search_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            results = []

            # Check if we got search results
            result_elements = soup.select('.result__body')
            if not result_elements:
                logger.warning("No result elements found in DuckDuckGo response")
                return []

            for result in result_elements[:num_results]:
                title_elem = result.select_one('.result__title')
                link_elem = result.select_one('.result__url')
                snippet_elem = result.select_one('.result__snippet')
                
                if title_elem and link_elem and snippet_elem:
                    title = title_elem.text.strip()
                    link = link_elem.text.strip()
                    snippet = snippet_elem.text.strip()
                    
                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet
                    })

            return results
        except Exception as e:
            logger.error(f"Error performing DuckDuckGo search: {e}", exc_info=True)
            return []

    def _search_google(self, query, num_results=5):
        try:
            params = {'q': query, 'num': num_results}
            response = requests.get(self.google_search_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            results = []

            # Google search results are in divs with class 'g'
            for result in soup.select('div.g')[:num_results]:
                # Extract title
                title_elem = result.select_one('h3')
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                
                # Extract link
                link_elem = result.select_one('a')
                if not link_elem or not link_elem.has_attr('href'):
                    continue
                link = link_elem['href']
                if link.startswith('/url?'):
                    link = re.search(r'url\?q=([^&]+)', link).group(1)
                
                # Extract snippet
                snippet_elem = result.select_one('div.VwiC3b')
                snippet = snippet_elem.text.strip() if snippet_elem else "No description available"
                
                results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet
                })

            return results
        except Exception as e:
            logger.error(f"Error performing Google search: {e}", exc_info=True)
            return []

    def _search_serpapi(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Search the web using SerpAPI and return a list of results."""
        try:
            from serpapi import GoogleSearch
            params = {
                "api_key": self.serpapi_key,
                "q": query,
                "num": num_results,
                "gl": "us",
                "hl": "en"
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            logger.debug(f"SerpAPI Raw Response: {results}")  # Add this line
            search_results = []
            if 'organic_results' in results:
                for result in results['organic_results']:
                    title = result.get('title', 'N/A')
                    link = result.get('link', 'N/A')
                    snippet = result.get('snippet', 'N/A')
                    search_results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet
                    })
                logger.info(f"Found {len(search_results)} results from SerpAPI")
                return search_results
            else:
                logger.warning("No organic results found in SerpAPI response.")
                return []
        except Exception as e:
            logger.error(f"Error performing SerpAPI search: {e}", exc_info=True)
            return []

    def scrape_webpage(self, url):
        """
        Scrape the content of a webpage and return the text.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract all text from the webpage
            text = soup.get_text(separator=' ', strip=True)
            return text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping webpage {url}: {e}")
            return ""