---
id: airbyte_agent_sdk-connectors-incident_io-connector
title: airbyte_agent_sdk.connectors.incident_io.connector
---

Module airbyte_agent_sdk.connectors.incident_io.connector
=========================================================
Incident-Io connector.

Classes
-------

<a id="AlertsQuery"></a>

`AlertsQuery(connector: IncidentIoConnector)`
:   Query class for Alerts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AlertsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[AlertsSearchData]`
    :   Search alerts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AlertsSearchFilter):
        - alert_source_id: ID of the alert source that generated this alert
        - attributes: Structured alert attributes
        - created_at: When the alert was created
        - deduplication_key: Deduplication key uniquely referencing this alert
        - description: Description of the alert
        - id: Unique identifier for the alert
        - resolved_at: When the alert was resolved
        - source_url: Link to the alert in the upstream system
        - status: Status of the alert: firing or resolved
        - title: Title of the alert
        - updated_at: When the alert was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AlertsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.Alert`
    :   Show a single alert by ID.
        
        Args:
            id: Alert ID
            **kwargs: Additional parameters
        
        Returns:
            Alert

    `list(self, page_size: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta[list[Alert], AlertsListResultMeta]`
    :   List all alerts for the account with cursor-based pagination.
        
        Args:
            page_size: Number of alerts per page
            after: Cursor for the next page of results
            **kwargs: Additional parameters
        
        Returns:
            AlertsListResult

<a id="CatalogTypesQuery"></a>

`CatalogTypesQuery(connector: IncidentIoConnector)`
:   Query class for CatalogTypes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CatalogTypesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[CatalogTypesSearchData]`
    :   Search catalog_types records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CatalogTypesSearchFilter):
        - annotations: Annotations metadata
        - categories: Categories this type belongs to
        - color: Display color
        - created_at: When the catalog type was created
        - description: Description of the catalog type
        - icon: Display icon
        - id: Unique identifier for the catalog type
        - is_editable: Whether entries can be edited
        - last_synced_at: When the catalog type was last synced
        - name: Name of the catalog type
        - ranked: Whether entries are ranked
        - registry_type: Registry type if synced from an integration
        - required_integrations: Integrations required for this type
        - schema_: Schema definition for the catalog type
        - semantic_type: Semantic type for special behavior
        - type_name: Programmatic type name
        - updated_at: When the catalog type was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CatalogTypesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.CatalogType`
    :   Show a single catalog type by ID.
        
        Args:
            id: Catalog type ID
            **kwargs: Additional parameters
        
        Returns:
            CatalogType

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult[list[CatalogType]]`
    :   List all catalog types for the organisation.
        
        Returns:
            CatalogTypesListResult

<a id="CustomFieldsQuery"></a>

`CustomFieldsQuery(connector: IncidentIoConnector)`
:   Query class for CustomFields entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CustomFieldsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[CustomFieldsSearchData]`
    :   Search custom_fields records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CustomFieldsSearchFilter):
        - created_at: When the custom field was created
        - description: Description of the custom field
        - field_type: Type of field
        - id: Unique identifier for the custom field
        - name: Name of the custom field
        - updated_at: When the custom field was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CustomFieldsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.CustomField`
    :   Get a single custom field by ID.
        
        Args:
            id: Custom field ID
            **kwargs: Additional parameters
        
        Returns:
            CustomField

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult[list[CustomField]]`
    :   List all custom fields for the organisation.
        
        Returns:
            CustomFieldsListResult

<a id="EscalationsQuery"></a>

`EscalationsQuery(connector: IncidentIoConnector)`
:   Query class for Escalations entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: EscalationsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[EscalationsSearchData]`
    :   Search escalations records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (EscalationsSearchFilter):
        - created_at: When the escalation was created
        - creator: The creator of this escalation
        - escalation_path_id: ID of the escalation path used
        - events: History of escalation events
        - id: Unique identifier for the escalation
        - priority: Priority of the escalation
        - related_alerts: Alerts related to this escalation
        - related_incidents: Incidents related to this escalation
        - status: Status: pending, triggered, acked, resolved, expired, cancelled
        - title: Title of the escalation
        - updated_at: When the escalation was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            EscalationsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.Escalation`
    :   Show a specific escalation by ID.
        
        Args:
            id: Escalation ID
            **kwargs: Additional parameters
        
        Returns:
            Escalation

    `list(self, page_size: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta[list[Escalation], EscalationsListResultMeta]`
    :   List all escalations for the account with cursor-based pagination.
        
        Args:
            page_size: Number of escalations per page
            after: Cursor for the next page of results
            **kwargs: Additional parameters
        
        Returns:
            EscalationsListResult

