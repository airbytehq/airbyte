---
id: airbyte_agent_sdk-connectors-gmail-types
title: airbyte_agent_sdk.connectors.gmail.types
---

Module airbyte_agent_sdk.connectors.gmail.types
===============================================
Type definitions for gmail connector.

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

<a id="DraftsAndCondition"></a>

`DraftsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.gmail.types.DraftsEqCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsNeqCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsGtCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsGteCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsLtCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsLteCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsInCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsLikeCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsContainsCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsNotCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsAndCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsOrCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsAnyCondition]`
    :   The type of the None singleton.

<a id="DraftsAnyCondition"></a>

`DraftsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.gmail.types.DraftsAnyValueFilter`
    :   The type of the None singleton.

<a id="DraftsAnyValueFilter"></a>

`DraftsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier for the draft

    `message: Any`
    :   Draft message payload (headers, body, and metadata)

<a id="DraftsContainsCondition"></a>

`DraftsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gmail.types.DraftsAnyValueFilter`
    :   The type of the None singleton.

<a id="DraftsCreateParams"></a>

`DraftsCreateParams(*args, **kwargs)`
:   Parameters for drafts.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `message: airbyte_agent_sdk.connectors.gmail.types.DraftsCreateParamsMessage`
    :   The type of the None singleton.

<a id="DraftsCreateParamsMessage"></a>

`DraftsCreateParamsMessage(*args, **kwargs)`
:   The draft message content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `raw: str`
    :   The type of the None singleton.

    `threadId: str`
    :   The type of the None singleton.

<a id="DraftsDeleteParams"></a>

`DraftsDeleteParams(*args, **kwargs)`
:   Parameters for drafts.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `draft_id: str`
    :   The type of the None singleton.

<a id="DraftsEqCondition"></a>

`DraftsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gmail.types.DraftsSearchFilter`
    :   The type of the None singleton.

<a id="DraftsFuzzyCondition"></a>

`DraftsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gmail.types.DraftsStringFilter`
    :   The type of the None singleton.

<a id="DraftsGetParams"></a>

`DraftsGetParams(*args, **kwargs)`
:   Parameters for drafts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `draft_id: str`
    :   The type of the None singleton.

    `format: str`
    :   The type of the None singleton.

<a id="DraftsGtCondition"></a>

`DraftsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gmail.types.DraftsSearchFilter`
    :   The type of the None singleton.

<a id="DraftsGteCondition"></a>

`DraftsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gmail.types.DraftsSearchFilter`
    :   The type of the None singleton.

<a id="DraftsInCondition"></a>

`DraftsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.gmail.types.DraftsInFilter`
    :   The type of the None singleton.

<a id="DraftsInFilter"></a>

`DraftsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[str]`
    :   Unique identifier for the draft

    `message: list[dict[str, typing.Any]]`
    :   Draft message payload (headers, body, and metadata)

<a id="DraftsKeywordCondition"></a>

`DraftsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gmail.types.DraftsStringFilter`
    :   The type of the None singleton.

<a id="DraftsLikeCondition"></a>

`DraftsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gmail.types.DraftsStringFilter`
    :   The type of the None singleton.

<a id="DraftsListParams"></a>

`DraftsListParams(*args, **kwargs)`
:   Parameters for drafts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include_spam_trash: bool`
    :   The type of the None singleton.

    `max_results: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

<a id="DraftsLtCondition"></a>

`DraftsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gmail.types.DraftsSearchFilter`
    :   The type of the None singleton.

<a id="DraftsLteCondition"></a>

`DraftsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gmail.types.DraftsSearchFilter`
    :   The type of the None singleton.

<a id="DraftsNeqCondition"></a>

`DraftsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gmail.types.DraftsSearchFilter`
    :   The type of the None singleton.

<a id="DraftsNotCondition"></a>

`DraftsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.gmail.types.DraftsEqCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsNeqCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsGtCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsGteCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsLtCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsLteCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsInCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsLikeCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsContainsCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsNotCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsAndCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsOrCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsAnyCondition`
    :   The type of the None singleton.

<a id="DraftsOrCondition"></a>

`DraftsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.gmail.types.DraftsEqCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsNeqCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsGtCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsGteCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsLtCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsLteCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsInCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsLikeCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsContainsCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsNotCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsAndCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsOrCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsAnyCondition]`
    :   The type of the None singleton.

<a id="DraftsSearchFilter"></a>

`DraftsSearchFilter(*args, **kwargs)`
:   Available fields for filtering drafts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the draft

    `message: dict[str, typing.Any] | None`
    :   Draft message payload (headers, body, and metadata)

<a id="DraftsSearchQuery"></a>

`DraftsSearchQuery(*args, **kwargs)`
:   Search query for drafts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gmail.types.DraftsEqCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsNeqCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsGtCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsGteCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsLtCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsLteCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsInCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsLikeCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsContainsCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsNotCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsAndCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsOrCondition | airbyte_agent_sdk.connectors.gmail.types.DraftsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gmail.types.DraftsSortFilter]`
    :   The type of the None singleton.

