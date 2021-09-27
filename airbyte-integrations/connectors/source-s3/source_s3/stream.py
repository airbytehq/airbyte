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


from typing import Iterator

from boto3 import session as boto3session
from botocore import UNSIGNED
from botocore.config import Config
from source_s3.s3_utils import make_s3_client

from .s3file import S3File
from .source_files_abstract.stream import IncrementalFileStream


class IncrementalFileStreamS3(IncrementalFileStream):
    @property
    def storagefile_class(self) -> type:
        return S3File

    def _list_bucket(self, accept_key=lambda k: True) -> Iterator[str]:
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
        client = make_s3_client(self._provider, config=client_config, session=session)

        ctoken = None
        while True:
            # list_objects_v2 doesn't like a None value for ContinuationToken
            # so we don't set it if we don't have one.
            if ctoken:
                kwargs = dict(Bucket=provider["bucket"], Prefix=provider.get("path_prefix", ""), ContinuationToken=ctoken)
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
                        yield key
            ctoken = response.get("NextContinuationToken", None)
            if not ctoken:
                break

    def filepath_iterator(self) -> Iterator[str]:
        """
        See _list_bucket() for logic of interacting with S3

        :yield: url filepath to use in S3File()
        """
        prefix = self._provider.get("path_prefix")
        if prefix is None:
            prefix = ""

        msg = f"Iterating S3 bucket '{self._provider['bucket']}'"
        self.logger.info(msg + f" with prefix: '{prefix}' " if prefix != "" else msg)

        for blob in self._list_bucket(accept_key=lambda k: not k.endswith("/")):  # filter out 'folders', we just want actual blobs
            yield blob
