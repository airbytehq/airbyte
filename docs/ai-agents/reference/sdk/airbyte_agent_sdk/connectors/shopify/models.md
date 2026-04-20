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

`AbandonedCheckout(**data: Any)`
:   An abandoned checkout
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `abandoned_checkout_url: str | Any | None`
    :   The type of the None singleton.

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `billing_address: Any`
    :   The type of the None singleton.

    `buyer_accepts_marketing: bool | Any | None`
    :   The type of the None singleton.

    `buyer_accepts_sms_marketing: bool | Any | None`
    :   The type of the None singleton.

    `cart_token: str | Any | None`
    :   The type of the None singleton.

    `closed_at: str | Any | None`
    :   The type of the None singleton.

    `completed_at: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `customer: Any`
    :   The type of the None singleton.

    `customer_locale: str | Any | None`
    :   The type of the None singleton.

    `device_id: int | Any | None`
    :   The type of the None singleton.

    `discount_codes: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `gateway: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `landing_site: str | Any | None`
    :   The type of the None singleton.

    `line_items: list[airbyte_agent_sdk.connectors.shopify.models.LineItem] | Any | None`
    :   The type of the None singleton.

    `location_id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `note: str | Any | None`
    :   The type of the None singleton.

    `note_attributes: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `presentment_currency: str | Any | None`
    :   The type of the None singleton.

    `referring_site: str | Any | None`
    :   The type of the None singleton.

    `shipping_address: Any`
    :   The type of the None singleton.

    `shipping_lines: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `sms_marketing_phone: str | Any | None`
    :   The type of the None singleton.

    `source: str | Any | None`
    :   The type of the None singleton.

    `source_identifier: str | Any | None`
    :   The type of the None singleton.

    `source_name: str | Any | None`
    :   The type of the None singleton.

    `source_url: str | Any | None`
    :   The type of the None singleton.

    `subtotal_price: str | Any | None`
    :   The type of the None singleton.

    `tax_lines: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `taxes_included: bool | Any | None`
    :   The type of the None singleton.

    `token: str | Any | None`
    :   The type of the None singleton.

    `total_discounts: str | Any | None`
    :   The type of the None singleton.

    `total_duties: str | Any | None`
    :   The type of the None singleton.

    `total_line_items_price: str | Any | None`
    :   The type of the None singleton.

    `total_price: str | Any | None`
    :   The type of the None singleton.

    `total_tax: str | Any | None`
    :   The type of the None singleton.

    `total_weight: int | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `user_id: int | Any | None`
    :   The type of the None singleton.

`AbandonedCheckoutList(**data: Any)`
:   AbandonedCheckoutList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checkouts: list[airbyte_agent_sdk.connectors.shopify.models.AbandonedCheckout] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`AbandonedCheckoutsSearchData(**data: Any)`
:   Search result data for abandoned_checkouts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`Collect(**data: Any)`
:   A collect (product-collection link)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `collection_id: int | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `position: int | Any | None`
    :   The type of the None singleton.

    `product_id: int | Any | None`
    :   The type of the None singleton.

    `sort_value: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`CollectList(**data: Any)`
:   CollectList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `collects: list[airbyte_agent_sdk.connectors.shopify.models.Collect] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`CollectsSearchData(**data: Any)`
:   Search result data for collects entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`CountriesSearchData(**data: Any)`
:   Search result data for countries entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`Country(**data: Any)`
:   A country
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `provinces: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `tax: float | Any | None`
    :   The type of the None singleton.

    `tax_name: str | Any | None`
    :   The type of the None singleton.

