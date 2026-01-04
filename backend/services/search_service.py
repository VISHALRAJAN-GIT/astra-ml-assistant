from duckduckgo_search import DDGS
from typing import List, Dict, Any

class SearchService:
    """Service for performing web searches using DuckDuckGo"""
    
    def __init__(self):
        pass

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a web search and returns a list of results.
        """
        results = []
        try:
            with DDGS() as ddgs:
                ddgs_gen = ddgs.text(query, max_results=max_results)
                for r in ddgs_gen:
                    results.append({
                        "title": r.get("title", "No Title"),
                        "url": r.get("href", "#"),
                        "snippet": r.get("body", "No description available.")
                    })
            return results
        except Exception as e:
            print(f"Search Error: {e}")
            return [{"error": str(e)}]

# Singleton instance
search_service = SearchService()
