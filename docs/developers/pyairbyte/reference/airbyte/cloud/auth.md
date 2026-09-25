---
id: airbyte-cloud-auth
title: "airbyte.cloud.auth Module"
sidebar_label: "airbyte.cloud.auth"
toc_max_heading_level: 5
---

# `airbyte.cloud.auth` Module

Authentication-related constants and utilities for the Airbyte Cloud.

### `resolve_cloud_api_url` {#airbyte.cloud.auth.resolve_cloud_api_url}

<ApiMember kind="function">

<ApiSignature>

```python
def resolve_cloud_api_url(input_value: str | None = None, /) -> str
```

</ApiSignature>

Get the Airbyte Cloud API URL from the environment, or return the default.

</ApiMember>

### `resolve_cloud_bearer_token` {#airbyte.cloud.auth.resolve_cloud_bearer_token}

<ApiMember kind="function">

<ApiSignature>

```python
def resolve_cloud_bearer_token(
    input_value: str | airbyte.secrets.base.SecretString | None = None,
    /,
) -> airbyte.secrets.base.SecretString | None
```

</ApiSignature>

Get the Airbyte Cloud bearer token from the environment.

Unlike other resolve functions, this returns None if no bearer token is found,
since bearer token authentication is optional (client credentials can be used instead).

**Args:**

- **`input_value`**: Optional explicit bearer token value. If provided, it will be returned directly (wrapped in SecretString if needed).

**Returns:**

The bearer token as a SecretString, or None if not found.

</ApiMember>

### `resolve_cloud_client_id` {#airbyte.cloud.auth.resolve_cloud_client_id}

<ApiMember kind="function">

<ApiSignature>

```python
def resolve_cloud_client_id(
    input_value: str | airbyte.secrets.base.SecretString | None = None,
    /,
) -> airbyte.secrets.base.SecretString
```

</ApiSignature>

Get the Airbyte Cloud client ID from the environment.

</ApiMember>

### `resolve_cloud_client_secret` {#airbyte.cloud.auth.resolve_cloud_client_secret}

<ApiMember kind="function">

<ApiSignature>

```python
def resolve_cloud_client_secret(
    input_value: str | airbyte.secrets.base.SecretString | None = None,
    /,
) -> airbyte.secrets.base.SecretString
```

</ApiSignature>

Get the Airbyte Cloud client secret from the environment.

</ApiMember>

### `resolve_cloud_config_api_url` {#airbyte.cloud.auth.resolve_cloud_config_api_url}

<ApiMember kind="function">

<ApiSignature>

```python
def resolve_cloud_config_api_url(
    input_value: str | None = None,
    /,
) -> str | None
```

</ApiSignature>

Get the Airbyte Cloud Config API URL from the environment, or return None if not set.

The Config API is a separate internal API used for certain operations like
connector builder projects and custom source definitions.

**Returns:**

The Config API URL if set via environment variable or input, None otherwise.

</ApiMember>

### `resolve_cloud_workspace_id` {#airbyte.cloud.auth.resolve_cloud_workspace_id}

<ApiMember kind="function">

<ApiSignature>

```python
def resolve_cloud_workspace_id(input_value: str | None = None, /) -> str
```

</ApiSignature>

Get the Airbyte Cloud workspace ID from the environment, or return None if not set.

</ApiMember>