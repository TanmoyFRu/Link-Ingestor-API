from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.api.schemas.ingest import IngestRequest, IngestResponse, IngestSummaryResponse
from app.domain.services.ingest_service import IngestService
from app.api.v2.services.ingest_service import (
    ingest_page_service,
    get_ingestion_summary_service,
    ingest_page_async_service,
    process_async_ingestion_service
)
import structlog
from datetime import datetime

logger = structlog.get_logger(__name__)
router = APIRouter()

@router.post("/", response_model=IngestResponse)
async def ingest_page(request: IngestRequest):
    return await ingest_page_service(request)

@router.get("/summary", response_model=IngestSummaryResponse)
async def get_ingestion_summary(url: str):
    return await get_ingestion_summary_service(url)

@router.post("/async")
async def ingest_page_async(request: IngestRequest, background_tasks: BackgroundTasks):
    return await ingest_page_async_service(request, background_tasks)

async def _process_async_ingestion(url: str):
    await process_async_ingestion_service(url)



