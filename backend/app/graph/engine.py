import re
from typing import Dict, Any, List, Set, Tuple

class KnowledgeEntity:
    def __init__(self, entity_id: str, name: str, entity_type: str, properties: Dict[str, Any]):
        self.entity_id = entity_id
        self.name = name
        self.entity_type = entity_type
        self.properties = properties


class KnowledgeRelationship:
    def __init__(self, source_id: str, target_id: str, rel_type: str, weight: float = 1.0):
        self.source_id = source_id
        self.target_id = target_id
        self.rel_type = rel_type
        self.weight = weight


class KnowledgeGraphEngine:
    """Graph traversal and entity/relationship extraction engine."""

    def __init__(self):
        self.entities: Dict[str, KnowledgeEntity] = {}
        self.relationships: List[KnowledgeRelationship] = []

    def extract_and_index(self, document_id: str, text: str, metadata: Dict[str, Any]) -> Tuple[List[KnowledgeEntity], List[KnowledgeRelationship]]:
        extracted_entities = []
        extracted_rels = []

        # 1. Main Document Entity
        doc_entity = KnowledgeEntity(
            entity_id=f"doc_{document_id}",
            name=metadata.get("file_name", f"Document-{document_id}"),
            entity_type="DOCUMENT",
            properties=metadata
        )
        self.entities[doc_entity.entity_id] = doc_entity
        extracted_entities.append(doc_entity)

        # 2. Extract Author / User Entity
        if "author" in metadata or "owner" in metadata:
            author_name = metadata.get("author") or metadata.get("owner")
            author_id = f"usr_{re.sub(r'\W+', '_', author_name.lower())}"
            if author_id not in self.entities:
                author_entity = KnowledgeEntity(author_id, author_name, "USER", {"role": "AUTHOR"})
                self.entities[author_id] = author_entity
                extracted_entities.append(author_entity)

            rel = KnowledgeRelationship(source_id=author_id, target_id=doc_entity.entity_id, rel_type="AUTHORED")
            self.relationships.append(rel)
            extracted_rels.append(rel)

        # 3. Extract Technology / System Entities
        tech_keywords = ["PostgreSQL", "pgvector", "Zero Trust", "Slack", "Jira", "OpenAI", "Celery", "Redis"]
        for tech in tech_keywords:
            if tech.lower() in text.lower():
                tech_id = f"tech_{tech.lower()}"
                if tech_id not in self.entities:
                    tech_entity = KnowledgeEntity(tech_id, tech, "TECHNOLOGY", {})
                    self.entities[tech_id] = tech_entity
                    extracted_entities.append(tech_entity)

                rel = KnowledgeRelationship(source_id=doc_entity.entity_id, target_id=tech_id, rel_type="REFERENCES")
                self.relationships.append(rel)
                extracted_rels.append(rel)

        return extracted_entities, extracted_rels

    def get_adjacency_graph(self) -> Dict[str, Any]:
        """Export graph JSON structure for visual graph canvas in Next.js UI."""
        nodes = [
            {"id": e.entity_id, "label": e.name, "type": e.entity_type}
            for e in self.entities.values()
        ]
        edges = [
            {"source": r.source_id, "target": r.target_id, "label": r.rel_type}
            for r in self.relationships
        ]
        return {"nodes": nodes, "edges": edges}
