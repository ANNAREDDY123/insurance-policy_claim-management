from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import Base, engine


# ============================================================
# MODELS
# ============================================================

from app.models.user import User
from app.models.plan import Plan
from app.models.customer import Customer
from app.models.policy import Policy
from app.models.policy_renewal import PolicyRenewal
from app.models.payment import Payment
from app.models.claim import Claim
from app.models.claim_document import ClaimDocument
from app.models.audit_log import AuditLog


# ============================================================
# ROUTERS
# ============================================================

from app.routes.auth import router as auth_router
from app.routes.plan import router as plan_router
from app.routes.customer import router as customer_router
from app.routes.policy import router as policy_router
from app.routes.dashboard import router as dashboard_router
from app.routes.notifications import router as notifications_router
from app.routes.policy_notifications import (
    router as policy_notifications_router,
)
from app.routes.policy_renewal import (
    router as policy_renewal_router,
)
from app.routes.payment import router as payment_router
from app.routes.claim import router as claim_router
from app.routes.claim_document import (
    router as claim_document_router,
)
from app.routes.claim_assessment import (
    router as claim_assessment_router,
)
from app.routes.claim_settlement import (
    router as claim_settlement_router,
)
from app.routes.beneficiary import (
    router as beneficiary_policy_router,
    beneficiary_router,
)
from app.routes.audit_logs import (
    router as audit_logs_router,
)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Insurance Policy & Claim Management System "
        "built with FastAPI."
    ),
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Database error occurred",
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
        },
    )


# ============================================================
# REGISTER ROUTERS
# ============================================================

app.include_router(auth_router)

app.include_router(plan_router)

app.include_router(customer_router)

app.include_router(policy_renewal_router)

app.include_router(policy_router)

app.include_router(beneficiary_policy_router)

app.include_router(beneficiary_router)

app.include_router(payment_router)

app.include_router(claim_router)

app.include_router(claim_document_router)

app.include_router(claim_assessment_router)

app.include_router(claim_settlement_router)

app.include_router(dashboard_router)

app.include_router(notifications_router)

app.include_router(policy_notifications_router)

app.include_router(audit_logs_router)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": (
            "Insurance Policy & Claim Management "
            "API is running"
        )
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": settings.app_version,
    }