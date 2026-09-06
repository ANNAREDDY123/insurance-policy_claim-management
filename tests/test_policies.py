from datetime import date, timedelta


def register_and_login(
    client,
    email,
    password,
    role,
    full_name,
):
    register_response = client.post(
        "/auth/register",
        json={
            "full_name": full_name,
            "email": email,
            "password": password,
            "role": role,
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


def create_plan(client, token):
    response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "plan_name": "Policy Test Life Plan",
            "plan_type": "Life",
            "description": "Policy testing plan",
            "coverage_amount": 1000000,
            "premium_amount": 25000,
            "duration_years": 20,
            "eligibility_age_min": 18,
            "eligibility_age_max": 60,
            "status": "Active",
        },
    )

    assert response.status_code in (200, 201)

    return response.json()["id"]


def create_customer(client, token):
    response = client.post(
        "/customers",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "full_name": "Policy Test Customer",
            "email": "policy.customer@example.com",
            "phone": "9876543210",
            "date_of_birth": "1995-06-15",
            "address": "Hyderabad",
            "identification_number": "POLICY-ID-001",
            "occupation": "Engineer",
        },
    )

    assert response.status_code in (200, 201)

    return response.json()["id"]


def test_create_policy(client):
    token = register_and_login(
        client,
        "policy.agent@example.com",
        "Agent@12345",
        "Insurance Agent",
        "Policy Test Agent",
    )

    plan_id = create_plan(
        client,
        token,
    )

    customer_id = create_customer(
        client,
        token,
    )

    response = client.post(
        "/policies",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "policy_number": "POL-TEST-001",
            "customer_id": customer_id,
            "plan_id": plan_id,
            "agent_id": 1,
            "start_date": str(date.today()),
            "end_date": str(
                date.today() + timedelta(days=365)
            ),
            "coverage_amount": 1000000,
            "premium_amount": 25000,
            "policy_status": "Pending",
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["policy_number"] == "POL-TEST-001"
    assert data["customer_id"] == customer_id
    assert data["plan_id"] == plan_id
    assert data["policy_status"] == "Pending"


def test_get_policies(client):
    token = register_and_login(
        client,
        "policy.get.agent@example.com",
        "Agent@12345",
        "Insurance Agent",
        "Policy Get Agent",
    )

    response = client.get(
        "/policies",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_policy_invalid_dates(client):
    token = register_and_login(
        client,
        "policy.date.agent@example.com",
        "Agent@12345",
        "Insurance Agent",
        "Policy Date Agent",
    )

    plan_id = create_plan(
        client,
        token,
    )

    customer_id = create_customer(
        client,
        token,
    )

    response = client.post(
        "/policies",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "policy_number": "POL-INVALID-DATE",
            "customer_id": customer_id,
            "plan_id": plan_id,
            "agent_id": 1,
            "start_date": "2026-12-31",
            "end_date": "2026-01-01",
            "coverage_amount": 1000000,
            "premium_amount": 25000,
            "policy_status": "Pending",
        },
    )

    assert response.status_code == 400


def test_create_policy_invalid_coverage(client):
    token = register_and_login(
        client,
        "policy.coverage.agent@example.com",
        "Agent@12345",
        "Insurance Agent",
        "Policy Coverage Agent",
    )

    plan_id = create_plan(
        client,
        token,
    )

    customer_id = create_customer(
        client,
        token,
    )

    response = client.post(
        "/policies",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "policy_number": "POL-INVALID-COVERAGE",
            "customer_id": customer_id,
            "plan_id": plan_id,
            "agent_id": 1,
            "start_date": str(date.today()),
            "end_date": str(
                date.today() + timedelta(days=365)
            ),
            "coverage_amount": 10000,
            "premium_amount": 25000,
            "policy_status": "Pending",
        },
    )

    assert response.status_code == 400


def test_activate_policy(client):
    token = register_and_login(
        client,
        "policy.activate.agent@example.com",
        "Agent@12345",
        "Insurance Agent",
        "Policy Activate Agent",
    )

    plan_id = create_plan(
        client,
        token,
    )

    customer_id = create_customer(
        client,
        token,
    )

    create_response = client.post(
        "/policies",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "policy_number": "POL-ACTIVATE-001",
            "customer_id": customer_id,
            "plan_id": plan_id,
            "agent_id": 1,
            "start_date": str(date.today()),
            "end_date": str(
                date.today() + timedelta(days=365)
            ),
            "coverage_amount": 1000000,
            "premium_amount": 25000,
            "policy_status": "Pending",
        },
    )

    assert create_response.status_code in (200, 201)

    policy_id = create_response.json()["id"]

    response = client.post(
        f"/policies/{policy_id}/activate",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["policy_status"] == "Active"


def test_cancel_policy(client):
    token = register_and_login(
        client,
        "policy.cancel.agent@example.com",
        "Agent@12345",
        "Insurance Agent",
        "Policy Cancel Agent",
    )

    plan_id = create_plan(
        client,
        token,
    )

    customer_id = create_customer(
        client,
        token,
    )

    create_response = client.post(
        "/policies",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "policy_number": "POL-CANCEL-001",
            "customer_id": customer_id,
            "plan_id": plan_id,
            "agent_id": 1,
            "start_date": str(date.today()),
            "end_date": str(
                date.today() + timedelta(days=365)
            ),
            "coverage_amount": 1000000,
            "premium_amount": 25000,
            "policy_status": "Pending",
        },
    )

    assert create_response.status_code in (200, 201)

    policy_id = create_response.json()["id"]

    response = client.post(
        f"/policies/{policy_id}/cancel",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["policy_status"] == "Cancelled"