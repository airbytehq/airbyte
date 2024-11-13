#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups functions to interact with remote storage services like S3 or GCS."""

import uuid
from pathlib import Path
from typing import List, Optional, Tuple

from dagger import Client, File
from pipelines.helpers.utils import get_exec_result, secret_host_variable, with_exit_code
from pipelines.models.secrets import Secret

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
    return await with_exit_code(
        dagger_client.container()
        .from_("amazon/aws-cli:latest")
        .with_file(str(file_to_upload_path), file_to_upload)
        .with_(secret_host_variable(dagger_client, "AWS_ACCESS_KEY_ID"))
        .with_(secret_host_variable(dagger_client, "AWS_SECRET_ACCESS_KEY"))
        .with_(secret_host_variable(dagger_client, "AWS_DEFAULT_REGION"))
        .with_exec(["s3", "cp", str(file_to_upload_path), s3_uri], use_entrypoint=True)
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
        gcs_credentials (Secret): The secret holding the credentials to get and upload the targeted GCS bucket.
        flags (List[str]): Flags to be passed to the 'gcloud storage cp' command.
        cache_upload (bool): If false, the gcloud commands will be executed on each call.
    Returns:
        Tuple[int, str, str]: Exit code, stdout, stderr
    """
    flags = [] if flags is None else flags
    gcs_uri = f"gs://{bucket}/{key}"
    dagger_client = dagger_client
    cp_command = ["gcloud", "storage", "cp"] + flags + ["to_upload", gcs_uri]

    gcloud_container = (
        dagger_client.container()
        .from_(f"google/cloud-sdk:{GOOGLE_CLOUD_SDK_TAG}")
        .with_workdir("/upload")
        .with_mounted_secret("credentials.json", gcs_credentials.as_dagger_secret(dagger_client))
        .with_env_variable("GOOGLE_APPLICATION_CREDENTIALS", "/upload/credentials.json")
        .with_file("to_upload", file_to_upload)
    )
    if not cache_upload:
        gcloud_container = gcloud_container.with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
    else:
        gcloud_container = gcloud_container.without_env_variable("CACHEBUSTER")

    gcloud_auth_container = gcloud_container.with_exec(["gcloud", "auth", "login", "--cred-file=credentials.json"], use_entrypoint=True)
    if (await with_exit_code(gcloud_auth_container)) == 1:
        gcloud_auth_container = gcloud_container.with_exec(
            ["gcloud", "auth", "activate-service-account", "--key-file", "credentials.json"], use_entrypoint=True
        )

    gcloud_cp_container = gcloud_auth_container.with_exec(cp_command)
    return await get_exec_result(gcloud_cp_container)
