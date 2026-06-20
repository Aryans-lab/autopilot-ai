"""
NanoCorp v3.0 - Web Tools

HTTP requests, scraping, and search.
"""
from __future__ import annotations

import requests
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
from dataclasses import dataclass

from .base import BaseTool, ToolOutput, success_result, error_result, ToolCategory


# ===========================================
# HTTP REQUEST TOOL
# ===========================================

@dataclass
class HTTPResponse:
    """HTTP response data."""
    status_code: int
    headers: Dict[str, str]
    body: str
    url: str
    elapsed: float


class HTTPRequestTool(BaseTool):
    """Make HTTP requests (GET, POST, PUT, DELETE, etc.)."""
    
    def __init__(
        self,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
        user_agent: str = "NanoCorp/3.0"
    ):
        super().__init__()
        self.timeout = timeout
        self.default_headers = headers or {}
        self.default_headers["User-Agent"] = user_agent
    
    @property
    def name(self) -> str:
        return "http_request"
    
    @property
    def description(self) -> str:
        return "Make HTTP requests (GET, POST, PUT, DELETE). Returns status, headers, and body."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.WEB
    
    def execute(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> ToolOutput:
        """
        Make an HTTP request.
        
        Args:
            url: Target URL
            method: HTTP method
            params: URL parameters
            data: Form data
            json_data: JSON body
            headers: Additional headers
            timeout: Request timeout
        
        Returns:
            Response with status, headers, body
        """
        try:
            req_headers = {**self.default_headers, **(headers or {})}
            req_timeout = timeout or self.timeout
            
            response = requests.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=req_headers,
                timeout=req_timeout
            )
            
            return success_result({
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text[:10000],  # Limit body size
                "url": response.url,
                "elapsed": response.elapsed.total_seconds()
            })
            
        except requests.Timeout:
            return error_result(f"Request timed out after {self.timeout}s: {url}")
        except requests.RequestException as e:
            return error_result(f"HTTP request failed: {e}")


# ===========================================
# WEB SCRAPER TOOL
# ===========================================

class WebScraperTool(BaseTool):
    """Scrape web pages and extract content."""
    
    def __init__(
        self,
        timeout: int = 30,
        user_agent: str = "NanoCorp/3.0 (Web Scraper)"
    ):
        super().__init__()
        self.timeout = timeout
        self.user_agent = user_agent
    
    @property
    def name(self) -> str:
        return "web_scrape"
    
    @property
    def description(self) -> str:
        return "Scrape a web page and extract clean text content."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.WEB
    
    def execute(
        self,
        url: str,
        selector: Optional[str] = None,
        extract_links: bool = False,
        extract_images: bool = False
    ) -> ToolOutput:
        """
        Scrape a web page.
        
        Args:
            url: Target URL
            selector: CSS selector to extract specific element
            extract_links: Extract all links
            extract_images: Extract all images
        
        Returns:
            Page content and extracted data
        """
        try:
            import httpx
            
            headers = {"User-Agent": self.user_agent}
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
            
            # Try to parse with BeautifulSoup
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract text
                if selector:
                    element = soup.select_one(selector)
                    text = element.get_text(separator="\n", strip=True) if element else ""
                else:
                    # Remove script and style elements
                    for tag in soup(["script", "style", "nav", "footer", "header"]):
                        tag.decompose()
                    text = soup.get_text(separator="\n", strip=True)
                
                # Extract links
                links = []
                if extract_links:
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        # Make absolute URLs
                        if href.startswith("/"):
                            parsed = urlparse(url)
                            href = f"{parsed.scheme}://{parsed.netloc}{href}"
                        links.append({"text": a.get_text(strip=True), "href": href})
                
                # Extract images
                images = []
                if extract_images:
                    for img in soup.find_all("img"):
                        src = img.get("src", "")
                        if src.startswith("//"):
                            src = "https:" + src
                        elif src.startswith("/"):
                            parsed = urlparse(url)
                            src = f"{parsed.scheme}://{parsed.netloc}{src}"
                        images.append({"alt": img.get("alt", ""), "src": src})
                
                return success_result({
                    "url": url,
                    "title": soup.title.string if soup.title else None,
                    "text": text[:50000],  # Limit text
                    "links": links[:100] if links else None,
                    "images": images[:50] if images else None,
                    "status_code": response.status_code
                })
                
            except ImportError:
                # Fallback to raw text
                return success_result({
                    "url": url,
                    "text": response.text[:50000],
                    "status_code": response.status_code
                })
                
        except Exception as e:
            return error_result(f"Scraping failed: {e}")


# ===========================================
# WEB SEARCH TOOL
# ===========================================

class WebSearchTool(BaseTool):
    """Search the web for information."""
    
    def __init__(self, tavily_api_key: Optional[str] = None):
        super().__init__()
        self.tavily_api_key = tavily_api_key
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return "Search the web for information using Tavily (preferred) or DuckDuckGo."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.WEB
    
    def execute(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic"
    ) -> ToolOutput:
        """
        Search the web.
        
        Args:
            query: Search query
            max_results: Maximum results
            search_depth: "basic" or "advanced"
        
        Returns:
            Search results with titles, URLs, and snippets
        """
        # Try Tavily first
        if self.tavily_api_key:
            return self._search_tavily(query, max_results, search_depth)
        
        # Fallback to DuckDuckGo
        return self._search_duckduckgo(query, max_results)
    
    def _search_tavily(self, query: str, max_results: int, depth: str) -> ToolOutput:
        """Search using Tavily API."""
        try:
            import httpx
            
            response = httpx.post(
                "https://api.tavily.com/search",
                json={
                    "query": query,
                    "search_depth": depth,
                    "max_results": max_results,
                    "api_key": self.tavily_api_key
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            results = [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", ""),
                    "score": r.get("score", 0)
                }
                for r in data.get("results", [])
            ]
            
            return success_result({
                "query": query,
                "results": results,
                "answer": data.get("answer")
            })
            
        except Exception as e:
            return error_result(f"Tavily search failed: {e}")
    
    def _search_duckduckgo(self, query: str, max_results: int) -> ToolOutput:
        """Search using DuckDuckGo HTML."""
        try:
            from bs4 import BeautifulSoup
            import httpx
            
            response = httpx.get(
                "https://duckduckgo.com/html/",
                params={"q": query},
                timeout=30
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            results = []
            for result in soup.select(".result")[:max_results]:
                title_elem = result.select_one(".result__title a")
                snippet_elem = result.select_one(".result__snippet")
                
                if title_elem:
                    results.append({
                        "title": title_elem.get_text(strip=True),
                        "url": title_elem["href"],
                        "snippet": snippet_elem.get_text(strip=True) if snippet_elem else ""
                    })
            
            return success_result({
                "query": query,
                "results": results
            })
            
        except Exception as e:
            return error_result(f"DuckDuckGo search failed: {e}")


# ===========================================
# EXPORTS
# ===========================================

__all__ = [
    "HTTPRequestTool",
    "WebScraperTool",
    "WebSearchTool",
    "HTTPResponse",
]