`CountryList(**data: Any)`
:   CountryList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `countries: list[airbyte_agent_sdk.connectors.shopify.models.Country] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CustomCollection(**data: Any)`
:   A custom collection
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `body_html: str | Any | None`
    :   The type of the None singleton.

    `handle: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `image: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `products_count: int | Any | None`
    :   The type of the None singleton.

    `published_at: str | Any | None`
    :   The type of the None singleton.

    `published_scope: str | Any | None`
    :   The type of the None singleton.

    `sort_order: str | Any | None`
    :   The type of the None singleton.

    `template_suffix: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`CustomCollectionList(**data: Any)`
:   CustomCollectionList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `custom_collections: list[airbyte_agent_sdk.connectors.shopify.models.CustomCollection] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`CustomCollectionsSearchData(**data: Any)`
:   Search result data for custom_collections entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`Customer(**data: Any)`
:   A Shopify customer
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accepts_marketing: bool | Any | None`
    :   The type of the None singleton.

    `accepts_marketing_updated_at: str | Any | None`
    :   The type of the None singleton.

    `addresses: list[airbyte_agent_sdk.connectors.shopify.models.CustomerAddress] | Any | None`
    :   The type of the None singleton.

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `default_address: Any`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `email_marketing_consent: Any`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `last_order_id: int | Any | None`
    :   The type of the None singleton.

    `last_order_name: str | Any | None`
    :   The type of the None singleton.

    `marketing_opt_in_level: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `multipass_identifier: str | Any | None`
    :   The type of the None singleton.

    `note: str | Any | None`
    :   The type of the None singleton.

    `orders_count: int | Any | None`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `sms_marketing_consent: Any`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

    `tags: str | Any | None`
    :   The type of the None singleton.

    `tax_exempt: bool | Any | None`
    :   The type of the None singleton.

    `tax_exemptions: list[str] | Any | None`
    :   The type of the None singleton.

    `total_spent: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `verified_email: bool | Any | None`
    :   The type of the None singleton.

`CustomerAddress(**data: Any)`
:   A customer address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address1: str | Any | None`
    :   The type of the None singleton.

    `address2: str | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `company: str | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `country_code: str | Any | None`
    :   The type of the None singleton.

    `country_name: str | Any | None`
    :   The type of the None singleton.

    `customer_id: int | Any | None`
    :   The type of the None singleton.

    `default: bool | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `province: str | Any | None`
    :   The type of the None singleton.

    `province_code: str | Any | None`
    :   The type of the None singleton.

    `zip: str | Any | None`
    :   The type of the None singleton.

`CustomerAddressList(**data: Any)`
:   CustomerAddressList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `addresses: list[airbyte_agent_sdk.connectors.shopify.models.CustomerAddress] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`CustomerList(**data: Any)`
:   CustomerList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `customers: list[airbyte_agent_sdk.connectors.shopify.models.Customer] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`CustomersSearchData(**data: Any)`
:   Search result data for customers entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`DiscountCode(**data: Any)`
:   A discount code
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `price_rule_id: int | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `usage_count: int | Any | None`
    :   The type of the None singleton.

`DiscountCodeList(**data: Any)`
:   DiscountCodeList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `discount_codes: list[airbyte_agent_sdk.connectors.shopify.models.DiscountCode] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`DiscountCodesSearchData(**data: Any)`
:   Search result data for discount_codes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`DraftOrder(**data: Any)`
:   A draft order
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `allow_discount_codes_in_checkout: bool | Any | None`
    :   The type of the None singleton.

    `api_client_id: int | Any | None`
    :   The type of the None singleton.

    `applied_discount: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `b2b: bool | Any | None`
    :   The type of the None singleton.

    `billing_address: Any`
    :   The type of the None singleton.

    `completed_at: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `created_on_api_version_handle: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `customer: Any`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `invoice_sent_at: str | Any | None`
    :   The type of the None singleton.

    `invoice_url: str | Any | None`
    :   The type of the None singleton.

    `line_items: list[airbyte_agent_sdk.connectors.shopify.models.LineItem] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `note: str | Any | None`
    :   The type of the None singleton.

    `note_attributes: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `order_id: int | Any | None`
    :   The type of the None singleton.

    `payment_terms: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `shipping_address: Any`
    :   The type of the None singleton.

    `shipping_line: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `subtotal_price: str | Any | None`
    :   The type of the None singleton.

    `tags: str | Any | None`
    :   The type of the None singleton.

    `tax_exempt: bool | Any | None`
    :   The type of the None singleton.

    `tax_lines: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `taxes_included: bool | Any | None`
    :   The type of the None singleton.

    `total_price: str | Any | None`
    :   The type of the None singleton.

    `total_tax: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`DraftOrderList(**data: Any)`
