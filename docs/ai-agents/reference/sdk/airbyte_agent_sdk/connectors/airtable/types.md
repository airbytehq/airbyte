---
id: airbyte_agent_sdk-connectors-airtable-types
title: airbyte_agent_sdk.connectors.airtable.types
---

Module airbyte_agent_sdk.connectors.airtable.types
==================================================
Type definitions for airtable connector.

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

<a id="BasesAndCondition"></a>

`BasesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.airtable.types.BasesEqCondition | airbyte_agent_sdk.connectors.airtable.types.BasesNeqCondition | airbyte_agent_sdk.connectors.airtable.types.BasesGtCondition | airbyte_agent_sdk.connectors.airtable.types.BasesGteCondition | airbyte_agent_sdk.connectors.airtable.types.BasesLtCondition | airbyte_agent_sdk.connectors.airtable.types.BasesLteCondition | airbyte_agent_sdk.connectors.airtable.types.BasesInCondition | airbyte_agent_sdk.connectors.airtable.types.BasesLikeCondition | airbyte_agent_sdk.connectors.airtable.types.BasesFuzzyCondition | airbyte_agent_sdk.connectors.airtable.types.BasesKeywordCondition | airbyte_agent_sdk.connectors.airtable.types.BasesContainsCondition | airbyte_agent_sdk.connectors.airtable.types.BasesNotCondition | airbyte_agent_sdk.connectors.airtable.types.BasesAndCondition | airbyte_agent_sdk.connectors.airtable.types.BasesOrCondition | airbyte_agent_sdk.connectors.airtable.types.BasesAnyCondition]`
    :   The type of the None singleton.

<a id="BasesAnyCondition"></a>

`BasesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.airtable.types.BasesAnyValueFilter`
    :   The type of the None singleton.

<a id="BasesAnyValueFilter"></a>

`BasesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier for the base

    `name: Any`
    :   Name of the base

    `permission_level: Any`
    :   Permission level for the base

<a id="BasesContainsCondition"></a>

`BasesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.airtable.types.BasesAnyValueFilter`
    :   The type of the None singleton.

<a id="BasesEqCondition"></a>

`BasesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.airtable.types.BasesSearchFilter`
    :   The type of the None singleton.

<a id="BasesFuzzyCondition"></a>

`BasesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.airtable.types.BasesStringFilter`
    :   The type of the None singleton.

<a id="BasesGtCondition"></a>

`BasesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.airtable.types.BasesSearchFilter`
    :   The type of the None singleton.

<a id="BasesGteCondition"></a>

`BasesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.airtable.types.BasesSearchFilter`
    :   The type of the None singleton.

<a id="BasesInCondition"></a>

`BasesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.airtable.types.BasesInFilter`
    :   The type of the None singleton.

<a id="BasesInFilter"></a>

`BasesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[str]`
    :   Unique identifier for the base

    `name: list[str]`
    :   Name of the base

    `permission_level: list[str]`
    :   Permission level for the base

<a id="BasesKeywordCondition"></a>

`BasesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.airtable.types.BasesStringFilter`
    :   The type of the None singleton.

<a id="BasesLikeCondition"></a>

`BasesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.airtable.types.BasesStringFilter`
    :   The type of the None singleton.

<a id="BasesListParams"></a>

`BasesListParams(*args, **kwargs)`
:   Parameters for bases.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `offset: str`
    :   The type of the None singleton.

<a id="BasesLtCondition"></a>

`BasesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.airtable.types.BasesSearchFilter`
    :   The type of the None singleton.

<a id="BasesLteCondition"></a>

`BasesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.airtable.types.BasesSearchFilter`
    :   The type of the None singleton.

<a id="BasesNeqCondition"></a>

`BasesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.airtable.types.BasesSearchFilter`
    :   The type of the None singleton.

<a id="BasesNotCondition"></a>

`BasesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.airtable.types.BasesEqCondition | airbyte_agent_sdk.connectors.airtable.types.BasesNeqCondition | airbyte_agent_sdk.connectors.airtable.types.BasesGtCondition | airbyte_agent_sdk.connectors.airtable.types.BasesGteCondition | airbyte_agent_sdk.connectors.airtable.types.BasesLtCondition | airbyte_agent_sdk.connectors.airtable.types.BasesLteCondition | airbyte_agent_sdk.connectors.airtable.types.BasesInCondition | airbyte_agent_sdk.connectors.airtable.types.BasesLikeCondition | airbyte_agent_sdk.connectors.airtable.types.BasesFuzzyCondition | airbyte_agent_sdk.connectors.airtable.types.BasesKeywordCondition | airbyte_agent_sdk.connectors.airtable.types.BasesContainsCondition | airbyte_agent_sdk.connectors.airtable.types.BasesNotCondition | airbyte_agent_sdk.connectors.airtable.types.BasesAndCondition | airbyte_agent_sdk.connectors.airtable.types.BasesOrCondition | airbyte_agent_sdk.connectors.airtable.types.BasesAnyCondition`
    :   The type of the None singleton.

<a id="BasesOrCondition"></a>

`BasesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.airtable.types.BasesEqCondition | airbyte_agent_sdk.connectors.airtable.types.BasesNeqCondition | airbyte_agent_sdk.connectors.airtable.types.BasesGtCondition | airbyte_agent_sdk.connectors.airtable.types.BasesGteCondition | airbyte_agent_sdk.connectors.airtable.types.BasesLtCondition | airbyte_agent_sdk.connectors.airtable.types.BasesLteCondition | airbyte_agent_sdk.connectors.airtable.types.BasesInCondition | airbyte_agent_sdk.connectors.airtable.types.BasesLikeCondition | airbyte_agent_sdk.connectors.airtable.types.BasesFuzzyCondition | airbyte_agent_sdk.connectors.airtable.types.BasesKeywordCondition | airbyte_agent_sdk.connectors.airtable.types.BasesContainsCondition | airbyte_agent_sdk.connectors.airtable.types.BasesNotCondition | airbyte_agent_sdk.connectors.airtable.types.BasesAndCondition | airbyte_agent_sdk.connectors.airtable.types.BasesOrCondition | airbyte_agent_sdk.connectors.airtable.types.BasesAnyCondition]`
    :   The type of the None singleton.

<a id="BasesSearchFilter"></a>

`BasesSearchFilter(*args, **kwargs)`
:   Available fields for filtering bases search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str | None`
    :   Unique identifier for the base

    `name: str | None`
    :   Name of the base

    `permission_level: str | None`
    :   Permission level for the base