<a id="DraftsSendCreateParams"></a>

`DraftsSendCreateParams(*args, **kwargs)`
:   Parameters for drafts_send.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="DraftsSortFilter"></a>

`DraftsSortFilter(*args, **kwargs)`
:   Available fields for sorting drafts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the draft

    `message: Literal['asc', 'desc']`
    :   Draft message payload (headers, body, and metadata)

<a id="DraftsStringFilter"></a>

`DraftsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the draft

    `message: str`
    :   Draft message payload (headers, body, and metadata)

<a id="DraftsUpdateParams"></a>

`DraftsUpdateParams(*args, **kwargs)`
:   Parameters for drafts.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `draft_id: str`
    :   The type of the None singleton.

    `message: airbyte_agent_sdk.connectors.gmail.types.DraftsUpdateParamsMessage`
    :   The type of the None singleton.

<a id="DraftsUpdateParamsMessage"></a>

`DraftsUpdateParamsMessage(*args, **kwargs)`
:   The draft message content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `raw: str`
    :   The type of the None singleton.

    `threadId: str`
    :   The type of the None singleton.

<a id="LabelsAndCondition"></a>

`LabelsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.gmail.types.LabelsEqCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsNeqCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsGtCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsGteCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsLtCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsLteCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsInCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsLikeCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsContainsCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsNotCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsAndCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsOrCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsAnyCondition]`
    :   The type of the None singleton.

<a id="LabelsAnyCondition"></a>

`LabelsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.gmail.types.LabelsAnyValueFilter`
    :   The type of the None singleton.

<a id="LabelsAnyValueFilter"></a>

`LabelsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier for the label

    `label_list_visibility: Any`
    :   Visibility of the label in the label list

    `message_list_visibility: Any`
    :   Visibility of the label when viewing a message list

    `name: Any`
    :   Display name of the label

    `type_: Any`
    :   Label type: `system` or `user`

<a id="LabelsContainsCondition"></a>

`LabelsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gmail.types.LabelsAnyValueFilter`
    :   The type of the None singleton.

<a id="LabelsCreateParams"></a>

`LabelsCreateParams(*args, **kwargs)`
:   Parameters for labels.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: airbyte_agent_sdk.connectors.gmail.types.LabelsCreateParamsColor`
    :   The type of the None singleton.

    `label_list_visibility: str`
    :   The type of the None singleton.

    `message_list_visibility: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="LabelsCreateParamsColor"></a>

`LabelsCreateParamsColor(*args, **kwargs)`
:   The color to assign to the label

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `backgroundColor: str`
    :   The type of the None singleton.

    `textColor: str`
    :   The type of the None singleton.

<a id="LabelsDeleteParams"></a>

`LabelsDeleteParams(*args, **kwargs)`
:   Parameters for labels.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `label_id: str`
    :   The type of the None singleton.

<a id="LabelsEqCondition"></a>

`LabelsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gmail.types.LabelsSearchFilter`
    :   The type of the None singleton.

<a id="LabelsFuzzyCondition"></a>

`LabelsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gmail.types.LabelsStringFilter`
    :   The type of the None singleton.

<a id="LabelsGetParams"></a>

`LabelsGetParams(*args, **kwargs)`
:   Parameters for labels.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `label_id: str`
    :   The type of the None singleton.

<a id="LabelsGtCondition"></a>

`LabelsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gmail.types.LabelsSearchFilter`
    :   The type of the None singleton.

<a id="LabelsGteCondition"></a>

`LabelsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gmail.types.LabelsSearchFilter`
    :   The type of the None singleton.

<a id="LabelsInCondition"></a>

`LabelsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.gmail.types.LabelsInFilter`
    :   The type of the None singleton.

<a id="LabelsInFilter"></a>

`LabelsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[str]`
    :   Unique identifier for the label

    `label_list_visibility: list[str]`
    :   Visibility of the label in the label list

    `message_list_visibility: list[str]`
    :   Visibility of the label when viewing a message list

    `name: list[str]`
    :   Display name of the label

    `type_: list[str]`
    :   Label type: `system` or `user`

<a id="LabelsKeywordCondition"></a>

`LabelsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gmail.types.LabelsStringFilter`
    :   The type of the None singleton.

<a id="LabelsLikeCondition"></a>

`LabelsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gmail.types.LabelsStringFilter`
    :   The type of the None singleton.

<a id="LabelsListParams"></a>

`LabelsListParams(*args, **kwargs)`
:   Parameters for labels.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="LabelsLtCondition"></a>

`LabelsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gmail.types.LabelsSearchFilter`
    :   The type of the None singleton.

<a id="LabelsLteCondition"></a>

`LabelsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gmail.types.LabelsSearchFilter`
    :   The type of the None singleton.

<a id="LabelsNeqCondition"></a>

`LabelsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gmail.types.LabelsSearchFilter`
    :   The type of the None singleton.

<a id="LabelsNotCondition"></a>

`LabelsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.gmail.types.LabelsEqCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsNeqCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsGtCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsGteCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsLtCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsLteCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsInCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsLikeCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsContainsCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsNotCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsAndCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsOrCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsAnyCondition`
    :   The type of the None singleton.

<a id="LabelsOrCondition"></a>

`LabelsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.gmail.types.LabelsEqCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsNeqCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsGtCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsGteCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsLtCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsLteCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsInCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsLikeCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsContainsCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsNotCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsAndCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsOrCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsAnyCondition]`
    :   The type of the None singleton.

<a id="LabelsSearchFilter"></a>

`LabelsSearchFilter(*args, **kwargs)`
:   Available fields for filtering labels search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the label

    `label_list_visibility: str | None`
    :   Visibility of the label in the label list

    `message_list_visibility: str | None`
    :   Visibility of the label when viewing a message list

    `name: str | None`
    :   Display name of the label

    `type_: str | None`
    :   Label type: `system` or `user`

<a id="LabelsSearchQuery"></a>

`LabelsSearchQuery(*args, **kwargs)`
:   Search query for labels entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gmail.types.LabelsEqCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsNeqCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsGtCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsGteCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsLtCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsLteCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsInCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsLikeCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsContainsCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsNotCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsAndCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsOrCondition | airbyte_agent_sdk.connectors.gmail.types.LabelsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gmail.types.LabelsSortFilter]`
    :   The type of the None singleton.

<a id="LabelsSortFilter"></a>

`LabelsSortFilter(*args, **kwargs)`
:   Available fields for sorting labels search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the label

    `label_list_visibility: Literal['asc', 'desc']`
    :   Visibility of the label in the label list

    `message_list_visibility: Literal['asc', 'desc']`
    :   Visibility of the label when viewing a message list

    `name: Literal['asc', 'desc']`
    :   Display name of the label

    `type_: Literal['asc', 'desc']`
    :   Label type: `system` or `user`

<a id="LabelsStringFilter"></a>

`LabelsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the label

    `label_list_visibility: str`
    :   Visibility of the label in the label list

    `message_list_visibility: str`
    :   Visibility of the label when viewing a message list

    `name: str`
    :   Display name of the label

    `type_: str`
    :   Label type: `system` or `user`

