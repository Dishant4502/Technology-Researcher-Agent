"""Unit tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.models.schemas import ResearchRequest, SearchResult


class TestResearchRequest:
    """Validate the ResearchRequest model constraints."""

    def test_valid_minimal_request(self):
        req = ResearchRequest(query="AI chip market trends")
        assert req.depth == "advanced"
        assert req.source_limit == 6

    def test_valid_full_request(self):
        req = ResearchRequest(query="What is quantum computing?", depth="deep", source_limit=8)
        assert req.depth == "deep"
        assert req.source_limit == 8

    def test_query_too_short_raises(self):
        with pytest.raises(ValidationError):
            ResearchRequest(query="AI")  # < 5 chars

    def test_query_too_long_raises(self):
        with pytest.raises(ValidationError):
            ResearchRequest(query="x" * 301)  # > 300 chars

    def test_invalid_depth_raises(self):
        with pytest.raises(ValidationError):
            ResearchRequest(query="AI chip market", depth="extreme")

    def test_source_limit_below_minimum_raises(self):
        with pytest.raises(ValidationError):
            ResearchRequest(query="AI chip market", source_limit=2)

    def test_source_limit_above_maximum_raises(self):
        with pytest.raises(ValidationError):
            ResearchRequest(query="AI chip market", source_limit=11)

    @pytest.mark.parametrize("depth", ["standard", "advanced", "deep"])
    def test_all_valid_depths(self, depth):
        req = ResearchRequest(query="Test query ok", depth=depth)
        assert req.depth == depth


class TestSearchResult:
    """Validate SearchResult URL parsing and field defaults."""

    def test_valid_search_result(self):
        result = SearchResult(
            title="OpenAI launches GPT-5",
            url="https://example.com/article",
            snippet="A short snippet about AI.",
            source="Tavily",
        )
        assert str(result.url).startswith("https://")

    def test_invalid_url_raises(self):
        with pytest.raises(ValidationError):
            SearchResult(
                title="Bad result",
                url="not-a-url",
                snippet="snippet",
                source="DuckDuckGo",
            )
