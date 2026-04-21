---
id: airbyte_agent_sdk-connectors-shopify-types
title: airbyte_agent_sdk.connectors.shopify.types
---

Module airbyte_agent_sdk.connectors.shopify.types
=================================================
Type definitions for shopify connector.

Classes
-------

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

`AbandonedCheckoutsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`AbandonedCheckoutsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsAnyValueFilter`
    :   The type of the None singleton.

`AbandonedCheckoutsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsSearchFilter`
    :   The type of the None singleton.

`AbandonedCheckoutsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsStringFilter`
    :   The type of the None singleton.

`AbandonedCheckoutsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsSearchFilter`
    :   The type of the None singleton.

`AbandonedCheckoutsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsSearchFilter`
    :   The type of the None singleton.

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

`AbandonedCheckoutsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`AbandonedCheckoutsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsStringFilter`
    :   The type of the None singleton.

`AbandonedCheckoutsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsStringFilter`
    :   The type of the None singleton.

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

`AbandonedCheckoutsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsSearchFilter`
    :   The type of the None singleton.

`AbandonedCheckoutsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsSearchFilter`
    :   The type of the None singleton.

`AbandonedCheckoutsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsSearchFilter`
    :   The type of the None singleton.

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

`AbandonedCheckoutsSearchFilter(*args, **kwargs)`
:   Available fields for filtering abandoned_checkouts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`AbandonedCheckoutsSearchQuery(*args, **kwargs)`
:   Search query for abandoned_checkouts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsEqCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsGtCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsGteCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLtCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLteCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsInCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsNotCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsAndCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsOrCondition | airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.AbandonedCheckoutsSortFilter]`
    :   The type of the None singleton.

`AbandonedCheckoutsSortFilter(*args, **kwargs)`
:   Available fields for sorting abandoned_checkouts search results.

    ### Ancestors (in MRO)

    * builtins.dict

`AbandonedCheckoutsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`CollectsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`CollectsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.CollectsAnyValueFilter`
    :   The type of the None singleton.

`CollectsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.CollectsSearchFilter`
    :   The type of the None singleton.

`CollectsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.CollectsStringFilter`
    :   The type of the None singleton.

`CollectsGetParams(*args, **kwargs)`
:   Parameters for collects.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collect_id: str`
    :   The type of the None singleton.

`CollectsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.CollectsSearchFilter`
    :   The type of the None singleton.

`CollectsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.CollectsSearchFilter`
    :   The type of the None singleton.

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

`CollectsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`CollectsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.CollectsStringFilter`
    :   The type of the None singleton.

`CollectsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.CollectsStringFilter`
    :   The type of the None singleton.

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

`CollectsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.CollectsSearchFilter`
    :   The type of the None singleton.

`CollectsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.CollectsSearchFilter`
    :   The type of the None singleton.

`CollectsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.CollectsSearchFilter`
    :   The type of the None singleton.

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

`CollectsSearchFilter(*args, **kwargs)`
:   Available fields for filtering collects search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`CollectsSearchQuery(*args, **kwargs)`
:   Search query for collects entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.CollectsEqCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsGtCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsGteCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLtCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLteCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsInCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsNotCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsAndCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsOrCondition | airbyte_agent_sdk.connectors.shopify.types.CollectsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.CollectsSortFilter]`
    :   The type of the None singleton.

`CollectsSortFilter(*args, **kwargs)`
:   Available fields for sorting collects search results.

    ### Ancestors (in MRO)

    * builtins.dict

`CollectsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`CountriesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`CountriesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.CountriesAnyValueFilter`
    :   The type of the None singleton.

`CountriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.CountriesSearchFilter`
    :   The type of the None singleton.

`CountriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.CountriesStringFilter`
    :   The type of the None singleton.

`CountriesGetParams(*args, **kwargs)`
:   Parameters for countries.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country_id: str`
    :   The type of the None singleton.

`CountriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.CountriesSearchFilter`
    :   The type of the None singleton.

`CountriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.CountriesSearchFilter`
    :   The type of the None singleton.

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

`CountriesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`CountriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.CountriesStringFilter`
    :   The type of the None singleton.

`CountriesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.CountriesStringFilter`
    :   The type of the None singleton.

`CountriesListParams(*args, **kwargs)`
:   Parameters for countries.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `since_id: int`
    :   The type of the None singleton.

`CountriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.CountriesSearchFilter`
    :   The type of the None singleton.

`CountriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.CountriesSearchFilter`
    :   The type of the None singleton.

`CountriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.CountriesSearchFilter`
    :   The type of the None singleton.

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

`CountriesSearchFilter(*args, **kwargs)`
:   Available fields for filtering countries search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`CountriesSearchQuery(*args, **kwargs)`
:   Search query for countries entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.CountriesEqCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesGtCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesGteCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLtCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLteCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesInCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesNotCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesAndCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesOrCondition | airbyte_agent_sdk.connectors.shopify.types.CountriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.CountriesSortFilter]`
    :   The type of the None singleton.

`CountriesSortFilter(*args, **kwargs)`
:   Available fields for sorting countries search results.

    ### Ancestors (in MRO)

    * builtins.dict

`CountriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`CustomCollectionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`CustomCollectionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsAnyValueFilter`
    :   The type of the None singleton.

`CustomCollectionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsSearchFilter`
    :   The type of the None singleton.

`CustomCollectionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsStringFilter`
    :   The type of the None singleton.

`CustomCollectionsGetParams(*args, **kwargs)`
:   Parameters for custom_collections.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_id: str`
    :   The type of the None singleton.

`CustomCollectionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsSearchFilter`
    :   The type of the None singleton.

`CustomCollectionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsSearchFilter`
    :   The type of the None singleton.

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

`CustomCollectionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`CustomCollectionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsStringFilter`
    :   The type of the None singleton.

`CustomCollectionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsStringFilter`
    :   The type of the None singleton.

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

`CustomCollectionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsSearchFilter`
    :   The type of the None singleton.

`CustomCollectionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsSearchFilter`
    :   The type of the None singleton.

`CustomCollectionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsSearchFilter`
    :   The type of the None singleton.

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

`CustomCollectionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering custom_collections search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`CustomCollectionsSearchQuery(*args, **kwargs)`
:   Search query for custom_collections entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.CustomCollectionsSortFilter]`
    :   The type of the None singleton.

`CustomCollectionsSortFilter(*args, **kwargs)`
:   Available fields for sorting custom_collections search results.

    ### Ancestors (in MRO)

    * builtins.dict

`CustomCollectionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

`CustomerAddressGetParams(*args, **kwargs)`
:   Parameters for customer_address.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address_id: str`
    :   The type of the None singleton.

    `customer_id: str`
    :   The type of the None singleton.

`CustomerAddressListParams(*args, **kwargs)`
:   Parameters for customer_address.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

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

`CustomersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`CustomersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.CustomersAnyValueFilter`
    :   The type of the None singleton.

`CustomersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.CustomersSearchFilter`
    :   The type of the None singleton.

`CustomersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.CustomersStringFilter`
    :   The type of the None singleton.

`CustomersGetParams(*args, **kwargs)`
:   Parameters for customers.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

`CustomersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.CustomersSearchFilter`
    :   The type of the None singleton.

`CustomersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.CustomersSearchFilter`
    :   The type of the None singleton.

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

`CustomersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`CustomersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.CustomersStringFilter`
    :   The type of the None singleton.

`CustomersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.CustomersStringFilter`
    :   The type of the None singleton.

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

`CustomersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.CustomersSearchFilter`
    :   The type of the None singleton.

`CustomersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.CustomersSearchFilter`
    :   The type of the None singleton.

`CustomersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.CustomersSearchFilter`
    :   The type of the None singleton.

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

`CustomersSearchFilter(*args, **kwargs)`
:   Available fields for filtering customers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`CustomersSearchQuery(*args, **kwargs)`
:   Search query for customers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.CustomersEqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersGtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersGteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLtCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLteCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersInCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersNotCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersAndCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersOrCondition | airbyte_agent_sdk.connectors.shopify.types.CustomersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.CustomersSortFilter]`
    :   The type of the None singleton.

`CustomersSortFilter(*args, **kwargs)`
:   Available fields for sorting customers search results.

    ### Ancestors (in MRO)

    * builtins.dict

`CustomersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`DiscountCodesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`DiscountCodesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesAnyValueFilter`
    :   The type of the None singleton.

`DiscountCodesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesSearchFilter`
    :   The type of the None singleton.

`DiscountCodesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesStringFilter`
    :   The type of the None singleton.

`DiscountCodesGetParams(*args, **kwargs)`
:   Parameters for discount_codes.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `discount_code_id: str`
    :   The type of the None singleton.

    `price_rule_id: str`
    :   The type of the None singleton.

`DiscountCodesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesSearchFilter`
    :   The type of the None singleton.

`DiscountCodesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesSearchFilter`
    :   The type of the None singleton.

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

`DiscountCodesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`DiscountCodesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesStringFilter`
    :   The type of the None singleton.

`DiscountCodesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesStringFilter`
    :   The type of the None singleton.

`DiscountCodesListParams(*args, **kwargs)`
:   Parameters for discount_codes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `price_rule_id: str`
    :   The type of the None singleton.

`DiscountCodesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesSearchFilter`
    :   The type of the None singleton.

`DiscountCodesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesSearchFilter`
    :   The type of the None singleton.

`DiscountCodesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesSearchFilter`
    :   The type of the None singleton.

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

`DiscountCodesSearchFilter(*args, **kwargs)`
:   Available fields for filtering discount_codes search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`DiscountCodesSearchQuery(*args, **kwargs)`
:   Search query for discount_codes entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.DiscountCodesEqCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesGtCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesGteCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLtCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLteCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesInCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesNotCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesAndCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesOrCondition | airbyte_agent_sdk.connectors.shopify.types.DiscountCodesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.DiscountCodesSortFilter]`
    :   The type of the None singleton.

`DiscountCodesSortFilter(*args, **kwargs)`
:   Available fields for sorting discount_codes search results.

    ### Ancestors (in MRO)

    * builtins.dict

`DiscountCodesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`DraftOrdersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`DraftOrdersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersAnyValueFilter`
    :   The type of the None singleton.

`DraftOrdersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersSearchFilter`
    :   The type of the None singleton.

`DraftOrdersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersStringFilter`
    :   The type of the None singleton.

`DraftOrdersGetParams(*args, **kwargs)`
:   Parameters for draft_orders.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `draft_order_id: str`
    :   The type of the None singleton.

`DraftOrdersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersSearchFilter`
    :   The type of the None singleton.

`DraftOrdersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersSearchFilter`
    :   The type of the None singleton.

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

`DraftOrdersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`DraftOrdersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersStringFilter`
    :   The type of the None singleton.

`DraftOrdersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersStringFilter`
    :   The type of the None singleton.

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

`DraftOrdersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersSearchFilter`
    :   The type of the None singleton.

`DraftOrdersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersSearchFilter`
    :   The type of the None singleton.

`DraftOrdersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersSearchFilter`
    :   The type of the None singleton.

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

`DraftOrdersSearchFilter(*args, **kwargs)`
:   Available fields for filtering draft_orders search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`DraftOrdersSearchQuery(*args, **kwargs)`
:   Search query for draft_orders entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.DraftOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.DraftOrdersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.DraftOrdersSortFilter]`
    :   The type of the None singleton.

`DraftOrdersSortFilter(*args, **kwargs)`
:   Available fields for sorting draft_orders search results.

    ### Ancestors (in MRO)

    * builtins.dict

`DraftOrdersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`FulfillmentOrdersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`FulfillmentOrdersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersAnyValueFilter`
    :   The type of the None singleton.

`FulfillmentOrdersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersSearchFilter`
    :   The type of the None singleton.

`FulfillmentOrdersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersStringFilter`
    :   The type of the None singleton.

`FulfillmentOrdersGetParams(*args, **kwargs)`
:   Parameters for fulfillment_orders.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fulfillment_order_id: str`
    :   The type of the None singleton.

`FulfillmentOrdersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersSearchFilter`
    :   The type of the None singleton.

`FulfillmentOrdersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersSearchFilter`
    :   The type of the None singleton.

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

`FulfillmentOrdersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`FulfillmentOrdersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersStringFilter`
    :   The type of the None singleton.

`FulfillmentOrdersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersStringFilter`
    :   The type of the None singleton.

`FulfillmentOrdersListParams(*args, **kwargs)`
:   Parameters for fulfillment_orders.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_id: str`
    :   The type of the None singleton.

`FulfillmentOrdersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersSearchFilter`
    :   The type of the None singleton.

`FulfillmentOrdersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersSearchFilter`
    :   The type of the None singleton.

`FulfillmentOrdersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersSearchFilter`
    :   The type of the None singleton.

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

`FulfillmentOrdersSearchFilter(*args, **kwargs)`
:   Available fields for filtering fulfillment_orders search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`FulfillmentOrdersSearchQuery(*args, **kwargs)`
:   Search query for fulfillment_orders entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.FulfillmentOrdersSortFilter]`
    :   The type of the None singleton.

`FulfillmentOrdersSortFilter(*args, **kwargs)`
:   Available fields for sorting fulfillment_orders search results.

    ### Ancestors (in MRO)

    * builtins.dict

`FulfillmentOrdersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`FulfillmentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`FulfillmentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsAnyValueFilter`
    :   The type of the None singleton.

`FulfillmentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsSearchFilter`
    :   The type of the None singleton.

`FulfillmentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsStringFilter`
    :   The type of the None singleton.

`FulfillmentsGetParams(*args, **kwargs)`
:   Parameters for fulfillments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fulfillment_id: str`
    :   The type of the None singleton.

    `order_id: str`
    :   The type of the None singleton.

`FulfillmentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsSearchFilter`
    :   The type of the None singleton.

`FulfillmentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsSearchFilter`
    :   The type of the None singleton.

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

`FulfillmentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`FulfillmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsStringFilter`
    :   The type of the None singleton.

`FulfillmentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsStringFilter`
    :   The type of the None singleton.

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

`FulfillmentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsSearchFilter`
    :   The type of the None singleton.

`FulfillmentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsSearchFilter`
    :   The type of the None singleton.

`FulfillmentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsSearchFilter`
    :   The type of the None singleton.

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

`FulfillmentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering fulfillments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`FulfillmentsSearchQuery(*args, **kwargs)`
:   Search query for fulfillments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.FulfillmentsEqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsGtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsGteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLtCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLteCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsInCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsNotCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsAndCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsOrCondition | airbyte_agent_sdk.connectors.shopify.types.FulfillmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.FulfillmentsSortFilter]`
    :   The type of the None singleton.

`FulfillmentsSortFilter(*args, **kwargs)`
:   Available fields for sorting fulfillments search results.

    ### Ancestors (in MRO)

    * builtins.dict

`FulfillmentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`InventoryItemsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`InventoryItemsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsAnyValueFilter`
    :   The type of the None singleton.

`InventoryItemsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsSearchFilter`
    :   The type of the None singleton.

`InventoryItemsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsStringFilter`
    :   The type of the None singleton.

`InventoryItemsGetParams(*args, **kwargs)`
:   Parameters for inventory_items.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `inventory_item_id: str`
    :   The type of the None singleton.

`InventoryItemsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsSearchFilter`
    :   The type of the None singleton.

`InventoryItemsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsSearchFilter`
    :   The type of the None singleton.

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

`InventoryItemsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`InventoryItemsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsStringFilter`
    :   The type of the None singleton.

`InventoryItemsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsStringFilter`
    :   The type of the None singleton.

`InventoryItemsListParams(*args, **kwargs)`
:   Parameters for inventory_items.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ids: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`InventoryItemsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsSearchFilter`
    :   The type of the None singleton.

`InventoryItemsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsSearchFilter`
    :   The type of the None singleton.

`InventoryItemsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsSearchFilter`
    :   The type of the None singleton.

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

`InventoryItemsSearchFilter(*args, **kwargs)`
:   Available fields for filtering inventory_items search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`InventoryItemsSearchQuery(*args, **kwargs)`
:   Search query for inventory_items entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.InventoryItemsEqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsGtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsGteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsInCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsNotCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsAndCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsOrCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryItemsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.InventoryItemsSortFilter]`
    :   The type of the None singleton.

