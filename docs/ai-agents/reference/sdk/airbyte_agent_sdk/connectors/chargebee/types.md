---
id: airbyte_agent_sdk-connectors-chargebee-types
title: airbyte_agent_sdk.connectors.chargebee.types
---

Module airbyte_agent_sdk.connectors.chargebee.types
===================================================
Type definitions for chargebee connector.

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

<a id="CouponAndCondition"></a>

`CouponAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.chargebee.types.CouponEqCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponGtCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponGteCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponLtCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponLteCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponInCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponNotCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponAndCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponOrCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponAnyCondition]`
    :   The type of the None singleton.

<a id="CouponAnyCondition"></a>

`CouponAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.chargebee.types.CouponAnyValueFilter`
    :   The type of the None singleton.

<a id="CouponAnyValueFilter"></a>

`CouponAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `apply_discount_on: Any`
    :   Determines where the discount is applied on (e.g. subtotal, total).

    `apply_on: Any`
    :   Specify on what type of items the coupon applies (e.g. subscription, addon).

    `archived_at: Any`
    :   Timestamp when the coupon was archived.

    `coupon_constraints: Any`
    :   Represents the constraints associated with the coupon

    `created_at: Any`
    :   Timestamp of the coupon creation.

    `currency_code: Any`
    :   The currency code for the coupon (e.g. USD, EUR).

    `custom_fields: Any`
    :   The type of the None singleton.

    `discount_amount: Any`
    :   The fixed discount amount applied by the coupon.

    `discount_percentage: Any`
    :   Percentage discount applied by the coupon.

    `discount_quantity: Any`
    :   Specifies the number of free units provided for the item price, without affecting the total quantity sold. This parameter is applicable only when the discount_type is set to offer_quantity.

    `discount_type: Any`
    :   Type of discount (e.g. fixed, percentage).

    `duration_month: Any`
    :   Duration of the coupon in months.

    `duration_type: Any`
    :   Type of duration (e.g. forever, one-time).

    `id: Any`
    :   Unique identifier for the coupon.

    `invoice_name: Any`
    :   Name displayed on invoices when the coupon is used.

    `invoice_notes: Any`
    :   Additional notes displayed on invoices when the coupon is used.

    `item_constraint_criteria: Any`
    :   Criteria for item constraints

    `item_constraints: Any`
    :   Constraints related to the items

    `max_redemptions: Any`
    :   Maximum number of times the coupon can be redeemed.

    `name: Any`
    :   Name of the coupon.

    `object_: Any`
    :   Type of object (usually 'coupon').

    `period: Any`
    :   Duration or frequency for which the coupon is valid.

    `period_unit: Any`
    :   Unit of the period (e.g. days, weeks).

    `redemptions: Any`
    :   Number of times the coupon has been redeemed.

    `resource_version: Any`
    :   Version of the resource.

    `status: Any`
    :   Current status of the coupon (e.g. active, inactive).

    `updated_at: Any`
    :   Timestamp when the coupon was last updated.

    `valid_till: Any`
    :   Date until which the coupon is valid for use.

<a id="CouponContainsCondition"></a>

`CouponContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.chargebee.types.CouponAnyValueFilter`
    :   The type of the None singleton.

<a id="CouponEqCondition"></a>

`CouponEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.chargebee.types.CouponSearchFilter`
    :   The type of the None singleton.

<a id="CouponFuzzyCondition"></a>

`CouponFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.chargebee.types.CouponStringFilter`
    :   The type of the None singleton.

<a id="CouponGetParams"></a>

`CouponGetParams(*args, **kwargs)`
:   Parameters for coupon.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CouponGtCondition"></a>

`CouponGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.chargebee.types.CouponSearchFilter`
    :   The type of the None singleton.

<a id="CouponGteCondition"></a>

`CouponGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.chargebee.types.CouponSearchFilter`
    :   The type of the None singleton.

<a id="CouponInCondition"></a>

`CouponInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.chargebee.types.CouponInFilter`
    :   The type of the None singleton.

<a id="CouponInFilter"></a>

`CouponInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `apply_discount_on: list[str]`
    :   Determines where the discount is applied on (e.g. subtotal, total).

    `apply_on: list[str]`
    :   Specify on what type of items the coupon applies (e.g. subscription, addon).

    `archived_at: list[int]`
    :   Timestamp when the coupon was archived.

    `coupon_constraints: list[list[typing.Any]]`
    :   Represents the constraints associated with the coupon

    `created_at: list[int]`
    :   Timestamp of the coupon creation.

    `currency_code: list[str]`
    :   The currency code for the coupon (e.g. USD, EUR).

    `custom_fields: list[list[typing.Any]]`
    :   The type of the None singleton.

    `discount_amount: list[int]`
    :   The fixed discount amount applied by the coupon.

    `discount_percentage: list[float]`
    :   Percentage discount applied by the coupon.

    `discount_quantity: list[int]`
    :   Specifies the number of free units provided for the item price, without affecting the total quantity sold. This parameter is applicable only when the discount_type is set to offer_quantity.

    `discount_type: list[str]`
    :   Type of discount (e.g. fixed, percentage).

    `duration_month: list[int]`
    :   Duration of the coupon in months.

    `duration_type: list[str]`
    :   Type of duration (e.g. forever, one-time).

    `id: list[str]`
    :   Unique identifier for the coupon.

    `invoice_name: list[str]`
    :   Name displayed on invoices when the coupon is used.

    `invoice_notes: list[str]`
    :   Additional notes displayed on invoices when the coupon is used.

    `item_constraint_criteria: list[list[typing.Any]]`
    :   Criteria for item constraints

    `item_constraints: list[list[typing.Any]]`
    :   Constraints related to the items

    `max_redemptions: list[int]`
    :   Maximum number of times the coupon can be redeemed.

    `name: list[str]`
    :   Name of the coupon.

    `object_: list[str]`
    :   Type of object (usually 'coupon').

    `period: list[int]`
    :   Duration or frequency for which the coupon is valid.

    `period_unit: list[str]`
    :   Unit of the period (e.g. days, weeks).

    `redemptions: list[int]`
    :   Number of times the coupon has been redeemed.

    `resource_version: list[int]`
    :   Version of the resource.

    `status: list[str]`
    :   Current status of the coupon (e.g. active, inactive).

    `updated_at: list[int]`
    :   Timestamp when the coupon was last updated.

    `valid_till: list[int]`
    :   Date until which the coupon is valid for use.

<a id="CouponKeywordCondition"></a>

`CouponKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.chargebee.types.CouponStringFilter`
    :   The type of the None singleton.

<a id="CouponLikeCondition"></a>

`CouponLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.chargebee.types.CouponStringFilter`
    :   The type of the None singleton.

<a id="CouponListParams"></a>

`CouponListParams(*args, **kwargs)`
:   Parameters for coupon.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

<a id="CouponLtCondition"></a>

`CouponLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.chargebee.types.CouponSearchFilter`
    :   The type of the None singleton.

<a id="CouponLteCondition"></a>

`CouponLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.chargebee.types.CouponSearchFilter`
    :   The type of the None singleton.

<a id="CouponNeqCondition"></a>

`CouponNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.chargebee.types.CouponSearchFilter`
    :   The type of the None singleton.

<a id="CouponNotCondition"></a>

`CouponNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.chargebee.types.CouponEqCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponGtCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponGteCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponLtCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponLteCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponInCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponNotCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponAndCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponOrCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponAnyCondition`
    :   The type of the None singleton.

<a id="CouponOrCondition"></a>

`CouponOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.chargebee.types.CouponEqCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponGtCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponGteCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponLtCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponLteCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponInCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponNotCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponAndCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponOrCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponAnyCondition]`
    :   The type of the None singleton.

<a id="CouponSearchFilter"></a>

`CouponSearchFilter(*args, **kwargs)`
:   Available fields for filtering coupon search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CouponSearchQuery"></a>

`CouponSearchQuery(*args, **kwargs)`
:   Search query for coupon entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.chargebee.types.CouponEqCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponGtCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponGteCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponLtCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponLteCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponInCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponNotCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponAndCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponOrCondition | airbyte_agent_sdk.connectors.chargebee.types.CouponAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.chargebee.types.CouponSortFilter]`
    :   The type of the None singleton.

<a id="CouponSortFilter"></a>

`CouponSortFilter(*args, **kwargs)`
:   Available fields for sorting coupon search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `apply_discount_on: Literal['asc', 'desc']`
    :   Determines where the discount is applied on (e.g. subtotal, total).

    `apply_on: Literal['asc', 'desc']`
    :   Specify on what type of items the coupon applies (e.g. subscription, addon).

    `archived_at: Literal['asc', 'desc']`
    :   Timestamp when the coupon was archived.

    `coupon_constraints: Literal['asc', 'desc']`
    :   Represents the constraints associated with the coupon

    `created_at: Literal['asc', 'desc']`
    :   Timestamp of the coupon creation.

    `currency_code: Literal['asc', 'desc']`
    :   The currency code for the coupon (e.g. USD, EUR).

    `custom_fields: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `discount_amount: Literal['asc', 'desc']`
    :   The fixed discount amount applied by the coupon.

    `discount_percentage: Literal['asc', 'desc']`
    :   Percentage discount applied by the coupon.

    `discount_quantity: Literal['asc', 'desc']`
    :   Specifies the number of free units provided for the item price, without affecting the total quantity sold. This parameter is applicable only when the discount_type is set to offer_quantity.

    `discount_type: Literal['asc', 'desc']`
    :   Type of discount (e.g. fixed, percentage).

    `duration_month: Literal['asc', 'desc']`
    :   Duration of the coupon in months.

    `duration_type: Literal['asc', 'desc']`
    :   Type of duration (e.g. forever, one-time).

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the coupon.

    `invoice_name: Literal['asc', 'desc']`
    :   Name displayed on invoices when the coupon is used.

    `invoice_notes: Literal['asc', 'desc']`
    :   Additional notes displayed on invoices when the coupon is used.

    `item_constraint_criteria: Literal['asc', 'desc']`
    :   Criteria for item constraints

    `item_constraints: Literal['asc', 'desc']`
    :   Constraints related to the items

    `max_redemptions: Literal['asc', 'desc']`
    :   Maximum number of times the coupon can be redeemed.

    `name: Literal['asc', 'desc']`
    :   Name of the coupon.

    `object_: Literal['asc', 'desc']`
    :   Type of object (usually 'coupon').

    `period: Literal['asc', 'desc']`
    :   Duration or frequency for which the coupon is valid.

    `period_unit: Literal['asc', 'desc']`
    :   Unit of the period (e.g. days, weeks).

    `redemptions: Literal['asc', 'desc']`
    :   Number of times the coupon has been redeemed.

    `resource_version: Literal['asc', 'desc']`
    :   Version of the resource.

    `status: Literal['asc', 'desc']`
    :   Current status of the coupon (e.g. active, inactive).

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the coupon was last updated.

    `valid_till: Literal['asc', 'desc']`
    :   Date until which the coupon is valid for use.

<a id="CouponStringFilter"></a>

`CouponStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `apply_discount_on: str`
    :   Determines where the discount is applied on (e.g. subtotal, total).

    `apply_on: str`
    :   Specify on what type of items the coupon applies (e.g. subscription, addon).

    `archived_at: str`
    :   Timestamp when the coupon was archived.

    `coupon_constraints: str`
    :   Represents the constraints associated with the coupon

    `created_at: str`
    :   Timestamp of the coupon creation.

    `currency_code: str`
    :   The currency code for the coupon (e.g. USD, EUR).

    `custom_fields: str`
    :   The type of the None singleton.

    `discount_amount: str`
    :   The fixed discount amount applied by the coupon.

    `discount_percentage: str`
    :   Percentage discount applied by the coupon.

    `discount_quantity: str`
    :   Specifies the number of free units provided for the item price, without affecting the total quantity sold. This parameter is applicable only when the discount_type is set to offer_quantity.

    `discount_type: str`
    :   Type of discount (e.g. fixed, percentage).

    `duration_month: str`
    :   Duration of the coupon in months.

    `duration_type: str`
    :   Type of duration (e.g. forever, one-time).

    `id: str`
    :   Unique identifier for the coupon.

    `invoice_name: str`
    :   Name displayed on invoices when the coupon is used.

    `invoice_notes: str`
    :   Additional notes displayed on invoices when the coupon is used.

    `item_constraint_criteria: str`
    :   Criteria for item constraints

    `item_constraints: str`
    :   Constraints related to the items

    `max_redemptions: str`
    :   Maximum number of times the coupon can be redeemed.

    `name: str`
    :   Name of the coupon.

    `object_: str`
    :   Type of object (usually 'coupon').

    `period: str`
    :   Duration or frequency for which the coupon is valid.

    `period_unit: str`
    :   Unit of the period (e.g. days, weeks).

    `redemptions: str`
    :   Number of times the coupon has been redeemed.

    `resource_version: str`
    :   Version of the resource.

    `status: str`
    :   Current status of the coupon (e.g. active, inactive).

    `updated_at: str`
    :   Timestamp when the coupon was last updated.

    `valid_till: str`
    :   Date until which the coupon is valid for use.

<a id="CreditNoteAndCondition"></a>

`CreditNoteAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.chargebee.types.CreditNoteEqCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteGtCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteGteCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteLtCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteLteCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteInCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteNotCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteAndCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteOrCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteAnyCondition]`
    :   The type of the None singleton.

<a id="CreditNoteAnyCondition"></a>

`CreditNoteAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.chargebee.types.CreditNoteAnyValueFilter`
    :   The type of the None singleton.

<a id="CreditNoteAnyValueFilter"></a>

`CreditNoteAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allocations: Any`
    :   Details of allocations associated with the credit note

    `amount_allocated: Any`
    :   The amount of credits allocated.

    `amount_available: Any`
    :   The amount of credits available.

    `amount_refunded: Any`
    :   The amount of credits refunded.

    `base_currency_code: Any`
    :   The base currency code for the credit note.

    `billing_address: Any`
    :   Details of the billing address associated with the credit note

    `business_entity_id: Any`
    :   The ID of the business entity associated with the credit note.

    `channel: Any`
    :   The channel through which the credit note was created.

    `create_reason_code: Any`
    :   The reason code for creating the credit note.

    `currency_code: Any`
    :   The currency code for the credit note.

    `custom_fields: Any`
    :   The type of the None singleton.

    `customer_id: Any`
    :   The ID of the customer associated with the credit note.

    `customer_notes: Any`
    :   Notes provided by the customer for the credit note.

    `date: Any`
    :   The date when the credit note was created.

    `deleted: Any`
    :   Indicates if the credit note has been deleted.

    `discounts: Any`
    :   Details of discounts applied to the credit note

    `exchange_rate: Any`
    :   The exchange rate used for currency conversion.

    `fractional_correction: Any`
    :   Fractional correction for rounding off decimals.

    `generated_at: Any`
    :   The date when the credit note was generated.

    `id: Any`
    :   The unique identifier for the credit note.

    `is_digital: Any`
    :   Indicates if the credit note is in digital format.

    `is_vat_moss_registered: Any`
    :   Indicates if VAT MOSS registration applies.

    `line_item_discounts: Any`
    :   Details of discounts applied at the line item level in the credit note

    `line_item_taxes: Any`
    :   Details of taxes applied at the line item level in the credit note

    `line_item_tiers: Any`
    :   Details of tiers applied to line items in the credit note

    `line_items: Any`
    :   Details of line items in the credit note

    `linked_refunds: Any`
    :   Details of linked refunds to the credit note

    `linked_tax_withheld_refunds: Any`
    :   Details of linked tax withheld refunds to the credit note

    `local_currency_code: Any`
    :   The local currency code for the credit note.

    `object_: Any`
    :   The object type of the credit note.

    `price_type: Any`
    :   The type of pricing used for the credit note.

    `reason_code: Any`
    :   The reason code for creating the credit note.

    `reference_invoice_id: Any`
    :   The ID of the invoice this credit note references.

    `refunded_at: Any`
    :   The date when the credit note was refunded.

    `resource_version: Any`
    :   The version of the credit note resource.

    `round_off_amount: Any`
    :   Amount rounded off for currency conversions.

    `shipping_address: Any`
    :   Details of the shipping address associated with the credit note

    `status: Any`
    :   The status of the credit note.

    `sub_total: Any`
    :   The subtotal amount of the credit note.

    `sub_total_in_local_currency: Any`
    :   The subtotal amount in local currency.

    `subscription_id: Any`
    :   The ID of the subscription associated with the credit note.

    `taxes: Any`
    :   List of taxes applied to the credit note

    `total: Any`
    :   The total amount of the credit note.

    `total_in_local_currency: Any`
    :   The total amount in local currency.

    `type_: Any`
    :   The type of credit note.

    `updated_at: Any`
    :   The date when the credit note was last updated.

    `vat_number: Any`
    :   VAT number associated with the credit note.

    `vat_number_prefix: Any`
    :   Prefix for the VAT number.

    `voided_at: Any`
    :   The date when the credit note was voided.

<a id="CreditNoteContainsCondition"></a>

`CreditNoteContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.chargebee.types.CreditNoteAnyValueFilter`
    :   The type of the None singleton.

<a id="CreditNoteEqCondition"></a>

`CreditNoteEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.chargebee.types.CreditNoteSearchFilter`
    :   The type of the None singleton.

<a id="CreditNoteFuzzyCondition"></a>

`CreditNoteFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.chargebee.types.CreditNoteStringFilter`
    :   The type of the None singleton.

<a id="CreditNoteGetParams"></a>

`CreditNoteGetParams(*args, **kwargs)`
:   Parameters for credit_note.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CreditNoteGtCondition"></a>

`CreditNoteGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.chargebee.types.CreditNoteSearchFilter`
    :   The type of the None singleton.

<a id="CreditNoteGteCondition"></a>

`CreditNoteGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.chargebee.types.CreditNoteSearchFilter`
    :   The type of the None singleton.

<a id="CreditNoteInCondition"></a>

`CreditNoteInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.chargebee.types.CreditNoteInFilter`
    :   The type of the None singleton.

<a id="CreditNoteInFilter"></a>

`CreditNoteInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allocations: list[list[typing.Any]]`
    :   Details of allocations associated with the credit note

    `amount_allocated: list[int]`
    :   The amount of credits allocated.

    `amount_available: list[int]`
    :   The amount of credits available.

    `amount_refunded: list[int]`
    :   The amount of credits refunded.

    `base_currency_code: list[str]`
    :   The base currency code for the credit note.

    `billing_address: list[dict[str, typing.Any]]`
    :   Details of the billing address associated with the credit note

    `business_entity_id: list[str]`
    :   The ID of the business entity associated with the credit note.

    `channel: list[str]`
    :   The channel through which the credit note was created.

    `create_reason_code: list[str]`
    :   The reason code for creating the credit note.

    `currency_code: list[str]`
    :   The currency code for the credit note.

    `custom_fields: list[list[typing.Any]]`
    :   The type of the None singleton.

    `customer_id: list[str]`
    :   The ID of the customer associated with the credit note.

    `customer_notes: list[str]`
    :   Notes provided by the customer for the credit note.

    `date: list[int]`
    :   The date when the credit note was created.

    `deleted: list[bool]`
    :   Indicates if the credit note has been deleted.

    `discounts: list[list[typing.Any]]`
    :   Details of discounts applied to the credit note

    `exchange_rate: list[float]`
    :   The exchange rate used for currency conversion.

    `fractional_correction: list[int]`
    :   Fractional correction for rounding off decimals.

    `generated_at: list[int]`
    :   The date when the credit note was generated.

    `id: list[str]`
    :   The unique identifier for the credit note.

    `is_digital: list[bool]`
    :   Indicates if the credit note is in digital format.

    `is_vat_moss_registered: list[bool]`
    :   Indicates if VAT MOSS registration applies.

    `line_item_discounts: list[list[typing.Any]]`
    :   Details of discounts applied at the line item level in the credit note

    `line_item_taxes: list[list[typing.Any]]`
    :   Details of taxes applied at the line item level in the credit note

    `line_item_tiers: list[list[typing.Any]]`
    :   Details of tiers applied to line items in the credit note

    `line_items: list[list[typing.Any]]`
    :   Details of line items in the credit note

    `linked_refunds: list[list[typing.Any]]`
    :   Details of linked refunds to the credit note

    `linked_tax_withheld_refunds: list[list[typing.Any]]`
    :   Details of linked tax withheld refunds to the credit note

    `local_currency_code: list[str]`
    :   The local currency code for the credit note.

    `object_: list[str]`
    :   The object type of the credit note.

    `price_type: list[str]`
    :   The type of pricing used for the credit note.

    `reason_code: list[str]`
    :   The reason code for creating the credit note.

    `reference_invoice_id: list[str]`
    :   The ID of the invoice this credit note references.

    `refunded_at: list[int]`
    :   The date when the credit note was refunded.

    `resource_version: list[int]`
    :   The version of the credit note resource.

    `round_off_amount: list[int]`
    :   Amount rounded off for currency conversions.

    `shipping_address: list[dict[str, typing.Any]]`
    :   Details of the shipping address associated with the credit note

    `status: list[str]`
    :   The status of the credit note.

    `sub_total: list[int]`
    :   The subtotal amount of the credit note.

    `sub_total_in_local_currency: list[int]`
    :   The subtotal amount in local currency.

    `subscription_id: list[str]`
    :   The ID of the subscription associated with the credit note.

    `taxes: list[list[typing.Any]]`
    :   List of taxes applied to the credit note

    `total: list[int]`
    :   The total amount of the credit note.

    `total_in_local_currency: list[int]`
    :   The total amount in local currency.

    `type_: list[str]`
    :   The type of credit note.

    `updated_at: list[int]`
    :   The date when the credit note was last updated.

    `vat_number: list[str]`
    :   VAT number associated with the credit note.

    `vat_number_prefix: list[str]`
    :   Prefix for the VAT number.

    `voided_at: list[int]`
    :   The date when the credit note was voided.

<a id="CreditNoteKeywordCondition"></a>

`CreditNoteKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.chargebee.types.CreditNoteStringFilter`
    :   The type of the None singleton.

<a id="CreditNoteLikeCondition"></a>

`CreditNoteLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.chargebee.types.CreditNoteStringFilter`
    :   The type of the None singleton.

<a id="CreditNoteListParams"></a>

`CreditNoteListParams(*args, **kwargs)`
:   Parameters for credit_note.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

<a id="CreditNoteLtCondition"></a>

`CreditNoteLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.chargebee.types.CreditNoteSearchFilter`
    :   The type of the None singleton.

<a id="CreditNoteLteCondition"></a>

`CreditNoteLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.chargebee.types.CreditNoteSearchFilter`
    :   The type of the None singleton.

<a id="CreditNoteNeqCondition"></a>

`CreditNoteNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.chargebee.types.CreditNoteSearchFilter`
    :   The type of the None singleton.

<a id="CreditNoteNotCondition"></a>

`CreditNoteNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.chargebee.types.CreditNoteEqCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteGtCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteGteCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteLtCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteLteCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteInCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteNotCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteAndCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteOrCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteAnyCondition`
    :   The type of the None singleton.

<a id="CreditNoteOrCondition"></a>

`CreditNoteOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.chargebee.types.CreditNoteEqCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteGtCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteGteCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteLtCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteLteCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteInCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteNotCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteAndCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteOrCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteAnyCondition]`
    :   The type of the None singleton.

<a id="CreditNoteSearchFilter"></a>

`CreditNoteSearchFilter(*args, **kwargs)`
:   Available fields for filtering credit_note search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CreditNoteSearchQuery"></a>

`CreditNoteSearchQuery(*args, **kwargs)`
:   Search query for credit_note entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.chargebee.types.CreditNoteEqCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteGtCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteGteCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteLtCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteLteCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteInCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteNotCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteAndCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteOrCondition | airbyte_agent_sdk.connectors.chargebee.types.CreditNoteAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.chargebee.types.CreditNoteSortFilter]`
    :   The type of the None singleton.

<a id="CreditNoteSortFilter"></a>

