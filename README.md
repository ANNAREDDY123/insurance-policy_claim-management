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

⚙️ Installation
1. Clone the repository
git clone https://github.com/ANNAREDDY123/insurance-policy_claim-management.git
2. Navigate to the project folder
cd insurance-policy_claim-management
3. Create a virtual environment
python -m venv venv
4. Activate the virtual environment
Windows
venv\Scripts\activate
macOS/Linux
source venv/bin/activate
5. Install dependencies
pip install -r requirements.txt
▶️ Run the Application

Start the FastAPI server:

uvicorn app.main:app --reload

The API will be available at:

http://127.0.0.1:8000
📖 API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI
http://127.0.0.1:8000/docs
ReDoc
http://127.0.0.1:8000/redoc
🧪 Running Tests

Run all tests:

pytest

The project currently includes tests for:

Authentication
Customers
Plans
Policies
Beneficiaries
Payments
Claims
Claim filters
Claim documents
Claim assessment
Claim settlement
Policy renewals
Notifications
Dashboard functionality
🔐 User Roles

The system supports the following roles:

Super Admin
Insurance Agent
Claims Officer
Finance Officer
Customer
🌐 API Modules
Module	Description
Authentication	User registration, login, token management
Customers	Customer management
Plans	Insurance plan management
Policies	Policy management
Beneficiaries	Policy beneficiary management
Payments	Payment processing and tracking
Claims	Insurance claim management
Claim Documents	Claim document management
Claim Assessment	Claim assessment workflow
Claim Settlement	Claim settlement management
Policy Renewal	Policy renewal workflow
Notifications	User notifications
Dashboard	Dashboard statistics and reports
Audit Logs	System activity tracking
👨‍💻 Author

ANNAREDDY JAGADESWAR REDDY
