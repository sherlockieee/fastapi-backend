from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from dateutil.parser import parse


def test_read_projects(client: TestClient, db: Session) -> None:
    response = client.get(f"/projects")
    assert response.status_code == 200


def test_create_project(client: TestClient, db: Session) -> None:
    data = {
        "end_date": "2022-09-13T01:57:13.264",
        "title": "Biochar Project",
        "funding_needed": 30000,
        "currency": "USD",
        "total_raised": 15000,
        "total_backers": 380,
        "description": "We hope to remove 10,000 tonnes of CO2 by 2025 using biochar as a fertilizer in rural regions in Vietnam. This project has been piloted in Da Nang, and the result has been positive: farms with biochar application are able to produce 30% more output while also drawing down 43% more carbon into the soil.",
        "tags": [],
    }

    response = client.post("/projects/", json=data)
    assert response.status_code == 201
    content = response.json()
    assert content["title"] == data["title"]
    assert parse(content["end_date"]) == parse(data["end_date"])
    assert content["funding_needed"] == data["funding_needed"]
    assert content["currency"] == data["currency"]
    assert content["total_raised"] == data["total_raised"]
    assert content["total_backers"] == data["total_backers"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "created" in content
    assert "uuid" in content
