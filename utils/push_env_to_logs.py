import time
from dotenv import load_dotenv
import os
import boto3

load_dotenv()

def read_env_var_ssm(key:str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Environment variable {key} is not set")
    try:
        ssm = boto3.client('ssm')
        response = ssm.get_parameter(Name=value, WithDecryption=False)
        value = response['Parameter']['Value']
        print(f"✅ Successfully read environment variable {key} from SSM")
        return value
    except Exception as e:
        print(f"❌ Error reading environment variable {key} from SSM: {e}")
        raise e

def push_env_to_logs(key:str, value:str):
    try:
        client = boto3.client('logs')
        client.put_log_events(
            logGroupName="/aws/lambda/poshub-dev",
            logStreamName="poshub-dev-log-stream",
            logEvents=[
                {
                    'timestamp': int(time.time() * 1000),
                    'message': f'{key}: {value}'
                }
            ]
        )
        print(f"✅ Successfully pushed {key}: {value} to logs")
    except Exception as e:
        print(f"❌ Error pushing {key}: {value} to logs: {e}")

def main():
    try:
        value = read_env_var_ssm("API_KEY_PARAM")
        push_env_to_logs("API_KEY_PARAM", value)
    except Exception as e:
        print(f"❌ Error reading environment variable: {e}")

if __name__ == "__main__":
    main()
    
def handler(event, context):
    try:
        main()
        return {
            'statusCode': 200,
            'body': '✅ Successfully pushed environment variables to logs'
        }
    except Exception as e:
        print(f"❌ Error in handler: {e}")
        return {
            'statusCode': 500,
            'body': f'Error: {e}'
    }





