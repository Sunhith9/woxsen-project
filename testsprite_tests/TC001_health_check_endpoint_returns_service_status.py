import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_health_check_endpoint_returns_service_status():
    url = f"{BASE_URL}/health"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to /health endpoint failed: {e}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    try:
        json_data = response.json()
    except ValueError:
        assert False, "Response from /health endpoint is not valid JSON"

    # As per health check, expect at least a 'status' or similar key indicating service is operational
    # Since PRD doesn't specify exact response schema, verify presence of status or message key with expected value
    assert isinstance(json_data, dict), "Response JSON is not an object"
    assert any(key in json_data for key in ["status", "message", "health"]), \
        "Response JSON does not contain 'status', 'message' or 'health' key to indicate service status"
    # Optionally check if the status value indicates success
    if "status" in json_data:
        assert json_data["status"].lower() in ["ok", "healthy", "available", "up", "running"], \
            f"Unexpected status value: {json_data['status']}"
    elif "health" in json_data:
        assert json_data["health"].lower() in ["ok", "healthy", "available", "up", "running"], \
            f"Unexpected health value: {json_data['health']}"
    elif "message" in json_data:
        assert isinstance(json_data["message"], str) and len(json_data["message"]) > 0, \
            "Message key is present but empty or not a string"

test_health_check_endpoint_returns_service_status()