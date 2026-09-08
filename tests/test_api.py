from fastapi.testclient import TestClient
from app import app, DATA

client = TestClient(app)

def test_seeded_data():
    assert len(DATA) >= 30

def test_fares_search():
    response = client.get('/api/v1/fares?origin=DEL&destination=BOM')
    assert response.status_code == 200
    assert response.json()[0]['currency'] == 'INR'

def test_index_and_history():
    assert client.get('/api/v1/fares/history').json()
    assert client.get('/api/v1/index/daily').json()

def test_health():
    assert client.get('/health').json()['status'] == 'ok'
