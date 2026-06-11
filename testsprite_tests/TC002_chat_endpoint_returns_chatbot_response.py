import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_chat_endpoint_returns_chatbot_response():
    url = f"{BASE_URL}/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "question": "What are the library opening hours?"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to /chat endpoint failed: {e}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    data = response.json()
    assert isinstance(data, dict), "Response JSON is not a dictionary"
    assert "answer" in data, "Response JSON does not contain expected key 'answer'"

    answer = data.get("answer")
    assert isinstance(answer, str) and answer.strip(), "Chatbot answer is empty or not a string"


test_chat_endpoint_returns_chatbot_response()
