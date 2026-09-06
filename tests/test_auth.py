from fastapi.testclient import TestClient


def test_register_customer(client: TestClient):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test Customer",
            "email": "pytest.customer@example.com",
            "password": "Test@12345",
            "role": "Customer",
        },
    )

    assert response.status_code in (200, 201)


def test_login_customer(client: TestClient):
    # Register first in case the test database is empty.
    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Login Customer",
            "email": "pytest.login@example.com",
            "password": "Test@12345",
            "role": "Customer",
        },
    )

    assert register_response.status_code in (200, 201)

    response = client.post(
        "/auth/login",
        json={
            "email": "pytest.login@example.com",
            "password": "Test@12345",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"].lower() == "bearer"


def test_invalid_login(client: TestClient):
    response = client.post(
        "/auth/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "Wrong@123",
        },
    )

    assert response.status_code in (401, 404)


def test_protected_endpoint_requires_authentication(
    client: TestClient,
):
    response = client.get("/plans")

    assert response.status_code in (401, 403)


def test_customer_cannot_create_plan(client: TestClient):
    email = "pytest.rbac.customer@example.com"
    password = "Test@12345"

    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "RBAC Customer",
            "email": email,
            "password": password,
            "role": "Customer",
        },
    )

    assert register_response.status_code in (200, 201)

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "plan_name": "Unauthorized Test Plan",
            "plan_type": "Life",
            "description": "RBAC test",
            "coverage_amount": 100000,
            "premium_amount": 5000,
            "duration_years": 10,
            "eligibility_age_min": 18,
            "eligibility_age_max": 60,
            "status": "Active",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"