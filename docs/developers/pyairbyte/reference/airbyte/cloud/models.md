---
id: airbyte-cloud-models
title: "airbyte.cloud.models Module"
sidebar_label: "airbyte.cloud.models"
---

# `airbyte.cloud.models` Module

Public response models for Airbyte Cloud APIs.

### `CloudConnectionInfo` {#airbyte.cloud.models.CloudConnectionInfo}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudConnectionInfo(**data: Any)
```

</ApiSignature>

Information about an Airbyte Cloud connection.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Attributes {#airbyte.cloud.models.CloudConnectionInfo--attributes}

- **`configurations`**&nbsp;(`Any`)

  Stream configuration details for the connection.

- **`connection_id`**&nbsp;(`str`)

  The connection ID.

- **`destination_id`**&nbsp;(`str`)

  The destination ID.

- **`name`**&nbsp;(`str`)

  The connection name.

- **`prefix`**&nbsp;(`str | None`)

  The destination table prefix.

- **`source_id`**&nbsp;(`str`)

  The source ID.

- **`status`**&nbsp;(`str`)

  The connection status.

- **`workspace_id`**&nbsp;(`str`)

  The workspace ID.

#### `from_api_response` {#airbyte.cloud.models.CloudConnectionInfo.from_api_response}

<ApiMember kind="method">

<ApiSignature>

```python
def from_api_response(
    connection: _ConnectionResponseLike,
) -> airbyte.cloud.models.CloudConnectionInfo
```

</ApiSignature>

Create a public model from an internal API connection response.

</ApiMember>

</ApiMember>

### `CloudCustomSourceDefinitionInfo` {#airbyte.cloud.models.CloudCustomSourceDefinitionInfo}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudCustomSourceDefinitionInfo(**data: Any)
```

</ApiSignature>

