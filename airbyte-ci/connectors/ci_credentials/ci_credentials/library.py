# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Library code for the ci_credentials connector.

These functions are designed to be called by Python code.
"""
from __future__ import annotations

import json
import os
from common_utils import Logger

from . import SecretsManager
from .models import RemoteSecret

logger = Logger()

ENV_GCP_GSM_CREDENTIALS = "GCP_GSM_CREDENTIALS"


def get_secrets_manager(
    connector_name: str | None = None,
    gcp_gsm_credentials: dict | str | None = None,
) -> SecretsManager:
    """Get a SecretsManager instance.

    Args:
        connector_name: The name of the connector, or "all" to load secrets for all connectors.
        gcp_gsm_credentials: The credentials for Google Secret Manager. Can be a dict, a JSON
        string, or None. If None, the value of the GCP_GSM_CREDENTIALS environment variable will be
        used.
    """
    if gcp_gsm_credentials is None:
        gcp_gsm_credentials = os.getenv(ENV_GCP_GSM_CREDENTIALS)

    if gcp_gsm_credentials is None:
        raise ValueError("GCP_GSM_CREDENTIALS shouldn't be empty!")

    if isinstance(gcp_gsm_credentials, str):
        gcp_gsm_credentials = json.loads(gcp_gsm_credentials)

    return SecretsManager(
        connector_name=connector_name,
        gsm_credentials=gcp_gsm_credentials,
    )

def get_connector_secrets(
    connector_name: str | None = None,
    gcp_gsm_credentials: dict | str | None = None,
) -> tuple[list[RemoteSecret], SecretsManager]:
    """Get the secrets for a connector.

    This is a thin wrapper around `get_secrets_manager`.

    Args:
        connector_name: The name of the connector. Use `None` or `'all'` to load secrets for all
            connectors.
        gcp_gsm_credentials: The credentials for Google Secret Manager. Can be a dict, a JSON
            string, or None. If None, the value of the GCP_GSM_CREDENTIALS environment variable will
            be used.

    Returns:
        A tuple containing the (1) a list of secrets and (2) the SecretsManager instance.

    Usage:

    If you only need the secrets, you can use the following code:

    ```python
    secrets, _ = get_connector_secrets(connector_name="my_connector")
    ```

    If you need to do additional work with the Secret Manager, you can use the following code:

    ```python
    secrets, secrets_manager = get_connector_secrets(connector_name="my_connector")
    ```
    """
    secrets_manager = get_secrets_manager(
        connector_name=connector_name,
        gcp_gsm_credentials=gcp_gsm_credentials,
    )
    return secrets_manager.read_from_gsm(), secrets_manager
