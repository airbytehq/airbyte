#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import logging
import os
import shutil
import time
from typing import Any, Dict, Iterator, List, Mapping

import boto3
import pytest
from airbyte_cdk import AirbyteLogger
from botocore.errorfactory import ClientError
from source_s3.source import SourceS3
from source_s3.stream import IncrementalFileStreamS3
from unit_tests.abstract_test_parser import memory_limit
from unit_tests.test_csv_parser import generate_big_file

from .integration_test_abstract import HERE, SAMPLE_DIR, AbstractTestIncrementalFileStream

TMP_FOLDER = "/tmp/test_minio_source_s3"
if not os.path.exists(TMP_FOLDER):
    os.makedirs(TMP_FOLDER)

LOGGER = AirbyteLogger()


class TestIncrementalFileStreamS3(AbstractTestIncrementalFileStream):
    region = "eu-west-3"

    @property
    def stream_class(self) -> type:
        return IncrementalFileStreamS3

    @property
    def credentials(self) -> Mapping:
        filename = HERE.parent / "secrets/config.json"
        with open(filename) as json_file:
            config = json.load(json_file)
        return {
            "aws_access_key_id": config["provider"]["aws_access_key_id"],
            "aws_secret_access_key": config["provider"]["aws_secret_access_key"],
        }

    def provider(self, bucket_name: str) -> Mapping:
        return {"storage": "S3", "bucket": bucket_name}

    def _s3_connect(self, credentials: Mapping) -> None:
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=credentials["aws_access_key_id"],
            aws_secret_access_key=credentials["aws_secret_access_key"],
            region_name=self.region,
        )
        self.s3_resource = boto3.resource(
            "s3", aws_access_key_id=credentials["aws_access_key_id"], aws_secret_access_key=credentials["aws_secret_access_key"]
        )

    def cloud_files(self, cloud_bucket_name: str, credentials: Mapping, files_to_upload: List, private: bool = True) -> Iterator[str]:
        self._s3_connect(credentials)

        location = {"LocationConstraint": self.region}
        bucket_name = cloud_bucket_name

        print("\n")
        LOGGER.info(f"Uploading {len(files_to_upload)} file(s) to {'private' if private else 'public'} aws bucket '{bucket_name}'")
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
        except ClientError:
            acl = "private" if private else "public-read"
            self.s3_client.create_bucket(ACL=acl, Bucket=bucket_name, CreateBucketConfiguration=location)

        # wait here until the bucket is ready
        ready = False
        attempts, max_attempts = 0, 30
        while not ready:
            time.sleep(1)
            try:
                self.s3_client.head_bucket(Bucket=bucket_name)
            except ClientError:
                attempts += 1
                if attempts >= max_attempts:
                    raise RuntimeError(f"Couldn't get a successful ping on bucket after ~{max_attempts} seconds")
            else:
                ready = True
                LOGGER.info(f"bucket {bucket_name} initialised")

        extra_args = {}
        if not private:
            extra_args = {"ACL": "public-read"}
        for filepath in files_to_upload:
            upload_path = str(filepath).replace(str(SAMPLE_DIR), "")
            upload_path = upload_path[1:] if upload_path[0] == "/" else upload_path
            self.s3_client.upload_file(str(filepath), bucket_name, upload_path, ExtraArgs=extra_args)
            yield f"{bucket_name}/{upload_path}"

    def teardown_infra(self, cloud_bucket_name: str, credentials: Mapping) -> None:
        self._s3_connect(credentials)
        bucket = self.s3_resource.Bucket(cloud_bucket_name)
        bucket.objects.all().delete()
        bucket.delete()
        LOGGER.info(f"S3 Bucket {cloud_bucket_name} is now deleted")


class TestIntegrationCsvFiles:
    logger = logging.getLogger("airbyte")

    @memory_limit(150)  # max used memory should be less than 150Mb
    def read_source(self, credentials: Dict[str, Any], catalog: Dict[str, Any]) -> int:
        read_count = 0
        for msg in SourceS3().read(logger=self.logger, config=credentials, catalog=catalog):
            if msg.record:
                read_count += 1
        return read_count

    @pytest.mark.order(1)
    def test_big_file(self, minio_credentials: Dict[str, Any]) -> None:
        """tests a big csv file (>= 1.0G records)"""
        # generates a big CSV files separately
        big_file_folder = os.path.join(TMP_FOLDER, "minio_data", "test-bucket", "big_files")
        shutil.rmtree(big_file_folder, ignore_errors=True)
        os.makedirs(big_file_folder)
        filepath = os.path.join(big_file_folder, "file.csv")

        # please change this value if you need to test another file size
        future_file_size = 0.5  # in gigabytes
        _, file_size = generate_big_file(filepath, future_file_size, 500)
        expected_count = sum(1 for _ in open(filepath)) - 1
        self.logger.info(f"generated file {filepath} with size {file_size}Gb, lines: {expected_count}")

        minio_credentials["path_pattern"] = "big_files/file.csv"
        minio_credentials["format"]["block_size"] = 5 * 1024**2
        source = SourceS3()
        catalog = source.read_catalog(HERE / "configured_catalogs/csv.json")
        assert self.read_source(minio_credentials, catalog) == expected_count
