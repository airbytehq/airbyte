---
id: airbyte-exceptions
title: "airbyte.exceptions Module"
sidebar_label: "airbyte.exceptions"
toc_max_heading_level: 5
---

# `airbyte.exceptions` Module

All exceptions used in the PyAirbyte.

This design is modeled after structlog's exceptions, in that we bias towards auto-generated
property prints rather than sentence-like string concatenation.

E.g. Instead of this:

> `Subprocess failed with exit code '1'`

We do this:

> `Subprocess failed. (exit_code=1)`

The benefit of this approach is that we can easily support structured logging, and we can
easily add new properties to exceptions without having to update all the places where they
are raised. We can also support any arbitrary number of properties in exceptions, without spending
time on building sentence-like string constructions with optional inputs.

In addition, the following principles are applied for exception class design:

- All exceptions inherit from a common base class.
- All exceptions have a message attribute.
- The first line of the docstring is used as the default message.
- The default message can be overridden by explicitly setting the message attribute.
- Exceptions may optionally have a guidance attribute.
- Exceptions may optionally have a help_url attribute.
- Rendering is automatically handled by the base class.
- Any helpful context not defined by the exception class can be passed in the `context` dict arg.
- Within reason, avoid sending PII to the exception constructor.
- Exceptions are dataclasses, so they can be instantiated with keyword arguments.
- Use the 'from' syntax to chain exceptions when it is helpful to do so.
  E.g. `raise AirbyteConnectorNotFoundError(...) from FileNotFoundError(connector_path)`
- Any exception that adds a new property should also be decorated as `@dataclass`.

### `AirbyteConnectionError` {#airbyte.exceptions.AirbyteConnectionError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectionError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    response: AirbyteApiResponseDuckType | None = None,
    workspace: _WorkspaceWithUrl | None = None,
    connection_id: str | None = None,
    job_id: int | None = None,
    job_status: str | None = None,
)
```

</ApiSignature>

An connection error occurred while communicating with the hosted Airbyte instance.

#### Bases {#airbyte.exceptions.AirbyteConnectionError--bases}

`airbyte.exceptions.AirbyteError`
#### Descendants {#airbyte.exceptions.AirbyteConnectionError--descendants}

`airbyte.exceptions.AirbyteConnectionSyncActiveError`, `airbyte.exceptions.AirbyteConnectionSyncError`
#### Instance Variables {#airbyte.exceptions.AirbyteConnectionError--instance-variables}

- **`connection_id`**&nbsp;(`str | None`)

  The connection ID where the error occurred.

- **`connection_url`**&nbsp;(`str | None`)

  The web URL to the connection where the error occurred.

- **`job_history_url`**&nbsp;(`str | None`)

  The URL to the job history where the error occurred.

- **`job_id`**&nbsp;(`int | None`)

  The job ID where the error occurred (if applicable).

- **`job_status`**&nbsp;(`str | None`)

  The latest status of the job where the error occurred (if applicable).

- **`job_url`**&nbsp;(`str | None`)

  The URL to the job where the error occurred.

</ApiMember>

### `AirbyteConnectionSyncActiveError` {#airbyte.exceptions.AirbyteConnectionSyncActiveError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectionSyncActiveError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    response: AirbyteApiResponseDuckType | None = None,
    workspace: _WorkspaceWithUrl | None = None,
    connection_id: str | None = None,
    job_id: int | None = None,
    job_status: str | None = None,
)
```

</ApiSignature>

State update rejected because a sync is currently running (HTTP 423).

#### Bases {#airbyte.exceptions.AirbyteConnectionSyncActiveError--bases}

`airbyte.exceptions.AirbyteConnectionError`

</ApiMember>

### `AirbyteConnectionSyncError` {#airbyte.exceptions.AirbyteConnectionSyncError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectionSyncError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    response: AirbyteApiResponseDuckType | None = None,
    workspace: _WorkspaceWithUrl | None = None,
    connection_id: str | None = None,
    job_id: int | None = None,
    job_status: str | None = None,
)
```

</ApiSignature>

An error occurred while executing the remote Airbyte job.

#### Bases {#airbyte.exceptions.AirbyteConnectionSyncError--bases}

`airbyte.exceptions.AirbyteConnectionError`
#### Descendants {#airbyte.exceptions.AirbyteConnectionSyncError--descendants}

`airbyte.exceptions.AirbyteConnectionSyncTimeoutError`

</ApiMember>

### `AirbyteConnectionSyncTimeoutError` {#airbyte.exceptions.AirbyteConnectionSyncTimeoutError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectionSyncTimeoutError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    response: AirbyteApiResponseDuckType | None = None,
    workspace: _WorkspaceWithUrl | None = None,
    connection_id: str | None = None,
    job_id: int | None = None,
    job_status: str | None = None,
    timeout: int | None = None,
)
```

