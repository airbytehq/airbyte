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


from abc import ABC, abstractmethod
import time
import json
import boto3
from botocore.errorfactory import ClientError
from pathlib import Path
from uuid import uuid4
from typing import Iterator, List, Mapping

import pytest
from source_files_abstract.stream import FileStream
from source_s3.stream import IncrementalFileStreamS3
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode


HERE = Path(__file__).resolve().parent
SAMPLE_DIR = HERE.joinpath("sample_files/")
LOGGER = AirbyteLogger()
RANDOM_SUFFIX = str(uuid4())


@pytest.fixture(scope="session")
def cloud_bucket_name() -> str:
    return f"airbytetest-{RANDOM_SUFFIX}"

@pytest.fixture(scope="session")
def format() -> str:
    return {"filetype": "csv"}

@pytest.fixture(scope="session")
def airbyte_system_columns() -> Mapping[str,str]:
    return {FileStream.ab_additional_col: "object", FileStream.ab_last_mod_col: "string", FileStream.ab_file_name_col: "string"}


class AbstractTestIncrementalFileStream(ABC):
    """ Prefix this class with Abstract so the tests don't run here but only in the children """

    @property
    @abstractmethod
    def stream_class(self) -> type:
        """
        :return: provider specific FileStream class (e.g. IncrementalFileStreamS3)
        :rtype: type
        """

    @property
    @abstractmethod
    def credentials(self) -> Mapping:
        """
        These will be added automatically to the provider property

        :return: mapping of provider specific credentials
        :rtype: Mapping
        """

    @abstractmethod
    def provider(self, bucket_name: str) -> Mapping:
        """
        :return: provider specific provider dict as described in spec.json (leave out credentials, they will be added automatically)
        :rtype: Mapping
        """

    @abstractmethod
    def cloud_files(self, cloud_bucket_name: str, credentials: Mapping, files_to_upload: List, private: bool=True) -> Iterator[str]:
        """
        See S3 for example what the override of this needs to achieve.

        :param cloud_bucket_name: name of bucket (or equivalent)
        :type cloud_bucket_name: str
        :param credentials: mapping of provider specific credentials
        :type credentials: Mapping
        :param files_to_upload: list of paths to local files to upload, pass empty list to test zero files case
        :type files_to_upload: List
        :param private: whether or not to make the files private and require credentials to read, defaults to True
        :type private: bool, optional
        :yield: url filepath to uploaded file
        :rtype: Iterator[str]
        """
    
    @abstractmethod
    def teardown_infra(self, cloud_bucket_name: str, credentials: Mapping):
        """
        Provider-specific logic to tidy up any cloud resources.
        See S3 for example.

        :param cloud_bucket_name: bucket (or equivalent) name
        :type cloud_bucket_name: str
        :param credentials: mapping of provider specific credentials
        :type credentials: Mapping
        """

    @pytest.mark.parametrize(  # make user_schema None to test auto-inference. Exclude any _airbyte system columns in expected_schema
        "files, path_patterns, private, num_columns, num_records, expected_schema, user_schema, fails",
        [
            ([SAMPLE_DIR.joinpath("simple_test.csv")], ["*"], False, 3, 8, {"id":"integer","name":"string","valid":"boolean"}, None, False),
            ([SAMPLE_DIR.joinpath("simple_test.csv")], ["*"], True, 3, 8, {"id":"integer","name":"string","valid":"boolean"}, None, False),
        ]
    )
    def test_stream_records(
        self, 
        cloud_bucket_name, format, airbyte_system_columns,
        files, path_patterns, private, num_columns, num_records, expected_schema, user_schema, fails
    ):
        # TODO: replace try/except/finally with pytest fixture to do teardown after each test
        try:
            uploaded_files = [fpath for fpath in self.cloud_files(cloud_bucket_name, self.credentials, files_to_upload=files, private=private)]
            LOGGER.info(f"file(s) uploaded: {uploaded_files}")

            full_expected_schema = {**expected_schema, **airbyte_system_columns}
            total_num_columns = num_columns + len(airbyte_system_columns.keys())
            provider = {**self.provider(cloud_bucket_name), **self.credentials} if private else self.provider(cloud_bucket_name)

            for sync_mode in [SyncMode("full_refresh"), SyncMode("incremental")]:
                
                if not fails:
                    fs = self.stream_class("dataset_name", provider, format, path_patterns, user_schema)
                    LOGGER.info(f"Testing stream_records() in SyncMode:{sync_mode.value}")

                    assert fs.get_json_schema() == full_expected_schema

                    records = []
                    for stream_slice in fs.stream_slices(sync_mode=sync_mode):
                        for record in fs.read_records(sync_mode, stream_slice=stream_slice):
                            records.append(record)
                    
                    assert all([len(r.keys()) == total_num_columns for r in records])
                    assert len(records) == num_records
                else:
                    with pytest.raises(Exception) as e_info:
                        fs = self.stream_class("dataset_name", provider, format, path_patterns, user_schema)
                        LOGGER.info(f"Testing EXPECTED FAILURE stream_records() in SyncMode:{sync_mode.value}")

                        fs.get_json_schema()

                        records = []
                        for stream_slice in fs.stream_slices(sync_mode=sync_mode):
                            for record in fs.read_records(sync_mode, stream_slice=stream_slice):
                                records.append(record)

        except Exception as e:
            raise e

        finally:
            self.teardown_infra(cloud_bucket_name, self.credentials)


class TestIncrementalFileStreamS3(AbstractTestIncrementalFileStream):

    @property
    def stream_class(self) -> type:
        return IncrementalFileStreamS3

    @property
    def credentials(self) -> Mapping:
        filename = HERE.parent / "secrets/aws.json"
        with open(filename) as json_file:
            return json.load(json_file)

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

    def cloud_files(self, cloud_bucket_name: str, credentials: Mapping, files_to_upload: List, private: bool=True) -> Iterator[str]:
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

        # small wait here to ensure bucket is up
        time.sleep(5)  # 5 seconds

        extra_args = {}
        if not private:
            extra_args = {'ACL': 'public-read'}
        for filepath in files_to_upload:
            self.s3_client.upload_file(str(filepath), bucket_name, str(filepath).replace(str(SAMPLE_DIR),''), ExtraArgs=extra_args)
            yield f"{bucket_name}/{str(filepath).replace(str(SAMPLE_DIR),'')}"
            
    def teardown_infra(self, cloud_bucket_name: str, credentials: Mapping):
        self._s3_connect(credentials)
        bucket = self.s3_resource.Bucket(cloud_bucket_name)
        bucket.objects.all().delete()
        bucket.delete()
        LOGGER.info(f"S3 Bucket {cloud_bucket_name} is now deleted")
