---
sidebar_label: registry
title: airbyte.registry
---

Connectivity to the connector catalog registry.

## annotations

## json

## logging

## os

## warnings

## copy

## Enum

## Path

## Any

## cast

## requests

## yaml

## BaseModel

## Field

## Self

## exc

## fetch\_registry\_version\_date

## parse\_changelog\_html

## is\_docker\_installed

## AIRBYTE\_OFFLINE\_MODE

## warn\_once

## get\_version

#### logger

#### \_\_cache

#### \_REGISTRY\_ENV\_VAR

#### \_REGISTRY\_URL

#### \_PYTHON\_LANGUAGE

#### \_MANIFEST\_ONLY\_LANGUAGE

#### \_PYTHON\_LANGUAGE\_TAG

#### \_MANIFEST\_ONLY\_TAG

#### \_DEFAULT\_MANIFEST\_URL

## InstallType Objects

```python
class InstallType(str, Enum)
```

The type of installation for a connector.

#### YAML

Manifest-only connectors that can be run without Docker.

#### PYTHON

Python-based connectors available via PyPI.

#### DOCKER

Docker-based connectors (returns all connectors for backward compatibility).

#### JAVA

Java-based connectors.

#### INSTALLABLE

Connectors installable in the current environment (environment-sensitive).

Returns all connectors if Docker is installed, otherwise only Python and YAML.

#### ANY

All connectors in the registry (environment-independent).

## Language Objects

```python
class Language(str, Enum)
```

The language of a connector.

#### PYTHON

#### JAVA

#### MANIFEST\_ONLY

## ConnectorMetadata Objects

```python
class ConnectorMetadata(BaseModel)
```

Metadata for a connector.

#### name

Connector name. For example, &quot;source-google-sheets&quot;.

#### latest\_available\_version

The latest available version of the connector.

#### pypi\_package\_name

The name of the PyPI package for the connector, if it exists.

#### language

The language of the connector.

#### install\_types

The supported install types for the connector.

#### suggested\_streams

A list of suggested streams for the connector, if available.

#### default\_install\_type

```python
@property
def default_install_type() -> InstallType
```

Return the default install type for the connector.

#### \_get\_registry\_url

```python
def _get_registry_url() -> str
```

#### \_is\_registry\_disabled

```python
def _is_registry_disabled(url: str) -> bool
```

#### \_registry\_entry\_to\_connector\_metadata

```python
def _registry_entry_to_connector_metadata(entry: dict) -> ConnectorMetadata
```

#### \_get\_registry\_cache

```python
def _get_registry_cache(*,
                        force_refresh: bool = False
                        ) -> dict[str, ConnectorMetadata]
```

Return the registry cache.

Result is a mapping of connector name to ConnectorMetadata.

#### get\_connector\_metadata

```python
def get_connector_metadata(name: str) -> ConnectorMetadata | None
```

Check the cache for the connector.

If the cache is empty, populate by calling update_cache.

#### get\_available\_connectors

```python
def get_available_connectors(
    install_type: InstallType | str | None = InstallType.INSTALLABLE
) -> list[str]
```

Return a list of all available connectors.

Connectors will be returned in alphabetical order, with the standard prefix &quot;source-&quot;.

**Arguments**:

- `install_type` - The type of installation for the connector.
  Defaults to `InstallType.INSTALLABLE`.

## ConnectorVersionInfo Objects

```python
class ConnectorVersionInfo(BaseModel)
```

Information about a specific connector version.

#### version

#### release\_date

#### docker\_image\_url

#### changelog\_url

#### pr\_url

#### pr\_title

#### parsing\_errors

## ApiDocsUrl Objects

```python
class ApiDocsUrl(BaseModel)
```

API documentation URL information.

#### title

#### url

#### source

#### doc\_type

#### requires\_login

#### model\_config

#### from\_manifest\_dict

```python
@classmethod
def from_manifest_dict(cls, manifest_data: dict[str, Any]) -> list[Self]
```

Extract documentation URLs from parsed manifest data.

**Arguments**:

- `manifest_data` - The parsed manifest.yaml data as a dictionary
  

**Returns**:

  List of ApiDocsUrl objects extracted from the manifest

#### \_manifest\_url\_for

```python
def _manifest_url_for(connector_name: str) -> str
```

Get the expected URL of the manifest.yaml file for a connector.

**Arguments**:

- `connector_name` - The canonical connector name (e.g., &quot;source-facebook-marketing&quot;)
  

**Returns**:

  The URL to the connector&#x27;s manifest.yaml file

#### \_fetch\_manifest\_dict

```python
def _fetch_manifest_dict(url: str) -> dict[str, Any]
```

Fetch and parse a manifest.yaml file from a URL.

**Arguments**:

- `url` - The URL to fetch the manifest from
  

**Returns**:

  The parsed manifest data as a dictionary, or empty dict if manifest not found (404)
  

**Raises**:

- `HTTPError` - If the request fails with a non-404 status code

#### \_extract\_docs\_from\_registry

```python
def _extract_docs_from_registry(connector_name: str) -> list[ApiDocsUrl]
```

Extract documentation URLs from connector registry metadata.

**Arguments**:

- `connector_name` - The canonical connector name (e.g., &quot;source-facebook-marketing&quot;)
  

**Returns**:

  List of ApiDocsUrl objects extracted from the registry

#### get\_connector\_api\_docs\_urls

```python
def get_connector_api_docs_urls(connector_name: str) -> list[ApiDocsUrl]
```

Get API documentation URLs for a connector.

This function retrieves documentation URLs for a connector&#x27;s upstream API from multiple sources:
- Registry metadata (documentationUrl, externalDocumentationUrls)
- Connector manifest.yaml file (data.externalDocumentationUrls)

**Arguments**:

- `connector_name` - The canonical connector name (e.g., &quot;source-facebook-marketing&quot;)
  

**Returns**:

  List of ApiDocsUrl objects with documentation URLs, deduplicated by URL.
  

**Raises**:

- `AirbyteConnectorNotRegisteredError` - If the connector is not found in the registry.

#### get\_connector\_version\_history

```python
def get_connector_version_history(
        connector_name: str,
        *,
        num_versions_to_validate: int = 5,
        timeout: int = 30) -> list[ConnectorVersionInfo]
```

Get version history for a connector.

This function retrieves the version history for a connector by:
1. Scraping the changelog HTML from docs.airbyte.com
2. Parsing version information including PR URLs and titles
3. Overriding release dates for the most recent N versions with accurate
registry data

**Arguments**:

- `connector_name` - Name of the connector (e.g., &#x27;source-faker&#x27;, &#x27;destination-postgres&#x27;)
- `num_versions_to_validate` - Number of most recent versions to override with
  registry release dates for accuracy. Defaults to 5.
- `timeout` - Timeout in seconds for the changelog fetch. Defaults to 30.
  

**Returns**:

  List of ConnectorVersionInfo objects, sorted by most recent first.
  

**Raises**:

- `AirbyteConnectorNotRegisteredError` - If the connector is not found in the registry.
  

**Example**:

  &gt;&gt;&gt; versions = get_connector_version_history(&quot;source-faker&quot;, num_versions_to_validate=3)
  &gt;&gt;&gt; for v in versions[:5]:
  ...     print(f&quot;{v.version}: {v.release_date}&quot;)

