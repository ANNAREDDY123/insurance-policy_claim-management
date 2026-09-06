from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_customers: int

    active_policies: int
    expired_policies: int

    total_premium_collected: float
    pending_premium: float

    total_claims: int
    approved_claims: int
    rejected_claims: int
    pending_claims: int

    total_settlement_amount: float


class PolicyPremiumReport(BaseModel):
    policy_id: int
    policy_number: str
    customer_id: int
    premium_amount: float
    total_paid: float


class CustomerPolicyHistory(BaseModel):
    customer_id: int
    customer_name: str
    policy_id: int
    policy_number: str
    plan_id: int
    start_date: str
    end_date: str
    policy_status: str
    premium_amount: float


class ClaimSettlementReport(BaseModel):
    claim_id: int
    claim_number: str
    customer_id: int
    claim_amount: float
    claim_status: str
    settlement_amount: float | None = None
    settlement_status: str | None = None


class AgentPerformanceReport(BaseModel):
    agent_id: int
    agent_name: str
    total_policies: int
    active_policies: int
    total_premium: float


class MonthlyPremiumReport(BaseModel):
    month: str
    total_premium_collected: float


class MonthlyClaimReport(BaseModel):
    month: str
    total_claims: int
    total_claim_amount: float