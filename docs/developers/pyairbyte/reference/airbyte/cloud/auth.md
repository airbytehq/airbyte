---
id: airbyte-cloud-auth
title: airbyte.cloud.auth
---

Module airbyte.cloud.auth
=========================
Authentication-related constants and utilities for the Airbyte Cloud.

Functions
---------

`resolve_cloud_api_url(input_value: str | None = None, /) ‑> str`
:   Get the Airbyte Cloud API URL from the environment, or return the default.

`resolve_cloud_bearer_token(input_value: str | airbyte.secrets.base.SecretString | None = None, /) ‑> airbyte.secrets.base.SecretString | None`
:   Get the Airbyte Cloud bearer token from the environment.
    
    Unlike other resolve functions, this returns None if no bearer token is found,
    since bearer token authentication is optional (client credentials can be used instead).
    
    Args:
        input_value: Optional explicit bearer token value. If provided, it will be
            returned directly (wrapped in SecretString if needed).
    
    Returns:
        The bearer token as a SecretString, or None if not found.

`resolve_cloud_client_id(input_value: str | airbyte.secrets.base.SecretString | None = None, /) ‑> airbyte.secrets.base.SecretString`
:   Get the Airbyte Cloud client ID from the environment.

`resolve_cloud_client_secret(input_value: str | airbyte.secrets.base.SecretString | None = None, /) ‑> airbyte.secrets.base.SecretString`
:   Get the Airbyte Cloud client secret from the environment.

`resolve_cloud_config_api_url(input_value: str | None = None, /) ‑> str | None`
:   Get the Airbyte Cloud Config API URL from the environment, or return None if not set.
    
    The Config API is a separate internal API used for certain operations like
    connector builder projects and custom source definitions.
    
    Returns:
        The Config API URL if set via environment variable or input, None otherwise.

`resolve_cloud_workspace_id(input_value: str | None = None, /) ‑> str`
:   Get the Airbyte Cloud workspace ID from the environment, or return None if not set.