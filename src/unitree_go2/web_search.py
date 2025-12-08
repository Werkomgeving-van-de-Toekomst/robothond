"""
Web Search Functionaliteit voor Go2 Robot

Zoekt informatie op internet en kan resultaten tonen.
"""

import requests
from typing import List, Dict, Optional, Any
import json
from urllib.parse import quote


class WebSearcher:
    """
    Zoekt informatie op internet
    
    Ondersteunt verschillende search engines en APIs.
    """
    
    def __init__(self, search_engine: str = "duckduckgo"):
        """
        Initialiseer web searcher
        
        Args:
            search_engine: Search engine ("duckduckgo", "google", "bing")
        """
        self.search_engine = search_engine
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Zoek op internet
        
        Args:
            query: Zoekterm
            max_results: Maximum aantal resultaten
            
        Returns:
            Lijst van resultaten met title, url, snippet
        """
        if self.search_engine == "duckduckgo":
            return self._search_duckduckgo(query, max_results)
        elif self.search_engine == "google":
            return self._search_google(query, max_results)
        elif self.search_engine == "bing":
            return self._search_bing(query, max_results)
        else:
            raise ValueError(f"Onbekende search engine: {self.search_engine}")
    
    def _search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Zoek met DuckDuckGo (geen API key nodig)
        
        Args:
            query: Zoekterm
            max_results: Maximum aantal resultaten
            
        Returns:
            Lijst van resultaten
        """
        try:
            # DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            results = []
            
            # Abstract (korte samenvatting)
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", query),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data.get("Abstract", ""),
                    "type": "abstract"
                })
            
            # Related topics
            for topic in data.get("RelatedTopics", [])[:max_results - len(results)]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                        "type": "related"
                    })
            
            # Als geen resultaten, gebruik HTML scraping (simpele versie)
            if not results:
                # Fallback: gebruik DuckDuckGo HTML
                html_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                results.append({
                    "title": f"Zoekresultaten voor: {query}",
                    "url": html_url,
                    "snippet": f"Klik hier voor zoekresultaten: {html_url}",
                    "type": "html"
                })
            
            return results[:max_results]
            
        except Exception as e:
            print(f"⚠️  Fout bij DuckDuckGo search: {e}")
            # Fallback: return simpele resultaat
            return [{
                "title": f"Zoekresultaten voor: {query}",
                "url": f"https://duckduckgo.com/?q={quote(query)}",
                "snippet": f"Zoek op DuckDuckGo: {query}",
                "type": "fallback"
            }]
    
    def _search_google(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Zoek met Google (vereist API key of scraping)
        
        Args:
            query: Zoekterm
            max_results: Maximum aantal resultaten
            
        Returns:
            Lijst van resultaten
        """
        # Voor nu: redirect naar Google search
        # Voor echte API: gebruik Google Custom Search API met API key
        return [{
            "title": f"Zoekresultaten voor: {query}",
            "url": f"https://www.google.com/search?q={quote(query)}",
            "snippet": f"Zoek op Google: {query}",
            "type": "google"
        }]
    
    def _search_bing(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Zoek met Bing (vereist API key)
        
        Args:
            query: Zoekterm
            max_results: Maximum aantal resultaten
            
        Returns:
            Lijst van resultaten
        """
        # Voor nu: redirect naar Bing search
        return [{
            "title": f"Zoekresultaten voor: {query}",
            "url": f"https://www.bing.com/search?q={quote(query)}",
            "snippet": f"Zoek op Bing: {query}",
            "type": "bing"
        }]
    
    def search_and_summarize(self, query: str, max_results: int = 3) -> str:
        """
        Zoek en maak een korte samenvatting
        
        Args:
            query: Zoekterm
            max_results: Maximum aantal resultaten
            
        Returns:
            Korte samenvatting tekst
        """
        results = self.search(query, max_results)
        
        if not results:
            return f"Geen resultaten gevonden voor: {query}"
        
        summary_parts = [f"Zoekresultaten voor '{query}':"]
        
        for i, result in enumerate(results[:max_results], 1):
            summary_parts.append(f"\n{i}. {result['title']}")
            if result.get('snippet'):
                snippet = result['snippet'][:150]  # Limiteer lengte
                summary_parts.append(f"   {snippet}...")
        
        return "\n".join(summary_parts)

