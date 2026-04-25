def test_ingest_valid_event(client, db_session):
    # Get token
    login_res = client.post("/auth/login", data={"username": "testuser", "password": "password123"})
    token = login_res.json()["access_token"]
    
    user = db_session.query(User).filter_by(username="testuser").first()
    
    res = client.post(
        "/logs/ingest", 
        json={
            "user_id": str(user.id),
            "event_type": "FILE_ACCESS",
            "resource_accessed": "engineering/docs.pdf"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "log_id" in data
    assert "risk_score" in data
    
from app.models import User
