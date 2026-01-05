---
sidebar_label: local_ops
title: airbyte.mcp.local_ops
---

Local MCP operations.

## sys

## traceback

## islice

## Path

## TYPE\_CHECKING

## Annotated

## Any

## Literal

## FastMCP

## BaseModel

## Field

## get\_source

## is\_docker\_installed

## get\_default\_cache

## mcp\_tool

## register\_tools

## resolve\_config

## resolve\_list\_of\_strings

## get\_connector\_metadata

## \_get\_secret\_sources

## DotenvSecretManager

## GoogleGSMSecretManager

## Source

#### \_CONFIG\_HELP

#### \_get\_mcp\_source

```python
def _get_mcp_source(connector_name: str,
                    override_execution_mode: Literal["auto", "docker",
                                                     "python",
                                                     "yaml"] = "auto",
                    *,
                    install_if_missing: bool = True,
                    manifest_path: str | Path | None) -> Source
```

Get the MCP source for a connector.

#### validate\_connector\_config

```python
@mcp_tool(
    domain="local",
    read_only=True,
    idempotent=True,
    extra_help_text=_CONFIG_HELP,
)
def validate_connector_config(connector_name: Annotated[
    str,
    Field(description="The name of the connector to validate."),
], config: Annotated[
    dict | str | None,
    Field(
        description=
        "The configuration for the connector as a dict object or JSON string.",
        default=None,
    ),
], config_file: Annotated[
    str | Path | None,
    Field(
        description=
        "Path to a YAML or JSON file containing the connector configuration.",
        default=None,
    ),
], config_secret_name: Annotated[
    str | None,
    Field(
        description="The name of the secret containing the configuration.",
        default=None,
    ),
], override_execution_mode: Annotated[
    Literal["docker", "python", "yaml", "auto"],
    Field(
        description=
        "Optionally override the execution method to use for the connector. "
        "This parameter is ignored if manifest_path is provided (yaml mode will be used).",
        default="auto",
    ),
], manifest_path: Annotated[
    str | Path | None,
    Field(
        description=
        "Path to a local YAML manifest file for declarative connectors.",
        default=None,
    ),
]) -> tuple[bool, str]
```

Validate a connector configuration.

Returns a tuple of (is_valid: bool, message: str).

#### list\_connector\_config\_secrets

```python
@mcp_tool(
    domain="local",
    read_only=True,
    idempotent=True,
)
def list_connector_config_secrets(
    connector_name: Annotated[
        str,
        Field(description="The name of the connector."),
    ]
) -> list[str]
```

List all `config_secret_name` options that are known for the given connector.

This can be used to find out which already-created config secret names are available
for a given connector. The return value is a list of secret names, but it will not
return the actual secret values.

#### list\_dotenv\_secrets

```python
@mcp_tool(
    domain="local",
    read_only=True,
    idempotent=True,
    extra_help_text=_CONFIG_HELP,
)
def list_dotenv_secrets() -> dict[str, list[str]]
```

List all environment variable names declared within declared .env files.

This returns a dictionary mapping the .env file name to a list of environment
variable names. The values of the environment variables are not returned.

#### list\_source\_streams

```python
@mcp_tool(
    domain="local",
    read_only=True,
    idempotent=True,
    extra_help_text=_CONFIG_HELP,
)
def list_source_streams(source_connector_name: Annotated[
    str,
    Field(description="The name of the source connector."),
], config: Annotated[
    dict | str | None,
    Field(
        description=
        "The configuration for the source connector as a dict or JSON string.",
        default=None,
    ),
], config_file: Annotated[
    str | Path | None,
    Field(
        description=
        "Path to a YAML or JSON file containing the source connector config.",
        default=None,
    ),
], config_secret_name: Annotated[
    str | None,
    Field(
        description="The name of the secret containing the configuration.",
        default=None,
    ),
], override_execution_mode: Annotated[
    Literal["docker", "python", "yaml", "auto"],
    Field(
        description=
        "Optionally override the execution method to use for the connector. "
        "This parameter is ignored if manifest_path is provided (yaml mode will be used).",
        default="auto",
    ),
], manifest_path: Annotated[
    str | Path | None,
    Field(
        description=
        "Path to a local YAML manifest file for declarative connectors.",
        default=None,
    ),
]) -> list[str]
```

