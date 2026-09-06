from datetime import date, datetime

from app.models.user import User
from app.models.customer import Customer
from app.models.plan import Plan
from app.models.policy import Policy
from app.models.payment import Payment
from app.models.claim import Claim
from app.models.claim_settlement import ClaimSettlement

from app.utils.security import create_access_token


def create_test_data(db):
    """
    Create common test data for dashboard and report tests.
    """

    # ---------------------------------------------------------
    # USERS
    # ---------------------------------------------------------

    admin = User(
        full_name="Dashboard Admin",
        email="dashboard_admin@example.com",
        hashed_password="test-password",
        role="Super Admin",
        is_active=True,
    )

    agent = User(
        full_name="Dashboard Agent",
        email="dashboard_agent@example.com",
        hashed_password="test-password",
        role="Insurance Agent",
        is_active=True,
    )

    db.add_all([admin, agent])
    db.commit()

    db.refresh(admin)
    db.refresh(agent)

    # ---------------------------------------------------------
    # CUSTOMER
    # ---------------------------------------------------------

    customer = Customer(
        full_name="Dashboard Customer",
        email="dashboard_customer@example.com",
        phone="9876543210",
        date_of_birth=date(1990, 1, 1),
        address="Hyderabad",
        identification_number="DASH-ID-001",
        occupation="Engineer",
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    # ---------------------------------------------------------
    # PLAN
    # ---------------------------------------------------------

    plan = Plan(
        plan_name="Dashboard Life Plan",
        plan_type="Life",
        description="Dashboard test insurance plan",
        coverage_amount=1000000,
        premium_amount=50000,
        duration_years=10,
        eligibility_age_min=18,
        eligibility_age_max=60,
        status="Active",
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    # ---------------------------------------------------------
    # POLICY 1 - ACTIVE
    # ---------------------------------------------------------

    active_policy = Policy(
        policy_number="DASH-POL-001",
        customer_id=customer.id,
        plan_id=plan.id,
        agent_id=agent.id,
        start_date=date(2026, 1, 1),
        end_date=date(2036, 1, 1),
        coverage_amount=1000000,
        premium_amount=50000,
        policy_status="Active",
    )

    # ---------------------------------------------------------
    # POLICY 2 - EXPIRED
    # ---------------------------------------------------------

    expired_policy = Policy(
        policy_number="DASH-POL-002",
        customer_id=customer.id,
        plan_id=plan.id,
        agent_id=agent.id,
        start_date=date(2015, 1, 1),
        end_date=date(2025, 1, 1),
        coverage_amount=1000000,
        premium_amount=50000,
        policy_status="Expired",
    )

    db.add_all([active_policy, expired_policy])
    db.commit()

    db.refresh(active_policy)
    db.refresh(expired_policy)

    # ---------------------------------------------------------
    # PAYMENTS
    # ---------------------------------------------------------

    successful_payment = Payment(
        policy_id=active_policy.id,
        amount=50000,
        payment_date=date(2026, 1, 10),
        payment_method="UPI",
        transaction_id="DASH-TXN-001",
        payment_status="Success",
    )

    pending_payment = Payment(
        policy_id=active_policy.id,
        amount=50000,
        payment_date=date(2026, 2, 10),
        payment_method="Card",
        transaction_id="DASH-TXN-002",
        payment_status="Pending",
    )

    db.add_all([
        successful_payment,
        pending_payment,
    ])
    db.commit()

    # ---------------------------------------------------------
    # CLAIM 1 - APPROVED
    # ---------------------------------------------------------

    approved_claim = Claim(
        claim_number="DASH-CLM-001",
        policy_id=active_policy.id,
        customer_id=customer.id,
        claim_type="Medical",
        incident_date=date(2026, 3, 1),
        claim_amount=100000,
        description="Approved dashboard test claim",
        status="Approved",
    )

    # ---------------------------------------------------------
    # CLAIM 2 - PENDING
    # ---------------------------------------------------------

    pending_claim = Claim(
        claim_number="DASH-CLM-002",
        policy_id=active_policy.id,
        customer_id=customer.id,
        claim_type="Medical",
        incident_date=date(2026, 4, 1),
        claim_amount=50000,
        description="Pending dashboard test claim",
        status="Submitted",
    )

    # ---------------------------------------------------------
    # CLAIM 3 - REJECTED
    # ---------------------------------------------------------

    rejected_claim = Claim(
        claim_number="DASH-CLM-003",
        policy_id=active_policy.id,
        customer_id=customer.id,
        claim_type="Medical",
        incident_date=date(2026, 5, 1),
        claim_amount=25000,
        description="Rejected dashboard test claim",
        status="Rejected",
    )

    db.add_all([
        approved_claim,
        pending_claim,
        rejected_claim,
    ])

    db.commit()

    db.refresh(approved_claim)
    db.refresh(pending_claim)
    db.refresh(rejected_claim)

    # ---------------------------------------------------------
    # SETTLEMENT
    # ---------------------------------------------------------

    settlement = ClaimSettlement(
        claim_id=approved_claim.id,
        settled_by=admin.id,
        settlement_amount=90000,
        settlement_status="Completed",
        payment_reference="DASH-SET-001",
        remarks="Dashboard test settlement",
        settled_at=datetime(2026, 3, 20, 10, 0, 0),
    )

    db.add(settlement)
    db.commit()
    db.refresh(settlement)

    # ---------------------------------------------------------
    # AUTH HEADER
    # ---------------------------------------------------------

    access_token = create_access_token(
        user_id=admin.id,
        role=admin.role,
    )

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    return {
        "headers": headers,
        "admin_id": admin.id,
        "agent_id": agent.id,
        "customer_id": customer.id,
        "plan_id": plan.id,
        "active_policy_id": active_policy.id,
        "expired_policy_id": expired_policy.id,
        "approved_claim_id": approved_claim.id,
        "pending_claim_id": pending_claim.id,
        "rejected_claim_id": rejected_claim.id,
        "settlement_id": settlement.id,
    }


# =============================================================
# DASHBOARD
# =============================================================

def test_dashboard(client, db_session):

    data = create_test_data(db_session)

    response = client.get(
        "/dashboard",
        headers=data["headers"],
    )

    assert response.status_code == 200

    result = response.json()

    assert result["total_customers"] == 1
    assert result["active_policies"] == 1
    assert result["expired_policies"] == 1

    assert result["total_premium_collected"] == 50000
    assert result["pending_premium"] == 50000

    assert result["total_claims"] == 3
    assert result["approved_claims"] == 1
    assert result["rejected_claims"] == 1
    assert result["pending_claims"] == 1

    assert result["total_settlement_amount"] == 90000


# =============================================================
# POLICY PREMIUM REPORT
# =============================================================

def test_policy_premium_report(client, db_session):

    data = create_test_data(db_session)

    response = client.get(
        "/reports/policy-premium",
        headers=data["headers"],
    )

    assert response.status_code == 200

    result = response.json()

    assert len(result) == 2

    active_policy = next(
        item
        for item in result
        if item["policy_number"] == "DASH-POL-001"
    )

    assert active_policy["premium_amount"] == 50000
    assert active_policy["total_paid"] == 50000


# =============================================================
# CUSTOMER POLICY HISTORY
# =============================================================

def test_customer_policy_history_report(client, db_session):

    data = create_test_data(db_session)

    response = client.get(
        "/reports/customer-policy-history",
        headers=data["headers"],
    )

    assert response.status_code == 200

    result = response.json()

    assert len(result) == 2

    policy_numbers = {
        item["policy_number"]
        for item in result
    }

    assert "DASH-POL-001" in policy_numbers
    assert "DASH-POL-002" in policy_numbers


# =============================================================
# CLAIM SETTLEMENT REPORT
# =============================================================

def test_claim_settlement_report(client, db_session):

    data = create_test_data(db_session)

    response = client.get(
        "/reports/claim-settlement",
        headers=data["headers"],
    )

    assert response.status_code == 200

    result = response.json()

    assert len(result) == 3

    approved_claim = next(
        item
        for item in result
        if item["claim_number"] == "DASH-CLM-001"
    )

    assert approved_claim["claim_status"] == "Approved"
    assert approved_claim["settlement_amount"] == 90000
    assert approved_claim["settlement_status"] == "Completed"


# =============================================================
# AGENT PERFORMANCE
# =============================================================

def test_agent_performance_report(client, db_session):

    data = create_test_data(db_session)

    response = client.get(
        "/reports/agent-performance",
        headers=data["headers"],
    )

    assert response.status_code == 200

    result = response.json()

    assert len(result) >= 1

    agent = next(
        item
        for item in result
        if item["agent_id"] == data["agent_id"]
    )

    assert agent["agent_name"] == "Dashboard Agent"
    assert agent["total_policies"] == 2
    assert agent["active_policies"] == 1
    assert agent["total_premium"] == 100000


# =============================================================
# MONTHLY PREMIUM
# =============================================================

def test_monthly_premium_report(client, db_session):

    data = create_test_data(db_session)

    response = client.get(
        "/reports/monthly-premium",
        headers=data["headers"],
    )

    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, list)
    assert len(result) >= 1

    months = {
        item["month"]
        for item in result
    }

    assert "2026-01" in months


# =============================================================
# MONTHLY CLAIMS
# =============================================================

def test_monthly_claim_report(client, db_session):

    data = create_test_data(db_session)

    response = client.get(
        "/reports/monthly-claims",
        headers=data["headers"],
    )

    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, list)
    assert len(result) >= 1

    months = {
        item["month"]
        for item in result
    }

    assert "2026-03" in months