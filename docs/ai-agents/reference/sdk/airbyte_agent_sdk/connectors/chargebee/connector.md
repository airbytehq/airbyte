---
id: airbyte_agent_sdk-connectors-chargebee-connector
title: airbyte_agent_sdk.connectors.chargebee.connector
---

Module airbyte_agent_sdk.connectors.chargebee.connector
=======================================================
Chargebee connector.

Classes
-------

<a id="ChargebeeConnector"></a>

`ChargebeeConnector(auth_config: ChargebeeAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, site: str | None = None)`
:   Type-safe Chargebee API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new chargebee connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., ChargebeeAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            site: Your Chargebee site name (subdomain)
    Examples:
        # Local mode (direct API calls)
        connector = ChargebeeConnector(auth_config=ChargebeeAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = ChargebeeConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = ChargebeeConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'ChargebeeAuthConfig'", name: str | None = None, replication_config: "'ChargebeeReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A ChargebeeConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await ChargebeeConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ChargebeeAuthConfig(api_key="..."),
            )
        
            # With replication config (required for this connector):
            connector = await ChargebeeConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ChargebeeAuthConfig(api_key="..."),
                replication_config=ChargebeeReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @ChargebeeConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ChargebeeConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await ChargebeeConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.chargebee.models.ChargebeeCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            ChargebeeCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="CouponQuery"></a>

`CouponQuery(connector: ChargebeeConnector)`
:   Query class for Coupon entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CouponSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[CouponSearchData]`
    :   Search coupon records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CouponSearchFilter):
        - apply_discount_on: Determines where the discount is applied on (e.g. subtotal, total).
        - apply_on: Specify on what type of items the coupon applies (e.g. subscription, addon).
        - archived_at: Timestamp when the coupon was archived.
        - coupon_constraints: Represents the constraints associated with the coupon
        - created_at: Timestamp of the coupon creation.
        - currency_code: The currency code for the coupon (e.g. USD, EUR).
        - custom_fields: 
        - discount_amount: The fixed discount amount applied by the coupon.
        - discount_percentage: Percentage discount applied by the coupon.
        - discount_quantity: Specifies the number of free units provided for the item price, without affecting the total quantity sold. This parameter is applicable only when the discount_type is set to offer_quantity.
        - discount_type: Type of discount (e.g. fixed, percentage).
        - duration_month: Duration of the coupon in months.
        - duration_type: Type of duration (e.g. forever, one-time).
        - id: Unique identifier for the coupon.
        - invoice_name: Name displayed on invoices when the coupon is used.
        - invoice_notes: Additional notes displayed on invoices when the coupon is used.
        - item_constraint_criteria: Criteria for item constraints
        - item_constraints: Constraints related to the items
        - max_redemptions: Maximum number of times the coupon can be redeemed.
        - name: Name of the coupon.
        - object_: Type of object (usually 'coupon').
        - period: Duration or frequency for which the coupon is valid.
        - period_unit: Unit of the period (e.g. days, weeks).
        - redemptions: Number of times the coupon has been redeemed.
        - resource_version: Version of the resource.
        - status: Current status of the coupon (e.g. active, inactive).
        - updated_at: Timestamp when the coupon was last updated.
        - valid_till: Date until which the coupon is valid for use.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CouponSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.Coupon`
    :   Retrieve a coupon
        
        Args:
            id: Coupon ID
            **kwargs: Additional parameters
        
        Returns:
            Coupon

    `list(self, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Coupon], CouponListResultMeta]`
    :   List coupons
        
        Args:
            limit: Parameter limit
            offset: Parameter offset
            **kwargs: Additional parameters
        
        Returns:
            CouponListResult

<a id="CreditNoteQuery"></a>

