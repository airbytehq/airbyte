---
id: airbyte-constants
title: airbyte.constants
---

Module airbyte.constants
========================
Constants shared across the PyAirbyte codebase.

Variables
---------

`AB_EXTRACTED_AT_COLUMN`
:   A column that stores the timestamp when the record was extracted.

`AB_INTERNAL_COLUMNS`
:   A set of internal columns that are reserved for PyAirbyte's internal use.

`AB_META_COLUMN`
:   A column that stores metadata about the record.

`AB_RAW_ID_COLUMN`
:   A column that stores a unique identifier for each row in the source data.
    
    Note: The interpretation of this column is slightly different from in Airbyte Dv2 destinations.
    In Airbyte Dv2 destinations, this column points to a row in a separate 'raw' table. In PyAirbyte,
    this column is simply used as a unique identifier for each record as it is received.
    
    PyAirbyte uses ULIDs for this column, which are identifiers that can be sorted by time
    received. This allows us to determine the debug the order of records as they are received, even if
    the source provides records that are tied or received out of order from the perspective of their
    `emitted_at` (`_airbyte_extracted_at`) timestamps.

`AIRBYTE_MCP_DOMAINS: list[str] | None`
:   Enabled MCP tool domains from the `AIRBYTE_MCP_DOMAINS` environment variable.
    
    Accepts a comma-separated list of domain names (e.g., "registry,cloud").
    If set, only tools from these domains will be advertised by the MCP server.
    If not set (None), all domains are enabled by default.
    
    Values are case-insensitive and whitespace is trimmed.

`AIRBYTE_MCP_DOMAINS_DISABLED: list[str] | None`
:   Disabled MCP tool domains from the `AIRBYTE_MCP_DOMAINS_DISABLED` environment variable.
    
    Accepts a comma-separated list of domain names (e.g., "registry").
    Tools from these domains will not be advertised by the MCP server.
    
    When both `AIRBYTE_MCP_DOMAINS` and `AIRBYTE_MCP_DOMAINS_DISABLED` are set,
    the disabled list takes precedence (subtracts from the enabled list).
    
    Values are case-insensitive and whitespace is trimmed.

`AIRBYTE_OFFLINE_MODE`
:   Enable or disable offline mode.
    
    When offline mode is enabled, PyAirbyte will attempt to fetch metadata for connectors from the
    Airbyte registry but will not raise an error if the registry is unavailable. This can be useful in
    environments without internet access or with air-gapped networks.
    
    Offline mode also disables telemetry, similar to a `DO_NOT_TRACK` setting, ensuring no usage data
    is sent from your environment. You may also specify a custom registry URL via the`_REGISTRY_ENV_VAR`
    environment variable if you prefer to use a different registry source for metadata.
    
    This setting helps you make informed choices about data privacy and operation in restricted and
    air-gapped environments.

`AIRBYTE_PRINT_FULL_ERROR_LOGS: bool`
:   Whether to print full error logs when an error occurs.
    This setting helps in debugging by providing detailed logs when errors occur. This is especially
    helpful in ephemeral environments like CI/CD pipelines where log files may not be persisted after
    the pipeline run.
    
    If not set, the default value is `False` for non-CI environments.
    If running in a CI environment ("CI" env var is set), then the default value is `True`.

`CLOUD_API_ROOT: str`
:   The Airbyte Cloud API root URL.
    
    This is the root URL for the Airbyte Cloud API. It is used to interact with the Airbyte Cloud API
    and is the default API root for the `CloudWorkspace` class.
    - https://reference.airbyte.com/reference/getting-started

`CLOUD_API_ROOT_ENV_VAR: str`
:   The environment variable name for the Airbyte Cloud API URL.

`CLOUD_BEARER_TOKEN_ENV_VAR: str`
:   The environment variable name for the Airbyte Cloud bearer token.
    
    When set, this bearer token will be used for authentication instead of
    client credentials (client_id + client_secret). This is useful when you
    already have a valid bearer token and want to skip the OAuth2 token exchange.

`CLOUD_CLIENT_ID_ENV_VAR: str`
:   The environment variable name for the Airbyte Cloud client ID.

