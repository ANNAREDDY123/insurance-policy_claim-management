def get_super_admin_token(client):
    email = "pytest.plan.admin@example.com"
    password = "Admin@12345"

    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Plan Test Admin",
            "email": email,
            "password": password,
            "role": "Super Admin",
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

    return login_response.json()["access_token"]


def get_agent_token(client):
    email = "pytest.plan.agent@example.com"
    password = "Agent@12345"

    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Plan Test Agent",
            "email": email,
            "password": password,
            "role": "Insurance Agent",
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

    return login_response.json()["access_token"]


def plan_data(name="Pytest Life Plan"):
    return {
        "plan_name": name,
        "plan_type": "Life",
        "description": "Plan API test",
        "coverage_amount": 1000000,
        "premium_amount": 25000,
        "duration_years": 20,
        "eligibility_age_min": 18,
        "eligibility_age_max": 60,
        "status": "Active",
    }


def test_create_plan_as_agent(client):
    token = get_agent_token(client)

    response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=plan_data(),
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["plan_name"] == "Pytest Life Plan"
    assert data["plan_type"] == "Life"
    assert data["coverage_amount"] == 1000000
    assert data["premium_amount"] == 25000


def test_get_plans(client):
    token = get_agent_token(client)

    response = client.get(
        "/plans",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_plan(client):
    token = get_agent_token(client)

    create_response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=plan_data("Single Plan Test"),
    )

    assert create_response.status_code in (200, 201)

    plan_id = create_response.json()["id"]

    response = client.get(
        f"/plans/{plan_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == plan_id


def test_invalid_coverage_and_premium(client):
    token = get_agent_token(client)

    data = plan_data("Invalid Coverage Plan")

    data["coverage_amount"] = 10000
    data["premium_amount"] = 25000

    response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=data,
    )

    assert response.status_code == 400


def test_update_plan(client):
    token = get_agent_token(client)

    create_response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=plan_data("Update Plan Test"),
    )

    assert create_response.status_code in (200, 201)

    plan_id = create_response.json()["id"]

    response = client.put(
        f"/plans/{plan_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "plan_name": "Updated Plan Name",
        },
    )

    assert response.status_code == 200
    assert response.json()["plan_name"] == "Updated Plan Name"


def test_delete_plan_requires_super_admin(client):
    agent_token = get_agent_token(client)

    create_response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
        json=plan_data("Delete Permission Test"),
    )

    assert create_response.status_code in (200, 201)

    plan_id = create_response.json()["id"]

    response = client.delete(
        f"/plans/{plan_id}",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_super_admin_can_delete_plan(client):
    token = get_super_admin_token(client)

    create_response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=plan_data("Super Admin Delete Test"),
    )

    assert create_response.status_code in (200, 201)

    plan_id = create_response.json()["id"]

    response = client.delete(
        f"/plans/{plan_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200