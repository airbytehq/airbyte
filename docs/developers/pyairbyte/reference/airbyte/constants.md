---
sidebar_label: constants
title: airbyte.constants
---

Constants shared across the PyAirbyte codebase.

## annotations

## logging

## os

## Path

#### logger

#### DEBUG\_MODE

Set to True to enable additional debug logging.

#### AB\_EXTRACTED\_AT\_COLUMN

A column that stores the timestamp when the record was extracted.

#### AB\_META\_COLUMN

A column that stores metadata about the record.

#### AB\_RAW\_ID\_COLUMN

A column that stores a unique identifier for each row in the source data.

Note: The interpretation of this column is slightly different from in Airbyte Dv2 destinations.
In Airbyte Dv2 destinations, this column points to a row in a separate &#x27;raw&#x27; table. In PyAirbyte,
this column is simply used as a unique identifier for each record as it is received.

PyAirbyte uses ULIDs for this column, which are identifiers that can be sorted by time
received. This allows us to determine the debug the order of records as they are received, even if
the source provides records that are tied or received out of order from the perspective of their
`emitted_at` (`_airbyte_extracted_at`) timestamps.

#### AB\_INTERNAL\_COLUMNS

A set of internal columns that are reserved for PyAirbyte&#x27;s internal use.

#### \_try\_create\_dir\_if\_missing

```python
def _try_create_dir_if_missing(path: Path, desc: str = "specified") -> Path
```

Try to create a directory if it does not exist.

#### DEFAULT\_PROJECT\_DIR

Default project directory.

Can be overridden by setting the `AIRBYTE_PROJECT_DIR` environment variable.

If not set, defaults to the current working directory.

This serves as the parent directory for both cache and install directories when not explicitly
configured.

If a path is specified that does not yet exist, PyAirbyte will attempt to create it.

#### DEFAULT\_INSTALL\_DIR

Default install directory for connectors.

If not set, defaults to `DEFAULT_PROJECT_DIR` (`AIRBYTE_PROJECT_DIR` env var) or the current
working directory if neither is set.

If a path is specified that does not yet exist, PyAirbyte will attempt to create it.

#### DEFAULT\_CACHE\_ROOT

Default cache root is `.cache` in the current working directory.

The default location can be overridden by setting the `AIRBYTE_CACHE_ROOT` environment variable.

Overriding this can be useful if you always want to store cache files in a specific location.
For example, in ephemeral environments like Google Colab, you might want to store cache files in
your mounted Google Drive by setting this to a path like `/content/drive/MyDrive/Airbyte/cache`.

#### DEFAULT\_CACHE\_SCHEMA\_NAME

The default schema name to use for caches.

Specific caches may override this value with a different schema name.

#### DEFAULT\_GOOGLE\_DRIVE\_MOUNT\_PATH

Default path to mount Google Drive in Google Colab environments.

#### DEFAULT\_ARROW\_MAX\_CHUNK\_SIZE

The default number of records to include in each batch of an Arrow dataset.

#### \_str\_to\_bool

```python
def _str_to_bool(value: str) -> bool
```

Convert a string value of an environment values to a boolean value.

#### TEMP\_DIR\_OVERRIDE

The directory to use for temporary files.

This value is read from the `AIRBYTE_TEMP_DIR` environment variable. If the variable is not set,
Tempfile will use the system&#x27;s default temporary directory.

This can be useful if you want to store temporary files in a specific location (or) when you
need your temporary files to exist in user level directories, and not in system level
directories for permissions reasons.

#### TEMP\_FILE\_CLEANUP

Whether to clean up temporary files after use.

This value is read from the `AIRBYTE_TEMP_FILE_CLEANUP` environment variable. If the variable is
not set, the default value is `True`.

#### AIRBYTE\_OFFLINE\_MODE

Enable or disable offline mode.

When offline mode is enabled, PyAirbyte will attempt to fetch metadata for connectors from the
Airbyte registry but will not raise an error if the registry is unavailable. This can be useful in
environments without internet access or with air-gapped networks.

Offline mode also disables telemetry, similar to a `DO_NOT_TRACK` setting, ensuring no usage data
is sent from your environment. You may also specify a custom registry URL via the`_REGISTRY_ENV_VAR`
environment variable if you prefer to use a different registry source for metadata.

This setting helps you make informed choices about data privacy and operation in restricted and
air-gapped environments.

#### AIRBYTE\_PRINT\_FULL\_ERROR\_LOGS

