# mca-scraper

## How to use
Modify parameters like LLP_INPUT_FILE in mv_govt_parser and run using python3

## Lambda
cd ~/PycharmProjects/awsLambdaTest/v-env/lib/python3.7/site-packages/
zip -r9 ~/PycharmProjects/ajay-demo/function.zip .
cd ~/PycharmProjects/ajay-demo
zip -g function.zip *.py
https_proxy= http_proxy= aws lambda update-function-code --function-name mcParser --zip-file fileb://function.zip