<a id="BasesSearchQuery"></a>

`BasesSearchQuery(*args, **kwargs)`
:   Search query for bases entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.airtable.types.BasesEqCondition | airbyte_agent_sdk.connectors.airtable.types.BasesNeqCondition | airbyte_agent_sdk.connectors.airtable.types.BasesGtCondition | airbyte_agent_sdk.connectors.airtable.types.BasesGteCondition | airbyte_agent_sdk.connectors.airtable.types.BasesLtCondition | airbyte_agent_sdk.connectors.airtable.types.BasesLteCondition | airbyte_agent_sdk.connectors.airtable.types.BasesInCondition | airbyte_agent_sdk.connectors.airtable.types.BasesLikeCondition | airbyte_agent_sdk.connectors.airtable.types.BasesFuzzyCondition | airbyte_agent_sdk.connectors.airtable.types.BasesKeywordCondition | airbyte_agent_sdk.connectors.airtable.types.BasesContainsCondition | airbyte_agent_sdk.connectors.airtable.types.BasesNotCondition | airbyte_agent_sdk.connectors.airtable.types.BasesAndCondition | airbyte_agent_sdk.connectors.airtable.types.BasesOrCondition | airbyte_agent_sdk.connectors.airtable.types.BasesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.airtable.types.BasesSortFilter]`
    :   The type of the None singleton.

<a id="BasesSortFilter"></a>

`BasesSortFilter(*args, **kwargs)`
:   Available fields for sorting bases search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the base

    `name: Literal['asc', 'desc']`
    :   Name of the base

    `permission_level: Literal['asc', 'desc']`
    :   Permission level for the base

<a id="BasesStringFilter"></a>

`BasesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the base

    `name: str`
    :   Name of the base

    `permission_level: str`
    :   Permission level for the base

<a id="RecordsGetParams"></a>

`RecordsGetParams(*args, **kwargs)`
:   Parameters for records.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_id: str`
    :   The type of the None singleton.

    `record_id: str`
    :   The type of the None singleton.

    `table_id_or_name: str`
    :   The type of the None singleton.

<a id="RecordsListParams"></a>

`RecordsListParams(*args, **kwargs)`
:   Parameters for records.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_id: str`
    :   The type of the None singleton.

    `filter_by_formula: str`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

    `table_id_or_name: str`
    :   The type of the None singleton.

    `view: str`
    :   The type of the None singleton.

