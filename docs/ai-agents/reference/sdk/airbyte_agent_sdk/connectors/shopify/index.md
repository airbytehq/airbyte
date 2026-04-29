---
id: airbyte_agent_sdk-connectors-shopify-index
title: airbyte_agent_sdk.connectors.shopify.index
---

Module airbyte_agent_sdk.connectors.shopify
===========================================
Shopify connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.shopify.connector
* airbyte_agent_sdk.connectors.shopify.connector_model
* airbyte_agent_sdk.connectors.shopify.models
* airbyte_agent_sdk.connectors.shopify.types

Classes
-------

<a id="AbandonedCheckoutsSearchData"></a>

`AbandonedCheckoutsSearchData(**data: Any)`
:   Search result data for abandoned_checkouts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `completed_at: str | None`
    :   ISO 8601 timestamp when the checkout was completed, if applicable

    `created_at: str | None`
    :   ISO 8601 timestamp when the checkout was created

    `currency: str | None`
    :   ISO 4217 currency code for the checkout totals

    `email: str | None`
    :   Email address provided for the checkout

    `id: int | None`
    :   Unique identifier for the abandoned checkout

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Shopify-assigned display name for the checkout (e.g. `#C12345`)

    `phone: str | None`
    :   Phone number provided for the checkout

    `token: str | None`
    :   Unique token identifying the checkout

    `total_price: str | None`
    :   Total price of the checkout in the shop's currency

    `updated_at: str | None`
    :   ISO 8601 timestamp when the checkout was last updated

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

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[AbandonedCheckoutsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[CollectsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[CountriesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[CustomCollectionsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[CustomersSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[DiscountCodesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[DraftOrdersSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[FulfillmentOrdersSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[FulfillmentsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[InventoryItemsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[InventoryLevelsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[LocationsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldCustomersSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldDraftOrdersSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldLocationsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldOrdersSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldProductImagesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldProductVariantsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldProductsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldShopsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldSmartCollectionsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[OrderRefundsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[PriceRulesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[ProductImagesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[ProductVariantsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[ShopSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[SmartCollectionsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[TenderTransactionsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsSearchResult"></a>

`AbandonedCheckoutsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CollectsSearchResult"></a>

`CollectsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CountriesSearchResult"></a>

`CountriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CustomCollectionsSearchResult"></a>

`CustomCollectionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CustomersSearchResult"></a>

`CustomersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="DiscountCodesSearchResult"></a>

`DiscountCodesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="DraftOrdersSearchResult"></a>

`DraftOrdersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="FulfillmentOrdersSearchResult"></a>

`FulfillmentOrdersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="FulfillmentsSearchResult"></a>

`FulfillmentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="InventoryItemsSearchResult"></a>

`InventoryItemsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="InventoryLevelsSearchResult"></a>

`InventoryLevelsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="LocationsSearchResult"></a>

`LocationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MetafieldCustomersSearchResult"></a>

`MetafieldCustomersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MetafieldDraftOrdersSearchResult"></a>

`MetafieldDraftOrdersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MetafieldLocationsSearchResult"></a>

`MetafieldLocationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MetafieldOrdersSearchResult"></a>

`MetafieldOrdersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MetafieldProductImagesSearchResult"></a>

`MetafieldProductImagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MetafieldProductVariantsSearchResult"></a>

`MetafieldProductVariantsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MetafieldProductsSearchResult"></a>

`MetafieldProductsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MetafieldShopsSearchResult"></a>

`MetafieldShopsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MetafieldSmartCollectionsSearchResult"></a>

`MetafieldSmartCollectionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="OrderRefundsSearchResult"></a>

`OrderRefundsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="PriceRulesSearchResult"></a>

`PriceRulesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ProductImagesSearchResult"></a>

`ProductImagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ProductVariantsSearchResult"></a>

`ProductVariantsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ShopSearchResult"></a>

`ShopSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SmartCollectionsSearchResult"></a>

`SmartCollectionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TenderTransactionsSearchResult"></a>

`TenderTransactionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CollectsSearchData"></a>

`CollectsSearchData(**data: Any)`
:   Search result data for collects entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `collection_id: int | None`
    :   Identifier of the collection the product belongs to

    `created_at: str | None`
    :   ISO 8601 timestamp when the collect was created

    `id: int | None`
    :   Unique identifier for the collect

    `model_config`
    :   The type of the None singleton.

    `position: int | None`
    :   Position of the product within the collection

    `product_id: int | None`
    :   Identifier of the product in the collection

    `updated_at: str | None`
    :   ISO 8601 timestamp when the collect was last updated

<a id="CountriesSearchData"></a>

`CountriesSearchData(**data: Any)`
:   Search result data for countries entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   ISO 3166-1 alpha-2 country code

    `id: int | None`
    :   Unique identifier for the country tax row

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Human-readable country name

    `tax_name: str | None`
    :   Localized name of the tax applied in this country

<a id="CustomCollectionsSearchData"></a>

`CustomCollectionsSearchData(**data: Any)`
:   Search result data for custom_collections entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `handle: str | None`
    :   URL-friendly handle for the custom collection

    `id: int | None`
    :   Unique identifier for the custom collection

    `model_config`
    :   The type of the None singleton.

    `published_at: str | None`
    :   ISO 8601 timestamp when the collection was published

    `published_scope: str | None`
    :   Publishing scope (`web` or `global`)

    `sort_order: str | None`
    :   How products are sorted within the collection (e.g. `best-selling`)

    `title: str | None`
    :   Display title of the custom collection

    `updated_at: str | None`
    :   ISO 8601 timestamp when the collection was last updated

<a id="CustomersSearchData"></a>

`CustomersSearchData(**data: Any)`
:   Search result data for customers entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the customer record was created

    `currency: str | None`
    :   ISO 4217 currency code for the customer's total spend

    `email: str | None`
    :   Primary email address of the customer

    `first_name: str | None`
    :   First name of the customer

    `id: int | None`
    :   Unique identifier for the customer

    `last_name: str | None`
    :   Last name of the customer

    `model_config`
    :   The type of the None singleton.

    `orders_count: int | None`
    :   Number of orders placed by the customer

    `phone: str | None`
    :   Primary phone number of the customer

    `state: str | None`
    :   Account state (`disabled`, `invited`, `enabled`, `declined`)

    `total_spent: str | None`
    :   Total lifetime amount spent by the customer

    `updated_at: str | None`
    :   ISO 8601 timestamp when the customer record was last updated

<a id="DiscountCodesSearchData"></a>

`DiscountCodesSearchData(**data: Any)`
:   Search result data for discount_codes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   Discount code string shoppers enter at checkout

    `created_at: str | None`
    :   ISO 8601 timestamp when the code was created

    `id: int | None`
    :   Unique identifier for the discount code

    `model_config`
    :   The type of the None singleton.

    `price_rule_id: int | None`
    :   Identifier of the parent price rule

    `updated_at: str | None`
    :   ISO 8601 timestamp when the code was last updated

    `usage_count: int | None`
    :   Number of times the code has been redeemed

<a id="DraftOrdersSearchData"></a>

`DraftOrdersSearchData(**data: Any)`
:   Search result data for draft_orders entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `completed_at: str | None`
    :   ISO 8601 timestamp when the draft order was completed, if applicable

    `created_at: str | None`
    :   ISO 8601 timestamp when the draft order was created

    `currency: str | None`
    :   ISO 4217 currency code for the draft order totals

    `email: str | None`
    :   Email address associated with the draft order

    `id: int | None`
    :   Unique identifier for the draft order

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Shopify-assigned display name for the draft order (e.g. `#D12345`)

    `order_id: int | None`
    :   Identifier of the completed order, if the draft has been completed

    `status: str | None`
    :   Status of the draft order (`open`, `invoice_sent`, `completed`)

    `total_price: str | None`
    :   Total price of the draft order

    `updated_at: str | None`
    :   ISO 8601 timestamp when the draft order was last updated

<a id="FulfillmentOrdersSearchData"></a>

`FulfillmentOrdersSearchData(**data: Any)`
:   Search result data for fulfillment_orders entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assigned_location_id: int | None`
    :   Identifier of the location assigned to fulfill the order

    `created_at: str | None`
    :   ISO 8601 timestamp when the fulfillment order was created

    `id: int | None`
    :   Unique identifier for the fulfillment order

    `model_config`
    :   The type of the None singleton.

    `order_id: int | None`
    :   Identifier of the parent order

    `request_status: str | None`
    :   Status of the fulfillment request (e.g. `unsubmitted`, `submitted`)

    `shop_id: int | None`
    :   Identifier of the shop that owns the fulfillment order

    `status: str | None`
    :   Fulfillment order status (e.g. `open`, `in_progress`, `closed`)

    `updated_at: str | None`
    :   ISO 8601 timestamp when the fulfillment order was last updated

<a id="FulfillmentsSearchData"></a>

`FulfillmentsSearchData(**data: Any)`
:   Search result data for fulfillments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the fulfillment was created

    `id: int | None`
    :   Unique identifier for the fulfillment

    `location_id: int | None`
    :   Identifier of the fulfilling location

    `model_config`
    :   The type of the None singleton.

    `order_id: int | None`
    :   Identifier of the parent order

    `shipment_status: str | None`
    :   Carrier shipment status (e.g. `delivered`, `in_transit`)

    `status: str | None`
    :   Fulfillment status (e.g. `pending`, `open`, `success`, `cancelled`)

    `tracking_company: str | None`
    :   Name of the shipping carrier

    `tracking_number: str | None`
    :   Primary tracking number for the shipment

    `updated_at: str | None`
    :   ISO 8601 timestamp when the fulfillment was last updated

<a id="InventoryItemsSearchData"></a>

`InventoryItemsSearchData(**data: Any)`
:   Search result data for inventory_items entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `country_code_of_origin: str | None`
    :   ISO country code of the item's country of origin

    `created_at: str | None`
    :   ISO 8601 timestamp when the inventory item was created

    `id: int | None`
    :   Unique identifier for the inventory item

    `model_config`
    :   The type of the None singleton.

    `requires_shipping: bool | None`
    :   Whether the item requires shipping

    `sku: str | None`
    :   Stock keeping unit associated with the inventory item

    `tracked: bool | None`
    :   Whether Shopify is tracking inventory for this item

    `updated_at: str | None`
    :   ISO 8601 timestamp when the inventory item was last updated

<a id="InventoryLevelsSearchData"></a>

`InventoryLevelsSearchData(**data: Any)`
:   Search result data for inventory_levels entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `available: int | None`
    :   Number of units available at the location

    `inventory_item_id: int | None`
    :   Identifier of the inventory item

    `location_id: int | None`
    :   Identifier of the location holding the inventory

    `model_config`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   ISO 8601 timestamp when the inventory level was last updated

<a id="LocationsSearchData"></a>

`LocationsSearchData(**data: Any)`
:   Search result data for locations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | None`
    :   Whether the location is currently active

    `address1: str | None`
    :   Primary street address of the location

    `city: str | None`
    :   City of the location

    `country: str | None`
    :   Country name of the location

    `country_code: str | None`
    :   ISO 3166-1 alpha-2 country code of the location

    `created_at: str | None`
    :   ISO 8601 timestamp when the location was created

    `id: int | None`
    :   Unique identifier for the location

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Display name of the location

    `phone: str | None`
    :   Phone number for the location

    `province: str | None`
    :   Province, state, or region of the location

    `updated_at: str | None`
    :   ISO 8601 timestamp when the location was last updated

<a id="MetafieldCustomersSearchData"></a>

`MetafieldCustomersSearchData(**data: Any)`
:   Search result data for metafield_customers entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   Namespace group for the metafield

    `owner_id: int | None`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str | None`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str | None`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str | None`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str | None`
    :   Serialized value stored in the metafield

<a id="MetafieldDraftOrdersSearchData"></a>

`MetafieldDraftOrdersSearchData(**data: Any)`
:   Search result data for metafield_draft_orders entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   Namespace group for the metafield

    `owner_id: int | None`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str | None`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str | None`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str | None`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str | None`
    :   Serialized value stored in the metafield

<a id="MetafieldLocationsSearchData"></a>

`MetafieldLocationsSearchData(**data: Any)`
:   Search result data for metafield_locations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   Namespace group for the metafield

    `owner_id: int | None`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str | None`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str | None`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str | None`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str | None`
    :   Serialized value stored in the metafield

<a id="MetafieldOrdersSearchData"></a>

`MetafieldOrdersSearchData(**data: Any)`
:   Search result data for metafield_orders entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   Namespace group for the metafield

    `owner_id: int | None`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str | None`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str | None`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str | None`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str | None`
    :   Serialized value stored in the metafield

<a id="MetafieldProductImagesSearchData"></a>

`MetafieldProductImagesSearchData(**data: Any)`
:   Search result data for metafield_product_images entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   Namespace group for the metafield

    `owner_id: int | None`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str | None`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str | None`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str | None`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str | None`
    :   Serialized value stored in the metafield

<a id="MetafieldProductVariantsSearchData"></a>

`MetafieldProductVariantsSearchData(**data: Any)`
:   Search result data for metafield_product_variants entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   Namespace group for the metafield

    `owner_id: int | None`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str | None`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str | None`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str | None`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str | None`
    :   Serialized value stored in the metafield

<a id="MetafieldProductsSearchData"></a>

`MetafieldProductsSearchData(**data: Any)`
:   Search result data for metafield_products entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   Namespace group for the metafield

    `owner_id: int | None`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str | None`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str | None`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str | None`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str | None`
    :   Serialized value stored in the metafield

<a id="MetafieldShopsSearchData"></a>

`MetafieldShopsSearchData(**data: Any)`
:   Search result data for metafield_shops entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   Namespace group for the metafield

    `owner_id: int | None`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str | None`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str | None`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str | None`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str | None`
    :   Serialized value stored in the metafield

<a id="MetafieldSmartCollectionsSearchData"></a>

`MetafieldSmartCollectionsSearchData(**data: Any)`
:   Search result data for metafield_smart_collections entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   Namespace group for the metafield

    `owner_id: int | None`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str | None`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str | None`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str | None`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str | None`
    :   Serialized value stored in the metafield

<a id="OrderRefundsSearchData"></a>

`OrderRefundsSearchData(**data: Any)`
:   Search result data for order_refunds entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the refund was created

    `id: int | None`
    :   Unique identifier for the refund

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   Merchant-provided note explaining the refund

    `order_id: int | None`
    :   Identifier of the refunded order

    `processed_at: str | None`
    :   ISO 8601 timestamp when the refund was processed

    `user_id: int | None`
    :   Identifier of the staff user who processed the refund

<a id="PriceRulesSearchData"></a>

`PriceRulesSearchData(**data: Any)`
:   Search result data for price_rules entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allocation_method: str | None`
    :   How the discount is allocated (`each` or `across`)

    `created_at: str | None`
    :   ISO 8601 timestamp when the rule was created

    `ends_at: str | None`
    :   ISO 8601 timestamp when the rule stops being active, if applicable

    `id: int | None`
    :   Unique identifier for the price rule

    `model_config`
    :   The type of the None singleton.

    `starts_at: str | None`
    :   ISO 8601 timestamp when the rule starts being active

    `target_selection: str | None`
    :   Which target items the rule applies to (`all` or `entitled`)

    `target_type: str | None`
    :   Type of target the rule applies to (`line_item` or `shipping_line`)

    `title: str | None`
    :   Administrative title of the price rule

    `updated_at: str | None`
    :   ISO 8601 timestamp when the rule was last updated

    `value: str | None`
    :   Discount value applied by the rule

    `value_type: str | None`
    :   How the discount value is interpreted (`fixed_amount` or `percentage`)

<a id="ProductImagesSearchData"></a>

`ProductImagesSearchData(**data: Any)`
:   Search result data for product_images entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `alt: str | None`
    :   Alt text for the image

    `created_at: str | None`
    :   ISO 8601 timestamp when the image was created

    `height: int | None`
    :   Image height in pixels

    `id: int | None`
    :   Unique identifier for the product image

    `model_config`
    :   The type of the None singleton.

    `position: int | None`
    :   Display position of the image within the product

    `product_id: int | None`
    :   Identifier of the product the image belongs to

    `src: str | None`
    :   Public URL of the image

    `updated_at: str | None`
    :   ISO 8601 timestamp when the image was last updated

    `width: int | None`
    :   Image width in pixels

<a id="ProductVariantsSearchData"></a>

`ProductVariantsSearchData(**data: Any)`
:   Search result data for product_variants entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `compare_at_price: str | None`
    :   Original (compare-at) price of the variant, if set

    `created_at: str | None`
    :   ISO 8601 timestamp when the variant was created

    `id: int | None`
    :   Unique identifier for the product variant

    `inventory_policy: str | None`
    :   Behaviour when out of stock (`deny` or `continue`)

    `model_config`
    :   The type of the None singleton.

    `position: int | None`
    :   Display position of the variant within the product

    `price: str | None`
    :   Price of the variant in the shop's currency

    `product_id: int | None`
    :   Identifier of the parent product

    `sku: str | None`
    :   Stock keeping unit for the variant

    `title: str | None`
    :   Display title of the variant

    `updated_at: str | None`
    :   ISO 8601 timestamp when the variant was last updated

<a id="ShopSearchData"></a>

`ShopSearchData(**data: Any)`
:   Search result data for shop entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `country_code: str | None`
    :   ISO 3166-1 alpha-2 country code of the shop

    `created_at: str | None`
    :   ISO 8601 timestamp when the shop was created

    `currency: str | None`
    :   ISO 4217 currency code used by the shop

    `domain: str | None`
    :   Custom domain configured for the shop, if any

    `email: str | None`
    :   Primary contact email for the shop

    `id: int | None`
    :   Unique identifier for the shop

    `model_config`
    :   The type of the None singleton.

    `myshopify_domain: str | None`
    :   Canonical `*.myshopify.com` domain for the shop

    `name: str | None`
    :   Display name of the shop

    `plan_name: str | None`
    :   Shopify plan identifier (e.g. `shopify_plus`, `basic`)

    `timezone: str | None`
    :   Timezone configured for the shop (e.g. `(GMT-05:00) Eastern Time`)

    `updated_at: str | None`
    :   ISO 8601 timestamp when the shop was last updated

<a id="ShopifyAuthConfig"></a>

`ShopifyAuthConfig(**data: Any)`
:   Access Token Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Shopify Admin API access token

    `model_config`
    :   The type of the None singleton.

<a id="ShopifyConnector"></a>

`ShopifyConnector(auth_config: ShopifyAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, shop: str | None = None)`
:   Type-safe Shopify API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new shopify connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., ShopifyAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            shop: Your Shopify store name (e.g., 'my-store' from my-store.myshopify.com)
    Examples:
        # Local mode (direct API calls)
        connector = ShopifyConnector(auth_config=ShopifyAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = ShopifyConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = ShopifyConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'ShopifyAuthConfig'", name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> airbyte_agent_sdk.connectors.shopify.connector.ShopifyConnector`
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
            A ShopifyConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await ShopifyConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ShopifyAuthConfig(api_key="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000, framework: FrameworkName | None = None, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Composes :func:`airbyte_agent_sdk.translation.translate_exceptions` for
        runtime wrapping (sync/async branch + output-size check + framework
        signal translation + optional internal retry loop), and adds
        connector-specific docstring augmentation on top of it.
        
        Usage:
            @mcp.tool()
            @ShopifyConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ShopifyConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ShopifyConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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
        
        Example:
            connector = await ShopifyConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            ShopifyCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="SmartCollectionsSearchData"></a>

`SmartCollectionsSearchData(**data: Any)`
:   Search result data for smart_collections entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `handle: str | None`
    :   URL-friendly handle for the smart collection

    `id: int | None`
    :   Unique identifier for the smart collection

    `model_config`
    :   The type of the None singleton.

    `published_at: str | None`
    :   ISO 8601 timestamp when the collection was published

    `published_scope: str | None`
    :   Publishing scope (`web` or `global`)

    `sort_order: str | None`
    :   How products are sorted within the collection

    `title: str | None`
    :   Display title of the smart collection

    `updated_at: str | None`
    :   ISO 8601 timestamp when the collection was last updated

<a id="TenderTransactionsSearchData"></a>

`TenderTransactionsSearchData(**data: Any)`
:   Search result data for tender_transactions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   Amount of the transaction in the shop's currency

    `currency: str | None`
    :   ISO 4217 currency code for the transaction amount

    `id: int | None`
    :   Unique identifier for the tender transaction

    `model_config`
    :   The type of the None singleton.

    `order_id: int | None`
    :   Identifier of the order the transaction belongs to

    `payment_method: str | None`
    :   Payment method used (e.g. `credit_card`, `paypal`)

    `processed_at: str | None`
    :   ISO 8601 timestamp when the transaction was processed

    `test: bool | None`
    :   Whether the transaction was a test transaction

    `user_id: int | None`
    :   Identifier of the staff user who processed the transaction