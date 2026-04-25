def test_analytics_summary(client, db_session):
    login_res = client.post("/auth/login", data={"username": "testuser", "password": "password123"})
    token = login_res.json()["access_token"]
    
    res = client.get("/analytics/summary", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "total_users" in data
    assert "active_alerts" in data
    assert "avg_risk" in data

def test_analytics_dept(client, db_session):
    login_res = client.post("/auth/login", data={"username": "testuser", "password": "password123"})
    token = login_res.json()["access_token"]
    
    res = client.get("/analytics/department", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)