</ApiSignature>

An timeout occurred while waiting for the remote Airbyte job to complete.

#### Bases {#airbyte.exceptions.AirbyteConnectionSyncTimeoutError--bases}

`airbyte.exceptions.AirbyteConnectionSyncError`
#### Instance Variables {#airbyte.exceptions.AirbyteConnectionSyncTimeoutError--instance-variables}

- **`timeout`**&nbsp;(`int | None`)

  The timeout in seconds that was reached.

</ApiMember>

### `AirbyteConnectorCheckFailedError` {#airbyte.exceptions.AirbyteConnectorCheckFailedError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorCheckFailedError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

Connector check failed.

#### Bases {#airbyte.exceptions.AirbyteConnectorCheckFailedError--bases}

`airbyte.exceptions.AirbyteConnectorError`
#### Class Variables {#airbyte.exceptions.AirbyteConnectorCheckFailedError--class-variables}

- **`guidance`**&nbsp;(`str | None`)

</ApiMember>

### `AirbyteConnectorConfigurationMissingError` {#airbyte.exceptions.AirbyteConnectorConfigurationMissingError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorConfigurationMissingError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

Connector is missing configuration.

#### Bases {#airbyte.exceptions.AirbyteConnectorConfigurationMissingError--bases}

`airbyte.exceptions.PyAirbyteCacheError`
#### Instance Variables {#airbyte.exceptions.AirbyteConnectorConfigurationMissingError--instance-variables}

- **`connector_name`**&nbsp;(`str | None`)

</ApiMember>

### `AirbyteConnectorDiscoverFailedError` {#airbyte.exceptions.AirbyteConnectorDiscoverFailedError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorDiscoverFailedError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

Error when running discovery on the connector.

#### Bases {#airbyte.exceptions.AirbyteConnectorDiscoverFailedError--bases}

`airbyte.exceptions.AirbyteConnectorError`

</ApiMember>

### `AirbyteConnectorError` {#airbyte.exceptions.AirbyteConnectorError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

Error when running the connector.

#### Bases {#airbyte.exceptions.AirbyteConnectorError--bases}

`airbyte.exceptions.PyAirbyteError`
#### Descendants {#airbyte.exceptions.AirbyteConnectorError--descendants}

`airbyte.exceptions.AirbyteConnectorCheckFailedError`, `airbyte.exceptions.AirbyteConnectorDiscoverFailedError`, `airbyte.exceptions.AirbyteConnectorExecutableNotFoundError`, `airbyte.exceptions.AirbyteConnectorFailedError`, `airbyte.exceptions.AirbyteConnectorInstallationError`, `airbyte.exceptions.AirbyteConnectorMissingCatalogError`, `airbyte.exceptions.AirbyteConnectorMissingSpecError`, `airbyte.exceptions.AirbyteConnectorReadError`, `airbyte.exceptions.AirbyteConnectorSpecFailedError`, `airbyte.exceptions.AirbyteConnectorValidationFailedError`, `airbyte.exceptions.AirbyteConnectorWriteError`, `airbyte.exceptions.AirbyteNoDataFromConnectorError`, `airbyte.exceptions.AirbyteStateNotFoundError`, `airbyte.exceptions.AirbyteStreamNotFoundError`
#### Instance Variables {#airbyte.exceptions.AirbyteConnectorError--instance-variables}

- **`connector_name`**&nbsp;(`str | None`)

</ApiMember>

### `AirbyteConnectorExecutableNotFoundError` {#airbyte.exceptions.AirbyteConnectorExecutableNotFoundError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorExecutableNotFoundError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

Connector executable not found.

#### Bases {#airbyte.exceptions.AirbyteConnectorExecutableNotFoundError--bases}

`airbyte.exceptions.AirbyteConnectorError`

</ApiMember>

