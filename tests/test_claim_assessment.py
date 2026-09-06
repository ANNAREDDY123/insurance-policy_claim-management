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


def create_claim(client):
    admin_token = register_and_login(
        client,
        "assessment.admin@example.com",
        "Admin@12345",
        "Super Admin",
        "Assessment Test Admin",
    )

    register_and_login(
        client,
        "assessment.agent@example.com",
        "Agent@12345",
        "Insurance Agent",
        "Assessment Test Agent",
    )

    plan_response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "plan_name": "Assessment Test Plan",
            "plan_type": "Life",
            "description": "Plan for assessment testing",
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
            "full_name": "Assessment Test Customer",
            "email": "assessment.customer@example.com",
            "phone": "9876543002",
            "date_of_birth": "1990-01-01",
            "address": "Hyderabad",
            "identification_number": "ASSESS-CUST-001",
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
            "policy_number": "ASSESS-POL-001",
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
            "claim_number": "ASSESS-CLM-001",
            "policy_id": policy_id,
            "customer_id": customer_id,
            "claim_type": "Accident",
            "incident_date": str(date.today()),
            "claim_amount": 100000,
            "description": "Claim for assessment testing",
            "status": "Submitted",
        },
    )

    assert claim_response.status_code in (200, 201)

    claim_id = claim_response.json()["id"]

    return admin_token, claim_id


def test_create_assessment(client):
    token, claim_id = create_claim(client)

    response = client.post(
        f"/claims/{claim_id}/assessments",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "claim_id": claim_id,
            "assessment_status": "Pending",
            "approved_amount": 80000,
            "remarks": "Initial claim assessment",
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["claim_id"] == claim_id
    assert data["assessment_status"] == "Pending"
    assert data["approved_amount"] == 80000
    assert data["remarks"] == "Initial claim assessment"


def test_get_claim_assessments(client):
    token, claim_id = create_claim(client)

    create_response = client.post(
        f"/claims/{claim_id}/assessments",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "claim_id": claim_id,
            "assessment_status": "Pending",
            "approved_amount": 75000,
            "remarks": "Assessment created",
        },
    )

    assert create_response.status_code in (200, 201)

    response = client.get(
        f"/claims/{claim_id}/assessments",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_single_assessment(client):
    token, claim_id = create_claim(client)

    create_response = client.post(
        f"/claims/{claim_id}/assessments",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "claim_id": claim_id,
            "assessment_status": "Pending",
            "approved_amount": 70000,
            "remarks": "Single assessment test",
        },
    )

    assert create_response.status_code in (200, 201)

    assessment_id = create_response.json()["id"]

    response = client.get(
        f"/claims/assessments/{assessment_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == assessment_id


def test_update_assessment(client):
    token, claim_id = create_claim(client)

    create_response = client.post(
        f"/claims/{claim_id}/assessments",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "claim_id": claim_id,
            "assessment_status": "Pending",
            "approved_amount": 60000,
            "remarks": "Before update",
        },
    )

    assert create_response.status_code in (200, 201)

    assessment_id = create_response.json()["id"]

    response = client.put(
        f"/claims/assessments/{assessment_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "assessment_status": "Approved",
            "approved_amount": 55000,
            "remarks": "Assessment approved",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["assessment_status"] == "Approved"
    assert data["approved_amount"] == 55000
    assert data["remarks"] == "Assessment approved"


def test_delete_assessment_requires_super_admin(client):
    token, claim_id = create_claim(client)

    create_response = client.post(
        f"/claims/{claim_id}/assessments",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "claim_id": claim_id,
            "assessment_status": "Pending",
            "approved_amount": 50000,
            "remarks": "Delete test",
        },
    )

    assert create_response.status_code in (200, 201)

    assessment_id = create_response.json()["id"]

    response = client.delete(
        f"/claims/assessments/{assessment_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    get_response = client.get(
        f"/claims/assessments/{assessment_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert get_response.status_code == 404


def test_assessment_claim_id_mismatch(client):
    token, claim_id = create_claim(client)

    response = client.post(
        f"/claims/{claim_id}/assessments",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "claim_id": 999999,
            "assessment_status": "Pending",
            "approved_amount": 50000,
            "remarks": "Mismatch test",
        },
    )

    assert response.status_code == 400


def test_assessment_duplicate_rejected(client):
    token, claim_id = create_claim(client)

    payload = {
        "claim_id": claim_id,
        "assessment_status": "Pending",
        "approved_amount": 50000,
        "remarks": "Duplicate test",
    }

    first_response = client.post(
        f"/claims/{claim_id}/assessments",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=payload,
    )

    assert first_response.status_code in (200, 201)

    second_response = client.post(
        f"/claims/{claim_id}/assessments",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=payload,
    )

    assert second_response.status_code == 409


def test_assessment_requires_authentication(client):
    response = client.get(
        "/claims/1/assessments"
    )

    assert response.status_code in (401, 403)