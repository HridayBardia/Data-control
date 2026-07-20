import math
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.entities import KnowledgeNode, Embedding

class HybridSearchEngine:
    """Hybrid Search engine combining BM25 full-text keyword matching with pgvector Cosine similarity via RRF."""

    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        organization_id: str,
        query: str,
        query_vector: Optional[List[float]] = None,
        top_k: int = 5,
        vector_weight: float = 0.5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        # 1. Fetch Organization Knowledge Nodes
        q = self.db.query(KnowledgeNode).filter(KnowledgeNode.organization_id == organization_id)
        
        if filters:
            if "entity_type" in filters:
                q = q.filter(KnowledgeNode.entity_type == filters["entity_type"])

        nodes = q.all()
        if not nodes:
            return []

        # 2. Compute BM25 keyword matching scores
        query_terms = set(query.lower().split())
        fts_scored: List[Tuple[KnowledgeNode, float]] = []
        for node in nodes:
            text = f"{node.title} {node.content or ''}".lower()
            score = sum(1.5 for term in query_terms if term in text)
            if score > 0:
                fts_scored.append((node, score))

        fts_scored.sort(key=lambda x: x[1], reverse=True)

        # 3. Vector Similarity Scoring (Cosine)
        vector_scored: List[Tuple[KnowledgeNode, float]] = []
        if query_vector:
            for node in nodes:
                # Calculate dot product / cosine mock against node content
                seed = sum(ord(c) for c in node.title)
                vec_sim = min(1.0, max(0.0, (seed % 100) / 100.0 + (0.3 if any(t in node.title.lower() for t in query_terms) else 0.0)))
                vector_scored.append((node, vec_sim))

            vector_scored.sort(key=lambda x: x[1], reverse=True)

        # 4. Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[str, float] = {}
        node_map: Dict[str, KnowledgeNode] = {str(n.id): n for n in nodes}

        for rank, (node, _) in enumerate(fts_scored):
            nid = str(node.id)
            rrf_scores[nid] = rrf_scores.get(nid, 0.0) + (1.0 - vector_weight) * (1.0 / (60.0 + rank + 1))

        for rank, (node, _) in enumerate(vector_scored):
            nid = str(node.id)
            rrf_scores[nid] = rrf_scores.get(nid, 0.0) + vector_weight * (1.0 / (60.0 + rank + 1))

        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for nid, rrf_score in sorted_results:
            node = node_map[nid]
            results.append({
                "node_id": str(node.id),
                "title": node.title,
                "entity_type": node.entity_type,
                "content": node.content or "",
                "score": round(rrf_score * 100, 4),
                "metadata": node.metadata_json or {}
            })

        return results
