from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_read_tags(client: TestClient, db: Session) -> None:
    response = client.get(f"/tags")
    assert response.status_code == 200


def test_create_tag(client: TestClient, db: Session) -> None:
    data = {
        "name": "Carbon removal",
    }

    response = client.post("/tags/", json=data)
    assert response.status_code == 201
    content = response.json()
    assert content["name"] == data["name"]
    assert "id" in content
    assert "projects" in content
