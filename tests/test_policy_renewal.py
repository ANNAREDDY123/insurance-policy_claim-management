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


def create_test_policy(
    client,
    policy_status="Active",
    end_date=None,
):
    admin_token = register_and_login(
        client,
        "renewal.admin@example.com",
        "Admin@12345",
        "Super Admin",
        "Renewal Test Admin",
    )

    register_and_login(
        client,
        "renewal.agent@example.com",
        "Agent@12345",
        "Insurance Agent",
        "Renewal Test Agent",
    )

    plan_response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "plan_name": "Renewal Test Plan",
            "plan_type": "Life",
            "description": "Plan for renewal testing",
            "coverage_amount": 1000000,
            "premium_amount": 25000,
            "duration_years": 20,
            "eligibility_age_min": 18,
            "eligibility_age_max": 60,
            "status": "Active",
        },
    )

    assert plan_response.status_code in (200, 201)

    plan_id = plan_response.json()["id"]

    customer_response = client.post(
        "/customers",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "full_name": "Renewal Test Customer",
            "email": "renewal.customer@example.com",
            "phone": "9876543010",
            "date_of_birth": "1990-01-01",
            "address": "Hyderabad",
            "identification_number": "RENEW-CUST-001",
            "occupation": "Engineer",
        },
    )

    assert customer_response.status_code in (200, 201)

    customer_id = customer_response.json()["id"]

    if end_date is None:
        end_date = date.today() + timedelta(days=365)

    policy_response = client.post(
        "/policies",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "policy_number": "RENEW-POL-001",
            "customer_id": customer_id,
            "plan_id": plan_id,
            "agent_id": 2,
            "start_date": str(date.today()),
            "end_date": str(end_date),
            "coverage_amount": 1000000,
            "premium_amount": 25000,
            "policy_status": policy_status,
        },
    )

    assert policy_response.status_code in (200, 201)

    policy_id = policy_response.json()["id"]

    return admin_token, policy_id


def test_create_policy_renewal(client):
    token, policy_id = create_test_policy(client)

    response = client.post(
        f"/policies/{policy_id}/renew",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["previous_policy_id"] == policy_id
    assert data["renewed_policy_id"] is not None
    assert data["id"] is not None


def test_renewal_creates_new_policy(client):
    token, policy_id = create_test_policy(client)

    response = client.post(
        f"/policies/{policy_id}/renew",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201

    renewed_policy_id = response.json()[
        "renewed_policy_id"
    ]

    policy_response = client.get(
        f"/policies/{renewed_policy_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert policy_response.status_code == 200

    renewed_policy = policy_response.json()

    assert renewed_policy["id"] == renewed_policy_id
    assert renewed_policy["policy_number"] == (
        "RENEW-POL-001-R1"
    )
    assert renewed_policy["policy_status"] == "Pending"


def test_renewal_generates_new_policy_period(client):
    token, policy_id = create_test_policy(client)

    original_response = client.get(
        f"/policies/{policy_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert original_response.status_code == 200

    original_policy = original_response.json()

    response = client.post(
        f"/policies/{policy_id}/renew",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201

    renewed_policy_id = response.json()[
        "renewed_policy_id"
    ]

    renewed_response = client.get(
        f"/policies/{renewed_policy_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert renewed_response.status_code == 200

    renewed_policy = renewed_response.json()

    expected_start = (
        date.fromisoformat(
            original_policy["end_date"]
        )
        + timedelta(days=1)
    )

    actual_start = date.fromisoformat(
        renewed_policy["start_date"]
    )

    assert actual_start == expected_start


def test_duplicate_renewal_rejected(client):
    token, policy_id = create_test_policy(client)

    first_response = client.post(
        f"/policies/{policy_id}/renew",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/policies/{policy_id}/renew",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert second_response.status_code == 409


def test_cancelled_policy_cannot_be_renewed(client):
    token, policy_id = create_test_policy(
        client,
        policy_status="Cancelled",
    )

    response = client.post(
        f"/policies/{policy_id}/renew",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400


def test_suspended_policy_cannot_be_renewed(client):
    token, policy_id = create_test_policy(
        client,
        policy_status="Suspended",
    )

    response = client.post(
        f"/policies/{policy_id}/renew",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400


def test_inactive_plan_cannot_be_renewed(client):
    token, policy_id = create_test_policy(client)

    policy_response = client.get(
        f"/policies/{policy_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert policy_response.status_code == 200

    plan_id = policy_response.json()["plan_id"]

    plan_response = client.put(
        f"/plans/{plan_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "status": "Inactive"
        },
    )

    assert plan_response.status_code == 200

    response = client.post(
        f"/policies/{policy_id}/renew",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400


def test_get_expiring_policies(client):
    token, policy_id = create_test_policy(
        client,
        end_date=date.today() + timedelta(days=10),
    )

    response = client.get(
        "/policies/expiring?days=30",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert any(
        policy["id"] == policy_id
        for policy in data
    )


def test_expiring_policies_excludes_distant_policy(client):
    token, policy_id = create_test_policy(
        client,
        end_date=date.today() + timedelta(days=100),
    )

    response = client.get(
        "/policies/expiring?days=30",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert not any(
        policy["id"] == policy_id
        for policy in data
    )


def test_policy_renewal_requires_authentication(client):
    response = client.post(
        "/policies/1/renew"
    )

    assert response.status_code in (401, 403)


def test_expiring_policies_requires_authentication(client):
    response = client.get(
        "/policies/expiring"
    )

    assert response.status_code in (401, 403)