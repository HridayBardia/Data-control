from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_auth_and_registration_lifecycle(client: TestClient, db: Session):
    # 1. Register organization
    org_data = {"name": "Atlas Corp", "slug": "atlas-corp"}
    response = client.post("/api/v1/auth/register/organization", json=org_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Atlas Corp"
    assert response.json()["slug"] == "atlas-corp"

    # 2. Register user under the organization
    user_data = {
        "email": "admin@atlascorp.com",
        "password": "supersecurepassword123",
        "full_name": "Atlas Admin",
        "role": "ADMIN",
        "organization_slug": "atlas-corp"
    }
    response = client.post("/api/v1/auth/register/user", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == "admin@atlascorp.com"
    assert response.json()["role"] == "ADMIN"

    # 3. Attempt login with credentials
    login_data = {
        "username": "admin@atlascorp.com",
        "password": "supersecurepassword123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

    # 4. Get active user details using token
    access_token = tokens["access_token"]
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "admin@atlascorp.com"
    assert response.json()["full_name"] == "Atlas Admin"
