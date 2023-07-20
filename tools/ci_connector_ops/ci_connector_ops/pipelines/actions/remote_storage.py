#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups functions to interact with remote storage services like S3 or GCS."""

import uuid
from pathlib import Path
from typing import List, Optional, Tuple

import asyncer
from ci_connector_ops.pipelines.utils import with_exit_code, with_stderr, with_stdout
from dagger import Client, File, Secret

GOOGLE_CLOUD_SDK_TAG = "425.0.0-slim"


async def upload_to_s3(dagger_client: Client, file_to_upload_path: Path, key: str, bucket: str) -> int:
    """Upload a local file to S3 using the AWS CLI docker image and running aws s3 cp command.

    Args:
        dagger_client (Client): The dagger client.
        file_to_upload_path (Path): The local path to the file to upload.
        key (str): The key that will be written on the S3 bucket.
        bucket (str): The S3 bucket name.

    Returns:
        int: Exit code of the upload process.
    """
    s3_uri = f"s3://{bucket}/{key}"
    file_to_upload: File = dagger_client.host().directory(".", include=[str(file_to_upload_path)]).file(str(file_to_upload_path))
    aws_access_key_id: Secret = dagger_client.host().env_variable("AWS_ACCESS_KEY_ID").secret()
    aws_secret_access_key: Secret = dagger_client.host().env_variable("AWS_SECRET_ACCESS_KEY").secret()
    aws_region: Secret = dagger_client.host().env_variable("AWS_DEFAULT_REGION").secret()
    return await with_exit_code(
        dagger_client.container()
        .from_("amazon/aws-cli:latest")
        .with_file(str(file_to_upload_path), file_to_upload)
        .with_secret_variable("AWS_ACCESS_KEY_ID", aws_access_key_id)
        .with_secret_variable("AWS_SECRET_ACCESS_KEY", aws_secret_access_key)
        .with_secret_variable("AWS_DEFAULT_REGION", aws_region)
        .with_exec(["s3", "cp", str(file_to_upload_path), s3_uri])
    )


async def upload_to_gcs(
    dagger_client: Client,
    file_to_upload: File,
    key: str,
    bucket: str,
    gcs_credentials: Secret,
    flags: Optional[List] = None,
    cache_upload: bool = False,
) -> Tuple[int, str, str]:
    """Upload a local file to GCS using the AWS CLI docker image and running aws s3 cp command.
    Args:
        dagger_client (Client): The dagger client.
        file_to_upload (File): The dagger File to upload.
        key (str): The key that will be written on the S3 bucket.
        bucket (str): The S3 bucket name.
        gcs_credentials (Secret): The dagger secret holding the credentials to get and upload the targeted GCS bucket.
        flags (List[str]): Flags to be passed to the 'gcloud storage cp' command.
        cache_upload (bool): If false, the gcloud commands will be executed on each call.
    Returns:
        Tuple[int, str, str]: Exit code, stdout, stderr
    """
    flags = [] if flags is None else flags
    gcs_uri = f"gs://{bucket}/{key}"
    dagger_client = dagger_client.pipeline(f"Upload file to {gcs_uri}")
    cp_command = ["gcloud", "storage", "cp"] + flags + ["to_upload", gcs_uri]

    gcloud_container = (
        dagger_client.container()
        .from_(f"google/cloud-sdk:{GOOGLE_CLOUD_SDK_TAG}")
        .with_workdir("/upload")
        .with_new_file("credentials.json", await gcs_credentials.plaintext())
        .with_env_variable("GOOGLE_APPLICATION_CREDENTIALS", "/upload/credentials.json")
        .with_file("to_upload", file_to_upload)
    )
    if not cache_upload:
        gcloud_container = gcloud_container.with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
    else:
        gcloud_container = gcloud_container.without_env_variable("CACHEBUSTER")

    gcloud_auth_container = gcloud_container.with_exec(["gcloud", "auth", "login", "--cred-file=credentials.json"])
    if (await with_exit_code(gcloud_auth_container)) == 1:
        gcloud_auth_container = gcloud_container.with_exec(["gcloud", "auth", "activate-service-account", "--key-file", "credentials.json"])

    gcloud_cp_container = gcloud_auth_container.with_exec(cp_command)

    async with asyncer.create_task_group() as task_group:
        soon_exit_code = task_group.soonify(with_exit_code)(gcloud_cp_container)
        soon_stderr = task_group.soonify(with_stderr)(gcloud_cp_container)
        soon_stdout = task_group.soonify(with_stdout)(gcloud_cp_container)
    return soon_exit_code.value, soon_stdout.value, soon_stderr.value
