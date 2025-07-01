import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.anyio
async def test_external_service():
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000"
        ) as ac:
            response = await ac.get("/demo/external-demo")
    assert response.status_code == 200
