from pathlib import Path
from time import sleep
from typing import Optional

import boto3
from boto3.exceptions import S3UploadFailedError
from botocore.exceptions import EndpointConnectionError, ClientError


class S3ObjectsManager:
    def __init__(self, bucket: str, s3_path: str, aws_access_key_id: str = None, aws_secret_access_key: str = None):
        self.bucket = bucket
        self.s3_path = s3_path

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

        self.session = None

    def upload_file_to_s3(self, file_path: str) -> Optional[str]:
        """
        Uploads the given file path object to S3. Before the method returns it checks if the file is on S3 for
        consistency to avoid `S3ServiceException:The specified key does not exist` exception thrown when `psycopg2`
        tries to import the file from S3 which is not yet uploaded.

        :param file_path: The full path of the local file to be uploaded to S3 together with its extension

        :return: The object key written on S3 (the object key is the part after the bucket name)
        :rtype: str
        """
        file_name = Path(file_path).name
        object_name = self._object_name(file_name=file_name)
        s3_path = f"s3://{self.bucket}/{object_name}"

        try:
            self._session.client("s3").upload_file(file_path, self.bucket, object_name)

            # Check if the file is uploaded on S3 successfully for consistency
            while not self.check_file_exists(file_name=file_name):
                sleep(1)

            return s3_path
        except (ClientError, EndpointConnectionError, S3UploadFailedError):
            return self.upload_file_to_s3(file_path=file_path)
        except RuntimeError as error:
            raise error

    def delete_file_from_s3(self, file_path: str) -> bool:
        """
        Deletes an table data file (object) on S3 given the table name and the extension

        :param file_path: The full path of the local file to be uploaded to S3 together with its extension

        :return: A boolean `True` if the object is deleted successfully otherwise returns `False`
        :rtype: bool
        """
        file_name = Path(file_path).name
        key = self._object_name(file_name=file_name)

        try:
            self._session.client("s3").delete_object(Bucket=self.bucket, Key=key)
        except (ClientError, EndpointConnectionError) as error:
            return self.delete_file_from_s3(file_path=file_path)
        return True

    def check_file_exists(self, file_name: str) -> bool:
        """
        Checks if the data file for the given table and extension exist on the S3 bucket or not.

        :param file_name: The file name with its extension

        :return: A boolean `True` if the object exists on the S3 bucket otherwise returns `False`
        :rtype: bool
        """
        object_name = self._object_name(file_name=file_name)

        try:
            self._session.client("s3").head_object(Bucket=self.bucket, Key=object_name)
        except (ClientError, EndpointConnectionError):
            return False
        return True

    @property
    def _session(self):
        if not self.session:
            return boto3.session.Session(aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key)
        else:
            return self.session

    def _object_name(self, file_name: str) -> str:
        return f"{self.s3_path}/{file_name}"
