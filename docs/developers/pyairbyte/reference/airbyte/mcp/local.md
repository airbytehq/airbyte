---
id: airbyte-mcp-local
title: airbyte.mcp.local
---

Module airbyte.mcp.local
========================
Local MCP operations.

Functions
---------

`describe_default_cache() ‑> dict[str, typing.Any]`
:   Describe the currently configured default cache.
    
    
    You can provide `config` as JSON or a Path to a YAML/JSON file.
    If a `dict` is provided, it must not contain hardcoded secrets.
    Instead, secrets should be provided using environment variables,
    and the config should reference them using the format
    `secret_reference::ENV_VAR_NAME`.
    
    You can also provide a `config_secret_name` to use a specific
    secret name for the configuration. This is useful if you want to
    validate a configuration that is stored in a secrets manager.
    
    If `config_secret_name` is provided, it should point to a string
    that contains valid JSON or YAML.
    
    If both `config` and `config_secret_name` are provided, the
    `config` will be loaded first and then the referenced secret config
    will be layered on top of the non-secret config.
    
    For declarative connectors, you can provide a `manifest_path` to
    specify a local YAML manifest file instead of using the registry
    version. This is useful for testing custom or locally-developed
    connector manifests.

`get_source_stream_json_schema(source_connector_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The name of the source connector.')], stream_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The name of the stream.')], config: Annotated[dict | str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The configuration for the source connector as a dict or JSON string.')], config_file: Annotated[str | pathlib.Path | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Path to a YAML or JSON file containing the source connector config.')], config_secret_name: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The name of the secret containing the configuration.')], override_execution_mode: Annotated[Literal['docker', 'python', 'yaml', 'auto'], FieldInfo(annotation=NoneType, required=False, default='auto', description='Optionally override the execution method to use for the connector. This parameter is ignored if manifest_path is provided (yaml mode will be used).')], manifest_path: Annotated[str | pathlib.Path | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Path to a local YAML manifest file for declarative connectors.')]) ‑> dict[str, typing.Any]`
:   List all properties for a specific stream in a source connector.
    
    
    You can provide `config` as JSON or a Path to a YAML/JSON file.
    If a `dict` is provided, it must not contain hardcoded secrets.
    Instead, secrets should be provided using environment variables,
    and the config should reference them using the format
    `secret_reference::ENV_VAR_NAME`.
    
    You can also provide a `config_secret_name` to use a specific
    secret name for the configuration. This is useful if you want to
    validate a configuration that is stored in a secrets manager.
    
    If `config_secret_name` is provided, it should point to a string
    that contains valid JSON or YAML.
    
    If both `config` and `config_secret_name` are provided, the
    `config` will be loaded first and then the referenced secret config
    will be layered on top of the non-secret config.
    
    For declarative connectors, you can provide a `manifest_path` to
    specify a local YAML manifest file instead of using the registry
    version. This is useful for testing custom or locally-developed
    connector manifests.

`get_stream_previews(source_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The name of the source connector.')], config: Annotated[dict | str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The configuration for the source connector as a dict or JSON string.')], config_file: Annotated[str | pathlib.Path | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Path to a YAML or JSON file containing the source connector config.')], config_secret_name: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The name of the secret containing the configuration.')], streams: Annotated[list[str] | str | None, FieldInfo(annotation=NoneType, required=False, default=None, description="The streams to get previews for. Use '*' for all streams, or None for selected streams.")], limit: Annotated[int, FieldInfo(annotation=NoneType, required=False, default=10, description='The maximum number of sample records to return per stream.')], override_execution_mode: Annotated[Literal['docker', 'python', 'yaml', 'auto'], FieldInfo(annotation=NoneType, required=False, default='auto', description='Optionally override the execution method to use for the connector. This parameter is ignored if manifest_path is provided (yaml mode will be used).')], manifest_path: Annotated[str | pathlib.Path | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Path to a local YAML manifest file for declarative connectors.')]) ‑> dict[str, list[dict[str, typing.Any]] | str]`
:   Get sample records (previews) from streams in a source connector.
    
        This operation requires a valid configuration, including any required secrets.
        Returns a dictionary mapping stream names to lists of sample records, or an error
        message string if an error occurred for that stream.
        
    
    
    You can provide `config` as JSON or a Path to a YAML/JSON file.
    If a `dict` is provided, it must not contain hardcoded secrets.
    Instead, secrets should be provided using environment variables,
    and the config should reference them using the format
    `secret_reference::ENV_VAR_NAME`.
    
    You can also provide a `config_secret_name` to use a specific
    secret name for the configuration. This is useful if you want to
    validate a configuration that is stored in a secrets manager.
    
    If `config_secret_name` is provided, it should point to a string
    that contains valid JSON or YAML.
    
    If both `config` and `config_secret_name` are provided, the
    `config` will be loaded first and then the referenced secret config
    will be layered on top of the non-secret config.
    
    For declarative connectors, you can provide a `manifest_path` to
    specify a local YAML manifest file instead of using the registry
    version. This is useful for testing custom or locally-developed
    connector manifests.

