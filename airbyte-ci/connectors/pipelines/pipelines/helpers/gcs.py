#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path
from typing import Tuple

from google.cloud import storage  # type: ignore
from google.oauth2 import service_account  # type: ignore
from pipelines import main_logger
from pipelines.consts import GCS_PUBLIC_DOMAIN


def upload_to_gcs(file_path: Path, bucket_name: str, object_name: str, credentials: str) -> Tuple[str, str]:
    """Upload a file to a GCS bucket.

    Args:
        file_path (Path): The path to the file to upload.
        bucket_name (str): The name of the GCS bucket.
        object_name (str): The name of the object in the GCS bucket.
        credentials (str): The GCS credentials as a JSON string.
    """
    # Exit early if file does not exist
    if not file_path.exists():
        main_logger.warning(f"File {file_path} does not exist. Skipping upload to GCS.")
        return "", ""

    credentials = service_account.Credentials.from_service_account_info(json.loads(credentials))
    client = storage.Client(credentials=credentials)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(str(file_path))
    gcs_uri = f"gs://{bucket_name}/{object_name}"
    public_url = f"{GCS_PUBLIC_DOMAIN}/{bucket_name}/{object_name}"
    return gcs_uri, public_url


def sanitize_gcp_credentials(raw_value: str) -> str:
    """Try to parse the raw string input that should contain a json object with the GCS credentials.
    It will raise an exception if the parsing fails and help us to fail fast on invalid credentials input.

    Args:
        raw_value (str): A string representing a json object with the GCS credentials.

    Returns:
        str: The raw value string if it was successfully parsed.
    """
    return json.dumps(json.loads(raw_value))