`CreditNoteQuery(connector: ChargebeeConnector)`
:   Query class for CreditNote entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CreditNoteSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[CreditNoteSearchData]`
    :   Search credit_note records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CreditNoteSearchFilter):
        - allocations: Details of allocations associated with the credit note
        - amount_allocated: The amount of credits allocated.
        - amount_available: The amount of credits available.
        - amount_refunded: The amount of credits refunded.
        - base_currency_code: The base currency code for the credit note.
        - billing_address: Details of the billing address associated with the credit note
        - business_entity_id: The ID of the business entity associated with the credit note.
        - channel: The channel through which the credit note was created.
        - create_reason_code: The reason code for creating the credit note.
        - currency_code: The currency code for the credit note.
        - custom_fields: 
        - customer_id: The ID of the customer associated with the credit note.
        - customer_notes: Notes provided by the customer for the credit note.
        - date: The date when the credit note was created.
        - deleted: Indicates if the credit note has been deleted.
        - discounts: Details of discounts applied to the credit note
        - exchange_rate: The exchange rate used for currency conversion.
        - fractional_correction: Fractional correction for rounding off decimals.
        - generated_at: The date when the credit note was generated.
        - id: The unique identifier for the credit note.
        - is_digital: Indicates if the credit note is in digital format.
        - is_vat_moss_registered: Indicates if VAT MOSS registration applies.
        - line_item_discounts: Details of discounts applied at the line item level in the credit note
        - line_item_taxes: Details of taxes applied at the line item level in the credit note
        - line_item_tiers: Details of tiers applied to line items in the credit note
        - line_items: Details of line items in the credit note
        - linked_refunds: Details of linked refunds to the credit note
        - linked_tax_withheld_refunds: Details of linked tax withheld refunds to the credit note
        - local_currency_code: The local currency code for the credit note.
        - object_: The object type of the credit note.
        - price_type: The type of pricing used for the credit note.
        - reason_code: The reason code for creating the credit note.
        - reference_invoice_id: The ID of the invoice this credit note references.
        - refunded_at: The date when the credit note was refunded.
        - resource_version: The version of the credit note resource.
        - round_off_amount: Amount rounded off for currency conversions.
        - shipping_address: Details of the shipping address associated with the credit note
        - status: The status of the credit note.
        - sub_total: The subtotal amount of the credit note.
        - sub_total_in_local_currency: The subtotal amount in local currency.
        - subscription_id: The ID of the subscription associated with the credit note.
        - taxes: List of taxes applied to the credit note
        - total: The total amount of the credit note.
        - total_in_local_currency: The total amount in local currency.
        - type_: The type of credit note.
        - updated_at: The date when the credit note was last updated.
        - vat_number: VAT number associated with the credit note.
        - vat_number_prefix: Prefix for the VAT number.
        - voided_at: The date when the credit note was voided.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CreditNoteSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.CreditNote`
    :   Retrieve a credit note
        
        Args:
            id: Credit note ID
            **kwargs: Additional parameters
        
        Returns:
            CreditNote

    `list(self, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[CreditNote], CreditNoteListResultMeta]`
    :   List credit notes
        
        Args:
            limit: Parameter limit
            offset: Parameter offset
            **kwargs: Additional parameters
        
        Returns:
            CreditNoteListResult

<a id="CustomerQuery"></a>

