---
id: airbyte-constants
title: "airbyte.constants Module"
sidebar_label: "airbyte.constants"
---

# `airbyte.constants` Module

Constants shared across the PyAirbyte codebase.

- **`AB_EXTRACTED_AT_COLUMN`**

  A column that stores the timestamp when the record was extracted.

- **`AB_INTERNAL_COLUMNS`**

  A set of internal columns that are reserved for PyAirbyte's internal use.

- **`AB_META_COLUMN`**

  A column that stores metadata about the record.

- **`AB_RAW_ID_COLUMN`**

  A column that stores a unique identifier for each row in the source data.

  Note: The interpretation of this column is slightly different from in Airbyte Dv2 destinations.
  In Airbyte Dv2 destinations, this column points to a row in a separate 'raw' table. In PyAirbyte,
  this column is simply used as a unique identifier for each record as it is received.

  PyAirbyte uses ULIDs for this column, which are identifiers that can be sorted by time
  received. This allows us to determine the debug the order of records as they are received, even if
  the source provides records that are tied or received out of order from the perspective of their
  `emitted_at` (`_airbyte_extracted_at`) timestamps.

- **`AIRBYTE_OFFLINE_MODE`**

  Enable or disable offline mode.

  When offline mode is enabled, PyAirbyte will attempt to fetch metadata for connectors from the
  Airbyte registry but will not raise an error if the registry is unavailable. This can be useful in
  environments without internet access or with air-gapped networks.

  Offline mode also disables telemetry, similar to a `DO_NOT_TRACK` setting, ensuring no usage data
  is sent from your environment. You may also specify a custom registry URL via the`_REGISTRY_ENV_VAR`
  environment variable if you prefer to use a different registry source for metadata.

  This setting helps you make informed choices about data privacy and operation in restricted and
  air-gapped environments.

- **`AIRBYTE_PRINT_FULL_ERROR_LOGS`**&nbsp;(`bool`)

  Whether to print full error logs when an error occurs.
  This setting helps in debugging by providing detailed logs when errors occur. This is especially
  helpful in ephemeral environments like CI/CD pipelines where log files may not be persisted after
  the pipeline run.

  If not set, the default value is `False` for non-CI environments.
  If running in a CI environment ("CI" env var is set), then the default value is `True`.

- **`CLOUD_API_ROOT`**&nbsp;(`str`)

  The Airbyte Cloud API root URL.

  This is the root URL for the Airbyte Cloud API. It is used to interact with the Airbyte Cloud API
  and is the default API root for the `CloudWorkspace` class.
  - https://reference.airbyte.com/reference/getting-started

- **`CLOUD_API_ROOT_ENV_VAR`**&nbsp;(`str`)

  The environment variable name for the Airbyte Cloud API URL.

- **`CLOUD_BEARER_TOKEN_ENV_VAR`**&nbsp;(`str`)

  The environment variable name for the Airbyte Cloud bearer token.

  When set, this bearer token will be used for authentication instead of
  client credentials (client_id + client_secret). This is useful when you
  already have a valid bearer token and want to skip the OAuth2 token exchange.

- **`CLOUD_CLIENT_ID_ENV_VAR`**&nbsp;(`str`)

  The environment variable name for the Airbyte Cloud client ID.

- **`CLOUD_CLIENT_SECRET_ENV_VAR`**&nbsp;(`str`)

  The environment variable name for the Airbyte Cloud client secret.

- **`CLOUD_CONFIG_API_ROOT`**&nbsp;(`str`)

  Internal-Use API Root, aka Airbyte "Config API".

  Documentation:
  - https://docs.airbyte.com/api-documentation#configuration-api-deprecated
  - https://github.com/airbytehq/airbyte-platform-internal/blob/master/oss/airbyte-api/server-api/src/main/openapi/config.yaml

- **`CLOUD_CONFIG_API_ROOT_ENV_VAR`**&nbsp;(`str`)

  The environment variable name for the Airbyte Cloud Config API URL.

  The Config API is a separate internal API used for certain operations like
  connector builder projects and custom source definitions. This environment
  variable allows overriding the default Config API URL, which is useful when
  the public API URL has been overridden and the Config API cannot be derived
  from it automatically.

- **`CLOUD_ORGANIZATION_ID_ENV_VAR`**&nbsp;(`str`)

  The environment variable name for the Airbyte Cloud organization ID.

- **`CLOUD_WORKSPACE_ID_ENV_VAR`**&nbsp;(`str`)

  The environment variable name for the Airbyte Cloud workspace ID.

- **`DEFAULT_ARROW_MAX_CHUNK_SIZE`**

  The default number of records to include in each batch of an Arrow dataset.

- **`DEFAULT_CACHE_ROOT`**&nbsp;(`pathlib.Path`)

  Default cache root is `.cache` in the current working directory.

  The default location can be overridden by setting the `AIRBYTE_CACHE_ROOT` environment variable.

  Overriding this can be useful if you always want to store cache files in a specific location.
  For example, in ephemeral environments like Google Colab, you might want to store cache files in
  your mounted Google Drive by setting this to a path like `/content/drive/MyDrive/Airbyte/cache`.

- **`DEFAULT_CACHE_SCHEMA_NAME`**

  The default schema name to use for caches.

  Specific caches may override this value with a different schema name.

- **`DEFAULT_GOOGLE_DRIVE_MOUNT_PATH`**

  Default path to mount Google Drive in Google Colab environments.

