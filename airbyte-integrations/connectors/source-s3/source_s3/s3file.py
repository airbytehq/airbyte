#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from contextlib import contextmanager
from typing import Any, BinaryIO, Iterator, Mapping, TextIO, Union

import smart_open
from boto3 import session as boto3session
from botocore import UNSIGNED
from botocore.client import Config as ClientConfig
from botocore.config import Config
from source_s3.s3_utils import make_s3_client, make_s3_resource

from .source_files_abstract.storagefile import StorageFile


class S3File(StorageFile):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._setup_boto_session()

    def _setup_boto_session(self) -> None:
        """
        Making a new Session at file level rather than stream level as boto3 sessions are NOT thread-safe.
        Currently grabbing last_modified across multiple files asynchronously and may implement more multi-threading in future.
        See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html (anchor link broken, scroll to bottom)
        """
        if self.use_aws_account(self._provider):
            self._boto_session = boto3session.Session(
                aws_access_key_id=self._provider.get("aws_access_key_id"),
                aws_secret_access_key=self._provider.get("aws_secret_access_key"),
            )
            self._boto_s3_resource = make_s3_resource(self._provider, session=self._boto_session)
        else:
            self._boto_session = boto3session.Session()
            self._boto_s3_resource = make_s3_resource(self._provider, config=Config(signature_version=UNSIGNED), session=self._boto_session)

    @staticmethod
    def use_aws_account(provider: Mapping[str, str]) -> bool:
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
        else:
            config = ClientConfig(signature_version=UNSIGNED)
            params = {"client": make_s3_client(self._provider, config=config)}
        self.logger.debug(f"try to open {self.file_info}")
        # There are rare cases when some keys become unreachable during sync
        # and we don't know about it, because catalog has been initially formed only once at the beginning
        # This is happen for example if a file was deleted/moved (or anything else) while we proceed with another file
        try:
            result = smart_open.open(f"s3://{bucket}/{self.url}", transport_params=params, mode=mode)
        except OSError as e:
            self.logger.warn(
                f"We don't have access to {self.url}. "
                f"Check whether key {self.url} exists in `{bucket}` bucket and/or has proper ACL permissions"
            )
            raise e
        # see https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager for why we do this
        try:
            yield result
        finally:
            result.close()
