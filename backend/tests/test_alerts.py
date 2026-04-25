from app.models import User, Alert, SeverityEnum

def test_alerts_list(client, db_session):
    login_res = client.post("/auth/login", data={"username": "testuser", "password": "password123"})
    token = login_res.json()["access_token"]
    
    res = client.get("/alerts", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_acknowledge_alert(client, db_session):
    login_res = client.post("/auth/login", data={"username": "testuser", "password": "password123"})
    token = login_res.json()["access_token"]
    user = db_session.query(User).filter_by(username="testuser").first()
    
    alert = Alert(user_id=user.id, severity=SeverityEnum.HIGH, alert_type="High Risk Activity", description="Test")
    db_session.add(alert)
    db_session.commit()
    
    res = client.patch(f"/alerts/{alert.id}/acknowledge", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    
    db_session.refresh(alert)
    assert alert.acknowledged == True
