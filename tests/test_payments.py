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


def create_payment_test_policy(client):
    # Insurance Agent creates the policy
    agent_token = register_and_login(
        client,
        "payment.agent@example.com",
        "Agent@12345",
        "Insurance Agent",
        "Payment Test Agent",
    )

    # Finance Officer handles payments
    finance_token = register_and_login(
        client,
        "payment.finance@example.com",
        "Finance@12345",
        "Finance Officer",
        "Payment Test Finance Officer",
    )

    plan_response = client.post(
        "/plans",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
        json={
            "plan_name": "Payment Test Plan",
            "plan_type": "Life",
            "description": "Payment testing plan",
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
            "full_name": "Payment Test Customer",
            "email": "payment.customer@example.com",
            "phone": "9876543200",
            "date_of_birth": "1995-06-15",
            "address": "Hyderabad",
            "identification_number": "PAY-CUST-001",
            "occupation": "Engineer",
        },
    )

    assert customer_response.status_code in (200, 201)

    customer_id = customer_response.json()["id"]

    # Find the Insurance Agent's user ID
    users_response = client.get(
        "/auth/users",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
    )

    if users_response.status_code == 200:
        users = users_response.json()

        agent_id = next(
            user["id"]
            for user in users
            if user["email"] == "payment.agent@example.com"
        )
    else:
        # Existing test database uses user ID 1
        agent_id = 1

    policy_response = client.post(
        "/policies",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
        json={
            "policy_number": "PAY-POL-001",
            "customer_id": customer_id,
            "plan_id": plan_id,
            "agent_id": agent_id,
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

    return finance_token, agent_token, policy_id


def test_create_premium_payment(client):
    finance_token, _, policy_id = create_payment_test_policy(
        client
    )

    response = client.post(
        f"/policies/{policy_id}/premium-payment",
        headers={
            "Authorization": f"Bearer {finance_token}"
        },
        json={
            "amount": 25000,
            "payment_date": str(date.today()),
            "payment_method": "UPI",
            "transaction_id": "TXN-TEST-001",
            "payment_status": "Pending",
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["policy_id"] == policy_id
    assert data["amount"] == 25000
    assert data["payment_method"] == "UPI"
    assert data["transaction_id"] == "TXN-TEST-001"


def test_successful_payment_activates_policy(client):
    finance_token, agent_token, policy_id = (
        create_payment_test_policy(client)
    )

    response = client.post(
        f"/policies/{policy_id}/premium-payment",
        headers={
            "Authorization": f"Bearer {finance_token}"
        },
        json={
            "amount": 25000,
            "payment_date": str(date.today()),
            "payment_method": "Card",
            "transaction_id": "TXN-ACTIVATE-001",
            "payment_status": "Success",
        },
    )

    assert response.status_code in (200, 201)

    policy_response = client.get(
        f"/policies/{policy_id}",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
    )

    assert policy_response.status_code == 200
    assert policy_response.json()["policy_status"] == "Active"


def test_failed_payment_does_not_activate_policy(client):
    finance_token, agent_token, policy_id = (
        create_payment_test_policy(client)
    )

    response = client.post(
        f"/policies/{policy_id}/premium-payment",
        headers={
            "Authorization": f"Bearer {finance_token}"
        },
        json={
            "amount": 25000,
            "payment_date": str(date.today()),
            "payment_method": "UPI",
            "transaction_id": "TXN-FAILED-001",
            "payment_status": "Failed",
        },
    )

    assert response.status_code in (200, 201)

    policy_response = client.get(
        f"/policies/{policy_id}",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
    )

    assert policy_response.status_code == 200
    assert policy_response.json()["policy_status"] == "Pending"


def test_duplicate_transaction_rejected(client):
    finance_token, _, policy_id = create_payment_test_policy(
        client
    )

    payment_data = {
        "amount": 25000,
        "payment_date": str(date.today()),
        "payment_method": "UPI",
        "transaction_id": "TXN-DUPLICATE-001",
        "payment_status": "Pending",
    }

    first_response = client.post(
        f"/policies/{policy_id}/premium-payment",
        headers={
            "Authorization": f"Bearer {finance_token}"
        },
        json=payment_data,
    )

    assert first_response.status_code in (200, 201)

    second_response = client.post(
        f"/policies/{policy_id}/premium-payment",
        headers={
            "Authorization": f"Bearer {finance_token}"
        },
        json=payment_data,
    )

    assert second_response.status_code == 409


def test_invalid_payment_amount_rejected(client):
    finance_token, _, policy_id = create_payment_test_policy(
        client
    )

    response = client.post(
        f"/policies/{policy_id}/premium-payment",
        headers={
            "Authorization": f"Bearer {finance_token}"
        },
        json={
            "amount": 10000,
            "payment_date": str(date.today()),
            "payment_method": "UPI",
            "transaction_id": "TXN-AMOUNT-001",
            "payment_status": "Pending",
        },
    )

    assert response.status_code == 400


def test_invalid_payment_method_rejected(client):
    finance_token, _, policy_id = create_payment_test_policy(
        client
    )

    response = client.post(
        f"/policies/{policy_id}/premium-payment",
        headers={
            "Authorization": f"Bearer {finance_token}"
        },
        json={
            "amount": 25000,
            "payment_date": str(date.today()),
            "payment_method": "Cash",
            "transaction_id": "TXN-METHOD-001",
            "payment_status": "Pending",
        },
    )

    assert response.status_code == 400


def test_get_policy_payments(client):
    finance_token, _, policy_id = create_payment_test_policy(
        client
    )

    create_response = client.post(
        f"/policies/{policy_id}/premium-payment",
        headers={
            "Authorization": f"Bearer {finance_token}"
        },
        json={
            "amount": 25000,
            "payment_date": str(date.today()),
            "payment_method": "Net Banking",
            "transaction_id": "TXN-HISTORY-001",
            "payment_status": "Success",
        },
    )

    assert create_response.status_code in (200, 201)

    response = client.get(
        f"/policies/{policy_id}/payments",
        headers={
            "Authorization": f"Bearer {finance_token}"
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_all_payments(client):
    finance_token, _, policy_id = create_payment_test_policy(
        client
    )

    create_response = client.post(
        f"/policies/{policy_id}/premium-payment",
        headers={
            "Authorization": f"Bearer {finance_token}"
        },
        json={
            "amount": 25000,
            "payment_date": str(date.today()),
            "payment_method": "Auto Debit",
            "transaction_id": "TXN-ALL-001",
            "payment_status": "Success",
        },
    )

    assert create_response.status_code in (200, 201)

    response = client.get(
        "/payments",
        headers={
            "Authorization": f"Bearer {finance_token}"
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_payment(client):
    finance_token, _, policy_id = create_payment_test_policy(
        client
    )

    create_response = client.post(
        f"/policies/{policy_id}/premium-payment",
        headers={
            "Authorization": f"Bearer {finance_token}"
        },
        json={
            "amount": 25000,
            "payment_date": str(date.today()),
            "payment_method": "Card",
            "transaction_id": "TXN-SINGLE-001",
            "payment_status": "Success",
        },
    )

    assert create_response.status_code in (200, 201)

    payment_id = create_response.json()["id"]

    response = client.get(
        f"/payments/{payment_id}",
        headers={
            "Authorization": f"Bearer {finance_token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == payment_id