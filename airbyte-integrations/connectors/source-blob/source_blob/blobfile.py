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
from datetime import datetime
import json
import traceback
from urllib.parse import urlparse
from boto3 import session as boto3session
import smart_open
from azure.storage.blob import BlobServiceClient
from botocore import UNSIGNED
from botocore.config import Config
from google.cloud.storage import Client as GCSClient
from google.oauth2 import service_account
from airbyte_cdk.logger import AirbyteLogger


# NOTE: this is based off the URLFile class from source-file's client.py


class ConfigurationError(Exception):
    """Client mis-configured"""


class PermissionsError(Exception):
    """User doesn't have enough permissions"""


class BlobFile(ABC):
    """ TODO docstring
    Manages accessing a file using smart_open. Child classes implement provider specific logic.
    """

    def __init__(self, url: str, provider: dict):
        self._url = url
        self._provider = provider
        self._file = None
        self.logger = AirbyteLogger()

    def __enter__(self):
        return self._file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def url(self) -> str:
        """Convert URL to remove the URL prefix (scheme)
        :return: the corresponding URL without URL prefix / scheme
        """
        parse_result = urlparse(self._url)
        if parse_result.scheme:
            return self._url.split("://")[-1]
        else:
            return self._url

    @property
    def full_url(self):
        return f"{self.storage_scheme}{self.url}"

    @property
    @abstractmethod
    def storage_scheme(self) -> str:
        """Convert Storage Names to the proper URL Prefix
        :return: the corresponding URL prefix / scheme
        """
        # storage_name = self._provider["storage"].upper()
        # parse_result = urlparse(self._url)
        # if storage_name == "HTTPS":
        #     return "https://"
        # elif storage_name == "SSH" or storage_name == "SCP":
        #     return "scp://"
        # elif storage_name == "SFTP":
        #     return "sftp://"
        # elif storage_name == "WEBHDFS":
        #     return "webhdfs://"
        # elif storage_name == "LOCAL":
        #     return "file://"
        # elif parse_result.scheme:
        #     return parse_result.scheme
        # self.logger.error(f"Unknown Storage provider in: {self.full_url}")
        # return ""

    @property
    @abstractmethod
    def last_modified(self) -> datetime:
        """ TODO Docstring """

    def close(self):
        if self._file:
            self._file.close()
            self._file = None

    def open(self, binary=False):
        self.close()
        self._file = self._open(binary=binary)
        return self

    @abstractmethod
    def _open(self, binary):
        """TODO docstring"""
        # mode = "rb" if binary else "r"
        # storage = self.storage_scheme
        # url = self.url
        # if storage == "webhdfs://":
        #     host = self._provider["host"]
        #     port = self._provider["port"]
        #     return smart_open.open(f"webhdfs://{host}:{port}/{url}", mode=mode)
        # elif storage in ("ssh://", "scp://", "sftp://"):
        #     user = self._provider["user"]
        #     host = self._provider["host"]
        #     port = self._provider.get("port", 22)
        #     # Explicitly turn off ssh keys stored in ~/.ssh
        #     transport_params = {"connect_kwargs": {"look_for_keys": False}}
        #     if "password" in self._provider:
        #         password = self._provider["password"]
        #         uri = f"{storage}{user}:{password}@{host}:{port}/{url}"
        #     else:
        #         uri = f"{storage}{user}@{host}:{port}/{url}"
        #     return smart_open.open(uri, transport_params=transport_params, mode=mode)
        # return smart_open.open(self.full_url, mode=mode)


class BlobFileS3(BlobFile):
    """TODO docstring"""

    class _Decorators():
        """ TODO docstring """
        @classmethod
        def init_boto_session(cls, func):
            """TODO Docstring (this is a decorator)"""
            def inner(self, *args, **kwargs):
                # why we're making a new Session at file level rather than stream level
                # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html#multithreading-and-multiprocessing
                if not hasattr(self, '_boto_session'):
                    if self.use_aws_account:
                        self._boto_session = boto3session.Session(
                            aws_access_key_id=self._provider.get("aws_access_key_id"),
                            aws_secret_access_key=self._provider.get("aws_secret_access_key"))
                    else:
                        self._boto_session = boto3session.Session()
                if not hasattr(self, '_boto_s3_resource'):
                    if self.use_aws_account:
                        self._boto_s3_resource = self._boto_session.resource('s3')
                    else:
                        self._boto_s3_resource = self._boto_session.resource('s3', config=Config(signature_version=UNSIGNED))
                return func(self, *args, **kwargs)
            return inner

    @property
    def storage_scheme(self) -> str:
        return "s3://"

    @property
    @_Decorators.init_boto_session
    def last_modified(self) -> datetime:
        """ TODO docstring """
        obj = self._boto_s3_resource.Object(self._provider.get('bucket'), self.url)
        return obj.last_modified

    @staticmethod
    def use_aws_account(provider: dict) -> bool:
        aws_access_key_id = provider.get("aws_access_key_id")
        aws_secret_access_key = provider.get("aws_secret_access_key")
        return aws_access_key_id and aws_secret_access_key

    def _open(self, binary):

        mode = "rb" if binary else "r"
        if self.use_aws_account(self._provider):
            aws_access_key_id = self._provider.get("aws_access_key_id", "")
            aws_secret_access_key = self._provider.get("aws_secret_access_key", "")
            result = smart_open.open(f"{self.storage_scheme}{aws_access_key_id}:{aws_secret_access_key}@{self.url}", mode=mode)
        else:
            config = Config(signature_version=UNSIGNED)
            params = {
                "resource_kwargs": {"config": config},
            }
            result = smart_open.open(self.full_url, transport_params=params, mode=mode)
        return result


class BlobFileGCS(BlobFile):
    """TODO docstring"""

    @property
    def storage_scheme(self) -> str:
        return "gs://"

    # TODO: last_modified property

    def _open(self, binary):
        mode = "rb" if binary else "r"
        service_account_json = self._provider.get("service_account_json")
        credentials = None
        if service_account_json:
            try:
                credentials = json.loads(self._provider["service_account_json"])
            except json.decoder.JSONDecodeError as err:
                error_msg = f"Failed to parse gcs service account json: {repr(err)}\n{traceback.format_exc()}"
                self.logger.error(error_msg)
                raise ConfigurationError(error_msg) from err

        if credentials:
            credentials = service_account.Credentials.from_service_account_info(credentials)
            client = GCSClient(credentials=credentials, project=credentials._project_id)
        else:
            client = GCSClient.create_anonymous_client()
        file_to_close = smart_open.open(self.full_url, transport_params=dict(client=client), mode=mode)

        return file_to_close


class BlobFileAzure(BlobFile):
    """TODO docstring"""

    @property
    def storage_scheme(self) -> str:
        return "azure://"

    # TODO: last_modified property

    def _open(self, binary):
        mode = "rb" if binary else "r"
        storage_account = self._provider.get("storage_account")
        storage_acc_url = f"https://{storage_account}.blob.core.windows.net"
        sas_token = self._provider.get("sas_token", None)
        shared_key = self._provider.get("shared_key", None)
        # if both keys are provided, shared_key is preferred as has permissions on entire storage account
        credential = shared_key or sas_token

        if credential:
            client = BlobServiceClient(account_url=storage_acc_url, credential=credential)
        else:
            # assuming anonymous public read access given no credential
            client = BlobServiceClient(account_url=storage_acc_url)

        result = smart_open.open(f"{self.storage_scheme}{self.url}", transport_params=dict(client=client), mode=mode)
        return result
