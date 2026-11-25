from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.services import matches_priority, matches_status


def test_health_and_users(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}
    resp = client.get("/users")
    assert resp.status_code == 200
    assert resp.json() == [{"id": 1, "name": "Agent A"}, {"id": 2, "name": "Agent B"}]
    assert client.post("/users", json={"name": "Agent C"}).status_code == 405


def test_t01_create_ticket_minimal(client: TestClient) -> None:
    resp = client.post("/tickets", json={"title": "  Не працює принтер  "})
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == 1
    assert data["title"] == "Не працює принтер"
    assert data["description"] == ""
    assert data["status"] == "OPEN"
    assert data["priority"] == "medium"
    assert data["assignee_id"] is None
    assert data["created_at"].endswith("Z")


@pytest.mark.parametrize(
    "raw_title,expected_code",
    [
        ("  ab  ", 422),
        ("  abc  ", 201),
        ("x" * 120, 201),
        ("x" * 121, 422),
    ],
)
def test_t02_title_boundaries(
    client: TestClient, raw_title: str, expected_code: int
) -> None:
    resp = client.post("/tickets", json={"title": raw_title})
    assert resp.status_code == expected_code


def test_t03_list_detail_and_404(client: TestClient) -> None:
    r1 = client.post("/tickets", json={"title": "Перший тікет"}).json()
    r2 = client.post("/tickets", json={"title": "Другий тікет"}).json()

    items = client.get("/tickets").json()
    assert [i["id"] for i in items] == [r1["id"], r2["id"]]

    detail = client.get(f"/tickets/{r1['id']}")
    assert detail.status_code == 200
    assert detail.json()["title"] == "Перший тікет"

    assert client.get("/tickets/999").status_code == 404


def test_t04_t05_t06_filters_and_predicates(client: TestClient) -> None:
    assert matches_status({"status": "OPEN"}, None) is True
    assert matches_status({"status": "OPEN"}, "OPEN") is True
    assert matches_status({"status": "OPEN"}, "CLOSED") is False
    assert matches_priority({"priority": "high"}, None) is True
    assert matches_priority({"priority": "high"}, "high") is True
    assert matches_priority({"priority": "high"}, "low") is False

    t1 = client.post("/tickets", json={"title": "VPN 1", "priority": "high"}).json()
    client.post("/tickets", json={"title": "VPN 2", "priority": "low"})
    t3 = client.post("/tickets", json={"title": "VPN 3", "priority": "high"}).json()
    client.patch(f"/tickets/{t3['id']}/status", json={"status": "CLOSED"})

    # T04: status filter and empty result
    r_empty = client.get("/tickets?status=IN_PROGRESS")
    assert r_empty.status_code == 200
    assert r_empty.json() == []

    # T05: priority filter and invalid value
    r_prio = client.get("/tickets?priority=low")
    assert r_prio.status_code == 200
    assert len(r_prio.json()) == 1
    assert client.get("/tickets?priority=URGENT").status_code == 422

    # T06: combined AND filter
    r_and = client.get("/tickets?status=OPEN&priority=high")
    assert r_and.status_code == 200
    assert [t["id"] for t in r_and.json()] == [t1["id"]]


def test_t07_patch_partial_and_null_forbidden(client: TestClient) -> None:
    t = client.post(
        "/tickets",
        json={"title": "Сбій VPN", "description": "Помилка 401", "priority": "low"},
    ).json()

    r = client.patch(f"/tickets/{t['id']}", json={"priority": "high"})
    assert r.status_code == 200
    assert r.json()["priority"] == "high"
    assert r.json()["title"] == "Сбій VPN"
    assert r.json()["description"] == "Помилка 401"

    assert client.patch(f"/tickets/{t['id']}", json={"title": None}).status_code == 422
    assert client.patch(f"/tickets/{t['id']}", json={"priority": None}).status_code == 422


def test_t08_assignee_and_unassign(client: TestClient) -> None:
    t = client.post("/tickets", json={"title": "Призначення"}).json()

    r1 = client.patch(f"/tickets/{t['id']}", json={"assignee_id": 2})
    assert r1.status_code == 200
    assert r1.json()["assignee_id"] == 2

    r2 = client.patch(f"/tickets/{t['id']}", json={"assignee_id": None})
    assert r2.status_code == 200
    assert r2.json()["assignee_id"] is None

    r3 = client.patch(f"/tickets/{t['id']}", json={"assignee_id": 99})
    assert r3.status_code == 422


def test_t09_t10_status_transitions(client: TestClient) -> None:
    t = client.post("/tickets", json={"title": "Статуси"}).json()

    assert client.patch(f"/tickets/{t['id']}/status", json={"status": "IN_PROGRESS"}).status_code == 200
    assert client.patch(f"/tickets/{t['id']}/status", json={"status": "IN_PROGRESS"}).status_code == 200
    assert client.patch(f"/tickets/{t['id']}/status", json={"status": "OPEN"}).status_code == 409
    assert client.patch(f"/tickets/{t['id']}/status", json={"status": "CLOSED"}).status_code == 200
    assert client.patch(f"/tickets/{t['id']}/status", json={"status": "CLOSED"}).status_code == 200

    # T10: CLOSED -> OPEN returns 409 and preserves CLOSED
    r_reopen = client.patch(f"/tickets/{t['id']}/status", json={"status": "OPEN"})
    assert r_reopen.status_code == 409
    assert client.get(f"/tickets/{t['id']}").json()["status"] == "CLOSED"

    # Editing CLOSED ticket returns 409
    assert client.patch(f"/tickets/{t['id']}", json={"title": "Нова назва"}).status_code == 409


def test_t13_persistence_across_restart(db_file: Path) -> None:
    client1 = TestClient(create_app(db_path=db_file))
    created = client1.post("/tickets", json={"title": "Збереження БД"}).json()

    client2 = TestClient(create_app(db_path=db_file))
    fetched = client2.get(f"/tickets/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Збереження БД"


def test_t14_patch_empty_unknown_status_and_atomicity(client: TestClient) -> None:
    t = client.post("/tickets", json={"title": "Атомарність", "priority": "low"}).json()

    assert client.patch(f"/tickets/{t['id']}", json={}).status_code == 422
    assert client.patch(f"/tickets/{t['id']}", json={"unknown": 1}).status_code == 422
    assert client.patch(f"/tickets/{t['id']}", json={"status": "CLOSED"}).status_code == 422

    # Mixed valid + invalid payload must not update priority
    r_mix = client.patch(f"/tickets/{t['id']}", json={"priority": "high", "title": "a"})
    assert r_mix.status_code == 422
    assert client.get(f"/tickets/{t['id']}").json()["priority"] == "low"