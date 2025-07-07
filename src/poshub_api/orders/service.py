from datetime import datetime, time

import json

from poshub_api.orders.exceptions import (
    OrderAlreadyExistsException,
    OrderNotFoundException,
)
from poshub_api.orders.schemas import OrderIn, OrderOut

import boto3

import structlog

logger = structlog.get_logger(__name__)

ssm = boto3.client('ssm', region_name='eu-north-1')


queue_url = ssm.get_parameter(Name='QUEUE_URL', WithDecryption=False)['Parameter']['Value']

sqs = boto3.client('sqs', region_name='eu-north-1')

logs = boto3.client('logs', region_name='eu-north-1')


orders = []

class OrderService:

    def create_order(self, order: OrderIn) -> OrderOut:
        if order.order_id in [o.order_id for o in orders]:
            raise OrderAlreadyExistsException("Order already exists")
        orders.append(order)
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = {
            "date": date,
            "source": "local lambda",
            "order": order.model_dump(by_alias=True, exclude={"created_at"})
        }
        try:
            response = sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))
            logger.info(f"Order {order.order_id} sent to queue in message #{response['MessageId']}")
            logs.put_log_events(
                logGroupName="/aws/lambda/poshub-dev",
                logStreamName="orders_queue",
                logEvents=[
                    {
                        "timestamp": int(datetime.now().timestamp() * 1000),
                        "message": f"Order {order.order_id} sent to queue in message #{response['MessageId']}"
                    }
                ]
            )
            return OrderOut(**order.model_dump(by_alias=True))
        except Exception as e:
            logger.error(f"Error sending order {order.order_id} to queue: {e}")
            raise e

    def get_order(self, order_id: str) -> OrderOut:
        for order in orders:
            if order.order_id == order_id:
                return OrderOut(**order.model_dump(by_alias=True))
        raise OrderNotFoundException(f"Order {order_id} not found")
