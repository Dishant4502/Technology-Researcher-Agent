from fastapi import APIRouter, HTTPException

from app.models.schemas import EntryDetailResponse, KnowledgeEntry, ResearchRequest, ResearchResponse
from app.services.repository import KnowledgeRepository
from app.services.research_service import ResearchService


router = APIRouter(prefix="/research", tags=["research"])
research_service = ResearchService()
repository = KnowledgeRepository()


@router.post("", response_model=ResearchResponse)
def run_research(request: ResearchRequest) -> ResearchResponse:
    return research_service.run(request)


@router.get("/entries", response_model=list[KnowledgeEntry])
def list_entries() -> list[KnowledgeEntry]:
    return repository.list_entries()


@router.get("/entries/{entry_id}", response_model=EntryDetailResponse)
def get_entry(entry_id: str) -> EntryDetailResponse:
    record = repository.get_entry_report(entry_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Entry not found.")
    entry, raw_report = record
    return EntryDetailResponse(entry=entry, raw_report=raw_report)
