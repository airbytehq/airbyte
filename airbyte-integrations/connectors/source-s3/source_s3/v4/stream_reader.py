#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from datetime import date as date_type, timedelta
from io import IOBase
from typing import Dict, Iterable, List, Optional, Set, Tuple, cast

import boto3.session
import pendulum
import psutil
import pytz
import smart_open
from botocore.client import BaseClient
from botocore.client import Config as ClientConfig
from botocore.credentials import RefreshableCredentials
from botocore.exceptions import ClientError
from botocore.session import get_session
from typing_extensions import override

from airbyte_cdk import FailureType
from airbyte_cdk.sources.file_based.exceptions import CustomFileBasedException, ErrorListingFiles, FileBasedSourceError, FileSizeLimitError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from source_s3.v4.config import Config
from source_s3.v4.zip_reader import DecompressedStream, RemoteFileInsideArchive, ZipContentReader, ZipFileHandler


class SourceS3StreamReader(AbstractFileBasedStreamReader):
    FILE_SIZE_LIMIT = 1_500_000_000

    def __init__(self):
        super().__init__()
        self._s3_client = None
        self._cloudtrail_cursor_date: Optional[datetime] = None
        self._check_mode: bool = False

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
            client_kv_args = _get_s3_compatible_client_args(self.config) if self.config.endpoint else {}

            # Set the region_name if it's provided in the config
            if self.config.region_name:
                client_kv_args["region_name"] = self.config.region_name

            if self.config.role_arn:
                self._s3_client = self._get_iam_s3_client(client_kv_args)
            else:
                # Only use explicit credentials if provided
                if self.config.aws_access_key_id and self.config.aws_secret_access_key:
                    self._s3_client = boto3.client(
                        "s3",
                        aws_access_key_id=self.config.aws_access_key_id,
                        aws_secret_access_key=self.config.aws_secret_access_key,
                        **client_kv_args,
                    )
                else:
                    # Use environment variables or instance profile credentials
                    self._s3_client = boto3.client("s3", **client_kv_args)

        return self._s3_client

    def _get_iam_s3_client(self, client_kv_args: dict) -> BaseClient:
        """
        Creates an S3 client using AWS Security Token Service (STS) with assumed role credentials. This method handles
        the authentication process by assuming an IAM role, optionally using an external ID for enhanced security.
        The obtained credentials are set to auto-refresh upon expiration, ensuring uninterrupted access to the S3 service.

        This method uses the current role (from environment variables or from the EKS pod's role) when performing
        assume role operations, rather than requiring explicit access keys.

        :param client_kv_args: A dictionary of key-value pairs for the boto3 S3 client constructor.
        :return: An instance of a boto3 S3 client with the assumed role credentials.

        The method assumes a role specified in the `self.config.role_arn` and creates a session with the S3 service.
        If `external_id` is set in the config, it will be used during the role assumption for additional security.
        """

        def refresh():
            # Use the current role (from environment variables or instance profile)
            # to assume the specified role instead of using explicit credentials
            client = boto3.client("sts")
            
            assume_role_params = {
                "RoleArn": self.config.role_arn,
                "RoleSessionName": "airbyte-source-s3",
            }
            
            # Add external ID if specified
            if self.config.external_id:
                assume_role_params["ExternalId"] = self.config.external_id
            
            role = client.assume_role(**assume_role_params)

            creds = role.get("Credentials", {})
            return {
                "access_key": creds["AccessKeyId"],
                "secret_key": creds["SecretAccessKey"],
                "token": creds["SessionToken"],
                "expiry_time": creds["Expiration"].isoformat(),
            }

        session_credentials = RefreshableCredentials.create_from_metadata(
            metadata=refresh(),
            refresh_using=refresh,
            method="sts-assume-role",
        )

        session = get_session()
        session._credentials = session_credentials
        autorefresh_session = boto3.Session(botocore_session=session)

        return autorefresh_session.client("s3", **client_kv_args)

    def set_cloudtrail_cursor_date(self, cursor_date: Optional[datetime]) -> None:
        self._cloudtrail_cursor_date = cursor_date

    def _extract_cloudtrail_base_prefix(self, globs: List[str]) -> Optional[str]:
        """Extract the CloudTrail base prefix (up to and including 'CloudTrail/') from globs."""
        for glob in globs:
            match = re.match(r"(.*CloudTrail/)", glob)
            if match:
                return match.group(1)
        return None

    def _discover_cloudtrail_regions(self, s3: BaseClient, bucket: str, base_prefix: str) -> List[str]:
        """Discover CloudTrail regions via delimiter-based listing (one API call)."""
        response = s3.list_objects_v2(Bucket=bucket, Prefix=base_prefix, Delimiter="/")
        regions = []
        for prefix_obj in response.get("CommonPrefixes", []):
            region = prefix_obj["Prefix"][len(base_prefix):].strip("/")
            if region:
                regions.append(region)
        return regions

    def _generate_cloudtrail_prefixes(self, base_prefix: str, regions: List[str], start_date: date_type, end_date: date_type) -> List[str]:
        """Generate per-day S3 prefixes for each region."""
        prefixes = []
        current = start_date
        while current <= end_date:
            date_path = current.strftime("%Y/%m/%d")
            for region in regions:
                prefixes.append(f"{base_prefix}{region}/{date_path}/")
            current += timedelta(days=1)
        return prefixes

    def _list_cloudtrail_prefix(self, s3: BaseClient, bucket: str, prefix: str, globs: List[str], logger: logging.Logger) -> List[RemoteFile]:
        """List all files under a single prefix. Called from thread pool."""
        files = []
        kwargs = {"Bucket": bucket, "Prefix": prefix}
        while True:
            response = s3.list_objects_v2(**kwargs)
            for obj in response.get("Contents", []):
                if self._is_folder(obj):
                    continue
                remote_file = self._handle_regular_file(obj)
                if self.file_matches_globs(remote_file, globs):
                    files.append(remote_file)
            if next_token := response.get("NextContinuationToken"):
                kwargs["ContinuationToken"] = next_token
            else:
                break
        return files

    def get_matching_files(self, globs: List[str], prefix: Optional[str], logger: logging.Logger) -> Iterable[RemoteFile]:
        """
        Get all files matching the specified glob patterns.
        Uses CloudTrail-optimized date-aware prefix listing when applicable.
        """
        # Check if CloudTrail optimization applies
        if getattr(self, "_config", None) is not None and self.config.flatten_records_key:
            base_prefix = self._extract_cloudtrail_base_prefix(globs)
            if base_prefix:
                yield from self._get_matching_files_cloudtrail(globs, base_prefix, logger)
                return

        # Default path: existing behavior (unchanged)
        s3 = self.s3_client
        prefixes = [prefix] if prefix else self.get_prefixes_from_globs(globs)
        seen = set()
        total_n_keys = 0

        try:
            for current_prefix in prefixes if prefixes else [None]:
                for remote_file in self._page(s3, globs, self.config.bucket, current_prefix, seen, logger):
                    total_n_keys += 1
                    yield remote_file

            logger.info(f"Finished listing objects from S3. Found {total_n_keys} objects total ({len(seen)} unique objects).")
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchBucket":
                raise CustomFileBasedException(
                    f"The bucket {self.config.bucket} does not exist.", failure_type=FailureType.config_error, exception=exc
                )
            self._raise_error_listing_files(globs, exc)
        except Exception as exc:
            self._raise_error_listing_files(globs, exc)

    def _check_cloudtrail_connectivity(self, s3: BaseClient, bucket: str, base_prefix: str, globs: List[str], logger: logging.Logger) -> Optional[RemoteFile]:
        """Quick connectivity check: list one file from today's prefix. Returns a RemoteFile or None."""
        today = date_type.today()
        regions = self._discover_cloudtrail_regions(s3, bucket, base_prefix)
        if not regions:
            return None
        # Try today's prefix for the first region, then yesterday if empty
        for days_back in range(3):
            d = today - timedelta(days=days_back)
            prefix = f"{base_prefix}{regions[0]}/{d.strftime('%Y/%m/%d')}/"
            response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)
            contents = response.get("Contents", [])
            if contents and not self._is_folder(contents[0]):
                return self._handle_regular_file(contents[0])
        return None

    def _get_matching_files_cloudtrail(self, globs: List[str], base_prefix: str, logger: logging.Logger) -> Iterable[RemoteFile]:
        """CloudTrail-optimized listing: date-aware prefixes, parallel threads."""
        s3 = self.s3_client
        bucket = self.config.bucket

        # Fast path for check mode: just verify we can list one file
        if self._check_mode:
            logger.info("CloudTrail check mode: quick connectivity verification")
            file = self._check_cloudtrail_connectivity(s3, bucket, base_prefix, globs, logger)
            if file:
                yield file
            return

        # Determine start date
        if self._cloudtrail_cursor_date:
            start_dt = self._cloudtrail_cursor_date  # cursor handles filtering, no overlap needed
            start = start_dt.date() if isinstance(start_dt, datetime) else start_dt
        elif self.config.start_date:
            start = pendulum.parse(self.config.start_date).date()
        else:
            logger.warning("CloudTrail mode: no cursor or start_date, falling back to broad listing")
            seen: Set[str] = set()
            for remote_file in self._page(s3, globs, self.config.bucket, base_prefix, seen, logger):
                yield remote_file
            return

        end = date_type.today()

        # Discover or use configured regions
        if hasattr(self.config, "cloudtrail_regions") and self.config.cloudtrail_regions:
            regions = self.config.cloudtrail_regions
        else:
            regions = self._discover_cloudtrail_regions(s3, bucket, base_prefix)

        if not regions:
            logger.warning(f"No CloudTrail regions found under {base_prefix}")
            return

        logger.info(f"CloudTrail listing: {len(regions)} regions, {start} to {end}")

        # Generate per-day prefixes
        prefixes = self._generate_cloudtrail_prefixes(base_prefix, regions, start, end)
        logger.info(f"Generated {len(prefixes)} day-prefixes for parallel listing")

        # List in parallel
        total_files = 0
        seen_uris: Set[str] = set()
        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = {
                pool.submit(self._list_cloudtrail_prefix, s3, bucket, p, globs, logger): p
                for p in prefixes
            }
            for future in as_completed(futures):
                prefix_name = futures[future]
                try:
                    files = future.result()
                    for f in files:
                        if f.uri not in seen_uris:
                            seen_uris.add(f.uri)
                            total_files += 1
                            yield f
                except Exception as exc:
                    logger.error(f"Error listing prefix {prefix_name}: {exc}")
                    raise

        logger.info(f"CloudTrail listing complete: {total_files} files from {len(prefixes)} prefixes")

    def _raise_error_listing_files(self, globs: List[str], exc: Optional[Exception] = None):
        """Helper method to raise the ErrorListingFiles exception."""
        raise ErrorListingFiles(
            FileBasedSourceError.ERROR_LISTING_FILES,
            source="s3",
            bucket=self.config.bucket,
            globs=globs,
            endpoint=self.config.endpoint,
        ) from exc

    def open_file(self, file: RemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        try:
            params = {"client": self.s3_client}
        except Exception as exc:
            raise exc

        logger.debug(f"try to open {file.uri}")
        try:
            if isinstance(file, RemoteFileInsideArchive):
                s3_file_object = smart_open.open(f"s3://{self.config.bucket}/{file.uri.split('#')[0]}", transport_params=params, mode="rb")
                decompressed_stream = DecompressedStream(s3_file_object, file)
                result = ZipContentReader(decompressed_stream, encoding)
            else:
                result = smart_open.open(
                    f"s3://{self.config.bucket}/{file.uri}", transport_params=params, mode=mode.value, encoding=encoding
                )
        except OSError:
            logger.warning(
                f"We don't have access to {file.uri}. The file appears to have become unreachable during sync."
                f"Check whether key {file.uri} exists in `{self.config.bucket}` bucket and/or has proper ACL permissions"
            )

        # we can simply return the result here as it is a context manager itself that will release all resources
        return result

    @staticmethod
    def create_progress_handler(file_size: int, local_file_path: str, logger: logging.Logger):
        previous_bytes_checkpoint = 0
        total_bytes_transferred = 0

        def progress_handler(bytes_transferred: int):
            nonlocal previous_bytes_checkpoint, total_bytes_transferred
            total_bytes_transferred += bytes_transferred
            if total_bytes_transferred - previous_bytes_checkpoint >= 100 * 1024 * 1024:
                logger.info(
                    f"{total_bytes_transferred / (1024 * 1024):,.2f} MB ({total_bytes_transferred / (1024 * 1024 * 1024):.2f} GB) "
                    f"of {file_size / (1024 * 1024):,.2f} MB ({file_size / (1024 * 1024 * 1024):.2f} GB) "
                    f"written to {local_file_path}"
                )
                previous_bytes_checkpoint = total_bytes_transferred

                # Get available disk space
                disk_usage = psutil.disk_usage("/")
                available_disk_space = disk_usage.free

                # Get available memory
                memory_info = psutil.virtual_memory()
                available_memory = memory_info.available
                logger.info(
                    f"Available disk space: {available_disk_space / (1024 * 1024):,.2f} MB ({available_disk_space / (1024 * 1024 * 1024):.2f} GB), "
                    f"available memory: {available_memory / (1024 * 1024):,.2f} MB ({available_memory / (1024 * 1024 * 1024):.2f} GB)."
                )

        return progress_handler

    @override
    def get_file(self, file: RemoteFile, local_directory: str, logger: logging.Logger) -> Dict[str, str | int]:
        """
        Downloads a file from an S3 bucket to a specified local directory.

        Args:
            file (RemoteFile): The remote file object containing URI and metadata.
            local_directory (str): The local directory path where the file will be downloaded.
            logger (logging.Logger): Logger for logging information and errors.

        Returns:
            dict: A dictionary containing the following:
                - "file_url" (str): The absolute path of the downloaded file.
                - "bytes" (int): The file size in bytes.
                - "file_relative_path" (str): The relative path of the file for local storage. Is relative to local_directory as
                this a mounted volume in the pod container.

        Raises:
            FileSizeLimitError: If the file size exceeds the predefined limit (1 GB).
        """
        file_size = self.file_size(file)
        # I'm putting this check here so we can remove the safety wheels per connector when ready.
        if file_size > self.FILE_SIZE_LIMIT:
            message = "File size exceeds the 1 GB limit."
            raise FileSizeLimitError(message=message, internal_message=message, failure_type=FailureType.config_error)

        file_relative_path, local_file_path, absolute_file_path = self._get_file_transfer_paths(file, local_directory)

        logger.info(
            f"Starting to download the file {file.uri} with size: {file_size / (1024 * 1024):,.2f} MB ({file_size / (1024 * 1024 * 1024):.2f} GB)"
        )
        # at some moment maybe we will require to play with the max_pool_connections and max_concurrency of s3 config
        start_download_time = time.time()
        progress_handler = self.create_progress_handler(file_size, local_file_path, logger)
        self.s3_client.download_file(self.config.bucket, file.uri, local_file_path, Callback=progress_handler)
        write_duration = time.time() - start_download_time
        logger.info(f"Finished downloading the file {file.uri} and saved to {local_file_path} in {write_duration:,.2f} seconds.")

        return {"file_url": absolute_file_path, "bytes": file_size, "file_relative_path": file_relative_path}

    @override
    def file_size(self, file: RemoteFile) -> int:
        s3_object: boto3.s3.Object = self.s3_client.get_object(
            Bucket=self.config.bucket,
            Key=file.uri,
        )
        return cast(int, s3_object["ContentLength"])

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
            response = s3.list_objects_v2(Prefix=prefix, **kwargs) if prefix else s3.list_objects_v2(**kwargs)
            key_count = response.get("KeyCount")
            total_n_keys_for_prefix += key_count
            logger.info(f"Received {key_count} objects from S3 for prefix '{prefix}'.")

            if "Contents" in response:
                for file in response["Contents"]:
                    if self._is_folder(file):
                        continue

                    for remote_file in self._handle_file(file):
                        if (
                            self.file_matches_globs(remote_file, globs)
                            and self.is_modified_after_start_date(remote_file.last_modified)
                            and remote_file.uri not in seen
                        ):
                            seen.add(remote_file.uri)
                            yield remote_file
            else:
                logger.warning(f"Invalid response from S3; missing 'Contents' key. kwargs={kwargs}.")

            if next_token := response.get("NextContinuationToken"):
                kwargs["ContinuationToken"] = next_token
            else:
                logger.info(f"Finished listing objects from S3 for prefix={prefix}. Found {total_n_keys_for_prefix} objects.")
                break

    def is_modified_after_start_date(self, last_modified_date: Optional[datetime]) -> bool:
        """Returns True if given date higher or equal than start date or something is missing"""
        if not (self.config.start_date and last_modified_date):
            return True
        return last_modified_date >= pendulum.parse(self.config.start_date).naive()

    def _handle_file(self, file):
        if file["Key"].endswith(".zip"):
            yield from self._handle_zip_file(file)
        else:
            yield self._handle_regular_file(file)

    def _handle_zip_file(self, file):
        zip_handler = ZipFileHandler(self.s3_client, self.config)
        zip_members, cd_start = zip_handler.get_zip_files(file["Key"])

        for zip_member in zip_members:
            remote_file = RemoteFileInsideArchive(
                uri=file["Key"] + "#" + zip_member.filename,
                last_modified=datetime(*zip_member.date_time).astimezone(pytz.utc).replace(tzinfo=None),
                start_offset=zip_member.header_offset + cd_start,
                compressed_size=zip_member.compress_size,
                uncompressed_size=zip_member.file_size,
                compression_method=zip_member.compress_type,
            )
            yield remote_file

    def _handle_regular_file(self, file):
        remote_file = RemoteFile(uri=file["Key"], last_modified=file["LastModified"].astimezone(pytz.utc).replace(tzinfo=None))
        return remote_file


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
