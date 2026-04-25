---
id: airbyte_agent_sdk-connectors-gitlab-index
title: airbyte_agent_sdk.connectors.gitlab.index
---

Module airbyte_agent_sdk.connectors.gitlab
==========================================
Gitlab connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.gitlab.connector
* airbyte_agent_sdk.connectors.gitlab.connector_model
* airbyte_agent_sdk.connectors.gitlab.models
* airbyte_agent_sdk.connectors.gitlab.types

Classes
-------

<a id="AirbyteAuthConfig"></a>

`AirbyteAuthConfig(**data: Any)`
:   Authentication configuration for Airbyte hosted mode execution.
    
    Pass this to the connector's `auth_config` parameter to use hosted mode,
    where API credentials are stored securely in Airbyte Cloud.
    
    For hosted mode execution, provide client credentials with either:
    - `connector_id`: Direct connector/source ID (skips lookup)
    - `workspace_name`: Workspace name for connector lookup
    
    Attributes:
        workspace_name: Workspace name for hosted mode connector lookup
        organization_id: Optional Airbyte organization ID for multi-org selection
        airbyte_client_id: Airbyte OAuth client ID (required for hosted mode)
        airbyte_client_secret: Airbyte OAuth client secret (required for hosted mode)
        connector_id: Specific connector/source ID (skips lookup if provided)
    
    Examples:
        # Hosted mode with connector_id (no lookup needed)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with workspace_name (lookup by workspace)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `airbyte_client_id: str | None`
    :   The type of the None singleton.

    `airbyte_client_secret: str | None`
    :   The type of the None singleton.

    `connector_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: str | None`
    :   The type of the None singleton.

    `workspace_name: str | None`
    :   The type of the None singleton.

<a id="AirbyteSearchMeta"></a>

`AirbyteSearchMeta(**data: Any)`
:   Pagination metadata for search responses.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   Cursor for fetching the next page of results.

    `has_more: bool`
    :   Whether more results are available.

    `model_config`
    :   The type of the None singleton.

    `took_ms: int | None`
    :   Time taken to execute the search in milliseconds.

<a id="AirbyteSearchResult"></a>

`AirbyteSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[BranchesSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[CommitsSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[GroupMembersSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[GroupMilestonesSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[GroupsSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[IssuesSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[MergeRequestsSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[PipelinesSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[ProjectMembersSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[ProjectMilestonesSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[ProjectsSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[ReleasesSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[TagsSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="BranchesSearchResult"></a>

`BranchesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CommitsSearchResult"></a>

`CommitsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GroupMembersSearchResult"></a>

`GroupMembersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GroupMilestonesSearchResult"></a>

`GroupMilestonesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GroupsSearchResult"></a>

`GroupsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="IssuesSearchResult"></a>

`IssuesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MergeRequestsSearchResult"></a>

`MergeRequestsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="PipelinesSearchResult"></a>

`PipelinesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ProjectMembersSearchResult"></a>

`ProjectMembersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ProjectMilestonesSearchResult"></a>

`ProjectMilestonesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ProjectsSearchResult"></a>

`ProjectsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ReleasesSearchResult"></a>

`ReleasesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TagsSearchResult"></a>

`TagsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="UsersSearchResult"></a>

`UsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="BranchesSearchData"></a>

`BranchesSearchData(**data: Any)`
:   Search result data for branches entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `can_push: bool | None`
    :   Whether the current user can push

    `commit: dict[str, typing.Any] | None`
    :   Head commit details

    `commit_id: str | None`
    :   SHA of the head commit

    `default: bool | None`
    :   Whether this is the default branch

    `developers_can_merge: bool | None`
    :   Whether developers can merge into the branch

    `developers_can_push: bool | None`
    :   Whether developers can push to the branch

    `merged: bool | None`
    :   Whether the branch is merged

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the branch

    `project_id: int | None`
    :   ID of the project the branch belongs to

    `protected: bool | None`
    :   Whether the branch is protected

    `web_url: str | None`
    :   Web URL of the branch

<a id="CommitsSearchData"></a>

`CommitsSearchData(**data: Any)`
:   Search result data for commits entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_email: str | None`
    :   Email of the commit author

    `author_name: str | None`
    :   Name of the commit author

    `authored_date: str | None`
    :   Date the commit was authored

    `committed_date: str | None`
    :   Date the commit was committed

    `committer_email: str | None`
    :   Email of the committer

    `committer_name: str | None`
    :   Name of the committer

    `created_at: str | None`
    :   Timestamp when the commit was created

    `id: str | None`
    :   SHA of the commit

    `message: str | None`
    :   Full commit message

    `model_config`
    :   The type of the None singleton.

    `parent_ids: list[typing.Any] | None`
    :   SHAs of parent commits

    `project_id: int | None`
    :   ID of the project the commit belongs to

    `short_id: str | None`
    :   Short SHA of the commit

    `stats: dict[str, typing.Any] | None`
    :   Commit statistics

    `title: str | None`
    :   Title of the commit

    `trailers: dict[str, typing.Any] | None`
    :   Git trailers for the commit

    `web_url: str | None`
    :   Web URL of the commit