<a id="TablesAndCondition"></a>

`TablesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.airtable.types.TablesEqCondition | airbyte_agent_sdk.connectors.airtable.types.TablesNeqCondition | airbyte_agent_sdk.connectors.airtable.types.TablesGtCondition | airbyte_agent_sdk.connectors.airtable.types.TablesGteCondition | airbyte_agent_sdk.connectors.airtable.types.TablesLtCondition | airbyte_agent_sdk.connectors.airtable.types.TablesLteCondition | airbyte_agent_sdk.connectors.airtable.types.TablesInCondition | airbyte_agent_sdk.connectors.airtable.types.TablesLikeCondition | airbyte_agent_sdk.connectors.airtable.types.TablesFuzzyCondition | airbyte_agent_sdk.connectors.airtable.types.TablesKeywordCondition | airbyte_agent_sdk.connectors.airtable.types.TablesContainsCondition | airbyte_agent_sdk.connectors.airtable.types.TablesNotCondition | airbyte_agent_sdk.connectors.airtable.types.TablesAndCondition | airbyte_agent_sdk.connectors.airtable.types.TablesOrCondition | airbyte_agent_sdk.connectors.airtable.types.TablesAnyCondition]`
    :   The type of the None singleton.

<a id="TablesAnyCondition"></a>

`TablesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.airtable.types.TablesAnyValueFilter`
    :   The type of the None singleton.

<a id="TablesAnyValueFilter"></a>

`TablesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: Any`
    :   List of fields in the table

    `id: Any`
    :   Unique identifier for the table

    `name: Any`
    :   Name of the table

    `primary_field_id: Any`
    :   ID of the primary field

    `views: Any`
    :   List of views in the table

<a id="TablesContainsCondition"></a>

`TablesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.airtable.types.TablesAnyValueFilter`
    :   The type of the None singleton.

<a id="TablesEqCondition"></a>

`TablesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.airtable.types.TablesSearchFilter`
    :   The type of the None singleton.

<a id="TablesFuzzyCondition"></a>

`TablesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.airtable.types.TablesStringFilter`
    :   The type of the None singleton.

<a id="TablesGtCondition"></a>

`TablesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.airtable.types.TablesSearchFilter`
    :   The type of the None singleton.

<a id="TablesGteCondition"></a>

`TablesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.airtable.types.TablesSearchFilter`
    :   The type of the None singleton.

<a id="TablesInCondition"></a>

`TablesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.airtable.types.TablesInFilter`
    :   The type of the None singleton.

<a id="TablesInFilter"></a>

`TablesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[list[typing.Any]]`
    :   List of fields in the table

    `id: list[str]`
    :   Unique identifier for the table

    `name: list[str]`
    :   Name of the table

    `primary_field_id: list[str]`
    :   ID of the primary field

    `views: list[list[typing.Any]]`
    :   List of views in the table

<a id="TablesKeywordCondition"></a>

`TablesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.airtable.types.TablesStringFilter`
    :   The type of the None singleton.

<a id="TablesLikeCondition"></a>

`TablesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.airtable.types.TablesStringFilter`
    :   The type of the None singleton.

<a id="TablesListParams"></a>

