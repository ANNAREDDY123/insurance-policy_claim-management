from datetime import date

from app.models.customer import Customer


def test_customer_model():
    customer = Customer(
        full_name="Test Customer",
        email="customer.test@example.com",
        phone="9876543210",
        date_of_birth=date(1995, 5, 10),
        address="Hyderabad",
        identification_number="TEST-ID-001",
        occupation="Engineer",
    )

    assert customer.full_name == "Test Customer"
    assert customer.email == "customer.test@example.com"
    assert customer.phone == "9876543210"
    assert customer.date_of_birth == date(1995, 5, 10)
    assert customer.identification_number == "TEST-ID-001"
    assert customer.occupation == "Engineer"