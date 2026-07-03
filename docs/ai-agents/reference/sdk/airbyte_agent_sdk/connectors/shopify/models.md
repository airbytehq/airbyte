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
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[ArticlesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[BalanceTransactionsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[BlogsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[CollectsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[CountriesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[CustomCollectionsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[CustomersSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[DiscountCodesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[DisputesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[DraftOrdersSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[FulfillmentOrdersSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[FulfillmentsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[InventoryItemsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[InventoryLevelsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[LocationsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldArticlesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldBlogsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldCustomersSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldDraftOrdersSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldLocationsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldOrdersSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldPagesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldProductImagesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldProductVariantsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldProductsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldShopsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldSmartCollectionsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[OrderRefundsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[OrdersSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[PagesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[PriceRulesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[ProductImagesSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[ProductVariantsSearchData]
    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[ProductsSearchData]
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

`AirbyteSearchResult[ArticlesSearchData](**data: Any)`
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

<a id="ArticlesSearchResult"></a>

`ArticlesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[BalanceTransactionsSearchData](**data: Any)`
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

<a id="BalanceTransactionsSearchResult"></a>

`BalanceTransactionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[BlogsSearchData](**data: Any)`
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

<a id="BlogsSearchResult"></a>

`BlogsSearchResult(**data: Any)`
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

`AirbyteSearchResult[DisputesSearchData](**data: Any)`
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

<a id="DisputesSearchResult"></a>

`DisputesSearchResult(**data: Any)`
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

`AirbyteSearchResult[MetafieldArticlesSearchData](**data: Any)`
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

<a id="MetafieldArticlesSearchResult"></a>

`MetafieldArticlesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[MetafieldBlogsSearchData](**data: Any)`
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

<a id="MetafieldBlogsSearchResult"></a>

`MetafieldBlogsSearchResult(**data: Any)`
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

`AirbyteSearchResult[MetafieldPagesSearchData](**data: Any)`
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

<a id="MetafieldPagesSearchResult"></a>

`MetafieldPagesSearchResult(**data: Any)`
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

`AirbyteSearchResult[OrdersSearchData](**data: Any)`
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

<a id="OrdersSearchResult"></a>

`OrdersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[PagesSearchData](**data: Any)`
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

<a id="PagesSearchResult"></a>

`PagesSearchResult(**data: Any)`
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

`AirbyteSearchResult[ProductsSearchData](**data: Any)`
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

<a id="ProductsSearchResult"></a>

`ProductsSearchResult(**data: Any)`
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

<a id="Article"></a>

`Article(**data: Any)`
:   A blog article (post)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `author: str | None`
    :   The type of the None singleton.

    `blog_id: int | None`
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

    `model_config`
    :   The type of the None singleton.

    `published_at: str | None`
    :   The type of the None singleton.

    `summary_html: str | None`
    :   The type of the None singleton.

    `tags: str | None`
    :   The type of the None singleton.

    `template_suffix: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `user_id: int | None`
    :   The type of the None singleton.

<a id="ArticleCreateParams"></a>

`ArticleCreateParams(**data: Any)`
:   Parameters for creating a blog article.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `article: airbyte_agent_sdk.connectors.shopify.models.ArticleCreateParamsArticle`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ArticleCreateParamsArticle"></a>

`ArticleCreateParamsArticle(**data: Any)`
:   Nested schema for ArticleCreateParams.article
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: airbyte_agent_sdk.connectors.shopify.models.ArticleCreateParamsArticleAuthor`
    :   Author of the article. Required by Shopify's articleCreate mutation (ArticleCreateInput.author is non-null).

    `blog_id: str`
    :   GraphQL GID of the blog this article belongs to

    `body: str | None`
    :   Article body content (HTML)

    `handle: str | None`
    :   URL handle for the article

    `is_published: bool | None`
    :   Whether the article is published

    `model_config`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

    `title: str`
    :   Article title

<a id="ArticleCreateParamsArticleAuthor"></a>

`ArticleCreateParamsArticleAuthor(**data: Any)`
:   Author of the article. Required by Shopify's articleCreate mutation (ArticleCreateInput.author is non-null).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   Author display name. Required (provide the author's name).

<a id="ArticleCreatePayload"></a>

`ArticleCreatePayload(**data: Any)`
:   ArticleCreatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `article: airbyte_agent_sdk.connectors.shopify.models.GraphQLArticle | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="ArticleDeleteParams"></a>

`ArticleDeleteParams(**data: Any)`
:   Parameters for deleting a blog article.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ArticleDeletePayload"></a>

`ArticleDeletePayload(**data: Any)`
:   ArticleDeletePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `deleted_article_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="ArticleDeleteResponse"></a>

`ArticleDeleteResponse(**data: Any)`
:   ArticleDeleteResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.ArticleDeleteResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ArticleDeleteResponseData"></a>

`ArticleDeleteResponseData(**data: Any)`
:   Nested schema for ArticleDeleteResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `article_delete: airbyte_agent_sdk.connectors.shopify.models.ArticleDeletePayload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ArticleList"></a>

`ArticleList(**data: Any)`
:   ArticleList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `articles: list[airbyte_agent_sdk.connectors.shopify.models.Article] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ArticleMutationResponse"></a>

`ArticleMutationResponse(**data: Any)`
:   ArticleMutationResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.ArticleMutationResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ArticleMutationResponseData"></a>

`ArticleMutationResponseData(**data: Any)`
:   Nested schema for ArticleMutationResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `article_create: airbyte_agent_sdk.connectors.shopify.models.ArticleCreatePayload | None`
    :   The type of the None singleton.

    `article_update: airbyte_agent_sdk.connectors.shopify.models.ArticleUpdatePayload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ArticleUpdateParams"></a>

`ArticleUpdateParams(**data: Any)`
:   Parameters for updating a blog article.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `article: airbyte_agent_sdk.connectors.shopify.models.ArticleUpdateParamsArticle`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ArticleUpdateParamsArticle"></a>

`ArticleUpdateParamsArticle(**data: Any)`
:   Nested schema for ArticleUpdateParams.article
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body: str | None`
    :   The type of the None singleton.

    `handle: str | None`
    :   The type of the None singleton.

    `is_published: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="ArticleUpdatePayload"></a>

`ArticleUpdatePayload(**data: Any)`
:   ArticleUpdatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `article: airbyte_agent_sdk.connectors.shopify.models.GraphQLArticle | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="ArticlesListResultMeta"></a>

`ArticlesListResultMeta(**data: Any)`
:   Metadata for articles.Action.LIST operation
    
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

<a id="ArticlesSearchData"></a>

`ArticlesSearchData(**data: Any)`
:   Search result data for articles entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: str | None`
    :   Name of the author of the article

    `blog_id: int | None`
    :   Identifier of the blog the article belongs to

    `body_html: str | None`
    :   HTML content of the article body

    `created_at: str | None`
    :   ISO 8601 timestamp when the article was created

    `handle: str | None`
    :   URL-friendly handle for the article

    `id: int | None`
    :   Unique identifier for the article

    `model_config`
    :   The type of the None singleton.

    `published_at: str | None`
    :   ISO 8601 timestamp when the article was published

    `summary_html: str | None`
    :   Summary of the article in HTML

    `tags: str | None`
    :   Comma-separated list of tags for the article

    `title: str | None`
    :   Title of the article

    `updated_at: str | None`
    :   ISO 8601 timestamp when the article was last updated

<a id="BalanceTransaction"></a>

`BalanceTransaction(**data: Any)`
:   A Shopify Payments balance transaction
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `adjustment_order_transactions: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `adjustment_reason: str | None`
    :   The type of the None singleton.

    `amount: str | None`
    :   The type of the None singleton.

    `currency: str | None`
    :   The type of the None singleton.

    `fee: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `net: str | None`
    :   The type of the None singleton.

    `payout_id: int | None`
    :   The type of the None singleton.

    `payout_status: str | None`
    :   The type of the None singleton.

    `processed_at: str | None`
    :   The type of the None singleton.

    `source_id: int | None`
    :   The type of the None singleton.

    `source_order_id: int | None`
    :   The type of the None singleton.

    `source_order_transaction_id: int | None`
    :   The type of the None singleton.

    `source_type: str | None`
    :   The type of the None singleton.

    `test: bool | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BalanceTransactionList"></a>

`BalanceTransactionList(**data: Any)`
:   BalanceTransactionList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `transactions: list[airbyte_agent_sdk.connectors.shopify.models.BalanceTransaction] | None`
    :   The type of the None singleton.

<a id="BalanceTransactionsListResultMeta"></a>

`BalanceTransactionsListResultMeta(**data: Any)`
:   Metadata for balance_transactions.Action.LIST operation
    
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

<a id="BalanceTransactionsSearchData"></a>

`BalanceTransactionsSearchData(**data: Any)`
:   Search result data for balance_transactions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   Gross amount of the transaction

    `currency: str | None`
    :   ISO 4217 currency code of the transaction

    `fee: str | None`
    :   Total fees deducted from the transaction

    `id: int | None`
    :   Unique identifier of the balance transaction

    `model_config`
    :   The type of the None singleton.

    `net: str | None`
    :   Net amount of the transaction

    `payout_id: int | None`
    :   Identifier of the payout the transaction was paid out in

    `payout_status: str | None`
    :   Status of the associated payout

    `processed_at: str | None`
    :   ISO 8601 timestamp when the transaction was processed

    `source_order_id: int | None`
    :   Identifier of the source order, if applicable

    `source_type: str | None`
    :   Type of the resource that led to this transaction

    `type_: str | None`
    :   Type of the transaction (charge, refund, dispute, reserve, adjustment, credit, debit, payout, etc.)

<a id="Blog"></a>

`Blog(**data: Any)`
:   A blog on the store
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `commentable: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `feedburner: str | None`
    :   The type of the None singleton.

    `feedburner_location: str | None`
    :   The type of the None singleton.

    `handle: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `tags: str | None`
    :   The type of the None singleton.

    `template_suffix: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="BlogCreateParams"></a>

`BlogCreateParams(**data: Any)`
:   Parameters for creating a blog.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `blog: airbyte_agent_sdk.connectors.shopify.models.BlogCreateParamsBlog`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlogCreateParamsBlog"></a>

`BlogCreateParamsBlog(**data: Any)`
:   Nested schema for BlogCreateParams.blog
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `handle: str | None`
    :   URL handle for the blog

    `model_config`
    :   The type of the None singleton.

    `title: str`
    :   Blog title

<a id="BlogCreatePayload"></a>

`BlogCreatePayload(**data: Any)`
:   BlogCreatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `blog: airbyte_agent_sdk.connectors.shopify.models.GraphQLBlog | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="BlogDeleteParams"></a>

`BlogDeleteParams(**data: Any)`
:   Parameters for deleting a blog.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlogDeletePayload"></a>

`BlogDeletePayload(**data: Any)`
:   BlogDeletePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `deleted_blog_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="BlogDeleteResponse"></a>

`BlogDeleteResponse(**data: Any)`
:   BlogDeleteResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.BlogDeleteResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlogDeleteResponseData"></a>

`BlogDeleteResponseData(**data: Any)`
:   Nested schema for BlogDeleteResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `blog_delete: airbyte_agent_sdk.connectors.shopify.models.BlogDeletePayload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlogList"></a>

`BlogList(**data: Any)`
:   BlogList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `blogs: list[airbyte_agent_sdk.connectors.shopify.models.Blog] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlogMutationResponse"></a>

`BlogMutationResponse(**data: Any)`
:   BlogMutationResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.BlogMutationResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlogMutationResponseData"></a>

`BlogMutationResponseData(**data: Any)`
:   Nested schema for BlogMutationResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `blog_create: airbyte_agent_sdk.connectors.shopify.models.BlogCreatePayload | None`
    :   The type of the None singleton.

    `blog_update: airbyte_agent_sdk.connectors.shopify.models.BlogUpdatePayload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlogUpdateParams"></a>

`BlogUpdateParams(**data: Any)`
:   Parameters for updating a blog.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `blog: airbyte_agent_sdk.connectors.shopify.models.BlogUpdateParamsBlog`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlogUpdateParamsBlog"></a>

`BlogUpdateParamsBlog(**data: Any)`
:   Nested schema for BlogUpdateParams.blog
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `handle: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="BlogUpdatePayload"></a>

`BlogUpdatePayload(**data: Any)`
:   BlogUpdatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `blog: airbyte_agent_sdk.connectors.shopify.models.GraphQLBlog | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="BlogsListResultMeta"></a>

`BlogsListResultMeta(**data: Any)`
:   Metadata for blogs.Action.LIST operation
    
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

<a id="BlogsSearchData"></a>

`BlogsSearchData(**data: Any)`
:   Search result data for blogs entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `commentable: str | None`
    :   Whether readers can post comments (no, moderate, yes)

    `created_at: str | None`
    :   ISO 8601 timestamp when the blog was created

    `handle: str | None`
    :   URL-friendly handle for the blog

    `id: int | None`
    :   Unique identifier for the blog

    `model_config`
    :   The type of the None singleton.

    `tags: str | None`
    :   Comma-separated tags from the blog's articles

    `title: str | None`
    :   Title of the blog

    `updated_at: str | None`
    :   ISO 8601 timestamp when the blog was last updated

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

<a id="CollectionCreateParams"></a>

`CollectionCreateParams(**data: Any)`
:   Parameters for creating a collection (custom or smart).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `input: airbyte_agent_sdk.connectors.shopify.models.CollectionCreateParamsInput`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CollectionCreateParamsInput"></a>

`CollectionCreateParamsInput(**data: Any)`
:   Nested schema for CollectionCreateParams.input
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description_html: str | None`
    :   Collection description in HTML

    `handle: str | None`
    :   URL handle for the collection

    `model_config`
    :   The type of the None singleton.

    `rule_set: airbyte_agent_sdk.connectors.shopify.models.CollectionCreateParamsInputRuleset | None`
    :   Rule set for smart collections

    `sort_order: str | None`
    :   Sort order for products

    `template_suffix: str | None`
    :   Liquid template suffix

    `title: str`
    :   Collection title

<a id="CollectionCreateParamsInputRuleset"></a>

`CollectionCreateParamsInputRuleset(**data: Any)`
:   Rule set for smart collections
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `applied_disjunctively: bool | None`
    :   Whether rules are OR (true) or AND (false)

    `model_config`
    :   The type of the None singleton.

    `rules: list[airbyte_agent_sdk.connectors.shopify.models.CollectionCreateParamsInputRulesetRulesItem] | None`
    :   The type of the None singleton.

<a id="CollectionCreateParamsInputRulesetRulesItem"></a>

`CollectionCreateParamsInputRulesetRulesItem(**data: Any)`
:   Nested schema for CollectionCreateParamsInputRuleset.rules_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `column: str | None`
    :   Rule column (e.g. TAG, TITLE, VENDOR)

    `condition: str | None`
    :   Rule condition value

    `model_config`
    :   The type of the None singleton.

    `relation: str | None`
    :   Rule relation (e.g. EQUALS, CONTAINS)

<a id="CollectionCreatePayload"></a>

`CollectionCreatePayload(**data: Any)`
:   CollectionCreatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `collection: airbyte_agent_sdk.connectors.shopify.models.CollectionCreatePayloadCollection | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="CollectionCreatePayloadCollection"></a>

`CollectionCreatePayloadCollection(**data: Any)`
:   Nested schema for CollectionCreatePayload.collection
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description_html: str | None`
    :   The type of the None singleton.

    `handle: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `sort_order: str | None`
    :   The type of the None singleton.

    `template_suffix: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="CollectionDeleteParams"></a>

`CollectionDeleteParams(**data: Any)`
:   Parameters for deleting a collection.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `input: airbyte_agent_sdk.connectors.shopify.models.CollectionDeleteParamsInput`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CollectionDeleteParamsInput"></a>

`CollectionDeleteParamsInput(**data: Any)`
:   Nested schema for CollectionDeleteParams.input
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The GraphQL GID of the collection to delete

    `model_config`
    :   The type of the None singleton.

<a id="CollectionDeletePayload"></a>

`CollectionDeletePayload(**data: Any)`
:   CollectionDeletePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `deleted_collection_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="CollectionDeleteResponse"></a>

`CollectionDeleteResponse(**data: Any)`
:   CollectionDeleteResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.CollectionDeleteResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CollectionDeleteResponseData"></a>

`CollectionDeleteResponseData(**data: Any)`
:   Nested schema for CollectionDeleteResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `collection_delete: airbyte_agent_sdk.connectors.shopify.models.CollectionDeletePayload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CollectionMutationResponse"></a>

`CollectionMutationResponse(**data: Any)`
:   CollectionMutationResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.CollectionMutationResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CollectionMutationResponseData"></a>

`CollectionMutationResponseData(**data: Any)`
:   Nested schema for CollectionMutationResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `collection_create: airbyte_agent_sdk.connectors.shopify.models.CollectionCreatePayload | None`
    :   The type of the None singleton.

    `collection_update: airbyte_agent_sdk.connectors.shopify.models.CollectionUpdatePayload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CollectionUpdateParams"></a>

`CollectionUpdateParams(**data: Any)`
:   Parameters for updating a collection.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `input: airbyte_agent_sdk.connectors.shopify.models.CollectionUpdateParamsInput`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CollectionUpdateParamsInput"></a>

`CollectionUpdateParamsInput(**data: Any)`
:   Nested schema for CollectionUpdateParams.input
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description_html: str | None`
    :   The type of the None singleton.

    `handle: str | None`
    :   The type of the None singleton.

    `id: str`
    :   The GraphQL GID of the collection

    `model_config`
    :   The type of the None singleton.

    `sort_order: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="CollectionUpdatePayload"></a>

`CollectionUpdatePayload(**data: Any)`
:   CollectionUpdatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `collection: airbyte_agent_sdk.connectors.shopify.models.CollectionUpdatePayloadCollection | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="CollectionUpdatePayloadCollection"></a>

`CollectionUpdatePayloadCollection(**data: Any)`
:   Nested schema for CollectionUpdatePayload.collection
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description_html: str | None`
    :   The type of the None singleton.

    `handle: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `sort_order: str | None`
    :   The type of the None singleton.

    `template_suffix: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
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

<a id="CustomerCreateParams"></a>

`CustomerCreateParams(**data: Any)`
:   Parameters for creating a customer. Provide fields inside the 'input' object.
    At least one of email, phone, firstName, or lastName is required.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `input: airbyte_agent_sdk.connectors.shopify.models.CustomerCreateParamsInput`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomerCreateParamsInput"></a>

`CustomerCreateParamsInput(**data: Any)`
:   CustomerInput object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `addresses: list[airbyte_agent_sdk.connectors.shopify.models.CustomerCreateParamsInputAddressesItem] | None`
    :   List of customer addresses

    `email: str | None`
    :   Customer email address

    `first_name: str | None`
    :   Customer first name

    `last_name: str | None`
    :   Customer last name

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   Note about the customer

    `phone: str | None`
    :   Customer phone number (E.164 format, e.g. +16465555555)

    `tags: list[str] | None`
    :   Tags to associate with the customer

    `tax_exempt: bool | None`
    :   Whether the customer is tax exempt

<a id="CustomerCreateParamsInputAddressesItem"></a>

`CustomerCreateParamsInputAddressesItem(**data: Any)`
:   Nested schema for CustomerCreateParamsInput.addresses_item
    
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

    `country_code: str | None`
    :   The type of the None singleton.

    `first_name: str | None`
    :   The type of the None singleton.

    `last_name: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `phone: str | None`
    :   The type of the None singleton.

    `province: str | None`
    :   The type of the None singleton.

    `zip: str | None`
    :   The type of the None singleton.

<a id="CustomerCreatePayload"></a>

`CustomerCreatePayload(**data: Any)`
:   CustomerCreatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `customer: airbyte_agent_sdk.connectors.shopify.models.GraphQLCustomer | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="CustomerDeleteParams"></a>

`CustomerDeleteParams(**data: Any)`
:   Parameters for deleting a customer. Only succeeds if the customer has no orders.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `input: airbyte_agent_sdk.connectors.shopify.models.CustomerDeleteParamsInput`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomerDeleteParamsInput"></a>

`CustomerDeleteParamsInput(**data: Any)`
:   Nested schema for CustomerDeleteParams.input
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The GraphQL GID of the customer to delete (e.g. gid://shopify/Customer/123)

    `model_config`
    :   The type of the None singleton.

<a id="CustomerDeletePayload"></a>

`CustomerDeletePayload(**data: Any)`
:   CustomerDeletePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `deleted_customer_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="CustomerDeleteResponse"></a>

`CustomerDeleteResponse(**data: Any)`
:   CustomerDeleteResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.CustomerDeleteResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomerDeleteResponseData"></a>

`CustomerDeleteResponseData(**data: Any)`
:   Nested schema for CustomerDeleteResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `customer_delete: airbyte_agent_sdk.connectors.shopify.models.CustomerDeletePayload | None`
    :   The type of the None singleton.

    `model_config`
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

<a id="CustomerMutationResponse"></a>

`CustomerMutationResponse(**data: Any)`
:   CustomerMutationResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.CustomerMutationResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomerMutationResponseData"></a>

`CustomerMutationResponseData(**data: Any)`
:   Nested schema for CustomerMutationResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `customer_create: airbyte_agent_sdk.connectors.shopify.models.CustomerCreatePayload | None`
    :   The type of the None singleton.

    `customer_update: airbyte_agent_sdk.connectors.shopify.models.CustomerUpdatePayload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomerUpdateParams"></a>

`CustomerUpdateParams(**data: Any)`
:   Parameters for updating a customer. The input.id field is required.
    All other fields are optional for partial updates.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `input: airbyte_agent_sdk.connectors.shopify.models.CustomerUpdateParamsInput`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomerUpdateParamsInput"></a>

`CustomerUpdateParamsInput(**data: Any)`
:   CustomerInput object with id
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | None`
    :   Customer email address

    `first_name: str | None`
    :   Customer first name

    `id: str`
    :   The GraphQL GID of the customer (e.g. gid://shopify/Customer/123)

    `last_name: str | None`
    :   Customer last name

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   Note about the customer

    `phone: str | None`
    :   Customer phone number (E.164 format)

    `tags: list[str] | None`
    :   Tags to associate with the customer

    `tax_exempt: bool | None`
    :   Whether the customer is tax exempt

<a id="CustomerUpdatePayload"></a>

`CustomerUpdatePayload(**data: Any)`
:   CustomerUpdatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `customer: airbyte_agent_sdk.connectors.shopify.models.GraphQLCustomer | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
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

<a id="DiscountCodeBasicCreatePayload"></a>

`DiscountCodeBasicCreatePayload(**data: Any)`
:   DiscountCodeBasicCreatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code_discount_node: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeBasicCreatePayloadCodediscountnode | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="DiscountCodeBasicCreatePayloadCodediscountnode"></a>

`DiscountCodeBasicCreatePayloadCodediscountnode(**data: Any)`
:   Nested schema for DiscountCodeBasicCreatePayload.codeDiscountNode
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code_discount: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeBasicCreatePayloadCodediscountnodeCodediscount | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodeBasicCreatePayloadCodediscountnodeCodediscount"></a>

`DiscountCodeBasicCreatePayloadCodediscountnodeCodediscount(**data: Any)`
:   Nested schema for DiscountCodeBasicCreatePayloadCodediscountnode.codeDiscount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `codes: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeBasicCreatePayloadCodediscountnodeCodediscountCodes | None`
    :   The type of the None singleton.

    `ends_at: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `starts_at: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `summary: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="DiscountCodeBasicCreatePayloadCodediscountnodeCodediscountCodes"></a>

`DiscountCodeBasicCreatePayloadCodediscountnodeCodediscountCodes(**data: Any)`
:   Nested schema for DiscountCodeBasicCreatePayloadCodediscountnodeCodediscount.codes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `nodes: list[airbyte_agent_sdk.connectors.shopify.models.DiscountCodeBasicCreatePayloadCodediscountnodeCodediscountCodesNodesItem] | None`
    :   The type of the None singleton.

<a id="DiscountCodeBasicCreatePayloadCodediscountnodeCodediscountCodesNodesItem"></a>

`DiscountCodeBasicCreatePayloadCodediscountnodeCodediscountCodesNodesItem(**data: Any)`
:   Nested schema for DiscountCodeBasicCreatePayloadCodediscountnodeCodediscountCodes.nodes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodeBasicUpdatePayload"></a>

`DiscountCodeBasicUpdatePayload(**data: Any)`
:   DiscountCodeBasicUpdatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code_discount_node: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeBasicUpdatePayloadCodediscountnode | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="DiscountCodeBasicUpdatePayloadCodediscountnode"></a>

`DiscountCodeBasicUpdatePayloadCodediscountnode(**data: Any)`
:   Nested schema for DiscountCodeBasicUpdatePayload.codeDiscountNode
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code_discount: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeBasicUpdatePayloadCodediscountnodeCodediscount | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodeBasicUpdatePayloadCodediscountnodeCodediscount"></a>

`DiscountCodeBasicUpdatePayloadCodediscountnodeCodediscount(**data: Any)`
:   Nested schema for DiscountCodeBasicUpdatePayloadCodediscountnode.codeDiscount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `codes: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeBasicUpdatePayloadCodediscountnodeCodediscountCodes | None`
    :   The type of the None singleton.

    `ends_at: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `starts_at: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `summary: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="DiscountCodeBasicUpdatePayloadCodediscountnodeCodediscountCodes"></a>

`DiscountCodeBasicUpdatePayloadCodediscountnodeCodediscountCodes(**data: Any)`
:   Nested schema for DiscountCodeBasicUpdatePayloadCodediscountnodeCodediscount.codes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `nodes: list[airbyte_agent_sdk.connectors.shopify.models.DiscountCodeBasicUpdatePayloadCodediscountnodeCodediscountCodesNodesItem] | None`
    :   The type of the None singleton.

<a id="DiscountCodeBasicUpdatePayloadCodediscountnodeCodediscountCodesNodesItem"></a>

`DiscountCodeBasicUpdatePayloadCodediscountnodeCodediscountCodesNodesItem(**data: Any)`
:   Nested schema for DiscountCodeBasicUpdatePayloadCodediscountnodeCodediscountCodes.nodes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodeCreateParams"></a>

`DiscountCodeCreateParams(**data: Any)`
:   Parameters for creating a basic discount code.
    Supports percentage or fixed amount discounts.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `basic_code_discount: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeCreateParamsBasiccodediscount`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodeCreateParamsBasiccodediscount"></a>

`DiscountCodeCreateParamsBasiccodediscount(**data: Any)`
:   Nested schema for DiscountCodeCreateParams.basicCodeDiscount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str`
    :   Discount code that customers enter at checkout

    `customer_gets: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeCreateParamsBasiccodediscountCustomergets`
    :   What the customer gets from this discount

    `customer_selection: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeCreateParamsBasiccodediscountCustomerselection`
    :   Which customers can use this discount

    `ends_at: str | None`
    :   When the discount ends (ISO 8601, optional)

    `model_config`
    :   The type of the None singleton.

    `starts_at: str`
    :   When the discount starts (ISO 8601)

    `title: str`
    :   Discount title

    `usage_limit: int | None`
    :   Maximum number of times the discount can be used

<a id="DiscountCodeCreateParamsBasiccodediscountCustomergets"></a>

`DiscountCodeCreateParamsBasiccodediscountCustomergets(**data: Any)`
:   What the customer gets from this discount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `items: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeCreateParamsBasiccodediscountCustomergetsItems | None`
    :   Which items the discount applies to

    `model_config`
    :   The type of the None singleton.

    `value: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeCreateParamsBasiccodediscountCustomergetsValue | None`
    :   The discount value

<a id="DiscountCodeCreateParamsBasiccodediscountCustomergetsItems"></a>

`DiscountCodeCreateParamsBasiccodediscountCustomergetsItems(**data: Any)`
:   Which items the discount applies to
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `all: bool | None`
    :   Set to true for all items

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodeCreateParamsBasiccodediscountCustomergetsValue"></a>

`DiscountCodeCreateParamsBasiccodediscountCustomergetsValue(**data: Any)`
:   The discount value
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `discount_amount: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeCreateParamsBasiccodediscountCustomergetsValueDiscountamount | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `percentage: float | None`
    :   Percentage discount (e.g. 0.1 for 10%)

<a id="DiscountCodeCreateParamsBasiccodediscountCustomergetsValueDiscountamount"></a>

`DiscountCodeCreateParamsBasiccodediscountCustomergetsValueDiscountamount(**data: Any)`
:   Nested schema for DiscountCodeCreateParamsBasiccodediscountCustomergetsValue.discountAmount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   The type of the None singleton.

    `applies_on_each_item: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodeCreateParamsBasiccodediscountCustomerselection"></a>

`DiscountCodeCreateParamsBasiccodediscountCustomerselection(**data: Any)`
:   Which customers can use this discount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `all: bool | None`
    :   Set to true for all customers

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodeDeleteParams"></a>

`DiscountCodeDeleteParams(**data: Any)`
:   Parameters for deleting a discount code.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodeDeletePayload"></a>

`DiscountCodeDeletePayload(**data: Any)`
:   DiscountCodeDeletePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `deleted_code_discount_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="DiscountCodeDeleteResponse"></a>

`DiscountCodeDeleteResponse(**data: Any)`
:   DiscountCodeDeleteResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeDeleteResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodeDeleteResponseData"></a>

`DiscountCodeDeleteResponseData(**data: Any)`
:   Nested schema for DiscountCodeDeleteResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `discount_code_delete: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeDeletePayload | None`
    :   The type of the None singleton.

    `model_config`
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

<a id="DiscountCodeMutationResponse"></a>

`DiscountCodeMutationResponse(**data: Any)`
:   DiscountCodeMutationResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeMutationResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodeMutationResponseData"></a>

`DiscountCodeMutationResponseData(**data: Any)`
:   Nested schema for DiscountCodeMutationResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `discount_code_basic_create: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeBasicCreatePayload | None`
    :   The type of the None singleton.

    `discount_code_basic_update: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeBasicUpdatePayload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodeUpdateParams"></a>

`DiscountCodeUpdateParams(**data: Any)`
:   Parameters for updating a basic discount code.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `basic_code_discount: airbyte_agent_sdk.connectors.shopify.models.DiscountCodeUpdateParamsBasiccodediscount`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DiscountCodeUpdateParamsBasiccodediscount"></a>

`DiscountCodeUpdateParamsBasiccodediscount(**data: Any)`
:   Nested schema for DiscountCodeUpdateParams.basicCodeDiscount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `ends_at: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `starts_at: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `usage_limit: int | None`
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

<a id="Dispute"></a>

`Dispute(**data: Any)`
:   A Shopify Payments dispute
    
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

    `evidence_due_by: str | None`
    :   The type of the None singleton.

    `evidence_sent_on: str | None`
    :   The type of the None singleton.

    `finalized_on: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `initiated_at: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `network_reason_code: str | None`
    :   The type of the None singleton.

    `order_id: int | None`
    :   The type of the None singleton.

    `reason: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="DisputeList"></a>

`DisputeList(**data: Any)`
:   DisputeList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `disputes: list[airbyte_agent_sdk.connectors.shopify.models.Dispute] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DisputesListResultMeta"></a>

`DisputesListResultMeta(**data: Any)`
:   Metadata for disputes.Action.LIST operation
    
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

<a id="DisputesSearchData"></a>

`DisputesSearchData(**data: Any)`
:   Search result data for disputes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   Disputed amount

    `currency: str | None`
    :   ISO 4217 currency code of the dispute amount

    `evidence_due_by: str | None`
    :   ISO 8601 deadline for evidence submission

    `finalized_on: str | None`
    :   ISO 8601 timestamp when the dispute was resolved

    `id: int | None`
    :   Unique identifier for the dispute

    `initiated_at: str | None`
    :   ISO 8601 timestamp when the dispute was initiated

    `model_config`
    :   The type of the None singleton.

    `network_reason_code: str | None`
    :   Network reason code from the cardholder's bank

    `order_id: int | None`
    :   Identifier of the order the dispute belongs to

    `reason: str | None`
    :   Reason for the dispute provided by the cardholder's bank

    `status: str | None`
    :   Current state of the dispute (needs_response, under_review, charge_refunded, accepted, won, lost)

    `type_: str | None`
    :   Whether the dispute is an inquiry or chargeback

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

<a id="DraftOrderCompleteParams"></a>

`DraftOrderCompleteParams(**data: Any)`
:   Parameters for completing a draft order, converting it to a regular order.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `payment_pending: bool | None`
    :   The type of the None singleton.

<a id="DraftOrderCompletePayload"></a>

`DraftOrderCompletePayload(**data: Any)`
:   DraftOrderCompletePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `draft_order: airbyte_agent_sdk.connectors.shopify.models.DraftOrderCompletePayloadDraftorder | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="DraftOrderCompletePayloadDraftorder"></a>

`DraftOrderCompletePayloadDraftorder(**data: Any)`
:   Nested schema for DraftOrderCompletePayload.draftOrder
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `order: airbyte_agent_sdk.connectors.shopify.models.DraftOrderCompletePayloadDraftorderOrder | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

<a id="DraftOrderCompletePayloadDraftorderOrder"></a>

`DraftOrderCompletePayloadDraftorderOrder(**data: Any)`
:   Nested schema for DraftOrderCompletePayloadDraftorder.order
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

<a id="DraftOrderCompleteResponse"></a>

`DraftOrderCompleteResponse(**data: Any)`
:   DraftOrderCompleteResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.DraftOrderCompleteResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DraftOrderCompleteResponseData"></a>

`DraftOrderCompleteResponseData(**data: Any)`
:   Nested schema for DraftOrderCompleteResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `draft_order_complete: airbyte_agent_sdk.connectors.shopify.models.DraftOrderCompletePayload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DraftOrderCreateParams"></a>

`DraftOrderCreateParams(**data: Any)`
:   Parameters for creating a draft order.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `input: airbyte_agent_sdk.connectors.shopify.models.DraftOrderCreateParamsInput`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DraftOrderCreateParamsInput"></a>

`DraftOrderCreateParamsInput(**data: Any)`
:   DraftOrderInput object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `customer_id: str | None`
    :   GraphQL GID of the customer

    `email: str | None`
    :   Customer email

    `line_items: list[airbyte_agent_sdk.connectors.shopify.models.DraftOrderCreateParamsInputLineitemsItem] | None`
    :   Line items for the draft order

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   Draft order note

    `shipping_address: airbyte_agent_sdk.connectors.shopify.models.DraftOrderCreateParamsInputShippingaddress | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

<a id="DraftOrderCreateParamsInputLineitemsItem"></a>

`DraftOrderCreateParamsInputLineitemsItem(**data: Any)`
:   Nested schema for DraftOrderCreateParamsInput.lineItems_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `original_unit_price: str | None`
    :   Unit price

    `quantity: int | None`
    :   Quantity

    `title: str | None`
    :   Custom title

    `variant_id: str | None`
    :   GraphQL GID of the product variant

<a id="DraftOrderCreateParamsInputShippingaddress"></a>

`DraftOrderCreateParamsInputShippingaddress(**data: Any)`
:   Nested schema for DraftOrderCreateParamsInput.shippingAddress
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address1: str | None`
    :   The type of the None singleton.

    `city: str | None`
    :   The type of the None singleton.

    `country_code: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `province_code: str | None`
    :   The type of the None singleton.

    `zip: str | None`
    :   The type of the None singleton.

<a id="DraftOrderCreatePayload"></a>

`DraftOrderCreatePayload(**data: Any)`
:   DraftOrderCreatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `draft_order: airbyte_agent_sdk.connectors.shopify.models.GraphQLDraftOrder | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="DraftOrderDeleteParams"></a>

`DraftOrderDeleteParams(**data: Any)`
:   Parameters for deleting a draft order. Only open draft orders can be deleted.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `input: airbyte_agent_sdk.connectors.shopify.models.DraftOrderDeleteParamsInput`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DraftOrderDeleteParamsInput"></a>

`DraftOrderDeleteParamsInput(**data: Any)`
:   Nested schema for DraftOrderDeleteParams.input
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The GraphQL GID of the draft order to delete

    `model_config`
    :   The type of the None singleton.

<a id="DraftOrderDeletePayload"></a>

`DraftOrderDeletePayload(**data: Any)`
:   DraftOrderDeletePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `deleted_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="DraftOrderDeleteResponse"></a>

`DraftOrderDeleteResponse(**data: Any)`
:   DraftOrderDeleteResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.DraftOrderDeleteResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DraftOrderDeleteResponseData"></a>

`DraftOrderDeleteResponseData(**data: Any)`
:   Nested schema for DraftOrderDeleteResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `draft_order_delete: airbyte_agent_sdk.connectors.shopify.models.DraftOrderDeletePayload | None`
    :   The type of the None singleton.

    `model_config`
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

<a id="DraftOrderMutationResponse"></a>

`DraftOrderMutationResponse(**data: Any)`
:   DraftOrderMutationResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.DraftOrderMutationResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DraftOrderMutationResponseData"></a>

`DraftOrderMutationResponseData(**data: Any)`
:   Nested schema for DraftOrderMutationResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `draft_order_create: airbyte_agent_sdk.connectors.shopify.models.DraftOrderCreatePayload | None`
    :   The type of the None singleton.

    `draft_order_update: airbyte_agent_sdk.connectors.shopify.models.DraftOrderUpdatePayload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DraftOrderUpdateParams"></a>

`DraftOrderUpdateParams(**data: Any)`
:   Parameters for updating a draft order.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `input: airbyte_agent_sdk.connectors.shopify.models.DraftOrderUpdateParamsInput`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DraftOrderUpdateParamsInput"></a>

`DraftOrderUpdateParamsInput(**data: Any)`
:   DraftOrderInput object with updated fields
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | None`
    :   The type of the None singleton.

    `line_items: list[airbyte_agent_sdk.connectors.shopify.models.DraftOrderUpdateParamsInputLineitemsItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

<a id="DraftOrderUpdateParamsInputLineitemsItem"></a>

`DraftOrderUpdateParamsInputLineitemsItem(**data: Any)`
:   Nested schema for DraftOrderUpdateParamsInput.lineItems_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `original_unit_price: str | None`
    :   The type of the None singleton.

    `quantity: int | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `variant_id: str | None`
    :   The type of the None singleton.

<a id="DraftOrderUpdatePayload"></a>

`DraftOrderUpdatePayload(**data: Any)`
:   DraftOrderUpdatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `draft_order: airbyte_agent_sdk.connectors.shopify.models.GraphQLDraftOrder | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
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

<a id="GraphQLArticle"></a>

`GraphQLArticle(**data: Any)`
:   GraphQLArticle type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `blog: airbyte_agent_sdk.connectors.shopify.models.GraphQLArticleBlog | None`
    :   The type of the None singleton.

    `body: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `handle: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="GraphQLArticleBlog"></a>

`GraphQLArticleBlog(**data: Any)`
:   Nested schema for GraphQLArticle.blog
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="GraphQLBlog"></a>

`GraphQLBlog(**data: Any)`
:   GraphQLBlog type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `handle: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="GraphQLCustomer"></a>

`GraphQLCustomer(**data: Any)`
:   Customer returned from GraphQL mutation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `first_name: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `last_name: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   The type of the None singleton.

    `phone: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

    `tax_exempt: bool | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="GraphQLDraftOrder"></a>

`GraphQLDraftOrder(**data: Any)`
:   GraphQLDraftOrder type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `currency_code: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `total_price: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="GraphQLOrder"></a>

`GraphQLOrder(**data: Any)`
:   GraphQLOrder type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `display_financial_status: str | None`
    :   The type of the None singleton.

    `display_fulfillment_status: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `total_price_set: airbyte_agent_sdk.connectors.shopify.models.GraphQLOrderTotalpriceset | None`
    :   The type of the None singleton.

<a id="GraphQLOrderTotalpriceset"></a>

`GraphQLOrderTotalpriceset(**data: Any)`
:   Nested schema for GraphQLOrder.totalPriceSet
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `shop_money: airbyte_agent_sdk.connectors.shopify.models.GraphQLOrderTotalpricesetShopmoney | None`
    :   The type of the None singleton.

<a id="GraphQLOrderTotalpricesetShopmoney"></a>

`GraphQLOrderTotalpricesetShopmoney(**data: Any)`
:   Nested schema for GraphQLOrderTotalpriceset.shopMoney
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   The type of the None singleton.

    `currency_code: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="GraphQLPage"></a>

`GraphQLPage(**data: Any)`
:   GraphQLPage type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `handle: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="GraphQLProduct"></a>

`GraphQLProduct(**data: Any)`
:   Product returned from GraphQL mutation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `description_html: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `product_type: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `vendor: str | None`
    :   The type of the None singleton.

<a id="GraphQLProductVariant"></a>

`GraphQLProductVariant(**data: Any)`
:   GraphQLProductVariant type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `barcode: str | None`
    :   The type of the None singleton.

    `compare_at_price: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `inventory_quantity: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `price: str | None`
    :   The type of the None singleton.

    `sku: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="GraphQLUserError"></a>

`GraphQLUserError(**data: Any)`
:   GraphQLUserError type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | None`
    :   The type of the None singleton.

    `field: typing.Any | None`
    :   The type of the None singleton.

    `message: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InventoryAdjustQuantitiesParams"></a>

`InventoryAdjustQuantitiesParams(**data: Any)`
:   Parameters for adjusting inventory quantities relatively (add/subtract).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `input: airbyte_agent_sdk.connectors.shopify.models.InventoryAdjustQuantitiesParamsInput`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InventoryAdjustQuantitiesParamsInput"></a>

`InventoryAdjustQuantitiesParamsInput(**data: Any)`
:   Nested schema for InventoryAdjustQuantitiesParams.input
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `changes: list[airbyte_agent_sdk.connectors.shopify.models.InventoryAdjustQuantitiesParamsInputChangesItem]`
    :   Inventory changes to apply

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   Quantity name (e.g. 'available')

    `reason: str`
    :   Reason for the adjustment

    `reference_document_uri: str | None`
    :   URI for the reference document

<a id="InventoryAdjustQuantitiesParamsInputChangesItem"></a>

`InventoryAdjustQuantitiesParamsInputChangesItem(**data: Any)`
:   Nested schema for InventoryAdjustQuantitiesParamsInput.changes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `delta: int`
    :   Amount to adjust (positive to add, negative to subtract)

    `inventory_item_id: str`
    :   GraphQL GID of the inventory item

    `location_id: str`
    :   GraphQL GID of the location

    `model_config`
    :   The type of the None singleton.

<a id="InventoryAdjustQuantitiesPayload"></a>

`InventoryAdjustQuantitiesPayload(**data: Any)`
:   InventoryAdjustQuantitiesPayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `inventory_adjustment_group: airbyte_agent_sdk.connectors.shopify.models.InventoryAdjustmentGroup | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="InventoryAdjustQuantitiesResponse"></a>

`InventoryAdjustQuantitiesResponse(**data: Any)`
:   InventoryAdjustQuantitiesResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.InventoryAdjustQuantitiesResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InventoryAdjustQuantitiesResponseData"></a>

`InventoryAdjustQuantitiesResponseData(**data: Any)`
:   Nested schema for InventoryAdjustQuantitiesResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `inventory_adjust_quantities: airbyte_agent_sdk.connectors.shopify.models.InventoryAdjustQuantitiesPayload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InventoryAdjustmentGroup"></a>

`InventoryAdjustmentGroup(**data: Any)`
:   InventoryAdjustmentGroup type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `changes: list[airbyte_agent_sdk.connectors.shopify.models.InventoryAdjustmentGroupChangesItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reason: str | None`
    :   The type of the None singleton.

    `reference_document_uri: str | None`
    :   The type of the None singleton.

<a id="InventoryAdjustmentGroupChangesItem"></a>

`InventoryAdjustmentGroupChangesItem(**data: Any)`
:   Nested schema for InventoryAdjustmentGroup.changes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `delta: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `quantity_after_change: int | None`
    :   The type of the None singleton.

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

<a id="InventorySetQuantitiesParams"></a>

`InventorySetQuantitiesParams(**data: Any)`
:   Parameters for setting absolute inventory quantities.
    Requires a reason and reference document URI.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `input: airbyte_agent_sdk.connectors.shopify.models.InventorySetQuantitiesParamsInput`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InventorySetQuantitiesParamsInput"></a>

`InventorySetQuantitiesParamsInput(**data: Any)`
:   Nested schema for InventorySetQuantitiesParams.input
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   Quantity name (e.g. 'available', 'on_hand')

    `quantities: list[airbyte_agent_sdk.connectors.shopify.models.InventorySetQuantitiesParamsInputQuantitiesItem]`
    :   Quantities to set

    `reason: str`
    :   Reason for the adjustment (e.g. 'correction', 'other')

    `reference_document_uri: str | None`
    :   URI for the reference document

<a id="InventorySetQuantitiesParamsInputQuantitiesItem"></a>

`InventorySetQuantitiesParamsInputQuantitiesItem(**data: Any)`
:   Nested schema for InventorySetQuantitiesParamsInput.quantities_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `inventory_item_id: str`
    :   GraphQL GID of the inventory item

    `location_id: str`
    :   GraphQL GID of the location

    `model_config`
    :   The type of the None singleton.

    `quantity: int`
    :   Absolute quantity to set

<a id="InventorySetQuantitiesPayload"></a>

`InventorySetQuantitiesPayload(**data: Any)`
:   InventorySetQuantitiesPayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `inventory_adjustment_group: airbyte_agent_sdk.connectors.shopify.models.InventoryAdjustmentGroup | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="InventorySetQuantitiesResponse"></a>

`InventorySetQuantitiesResponse(**data: Any)`
:   InventorySetQuantitiesResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.InventorySetQuantitiesResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InventorySetQuantitiesResponseData"></a>

`InventorySetQuantitiesResponseData(**data: Any)`
:   Nested schema for InventorySetQuantitiesResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `inventory_set_quantities: airbyte_agent_sdk.connectors.shopify.models.InventorySetQuantitiesPayload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

<a id="MetafieldArticlesListResultMeta"></a>

`MetafieldArticlesListResultMeta(**data: Any)`
:   Metadata for metafield_articles.Action.LIST operation
    
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

<a id="MetafieldArticlesSearchData"></a>

`MetafieldArticlesSearchData(**data: Any)`
:   Search result data for metafield_articles entity.
    
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
    :   Identifier key for the metafield

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   Container namespace for the metafield

    `owner_id: int | None`
    :   Identifier of the article that owns this metafield

    `owner_resource: str | None`
    :   Resource type that owns this metafield (e.g. `article`)

    `type_: str | None`
    :   The metafield's information type

    `updated_at: str | None`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str | None`
    :   The metafield value

<a id="MetafieldBlogsListResultMeta"></a>

`MetafieldBlogsListResultMeta(**data: Any)`
:   Metadata for metafield_blogs.Action.LIST operation
    
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

<a id="MetafieldBlogsSearchData"></a>

`MetafieldBlogsSearchData(**data: Any)`
:   Search result data for metafield_blogs entity.
    
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
    :   Identifier key for the metafield

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   Container namespace for the metafield

    `owner_id: int | None`
    :   Identifier of the blog that owns this metafield

    `owner_resource: str | None`
    :   Resource type that owns this metafield (e.g. `blog`)

    `type_: str | None`
    :   The metafield's information type

    `updated_at: str | None`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str | None`
    :   The metafield value

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

<a id="MetafieldDeleteParams"></a>

`MetafieldDeleteParams(**data: Any)`
:   Parameters for deleting metafields. Identify each metafield by
    ownerId + namespace + key.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metafields: list[airbyte_agent_sdk.connectors.shopify.models.MetafieldDeleteParamsMetafieldsItem]`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="MetafieldDeleteParamsMetafieldsItem"></a>

`MetafieldDeleteParamsMetafieldsItem(**data: Any)`
:   Nested schema for MetafieldDeleteParams.metafields_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `key: str`
    :   Metafield key (e.g. 'color')

    `model_config`
    :   The type of the None singleton.

    `namespace: str`
    :   Metafield namespace (e.g. 'custom')

    `owner_id: str`
    :   GraphQL GID of the owner resource (e.g. gid://shopify/Product/123)

<a id="MetafieldDeletePayload"></a>

`MetafieldDeletePayload(**data: Any)`
:   MetafieldDeletePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `deleted_metafields: list[airbyte_agent_sdk.connectors.shopify.models.MetafieldDeletePayloadDeletedmetafieldsItem | None] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="MetafieldDeletePayloadDeletedmetafieldsItem"></a>

`MetafieldDeletePayloadDeletedmetafieldsItem(**data: Any)`
:   Nested schema for MetafieldDeletePayload.deletedMetafields_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `key: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   The type of the None singleton.

    `owner_id: str | None`
    :   The type of the None singleton.

<a id="MetafieldDeleteResponse"></a>

`MetafieldDeleteResponse(**data: Any)`
:   MetafieldDeleteResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.MetafieldDeleteResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="MetafieldDeleteResponseData"></a>

`MetafieldDeleteResponseData(**data: Any)`
:   Nested schema for MetafieldDeleteResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metafields_delete: airbyte_agent_sdk.connectors.shopify.models.MetafieldDeletePayload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

<a id="MetafieldPagesListResultMeta"></a>

`MetafieldPagesListResultMeta(**data: Any)`
:   Metadata for metafield_pages.Action.LIST operation
    
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

<a id="MetafieldPagesSearchData"></a>

`MetafieldPagesSearchData(**data: Any)`
:   Search result data for metafield_pages entity.
    
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
    :   Identifier key for the metafield

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   Container namespace for the metafield

    `owner_id: int | None`
    :   Identifier of the page that owns this metafield

    `owner_resource: str | None`
    :   Resource type that owns this metafield (e.g. `page`)

    `type_: str | None`
    :   The metafield's information type

    `updated_at: str | None`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str | None`
    :   The metafield value

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

<a id="MetafieldsSetParams"></a>

`MetafieldsSetParams(**data: Any)`
:   Parameters for setting (creating or updating) metafields atomically.
    Supports up to 25 metafields per call.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metafields: list[airbyte_agent_sdk.connectors.shopify.models.MetafieldsSetParamsMetafieldsItem]`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="MetafieldsSetParamsMetafieldsItem"></a>

`MetafieldsSetParamsMetafieldsItem(**data: Any)`
:   Nested schema for MetafieldsSetParams.metafields_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `key: str`
    :   Metafield key (e.g. 'color')

    `model_config`
    :   The type of the None singleton.

    `namespace: str`
    :   Metafield namespace (e.g. 'custom')

    `owner_id: str`
    :   GraphQL GID of the owner resource (e.g. gid://shopify/Product/123)

    `type_: str`
    :   Metafield type (e.g. 'single_line_text_field', 'number_integer', 'boolean')

    `value: str`
    :   Metafield value

<a id="MetafieldsSetPayload"></a>

`MetafieldsSetPayload(**data: Any)`
:   MetafieldsSetPayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metafields: list[airbyte_agent_sdk.connectors.shopify.models.MetafieldsSetPayloadMetafieldsItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="MetafieldsSetPayloadMetafieldsItem"></a>

`MetafieldsSetPayloadMetafieldsItem(**data: Any)`
:   Nested schema for MetafieldsSetPayload.metafields_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `key: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `namespace: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="MetafieldsSetResponse"></a>

`MetafieldsSetResponse(**data: Any)`
:   MetafieldsSetResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.MetafieldsSetResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="MetafieldsSetResponseData"></a>

`MetafieldsSetResponseData(**data: Any)`
:   Nested schema for MetafieldsSetResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metafields_set: airbyte_agent_sdk.connectors.shopify.models.MetafieldsSetPayload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

<a id="OrderCancelParams"></a>

`OrderCancelParams(**data: Any)`
:   Parameters for cancelling an order. This action is irreversible.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `notify_customer: bool | None`
    :   The type of the None singleton.

    `order_id: str`
    :   The type of the None singleton.

    `reason: str`
    :   The type of the None singleton.

    `refund: bool | None`
    :   The type of the None singleton.

    `restock: bool`
    :   The type of the None singleton.

    `staff_note: str | None`
    :   The type of the None singleton.

<a id="OrderCancelPayload"></a>

`OrderCancelPayload(**data: Any)`
:   OrderCancelPayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `job: airbyte_agent_sdk.connectors.shopify.models.OrderCancelPayloadJob | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `order_cancel_user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="OrderCancelPayloadJob"></a>

`OrderCancelPayloadJob(**data: Any)`
:   Nested schema for OrderCancelPayload.job
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderCancelResponse"></a>

`OrderCancelResponse(**data: Any)`
:   OrderCancelResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.OrderCancelResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderCancelResponseData"></a>

`OrderCancelResponseData(**data: Any)`
:   Nested schema for OrderCancelResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `order_cancel: airbyte_agent_sdk.connectors.shopify.models.OrderCancelPayload | None`
    :   The type of the None singleton.

<a id="OrderCreateParams"></a>

`OrderCreateParams(**data: Any)`
:   Parameters for creating an order.
    Use line items with variantId and quantity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `options: airbyte_agent_sdk.connectors.shopify.models.OrderCreateParamsOptions | None`
    :   The type of the None singleton.

    `order: airbyte_agent_sdk.connectors.shopify.models.OrderCreateParamsOrder`
    :   The type of the None singleton.

<a id="OrderCreateParamsOptions"></a>

`OrderCreateParamsOptions(**data: Any)`
:   OrderCreateOptionsInput
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `inventory_behaviour: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderCreateParamsOrder"></a>

`OrderCreateParamsOrder(**data: Any)`
:   OrderCreateOrderInput object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `customer_id: str | None`
    :   GraphQL GID of the customer

    `email: str | None`
    :   Customer email

    `line_items: list[airbyte_agent_sdk.connectors.shopify.models.OrderCreateParamsOrderLineitemsItem]`
    :   Line items for the order

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   Order note

    `shipping_address: airbyte_agent_sdk.connectors.shopify.models.OrderCreateParamsOrderShippingaddress | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   Order tags

<a id="OrderCreateParamsOrderLineitemsItem"></a>

`OrderCreateParamsOrderLineitemsItem(**data: Any)`
:   Nested schema for OrderCreateParamsOrder.lineItems_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `price_set: airbyte_agent_sdk.connectors.shopify.models.OrderCreateParamsOrderLineitemsItemPriceset | None`
    :   The type of the None singleton.

    `quantity: int | None`
    :   Quantity to order

    `title: str | None`
    :   Custom title (for custom line items without a variant)

    `variant_id: str | None`
    :   GraphQL GID of the product variant

<a id="OrderCreateParamsOrderLineitemsItemPriceset"></a>

`OrderCreateParamsOrderLineitemsItemPriceset(**data: Any)`
:   Nested schema for OrderCreateParamsOrderLineitemsItem.priceSet
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `shop_money: airbyte_agent_sdk.connectors.shopify.models.OrderCreateParamsOrderLineitemsItemPricesetShopmoney | None`
    :   The type of the None singleton.

<a id="OrderCreateParamsOrderLineitemsItemPricesetShopmoney"></a>

`OrderCreateParamsOrderLineitemsItemPricesetShopmoney(**data: Any)`
:   Nested schema for OrderCreateParamsOrderLineitemsItemPriceset.shopMoney
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   The type of the None singleton.

    `currency_code: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderCreateParamsOrderShippingaddress"></a>

`OrderCreateParamsOrderShippingaddress(**data: Any)`
:   Nested schema for OrderCreateParamsOrder.shippingAddress
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address1: str | None`
    :   The type of the None singleton.

    `city: str | None`
    :   The type of the None singleton.

    `country_code: str | None`
    :   The type of the None singleton.

    `first_name: str | None`
    :   The type of the None singleton.

    `last_name: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `province_code: str | None`
    :   The type of the None singleton.

    `zip: str | None`
    :   The type of the None singleton.

<a id="OrderCreatePayload"></a>

`OrderCreatePayload(**data: Any)`
:   OrderCreatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `order: airbyte_agent_sdk.connectors.shopify.models.GraphQLOrder | None`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
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

<a id="OrderMutationResponse"></a>

`OrderMutationResponse(**data: Any)`
:   OrderMutationResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.OrderMutationResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderMutationResponseData"></a>

`OrderMutationResponseData(**data: Any)`
:   Nested schema for OrderMutationResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `order_create: airbyte_agent_sdk.connectors.shopify.models.OrderCreatePayload | None`
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

<a id="OrderUpdateParams"></a>

`OrderUpdateParams(**data: Any)`
:   Parameters for updating an order. The input.id field is required.
    For line item changes, use orderEditBegin/orderEditCommit instead.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `input: airbyte_agent_sdk.connectors.shopify.models.OrderUpdateParamsInput`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderUpdateParamsInput"></a>

`OrderUpdateParamsInput(**data: Any)`
:   Nested schema for OrderUpdateParams.input
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | None`
    :   Customer email

    `id: str`
    :   The GraphQL GID of the order (e.g. gid://shopify/Order/123)

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   Order note

    `shipping_address: airbyte_agent_sdk.connectors.shopify.models.OrderUpdateParamsInputShippingaddress | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   Order tags

<a id="OrderUpdateParamsInputShippingaddress"></a>

`OrderUpdateParamsInputShippingaddress(**data: Any)`
:   Nested schema for OrderUpdateParamsInput.shippingAddress
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address1: str | None`
    :   The type of the None singleton.

    `city: str | None`
    :   The type of the None singleton.

    `country_code: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `province_code: str | None`
    :   The type of the None singleton.

    `zip: str | None`
    :   The type of the None singleton.

<a id="OrderUpdatePayload"></a>

`OrderUpdatePayload(**data: Any)`
:   OrderUpdatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `order: airbyte_agent_sdk.connectors.shopify.models.OrderUpdatePayloadOrder | None`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="OrderUpdatePayloadOrder"></a>

`OrderUpdatePayloadOrder(**data: Any)`
:   Nested schema for OrderUpdatePayload.order
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `display_financial_status: str | None`
    :   The type of the None singleton.

    `display_fulfillment_status: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `note: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

<a id="OrderUpdateResponse"></a>

`OrderUpdateResponse(**data: Any)`
:   OrderUpdateResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.OrderUpdateResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderUpdateResponseData"></a>

`OrderUpdateResponseData(**data: Any)`
:   Nested schema for OrderUpdateResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `order_update: airbyte_agent_sdk.connectors.shopify.models.OrderUpdatePayload | None`
    :   The type of the None singleton.

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

    `cancel_reason: str | None`
    :   Reason the order was cancelled, if applicable

    `cancelled_at: str | None`
    :   ISO 8601 timestamp when the order was cancelled, if applicable

    `closed_at: str | None`
    :   ISO 8601 timestamp when the order was closed, if applicable

    `created_at: str | None`
    :   ISO 8601 timestamp when the order was created

    `currency: str | None`
    :   ISO 4217 currency code for the order totals

    `email: str | None`
    :   Email address associated with the order

    `financial_status: str | None`
    :   Payment status of the order (e.g. `paid`, `pending`, `refunded`, `partially_refunded`)

    `fulfillment_status: str | None`
    :   Fulfillment status of the order (e.g. `fulfilled`, `partial`, `null` for unfulfilled)

    `id: int | None`
    :   Unique identifier for the order

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Shopify-assigned display name for the order (e.g. `#1001`)

    `note: str | None`
    :   Merchant-provided note on the order

    `order_number: int | None`
    :   Sequential order number displayed in the Shopify admin

    `phone: str | None`
    :   Phone number associated with the order

    `processed_at: str | None`
    :   ISO 8601 timestamp when the order was processed

    `subtotal_price: str | None`
    :   Subtotal of the order before shipping and taxes

    `tags: str | None`
    :   Comma-separated tags attached to the order

    `total_discounts: str | None`
    :   Total discount amount applied to the order

    `total_price: str | None`
    :   Total price of the order including taxes and discounts

    `total_tax: str | None`
    :   Total tax amount applied to the order

    `total_weight: int | None`
    :   Total weight of all items in the order, in grams

    `updated_at: str | None`
    :   ISO 8601 timestamp when the order was last updated

<a id="Page"></a>

`Page(**data: Any)`
:   A static page on the store
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | None`
    :   The type of the None singleton.

    `author: str | None`
    :   The type of the None singleton.

    `body_html: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `handle: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `published_at: str | None`
    :   The type of the None singleton.

    `template_suffix: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="PageCreateParams"></a>

`PageCreateParams(**data: Any)`
:   Parameters for creating a page.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page: airbyte_agent_sdk.connectors.shopify.models.PageCreateParamsPage`
    :   The type of the None singleton.

<a id="PageCreateParamsPage"></a>

`PageCreateParamsPage(**data: Any)`
:   Nested schema for PageCreateParams.page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body: str | None`
    :   Page body content (HTML)

    `handle: str | None`
    :   URL handle for the page

    `is_published: bool | None`
    :   Whether the page is published

    `model_config`
    :   The type of the None singleton.

    `title: str`
    :   Page title

<a id="PageCreatePayload"></a>

`PageCreatePayload(**data: Any)`
:   PageCreatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page: airbyte_agent_sdk.connectors.shopify.models.GraphQLPage | None`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="PageDeleteParams"></a>

`PageDeleteParams(**data: Any)`
:   Parameters for deleting a page.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="PageDeletePayload"></a>

`PageDeletePayload(**data: Any)`
:   PageDeletePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `deleted_page_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="PageDeleteResponse"></a>

`PageDeleteResponse(**data: Any)`
:   PageDeleteResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.PageDeleteResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="PageDeleteResponseData"></a>

`PageDeleteResponseData(**data: Any)`
:   Nested schema for PageDeleteResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_delete: airbyte_agent_sdk.connectors.shopify.models.PageDeletePayload | None`
    :   The type of the None singleton.

<a id="PageList"></a>

`PageList(**data: Any)`
:   PageList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `pages: list[airbyte_agent_sdk.connectors.shopify.models.Page] | None`
    :   The type of the None singleton.

<a id="PageMutationResponse"></a>

`PageMutationResponse(**data: Any)`
:   PageMutationResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.PageMutationResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="PageMutationResponseData"></a>

`PageMutationResponseData(**data: Any)`
:   Nested schema for PageMutationResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_create: airbyte_agent_sdk.connectors.shopify.models.PageCreatePayload | None`
    :   The type of the None singleton.

    `page_update: airbyte_agent_sdk.connectors.shopify.models.PageUpdatePayload | None`
    :   The type of the None singleton.

<a id="PageUpdateParams"></a>

`PageUpdateParams(**data: Any)`
:   Parameters for updating a page.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `page: airbyte_agent_sdk.connectors.shopify.models.PageUpdateParamsPage`
    :   The type of the None singleton.

<a id="PageUpdateParamsPage"></a>

`PageUpdateParamsPage(**data: Any)`
:   Nested schema for PageUpdateParams.page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body: str | None`
    :   The type of the None singleton.

    `handle: str | None`
    :   The type of the None singleton.

    `is_published: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="PageUpdatePayload"></a>

`PageUpdatePayload(**data: Any)`
:   PageUpdatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page: airbyte_agent_sdk.connectors.shopify.models.GraphQLPage | None`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="PagesListResultMeta"></a>

`PagesListResultMeta(**data: Any)`
:   Metadata for pages.Action.LIST operation
    
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

<a id="PagesSearchData"></a>

`PagesSearchData(**data: Any)`
:   Search result data for pages entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: str | None`
    :   Name of the page author

    `body_html: str | None`
    :   HTML content of the page

    `created_at: str | None`
    :   ISO 8601 timestamp when the page was created

    `handle: str | None`
    :   URL-friendly handle for the page

    `id: int | None`
    :   Unique identifier for the page

    `model_config`
    :   The type of the None singleton.

    `published_at: str | None`
    :   ISO 8601 timestamp when the page was published

    `title: str | None`
    :   Title of the page

    `updated_at: str | None`
    :   ISO 8601 timestamp when the page was last updated

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

<a id="ProductCreateParams"></a>

`ProductCreateParams(**data: Any)`
:   Parameters for creating a product.
    Creates the product with a default variant.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `media: list[airbyte_agent_sdk.connectors.shopify.models.ProductCreateParamsMediaItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `product: airbyte_agent_sdk.connectors.shopify.models.ProductCreateParamsProduct`
    :   The type of the None singleton.

<a id="ProductCreateParamsMediaItem"></a>

`ProductCreateParamsMediaItem(**data: Any)`
:   Nested schema for ProductCreateParams.media_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `media_content_type: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `original_source: str | None`
    :   URL of the media

<a id="ProductCreateParamsProduct"></a>

`ProductCreateParamsProduct(**data: Any)`
:   ProductCreateInput object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description_html: str | None`
    :   Product description in HTML

    `model_config`
    :   The type of the None singleton.

    `product_type: str | None`
    :   Product type

    `status: str | None`
    :   Product status (ACTIVE, ARCHIVED, DRAFT)

    `tags: list[str] | None`
    :   Tags for the product

    `title: str`
    :   Product title

    `vendor: str | None`
    :   Product vendor

<a id="ProductCreatePayload"></a>

`ProductCreatePayload(**data: Any)`
:   ProductCreatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `product: airbyte_agent_sdk.connectors.shopify.models.GraphQLProduct | None`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="ProductDeleteParams"></a>

`ProductDeleteParams(**data: Any)`
:   Parameters for deleting a product. This action is irreversible.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `input: airbyte_agent_sdk.connectors.shopify.models.ProductDeleteParamsInput`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProductDeleteParamsInput"></a>

`ProductDeleteParamsInput(**data: Any)`
:   Nested schema for ProductDeleteParams.input
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The GraphQL GID of the product to delete (e.g. gid://shopify/Product/123)

    `model_config`
    :   The type of the None singleton.

<a id="ProductDeletePayload"></a>

`ProductDeletePayload(**data: Any)`
:   ProductDeletePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `deleted_product_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="ProductDeleteResponse"></a>

`ProductDeleteResponse(**data: Any)`
:   ProductDeleteResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.ProductDeleteResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProductDeleteResponseData"></a>

`ProductDeleteResponseData(**data: Any)`
:   Nested schema for ProductDeleteResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `product_delete: airbyte_agent_sdk.connectors.shopify.models.ProductDeletePayload | None`
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

<a id="ProductMutationResponse"></a>

`ProductMutationResponse(**data: Any)`
:   ProductMutationResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.ProductMutationResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProductMutationResponseData"></a>

`ProductMutationResponseData(**data: Any)`
:   Nested schema for ProductMutationResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `product_create: airbyte_agent_sdk.connectors.shopify.models.ProductCreatePayload | None`
    :   The type of the None singleton.

    `product_update: airbyte_agent_sdk.connectors.shopify.models.ProductUpdatePayload | None`
    :   The type of the None singleton.

<a id="ProductUpdateParams"></a>

`ProductUpdateParams(**data: Any)`
:   Parameters for updating a product. The product.id field is required.
    All other fields are optional for partial updates.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `product: airbyte_agent_sdk.connectors.shopify.models.ProductUpdateParamsProduct`
    :   The type of the None singleton.

<a id="ProductUpdateParamsProduct"></a>

`ProductUpdateParamsProduct(**data: Any)`
:   ProductUpdateInput object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description_html: str | None`
    :   Product description in HTML

    `id: str`
    :   The GraphQL GID of the product (e.g. gid://shopify/Product/123)

    `model_config`
    :   The type of the None singleton.

    `product_type: str | None`
    :   Product type

    `status: str | None`
    :   Product status

    `tags: list[str] | None`
    :   Tags for the product

    `title: str | None`
    :   Product title

    `vendor: str | None`
    :   Product vendor

<a id="ProductUpdatePayload"></a>

`ProductUpdatePayload(**data: Any)`
:   ProductUpdatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `product: airbyte_agent_sdk.connectors.shopify.models.GraphQLProduct | None`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
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

<a id="ProductVariantsBulkCreatePayload"></a>

`ProductVariantsBulkCreatePayload(**data: Any)`
:   ProductVariantsBulkCreatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `product_variants: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLProductVariant] | None`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="ProductVariantsBulkDeletePayload"></a>

`ProductVariantsBulkDeletePayload(**data: Any)`
:   ProductVariantsBulkDeletePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `product: airbyte_agent_sdk.connectors.shopify.models.ProductVariantsBulkDeletePayloadProduct | None`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="ProductVariantsBulkDeletePayloadProduct"></a>

`ProductVariantsBulkDeletePayloadProduct(**data: Any)`
:   Nested schema for ProductVariantsBulkDeletePayload.product
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="ProductVariantsBulkUpdatePayload"></a>

`ProductVariantsBulkUpdatePayload(**data: Any)`
:   ProductVariantsBulkUpdatePayload type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `product_variants: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLProductVariant] | None`
    :   The type of the None singleton.

    `user_errors: list[airbyte_agent_sdk.connectors.shopify.models.GraphQLUserError] | None`
    :   The type of the None singleton.

<a id="ProductVariantsCreateParams"></a>

`ProductVariantsCreateParams(**data: Any)`
:   Parameters for bulk creating product variants.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `product_id: str`
    :   The type of the None singleton.

    `variants: list[ProductVariantsCreateParamsVariantsItem]`
    :   The type of the None singleton.

<a id="ProductVariantsDeleteParams"></a>

`ProductVariantsDeleteParams(**data: Any)`
:   Parameters for bulk deleting product variants. Cannot delete the last variant.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `product_id: str`
    :   The type of the None singleton.

    `variants_ids: list[str]`
    :   The type of the None singleton.

<a id="ProductVariantsDeleteResponse"></a>

`ProductVariantsDeleteResponse(**data: Any)`
:   ProductVariantsDeleteResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.ProductVariantsDeleteResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProductVariantsDeleteResponseData"></a>

`ProductVariantsDeleteResponseData(**data: Any)`
:   Nested schema for ProductVariantsDeleteResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `product_variants_bulk_delete: airbyte_agent_sdk.connectors.shopify.models.ProductVariantsBulkDeletePayload | None`
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

<a id="ProductVariantsMutationResponse"></a>

`ProductVariantsMutationResponse(**data: Any)`
:   ProductVariantsMutationResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.shopify.models.ProductVariantsMutationResponseData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProductVariantsMutationResponseData"></a>

`ProductVariantsMutationResponseData(**data: Any)`
:   Nested schema for ProductVariantsMutationResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `product_variants_bulk_create: airbyte_agent_sdk.connectors.shopify.models.ProductVariantsBulkCreatePayload | None`
    :   The type of the None singleton.

    `product_variants_bulk_update: airbyte_agent_sdk.connectors.shopify.models.ProductVariantsBulkUpdatePayload | None`
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

<a id="ProductVariantsUpdateParams"></a>

`ProductVariantsUpdateParams(**data: Any)`
:   Parameters for bulk updating product variants.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `product_id: str`
    :   The type of the None singleton.

    `variants: list[ProductVariantsUpdateParamsVariantsItem]`
    :   The type of the None singleton.

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

<a id="ProductsSearchData"></a>

`ProductsSearchData(**data: Any)`
:   Search result data for products entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body_html: str | None`
    :   Product description in HTML

    `created_at: str | None`
    :   ISO 8601 timestamp when the product was created

    `handle: str | None`
    :   URL-friendly handle for the product

    `id: int | None`
    :   Unique identifier for the product

    `model_config`
    :   The type of the None singleton.

    `product_type: str | None`
    :   Product type used for categorization

    `published_at: str | None`
    :   ISO 8601 timestamp when the product was published

    `published_scope: str | None`
    :   Publishing scope (`web` or `global`)

    `status: str | None`
    :   Product status (`active`, `archived`, or `draft`)

    `tags: str | None`
    :   Comma-separated tags attached to the product

    `title: str | None`
    :   Product title

    `updated_at: str | None`
    :   ISO 8601 timestamp when the product was last updated

    `vendor: str | None`
    :   Product vendor or manufacturer

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

<a id="ShopifyAccessTokenAuthenticationAuthConfig"></a>

`ShopifyAccessTokenAuthenticationAuthConfig(**data: Any)`
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
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Article], ArticlesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[BalanceTransaction], BalanceTransactionsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Blog], BlogsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Collect], CollectsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Country], CountriesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[CustomCollection], CustomCollectionsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[CustomerAddress], CustomerAddressListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Customer], CustomersListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[DiscountCode], DiscountCodesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Dispute], DisputesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[DraftOrder], DraftOrdersListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[FulfillmentOrder], FulfillmentOrdersListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Fulfillment], FulfillmentsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[InventoryItem], InventoryItemsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[InventoryLevel], InventoryLevelsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Location], LocationsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldArticlesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldBlogsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldCustomersListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldDraftOrdersListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldLocationsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldOrdersListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldPagesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldProductImagesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldProductVariantsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldProductsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldShopsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldSmartCollectionsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Order], OrdersListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Page], PagesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[PriceRule], PriceRulesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[ProductImage], ProductImagesListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[ProductVariant], ProductVariantsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Product], ProductsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Refund], OrderRefundsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[SmartCollection], SmartCollectionsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[TenderTransaction], TenderTransactionsListResultMeta]
    * airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Transaction], TransactionsListResultMeta]

    ### Class variables

    `meta: ~S | None`
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

`ShopifyExecuteResultWithMeta[list[Article], ArticlesListResultMeta](**data: Any)`
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

<a id="ArticlesListResult"></a>

`ArticlesListResult(**data: Any)`
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

`ShopifyExecuteResultWithMeta[list[BalanceTransaction], BalanceTransactionsListResultMeta](**data: Any)`
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

<a id="BalanceTransactionsListResult"></a>

`BalanceTransactionsListResult(**data: Any)`
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

`ShopifyExecuteResultWithMeta[list[Blog], BlogsListResultMeta](**data: Any)`
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

<a id="BlogsListResult"></a>

`BlogsListResult(**data: Any)`
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

`ShopifyExecuteResultWithMeta[list[Dispute], DisputesListResultMeta](**data: Any)`
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

<a id="DisputesListResult"></a>

`DisputesListResult(**data: Any)`
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

`ShopifyExecuteResultWithMeta[list[Metafield], MetafieldArticlesListResultMeta](**data: Any)`
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

<a id="MetafieldArticlesListResult"></a>

`MetafieldArticlesListResult(**data: Any)`
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

`ShopifyExecuteResultWithMeta[list[Metafield], MetafieldBlogsListResultMeta](**data: Any)`
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

<a id="MetafieldBlogsListResult"></a>

`MetafieldBlogsListResult(**data: Any)`
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

`ShopifyExecuteResultWithMeta[list[Metafield], MetafieldPagesListResultMeta](**data: Any)`
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

<a id="MetafieldPagesListResult"></a>

`MetafieldPagesListResult(**data: Any)`
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

`ShopifyExecuteResultWithMeta[list[Page], PagesListResultMeta](**data: Any)`
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

<a id="PagesListResult"></a>

`PagesListResult(**data: Any)`
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

<a id="ShopifyOauth2AuthConfig"></a>

`ShopifyOauth2AuthConfig(**data: Any)`
:   OAuth2
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   Your Shopify OAuth2 access token

    `client_id: str | None`
    :   Your Shopify OAuth2 application client ID

    `client_secret: str | None`
    :   Your Shopify OAuth2 application client secret

    `model_config`
    :   The type of the None singleton.

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