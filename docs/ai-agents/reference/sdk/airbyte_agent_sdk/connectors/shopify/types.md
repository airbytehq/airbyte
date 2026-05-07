---
id: airbyte_agent_sdk-connectors-shopify-types
title: airbyte_agent_sdk.connectors.shopify.types
---

Module airbyte_agent_sdk.connectors.shopify.types
=================================================
Type definitions for shopify connector.

Classes
-------

<a id="AbandonedCheckoutsAndCondition"></a>

`AbandonedCheckoutsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsEqCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsGtCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsGteCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLtCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLteCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsInCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsNotCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsAndCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsOrCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsAnyCondition]`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsAnyCondition"></a>

`AbandonedCheckoutsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsAnyValueFilter`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsAnyValueFilter"></a>

`AbandonedCheckoutsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `completed_at: Any`
    :   ISO 8601 timestamp when the checkout was completed, if applicable

    `created_at: Any`
    :   ISO 8601 timestamp when the checkout was created

    `currency: Any`
    :   ISO 4217 currency code for the checkout totals

    `email: Any`
    :   Email address provided for the checkout

    `id: Any`
    :   Unique identifier for the abandoned checkout

    `name: Any`
    :   Shopify-assigned display name for the checkout (e.g. `#C12345`)

    `phone: Any`
    :   Phone number provided for the checkout

    `token: Any`
    :   Unique token identifying the checkout

    `total_price: Any`
    :   Total price of the checkout in the shop's currency

    `updated_at: Any`
    :   ISO 8601 timestamp when the checkout was last updated

<a id="AbandonedCheckoutsContainsCondition"></a>

`AbandonedCheckoutsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsAnyValueFilter`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsEqCondition"></a>

`AbandonedCheckoutsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsSearchFilter`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsFuzzyCondition"></a>

`AbandonedCheckoutsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsStringFilter`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsGtCondition"></a>

`AbandonedCheckoutsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsSearchFilter`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsGteCondition"></a>

`AbandonedCheckoutsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsSearchFilter`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsInCondition"></a>

`AbandonedCheckoutsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsInFilter`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsInFilter"></a>

`AbandonedCheckoutsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `completed_at: list[str]`
    :   ISO 8601 timestamp when the checkout was completed, if applicable

    `created_at: list[str]`
    :   ISO 8601 timestamp when the checkout was created

    `currency: list[str]`
    :   ISO 4217 currency code for the checkout totals

    `email: list[str]`
    :   Email address provided for the checkout

    `id: list[int]`
    :   Unique identifier for the abandoned checkout

    `name: list[str]`
    :   Shopify-assigned display name for the checkout (e.g. `#C12345`)

    `phone: list[str]`
    :   Phone number provided for the checkout

    `token: list[str]`
    :   Unique token identifying the checkout

    `total_price: list[str]`
    :   Total price of the checkout in the shop's currency

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the checkout was last updated

<a id="AbandonedCheckoutsKeywordCondition"></a>

`AbandonedCheckoutsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsStringFilter`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsLikeCondition"></a>

`AbandonedCheckoutsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsStringFilter`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsListParams"></a>

`AbandonedCheckoutsListParams(*args, **kwargs)`
:   Parameters for abandoned_checkouts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at_max: str`
    :   The type of the None singleton.

    `created_at_min: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `updated_at_max: str`
    :   The type of the None singleton.

    `updated_at_min: str`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsLtCondition"></a>

`AbandonedCheckoutsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsSearchFilter`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsLteCondition"></a>

`AbandonedCheckoutsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsSearchFilter`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsNeqCondition"></a>

`AbandonedCheckoutsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsSearchFilter`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsNotCondition"></a>

`AbandonedCheckoutsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsEqCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsGtCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsGteCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLtCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLteCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsInCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsNotCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsAndCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsOrCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsAnyCondition`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsOrCondition"></a>

`AbandonedCheckoutsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsEqCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsGtCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsGteCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLtCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLteCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsInCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsNotCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsAndCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsOrCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsAnyCondition]`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsSearchFilter"></a>

`AbandonedCheckoutsSearchFilter(*args, **kwargs)`
:   Available fields for filtering abandoned_checkouts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="AbandonedCheckoutsSearchQuery"></a>

`AbandonedCheckoutsSearchQuery(*args, **kwargs)`
:   Search query for abandoned_checkouts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsEqCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsGtCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsGteCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLtCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLteCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsInCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsNotCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsAndCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsOrCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsSortFilter]`
    :   The type of the None singleton.

<a id="AbandonedCheckoutsSortFilter"></a>

`AbandonedCheckoutsSortFilter(*args, **kwargs)`
:   Available fields for sorting abandoned_checkouts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `completed_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the checkout was completed, if applicable

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the checkout was created

    `currency: Literal['asc', 'desc']`
    :   ISO 4217 currency code for the checkout totals

    `email: Literal['asc', 'desc']`
    :   Email address provided for the checkout

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the abandoned checkout

    `name: Literal['asc', 'desc']`
    :   Shopify-assigned display name for the checkout (e.g. `#C12345`)

    `phone: Literal['asc', 'desc']`
    :   Phone number provided for the checkout

    `token: Literal['asc', 'desc']`
    :   Unique token identifying the checkout

    `total_price: Literal['asc', 'desc']`
    :   Total price of the checkout in the shop's currency

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the checkout was last updated

<a id="AbandonedCheckoutsStringFilter"></a>

`AbandonedCheckoutsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `completed_at: str`
    :   ISO 8601 timestamp when the checkout was completed, if applicable

    `created_at: str`
    :   ISO 8601 timestamp when the checkout was created

    `currency: str`
    :   ISO 4217 currency code for the checkout totals

    `email: str`
    :   Email address provided for the checkout

    `id: str`
    :   Unique identifier for the abandoned checkout

    `name: str`
    :   Shopify-assigned display name for the checkout (e.g. `#C12345`)

    `phone: str`
    :   Phone number provided for the checkout

    `token: str`
    :   Unique token identifying the checkout

    `total_price: str`
    :   Total price of the checkout in the shop's currency

    `updated_at: str`
    :   ISO 8601 timestamp when the checkout was last updated

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

<a id="CollectsAndCondition"></a>

`CollectsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.CollectsEqCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsGtCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsGteCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLtCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLteCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsInCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsNotCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsAndCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsOrCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsAnyCondition]`
    :   The type of the None singleton.

<a id="CollectsAnyCondition"></a>

`CollectsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.CollectsAnyValueFilter`
    :   The type of the None singleton.

<a id="CollectsAnyValueFilter"></a>

`CollectsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_id: Any`
    :   Identifier of the collection the product belongs to

    `created_at: Any`
    :   ISO 8601 timestamp when the collect was created

    `id: Any`
    :   Unique identifier for the collect

    `position: Any`
    :   Position of the product within the collection

    `product_id: Any`
    :   Identifier of the product in the collection

    `updated_at: Any`
    :   ISO 8601 timestamp when the collect was last updated

<a id="CollectsContainsCondition"></a>

`CollectsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.CollectsAnyValueFilter`
    :   The type of the None singleton.

<a id="CollectsEqCondition"></a>

`CollectsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.CollectsSearchFilter`
    :   The type of the None singleton.

<a id="CollectsFuzzyCondition"></a>

`CollectsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.CollectsStringFilter`
    :   The type of the None singleton.

<a id="CollectsGetParams"></a>

`CollectsGetParams(*args, **kwargs)`
:   Parameters for collects.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collect_id: str`
    :   The type of the None singleton.

<a id="CollectsGtCondition"></a>

`CollectsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.CollectsSearchFilter`
    :   The type of the None singleton.

<a id="CollectsGteCondition"></a>

`CollectsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.CollectsSearchFilter`
    :   The type of the None singleton.

<a id="CollectsInCondition"></a>

`CollectsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.CollectsInFilter`
    :   The type of the None singleton.

<a id="CollectsInFilter"></a>

`CollectsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_id: list[int]`
    :   Identifier of the collection the product belongs to

    `created_at: list[str]`
    :   ISO 8601 timestamp when the collect was created

    `id: list[int]`
    :   Unique identifier for the collect

    `position: list[int]`
    :   Position of the product within the collection

    `product_id: list[int]`
    :   Identifier of the product in the collection

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the collect was last updated

<a id="CollectsKeywordCondition"></a>

`CollectsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.CollectsStringFilter`
    :   The type of the None singleton.

<a id="CollectsLikeCondition"></a>

`CollectsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.CollectsStringFilter`
    :   The type of the None singleton.

<a id="CollectsListParams"></a>

`CollectsListParams(*args, **kwargs)`
:   Parameters for collects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_id: int`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `product_id: int`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

<a id="CollectsLtCondition"></a>

`CollectsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.CollectsSearchFilter`
    :   The type of the None singleton.

<a id="CollectsLteCondition"></a>

`CollectsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.CollectsSearchFilter`
    :   The type of the None singleton.

<a id="CollectsNeqCondition"></a>

`CollectsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.CollectsSearchFilter`
    :   The type of the None singleton.

<a id="CollectsNotCondition"></a>

`CollectsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.CollectsEqCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsGtCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsGteCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLtCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLteCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsInCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsNotCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsAndCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsOrCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsAnyCondition`
    :   The type of the None singleton.

<a id="CollectsOrCondition"></a>

`CollectsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.CollectsEqCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsGtCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsGteCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLtCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLteCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsInCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsNotCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsAndCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsOrCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsAnyCondition]`
    :   The type of the None singleton.

<a id="CollectsSearchFilter"></a>

`CollectsSearchFilter(*args, **kwargs)`
:   Available fields for filtering collects search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_id: int | None`
    :   Identifier of the collection the product belongs to

    `created_at: str | None`
    :   ISO 8601 timestamp when the collect was created

    `id: int | None`
    :   Unique identifier for the collect

    `position: int | None`
    :   Position of the product within the collection

    `product_id: int | None`
    :   Identifier of the product in the collection

    `updated_at: str | None`
    :   ISO 8601 timestamp when the collect was last updated

<a id="CollectsSearchQuery"></a>

`CollectsSearchQuery(*args, **kwargs)`
:   Search query for collects entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.CollectsEqCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsGtCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsGteCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLtCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLteCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsInCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsNotCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsAndCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsOrCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.CollectsSortFilter]`
    :   The type of the None singleton.

<a id="CollectsSortFilter"></a>

`CollectsSortFilter(*args, **kwargs)`
:   Available fields for sorting collects search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_id: Literal['asc', 'desc']`
    :   Identifier of the collection the product belongs to

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the collect was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the collect

    `position: Literal['asc', 'desc']`
    :   Position of the product within the collection

    `product_id: Literal['asc', 'desc']`
    :   Identifier of the product in the collection

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the collect was last updated

<a id="CollectsStringFilter"></a>

`CollectsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_id: str`
    :   Identifier of the collection the product belongs to

    `created_at: str`
    :   ISO 8601 timestamp when the collect was created

    `id: str`
    :   Unique identifier for the collect

    `position: str`
    :   Position of the product within the collection

    `product_id: str`
    :   Identifier of the product in the collection

    `updated_at: str`
    :   ISO 8601 timestamp when the collect was last updated

<a id="CountriesAndCondition"></a>

`CountriesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.CountriesEqCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesGtCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesGteCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLtCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLteCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesInCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesNotCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesAndCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesOrCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesAnyCondition]`
    :   The type of the None singleton.

<a id="CountriesAnyCondition"></a>

`CountriesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.CountriesAnyValueFilter`
    :   The type of the None singleton.

<a id="CountriesAnyValueFilter"></a>

`CountriesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `code: Any`
    :   ISO 3166-1 alpha-2 country code

    `id: Any`
    :   Unique identifier for the country tax row

    `name: Any`
    :   Human-readable country name

    `tax_name: Any`
    :   Localized name of the tax applied in this country

<a id="CountriesContainsCondition"></a>

`CountriesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.CountriesAnyValueFilter`
    :   The type of the None singleton.

<a id="CountriesEqCondition"></a>

`CountriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.CountriesSearchFilter`
    :   The type of the None singleton.

<a id="CountriesFuzzyCondition"></a>

`CountriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.CountriesStringFilter`
    :   The type of the None singleton.

<a id="CountriesGetParams"></a>

`CountriesGetParams(*args, **kwargs)`
:   Parameters for countries.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country_id: str`
    :   The type of the None singleton.

<a id="CountriesGtCondition"></a>

`CountriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.CountriesSearchFilter`
    :   The type of the None singleton.

<a id="CountriesGteCondition"></a>

`CountriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.CountriesSearchFilter`
    :   The type of the None singleton.

<a id="CountriesInCondition"></a>

`CountriesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.CountriesInFilter`
    :   The type of the None singleton.

<a id="CountriesInFilter"></a>

`CountriesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `code: list[str]`
    :   ISO 3166-1 alpha-2 country code

    `id: list[int]`
    :   Unique identifier for the country tax row

    `name: list[str]`
    :   Human-readable country name

    `tax_name: list[str]`
    :   Localized name of the tax applied in this country

<a id="CountriesKeywordCondition"></a>

`CountriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.CountriesStringFilter`
    :   The type of the None singleton.

<a id="CountriesLikeCondition"></a>

`CountriesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.CountriesStringFilter`
    :   The type of the None singleton.

<a id="CountriesListParams"></a>

`CountriesListParams(*args, **kwargs)`
:   Parameters for countries.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `since_id: int`
    :   The type of the None singleton.

<a id="CountriesLtCondition"></a>

`CountriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.CountriesSearchFilter`
    :   The type of the None singleton.

<a id="CountriesLteCondition"></a>

`CountriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.CountriesSearchFilter`
    :   The type of the None singleton.

<a id="CountriesNeqCondition"></a>

`CountriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.CountriesSearchFilter`
    :   The type of the None singleton.

<a id="CountriesNotCondition"></a>

`CountriesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.CountriesEqCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesGtCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesGteCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLtCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLteCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesInCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesNotCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesAndCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesOrCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesAnyCondition`
    :   The type of the None singleton.

<a id="CountriesOrCondition"></a>

`CountriesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.CountriesEqCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesGtCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesGteCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLtCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLteCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesInCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesNotCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesAndCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesOrCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesAnyCondition]`
    :   The type of the None singleton.

<a id="CountriesSearchFilter"></a>

`CountriesSearchFilter(*args, **kwargs)`
:   Available fields for filtering countries search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `code: str | None`
    :   ISO 3166-1 alpha-2 country code

    `id: int | None`
    :   Unique identifier for the country tax row

    `name: str | None`
    :   Human-readable country name

    `tax_name: str | None`
    :   Localized name of the tax applied in this country

<a id="CountriesSearchQuery"></a>

`CountriesSearchQuery(*args, **kwargs)`
:   Search query for countries entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.CountriesEqCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesGtCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesGteCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLtCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLteCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesInCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesNotCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesAndCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesOrCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.CountriesSortFilter]`
    :   The type of the None singleton.

<a id="CountriesSortFilter"></a>

`CountriesSortFilter(*args, **kwargs)`
:   Available fields for sorting countries search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `code: Literal['asc', 'desc']`
    :   ISO 3166-1 alpha-2 country code

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the country tax row

    `name: Literal['asc', 'desc']`
    :   Human-readable country name

    `tax_name: Literal['asc', 'desc']`
    :   Localized name of the tax applied in this country

<a id="CountriesStringFilter"></a>

`CountriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `code: str`
    :   ISO 3166-1 alpha-2 country code

    `id: str`
    :   Unique identifier for the country tax row

    `name: str`
    :   Human-readable country name

    `tax_name: str`
    :   Localized name of the tax applied in this country

<a id="CustomCollectionsAndCondition"></a>

`CustomCollectionsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsAnyCondition]`
    :   The type of the None singleton.

<a id="CustomCollectionsAnyCondition"></a>

`CustomCollectionsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomCollectionsAnyValueFilter"></a>

`CustomCollectionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `handle: Any`
    :   URL-friendly handle for the custom collection

    `id: Any`
    :   Unique identifier for the custom collection

    `published_at: Any`
    :   ISO 8601 timestamp when the collection was published

    `published_scope: Any`
    :   Publishing scope (`web` or `global`)

    `sort_order: Any`
    :   How products are sorted within the collection (e.g. `best-selling`)

    `title: Any`
    :   Display title of the custom collection

    `updated_at: Any`
    :   ISO 8601 timestamp when the collection was last updated

<a id="CustomCollectionsContainsCondition"></a>

`CustomCollectionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomCollectionsEqCondition"></a>

`CustomCollectionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="CustomCollectionsFuzzyCondition"></a>

`CustomCollectionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsStringFilter`
    :   The type of the None singleton.

<a id="CustomCollectionsGetParams"></a>

`CustomCollectionsGetParams(*args, **kwargs)`
:   Parameters for custom_collections.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_id: str`
    :   The type of the None singleton.

<a id="CustomCollectionsGtCondition"></a>

`CustomCollectionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="CustomCollectionsGteCondition"></a>

`CustomCollectionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="CustomCollectionsInCondition"></a>

`CustomCollectionsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsInFilter`
    :   The type of the None singleton.

<a id="CustomCollectionsInFilter"></a>

`CustomCollectionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `handle: list[str]`
    :   URL-friendly handle for the custom collection

    `id: list[int]`
    :   Unique identifier for the custom collection

    `published_at: list[str]`
    :   ISO 8601 timestamp when the collection was published

    `published_scope: list[str]`
    :   Publishing scope (`web` or `global`)

    `sort_order: list[str]`
    :   How products are sorted within the collection (e.g. `best-selling`)

    `title: list[str]`
    :   Display title of the custom collection

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the collection was last updated

<a id="CustomCollectionsKeywordCondition"></a>

`CustomCollectionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsStringFilter`
    :   The type of the None singleton.

<a id="CustomCollectionsLikeCondition"></a>

`CustomCollectionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsStringFilter`
    :   The type of the None singleton.

<a id="CustomCollectionsListParams"></a>

