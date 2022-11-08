#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Callable, Iterator

from boto3 import session as boto3session
from botocore import UNSIGNED
from botocore.config import Config
from source_s3.s3_utils import make_s3_client

from .s3file import S3File
from .source_files_abstract.file_info import FileInfo
from .source_files_abstract.stream import IncrementalFileStream


class IncrementalFileStreamS3(IncrementalFileStream):
    @property
    def storagefile_class(self) -> type:
        return S3File

    def _list_bucket(self, accept_key: Callable = lambda k: True) -> Iterator[FileInfo]:
        """
        Wrapper for boto3's list_objects_v2 so we can handle pagination, filter by lambda func and operate with or without credentials

        :param accept_key: lambda function to allow filtering return keys, e.g. lambda k: not k.endswith('/'), defaults to lambda k: True
        :yield: key (name) of each object
        """
        provider = self._provider

        client_config = None
        if S3File.use_aws_account(provider):
            session = boto3session.Session(
                aws_access_key_id=provider["aws_access_key_id"], aws_secret_access_key=provider["aws_secret_access_key"]
            )
        else:
            session = boto3session.Session()
            client_config = Config(signature_version=UNSIGNED)
        client = make_s3_client(provider, config=client_config, session=session)

        ctoken = None
        while True:
            # list_objects_v2 doesn't like a None value for ContinuationToken
            # so we don't set it if we don't have one.
            if ctoken:
                kwargs = dict(Bucket=provider["bucket"], Prefix=provider.get("path_prefix", ""), ContinuationToken=ctoken)  # type: ignore[unreachable]
            else:
                kwargs = dict(Bucket=provider["bucket"], Prefix=provider.get("path_prefix", ""))
            response = client.list_objects_v2(**kwargs)
            try:
                content = response["Contents"]
            except KeyError:
                pass
            else:
                for c in content:
                    key = c["Key"]
                    if accept_key(key):
                        yield FileInfo(key=key, last_modified=c["LastModified"], size=c["Size"])
            ctoken = response.get("NextContinuationToken", None)
            if not ctoken:
                break

    def filepath_iterator(self) -> Iterator[FileInfo]:
        """
        See _list_bucket() for logic of interacting with S3

        :yield: url filepath to use in S3File()
        """
        prefix = self._provider.get("path_prefix")
        if prefix is None:
            prefix = ""

        msg = f"Iterating S3 bucket '{self._provider['bucket']}'"
        self.logger.info(msg + f" with prefix: '{prefix}' " if prefix != "" else msg)

        # filter out 'folders', we just want actual blobs
        yield from self._list_bucket(accept_key=lambda k: not k.endswith("/"))
