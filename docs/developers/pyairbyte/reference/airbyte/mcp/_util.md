---
sidebar_label: _util
title: airbyte.mcp._util
---

Internal utility functions for MCP.

## annotations

## json

## os

## Path

## Any

## overload

## dotenv

## yaml

## get\_http\_headers

## is\_interactive

## resolve\_cloud\_api\_url

## resolve\_cloud\_bearer\_token

## resolve\_cloud\_client\_id

## resolve\_cloud\_client\_secret

## resolve\_cloud\_workspace\_id

## CloudClientConfig

## DotenvSecretManager

## GoogleGSMSecretManager

## SecretSourceEnum

## register\_secret\_manager

## SecretString

## disable\_secret\_source

## deep\_update

## detect\_hardcoded\_secrets

## get\_secret

## is\_secret\_available

#### AIRBYTE\_MCP\_DOTENV\_PATH\_ENVVAR

#### HEADER\_CLIENT\_ID

#### HEADER\_CLIENT\_SECRET

#### HEADER\_WORKSPACE\_ID

#### HEADER\_API\_URL

#### \_load\_dotenv\_file

```python
def _load_dotenv_file(dotenv_path: Path | str) -> None
```

Load environment variables from a .env file.

#### initialize\_secrets

```python
def initialize_secrets() -> None
```

Initialize dotenv to load environment variables from .env files.

Note: Later secret manager registrations have higher priority than earlier ones.

#### resolve\_list\_of\_strings

```python
@overload
def resolve_list_of_strings(value: None) -> None
```

#### resolve\_list\_of\_strings

```python
@overload
def resolve_list_of_strings(value: str | list[str] | set[str]) -> list[str]
```

#### resolve\_list\_of\_strings

```python
def resolve_list_of_strings(
        value: str | list[str] | set[str] | None) -> list[str] | None
```

Resolve a string or list of strings to a list of strings.

This method will handle three types of input:

1. A list of strings (e.g., [&quot;stream1&quot;, &quot;stream2&quot;]) will be returned as-is.
2. None or empty input will return None.
3. A single CSV string (e.g., &quot;stream1,stream2&quot;) will be split into a list.
4. A JSON string (e.g., &#x27;[&quot;stream1&quot;, &quot;stream2&quot;]&#x27;) will be parsed into a list.
5. If the input is empty or None, an empty list will be returned.

**Arguments**:

- `value` - A string or list of strings.

#### resolve\_config

```python
def resolve_config(
        config: dict | str | None = None,
        config_file: str | Path | None = None,
        config_secret_name: str | None = None,
        config_spec_jsonschema: dict[str, Any] | None = None
) -> dict[str, Any]
```

Resolve a configuration dictionary, JSON string, or file path to a dictionary.

**Returns**:

  Resolved configuration dictionary
  

**Raises**:

- `ValueError` - If no configuration provided or if JSON parsing fails
  
  We reject hardcoded secrets in a config dict if we detect them.

#### \_get\_header\_value

```python
def _get_header_value(headers: dict[str, str], header_name: str) -> str | None
```

Get a header value from a headers dict, case-insensitively.

**Arguments**:

- `headers` - Dictionary of HTTP headers.
- `header_name` - The header name to look for (case-insensitive).
  

**Returns**:

  The header value if found, None otherwise.

#### get\_bearer\_token\_from\_headers

```python
def get_bearer_token_from_headers() -> SecretString | None
```

Extract bearer token from HTTP Authorization header.

This function extracts the bearer token from the standard HTTP
`Authorization: Bearer <token>` header when running as an MCP HTTP server.

**Returns**:

  The bearer token as a SecretString, or None if not found or not in HTTP context.

#### get\_client\_id\_from\_headers

```python
def get_client_id_from_headers() -> SecretString | None
```

Extract client ID from HTTP headers.

**Returns**:

  The client ID as a SecretString, or None if not found.

#### get\_client\_secret\_from\_headers

```python
def get_client_secret_from_headers() -> SecretString | None
```

Extract client secret from HTTP headers.

**Returns**:

  The client secret as a SecretString, or None if not found.

#### get\_workspace\_id\_from\_headers

```python
def get_workspace_id_from_headers() -> str | None
```

Extract workspace ID from HTTP headers.

**Returns**:

  The workspace ID, or None if not found.

#### get\_api\_url\_from\_headers

```python
def get_api_url_from_headers() -> str | None
```

Extract API URL from HTTP headers.

**Returns**:

  The API URL, or None if not found.

#### resolve\_cloud\_credentials

```python
def resolve_cloud_credentials(
        *,
        client_id: SecretString | str | None = None,
        client_secret: SecretString | str | None = None,
        bearer_token: SecretString | str | None = None,
        api_root: str | None = None) -> CloudClientConfig
```

Resolve CloudClientConfig from multiple sources.

This function resolves authentication credentials for Airbyte Cloud
from multiple sources in the following priority order:

1. Explicit parameters passed to this function
2. HTTP headers (when running as MCP HTTP server)
3. Environment variables

For bearer token authentication, the resolution order is:
1. Explicit `bearer_token` parameter
2. HTTP `Authorization: Bearer <token>` header
3. `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable

For client credentials authentication, the resolution order is:
1. Explicit `client_id` and `client_secret` parameters
2. HTTP `X-Airbyte-Cloud-Client-Id` and `X-Airbyte-Cloud-Client-Secret` headers
3. `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET` environment variables

**Arguments**:

- `client_id` - Optional explicit client ID.
- `client_secret` - Optional explicit client secret.
- `bearer_token` - Optional explicit bearer token.
- `Authorization: Bearer <token>`2 - Optional explicit API root URL.
  

**Returns**:

  A CloudClientConfig instance with resolved authentication.
  

**Raises**:

- `Authorization: Bearer <token>`3 - If no valid authentication can be resolved.

#### resolve\_workspace\_id

```python
def resolve_workspace_id(workspace_id: str | None = None) -> str
```

Resolve workspace ID from multiple sources.

Resolution order:
1. Explicit `workspace_id` parameter
2. HTTP `X-Airbyte-Cloud-Workspace-Id` header
3. `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable

**Arguments**:

- `workspace_id` - Optional explicit workspace ID.
  

**Returns**:

  The resolved workspace ID.
  

**Raises**:

- `PyAirbyteSecretNotFoundError` - If no workspace ID can be resolved.

