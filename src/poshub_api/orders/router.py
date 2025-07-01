from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from .auth import validate_jwt_and_scope
from .exceptions import OrderAlreadyExistsException, OrderNotFoundException
from .schemas import OrderIn
from .service import OrderService

router = APIRouter()


@router.post("/orders", status_code=201)
def create_order(
    order: OrderIn,
    service: Annotated[OrderService, Depends(OrderService)],
    user=Depends(validate_jwt_and_scope(["orders:write"])),
):
    try:
        return service.create_order(order)
    except OrderAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/{order_id}")
def get_order(
    order_id: str, service: Annotated[OrderService, Depends(OrderService)]
):
    try:
        return service.get_order(order_id)
    except OrderNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
