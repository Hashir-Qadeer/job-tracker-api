def test_create_job(client, auth_headers):
    resp = client.post("/jobs/", json={"title": "Dev", "company": "Acme"}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["title"] == "Dev"

def test_get_job_not_found(client, auth_headers):
    resp = client.get("/jobs/9999", headers=auth_headers)
    assert resp.status_code == 404

def test_list_jobs_empty(client, auth_headers):
    resp = client.get("/jobs/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0

def test_create_job_invalid_status(client, auth_headers):
    resp = client.post("/jobs/", json={"title": "Dev", "company": "Acme", "status": "not_a_status"}, headers=auth_headers)
    assert resp.status_code == 422

def test_update_job(client, auth_headers):
    created = client.post("/jobs/", json={"title": "Dev", "company": "Acme"}, headers=auth_headers).json()
    resp = client.put(f"/jobs/{created['id']}", json={"title": "Senior Dev"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Senior Dev"

def test_delete_job(client, auth_headers):
    created = client.post("/jobs/", json={"title": "Dev", "company": "Acme"}, headers=auth_headers).json()
    resp = client.delete(f"/jobs/{created['id']}", headers=auth_headers)
    assert resp.status_code == 204