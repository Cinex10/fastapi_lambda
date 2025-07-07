from datetime import datetime
import json
import logging
from typing import Dict, Any
import boto3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logs = boto3.client('logs', region_name='eu-north-1')

batch_item_failures = []
sqs_batch_response = {}

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler that processes SQS messages
    """
    if not event:
        logger.error("No event received")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'No event received'
            })
        }
    logger.info(f"Received event with {len(event['Records'])} records")
    
    
    # Process each SQS message
    for record in event['Records']:
        try:
            # Extract message details
            message_id = record['messageId']
            message_body = record['body']
            
            # Parse message body (if it's JSON)
            try:
                parsed_body = json.loads(message_body)
                logger.info(f"Processing message {message_id}: {parsed_body}")
            except json.JSONDecodeError:
                on_error(message_id, Exception("Fail to process order"))
                continue
            
            # Process the message based on your business logic
            success = process_message(parsed_body, message_id)
            
            if success:
                logger.info(f"Successfully processed message {message_id}")
            else:
                on_error(message_id, Exception("Fail to process order"))
                continue
                
        except Exception as e:
            on_error(message_id, e)
            continue
    
    if batch_item_failures:
        sqs_batch_response["batchItemFailures"] = batch_item_failures
        return sqs_batch_response
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Successfully processed {len(event["Records"])} messages'
        })
    }

def process_message(message_data: Dict[str, Any], message_id: str) -> bool:
    """
    Process individual SQS message
    Returns True if successful, False otherwise
    """
    try:
        # Example: Extract data from the message
        source = message_data.get('source', 'unknown')
        timestamp = message_data.get('timestamp')
        order = message_data.get('order', {})
        
        if order.get('totalAmount', 0) == -1:
            raise Exception(f"Fail to process order {order['orderId']} from message #{message_id} beacause must be totalAmount != -1")
            
        
        logger.info(f"Processing message from {source} at {timestamp}")
        
        logs.put_log_events(
                logGroupName="/aws/lambda/poshub-dev",
                logStreamName="orders_queue",
                logEvents=[
                    {
                        "timestamp": int(datetime.now().timestamp() * 1000),
                        "message": f"Order Processed Successfully {order['orderId']} from message #{message_id}"
                    }
                ]
            )
            
        return True
        
    except Exception as e:
        logger.error(f"Error in process_message: {str(e)}")
        return False

def on_error(message_id: str, e: Exception):
    logs.put_log_events(
                logGroupName="/aws/lambda/poshub-dev",
                logStreamName="orders_queue",
                logEvents=[
                    {
                        "timestamp": int(datetime.now().timestamp() * 1000),
                        "message": f"Error processing message {message_id}: {str(e)}"
                    }
                ]
            )
    logger.error(f"Error processing message {message_id}: {str(e)}")
    batch_item_failures.append({
        "itemIdentifier": message_id
    })