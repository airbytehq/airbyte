---
id: airbyte_agent_sdk-connectors-paypal_transaction-connector
title: airbyte_agent_sdk.connectors.paypal_transaction.connector
---

Module airbyte_agent_sdk.connectors.paypal_transaction.connector
================================================================
Paypal-Transaction connector.

Classes
-------

<a id="BalancesQuery"></a>

`BalancesQuery(connector: PaypalTransactionConnector)`
:   Query class for Balances entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BalancesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[BalancesSearchData]`
    :   Search balances records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BalancesSearchFilter):
        - account_id: The unique identifier of the account.
        - as_of_time: The timestamp when the balances data was reported.
        - balances: Object containing information about the account balances.
        - last_refresh_time: The timestamp when the balances data was last refreshed.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BalancesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, as_of_time: str | None = None, currency_code: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult[BalancesResponse]`
    :   List all balances for a PayPal account. Specify date time to list balances for that time. It takes a maximum of three hours for balances to appear. Lists balances up to the previous three years.
        
        
        Args:
            as_of_time: List balances at the date time provided in ISO 8601 format. Returns the last refreshed balance when not provided.
        
            currency_code: Three-character ISO-4217 currency code to filter balances.
        
            **kwargs: Additional parameters
        
        Returns:
            BalancesListResult

<a id="ListDisputesQuery"></a>

`ListDisputesQuery(connector: PaypalTransactionConnector)`
:   Query class for ListDisputes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ListDisputesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[ListDisputesSearchData]`
    :   Search list_disputes records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ListDisputesSearchFilter):
        - create_time: The timestamp when the dispute was created.
        - dispute_amount: Details about the disputed amount.
        - dispute_channel: The channel through which the dispute was initiated.
        - dispute_id: The unique identifier for the dispute.
        - dispute_life_cycle_stage: The stage in the life cycle of the dispute.
        - dispute_state: The current state of the dispute.
        - disputed_transactions: Details of transactions involved in the dispute.
        - links: Links related to the dispute.
        - outcome: The outcome of the dispute resolution.
        - reason: The reason for the dispute.
        - status: The current status of the dispute.
        - update_time: The timestamp when the dispute was last updated.
        - updated_time_cut: The cut-off timestamp for the last update.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ListDisputesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, update_time_after: str | None = None, update_time_before: str | None = None, page_size: int | None = None, next_page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta[list[Dispute], ListDisputesListResultMeta]`
    :   Lists disputes for the PayPal account. Supports filtering by update time range.
        
        
        Args:
            update_time_after: Filter disputes updated after this time in ISO 8601 format.
            update_time_before: Filter disputes updated before this time in ISO 8601 format.
            page_size: Number of items per page (max 50).
            next_page_token: Token for retrieving the next page of results.
            **kwargs: Additional parameters
        
        Returns:
            ListDisputesListResult

<a id="ListPaymentsQuery"></a>

`ListPaymentsQuery(connector: PaypalTransactionConnector)`
:   Query class for ListPayments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ListPaymentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[ListPaymentsSearchData]`
    :   Search list_payments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ListPaymentsSearchFilter):
        - cart: Details of the cart associated with the payment.
        - create_time: The date and time when the payment was created.
        - id: Unique identifier for the payment.
        - intent: The intention or purpose behind the payment.
        - links: Collection of links related to the payment
        - payer: Details of the payer who made the payment
        - state: The state of the payment.
        - transactions: List of transactions associated with the payment
        - update_time: The date and time when the payment was last updated.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ListPaymentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, start_time: str | None = None, end_time: str | None = None, count: int | None = None, start_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta[list[Payment], ListPaymentsListResultMeta]`
    :   Lists payments for the PayPal account. Supports filtering by start and end times.
        
        
        Args:
            start_time: Start time in ISO 8601 format.
            end_time: End time in ISO 8601 format.
            count: Number of items per page (max 20).
            start_id: Starting resource ID for pagination.
            **kwargs: Additional parameters
        
        Returns:
            ListPaymentsListResult

<a id="ListProductsQuery"></a>

`ListProductsQuery(connector: PaypalTransactionConnector)`
:   Query class for ListProducts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ListProductsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[ListProductsSearchData]`
    :   Search list_products records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ListProductsSearchFilter):
        - create_time: The time when the product was created
        - description: Detailed information or features of the product
        - id: Unique identifier for the product
        - links: List of links related to the fetched products.
        - name: The name or title of the product
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ListProductsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page_size: int | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta[list[Product], ListProductsListResultMeta]`
    :   Lists all catalog products for the PayPal account.
        
        Args:
            page_size: Number of items per page (max 20).
            page: Page number starting from 1.
            **kwargs: Additional parameters
        
        Returns:
            ListProductsListResult

<a id="PaypalTransactionConnector"></a>