<a id="IncidentIoConnector"></a>

`IncidentIoConnector(auth_config: IncidentIoAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Incident-Io API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new incident-io connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., IncidentIoAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = IncidentIoConnector(auth_config=IncidentIoAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = IncidentIoConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = IncidentIoConnector(
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

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000, framework: FrameworkName | None = None, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Composes :func:`airbyte_agent_sdk.translation.translate_exceptions` for
        runtime wrapping (sync/async branch + output-size check + framework
        signal translation + optional internal retry loop), and adds
        connector-specific docstring augmentation on top of it.
        
        Usage:
            @mcp.tool()
            @IncidentIoConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @IncidentIoConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @IncidentIoConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
            async def execute(entity: str, action: str, params: dict):
                ...
        
        Args:
            update_docstring: When True, append connector capabilities to __doc__.
            max_output_chars: Max serialized output size before raising. Use None to disable.
            framework: One of ``"pydantic_ai" | "langchain" | "openai_agents" | "mcp"``.
                Defaults to None → auto-detect by attempting each framework's canonical
                import in order. Explicit always wins.
            internal_retries: How many transient runtime failures (429/5xx, network,
                timeout) to retry silently before surfacing. Default 0. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate ``(error, args, kwargs) -> bool``
                further restricting which retryable errors are safe for this specific
                tool. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback
                ``(error, args, kwargs) -> str | None``. Invoked after internal retries
                are exhausted OR were skipped via ``should_internal_retry`` returning
                False. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentIoCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            IncidentIoCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="IncidentRolesQuery"></a>

`IncidentRolesQuery(connector: IncidentIoConnector)`
:   Query class for IncidentRoles entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: IncidentRolesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentRolesSearchData]`
    :   Search incident_roles records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IncidentRolesSearchFilter):
        - created_at: When the role was created
        - description: Description of the role
        - id: Unique identifier for the incident role
        - instructions: Instructions for the role holder
        - name: Name of the role
        - required: Whether this role must be assigned
        - role_type: Type of role
        - shortform: Short form label for the role
        - updated_at: When the role was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            IncidentRolesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentRole`
    :   Get a single incident role by ID.
        
        Args:
            id: Incident role ID
            **kwargs: Additional parameters
        
        Returns:
            IncidentRole

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult[list[IncidentRole]]`
    :   List all incident roles for the organisation.
        
        Returns:
            IncidentRolesListResult

<a id="IncidentStatusesQuery"></a>

`IncidentStatusesQuery(connector: IncidentIoConnector)`
:   Query class for IncidentStatuses entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: IncidentStatusesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentStatusesSearchData]`
    :   Search incident_statuses records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IncidentStatusesSearchFilter):
        - category: Category: triage, active, post-incident, closed, etc.
        - created_at: When the status was created
        - description: Description of the status
        - id: Unique identifier for the status
        - name: Name of the status
        - rank: Rank for ordering
        - updated_at: When the status was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            IncidentStatusesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentStatus`
    :   Get a single incident status by ID.
        
        Args:
            id: Incident status ID
            **kwargs: Additional parameters
        
        Returns:
            IncidentStatus

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult[list[IncidentStatus]]`
    :   List all incident statuses for the organisation.
        
        Returns:
            IncidentStatusesListResult

<a id="IncidentTimestampsQuery"></a>

`IncidentTimestampsQuery(connector: IncidentIoConnector)`
:   Query class for IncidentTimestamps entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: IncidentTimestampsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentTimestampsSearchData]`
    :   Search incident_timestamps records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IncidentTimestampsSearchFilter):
        - id: Unique identifier for the timestamp
        - name: Name of the timestamp
        - rank: Rank for ordering
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            IncidentTimestampsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentTimestamp`
    :   Get a single incident timestamp by ID.
        
        Args:
            id: Incident timestamp ID
            **kwargs: Additional parameters
        
        Returns:
            IncidentTimestamp

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult[list[IncidentTimestamp]]`
    :   List all incident timestamps for the organisation.
        
        Returns:
            IncidentTimestampsListResult

<a id="IncidentUpdatesQuery"></a>

`IncidentUpdatesQuery(connector: IncidentIoConnector)`
:   Query class for IncidentUpdates entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: IncidentUpdatesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentUpdatesSearchData]`
    :   Search incident_updates records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IncidentUpdatesSearchFilter):
        - created_at: When the update was created
        - id: Unique identifier for the incident update
        - incident_id: ID of the incident this update belongs to
        - message: Update message content
        - new_incident_status: New incident status set by this update
        - new_severity: New severity set by this update
        - updater: Who made this update
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            IncidentUpdatesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page_size: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta[list[IncidentUpdate], IncidentUpdatesListResultMeta]`
    :   List all incident updates for the organisation with cursor-based pagination.
        
        Args:
            page_size: Number of incident updates per page
            after: Cursor for the next page of results
            **kwargs: Additional parameters
        
        Returns:
            IncidentUpdatesListResult

