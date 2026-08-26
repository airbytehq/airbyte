---
id: airbyte-sources-registry
title: airbyte.sources.registry
---

Backwards compatibility shim for airbyte.sources.registry.

This module re-exports symbols from airbyte.registry for backwards compatibility.
New code should import from airbyte.registry directly.

### `get_available_connectors` {#airbyte.sources.registry.get_available_connectors}

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

### `get_connector_metadata` {#airbyte.sources.registry.get_connector_metadata}

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

### `ConnectorMetadata` {#airbyte.sources.registry.ConnectorMetadata}

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

#### Attributes {#airbyte.sources.registry.ConnectorMetadata--attributes}

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

### `InstallType` {#airbyte.sources.registry.InstallType}

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

#### Attributes {#airbyte.sources.registry.InstallType--attributes}

- **`ANY`** — All connectors in the registry (environment-independent).

- **`DOCKER`** — Docker-based connectors (returns all connectors for backward compatibility).

- **`INSTALLABLE`** — Connectors installable in the current environment (environment-sensitive).  Returns all connectors if Docker is installed, otherwise only Python and YAML.

- **`JAVA`** — Java-based connectors.

- **`PYTHON`** — Python-based connectors available via PyPI.

- **`YAML`** — Manifest-only connectors that can be run without Docker.

</ApiMember>

### `Language` {#airbyte.sources.registry.Language}

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

#### Attributes {#airbyte.sources.registry.Language--attributes}

- **`JAVA`**

- **`MANIFEST_ONLY`**

- **`PYTHON`**

</ApiMember>