<a id="LabelsUpdateParams"></a>

`LabelsUpdateParams(*args, **kwargs)`
:   Parameters for labels.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: airbyte_agent_sdk.connectors.gmail.types.LabelsUpdateParamsColor`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `label_id: str`
    :   The type of the None singleton.

    `label_list_visibility: str`
    :   The type of the None singleton.

    `message_list_visibility: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="LabelsUpdateParamsColor"></a>

`LabelsUpdateParamsColor(*args, **kwargs)`
:   The color to assign to the label

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `backgroundColor: str`
    :   The type of the None singleton.

    `textColor: str`
    :   The type of the None singleton.

<a id="MessagesAndCondition"></a>

`MessagesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.gmail.types.MessagesEqCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesNeqCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesGtCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesGteCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesLtCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesLteCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesInCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesLikeCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesContainsCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesNotCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesAndCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesOrCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesAnyCondition]`
    :   The type of the None singleton.

<a id="MessagesAnyCondition"></a>

`MessagesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.gmail.types.MessagesAnyValueFilter`
    :   The type of the None singleton.

<a id="MessagesAnyValueFilter"></a>

`MessagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier for the message

    `thread_id: Any`
    :   Identifier of the thread this message belongs to

<a id="MessagesContainsCondition"></a>

`MessagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gmail.types.MessagesAnyValueFilter`
    :   The type of the None singleton.

<a id="MessagesCreateParams"></a>

`MessagesCreateParams(*args, **kwargs)`
:   Parameters for messages.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `raw: str`
    :   The type of the None singleton.

    `thread_id: str`
    :   The type of the None singleton.

<a id="MessagesEqCondition"></a>

`MessagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gmail.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesFuzzyCondition"></a>

`MessagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gmail.types.MessagesStringFilter`
    :   The type of the None singleton.

<a id="MessagesGetParams"></a>

`MessagesGetParams(*args, **kwargs)`
:   Parameters for messages.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `format: str`
    :   The type of the None singleton.

    `message_id: str`
    :   The type of the None singleton.

    `metadata_headers: str`
    :   The type of the None singleton.

<a id="MessagesGtCondition"></a>

`MessagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gmail.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesGteCondition"></a>

`MessagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gmail.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesInCondition"></a>

`MessagesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.gmail.types.MessagesInFilter`
    :   The type of the None singleton.

<a id="MessagesInFilter"></a>

`MessagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[str]`
    :   Unique identifier for the message

    `thread_id: list[str]`
    :   Identifier of the thread this message belongs to

<a id="MessagesKeywordCondition"></a>

`MessagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gmail.types.MessagesStringFilter`
    :   The type of the None singleton.

<a id="MessagesLikeCondition"></a>

`MessagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gmail.types.MessagesStringFilter`
    :   The type of the None singleton.

<a id="MessagesListParams"></a>

`MessagesListParams(*args, **kwargs)`
:   Parameters for messages.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include_spam_trash: bool`
    :   The type of the None singleton.

    `label_ids: str`
    :   The type of the None singleton.

    `max_results: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

<a id="MessagesLtCondition"></a>

`MessagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gmail.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesLteCondition"></a>

`MessagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gmail.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesNeqCondition"></a>

`MessagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gmail.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesNotCondition"></a>

`MessagesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.gmail.types.MessagesEqCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesNeqCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesGtCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesGteCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesLtCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesLteCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesInCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesLikeCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesContainsCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesNotCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesAndCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesOrCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesAnyCondition`
    :   The type of the None singleton.

<a id="MessagesOrCondition"></a>

`MessagesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.gmail.types.MessagesEqCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesNeqCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesGtCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesGteCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesLtCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesLteCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesInCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesLikeCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesContainsCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesNotCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesAndCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesOrCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesAnyCondition]`
    :   The type of the None singleton.

<a id="MessagesSearchFilter"></a>

`MessagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering messages search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the message

    `thread_id: str | None`
    :   Identifier of the thread this message belongs to

