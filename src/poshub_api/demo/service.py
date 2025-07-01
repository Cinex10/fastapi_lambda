from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient

from poshub_api.demo.client import get_http, safe_get
from poshub_api.demo.exceptions import ExternalDemoException
from poshub_api.demo.schemas import ProductOut


class DemoService:
    def __init__(self, client: Annotated[AsyncClient, Depends(get_http)]):
        self.client = client

    async def external_demo(self) -> list[ProductOut]:
        response = await safe_get(self.client, "/products")
        if response.status_code == 500:
            raise ExternalDemoException("Internal server error")
        return [ProductOut(**product) for product in response.json()["data"]]
