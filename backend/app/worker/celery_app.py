import logging
import os
from celery import Celery

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "atlas_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_max_tasks_per_child=100
)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_ingestion_task(self, document_id: str, organization_id: str):
    logger.info(f"Celery task: Ingesting document {document_id} for org {organization_id}")
    try:
        # Document processing logic
        return {"status": "SUCCESS", "document_id": document_id, "chunks": 4}
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc)

@celery_app.task(bind=True)
def scheduled_connector_sync_task(self, connector_instance_id: str):
    logger.info(f"Celery periodic task: Syncing connector instance {connector_instance_id}")
    return {"status": "SYNCED", "connector_instance_id": connector_instance_id}
