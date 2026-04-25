---
id: airbyte_agent_sdk-connectors-woocommerce-models
title: airbyte_agent_sdk.connectors.woocommerce.models
---

Module airbyte_agent_sdk.connectors.woocommerce.models
======================================================
Pydantic models for woocommerce connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

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

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[CouponsSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[CustomersSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[OrderNotesSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[OrdersSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[PaymentGatewaysSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ProductAttributesSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ProductCategoriesSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ProductReviewsSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ProductTagsSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ProductVariationsSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ProductsSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[RefundsSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ShippingMethodsSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ShippingZonesSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[TaxClassesSearchData]
    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[TaxRatesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[CouponsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CouponsSearchResult"></a>

`CouponsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CustomersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[OrderNotesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrderNotesSearchResult"></a>

`OrderNotesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[OrdersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[PaymentGatewaysSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PaymentGatewaysSearchResult"></a>

`PaymentGatewaysSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProductAttributesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductAttributesSearchResult"></a>

`ProductAttributesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProductCategoriesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductCategoriesSearchResult"></a>

`ProductCategoriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProductReviewsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductReviewsSearchResult"></a>

`ProductReviewsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProductTagsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductTagsSearchResult"></a>

`ProductTagsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProductVariationsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductVariationsSearchResult"></a>

`ProductVariationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProductsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[RefundsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="RefundsSearchResult"></a>

`RefundsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ShippingMethodsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ShippingMethodsSearchResult"></a>

`ShippingMethodsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ShippingZonesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ShippingZonesSearchResult"></a>

`ShippingZonesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TaxClassesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TaxClassesSearchResult"></a>

`TaxClassesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TaxRatesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TaxRatesSearchResult"></a>

`TaxRatesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Coupon"></a>

`Coupon(**data: Any)`
:   Coupon type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any | None`
    :   The type of the None singleton.

    `code: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_created_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_expires: str | Any | None`
    :   The type of the None singleton.

    `date_expires_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_modified: str | Any | None`
    :   The type of the None singleton.

    `date_modified_gmt: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `discount_type: str | Any | None`
    :   The type of the None singleton.

    `email_restrictions: list[str | None] | Any | None`
    :   The type of the None singleton.

    `exclude_sale_items: bool | Any | None`
    :   The type of the None singleton.

    `excluded_product_categories: list[int | None] | Any | None`
    :   The type of the None singleton.

    `excluded_product_ids: list[int | None] | Any | None`
    :   The type of the None singleton.

    `free_shipping: bool | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `individual_use: bool | Any | None`
    :   The type of the None singleton.

    `limit_usage_to_x_items: int | Any | None`
    :   The type of the None singleton.

    `maximum_amount: str | Any | None`
    :   The type of the None singleton.

    `meta_data: list[airbyte_agent_sdk.connectors.woocommerce.models.CouponMetaDataItem] | Any | None`
    :   The type of the None singleton.

    `minimum_amount: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `product_categories: list[int | None] | Any | None`
    :   The type of the None singleton.

    `product_ids: list[int | None] | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `usage_count: int | Any | None`
    :   The type of the None singleton.

    `usage_limit: int | Any | None`
    :   The type of the None singleton.

    `usage_limit_per_user: int | Any | None`
    :   The type of the None singleton.

    `used_by: list[str | None] | Any | None`
    :   The type of the None singleton.

<a id="CouponMetaDataItem"></a>

`CouponMetaDataItem(**data: Any)`
:   Nested schema for Coupon.meta_data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `key: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: Any`
    :   The type of the None singleton.

<a id="CouponsListResultMeta"></a>

`CouponsListResultMeta(**data: Any)`
:   Metadata for coupons.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="CouponsSearchData"></a>

`CouponsSearchData(**data: Any)`
:   Search result data for coupons entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   The amount of discount

    `code: str | None`
    :   Coupon code

    `date_created: str | None`
    :   The date the coupon was created

    `date_created_gmt: str | None`
    :   The date the coupon was created, as GMT

    `date_expires: str | None`
    :   The date the coupon expires

    `date_expires_gmt: str | None`
    :   The date the coupon expires, as GMT

    `date_modified: str | None`
    :   The date the coupon was last modified

    `date_modified_gmt: str | None`
    :   The date the coupon was last modified, as GMT

    `description: str | None`
    :   Coupon description

    `discount_type: str | None`
    :   Determines the type of discount

    `email_restrictions: list[typing.Any] | None`
    :   List of email addresses that can use this coupon

    `exclude_sale_items: bool | None`
    :   If true, not applied to sale items

    `excluded_product_categories: list[typing.Any] | None`
    :   Excluded category IDs

    `excluded_product_ids: list[typing.Any] | None`
    :   Excluded product IDs

    `free_shipping: bool | None`
    :   Enables free shipping

    `id: int | None`
    :   Unique identifier

    `individual_use: bool | None`
    :   Can only be used individually

    `limit_usage_to_x_items: int | None`
    :   Max cart items coupon applies to

    `maximum_amount: str | None`
    :   Maximum order amount

    `meta_data: list[typing.Any] | None`
    :   Meta data

    `minimum_amount: str | None`
    :   Minimum order amount

    `model_config`
    :   The type of the None singleton.

    `product_categories: list[typing.Any] | None`
    :   Applicable category IDs

    `product_ids: list[typing.Any] | None`
    :   Applicable product IDs

    `usage_count: int | None`
    :   Times used

    `usage_limit: int | None`
    :   Total usage limit

    `usage_limit_per_user: int | None`
    :   Per-customer usage limit

    `used_by: list[typing.Any] | None`
    :   Users who have used the coupon

<a id="Customer"></a>

`Customer(**data: Any)`
:   Customer type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_url: str | Any | None`
    :   The type of the None singleton.

    `billing: airbyte_agent_sdk.connectors.woocommerce.models.CustomerBilling | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_created_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_modified: str | Any | None`
    :   The type of the None singleton.

    `date_modified_gmt: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `is_paying_customer: bool | Any | None`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `meta_data: list[airbyte_agent_sdk.connectors.woocommerce.models.CustomerMetaDataItem] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `role: str | Any | None`
    :   The type of the None singleton.

    `shipping: airbyte_agent_sdk.connectors.woocommerce.models.CustomerShipping | Any | None`
    :   The type of the None singleton.

    `username: str | Any | None`
    :   The type of the None singleton.

<a id="CustomerBilling"></a>

`CustomerBilling(**data: Any)`
:   List of billing address data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address_1: str | Any | None`
    :   The type of the None singleton.

    `address_2: str | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `company: str | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `postcode: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

<a id="CustomerMetaDataItem"></a>

`CustomerMetaDataItem(**data: Any)`
:   Nested schema for Customer.meta_data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `key: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: str | Any | None`
    :   The type of the None singleton.

<a id="CustomerShipping"></a>

`CustomerShipping(**data: Any)`
:   List of shipping address data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address_1: str | Any | None`
    :   The type of the None singleton.

    `address_2: str | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `company: str | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `postcode: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
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

    `next: str | Any | None`
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

    `avatar_url: str | None`
    :   Avatar URL

    `billing: dict[str, typing.Any] | None`
    :   List of billing address data

    `date_created: str | None`
    :   The date the customer was created, in the site's timezone

    `date_created_gmt: str | None`
    :   The date the customer was created, as GMT

    `date_modified: str | None`
    :   The date the customer was last modified, in the site's timezone

    `date_modified_gmt: str | None`
    :   The date the customer was last modified, as GMT

    `email: str | None`
    :   The email address for the customer

    `first_name: str | None`
    :   Customer first name

    `id: int | None`
    :   Unique identifier for the resource

    `is_paying_customer: bool | None`
    :   Is the customer a paying customer

    `last_name: str | None`
    :   Customer last name

    `meta_data: list[typing.Any] | None`
    :   Meta data

    `model_config`
    :   The type of the None singleton.

    `role: str | None`
    :   Customer role

    `shipping: dict[str, typing.Any] | None`
    :   List of shipping address data

    `username: str | None`
    :   Customer login name

<a id="Order"></a>

`Order(**data: Any)`
:   Order type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billing: airbyte_agent_sdk.connectors.woocommerce.models.OrderBilling | Any | None`
    :   The type of the None singleton.

    `cart_hash: str | Any | None`
    :   The type of the None singleton.

    `cart_tax: str | Any | None`
    :   The type of the None singleton.

    `coupon_lines: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderCouponLinesItem] | Any | None`
    :   The type of the None singleton.

    `created_via: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `currency_symbol: str | Any | None`
    :   The type of the None singleton.

    `customer_id: int | Any | None`
    :   The type of the None singleton.

    `customer_ip_address: str | Any | None`
    :   The type of the None singleton.

    `customer_note: str | Any | None`
    :   The type of the None singleton.

    `customer_user_agent: str | Any | None`
    :   The type of the None singleton.

    `date_completed: str | Any | None`
    :   The type of the None singleton.

    `date_completed_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_created_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_modified: str | Any | None`
    :   The type of the None singleton.

    `date_modified_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_paid: str | Any | None`
    :   The type of the None singleton.

    `date_paid_gmt: str | Any | None`
    :   The type of the None singleton.

    `discount_tax: str | Any | None`
    :   The type of the None singleton.

    `discount_total: str | Any | None`
    :   The type of the None singleton.

    `fee_lines: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderFeeLinesItem] | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `is_editable: bool | Any | None`
    :   The type of the None singleton.

    `line_items: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderLineItemsItem] | Any | None`
    :   The type of the None singleton.

    `meta_data: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderMetaDataItem] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `needs_payment: bool | Any | None`
    :   The type of the None singleton.

    `needs_processing: bool | Any | None`
    :   The type of the None singleton.

    `number: str | Any | None`
    :   The type of the None singleton.

    `order_key: str | Any | None`
    :   The type of the None singleton.

    `parent_id: int | Any | None`
    :   The type of the None singleton.

    `payment_method: str | Any | None`
    :   The type of the None singleton.

    `payment_method_title: str | Any | None`
    :   The type of the None singleton.

    `payment_url: str | Any | None`
    :   The type of the None singleton.

    `prices_include_tax: bool | Any | None`
    :   The type of the None singleton.

    `refunds: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderRefundsItem] | Any | None`
    :   The type of the None singleton.

    `shipping: airbyte_agent_sdk.connectors.woocommerce.models.OrderShipping | Any | None`
    :   The type of the None singleton.

    `shipping_lines: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderShippingLinesItem] | Any | None`
    :   The type of the None singleton.

    `shipping_tax: str | Any | None`
    :   The type of the None singleton.

    `shipping_total: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `tax_lines: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderTaxLinesItem] | Any | None`
    :   The type of the None singleton.

    `total: str | Any | None`
    :   The type of the None singleton.

    `total_tax: str | Any | None`
    :   The type of the None singleton.

    `transaction_id: str | Any | None`
    :   The type of the None singleton.

    `version: str | Any | None`
    :   The type of the None singleton.

<a id="OrderBilling"></a>

`OrderBilling(**data: Any)`
:   Billing address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address_1: str | Any | None`
    :   The type of the None singleton.

    `address_2: str | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `company: str | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `postcode: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

<a id="OrderCouponLinesItem"></a>

`OrderCouponLinesItem(**data: Any)`
:   Nested schema for Order.coupon_lines_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | Any | None`
    :   The type of the None singleton.

    `discount: str | Any | None`
    :   The type of the None singleton.

    `discount_tax: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `meta_data: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderCouponLinesItemMetaDataItem] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderCouponLinesItemMetaDataItem"></a>

`OrderCouponLinesItemMetaDataItem(**data: Any)`
:   Nested schema for OrderCouponLinesItem.meta_data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `key: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: Any`
    :   The type of the None singleton.

<a id="OrderFeeLinesItem"></a>

`OrderFeeLinesItem(**data: Any)`
:   Nested schema for Order.fee_lines_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `meta_data: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderFeeLinesItemMetaDataItem] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `tax_class: str | Any | None`
    :   The type of the None singleton.

    `tax_status: str | Any | None`
    :   The type of the None singleton.

    `taxes: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderFeeLinesItemTaxesItem] | Any | None`
    :   The type of the None singleton.

    `total: str | Any | None`
    :   The type of the None singleton.

    `total_tax: str | Any | None`
    :   The type of the None singleton.

<a id="OrderFeeLinesItemMetaDataItem"></a>

`OrderFeeLinesItemMetaDataItem(**data: Any)`
:   Nested schema for OrderFeeLinesItem.meta_data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `key: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: Any`
    :   The type of the None singleton.

<a id="OrderFeeLinesItemTaxesItem"></a>

`OrderFeeLinesItemTaxesItem(**data: Any)`
:   Nested schema for OrderFeeLinesItem.taxes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `subtotal: str | Any | None`
    :   The type of the None singleton.

    `total: str | Any | None`
    :   The type of the None singleton.

<a id="OrderLineItemsItem"></a>

`OrderLineItemsItem(**data: Any)`
:   Nested schema for Order.line_items_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `image: airbyte_agent_sdk.connectors.woocommerce.models.OrderLineItemsItemImage | Any | None`
    :   The type of the None singleton.

    `meta_data: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderLineItemsItemMetaDataItem] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `parent_name: str | Any | None`
    :   The type of the None singleton.

    `price: float | Any | None`
    :   The type of the None singleton.

    `product_id: int | Any | None`
    :   The type of the None singleton.

    `quantity: int | Any | None`
    :   The type of the None singleton.

    `sku: str | Any | None`
    :   The type of the None singleton.

    `subtotal: str | Any | None`
    :   The type of the None singleton.

    `subtotal_tax: str | Any | None`
    :   The type of the None singleton.

    `tax_class: str | Any | None`
    :   The type of the None singleton.

    `taxes: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderLineItemsItemTaxesItem] | Any | None`
    :   The type of the None singleton.

    `total: str | Any | None`
    :   The type of the None singleton.

    `total_tax: str | Any | None`
    :   The type of the None singleton.

    `variation_id: int | Any | None`
    :   The type of the None singleton.

<a id="OrderLineItemsItemImage"></a>

`OrderLineItemsItemImage(**data: Any)`
:   Nested schema for OrderLineItemsItem.image
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `src: str | Any | None`
    :   The type of the None singleton.

<a id="OrderLineItemsItemMetaDataItem"></a>

`OrderLineItemsItemMetaDataItem(**data: Any)`
:   Nested schema for OrderLineItemsItem.meta_data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `display_key: str | Any | None`
    :   The type of the None singleton.

    `display_value: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `key: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: Any`
    :   The type of the None singleton.

<a id="OrderLineItemsItemTaxesItem"></a>

`OrderLineItemsItemTaxesItem(**data: Any)`
:   Nested schema for OrderLineItemsItem.taxes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `subtotal: str | Any | None`
    :   The type of the None singleton.

    `total: str | Any | None`
    :   The type of the None singleton.

<a id="OrderMetaDataItem"></a>

`OrderMetaDataItem(**data: Any)`
:   Nested schema for Order.meta_data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `key: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: Any`
    :   The type of the None singleton.

<a id="OrderNote"></a>

`OrderNote(**data: Any)`
:   OrderNote type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: str | Any | None`
    :   The type of the None singleton.

    `customer_note: bool | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_created_gmt: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `note: str | Any | None`
    :   The type of the None singleton.

<a id="OrderNotesListResultMeta"></a>

`OrderNotesListResultMeta(**data: Any)`
:   Metadata for order_notes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="OrderNotesSearchData"></a>

`OrderNotesSearchData(**data: Any)`
:   Search result data for order_notes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: str | None`
    :   Order note author

    `date_created: str | None`
    :   The date the order note was created

    `date_created_gmt: str | None`
    :   The date the order note was created, as GMT

    `id: int | None`
    :   Unique identifier

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   Order note content

<a id="OrderRefundsItem"></a>

`OrderRefundsItem(**data: Any)`
:   Nested schema for Order.refunds_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reason: str | Any | None`
    :   The type of the None singleton.

    `total: str | Any | None`
    :   The type of the None singleton.

<a id="OrderShipping"></a>

`OrderShipping(**data: Any)`
:   Shipping address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address_1: str | Any | None`
    :   The type of the None singleton.

    `address_2: str | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `company: str | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `postcode: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

<a id="OrderShippingLinesItem"></a>

`OrderShippingLinesItem(**data: Any)`
:   Nested schema for Order.shipping_lines_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `meta_data: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderShippingLinesItemMetaDataItem] | Any | None`
    :   The type of the None singleton.

    `method_id: str | Any | None`
    :   The type of the None singleton.

    `method_title: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `taxes: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderShippingLinesItemTaxesItem] | Any | None`
    :   The type of the None singleton.

    `total: str | Any | None`
    :   The type of the None singleton.

    `total_tax: str | Any | None`
    :   The type of the None singleton.

<a id="OrderShippingLinesItemMetaDataItem"></a>

`OrderShippingLinesItemMetaDataItem(**data: Any)`
:   Nested schema for OrderShippingLinesItem.meta_data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `key: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: Any`
    :   The type of the None singleton.

<a id="OrderShippingLinesItemTaxesItem"></a>

`OrderShippingLinesItemTaxesItem(**data: Any)`
:   Nested schema for OrderShippingLinesItem.taxes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `subtotal: str | Any | None`
    :   The type of the None singleton.

    `total: str | Any | None`
    :   The type of the None singleton.

<a id="OrderTaxLinesItem"></a>

`OrderTaxLinesItem(**data: Any)`
:   Nested schema for Order.tax_lines_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `compound: bool | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `label: str | Any | None`
    :   The type of the None singleton.

    `meta_data: list[airbyte_agent_sdk.connectors.woocommerce.models.OrderTaxLinesItemMetaDataItem] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rate_code: str | Any | None`
    :   The type of the None singleton.

    `rate_id: int | Any | None`
    :   The type of the None singleton.

    `shipping_tax_total: str | Any | None`
    :   The type of the None singleton.

    `tax_total: str | Any | None`
    :   The type of the None singleton.

<a id="OrderTaxLinesItemMetaDataItem"></a>

`OrderTaxLinesItemMetaDataItem(**data: Any)`
:   Nested schema for OrderTaxLinesItem.meta_data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `key: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: Any`
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

    `next: str | Any | None`
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

    `billing: dict[str, typing.Any] | None`
    :   Billing address

    `cart_hash: str | None`
    :   MD5 hash of cart items to ensure orders are not modified

    `cart_tax: str | None`
    :   Sum of line item taxes only

    `coupon_lines: list[typing.Any] | None`
    :   Coupons line data

    `created_via: str | None`
    :   Shows where the order was created

    `currency: str | None`
    :   Currency the order was created with, in ISO format

    `customer_id: int | None`
    :   User ID who owns the order (0 for guests)

    `customer_ip_address: str | None`
    :   Customer's IP address

    `customer_note: str | None`
    :   Note left by the customer during checkout

    `customer_user_agent: str | None`
    :   User agent of the customer

    `date_completed: str | None`
    :   The date the order was completed, in the site's timezone

    `date_completed_gmt: str | None`
    :   The date the order was completed, as GMT

    `date_created: str | None`
    :   The date the order was created, in the site's timezone

    `date_created_gmt: str | None`
    :   The date the order was created, as GMT

    `date_modified: str | None`
    :   The date the order was last modified, in the site's timezone

    `date_modified_gmt: str | None`
    :   The date the order was last modified, as GMT

    `date_paid: str | None`
    :   The date the order was paid, in the site's timezone

    `date_paid_gmt: str | None`
    :   The date the order was paid, as GMT

    `discount_tax: str | None`
    :   Total discount tax amount for the order

    `discount_total: str | None`
    :   Total discount amount for the order

    `fee_lines: list[typing.Any] | None`
    :   Fee lines data

    `id: int | None`
    :   Unique identifier for the resource

    `line_items: list[typing.Any] | None`
    :   Line items data

    `meta_data: list[typing.Any] | None`
    :   Meta data

    `model_config`
    :   The type of the None singleton.

    `number: str | None`
    :   Order number

    `order_key: str | None`
    :   Order key

    `parent_id: int | None`
    :   Parent order ID

    `payment_method: str | None`
    :   Payment method ID

    `payment_method_title: str | None`
    :   Payment method title

    `prices_include_tax: bool | None`
    :   True if the prices included tax during checkout

    `refunds: list[typing.Any] | None`
    :   List of refunds

    `shipping: dict[str, typing.Any] | None`
    :   Shipping address

    `shipping_lines: list[typing.Any] | None`
    :   Shipping lines data

    `shipping_tax: str | None`
    :   Total shipping tax amount for the order

    `shipping_total: str | None`
    :   Total shipping amount for the order

    `status: str | None`
    :   Order status

    `tax_lines: list[typing.Any] | None`
    :   Tax lines data

    `total: str | None`
    :   Grand total

    `total_tax: str | None`
    :   Sum of all taxes

    `transaction_id: str | None`
    :   Unique transaction ID

    `version: str | None`
    :   Version of WooCommerce which last updated the order

<a id="PaymentGateway"></a>

`PaymentGateway(**data: Any)`
:   PaymentGateway type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `connection_url: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `enabled: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `method_description: str | Any | None`
    :   The type of the None singleton.

    `method_supports: list[str | None] | Any | None`
    :   The type of the None singleton.

    `method_title: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `needs_setup: bool | Any | None`
    :   The type of the None singleton.

    `order: int | Any | None`
    :   The type of the None singleton.

    `post_install_scripts: list[str | None] | Any | None`
    :   The type of the None singleton.

    `required_settings_keys: list[str | None] | Any | None`
    :   The type of the None singleton.

    `settings: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `settings_url: str | Any | None`
    :   The type of the None singleton.

    `setup_help_text: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

<a id="PaymentGatewaysListResultMeta"></a>

`PaymentGatewaysListResultMeta(**data: Any)`
:   Metadata for payment_gateways.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="PaymentGatewaysSearchData"></a>

`PaymentGatewaysSearchData(**data: Any)`
:   Search result data for payment_gateways entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | None`
    :   Payment gateway description on checkout

    `enabled: bool | None`
    :   Payment gateway enabled status

    `id: str | None`
    :   Payment gateway ID

    `method_description: str | None`
    :   Payment gateway method description

    `method_supports: list[typing.Any] | None`
    :   Supported features

    `method_title: str | None`
    :   Payment gateway method title

    `model_config`
    :   The type of the None singleton.

    `order: Any`
    :   Payment gateway sort order

    `settings: dict[str, typing.Any] | None`
    :   Payment gateway settings

    `title: str | None`
    :   Payment gateway title on checkout

<a id="Product"></a>

`Product(**data: Any)`
:   Product type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: list[airbyte_agent_sdk.connectors.woocommerce.models.ProductAttributesItem] | Any | None`
    :   The type of the None singleton.

    `average_rating: str | Any | None`
    :   The type of the None singleton.

    `backordered: bool | Any | None`
    :   The type of the None singleton.

    `backorders: str | Any | None`
    :   The type of the None singleton.

    `backorders_allowed: bool | Any | None`
    :   The type of the None singleton.

    `brands: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `button_text: str | Any | None`
    :   The type of the None singleton.

    `catalog_visibility: str | Any | None`
    :   The type of the None singleton.

    `categories: list[airbyte_agent_sdk.connectors.woocommerce.models.ProductCategoriesItem] | Any | None`
    :   The type of the None singleton.

    `cross_sell_ids: list[int | None] | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_created_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_modified: str | Any | None`
    :   The type of the None singleton.

    `date_modified_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_on_sale_from: str | Any | None`
    :   The type of the None singleton.

    `date_on_sale_from_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_on_sale_to: str | Any | None`
    :   The type of the None singleton.

    `date_on_sale_to_gmt: str | Any | None`
    :   The type of the None singleton.

    `default_attributes: list[airbyte_agent_sdk.connectors.woocommerce.models.ProductDefaultAttributesItem] | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `dimensions: airbyte_agent_sdk.connectors.woocommerce.models.ProductDimensions | Any | None`
    :   The type of the None singleton.

    `download_expiry: int | Any | None`
    :   The type of the None singleton.

    `download_limit: int | Any | None`
    :   The type of the None singleton.

    `downloadable: bool | Any | None`
    :   The type of the None singleton.

    `downloads: list[airbyte_agent_sdk.connectors.woocommerce.models.ProductDownloadsItem] | Any | None`
    :   The type of the None singleton.

    `external_url: str | Any | None`
    :   The type of the None singleton.

    `featured: bool | Any | None`
    :   The type of the None singleton.

    `global_unique_id: str | Any | None`
    :   The type of the None singleton.

    `grouped_products: list[int | None] | Any | None`
    :   The type of the None singleton.

    `has_options: bool | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `images: list[airbyte_agent_sdk.connectors.woocommerce.models.ProductImagesItem] | Any | None`
    :   The type of the None singleton.

    `low_stock_amount: int | Any | None`
    :   The type of the None singleton.

    `manage_stock: bool | Any | None`
    :   The type of the None singleton.

    `menu_order: int | Any | None`
    :   The type of the None singleton.

    `meta_data: list[airbyte_agent_sdk.connectors.woocommerce.models.ProductMetaDataItem] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `on_sale: bool | Any | None`
    :   The type of the None singleton.

    `parent_id: int | Any | None`
    :   The type of the None singleton.

    `permalink: str | Any | None`
    :   The type of the None singleton.

    `post_password: str | Any | None`
    :   The type of the None singleton.

    `price: str | Any | None`
    :   The type of the None singleton.

    `price_html: str | Any | None`
    :   The type of the None singleton.

    `purchasable: bool | Any | None`
    :   The type of the None singleton.

    `purchase_note: str | Any | None`
    :   The type of the None singleton.

    `rating_count: int | Any | None`
    :   The type of the None singleton.

    `regular_price: str | Any | None`
    :   The type of the None singleton.

    `related_ids: list[int | None] | Any | None`
    :   The type of the None singleton.

    `reviews_allowed: bool | Any | None`
    :   The type of the None singleton.

    `sale_price: str | Any | None`
    :   The type of the None singleton.

    `shipping_class: str | Any | None`
    :   The type of the None singleton.

    `shipping_class_id: int | Any | None`
    :   The type of the None singleton.

    `shipping_required: bool | Any | None`
    :   The type of the None singleton.

    `shipping_taxable: bool | Any | None`
    :   The type of the None singleton.

    `short_description: str | Any | None`
    :   The type of the None singleton.

    `sku: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

    `sold_individually: bool | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `stock_quantity: int | Any | None`
    :   The type of the None singleton.

    `stock_status: str | Any | None`
    :   The type of the None singleton.

    `tags: list[airbyte_agent_sdk.connectors.woocommerce.models.ProductTagsItem] | Any | None`
    :   The type of the None singleton.

    `tax_class: str | Any | None`
    :   The type of the None singleton.

    `tax_status: str | Any | None`
    :   The type of the None singleton.

    `total_sales: int | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `upsell_ids: list[int | None] | Any | None`
    :   The type of the None singleton.

    `variations: list[int | None] | Any | None`
    :   The type of the None singleton.

    `virtual: bool | Any | None`
    :   The type of the None singleton.

    `weight: str | Any | None`
    :   The type of the None singleton.

<a id="ProductAttribute"></a>

`ProductAttribute(**data: Any)`
:   ProductAttribute type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_archives: bool | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `order_by: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="ProductAttributesItem"></a>

`ProductAttributesItem(**data: Any)`
:   Nested schema for Product.attributes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `options: list[str | None] | Any | None`
    :   The type of the None singleton.

    `position: int | Any | None`
    :   The type of the None singleton.

    `variation: bool | Any | None`
    :   The type of the None singleton.

    `visible: bool | Any | None`
    :   The type of the None singleton.

<a id="ProductAttributesListResultMeta"></a>

`ProductAttributesListResultMeta(**data: Any)`
:   Metadata for product_attributes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="ProductAttributesSearchData"></a>

`ProductAttributesSearchData(**data: Any)`
:   Search result data for product_attributes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_archives: bool | None`
    :   Enable/Disable attribute archives

    `id: int | None`
    :   Unique identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Attribute name

    `order_by: str | None`
    :   Default sort order

    `slug: str | None`
    :   Alphanumeric identifier

    `type_: str | None`
    :   Type of attribute

<a id="ProductCategoriesItem"></a>

`ProductCategoriesItem(**data: Any)`
:   Nested schema for Product.categories_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

<a id="ProductCategoriesListResultMeta"></a>

`ProductCategoriesListResultMeta(**data: Any)`
:   Metadata for product_categories.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="ProductCategoriesSearchData"></a>

`ProductCategoriesSearchData(**data: Any)`
:   Search result data for product_categories entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | None`
    :   Number of published products for the resource

    `description: str | None`
    :   HTML description of the resource

    `display: str | None`
    :   Category archive display type

    `id: int | None`
    :   Unique identifier for the resource

    `image: list[typing.Any] | None`
    :   Image data

    `menu_order: int | None`
    :   Menu order

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Category name

    `parent: int | None`
    :   The ID for the parent of the resource

    `slug: str | None`
    :   An alphanumeric identifier

<a id="ProductCategory"></a>

`ProductCategory(**data: Any)`
:   ProductCategory type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `display: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `image: airbyte_agent_sdk.connectors.woocommerce.models.ProductCategoryImage | Any | None`
    :   The type of the None singleton.

    `menu_order: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `parent: int | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

<a id="ProductCategoryImage"></a>

`ProductCategoryImage(**data: Any)`
:   Image data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `alt: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_created_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_modified: str | Any | None`
    :   The type of the None singleton.

    `date_modified_gmt: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `src: str | Any | None`
    :   The type of the None singleton.

<a id="ProductDefaultAttributesItem"></a>

`ProductDefaultAttributesItem(**data: Any)`
:   Nested schema for Product.default_attributes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `option: str | Any | None`
    :   The type of the None singleton.

<a id="ProductDimensions"></a>

`ProductDimensions(**data: Any)`
:   Product dimensions
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `height: str | Any | None`
    :   The type of the None singleton.

    `length: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `width: str | Any | None`
    :   The type of the None singleton.

<a id="ProductDownloadsItem"></a>

`ProductDownloadsItem(**data: Any)`
:   Nested schema for Product.downloads_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `file: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

<a id="ProductImagesItem"></a>

`ProductImagesItem(**data: Any)`
:   Nested schema for Product.images_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `alt: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_created_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_modified: str | Any | None`
    :   The type of the None singleton.

    `date_modified_gmt: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `src: str | Any | None`
    :   The type of the None singleton.

<a id="ProductMetaDataItem"></a>

`ProductMetaDataItem(**data: Any)`
:   Nested schema for Product.meta_data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `key: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: Any`
    :   The type of the None singleton.

<a id="ProductReview"></a>

`ProductReview(**data: Any)`
:   ProductReview type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_created_gmt: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `product_id: int | Any | None`
    :   The type of the None singleton.

    `product_name: str | Any | None`
    :   The type of the None singleton.

    `product_permalink: str | Any | None`
    :   The type of the None singleton.

    `rating: int | Any | None`
    :   The type of the None singleton.

    `review: str | Any | None`
    :   The type of the None singleton.

    `reviewer: str | Any | None`
    :   The type of the None singleton.

    `reviewer_avatar_urls: dict[str, str | None] | Any | None`
    :   The type of the None singleton.

    `reviewer_email: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `verified: bool | Any | None`
    :   The type of the None singleton.

<a id="ProductReviewsListResultMeta"></a>

`ProductReviewsListResultMeta(**data: Any)`
:   Metadata for product_reviews.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="ProductReviewsSearchData"></a>

`ProductReviewsSearchData(**data: Any)`
:   Search result data for product_reviews entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date_created: str | None`
    :   The date the review was created

    `date_created_gmt: str | None`
    :   The date the review was created, as GMT

    `id: int | None`
    :   Unique identifier

    `model_config`
    :   The type of the None singleton.

    `product_id: int | None`
    :   Product the review belongs to

    `rating: int | None`
    :   Review rating (0 to 5)

    `review: str | None`
    :   The content of the review

    `reviewer: str | None`
    :   Reviewer name

    `reviewer_email: str | None`
    :   Reviewer email

    `status: str | None`
    :   Status of the review

    `verified: bool | None`
    :   Shows if the reviewer bought the product

<a id="ProductTag"></a>

`ProductTag(**data: Any)`
:   ProductTag type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

<a id="ProductTagsItem"></a>

`ProductTagsItem(**data: Any)`
:   Nested schema for Product.tags_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

<a id="ProductTagsListResultMeta"></a>

`ProductTagsListResultMeta(**data: Any)`
:   Metadata for product_tags.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="ProductTagsSearchData"></a>

`ProductTagsSearchData(**data: Any)`
:   Search result data for product_tags entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | None`
    :   Number of published products

    `description: str | None`
    :   HTML description

    `id: int | None`
    :   Unique identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Tag name

    `slug: str | None`
    :   Alphanumeric identifier

<a id="ProductVariation"></a>

`ProductVariation(**data: Any)`
:   ProductVariation type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: list[airbyte_agent_sdk.connectors.woocommerce.models.ProductVariationAttributesItem] | Any | None`
    :   The type of the None singleton.

    `backordered: bool | Any | None`
    :   The type of the None singleton.

    `backorders: str | Any | None`
    :   The type of the None singleton.

    `backorders_allowed: bool | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_created_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_modified: str | Any | None`
    :   The type of the None singleton.

    `date_modified_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_on_sale_from: str | Any | None`
    :   The type of the None singleton.

    `date_on_sale_from_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_on_sale_to: str | Any | None`
    :   The type of the None singleton.

    `date_on_sale_to_gmt: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `dimensions: airbyte_agent_sdk.connectors.woocommerce.models.ProductVariationDimensions | Any | None`
    :   The type of the None singleton.

    `download_expiry: int | Any | None`
    :   The type of the None singleton.

    `download_limit: int | Any | None`
    :   The type of the None singleton.

    `downloadable: bool | Any | None`
    :   The type of the None singleton.

    `downloads: list[airbyte_agent_sdk.connectors.woocommerce.models.ProductVariationDownloadsItem] | Any | None`
    :   The type of the None singleton.

    `global_unique_id: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `image: airbyte_agent_sdk.connectors.woocommerce.models.ProductVariationImage | Any | None`
    :   The type of the None singleton.

    `low_stock_amount: int | Any | None`
    :   The type of the None singleton.

    `manage_stock: bool | Any | None`
    :   The type of the None singleton.

    `menu_order: int | Any | None`
    :   The type of the None singleton.

    `meta_data: list[airbyte_agent_sdk.connectors.woocommerce.models.ProductVariationMetaDataItem] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `on_sale: bool | Any | None`
    :   The type of the None singleton.

    `parent_id: int | Any | None`
    :   The type of the None singleton.

    `permalink: str | Any | None`
    :   The type of the None singleton.

    `price: str | Any | None`
    :   The type of the None singleton.

    `purchasable: bool | Any | None`
    :   The type of the None singleton.

    `regular_price: str | Any | None`
    :   The type of the None singleton.

    `sale_price: str | Any | None`
    :   The type of the None singleton.

    `shipping_class: str | Any | None`
    :   The type of the None singleton.

    `shipping_class_id: int | Any | None`
    :   The type of the None singleton.

    `sku: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `stock_quantity: int | Any | None`
    :   The type of the None singleton.

    `stock_status: str | Any | None`
    :   The type of the None singleton.

    `tax_class: str | Any | None`
    :   The type of the None singleton.

    `tax_status: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `virtual: bool | Any | None`
    :   The type of the None singleton.

    `weight: str | Any | None`
    :   The type of the None singleton.

<a id="ProductVariationAttributesItem"></a>

`ProductVariationAttributesItem(**data: Any)`
:   Nested schema for ProductVariation.attributes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `option: str | Any | None`
    :   The type of the None singleton.

<a id="ProductVariationDimensions"></a>

`ProductVariationDimensions(**data: Any)`
:   Variation dimensions
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `height: str | Any | None`
    :   The type of the None singleton.

    `length: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `width: str | Any | None`
    :   The type of the None singleton.

<a id="ProductVariationDownloadsItem"></a>

`ProductVariationDownloadsItem(**data: Any)`
:   Nested schema for ProductVariation.downloads_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `file: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

<a id="ProductVariationImage"></a>

`ProductVariationImage(**data: Any)`
:   Variation image data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `alt: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_created_gmt: str | Any | None`
    :   The type of the None singleton.

    `date_modified: str | Any | None`
    :   The type of the None singleton.

    `date_modified_gmt: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `src: str | Any | None`
    :   The type of the None singleton.

<a id="ProductVariationMetaDataItem"></a>

`ProductVariationMetaDataItem(**data: Any)`
:   Nested schema for ProductVariation.meta_data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `key: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: Any`
    :   The type of the None singleton.

<a id="ProductVariationsListResultMeta"></a>

`ProductVariationsListResultMeta(**data: Any)`
:   Metadata for product_variations.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="ProductVariationsSearchData"></a>

`ProductVariationsSearchData(**data: Any)`
:   Search result data for product_variations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: list[typing.Any] | None`
    :   List of attributes

    `backordered: bool | None`
    :   On backordered

    `backorders: str | None`
    :   Backorders allowed setting

    `backorders_allowed: bool | None`
    :   Shows if backorders are allowed

    `date_created: str | None`
    :   The date the variation was created

    `date_created_gmt: str | None`
    :   The date the variation was created, as GMT

    `date_modified: str | None`
    :   The date the variation was last modified

    `date_modified_gmt: str | None`
    :   The date the variation was last modified, as GMT

    `date_on_sale_from: str | None`
    :   Start date of sale price

    `date_on_sale_from_gmt: str | None`
    :   Start date of sale price, as GMT

    `date_on_sale_to: str | None`
    :   End date of sale price

    `date_on_sale_to_gmt: str | None`
    :   End date of sale price, as GMT

    `description: str | None`
    :   Variation description

    `dimensions: dict[str, typing.Any] | None`
    :   Variation dimensions

    `download_expiry: int | None`
    :   Days until access expires

    `download_limit: int | None`
    :   Download limit

    `downloadable: bool | None`
    :   If downloadable

    `downloads: list[typing.Any] | None`
    :   Downloadable files

    `id: int | None`
    :   Unique identifier

    `image: list[typing.Any] | None`
    :   Variation image data

    `manage_stock: str | None`
    :   Stock management at variation level

    `menu_order: int | None`
    :   Menu order

    `meta_data: list[typing.Any] | None`
    :   Meta data

    `model_config`
    :   The type of the None singleton.

    `on_sale: bool | None`
    :   Shows if on sale

    `permalink: str | None`
    :   Variation URL

    `price: str | None`
    :   Current variation price

    `purchasable: bool | None`
    :   Can be bought

    `regular_price: str | None`
    :   Variation regular price

    `sale_price: str | None`
    :   Variation sale price

    `shipping_class: str | None`
    :   Shipping class slug

    `shipping_class_id: int | None`
    :   Shipping class ID

    `sku: str | None`
    :   Unique identifier (SKU)

    `status: str | None`
    :   Variation status

    `stock_quantity: int | None`
    :   Stock quantity

    `stock_status: str | None`
    :   Controls the stock status

    `tax_class: str | None`
    :   Tax class

    `tax_status: str | None`
    :   Tax status

    `virtual: bool | None`
    :   If virtual

    `weight: str | None`
    :   Variation weight

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

    `next: str | Any | None`
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

    `attributes: list[typing.Any] | None`
    :   List of attributes

    `average_rating: str | None`
    :   Reviews average rating

    `backordered: bool | None`
    :   Shows if the product is on backordered

    `backorders: str | None`
    :   If managing stock, this controls if backorders are allowed

    `backorders_allowed: bool | None`
    :   Shows if backorders are allowed

    `button_text: str | None`
    :   Product external button text

    `catalog_visibility: str | None`
    :   Catalog visibility

    `categories: list[typing.Any] | None`
    :   List of categories

    `cross_sell_ids: list[typing.Any] | None`
    :   List of cross-sell products IDs

    `date_created: str | None`
    :   The date the product was created

    `date_created_gmt: str | None`
    :   The date the product was created, as GMT

    `date_modified: str | None`
    :   The date the product was last modified

    `date_modified_gmt: str | None`
    :   The date the product was last modified, as GMT

    `date_on_sale_from: str | None`
    :   Start date of sale price

    `date_on_sale_from_gmt: str | None`
    :   Start date of sale price, as GMT

    `date_on_sale_to: str | None`
    :   End date of sale price

    `date_on_sale_to_gmt: str | None`
    :   End date of sale price, as GMT

    `default_attributes: list[typing.Any] | None`
    :   Defaults variation attributes

    `description: str | None`
    :   Product description

    `dimensions: dict[str, typing.Any] | None`
    :   Product dimensions

    `download_expiry: int | None`
    :   Number of days until access to downloadable files expires

    `download_limit: int | None`
    :   Number of times downloadable files can be downloaded

    `downloadable: bool | None`
    :   If the product is downloadable

    `downloads: list[typing.Any] | None`
    :   List of downloadable files

    `external_url: str | None`
    :   Product external URL

    `grouped_products: list[typing.Any] | None`
    :   List of grouped products ID

    `id: int | None`
    :   Unique identifier for the resource

    `images: list[typing.Any] | None`
    :   List of images

    `manage_stock: bool | None`
    :   Stock management at product level

    `menu_order: int | None`
    :   Menu order

    `meta_data: list[typing.Any] | None`
    :   Meta data

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Product name

    `on_sale: bool | None`
    :   Shows if the product is on sale

    `parent_id: int | None`
    :   Product parent ID

    `permalink: str | None`
    :   Product URL

    `price: str | None`
    :   Current product price

    `price_html: str | None`
    :   Price formatted in HTML

    `purchasable: bool | None`
    :   Shows if the product can be bought

    `purchase_note: str | None`
    :   Note to send customer after purchase

    `rating_count: int | None`
    :   Amount of reviews

    `regular_price: str | None`
    :   Product regular price

    `related_ids: list[typing.Any] | None`
    :   List of related products IDs

    `reviews_allowed: bool | None`
    :   Allow reviews

    `sale_price: str | None`
    :   Product sale price

    `shipping_class: str | None`
    :   Shipping class slug

    `shipping_class_id: int | None`
    :   Shipping class ID

    `shipping_required: bool | None`
    :   Shows if the product needs to be shipped

    `shipping_taxable: bool | None`
    :   Shows if product shipping is taxable

    `short_description: str | None`
    :   Product short description

    `sku: str | None`
    :   Unique identifier (SKU)

    `slug: str | None`
    :   Product slug

    `sold_individually: bool | None`
    :   Allow one item per order

    `status: str | None`
    :   Product status

    `stock_quantity: int | None`
    :   Stock quantity

    `stock_status: str | None`
    :   Controls the stock status

    `tags: list[typing.Any] | None`
    :   List of tags

    `tax_class: str | None`
    :   Tax class

    `tax_status: str | None`
    :   Tax status

    `total_sales: int | None`
    :   Amount of sales

    `type_: str | None`
    :   Product type

    `upsell_ids: list[typing.Any] | None`
    :   List of up-sell products IDs

    `variations: list[typing.Any] | None`
    :   List of variations IDs

    `virtual: bool | None`
    :   If the product is virtual

    `weight: str | None`
    :   Product weight

<a id="Refund"></a>

`Refund(**data: Any)`
:   Refund type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_created_gmt: str | Any | None`
    :   The type of the None singleton.

    `fee_lines: list[airbyte_agent_sdk.connectors.woocommerce.models.RefundFeeLinesItem] | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `line_items: list[airbyte_agent_sdk.connectors.woocommerce.models.RefundLineItemsItem] | Any | None`
    :   The type of the None singleton.

    `meta_data: list[airbyte_agent_sdk.connectors.woocommerce.models.RefundMetaDataItem] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reason: str | Any | None`
    :   The type of the None singleton.

    `refunded_by: int | Any | None`
    :   The type of the None singleton.

    `refunded_payment: bool | Any | None`
    :   The type of the None singleton.

    `shipping_lines: list[airbyte_agent_sdk.connectors.woocommerce.models.RefundShippingLinesItem] | Any | None`
    :   The type of the None singleton.

    `tax_lines: list[airbyte_agent_sdk.connectors.woocommerce.models.RefundTaxLinesItem] | Any | None`
    :   The type of the None singleton.

<a id="RefundFeeLinesItem"></a>

`RefundFeeLinesItem(**data: Any)`
:   Nested schema for Refund.fee_lines_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `tax_class: str | Any | None`
    :   The type of the None singleton.

    `tax_status: str | Any | None`
    :   The type of the None singleton.

    `total: str | Any | None`
    :   The type of the None singleton.

    `total_tax: str | Any | None`
    :   The type of the None singleton.

<a id="RefundLineItemsItem"></a>

`RefundLineItemsItem(**data: Any)`
:   Nested schema for Refund.line_items_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `meta_data: list[airbyte_agent_sdk.connectors.woocommerce.models.RefundLineItemsItemMetaDataItem] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `price: float | Any | None`
    :   The type of the None singleton.

    `product_id: int | Any | None`
    :   The type of the None singleton.

    `quantity: int | Any | None`
    :   The type of the None singleton.

    `sku: str | Any | None`
    :   The type of the None singleton.

    `subtotal: str | Any | None`
    :   The type of the None singleton.

    `subtotal_tax: str | Any | None`
    :   The type of the None singleton.

    `tax_class: str | Any | None`
    :   The type of the None singleton.

    `taxes: list[airbyte_agent_sdk.connectors.woocommerce.models.RefundLineItemsItemTaxesItem] | Any | None`
    :   The type of the None singleton.

    `total: str | Any | None`
    :   The type of the None singleton.

    `total_tax: str | Any | None`
    :   The type of the None singleton.

    `variation_id: int | Any | None`
    :   The type of the None singleton.

<a id="RefundLineItemsItemMetaDataItem"></a>

`RefundLineItemsItemMetaDataItem(**data: Any)`
:   Nested schema for RefundLineItemsItem.meta_data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `key: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: Any`
    :   The type of the None singleton.

<a id="RefundLineItemsItemTaxesItem"></a>

`RefundLineItemsItemTaxesItem(**data: Any)`
:   Nested schema for RefundLineItemsItem.taxes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `subtotal: str | Any | None`
    :   The type of the None singleton.

    `total: str | Any | None`
    :   The type of the None singleton.

<a id="RefundMetaDataItem"></a>

`RefundMetaDataItem(**data: Any)`
:   Nested schema for Refund.meta_data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `key: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: Any`
    :   The type of the None singleton.

<a id="RefundShippingLinesItem"></a>

`RefundShippingLinesItem(**data: Any)`
:   Nested schema for Refund.shipping_lines_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `method_id: str | Any | None`
    :   The type of the None singleton.

    `method_title: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total: str | Any | None`
    :   The type of the None singleton.

    `total_tax: str | Any | None`
    :   The type of the None singleton.

<a id="RefundTaxLinesItem"></a>

`RefundTaxLinesItem(**data: Any)`
:   Nested schema for Refund.tax_lines_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `compound: bool | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `label: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rate_code: str | Any | None`
    :   The type of the None singleton.

    `rate_id: int | Any | None`
    :   The type of the None singleton.

    `shipping_tax_total: str | Any | None`
    :   The type of the None singleton.

    `tax_total: str | Any | None`
    :   The type of the None singleton.

<a id="RefundsListResultMeta"></a>

`RefundsListResultMeta(**data: Any)`
:   Metadata for refunds.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="RefundsSearchData"></a>

`RefundsSearchData(**data: Any)`
:   Search result data for refunds entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   Refund amount

    `date_created: str | None`
    :   The date the refund was created

    `date_created_gmt: str | None`
    :   The date the refund was created, as GMT

    `id: int | None`
    :   Unique identifier

    `line_items: list[typing.Any] | None`
    :   Line items data

    `meta_data: list[typing.Any] | None`
    :   Meta data

    `model_config`
    :   The type of the None singleton.

    `reason: str | None`
    :   Reason for refund

    `refunded_by: int | None`
    :   User ID of user who created the refund

    `refunded_payment: bool | None`
    :   If the payment was refunded via the API

<a id="ShippingMethod"></a>

`ShippingMethod(**data: Any)`
:   ShippingMethod type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

<a id="ShippingMethodsListResultMeta"></a>

`ShippingMethodsListResultMeta(**data: Any)`
:   Metadata for shipping_methods.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="ShippingMethodsSearchData"></a>

`ShippingMethodsSearchData(**data: Any)`
:   Search result data for shipping_methods entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | None`
    :   Shipping method description

    `id: str | None`
    :   Method ID

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   Shipping method title

<a id="ShippingZone"></a>

`ShippingZone(**data: Any)`
:   ShippingZone type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `order: int | Any | None`
    :   The type of the None singleton.

<a id="ShippingZonesListResultMeta"></a>

`ShippingZonesListResultMeta(**data: Any)`
:   Metadata for shipping_zones.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="ShippingZonesSearchData"></a>

`ShippingZonesSearchData(**data: Any)`
:   Search result data for shipping_zones entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | None`
    :   Unique identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Shipping zone name

    `order: int | None`
    :   Shipping zone order

<a id="TaxClass"></a>

`TaxClass(**data: Any)`
:   TaxClass type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

<a id="TaxClassesListResultMeta"></a>

`TaxClassesListResultMeta(**data: Any)`
:   Metadata for tax_classes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="TaxClassesSearchData"></a>

`TaxClassesSearchData(**data: Any)`
:   Search result data for tax_classes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Tax class name

    `slug: str | None`
    :   Unique identifier

<a id="TaxRate"></a>

`TaxRate(**data: Any)`
:   TaxRate type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cities: list[str | None] | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `class_: str | Any | None`
    :   The type of the None singleton.

    `compound: bool | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `order: int | Any | None`
    :   The type of the None singleton.

    `postcode: str | Any | None`
    :   The type of the None singleton.

    `postcodes: list[str | None] | Any | None`
    :   The type of the None singleton.

    `priority: int | Any | None`
    :   The type of the None singleton.

    `rate: str | Any | None`
    :   The type of the None singleton.

    `shipping: bool | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

<a id="TaxRatesListResultMeta"></a>

`TaxRatesListResultMeta(**data: Any)`
:   Metadata for tax_rates.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="TaxRatesSearchData"></a>

`TaxRatesSearchData(**data: Any)`
:   Search result data for tax_rates entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cities: list[typing.Any] | None`
    :   City names

    `city: str | None`
    :   City name

    `class_: str | None`
    :   Tax class

    `compound: bool | None`
    :   Whether this is a compound rate

    `country: str | None`
    :   Country ISO 3166 code

    `id: int | None`
    :   Unique identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Tax rate name

    `order: int | None`
    :   Order in queries

    `postcode: str | None`
    :   Postcode/ZIP

    `postcodes: list[typing.Any] | None`
    :   Postcodes/ZIPs

    `priority: int | None`
    :   Tax priority

    `rate: str | None`
    :   Tax rate

    `shipping: bool | None`
    :   Applied to shipping

    `state: str | None`
    :   State code

<a id="WoocommerceAuthConfig"></a>

`WoocommerceAuthConfig(**data: Any)`
:   WooCommerce API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   WooCommerce REST API consumer key (starts with ck_)

    `api_secret: str`
    :   WooCommerce REST API consumer secret (starts with cs_)

    `model_config`
    :   The type of the None singleton.

<a id="WoocommerceCheckResult"></a>

`WoocommerceCheckResult(**data: Any)`
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

<a id="WoocommerceExecuteResult"></a>

`WoocommerceExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="WoocommerceExecuteResultWithMeta"></a>

`WoocommerceExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[Coupon], CouponsListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[Customer], CustomersListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[OrderNote], OrderNotesListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[Order], OrdersListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[PaymentGateway], PaymentGatewaysListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[ProductAttribute], ProductAttributesListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[ProductCategory], ProductCategoriesListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[ProductReview], ProductReviewsListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[ProductTag], ProductTagsListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[ProductVariation], ProductVariationsListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[Product], ProductsListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[Refund], RefundsListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[ShippingMethod], ShippingMethodsListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[ShippingZone], ShippingZonesListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[TaxClass], TaxClassesListResultMeta]
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[TaxRate], TaxRatesListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`WoocommerceExecuteResultWithMeta[list[Coupon], CouponsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CouponsListResult"></a>

`CouponsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[Customer], CustomersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
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

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[OrderNote], OrderNotesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrderNotesListResult"></a>

`OrderNotesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[Order], OrdersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
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

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[PaymentGateway], PaymentGatewaysListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PaymentGatewaysListResult"></a>

`PaymentGatewaysListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[ProductAttribute], ProductAttributesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductAttributesListResult"></a>

`ProductAttributesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[ProductCategory], ProductCategoriesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductCategoriesListResult"></a>

`ProductCategoriesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[ProductReview], ProductReviewsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductReviewsListResult"></a>

`ProductReviewsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[ProductTag], ProductTagsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductTagsListResult"></a>

`ProductTagsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[ProductVariation], ProductVariationsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductVariationsListResult"></a>

`ProductVariationsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[Product], ProductsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
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

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[Refund], RefundsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="RefundsListResult"></a>

`RefundsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[ShippingMethod], ShippingMethodsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ShippingMethodsListResult"></a>

`ShippingMethodsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[ShippingZone], ShippingZonesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ShippingZonesListResult"></a>

`ShippingZonesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[TaxClass], TaxClassesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TaxClassesListResult"></a>

`TaxClassesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`WoocommerceExecuteResultWithMeta[list[TaxRate], TaxRatesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TaxRatesListResult"></a>

`TaxRatesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="WoocommerceReplicationConfig"></a>

`WoocommerceReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from WooCommerce.
    
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
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data.