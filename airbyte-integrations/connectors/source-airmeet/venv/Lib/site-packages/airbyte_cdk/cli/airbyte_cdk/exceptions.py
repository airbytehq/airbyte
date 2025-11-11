# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Exceptions for the Airbyte CDK CLI."""

from dataclasses import dataclass


@dataclass(kw_only=True)
class ConnectorSecretWithNoValidVersionsError(Exception):
    """Error when a connector secret has no valid versions."""

    connector_name: str
    secret_name: str
    gcp_project_id: str

    def __str__(self) -> str:
        """Return a string representation of the exception."""
        from airbyte_cdk.cli.airbyte_cdk._secrets import _get_secret_url

        url = _get_secret_url(self.secret_name, self.gcp_project_id)
        return (
            f"No valid versions found for secret '{self.secret_name}' in connector '{self.connector_name}'. "
            f"Please check the following URL for more information:\n- {url}"
        )
