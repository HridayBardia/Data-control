import re
from collections import deque
from typing import Dict, Any, List, Set, Tuple, Optional

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
    """
    Enterprise Knowledge Graph Engine:
    - Entity & Relationship Extraction
    - Entity Resolution & Alias Merging
    - Graph Traversal (BFS, DFS, Shortest Path)
    - Graph Search & Adjacency Canvas Export
    """

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

        # 3. Extract Technology & System Entities
        tech_keywords = [
            "PostgreSQL", "pgvector", "Zero Trust", "Slack", "Jira", "OpenAI", "Celery", "Redis",
            "Anthropic", "Gemini", "Kubernetes", "Terraform", "Docker", "FastAPI", "Next.js"
        ]
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

    def find_shortest_path(self, start_entity_id: str, end_entity_id: str) -> List[str]:
        """BFS Shortest Path between two nodes in the knowledge graph."""
        if start_entity_id not in self.entities or end_entity_id not in self.entities:
            return []

        adj: Dict[str, List[str]] = {eid: [] for eid in self.entities}
        for rel in self.relationships:
            adj[rel.source_id].append(rel.target_id)
            adj[rel.target_id].append(rel.source_id)

        queue = deque([[start_entity_id]])
        visited = {start_entity_id}

        while queue:
            path = queue.popleft()
            node = path[-1]
            if node == end_entity_id:
                return path

            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        return []

    def graph_search(self, query: str) -> List[Dict[str, Any]]:
        """Search nodes matching query string."""
        q = query.lower()
        results = []
        for e in self.entities.values():
            if q in e.name.lower() or q in e.entity_type.lower():
                results.append({
                    "id": e.entity_id,
                    "name": e.name,
                    "type": e.entity_type,
                    "properties": e.properties
                })
        return results

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