`CustomCollectionsListParams(*args, **kwargs)`
:   Parameters for custom_collections.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `product_id: int`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

    `updated_at_max: str`
    :   The type of the None singleton.

    `updated_at_min: str`
    :   The type of the None singleton.

<a id="CustomCollectionsLtCondition"></a>

`CustomCollectionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="CustomCollectionsLteCondition"></a>

`CustomCollectionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="CustomCollectionsNeqCondition"></a>

`CustomCollectionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="CustomCollectionsNotCondition"></a>

`CustomCollectionsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsAnyCondition`
    :   The type of the None singleton.

<a id="CustomCollectionsOrCondition"></a>

`CustomCollectionsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsAnyCondition]`
    :   The type of the None singleton.

<a id="CustomCollectionsSearchFilter"></a>

`CustomCollectionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering custom_collections search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `handle: str | None`
    :   URL-friendly handle for the custom collection

    `id: int | None`
    :   Unique identifier for the custom collection

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

<a id="CustomCollectionsSearchQuery"></a>

`CustomCollectionsSearchQuery(*args, **kwargs)`
:   Search query for custom_collections entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsSortFilter]`
    :   The type of the None singleton.

<a id="CustomCollectionsSortFilter"></a>

`CustomCollectionsSortFilter(*args, **kwargs)`
:   Available fields for sorting custom_collections search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `handle: Literal['asc', 'desc']`
    :   URL-friendly handle for the custom collection

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the custom collection

    `published_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the collection was published

    `published_scope: Literal['asc', 'desc']`
    :   Publishing scope (`web` or `global`)

    `sort_order: Literal['asc', 'desc']`
    :   How products are sorted within the collection (e.g. `best-selling`)

    `title: Literal['asc', 'desc']`
    :   Display title of the custom collection

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the collection was last updated

<a id="CustomCollectionsStringFilter"></a>

`CustomCollectionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `handle: str`
    :   URL-friendly handle for the custom collection

    `id: str`
    :   Unique identifier for the custom collection

    `published_at: str`
    :   ISO 8601 timestamp when the collection was published

    `published_scope: str`
    :   Publishing scope (`web` or `global`)

    `sort_order: str`
    :   How products are sorted within the collection (e.g. `best-selling`)

    `title: str`
    :   Display title of the custom collection

    `updated_at: str`
    :   ISO 8601 timestamp when the collection was last updated

<a id="CustomerAddressGetParams"></a>

`CustomerAddressGetParams(*args, **kwargs)`
:   Parameters for customer_address.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address_id: str`
    :   The type of the None singleton.

    `customer_id: str`
    :   The type of the None singleton.

<a id="CustomerAddressListParams"></a>

`CustomerAddressListParams(*args, **kwargs)`
:   Parameters for customer_address.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.CustomersEqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersGtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersGteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersInCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersNotCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersAndCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersOrCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.CustomersAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomersAnyValueFilter"></a>

`CustomersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the customer record was created

    `currency: Any`
    :   ISO 4217 currency code for the customer's total spend

    `email: Any`
    :   Primary email address of the customer

    `first_name: Any`
    :   First name of the customer

    `id: Any`
    :   Unique identifier for the customer

    `last_name: Any`
    :   Last name of the customer

    `orders_count: Any`
    :   Number of orders placed by the customer

    `phone: Any`
    :   Primary phone number of the customer

    `state: Any`
    :   Account state (`disabled`, `invited`, `enabled`, `declined`)

    `total_spent: Any`
    :   Total lifetime amount spent by the customer

    `updated_at: Any`
    :   ISO 8601 timestamp when the customer record was last updated

<a id="CustomersContainsCondition"></a>

`CustomersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.CustomersAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomersEqCondition"></a>

`CustomersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersFuzzyCondition"></a>

`CustomersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.CustomersStringFilter`
    :   The type of the None singleton.

<a id="CustomersGetParams"></a>

`CustomersGetParams(*args, **kwargs)`
:   Parameters for customers.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

<a id="CustomersGtCondition"></a>

`CustomersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersGteCondition"></a>

`CustomersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.CustomersSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.CustomersInFilter`
    :   The type of the None singleton.

<a id="CustomersInFilter"></a>

`CustomersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the customer record was created

    `currency: list[str]`
    :   ISO 4217 currency code for the customer's total spend

    `email: list[str]`
    :   Primary email address of the customer

    `first_name: list[str]`
    :   First name of the customer

    `id: list[int]`
    :   Unique identifier for the customer

    `last_name: list[str]`
    :   Last name of the customer

    `orders_count: list[int]`
    :   Number of orders placed by the customer

    `phone: list[str]`
    :   Primary phone number of the customer

    `state: list[str]`
    :   Account state (`disabled`, `invited`, `enabled`, `declined`)

    `total_spent: list[str]`
    :   Total lifetime amount spent by the customer

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the customer record was last updated

<a id="CustomersKeywordCondition"></a>

`CustomersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.CustomersStringFilter`
    :   The type of the None singleton.

<a id="CustomersLikeCondition"></a>

`CustomersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.CustomersStringFilter`
    :   The type of the None singleton.

<a id="CustomersListParams"></a>

`CustomersListParams(*args, **kwargs)`
:   Parameters for customers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at_max: str`
    :   The type of the None singleton.

    `created_at_min: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

    `updated_at_max: str`
    :   The type of the None singleton.

    `updated_at_min: str`
    :   The type of the None singleton.

<a id="CustomersLtCondition"></a>

`CustomersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersLteCondition"></a>

`CustomersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersNeqCondition"></a>

`CustomersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.CustomersSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.CustomersEqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersGtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersGteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersInCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersNotCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersAndCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersOrCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.CustomersEqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersGtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersGteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersInCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersNotCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersAndCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersOrCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersAnyCondition]`
    :   The type of the None singleton.

<a id="CustomersSearchFilter"></a>

`CustomersSearchFilter(*args, **kwargs)`
:   Available fields for filtering customers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CustomersSearchQuery"></a>

`CustomersSearchQuery(*args, **kwargs)`
:   Search query for customers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.CustomersEqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersGtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersGteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersInCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersNotCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersAndCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersOrCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.CustomersSortFilter]`
    :   The type of the None singleton.

<a id="CustomersSortFilter"></a>

`CustomersSortFilter(*args, **kwargs)`
:   Available fields for sorting customers search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the customer record was created

    `currency: Literal['asc', 'desc']`
    :   ISO 4217 currency code for the customer's total spend

    `email: Literal['asc', 'desc']`
    :   Primary email address of the customer

    `first_name: Literal['asc', 'desc']`
    :   First name of the customer

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the customer

    `last_name: Literal['asc', 'desc']`
    :   Last name of the customer

    `orders_count: Literal['asc', 'desc']`
    :   Number of orders placed by the customer

    `phone: Literal['asc', 'desc']`
    :   Primary phone number of the customer

    `state: Literal['asc', 'desc']`
    :   Account state (`disabled`, `invited`, `enabled`, `declined`)

    `total_spent: Literal['asc', 'desc']`
    :   Total lifetime amount spent by the customer

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the customer record was last updated

<a id="CustomersStringFilter"></a>

`CustomersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the customer record was created

    `currency: str`
    :   ISO 4217 currency code for the customer's total spend

    `email: str`
    :   Primary email address of the customer

    `first_name: str`
    :   First name of the customer

    `id: str`
    :   Unique identifier for the customer

    `last_name: str`
    :   Last name of the customer

    `orders_count: str`
    :   Number of orders placed by the customer

    `phone: str`
    :   Primary phone number of the customer

    `state: str`
    :   Account state (`disabled`, `invited`, `enabled`, `declined`)

    `total_spent: str`
    :   Total lifetime amount spent by the customer

    `updated_at: str`
    :   ISO 8601 timestamp when the customer record was last updated

<a id="DiscountCodesAndCondition"></a>

`DiscountCodesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.DiscountCodesEqCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesGtCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesGteCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLtCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLteCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesInCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesNotCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesAndCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesOrCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesAnyCondition]`
    :   The type of the None singleton.

<a id="DiscountCodesAnyCondition"></a>

`DiscountCodesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesAnyValueFilter`
    :   The type of the None singleton.

<a id="DiscountCodesAnyValueFilter"></a>

`DiscountCodesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `code: Any`
    :   Discount code string shoppers enter at checkout

    `created_at: Any`
    :   ISO 8601 timestamp when the code was created

    `id: Any`
    :   Unique identifier for the discount code

    `price_rule_id: Any`
    :   Identifier of the parent price rule

    `updated_at: Any`
    :   ISO 8601 timestamp when the code was last updated

    `usage_count: Any`
    :   Number of times the code has been redeemed

<a id="DiscountCodesContainsCondition"></a>

`DiscountCodesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesAnyValueFilter`
    :   The type of the None singleton.

<a id="DiscountCodesEqCondition"></a>

`DiscountCodesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesSearchFilter`
    :   The type of the None singleton.

<a id="DiscountCodesFuzzyCondition"></a>

`DiscountCodesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesStringFilter`
    :   The type of the None singleton.

<a id="DiscountCodesGetParams"></a>

`DiscountCodesGetParams(*args, **kwargs)`
:   Parameters for discount_codes.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `discount_code_id: str`
    :   The type of the None singleton.

    `price_rule_id: str`
    :   The type of the None singleton.

<a id="DiscountCodesGtCondition"></a>

`DiscountCodesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesSearchFilter`
    :   The type of the None singleton.

<a id="DiscountCodesGteCondition"></a>

`DiscountCodesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesSearchFilter`
    :   The type of the None singleton.

<a id="DiscountCodesInCondition"></a>

`DiscountCodesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesInFilter`
    :   The type of the None singleton.

<a id="DiscountCodesInFilter"></a>

`DiscountCodesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `code: list[str]`
    :   Discount code string shoppers enter at checkout

    `created_at: list[str]`
    :   ISO 8601 timestamp when the code was created

    `id: list[int]`
    :   Unique identifier for the discount code

    `price_rule_id: list[int]`
    :   Identifier of the parent price rule

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the code was last updated

    `usage_count: list[int]`
    :   Number of times the code has been redeemed

<a id="DiscountCodesKeywordCondition"></a>

`DiscountCodesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesStringFilter`
    :   The type of the None singleton.

<a id="DiscountCodesLikeCondition"></a>

`DiscountCodesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesStringFilter`
    :   The type of the None singleton.

<a id="DiscountCodesListParams"></a>

`DiscountCodesListParams(*args, **kwargs)`
:   Parameters for discount_codes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `price_rule_id: str`
    :   The type of the None singleton.

<a id="DiscountCodesLtCondition"></a>

`DiscountCodesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesSearchFilter`
    :   The type of the None singleton.

<a id="DiscountCodesLteCondition"></a>

`DiscountCodesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesSearchFilter`
    :   The type of the None singleton.

<a id="DiscountCodesNeqCondition"></a>

`DiscountCodesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesSearchFilter`
    :   The type of the None singleton.

<a id="DiscountCodesNotCondition"></a>

`DiscountCodesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesEqCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesGtCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesGteCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLtCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLteCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesInCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesNotCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesAndCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesOrCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesAnyCondition`
    :   The type of the None singleton.

<a id="DiscountCodesOrCondition"></a>

`DiscountCodesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.DiscountCodesEqCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesGtCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesGteCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLtCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLteCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesInCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesNotCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesAndCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesOrCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesAnyCondition]`
    :   The type of the None singleton.

<a id="DiscountCodesSearchFilter"></a>

`DiscountCodesSearchFilter(*args, **kwargs)`
:   Available fields for filtering discount_codes search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `code: str | None`
    :   Discount code string shoppers enter at checkout

    `created_at: str | None`
    :   ISO 8601 timestamp when the code was created

    `id: int | None`
    :   Unique identifier for the discount code

    `price_rule_id: int | None`
    :   Identifier of the parent price rule

    `updated_at: str | None`
    :   ISO 8601 timestamp when the code was last updated

    `usage_count: int | None`
    :   Number of times the code has been redeemed

<a id="DiscountCodesSearchQuery"></a>

`DiscountCodesSearchQuery(*args, **kwargs)`
:   Search query for discount_codes entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesEqCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesGtCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesGteCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLtCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLteCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesInCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesNotCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesAndCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesOrCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.DiscountCodesSortFilter]`
    :   The type of the None singleton.

<a id="DiscountCodesSortFilter"></a>

`DiscountCodesSortFilter(*args, **kwargs)`
:   Available fields for sorting discount_codes search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `code: Literal['asc', 'desc']`
    :   Discount code string shoppers enter at checkout

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the code was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the discount code

    `price_rule_id: Literal['asc', 'desc']`
    :   Identifier of the parent price rule

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the code was last updated

    `usage_count: Literal['asc', 'desc']`
    :   Number of times the code has been redeemed

<a id="DiscountCodesStringFilter"></a>

`DiscountCodesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `code: str`
    :   Discount code string shoppers enter at checkout

    `created_at: str`
    :   ISO 8601 timestamp when the code was created

    `id: str`
    :   Unique identifier for the discount code

    `price_rule_id: str`
    :   Identifier of the parent price rule

    `updated_at: str`
    :   ISO 8601 timestamp when the code was last updated

    `usage_count: str`
    :   Number of times the code has been redeemed

<a id="DraftOrdersAndCondition"></a>

`DraftOrdersAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.DraftOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersAnyCondition]`
    :   The type of the None singleton.

<a id="DraftOrdersAnyCondition"></a>

`DraftOrdersAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersAnyValueFilter`
    :   The type of the None singleton.

<a id="DraftOrdersAnyValueFilter"></a>

`DraftOrdersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `completed_at: Any`
    :   ISO 8601 timestamp when the draft order was completed, if applicable

    `created_at: Any`
    :   ISO 8601 timestamp when the draft order was created

    `currency: Any`
    :   ISO 4217 currency code for the draft order totals

    `email: Any`
    :   Email address associated with the draft order

    `id: Any`
    :   Unique identifier for the draft order

    `name: Any`
    :   Shopify-assigned display name for the draft order (e.g. `#D12345`)

    `order_id: Any`
    :   Identifier of the completed order, if the draft has been completed

    `status: Any`
    :   Status of the draft order (`open`, `invoice_sent`, `completed`)

    `total_price: Any`
    :   Total price of the draft order

    `updated_at: Any`
    :   ISO 8601 timestamp when the draft order was last updated

<a id="DraftOrdersContainsCondition"></a>

`DraftOrdersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersAnyValueFilter`
    :   The type of the None singleton.

<a id="DraftOrdersEqCondition"></a>

`DraftOrdersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersSearchFilter`
    :   The type of the None singleton.

<a id="DraftOrdersFuzzyCondition"></a>

`DraftOrdersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersStringFilter`
    :   The type of the None singleton.

<a id="DraftOrdersGetParams"></a>

`DraftOrdersGetParams(*args, **kwargs)`
:   Parameters for draft_orders.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `draft_order_id: str`
    :   The type of the None singleton.

<a id="DraftOrdersGtCondition"></a>

`DraftOrdersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersSearchFilter`
    :   The type of the None singleton.

<a id="DraftOrdersGteCondition"></a>

`DraftOrdersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersSearchFilter`
    :   The type of the None singleton.

<a id="DraftOrdersInCondition"></a>

`DraftOrdersInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersInFilter`
    :   The type of the None singleton.

<a id="DraftOrdersInFilter"></a>

`DraftOrdersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `completed_at: list[str]`
    :   ISO 8601 timestamp when the draft order was completed, if applicable

    `created_at: list[str]`
    :   ISO 8601 timestamp when the draft order was created

    `currency: list[str]`
    :   ISO 4217 currency code for the draft order totals

    `email: list[str]`
    :   Email address associated with the draft order

    `id: list[int]`
    :   Unique identifier for the draft order

    `name: list[str]`
    :   Shopify-assigned display name for the draft order (e.g. `#D12345`)

    `order_id: list[int]`
    :   Identifier of the completed order, if the draft has been completed

    `status: list[str]`
    :   Status of the draft order (`open`, `invoice_sent`, `completed`)

    `total_price: list[str]`
    :   Total price of the draft order

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the draft order was last updated

<a id="DraftOrdersKeywordCondition"></a>

`DraftOrdersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersStringFilter`
    :   The type of the None singleton.

<a id="DraftOrdersLikeCondition"></a>

`DraftOrdersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersStringFilter`
    :   The type of the None singleton.

<a id="DraftOrdersListParams"></a>

`DraftOrdersListParams(*args, **kwargs)`
:   Parameters for draft_orders.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `updated_at_max: str`
    :   The type of the None singleton.

    `updated_at_min: str`
    :   The type of the None singleton.

<a id="DraftOrdersLtCondition"></a>

`DraftOrdersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersSearchFilter`
    :   The type of the None singleton.

<a id="DraftOrdersLteCondition"></a>

`DraftOrdersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersSearchFilter`
    :   The type of the None singleton.

<a id="DraftOrdersNeqCondition"></a>

`DraftOrdersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersSearchFilter`
    :   The type of the None singleton.

<a id="DraftOrdersNotCondition"></a>

`DraftOrdersNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersAnyCondition`
    :   The type of the None singleton.

<a id="DraftOrdersOrCondition"></a>

`DraftOrdersOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.DraftOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersAnyCondition]`
    :   The type of the None singleton.

<a id="DraftOrdersSearchFilter"></a>

`DraftOrdersSearchFilter(*args, **kwargs)`
:   Available fields for filtering draft_orders search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="DraftOrdersSearchQuery"></a>

