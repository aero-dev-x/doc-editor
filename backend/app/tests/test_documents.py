import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.session import Base, get_db
from app.main import app

TEST_DB = "sqlite+aiosqlite:///./test.db"


@pytest_asyncio.fixture(scope="function")
async def client():
    engine = create_async_engine(TEST_DB, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def _register_and_login(client: AsyncClient, email: str, username: str, password: str = "pass1234"):
    res = await client.post("/api/auth/register", json={"email": email, "username": username, "password": password})
    assert res.status_code == 201, res.text
    return res.json()["access_token"]


def _auth(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_document_lifecycle(client: AsyncClient):
    token_a = await _register_and_login(client, "alice@test.com", "alice")
    token_b = await _register_and_login(client, "bob@test.com", "bob")

    res = await client.post("/api/documents", json={"title": "Alice's Doc"}, headers=_auth(token_a))
    assert res.status_code == 201
    doc = res.json()
    doc_id = doc["id"]
    assert doc["title"] == "Alice's Doc"

    res = await client.get(f"/api/documents/{doc_id}", headers=_auth(token_a))
    assert res.status_code == 200
    assert res.json()["id"] == doc_id

    # bob has no access before the share
    res = await client.get(f"/api/documents/{doc_id}", headers=_auth(token_b))
    assert res.status_code == 403

    res = await client.post(
        f"/api/documents/{doc_id}/shares",
        json={"email": "bob@test.com", "permission": "edit"},
        headers=_auth(token_a),
    )
    assert res.status_code == 201

    res = await client.get(f"/api/documents/{doc_id}", headers=_auth(token_b))
    assert res.status_code == 200

    res = await client.get(f"/api/documents/{doc_id}/shares", headers=_auth(token_a))
    assert res.status_code == 200
    emails = [s["shared_with_email"] for s in res.json()]
    assert "bob@test.com" in emails

    res = await client.get("/api/documents/shared", headers=_auth(token_b))
    assert res.status_code == 200
    ids = [d["id"] for d in res.json()]
    assert doc_id in ids


@pytest.mark.asyncio
async def test_file_upload_txt(client: AsyncClient):
    token = await _register_and_login(client, "carol@test.com", "carol")
    content = b"Hello world\n\nSecond paragraph"
    files = {"file": ("notes.txt", content, "text/plain")}
    res = await client.post("/api/documents/upload", files=files, headers=_auth(token))
    assert res.status_code == 201
    doc = res.json()
    assert doc["title"] == "notes"
    assert "Hello world" in doc["content"]
