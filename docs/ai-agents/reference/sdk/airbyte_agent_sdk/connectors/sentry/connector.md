---
id: airbyte_agent_sdk-connectors-sentry-connector
title: airbyte_agent_sdk.connectors.sentry.connector
---

Module airbyte_agent_sdk.connectors.sentry.connector
====================================================
Sentry connector.

Classes
-------

<a id="EventsQuery"></a>

`EventsQuery(connector: SentryConnector)`
:   Query class for Events entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: EventsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult[EventsSearchData]`
    :   Search events records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (EventsSearchFilter):
        - meta: Meta information for data scrubbing.
        - context: Additional context data.
        - contexts: Structured context information.
        - crash_file: Crash file reference.
        - culprit: The culprit (source) of the event.
        - date_created: When the event was created.
        - date_received: When the event was received by Sentry.
        - dist: Distribution information.
        - entries: Event entries (exception, breadcrumbs, request, etc.).
        - errors: Processing errors.
        - event_type: The type of the event.
        - event_id: Event ID as reported by the client.
        - fingerprints: Fingerprints used for grouping.
        - group_id: ID of the issue group this event belongs to.
        - grouping_config: Grouping configuration.
        - id: Unique event identifier.
        - location: Location in source code.
        - message: Event message.
        - metadata: Event metadata.
        - occurrence: Occurrence information for the event.
        - packages: Package information.
        - platform: Platform the event was generated on.
        - project_id: Project ID this event belongs to.
        - sdk: SDK information.
        - size: Event payload size in bytes.
        - tags: Tags associated with the event.
        - title: Event title.
        - type_: Event type.
        - user: User associated with the event.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            EventsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, organization_slug: str, project_slug: str, event_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.sentry.models.Event`
    :   Return details on an individual event.
        
        Args:
            organization_slug: The slug of the organization the event belongs to.
            project_slug: The slug of the project the event belongs to.
            event_id: The ID of the event to retrieve (hexadecimal).
            **kwargs: Additional parameters
        
        Returns:
            Event

    `list(self, organization_slug: str, project_slug: str, full: str | None = None, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta[list[Event], EventsListResultMeta]`
    :   Return a list of events bound to a project.
        
        Args:
            organization_slug: The slug of the organization the events belong to.
            project_slug: The slug of the project the events belong to.
            full: If set to true, the event payload will include the full event body.
            cursor: Pagination cursor for next page of results.
            **kwargs: Additional parameters
        
        Returns:
            EventsListResult

<a id="IssuesQuery"></a>

`IssuesQuery(connector: SentryConnector)`
:   Query class for Issues entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: IssuesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult[IssuesSearchData]`
    :   Search issues records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IssuesSearchFilter):
        - annotations: Annotations on the issue.
        - assigned_to: User or team assigned to this issue.
        - count: Number of events for this issue.
        - culprit: The culprit (source) of the issue.
        - first_seen: When the issue was first seen.
        - has_seen: Whether the authenticated user has seen the issue.
        - id: Unique issue identifier.
        - is_bookmarked: Whether the issue is bookmarked.
        - is_public: Whether the issue is public.
        - is_subscribed: Whether the user is subscribed to the issue.
        - is_unhandled: Whether the issue is from an unhandled error.
        - issue_category: The category classification of the issue.
        - issue_type: The type classification of the issue.
        - last_seen: When the issue was last seen.
        - level: Issue severity level.
        - logger: Logger that generated the issue.
        - metadata: Issue metadata.
        - num_comments: Number of comments on the issue.
        - permalink: Permalink to the issue in the Sentry UI.
        - platform: Platform for this issue.
        - project: Project this issue belongs to.
        - share_id: Share ID if the issue is shared.
        - short_id: Short human-readable identifier.
        - stats: Issue event statistics.
        - status: Issue status (resolved, unresolved, ignored).
        - status_details: Status detail information.
        - subscription_details: Subscription details.
        - substatus: Issue substatus.
        - title: Issue title.
        - type_: Issue type.
        - user_count: Number of users affected.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            IssuesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, organization_slug: str, issue_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.sentry.models.Issue`
    :   Return details on an individual issue. This returns the basic stats for the issue (title, last seen, first seen), some overall numbers (number of comments, user reports) as well as the summarized event data.
        
        Args:
            organization_slug: The slug of the organization the issue belongs to.
            issue_id: The ID of the issue to retrieve.
            **kwargs: Additional parameters
        
        Returns:
            Issue

    `list(self, organization_slug: str, project_slug: str, query: str | None = None, stats_period: str | None = None, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta[list[Issue], IssuesListResultMeta]`
    :   Return a list of issues (groups) bound to a project. A default query of is:unresolved is applied. To return results with other statuses send a new query value (i.e. ?query= for all results).
        
        Args:
            organization_slug: The slug of the organization the issues belong to.
            project_slug: The slug of the project the issues belong to.
            query: An optional Sentry structured search query. If not provided an implied "is:unresolved" is assumed.
            stats_period: An optional stat period (can be one of "24h", "14d", and "").
            cursor: Pagination cursor for next page of results.
            **kwargs: Additional parameters
        
        Returns:
            IssuesListResult

