---
id: airbyte-registry
title: airbyte.registry
---

Connectivity to the connector catalog registry.

### `get_available_connectors` {#airbyte.registry.get_available_connectors}

<ApiMember kind="function">

<ApiSignature>

```python
def get_available_connectors(
    install_type: InstallType | str | None = InstallType.INSTALLABLE,
) -> list[str]
```

</ApiSignature>

Return a list of all available connectors.

Connectors will be returned in alphabetical order, with the standard prefix "source-".

**Args:**

- **`install_type`**: The type of installation for the connector. Defaults to `InstallType.INSTALLABLE`.

</ApiMember>

### `get_connector_api_docs_urls` {#airbyte.registry.get_connector_api_docs_urls}

<ApiMember kind="function">

<ApiSignature>

```python
def get_connector_api_docs_urls(
    connector_name: str,
) -> list[airbyte.registry.ApiDocsUrl]
```

</ApiSignature>

Get API documentation URLs for a connector.

This function retrieves documentation URLs for a connector's upstream API from multiple sources:
- Registry metadata (documentationUrl, externalDocumentationUrls)
- Connector manifest.yaml file (data.externalDocumentationUrls)

**Args:**

- **`connector_name`**: The canonical connector name (e.g., "source-facebook-marketing")

**Returns:**

List of ApiDocsUrl objects with documentation URLs, deduplicated by URL.

**Raises:**

- **`AirbyteConnectorNotRegisteredError`**: If the connector is not found in the registry.

</ApiMember>

### `get_connector_metadata` {#airbyte.registry.get_connector_metadata}

<ApiMember kind="function">

<ApiSignature>

```python
def get_connector_metadata(
    name: str,
) -> airbyte.registry.ConnectorMetadata | None
```

</ApiSignature>

Check the cache for the connector.

If the cache is empty, populate by calling update_cache.

</ApiMember>

### `get_connector_version_history` {#airbyte.registry.get_connector_version_history}

<ApiMember kind="function">

<ApiSignature>

```python
def get_connector_version_history(
    connector_name: str,
    *,
    num_versions_to_validate: int = 5,
    timeout: int = 30,
) -> list[airbyte.registry.ConnectorVersionInfo]
```

</ApiSignature>

Get version history for a connector.

This function retrieves the version history for a connector by:
1. Scraping the changelog HTML from docs.airbyte.com
2. Parsing version information including PR URLs and titles
3. Overriding release dates for the most recent N versions with accurate
   registry data

**Args:**

- **`connector_name`**: Name of the connector (e.g., 'source-faker', 'destination-postgres')
- **`num_versions_to_validate`**: Number of most recent versions to override with registry release dates for accuracy. Defaults to 5.
- **`timeout`**: Timeout in seconds for the changelog fetch. Defaults to 30.

**Returns:**

List of ConnectorVersionInfo objects, sorted by most recent first.

**Raises:**

- **`AirbyteConnectorNotRegisteredError`**: If the connector is not found in the registry.

**Example:**

```python
versions = get_connector_version_history("source-faker", num_versions_to_validate=3)
for v in versions[:5]:
    print(f"{v.version}: {v.release_date}")
```

</ApiMember>

### `ApiDocsUrl` {#airbyte.registry.ApiDocsUrl}

<ApiMember kind="class">

<ApiSignature>

```python
class ApiDocsUrl(**data: Any)
```

</ApiSignature>

