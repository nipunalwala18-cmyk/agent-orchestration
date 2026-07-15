import logging
from typing import Any
import httpx

from app.core.config import settings

logger = logging.getLogger("platform.web_search")

class WebSearchService:
    """Service to search the internet and augment RAG contexts.
    
    Prefers Tavily API if TAVILY_API_KEY is available.
    """

    def __init__(self):
        self.tavily_api_key = settings.TAVILY_API_KEY
        self.serper_api_key = settings.SERPER_API_KEY

    async def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Perform a web search and return the top_k results.
        
        Returns a list of dictionaries with keys: title, url, snippet/content.
        """
        if self.tavily_api_key:
            return await self._search_tavily(query, top_k)
        elif self.serper_api_key:
            return await self._search_serper(query, top_k)
        
        logger.warning("No web search API keys configured. Skipping web search.")
        return []

    async def _search_tavily(self, query: str, top_k: int) -> list[dict[str, Any]]:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": top_k,
            "include_answer": False,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title", "No Title"),
                        "url": item.get("url", ""),
                        "text": item.get("content", ""),
                    })
                return results
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return []

    async def _search_serper(self, query: str, top_k: int) -> list[dict[str, Any]]:
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": top_k
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("organic", []):
                    results.append({
                        "title": item.get("title", "No Title"),
                        "url": item.get("link", ""),
                        "text": item.get("snippet", ""),
                    })
                # Ensure we only return top_k if serper returns more
                return results[:top_k]
        except Exception as e:
            logger.error(f"Serper search failed: {e}")
            return []