`CreditNoteSortFilter(*args, **kwargs)`
:   Available fields for sorting credit_note search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allocations: Literal['asc', 'desc']`
    :   Details of allocations associated with the credit note

    `amount_allocated: Literal['asc', 'desc']`
    :   The amount of credits allocated.

    `amount_available: Literal['asc', 'desc']`
    :   The amount of credits available.

    `amount_refunded: Literal['asc', 'desc']`
    :   The amount of credits refunded.

    `base_currency_code: Literal['asc', 'desc']`
    :   The base currency code for the credit note.

    `billing_address: Literal['asc', 'desc']`
    :   Details of the billing address associated with the credit note

    `business_entity_id: Literal['asc', 'desc']`
    :   The ID of the business entity associated with the credit note.

    `channel: Literal['asc', 'desc']`
    :   The channel through which the credit note was created.

    `create_reason_code: Literal['asc', 'desc']`
    :   The reason code for creating the credit note.

    `currency_code: Literal['asc', 'desc']`
    :   The currency code for the credit note.

    `custom_fields: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `customer_id: Literal['asc', 'desc']`
    :   The ID of the customer associated with the credit note.

    `customer_notes: Literal['asc', 'desc']`
    :   Notes provided by the customer for the credit note.

    `date: Literal['asc', 'desc']`
    :   The date when the credit note was created.

    `deleted: Literal['asc', 'desc']`
    :   Indicates if the credit note has been deleted.

    `discounts: Literal['asc', 'desc']`
    :   Details of discounts applied to the credit note

    `exchange_rate: Literal['asc', 'desc']`
    :   The exchange rate used for currency conversion.

    `fractional_correction: Literal['asc', 'desc']`
    :   Fractional correction for rounding off decimals.

    `generated_at: Literal['asc', 'desc']`
    :   The date when the credit note was generated.

    `id: Literal['asc', 'desc']`
    :   The unique identifier for the credit note.

    `is_digital: Literal['asc', 'desc']`
    :   Indicates if the credit note is in digital format.

    `is_vat_moss_registered: Literal['asc', 'desc']`
    :   Indicates if VAT MOSS registration applies.

    `line_item_discounts: Literal['asc', 'desc']`
    :   Details of discounts applied at the line item level in the credit note

    `line_item_taxes: Literal['asc', 'desc']`
    :   Details of taxes applied at the line item level in the credit note

    `line_item_tiers: Literal['asc', 'desc']`
    :   Details of tiers applied to line items in the credit note

    `line_items: Literal['asc', 'desc']`
    :   Details of line items in the credit note

    `linked_refunds: Literal['asc', 'desc']`
    :   Details of linked refunds to the credit note

    `linked_tax_withheld_refunds: Literal['asc', 'desc']`
    :   Details of linked tax withheld refunds to the credit note

    `local_currency_code: Literal['asc', 'desc']`
    :   The local currency code for the credit note.

    `object_: Literal['asc', 'desc']`
    :   The object type of the credit note.

    `price_type: Literal['asc', 'desc']`
    :   The type of pricing used for the credit note.

    `reason_code: Literal['asc', 'desc']`
    :   The reason code for creating the credit note.

    `reference_invoice_id: Literal['asc', 'desc']`
    :   The ID of the invoice this credit note references.

    `refunded_at: Literal['asc', 'desc']`
    :   The date when the credit note was refunded.

    `resource_version: Literal['asc', 'desc']`
    :   The version of the credit note resource.

    `round_off_amount: Literal['asc', 'desc']`
    :   Amount rounded off for currency conversions.

    `shipping_address: Literal['asc', 'desc']`
    :   Details of the shipping address associated with the credit note

    `status: Literal['asc', 'desc']`
    :   The status of the credit note.

    `sub_total: Literal['asc', 'desc']`
    :   The subtotal amount of the credit note.

    `sub_total_in_local_currency: Literal['asc', 'desc']`
    :   The subtotal amount in local currency.

    `subscription_id: Literal['asc', 'desc']`
    :   The ID of the subscription associated with the credit note.

    `taxes: Literal['asc', 'desc']`
    :   List of taxes applied to the credit note

    `total: Literal['asc', 'desc']`
    :   The total amount of the credit note.

    `total_in_local_currency: Literal['asc', 'desc']`
    :   The total amount in local currency.

    `type_: Literal['asc', 'desc']`
    :   The type of credit note.

    `updated_at: Literal['asc', 'desc']`
    :   The date when the credit note was last updated.

    `vat_number: Literal['asc', 'desc']`
    :   VAT number associated with the credit note.

    `vat_number_prefix: Literal['asc', 'desc']`
    :   Prefix for the VAT number.

    `voided_at: Literal['asc', 'desc']`
    :   The date when the credit note was voided.

<a id="CreditNoteStringFilter"></a>

`CreditNoteStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allocations: str`
    :   Details of allocations associated with the credit note

    `amount_allocated: str`
    :   The amount of credits allocated.

    `amount_available: str`
    :   The amount of credits available.

    `amount_refunded: str`
    :   The amount of credits refunded.

    `base_currency_code: str`
    :   The base currency code for the credit note.

    `billing_address: str`
    :   Details of the billing address associated with the credit note

    `business_entity_id: str`
    :   The ID of the business entity associated with the credit note.

    `channel: str`
    :   The channel through which the credit note was created.

    `create_reason_code: str`
    :   The reason code for creating the credit note.

    `currency_code: str`
    :   The currency code for the credit note.

    `custom_fields: str`
    :   The type of the None singleton.

    `customer_id: str`
    :   The ID of the customer associated with the credit note.

    `customer_notes: str`
    :   Notes provided by the customer for the credit note.

    `date: str`
    :   The date when the credit note was created.

    `deleted: str`
    :   Indicates if the credit note has been deleted.

    `discounts: str`
    :   Details of discounts applied to the credit note

    `exchange_rate: str`
    :   The exchange rate used for currency conversion.

    `fractional_correction: str`
    :   Fractional correction for rounding off decimals.

    `generated_at: str`
    :   The date when the credit note was generated.

    `id: str`
    :   The unique identifier for the credit note.

    `is_digital: str`
    :   Indicates if the credit note is in digital format.

    `is_vat_moss_registered: str`
    :   Indicates if VAT MOSS registration applies.

    `line_item_discounts: str`
    :   Details of discounts applied at the line item level in the credit note

    `line_item_taxes: str`
    :   Details of taxes applied at the line item level in the credit note

    `line_item_tiers: str`
    :   Details of tiers applied to line items in the credit note

    `line_items: str`
    :   Details of line items in the credit note

    `linked_refunds: str`
    :   Details of linked refunds to the credit note

    `linked_tax_withheld_refunds: str`
    :   Details of linked tax withheld refunds to the credit note

    `local_currency_code: str`
    :   The local currency code for the credit note.

    `object_: str`
    :   The object type of the credit note.

    `price_type: str`
    :   The type of pricing used for the credit note.

    `reason_code: str`
    :   The reason code for creating the credit note.

    `reference_invoice_id: str`
    :   The ID of the invoice this credit note references.

    `refunded_at: str`
    :   The date when the credit note was refunded.

    `resource_version: str`
    :   The version of the credit note resource.

    `round_off_amount: str`
    :   Amount rounded off for currency conversions.

    `shipping_address: str`
    :   Details of the shipping address associated with the credit note

    `status: str`
    :   The status of the credit note.

    `sub_total: str`
    :   The subtotal amount of the credit note.

    `sub_total_in_local_currency: str`
    :   The subtotal amount in local currency.

    `subscription_id: str`
    :   The ID of the subscription associated with the credit note.

    `taxes: str`
    :   List of taxes applied to the credit note

    `total: str`
    :   The total amount of the credit note.

    `total_in_local_currency: str`
    :   The total amount in local currency.

    `type_: str`
    :   The type of credit note.

    `updated_at: str`
    :   The date when the credit note was last updated.

    `vat_number: str`
    :   VAT number associated with the credit note.

    `vat_number_prefix: str`
    :   Prefix for the VAT number.

    `voided_at: str`
    :   The date when the credit note was voided.

<a id="CustomerAndCondition"></a>

`CustomerAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.chargebee.types.CustomerEqCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerGtCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerGteCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerLtCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerLteCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerInCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerNotCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerAndCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerOrCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerAnyCondition]`
    :   The type of the None singleton.

<a id="CustomerAnyCondition"></a>

`CustomerAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.chargebee.types.CustomerAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomerAnyValueFilter"></a>

`CustomerAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allow_direct_debit: Any`
    :   Indicates if direct debit is allowed for the customer.

    `auto_close_invoices: Any`
    :   Flag to automatically close invoices for the customer.

    `auto_collection: Any`
    :   Configures the automatic collection settings for the customer.

    `backup_payment_source_id: Any`
    :   ID of the backup payment source for the customer.

    `balances: Any`
    :   Customer's balance information related to their account.

    `billing_address: Any`
    :   Customer's billing address details.

    `billing_date: Any`
    :   Date for billing cycle.

    `billing_date_mode: Any`
    :   Mode for billing date calculation.

    `billing_day_of_week: Any`
    :   Day of the week for billing cycle.

    `billing_day_of_week_mode: Any`
    :   Mode for billing day of the week calculation.

    `billing_month: Any`
    :   Month for billing cycle.

    `business_customer_without_vat_number: Any`
    :   Flag indicating business customer without a VAT number.

    `business_entity_id: Any`
    :   ID of the business entity.

    `card_status: Any`
    :   Status of payment card associated with the customer.

    `channel: Any`
    :   Channel through which the customer was acquired.

    `child_account_access: Any`
    :   Information regarding the access rights of child accounts linked to the customer's account.

    `client_profile_id: Any`
    :   Client profile ID of the customer.

    `company: Any`
    :   Company or organization name.

    `consolidated_invoicing: Any`
    :   Flag for consolidated invoicing setting.

    `contacts: Any`
    :   List of contact details associated with the customer.

    `created_at: Any`
    :   Date and time when the customer was created.

    `created_from_ip: Any`
    :   IP address from which the customer was created.

    `custom_fields: Any`
    :   The type of the None singleton.

    `customer_type: Any`
    :   Type of customer (e.g., individual, business).

    `deleted: Any`
    :   Flag indicating if the customer is deleted.

    `email: Any`
    :   Email address of the customer.

    `entity_code: Any`
    :   Code for the customer entity.

    `excess_payments: Any`
    :   Total amount of excess payments by the customer.

    `exempt_number: Any`
    :   Exemption number for tax purposes.

    `exemption_details: Any`
    :   Details about any exemptions applicable to the customer's account.

    `first_name: Any`
    :   First name of the customer.

    `fraud_flag: Any`
    :   Flag indicating if fraud is associated with the customer.

    `id: Any`
    :   Unique ID of the customer.

    `invoice_notes: Any`
    :   Notes added to the customer's invoices.

    `is_location_valid: Any`
    :   Flag indicating if the customer location is valid.

    `last_name: Any`
    :   Last name of the customer.

    `locale: Any`
    :   Locale setting for the customer.

    `meta_data: Any`
    :   Additional metadata associated with the customer.

    `mrr: Any`
    :   Monthly recurring revenue generated from the customer.

    `net_term_days: Any`
    :   Number of days for net terms.

    `object_: Any`
    :   Object type for the customer.

    `offline_payment_method: Any`
    :   Offline payment method used by the customer.

    `parent_account_access: Any`
    :   Information regarding the access rights of the parent account, if applicable.

    `payment_method: Any`
    :   Customer's preferred payment method details.

    `phone: Any`
    :   Phone number of the customer.

    `pii_cleared: Any`
    :   Flag indicating if PII (Personally Identifiable Information) is cleared.

    `preferred_currency_code: Any`
    :   Preferred currency code for transactions.

    `primary_payment_source_id: Any`
    :   ID of the primary payment source for the customer.

    `promotional_credits: Any`
    :   Total amount of promotional credits used.

    `referral_urls: Any`
    :   List of referral URLs associated with the customer.

    `refundable_credits: Any`
    :   Total amount of refundable credits.

    `registered_for_gst: Any`
    :   Flag indicating if the customer is registered for GST.

    `relationship: Any`
    :   Details about the relationship of the customer to other entities, if any.

    `resource_version: Any`
    :   Version of the customer's resource.

    `tax_providers_fields: Any`
    :   Fields related to tax providers.

    `taxability: Any`
    :   Taxability status of the customer.

    `unbilled_charges: Any`
    :   Total amount of unbilled charges.

    `updated_at: Any`
    :   Date and time when the customer record was last updated.

    `use_default_hierarchy_settings: Any`
    :   Flag indicating if default hierarchy settings are used.

    `vat_number: Any`
    :   VAT number associated with the customer.

    `vat_number_prefix: Any`
    :   Prefix for the VAT number.

    `vat_number_status: Any`
    :   Status of the VAT number validation.

    `vat_number_validated_time: Any`
    :   Date and time when the VAT number was validated.

<a id="CustomerContainsCondition"></a>

`CustomerContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.chargebee.types.CustomerAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomerEqCondition"></a>

`CustomerEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.chargebee.types.CustomerSearchFilter`
    :   The type of the None singleton.

<a id="CustomerFuzzyCondition"></a>

`CustomerFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.chargebee.types.CustomerStringFilter`
    :   The type of the None singleton.

<a id="CustomerGetParams"></a>

`CustomerGetParams(*args, **kwargs)`
:   Parameters for customer.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CustomerGtCondition"></a>

`CustomerGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.chargebee.types.CustomerSearchFilter`
    :   The type of the None singleton.

<a id="CustomerGteCondition"></a>

`CustomerGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.chargebee.types.CustomerSearchFilter`
    :   The type of the None singleton.

<a id="CustomerInCondition"></a>

`CustomerInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.chargebee.types.CustomerInFilter`
    :   The type of the None singleton.

<a id="CustomerInFilter"></a>

`CustomerInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allow_direct_debit: list[bool]`
    :   Indicates if direct debit is allowed for the customer.

    `auto_close_invoices: list[bool]`
    :   Flag to automatically close invoices for the customer.

    `auto_collection: list[str]`
    :   Configures the automatic collection settings for the customer.

    `backup_payment_source_id: list[str]`
    :   ID of the backup payment source for the customer.

    `balances: list[list[typing.Any]]`
    :   Customer's balance information related to their account.

    `billing_address: list[dict[str, typing.Any]]`
    :   Customer's billing address details.

    `billing_date: list[int]`
    :   Date for billing cycle.

    `billing_date_mode: list[str]`
    :   Mode for billing date calculation.

    `billing_day_of_week: list[str]`
    :   Day of the week for billing cycle.

    `billing_day_of_week_mode: list[str]`
    :   Mode for billing day of the week calculation.

    `billing_month: list[int]`
    :   Month for billing cycle.

    `business_customer_without_vat_number: list[bool]`
    :   Flag indicating business customer without a VAT number.

    `business_entity_id: list[str]`
    :   ID of the business entity.

    `card_status: list[str]`
    :   Status of payment card associated with the customer.

    `channel: list[str]`
    :   Channel through which the customer was acquired.

    `child_account_access: list[dict[str, typing.Any]]`
    :   Information regarding the access rights of child accounts linked to the customer's account.

    `client_profile_id: list[str]`
    :   Client profile ID of the customer.

    `company: list[str]`
    :   Company or organization name.

    `consolidated_invoicing: list[bool]`
    :   Flag for consolidated invoicing setting.

    `contacts: list[list[typing.Any]]`
    :   List of contact details associated with the customer.

    `created_at: list[int]`
    :   Date and time when the customer was created.

    `created_from_ip: list[str]`
    :   IP address from which the customer was created.

    `custom_fields: list[list[typing.Any]]`
    :   The type of the None singleton.

    `customer_type: list[str]`
    :   Type of customer (e.g., individual, business).

    `deleted: list[bool]`
    :   Flag indicating if the customer is deleted.

    `email: list[str]`
    :   Email address of the customer.

    `entity_code: list[str]`
    :   Code for the customer entity.

    `excess_payments: list[int]`
    :   Total amount of excess payments by the customer.

    `exempt_number: list[str]`
    :   Exemption number for tax purposes.

    `exemption_details: list[list[typing.Any]]`
    :   Details about any exemptions applicable to the customer's account.

    `first_name: list[str]`
    :   First name of the customer.

    `fraud_flag: list[str]`
    :   Flag indicating if fraud is associated with the customer.

    `id: list[str]`
    :   Unique ID of the customer.

    `invoice_notes: list[str]`
    :   Notes added to the customer's invoices.

    `is_location_valid: list[bool]`
    :   Flag indicating if the customer location is valid.

    `last_name: list[str]`
    :   Last name of the customer.

    `locale: list[str]`
    :   Locale setting for the customer.

    `meta_data: list[dict[str, typing.Any]]`
    :   Additional metadata associated with the customer.

    `mrr: list[int]`
    :   Monthly recurring revenue generated from the customer.

    `net_term_days: list[int]`
    :   Number of days for net terms.

    `object_: list[str]`
    :   Object type for the customer.

    `offline_payment_method: list[str]`
    :   Offline payment method used by the customer.

    `parent_account_access: list[dict[str, typing.Any]]`
    :   Information regarding the access rights of the parent account, if applicable.

    `payment_method: list[dict[str, typing.Any]]`
    :   Customer's preferred payment method details.

    `phone: list[str]`
    :   Phone number of the customer.

    `pii_cleared: list[str]`
    :   Flag indicating if PII (Personally Identifiable Information) is cleared.

    `preferred_currency_code: list[str]`
    :   Preferred currency code for transactions.

    `primary_payment_source_id: list[str]`
    :   ID of the primary payment source for the customer.

    `promotional_credits: list[int]`
    :   Total amount of promotional credits used.

    `referral_urls: list[list[typing.Any]]`
    :   List of referral URLs associated with the customer.

    `refundable_credits: list[int]`
    :   Total amount of refundable credits.

    `registered_for_gst: list[bool]`
    :   Flag indicating if the customer is registered for GST.

    `relationship: list[dict[str, typing.Any]]`
    :   Details about the relationship of the customer to other entities, if any.

    `resource_version: list[int]`
    :   Version of the customer's resource.

    `tax_providers_fields: list[list[typing.Any]]`
    :   Fields related to tax providers.

    `taxability: list[str]`
    :   Taxability status of the customer.

    `unbilled_charges: list[int]`
    :   Total amount of unbilled charges.

    `updated_at: list[int]`
    :   Date and time when the customer record was last updated.

    `use_default_hierarchy_settings: list[bool]`
    :   Flag indicating if default hierarchy settings are used.

    `vat_number: list[str]`
    :   VAT number associated with the customer.

    `vat_number_prefix: list[str]`
    :   Prefix for the VAT number.

    `vat_number_status: list[str]`
    :   Status of the VAT number validation.

    `vat_number_validated_time: list[int]`
    :   Date and time when the VAT number was validated.

<a id="CustomerKeywordCondition"></a>

`CustomerKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.chargebee.types.CustomerStringFilter`
    :   The type of the None singleton.

<a id="CustomerLikeCondition"></a>

`CustomerLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.chargebee.types.CustomerStringFilter`
    :   The type of the None singleton.

<a id="CustomerListParams"></a>

`CustomerListParams(*args, **kwargs)`
:   Parameters for customer.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

<a id="CustomerLtCondition"></a>

`CustomerLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.chargebee.types.CustomerSearchFilter`
    :   The type of the None singleton.

<a id="CustomerLteCondition"></a>

`CustomerLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.chargebee.types.CustomerSearchFilter`
    :   The type of the None singleton.

<a id="CustomerNeqCondition"></a>

`CustomerNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.chargebee.types.CustomerSearchFilter`
    :   The type of the None singleton.

<a id="CustomerNotCondition"></a>

`CustomerNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.chargebee.types.CustomerEqCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerGtCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerGteCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerLtCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerLteCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerInCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerNotCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerAndCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerOrCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerAnyCondition`
    :   The type of the None singleton.

<a id="CustomerOrCondition"></a>

`CustomerOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.chargebee.types.CustomerEqCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerGtCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerGteCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerLtCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerLteCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerInCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerNotCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerAndCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerOrCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerAnyCondition]`
    :   The type of the None singleton.

<a id="CustomerSearchFilter"></a>

`CustomerSearchFilter(*args, **kwargs)`
:   Available fields for filtering customer search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CustomerSearchQuery"></a>

