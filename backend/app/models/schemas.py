from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class SearchResult(BaseModel):
    title: str
    url: HttpUrl
    snippet: str
    source: str


class ResearchRequest(BaseModel):
    query: str = Field(min_length=5, max_length=300)
    depth: str = Field(default="advanced", pattern="^(standard|advanced|deep)$")
    source_limit: int = Field(default=6, ge=3, le=10)


class KnowledgeEntry(BaseModel):
    entry_id: str
    title: str
    query: str
    summary: str
    created_at: datetime
    file_path: str
    sources: list[SearchResult]


class ResearchResponse(BaseModel):
    entry: KnowledgeEntry
    raw_report: str


class EntryDetailResponse(BaseModel):
    entry: KnowledgeEntry
    raw_report: str
