from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def db_file(tmp_path: Path) -> Path:
    return tmp_path / "test_techdesk.db"


@pytest.fixture()
def client(db_file: Path) -> TestClient:
    app = create_app(db_path=db_file)
    return TestClient(app)