:   DraftOrderList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `draft_orders: list[airbyte_agent_sdk.connectors.shopify.models.DraftOrder] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`DraftOrdersSearchData(**data: Any)`
:   Search result data for draft_orders entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`Fulfillment(**data: Any)`
:   A fulfillment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `line_items: list[airbyte_agent_sdk.connectors.shopify.models.LineItem] | Any | None`
    :   The type of the None singleton.

    `location_id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `order_id: int | Any | None`
    :   The type of the None singleton.

    `origin_address: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `receipt: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `service: str | Any | None`
    :   The type of the None singleton.

    `shipment_status: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `tracking_company: str | Any | None`
    :   The type of the None singleton.

    `tracking_number: str | Any | None`
    :   The type of the None singleton.

    `tracking_numbers: list[str] | Any | None`
    :   The type of the None singleton.

    `tracking_url: str | Any | None`
    :   The type of the None singleton.

    `tracking_urls: list[str] | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`FulfillmentList(**data: Any)`
:   FulfillmentList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `fulfillments: list[airbyte_agent_sdk.connectors.shopify.models.Fulfillment] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`FulfillmentOrder(**data: Any)`
:   A fulfillment order
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assigned_location: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `assigned_location_id: int | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `delivery_method: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `destination: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `fulfill_at: str | Any | None`
    :   The type of the None singleton.

    `fulfill_by: str | Any | None`
    :   The type of the None singleton.

    `fulfillment_holds: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `international_duties: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `line_items: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `merchant_requests: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `order_id: int | Any | None`
    :   The type of the None singleton.

    `request_status: str | Any | None`
    :   The type of the None singleton.

    `shop_id: int | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `supported_actions: list[str] | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`FulfillmentOrderList(**data: Any)`
:   FulfillmentOrderList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `fulfillment_orders: list[airbyte_agent_sdk.connectors.shopify.models.FulfillmentOrder] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`FulfillmentOrdersSearchData(**data: Any)`
:   Search result data for fulfillment_orders entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`FulfillmentsSearchData(**data: Any)`
:   Search result data for fulfillments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`InventoryItem(**data: Any)`
:   An inventory item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `cost: str | Any | None`
    :   The type of the None singleton.

    `country_code_of_origin: str | Any | None`
    :   The type of the None singleton.

    `country_harmonized_system_codes: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `harmonized_system_code: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `province_code_of_origin: str | Any | None`
    :   The type of the None singleton.

    `requires_shipping: bool | Any | None`
    :   The type of the None singleton.

    `sku: str | Any | None`
    :   The type of the None singleton.

    `tracked: bool | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`InventoryItemList(**data: Any)`
:   InventoryItemList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `inventory_items: list[airbyte_agent_sdk.connectors.shopify.models.InventoryItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`InventoryItemsSearchData(**data: Any)`
:   Search result data for inventory_items entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`InventoryLevel(**data: Any)`
:   An inventory level
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `available: int | Any | None`
    :   The type of the None singleton.

    `inventory_item_id: int | Any`
    :   The type of the None singleton.

    `location_id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`InventoryLevelList(**data: Any)`
