---
id: airbyte_agent_sdk-connectors-harvest-connector
title: airbyte_agent_sdk.connectors.harvest.connector
---

Module airbyte_agent_sdk.connectors.harvest.connector
=====================================================
Harvest connector.

Classes
-------

<a id="ClientsQuery"></a>

`ClientsQuery(connector: HarvestConnector)`
:   Query class for Clients entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ClientsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ClientsSearchData]`
    :   Search clients records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ClientsSearchFilter):
        - address: The client's postal address
        - created_at: When the client record was created
        - currency: The currency used by the client
        - id: Unique identifier for the client
        - is_active: Whether the client is active
        - name: The client's name
        - updated_at: When the client record was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ClientsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.Client`
    :   Get a single client by ID
        
        Args:
            id: Client ID
            **kwargs: Additional parameters
        
        Returns:
            Client

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Client], ClientsListResultMeta]`
    :   Returns a paginated list of clients
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            ClientsListResult

<a id="CompanyQuery"></a>

`CompanyQuery(connector: HarvestConnector)`
:   Query class for Company entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CompanySearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[CompanySearchData]`
    :   Search company records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CompanySearchFilter):
        - base_uri: The base URI
        - currency: Currency used by the company
        - full_domain: The full domain name
        - is_active: Whether the company is active
        - name: The name of the company
        - plan_type: The plan type
        - weekly_capacity: Weekly capacity in seconds
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CompanySearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.Company`
    :   Returns the company information for the authenticated account
        
        Returns:
            Company

<a id="ContactsQuery"></a>

`ContactsQuery(connector: HarvestConnector)`
:   Query class for Contacts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ContactsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ContactsSearchData]`
    :   Search contacts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ContactsSearchFilter):
        - client: Client associated with the contact
        - created_at: When created
        - email: Email address
        - first_name: First name
        - id: Unique identifier
        - last_name: Last name
        - title: Job title
        - updated_at: When last updated
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.Contact`
    :   Get a single contact by ID
        
        Args:
            id: Contact ID
            **kwargs: Additional parameters
        
        Returns:
            Contact

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Contact], ContactsListResultMeta]`
    :   Returns a paginated list of contacts
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            ContactsListResult

<a id="EstimateItemCategoriesQuery"></a>

`EstimateItemCategoriesQuery(connector: HarvestConnector)`
:   Query class for EstimateItemCategories entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: EstimateItemCategoriesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[EstimateItemCategoriesSearchData]`
    :   Search estimate_item_categories records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (EstimateItemCategoriesSearchFilter):
        - created_at: When created
        - id: Unique identifier
        - name: Category name
        - updated_at: When last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            EstimateItemCategoriesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.EstimateItemCategory`
    :   Get a single estimate item category by ID
        
        Args:
            id: Estimate item category ID
            **kwargs: Additional parameters
        
        Returns:
            EstimateItemCategory

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[EstimateItemCategory], EstimateItemCategoriesListResultMeta]`
    :   Returns a paginated list of estimate item categories
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            EstimateItemCategoriesListResult

<a id="EstimatesQuery"></a>

`EstimatesQuery(connector: HarvestConnector)`
:   Query class for Estimates entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: EstimatesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[EstimatesSearchData]`
    :   Search estimates records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (EstimatesSearchFilter):
        - amount: Total amount
        - client: Client details
        - created_at: When created
        - currency: Currency
        - id: Unique identifier
        - issue_date: Issue date
        - number: Estimate number
        - state: Current state
        - subject: Subject
        - updated_at: When last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            EstimatesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.Estimate`
    :   Get a single estimate by ID
        
        Args:
            id: Estimate ID
            **kwargs: Additional parameters
        
        Returns:
            Estimate

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Estimate], EstimatesListResultMeta]`
    :   Returns a paginated list of estimates
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            EstimatesListResult

<a id="ExpenseCategoriesQuery"></a>

`ExpenseCategoriesQuery(connector: HarvestConnector)`
:   Query class for ExpenseCategories entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ExpenseCategoriesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ExpenseCategoriesSearchData]`
    :   Search expense_categories records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ExpenseCategoriesSearchFilter):
        - created_at: When created
        - id: Unique identifier
        - is_active: Whether active
        - name: Category name
        - unit_name: Unit name
        - unit_price: Unit price
        - updated_at: When last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ExpenseCategoriesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.ExpenseCategory`
    :   Get a single expense category by ID
        
        Args:
            id: Expense category ID
            **kwargs: Additional parameters
        
        Returns:
            ExpenseCategory

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[ExpenseCategory], ExpenseCategoriesListResultMeta]`
    :   Returns a paginated list of expense categories
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            ExpenseCategoriesListResult

<a id="ExpensesQuery"></a>

`ExpensesQuery(connector: HarvestConnector)`
:   Query class for Expenses entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ExpensesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ExpensesSearchData]`
    :   Search expenses records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ExpensesSearchFilter):
        - billable: Whether billable
        - client: Associated client
        - created_at: When created
        - expense_category: Expense category
        - id: Unique identifier
        - is_billed: Whether billed
        - notes: Notes
        - project: Associated project
        - spent_date: Date spent
        - total_cost: Total cost
        - updated_at: When last updated
        - user: Associated user
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ExpensesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.Expense`
    :   Get a single expense by ID
        
        Args:
            id: Expense ID
            **kwargs: Additional parameters
        
        Returns:
            Expense

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Expense], ExpensesListResultMeta]`
    :   Returns a paginated list of expenses
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            ExpensesListResult

