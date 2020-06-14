import csv
import json
import os

import boto3
import requests
from os.path import isfile, join

from mc_govt_parser import LLPDataParser, DinDataParser

s3_client = boto3.client('s3')

in_file = "/tmp/input.csv"
out_path = "/tmp/out"

if not os.path.exists(out_path):
    os.mkdir(out_path)


event = {
    "bucket": "ajaykonale",
    "input_file": "eirSeptember_2018.csv",
    "ouput_path": "out_2018",
    "max_results": 3
}
def lambda_handler(event, context):
    print(event)

    bucket = event["bucket"]
    input_s3_file = event["input_file"]
    output_s3_path = event["output_path"]
    max_results = event["max_results"]

    print(context)
    print("Hello from lambda")
    s3_client.download_file(bucket, input_s3_file, in_file)

    LLPDataParser(in_file, os.path.join(out_path, "llp_details.csv"), max_results).parse()
    DinDataParser(in_file, os.path.join(out_path, "llp_details.csv"), max_results).parse()

    onlyfiles = [f for f in os.listdir(out_path) if isfile(join(out_path, f))]
    print("Files to upload: ", onlyfiles)
    out_s3_files = []
    for each in onlyfiles:
        full_path = join(out_path, each)
        out_filename = os.path.join(output_s3_path, each)
        out_s3_files.append(out_filename)
        s3_client.upload_file(full_path, bucket, out_filename)

    return {
        'statusCode': "done",
        'outputFiles': json.dumps(onlyfiles)
    }

def main():
    s3_client.download_file("ajaykonale", "mc_parser/myinput.json", "/tmp/input.json")
    with open("/tmp/input.json") as f:
        event = json.load(f)
        lambda_handler(event, None)

if __name__ == '__main__':
    main()
