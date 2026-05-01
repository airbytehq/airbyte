---
id: airbyte_agent_sdk-connectors-shopify-models
title: airbyte_agent_sdk.connectors.shopify.models
---

Module airbyte_agent_sdk.connectors.shopify.models
==================================================
Pydantic models for shopify connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="AbandonedCheckout"></a>

`AbandonedCheckout(**data: Any)`
:   An abandoned checkout
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `abandoned_checkout_url: str | None`
    :   The type of the None singleton.

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `billing_address: typing.Any | None`
    :   The type of the None singleton.

    `buyer_accepts_marketing: bool | None`
    :   The type of the None singleton.

    `buyer_accepts_sms_marketing: bool | None`
    :   The type of the None singleton.

    `cart_token: str | None`
    :   The type of the None singleton.

    `closed_at: str | None`
    :   The type of the None singleton.

    `completed_at: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `currency: str | None`
    :   The type of the None singleton.

    `customer: typing.Any | None`
    :   The type of the None singleton.

    `customer_locale: str | None`
    :   The type of the None singleton.

    `device_id: int | None`
    :   The type of the None singleton.

    `discount_codes: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `gateway: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `landing_site: str | None`
    :   The type of the None singleton.

    `line_items: list[airbyte_agent_sdk.connectors.shopify.models.LineItem] | None`
    :   The type of the None singleton.

    `location_id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `note: str | None`
    :   The type of the None singleton.

    `note_attributes: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `phone: str | None`
    :   The type of the None singleton.

    `presentment_currency: str | None`
    :   The type of the None singleton.

    `referring_site: str | None`
    :   The type of the None singleton.

    `shipping_address: typing.Any | None`
    :   The type of the None singleton.

    `shipping_lines: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `sms_marketing_phone: str | None`
    :   The type of the None singleton.

    `source: str | None`
    :   The type of the None singleton.

    `source_identifier: str | None`
    :   The type of the None singleton.

    `source_name: str | None`
    :   The type of the None singleton.

    `source_url: str | None`
    :   The type of the None singleton.

    `subtotal_price: str | None`
    :   The type of the None singleton.

    `tax_lines: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `taxes_included: bool | None`
    :   The type of the None singleton.

    `token: str | None`
    :   The type of the None singleton.

    `total_discounts: str | None`
    :   The type of the None singleton.

    `total_duties: str | None`
    :   The type of the None singleton.

    `total_line_items_price: str | None`
    :   The type of the None singleton.

    `total_price: str | None`
    :   The type of the None singleton.

    `total_tax: str | None`
    :   The type of the None singleton.

    `total_weight: int | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `user_id: int | None`
    :   The type of the None singleton.

<a id="AbandonedCheckoutList"></a>

`AbandonedCheckoutList(**data: Any)`
:   AbandonedCheckoutList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checkouts: list[airbyte_agent_sdk.connectors.shopify.models.AbandonedCheckout] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsListResultMeta"></a>

`AbandonedCheckoutsListResultMeta(**data: Any)`
:   Metadata for abandoned_checkouts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

