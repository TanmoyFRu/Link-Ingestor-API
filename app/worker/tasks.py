from celery import Celery
from app.core.config import settings
from app.domain.services.ingest_service import IngestService

# Initialize Celery app
celery_app = Celery('link_ingestor')
celery_app.config_from_object({
    'broker_url': settings.redis_url,
    'result_backend': settings.redis_url,
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'enable_utc': True,
})

@celery_app.task(name='ingest_page')
def ingest_page(url, include_backlinks=False, max_backlinks_per_link=5):
    """Celery task to ingest a page and extract links."""
    ingest_service = IngestService()
    result = ingest_service.ingest_page(
        url=url,
        include_backlinks=include_backlinks,
        max_backlinks_per_link=max_backlinks_per_link
    )
    return result