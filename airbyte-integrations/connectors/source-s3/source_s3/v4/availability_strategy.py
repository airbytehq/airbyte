#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import logging
import traceback
from typing import Optional, Tuple

from botocore.exceptions import ClientError, ConnectTimeoutError, EndpointConnectionError

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.file_based.availability_strategy import (
    DefaultFileBasedAvailabilityStrategy,
)
from airbyte_cdk.sources.file_based.exceptions import (
    CheckAvailabilityError,
    FileBasedSourceError,
)
from airbyte_cdk.sources.file_based.file_types.parquet_parser import ParquetParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.abstract_file_based_stream import AbstractFileBasedStream
from source_s3.v4.config import S3FileBasedStreamConfig


class SourceS3AvailabilityStrategy(DefaultFileBasedAvailabilityStrategy):
    """
    Custom availability strategy that optionally skips the full parse check for Parquet
    streams to avoid OOM errors on large files.  The skip is gated behind the per-stream
    ``skip_full_check_for_parquet`` flag (default False).  Non-Parquet streams and streams
    without the flag always use the default check path.
    """

    @staticmethod
    def _raise_aws_error(exc: Exception) -> None:
        messages = {
            "InvalidAccessKeyId": "S3 access key ID is invalid. Check the AWS access key ID in Authentication.",
            "SignatureDoesNotMatch": "S3 request signature is invalid. Check the AWS secret access key and configured region.",
            "AccessDenied": "S3 access is denied. Grant the configured user or role s3:ListBucket and s3:GetObject permissions in IAM and the bucket policy.",
            "NoSuchBucket": "S3 bucket does not exist. Check the bucket name and AWS region.",
        }
        current = exc
        seen = set()
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            message = None
            if isinstance(current, ClientError):
                message = messages.get(current.response.get("Error", {}).get("Code"))
            elif isinstance(current, (EndpointConnectionError, ConnectTimeoutError)):
                message = "S3 endpoint is unreachable. Check the endpoint URL, AWS region, and network allowlist."
            if message:
                raise AirbyteTracedException(message=message, internal_message=str(exc), failure_type=FailureType.config_error) from exc
            current = current.__cause__ or current.__context__

    def _check_list_files(self, stream: AbstractFileBasedStream) -> RemoteFile:
        try:
            return super()._check_list_files(stream)
        except Exception as exc:
            self._raise_aws_error(exc)
            raise

    def _check_parse_record(self, stream: AbstractFileBasedStream, file: RemoteFile, logger: logging.Logger) -> None:
        try:
            return super()._check_parse_record(stream, file, logger)
        except Exception as exc:
            self._raise_aws_error(exc)
            if isinstance(exc, CheckAvailabilityError) and isinstance(exc.__cause__, Exception):
                raise AirbyteTracedException(
                    message="S3 file cannot be parsed with the configured format. Check the file format, encoding, and stream format options.",
                    internal_message=str(exc),
                    failure_type=FailureType.config_error,
                ) from exc
            raise

    def check_availability_and_parsability(
        self,
        stream,
        logger: logging.Logger,
        source: Optional[Source],
    ) -> Tuple[bool, Optional[str]]:
        parser = stream.get_parser()

        skip_flag = isinstance(stream.config, S3FileBasedStreamConfig) and stream.config.skip_full_check_for_parquet
        if not (isinstance(parser, ParquetParser) and skip_flag):
            try:
                return super().check_availability_and_parsability(stream, logger, source)
            except Exception as exc:
                self._raise_aws_error(exc)
                raise

        # Parquet path: validate config, list files, and open the file to verify
        # accessibility — but skip the full record parse to avoid loading entire
        # row groups into memory.
        config_check_result, config_check_error_message = parser.check_config(stream.config)
        if config_check_result is False:
            return False, config_check_error_message

        try:
            file = self._check_list_files(stream)
            handle = stream.stream_reader.open_file(file, parser.file_read_mode, None, logger)
            handle.close()
        except AirbyteTracedException as ate:
            raise ate
        except CheckAvailabilityError:
            return False, "".join(traceback.format_exc())
        except Exception as exc:
            self._raise_aws_error(exc)
            raise CheckAvailabilityError(FileBasedSourceError.ERROR_READING_FILE, stream=stream.name, file=file.uri) from exc

        return True, None