### `AirbyteConnectorFailedError` {#airbyte.exceptions.AirbyteConnectorFailedError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorFailedError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
    exit_code: int | None = None,
)
```

</ApiSignature>

Connector failed.

#### Bases {#airbyte.exceptions.AirbyteConnectorFailedError--bases}

`airbyte.exceptions.AirbyteConnectorError`
#### Instance Variables {#airbyte.exceptions.AirbyteConnectorFailedError--instance-variables}

- **`exit_code`**&nbsp;(`int | None`)

</ApiMember>

### `AirbyteConnectorInstallationError` {#airbyte.exceptions.AirbyteConnectorInstallationError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorInstallationError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

Error when installing the connector.

#### Bases {#airbyte.exceptions.AirbyteConnectorInstallationError--bases}

`airbyte.exceptions.AirbyteConnectorError`

</ApiMember>

### `AirbyteConnectorMissingCatalogError` {#airbyte.exceptions.AirbyteConnectorMissingCatalogError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorMissingCatalogError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

Connector did not return a catalog.

#### Bases {#airbyte.exceptions.AirbyteConnectorMissingCatalogError--bases}

`airbyte.exceptions.AirbyteConnectorError`

</ApiMember>

### `AirbyteConnectorMissingSpecError` {#airbyte.exceptions.AirbyteConnectorMissingSpecError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorMissingSpecError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

Connector did not return a spec.

#### Bases {#airbyte.exceptions.AirbyteConnectorMissingSpecError--bases}

`airbyte.exceptions.AirbyteConnectorError`

</ApiMember>

### `AirbyteConnectorNotPyPiPublishedError` {#airbyte.exceptions.AirbyteConnectorNotPyPiPublishedError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorNotPyPiPublishedError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

Connector found, but not published to PyPI.

#### Bases {#airbyte.exceptions.AirbyteConnectorNotPyPiPublishedError--bases}

`airbyte.exceptions.AirbyteConnectorRegistryError`
#### Class Variables {#airbyte.exceptions.AirbyteConnectorNotPyPiPublishedError--class-variables}

- **`guidance`**&nbsp;(`str | None`)

#### Instance Variables {#airbyte.exceptions.AirbyteConnectorNotPyPiPublishedError--instance-variables}

- **`connector_name`**&nbsp;(`str | None`)

</ApiMember>

### `AirbyteConnectorNotRegisteredError` {#airbyte.exceptions.AirbyteConnectorNotRegisteredError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorNotRegisteredError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

Connector not found in registry.

#### Bases {#airbyte.exceptions.AirbyteConnectorNotRegisteredError--bases}

`airbyte.exceptions.AirbyteConnectorRegistryError`
#### Class Variables {#airbyte.exceptions.AirbyteConnectorNotRegisteredError--class-variables}

- **`guidance`**&nbsp;(`str | None`)

- **`help_url`**&nbsp;(`str | None`)

#### Instance Variables {#airbyte.exceptions.AirbyteConnectorNotRegisteredError--instance-variables}

- **`connector_name`**&nbsp;(`str | None`)

</ApiMember>

### `AirbyteConnectorReadError` {#airbyte.exceptions.AirbyteConnectorReadError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorReadError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

Error when reading from the connector.

#### Bases {#airbyte.exceptions.AirbyteConnectorReadError--bases}

`airbyte.exceptions.AirbyteConnectorError`

</ApiMember>

### `AirbyteConnectorRegistryError` {#airbyte.exceptions.AirbyteConnectorRegistryError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorRegistryError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
)
```

</ApiSignature>

Error when accessing the connector registry.

#### Bases {#airbyte.exceptions.AirbyteConnectorRegistryError--bases}

`airbyte.exceptions.PyAirbyteError`
#### Descendants {#airbyte.exceptions.AirbyteConnectorRegistryError--descendants}

`airbyte.exceptions.AirbyteConnectorNotPyPiPublishedError`, `airbyte.exceptions.AirbyteConnectorNotRegisteredError`

</ApiMember>

### `AirbyteConnectorSpecFailedError` {#airbyte.exceptions.AirbyteConnectorSpecFailedError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorSpecFailedError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

Error when getting spec from the connector.

#### Bases {#airbyte.exceptions.AirbyteConnectorSpecFailedError--bases}

`airbyte.exceptions.AirbyteConnectorError`

</ApiMember>

### `AirbyteConnectorValidationFailedError` {#airbyte.exceptions.AirbyteConnectorValidationFailedError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorValidationFailedError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

Connector config validation failed.

#### Bases {#airbyte.exceptions.AirbyteConnectorValidationFailedError--bases}

`airbyte.exceptions.AirbyteConnectorError`
#### Class Variables {#airbyte.exceptions.AirbyteConnectorValidationFailedError--class-variables}

- **`guidance`**&nbsp;(`str | None`)

</ApiMember>

