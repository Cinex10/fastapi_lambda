import structlog
from fastapi import Request, Response
from httpx import AsyncClient
from tenacity import retry, stop_after_attempt, wait_fixed

logger = structlog.get_logger(__name__)


def get_http(request: Request) -> AsyncClient:
    return request.app.state.http


@retry(stop=stop_after_attempt(2), wait=wait_fixed(10))
async def safe_get(client: AsyncClient, url: str) -> Response:
    attempt_info = safe_get.retry.statistics
    attempt_number = (
        attempt_info.get("attempt_number", 1) if attempt_info else 1
    )
    logger.info(
        "HTTP GET request started",
        url=url,
        attempt=attempt_number,
        timeout="10s",
    )
    response = await client.get(url)
    logger.info(
        "HTTP GET request successful",
        url=url,
        status_code=response.status_code,
        attempt=attempt_number,
        response_size=len(response.content),
    )
    return response
