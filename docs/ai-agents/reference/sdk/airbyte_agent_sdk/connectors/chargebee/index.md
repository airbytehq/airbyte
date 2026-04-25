---
id: airbyte_agent_sdk-connectors-chargebee-index
title: airbyte_agent_sdk.connectors.chargebee.index
---

Module airbyte_agent_sdk.connectors.chargebee
=============================================
Chargebee connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.chargebee.connector
* airbyte_agent_sdk.connectors.chargebee.connector_model
* airbyte_agent_sdk.connectors.chargebee.models
* airbyte_agent_sdk.connectors.chargebee.types

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

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[CouponSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[CreditNoteSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[CustomerSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[EventSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[InvoiceSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[ItemPriceSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[ItemSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[OrderSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[PaymentSourceSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[SubscriptionSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[TransactionSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="CouponSearchResult"></a>

`CouponSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CreditNoteSearchResult"></a>

`CreditNoteSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CustomerSearchResult"></a>

`CustomerSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="EventSearchResult"></a>

`EventSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="InvoiceSearchResult"></a>

`InvoiceSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ItemPriceSearchResult"></a>

`ItemPriceSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ItemSearchResult"></a>

`ItemSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="OrderSearchResult"></a>

`OrderSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="PaymentSourceSearchResult"></a>

`PaymentSourceSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SubscriptionSearchResult"></a>

`SubscriptionSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TransactionSearchResult"></a>

`TransactionSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ChargebeeAuthConfig"></a>

`ChargebeeAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Chargebee API key (used as the HTTP Basic username)

    `model_config`
    :   The type of the None singleton.

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

<a id="ChargebeeReplicationConfig"></a>

`ChargebeeReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Chargebee.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ. Data before this date is excluded.

<a id="CouponSearchData"></a>

`CouponSearchData(**data: Any)`
:   Search result data for coupon entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `apply_discount_on: str | None`
    :   Determines where the discount is applied on (e.g. subtotal, total).

    `apply_on: str | None`
    :   Specify on what type of items the coupon applies (e.g. subscription, addon).

    `archived_at: int | None`
    :   Timestamp when the coupon was archived.

    `coupon_constraints: list[typing.Any] | None`
    :   Represents the constraints associated with the coupon

    `created_at: int | None`
    :   Timestamp of the coupon creation.

    `currency_code: str | None`
    :   The currency code for the coupon (e.g. USD, EUR).

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `discount_amount: int | None`
    :   The fixed discount amount applied by the coupon.

    `discount_percentage: float | None`
    :   Percentage discount applied by the coupon.

    `discount_quantity: int | None`
    :   Specifies the number of free units provided for the item price, without affecting the total quantity sold. This parameter is applicable only when the discount_type is set to offer_quantity.

    `discount_type: str | None`
    :   Type of discount (e.g. fixed, percentage).

    `duration_month: int | None`
    :   Duration of the coupon in months.

    `duration_type: str | None`
    :   Type of duration (e.g. forever, one-time).

    `id: str | None`
    :   Unique identifier for the coupon.

    `invoice_name: str | None`
    :   Name displayed on invoices when the coupon is used.

    `invoice_notes: str | None`
    :   Additional notes displayed on invoices when the coupon is used.

    `item_constraint_criteria: list[typing.Any] | None`
    :   Criteria for item constraints

    `item_constraints: list[typing.Any] | None`
    :   Constraints related to the items

    `max_redemptions: int | None`
    :   Maximum number of times the coupon can be redeemed.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the coupon.

    `object_: str | None`
    :   Type of object (usually 'coupon').

    `period: int | None`
    :   Duration or frequency for which the coupon is valid.

    `period_unit: str | None`
    :   Unit of the period (e.g. days, weeks).

    `redemptions: int | None`
    :   Number of times the coupon has been redeemed.

    `resource_version: int | None`
    :   Version of the resource.

    `status: str | None`
    :   Current status of the coupon (e.g. active, inactive).

    `updated_at: int | None`
    :   Timestamp when the coupon was last updated.

    `valid_till: int | None`
    :   Date until which the coupon is valid for use.

<a id="CreditNoteSearchData"></a>

`CreditNoteSearchData(**data: Any)`
:   Search result data for credit_note entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allocations: list[typing.Any] | None`
    :   Details of allocations associated with the credit note

    `amount_allocated: int | None`
    :   The amount of credits allocated.

    `amount_available: int | None`
    :   The amount of credits available.

    `amount_refunded: int | None`
    :   The amount of credits refunded.

    `base_currency_code: str | None`
    :   The base currency code for the credit note.

    `billing_address: dict[str, typing.Any] | None`
    :   Details of the billing address associated with the credit note

    `business_entity_id: str | None`
    :   The ID of the business entity associated with the credit note.

    `channel: str | None`
    :   The channel through which the credit note was created.

    `create_reason_code: str | None`
    :   The reason code for creating the credit note.

    `currency_code: str | None`
    :   The currency code for the credit note.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `customer_id: str | None`
    :   The ID of the customer associated with the credit note.

    `customer_notes: str | None`
    :   Notes provided by the customer for the credit note.

    `date: int | None`
    :   The date when the credit note was created.

    `deleted: bool | None`
    :   Indicates if the credit note has been deleted.

    `discounts: list[typing.Any] | None`
    :   Details of discounts applied to the credit note

    `exchange_rate: float | None`
    :   The exchange rate used for currency conversion.

    `fractional_correction: int | None`
    :   Fractional correction for rounding off decimals.

    `generated_at: int | None`
    :   The date when the credit note was generated.

    `id: str | None`
    :   The unique identifier for the credit note.

    `is_digital: bool | None`
    :   Indicates if the credit note is in digital format.

    `is_vat_moss_registered: bool | None`
    :   Indicates if VAT MOSS registration applies.

    `line_item_discounts: list[typing.Any] | None`
    :   Details of discounts applied at the line item level in the credit note

    `line_item_taxes: list[typing.Any] | None`
    :   Details of taxes applied at the line item level in the credit note

    `line_item_tiers: list[typing.Any] | None`
    :   Details of tiers applied to line items in the credit note

    `line_items: list[typing.Any] | None`
    :   Details of line items in the credit note

    `linked_refunds: list[typing.Any] | None`
    :   Details of linked refunds to the credit note

    `linked_tax_withheld_refunds: list[typing.Any] | None`
    :   Details of linked tax withheld refunds to the credit note

    `local_currency_code: str | None`
    :   The local currency code for the credit note.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   The object type of the credit note.

    `price_type: str | None`
    :   The type of pricing used for the credit note.

    `reason_code: str | None`
    :   The reason code for creating the credit note.

    `reference_invoice_id: str | None`
    :   The ID of the invoice this credit note references.

    `refunded_at: int | None`
    :   The date when the credit note was refunded.

    `resource_version: int | None`
    :   The version of the credit note resource.

    `round_off_amount: int | None`
    :   Amount rounded off for currency conversions.

    `shipping_address: dict[str, typing.Any] | None`
    :   Details of the shipping address associated with the credit note

    `status: str | None`
    :   The status of the credit note.

    `sub_total: int | None`
    :   The subtotal amount of the credit note.

    `sub_total_in_local_currency: int | None`
    :   The subtotal amount in local currency.

    `subscription_id: str | None`
    :   The ID of the subscription associated with the credit note.

    `taxes: list[typing.Any] | None`
    :   List of taxes applied to the credit note

    `total: int | None`
    :   The total amount of the credit note.

    `total_in_local_currency: int | None`
    :   The total amount in local currency.

    `type_: str | None`
    :   The type of credit note.

    `updated_at: int | None`
    :   The date when the credit note was last updated.

    `vat_number: str | None`
    :   VAT number associated with the credit note.

    `vat_number_prefix: str | None`
    :   Prefix for the VAT number.

    `voided_at: int | None`
    :   The date when the credit note was voided.

<a id="CustomerSearchData"></a>

`CustomerSearchData(**data: Any)`
:   Search result data for customer entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allow_direct_debit: bool | None`
    :   Indicates if direct debit is allowed for the customer.

    `auto_close_invoices: bool | None`
    :   Flag to automatically close invoices for the customer.

    `auto_collection: str | None`
    :   Configures the automatic collection settings for the customer.

    `backup_payment_source_id: str | None`
    :   ID of the backup payment source for the customer.

    `balances: list[typing.Any] | None`
    :   Customer's balance information related to their account.

    `billing_address: dict[str, typing.Any] | None`
    :   Customer's billing address details.

    `billing_date: int | None`
    :   Date for billing cycle.

    `billing_date_mode: str | None`
    :   Mode for billing date calculation.

    `billing_day_of_week: str | None`
    :   Day of the week for billing cycle.

    `billing_day_of_week_mode: str | None`
    :   Mode for billing day of the week calculation.

    `billing_month: int | None`
    :   Month for billing cycle.

    `business_customer_without_vat_number: bool | None`
    :   Flag indicating business customer without a VAT number.

    `business_entity_id: str | None`
    :   ID of the business entity.

    `card_status: str | None`
    :   Status of payment card associated with the customer.

    `channel: str | None`
    :   Channel through which the customer was acquired.

    `child_account_access: dict[str, typing.Any] | None`
    :   Information regarding the access rights of child accounts linked to the customer's account.

    `client_profile_id: str | None`
    :   Client profile ID of the customer.

    `company: str | None`
    :   Company or organization name.

    `consolidated_invoicing: bool | None`
    :   Flag for consolidated invoicing setting.

    `contacts: list[typing.Any] | None`
    :   List of contact details associated with the customer.

    `created_at: int | None`
    :   Date and time when the customer was created.

    `created_from_ip: str | None`
    :   IP address from which the customer was created.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `customer_type: str | None`
    :   Type of customer (e.g., individual, business).

    `deleted: bool | None`
    :   Flag indicating if the customer is deleted.

    `email: str | None`
    :   Email address of the customer.

    `entity_code: str | None`
    :   Code for the customer entity.

    `excess_payments: int | None`
    :   Total amount of excess payments by the customer.

    `exempt_number: str | None`
    :   Exemption number for tax purposes.

    `exemption_details: list[typing.Any] | None`
    :   Details about any exemptions applicable to the customer's account.

    `first_name: str | None`
    :   First name of the customer.

    `fraud_flag: str | None`
    :   Flag indicating if fraud is associated with the customer.

    `id: str | None`
    :   Unique ID of the customer.

    `invoice_notes: str | None`
    :   Notes added to the customer's invoices.

    `is_location_valid: bool | None`
    :   Flag indicating if the customer location is valid.

    `last_name: str | None`
    :   Last name of the customer.

    `locale: str | None`
    :   Locale setting for the customer.

    `meta_data: dict[str, typing.Any] | None`
    :   Additional metadata associated with the customer.

    `model_config`
    :   The type of the None singleton.

    `mrr: int | None`
    :   Monthly recurring revenue generated from the customer.

    `net_term_days: int | None`
    :   Number of days for net terms.

    `object_: str | None`
    :   Object type for the customer.

    `offline_payment_method: str | None`
    :   Offline payment method used by the customer.

    `parent_account_access: dict[str, typing.Any] | None`
    :   Information regarding the access rights of the parent account, if applicable.

    `payment_method: dict[str, typing.Any] | None`
    :   Customer's preferred payment method details.

    `phone: str | None`
    :   Phone number of the customer.

    `pii_cleared: str | None`
    :   Flag indicating if PII (Personally Identifiable Information) is cleared.

    `preferred_currency_code: str | None`
    :   Preferred currency code for transactions.

    `primary_payment_source_id: str | None`
    :   ID of the primary payment source for the customer.

    `promotional_credits: int | None`
    :   Total amount of promotional credits used.

    `referral_urls: list[typing.Any] | None`
    :   List of referral URLs associated with the customer.

    `refundable_credits: int | None`
    :   Total amount of refundable credits.

    `registered_for_gst: bool | None`
    :   Flag indicating if the customer is registered for GST.

    `relationship: dict[str, typing.Any] | None`
    :   Details about the relationship of the customer to other entities, if any.

    `resource_version: int | None`
    :   Version of the customer's resource.

    `tax_providers_fields: list[typing.Any] | None`
    :   Fields related to tax providers.

    `taxability: str | None`
    :   Taxability status of the customer.

    `unbilled_charges: int | None`
    :   Total amount of unbilled charges.

    `updated_at: int | None`
    :   Date and time when the customer record was last updated.

    `use_default_hierarchy_settings: bool | None`
    :   Flag indicating if default hierarchy settings are used.

    `vat_number: str | None`
    :   VAT number associated with the customer.

    `vat_number_prefix: str | None`
    :   Prefix for the VAT number.

    `vat_number_status: str | None`
    :   Status of the VAT number validation.

    `vat_number_validated_time: int | None`
    :   Date and time when the VAT number was validated.

<a id="EventSearchData"></a>

`EventSearchData(**data: Any)`
:   Search result data for event entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_version: str | None`
    :   The version of the Chargebee API being used to fetch the event data.

    `content: dict[str, typing.Any] | None`
    :   The specific content or information associated with the event.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `event_type: str | None`
    :   The type or category of the event.

    `id: str | None`
    :   Unique identifier for the event data record.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   The object or entity that the event is triggered for.

    `occurred_at: int | None`
    :   The datetime when the event occurred.

    `source: str | None`
    :   The source or origin of the event data.

    `user: str | None`
    :   Information about the user or entity associated with the event.

    `webhook_status: str | None`
    :   The status of the webhook execution for the event.

    `webhooks: list[typing.Any] | None`
    :   List of webhooks associated with the event.

<a id="InvoiceSearchData"></a>

`InvoiceSearchData(**data: Any)`
:   Search result data for invoice entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `adjustment_credit_notes: list[typing.Any] | None`
    :   Details of adjustment credit notes applied to the invoice

    `amount_adjusted: int | None`
    :   Total amount adjusted in the invoice

    `amount_due: int | None`
    :   Amount due for payment

    `amount_paid: int | None`
    :   Amount already paid

    `amount_to_collect: int | None`
    :   Amount yet to be collected

    `applied_credits: list[typing.Any] | None`
    :   Details of credits applied to the invoice

    `base_currency_code: str | None`
    :   Currency code used as base for the invoice

    `billing_address: dict[str, typing.Any] | None`
    :   Details of the billing address associated with the invoice

    `business_entity_id: str | None`
    :   ID of the business entity

    `channel: str | None`
    :   Channel through which the invoice was generated

    `credits_applied: int | None`
    :   Total credits applied to the invoice

    `currency_code: str | None`
    :   Currency code of the invoice

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `customer_id: str | None`
    :   ID of the customer

    `date: int | None`
    :   Date of the invoice

    `deleted: bool | None`
    :   Flag indicating if the invoice is deleted

    `discounts: list[typing.Any] | None`
    :   Discount details applied to the invoice

    `due_date: int | None`
    :   Due date for payment

    `dunning_attempts: list[typing.Any] | None`
    :   Details of dunning attempts made

    `dunning_status: str | None`
    :   Status of dunning for the invoice

    `einvoice: dict[str, typing.Any] | None`
    :   Details of electronic invoice

    `exchange_rate: float | None`
    :   Exchange rate used for currency conversion

    `expected_payment_date: int | None`
    :   Expected date of payment

    `first_invoice: bool | None`
    :   Flag indicating whether it's the first invoice

    `generated_at: int | None`
    :   Date when the invoice was generated

    `has_advance_charges: bool | None`
    :   Flag indicating if there are advance charges

    `id: str | None`
    :   Unique ID of the invoice

    `is_digital: bool | None`
    :   Flag indicating if the invoice is digital

    `is_gifted: bool | None`
    :   Flag indicating if the invoice is gifted

    `issued_credit_notes: list[typing.Any] | None`
    :   Details of credit notes issued

    `line_item_discounts: list[typing.Any] | None`
    :   Details of line item discounts

    `line_item_taxes: list[typing.Any] | None`
    :   Tax details applied to each line item in the invoice

    `line_item_tiers: list[typing.Any] | None`
    :   Tiers information for each line item in the invoice

    `line_items: list[typing.Any] | None`
    :   Details of individual line items in the invoice

    `linked_orders: list[typing.Any] | None`
    :   Details of linked orders to the invoice

    `linked_payments: list[typing.Any] | None`
    :   Details of linked payments

    `linked_taxes_withheld: list[typing.Any] | None`
    :   Details of linked taxes withheld on the invoice

    `local_currency_code: str | None`
    :   Local currency code of the invoice

    `local_currency_exchange_rate: float | None`
    :   Exchange rate for local currency conversion

    `model_config`
    :   The type of the None singleton.

    `net_term_days: int | None`
    :   Net term days for payment

    `new_sales_amount: int | None`
    :   New sales amount in the invoice

    `next_retry_at: int | None`
    :   Date of the next payment retry

    `notes: list[typing.Any] | None`
    :   Notes associated with the invoice

    `object_: str | None`
    :   Type of object

    `paid_at: int | None`
    :   Date when the invoice was paid

    `payment_owner: str | None`
    :   Owner of the payment

    `po_number: str | None`
    :   Purchase order number

    `price_type: str | None`
    :   Type of pricing

    `recurring: bool | None`
    :   Flag indicating if it's a recurring invoice

    `resource_version: int | None`
    :   Resource version of the invoice

    `round_off_amount: int | None`
    :   Amount rounded off

    `shipping_address: dict[str, typing.Any] | None`
    :   Details of the shipping address associated with the invoice

    `statement_descriptor: dict[str, typing.Any] | None`
    :   Descriptor for the statement

    `status: str | None`
    :   Status of the invoice

    `sub_total: int | None`
    :   Subtotal amount

    `sub_total_in_local_currency: int | None`
    :   Subtotal amount in local currency

    `subscription_id: str | None`
    :   ID of the subscription associated

    `tax: int | None`
    :   Total tax amount

    `tax_category: str | None`
    :   Tax category

    `taxes: list[typing.Any] | None`
    :   Details of taxes applied

    `term_finalized: bool | None`
    :   Flag indicating if the term is finalized

    `total: int | None`
    :   Total amount of the invoice

    `total_in_local_currency: int | None`
    :   Total amount in local currency

    `updated_at: int | None`
    :   Date of last update

    `vat_number: str | None`
    :   VAT number

    `vat_number_prefix: str | None`
    :   Prefix for the VAT number

    `void_reason_code: str | None`
    :   Reason code for voiding the invoice

    `voided_at: int | None`
    :   Date when the invoice was voided

    `write_off_amount: int | None`
    :   Amount written off

<a id="ItemPriceSearchData"></a>

`ItemPriceSearchData(**data: Any)`
:   Search result data for item_price entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accounting_detail: dict[str, typing.Any] | None`
    :   Details related to accounting such as cost, revenue, expenses, etc.

    `archived_at: int | None`
    :   Date and time when the item was archived.

    `billing_cycles: int | None`
    :   Number of billing cycles for the item.

    `channel: str | None`
    :   The channel through which the item is sold.

    `created_at: int | None`
    :   Date and time when the item was created.

    `currency_code: str | None`
    :   The currency code used for pricing the item.

    `custom_fields: list[typing.Any] | None`
    :   Custom field entries for the item price.

    `description: str | None`
    :   Description of the item.

    `external_name: str | None`
    :   External name of the item.

    `free_quantity: int | None`
    :   Free quantity allowed for the item.

    `free_quantity_in_decimal: str | None`
    :   Free quantity allowed represented in decimal format.

    `id: str | None`
    :   Unique identifier for the item price.

    `invoice_notes: str | None`
    :   Notes to be included in the invoice for the item.

    `is_taxable: bool | None`
    :   Flag indicating whether the item is taxable.

    `item_family_id: str | None`
    :   Identifier for the item family to which the item belongs.

    `item_id: str | None`
    :   Unique identifier for the parent item.

    `item_type: str | None`
    :   Type of the item (e.g., product, service).

    `metadata: dict[str, typing.Any] | None`
    :   Additional metadata associated with the item.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the item price.

    `object_: str | None`
    :   Object type representing the item price.

    `period: int | None`
    :   Duration of the item's billing period.

    `period_unit: str | None`
    :   Unit of measurement for the billing period duration.

    `price: int | None`
    :   Price of the item.

    `price_in_decimal: str | None`
    :   Price of the item represented in decimal format.

    `pricing_model: str | None`
    :   The pricing model used for the item (e.g., flat fee, usage-based).

    `resource_version: int | None`
    :   Version of the item price resource.

    `shipping_period: int | None`
    :   Duration of the item's shipping period.

    `shipping_period_unit: str | None`
    :   Unit of measurement for the shipping period duration.

    `show_description_in_invoices: bool | None`
    :   Flag indicating whether to show the description in invoices.

    `show_description_in_quotes: bool | None`
    :   Flag indicating whether to show the description in quotes.

    `status: str | None`
    :   Current status of the item price (e.g., active, inactive).

    `tax_detail: dict[str, typing.Any] | None`
    :   Information about taxes associated with the item price.

    `tiers: list[typing.Any] | None`
    :   Different pricing tiers for the item.

    `trial_end_action: str | None`
    :   Action to be taken at the end of the trial period.

    `trial_period: int | None`
    :   Duration of the trial period.

    `trial_period_unit: str | None`
    :   Unit of measurement for the trial period duration.

    `updated_at: int | None`
    :   Date and time when the item price was last updated.

<a id="ItemSearchData"></a>

`ItemSearchData(**data: Any)`
:   Search result data for item entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `applicable_items: list[typing.Any] | None`
    :   Items associated with the item

    `archived_at: int | None`
    :   Date and time when the item was archived

    `channel: str | None`
    :   Channel the item belongs to

    `custom_fields: list[typing.Any] | None`
    :   Custom field entries for the item

    `description: str | None`
    :   Description of the item

    `enabled_for_checkout: bool | None`
    :   Flag indicating if the item is enabled for checkout

    `enabled_in_portal: bool | None`
    :   Flag indicating if the item is enabled in the portal

    `external_name: str | None`
    :   Name of the item in an external system

    `gift_claim_redirect_url: str | None`
    :   URL to redirect for gift claim

    `id: str | None`
    :   Unique identifier for the item

    `included_in_mrr: bool | None`
    :   Flag indicating if the item is included in Monthly Recurring Revenue

    `is_giftable: bool | None`
    :   Flag indicating if the item is giftable

    `is_shippable: bool | None`
    :   Flag indicating if the item is shippable

    `item_applicability: str | None`
    :   Applicability of the item

    `item_family_id: str | None`
    :   ID of the item's family

    `metadata: dict[str, typing.Any] | None`
    :   Additional data associated with the item

    `metered: bool | None`
    :   Flag indicating if the item is metered

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the item

    `object_: str | None`
    :   Type of object

    `redirect_url: str | None`
    :   URL to redirect for the item

    `resource_version: int | None`
    :   Version of the resource

    `status: str | None`
    :   Status of the item

    `type_: str | None`
    :   Type of the item

    `unit: str | None`
    :   Unit associated with the item

    `updated_at: int | None`
    :   Date and time when the item was last updated

    `usage_calculation: str | None`
    :   Calculation method used for item usage

<a id="OrderSearchData"></a>

`OrderSearchData(**data: Any)`
:   Search result data for order entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount_adjusted: int | None`
    :   Adjusted amount for the order.

    `amount_paid: int | None`
    :   Amount paid for the order.

    `base_currency_code: str | None`
    :   The base currency code used for the order.

    `batch_id: str | None`
    :   Unique identifier for the batch the order belongs to.

    `billing_address: dict[str, typing.Any] | None`
    :   The billing address associated with the order

    `business_entity_id: str | None`
    :   Identifier for the business entity associated with the order.

    `cancellation_reason: str | None`
    :   Reason for order cancellation.

    `cancelled_at: int | None`
    :   Timestamp when the order was cancelled.

    `created_at: int | None`
    :   Timestamp when the order was created.

    `created_by: str | None`
    :   User or system that created the order.

    `currency_code: str | None`
    :   Currency code used for the order.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `customer_id: str | None`
    :   Identifier for the customer placing the order.

    `deleted: bool | None`
    :   Flag indicating if the order has been deleted.

    `delivered_at: int | None`
    :   Timestamp when the order was delivered.

    `discount: int | None`
    :   Discount amount applied to the order.

    `document_number: str | None`
    :   Unique document number associated with the order.

    `exchange_rate: float | None`
    :   Rate used for currency exchange in the order.

    `fulfillment_status: str | None`
    :   Status of fulfillment for the order.

    `gift_id: str | None`
    :   Identifier for any gift associated with the order.

    `gift_note: str | None`
    :   Note attached to any gift in the order.

    `id: str | None`
    :   Unique identifier for the order.

    `invoice_id: str | None`
    :   Identifier for the invoice associated with the order.

    `invoice_round_off_amount: int | None`
    :   Round-off amount applied to the invoice.

    `is_gifted: bool | None`
    :   Flag indicating if the order is a gift.

    `is_resent: bool | None`
    :   Flag indicating if the order has been resent.

    `line_item_discounts: list[typing.Any] | None`
    :   Discounts applied to individual line items

    `line_item_taxes: list[typing.Any] | None`
    :   Taxes applied to individual line items

    `linked_credit_notes: list[typing.Any] | None`
    :   Credit notes linked to the order

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   Additional notes or comments for the order.

    `object_: str | None`
    :   Type of object representing an order in the system.

    `order_date: int | None`
    :   Date when the order was created.

    `order_line_items: list[typing.Any] | None`
    :   List of line items in the order

    `order_type: str | None`
    :   Type of order such as purchase order or sales order.

    `original_order_id: str | None`
    :   Identifier for the original order if this is a modified order.

    `paid_on: int | None`
    :   Timestamp when the order was paid for.

    `payment_status: str | None`
    :   Status of payment for the order.

    `price_type: str | None`
    :   Type of pricing used for the order.

    `reference_id: str | None`
    :   Reference identifier for the order.

    `refundable_credits: int | None`
    :   Credits that can be refunded for the whole order.

    `refundable_credits_issued: int | None`
    :   Credits already issued for refund for the whole order.

    `resend_reason: str | None`
    :   Reason for resending the order.

    `resent_orders: list[typing.Any] | None`
    :   Orders that were resent to the customer

    `resent_status: str | None`
    :   Status of the resent order.

    `resource_version: int | None`
    :   Version of the resource or order data.

    `rounding_adjustement: int | None`
    :   Adjustment made for rounding off the order amount.

    `shipment_carrier: str | None`
    :   Carrier for shipping the order.

    `shipped_at: int | None`
    :   Timestamp when the order was shipped.

    `shipping_address: dict[str, typing.Any] | None`
    :   The shipping address for the order

    `shipping_cut_off_date: int | None`
    :   Date indicating the shipping cut-off for the order.

    `shipping_date: int | None`
    :   Date when the order is scheduled for shipping.

    `status: str | None`
    :   Current status of the order.

    `status_update_at: int | None`
    :   Timestamp when the status of the order was last updated.

    `sub_total: int | None`
    :   Sub-total amount for the order before applying taxes or discounts.

    `subscription_id: str | None`
    :   Identifier for the subscription associated with the order.

    `tax: int | None`
    :   Total tax amount for the order.

    `total: int | None`
    :   Total amount including taxes and discounts for the order.

    `tracking_id: str | None`
    :   Tracking identifier for the order shipment.

    `tracking_url: str | None`
    :   URL for tracking the order shipment.

    `updated_at: int | None`
    :   Timestamp when the order data was last updated.

<a id="PaymentSourceSearchData"></a>

`PaymentSourceSearchData(**data: Any)`
:   Search result data for payment_source entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amazon_payment: dict[str, typing.Any] | None`
    :   Data related to Amazon Pay payment source

    `bank_account: dict[str, typing.Any] | None`
    :   Data related to bank account payment source

    `business_entity_id: str | None`
    :   Identifier for the business entity associated with the payment source

    `card: dict[str, typing.Any] | None`
    :   Data related to card payment source

    `created_at: int | None`
    :   Timestamp indicating when the payment source was created

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `customer_id: str | None`
    :   Unique identifier for the customer associated with the payment source

    `deleted: bool | None`
    :   Indicates if the payment source has been deleted

    `gateway: str | None`
    :   Name of the payment gateway used for the payment source

    `gateway_account_id: str | None`
    :   Identifier for the gateway account tied to the payment source

    `id: str | None`
    :   Unique identifier for the payment source

    `ip_address: str | None`
    :   IP address associated with the payment source

    `issuing_country: str | None`
    :   Country where the payment source was issued

    `mandates: dict[str, typing.Any] | None`
    :   Data related to mandates for payments

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   Type of object, e.g., payment_source

    `paypal: dict[str, typing.Any] | None`
    :   Data related to PayPal payment source

    `reference_id: str | None`
    :   Reference identifier for the payment source

    `resource_version: int | None`
    :   Version of the payment source resource

    `status: str | None`
    :   Status of the payment source, e.g., active or inactive

    `type_: str | None`
    :   Type of payment source, e.g., card, bank_account

    `updated_at: int | None`
    :   Timestamp indicating when the payment source was last updated

    `upi: dict[str, typing.Any] | None`
    :   Data related to UPI payment source

<a id="SubscriptionSearchData"></a>

`SubscriptionSearchData(**data: Any)`
:   Search result data for subscription entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `activated_at: int | None`
    :   The date and time when the subscription was activated.

    `addons: list[typing.Any] | None`
    :   Represents any additional features or services added to the subscription

    `affiliate_token: str | None`
    :   The affiliate token associated with the subscription.

    `auto_close_invoices: bool | None`
    :   Defines if the invoices are automatically closed or not.

    `auto_collection: str | None`
    :   Indicates if auto-collection is enabled for the subscription.

    `base_currency_code: str | None`
    :   The base currency code used for the subscription.

    `billing_period: int | None`
    :   The billing period duration for the subscription.

    `billing_period_unit: str | None`
    :   The unit of the billing period.

    `business_entity_id: str | None`
    :   The ID of the business entity to which the subscription belongs.

    `cancel_reason: str | None`
    :   The reason for the cancellation of the subscription.

    `cancel_reason_code: str | None`
    :   The code associated with the cancellation reason.

    `cancel_schedule_created_at: int | None`
    :   The date and time when the cancellation schedule was created.

    `cancelled_at: int | None`
    :   The date and time when the subscription was cancelled.

    `channel: str | None`
    :   The channel through which the subscription was acquired.

    `charged_event_based_addons: list[typing.Any] | None`
    :   Details of addons charged based on events

    `charged_items: list[typing.Any] | None`
    :   Lists the items that have been charged as part of the subscription

    `contract_term: dict[str, typing.Any] | None`
    :   Contains details about the contract term of the subscription

    `contract_term_billing_cycle_on_renewal: int | None`
    :   Indicates if the contract term billing cycle is applied on renewal.

    `coupon: str | None`
    :   The coupon applied to the subscription.

    `coupons: list[typing.Any] | None`
    :   Details of applied coupons

    `create_pending_invoices: bool | None`
    :   Indicates if pending invoices are created.

    `created_at: int | None`
    :   The date and time of the creation of the subscription.

    `created_from_ip: str | None`
    :   The IP address from which the subscription was created.

    `currency_code: str | None`
    :   The currency code used for the subscription.

    `current_term_end: int | None`
    :   The end date of the current term for the subscription.

    `current_term_start: int | None`
    :   The start date of the current term for the subscription.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `customer_id: str | None`
    :   The ID of the customer associated with the subscription.

    `deleted: bool | None`
    :   Indicates if the subscription has been deleted.

    `discounts: list[typing.Any] | None`
    :   Includes any discounts applied to the subscription

    `due_invoices_count: int | None`
    :   The count of due invoices for the subscription.

    `due_since: int | None`
    :   The date since which the invoices are due.

    `event_based_addons: list[typing.Any] | None`
    :   Specifies any event-based addons associated with the subscription

    `exchange_rate: float | None`
    :   The exchange rate used for currency conversion.

    `free_period: int | None`
    :   The duration of the free period for the subscription.

    `free_period_unit: str | None`
    :   The unit of the free period duration.

    `gift_id: str | None`
    :   The ID of the gift associated with the subscription.

    `has_scheduled_advance_invoices: bool | None`
    :   Indicates if there are scheduled advance invoices for the subscription.

    `has_scheduled_changes: bool | None`
    :   Indicates if there are scheduled changes for the subscription.

    `id: str | None`
    :   The unique ID of the subscription.

    `invoice_notes: str | None`
    :   Any notes added to the invoices of the subscription.

    `item_tiers: list[typing.Any] | None`
    :   Provides information about tiers or levels for specific subscription items

    `meta_data: dict[str, typing.Any] | None`
    :   Additional metadata associated with subscription

    `metadata: dict[str, typing.Any] | None`
    :   Additional metadata associated with subscription

    `model_config`
    :   The type of the None singleton.

    `mrr: int | None`
    :   The monthly recurring revenue generated by the subscription.

    `next_billing_at: int | None`
    :   The date and time of the next billing event for the subscription.

    `object_: str | None`
    :   The type of object (subscription).

    `offline_payment_method: str | None`
    :   The offline payment method used for the subscription.

    `override_relationship: bool | None`
    :   Indicates if the existing relationship is overridden by this subscription.

    `pause_date: int | None`
    :   The date on which the subscription was paused.

    `payment_source_id: str | None`
    :   The ID of the payment source used for the subscription.

    `plan_amount: int | None`
    :   The total amount charged for the plan of the subscription.

    `plan_amount_in_decimal: str | None`
    :   The total amount charged for the plan in decimal format.

    `plan_free_quantity: int | None`
    :   The free quantity included in the plan of the subscription.

    `plan_free_quantity_in_decimal: str | None`
    :   The free quantity included in the plan in decimal format.

    `plan_id: str | None`
    :   The ID of the plan associated with the subscription.

    `plan_quantity: int | None`
    :   The quantity of the plan included in the subscription.

    `plan_quantity_in_decimal: str | None`
    :   The quantity of the plan in decimal format.

    `plan_unit_price: int | None`
    :   The unit price of the plan for the subscription.

    `plan_unit_price_in_decimal: str | None`
    :   The unit price of the plan in decimal format.

    `po_number: str | None`
    :   The purchase order number associated with the subscription.

    `referral_info: dict[str, typing.Any] | None`
    :   Contains details related to any referral information associated with the subscription

    `remaining_billing_cycles: int | None`
    :   The count of remaining billing cycles for the subscription.

    `resource_version: int | None`
    :   The version of the resource (subscription).

    `resume_date: int | None`
    :   The date on which the subscription was resumed.

    `setup_fee: int | None`
    :   The setup fee charged for the subscription.

    `shipping_address: dict[str, typing.Any] | None`
    :   Stores the shipping address related to the subscription

    `start_date: int | None`
    :   The start date of the subscription.

    `started_at: int | None`
    :   The date and time when the subscription started.

    `status: str | None`
    :   The current status of the subscription.

    `subscription_items: list[typing.Any] | None`
    :   Lists individual items included in the subscription

    `total_dues: int | None`
    :   The total amount of dues for the subscription.

    `trial_end: int | None`
    :   The end date of the trial period for the subscription.

    `trial_end_action: str | None`
    :   The action to be taken at the end of the trial period.

    `trial_start: int | None`
    :   The start date of the trial period for the subscription.

    `updated_at: int | None`
    :   The date and time when the subscription was last updated.

<a id="TransactionSearchData"></a>

`TransactionSearchData(**data: Any)`
:   Search result data for transaction entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | None`
    :   The total amount of the transaction.

    `amount_capturable: int | None`
    :   The remaining amount that can be captured in the transaction.

    `amount_unused: int | None`
    :   The amount in the transaction that remains unused.

    `authorization_reason: str | None`
    :   Reason for authorization of the transaction.

    `base_currency_code: str | None`
    :   The base currency code of the transaction.

    `business_entity_id: str | None`
    :   The ID of the business entity related to the transaction.

    `cn_create_reason_code: str | None`
    :   Reason code for creating a credit note.

    `cn_date: int | None`
    :   Date of the credit note.

    `cn_reference_invoice_id: str | None`
    :   ID of the invoice referenced in the credit note.

    `cn_status: str | None`
    :   Status of the credit note.

    `cn_total: int | None`
    :   Total amount of the credit note.

    `currency_code: str | None`
    :   The currency code of the transaction.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `customer_id: str | None`
    :   The ID of the customer associated with the transaction.

    `date: int | None`
    :   Date of the transaction.

    `deleted: bool | None`
    :   Flag indicating if the transaction is deleted.

    `error_code: str | None`
    :   Error code associated with the transaction.

    `error_detail: str | None`
    :   Detailed error information related to the transaction.

    `error_text: str | None`
    :   Error message text of the transaction.

    `exchange_rate: float | None`
    :   Exchange rate used in the transaction.

    `fraud_flag: str | None`
    :   Flag indicating if the transaction is flagged for fraud.

    `fraud_reason: str | None`
    :   Reason for flagging the transaction as fraud.

    `gateway: str | None`
    :   The payment gateway used in the transaction.

    `gateway_account_id: str | None`
    :   ID of the gateway account used in the transaction.

    `id: str | None`
    :   Unique identifier of the transaction.

    `id_at_gateway: str | None`
    :   Transaction ID assigned by the gateway.

    `iin: str | None`
    :   Bank identification number of the transaction.

    `initiator_type: str | None`
    :   Type of initiator involved in the transaction.

    `last4: str | None`
    :   Last 4 digits of the card used in the transaction.

    `linked_credit_notes: list[typing.Any] | None`
    :   Linked credit notes associated with the transaction.

    `linked_invoices: list[typing.Any] | None`
    :   Linked invoices associated with the transaction.

    `linked_payments: list[typing.Any] | None`
    :   Linked payments associated with the transaction.

    `linked_refunds: list[typing.Any] | None`
    :   Linked refunds associated with the transaction.

    `masked_card_number: str | None`
    :   Masked card number used in the transaction.

    `merchant_reference_id: str | None`
    :   Merchant reference ID of the transaction.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   Type of object representing the transaction.

    `payment_method: str | None`
    :   Payment method used in the transaction.

    `payment_method_details: str | None`
    :   Details of the payment method used in the transaction.

    `payment_source_id: str | None`
    :   ID of the payment source used in the transaction.

    `reference_authorization_id: str | None`
    :   Reference authorization ID of the transaction.

    `reference_number: str | None`
    :   Reference number associated with the transaction.

    `reference_transaction_id: str | None`
    :   ID of the reference transaction.

    `refrence_number: str | None`
    :   Reference number of the transaction.

    `refunded_txn_id: str | None`
    :   ID of the refunded transaction.

    `resource_version: int | None`
    :   Resource version of the transaction.

    `reversal_transaction_id: str | None`
    :   ID of the reversal transaction, if any.

    `settled_at: int | None`
    :   Date when the transaction was settled.

    `status: str | None`
    :   Status of the transaction.

    `subscription_id: str | None`
    :   ID of the subscription related to the transaction.

    `three_d_secure: bool | None`
    :   Flag indicating if 3D secure was used in the transaction.

    `txn_amount: int | None`
    :   Amount of the transaction.

    `txn_date: int | None`
    :   Date of the transaction.

    `type_: str | None`
    :   Type of the transaction.

    `updated_at: int | None`
    :   Date when the transaction was last updated.

    `voided_at: int | None`
    :   Date when the transaction was voided.