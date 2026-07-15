---
id: airbyte-cloud-client_config
title: airbyte.cloud.client_config
---

Module airbyte.cloud.client_config
==================================
Cloud client configuration for Airbyte Cloud API authentication.

This module provides the CloudClientConfig class for managing authentication
credentials and API configuration when connecting to Airbyte Cloud, OSS, or
Enterprise instances.

Two authentication methods are supported (mutually exclusive):
1. OAuth2 client credentials (client_id + client_secret)
2. Bearer token authentication

Example usage with client credentials:
    ```python
    from airbyte.cloud.client_config import CloudClientConfig

    config = CloudClientConfig(
        client_id="your-client-id",
        client_secret="your-client-secret",
    )
    ```

Example usage with bearer token:
    ```python
    from airbyte.cloud.client_config import CloudClientConfig

    config = CloudClientConfig(
        bearer_token="your-bearer-token",
    )
    ```

Example using environment variables:
    ```python
    from airbyte.cloud.client_config import CloudClientConfig

    # Resolves from AIRBYTE_CLOUD_CLIENT_ID, AIRBYTE_CLOUD_CLIENT_SECRET,
    # AIRBYTE_CLOUD_BEARER_TOKEN, and AIRBYTE_CLOUD_API_URL environment variables
    config = CloudClientConfig.from_env()
    ```

Classes
-------

`CloudClientConfig(client_id: SecretString | None = None, client_secret: SecretString | None = None, bearer_token: SecretString | None = None, api_root: str = 'https://api.airbyte.com/v1')`
:   Client configuration for Airbyte Cloud API.
    
    This class encapsulates the authentication and API configuration needed to connect
    to Airbyte Cloud, OSS, or Enterprise instances. It supports two mutually
    exclusive authentication methods:
    
    1. OAuth2 client credentials flow (client_id + client_secret)
    2. Bearer token authentication
    
    Exactly one authentication method must be provided. Providing both or neither
    will raise a validation error.
    
    Attributes:
        client_id: OAuth2 client ID for client credentials flow.
        client_secret: OAuth2 client secret for client credentials flow.
        bearer_token: Pre-generated bearer token for direct authentication.
        api_root: The API root URL. Defaults to Airbyte Cloud API.

    ### Static methods

    `from_env(*, api_root: str | None = None) ‑> airbyte.cloud.client_config.CloudClientConfig`
    :   Create CloudClientConfig from environment variables.
        
        This factory method resolves credentials from environment variables,
        providing a convenient way to create credentials without explicitly
        passing secrets.
        
        Environment variables used:
            - `AIRBYTE_CLOUD_CLIENT_ID`: OAuth client ID (for client credentials flow).
            - `AIRBYTE_CLOUD_CLIENT_SECRET`: OAuth client secret (for client credentials flow).
            - `AIRBYTE_CLOUD_BEARER_TOKEN`: Bearer token (alternative to client credentials).
            - `AIRBYTE_CLOUD_API_URL`: Optional. The API root URL (defaults to Airbyte Cloud).
        
        The method will first check for a bearer token. If not found, it will
        attempt to use client credentials.
        
        Args:
            api_root: The API root URL. If not provided, will be resolved from
                the `AIRBYTE_CLOUD_API_URL` environment variable, or default to
                the Airbyte Cloud API.
        
        Returns:
            A CloudClientConfig instance configured with credentials from the environment.
        
        Raises:
            PyAirbyteSecretNotFoundError: If required credentials are not found in
                the environment.

    ### Instance variables

    `api_root: str`
    :   The API root URL. Defaults to Airbyte Cloud API.

    `bearer_token: airbyte.secrets.base.SecretString | None`
    :   Bearer token for direct authentication (alternative to client credentials).

    `client_id: airbyte.secrets.base.SecretString | None`
    :   OAuth2 client ID for client credentials authentication.

    `client_secret: airbyte.secrets.base.SecretString | None`
    :   OAuth2 client secret for client credentials authentication.

    `uses_bearer_token: bool`
    :   Return True if using bearer token authentication.

    `uses_client_credentials: bool`
    :   Return True if using client credentials authentication.