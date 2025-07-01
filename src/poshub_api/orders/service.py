from poshub_api.orders.exceptions import (
    OrderAlreadyExistsException,
    OrderNotFoundException,
)
from poshub_api.orders.schemas import OrderIn, OrderOut

orders = []


class OrderService:

    def create_order(self, order: OrderIn) -> OrderOut:
        if order.order_id in [o.order_id for o in orders]:
            raise OrderAlreadyExistsException("Order already exists")
        orders.append(order)
        return OrderOut(**order.model_dump(by_alias=True))

    def get_order(self, order_id: str) -> OrderOut:
        for order in orders:
            if order.order_id == order_id:
                return OrderOut(**order.model_dump(by_alias=True))
        raise OrderNotFoundException(f"Order {order_id} not found")
