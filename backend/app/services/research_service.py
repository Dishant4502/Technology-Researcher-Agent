from __future__ import annotations

import re

from fastapi import HTTPException

from app.config import get_settings
from app.agents.crew import build_research_crew
from app.models.schemas import ResearchRequest, ResearchResponse, SearchResult
from app.services.domain_relevance import DomainRelevanceService
from app.services.repository import KnowledgeRepository
from app.services.search import SearchService


class ResearchService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.domain_relevance_service = DomainRelevanceService()
        self.search_service = SearchService()
        self.repository = KnowledgeRepository()

    def run(self, request: ResearchRequest) -> ResearchResponse:
        if not self.domain_relevance_service.is_technology_query(request.query):
            raise HTTPException(
                status_code=400,
                detail=self.domain_relevance_service.rejection_message(),
            )
        if not self.settings.llm_api_key:
            raise HTTPException(
                status_code=500,
                detail="No LLM key configured. Set GROQ_API_KEY (preferred) or OPENAI_API_KEY.",
            )
        sources = self.search_service.search(request.query, request.source_limit)
        crew = build_research_crew(query=request.query, sources=sources, depth=request.depth)
        result = crew.kickoff()
        report = str(result).strip()
        report = self._append_verified_source_notes(report, sources)
        summary = self._extract_summary(report)
        entry = self.repository.save_entry(
            query=request.query,
            report=report,
            summary=summary,
            sources=sources,
        )
        return ResearchResponse(entry=entry, raw_report=report)

    @staticmethod
    def _extract_summary(report: str) -> str:
        cleaned = re.sub(r"#+\s*", "", report)
        first_block = cleaned.split("\n\n")[0].strip()
        return first_block[:320]

    @staticmethod
    def _append_verified_source_notes(report: str, sources: list[SearchResult]) -> str:
        if not sources:
            return report
        report = ResearchService._strip_existing_sources_section(report)
        lines = ["## Sources", ""]
        for index, source in enumerate(sources[:5], start=1):
            lines.append(f"{index}. {source.url}")
        section = "\n".join(lines).strip()
        return f"{report}\n\n{section}"

    @staticmethod
    def _strip_existing_sources_section(report: str) -> str:
        pattern = re.compile(
            r"\n##\s+(Sources|Source Notes|Verified Source Notes)\s*.*\Z",
            re.IGNORECASE | re.DOTALL,
        )
        return re.sub(pattern, "", report).rstrip()