<a id="MessagesSearchQuery"></a>

`MessagesSearchQuery(*args, **kwargs)`
:   Search query for messages entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gmail.types.MessagesEqCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesNeqCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesGtCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesGteCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesLtCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesLteCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesInCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesLikeCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesContainsCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesNotCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesAndCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesOrCondition | airbyte_agent_sdk.connectors.gmail.types.MessagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gmail.types.MessagesSortFilter]`
    :   The type of the None singleton.

<a id="MessagesSortFilter"></a>

`MessagesSortFilter(*args, **kwargs)`
:   Available fields for sorting messages search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the message

    `thread_id: Literal['asc', 'desc']`
    :   Identifier of the thread this message belongs to

<a id="MessagesStringFilter"></a>

`MessagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the message

    `thread_id: str`
    :   Identifier of the thread this message belongs to

<a id="MessagesTrashCreateParams"></a>

`MessagesTrashCreateParams(*args, **kwargs)`
:   Parameters for messages_trash.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `message_id: str`
    :   The type of the None singleton.

<a id="MessagesUntrashCreateParams"></a>

`MessagesUntrashCreateParams(*args, **kwargs)`
:   Parameters for messages_untrash.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `message_id: str`
    :   The type of the None singleton.

<a id="MessagesUpdateParams"></a>

`MessagesUpdateParams(*args, **kwargs)`
:   Parameters for messages.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `add_label_ids: list[str]`
    :   The type of the None singleton.

    `message_id: str`
    :   The type of the None singleton.

    `remove_label_ids: list[str]`
    :   The type of the None singleton.

<a id="ProfileAndCondition"></a>

`ProfileAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.gmail.types.ProfileEqCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileNeqCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileGtCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileGteCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileLtCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileLteCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileInCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileLikeCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileContainsCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileNotCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileAndCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileOrCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileAnyCondition]`
    :   The type of the None singleton.

<a id="ProfileAnyCondition"></a>

`ProfileAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.gmail.types.ProfileAnyValueFilter`
    :   The type of the None singleton.

<a id="ProfileAnyValueFilter"></a>

`ProfileAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email_address: Any`
    :   Email address of the authenticated Gmail account

    `history_id: Any`
    :   Mailbox history record identifier used for incremental sync

    `messages_total: Any`
    :   Total number of messages currently in the mailbox

    `threads_total: Any`
    :   Total number of threads currently in the mailbox

<a id="ProfileContainsCondition"></a>

`ProfileContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gmail.types.ProfileAnyValueFilter`
    :   The type of the None singleton.

<a id="ProfileEqCondition"></a>

`ProfileEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gmail.types.ProfileSearchFilter`
    :   The type of the None singleton.

<a id="ProfileFuzzyCondition"></a>

`ProfileFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gmail.types.ProfileStringFilter`
    :   The type of the None singleton.

<a id="ProfileGetParams"></a>

`ProfileGetParams(*args, **kwargs)`
:   Parameters for profile.get operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ProfileGtCondition"></a>

`ProfileGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gmail.types.ProfileSearchFilter`
    :   The type of the None singleton.

<a id="ProfileGteCondition"></a>

`ProfileGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gmail.types.ProfileSearchFilter`
    :   The type of the None singleton.

<a id="ProfileInCondition"></a>

`ProfileInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.gmail.types.ProfileInFilter`
    :   The type of the None singleton.

<a id="ProfileInFilter"></a>

`ProfileInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email_address: list[str]`
    :   Email address of the authenticated Gmail account

    `history_id: list[str]`
    :   Mailbox history record identifier used for incremental sync

    `messages_total: list[float]`
    :   Total number of messages currently in the mailbox

    `threads_total: list[float]`
    :   Total number of threads currently in the mailbox

<a id="ProfileKeywordCondition"></a>

`ProfileKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gmail.types.ProfileStringFilter`
    :   The type of the None singleton.

<a id="ProfileLikeCondition"></a>

`ProfileLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gmail.types.ProfileStringFilter`
    :   The type of the None singleton.

