---
sidebar_label: cloud_ops
title: airbyte.mcp.cloud_ops
---

Airbyte Cloud MCP operations.

## Path

## Annotated

## Any

## Literal

## cast

## FastMCP

## BaseModel

## Field

## cloud

## get\_destination

## get\_source

## api\_util

## CustomCloudSourceDefinition

## FAILED\_STATUSES

## CloudWorkspace

## get\_noop\_destination

## AirbyteMissingResourceError

## PyAirbyteInputError

## check\_guid\_created\_in\_session

## mcp\_tool

## register\_guid\_created\_in\_session

## register\_tools

## resolve\_cloud\_credentials

## resolve\_config

## resolve\_list\_of\_strings

## resolve\_workspace\_id

## SecretString

#### CLOUD\_AUTH\_TIP\_TEXT

#### WORKSPACE\_ID\_TIP\_TEXT

## CloudSourceResult Objects

```python
class CloudSourceResult(BaseModel)
```

Information about a deployed source connector in Airbyte Cloud.

#### id

The source ID.

#### name

Display name of the source.

#### url

Web URL for managing this source in Airbyte Cloud.

## CloudDestinationResult Objects

```python
class CloudDestinationResult(BaseModel)
```

Information about a deployed destination connector in Airbyte Cloud.

#### id

The destination ID.

#### name

Display name of the destination.

#### url

Web URL for managing this destination in Airbyte Cloud.

## CloudConnectionResult Objects

```python
class CloudConnectionResult(BaseModel)
```

Information about a deployed connection in Airbyte Cloud.

#### id

The connection ID.

#### name

Display name of the connection.

#### url

Web URL for managing this connection in Airbyte Cloud.

#### source\_id

ID of the source used by this connection.

#### destination\_id

ID of the destination used by this connection.

#### last\_job\_status

