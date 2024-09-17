#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import timedelta
from typing import Any, Iterator, Mapping

import pendulum
from airbyte_cdk import AirbyteTracedException, FailureType
from boto3 import session as boto3session
from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError
from source_s3.s3_utils import make_s3_client

from .s3file import S3File
from .source_files_abstract.file_info import FileInfo
from .source_files_abstract.stream import IncrementalFileStream


class IncrementalFileStreamS3(IncrementalFileStream):
    @property
    def storagefile_class(self) -> type:
        return S3File

    def filepath_iterator(self, stream_state: Mapping[str, Any] = None) -> Iterator[FileInfo]:
        """
        :yield: url filepath to use in S3File()
        """
        stream_state = self._get_converted_stream_state(stream_state)
        prefix = self._provider.get("path_prefix")
        if prefix is None:
            prefix = ""

        msg = f"Iterating S3 bucket '{self._provider['bucket']}'"
        self.logger.info(msg + f" with prefix: '{prefix}' " if prefix != "" else msg)

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
                kwargs = dict(
                    Bucket=provider["bucket"], Prefix=provider.get("path_prefix", ""), ContinuationToken=ctoken
                )  # type: ignore[unreachable]
            else:
                kwargs = dict(Bucket=provider["bucket"], Prefix=provider.get("path_prefix", ""))
            try:
                response = client.list_objects_v2(**kwargs)
                content = response["Contents"]
            except ClientError as e:
                message = e.response.get("Error", {}).get("Message", {})
                raise AirbyteTracedException(message, message, failure_type=FailureType.config_error)
            except KeyError:
                pass
            else:
                for file in content:
                    if self.is_not_folder(file) and self._filter_by_last_modified_date(file, stream_state):
                        yield FileInfo(key=file["Key"], last_modified=file["LastModified"], size=file["Size"])
            ctoken = response.get("NextContinuationToken", None)
            if not ctoken:
                break

    @staticmethod
    def is_not_folder(file) -> bool:
        return not file["Key"].endswith("/")

    def _filter_by_last_modified_date(self, file: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None):
        cursor_date = pendulum.parse(stream_state.get(self.cursor_field)) if stream_state else self.start_date

        file_in_history_and_last_modified_is_earlier_than_cursor_value = (
            stream_state is not None
            and self.cursor_field in stream_state.keys()
            and file.get("LastModified") <= self._get_datetime_from_stream_state(stream_state)
            and self.file_in_history(file["Key"], stream_state.get("history", {}))
        )

        file_is_not_in_history_and_last_modified_plus_buffer_days_is_earlier_than_cursor_value = file.get("LastModified") + timedelta(
            days=self.buffer_days
        ) < self._get_datetime_from_stream_state(stream_state) and not self.file_in_history(file["Key"], stream_state.get("history", {}))

        return (
            file.get("LastModified") > cursor_date
            and not file_in_history_and_last_modified_is_earlier_than_cursor_value
            and not file_is_not_in_history_and_last_modified_plus_buffer_days_is_earlier_than_cursor_value
        )