<a id="HarvestConnector"></a>

`HarvestConnector(auth_config: HarvestAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Harvest API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new harvest connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., HarvestAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = HarvestConnector(auth_config=HarvestAuthConfig(client_id="...", client_secret="...", refresh_token="...", account_id="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = HarvestConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = HarvestConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'HarvestAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'HarvestReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A HarvestConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await HarvestConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=HarvestAuthConfig(client_id="...", client_secret="...", refresh_token="...", account_id="..."),
            )
        
            # With replication config (required for this connector):
            connector = await HarvestConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=HarvestAuthConfig(client_id="...", client_secret="...", refresh_token="...", account_id="..."),
                replication_config=HarvestReplicationConfig(replication_start_date="..."),
            )
        
            # With server-side OAuth:
            connector = await HarvestConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=HarvestReplicationConfig(replication_start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'HarvestReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await HarvestConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Harvest Source",
                replication_config=HarvestReplicationConfig(replication_start_date="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @HarvestConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @HarvestConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await HarvestConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            HarvestCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="InvoiceItemCategoriesQuery"></a>

`InvoiceItemCategoriesQuery(connector: HarvestConnector)`
:   Query class for InvoiceItemCategories entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: InvoiceItemCategoriesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[InvoiceItemCategoriesSearchData]`
    :   Search invoice_item_categories records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (InvoiceItemCategoriesSearchFilter):
        - created_at: When created
        - id: Unique identifier
        - name: Category name
        - updated_at: When last updated
        - use_as_expense: Whether used as expense type
        - use_as_service: Whether used as service type
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            InvoiceItemCategoriesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.InvoiceItemCategory`
    :   Get a single invoice item category by ID
        
        Args:
            id: Invoice item category ID
            **kwargs: Additional parameters
        
        Returns:
            InvoiceItemCategory

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[InvoiceItemCategory], InvoiceItemCategoriesListResultMeta]`
    :   Returns a paginated list of invoice item categories
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            InvoiceItemCategoriesListResult

<a id="InvoicesQuery"></a>

`InvoicesQuery(connector: HarvestConnector)`
:   Query class for Invoices entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: InvoicesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[InvoicesSearchData]`
    :   Search invoices records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (InvoicesSearchFilter):
        - amount: Total amount
        - client: Client details
        - created_at: When created
        - currency: Currency
        - due_amount: Amount due
        - due_date: Due date
        - id: Unique identifier
        - issue_date: Issue date
        - number: Invoice number
        - state: Current state
        - subject: Subject
        - updated_at: When last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            InvoicesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.Invoice`
    :   Get a single invoice by ID
        
        Args:
            id: Invoice ID
            **kwargs: Additional parameters
        
        Returns:
            Invoice

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Invoice], InvoicesListResultMeta]`
    :   Returns a paginated list of invoices
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            InvoicesListResult

<a id="ProjectsQuery"></a>

`ProjectsQuery(connector: HarvestConnector)`
:   Query class for Projects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProjectsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ProjectsSearchData]`
    :   Search projects records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProjectsSearchFilter):
        - budget: Budget amount
        - client: Client details
        - code: Project code
        - created_at: When created
        - hourly_rate: Hourly rate
        - id: Unique identifier
        - is_active: Whether active
        - is_billable: Whether billable
        - name: Project name
        - starts_on: Start date
        - updated_at: When last updated
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.Project`
    :   Get a single project by ID
        
        Args:
            id: Project ID
            **kwargs: Additional parameters
        
        Returns:
            Project

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Project], ProjectsListResultMeta]`
    :   Returns a paginated list of projects
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            ProjectsListResult

<a id="RolesQuery"></a>

