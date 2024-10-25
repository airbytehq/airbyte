# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging

import boto3
from airbyte_cdk.sources.file_based.config.clients_config import S3SyncConfig
from botocore.session import Session

MIN_CHUNK_SIZE = 5000000


class S3FileTransferClient:
    _connection = Session

    def __init__(self, config: S3SyncConfig):
        self._config = config
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
        )
        self._connection = s3_client

    @property
    def connection(self) -> Session:
        return self._connection

    @classmethod
    def get_client(cls, config: S3SyncConfig):
        return cls(config)

    def write(self, file_uri: str, fp, file_size: int, logger: logging.Logger):
        s3_bucket = self._config.bucket
        s3_buket_path = self._config.path_prefix
        s3_key = f"{s3_buket_path}/{file_uri}"
        if file_size <= MIN_CHUNK_SIZE:
            logger.info(f"File size is smaller than chunk size. Performing regular upload for {file_uri}.")
            self._connection.put_object(Bucket=s3_bucket, Key=s3_key, Body=fp.read())
            logger.info(f"File {file_uri} successfully uploaded to S3 bucket {s3_bucket} with regular upload.")
        else:
            upload_id = self._connection.create_multipart_upload(Bucket=s3_bucket, Key=s3_key)["UploadId"]
            part_number = 1
            parts = []

            while True:
                data = fp.read(MIN_CHUNK_SIZE)
                if not data:
                    break

                # Upload the chunk to S3
                part = self._connection.upload_part(Bucket=s3_bucket, Key=s3_key, PartNumber=part_number, UploadId=upload_id, Body=data)
                # Keep track of parts uploaded
                parts.append({"ETag": part["ETag"], "PartNumber": part_number})
                logger.info(f"Uploading part {part_number} with ETag {part['ETag']}")
                part_number += 1

            # Complete the multipart upload
            self._connection.complete_multipart_upload(Bucket=s3_bucket, Key=s3_key, MultipartUpload={"Parts": parts}, UploadId=upload_id)
            logger.info(f"File {file_uri} successfully transferred to S3 bucket {s3_bucket}.")
        return {"file_url": s3_key, "size": file_size, "file_relative_path": s3_key}
