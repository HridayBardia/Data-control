import random
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.entities import KnowledgeNode, Embedding, KnowledgeEdge
from app.schemas.knowledge import IngestNode, SearchResult

class KnowledgeService:
    @staticmethod
    def _generate_mock_embedding(text_content: str) -> List[float]:
        """
        Generates a deterministic 1536-dimensional normalized vector from text content.
        This provides a drop-in replacement for OpenAI embeddings in local setups.
        """
        # Seed generator based on text hash to keep it deterministic
        seed = sum(ord(c) for c in text_content) % 100000
        rng = random.Random(seed)
        
        vector = [rng.gauss(0, 1) for _ in range(1536)]
        # Normalize vector
        magnitude = sum(x*x for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        return vector

    @staticmethod
    def chunk_text(content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Chunks raw document content into smaller overlapping pieces for vector search.
        """
        if not content:
            return []
        
        chunks = []
        start = 0
        content_len = len(content)
        
        while start < content_len:
            end = min(start + chunk_size, content_len)
            chunks.append(content[start:end])
            if end == content_len:
                break
            start += chunk_size - overlap
            
        return chunks

    @classmethod
    def ingest_node(
        cls, db: Session, organization_id: UUID, node_in: IngestNode
    ) -> KnowledgeNode:
        """
        Ingests a knowledge node, chunks the content, generates vector embeddings,
        and saves everything inside a tenant-isolated environment.
        """
        # Create or update KnowledgeNode
        node = (
            db.query(KnowledgeNode)
            .filter(
                KnowledgeNode.organization_id == organization_id,
                KnowledgeNode.external_id == node_in.external_id,
                KnowledgeNode.entity_type == node_in.entity_type
            )
            .first()
        )
        
        if node:
            node.title = node_in.title
            node.content = node_in.content
            node.metadata_json = node_in.metadata_json
            node.connector_instance_id = node_in.connector_instance_id
            node.version += 1
            # Clear old embeddings for update
            db.query(Embedding).filter(Embedding.node_id == node.id).delete()
        else:
            node = KnowledgeNode(
                organization_id=organization_id,
                connector_instance_id=node_in.connector_instance_id,
                external_id=node_in.external_id,
                entity_type=node_in.entity_type,
                title=node_in.title,
                content=node_in.content,
                metadata_json=node_in.metadata_json or {},
            )
            db.add(node)
            
        db.flush() # Populate node.id

        # Perform chunking & embedding generation
        if node.content:
            chunks = cls.chunk_text(node.content)
            for idx, chunk in enumerate(chunks):
                vector = cls._generate_mock_embedding(chunk)
                embedding = Embedding(
                    organization_id=organization_id,
                    node_id=node.id,
                    chunk_index=idx,
                    chunk_text=chunk,
                    vector=vector
                )
                db.add(embedding)
                
        db.commit()
        db.refresh(node)
        return node

    @classmethod
    def semantic_search(
        cls, db: Session, organization_id: UUID, query_text: str, limit: int = 10, entity_type: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Performs semantic cosine-similarity vector search against database embeddings.
        Enforces strict organization-based multi-tenant isolation.
        """
        query_vector = cls._generate_mock_embedding(query_text)
        
        # Check if database is SQLite (e.g. during local tests)
        if db.bind and db.bind.dialect.name == "sqlite":
            query = (
                db.query(Embedding, KnowledgeNode)
                .join(KnowledgeNode, Embedding.node_id == KnowledgeNode.id)
                .filter(Embedding.organization_id == organization_id)
            )
            if entity_type:
                query = query.filter(KnowledgeNode.entity_type == entity_type)
            
            all_records = query.all()
            scored = []
            for emb, kn in all_records:
                vec = emb.vector
                if isinstance(vec, str):
                    import json
                    try:
                        vec = json.loads(vec)
                    except Exception:
                        vec = [float(x) for x in vec.strip("[]").split(",") if x.strip()]
                score = sum(a * b for a, b in zip(vec, query_vector))
                scored.append((score, emb, kn))
            
            scored.sort(key=lambda x: x[0], reverse=True)
            scored = scored[:limit]
            
            return [
                SearchResult(
                    chunk_text=emb.chunk_text,
                    chunk_index=emb.chunk_index,
                    node_id=emb.node_id,
                    title=kn.title,
                    entity_type=kn.entity_type,
                    external_id=kn.external_id,
                    score=float(score)
                )
                for score, emb, kn in scored
            ]

        # SQL query using pgvector Cosine Distance operator <=>
        # Cosine similarity is 1 - Cosine Distance
        sql_query = """
            SELECT 
                emb.chunk_text,
                emb.chunk_index,
                emb.node_id,
                kn.title,
                kn.entity_type,
                kn.external_id,
                1 - (emb.vector <=> :query_vector) AS similarity_score
            FROM embeddings emb
            JOIN knowledge_nodes kn ON emb.node_id = kn.id
            WHERE emb.organization_id = :org_id
        """
        
        params = {
            "query_vector": str(query_vector),
            "org_id": organization_id,
            "limit_val": limit
        }
        
        if entity_type:
            sql_query += " AND kn.entity_type = :entity_type"
            params["entity_type"] = entity_type
            
        sql_query += " ORDER BY emb.vector <=> :query_vector ASC LIMIT :limit_val"
        
        results = db.execute(text(sql_query), params).fetchall()
        
        search_results = []
        for row in results:
            search_results.append(
                SearchResult(
                    chunk_text=row[0],
                    chunk_index=row[1],
                    node_id=row[2],
                    title=row[3],
                    entity_type=row[4],
                    external_id=row[5],
                    score=float(row[6])
                )
            )
            
        return search_results