`CustomerQuery(connector: ChargebeeConnector)`
:   Query class for Customer entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CustomerSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[CustomerSearchData]`
    :   Search customer records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CustomerSearchFilter):
        - allow_direct_debit: Indicates if direct debit is allowed for the customer.
        - auto_close_invoices: Flag to automatically close invoices for the customer.
        - auto_collection: Configures the automatic collection settings for the customer.
        - backup_payment_source_id: ID of the backup payment source for the customer.
        - balances: Customer's balance information related to their account.
        - billing_address: Customer's billing address details.
        - billing_date: Date for billing cycle.
        - billing_date_mode: Mode for billing date calculation.
        - billing_day_of_week: Day of the week for billing cycle.
        - billing_day_of_week_mode: Mode for billing day of the week calculation.
        - billing_month: Month for billing cycle.
        - business_customer_without_vat_number: Flag indicating business customer without a VAT number.
        - business_entity_id: ID of the business entity.
        - card_status: Status of payment card associated with the customer.
        - channel: Channel through which the customer was acquired.
        - child_account_access: Information regarding the access rights of child accounts linked to the customer's account.
        - client_profile_id: Client profile ID of the customer.
        - company: Company or organization name.
        - consolidated_invoicing: Flag for consolidated invoicing setting.
        - contacts: List of contact details associated with the customer.
        - created_at: Date and time when the customer was created.
        - created_from_ip: IP address from which the customer was created.
        - custom_fields: 
        - customer_type: Type of customer (e.g., individual, business).
        - deleted: Flag indicating if the customer is deleted.
        - email: Email address of the customer.
        - entity_code: Code for the customer entity.
        - excess_payments: Total amount of excess payments by the customer.
        - exempt_number: Exemption number for tax purposes.
        - exemption_details: Details about any exemptions applicable to the customer's account.
        - first_name: First name of the customer.
        - fraud_flag: Flag indicating if fraud is associated with the customer.
        - id: Unique ID of the customer.
        - invoice_notes: Notes added to the customer's invoices.
        - is_location_valid: Flag indicating if the customer location is valid.
        - last_name: Last name of the customer.
        - locale: Locale setting for the customer.
        - meta_data: Additional metadata associated with the customer.
        - mrr: Monthly recurring revenue generated from the customer.
        - net_term_days: Number of days for net terms.
        - object_: Object type for the customer.
        - offline_payment_method: Offline payment method used by the customer.
        - parent_account_access: Information regarding the access rights of the parent account, if applicable.
        - payment_method: Customer's preferred payment method details.
        - phone: Phone number of the customer.
        - pii_cleared: Flag indicating if PII (Personally Identifiable Information) is cleared.
        - preferred_currency_code: Preferred currency code for transactions.
        - primary_payment_source_id: ID of the primary payment source for the customer.
        - promotional_credits: Total amount of promotional credits used.
        - referral_urls: List of referral URLs associated with the customer.
        - refundable_credits: Total amount of refundable credits.
        - registered_for_gst: Flag indicating if the customer is registered for GST.
        - relationship: Details about the relationship of the customer to other entities, if any.
        - resource_version: Version of the customer's resource.
        - tax_providers_fields: Fields related to tax providers.
        - taxability: Taxability status of the customer.
        - unbilled_charges: Total amount of unbilled charges.
        - updated_at: Date and time when the customer record was last updated.
        - use_default_hierarchy_settings: Flag indicating if default hierarchy settings are used.
        - vat_number: VAT number associated with the customer.
        - vat_number_prefix: Prefix for the VAT number.
        - vat_number_status: Status of the VAT number validation.
        - vat_number_validated_time: Date and time when the VAT number was validated.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CustomerSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.Customer`
    :   Retrieve a customer
        
        Args:
            id: Customer ID
            **kwargs: Additional parameters
        
        Returns:
            Customer

    `list(self, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Customer], CustomerListResultMeta]`
    :   List customers
        
        Args:
            limit: Number of items to return (max 100)
            offset: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            CustomerListResult

<a id="EventQuery"></a>

`EventQuery(connector: ChargebeeConnector)`
:   Query class for Event entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: EventSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[EventSearchData]`
    :   Search event records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (EventSearchFilter):
        - api_version: The version of the Chargebee API being used to fetch the event data.
        - content: The specific content or information associated with the event.
        - custom_fields: 
        - event_type: The type or category of the event.
        - id: Unique identifier for the event data record.
        - object_: The object or entity that the event is triggered for.
        - occurred_at: The datetime when the event occurred.
        - source: The source or origin of the event data.
        - user: Information about the user or entity associated with the event.
        - webhook_status: The status of the webhook execution for the event.
        - webhooks: List of webhooks associated with the event.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            EventSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.Event`
    :   Retrieve an event
        
        Args:
            id: Event ID
            **kwargs: Additional parameters
        
        Returns:
            Event

    `list(self, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Event], EventListResultMeta]`
    :   List events
        
        Args:
            limit: Parameter limit
            offset: Parameter offset
            **kwargs: Additional parameters
        
        Returns:
            EventListResult

<a id="InvoiceQuery"></a>