`DraftOrdersSearchQuery(*args, **kwargs)`
:   Search query for draft_orders entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.DraftOrdersSortFilter]`
    :   The type of the None singleton.

<a id="DraftOrdersSortFilter"></a>

`DraftOrdersSortFilter(*args, **kwargs)`
:   Available fields for sorting draft_orders search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `completed_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the draft order was completed, if applicable

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the draft order was created

    `currency: Literal['asc', 'desc']`
    :   ISO 4217 currency code for the draft order totals

    `email: Literal['asc', 'desc']`
    :   Email address associated with the draft order

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the draft order

    `name: Literal['asc', 'desc']`
    :   Shopify-assigned display name for the draft order (e.g. `#D12345`)

    `order_id: Literal['asc', 'desc']`
    :   Identifier of the completed order, if the draft has been completed

    `status: Literal['asc', 'desc']`
    :   Status of the draft order (`open`, `invoice_sent`, `completed`)

    `total_price: Literal['asc', 'desc']`
    :   Total price of the draft order

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the draft order was last updated

<a id="DraftOrdersStringFilter"></a>

`DraftOrdersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `completed_at: str`
    :   ISO 8601 timestamp when the draft order was completed, if applicable

    `created_at: str`
    :   ISO 8601 timestamp when the draft order was created

    `currency: str`
    :   ISO 4217 currency code for the draft order totals

    `email: str`
    :   Email address associated with the draft order

    `id: str`
    :   Unique identifier for the draft order

    `name: str`
    :   Shopify-assigned display name for the draft order (e.g. `#D12345`)

    `order_id: str`
    :   Identifier of the completed order, if the draft has been completed

    `status: str`
    :   Status of the draft order (`open`, `invoice_sent`, `completed`)

    `total_price: str`
    :   Total price of the draft order

    `updated_at: str`
    :   ISO 8601 timestamp when the draft order was last updated

<a id="FulfillmentOrdersAndCondition"></a>

`FulfillmentOrdersAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersAnyCondition]`
    :   The type of the None singleton.

<a id="FulfillmentOrdersAnyCondition"></a>

`FulfillmentOrdersAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersAnyValueFilter`
    :   The type of the None singleton.

<a id="FulfillmentOrdersAnyValueFilter"></a>

`FulfillmentOrdersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assigned_location_id: Any`
    :   Identifier of the location assigned to fulfill the order

    `created_at: Any`
    :   ISO 8601 timestamp when the fulfillment order was created

    `id: Any`
    :   Unique identifier for the fulfillment order

    `order_id: Any`
    :   Identifier of the parent order

    `request_status: Any`
    :   Status of the fulfillment request (e.g. `unsubmitted`, `submitted`)

    `shop_id: Any`
    :   Identifier of the shop that owns the fulfillment order

    `status: Any`
    :   Fulfillment order status (e.g. `open`, `in_progress`, `closed`)

    `updated_at: Any`
    :   ISO 8601 timestamp when the fulfillment order was last updated

<a id="FulfillmentOrdersContainsCondition"></a>

`FulfillmentOrdersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersAnyValueFilter`
    :   The type of the None singleton.

<a id="FulfillmentOrdersEqCondition"></a>

`FulfillmentOrdersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersSearchFilter`
    :   The type of the None singleton.

<a id="FulfillmentOrdersFuzzyCondition"></a>

`FulfillmentOrdersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersStringFilter`
    :   The type of the None singleton.

<a id="FulfillmentOrdersGetParams"></a>

`FulfillmentOrdersGetParams(*args, **kwargs)`
:   Parameters for fulfillment_orders.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fulfillment_order_id: str`
    :   The type of the None singleton.

<a id="FulfillmentOrdersGtCondition"></a>

`FulfillmentOrdersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersSearchFilter`
    :   The type of the None singleton.

<a id="FulfillmentOrdersGteCondition"></a>

`FulfillmentOrdersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersSearchFilter`
    :   The type of the None singleton.

<a id="FulfillmentOrdersInCondition"></a>

`FulfillmentOrdersInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersInFilter`
    :   The type of the None singleton.

<a id="FulfillmentOrdersInFilter"></a>

`FulfillmentOrdersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assigned_location_id: list[int]`
    :   Identifier of the location assigned to fulfill the order

    `created_at: list[str]`
    :   ISO 8601 timestamp when the fulfillment order was created

    `id: list[int]`
    :   Unique identifier for the fulfillment order

    `order_id: list[int]`
    :   Identifier of the parent order

    `request_status: list[str]`
    :   Status of the fulfillment request (e.g. `unsubmitted`, `submitted`)

    `shop_id: list[int]`
    :   Identifier of the shop that owns the fulfillment order

    `status: list[str]`
    :   Fulfillment order status (e.g. `open`, `in_progress`, `closed`)

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the fulfillment order was last updated

<a id="FulfillmentOrdersKeywordCondition"></a>

`FulfillmentOrdersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersStringFilter`
    :   The type of the None singleton.

<a id="FulfillmentOrdersLikeCondition"></a>

`FulfillmentOrdersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersStringFilter`
    :   The type of the None singleton.

<a id="FulfillmentOrdersListParams"></a>

`FulfillmentOrdersListParams(*args, **kwargs)`
:   Parameters for fulfillment_orders.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_id: str`
    :   The type of the None singleton.

<a id="FulfillmentOrdersLtCondition"></a>

`FulfillmentOrdersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersSearchFilter`
    :   The type of the None singleton.

<a id="FulfillmentOrdersLteCondition"></a>

`FulfillmentOrdersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersSearchFilter`
    :   The type of the None singleton.

<a id="FulfillmentOrdersNeqCondition"></a>

`FulfillmentOrdersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersSearchFilter`
    :   The type of the None singleton.

<a id="FulfillmentOrdersNotCondition"></a>

`FulfillmentOrdersNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersAnyCondition`
    :   The type of the None singleton.

<a id="FulfillmentOrdersOrCondition"></a>

`FulfillmentOrdersOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersAnyCondition]`
    :   The type of the None singleton.

<a id="FulfillmentOrdersSearchFilter"></a>

`FulfillmentOrdersSearchFilter(*args, **kwargs)`
:   Available fields for filtering fulfillment_orders search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assigned_location_id: int | None`
    :   Identifier of the location assigned to fulfill the order

    `created_at: str | None`
    :   ISO 8601 timestamp when the fulfillment order was created

    `id: int | None`
    :   Unique identifier for the fulfillment order

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

<a id="FulfillmentOrdersSearchQuery"></a>

`FulfillmentOrdersSearchQuery(*args, **kwargs)`
:   Search query for fulfillment_orders entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersSortFilter]`
    :   The type of the None singleton.

<a id="FulfillmentOrdersSortFilter"></a>

`FulfillmentOrdersSortFilter(*args, **kwargs)`
:   Available fields for sorting fulfillment_orders search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assigned_location_id: Literal['asc', 'desc']`
    :   Identifier of the location assigned to fulfill the order

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the fulfillment order was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the fulfillment order

    `order_id: Literal['asc', 'desc']`
    :   Identifier of the parent order

    `request_status: Literal['asc', 'desc']`
    :   Status of the fulfillment request (e.g. `unsubmitted`, `submitted`)

    `shop_id: Literal['asc', 'desc']`
    :   Identifier of the shop that owns the fulfillment order

    `status: Literal['asc', 'desc']`
    :   Fulfillment order status (e.g. `open`, `in_progress`, `closed`)

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the fulfillment order was last updated

<a id="FulfillmentOrdersStringFilter"></a>

`FulfillmentOrdersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assigned_location_id: str`
    :   Identifier of the location assigned to fulfill the order

    `created_at: str`
    :   ISO 8601 timestamp when the fulfillment order was created

    `id: str`
    :   Unique identifier for the fulfillment order

    `order_id: str`
    :   Identifier of the parent order

    `request_status: str`
    :   Status of the fulfillment request (e.g. `unsubmitted`, `submitted`)

    `shop_id: str`
    :   Identifier of the shop that owns the fulfillment order

    `status: str`
    :   Fulfillment order status (e.g. `open`, `in_progress`, `closed`)

    `updated_at: str`
    :   ISO 8601 timestamp when the fulfillment order was last updated

<a id="FulfillmentsAndCondition"></a>

`FulfillmentsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.FulfillmentsEqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsGtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsGteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsInCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsNotCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsAndCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsOrCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsAnyCondition]`
    :   The type of the None singleton.

<a id="FulfillmentsAnyCondition"></a>

`FulfillmentsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="FulfillmentsAnyValueFilter"></a>

`FulfillmentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the fulfillment was created

    `id: Any`
    :   Unique identifier for the fulfillment

    `location_id: Any`
    :   Identifier of the fulfilling location

    `order_id: Any`
    :   Identifier of the parent order

    `shipment_status: Any`
    :   Carrier shipment status (e.g. `delivered`, `in_transit`)

    `status: Any`
    :   Fulfillment status (e.g. `pending`, `open`, `success`, `cancelled`)

    `tracking_company: Any`
    :   Name of the shipping carrier

    `tracking_number: Any`
    :   Primary tracking number for the shipment

    `updated_at: Any`
    :   ISO 8601 timestamp when the fulfillment was last updated

<a id="FulfillmentsContainsCondition"></a>

`FulfillmentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="FulfillmentsEqCondition"></a>

`FulfillmentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsSearchFilter`
    :   The type of the None singleton.

<a id="FulfillmentsFuzzyCondition"></a>

`FulfillmentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsStringFilter`
    :   The type of the None singleton.

<a id="FulfillmentsGetParams"></a>

`FulfillmentsGetParams(*args, **kwargs)`
:   Parameters for fulfillments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fulfillment_id: str`
    :   The type of the None singleton.

    `order_id: str`
    :   The type of the None singleton.

<a id="FulfillmentsGtCondition"></a>

`FulfillmentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsSearchFilter`
    :   The type of the None singleton.

<a id="FulfillmentsGteCondition"></a>

`FulfillmentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsSearchFilter`
    :   The type of the None singleton.

<a id="FulfillmentsInCondition"></a>

`FulfillmentsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsInFilter`
    :   The type of the None singleton.

<a id="FulfillmentsInFilter"></a>

`FulfillmentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the fulfillment was created

    `id: list[int]`
    :   Unique identifier for the fulfillment

    `location_id: list[int]`
    :   Identifier of the fulfilling location

    `order_id: list[int]`
    :   Identifier of the parent order

    `shipment_status: list[str]`
    :   Carrier shipment status (e.g. `delivered`, `in_transit`)

    `status: list[str]`
    :   Fulfillment status (e.g. `pending`, `open`, `success`, `cancelled`)

    `tracking_company: list[str]`
    :   Name of the shipping carrier

    `tracking_number: list[str]`
    :   Primary tracking number for the shipment

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the fulfillment was last updated

<a id="FulfillmentsKeywordCondition"></a>

`FulfillmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsStringFilter`
    :   The type of the None singleton.

<a id="FulfillmentsLikeCondition"></a>

`FulfillmentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsStringFilter`
    :   The type of the None singleton.

<a id="FulfillmentsListParams"></a>

`FulfillmentsListParams(*args, **kwargs)`
:   Parameters for fulfillments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at_max: str`
    :   The type of the None singleton.

    `created_at_min: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `order_id: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

    `updated_at_max: str`
    :   The type of the None singleton.

    `updated_at_min: str`
    :   The type of the None singleton.

<a id="FulfillmentsLtCondition"></a>

`FulfillmentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsSearchFilter`
    :   The type of the None singleton.

<a id="FulfillmentsLteCondition"></a>

`FulfillmentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsSearchFilter`
    :   The type of the None singleton.

<a id="FulfillmentsNeqCondition"></a>

`FulfillmentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsSearchFilter`
    :   The type of the None singleton.

<a id="FulfillmentsNotCondition"></a>

`FulfillmentsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsEqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsGtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsGteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsInCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsNotCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsAndCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsOrCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsAnyCondition`
    :   The type of the None singleton.

<a id="FulfillmentsOrCondition"></a>

`FulfillmentsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.FulfillmentsEqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsGtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsGteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsInCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsNotCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsAndCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsOrCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsAnyCondition]`
    :   The type of the None singleton.

<a id="FulfillmentsSearchFilter"></a>

`FulfillmentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering fulfillments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the fulfillment was created

    `id: int | None`
    :   Unique identifier for the fulfillment

    `location_id: int | None`
    :   Identifier of the fulfilling location

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

<a id="FulfillmentsSearchQuery"></a>

`FulfillmentsSearchQuery(*args, **kwargs)`
:   Search query for fulfillments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsEqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsGtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsGteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsInCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsNotCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsAndCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsOrCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.FulfillmentsSortFilter]`
    :   The type of the None singleton.

<a id="FulfillmentsSortFilter"></a>

`FulfillmentsSortFilter(*args, **kwargs)`
:   Available fields for sorting fulfillments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the fulfillment was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the fulfillment

    `location_id: Literal['asc', 'desc']`
    :   Identifier of the fulfilling location

    `order_id: Literal['asc', 'desc']`
    :   Identifier of the parent order

    `shipment_status: Literal['asc', 'desc']`
    :   Carrier shipment status (e.g. `delivered`, `in_transit`)

    `status: Literal['asc', 'desc']`
    :   Fulfillment status (e.g. `pending`, `open`, `success`, `cancelled`)

    `tracking_company: Literal['asc', 'desc']`
    :   Name of the shipping carrier

    `tracking_number: Literal['asc', 'desc']`
    :   Primary tracking number for the shipment

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the fulfillment was last updated

<a id="FulfillmentsStringFilter"></a>

`FulfillmentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the fulfillment was created

    `id: str`
    :   Unique identifier for the fulfillment

    `location_id: str`
    :   Identifier of the fulfilling location

    `order_id: str`
    :   Identifier of the parent order

    `shipment_status: str`
    :   Carrier shipment status (e.g. `delivered`, `in_transit`)

    `status: str`
    :   Fulfillment status (e.g. `pending`, `open`, `success`, `cancelled`)

    `tracking_company: str`
    :   Name of the shipping carrier

    `tracking_number: str`
    :   Primary tracking number for the shipment

    `updated_at: str`
    :   ISO 8601 timestamp when the fulfillment was last updated

<a id="InventoryItemsAndCondition"></a>

`InventoryItemsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.InventoryItemsEqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsGtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsGteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsInCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsNotCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsAndCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsOrCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsAnyCondition]`
    :   The type of the None singleton.

<a id="InventoryItemsAnyCondition"></a>

`InventoryItemsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsAnyValueFilter`
    :   The type of the None singleton.

<a id="InventoryItemsAnyValueFilter"></a>

`InventoryItemsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country_code_of_origin: Any`
    :   ISO country code of the item's country of origin

    `created_at: Any`
    :   ISO 8601 timestamp when the inventory item was created

    `id: Any`
    :   Unique identifier for the inventory item

    `requires_shipping: Any`
    :   Whether the item requires shipping

    `sku: Any`
    :   Stock keeping unit associated with the inventory item

    `tracked: Any`
    :   Whether Shopify is tracking inventory for this item

    `updated_at: Any`
    :   ISO 8601 timestamp when the inventory item was last updated

<a id="InventoryItemsContainsCondition"></a>

`InventoryItemsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsAnyValueFilter`
    :   The type of the None singleton.

<a id="InventoryItemsEqCondition"></a>

`InventoryItemsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsSearchFilter`
    :   The type of the None singleton.

<a id="InventoryItemsFuzzyCondition"></a>

`InventoryItemsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsStringFilter`
    :   The type of the None singleton.

<a id="InventoryItemsGetParams"></a>

`InventoryItemsGetParams(*args, **kwargs)`
:   Parameters for inventory_items.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `inventory_item_id: str`
    :   The type of the None singleton.

<a id="InventoryItemsGtCondition"></a>

`InventoryItemsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsSearchFilter`
    :   The type of the None singleton.

<a id="InventoryItemsGteCondition"></a>

`InventoryItemsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsSearchFilter`
    :   The type of the None singleton.

<a id="InventoryItemsInCondition"></a>

`InventoryItemsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsInFilter`
    :   The type of the None singleton.

<a id="InventoryItemsInFilter"></a>

`InventoryItemsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country_code_of_origin: list[str]`
    :   ISO country code of the item's country of origin

    `created_at: list[str]`
    :   ISO 8601 timestamp when the inventory item was created

    `id: list[int]`
    :   Unique identifier for the inventory item

    `requires_shipping: list[bool]`
    :   Whether the item requires shipping

    `sku: list[str]`
    :   Stock keeping unit associated with the inventory item

    `tracked: list[bool]`
    :   Whether Shopify is tracking inventory for this item

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the inventory item was last updated

<a id="InventoryItemsKeywordCondition"></a>

`InventoryItemsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsStringFilter`
    :   The type of the None singleton.

<a id="InventoryItemsLikeCondition"></a>

`InventoryItemsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsStringFilter`
    :   The type of the None singleton.

<a id="InventoryItemsListParams"></a>

`InventoryItemsListParams(*args, **kwargs)`
:   Parameters for inventory_items.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ids: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

<a id="InventoryItemsLtCondition"></a>

`InventoryItemsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsSearchFilter`
    :   The type of the None singleton.

<a id="InventoryItemsLteCondition"></a>

`InventoryItemsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsSearchFilter`
    :   The type of the None singleton.

<a id="InventoryItemsNeqCondition"></a>

`InventoryItemsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsSearchFilter`
    :   The type of the None singleton.

<a id="InventoryItemsNotCondition"></a>

`InventoryItemsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsEqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsGtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsGteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsInCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsNotCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsAndCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsOrCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsAnyCondition`
    :   The type of the None singleton.

<a id="InventoryItemsOrCondition"></a>

`InventoryItemsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.InventoryItemsEqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsGtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsGteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsInCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsNotCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsAndCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsOrCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsAnyCondition]`
    :   The type of the None singleton.

<a id="InventoryItemsSearchFilter"></a>

`InventoryItemsSearchFilter(*args, **kwargs)`
:   Available fields for filtering inventory_items search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country_code_of_origin: str | None`
    :   ISO country code of the item's country of origin

    `created_at: str | None`
    :   ISO 8601 timestamp when the inventory item was created

    `id: int | None`
    :   Unique identifier for the inventory item

    `requires_shipping: bool | None`
    :   Whether the item requires shipping

    `sku: str | None`
    :   Stock keeping unit associated with the inventory item

    `tracked: bool | None`
    :   Whether Shopify is tracking inventory for this item

    `updated_at: str | None`
    :   ISO 8601 timestamp when the inventory item was last updated

<a id="InventoryItemsSearchQuery"></a>

`InventoryItemsSearchQuery(*args, **kwargs)`
:   Search query for inventory_items entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsEqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsGtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsGteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsInCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsNotCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsAndCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsOrCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.InventoryItemsSortFilter]`
    :   The type of the None singleton.

