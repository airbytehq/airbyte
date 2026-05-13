---
id: airbyte_agent_sdk-connectors-woocommerce-types
title: airbyte_agent_sdk.connectors.woocommerce.types
---

Module airbyte_agent_sdk.connectors.woocommerce.types
=====================================================
Type definitions for woocommerce connector.

Classes
-------

<a id="AirbyteSearchParams"></a>

`AirbyteSearchParams(*args, **kwargs)`
:   Parameters for Airbyte cache search operations (generic, use entity-specific query types for better type hints).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `fields: list[list[str]]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `query: dict[str, typing.Any]`
    :   The type of the None singleton.

<a id="CouponsAndCondition"></a>

`CouponsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.CouponsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsAnyCondition]`
    :   The type of the None singleton.

<a id="CouponsAnyCondition"></a>

`CouponsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.CouponsAnyValueFilter`
    :   The type of the None singleton.

<a id="CouponsAnyValueFilter"></a>

`CouponsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Any`
    :   The amount of discount

    `code: Any`
    :   Coupon code

    `date_created: Any`
    :   The date the coupon was created

    `date_created_gmt: Any`
    :   The date the coupon was created, as GMT

    `date_expires: Any`
    :   The date the coupon expires

    `date_expires_gmt: Any`
    :   The date the coupon expires, as GMT

    `date_modified: Any`
    :   The date the coupon was last modified

    `date_modified_gmt: Any`
    :   The date the coupon was last modified, as GMT

    `description: Any`
    :   Coupon description

    `discount_type: Any`
    :   Determines the type of discount

    `email_restrictions: Any`
    :   List of email addresses that can use this coupon

    `exclude_sale_items: Any`
    :   If true, not applied to sale items

    `excluded_product_categories: Any`
    :   Excluded category IDs

    `excluded_product_ids: Any`
    :   Excluded product IDs

    `free_shipping: Any`
    :   Enables free shipping

    `id: Any`
    :   Unique identifier

    `individual_use: Any`
    :   Can only be used individually

    `limit_usage_to_x_items: Any`
    :   Max cart items coupon applies to

    `maximum_amount: Any`
    :   Maximum order amount

    `meta_data: Any`
    :   Meta data

    `minimum_amount: Any`
    :   Minimum order amount

    `product_categories: Any`
    :   Applicable category IDs

    `product_ids: Any`
    :   Applicable product IDs

    `usage_count: Any`
    :   Times used

    `usage_limit: Any`
    :   Total usage limit

    `usage_limit_per_user: Any`
    :   Per-customer usage limit

    `used_by: Any`
    :   Users who have used the coupon

<a id="CouponsContainsCondition"></a>

`CouponsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.CouponsAnyValueFilter`
    :   The type of the None singleton.

<a id="CouponsEqCondition"></a>

`CouponsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.CouponsSearchFilter`
    :   The type of the None singleton.

<a id="CouponsFuzzyCondition"></a>

`CouponsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.CouponsStringFilter`
    :   The type of the None singleton.

<a id="CouponsGetParams"></a>

`CouponsGetParams(*args, **kwargs)`
:   Parameters for coupons.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CouponsGtCondition"></a>

`CouponsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.CouponsSearchFilter`
    :   The type of the None singleton.

<a id="CouponsGteCondition"></a>

`CouponsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.CouponsSearchFilter`
    :   The type of the None singleton.

<a id="CouponsInCondition"></a>

`CouponsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.CouponsInFilter`
    :   The type of the None singleton.

<a id="CouponsInFilter"></a>

`CouponsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: list[str]`
    :   The amount of discount

    `code: list[str]`
    :   Coupon code

    `date_created: list[str]`
    :   The date the coupon was created

    `date_created_gmt: list[str]`
    :   The date the coupon was created, as GMT

    `date_expires: list[str]`
    :   The date the coupon expires

    `date_expires_gmt: list[str]`
    :   The date the coupon expires, as GMT

    `date_modified: list[str]`
    :   The date the coupon was last modified

    `date_modified_gmt: list[str]`
    :   The date the coupon was last modified, as GMT

    `description: list[str]`
    :   Coupon description

    `discount_type: list[str]`
    :   Determines the type of discount

    `email_restrictions: list[list[typing.Any]]`
    :   List of email addresses that can use this coupon

    `exclude_sale_items: list[bool]`
    :   If true, not applied to sale items

    `excluded_product_categories: list[list[typing.Any]]`
    :   Excluded category IDs

    `excluded_product_ids: list[list[typing.Any]]`
    :   Excluded product IDs

    `free_shipping: list[bool]`
    :   Enables free shipping

    `id: list[int]`
    :   Unique identifier

    `individual_use: list[bool]`
    :   Can only be used individually

    `limit_usage_to_x_items: list[int]`
    :   Max cart items coupon applies to

    `maximum_amount: list[str]`
    :   Maximum order amount

    `meta_data: list[list[typing.Any]]`
    :   Meta data

    `minimum_amount: list[str]`
    :   Minimum order amount

    `product_categories: list[list[typing.Any]]`
    :   Applicable category IDs

    `product_ids: list[list[typing.Any]]`
    :   Applicable product IDs

    `usage_count: list[int]`
    :   Times used

    `usage_limit: list[int]`
    :   Total usage limit

    `usage_limit_per_user: list[int]`
    :   Per-customer usage limit

    `used_by: list[list[typing.Any]]`
    :   Users who have used the coupon

<a id="CouponsKeywordCondition"></a>

`CouponsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.CouponsStringFilter`
    :   The type of the None singleton.

<a id="CouponsLikeCondition"></a>

`CouponsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.CouponsStringFilter`
    :   The type of the None singleton.

<a id="CouponsListParams"></a>

`CouponsListParams(*args, **kwargs)`
:   Parameters for coupons.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `before: str`
    :   The type of the None singleton.

    `code: str`
    :   The type of the None singleton.

    `modified_after: str`
    :   The type of the None singleton.

    `modified_before: str`
    :   The type of the None singleton.

    `order: str`
    :   The type of the None singleton.

    `orderby: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

<a id="CouponsLtCondition"></a>

`CouponsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.CouponsSearchFilter`
    :   The type of the None singleton.

<a id="CouponsLteCondition"></a>

`CouponsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.CouponsSearchFilter`
    :   The type of the None singleton.

<a id="CouponsNeqCondition"></a>

`CouponsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.CouponsSearchFilter`
    :   The type of the None singleton.

<a id="CouponsNotCondition"></a>

`CouponsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.CouponsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsAnyCondition`
    :   The type of the None singleton.

<a id="CouponsOrCondition"></a>

`CouponsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.CouponsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsAnyCondition]`
    :   The type of the None singleton.

<a id="CouponsSearchFilter"></a>

`CouponsSearchFilter(*args, **kwargs)`
:   Available fields for filtering coupons search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CouponsSearchQuery"></a>

`CouponsSearchQuery(*args, **kwargs)`
:   Search query for coupons entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.CouponsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.CouponsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.CouponsSortFilter]`
    :   The type of the None singleton.

<a id="CouponsSortFilter"></a>

`CouponsSortFilter(*args, **kwargs)`
:   Available fields for sorting coupons search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Literal['asc', 'desc']`
    :   The amount of discount

    `code: Literal['asc', 'desc']`
    :   Coupon code

    `date_created: Literal['asc', 'desc']`
    :   The date the coupon was created

    `date_created_gmt: Literal['asc', 'desc']`
    :   The date the coupon was created, as GMT

    `date_expires: Literal['asc', 'desc']`
    :   The date the coupon expires

    `date_expires_gmt: Literal['asc', 'desc']`
    :   The date the coupon expires, as GMT

    `date_modified: Literal['asc', 'desc']`
    :   The date the coupon was last modified

    `date_modified_gmt: Literal['asc', 'desc']`
    :   The date the coupon was last modified, as GMT

    `description: Literal['asc', 'desc']`
    :   Coupon description

    `discount_type: Literal['asc', 'desc']`
    :   Determines the type of discount

    `email_restrictions: Literal['asc', 'desc']`
    :   List of email addresses that can use this coupon

    `exclude_sale_items: Literal['asc', 'desc']`
    :   If true, not applied to sale items

    `excluded_product_categories: Literal['asc', 'desc']`
    :   Excluded category IDs

    `excluded_product_ids: Literal['asc', 'desc']`
    :   Excluded product IDs

    `free_shipping: Literal['asc', 'desc']`
    :   Enables free shipping

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `individual_use: Literal['asc', 'desc']`
    :   Can only be used individually

    `limit_usage_to_x_items: Literal['asc', 'desc']`
    :   Max cart items coupon applies to

    `maximum_amount: Literal['asc', 'desc']`
    :   Maximum order amount

    `meta_data: Literal['asc', 'desc']`
    :   Meta data

    `minimum_amount: Literal['asc', 'desc']`
    :   Minimum order amount

    `product_categories: Literal['asc', 'desc']`
    :   Applicable category IDs

    `product_ids: Literal['asc', 'desc']`
    :   Applicable product IDs

    `usage_count: Literal['asc', 'desc']`
    :   Times used

    `usage_limit: Literal['asc', 'desc']`
    :   Total usage limit

    `usage_limit_per_user: Literal['asc', 'desc']`
    :   Per-customer usage limit

    `used_by: Literal['asc', 'desc']`
    :   Users who have used the coupon

<a id="CouponsStringFilter"></a>

`CouponsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   The amount of discount

    `code: str`
    :   Coupon code

    `date_created: str`
    :   The date the coupon was created

    `date_created_gmt: str`
    :   The date the coupon was created, as GMT

    `date_expires: str`
    :   The date the coupon expires

    `date_expires_gmt: str`
    :   The date the coupon expires, as GMT

    `date_modified: str`
    :   The date the coupon was last modified

    `date_modified_gmt: str`
    :   The date the coupon was last modified, as GMT

    `description: str`
    :   Coupon description

    `discount_type: str`
    :   Determines the type of discount

    `email_restrictions: str`
    :   List of email addresses that can use this coupon

    `exclude_sale_items: str`
    :   If true, not applied to sale items

    `excluded_product_categories: str`
    :   Excluded category IDs

    `excluded_product_ids: str`
    :   Excluded product IDs

    `free_shipping: str`
    :   Enables free shipping

    `id: str`
    :   Unique identifier

    `individual_use: str`
    :   Can only be used individually

    `limit_usage_to_x_items: str`
    :   Max cart items coupon applies to

    `maximum_amount: str`
    :   Maximum order amount

    `meta_data: str`
    :   Meta data

    `minimum_amount: str`
    :   Minimum order amount

    `product_categories: str`
    :   Applicable category IDs

    `product_ids: str`
    :   Applicable product IDs

    `usage_count: str`
    :   Times used

    `usage_limit: str`
    :   Total usage limit

    `usage_limit_per_user: str`
    :   Per-customer usage limit

    `used_by: str`
    :   Users who have used the coupon

<a id="CustomersAndCondition"></a>

`CustomersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.CustomersEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersInCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersAnyCondition]`
    :   The type of the None singleton.

<a id="CustomersAnyCondition"></a>

`CustomersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.CustomersAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomersAnyValueFilter"></a>

`CustomersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: Any`
    :   Avatar URL

    `billing: Any`
    :   List of billing address data

    `date_created: Any`
    :   The date the customer was created, in the site's timezone

    `date_created_gmt: Any`
    :   The date the customer was created, as GMT

    `date_modified: Any`
    :   The date the customer was last modified, in the site's timezone

    `date_modified_gmt: Any`
    :   The date the customer was last modified, as GMT

    `email: Any`
    :   The email address for the customer

    `first_name: Any`
    :   Customer first name

    `id: Any`
    :   Unique identifier for the resource

    `is_paying_customer: Any`
    :   Is the customer a paying customer

    `last_name: Any`
    :   Customer last name

    `meta_data: Any`
    :   Meta data

    `role: Any`
    :   Customer role

    `shipping: Any`
    :   List of shipping address data

    `username: Any`
    :   Customer login name

<a id="CustomersContainsCondition"></a>

`CustomersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.CustomersAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomersEqCondition"></a>

`CustomersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersFuzzyCondition"></a>

`CustomersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.CustomersStringFilter`
    :   The type of the None singleton.

<a id="CustomersGetParams"></a>

`CustomersGetParams(*args, **kwargs)`
:   Parameters for customers.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CustomersGtCondition"></a>

`CustomersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersGteCondition"></a>

`CustomersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersInCondition"></a>

`CustomersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.CustomersInFilter`
    :   The type of the None singleton.

<a id="CustomersInFilter"></a>

`CustomersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: list[str]`
    :   Avatar URL

    `billing: list[dict[str, typing.Any]]`
    :   List of billing address data

    `date_created: list[str]`
    :   The date the customer was created, in the site's timezone

    `date_created_gmt: list[str]`
    :   The date the customer was created, as GMT

    `date_modified: list[str]`
    :   The date the customer was last modified, in the site's timezone

    `date_modified_gmt: list[str]`
    :   The date the customer was last modified, as GMT

    `email: list[str]`
    :   The email address for the customer

    `first_name: list[str]`
    :   Customer first name

    `id: list[int]`
    :   Unique identifier for the resource

    `is_paying_customer: list[bool]`
    :   Is the customer a paying customer

    `last_name: list[str]`
    :   Customer last name

    `meta_data: list[list[typing.Any]]`
    :   Meta data

    `role: list[str]`
    :   Customer role

    `shipping: list[dict[str, typing.Any]]`
    :   List of shipping address data

    `username: list[str]`
    :   Customer login name

<a id="CustomersKeywordCondition"></a>

`CustomersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.CustomersStringFilter`
    :   The type of the None singleton.

<a id="CustomersLikeCondition"></a>

`CustomersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.CustomersStringFilter`
    :   The type of the None singleton.

<a id="CustomersListParams"></a>

`CustomersListParams(*args, **kwargs)`
:   Parameters for customers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: str`
    :   The type of the None singleton.

    `order: str`
    :   The type of the None singleton.

    `orderby: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

<a id="CustomersLtCondition"></a>

`CustomersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersLteCondition"></a>

`CustomersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersNeqCondition"></a>

`CustomersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersNotCondition"></a>

`CustomersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.CustomersEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersInCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersAnyCondition`
    :   The type of the None singleton.

<a id="CustomersOrCondition"></a>

`CustomersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.CustomersEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersInCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersAnyCondition]`
    :   The type of the None singleton.

<a id="CustomersSearchFilter"></a>

`CustomersSearchFilter(*args, **kwargs)`
:   Available fields for filtering customers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

    `role: str | None`
    :   Customer role

    `shipping: dict[str, typing.Any] | None`
    :   List of shipping address data

    `username: str | None`
    :   Customer login name

<a id="CustomersSearchQuery"></a>

`CustomersSearchQuery(*args, **kwargs)`
:   Search query for customers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.CustomersEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersInCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.CustomersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.CustomersSortFilter]`
    :   The type of the None singleton.

<a id="CustomersSortFilter"></a>

`CustomersSortFilter(*args, **kwargs)`
:   Available fields for sorting customers search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: Literal['asc', 'desc']`
    :   Avatar URL

    `billing: Literal['asc', 'desc']`
    :   List of billing address data

    `date_created: Literal['asc', 'desc']`
    :   The date the customer was created, in the site's timezone

    `date_created_gmt: Literal['asc', 'desc']`
    :   The date the customer was created, as GMT

    `date_modified: Literal['asc', 'desc']`
    :   The date the customer was last modified, in the site's timezone

    `date_modified_gmt: Literal['asc', 'desc']`
    :   The date the customer was last modified, as GMT

    `email: Literal['asc', 'desc']`
    :   The email address for the customer

    `first_name: Literal['asc', 'desc']`
    :   Customer first name

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the resource

    `is_paying_customer: Literal['asc', 'desc']`
    :   Is the customer a paying customer

    `last_name: Literal['asc', 'desc']`
    :   Customer last name

    `meta_data: Literal['asc', 'desc']`
    :   Meta data

    `role: Literal['asc', 'desc']`
    :   Customer role

    `shipping: Literal['asc', 'desc']`
    :   List of shipping address data

    `username: Literal['asc', 'desc']`
    :   Customer login name

<a id="CustomersStringFilter"></a>

`CustomersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: str`
    :   Avatar URL

    `billing: str`
    :   List of billing address data

    `date_created: str`
    :   The date the customer was created, in the site's timezone

    `date_created_gmt: str`
    :   The date the customer was created, as GMT

    `date_modified: str`
    :   The date the customer was last modified, in the site's timezone

    `date_modified_gmt: str`
    :   The date the customer was last modified, as GMT

    `email: str`
    :   The email address for the customer

    `first_name: str`
    :   Customer first name

    `id: str`
    :   Unique identifier for the resource

    `is_paying_customer: str`
    :   Is the customer a paying customer

    `last_name: str`
    :   Customer last name

    `meta_data: str`
    :   Meta data

    `role: str`
    :   Customer role

    `shipping: str`
    :   List of shipping address data

    `username: str`
    :   Customer login name

<a id="OrderNotesAndCondition"></a>

`OrderNotesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesAnyCondition]`
    :   The type of the None singleton.

<a id="OrderNotesAnyCondition"></a>

`OrderNotesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesAnyValueFilter`
    :   The type of the None singleton.

<a id="OrderNotesAnyValueFilter"></a>

`OrderNotesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: Any`
    :   Order note author

    `date_created: Any`
    :   The date the order note was created

    `date_created_gmt: Any`
    :   The date the order note was created, as GMT

    `id: Any`
    :   Unique identifier

    `note: Any`
    :   Order note content

<a id="OrderNotesContainsCondition"></a>

`OrderNotesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesAnyValueFilter`
    :   The type of the None singleton.

<a id="OrderNotesEqCondition"></a>

`OrderNotesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesSearchFilter`
    :   The type of the None singleton.

<a id="OrderNotesFuzzyCondition"></a>

`OrderNotesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesStringFilter`
    :   The type of the None singleton.

<a id="OrderNotesGetParams"></a>

`OrderNotesGetParams(*args, **kwargs)`
:   Parameters for order_notes.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `order_id: str`
    :   The type of the None singleton.

<a id="OrderNotesGtCondition"></a>

`OrderNotesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesSearchFilter`
    :   The type of the None singleton.

<a id="OrderNotesGteCondition"></a>

`OrderNotesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesSearchFilter`
    :   The type of the None singleton.

<a id="OrderNotesInCondition"></a>

`OrderNotesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesInFilter`
    :   The type of the None singleton.

<a id="OrderNotesInFilter"></a>

`OrderNotesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: list[str]`
    :   Order note author

    `date_created: list[str]`
    :   The date the order note was created

    `date_created_gmt: list[str]`
    :   The date the order note was created, as GMT

    `id: list[int]`
    :   Unique identifier

    `note: list[str]`
    :   Order note content

<a id="OrderNotesKeywordCondition"></a>

`OrderNotesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesStringFilter`
    :   The type of the None singleton.

<a id="OrderNotesLikeCondition"></a>

`OrderNotesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesStringFilter`
    :   The type of the None singleton.

<a id="OrderNotesListParams"></a>

`OrderNotesListParams(*args, **kwargs)`
:   Parameters for order_notes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_id: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="OrderNotesLtCondition"></a>

`OrderNotesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesSearchFilter`
    :   The type of the None singleton.

<a id="OrderNotesLteCondition"></a>

`OrderNotesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesSearchFilter`
    :   The type of the None singleton.

<a id="OrderNotesNeqCondition"></a>

`OrderNotesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesSearchFilter`
    :   The type of the None singleton.

<a id="OrderNotesNotCondition"></a>

`OrderNotesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesAnyCondition`
    :   The type of the None singleton.

<a id="OrderNotesOrCondition"></a>

`OrderNotesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesAnyCondition]`
    :   The type of the None singleton.

<a id="OrderNotesSearchFilter"></a>

`OrderNotesSearchFilter(*args, **kwargs)`
:   Available fields for filtering order_notes search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: str | None`
    :   Order note author

    `date_created: str | None`
    :   The date the order note was created

    `date_created_gmt: str | None`
    :   The date the order note was created, as GMT

    `id: int | None`
    :   Unique identifier

    `note: str | None`
    :   Order note content

<a id="OrderNotesSearchQuery"></a>

`OrderNotesSearchQuery(*args, **kwargs)`
:   Search query for order_notes entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.OrderNotesSortFilter]`
    :   The type of the None singleton.

<a id="OrderNotesSortFilter"></a>

`OrderNotesSortFilter(*args, **kwargs)`
:   Available fields for sorting order_notes search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: Literal['asc', 'desc']`
    :   Order note author

    `date_created: Literal['asc', 'desc']`
    :   The date the order note was created

    `date_created_gmt: Literal['asc', 'desc']`
    :   The date the order note was created, as GMT

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `note: Literal['asc', 'desc']`
    :   Order note content

<a id="OrderNotesStringFilter"></a>

`OrderNotesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: str`
    :   Order note author

    `date_created: str`
    :   The date the order note was created

    `date_created_gmt: str`
    :   The date the order note was created, as GMT

    `id: str`
    :   Unique identifier

    `note: str`
    :   Order note content

<a id="OrdersAndCondition"></a>

`OrdersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.OrdersEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersInCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersAnyCondition]`
    :   The type of the None singleton.

<a id="OrdersAnyCondition"></a>

`OrdersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.OrdersAnyValueFilter`
    :   The type of the None singleton.

<a id="OrdersAnyValueFilter"></a>

`OrdersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billing: Any`
    :   Billing address

    `cart_hash: Any`
    :   MD5 hash of cart items to ensure orders are not modified

    `cart_tax: Any`
    :   Sum of line item taxes only

    `coupon_lines: Any`
    :   Coupons line data

    `created_via: Any`
    :   Shows where the order was created

    `currency: Any`
    :   Currency the order was created with, in ISO format

    `customer_id: Any`
    :   User ID who owns the order (0 for guests)

    `customer_ip_address: Any`
    :   Customer's IP address

    `customer_note: Any`
    :   Note left by the customer during checkout

    `customer_user_agent: Any`
    :   User agent of the customer

    `date_completed: Any`
    :   The date the order was completed, in the site's timezone

    `date_completed_gmt: Any`
    :   The date the order was completed, as GMT

    `date_created: Any`
    :   The date the order was created, in the site's timezone

    `date_created_gmt: Any`
    :   The date the order was created, as GMT

    `date_modified: Any`
    :   The date the order was last modified, in the site's timezone

    `date_modified_gmt: Any`
    :   The date the order was last modified, as GMT

    `date_paid: Any`
    :   The date the order was paid, in the site's timezone

    `date_paid_gmt: Any`
    :   The date the order was paid, as GMT

    `discount_tax: Any`
    :   Total discount tax amount for the order

    `discount_total: Any`
    :   Total discount amount for the order

    `fee_lines: Any`
    :   Fee lines data

    `id: Any`
    :   Unique identifier for the resource

    `line_items: Any`
    :   Line items data

    `meta_data: Any`
    :   Meta data

    `number: Any`
    :   Order number

    `order_key: Any`
    :   Order key

    `parent_id: Any`
    :   Parent order ID

    `payment_method: Any`
    :   Payment method ID

    `payment_method_title: Any`
    :   Payment method title

    `prices_include_tax: Any`
    :   True if the prices included tax during checkout

    `refunds: Any`
    :   List of refunds

    `shipping: Any`
    :   Shipping address

    `shipping_lines: Any`
    :   Shipping lines data

    `shipping_tax: Any`
    :   Total shipping tax amount for the order

    `shipping_total: Any`
    :   Total shipping amount for the order

    `status: Any`
    :   Order status

    `tax_lines: Any`
    :   Tax lines data

    `total: Any`
    :   Grand total

    `total_tax: Any`
    :   Sum of all taxes

    `transaction_id: Any`
    :   Unique transaction ID

    `version: Any`
    :   Version of WooCommerce which last updated the order

<a id="OrdersContainsCondition"></a>

`OrdersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.OrdersAnyValueFilter`
    :   The type of the None singleton.

<a id="OrdersEqCondition"></a>

`OrdersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.OrdersSearchFilter`
    :   The type of the None singleton.

<a id="OrdersFuzzyCondition"></a>

`OrdersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.OrdersStringFilter`
    :   The type of the None singleton.

<a id="OrdersGetParams"></a>

`OrdersGetParams(*args, **kwargs)`
:   Parameters for orders.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="OrdersGtCondition"></a>

`OrdersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.OrdersSearchFilter`
    :   The type of the None singleton.

<a id="OrdersGteCondition"></a>

`OrdersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.OrdersSearchFilter`
    :   The type of the None singleton.

<a id="OrdersInCondition"></a>

`OrdersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.OrdersInFilter`
    :   The type of the None singleton.

<a id="OrdersInFilter"></a>

`OrdersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billing: list[dict[str, typing.Any]]`
    :   Billing address

    `cart_hash: list[str]`
    :   MD5 hash of cart items to ensure orders are not modified

    `cart_tax: list[str]`
    :   Sum of line item taxes only

    `coupon_lines: list[list[typing.Any]]`
    :   Coupons line data

    `created_via: list[str]`
    :   Shows where the order was created

    `currency: list[str]`
    :   Currency the order was created with, in ISO format

    `customer_id: list[int]`
    :   User ID who owns the order (0 for guests)

    `customer_ip_address: list[str]`
    :   Customer's IP address

    `customer_note: list[str]`
    :   Note left by the customer during checkout

    `customer_user_agent: list[str]`
    :   User agent of the customer

    `date_completed: list[str]`
    :   The date the order was completed, in the site's timezone

    `date_completed_gmt: list[str]`
    :   The date the order was completed, as GMT

    `date_created: list[str]`
    :   The date the order was created, in the site's timezone

    `date_created_gmt: list[str]`
    :   The date the order was created, as GMT

    `date_modified: list[str]`
    :   The date the order was last modified, in the site's timezone

    `date_modified_gmt: list[str]`
    :   The date the order was last modified, as GMT

    `date_paid: list[str]`
    :   The date the order was paid, in the site's timezone

    `date_paid_gmt: list[str]`
    :   The date the order was paid, as GMT

    `discount_tax: list[str]`
    :   Total discount tax amount for the order

    `discount_total: list[str]`
    :   Total discount amount for the order

    `fee_lines: list[list[typing.Any]]`
    :   Fee lines data

    `id: list[int]`
    :   Unique identifier for the resource

    `line_items: list[list[typing.Any]]`
    :   Line items data

    `meta_data: list[list[typing.Any]]`
    :   Meta data

    `number: list[str]`
    :   Order number

    `order_key: list[str]`
    :   Order key

    `parent_id: list[int]`
    :   Parent order ID

    `payment_method: list[str]`
    :   Payment method ID

    `payment_method_title: list[str]`
    :   Payment method title

    `prices_include_tax: list[bool]`
    :   True if the prices included tax during checkout

    `refunds: list[list[typing.Any]]`
    :   List of refunds

    `shipping: list[dict[str, typing.Any]]`
    :   Shipping address

    `shipping_lines: list[list[typing.Any]]`
    :   Shipping lines data

    `shipping_tax: list[str]`
    :   Total shipping tax amount for the order

    `shipping_total: list[str]`
    :   Total shipping amount for the order

    `status: list[str]`
    :   Order status

    `tax_lines: list[list[typing.Any]]`
    :   Tax lines data

    `total: list[str]`
    :   Grand total

    `total_tax: list[str]`
    :   Sum of all taxes

    `transaction_id: list[str]`
    :   Unique transaction ID

    `version: list[str]`
    :   Version of WooCommerce which last updated the order

<a id="OrdersKeywordCondition"></a>

`OrdersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.OrdersStringFilter`
    :   The type of the None singleton.

<a id="OrdersLikeCondition"></a>

`OrdersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.OrdersStringFilter`
    :   The type of the None singleton.

<a id="OrdersListParams"></a>

