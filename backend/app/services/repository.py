from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from slugify import slugify

from app.config import KNOWLEDGE_REPO_DIR, get_settings
from app.models.schemas import KnowledgeEntry, SearchResult


INDEX_FILE = KNOWLEDGE_REPO_DIR / "index.json"


class KnowledgeRepository:
    def __init__(self) -> None:
        self.settings = get_settings()
        KNOWLEDGE_REPO_DIR.mkdir(parents=True, exist_ok=True)
        if not INDEX_FILE.exists():
            INDEX_FILE.write_text("[]", encoding="utf-8")
        self._enforce_retention()

    def save_entry(self, query: str, report: str, summary: str, sources: list[SearchResult]) -> KnowledgeEntry:
        created_at = datetime.now(timezone.utc)
        title = self._title_from_query(query)
        entry_id = f"{created_at.strftime('%Y%m%d%H%M%S')}-{slugify(title)[:48]}"
        file_path = KNOWLEDGE_REPO_DIR / f"{entry_id}.md"

        body = self._build_document(title=title, query=query, created_at=created_at, report=report, sources=sources)
        file_path.write_text(body, encoding="utf-8")

        entry = KnowledgeEntry(
            entry_id=entry_id,
            title=title,
            query=query,
            summary=summary,
            created_at=created_at,
            file_path=str(file_path),
            sources=sources,
        )
        index = self.list_entries()
        index.insert(0, entry)
        self._write_index(index)
        return entry

    def list_entries(self) -> list[KnowledgeEntry]:
        raw = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        entries = [KnowledgeEntry.model_validate(item) for item in raw]
        trimmed_entries = entries[: self.settings.knowledge_retention_limit]
        if len(trimmed_entries) != len(entries):
            self._remove_stale_files(entries[self.settings.knowledge_retention_limit :])
            self._write_index(trimmed_entries)
        return trimmed_entries

    def get_entry_report(self, entry_id: str) -> tuple[KnowledgeEntry, str] | None:
        for entry in self.list_entries():
            if entry.entry_id != entry_id:
                continue
            path = Path(entry.file_path)
            if not path.exists():
                return None
            full_text = path.read_text(encoding="utf-8")
            report = self._extract_report_section(full_text)
            return entry, report
        return None

    @staticmethod
    def _title_from_query(query: str) -> str:
        return query[:80].rstrip("?").strip().title()

    @staticmethod
    def _build_document(
        title: str,
        query: str,
        created_at: datetime,
        report: str,
        sources: list[SearchResult],
    ) -> str:
        source_lines = "\n".join(
            f"- {source.title} ({source.source}): {source.url}" for source in sources
        )
        return (
            f"# {title}\n\n"
            f"Generated: {created_at.isoformat()}\n"
            f"Query: {query}\n\n"
            f"## Research Report\n\n{report}\n\n"
            f"## Source Registry\n{source_lines}\n"
        )

    @staticmethod
    def _remove_stale_files(stale_entries: list[KnowledgeEntry]) -> None:
        repo_root = KNOWLEDGE_REPO_DIR.resolve()
        for stale in stale_entries:
            stale_path = Path(stale.file_path)
            try:
                resolved = stale_path.resolve()
                resolved.relative_to(repo_root)
            except (OSError, ValueError):
                continue
            if resolved.exists():
                resolved.unlink()

    def _enforce_retention(self) -> None:
        raw = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        entries = [KnowledgeEntry.model_validate(item) for item in raw]
        trimmed_entries = entries[: self.settings.knowledge_retention_limit]
        if len(trimmed_entries) != len(entries):
            self._remove_stale_files(entries[self.settings.knowledge_retention_limit :])
            self._write_index(trimmed_entries)

    @staticmethod
    def _write_index(entries: list[KnowledgeEntry]) -> None:
        INDEX_FILE.write_text(
            json.dumps([item.model_dump(mode="json") for item in entries], indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _extract_report_section(document: str) -> str:
        marker = "## Research Report"
        source_marker = "## Source Registry"
        start = document.find(marker)
        if start == -1:
            return document.strip()
        body_start = start + len(marker)
        report_plus_tail = document[body_start:].lstrip()
        end = report_plus_tail.find(source_marker)
        if end == -1:
            return report_plus_tail.strip()
        return report_plus_tail[:end].strip()