- **`DEFAULT_INSTALL_DIR`**&nbsp;(`pathlib.Path`)

  Default install directory for connectors.

  If not set, defaults to `DEFAULT_PROJECT_DIR` (`AIRBYTE_PROJECT_DIR` env var) or the current
  working directory if neither is set.

  If a path is specified that does not yet exist, PyAirbyte will attempt to create it.

- **`DEFAULT_PROJECT_DIR`**&nbsp;(`pathlib.Path`)

  Default project directory.

  Can be overridden by setting the `AIRBYTE_PROJECT_DIR` environment variable.

  If not set, defaults to the current working directory.

  This serves as the parent directory for both cache and install directories when not explicitly
  configured.

  If a path is specified that does not yet exist, PyAirbyte will attempt to create it.

- **`MCP_BEARER_TOKEN_HEADER`**&nbsp;(`str`)

  HTTP header key for bearer token (standard Authorization header).

- **`MCP_CONFIG_API_URL`**&nbsp;(`str`)

  Config arg name for the API URL setting.

- **`MCP_CONFIG_BEARER_TOKEN`**&nbsp;(`str`)

  Config arg name for the bearer token setting.

- **`MCP_CONFIG_CLIENT_ID`**&nbsp;(`str`)

  Config arg name for the client ID setting.

- **`MCP_CONFIG_CLIENT_SECRET`**&nbsp;(`str`)

  Config arg name for the client secret setting.

- **`MCP_CONFIG_CONFIG_API_URL`**&nbsp;(`str`)

  Config arg name for the Config API URL setting.

- **`MCP_CONFIG_EXCLUDE_MODULES`**&nbsp;(`str`)

  Config arg name for the legacy AIRBYTE_MCP_DOMAINS_DISABLED setting.

- **`MCP_CONFIG_INCLUDE_MODULES`**&nbsp;(`str`)

  Config arg name for the legacy AIRBYTE_MCP_DOMAINS setting.

- **`MCP_CONFIG_READONLY_MODE`**&nbsp;(`str`)

  Config arg name for the legacy AIRBYTE_CLOUD_MCP_READONLY_MODE setting.

- **`MCP_CONFIG_WORKSPACE_ID`**&nbsp;(`str`)

  Config arg name for the workspace ID setting.

- **`MCP_DOMAINS_DISABLED_ENV_VAR`**&nbsp;(`str`)

  Environment variable to disable specific MCP tool domains.

  Accepts a comma-separated list of domain names (e.g., "local,registry").
  Tools from these domains will not be advertised by the MCP server.

- **`MCP_DOMAINS_ENV_VAR`**&nbsp;(`str`)

  Environment variable to enable specific MCP tool domains.

  Accepts a comma-separated list of domain names (e.g., "cloud,registry").
  If set, only tools from these domains will be advertised by the MCP server.

- **`MCP_EXTENSIONS_HEADER`**&nbsp;(`str`)

  HTTP header key for client-declared MCP extension IDs.

- **`MCP_READONLY_MODE_ENV_VAR`**&nbsp;(`str`)

  Environment variable to enable read-only mode for the MCP server.

  When set to "1" or "true", only tools with readOnlyHint=True will be available.

- **`MCP_TRUSTED_EXECUTION_ENV_VAR`**&nbsp;(`str`)

  Environment variable that enables trusted (local) execution for the MCP server.

  When set to `1`/`true`/`yes`, the server may use its trusted-machine capabilities: local
  filesystem access, local connector installation/execution, and server-side secret
  resolution. It defaults to *off* on every transport and is permanently unavailable over
  the HTTP transport (a hosted deployment can never enable it). This gate is server-owned
  and is deliberately never read from a request header, because it *widens* the surface and
  so must never be caller-controllable.

- **`MCP_WORKSPACE_ID_HEADER`**&nbsp;(`str`)

  HTTP header key for passing workspace ID to the MCP server.

  This allows per-request workspace ID configuration when using HTTP transport.

- **`NO_UV`**&nbsp;(`bool`)

  Whether to disable uv and use pip for Python package management.

  This value is determined by the `AIRBYTE_NO_UV` environment variable. When `AIRBYTE_NO_UV`
  is set to "1", "true", or "yes", pip will be used instead of uv.

  If the variable is not set or set to any other value, uv will be used by default. Set this
  variable to opt out of uv and use pip instead.

- **`SECRETS_HYDRATION_PREFIX`**

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

- **`TEMP_DIR_OVERRIDE`**&nbsp;(`pathlib.Path | None`)

  The directory to use for temporary files.

  This value is read from the `AIRBYTE_TEMP_DIR` environment variable. If the variable is not set,
  Tempfile will use the system's default temporary directory.

  This can be useful if you want to store temporary files in a specific location (or) when you
  need your temporary files to exist in user level directories, and not in system level
  directories for permissions reasons.

- **`TEMP_FILE_CLEANUP`**

  Whether to clean up temporary files after use.

  This value is read from the `AIRBYTE_TEMP_FILE_CLEANUP` environment variable. If the variable is
  not set, the default value is `True`.

### `is_hosted_mcp_mode` {#airbyte.constants.is_hosted_mcp_mode}

<ApiMember kind="function">

<ApiSignature>

```python
def is_hosted_mcp_mode() -> bool
```

</ApiSignature>

Return True if the process serves MCP over hosted HTTP transport.

</ApiMember>

### `set_hosted_mcp_mode` {#airbyte.constants.set_hosted_mcp_mode}

<ApiMember kind="function">

<ApiSignature>

```python
def set_hosted_mcp_mode() -> None
```

</ApiSignature>

Set the flag indicating the process serves MCP over hosted HTTP transport.

</ApiMember>