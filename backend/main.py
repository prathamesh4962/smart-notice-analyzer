from typing import Annotated

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.analysis_service import analyze_notice


class NoticeRequest(BaseModel):
    text: Annotated[str, Field(min_length=1)]


class DateResult(BaseModel):
    text: str
    normalized_date: str | None
    is_ambiguous: bool
    is_deadline: bool
    context: str


class EntityResult(BaseModel):
    text: str
    label: str


class AnalysisResponse(BaseModel):
    original_text: str
    category: str
    estimated_probability: float
    summary: str
    dates: list[DateResult]
    entities: list[EntityResult]
    action_items: list[str]
    report: str


app = FastAPI(
    title="Smart Notice Analyzer API",
    description="Analyze college notices and extract useful details.",
    version="1.0.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze_notice_endpoint(request: NoticeRequest) -> AnalysisResponse:
    try:
        return AnalysisResponse(**analyze_notice(request.text))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except (FileNotFoundError, RuntimeError, OSError) as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