`CustomerSearchQuery(*args, **kwargs)`
:   Search query for customer entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.chargebee.types.CustomerEqCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerGtCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerGteCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerLtCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerLteCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerInCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerNotCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerAndCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerOrCondition | airbyte_agent_sdk.connectors.chargebee.types.CustomerAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.chargebee.types.CustomerSortFilter]`
    :   The type of the None singleton.

<a id="CustomerSortFilter"></a>

`CustomerSortFilter(*args, **kwargs)`
:   Available fields for sorting customer search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allow_direct_debit: Literal['asc', 'desc']`
    :   Indicates if direct debit is allowed for the customer.

    `auto_close_invoices: Literal['asc', 'desc']`
    :   Flag to automatically close invoices for the customer.

    `auto_collection: Literal['asc', 'desc']`
    :   Configures the automatic collection settings for the customer.

    `backup_payment_source_id: Literal['asc', 'desc']`
    :   ID of the backup payment source for the customer.

    `balances: Literal['asc', 'desc']`
    :   Customer's balance information related to their account.

    `billing_address: Literal['asc', 'desc']`
    :   Customer's billing address details.

    `billing_date: Literal['asc', 'desc']`
    :   Date for billing cycle.

    `billing_date_mode: Literal['asc', 'desc']`
    :   Mode for billing date calculation.

    `billing_day_of_week: Literal['asc', 'desc']`
    :   Day of the week for billing cycle.

    `billing_day_of_week_mode: Literal['asc', 'desc']`
    :   Mode for billing day of the week calculation.

    `billing_month: Literal['asc', 'desc']`
    :   Month for billing cycle.

    `business_customer_without_vat_number: Literal['asc', 'desc']`
    :   Flag indicating business customer without a VAT number.

    `business_entity_id: Literal['asc', 'desc']`
    :   ID of the business entity.

    `card_status: Literal['asc', 'desc']`
    :   Status of payment card associated with the customer.

    `channel: Literal['asc', 'desc']`
    :   Channel through which the customer was acquired.

    `child_account_access: Literal['asc', 'desc']`
    :   Information regarding the access rights of child accounts linked to the customer's account.

    `client_profile_id: Literal['asc', 'desc']`
    :   Client profile ID of the customer.

    `company: Literal['asc', 'desc']`
    :   Company or organization name.

    `consolidated_invoicing: Literal['asc', 'desc']`
    :   Flag for consolidated invoicing setting.

    `contacts: Literal['asc', 'desc']`
    :   List of contact details associated with the customer.

    `created_at: Literal['asc', 'desc']`
    :   Date and time when the customer was created.

    `created_from_ip: Literal['asc', 'desc']`
    :   IP address from which the customer was created.

    `custom_fields: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `customer_type: Literal['asc', 'desc']`
    :   Type of customer (e.g., individual, business).

    `deleted: Literal['asc', 'desc']`
    :   Flag indicating if the customer is deleted.

    `email: Literal['asc', 'desc']`
    :   Email address of the customer.

    `entity_code: Literal['asc', 'desc']`
    :   Code for the customer entity.

    `excess_payments: Literal['asc', 'desc']`
    :   Total amount of excess payments by the customer.

    `exempt_number: Literal['asc', 'desc']`
    :   Exemption number for tax purposes.

    `exemption_details: Literal['asc', 'desc']`
    :   Details about any exemptions applicable to the customer's account.

    `first_name: Literal['asc', 'desc']`
    :   First name of the customer.

    `fraud_flag: Literal['asc', 'desc']`
    :   Flag indicating if fraud is associated with the customer.

    `id: Literal['asc', 'desc']`
    :   Unique ID of the customer.

    `invoice_notes: Literal['asc', 'desc']`
    :   Notes added to the customer's invoices.

    `is_location_valid: Literal['asc', 'desc']`
    :   Flag indicating if the customer location is valid.

    `last_name: Literal['asc', 'desc']`
    :   Last name of the customer.

    `locale: Literal['asc', 'desc']`
    :   Locale setting for the customer.

    `meta_data: Literal['asc', 'desc']`
    :   Additional metadata associated with the customer.

    `mrr: Literal['asc', 'desc']`
    :   Monthly recurring revenue generated from the customer.

    `net_term_days: Literal['asc', 'desc']`
    :   Number of days for net terms.

    `object_: Literal['asc', 'desc']`
    :   Object type for the customer.

    `offline_payment_method: Literal['asc', 'desc']`
    :   Offline payment method used by the customer.

    `parent_account_access: Literal['asc', 'desc']`
    :   Information regarding the access rights of the parent account, if applicable.

    `payment_method: Literal['asc', 'desc']`
    :   Customer's preferred payment method details.

    `phone: Literal['asc', 'desc']`
    :   Phone number of the customer.

    `pii_cleared: Literal['asc', 'desc']`
    :   Flag indicating if PII (Personally Identifiable Information) is cleared.

    `preferred_currency_code: Literal['asc', 'desc']`
    :   Preferred currency code for transactions.

    `primary_payment_source_id: Literal['asc', 'desc']`
    :   ID of the primary payment source for the customer.

    `promotional_credits: Literal['asc', 'desc']`
    :   Total amount of promotional credits used.

    `referral_urls: Literal['asc', 'desc']`
    :   List of referral URLs associated with the customer.

    `refundable_credits: Literal['asc', 'desc']`
    :   Total amount of refundable credits.

    `registered_for_gst: Literal['asc', 'desc']`
    :   Flag indicating if the customer is registered for GST.

    `relationship: Literal['asc', 'desc']`
    :   Details about the relationship of the customer to other entities, if any.

    `resource_version: Literal['asc', 'desc']`
    :   Version of the customer's resource.

    `tax_providers_fields: Literal['asc', 'desc']`
    :   Fields related to tax providers.

    `taxability: Literal['asc', 'desc']`
    :   Taxability status of the customer.

    `unbilled_charges: Literal['asc', 'desc']`
    :   Total amount of unbilled charges.

    `updated_at: Literal['asc', 'desc']`
    :   Date and time when the customer record was last updated.

    `use_default_hierarchy_settings: Literal['asc', 'desc']`
    :   Flag indicating if default hierarchy settings are used.

    `vat_number: Literal['asc', 'desc']`
    :   VAT number associated with the customer.

    `vat_number_prefix: Literal['asc', 'desc']`
    :   Prefix for the VAT number.

    `vat_number_status: Literal['asc', 'desc']`
    :   Status of the VAT number validation.

    `vat_number_validated_time: Literal['asc', 'desc']`
    :   Date and time when the VAT number was validated.

<a id="CustomerStringFilter"></a>

`CustomerStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allow_direct_debit: str`
    :   Indicates if direct debit is allowed for the customer.

    `auto_close_invoices: str`
    :   Flag to automatically close invoices for the customer.

    `auto_collection: str`
    :   Configures the automatic collection settings for the customer.

    `backup_payment_source_id: str`
    :   ID of the backup payment source for the customer.

    `balances: str`
    :   Customer's balance information related to their account.

    `billing_address: str`
    :   Customer's billing address details.

    `billing_date: str`
    :   Date for billing cycle.

    `billing_date_mode: str`
    :   Mode for billing date calculation.

    `billing_day_of_week: str`
    :   Day of the week for billing cycle.

    `billing_day_of_week_mode: str`
    :   Mode for billing day of the week calculation.

    `billing_month: str`
    :   Month for billing cycle.

    `business_customer_without_vat_number: str`
    :   Flag indicating business customer without a VAT number.

    `business_entity_id: str`
    :   ID of the business entity.

    `card_status: str`
    :   Status of payment card associated with the customer.

    `channel: str`
    :   Channel through which the customer was acquired.

    `child_account_access: str`
    :   Information regarding the access rights of child accounts linked to the customer's account.

    `client_profile_id: str`
    :   Client profile ID of the customer.

    `company: str`
    :   Company or organization name.

    `consolidated_invoicing: str`
    :   Flag for consolidated invoicing setting.

    `contacts: str`
    :   List of contact details associated with the customer.

    `created_at: str`
    :   Date and time when the customer was created.

    `created_from_ip: str`
    :   IP address from which the customer was created.

    `custom_fields: str`
    :   The type of the None singleton.

    `customer_type: str`
    :   Type of customer (e.g., individual, business).

    `deleted: str`
    :   Flag indicating if the customer is deleted.

    `email: str`
    :   Email address of the customer.

    `entity_code: str`
    :   Code for the customer entity.

    `excess_payments: str`
    :   Total amount of excess payments by the customer.

    `exempt_number: str`
    :   Exemption number for tax purposes.

    `exemption_details: str`
    :   Details about any exemptions applicable to the customer's account.

    `first_name: str`
    :   First name of the customer.

    `fraud_flag: str`
    :   Flag indicating if fraud is associated with the customer.

    `id: str`
    :   Unique ID of the customer.

    `invoice_notes: str`
    :   Notes added to the customer's invoices.

    `is_location_valid: str`
    :   Flag indicating if the customer location is valid.

    `last_name: str`
    :   Last name of the customer.

    `locale: str`
    :   Locale setting for the customer.

    `meta_data: str`
    :   Additional metadata associated with the customer.

    `mrr: str`
    :   Monthly recurring revenue generated from the customer.

    `net_term_days: str`
    :   Number of days for net terms.

    `object_: str`
    :   Object type for the customer.

    `offline_payment_method: str`
    :   Offline payment method used by the customer.

    `parent_account_access: str`
    :   Information regarding the access rights of the parent account, if applicable.

    `payment_method: str`
    :   Customer's preferred payment method details.

    `phone: str`
    :   Phone number of the customer.

    `pii_cleared: str`
    :   Flag indicating if PII (Personally Identifiable Information) is cleared.

    `preferred_currency_code: str`
    :   Preferred currency code for transactions.

    `primary_payment_source_id: str`
    :   ID of the primary payment source for the customer.

    `promotional_credits: str`
    :   Total amount of promotional credits used.

    `referral_urls: str`
    :   List of referral URLs associated with the customer.

    `refundable_credits: str`
    :   Total amount of refundable credits.

    `registered_for_gst: str`
    :   Flag indicating if the customer is registered for GST.

    `relationship: str`
    :   Details about the relationship of the customer to other entities, if any.

    `resource_version: str`
    :   Version of the customer's resource.

    `tax_providers_fields: str`
    :   Fields related to tax providers.

    `taxability: str`
    :   Taxability status of the customer.

    `unbilled_charges: str`
    :   Total amount of unbilled charges.

    `updated_at: str`
    :   Date and time when the customer record was last updated.

    `use_default_hierarchy_settings: str`
    :   Flag indicating if default hierarchy settings are used.

    `vat_number: str`
    :   VAT number associated with the customer.

    `vat_number_prefix: str`
    :   Prefix for the VAT number.

    `vat_number_status: str`
    :   Status of the VAT number validation.

    `vat_number_validated_time: str`
    :   Date and time when the VAT number was validated.

<a id="EventAndCondition"></a>

`EventAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.chargebee.types.EventEqCondition | airbyte_agent_sdk.connectors.chargebee.types.EventNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.EventGtCondition | airbyte_agent_sdk.connectors.chargebee.types.EventGteCondition | airbyte_agent_sdk.connectors.chargebee.types.EventLtCondition | airbyte_agent_sdk.connectors.chargebee.types.EventLteCondition | airbyte_agent_sdk.connectors.chargebee.types.EventInCondition | airbyte_agent_sdk.connectors.chargebee.types.EventLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.EventFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.EventKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.EventContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.EventNotCondition | airbyte_agent_sdk.connectors.chargebee.types.EventAndCondition | airbyte_agent_sdk.connectors.chargebee.types.EventOrCondition | airbyte_agent_sdk.connectors.chargebee.types.EventAnyCondition]`
    :   The type of the None singleton.

<a id="EventAnyCondition"></a>

`EventAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.chargebee.types.EventAnyValueFilter`
    :   The type of the None singleton.

<a id="EventAnyValueFilter"></a>

`EventAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `api_version: Any`
    :   The version of the Chargebee API being used to fetch the event data.

    `content: Any`
    :   The specific content or information associated with the event.

    `custom_fields: Any`
    :   The type of the None singleton.

    `event_type: Any`
    :   The type or category of the event.

    `id: Any`
    :   Unique identifier for the event data record.

    `object_: Any`
    :   The object or entity that the event is triggered for.

    `occurred_at: Any`
    :   The datetime when the event occurred.

    `source: Any`
    :   The source or origin of the event data.

    `user: Any`
    :   Information about the user or entity associated with the event.

    `webhook_status: Any`
    :   The status of the webhook execution for the event.

    `webhooks: Any`
    :   List of webhooks associated with the event.

<a id="EventContainsCondition"></a>

`EventContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.chargebee.types.EventAnyValueFilter`
    :   The type of the None singleton.

<a id="EventEqCondition"></a>

`EventEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.chargebee.types.EventSearchFilter`
    :   The type of the None singleton.

<a id="EventFuzzyCondition"></a>

`EventFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.chargebee.types.EventStringFilter`
    :   The type of the None singleton.

<a id="EventGetParams"></a>

`EventGetParams(*args, **kwargs)`
:   Parameters for event.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="EventGtCondition"></a>

`EventGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.chargebee.types.EventSearchFilter`
    :   The type of the None singleton.

<a id="EventGteCondition"></a>

`EventGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.chargebee.types.EventSearchFilter`
    :   The type of the None singleton.

<a id="EventInCondition"></a>

`EventInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.chargebee.types.EventInFilter`
    :   The type of the None singleton.

<a id="EventInFilter"></a>

`EventInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `api_version: list[str]`
    :   The version of the Chargebee API being used to fetch the event data.

    `content: list[dict[str, typing.Any]]`
    :   The specific content or information associated with the event.

    `custom_fields: list[list[typing.Any]]`
    :   The type of the None singleton.

    `event_type: list[str]`
    :   The type or category of the event.

    `id: list[str]`
    :   Unique identifier for the event data record.

    `object_: list[str]`
    :   The object or entity that the event is triggered for.

    `occurred_at: list[int]`
    :   The datetime when the event occurred.

    `source: list[str]`
    :   The source or origin of the event data.

    `user: list[str]`
    :   Information about the user or entity associated with the event.

    `webhook_status: list[str]`
    :   The status of the webhook execution for the event.

    `webhooks: list[list[typing.Any]]`
    :   List of webhooks associated with the event.

<a id="EventKeywordCondition"></a>

`EventKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.chargebee.types.EventStringFilter`
    :   The type of the None singleton.

<a id="EventLikeCondition"></a>

`EventLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.chargebee.types.EventStringFilter`
    :   The type of the None singleton.

<a id="EventListParams"></a>

`EventListParams(*args, **kwargs)`
:   Parameters for event.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

<a id="EventLtCondition"></a>

`EventLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.chargebee.types.EventSearchFilter`
    :   The type of the None singleton.

<a id="EventLteCondition"></a>

`EventLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.chargebee.types.EventSearchFilter`
    :   The type of the None singleton.

<a id="EventNeqCondition"></a>

`EventNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.chargebee.types.EventSearchFilter`
    :   The type of the None singleton.

<a id="EventNotCondition"></a>

`EventNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.chargebee.types.EventEqCondition | airbyte_agent_sdk.connectors.chargebee.types.EventNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.EventGtCondition | airbyte_agent_sdk.connectors.chargebee.types.EventGteCondition | airbyte_agent_sdk.connectors.chargebee.types.EventLtCondition | airbyte_agent_sdk.connectors.chargebee.types.EventLteCondition | airbyte_agent_sdk.connectors.chargebee.types.EventInCondition | airbyte_agent_sdk.connectors.chargebee.types.EventLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.EventFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.EventKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.EventContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.EventNotCondition | airbyte_agent_sdk.connectors.chargebee.types.EventAndCondition | airbyte_agent_sdk.connectors.chargebee.types.EventOrCondition | airbyte_agent_sdk.connectors.chargebee.types.EventAnyCondition`
    :   The type of the None singleton.

<a id="EventOrCondition"></a>

`EventOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.chargebee.types.EventEqCondition | airbyte_agent_sdk.connectors.chargebee.types.EventNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.EventGtCondition | airbyte_agent_sdk.connectors.chargebee.types.EventGteCondition | airbyte_agent_sdk.connectors.chargebee.types.EventLtCondition | airbyte_agent_sdk.connectors.chargebee.types.EventLteCondition | airbyte_agent_sdk.connectors.chargebee.types.EventInCondition | airbyte_agent_sdk.connectors.chargebee.types.EventLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.EventFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.EventKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.EventContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.EventNotCondition | airbyte_agent_sdk.connectors.chargebee.types.EventAndCondition | airbyte_agent_sdk.connectors.chargebee.types.EventOrCondition | airbyte_agent_sdk.connectors.chargebee.types.EventAnyCondition]`
    :   The type of the None singleton.

<a id="EventSearchFilter"></a>

`EventSearchFilter(*args, **kwargs)`
:   Available fields for filtering event search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="EventSearchQuery"></a>

`EventSearchQuery(*args, **kwargs)`
:   Search query for event entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.chargebee.types.EventEqCondition | airbyte_agent_sdk.connectors.chargebee.types.EventNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.EventGtCondition | airbyte_agent_sdk.connectors.chargebee.types.EventGteCondition | airbyte_agent_sdk.connectors.chargebee.types.EventLtCondition | airbyte_agent_sdk.connectors.chargebee.types.EventLteCondition | airbyte_agent_sdk.connectors.chargebee.types.EventInCondition | airbyte_agent_sdk.connectors.chargebee.types.EventLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.EventFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.EventKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.EventContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.EventNotCondition | airbyte_agent_sdk.connectors.chargebee.types.EventAndCondition | airbyte_agent_sdk.connectors.chargebee.types.EventOrCondition | airbyte_agent_sdk.connectors.chargebee.types.EventAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.chargebee.types.EventSortFilter]`
    :   The type of the None singleton.

<a id="EventSortFilter"></a>

`EventSortFilter(*args, **kwargs)`
:   Available fields for sorting event search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `api_version: Literal['asc', 'desc']`
    :   The version of the Chargebee API being used to fetch the event data.

    `content: Literal['asc', 'desc']`
    :   The specific content or information associated with the event.

    `custom_fields: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `event_type: Literal['asc', 'desc']`
    :   The type or category of the event.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the event data record.

    `object_: Literal['asc', 'desc']`
    :   The object or entity that the event is triggered for.

    `occurred_at: Literal['asc', 'desc']`
    :   The datetime when the event occurred.

    `source: Literal['asc', 'desc']`
    :   The source or origin of the event data.

    `user: Literal['asc', 'desc']`
    :   Information about the user or entity associated with the event.

    `webhook_status: Literal['asc', 'desc']`
    :   The status of the webhook execution for the event.

    `webhooks: Literal['asc', 'desc']`
    :   List of webhooks associated with the event.

<a id="EventStringFilter"></a>

`EventStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `api_version: str`
    :   The version of the Chargebee API being used to fetch the event data.

    `content: str`
    :   The specific content or information associated with the event.

    `custom_fields: str`
    :   The type of the None singleton.

    `event_type: str`
    :   The type or category of the event.

    `id: str`
    :   Unique identifier for the event data record.

    `object_: str`
    :   The object or entity that the event is triggered for.

    `occurred_at: str`
    :   The datetime when the event occurred.

    `source: str`
    :   The source or origin of the event data.

    `user: str`
    :   Information about the user or entity associated with the event.

    `webhook_status: str`
    :   The status of the webhook execution for the event.

    `webhooks: str`
    :   List of webhooks associated with the event.

<a id="InvoiceAndCondition"></a>

`InvoiceAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.chargebee.types.InvoiceEqCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceGtCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceGteCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceLtCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceLteCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceInCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceNotCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceAndCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceOrCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceAnyCondition]`
    :   The type of the None singleton.

<a id="InvoiceAnyCondition"></a>

`InvoiceAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.chargebee.types.InvoiceAnyValueFilter`
    :   The type of the None singleton.

<a id="InvoiceAnyValueFilter"></a>

`InvoiceAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adjustment_credit_notes: Any`
    :   Details of adjustment credit notes applied to the invoice

    `amount_adjusted: Any`
    :   Total amount adjusted in the invoice

    `amount_due: Any`
    :   Amount due for payment

    `amount_paid: Any`
    :   Amount already paid

    `amount_to_collect: Any`
    :   Amount yet to be collected

    `applied_credits: Any`
    :   Details of credits applied to the invoice

    `base_currency_code: Any`
    :   Currency code used as base for the invoice

    `billing_address: Any`
    :   Details of the billing address associated with the invoice

    `business_entity_id: Any`
    :   ID of the business entity

    `channel: Any`
    :   Channel through which the invoice was generated

    `credits_applied: Any`
    :   Total credits applied to the invoice

    `currency_code: Any`
    :   Currency code of the invoice

    `custom_fields: Any`
    :   The type of the None singleton.

    `customer_id: Any`
    :   ID of the customer

    `date: Any`
    :   Date of the invoice

    `deleted: Any`
    :   Flag indicating if the invoice is deleted

    `discounts: Any`
    :   Discount details applied to the invoice

    `due_date: Any`
    :   Due date for payment

    `dunning_attempts: Any`
    :   Details of dunning attempts made

    `dunning_status: Any`
    :   Status of dunning for the invoice

    `einvoice: Any`
    :   Details of electronic invoice

    `exchange_rate: Any`
    :   Exchange rate used for currency conversion

    `expected_payment_date: Any`
    :   Expected date of payment

    `first_invoice: Any`
    :   Flag indicating whether it's the first invoice

    `generated_at: Any`
    :   Date when the invoice was generated

    `has_advance_charges: Any`
    :   Flag indicating if there are advance charges

    `id: Any`
    :   Unique ID of the invoice

    `is_digital: Any`
    :   Flag indicating if the invoice is digital

    `is_gifted: Any`
    :   Flag indicating if the invoice is gifted

    `issued_credit_notes: Any`
    :   Details of credit notes issued

    `line_item_discounts: Any`
    :   Details of line item discounts

    `line_item_taxes: Any`
    :   Tax details applied to each line item in the invoice

    `line_item_tiers: Any`
    :   Tiers information for each line item in the invoice

    `line_items: Any`
    :   Details of individual line items in the invoice

    `linked_orders: Any`
    :   Details of linked orders to the invoice

    `linked_payments: Any`
    :   Details of linked payments

    `linked_taxes_withheld: Any`
    :   Details of linked taxes withheld on the invoice

    `local_currency_code: Any`
    :   Local currency code of the invoice

    `local_currency_exchange_rate: Any`
    :   Exchange rate for local currency conversion

    `net_term_days: Any`
    :   Net term days for payment

    `new_sales_amount: Any`
    :   New sales amount in the invoice

    `next_retry_at: Any`
    :   Date of the next payment retry

    `notes: Any`
    :   Notes associated with the invoice

    `object_: Any`
    :   Type of object

    `paid_at: Any`
    :   Date when the invoice was paid

    `payment_owner: Any`
    :   Owner of the payment

    `po_number: Any`
    :   Purchase order number

    `price_type: Any`
    :   Type of pricing

    `recurring: Any`
    :   Flag indicating if it's a recurring invoice

    `resource_version: Any`
    :   Resource version of the invoice

    `round_off_amount: Any`
    :   Amount rounded off

    `shipping_address: Any`
    :   Details of the shipping address associated with the invoice

    `statement_descriptor: Any`
    :   Descriptor for the statement

    `status: Any`
    :   Status of the invoice

    `sub_total: Any`
    :   Subtotal amount

    `sub_total_in_local_currency: Any`
    :   Subtotal amount in local currency

    `subscription_id: Any`
    :   ID of the subscription associated

    `tax: Any`
    :   Total tax amount

    `tax_category: Any`
    :   Tax category

    `taxes: Any`
    :   Details of taxes applied

    `term_finalized: Any`
    :   Flag indicating if the term is finalized

    `total: Any`
    :   Total amount of the invoice

    `total_in_local_currency: Any`
    :   Total amount in local currency

    `updated_at: Any`
    :   Date of last update

    `vat_number: Any`
    :   VAT number

    `vat_number_prefix: Any`
    :   Prefix for the VAT number

    `void_reason_code: Any`
    :   Reason code for voiding the invoice

    `voided_at: Any`
    :   Date when the invoice was voided

    `write_off_amount: Any`
    :   Amount written off

<a id="InvoiceContainsCondition"></a>

`InvoiceContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.chargebee.types.InvoiceAnyValueFilter`
    :   The type of the None singleton.

<a id="InvoiceEqCondition"></a>

`InvoiceEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.chargebee.types.InvoiceSearchFilter`
    :   The type of the None singleton.

<a id="InvoiceFuzzyCondition"></a>

`InvoiceFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.chargebee.types.InvoiceStringFilter`
    :   The type of the None singleton.

<a id="InvoiceGetParams"></a>

`InvoiceGetParams(*args, **kwargs)`
:   Parameters for invoice.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="InvoiceGtCondition"></a>

`InvoiceGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.chargebee.types.InvoiceSearchFilter`
    :   The type of the None singleton.

<a id="InvoiceGteCondition"></a>

`InvoiceGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.chargebee.types.InvoiceSearchFilter`
    :   The type of the None singleton.

<a id="InvoiceInCondition"></a>

`InvoiceInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.chargebee.types.InvoiceInFilter`
    :   The type of the None singleton.

<a id="InvoiceInFilter"></a>

`InvoiceInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adjustment_credit_notes: list[list[typing.Any]]`
    :   Details of adjustment credit notes applied to the invoice

    `amount_adjusted: list[int]`
    :   Total amount adjusted in the invoice

    `amount_due: list[int]`
    :   Amount due for payment

    `amount_paid: list[int]`
    :   Amount already paid

    `amount_to_collect: list[int]`
    :   Amount yet to be collected

    `applied_credits: list[list[typing.Any]]`
    :   Details of credits applied to the invoice

    `base_currency_code: list[str]`
    :   Currency code used as base for the invoice

    `billing_address: list[dict[str, typing.Any]]`
    :   Details of the billing address associated with the invoice

    `business_entity_id: list[str]`
    :   ID of the business entity

    `channel: list[str]`
    :   Channel through which the invoice was generated

    `credits_applied: list[int]`
    :   Total credits applied to the invoice

    `currency_code: list[str]`
    :   Currency code of the invoice

    `custom_fields: list[list[typing.Any]]`
    :   The type of the None singleton.

    `customer_id: list[str]`
    :   ID of the customer

    `date: list[int]`
    :   Date of the invoice

    `deleted: list[bool]`
    :   Flag indicating if the invoice is deleted

    `discounts: list[list[typing.Any]]`
    :   Discount details applied to the invoice

    `due_date: list[int]`
    :   Due date for payment

    `dunning_attempts: list[list[typing.Any]]`
    :   Details of dunning attempts made

    `dunning_status: list[str]`
    :   Status of dunning for the invoice

    `einvoice: list[dict[str, typing.Any]]`
    :   Details of electronic invoice

    `exchange_rate: list[float]`
    :   Exchange rate used for currency conversion

    `expected_payment_date: list[int]`
    :   Expected date of payment

    `first_invoice: list[bool]`
    :   Flag indicating whether it's the first invoice

    `generated_at: list[int]`
    :   Date when the invoice was generated

    `has_advance_charges: list[bool]`
    :   Flag indicating if there are advance charges

    `id: list[str]`
    :   Unique ID of the invoice

    `is_digital: list[bool]`
    :   Flag indicating if the invoice is digital

    `is_gifted: list[bool]`
    :   Flag indicating if the invoice is gifted

    `issued_credit_notes: list[list[typing.Any]]`
    :   Details of credit notes issued

    `line_item_discounts: list[list[typing.Any]]`
    :   Details of line item discounts

    `line_item_taxes: list[list[typing.Any]]`
    :   Tax details applied to each line item in the invoice

    `line_item_tiers: list[list[typing.Any]]`
    :   Tiers information for each line item in the invoice

    `line_items: list[list[typing.Any]]`
    :   Details of individual line items in the invoice

    `linked_orders: list[list[typing.Any]]`
    :   Details of linked orders to the invoice

    `linked_payments: list[list[typing.Any]]`
    :   Details of linked payments

    `linked_taxes_withheld: list[list[typing.Any]]`
    :   Details of linked taxes withheld on the invoice

    `local_currency_code: list[str]`
    :   Local currency code of the invoice

    `local_currency_exchange_rate: list[float]`
    :   Exchange rate for local currency conversion

    `net_term_days: list[int]`
    :   Net term days for payment

    `new_sales_amount: list[int]`
    :   New sales amount in the invoice

    `next_retry_at: list[int]`
    :   Date of the next payment retry

    `notes: list[list[typing.Any]]`
    :   Notes associated with the invoice

    `object_: list[str]`
    :   Type of object

    `paid_at: list[int]`
    :   Date when the invoice was paid

    `payment_owner: list[str]`
    :   Owner of the payment

    `po_number: list[str]`
    :   Purchase order number

    `price_type: list[str]`
    :   Type of pricing

    `recurring: list[bool]`
    :   Flag indicating if it's a recurring invoice

    `resource_version: list[int]`
    :   Resource version of the invoice

    `round_off_amount: list[int]`
    :   Amount rounded off

    `shipping_address: list[dict[str, typing.Any]]`
    :   Details of the shipping address associated with the invoice

    `statement_descriptor: list[dict[str, typing.Any]]`
    :   Descriptor for the statement

    `status: list[str]`
    :   Status of the invoice

    `sub_total: list[int]`
    :   Subtotal amount

    `sub_total_in_local_currency: list[int]`
    :   Subtotal amount in local currency

    `subscription_id: list[str]`
    :   ID of the subscription associated

    `tax: list[int]`
    :   Total tax amount

    `tax_category: list[str]`
    :   Tax category

    `taxes: list[list[typing.Any]]`
    :   Details of taxes applied

    `term_finalized: list[bool]`
    :   Flag indicating if the term is finalized

    `total: list[int]`
    :   Total amount of the invoice

    `total_in_local_currency: list[int]`
    :   Total amount in local currency

    `updated_at: list[int]`
    :   Date of last update

    `vat_number: list[str]`
    :   VAT number

    `vat_number_prefix: list[str]`
    :   Prefix for the VAT number

    `void_reason_code: list[str]`
    :   Reason code for voiding the invoice

    `voided_at: list[int]`
    :   Date when the invoice was voided

    `write_off_amount: list[int]`
    :   Amount written off