`InvoiceQuery(connector: ChargebeeConnector)`
:   Query class for Invoice entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: InvoiceSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[InvoiceSearchData]`
    :   Search invoice records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (InvoiceSearchFilter):
        - adjustment_credit_notes: Details of adjustment credit notes applied to the invoice
        - amount_adjusted: Total amount adjusted in the invoice
        - amount_due: Amount due for payment
        - amount_paid: Amount already paid
        - amount_to_collect: Amount yet to be collected
        - applied_credits: Details of credits applied to the invoice
        - base_currency_code: Currency code used as base for the invoice
        - billing_address: Details of the billing address associated with the invoice
        - business_entity_id: ID of the business entity
        - channel: Channel through which the invoice was generated
        - credits_applied: Total credits applied to the invoice
        - currency_code: Currency code of the invoice
        - custom_fields: 
        - customer_id: ID of the customer
        - date: Date of the invoice
        - deleted: Flag indicating if the invoice is deleted
        - discounts: Discount details applied to the invoice
        - due_date: Due date for payment
        - dunning_attempts: Details of dunning attempts made
        - dunning_status: Status of dunning for the invoice
        - einvoice: Details of electronic invoice
        - exchange_rate: Exchange rate used for currency conversion
        - expected_payment_date: Expected date of payment
        - first_invoice: Flag indicating whether it's the first invoice
        - generated_at: Date when the invoice was generated
        - has_advance_charges: Flag indicating if there are advance charges
        - id: Unique ID of the invoice
        - is_digital: Flag indicating if the invoice is digital
        - is_gifted: Flag indicating if the invoice is gifted
        - issued_credit_notes: Details of credit notes issued
        - line_item_discounts: Details of line item discounts
        - line_item_taxes: Tax details applied to each line item in the invoice
        - line_item_tiers: Tiers information for each line item in the invoice
        - line_items: Details of individual line items in the invoice
        - linked_orders: Details of linked orders to the invoice
        - linked_payments: Details of linked payments
        - linked_taxes_withheld: Details of linked taxes withheld on the invoice
        - local_currency_code: Local currency code of the invoice
        - local_currency_exchange_rate: Exchange rate for local currency conversion
        - net_term_days: Net term days for payment
        - new_sales_amount: New sales amount in the invoice
        - next_retry_at: Date of the next payment retry
        - notes: Notes associated with the invoice
        - object_: Type of object
        - paid_at: Date when the invoice was paid
        - payment_owner: Owner of the payment
        - po_number: Purchase order number
        - price_type: Type of pricing
        - recurring: Flag indicating if it's a recurring invoice
        - resource_version: Resource version of the invoice
        - round_off_amount: Amount rounded off
        - shipping_address: Details of the shipping address associated with the invoice
        - statement_descriptor: Descriptor for the statement
        - status: Status of the invoice
        - sub_total: Subtotal amount
        - sub_total_in_local_currency: Subtotal amount in local currency
        - subscription_id: ID of the subscription associated
        - tax: Total tax amount
        - tax_category: Tax category
        - taxes: Details of taxes applied
        - term_finalized: Flag indicating if the term is finalized
        - total: Total amount of the invoice
        - total_in_local_currency: Total amount in local currency
        - updated_at: Date of last update
        - vat_number: VAT number
        - vat_number_prefix: Prefix for the VAT number
        - void_reason_code: Reason code for voiding the invoice
        - voided_at: Date when the invoice was voided
        - write_off_amount: Amount written off
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            InvoiceSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.Invoice`
    :   Retrieve an invoice
        
        Args:
            id: Invoice ID
            **kwargs: Additional parameters
        
        Returns:
            Invoice

    `list(self, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Invoice], InvoiceListResultMeta]`
    :   List invoices
        
        Args:
            limit: Parameter limit
            offset: Parameter offset
            **kwargs: Additional parameters
        
        Returns:
            InvoiceListResult

<a id="ItemPriceQuery"></a>

`ItemPriceQuery(connector: ChargebeeConnector)`
:   Query class for ItemPrice entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ItemPriceSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[ItemPriceSearchData]`
    :   Search item_price records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ItemPriceSearchFilter):
        - accounting_detail: Details related to accounting such as cost, revenue, expenses, etc.
        - archived_at: Date and time when the item was archived.
        - billing_cycles: Number of billing cycles for the item.
        - channel: The channel through which the item is sold.
        - created_at: Date and time when the item was created.
        - currency_code: The currency code used for pricing the item.
        - custom_fields: Custom field entries for the item price.
        - description: Description of the item.
        - external_name: External name of the item.
        - free_quantity: Free quantity allowed for the item.
        - free_quantity_in_decimal: Free quantity allowed represented in decimal format.
        - id: Unique identifier for the item price.
        - invoice_notes: Notes to be included in the invoice for the item.
        - is_taxable: Flag indicating whether the item is taxable.
        - item_family_id: Identifier for the item family to which the item belongs.
        - item_id: Unique identifier for the parent item.
        - item_type: Type of the item (e.g., product, service).
        - metadata: Additional metadata associated with the item.
        - name: Name of the item price.
        - object_: Object type representing the item price.
        - period: Duration of the item's billing period.
        - period_unit: Unit of measurement for the billing period duration.
        - price: Price of the item.
        - price_in_decimal: Price of the item represented in decimal format.
        - pricing_model: The pricing model used for the item (e.g., flat fee, usage-based).
        - resource_version: Version of the item price resource.
        - shipping_period: Duration of the item's shipping period.
        - shipping_period_unit: Unit of measurement for the shipping period duration.
        - show_description_in_invoices: Flag indicating whether to show the description in invoices.
        - show_description_in_quotes: Flag indicating whether to show the description in quotes.
        - status: Current status of the item price (e.g., active, inactive).
        - tax_detail: Information about taxes associated with the item price.
        - tiers: Different pricing tiers for the item.
        - trial_end_action: Action to be taken at the end of the trial period.
        - trial_period: Duration of the trial period.
        - trial_period_unit: Unit of measurement for the trial period duration.
        - updated_at: Date and time when the item price was last updated.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ItemPriceSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.ItemPrice`
    :   Retrieve an item price
        
        Args:
            id: Item price ID
            **kwargs: Additional parameters
        
        Returns:
            ItemPrice

    `list(self, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[ItemPrice], ItemPriceListResultMeta]`
    :   List item prices
        
        Args:
            limit: Parameter limit
            offset: Parameter offset
            **kwargs: Additional parameters
        
        Returns:
            ItemPriceListResult