List all streams available in a source connector.

This operation (generally) requires a valid configuration, including any required secrets.

#### get\_source\_stream\_json\_schema

```python
@mcp_tool(
    domain="local",
    read_only=True,
    idempotent=True,
    extra_help_text=_CONFIG_HELP,
)
def get_source_stream_json_schema(source_connector_name: Annotated[
    str,
    Field(description="The name of the source connector."),
], stream_name: Annotated[
    str,
    Field(description="The name of the stream."),
], config: Annotated[
    dict | str | None,
    Field(
        description=
        "The configuration for the source connector as a dict or JSON string.",
        default=None,
    ),
], config_file: Annotated[
    str | Path | None,
    Field(
        description=
        "Path to a YAML or JSON file containing the source connector config.",
        default=None,
    ),
], config_secret_name: Annotated[
    str | None,
    Field(
        description="The name of the secret containing the configuration.",
        default=None,
    ),
], override_execution_mode: Annotated[
    Literal["docker", "python", "yaml", "auto"],
    Field(
        description=
        "Optionally override the execution method to use for the connector. "
        "This parameter is ignored if manifest_path is provided (yaml mode will be used).",
        default="auto",
    ),
], manifest_path: Annotated[
    str | Path | None,
    Field(
        description=
        "Path to a local YAML manifest file for declarative connectors.",
        default=None,
    ),
]) -> dict[str, Any]
```

List all properties for a specific stream in a source connector.

#### read\_source\_stream\_records

```python
@mcp_tool(
    domain="local",
    read_only=True,
    extra_help_text=_CONFIG_HELP,
)
def read_source_stream_records(source_connector_name: Annotated[
    str,
    Field(description="The name of the source connector."),
], config: Annotated[
    dict | str | None,
    Field(
        description=
        "The configuration for the source connector as a dict or JSON string.",
        default=None,
    ),
], config_file: Annotated[
    str | Path | None,
    Field(
        description=
        "Path to a YAML or JSON file containing the source connector config.",
        default=None,
    ),
], config_secret_name: Annotated[
    str | None,
    Field(
        description="The name of the secret containing the configuration.",
        default=None,
    ),
], *, stream_name: Annotated[
    str,
    Field(description="The name of the stream to read records from."),
], max_records: Annotated[
    int,
    Field(
        description="The maximum number of records to read.",
        default=1000,
    ),
], override_execution_mode: Annotated[
    Literal["docker", "python", "yaml", "auto"],
    Field(
        description=
        "Optionally override the execution method to use for the connector. "
        "This parameter is ignored if manifest_path is provided (yaml mode will be used).",
        default="auto",
    ),
], manifest_path: Annotated[
    str | Path | None,
    Field(
        description=
        "Path to a local YAML manifest file for declarative connectors.",
        default=None,
    ),
]) -> list[dict[str, Any]] | str
```

Get records from a source connector.

#### get\_stream\_previews

```python
@mcp_tool(
    domain="local",
    read_only=True,
    extra_help_text=_CONFIG_HELP,
)
def get_stream_previews(source_name: Annotated[
    str,
    Field(description="The name of the source connector."),
], config: Annotated[
    dict | str | None,
    Field(
        description=
        "The configuration for the source connector as a dict or JSON string.",
        default=None,
    ),
], config_file: Annotated[
    str | Path | None,
    Field(
        description=
        "Path to a YAML or JSON file containing the source connector config.",
        default=None,
    ),
], config_secret_name: Annotated[
    str | None,
    Field(
        description="The name of the secret containing the configuration.",
        default=None,
    ),
], streams: Annotated[
    list[str] | str | None,
    Field(
        description=("The streams to get previews for. "
                     "Use '*' for all streams, or None for selected streams."),
        default=None,
    ),
], limit: Annotated[
    int,
    Field(
        description=
        "The maximum number of sample records to return per stream.",
        default=10,
    ),
], override_execution_mode: Annotated[
    Literal["docker", "python", "yaml", "auto"],
    Field(
        description=
        "Optionally override the execution method to use for the connector. "
        "This parameter is ignored if manifest_path is provided (yaml mode will be used).",
        default="auto",
    ),
], manifest_path: Annotated[
    str | Path | None,
    Field(
        description=
        "Path to a local YAML manifest file for declarative connectors.",
        default=None,
    ),
]) -> dict[str, list[dict[str, Any]] | str]
```

