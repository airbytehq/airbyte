---
id: airbyte_agent_sdk-connectors-hubspot-types
title: airbyte_agent_sdk.connectors.hubspot.types
---

Module airbyte_agent_sdk.connectors.hubspot.types
=================================================
Type definitions for hubspot connector.

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

`CompaniesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.hubspot.types.CompaniesEqCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesGtCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesGteCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLtCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLteCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesInCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesNotCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesAndCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesOrCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesAnyCondition]`
    :   The type of the None singleton.

`CompaniesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.hubspot.types.CompaniesAnyValueFilter`
    :   The type of the None singleton.

`CompaniesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Indicates whether the company has been deleted and moved to the recycling bin

    `contacts: Any`
    :   Associated contact records linked to this company

    `created_at: Any`
    :   Timestamp when the company record was created

    `id: Any`
    :   Unique identifier for the company record

    `properties: Any`
    :   Object containing all property values for the company

    `updated_at: Any`
    :   Timestamp when the company record was last modified

`CompaniesApiSearchParams(*args, **kwargs)`
:   Parameters for companies.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `filter_groups: list[airbyte_agent_sdk.connectors.hubspot.types.CompaniesApiSearchParamsFiltergroupsItem]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `properties: list[str]`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

    `sorts: list[airbyte_agent_sdk.connectors.hubspot.types.CompaniesApiSearchParamsSortsItem]`
    :   The type of the None singleton.

`CompaniesApiSearchParamsFiltergroupsItem(*args, **kwargs)`
:   Nested schema for CompaniesApiSearchParams.filterGroups_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filters: list[airbyte_agent_sdk.connectors.hubspot.types.CompaniesApiSearchParamsFiltergroupsItemFiltersItem]`
    :   The type of the None singleton.

`CompaniesApiSearchParamsFiltergroupsItemFiltersItem(*args, **kwargs)`
:   Nested schema for CompaniesApiSearchParamsFiltergroupsItem.filters_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `operator: str`
    :   The type of the None singleton.

    `propertyName: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

    ### Methods

    `values(self, /) ‑> list[str]`
    :   Return an object providing a view on the dict's values.

`CompaniesApiSearchParamsSortsItem(*args, **kwargs)`
:   Nested schema for CompaniesApiSearchParams.sorts_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `direction: str`
    :   The type of the None singleton.

    `propertyName: str`
    :   The type of the None singleton.

`CompaniesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.hubspot.types.CompaniesAnyValueFilter`
    :   The type of the None singleton.

`CompaniesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.hubspot.types.CompaniesSearchFilter`
    :   The type of the None singleton.

`CompaniesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.hubspot.types.CompaniesStringFilter`
    :   The type of the None singleton.

`CompaniesGetParams(*args, **kwargs)`
:   Parameters for companies.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `associations: str`
    :   The type of the None singleton.

    `company_id: str`
    :   The type of the None singleton.

    `id_property: str`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `properties_with_history: str`
    :   The type of the None singleton.

`CompaniesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.hubspot.types.CompaniesSearchFilter`
    :   The type of the None singleton.

`CompaniesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.hubspot.types.CompaniesSearchFilter`
    :   The type of the None singleton.

`CompaniesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.hubspot.types.CompaniesInFilter`
    :   The type of the None singleton.

`CompaniesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Indicates whether the company has been deleted and moved to the recycling bin

    `contacts: list[list[typing.Any]]`
    :   Associated contact records linked to this company

    `created_at: list[str]`
    :   Timestamp when the company record was created

    `id: list[str]`
    :   Unique identifier for the company record

    `properties: list[dict[str, typing.Any]]`
    :   Object containing all property values for the company

    `updated_at: list[str]`
    :   Timestamp when the company record was last modified

`CompaniesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.hubspot.types.CompaniesStringFilter`
    :   The type of the None singleton.

`CompaniesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.hubspot.types.CompaniesStringFilter`
    :   The type of the None singleton.

`CompaniesListParams(*args, **kwargs)`
:   Parameters for companies.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `archived: bool`
    :   The type of the None singleton.

    `associations: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `properties_with_history: str`
    :   The type of the None singleton.

`CompaniesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.hubspot.types.CompaniesSearchFilter`
    :   The type of the None singleton.

`CompaniesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.hubspot.types.CompaniesSearchFilter`
    :   The type of the None singleton.

`CompaniesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.hubspot.types.CompaniesSearchFilter`
    :   The type of the None singleton.

`CompaniesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.hubspot.types.CompaniesEqCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesGtCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesGteCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLtCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLteCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesInCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesNotCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesAndCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesOrCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesAnyCondition`
    :   The type of the None singleton.

`CompaniesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.hubspot.types.CompaniesEqCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesGtCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesGteCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLtCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLteCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesInCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesNotCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesAndCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesOrCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesAnyCondition]`
    :   The type of the None singleton.

`CompaniesSearchFilter(*args, **kwargs)`
:   Available fields for filtering companies search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the company has been deleted and moved to the recycling bin

    `contacts: list[typing.Any] | None`
    :   Associated contact records linked to this company

    `created_at: str | None`
    :   Timestamp when the company record was created

    `id: str | None`
    :   Unique identifier for the company record

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the company

    `updated_at: str | None`
    :   Timestamp when the company record was last modified

`CompaniesSearchQuery(*args, **kwargs)`
:   Search query for companies entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.hubspot.types.CompaniesEqCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesGtCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesGteCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLtCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLteCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesInCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesNotCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesAndCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesOrCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.hubspot.types.CompaniesSortFilter]`
    :   The type of the None singleton.

`CompaniesSortFilter(*args, **kwargs)`
:   Available fields for sorting companies search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Indicates whether the company has been deleted and moved to the recycling bin

    `contacts: Literal['asc', 'desc']`
    :   Associated contact records linked to this company

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the company record was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the company record

    `properties: Literal['asc', 'desc']`
    :   Object containing all property values for the company

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the company record was last modified

`CompaniesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Indicates whether the company has been deleted and moved to the recycling bin

    `contacts: str`
    :   Associated contact records linked to this company

    `created_at: str`
    :   Timestamp when the company record was created

    `id: str`
    :   Unique identifier for the company record

    `properties: str`
    :   Object containing all property values for the company

    `updated_at: str`
    :   Timestamp when the company record was last modified

`ContactsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.hubspot.types.ContactsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsInCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsAnyCondition]`
    :   The type of the None singleton.

`ContactsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.hubspot.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

`ContactsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Boolean flag indicating whether the contact has been archived or deleted.

    `companies: Any`
    :   Associated company records linked to this contact.

    `created_at: Any`
    :   Timestamp indicating when the contact was first created in the system.

    `id: Any`
    :   Unique identifier for the contact record.

    `properties: Any`
    :   Key-value object storing all contact properties and their values.

    `updated_at: Any`
    :   Timestamp indicating when the contact record was last modified.

`ContactsApiSearchParams(*args, **kwargs)`
:   Parameters for contacts.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `filter_groups: list[airbyte_agent_sdk.connectors.hubspot.types.ContactsApiSearchParamsFiltergroupsItem]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `properties: list[str]`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

    `sorts: list[airbyte_agent_sdk.connectors.hubspot.types.ContactsApiSearchParamsSortsItem]`
    :   The type of the None singleton.

`ContactsApiSearchParamsFiltergroupsItem(*args, **kwargs)`
:   Nested schema for ContactsApiSearchParams.filterGroups_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filters: list[airbyte_agent_sdk.connectors.hubspot.types.ContactsApiSearchParamsFiltergroupsItemFiltersItem]`
    :   The type of the None singleton.

`ContactsApiSearchParamsFiltergroupsItemFiltersItem(*args, **kwargs)`
:   Nested schema for ContactsApiSearchParamsFiltergroupsItem.filters_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `operator: str`
    :   The type of the None singleton.

    `propertyName: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

    ### Methods

    `values(self, /) ‑> list[str]`
    :   Return an object providing a view on the dict's values.

`ContactsApiSearchParamsSortsItem(*args, **kwargs)`
:   Nested schema for ContactsApiSearchParams.sorts_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `direction: str`
    :   The type of the None singleton.

    `propertyName: str`
    :   The type of the None singleton.

`ContactsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.hubspot.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

`ContactsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.hubspot.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.hubspot.types.ContactsStringFilter`
    :   The type of the None singleton.

`ContactsGetParams(*args, **kwargs)`
:   Parameters for contacts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `associations: str`
    :   The type of the None singleton.

    `contact_id: str`
    :   The type of the None singleton.

    `id_property: str`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `properties_with_history: str`
    :   The type of the None singleton.

`ContactsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.hubspot.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.hubspot.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.hubspot.types.ContactsInFilter`
    :   The type of the None singleton.

`ContactsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Boolean flag indicating whether the contact has been archived or deleted.

    `companies: list[list[typing.Any]]`
    :   Associated company records linked to this contact.

    `created_at: list[str]`
    :   Timestamp indicating when the contact was first created in the system.

    `id: list[str]`
    :   Unique identifier for the contact record.

    `properties: list[dict[str, typing.Any]]`
    :   Key-value object storing all contact properties and their values.

    `updated_at: list[str]`
    :   Timestamp indicating when the contact record was last modified.

`ContactsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.hubspot.types.ContactsStringFilter`
    :   The type of the None singleton.

`ContactsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.hubspot.types.ContactsStringFilter`
    :   The type of the None singleton.

`ContactsListParams(*args, **kwargs)`
:   Parameters for contacts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `archived: bool`
    :   The type of the None singleton.

    `associations: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `properties_with_history: str`
    :   The type of the None singleton.

`ContactsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.hubspot.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.hubspot.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.hubspot.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.hubspot.types.ContactsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsInCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsAnyCondition`
    :   The type of the None singleton.

`ContactsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.hubspot.types.ContactsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsInCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsAnyCondition]`
    :   The type of the None singleton.

`ContactsSearchFilter(*args, **kwargs)`
:   Available fields for filtering contacts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool | None`
    :   Boolean flag indicating whether the contact has been archived or deleted.

    `companies: list[typing.Any] | None`
    :   Associated company records linked to this contact.

    `created_at: str | None`
    :   Timestamp indicating when the contact was first created in the system.

    `id: str | None`
    :   Unique identifier for the contact record.

    `properties: dict[str, typing.Any]`
    :   Key-value object storing all contact properties and their values.

    `updated_at: str | None`
    :   Timestamp indicating when the contact record was last modified.

`ContactsSearchQuery(*args, **kwargs)`
:   Search query for contacts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.hubspot.types.ContactsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsInCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.hubspot.types.ContactsSortFilter]`
    :   The type of the None singleton.

`ContactsSortFilter(*args, **kwargs)`
:   Available fields for sorting contacts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Boolean flag indicating whether the contact has been archived or deleted.

    `companies: Literal['asc', 'desc']`
    :   Associated company records linked to this contact.

    `created_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the contact was first created in the system.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the contact record.

    `properties: Literal['asc', 'desc']`
    :   Key-value object storing all contact properties and their values.

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the contact record was last modified.

`ContactsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Boolean flag indicating whether the contact has been archived or deleted.

    `companies: str`
    :   Associated company records linked to this contact.

    `created_at: str`
    :   Timestamp indicating when the contact was first created in the system.

    `id: str`
    :   Unique identifier for the contact record.

    `properties: str`
    :   Key-value object storing all contact properties and their values.

    `updated_at: str`
    :   Timestamp indicating when the contact record was last modified.

`DealsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.hubspot.types.DealsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsInCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsAnyCondition]`
    :   The type of the None singleton.

`DealsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.hubspot.types.DealsAnyValueFilter`
    :   The type of the None singleton.

`DealsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Indicates whether the deal has been deleted and moved to the recycling bin

    `companies: Any`
    :   Collection of company records associated with the deal

    `contacts: Any`
    :   Collection of contact records associated with the deal

    `created_at: Any`
    :   Timestamp when the deal record was originally created

    `id: Any`
    :   Unique identifier for the deal record

    `line_items: Any`
    :   Collection of product line items associated with the deal

    `properties: Any`
    :   Key-value object containing all deal properties and custom fields

    `updated_at: Any`
    :   Timestamp when the deal record was last modified

`DealsApiSearchParams(*args, **kwargs)`
:   Parameters for deals.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `filter_groups: list[airbyte_agent_sdk.connectors.hubspot.types.DealsApiSearchParamsFiltergroupsItem]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `properties: list[str]`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

    `sorts: list[airbyte_agent_sdk.connectors.hubspot.types.DealsApiSearchParamsSortsItem]`
    :   The type of the None singleton.

