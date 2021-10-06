#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import json
import time
from typing import Iterator, List, Mapping

import boto3
from airbyte_cdk.logger import AirbyteLogger
from botocore.errorfactory import ClientError
from source_s3.stream import IncrementalFileStreamS3

from .integration_test_abstract import HERE, SAMPLE_DIR, AbstractTestIncrementalFileStream

LOGGER = AirbyteLogger()


class TestIncrementalFileStreamS3(AbstractTestIncrementalFileStream):
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

    def _s3_connect(self, credentials: Mapping):
        region = "eu-west-3"
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=credentials["aws_access_key_id"],
            aws_secret_access_key=credentials["aws_secret_access_key"],
            region_name=region,
        )
        self.s3_resource = boto3.resource(
            "s3", aws_access_key_id=credentials["aws_access_key_id"], aws_secret_access_key=credentials["aws_secret_access_key"]
        )

    def cloud_files(self, cloud_bucket_name: str, credentials: Mapping, files_to_upload: List, private: bool = True) -> Iterator[str]:
        self._s3_connect(credentials)
        region = "eu-west-3"
        location = {"LocationConstraint": region}
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

    def teardown_infra(self, cloud_bucket_name: str, credentials: Mapping):
        self._s3_connect(credentials)
        bucket = self.s3_resource.Bucket(cloud_bucket_name)
        bucket.objects.all().delete()
        bucket.delete()
        LOGGER.info(f"S3 Bucket {cloud_bucket_name} is now deleted")