`AirbyteSearchResult[AbandonedCheckoutsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

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

`AirbyteSearchResult[CollectsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[CountriesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[CustomCollectionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[CustomersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[DiscountCodesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[DraftOrdersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[FulfillmentOrdersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[FulfillmentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[InventoryItemsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[InventoryLevelsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[LocationsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[MetafieldCustomersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[MetafieldDraftOrdersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[MetafieldLocationsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[MetafieldOrdersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[MetafieldProductImagesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[MetafieldProductVariantsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[MetafieldProductsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[MetafieldShopsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[MetafieldSmartCollectionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[OrderRefundsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[PriceRulesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[ProductImagesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[ProductVariantsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[ShopSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[SmartCollectionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[TenderTransactionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

<a id="Collect"></a>

`Collect(**data: Any)`
:   A collect (product-collection link)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `collection_id: int | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `position: int | None`
    :   The type of the None singleton.

    `product_id: int | None`
    :   The type of the None singleton.

    `sort_value: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="CollectList"></a>

`CollectList(**data: Any)`
:   CollectList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `collects: list[airbyte_agent_sdk.connectors.shopify.models.Collect] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CollectsListResultMeta"></a>

`CollectsListResultMeta(**data: Any)`
:   Metadata for collects.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="CountriesListResultMeta"></a>

`CountriesListResultMeta(**data: Any)`
:   Metadata for countries.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="Country"></a>

`Country(**data: Any)`
:   A country
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `provinces: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `tax: float | None`
    :   The type of the None singleton.

    `tax_name: str | None`
    :   The type of the None singleton.

<a id="CountryList"></a>

`CountryList(**data: Any)`
:   CountryList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `countries: list[airbyte_agent_sdk.connectors.shopify.models.Country] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomCollection"></a>

`CustomCollection(**data: Any)`
:   A custom collection
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `body_html: str | None`
    :   The type of the None singleton.

    `handle: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `image: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `products_count: int | None`
    :   The type of the None singleton.

    `published_at: str | None`
    :   The type of the None singleton.

    `published_scope: str | None`
    :   The type of the None singleton.

    `sort_order: str | None`
    :   The type of the None singleton.

    `template_suffix: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="CustomCollectionList"></a>

`CustomCollectionList(**data: Any)`
:   CustomCollectionList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `custom_collections: list[airbyte_agent_sdk.connectors.shopify.models.CustomCollection] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomCollectionsListResultMeta"></a>

`CustomCollectionsListResultMeta(**data: Any)`
:   Metadata for custom_collections.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="Customer"></a>

`Customer(**data: Any)`
:   A Shopify customer
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accepts_marketing: bool | None`
    :   The type of the None singleton.

    `accepts_marketing_updated_at: str | None`
    :   The type of the None singleton.

    `addresses: list[airbyte_agent_sdk.connectors.shopify.models.CustomerAddress] | None`
    :   The type of the None singleton.

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `currency: str | None`
    :   The type of the None singleton.

    `default_address: typing.Any | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `email_marketing_consent: typing.Any | None`
    :   The type of the None singleton.

    `first_name: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `last_name: str | None`
    :   The type of the None singleton.

    `last_order_id: int | None`
    :   The type of the None singleton.

    `last_order_name: str | None`
    :   The type of the None singleton.

    `marketing_opt_in_level: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `multipass_identifier: str | None`
    :   The type of the None singleton.

    `note: str | None`
    :   The type of the None singleton.

    `orders_count: int | None`
    :   The type of the None singleton.

    `phone: str | None`
    :   The type of the None singleton.

    `sms_marketing_consent: typing.Any | None`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

    `tags: str | None`
    :   The type of the None singleton.

    `tax_exempt: bool | None`
    :   The type of the None singleton.

    `tax_exemptions: list[str] | None`
    :   The type of the None singleton.

    `total_spent: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `verified_email: bool | None`
    :   The type of the None singleton.

<a id="CustomerAddress"></a>

`CustomerAddress(**data: Any)`
:   A customer address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address1: str | None`
    :   The type of the None singleton.

    `address2: str | None`
    :   The type of the None singleton.

    `city: str | None`
    :   The type of the None singleton.

    `company: str | None`
    :   The type of the None singleton.

    `country: str | None`
    :   The type of the None singleton.

    `country_code: str | None`
    :   The type of the None singleton.

    `country_name: str | None`
    :   The type of the None singleton.

    `customer_id: int | None`
    :   The type of the None singleton.

    `default: bool | None`
    :   The type of the None singleton.

    `first_name: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `last_name: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `phone: str | None`
    :   The type of the None singleton.

    `province: str | None`
    :   The type of the None singleton.

    `province_code: str | None`
    :   The type of the None singleton.

    `zip: str | None`
    :   The type of the None singleton.

<a id="CustomerAddressList"></a>

`CustomerAddressList(**data: Any)`
:   CustomerAddressList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `addresses: list[airbyte_agent_sdk.connectors.shopify.models.CustomerAddress] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomerAddressListResultMeta"></a>

`CustomerAddressListResultMeta(**data: Any)`
:   Metadata for customer_address.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

<a id="CustomerList"></a>

`CustomerList(**data: Any)`
:   CustomerList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `customers: list[airbyte_agent_sdk.connectors.shopify.models.Customer] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomersListResultMeta"></a>

`CustomersListResultMeta(**data: Any)`
:   Metadata for customers.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="DiscountCode"></a>

`DiscountCode(**data: Any)`
:   A discount code
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `price_rule_id: int | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `usage_count: int | None`
    :   The type of the None singleton.

<a id="DiscountCodeList"></a>

`DiscountCodeList(**data: Any)`
:   DiscountCodeList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `discount_codes: list[airbyte_agent_sdk.connectors.shopify.models.DiscountCode] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodesListResultMeta"></a>

`DiscountCodesListResultMeta(**data: Any)`
:   Metadata for discount_codes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="DraftOrder"></a>

`DraftOrder(**data: Any)`
:   A draft order
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `allow_discount_codes_in_checkout: bool | None`
    :   The type of the None singleton.

    `api_client_id: int | None`
    :   The type of the None singleton.

    `applied_discount: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `b2b: bool | None`
    :   The type of the None singleton.

    `billing_address: typing.Any | None`
    :   The type of the None singleton.

    `completed_at: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `created_on_api_version_handle: str | None`
    :   The type of the None singleton.

    `currency: str | None`
    :   The type of the None singleton.

    `customer: typing.Any | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `invoice_sent_at: str | None`
    :   The type of the None singleton.

    `invoice_url: str | None`
    :   The type of the None singleton.

    `line_items: list[airbyte_agent_sdk.connectors.shopify.models.LineItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `note: str | None`
    :   The type of the None singleton.

    `note_attributes: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `order_id: int | None`
    :   The type of the None singleton.

    `payment_terms: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `shipping_address: typing.Any | None`
    :   The type of the None singleton.

    `shipping_line: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `subtotal_price: str | None`
    :   The type of the None singleton.

    `tags: str | None`
    :   The type of the None singleton.

    `tax_exempt: bool | None`
    :   The type of the None singleton.

    `tax_lines: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `taxes_included: bool | None`
    :   The type of the None singleton.

    `total_price: str | None`
    :   The type of the None singleton.

    `total_tax: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="DraftOrderList"></a>

`DraftOrderList(**data: Any)`
:   DraftOrderList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `draft_orders: list[airbyte_agent_sdk.connectors.shopify.models.DraftOrder] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DraftOrdersListResultMeta"></a>

`DraftOrdersListResultMeta(**data: Any)`
:   Metadata for draft_orders.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="Fulfillment"></a>

`Fulfillment(**data: Any)`
:   A fulfillment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `line_items: list[airbyte_agent_sdk.connectors.shopify.models.LineItem] | None`
    :   The type of the None singleton.

    `location_id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `order_id: int | None`
    :   The type of the None singleton.

    `origin_address: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `receipt: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `service: str | None`
    :   The type of the None singleton.

    `shipment_status: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `tracking_company: str | None`
    :   The type of the None singleton.

    `tracking_number: str | None`
    :   The type of the None singleton.

    `tracking_numbers: list[str] | None`
    :   The type of the None singleton.

    `tracking_url: str | None`
    :   The type of the None singleton.

    `tracking_urls: list[str] | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="FulfillmentList"></a>

`FulfillmentList(**data: Any)`
:   FulfillmentList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `fulfillments: list[airbyte_agent_sdk.connectors.shopify.models.Fulfillment] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FulfillmentOrder"></a>

`FulfillmentOrder(**data: Any)`
:   A fulfillment order
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assigned_location: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `assigned_location_id: int | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `delivery_method: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `destination: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `fulfill_at: str | None`
    :   The type of the None singleton.

    `fulfill_by: str | None`
    :   The type of the None singleton.

    `fulfillment_holds: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `international_duties: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `line_items: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `merchant_requests: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `order_id: int | None`
    :   The type of the None singleton.

    `request_status: str | None`
    :   The type of the None singleton.

    `shop_id: int | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `supported_actions: list[str] | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="FulfillmentOrderList"></a>

`FulfillmentOrderList(**data: Any)`
:   FulfillmentOrderList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `fulfillment_orders: list[airbyte_agent_sdk.connectors.shopify.models.FulfillmentOrder] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FulfillmentOrdersListResultMeta"></a>

`FulfillmentOrdersListResultMeta(**data: Any)`
:   Metadata for fulfillment_orders.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="FulfillmentsListResultMeta"></a>

`FulfillmentsListResultMeta(**data: Any)`
:   Metadata for fulfillments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="InventoryItem"></a>

`InventoryItem(**data: Any)`
:   An inventory item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `cost: str | None`
    :   The type of the None singleton.

    `country_code_of_origin: str | None`
    :   The type of the None singleton.

    `country_harmonized_system_codes: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `harmonized_system_code: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `province_code_of_origin: str | None`
    :   The type of the None singleton.

    `requires_shipping: bool | None`
    :   The type of the None singleton.

    `sku: str | None`
    :   The type of the None singleton.

    `tracked: bool | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="InventoryItemList"></a>

`InventoryItemList(**data: Any)`
:   InventoryItemList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `inventory_items: list[airbyte_agent_sdk.connectors.shopify.models.InventoryItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InventoryItemsListResultMeta"></a>

`InventoryItemsListResultMeta(**data: Any)`
:   Metadata for inventory_items.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="InventoryLevel"></a>

`InventoryLevel(**data: Any)`
:   An inventory level
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `available: int | None`
    :   The type of the None singleton.

    `inventory_item_id: int | None`
    :   The type of the None singleton.

    `location_id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="InventoryLevelList"></a>

`InventoryLevelList(**data: Any)`
:   InventoryLevelList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `inventory_levels: list[airbyte_agent_sdk.connectors.shopify.models.InventoryLevel] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InventoryLevelsListResultMeta"></a>

`InventoryLevelsListResultMeta(**data: Any)`
:   Metadata for inventory_levels.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="LineItem"></a>

`LineItem(**data: Any)`
:   LineItem type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `attributed_staffs: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `current_quantity: int | None`
    :   The type of the None singleton.

    `discount_allocations: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `duties: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `fulfillable_quantity: int | None`
    :   The type of the None singleton.

    `fulfillment_service: str | None`
    :   The type of the None singleton.

    `fulfillment_status: str | None`
    :   The type of the None singleton.

    `gift_card: bool | None`
    :   The type of the None singleton.

    `grams: int | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `price: str | None`
    :   The type of the None singleton.

    `price_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `product_exists: bool | None`
    :   The type of the None singleton.

    `product_id: int | None`
    :   The type of the None singleton.

    `properties: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `quantity: int | None`
    :   The type of the None singleton.

    `requires_shipping: bool | None`
    :   The type of the None singleton.

    `sku: str | None`
    :   The type of the None singleton.

    `tax_lines: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `taxable: bool | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `total_discount: str | None`
    :   The type of the None singleton.

    `total_discount_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `variant_id: int | None`
    :   The type of the None singleton.

    `variant_inventory_management: str | None`
    :   The type of the None singleton.

    `variant_title: str | None`
    :   The type of the None singleton.

    `vendor: str | None`
    :   The type of the None singleton.

<a id="Location"></a>

`Location(**data: Any)`
:   A store location
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | None`
    :   The type of the None singleton.

    `address1: str | None`
    :   The type of the None singleton.

    `address2: str | None`
    :   The type of the None singleton.

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `city: str | None`
    :   The type of the None singleton.

    `country: str | None`
    :   The type of the None singleton.

    `country_code: str | None`
    :   The type of the None singleton.

    `country_name: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `legacy: bool | None`
    :   The type of the None singleton.

    `localized_country_name: str | None`
    :   The type of the None singleton.

    `localized_province_name: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `phone: str | None`
    :   The type of the None singleton.

    `province: str | None`
    :   The type of the None singleton.

    `province_code: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `zip: str | None`
    :   The type of the None singleton.

<a id="LocationList"></a>

`LocationList(**data: Any)`
:   LocationList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `locations: list[airbyte_agent_sdk.connectors.shopify.models.Location] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="LocationsListResultMeta"></a>

`LocationsListResultMeta(**data: Any)`
:   Metadata for locations.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="MarketingConsent"></a>

`MarketingConsent(**data: Any)`
:   MarketingConsent type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `consent_collected_from: str | None`
    :   The type of the None singleton.

    `consent_updated_at: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `opt_in_level: str | None`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

<a id="Metafield"></a>

`Metafield(**data: Any)`
:   A metafield
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `key: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   The type of the None singleton.

    `owner_id: int | None`
    :   The type of the None singleton.

    `owner_resource: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `value: typing.Any | None`
    :   The type of the None singleton.

<a id="MetafieldCustomersListResultMeta"></a>

`MetafieldCustomersListResultMeta(**data: Any)`
:   Metadata for metafield_customers.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="MetafieldDraftOrdersListResultMeta"></a>

`MetafieldDraftOrdersListResultMeta(**data: Any)`
:   Metadata for metafield_draft_orders.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="MetafieldList"></a>

`MetafieldList(**data: Any)`
:   MetafieldList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metafields: list[airbyte_agent_sdk.connectors.shopify.models.Metafield] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="MetafieldLocationsListResultMeta"></a>

`MetafieldLocationsListResultMeta(**data: Any)`
:   Metadata for metafield_locations.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="MetafieldOrdersListResultMeta"></a>

`MetafieldOrdersListResultMeta(**data: Any)`
:   Metadata for metafield_orders.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="MetafieldProductImagesListResultMeta"></a>

`MetafieldProductImagesListResultMeta(**data: Any)`
:   Metadata for metafield_product_images.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="MetafieldProductVariantsListResultMeta"></a>

`MetafieldProductVariantsListResultMeta(**data: Any)`
:   Metadata for metafield_product_variants.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="MetafieldProductsListResultMeta"></a>

`MetafieldProductsListResultMeta(**data: Any)`
:   Metadata for metafield_products.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="MetafieldShopsListResultMeta"></a>

`MetafieldShopsListResultMeta(**data: Any)`
:   Metadata for metafield_shops.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="MetafieldSmartCollectionsListResultMeta"></a>

`MetafieldSmartCollectionsListResultMeta(**data: Any)`
:   Metadata for metafield_smart_collections.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="Order"></a>

`Order(**data: Any)`
:   A Shopify order
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `app_id: int | None`
    :   The type of the None singleton.

    `billing_address: typing.Any | None`
    :   The type of the None singleton.

    `browser_ip: str | None`
    :   The type of the None singleton.

    `buyer_accepts_marketing: bool | None`
    :   The type of the None singleton.

    `cancel_reason: str | None`
    :   The type of the None singleton.

    `cancelled_at: str | None`
    :   The type of the None singleton.

    `cart_token: str | None`
    :   The type of the None singleton.

    `checkout_id: int | None`
    :   The type of the None singleton.

    `checkout_token: str | None`
    :   The type of the None singleton.

    `client_details: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `closed_at: str | None`
    :   The type of the None singleton.

    `company: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `confirmation_number: str | None`
    :   The type of the None singleton.

    `confirmed: bool | None`
    :   The type of the None singleton.

    `contact_email: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `currency: str | None`
    :   The type of the None singleton.

    `current_subtotal_price: str | None`
    :   The type of the None singleton.

    `current_subtotal_price_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `current_total_additional_fees_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `current_total_discounts: str | None`
    :   The type of the None singleton.

    `current_total_discounts_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `current_total_duties_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `current_total_price: str | None`
    :   The type of the None singleton.

    `current_total_price_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `current_total_tax: str | None`
    :   The type of the None singleton.

    `current_total_tax_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `customer: typing.Any | None`
    :   The type of the None singleton.

    `customer_locale: str | None`
    :   The type of the None singleton.

    `device_id: int | None`
    :   The type of the None singleton.

    `discount_applications: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `discount_codes: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `duties_included: bool | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `estimated_taxes: bool | None`
    :   The type of the None singleton.

    `financial_status: str | None`
    :   The type of the None singleton.

    `fulfillment_status: str | None`
    :   The type of the None singleton.

    `fulfillments: list[airbyte_agent_sdk.connectors.shopify.models.Fulfillment] | None`
    :   The type of the None singleton.

    `gateway: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `landing_site: str | None`
    :   The type of the None singleton.

    `landing_site_ref: str | None`
    :   The type of the None singleton.

    `line_items: list[airbyte_agent_sdk.connectors.shopify.models.LineItem] | None`
    :   The type of the None singleton.

    `location_id: int | None`
    :   The type of the None singleton.

    `merchant_business_entity_id: str | None`
    :   The type of the None singleton.

    `merchant_of_record_app_id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `note: str | None`
    :   The type of the None singleton.

    `note_attributes: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `number: int | None`
    :   The type of the None singleton.

    `order_number: int | None`
    :   The type of the None singleton.

    `order_status_url: str | None`
    :   The type of the None singleton.

    `original_total_additional_fees_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `original_total_duties_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `payment_gateway_names: list[str] | None`
    :   The type of the None singleton.

    `payment_terms: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `phone: str | None`
    :   The type of the None singleton.

    `po_number: str | None`
    :   The type of the None singleton.

    `presentment_currency: str | None`
    :   The type of the None singleton.

    `processed_at: str | None`
    :   The type of the None singleton.

    `reference: str | None`
    :   The type of the None singleton.

    `referring_site: str | None`
    :   The type of the None singleton.

    `refunds: list[airbyte_agent_sdk.connectors.shopify.models.Refund] | None`
    :   The type of the None singleton.

    `shipping_address: typing.Any | None`
    :   The type of the None singleton.

    `shipping_lines: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `source_identifier: str | None`
    :   The type of the None singleton.

    `source_name: str | None`
    :   The type of the None singleton.

    `source_url: str | None`
    :   The type of the None singleton.

    `subtotal_price: str | None`
    :   The type of the None singleton.

    `subtotal_price_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `tags: str | None`
    :   The type of the None singleton.

    `tax_exempt: bool | None`
    :   The type of the None singleton.

    `tax_lines: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `taxes_included: bool | None`
    :   The type of the None singleton.

    `test: bool | None`
    :   The type of the None singleton.

    `token: str | None`
    :   The type of the None singleton.

    `total_cash_rounding_payment_adjustment_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `total_cash_rounding_refund_adjustment_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `total_discounts: str | None`
    :   The type of the None singleton.

    `total_discounts_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `total_line_items_price: str | None`
    :   The type of the None singleton.

    `total_line_items_price_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `total_outstanding: str | None`
    :   The type of the None singleton.

    `total_price: str | None`
    :   The type of the None singleton.

    `total_price_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `total_shipping_price_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `total_tax: str | None`
    :   The type of the None singleton.

    `total_tax_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `total_tip_received: str | None`
    :   The type of the None singleton.

    `total_weight: int | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `user_id: int | None`
    :   The type of the None singleton.

<a id="OrderAddress"></a>

`OrderAddress(**data: Any)`
:   An address in an order (shipping or billing) - does not have id field
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address1: str | None`
    :   The type of the None singleton.

    `address2: str | None`
    :   The type of the None singleton.

    `city: str | None`
    :   The type of the None singleton.

    `company: str | None`
    :   The type of the None singleton.

    `country: str | None`
    :   The type of the None singleton.

    `country_code: str | None`
    :   The type of the None singleton.

    `first_name: str | None`
    :   The type of the None singleton.

    `last_name: str | None`
    :   The type of the None singleton.

    `latitude: float | None`
    :   The type of the None singleton.

    `longitude: float | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `phone: str | None`
    :   The type of the None singleton.

    `province: str | None`
    :   The type of the None singleton.

    `province_code: str | None`
    :   The type of the None singleton.

    `zip: str | None`
    :   The type of the None singleton.

<a id="OrderList"></a>

`OrderList(**data: Any)`
:   OrderList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `orders: list[airbyte_agent_sdk.connectors.shopify.models.Order] | None`
    :   The type of the None singleton.

<a id="OrderRefundsListResultMeta"></a>

`OrderRefundsListResultMeta(**data: Any)`
:   Metadata for order_refunds.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="OrdersListResultMeta"></a>

`OrdersListResultMeta(**data: Any)`
:   Metadata for orders.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

<a id="PriceRule"></a>

`PriceRule(**data: Any)`
:   A price rule
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `allocation_limit: int | None`
    :   The type of the None singleton.

    `allocation_method: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `customer_segment_prerequisite_ids: list[int] | None`
    :   The type of the None singleton.

    `customer_selection: str | None`
    :   The type of the None singleton.

    `ends_at: str | None`
    :   The type of the None singleton.

    `entitled_collection_ids: list[int] | None`
    :   The type of the None singleton.

    `entitled_country_ids: list[int] | None`
    :   The type of the None singleton.

    `entitled_product_ids: list[int] | None`
    :   The type of the None singleton.

    `entitled_variant_ids: list[int] | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `once_per_customer: bool | None`
    :   The type of the None singleton.

    `prerequisite_collection_ids: list[int] | None`
    :   The type of the None singleton.

    `prerequisite_customer_ids: list[int] | None`
    :   The type of the None singleton.

    `prerequisite_product_ids: list[int] | None`
    :   The type of the None singleton.

    `prerequisite_quantity_range: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `prerequisite_shipping_price_range: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `prerequisite_subtotal_range: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `prerequisite_to_entitlement_purchase: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `prerequisite_to_entitlement_quantity_ratio: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `prerequisite_variant_ids: list[int] | None`
    :   The type of the None singleton.

    `starts_at: str | None`
    :   The type of the None singleton.

    `target_selection: str | None`
    :   The type of the None singleton.

    `target_type: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `usage_limit: int | None`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

    `value_type: str | None`
    :   The type of the None singleton.

<a id="PriceRuleList"></a>

`PriceRuleList(**data: Any)`
:   PriceRuleList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `price_rules: list[airbyte_agent_sdk.connectors.shopify.models.PriceRule] | None`
    :   The type of the None singleton.

<a id="PriceRulesListResultMeta"></a>

`PriceRulesListResultMeta(**data: Any)`
:   Metadata for price_rules.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="Product"></a>

`Product(**data: Any)`
:   A Shopify product
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `body_html: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `handle: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `image: typing.Any | None`
    :   The type of the None singleton.

    `images: list[airbyte_agent_sdk.connectors.shopify.models.ProductImage] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `options: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `product_type: str | None`
    :   The type of the None singleton.

    `published_at: str | None`
    :   The type of the None singleton.

    `published_scope: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `tags: str | None`
    :   The type of the None singleton.

    `template_suffix: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `variants: list[airbyte_agent_sdk.connectors.shopify.models.ProductVariant] | None`
    :   The type of the None singleton.

    `vendor: str | None`
    :   The type of the None singleton.

<a id="ProductImage"></a>

`ProductImage(**data: Any)`
:   A product image
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `alt: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `height: int | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `position: int | None`
    :   The type of the None singleton.

    `product_id: int | None`
    :   The type of the None singleton.

    `src: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `variant_ids: list[int] | None`
    :   The type of the None singleton.

    `width: int | None`
    :   The type of the None singleton.

<a id="ProductImageList"></a>

`ProductImageList(**data: Any)`
:   ProductImageList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `images: list[airbyte_agent_sdk.connectors.shopify.models.ProductImage] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProductImagesListResultMeta"></a>

`ProductImagesListResultMeta(**data: Any)`
:   Metadata for product_images.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="ProductList"></a>

`ProductList(**data: Any)`
:   ProductList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `products: list[airbyte_agent_sdk.connectors.shopify.models.Product] | None`
    :   The type of the None singleton.

<a id="ProductVariant"></a>

`ProductVariant(**data: Any)`
:   A product variant
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `barcode: str | None`
    :   The type of the None singleton.

    `compare_at_price: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `fulfillment_service: str | None`
    :   The type of the None singleton.

    `grams: int | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `image_id: int | None`
    :   The type of the None singleton.

    `inventory_item_id: int | None`
    :   The type of the None singleton.

    `inventory_management: str | None`
    :   The type of the None singleton.

    `inventory_policy: str | None`
    :   The type of the None singleton.

    `inventory_quantity: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `old_inventory_quantity: int | None`
    :   The type of the None singleton.

    `option1: str | None`
    :   The type of the None singleton.

    `option2: str | None`
    :   The type of the None singleton.

    `option3: str | None`
    :   The type of the None singleton.

    `position: int | None`
    :   The type of the None singleton.

    `price: str | None`
    :   The type of the None singleton.

    `product_id: int | None`
    :   The type of the None singleton.

    `requires_shipping: bool | None`
    :   The type of the None singleton.

    `sku: str | None`
    :   The type of the None singleton.

    `taxable: bool | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `weight: float | None`
    :   The type of the None singleton.

    `weight_unit: str | None`
    :   The type of the None singleton.

<a id="ProductVariantList"></a>

`ProductVariantList(**data: Any)`
:   ProductVariantList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `variants: list[airbyte_agent_sdk.connectors.shopify.models.ProductVariant] | None`
    :   The type of the None singleton.

<a id="ProductVariantsListResultMeta"></a>

`ProductVariantsListResultMeta(**data: Any)`
:   Metadata for product_variants.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="ProductsListResultMeta"></a>

`ProductsListResultMeta(**data: Any)`
:   Metadata for products.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

<a id="Refund"></a>

`Refund(**data: Any)`
:   An order refund
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `duties: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   The type of the None singleton.

    `order_adjustments: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `order_id: int | None`
    :   The type of the None singleton.

    `processed_at: str | None`
    :   The type of the None singleton.

    `refund_line_items: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `refund_shipping_lines: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `restock: bool | None`
    :   The type of the None singleton.

    `return_: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `total_duties_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `transactions: list[airbyte_agent_sdk.connectors.shopify.models.Transaction] | None`
    :   The type of the None singleton.

    `user_id: int | None`
    :   The type of the None singleton.

<a id="RefundList"></a>

`RefundList(**data: Any)`
:   RefundList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `refunds: list[airbyte_agent_sdk.connectors.shopify.models.Refund] | None`
    :   The type of the None singleton.

<a id="Shop"></a>

`Shop(**data: Any)`
:   Shop configuration
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address1: str | None`
    :   The type of the None singleton.

    `address2: str | None`
    :   The type of the None singleton.

    `auto_configure_tax_inclusivity: bool | None`
    :   The type of the None singleton.

    `checkout_api_supported: bool | None`
    :   The type of the None singleton.

    `city: str | None`
    :   The type of the None singleton.

    `country: str | None`
    :   The type of the None singleton.

    `country_code: str | None`
    :   The type of the None singleton.

    `country_name: str | None`
    :   The type of the None singleton.

    `county_taxes: bool | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `currency: str | None`
    :   The type of the None singleton.

    `customer_email: str | None`
    :   The type of the None singleton.

    `domain: str | None`
    :   The type of the None singleton.

    `eligible_for_payments: bool | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `enabled_presentment_currencies: list[str] | None`
    :   The type of the None singleton.

    `finances: bool | None`
    :   The type of the None singleton.

    `google_apps_domain: str | None`
    :   The type of the None singleton.

    `google_apps_login_enabled: bool | None`
    :   The type of the None singleton.

    `has_discounts: bool | None`
    :   The type of the None singleton.

    `has_gift_cards: bool | None`
    :   The type of the None singleton.

    `has_storefront: bool | None`
    :   The type of the None singleton.

    `iana_timezone: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `latitude: float | None`
    :   The type of the None singleton.

    `longitude: float | None`
    :   The type of the None singleton.

    `marketing_sms_consent_enabled_at_checkout: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `money_format: str | None`
    :   The type of the None singleton.

    `money_in_emails_format: str | None`
    :   The type of the None singleton.

    `money_with_currency_format: str | None`
    :   The type of the None singleton.

    `money_with_currency_in_emails_format: str | None`
    :   The type of the None singleton.

    `multi_location_enabled: bool | None`
    :   The type of the None singleton.

    `myshopify_domain: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `password_enabled: bool | None`
    :   The type of the None singleton.

    `phone: str | None`
    :   The type of the None singleton.

    `plan_display_name: str | None`
    :   The type of the None singleton.

    `plan_name: str | None`
    :   The type of the None singleton.

    `pre_launch_enabled: bool | None`
    :   The type of the None singleton.

    `primary_locale: str | None`
    :   The type of the None singleton.

    `primary_location_id: int | None`
    :   The type of the None singleton.

    `province: str | None`
    :   The type of the None singleton.

    `province_code: str | None`
    :   The type of the None singleton.

    `requires_extra_payments_agreement: bool | None`
    :   The type of the None singleton.

    `setup_required: bool | None`
    :   The type of the None singleton.

    `shop_owner: str | None`
    :   The type of the None singleton.

    `source: str | None`
    :   The type of the None singleton.

    `tax_shipping: bool | None`
    :   The type of the None singleton.

    `taxes_included: bool | None`
    :   The type of the None singleton.

    `timezone: str | None`
    :   The type of the None singleton.

    `transactional_sms_disabled: bool | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `weight_unit: str | None`
    :   The type of the None singleton.

    `zip: str | None`
    :   The type of the None singleton.

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

<a id="ShopifyCheckResult"></a>

`ShopifyCheckResult(**data: Any)`
:   Result of a health check operation.
    
    Returned by the check() method to indicate connectivity and credential status.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checked_action: str | None`
    :   Action name used for the health check.

    `checked_entity: str | None`
    :   Entity name used for the health check.

    `error: str | None`
    :   Error message if status is 'unhealthy', None otherwise.

    `model_config`
    :   The type of the None singleton.

    `status: str`
    :   Health check status: 'healthy' or 'unhealthy'.

<a id="ShopifyExecuteResult"></a>

`ShopifyExecuteResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="ShopifyExecuteResultWithMeta"></a>

`ShopifyExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[AbandonedCheckout], AbandonedCheckoutsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Collect], CollectsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Country], CountriesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[CustomCollection], CustomCollectionsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[CustomerAddress], CustomerAddressListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Customer], CustomersListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[DiscountCode], DiscountCodesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[DraftOrder], DraftOrdersListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[FulfillmentOrder], FulfillmentOrdersListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Fulfillment], FulfillmentsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[InventoryItem], InventoryItemsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[InventoryLevel], InventoryLevelsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Location], LocationsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldCustomersListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldDraftOrdersListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldLocationsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldOrdersListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldProductImagesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldProductVariantsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldProductsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldShopsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldSmartCollectionsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Order], OrdersListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[PriceRule], PriceRulesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[ProductImage], ProductImagesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[ProductVariant], ProductVariantsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Product], ProductsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Refund], OrderRefundsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[SmartCollection], SmartCollectionsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[TenderTransaction], TenderTransactionsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Transaction], TransactionsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`ShopifyExecuteResultWithMeta[list[AbandonedCheckout], AbandonedCheckoutsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsListResult"></a>

`AbandonedCheckoutsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Collect], CollectsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CollectsListResult"></a>

`CollectsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Country], CountriesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CountriesListResult"></a>

`CountriesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[CustomCollection], CustomCollectionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomCollectionsListResult"></a>

`CustomCollectionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[CustomerAddress], CustomerAddressListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomerAddressListResult"></a>

`CustomerAddressListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Customer], CustomersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomersListResult"></a>

`CustomersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[DiscountCode], DiscountCodesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodesListResult"></a>

`DiscountCodesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[DraftOrder], DraftOrdersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DraftOrdersListResult"></a>

`DraftOrdersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[FulfillmentOrder], FulfillmentOrdersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="FulfillmentOrdersListResult"></a>

`FulfillmentOrdersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Fulfillment], FulfillmentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="FulfillmentsListResult"></a>

`FulfillmentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[InventoryItem], InventoryItemsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="InventoryItemsListResult"></a>

`InventoryItemsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[InventoryLevel], InventoryLevelsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="InventoryLevelsListResult"></a>

`InventoryLevelsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Location], LocationsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="LocationsListResult"></a>

`LocationsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Metafield], MetafieldCustomersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MetafieldCustomersListResult"></a>

`MetafieldCustomersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Metafield], MetafieldDraftOrdersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersListResult"></a>

`MetafieldDraftOrdersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Metafield], MetafieldLocationsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MetafieldLocationsListResult"></a>

`MetafieldLocationsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Metafield], MetafieldOrdersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MetafieldOrdersListResult"></a>

`MetafieldOrdersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Metafield], MetafieldProductImagesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MetafieldProductImagesListResult"></a>

`MetafieldProductImagesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Metafield], MetafieldProductVariantsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsListResult"></a>

`MetafieldProductVariantsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Metafield], MetafieldProductsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MetafieldProductsListResult"></a>

`MetafieldProductsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Metafield], MetafieldShopsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MetafieldShopsListResult"></a>

`MetafieldShopsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Metafield], MetafieldSmartCollectionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsListResult"></a>

`MetafieldSmartCollectionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Order], OrdersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrdersListResult"></a>

`OrdersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[PriceRule], PriceRulesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PriceRulesListResult"></a>

`PriceRulesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[ProductImage], ProductImagesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductImagesListResult"></a>

`ProductImagesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[ProductVariant], ProductVariantsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductVariantsListResult"></a>

`ProductVariantsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Product], ProductsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductsListResult"></a>

`ProductsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Refund], OrderRefundsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrderRefundsListResult"></a>

`OrderRefundsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[SmartCollection], SmartCollectionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SmartCollectionsListResult"></a>

`SmartCollectionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[TenderTransaction], TenderTransactionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TenderTransactionsListResult"></a>

`TenderTransactionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ShopifyExecuteResultWithMeta[list[Transaction], TransactionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TransactionsListResult"></a>

`TransactionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SmartCollection"></a>

`SmartCollection(**data: Any)`
:   A smart collection
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `body_html: str | None`
    :   The type of the None singleton.

    `disjunctive: bool | None`
    :   The type of the None singleton.

    `handle: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `image: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `products_count: int | None`
    :   The type of the None singleton.

    `published_at: str | None`
    :   The type of the None singleton.

    `published_scope: str | None`
    :   The type of the None singleton.

    `rules: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `sort_order: str | None`
    :   The type of the None singleton.

    `template_suffix: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="SmartCollectionList"></a>

`SmartCollectionList(**data: Any)`
:   SmartCollectionList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `smart_collections: list[airbyte_agent_sdk.connectors.shopify.models.SmartCollection] | None`
    :   The type of the None singleton.

<a id="SmartCollectionsListResultMeta"></a>

`SmartCollectionsListResultMeta(**data: Any)`
:   Metadata for smart_collections.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="TenderTransaction"></a>

`TenderTransaction(**data: Any)`
:   A tender transaction
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   The type of the None singleton.

    `currency: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `order_id: int | None`
    :   The type of the None singleton.

    `payment_details: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `payment_method: str | None`
    :   The type of the None singleton.

    `processed_at: str | None`
    :   The type of the None singleton.

    `remote_reference: str | None`
    :   The type of the None singleton.

    `test: bool | None`
    :   The type of the None singleton.

    `user_id: int | None`
    :   The type of the None singleton.

<a id="TenderTransactionList"></a>

`TenderTransactionList(**data: Any)`
:   TenderTransactionList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `tender_transactions: list[airbyte_agent_sdk.connectors.shopify.models.TenderTransaction] | None`
    :   The type of the None singleton.

<a id="TenderTransactionsListResultMeta"></a>

`TenderTransactionsListResultMeta(**data: Any)`
:   Metadata for tender_transactions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.

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

<a id="Transaction"></a>

`Transaction(**data: Any)`
:   An order transaction
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `amount: str | None`
    :   The type of the None singleton.

    `authorization: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `currency: str | None`
    :   The type of the None singleton.

    `currency_exchange_adjustment: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `device_id: int | None`
    :   The type of the None singleton.

    `error_code: str | None`
    :   The type of the None singleton.

    `gateway: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `location_id: int | None`
    :   The type of the None singleton.

    `manual_payment_gateway: bool | None`
    :   The type of the None singleton.

    `message: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `order_id: int | None`
    :   The type of the None singleton.

    `parent_id: int | None`
    :   The type of the None singleton.

    `payment_id: str | None`
    :   The type of the None singleton.

    `processed_at: str | None`
    :   The type of the None singleton.

    `receipt: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `source_name: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `test: bool | None`
    :   The type of the None singleton.

    `total_unsettled_set: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `user_id: int | None`
    :   The type of the None singleton.

<a id="TransactionList"></a>

`TransactionList(**data: Any)`
:   TransactionList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `transactions: list[airbyte_agent_sdk.connectors.shopify.models.Transaction] | None`
    :   The type of the None singleton.

<a id="TransactionsListResultMeta"></a>

`TransactionsListResultMeta(**data: Any)`
:   Metadata for transactions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_url: str | None`
    :   The type of the None singleton.