`list_cached_streams() ‑> list[airbyte.mcp.local.CachedDatasetInfo]`
:   List all streams available in the default DuckDB cache.
    
    
    You can provide `config` as JSON or a Path to a YAML/JSON file.
    If a `dict` is provided, it must not contain hardcoded secrets.
    Instead, secrets should be provided using environment variables,
    and the config should reference them using the format
    `secret_reference::ENV_VAR_NAME`.
    
    You can also provide a `config_secret_name` to use a specific
    secret name for the configuration. This is useful if you want to
    validate a configuration that is stored in a secrets manager.
    
    If `config_secret_name` is provided, it should point to a string
    that contains valid JSON or YAML.
    
    If both `config` and `config_secret_name` are provided, the
    `config` will be loaded first and then the referenced secret config
    will be layered on top of the non-secret config.
    
    For declarative connectors, you can provide a `manifest_path` to
    specify a local YAML manifest file instead of using the registry
    version. This is useful for testing custom or locally-developed
    connector manifests.

`list_connector_config_secrets(connector_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The name of the connector.')]) ‑> list[str]`
:   List all `config_secret_name` options that are known for the given connector.
    
    This can be used to find out which already-created config secret names are available
    for a given connector. The return value is a list of secret names, but it will not
    return the actual secret values.

`list_dotenv_secrets() ‑> dict[str, list[str]]`
:   List all environment variable names declared within declared .env files.
    
        This returns a dictionary mapping the .env file name to a list of environment
        variable names. The values of the environment variables are not returned.
        
    
    
    You can provide `config` as JSON or a Path to a YAML/JSON file.
    If a `dict` is provided, it must not contain hardcoded secrets.
    Instead, secrets should be provided using environment variables,
    and the config should reference them using the format
    `secret_reference::ENV_VAR_NAME`.
    
    You can also provide a `config_secret_name` to use a specific
    secret name for the configuration. This is useful if you want to
    validate a configuration that is stored in a secrets manager.
    
    If `config_secret_name` is provided, it should point to a string
    that contains valid JSON or YAML.
    
    If both `config` and `config_secret_name` are provided, the
    `config` will be loaded first and then the referenced secret config
    will be layered on top of the non-secret config.
    
    For declarative connectors, you can provide a `manifest_path` to
    specify a local YAML manifest file instead of using the registry
    version. This is useful for testing custom or locally-developed
    connector manifests.

`list_source_streams(source_connector_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The name of the source connector.')], config: Annotated[dict | str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The configuration for the source connector as a dict or JSON string.')], config_file: Annotated[str | pathlib.Path | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Path to a YAML or JSON file containing the source connector config.')], config_secret_name: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The name of the secret containing the configuration.')], override_execution_mode: Annotated[Literal['docker', 'python', 'yaml', 'auto'], FieldInfo(annotation=NoneType, required=False, default='auto', description='Optionally override the execution method to use for the connector. This parameter is ignored if manifest_path is provided (yaml mode will be used).')], manifest_path: Annotated[str | pathlib.Path | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Path to a local YAML manifest file for declarative connectors.')]) ‑> list[str]`
:   List all streams available in a source connector.
    
        This operation (generally) requires a valid configuration, including any required secrets.
        
    
    
    You can provide `config` as JSON or a Path to a YAML/JSON file.
    If a `dict` is provided, it must not contain hardcoded secrets.
    Instead, secrets should be provided using environment variables,
    and the config should reference them using the format
    `secret_reference::ENV_VAR_NAME`.
    
    You can also provide a `config_secret_name` to use a specific
    secret name for the configuration. This is useful if you want to
    validate a configuration that is stored in a secrets manager.
    
    If `config_secret_name` is provided, it should point to a string
    that contains valid JSON or YAML.
    
    If both `config` and `config_secret_name` are provided, the
    `config` will be loaded first and then the referenced secret config
    will be layered on top of the non-secret config.
    
    For declarative connectors, you can provide a `manifest_path` to
    specify a local YAML manifest file instead of using the registry
    version. This is useful for testing custom or locally-developed
    connector manifests.

`read_source_stream_records(source_connector_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The name of the source connector.')], config: Annotated[dict | str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The configuration for the source connector as a dict or JSON string.')], config_file: Annotated[str | pathlib.Path | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Path to a YAML or JSON file containing the source connector config.')], config_secret_name: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The name of the secret containing the configuration.')], *, stream_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The name of the stream to read records from.')], max_records: Annotated[int, FieldInfo(annotation=NoneType, required=False, default=1000, description='The maximum number of records to read.')], override_execution_mode: Annotated[Literal['docker', 'python', 'yaml', 'auto'], FieldInfo(annotation=NoneType, required=False, default='auto', description='Optionally override the execution method to use for the connector. This parameter is ignored if manifest_path is provided (yaml mode will be used).')], manifest_path: Annotated[str | pathlib.Path | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Path to a local YAML manifest file for declarative connectors.')]) ‑> list[dict[str, typing.Any]] | str`
:   Get records from a source connector.
    
    
    You can provide `config` as JSON or a Path to a YAML/JSON file.
    If a `dict` is provided, it must not contain hardcoded secrets.
    Instead, secrets should be provided using environment variables,
    and the config should reference them using the format
    `secret_reference::ENV_VAR_NAME`.
    
    You can also provide a `config_secret_name` to use a specific
    secret name for the configuration. This is useful if you want to
    validate a configuration that is stored in a secrets manager.
    
    If `config_secret_name` is provided, it should point to a string
    that contains valid JSON or YAML.
    
    If both `config` and `config_secret_name` are provided, the
    `config` will be loaded first and then the referenced secret config
    will be layered on top of the non-secret config.
    
    For declarative connectors, you can provide a `manifest_path` to
    specify a local YAML manifest file instead of using the registry
    version. This is useful for testing custom or locally-developed
    connector manifests.

`register_local_tools(app: fastmcp.server.server.FastMCP) ‑> None`
:   Register local tools with the FastMCP app.
    
    Args:
        app: FastMCP application instance

`run_sql_query(sql_query: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The SQL query to execute.')], max_records: Annotated[int, FieldInfo(annotation=NoneType, required=False, default=1000, description='Maximum number of records to return.')]) ‑> list[dict[str, typing.Any]]`
:   Run a SQL query against the default cache.
    
        The dialect of SQL should match the dialect of the default cache.
        Use `describe_default_cache` to see the cache type.
    
        For DuckDB-type caches:
        - Use `SHOW TABLES` to list all tables.
        - Use `DESCRIBE <table_name>` to get the schema of a specific table
    
        For security reasons, only read-only operations are allowed: SELECT, DESCRIBE, SHOW, EXPLAIN.
        
    
    
    You can provide `config` as JSON or a Path to a YAML/JSON file.
    If a `dict` is provided, it must not contain hardcoded secrets.
    Instead, secrets should be provided using environment variables,
    and the config should reference them using the format
    `secret_reference::ENV_VAR_NAME`.
    
    You can also provide a `config_secret_name` to use a specific
    secret name for the configuration. This is useful if you want to
    validate a configuration that is stored in a secrets manager.
    
    If `config_secret_name` is provided, it should point to a string
    that contains valid JSON or YAML.
    
    If both `config` and `config_secret_name` are provided, the
    `config` will be loaded first and then the referenced secret config
    will be layered on top of the non-secret config.
    
    For declarative connectors, you can provide a `manifest_path` to
    specify a local YAML manifest file instead of using the registry
    version. This is useful for testing custom or locally-developed
    connector manifests.

