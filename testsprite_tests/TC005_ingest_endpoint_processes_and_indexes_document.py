import requests
import io

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_ingest_endpoint_processes_and_indexes_document():
    ingest_url = f"{BASE_URL}/ingest"
    
    # Prepare sample TXT document content in-memory
    sample_content = "This is a test document for ingestion."
    sample_filename = "test_document.txt"
    file_data = io.BytesIO(sample_content.encode("utf-8"))
    
    files = {"file": (sample_filename, file_data, "text/plain")}
    response = requests.post(ingest_url, files=files, timeout=TIMEOUT)
    
    # Check response status code
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Validate response content type is JSON
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type, f"Expected JSON response, got {content_type}"
    
    json_resp = response.json()
    
    # Confirm response has success indicators (commonly a message or ID)
    assert isinstance(json_resp, dict), "Response JSON is not a dictionary"
    assert ("message" in json_resp and isinstance(json_resp["message"], str)) or \
           ("id" in json_resp and json_resp["id"]), "Response does not contain confirmation message or document ID"

# Call the test function
test_ingest_endpoint_processes_and_indexes_document()
