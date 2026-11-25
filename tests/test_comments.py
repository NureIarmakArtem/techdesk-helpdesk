from fastapi.testclient import TestClient


def test_t11_comments_valid_and_validation(client: TestClient) -> None:
    t = client.post("/tickets", json={"title": "Коментарі"}).json()

    r1 = client.post(
        f"/tickets/{t['id']}/comments",
        json={"author_id": 1, "body": "  Перевірив логи DNS  "},
    )
    assert r1.status_code == 201
    assert r1.json()["body"] == "Перевірив логи DNS"

    r_list = client.get(f"/tickets/{t['id']}/comments")
    assert r_list.status_code == 200
    assert len(r_list.json()) == 1

    assert (
        client.post(
            f"/tickets/{t['id']}/comments", json={"author_id": 1, "body": "   "}
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"/tickets/{t['id']}/comments", json={"author_id": 99, "body": "Текст"}
        ).status_code
        == 422
    )


def test_t12_comments_404_and_closed_ticket(client: TestClient) -> None:
    assert (
        client.post(
            "/tickets/999/comments", json={"author_id": 1, "body": "Текст"}
        ).status_code
        == 404
    )
    assert client.get("/tickets/999/comments").status_code == 404

    t = client.post("/tickets", json={"title": "Закритий тікет"}).json()
    client.patch(f"/tickets/{t['id']}/status", json={"status": "CLOSED"})

    r_closed = client.post(
        f"/tickets/{t['id']}/comments",
        json={"author_id": 2, "body": "Фінальний коментар після закриття"},
    )
    assert r_closed.status_code == 201