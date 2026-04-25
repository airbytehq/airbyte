---
id: airbyte_agent_sdk-connectors-freshdesk-connector
title: airbyte_agent_sdk.connectors.freshdesk.connector
---

Module airbyte_agent_sdk.connectors.freshdesk.connector
=======================================================
Freshdesk connector.

Classes
-------

<a id="AgentsQuery"></a>

`AgentsQuery(connector: FreshdeskConnector)`
:   Query class for Agents entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AgentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[AgentsSearchData]`
    :   Search agents records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AgentsSearchFilter):
        - id: Unique agent ID
        - available: Whether the agent is available
        - available_since: Timestamp since the agent has been available
        - contact: Contact details of the agent including name, email, phone, and job title
        - occasional: Whether the agent is an occasional agent
        - signature: Signature of the agent (HTML)
        - ticket_scope: Ticket scope: 1=Global, 2=Group, 3=Restricted
        - type_: Agent type: support_agent, field_agent, collaborator
        - last_active_at: Timestamp of last agent activity
        - created_at: Agent creation timestamp
        - updated_at: Agent last update timestamp
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AgentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.Agent`
    :   Get a single agent by ID
        
        Args:
            id: Agent ID
            **kwargs: Additional parameters
        
        Returns:
            Agent

    `list(self, per_page: int | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[Agent], AgentsListResultMeta]`
    :   Returns a paginated list of agents
        
        Args:
            per_page: Number of items per page (max 100)
            page: Page number (starts at 1)
            **kwargs: Additional parameters
        
        Returns:
            AgentsListResult

<a id="CompaniesQuery"></a>

`CompaniesQuery(connector: FreshdeskConnector)`
:   Query class for Companies entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.Company`
    :   Get a single company by ID
        
        Args:
            id: Company ID
            **kwargs: Additional parameters
        
        Returns:
            Company

    `list(self, per_page: int | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[Company], CompaniesListResultMeta]`
    :   Returns a paginated list of companies
        
        Args:
            per_page: Number of items per page (max 100)
            page: Page number (starts at 1)
            **kwargs: Additional parameters
        
        Returns:
            CompaniesListResult

<a id="ContactsQuery"></a>

`ContactsQuery(connector: FreshdeskConnector)`
:   Query class for Contacts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.Contact`
    :   Get a single contact by ID
        
        Args:
            id: Contact ID
            **kwargs: Additional parameters
        
        Returns:
            Contact

    `list(self, per_page: int | None = None, page: int | None = None, updated_since: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[Contact], ContactsListResultMeta]`
    :   Returns a paginated list of contacts
        
        Args:
            per_page: Number of items per page (max 100)
            page: Page number (starts at 1)
            updated_since: Return contacts updated since this timestamp (ISO 8601)
            **kwargs: Additional parameters
        
        Returns:
            ContactsListResult

<a id="FreshdeskConnector"></a>

