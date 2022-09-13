from fastapi.testclient import TestClient


def test_main(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World, from FastAPI"}