`OrdersListParams(*args, **kwargs)`
:   Parameters for orders.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `before: str`
    :   The type of the None singleton.

    `customer: int`
    :   The type of the None singleton.

    `modified_after: str`
    :   The type of the None singleton.

    `modified_before: str`
    :   The type of the None singleton.

    `order: str`
    :   The type of the None singleton.

    `orderby: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `product: int`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

<a id="OrdersLtCondition"></a>

`OrdersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.OrdersSearchFilter`
    :   The type of the None singleton.

<a id="OrdersLteCondition"></a>

`OrdersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.OrdersSearchFilter`
    :   The type of the None singleton.

<a id="OrdersNeqCondition"></a>

`OrdersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.OrdersSearchFilter`
    :   The type of the None singleton.

<a id="OrdersNotCondition"></a>

`OrdersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.OrdersEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersInCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersAnyCondition`
    :   The type of the None singleton.

<a id="OrdersOrCondition"></a>

`OrdersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.OrdersEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersInCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersAnyCondition]`
    :   The type of the None singleton.

<a id="OrdersSearchFilter"></a>

`OrdersSearchFilter(*args, **kwargs)`
:   Available fields for filtering orders search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="OrdersSearchQuery"></a>

`OrdersSearchQuery(*args, **kwargs)`
:   Search query for orders entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.OrdersEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersInCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.OrdersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.OrdersSortFilter]`
    :   The type of the None singleton.

<a id="OrdersSortFilter"></a>

`OrdersSortFilter(*args, **kwargs)`
:   Available fields for sorting orders search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billing: Literal['asc', 'desc']`
    :   Billing address

    `cart_hash: Literal['asc', 'desc']`
    :   MD5 hash of cart items to ensure orders are not modified

    `cart_tax: Literal['asc', 'desc']`
    :   Sum of line item taxes only

    `coupon_lines: Literal['asc', 'desc']`
    :   Coupons line data

    `created_via: Literal['asc', 'desc']`
    :   Shows where the order was created

    `currency: Literal['asc', 'desc']`
    :   Currency the order was created with, in ISO format

    `customer_id: Literal['asc', 'desc']`
    :   User ID who owns the order (0 for guests)

    `customer_ip_address: Literal['asc', 'desc']`
    :   Customer's IP address

    `customer_note: Literal['asc', 'desc']`
    :   Note left by the customer during checkout

    `customer_user_agent: Literal['asc', 'desc']`
    :   User agent of the customer

    `date_completed: Literal['asc', 'desc']`
    :   The date the order was completed, in the site's timezone

    `date_completed_gmt: Literal['asc', 'desc']`
    :   The date the order was completed, as GMT

    `date_created: Literal['asc', 'desc']`
    :   The date the order was created, in the site's timezone

    `date_created_gmt: Literal['asc', 'desc']`
    :   The date the order was created, as GMT

    `date_modified: Literal['asc', 'desc']`
    :   The date the order was last modified, in the site's timezone

    `date_modified_gmt: Literal['asc', 'desc']`
    :   The date the order was last modified, as GMT

    `date_paid: Literal['asc', 'desc']`
    :   The date the order was paid, in the site's timezone

    `date_paid_gmt: Literal['asc', 'desc']`
    :   The date the order was paid, as GMT

    `discount_tax: Literal['asc', 'desc']`
    :   Total discount tax amount for the order

    `discount_total: Literal['asc', 'desc']`
    :   Total discount amount for the order

    `fee_lines: Literal['asc', 'desc']`
    :   Fee lines data

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the resource

    `line_items: Literal['asc', 'desc']`
    :   Line items data

    `meta_data: Literal['asc', 'desc']`
    :   Meta data

    `number: Literal['asc', 'desc']`
    :   Order number

    `order_key: Literal['asc', 'desc']`
    :   Order key

    `parent_id: Literal['asc', 'desc']`
    :   Parent order ID

    `payment_method: Literal['asc', 'desc']`
    :   Payment method ID

    `payment_method_title: Literal['asc', 'desc']`
    :   Payment method title

    `prices_include_tax: Literal['asc', 'desc']`
    :   True if the prices included tax during checkout

    `refunds: Literal['asc', 'desc']`
    :   List of refunds

    `shipping: Literal['asc', 'desc']`
    :   Shipping address

    `shipping_lines: Literal['asc', 'desc']`
    :   Shipping lines data

    `shipping_tax: Literal['asc', 'desc']`
    :   Total shipping tax amount for the order

    `shipping_total: Literal['asc', 'desc']`
    :   Total shipping amount for the order

    `status: Literal['asc', 'desc']`
    :   Order status

    `tax_lines: Literal['asc', 'desc']`
    :   Tax lines data

    `total: Literal['asc', 'desc']`
    :   Grand total

    `total_tax: Literal['asc', 'desc']`
    :   Sum of all taxes

    `transaction_id: Literal['asc', 'desc']`
    :   Unique transaction ID

    `version: Literal['asc', 'desc']`
    :   Version of WooCommerce which last updated the order

<a id="OrdersStringFilter"></a>

`OrdersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billing: str`
    :   Billing address

    `cart_hash: str`
    :   MD5 hash of cart items to ensure orders are not modified

    `cart_tax: str`
    :   Sum of line item taxes only

    `coupon_lines: str`
    :   Coupons line data

    `created_via: str`
    :   Shows where the order was created

    `currency: str`
    :   Currency the order was created with, in ISO format

    `customer_id: str`
    :   User ID who owns the order (0 for guests)

    `customer_ip_address: str`
    :   Customer's IP address

    `customer_note: str`
    :   Note left by the customer during checkout

    `customer_user_agent: str`
    :   User agent of the customer

    `date_completed: str`
    :   The date the order was completed, in the site's timezone

    `date_completed_gmt: str`
    :   The date the order was completed, as GMT

    `date_created: str`
    :   The date the order was created, in the site's timezone

    `date_created_gmt: str`
    :   The date the order was created, as GMT

    `date_modified: str`
    :   The date the order was last modified, in the site's timezone

    `date_modified_gmt: str`
    :   The date the order was last modified, as GMT

    `date_paid: str`
    :   The date the order was paid, in the site's timezone

    `date_paid_gmt: str`
    :   The date the order was paid, as GMT

    `discount_tax: str`
    :   Total discount tax amount for the order

    `discount_total: str`
    :   Total discount amount for the order

    `fee_lines: str`
    :   Fee lines data

    `id: str`
    :   Unique identifier for the resource

    `line_items: str`
    :   Line items data

    `meta_data: str`
    :   Meta data

    `number: str`
    :   Order number

    `order_key: str`
    :   Order key

    `parent_id: str`
    :   Parent order ID

    `payment_method: str`
    :   Payment method ID

    `payment_method_title: str`
    :   Payment method title

    `prices_include_tax: str`
    :   True if the prices included tax during checkout

    `refunds: str`
    :   List of refunds

    `shipping: str`
    :   Shipping address

    `shipping_lines: str`
    :   Shipping lines data

    `shipping_tax: str`
    :   Total shipping tax amount for the order

    `shipping_total: str`
    :   Total shipping amount for the order

    `status: str`
    :   Order status

    `tax_lines: str`
    :   Tax lines data

    `total: str`
    :   Grand total

    `total_tax: str`
    :   Sum of all taxes

    `transaction_id: str`
    :   Unique transaction ID

    `version: str`
    :   Version of WooCommerce which last updated the order

<a id="PaymentGatewaysAndCondition"></a>

`PaymentGatewaysAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysInCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysAnyCondition]`
    :   The type of the None singleton.

<a id="PaymentGatewaysAnyCondition"></a>

`PaymentGatewaysAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysAnyValueFilter`
    :   The type of the None singleton.

<a id="PaymentGatewaysAnyValueFilter"></a>

`PaymentGatewaysAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: Any`
    :   Payment gateway description on checkout

    `enabled: Any`
    :   Payment gateway enabled status

    `id: Any`
    :   Payment gateway ID

    `method_description: Any`
    :   Payment gateway method description

    `method_supports: Any`
    :   Supported features

    `method_title: Any`
    :   Payment gateway method title

    `order: Any`
    :   Payment gateway sort order

    `settings: Any`
    :   Payment gateway settings

    `title: Any`
    :   Payment gateway title on checkout

<a id="PaymentGatewaysContainsCondition"></a>

`PaymentGatewaysContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysAnyValueFilter`
    :   The type of the None singleton.

<a id="PaymentGatewaysEqCondition"></a>

`PaymentGatewaysEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysSearchFilter`
    :   The type of the None singleton.

<a id="PaymentGatewaysFuzzyCondition"></a>

`PaymentGatewaysFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysStringFilter`
    :   The type of the None singleton.

<a id="PaymentGatewaysGetParams"></a>

`PaymentGatewaysGetParams(*args, **kwargs)`
:   Parameters for payment_gateways.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="PaymentGatewaysGtCondition"></a>

`PaymentGatewaysGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysSearchFilter`
    :   The type of the None singleton.

<a id="PaymentGatewaysGteCondition"></a>

`PaymentGatewaysGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysSearchFilter`
    :   The type of the None singleton.

<a id="PaymentGatewaysInCondition"></a>

`PaymentGatewaysInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysInFilter`
    :   The type of the None singleton.

<a id="PaymentGatewaysInFilter"></a>

`PaymentGatewaysInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: list[str]`
    :   Payment gateway description on checkout

    `enabled: list[bool]`
    :   Payment gateway enabled status

    `id: list[str]`
    :   Payment gateway ID

    `method_description: list[str]`
    :   Payment gateway method description

    `method_supports: list[list[typing.Any]]`
    :   Supported features

    `method_title: list[str]`
    :   Payment gateway method title

    `order: list[typing.Any]`
    :   Payment gateway sort order

    `settings: list[dict[str, typing.Any]]`
    :   Payment gateway settings

    `title: list[str]`
    :   Payment gateway title on checkout

<a id="PaymentGatewaysKeywordCondition"></a>

`PaymentGatewaysKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysStringFilter`
    :   The type of the None singleton.

<a id="PaymentGatewaysLikeCondition"></a>

`PaymentGatewaysLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysStringFilter`
    :   The type of the None singleton.

<a id="PaymentGatewaysListParams"></a>

`PaymentGatewaysListParams(*args, **kwargs)`
:   Parameters for payment_gateways.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="PaymentGatewaysLtCondition"></a>

`PaymentGatewaysLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysSearchFilter`
    :   The type of the None singleton.

<a id="PaymentGatewaysLteCondition"></a>

`PaymentGatewaysLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysSearchFilter`
    :   The type of the None singleton.

<a id="PaymentGatewaysNeqCondition"></a>

`PaymentGatewaysNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysSearchFilter`
    :   The type of the None singleton.

<a id="PaymentGatewaysNotCondition"></a>

`PaymentGatewaysNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysInCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysAnyCondition`
    :   The type of the None singleton.

<a id="PaymentGatewaysOrCondition"></a>

`PaymentGatewaysOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysInCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysAnyCondition]`
    :   The type of the None singleton.

<a id="PaymentGatewaysSearchFilter"></a>

`PaymentGatewaysSearchFilter(*args, **kwargs)`
:   Available fields for filtering payment_gateways search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

    `order: Any`
    :   Payment gateway sort order

    `settings: dict[str, typing.Any] | None`
    :   Payment gateway settings

    `title: str | None`
    :   Payment gateway title on checkout

<a id="PaymentGatewaysSearchQuery"></a>

`PaymentGatewaysSearchQuery(*args, **kwargs)`
:   Search query for payment_gateways entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysInCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.PaymentGatewaysSortFilter]`
    :   The type of the None singleton.

<a id="PaymentGatewaysSortFilter"></a>

`PaymentGatewaysSortFilter(*args, **kwargs)`
:   Available fields for sorting payment_gateways search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: Literal['asc', 'desc']`
    :   Payment gateway description on checkout

    `enabled: Literal['asc', 'desc']`
    :   Payment gateway enabled status

    `id: Literal['asc', 'desc']`
    :   Payment gateway ID

    `method_description: Literal['asc', 'desc']`
    :   Payment gateway method description

    `method_supports: Literal['asc', 'desc']`
    :   Supported features

    `method_title: Literal['asc', 'desc']`
    :   Payment gateway method title

    `order: Literal['asc', 'desc']`
    :   Payment gateway sort order

    `settings: Literal['asc', 'desc']`
    :   Payment gateway settings

    `title: Literal['asc', 'desc']`
    :   Payment gateway title on checkout

<a id="PaymentGatewaysStringFilter"></a>

`PaymentGatewaysStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str`
    :   Payment gateway description on checkout

    `enabled: str`
    :   Payment gateway enabled status

    `id: str`
    :   Payment gateway ID

    `method_description: str`
    :   Payment gateway method description

    `method_supports: str`
    :   Supported features

    `method_title: str`
    :   Payment gateway method title

    `order: str`
    :   Payment gateway sort order

    `settings: str`
    :   Payment gateway settings

    `title: str`
    :   Payment gateway title on checkout

<a id="ProductAttributesAndCondition"></a>

`ProductAttributesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesAnyCondition]`
    :   The type of the None singleton.

<a id="ProductAttributesAnyCondition"></a>

`ProductAttributesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductAttributesAnyValueFilter"></a>

`ProductAttributesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `has_archives: Any`
    :   Enable/Disable attribute archives

    `id: Any`
    :   Unique identifier

    `name: Any`
    :   Attribute name

    `order_by: Any`
    :   Default sort order

    `slug: Any`
    :   Alphanumeric identifier

    `type_: Any`
    :   Type of attribute

<a id="ProductAttributesContainsCondition"></a>

`ProductAttributesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductAttributesEqCondition"></a>

`ProductAttributesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesSearchFilter`
    :   The type of the None singleton.

<a id="ProductAttributesFuzzyCondition"></a>

`ProductAttributesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesStringFilter`
    :   The type of the None singleton.

<a id="ProductAttributesGetParams"></a>

`ProductAttributesGetParams(*args, **kwargs)`
:   Parameters for product_attributes.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ProductAttributesGtCondition"></a>

`ProductAttributesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesSearchFilter`
    :   The type of the None singleton.

<a id="ProductAttributesGteCondition"></a>

`ProductAttributesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesSearchFilter`
    :   The type of the None singleton.

<a id="ProductAttributesInCondition"></a>

`ProductAttributesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesInFilter`
    :   The type of the None singleton.

<a id="ProductAttributesInFilter"></a>

`ProductAttributesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `has_archives: list[bool]`
    :   Enable/Disable attribute archives

    `id: list[int]`
    :   Unique identifier

    `name: list[str]`
    :   Attribute name

    `order_by: list[str]`
    :   Default sort order

    `slug: list[str]`
    :   Alphanumeric identifier

    `type_: list[str]`
    :   Type of attribute

<a id="ProductAttributesKeywordCondition"></a>

`ProductAttributesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesStringFilter`
    :   The type of the None singleton.

<a id="ProductAttributesLikeCondition"></a>

`ProductAttributesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesStringFilter`
    :   The type of the None singleton.

<a id="ProductAttributesListParams"></a>

`ProductAttributesListParams(*args, **kwargs)`
:   Parameters for product_attributes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="ProductAttributesLtCondition"></a>

`ProductAttributesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesSearchFilter`
    :   The type of the None singleton.

<a id="ProductAttributesLteCondition"></a>

`ProductAttributesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesSearchFilter`
    :   The type of the None singleton.

<a id="ProductAttributesNeqCondition"></a>

`ProductAttributesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesSearchFilter`
    :   The type of the None singleton.

<a id="ProductAttributesNotCondition"></a>

`ProductAttributesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesAnyCondition`
    :   The type of the None singleton.

<a id="ProductAttributesOrCondition"></a>

`ProductAttributesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesAnyCondition]`
    :   The type of the None singleton.

<a id="ProductAttributesSearchFilter"></a>

`ProductAttributesSearchFilter(*args, **kwargs)`
:   Available fields for filtering product_attributes search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `has_archives: bool | None`
    :   Enable/Disable attribute archives

    `id: int | None`
    :   Unique identifier

    `name: str | None`
    :   Attribute name

    `order_by: str | None`
    :   Default sort order

    `slug: str | None`
    :   Alphanumeric identifier

    `type_: str | None`
    :   Type of attribute

<a id="ProductAttributesSearchQuery"></a>

`ProductAttributesSearchQuery(*args, **kwargs)`
:   Search query for product_attributes entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductAttributesSortFilter]`
    :   The type of the None singleton.

<a id="ProductAttributesSortFilter"></a>

`ProductAttributesSortFilter(*args, **kwargs)`
:   Available fields for sorting product_attributes search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `has_archives: Literal['asc', 'desc']`
    :   Enable/Disable attribute archives

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `name: Literal['asc', 'desc']`
    :   Attribute name

    `order_by: Literal['asc', 'desc']`
    :   Default sort order

    `slug: Literal['asc', 'desc']`
    :   Alphanumeric identifier

    `type_: Literal['asc', 'desc']`
    :   Type of attribute

<a id="ProductAttributesStringFilter"></a>

`ProductAttributesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `has_archives: str`
    :   Enable/Disable attribute archives

    `id: str`
    :   Unique identifier

    `name: str`
    :   Attribute name

    `order_by: str`
    :   Default sort order

    `slug: str`
    :   Alphanumeric identifier

    `type_: str`
    :   Type of attribute

<a id="ProductCategoriesAndCondition"></a>

`ProductCategoriesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesAnyCondition]`
    :   The type of the None singleton.

<a id="ProductCategoriesAnyCondition"></a>

`ProductCategoriesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductCategoriesAnyValueFilter"></a>

`ProductCategoriesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: Any`
    :   Number of published products for the resource

    `description: Any`
    :   HTML description of the resource

    `display: Any`
    :   Category archive display type

    `id: Any`
    :   Unique identifier for the resource

    `image: Any`
    :   Image data

    `menu_order: Any`
    :   Menu order

    `name: Any`
    :   Category name

    `parent: Any`
    :   The ID for the parent of the resource

    `slug: Any`
    :   An alphanumeric identifier

<a id="ProductCategoriesContainsCondition"></a>

`ProductCategoriesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductCategoriesEqCondition"></a>

`ProductCategoriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="ProductCategoriesFuzzyCondition"></a>

`ProductCategoriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesStringFilter`
    :   The type of the None singleton.

<a id="ProductCategoriesGetParams"></a>

`ProductCategoriesGetParams(*args, **kwargs)`
:   Parameters for product_categories.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ProductCategoriesGtCondition"></a>

`ProductCategoriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="ProductCategoriesGteCondition"></a>

`ProductCategoriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="ProductCategoriesInCondition"></a>

`ProductCategoriesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesInFilter`
    :   The type of the None singleton.

<a id="ProductCategoriesInFilter"></a>

`ProductCategoriesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: list[int]`
    :   Number of published products for the resource

    `description: list[str]`
    :   HTML description of the resource

    `display: list[str]`
    :   Category archive display type

    `id: list[int]`
    :   Unique identifier for the resource

    `image: list[list[typing.Any]]`
    :   Image data

    `menu_order: list[int]`
    :   Menu order

    `name: list[str]`
    :   Category name

    `parent: list[int]`
    :   The ID for the parent of the resource

    `slug: list[str]`
    :   An alphanumeric identifier

<a id="ProductCategoriesKeywordCondition"></a>

`ProductCategoriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesStringFilter`
    :   The type of the None singleton.

<a id="ProductCategoriesLikeCondition"></a>

`ProductCategoriesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesStringFilter`
    :   The type of the None singleton.

<a id="ProductCategoriesListParams"></a>

`ProductCategoriesListParams(*args, **kwargs)`
:   Parameters for product_categories.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hide_empty: bool`
    :   The type of the None singleton.

    `order: str`
    :   The type of the None singleton.

    `orderby: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `parent: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `product: int`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

    `slug: str`
    :   The type of the None singleton.

<a id="ProductCategoriesLtCondition"></a>

`ProductCategoriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="ProductCategoriesLteCondition"></a>

`ProductCategoriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="ProductCategoriesNeqCondition"></a>

`ProductCategoriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="ProductCategoriesNotCondition"></a>

`ProductCategoriesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesAnyCondition`
    :   The type of the None singleton.

<a id="ProductCategoriesOrCondition"></a>

`ProductCategoriesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesAnyCondition]`
    :   The type of the None singleton.

<a id="ProductCategoriesSearchFilter"></a>

`ProductCategoriesSearchFilter(*args, **kwargs)`
:   Available fields for filtering product_categories search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

    `name: str | None`
    :   Category name

    `parent: int | None`
    :   The ID for the parent of the resource

    `slug: str | None`
    :   An alphanumeric identifier

<a id="ProductCategoriesSearchQuery"></a>

`ProductCategoriesSearchQuery(*args, **kwargs)`
:   Search query for product_categories entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductCategoriesSortFilter]`
    :   The type of the None singleton.

<a id="ProductCategoriesSortFilter"></a>

`ProductCategoriesSortFilter(*args, **kwargs)`
:   Available fields for sorting product_categories search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: Literal['asc', 'desc']`
    :   Number of published products for the resource

    `description: Literal['asc', 'desc']`
    :   HTML description of the resource

    `display: Literal['asc', 'desc']`
    :   Category archive display type

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the resource

    `image: Literal['asc', 'desc']`
    :   Image data

    `menu_order: Literal['asc', 'desc']`
    :   Menu order

    `name: Literal['asc', 'desc']`
    :   Category name

    `parent: Literal['asc', 'desc']`
    :   The ID for the parent of the resource

    `slug: Literal['asc', 'desc']`
    :   An alphanumeric identifier

<a id="ProductCategoriesStringFilter"></a>

`ProductCategoriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   Number of published products for the resource

    `description: str`
    :   HTML description of the resource

    `display: str`
    :   Category archive display type

    `id: str`
    :   Unique identifier for the resource

    `image: str`
    :   Image data

    `menu_order: str`
    :   Menu order

    `name: str`
    :   Category name

    `parent: str`
    :   The ID for the parent of the resource

    `slug: str`
    :   An alphanumeric identifier

<a id="ProductReviewsAndCondition"></a>

`ProductReviewsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsAnyCondition]`
    :   The type of the None singleton.

<a id="ProductReviewsAnyCondition"></a>

`ProductReviewsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductReviewsAnyValueFilter"></a>

`ProductReviewsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_created: Any`
    :   The date the review was created

    `date_created_gmt: Any`
    :   The date the review was created, as GMT

    `id: Any`
    :   Unique identifier

    `product_id: Any`
    :   Product the review belongs to

    `rating: Any`
    :   Review rating (0 to 5)

    `review: Any`
    :   The content of the review

    `reviewer: Any`
    :   Reviewer name

    `reviewer_email: Any`
    :   Reviewer email

    `status: Any`
    :   Status of the review

    `verified: Any`
    :   Shows if the reviewer bought the product

<a id="ProductReviewsContainsCondition"></a>

`ProductReviewsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductReviewsEqCondition"></a>

`ProductReviewsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsSearchFilter`
    :   The type of the None singleton.

<a id="ProductReviewsFuzzyCondition"></a>

`ProductReviewsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsStringFilter`
    :   The type of the None singleton.

<a id="ProductReviewsGetParams"></a>

`ProductReviewsGetParams(*args, **kwargs)`
:   Parameters for product_reviews.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ProductReviewsGtCondition"></a>

`ProductReviewsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsSearchFilter`
    :   The type of the None singleton.

<a id="ProductReviewsGteCondition"></a>

`ProductReviewsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsSearchFilter`
    :   The type of the None singleton.

<a id="ProductReviewsInCondition"></a>

`ProductReviewsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsInFilter`
    :   The type of the None singleton.

<a id="ProductReviewsInFilter"></a>

`ProductReviewsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_created: list[str]`
    :   The date the review was created

    `date_created_gmt: list[str]`
    :   The date the review was created, as GMT

    `id: list[int]`
    :   Unique identifier

    `product_id: list[int]`
    :   Product the review belongs to

    `rating: list[int]`
    :   Review rating (0 to 5)

    `review: list[str]`
    :   The content of the review

    `reviewer: list[str]`
    :   Reviewer name

    `reviewer_email: list[str]`
    :   Reviewer email

    `status: list[str]`
    :   Status of the review

    `verified: list[bool]`
    :   Shows if the reviewer bought the product

<a id="ProductReviewsKeywordCondition"></a>

`ProductReviewsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsStringFilter`
    :   The type of the None singleton.

<a id="ProductReviewsLikeCondition"></a>

`ProductReviewsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsStringFilter`
    :   The type of the None singleton.

<a id="ProductReviewsListParams"></a>

`ProductReviewsListParams(*args, **kwargs)`
:   Parameters for product_reviews.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `before: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `product: list[int]`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

<a id="ProductReviewsLtCondition"></a>

`ProductReviewsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsSearchFilter`
    :   The type of the None singleton.

<a id="ProductReviewsLteCondition"></a>

`ProductReviewsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsSearchFilter`
    :   The type of the None singleton.

<a id="ProductReviewsNeqCondition"></a>

`ProductReviewsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsSearchFilter`
    :   The type of the None singleton.

<a id="ProductReviewsNotCondition"></a>

`ProductReviewsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsAnyCondition`
    :   The type of the None singleton.

<a id="ProductReviewsOrCondition"></a>

`ProductReviewsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsAnyCondition]`
    :   The type of the None singleton.

<a id="ProductReviewsSearchFilter"></a>

`ProductReviewsSearchFilter(*args, **kwargs)`
:   Available fields for filtering product_reviews search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_created: str | None`
    :   The date the review was created

    `date_created_gmt: str | None`
    :   The date the review was created, as GMT

    `id: int | None`
    :   Unique identifier

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

<a id="ProductReviewsSearchQuery"></a>

`ProductReviewsSearchQuery(*args, **kwargs)`
:   Search query for product_reviews entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductReviewsSortFilter]`
    :   The type of the None singleton.

<a id="ProductReviewsSortFilter"></a>

`ProductReviewsSortFilter(*args, **kwargs)`
:   Available fields for sorting product_reviews search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_created: Literal['asc', 'desc']`
    :   The date the review was created

    `date_created_gmt: Literal['asc', 'desc']`
    :   The date the review was created, as GMT

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `product_id: Literal['asc', 'desc']`
    :   Product the review belongs to

    `rating: Literal['asc', 'desc']`
    :   Review rating (0 to 5)

    `review: Literal['asc', 'desc']`
    :   The content of the review

    `reviewer: Literal['asc', 'desc']`
    :   Reviewer name

    `reviewer_email: Literal['asc', 'desc']`
    :   Reviewer email

    `status: Literal['asc', 'desc']`
    :   Status of the review

    `verified: Literal['asc', 'desc']`
    :   Shows if the reviewer bought the product

<a id="ProductReviewsStringFilter"></a>

`ProductReviewsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_created: str`
    :   The date the review was created

    `date_created_gmt: str`
    :   The date the review was created, as GMT

    `id: str`
    :   Unique identifier

    `product_id: str`
    :   Product the review belongs to

    `rating: str`
    :   Review rating (0 to 5)

    `review: str`
    :   The content of the review

    `reviewer: str`
    :   Reviewer name

    `reviewer_email: str`
    :   Reviewer email

    `status: str`
    :   Status of the review

    `verified: str`
    :   Shows if the reviewer bought the product

<a id="ProductTagsAndCondition"></a>

`ProductTagsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsAnyCondition]`
    :   The type of the None singleton.

<a id="ProductTagsAnyCondition"></a>

`ProductTagsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductTagsAnyValueFilter"></a>

`ProductTagsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: Any`
    :   Number of published products

    `description: Any`
    :   HTML description

    `id: Any`
    :   Unique identifier

    `name: Any`
    :   Tag name

    `slug: Any`
    :   Alphanumeric identifier

<a id="ProductTagsContainsCondition"></a>

`ProductTagsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductTagsEqCondition"></a>

`ProductTagsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsSearchFilter`
    :   The type of the None singleton.

<a id="ProductTagsFuzzyCondition"></a>

`ProductTagsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsStringFilter`
    :   The type of the None singleton.

<a id="ProductTagsGetParams"></a>

`ProductTagsGetParams(*args, **kwargs)`
:   Parameters for product_tags.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ProductTagsGtCondition"></a>

`ProductTagsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsSearchFilter`
    :   The type of the None singleton.

<a id="ProductTagsGteCondition"></a>

`ProductTagsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsSearchFilter`
    :   The type of the None singleton.

<a id="ProductTagsInCondition"></a>

`ProductTagsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsInFilter`
    :   The type of the None singleton.

<a id="ProductTagsInFilter"></a>

`ProductTagsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: list[int]`
    :   Number of published products

    `description: list[str]`
    :   HTML description

    `id: list[int]`
    :   Unique identifier

    `name: list[str]`
    :   Tag name

    `slug: list[str]`
    :   Alphanumeric identifier

<a id="ProductTagsKeywordCondition"></a>

`ProductTagsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsStringFilter`
    :   The type of the None singleton.

<a id="ProductTagsLikeCondition"></a>

`ProductTagsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsStringFilter`
    :   The type of the None singleton.

<a id="ProductTagsListParams"></a>

`ProductTagsListParams(*args, **kwargs)`
:   Parameters for product_tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hide_empty: bool`
    :   The type of the None singleton.

    `order: str`
    :   The type of the None singleton.

    `orderby: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `product: int`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

    `slug: str`
    :   The type of the None singleton.

<a id="ProductTagsLtCondition"></a>

`ProductTagsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsSearchFilter`
    :   The type of the None singleton.

<a id="ProductTagsLteCondition"></a>

`ProductTagsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsSearchFilter`
    :   The type of the None singleton.

<a id="ProductTagsNeqCondition"></a>

`ProductTagsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsSearchFilter`
    :   The type of the None singleton.

<a id="ProductTagsNotCondition"></a>

`ProductTagsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsAnyCondition`
    :   The type of the None singleton.

<a id="ProductTagsOrCondition"></a>

`ProductTagsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsAnyCondition]`
    :   The type of the None singleton.

<a id="ProductTagsSearchFilter"></a>

`ProductTagsSearchFilter(*args, **kwargs)`
:   Available fields for filtering product_tags search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: int | None`
    :   Number of published products

    `description: str | None`
    :   HTML description

    `id: int | None`
    :   Unique identifier

    `name: str | None`
    :   Tag name

    `slug: str | None`
    :   Alphanumeric identifier

<a id="ProductTagsSearchQuery"></a>

`ProductTagsSearchQuery(*args, **kwargs)`
:   Search query for product_tags entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductTagsSortFilter]`
    :   The type of the None singleton.

<a id="ProductTagsSortFilter"></a>

`ProductTagsSortFilter(*args, **kwargs)`
:   Available fields for sorting product_tags search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: Literal['asc', 'desc']`
    :   Number of published products

    `description: Literal['asc', 'desc']`
    :   HTML description

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `name: Literal['asc', 'desc']`
    :   Tag name

    `slug: Literal['asc', 'desc']`
    :   Alphanumeric identifier

<a id="ProductTagsStringFilter"></a>

`ProductTagsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   Number of published products

    `description: str`
    :   HTML description

    `id: str`
    :   Unique identifier

    `name: str`
    :   Tag name

    `slug: str`
    :   Alphanumeric identifier

<a id="ProductVariationsAndCondition"></a>

`ProductVariationsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsAnyCondition]`
    :   The type of the None singleton.

<a id="ProductVariationsAnyCondition"></a>

`ProductVariationsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductVariationsAnyValueFilter"></a>

`ProductVariationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Any`
    :   List of attributes

    `backordered: Any`
    :   On backordered

    `backorders: Any`
    :   Backorders allowed setting

    `backorders_allowed: Any`
    :   Shows if backorders are allowed

    `date_created: Any`
    :   The date the variation was created

    `date_created_gmt: Any`
    :   The date the variation was created, as GMT

    `date_modified: Any`
    :   The date the variation was last modified

    `date_modified_gmt: Any`
    :   The date the variation was last modified, as GMT

    `date_on_sale_from: Any`
    :   Start date of sale price

    `date_on_sale_from_gmt: Any`
    :   Start date of sale price, as GMT

    `date_on_sale_to: Any`
    :   End date of sale price

    `date_on_sale_to_gmt: Any`
    :   End date of sale price, as GMT

    `description: Any`
    :   Variation description

    `dimensions: Any`
    :   Variation dimensions

    `download_expiry: Any`
    :   Days until access expires

    `download_limit: Any`
    :   Download limit

    `downloadable: Any`
    :   If downloadable

    `downloads: Any`
    :   Downloadable files

    `id: Any`
    :   Unique identifier

    `image: Any`
    :   Variation image data

    `manage_stock: Any`
    :   Stock management at variation level

    `menu_order: Any`
    :   Menu order

    `meta_data: Any`
    :   Meta data

    `on_sale: Any`
    :   Shows if on sale

    `permalink: Any`
    :   Variation URL

    `price: Any`
    :   Current variation price

    `purchasable: Any`
    :   Can be bought

    `regular_price: Any`
    :   Variation regular price

    `sale_price: Any`
    :   Variation sale price

    `shipping_class: Any`
    :   Shipping class slug

    `shipping_class_id: Any`
    :   Shipping class ID

    `sku: Any`
    :   Unique identifier (SKU)

    `status: Any`
    :   Variation status

    `stock_quantity: Any`
    :   Stock quantity

    `stock_status: Any`
    :   Controls the stock status

    `tax_class: Any`
    :   Tax class

    `tax_status: Any`
    :   Tax status

    `virtual: Any`
    :   If virtual

    `weight: Any`
    :   Variation weight

<a id="ProductVariationsContainsCondition"></a>

`ProductVariationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductVariationsEqCondition"></a>

`ProductVariationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsSearchFilter`
    :   The type of the None singleton.

<a id="ProductVariationsFuzzyCondition"></a>

`ProductVariationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsStringFilter`
    :   The type of the None singleton.

<a id="ProductVariationsGetParams"></a>

`ProductVariationsGetParams(*args, **kwargs)`
:   Parameters for product_variations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `product_id: str`
    :   The type of the None singleton.

<a id="ProductVariationsGtCondition"></a>

`ProductVariationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsSearchFilter`
    :   The type of the None singleton.

<a id="ProductVariationsGteCondition"></a>

`ProductVariationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsSearchFilter`
    :   The type of the None singleton.

<a id="ProductVariationsInCondition"></a>

`ProductVariationsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsInFilter`
    :   The type of the None singleton.

<a id="ProductVariationsInFilter"></a>

`ProductVariationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: list[list[typing.Any]]`
    :   List of attributes

    `backordered: list[bool]`
    :   On backordered

    `backorders: list[str]`
    :   Backorders allowed setting

    `backorders_allowed: list[bool]`
    :   Shows if backorders are allowed

    `date_created: list[str]`
    :   The date the variation was created

    `date_created_gmt: list[str]`
    :   The date the variation was created, as GMT

    `date_modified: list[str]`
    :   The date the variation was last modified

    `date_modified_gmt: list[str]`
    :   The date the variation was last modified, as GMT

    `date_on_sale_from: list[str]`
    :   Start date of sale price

    `date_on_sale_from_gmt: list[str]`
    :   Start date of sale price, as GMT

    `date_on_sale_to: list[str]`
    :   End date of sale price

    `date_on_sale_to_gmt: list[str]`
    :   End date of sale price, as GMT

    `description: list[str]`
    :   Variation description

    `dimensions: list[dict[str, typing.Any]]`
    :   Variation dimensions

    `download_expiry: list[int]`
    :   Days until access expires

    `download_limit: list[int]`
    :   Download limit

    `downloadable: list[bool]`
    :   If downloadable

    `downloads: list[list[typing.Any]]`
    :   Downloadable files

    `id: list[int]`
    :   Unique identifier

    `image: list[list[typing.Any]]`
    :   Variation image data

    `manage_stock: list[str]`
    :   Stock management at variation level

    `menu_order: list[int]`
    :   Menu order

    `meta_data: list[list[typing.Any]]`
    :   Meta data

    `on_sale: list[bool]`
    :   Shows if on sale

    `permalink: list[str]`
    :   Variation URL

    `price: list[str]`
    :   Current variation price

    `purchasable: list[bool]`
    :   Can be bought

    `regular_price: list[str]`
    :   Variation regular price

    `sale_price: list[str]`
    :   Variation sale price

    `shipping_class: list[str]`
    :   Shipping class slug

    `shipping_class_id: list[int]`
    :   Shipping class ID

    `sku: list[str]`
    :   Unique identifier (SKU)

    `status: list[str]`
    :   Variation status

    `stock_quantity: list[int]`
    :   Stock quantity

    `stock_status: list[str]`
    :   Controls the stock status

    `tax_class: list[str]`
    :   Tax class

    `tax_status: list[str]`
    :   Tax status

    `virtual: list[bool]`
    :   If virtual

    `weight: list[str]`
    :   Variation weight

<a id="ProductVariationsKeywordCondition"></a>

`ProductVariationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsStringFilter`
    :   The type of the None singleton.

<a id="ProductVariationsLikeCondition"></a>

`ProductVariationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsStringFilter`
    :   The type of the None singleton.

<a id="ProductVariationsListParams"></a>

`ProductVariationsListParams(*args, **kwargs)`
:   Parameters for product_variations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `max_price: str`
    :   The type of the None singleton.

    `min_price: str`
    :   The type of the None singleton.

    `on_sale: bool`
    :   The type of the None singleton.

    `order: str`
    :   The type of the None singleton.

    `orderby: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `product_id: str`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

    `sku: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `stock_status: str`
    :   The type of the None singleton.

<a id="ProductVariationsLtCondition"></a>

`ProductVariationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsSearchFilter`
    :   The type of the None singleton.

<a id="ProductVariationsLteCondition"></a>

`ProductVariationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsSearchFilter`
    :   The type of the None singleton.

<a id="ProductVariationsNeqCondition"></a>

`ProductVariationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsSearchFilter`
    :   The type of the None singleton.

<a id="ProductVariationsNotCondition"></a>

`ProductVariationsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsAnyCondition`
    :   The type of the None singleton.

<a id="ProductVariationsOrCondition"></a>

`ProductVariationsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsAnyCondition]`
    :   The type of the None singleton.

<a id="ProductVariationsSearchFilter"></a>

`ProductVariationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering product_variations search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="ProductVariationsSearchQuery"></a>

`ProductVariationsSearchQuery(*args, **kwargs)`
:   Search query for product_variations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductVariationsSortFilter]`
    :   The type of the None singleton.

<a id="ProductVariationsSortFilter"></a>

`ProductVariationsSortFilter(*args, **kwargs)`
:   Available fields for sorting product_variations search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Literal['asc', 'desc']`
    :   List of attributes

    `backordered: Literal['asc', 'desc']`
    :   On backordered

    `backorders: Literal['asc', 'desc']`
    :   Backorders allowed setting

    `backorders_allowed: Literal['asc', 'desc']`
    :   Shows if backorders are allowed

    `date_created: Literal['asc', 'desc']`
    :   The date the variation was created

    `date_created_gmt: Literal['asc', 'desc']`
    :   The date the variation was created, as GMT

    `date_modified: Literal['asc', 'desc']`
    :   The date the variation was last modified

    `date_modified_gmt: Literal['asc', 'desc']`
    :   The date the variation was last modified, as GMT

    `date_on_sale_from: Literal['asc', 'desc']`
    :   Start date of sale price

    `date_on_sale_from_gmt: Literal['asc', 'desc']`
    :   Start date of sale price, as GMT

    `date_on_sale_to: Literal['asc', 'desc']`
    :   End date of sale price

    `date_on_sale_to_gmt: Literal['asc', 'desc']`
    :   End date of sale price, as GMT

    `description: Literal['asc', 'desc']`
    :   Variation description

    `dimensions: Literal['asc', 'desc']`
    :   Variation dimensions

    `download_expiry: Literal['asc', 'desc']`
    :   Days until access expires

    `download_limit: Literal['asc', 'desc']`
    :   Download limit

    `downloadable: Literal['asc', 'desc']`
    :   If downloadable

    `downloads: Literal['asc', 'desc']`
    :   Downloadable files

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `image: Literal['asc', 'desc']`
    :   Variation image data

    `manage_stock: Literal['asc', 'desc']`
    :   Stock management at variation level

    `menu_order: Literal['asc', 'desc']`
    :   Menu order

    `meta_data: Literal['asc', 'desc']`
    :   Meta data

    `on_sale: Literal['asc', 'desc']`
    :   Shows if on sale

    `permalink: Literal['asc', 'desc']`
    :   Variation URL

    `price: Literal['asc', 'desc']`
    :   Current variation price

    `purchasable: Literal['asc', 'desc']`
    :   Can be bought

    `regular_price: Literal['asc', 'desc']`
    :   Variation regular price

    `sale_price: Literal['asc', 'desc']`
    :   Variation sale price

    `shipping_class: Literal['asc', 'desc']`
    :   Shipping class slug

    `shipping_class_id: Literal['asc', 'desc']`
    :   Shipping class ID

    `sku: Literal['asc', 'desc']`
    :   Unique identifier (SKU)

    `status: Literal['asc', 'desc']`
    :   Variation status

    `stock_quantity: Literal['asc', 'desc']`
    :   Stock quantity

    `stock_status: Literal['asc', 'desc']`
    :   Controls the stock status

    `tax_class: Literal['asc', 'desc']`
    :   Tax class

    `tax_status: Literal['asc', 'desc']`
    :   Tax status

    `virtual: Literal['asc', 'desc']`
    :   If virtual

    `weight: Literal['asc', 'desc']`
    :   Variation weight

<a id="ProductVariationsStringFilter"></a>

`ProductVariationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: str`
    :   List of attributes

    `backordered: str`
    :   On backordered

    `backorders: str`
    :   Backorders allowed setting

    `backorders_allowed: str`
    :   Shows if backorders are allowed

    `date_created: str`
    :   The date the variation was created

    `date_created_gmt: str`
    :   The date the variation was created, as GMT

    `date_modified: str`
    :   The date the variation was last modified

    `date_modified_gmt: str`
    :   The date the variation was last modified, as GMT

    `date_on_sale_from: str`
    :   Start date of sale price

    `date_on_sale_from_gmt: str`
    :   Start date of sale price, as GMT

    `date_on_sale_to: str`
    :   End date of sale price

    `date_on_sale_to_gmt: str`
    :   End date of sale price, as GMT

    `description: str`
    :   Variation description

    `dimensions: str`
    :   Variation dimensions

    `download_expiry: str`
    :   Days until access expires

    `download_limit: str`
    :   Download limit

    `downloadable: str`
    :   If downloadable

    `downloads: str`
    :   Downloadable files

    `id: str`
    :   Unique identifier

    `image: str`
    :   Variation image data

    `manage_stock: str`
    :   Stock management at variation level

    `menu_order: str`
    :   Menu order

    `meta_data: str`
    :   Meta data

    `on_sale: str`
    :   Shows if on sale

    `permalink: str`
    :   Variation URL

    `price: str`
    :   Current variation price

    `purchasable: str`
    :   Can be bought

    `regular_price: str`
    :   Variation regular price

    `sale_price: str`
    :   Variation sale price

    `shipping_class: str`
    :   Shipping class slug

    `shipping_class_id: str`
    :   Shipping class ID

    `sku: str`
    :   Unique identifier (SKU)

    `status: str`
    :   Variation status

    `stock_quantity: str`
    :   Stock quantity

    `stock_status: str`
    :   Controls the stock status

    `tax_class: str`
    :   Tax class

    `tax_status: str`
    :   Tax status

    `virtual: str`
    :   If virtual

    `weight: str`
    :   Variation weight

<a id="ProductsAndCondition"></a>

`ProductsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsAnyCondition]`
    :   The type of the None singleton.

<a id="ProductsAnyCondition"></a>

`ProductsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.ProductsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductsAnyValueFilter"></a>

`ProductsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Any`
    :   List of attributes

    `average_rating: Any`
    :   Reviews average rating

    `backordered: Any`
    :   Shows if the product is on backordered

    `backorders: Any`
    :   If managing stock, this controls if backorders are allowed

    `backorders_allowed: Any`
    :   Shows if backorders are allowed

    `button_text: Any`
    :   Product external button text

    `catalog_visibility: Any`
    :   Catalog visibility

    `categories: Any`
    :   List of categories

    `cross_sell_ids: Any`
    :   List of cross-sell products IDs

    `date_created: Any`
    :   The date the product was created

    `date_created_gmt: Any`
    :   The date the product was created, as GMT

    `date_modified: Any`
    :   The date the product was last modified

    `date_modified_gmt: Any`
    :   The date the product was last modified, as GMT

    `date_on_sale_from: Any`
    :   Start date of sale price

    `date_on_sale_from_gmt: Any`
    :   Start date of sale price, as GMT

    `date_on_sale_to: Any`
    :   End date of sale price

    `date_on_sale_to_gmt: Any`
    :   End date of sale price, as GMT

    `default_attributes: Any`
    :   Defaults variation attributes

    `description: Any`
    :   Product description

    `dimensions: Any`
    :   Product dimensions

    `download_expiry: Any`
    :   Number of days until access to downloadable files expires

    `download_limit: Any`
    :   Number of times downloadable files can be downloaded

    `downloadable: Any`
    :   If the product is downloadable

    `downloads: Any`
    :   List of downloadable files

    `external_url: Any`
    :   Product external URL

    `grouped_products: Any`
    :   List of grouped products ID

    `id: Any`
    :   Unique identifier for the resource

    `images: Any`
    :   List of images

    `manage_stock: Any`
    :   Stock management at product level

    `menu_order: Any`
    :   Menu order

    `meta_data: Any`
    :   Meta data

    `name: Any`
    :   Product name

    `on_sale: Any`
    :   Shows if the product is on sale

    `parent_id: Any`
    :   Product parent ID

    `permalink: Any`
    :   Product URL

    `price: Any`
    :   Current product price

    `price_html: Any`
    :   Price formatted in HTML

    `purchasable: Any`
    :   Shows if the product can be bought

    `purchase_note: Any`
    :   Note to send customer after purchase

    `rating_count: Any`
    :   Amount of reviews

    `regular_price: Any`
    :   Product regular price

    `related_ids: Any`
    :   List of related products IDs

    `reviews_allowed: Any`
    :   Allow reviews

    `sale_price: Any`
    :   Product sale price

    `shipping_class: Any`
    :   Shipping class slug

    `shipping_class_id: Any`
    :   Shipping class ID

    `shipping_required: Any`
    :   Shows if the product needs to be shipped

    `shipping_taxable: Any`
    :   Shows if product shipping is taxable

    `short_description: Any`
    :   Product short description

    `sku: Any`
    :   Unique identifier (SKU)

    `slug: Any`
    :   Product slug

    `sold_individually: Any`
    :   Allow one item per order

    `status: Any`
    :   Product status

    `stock_quantity: Any`
    :   Stock quantity

    `stock_status: Any`
    :   Controls the stock status

    `tags: Any`
    :   List of tags

    `tax_class: Any`
    :   Tax class

    `tax_status: Any`
    :   Tax status

    `total_sales: Any`
    :   Amount of sales

    `type_: Any`
    :   Product type

    `upsell_ids: Any`
    :   List of up-sell products IDs

    `variations: Any`
    :   List of variations IDs

    `virtual: Any`
    :   If the product is virtual

    `weight: Any`
    :   Product weight

<a id="ProductsContainsCondition"></a>

`ProductsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.ProductsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductsEqCondition"></a>

`ProductsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.ProductsSearchFilter`
    :   The type of the None singleton.

<a id="ProductsFuzzyCondition"></a>

`ProductsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.ProductsStringFilter`
    :   The type of the None singleton.

<a id="ProductsGetParams"></a>

`ProductsGetParams(*args, **kwargs)`
:   Parameters for products.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ProductsGtCondition"></a>

`ProductsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.ProductsSearchFilter`
    :   The type of the None singleton.

<a id="ProductsGteCondition"></a>

`ProductsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.ProductsSearchFilter`
    :   The type of the None singleton.

<a id="ProductsInCondition"></a>

`ProductsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.ProductsInFilter`
    :   The type of the None singleton.

<a id="ProductsInFilter"></a>

`ProductsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: list[list[typing.Any]]`
    :   List of attributes

    `average_rating: list[str]`
    :   Reviews average rating

    `backordered: list[bool]`
    :   Shows if the product is on backordered

    `backorders: list[str]`
    :   If managing stock, this controls if backorders are allowed

    `backorders_allowed: list[bool]`
    :   Shows if backorders are allowed

    `button_text: list[str]`
    :   Product external button text

    `catalog_visibility: list[str]`
    :   Catalog visibility

    `categories: list[list[typing.Any]]`
    :   List of categories

    `cross_sell_ids: list[list[typing.Any]]`
    :   List of cross-sell products IDs

    `date_created: list[str]`
    :   The date the product was created

    `date_created_gmt: list[str]`
    :   The date the product was created, as GMT

    `date_modified: list[str]`
    :   The date the product was last modified

    `date_modified_gmt: list[str]`
    :   The date the product was last modified, as GMT

    `date_on_sale_from: list[str]`
    :   Start date of sale price

    `date_on_sale_from_gmt: list[str]`
    :   Start date of sale price, as GMT

    `date_on_sale_to: list[str]`
    :   End date of sale price

    `date_on_sale_to_gmt: list[str]`
    :   End date of sale price, as GMT

    `default_attributes: list[list[typing.Any]]`
    :   Defaults variation attributes

    `description: list[str]`
    :   Product description

    `dimensions: list[dict[str, typing.Any]]`
    :   Product dimensions

    `download_expiry: list[int]`
    :   Number of days until access to downloadable files expires

    `download_limit: list[int]`
    :   Number of times downloadable files can be downloaded

    `downloadable: list[bool]`
    :   If the product is downloadable

    `downloads: list[list[typing.Any]]`
    :   List of downloadable files

    `external_url: list[str]`
    :   Product external URL

    `grouped_products: list[list[typing.Any]]`
    :   List of grouped products ID

    `id: list[int]`
    :   Unique identifier for the resource

    `images: list[list[typing.Any]]`
    :   List of images

    `manage_stock: list[bool]`
    :   Stock management at product level

    `menu_order: list[int]`
    :   Menu order

    `meta_data: list[list[typing.Any]]`
    :   Meta data

    `name: list[str]`
    :   Product name

    `on_sale: list[bool]`
    :   Shows if the product is on sale

    `parent_id: list[int]`
    :   Product parent ID

    `permalink: list[str]`
    :   Product URL

    `price: list[str]`
    :   Current product price

    `price_html: list[str]`
    :   Price formatted in HTML

    `purchasable: list[bool]`
    :   Shows if the product can be bought

    `purchase_note: list[str]`
    :   Note to send customer after purchase

    `rating_count: list[int]`
    :   Amount of reviews

    `regular_price: list[str]`
    :   Product regular price

    `related_ids: list[list[typing.Any]]`
    :   List of related products IDs

    `reviews_allowed: list[bool]`
    :   Allow reviews

    `sale_price: list[str]`
    :   Product sale price

    `shipping_class: list[str]`
    :   Shipping class slug

    `shipping_class_id: list[int]`
    :   Shipping class ID

    `shipping_required: list[bool]`
    :   Shows if the product needs to be shipped

    `shipping_taxable: list[bool]`
    :   Shows if product shipping is taxable

    `short_description: list[str]`
    :   Product short description

    `sku: list[str]`
    :   Unique identifier (SKU)

    `slug: list[str]`
    :   Product slug

    `sold_individually: list[bool]`
    :   Allow one item per order

    `status: list[str]`
    :   Product status

    `stock_quantity: list[int]`
    :   Stock quantity

    `stock_status: list[str]`
    :   Controls the stock status

    `tags: list[list[typing.Any]]`
    :   List of tags

    `tax_class: list[str]`
    :   Tax class

    `tax_status: list[str]`
    :   Tax status

    `total_sales: list[int]`
    :   Amount of sales

    `type_: list[str]`
    :   Product type

    `upsell_ids: list[list[typing.Any]]`
    :   List of up-sell products IDs

    `variations: list[list[typing.Any]]`
    :   List of variations IDs

    `virtual: list[bool]`
    :   If the product is virtual

    `weight: list[str]`
    :   Product weight

<a id="ProductsKeywordCondition"></a>

`ProductsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.ProductsStringFilter`
    :   The type of the None singleton.

<a id="ProductsLikeCondition"></a>

`ProductsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.ProductsStringFilter`
    :   The type of the None singleton.

<a id="ProductsListParams"></a>

`ProductsListParams(*args, **kwargs)`
:   Parameters for products.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `before: str`
    :   The type of the None singleton.

    `category: str`
    :   The type of the None singleton.

    `featured: bool`
    :   The type of the None singleton.

    `max_price: str`
    :   The type of the None singleton.

    `min_price: str`
    :   The type of the None singleton.

    `modified_after: str`
    :   The type of the None singleton.

    `modified_before: str`
    :   The type of the None singleton.

    `on_sale: bool`
    :   The type of the None singleton.

    `order: str`
    :   The type of the None singleton.

    `orderby: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

    `sku: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `stock_status: str`
    :   The type of the None singleton.

    `tag: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="ProductsLtCondition"></a>

`ProductsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.ProductsSearchFilter`
    :   The type of the None singleton.

<a id="ProductsLteCondition"></a>

`ProductsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.ProductsSearchFilter`
    :   The type of the None singleton.

<a id="ProductsNeqCondition"></a>

`ProductsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.ProductsSearchFilter`
    :   The type of the None singleton.

<a id="ProductsNotCondition"></a>

`ProductsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.ProductsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsAnyCondition`
    :   The type of the None singleton.

<a id="ProductsOrCondition"></a>

`ProductsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsAnyCondition]`
    :   The type of the None singleton.

<a id="ProductsSearchFilter"></a>

`ProductsSearchFilter(*args, **kwargs)`
:   Available fields for filtering products search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="ProductsSearchQuery"></a>

`ProductsSearchQuery(*args, **kwargs)`
:   Search query for products entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.ProductsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ProductsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.ProductsSortFilter]`
    :   The type of the None singleton.

<a id="ProductsSortFilter"></a>

