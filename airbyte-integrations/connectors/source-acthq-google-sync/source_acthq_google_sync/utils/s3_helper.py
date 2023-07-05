import boto3
from botocore.exceptions import ClientError
import json
class S3Helper :
    def __init__(self, config) -> None:
        self.client =  boto3.resource(
            's3',
            region_name=config['region'],
            aws_access_key_id=config["accessKey"],
            aws_secret_access_key=config["secretKey"]
        )
    def upload(self, path, fileName, data):
        result = self.client.Object(path, fileName).put(Body=json.dumps(data))
        return result
