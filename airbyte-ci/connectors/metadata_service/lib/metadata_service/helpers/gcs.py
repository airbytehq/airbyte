#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import base64
import json
import os

from google.cloud import storage
from google.oauth2 import service_account


def get_gcs_storage_client() -> storage.Client:
    """Get the GCS storage client using credentials form GCS_CREDENTIALS env variable."""
    gcs_creds = os.environ.get("GCS_CREDENTIALS")
    if not gcs_creds:
        raise ValueError("Please set the GCS_CREDENTIALS env var.")

    service_account_info = json.loads(gcs_creds)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    return storage.Client(credentials=credentials)