<a id="GitlabConnector"></a>

`GitlabConnector(auth_config: GitlabAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, api_url: str | None = None)`
:   Type-safe Gitlab API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new gitlab connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., GitlabAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            api_url: GitLab instance hostname
    Examples:
        # Local mode (direct API calls)
        connector = GitlabConnector(auth_config=GitlabAuthConfig(access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = GitlabConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = GitlabConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )

    ### Class variables

    `connector_name`
    :   The type of the None singleton.

    `connector_version`
    :   The type of the None singleton.

    `sdk_version`
    :   The type of the None singleton.

    ### Static methods

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'GitlabAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'GitlabReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Supports two authentication modes:
        1. Direct credentials: Provide `auth_config` with typed credentials
        2. Server-side OAuth: Provide `server_side_oauth_secret_id` from OAuth flow
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config. Required unless using server_side_oauth_secret_id.
            server_side_oauth_secret_id: OAuth secret ID from get_consent_url redirect.
                When provided, auth_config is not required.
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Typed replication settings.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A GitlabConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await GitlabConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GitlabAuthConfig(access_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await GitlabConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GitlabAuthConfig(access_token="..."),
                replication_config=GitlabReplicationConfig(start_date="..."),
            )
        
            # With server-side OAuth:
            connector = await GitlabConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=GitlabReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'GitlabReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Initiate server-side OAuth flow with auto-source creation.
        
        Returns a consent URL where the end user should be redirected to grant access.
        After completing consent, the source is automatically created and the user is
        redirected to your redirect_url with a `connector_id` query parameter.
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            redirect_url: URL where users will be redirected after OAuth consent.
                After consent, user arrives at: redirect_url?connector_id=...
            name: Optional name for the source. Defaults to connector name + workspace_name.
            replication_config: Typed replication settings. Merged with OAuth credentials.
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            The OAuth consent URL
        
        Example:
            consent_url = await GitlabConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Gitlab Source",
                replication_config=GitlabReplicationConfig(start_date="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @GitlabConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GitlabConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
        Args:
            update_docstring: When True, append connector capabilities to __doc__.
            max_output_chars: Max serialized output size before raising. Use None to disable.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.
        
        Example:
            connector = await GitlabConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            GitlabCheckResult with status ("healthy" or "unhealthy") and optional error message
        
        Example:
            result = await connector.check()
            if result.status == "healthy":
                print("Connection verified!")
            else:
                print(f"Check failed: \{result.error\}")

    `close(self)`
    :   Close the connector and release resources.

    `entity_schema(self, entity: str) ‑> dict[str, typing.Any] | None`
    :   Get the JSON schema for an entity.
        
        Args:
            entity: Entity name (e.g., "contacts", "companies")
        
        Returns:
            JSON schema dict describing the entity structure, or None if not found.
        
        Example:
            schema = connector.entity_schema("contacts")
            if schema:
                print(f"Contact properties: \{list(schema.get('properties', \{\}).keys())\}")

    `execute(self, entity: str, action: "Literal['list', 'get', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
        
        Returns:
            Typed response based on the operation
        
        Example:
            customer = await connector.execute(
                entity="customers",
                action="get",
                params=\{"id": "cus_123"\}
            )

    `list_entities(self) ‑> list[dict[str, typing.Any]]`
    :   Get structured data about available entities, actions, and parameters.
        
        Returns a list of entity descriptions with:
        - entity_name: Name of the entity (e.g., "contacts", "deals")
        - description: Entity description from the first endpoint
        - available_actions: List of actions (e.g., ["list", "get", "create"])
        - parameters: Dict mapping action -> list of parameter dicts
        
        Example:
            entities = connector.list_entities()
            for entity in entities:
                print(f"\{entity['entity_name']\}: \{entity['available_actions']\}")

<a id="GitlabReplicationConfig"></a>

`GitlabReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from GitLab.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str | None`
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data. If not set, all data will be replicated.

<a id="GroupMembersSearchData"></a>

`GroupMembersSearchData(**data: Any)`
:   Search result data for group_members entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_level: int | None`
    :   Access level of the member

    `avatar_url: str | None`
    :   URL of the member avatar

    `created_at: str | None`
    :   Timestamp when the member was added

    `created_by: dict[str, typing.Any] | None`
    :   User who added the member

    `expires_at: str | None`
    :   Expiration date of the membership

    `group_id: int | None`
    :   ID of the group

    `id: int | None`
    :   ID of the member

    `locked: bool | None`
    :   Whether the member account is locked

    `membership_state: str | None`
    :   State of the membership

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the member

    `state: str | None`
    :   State of the member account

    `username: str | None`
    :   Username of the member

    `web_url: str | None`
    :   Web URL of the member profile

<a id="GroupMilestonesSearchData"></a>

`GroupMilestonesSearchData(**data: Any)`
:   Search result data for group_milestones entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the milestone was created

    `description: str | None`
    :   Description of the milestone

    `due_date: str | None`
    :   Due date of the milestone

    `expired: bool | None`
    :   Whether the milestone is expired

    `group_id: int | None`
    :   ID of the group

    `id: int | None`
    :   ID of the milestone

    `iid: int | None`
    :   Internal ID of the milestone within the group

    `model_config`
    :   The type of the None singleton.

    `start_date: str | None`
    :   Start date of the milestone

    `state: str | None`
    :   State of the milestone

    `title: str | None`
    :   Title of the milestone

    `updated_at: str | None`
    :   Timestamp when the milestone was last updated

    `web_url: str | None`
    :   Web URL of the milestone

<a id="GroupsSearchData"></a>

`GroupsSearchData(**data: Any)`
:   Search result data for groups entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auto_devops_enabled: bool | None`
    :   Whether Auto DevOps is enabled

    `avatar_url: str | None`
    :   URL of the group avatar

    `created_at: str | None`
    :   Timestamp when the group was created

    `default_branch_protection: int | None`
    :   Default branch protection level

    `description: str | None`
    :   Description of the group

    `emails_disabled: bool | None`
    :   Whether emails are disabled

    `emails_enabled: bool | None`
    :   Whether emails are enabled

    `full_name: str | None`
    :   Full name of the group

    `full_path: str | None`
    :   Full path of the group

    `id: int | None`
    :   ID of the group

    `lfs_enabled: bool | None`
    :   Whether Git LFS is enabled

    `mentions_disabled: bool | None`
    :   Whether mentions are disabled

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the group

    `parent_id: int | None`
    :   ID of the parent group

    `path: str | None`
    :   URL path of the group

    `project_creation_level: str | None`
    :   Level required to create projects

    `projects: list[typing.Any] | None`
    :   Projects in the group

    `request_access_enabled: bool | None`
    :   Whether access requests are enabled

    `require_two_factor_authentication: bool | None`
    :   Whether two-factor authentication is required

    `share_with_group_lock: bool | None`
    :   Whether sharing with other groups is locked

    `shared_with_groups: list[typing.Any] | None`
    :   Groups this group is shared with

    `subgroup_creation_level: str | None`
    :   Level required to create subgroups

    `two_factor_grace_period: int | None`
    :   Grace period for two-factor authentication

    `visibility: str | None`
    :   Visibility level of the group

    `web_url: str | None`
    :   Web URL of the group

<a id="IssuesSearchData"></a>

`IssuesSearchData(**data: Any)`
:   Search result data for issues entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee: dict[str, typing.Any] | None`
    :   Primary assignee of the issue

    `assignee_id: int | None`
    :   ID of the primary assignee

    `assignees: list[typing.Any] | None`
    :   Users assigned to the issue

    `author: dict[str, typing.Any] | None`
    :   Author of the issue

    `author_id: int | None`
    :   ID of the author

    `blocking_issues_count: int | None`
    :   Number of blocking issues

    `closed_at: str | None`
    :   Timestamp when the issue was closed

    `closed_by: dict[str, typing.Any] | None`
    :   User who closed the issue

    `closed_by_id: int | None`
    :   ID of the user who closed the issue

    `confidential: bool | None`
    :   Whether the issue is confidential

    `created_at: str | None`
    :   Timestamp when the issue was created

    `description: str | None`
    :   Description of the issue

    `discussion_locked: bool | None`
    :   Whether discussion is locked

    `downvotes: int | None`
    :   Number of downvotes

    `due_date: str | None`
    :   Due date for the issue

    `has_tasks: bool | None`
    :   Whether the issue has tasks

    `id: int | None`
    :   ID of the issue

    `iid: int | None`
    :   Internal ID of the issue within the project

    `issue_type: str | None`
    :   Type classification of the issue

    `labels: list[typing.Any] | None`
    :   Labels assigned to the issue

    `links: dict[str, typing.Any] | None`
    :   Related resource links

    `merge_requests_count: int | None`
    :   Number of related merge requests

    `milestone: dict[str, typing.Any] | None`
    :   Milestone the issue belongs to

    `milestone_id: int | None`
    :   ID of the milestone

    `model_config`
    :   The type of the None singleton.

    `project_id: int | None`
    :   ID of the project the issue belongs to

    `references: dict[str, typing.Any] | None`
    :   Issue references

    `severity: str | None`
    :   Severity level of the issue

    `state: str | None`
    :   State of the issue

    `task_completion_status: dict[str, typing.Any] | None`
    :   Task completion status

    `time_stats: dict[str, typing.Any] | None`
    :   Time tracking statistics

    `title: str | None`
    :   Title of the issue

    `type_: str | None`
    :   Type of the issue

    `updated_at: str | None`
    :   Timestamp when the issue was last updated

    `upvotes: int | None`
    :   Number of upvotes

    `user_notes_count: int | None`
    :   Number of user notes on the issue

    `web_url: str | None`
    :   Web URL of the issue

    `weight: int | None`
    :   Weight of the issue

<a id="MergeRequestsSearchData"></a>

`MergeRequestsSearchData(**data: Any)`
:   Search result data for merge_requests entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee: dict[str, typing.Any] | None`
    :   Primary assignee of the merge request

    `assignee_id: int | None`
    :   ID of the primary assignee

    `assignees: list[typing.Any] | None`
    :   Users assigned to the merge request

    `author: dict[str, typing.Any] | None`
    :   Author of the merge request

    `author_id: int | None`
    :   ID of the author

    `blocking_discussions_resolved: bool | None`
    :   Whether blocking discussions are resolved

    `closed_at: str | None`
    :   Timestamp when the merge request was closed

    `closed_by: dict[str, typing.Any] | None`
    :   User who closed the merge request

    `closed_by_id: int | None`
    :   ID of the user who closed it

    `created_at: str | None`
    :   Timestamp when the merge request was created

    `description: str | None`
    :   Description of the merge request

    `detailed_merge_status: str | None`
    :   Detailed merge status

    `discussion_locked: bool | None`
    :   Whether discussion is locked

    `downvotes: int | None`
    :   Number of downvotes

    `draft: bool | None`
    :   Whether the merge request is a draft

    `force_remove_source_branch: bool | None`
    :   Whether to force remove source branch

    `has_conflicts: bool | None`
    :   Whether the merge request has conflicts

    `id: int | None`
    :   ID of the merge request

    `iid: int | None`
    :   Internal ID of the merge request within the project

    `labels: list[typing.Any] | None`
    :   Labels assigned to the merge request

    `merge_commit_sha: str | None`
    :   SHA of the merge commit

    `merge_status: str | None`
    :   Merge status of the merge request

    `merge_user: dict[str, typing.Any] | None`
    :   User who performed the merge

    `merge_when_pipeline_succeeds: bool | None`
    :   Whether to merge when pipeline succeeds

    `merged_at: str | None`
    :   Timestamp when the merge request was merged

    `merged_by: dict[str, typing.Any] | None`
    :   User who merged the merge request

    `merged_by_id: int | None`
    :   ID of the user who merged it

    `milestone: dict[str, typing.Any] | None`
    :   Milestone the merge request belongs to

    `milestone_id: int | None`
    :   ID of the milestone

    `model_config`
    :   The type of the None singleton.

    `project_id: int | None`
    :   ID of the project

    `reference: str | None`
    :   Short reference for the merge request

    `references: dict[str, typing.Any] | None`
    :   Merge request references

    `reviewers: list[typing.Any] | None`
    :   Users assigned as reviewers

    `sha: str | None`
    :   SHA of the head commit

    `should_remove_source_branch: bool | None`
    :   Whether source branch should be removed

    `source_branch: str | None`
    :   Source branch for the merge request

    `source_project_id: int | None`
    :   ID of the source project

    `squash: bool | None`
    :   Whether to squash commits on merge

    `squash_commit_sha: str | None`
    :   SHA of the squash commit

    `state: str | None`
    :   State of the merge request

    `target_branch: str | None`
    :   Target branch for the merge request

    `target_project_id: int | None`
    :   ID of the target project

    `task_completion_status: dict[str, typing.Any] | None`
    :   Task completion status

    `time_stats: dict[str, typing.Any] | None`
    :   Time tracking statistics

    `title: str | None`
    :   Title of the merge request

    `updated_at: str | None`
    :   Timestamp when the merge request was last updated

    `upvotes: int | None`
    :   Number of upvotes

    `user_notes_count: int | None`
    :   Number of user notes

    `web_url: str | None`
    :   Web URL of the merge request

    `work_in_progress: bool | None`
    :   Whether the merge request is a work in progress

<a id="PipelinesSearchData"></a>

`PipelinesSearchData(**data: Any)`
:   Search result data for pipelines entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the pipeline was created

    `id: int | None`
    :   ID of the pipeline

    `iid: int | None`
    :   Internal ID of the pipeline within the project

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the pipeline

    `project_id: int | None`
    :   ID of the project

    `ref: str | None`
    :   Branch or tag that triggered the pipeline

    `sha: str | None`
    :   SHA of the commit that triggered the pipeline

    `source: str | None`
    :   Source that triggered the pipeline

    `status: str | None`
    :   Status of the pipeline

    `updated_at: str | None`
    :   Timestamp when the pipeline was last updated

    `web_url: str | None`
    :   Web URL of the pipeline

<a id="ProjectMembersSearchData"></a>

`ProjectMembersSearchData(**data: Any)`
:   Search result data for project_members entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_level: int | None`
    :   Access level of the member

    `avatar_url: str | None`
    :   URL of the member avatar

    `created_at: str | None`
    :   Timestamp when the member was added

    `created_by: dict[str, typing.Any] | None`
    :   User who added the member

    `expires_at: str | None`
    :   Expiration date of the membership

    `id: int | None`
    :   ID of the member

    `locked: bool | None`
    :   Whether the member account is locked

    `membership_state: str | None`
    :   State of the membership

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the member

    `project_id: int | None`
    :   ID of the project

    `state: str | None`
    :   State of the member account

    `username: str | None`
    :   Username of the member

    `web_url: str | None`
    :   Web URL of the member profile

<a id="ProjectMilestonesSearchData"></a>

`ProjectMilestonesSearchData(**data: Any)`
:   Search result data for project_milestones entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the milestone was created

    `description: str | None`
    :   Description of the milestone

    `due_date: str | None`
    :   Due date of the milestone

    `expired: bool | None`
    :   Whether the milestone is expired

    `id: int | None`
    :   ID of the milestone

    `iid: int | None`
    :   Internal ID of the milestone within the project

    `model_config`
    :   The type of the None singleton.

    `project_id: int | None`
    :   ID of the project

    `start_date: str | None`
    :   Start date of the milestone

    `state: str | None`
    :   State of the milestone

    `title: str | None`
    :   Title of the milestone

    `updated_at: str | None`
    :   Timestamp when the milestone was last updated

    `web_url: str | None`
    :   Web URL of the milestone

<a id="ProjectsSearchData"></a>

`ProjectsSearchData(**data: Any)`
:   Search result data for projects entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allow_merge_on_skipped_pipeline: bool | None`
    :   Whether merge is allowed on skipped pipeline

    `analytics_access_level: str | None`
    :   Access level for analytics

    `archived: bool | None`
    :   Whether the project is archived

    `auto_cancel_pending_pipelines: str | None`
    :   Auto-cancel pending pipelines setting

    `auto_devops_deploy_strategy: str | None`
    :   Auto DevOps deployment strategy

    `auto_devops_enabled: bool | None`
    :   Whether Auto DevOps is enabled

    `autoclose_referenced_issues: bool | None`
    :   Whether referenced issues are auto-closed

    `avatar_url: str | None`
    :   URL of the project avatar

    `build_timeout: int | None`
    :   Build timeout in seconds

    `builds_access_level: str | None`
    :   Access level for builds

    `can_create_merge_request_in: bool | None`
    :   Whether user can create merge requests

    `ci_config_path: str | None`
    :   Path to the CI configuration file

    `ci_default_git_depth: int | None`
    :   Default git depth for CI pipelines

    `ci_forward_deployment_enabled: bool | None`
    :   Whether CI forward deployment is enabled

    `compliance_frameworks: list[typing.Any] | None`
    :   Compliance frameworks for the project

    `container_expiration_policy: dict[str, typing.Any] | None`
    :   Container expiration policy settings

    `container_registry_enabled: bool | None`
    :   Whether container registry is enabled

    `container_registry_image_prefix: str | None`
    :   Prefix for container registry images

    `created_at: str | None`
    :   Timestamp when the project was created

    `creator_id: int | None`
    :   ID of the project creator

    `default_branch: str | None`
    :   Default branch of the project

    `description: str | None`
    :   Description of the project

    `description_html: str | None`
    :   HTML-rendered description of the project

    `emails_disabled: bool | None`
    :   Whether emails are disabled

    `empty_repo: bool | None`
    :   Whether the repository is empty

    `external_authorization_classification_label: str | None`
    :   External authorization classification label

    `forking_access_level: str | None`
    :   Access level for forking

    `forks_count: int | None`
    :   Number of forks

    `http_url_to_repo: str | None`
    :   HTTP URL to the repository

    `id: int | None`
    :   ID of the project

    `import_status: str | None`
    :   Import status of the project

    `issues_access_level: str | None`
    :   Access level for issues

    `issues_enabled: bool | None`
    :   Whether issues are enabled

    `jobs_enabled: bool | None`
    :   Whether jobs are enabled

    `keep_latest_artifact: bool | None`
    :   Whether the latest artifact is kept

    `last_activity_at: str | None`
    :   Timestamp of last activity

    `lfs_enabled: bool | None`
    :   Whether Git LFS is enabled

    `links: dict[str, typing.Any] | None`
    :   Related resource links

    `merge_method: str | None`
    :   Merge method used for the project

    `merge_requests_access_level: str | None`
    :   Access level for merge requests

    `merge_requests_enabled: bool | None`
    :   Whether merge requests are enabled

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the project

    `name_with_namespace: str | None`
    :   Full name including namespace

    `namespace: dict[str, typing.Any] | None`
    :   Namespace the project belongs to

    `only_allow_merge_if_all_discussions_are_resolved: bool | None`
    :   Whether merge requires all discussions resolved

    `only_allow_merge_if_pipeline_succeeds: bool | None`
    :   Whether merge requires pipeline success

    `open_issues_count: int | None`
    :   Number of open issues

    `operations_access_level: str | None`
    :   Access level for operations

    `packages_enabled: bool | None`
    :   Whether packages are enabled

    `pages_access_level: str | None`
    :   Access level for pages

    `path: str | None`
    :   URL path of the project

    `path_with_namespace: str | None`
    :   Full path including namespace

    `permissions: dict[str, typing.Any] | None`
    :   User permissions for the project

    `printing_merge_request_link_enabled: bool | None`
    :   Whether MR link printing is enabled

    `public_jobs: bool | None`
    :   Whether jobs are public

    `readme_url: str | None`
    :   URL to the project README

    `remove_source_branch_after_merge: bool | None`
    :   Whether source branch is removed after merge

    `repository_access_level: str | None`
    :   Access level for the repository

    `request_access_enabled: bool | None`
    :   Whether access requests are enabled

    `requirements_enabled: bool | None`
    :   Whether requirements are enabled

    `resolve_outdated_diff_discussions: bool | None`
    :   Whether outdated diff discussions are auto-resolved

    `restrict_user_defined_variables: bool | None`
    :   Whether user-defined variables are restricted

    `security_and_compliance_enabled: bool | None`
    :   Whether security and compliance is enabled

    `service_desk_address: str | None`
    :   Email address for the service desk

    `service_desk_enabled: bool | None`
    :   Whether service desk is enabled

    `shared_runners_enabled: bool | None`
    :   Whether shared runners are enabled

    `shared_with_groups: list[typing.Any] | None`
    :   Groups the project is shared with

    `snippets_access_level: str | None`
    :   Access level for snippets

    `snippets_enabled: bool | None`
    :   Whether snippets are enabled

    `ssh_url_to_repo: str | None`
    :   SSH URL to the repository

    `star_count: int | None`
    :   Number of stars

    `statistics: dict[str, typing.Any] | None`
    :   Project statistics

    `tag_list: list[typing.Any] | None`
    :   List of tags for the project

    `topics: list[typing.Any] | None`
    :   List of topics for the project

    `updated_at: str | None`
    :   Timestamp when the project was last updated

    `visibility: str | None`
    :   Visibility level of the project

    `web_url: str | None`
    :   Web URL of the project

    `wiki_access_level: str | None`
    :   Access level for the wiki

    `wiki_enabled: bool | None`
    :   Whether wiki is enabled

<a id="ReleasesSearchData"></a>

`ReleasesSearchData(**data: Any)`
:   Search result data for releases entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assets: dict[str, typing.Any] | None`
    :   Assets attached to the release

    `author: dict[str, typing.Any] | None`
    :   Author of the release

    `author_id: int | None`
    :   ID of the author

    `commit: dict[str, typing.Any] | None`
    :   Commit associated with the release

    `commit_id: str | None`
    :   SHA of the associated commit

    `commit_path: str | None`
    :   Path to the release commit

    `created_at: str | None`
    :   Timestamp when the release was created

    `description: str | None`
    :   Description of the release

    `evidences: list[typing.Any] | None`
    :   Evidences collected for the release

    `links: dict[str, typing.Any] | None`
    :   Related resource links

    `milestones: list[typing.Any] | None`
    :   Milestones associated with the release

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the release

    `project_id: int | None`
    :   ID of the project

    `released_at: str | None`
    :   Timestamp when the release was published

    `tag_name: str | None`
    :   Tag name associated with the release

    `tag_path: str | None`
    :   Path to the release tag

    `upcoming_release: bool | None`
    :   Whether this is an upcoming release

<a id="TagsSearchData"></a>

`TagsSearchData(**data: Any)`
:   Search result data for tags entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `commit: dict[str, typing.Any] | None`
    :   Commit the tag points to

    `commit_id: str | None`
    :   SHA of the tagged commit

    `message: str | None`
    :   Annotation message of the tag

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the tag

    `project_id: int | None`
    :   ID of the project

    `protected: bool | None`
    :   Whether the tag is protected

    `release: dict[str, typing.Any] | None`
    :   Release associated with the tag

    `target: str | None`
    :   SHA the tag points to

<a id="UsersSearchData"></a>

`UsersSearchData(**data: Any)`
:   Search result data for users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_url: str | None`
    :   URL of the user avatar

    `id: int | None`
    :   ID of the user

    `locked: bool | None`
    :   Whether the user account is locked

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the user

    `state: str | None`
    :   State of the user account

    `username: str | None`
    :   Username of the user

    `web_url: str | None`
    :   Web URL of the user profile