Information about a custom Airbyte Cloud source definition.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Attributes {#airbyte.cloud.models.CloudCustomSourceDefinitionInfo--attributes}

- **`definition_id`**&nbsp;(`str`)

  The source definition ID.

- **`manifest`**&nbsp;(`dict[str, typing.Any] | None`)

  The source definition manifest.

- **`name`**&nbsp;(`str`)

  The source definition name.

- **`version`**&nbsp;(`str`)

  The source definition version.

#### `from_api_response` {#airbyte.cloud.models.CloudCustomSourceDefinitionInfo.from_api_response}

<ApiMember kind="method">

<ApiSignature>

```python
def from_api_response(
    definition: _DeclarativeSourceDefinitionResponseLike,
) -> airbyte.cloud.models.CloudCustomSourceDefinitionInfo
```

</ApiSignature>

Create a public model from an internal API source definition response.

</ApiMember>

</ApiMember>

### `CloudDestinationInfo` {#airbyte.cloud.models.CloudDestinationInfo}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudDestinationInfo(**data: Any)
```

</ApiSignature>

Information about an Airbyte Cloud destination.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Attributes {#airbyte.cloud.models.CloudDestinationInfo--attributes}

- **`definition_id`**&nbsp;(`str`)

  The connector definition ID (for example, the ID for `destination-snowflake`).

- **`destination_id`**&nbsp;(`str`)

  The destination ID.

- **`name`**&nbsp;(`str`)

  The destination name.

#### `from_api_response` {#airbyte.cloud.models.CloudDestinationInfo.from_api_response}

<ApiMember kind="method">

<ApiSignature>

```python
def from_api_response(
    destination: _DestinationResponseLike,
) -> airbyte.cloud.models.CloudDestinationInfo
```

</ApiSignature>

Create a public model from an internal API destination response.

</ApiMember>

</ApiMember>

### `CloudJobInfo` {#airbyte.cloud.models.CloudJobInfo}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudJobInfo(**data: Any)
```

</ApiSignature>

Information about an Airbyte Cloud job.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Attributes {#airbyte.cloud.models.CloudJobInfo--attributes}

- **`bytes_synced`**&nbsp;(`int | None`)

  The number of bytes synced by the job, if available.

- **`job_id`**&nbsp;(`int`)

  The job ID.

- **`rows_synced`**&nbsp;(`int | None`)

  The number of rows synced by the job, if available.

- **`start_time`**&nbsp;(`str`)

  The job start time.

- **`status`**&nbsp;(`airbyte.cloud.models.JobStatusEnum`)

  The job status.

#### `from_api_response` {#airbyte.cloud.models.CloudJobInfo.from_api_response}

<ApiMember kind="method">

<ApiSignature>

```python
def from_api_response(
    job: _JobResponseLike,
) -> airbyte.cloud.models.CloudJobInfo
```

</ApiSignature>

Create a public model from an internal API job response.

</ApiMember>

</ApiMember>

### `CloudSourceInfo` {#airbyte.cloud.models.CloudSourceInfo}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudSourceInfo(**data: Any)
```

</ApiSignature>

Information about an Airbyte Cloud source.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Attributes {#airbyte.cloud.models.CloudSourceInfo--attributes}

- **`definition_id`**&nbsp;(`str`)

  The connector definition ID (for example, the ID for `source-postgres`).

- **`name`**&nbsp;(`str`)

  The source name.

- **`source_id`**&nbsp;(`str`)

  The source ID.

#### `from_api_response` {#airbyte.cloud.models.CloudSourceInfo.from_api_response}

<ApiMember kind="method">

<ApiSignature>

```python
def from_api_response(
    source: _SourceResponseLike,
) -> airbyte.cloud.models.CloudSourceInfo
```

</ApiSignature>

Create a public model from an internal API source response.

</ApiMember>

</ApiMember>

### `CloudWorkspaceInfo` {#airbyte.cloud.models.CloudWorkspaceInfo}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudWorkspaceInfo(**data: Any)
```

</ApiSignature>

Information about an Airbyte workspace.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Attributes {#airbyte.cloud.models.CloudWorkspaceInfo--attributes}

- **`data_residency`**&nbsp;(`str | None`)

  The data residency setting for the workspace, if available.

- **`name`**&nbsp;(`str`)

  The workspace name.

- **`notifications`**&nbsp;(`dict[str, object | None] | list[dict[str, object | None]]`)

  Workspace notification settings.

- **`organization_id`**&nbsp;(`str | None`)

  The organization ID for the workspace, if available.

- **`workspace_id`**&nbsp;(`str`)

  The workspace ID.

#### `from_api_response` {#airbyte.cloud.models.CloudWorkspaceInfo.from_api_response}

<ApiMember kind="method">

<ApiSignature>

```python
def from_api_response(
    workspace: _WorkspaceResponseLike,
) -> airbyte.cloud.models.CloudWorkspaceInfo
```

</ApiSignature>

Create a public model from an internal API workspace response.

</ApiMember>

#### `from_mapping` {#airbyte.cloud.models.CloudWorkspaceInfo.from_mapping}

<ApiMember kind="method">

<ApiSignature>

```python
def from_mapping(
    workspace: Mapping[str, object],
) -> airbyte.cloud.models.CloudWorkspaceInfo
```

</ApiSignature>

Create a public model from a workspace mapping.

</ApiMember>

#### `to_dict` {#airbyte.cloud.models.CloudWorkspaceInfo.to_dict}

<ApiMember kind="method">

<ApiSignature>

```python
def to_dict(self) -> dict[str, object]
```

</ApiSignature>

Return a JSON-serializable dictionary.

</ApiMember>

</ApiMember>

### `JobStatusEnum` {#airbyte.cloud.models.JobStatusEnum}

<ApiMember kind="class">

<ApiSignature>

```python
class JobStatusEnum(
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

Status values for an Airbyte Cloud job.

**Bases:** `builtins.str`, `enum.Enum`

#### Attributes {#airbyte.cloud.models.JobStatusEnum--attributes}

- **`CANCELLED`**

- **`FAILED`**

- **`INCOMPLETE`**

- **`PENDING`**

- **`RUNNING`**

- **`SUCCEEDED`**

</ApiMember>

### `JobTypeEnum` {#airbyte.cloud.models.JobTypeEnum}

<ApiMember kind="class">

<ApiSignature>

```python
class JobTypeEnum(
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

Job type values for Airbyte Cloud jobs.

**Bases:** `builtins.str`, `enum.Enum`

#### Attributes {#airbyte.cloud.models.JobTypeEnum--attributes}

- **`CLEAR`**

- **`REFRESH`**

- **`RESET`**

- **`SYNC`**

</ApiMember>