---
id: airbyte_agent_sdk-connectors-sendgrid-connector
title: airbyte_agent_sdk.connectors.sendgrid.connector
---

Module airbyte_agent_sdk.connectors.sendgrid.connector
======================================================
Sendgrid connector.

Classes
-------

<a id="BlocksQuery"></a>

`BlocksQuery(connector: SendgridConnector)`
:   Query class for Blocks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BlocksSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[BlocksSearchData]`
    :   Search blocks records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BlocksSearchFilter):
        - created: Unix timestamp when the block occurred
        - email: The blocked email address
        - reason: The reason for the block
        - status: The status code for the block
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BlocksSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, limit: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Block], BlocksListResultMeta]`
    :   Returns all blocked email records.
        
        Args:
            limit: Number of records to return
            offset: Number of records to skip for pagination
            **kwargs: Additional parameters
        
        Returns:
            BlocksListResult

<a id="BouncesQuery"></a>

`BouncesQuery(connector: SendgridConnector)`
:   Query class for Bounces entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BouncesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[BouncesSearchData]`
    :   Search bounces records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BouncesSearchFilter):
        - created: Unix timestamp when the bounce occurred
        - email: The email address that bounced
        - reason: The reason for the bounce
        - status: The enhanced status code for the bounce
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BouncesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, limit: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Bounce], BouncesListResultMeta]`
    :   Returns all bounced email records.
        
        Args:
            limit: Number of records to return
            offset: Number of records to skip for pagination
            **kwargs: Additional parameters
        
        Returns:
            BouncesListResult

<a id="CampaignsQuery"></a>

`CampaignsQuery(connector: SendgridConnector)`
:   Query class for Campaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[CampaignsSearchData]`
    :   Search campaigns records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignsSearchFilter):
        - channels: Channels for this campaign
        - created_at: When the campaign was created
        - id: Unique campaign identifier
        - is_abtest: Whether this campaign is an A/B test
        - name: Campaign name
        - status: Campaign status
        - updated_at: When the campaign was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CampaignsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]`
    :   Returns all marketing campaigns.
        
        Args:
            page_size: Maximum number of campaigns to return per page
            **kwargs: Additional parameters
        
        Returns:
            CampaignsListResult

<a id="ContactsQuery"></a>

