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


def create_test_policy(client):
    token = register_and_login(
        client,
        "beneficiary.agent@example.com",
        "Agent@12345",
        "Insurance Agent",
        "Beneficiary Test Agent",
    )

    plan_response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "plan_name": "Beneficiary Test Plan",
            "plan_type": "Life",
            "description": "Beneficiary test plan",
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
            "Authorization": f"Bearer {token}"
        },
        json={
            "full_name": "Beneficiary Customer",
            "email": "beneficiary.customer@example.com",
            "phone": "9876543210",
            "date_of_birth": "1995-06-15",
            "address": "Hyderabad",
            "identification_number": "BEN-CUST-001",
            "occupation": "Engineer",
        },
    )

    assert customer_response.status_code in (200, 201)

    customer_id = customer_response.json()["id"]

    policy_response = client.post(
        "/policies",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "policy_number": "BEN-POL-001",
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

    assert policy_response.status_code in (200, 201)

    return token, policy_response.json()["id"]


def test_create_beneficiary(client):
    token, policy_id = create_test_policy(client)

    response = client.post(
        f"/policies/{policy_id}/beneficiaries",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Priya Reddy",
            "relationship": "Spouse",
            "percentage": 100,
            "phone": "9876543211",
            "identification_number": "BEN-ID-001",
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["policy_id"] == policy_id
    assert data["name"] == "Priya Reddy"
    assert data["percentage"] == 100


def test_get_beneficiaries(client):
    token, policy_id = create_test_policy(client)

    create_response = client.post(
        f"/policies/{policy_id}/beneficiaries",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Get Test Beneficiary",
            "relationship": "Parent",
            "percentage": 100,
            "phone": "9876543212",
            "identification_number": "BEN-ID-002",
        },
    )

    assert create_response.status_code in (200, 201)

    response = client.get(
        f"/policies/{policy_id}/beneficiaries",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_beneficiary_percentage_cannot_exceed_100(client):
    token, policy_id = create_test_policy(client)

    first_response = client.post(
        f"/policies/{policy_id}/beneficiaries",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "First Beneficiary",
            "relationship": "Spouse",
            "percentage": 60,
            "phone": "9876543213",
            "identification_number": "BEN-ID-003",
        },
    )

    assert first_response.status_code in (200, 201)

    second_response = client.post(
        f"/policies/{policy_id}/beneficiaries",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Second Beneficiary",
            "relationship": "Child",
            "percentage": 50,
            "phone": "9876543214",
            "identification_number": "BEN-ID-004",
        },
    )

    assert second_response.status_code == 400
    assert (
        second_response.json()["detail"]
        == "Beneficiary percentages cannot exceed 100%"
    )


def test_duplicate_beneficiary_rejected(client):
    token, policy_id = create_test_policy(client)

    data = {
        "name": "Duplicate Beneficiary",
        "relationship": "Spouse",
        "percentage": 100,
        "phone": "9876543215",
        "identification_number": "BEN-ID-005",
    }

    first_response = client.post(
        f"/policies/{policy_id}/beneficiaries",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=data,
    )

    assert first_response.status_code in (200, 201)

    second_response = client.post(
        f"/policies/{policy_id}/beneficiaries",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=data,
    )

    assert second_response.status_code == 409


def test_update_beneficiary(client):
    token, policy_id = create_test_policy(client)

    create_response = client.post(
        f"/policies/{policy_id}/beneficiaries",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Original Name",
            "relationship": "Spouse",
            "percentage": 100,
            "phone": "9876543216",
            "identification_number": "BEN-ID-006",
        },
    )

    assert create_response.status_code in (200, 201)

    beneficiary_id = create_response.json()["id"]

    response = client.put(
        f"/beneficiaries/{beneficiary_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Updated Name",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_delete_beneficiary(client):
    token, policy_id = create_test_policy(client)

    create_response = client.post(
        f"/policies/{policy_id}/beneficiaries",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Delete Beneficiary",
            "relationship": "Child",
            "percentage": 100,
            "phone": "9876543217",
            "identification_number": "BEN-ID-007",
        },
    )

    assert create_response.status_code in (200, 201)

    beneficiary_id = create_response.json()["id"]

    response = client.delete(
        f"/beneficiaries/{beneficiary_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["message"]
        == "Beneficiary deleted successfully"
    )