<a id="ItemQuery"></a>

`ItemQuery(connector: ChargebeeConnector)`
:   Query class for Item entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ItemSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[ItemSearchData]`
    :   Search item records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ItemSearchFilter):
        - applicable_items: Items associated with the item
        - archived_at: Date and time when the item was archived
        - channel: Channel the item belongs to
        - custom_fields: Custom field entries for the item
        - description: Description of the item
        - enabled_for_checkout: Flag indicating if the item is enabled for checkout
        - enabled_in_portal: Flag indicating if the item is enabled in the portal
        - external_name: Name of the item in an external system
        - gift_claim_redirect_url: URL to redirect for gift claim
        - id: Unique identifier for the item
        - included_in_mrr: Flag indicating if the item is included in Monthly Recurring Revenue
        - is_giftable: Flag indicating if the item is giftable
        - is_shippable: Flag indicating if the item is shippable
        - item_applicability: Applicability of the item
        - item_family_id: ID of the item's family
        - metadata: Additional data associated with the item
        - metered: Flag indicating if the item is metered
        - name: Name of the item
        - object_: Type of object
        - redirect_url: URL to redirect for the item
        - resource_version: Version of the resource
        - status: Status of the item
        - type_: Type of the item
        - unit: Unit associated with the item
        - updated_at: Date and time when the item was last updated
        - usage_calculation: Calculation method used for item usage
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ItemSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.Item`
    :   Retrieve an item
        
        Args:
            id: Item ID
            **kwargs: Additional parameters
        
        Returns:
            Item

    `list(self, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Item], ItemListResultMeta]`
    :   List items
        
        Args:
            limit: Parameter limit
            offset: Parameter offset
            **kwargs: Additional parameters
        
        Returns:
            ItemListResult

<a id="OrderQuery"></a>