`FreshdeskConnector(auth_config: FreshdeskAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, subdomain: str | None = None)`
:   Type-safe Freshdesk API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new freshdesk connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., FreshdeskAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            subdomain: Your Freshdesk subdomain (e.g., "acme" for acme.freshdesk.com)
    Examples:
        # Local mode (direct API calls)
        connector = FreshdeskConnector(auth_config=FreshdeskAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = FreshdeskConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = FreshdeskConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'FreshdeskAuthConfig'", name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> airbyte_agent_sdk.connectors.freshdesk.connector.FreshdeskConnector`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config (same as local mode)
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Optional replication settings dict.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A FreshdeskConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await FreshdeskConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=FreshdeskAuthConfig(api_key="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @FreshdeskConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @FreshdeskConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await FreshdeskConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            FreshdeskCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="GroupsQuery"></a>

`GroupsQuery(connector: FreshdeskConnector)`
:   Query class for Groups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: GroupsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[GroupsSearchData]`
    :   Search groups records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (GroupsSearchFilter):
        - id: Unique group ID
        - name: Name of the group
        - description: Description of the group
        - auto_ticket_assign: Auto ticket assignment: 0=Disabled, 1=Round Robin, 2=Skill Based, 3=Load Based
        - business_hour_id: ID of the associated business hour
        - escalate_to: User ID for escalation
        - group_type: Type of the group (e.g., support_agent_group)
        - unassigned_for: Time after which escalation triggers
        - created_at: Group creation timestamp
        - updated_at: Group last update timestamp
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            GroupsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.Group`
    :   Get a single group by ID
        
        Args:
            id: Group ID
            **kwargs: Additional parameters
        
        Returns:
            Group

    `list(self, per_page: int | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[Group], GroupsListResultMeta]`
    :   Returns a paginated list of groups
        
        Args:
            per_page: Number of items per page (max 100)
            page: Page number (starts at 1)
            **kwargs: Additional parameters
        
        Returns:
            GroupsListResult

<a id="RolesQuery"></a>

`RolesQuery(connector: FreshdeskConnector)`
:   Query class for Roles entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.Role`
    :   Get a single role by ID
        
        Args:
            id: Role ID
            **kwargs: Additional parameters
        
        Returns:
            Role

    `list(self, per_page: int | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[Role], RolesListResultMeta]`
    :   Returns a paginated list of roles
        
        Args:
            per_page: Number of items per page (max 100)
            page: Page number (starts at 1)
            **kwargs: Additional parameters
        
        Returns:
            RolesListResult

<a id="SatisfactionRatingsQuery"></a>

`SatisfactionRatingsQuery(connector: FreshdeskConnector)`
:   Query class for SatisfactionRatings entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, per_page: int | None = None, page: int | None = None, created_since: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[SatisfactionRating], SatisfactionRatingsListResultMeta]`
    :   Returns a paginated list of satisfaction ratings
        
        Args:
            per_page: Number of items per page (max 100)
            page: Page number (starts at 1)
            created_since: Return ratings created since this timestamp (ISO 8601)
            **kwargs: Additional parameters
        
        Returns:
            SatisfactionRatingsListResult

<a id="SurveysQuery"></a>

`SurveysQuery(connector: FreshdeskConnector)`
:   Query class for Surveys entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, per_page: int | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[Survey], SurveysListResultMeta]`
    :   Returns a paginated list of surveys
        
        Args:
            per_page: Number of items per page (max 100)
            page: Page number (starts at 1)
            **kwargs: Additional parameters
        
        Returns:
            SurveysListResult

<a id="TicketFieldsQuery"></a>

`TicketFieldsQuery(connector: FreshdeskConnector)`
:   Query class for TicketFields entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, per_page: int | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[TicketField], TicketFieldsListResultMeta]`
    :   Returns a list of all ticket fields
        
        Args:
            per_page: Number of items per page (max 100)
            page: Page number (starts at 1)
            **kwargs: Additional parameters
        
        Returns:
            TicketFieldsListResult

<a id="TicketsQuery"></a>

`TicketsQuery(connector: FreshdeskConnector)`
:   Query class for Tickets entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TicketsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[TicketsSearchData]`
    :   Search tickets records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TicketsSearchFilter):
        - id: Unique ticket ID
        - subject: Subject of the ticket
        - description: HTML content of the ticket
        - description_text: Plain text content of the ticket
        - status: Status: 2=Open, 3=Pending, 4=Resolved, 5=Closed
        - priority: Priority: 1=Low, 2=Medium, 3=High, 4=Urgent
        - source: Source: 1=Email, 2=Portal, 3=Phone, 7=Chat, 9=Feedback Widget, 10=Outbound Email
        - type_: Ticket type
        - requester_id: ID of the requester
        - requester: Requester details including name, email, and contact info
        - responder_id: ID of the agent to whom the ticket is assigned
        - group_id: ID of the group to which the ticket is assigned
        - company_id: Company ID of the requester
        - product_id: ID of the product associated with the ticket
        - email_config_id: ID of the email config used for the ticket
        - cc_emails: CC email addresses
        - ticket_cc_emails: Ticket CC email addresses
        - to_emails: To email addresses
        - fwd_emails: Forwarded email addresses
        - reply_cc_emails: Reply CC email addresses
        - tags: Tags associated with the ticket
        - custom_fields: Custom fields associated with the ticket
        - due_by: Resolution due by timestamp
        - fr_due_by: First response due by timestamp
        - fr_escalated: Whether the first response time was breached
        - is_escalated: Whether the ticket is escalated
        - nr_due_by: Next response due by timestamp
        - nr_escalated: Whether the next response time was breached
        - spam: Whether the ticket is marked as spam
        - association_type: Association type for parent/child tickets
        - associated_tickets_count: Number of associated tickets
        - stats: Ticket statistics including response and resolution times
        - created_at: Ticket creation timestamp
        - updated_at: Ticket last update timestamp
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TicketsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.Ticket`
    :   Get a single ticket by ID
        
        Args:
            id: Ticket ID
            **kwargs: Additional parameters
        
        Returns:
            Ticket

    `list(self, per_page: int | None = None, page: int | None = None, updated_since: str | None = None, order_by: str | None = None, order_type: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[Ticket], TicketsListResultMeta]`
    :   Returns a paginated list of tickets. By default returns tickets created in the past 30 days. Use updated_since to get older tickets.
        
        Args:
            per_page: Number of items per page (max 100)
            page: Page number (starts at 1)
            updated_since: Return tickets updated since this timestamp (ISO 8601)
            order_by: Sort field
            order_type: Sort order
            **kwargs: Additional parameters
        
        Returns:
            TicketsListResult

<a id="TimeEntriesQuery"></a>

`TimeEntriesQuery(connector: FreshdeskConnector)`
:   Query class for TimeEntries entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, per_page: int | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[TimeEntry], TimeEntriesListResultMeta]`
    :   Returns a paginated list of time entries
        
        Args:
            per_page: Number of items per page (max 100)
            page: Page number (starts at 1)
            **kwargs: Additional parameters
        
        Returns:
            TimeEntriesListResult