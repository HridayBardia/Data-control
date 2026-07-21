from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.graph.engine import KnowledgeGraphEngine

router = APIRouter()
graph_engine = KnowledgeGraphEngine()

class GraphExtractRequest(BaseModel):
    document_id: str
    text: str
    metadata: Dict[str, Any]

@router.post("/extract")
def extract_graph_entities(req: GraphExtractRequest):
    entities, rels = graph_engine.extract_and_index(req.document_id, req.text, req.metadata)
    return {
        "document_id": req.document_id,
        "extracted_entities": len(entities),
        "extracted_relationships": len(rels)
    }

@router.get("/adjacency")
def get_adjacency():
    return graph_engine.get_adjacency_graph()
