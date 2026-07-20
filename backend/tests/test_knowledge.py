from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_knowledge_ingestion_and_search(client: TestClient, db: Session):
    # 1. Register organization and admin user
    org_data = {"name": "Search Labs", "slug": "search-labs"}
    client.post("/api/v1/auth/register/organization", json=org_data)

    user_data = {
        "email": "searcher@searchlabs.com",
        "password": "securesearchpassword123",
        "full_name": "Search Operator",
        "role": "MEMBER",
        "organization_slug": "search-labs"
    }
    client.post("/api/v1/auth/register/user", json=user_data)

    # Log in to get authorization headers
    login_data = {
        "username": "searcher@searchlabs.com",
        "password": "securesearchpassword123"
    }
    tokens = client.post("/api/v1/auth/login", data=login_data).json()
    auth_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # 2. Ingest a document
    doc_in = {
        "external_id": "doc-101",
        "entity_type": "DOCUMENT",
        "title": "Quantum Physics Research Details",
        "content": "Quantum physics describes the behavior of matter and energy at the atomic and subatomic level. Max Planck is widely considered the pioneer.",
        "metadata_json": {"author": "Max Planck"}
    }
    response = client.post(
        "/api/v1/knowledge/ingest",
        json=doc_in,
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["chunks_created"] > 0

    # 3. Perform semantic search
    search_query = {
        "query": "Who is the pioneer of quantum physics?",
        "limit": 5
    }
    search_response = client.post(
        "/api/v1/knowledge/search",
        json=search_query,
        headers=auth_headers
    )
    assert search_response.status_code == 200
    results = search_response.json()["results"]
    assert len(results) > 0
    assert results[0]["title"] == "Quantum Physics Research Details"
    assert "Planck" in results[0]["chunk_text"]
    assert results[0]["score"] > 0.0  # Cosine similarity should be computed
