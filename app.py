"""
Simple HTTP API that returns a GitHub user's public Gists.
"""

import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

GITHUB_API_BASE = "https://api.github.com"


def get_user_gists(username: str) -> list:
    """Fetch public gists for a given GitHub user."""
    url = f"{GITHUB_API_BASE}/users/{username}/gists"
    headers = {"Accept": "application/vnd.github+json"}
    
    # Optional: Use GitHub token if available to avoid rate limiting
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    return response.json()


def format_gist(gist: dict) -> dict:
    """Extract relevant information from a gist."""
    return {
        "id": gist.get("id"),
        "url": gist.get("html_url"),
        "description": gist.get("description"),
        "created_at": gist.get("created_at"),
        "updated_at": gist.get("updated_at"),
        "files": list(gist.get("files", {}).keys()),
    }


@app.route("/<username>")
def get_gists(username: str):
    """Return a list of public gists for the specified GitHub user."""
    try:
        gists = get_user_gists(username)
        formatted_gists = [format_gist(gist) for gist in gists]
        return jsonify({
            "user": username,
            "count": len(formatted_gists),
            "gists": formatted_gists,
        })
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return jsonify({"error": f"User '{username}' not found"}), 404
        return jsonify({"error": "GitHub API error"}), 502
    except requests.exceptions.RequestException:
        return jsonify({"error": "Failed to connect to GitHub API"}), 502


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