`ProductsSortFilter(*args, **kwargs)`
:   Available fields for sorting products search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Literal['asc', 'desc']`
    :   List of attributes

    `average_rating: Literal['asc', 'desc']`
    :   Reviews average rating

    `backordered: Literal['asc', 'desc']`
    :   Shows if the product is on backordered

    `backorders: Literal['asc', 'desc']`
    :   If managing stock, this controls if backorders are allowed

    `backorders_allowed: Literal['asc', 'desc']`
    :   Shows if backorders are allowed

    `button_text: Literal['asc', 'desc']`
    :   Product external button text

    `catalog_visibility: Literal['asc', 'desc']`
    :   Catalog visibility

    `categories: Literal['asc', 'desc']`
    :   List of categories

    `cross_sell_ids: Literal['asc', 'desc']`
    :   List of cross-sell products IDs

    `date_created: Literal['asc', 'desc']`
    :   The date the product was created

    `date_created_gmt: Literal['asc', 'desc']`
    :   The date the product was created, as GMT

    `date_modified: Literal['asc', 'desc']`
    :   The date the product was last modified

    `date_modified_gmt: Literal['asc', 'desc']`
    :   The date the product was last modified, as GMT

    `date_on_sale_from: Literal['asc', 'desc']`
    :   Start date of sale price

    `date_on_sale_from_gmt: Literal['asc', 'desc']`
    :   Start date of sale price, as GMT

    `date_on_sale_to: Literal['asc', 'desc']`
    :   End date of sale price

    `date_on_sale_to_gmt: Literal['asc', 'desc']`
    :   End date of sale price, as GMT

    `default_attributes: Literal['asc', 'desc']`
    :   Defaults variation attributes

    `description: Literal['asc', 'desc']`
    :   Product description

    `dimensions: Literal['asc', 'desc']`
    :   Product dimensions

    `download_expiry: Literal['asc', 'desc']`
    :   Number of days until access to downloadable files expires

    `download_limit: Literal['asc', 'desc']`
    :   Number of times downloadable files can be downloaded

    `downloadable: Literal['asc', 'desc']`
    :   If the product is downloadable

    `downloads: Literal['asc', 'desc']`
    :   List of downloadable files

    `external_url: Literal['asc', 'desc']`
    :   Product external URL

    `grouped_products: Literal['asc', 'desc']`
    :   List of grouped products ID

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the resource

    `images: Literal['asc', 'desc']`
    :   List of images

    `manage_stock: Literal['asc', 'desc']`
    :   Stock management at product level

    `menu_order: Literal['asc', 'desc']`
    :   Menu order

    `meta_data: Literal['asc', 'desc']`
    :   Meta data

    `name: Literal['asc', 'desc']`
    :   Product name

    `on_sale: Literal['asc', 'desc']`
    :   Shows if the product is on sale

    `parent_id: Literal['asc', 'desc']`
    :   Product parent ID

    `permalink: Literal['asc', 'desc']`
    :   Product URL

    `price: Literal['asc', 'desc']`
    :   Current product price

    `price_html: Literal['asc', 'desc']`
    :   Price formatted in HTML

    `purchasable: Literal['asc', 'desc']`
    :   Shows if the product can be bought

    `purchase_note: Literal['asc', 'desc']`
    :   Note to send customer after purchase

    `rating_count: Literal['asc', 'desc']`
    :   Amount of reviews

    `regular_price: Literal['asc', 'desc']`
    :   Product regular price

    `related_ids: Literal['asc', 'desc']`
    :   List of related products IDs

    `reviews_allowed: Literal['asc', 'desc']`
    :   Allow reviews

    `sale_price: Literal['asc', 'desc']`
    :   Product sale price

    `shipping_class: Literal['asc', 'desc']`
    :   Shipping class slug

    `shipping_class_id: Literal['asc', 'desc']`
    :   Shipping class ID

    `shipping_required: Literal['asc', 'desc']`
    :   Shows if the product needs to be shipped

    `shipping_taxable: Literal['asc', 'desc']`
    :   Shows if product shipping is taxable

    `short_description: Literal['asc', 'desc']`
    :   Product short description

    `sku: Literal['asc', 'desc']`
    :   Unique identifier (SKU)

    `slug: Literal['asc', 'desc']`
    :   Product slug

    `sold_individually: Literal['asc', 'desc']`
    :   Allow one item per order

    `status: Literal['asc', 'desc']`
    :   Product status

    `stock_quantity: Literal['asc', 'desc']`
    :   Stock quantity

    `stock_status: Literal['asc', 'desc']`
    :   Controls the stock status

    `tags: Literal['asc', 'desc']`
    :   List of tags

    `tax_class: Literal['asc', 'desc']`
    :   Tax class

    `tax_status: Literal['asc', 'desc']`
    :   Tax status

    `total_sales: Literal['asc', 'desc']`
    :   Amount of sales

    `type_: Literal['asc', 'desc']`
    :   Product type

    `upsell_ids: Literal['asc', 'desc']`
    :   List of up-sell products IDs

    `variations: Literal['asc', 'desc']`
    :   List of variations IDs

    `virtual: Literal['asc', 'desc']`
    :   If the product is virtual

    `weight: Literal['asc', 'desc']`
    :   Product weight

<a id="ProductsStringFilter"></a>

`ProductsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: str`
    :   List of attributes

    `average_rating: str`
    :   Reviews average rating

    `backordered: str`
    :   Shows if the product is on backordered

    `backorders: str`
    :   If managing stock, this controls if backorders are allowed

    `backorders_allowed: str`
    :   Shows if backorders are allowed

    `button_text: str`
    :   Product external button text

    `catalog_visibility: str`
    :   Catalog visibility

    `categories: str`
    :   List of categories

    `cross_sell_ids: str`
    :   List of cross-sell products IDs

    `date_created: str`
    :   The date the product was created

    `date_created_gmt: str`
    :   The date the product was created, as GMT

    `date_modified: str`
    :   The date the product was last modified

    `date_modified_gmt: str`
    :   The date the product was last modified, as GMT

    `date_on_sale_from: str`
    :   Start date of sale price

    `date_on_sale_from_gmt: str`
    :   Start date of sale price, as GMT

    `date_on_sale_to: str`
    :   End date of sale price

    `date_on_sale_to_gmt: str`
    :   End date of sale price, as GMT

    `default_attributes: str`
    :   Defaults variation attributes

    `description: str`
    :   Product description

    `dimensions: str`
    :   Product dimensions

    `download_expiry: str`
    :   Number of days until access to downloadable files expires

    `download_limit: str`
    :   Number of times downloadable files can be downloaded

    `downloadable: str`
    :   If the product is downloadable

    `downloads: str`
    :   List of downloadable files

    `external_url: str`
    :   Product external URL

    `grouped_products: str`
    :   List of grouped products ID

    `id: str`
    :   Unique identifier for the resource

    `images: str`
    :   List of images

    `manage_stock: str`
    :   Stock management at product level

    `menu_order: str`
    :   Menu order

    `meta_data: str`
    :   Meta data

    `name: str`
    :   Product name

    `on_sale: str`
    :   Shows if the product is on sale

    `parent_id: str`
    :   Product parent ID

    `permalink: str`
    :   Product URL

    `price: str`
    :   Current product price

    `price_html: str`
    :   Price formatted in HTML

    `purchasable: str`
    :   Shows if the product can be bought

    `purchase_note: str`
    :   Note to send customer after purchase

    `rating_count: str`
    :   Amount of reviews

    `regular_price: str`
    :   Product regular price

    `related_ids: str`
    :   List of related products IDs

    `reviews_allowed: str`
    :   Allow reviews

    `sale_price: str`
    :   Product sale price

    `shipping_class: str`
    :   Shipping class slug

    `shipping_class_id: str`
    :   Shipping class ID

    `shipping_required: str`
    :   Shows if the product needs to be shipped

    `shipping_taxable: str`
    :   Shows if product shipping is taxable

    `short_description: str`
    :   Product short description

    `sku: str`
    :   Unique identifier (SKU)

    `slug: str`
    :   Product slug

    `sold_individually: str`
    :   Allow one item per order

    `status: str`
    :   Product status

    `stock_quantity: str`
    :   Stock quantity

    `stock_status: str`
    :   Controls the stock status

    `tags: str`
    :   List of tags

    `tax_class: str`
    :   Tax class

    `tax_status: str`
    :   Tax status

    `total_sales: str`
    :   Amount of sales

    `type_: str`
    :   Product type

    `upsell_ids: str`
    :   List of up-sell products IDs

    `variations: str`
    :   List of variations IDs

    `virtual: str`
    :   If the product is virtual

    `weight: str`
    :   Product weight

<a id="RefundsAndCondition"></a>

`RefundsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.RefundsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsAnyCondition]`
    :   The type of the None singleton.

<a id="RefundsAnyCondition"></a>

`RefundsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.RefundsAnyValueFilter`
    :   The type of the None singleton.

<a id="RefundsAnyValueFilter"></a>

`RefundsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Any`
    :   Refund amount

    `date_created: Any`
    :   The date the refund was created

    `date_created_gmt: Any`
    :   The date the refund was created, as GMT

    `id: Any`
    :   Unique identifier

    `line_items: Any`
    :   Line items data

    `meta_data: Any`
    :   Meta data

    `reason: Any`
    :   Reason for refund

    `refunded_by: Any`
    :   User ID of user who created the refund

    `refunded_payment: Any`
    :   If the payment was refunded via the API

<a id="RefundsContainsCondition"></a>

`RefundsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.RefundsAnyValueFilter`
    :   The type of the None singleton.

<a id="RefundsEqCondition"></a>

`RefundsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.RefundsSearchFilter`
    :   The type of the None singleton.

<a id="RefundsFuzzyCondition"></a>

`RefundsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.RefundsStringFilter`
    :   The type of the None singleton.

<a id="RefundsGetParams"></a>

`RefundsGetParams(*args, **kwargs)`
:   Parameters for refunds.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `order_id: str`
    :   The type of the None singleton.

<a id="RefundsGtCondition"></a>

`RefundsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.RefundsSearchFilter`
    :   The type of the None singleton.

<a id="RefundsGteCondition"></a>

`RefundsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.RefundsSearchFilter`
    :   The type of the None singleton.

<a id="RefundsInCondition"></a>

`RefundsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.RefundsInFilter`
    :   The type of the None singleton.

<a id="RefundsInFilter"></a>

`RefundsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: list[str]`
    :   Refund amount

    `date_created: list[str]`
    :   The date the refund was created

    `date_created_gmt: list[str]`
    :   The date the refund was created, as GMT

    `id: list[int]`
    :   Unique identifier

    `line_items: list[list[typing.Any]]`
    :   Line items data

    `meta_data: list[list[typing.Any]]`
    :   Meta data

    `reason: list[str]`
    :   Reason for refund

    `refunded_by: list[int]`
    :   User ID of user who created the refund

    `refunded_payment: list[bool]`
    :   If the payment was refunded via the API

<a id="RefundsKeywordCondition"></a>

`RefundsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.RefundsStringFilter`
    :   The type of the None singleton.

<a id="RefundsLikeCondition"></a>

`RefundsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.RefundsStringFilter`
    :   The type of the None singleton.

<a id="RefundsListParams"></a>

`RefundsListParams(*args, **kwargs)`
:   Parameters for refunds.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="RefundsLtCondition"></a>

`RefundsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.RefundsSearchFilter`
    :   The type of the None singleton.

<a id="RefundsLteCondition"></a>

`RefundsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.RefundsSearchFilter`
    :   The type of the None singleton.

<a id="RefundsNeqCondition"></a>

`RefundsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.RefundsSearchFilter`
    :   The type of the None singleton.

<a id="RefundsNotCondition"></a>

`RefundsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.RefundsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsAnyCondition`
    :   The type of the None singleton.

<a id="RefundsOrCondition"></a>

`RefundsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.RefundsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsAnyCondition]`
    :   The type of the None singleton.

<a id="RefundsSearchFilter"></a>

`RefundsSearchFilter(*args, **kwargs)`
:   Available fields for filtering refunds search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

    `reason: str | None`
    :   Reason for refund

    `refunded_by: int | None`
    :   User ID of user who created the refund

    `refunded_payment: bool | None`
    :   If the payment was refunded via the API

<a id="RefundsSearchQuery"></a>

`RefundsSearchQuery(*args, **kwargs)`
:   Search query for refunds entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.RefundsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.RefundsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.RefundsSortFilter]`
    :   The type of the None singleton.

<a id="RefundsSortFilter"></a>

`RefundsSortFilter(*args, **kwargs)`
:   Available fields for sorting refunds search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Literal['asc', 'desc']`
    :   Refund amount

    `date_created: Literal['asc', 'desc']`
    :   The date the refund was created

    `date_created_gmt: Literal['asc', 'desc']`
    :   The date the refund was created, as GMT

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `line_items: Literal['asc', 'desc']`
    :   Line items data

    `meta_data: Literal['asc', 'desc']`
    :   Meta data

    `reason: Literal['asc', 'desc']`
    :   Reason for refund

    `refunded_by: Literal['asc', 'desc']`
    :   User ID of user who created the refund

    `refunded_payment: Literal['asc', 'desc']`
    :   If the payment was refunded via the API

<a id="RefundsStringFilter"></a>

`RefundsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   Refund amount

    `date_created: str`
    :   The date the refund was created

    `date_created_gmt: str`
    :   The date the refund was created, as GMT

    `id: str`
    :   Unique identifier

    `line_items: str`
    :   Line items data

    `meta_data: str`
    :   Meta data

    `reason: str`
    :   Reason for refund

    `refunded_by: str`
    :   User ID of user who created the refund

    `refunded_payment: str`
    :   If the payment was refunded via the API

<a id="ShippingMethodsAndCondition"></a>

`ShippingMethodsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsAnyCondition]`
    :   The type of the None singleton.

<a id="ShippingMethodsAnyCondition"></a>

`ShippingMethodsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsAnyValueFilter`
    :   The type of the None singleton.

<a id="ShippingMethodsAnyValueFilter"></a>

`ShippingMethodsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: Any`
    :   Shipping method description

    `id: Any`
    :   Method ID

    `title: Any`
    :   Shipping method title

<a id="ShippingMethodsContainsCondition"></a>

`ShippingMethodsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsAnyValueFilter`
    :   The type of the None singleton.

<a id="ShippingMethodsEqCondition"></a>

`ShippingMethodsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsSearchFilter`
    :   The type of the None singleton.

<a id="ShippingMethodsFuzzyCondition"></a>

`ShippingMethodsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsStringFilter`
    :   The type of the None singleton.

<a id="ShippingMethodsGetParams"></a>

`ShippingMethodsGetParams(*args, **kwargs)`
:   Parameters for shipping_methods.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ShippingMethodsGtCondition"></a>

`ShippingMethodsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsSearchFilter`
    :   The type of the None singleton.

<a id="ShippingMethodsGteCondition"></a>

`ShippingMethodsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsSearchFilter`
    :   The type of the None singleton.

<a id="ShippingMethodsInCondition"></a>

`ShippingMethodsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsInFilter`
    :   The type of the None singleton.

<a id="ShippingMethodsInFilter"></a>

`ShippingMethodsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: list[str]`
    :   Shipping method description

    `id: list[str]`
    :   Method ID

    `title: list[str]`
    :   Shipping method title

<a id="ShippingMethodsKeywordCondition"></a>

`ShippingMethodsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsStringFilter`
    :   The type of the None singleton.

<a id="ShippingMethodsLikeCondition"></a>

`ShippingMethodsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsStringFilter`
    :   The type of the None singleton.

<a id="ShippingMethodsListParams"></a>

`ShippingMethodsListParams(*args, **kwargs)`
:   Parameters for shipping_methods.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ShippingMethodsLtCondition"></a>

`ShippingMethodsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsSearchFilter`
    :   The type of the None singleton.

<a id="ShippingMethodsLteCondition"></a>

`ShippingMethodsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsSearchFilter`
    :   The type of the None singleton.

<a id="ShippingMethodsNeqCondition"></a>

`ShippingMethodsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsSearchFilter`
    :   The type of the None singleton.