Whether to print full error logs when an error occurs.
This setting helps in debugging by providing detailed logs when errors occur. This is especially
helpful in ephemeral environments like CI/CD pipelines where log files may not be persisted after
the pipeline run.

If not set, the default value is `False` for non-CI environments.
If running in a CI environment (&quot;CI&quot; env var is set), then the default value is `True`.

#### NO\_UV

Whether to use uv for Python package management.

This value is determined by the `AIRBYTE_NO_UV` environment variable. When `AIRBYTE_NO_UV`
is set to &quot;1&quot;, &quot;true&quot;, or &quot;yes&quot;, uv will be disabled and pip will be used instead.

If the variable is not set or set to any other value, uv will be used by default.
This provides a safe fallback mechanism for environments where uv is not available
or causes issues.

#### SECRETS\_HYDRATION\_PREFIX

Use this prefix to indicate a secret reference in configuration.

For example, this snippet will populate the `personal_access_token` field with the value of the
secret named `GITHUB_PERSONAL_ACCESS_TOKEN`, for instance from an environment variable.

```json
{
  "credentials": {
    "personal_access_token": "secret_reference::GITHUB_PERSONAL_ACCESS_TOKEN"
  }
}
```

For more information, see the `airbyte.secrets` module documentation.

#### CLOUD\_CLIENT\_ID\_ENV\_VAR

The environment variable name for the Airbyte Cloud client ID.

#### CLOUD\_CLIENT\_SECRET\_ENV\_VAR

The environment variable name for the Airbyte Cloud client secret.

#### CLOUD\_API\_ROOT\_ENV\_VAR

The environment variable name for the Airbyte Cloud API URL.

#### CLOUD\_CONFIG\_API\_ROOT\_ENV\_VAR

The environment variable name for the Airbyte Cloud Config API URL.

The Config API is a separate internal API used for certain operations like
connector builder projects and custom source definitions. This environment
variable allows overriding the default Config API URL, which is useful when
the public API URL has been overridden and the Config API cannot be derived
from it automatically.

#### CLOUD\_WORKSPACE\_ID\_ENV\_VAR

The environment variable name for the Airbyte Cloud workspace ID.

#### CLOUD\_BEARER\_TOKEN\_ENV\_VAR

The environment variable name for the Airbyte Cloud bearer token.

When set, this bearer token will be used for authentication instead of
client credentials (client_id + client_secret). This is useful when you
already have a valid bearer token and want to skip the OAuth2 token exchange.

#### CLOUD\_API\_ROOT

The Airbyte Cloud API root URL.

This is the root URL for the Airbyte Cloud API. It is used to interact with the Airbyte Cloud API
and is the default API root for the `CloudWorkspace` class.
- https://reference.airbyte.com/reference/getting-started

#### CLOUD\_CONFIG\_API\_ROOT

Internal-Use API Root, aka Airbyte &quot;Config API&quot;.

Documentation:
- https://docs.airbyte.com/api-documentation#configuration-api-deprecated
- https://github.com/airbytehq/airbyte-platform-internal/blob/master/oss/airbyte-api/server-api/src/main/openapi/config.yaml

#### MCP\_TOOL\_DOMAINS

Valid MCP tool domains available in the server.

- `cloud`: Tools for managing Airbyte Cloud resources (sources, destinations, connections)
- `local`: Tools for local operations (connector validation, caching, SQL queries)
- `registry`: Tools for querying the Airbyte connector registry

#### AIRBYTE\_MCP\_DOMAINS

Enabled MCP tool domains from the `AIRBYTE_MCP_DOMAINS` environment variable.

Accepts a comma-separated list of domain names (e.g., &quot;registry,cloud&quot;).
If set, only tools from these domains will be advertised by the MCP server.
If not set (None), all domains are enabled by default.

Values are case-insensitive and whitespace is trimmed.

#### AIRBYTE\_MCP\_DOMAINS\_DISABLED

Disabled MCP tool domains from the `AIRBYTE_MCP_DOMAINS_DISABLED` environment variable.

Accepts a comma-separated list of domain names (e.g., &quot;registry&quot;).
Tools from these domains will not be advertised by the MCP server.

When both `AIRBYTE_MCP_DOMAINS` and `AIRBYTE_MCP_DOMAINS_DISABLED` are set,
the disabled list takes precedence (subtracts from the enabled list).

Values are case-insensitive and whitespace is trimmed.

