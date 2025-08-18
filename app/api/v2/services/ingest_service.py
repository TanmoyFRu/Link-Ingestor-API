import structlog
from datetime import datetime
from fastapi import HTTPException, BackgroundTasks
from app.api.schemas.ingest import IngestRequest, IngestResponse, IngestSummaryResponse
from app.domain.services.ingest_service import IngestService

logger = structlog.get_logger(__name__)

def ingest_page_service(request: IngestRequest):
    async def inner():
        try:
            logger.info("Received ingestion request", url=str(request.url))
            ingest_service = IngestService()
            result = await ingest_service.ingest_page(str(request.url))
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
            logger.info("Ingestion completed successfully", url=str(request.url), links_found=result.total_links, backlinks_found=result.total_backlinks)
            return response
        except Exception as e:
            logger.error("Error during ingestion", url=str(request.url), error=str(e))
            raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    return inner()

def get_ingestion_summary_service(url: str):
    async def inner():
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
    return inner()

def ingest_page_async_service(request: IngestRequest, background_tasks: BackgroundTasks):
    async def inner():
        try:
            logger.info("Starting async ingestion", url=str(request.url))
            job_id = f"async_job_{hash(str(request.url))}"
            background_tasks.add_task(process_async_ingestion_service, str(request.url))
            return {
                "job_id": job_id,
                "status": "queued",
                "message": "Ingestion job has been queued for processing"
            }
        except Exception as e:
            logger.error("Error queuing async ingestion", url=str(request.url), error=str(e))
            raise HTTPException(status_code=500, detail=f"Failed to queue job: {str(e)}")
    return inner()

def process_async_ingestion_service(url: str):
    async def inner():
        try:
            ingest_service = IngestService()
            await ingest_service.ingest_page(url)
            logger.info("Async ingestion completed", url=url)
        except Exception as e:
            logger.error("Async ingestion failed", url=url, error=str(e))
    return inner()