`OrderQuery(connector: ChargebeeConnector)`
:   Query class for Order entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OrderSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[OrderSearchData]`
    :   Search order records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OrderSearchFilter):
        - amount_adjusted: Adjusted amount for the order.
        - amount_paid: Amount paid for the order.
        - base_currency_code: The base currency code used for the order.
        - batch_id: Unique identifier for the batch the order belongs to.
        - billing_address: The billing address associated with the order
        - business_entity_id: Identifier for the business entity associated with the order.
        - cancellation_reason: Reason for order cancellation.
        - cancelled_at: Timestamp when the order was cancelled.
        - created_at: Timestamp when the order was created.
        - created_by: User or system that created the order.
        - currency_code: Currency code used for the order.
        - custom_fields: 
        - customer_id: Identifier for the customer placing the order.
        - deleted: Flag indicating if the order has been deleted.
        - delivered_at: Timestamp when the order was delivered.
        - discount: Discount amount applied to the order.
        - document_number: Unique document number associated with the order.
        - exchange_rate: Rate used for currency exchange in the order.
        - fulfillment_status: Status of fulfillment for the order.
        - gift_id: Identifier for any gift associated with the order.
        - gift_note: Note attached to any gift in the order.
        - id: Unique identifier for the order.
        - invoice_id: Identifier for the invoice associated with the order.
        - invoice_round_off_amount: Round-off amount applied to the invoice.
        - is_gifted: Flag indicating if the order is a gift.
        - is_resent: Flag indicating if the order has been resent.
        - line_item_discounts: Discounts applied to individual line items
        - line_item_taxes: Taxes applied to individual line items
        - linked_credit_notes: Credit notes linked to the order
        - note: Additional notes or comments for the order.
        - object_: Type of object representing an order in the system.
        - order_date: Date when the order was created.
        - order_line_items: List of line items in the order
        - order_type: Type of order such as purchase order or sales order.
        - original_order_id: Identifier for the original order if this is a modified order.
        - paid_on: Timestamp when the order was paid for.
        - payment_status: Status of payment for the order.
        - price_type: Type of pricing used for the order.
        - reference_id: Reference identifier for the order.
        - refundable_credits: Credits that can be refunded for the whole order.
        - refundable_credits_issued: Credits already issued for refund for the whole order.
        - resend_reason: Reason for resending the order.
        - resent_orders: Orders that were resent to the customer
        - resent_status: Status of the resent order.
        - resource_version: Version of the resource or order data.
        - rounding_adjustement: Adjustment made for rounding off the order amount.
        - shipment_carrier: Carrier for shipping the order.
        - shipped_at: Timestamp when the order was shipped.
        - shipping_address: The shipping address for the order
        - shipping_cut_off_date: Date indicating the shipping cut-off for the order.
        - shipping_date: Date when the order is scheduled for shipping.
        - status: Current status of the order.
        - status_update_at: Timestamp when the status of the order was last updated.
        - sub_total: Sub-total amount for the order before applying taxes or discounts.
        - subscription_id: Identifier for the subscription associated with the order.
        - tax: Total tax amount for the order.
        - total: Total amount including taxes and discounts for the order.
        - tracking_id: Tracking identifier for the order shipment.
        - tracking_url: URL for tracking the order shipment.
        - updated_at: Timestamp when the order data was last updated.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OrderSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.Order`
    :   Retrieve an order
        
        Args:
            id: Order ID
            **kwargs: Additional parameters
        
        Returns:
            Order

    `list(self, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Order], OrderListResultMeta]`
    :   List orders
        
        Args:
            limit: Parameter limit
            offset: Parameter offset
            **kwargs: Additional parameters
        
        Returns:
            OrderListResult

<a id="PaymentSourceQuery"></a>

`PaymentSourceQuery(connector: ChargebeeConnector)`
:   Query class for PaymentSource entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: PaymentSourceSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[PaymentSourceSearchData]`
    :   Search payment_source records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (PaymentSourceSearchFilter):
        - amazon_payment: Data related to Amazon Pay payment source
        - bank_account: Data related to bank account payment source
        - business_entity_id: Identifier for the business entity associated with the payment source
        - card: Data related to card payment source
        - created_at: Timestamp indicating when the payment source was created
        - custom_fields: 
        - customer_id: Unique identifier for the customer associated with the payment source
        - deleted: Indicates if the payment source has been deleted
        - gateway: Name of the payment gateway used for the payment source
        - gateway_account_id: Identifier for the gateway account tied to the payment source
        - id: Unique identifier for the payment source
        - ip_address: IP address associated with the payment source
        - issuing_country: Country where the payment source was issued
        - mandates: Data related to mandates for payments
        - object_: Type of object, e.g., payment_source
        - paypal: Data related to PayPal payment source
        - reference_id: Reference identifier for the payment source
        - resource_version: Version of the payment source resource
        - status: Status of the payment source, e.g., active or inactive
        - type_: Type of payment source, e.g., card, bank_account
        - updated_at: Timestamp indicating when the payment source was last updated
        - upi: Data related to UPI payment source
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            PaymentSourceSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.PaymentSource`
    :   Retrieve a payment source
        
        Args:
            id: Payment source ID
            **kwargs: Additional parameters
        
        Returns:
            PaymentSource

    `list(self, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[PaymentSource], PaymentSourceListResultMeta]`
    :   List payment sources
        
        Args:
            limit: Parameter limit
            offset: Parameter offset
            **kwargs: Additional parameters
        
        Returns:
            PaymentSourceListResult

<a id="SubscriptionQuery"></a>