`CLOUD_CLIENT_SECRET_ENV_VAR: str`
:   The environment variable name for the Airbyte Cloud client secret.

`CLOUD_CONFIG_API_ROOT: str`
:   Internal-Use API Root, aka Airbyte "Config API".
    
    Documentation:
    - https://docs.airbyte.com/api-documentation#configuration-api-deprecated
    - https://github.com/airbytehq/airbyte-platform-internal/blob/master/oss/airbyte-api/server-api/src/main/openapi/config.yaml

`CLOUD_CONFIG_API_ROOT_ENV_VAR: str`
:   The environment variable name for the Airbyte Cloud Config API URL.
    
    The Config API is a separate internal API used for certain operations like
    connector builder projects and custom source definitions. This environment
    variable allows overriding the default Config API URL, which is useful when
    the public API URL has been overridden and the Config API cannot be derived
    from it automatically.

`CLOUD_WORKSPACE_ID_ENV_VAR: str`
:   The environment variable name for the Airbyte Cloud workspace ID.

`DEFAULT_ARROW_MAX_CHUNK_SIZE`
:   The default number of records to include in each batch of an Arrow dataset.

`DEFAULT_CACHE_ROOT: pathlib.Path`
:   Default cache root is `.cache` in the current working directory.
    
    The default location can be overridden by setting the `AIRBYTE_CACHE_ROOT` environment variable.
    
    Overriding this can be useful if you always want to store cache files in a specific location.
    For example, in ephemeral environments like Google Colab, you might want to store cache files in
    your mounted Google Drive by setting this to a path like `/content/drive/MyDrive/Airbyte/cache`.

`DEFAULT_CACHE_SCHEMA_NAME`
:   The default schema name to use for caches.
    
    Specific caches may override this value with a different schema name.

`DEFAULT_GOOGLE_DRIVE_MOUNT_PATH`
:   Default path to mount Google Drive in Google Colab environments.

`DEFAULT_INSTALL_DIR: pathlib.Path`
:   Default install directory for connectors.
    
    If not set, defaults to `DEFAULT_PROJECT_DIR` (`AIRBYTE_PROJECT_DIR` env var) or the current
    working directory if neither is set.
    
    If a path is specified that does not yet exist, PyAirbyte will attempt to create it.

`DEFAULT_PROJECT_DIR: pathlib.Path`
:   Default project directory.
    
    Can be overridden by setting the `AIRBYTE_PROJECT_DIR` environment variable.
    
    If not set, defaults to the current working directory.
    
    This serves as the parent directory for both cache and install directories when not explicitly
    configured.
    
    If a path is specified that does not yet exist, PyAirbyte will attempt to create it.

`MCP_TOOL_DOMAINS: list[str]`
:   Valid MCP tool domains available in the server.
    
    - `cloud`: Tools for managing Airbyte Cloud resources (sources, destinations, connections)
    - `local`: Tools for local operations (connector validation, caching, SQL queries)
    - `registry`: Tools for querying the Airbyte connector registry

`NO_UV: bool`
:   Whether to use uv for Python package management.
    
    This value is determined by the `AIRBYTE_NO_UV` environment variable. When `AIRBYTE_NO_UV`
    is set to "1", "true", or "yes", uv will be disabled and pip will be used instead.
    
    If the variable is not set or set to any other value, uv will be used by default.
    This provides a safe fallback mechanism for environments where uv is not available
    or causes issues.

`SECRETS_HYDRATION_PREFIX`
:   Use this prefix to indicate a secret reference in configuration.
    
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

`TEMP_DIR_OVERRIDE: pathlib.Path | None`
:   The directory to use for temporary files.
    
    This value is read from the `AIRBYTE_TEMP_DIR` environment variable. If the variable is not set,
    Tempfile will use the system's default temporary directory.
    
    This can be useful if you want to store temporary files in a specific location (or) when you
    need your temporary files to exist in user level directories, and not in system level
    directories for permissions reasons.

`TEMP_FILE_CLEANUP`
:   Whether to clean up temporary files after use.
    
    This value is read from the `AIRBYTE_TEMP_FILE_CLEANUP` environment variable. If the variable is
    not set, the default value is `True`.