`TablesListParams(*args, **kwargs)`
:   Parameters for tables.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_id: str`
    :   The type of the None singleton.

<a id="TablesLtCondition"></a>

`TablesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.airtable.types.TablesSearchFilter`
    :   The type of the None singleton.

<a id="TablesLteCondition"></a>

`TablesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.airtable.types.TablesSearchFilter`
    :   The type of the None singleton.

<a id="TablesNeqCondition"></a>

`TablesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.airtable.types.TablesSearchFilter`
    :   The type of the None singleton.

<a id="TablesNotCondition"></a>

`TablesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.airtable.types.TablesEqCondition | airbyte_agent_sdk.connectors.airtable.types.TablesNeqCondition | airbyte_agent_sdk.connectors.airtable.types.TablesGtCondition | airbyte_agent_sdk.connectors.airtable.types.TablesGteCondition | airbyte_agent_sdk.connectors.airtable.types.TablesLtCondition | airbyte_agent_sdk.connectors.airtable.types.TablesLteCondition | airbyte_agent_sdk.connectors.airtable.types.TablesInCondition | airbyte_agent_sdk.connectors.airtable.types.TablesLikeCondition | airbyte_agent_sdk.connectors.airtable.types.TablesFuzzyCondition | airbyte_agent_sdk.connectors.airtable.types.TablesKeywordCondition | airbyte_agent_sdk.connectors.airtable.types.TablesContainsCondition | airbyte_agent_sdk.connectors.airtable.types.TablesNotCondition | airbyte_agent_sdk.connectors.airtable.types.TablesAndCondition | airbyte_agent_sdk.connectors.airtable.types.TablesOrCondition | airbyte_agent_sdk.connectors.airtable.types.TablesAnyCondition`
    :   The type of the None singleton.

<a id="TablesOrCondition"></a>

`TablesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.airtable.types.TablesEqCondition | airbyte_agent_sdk.connectors.airtable.types.TablesNeqCondition | airbyte_agent_sdk.connectors.airtable.types.TablesGtCondition | airbyte_agent_sdk.connectors.airtable.types.TablesGteCondition | airbyte_agent_sdk.connectors.airtable.types.TablesLtCondition | airbyte_agent_sdk.connectors.airtable.types.TablesLteCondition | airbyte_agent_sdk.connectors.airtable.types.TablesInCondition | airbyte_agent_sdk.connectors.airtable.types.TablesLikeCondition | airbyte_agent_sdk.connectors.airtable.types.TablesFuzzyCondition | airbyte_agent_sdk.connectors.airtable.types.TablesKeywordCondition | airbyte_agent_sdk.connectors.airtable.types.TablesContainsCondition | airbyte_agent_sdk.connectors.airtable.types.TablesNotCondition | airbyte_agent_sdk.connectors.airtable.types.TablesAndCondition | airbyte_agent_sdk.connectors.airtable.types.TablesOrCondition | airbyte_agent_sdk.connectors.airtable.types.TablesAnyCondition]`
    :   The type of the None singleton.

<a id="TablesSearchFilter"></a>

`TablesSearchFilter(*args, **kwargs)`
:   Available fields for filtering tables search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[typing.Any] | None`
    :   List of fields in the table

    `id: str | None`
    :   Unique identifier for the table

    `name: str | None`
    :   Name of the table

    `primary_field_id: str | None`
    :   ID of the primary field

    `views: list[typing.Any] | None`
    :   List of views in the table

<a id="TablesSearchQuery"></a>

`TablesSearchQuery(*args, **kwargs)`
:   Search query for tables entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.airtable.types.TablesEqCondition | airbyte_agent_sdk.connectors.airtable.types.TablesNeqCondition | airbyte_agent_sdk.connectors.airtable.types.TablesGtCondition | airbyte_agent_sdk.connectors.airtable.types.TablesGteCondition | airbyte_agent_sdk.connectors.airtable.types.TablesLtCondition | airbyte_agent_sdk.connectors.airtable.types.TablesLteCondition | airbyte_agent_sdk.connectors.airtable.types.TablesInCondition | airbyte_agent_sdk.connectors.airtable.types.TablesLikeCondition | airbyte_agent_sdk.connectors.airtable.types.TablesFuzzyCondition | airbyte_agent_sdk.connectors.airtable.types.TablesKeywordCondition | airbyte_agent_sdk.connectors.airtable.types.TablesContainsCondition | airbyte_agent_sdk.connectors.airtable.types.TablesNotCondition | airbyte_agent_sdk.connectors.airtable.types.TablesAndCondition | airbyte_agent_sdk.connectors.airtable.types.TablesOrCondition | airbyte_agent_sdk.connectors.airtable.types.TablesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.airtable.types.TablesSortFilter]`
    :   The type of the None singleton.

<a id="TablesSortFilter"></a>

`TablesSortFilter(*args, **kwargs)`
:   Available fields for sorting tables search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: Literal['asc', 'desc']`
    :   List of fields in the table

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the table

    `name: Literal['asc', 'desc']`
    :   Name of the table

    `primary_field_id: Literal['asc', 'desc']`
    :   ID of the primary field

    `views: Literal['asc', 'desc']`
    :   List of views in the table

<a id="TablesStringFilter"></a>

`TablesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   List of fields in the table

    `id: str`
    :   Unique identifier for the table

    `name: str`
    :   Name of the table

    `primary_field_id: str`
    :   ID of the primary field

    `views: str`
    :   List of views in the table