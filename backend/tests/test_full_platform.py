import pytest
from app.ai.router import ai_orchestrator
from app.graph.engine import KnowledgeGraphEngine
from app.governance.classifier import data_classifier
from app.policy.engine import policy_engine
from app.connectors.engine import GoogleDriveConnector, ConnectorInstance
from app.services.search import HybridSearchEngine
import uuid

@pytest.mark.anyio
async def test_ai_orchestrator_multi_provider_routing():
    res = await ai_orchestrator.execute_query(
        prompt="Explain Zero Trust Data Governance",
        preferred_provider="gemini"
    )
    assert res["status"] == "SUCCESS"
    assert "provider" in res
    assert res["tokens_used"] > 0
    assert res["cost_usd"] >= 0.0

def test_knowledge_graph_traversal_shortest_path():
    graph = KnowledgeGraphEngine()
    graph.extract_and_index("doc1", "PostgreSQL and pgvector architecture overview", {"author": "Alice"})
    graph.extract_and_index("doc2", "pgvector and Zero Trust security integration", {"author": "Bob"})

    shortest_path = graph.find_shortest_path("usr_alice", "doc_doc1")
    assert len(shortest_path) == 2
    assert shortest_path == ["usr_alice", "doc_doc1"]

def test_data_classifier_multi_pii_detection():
    sample_text = "AWS Secret AKIAIOSFODNN7EXAMPLE and IBAN GB82WEST12345698765432 with SSN 000-12-3456."
    res = data_classifier.scan_and_classify(sample_text)
    assert res["has_pii"] is True
    assert res["classification"] == "RESTRICTED"
    assert res["retention_policy_years"] == 7
    assert len(res["findings"]) >= 2

def test_policy_engine_simulation_allow_and_deny():
    finance_user = {"department": "Finance"}
    eng_user = {"department": "Engineering"}
    resource_meta = {"classification": "INTERNAL"}

    allow_sim = policy_engine.simulate_policy(finance_user, "read", resource_meta)
    assert allow_sim["allowed"] is True

    deny_sim = policy_engine.simulate_policy(eng_user, "read", resource_meta)
    assert deny_sim["allowed"] is False
