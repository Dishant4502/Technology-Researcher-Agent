from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.rag_service import RagService


router = APIRouter(prefix="/rag", tags=["rag"])
rag_service = RagService()


class RagQueryRequest(BaseModel):
    query: str


class RagSource(BaseModel):
    content: str
    metadata: dict[str, Any]


class RagQueryResponse(BaseModel):
    answer: str
    sources: list[RagSource]


@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)) -> dict[str, Any]:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        doc_ids = rag_service.ingest_pdf(file)
        return {"message": f"Successfully processed {file.filename}", "chunks": len(doc_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=RagQueryResponse)
def chat(request: RagQueryRequest) -> RagQueryResponse:
    try:
        result = rag_service.ask_question(request.query)
        return RagQueryResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