API documentation URL information.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Attributes {#airbyte.registry.ApiDocsUrl--attributes}

- **`doc_type`**&nbsp;(`str`)

- **`requires_login`**&nbsp;(`bool`)

- **`source`**&nbsp;(`str`)

- **`title`**&nbsp;(`str`)

- **`url`**&nbsp;(`str`)

#### `from_manifest_dict` {#airbyte.registry.ApiDocsUrl.from_manifest_dict}

<ApiMember kind="method">

<ApiSignature>

```python
def from_manifest_dict(
    manifest_data: dict[str, Any],
) -> list[typing_extensions.Self]
```

</ApiSignature>

Extract documentation URLs from parsed manifest data.

**Args:**

- **`manifest_data`**: The parsed manifest.yaml data as a dictionary

**Returns:**

List of ApiDocsUrl objects extracted from the manifest

</ApiMember>

</ApiMember>

### `ConnectorMetadata` {#airbyte.registry.ConnectorMetadata}

<ApiMember kind="class">

<ApiSignature>

```python
class ConnectorMetadata(**data: Any)
```

</ApiSignature>

Metadata for a connector.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Attributes {#airbyte.registry.ConnectorMetadata--attributes}

- **`connector_type`**&nbsp;(`str | None`) — Connector type: `source` or `destination`.

- **`definition_id`**&nbsp;(`str | None`) — Source or destination definition ID.

- **`display_name`**&nbsp;(`str | None`) — Human-readable connector name.

- **`docker_repository`**&nbsp;(`str | None`) — Docker repository for the connector image.

- **`documentation_url`**&nbsp;(`str | None`) — Connector documentation URL.

- **`github_issue_label`**&nbsp;(`str | None`) — GitHub issue label for the connector.

- **`install_types`**&nbsp;(`set[airbyte.registry.InstallType]`) — The supported install types for the connector.

- **`language`**&nbsp;(`airbyte.registry.Language | None`) — The language of the connector.

- **`latest_available_version`**&nbsp;(`str | None`) — The latest available version of the connector.

- **`name`**&nbsp;(`str`) — Connector name. For example, "source-google-sheets".

- **`pypi_package_name`**&nbsp;(`str | None`) — The name of the PyPI package for the connector, if it exists.

- **`release_date`**&nbsp;(`str | None`) — Connector release date.

- **`release_stage`**&nbsp;(`str | None`) — Connector release stage.

- **`source_type`**&nbsp;(`str | None`) — Connector subtype.

- **`suggested_streams`**&nbsp;(`list[str] | None`) — A list of suggested streams for the connector, if available.

- **`support_level`**&nbsp;(`str | None`) — Connector support level.

- **`default_install_type`**&nbsp;(`InstallType`) — Return the default install type for the connector.

</ApiMember>

### `ConnectorVersionInfo` {#airbyte.registry.ConnectorVersionInfo}

<ApiMember kind="class">

<ApiSignature>

```python
class ConnectorVersionInfo(**data: Any)
```

</ApiSignature>

Information about a specific connector version.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Attributes {#airbyte.registry.ConnectorVersionInfo--attributes}

- **`changelog_url`**&nbsp;(`str`)

- **`docker_image_url`**&nbsp;(`str`)

- **`parsing_errors`**&nbsp;(`list[str]`)

- **`pr_title`**&nbsp;(`str | None`)

- **`pr_url`**&nbsp;(`str | None`)

- **`release_date`**&nbsp;(`str | None`)

- **`version`**&nbsp;(`str`)

</ApiMember>

### `InstallType` {#airbyte.registry.InstallType}

<ApiMember kind="class">

<ApiSignature>

```python
class InstallType(
    value,
    names=None,
    *,
    module=None,
    qualname=None,
    type=None,
    start=1,
)
```

</ApiSignature>

The type of installation for a connector.

**Bases:** `builtins.str`, `enum.Enum`

#### Attributes {#airbyte.registry.InstallType--attributes}

- **`ANY`** — All connectors in the registry (environment-independent).

- **`DOCKER`** — Docker-based connectors (returns all connectors for backward compatibility).

- **`INSTALLABLE`** — Connectors installable in the current environment (environment-sensitive).  Returns all connectors if Docker is installed, otherwise only Python and YAML.

- **`JAVA`** — Java-based connectors.

- **`PYTHON`** — Python-based connectors available via PyPI.

- **`YAML`** — Manifest-only connectors that can be run without Docker.

</ApiMember>

### `Language` {#airbyte.registry.Language}

<ApiMember kind="class">

<ApiSignature>

```python
class Language(
    value,
    names=None,
    *,
    module=None,
    qualname=None,
    type=None,
    start=1,
)
```

</ApiSignature>

The language of a connector.

**Bases:** `builtins.str`, `enum.Enum`

#### Attributes {#airbyte.registry.Language--attributes}

- **`JAVA`**

- **`MANIFEST_ONLY`**

- **`PYTHON`**

</ApiMember>