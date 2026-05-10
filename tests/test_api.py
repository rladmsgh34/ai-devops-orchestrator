import pytest
from fastapi.testclient import TestClient
from services.langchain_api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_verify_gate_pass():
    payload = {
        "project": "gwangcheon-shop",
        "event_type": "build",
        "status": "success"
    }
    response = client.post("/verify/gate", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "pass"

def test_verify_gate_fail_pnpm():
    payload = {
        "project": "gwangcheon-shop",
        "event_type": "build",
        "status": "failure",
        "log_snippet": "ERR_PNPM_FROZEN_LOCKFILE_WITH_OUTDATED_LOCKFILE"
    }
    response = client.post("/verify/gate", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "fail"
    assert "pnpm-lock.yaml" in response.json()["reason"]

def test_pr_event_synchronize():
    payload = {
        "action": "synchronize",
        "pull_request": {"number": 123}
    }
    response = client.post("/pr/event", json=payload)
    assert response.status_code == 200
    assert response.json()["action"] == "remove_label"
    assert response.json()["label"] == "verified"