<a id="InvoiceKeywordCondition"></a>

`InvoiceKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.chargebee.types.InvoiceStringFilter`
    :   The type of the None singleton.

<a id="InvoiceLikeCondition"></a>

`InvoiceLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.chargebee.types.InvoiceStringFilter`
    :   The type of the None singleton.

<a id="InvoiceListParams"></a>

`InvoiceListParams(*args, **kwargs)`
:   Parameters for invoice.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

<a id="InvoiceLtCondition"></a>

`InvoiceLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.chargebee.types.InvoiceSearchFilter`
    :   The type of the None singleton.

<a id="InvoiceLteCondition"></a>

`InvoiceLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.chargebee.types.InvoiceSearchFilter`
    :   The type of the None singleton.

<a id="InvoiceNeqCondition"></a>

`InvoiceNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.chargebee.types.InvoiceSearchFilter`
    :   The type of the None singleton.

<a id="InvoiceNotCondition"></a>

`InvoiceNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.chargebee.types.InvoiceEqCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceGtCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceGteCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceLtCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceLteCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceInCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceNotCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceAndCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceOrCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceAnyCondition`
    :   The type of the None singleton.

<a id="InvoiceOrCondition"></a>

`InvoiceOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.chargebee.types.InvoiceEqCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceGtCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceGteCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceLtCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceLteCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceInCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceNotCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceAndCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceOrCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceAnyCondition]`
    :   The type of the None singleton.

<a id="InvoiceSearchFilter"></a>

`InvoiceSearchFilter(*args, **kwargs)`
:   Available fields for filtering invoice search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="InvoiceSearchQuery"></a>

`InvoiceSearchQuery(*args, **kwargs)`
:   Search query for invoice entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.chargebee.types.InvoiceEqCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceGtCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceGteCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceLtCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceLteCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceInCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceNotCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceAndCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceOrCondition | airbyte_agent_sdk.connectors.chargebee.types.InvoiceAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.chargebee.types.InvoiceSortFilter]`
    :   The type of the None singleton.

<a id="InvoiceSortFilter"></a>

`InvoiceSortFilter(*args, **kwargs)`
:   Available fields for sorting invoice search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adjustment_credit_notes: Literal['asc', 'desc']`
    :   Details of adjustment credit notes applied to the invoice

    `amount_adjusted: Literal['asc', 'desc']`
    :   Total amount adjusted in the invoice

    `amount_due: Literal['asc', 'desc']`
    :   Amount due for payment

    `amount_paid: Literal['asc', 'desc']`
    :   Amount already paid

    `amount_to_collect: Literal['asc', 'desc']`
    :   Amount yet to be collected

    `applied_credits: Literal['asc', 'desc']`
    :   Details of credits applied to the invoice

    `base_currency_code: Literal['asc', 'desc']`
    :   Currency code used as base for the invoice

    `billing_address: Literal['asc', 'desc']`
    :   Details of the billing address associated with the invoice

    `business_entity_id: Literal['asc', 'desc']`
    :   ID of the business entity

    `channel: Literal['asc', 'desc']`
    :   Channel through which the invoice was generated

    `credits_applied: Literal['asc', 'desc']`
    :   Total credits applied to the invoice

    `currency_code: Literal['asc', 'desc']`
    :   Currency code of the invoice

    `custom_fields: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `customer_id: Literal['asc', 'desc']`
    :   ID of the customer

    `date: Literal['asc', 'desc']`
    :   Date of the invoice

    `deleted: Literal['asc', 'desc']`
    :   Flag indicating if the invoice is deleted

    `discounts: Literal['asc', 'desc']`
    :   Discount details applied to the invoice

    `due_date: Literal['asc', 'desc']`
    :   Due date for payment

    `dunning_attempts: Literal['asc', 'desc']`
    :   Details of dunning attempts made

    `dunning_status: Literal['asc', 'desc']`
    :   Status of dunning for the invoice

    `einvoice: Literal['asc', 'desc']`
    :   Details of electronic invoice

    `exchange_rate: Literal['asc', 'desc']`
    :   Exchange rate used for currency conversion

    `expected_payment_date: Literal['asc', 'desc']`
    :   Expected date of payment

    `first_invoice: Literal['asc', 'desc']`
    :   Flag indicating whether it's the first invoice

    `generated_at: Literal['asc', 'desc']`
    :   Date when the invoice was generated

    `has_advance_charges: Literal['asc', 'desc']`
    :   Flag indicating if there are advance charges

    `id: Literal['asc', 'desc']`
    :   Unique ID of the invoice

    `is_digital: Literal['asc', 'desc']`
    :   Flag indicating if the invoice is digital

    `is_gifted: Literal['asc', 'desc']`
    :   Flag indicating if the invoice is gifted

    `issued_credit_notes: Literal['asc', 'desc']`
    :   Details of credit notes issued

    `line_item_discounts: Literal['asc', 'desc']`
    :   Details of line item discounts

    `line_item_taxes: Literal['asc', 'desc']`
    :   Tax details applied to each line item in the invoice

    `line_item_tiers: Literal['asc', 'desc']`
    :   Tiers information for each line item in the invoice

    `line_items: Literal['asc', 'desc']`
    :   Details of individual line items in the invoice

    `linked_orders: Literal['asc', 'desc']`
    :   Details of linked orders to the invoice

    `linked_payments: Literal['asc', 'desc']`
    :   Details of linked payments

    `linked_taxes_withheld: Literal['asc', 'desc']`
    :   Details of linked taxes withheld on the invoice

    `local_currency_code: Literal['asc', 'desc']`
    :   Local currency code of the invoice

    `local_currency_exchange_rate: Literal['asc', 'desc']`
    :   Exchange rate for local currency conversion

    `net_term_days: Literal['asc', 'desc']`
    :   Net term days for payment

    `new_sales_amount: Literal['asc', 'desc']`
    :   New sales amount in the invoice

    `next_retry_at: Literal['asc', 'desc']`
    :   Date of the next payment retry

    `notes: Literal['asc', 'desc']`
    :   Notes associated with the invoice

    `object_: Literal['asc', 'desc']`
    :   Type of object

    `paid_at: Literal['asc', 'desc']`
    :   Date when the invoice was paid

    `payment_owner: Literal['asc', 'desc']`
    :   Owner of the payment

    `po_number: Literal['asc', 'desc']`
    :   Purchase order number

    `price_type: Literal['asc', 'desc']`
    :   Type of pricing

    `recurring: Literal['asc', 'desc']`
    :   Flag indicating if it's a recurring invoice

    `resource_version: Literal['asc', 'desc']`
    :   Resource version of the invoice

    `round_off_amount: Literal['asc', 'desc']`
    :   Amount rounded off

    `shipping_address: Literal['asc', 'desc']`
    :   Details of the shipping address associated with the invoice

    `statement_descriptor: Literal['asc', 'desc']`
    :   Descriptor for the statement

    `status: Literal['asc', 'desc']`
    :   Status of the invoice

    `sub_total: Literal['asc', 'desc']`
    :   Subtotal amount

    `sub_total_in_local_currency: Literal['asc', 'desc']`
    :   Subtotal amount in local currency

    `subscription_id: Literal['asc', 'desc']`
    :   ID of the subscription associated

    `tax: Literal['asc', 'desc']`
    :   Total tax amount

    `tax_category: Literal['asc', 'desc']`
    :   Tax category

    `taxes: Literal['asc', 'desc']`
    :   Details of taxes applied

    `term_finalized: Literal['asc', 'desc']`
    :   Flag indicating if the term is finalized

    `total: Literal['asc', 'desc']`
    :   Total amount of the invoice

    `total_in_local_currency: Literal['asc', 'desc']`
    :   Total amount in local currency

    `updated_at: Literal['asc', 'desc']`
    :   Date of last update

    `vat_number: Literal['asc', 'desc']`
    :   VAT number

    `vat_number_prefix: Literal['asc', 'desc']`
    :   Prefix for the VAT number

    `void_reason_code: Literal['asc', 'desc']`
    :   Reason code for voiding the invoice

    `voided_at: Literal['asc', 'desc']`
    :   Date when the invoice was voided

    `write_off_amount: Literal['asc', 'desc']`
    :   Amount written off

<a id="InvoiceStringFilter"></a>

`InvoiceStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adjustment_credit_notes: str`
    :   Details of adjustment credit notes applied to the invoice

    `amount_adjusted: str`
    :   Total amount adjusted in the invoice

    `amount_due: str`
    :   Amount due for payment

    `amount_paid: str`
    :   Amount already paid

    `amount_to_collect: str`
    :   Amount yet to be collected

    `applied_credits: str`
    :   Details of credits applied to the invoice

    `base_currency_code: str`
    :   Currency code used as base for the invoice

    `billing_address: str`
    :   Details of the billing address associated with the invoice

    `business_entity_id: str`
    :   ID of the business entity

    `channel: str`
    :   Channel through which the invoice was generated

    `credits_applied: str`
    :   Total credits applied to the invoice

    `currency_code: str`
    :   Currency code of the invoice

    `custom_fields: str`
    :   The type of the None singleton.

    `customer_id: str`
    :   ID of the customer

    `date: str`
    :   Date of the invoice

    `deleted: str`
    :   Flag indicating if the invoice is deleted

    `discounts: str`
    :   Discount details applied to the invoice

    `due_date: str`
    :   Due date for payment

    `dunning_attempts: str`
    :   Details of dunning attempts made

    `dunning_status: str`
    :   Status of dunning for the invoice

    `einvoice: str`
    :   Details of electronic invoice

    `exchange_rate: str`
    :   Exchange rate used for currency conversion

    `expected_payment_date: str`
    :   Expected date of payment

    `first_invoice: str`
    :   Flag indicating whether it's the first invoice

    `generated_at: str`
    :   Date when the invoice was generated

    `has_advance_charges: str`
    :   Flag indicating if there are advance charges

    `id: str`
    :   Unique ID of the invoice

    `is_digital: str`
    :   Flag indicating if the invoice is digital

    `is_gifted: str`
    :   Flag indicating if the invoice is gifted

    `issued_credit_notes: str`
    :   Details of credit notes issued

    `line_item_discounts: str`
    :   Details of line item discounts

    `line_item_taxes: str`
    :   Tax details applied to each line item in the invoice

    `line_item_tiers: str`
    :   Tiers information for each line item in the invoice

    `line_items: str`
    :   Details of individual line items in the invoice

    `linked_orders: str`
    :   Details of linked orders to the invoice

    `linked_payments: str`
    :   Details of linked payments

    `linked_taxes_withheld: str`
    :   Details of linked taxes withheld on the invoice

    `local_currency_code: str`
    :   Local currency code of the invoice

    `local_currency_exchange_rate: str`
    :   Exchange rate for local currency conversion

    `net_term_days: str`
    :   Net term days for payment

    `new_sales_amount: str`
    :   New sales amount in the invoice

    `next_retry_at: str`
    :   Date of the next payment retry

    `notes: str`
    :   Notes associated with the invoice

    `object_: str`
    :   Type of object

    `paid_at: str`
    :   Date when the invoice was paid

    `payment_owner: str`
    :   Owner of the payment

    `po_number: str`
    :   Purchase order number

    `price_type: str`
    :   Type of pricing

    `recurring: str`
    :   Flag indicating if it's a recurring invoice

    `resource_version: str`
    :   Resource version of the invoice

    `round_off_amount: str`
    :   Amount rounded off

    `shipping_address: str`
    :   Details of the shipping address associated with the invoice

    `statement_descriptor: str`
    :   Descriptor for the statement

    `status: str`
    :   Status of the invoice

    `sub_total: str`
    :   Subtotal amount

    `sub_total_in_local_currency: str`
    :   Subtotal amount in local currency

    `subscription_id: str`
    :   ID of the subscription associated

    `tax: str`
    :   Total tax amount

    `tax_category: str`
    :   Tax category

    `taxes: str`
    :   Details of taxes applied

    `term_finalized: str`
    :   Flag indicating if the term is finalized

    `total: str`
    :   Total amount of the invoice

    `total_in_local_currency: str`
    :   Total amount in local currency

    `updated_at: str`
    :   Date of last update

    `vat_number: str`
    :   VAT number

    `vat_number_prefix: str`
    :   Prefix for the VAT number

    `void_reason_code: str`
    :   Reason code for voiding the invoice

    `voided_at: str`
    :   Date when the invoice was voided

    `write_off_amount: str`
    :   Amount written off

<a id="ItemAndCondition"></a>

`ItemAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.chargebee.types.ItemEqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemGtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemGteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemLtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemLteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemInCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemNotCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemAndCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemOrCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemAnyCondition]`
    :   The type of the None singleton.

<a id="ItemAnyCondition"></a>

`ItemAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.chargebee.types.ItemAnyValueFilter`
    :   The type of the None singleton.

<a id="ItemAnyValueFilter"></a>

`ItemAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `applicable_items: Any`
    :   Items associated with the item

    `archived_at: Any`
    :   Date and time when the item was archived

    `channel: Any`
    :   Channel the item belongs to

    `custom_fields: Any`
    :   Custom field entries for the item

    `description: Any`
    :   Description of the item

    `enabled_for_checkout: Any`
    :   Flag indicating if the item is enabled for checkout

    `enabled_in_portal: Any`
    :   Flag indicating if the item is enabled in the portal

    `external_name: Any`
    :   Name of the item in an external system

    `gift_claim_redirect_url: Any`
    :   URL to redirect for gift claim

    `id: Any`
    :   Unique identifier for the item

    `included_in_mrr: Any`
    :   Flag indicating if the item is included in Monthly Recurring Revenue

    `is_giftable: Any`
    :   Flag indicating if the item is giftable

    `is_shippable: Any`
    :   Flag indicating if the item is shippable

    `item_applicability: Any`
    :   Applicability of the item

    `item_family_id: Any`
    :   ID of the item's family

    `metadata: Any`
    :   Additional data associated with the item

    `metered: Any`
    :   Flag indicating if the item is metered

    `name: Any`
    :   Name of the item

    `object_: Any`
    :   Type of object

    `redirect_url: Any`
    :   URL to redirect for the item

    `resource_version: Any`
    :   Version of the resource

    `status: Any`
    :   Status of the item

    `type_: Any`
    :   Type of the item

    `unit: Any`
    :   Unit associated with the item

    `updated_at: Any`
    :   Date and time when the item was last updated

    `usage_calculation: Any`
    :   Calculation method used for item usage

<a id="ItemContainsCondition"></a>

`ItemContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.chargebee.types.ItemAnyValueFilter`
    :   The type of the None singleton.

<a id="ItemEqCondition"></a>

`ItemEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.chargebee.types.ItemSearchFilter`
    :   The type of the None singleton.

<a id="ItemFuzzyCondition"></a>

`ItemFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.chargebee.types.ItemStringFilter`
    :   The type of the None singleton.

<a id="ItemGetParams"></a>

`ItemGetParams(*args, **kwargs)`
:   Parameters for item.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ItemGtCondition"></a>

`ItemGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.chargebee.types.ItemSearchFilter`
    :   The type of the None singleton.

<a id="ItemGteCondition"></a>

`ItemGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.chargebee.types.ItemSearchFilter`
    :   The type of the None singleton.

<a id="ItemInCondition"></a>

`ItemInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.chargebee.types.ItemInFilter`
    :   The type of the None singleton.

<a id="ItemInFilter"></a>

`ItemInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `applicable_items: list[list[typing.Any]]`
    :   Items associated with the item

    `archived_at: list[int]`
    :   Date and time when the item was archived

    `channel: list[str]`
    :   Channel the item belongs to

    `custom_fields: list[list[typing.Any]]`
    :   Custom field entries for the item

    `description: list[str]`
    :   Description of the item

    `enabled_for_checkout: list[bool]`
    :   Flag indicating if the item is enabled for checkout

    `enabled_in_portal: list[bool]`
    :   Flag indicating if the item is enabled in the portal

    `external_name: list[str]`
    :   Name of the item in an external system

    `gift_claim_redirect_url: list[str]`
    :   URL to redirect for gift claim

    `id: list[str]`
    :   Unique identifier for the item

    `included_in_mrr: list[bool]`
    :   Flag indicating if the item is included in Monthly Recurring Revenue

    `is_giftable: list[bool]`
    :   Flag indicating if the item is giftable

    `is_shippable: list[bool]`
    :   Flag indicating if the item is shippable

    `item_applicability: list[str]`
    :   Applicability of the item

    `item_family_id: list[str]`
    :   ID of the item's family

    `metadata: list[dict[str, typing.Any]]`
    :   Additional data associated with the item

    `metered: list[bool]`
    :   Flag indicating if the item is metered

    `name: list[str]`
    :   Name of the item

    `object_: list[str]`
    :   Type of object

    `redirect_url: list[str]`
    :   URL to redirect for the item

    `resource_version: list[int]`
    :   Version of the resource

    `status: list[str]`
    :   Status of the item

    `type_: list[str]`
    :   Type of the item

    `unit: list[str]`
    :   Unit associated with the item

    `updated_at: list[int]`
    :   Date and time when the item was last updated

    `usage_calculation: list[str]`
    :   Calculation method used for item usage

<a id="ItemKeywordCondition"></a>

`ItemKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.chargebee.types.ItemStringFilter`
    :   The type of the None singleton.

<a id="ItemLikeCondition"></a>

`ItemLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.chargebee.types.ItemStringFilter`
    :   The type of the None singleton.

<a id="ItemListParams"></a>

`ItemListParams(*args, **kwargs)`
:   Parameters for item.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

<a id="ItemLtCondition"></a>

`ItemLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.chargebee.types.ItemSearchFilter`
    :   The type of the None singleton.

<a id="ItemLteCondition"></a>

`ItemLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.chargebee.types.ItemSearchFilter`
    :   The type of the None singleton.

<a id="ItemNeqCondition"></a>

`ItemNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.chargebee.types.ItemSearchFilter`
    :   The type of the None singleton.

<a id="ItemNotCondition"></a>

`ItemNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.chargebee.types.ItemEqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemGtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemGteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemLtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemLteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemInCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemNotCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemAndCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemOrCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemAnyCondition`
    :   The type of the None singleton.

<a id="ItemOrCondition"></a>

`ItemOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.chargebee.types.ItemEqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemGtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemGteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemLtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemLteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemInCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemNotCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemAndCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemOrCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemAnyCondition]`
    :   The type of the None singleton.

<a id="ItemPriceAndCondition"></a>

`ItemPriceAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.chargebee.types.ItemPriceEqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceGtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceGteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceLtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceLteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceInCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceNotCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceAndCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceOrCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceAnyCondition]`
    :   The type of the None singleton.

<a id="ItemPriceAnyCondition"></a>

`ItemPriceAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.chargebee.types.ItemPriceAnyValueFilter`
    :   The type of the None singleton.

<a id="ItemPriceAnyValueFilter"></a>

`ItemPriceAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accounting_detail: Any`
    :   Details related to accounting such as cost, revenue, expenses, etc.

    `archived_at: Any`
    :   Date and time when the item was archived.

    `billing_cycles: Any`
    :   Number of billing cycles for the item.

    `channel: Any`
    :   The channel through which the item is sold.

    `created_at: Any`
    :   Date and time when the item was created.

    `currency_code: Any`
    :   The currency code used for pricing the item.

    `custom_fields: Any`
    :   Custom field entries for the item price.

    `description: Any`
    :   Description of the item.

    `external_name: Any`
    :   External name of the item.

    `free_quantity: Any`
    :   Free quantity allowed for the item.

    `free_quantity_in_decimal: Any`
    :   Free quantity allowed represented in decimal format.

    `id: Any`
    :   Unique identifier for the item price.

    `invoice_notes: Any`
    :   Notes to be included in the invoice for the item.

    `is_taxable: Any`
    :   Flag indicating whether the item is taxable.

    `item_family_id: Any`
    :   Identifier for the item family to which the item belongs.

    `item_id: Any`
    :   Unique identifier for the parent item.

    `item_type: Any`
    :   Type of the item (e.g., product, service).

    `metadata: Any`
    :   Additional metadata associated with the item.

    `name: Any`
    :   Name of the item price.

    `object_: Any`
    :   Object type representing the item price.

    `period: Any`
    :   Duration of the item's billing period.

    `period_unit: Any`
    :   Unit of measurement for the billing period duration.

    `price: Any`
    :   Price of the item.

    `price_in_decimal: Any`
    :   Price of the item represented in decimal format.

    `pricing_model: Any`
    :   The pricing model used for the item (e.g., flat fee, usage-based).

    `resource_version: Any`
    :   Version of the item price resource.

    `shipping_period: Any`
    :   Duration of the item's shipping period.

    `shipping_period_unit: Any`
    :   Unit of measurement for the shipping period duration.

    `show_description_in_invoices: Any`
    :   Flag indicating whether to show the description in invoices.

    `show_description_in_quotes: Any`
    :   Flag indicating whether to show the description in quotes.

    `status: Any`
    :   Current status of the item price (e.g., active, inactive).

    `tax_detail: Any`
    :   Information about taxes associated with the item price.

    `tiers: Any`
    :   Different pricing tiers for the item.

    `trial_end_action: Any`
    :   Action to be taken at the end of the trial period.

    `trial_period: Any`
    :   Duration of the trial period.

    `trial_period_unit: Any`
    :   Unit of measurement for the trial period duration.

    `updated_at: Any`
    :   Date and time when the item price was last updated.

<a id="ItemPriceContainsCondition"></a>

`ItemPriceContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.chargebee.types.ItemPriceAnyValueFilter`
    :   The type of the None singleton.

<a id="ItemPriceEqCondition"></a>

`ItemPriceEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.chargebee.types.ItemPriceSearchFilter`
    :   The type of the None singleton.

<a id="ItemPriceFuzzyCondition"></a>

`ItemPriceFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.chargebee.types.ItemPriceStringFilter`
    :   The type of the None singleton.

<a id="ItemPriceGetParams"></a>

`ItemPriceGetParams(*args, **kwargs)`
:   Parameters for item_price.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ItemPriceGtCondition"></a>

`ItemPriceGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.chargebee.types.ItemPriceSearchFilter`
    :   The type of the None singleton.

<a id="ItemPriceGteCondition"></a>

`ItemPriceGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.chargebee.types.ItemPriceSearchFilter`
    :   The type of the None singleton.

<a id="ItemPriceInCondition"></a>

`ItemPriceInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.chargebee.types.ItemPriceInFilter`
    :   The type of the None singleton.

<a id="ItemPriceInFilter"></a>

`ItemPriceInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accounting_detail: list[dict[str, typing.Any]]`
    :   Details related to accounting such as cost, revenue, expenses, etc.

    `archived_at: list[int]`
    :   Date and time when the item was archived.

    `billing_cycles: list[int]`
    :   Number of billing cycles for the item.

    `channel: list[str]`
    :   The channel through which the item is sold.

    `created_at: list[int]`
    :   Date and time when the item was created.

    `currency_code: list[str]`
    :   The currency code used for pricing the item.

    `custom_fields: list[list[typing.Any]]`
    :   Custom field entries for the item price.

    `description: list[str]`
    :   Description of the item.

    `external_name: list[str]`
    :   External name of the item.

    `free_quantity: list[int]`
    :   Free quantity allowed for the item.

    `free_quantity_in_decimal: list[str]`
    :   Free quantity allowed represented in decimal format.

    `id: list[str]`
    :   Unique identifier for the item price.

    `invoice_notes: list[str]`
    :   Notes to be included in the invoice for the item.

    `is_taxable: list[bool]`
    :   Flag indicating whether the item is taxable.

    `item_family_id: list[str]`
    :   Identifier for the item family to which the item belongs.

    `item_id: list[str]`
    :   Unique identifier for the parent item.

    `item_type: list[str]`
    :   Type of the item (e.g., product, service).

    `metadata: list[dict[str, typing.Any]]`
    :   Additional metadata associated with the item.

    `name: list[str]`
    :   Name of the item price.

    `object_: list[str]`
    :   Object type representing the item price.

    `period: list[int]`
    :   Duration of the item's billing period.

    `period_unit: list[str]`
    :   Unit of measurement for the billing period duration.

    `price: list[int]`
    :   Price of the item.

    `price_in_decimal: list[str]`
    :   Price of the item represented in decimal format.

    `pricing_model: list[str]`
    :   The pricing model used for the item (e.g., flat fee, usage-based).

    `resource_version: list[int]`
    :   Version of the item price resource.

    `shipping_period: list[int]`
    :   Duration of the item's shipping period.

    `shipping_period_unit: list[str]`
    :   Unit of measurement for the shipping period duration.

    `show_description_in_invoices: list[bool]`
    :   Flag indicating whether to show the description in invoices.

    `show_description_in_quotes: list[bool]`
    :   Flag indicating whether to show the description in quotes.

    `status: list[str]`
    :   Current status of the item price (e.g., active, inactive).

    `tax_detail: list[dict[str, typing.Any]]`
    :   Information about taxes associated with the item price.

    `tiers: list[list[typing.Any]]`
    :   Different pricing tiers for the item.

    `trial_end_action: list[str]`
    :   Action to be taken at the end of the trial period.

    `trial_period: list[int]`
    :   Duration of the trial period.

    `trial_period_unit: list[str]`
    :   Unit of measurement for the trial period duration.

    `updated_at: list[int]`
    :   Date and time when the item price was last updated.

<a id="ItemPriceKeywordCondition"></a>

`ItemPriceKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.chargebee.types.ItemPriceStringFilter`
    :   The type of the None singleton.

<a id="ItemPriceLikeCondition"></a>

`ItemPriceLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.chargebee.types.ItemPriceStringFilter`
    :   The type of the None singleton.

<a id="ItemPriceListParams"></a>

`ItemPriceListParams(*args, **kwargs)`
:   Parameters for item_price.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

<a id="ItemPriceLtCondition"></a>

`ItemPriceLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.chargebee.types.ItemPriceSearchFilter`
    :   The type of the None singleton.

<a id="ItemPriceLteCondition"></a>

`ItemPriceLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.chargebee.types.ItemPriceSearchFilter`
    :   The type of the None singleton.

<a id="ItemPriceNeqCondition"></a>

`ItemPriceNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.chargebee.types.ItemPriceSearchFilter`
    :   The type of the None singleton.

<a id="ItemPriceNotCondition"></a>

`ItemPriceNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.chargebee.types.ItemPriceEqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceGtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceGteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceLtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceLteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceInCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceNotCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceAndCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceOrCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceAnyCondition`
    :   The type of the None singleton.

<a id="ItemPriceOrCondition"></a>

`ItemPriceOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.chargebee.types.ItemPriceEqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceGtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceGteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceLtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceLteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceInCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceNotCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceAndCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceOrCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceAnyCondition]`
    :   The type of the None singleton.

<a id="ItemPriceSearchFilter"></a>

`ItemPriceSearchFilter(*args, **kwargs)`
:   Available fields for filtering item_price search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="ItemPriceSearchQuery"></a>

`ItemPriceSearchQuery(*args, **kwargs)`
:   Search query for item_price entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.chargebee.types.ItemPriceEqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceGtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceGteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceLtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceLteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceInCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceNotCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceAndCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceOrCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemPriceAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.chargebee.types.ItemPriceSortFilter]`
    :   The type of the None singleton.

