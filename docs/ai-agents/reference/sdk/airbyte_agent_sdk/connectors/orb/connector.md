---
id: airbyte_agent_sdk-connectors-orb-connector
title: airbyte_agent_sdk.connectors.orb.connector
---

Module airbyte_agent_sdk.connectors.orb.connector
=================================================
Orb connector.

Classes
-------

<a id="CustomersQuery"></a>

`CustomersQuery(connector: OrbConnector)`
:   Query class for Customers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CustomersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult[CustomersSearchData]`
    :   Search customers records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CustomersSearchFilter):
        - id: The unique identifier of the customer
        - external_customer_id: The ID of the customer in an external system
        - name: The name of the customer
        - email: The email address of the customer
        - created_at: The date and time when the customer was created
        - payment_provider: The payment provider used by the customer
        - payment_provider_id: The ID of the customer in the payment provider's system
        - timezone: The timezone setting of the customer
        - shipping_address: The shipping address of the customer
        - billing_address: The billing address of the customer
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CustomersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, customer_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.Customer`
    :   Get a single customer by ID
        
        Args:
            customer_id: Customer ID
            **kwargs: Additional parameters
        
        Returns:
            Customer

    `list(self, limit: int | None = None, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta[list[Customer], CustomersListResultMeta]`
    :   Returns a paginated list of customers
        
        Args:
            limit: Number of items to return per page
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            CustomersListResult

<a id="InvoicesQuery"></a>

`InvoicesQuery(connector: OrbConnector)`
:   Query class for Invoices entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: InvoicesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult[InvoicesSearchData]`
    :   Search invoices records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (InvoicesSearchFilter):
        - id: The unique identifier of the invoice
        - created_at: The date and time when the invoice was created
        - invoice_date: The date of the invoice
        - due_date: The due date for the invoice
        - invoice_pdf: The URL to download the PDF version of the invoice
        - subtotal: The subtotal amount of the invoice
        - total: The total amount of the invoice
        - amount_due: The amount due on the invoice
        - status: The current status of the invoice
        - memo: Any additional notes or comments on the invoice
        - paid_at: The date and time when the invoice was paid
        - issued_at: The date and time when the invoice was issued
        - hosted_invoice_url: The URL to view the hosted invoice
        - line_items: The line items on the invoice
        - subscription: The subscription associated with the invoice
        
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

    `get(self, invoice_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.Invoice`
    :   Get a single invoice by ID
        
        Args:
            invoice_id: Invoice ID
            **kwargs: Additional parameters
        
        Returns:
            Invoice

    `list(self, limit: int | None = None, cursor: str | None = None, customer_id: str | None = None, external_customer_id: str | None = None, subscription_id: str | None = None, invoice_date_gt: str | None = None, invoice_date_gte: str | None = None, invoice_date_lt: str | None = None, invoice_date_lte: str | None = None, status: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta[list[Invoice], InvoicesListResultMeta]`
    :   Returns a paginated list of invoices
        
        Args:
            limit: Number of items to return per page
            cursor: Cursor for pagination
            customer_id: Filter invoices by customer ID
            external_customer_id: Filter invoices by external customer ID
            subscription_id: Filter invoices by subscription ID
            invoice_date_gt: Filter invoices with invoice date greater than this value (ISO 8601 format)
            invoice_date_gte: Filter invoices with invoice date greater than or equal to this value (ISO 8601 format)
            invoice_date_lt: Filter invoices with invoice date less than this value (ISO 8601 format)
            invoice_date_lte: Filter invoices with invoice date less than or equal to this value (ISO 8601 format)
            status: Filter invoices by status
            **kwargs: Additional parameters
        
        Returns:
            InvoicesListResult

<a id="OrbConnector"></a>

`OrbConnector(auth_config: OrbAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Orb API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new orb connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., OrbAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = OrbConnector(auth_config=OrbAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = OrbConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = OrbConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'OrbAuthConfig'", name: str | None = None, replication_config: "'OrbReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A OrbConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await OrbConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=OrbAuthConfig(api_key="..."),
            )
        
            # With replication config (required for this connector):
            connector = await OrbConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=OrbAuthConfig(api_key="..."),
                replication_config=OrbReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @OrbConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @OrbConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await OrbConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.orb.models.OrbCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            OrbCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="PlansQuery"></a>

`PlansQuery(connector: OrbConnector)`
:   Query class for Plans entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: PlansSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult[PlansSearchData]`
    :   Search plans records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (PlansSearchFilter):
        - id: The unique identifier of the plan
        - created_at: The date and time when the plan was created
        - name: The name of the plan
        - description: A description of the plan
        - prices: The pricing options for the plan
        - product: The product associated with the plan
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            PlansSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, plan_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.Plan`
    :   Get a single plan by ID
        
        Args:
            plan_id: Plan ID
            **kwargs: Additional parameters
        
        Returns:
            Plan

    `list(self, limit: int | None = None, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta[list[Plan], PlansListResultMeta]`
    :   Returns a paginated list of plans
        
        Args:
            limit: Number of items to return per page
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            PlansListResult

<a id="SubscriptionsQuery"></a>

`SubscriptionsQuery(connector: OrbConnector)`
:   Query class for Subscriptions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SubscriptionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult[SubscriptionsSearchData]`
    :   Search subscriptions records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SubscriptionsSearchFilter):
        - id: The unique identifier of the subscription
        - created_at: The date and time when the subscription was created
        - start_date: The date and time when the subscription starts
        - end_date: The date and time when the subscription ends
        - status: The current status of the subscription
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SubscriptionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, subscription_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.Subscription`
    :   Get a single subscription by ID
        
        Args:
            subscription_id: Subscription ID
            **kwargs: Additional parameters
        
        Returns:
            Subscription

    `list(self, limit: int | None = None, cursor: str | None = None, customer_id: str | None = None, external_customer_id: str | None = None, status: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta[list[Subscription], SubscriptionsListResultMeta]`
    :   Returns a paginated list of subscriptions
        
        Args:
            limit: Number of items to return per page
            cursor: Cursor for pagination
            customer_id: Filter subscriptions by customer ID
            external_customer_id: Filter subscriptions by external customer ID
            status: Filter subscriptions by status
            **kwargs: Additional parameters
        
        Returns:
            SubscriptionsListResult