:   InventoryLevelList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `inventory_levels: list[airbyte_agent_sdk.connectors.shopify.models.InventoryLevel] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`InventoryLevelsSearchData(**data: Any)`
:   Search result data for inventory_levels entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`LineItem(**data: Any)`
:   LineItem type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `attributed_staffs: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `current_quantity: int | Any | None`
    :   The type of the None singleton.

    `discount_allocations: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `duties: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `fulfillable_quantity: int | Any | None`
    :   The type of the None singleton.

    `fulfillment_service: str | Any | None`
    :   The type of the None singleton.

    `fulfillment_status: str | Any | None`
    :   The type of the None singleton.

    `gift_card: bool | Any | None`
    :   The type of the None singleton.

    `grams: int | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `price: str | Any | None`
    :   The type of the None singleton.

    `price_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `product_exists: bool | Any | None`
    :   The type of the None singleton.

    `product_id: int | Any | None`
    :   The type of the None singleton.

    `properties: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `quantity: int | Any | None`
    :   The type of the None singleton.

    `requires_shipping: bool | Any | None`
    :   The type of the None singleton.

    `sku: str | Any | None`
    :   The type of the None singleton.

    `tax_lines: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `taxable: bool | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `total_discount: str | Any | None`
    :   The type of the None singleton.

    `total_discount_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `variant_id: int | Any | None`
    :   The type of the None singleton.

    `variant_inventory_management: str | Any | None`
    :   The type of the None singleton.

    `variant_title: str | Any | None`
    :   The type of the None singleton.

    `vendor: str | Any | None`
    :   The type of the None singleton.

`Location(**data: Any)`
:   A store location
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any | None`
    :   The type of the None singleton.

    `address1: str | Any | None`
    :   The type of the None singleton.

    `address2: str | Any | None`
    :   The type of the None singleton.

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `country_code: str | Any | None`
    :   The type of the None singleton.

    `country_name: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `legacy: bool | Any | None`
    :   The type of the None singleton.

    `localized_country_name: str | Any | None`
    :   The type of the None singleton.

    `localized_province_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `province: str | Any | None`
    :   The type of the None singleton.

    `province_code: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `zip: str | Any | None`
    :   The type of the None singleton.

