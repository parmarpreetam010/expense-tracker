import pytest


@pytest.fixture
def auth_headers(client):
    # Register and login primary user
    client.post("/users", json={"email": "user1@example.com", "password": "password123"})
    res = client.post("/login", data={"username": "user1@example.com", "password": "password123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user2_headers(client):
    # Register and login a second user to test tenant isolation
    client.post("/users", json={"email": "user2@example.com", "password": "password123"})
    res = client.post("/login", data={"username": "user2@example.com", "password": "password123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_expense_unauthenticated(client):
    response = client.post("/expenses", json={"title": "Coffee", "amount": 4.5, "category": "Food"})
    assert response.status_code == 401


def test_create_and_get_expense(client, auth_headers):
    # Create expense
    payload = {"title": "Coffee", "amount": 4.5, "category": "Food"}
    create_res = client.post("/expenses", json=payload, headers=auth_headers)
    assert create_res.status_code == 201
    expense_id = create_res.json()["id"]

    # Fetch expense list
    get_res = client.get("/expenses", headers=auth_headers)
    assert get_res.status_code == 200
    res_data = get_res.json()
    assert res_data["total_records"] == 1
    assert len(res_data["data"]) == 1
    assert res_data["data"][0]["id"] == expense_id
    assert res_data["data"][0]["title"] == "Coffee"


def test_multi_tenant_isolation(client, auth_headers, user2_headers):
    # User 1 creates an expense
    payload = {"title": "Private User1 Expense", "amount": 100.0, "category": "Bills"}
    create_res = client.post("/expenses", json=payload, headers=auth_headers)
    user1_expense_id = create_res.json()["id"]

    # User 2 fetches expense list — should be empty for User 2
    user2_list = client.get("/expenses", headers=user2_headers)
    assert user2_list.status_code == 200
    res_data = user2_list.json()
    assert res_data["total_records"] == 0
    assert len(res_data["data"]) == 0

    # User 2 attempts to delete User 1's expense — should return 404
    delete_res = client.delete(f"/expenses/{user1_expense_id}", headers=user2_headers)
    assert delete_res.status_code == 404