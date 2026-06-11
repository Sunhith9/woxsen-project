import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_stats_endpoint_returns_knowledge_base_statistics():
    url = f"{BASE_URL}/stats"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        data = response.json()
        # Check that response is a dictionary
        assert isinstance(data, dict), "Response JSON is not a dictionary"
        # If keys exist, check their types but do not require keys
        if "total_documents" in data:
            assert isinstance(data["total_documents"], int), "'total_documents' should be an integer"
        if "total_vectors" in data:
            assert isinstance(data["total_vectors"], int), "'total_vectors' should be an integer"
        if "collection_names" in data:
            assert isinstance(data["collection_names"], list), "'collection_names' should be a list"
        if "last_indexed" in data:
            assert data["last_indexed"] is None or isinstance(data["last_indexed"], str), "'last_indexed' should be None or a string"
    except requests.exceptions.RequestException as e:
        assert False, f"Request to /stats endpoint failed: {e}"

test_stats_endpoint_returns_knowledge_base_statistics()