<a id="InventoryItemsSortFilter"></a>

`InventoryItemsSortFilter(*args, **kwargs)`
:   Available fields for sorting inventory_items search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country_code_of_origin: Literal['asc', 'desc']`
    :   ISO country code of the item's country of origin

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the inventory item was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the inventory item

    `requires_shipping: Literal['asc', 'desc']`
    :   Whether the item requires shipping

    `sku: Literal['asc', 'desc']`
    :   Stock keeping unit associated with the inventory item

    `tracked: Literal['asc', 'desc']`
    :   Whether Shopify is tracking inventory for this item

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the inventory item was last updated

<a id="InventoryItemsStringFilter"></a>

`InventoryItemsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country_code_of_origin: str`
    :   ISO country code of the item's country of origin

    `created_at: str`
    :   ISO 8601 timestamp when the inventory item was created

    `id: str`
    :   Unique identifier for the inventory item

    `requires_shipping: str`
    :   Whether the item requires shipping

    `sku: str`
    :   Stock keeping unit associated with the inventory item

    `tracked: str`
    :   Whether Shopify is tracking inventory for this item

    `updated_at: str`
    :   ISO 8601 timestamp when the inventory item was last updated

<a id="InventoryLevelsAndCondition"></a>

`InventoryLevelsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsEqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsGtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsGteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsInCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsNotCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsAndCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsOrCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsAnyCondition]`
    :   The type of the None singleton.

<a id="InventoryLevelsAnyCondition"></a>

`InventoryLevelsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsAnyValueFilter`
    :   The type of the None singleton.

<a id="InventoryLevelsAnyValueFilter"></a>

`InventoryLevelsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `available: Any`
    :   Number of units available at the location

    `inventory_item_id: Any`
    :   Identifier of the inventory item

    `location_id: Any`
    :   Identifier of the location holding the inventory

    `updated_at: Any`
    :   ISO 8601 timestamp when the inventory level was last updated

<a id="InventoryLevelsContainsCondition"></a>

`InventoryLevelsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsAnyValueFilter`
    :   The type of the None singleton.

<a id="InventoryLevelsEqCondition"></a>

`InventoryLevelsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsSearchFilter`
    :   The type of the None singleton.

<a id="InventoryLevelsFuzzyCondition"></a>

`InventoryLevelsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsStringFilter`
    :   The type of the None singleton.

<a id="InventoryLevelsGtCondition"></a>

`InventoryLevelsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsSearchFilter`
    :   The type of the None singleton.

<a id="InventoryLevelsGteCondition"></a>

`InventoryLevelsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsSearchFilter`
    :   The type of the None singleton.

<a id="InventoryLevelsInCondition"></a>

`InventoryLevelsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsInFilter`
    :   The type of the None singleton.

<a id="InventoryLevelsInFilter"></a>

`InventoryLevelsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `available: list[int]`
    :   Number of units available at the location

    `inventory_item_id: list[int]`
    :   Identifier of the inventory item

    `location_id: list[int]`
    :   Identifier of the location holding the inventory

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the inventory level was last updated

<a id="InventoryLevelsKeywordCondition"></a>

`InventoryLevelsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsStringFilter`
    :   The type of the None singleton.

<a id="InventoryLevelsLikeCondition"></a>

`InventoryLevelsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsStringFilter`
    :   The type of the None singleton.

<a id="InventoryLevelsListParams"></a>

`InventoryLevelsListParams(*args, **kwargs)`
:   Parameters for inventory_levels.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `location_id: str`
    :   The type of the None singleton.

<a id="InventoryLevelsLtCondition"></a>

`InventoryLevelsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsSearchFilter`
    :   The type of the None singleton.

<a id="InventoryLevelsLteCondition"></a>

`InventoryLevelsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsSearchFilter`
    :   The type of the None singleton.

<a id="InventoryLevelsNeqCondition"></a>

`InventoryLevelsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsSearchFilter`
    :   The type of the None singleton.

<a id="InventoryLevelsNotCondition"></a>

`InventoryLevelsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsEqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsGtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsGteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsInCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsNotCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsAndCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsOrCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsAnyCondition`
    :   The type of the None singleton.

<a id="InventoryLevelsOrCondition"></a>

`InventoryLevelsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsEqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsGtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsGteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsInCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsNotCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsAndCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsOrCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsAnyCondition]`
    :   The type of the None singleton.

<a id="InventoryLevelsSearchFilter"></a>

`InventoryLevelsSearchFilter(*args, **kwargs)`
:   Available fields for filtering inventory_levels search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `available: int | None`
    :   Number of units available at the location

    `inventory_item_id: int | None`
    :   Identifier of the inventory item

    `location_id: int | None`
    :   Identifier of the location holding the inventory

    `updated_at: str | None`
    :   ISO 8601 timestamp when the inventory level was last updated

<a id="InventoryLevelsSearchQuery"></a>

`InventoryLevelsSearchQuery(*args, **kwargs)`
:   Search query for inventory_levels entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsEqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsGtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsGteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsInCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsNotCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsAndCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsOrCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsSortFilter]`
    :   The type of the None singleton.

<a id="InventoryLevelsSortFilter"></a>

`InventoryLevelsSortFilter(*args, **kwargs)`
:   Available fields for sorting inventory_levels search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `available: Literal['asc', 'desc']`
    :   Number of units available at the location

    `inventory_item_id: Literal['asc', 'desc']`
    :   Identifier of the inventory item

    `location_id: Literal['asc', 'desc']`
    :   Identifier of the location holding the inventory

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the inventory level was last updated

<a id="InventoryLevelsStringFilter"></a>

`InventoryLevelsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `available: str`
    :   Number of units available at the location

    `inventory_item_id: str`
    :   Identifier of the inventory item

    `location_id: str`
    :   Identifier of the location holding the inventory

    `updated_at: str`
    :   ISO 8601 timestamp when the inventory level was last updated

<a id="LocationsAndCondition"></a>

`LocationsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.LocationsEqCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsGtCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsGteCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLtCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLteCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsInCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsNotCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsAndCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsOrCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsAnyCondition]`
    :   The type of the None singleton.

<a id="LocationsAnyCondition"></a>

`LocationsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.LocationsAnyValueFilter`
    :   The type of the None singleton.

<a id="LocationsAnyValueFilter"></a>

`LocationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Any`
    :   Whether the location is currently active

    `address1: Any`
    :   Primary street address of the location

    `city: Any`
    :   City of the location

    `country: Any`
    :   Country name of the location

    `country_code: Any`
    :   ISO 3166-1 alpha-2 country code of the location

    `created_at: Any`
    :   ISO 8601 timestamp when the location was created

    `id: Any`
    :   Unique identifier for the location

    `name: Any`
    :   Display name of the location

    `phone: Any`
    :   Phone number for the location

    `province: Any`
    :   Province, state, or region of the location

    `updated_at: Any`
    :   ISO 8601 timestamp when the location was last updated

<a id="LocationsContainsCondition"></a>

`LocationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.LocationsAnyValueFilter`
    :   The type of the None singleton.

<a id="LocationsEqCondition"></a>

`LocationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.LocationsSearchFilter`
    :   The type of the None singleton.

<a id="LocationsFuzzyCondition"></a>

`LocationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.LocationsStringFilter`
    :   The type of the None singleton.

<a id="LocationsGetParams"></a>

`LocationsGetParams(*args, **kwargs)`
:   Parameters for locations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `location_id: str`
    :   The type of the None singleton.

<a id="LocationsGtCondition"></a>

`LocationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.LocationsSearchFilter`
    :   The type of the None singleton.

<a id="LocationsGteCondition"></a>

`LocationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.LocationsSearchFilter`
    :   The type of the None singleton.

<a id="LocationsInCondition"></a>

`LocationsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.LocationsInFilter`
    :   The type of the None singleton.

<a id="LocationsInFilter"></a>

`LocationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: list[bool]`
    :   Whether the location is currently active

    `address1: list[str]`
    :   Primary street address of the location

    `city: list[str]`
    :   City of the location

    `country: list[str]`
    :   Country name of the location

    `country_code: list[str]`
    :   ISO 3166-1 alpha-2 country code of the location

    `created_at: list[str]`
    :   ISO 8601 timestamp when the location was created

    `id: list[int]`
    :   Unique identifier for the location

    `name: list[str]`
    :   Display name of the location

    `phone: list[str]`
    :   Phone number for the location

    `province: list[str]`
    :   Province, state, or region of the location

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the location was last updated

<a id="LocationsKeywordCondition"></a>

`LocationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.LocationsStringFilter`
    :   The type of the None singleton.

<a id="LocationsLikeCondition"></a>

`LocationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.LocationsStringFilter`
    :   The type of the None singleton.

<a id="LocationsListParams"></a>

`LocationsListParams(*args, **kwargs)`
:   Parameters for locations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="LocationsLtCondition"></a>

`LocationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.LocationsSearchFilter`
    :   The type of the None singleton.

<a id="LocationsLteCondition"></a>

`LocationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.LocationsSearchFilter`
    :   The type of the None singleton.

<a id="LocationsNeqCondition"></a>

`LocationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.LocationsSearchFilter`
    :   The type of the None singleton.

<a id="LocationsNotCondition"></a>

`LocationsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.LocationsEqCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsGtCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsGteCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLtCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLteCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsInCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsNotCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsAndCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsOrCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsAnyCondition`
    :   The type of the None singleton.

<a id="LocationsOrCondition"></a>

`LocationsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.LocationsEqCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsGtCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsGteCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLtCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLteCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsInCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsNotCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsAndCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsOrCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsAnyCondition]`
    :   The type of the None singleton.

<a id="LocationsSearchFilter"></a>

`LocationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering locations search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

    `name: str | None`
    :   Display name of the location

    `phone: str | None`
    :   Phone number for the location

    `province: str | None`
    :   Province, state, or region of the location

    `updated_at: str | None`
    :   ISO 8601 timestamp when the location was last updated

<a id="LocationsSearchQuery"></a>

`LocationsSearchQuery(*args, **kwargs)`
:   Search query for locations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.LocationsEqCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsGtCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsGteCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLtCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLteCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsInCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsNotCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsAndCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsOrCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.LocationsSortFilter]`
    :   The type of the None singleton.

<a id="LocationsSortFilter"></a>

`LocationsSortFilter(*args, **kwargs)`
:   Available fields for sorting locations search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Literal['asc', 'desc']`
    :   Whether the location is currently active

    `address1: Literal['asc', 'desc']`
    :   Primary street address of the location

    `city: Literal['asc', 'desc']`
    :   City of the location

    `country: Literal['asc', 'desc']`
    :   Country name of the location

    `country_code: Literal['asc', 'desc']`
    :   ISO 3166-1 alpha-2 country code of the location

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the location was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the location

    `name: Literal['asc', 'desc']`
    :   Display name of the location

    `phone: Literal['asc', 'desc']`
    :   Phone number for the location

    `province: Literal['asc', 'desc']`
    :   Province, state, or region of the location

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the location was last updated

<a id="LocationsStringFilter"></a>

`LocationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: str`
    :   Whether the location is currently active

    `address1: str`
    :   Primary street address of the location

    `city: str`
    :   City of the location

    `country: str`
    :   Country name of the location

    `country_code: str`
    :   ISO 3166-1 alpha-2 country code of the location

    `created_at: str`
    :   ISO 8601 timestamp when the location was created

    `id: str`
    :   Unique identifier for the location

    `name: str`
    :   Display name of the location

    `phone: str`
    :   Phone number for the location

    `province: str`
    :   Province, state, or region of the location

    `updated_at: str`
    :   ISO 8601 timestamp when the location was last updated

<a id="MetafieldCustomersAndCondition"></a>

`MetafieldCustomersAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldCustomersAnyCondition"></a>

`MetafieldCustomersAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldCustomersAnyValueFilter"></a>

`MetafieldCustomersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the metafield was created

    `description: Any`
    :   Human-readable description of the metafield

    `id: Any`
    :   Unique identifier for the metafield

    `key: Any`
    :   Key of the metafield within its namespace

    `namespace: Any`
    :   Namespace group for the metafield

    `owner_id: Any`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Any`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Any`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Any`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Any`
    :   Serialized value stored in the metafield

<a id="MetafieldCustomersContainsCondition"></a>

`MetafieldCustomersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldCustomersEqCondition"></a>

`MetafieldCustomersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldCustomersFuzzyCondition"></a>

`MetafieldCustomersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersStringFilter`
    :   The type of the None singleton.

<a id="MetafieldCustomersGtCondition"></a>

`MetafieldCustomersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldCustomersGteCondition"></a>

`MetafieldCustomersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldCustomersInCondition"></a>

`MetafieldCustomersInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersInFilter`
    :   The type of the None singleton.

<a id="MetafieldCustomersInFilter"></a>

`MetafieldCustomersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the metafield was created

    `description: list[str]`
    :   Human-readable description of the metafield

    `id: list[int]`
    :   Unique identifier for the metafield

    `key: list[str]`
    :   Key of the metafield within its namespace

    `namespace: list[str]`
    :   Namespace group for the metafield

    `owner_id: list[int]`
    :   Identifier of the resource that owns this metafield

    `owner_resource: list[str]`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: list[str]`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: list[str]`
    :   Serialized value stored in the metafield

<a id="MetafieldCustomersKeywordCondition"></a>

`MetafieldCustomersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersStringFilter`
    :   The type of the None singleton.

<a id="MetafieldCustomersLikeCondition"></a>

`MetafieldCustomersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersStringFilter`
    :   The type of the None singleton.

<a id="MetafieldCustomersListParams"></a>

`MetafieldCustomersListParams(*args, **kwargs)`
:   Parameters for metafield_customers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `key: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `namespace: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

<a id="MetafieldCustomersLtCondition"></a>

`MetafieldCustomersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldCustomersLteCondition"></a>

`MetafieldCustomersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldCustomersNeqCondition"></a>

`MetafieldCustomersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldCustomersNotCondition"></a>

`MetafieldCustomersNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersAnyCondition`
    :   The type of the None singleton.

<a id="MetafieldCustomersOrCondition"></a>

`MetafieldCustomersOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldCustomersSearchFilter"></a>

`MetafieldCustomersSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_customers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

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

<a id="MetafieldCustomersSearchQuery"></a>

`MetafieldCustomersSearchQuery(*args, **kwargs)`
:   Search query for metafield_customers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersSortFilter]`
    :   The type of the None singleton.

<a id="MetafieldCustomersSortFilter"></a>

`MetafieldCustomersSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_customers search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was created

    `description: Literal['asc', 'desc']`
    :   Human-readable description of the metafield

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the metafield

    `key: Literal['asc', 'desc']`
    :   Key of the metafield within its namespace

    `namespace: Literal['asc', 'desc']`
    :   Namespace group for the metafield

    `owner_id: Literal['asc', 'desc']`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Literal['asc', 'desc']`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Literal['asc', 'desc']`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Literal['asc', 'desc']`
    :   Serialized value stored in the metafield

<a id="MetafieldCustomersStringFilter"></a>

`MetafieldCustomersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the metafield was created

    `description: str`
    :   Human-readable description of the metafield

    `id: str`
    :   Unique identifier for the metafield

    `key: str`
    :   Key of the metafield within its namespace

    `namespace: str`
    :   Namespace group for the metafield

    `owner_id: str`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str`
    :   Serialized value stored in the metafield

<a id="MetafieldDraftOrdersAndCondition"></a>

`MetafieldDraftOrdersAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersAnyCondition"></a>

`MetafieldDraftOrdersAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersAnyValueFilter"></a>

`MetafieldDraftOrdersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the metafield was created

    `description: Any`
    :   Human-readable description of the metafield

    `id: Any`
    :   Unique identifier for the metafield

    `key: Any`
    :   Key of the metafield within its namespace

    `namespace: Any`
    :   Namespace group for the metafield

    `owner_id: Any`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Any`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Any`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Any`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Any`
    :   Serialized value stored in the metafield

<a id="MetafieldDraftOrdersContainsCondition"></a>

`MetafieldDraftOrdersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersEqCondition"></a>

`MetafieldDraftOrdersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersFuzzyCondition"></a>

`MetafieldDraftOrdersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersStringFilter`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersGtCondition"></a>

`MetafieldDraftOrdersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersGteCondition"></a>

`MetafieldDraftOrdersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersInCondition"></a>

`MetafieldDraftOrdersInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersInFilter`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersInFilter"></a>

`MetafieldDraftOrdersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the metafield was created

    `description: list[str]`
    :   Human-readable description of the metafield

    `id: list[int]`
    :   Unique identifier for the metafield

    `key: list[str]`
    :   Key of the metafield within its namespace

    `namespace: list[str]`
    :   Namespace group for the metafield

    `owner_id: list[int]`
    :   Identifier of the resource that owns this metafield

    `owner_resource: list[str]`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: list[str]`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: list[str]`
    :   Serialized value stored in the metafield

<a id="MetafieldDraftOrdersKeywordCondition"></a>

`MetafieldDraftOrdersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersStringFilter`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersLikeCondition"></a>

`MetafieldDraftOrdersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersStringFilter`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersListParams"></a>

`MetafieldDraftOrdersListParams(*args, **kwargs)`
:   Parameters for metafield_draft_orders.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `draft_order_id: str`
    :   The type of the None singleton.

    `key: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `namespace: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersLtCondition"></a>

`MetafieldDraftOrdersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersLteCondition"></a>

`MetafieldDraftOrdersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersNeqCondition"></a>

`MetafieldDraftOrdersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersNotCondition"></a>

`MetafieldDraftOrdersNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersAnyCondition`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersOrCondition"></a>

`MetafieldDraftOrdersOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersSearchFilter"></a>

`MetafieldDraftOrdersSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_draft_orders search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

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

<a id="MetafieldDraftOrdersSearchQuery"></a>

`MetafieldDraftOrdersSearchQuery(*args, **kwargs)`
:   Search query for metafield_draft_orders entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersSortFilter]`
    :   The type of the None singleton.

<a id="MetafieldDraftOrdersSortFilter"></a>

`MetafieldDraftOrdersSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_draft_orders search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was created

    `description: Literal['asc', 'desc']`
    :   Human-readable description of the metafield

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the metafield

    `key: Literal['asc', 'desc']`
    :   Key of the metafield within its namespace

    `namespace: Literal['asc', 'desc']`
    :   Namespace group for the metafield

    `owner_id: Literal['asc', 'desc']`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Literal['asc', 'desc']`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Literal['asc', 'desc']`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Literal['asc', 'desc']`
    :   Serialized value stored in the metafield

<a id="MetafieldDraftOrdersStringFilter"></a>

`MetafieldDraftOrdersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the metafield was created

    `description: str`
    :   Human-readable description of the metafield

    `id: str`
    :   Unique identifier for the metafield

    `key: str`
    :   Key of the metafield within its namespace

    `namespace: str`
    :   Namespace group for the metafield

    `owner_id: str`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str`
    :   Serialized value stored in the metafield

<a id="MetafieldLocationsAndCondition"></a>

`MetafieldLocationsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldLocationsAnyCondition"></a>

`MetafieldLocationsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldLocationsAnyValueFilter"></a>

`MetafieldLocationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the metafield was created

    `description: Any`
    :   Human-readable description of the metafield

    `id: Any`
    :   Unique identifier for the metafield

    `key: Any`
    :   Key of the metafield within its namespace

    `namespace: Any`
    :   Namespace group for the metafield

    `owner_id: Any`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Any`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Any`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Any`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Any`
    :   Serialized value stored in the metafield

<a id="MetafieldLocationsContainsCondition"></a>

`MetafieldLocationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldLocationsEqCondition"></a>

`MetafieldLocationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldLocationsFuzzyCondition"></a>

`MetafieldLocationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldLocationsGtCondition"></a>

`MetafieldLocationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldLocationsGteCondition"></a>

`MetafieldLocationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldLocationsInCondition"></a>

`MetafieldLocationsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsInFilter`
    :   The type of the None singleton.

<a id="MetafieldLocationsInFilter"></a>

`MetafieldLocationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the metafield was created

    `description: list[str]`
    :   Human-readable description of the metafield

    `id: list[int]`
    :   Unique identifier for the metafield

    `key: list[str]`
    :   Key of the metafield within its namespace

    `namespace: list[str]`
    :   Namespace group for the metafield

    `owner_id: list[int]`
    :   Identifier of the resource that owns this metafield

    `owner_resource: list[str]`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: list[str]`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: list[str]`
    :   Serialized value stored in the metafield

<a id="MetafieldLocationsKeywordCondition"></a>

`MetafieldLocationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldLocationsLikeCondition"></a>

`MetafieldLocationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldLocationsListParams"></a>

`MetafieldLocationsListParams(*args, **kwargs)`
:   Parameters for metafield_locations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `key: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `location_id: str`
    :   The type of the None singleton.

    `namespace: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

<a id="MetafieldLocationsLtCondition"></a>

`MetafieldLocationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldLocationsLteCondition"></a>

`MetafieldLocationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldLocationsNeqCondition"></a>

`MetafieldLocationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldLocationsNotCondition"></a>

`MetafieldLocationsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsAnyCondition`
    :   The type of the None singleton.

<a id="MetafieldLocationsOrCondition"></a>

`MetafieldLocationsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldLocationsSearchFilter"></a>

`MetafieldLocationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_locations search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

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

<a id="MetafieldLocationsSearchQuery"></a>

`MetafieldLocationsSearchQuery(*args, **kwargs)`
:   Search query for metafield_locations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsSortFilter]`
    :   The type of the None singleton.

<a id="MetafieldLocationsSortFilter"></a>

`MetafieldLocationsSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_locations search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was created

    `description: Literal['asc', 'desc']`
    :   Human-readable description of the metafield

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the metafield

    `key: Literal['asc', 'desc']`
    :   Key of the metafield within its namespace

    `namespace: Literal['asc', 'desc']`
    :   Namespace group for the metafield

    `owner_id: Literal['asc', 'desc']`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Literal['asc', 'desc']`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Literal['asc', 'desc']`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Literal['asc', 'desc']`
    :   Serialized value stored in the metafield

<a id="MetafieldLocationsStringFilter"></a>

`MetafieldLocationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the metafield was created

    `description: str`
    :   Human-readable description of the metafield

    `id: str`
    :   Unique identifier for the metafield

    `key: str`
    :   Key of the metafield within its namespace

    `namespace: str`
    :   Namespace group for the metafield

    `owner_id: str`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str`
    :   Serialized value stored in the metafield

<a id="MetafieldOrdersAndCondition"></a>

`MetafieldOrdersAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldOrdersAnyCondition"></a>

`MetafieldOrdersAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldOrdersAnyValueFilter"></a>

`MetafieldOrdersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the metafield was created

    `description: Any`
    :   Human-readable description of the metafield

    `id: Any`
    :   Unique identifier for the metafield

    `key: Any`
    :   Key of the metafield within its namespace

    `namespace: Any`
    :   Namespace group for the metafield

    `owner_id: Any`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Any`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Any`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Any`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Any`
    :   Serialized value stored in the metafield

<a id="MetafieldOrdersContainsCondition"></a>

`MetafieldOrdersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldOrdersEqCondition"></a>

`MetafieldOrdersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldOrdersFuzzyCondition"></a>

`MetafieldOrdersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersStringFilter`
    :   The type of the None singleton.

<a id="MetafieldOrdersGtCondition"></a>

`MetafieldOrdersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldOrdersGteCondition"></a>

`MetafieldOrdersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldOrdersInCondition"></a>

`MetafieldOrdersInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersInFilter`
    :   The type of the None singleton.

<a id="MetafieldOrdersInFilter"></a>

`MetafieldOrdersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the metafield was created

    `description: list[str]`
    :   Human-readable description of the metafield

    `id: list[int]`
    :   Unique identifier for the metafield

    `key: list[str]`
    :   Key of the metafield within its namespace

    `namespace: list[str]`
    :   Namespace group for the metafield

    `owner_id: list[int]`
    :   Identifier of the resource that owns this metafield

    `owner_resource: list[str]`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: list[str]`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: list[str]`
    :   Serialized value stored in the metafield

<a id="MetafieldOrdersKeywordCondition"></a>

`MetafieldOrdersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersStringFilter`
    :   The type of the None singleton.

<a id="MetafieldOrdersLikeCondition"></a>

`MetafieldOrdersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersStringFilter`
    :   The type of the None singleton.

<a id="MetafieldOrdersListParams"></a>

`MetafieldOrdersListParams(*args, **kwargs)`
:   Parameters for metafield_orders.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `key: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `namespace: str`
    :   The type of the None singleton.

    `order_id: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

<a id="MetafieldOrdersLtCondition"></a>

`MetafieldOrdersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldOrdersLteCondition"></a>

`MetafieldOrdersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldOrdersNeqCondition"></a>

`MetafieldOrdersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldOrdersNotCondition"></a>

`MetafieldOrdersNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersAnyCondition`
    :   The type of the None singleton.

<a id="MetafieldOrdersOrCondition"></a>

`MetafieldOrdersOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldOrdersSearchFilter"></a>

`MetafieldOrdersSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_orders search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

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

<a id="MetafieldOrdersSearchQuery"></a>

`MetafieldOrdersSearchQuery(*args, **kwargs)`
:   Search query for metafield_orders entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersSortFilter]`
    :   The type of the None singleton.

<a id="MetafieldOrdersSortFilter"></a>

`MetafieldOrdersSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_orders search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was created

    `description: Literal['asc', 'desc']`
    :   Human-readable description of the metafield

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the metafield

    `key: Literal['asc', 'desc']`
    :   Key of the metafield within its namespace

    `namespace: Literal['asc', 'desc']`
    :   Namespace group for the metafield

    `owner_id: Literal['asc', 'desc']`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Literal['asc', 'desc']`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Literal['asc', 'desc']`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Literal['asc', 'desc']`
    :   Serialized value stored in the metafield

<a id="MetafieldOrdersStringFilter"></a>

`MetafieldOrdersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the metafield was created

    `description: str`
    :   Human-readable description of the metafield

    `id: str`
    :   Unique identifier for the metafield

    `key: str`
    :   Key of the metafield within its namespace

    `namespace: str`
    :   Namespace group for the metafield

    `owner_id: str`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str`
    :   Serialized value stored in the metafield

<a id="MetafieldProductImagesAndCondition"></a>

`MetafieldProductImagesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldProductImagesAnyCondition"></a>

`MetafieldProductImagesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldProductImagesAnyValueFilter"></a>

`MetafieldProductImagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the metafield was created

    `description: Any`
    :   Human-readable description of the metafield

    `id: Any`
    :   Unique identifier for the metafield

    `key: Any`
    :   Key of the metafield within its namespace

    `namespace: Any`
    :   Namespace group for the metafield

    `owner_id: Any`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Any`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Any`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Any`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Any`
    :   Serialized value stored in the metafield

<a id="MetafieldProductImagesContainsCondition"></a>

`MetafieldProductImagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldProductImagesEqCondition"></a>

`MetafieldProductImagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductImagesFuzzyCondition"></a>

`MetafieldProductImagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesStringFilter`
    :   The type of the None singleton.

<a id="MetafieldProductImagesGtCondition"></a>

`MetafieldProductImagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductImagesGteCondition"></a>

`MetafieldProductImagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductImagesInCondition"></a>

`MetafieldProductImagesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesInFilter`
    :   The type of the None singleton.

<a id="MetafieldProductImagesInFilter"></a>

`MetafieldProductImagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the metafield was created

    `description: list[str]`
    :   Human-readable description of the metafield

    `id: list[int]`
    :   Unique identifier for the metafield

    `key: list[str]`
    :   Key of the metafield within its namespace

    `namespace: list[str]`
    :   Namespace group for the metafield

    `owner_id: list[int]`
    :   Identifier of the resource that owns this metafield

    `owner_resource: list[str]`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: list[str]`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: list[str]`
    :   Serialized value stored in the metafield

<a id="MetafieldProductImagesKeywordCondition"></a>

`MetafieldProductImagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesStringFilter`
    :   The type of the None singleton.

<a id="MetafieldProductImagesLikeCondition"></a>

`MetafieldProductImagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesStringFilter`
    :   The type of the None singleton.

<a id="MetafieldProductImagesListParams"></a>

`MetafieldProductImagesListParams(*args, **kwargs)`
:   Parameters for metafield_product_images.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `image_id: str`
    :   The type of the None singleton.

    `key: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `namespace: str`
    :   The type of the None singleton.

    `product_id: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

<a id="MetafieldProductImagesLtCondition"></a>

`MetafieldProductImagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductImagesLteCondition"></a>

`MetafieldProductImagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductImagesNeqCondition"></a>

`MetafieldProductImagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductImagesNotCondition"></a>

`MetafieldProductImagesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesAnyCondition`
    :   The type of the None singleton.

<a id="MetafieldProductImagesOrCondition"></a>

`MetafieldProductImagesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldProductImagesSearchFilter"></a>

`MetafieldProductImagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_product_images search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

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

<a id="MetafieldProductImagesSearchQuery"></a>

`MetafieldProductImagesSearchQuery(*args, **kwargs)`
:   Search query for metafield_product_images entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesSortFilter]`
    :   The type of the None singleton.

<a id="MetafieldProductImagesSortFilter"></a>

`MetafieldProductImagesSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_product_images search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was created

    `description: Literal['asc', 'desc']`
    :   Human-readable description of the metafield

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the metafield

    `key: Literal['asc', 'desc']`
    :   Key of the metafield within its namespace

    `namespace: Literal['asc', 'desc']`
    :   Namespace group for the metafield

    `owner_id: Literal['asc', 'desc']`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Literal['asc', 'desc']`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Literal['asc', 'desc']`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Literal['asc', 'desc']`
    :   Serialized value stored in the metafield

<a id="MetafieldProductImagesStringFilter"></a>

`MetafieldProductImagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the metafield was created

    `description: str`
    :   Human-readable description of the metafield

    `id: str`
    :   Unique identifier for the metafield

    `key: str`
    :   Key of the metafield within its namespace

    `namespace: str`
    :   Namespace group for the metafield

    `owner_id: str`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str`
    :   Serialized value stored in the metafield

<a id="MetafieldProductVariantsAndCondition"></a>

`MetafieldProductVariantsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsAnyCondition"></a>

`MetafieldProductVariantsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsAnyValueFilter"></a>

`MetafieldProductVariantsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the metafield was created

    `description: Any`
    :   Human-readable description of the metafield

    `id: Any`
    :   Unique identifier for the metafield

    `key: Any`
    :   Key of the metafield within its namespace

    `namespace: Any`
    :   Namespace group for the metafield

    `owner_id: Any`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Any`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Any`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Any`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Any`
    :   Serialized value stored in the metafield

<a id="MetafieldProductVariantsContainsCondition"></a>

`MetafieldProductVariantsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsEqCondition"></a>

`MetafieldProductVariantsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsFuzzyCondition"></a>

`MetafieldProductVariantsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsGtCondition"></a>

`MetafieldProductVariantsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsGteCondition"></a>

`MetafieldProductVariantsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsInCondition"></a>

`MetafieldProductVariantsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsInFilter`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsInFilter"></a>

`MetafieldProductVariantsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the metafield was created

    `description: list[str]`
    :   Human-readable description of the metafield

    `id: list[int]`
    :   Unique identifier for the metafield

    `key: list[str]`
    :   Key of the metafield within its namespace

    `namespace: list[str]`
    :   Namespace group for the metafield

    `owner_id: list[int]`
    :   Identifier of the resource that owns this metafield

    `owner_resource: list[str]`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: list[str]`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: list[str]`
    :   Serialized value stored in the metafield

<a id="MetafieldProductVariantsKeywordCondition"></a>

`MetafieldProductVariantsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsLikeCondition"></a>

`MetafieldProductVariantsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsListParams"></a>

`MetafieldProductVariantsListParams(*args, **kwargs)`
:   Parameters for metafield_product_variants.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `key: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `namespace: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

    `variant_id: str`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsLtCondition"></a>

`MetafieldProductVariantsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsLteCondition"></a>

`MetafieldProductVariantsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsNeqCondition"></a>

`MetafieldProductVariantsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsNotCondition"></a>

`MetafieldProductVariantsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsAnyCondition`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsOrCondition"></a>

`MetafieldProductVariantsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsSearchFilter"></a>

`MetafieldProductVariantsSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_product_variants search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

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

<a id="MetafieldProductVariantsSearchQuery"></a>

`MetafieldProductVariantsSearchQuery(*args, **kwargs)`
:   Search query for metafield_product_variants entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsSortFilter]`
    :   The type of the None singleton.

<a id="MetafieldProductVariantsSortFilter"></a>

`MetafieldProductVariantsSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_product_variants search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was created

    `description: Literal['asc', 'desc']`
    :   Human-readable description of the metafield

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the metafield

    `key: Literal['asc', 'desc']`
    :   Key of the metafield within its namespace

    `namespace: Literal['asc', 'desc']`
    :   Namespace group for the metafield

    `owner_id: Literal['asc', 'desc']`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Literal['asc', 'desc']`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Literal['asc', 'desc']`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Literal['asc', 'desc']`
    :   Serialized value stored in the metafield

<a id="MetafieldProductVariantsStringFilter"></a>

`MetafieldProductVariantsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the metafield was created

    `description: str`
    :   Human-readable description of the metafield

    `id: str`
    :   Unique identifier for the metafield

    `key: str`
    :   Key of the metafield within its namespace

    `namespace: str`
    :   Namespace group for the metafield

    `owner_id: str`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str`
    :   Serialized value stored in the metafield

<a id="MetafieldProductsAndCondition"></a>

`MetafieldProductsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldProductsAnyCondition"></a>

`MetafieldProductsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldProductsAnyValueFilter"></a>

`MetafieldProductsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the metafield was created

    `description: Any`
    :   Human-readable description of the metafield

    `id: Any`
    :   Unique identifier for the metafield

    `key: Any`
    :   Key of the metafield within its namespace

    `namespace: Any`
    :   Namespace group for the metafield

    `owner_id: Any`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Any`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Any`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Any`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Any`
    :   Serialized value stored in the metafield

<a id="MetafieldProductsContainsCondition"></a>

`MetafieldProductsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldProductsEqCondition"></a>

`MetafieldProductsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductsFuzzyCondition"></a>

`MetafieldProductsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldProductsGtCondition"></a>

`MetafieldProductsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductsGteCondition"></a>

`MetafieldProductsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductsInCondition"></a>

`MetafieldProductsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsInFilter`
    :   The type of the None singleton.

<a id="MetafieldProductsInFilter"></a>

`MetafieldProductsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the metafield was created

    `description: list[str]`
    :   Human-readable description of the metafield

    `id: list[int]`
    :   Unique identifier for the metafield

    `key: list[str]`
    :   Key of the metafield within its namespace

    `namespace: list[str]`
    :   Namespace group for the metafield

    `owner_id: list[int]`
    :   Identifier of the resource that owns this metafield

    `owner_resource: list[str]`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: list[str]`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: list[str]`
    :   Serialized value stored in the metafield

<a id="MetafieldProductsKeywordCondition"></a>

`MetafieldProductsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldProductsLikeCondition"></a>

`MetafieldProductsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldProductsListParams"></a>

`MetafieldProductsListParams(*args, **kwargs)`
:   Parameters for metafield_products.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `key: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `namespace: str`
    :   The type of the None singleton.

    `product_id: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

<a id="MetafieldProductsLtCondition"></a>

`MetafieldProductsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductsLteCondition"></a>

`MetafieldProductsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductsNeqCondition"></a>

`MetafieldProductsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldProductsNotCondition"></a>

`MetafieldProductsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsAnyCondition`
    :   The type of the None singleton.

<a id="MetafieldProductsOrCondition"></a>

`MetafieldProductsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldProductsSearchFilter"></a>

`MetafieldProductsSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_products search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

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

<a id="MetafieldProductsSearchQuery"></a>

`MetafieldProductsSearchQuery(*args, **kwargs)`
:   Search query for metafield_products entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsSortFilter]`
    :   The type of the None singleton.

<a id="MetafieldProductsSortFilter"></a>

`MetafieldProductsSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_products search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was created

    `description: Literal['asc', 'desc']`
    :   Human-readable description of the metafield

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the metafield

    `key: Literal['asc', 'desc']`
    :   Key of the metafield within its namespace

    `namespace: Literal['asc', 'desc']`
    :   Namespace group for the metafield

    `owner_id: Literal['asc', 'desc']`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Literal['asc', 'desc']`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Literal['asc', 'desc']`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Literal['asc', 'desc']`
    :   Serialized value stored in the metafield

<a id="MetafieldProductsStringFilter"></a>

`MetafieldProductsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the metafield was created

    `description: str`
    :   Human-readable description of the metafield

    `id: str`
    :   Unique identifier for the metafield

    `key: str`
    :   Key of the metafield within its namespace

    `namespace: str`
    :   Namespace group for the metafield

    `owner_id: str`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str`
    :   Serialized value stored in the metafield

<a id="MetafieldShopsAndCondition"></a>

`MetafieldShopsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldShopsAnyCondition"></a>

`MetafieldShopsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldShopsAnyValueFilter"></a>

`MetafieldShopsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the metafield was created

    `description: Any`
    :   Human-readable description of the metafield

    `id: Any`
    :   Unique identifier for the metafield

    `key: Any`
    :   Key of the metafield within its namespace

    `namespace: Any`
    :   Namespace group for the metafield

    `owner_id: Any`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Any`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Any`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Any`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Any`
    :   Serialized value stored in the metafield

<a id="MetafieldShopsContainsCondition"></a>

`MetafieldShopsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldShopsEqCondition"></a>

`MetafieldShopsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldShopsFuzzyCondition"></a>

`MetafieldShopsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldShopsGetParams"></a>

`MetafieldShopsGetParams(*args, **kwargs)`
:   Parameters for metafield_shops.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `metafield_id: str`
    :   The type of the None singleton.

<a id="MetafieldShopsGtCondition"></a>

`MetafieldShopsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldShopsGteCondition"></a>

`MetafieldShopsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldShopsInCondition"></a>

`MetafieldShopsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsInFilter`
    :   The type of the None singleton.

<a id="MetafieldShopsInFilter"></a>

`MetafieldShopsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the metafield was created

    `description: list[str]`
    :   Human-readable description of the metafield

    `id: list[int]`
    :   Unique identifier for the metafield

    `key: list[str]`
    :   Key of the metafield within its namespace

    `namespace: list[str]`
    :   Namespace group for the metafield

    `owner_id: list[int]`
    :   Identifier of the resource that owns this metafield

    `owner_resource: list[str]`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: list[str]`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: list[str]`
    :   Serialized value stored in the metafield

<a id="MetafieldShopsKeywordCondition"></a>

`MetafieldShopsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldShopsLikeCondition"></a>

`MetafieldShopsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldShopsListParams"></a>

`MetafieldShopsListParams(*args, **kwargs)`
:   Parameters for metafield_shops.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `key: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `namespace: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="MetafieldShopsLtCondition"></a>

`MetafieldShopsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldShopsLteCondition"></a>

`MetafieldShopsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldShopsNeqCondition"></a>

`MetafieldShopsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldShopsNotCondition"></a>

`MetafieldShopsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsAnyCondition`
    :   The type of the None singleton.

<a id="MetafieldShopsOrCondition"></a>

`MetafieldShopsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldShopsSearchFilter"></a>

`MetafieldShopsSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_shops search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

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

<a id="MetafieldShopsSearchQuery"></a>

`MetafieldShopsSearchQuery(*args, **kwargs)`
:   Search query for metafield_shops entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsSortFilter]`
    :   The type of the None singleton.

<a id="MetafieldShopsSortFilter"></a>

`MetafieldShopsSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_shops search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was created

    `description: Literal['asc', 'desc']`
    :   Human-readable description of the metafield

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the metafield

    `key: Literal['asc', 'desc']`
    :   Key of the metafield within its namespace

    `namespace: Literal['asc', 'desc']`
    :   Namespace group for the metafield

    `owner_id: Literal['asc', 'desc']`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Literal['asc', 'desc']`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Literal['asc', 'desc']`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Literal['asc', 'desc']`
    :   Serialized value stored in the metafield

<a id="MetafieldShopsStringFilter"></a>

`MetafieldShopsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the metafield was created

    `description: str`
    :   Human-readable description of the metafield

    `id: str`
    :   Unique identifier for the metafield

    `key: str`
    :   Key of the metafield within its namespace

    `namespace: str`
    :   Namespace group for the metafield

    `owner_id: str`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str`
    :   Serialized value stored in the metafield

<a id="MetafieldSmartCollectionsAndCondition"></a>

`MetafieldSmartCollectionsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsAnyCondition"></a>

`MetafieldSmartCollectionsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsAnyValueFilter"></a>

`MetafieldSmartCollectionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the metafield was created

    `description: Any`
    :   Human-readable description of the metafield

    `id: Any`
    :   Unique identifier for the metafield

    `key: Any`
    :   Key of the metafield within its namespace

    `namespace: Any`
    :   Namespace group for the metafield

    `owner_id: Any`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Any`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Any`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Any`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Any`
    :   Serialized value stored in the metafield

<a id="MetafieldSmartCollectionsContainsCondition"></a>

`MetafieldSmartCollectionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsAnyValueFilter`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsEqCondition"></a>

`MetafieldSmartCollectionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsFuzzyCondition"></a>

`MetafieldSmartCollectionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsGtCondition"></a>

`MetafieldSmartCollectionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsGteCondition"></a>

`MetafieldSmartCollectionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsInCondition"></a>

`MetafieldSmartCollectionsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsInFilter`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsInFilter"></a>

`MetafieldSmartCollectionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the metafield was created

    `description: list[str]`
    :   Human-readable description of the metafield

    `id: list[int]`
    :   Unique identifier for the metafield

    `key: list[str]`
    :   Key of the metafield within its namespace

    `namespace: list[str]`
    :   Namespace group for the metafield

    `owner_id: list[int]`
    :   Identifier of the resource that owns this metafield

    `owner_resource: list[str]`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: list[str]`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: list[str]`
    :   Serialized value stored in the metafield

<a id="MetafieldSmartCollectionsKeywordCondition"></a>

`MetafieldSmartCollectionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsLikeCondition"></a>

`MetafieldSmartCollectionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsStringFilter`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsListParams"></a>

`MetafieldSmartCollectionsListParams(*args, **kwargs)`
:   Parameters for metafield_smart_collections.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_id: str`
    :   The type of the None singleton.

    `key: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `namespace: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsLtCondition"></a>

`MetafieldSmartCollectionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsLteCondition"></a>

`MetafieldSmartCollectionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsNeqCondition"></a>

`MetafieldSmartCollectionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsNotCondition"></a>

`MetafieldSmartCollectionsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsAnyCondition`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsOrCondition"></a>

`MetafieldSmartCollectionsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsAnyCondition]`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsSearchFilter"></a>

`MetafieldSmartCollectionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_smart_collections search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the metafield was created

    `description: str | None`
    :   Human-readable description of the metafield

    `id: int | None`
    :   Unique identifier for the metafield

    `key: str | None`
    :   Key of the metafield within its namespace

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

<a id="MetafieldSmartCollectionsSearchQuery"></a>

`MetafieldSmartCollectionsSearchQuery(*args, **kwargs)`
:   Search query for metafield_smart_collections entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsSortFilter]`
    :   The type of the None singleton.

<a id="MetafieldSmartCollectionsSortFilter"></a>

`MetafieldSmartCollectionsSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_smart_collections search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was created

    `description: Literal['asc', 'desc']`
    :   Human-readable description of the metafield

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the metafield

    `key: Literal['asc', 'desc']`
    :   Key of the metafield within its namespace

    `namespace: Literal['asc', 'desc']`
    :   Namespace group for the metafield

    `owner_id: Literal['asc', 'desc']`
    :   Identifier of the resource that owns this metafield

    `owner_resource: Literal['asc', 'desc']`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: Literal['asc', 'desc']`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: Literal['asc', 'desc']`
    :   Serialized value stored in the metafield

<a id="MetafieldSmartCollectionsStringFilter"></a>

`MetafieldSmartCollectionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the metafield was created

    `description: str`
    :   Human-readable description of the metafield

    `id: str`
    :   Unique identifier for the metafield

    `key: str`
    :   Key of the metafield within its namespace

    `namespace: str`
    :   Namespace group for the metafield

    `owner_id: str`
    :   Identifier of the resource that owns this metafield

    `owner_resource: str`
    :   Resource type that owns this metafield (e.g. `product`, `customer`)

    `type_: str`
    :   Shopify metafield type (e.g. `single_line_text_field`, `json`)

    `updated_at: str`
    :   ISO 8601 timestamp when the metafield was last updated

    `value: str`
    :   Serialized value stored in the metafield

<a id="OrderRefundsAndCondition"></a>

`OrderRefundsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.OrderRefundsEqCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsGtCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsGteCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLtCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLteCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsInCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsNotCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsAndCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsOrCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsAnyCondition]`
    :   The type of the None singleton.

<a id="OrderRefundsAnyCondition"></a>

`OrderRefundsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsAnyValueFilter`
    :   The type of the None singleton.

<a id="OrderRefundsAnyValueFilter"></a>

`OrderRefundsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the refund was created

    `id: Any`
    :   Unique identifier for the refund

    `note: Any`
    :   Merchant-provided note explaining the refund

    `order_id: Any`
    :   Identifier of the refunded order

    `processed_at: Any`
    :   ISO 8601 timestamp when the refund was processed

    `user_id: Any`
    :   Identifier of the staff user who processed the refund

<a id="OrderRefundsContainsCondition"></a>

`OrderRefundsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsAnyValueFilter`
    :   The type of the None singleton.

<a id="OrderRefundsEqCondition"></a>

`OrderRefundsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsSearchFilter`
    :   The type of the None singleton.

<a id="OrderRefundsFuzzyCondition"></a>

`OrderRefundsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsStringFilter`
    :   The type of the None singleton.

<a id="OrderRefundsGetParams"></a>

`OrderRefundsGetParams(*args, **kwargs)`
:   Parameters for order_refunds.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_id: str`
    :   The type of the None singleton.

    `refund_id: str`
    :   The type of the None singleton.

<a id="OrderRefundsGtCondition"></a>

`OrderRefundsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsSearchFilter`
    :   The type of the None singleton.

<a id="OrderRefundsGteCondition"></a>

`OrderRefundsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsSearchFilter`
    :   The type of the None singleton.

<a id="OrderRefundsInCondition"></a>

`OrderRefundsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsInFilter`
    :   The type of the None singleton.

<a id="OrderRefundsInFilter"></a>

`OrderRefundsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the refund was created

    `id: list[int]`
    :   Unique identifier for the refund

    `note: list[str]`
    :   Merchant-provided note explaining the refund

    `order_id: list[int]`
    :   Identifier of the refunded order

    `processed_at: list[str]`
    :   ISO 8601 timestamp when the refund was processed

    `user_id: list[int]`
    :   Identifier of the staff user who processed the refund

<a id="OrderRefundsKeywordCondition"></a>

`OrderRefundsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsStringFilter`
    :   The type of the None singleton.

<a id="OrderRefundsLikeCondition"></a>

`OrderRefundsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsStringFilter`
    :   The type of the None singleton.

<a id="OrderRefundsListParams"></a>

`OrderRefundsListParams(*args, **kwargs)`
:   Parameters for order_refunds.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `order_id: str`
    :   The type of the None singleton.

<a id="OrderRefundsLtCondition"></a>

`OrderRefundsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsSearchFilter`
    :   The type of the None singleton.

<a id="OrderRefundsLteCondition"></a>

`OrderRefundsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsSearchFilter`
    :   The type of the None singleton.

<a id="OrderRefundsNeqCondition"></a>

`OrderRefundsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsSearchFilter`
    :   The type of the None singleton.

<a id="OrderRefundsNotCondition"></a>

`OrderRefundsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsEqCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsGtCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsGteCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLtCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLteCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsInCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsNotCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsAndCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsOrCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsAnyCondition`
    :   The type of the None singleton.

<a id="OrderRefundsOrCondition"></a>

`OrderRefundsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.OrderRefundsEqCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsGtCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsGteCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLtCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLteCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsInCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsNotCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsAndCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsOrCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsAnyCondition]`
    :   The type of the None singleton.

<a id="OrderRefundsSearchFilter"></a>

`OrderRefundsSearchFilter(*args, **kwargs)`
:   Available fields for filtering order_refunds search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the refund was created

    `id: int | None`
    :   Unique identifier for the refund

    `note: str | None`
    :   Merchant-provided note explaining the refund

    `order_id: int | None`
    :   Identifier of the refunded order

    `processed_at: str | None`
    :   ISO 8601 timestamp when the refund was processed

    `user_id: int | None`
    :   Identifier of the staff user who processed the refund

<a id="OrderRefundsSearchQuery"></a>

`OrderRefundsSearchQuery(*args, **kwargs)`
:   Search query for order_refunds entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsEqCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsGtCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsGteCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLtCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLteCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsInCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsNotCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsAndCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsOrCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.OrderRefundsSortFilter]`
    :   The type of the None singleton.

<a id="OrderRefundsSortFilter"></a>

`OrderRefundsSortFilter(*args, **kwargs)`
:   Available fields for sorting order_refunds search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the refund was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the refund

    `note: Literal['asc', 'desc']`
    :   Merchant-provided note explaining the refund

    `order_id: Literal['asc', 'desc']`
    :   Identifier of the refunded order

    `processed_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the refund was processed

    `user_id: Literal['asc', 'desc']`
    :   Identifier of the staff user who processed the refund

<a id="OrderRefundsStringFilter"></a>

`OrderRefundsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the refund was created

    `id: str`
    :   Unique identifier for the refund

    `note: str`
    :   Merchant-provided note explaining the refund

    `order_id: str`
    :   Identifier of the refunded order

    `processed_at: str`
    :   ISO 8601 timestamp when the refund was processed

    `user_id: str`
    :   Identifier of the staff user who processed the refund

<a id="OrdersGetParams"></a>

`OrdersGetParams(*args, **kwargs)`
:   Parameters for orders.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_id: str`
    :   The type of the None singleton.

<a id="OrdersListParams"></a>

`OrdersListParams(*args, **kwargs)`
:   Parameters for orders.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at_max: str`
    :   The type of the None singleton.

    `created_at_min: str`
    :   The type of the None singleton.

    `financial_status: str`
    :   The type of the None singleton.

    `fulfillment_status: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `updated_at_max: str`
    :   The type of the None singleton.

    `updated_at_min: str`
    :   The type of the None singleton.

<a id="PriceRulesAndCondition"></a>

`PriceRulesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.PriceRulesEqCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesGtCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesGteCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLtCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLteCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesInCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesNotCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesAndCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesOrCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesAnyCondition]`
    :   The type of the None singleton.

<a id="PriceRulesAnyCondition"></a>

`PriceRulesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.PriceRulesAnyValueFilter`
    :   The type of the None singleton.

<a id="PriceRulesAnyValueFilter"></a>

`PriceRulesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allocation_method: Any`
    :   How the discount is allocated (`each` or `across`)

    `created_at: Any`
    :   ISO 8601 timestamp when the rule was created

    `ends_at: Any`
    :   ISO 8601 timestamp when the rule stops being active, if applicable

    `id: Any`
    :   Unique identifier for the price rule

    `starts_at: Any`
    :   ISO 8601 timestamp when the rule starts being active

    `target_selection: Any`
    :   Which target items the rule applies to (`all` or `entitled`)

    `target_type: Any`
    :   Type of target the rule applies to (`line_item` or `shipping_line`)

    `title: Any`
    :   Administrative title of the price rule

    `updated_at: Any`
    :   ISO 8601 timestamp when the rule was last updated

    `value: Any`
    :   Discount value applied by the rule

    `value_type: Any`
    :   How the discount value is interpreted (`fixed_amount` or `percentage`)

<a id="PriceRulesContainsCondition"></a>

`PriceRulesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.PriceRulesAnyValueFilter`
    :   The type of the None singleton.

<a id="PriceRulesEqCondition"></a>

`PriceRulesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.PriceRulesSearchFilter`
    :   The type of the None singleton.

<a id="PriceRulesFuzzyCondition"></a>

`PriceRulesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.PriceRulesStringFilter`
    :   The type of the None singleton.

<a id="PriceRulesGetParams"></a>

`PriceRulesGetParams(*args, **kwargs)`
:   Parameters for price_rules.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `price_rule_id: str`
    :   The type of the None singleton.

<a id="PriceRulesGtCondition"></a>

`PriceRulesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.PriceRulesSearchFilter`
    :   The type of the None singleton.

<a id="PriceRulesGteCondition"></a>

`PriceRulesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.PriceRulesSearchFilter`
    :   The type of the None singleton.

<a id="PriceRulesInCondition"></a>

`PriceRulesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.PriceRulesInFilter`
    :   The type of the None singleton.

<a id="PriceRulesInFilter"></a>

`PriceRulesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allocation_method: list[str]`
    :   How the discount is allocated (`each` or `across`)

    `created_at: list[str]`
    :   ISO 8601 timestamp when the rule was created

    `ends_at: list[str]`
    :   ISO 8601 timestamp when the rule stops being active, if applicable

    `id: list[int]`
    :   Unique identifier for the price rule

    `starts_at: list[str]`
    :   ISO 8601 timestamp when the rule starts being active

    `target_selection: list[str]`
    :   Which target items the rule applies to (`all` or `entitled`)

    `target_type: list[str]`
    :   Type of target the rule applies to (`line_item` or `shipping_line`)

    `title: list[str]`
    :   Administrative title of the price rule

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the rule was last updated

    `value: list[str]`
    :   Discount value applied by the rule

    `value_type: list[str]`
    :   How the discount value is interpreted (`fixed_amount` or `percentage`)

<a id="PriceRulesKeywordCondition"></a>

`PriceRulesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.PriceRulesStringFilter`
    :   The type of the None singleton.

<a id="PriceRulesLikeCondition"></a>

`PriceRulesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.PriceRulesStringFilter`
    :   The type of the None singleton.

<a id="PriceRulesListParams"></a>

`PriceRulesListParams(*args, **kwargs)`
:   Parameters for price_rules.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at_max: str`
    :   The type of the None singleton.

    `created_at_min: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

    `updated_at_max: str`
    :   The type of the None singleton.

    `updated_at_min: str`
    :   The type of the None singleton.

<a id="PriceRulesLtCondition"></a>

`PriceRulesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.PriceRulesSearchFilter`
    :   The type of the None singleton.

<a id="PriceRulesLteCondition"></a>

`PriceRulesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.PriceRulesSearchFilter`
    :   The type of the None singleton.

<a id="PriceRulesNeqCondition"></a>

`PriceRulesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.PriceRulesSearchFilter`
    :   The type of the None singleton.

<a id="PriceRulesNotCondition"></a>

`PriceRulesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.PriceRulesEqCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesGtCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesGteCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLtCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLteCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesInCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesNotCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesAndCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesOrCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesAnyCondition`
    :   The type of the None singleton.

<a id="PriceRulesOrCondition"></a>

`PriceRulesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.PriceRulesEqCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesGtCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesGteCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLtCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLteCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesInCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesNotCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesAndCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesOrCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesAnyCondition]`
    :   The type of the None singleton.

<a id="PriceRulesSearchFilter"></a>

`PriceRulesSearchFilter(*args, **kwargs)`
:   Available fields for filtering price_rules search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allocation_method: str | None`
    :   How the discount is allocated (`each` or `across`)

    `created_at: str | None`
    :   ISO 8601 timestamp when the rule was created

    `ends_at: str | None`
    :   ISO 8601 timestamp when the rule stops being active, if applicable

    `id: int | None`
    :   Unique identifier for the price rule

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

<a id="PriceRulesSearchQuery"></a>

`PriceRulesSearchQuery(*args, **kwargs)`
:   Search query for price_rules entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.PriceRulesEqCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesGtCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesGteCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLtCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLteCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesInCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesNotCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesAndCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesOrCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.PriceRulesSortFilter]`
    :   The type of the None singleton.

<a id="PriceRulesSortFilter"></a>

`PriceRulesSortFilter(*args, **kwargs)`
:   Available fields for sorting price_rules search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allocation_method: Literal['asc', 'desc']`
    :   How the discount is allocated (`each` or `across`)

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the rule was created

    `ends_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the rule stops being active, if applicable

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the price rule

    `starts_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the rule starts being active

    `target_selection: Literal['asc', 'desc']`
    :   Which target items the rule applies to (`all` or `entitled`)

    `target_type: Literal['asc', 'desc']`
    :   Type of target the rule applies to (`line_item` or `shipping_line`)

    `title: Literal['asc', 'desc']`
    :   Administrative title of the price rule

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the rule was last updated

    `value: Literal['asc', 'desc']`
    :   Discount value applied by the rule

    `value_type: Literal['asc', 'desc']`
    :   How the discount value is interpreted (`fixed_amount` or `percentage`)

<a id="PriceRulesStringFilter"></a>

`PriceRulesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allocation_method: str`
    :   How the discount is allocated (`each` or `across`)

    `created_at: str`
    :   ISO 8601 timestamp when the rule was created

    `ends_at: str`
    :   ISO 8601 timestamp when the rule stops being active, if applicable

    `id: str`
    :   Unique identifier for the price rule

    `starts_at: str`
    :   ISO 8601 timestamp when the rule starts being active

    `target_selection: str`
    :   Which target items the rule applies to (`all` or `entitled`)

    `target_type: str`
    :   Type of target the rule applies to (`line_item` or `shipping_line`)

    `title: str`
    :   Administrative title of the price rule

    `updated_at: str`
    :   ISO 8601 timestamp when the rule was last updated

    `value: str`
    :   Discount value applied by the rule

    `value_type: str`
    :   How the discount value is interpreted (`fixed_amount` or `percentage`)

<a id="ProductImagesAndCondition"></a>

`ProductImagesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.ProductImagesEqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesGtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesGteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesInCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesNotCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesAndCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesOrCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesAnyCondition]`
    :   The type of the None singleton.

<a id="ProductImagesAnyCondition"></a>

`ProductImagesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.ProductImagesAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductImagesAnyValueFilter"></a>

`ProductImagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alt: Any`
    :   Alt text for the image

    `created_at: Any`
    :   ISO 8601 timestamp when the image was created

    `height: Any`
    :   Image height in pixels

    `id: Any`
    :   Unique identifier for the product image

    `position: Any`
    :   Display position of the image within the product

    `product_id: Any`
    :   Identifier of the product the image belongs to

    `src: Any`
    :   Public URL of the image

    `updated_at: Any`
    :   ISO 8601 timestamp when the image was last updated

    `width: Any`
    :   Image width in pixels

<a id="ProductImagesContainsCondition"></a>

`ProductImagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.ProductImagesAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductImagesEqCondition"></a>

`ProductImagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.ProductImagesSearchFilter`
    :   The type of the None singleton.

<a id="ProductImagesFuzzyCondition"></a>

`ProductImagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.ProductImagesStringFilter`
    :   The type of the None singleton.

<a id="ProductImagesGetParams"></a>

`ProductImagesGetParams(*args, **kwargs)`
:   Parameters for product_images.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `image_id: str`
    :   The type of the None singleton.

    `product_id: str`
    :   The type of the None singleton.

<a id="ProductImagesGtCondition"></a>

`ProductImagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.ProductImagesSearchFilter`
    :   The type of the None singleton.

<a id="ProductImagesGteCondition"></a>

`ProductImagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.ProductImagesSearchFilter`
    :   The type of the None singleton.

<a id="ProductImagesInCondition"></a>

`ProductImagesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.ProductImagesInFilter`
    :   The type of the None singleton.

<a id="ProductImagesInFilter"></a>

`ProductImagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alt: list[str]`
    :   Alt text for the image

    `created_at: list[str]`
    :   ISO 8601 timestamp when the image was created

    `height: list[int]`
    :   Image height in pixels

    `id: list[int]`
    :   Unique identifier for the product image

    `position: list[int]`
    :   Display position of the image within the product

    `product_id: list[int]`
    :   Identifier of the product the image belongs to

    `src: list[str]`
    :   Public URL of the image

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the image was last updated

    `width: list[int]`
    :   Image width in pixels

<a id="ProductImagesKeywordCondition"></a>

`ProductImagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.ProductImagesStringFilter`
    :   The type of the None singleton.

<a id="ProductImagesLikeCondition"></a>

`ProductImagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.ProductImagesStringFilter`
    :   The type of the None singleton.

<a id="ProductImagesListParams"></a>

`ProductImagesListParams(*args, **kwargs)`
:   Parameters for product_images.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `product_id: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

<a id="ProductImagesLtCondition"></a>

`ProductImagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.ProductImagesSearchFilter`
    :   The type of the None singleton.

<a id="ProductImagesLteCondition"></a>

`ProductImagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.ProductImagesSearchFilter`
    :   The type of the None singleton.

<a id="ProductImagesNeqCondition"></a>

`ProductImagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.ProductImagesSearchFilter`
    :   The type of the None singleton.

<a id="ProductImagesNotCondition"></a>

`ProductImagesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.ProductImagesEqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesGtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesGteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesInCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesNotCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesAndCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesOrCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesAnyCondition`
    :   The type of the None singleton.

<a id="ProductImagesOrCondition"></a>

`ProductImagesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.ProductImagesEqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesGtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesGteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesInCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesNotCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesAndCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesOrCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesAnyCondition]`
    :   The type of the None singleton.

<a id="ProductImagesSearchFilter"></a>

`ProductImagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering product_images search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alt: str | None`
    :   Alt text for the image

    `created_at: str | None`
    :   ISO 8601 timestamp when the image was created

    `height: int | None`
    :   Image height in pixels

    `id: int | None`
    :   Unique identifier for the product image

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

<a id="ProductImagesSearchQuery"></a>

`ProductImagesSearchQuery(*args, **kwargs)`
:   Search query for product_images entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.ProductImagesEqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesGtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesGteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesInCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesNotCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesAndCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesOrCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.ProductImagesSortFilter]`
    :   The type of the None singleton.

<a id="ProductImagesSortFilter"></a>

`ProductImagesSortFilter(*args, **kwargs)`
:   Available fields for sorting product_images search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alt: Literal['asc', 'desc']`
    :   Alt text for the image

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the image was created

    `height: Literal['asc', 'desc']`
    :   Image height in pixels

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the product image

    `position: Literal['asc', 'desc']`
    :   Display position of the image within the product

    `product_id: Literal['asc', 'desc']`
    :   Identifier of the product the image belongs to

    `src: Literal['asc', 'desc']`
    :   Public URL of the image

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the image was last updated

    `width: Literal['asc', 'desc']`
    :   Image width in pixels

<a id="ProductImagesStringFilter"></a>

`ProductImagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alt: str`
    :   Alt text for the image

    `created_at: str`
    :   ISO 8601 timestamp when the image was created

    `height: str`
    :   Image height in pixels

    `id: str`
    :   Unique identifier for the product image

    `position: str`
    :   Display position of the image within the product

    `product_id: str`
    :   Identifier of the product the image belongs to

    `src: str`
    :   Public URL of the image

    `updated_at: str`
    :   ISO 8601 timestamp when the image was last updated

    `width: str`
    :   Image width in pixels

<a id="ProductVariantsAndCondition"></a>

`ProductVariantsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.ProductVariantsEqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsGtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsGteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsInCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsNotCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsAndCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsOrCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsAnyCondition]`
    :   The type of the None singleton.

<a id="ProductVariantsAnyCondition"></a>

`ProductVariantsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductVariantsAnyValueFilter"></a>

`ProductVariantsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `compare_at_price: Any`
    :   Original (compare-at) price of the variant, if set

    `created_at: Any`
    :   ISO 8601 timestamp when the variant was created

    `id: Any`
    :   Unique identifier for the product variant

    `inventory_policy: Any`
    :   Behaviour when out of stock (`deny` or `continue`)

    `position: Any`
    :   Display position of the variant within the product

    `price: Any`
    :   Price of the variant in the shop's currency

    `product_id: Any`
    :   Identifier of the parent product

    `sku: Any`
    :   Stock keeping unit for the variant

    `title: Any`
    :   Display title of the variant

    `updated_at: Any`
    :   ISO 8601 timestamp when the variant was last updated

<a id="ProductVariantsContainsCondition"></a>

`ProductVariantsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProductVariantsEqCondition"></a>

`ProductVariantsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsSearchFilter`
    :   The type of the None singleton.

<a id="ProductVariantsFuzzyCondition"></a>

`ProductVariantsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsStringFilter`
    :   The type of the None singleton.

<a id="ProductVariantsGetParams"></a>

`ProductVariantsGetParams(*args, **kwargs)`
:   Parameters for product_variants.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `variant_id: str`
    :   The type of the None singleton.

<a id="ProductVariantsGtCondition"></a>

`ProductVariantsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsSearchFilter`
    :   The type of the None singleton.

<a id="ProductVariantsGteCondition"></a>

`ProductVariantsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsSearchFilter`
    :   The type of the None singleton.

<a id="ProductVariantsInCondition"></a>

`ProductVariantsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsInFilter`
    :   The type of the None singleton.

<a id="ProductVariantsInFilter"></a>

`ProductVariantsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `compare_at_price: list[str]`
    :   Original (compare-at) price of the variant, if set

    `created_at: list[str]`
    :   ISO 8601 timestamp when the variant was created

    `id: list[int]`
    :   Unique identifier for the product variant

    `inventory_policy: list[str]`
    :   Behaviour when out of stock (`deny` or `continue`)

    `position: list[int]`
    :   Display position of the variant within the product

    `price: list[str]`
    :   Price of the variant in the shop's currency

    `product_id: list[int]`
    :   Identifier of the parent product

    `sku: list[str]`
    :   Stock keeping unit for the variant

    `title: list[str]`
    :   Display title of the variant

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the variant was last updated

<a id="ProductVariantsKeywordCondition"></a>

`ProductVariantsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsStringFilter`
    :   The type of the None singleton.

<a id="ProductVariantsLikeCondition"></a>

`ProductVariantsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsStringFilter`
    :   The type of the None singleton.

<a id="ProductVariantsListParams"></a>

`ProductVariantsListParams(*args, **kwargs)`
:   Parameters for product_variants.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `product_id: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

<a id="ProductVariantsLtCondition"></a>

`ProductVariantsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsSearchFilter`
    :   The type of the None singleton.

<a id="ProductVariantsLteCondition"></a>

`ProductVariantsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsSearchFilter`
    :   The type of the None singleton.

<a id="ProductVariantsNeqCondition"></a>

`ProductVariantsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsSearchFilter`
    :   The type of the None singleton.

<a id="ProductVariantsNotCondition"></a>

`ProductVariantsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsEqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsGtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsGteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsInCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsNotCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsAndCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsOrCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsAnyCondition`
    :   The type of the None singleton.

<a id="ProductVariantsOrCondition"></a>

`ProductVariantsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.ProductVariantsEqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsGtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsGteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsInCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsNotCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsAndCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsOrCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsAnyCondition]`
    :   The type of the None singleton.

<a id="ProductVariantsSearchFilter"></a>

`ProductVariantsSearchFilter(*args, **kwargs)`
:   Available fields for filtering product_variants search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `compare_at_price: str | None`
    :   Original (compare-at) price of the variant, if set

    `created_at: str | None`
    :   ISO 8601 timestamp when the variant was created

    `id: int | None`
    :   Unique identifier for the product variant

    `inventory_policy: str | None`
    :   Behaviour when out of stock (`deny` or `continue`)

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

<a id="ProductVariantsSearchQuery"></a>

`ProductVariantsSearchQuery(*args, **kwargs)`
:   Search query for product_variants entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsEqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsGtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsGteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsInCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsNotCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsAndCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsOrCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.ProductVariantsSortFilter]`
    :   The type of the None singleton.

<a id="ProductVariantsSortFilter"></a>

`ProductVariantsSortFilter(*args, **kwargs)`
:   Available fields for sorting product_variants search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `compare_at_price: Literal['asc', 'desc']`
    :   Original (compare-at) price of the variant, if set

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the variant was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the product variant

    `inventory_policy: Literal['asc', 'desc']`
    :   Behaviour when out of stock (`deny` or `continue`)

    `position: Literal['asc', 'desc']`
    :   Display position of the variant within the product

    `price: Literal['asc', 'desc']`
    :   Price of the variant in the shop's currency

    `product_id: Literal['asc', 'desc']`
    :   Identifier of the parent product

    `sku: Literal['asc', 'desc']`
    :   Stock keeping unit for the variant

    `title: Literal['asc', 'desc']`
    :   Display title of the variant

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the variant was last updated

<a id="ProductVariantsStringFilter"></a>

`ProductVariantsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `compare_at_price: str`
    :   Original (compare-at) price of the variant, if set

    `created_at: str`
    :   ISO 8601 timestamp when the variant was created

    `id: str`
    :   Unique identifier for the product variant

    `inventory_policy: str`
    :   Behaviour when out of stock (`deny` or `continue`)

    `position: str`
    :   Display position of the variant within the product

    `price: str`
    :   Price of the variant in the shop's currency

    `product_id: str`
    :   Identifier of the parent product

    `sku: str`
    :   Stock keeping unit for the variant

    `title: str`
    :   Display title of the variant

    `updated_at: str`
    :   ISO 8601 timestamp when the variant was last updated

<a id="ProductsGetParams"></a>

`ProductsGetParams(*args, **kwargs)`
:   Parameters for products.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `product_id: str`
    :   The type of the None singleton.

<a id="ProductsListParams"></a>

`ProductsListParams(*args, **kwargs)`
:   Parameters for products.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_id: int`
    :   The type of the None singleton.

    `created_at_max: str`
    :   The type of the None singleton.

    `created_at_min: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `product_type: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `updated_at_max: str`
    :   The type of the None singleton.

    `updated_at_min: str`
    :   The type of the None singleton.

    `vendor: str`
    :   The type of the None singleton.

<a id="ShopAndCondition"></a>

`ShopAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.ShopEqCondition | airbyte_agent_sdk.connectors.shopify.types.ShopNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ShopGtCondition | airbyte_agent_sdk.connectors.shopify.types.ShopGteCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLtCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLteCondition | airbyte_agent_sdk.connectors.shopify.types.ShopInCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ShopFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ShopKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ShopContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ShopNotCondition | airbyte_agent_sdk.connectors.shopify.types.ShopAndCondition | airbyte_agent_sdk.connectors.shopify.types.ShopOrCondition | airbyte_agent_sdk.connectors.shopify.types.ShopAnyCondition]`
    :   The type of the None singleton.

<a id="ShopAnyCondition"></a>

`ShopAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.ShopAnyValueFilter`
    :   The type of the None singleton.

