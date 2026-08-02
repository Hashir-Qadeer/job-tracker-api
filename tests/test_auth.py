def test_register_success(client):
    resp = client.post("/auth/register", json={
        "username": "usera", "email": "a@test.com", "password": "pass123"
    })
    assert resp.status_code in (200, 201)

def test_register_duplicate_email(client):
    client.post("/auth/register", json={"username": "dupuser", "email": "dup@test.com", "password": "pass123"})
    resp = client.post("/auth/register", json={"username": "dupuser2", "email": "dup@test.com", "password": "pass123"})
    assert resp.status_code == 409

def test_login_success(client):
    client.post("/auth/register", json={"username": "userb", "email": "b@test.com", "password": "pass123"})
    resp = client.post("/auth/login", data={"username": "b@test.com", "password": "pass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "userc", "email": "c@test.com", "password": "pass123"})
    resp = client.post("/auth/login", data={"username": "c@test.com", "password": "wrongpass"})
    assert resp.status_code == 401