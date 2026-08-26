---
id: airbyte-cloud-client
title: airbyte.cloud.client
---

PyAirbyte Cloud client.

### `CloudClient` {#airbyte.cloud.client.CloudClient}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudClient(
    *,
    client_id: str | SecretString | None = None,
    client_secret: str | SecretString | None = None,
    bearer_token: str | SecretString | None = None,
    public_api_root: str | None = None,
    config_api_root: str | None = None,
    workspace_id: str | None = None,
    organization_id: str | None = None,
)
```

</ApiSignature>

Authenticated client for Airbyte Cloud and self-managed Airbyte APIs.

Initialize a `CloudClient` from explicit auth values.

#### Attributes {#airbyte.cloud.client.CloudClient--attributes}

- **`bearer_token`**&nbsp;(`SecretString | None`) — Bearer token used for authentication.

- **`client_id`**&nbsp;(`SecretString | None`) — OAuth client ID used for authentication.

- **`client_secret`**&nbsp;(`SecretString | None`) — OAuth client secret used for authentication.

- **`config_api_root`**&nbsp;(`str | None`) — Airbyte Config API root.

- **`organization_id`**&nbsp;(`str | None`) — Default organization ID for organization-scoped operations.

- **`public_api_root`**&nbsp;(`str`) — Airbyte Public API root.

#### `from_auth` {#airbyte.cloud.client.CloudClient.from_auth}

<ApiMember kind="method">

<ApiSignature>

```python
def from_auth(
    *,
    env_vars: bool = False,
    organization_id: str | None = None,
    client_id: str | SecretString | None = None,
    client_secret: str | SecretString | None = None,
    bearer_token: str | SecretString | None = None,
    public_api_root: str | None = None,
    config_api_root: str | None = None,
)
```

</ApiSignature>

Create a client from explicit inputs and optionally environment variables.

When `env_vars` is True, environment variables are checked as a fallback
after any explicitly provided values.

</ApiMember>

#### `create_workspace` {#airbyte.cloud.client.CloudClient.create_workspace}

<ApiMember kind="method">

<ApiSignature>

```python
def create_workspace(
    self,
    *,
    name: str,
    organization_id: str | None = None,
    region_id: str | None = None,
) -> airbyte.cloud.models.CloudWorkspaceInfo
```

</ApiSignature>

Create an Airbyte workspace.

</ApiMember>

#### `get_organization` {#airbyte.cloud.client.CloudClient.get_organization}

<ApiMember kind="method">

<ApiSignature>

```python
def get_organization(
    self,
    organization_id: str | None = None,
    *,
    organization_name: str | None = None,
) -> airbyte.cloud.organizations.CloudOrganization
```

</ApiSignature>

Resolve an organization by ID or exact name.

</ApiMember>

#### `get_workspace` {#airbyte.cloud.client.CloudClient.get_workspace}

<ApiMember kind="method">

<ApiSignature>

```python
def get_workspace(
    self,
    workspace_id: str | None = None,
) -> airbyte.cloud.workspaces.CloudWorkspace
```

</ApiSignature>

Create a `CloudWorkspace` using this client's credentials.

</ApiMember>

#### `list_organizations` {#airbyte.cloud.client.CloudClient.list_organizations}

<ApiMember kind="method">

<ApiSignature>

```python
def list_organizations(
    self,
) -> list[airbyte.cloud.organizations.CloudOrganization]
```

</ApiSignature>

List all organizations available to this client.

</ApiMember>

#### `list_workspaces` {#airbyte.cloud.client.CloudClient.list_workspaces}

<ApiMember kind="method">

<ApiSignature>

```python
def list_workspaces(
    self,
    name: str | None = None,
    *,
    organization_id: str | None = None,
    name_contains: str | None = None,
    name_filter: Callable[[str], bool] | None = None,
    limit: int | None = None,
) -> list[CloudWorkspaceInfo]
```

</ApiSignature>

List workspaces available to this client.

</ApiMember>

#### `permanently_delete_workspace` {#airbyte.cloud.client.CloudClient.permanently_delete_workspace}

<ApiMember kind="method">

<ApiSignature>

```python
def permanently_delete_workspace(
    self,
    workspace_id: str,
    *,
    workspace_name: str | None = None,
    safe_mode: bool = True,
) -> None
```

</ApiSignature>

Permanently delete an Airbyte workspace if it has no connections.

When `safe_mode` is enabled, the workspace name must contain `delete-me`
or `deleteme`. This also checks for existing connections before deleting
and raises `AirbyteWorkspaceNotEmptyError` if the workspace is not empty.

</ApiMember>

#### `rename_workspace` {#airbyte.cloud.client.CloudClient.rename_workspace}

<ApiMember kind="method">

<ApiSignature>

```python
def rename_workspace(
    self,
    workspace_id: str,
    *,
    name: str,
) -> airbyte.cloud.models.CloudWorkspaceInfo
```

</ApiSignature>

Rename an Airbyte workspace.

</ApiMember>

</ApiMember>