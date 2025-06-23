from langchain_core.tools import tool
from duckduckgo_search import DDGS
from typing import List, Dict
import time

class WebSearchTool:
    """Free web search using DuckDuckGo"""
    
    def __init__(self):
        self.ddg = DDGS()
    
    def search_mathematics(self, query: str, max_results: int = 3) -> str:
        """Search for mathematics content on the web"""
        try:
            # Enhance query for better math results
            enhanced_query = f"mathematics tutorial {query} site:khanacademy.org OR site:mathworld.wolfram.com OR site:brilliant.org"
            
            results = list(self.ddg.text(enhanced_query, max_results=max_results))
            
            if not results:
                # Fallback to simpler query
                results = list(self.ddg.text(f"math {query}", max_results=max_results))
            
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append(
                    f"Result {i+1}:\n"
                    f"Title: {result.get('title', 'N/A')}\n"
                    f"Content: {result.get('body', 'N/A')[:400]}...\n"
                    f"URL: {result.get('href', 'N/A')}\n"
                    f"---"
                )
            
            return "\n".join(formatted_results) if formatted_results else "No web results found."
            
        except Exception as e:
            return f"Web search failed: {str(e)}"

@tool
def search_knowledge_base(query: str) -> str:
    """Search the internal math knowledge base for relevant problems and solutions."""
    try:
        from src.knowledge_base.setup import math_kb
        
        results = math_kb.search(query, limit=3)
        
        if not results:
            return "No relevant problems found in knowledge base."
        
        formatted_results = []
        for result in results:
            formatted_results.append(
                f"Problem: {result['problem']}\n"
                f"Solution: {result['solution'][:500]}{'...' if len(result['solution']) > 500 else ''}\n"
                f"Topic: {result['topic']} | Difficulty: {result['difficulty']}\n"
                f"Source: {result['source']} | Relevance: {result['score']:.2f}\n"
                f"---"
            )
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Knowledge base search failed: {str(e)}"

@tool
def search_web(query: str) -> str:
    """Search the web for current mathematics information and research."""
    web_tool = WebSearchTool()
    return web_tool.search_mathematics(query)

# Global instances
web_search_tool = WebSearchTool()