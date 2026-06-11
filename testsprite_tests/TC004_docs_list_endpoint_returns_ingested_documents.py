import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_docs_list_endpoint_returns_ingested_documents():
    url = f"{BASE_URL}/docs-list"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to /docs-list failed: {e}"

    # Validate response code is 200
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    try:
        docs_list = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # The response can be a dict or a list, handle both cases
    if isinstance(docs_list, dict):
        assert len(docs_list) > 0, "Response dict should not be empty"

        some_list_found = False
        for key, value in docs_list.items():
            if isinstance(value, list):
                some_list_found = True
                if len(value) > 0:
                    first_doc = value[0]
                    assert isinstance(first_doc, dict), "Each document should be a dict"
                    assert any(k in first_doc for k in ['id', 'name', 'filename', 'source']), "Document dict should have an identifying key"
                break
        assert some_list_found, "Response dict should contain a list of documents"

    elif isinstance(docs_list, list):
        assert len(docs_list) > 0, "Response list should not be empty"
        first_doc = docs_list[0]
        assert isinstance(first_doc, dict), "Each document should be a dict"
        assert any(k in first_doc for k in ['id', 'name', 'filename', 'source']), "Document dict should have an identifying key"

    else:
        assert False, f"Expected response to be a dict or list, got {type(docs_list)}"


test_docs_list_endpoint_returns_ingested_documents()
