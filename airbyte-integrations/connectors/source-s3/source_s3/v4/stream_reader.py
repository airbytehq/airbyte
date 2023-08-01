#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from contextlib import contextmanager
from io import IOBase
from typing import Iterable, List, Optional, Set

import boto3.session
import smart_open
from airbyte_cdk.sources.file_based.exceptions import ErrorListingFiles, FileBasedSourceError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from botocore.client import BaseClient
from botocore.client import Config as ClientConfig
from source_s3.v4.config import Config


class SourceS3StreamReader(AbstractFileBasedStreamReader):
    def __init__(self):
        super().__init__()
        self._s3_client = None

    @property
    def config(self) -> Config:
        return self._config

    @config.setter
    def config(self, value: Config):
        """
        FileBasedSource reads the config from disk and parses it, and once parsed, the source sets the config on its StreamReader.

        Note: FileBasedSource only requires the keys defined in the abstract config, whereas concrete implementations of StreamReader
        will require keys that (for example) allow it to authenticate with the 3rd party.

        Therefore, concrete implementations of AbstractFileBasedStreamReader's config setter should assert that `value` is of the correct
        config type for that type of StreamReader.
        """
        assert isinstance(value, Config)
        self._config = value

    @property
    def s3_client(self) -> BaseClient:
        if self.config is None:
            # We shouldn't hit this; config should always get set before attempting to
            # list or read files.
            raise ValueError("Source config is missing; cannot create the S3 client.")
        if self._s3_client is None:
            if self.config.endpoint:
                client_kv_args = _get_s3_compatible_client_args(self.config)
                self._s3_client = boto3.client("s3", **client_kv_args)
            else:
                self._s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=self.config.aws_access_key_id,
                    aws_secret_access_key=self.config.aws_secret_access_key,
                )
        return self._s3_client

    def get_matching_files(self, globs: List[str], logger: logging.Logger) -> Iterable[RemoteFile]:
        """
        Get all files matching the specified glob patterns.
        """
        s3 = self.s3_client
        prefixes = self.get_prefixes_from_globs(globs)
        seen = set()
        total_n_keys = 0

        try:
            if prefixes:
                for prefix in prefixes:
                    for remote_file in self._page(s3, globs, self.config.bucket, prefix, seen, logger):
                        total_n_keys += 1
                        yield remote_file
            else:
                for remote_file in self._page(s3, globs, self.config.bucket, None, seen, logger):
                    total_n_keys += 1
                    yield remote_file

            logger.info(f"Finished listing objects from S3. Found {total_n_keys} objects total ({len(seen)} unique objects).")
        except Exception as exc:
            raise ErrorListingFiles(
                FileBasedSourceError.ERROR_LISTING_FILES,
                source="s3",
                bucket=self.config.bucket,
                globs=globs,
                endpoint=self.config.endpoint,
            ) from exc

    @contextmanager
    def open_file(self, file: RemoteFile, mode: FileReadMode, logger: logging.Logger) -> IOBase:
        try:
            params = {"client": self.s3_client}
        except Exception as exc:
            raise exc

        logger.debug(f"try to open {file.uri}")
        try:
            result = smart_open.open(f"s3://{self.config.bucket}/{file.uri}", transport_params=params, mode=mode.value)
        except OSError:
            logger.warning(
                f"We don't have access to {file.uri}. The file appears to have become unreachable during sync."
                f"Check whether key {file.uri} exists in `{self.config.bucket}` bucket and/or has proper ACL permissions"
            )
        # see https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager for why we do this
        try:
            yield result
        finally:
            result.close()

    @staticmethod
    def _is_folder(file) -> bool:
        return file["Key"].endswith("/")

    def _page(
        self, s3: BaseClient, globs: List[str], bucket: str, prefix: Optional[str], seen: Set[str], logger: logging.Logger
    ) -> Iterable[RemoteFile]:
        """
        Page through lists of S3 objects.
        """
        total_n_keys_for_prefix = 0
        kwargs = {"Bucket": bucket}
        while True:
            response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix) if prefix else s3.list_objects_v2(Bucket=bucket)
            key_count = response.get("KeyCount")
            total_n_keys_for_prefix += key_count
            logger.info(f"Received {key_count} objects from S3 for prefix '{prefix}'.")

            if "Contents" in response:
                for file in response["Contents"]:
                    if self._is_folder(file):
                        continue
                    remote_file = RemoteFile(uri=file["Key"], last_modified=file["LastModified"])
                    if self.file_matches_globs(remote_file, globs) and remote_file.uri not in seen:
                        seen.add(remote_file.uri)
                        yield remote_file
            else:
                logger.warning(f"Invalid response from S3; missing 'Contents' key. kwargs={kwargs}.")

            if next_token := response.get("NextContinuationToken"):
                kwargs["ContinuationToken"] = next_token
            else:
                logger.info(f"Finished listing objects from S3 for prefix={prefix}. Found {total_n_keys_for_prefix} objects.")
                break


def _get_s3_compatible_client_args(config: Config) -> dict:
    """
    Returns map of args used for creating s3 boto3 client.
    """
    client_kv_args = {
        "config": ClientConfig(s3={"addressing_style": "auto"}),
        "endpoint_url": config.endpoint,
        "use_ssl": True,
        "verify": True,
    }
    return client_kv_args