`ContactsQuery(connector: SendgridConnector)`
:   Query class for Contacts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ContactsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[ContactsSearchData]`
    :   Search contacts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ContactsSearchFilter):
        - address_line_1: Address line 1
        - address_line_2: Address line 2
        - alternate_emails: Alternate email addresses
        - city: City
        - contact_id: Unique contact identifier used by Airbyte
        - country: Country
        - created_at: When the contact was created
        - custom_fields: Custom field values
        - email: Contact email address
        - facebook: Facebook ID
        - first_name: Contact first name
        - last_name: Contact last name
        - line: LINE ID
        - list_ids: IDs of lists the contact belongs to
        - phone_number: Phone number
        - postal_code: Postal code
        - state_province_region: State, province, or region
        - unique_name: Unique name for the contact
        - updated_at: When the contact was last updated
        - whatsapp: WhatsApp number
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ContactsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.Contact`
    :   Returns the full details and all fields for the specified contact.
        
        Args:
            id: The ID of the contact
            **kwargs: Additional parameters
        
        Returns:
            Contact

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Contact], ContactsListResultMeta]`
    :   Returns a sample of contacts. Use the export endpoint for full lists.
        
        Returns:
            ContactsListResult

<a id="GlobalSuppressionsQuery"></a>

`GlobalSuppressionsQuery(connector: SendgridConnector)`
:   Query class for GlobalSuppressions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: GlobalSuppressionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[GlobalSuppressionsSearchData]`
    :   Search global_suppressions records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (GlobalSuppressionsSearchFilter):
        - created: Unix timestamp when the global suppression was created
        - email: The globally suppressed email address
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            GlobalSuppressionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, limit: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[GlobalSuppression], GlobalSuppressionsListResultMeta]`
    :   Returns all globally unsubscribed email addresses.
        
        Args:
            limit: Number of records to return
            offset: Number of records to skip for pagination
            **kwargs: Additional parameters
        
        Returns:
            GlobalSuppressionsListResult

<a id="InvalidEmailsQuery"></a>

`InvalidEmailsQuery(connector: SendgridConnector)`
:   Query class for InvalidEmails entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: InvalidEmailsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[InvalidEmailsSearchData]`
    :   Search invalid_emails records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (InvalidEmailsSearchFilter):
        - created: Unix timestamp when the invalid email was recorded
        - email: The invalid email address
        - reason: The reason the email is invalid
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            InvalidEmailsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, limit: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[InvalidEmail], InvalidEmailsListResultMeta]`
    :   Returns all invalid email records.
        
        Args:
            limit: Number of records to return
            offset: Number of records to skip for pagination
            **kwargs: Additional parameters
        
        Returns:
            InvalidEmailsListResult

<a id="ListsQuery"></a>

`ListsQuery(connector: SendgridConnector)`
:   Query class for Lists entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ListsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[ListsSearchData]`
    :   Search lists records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ListsSearchFilter):
        - metadata: Metadata about the list resource
        - contact_count: Number of contacts in the list
        - id: Unique list identifier
        - name: Name of the list
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ListsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.List`
    :   Returns a specific marketing list by ID.
        
        Args:
            id: The ID of the list
            **kwargs: Additional parameters
        
        Returns:
            List

    `list(self, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[List], ListsListResultMeta]`
    :   Returns all marketing contact lists.
        
        Args:
            page_size: Maximum number of lists to return
            **kwargs: Additional parameters
        
        Returns:
            ListsListResult

<a id="SegmentsQuery"></a>

`SegmentsQuery(connector: SendgridConnector)`
:   Query class for Segments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SegmentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SegmentsSearchData]`
    :   Search segments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SegmentsSearchFilter):
        - contacts_count: Number of contacts in the segment
        - created_at: When the segment was created
        - id: Unique segment identifier
        - name: Segment name
        - next_sample_update: When the next sample update will occur
        - parent_list_ids: IDs of parent lists
        - query_version: Query version used
        - sample_updated_at: When the sample was last updated
        - status: Segment status details
        - updated_at: When the segment was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SegmentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, segment_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.Segment`
    :   Returns a specific segment by ID.
        
        Args:
            segment_id: The ID of the segment
            **kwargs: Additional parameters
        
        Returns:
            Segment

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult[list[Segment]]`
    :   Returns all segments (v2).
        
        Returns:
            SegmentsListResult

<a id="SendgridConnector"></a>

