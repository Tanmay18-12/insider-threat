def test_login_success(client, db_session):
    response = client.post("/auth/login", data={"username": "testuser", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_creds(client):
    response = client.post("/auth/login", data={"username": "testuser", "password": "wrong"})
    assert response.status_code == 401