<a id="ShopAnyValueFilter"></a>

`ShopAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country_code: Any`
    :   ISO 3166-1 alpha-2 country code of the shop

    `created_at: Any`
    :   ISO 8601 timestamp when the shop was created

    `currency: Any`
    :   ISO 4217 currency code used by the shop

    `domain: Any`
    :   Custom domain configured for the shop, if any

    `email: Any`
    :   Primary contact email for the shop

    `id: Any`
    :   Unique identifier for the shop

    `myshopify_domain: Any`
    :   Canonical `*.myshopify.com` domain for the shop

    `name: Any`
    :   Display name of the shop

    `plan_name: Any`
    :   Shopify plan identifier (e.g. `shopify_plus`, `basic`)

    `timezone: Any`
    :   Timezone configured for the shop (e.g. `(GMT-05:00) Eastern Time`)

    `updated_at: Any`
    :   ISO 8601 timestamp when the shop was last updated

<a id="ShopContainsCondition"></a>

`ShopContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.ShopAnyValueFilter`
    :   The type of the None singleton.

<a id="ShopEqCondition"></a>

`ShopEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.ShopSearchFilter`
    :   The type of the None singleton.

<a id="ShopFuzzyCondition"></a>

`ShopFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.ShopStringFilter`
    :   The type of the None singleton.

<a id="ShopGetParams"></a>

`ShopGetParams(*args, **kwargs)`
:   Parameters for shop.get operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ShopGtCondition"></a>

`ShopGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.ShopSearchFilter`
    :   The type of the None singleton.

<a id="ShopGteCondition"></a>

`ShopGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.ShopSearchFilter`
    :   The type of the None singleton.

<a id="ShopInCondition"></a>

`ShopInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.ShopInFilter`
    :   The type of the None singleton.

<a id="ShopInFilter"></a>

`ShopInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country_code: list[str]`
    :   ISO 3166-1 alpha-2 country code of the shop

    `created_at: list[str]`
    :   ISO 8601 timestamp when the shop was created

    `currency: list[str]`
    :   ISO 4217 currency code used by the shop

    `domain: list[str]`
    :   Custom domain configured for the shop, if any

    `email: list[str]`
    :   Primary contact email for the shop

    `id: list[int]`
    :   Unique identifier for the shop

    `myshopify_domain: list[str]`
    :   Canonical `*.myshopify.com` domain for the shop

    `name: list[str]`
    :   Display name of the shop

    `plan_name: list[str]`
    :   Shopify plan identifier (e.g. `shopify_plus`, `basic`)

    `timezone: list[str]`
    :   Timezone configured for the shop (e.g. `(GMT-05:00) Eastern Time`)

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the shop was last updated

<a id="ShopKeywordCondition"></a>

`ShopKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.ShopStringFilter`
    :   The type of the None singleton.

<a id="ShopLikeCondition"></a>

`ShopLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.ShopStringFilter`
    :   The type of the None singleton.

<a id="ShopLtCondition"></a>

`ShopLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.ShopSearchFilter`
    :   The type of the None singleton.

<a id="ShopLteCondition"></a>

`ShopLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.ShopSearchFilter`
    :   The type of the None singleton.

<a id="ShopNeqCondition"></a>

`ShopNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.ShopSearchFilter`
    :   The type of the None singleton.

<a id="ShopNotCondition"></a>

`ShopNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.ShopEqCondition | airbyte_agent_sdk.connectors.shopify.types.ShopNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ShopGtCondition | airbyte_agent_sdk.connectors.shopify.types.ShopGteCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLtCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLteCondition | airbyte_agent_sdk.connectors.shopify.types.ShopInCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ShopFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ShopKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ShopContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ShopNotCondition | airbyte_agent_sdk.connectors.shopify.types.ShopAndCondition | airbyte_agent_sdk.connectors.shopify.types.ShopOrCondition | airbyte_agent_sdk.connectors.shopify.types.ShopAnyCondition`
    :   The type of the None singleton.

<a id="ShopOrCondition"></a>

`ShopOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.ShopEqCondition | airbyte_agent_sdk.connectors.shopify.types.ShopNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ShopGtCondition | airbyte_agent_sdk.connectors.shopify.types.ShopGteCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLtCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLteCondition | airbyte_agent_sdk.connectors.shopify.types.ShopInCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ShopFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ShopKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ShopContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ShopNotCondition | airbyte_agent_sdk.connectors.shopify.types.ShopAndCondition | airbyte_agent_sdk.connectors.shopify.types.ShopOrCondition | airbyte_agent_sdk.connectors.shopify.types.ShopAnyCondition]`
    :   The type of the None singleton.

<a id="ShopSearchFilter"></a>

`ShopSearchFilter(*args, **kwargs)`
:   Available fields for filtering shop search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="ShopSearchQuery"></a>

`ShopSearchQuery(*args, **kwargs)`
:   Search query for shop entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.ShopEqCondition | airbyte_agent_sdk.connectors.shopify.types.ShopNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ShopGtCondition | airbyte_agent_sdk.connectors.shopify.types.ShopGteCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLtCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLteCondition | airbyte_agent_sdk.connectors.shopify.types.ShopInCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ShopFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ShopKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ShopContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ShopNotCondition | airbyte_agent_sdk.connectors.shopify.types.ShopAndCondition | airbyte_agent_sdk.connectors.shopify.types.ShopOrCondition | airbyte_agent_sdk.connectors.shopify.types.ShopAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.ShopSortFilter]`
    :   The type of the None singleton.

<a id="ShopSortFilter"></a>

`ShopSortFilter(*args, **kwargs)`
:   Available fields for sorting shop search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country_code: Literal['asc', 'desc']`
    :   ISO 3166-1 alpha-2 country code of the shop

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the shop was created

    `currency: Literal['asc', 'desc']`
    :   ISO 4217 currency code used by the shop

    `domain: Literal['asc', 'desc']`
    :   Custom domain configured for the shop, if any

    `email: Literal['asc', 'desc']`
    :   Primary contact email for the shop

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the shop

    `myshopify_domain: Literal['asc', 'desc']`
    :   Canonical `*.myshopify.com` domain for the shop

    `name: Literal['asc', 'desc']`
    :   Display name of the shop

    `plan_name: Literal['asc', 'desc']`
    :   Shopify plan identifier (e.g. `shopify_plus`, `basic`)

    `timezone: Literal['asc', 'desc']`
    :   Timezone configured for the shop (e.g. `(GMT-05:00) Eastern Time`)

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the shop was last updated

<a id="ShopStringFilter"></a>

`ShopStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country_code: str`
    :   ISO 3166-1 alpha-2 country code of the shop

    `created_at: str`
    :   ISO 8601 timestamp when the shop was created

    `currency: str`
    :   ISO 4217 currency code used by the shop

    `domain: str`
    :   Custom domain configured for the shop, if any

    `email: str`
    :   Primary contact email for the shop

    `id: str`
    :   Unique identifier for the shop

    `myshopify_domain: str`
    :   Canonical `*.myshopify.com` domain for the shop

    `name: str`
    :   Display name of the shop

    `plan_name: str`
    :   Shopify plan identifier (e.g. `shopify_plus`, `basic`)

    `timezone: str`
    :   Timezone configured for the shop (e.g. `(GMT-05:00) Eastern Time`)

    `updated_at: str`
    :   ISO 8601 timestamp when the shop was last updated

<a id="SmartCollectionsAndCondition"></a>

`SmartCollectionsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsAnyCondition]`
    :   The type of the None singleton.

<a id="SmartCollectionsAnyCondition"></a>

`SmartCollectionsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsAnyValueFilter`
    :   The type of the None singleton.

<a id="SmartCollectionsAnyValueFilter"></a>

`SmartCollectionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `handle: Any`
    :   URL-friendly handle for the smart collection

    `id: Any`
    :   Unique identifier for the smart collection

    `published_at: Any`
    :   ISO 8601 timestamp when the collection was published

    `published_scope: Any`
    :   Publishing scope (`web` or `global`)

    `sort_order: Any`
    :   How products are sorted within the collection

    `title: Any`
    :   Display title of the smart collection

    `updated_at: Any`
    :   ISO 8601 timestamp when the collection was last updated

<a id="SmartCollectionsContainsCondition"></a>

`SmartCollectionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsAnyValueFilter`
    :   The type of the None singleton.

<a id="SmartCollectionsEqCondition"></a>

`SmartCollectionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="SmartCollectionsFuzzyCondition"></a>

`SmartCollectionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsStringFilter`
    :   The type of the None singleton.

<a id="SmartCollectionsGetParams"></a>

`SmartCollectionsGetParams(*args, **kwargs)`
:   Parameters for smart_collections.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_id: str`
    :   The type of the None singleton.

<a id="SmartCollectionsGtCondition"></a>

`SmartCollectionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="SmartCollectionsGteCondition"></a>

`SmartCollectionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="SmartCollectionsInCondition"></a>

`SmartCollectionsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsInFilter`
    :   The type of the None singleton.

<a id="SmartCollectionsInFilter"></a>

`SmartCollectionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `handle: list[str]`
    :   URL-friendly handle for the smart collection

    `id: list[int]`
    :   Unique identifier for the smart collection

    `published_at: list[str]`
    :   ISO 8601 timestamp when the collection was published

    `published_scope: list[str]`
    :   Publishing scope (`web` or `global`)

    `sort_order: list[str]`
    :   How products are sorted within the collection

    `title: list[str]`
    :   Display title of the smart collection

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the collection was last updated

<a id="SmartCollectionsKeywordCondition"></a>

`SmartCollectionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsStringFilter`
    :   The type of the None singleton.

<a id="SmartCollectionsLikeCondition"></a>

`SmartCollectionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsStringFilter`
    :   The type of the None singleton.

<a id="SmartCollectionsListParams"></a>

`SmartCollectionsListParams(*args, **kwargs)`
:   Parameters for smart_collections.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `product_id: int`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

    `updated_at_max: str`
    :   The type of the None singleton.

    `updated_at_min: str`
    :   The type of the None singleton.

<a id="SmartCollectionsLtCondition"></a>

`SmartCollectionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="SmartCollectionsLteCondition"></a>

`SmartCollectionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="SmartCollectionsNeqCondition"></a>

`SmartCollectionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsSearchFilter`
    :   The type of the None singleton.

<a id="SmartCollectionsNotCondition"></a>

`SmartCollectionsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsAnyCondition`
    :   The type of the None singleton.

<a id="SmartCollectionsOrCondition"></a>

`SmartCollectionsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsAnyCondition]`
    :   The type of the None singleton.

<a id="SmartCollectionsSearchFilter"></a>

`SmartCollectionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering smart_collections search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `handle: str | None`
    :   URL-friendly handle for the smart collection

    `id: int | None`
    :   Unique identifier for the smart collection

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

<a id="SmartCollectionsSearchQuery"></a>

`SmartCollectionsSearchQuery(*args, **kwargs)`
:   Search query for smart_collections entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsSortFilter]`
    :   The type of the None singleton.

<a id="SmartCollectionsSortFilter"></a>

`SmartCollectionsSortFilter(*args, **kwargs)`
:   Available fields for sorting smart_collections search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `handle: Literal['asc', 'desc']`
    :   URL-friendly handle for the smart collection

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the smart collection

    `published_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the collection was published

    `published_scope: Literal['asc', 'desc']`
    :   Publishing scope (`web` or `global`)

    `sort_order: Literal['asc', 'desc']`
    :   How products are sorted within the collection

    `title: Literal['asc', 'desc']`
    :   Display title of the smart collection

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the collection was last updated

<a id="SmartCollectionsStringFilter"></a>

`SmartCollectionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `handle: str`
    :   URL-friendly handle for the smart collection

    `id: str`
    :   Unique identifier for the smart collection

    `published_at: str`
    :   ISO 8601 timestamp when the collection was published

    `published_scope: str`
    :   Publishing scope (`web` or `global`)

    `sort_order: str`
    :   How products are sorted within the collection

    `title: str`
    :   Display title of the smart collection

    `updated_at: str`
    :   ISO 8601 timestamp when the collection was last updated

<a id="TenderTransactionsAndCondition"></a>

`TenderTransactionsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsInCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsAnyCondition]`
    :   The type of the None singleton.

<a id="TenderTransactionsAnyCondition"></a>

`TenderTransactionsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsAnyValueFilter`
    :   The type of the None singleton.

<a id="TenderTransactionsAnyValueFilter"></a>

`TenderTransactionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Any`
    :   Amount of the transaction in the shop's currency

    `currency: Any`
    :   ISO 4217 currency code for the transaction amount

    `id: Any`
    :   Unique identifier for the tender transaction

    `order_id: Any`
    :   Identifier of the order the transaction belongs to

    `payment_method: Any`
    :   Payment method used (e.g. `credit_card`, `paypal`)

    `processed_at: Any`
    :   ISO 8601 timestamp when the transaction was processed

    `test: Any`
    :   Whether the transaction was a test transaction

    `user_id: Any`
    :   Identifier of the staff user who processed the transaction

<a id="TenderTransactionsContainsCondition"></a>

`TenderTransactionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsAnyValueFilter`
    :   The type of the None singleton.

<a id="TenderTransactionsEqCondition"></a>

`TenderTransactionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsSearchFilter`
    :   The type of the None singleton.

<a id="TenderTransactionsFuzzyCondition"></a>

`TenderTransactionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsStringFilter`
    :   The type of the None singleton.

<a id="TenderTransactionsGtCondition"></a>

`TenderTransactionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsSearchFilter`
    :   The type of the None singleton.

<a id="TenderTransactionsGteCondition"></a>

`TenderTransactionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsSearchFilter`
    :   The type of the None singleton.

<a id="TenderTransactionsInCondition"></a>

`TenderTransactionsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsInFilter`
    :   The type of the None singleton.

<a id="TenderTransactionsInFilter"></a>

`TenderTransactionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: list[str]`
    :   Amount of the transaction in the shop's currency

    `currency: list[str]`
    :   ISO 4217 currency code for the transaction amount

    `id: list[int]`
    :   Unique identifier for the tender transaction

    `order_id: list[int]`
    :   Identifier of the order the transaction belongs to

    `payment_method: list[str]`
    :   Payment method used (e.g. `credit_card`, `paypal`)

    `processed_at: list[str]`
    :   ISO 8601 timestamp when the transaction was processed

    `test: list[bool]`
    :   Whether the transaction was a test transaction

    `user_id: list[int]`
    :   Identifier of the staff user who processed the transaction

<a id="TenderTransactionsKeywordCondition"></a>

`TenderTransactionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsStringFilter`
    :   The type of the None singleton.

<a id="TenderTransactionsLikeCondition"></a>

`TenderTransactionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsStringFilter`
    :   The type of the None singleton.

<a id="TenderTransactionsListParams"></a>

`TenderTransactionsListParams(*args, **kwargs)`
:   Parameters for tender_transactions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `order: str`
    :   The type of the None singleton.

    `processed_at_max: str`
    :   The type of the None singleton.

    `processed_at_min: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

<a id="TenderTransactionsLtCondition"></a>

`TenderTransactionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsSearchFilter`
    :   The type of the None singleton.

<a id="TenderTransactionsLteCondition"></a>

`TenderTransactionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsSearchFilter`
    :   The type of the None singleton.

<a id="TenderTransactionsNeqCondition"></a>

`TenderTransactionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsSearchFilter`
    :   The type of the None singleton.

<a id="TenderTransactionsNotCondition"></a>

`TenderTransactionsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsInCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsAnyCondition`
    :   The type of the None singleton.

<a id="TenderTransactionsOrCondition"></a>

`TenderTransactionsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsInCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsAnyCondition]`
    :   The type of the None singleton.

<a id="TenderTransactionsSearchFilter"></a>

`TenderTransactionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering tender_transactions search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str | None`
    :   Amount of the transaction in the shop's currency

    `currency: str | None`
    :   ISO 4217 currency code for the transaction amount

    `id: int | None`
    :   Unique identifier for the tender transaction

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

<a id="TenderTransactionsSearchQuery"></a>

`TenderTransactionsSearchQuery(*args, **kwargs)`
:   Search query for tender_transactions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsInCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsSortFilter]`
    :   The type of the None singleton.

<a id="TenderTransactionsSortFilter"></a>

`TenderTransactionsSortFilter(*args, **kwargs)`
:   Available fields for sorting tender_transactions search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Literal['asc', 'desc']`
    :   Amount of the transaction in the shop's currency

    `currency: Literal['asc', 'desc']`
    :   ISO 4217 currency code for the transaction amount

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the tender transaction

    `order_id: Literal['asc', 'desc']`
    :   Identifier of the order the transaction belongs to

    `payment_method: Literal['asc', 'desc']`
    :   Payment method used (e.g. `credit_card`, `paypal`)

    `processed_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the transaction was processed

    `test: Literal['asc', 'desc']`
    :   Whether the transaction was a test transaction

    `user_id: Literal['asc', 'desc']`
    :   Identifier of the staff user who processed the transaction

<a id="TenderTransactionsStringFilter"></a>

`TenderTransactionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   Amount of the transaction in the shop's currency

    `currency: str`
    :   ISO 4217 currency code for the transaction amount

    `id: str`
    :   Unique identifier for the tender transaction

    `order_id: str`
    :   Identifier of the order the transaction belongs to

    `payment_method: str`
    :   Payment method used (e.g. `credit_card`, `paypal`)

    `processed_at: str`
    :   ISO 8601 timestamp when the transaction was processed

    `test: str`
    :   Whether the transaction was a test transaction

    `user_id: str`
    :   Identifier of the staff user who processed the transaction

<a id="TransactionsGetParams"></a>

`TransactionsGetParams(*args, **kwargs)`
:   Parameters for transactions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_id: str`
    :   The type of the None singleton.

    `transaction_id: str`
    :   The type of the None singleton.

<a id="TransactionsListParams"></a>

`TransactionsListParams(*args, **kwargs)`
:   Parameters for transactions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_id: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.