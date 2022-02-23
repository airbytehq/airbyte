#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from contextlib import contextmanager
from datetime import datetime
from typing import BinaryIO, Iterator, TextIO, Union

import smart_open
from boto3 import session as boto3session
from botocore import UNSIGNED
from botocore.client import Config as ClientConfig
from botocore.config import Config
from botocore.exceptions import NoCredentialsError
from source_s3.s3_utils import make_s3_client, make_s3_resource

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
            self._boto_s3_resource = make_s3_resource(self._provider, session=self._boto_session)
        else:
            self._boto_session = boto3session.Session()
            self._boto_s3_resource = make_s3_resource(self._provider, config=Config(signature_version=UNSIGNED), session=self._boto_session)

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
            # we don't expect this error if using credentials so throw it
            if self.use_aws_account(self._provider):
                raise nce
            else:
                return make_s3_client(self._provider, config=ClientConfig(signature_version=UNSIGNED)).head_object(
                    Bucket=bucket, Key=self.url
                )["LastModified"]

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
            params = {"client": make_s3_client(self._provider, session=self._boto_session)}
            result = smart_open.open(f"s3://{bucket}/{self.url}", transport_params=params, mode=mode)
        else:
            config = ClientConfig(signature_version=UNSIGNED)
            params = {"client": make_s3_client(self._provider, config=config)}
            result = smart_open.open(f"s3://{bucket}/{self.url}", transport_params=params, mode=mode)

        # see https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager for why we do this
        try:
            yield result
        finally:
            result.close()
