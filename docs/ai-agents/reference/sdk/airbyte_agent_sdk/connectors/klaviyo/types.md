---
id: airbyte_agent_sdk-connectors-klaviyo-types
title: airbyte_agent_sdk.connectors.klaviyo.types
---

Module airbyte_agent_sdk.connectors.klaviyo.types
=================================================
Type definitions for klaviyo connector.

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

<a id="CampaignsAndCondition"></a>

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

<a id="CampaignsAnyCondition"></a>

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

<a id="CampaignsAnyValueFilter"></a>

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

<a id="CampaignsContainsCondition"></a>

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsEqCondition"></a>

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsFuzzyCondition"></a>

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsGetParams"></a>

`CampaignsGetParams(*args, **kwargs)`
:   Parameters for campaigns.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CampaignsGtCondition"></a>

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsGteCondition"></a>

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsInCondition"></a>

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

<a id="CampaignsInFilter"></a>

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

<a id="CampaignsKeywordCondition"></a>

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsLikeCondition"></a>

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsListParams"></a>

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

<a id="CampaignsLtCondition"></a>

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsLteCondition"></a>

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsNeqCondition"></a>

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsNotCondition"></a>

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

<a id="CampaignsOrCondition"></a>

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

<a id="CampaignsSearchFilter"></a>

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

<a id="CampaignsSearchQuery"></a>

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.klaviyo.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.klaviyo.types.CampaignsSortFilter]`
    :   The type of the None singleton.

<a id="CampaignsSortFilter"></a>

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

<a id="CampaignsStringFilter"></a>

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

<a id="EmailTemplatesAndCondition"></a>

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

<a id="EmailTemplatesAnyCondition"></a>

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

<a id="EmailTemplatesAnyValueFilter"></a>

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

<a id="EmailTemplatesContainsCondition"></a>

`EmailTemplatesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesAnyValueFilter`
    :   The type of the None singleton.

<a id="EmailTemplatesEqCondition"></a>

`EmailTemplatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesSearchFilter`
    :   The type of the None singleton.

<a id="EmailTemplatesFuzzyCondition"></a>

`EmailTemplatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesStringFilter`
    :   The type of the None singleton.

<a id="EmailTemplatesGetParams"></a>

`EmailTemplatesGetParams(*args, **kwargs)`
:   Parameters for email_templates.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="EmailTemplatesGtCondition"></a>

`EmailTemplatesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesSearchFilter`
    :   The type of the None singleton.

<a id="EmailTemplatesGteCondition"></a>

`EmailTemplatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesSearchFilter`
    :   The type of the None singleton.

<a id="EmailTemplatesInCondition"></a>

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

<a id="EmailTemplatesInFilter"></a>

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

<a id="EmailTemplatesKeywordCondition"></a>

`EmailTemplatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesStringFilter`
    :   The type of the None singleton.

<a id="EmailTemplatesLikeCondition"></a>

`EmailTemplatesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesStringFilter`
    :   The type of the None singleton.

<a id="EmailTemplatesListParams"></a>

`EmailTemplatesListParams(*args, **kwargs)`
:   Parameters for email_templates.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_cursor: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="EmailTemplatesLtCondition"></a>

`EmailTemplatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesSearchFilter`
    :   The type of the None singleton.

<a id="EmailTemplatesLteCondition"></a>

`EmailTemplatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesSearchFilter`
    :   The type of the None singleton.

<a id="EmailTemplatesNeqCondition"></a>

`EmailTemplatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesSearchFilter`
    :   The type of the None singleton.

<a id="EmailTemplatesNotCondition"></a>

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

<a id="EmailTemplatesOrCondition"></a>

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

<a id="EmailTemplatesSearchFilter"></a>

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

<a id="EmailTemplatesSearchQuery"></a>

`EmailTemplatesSearchQuery(*args, **kwargs)`
:   Search query for email_templates entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesInCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.klaviyo.types.EmailTemplatesSortFilter]`
    :   The type of the None singleton.

