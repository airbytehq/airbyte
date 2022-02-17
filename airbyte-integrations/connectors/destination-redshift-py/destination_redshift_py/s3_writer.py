from pathlib import Path
from time import sleep
from typing import Optional

import boto3
from boto3.exceptions import S3UploadFailedError
from botocore.exceptions import EndpointConnectionError, ClientError


class S3Writer:
    def __init__(self, bucket: str, s3_path: str):
        self.bucket = bucket
        self.s3_path = s3_path

    def upload_file_to_s3(self, file_path: str) -> Optional[str]:
        file_name = Path(file_path).name
        object_name = self.__object_name(file_name=file_name)
        s3_path = f"s3://{self.bucket}/{object_name}"

        try:
            boto3.session.Session().client("s3").upload_file(file_path, self.bucket, object_name)

            # Check if the file is uploaded on S3 successfully for consistency
            while not self.check_file_exists(file_name=file_name):
                sleep(1)

            return s3_path
        except (ClientError, EndpointConnectionError, S3UploadFailedError):
            return self.upload_file_to_s3(file_path=file_path)
        except RuntimeError as error:
            raise error

    def check_file_exists(self, file_name: str) -> bool:
        """
        Checks if the data file for the given table and extension exist on the S3 bucket or not.
        :param file_name: The file name with its extension
        :return: A boolean `True` if the object exists on the S3 bucket otherwise returns `False`
        :rtype: bool
        """
        object_name = self.__object_name(file_name=file_name)

        try:
            boto3.session.Session().client("s3").head_object(Bucket=self.bucket, Key=object_name)
        except (ClientError, EndpointConnectionError):
            return False
        return True

    def __object_name(self, file_name: str) -> str:
        return f"{self.s3_path}/{file_name}"