<a id="IncidentsQuery"></a>

`IncidentsQuery(connector: IncidentIoConnector)`
:   Query class for Incidents entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: IncidentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentsSearchData]`
    :   Search incidents records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IncidentsSearchFilter):
        - created_at: When the incident was created
        - creator: The user who created the incident
        - custom_field_entries: Custom field values for the incident
        - duration_metrics: Duration metrics associated with the incident
        - has_debrief: Whether the incident has had a debrief
        - id: Unique identifier for the incident
        - incident_role_assignments: Role assignments for the incident
        - incident_status: Current status of the incident
        - incident_timestamp_values: Timestamp values for the incident
        - incident_type: Type of the incident
        - mode: Mode of the incident: standard, retrospective, test, or tutorial
        - name: Name/title of the incident
        - permalink: Link to the incident in the dashboard
        - reference: Human-readable reference (e.g. INC-123)
        - severity: Severity of the incident
        - slack_channel_id: Slack channel ID for the incident
        - slack_channel_name: Slack channel name for the incident
        - slack_team_id: Slack team/workspace ID
        - summary: Detailed summary of the incident
        - updated_at: When the incident was last updated
        - visibility: Whether the incident is public or private
        - workload_minutes_late: Minutes of workload classified as late
        - workload_minutes_sleeping: Minutes of workload classified as sleeping
        - workload_minutes_total: Total workload minutes
        - workload_minutes_working: Minutes of workload classified as working
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            IncidentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.Incident`
    :   Get a single incident by ID or numeric reference.
        
        Args:
            id: Incident ID or numeric reference
            **kwargs: Additional parameters
        
        Returns:
            Incident

    `list(self, page_size: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta[list[Incident], IncidentsListResultMeta]`
    :   List all incidents for the organisation with cursor-based pagination.
        
        Args:
            page_size: Number of incidents per page
            after: Cursor for the next page of results
            **kwargs: Additional parameters
        
        Returns:
            IncidentsListResult

<a id="SchedulesQuery"></a>

`SchedulesQuery(connector: IncidentIoConnector)`
:   Query class for Schedules entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SchedulesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[SchedulesSearchData]`
    :   Search schedules records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SchedulesSearchFilter):
        - annotations: Annotations metadata
        - config: Schedule configuration with rotations
        - created_at: When the schedule was created
        - current_shifts: Currently active shifts
        - id: Unique identifier for the schedule
        - name: Name of the schedule
        - timezone: Timezone for the schedule
        - updated_at: When the schedule was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SchedulesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.Schedule`
    :   Get a single on-call schedule by ID.
        
        Args:
            id: Schedule ID
            **kwargs: Additional parameters
        
        Returns:
            Schedule

    `list(self, page_size: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta[list[Schedule], SchedulesListResultMeta]`
    :   List all on-call schedules with cursor-based pagination.
        
        Args:
            page_size: Number of schedules per page
            after: Cursor for the next page of results
            **kwargs: Additional parameters
        
        Returns:
            SchedulesListResult

<a id="SeveritiesQuery"></a>

`SeveritiesQuery(connector: IncidentIoConnector)`
:   Query class for Severities entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SeveritiesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[SeveritiesSearchData]`
    :   Search severities records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SeveritiesSearchFilter):
        - created_at: When the severity was created
        - description: Description of the severity
        - id: Unique identifier for the severity
        - name: Name of the severity
        - rank: Rank for ordering
        - updated_at: When the severity was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SeveritiesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.Severity`
    :   Get a single severity by ID.
        
        Args:
            id: Severity ID
            **kwargs: Additional parameters
        
        Returns:
            Severity

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult[list[Severity]]`
    :   List all severities for the organisation.
        
        Returns:
            SeveritiesListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: IncidentIoConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - base_role: Base role assigned to the user
        - custom_roles: Custom roles assigned to the user
        - email: Email address of the user
        - id: Unique identifier for the user
        - name: Full name of the user
        - role: Deprecated role field
        - slack_user_id: Slack user ID
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            UsersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.User`
    :   Get a single user by ID.
        
        Args:
            id: User ID
            **kwargs: Additional parameters
        
        Returns:
            User

    `list(self, page_size: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta[list[User], UsersListResultMeta]`
    :   List all users for the organisation with cursor-based pagination.
        
        Args:
            page_size: Number of users per page
            after: Cursor for the next page of results
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult