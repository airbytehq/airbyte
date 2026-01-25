---
id: airbyte-mcp-connector_registry
title: airbyte.mcp.connector_registry
---

Module airbyte.mcp.connector_registry
=====================================
Airbyte Cloud MCP operations.

Functions
---------

`get_api_docs_urls(connector_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description="The canonical connector name (e.g., 'source-facebook-marketing', 'destination-snowflake')")]) ‑> list[airbyte.registry.ApiDocsUrl] | Literal['Connector not found.']`
:   Get API documentation URLs for a connector.
    
    This tool retrieves documentation URLs for a connector's upstream API from multiple sources:
    - Registry metadata (documentationUrl, externalDocumentationUrls)
    - Connector manifest.yaml file (data.externalDocumentationUrls)

`get_connector_info(connector_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The name of the connector to get information for.')]) ‑> airbyte.mcp.connector_registry.ConnectorInfo | Literal['Connector not found.']`
:   Get the documentation URL for a connector.

`get_connector_version_history(connector_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description="The name of the connector (e.g., 'source-faker', 'destination-postgres')")], num_versions_to_validate: Annotated[int, FieldInfo(annotation=NoneType, required=False, default=5, description='Number of most recent versions to validate with registry data for accurate release dates. Defaults to 5.')] = 5, limit: Annotated[int | None, FieldInfo(annotation=NoneType, required=False, default=None, description='DEPRECATED: Use num_versions_to_validate instead. Maximum number of versions to return (most recent first). If specified, only the first N versions will be returned.')] = None) ‑> list[airbyte.registry.ConnectorVersionInfo] | Literal['Connector not found.', 'Failed to fetch changelog.']`
:   Get version history for a connector.
    
    This tool retrieves the version history for a connector, including:
    - Version number
    - Release date (from changelog, with registry override for recent versions)
    - DockerHub URL for the version
    - Changelog URL
    - PR URL and title (scraped from changelog)
    
    For the most recent N versions (default 5), release dates are fetched from the
    registry for accuracy. For older versions, changelog dates are used.
    
    Returns:
        List of version information, sorted by most recent first.

`list_connectors(keyword_filter: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Filter connectors by keyword.')], connector_type_filter: Annotated[Literal['source', 'destination'] | None, FieldInfo(annotation=NoneType, required=False, default=None, description="Filter connectors by type ('source' or 'destination').")], install_types: Annotated[Literal['java', 'python', 'yaml', 'docker'] | list[Literal['java', 'python', 'yaml', 'docker']] | None, FieldInfo(annotation=NoneType, required=False, default=None, description='\n                Filter connectors by install type.\n                These are not mutually exclusive:\n                - "python": Connectors that can be installed as Python packages.\n                - "yaml": Connectors that can be installed simply via YAML download.\n                    These connectors are the fastest to install and run, as they do not require any\n                    additional dependencies.\n                - "java": Connectors that can only be installed via Java. Since PyAirbyte does not\n                    currently ship with a JVM, these connectors will be run via Docker instead.\n                    In environments where Docker is not available, these connectors may not be\n                    runnable.\n                - "docker": Connectors that can be installed via Docker. Note that all connectors\n                    can be run in Docker, so this filter should generally return the same results as\n                    not specifying a filter.\n                If no install types are specified, all connectors will be returned.\n                ')]) ‑> list[str]`
:   List available Airbyte connectors with optional filtering.
    
    Returns:
        List of connector names.

`register_connector_registry_tools(app: fastmcp.server.server.FastMCP) ‑> None`
:   @private Register tools with the FastMCP app.
    
    This is an internal function and should not be called directly.

Classes
-------

`ConnectorInfo(**data: Any)`
:   @private Class to hold connector information.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `config_spec_jsonschema: dict | None`
    :

    `connector_metadata: airbyte.registry.ConnectorMetadata | None`
    :

    `connector_name: str`
    :

    `documentation_url: str | None`
    :

    `manifest_url: str | None`
    :

    `model_config`
    :