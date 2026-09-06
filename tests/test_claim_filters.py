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


def create_active_policy(
    client,
    suffix="001",
):
    agent_token = register_and_login(
        client,
        f"filter.agent.{suffix}@example.com",
        "Agent@12345",
        "Insurance Agent",
        f"Filter Test Agent {suffix}",
    )

    admin_token = register_and_login(
        client,
        f"filter.admin.{suffix}@example.com",
        "Admin@12345",
        "Super Admin",
        f"Filter Test Admin {suffix}",
    )

    plan_response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
        json={
            "plan_name": f"Filter Test Plan {suffix}",
            "plan_type": "Life",
            "description": "Plan for claim filter testing",
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
            "full_name": f"Filter Test Customer {suffix}",
            "email": f"filter.customer.{suffix}@example.com",
            "phone": f"987654{3100 + int(suffix):04d}",
            "date_of_birth": "1990-06-15",
            "address": "Hyderabad",
            "identification_number": f"FILTER-CUST-{suffix}",
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
            "policy_number": f"FILTER-POL-{suffix}",
            "customer_id": customer_id,
            "plan_id": plan_id,
            "agent_id": 1,
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "coverage_amount": 1000000,
            "premium_amount": 25000,
            "policy_status": "Active",
        },
    )

    assert policy_response.status_code in (200, 201)

    policy_id = policy_response.json()["id"]

    return (
        admin_token,
        policy_id,
        customer_id,
    )


def create_claim(
    client,
    token,
    policy_id,
    customer_id,
    claim_number,
    claim_type,
    incident_date,
    claim_amount,
    status="Submitted",
):
    response = client.post(
        "/claims",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "claim_number": claim_number,
            "policy_id": policy_id,
            "customer_id": customer_id,
            "claim_type": claim_type,
            "incident_date": incident_date,
            "claim_amount": claim_amount,
            "description": "Claim filter testing",
            "status": status,
        },
    )

    assert response.status_code in (200, 201)

    return response.json()


def test_claim_status_filter(client):
    token, policy_id, customer_id = (
        create_active_policy(client, "101")
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-STATUS-001",
        "Accident",
        "2026-02-10",
        100000,
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-STATUS-002",
        "Accident",
        "2026-02-11",
        150000,
    )

    response = client.get(
        "/claims?status=Submitted",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    for claim in data:
        assert claim["status"] == "Submitted"


def test_claim_type_filter(client):
    token, policy_id, customer_id = (
        create_active_policy(client, "102")
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-TYPE-001",
        "Accident",
        "2026-03-10",
        100000,
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-TYPE-002",
        "Medical",
        "2026-03-11",
        200000,
    )

    response = client.get(
        "/claims?claim_type=Medical",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["claim_type"] == "Medical"


def test_claim_date_range_filter(client):
    token, policy_id, customer_id = (
        create_active_policy(client, "103")
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-DATE-001",
        "Accident",
        "2026-04-10",
        100000,
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-DATE-002",
        "Accident",
        "2026-05-10",
        200000,
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-DATE-003",
        "Accident",
        "2026-06-10",
        300000,
    )

    response = client.get(
        "/claims"
        "?date_from=2026-05-01"
        "&date_to=2026-05-31",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["incident_date"] == "2026-05-10"


def test_claim_amount_range_filter(client):
    token, policy_id, customer_id = (
        create_active_policy(client, "104")
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-AMOUNT-001",
        "Accident",
        "2026-07-10",
        50000,
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-AMOUNT-002",
        "Accident",
        "2026-08-10",
        150000,
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-AMOUNT-003",
        "Accident",
        "2026-09-10",
        250000,
    )

    response = client.get(
        "/claims?amount_min=100000&amount_max=200000",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["claim_amount"] == 150000


def test_claim_pagination(client):
    token, policy_id, customer_id = (
        create_active_policy(client, "105")
    )

    for i in range(1, 6):
        create_claim(
            client,
            token,
            policy_id,
            customer_id,
            f"FILTER-PAGE-{i:03d}",
            "Accident",
            f"2026-01-{10 + i:02d}",
            i * 50000,
        )

    response = client.get(
        "/claims?page=1&limit=2",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_claim_second_page(client):
    token, policy_id, customer_id = (
        create_active_policy(client, "106")
    )

    for i in range(1, 6):
        create_claim(
            client,
            token,
            policy_id,
            customer_id,
            f"FILTER-PAGE2-{i:03d}",
            "Accident",
            f"2026-01-{10 + i:02d}",
            i * 50000,
        )

    response = client.get(
        "/claims?page=2&limit=2",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_claim_sort_by_amount_desc(client):
    token, policy_id, customer_id = (
        create_active_policy(client, "107")
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-SORT-001",
        "Accident",
        "2026-01-10",
        100000,
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-SORT-002",
        "Accident",
        "2026-01-11",
        300000,
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-SORT-003",
        "Accident",
        "2026-01-12",
        200000,
    )

    response = client.get(
        "/claims?sort_by=claim_amount&sort_order=desc",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    amounts = [
        claim["claim_amount"]
        for claim in data
    ]

    assert amounts == [300000, 200000, 100000]


def test_claim_sort_by_date_asc(client):
    token, policy_id, customer_id = (
        create_active_policy(client, "108")
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-DATE-SORT-001",
        "Accident",
        "2026-03-10",
        100000,
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-DATE-SORT-002",
        "Accident",
        "2026-01-10",
        200000,
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-DATE-SORT-003",
        "Accident",
        "2026-02-10",
        300000,
    )

    response = client.get(
        "/claims?sort_by=incident_date&sort_order=asc",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    dates = [
        claim["incident_date"]
        for claim in data
    ]

    assert dates == [
        "2026-01-10",
        "2026-02-10",
        "2026-03-10",
    ]


def test_invalid_claim_sort_field(client):
    token, _, _ = create_active_policy(
        client,
        "109",
    )

    response = client.get(
        "/claims?sort_by=invalid_field",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400


def test_invalid_claim_sort_order(client):
    token, _, _ = create_active_policy(
        client,
        "110",
    )

    response = client.get(
        "/claims?sort_order=wrong",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400


def test_invalid_claim_date_range(client):
    token, _, _ = create_active_policy(
        client,
        "111",
    )

    response = client.get(
        "/claims"
        "?date_from=2026-06-01"
        "&date_to=2026-05-01",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400


def test_invalid_claim_amount_range(client):
    token, _, _ = create_active_policy(
        client,
        "112",
    )

    response = client.get(
        "/claims?amount_min=500000&amount_max=100000",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400


def test_claim_status_alias(client):
    token, policy_id, customer_id = (
        create_active_policy(client, "113")
    )

    create_claim(
        client,
        token,
        policy_id,
        customer_id,
        "FILTER-ALIAS-001",
        "Accident",
        "2026-10-10",
        100000,
    )

    response = client.get(
        "/claims?claim_status=Submitted",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["status"] == "Submitted"