`SendgridConnector(auth_config: SendgridAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Sendgrid API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new sendgrid connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., SendgridAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = SendgridConnector(auth_config=SendgridAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = SendgridConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = SendgridConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'SendgridAuthConfig'", name: str | None = None, replication_config: "'SendgridReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A SendgridConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await SendgridConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=SendgridAuthConfig(api_key="..."),
            )
        
            # With replication config (required for this connector):
            connector = await SendgridConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=SendgridAuthConfig(api_key="..."),
                replication_config=SendgridReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @SendgridConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @SendgridConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await SendgridConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            SendgridCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="SinglesendStatsQuery"></a>

`SinglesendStatsQuery(connector: SendgridConnector)`
:   Query class for SinglesendStats entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SinglesendStatsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SinglesendStatsSearchData]`
    :   Search singlesend_stats records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SinglesendStatsSearchFilter):
        - ab_phase: The A/B test phase
        - ab_variation: The A/B test variation
        - aggregation: The aggregation type
        - id: The single send ID
        - stats: Email statistics for the single send
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SinglesendStatsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[SingleSendStats], SinglesendStatsListResultMeta]`
    :   Returns stats for all single sends.
        
        Args:
            page_size: Maximum number of stats to return per page
            **kwargs: Additional parameters
        
        Returns:
            SinglesendStatsListResult

<a id="SinglesendsQuery"></a>

`SinglesendsQuery(connector: SendgridConnector)`
:   Query class for Singlesends entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SinglesendsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SinglesendsSearchData]`
    :   Search singlesends records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SinglesendsSearchFilter):
        - categories: Categories associated with this single send
        - created_at: When the single send was created
        - id: Unique single send identifier
        - is_abtest: Whether this is an A/B test
        - name: Single send name
        - send_at: Scheduled send time
        - status: Current status: draft, scheduled, or triggered
        - updated_at: When the single send was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SinglesendsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SingleSend`
    :   Returns details about one single send.
        
        Args:
            id: The ID of the single send
            **kwargs: Additional parameters
        
        Returns:
            SingleSend

    `list(self, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[SingleSend], SinglesendsListResultMeta]`
    :   Returns all single sends.
        
        Args:
            page_size: Maximum number of single sends to return per page
            **kwargs: Additional parameters
        
        Returns:
            SinglesendsListResult

<a id="SpamReportsQuery"></a>

`SpamReportsQuery(connector: SendgridConnector)`
:   Query class for SpamReports entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, limit: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[SpamReport], SpamReportsListResultMeta]`
    :   Returns all spam report records.
        
        Args:
            limit: Number of records to return
            offset: Number of records to skip for pagination
            **kwargs: Additional parameters
        
        Returns:
            SpamReportsListResult

<a id="SuppressionGroupMembersQuery"></a>

`SuppressionGroupMembersQuery(connector: SendgridConnector)`
:   Query class for SuppressionGroupMembers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SuppressionGroupMembersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SuppressionGroupMembersSearchData]`
    :   Search suppression_group_members records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SuppressionGroupMembersSearchFilter):
        - created_at: Unix timestamp when the suppression was created
        - email: The suppressed email address
        - group_id: ID of the suppression group
        - group_name: Name of the suppression group
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SuppressionGroupMembersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, limit: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[SuppressionGroupMember], SuppressionGroupMembersListResultMeta]`
    :   Returns all suppressions across all groups.
        
        Args:
            limit: Number of records to return
            offset: Number of records to skip for pagination
            **kwargs: Additional parameters
        
        Returns:
            SuppressionGroupMembersListResult

<a id="SuppressionGroupsQuery"></a>

`SuppressionGroupsQuery(connector: SendgridConnector)`
:   Query class for SuppressionGroups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SuppressionGroupsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SuppressionGroupsSearchData]`
    :   Search suppression_groups records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SuppressionGroupsSearchFilter):
        - description: Description of the suppression group
        - id: Unique suppression group identifier
        - is_default: Whether this is the default suppression group
        - name: Suppression group name
        - unsubscribes: Number of unsubscribes in this group
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SuppressionGroupsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, group_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SuppressionGroup`
    :   Returns information about a single suppression group.
        
        Args:
            group_id: The ID of the suppression group
            **kwargs: Additional parameters
        
        Returns:
            SuppressionGroup

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult[list[SuppressionGroup]]`
    :   Returns all suppression (unsubscribe) groups.
        
        Returns:
            SuppressionGroupsListResult

<a id="TemplatesQuery"></a>

`TemplatesQuery(connector: SendgridConnector)`
:   Query class for Templates entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TemplatesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[TemplatesSearchData]`
    :   Search templates records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TemplatesSearchFilter):
        - generation: Template generation (legacy or dynamic)
        - id: Unique template identifier
        - name: Template name
        - updated_at: When the template was last updated
        - versions: Template versions
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TemplatesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, template_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.Template`
    :   Returns a single transactional template.
        
        Args:
            template_id: The ID of the template
            **kwargs: Additional parameters
        
        Returns:
            Template

    `list(self, generations: str | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Template], TemplatesListResultMeta]`
    :   Returns paged transactional templates (legacy and dynamic).
        
        Args:
            generations: Template generations to return
            page_size: Number of templates per page
            **kwargs: Additional parameters
        
        Returns:
            TemplatesListResult