`LocationList(**data: Any)`
:   LocationList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `locations: list[airbyte_agent_sdk.connectors.shopify.models.Location] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`LocationsSearchData(**data: Any)`
:   Search result data for locations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`MarketingConsent(**data: Any)`
:   MarketingConsent type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `consent_collected_from: str | Any | None`
    :   The type of the None singleton.

    `consent_updated_at: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `opt_in_level: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

`Metafield(**data: Any)`
:   A metafield
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `key: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `namespace: str | Any | None`
    :   The type of the None singleton.

    `owner_id: int | Any | None`
    :   The type of the None singleton.

    `owner_resource: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `value: Any`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`MetafieldCustomersSearchData(**data: Any)`
:   Search result data for metafield_customers entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`MetafieldDraftOrdersSearchData(**data: Any)`
:   Search result data for metafield_draft_orders entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`MetafieldList(**data: Any)`
:   MetafieldList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metafields: list[airbyte_agent_sdk.connectors.shopify.models.Metafield] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`MetafieldLocationsSearchData(**data: Any)`
:   Search result data for metafield_locations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`MetafieldOrdersSearchData(**data: Any)`
:   Search result data for metafield_orders entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`MetafieldProductImagesSearchData(**data: Any)`
:   Search result data for metafield_product_images entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`MetafieldProductVariantsSearchData(**data: Any)`
:   Search result data for metafield_product_variants entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`MetafieldProductsSearchData(**data: Any)`
:   Search result data for metafield_products entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`MetafieldShopsSearchData(**data: Any)`
:   Search result data for metafield_shops entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`MetafieldSmartCollectionsSearchData(**data: Any)`
:   Search result data for metafield_smart_collections entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`Order(**data: Any)`
:   A Shopify order
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `app_id: int | Any | None`
    :   The type of the None singleton.

    `billing_address: Any`
    :   The type of the None singleton.

    `browser_ip: str | Any | None`
    :   The type of the None singleton.

    `buyer_accepts_marketing: bool | Any | None`
    :   The type of the None singleton.

    `cancel_reason: str | Any | None`
    :   The type of the None singleton.

    `cancelled_at: str | Any | None`
    :   The type of the None singleton.

    `cart_token: str | Any | None`
    :   The type of the None singleton.

    `checkout_id: int | Any | None`
    :   The type of the None singleton.

    `checkout_token: str | Any | None`
    :   The type of the None singleton.

    `client_details: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `closed_at: str | Any | None`
    :   The type of the None singleton.

    `company: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `confirmation_number: str | Any | None`
    :   The type of the None singleton.

    `confirmed: bool | Any | None`
    :   The type of the None singleton.

    `contact_email: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `current_subtotal_price: str | Any | None`
    :   The type of the None singleton.

    `current_subtotal_price_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `current_total_additional_fees_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `current_total_discounts: str | Any | None`
    :   The type of the None singleton.

    `current_total_discounts_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `current_total_duties_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `current_total_price: str | Any | None`
    :   The type of the None singleton.

    `current_total_price_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `current_total_tax: str | Any | None`
    :   The type of the None singleton.

    `current_total_tax_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `customer: Any`
    :   The type of the None singleton.

    `customer_locale: str | Any | None`
    :   The type of the None singleton.

    `device_id: int | Any | None`
    :   The type of the None singleton.

    `discount_applications: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `discount_codes: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `duties_included: bool | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `estimated_taxes: bool | Any | None`
    :   The type of the None singleton.

    `financial_status: str | Any | None`
    :   The type of the None singleton.

    `fulfillment_status: str | Any | None`
    :   The type of the None singleton.

    `fulfillments: list[airbyte_agent_sdk.connectors.shopify.models.Fulfillment] | Any | None`
    :   The type of the None singleton.

    `gateway: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `landing_site: str | Any | None`
    :   The type of the None singleton.

    `landing_site_ref: str | Any | None`
    :   The type of the None singleton.

    `line_items: list[airbyte_agent_sdk.connectors.shopify.models.LineItem] | Any | None`
    :   The type of the None singleton.

    `location_id: int | Any | None`
    :   The type of the None singleton.

    `merchant_business_entity_id: str | Any | None`
    :   The type of the None singleton.

    `merchant_of_record_app_id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `note: str | Any | None`
    :   The type of the None singleton.

    `note_attributes: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `number: int | Any | None`
    :   The type of the None singleton.

    `order_number: int | Any | None`
    :   The type of the None singleton.

    `order_status_url: str | Any | None`
    :   The type of the None singleton.

    `original_total_additional_fees_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `original_total_duties_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `payment_gateway_names: list[str] | Any | None`
    :   The type of the None singleton.

    `payment_terms: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `po_number: str | Any | None`
    :   The type of the None singleton.

    `presentment_currency: str | Any | None`
    :   The type of the None singleton.

    `processed_at: str | Any | None`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The type of the None singleton.

    `referring_site: str | Any | None`
    :   The type of the None singleton.

    `refunds: list[airbyte_agent_sdk.connectors.shopify.models.Refund] | Any | None`
    :   The type of the None singleton.

    `shipping_address: Any`
    :   The type of the None singleton.

    `shipping_lines: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `source_identifier: str | Any | None`
    :   The type of the None singleton.

    `source_name: str | Any | None`
    :   The type of the None singleton.

    `source_url: str | Any | None`
    :   The type of the None singleton.

    `subtotal_price: str | Any | None`
    :   The type of the None singleton.

    `subtotal_price_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `tags: str | Any | None`
    :   The type of the None singleton.

    `tax_exempt: bool | Any | None`
    :   The type of the None singleton.

    `tax_lines: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `taxes_included: bool | Any | None`
    :   The type of the None singleton.

    `test: bool | Any | None`
    :   The type of the None singleton.

    `token: str | Any | None`
    :   The type of the None singleton.

    `total_cash_rounding_payment_adjustment_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `total_cash_rounding_refund_adjustment_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `total_discounts: str | Any | None`
    :   The type of the None singleton.

    `total_discounts_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `total_line_items_price: str | Any | None`
    :   The type of the None singleton.

    `total_line_items_price_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `total_outstanding: str | Any | None`
    :   The type of the None singleton.

    `total_price: str | Any | None`
    :   The type of the None singleton.

    `total_price_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `total_shipping_price_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `total_tax: str | Any | None`
    :   The type of the None singleton.

    `total_tax_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `total_tip_received: str | Any | None`
    :   The type of the None singleton.

    `total_weight: int | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `user_id: int | Any | None`
    :   The type of the None singleton.

