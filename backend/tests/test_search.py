"""Unit tests for the SearchService result normaliser (no network calls)."""

import pytest

from app.services.search import SearchService


class TestSearchServiceCoercion:
    """Test the _coerce_results and _normalize_result static helpers."""

    def test_coerce_list_of_dicts(self):
        raw = [{"title": "A", "url": "https://a.com", "content": "snippet A"}]
        assert SearchService._coerce_results(raw) == raw

    def test_coerce_dict_with_results_key(self):
        raw = {"results": [{"title": "B"}]}
        assert SearchService._coerce_results(raw) == [{"title": "B"}]

    def test_coerce_dict_with_items_key(self):
        raw = {"items": [{"title": "C"}]}
        assert SearchService._coerce_results(raw) == [{"title": "C"}]

    def test_coerce_empty_dict_returns_empty_list(self):
        assert SearchService._coerce_results({}) == []

    def test_coerce_json_string(self):
        import json
        raw = json.dumps([{"title": "D", "url": "https://d.com"}])
        assert SearchService._coerce_results(raw) == [{"title": "D", "url": "https://d.com"}]

    def test_normalize_result_prefers_url_over_link(self):
        item = {"url": "https://pref.com", "link": "https://fallback.com", "title": "T", "content": "s"}
        result = SearchService._normalize_result(item, "Tavily")
        assert "pref.com" in str(result.url)

    def test_normalize_result_falls_back_to_link(self):
        item = {"link": "https://fallback.com", "title": "T", "snippet": "s"}
        result = SearchService._normalize_result(item, "DuckDuckGo")
        assert "fallback.com" in str(result.url)

    def test_normalize_result_sets_source_name(self):
        item = {"url": "https://x.com", "title": "X", "content": "x content"}
        result = SearchService._normalize_result(item, "Tavily")
        assert result.source == "Tavily"