<a id="ShippingMethodsNotCondition"></a>

`ShippingMethodsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsAnyCondition`
    :   The type of the None singleton.

<a id="ShippingMethodsOrCondition"></a>

`ShippingMethodsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsAnyCondition]`
    :   The type of the None singleton.

<a id="ShippingMethodsSearchFilter"></a>

`ShippingMethodsSearchFilter(*args, **kwargs)`
:   Available fields for filtering shipping_methods search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str | None`
    :   Shipping method description

    `id: str | None`
    :   Method ID

    `title: str | None`
    :   Shipping method title

<a id="ShippingMethodsSearchQuery"></a>

`ShippingMethodsSearchQuery(*args, **kwargs)`
:   Search query for shipping_methods entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.ShippingMethodsSortFilter]`
    :   The type of the None singleton.

<a id="ShippingMethodsSortFilter"></a>

`ShippingMethodsSortFilter(*args, **kwargs)`
:   Available fields for sorting shipping_methods search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: Literal['asc', 'desc']`
    :   Shipping method description

    `id: Literal['asc', 'desc']`
    :   Method ID

    `title: Literal['asc', 'desc']`
    :   Shipping method title

<a id="ShippingMethodsStringFilter"></a>

`ShippingMethodsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str`
    :   Shipping method description

    `id: str`
    :   Method ID

    `title: str`
    :   Shipping method title

<a id="ShippingZonesAndCondition"></a>

`ShippingZonesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesAnyCondition]`
    :   The type of the None singleton.

<a id="ShippingZonesAnyCondition"></a>

`ShippingZonesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesAnyValueFilter`
    :   The type of the None singleton.

<a id="ShippingZonesAnyValueFilter"></a>

`ShippingZonesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier

    `name: Any`
    :   Shipping zone name

    `order: Any`
    :   Shipping zone order

<a id="ShippingZonesContainsCondition"></a>

`ShippingZonesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesAnyValueFilter`
    :   The type of the None singleton.

<a id="ShippingZonesEqCondition"></a>

`ShippingZonesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesSearchFilter`
    :   The type of the None singleton.

<a id="ShippingZonesFuzzyCondition"></a>

`ShippingZonesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesStringFilter`
    :   The type of the None singleton.

<a id="ShippingZonesGetParams"></a>

`ShippingZonesGetParams(*args, **kwargs)`
:   Parameters for shipping_zones.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ShippingZonesGtCondition"></a>

`ShippingZonesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesSearchFilter`
    :   The type of the None singleton.

<a id="ShippingZonesGteCondition"></a>

`ShippingZonesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesSearchFilter`
    :   The type of the None singleton.

<a id="ShippingZonesInCondition"></a>

`ShippingZonesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesInFilter`
    :   The type of the None singleton.

<a id="ShippingZonesInFilter"></a>

`ShippingZonesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[int]`
    :   Unique identifier

    `name: list[str]`
    :   Shipping zone name

    `order: list[int]`
    :   Shipping zone order

<a id="ShippingZonesKeywordCondition"></a>

`ShippingZonesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesStringFilter`
    :   The type of the None singleton.

<a id="ShippingZonesLikeCondition"></a>

`ShippingZonesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesStringFilter`
    :   The type of the None singleton.

<a id="ShippingZonesListParams"></a>

`ShippingZonesListParams(*args, **kwargs)`
:   Parameters for shipping_zones.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ShippingZonesLtCondition"></a>

`ShippingZonesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesSearchFilter`
    :   The type of the None singleton.

<a id="ShippingZonesLteCondition"></a>

`ShippingZonesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesSearchFilter`
    :   The type of the None singleton.

<a id="ShippingZonesNeqCondition"></a>

`ShippingZonesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesSearchFilter`
    :   The type of the None singleton.

<a id="ShippingZonesNotCondition"></a>

`ShippingZonesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesAnyCondition`
    :   The type of the None singleton.

<a id="ShippingZonesOrCondition"></a>

`ShippingZonesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesAnyCondition]`
    :   The type of the None singleton.

<a id="ShippingZonesSearchFilter"></a>

`ShippingZonesSearchFilter(*args, **kwargs)`
:   Available fields for filtering shipping_zones search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: int | None`
    :   Unique identifier

    `name: str | None`
    :   Shipping zone name

    `order: int | None`
    :   Shipping zone order

<a id="ShippingZonesSearchQuery"></a>

`ShippingZonesSearchQuery(*args, **kwargs)`
:   Search query for shipping_zones entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.ShippingZonesSortFilter]`
    :   The type of the None singleton.

<a id="ShippingZonesSortFilter"></a>

`ShippingZonesSortFilter(*args, **kwargs)`
:   Available fields for sorting shipping_zones search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `name: Literal['asc', 'desc']`
    :   Shipping zone name

    `order: Literal['asc', 'desc']`
    :   Shipping zone order

<a id="ShippingZonesStringFilter"></a>

`ShippingZonesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier

    `name: str`
    :   Shipping zone name

    `order: str`
    :   Shipping zone order

<a id="TaxClassesAndCondition"></a>

`TaxClassesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesAnyCondition]`
    :   The type of the None singleton.

<a id="TaxClassesAnyCondition"></a>

`TaxClassesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesAnyValueFilter`
    :   The type of the None singleton.

<a id="TaxClassesAnyValueFilter"></a>

`TaxClassesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: Any`
    :   Tax class name

    `slug: Any`
    :   Unique identifier

<a id="TaxClassesContainsCondition"></a>

`TaxClassesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesAnyValueFilter`
    :   The type of the None singleton.

<a id="TaxClassesEqCondition"></a>

`TaxClassesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesSearchFilter`
    :   The type of the None singleton.

<a id="TaxClassesFuzzyCondition"></a>

`TaxClassesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesStringFilter`
    :   The type of the None singleton.

<a id="TaxClassesGtCondition"></a>

`TaxClassesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesSearchFilter`
    :   The type of the None singleton.

<a id="TaxClassesGteCondition"></a>

`TaxClassesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesSearchFilter`
    :   The type of the None singleton.

<a id="TaxClassesInCondition"></a>

`TaxClassesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesInFilter`
    :   The type of the None singleton.

<a id="TaxClassesInFilter"></a>

`TaxClassesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: list[str]`
    :   Tax class name

    `slug: list[str]`
    :   Unique identifier

<a id="TaxClassesKeywordCondition"></a>

`TaxClassesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesStringFilter`
    :   The type of the None singleton.

<a id="TaxClassesLikeCondition"></a>

`TaxClassesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesStringFilter`
    :   The type of the None singleton.

<a id="TaxClassesListParams"></a>

`TaxClassesListParams(*args, **kwargs)`
:   Parameters for tax_classes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="TaxClassesLtCondition"></a>

`TaxClassesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesSearchFilter`
    :   The type of the None singleton.

<a id="TaxClassesLteCondition"></a>

`TaxClassesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesSearchFilter`
    :   The type of the None singleton.

<a id="TaxClassesNeqCondition"></a>

`TaxClassesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesSearchFilter`
    :   The type of the None singleton.

<a id="TaxClassesNotCondition"></a>

`TaxClassesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesAnyCondition`
    :   The type of the None singleton.

<a id="TaxClassesOrCondition"></a>

`TaxClassesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesAnyCondition]`
    :   The type of the None singleton.

<a id="TaxClassesSearchFilter"></a>

`TaxClassesSearchFilter(*args, **kwargs)`
:   Available fields for filtering tax_classes search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str | None`
    :   Tax class name

    `slug: str | None`
    :   Unique identifier

<a id="TaxClassesSearchQuery"></a>

`TaxClassesSearchQuery(*args, **kwargs)`
:   Search query for tax_classes entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.TaxClassesSortFilter]`
    :   The type of the None singleton.

<a id="TaxClassesSortFilter"></a>

`TaxClassesSortFilter(*args, **kwargs)`
:   Available fields for sorting tax_classes search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: Literal['asc', 'desc']`
    :   Tax class name

    `slug: Literal['asc', 'desc']`
    :   Unique identifier

<a id="TaxClassesStringFilter"></a>

`TaxClassesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   Tax class name

    `slug: str`
    :   Unique identifier

<a id="TaxRatesAndCondition"></a>

`TaxRatesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesAnyCondition]`
    :   The type of the None singleton.

<a id="TaxRatesAnyCondition"></a>

`TaxRatesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesAnyValueFilter`
    :   The type of the None singleton.

<a id="TaxRatesAnyValueFilter"></a>

`TaxRatesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cities: Any`
    :   City names

    `city: Any`
    :   City name

    `class_: Any`
    :   Tax class

    `compound: Any`
    :   Whether this is a compound rate

    `country: Any`
    :   Country ISO 3166 code

    `id: Any`
    :   Unique identifier

    `name: Any`
    :   Tax rate name

    `order: Any`
    :   Order in queries

    `postcode: Any`
    :   Postcode/ZIP

    `postcodes: Any`
    :   Postcodes/ZIPs

    `priority: Any`
    :   Tax priority

    `rate: Any`
    :   Tax rate

    `shipping: Any`
    :   Applied to shipping

    `state: Any`
    :   State code

<a id="TaxRatesContainsCondition"></a>

`TaxRatesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesAnyValueFilter`
    :   The type of the None singleton.

<a id="TaxRatesEqCondition"></a>

`TaxRatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesSearchFilter`
    :   The type of the None singleton.

<a id="TaxRatesFuzzyCondition"></a>

`TaxRatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesStringFilter`
    :   The type of the None singleton.

<a id="TaxRatesGetParams"></a>

`TaxRatesGetParams(*args, **kwargs)`
:   Parameters for tax_rates.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="TaxRatesGtCondition"></a>

`TaxRatesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesSearchFilter`
    :   The type of the None singleton.

<a id="TaxRatesGteCondition"></a>

`TaxRatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesSearchFilter`
    :   The type of the None singleton.

<a id="TaxRatesInCondition"></a>

`TaxRatesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesInFilter`
    :   The type of the None singleton.

<a id="TaxRatesInFilter"></a>

`TaxRatesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cities: list[list[typing.Any]]`
    :   City names

    `city: list[str]`
    :   City name

    `class_: list[str]`
    :   Tax class

    `compound: list[bool]`
    :   Whether this is a compound rate

    `country: list[str]`
    :   Country ISO 3166 code

    `id: list[int]`
    :   Unique identifier

    `name: list[str]`
    :   Tax rate name

    `order: list[int]`
    :   Order in queries

    `postcode: list[str]`
    :   Postcode/ZIP

    `postcodes: list[list[typing.Any]]`
    :   Postcodes/ZIPs

    `priority: list[int]`
    :   Tax priority

    `rate: list[str]`
    :   Tax rate

    `shipping: list[bool]`
    :   Applied to shipping

    `state: list[str]`
    :   State code

<a id="TaxRatesKeywordCondition"></a>

`TaxRatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesStringFilter`
    :   The type of the None singleton.

<a id="TaxRatesLikeCondition"></a>

`TaxRatesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesStringFilter`
    :   The type of the None singleton.

<a id="TaxRatesListParams"></a>

`TaxRatesListParams(*args, **kwargs)`
:   Parameters for tax_rates.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `class_: str`
    :   The type of the None singleton.

    `order: str`
    :   The type of the None singleton.

    `orderby: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="TaxRatesLtCondition"></a>

`TaxRatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesSearchFilter`
    :   The type of the None singleton.

<a id="TaxRatesLteCondition"></a>

`TaxRatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesSearchFilter`
    :   The type of the None singleton.

<a id="TaxRatesNeqCondition"></a>

`TaxRatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesSearchFilter`
    :   The type of the None singleton.

<a id="TaxRatesNotCondition"></a>

`TaxRatesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesAnyCondition`
    :   The type of the None singleton.

<a id="TaxRatesOrCondition"></a>

`TaxRatesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesAnyCondition]`
    :   The type of the None singleton.

<a id="TaxRatesSearchFilter"></a>

`TaxRatesSearchFilter(*args, **kwargs)`
:   Available fields for filtering tax_rates search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="TaxRatesSearchQuery"></a>

`TaxRatesSearchQuery(*args, **kwargs)`
:   Search query for tax_rates entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesEqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesNeqCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesGtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesGteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesLtCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesLteCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesInCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesLikeCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesFuzzyCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesKeywordCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesContainsCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesNotCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesAndCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesOrCondition | airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.woocommerce.types.TaxRatesSortFilter]`
    :   The type of the None singleton.

<a id="TaxRatesSortFilter"></a>

`TaxRatesSortFilter(*args, **kwargs)`
:   Available fields for sorting tax_rates search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cities: Literal['asc', 'desc']`
    :   City names

    `city: Literal['asc', 'desc']`
    :   City name

    `class_: Literal['asc', 'desc']`
    :   Tax class

    `compound: Literal['asc', 'desc']`
    :   Whether this is a compound rate

    `country: Literal['asc', 'desc']`
    :   Country ISO 3166 code

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `name: Literal['asc', 'desc']`
    :   Tax rate name

    `order: Literal['asc', 'desc']`
    :   Order in queries

    `postcode: Literal['asc', 'desc']`
    :   Postcode/ZIP

    `postcodes: Literal['asc', 'desc']`
    :   Postcodes/ZIPs

    `priority: Literal['asc', 'desc']`
    :   Tax priority

    `rate: Literal['asc', 'desc']`
    :   Tax rate

    `shipping: Literal['asc', 'desc']`
    :   Applied to shipping

    `state: Literal['asc', 'desc']`
    :   State code

<a id="TaxRatesStringFilter"></a>

`TaxRatesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cities: str`
    :   City names

    `city: str`
    :   City name

    `class_: str`
    :   Tax class

    `compound: str`
    :   Whether this is a compound rate

    `country: str`
    :   Country ISO 3166 code

    `id: str`
    :   Unique identifier

    `name: str`
    :   Tax rate name

    `order: str`
    :   Order in queries

    `postcode: str`
    :   Postcode/ZIP

    `postcodes: str`
    :   Postcodes/ZIPs

    `priority: str`
    :   Tax priority

    `rate: str`
    :   Tax rate

    `shipping: str`
    :   Applied to shipping

    `state: str`
    :   State code