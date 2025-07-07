## Building Lambda layer
### Export requirement.txt
1. Add poetry export plugin ([for more details](https://github.com/python-poetry/poetry-plugin-export)).
```bash
poetry self add poetry-plugin-export
```
2. Export packages in requirement.txt
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
# --without-hashes will add platform specific hashes to packages
```

### Create the layer
1. install plugins locally
```bash
mkdir -p layers/python-deps/python # create layer folder
```

2. Download packages
```bash
pip install -r requirements.txt -t layers/python-deps/python --platform manylinux2014_x86_64 --only-binary=:all: --no-deps
```
**Args explanation**
> *`--platform manylinux2014_x86_64`* = Downloads packages compiled for a Linux x86_64 architecture which is used by AWS Lambda
> *`--only-binary=:all:`* =  Forces pip to only use pre-compiled binary wheels (Compiled, Ready to install), never source distributions (Suitable for devlopement )
> *`--no-deps`* = Skips automatic dependency resolution and installation since Poetry already resolved all dependencies ( Prevents pip from potentially installing different versions)

3. create .zip file
```bash
cd layers/python-deps/python
zip -r ../../python-deps-layer.zip .                                 
```

## Deplying Lambda layer

At this point, every thing is ready to create our serverless function, actually, we can do that in 2 diffrent ways:

### Manually (Using AWS Console)
1. Create the layer : upload .zip, choose right paramters (arch, runtime)
2. Create the function:
    - choose "Author from scratch", Runtime, Role and upload the zip, change handler path, if we have made edits in the provisioned IDE, make sure you have tapped "Deploy" before test, we can create event test case by choosing right event template (API Gateway, S3...etc), then tap test.
### Using IaC
1. Write/Generate sam-min.yml file
> I have added trust policy to *poshub-lambda-role* to trust lambda, so the our lambda function can assume it
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: FastAPI application with Mangum handler

Globals:
  Function:
    Timeout: 30
    MemorySize: 512
    Runtime: python3.13

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]
    Description: Environment name

Resources:
  PythonDependenciesLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: !Sub "${Environment}-python-deps"
      Description: Python dependencies including FastAPI and Mangum
      ContentUri: layers/python-deps-layer.zip
      CompatibleRuntimes:
        - python3.13
      RetentionPolicy: Retain

  FastApiFunctionIac:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: main.handler
      Runtime: python3.13
      Layers:
        - !Ref PythonDependenciesLayer
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
          LOG_LEVEL: INFO
      Role: !Sub 'arn:aws:iam::${AWS::AccountId}:role/poshub-lambda-role'
      Events:
        ApiRoot:
          Type: Api
          Properties:
            Path: /
            Method: ANY
            RestApiId: !Ref FastApiGateway
        ApiProxy:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
            RestApiId: !Ref FastApiGateway
  
  PushEnvToLogsIac:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: utils.push_env_to_logs.handler
      Runtime: python3.13
      Layers:
        - !Ref PythonDependenciesLayer
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
          LOG_LEVEL: INFO
      Role: !Sub 'arn:aws:iam::${AWS::AccountId}:role/poshub-lambda-role'
      Events:
        ApiRoot:
          Type: Api
          Properties:
            Path: /push-env-to-logs
            Method: ANY
            RestApiId: !Ref FastApiGateway
  FastApiGateway:
    Type: AWS::Serverless::Api
    Properties:
      StageName: !Ref Environment
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS,PATCH'"
        AllowHeaders: "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
        AllowOrigin: "'*'"

Outputs:
  FastApiUrl:
    Description: "FastAPI URL"
    Value: !Sub "https://${FastApiGateway}.execute-api.${AWS::Region}.amazonaws.com/${Environment}/"
    Export:
      Name: !Sub "${AWS::StackName}-FastApiUrl"
  
  FunctionArn:
    Description: "FastAPI Lambda Function ARN"
    Value: !GetAtt FastApiFunctionIac.Arn
    Export:
      Name: !Sub "${AWS::StackName}-FunctionArn"
```
 You can test this template locally (using Docker), with this command
```bash
# A simulation of an API Gateway event 
echo '{
  "version": "2.0",
  "routeKey": "GET /demo/external-demo",
  "rawPath": "/demo/external-demo",
  "rawQueryString": "",
  "headers": {
    "host": "localhost",
    "x-forwarded-proto": "http"
  },
  "requestContext": {
    "http": {
      "method": "GET",
      "path": "/demo/external-demo",
      "sourceIp": "127.0.0.1"
    }
  },
  "isBase64Encoded": false
}' > event.json

sam local invoke FastApiFunctionIac --container-host 127.0.0.1 -t sam-min.yml -e event.json
```



2. Deploy the template
```bash
sam deploy --template-file sam-min.yml --stack-name poshub-app-iac --s3-bucket poshub-dev-bucket
```

3. Testing
```bash
aws lambda invoke \
  --function-name poshub-app-iac-FastApiFunctionIac-stUZnmzHspwg \
  --payload "$(base64 -i events/api-gateway-event.json)" \
  response.json

cat response.json 
# {"statusCode": 200, "body": "[{\"id\":\"prod_elec_tv_sony_bravia_xr_a90j\",\"sku\":\"XR65A90J\",\"name\":\"Sony BRAVIA XR A90J 65\\\" OLED 4K HDR Smart TV\",\"status\":\"active\"},{\"id\":\"prod_app_shirt_cotton_crew\",\"sku\":\"TSHIRT-CREW-BL-M\",\"name\":\"Men's Cotton Crew Neck T-Shirt\",\"status\":\"active\"}]", "headers": {"content-length": "252", "content-type": "application/json", "x-correlation-id": "2d9cdf7e-5080-4e38-94be-4ae87b8905fc"}, "isBase64Encoded": false}
```