`SubscriptionQuery(connector: ChargebeeConnector)`
:   Query class for Subscription entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SubscriptionSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[SubscriptionSearchData]`
    :   Search subscription records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SubscriptionSearchFilter):
        - activated_at: The date and time when the subscription was activated.
        - addons: Represents any additional features or services added to the subscription
        - affiliate_token: The affiliate token associated with the subscription.
        - auto_close_invoices: Defines if the invoices are automatically closed or not.
        - auto_collection: Indicates if auto-collection is enabled for the subscription.
        - base_currency_code: The base currency code used for the subscription.
        - billing_period: The billing period duration for the subscription.
        - billing_period_unit: The unit of the billing period.
        - business_entity_id: The ID of the business entity to which the subscription belongs.
        - cancel_reason: The reason for the cancellation of the subscription.
        - cancel_reason_code: The code associated with the cancellation reason.
        - cancel_schedule_created_at: The date and time when the cancellation schedule was created.
        - cancelled_at: The date and time when the subscription was cancelled.
        - channel: The channel through which the subscription was acquired.
        - charged_event_based_addons: Details of addons charged based on events
        - charged_items: Lists the items that have been charged as part of the subscription
        - contract_term: Contains details about the contract term of the subscription
        - contract_term_billing_cycle_on_renewal: Indicates if the contract term billing cycle is applied on renewal.
        - coupon: The coupon applied to the subscription.
        - coupons: Details of applied coupons
        - create_pending_invoices: Indicates if pending invoices are created.
        - created_at: The date and time of the creation of the subscription.
        - created_from_ip: The IP address from which the subscription was created.
        - currency_code: The currency code used for the subscription.
        - current_term_end: The end date of the current term for the subscription.
        - current_term_start: The start date of the current term for the subscription.
        - custom_fields: 
        - customer_id: The ID of the customer associated with the subscription.
        - deleted: Indicates if the subscription has been deleted.
        - discounts: Includes any discounts applied to the subscription
        - due_invoices_count: The count of due invoices for the subscription.
        - due_since: The date since which the invoices are due.
        - event_based_addons: Specifies any event-based addons associated with the subscription
        - exchange_rate: The exchange rate used for currency conversion.
        - free_period: The duration of the free period for the subscription.
        - free_period_unit: The unit of the free period duration.
        - gift_id: The ID of the gift associated with the subscription.
        - has_scheduled_advance_invoices: Indicates if there are scheduled advance invoices for the subscription.
        - has_scheduled_changes: Indicates if there are scheduled changes for the subscription.
        - id: The unique ID of the subscription.
        - invoice_notes: Any notes added to the invoices of the subscription.
        - item_tiers: Provides information about tiers or levels for specific subscription items
        - meta_data: Additional metadata associated with subscription
        - metadata: Additional metadata associated with subscription
        - mrr: The monthly recurring revenue generated by the subscription.
        - next_billing_at: The date and time of the next billing event for the subscription.
        - object_: The type of object (subscription).
        - offline_payment_method: The offline payment method used for the subscription.
        - override_relationship: Indicates if the existing relationship is overridden by this subscription.
        - pause_date: The date on which the subscription was paused.
        - payment_source_id: The ID of the payment source used for the subscription.
        - plan_amount: The total amount charged for the plan of the subscription.
        - plan_amount_in_decimal: The total amount charged for the plan in decimal format.
        - plan_free_quantity: The free quantity included in the plan of the subscription.
        - plan_free_quantity_in_decimal: The free quantity included in the plan in decimal format.
        - plan_id: The ID of the plan associated with the subscription.
        - plan_quantity: The quantity of the plan included in the subscription.
        - plan_quantity_in_decimal: The quantity of the plan in decimal format.
        - plan_unit_price: The unit price of the plan for the subscription.
        - plan_unit_price_in_decimal: The unit price of the plan in decimal format.
        - po_number: The purchase order number associated with the subscription.
        - referral_info: Contains details related to any referral information associated with the subscription
        - remaining_billing_cycles: The count of remaining billing cycles for the subscription.
        - resource_version: The version of the resource (subscription).
        - resume_date: The date on which the subscription was resumed.
        - setup_fee: The setup fee charged for the subscription.
        - shipping_address: Stores the shipping address related to the subscription
        - start_date: The start date of the subscription.
        - started_at: The date and time when the subscription started.
        - status: The current status of the subscription.
        - subscription_items: Lists individual items included in the subscription
        - total_dues: The total amount of dues for the subscription.
        - trial_end: The end date of the trial period for the subscription.
        - trial_end_action: The action to be taken at the end of the trial period.
        - trial_start: The start date of the trial period for the subscription.
        - updated_at: The date and time when the subscription was last updated.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SubscriptionSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.Subscription`
    :   Retrieve a subscription
        
        Args:
            id: Subscription ID
            **kwargs: Additional parameters
        
        Returns:
            Subscription

    `list(self, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Subscription], SubscriptionListResultMeta]`
    :   List subscriptions
        
        Args:
            limit: Parameter limit
            offset: Parameter offset
            **kwargs: Additional parameters
        
        Returns:
            SubscriptionListResult

