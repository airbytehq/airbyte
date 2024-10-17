# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import logging

from google.api_core.exceptions import PermissionDenied
from google.cloud import secretmanager

LIVE_TESTS_AIRBYTE_API_KEY_SECRET_ID = "projects/587336813068/secrets/live_tests_airbyte_api_key"


def get_secret_value(secret_manager_client: secretmanager.SecretManagerServiceClient, secret_id: str) -> str:
    """Get the value of the enabled version of a secret

    Args:
        secret_manager_client (secretmanager.SecretManagerServiceClient): The secret manager client
        secret_id (str): The id of the secret

    Returns:
        str: The value of the enabled version of the secret
    """
    try:
        response = secret_manager_client.list_secret_versions(request={"parent": secret_id, "filter": "state:ENABLED"})
        if len(response.versions) == 0:
            raise ValueError(f"No enabled version of secret {secret_id} found")
        enabled_version = response.versions[0]
        response = secret_manager_client.access_secret_version(name=enabled_version.name)
        return response.payload.data.decode("UTF-8")
    except PermissionDenied as e:
        logging.exception(
            f"Permission denied while trying to access secret {secret_id}. Please write to #dev-tooling in Airbyte Slack for help.",
            exc_info=e,
        )
        raise e


def get_airbyte_api_key() -> str:
    secret_manager_client = secretmanager.SecretManagerServiceClient()
    return get_secret_value(secret_manager_client, LIVE_TESTS_AIRBYTE_API_KEY_SECRET_ID)
