from __future__ import annotations

import json
import os
from typing import Any

from langchain_community.tools import DuckDuckGoSearchResults

try:
    from langchain_tavily import TavilySearch

    HAS_LANGCHAIN_TAVILY = True
except ImportError:
    from langchain_community.tools.tavily_search import TavilySearchResults

    HAS_LANGCHAIN_TAVILY = False

from app.config import get_settings
from app.models.schemas import SearchResult


class SearchService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def search(self, query: str, limit: int) -> list[SearchResult]:
        if self.settings.tavily_api_key:
            return self._search_with_tavily(query, limit)
        return self._search_with_duckduckgo(query, limit)

    def _search_with_tavily(self, query: str, limit: int) -> list[SearchResult]:
        os.environ["TAVILY_API_KEY"] = self.settings.tavily_api_key or ""
        if HAS_LANGCHAIN_TAVILY:
            tool = TavilySearch(
                max_results=limit,
                search_depth="advanced",
                include_answer=False,
                include_raw_content=False,
            )
            results = tool.invoke(query)
        else:
            tool = TavilySearchResults(
                api_key=self.settings.tavily_api_key,
                max_results=limit,
                search_depth="advanced",
                include_answer=False,
                include_raw_content=False,
            )
            results = tool.invoke({"query": query})
        parsed = self._coerce_results(results)
        return [self._normalize_result(item, "Tavily") for item in parsed[:limit]]

    def _search_with_duckduckgo(self, query: str, limit: int) -> list[SearchResult]:
        tool = DuckDuckGoSearchResults(output_format="list", num_results=limit)
        results = tool.invoke(query)
        parsed = self._coerce_results(results)
        return [self._normalize_result(item, "DuckDuckGo") for item in parsed[:limit]]

    @staticmethod
    def _coerce_results(results: Any) -> list[dict[str, Any]]:
        if isinstance(results, list):
            return results
        if isinstance(results, dict):
            if isinstance(results.get("results"), list):
                return results["results"]
            if isinstance(results.get("items"), list):
                return results["items"]
            return []
        if isinstance(results, str):
            decoded = json.loads(results)
            if isinstance(decoded, list):
                return decoded
            if isinstance(decoded, dict):
                if isinstance(decoded.get("results"), list):
                    return decoded["results"]
                if isinstance(decoded.get("items"), list):
                    return decoded["items"]
        return []

    @staticmethod
    def _normalize_result(item: dict[str, Any], source_name: str) -> SearchResult:
        url = item.get("url") or item.get("link")
        title = item.get("title") or item.get("snippet", "Untitled source")
        snippet = item.get("content") or item.get("snippet") or "No snippet provided."
        return SearchResult(title=title, url=url, snippet=snippet, source=source_name)