`OrderAddress(**data: Any)`
:   An address in an order (shipping or billing) - does not have id field
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address1: str | Any | None`
    :   The type of the None singleton.

    `address2: str | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `company: str | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `country_code: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `latitude: float | Any | None`
    :   The type of the None singleton.

    `longitude: float | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `province: str | Any | None`
    :   The type of the None singleton.

    `province_code: str | Any | None`
    :   The type of the None singleton.

    `zip: str | Any | None`
    :   The type of the None singleton.

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

    `orders: list[airbyte_agent_sdk.connectors.shopify.models.Order] | Any`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`OrderRefundsSearchData(**data: Any)`
:   Search result data for order_refunds entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`PriceRule(**data: Any)`
:   A price rule
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `allocation_limit: int | Any | None`
    :   The type of the None singleton.

    `allocation_method: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `customer_segment_prerequisite_ids: list[int] | Any | None`
    :   The type of the None singleton.

    `customer_selection: str | Any | None`
    :   The type of the None singleton.

    `ends_at: str | Any | None`
    :   The type of the None singleton.

    `entitled_collection_ids: list[int] | Any | None`
    :   The type of the None singleton.

    `entitled_country_ids: list[int] | Any | None`
    :   The type of the None singleton.

    `entitled_product_ids: list[int] | Any | None`
    :   The type of the None singleton.

    `entitled_variant_ids: list[int] | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `once_per_customer: bool | Any | None`
    :   The type of the None singleton.

    `prerequisite_collection_ids: list[int] | Any | None`
    :   The type of the None singleton.

    `prerequisite_customer_ids: list[int] | Any | None`
    :   The type of the None singleton.

    `prerequisite_product_ids: list[int] | Any | None`
    :   The type of the None singleton.

    `prerequisite_quantity_range: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `prerequisite_shipping_price_range: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `prerequisite_subtotal_range: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `prerequisite_to_entitlement_purchase: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `prerequisite_to_entitlement_quantity_ratio: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `prerequisite_variant_ids: list[int] | Any | None`
    :   The type of the None singleton.

    `starts_at: str | Any | None`
    :   The type of the None singleton.

    `target_selection: str | Any | None`
    :   The type of the None singleton.

    `target_type: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `usage_limit: int | Any | None`
    :   The type of the None singleton.

    `value: str | Any | None`
    :   The type of the None singleton.

    `value_type: str | Any | None`
    :   The type of the None singleton.

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

    `price_rules: list[airbyte_agent_sdk.connectors.shopify.models.PriceRule] | Any`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`PriceRulesSearchData(**data: Any)`
:   Search result data for price_rules entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`Product(**data: Any)`
:   A Shopify product
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `body_html: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `handle: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `image: Any`
    :   The type of the None singleton.

    `images: list[airbyte_agent_sdk.connectors.shopify.models.ProductImage] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `options: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `product_type: str | Any | None`
    :   The type of the None singleton.

    `published_at: str | Any | None`
    :   The type of the None singleton.

    `published_scope: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `tags: str | Any | None`
    :   The type of the None singleton.

    `template_suffix: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `variants: list[airbyte_agent_sdk.connectors.shopify.models.ProductVariant] | Any | None`
    :   The type of the None singleton.

    `vendor: str | Any | None`
    :   The type of the None singleton.

`ProductImage(**data: Any)`
:   A product image
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `alt: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `height: int | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `position: int | Any | None`
    :   The type of the None singleton.

    `product_id: int | Any | None`
    :   The type of the None singleton.

    `src: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `variant_ids: list[int] | Any | None`
    :   The type of the None singleton.

    `width: int | Any | None`
    :   The type of the None singleton.