<a id="TransactionQuery"></a>

`TransactionQuery(connector: ChargebeeConnector)`
:   Query class for Transaction entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TransactionSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[TransactionSearchData]`
    :   Search transaction records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TransactionSearchFilter):
        - amount: The total amount of the transaction.
        - amount_capturable: The remaining amount that can be captured in the transaction.
        - amount_unused: The amount in the transaction that remains unused.
        - authorization_reason: Reason for authorization of the transaction.
        - base_currency_code: The base currency code of the transaction.
        - business_entity_id: The ID of the business entity related to the transaction.
        - cn_create_reason_code: Reason code for creating a credit note.
        - cn_date: Date of the credit note.
        - cn_reference_invoice_id: ID of the invoice referenced in the credit note.
        - cn_status: Status of the credit note.
        - cn_total: Total amount of the credit note.
        - currency_code: The currency code of the transaction.
        - custom_fields: 
        - customer_id: The ID of the customer associated with the transaction.
        - date: Date of the transaction.
        - deleted: Flag indicating if the transaction is deleted.
        - error_code: Error code associated with the transaction.
        - error_detail: Detailed error information related to the transaction.
        - error_text: Error message text of the transaction.
        - exchange_rate: Exchange rate used in the transaction.
        - fraud_flag: Flag indicating if the transaction is flagged for fraud.
        - fraud_reason: Reason for flagging the transaction as fraud.
        - gateway: The payment gateway used in the transaction.
        - gateway_account_id: ID of the gateway account used in the transaction.
        - id: Unique identifier of the transaction.
        - id_at_gateway: Transaction ID assigned by the gateway.
        - iin: Bank identification number of the transaction.
        - initiator_type: Type of initiator involved in the transaction.
        - last4: Last 4 digits of the card used in the transaction.
        - linked_credit_notes: Linked credit notes associated with the transaction.
        - linked_invoices: Linked invoices associated with the transaction.
        - linked_payments: Linked payments associated with the transaction.
        - linked_refunds: Linked refunds associated with the transaction.
        - masked_card_number: Masked card number used in the transaction.
        - merchant_reference_id: Merchant reference ID of the transaction.
        - object_: Type of object representing the transaction.
        - payment_method: Payment method used in the transaction.
        - payment_method_details: Details of the payment method used in the transaction.
        - payment_source_id: ID of the payment source used in the transaction.
        - reference_authorization_id: Reference authorization ID of the transaction.
        - reference_number: Reference number associated with the transaction.
        - reference_transaction_id: ID of the reference transaction.
        - refrence_number: Reference number of the transaction.
        - refunded_txn_id: ID of the refunded transaction.
        - resource_version: Resource version of the transaction.
        - reversal_transaction_id: ID of the reversal transaction, if any.
        - settled_at: Date when the transaction was settled.
        - status: Status of the transaction.
        - subscription_id: ID of the subscription related to the transaction.
        - three_d_secure: Flag indicating if 3D secure was used in the transaction.
        - txn_amount: Amount of the transaction.
        - txn_date: Date of the transaction.
        - type_: Type of the transaction.
        - updated_at: Date when the transaction was last updated.
        - voided_at: Date when the transaction was voided.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TransactionSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.Transaction`
    :   Retrieve a transaction
        
        Args:
            id: Transaction ID
            **kwargs: Additional parameters
        
        Returns:
            Transaction

    `list(self, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Transaction], TransactionListResultMeta]`
    :   List transactions
        
        Args:
            limit: Parameter limit
            offset: Parameter offset
            **kwargs: Additional parameters
        
        Returns:
            TransactionListResult