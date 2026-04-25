---
id: airbyte_agent_sdk-connectors-amazon_seller_partner-index
title: airbyte_agent_sdk.connectors.amazon_seller_partner.index
---

Module airbyte_agent_sdk.connectors.amazon_seller_partner
=========================================================
Amazon-Seller-Partner connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.amazon_seller_partner.connector
* airbyte_agent_sdk.connectors.amazon_seller_partner.connector_model
* airbyte_agent_sdk.connectors.amazon_seller_partner.models
* airbyte_agent_sdk.connectors.amazon_seller_partner.types

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

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult[ListFinancialEventGroupsSearchData]
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult[ListFinancialEventsSearchData]
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult[OrderItemsSearchData]
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult[OrdersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsSearchResult"></a>

`ListFinancialEventGroupsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ListFinancialEventsSearchResult"></a>

`ListFinancialEventsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="OrderItemsSearchResult"></a>

`OrderItemsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="OrdersSearchResult"></a>

`OrdersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AmazonSellerPartnerAuthConfig"></a>

`AmazonSellerPartnerAuthConfig(**data: Any)`
:   Login with Amazon OAuth 2.0
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str | None`
    :   Access token (optional if refresh_token is provided).

    `lwa_app_id: str`
    :   Your Login with Amazon Client ID.

    `lwa_client_secret: str`
    :   Your Login with Amazon Client Secret.

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   The Refresh Token obtained via the OAuth authorization flow.

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

<a id="AmazonSellerPartnerReplicationConfig"></a>

`AmazonSellerPartnerReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Amazon Seller Partner.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `replication_start_date: str`
    :   UTC date and time in ISO 8601 format (e.g. 2024-01-01T00:00:00Z). Any data before this date will not be replicated. This sets the earliest date for order creation and financial event queries. For most sellers, a start date of 1-2 years ago is a good default. Must include the time component and Z timezone suffix.

<a id="ListFinancialEventGroupsSearchData"></a>

`ListFinancialEventGroupsSearchData(**data: Any)`
:   Search result data for list_financial_event_groups entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_tail: str | None`
    :   The last digits of the account number

    `beginning_balance: dict[str, typing.Any] | None`
    :   Beginning balance

    `converted_total: dict[str, typing.Any] | None`
    :   Converted total

    `financial_event_group_end: str | None`
    :   End datetime of the financial event group

    `financial_event_group_id: str | None`
    :   Unique identifier for the financial event group

    `financial_event_group_start: str | None`
    :   Start datetime of the financial event group

    `fund_transfer_date: str | None`
    :   Date the fund transfer occurred

    `fund_transfer_status: str | None`
    :   Status of the fund transfer

    `model_config`
    :   The type of the None singleton.

    `original_total: dict[str, typing.Any] | None`
    :   Original total amount

    `processing_status: str | None`
    :   Processing status of the financial event group

    `trace_id: str | None`
    :   Unique identifier for tracing

<a id="ListFinancialEventsSearchData"></a>

`ListFinancialEventsSearchData(**data: Any)`
:   Search result data for list_financial_events entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `adhoc_disbursement_event_list: list[typing.Any] | None`
    :   List of adhoc disbursement events

    `adjustment_event_list: list[typing.Any] | None`
    :   List of adjustment events

    `affordability_expense_event_list: list[typing.Any] | None`
    :   List of affordability expense events

    `affordability_expense_reversal_event_list: list[typing.Any] | None`
    :   List of affordability expense reversal events

    `capacity_reservation_billing_event_list: list[typing.Any] | None`
    :   List of capacity reservation billing events

    `charge_refund_event_list: list[typing.Any] | None`
    :   List of charge refund events

    `chargeback_event_list: list[typing.Any] | None`
    :   List of chargeback events

    `coupon_payment_event_list: list[typing.Any] | None`
    :   List of coupon payment events

    `debt_recovery_event_list: list[typing.Any] | None`
    :   List of debt recovery events

    `failed_adhoc_disbursement_event_list: list[typing.Any] | None`
    :   List of failed adhoc disbursement events

    `fba_liquidation_event_list: list[typing.Any] | None`
    :   List of FBA liquidation events

    `guarantee_claim_event_list: list[typing.Any] | None`
    :   List of guarantee claim events

    `imaging_services_fee_event_list: list[typing.Any] | None`
    :   List of imaging services fee events

    `loan_servicing_event_list: list[typing.Any] | None`
    :   List of loan servicing events

    `model_config`
    :   The type of the None singleton.

    `network_commingling_transaction_event_list: list[typing.Any] | None`
    :   List of network commingling events

    `pay_with_amazon_event_list: list[typing.Any] | None`
    :   List of Pay with Amazon events

    `performance_bond_refund_event_list: list[typing.Any] | None`
    :   List of performance bond refund events

    `posted_before: str | None`
    :   Date filter for events posted before

    `product_ads_payment_event_list: list[typing.Any] | None`
    :   List of product ads payment events

    `refund_event_list: list[typing.Any] | None`
    :   List of refund events

    `removal_shipment_adjustment_event_list: list[typing.Any] | None`
    :   List of removal shipment adjustment events

    `removal_shipment_event_list: list[typing.Any] | None`
    :   List of removal shipment events

    `rental_transaction_event_list: list[typing.Any] | None`
    :   List of rental transaction events

    `retrocharge_event_list: list[typing.Any] | None`
    :   List of retrocharge events

    `safet_reimbursement_event_list: list[typing.Any] | None`
    :   List of SAFET reimbursement events

    `seller_deal_payment_event_list: list[typing.Any] | None`
    :   List of seller deal payment events

    `seller_review_enrollment_payment_event_list: list[typing.Any] | None`
    :   List of seller review enrollment events

    `service_fee_event_list: list[typing.Any] | None`
    :   List of service fee events

    `service_provider_credit_event_list: list[typing.Any] | None`
    :   List of service provider credit events

    `shipment_event_list: list[typing.Any] | None`
    :   List of shipment events

    `shipment_settle_event_list: list[typing.Any] | None`
    :   List of shipment settlement events

    `tax_withholding_event_list: list[typing.Any] | None`
    :   List of tax withholding events

    `tds_reimbursement_event_list: list[typing.Any] | None`
    :   List of TDS reimbursement events

    `trial_shipment_event_list: list[typing.Any] | None`
    :   List of trial shipment events

    `value_added_service_charge_event_list: list[typing.Any] | None`
    :   List of value-added service charge events

<a id="OrderItemsSearchData"></a>

`OrderItemsSearchData(**data: Any)`
:   Search result data for order_items entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amazon_order_id: str | None`
    :   ID of the Amazon order

    `asin: str | None`
    :   Amazon Standard Identification Number of the product

    `buyer_info: dict[str, typing.Any] | None`
    :   Information about the buyer

    `buyer_requested_cancel: dict[str, typing.Any] | None`
    :   Information about buyer's request for cancellation

    `cod_fee: dict[str, typing.Any] | None`
    :   Cash on delivery fee

    `cod_fee_discount: dict[str, typing.Any] | None`
    :   Discount on cash on delivery fee

    `condition_id: str | None`
    :   Condition ID of the product

    `condition_note: str | None`
    :   Additional notes on the condition of the product

    `condition_subtype_id: str | None`
    :   Subtype ID of the product condition

    `deemed_reseller_category: str | None`
    :   Category indicating if the seller is considered a reseller

    `ioss_number: str | None`
    :   Import One Stop Shop number

    `is_gift: str | None`
    :   Flag indicating if the order is a gift

    `is_transparency: bool | None`
    :   Flag indicating if transparency is applied

    `item_price: dict[str, typing.Any] | None`
    :   Price of the item

    `item_tax: dict[str, typing.Any] | None`
    :   Tax applied on the item

    `last_update_date: str | None`
    :   Date and time of the last update

    `model_config`
    :   The type of the None singleton.

    `order_item_id: str | None`
    :   ID of the order item

    `points_granted: dict[str, typing.Any] | None`
    :   Points granted for the purchase

    `price_designation: str | None`
    :   Designation of the price

    `product_info: dict[str, typing.Any] | None`
    :   Information about the product

    `promotion_discount: dict[str, typing.Any] | None`
    :   Discount applied due to promotion

    `promotion_discount_tax: dict[str, typing.Any] | None`
    :   Tax applied on the promotion discount

    `promotion_ids: list[typing.Any] | None`
    :   IDs of promotions applied

    `quantity_ordered: int | None`
    :   Quantity of the item ordered

    `quantity_shipped: int | None`
    :   Quantity of the item shipped

    `scheduled_delivery_end_date: str | None`
    :   End date for scheduled delivery

    `scheduled_delivery_start_date: str | None`
    :   Start date for scheduled delivery

    `seller_sku: str | None`
    :   SKU of the seller

    `serial_number_required: bool | None`
    :   Flag indicating if serial number is required

    `serial_numbers: list[typing.Any] | None`
    :   List of serial numbers

    `shipping_discount: dict[str, typing.Any] | None`
    :   Discount applied on shipping

    `shipping_discount_tax: dict[str, typing.Any] | None`
    :   Tax applied on the shipping discount

    `shipping_price: dict[str, typing.Any] | None`
    :   Price of shipping

    `shipping_tax: dict[str, typing.Any] | None`
    :   Tax applied on shipping

    `store_chain_store_id: str | None`
    :   ID of the store chain

    `tax_collection: dict[str, typing.Any] | None`
    :   Information about tax collection

    `title: str | None`
    :   Title of the product

<a id="OrdersSearchData"></a>

`OrdersSearchData(**data: Any)`
:   Search result data for orders entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amazon_order_id: str | None`
    :   Unique identifier for the Amazon order

    `automated_shipping_settings: dict[str, typing.Any] | None`
    :   Settings related to automated shipping processes

    `buyer_info: dict[str, typing.Any] | None`
    :   Information about the buyer

    `default_ship_from_location_address: dict[str, typing.Any] | None`
    :   The default address from which orders are shipped

    `earliest_delivery_date: str | None`
    :   Earliest estimated delivery date of the order

    `earliest_ship_date: str | None`
    :   Earliest shipment date for the order

    `fulfillment_channel: str | None`
    :   Channel through which the order is fulfilled

    `has_regulated_items: bool | None`
    :   Indicates if the order has regulated items

    `is_access_point_order: bool | None`
    :   Indicates if the order is an Amazon Hub Counter order

    `is_business_order: bool | None`
    :   Indicates if the order is a business order

    `is_global_express_enabled: bool | None`
    :   Indicates if global express is enabled for the order

    `is_ispu: bool | None`
    :   Indicates if the order is for In-Store Pickup

    `is_premium_order: bool | None`
    :   Indicates if the order is a premium order

    `is_prime: bool | None`
    :   Indicates if the order is a Prime order

    `is_replacement_order: str | None`
    :   Indicates if the order is a replacement order

    `is_sold_by_ab: bool | None`
    :   Indicates if the order is sold by Amazon Business

    `last_update_date: str | None`
    :   Date and time when the order was last updated

    `latest_delivery_date: str | None`
    :   Latest estimated delivery date of the order

    `latest_ship_date: str | None`
    :   Latest shipment date for the order

    `marketplace_id: str | None`
    :   Identifier for the marketplace where the order was placed

    `model_config`
    :   The type of the None singleton.

    `number_of_items_shipped: int | None`
    :   Number of items shipped in the order

    `number_of_items_unshipped: int | None`
    :   Number of items yet to be shipped in the order

    `order_status: str | None`
    :   Status of the order

    `order_total: dict[str, typing.Any] | None`
    :   Total amount of the order

    `order_type: str | None`
    :   Type of the order

    `payment_method: str | None`
    :   Payment method used for the order

    `payment_method_details: list[typing.Any] | None`
    :   Details of the payment method used for the order

    `purchase_date: str | None`
    :   Date and time when the order was purchased

    `sales_channel: str | None`
    :   Channel through which the order was sold

    `seller_id: str | None`
    :   Identifier for the seller associated with the order

    `seller_order_id: str | None`
    :   Unique identifier given by the seller for the order

    `ship_service_level: str | None`
    :   Service level for shipping the order

    `shipment_service_level_category: str | None`
    :   Service level category for shipping the order

    `shipping_address: dict[str, typing.Any] | None`
    :   The address to which the order will be shipped