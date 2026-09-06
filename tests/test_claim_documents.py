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
        "document.admin@example.com",
        "Admin@12345",
        "Super Admin",
        "Document Test Admin",
    )

    register_and_login(
        client,
        "document.agent@example.com",
        "Agent@12345",
        "Insurance Agent",
        "Document Test Agent",
    )

    plan_response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "plan_name": "Document Test Plan",
            "plan_type": "Life",
            "description": "Plan for document testing",
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
            "full_name": "Document Test Customer",
            "email": "document.customer@example.com",
            "phone": "9876543001",
            "date_of_birth": "1990-01-01",
            "address": "Hyderabad",
            "identification_number": "DOC-CUST-001",
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
            "policy_number": "DOC-POL-001",
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
            "claim_number": "DOC-CLM-001",
            "policy_id": policy_id,
            "customer_id": customer_id,
            "claim_type": "Accident",
            "incident_date": str(date.today()),
            "claim_amount": 100000,
            "description": "Claim for document testing",
            "status": "Submitted",
        },
    )

    assert claim_response.status_code in (200, 201)

    claim_id = claim_response.json()["id"]

    return admin_token, claim_id


def test_upload_claim_document(client):
    token, claim_id = create_claim(client)

    response = client.post(
        f"/claims/{claim_id}/documents",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "document_type": "Police Report",
            "file_name": "police_report.pdf",
            "file_path": "uploads/police_report.pdf",
            "description": "Police report for accident claim",
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["claim_id"] == claim_id
    assert data["document_type"] == "Police Report"
    assert data["file_name"] == "police_report.pdf"
    assert data["status"] == "Uploaded"


def test_get_claim_documents(client):
    token, claim_id = create_claim(client)

    create_response = client.post(
        f"/claims/{claim_id}/documents",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "document_type": "Medical Report",
            "file_name": "medical_report.pdf",
            "file_path": "uploads/medical_report.pdf",
            "description": "Medical report",
        },
    )

    assert create_response.status_code in (200, 201)

    response = client.get(
        f"/claims/{claim_id}/documents",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_single_claim_document(client):
    token, claim_id = create_claim(client)

    create_response = client.post(
        f"/claims/{claim_id}/documents",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "document_type": "Identity Proof",
            "file_name": "identity.pdf",
            "file_path": "uploads/identity.pdf",
            "description": "Identity proof",
        },
    )

    assert create_response.status_code in (200, 201)

    document_id = create_response.json()["id"]

    response = client.get(
        f"/claims/documents/{document_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == document_id


def test_update_claim_document(client):
    token, claim_id = create_claim(client)

    create_response = client.post(
        f"/claims/{claim_id}/documents",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "document_type": "Original Report",
            "file_name": "report.pdf",
            "file_path": "uploads/report.pdf",
            "description": "Original report",
        },
    )

    assert create_response.status_code in (200, 201)

    document_id = create_response.json()["id"]

    response = client.put(
        f"/claims/documents/{document_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "document_type": "Updated Report",
            "description": "Updated report description",
            "status": "Verified",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_type"] == "Updated Report"
    assert data["description"] == "Updated report description"
    assert data["status"] == "Verified"


def test_delete_claim_document(client):
    token, claim_id = create_claim(client)

    create_response = client.post(
        f"/claims/{claim_id}/documents",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "document_type": "Delete Test",
            "file_name": "delete.pdf",
            "file_path": "uploads/delete.pdf",
            "description": "Delete test document",
        },
    )

    assert create_response.status_code in (200, 201)

    document_id = create_response.json()["id"]

    response = client.delete(
        f"/claims/documents/{document_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    get_response = client.get(
        f"/claims/documents/{document_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert get_response.status_code == 404


def test_document_requires_existing_claim(client):
    token = register_and_login(
        client,
        "document.invalid@example.com",
        "Admin@12345",
        "Super Admin",
        "Invalid Document Admin",
    )

    response = client.post(
        "/claims/999999/documents",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "document_type": "Police Report",
            "file_name": "report.pdf",
            "file_path": "uploads/report.pdf",
            "description": "Invalid claim test",
        },
    )

    assert response.status_code == 404


def test_document_requires_authentication(client):
    response = client.get(
        "/claims/1/documents"
    )

    assert response.status_code in (401, 403)