import pytest
import requests

def test_search_money():
    BASE_URL = "http://127.0.0.1:8000"
    response = requests.post(f"{BASE_URL}/money/export",
        json={
            "q": "",
            "date_range": [],
            "code": "0"
        }
    )
    assert response.status_code == 200