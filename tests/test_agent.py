import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.agent.graph import build_graph
import app.main as main_module


@pytest.fixture(autouse=True)
def setup_graph():
    main_module._graph = build_graph()
    yield
    main_module._graph = None


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health(client):
    async with client as c:
        resp = await c.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_query_missing_question(client):
    async with client as c:
        resp = await c.post("/query", json={})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_query_empty_question(client):
    async with client as c:
        resp = await c.post("/query", json={"question": ""})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_query_success(client):
    async with client as c:
        resp = await c.post(
            "/query", json={"question": "What is the capital of France?"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data
        assert "data" in data
        assert "metadata" in data
        assert data["metadata"]["response_time_ms"] > 0
