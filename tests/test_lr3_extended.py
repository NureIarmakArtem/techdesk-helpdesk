import pytest
from fastapi.testclient import TestClient


# [Origin: AI as-is] AC-04-01..03: повна матриця переходів 3x3
@pytest.mark.parametrize(
    "start_status,target_status,expected_code",
    [
        ("OPEN", "OPEN", 200),
        ("OPEN", "IN_PROGRESS", 200),
        ("OPEN", "CLOSED", 200),
        ("IN_PROGRESS", "OPEN", 409),
        ("IN_PROGRESS", "IN_PROGRESS", 200),
        ("IN_PROGRESS", "CLOSED", 200),
        ("CLOSED", "OPEN", 409),
        ("CLOSED", "IN_PROGRESS", 409),
        ("CLOSED", "CLOSED", 200),
    ],
)
def test_lr3_all_nine_status_transitions(
    client: TestClient, start_status: str, target_status: str, expected_code: int
) -> None:
    ticket = client.post("/tickets", json={"title": "Матриця станів"}).json()
    if start_status != "OPEN":
        client.patch(f"/tickets/{ticket['id']}/status", json={"status": start_status})

    resp = client.patch(f"/tickets/{ticket['id']}/status", json={"status": target_status})
    assert resp.status_code == expected_code

    fetched = client.get(f"/tickets/{ticket['id']}").json()
    expected_final = target_status if expected_code == 200 else start_status
    assert fetched["status"] == expected_final


# [Origin: AI as-is] AC-03-02, AC-05-02: атомарність PATCH (priority + невідомий assignee_id)
def test_lr3_patch_atomicity_priority_and_unknown_assignee(client: TestClient) -> None:
    ticket = client.post(
        "/tickets", json={"title": "Атомарний PATCH", "priority": "medium", "assignee_id": 1}
    ).json()

    resp = client.patch(
        f"/tickets/{ticket['id']}", json={"priority": "high", "assignee_id": 999}
    )
    assert resp.status_code == 422

    after = client.get(f"/tickets/{ticket['id']}").json()
    assert after["priority"] == "medium"
    assert after["assignee_id"] == 1


# [Origin: AI as-is] AC-01-01, NFR-02: збереження назви з апострофом без спотворення
@pytest.mark.parametrize("title_text", ["Save button", "O'Brien"])
def test_lr3_title_with_apostrophe_saved_exact(
    client: TestClient, title_text: str
) -> None:
    resp = client.post("/tickets", json={"title": title_text})
    assert resp.status_code == 201
    created = resp.json()

    fetched = client.get(f"/tickets/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == title_text


# [Origin: Student] AC-01-02, AC-06-02: межі довжини description (2000/2001) і body (1000/1001)
def test_lr3_description_and_comment_length_boundaries(client: TestClient) -> None:
    r_ok = client.post("/tickets", json={"title": "Межі опису", "description": "d" * 2000})
    assert r_ok.status_code == 201
    tid = r_ok.json()["id"]

    r_too_long = client.post("/tickets", json={"title": "Межі опису", "description": "d" * 2001})
    assert r_too_long.status_code == 422

    c_ok = client.post(f"/tickets/{tid}/comments", json={"author_id": 1, "body": "c" * 1000})
    assert c_ok.status_code == 201

    c_too_long = client.post(
        f"/tickets/{tid}/comments", json={"author_id": 1, "body": "c" * 1001}
    )
    assert c_too_long.status_code == 422