### `AirbyteConnectorWriteError` {#airbyte.exceptions.AirbyteConnectorWriteError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteConnectorWriteError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

Error when writing to the connector.

#### Bases {#airbyte.exceptions.AirbyteConnectorWriteError--bases}

`airbyte.exceptions.AirbyteConnectorError`

</ApiMember>

### `AirbyteDuplicateResourcesError` {#airbyte.exceptions.AirbyteDuplicateResourcesError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteDuplicateResourcesError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    response: AirbyteApiResponseDuckType | None = None,
    workspace: _WorkspaceWithUrl | None = None,
    resource_type: str | None = None,
    resource_name: str | None = None,
)
```

</ApiSignature>

Process failed because resource name was not unique.

#### Bases {#airbyte.exceptions.AirbyteDuplicateResourcesError--bases}

`airbyte.exceptions.AirbyteError`
#### Instance Variables {#airbyte.exceptions.AirbyteDuplicateResourcesError--instance-variables}

- **`resource_name`**&nbsp;(`str | None`)

- **`resource_type`**&nbsp;(`str | None`)

</ApiMember>

### `AirbyteError` {#airbyte.exceptions.AirbyteError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    response: AirbyteApiResponseDuckType | None = None,
    workspace: _WorkspaceWithUrl | None = None,
)
```

</ApiSignature>

An error occurred while communicating with the hosted Airbyte instance.

#### Bases {#airbyte.exceptions.AirbyteError--bases}

`airbyte.exceptions.PyAirbyteError`
#### Descendants {#airbyte.exceptions.AirbyteError--descendants}

`airbyte.exceptions.AirbyteConnectionError`, `airbyte.exceptions.AirbyteDuplicateResourcesError`, `airbyte.exceptions.AirbyteMissingResourceError`, `airbyte.exceptions.AirbyteMultipleResourcesError`, `airbyte.exceptions.AirbyteWorkspaceMismatchError`, `airbyte.exceptions.AirbyteWorkspaceNotEmptyError`
#### Instance Variables {#airbyte.exceptions.AirbyteError--instance-variables}

- **`response`**&nbsp;(`AirbyteApiResponseDuckType | None`)

  The API response from the failed request.

- **`workspace`**&nbsp;(`_WorkspaceWithUrl | None`)

  The workspace where the error occurred.

- **`workspace_url`**&nbsp;(`str | None`)

  The URL to the workspace where the error occurred.

</ApiMember>

### `AirbyteExperimentalFeatureWarning` {#airbyte.exceptions.AirbyteExperimentalFeatureWarning}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteExperimentalFeatureWarning(*args, **kwargs)
```

</ApiSignature>

Warning whenever using experimental features in PyAirbyte.

#### Bases {#airbyte.exceptions.AirbyteExperimentalFeatureWarning--bases}

`builtins.FutureWarning`

</ApiMember>

### `AirbyteMCPError` {#airbyte.exceptions.AirbyteMCPError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteMCPError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
)
```

</ApiSignature>

An error occurred in the Airbyte MCP server.

#### Bases {#airbyte.exceptions.AirbyteMCPError--bases}

`airbyte.exceptions.PyAirbyteError`
#### Descendants {#airbyte.exceptions.AirbyteMCPError--descendants}

`airbyte.exceptions.AirbyteTrustedExecutionRequiredError`

</ApiMember>

### `AirbyteMissingResourceError` {#airbyte.exceptions.AirbyteMissingResourceError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteMissingResourceError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    response: AirbyteApiResponseDuckType | None = None,
    workspace: _WorkspaceWithUrl | None = None,
    resource_type: str | None = None,
    resource_name_or_id: str | None = None,
)
```

</ApiSignature>

Remote Airbyte resources does not exist.

#### Bases {#airbyte.exceptions.AirbyteMissingResourceError--bases}

`airbyte.exceptions.AirbyteError`
#### Instance Variables {#airbyte.exceptions.AirbyteMissingResourceError--instance-variables}

- **`resource_name_or_id`**&nbsp;(`str | None`)

- **`resource_type`**&nbsp;(`str | None`)

</ApiMember>

### `AirbyteMissingWorkspaceContextError` {#airbyte.exceptions.AirbyteMissingWorkspaceContextError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteMissingWorkspaceContextError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    input_value: str | None = None,
)
```

</ApiSignature>

Workspace ID is required but not provided.

#### Bases {#airbyte.exceptions.AirbyteMissingWorkspaceContextError--bases}

`airbyte.exceptions.PyAirbyteInputError`
#### Instance Variables {#airbyte.exceptions.AirbyteMissingWorkspaceContextError--instance-variables}

