import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_unified_response(client: AsyncClient) -> None:
    response = await client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["message"] == ""
    assert payload["data"]["status"] == "ok"
