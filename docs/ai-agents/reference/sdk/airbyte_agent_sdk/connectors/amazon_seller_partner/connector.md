---
id: airbyte_agent_sdk-connectors-amazon_seller_partner-connector
title: airbyte_agent_sdk.connectors.amazon_seller_partner.connector
---

Module airbyte_agent_sdk.connectors.amazon_seller_partner.connector
===================================================================
Amazon-Seller-Partner connector.

Classes
-------

<a id="AmazonSellerPartnerConnector"></a>

`AmazonSellerPartnerConnector(auth_config: AmazonSellerPartnerAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, region: str | None = None)`
:   Type-safe Amazon-Seller-Partner API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
            Initialize a new amazon-seller-partner connector instance.
    
            Supports both local and hosted execution modes:
            - Local mode: Provide connector-specific auth config (e.g., AmazonSellerPartnerAuthConfig)
            - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
            Args:
                auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
                on_token_refresh: Optional callback for OAuth2 token refresh persistence.
                    Called with new_tokens dict when tokens are refreshed. Can be sync or async.
                    Example: lambda tokens: save_to_database(tokens)            region: The seller's marketplace region. This determines both the API endpoint and the marketplace ID used for queries. Select the country code where you sell:
    North America (NA endpoint): US (Amazon.com), CA (Amazon.ca), MX (Amazon.com.mx), BR (Amazon.com.br)
    Europe (EU endpoint): DE (Amazon.de), FR (Amazon.fr), IT (Amazon.it), ES (Amazon.es), UK/GB (Amazon.co.uk), NL (Amazon.nl), SE (Amazon.se), PL (Amazon.pl), BE (Amazon.com.be), TR (Amazon.com.tr), EG (Amazon.eg), SA (Amazon.sa), AE (Amazon.ae), IN (Amazon.in), ZA (Amazon.co.za)
    Far East (FE endpoint): JP (Amazon.co.jp), AU (Amazon.com.au), SG (Amazon.sg)
    The region is automatically mapped to the correct API endpoint (na/eu/fe) and marketplace ID. You only need to specify your country code.
            Examples:
                # Local mode (direct API calls)
                connector = AmazonSellerPartnerConnector(auth_config=AmazonSellerPartnerAuthConfig(lwa_app_id="...", lwa_client_secret="...", refresh_token="...", access_token="..."))
                # Hosted mode with explicit connector_id (no lookup needed)
                connector = AmazonSellerPartnerConnector(
                    auth_config=AirbyteAuthConfig(
                        airbyte_client_id="client_abc123",
                        airbyte_client_secret="secret_xyz789",
                        connector_id="existing-source-uuid"
                    )
                )
    
                # Hosted mode with lookup by workspace_name
                connector = AmazonSellerPartnerConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'AmazonSellerPartnerAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'AmazonSellerPartnerReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A AmazonSellerPartnerConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await AmazonSellerPartnerConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=AmazonSellerPartnerAuthConfig(lwa_app_id="...", lwa_client_secret="...", refresh_token="...", access_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await AmazonSellerPartnerConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=AmazonSellerPartnerAuthConfig(lwa_app_id="...", lwa_client_secret="...", refresh_token="...", access_token="..."),
                replication_config=AmazonSellerPartnerReplicationConfig(replication_start_date="..."),
            )
        
            # With server-side OAuth:
            connector = await AmazonSellerPartnerConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=AmazonSellerPartnerReplicationConfig(replication_start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'AmazonSellerPartnerReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await AmazonSellerPartnerConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Amazon-Seller-Partner Source",
                replication_config=AmazonSellerPartnerReplicationConfig(replication_start_date="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @AmazonSellerPartnerConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @AmazonSellerPartnerConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await AmazonSellerPartnerConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            AmazonSellerPartnerCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="CatalogItemsQuery"></a>

`CatalogItemsQuery(connector: AmazonSellerPartnerConnector)`
:   Query class for CatalogItems entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, asin: str, marketplace_ids: str, included_data: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_seller_partner.models.CatalogItem`
    :   Retrieves details for an item in the Amazon catalog by ASIN.
        
        Args:
            asin: The Amazon Standard Identification Number (ASIN) of the item. ASINs are 10-character alphanumeric unique identifiers (e.g. B08N5WRWNW). You can find ASINs from order items (the ASIN field) or from catalog search results.
            marketplace_ids: A marketplace identifier. This is auto-injected from the configured seller region — do not ask the user for a marketplace ID. The correct ID is resolved automatically from the region setting.
            included_data: Comma-separated list of data sets to include in the response. Default is "summaries" (brand, title, classification). Other options: identifiers, images, productTypes, salesRanks, dimensions, relationships, vendorDetails.
            **kwargs: Additional parameters
        
        Returns:
            CatalogItem

    `list(self, marketplace_ids: str, keywords: str | None = None, identifiers: str | None = None, identifiers_type: str | None = None, included_data: str | None = None, page_size: int | None = None, page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta[list[CatalogItem], CatalogItemsListResultMeta]`
    :   Search for items in the Amazon catalog by keywords or identifiers.
        
        Args:
            marketplace_ids: A marketplace identifier. This is auto-injected from the configured seller region — do not ask the user for a marketplace ID. Each Amazon marketplace has a unique ID (e.g. ATVPDKIKX0DER for US, A1PA6795UKMFR9 for DE). The correct ID is resolved automatically from the region setting.
            keywords: Keywords to search for in the Amazon catalog. Use this for text-based product search. Cannot be used together with identifiers — provide one or the other.
            identifiers: Product identifiers to search for (ASIN, EAN, UPC, etc.). When using this parameter, identifiersType must also be set. Cannot be used together with keywords — provide one or the other.
            identifiers_type: Type of product identifiers being searched. Required when identifiers is set. Valid values: ASIN, EAN, GTIN, ISBN, JAN, MINSAN, SKU, UPC.
            included_data: Comma-separated list of data sets to include in the response. Default is "summaries" (brand, title, classification). Other options: identifiers, images, productTypes, salesRanks, dimensions, relationships, vendorDetails.
            page_size: Number of items to return per page (1-20, default 10).
            page_token: Token for pagination returned by a previous request.
            **kwargs: Additional parameters
        
        Returns:
            CatalogItemsListResult

<a id="ListFinancialEventGroupsQuery"></a>

`ListFinancialEventGroupsQuery(connector: AmazonSellerPartnerConnector)`
:   Query class for ListFinancialEventGroups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ListFinancialEventGroupsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult[ListFinancialEventGroupsSearchData]`
    :   Search list_financial_event_groups records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ListFinancialEventGroupsSearchFilter):
        - account_tail: The last digits of the account number
        - beginning_balance: Beginning balance
        - converted_total: Converted total
        - financial_event_group_end: End datetime of the financial event group
        - financial_event_group_id: Unique identifier for the financial event group
        - financial_event_group_start: Start datetime of the financial event group
        - fund_transfer_date: Date the fund transfer occurred
        - fund_transfer_status: Status of the fund transfer
        - original_total: Original total amount
        - processing_status: Processing status of the financial event group
        - trace_id: Unique identifier for tracing
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ListFinancialEventGroupsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, financial_event_group_started_after: str | None = None, financial_event_group_started_before: str | None = None, max_results_per_page: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta[list[FinancialEventGroup], ListFinancialEventGroupsListResultMeta]`
    :   Returns financial event groups for a given date range.
        
        Args:
            financial_event_group_started_after: Return groups that started after this date. Must be in ISO 8601 date-time format (e.g. 2024-01-01T00:00:00Z). Use this to scope results to a specific time period. For example, to see settlements from the last 90 days, set this to 90 days ago.
            financial_event_group_started_before: Return groups that started before this date. Must be in ISO 8601 date-time format (e.g. 2024-03-31T23:59:59Z). Use together with FinancialEventGroupStartedAfter to define a date range. If omitted, defaults to now.
            max_results_per_page: Maximum number of results to return per page (1-100, default 100).
            next_token: A string token returned in a previous response for pagination.
            **kwargs: Additional parameters
        
        Returns:
            ListFinancialEventGroupsListResult

<a id="ListFinancialEventsQuery"></a>

`ListFinancialEventsQuery(connector: AmazonSellerPartnerConnector)`
:   Query class for ListFinancialEvents entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ListFinancialEventsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult[ListFinancialEventsSearchData]`
    :   Search list_financial_events records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ListFinancialEventsSearchFilter):
        - adhoc_disbursement_event_list: List of adhoc disbursement events
        - adjustment_event_list: List of adjustment events
        - affordability_expense_event_list: List of affordability expense events
        - affordability_expense_reversal_event_list: List of affordability expense reversal events
        - capacity_reservation_billing_event_list: List of capacity reservation billing events
        - charge_refund_event_list: List of charge refund events
        - chargeback_event_list: List of chargeback events
        - coupon_payment_event_list: List of coupon payment events
        - debt_recovery_event_list: List of debt recovery events
        - fba_liquidation_event_list: List of FBA liquidation events
        - failed_adhoc_disbursement_event_list: List of failed adhoc disbursement events
        - guarantee_claim_event_list: List of guarantee claim events
        - imaging_services_fee_event_list: List of imaging services fee events
        - loan_servicing_event_list: List of loan servicing events
        - network_commingling_transaction_event_list: List of network commingling events
        - pay_with_amazon_event_list: List of Pay with Amazon events
        - performance_bond_refund_event_list: List of performance bond refund events
        - posted_before: Date filter for events posted before
        - product_ads_payment_event_list: List of product ads payment events
        - refund_event_list: List of refund events
        - removal_shipment_adjustment_event_list: List of removal shipment adjustment events
        - removal_shipment_event_list: List of removal shipment events
        - rental_transaction_event_list: List of rental transaction events
        - retrocharge_event_list: List of retrocharge events
        - safet_reimbursement_event_list: List of SAFET reimbursement events
        - seller_deal_payment_event_list: List of seller deal payment events
        - seller_review_enrollment_payment_event_list: List of seller review enrollment events
        - service_fee_event_list: List of service fee events
        - service_provider_credit_event_list: List of service provider credit events
        - shipment_event_list: List of shipment events
        - shipment_settle_event_list: List of shipment settlement events
        - tds_reimbursement_event_list: List of TDS reimbursement events
        - tax_withholding_event_list: List of tax withholding events
        - trial_shipment_event_list: List of trial shipment events
        - value_added_service_charge_event_list: List of value-added service charge events
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ListFinancialEventsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, posted_after: str | None = None, posted_before: str | None = None, max_results_per_page: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta[FinancialEvents, ListFinancialEventsListResultMeta]`
    :   Returns financial events for a given date range.
        
        Args:
            posted_after: Return events posted after this date. Must be in ISO 8601 date-time format (e.g. 2024-01-01T00:00:00Z). Recommended for scoping results to a manageable date range. For recent activity, set this to 30 days ago.
            posted_before: Return events posted before this date. Must be in ISO 8601 date-time format (e.g. 2024-01-31T23:59:59Z). Use together with PostedAfter to define a date range. If omitted, defaults to now.
            max_results_per_page: Maximum number of results to return per page (1-100, default 100).
            next_token: A string token returned in a previous response for pagination.
            **kwargs: Additional parameters
        
        Returns:
            ListFinancialEventsListResult

<a id="OrderItemsQuery"></a>

`OrderItemsQuery(connector: AmazonSellerPartnerConnector)`
:   Query class for OrderItems entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OrderItemsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult[OrderItemsSearchData]`
    :   Search order_items records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OrderItemsSearchFilter):
        - asin: Amazon Standard Identification Number of the product
        - amazon_order_id: ID of the Amazon order
        - buyer_info: Information about the buyer
        - buyer_requested_cancel: Information about buyer's request for cancellation
        - cod_fee: Cash on delivery fee
        - cod_fee_discount: Discount on cash on delivery fee
        - condition_id: Condition ID of the product
        - condition_note: Additional notes on the condition of the product
        - condition_subtype_id: Subtype ID of the product condition
        - deemed_reseller_category: Category indicating if the seller is considered a reseller
        - ioss_number: Import One Stop Shop number
        - is_gift: Flag indicating if the order is a gift
        - is_transparency: Flag indicating if transparency is applied
        - item_price: Price of the item
        - item_tax: Tax applied on the item
        - last_update_date: Date and time of the last update
        - order_item_id: ID of the order item
        - points_granted: Points granted for the purchase
        - price_designation: Designation of the price
        - product_info: Information about the product
        - promotion_discount: Discount applied due to promotion
        - promotion_discount_tax: Tax applied on the promotion discount
        - promotion_ids: IDs of promotions applied
        - quantity_ordered: Quantity of the item ordered
        - quantity_shipped: Quantity of the item shipped
        - scheduled_delivery_end_date: End date for scheduled delivery
        - scheduled_delivery_start_date: Start date for scheduled delivery
        - seller_sku: SKU of the seller
        - serial_number_required: Flag indicating if serial number is required
        - serial_numbers: List of serial numbers
        - shipping_discount: Discount applied on shipping
        - shipping_discount_tax: Tax applied on the shipping discount
        - shipping_price: Price of shipping
        - shipping_tax: Tax applied on shipping
        - store_chain_store_id: ID of the store chain
        - tax_collection: Information about tax collection
        - title: Title of the product
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OrderItemsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, order_id: str, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta[list[OrderItem], OrderItemsListResultMeta]`
    :   Returns detailed order item information for the order indicated by the specified order ID.
        
        Args:
            order_id: An Amazon order identifier in 3-7-7 format (e.g. 111-2222222-3333333). This is the AmazonOrderId returned by the list orders endpoint.
            next_token: A string token returned in a previous response for pagination.
            **kwargs: Additional parameters
        
        Returns:
            OrderItemsListResult

<a id="OrdersQuery"></a>

`OrdersQuery(connector: AmazonSellerPartnerConnector)`
:   Query class for Orders entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OrdersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult[OrdersSearchData]`
    :   Search orders records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OrdersSearchFilter):
        - amazon_order_id: Unique identifier for the Amazon order
        - automated_shipping_settings: Settings related to automated shipping processes
        - buyer_info: Information about the buyer
        - default_ship_from_location_address: The default address from which orders are shipped
        - earliest_delivery_date: Earliest estimated delivery date of the order
        - earliest_ship_date: Earliest shipment date for the order
        - fulfillment_channel: Channel through which the order is fulfilled
        - has_regulated_items: Indicates if the order has regulated items
        - is_access_point_order: Indicates if the order is an Amazon Hub Counter order
        - is_business_order: Indicates if the order is a business order
        - is_global_express_enabled: Indicates if global express is enabled for the order
        - is_ispu: Indicates if the order is for In-Store Pickup
        - is_premium_order: Indicates if the order is a premium order
        - is_prime: Indicates if the order is a Prime order
        - is_replacement_order: Indicates if the order is a replacement order
        - is_sold_by_ab: Indicates if the order is sold by Amazon Business
        - last_update_date: Date and time when the order was last updated
        - latest_delivery_date: Latest estimated delivery date of the order
        - latest_ship_date: Latest shipment date for the order
        - marketplace_id: Identifier for the marketplace where the order was placed
        - number_of_items_shipped: Number of items shipped in the order
        - number_of_items_unshipped: Number of items yet to be shipped in the order
        - order_status: Status of the order
        - order_total: Total amount of the order
        - order_type: Type of the order
        - payment_method: Payment method used for the order
        - payment_method_details: Details of the payment method used for the order
        - purchase_date: Date and time when the order was purchased
        - sales_channel: Channel through which the order was sold
        - seller_order_id: Unique identifier given by the seller for the order
        - ship_service_level: Service level for shipping the order
        - shipment_service_level_category: Service level category for shipping the order
        - shipping_address: The address to which the order will be shipped
        - seller_id: Identifier for the seller associated with the order
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OrdersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, order_id: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Returns the order indicated by the specified order ID.
        
        Args:
            order_id: An Amazon order identifier in 3-7-7 format (e.g. 111-2222222-3333333). This is the AmazonOrderId returned by the list orders endpoint.
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, marketplace_ids: str, created_after: str | None = None, created_before: str | None = None, last_updated_after: str | None = None, last_updated_before: str | None = None, order_statuses: str | None = None, max_results_per_page: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta[list[Order], OrdersListResultMeta]`
    :   Returns a list of orders based on the specified parameters.
        
        Args:
            marketplace_ids: A list of MarketplaceId values. Used to select orders placed in the specified marketplaces. This is auto-injected from the configured seller region — do not ask the user for a marketplace ID. Each Amazon marketplace has a unique ID (e.g. ATVPDKIKX0DER for US, A1PA6795UKMFR9 for DE). The correct ID is resolved automatically from the region setting (US, CA, MX, BR, DE, FR, IT, ES, UK, IN, JP, AU, SG, etc.).
            created_after: A date used for selecting orders created after the specified date. Must be in ISO 8601 date-time format (e.g. 2024-01-15T00:00:00Z). Required if LastUpdatedAfter is not specified — the API requires at least one of CreatedAfter or LastUpdatedAfter. Use this to scope orders by creation date. For example, to get orders from the last 30 days, set this to a date 30 days ago.
            created_before: A date used for selecting orders created before the specified date. Must be in ISO 8601 date-time format (e.g. 2024-02-15T23:59:59Z). Use together with CreatedAfter to define a creation date range. If omitted, defaults to now.
            last_updated_after: A date used for selecting orders that were last updated after the specified date. Must be in ISO 8601 date-time format (e.g. 2024-01-15T00:00:00Z). Required if CreatedAfter is not specified — the API requires at least one of these. Use this when you want orders that changed recently (e.g. status updates, shipment changes).
            last_updated_before: A date used for selecting orders that were last updated before the specified date. Must be in ISO 8601 date-time format (e.g. 2024-02-15T23:59:59Z). Use together with LastUpdatedAfter to define an update date range. If omitted, defaults to now.
            order_statuses: Filter by order status values. Comma-separated list of statuses: Pending, Unshipped, PartiallyShipped, Shipped, Canceled, Unfulfillable, InvoiceUnconfirmed, PendingAvailability. Example: "Shipped,Unshipped".
            max_results_per_page: Maximum number of results to return per page (1-100, default 100).
            next_token: A string token returned in a previous response for pagination.
            **kwargs: Additional parameters
        
        Returns:
            OrdersListResult

<a id="ReportsQuery"></a>

`ReportsQuery(connector: AmazonSellerPartnerConnector)`
:   Query class for Reports entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, report_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_seller_partner.models.Report`
    :   Returns report details including status and report document ID for a specified report.
        
        Args:
            report_id: The identifier for the report. Obtain this from the list reports endpoint. The reportId is a unique string identifier assigned when a report is created.
            **kwargs: Additional parameters
        
        Returns:
            Report

    `list(self, report_types: str | None = None, processing_statuses: str | None = None, marketplace_ids: str | None = None, page_size: int | None = None, created_since: str | None = None, created_until: str | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta[list[Report], ReportsListResultMeta]`
    :   Returns report details for the reports that match the specified filters.
        
        Args:
            report_types: A comma-separated list of report types to filter by. Common report types include GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL (orders), GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA (FBA removals), GET_MERCHANT_LISTINGS_ALL_DATA (listings). See SP-API docs for full list.
            processing_statuses: A comma-separated list of processing statuses to filter by. Valid values: IN_QUEUE, IN_PROGRESS, DONE, CANCELLED, FATAL. Use "DONE" to find completed reports ready for download.
            marketplace_ids: A list of marketplace identifiers used to filter reports. This is auto-injected from the configured seller region — do not ask the user for a marketplace ID. The correct ID is resolved automatically from the region setting.
            page_size: Maximum number of reports to return per page (1-100, default 10).
            created_since: Earliest report creation date and time. Must be in ISO 8601 date-time format (e.g. 2024-01-01T00:00:00Z). Use together with createdUntil to define a date range for when reports were created.
            created_until: Latest report creation date and time. Must be in ISO 8601 date-time format (e.g. 2024-01-31T23:59:59Z). Use together with createdSince to define a date range. If omitted, defaults to now.
            next_token: A string token returned in a previous response for pagination.
            **kwargs: Additional parameters
        
        Returns:
            ReportsListResult