`InventoryItemsSortFilter(*args, **kwargs)`
:   Available fields for sorting inventory_items search results.

    ### Ancestors (in MRO)

    * builtins.dict

`InventoryItemsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`InventoryLevelsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`InventoryLevelsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsAnyValueFilter`
    :   The type of the None singleton.

`InventoryLevelsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsSearchFilter`
    :   The type of the None singleton.

`InventoryLevelsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsStringFilter`
    :   The type of the None singleton.

`InventoryLevelsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsSearchFilter`
    :   The type of the None singleton.

`InventoryLevelsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsSearchFilter`
    :   The type of the None singleton.

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

`InventoryLevelsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`InventoryLevelsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsStringFilter`
    :   The type of the None singleton.

`InventoryLevelsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsStringFilter`
    :   The type of the None singleton.

`InventoryLevelsListParams(*args, **kwargs)`
:   Parameters for inventory_levels.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `location_id: str`
    :   The type of the None singleton.

`InventoryLevelsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsSearchFilter`
    :   The type of the None singleton.

`InventoryLevelsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsSearchFilter`
    :   The type of the None singleton.

`InventoryLevelsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsSearchFilter`
    :   The type of the None singleton.

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

`InventoryLevelsSearchFilter(*args, **kwargs)`
:   Available fields for filtering inventory_levels search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`InventoryLevelsSearchQuery(*args, **kwargs)`
:   Search query for inventory_levels entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsEqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsGtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsGteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLtCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLteCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsInCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsNotCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsAndCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsOrCondition | airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.InventoryLevelsSortFilter]`
    :   The type of the None singleton.

`InventoryLevelsSortFilter(*args, **kwargs)`
:   Available fields for sorting inventory_levels search results.

    ### Ancestors (in MRO)

    * builtins.dict

`InventoryLevelsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`LocationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`LocationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.LocationsAnyValueFilter`
    :   The type of the None singleton.

`LocationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.LocationsSearchFilter`
    :   The type of the None singleton.

`LocationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.LocationsStringFilter`
    :   The type of the None singleton.

`LocationsGetParams(*args, **kwargs)`
:   Parameters for locations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `location_id: str`
    :   The type of the None singleton.

`LocationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.LocationsSearchFilter`
    :   The type of the None singleton.

`LocationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.LocationsSearchFilter`
    :   The type of the None singleton.

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

`LocationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`LocationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.LocationsStringFilter`
    :   The type of the None singleton.

`LocationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.LocationsStringFilter`
    :   The type of the None singleton.

`LocationsListParams(*args, **kwargs)`
:   Parameters for locations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`LocationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.LocationsSearchFilter`
    :   The type of the None singleton.

`LocationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.LocationsSearchFilter`
    :   The type of the None singleton.

`LocationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.LocationsSearchFilter`
    :   The type of the None singleton.

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

`LocationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering locations search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`LocationsSearchQuery(*args, **kwargs)`
:   Search query for locations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.LocationsEqCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsGtCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsGteCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLtCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLteCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsInCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsNotCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsAndCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsOrCondition | airbyte_agent_sdk.connectors.shopify.types.LocationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.LocationsSortFilter]`
    :   The type of the None singleton.

`LocationsSortFilter(*args, **kwargs)`
:   Available fields for sorting locations search results.

    ### Ancestors (in MRO)

    * builtins.dict

`LocationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`MetafieldCustomersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldCustomersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersAnyValueFilter`
    :   The type of the None singleton.

`MetafieldCustomersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersSearchFilter`
    :   The type of the None singleton.

`MetafieldCustomersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersStringFilter`
    :   The type of the None singleton.

`MetafieldCustomersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersSearchFilter`
    :   The type of the None singleton.

`MetafieldCustomersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersSearchFilter`
    :   The type of the None singleton.

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

`MetafieldCustomersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldCustomersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersStringFilter`
    :   The type of the None singleton.

`MetafieldCustomersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersStringFilter`
    :   The type of the None singleton.

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

`MetafieldCustomersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersSearchFilter`
    :   The type of the None singleton.

`MetafieldCustomersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersSearchFilter`
    :   The type of the None singleton.

`MetafieldCustomersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersSearchFilter`
    :   The type of the None singleton.

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

`MetafieldCustomersSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_customers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldCustomersSearchQuery(*args, **kwargs)`
:   Search query for metafield_customers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldCustomersSortFilter]`
    :   The type of the None singleton.

`MetafieldCustomersSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_customers search results.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldCustomersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`MetafieldDraftOrdersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldDraftOrdersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersAnyValueFilter`
    :   The type of the None singleton.

`MetafieldDraftOrdersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersSearchFilter`
    :   The type of the None singleton.

`MetafieldDraftOrdersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersStringFilter`
    :   The type of the None singleton.

`MetafieldDraftOrdersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersSearchFilter`
    :   The type of the None singleton.

`MetafieldDraftOrdersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersSearchFilter`
    :   The type of the None singleton.

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

`MetafieldDraftOrdersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldDraftOrdersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersStringFilter`
    :   The type of the None singleton.

`MetafieldDraftOrdersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersStringFilter`
    :   The type of the None singleton.

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

`MetafieldDraftOrdersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersSearchFilter`
    :   The type of the None singleton.

`MetafieldDraftOrdersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersSearchFilter`
    :   The type of the None singleton.

`MetafieldDraftOrdersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersSearchFilter`
    :   The type of the None singleton.

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

`MetafieldDraftOrdersSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_draft_orders search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldDraftOrdersSearchQuery(*args, **kwargs)`
:   Search query for metafield_draft_orders entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldDraftOrdersSortFilter]`
    :   The type of the None singleton.

`MetafieldDraftOrdersSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_draft_orders search results.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldDraftOrdersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`MetafieldLocationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldLocationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsAnyValueFilter`
    :   The type of the None singleton.

`MetafieldLocationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsSearchFilter`
    :   The type of the None singleton.

`MetafieldLocationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsStringFilter`
    :   The type of the None singleton.

`MetafieldLocationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsSearchFilter`
    :   The type of the None singleton.

`MetafieldLocationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsSearchFilter`
    :   The type of the None singleton.

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

`MetafieldLocationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldLocationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsStringFilter`
    :   The type of the None singleton.

`MetafieldLocationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsStringFilter`
    :   The type of the None singleton.

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

`MetafieldLocationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsSearchFilter`
    :   The type of the None singleton.

`MetafieldLocationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsSearchFilter`
    :   The type of the None singleton.

`MetafieldLocationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsSearchFilter`
    :   The type of the None singleton.

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

`MetafieldLocationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_locations search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldLocationsSearchQuery(*args, **kwargs)`
:   Search query for metafield_locations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldLocationsSortFilter]`
    :   The type of the None singleton.

`MetafieldLocationsSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_locations search results.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldLocationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`MetafieldOrdersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldOrdersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersAnyValueFilter`
    :   The type of the None singleton.

`MetafieldOrdersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersSearchFilter`
    :   The type of the None singleton.

`MetafieldOrdersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersStringFilter`
    :   The type of the None singleton.

`MetafieldOrdersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersSearchFilter`
    :   The type of the None singleton.

`MetafieldOrdersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersSearchFilter`
    :   The type of the None singleton.

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

`MetafieldOrdersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldOrdersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersStringFilter`
    :   The type of the None singleton.

`MetafieldOrdersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersStringFilter`
    :   The type of the None singleton.

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

`MetafieldOrdersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersSearchFilter`
    :   The type of the None singleton.

`MetafieldOrdersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersSearchFilter`
    :   The type of the None singleton.

`MetafieldOrdersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersSearchFilter`
    :   The type of the None singleton.

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

`MetafieldOrdersSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_orders search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldOrdersSearchQuery(*args, **kwargs)`
:   Search query for metafield_orders entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldOrdersSortFilter]`
    :   The type of the None singleton.

`MetafieldOrdersSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_orders search results.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldOrdersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`MetafieldProductImagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldProductImagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesAnyValueFilter`
    :   The type of the None singleton.

`MetafieldProductImagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesSearchFilter`
    :   The type of the None singleton.

`MetafieldProductImagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesStringFilter`
    :   The type of the None singleton.

`MetafieldProductImagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesSearchFilter`
    :   The type of the None singleton.

`MetafieldProductImagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesSearchFilter`
    :   The type of the None singleton.

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

`MetafieldProductImagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldProductImagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesStringFilter`
    :   The type of the None singleton.

`MetafieldProductImagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesStringFilter`
    :   The type of the None singleton.

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

`MetafieldProductImagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesSearchFilter`
    :   The type of the None singleton.

`MetafieldProductImagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesSearchFilter`
    :   The type of the None singleton.

`MetafieldProductImagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesSearchFilter`
    :   The type of the None singleton.

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

`MetafieldProductImagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_product_images search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldProductImagesSearchQuery(*args, **kwargs)`
:   Search query for metafield_product_images entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldProductImagesSortFilter]`
    :   The type of the None singleton.

`MetafieldProductImagesSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_product_images search results.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldProductImagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`MetafieldProductVariantsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldProductVariantsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsAnyValueFilter`
    :   The type of the None singleton.

`MetafieldProductVariantsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsSearchFilter`
    :   The type of the None singleton.

`MetafieldProductVariantsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsStringFilter`
    :   The type of the None singleton.

`MetafieldProductVariantsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsSearchFilter`
    :   The type of the None singleton.

`MetafieldProductVariantsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsSearchFilter`
    :   The type of the None singleton.

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

`MetafieldProductVariantsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldProductVariantsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsStringFilter`
    :   The type of the None singleton.

`MetafieldProductVariantsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsStringFilter`
    :   The type of the None singleton.

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

`MetafieldProductVariantsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsSearchFilter`
    :   The type of the None singleton.

`MetafieldProductVariantsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsSearchFilter`
    :   The type of the None singleton.

`MetafieldProductVariantsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsSearchFilter`
    :   The type of the None singleton.

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

`MetafieldProductVariantsSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_product_variants search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldProductVariantsSearchQuery(*args, **kwargs)`
:   Search query for metafield_product_variants entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldProductVariantsSortFilter]`
    :   The type of the None singleton.

`MetafieldProductVariantsSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_product_variants search results.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldProductVariantsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`MetafieldProductsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldProductsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsAnyValueFilter`
    :   The type of the None singleton.

`MetafieldProductsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsSearchFilter`
    :   The type of the None singleton.

`MetafieldProductsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsStringFilter`
    :   The type of the None singleton.

`MetafieldProductsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsSearchFilter`
    :   The type of the None singleton.

`MetafieldProductsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsSearchFilter`
    :   The type of the None singleton.

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

`MetafieldProductsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldProductsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsStringFilter`
    :   The type of the None singleton.

`MetafieldProductsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsStringFilter`
    :   The type of the None singleton.

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

`MetafieldProductsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsSearchFilter`
    :   The type of the None singleton.

`MetafieldProductsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsSearchFilter`
    :   The type of the None singleton.

`MetafieldProductsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsSearchFilter`
    :   The type of the None singleton.

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

`MetafieldProductsSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_products search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldProductsSearchQuery(*args, **kwargs)`
:   Search query for metafield_products entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldProductsSortFilter]`
    :   The type of the None singleton.

`MetafieldProductsSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_products search results.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldProductsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`MetafieldShopsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldShopsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsAnyValueFilter`
    :   The type of the None singleton.

`MetafieldShopsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsSearchFilter`
    :   The type of the None singleton.

`MetafieldShopsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsStringFilter`
    :   The type of the None singleton.

`MetafieldShopsGetParams(*args, **kwargs)`
:   Parameters for metafield_shops.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `metafield_id: str`
    :   The type of the None singleton.

`MetafieldShopsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsSearchFilter`
    :   The type of the None singleton.

`MetafieldShopsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsSearchFilter`
    :   The type of the None singleton.

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

`MetafieldShopsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldShopsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsStringFilter`
    :   The type of the None singleton.

`MetafieldShopsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsStringFilter`
    :   The type of the None singleton.

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

`MetafieldShopsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsSearchFilter`
    :   The type of the None singleton.

`MetafieldShopsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsSearchFilter`
    :   The type of the None singleton.

`MetafieldShopsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsSearchFilter`
    :   The type of the None singleton.

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

`MetafieldShopsSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_shops search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldShopsSearchQuery(*args, **kwargs)`
:   Search query for metafield_shops entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldShopsSortFilter]`
    :   The type of the None singleton.

`MetafieldShopsSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_shops search results.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldShopsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`MetafieldSmartCollectionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldSmartCollectionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsAnyValueFilter`
    :   The type of the None singleton.

`MetafieldSmartCollectionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsSearchFilter`
    :   The type of the None singleton.

`MetafieldSmartCollectionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsStringFilter`
    :   The type of the None singleton.

`MetafieldSmartCollectionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsSearchFilter`
    :   The type of the None singleton.

`MetafieldSmartCollectionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsSearchFilter`
    :   The type of the None singleton.

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

`MetafieldSmartCollectionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldSmartCollectionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsStringFilter`
    :   The type of the None singleton.

`MetafieldSmartCollectionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsStringFilter`
    :   The type of the None singleton.

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

`MetafieldSmartCollectionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsSearchFilter`
    :   The type of the None singleton.

`MetafieldSmartCollectionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsSearchFilter`
    :   The type of the None singleton.

`MetafieldSmartCollectionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsSearchFilter`
    :   The type of the None singleton.

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

`MetafieldSmartCollectionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering metafield_smart_collections search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldSmartCollectionsSearchQuery(*args, **kwargs)`
:   Search query for metafield_smart_collections entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.MetafieldSmartCollectionsSortFilter]`
    :   The type of the None singleton.

`MetafieldSmartCollectionsSortFilter(*args, **kwargs)`
:   Available fields for sorting metafield_smart_collections search results.

    ### Ancestors (in MRO)

    * builtins.dict

`MetafieldSmartCollectionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`OrderRefundsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`OrderRefundsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsAnyValueFilter`
    :   The type of the None singleton.

`OrderRefundsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsSearchFilter`
    :   The type of the None singleton.

`OrderRefundsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsStringFilter`
    :   The type of the None singleton.

`OrderRefundsGetParams(*args, **kwargs)`
:   Parameters for order_refunds.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_id: str`
    :   The type of the None singleton.

    `refund_id: str`
    :   The type of the None singleton.

`OrderRefundsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsSearchFilter`
    :   The type of the None singleton.

`OrderRefundsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsSearchFilter`
    :   The type of the None singleton.

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

`OrderRefundsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`OrderRefundsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsStringFilter`
    :   The type of the None singleton.

`OrderRefundsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsStringFilter`
    :   The type of the None singleton.

`OrderRefundsListParams(*args, **kwargs)`
:   Parameters for order_refunds.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `order_id: str`
    :   The type of the None singleton.

`OrderRefundsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsSearchFilter`
    :   The type of the None singleton.

`OrderRefundsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsSearchFilter`
    :   The type of the None singleton.

`OrderRefundsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsSearchFilter`
    :   The type of the None singleton.

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

`OrderRefundsSearchFilter(*args, **kwargs)`
:   Available fields for filtering order_refunds search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`OrderRefundsSearchQuery(*args, **kwargs)`
:   Search query for order_refunds entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.OrderRefundsEqCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsGtCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsGteCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLtCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLteCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsInCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsNotCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsAndCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsOrCondition | airbyte_agent_sdk.connectors.shopify.types.OrderRefundsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.OrderRefundsSortFilter]`
    :   The type of the None singleton.

`OrderRefundsSortFilter(*args, **kwargs)`
:   Available fields for sorting order_refunds search results.

    ### Ancestors (in MRO)

    * builtins.dict

`OrderRefundsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

`OrdersGetParams(*args, **kwargs)`
:   Parameters for orders.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_id: str`
    :   The type of the None singleton.

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

`PriceRulesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`PriceRulesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.PriceRulesAnyValueFilter`
    :   The type of the None singleton.

`PriceRulesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.PriceRulesSearchFilter`
    :   The type of the None singleton.

`PriceRulesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.PriceRulesStringFilter`
    :   The type of the None singleton.

`PriceRulesGetParams(*args, **kwargs)`
:   Parameters for price_rules.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `price_rule_id: str`
    :   The type of the None singleton.

`PriceRulesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.PriceRulesSearchFilter`
    :   The type of the None singleton.

`PriceRulesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.PriceRulesSearchFilter`
    :   The type of the None singleton.

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

`PriceRulesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`PriceRulesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.PriceRulesStringFilter`
    :   The type of the None singleton.

`PriceRulesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.PriceRulesStringFilter`
    :   The type of the None singleton.

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

`PriceRulesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.PriceRulesSearchFilter`
    :   The type of the None singleton.

`PriceRulesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.PriceRulesSearchFilter`
    :   The type of the None singleton.

`PriceRulesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.PriceRulesSearchFilter`
    :   The type of the None singleton.

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

`PriceRulesSearchFilter(*args, **kwargs)`
:   Available fields for filtering price_rules search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`PriceRulesSearchQuery(*args, **kwargs)`
:   Search query for price_rules entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.PriceRulesEqCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesGtCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesGteCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLtCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLteCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesInCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesNotCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesAndCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesOrCondition | airbyte_agent_sdk.connectors.shopify.types.PriceRulesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.PriceRulesSortFilter]`
    :   The type of the None singleton.

`PriceRulesSortFilter(*args, **kwargs)`
:   Available fields for sorting price_rules search results.

    ### Ancestors (in MRO)

    * builtins.dict

`PriceRulesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`ProductImagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`ProductImagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.ProductImagesAnyValueFilter`
    :   The type of the None singleton.

`ProductImagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.ProductImagesSearchFilter`
    :   The type of the None singleton.

`ProductImagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.ProductImagesStringFilter`
    :   The type of the None singleton.

`ProductImagesGetParams(*args, **kwargs)`
:   Parameters for product_images.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `image_id: str`
    :   The type of the None singleton.

    `product_id: str`
    :   The type of the None singleton.

`ProductImagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.ProductImagesSearchFilter`
    :   The type of the None singleton.

`ProductImagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.ProductImagesSearchFilter`
    :   The type of the None singleton.

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

`ProductImagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`ProductImagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.ProductImagesStringFilter`
    :   The type of the None singleton.

`ProductImagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.ProductImagesStringFilter`
    :   The type of the None singleton.

`ProductImagesListParams(*args, **kwargs)`
:   Parameters for product_images.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `product_id: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

`ProductImagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.ProductImagesSearchFilter`
    :   The type of the None singleton.

`ProductImagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.ProductImagesSearchFilter`
    :   The type of the None singleton.

`ProductImagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.ProductImagesSearchFilter`
    :   The type of the None singleton.

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

`ProductImagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering product_images search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`ProductImagesSearchQuery(*args, **kwargs)`
:   Search query for product_images entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.ProductImagesEqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesGtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesGteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesInCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesNotCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesAndCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesOrCondition | airbyte_agent_sdk.connectors.shopify.types.ProductImagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.ProductImagesSortFilter]`
    :   The type of the None singleton.

`ProductImagesSortFilter(*args, **kwargs)`
:   Available fields for sorting product_images search results.

    ### Ancestors (in MRO)

    * builtins.dict

`ProductImagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`ProductVariantsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`ProductVariantsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsAnyValueFilter`
    :   The type of the None singleton.

`ProductVariantsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsSearchFilter`
    :   The type of the None singleton.

`ProductVariantsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsStringFilter`
    :   The type of the None singleton.

`ProductVariantsGetParams(*args, **kwargs)`
:   Parameters for product_variants.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `variant_id: str`
    :   The type of the None singleton.

`ProductVariantsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsSearchFilter`
    :   The type of the None singleton.

`ProductVariantsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsSearchFilter`
    :   The type of the None singleton.

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

`ProductVariantsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`ProductVariantsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsStringFilter`
    :   The type of the None singleton.

`ProductVariantsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsStringFilter`
    :   The type of the None singleton.

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

`ProductVariantsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsSearchFilter`
    :   The type of the None singleton.

`ProductVariantsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsSearchFilter`
    :   The type of the None singleton.

`ProductVariantsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsSearchFilter`
    :   The type of the None singleton.

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

`ProductVariantsSearchFilter(*args, **kwargs)`
:   Available fields for filtering product_variants search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`ProductVariantsSearchQuery(*args, **kwargs)`
:   Search query for product_variants entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.ProductVariantsEqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsGtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsGteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLtCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLteCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsInCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsNotCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsAndCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsOrCondition | airbyte_agent_sdk.connectors.shopify.types.ProductVariantsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.ProductVariantsSortFilter]`
    :   The type of the None singleton.

`ProductVariantsSortFilter(*args, **kwargs)`
:   Available fields for sorting product_variants search results.

    ### Ancestors (in MRO)

    * builtins.dict

`ProductVariantsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

`ProductsGetParams(*args, **kwargs)`
:   Parameters for products.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `product_id: str`
    :   The type of the None singleton.

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

`ShopAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`ShopContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.ShopAnyValueFilter`
    :   The type of the None singleton.

`ShopEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.ShopSearchFilter`
    :   The type of the None singleton.

`ShopFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.ShopStringFilter`
    :   The type of the None singleton.

`ShopGetParams(*args, **kwargs)`
:   Parameters for shop.get operation

    ### Ancestors (in MRO)

    * builtins.dict

`ShopGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.ShopSearchFilter`
    :   The type of the None singleton.

`ShopGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.ShopSearchFilter`
    :   The type of the None singleton.

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

`ShopInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`ShopKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.ShopStringFilter`
    :   The type of the None singleton.

`ShopLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.ShopStringFilter`
    :   The type of the None singleton.

`ShopLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.ShopSearchFilter`
    :   The type of the None singleton.

`ShopLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.ShopSearchFilter`
    :   The type of the None singleton.

`ShopNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.ShopSearchFilter`
    :   The type of the None singleton.

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

`ShopSearchFilter(*args, **kwargs)`
:   Available fields for filtering shop search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`ShopSearchQuery(*args, **kwargs)`
:   Search query for shop entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.ShopEqCondition | airbyte_agent_sdk.connectors.shopify.types.ShopNeqCondition | airbyte_agent_sdk.connectors.shopify.types.ShopGtCondition | airbyte_agent_sdk.connectors.shopify.types.ShopGteCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLtCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLteCondition | airbyte_agent_sdk.connectors.shopify.types.ShopInCondition | airbyte_agent_sdk.connectors.shopify.types.ShopLikeCondition | airbyte_agent_sdk.connectors.shopify.types.ShopFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.ShopKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.ShopContainsCondition | airbyte_agent_sdk.connectors.shopify.types.ShopNotCondition | airbyte_agent_sdk.connectors.shopify.types.ShopAndCondition | airbyte_agent_sdk.connectors.shopify.types.ShopOrCondition | airbyte_agent_sdk.connectors.shopify.types.ShopAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.ShopSortFilter]`
    :   The type of the None singleton.

`ShopSortFilter(*args, **kwargs)`
:   Available fields for sorting shop search results.

    ### Ancestors (in MRO)

    * builtins.dict

`ShopStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`SmartCollectionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`SmartCollectionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsAnyValueFilter`
    :   The type of the None singleton.

`SmartCollectionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsSearchFilter`
    :   The type of the None singleton.

`SmartCollectionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsStringFilter`
    :   The type of the None singleton.

`SmartCollectionsGetParams(*args, **kwargs)`
:   Parameters for smart_collections.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_id: str`
    :   The type of the None singleton.

`SmartCollectionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsSearchFilter`
    :   The type of the None singleton.

`SmartCollectionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsSearchFilter`
    :   The type of the None singleton.

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

`SmartCollectionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`SmartCollectionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsStringFilter`
    :   The type of the None singleton.

`SmartCollectionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsStringFilter`
    :   The type of the None singleton.

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

`SmartCollectionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsSearchFilter`
    :   The type of the None singleton.

`SmartCollectionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsSearchFilter`
    :   The type of the None singleton.

`SmartCollectionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsSearchFilter`
    :   The type of the None singleton.

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

`SmartCollectionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering smart_collections search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`SmartCollectionsSearchQuery(*args, **kwargs)`
:   Search query for smart_collections entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsInCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.SmartCollectionsSortFilter]`
    :   The type of the None singleton.

`SmartCollectionsSortFilter(*args, **kwargs)`
:   Available fields for sorting smart_collections search results.

    ### Ancestors (in MRO)

    * builtins.dict

`SmartCollectionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`TenderTransactionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`TenderTransactionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsAnyValueFilter`
    :   The type of the None singleton.

`TenderTransactionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsSearchFilter`
    :   The type of the None singleton.

`TenderTransactionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsStringFilter`
    :   The type of the None singleton.

`TenderTransactionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsSearchFilter`
    :   The type of the None singleton.

`TenderTransactionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsSearchFilter`
    :   The type of the None singleton.

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

`TenderTransactionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`TenderTransactionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsStringFilter`
    :   The type of the None singleton.

`TenderTransactionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsStringFilter`
    :   The type of the None singleton.

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

`TenderTransactionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsSearchFilter`
    :   The type of the None singleton.

`TenderTransactionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsSearchFilter`
    :   The type of the None singleton.

`TenderTransactionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsSearchFilter`
    :   The type of the None singleton.

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

`TenderTransactionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering tender_transactions search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`TenderTransactionsSearchQuery(*args, **kwargs)`
:   Search query for tender_transactions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsEqCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsNeqCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsGtCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsGteCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLtCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLteCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsInCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsLikeCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsFuzzyCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsKeywordCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsContainsCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsNotCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsAndCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsOrCondition | airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.shopify.types.TenderTransactionsSortFilter]`
    :   The type of the None singleton.

`TenderTransactionsSortFilter(*args, **kwargs)`
:   Available fields for sorting tender_transactions search results.

    ### Ancestors (in MRO)

    * builtins.dict

`TenderTransactionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

`TransactionsGetParams(*args, **kwargs)`
:   Parameters for transactions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_id: str`
    :   The type of the None singleton.

    `transaction_id: str`
    :   The type of the None singleton.

`TransactionsListParams(*args, **kwargs)`
:   Parameters for transactions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_id: str`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.