---
id: airbyte_agent_sdk-connectors-klaviyo-types
title: airbyte_agent_sdk.connectors.klaviyo.types
---

Module airbyte_agent_sdk.connectors.klaviyo.types
=================================================
Type definitions for klaviyo connector.

Classes
-------

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

`CampaignsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.klaviyo.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

`CampaignsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

`CampaignsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Any`
    :   The type of the None singleton.

    `id: Any`
    :   The type of the None singleton.

    `links: Any`
    :   The type of the None singleton.

    `relationships: Any`
    :   The type of the None singleton.

    `type_: Any`
    :   The type of the None singleton.

    `updated_at: Any`
    :   The type of the None singleton.

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsGetParams(*args, **kwargs)`
:   Parameters for campaigns.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsInFilter`
    :   The type of the None singleton.

`CampaignsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `links: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `relationships: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `type_: list[str]`
    :   The type of the None singleton.

    `updated_at: list[str]`
    :   The type of the None singleton.

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsListParams(*args, **kwargs)`
:   Parameters for campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: str`
    :   The type of the None singleton.

    `page_cursor: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsAnyCondition`
    :   The type of the None singleton.

`CampaignsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.klaviyo.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

`CampaignsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaigns search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.klaviyo.types.CampaignsSortFilter]`
    :   The type of the None singleton.

`CampaignsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaigns search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `links: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `relationships: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `type_: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `updated_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

`CampaignsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `links: str`
    :   The type of the None singleton.

    `relationships: str`
    :   The type of the None singleton.

    `type_: str`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.

`EmailTemplatesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesInCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesAnyCondition]`
    :   The type of the None singleton.

`EmailTemplatesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesAnyValueFilter`
    :   The type of the None singleton.

`EmailTemplatesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Any`
    :   The type of the None singleton.

    `id: Any`
    :   The type of the None singleton.

    `links: Any`
    :   The type of the None singleton.

    `type_: Any`
    :   The type of the None singleton.

    `updated: Any`
    :   The type of the None singleton.

`EmailTemplatesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesAnyValueFilter`
    :   The type of the None singleton.

`EmailTemplatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesSearchFilter`
    :   The type of the None singleton.

`EmailTemplatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesStringFilter`
    :   The type of the None singleton.

`EmailTemplatesGetParams(*args, **kwargs)`
:   Parameters for email_templates.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`EmailTemplatesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesSearchFilter`
    :   The type of the None singleton.

`EmailTemplatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesSearchFilter`
    :   The type of the None singleton.

`EmailTemplatesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesInFilter`
    :   The type of the None singleton.

`EmailTemplatesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `links: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `type_: list[str]`
    :   The type of the None singleton.

    `updated: list[str]`
    :   The type of the None singleton.

`EmailTemplatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesStringFilter`
    :   The type of the None singleton.

`EmailTemplatesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesStringFilter`
    :   The type of the None singleton.

`EmailTemplatesListParams(*args, **kwargs)`
:   Parameters for email_templates.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_cursor: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`EmailTemplatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesSearchFilter`
    :   The type of the None singleton.

`EmailTemplatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesSearchFilter`
    :   The type of the None singleton.

`EmailTemplatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesSearchFilter`
    :   The type of the None singleton.

`EmailTemplatesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesInCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesAnyCondition`
    :   The type of the None singleton.

`EmailTemplatesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesInCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesAnyCondition]`
    :   The type of the None singleton.

`EmailTemplatesSearchFilter(*args, **kwargs)`
:   Available fields for filtering email_templates search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated: str | None`
    :   The type of the None singleton.

`EmailTemplatesSearchQuery(*args, **kwargs)`
:   Search query for email_templates entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesInCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesSortFilter]`
    :   The type of the None singleton.

`EmailTemplatesSortFilter(*args, **kwargs)`
:   Available fields for sorting email_templates search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `links: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `type_: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `updated: Literal['asc', 'desc']`
    :   The type of the None singleton.

`EmailTemplatesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `links: str`
    :   The type of the None singleton.

    `type_: str`
    :   The type of the None singleton.

    `updated: str`
    :   The type of the None singleton.

`EventsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.klaviyo.types.EventsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsAnyCondition]`
    :   The type of the None singleton.

`EventsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.klaviyo.types.EventsAnyValueFilter`
    :   The type of the None singleton.

`EventsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Any`
    :   The type of the None singleton.

    `datetime: Any`
    :   The type of the None singleton.

    `id: Any`
    :   The type of the None singleton.

    `links: Any`
    :   The type of the None singleton.

    `relationships: Any`
    :   The type of the None singleton.

    `type_: Any`
    :   The type of the None singleton.

`EventsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.klaviyo.types.EventsAnyValueFilter`
    :   The type of the None singleton.

`EventsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.klaviyo.types.EventsSearchFilter`
    :   The type of the None singleton.

`EventsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.klaviyo.types.EventsStringFilter`
    :   The type of the None singleton.

`EventsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.klaviyo.types.EventsSearchFilter`
    :   The type of the None singleton.

`EventsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.klaviyo.types.EventsSearchFilter`
    :   The type of the None singleton.

`EventsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.klaviyo.types.EventsInFilter`
    :   The type of the None singleton.

`EventsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `datetime: list[str]`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `links: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `relationships: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `type_: list[str]`
    :   The type of the None singleton.

`EventsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.klaviyo.types.EventsStringFilter`
    :   The type of the None singleton.

`EventsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.klaviyo.types.EventsStringFilter`
    :   The type of the None singleton.

`EventsListParams(*args, **kwargs)`
:   Parameters for events.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_cursor: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

`EventsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.klaviyo.types.EventsSearchFilter`
    :   The type of the None singleton.

`EventsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.klaviyo.types.EventsSearchFilter`
    :   The type of the None singleton.

`EventsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.klaviyo.types.EventsSearchFilter`
    :   The type of the None singleton.

`EventsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.klaviyo.types.EventsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsAnyCondition`
    :   The type of the None singleton.

`EventsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.klaviyo.types.EventsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsAnyCondition]`
    :   The type of the None singleton.

`EventsSearchFilter(*args, **kwargs)`
:   Available fields for filtering events search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `datetime: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

`EventsSearchQuery(*args, **kwargs)`
:   Search query for events entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.klaviyo.types.EventsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.klaviyo.types.EventsSortFilter]`
    :   The type of the None singleton.

`EventsSortFilter(*args, **kwargs)`
:   Available fields for sorting events search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `datetime: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `links: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `relationships: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `type_: Literal['asc', 'desc']`
    :   The type of the None singleton.

`EventsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: str`
    :   The type of the None singleton.

    `datetime: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `links: str`
    :   The type of the None singleton.

    `relationships: str`
    :   The type of the None singleton.

    `type_: str`
    :   The type of the None singleton.

`FlowsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.klaviyo.types.FlowsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsAnyCondition]`
    :   The type of the None singleton.

`FlowsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.klaviyo.types.FlowsAnyValueFilter`
    :   The type of the None singleton.

`FlowsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Any`
    :   The type of the None singleton.

    `id: Any`
    :   The type of the None singleton.

    `links: Any`
    :   The type of the None singleton.

    `relationships: Any`
    :   The type of the None singleton.

    `type_: Any`
    :   The type of the None singleton.

    `updated: Any`
    :   The type of the None singleton.

`FlowsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.klaviyo.types.FlowsAnyValueFilter`
    :   The type of the None singleton.

`FlowsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.klaviyo.types.FlowsSearchFilter`
    :   The type of the None singleton.

`FlowsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.klaviyo.types.FlowsStringFilter`
    :   The type of the None singleton.

`FlowsGetParams(*args, **kwargs)`
:   Parameters for flows.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`FlowsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.klaviyo.types.FlowsSearchFilter`
    :   The type of the None singleton.

`FlowsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.klaviyo.types.FlowsSearchFilter`
    :   The type of the None singleton.

`FlowsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.klaviyo.types.FlowsInFilter`
    :   The type of the None singleton.

`FlowsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `links: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `relationships: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `type_: list[str]`
    :   The type of the None singleton.

    `updated: list[str]`
    :   The type of the None singleton.

`FlowsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.klaviyo.types.FlowsStringFilter`
    :   The type of the None singleton.

`FlowsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.klaviyo.types.FlowsStringFilter`
    :   The type of the None singleton.

`FlowsListParams(*args, **kwargs)`
:   Parameters for flows.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_cursor: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`FlowsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.klaviyo.types.FlowsSearchFilter`
    :   The type of the None singleton.

`FlowsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.klaviyo.types.FlowsSearchFilter`
    :   The type of the None singleton.

`FlowsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.klaviyo.types.FlowsSearchFilter`
    :   The type of the None singleton.

`FlowsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.klaviyo.types.FlowsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsAnyCondition`
    :   The type of the None singleton.

`FlowsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.klaviyo.types.FlowsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsAnyCondition]`
    :   The type of the None singleton.

`FlowsSearchFilter(*args, **kwargs)`
:   Available fields for filtering flows search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated: str | None`
    :   The type of the None singleton.

