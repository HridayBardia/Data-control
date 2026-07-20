from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class SearchQuery(BaseModel):
    query: str = Field(..., description="Semantic search query text")
    limit: int = Field(10, ge=1, le=50, description="Max search results to return")
    entity_type: Optional[str] = Field(None, description="Optional entity type filter (e.g., DOCUMENT, EMAIL)")

class SearchResult(BaseModel):
    node_id: UUID
    title: str
    entity_type: str
    external_id: str
    chunk_text: str
    chunk_index: int
    score: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]


class IngestNode(BaseModel):
    external_id: str = Field(..., description="Unique ID from the source system")
    entity_type: str = Field(..., description="Type of entity: DOCUMENT, EMAIL, MEETING, TICKET, TASK")
    title: str = Field(..., description="Title of the resource")
    content: Optional[str] = Field(None, description="Raw text content of the resource")
    metadata_json: Optional[Dict[str, Any]] = Field(None, description="Key-value metadata dictionary")
    connector_instance_id: Optional[UUID] = Field(None, description="Associated connector instance ID")

class IngestResponse(BaseModel):
    success: bool
    node_id: UUID
    chunks_created: int