<a id="EmailTemplatesSortFilter"></a>

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

<a id="EmailTemplatesStringFilter"></a>

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

<a id="EventsAndCondition"></a>

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

<a id="EventsAnyCondition"></a>

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

<a id="EventsAnyValueFilter"></a>

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

<a id="EventsContainsCondition"></a>

`EventsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.klaviyo.types.EventsAnyValueFilter`
    :   The type of the None singleton.

<a id="EventsEqCondition"></a>

`EventsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.klaviyo.types.EventsSearchFilter`
    :   The type of the None singleton.

<a id="EventsFuzzyCondition"></a>

`EventsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.klaviyo.types.EventsStringFilter`
    :   The type of the None singleton.

<a id="EventsGtCondition"></a>

`EventsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.klaviyo.types.EventsSearchFilter`
    :   The type of the None singleton.

<a id="EventsGteCondition"></a>

`EventsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.klaviyo.types.EventsSearchFilter`
    :   The type of the None singleton.

<a id="EventsInCondition"></a>

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

<a id="EventsInFilter"></a>

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

<a id="EventsKeywordCondition"></a>

`EventsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.klaviyo.types.EventsStringFilter`
    :   The type of the None singleton.

<a id="EventsLikeCondition"></a>

`EventsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.klaviyo.types.EventsStringFilter`
    :   The type of the None singleton.

<a id="EventsListParams"></a>

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

<a id="EventsLtCondition"></a>

`EventsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.klaviyo.types.EventsSearchFilter`
    :   The type of the None singleton.

<a id="EventsLteCondition"></a>

`EventsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.klaviyo.types.EventsSearchFilter`
    :   The type of the None singleton.

<a id="EventsNeqCondition"></a>

`EventsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.klaviyo.types.EventsSearchFilter`
    :   The type of the None singleton.

<a id="EventsNotCondition"></a>

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

<a id="EventsOrCondition"></a>

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

<a id="EventsSearchFilter"></a>

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

<a id="EventsSearchQuery"></a>

`EventsSearchQuery(*args, **kwargs)`
:   Search query for events entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.klaviyo.types.EventsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.EventsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.klaviyo.types.EventsSortFilter]`
    :   The type of the None singleton.

<a id="EventsSortFilter"></a>

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

<a id="EventsStringFilter"></a>

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

<a id="FlowsAndCondition"></a>

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

<a id="FlowsAnyCondition"></a>

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

<a id="FlowsAnyValueFilter"></a>

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

<a id="FlowsContainsCondition"></a>

`FlowsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.klaviyo.types.FlowsAnyValueFilter`
    :   The type of the None singleton.

<a id="FlowsEqCondition"></a>

`FlowsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.klaviyo.types.FlowsSearchFilter`
    :   The type of the None singleton.

<a id="FlowsFuzzyCondition"></a>

`FlowsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.klaviyo.types.FlowsStringFilter`
    :   The type of the None singleton.

<a id="FlowsGetParams"></a>

`FlowsGetParams(*args, **kwargs)`
:   Parameters for flows.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="FlowsGtCondition"></a>

`FlowsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.klaviyo.types.FlowsSearchFilter`
    :   The type of the None singleton.

<a id="FlowsGteCondition"></a>

`FlowsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.klaviyo.types.FlowsSearchFilter`
    :   The type of the None singleton.

<a id="FlowsInCondition"></a>

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

<a id="FlowsInFilter"></a>

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

<a id="FlowsKeywordCondition"></a>

`FlowsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.klaviyo.types.FlowsStringFilter`
    :   The type of the None singleton.

<a id="FlowsLikeCondition"></a>

`FlowsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.klaviyo.types.FlowsStringFilter`
    :   The type of the None singleton.

<a id="FlowsListParams"></a>

`FlowsListParams(*args, **kwargs)`
:   Parameters for flows.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_cursor: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="FlowsLtCondition"></a>

`FlowsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.klaviyo.types.FlowsSearchFilter`
    :   The type of the None singleton.

<a id="FlowsLteCondition"></a>

`FlowsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.klaviyo.types.FlowsSearchFilter`
    :   The type of the None singleton.

<a id="FlowsNeqCondition"></a>

`FlowsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.klaviyo.types.FlowsSearchFilter`
    :   The type of the None singleton.

<a id="FlowsNotCondition"></a>

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

<a id="FlowsOrCondition"></a>

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

<a id="FlowsSearchFilter"></a>

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

<a id="FlowsSearchQuery"></a>

`FlowsSearchQuery(*args, **kwargs)`
:   Search query for flows entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.klaviyo.types.FlowsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.FlowsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.klaviyo.types.FlowsSortFilter]`
    :   The type of the None singleton.