`DealsApiSearchParamsFiltergroupsItem(*args, **kwargs)`
:   Nested schema for DealsApiSearchParams.filterGroups_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filters: list[airbyte_agent_sdk.connectors.hubspot.types.DealsApiSearchParamsFiltergroupsItemFiltersItem]`
    :   The type of the None singleton.

`DealsApiSearchParamsFiltergroupsItemFiltersItem(*args, **kwargs)`
:   Nested schema for DealsApiSearchParamsFiltergroupsItem.filters_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `operator: str`
    :   The type of the None singleton.

    `propertyName: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

    ### Methods

    `values(self, /) ‑> list[str]`
    :   Return an object providing a view on the dict's values.

`DealsApiSearchParamsSortsItem(*args, **kwargs)`
:   Nested schema for DealsApiSearchParams.sorts_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `direction: str`
    :   The type of the None singleton.

    `propertyName: str`
    :   The type of the None singleton.

`DealsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.hubspot.types.DealsAnyValueFilter`
    :   The type of the None singleton.

`DealsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.hubspot.types.DealsSearchFilter`
    :   The type of the None singleton.

`DealsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.hubspot.types.DealsStringFilter`
    :   The type of the None singleton.

`DealsGetParams(*args, **kwargs)`
:   Parameters for deals.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `associations: str`
    :   The type of the None singleton.

    `deal_id: str`
    :   The type of the None singleton.

    `id_property: str`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `properties_with_history: str`
    :   The type of the None singleton.

`DealsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.hubspot.types.DealsSearchFilter`
    :   The type of the None singleton.

`DealsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.hubspot.types.DealsSearchFilter`
    :   The type of the None singleton.

`DealsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.hubspot.types.DealsInFilter`
    :   The type of the None singleton.

`DealsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Indicates whether the deal has been deleted and moved to the recycling bin

    `companies: list[list[typing.Any]]`
    :   Collection of company records associated with the deal

    `contacts: list[list[typing.Any]]`
    :   Collection of contact records associated with the deal

    `created_at: list[str]`
    :   Timestamp when the deal record was originally created

    `id: list[str]`
    :   Unique identifier for the deal record

    `line_items: list[list[typing.Any]]`
    :   Collection of product line items associated with the deal

    `properties: list[dict[str, typing.Any]]`
    :   Key-value object containing all deal properties and custom fields

    `updated_at: list[str]`
    :   Timestamp when the deal record was last modified

`DealsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.hubspot.types.DealsStringFilter`
    :   The type of the None singleton.

`DealsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.hubspot.types.DealsStringFilter`
    :   The type of the None singleton.

`DealsListParams(*args, **kwargs)`
:   Parameters for deals.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `archived: bool`
    :   The type of the None singleton.

    `associations: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `properties_with_history: str`
    :   The type of the None singleton.

`DealsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.hubspot.types.DealsSearchFilter`
    :   The type of the None singleton.

`DealsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.hubspot.types.DealsSearchFilter`
    :   The type of the None singleton.

`DealsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.hubspot.types.DealsSearchFilter`
    :   The type of the None singleton.

`DealsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.hubspot.types.DealsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsInCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsAnyCondition`
    :   The type of the None singleton.

`DealsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.hubspot.types.DealsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsInCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsAnyCondition]`
    :   The type of the None singleton.

`DealsSearchFilter(*args, **kwargs)`
:   Available fields for filtering deals search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the deal has been deleted and moved to the recycling bin

    `companies: list[typing.Any] | None`
    :   Collection of company records associated with the deal

    `contacts: list[typing.Any] | None`
    :   Collection of contact records associated with the deal

    `created_at: str | None`
    :   Timestamp when the deal record was originally created

    `id: str | None`
    :   Unique identifier for the deal record

    `line_items: list[typing.Any] | None`
    :   Collection of product line items associated with the deal

    `properties: dict[str, typing.Any]`
    :   Key-value object containing all deal properties and custom fields

    `updated_at: str | None`
    :   Timestamp when the deal record was last modified