Get sample records (previews) from streams in a source connector.

This operation requires a valid configuration, including any required secrets.
Returns a dictionary mapping stream names to lists of sample records, or an error
message string if an error occurred for that stream.

#### sync\_source\_to\_cache

```python
@mcp_tool(
    domain="local",
    destructive=False,
    extra_help_text=_CONFIG_HELP,
)
def sync_source_to_cache(source_connector_name: Annotated[
    str,
    Field(description="The name of the source connector."),
], config: Annotated[
    dict | str | None,
    Field(
        description=
        "The configuration for the source connector as a dict or JSON string.",
        default=None,
    ),
], config_file: Annotated[
    str | Path | None,
    Field(
        description=
        "Path to a YAML or JSON file containing the source connector config.",
        default=None,
    ),
], config_secret_name: Annotated[
    str | None,
    Field(
        description="The name of the secret containing the configuration.",
        default=None,
    ),
], streams: Annotated[
    list[str] | str,
    Field(
        description="The streams to sync.",
        default="suggested",
    ),
], override_execution_mode: Annotated[
    Literal["docker", "python", "yaml", "auto"],
    Field(
        description=
        "Optionally override the execution method to use for the connector. "
        "This parameter is ignored if manifest_path is provided (yaml mode will be used).",
        default="auto",
    ),
], manifest_path: Annotated[
    str | Path | None,
    Field(
        description=
        "Path to a local YAML manifest file for declarative connectors.",
        default=None,
    ),
]) -> str
```

Run a sync from a source connector to the default DuckDB cache.

## CachedDatasetInfo Objects

```python
class CachedDatasetInfo(BaseModel)
```

Class to hold information about a cached dataset.

#### stream\_name

The name of the stream in the cache.

#### table\_name

#### schema\_name

#### list\_cached\_streams

```python
@mcp_tool(
    domain="local",
    read_only=True,
    idempotent=True,
    extra_help_text=_CONFIG_HELP,
)
def list_cached_streams() -> list[CachedDatasetInfo]
```

List all streams available in the default DuckDB cache.

#### describe\_default\_cache

```python
@mcp_tool(
    domain="local",
    read_only=True,
    idempotent=True,
    extra_help_text=_CONFIG_HELP,
)
def describe_default_cache() -> dict[str, Any]
```

Describe the currently configured default cache.

#### \_is\_safe\_sql

```python
def _is_safe_sql(sql_query: str) -> bool
```

Check if a SQL query is safe to execute.

For security reasons, we only allow read-only operations like SELECT, DESCRIBE, and SHOW.
Multi-statement queries (containing semicolons) are also disallowed for security.

Note: SQLAlchemy will also validate downstream, but this is a first-pass check.

**Arguments**:

- `sql_query` - The SQL query to check
  

**Returns**:

  True if the query is safe to execute, False otherwise

#### run\_sql\_query

```python
@mcp_tool(
    domain="local",
    read_only=True,
    idempotent=True,
    extra_help_text=_CONFIG_HELP,
)
def run_sql_query(
    sql_query: Annotated[
        str,
        Field(description="The SQL query to execute."),
    ], max_records: Annotated[
        int,
        Field(
            description="Maximum number of records to return.",
            default=1000,
        ),
    ]
) -> list[dict[str, Any]]
```

Run a SQL query against the default cache.

The dialect of SQL should match the dialect of the default cache.
Use `describe_default_cache` to see the cache type.

For DuckDB-type caches:
- Use `SHOW TABLES` to list all tables.
- Use `DESCRIBE <table_name>` to get the schema of a specific table

For security reasons, only read-only operations are allowed: SELECT, DESCRIBE, SHOW, EXPLAIN.

#### register\_local\_ops\_tools

```python
def register_local_ops_tools(app: FastMCP) -> None
```

@private Register tools with the FastMCP app.

This is an internal function and should not be called directly.