`PaypalTransactionConnector(auth_config: PaypalTransactionAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Paypal-Transaction API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new paypal-transaction connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., PaypalTransactionAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = PaypalTransactionConnector(auth_config=PaypalTransactionAuthConfig(client_id="...", client_secret="...", access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = PaypalTransactionConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = PaypalTransactionConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'PaypalTransactionAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'PaypalTransactionReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A PaypalTransactionConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await PaypalTransactionConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=PaypalTransactionAuthConfig(client_id="...", client_secret="...", access_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await PaypalTransactionConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=PaypalTransactionAuthConfig(client_id="...", client_secret="...", access_token="..."),
                replication_config=PaypalTransactionReplicationConfig(start_date="..."),
            )
        
            # With server-side OAuth:
            connector = await PaypalTransactionConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=PaypalTransactionReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'PaypalTransactionReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await PaypalTransactionConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Paypal-Transaction Source",
                replication_config=PaypalTransactionReplicationConfig(start_date="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @PaypalTransactionConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @PaypalTransactionConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await PaypalTransactionConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            PaypalTransactionCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="SearchInvoicesQuery"></a>

`SearchInvoicesQuery(connector: PaypalTransactionConnector)`
:   Query class for SearchInvoices entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SearchInvoicesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[SearchInvoicesSearchData]`
    :   Search search_invoices records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SearchInvoicesSearchFilter):
        - additional_recipients: List of additional recipients associated with the invoice
        - amount: Detailed breakdown of the invoice amount
        - configuration: Configuration settings related to the invoice
        - detail: Detailed information about the invoice
        - due_amount: Due amount remaining to be paid for the invoice
        - gratuity: Gratuity amount included in the invoice
        - id: Unique identifier of the invoice
        - invoicer: Information about the invoicer associated with the invoice
        - last_update_time: Date and time of the last update made to the invoice
        - links: Links associated with the invoice
        - payments: Payment transactions associated with the invoice
        - primary_recipients: Primary recipients associated with the invoice
        - refunds: Refund transactions associated with the invoice
        - status: Current status of the invoice
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SearchInvoicesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, creation_date_range: SearchInvoicesListParamsCreationDateRange | None = None, page_size: int | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta[list[Invoice], SearchInvoicesListResultMeta]`
    :   Searches for invoices matching the specified criteria. Uses POST with a JSON body for filtering.
        
        
        Args:
            creation_date_range: Filter by invoice creation date range.
            page_size: Number of items per page (max 100).
            page: Page number starting from 1.
            **kwargs: Additional parameters
        
        Returns:
            SearchInvoicesListResult

<a id="ShowProductDetailsQuery"></a>

`ShowProductDetailsQuery(connector: PaypalTransactionConnector)`
:   Query class for ShowProductDetails entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ShowProductDetailsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[ShowProductDetailsSearchData]`
    :   Search show_product_details records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ShowProductDetailsSearchFilter):
        - category: The category to which the product belongs
        - create_time: The date and time when the product was created
        - description: The detailed description of the product
        - home_url: The URL for the home page of the product
        - id: The unique identifier for the product
        - image_url: The URL to the image representing the product
        - links: Contains links related to the product details.
        - name: The name of the product
        - type_: The type or category of the product
        - update_time: The date and time when the product was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ShowProductDetailsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.ProductDetails`
    :   Shows details for a catalog product by ID.
        
        Args:
            id: Product ID.
            **kwargs: Additional parameters
        
        Returns:
            ProductDetails

<a id="TransactionsQuery"></a>

`TransactionsQuery(connector: PaypalTransactionConnector)`
:   Query class for Transactions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TransactionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[TransactionsSearchData]`
    :   Search transactions records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TransactionsSearchFilter):
        - auction_info: Information related to an auction
        - cart_info: Details of items in the cart
        - incentive_info: Details of any incentives applied
        - payer_info: Information about the payer
        - shipping_info: Shipping information
        - store_info: Information about the store
        - transaction_id: Unique ID of the transaction
        - transaction_info: Detailed information about the transaction
        - transaction_initiation_date: Date and time when the transaction was initiated
        - transaction_updated_date: Date and time when the transaction was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TransactionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, start_date: str, end_date: str, transaction_id: str | None = None, transaction_type: str | None = None, transaction_status: str | None = None, transaction_currency: str | None = None, fields: str | None = None, page_size: int | None = None, page: int | None = None, balance_affecting_records_only: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta[list[Transaction], TransactionsListResultMeta]`
    :   Lists transactions for a PayPal account. Specify one or more query parameters to filter the transactions. Requires start_date and end_date parameters. The maximum supported date range is 31 days. It takes a maximum of three hours for executed transactions to appear.
        
        
        Args:
            start_date: Start date and time in ISO 8601 format. Seconds are required.
        
            end_date: End date and time in ISO 8601 format. Seconds are required. Maximum supported range is 31 days.
        
            transaction_id: Filters by PayPal transaction ID (17-19 characters).
            transaction_type: Filters by PayPal transaction event code.
            transaction_status: Filters by PayPal transaction status code. D=Denied, P=Pending, S=Successful, V=Reversed.
        
            transaction_currency: Three-character ISO-4217 currency code.
            fields: Fields to include in the response. Comma-separated list. Use 'all' to include all fields. Default is transaction_info.
        
            page_size: Number of items per page (1-500).
            page: Page number to return.
            balance_affecting_records_only: Y to include only balance-impacting transactions (default). N to include all transactions.
        
            **kwargs: Additional parameters
        
        Returns:
            TransactionsListResult