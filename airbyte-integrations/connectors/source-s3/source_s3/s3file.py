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


from contextlib import contextmanager
from datetime import datetime
from typing import BinaryIO, Iterator, TextIO, Union

import boto3
import smart_open
from boto3 import session as boto3session
from botocore import UNSIGNED
from botocore.client import Config as ClientConfig
from botocore.config import Config
from botocore.exceptions import NoCredentialsError

from .source_files_abstract.storagefile import StorageFile


class S3File(StorageFile):
    def __init__(self, url: str, provider: dict):
        super().__init__(url, provider)
        self._setup_boto_session()

    def _setup_boto_session(self):
        """
        Making a new Session at file level rather than stream level as boto3 sessions are NOT thread-safe.
        Currently grabbing last_modified across multiple files asynchronously and may implement more multi-threading in future.
        See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html (anchor link broken, scroll to bottom)
        """
        if self.use_aws_account:
            self._boto_session = boto3session.Session(
                aws_access_key_id=self._provider.get("aws_access_key_id"),
                aws_secret_access_key=self._provider.get("aws_secret_access_key"),
            )
        else:
            self._boto_session = boto3session.Session()
        if self.use_aws_account:
            self._boto_s3_resource = self._boto_session.resource("s3")
        else:
            self._boto_s3_resource = self._boto_session.resource("s3", config=Config(signature_version=UNSIGNED))

    @property
    def last_modified(self) -> datetime:
        """
        Using decorator set up boto3 session & s3 resource.
        Note: slight nuance for grabbing this when we have no credentials.

        :return: last_modified property of the blob/file
        """
        bucket = self._provider.get("bucket")
        try:
            obj = self._boto_s3_resource.Object(bucket, self.url)
            return obj.last_modified
        # For some reason, this standard method above doesn't work for public files with no credentials so fall back on below
        except NoCredentialsError as nce:
            if self.use_aws_account(self._provider):  # we don't expect this error if using credentials so throw it
                raise nce
            else:
                return boto3.client("s3", config=ClientConfig(signature_version=UNSIGNED)).head_object(Bucket=bucket, Key=self.url)[
                    "LastModified"
                ]

    @staticmethod
    def use_aws_account(provider: dict) -> bool:
        aws_access_key_id = provider.get("aws_access_key_id")
        aws_secret_access_key = provider.get("aws_secret_access_key")
        return True if (aws_access_key_id is not None and aws_secret_access_key is not None) else False

    @contextmanager
    def open(self, binary: bool) -> Iterator[Union[TextIO, BinaryIO]]:
        """
        Utilising smart_open to handle this (https://github.com/RaRe-Technologies/smart_open)

        :param binary: whether or not to open file as binary
        :return: file-like object
        """
        mode = "rb" if binary else "r"
        bucket = self._provider.get("bucket")

        if self.use_aws_account(self._provider):
            aws_access_key_id = self._provider.get("aws_access_key_id", "")
            aws_secret_access_key = self._provider.get("aws_secret_access_key", "")
            result = smart_open.open(f"s3://{aws_access_key_id}:{aws_secret_access_key}@{bucket}/{self.url}", mode=mode)
        else:
            config = ClientConfig(signature_version=UNSIGNED)
            params = {"client": boto3.client("s3", config=config)}
            result = smart_open.open(f"s3://{bucket}/{self.url}", transport_params=params, mode=mode)

        # see https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager for why we do this
        try:
            yield result
        finally:
            result.close()
