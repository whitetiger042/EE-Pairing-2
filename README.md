# GitHub Gists API

A simple HTTP API that returns a GitHub user's public Gists.

## Project Structure

```
├── app.py              # Main Flask application
├── test_app.py         # Automated tests (unit + integration)
├── Dockerfile          # Multi-stage Docker build (dev/uat/prod)
├── requirements.txt    # Python dependencies
├── .dockerignore       # Files excluded from Docker build
└── README.md           # This file
```

## Quick Start
### Using Docker

#### Development Environment
```bash
# Build
docker build --target dev -t gists-api:dev .

# Run the container (with hot reload)
docker run -d --name gists-api-dev -p 8080:8080 gists-api:dev

# Health check
curl http://localhost:8080/health
```

# 5. Cleanup
docker stop gists-api && docker rm gists-api


#### UAT Environment
```bash
# Build
docker build --target uat -t gists-api:uat .

# Run
docker run -d --name gists-api-uat -p 8080:8080 gists-api:uat

# Health check
curl http://localhost:8080/health
```

#### Production Environment
```bash
# Build
docker build --target prod -t gists-api:prod .

# Run
docker run -d --name gists-api-prod -p 8080:8080 gists-api:prod

# Health check
curl http://localhost:8080/health
```


```

### Run Locally

Requires Python 3.10+

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py

# Health check (in another terminal)
curl http://localhost:8080/health
```

To deactivate the virtual environment:
```bash
deactivate
```

To free port 8080 (if already in use):
```bash
# Find the process using port 8080
lsof -i :8080

# Kill the process (replace <PID> with the actual process ID)
kill <PID>
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/<username>` | GET | Returns list of public gists for the GitHub user |
| `/health` | GET | Health check endpoint |

## Usage

Fetch a user's public gists:

```bash
curl http://localhost:8080/octocat
```

Sample Response:
```json
{
  "user": "octocat",
  "count": 8,
  "gists": [
    {
      "id": "6cad326836d38bd3a7ae",
      "url": "https://gist.github.com/octocat/6cad326836d38bd3a7ae",
      "description": "Hello World!",
      "created_at": "2014-02-04T14:38:36Z",
      "updated_at": "2023-12-05T18:47:24Z",
      "files": ["helloworld.rb"]
    }
  ]
}
```

Health check:
```bash
curl http://localhost:8080/health
```

## Running Tests

### Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt pytest responses
```

### Run Tests

```bash
# Run all unit tests (mocked, fast, no network calls)
pytest -v

# Run specific test class
pytest test_app.py::TestGistsEndpoint -v

# Run a single test
pytest test_app.py::TestHealthEndpoint::test_health_returns_ok -v

# Run integration tests (calls real GitHub API)
pytest -v -m integration

# Run all tests except integration
pytest -v -m "not integration"
```

### Expected Output

```
test_app.py::TestFormatGist::test_format_gist_extracts_correct_fields     PASSED
test_app.py::TestHealthEndpoint::test_health_returns_ok                   PASSED
test_app.py::TestGistsEndpoint::test_get_gists_returns_user_gists         PASSED
test_app.py::TestGistsEndpoint::test_get_gists_returns_404_for_unknown_user PASSED
test_app.py::TestGistsEndpoint::test_get_gists_handles_empty_gist_list    PASSED
test_app.py::TestGistsEndpoint::test_get_gists_handles_github_api_error   PASSED
test_app.py::TestIntegration::test_octocat_gists_live                     PASSED

7 passed
```


