---
id: airbyte_agent_sdk-connectors-woocommerce-index
title: airbyte_agent_sdk.connectors.woocommerce.index
---

Module airbyte_agent_sdk.connectors.woocommerce
===============================================
Woocommerce connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.woocommerce.connector
* airbyte_agent_sdk.connectors.woocommerce.connector_model
* airbyte_agent_sdk.connectors.woocommerce.models
* airbyte_agent_sdk.connectors.woocommerce.types

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

<a id="WoocommerceConnector"></a>

`WoocommerceConnector(auth_config: WoocommerceAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, shop: str | None = None)`
:   Type-safe Woocommerce API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new woocommerce connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., WoocommerceAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            shop: The WooCommerce store domain (e.g., mystore.com)
    Examples:
        # Local mode (direct API calls)
        connector = WoocommerceConnector(auth_config=WoocommerceAuthConfig(api_key="...", api_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = WoocommerceConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = WoocommerceConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'WoocommerceAuthConfig'", name: str | None = None, replication_config: "'WoocommerceReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A WoocommerceConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await WoocommerceConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=WoocommerceAuthConfig(api_key="...", api_secret="..."),
            )
        
            # With replication config (required for this connector):
            connector = await WoocommerceConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=WoocommerceAuthConfig(api_key="...", api_secret="..."),
                replication_config=WoocommerceReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @WoocommerceConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @WoocommerceConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await WoocommerceConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            WoocommerceCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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