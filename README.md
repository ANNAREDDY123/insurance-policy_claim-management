# Insurance Policy & Claim Management System

A backend REST API for managing insurance policies, customers, claims, payments, beneficiaries, claim documents, claim assessments, claim settlements, notifications, and policy renewals.

Built using FastAPI, SQLAlchemy, and SQLite.

---

## 🚀 Features

### Authentication & Authorization
- User registration and login
- JWT access token authentication
- Refresh token support
- Role-based access control
- Password hashing using bcrypt
- Change password functionality

### Customer Management
- Create customers
- View customers
- Update customer details
- Soft delete customers
- Search and filter customers

### Insurance Plan Management
- Create insurance plans
- View plans
- Update plans
- Delete plans
- Manage plan status

### Policy Management
- Create insurance policies
- View policies
- Update policies
- Cancel policies
- Policy status management

### Policy Renewals
- Renew existing policies
- Track policy renewal history
- Manage policy renewal dates

### Beneficiary Management
- Add beneficiaries to policies
- Update beneficiary details
- Delete beneficiaries
- Manage beneficiary percentage allocation

### Payment Management
- Record insurance payments
- Track payment status
- Filter payments
- Manage transaction records

### Claim Management
- Create insurance claims
- View claims
- Update claims
- Claim status management
- Filter claims

### Claim Documents
- Upload claim document information
- View claim documents
- Update documents
- Delete documents
- Document verification workflow

### Claim Assessment
- Assess insurance claims
- Record approved or rejected amounts
- Add assessment remarks
- Track claim assessment status

### Claim Settlement
- Create claim settlements
- Manage settlement status
- Track settlement amounts
- Record payment references

### Notifications
- Create notifications
- View notifications
- Mark notifications as read
- Policy-related notifications

### Audit Logs
- Track important user activities
- Store actions and entity information
- Maintain audit history

### Security
- JWT authentication
- Role-based authorization
- Password hashing
- Rate limiting for authentication endpoints

---

## 🛠️ Tech Stack

- Python 3
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite
- JWT Authentication
- Passlib / bcrypt
- Pytest
- Git & GitHub

---

## 📂 Project Structure

```text
insurance-policy-claim-management/
│
├── app/
│   ├── models/          # SQLAlchemy database models
│   ├── repositories/    # Database access layer
│   ├── routes/          # API endpoints
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── utils/           # Security and dependencies
│   ├── config.py
│   ├── database.py
│   └── main.py
│
├── tests/               # Pytest test files
│
├── requirements.txt
├── README.md
└── .env
