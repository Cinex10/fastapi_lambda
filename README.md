# (To be cleaned)
## Building Lambda layer
1.   Export requirement.txt
* add poetry export plugin.
* export requirement.txt

2. install plugins locally
* create layer folder "layers/python-deps/python"
* pip install -r requirements.txt -t layers/python-deps/python --platform manylinux2014_x86_64 --only-binary=:all: --no-deps

3. create .zip file

at this point, every thing is ready to create our serverless function, actually, we can do that in 2 diffrent ways:
* Manually (Using AWS Console)
    1. Create the layer : upload .zip, choose right paramters (arch, runtime)
    2. Create the function:
      - choose "Author from scratch", Runtime, Role and upload the zip, change handler path, if we have made edits in the provisioned IDE, make sure you have tapped "Deploy" before test, we can create event test case by choosing right event template (API Gateway, S3...etc), then tap test.
* Using IaC
    1. Write/Generate sam-min.yml file
    //


aws lambda invoke \
  --function-name FastApiFunction1 \
  --payload "$(cat events/api-gateway-event.json)" \
  response.json


"i have added trust policy to poshub-role to trust lambda


aws lambda invoke \                              ✔  poshub-api-py3.13  
  --function-name poshub-app-iac-FastApiFunctionIac-stUZnmzHspwg \
  --payload "$(cat events/api-gateway-event.json)" \
  response-iac.json"