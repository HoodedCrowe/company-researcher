"""Tavily search client wrapper with retry logic."""

import os
import time
from urllib.parse import urlparse

from tavily import TavilyClient

from config import Config
from models.schemas import SearchResult


class SearchError(Exception):
    """Raised when search fails after retries."""
    pass


class TavilySearch:
    """Wrapper for Tavily search with retry logic."""
    
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY environment variable not set")
        self.client = TavilyClient(api_key=api_key)
    
    def search(self, query: str, max_results: int | None = None) -> list[SearchResult]:
        """
        Execute a search query with retry logic.
        
        Args:
            query: Search query string
            max_results: Maximum results to return (default from config)
            
        Returns:
            List of SearchResult objects
            
        Raises:
            SearchError: If search fails after all retries
        """
        max_results = max_results or Config.TAVILY_MAX_RESULTS_PER_QUERY
        last_error = None
        
        for attempt in range(Config.RETRY_ATTEMPTS + 1):
            try:
                response = self.client.search(
                    query=query,
                    max_results=max_results,
                    search_depth="basic",
                )
                
                results = []
                for item in response.get("results", []):
                    domain = urlparse(item.get("url", "")).netloc
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        domain=domain,
                    ))
                
                return results
                
            except Exception as e:
                last_error = e
                if attempt < Config.RETRY_ATTEMPTS:
                    time.sleep(1)  # Brief pause before retry
                    continue
                    
        raise SearchError(f"Search failed after {Config.RETRY_ATTEMPTS + 1} attempts: {last_error}")
    
    def is_priority_domain(self, domain: str) -> bool:
        """Check if a domain is in the priority list."""
        return any(priority in domain for priority in Config.PRIORITY_DOMAINS)
