from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.api.schemas.ingest import IngestRequest, IngestResponse, IngestSummaryResponse
from app.domain.services.ingest_service import IngestService
import structlog
from datetime import datetime

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=IngestResponse)
async def ingest_page(request: IngestRequest):
    """Ingest a web page and extract all links with backlinks."""
    try:
        logger.info("Received ingestion request", url=str(request.url))
        
        # Create ingestion service
        ingest_service = IngestService()
        
        # Process the page
        result = await ingest_service.ingest_page(str(request.url))
        
        # Convert to response format
        links_response = []
        for link in result.links:
            links_response.append({
                "url": link.url,
                "title": link.title,
                "description": link.description,
                "source_url": link.source_url,
                "domain": link.domain,
                "is_external": link.link_type == "external",
                "link_text": link.link_text,
                "created_at": link.created_at
            })
        
        backlinks_response = []
        for backlink in result.backlinks:
            backlinks_response.append({
                "backlink_url": backlink.backlink_url,
                "backlink_title": backlink.backlink_title,
                "backlink_domain": backlink.backlink_domain,
                "anchor_text": backlink.anchor_text,
                "created_at": backlink.created_at
            })
        
        response = IngestResponse(
            job_id=f"job_{hash(str(request.url))}",
            source_url=str(request.url),
            status=result.job.status,
            total_links_found=result.total_links,
            total_backlinks_found=result.total_backlinks,
            links=links_response,
            backlinks=backlinks_response,
            created_at=result.job.created_at or datetime.now(),
            completed_at=result.job.completed_at,
            error_message=result.job.error_message
        )
        
        logger.info("Ingestion completed successfully", 
                   url=str(request.url),
                   links_found=result.total_links,
                   backlinks_found=result.total_backlinks)
        
        return response
        
    except Exception as e:
        logger.error("Error during ingestion", url=str(request.url), error=str(e))
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/summary", response_model=IngestSummaryResponse)
async def get_ingestion_summary(url: str):
    """Get a summary of what would be ingested without full processing."""
    try:
        logger.info("Received summary request", url=url)
        
        ingest_service = IngestService()
        summary = await ingest_service.get_ingestion_summary(url)
        
        if "error" in summary:
            raise HTTPException(status_code=400, detail=summary["error"])
        
        return IngestSummaryResponse(**summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting ingestion summary", url=url, error=str(e))
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


@router.post("/async")
async def ingest_page_async(request: IngestRequest, background_tasks: BackgroundTasks):
    """Start an asynchronous ingestion job."""
    try:
        logger.info("Starting async ingestion", url=str(request.url))
        
        # For now, just return a job ID - in a real implementation,
        # this would queue the job with Celery
        job_id = f"async_job_{hash(str(request.url))}"
        
        # Add to background tasks (simplified version)
        background_tasks.add_task(_process_async_ingestion, str(request.url))
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Ingestion job has been queued for processing"
        }
        
    except Exception as e:
        logger.error("Error queuing async ingestion", url=str(request.url), error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to queue job: {str(e)}")


async def _process_async_ingestion(url: str):
    """Background task for async ingestion."""
    try:
        ingest_service = IngestService()
        await ingest_service.ingest_page(url)
        logger.info("Async ingestion completed", url=url)
    except Exception as e:
        logger.error("Async ingestion failed", url=url, error=str(e))


