---
sidebar_label: connector_registry
title: airbyte.mcp.connector_registry
---

Airbyte Cloud MCP operations.

## contextlib

## logging

## Annotated

## Any

## Literal

## requests

## FastMCP

## BaseModel

## Field

## exc

## is\_docker\_installed

## mcp\_tool

## register\_tools

## resolve\_list\_of\_strings

## \_DEFAULT\_MANIFEST\_URL

## ApiDocsUrl

## ConnectorMetadata

## ConnectorVersionInfo

## InstallType

## get\_available\_connectors

## get\_connector\_api\_docs\_urls

## get\_connector\_metadata

## \_get\_connector\_version\_history

## get\_source

#### logger

#### list\_connectors

```python
@mcp_tool(
    domain="registry",
    read_only=True,
    idempotent=True,
)
def list_connectors(keyword_filter: Annotated[
    str | None,
    Field(
        description="Filter connectors by keyword.",
        default=None,
    ),
], connector_type_filter: Annotated[
    Literal["source", "destination"] | None,
    Field(
        description="Filter connectors by type ('source' or 'destination').",
        default=None,
    ),
], install_types: Annotated[
    Literal["java", "python", "yaml", "docker"]
    | list[Literal["java", "python", "yaml", "docker"]]
    | None,
    Field(
        description=("""
                Filter connectors by install type.
                These are not mutually exclusive:
                - "python": Connectors that can be installed as Python packages.
                - "yaml": Connectors that can be installed simply via YAML download.
                    These connectors are the fastest to install and run, as they do not require any
                    additional dependencies.
                - "java": Connectors that can only be installed via Java. Since PyAirbyte does not
                    currently ship with a JVM, these connectors will be run via Docker instead.
                    In environments where Docker is not available, these connectors may not be
                    runnable.
                - "docker": Connectors that can be installed via Docker. Note that all connectors
                    can be run in Docker, so this filter should generally return the same results as
                    not specifying a filter.
                If no install types are specified, all connectors will be returned.
                """),
        default=None,
    ),
]) -> list[str]
```

List available Airbyte connectors with optional filtering.

**Returns**:

  List of connector names.

## ConnectorInfo Objects

```python
class ConnectorInfo(BaseModel)
```

@private Class to hold connector information.

#### connector\_name

#### connector\_metadata

#### documentation\_url

#### config\_spec\_jsonschema

#### manifest\_url

#### get\_connector\_info

```python
@mcp_tool(
    domain="registry",
    read_only=True,
    idempotent=True,
)
def get_connector_info(
    connector_name: Annotated[
        str,
        Field(description="The name of the connector to get information for."),
    ]
) -> ConnectorInfo | Literal["Connector not found."]
```

Get the documentation URL for a connector.

#### get\_api\_docs\_urls

```python
@mcp_tool(
    domain="registry",
    read_only=True,
    idempotent=True,
)
def get_api_docs_urls(
    connector_name: Annotated[
        str,
        Field(description=(
            "The canonical connector name "
            "(e.g., 'source-facebook-marketing', 'destination-snowflake')")),
    ]
) -> list[ApiDocsUrl] | Literal["Connector not found."]
```

Get API documentation URLs for a connector.

This tool retrieves documentation URLs for a connector&#x27;s upstream API from multiple sources:
- Registry metadata (documentationUrl, externalDocumentationUrls)
- Connector manifest.yaml file (data.externalDocumentationUrls)

#### get\_connector\_version\_history

```python
@mcp_tool(
    domain="registry",
    read_only=True,
    idempotent=True,
)
def get_connector_version_history(
    connector_name: Annotated[
        str,
        Field(
            description=
            "The name of the connector (e.g., 'source-faker', 'destination-postgres')"
        ),
    ],
    num_versions_to_validate: Annotated[
        int,
        Field(
            description=
            ("Number of most recent versions to validate with registry data for accurate "
             "release dates. Defaults to 5."),
            default=5,
        ),
    ] = 5,
    limit: Annotated[
        int | None,
        Field(
            description=(
                "DEPRECATED: Use num_versions_to_validate instead. "
                "Maximum number of versions to return (most recent first). "
                "If specified, only the first N versions will be returned."),
            default=None,
        ),
    ] = None
) -> list[ConnectorVersionInfo] | Literal["Connector not found.",
                                          "Failed to fetch changelog."]
```

Get version history for a connector.

This tool retrieves the version history for a connector, including:
- Version number
- Release date (from changelog, with registry override for recent versions)
- DockerHub URL for the version
- Changelog URL
- PR URL and title (scraped from changelog)

For the most recent N versions (default 5), release dates are fetched from the
registry for accuracy. For older versions, changelog dates are used.

**Returns**:

  List of version information, sorted by most recent first.

#### register\_connector\_registry\_tools

```python
def register_connector_registry_tools(app: FastMCP) -> None
```

@private Register tools with the FastMCP app.

This is an internal function and should not be called directly.

