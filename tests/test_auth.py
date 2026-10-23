def test_register_user_success(client):
    response = client.post(
        "/users",
        json={"email": "newuser@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data


def test_register_duplicate_email_fails(client):
    payload = {"email": "duplicate@example.com", "password": "securepassword123"}
    # First registration
    client.post("/users", json=payload)

    # Second registration with same email
    response = client.post("/users", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email is already registered"


def test_login_success(client):
    # Register first via /users
    client.post(
        "/users",
        json={"email": "loginuser@example.com", "password": "secretpassword"},
    )

    # Login via OAuth2 form data
    response = client.post(
        "/login",
        data={"username": "loginuser@example.com", "password": "secretpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post(
        "/login",
        data={"username": "nonexistent@example.com", "password": "wrongpassword"},
    )
    # Check for 401 or 403 depending on your router status code
    assert response.status_code in [401, 403]