<a id="FlowsSortFilter"></a>

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

<a id="FlowsStringFilter"></a>

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

<a id="ListsAndCondition"></a>

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

<a id="ListsAnyCondition"></a>

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

<a id="ListsAnyValueFilter"></a>

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

<a id="ListsContainsCondition"></a>

`ListsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.klaviyo.types.ListsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListsEqCondition"></a>

`ListsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.klaviyo.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsFuzzyCondition"></a>

`ListsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.klaviyo.types.ListsStringFilter`
    :   The type of the None singleton.

<a id="ListsGetParams"></a>

`ListsGetParams(*args, **kwargs)`
:   Parameters for lists.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ListsGtCondition"></a>

`ListsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.klaviyo.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsGteCondition"></a>

`ListsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.klaviyo.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsInCondition"></a>

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

<a id="ListsInFilter"></a>

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

<a id="ListsKeywordCondition"></a>

`ListsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.klaviyo.types.ListsStringFilter`
    :   The type of the None singleton.

<a id="ListsLikeCondition"></a>

`ListsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.klaviyo.types.ListsStringFilter`
    :   The type of the None singleton.

<a id="ListsListParams"></a>

`ListsListParams(*args, **kwargs)`
:   Parameters for lists.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_cursor: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="ListsLtCondition"></a>

`ListsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.klaviyo.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsLteCondition"></a>

`ListsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.klaviyo.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsNeqCondition"></a>

`ListsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.klaviyo.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsNotCondition"></a>

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

<a id="ListsOrCondition"></a>

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

<a id="ListsSearchFilter"></a>

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

<a id="ListsSearchQuery"></a>

`ListsSearchQuery(*args, **kwargs)`
:   Search query for lists entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.klaviyo.types.ListsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.ListsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.klaviyo.types.ListsSortFilter]`
    :   The type of the None singleton.

<a id="ListsSortFilter"></a>

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

<a id="ListsStringFilter"></a>

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

<a id="MetricsAndCondition"></a>

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

<a id="MetricsAnyCondition"></a>

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

<a id="MetricsAnyValueFilter"></a>

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

<a id="MetricsContainsCondition"></a>

`MetricsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.klaviyo.types.MetricsAnyValueFilter`
    :   The type of the None singleton.

<a id="MetricsEqCondition"></a>

`MetricsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.klaviyo.types.MetricsSearchFilter`
    :   The type of the None singleton.

<a id="MetricsFuzzyCondition"></a>

`MetricsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.klaviyo.types.MetricsStringFilter`
    :   The type of the None singleton.

<a id="MetricsGetParams"></a>

`MetricsGetParams(*args, **kwargs)`
:   Parameters for metrics.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="MetricsGtCondition"></a>

`MetricsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.klaviyo.types.MetricsSearchFilter`
    :   The type of the None singleton.

<a id="MetricsGteCondition"></a>

`MetricsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.klaviyo.types.MetricsSearchFilter`
    :   The type of the None singleton.

<a id="MetricsInCondition"></a>

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

<a id="MetricsInFilter"></a>

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