<a id="ItemPriceSortFilter"></a>

`ItemPriceSortFilter(*args, **kwargs)`
:   Available fields for sorting item_price search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accounting_detail: Literal['asc', 'desc']`
    :   Details related to accounting such as cost, revenue, expenses, etc.

    `archived_at: Literal['asc', 'desc']`
    :   Date and time when the item was archived.

    `billing_cycles: Literal['asc', 'desc']`
    :   Number of billing cycles for the item.

    `channel: Literal['asc', 'desc']`
    :   The channel through which the item is sold.

    `created_at: Literal['asc', 'desc']`
    :   Date and time when the item was created.

    `currency_code: Literal['asc', 'desc']`
    :   The currency code used for pricing the item.

    `custom_fields: Literal['asc', 'desc']`
    :   Custom field entries for the item price.

    `description: Literal['asc', 'desc']`
    :   Description of the item.

    `external_name: Literal['asc', 'desc']`
    :   External name of the item.

    `free_quantity: Literal['asc', 'desc']`
    :   Free quantity allowed for the item.

    `free_quantity_in_decimal: Literal['asc', 'desc']`
    :   Free quantity allowed represented in decimal format.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the item price.

    `invoice_notes: Literal['asc', 'desc']`
    :   Notes to be included in the invoice for the item.

    `is_taxable: Literal['asc', 'desc']`
    :   Flag indicating whether the item is taxable.

    `item_family_id: Literal['asc', 'desc']`
    :   Identifier for the item family to which the item belongs.

    `item_id: Literal['asc', 'desc']`
    :   Unique identifier for the parent item.

    `item_type: Literal['asc', 'desc']`
    :   Type of the item (e.g., product, service).

    `metadata: Literal['asc', 'desc']`
    :   Additional metadata associated with the item.

    `name: Literal['asc', 'desc']`
    :   Name of the item price.

    `object_: Literal['asc', 'desc']`
    :   Object type representing the item price.

    `period: Literal['asc', 'desc']`
    :   Duration of the item's billing period.

    `period_unit: Literal['asc', 'desc']`
    :   Unit of measurement for the billing period duration.

    `price: Literal['asc', 'desc']`
    :   Price of the item.

    `price_in_decimal: Literal['asc', 'desc']`
    :   Price of the item represented in decimal format.

    `pricing_model: Literal['asc', 'desc']`
    :   The pricing model used for the item (e.g., flat fee, usage-based).

    `resource_version: Literal['asc', 'desc']`
    :   Version of the item price resource.

    `shipping_period: Literal['asc', 'desc']`
    :   Duration of the item's shipping period.

    `shipping_period_unit: Literal['asc', 'desc']`
    :   Unit of measurement for the shipping period duration.

    `show_description_in_invoices: Literal['asc', 'desc']`
    :   Flag indicating whether to show the description in invoices.

    `show_description_in_quotes: Literal['asc', 'desc']`
    :   Flag indicating whether to show the description in quotes.

    `status: Literal['asc', 'desc']`
    :   Current status of the item price (e.g., active, inactive).

    `tax_detail: Literal['asc', 'desc']`
    :   Information about taxes associated with the item price.

    `tiers: Literal['asc', 'desc']`
    :   Different pricing tiers for the item.

    `trial_end_action: Literal['asc', 'desc']`
    :   Action to be taken at the end of the trial period.

    `trial_period: Literal['asc', 'desc']`
    :   Duration of the trial period.

    `trial_period_unit: Literal['asc', 'desc']`
    :   Unit of measurement for the trial period duration.

    `updated_at: Literal['asc', 'desc']`
    :   Date and time when the item price was last updated.

<a id="ItemPriceStringFilter"></a>

`ItemPriceStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accounting_detail: str`
    :   Details related to accounting such as cost, revenue, expenses, etc.

    `archived_at: str`
    :   Date and time when the item was archived.

    `billing_cycles: str`
    :   Number of billing cycles for the item.

    `channel: str`
    :   The channel through which the item is sold.

    `created_at: str`
    :   Date and time when the item was created.

    `currency_code: str`
    :   The currency code used for pricing the item.

    `custom_fields: str`
    :   Custom field entries for the item price.

    `description: str`
    :   Description of the item.

    `external_name: str`
    :   External name of the item.

    `free_quantity: str`
    :   Free quantity allowed for the item.

    `free_quantity_in_decimal: str`
    :   Free quantity allowed represented in decimal format.

    `id: str`
    :   Unique identifier for the item price.

    `invoice_notes: str`
    :   Notes to be included in the invoice for the item.

    `is_taxable: str`
    :   Flag indicating whether the item is taxable.

    `item_family_id: str`
    :   Identifier for the item family to which the item belongs.

    `item_id: str`
    :   Unique identifier for the parent item.

    `item_type: str`
    :   Type of the item (e.g., product, service).

    `metadata: str`
    :   Additional metadata associated with the item.

    `name: str`
    :   Name of the item price.

    `object_: str`
    :   Object type representing the item price.

    `period: str`
    :   Duration of the item's billing period.

    `period_unit: str`
    :   Unit of measurement for the billing period duration.

    `price: str`
    :   Price of the item.

    `price_in_decimal: str`
    :   Price of the item represented in decimal format.

    `pricing_model: str`
    :   The pricing model used for the item (e.g., flat fee, usage-based).

    `resource_version: str`
    :   Version of the item price resource.

    `shipping_period: str`
    :   Duration of the item's shipping period.

    `shipping_period_unit: str`
    :   Unit of measurement for the shipping period duration.

    `show_description_in_invoices: str`
    :   Flag indicating whether to show the description in invoices.

    `show_description_in_quotes: str`
    :   Flag indicating whether to show the description in quotes.

    `status: str`
    :   Current status of the item price (e.g., active, inactive).

    `tax_detail: str`
    :   Information about taxes associated with the item price.

    `tiers: str`
    :   Different pricing tiers for the item.

    `trial_end_action: str`
    :   Action to be taken at the end of the trial period.

    `trial_period: str`
    :   Duration of the trial period.

    `trial_period_unit: str`
    :   Unit of measurement for the trial period duration.

    `updated_at: str`
    :   Date and time when the item price was last updated.

<a id="ItemSearchFilter"></a>

`ItemSearchFilter(*args, **kwargs)`
:   Available fields for filtering item search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="ItemSearchQuery"></a>

`ItemSearchQuery(*args, **kwargs)`
:   Search query for item entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.chargebee.types.ItemEqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemGtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemGteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemLtCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemLteCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemInCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemNotCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemAndCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemOrCondition | airbyte_agent_sdk.connectors.chargebee.types.ItemAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.chargebee.types.ItemSortFilter]`
    :   The type of the None singleton.

<a id="ItemSortFilter"></a>

`ItemSortFilter(*args, **kwargs)`
:   Available fields for sorting item search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `applicable_items: Literal['asc', 'desc']`
    :   Items associated with the item

    `archived_at: Literal['asc', 'desc']`
    :   Date and time when the item was archived

    `channel: Literal['asc', 'desc']`
    :   Channel the item belongs to

    `custom_fields: Literal['asc', 'desc']`
    :   Custom field entries for the item

    `description: Literal['asc', 'desc']`
    :   Description of the item

    `enabled_for_checkout: Literal['asc', 'desc']`
    :   Flag indicating if the item is enabled for checkout

    `enabled_in_portal: Literal['asc', 'desc']`
    :   Flag indicating if the item is enabled in the portal

    `external_name: Literal['asc', 'desc']`
    :   Name of the item in an external system

    `gift_claim_redirect_url: Literal['asc', 'desc']`
    :   URL to redirect for gift claim

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the item

    `included_in_mrr: Literal['asc', 'desc']`
    :   Flag indicating if the item is included in Monthly Recurring Revenue

    `is_giftable: Literal['asc', 'desc']`
    :   Flag indicating if the item is giftable

    `is_shippable: Literal['asc', 'desc']`
    :   Flag indicating if the item is shippable

    `item_applicability: Literal['asc', 'desc']`
    :   Applicability of the item

    `item_family_id: Literal['asc', 'desc']`
    :   ID of the item's family

    `metadata: Literal['asc', 'desc']`
    :   Additional data associated with the item

    `metered: Literal['asc', 'desc']`
    :   Flag indicating if the item is metered

    `name: Literal['asc', 'desc']`
    :   Name of the item

    `object_: Literal['asc', 'desc']`
    :   Type of object

    `redirect_url: Literal['asc', 'desc']`
    :   URL to redirect for the item

    `resource_version: Literal['asc', 'desc']`
    :   Version of the resource

    `status: Literal['asc', 'desc']`
    :   Status of the item

    `type_: Literal['asc', 'desc']`
    :   Type of the item

    `unit: Literal['asc', 'desc']`
    :   Unit associated with the item

    `updated_at: Literal['asc', 'desc']`
    :   Date and time when the item was last updated

    `usage_calculation: Literal['asc', 'desc']`
    :   Calculation method used for item usage

<a id="ItemStringFilter"></a>

`ItemStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `applicable_items: str`
    :   Items associated with the item

    `archived_at: str`
    :   Date and time when the item was archived

    `channel: str`
    :   Channel the item belongs to

    `custom_fields: str`
    :   Custom field entries for the item

    `description: str`
    :   Description of the item

    `enabled_for_checkout: str`
    :   Flag indicating if the item is enabled for checkout

    `enabled_in_portal: str`
    :   Flag indicating if the item is enabled in the portal

    `external_name: str`
    :   Name of the item in an external system

    `gift_claim_redirect_url: str`
    :   URL to redirect for gift claim

    `id: str`
    :   Unique identifier for the item

    `included_in_mrr: str`
    :   Flag indicating if the item is included in Monthly Recurring Revenue

    `is_giftable: str`
    :   Flag indicating if the item is giftable

    `is_shippable: str`
    :   Flag indicating if the item is shippable

    `item_applicability: str`
    :   Applicability of the item

    `item_family_id: str`
    :   ID of the item's family

    `metadata: str`
    :   Additional data associated with the item

    `metered: str`
    :   Flag indicating if the item is metered

    `name: str`
    :   Name of the item

    `object_: str`
    :   Type of object

    `redirect_url: str`
    :   URL to redirect for the item

    `resource_version: str`
    :   Version of the resource

    `status: str`
    :   Status of the item

    `type_: str`
    :   Type of the item

    `unit: str`
    :   Unit associated with the item

    `updated_at: str`
    :   Date and time when the item was last updated

    `usage_calculation: str`
    :   Calculation method used for item usage

<a id="OrderAndCondition"></a>

`OrderAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.chargebee.types.OrderEqCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderGtCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderGteCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderLtCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderLteCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderInCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderNotCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderAndCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderOrCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderAnyCondition]`
    :   The type of the None singleton.

<a id="OrderAnyCondition"></a>

`OrderAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.chargebee.types.OrderAnyValueFilter`
    :   The type of the None singleton.

<a id="OrderAnyValueFilter"></a>

`OrderAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount_adjusted: Any`
    :   Adjusted amount for the order.

    `amount_paid: Any`
    :   Amount paid for the order.

    `base_currency_code: Any`
    :   The base currency code used for the order.

    `batch_id: Any`
    :   Unique identifier for the batch the order belongs to.

    `billing_address: Any`
    :   The billing address associated with the order

    `business_entity_id: Any`
    :   Identifier for the business entity associated with the order.

    `cancellation_reason: Any`
    :   Reason for order cancellation.

    `cancelled_at: Any`
    :   Timestamp when the order was cancelled.

    `created_at: Any`
    :   Timestamp when the order was created.

    `created_by: Any`
    :   User or system that created the order.

    `currency_code: Any`
    :   Currency code used for the order.

    `custom_fields: Any`
    :   The type of the None singleton.

    `customer_id: Any`
    :   Identifier for the customer placing the order.

    `deleted: Any`
    :   Flag indicating if the order has been deleted.

    `delivered_at: Any`
    :   Timestamp when the order was delivered.

    `discount: Any`
    :   Discount amount applied to the order.

    `document_number: Any`
    :   Unique document number associated with the order.

    `exchange_rate: Any`
    :   Rate used for currency exchange in the order.

    `fulfillment_status: Any`
    :   Status of fulfillment for the order.

    `gift_id: Any`
    :   Identifier for any gift associated with the order.

    `gift_note: Any`
    :   Note attached to any gift in the order.

    `id: Any`
    :   Unique identifier for the order.

    `invoice_id: Any`
    :   Identifier for the invoice associated with the order.

    `invoice_round_off_amount: Any`
    :   Round-off amount applied to the invoice.

    `is_gifted: Any`
    :   Flag indicating if the order is a gift.

    `is_resent: Any`
    :   Flag indicating if the order has been resent.

    `line_item_discounts: Any`
    :   Discounts applied to individual line items

    `line_item_taxes: Any`
    :   Taxes applied to individual line items

    `linked_credit_notes: Any`
    :   Credit notes linked to the order

    `note: Any`
    :   Additional notes or comments for the order.

    `object_: Any`
    :   Type of object representing an order in the system.

    `order_date: Any`
    :   Date when the order was created.

    `order_line_items: Any`
    :   List of line items in the order

    `order_type: Any`
    :   Type of order such as purchase order or sales order.

    `original_order_id: Any`
    :   Identifier for the original order if this is a modified order.

    `paid_on: Any`
    :   Timestamp when the order was paid for.

    `payment_status: Any`
    :   Status of payment for the order.

    `price_type: Any`
    :   Type of pricing used for the order.

    `reference_id: Any`
    :   Reference identifier for the order.

    `refundable_credits: Any`
    :   Credits that can be refunded for the whole order.

    `refundable_credits_issued: Any`
    :   Credits already issued for refund for the whole order.

    `resend_reason: Any`
    :   Reason for resending the order.

    `resent_orders: Any`
    :   Orders that were resent to the customer

    `resent_status: Any`
    :   Status of the resent order.

    `resource_version: Any`
    :   Version of the resource or order data.

    `rounding_adjustement: Any`
    :   Adjustment made for rounding off the order amount.

    `shipment_carrier: Any`
    :   Carrier for shipping the order.

    `shipped_at: Any`
    :   Timestamp when the order was shipped.

    `shipping_address: Any`
    :   The shipping address for the order

    `shipping_cut_off_date: Any`
    :   Date indicating the shipping cut-off for the order.

    `shipping_date: Any`
    :   Date when the order is scheduled for shipping.

    `status: Any`
    :   Current status of the order.

    `status_update_at: Any`
    :   Timestamp when the status of the order was last updated.

    `sub_total: Any`
    :   Sub-total amount for the order before applying taxes or discounts.

    `subscription_id: Any`
    :   Identifier for the subscription associated with the order.

    `tax: Any`
    :   Total tax amount for the order.

    `total: Any`
    :   Total amount including taxes and discounts for the order.

    `tracking_id: Any`
    :   Tracking identifier for the order shipment.

    `tracking_url: Any`
    :   URL for tracking the order shipment.

    `updated_at: Any`
    :   Timestamp when the order data was last updated.

<a id="OrderContainsCondition"></a>

`OrderContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.chargebee.types.OrderAnyValueFilter`
    :   The type of the None singleton.

<a id="OrderEqCondition"></a>

`OrderEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.chargebee.types.OrderSearchFilter`
    :   The type of the None singleton.

<a id="OrderFuzzyCondition"></a>

`OrderFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.chargebee.types.OrderStringFilter`
    :   The type of the None singleton.

<a id="OrderGetParams"></a>

`OrderGetParams(*args, **kwargs)`
:   Parameters for order.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="OrderGtCondition"></a>

`OrderGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.chargebee.types.OrderSearchFilter`
    :   The type of the None singleton.

<a id="OrderGteCondition"></a>

`OrderGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.chargebee.types.OrderSearchFilter`
    :   The type of the None singleton.

<a id="OrderInCondition"></a>

`OrderInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.chargebee.types.OrderInFilter`
    :   The type of the None singleton.

<a id="OrderInFilter"></a>

`OrderInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount_adjusted: list[int]`
    :   Adjusted amount for the order.

    `amount_paid: list[int]`
    :   Amount paid for the order.

    `base_currency_code: list[str]`
    :   The base currency code used for the order.

    `batch_id: list[str]`
    :   Unique identifier for the batch the order belongs to.

    `billing_address: list[dict[str, typing.Any]]`
    :   The billing address associated with the order

    `business_entity_id: list[str]`
    :   Identifier for the business entity associated with the order.

    `cancellation_reason: list[str]`
    :   Reason for order cancellation.

    `cancelled_at: list[int]`
    :   Timestamp when the order was cancelled.

    `created_at: list[int]`
    :   Timestamp when the order was created.

    `created_by: list[str]`
    :   User or system that created the order.

    `currency_code: list[str]`
    :   Currency code used for the order.

    `custom_fields: list[list[typing.Any]]`
    :   The type of the None singleton.

    `customer_id: list[str]`
    :   Identifier for the customer placing the order.

    `deleted: list[bool]`
    :   Flag indicating if the order has been deleted.

    `delivered_at: list[int]`
    :   Timestamp when the order was delivered.

    `discount: list[int]`
    :   Discount amount applied to the order.

    `document_number: list[str]`
    :   Unique document number associated with the order.

    `exchange_rate: list[float]`
    :   Rate used for currency exchange in the order.

    `fulfillment_status: list[str]`
    :   Status of fulfillment for the order.

    `gift_id: list[str]`
    :   Identifier for any gift associated with the order.

    `gift_note: list[str]`
    :   Note attached to any gift in the order.

    `id: list[str]`
    :   Unique identifier for the order.

    `invoice_id: list[str]`
    :   Identifier for the invoice associated with the order.

    `invoice_round_off_amount: list[int]`
    :   Round-off amount applied to the invoice.

    `is_gifted: list[bool]`
    :   Flag indicating if the order is a gift.

    `is_resent: list[bool]`
    :   Flag indicating if the order has been resent.

    `line_item_discounts: list[list[typing.Any]]`
    :   Discounts applied to individual line items

    `line_item_taxes: list[list[typing.Any]]`
    :   Taxes applied to individual line items

    `linked_credit_notes: list[list[typing.Any]]`
    :   Credit notes linked to the order

    `note: list[str]`
    :   Additional notes or comments for the order.

    `object_: list[str]`
    :   Type of object representing an order in the system.

    `order_date: list[int]`
    :   Date when the order was created.

    `order_line_items: list[list[typing.Any]]`
    :   List of line items in the order

    `order_type: list[str]`
    :   Type of order such as purchase order or sales order.

    `original_order_id: list[str]`
    :   Identifier for the original order if this is a modified order.

    `paid_on: list[int]`
    :   Timestamp when the order was paid for.

    `payment_status: list[str]`
    :   Status of payment for the order.

    `price_type: list[str]`
    :   Type of pricing used for the order.

    `reference_id: list[str]`
    :   Reference identifier for the order.

    `refundable_credits: list[int]`
    :   Credits that can be refunded for the whole order.

    `refundable_credits_issued: list[int]`
    :   Credits already issued for refund for the whole order.

    `resend_reason: list[str]`
    :   Reason for resending the order.

    `resent_orders: list[list[typing.Any]]`
    :   Orders that were resent to the customer

    `resent_status: list[str]`
    :   Status of the resent order.

    `resource_version: list[int]`
    :   Version of the resource or order data.

    `rounding_adjustement: list[int]`
    :   Adjustment made for rounding off the order amount.

    `shipment_carrier: list[str]`
    :   Carrier for shipping the order.

    `shipped_at: list[int]`
    :   Timestamp when the order was shipped.

    `shipping_address: list[dict[str, typing.Any]]`
    :   The shipping address for the order

    `shipping_cut_off_date: list[int]`
    :   Date indicating the shipping cut-off for the order.

    `shipping_date: list[int]`
    :   Date when the order is scheduled for shipping.

    `status: list[str]`
    :   Current status of the order.

    `status_update_at: list[int]`
    :   Timestamp when the status of the order was last updated.

    `sub_total: list[int]`
    :   Sub-total amount for the order before applying taxes or discounts.

    `subscription_id: list[str]`
    :   Identifier for the subscription associated with the order.

    `tax: list[int]`
    :   Total tax amount for the order.

    `total: list[int]`
    :   Total amount including taxes and discounts for the order.

    `tracking_id: list[str]`
    :   Tracking identifier for the order shipment.

    `tracking_url: list[str]`
    :   URL for tracking the order shipment.

    `updated_at: list[int]`
    :   Timestamp when the order data was last updated.

<a id="OrderKeywordCondition"></a>

`OrderKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.chargebee.types.OrderStringFilter`
    :   The type of the None singleton.

<a id="OrderLikeCondition"></a>

`OrderLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.chargebee.types.OrderStringFilter`
    :   The type of the None singleton.

<a id="OrderListParams"></a>

`OrderListParams(*args, **kwargs)`
:   Parameters for order.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

<a id="OrderLtCondition"></a>

`OrderLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.chargebee.types.OrderSearchFilter`
    :   The type of the None singleton.

<a id="OrderLteCondition"></a>

`OrderLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.chargebee.types.OrderSearchFilter`
    :   The type of the None singleton.

<a id="OrderNeqCondition"></a>

`OrderNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.chargebee.types.OrderSearchFilter`
    :   The type of the None singleton.

<a id="OrderNotCondition"></a>

`OrderNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.chargebee.types.OrderEqCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderGtCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderGteCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderLtCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderLteCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderInCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderNotCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderAndCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderOrCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderAnyCondition`
    :   The type of the None singleton.

<a id="OrderOrCondition"></a>

`OrderOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.chargebee.types.OrderEqCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderGtCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderGteCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderLtCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderLteCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderInCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderNotCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderAndCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderOrCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderAnyCondition]`
    :   The type of the None singleton.

<a id="OrderSearchFilter"></a>

`OrderSearchFilter(*args, **kwargs)`
:   Available fields for filtering order search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="OrderSearchQuery"></a>

`OrderSearchQuery(*args, **kwargs)`
:   Search query for order entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.chargebee.types.OrderEqCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderGtCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderGteCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderLtCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderLteCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderInCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderNotCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderAndCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderOrCondition | airbyte_agent_sdk.connectors.chargebee.types.OrderAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.chargebee.types.OrderSortFilter]`
    :   The type of the None singleton.

