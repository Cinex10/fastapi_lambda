from pydantic import BaseModel


class ProductOut(BaseModel):
    id: str
    sku: str
    name: str
    status: str
