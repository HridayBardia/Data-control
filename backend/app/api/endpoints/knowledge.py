from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user, get_current_tenant_org
from app.schemas.knowledge import IngestNode, IngestResponse, SearchQuery, SearchResponse
from app.services.knowledge import KnowledgeService
from app.models.entities import User

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
def ingest_record(
    node_in: IngestNode,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ingests and vectorizes enterprise documents/records. Scoped by user organization.
    """
    try:
        node = KnowledgeService.ingest_node(
            db=db,
            organization_id=current_user.organization_id,
            node_in=node_in
        )
        return IngestResponse(
            success=True,
            node_id=node.id,
            chunks_created=len(node.embeddings)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse)
def search_records(
    query_in: SearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Performs semantic vector search over the organization's knowledge graph and assets.
    """
    try:
        results = KnowledgeService.semantic_search(
            db=db,
            organization_id=current_user.organization_id,
            query_text=query_in.query,
            limit=query_in.limit,
            entity_type=query_in.entity_type
        )
        return SearchResponse(
            query=query_in.query,
            results=results
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search query failed: {str(e)}"
        )