`ProductImageList(**data: Any)`
:   ProductImageList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `images: list[airbyte_agent_sdk.connectors.shopify.models.ProductImage] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`ProductImagesSearchData(**data: Any)`
:   Search result data for product_images entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

    `products: list[airbyte_agent_sdk.connectors.shopify.models.Product] | Any`
    :   The type of the None singleton.

`ProductVariant(**data: Any)`
:   A product variant
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `barcode: str | Any | None`
    :   The type of the None singleton.

    `compare_at_price: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `fulfillment_service: str | Any | None`
    :   The type of the None singleton.

    `grams: int | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `image_id: int | Any | None`
    :   The type of the None singleton.

    `inventory_item_id: int | Any | None`
    :   The type of the None singleton.

    `inventory_management: str | Any | None`
    :   The type of the None singleton.

    `inventory_policy: str | Any | None`
    :   The type of the None singleton.

    `inventory_quantity: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `old_inventory_quantity: int | Any | None`
    :   The type of the None singleton.

    `option1: str | Any | None`
    :   The type of the None singleton.

    `option2: str | Any | None`
    :   The type of the None singleton.

    `option3: str | Any | None`
    :   The type of the None singleton.

    `position: int | Any | None`
    :   The type of the None singleton.

    `price: str | Any | None`
    :   The type of the None singleton.

    `product_id: int | Any | None`
    :   The type of the None singleton.

    `requires_shipping: bool | Any | None`
    :   The type of the None singleton.

    `sku: str | Any | None`
    :   The type of the None singleton.

    `taxable: bool | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `weight: float | Any | None`
    :   The type of the None singleton.

    `weight_unit: str | Any | None`
    :   The type of the None singleton.

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

    `variants: list[airbyte_agent_sdk.connectors.shopify.models.ProductVariant] | Any`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`ProductVariantsSearchData(**data: Any)`
:   Search result data for product_variants entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`Refund(**data: Any)`
:   An order refund
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `duties: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `note: str | Any | None`
    :   The type of the None singleton.

    `order_adjustments: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `order_id: int | Any | None`
    :   The type of the None singleton.

    `processed_at: str | Any | None`
    :   The type of the None singleton.

    `refund_line_items: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `refund_shipping_lines: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `restock: bool | Any | None`
    :   The type of the None singleton.

    `return_: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `total_duties_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `transactions: list[airbyte_agent_sdk.connectors.shopify.models.Transaction] | Any | None`
    :   The type of the None singleton.

    `user_id: int | Any | None`
    :   The type of the None singleton.

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

    `refunds: list[airbyte_agent_sdk.connectors.shopify.models.Refund] | Any`
    :   The type of the None singleton.

`Shop(**data: Any)`
:   Shop configuration
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address1: str | Any | None`
    :   The type of the None singleton.

    `address2: str | Any | None`
    :   The type of the None singleton.

    `auto_configure_tax_inclusivity: bool | Any | None`
    :   The type of the None singleton.

    `checkout_api_supported: bool | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `country_code: str | Any | None`
    :   The type of the None singleton.

    `country_name: str | Any | None`
    :   The type of the None singleton.

    `county_taxes: bool | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `customer_email: str | Any | None`
    :   The type of the None singleton.

    `domain: str | Any | None`
    :   The type of the None singleton.

    `eligible_for_payments: bool | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `enabled_presentment_currencies: list[str] | Any | None`
    :   The type of the None singleton.

    `finances: bool | Any | None`
    :   The type of the None singleton.

    `google_apps_domain: str | Any | None`
    :   The type of the None singleton.

    `google_apps_login_enabled: bool | Any | None`
    :   The type of the None singleton.

    `has_discounts: bool | Any | None`
    :   The type of the None singleton.

    `has_gift_cards: bool | Any | None`
    :   The type of the None singleton.

    `has_storefront: bool | Any | None`
    :   The type of the None singleton.

    `iana_timezone: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `latitude: float | Any | None`
    :   The type of the None singleton.

    `longitude: float | Any | None`
    :   The type of the None singleton.

    `marketing_sms_consent_enabled_at_checkout: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `money_format: str | Any | None`
    :   The type of the None singleton.

    `money_in_emails_format: str | Any | None`
    :   The type of the None singleton.

    `money_with_currency_format: str | Any | None`
    :   The type of the None singleton.

    `money_with_currency_in_emails_format: str | Any | None`
    :   The type of the None singleton.

    `multi_location_enabled: bool | Any | None`
    :   The type of the None singleton.

    `myshopify_domain: str | Any | None`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `password_enabled: bool | Any | None`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `plan_display_name: str | Any | None`
    :   The type of the None singleton.

    `plan_name: str | Any | None`
    :   The type of the None singleton.

    `pre_launch_enabled: bool | Any | None`
    :   The type of the None singleton.

    `primary_locale: str | Any | None`
    :   The type of the None singleton.

    `primary_location_id: int | Any | None`
    :   The type of the None singleton.

    `province: str | Any | None`
    :   The type of the None singleton.

    `province_code: str | Any | None`
    :   The type of the None singleton.

    `requires_extra_payments_agreement: bool | Any | None`
    :   The type of the None singleton.

    `setup_required: bool | Any | None`
    :   The type of the None singleton.

    `shop_owner: str | Any | None`
    :   The type of the None singleton.

    `source: str | Any | None`
    :   The type of the None singleton.

    `tax_shipping: bool | Any | None`
    :   The type of the None singleton.

    `taxes_included: bool | Any | None`
    :   The type of the None singleton.

    `timezone: str | Any | None`
    :   The type of the None singleton.

    `transactional_sms_disabled: bool | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `weight_unit: str | Any | None`
    :   The type of the None singleton.

    `zip: str | Any | None`
    :   The type of the None singleton.

