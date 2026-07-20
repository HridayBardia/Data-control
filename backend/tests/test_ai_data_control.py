import pytest
from app.ai.router import ai_orchestrator
from app.graph.engine import KnowledgeGraphEngine
from app.governance.classifier import data_classifier
from app.governance.lineage import lineage_tracker
from app.policy.engine import policy_engine

@pytest.mark.anyio
async def test_ai_orchestrator_execution():
    res = await ai_orchestrator.execute_query("What is Atlas Zero Trust RAG?")
    assert "provider" in res
    assert "response" in res
    assert res["tokens_used"] > 0

def test_knowledge_graph_extraction():
    graph = KnowledgeGraphEngine()
    entities, rels = graph.extract_and_index("doc_101", "PostgreSQL and pgvector architecture overview", {"author": "Security Team"})
    assert len(entities) >= 2
    adj = graph.get_adjacency_graph()
    assert "nodes" in adj
    assert "edges" in adj

def test_data_classifier_pii_detection():
    sample_text = "Contact support@atlascorp.com or call +1 555-0199 for SSN 123-45-6789 info."
    res = data_classifier.scan_and_classify(sample_text)
    assert res["has_pii"] is True
    assert res["classification"] == "RESTRICTED"

def test_data_lineage_tracker():
    trace = lineage_tracker.generate_lineage_trace("101", "SLACK", "CONFIDENTIAL")
    assert trace["total_steps"] == 18
    assert len(trace["provenance_chain"]) == 18

def test_policy_engine_simulation():
    user_context = {"department": "Finance"}
    resource_meta = {"classification": "CONFIDENTIAL"}
    sim = policy_engine.simulate_policy(user_context, "read", resource_meta)
    assert sim["allowed"] is True