`DealsSearchQuery(*args, **kwargs)`
:   Search query for deals entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.hubspot.types.DealsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsInCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.hubspot.types.DealsSortFilter]`
    :   The type of the None singleton.

`DealsSortFilter(*args, **kwargs)`
:   Available fields for sorting deals search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Indicates whether the deal has been deleted and moved to the recycling bin

    `companies: Literal['asc', 'desc']`
    :   Collection of company records associated with the deal

    `contacts: Literal['asc', 'desc']`
    :   Collection of contact records associated with the deal

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the deal record was originally created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the deal record

    `line_items: Literal['asc', 'desc']`
    :   Collection of product line items associated with the deal

    `properties: Literal['asc', 'desc']`
    :   Key-value object containing all deal properties and custom fields

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the deal record was last modified

`DealsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Indicates whether the deal has been deleted and moved to the recycling bin

    `companies: str`
    :   Collection of company records associated with the deal

    `contacts: str`
    :   Collection of contact records associated with the deal

    `created_at: str`
    :   Timestamp when the deal record was originally created

    `id: str`
    :   Unique identifier for the deal record

    `line_items: str`
    :   Collection of product line items associated with the deal

    `properties: str`
    :   Key-value object containing all deal properties and custom fields

    `updated_at: str`
    :   Timestamp when the deal record was last modified

`ObjectsGetParams(*args, **kwargs)`
:   Parameters for objects.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `associations: str`
    :   The type of the None singleton.

    `id_property: str`
    :   The type of the None singleton.

    `object_id: str`
    :   The type of the None singleton.

    `object_type: str`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `properties_with_history: str`
    :   The type of the None singleton.

`ObjectsListParams(*args, **kwargs)`
:   Parameters for objects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `archived: bool`
    :   The type of the None singleton.

    `associations: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `object_type: str`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `properties_with_history: str`
    :   The type of the None singleton.

`SchemasGetParams(*args, **kwargs)`
:   Parameters for schemas.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `object_type: str`
    :   The type of the None singleton.

`SchemasListParams(*args, **kwargs)`
:   Parameters for schemas.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

`TicketsApiSearchParams(*args, **kwargs)`
:   Parameters for tickets.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `filter_groups: list[airbyte_agent_sdk.connectors.hubspot.types.TicketsApiSearchParamsFiltergroupsItem]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `properties: list[str]`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

    `sorts: list[airbyte_agent_sdk.connectors.hubspot.types.TicketsApiSearchParamsSortsItem]`
    :   The type of the None singleton.

`TicketsApiSearchParamsFiltergroupsItem(*args, **kwargs)`
:   Nested schema for TicketsApiSearchParams.filterGroups_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filters: list[airbyte_agent_sdk.connectors.hubspot.types.TicketsApiSearchParamsFiltergroupsItemFiltersItem]`
    :   The type of the None singleton.

`TicketsApiSearchParamsFiltergroupsItemFiltersItem(*args, **kwargs)`
:   Nested schema for TicketsApiSearchParamsFiltergroupsItem.filters_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `operator: str`
    :   The type of the None singleton.

    `propertyName: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

    ### Methods

    `values(self, /) ‑> list[str]`
    :   Return an object providing a view on the dict's values.

`TicketsApiSearchParamsSortsItem(*args, **kwargs)`
:   Nested schema for TicketsApiSearchParams.sorts_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `direction: str`
    :   The type of the None singleton.

    `propertyName: str`
    :   The type of the None singleton.

`TicketsGetParams(*args, **kwargs)`
:   Parameters for tickets.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `associations: str`
    :   The type of the None singleton.

    `id_property: str`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `properties_with_history: str`
    :   The type of the None singleton.

    `ticket_id: str`
    :   The type of the None singleton.

`TicketsListParams(*args, **kwargs)`
:   Parameters for tickets.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `archived: bool`
    :   The type of the None singleton.

    `associations: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `properties_with_history: str`
    :   The type of the None singleton.