`RolesQuery(connector: HarvestConnector)`
:   Query class for Roles entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: RolesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[RolesSearchData]`
    :   Search roles records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (RolesSearchFilter):
        - created_at: When created
        - id: Unique identifier
        - name: Role name
        - updated_at: When last updated
        - user_ids: User IDs with this role
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            RolesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.Role`
    :   Get a single role by ID
        
        Args:
            id: Role ID
            **kwargs: Additional parameters
        
        Returns:
            Role

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Role], RolesListResultMeta]`
    :   Returns a paginated list of roles
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            RolesListResult

<a id="TaskAssignmentsQuery"></a>

`TaskAssignmentsQuery(connector: HarvestConnector)`
:   Query class for TaskAssignments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TaskAssignmentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TaskAssignmentsSearchData]`
    :   Search task_assignments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TaskAssignmentsSearchFilter):
        - billable: Whether billable
        - created_at: When created
        - hourly_rate: Hourly rate
        - id: Unique identifier
        - is_active: Whether active
        - project: Associated project
        - task: Associated task
        - updated_at: When last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TaskAssignmentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[TaskAssignment], TaskAssignmentsListResultMeta]`
    :   Returns a paginated list of task assignments across all projects
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            TaskAssignmentsListResult

<a id="TasksQuery"></a>

`TasksQuery(connector: HarvestConnector)`
:   Query class for Tasks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TasksSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TasksSearchData]`
    :   Search tasks records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TasksSearchFilter):
        - billable_by_default: Whether billable by default
        - created_at: When created
        - default_hourly_rate: Default hourly rate
        - id: Unique identifier
        - is_active: Whether active
        - name: Task name
        - updated_at: When last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TasksSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.Task`
    :   Get a single task by ID
        
        Args:
            id: Task ID
            **kwargs: Additional parameters
        
        Returns:
            Task

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Task], TasksListResultMeta]`
    :   Returns a paginated list of tasks
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            TasksListResult

<a id="TimeEntriesQuery"></a>

`TimeEntriesQuery(connector: HarvestConnector)`
:   Query class for TimeEntries entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TimeEntriesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TimeEntriesSearchData]`
    :   Search time_entries records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TimeEntriesSearchFilter):
        - billable: Whether billable
        - client: Associated client
        - created_at: When created
        - hours: Hours logged
        - id: Unique identifier
        - is_billed: Whether billed
        - notes: Notes
        - project: Associated project
        - spent_date: Date time was spent
        - task: Associated task
        - updated_at: When last updated
        - user: Associated user
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TimeEntriesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.TimeEntry`
    :   Get a single time entry by ID
        
        Args:
            id: Time entry ID
            **kwargs: Additional parameters
        
        Returns:
            TimeEntry

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[TimeEntry], TimeEntriesListResultMeta]`
    :   Returns a paginated list of time entries
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            TimeEntriesListResult

<a id="TimeProjectsQuery"></a>

`TimeProjectsQuery(connector: HarvestConnector)`
:   Query class for TimeProjects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TimeProjectsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TimeProjectsSearchData]`
    :   Search time_projects records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TimeProjectsSearchFilter):
        - billable_amount: Total billable amount
        - billable_hours: Number of billable hours
        - client_id: Client identifier
        - client_name: Client name
        - currency: Currency code
        - project_id: Project identifier
        - project_name: Project name
        - total_hours: Total hours spent
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TimeProjectsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, from_: str, to: str, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[TimeProject], TimeProjectsListResultMeta]`
    :   Returns time report data grouped by project for a given date range
        
        Args:
            from_: Start date for the report in YYYYMMDD format
            to: End date for the report in YYYYMMDD format
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            TimeProjectsListResult

<a id="TimeTasksQuery"></a>

`TimeTasksQuery(connector: HarvestConnector)`
:   Query class for TimeTasks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TimeTasksSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TimeTasksSearchData]`
    :   Search time_tasks records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TimeTasksSearchFilter):
        - billable_amount: Total billable amount
        - billable_hours: Number of billable hours
        - currency: Currency code
        - task_id: Task identifier
        - task_name: Task name
        - total_hours: Total hours spent
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TimeTasksSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, from_: str, to: str, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[TimeTask], TimeTasksListResultMeta]`
    :   Returns time report data grouped by task for a given date range
        
        Args:
            from_: Start date for the report in YYYYMMDD format
            to: End date for the report in YYYYMMDD format
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            TimeTasksListResult

<a id="UserAssignmentsQuery"></a>

`UserAssignmentsQuery(connector: HarvestConnector)`
:   Query class for UserAssignments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UserAssignmentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[UserAssignmentsSearchData]`
    :   Search user_assignments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UserAssignmentsSearchFilter):
        - budget: Budget
        - created_at: When created
        - hourly_rate: Hourly rate
        - id: Unique identifier
        - is_active: Whether active
        - is_project_manager: Whether project manager
        - project: Associated project
        - updated_at: When last updated
        - user: Associated user
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            UserAssignmentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[UserAssignment], UserAssignmentsListResultMeta]`
    :   Returns a paginated list of user assignments across all projects
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            UserAssignmentsListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: HarvestConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - avatar_url: Avatar URL
        - cost_rate: Cost rate
        - created_at: When created
        - default_hourly_rate: Default hourly rate
        - email: Email address
        - first_name: First name
        - id: Unique identifier
        - is_active: Whether active
        - is_contractor: Whether contractor
        - last_name: Last name
        - roles: Assigned roles
        - telephone: Phone number
        - timezone: Timezone
        - updated_at: When last updated
        - weekly_capacity: Weekly capacity in seconds
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.User`
    :   Get a single user by ID
        
        Args:
            id: User ID
            **kwargs: Additional parameters
        
        Returns:
            User

    `list(self, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[User], UsersListResultMeta]`
    :   Returns a paginated list of users in the Harvest account
        
        Args:
            per_page: Number of records per page (max 2000)
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult