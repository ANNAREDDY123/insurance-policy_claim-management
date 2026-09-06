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


def create_active_policy(client):
    agent_token = register_and_login(
        client,
        "claim.agent@example.com",
        "Agent@12345",
        "Insurance Agent",
        "Claim Test Agent",
    )

    admin_token = register_and_login(
        client,
        "claim.admin@example.com",
        "Admin@12345",
        "Super Admin",
        "Claim Test Admin",
    )

    plan_response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
        json={
            "plan_name": "Claim Test Plan",
            "plan_type": "Life",
            "description": "Plan for claim testing",
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
            "Authorization": f"Bearer {agent_token}"
        },
        json={
            "full_name": "Claim Test Customer",
            "email": "claim.customer@example.com",
            "phone": "9876543100",
            "date_of_birth": "1990-06-15",
            "address": "Hyderabad",
            "identification_number": "CLAIM-CUST-001",
            "occupation": "Engineer",
        },
    )

    assert customer_response.status_code in (200, 201)

    customer_id = customer_response.json()["id"]

    policy_response = client.post(
        "/policies",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
        json={
            "policy_number": "CLAIM-POL-001",
            "customer_id": customer_id,
            "plan_id": plan_id,
            "agent_id": 1,
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

    return (
        admin_token,
        agent_token,
        policy_id,
        customer_id,
    )


def test_create_claim(client):
    admin_token, _, policy_id, customer_id = (
        create_active_policy(client)
    )

    response = client.post(
        "/claims",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "claim_number": "CLM-TEST-001",
            "policy_id": policy_id,
            "customer_id": customer_id,
            "claim_type": "Accident",
            "incident_date": str(date.today()),
            "claim_amount": 200000,
            "description": "Accident claim for testing",
            "status": "Submitted",
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["claim_number"] == "CLM-TEST-001"
    assert data["policy_id"] == policy_id
    assert data["customer_id"] == customer_id
    assert data["claim_amount"] == 200000


def test_get_claims(client):
    admin_token, _, policy_id, customer_id = (
        create_active_policy(client)
    )

    create_response = client.post(
        "/claims",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "claim_number": "CLM-GET-001",
            "policy_id": policy_id,
            "customer_id": customer_id,
            "claim_type": "Health",
            "incident_date": str(date.today()),
            "claim_amount": 100000,
            "description": "Health claim testing",
            "status": "Submitted",
        },
    )

    assert create_response.status_code in (200, 201)

    response = client.get(
        "/claims",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_claim(client):
    admin_token, _, policy_id, customer_id = (
        create_active_policy(client)
    )

    create_response = client.post(
        "/claims",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "claim_number": "CLM-SINGLE-001",
            "policy_id": policy_id,
            "customer_id": customer_id,
            "claim_type": "Accident",
            "incident_date": str(date.today()),
            "claim_amount": 150000,
            "description": "Single claim testing",
            "status": "Submitted",
        },
    )

    assert create_response.status_code in (200, 201)

    claim_id = create_response.json()["id"]

    response = client.get(
        f"/claims/{claim_id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == claim_id


def test_claim_amount_cannot_exceed_coverage(client):
    admin_token, _, policy_id, customer_id = (
        create_active_policy(client)
    )

    response = client.post(
        "/claims",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "claim_number": "CLM-AMOUNT-001",
            "policy_id": policy_id,
            "customer_id": customer_id,
            "claim_type": "Accident",
            "incident_date": str(date.today()),
            "claim_amount": 2000000,
            "description": "Amount validation test",
            "status": "Submitted",
        },
    )

    assert response.status_code == 400


def test_claim_incident_date_must_be_within_policy(client):
    admin_token, _, policy_id, customer_id = (
        create_active_policy(client)
    )

    invalid_date = date.today() + timedelta(days=500)

    response = client.post(
        "/claims",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "claim_number": "CLM-DATE-001",
            "policy_id": policy_id,
            "customer_id": customer_id,
            "claim_type": "Accident",
            "incident_date": str(invalid_date),
            "claim_amount": 100000,
            "description": "Date validation test",
            "status": "Submitted",
        },
    )

    assert response.status_code == 400


def test_duplicate_claim_rejected(client):
    admin_token, _, policy_id, customer_id = (
        create_active_policy(client)
    )

    claim_data = {
        "claim_number": "CLM-DUP-001",
        "policy_id": policy_id,
        "customer_id": customer_id,
        "claim_type": "Accident",
        "incident_date": str(date.today()),
        "claim_amount": 100000,
        "description": "Duplicate claim test",
        "status": "Submitted",
    }

    first_response = client.post(
        "/claims",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json=claim_data,
    )

    assert first_response.status_code in (200, 201)

    second_data = claim_data.copy()
    second_data["claim_number"] = "CLM-DUP-002"

    second_response = client.post(
        "/claims",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json=second_data,
    )

    assert second_response.status_code == 409


def test_submit_claim(client):
    admin_token, _, policy_id, customer_id = (
        create_active_policy(client)
    )

    create_response = client.post(
        "/claims",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "claim_number": "CLM-SUBMIT-001",
            "policy_id": policy_id,
            "customer_id": customer_id,
            "claim_type": "Accident",
            "incident_date": str(date.today()),
            "claim_amount": 100000,
            "description": "Submit claim test",
            "status": "Submitted",
        },
    )

    assert create_response.status_code in (200, 201)

    claim_id = create_response.json()["id"]

    response = client.post(
        f"/claims/{claim_id}/submit",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Under Review"


def test_approve_claim(client):
    admin_token, _, policy_id, customer_id = (
        create_active_policy(client)
    )

    create_response = client.post(
        "/claims",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "claim_number": "CLM-APPROVE-001",
            "policy_id": policy_id,
            "customer_id": customer_id,
            "claim_type": "Accident",
            "incident_date": str(date.today()),
            "claim_amount": 100000,
            "description": "Approve claim test",
            "status": "Submitted",
        },
    )

    assert create_response.status_code in (200, 201)

    claim_id = create_response.json()["id"]

    submit_response = client.post(
        f"/claims/{claim_id}/submit",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
    )

    assert submit_response.status_code == 200

    response = client.post(
        f"/claims/{claim_id}/approve",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Approved"


def test_reject_claim(client):
    admin_token, _, policy_id, customer_id = (
        create_active_policy(client)
    )

    create_response = client.post(
        "/claims",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "claim_number": "CLM-REJECT-001",
            "policy_id": policy_id,
            "customer_id": customer_id,
            "claim_type": "Fraud",
            "incident_date": str(date.today()),
            "claim_amount": 100000,
            "description": "Reject claim test",
            "status": "Submitted",
        },
    )

    assert create_response.status_code in (200, 201)

    claim_id = create_response.json()["id"]

    submit_response = client.post(
        f"/claims/{claim_id}/submit",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
    )

    assert submit_response.status_code == 200

    response = client.post(
        f"/claims/{claim_id}/reject",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Rejected"


def test_claim_requires_active_policy(client):
    agent_token = register_and_login(
        client,
        "claim.pending.agent@example.com",
        "Agent@12345",
        "Insurance Agent",
        "Pending Policy Agent",
    )

    admin_token = register_and_login(
        client,
        "claim.pending.admin@example.com",
        "Admin@12345",
        "Super Admin",
        "Pending Claim Admin",
    )

    plan_response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
        json={
            "plan_name": "Pending Claim Plan",
            "plan_type": "Life",
            "description": "Pending policy test",
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
            "Authorization": f"Bearer {agent_token}"
        },
        json={
            "full_name": "Pending Claim Customer",
            "email": "claim.pending.customer@example.com",
            "phone": "9876543199",
            "date_of_birth": "1990-01-01",
            "address": "Hyderabad",
            "identification_number": "CLAIM-PENDING-001",
            "occupation": "Engineer",
        },
    )

    assert customer_response.status_code in (200, 201)

    customer_id = customer_response.json()["id"]

    policy_response = client.post(
        "/policies",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
        json={
            "policy_number": "CLAIM-PENDING-POL-001",
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

    policy_id = policy_response.json()["id"]

    response = client.post(
        "/claims",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "claim_number": "CLM-PENDING-001",
            "policy_id": policy_id,
            "customer_id": customer_id,
            "claim_type": "Accident",
            "incident_date": str(date.today()),
            "claim_amount": 100000,
            "description": "Pending policy claim",
            "status": "Submitted",
        },
    )

    assert response.status_code == 400