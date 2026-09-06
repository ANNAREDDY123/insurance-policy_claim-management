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


def create_payment_test_policy(
    client,
    suffix,
):
    agent_token = register_and_login(
        client,
        f"filter.payment.agent.{suffix}@example.com",
        "Agent@12345",
        "Insurance Agent",
        f"Filter Payment Agent {suffix}",
    )

    finance_token = register_and_login(
        client,
        f"filter.payment.finance.{suffix}@example.com",
        "Finance@12345",
        "Finance Officer",
        f"Filter Payment Finance {suffix}",
    )

    plan_response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
        json={
            "plan_name": f"Payment Filter Plan {suffix}",
            "plan_type": "Life",
            "description": "Payment filter testing plan",
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
            "full_name": f"Payment Filter Customer {suffix}",
            "email": f"filter.payment.customer.{suffix}@example.com",
            "phone": f"987654{3000 + int(suffix):04d}",
            "date_of_birth": "1995-06-15",
            "address": "Hyderabad",
            "identification_number": f"PAY-FILTER-CUST-{suffix}",
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
            "policy_number": f"PAY-FILTER-POL-{suffix}",
            "customer_id": customer_id,
            "plan_id": plan_id,
            "agent_id": 1,
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "coverage_amount": 1000000,
            "premium_amount": 25000,
            "policy_status": "Pending",
        },
    )

    assert policy_response.status_code in (200, 201)

    policy_id = policy_response.json()["id"]

    return finance_token, policy_id


def create_payment(
    client,
    token,
    policy_id,
    payment_date,
    payment_method,
    transaction_id,
    payment_status="Pending",
):
    response = client.post(
        f"/policies/{policy_id}/premium-payment",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "amount": 25000,
            "payment_date": payment_date,
            "payment_method": payment_method,
            "transaction_id": transaction_id,
            "payment_status": payment_status,
        },
    )

    assert response.status_code in (200, 201)

    return response.json()


def test_payment_status_filter(client):
    token, policy_id = create_payment_test_policy(
        client,
        "101",
    )

    create_payment(
        client,
        token,
        policy_id,
        "2026-02-10",
        "UPI",
        "FILTER-PAY-STATUS-001",
        "Pending",
    )

    create_payment(
        client,
        token,
        policy_id,
        "2026-02-11",
        "Card",
        "FILTER-PAY-STATUS-002",
        "Success",
    )

    response = client.get(
        "/payments?payment_status=Success",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["payment_status"] == "Success"


def test_payment_method_filter(client):
    token, policy_id = create_payment_test_policy(
        client,
        "102",
    )

    create_payment(
        client,
        token,
        policy_id,
        "2026-03-10",
        "UPI",
        "FILTER-PAY-METHOD-001",
    )

    create_payment(
        client,
        token,
        policy_id,
        "2026-03-11",
        "Card",
        "FILTER-PAY-METHOD-002",
    )

    response = client.get(
        "/payments?payment_method=Card",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["payment_method"] == "Card"


def test_payment_date_range_filter(client):
    token, policy_id = create_payment_test_policy(
        client,
        "103",
    )

    create_payment(
        client,
        token,
        policy_id,
        "2026-04-10",
        "UPI",
        "FILTER-PAY-DATE-001",
    )

    create_payment(
        client,
        token,
        policy_id,
        "2026-05-10",
        "Card",
        "FILTER-PAY-DATE-002",
    )

    create_payment(
        client,
        token,
        policy_id,
        "2026-06-10",
        "Net Banking",
        "FILTER-PAY-DATE-003",
    )

    response = client.get(
        "/payments"
        "?date_from=2026-05-01"
        "&date_to=2026-05-31",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["payment_date"] == "2026-05-10"


def test_payment_pagination(client):
    token, policy_id = create_payment_test_policy(
        client,
        "104",
    )

    payment_methods = [
        "UPI",
        "Card",
        "Net Banking",
        "Auto Debit",
        "UPI",
    ]

    for index, method in enumerate(
        payment_methods,
        start=1,
    ):
        create_payment(
            client,
            token,
            policy_id,
            f"2026-01-{10 + index:02d}",
            method,
            f"FILTER-PAY-PAGE-{index:03d}",
        )

    response = client.get(
        "/payments?page=1&limit=2",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_payment_second_page(client):
    token, policy_id = create_payment_test_policy(
        client,
        "105",
    )

    payment_methods = [
        "UPI",
        "Card",
        "Net Banking",
        "Auto Debit",
        "UPI",
    ]

    for index, method in enumerate(
        payment_methods,
        start=1,
    ):
        create_payment(
            client,
            token,
            policy_id,
            f"2026-01-{10 + index:02d}",
            method,
            f"FILTER-PAY-PAGE2-{index:03d}",
        )

    response = client.get(
        "/payments?page=2&limit=2",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_payment_sort_by_amount_desc(client):
    token, policy_id = create_payment_test_policy(
        client,
        "106",
    )

    create_payment(
        client,
        token,
        policy_id,
        "2026-01-10",
        "UPI",
        "FILTER-PAY-SORT-001",
    )

    create_payment(
        client,
        token,
        policy_id,
        "2026-01-11",
        "Card",
        "FILTER-PAY-SORT-002",
    )

    create_payment(
        client,
        token,
        policy_id,
        "2026-01-12",
        "Net Banking",
        "FILTER-PAY-SORT-003",
    )

    response = client.get(
        "/payments?sort_by=amount&sort_order=desc",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    amounts = [
        payment["amount"]
        for payment in data
    ]

    assert amounts == sorted(
        amounts,
        reverse=True,
    )


def test_payment_sort_by_date_asc(client):
    token, policy_id = create_payment_test_policy(
        client,
        "107",
    )

    create_payment(
        client,
        token,
        policy_id,
        "2026-03-10",
        "UPI",
        "FILTER-PAY-DATE-SORT-001",
    )

    create_payment(
        client,
        token,
        policy_id,
        "2026-01-10",
        "Card",
        "FILTER-PAY-DATE-SORT-002",
    )

    create_payment(
        client,
        token,
        policy_id,
        "2026-02-10",
        "Net Banking",
        "FILTER-PAY-DATE-SORT-003",
    )

    response = client.get(
        "/payments?sort_by=payment_date&sort_order=asc",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    dates = [
        payment["payment_date"]
        for payment in data
    ]

    assert dates == [
        "2026-01-10",
        "2026-02-10",
        "2026-03-10",
    ]


def test_invalid_payment_sort_field(client):
    token, _ = create_payment_test_policy(
        client,
        "108",
    )

    response = client.get(
        "/payments?sort_by=invalid_field",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400


def test_invalid_payment_sort_order(client):
    token, _ = create_payment_test_policy(
        client,
        "109",
    )

    response = client.get(
        "/payments?sort_order=wrong",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400


def test_invalid_payment_date_range(client):
    token, _ = create_payment_test_policy(
        client,
        "110",
    )

    response = client.get(
        "/payments"
        "?date_from=2026-06-01"
        "&date_to=2026-05-01",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400


def test_payment_policy_filter(client):
    token, policy_id = create_payment_test_policy(
        client,
        "111",
    )

    create_payment(
        client,
        token,
        policy_id,
        "2026-08-10",
        "UPI",
        "FILTER-PAY-POLICY-001",
    )

    response = client.get(
        f"/payments?policy_id={policy_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["policy_id"] == policy_id