<a id="ProfileLtCondition"></a>

`ProfileLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gmail.types.ProfileSearchFilter`
    :   The type of the None singleton.

<a id="ProfileLteCondition"></a>

`ProfileLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gmail.types.ProfileSearchFilter`
    :   The type of the None singleton.

<a id="ProfileNeqCondition"></a>

`ProfileNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gmail.types.ProfileSearchFilter`
    :   The type of the None singleton.

<a id="ProfileNotCondition"></a>

`ProfileNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.gmail.types.ProfileEqCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileNeqCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileGtCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileGteCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileLtCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileLteCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileInCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileLikeCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileContainsCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileNotCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileAndCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileOrCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileAnyCondition`
    :   The type of the None singleton.

<a id="ProfileOrCondition"></a>

`ProfileOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.gmail.types.ProfileEqCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileNeqCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileGtCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileGteCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileLtCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileLteCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileInCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileLikeCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileContainsCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileNotCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileAndCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileOrCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileAnyCondition]`
    :   The type of the None singleton.

<a id="ProfileSearchFilter"></a>

`ProfileSearchFilter(*args, **kwargs)`
:   Available fields for filtering profile search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email_address: str | None`
    :   Email address of the authenticated Gmail account

    `history_id: str | None`
    :   Mailbox history record identifier used for incremental sync

    `messages_total: float | None`
    :   Total number of messages currently in the mailbox

    `threads_total: float | None`
    :   Total number of threads currently in the mailbox

<a id="ProfileSearchQuery"></a>

`ProfileSearchQuery(*args, **kwargs)`
:   Search query for profile entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gmail.types.ProfileEqCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileNeqCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileGtCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileGteCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileLtCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileLteCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileInCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileLikeCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileContainsCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileNotCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileAndCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileOrCondition | airbyte_agent_sdk.connectors.gmail.types.ProfileAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gmail.types.ProfileSortFilter]`
    :   The type of the None singleton.

<a id="ProfileSortFilter"></a>

`ProfileSortFilter(*args, **kwargs)`
:   Available fields for sorting profile search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email_address: Literal['asc', 'desc']`
    :   Email address of the authenticated Gmail account

    `history_id: Literal['asc', 'desc']`
    :   Mailbox history record identifier used for incremental sync

    `messages_total: Literal['asc', 'desc']`
    :   Total number of messages currently in the mailbox

    `threads_total: Literal['asc', 'desc']`
    :   Total number of threads currently in the mailbox

<a id="ProfileStringFilter"></a>

`ProfileStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email_address: str`
    :   Email address of the authenticated Gmail account

    `history_id: str`
    :   Mailbox history record identifier used for incremental sync

    `messages_total: str`
    :   Total number of messages currently in the mailbox

    `threads_total: str`
    :   Total number of threads currently in the mailbox

<a id="ThreadsAndCondition"></a>

`ThreadsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.gmail.types.ThreadsEqCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsNeqCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsGtCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsGteCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsLtCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsLteCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsInCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsLikeCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsContainsCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsNotCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsAndCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsOrCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsAnyCondition]`
    :   The type of the None singleton.

<a id="ThreadsAnyCondition"></a>

`ThreadsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.gmail.types.ThreadsAnyValueFilter`
    :   The type of the None singleton.

<a id="ThreadsAnyValueFilter"></a>

`ThreadsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `history_id: Any`
    :   Mailbox history record identifier for the thread

    `id: Any`
    :   Unique identifier for the thread

    `snippet: Any`
    :   Short snippet of the thread's most recent message

<a id="ThreadsContainsCondition"></a>

`ThreadsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gmail.types.ThreadsAnyValueFilter`
    :   The type of the None singleton.

<a id="ThreadsEqCondition"></a>

`ThreadsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gmail.types.ThreadsSearchFilter`
    :   The type of the None singleton.

<a id="ThreadsFuzzyCondition"></a>

`ThreadsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gmail.types.ThreadsStringFilter`
    :   The type of the None singleton.

