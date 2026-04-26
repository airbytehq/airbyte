---
id: airbyte_agent_sdk-connectors-sentry-index
title: airbyte_agent_sdk.connectors.sentry.index
---

Module airbyte_agent_sdk.connectors.sentry
==========================================
Sentry connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.sentry.connector
* airbyte_agent_sdk.connectors.sentry.connector_model
* airbyte_agent_sdk.connectors.sentry.models
* airbyte_agent_sdk.connectors.sentry.types

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

    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult[EventsSearchData]
    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult[IssuesSearchData]
    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult[ProjectsSearchData]
    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult[ReleasesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="EventsSearchResult"></a>

`EventsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="EventsSearchData"></a>

`EventsSearchData(**data: Any)`
:   Search result data for events entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `context: dict[str, typing.Any] | None`
    :   Additional context data.

    `contexts: dict[str, typing.Any] | None`
    :   Structured context information.

    `crash_file: str | None`
    :   Crash file reference.

    `culprit: str | None`
    :   The culprit (source) of the event.

    `date_created: str | None`
    :   When the event was created.

    `date_received: str | None`
    :   When the event was received by Sentry.

    `dist: str | None`
    :   Distribution information.

    `entries: list[typing.Any] | None`
    :   Event entries (exception, breadcrumbs, request, etc.).

    `errors: list[typing.Any] | None`
    :   Processing errors.

    `event_id: str | None`
    :   Event ID as reported by the client.

    `event_type: str | None`
    :   The type of the event.

    `fingerprints: list[typing.Any] | None`
    :   Fingerprints used for grouping.

    `group_id: str | None`
    :   ID of the issue group this event belongs to.

    `grouping_config: dict[str, typing.Any] | None`
    :   Grouping configuration.

    `id: str | None`
    :   Unique event identifier.

    `location: str | None`
    :   Location in source code.

    `message: str | None`
    :   Event message.

    `meta: dict[str, typing.Any] | None`
    :   Meta information for data scrubbing.

    `metadata: dict[str, typing.Any] | None`
    :   Event metadata.

    `model_config`
    :   The type of the None singleton.

    `occurrence: str | None`
    :   Occurrence information for the event.

    `packages: dict[str, typing.Any] | None`
    :   Package information.

    `platform: str | None`
    :   Platform the event was generated on.

    `project_id: str | None`
    :   Project ID this event belongs to.

    `sdk: str | None`
    :   SDK information.

    `size: int | None`
    :   Event payload size in bytes.

    `tags: list[typing.Any] | None`
    :   Tags associated with the event.

    `title: str | None`
    :   Event title.

    `type_: str | None`
    :   Event type.

    `user: dict[str, typing.Any] | None`
    :   User associated with the event.

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

    `annotations: list[typing.Any] | None`
    :   Annotations on the issue.

    `assigned_to: dict[str, typing.Any] | None`
    :   User or team assigned to this issue.

    `count: str | None`
    :   Number of events for this issue.

    `culprit: str | None`
    :   The culprit (source) of the issue.

    `first_seen: str | None`
    :   When the issue was first seen.

    `has_seen: bool | None`
    :   Whether the authenticated user has seen the issue.

    `id: str | None`
    :   Unique issue identifier.

    `is_bookmarked: bool | None`
    :   Whether the issue is bookmarked.

    `is_public: bool | None`
    :   Whether the issue is public.

    `is_subscribed: bool | None`
    :   Whether the user is subscribed to the issue.

    `is_unhandled: bool | None`
    :   Whether the issue is from an unhandled error.

    `issue_category: str | None`
    :   The category classification of the issue.

    `issue_type: str | None`
    :   The type classification of the issue.

    `last_seen: str | None`
    :   When the issue was last seen.

    `level: str | None`
    :   Issue severity level.

    `logger: str | None`
    :   Logger that generated the issue.

    `metadata: dict[str, typing.Any] | None`
    :   Issue metadata.

    `model_config`
    :   The type of the None singleton.

    `num_comments: int | None`
    :   Number of comments on the issue.

    `permalink: str | None`
    :   Permalink to the issue in the Sentry UI.

    `platform: str | None`
    :   Platform for this issue.

    `project: dict[str, typing.Any] | None`
    :   Project this issue belongs to.

    `share_id: str | None`
    :   Share ID if the issue is shared.

    `short_id: str | None`
    :   Short human-readable identifier.

    `stats: dict[str, typing.Any] | None`
    :   Issue event statistics.

    `status: str | None`
    :   Issue status (resolved, unresolved, ignored).

    `status_details: dict[str, typing.Any] | None`
    :   Status detail information.

    `subscription_details: dict[str, typing.Any] | None`
    :   Subscription details.

    `substatus: str | None`
    :   Issue substatus.

    `title: str | None`
    :   Issue title.

    `type_: str | None`
    :   Issue type.

    `user_count: int | None`
    :   Number of users affected.

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

    `access: list[typing.Any] | None`
    :   List of access permissions for the authenticated user.

    `avatar: dict[str, typing.Any] | None`
    :   Project avatar information.

    `color: str | None`
    :   Project color code.

    `date_created: str | None`
    :   Date the project was created.

    `features: list[typing.Any] | None`
    :   List of enabled features.

    `first_event: str | None`
    :   Timestamp of the first event.

    `first_transaction_event: bool | None`
    :   Whether a transaction event has been received.

    `has_access: bool | None`
    :   Whether the user has access to this project.

    `has_custom_metrics: bool | None`
    :   Whether the project has custom metrics.

    `has_feedbacks: bool | None`
    :   Whether the project has user feedback.

    `has_minified_stack_trace: bool | None`
    :   Whether the project has minified stack traces.

    `has_monitors: bool | None`
    :   Whether the project has cron monitors.

    `has_new_feedbacks: bool | None`
    :   Whether the project has new user feedback.

    `has_profiles: bool | None`
    :   Whether the project has profiling data.

    `has_replays: bool | None`
    :   Whether the project has session replays.

    `has_sessions: bool | None`
    :   Whether the project has session data.

    `id: str | None`
    :   Unique project identifier.

    `is_bookmarked: bool | None`
    :   Whether the project is bookmarked.

    `is_internal: bool | None`
    :   Whether the project is internal.

    `is_member: bool | None`
    :   Whether the authenticated user is a member.

    `is_public: bool | None`
    :   Whether the project is public.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Human-readable project name.

    `organization: dict[str, typing.Any] | None`
    :   Organization this project belongs to.

    `platform: str | None`
    :   The platform for this project.

    `slug: str | None`
    :   URL-friendly project identifier.

    `status: str | None`
    :   Project status.

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

    `authors: list[typing.Any] | None`
    :   Authors of commits in this release.

    `commit_count: int | None`
    :   Number of commits in this release.

    `current_project_meta: dict[str, typing.Any] | None`
    :   Metadata for the current project context.

    `data: dict[str, typing.Any] | None`
    :   Additional release data.

    `date_created: str | None`
    :   When the release was created.

    `date_released: str | None`
    :   When the release was deployed.

    `deploy_count: int | None`
    :   Number of deploys for this release.

    `first_event: str | None`
    :   Timestamp of the first event in this release.

    `id: int | None`
    :   Unique release identifier.

    `last_commit: dict[str, typing.Any] | None`
    :   Last commit in this release.

    `last_deploy: dict[str, typing.Any] | None`
    :   Last deploy of this release.

    `last_event: str | None`
    :   Timestamp of the last event in this release.

    `model_config`
    :   The type of the None singleton.

    `new_groups: int | None`
    :   Number of new issue groups in this release.

    `owner: str | None`
    :   Owner of the release.

    `projects: list[typing.Any] | None`
    :   Projects associated with this release.

    `ref: str | None`
    :   Git reference (commit SHA, tag, etc.).

    `short_version: str | None`
    :   Short version string.

    `status: str | None`
    :   Release status.

    `url: str | None`
    :   URL associated with the release.

    `user_agent: str | None`
    :   User agent that created the release.

    `version: str | None`
    :   Release version string.

    `version_info: dict[str, typing.Any] | None`
    :   Parsed version information.

<a id="SentryAuthConfig"></a>

`SentryAuthConfig(**data: Any)`
:   Authentication Token
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auth_token: str`
    :   Sentry authentication token. Log into Sentry and create one at Settings > Account > API > Auth Tokens.

    `model_config`
    :   The type of the None singleton.

<a id="SentryConnector"></a>

`SentryConnector(auth_config: SentryAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, hostname: str | None = None)`
:   Type-safe Sentry API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new sentry connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., SentryAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            hostname: Host name of Sentry API server. For self-hosted instances, specify your host name here. Otherwise, leave as sentry.io.
    Examples:
        # Local mode (direct API calls)
        connector = SentryConnector(auth_config=SentryAuthConfig(auth_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = SentryConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = SentryConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'SentryAuthConfig'", name: str | None = None, replication_config: "'SentryReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config (same as local mode)
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Typed replication settings.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A SentryConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await SentryConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=SentryAuthConfig(auth_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await SentryConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=SentryAuthConfig(auth_token="..."),
                replication_config=SentryReplicationConfig(organization="...", project="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @SentryConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @SentryConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await SentryConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.sentry.models.SentryCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            SentryCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="SentryReplicationConfig"></a>

`SentryReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Sentry.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `organization: str`
    :   The slug of the organization to replicate data from.

    `project: str`
    :   The slug of the project to replicate data from.