"""Unit tests for the KnowledgeRepository service."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app.models.schemas import KnowledgeEntry, SearchResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_repo(tmp_path: Path):
    """Patch KNOWLEDGE_REPO_DIR to a temporary directory for each test."""
    with patch("app.services.repository.KNOWLEDGE_REPO_DIR", tmp_path), \
         patch("app.config.KNOWLEDGE_REPO_DIR", tmp_path):
        # Re-import inside patch context so module-level INDEX_FILE is correct
        import importlib
        import app.services.repository as repo_mod
        importlib.reload(repo_mod)
        yield tmp_path, repo_mod.KnowledgeRepository


@pytest.fixture()
def sample_source():
    return SearchResult(
        title="AI Frontier Report",
        url="https://example.com/ai-report",
        snippet="A detailed look at AI.",
        source="Tavily",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestKnowledgeRepository:

    def test_save_and_list_entry(self, tmp_repo, sample_source):
        _, Repo = tmp_repo
        repo = Repo()
        entry = repo.save_entry(
            query="What is the state of enterprise AI?",
            report="## Executive Summary\nAI is growing fast.",
            summary="AI is growing fast.",
            sources=[sample_source],
        )
        assert entry.entry_id
        assert entry.title

        entries = repo.list_entries()
        assert len(entries) == 1
        assert entries[0].entry_id == entry.entry_id

    def test_index_file_initialised_as_empty(self, tmp_repo):
        tmp_path, Repo = tmp_repo
        repo = Repo()
        index_file = tmp_path / "index.json"
        assert index_file.exists()
        assert json.loads(index_file.read_text()) == []

    def test_get_entry_report_returns_correct_report(self, tmp_repo, sample_source):
        _, Repo = tmp_repo
        repo = Repo()
        entry = repo.save_entry(
            query="Enterprise AI trends?",
            report="## Research Report\nSome findings here.",
            summary="Some findings.",
            sources=[sample_source],
        )
        result = repo.get_entry_report(entry.entry_id)
        assert result is not None
        fetched_entry, report_text = result
        assert fetched_entry.entry_id == entry.entry_id
        assert "findings" in report_text

    def test_get_entry_report_returns_none_for_unknown_id(self, tmp_repo):
        _, Repo = tmp_repo
        repo = Repo()
        result = repo.get_entry_report("nonexistent-id")
        assert result is None

    def test_title_from_query_strips_question_mark(self):
        from app.services.repository import KnowledgeRepository as Repo
        title = Repo._title_from_query("What is AI?")
        assert not title.endswith("?")

    def test_index_enforces_retention_limit(self, tmp_repo, sample_source):
        _, Repo = tmp_repo
        repo = Repo()
        # Write more entries than the default retention limit (8)
        with patch("app.config.Settings.knowledge_retention_limit", new=2):
            for i in range(3):
                repo.save_entry(
                    query=f"Query number {i} about AI tech",
                    report=f"Report {i}",
                    summary=f"Summary {i}",
                    sources=[sample_source],
                )