- **`guidance`**&nbsp;(`str | None`)

</ApiMember>

### `AirbyteMultipleResourcesError` {#airbyte.exceptions.AirbyteMultipleResourcesError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteMultipleResourcesError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    response: AirbyteApiResponseDuckType | None = None,
    workspace: _WorkspaceWithUrl | None = None,
    resource_type: str | None = None,
    resource_name_or_id: str | None = None,
)
```

</ApiSignature>

Could not locate the resource because multiple matching resources were found.

#### Bases {#airbyte.exceptions.AirbyteMultipleResourcesError--bases}

`airbyte.exceptions.AirbyteError`
#### Instance Variables {#airbyte.exceptions.AirbyteMultipleResourcesError--instance-variables}

- **`resource_name_or_id`**&nbsp;(`str | None`)

- **`resource_type`**&nbsp;(`str | None`)

</ApiMember>

### `AirbyteNoCloudCredentialsError` {#airbyte.exceptions.AirbyteNoCloudCredentialsError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteNoCloudCredentialsError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    input_value: str | None = None,
)
```

</ApiSignature>

No Airbyte credentials found.

#### Bases {#airbyte.exceptions.AirbyteNoCloudCredentialsError--bases}

`airbyte.exceptions.PyAirbyteInputError`
#### Instance Variables {#airbyte.exceptions.AirbyteNoCloudCredentialsError--instance-variables}

- **`guidance`**&nbsp;(`str | None`)

</ApiMember>

### `AirbyteNoDataFromConnectorError` {#airbyte.exceptions.AirbyteNoDataFromConnectorError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteNoDataFromConnectorError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
)
```

</ApiSignature>

No data was provided from the connector.

#### Bases {#airbyte.exceptions.AirbyteNoDataFromConnectorError--bases}

`airbyte.exceptions.AirbyteConnectorError`

</ApiMember>

### `AirbyteStateNotFoundError` {#airbyte.exceptions.AirbyteStateNotFoundError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteStateNotFoundError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
    stream_name: str | None = None,
    available_streams: list[str] | None = None,
)
```

</ApiSignature>

State entry not found.

#### Bases {#airbyte.exceptions.AirbyteStateNotFoundError--bases}

`airbyte.exceptions.AirbyteConnectorError`, `builtins.KeyError`
#### Instance Variables {#airbyte.exceptions.AirbyteStateNotFoundError--instance-variables}

- **`available_streams`**&nbsp;(`list[str] | None`)

- **`stream_name`**&nbsp;(`str | None`)

</ApiMember>

### `AirbyteStreamNotFoundError` {#airbyte.exceptions.AirbyteStreamNotFoundError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteStreamNotFoundError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    connector_name: str | None = None,
    stream_name: str | None = None,
    available_streams: list[str] | None = None,
)
```

</ApiSignature>

Connector stream not found.

#### Bases {#airbyte.exceptions.AirbyteStreamNotFoundError--bases}

`airbyte.exceptions.AirbyteConnectorError`
#### Instance Variables {#airbyte.exceptions.AirbyteStreamNotFoundError--instance-variables}

- **`available_streams`**&nbsp;(`list[str] | None`)

- **`stream_name`**&nbsp;(`str | None`)

</ApiMember>

### `AirbyteSubprocessError` {#airbyte.exceptions.AirbyteSubprocessError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteSubprocessError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    run_args: list[str] | None = None,
)
```

</ApiSignature>

Error when running subprocess.

#### Bases {#airbyte.exceptions.AirbyteSubprocessError--bases}

`airbyte.exceptions.PyAirbyteError`
#### Descendants {#airbyte.exceptions.AirbyteSubprocessError--descendants}

`airbyte.exceptions.AirbyteSubprocessFailedError`
#### Instance Variables {#airbyte.exceptions.AirbyteSubprocessError--instance-variables}

- **`run_args`**&nbsp;(`list[str] | None`)

</ApiMember>

### `AirbyteSubprocessFailedError` {#airbyte.exceptions.AirbyteSubprocessFailedError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteSubprocessFailedError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    run_args: list[str] | None = None,
    exit_code: int | None = None,
)
```

</ApiSignature>

Subprocess failed.

#### Bases {#airbyte.exceptions.AirbyteSubprocessFailedError--bases}

`airbyte.exceptions.AirbyteSubprocessError`
#### Instance Variables {#airbyte.exceptions.AirbyteSubprocessFailedError--instance-variables}

- **`exit_code`**&nbsp;(`int | None`)

</ApiMember>

### `AirbyteTrustedExecutionRequiredError` {#airbyte.exceptions.AirbyteTrustedExecutionRequiredError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteTrustedExecutionRequiredError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    feature: str | None = None,
)
```

