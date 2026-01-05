---
sidebar_label: auth
title: airbyte.cloud.auth
---

Authentication-related constants and utilities for the Airbyte Cloud.

## constants

## SecretString

## get\_secret

## try\_get\_secret

#### resolve\_cloud\_bearer\_token

```python
def resolve_cloud_bearer_token(
        input_value: str | SecretString | None = None) -> SecretString | None
```

Get the Airbyte Cloud bearer token from the environment.

Unlike other resolve functions, this returns None if no bearer token is found,
since bearer token authentication is optional (client credentials can be used instead).

**Arguments**:

- `input_value` - Optional explicit bearer token value. If provided, it will be
  returned directly (wrapped in SecretString if needed).
  

**Returns**:

  The bearer token as a SecretString, or None if not found.

#### resolve\_cloud\_client\_secret

```python
def resolve_cloud_client_secret(
        input_value: str | SecretString | None = None) -> SecretString
```

Get the Airbyte Cloud client secret from the environment.

#### resolve\_cloud\_client\_id

```python
def resolve_cloud_client_id(
        input_value: str | SecretString | None = None) -> SecretString
```

Get the Airbyte Cloud client ID from the environment.

#### resolve\_cloud\_api\_url

```python
def resolve_cloud_api_url(input_value: str | None = None) -> str
```

Get the Airbyte Cloud API URL from the environment, or return the default.

#### resolve\_cloud\_workspace\_id

```python
def resolve_cloud_workspace_id(input_value: str | None = None) -> str
```

Get the Airbyte Cloud workspace ID from the environment, or return None if not set.

#### resolve\_cloud\_config\_api\_url

```python
def resolve_cloud_config_api_url(input_value: str | None = None) -> str | None
```

Get the Airbyte Cloud Config API URL from the environment, or return None if not set.

The Config API is a separate internal API used for certain operations like
connector builder projects and custom source definitions.

**Returns**:

  The Config API URL if set via environment variable or input, None otherwise.

