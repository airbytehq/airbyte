#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups functions to interact with remote storage services like S3 or GCS."""

from pathlib import Path

from ci_connector_ops.pipelines.utils import with_exit_code
from dagger import Client, File, Secret


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