Status of the most recent completed sync job (e.g., &#x27;succeeded&#x27;, &#x27;failed&#x27;, &#x27;cancelled&#x27;).
Only populated when with_connection_status=True.

#### last\_job\_id

Job ID of the most recent completed sync. Only populated when with_connection_status=True.

#### last\_job\_time

ISO 8601 timestamp of the most recent completed sync.
Only populated when with_connection_status=True.

#### currently\_running\_job\_id

Job ID of a currently running sync, if any.
Only populated when with_connection_status=True.

#### currently\_running\_job\_start\_time

ISO 8601 timestamp of when the currently running sync started.
Only populated when with_connection_status=True.

## CloudSourceDetails Objects

```python
class CloudSourceDetails(BaseModel)
```

Detailed information about a deployed source connector in Airbyte Cloud.

#### source\_id

The source ID.

#### source\_name

Display name of the source.

#### source\_url

Web URL for managing this source in Airbyte Cloud.

#### connector\_definition\_id

The connector definition ID (e.g., the ID for &#x27;source-postgres&#x27;).

## CloudDestinationDetails Objects

```python
class CloudDestinationDetails(BaseModel)
```

Detailed information about a deployed destination connector in Airbyte Cloud.

#### destination\_id

The destination ID.

#### destination\_name

Display name of the destination.

#### destination\_url

Web URL for managing this destination in Airbyte Cloud.

#### connector\_definition\_id

The connector definition ID (e.g., the ID for &#x27;destination-snowflake&#x27;).

## CloudConnectionDetails Objects

```python
class CloudConnectionDetails(BaseModel)
```

Detailed information about a deployed connection in Airbyte Cloud.

#### connection\_id

The connection ID.

#### connection\_name

Display name of the connection.

#### connection\_url

Web URL for managing this connection in Airbyte Cloud.

#### source\_id

ID of the source used by this connection.

#### source\_name

Display name of the source.

#### destination\_id

ID of the destination used by this connection.

#### destination\_name

Display name of the destination.

#### selected\_streams

List of stream names selected for syncing.

#### table\_prefix

Table prefix applied when syncing to the destination.

## CloudOrganizationResult Objects

```python
class CloudOrganizationResult(BaseModel)
```

Information about an organization in Airbyte Cloud.

#### id

The organization ID.

#### name

Display name of the organization.

#### email

Email associated with the organization.

## CloudWorkspaceResult Objects

```python
class CloudWorkspaceResult(BaseModel)
```

Information about a workspace in Airbyte Cloud.

#### workspace\_id

The workspace ID.

#### workspace\_name

Display name of the workspace.

#### workspace\_url

URL to access the workspace in Airbyte Cloud.

#### organization\_id

ID of the organization (requires ORGANIZATION_READER permission).

#### organization\_name

Name of the organization (requires ORGANIZATION_READER permission).

## LogReadResult Objects

```python
class LogReadResult(BaseModel)
```

Result of reading sync logs with pagination support.

#### job\_id

The job ID the logs belong to.

#### attempt\_number

The attempt number the logs belong to.

#### log\_text

The string containing the log text we are returning.

#### log\_text\_start\_line

1-based line index of the first line returned.

#### log\_text\_line\_count

Count of lines we are returning.

#### total\_log\_lines\_available

Total number of log lines available, shows if any lines were missed due to the limit.

## SyncJobResult Objects

```python
class SyncJobResult(BaseModel)
```

Information about a sync job.

#### job\_id

The job ID.

#### status

The job status (e.g., &#x27;succeeded&#x27;, &#x27;failed&#x27;, &#x27;running&#x27;, &#x27;pending&#x27;).

#### bytes\_synced

Number of bytes synced in this job.

#### records\_synced

Number of records synced in this job.

#### start\_time

ISO 8601 timestamp of when the job started.

#### job\_url

URL to view the job in Airbyte Cloud.

## SyncJobListResult Objects

```python
class SyncJobListResult(BaseModel)
```

Result of listing sync jobs with pagination support.

#### jobs

List of sync jobs.

#### jobs\_count

Number of jobs returned in this response.

#### jobs\_offset

Offset used for this request (0 if not specified).

#### from\_tail

Whether jobs are ordered newest-first (True) or oldest-first (False).

#### \_get\_cloud\_workspace

```python
def _get_cloud_workspace(workspace_id: str | None = None) -> CloudWorkspace
```

Get an authenticated CloudWorkspace.

Resolves credentials from multiple sources in order:
1. HTTP headers (when running as MCP server with HTTP/SSE transport)
2. Environment variables

**Arguments**:

- `workspace_id` - Optional workspace ID. If not provided, uses HTTP headers
  or the AIRBYTE_CLOUD_WORKSPACE_ID environment variable.

#### deploy\_source\_to\_cloud

```python
@mcp_tool(
    domain="cloud",
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def deploy_source_to_cloud(source_name: Annotated[
    str,
    Field(description="The name to use when deploying the source."),
], source_connector_name: Annotated[
    str,
    Field(
        description="The name of the source connector (e.g., 'source-faker')."
    ),
], *, workspace_id: Annotated[
    str | None,
    Field(
        description=WORKSPACE_ID_TIP_TEXT,
        default=None,
    ),
], config: Annotated[
    dict | str | None,
    Field(
        description="The configuration for the source connector.",
        default=None,
    ),
], config_secret_name: Annotated[
    str | None,
    Field(
        description="The name of the secret containing the configuration.",
        default=None,
    ),
], unique: Annotated[
    bool,
    Field(
        description="Whether to require a unique name.",
        default=True,
    ),
]) -> str
```

Deploy a source connector to Airbyte Cloud.

#### deploy\_destination\_to\_cloud

```python
@mcp_tool(
    domain="cloud",
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def deploy_destination_to_cloud(destination_name: Annotated[
    str,
    Field(description="The name to use when deploying the destination."),
], destination_connector_name: Annotated[
    str,
    Field(
        description=
        "The name of the destination connector (e.g., 'destination-postgres')."
    ),
], *, workspace_id: Annotated[
    str | None,
    Field(
        description=WORKSPACE_ID_TIP_TEXT,
        default=None,
    ),
], config: Annotated[
    dict | str | None,
    Field(
        description="The configuration for the destination connector.",
        default=None,
    ),
], config_secret_name: Annotated[
    str | None,
    Field(
        description="The name of the secret containing the configuration.",
        default=None,
    ),
], unique: Annotated[
    bool,
    Field(
        description="Whether to require a unique name.",
        default=True,
    ),
]) -> str
```

Deploy a destination connector to Airbyte Cloud.

#### create\_connection\_on\_cloud

```python
@mcp_tool(
    domain="cloud",
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def create_connection_on_cloud(
    connection_name: Annotated[
        str,
        Field(description="The name of the connection."),
    ], source_id: Annotated[
        str,
        Field(description="The ID of the deployed source."),
    ], destination_id: Annotated[
        str,
        Field(description="The ID of the deployed destination."),
    ], selected_streams: Annotated[
        str | list[str],
        Field(description=(
            "The selected stream names to sync within the connection. "
            "Must be an explicit stream name or list of streams. "
            "Cannot be empty or '*'.")),
    ], *, workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ], table_prefix: Annotated[
        str | None,
        Field(
            description=
            "Optional table prefix to use when syncing to the destination.",
            default=None,
        ),
    ]
) -> str
```

Create a connection between a deployed source and destination on Airbyte Cloud.

#### run\_cloud\_sync

```python
@mcp_tool(
    domain="cloud",
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def run_cloud_sync(connection_id: Annotated[
    str,
    Field(description="The ID of the Airbyte Cloud connection."),
], *, workspace_id: Annotated[
    str | None,
    Field(
        description=WORKSPACE_ID_TIP_TEXT,
        default=None,
    ),
], wait: Annotated[
    bool,
    Field(
        description=
        ("Whether to wait for the sync to complete. Since a sync can take between several "
         "minutes and several hours, this option is not recommended for most "
         "scenarios."),
        default=False,
    ),
], wait_timeout: Annotated[
    int,
    Field(
        description="Maximum time to wait for sync completion (seconds).",
        default=300,
    ),
]) -> str
```

Run a sync job on Airbyte Cloud.

#### check\_airbyte\_cloud\_workspace

```python
@mcp_tool(
    domain="cloud",
    read_only=True,
    idempotent=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def check_airbyte_cloud_workspace(
    *, workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ]
) -> CloudWorkspaceResult
```

Check if we have a valid Airbyte Cloud connection and return workspace info.

Returns workspace details including workspace ID, name, and organization info.

#### deploy\_noop\_destination\_to\_cloud

```python
@mcp_tool(
    domain="cloud",
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def deploy_noop_destination_to_cloud(name: str = "No-op Destination",
                                     *,
                                     workspace_id: Annotated[
                                         str | None,
                                         Field(
                                             description=WORKSPACE_ID_TIP_TEXT,
                                             default=None,
                                         ),
                                     ],
                                     unique: bool = True) -> str
```

Deploy the No-op destination to Airbyte Cloud for testing purposes.

#### get\_cloud\_sync\_status

```python
@mcp_tool(
    domain="cloud",
    read_only=True,
    idempotent=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def get_cloud_sync_status(
    connection_id: Annotated[
        str,
        Field(description="The ID of the Airbyte Cloud connection.", ),
    ], job_id: Annotated[
        int | None,
        Field(
            description=
            "Optional job ID. If not provided, the latest job will be used.",
            default=None,
        ),
    ], *, workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ], include_attempts: Annotated[
        bool,
        Field(
            description="Whether to include detailed attempts information.",
            default=False,
        ),
    ]
) -> dict[str, Any]
```

Get the status of a sync job from the Airbyte Cloud.

#### list\_cloud\_sync\_jobs

```python
@mcp_tool(
    domain="cloud",
    read_only=True,
    idempotent=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def list_cloud_sync_jobs(
    connection_id: Annotated[
        str,
        Field(description="The ID of the Airbyte Cloud connection."),
    ], *, workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ], max_jobs: Annotated[
        int,
        Field(
            description=("Maximum number of jobs to return. "
                         "Defaults to 20 if not specified. "
                         "Maximum allowed value is 500."),
            default=20,
        ),
    ], from_tail: Annotated[
        bool | None,
        Field(
            description=(
                "When True, jobs are ordered newest-first (createdAt DESC). "
                "When False, jobs are ordered oldest-first (createdAt ASC). "
                "Defaults to True if `jobs_offset` is not specified. "
                "Cannot combine `from_tail=True` with `jobs_offset`."),
            default=None,
        ),
    ], jobs_offset: Annotated[
        int | None,
        Field(
            description=("Number of jobs to skip from the beginning. "
                         "Cannot be combined with `from_tail=True`."),
            default=None,
        ),
    ]
) -> SyncJobListResult
```

List sync jobs for a connection with pagination support.

This tool allows you to retrieve a list of sync jobs for a connection,
with control over ordering and pagination. By default, jobs are returned
newest-first (from_tail=True).

#### list\_deployed\_cloud\_source\_connectors

```python
@mcp_tool(
    domain="cloud",
    read_only=True,
    idempotent=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def list_deployed_cloud_source_connectors(
    *, workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ], name_contains: Annotated[
        str | None,
        Field(
            description=
            "Optional case-insensitive substring to filter sources by name",
            default=None,
        ),
    ], max_items_limit: Annotated[
        int | None,
        Field(
            description=
            "Optional maximum number of items to return (default: no limit)",
            default=None,
        ),
    ]
) -> list[CloudSourceResult]
```

List all deployed source connectors in the Airbyte Cloud workspace.

#### list\_deployed\_cloud\_destination\_connectors

```python
@mcp_tool(
    domain="cloud",
    read_only=True,
    idempotent=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def list_deployed_cloud_destination_connectors(*, workspace_id: Annotated[
    str | None,
    Field(
        description=WORKSPACE_ID_TIP_TEXT,
        default=None,
    ),
], name_contains: Annotated[
    str | None,
    Field(
        description=
        "Optional case-insensitive substring to filter destinations by name",
        default=None,
    ),
], max_items_limit: Annotated[
    int | None,
    Field(
        description=
        "Optional maximum number of items to return (default: no limit)",
        default=None,
    ),
]) -> list[CloudDestinationResult]
```

List all deployed destination connectors in the Airbyte Cloud workspace.

#### describe\_cloud\_source

```python
@mcp_tool(
    domain="cloud",
    read_only=True,
    idempotent=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def describe_cloud_source(
    source_id: Annotated[
        str,
        Field(description="The ID of the source to describe."),
    ], *, workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ]
) -> CloudSourceDetails
```

Get detailed information about a specific deployed source connector.

#### describe\_cloud\_destination

```python
@mcp_tool(
    domain="cloud",
    read_only=True,
    idempotent=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def describe_cloud_destination(
    destination_id: Annotated[
        str,
        Field(description="The ID of the destination to describe."),
    ], *, workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ]
) -> CloudDestinationDetails
```

Get detailed information about a specific deployed destination connector.

#### describe\_cloud\_connection

```python
@mcp_tool(
    domain="cloud",
    read_only=True,
    idempotent=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def describe_cloud_connection(
    connection_id: Annotated[
        str,
        Field(description="The ID of the connection to describe."),
    ], *, workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ]
) -> CloudConnectionDetails
```

Get detailed information about a specific deployed connection.

#### get\_cloud\_sync\_logs

```python
@mcp_tool(
    domain="cloud",
    read_only=True,
    idempotent=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def get_cloud_sync_logs(
    connection_id: Annotated[
        str,
        Field(description="The ID of the Airbyte Cloud connection."),
    ],
    job_id: Annotated[
        int | None,
        Field(
            description=
            "Optional job ID. If not provided, the latest job will be used."),
    ] = None,
    attempt_number: Annotated[
        int | None,
        Field(
            description=
            "Optional attempt number. If not provided, the latest attempt will be used."
        ),
    ] = None,
    *,
    workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ],
    max_lines: Annotated[
        int,
        Field(
            description=("Maximum number of lines to return. "
                         "Defaults to 4000 if not specified. "
                         "If '0' is provided, no limit is applied."),
            default=4000,
        ),
    ],
    from_tail: Annotated[
        bool | None,
        Field(
            description=
            ("Pull from the end of the log text if total lines is greater than 'max_lines'. "
             "Defaults to True if `line_offset` is not specified. "
             "Cannot combine `from_tail=True` with `line_offset`."),
            default=None,
        ),
    ],
    line_offset: Annotated[
        int | None,
        Field(
            description=(
                "Number of lines to skip from the beginning of the logs. "
                "Cannot be combined with `from_tail=True`."),
            default=None,
        ),
    ]
) -> LogReadResult
```

Get the logs from a sync job attempt on Airbyte Cloud.

#### list\_deployed\_cloud\_connections

```python
@mcp_tool(
    domain="cloud",
    read_only=True,
    idempotent=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def list_deployed_cloud_connections(*, workspace_id: Annotated[
    str | None,
    Field(
        description=WORKSPACE_ID_TIP_TEXT,
        default=None,
    ),
], name_contains: Annotated[
    str | None,
    Field(
        description=
        "Optional case-insensitive substring to filter connections by name",
        default=None,
    ),
], max_items_limit: Annotated[
    int | None,
    Field(
        description=
        "Optional maximum number of items to return (default: no limit)",
        default=None,
    ),
], with_connection_status: Annotated[
    bool | None,
    Field(
        description=
        "If True, include status info for each connection's most recent sync job",
        default=False,
    ),
], failing_connections_only: Annotated[
    bool | None,
    Field(
        description=
        "If True, only return connections with failed/cancelled last sync",
        default=False,
    ),
]) -> list[CloudConnectionResult]
```

List all deployed connections in the Airbyte Cloud workspace.

When with_connection_status is True, each connection result will include
information about the most recent sync job status, skipping over any
currently in-progress syncs to find the last completed job.

When failing_connections_only is True, only connections where the most
recent completed sync job failed or was cancelled will be returned.
This implicitly enables with_connection_status.

#### \_resolve\_organization

```python
def _resolve_organization(
    organization_id: str | None,
    organization_name: str | None,
    *,
    api_root: str,
    client_id: SecretString | None,
    client_secret: SecretString | None,
    bearer_token: SecretString | None = None
) -> api_util.models.OrganizationResponse
```

Resolve organization from either ID or exact name match.

**Arguments**:

- `organization_id` - The organization ID (if provided directly)
- `organization_name` - The organization name (exact match required)
- `api_root` - The API root URL
- `client_id` - OAuth client ID (optional if bearer_token is provided)
- `client_secret` - OAuth client secret (optional if bearer_token is provided)
- `bearer_token` - Bearer token for authentication (optional if client credentials provided)
  

**Returns**:

  The resolved OrganizationResponse object
  

**Raises**:

- `PyAirbyteInputError` - If neither or both parameters are provided,
  or if no organization matches the exact name
- `AirbyteMissingResourceError` - If the organization is not found

#### \_resolve\_organization\_id

```python
def _resolve_organization_id(organization_id: str | None,
                             organization_name: str | None,
                             *,
                             api_root: str,
                             client_id: SecretString | None,
                             client_secret: SecretString | None,
                             bearer_token: SecretString | None = None) -> str
```

Resolve organization ID from either ID or exact name match.

This is a convenience wrapper around _resolve_organization that returns just the ID.

#### list\_cloud\_workspaces

```python
@mcp_tool(
    domain="cloud",
    read_only=True,
    idempotent=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def list_cloud_workspaces(*, organization_id: Annotated[
    str | None,
    Field(
        description=
        "Organization ID. Required if organization_name is not provided.",
        default=None,
    ),
], organization_name: Annotated[
    str | None,
    Field(
        description=("Organization name (exact match). "
                     "Required if organization_id is not provided."),
        default=None,
    ),
], name_contains: Annotated[
    str | None,
    Field(
        description=
        "Optional substring to filter workspaces by name (server-side filtering)",
        default=None,
    ),
], max_items_limit: Annotated[
    int | None,
    Field(
        description=
        "Optional maximum number of items to return (default: no limit)",
        default=None,
    ),
]) -> list[CloudWorkspaceResult]
```

List all workspaces in a specific organization.

Requires either organization_id OR organization_name (exact match) to be provided.
This tool will NOT list workspaces across all organizations - you must specify
which organization to list workspaces from.

#### describe\_cloud\_organization

```python
@mcp_tool(
    domain="cloud",
    read_only=True,
    idempotent=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def describe_cloud_organization(
    *, organization_id: Annotated[
        str | None,
        Field(
            description=
            "Organization ID. Required if organization_name is not provided.",
            default=None,
        ),
    ], organization_name: Annotated[
        str | None,
        Field(
            description=("Organization name (exact match). "
                         "Required if organization_id is not provided."),
            default=None,
        ),
    ]
) -> CloudOrganizationResult
```

Get details about a specific organization.

Requires either organization_id OR organization_name (exact match) to be provided.
This tool is useful for looking up an organization&#x27;s ID from its name, or vice versa.

#### \_get\_custom\_source\_definition\_description

```python
def _get_custom_source_definition_description(
        custom_source: CustomCloudSourceDefinition) -> str
```

#### publish\_custom\_source\_definition

```python
@mcp_tool(
    domain="cloud",
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def publish_custom_source_definition(
    name: Annotated[
        str,
        Field(description="The name for the custom connector definition."),
    ],
    *,
    workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ],
    manifest_yaml: Annotated[
        str | Path | None,
        Field(
            description=(
                "The Low-code CDK manifest as a YAML string or file path. "
                "Required for YAML connectors."),
            default=None,
        ),
    ] = None,
    unique: Annotated[
        bool,
        Field(
            description="Whether to require a unique name.",
            default=True,
        ),
    ] = True,
    pre_validate: Annotated[
        bool,
        Field(
            description=
            "Whether to validate the manifest client-side before publishing.",
            default=True,
        ),
    ] = True,
    testing_values: Annotated[
        dict | str | None,
        Field(
            description=
            ("Optional testing configuration values for the Builder UI. "
             "Can be provided as a JSON object or JSON string. "
             "Supports inline secret refs via 'secret_reference::ENV_VAR_NAME' syntax. "
             "If provided, these values replace any existing testing values "
             "for the connector builder project, allowing immediate test read operations."
             ),
            default=None,
        ),
    ],
    testing_values_secret_name: Annotated[
        str | None,
        Field(
            description=
            ("Optional name of a secret containing testing configuration values "
             "in JSON or YAML format. The secret will be resolved by the MCP "
             "server and merged into testing_values, with secret values taking "
             "precedence. This lets the agent reference secrets without sending "
             "raw values as tool arguments."),
            default=None,
        ),
    ]
) -> str
```

Publish a custom YAML source connector definition to Airbyte Cloud.

Note: Only YAML (declarative) connectors are currently supported.
Docker-based custom sources are not yet available.

#### list\_custom\_source\_definitions

```python
@mcp_tool(
    domain="cloud",
    read_only=True,
    idempotent=True,
    open_world=True,
)
def list_custom_source_definitions(
    *, workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ]
) -> list[dict[str, Any]]
```

List custom YAML source definitions in the Airbyte Cloud workspace.

Note: Only YAML (declarative) connectors are currently supported.
Docker-based custom sources are not yet available.

#### update\_custom\_source\_definition

```python
@mcp_tool(
    domain="cloud",
    destructive=True,
    open_world=True,
)
def update_custom_source_definition(
    definition_id: Annotated[
        str,
        Field(description="The ID of the definition to update."),
    ],
    manifest_yaml: Annotated[
        str | Path | None,
        Field(
            description=("New manifest as YAML string or file path. "
                         "Optional; omit to update only testing values."),
            default=None,
        ),
    ] = None,
    *,
    workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ],
    pre_validate: Annotated[
        bool,
        Field(
            description=
            "Whether to validate the manifest client-side before updating.",
            default=True,
        ),
    ] = True,
    testing_values: Annotated[
        dict | str | None,
        Field(
            description=
            ("Optional testing configuration values for the Builder UI. "
             "Can be provided as a JSON object or JSON string. "
             "Supports inline secret refs via 'secret_reference::ENV_VAR_NAME' syntax. "
             "If provided, these values replace any existing testing values "
             "for the connector builder project. The entire testing values object "
             "is overwritten, so pass the full set of values you want to persist."
             ),
            default=None,
        ),
    ],
    testing_values_secret_name: Annotated[
        str | None,
        Field(
            description=
            ("Optional name of a secret containing testing configuration values "
             "in JSON or YAML format. The secret will be resolved by the MCP "
             "server and merged into testing_values, with secret values taking "
             "precedence. This lets the agent reference secrets without sending "
             "raw values as tool arguments."),
            default=None,
        ),
    ]
) -> str
```

Update a custom YAML source definition in Airbyte Cloud.

Updates the manifest and/or testing values for an existing custom source definition.
At least one of manifest_yaml, testing_values, or testing_values_secret_name must be provided.

#### permanently\_delete\_custom\_source\_definition

```python
@mcp_tool(
    domain="cloud",
    destructive=True,
    open_world=True,
)
def permanently_delete_custom_source_definition(definition_id: Annotated[
    str,
    Field(description="The ID of the custom source definition to delete."),
], name: Annotated[
    str,
    Field(
        description=
        "The expected name of the custom source definition (for verification)."
    ),
], *, workspace_id: Annotated[
    str | None,
    Field(
        description=WORKSPACE_ID_TIP_TEXT,
        default=None,
    ),
]) -> str
```

Permanently delete a custom YAML source definition from Airbyte Cloud.

IMPORTANT: This operation requires the connector name to contain &quot;delete-me&quot; or &quot;deleteme&quot;
(case insensitive).

If the connector does not meet this requirement, the deletion will be rejected with a
helpful error message. Instruct the user to rename the connector appropriately to authorize
the deletion.

The provided name must match the actual name of the definition for the operation to proceed.
This is a safety measure to ensure you are deleting the correct resource.

Note: Only YAML (declarative) connectors are currently supported.
Docker-based custom sources are not yet available.

#### permanently\_delete\_cloud\_source

```python
@mcp_tool(
    domain="cloud",
    destructive=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def permanently_delete_cloud_source(
    source_id: Annotated[
        str,
        Field(description="The ID of the deployed source to delete."),
    ], name: Annotated[
        str,
        Field(
            description="The expected name of the source (for verification)."),
    ]
) -> str
```

Permanently delete a deployed source connector from Airbyte Cloud.

IMPORTANT: This operation requires the source name to contain &quot;delete-me&quot; or &quot;deleteme&quot;
(case insensitive).

If the source does not meet this requirement, the deletion will be rejected with a
helpful error message. Instruct the user to rename the source appropriately to authorize
the deletion.

The provided name must match the actual name of the source for the operation to proceed.
This is a safety measure to ensure you are deleting the correct resource.

#### permanently\_delete\_cloud\_destination

```python
@mcp_tool(
    domain="cloud",
    destructive=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def permanently_delete_cloud_destination(destination_id: Annotated[
    str,
    Field(description="The ID of the deployed destination to delete."),
], name: Annotated[
    str,
    Field(
        description="The expected name of the destination (for verification)."
    ),
]) -> str
```

Permanently delete a deployed destination connector from Airbyte Cloud.

IMPORTANT: This operation requires the destination name to contain &quot;delete-me&quot; or &quot;deleteme&quot;
(case insensitive).

If the destination does not meet this requirement, the deletion will be rejected with a
helpful error message. Instruct the user to rename the destination appropriately to authorize
the deletion.

The provided name must match the actual name of the destination for the operation to proceed.
This is a safety measure to ensure you are deleting the correct resource.

#### permanently\_delete\_cloud\_connection

```python
@mcp_tool(
    domain="cloud",
    destructive=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def permanently_delete_cloud_connection(
    connection_id: Annotated[
        str,
        Field(description="The ID of the connection to delete."),
    ],
    name: Annotated[
        str,
        Field(description=
              "The expected name of the connection (for verification)."),
    ],
    *,
    cascade_delete_source: Annotated[
        bool,
        Field(
            description=
            ("Whether to also delete the source connector associated with this connection."
             ),
            default=False,
        ),
    ] = False,
    cascade_delete_destination: Annotated[
        bool,
        Field(
            description=
            ("Whether to also delete the destination connector associated with this connection."
             ),
            default=False,
        ),
    ] = False
) -> str
```

Permanently delete a connection from Airbyte Cloud.

IMPORTANT: This operation requires the connection name to contain &quot;delete-me&quot; or &quot;deleteme&quot;
(case insensitive).

If the connection does not meet this requirement, the deletion will be rejected with a
helpful error message. Instruct the user to rename the connection appropriately to authorize
the deletion.

The provided name must match the actual name of the connection for the operation to proceed.
This is a safety measure to ensure you are deleting the correct resource.

#### rename\_cloud\_source

```python
@mcp_tool(
    domain="cloud",
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def rename_cloud_source(
    source_id: Annotated[
        str,
        Field(description="The ID of the deployed source to rename."),
    ], name: Annotated[
        str,
        Field(description="New name for the source."),
    ], *, workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ]
) -> str
```

Rename a deployed source connector on Airbyte Cloud.

#### update\_cloud\_source\_config

```python
@mcp_tool(
    domain="cloud",
    destructive=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def update_cloud_source_config(
    source_id: Annotated[
        str,
        Field(description="The ID of the deployed source to update."),
    ],
    config: Annotated[
        dict | str,
        Field(description="New configuration for the source connector.", ),
    ],
    config_secret_name: Annotated[
        str | None,
        Field(
            description="The name of the secret containing the configuration.",
            default=None,
        ),
    ] = None,
    *,
    workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ]
) -> str
```

Update a deployed source connector&#x27;s configuration on Airbyte Cloud.

This is a destructive operation that can break existing connections if the
configuration is changed incorrectly. Use with caution.

#### rename\_cloud\_destination

```python
@mcp_tool(
    domain="cloud",
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def rename_cloud_destination(
    destination_id: Annotated[
        str,
        Field(description="The ID of the deployed destination to rename."),
    ], name: Annotated[
        str,
        Field(description="New name for the destination."),
    ], *, workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ]
) -> str
```

Rename a deployed destination connector on Airbyte Cloud.

#### update\_cloud\_destination\_config

```python
@mcp_tool(
    domain="cloud",
    destructive=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def update_cloud_destination_config(destination_id: Annotated[
    str,
    Field(description="The ID of the deployed destination to update."),
], config: Annotated[
    dict | str,
    Field(description="New configuration for the destination connector.", ),
], config_secret_name: Annotated[
    str | None,
    Field(
        description="The name of the secret containing the configuration.",
        default=None,
    ),
], *, workspace_id: Annotated[
    str | None,
    Field(
        description=WORKSPACE_ID_TIP_TEXT,
        default=None,
    ),
]) -> str
```

Update a deployed destination connector&#x27;s configuration on Airbyte Cloud.

This is a destructive operation that can break existing connections if the
configuration is changed incorrectly. Use with caution.

#### rename\_cloud\_connection

```python
@mcp_tool(
    domain="cloud",
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def rename_cloud_connection(
    connection_id: Annotated[
        str,
        Field(description="The ID of the connection to rename."),
    ], name: Annotated[
        str,
        Field(description="New name for the connection."),
    ], *, workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ]
) -> str
```

Rename a connection on Airbyte Cloud.

#### set\_cloud\_connection\_table\_prefix

```python
@mcp_tool(
    domain="cloud",
    destructive=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def set_cloud_connection_table_prefix(connection_id: Annotated[
    str,
    Field(description="The ID of the connection to update."),
], prefix: Annotated[
    str,
    Field(
        description="New table prefix to use when syncing to the destination."
    ),
], *, workspace_id: Annotated[
    str | None,
    Field(
        description=WORKSPACE_ID_TIP_TEXT,
        default=None,
    ),
]) -> str
```

Set the table prefix for a connection on Airbyte Cloud.

This is a destructive operation that can break downstream dependencies if the
table prefix is changed incorrectly. Use with caution.

#### set\_cloud\_connection\_selected\_streams

```python
@mcp_tool(
    domain="cloud",
    destructive=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def set_cloud_connection_selected_streams(
    connection_id: Annotated[
        str,
        Field(description="The ID of the connection to update."),
    ], stream_names: Annotated[
        str | list[str],
        Field(description=(
            "The selected stream names to sync within the connection. "
            "Must be an explicit stream name or list of streams.")),
    ], *, workspace_id: Annotated[
        str | None,
        Field(
            description=WORKSPACE_ID_TIP_TEXT,
            default=None,
        ),
    ]
) -> str
```

Set the selected streams for a connection on Airbyte Cloud.

This is a destructive operation that can break existing connections if the
stream selection is changed incorrectly. Use with caution.

#### update\_cloud\_connection

```python
@mcp_tool(
    domain="cloud",
    open_world=True,
    destructive=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def update_cloud_connection(connection_id: Annotated[
    str,
    Field(description="The ID of the connection to update."),
], *, enabled: Annotated[
    bool | None,
    Field(
        description=("Set the connection's enabled status. "
                     "True enables the connection (status='active'), "
                     "False disables it (status='inactive'). "
                     "Leave unset to keep the current status."),
        default=None,
    ),
], cron_expression: Annotated[
    str | None,
    Field(
        description=("A cron expression defining when syncs should run. "
                     "Examples: '0 0 * * *' (daily at midnight UTC), "
                     "'0 */6 * * *' (every 6 hours), "
                     "'0 0 * * 0' (weekly on Sunday at midnight UTC). "
                     "Leave unset to keep the current schedule. "
                     "Cannot be used together with 'manual_schedule'."),
        default=None,
    ),
], manual_schedule: Annotated[
    bool | None,
    Field(
        description=(
            "Set to True to disable automatic syncs (manual scheduling only). "
            "Syncs will only run when manually triggered. "
            "Cannot be used together with 'cron_expression'."),
        default=None,
    ),
], workspace_id: Annotated[
    str | None,
    Field(
        description=WORKSPACE_ID_TIP_TEXT,
        default=None,
    ),
]) -> str
```

Update a connection&#x27;s settings on Airbyte Cloud.

This tool allows updating multiple connection settings in a single call:
- Enable or disable the connection
- Set a cron schedule for automatic syncs
- Switch to manual scheduling (no automatic syncs)

At least one setting must be provided. The &#x27;cron_expression&#x27; and &#x27;manual_schedule&#x27;
parameters are mutually exclusive.

#### get\_connection\_artifact

```python
@mcp_tool(
    domain="cloud",
    read_only=True,
    idempotent=True,
    open_world=True,
    extra_help_text=CLOUD_AUTH_TIP_TEXT,
)
def get_connection_artifact(connection_id: Annotated[
    str,
    Field(description="The ID of the Airbyte Cloud connection."),
], artifact_type: Annotated[
    Literal["state", "catalog"],
    Field(
        description="The type of artifact to retrieve: 'state' or 'catalog'."),
], *, workspace_id: Annotated[
    str | None,
    Field(
        description=WORKSPACE_ID_TIP_TEXT,
        default=None,
    ),
]) -> dict[str, Any] | list[dict[str, Any]]
```

Get a connection artifact (state or catalog) from Airbyte Cloud.

Retrieves the specified artifact for a connection:
- &#x27;state&#x27;: Returns the persisted state for incremental syncs as a list of
  stream state objects, or {&quot;ERROR&quot;: &quot;...&quot;} if no state is set.
- &#x27;catalog&#x27;: Returns the configured catalog (syncCatalog) as a dict,
  or {&quot;ERROR&quot;: &quot;...&quot;} if not found.

#### register\_cloud\_ops\_tools

```python
def register_cloud_ops_tools(app: FastMCP) -> None
```

@private Register tools with the FastMCP app.

This is an internal function and should not be called directly.

Tools are filtered based on mode settings:
- AIRBYTE_CLOUD_MCP_READONLY_MODE=1: Only read-only tools are registered
- AIRBYTE_CLOUD_MCP_SAFE_MODE=1: All tools are registered, but destructive
  operations are protected by runtime session checks

