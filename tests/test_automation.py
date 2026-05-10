import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from services.langchain_api.main import app

client = TestClient(app)

def test_agent_trigger_success():
    payload = {
        "command": "develop",
        "issue_title": "Fix bug",
        "issue_body": "Detailed description",
        "discord_reply_url": "http://discord.com/webhook"
    }
    
    # Mock subprocess.run and the internal context_pack call if needed
    # Since context_pack depends on ChromaDB (which is disconnected), it will return a default message
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        
        response = client.post("/agent/trigger", json=payload)
        
        assert response.status_code == 200
        assert response.json()["status"] == "triggered"
        assert "GitHub Actions" in response.json()["message"]
        
        # Verify gh command was called
        args, kwargs = mock_run.call_args
        cmd = args[0]
        assert "gh" in cmd
        assert "workflow" in cmd
        assert "run" in cmd
        assert "full-loop-agent.yml" in cmd
        assert any("issue_title=Fix bug" in arg for arg in cmd)

def test_agent_trigger_failure():
    payload = {
        "command": "develop",
        "issue_title": "Fix bug",
        "issue_body": "Detailed description"
    }
    
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = Exception("GH CLI not authenticated")
        
        response = client.post("/agent/trigger", json=payload)
        
        assert response.status_code == 200 # The API catches the exception and returns status: error
        assert response.json()["status"] == "error"
        assert "GH CLI not authenticated" in response.json()["message"]
