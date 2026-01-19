"""
Tests for the Gists API server.
"""

import pytest
import responses
from app import app, get_user_gists, format_gist


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_gist_data():
    """Sample gist data matching GitHub API response format."""
    return [
        {
            "id": "abc123",
            "html_url": "https://gist.github.com/octocat/abc123",
            "description": "Hello World Example",
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T12:00:00Z",
            "files": {
                "hello.py": {"filename": "hello.py"},
                "README.md": {"filename": "README.md"},
            },
        },
        {
            "id": "def456",
            "html_url": "https://gist.github.com/octocat/def456",
            "description": "Another gist",
            "created_at": "2024-01-10T08:00:00Z",
            "updated_at": "2024-01-10T08:00:00Z",
            "files": {
                "script.sh": {"filename": "script.sh"},
            },
        },
    ]


class TestFormatGist:
    """Tests for the format_gist helper function."""

    def test_format_gist_extracts_correct_fields(self, mock_gist_data):
        """Verify that format_gist extracts the expected fields."""
        result = format_gist(mock_gist_data[0])
        
        assert result["id"] == "abc123"
        assert result["url"] == "https://gist.github.com/octocat/abc123"
        assert result["description"] == "Hello World Example"
        assert result["created_at"] == "2024-01-15T10:00:00Z"
        assert result["updated_at"] == "2024-01-15T12:00:00Z"
        assert set(result["files"]) == {"hello.py", "README.md"}



class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_ok(self, client):
        """Verify the health endpoint returns status ok."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json == {"status": "ok"}


class TestGistsEndpoint:
    """Tests for the /<username> endpoint."""

    @responses.activate
    def test_get_gists_returns_user_gists(self, client, mock_gist_data):
        """Verify that valid user returns their gists."""
        responses.add(
            responses.GET,
            "https://api.github.com/users/octocat/gists",
            json=mock_gist_data,
            status=200,
        )
        
        response = client.get("/octocat")
        
        assert response.status_code == 200
        data = response.json
        assert data["user"] == "octocat"
        assert data["count"] == 2
        assert len(data["gists"]) == 2
        assert data["gists"][0]["id"] == "abc123"

    @responses.activate
    def test_get_gists_returns_404_for_unknown_user(self, client):
        """Verify that unknown user returns 404."""
        responses.add(
            responses.GET,
            "https://api.github.com/users/nonexistent-user-xyz/gists",
            json={"message": "Not Found"},
            status=404,
        )
        
        response = client.get("/nonexistent-user-xyz")
        
        assert response.status_code == 404
        assert "not found" in response.json["error"].lower()

    @responses.activate
    def test_get_gists_handles_empty_gist_list(self, client):
        """Verify that user with no gists returns empty list."""
        responses.add(
            responses.GET,
            "https://api.github.com/users/newuser/gists",
            json=[],
            status=200,
        )
        
        response = client.get("/newuser")
        
        assert response.status_code == 200
        data = response.json
        assert data["count"] == 0
        assert data["gists"] == []

    @responses.activate
    def test_get_gists_handles_github_api_error(self, client):
        """Verify that GitHub API errors return 502."""
        responses.add(
            responses.GET,
            "https://api.github.com/users/testuser/gists",
            json={"message": "Internal Server Error"},
            status=500,
        )
        
        response = client.get("/testuser")
        
        assert response.status_code == 502


class TestIntegration:
    """Integration tests that call the real GitHub API."""

    @pytest.mark.integration
    def test_octocat_gists_live(self, client):
        """
        Integration test: Verify we can fetch octocat's gists from the real API.
        
        Run with: pytest -m integration
        """
        response = client.get("/octocat")
        
        assert response.status_code == 200
        data = response.json
        assert data["user"] == "octocat"
        assert isinstance(data["count"], int)
        assert isinstance(data["gists"], list)