<a id="ThreadsGetParams"></a>

`ThreadsGetParams(*args, **kwargs)`
:   Parameters for threads.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `format: str`
    :   The type of the None singleton.

    `metadata_headers: str`
    :   The type of the None singleton.

    `thread_id: str`
    :   The type of the None singleton.

<a id="ThreadsGtCondition"></a>

`ThreadsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gmail.types.ThreadsSearchFilter`
    :   The type of the None singleton.

<a id="ThreadsGteCondition"></a>

`ThreadsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gmail.types.ThreadsSearchFilter`
    :   The type of the None singleton.

<a id="ThreadsInCondition"></a>

`ThreadsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.gmail.types.ThreadsInFilter`
    :   The type of the None singleton.

<a id="ThreadsInFilter"></a>

`ThreadsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `history_id: list[str]`
    :   Mailbox history record identifier for the thread

    `id: list[str]`
    :   Unique identifier for the thread

    `snippet: list[str]`
    :   Short snippet of the thread's most recent message

<a id="ThreadsKeywordCondition"></a>

`ThreadsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gmail.types.ThreadsStringFilter`
    :   The type of the None singleton.

<a id="ThreadsLikeCondition"></a>

`ThreadsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gmail.types.ThreadsStringFilter`
    :   The type of the None singleton.

<a id="ThreadsListParams"></a>

`ThreadsListParams(*args, **kwargs)`
:   Parameters for threads.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include_spam_trash: bool`
    :   The type of the None singleton.

    `label_ids: str`
    :   The type of the None singleton.

    `max_results: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

<a id="ThreadsLtCondition"></a>

`ThreadsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gmail.types.ThreadsSearchFilter`
    :   The type of the None singleton.

<a id="ThreadsLteCondition"></a>

`ThreadsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gmail.types.ThreadsSearchFilter`
    :   The type of the None singleton.

<a id="ThreadsNeqCondition"></a>

`ThreadsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gmail.types.ThreadsSearchFilter`
    :   The type of the None singleton.

<a id="ThreadsNotCondition"></a>

`ThreadsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.gmail.types.ThreadsEqCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsNeqCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsGtCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsGteCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsLtCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsLteCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsInCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsLikeCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsContainsCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsNotCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsAndCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsOrCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsAnyCondition`
    :   The type of the None singleton.

<a id="ThreadsOrCondition"></a>

`ThreadsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.gmail.types.ThreadsEqCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsNeqCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsGtCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsGteCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsLtCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsLteCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsInCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsLikeCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsContainsCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsNotCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsAndCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsOrCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsAnyCondition]`
    :   The type of the None singleton.

<a id="ThreadsSearchFilter"></a>

`ThreadsSearchFilter(*args, **kwargs)`
:   Available fields for filtering threads search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `history_id: str | None`
    :   Mailbox history record identifier for the thread

    `id: str`
    :   Unique identifier for the thread

    `snippet: str | None`
    :   Short snippet of the thread's most recent message

<a id="ThreadsSearchQuery"></a>

`ThreadsSearchQuery(*args, **kwargs)`
:   Search query for threads entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gmail.types.ThreadsEqCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsNeqCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsGtCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsGteCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsLtCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsLteCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsInCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsLikeCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsFuzzyCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsKeywordCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsContainsCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsNotCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsAndCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsOrCondition | airbyte_agent_sdk.connectors.gmail.types.ThreadsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gmail.types.ThreadsSortFilter]`
    :   The type of the None singleton.

<a id="ThreadsSortFilter"></a>

`ThreadsSortFilter(*args, **kwargs)`
:   Available fields for sorting threads search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `history_id: Literal['asc', 'desc']`
    :   Mailbox history record identifier for the thread

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the thread

    `snippet: Literal['asc', 'desc']`
    :   Short snippet of the thread's most recent message

<a id="ThreadsStringFilter"></a>

`ThreadsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `history_id: str`
    :   Mailbox history record identifier for the thread

    `id: str`
    :   Unique identifier for the thread

    `snippet: str`
    :   Short snippet of the thread's most recent message