</ApiSignature>

A trusted-execution-only capability was invoked while trusted execution is disabled.

Trusted execution grants the MCP server its trusted-machine capabilities: local
filesystem access, local connector installation/execution, and server-side secret
resolution. It defaults to *off* on every transport and is permanently unavailable
over the HTTP transport, so a backend helper that exposes one of those capabilities
hard-fails when the gate is disabled -- independently of whether the corresponding
tool was hidden from the tool listing.

#### Bases {#airbyte.exceptions.AirbyteTrustedExecutionRequiredError--bases}

`airbyte.exceptions.AirbyteMCPError`
#### Class Variables {#airbyte.exceptions.AirbyteTrustedExecutionRequiredError--class-variables}

- **`guidance`**&nbsp;(`str | None`)

#### Instance Variables {#airbyte.exceptions.AirbyteTrustedExecutionRequiredError--instance-variables}

- **`feature`**&nbsp;(`str | None`)

</ApiMember>

### `AirbyteWorkspaceMismatchError` {#airbyte.exceptions.AirbyteWorkspaceMismatchError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteWorkspaceMismatchError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    response: AirbyteApiResponseDuckType | None = None,
    workspace: _WorkspaceWithUrl | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    expected_workspace_id: str | None = None,
    actual_workspace_id: str | None = None,
)
```

</ApiSignature>

Resource does not belong to the expected workspace.

This error is raised when a resource (connection, source, or destination) is fetched
from the API and the workspace ID in the response does not match the expected workspace.

#### Bases {#airbyte.exceptions.AirbyteWorkspaceMismatchError--bases}

`airbyte.exceptions.AirbyteError`
#### Instance Variables {#airbyte.exceptions.AirbyteWorkspaceMismatchError--instance-variables}

- **`actual_workspace_id`**&nbsp;(`str | None`)

  The workspace ID returned by the API.

- **`expected_workspace_id`**&nbsp;(`str | None`)

  The workspace ID that was expected.

- **`resource_id`**&nbsp;(`str | None`)

  The ID of the resource that was fetched.

- **`resource_type`**&nbsp;(`str | None`)

  The type of resource (e.g., 'connection', 'source', 'destination').

</ApiMember>

### `AirbyteWorkspaceNotEmptyError` {#airbyte.exceptions.AirbyteWorkspaceNotEmptyError}

<ApiMember kind="class">

<ApiSignature>

```python
class AirbyteWorkspaceNotEmptyError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    response: AirbyteApiResponseDuckType | None = None,
    workspace: _WorkspaceWithUrl | None = None,
    workspace_id: str | None = None,
    connection_ids: list[str] | None = None,
)
```

</ApiSignature>

Workspace cannot be deleted because it contains connections.

#### Bases {#airbyte.exceptions.AirbyteWorkspaceNotEmptyError--bases}

`airbyte.exceptions.AirbyteError`
#### Instance Variables {#airbyte.exceptions.AirbyteWorkspaceNotEmptyError--instance-variables}

- **`connection_ids`**&nbsp;(`list[str] | None`)

  The connection IDs found in the workspace.

- **`workspace_id`**&nbsp;(`str | None`)

  The workspace ID that was expected to be empty.

</ApiMember>

### `PyAirbyteCacheError` {#airbyte.exceptions.PyAirbyteCacheError}

<ApiMember kind="class">

<ApiSignature>

```python
class PyAirbyteCacheError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
)
```

</ApiSignature>

Error occurred while accessing the cache.

#### Bases {#airbyte.exceptions.PyAirbyteCacheError--bases}

`airbyte.exceptions.PyAirbyteError`
#### Descendants {#airbyte.exceptions.PyAirbyteCacheError--descendants}

`airbyte.exceptions.AirbyteConnectorConfigurationMissingError`, `airbyte.exceptions.PyAirbyteCacheTableValidationError`

</ApiMember>

### `PyAirbyteCacheTableValidationError` {#airbyte.exceptions.PyAirbyteCacheTableValidationError}

<ApiMember kind="class">

<ApiSignature>

```python
class PyAirbyteCacheTableValidationError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    violation: str | None = None,
)
```

</ApiSignature>

Cache table validation failed.

#### Bases {#airbyte.exceptions.PyAirbyteCacheTableValidationError--bases}

`airbyte.exceptions.PyAirbyteCacheError`
#### Instance Variables {#airbyte.exceptions.PyAirbyteCacheTableValidationError--instance-variables}

- **`violation`**&nbsp;(`str | None`)

</ApiMember>

### `PyAirbyteDataLossWarning` {#airbyte.exceptions.PyAirbyteDataLossWarning}

<ApiMember kind="class">

<ApiSignature>

```python
class PyAirbyteDataLossWarning(*args, **kwargs)
```

</ApiSignature>

Warning for potential data loss.

Users can ignore this warning by running:
> warnings.filterwarnings("ignore", category="airbyte.exceptions.PyAirbyteDataLossWarning")

#### Bases {#airbyte.exceptions.PyAirbyteDataLossWarning--bases}

`airbyte.exceptions.PyAirbyteWarning`

</ApiMember>

### `PyAirbyteError` {#airbyte.exceptions.PyAirbyteError}

<ApiMember kind="class">

<ApiSignature>

```python
class PyAirbyteError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
)
```

</ApiSignature>

Base class for exceptions in Airbyte.

#### Bases {#airbyte.exceptions.PyAirbyteError--bases}

`builtins.Exception`
#### Descendants {#airbyte.exceptions.PyAirbyteError--descendants}

`airbyte.exceptions.AirbyteConnectorError`, `airbyte.exceptions.AirbyteConnectorRegistryError`, `airbyte.exceptions.AirbyteError`, `airbyte.exceptions.AirbyteMCPError`, `airbyte.exceptions.AirbyteSubprocessError`, `airbyte.exceptions.PyAirbyteCacheError`, `airbyte.exceptions.PyAirbyteInputError`, `airbyte.exceptions.PyAirbyteInternalError`, `airbyte.exceptions.PyAirbyteNameNormalizationError`, `airbyte.exceptions.PyAirbyteSecretNotFoundError`
#### Instance Variables {#airbyte.exceptions.PyAirbyteError--instance-variables}

- **`context`**&nbsp;(`dict[str, typing.Any] | None`)

- **`guidance`**&nbsp;(`str | None`)

- **`help_url`**&nbsp;(`str | None`)

- **`log_file`**&nbsp;(`pathlib.Path | None`)

- **`log_text`**&nbsp;(`str | list[str] | None`)

- **`message`**&nbsp;(`str | None`)

- **`original_exception`**&nbsp;(`Exception | None`)

- **`print_full_log`**&nbsp;(`bool`)

#### Methods {#airbyte.exceptions.PyAirbyteError--methods}

##### `get_message` {#airbyte.exceptions.PyAirbyteError.get_message}

<ApiMember kind="method">

<ApiSignature>

```python
def get_message(self) -> str
```

</ApiSignature>

Return the best description for the exception.

We resolve the following in order:
1. The message sent to the exception constructor (if provided).
2. The first line of the class's docstring.

</ApiMember>

##### `safe_logging_dict` {#airbyte.exceptions.PyAirbyteError.safe_logging_dict}

<ApiMember kind="method">

<ApiSignature>

```python
def safe_logging_dict(self) -> dict[str, typing.Any]
```

</ApiSignature>

Return a dictionary of the exception's properties which is safe for logging.

We avoid any properties which could potentially contain PII.

</ApiMember>

</ApiMember>

### `PyAirbyteInputError` {#airbyte.exceptions.PyAirbyteInputError}

<ApiMember kind="class">

<ApiSignature>

```python
class PyAirbyteInputError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    input_value: str | None = None,
)
```

</ApiSignature>

The input provided to PyAirbyte did not match expected validation rules.

This inherits from ValueError so that it can be used as a drop-in replacement for
ValueError in the PyAirbyte API.

#### Bases {#airbyte.exceptions.PyAirbyteInputError--bases}

`airbyte.exceptions.PyAirbyteError`, `builtins.ValueError`
#### Descendants {#airbyte.exceptions.PyAirbyteInputError--descendants}

`airbyte.exceptions.AirbyteMissingWorkspaceContextError`, `airbyte.exceptions.AirbyteNoCloudCredentialsError`, `airbyte.exceptions.PyAirbyteNoStreamsSelectedError`
#### Class Variables {#airbyte.exceptions.PyAirbyteInputError--class-variables}

- **`guidance`**&nbsp;(`str | None`)

- **`help_url`**&nbsp;(`str | None`)

#### Instance Variables {#airbyte.exceptions.PyAirbyteInputError--instance-variables}

- **`input_value`**&nbsp;(`str | None`)

</ApiMember>

### `PyAirbyteInternalError` {#airbyte.exceptions.PyAirbyteInternalError}

<ApiMember kind="class">

<ApiSignature>

```python
class PyAirbyteInternalError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
)
```

</ApiSignature>

An internal error occurred in PyAirbyte.

#### Bases {#airbyte.exceptions.PyAirbyteInternalError--bases}

`airbyte.exceptions.PyAirbyteError`
#### Class Variables {#airbyte.exceptions.PyAirbyteInternalError--class-variables}

- **`guidance`**&nbsp;(`str | None`)

- **`help_url`**&nbsp;(`str | None`)

</ApiMember>

### `PyAirbyteNameNormalizationError` {#airbyte.exceptions.PyAirbyteNameNormalizationError}

<ApiMember kind="class">

<ApiSignature>

```python
class PyAirbyteNameNormalizationError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    raw_name: str | None = None,
    normalization_result: str | None = None,
)
```

</ApiSignature>

Error occurred while normalizing a table or column name.

#### Bases {#airbyte.exceptions.PyAirbyteNameNormalizationError--bases}

`airbyte.exceptions.PyAirbyteError`, `builtins.ValueError`
#### Class Variables {#airbyte.exceptions.PyAirbyteNameNormalizationError--class-variables}

- **`guidance`**&nbsp;(`str | None`)

- **`help_url`**&nbsp;(`str | None`)

#### Instance Variables {#airbyte.exceptions.PyAirbyteNameNormalizationError--instance-variables}

- **`normalization_result`**&nbsp;(`str | None`)

- **`raw_name`**&nbsp;(`str | None`)

</ApiMember>

### `PyAirbyteNoStreamsSelectedError` {#airbyte.exceptions.PyAirbyteNoStreamsSelectedError}

<ApiMember kind="class">

<ApiSignature>

```python
class PyAirbyteNoStreamsSelectedError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    input_value: str | None = None,
    connector_name: str | None = None,
    available_streams: list[str] | None = None,
)
```

</ApiSignature>

No streams were selected for the source.

#### Bases {#airbyte.exceptions.PyAirbyteNoStreamsSelectedError--bases}

`airbyte.exceptions.PyAirbyteInputError`
#### Class Variables {#airbyte.exceptions.PyAirbyteNoStreamsSelectedError--class-variables}

- **`guidance`**&nbsp;(`str | None`)

#### Instance Variables {#airbyte.exceptions.PyAirbyteNoStreamsSelectedError--instance-variables}

- **`available_streams`**&nbsp;(`list[str] | None`)

- **`connector_name`**&nbsp;(`str | None`)

</ApiMember>

### `PyAirbyteSecretNotFoundError` {#airbyte.exceptions.PyAirbyteSecretNotFoundError}

<ApiMember kind="class">

<ApiSignature>

```python
class PyAirbyteSecretNotFoundError(
    guidance: str | None = None,
    help_url: str | None = None,
    log_text: str | list[str] | None = None,
    log_file: Path | None = None,
    print_full_log: bool = False,
    context: dict[str, Any] | None = None,
    message: str | None = None,
    original_exception: Exception | None = None,
    secret_name: str | None = None,
    sources: list[str] | None = None,
)
```

</ApiSignature>

Secret not found.

#### Bases {#airbyte.exceptions.PyAirbyteSecretNotFoundError--bases}

`airbyte.exceptions.PyAirbyteError`
#### Class Variables {#airbyte.exceptions.PyAirbyteSecretNotFoundError--class-variables}

- **`guidance`**&nbsp;(`str | None`)

- **`help_url`**&nbsp;(`str | None`)

#### Instance Variables {#airbyte.exceptions.PyAirbyteSecretNotFoundError--instance-variables}

- **`secret_name`**&nbsp;(`str | None`)

- **`sources`**&nbsp;(`list[str] | None`)

</ApiMember>

### `PyAirbyteWarning` {#airbyte.exceptions.PyAirbyteWarning}

<ApiMember kind="class">

<ApiSignature>

```python
class PyAirbyteWarning(*args, **kwargs)
```

</ApiSignature>

General warnings from PyAirbyte.

#### Bases {#airbyte.exceptions.PyAirbyteWarning--bases}

`builtins.Warning`
#### Descendants {#airbyte.exceptions.PyAirbyteWarning--descendants}

`airbyte.exceptions.PyAirbyteDataLossWarning`

</ApiMember>