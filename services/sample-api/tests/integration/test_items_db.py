import importlib
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
import os

pytestmark = pytest.mark.integration

POSTGRES_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/app")

@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", POSTGRES_URL)

    import sample_api.db as db
    import sample_api.models as models
    import sample_api.main as main

    importlib.reload(db)
    importlib.reload(models)
    importlib.reload(main)

    db.Base.metadata.create_all(bind=db.engine)

    return TestClient(main.app)


@pytest.fixture(autouse=True)
def clean_items(client):  # <-- depend on client so Postgres engine is active and tables exist
    import sample_api.db as db
    with db.engine.begin() as conn:
        conn.execute(text("DELETE FROM items;"))
    yield


def test_create_and_list_items(client):
    r1 = client.post("/items", json={"name": "apple"})
    assert r1.status_code == 200
    body = r1.json()
    assert body["name"] == "apple"
    assert isinstance(body["id"], int)

    r2 = client.get("/items")
    assert r2.status_code == 200
    assert r2.json() == [{"id": body["id"], "name": "apple"}]
