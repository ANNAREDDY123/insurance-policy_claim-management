from datetime import date, timedelta


def register_and_login(
    client,
    email,
    password,
    role,
    full_name,
):
    response = client.post(
        "/auth/register",
        json={
            "full_name": full_name,
            "email": email,
            "password": password,
            "role": role,
        },
    )

    assert response.status_code in (200, 201)

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def create_approved_claim(client):
    admin_token = register_and_login(
        client,
        "settlement.admin@example.com",
        "Admin@12345",
        "Super Admin",
        "Settlement Test Admin",
    )

    register_and_login(
        client,
        "settlement.agent@example.com",
        "Agent@12345",
        "Insurance Agent",
        "Settlement Test Agent",
    )

    plan_response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "plan_name": "Settlement Test Plan",
            "plan_type": "Life",
            "description": "Plan for settlement testing",
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
            "full_name": "Settlement Test Customer",
            "email": "settlement.customer@example.com",
            "phone": "9876543003",
            "date_of_birth": "1990-01-01",
            "address": "Hyderabad",
            "identification_number": "SETTLE-CUST-001",
            "occupation": "Engineer",
        },
    )

    assert customer_response.status_code in (200, 201)
    customer_id = customer_response.json()["id"]

    policy_response = client.post(
        "/policies",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "policy_number": "SETTLE-POL-001",
            "customer_id": customer_id,
            "plan_id": plan_id,
            "agent_id": 2,
            "start_date": str(date.today()),
            "end_date": str(
                date.today() + timedelta(days=365)
            ),
            "coverage_amount": 1000000,
            "premium_amount": 25000,
            "policy_status": "Active",
        },
    )

    assert policy_response.status_code in (200, 201)
    policy_id = policy_response.json()["id"]

    claim_response = client.post(
        "/claims",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "claim_number": "SETTLE-CLM-001",
            "policy_id": policy_id,
            "customer_id": customer_id,
            "claim_type": "Accident",
            "incident_date": str(date.today()),
            "claim_amount": 100000,
            "description": "Claim for settlement testing",
            "status": "Submitted",
        },
    )

    assert claim_response.status_code in (200, 201)
    claim_id = claim_response.json()["id"]

    # Submitted -> Under Review
    response = client.post(
        f"/claims/{claim_id}/submit",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
    )

    assert response.status_code == 200

    # Under Review -> Approved
    response = client.post(
        f"/claims/{claim_id}/approve",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
    )

    assert response.status_code == 200

    return admin_token, claim_id


def test_create_settlement(client):
    token, claim_id = create_approved_claim(client)

    response = client.post(
        f"/claims/{claim_id}/settle",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "claim_id": claim_id,
            "settlement_amount": 80000,
            "settlement_status": "Completed",
            "payment_reference": "SET-PAY-001",
            "remarks": "Claim settlement",
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["claim_id"] == claim_id
    assert data["settlement_amount"] == 80000
    assert data["settlement_status"] == "Completed"


def test_get_settlements(client):
    token, claim_id = create_approved_claim(client)

    create_response = client.post(
        f"/claims/{claim_id}/settle",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "claim_id": claim_id,
            "settlement_amount": 75000,
            "settlement_status": "Completed",
            "payment_reference": "SET-PAY-002",
            "remarks": "Settlement",
        },
    )

    assert create_response.status_code in (200, 201)

    response = client.get(
        "/settlements",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_single_settlement(client):
    token, claim_id = create_approved_claim(client)

    create_response = client.post(
        f"/claims/{claim_id}/settle",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "claim_id": claim_id,
            "settlement_amount": 70000,
            "settlement_status": "Completed",
            "payment_reference": "SET-PAY-003",
            "remarks": "Single settlement",
        },
    )

    assert create_response.status_code in (200, 201)

    settlement_id = create_response.json()["id"]

    response = client.get(
        f"/settlements/{settlement_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == settlement_id


def test_settlement_requires_approved_claim(client):
    token = register_and_login(
        client,
        "settlement.pending@example.com",
        "Admin@12345",
        "Super Admin",
        "Pending Settlement Admin",
    )

    response = client.post(
        "/claims/999999/settle",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "claim_id": 999999,
            "settlement_amount": 40000,
            "settlement_status": "Completed",
            "payment_reference": "SET-PAY-004",
            "remarks": "Should fail",
        },
    )

    assert response.status_code == 404


def test_settlement_amount_cannot_exceed_claim(client):
    token, claim_id = create_approved_claim(client)

    response = client.post(
        f"/claims/{claim_id}/settle",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "claim_id": claim_id,
            "settlement_amount": 999999,
            "settlement_status": "Completed",
            "payment_reference": "SET-PAY-005",
            "remarks": "Invalid amount",
        },
    )

    assert response.status_code == 400


def test_duplicate_settlement_rejected(client):
    token, claim_id = create_approved_claim(client)

    payload = {
        "claim_id": claim_id,
        "settlement_amount": 50000,
        "settlement_status": "Completed",
        "payment_reference": "SET-PAY-006",
        "remarks": "Duplicate test",
    }

    first_response = client.post(
        f"/claims/{claim_id}/settle",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=payload,
    )

    assert first_response.status_code in (200, 201)

    second_response = client.post(
        f"/claims/{claim_id}/settle",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=payload,
    )

    assert second_response.status_code == 409


def test_successful_settlement_updates_claim_status(client):
    token, claim_id = create_approved_claim(client)

    response = client.post(
        f"/claims/{claim_id}/settle",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "claim_id": claim_id,
            "settlement_amount": 60000,
            "settlement_status": "Completed",
            "payment_reference": "SET-PAY-007",
            "remarks": "Successful settlement",
        },
    )

    assert response.status_code in (200, 201)

    claim_response = client.get(
        f"/claims/{claim_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert claim_response.status_code == 200
    assert claim_response.json()["status"] == "Settled"


def test_settlement_requires_authentication(client):
    response = client.get("/settlements")

    assert response.status_code in (401, 403)