<a id="MetricsKeywordCondition"></a>

`MetricsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.klaviyo.types.MetricsStringFilter`
    :   The type of the None singleton.

<a id="MetricsLikeCondition"></a>

`MetricsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.klaviyo.types.MetricsStringFilter`
    :   The type of the None singleton.

<a id="MetricsListParams"></a>

`MetricsListParams(*args, **kwargs)`
:   Parameters for metrics.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_cursor: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="MetricsLtCondition"></a>

`MetricsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.klaviyo.types.MetricsSearchFilter`
    :   The type of the None singleton.

<a id="MetricsLteCondition"></a>

`MetricsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.klaviyo.types.MetricsSearchFilter`
    :   The type of the None singleton.

<a id="MetricsNeqCondition"></a>

`MetricsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.klaviyo.types.MetricsSearchFilter`
    :   The type of the None singleton.

<a id="MetricsNotCondition"></a>

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

<a id="MetricsOrCondition"></a>

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

<a id="MetricsSearchFilter"></a>

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

<a id="MetricsSearchQuery"></a>

`MetricsSearchQuery(*args, **kwargs)`
:   Search query for metrics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.klaviyo.types.MetricsEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsInCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.MetricsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.klaviyo.types.MetricsSortFilter]`
    :   The type of the None singleton.

<a id="MetricsSortFilter"></a>

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

<a id="MetricsStringFilter"></a>

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

<a id="ProfilesAndCondition"></a>

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

<a id="ProfilesAnyCondition"></a>

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

<a id="ProfilesAnyValueFilter"></a>

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

<a id="ProfilesContainsCondition"></a>

`ProfilesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesAnyValueFilter`
    :   The type of the None singleton.

<a id="ProfilesEqCondition"></a>

`ProfilesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesSearchFilter`
    :   The type of the None singleton.

<a id="ProfilesFuzzyCondition"></a>

`ProfilesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesStringFilter`
    :   The type of the None singleton.

<a id="ProfilesGetParams"></a>

`ProfilesGetParams(*args, **kwargs)`
:   Parameters for profiles.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ProfilesGtCondition"></a>

`ProfilesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesSearchFilter`
    :   The type of the None singleton.

<a id="ProfilesGteCondition"></a>

`ProfilesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesSearchFilter`
    :   The type of the None singleton.

<a id="ProfilesInCondition"></a>

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

<a id="ProfilesInFilter"></a>

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

<a id="ProfilesKeywordCondition"></a>

`ProfilesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesStringFilter`
    :   The type of the None singleton.

<a id="ProfilesLikeCondition"></a>

`ProfilesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesStringFilter`
    :   The type of the None singleton.

<a id="ProfilesListParams"></a>

`ProfilesListParams(*args, **kwargs)`
:   Parameters for profiles.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_cursor: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="ProfilesLtCondition"></a>

`ProfilesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesSearchFilter`
    :   The type of the None singleton.

<a id="ProfilesLteCondition"></a>

`ProfilesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesSearchFilter`
    :   The type of the None singleton.

<a id="ProfilesNeqCondition"></a>

`ProfilesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesSearchFilter`
    :   The type of the None singleton.

<a id="ProfilesNotCondition"></a>

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

<a id="ProfilesOrCondition"></a>

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

<a id="ProfilesSearchFilter"></a>

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

<a id="ProfilesSearchQuery"></a>

`ProfilesSearchQuery(*args, **kwargs)`
:   Search query for profiles entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.klaviyo.types.ProfilesEqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesNeqCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesGtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesGteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLtCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLteCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesInCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesLikeCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesFuzzyCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesKeywordCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesContainsCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesNotCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesAndCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesOrCondition | airbyte_agent_sdk.connectors.klaviyo.types.ProfilesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.klaviyo.types.ProfilesSortFilter]`
    :   The type of the None singleton.

<a id="ProfilesSortFilter"></a>

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

<a id="ProfilesStringFilter"></a>

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