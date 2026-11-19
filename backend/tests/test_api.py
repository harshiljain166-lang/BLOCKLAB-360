from fastapi.testclient import TestClient
from app.main import app

def test_health_and_nodes():
    with TestClient(app) as client:
        assert client.get('/api/health').status_code==200
        assert len(client.get('/api/nodes').json()['nodes'])>=5

def test_transaction_validation():
    with TestClient(app) as client:
        r=client.post('/api/transactions',json={'sender':'alice','receiver':'bob','amount':10})
        assert r.status_code==201
        assert client.post('/api/transactions',json={'sender':'alice','receiver':'alice','amount':2}).status_code==400