<a id="ProjectDetailQuery"></a>

`ProjectDetailQuery(connector: SentryConnector)`
:   Query class for ProjectDetail entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, organization_slug: str, project_slug: str, **kwargs) ‑> airbyte_agent_sdk.connectors.sentry.models.ProjectDetail`
    :   Return detailed information about a specific project.
        
        Args:
            organization_slug: The slug of the organization the project belongs to.
            project_slug: The slug of the project.
            **kwargs: Additional parameters
        
        Returns:
            ProjectDetail

<a id="ProjectsQuery"></a>

`ProjectsQuery(connector: SentryConnector)`
:   Query class for Projects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProjectsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult[ProjectsSearchData]`
    :   Search projects records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProjectsSearchFilter):
        - access: List of access permissions for the authenticated user.
        - avatar: Project avatar information.
        - color: Project color code.
        - date_created: Date the project was created.
        - features: List of enabled features.
        - first_event: Timestamp of the first event.
        - first_transaction_event: Whether a transaction event has been received.
        - has_access: Whether the user has access to this project.
        - has_custom_metrics: Whether the project has custom metrics.
        - has_feedbacks: Whether the project has user feedback.
        - has_minified_stack_trace: Whether the project has minified stack traces.
        - has_monitors: Whether the project has cron monitors.
        - has_new_feedbacks: Whether the project has new user feedback.
        - has_profiles: Whether the project has profiling data.
        - has_replays: Whether the project has session replays.
        - has_sessions: Whether the project has session data.
        - id: Unique project identifier.
        - is_bookmarked: Whether the project is bookmarked.
        - is_internal: Whether the project is internal.
        - is_member: Whether the authenticated user is a member.
        - is_public: Whether the project is public.
        - name: Human-readable project name.
        - organization: Organization this project belongs to.
        - platform: The platform for this project.
        - slug: URL-friendly project identifier.
        - status: Project status.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProjectsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, organization_slug: str, project_slug: str, **kwargs) ‑> airbyte_agent_sdk.connectors.sentry.models.ProjectDetail`
    :   Return details on an individual project.
        
        Args:
            organization_slug: The slug of the organization the project belongs to.
            project_slug: The slug of the project to retrieve.
            **kwargs: Additional parameters
        
        Returns:
            ProjectDetail

    `list(self, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta[list[Project], ProjectsListResultMeta]`
    :   Return a list of projects available to the authenticated user.
        
        Args:
            cursor: Pagination cursor for next page of results.
            **kwargs: Additional parameters
        
        Returns:
            ProjectsListResult

<a id="ReleasesQuery"></a>

`ReleasesQuery(connector: SentryConnector)`
:   Query class for Releases entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ReleasesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult[ReleasesSearchData]`
    :   Search releases records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ReleasesSearchFilter):
        - authors: Authors of commits in this release.
        - commit_count: Number of commits in this release.
        - current_project_meta: Metadata for the current project context.
        - data: Additional release data.
        - date_created: When the release was created.
        - date_released: When the release was deployed.
        - deploy_count: Number of deploys for this release.
        - first_event: Timestamp of the first event in this release.
        - id: Unique release identifier.
        - last_commit: Last commit in this release.
        - last_deploy: Last deploy of this release.
        - last_event: Timestamp of the last event in this release.
        - new_groups: Number of new issue groups in this release.
        - owner: Owner of the release.
        - projects: Projects associated with this release.
        - ref: Git reference (commit SHA, tag, etc.).
        - short_version: Short version string.
        - status: Release status.
        - url: URL associated with the release.
        - user_agent: User agent that created the release.
        - version: Release version string.
        - version_info: Parsed version information.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ReleasesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, organization_slug: str, version: str, **kwargs) ‑> airbyte_agent_sdk.connectors.sentry.models.Release`
    :   Return a release for a given organization.
        
        Args:
            organization_slug: The slug of the organization.
            version: The version identifier of the release.
            **kwargs: Additional parameters
        
        Returns:
            Release

    `list(self, organization_slug: str, query: str | None = None, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta[list[Release], ReleasesListResultMeta]`
    :   Return a list of releases for a given organization.
        
        Args:
            organization_slug: The slug of the organization.
            query: This parameter can be used to create a "starts with" filter for the version.
            cursor: Pagination cursor for next page of results.
            **kwargs: Additional parameters
        
        Returns:
            ReleasesListResult

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