<a id="OrderSortFilter"></a>

`OrderSortFilter(*args, **kwargs)`
:   Available fields for sorting order search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount_adjusted: Literal['asc', 'desc']`
    :   Adjusted amount for the order.

    `amount_paid: Literal['asc', 'desc']`
    :   Amount paid for the order.

    `base_currency_code: Literal['asc', 'desc']`
    :   The base currency code used for the order.

    `batch_id: Literal['asc', 'desc']`
    :   Unique identifier for the batch the order belongs to.

    `billing_address: Literal['asc', 'desc']`
    :   The billing address associated with the order

    `business_entity_id: Literal['asc', 'desc']`
    :   Identifier for the business entity associated with the order.

    `cancellation_reason: Literal['asc', 'desc']`
    :   Reason for order cancellation.

    `cancelled_at: Literal['asc', 'desc']`
    :   Timestamp when the order was cancelled.

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the order was created.

    `created_by: Literal['asc', 'desc']`
    :   User or system that created the order.

    `currency_code: Literal['asc', 'desc']`
    :   Currency code used for the order.

    `custom_fields: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `customer_id: Literal['asc', 'desc']`
    :   Identifier for the customer placing the order.

    `deleted: Literal['asc', 'desc']`
    :   Flag indicating if the order has been deleted.

    `delivered_at: Literal['asc', 'desc']`
    :   Timestamp when the order was delivered.

    `discount: Literal['asc', 'desc']`
    :   Discount amount applied to the order.

    `document_number: Literal['asc', 'desc']`
    :   Unique document number associated with the order.

    `exchange_rate: Literal['asc', 'desc']`
    :   Rate used for currency exchange in the order.

    `fulfillment_status: Literal['asc', 'desc']`
    :   Status of fulfillment for the order.

    `gift_id: Literal['asc', 'desc']`
    :   Identifier for any gift associated with the order.

    `gift_note: Literal['asc', 'desc']`
    :   Note attached to any gift in the order.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the order.

    `invoice_id: Literal['asc', 'desc']`
    :   Identifier for the invoice associated with the order.

    `invoice_round_off_amount: Literal['asc', 'desc']`
    :   Round-off amount applied to the invoice.

    `is_gifted: Literal['asc', 'desc']`
    :   Flag indicating if the order is a gift.

    `is_resent: Literal['asc', 'desc']`
    :   Flag indicating if the order has been resent.

    `line_item_discounts: Literal['asc', 'desc']`
    :   Discounts applied to individual line items

    `line_item_taxes: Literal['asc', 'desc']`
    :   Taxes applied to individual line items

    `linked_credit_notes: Literal['asc', 'desc']`
    :   Credit notes linked to the order

    `note: Literal['asc', 'desc']`
    :   Additional notes or comments for the order.

    `object_: Literal['asc', 'desc']`
    :   Type of object representing an order in the system.

    `order_date: Literal['asc', 'desc']`
    :   Date when the order was created.

    `order_line_items: Literal['asc', 'desc']`
    :   List of line items in the order

    `order_type: Literal['asc', 'desc']`
    :   Type of order such as purchase order or sales order.

    `original_order_id: Literal['asc', 'desc']`
    :   Identifier for the original order if this is a modified order.

    `paid_on: Literal['asc', 'desc']`
    :   Timestamp when the order was paid for.

    `payment_status: Literal['asc', 'desc']`
    :   Status of payment for the order.

    `price_type: Literal['asc', 'desc']`
    :   Type of pricing used for the order.

    `reference_id: Literal['asc', 'desc']`
    :   Reference identifier for the order.

    `refundable_credits: Literal['asc', 'desc']`
    :   Credits that can be refunded for the whole order.

    `refundable_credits_issued: Literal['asc', 'desc']`
    :   Credits already issued for refund for the whole order.

    `resend_reason: Literal['asc', 'desc']`
    :   Reason for resending the order.

    `resent_orders: Literal['asc', 'desc']`
    :   Orders that were resent to the customer

    `resent_status: Literal['asc', 'desc']`
    :   Status of the resent order.

    `resource_version: Literal['asc', 'desc']`
    :   Version of the resource or order data.

    `rounding_adjustement: Literal['asc', 'desc']`
    :   Adjustment made for rounding off the order amount.

    `shipment_carrier: Literal['asc', 'desc']`
    :   Carrier for shipping the order.

    `shipped_at: Literal['asc', 'desc']`
    :   Timestamp when the order was shipped.

    `shipping_address: Literal['asc', 'desc']`
    :   The shipping address for the order

    `shipping_cut_off_date: Literal['asc', 'desc']`
    :   Date indicating the shipping cut-off for the order.

    `shipping_date: Literal['asc', 'desc']`
    :   Date when the order is scheduled for shipping.

    `status: Literal['asc', 'desc']`
    :   Current status of the order.

    `status_update_at: Literal['asc', 'desc']`
    :   Timestamp when the status of the order was last updated.

    `sub_total: Literal['asc', 'desc']`
    :   Sub-total amount for the order before applying taxes or discounts.

    `subscription_id: Literal['asc', 'desc']`
    :   Identifier for the subscription associated with the order.

    `tax: Literal['asc', 'desc']`
    :   Total tax amount for the order.

    `total: Literal['asc', 'desc']`
    :   Total amount including taxes and discounts for the order.

    `tracking_id: Literal['asc', 'desc']`
    :   Tracking identifier for the order shipment.

    `tracking_url: Literal['asc', 'desc']`
    :   URL for tracking the order shipment.

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the order data was last updated.

<a id="OrderStringFilter"></a>

`OrderStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount_adjusted: str`
    :   Adjusted amount for the order.

    `amount_paid: str`
    :   Amount paid for the order.

    `base_currency_code: str`
    :   The base currency code used for the order.

    `batch_id: str`
    :   Unique identifier for the batch the order belongs to.

    `billing_address: str`
    :   The billing address associated with the order

    `business_entity_id: str`
    :   Identifier for the business entity associated with the order.

    `cancellation_reason: str`
    :   Reason for order cancellation.

    `cancelled_at: str`
    :   Timestamp when the order was cancelled.

    `created_at: str`
    :   Timestamp when the order was created.

    `created_by: str`
    :   User or system that created the order.

    `currency_code: str`
    :   Currency code used for the order.

    `custom_fields: str`
    :   The type of the None singleton.

    `customer_id: str`
    :   Identifier for the customer placing the order.

    `deleted: str`
    :   Flag indicating if the order has been deleted.

    `delivered_at: str`
    :   Timestamp when the order was delivered.

    `discount: str`
    :   Discount amount applied to the order.

    `document_number: str`
    :   Unique document number associated with the order.

    `exchange_rate: str`
    :   Rate used for currency exchange in the order.

    `fulfillment_status: str`
    :   Status of fulfillment for the order.

    `gift_id: str`
    :   Identifier for any gift associated with the order.

    `gift_note: str`
    :   Note attached to any gift in the order.

    `id: str`
    :   Unique identifier for the order.

    `invoice_id: str`
    :   Identifier for the invoice associated with the order.

    `invoice_round_off_amount: str`
    :   Round-off amount applied to the invoice.

    `is_gifted: str`
    :   Flag indicating if the order is a gift.

    `is_resent: str`
    :   Flag indicating if the order has been resent.

    `line_item_discounts: str`
    :   Discounts applied to individual line items

    `line_item_taxes: str`
    :   Taxes applied to individual line items

    `linked_credit_notes: str`
    :   Credit notes linked to the order

    `note: str`
    :   Additional notes or comments for the order.

    `object_: str`
    :   Type of object representing an order in the system.

    `order_date: str`
    :   Date when the order was created.

    `order_line_items: str`
    :   List of line items in the order

    `order_type: str`
    :   Type of order such as purchase order or sales order.

    `original_order_id: str`
    :   Identifier for the original order if this is a modified order.

    `paid_on: str`
    :   Timestamp when the order was paid for.

    `payment_status: str`
    :   Status of payment for the order.

    `price_type: str`
    :   Type of pricing used for the order.

    `reference_id: str`
    :   Reference identifier for the order.

    `refundable_credits: str`
    :   Credits that can be refunded for the whole order.

    `refundable_credits_issued: str`
    :   Credits already issued for refund for the whole order.

    `resend_reason: str`
    :   Reason for resending the order.

    `resent_orders: str`
    :   Orders that were resent to the customer

    `resent_status: str`
    :   Status of the resent order.

    `resource_version: str`
    :   Version of the resource or order data.

    `rounding_adjustement: str`
    :   Adjustment made for rounding off the order amount.

    `shipment_carrier: str`
    :   Carrier for shipping the order.

    `shipped_at: str`
    :   Timestamp when the order was shipped.

    `shipping_address: str`
    :   The shipping address for the order

    `shipping_cut_off_date: str`
    :   Date indicating the shipping cut-off for the order.

    `shipping_date: str`
    :   Date when the order is scheduled for shipping.

    `status: str`
    :   Current status of the order.

    `status_update_at: str`
    :   Timestamp when the status of the order was last updated.

    `sub_total: str`
    :   Sub-total amount for the order before applying taxes or discounts.

    `subscription_id: str`
    :   Identifier for the subscription associated with the order.

    `tax: str`
    :   Total tax amount for the order.

    `total: str`
    :   Total amount including taxes and discounts for the order.

    `tracking_id: str`
    :   Tracking identifier for the order shipment.

    `tracking_url: str`
    :   URL for tracking the order shipment.

    `updated_at: str`
    :   Timestamp when the order data was last updated.

<a id="PaymentSourceAndCondition"></a>

`PaymentSourceAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceEqCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceGtCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceGteCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceLtCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceLteCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceInCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceNotCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceAndCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceOrCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceAnyCondition]`
    :   The type of the None singleton.

<a id="PaymentSourceAnyCondition"></a>

`PaymentSourceAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceAnyValueFilter`
    :   The type of the None singleton.

<a id="PaymentSourceAnyValueFilter"></a>

`PaymentSourceAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amazon_payment: Any`
    :   Data related to Amazon Pay payment source

    `bank_account: Any`
    :   Data related to bank account payment source

    `business_entity_id: Any`
    :   Identifier for the business entity associated with the payment source

    `card: Any`
    :   Data related to card payment source

    `created_at: Any`
    :   Timestamp indicating when the payment source was created

    `custom_fields: Any`
    :   The type of the None singleton.

    `customer_id: Any`
    :   Unique identifier for the customer associated with the payment source

    `deleted: Any`
    :   Indicates if the payment source has been deleted

    `gateway: Any`
    :   Name of the payment gateway used for the payment source

    `gateway_account_id: Any`
    :   Identifier for the gateway account tied to the payment source

    `id: Any`
    :   Unique identifier for the payment source

    `ip_address: Any`
    :   IP address associated with the payment source

    `issuing_country: Any`
    :   Country where the payment source was issued

    `mandates: Any`
    :   Data related to mandates for payments

    `object_: Any`
    :   Type of object, e.g., payment_source

    `paypal: Any`
    :   Data related to PayPal payment source

    `reference_id: Any`
    :   Reference identifier for the payment source

    `resource_version: Any`
    :   Version of the payment source resource

    `status: Any`
    :   Status of the payment source, e.g., active or inactive

    `type_: Any`
    :   Type of payment source, e.g., card, bank_account

    `updated_at: Any`
    :   Timestamp indicating when the payment source was last updated

    `upi: Any`
    :   Data related to UPI payment source

<a id="PaymentSourceContainsCondition"></a>

`PaymentSourceContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceAnyValueFilter`
    :   The type of the None singleton.

<a id="PaymentSourceEqCondition"></a>

`PaymentSourceEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceSearchFilter`
    :   The type of the None singleton.

<a id="PaymentSourceFuzzyCondition"></a>

`PaymentSourceFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceStringFilter`
    :   The type of the None singleton.

<a id="PaymentSourceGetParams"></a>

`PaymentSourceGetParams(*args, **kwargs)`
:   Parameters for payment_source.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="PaymentSourceGtCondition"></a>

`PaymentSourceGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceSearchFilter`
    :   The type of the None singleton.

<a id="PaymentSourceGteCondition"></a>

`PaymentSourceGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceSearchFilter`
    :   The type of the None singleton.

<a id="PaymentSourceInCondition"></a>

`PaymentSourceInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceInFilter`
    :   The type of the None singleton.

<a id="PaymentSourceInFilter"></a>

`PaymentSourceInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amazon_payment: list[dict[str, typing.Any]]`
    :   Data related to Amazon Pay payment source

    `bank_account: list[dict[str, typing.Any]]`
    :   Data related to bank account payment source

    `business_entity_id: list[str]`
    :   Identifier for the business entity associated with the payment source

    `card: list[dict[str, typing.Any]]`
    :   Data related to card payment source

    `created_at: list[int]`
    :   Timestamp indicating when the payment source was created

    `custom_fields: list[list[typing.Any]]`
    :   The type of the None singleton.

    `customer_id: list[str]`
    :   Unique identifier for the customer associated with the payment source

    `deleted: list[bool]`
    :   Indicates if the payment source has been deleted

    `gateway: list[str]`
    :   Name of the payment gateway used for the payment source

    `gateway_account_id: list[str]`
    :   Identifier for the gateway account tied to the payment source

    `id: list[str]`
    :   Unique identifier for the payment source

    `ip_address: list[str]`
    :   IP address associated with the payment source

    `issuing_country: list[str]`
    :   Country where the payment source was issued

    `mandates: list[dict[str, typing.Any]]`
    :   Data related to mandates for payments

    `object_: list[str]`
    :   Type of object, e.g., payment_source

    `paypal: list[dict[str, typing.Any]]`
    :   Data related to PayPal payment source

    `reference_id: list[str]`
    :   Reference identifier for the payment source

    `resource_version: list[int]`
    :   Version of the payment source resource

    `status: list[str]`
    :   Status of the payment source, e.g., active or inactive

    `type_: list[str]`
    :   Type of payment source, e.g., card, bank_account

    `updated_at: list[int]`
    :   Timestamp indicating when the payment source was last updated

    `upi: list[dict[str, typing.Any]]`
    :   Data related to UPI payment source

<a id="PaymentSourceKeywordCondition"></a>

`PaymentSourceKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceStringFilter`
    :   The type of the None singleton.

<a id="PaymentSourceLikeCondition"></a>

`PaymentSourceLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceStringFilter`
    :   The type of the None singleton.

<a id="PaymentSourceListParams"></a>

`PaymentSourceListParams(*args, **kwargs)`
:   Parameters for payment_source.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

<a id="PaymentSourceLtCondition"></a>

`PaymentSourceLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceSearchFilter`
    :   The type of the None singleton.

<a id="PaymentSourceLteCondition"></a>

`PaymentSourceLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceSearchFilter`
    :   The type of the None singleton.

<a id="PaymentSourceNeqCondition"></a>

`PaymentSourceNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceSearchFilter`
    :   The type of the None singleton.

<a id="PaymentSourceNotCondition"></a>

`PaymentSourceNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceEqCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceGtCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceGteCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceLtCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceLteCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceInCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceNotCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceAndCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceOrCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceAnyCondition`
    :   The type of the None singleton.

<a id="PaymentSourceOrCondition"></a>

`PaymentSourceOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceEqCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceGtCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceGteCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceLtCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceLteCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceInCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceNotCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceAndCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceOrCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceAnyCondition]`
    :   The type of the None singleton.

<a id="PaymentSourceSearchFilter"></a>

`PaymentSourceSearchFilter(*args, **kwargs)`
:   Available fields for filtering payment_source search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="PaymentSourceSearchQuery"></a>

`PaymentSourceSearchQuery(*args, **kwargs)`
:   Search query for payment_source entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceEqCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceGtCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceGteCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceLtCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceLteCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceInCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceNotCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceAndCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceOrCondition | airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.chargebee.types.PaymentSourceSortFilter]`
    :   The type of the None singleton.

<a id="PaymentSourceSortFilter"></a>

`PaymentSourceSortFilter(*args, **kwargs)`
:   Available fields for sorting payment_source search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amazon_payment: Literal['asc', 'desc']`
    :   Data related to Amazon Pay payment source

    `bank_account: Literal['asc', 'desc']`
    :   Data related to bank account payment source

    `business_entity_id: Literal['asc', 'desc']`
    :   Identifier for the business entity associated with the payment source

    `card: Literal['asc', 'desc']`
    :   Data related to card payment source

    `created_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the payment source was created

    `custom_fields: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `customer_id: Literal['asc', 'desc']`
    :   Unique identifier for the customer associated with the payment source

    `deleted: Literal['asc', 'desc']`
    :   Indicates if the payment source has been deleted

    `gateway: Literal['asc', 'desc']`
    :   Name of the payment gateway used for the payment source

    `gateway_account_id: Literal['asc', 'desc']`
    :   Identifier for the gateway account tied to the payment source

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the payment source

    `ip_address: Literal['asc', 'desc']`
    :   IP address associated with the payment source

    `issuing_country: Literal['asc', 'desc']`
    :   Country where the payment source was issued

    `mandates: Literal['asc', 'desc']`
    :   Data related to mandates for payments

    `object_: Literal['asc', 'desc']`
    :   Type of object, e.g., payment_source

    `paypal: Literal['asc', 'desc']`
    :   Data related to PayPal payment source

    `reference_id: Literal['asc', 'desc']`
    :   Reference identifier for the payment source

    `resource_version: Literal['asc', 'desc']`
    :   Version of the payment source resource

    `status: Literal['asc', 'desc']`
    :   Status of the payment source, e.g., active or inactive

    `type_: Literal['asc', 'desc']`
    :   Type of payment source, e.g., card, bank_account

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the payment source was last updated

    `upi: Literal['asc', 'desc']`
    :   Data related to UPI payment source

<a id="PaymentSourceStringFilter"></a>

`PaymentSourceStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amazon_payment: str`
    :   Data related to Amazon Pay payment source

    `bank_account: str`
    :   Data related to bank account payment source

    `business_entity_id: str`
    :   Identifier for the business entity associated with the payment source

    `card: str`
    :   Data related to card payment source

    `created_at: str`
    :   Timestamp indicating when the payment source was created

    `custom_fields: str`
    :   The type of the None singleton.

    `customer_id: str`
    :   Unique identifier for the customer associated with the payment source

    `deleted: str`
    :   Indicates if the payment source has been deleted

    `gateway: str`
    :   Name of the payment gateway used for the payment source

    `gateway_account_id: str`
    :   Identifier for the gateway account tied to the payment source

    `id: str`
    :   Unique identifier for the payment source

    `ip_address: str`
    :   IP address associated with the payment source

    `issuing_country: str`
    :   Country where the payment source was issued

    `mandates: str`
    :   Data related to mandates for payments

    `object_: str`
    :   Type of object, e.g., payment_source

    `paypal: str`
    :   Data related to PayPal payment source

    `reference_id: str`
    :   Reference identifier for the payment source

    `resource_version: str`
    :   Version of the payment source resource

    `status: str`
    :   Status of the payment source, e.g., active or inactive

    `type_: str`
    :   Type of payment source, e.g., card, bank_account

    `updated_at: str`
    :   Timestamp indicating when the payment source was last updated

    `upi: str`
    :   Data related to UPI payment source

<a id="SubscriptionAndCondition"></a>

`SubscriptionAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.chargebee.types.SubscriptionEqCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionGtCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionGteCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionLtCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionLteCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionInCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionNotCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionAndCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionOrCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionAnyCondition]`
    :   The type of the None singleton.

<a id="SubscriptionAnyCondition"></a>

`SubscriptionAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.chargebee.types.SubscriptionAnyValueFilter`
    :   The type of the None singleton.

<a id="SubscriptionAnyValueFilter"></a>

`SubscriptionAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `activated_at: Any`
    :   The date and time when the subscription was activated.

    `addons: Any`
    :   Represents any additional features or services added to the subscription

    `affiliate_token: Any`
    :   The affiliate token associated with the subscription.

    `auto_close_invoices: Any`
    :   Defines if the invoices are automatically closed or not.

    `auto_collection: Any`
    :   Indicates if auto-collection is enabled for the subscription.

    `base_currency_code: Any`
    :   The base currency code used for the subscription.

    `billing_period: Any`
    :   The billing period duration for the subscription.

    `billing_period_unit: Any`
    :   The unit of the billing period.

    `business_entity_id: Any`
    :   The ID of the business entity to which the subscription belongs.

    `cancel_reason: Any`
    :   The reason for the cancellation of the subscription.

    `cancel_reason_code: Any`
    :   The code associated with the cancellation reason.

    `cancel_schedule_created_at: Any`
    :   The date and time when the cancellation schedule was created.

    `cancelled_at: Any`
    :   The date and time when the subscription was cancelled.

    `channel: Any`
    :   The channel through which the subscription was acquired.

    `charged_event_based_addons: Any`
    :   Details of addons charged based on events

    `charged_items: Any`
    :   Lists the items that have been charged as part of the subscription

    `contract_term: Any`
    :   Contains details about the contract term of the subscription

    `contract_term_billing_cycle_on_renewal: Any`
    :   Indicates if the contract term billing cycle is applied on renewal.

    `coupon: Any`
    :   The coupon applied to the subscription.

    `coupons: Any`
    :   Details of applied coupons

    `create_pending_invoices: Any`
    :   Indicates if pending invoices are created.

    `created_at: Any`
    :   The date and time of the creation of the subscription.

    `created_from_ip: Any`
    :   The IP address from which the subscription was created.

    `currency_code: Any`
    :   The currency code used for the subscription.

    `current_term_end: Any`
    :   The end date of the current term for the subscription.

    `current_term_start: Any`
    :   The start date of the current term for the subscription.

    `custom_fields: Any`
    :   The type of the None singleton.

    `customer_id: Any`
    :   The ID of the customer associated with the subscription.

    `deleted: Any`
    :   Indicates if the subscription has been deleted.

    `discounts: Any`
    :   Includes any discounts applied to the subscription

    `due_invoices_count: Any`
    :   The count of due invoices for the subscription.

    `due_since: Any`
    :   The date since which the invoices are due.

    `event_based_addons: Any`
    :   Specifies any event-based addons associated with the subscription

    `exchange_rate: Any`
    :   The exchange rate used for currency conversion.

    `free_period: Any`
    :   The duration of the free period for the subscription.

    `free_period_unit: Any`
    :   The unit of the free period duration.

    `gift_id: Any`
    :   The ID of the gift associated with the subscription.

    `has_scheduled_advance_invoices: Any`
    :   Indicates if there are scheduled advance invoices for the subscription.

    `has_scheduled_changes: Any`
    :   Indicates if there are scheduled changes for the subscription.

    `id: Any`
    :   The unique ID of the subscription.

    `invoice_notes: Any`
    :   Any notes added to the invoices of the subscription.

    `item_tiers: Any`
    :   Provides information about tiers or levels for specific subscription items

    `meta_data: Any`
    :   Additional metadata associated with subscription

    `metadata: Any`
    :   Additional metadata associated with subscription

    `mrr: Any`
    :   The monthly recurring revenue generated by the subscription.

    `next_billing_at: Any`
    :   The date and time of the next billing event for the subscription.

    `object_: Any`
    :   The type of object (subscription).

    `offline_payment_method: Any`
    :   The offline payment method used for the subscription.

    `override_relationship: Any`
    :   Indicates if the existing relationship is overridden by this subscription.

    `pause_date: Any`
    :   The date on which the subscription was paused.

    `payment_source_id: Any`
    :   The ID of the payment source used for the subscription.

    `plan_amount: Any`
    :   The total amount charged for the plan of the subscription.

    `plan_amount_in_decimal: Any`
    :   The total amount charged for the plan in decimal format.

    `plan_free_quantity: Any`
    :   The free quantity included in the plan of the subscription.

    `plan_free_quantity_in_decimal: Any`
    :   The free quantity included in the plan in decimal format.

    `plan_id: Any`
    :   The ID of the plan associated with the subscription.

    `plan_quantity: Any`
    :   The quantity of the plan included in the subscription.

    `plan_quantity_in_decimal: Any`
    :   The quantity of the plan in decimal format.

    `plan_unit_price: Any`
    :   The unit price of the plan for the subscription.

    `plan_unit_price_in_decimal: Any`
    :   The unit price of the plan in decimal format.

    `po_number: Any`
    :   The purchase order number associated with the subscription.

    `referral_info: Any`
    :   Contains details related to any referral information associated with the subscription

    `remaining_billing_cycles: Any`
    :   The count of remaining billing cycles for the subscription.

    `resource_version: Any`
    :   The version of the resource (subscription).

    `resume_date: Any`
    :   The date on which the subscription was resumed.

    `setup_fee: Any`
    :   The setup fee charged for the subscription.

    `shipping_address: Any`
    :   Stores the shipping address related to the subscription

    `start_date: Any`
    :   The start date of the subscription.

    `started_at: Any`
    :   The date and time when the subscription started.

    `status: Any`
    :   The current status of the subscription.

    `subscription_items: Any`
    :   Lists individual items included in the subscription

    `total_dues: Any`
    :   The total amount of dues for the subscription.

    `trial_end: Any`
    :   The end date of the trial period for the subscription.

    `trial_end_action: Any`
    :   The action to be taken at the end of the trial period.

    `trial_start: Any`
    :   The start date of the trial period for the subscription.

    `updated_at: Any`
    :   The date and time when the subscription was last updated.

<a id="SubscriptionContainsCondition"></a>

`SubscriptionContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.chargebee.types.SubscriptionAnyValueFilter`
    :   The type of the None singleton.

<a id="SubscriptionEqCondition"></a>

`SubscriptionEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.chargebee.types.SubscriptionSearchFilter`
    :   The type of the None singleton.

<a id="SubscriptionFuzzyCondition"></a>

`SubscriptionFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.chargebee.types.SubscriptionStringFilter`
    :   The type of the None singleton.

<a id="SubscriptionGetParams"></a>

`SubscriptionGetParams(*args, **kwargs)`
:   Parameters for subscription.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="SubscriptionGtCondition"></a>

`SubscriptionGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.chargebee.types.SubscriptionSearchFilter`
    :   The type of the None singleton.

<a id="SubscriptionGteCondition"></a>

`SubscriptionGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.chargebee.types.SubscriptionSearchFilter`
    :   The type of the None singleton.

<a id="SubscriptionInCondition"></a>

`SubscriptionInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.chargebee.types.SubscriptionInFilter`
    :   The type of the None singleton.

<a id="SubscriptionInFilter"></a>

`SubscriptionInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `activated_at: list[int]`
    :   The date and time when the subscription was activated.

    `addons: list[list[typing.Any]]`
    :   Represents any additional features or services added to the subscription

    `affiliate_token: list[str]`
    :   The affiliate token associated with the subscription.

    `auto_close_invoices: list[bool]`
    :   Defines if the invoices are automatically closed or not.

    `auto_collection: list[str]`
    :   Indicates if auto-collection is enabled for the subscription.

    `base_currency_code: list[str]`
    :   The base currency code used for the subscription.

    `billing_period: list[int]`
    :   The billing period duration for the subscription.

    `billing_period_unit: list[str]`
    :   The unit of the billing period.

    `business_entity_id: list[str]`
    :   The ID of the business entity to which the subscription belongs.

    `cancel_reason: list[str]`
    :   The reason for the cancellation of the subscription.

    `cancel_reason_code: list[str]`
    :   The code associated with the cancellation reason.

    `cancel_schedule_created_at: list[int]`
    :   The date and time when the cancellation schedule was created.

    `cancelled_at: list[int]`
    :   The date and time when the subscription was cancelled.

    `channel: list[str]`
    :   The channel through which the subscription was acquired.

    `charged_event_based_addons: list[list[typing.Any]]`
    :   Details of addons charged based on events

    `charged_items: list[list[typing.Any]]`
    :   Lists the items that have been charged as part of the subscription

    `contract_term: list[dict[str, typing.Any]]`
    :   Contains details about the contract term of the subscription

    `contract_term_billing_cycle_on_renewal: list[int]`
    :   Indicates if the contract term billing cycle is applied on renewal.

    `coupon: list[str]`
    :   The coupon applied to the subscription.

    `coupons: list[list[typing.Any]]`
    :   Details of applied coupons

    `create_pending_invoices: list[bool]`
    :   Indicates if pending invoices are created.

    `created_at: list[int]`
    :   The date and time of the creation of the subscription.

    `created_from_ip: list[str]`
    :   The IP address from which the subscription was created.

    `currency_code: list[str]`
    :   The currency code used for the subscription.

    `current_term_end: list[int]`
    :   The end date of the current term for the subscription.

    `current_term_start: list[int]`
    :   The start date of the current term for the subscription.

    `custom_fields: list[list[typing.Any]]`
    :   The type of the None singleton.

    `customer_id: list[str]`
    :   The ID of the customer associated with the subscription.

    `deleted: list[bool]`
    :   Indicates if the subscription has been deleted.

    `discounts: list[list[typing.Any]]`
    :   Includes any discounts applied to the subscription

    `due_invoices_count: list[int]`
    :   The count of due invoices for the subscription.

    `due_since: list[int]`
    :   The date since which the invoices are due.

    `event_based_addons: list[list[typing.Any]]`
    :   Specifies any event-based addons associated with the subscription

    `exchange_rate: list[float]`
    :   The exchange rate used for currency conversion.

    `free_period: list[int]`
    :   The duration of the free period for the subscription.

    `free_period_unit: list[str]`
    :   The unit of the free period duration.

    `gift_id: list[str]`
    :   The ID of the gift associated with the subscription.

    `has_scheduled_advance_invoices: list[bool]`
    :   Indicates if there are scheduled advance invoices for the subscription.

    `has_scheduled_changes: list[bool]`
    :   Indicates if there are scheduled changes for the subscription.

    `id: list[str]`
    :   The unique ID of the subscription.

    `invoice_notes: list[str]`
    :   Any notes added to the invoices of the subscription.

    `item_tiers: list[list[typing.Any]]`
    :   Provides information about tiers or levels for specific subscription items

    `meta_data: list[dict[str, typing.Any]]`
    :   Additional metadata associated with subscription

    `metadata: list[dict[str, typing.Any]]`
    :   Additional metadata associated with subscription

    `mrr: list[int]`
    :   The monthly recurring revenue generated by the subscription.

    `next_billing_at: list[int]`
    :   The date and time of the next billing event for the subscription.

    `object_: list[str]`
    :   The type of object (subscription).

    `offline_payment_method: list[str]`
    :   The offline payment method used for the subscription.

    `override_relationship: list[bool]`
    :   Indicates if the existing relationship is overridden by this subscription.

    `pause_date: list[int]`
    :   The date on which the subscription was paused.

    `payment_source_id: list[str]`
    :   The ID of the payment source used for the subscription.

    `plan_amount: list[int]`
    :   The total amount charged for the plan of the subscription.

    `plan_amount_in_decimal: list[str]`
    :   The total amount charged for the plan in decimal format.

    `plan_free_quantity: list[int]`
    :   The free quantity included in the plan of the subscription.

    `plan_free_quantity_in_decimal: list[str]`
    :   The free quantity included in the plan in decimal format.

    `plan_id: list[str]`
    :   The ID of the plan associated with the subscription.

    `plan_quantity: list[int]`
    :   The quantity of the plan included in the subscription.

    `plan_quantity_in_decimal: list[str]`
    :   The quantity of the plan in decimal format.

    `plan_unit_price: list[int]`
    :   The unit price of the plan for the subscription.

    `plan_unit_price_in_decimal: list[str]`
    :   The unit price of the plan in decimal format.

    `po_number: list[str]`
    :   The purchase order number associated with the subscription.

    `referral_info: list[dict[str, typing.Any]]`
    :   Contains details related to any referral information associated with the subscription

    `remaining_billing_cycles: list[int]`
    :   The count of remaining billing cycles for the subscription.

    `resource_version: list[int]`
    :   The version of the resource (subscription).

    `resume_date: list[int]`
    :   The date on which the subscription was resumed.

    `setup_fee: list[int]`
    :   The setup fee charged for the subscription.

    `shipping_address: list[dict[str, typing.Any]]`
    :   Stores the shipping address related to the subscription

    `start_date: list[int]`
    :   The start date of the subscription.

    `started_at: list[int]`
    :   The date and time when the subscription started.

    `status: list[str]`
    :   The current status of the subscription.

    `subscription_items: list[list[typing.Any]]`
    :   Lists individual items included in the subscription

    `total_dues: list[int]`
    :   The total amount of dues for the subscription.

    `trial_end: list[int]`
    :   The end date of the trial period for the subscription.

    `trial_end_action: list[str]`
    :   The action to be taken at the end of the trial period.

    `trial_start: list[int]`
    :   The start date of the trial period for the subscription.

    `updated_at: list[int]`
    :   The date and time when the subscription was last updated.

<a id="SubscriptionKeywordCondition"></a>

`SubscriptionKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.chargebee.types.SubscriptionStringFilter`
    :   The type of the None singleton.

<a id="SubscriptionLikeCondition"></a>

`SubscriptionLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.chargebee.types.SubscriptionStringFilter`
    :   The type of the None singleton.

<a id="SubscriptionListParams"></a>

`SubscriptionListParams(*args, **kwargs)`
:   Parameters for subscription.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

<a id="SubscriptionLtCondition"></a>

`SubscriptionLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.chargebee.types.SubscriptionSearchFilter`
    :   The type of the None singleton.

<a id="SubscriptionLteCondition"></a>

`SubscriptionLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.chargebee.types.SubscriptionSearchFilter`
    :   The type of the None singleton.

<a id="SubscriptionNeqCondition"></a>

`SubscriptionNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.chargebee.types.SubscriptionSearchFilter`
    :   The type of the None singleton.

<a id="SubscriptionNotCondition"></a>

`SubscriptionNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.chargebee.types.SubscriptionEqCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionGtCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionGteCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionLtCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionLteCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionInCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionNotCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionAndCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionOrCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionAnyCondition`
    :   The type of the None singleton.

<a id="SubscriptionOrCondition"></a>

`SubscriptionOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.chargebee.types.SubscriptionEqCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionGtCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionGteCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionLtCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionLteCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionInCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionNotCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionAndCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionOrCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionAnyCondition]`
    :   The type of the None singleton.

<a id="SubscriptionSearchFilter"></a>

`SubscriptionSearchFilter(*args, **kwargs)`
:   Available fields for filtering subscription search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="SubscriptionSearchQuery"></a>

`SubscriptionSearchQuery(*args, **kwargs)`
:   Search query for subscription entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.chargebee.types.SubscriptionEqCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionGtCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionGteCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionLtCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionLteCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionInCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionNotCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionAndCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionOrCondition | airbyte_agent_sdk.connectors.chargebee.types.SubscriptionAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.chargebee.types.SubscriptionSortFilter]`
    :   The type of the None singleton.

<a id="SubscriptionSortFilter"></a>

`SubscriptionSortFilter(*args, **kwargs)`
:   Available fields for sorting subscription search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `activated_at: Literal['asc', 'desc']`
    :   The date and time when the subscription was activated.

    `addons: Literal['asc', 'desc']`
    :   Represents any additional features or services added to the subscription

    `affiliate_token: Literal['asc', 'desc']`
    :   The affiliate token associated with the subscription.

    `auto_close_invoices: Literal['asc', 'desc']`
    :   Defines if the invoices are automatically closed or not.

    `auto_collection: Literal['asc', 'desc']`
    :   Indicates if auto-collection is enabled for the subscription.

    `base_currency_code: Literal['asc', 'desc']`
    :   The base currency code used for the subscription.

    `billing_period: Literal['asc', 'desc']`
    :   The billing period duration for the subscription.

    `billing_period_unit: Literal['asc', 'desc']`
    :   The unit of the billing period.

    `business_entity_id: Literal['asc', 'desc']`
    :   The ID of the business entity to which the subscription belongs.

    `cancel_reason: Literal['asc', 'desc']`
    :   The reason for the cancellation of the subscription.

    `cancel_reason_code: Literal['asc', 'desc']`
    :   The code associated with the cancellation reason.

    `cancel_schedule_created_at: Literal['asc', 'desc']`
    :   The date and time when the cancellation schedule was created.

    `cancelled_at: Literal['asc', 'desc']`
    :   The date and time when the subscription was cancelled.

    `channel: Literal['asc', 'desc']`
    :   The channel through which the subscription was acquired.

    `charged_event_based_addons: Literal['asc', 'desc']`
    :   Details of addons charged based on events

    `charged_items: Literal['asc', 'desc']`
    :   Lists the items that have been charged as part of the subscription

    `contract_term: Literal['asc', 'desc']`
    :   Contains details about the contract term of the subscription

    `contract_term_billing_cycle_on_renewal: Literal['asc', 'desc']`
    :   Indicates if the contract term billing cycle is applied on renewal.

    `coupon: Literal['asc', 'desc']`
    :   The coupon applied to the subscription.

    `coupons: Literal['asc', 'desc']`
    :   Details of applied coupons

    `create_pending_invoices: Literal['asc', 'desc']`
    :   Indicates if pending invoices are created.

    `created_at: Literal['asc', 'desc']`
    :   The date and time of the creation of the subscription.

    `created_from_ip: Literal['asc', 'desc']`
    :   The IP address from which the subscription was created.

    `currency_code: Literal['asc', 'desc']`
    :   The currency code used for the subscription.

    `current_term_end: Literal['asc', 'desc']`
    :   The end date of the current term for the subscription.

    `current_term_start: Literal['asc', 'desc']`
    :   The start date of the current term for the subscription.

    `custom_fields: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `customer_id: Literal['asc', 'desc']`
    :   The ID of the customer associated with the subscription.

    `deleted: Literal['asc', 'desc']`
    :   Indicates if the subscription has been deleted.

    `discounts: Literal['asc', 'desc']`
    :   Includes any discounts applied to the subscription

    `due_invoices_count: Literal['asc', 'desc']`
    :   The count of due invoices for the subscription.

    `due_since: Literal['asc', 'desc']`
    :   The date since which the invoices are due.

    `event_based_addons: Literal['asc', 'desc']`
    :   Specifies any event-based addons associated with the subscription

    `exchange_rate: Literal['asc', 'desc']`
    :   The exchange rate used for currency conversion.

    `free_period: Literal['asc', 'desc']`
    :   The duration of the free period for the subscription.

    `free_period_unit: Literal['asc', 'desc']`
    :   The unit of the free period duration.

    `gift_id: Literal['asc', 'desc']`
    :   The ID of the gift associated with the subscription.

    `has_scheduled_advance_invoices: Literal['asc', 'desc']`
    :   Indicates if there are scheduled advance invoices for the subscription.

    `has_scheduled_changes: Literal['asc', 'desc']`
    :   Indicates if there are scheduled changes for the subscription.

    `id: Literal['asc', 'desc']`
    :   The unique ID of the subscription.

    `invoice_notes: Literal['asc', 'desc']`
    :   Any notes added to the invoices of the subscription.

    `item_tiers: Literal['asc', 'desc']`
    :   Provides information about tiers or levels for specific subscription items

    `meta_data: Literal['asc', 'desc']`
    :   Additional metadata associated with subscription

    `metadata: Literal['asc', 'desc']`
    :   Additional metadata associated with subscription

    `mrr: Literal['asc', 'desc']`
    :   The monthly recurring revenue generated by the subscription.

    `next_billing_at: Literal['asc', 'desc']`
    :   The date and time of the next billing event for the subscription.

    `object_: Literal['asc', 'desc']`
    :   The type of object (subscription).

    `offline_payment_method: Literal['asc', 'desc']`
    :   The offline payment method used for the subscription.

    `override_relationship: Literal['asc', 'desc']`
    :   Indicates if the existing relationship is overridden by this subscription.

    `pause_date: Literal['asc', 'desc']`
    :   The date on which the subscription was paused.

    `payment_source_id: Literal['asc', 'desc']`
    :   The ID of the payment source used for the subscription.

    `plan_amount: Literal['asc', 'desc']`
    :   The total amount charged for the plan of the subscription.

    `plan_amount_in_decimal: Literal['asc', 'desc']`
    :   The total amount charged for the plan in decimal format.

    `plan_free_quantity: Literal['asc', 'desc']`
    :   The free quantity included in the plan of the subscription.

    `plan_free_quantity_in_decimal: Literal['asc', 'desc']`
    :   The free quantity included in the plan in decimal format.

    `plan_id: Literal['asc', 'desc']`
    :   The ID of the plan associated with the subscription.

    `plan_quantity: Literal['asc', 'desc']`
    :   The quantity of the plan included in the subscription.

    `plan_quantity_in_decimal: Literal['asc', 'desc']`
    :   The quantity of the plan in decimal format.

    `plan_unit_price: Literal['asc', 'desc']`
    :   The unit price of the plan for the subscription.

    `plan_unit_price_in_decimal: Literal['asc', 'desc']`
    :   The unit price of the plan in decimal format.

    `po_number: Literal['asc', 'desc']`
    :   The purchase order number associated with the subscription.

    `referral_info: Literal['asc', 'desc']`
    :   Contains details related to any referral information associated with the subscription

    `remaining_billing_cycles: Literal['asc', 'desc']`
    :   The count of remaining billing cycles for the subscription.

    `resource_version: Literal['asc', 'desc']`
    :   The version of the resource (subscription).

    `resume_date: Literal['asc', 'desc']`
    :   The date on which the subscription was resumed.

    `setup_fee: Literal['asc', 'desc']`
    :   The setup fee charged for the subscription.

    `shipping_address: Literal['asc', 'desc']`
    :   Stores the shipping address related to the subscription

    `start_date: Literal['asc', 'desc']`
    :   The start date of the subscription.

    `started_at: Literal['asc', 'desc']`
    :   The date and time when the subscription started.

    `status: Literal['asc', 'desc']`
    :   The current status of the subscription.

    `subscription_items: Literal['asc', 'desc']`
    :   Lists individual items included in the subscription

    `total_dues: Literal['asc', 'desc']`
    :   The total amount of dues for the subscription.

    `trial_end: Literal['asc', 'desc']`
    :   The end date of the trial period for the subscription.

    `trial_end_action: Literal['asc', 'desc']`
    :   The action to be taken at the end of the trial period.

    `trial_start: Literal['asc', 'desc']`
    :   The start date of the trial period for the subscription.

    `updated_at: Literal['asc', 'desc']`
    :   The date and time when the subscription was last updated.

<a id="SubscriptionStringFilter"></a>

`SubscriptionStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `activated_at: str`
    :   The date and time when the subscription was activated.

    `addons: str`
    :   Represents any additional features or services added to the subscription

    `affiliate_token: str`
    :   The affiliate token associated with the subscription.

    `auto_close_invoices: str`
    :   Defines if the invoices are automatically closed or not.

    `auto_collection: str`
    :   Indicates if auto-collection is enabled for the subscription.

    `base_currency_code: str`
    :   The base currency code used for the subscription.

    `billing_period: str`
    :   The billing period duration for the subscription.

    `billing_period_unit: str`
    :   The unit of the billing period.

    `business_entity_id: str`
    :   The ID of the business entity to which the subscription belongs.

    `cancel_reason: str`
    :   The reason for the cancellation of the subscription.

    `cancel_reason_code: str`
    :   The code associated with the cancellation reason.

    `cancel_schedule_created_at: str`
    :   The date and time when the cancellation schedule was created.

    `cancelled_at: str`
    :   The date and time when the subscription was cancelled.

    `channel: str`
    :   The channel through which the subscription was acquired.

    `charged_event_based_addons: str`
    :   Details of addons charged based on events

    `charged_items: str`
    :   Lists the items that have been charged as part of the subscription

    `contract_term: str`
    :   Contains details about the contract term of the subscription

    `contract_term_billing_cycle_on_renewal: str`
    :   Indicates if the contract term billing cycle is applied on renewal.

    `coupon: str`
    :   The coupon applied to the subscription.

    `coupons: str`
    :   Details of applied coupons

    `create_pending_invoices: str`
    :   Indicates if pending invoices are created.

    `created_at: str`
    :   The date and time of the creation of the subscription.

    `created_from_ip: str`
    :   The IP address from which the subscription was created.

    `currency_code: str`
    :   The currency code used for the subscription.

    `current_term_end: str`
    :   The end date of the current term for the subscription.

    `current_term_start: str`
    :   The start date of the current term for the subscription.

    `custom_fields: str`
    :   The type of the None singleton.

    `customer_id: str`
    :   The ID of the customer associated with the subscription.

    `deleted: str`
    :   Indicates if the subscription has been deleted.

    `discounts: str`
    :   Includes any discounts applied to the subscription

    `due_invoices_count: str`
    :   The count of due invoices for the subscription.

    `due_since: str`
    :   The date since which the invoices are due.

    `event_based_addons: str`
    :   Specifies any event-based addons associated with the subscription

    `exchange_rate: str`
    :   The exchange rate used for currency conversion.

    `free_period: str`
    :   The duration of the free period for the subscription.

    `free_period_unit: str`
    :   The unit of the free period duration.

    `gift_id: str`
    :   The ID of the gift associated with the subscription.

    `has_scheduled_advance_invoices: str`
    :   Indicates if there are scheduled advance invoices for the subscription.

    `has_scheduled_changes: str`
    :   Indicates if there are scheduled changes for the subscription.

    `id: str`
    :   The unique ID of the subscription.

    `invoice_notes: str`
    :   Any notes added to the invoices of the subscription.

    `item_tiers: str`
    :   Provides information about tiers or levels for specific subscription items

    `meta_data: str`
    :   Additional metadata associated with subscription

    `metadata: str`
    :   Additional metadata associated with subscription

    `mrr: str`
    :   The monthly recurring revenue generated by the subscription.

    `next_billing_at: str`
    :   The date and time of the next billing event for the subscription.

    `object_: str`
    :   The type of object (subscription).

    `offline_payment_method: str`
    :   The offline payment method used for the subscription.

    `override_relationship: str`
    :   Indicates if the existing relationship is overridden by this subscription.

    `pause_date: str`
    :   The date on which the subscription was paused.

    `payment_source_id: str`
    :   The ID of the payment source used for the subscription.

    `plan_amount: str`
    :   The total amount charged for the plan of the subscription.

    `plan_amount_in_decimal: str`
    :   The total amount charged for the plan in decimal format.

    `plan_free_quantity: str`
    :   The free quantity included in the plan of the subscription.

    `plan_free_quantity_in_decimal: str`
    :   The free quantity included in the plan in decimal format.

    `plan_id: str`
    :   The ID of the plan associated with the subscription.

    `plan_quantity: str`
    :   The quantity of the plan included in the subscription.

    `plan_quantity_in_decimal: str`
    :   The quantity of the plan in decimal format.

    `plan_unit_price: str`
    :   The unit price of the plan for the subscription.

    `plan_unit_price_in_decimal: str`
    :   The unit price of the plan in decimal format.

    `po_number: str`
    :   The purchase order number associated with the subscription.

    `referral_info: str`
    :   Contains details related to any referral information associated with the subscription

    `remaining_billing_cycles: str`
    :   The count of remaining billing cycles for the subscription.

    `resource_version: str`
    :   The version of the resource (subscription).

    `resume_date: str`
    :   The date on which the subscription was resumed.

    `setup_fee: str`
    :   The setup fee charged for the subscription.

    `shipping_address: str`
    :   Stores the shipping address related to the subscription

    `start_date: str`
    :   The start date of the subscription.

    `started_at: str`
    :   The date and time when the subscription started.

    `status: str`
    :   The current status of the subscription.

    `subscription_items: str`
    :   Lists individual items included in the subscription

    `total_dues: str`
    :   The total amount of dues for the subscription.

    `trial_end: str`
    :   The end date of the trial period for the subscription.

    `trial_end_action: str`
    :   The action to be taken at the end of the trial period.

    `trial_start: str`
    :   The start date of the trial period for the subscription.

    `updated_at: str`
    :   The date and time when the subscription was last updated.

<a id="TransactionAndCondition"></a>

`TransactionAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.chargebee.types.TransactionEqCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionGtCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionGteCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionLtCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionLteCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionInCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionNotCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionAndCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionOrCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionAnyCondition]`
    :   The type of the None singleton.

<a id="TransactionAnyCondition"></a>

`TransactionAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.chargebee.types.TransactionAnyValueFilter`
    :   The type of the None singleton.

<a id="TransactionAnyValueFilter"></a>

`TransactionAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Any`
    :   The total amount of the transaction.

    `amount_capturable: Any`
    :   The remaining amount that can be captured in the transaction.

    `amount_unused: Any`
    :   The amount in the transaction that remains unused.

    `authorization_reason: Any`
    :   Reason for authorization of the transaction.

    `base_currency_code: Any`
    :   The base currency code of the transaction.

    `business_entity_id: Any`
    :   The ID of the business entity related to the transaction.

    `cn_create_reason_code: Any`
    :   Reason code for creating a credit note.

    `cn_date: Any`
    :   Date of the credit note.

    `cn_reference_invoice_id: Any`
    :   ID of the invoice referenced in the credit note.

    `cn_status: Any`
    :   Status of the credit note.

    `cn_total: Any`
    :   Total amount of the credit note.

    `currency_code: Any`
    :   The currency code of the transaction.

    `custom_fields: Any`
    :   The type of the None singleton.

    `customer_id: Any`
    :   The ID of the customer associated with the transaction.

    `date: Any`
    :   Date of the transaction.

    `deleted: Any`
    :   Flag indicating if the transaction is deleted.

    `error_code: Any`
    :   Error code associated with the transaction.

    `error_detail: Any`
    :   Detailed error information related to the transaction.

    `error_text: Any`
    :   Error message text of the transaction.

    `exchange_rate: Any`
    :   Exchange rate used in the transaction.

    `fraud_flag: Any`
    :   Flag indicating if the transaction is flagged for fraud.

    `fraud_reason: Any`
    :   Reason for flagging the transaction as fraud.

    `gateway: Any`
    :   The payment gateway used in the transaction.

    `gateway_account_id: Any`
    :   ID of the gateway account used in the transaction.

    `id: Any`
    :   Unique identifier of the transaction.

    `id_at_gateway: Any`
    :   Transaction ID assigned by the gateway.

    `iin: Any`
    :   Bank identification number of the transaction.

    `initiator_type: Any`
    :   Type of initiator involved in the transaction.

    `last4: Any`
    :   Last 4 digits of the card used in the transaction.

    `linked_credit_notes: Any`
    :   Linked credit notes associated with the transaction.

    `linked_invoices: Any`
    :   Linked invoices associated with the transaction.

    `linked_payments: Any`
    :   Linked payments associated with the transaction.

    `linked_refunds: Any`
    :   Linked refunds associated with the transaction.

    `masked_card_number: Any`
    :   Masked card number used in the transaction.

    `merchant_reference_id: Any`
    :   Merchant reference ID of the transaction.

    `object_: Any`
    :   Type of object representing the transaction.

    `payment_method: Any`
    :   Payment method used in the transaction.

    `payment_method_details: Any`
    :   Details of the payment method used in the transaction.

    `payment_source_id: Any`
    :   ID of the payment source used in the transaction.

    `reference_authorization_id: Any`
    :   Reference authorization ID of the transaction.

    `reference_number: Any`
    :   Reference number associated with the transaction.

    `reference_transaction_id: Any`
    :   ID of the reference transaction.

    `refrence_number: Any`
    :   Reference number of the transaction.

    `refunded_txn_id: Any`
    :   ID of the refunded transaction.

    `resource_version: Any`
    :   Resource version of the transaction.

    `reversal_transaction_id: Any`
    :   ID of the reversal transaction, if any.

    `settled_at: Any`
    :   Date when the transaction was settled.

    `status: Any`
    :   Status of the transaction.

    `subscription_id: Any`
    :   ID of the subscription related to the transaction.

    `three_d_secure: Any`
    :   Flag indicating if 3D secure was used in the transaction.

    `txn_amount: Any`
    :   Amount of the transaction.

    `txn_date: Any`
    :   Date of the transaction.

    `type_: Any`
    :   Type of the transaction.

    `updated_at: Any`
    :   Date when the transaction was last updated.

    `voided_at: Any`
    :   Date when the transaction was voided.

<a id="TransactionContainsCondition"></a>

`TransactionContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.chargebee.types.TransactionAnyValueFilter`
    :   The type of the None singleton.

<a id="TransactionEqCondition"></a>

`TransactionEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.chargebee.types.TransactionSearchFilter`
    :   The type of the None singleton.

<a id="TransactionFuzzyCondition"></a>

`TransactionFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.chargebee.types.TransactionStringFilter`
    :   The type of the None singleton.

<a id="TransactionGetParams"></a>

`TransactionGetParams(*args, **kwargs)`
:   Parameters for transaction.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="TransactionGtCondition"></a>

`TransactionGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.chargebee.types.TransactionSearchFilter`
    :   The type of the None singleton.

<a id="TransactionGteCondition"></a>

`TransactionGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.chargebee.types.TransactionSearchFilter`
    :   The type of the None singleton.

<a id="TransactionInCondition"></a>

`TransactionInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.chargebee.types.TransactionInFilter`
    :   The type of the None singleton.

<a id="TransactionInFilter"></a>

`TransactionInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: list[int]`
    :   The total amount of the transaction.

    `amount_capturable: list[int]`
    :   The remaining amount that can be captured in the transaction.

    `amount_unused: list[int]`
    :   The amount in the transaction that remains unused.

    `authorization_reason: list[str]`
    :   Reason for authorization of the transaction.

    `base_currency_code: list[str]`
    :   The base currency code of the transaction.

    `business_entity_id: list[str]`
    :   The ID of the business entity related to the transaction.

    `cn_create_reason_code: list[str]`
    :   Reason code for creating a credit note.

    `cn_date: list[int]`
    :   Date of the credit note.

    `cn_reference_invoice_id: list[str]`
    :   ID of the invoice referenced in the credit note.

    `cn_status: list[str]`
    :   Status of the credit note.

    `cn_total: list[int]`
    :   Total amount of the credit note.

    `currency_code: list[str]`
    :   The currency code of the transaction.

    `custom_fields: list[list[typing.Any]]`
    :   The type of the None singleton.

    `customer_id: list[str]`
    :   The ID of the customer associated with the transaction.

    `date: list[int]`
    :   Date of the transaction.

    `deleted: list[bool]`
    :   Flag indicating if the transaction is deleted.

    `error_code: list[str]`
    :   Error code associated with the transaction.

    `error_detail: list[str]`
    :   Detailed error information related to the transaction.

    `error_text: list[str]`
    :   Error message text of the transaction.

    `exchange_rate: list[float]`
    :   Exchange rate used in the transaction.

    `fraud_flag: list[str]`
    :   Flag indicating if the transaction is flagged for fraud.

    `fraud_reason: list[str]`
    :   Reason for flagging the transaction as fraud.

    `gateway: list[str]`
    :   The payment gateway used in the transaction.

    `gateway_account_id: list[str]`
    :   ID of the gateway account used in the transaction.

    `id: list[str]`
    :   Unique identifier of the transaction.

    `id_at_gateway: list[str]`
    :   Transaction ID assigned by the gateway.

    `iin: list[str]`
    :   Bank identification number of the transaction.

    `initiator_type: list[str]`
    :   Type of initiator involved in the transaction.

    `last4: list[str]`
    :   Last 4 digits of the card used in the transaction.

    `linked_credit_notes: list[list[typing.Any]]`
    :   Linked credit notes associated with the transaction.

    `linked_invoices: list[list[typing.Any]]`
    :   Linked invoices associated with the transaction.

    `linked_payments: list[list[typing.Any]]`
    :   Linked payments associated with the transaction.

    `linked_refunds: list[list[typing.Any]]`
    :   Linked refunds associated with the transaction.

    `masked_card_number: list[str]`
    :   Masked card number used in the transaction.

    `merchant_reference_id: list[str]`
    :   Merchant reference ID of the transaction.

    `object_: list[str]`
    :   Type of object representing the transaction.

    `payment_method: list[str]`
    :   Payment method used in the transaction.

    `payment_method_details: list[str]`
    :   Details of the payment method used in the transaction.

    `payment_source_id: list[str]`
    :   ID of the payment source used in the transaction.

    `reference_authorization_id: list[str]`
    :   Reference authorization ID of the transaction.

    `reference_number: list[str]`
    :   Reference number associated with the transaction.

    `reference_transaction_id: list[str]`
    :   ID of the reference transaction.

    `refrence_number: list[str]`
    :   Reference number of the transaction.

    `refunded_txn_id: list[str]`
    :   ID of the refunded transaction.

    `resource_version: list[int]`
    :   Resource version of the transaction.

    `reversal_transaction_id: list[str]`
    :   ID of the reversal transaction, if any.

    `settled_at: list[int]`
    :   Date when the transaction was settled.

    `status: list[str]`
    :   Status of the transaction.

    `subscription_id: list[str]`
    :   ID of the subscription related to the transaction.

    `three_d_secure: list[bool]`
    :   Flag indicating if 3D secure was used in the transaction.

    `txn_amount: list[int]`
    :   Amount of the transaction.

    `txn_date: list[int]`
    :   Date of the transaction.

    `type_: list[str]`
    :   Type of the transaction.

    `updated_at: list[int]`
    :   Date when the transaction was last updated.

    `voided_at: list[int]`
    :   Date when the transaction was voided.

<a id="TransactionKeywordCondition"></a>

`TransactionKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.chargebee.types.TransactionStringFilter`
    :   The type of the None singleton.

<a id="TransactionLikeCondition"></a>

`TransactionLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.chargebee.types.TransactionStringFilter`
    :   The type of the None singleton.

<a id="TransactionListParams"></a>

`TransactionListParams(*args, **kwargs)`
:   Parameters for transaction.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

<a id="TransactionLtCondition"></a>

`TransactionLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.chargebee.types.TransactionSearchFilter`
    :   The type of the None singleton.

<a id="TransactionLteCondition"></a>

`TransactionLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.chargebee.types.TransactionSearchFilter`
    :   The type of the None singleton.

<a id="TransactionNeqCondition"></a>

`TransactionNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.chargebee.types.TransactionSearchFilter`
    :   The type of the None singleton.

<a id="TransactionNotCondition"></a>

`TransactionNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.chargebee.types.TransactionEqCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionGtCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionGteCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionLtCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionLteCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionInCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionNotCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionAndCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionOrCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionAnyCondition`
    :   The type of the None singleton.

<a id="TransactionOrCondition"></a>

`TransactionOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.chargebee.types.TransactionEqCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionGtCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionGteCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionLtCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionLteCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionInCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionNotCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionAndCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionOrCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionAnyCondition]`
    :   The type of the None singleton.

<a id="TransactionSearchFilter"></a>

`TransactionSearchFilter(*args, **kwargs)`
:   Available fields for filtering transaction search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="TransactionSearchQuery"></a>

`TransactionSearchQuery(*args, **kwargs)`
:   Search query for transaction entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.chargebee.types.TransactionEqCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionNeqCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionGtCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionGteCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionLtCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionLteCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionInCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionLikeCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionFuzzyCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionKeywordCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionContainsCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionNotCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionAndCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionOrCondition | airbyte_agent_sdk.connectors.chargebee.types.TransactionAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.chargebee.types.TransactionSortFilter]`
    :   The type of the None singleton.

<a id="TransactionSortFilter"></a>

`TransactionSortFilter(*args, **kwargs)`
:   Available fields for sorting transaction search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Literal['asc', 'desc']`
    :   The total amount of the transaction.

    `amount_capturable: Literal['asc', 'desc']`
    :   The remaining amount that can be captured in the transaction.

    `amount_unused: Literal['asc', 'desc']`
    :   The amount in the transaction that remains unused.

    `authorization_reason: Literal['asc', 'desc']`
    :   Reason for authorization of the transaction.

    `base_currency_code: Literal['asc', 'desc']`
    :   The base currency code of the transaction.

    `business_entity_id: Literal['asc', 'desc']`
    :   The ID of the business entity related to the transaction.

    `cn_create_reason_code: Literal['asc', 'desc']`
    :   Reason code for creating a credit note.

    `cn_date: Literal['asc', 'desc']`
    :   Date of the credit note.

    `cn_reference_invoice_id: Literal['asc', 'desc']`
    :   ID of the invoice referenced in the credit note.

    `cn_status: Literal['asc', 'desc']`
    :   Status of the credit note.

    `cn_total: Literal['asc', 'desc']`
    :   Total amount of the credit note.

    `currency_code: Literal['asc', 'desc']`
    :   The currency code of the transaction.

    `custom_fields: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `customer_id: Literal['asc', 'desc']`
    :   The ID of the customer associated with the transaction.

    `date: Literal['asc', 'desc']`
    :   Date of the transaction.

    `deleted: Literal['asc', 'desc']`
    :   Flag indicating if the transaction is deleted.

    `error_code: Literal['asc', 'desc']`
    :   Error code associated with the transaction.

    `error_detail: Literal['asc', 'desc']`
    :   Detailed error information related to the transaction.

    `error_text: Literal['asc', 'desc']`
    :   Error message text of the transaction.

    `exchange_rate: Literal['asc', 'desc']`
    :   Exchange rate used in the transaction.

    `fraud_flag: Literal['asc', 'desc']`
    :   Flag indicating if the transaction is flagged for fraud.

    `fraud_reason: Literal['asc', 'desc']`
    :   Reason for flagging the transaction as fraud.

    `gateway: Literal['asc', 'desc']`
    :   The payment gateway used in the transaction.

    `gateway_account_id: Literal['asc', 'desc']`
    :   ID of the gateway account used in the transaction.

    `id: Literal['asc', 'desc']`
    :   Unique identifier of the transaction.

    `id_at_gateway: Literal['asc', 'desc']`
    :   Transaction ID assigned by the gateway.

    `iin: Literal['asc', 'desc']`
    :   Bank identification number of the transaction.

    `initiator_type: Literal['asc', 'desc']`
    :   Type of initiator involved in the transaction.

    `last4: Literal['asc', 'desc']`
    :   Last 4 digits of the card used in the transaction.

    `linked_credit_notes: Literal['asc', 'desc']`
    :   Linked credit notes associated with the transaction.

    `linked_invoices: Literal['asc', 'desc']`
    :   Linked invoices associated with the transaction.

    `linked_payments: Literal['asc', 'desc']`
    :   Linked payments associated with the transaction.

    `linked_refunds: Literal['asc', 'desc']`
    :   Linked refunds associated with the transaction.

    `masked_card_number: Literal['asc', 'desc']`
    :   Masked card number used in the transaction.

    `merchant_reference_id: Literal['asc', 'desc']`
    :   Merchant reference ID of the transaction.

    `object_: Literal['asc', 'desc']`
    :   Type of object representing the transaction.

    `payment_method: Literal['asc', 'desc']`
    :   Payment method used in the transaction.

    `payment_method_details: Literal['asc', 'desc']`
    :   Details of the payment method used in the transaction.

    `payment_source_id: Literal['asc', 'desc']`
    :   ID of the payment source used in the transaction.

    `reference_authorization_id: Literal['asc', 'desc']`
    :   Reference authorization ID of the transaction.

    `reference_number: Literal['asc', 'desc']`
    :   Reference number associated with the transaction.

    `reference_transaction_id: Literal['asc', 'desc']`
    :   ID of the reference transaction.

    `refrence_number: Literal['asc', 'desc']`
    :   Reference number of the transaction.

    `refunded_txn_id: Literal['asc', 'desc']`
    :   ID of the refunded transaction.

    `resource_version: Literal['asc', 'desc']`
    :   Resource version of the transaction.

    `reversal_transaction_id: Literal['asc', 'desc']`
    :   ID of the reversal transaction, if any.

    `settled_at: Literal['asc', 'desc']`
    :   Date when the transaction was settled.

    `status: Literal['asc', 'desc']`
    :   Status of the transaction.

    `subscription_id: Literal['asc', 'desc']`
    :   ID of the subscription related to the transaction.

    `three_d_secure: Literal['asc', 'desc']`
    :   Flag indicating if 3D secure was used in the transaction.

    `txn_amount: Literal['asc', 'desc']`
    :   Amount of the transaction.

    `txn_date: Literal['asc', 'desc']`
    :   Date of the transaction.

    `type_: Literal['asc', 'desc']`
    :   Type of the transaction.

    `updated_at: Literal['asc', 'desc']`
    :   Date when the transaction was last updated.

    `voided_at: Literal['asc', 'desc']`
    :   Date when the transaction was voided.

<a id="TransactionStringFilter"></a>

`TransactionStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   The total amount of the transaction.

    `amount_capturable: str`
    :   The remaining amount that can be captured in the transaction.

    `amount_unused: str`
    :   The amount in the transaction that remains unused.

    `authorization_reason: str`
    :   Reason for authorization of the transaction.

    `base_currency_code: str`
    :   The base currency code of the transaction.

    `business_entity_id: str`
    :   The ID of the business entity related to the transaction.

    `cn_create_reason_code: str`
    :   Reason code for creating a credit note.

    `cn_date: str`
    :   Date of the credit note.

    `cn_reference_invoice_id: str`
    :   ID of the invoice referenced in the credit note.

    `cn_status: str`
    :   Status of the credit note.

    `cn_total: str`
    :   Total amount of the credit note.

    `currency_code: str`
    :   The currency code of the transaction.

    `custom_fields: str`
    :   The type of the None singleton.

    `customer_id: str`
    :   The ID of the customer associated with the transaction.

    `date: str`
    :   Date of the transaction.

    `deleted: str`
    :   Flag indicating if the transaction is deleted.

    `error_code: str`
    :   Error code associated with the transaction.

    `error_detail: str`
    :   Detailed error information related to the transaction.

    `error_text: str`
    :   Error message text of the transaction.

    `exchange_rate: str`
    :   Exchange rate used in the transaction.

    `fraud_flag: str`
    :   Flag indicating if the transaction is flagged for fraud.

    `fraud_reason: str`
    :   Reason for flagging the transaction as fraud.

    `gateway: str`
    :   The payment gateway used in the transaction.

    `gateway_account_id: str`
    :   ID of the gateway account used in the transaction.

    `id: str`
    :   Unique identifier of the transaction.

    `id_at_gateway: str`
    :   Transaction ID assigned by the gateway.

    `iin: str`
    :   Bank identification number of the transaction.

    `initiator_type: str`
    :   Type of initiator involved in the transaction.

    `last4: str`
    :   Last 4 digits of the card used in the transaction.

    `linked_credit_notes: str`
    :   Linked credit notes associated with the transaction.

    `linked_invoices: str`
    :   Linked invoices associated with the transaction.

    `linked_payments: str`
    :   Linked payments associated with the transaction.

    `linked_refunds: str`
    :   Linked refunds associated with the transaction.

    `masked_card_number: str`
    :   Masked card number used in the transaction.

    `merchant_reference_id: str`
    :   Merchant reference ID of the transaction.

    `object_: str`
    :   Type of object representing the transaction.

    `payment_method: str`
    :   Payment method used in the transaction.

    `payment_method_details: str`
    :   Details of the payment method used in the transaction.

    `payment_source_id: str`
    :   ID of the payment source used in the transaction.

    `reference_authorization_id: str`
    :   Reference authorization ID of the transaction.

    `reference_number: str`
    :   Reference number associated with the transaction.

    `reference_transaction_id: str`
    :   ID of the reference transaction.

    `refrence_number: str`
    :   Reference number of the transaction.

    `refunded_txn_id: str`
    :   ID of the refunded transaction.

    `resource_version: str`
    :   Resource version of the transaction.

    `reversal_transaction_id: str`
    :   ID of the reversal transaction, if any.

    `settled_at: str`
    :   Date when the transaction was settled.

    `status: str`
    :   Status of the transaction.

    `subscription_id: str`
    :   ID of the subscription related to the transaction.

    `three_d_secure: str`
    :   Flag indicating if 3D secure was used in the transaction.

    `txn_amount: str`
    :   Amount of the transaction.

    `txn_date: str`
    :   Date of the transaction.

    `type_: str`
    :   Type of the transaction.

    `updated_at: str`
    :   Date when the transaction was last updated.

    `voided_at: str`
    :   Date when the transaction was voided.