`sync_source_to_cache(source_connector_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The name of the source connector.')], config: Annotated[dict | str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The configuration for the source connector as a dict or JSON string.')], config_file: Annotated[str | pathlib.Path | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Path to a YAML or JSON file containing the source connector config.')], config_secret_name: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The name of the secret containing the configuration.')], streams: Annotated[list[str] | str, FieldInfo(annotation=NoneType, required=False, default='suggested', description='The streams to sync.')], override_execution_mode: Annotated[Literal['docker', 'python', 'yaml', 'auto'], FieldInfo(annotation=NoneType, required=False, default='auto', description='Optionally override the execution method to use for the connector. This parameter is ignored if manifest_path is provided (yaml mode will be used).')], manifest_path: Annotated[str | pathlib.Path | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Path to a local YAML manifest file for declarative connectors.')]) ‑> str`
:   Run a sync from a source connector to the default DuckDB cache.
    
    
    You can provide `config` as JSON or a Path to a YAML/JSON file.
    If a `dict` is provided, it must not contain hardcoded secrets.
    Instead, secrets should be provided using environment variables,
    and the config should reference them using the format
    `secret_reference::ENV_VAR_NAME`.
    
    You can also provide a `config_secret_name` to use a specific
    secret name for the configuration. This is useful if you want to
    validate a configuration that is stored in a secrets manager.
    
    If `config_secret_name` is provided, it should point to a string
    that contains valid JSON or YAML.
    
    If both `config` and `config_secret_name` are provided, the
    `config` will be loaded first and then the referenced secret config
    will be layered on top of the non-secret config.
    
    For declarative connectors, you can provide a `manifest_path` to
    specify a local YAML manifest file instead of using the registry
    version. This is useful for testing custom or locally-developed
    connector manifests.

`validate_connector_config(connector_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The name of the connector to validate.')], config: Annotated[dict | str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The configuration for the connector as a dict object or JSON string.')], config_file: Annotated[str | pathlib.Path | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Path to a YAML or JSON file containing the connector configuration.')], config_secret_name: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The name of the secret containing the configuration.')], override_execution_mode: Annotated[Literal['docker', 'python', 'yaml', 'auto'], FieldInfo(annotation=NoneType, required=False, default='auto', description='Optionally override the execution method to use for the connector. This parameter is ignored if manifest_path is provided (yaml mode will be used).')], manifest_path: Annotated[str | pathlib.Path | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Path to a local YAML manifest file for declarative connectors.')]) ‑> tuple[bool, str]`
:   Validate a connector configuration.
    
        Returns a tuple of (is_valid: bool, message: str).
        
    
    
    You can provide `config` as JSON or a Path to a YAML/JSON file.
    If a `dict` is provided, it must not contain hardcoded secrets.
    Instead, secrets should be provided using environment variables,
    and the config should reference them using the format
    `secret_reference::ENV_VAR_NAME`.
    
    You can also provide a `config_secret_name` to use a specific
    secret name for the configuration. This is useful if you want to
    validate a configuration that is stored in a secrets manager.
    
    If `config_secret_name` is provided, it should point to a string
    that contains valid JSON or YAML.
    
    If both `config` and `config_secret_name` are provided, the
    `config` will be loaded first and then the referenced secret config
    will be layered on top of the non-secret config.
    
    For declarative connectors, you can provide a `manifest_path` to
    specify a local YAML manifest file instead of using the registry
    version. This is useful for testing custom or locally-developed
    connector manifests.

Classes
-------

`CachedDatasetInfo(**data: Any)`
:   Class to hold information about a cached dataset.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

    `schema_name: str | None`
    :

    `stream_name: str`
    :   The name of the stream in the cache.

    `table_name: str`
    :