# Deploy template 

sam deploy --template-file sam-min-2.yml --stack-name poshub-api --s3-bucket poshub-dev-bucket --parameter-overrides JwtSecret="a-string-secret-at-least-256-bits-long" Description="Adding mock endpoint 1" --capabilities CAPABILITY_NAMED_IAM

# Test

## GET /health
```bash
curl -X GET https://<rest_api>.execute-api.eu-north-1.amazonaws.com/dev/mock

# {"status":"ok"}
```

## POST /orders

This endpoint is protected with api key at the gateway level, and with a bearer token at the application level (FastAPI).

```bash
curl -X POST https://<rest_api>.execute-api.eu-north-1.amazonaws.com/dev/orders -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZXMiOiJvcmRlcnM6d3JpdGUifQ.LeZdAJBKMVKJTJ9YR5hBgo-nWLCe4FvWmNQWLpWu308" -H "x-api-key: rwmy8lyjhU6fx3iiPXFdy31gFwHE7QVJ2Su3DRaa"  -H "Content-Type: application/json"  -d '{ "orderId": "1", "createdAt": "1750933963", "totalAmount": 320.00, "currency": "USD" }'

# {
#     "orderId": "1",
#     "createdAt": "2025-06-26T10:32:43Z",
#     "totalAmount": 320.0,
#     "currency": "USD"
# }
```

## GET /orders/{id}

This endpoint is protected by an JWT authorizer implimented in a Lambda function.

```bash
curl -X GET https://<rest_api>.execute-api.eu-north-1.amazonaws.com/dev/orders/1 -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBSURBVzNSRUROVUNMMzJMNTdGT04iLCJzY29wZXMiOiJvcmRlcnM6cmVhZCJ9.HxFMUCdbt5eIEjfNqw5bKRCxWlP6WNWMfdZX-8Pd6KQ"

# {
#  "orderId": "1",
#  "createdAt": "2025-06-26T10:32:43Z",
#  "totalAmount": 320.0,
#  "currency": "USD"
# }
```

## OPTIONS /mock

```bash
curl -v -X OPTIONS https://<rest_api>.execute-api.eu-north-1.amazonaws.com/dev/mock

# < HTTP/2 200 
# < date: Fri, 04 Jul 2025 16:55:01 GMT
# < content-type: application/json
# < content-length: 5
# < x-amzn-requestid: 645bdb3f-be00-4f5f-a672-20f501d6ffe3
# < access-control-allow-origin: *
# < access-control-allow-headers: Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token
# < x-amz-apigw-id: NMYX7EeMgi0Etbg=
# < access-control-allow-methods: DELETE,GET,HEAD,OPTIONS,PUT,POST,PATCH
```