`ShopSearchData(**data: Any)`
:   Search result data for shop entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`SmartCollection(**data: Any)`
:   A smart collection
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `body_html: str | Any | None`
    :   The type of the None singleton.

    `disjunctive: bool | Any | None`
    :   The type of the None singleton.

    `handle: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `image: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `products_count: int | Any | None`
    :   The type of the None singleton.

    `published_at: str | Any | None`
    :   The type of the None singleton.

    `published_scope: str | Any | None`
    :   The type of the None singleton.

    `rules: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `sort_order: str | Any | None`
    :   The type of the None singleton.

    `template_suffix: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

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

    `smart_collections: list[airbyte_agent_sdk.connectors.shopify.models.SmartCollection] | Any`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`SmartCollectionsSearchData(**data: Any)`
:   Search result data for smart_collections entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TenderTransaction(**data: Any)`
:   A tender transaction
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `order_id: int | Any | None`
    :   The type of the None singleton.

    `payment_details: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `payment_method: str | Any | None`
    :   The type of the None singleton.

    `processed_at: str | Any | None`
    :   The type of the None singleton.

    `remote_reference: str | Any | None`
    :   The type of the None singleton.

    `test: bool | Any | None`
    :   The type of the None singleton.

    `user_id: int | Any | None`
    :   The type of the None singleton.

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

    `tender_transactions: list[airbyte_agent_sdk.connectors.shopify.models.TenderTransaction] | Any`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.

`TenderTransactionsSearchData(**data: Any)`
:   Search result data for tender_transactions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`Transaction(**data: Any)`
:   An order transaction
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_graphql_api_id: str | Any | None`
    :   The type of the None singleton.

    `amount: str | Any | None`
    :   The type of the None singleton.

    `authorization: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `currency_exchange_adjustment: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `device_id: int | Any | None`
    :   The type of the None singleton.

    `error_code: str | Any | None`
    :   The type of the None singleton.

    `gateway: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `kind: str | Any | None`
    :   The type of the None singleton.

    `location_id: int | Any | None`
    :   The type of the None singleton.

    `manual_payment_gateway: bool | Any | None`
    :   The type of the None singleton.

    `message: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `order_id: int | Any | None`
    :   The type of the None singleton.

    `parent_id: int | Any | None`
    :   The type of the None singleton.

    `payment_id: str | Any | None`
    :   The type of the None singleton.

    `processed_at: str | Any | None`
    :   The type of the None singleton.

    `receipt: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `source_name: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `test: bool | Any | None`
    :   The type of the None singleton.

    `total_unsettled_set: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `user_id: int | Any | None`
    :   The type of the None singleton.

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

    `transactions: list[airbyte_agent_sdk.connectors.shopify.models.Transaction] | Any`
    :   The type of the None singleton.

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

    `next_page_url: str | Any | None`
    :   The type of the None singleton.