`FlowsSearchQuery(*args, **kwargs)`
:   Search query for flows entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.klaviyo.types.FlowsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.klaviyo.types.FlowsSortFilter]`
    :   The type of the None singleton.

`FlowsSortFilter(*args, **kwargs)`
:   Available fields for sorting flows search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `links: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `relationships: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `type_: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `updated: Literal['asc', 'desc']`
    :   The type of the None singleton.

`FlowsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `links: str`
    :   The type of the None singleton.

    `relationships: str`
    :   The type of the None singleton.

    `type_: str`
    :   The type of the None singleton.

    `updated: str`
    :   The type of the None singleton.

`ListsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.klaviyo.types.ListsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsAnyCondition]`
    :   The type of the None singleton.

`ListsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.klaviyo.types.ListsAnyValueFilter`
    :   The type of the None singleton.

`ListsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Any`
    :   The type of the None singleton.

    `id: Any`
    :   The type of the None singleton.

    `links: Any`
    :   The type of the None singleton.

    `relationships: Any`
    :   The type of the None singleton.

    `type_: Any`
    :   The type of the None singleton.

    `updated: Any`
    :   The type of the None singleton.

`ListsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.klaviyo.types.ListsAnyValueFilter`
    :   The type of the None singleton.

`ListsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.klaviyo.types.ListsSearchFilter`
    :   The type of the None singleton.

`ListsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.klaviyo.types.ListsStringFilter`
    :   The type of the None singleton.

`ListsGetParams(*args, **kwargs)`
:   Parameters for lists.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`ListsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.klaviyo.types.ListsSearchFilter`
    :   The type of the None singleton.

`ListsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.klaviyo.types.ListsSearchFilter`
    :   The type of the None singleton.

`ListsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.klaviyo.types.ListsInFilter`
    :   The type of the None singleton.

`ListsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `links: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `relationships: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `type_: list[str]`
    :   The type of the None singleton.

    `updated: list[str]`
    :   The type of the None singleton.

`ListsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.klaviyo.types.ListsStringFilter`
    :   The type of the None singleton.

`ListsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.klaviyo.types.ListsStringFilter`
    :   The type of the None singleton.

`ListsListParams(*args, **kwargs)`
:   Parameters for lists.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_cursor: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`ListsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.klaviyo.types.ListsSearchFilter`
    :   The type of the None singleton.

`ListsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.klaviyo.types.ListsSearchFilter`
    :   The type of the None singleton.

`ListsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.klaviyo.types.ListsSearchFilter`
    :   The type of the None singleton.

`ListsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.klaviyo.types.ListsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsAnyCondition`
    :   The type of the None singleton.

`ListsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.klaviyo.types.ListsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsAnyCondition]`
    :   The type of the None singleton.

`ListsSearchFilter(*args, **kwargs)`
:   Available fields for filtering lists search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated: str | None`
    :   The type of the None singleton.

`ListsSearchQuery(*args, **kwargs)`
:   Search query for lists entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.klaviyo.types.ListsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.klaviyo.types.ListsSortFilter]`
    :   The type of the None singleton.

`ListsSortFilter(*args, **kwargs)`
:   Available fields for sorting lists search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `links: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `relationships: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `type_: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `updated: Literal['asc', 'desc']`
    :   The type of the None singleton.

`ListsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `links: str`
    :   The type of the None singleton.

    `relationships: str`
    :   The type of the None singleton.

    `type_: str`
    :   The type of the None singleton.

    `updated: str`
    :   The type of the None singleton.

`MetricsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.klaviyo.types.MetricsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsAnyCondition]`
    :   The type of the None singleton.

`MetricsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.klaviyo.types.MetricsAnyValueFilter`
    :   The type of the None singleton.

`MetricsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Any`
    :   The type of the None singleton.

    `id: Any`
    :   The type of the None singleton.

    `links: Any`
    :   The type of the None singleton.

    `relationships: Any`
    :   The type of the None singleton.

    `type_: Any`
    :   The type of the None singleton.

    `updated: Any`
    :   The type of the None singleton.

`MetricsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.klaviyo.types.MetricsAnyValueFilter`
    :   The type of the None singleton.

`MetricsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.klaviyo.types.MetricsSearchFilter`
    :   The type of the None singleton.

`MetricsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.klaviyo.types.MetricsStringFilter`
    :   The type of the None singleton.

`MetricsGetParams(*args, **kwargs)`
:   Parameters for metrics.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`MetricsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.klaviyo.types.MetricsSearchFilter`
    :   The type of the None singleton.

`MetricsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.klaviyo.types.MetricsSearchFilter`
    :   The type of the None singleton.

`MetricsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.klaviyo.types.MetricsInFilter`
    :   The type of the None singleton.

`MetricsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `links: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `relationships: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `type_: list[str]`
    :   The type of the None singleton.

    `updated: list[str]`
    :   The type of the None singleton.

`MetricsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.klaviyo.types.MetricsStringFilter`
    :   The type of the None singleton.

`MetricsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.klaviyo.types.MetricsStringFilter`
    :   The type of the None singleton.

`MetricsListParams(*args, **kwargs)`
:   Parameters for metrics.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_cursor: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`MetricsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.klaviyo.types.MetricsSearchFilter`
    :   The type of the None singleton.

`MetricsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.klaviyo.types.MetricsSearchFilter`
    :   The type of the None singleton.

`MetricsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.klaviyo.types.MetricsSearchFilter`
    :   The type of the None singleton.

`MetricsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.klaviyo.types.MetricsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsAnyCondition`
    :   The type of the None singleton.

`MetricsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.klaviyo.types.MetricsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsAnyCondition]`
    :   The type of the None singleton.

`MetricsSearchFilter(*args, **kwargs)`
:   Available fields for filtering metrics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated: str | None`
    :   The type of the None singleton.

`MetricsSearchQuery(*args, **kwargs)`
:   Search query for metrics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.klaviyo.types.MetricsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.klaviyo.types.MetricsSortFilter]`
    :   The type of the None singleton.

`MetricsSortFilter(*args, **kwargs)`
:   Available fields for sorting metrics search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `links: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `relationships: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `type_: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `updated: Literal['asc', 'desc']`
    :   The type of the None singleton.

`MetricsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `links: str`
    :   The type of the None singleton.

    `relationships: str`
    :   The type of the None singleton.

    `type_: str`
    :   The type of the None singleton.

    `updated: str`
    :   The type of the None singleton.

`ProfilesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.klaviyo.types.ProfilesEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesInCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesAnyCondition]`
    :   The type of the None singleton.

`ProfilesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesAnyValueFilter`
    :   The type of the None singleton.

`ProfilesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Any`
    :   The type of the None singleton.

    `id: Any`
    :   The type of the None singleton.

    `links: Any`
    :   The type of the None singleton.

    `relationships: Any`
    :   The type of the None singleton.

    `segments: Any`
    :   The type of the None singleton.

    `type_: Any`
    :   The type of the None singleton.

    `updated: Any`
    :   The type of the None singleton.

`ProfilesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesAnyValueFilter`
    :   The type of the None singleton.

`ProfilesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesSearchFilter`
    :   The type of the None singleton.

`ProfilesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesStringFilter`
    :   The type of the None singleton.

`ProfilesGetParams(*args, **kwargs)`
:   Parameters for profiles.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`ProfilesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesSearchFilter`
    :   The type of the None singleton.

`ProfilesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesSearchFilter`
    :   The type of the None singleton.

`ProfilesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesInFilter`
    :   The type of the None singleton.

`ProfilesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `links: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `relationships: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `segments: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `type_: list[str]`
    :   The type of the None singleton.

    `updated: list[str]`
    :   The type of the None singleton.

`ProfilesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesStringFilter`
    :   The type of the None singleton.

`ProfilesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesStringFilter`
    :   The type of the None singleton.

`ProfilesListParams(*args, **kwargs)`
:   Parameters for profiles.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_cursor: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`ProfilesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesSearchFilter`
    :   The type of the None singleton.

`ProfilesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesSearchFilter`
    :   The type of the None singleton.

`ProfilesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesSearchFilter`
    :   The type of the None singleton.

`ProfilesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesInCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesAnyCondition`
    :   The type of the None singleton.

`ProfilesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.klaviyo.types.ProfilesEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesInCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesAnyCondition]`
    :   The type of the None singleton.

`ProfilesSearchFilter(*args, **kwargs)`
:   Available fields for filtering profiles search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `segments: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated: str | None`
    :   The type of the None singleton.

`ProfilesSearchQuery(*args, **kwargs)`
:   Search query for profiles entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesInCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.klaviyo.types.ProfilesSortFilter]`
    :   The type of the None singleton.

`ProfilesSortFilter(*args, **kwargs)`
:   Available fields for sorting profiles search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `links: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `relationships: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `segments: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `type_: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `updated: Literal['asc', 'desc']`
    :   The type of the None singleton.

`ProfilesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attributes: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `links: str`
    :   The type of the None singleton.

    `relationships: str`
    :   The type of the None singleton.

    `segments: str`
    :   The type of the None singleton.

    `type_: str`
    :   The type of the None singleton.

    `updated: str`
    :   The type of the None singleton.