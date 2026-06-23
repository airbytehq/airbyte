---
id: airbyte_agent_sdk-connectors-hubspot-types
title: airbyte_agent_sdk.connectors.hubspot.types
---

Module airbyte_agent_sdk.connectors.hubspot.types
=================================================
Type definitions for hubspot connector.

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

<a id="CompaniesAndCondition"></a>

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

<a id="CompaniesAnyCondition"></a>

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

<a id="CompaniesAnyValueFilter"></a>

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

    `properties_createdate: Any`
    :   Date the company was created

    `properties_domain: Any`
    :   Company domain name

    `properties_hs_lastmodifieddate: Any`
    :   Last modified date of the company

    `properties_hs_object_id: Any`
    :   HubSpot object ID

    `properties_hubspot_owner_id: Any`
    :   ID of the HubSpot owner assigned to this company

    `properties_name: Any`
    :   Company name

    `updated_at: Any`
    :   Timestamp when the company record was last modified

<a id="CompaniesApiSearchParams"></a>

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

<a id="CompaniesApiSearchParamsFiltergroupsItem"></a>

`CompaniesApiSearchParamsFiltergroupsItem(*args, **kwargs)`
:   Nested schema for CompaniesApiSearchParams.filterGroups_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filters: list[airbyte_agent_sdk.connectors.hubspot.types.CompaniesApiSearchParamsFiltergroupsItemFiltersItem]`
    :   The type of the None singleton.

<a id="CompaniesApiSearchParamsFiltergroupsItemFiltersItem"></a>

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

<a id="CompaniesApiSearchParamsSortsItem"></a>

`CompaniesApiSearchParamsSortsItem(*args, **kwargs)`
:   Nested schema for CompaniesApiSearchParams.sorts_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `direction: str`
    :   The type of the None singleton.

    `propertyName: str`
    :   The type of the None singleton.

<a id="CompaniesContainsCondition"></a>

`CompaniesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.hubspot.types.CompaniesAnyValueFilter`
    :   The type of the None singleton.

<a id="CompaniesEqCondition"></a>

`CompaniesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.hubspot.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesFuzzyCondition"></a>

`CompaniesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.hubspot.types.CompaniesStringFilter`
    :   The type of the None singleton.

<a id="CompaniesGetParams"></a>

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

<a id="CompaniesGtCondition"></a>

`CompaniesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.hubspot.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesGteCondition"></a>

`CompaniesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.hubspot.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesInCondition"></a>

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

<a id="CompaniesInFilter"></a>

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

    `properties_createdate: list[str]`
    :   Date the company was created

    `properties_domain: list[str]`
    :   Company domain name

    `properties_hs_lastmodifieddate: list[str]`
    :   Last modified date of the company

    `properties_hs_object_id: list[str]`
    :   HubSpot object ID

    `properties_hubspot_owner_id: list[str]`
    :   ID of the HubSpot owner assigned to this company

    `properties_name: list[str]`
    :   Company name

    `updated_at: list[str]`
    :   Timestamp when the company record was last modified

<a id="CompaniesKeywordCondition"></a>

`CompaniesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.hubspot.types.CompaniesStringFilter`
    :   The type of the None singleton.

<a id="CompaniesLikeCondition"></a>

`CompaniesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.hubspot.types.CompaniesStringFilter`
    :   The type of the None singleton.

<a id="CompaniesListParams"></a>

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

<a id="CompaniesLtCondition"></a>

`CompaniesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.hubspot.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesLteCondition"></a>

`CompaniesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.hubspot.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesNeqCondition"></a>

`CompaniesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.hubspot.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesNotCondition"></a>

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

<a id="CompaniesOrCondition"></a>

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

<a id="CompaniesSearchFilter"></a>

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

    `properties_createdate: str | None`
    :   Date the company was created

    `properties_domain: str | None`
    :   Company domain name

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the company

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hubspot_owner_id: str | None`
    :   ID of the HubSpot owner assigned to this company

    `properties_name: str | None`
    :   Company name

    `updated_at: str | None`
    :   Timestamp when the company record was last modified

<a id="CompaniesSearchQuery"></a>

`CompaniesSearchQuery(*args, **kwargs)`
:   Search query for companies entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.hubspot.types.CompaniesEqCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesGtCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesGteCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLtCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLteCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesInCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesNotCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesAndCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesOrCondition | airbyte_agent_sdk.connectors.hubspot.types.CompaniesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.hubspot.types.CompaniesSortFilter]`
    :   The type of the None singleton.

<a id="CompaniesSortFilter"></a>

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

    `properties_createdate: Literal['asc', 'desc']`
    :   Date the company was created

    `properties_domain: Literal['asc', 'desc']`
    :   Company domain name

    `properties_hs_lastmodifieddate: Literal['asc', 'desc']`
    :   Last modified date of the company

    `properties_hs_object_id: Literal['asc', 'desc']`
    :   HubSpot object ID

    `properties_hubspot_owner_id: Literal['asc', 'desc']`
    :   ID of the HubSpot owner assigned to this company

    `properties_name: Literal['asc', 'desc']`
    :   Company name

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the company record was last modified

<a id="CompaniesStringFilter"></a>

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

    `properties_createdate: str`
    :   Date the company was created

    `properties_domain: str`
    :   Company domain name

    `properties_hs_lastmodifieddate: str`
    :   Last modified date of the company

    `properties_hs_object_id: str`
    :   HubSpot object ID

    `properties_hubspot_owner_id: str`
    :   ID of the HubSpot owner assigned to this company

    `properties_name: str`
    :   Company name

    `updated_at: str`
    :   Timestamp when the company record was last modified

<a id="ContactsAndCondition"></a>

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

<a id="ContactsAnyCondition"></a>

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

<a id="ContactsAnyValueFilter"></a>

`ContactsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Boolean flag indicating whether the contact has been archived or deleted

    `companies: Any`
    :   Associated company records linked to this contact

    `created_at: Any`
    :   Timestamp indicating when the contact was first created in the system

    `id: Any`
    :   Unique identifier for the contact record

    `properties: Any`
    :   Key-value object storing all contact properties and their values.

    `properties_associatedcompanyid: Any`
    :   ID of the associated company

    `properties_createdate: Any`
    :   Date the contact was created

    `properties_email: Any`
    :   Contact email address

    `properties_firstname: Any`
    :   Contact first name

    `properties_hs_object_id: Any`
    :   HubSpot object ID

    `properties_hubspot_owner_id: Any`
    :   ID of the HubSpot owner assigned to this contact

    `properties_lastmodifieddate: Any`
    :   Last modified date of the contact

    `properties_lastname: Any`
    :   Contact last name

    `updated_at: Any`
    :   Timestamp indicating when the contact record was last modified

<a id="ContactsApiSearchParams"></a>

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

<a id="ContactsApiSearchParamsFiltergroupsItem"></a>

`ContactsApiSearchParamsFiltergroupsItem(*args, **kwargs)`
:   Nested schema for ContactsApiSearchParams.filterGroups_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filters: list[airbyte_agent_sdk.connectors.hubspot.types.ContactsApiSearchParamsFiltergroupsItemFiltersItem]`
    :   The type of the None singleton.

<a id="ContactsApiSearchParamsFiltergroupsItemFiltersItem"></a>

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

<a id="ContactsApiSearchParamsSortsItem"></a>

`ContactsApiSearchParamsSortsItem(*args, **kwargs)`
:   Nested schema for ContactsApiSearchParams.sorts_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `direction: str`
    :   The type of the None singleton.

    `propertyName: str`
    :   The type of the None singleton.

<a id="ContactsContainsCondition"></a>

`ContactsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.hubspot.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

<a id="ContactsEqCondition"></a>

`ContactsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.hubspot.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsFuzzyCondition"></a>

`ContactsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.hubspot.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsGetParams"></a>

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

<a id="ContactsGtCondition"></a>

`ContactsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.hubspot.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsGteCondition"></a>

`ContactsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.hubspot.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsInCondition"></a>

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

<a id="ContactsInFilter"></a>

`ContactsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Boolean flag indicating whether the contact has been archived or deleted

    `companies: list[list[typing.Any]]`
    :   Associated company records linked to this contact

    `created_at: list[str]`
    :   Timestamp indicating when the contact was first created in the system

    `id: list[str]`
    :   Unique identifier for the contact record

    `properties: list[dict[str, typing.Any]]`
    :   Key-value object storing all contact properties and their values.

    `properties_associatedcompanyid: list[str]`
    :   ID of the associated company

    `properties_createdate: list[str]`
    :   Date the contact was created

    `properties_email: list[str]`
    :   Contact email address

    `properties_firstname: list[str]`
    :   Contact first name

    `properties_hs_object_id: list[str]`
    :   HubSpot object ID

    `properties_hubspot_owner_id: list[str]`
    :   ID of the HubSpot owner assigned to this contact

    `properties_lastmodifieddate: list[str]`
    :   Last modified date of the contact

    `properties_lastname: list[str]`
    :   Contact last name

    `updated_at: list[str]`
    :   Timestamp indicating when the contact record was last modified

<a id="ContactsKeywordCondition"></a>

`ContactsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.hubspot.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsLikeCondition"></a>

`ContactsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.hubspot.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsListParams"></a>

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

<a id="ContactsLtCondition"></a>

`ContactsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.hubspot.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsLteCondition"></a>

`ContactsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.hubspot.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsNeqCondition"></a>

`ContactsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.hubspot.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsNotCondition"></a>

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

<a id="ContactsOrCondition"></a>

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

<a id="ContactsSearchFilter"></a>

`ContactsSearchFilter(*args, **kwargs)`
:   Available fields for filtering contacts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool | None`
    :   Boolean flag indicating whether the contact has been archived or deleted

    `companies: list[typing.Any] | None`
    :   Associated company records linked to this contact

    `created_at: str | None`
    :   Timestamp indicating when the contact was first created in the system

    `id: str | None`
    :   Unique identifier for the contact record

    `properties: dict[str, typing.Any]`
    :   Key-value object storing all contact properties and their values.

    `properties_associatedcompanyid: str | None`
    :   ID of the associated company

    `properties_createdate: str | None`
    :   Date the contact was created

    `properties_email: str | None`
    :   Contact email address

    `properties_firstname: str | None`
    :   Contact first name

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hubspot_owner_id: str | None`
    :   ID of the HubSpot owner assigned to this contact

    `properties_lastmodifieddate: str | None`
    :   Last modified date of the contact

    `properties_lastname: str | None`
    :   Contact last name

    `updated_at: str | None`
    :   Timestamp indicating when the contact record was last modified

<a id="ContactsSearchQuery"></a>

`ContactsSearchQuery(*args, **kwargs)`
:   Search query for contacts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.hubspot.types.ContactsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsInCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.ContactsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.hubspot.types.ContactsSortFilter]`
    :   The type of the None singleton.

<a id="ContactsSortFilter"></a>

`ContactsSortFilter(*args, **kwargs)`
:   Available fields for sorting contacts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Boolean flag indicating whether the contact has been archived or deleted

    `companies: Literal['asc', 'desc']`
    :   Associated company records linked to this contact

    `created_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the contact was first created in the system

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the contact record

    `properties: Literal['asc', 'desc']`
    :   Key-value object storing all contact properties and their values.

    `properties_associatedcompanyid: Literal['asc', 'desc']`
    :   ID of the associated company

    `properties_createdate: Literal['asc', 'desc']`
    :   Date the contact was created

    `properties_email: Literal['asc', 'desc']`
    :   Contact email address

    `properties_firstname: Literal['asc', 'desc']`
    :   Contact first name

    `properties_hs_object_id: Literal['asc', 'desc']`
    :   HubSpot object ID

    `properties_hubspot_owner_id: Literal['asc', 'desc']`
    :   ID of the HubSpot owner assigned to this contact

    `properties_lastmodifieddate: Literal['asc', 'desc']`
    :   Last modified date of the contact

    `properties_lastname: Literal['asc', 'desc']`
    :   Contact last name

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the contact record was last modified

<a id="ContactsStringFilter"></a>

`ContactsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Boolean flag indicating whether the contact has been archived or deleted

    `companies: str`
    :   Associated company records linked to this contact

    `created_at: str`
    :   Timestamp indicating when the contact was first created in the system

    `id: str`
    :   Unique identifier for the contact record

    `properties: str`
    :   Key-value object storing all contact properties and their values.

    `properties_associatedcompanyid: str`
    :   ID of the associated company

    `properties_createdate: str`
    :   Date the contact was created

    `properties_email: str`
    :   Contact email address

    `properties_firstname: str`
    :   Contact first name

    `properties_hs_object_id: str`
    :   HubSpot object ID

    `properties_hubspot_owner_id: str`
    :   ID of the HubSpot owner assigned to this contact

    `properties_lastmodifieddate: str`
    :   Last modified date of the contact

    `properties_lastname: str`
    :   Contact last name

    `updated_at: str`
    :   Timestamp indicating when the contact record was last modified

<a id="DealsAndCondition"></a>

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

<a id="DealsAnyCondition"></a>

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

<a id="DealsAnyValueFilter"></a>

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

    `properties_amount: Any`
    :   Deal amount

    `properties_closedate: Any`
    :   Expected close date of the deal

    `properties_createdate: Any`
    :   Date the deal was created

    `properties_dealname: Any`
    :   Deal name

    `properties_dealstage: Any`
    :   Current deal stage

    `properties_hs_lastmodifieddate: Any`
    :   Last modified date of the deal

    `properties_hs_object_id: Any`
    :   HubSpot object ID

    `properties_hubspot_owner_id: Any`
    :   ID of the HubSpot owner assigned to this deal

    `properties_pipeline: Any`
    :   Deal pipeline

    `updated_at: Any`
    :   Timestamp when the deal record was last modified

<a id="DealsApiSearchParams"></a>

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

<a id="DealsApiSearchParamsFiltergroupsItem"></a>

`DealsApiSearchParamsFiltergroupsItem(*args, **kwargs)`
:   Nested schema for DealsApiSearchParams.filterGroups_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filters: list[airbyte_agent_sdk.connectors.hubspot.types.DealsApiSearchParamsFiltergroupsItemFiltersItem]`
    :   The type of the None singleton.

<a id="DealsApiSearchParamsFiltergroupsItemFiltersItem"></a>

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

<a id="DealsApiSearchParamsSortsItem"></a>

`DealsApiSearchParamsSortsItem(*args, **kwargs)`
:   Nested schema for DealsApiSearchParams.sorts_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `direction: str`
    :   The type of the None singleton.

    `propertyName: str`
    :   The type of the None singleton.

<a id="DealsContainsCondition"></a>

`DealsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.hubspot.types.DealsAnyValueFilter`
    :   The type of the None singleton.

<a id="DealsEqCondition"></a>

`DealsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.hubspot.types.DealsSearchFilter`
    :   The type of the None singleton.

<a id="DealsFuzzyCondition"></a>

`DealsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.hubspot.types.DealsStringFilter`
    :   The type of the None singleton.

<a id="DealsGetParams"></a>

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

<a id="DealsGtCondition"></a>

`DealsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.hubspot.types.DealsSearchFilter`
    :   The type of the None singleton.

<a id="DealsGteCondition"></a>

`DealsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.hubspot.types.DealsSearchFilter`
    :   The type of the None singleton.

<a id="DealsInCondition"></a>

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

<a id="DealsInFilter"></a>

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

    `properties_amount: list[str]`
    :   Deal amount

    `properties_closedate: list[str]`
    :   Expected close date of the deal

    `properties_createdate: list[str]`
    :   Date the deal was created

    `properties_dealname: list[str]`
    :   Deal name

    `properties_dealstage: list[str]`
    :   Current deal stage

    `properties_hs_lastmodifieddate: list[str]`
    :   Last modified date of the deal

    `properties_hs_object_id: list[str]`
    :   HubSpot object ID

    `properties_hubspot_owner_id: list[str]`
    :   ID of the HubSpot owner assigned to this deal

    `properties_pipeline: list[str]`
    :   Deal pipeline

    `updated_at: list[str]`
    :   Timestamp when the deal record was last modified

<a id="DealsKeywordCondition"></a>

`DealsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.hubspot.types.DealsStringFilter`
    :   The type of the None singleton.

<a id="DealsLikeCondition"></a>

`DealsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.hubspot.types.DealsStringFilter`
    :   The type of the None singleton.

<a id="DealsListParams"></a>

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

<a id="DealsLtCondition"></a>

`DealsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.hubspot.types.DealsSearchFilter`
    :   The type of the None singleton.

<a id="DealsLteCondition"></a>

`DealsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.hubspot.types.DealsSearchFilter`
    :   The type of the None singleton.

<a id="DealsNeqCondition"></a>

`DealsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.hubspot.types.DealsSearchFilter`
    :   The type of the None singleton.

<a id="DealsNotCondition"></a>

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

<a id="DealsOrCondition"></a>

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

<a id="DealsSearchFilter"></a>

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

    `properties_amount: str | None`
    :   Deal amount

    `properties_closedate: str | None`
    :   Expected close date of the deal

    `properties_createdate: str | None`
    :   Date the deal was created

    `properties_dealname: str | None`
    :   Deal name

    `properties_dealstage: str | None`
    :   Current deal stage

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the deal

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hubspot_owner_id: str | None`
    :   ID of the HubSpot owner assigned to this deal

    `properties_pipeline: str | None`
    :   Deal pipeline

    `updated_at: str | None`
    :   Timestamp when the deal record was last modified

<a id="DealsSearchQuery"></a>

`DealsSearchQuery(*args, **kwargs)`
:   Search query for deals entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.hubspot.types.DealsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsInCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.DealsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.hubspot.types.DealsSortFilter]`
    :   The type of the None singleton.

<a id="DealsSortFilter"></a>

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

    `properties_amount: Literal['asc', 'desc']`
    :   Deal amount

    `properties_closedate: Literal['asc', 'desc']`
    :   Expected close date of the deal

    `properties_createdate: Literal['asc', 'desc']`
    :   Date the deal was created

    `properties_dealname: Literal['asc', 'desc']`
    :   Deal name

    `properties_dealstage: Literal['asc', 'desc']`
    :   Current deal stage

    `properties_hs_lastmodifieddate: Literal['asc', 'desc']`
    :   Last modified date of the deal

    `properties_hs_object_id: Literal['asc', 'desc']`
    :   HubSpot object ID

    `properties_hubspot_owner_id: Literal['asc', 'desc']`
    :   ID of the HubSpot owner assigned to this deal

    `properties_pipeline: Literal['asc', 'desc']`
    :   Deal pipeline

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the deal record was last modified

<a id="DealsStringFilter"></a>

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

    `properties_amount: str`
    :   Deal amount

    `properties_closedate: str`
    :   Expected close date of the deal

    `properties_createdate: str`
    :   Date the deal was created

    `properties_dealname: str`
    :   Deal name

    `properties_dealstage: str`
    :   Current deal stage

    `properties_hs_lastmodifieddate: str`
    :   Last modified date of the deal

    `properties_hs_object_id: str`
    :   HubSpot object ID

    `properties_hubspot_owner_id: str`
    :   ID of the HubSpot owner assigned to this deal

    `properties_pipeline: str`
    :   Deal pipeline

    `updated_at: str`
    :   Timestamp when the deal record was last modified

<a id="ObjectsGetParams"></a>

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

<a id="ObjectsListParams"></a>

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

<a id="SchemasGetParams"></a>

`SchemasGetParams(*args, **kwargs)`
:   Parameters for schemas.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `object_type: str`
    :   The type of the None singleton.

<a id="SchemasListParams"></a>

`SchemasListParams(*args, **kwargs)`
:   Parameters for schemas.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

<a id="TicketsAndCondition"></a>

`TicketsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.hubspot.types.TicketsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsInCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketsAnyCondition"></a>

`TicketsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.hubspot.types.TicketsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketsAnyValueFilter"></a>

`TicketsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Indicates whether the ticket has been deleted and moved to the recycling bin

    `companies: Any`
    :   Collection of company records associated with the ticket

    `contacts: Any`
    :   Collection of contact records associated with the ticket

    `created_at: Any`
    :   Timestamp when the ticket record was originally created

    `id: Any`
    :   Unique identifier for the ticket record

    `properties: Any`
    :   Object containing all property values for the ticket

    `properties_content: Any`
    :   Ticket content/description

    `properties_createdate: Any`
    :   Date the ticket was created

    `properties_hs_lastmodifieddate: Any`
    :   Last modified date of the ticket

    `properties_hs_object_id: Any`
    :   HubSpot object ID

    `properties_hs_pipeline: Any`
    :   Ticket pipeline

    `properties_hs_pipeline_stage: Any`
    :   Current pipeline stage of the ticket

    `properties_hs_ticket_category: Any`
    :   Ticket category

    `properties_hs_ticket_priority: Any`
    :   Ticket priority level

    `properties_subject: Any`
    :   Ticket subject line

    `updated_at: Any`
    :   Timestamp when the ticket record was last modified

<a id="TicketsApiSearchParams"></a>

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

<a id="TicketsApiSearchParamsFiltergroupsItem"></a>

`TicketsApiSearchParamsFiltergroupsItem(*args, **kwargs)`
:   Nested schema for TicketsApiSearchParams.filterGroups_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filters: list[airbyte_agent_sdk.connectors.hubspot.types.TicketsApiSearchParamsFiltergroupsItemFiltersItem]`
    :   The type of the None singleton.

<a id="TicketsApiSearchParamsFiltergroupsItemFiltersItem"></a>

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

<a id="TicketsApiSearchParamsSortsItem"></a>

`TicketsApiSearchParamsSortsItem(*args, **kwargs)`
:   Nested schema for TicketsApiSearchParams.sorts_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `direction: str`
    :   The type of the None singleton.

    `propertyName: str`
    :   The type of the None singleton.

<a id="TicketsContainsCondition"></a>

`TicketsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.hubspot.types.TicketsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketsEqCondition"></a>

`TicketsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.hubspot.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsFuzzyCondition"></a>

`TicketsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.hubspot.types.TicketsStringFilter`
    :   The type of the None singleton.

<a id="TicketsGetParams"></a>

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

<a id="TicketsGtCondition"></a>

`TicketsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.hubspot.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsGteCondition"></a>

`TicketsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.hubspot.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsInCondition"></a>

`TicketsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.hubspot.types.TicketsInFilter`
    :   The type of the None singleton.

<a id="TicketsInFilter"></a>

`TicketsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Indicates whether the ticket has been deleted and moved to the recycling bin

    `companies: list[list[typing.Any]]`
    :   Collection of company records associated with the ticket

    `contacts: list[list[typing.Any]]`
    :   Collection of contact records associated with the ticket

    `created_at: list[str]`
    :   Timestamp when the ticket record was originally created

    `id: list[str]`
    :   Unique identifier for the ticket record

    `properties: list[dict[str, typing.Any]]`
    :   Object containing all property values for the ticket

    `properties_content: list[str]`
    :   Ticket content/description

    `properties_createdate: list[str]`
    :   Date the ticket was created

    `properties_hs_lastmodifieddate: list[str]`
    :   Last modified date of the ticket

    `properties_hs_object_id: list[str]`
    :   HubSpot object ID

    `properties_hs_pipeline: list[str]`
    :   Ticket pipeline

    `properties_hs_pipeline_stage: list[str]`
    :   Current pipeline stage of the ticket

    `properties_hs_ticket_category: list[str]`
    :   Ticket category

    `properties_hs_ticket_priority: list[str]`
    :   Ticket priority level

    `properties_subject: list[str]`
    :   Ticket subject line

    `updated_at: list[str]`
    :   Timestamp when the ticket record was last modified

<a id="TicketsKeywordCondition"></a>

`TicketsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.hubspot.types.TicketsStringFilter`
    :   The type of the None singleton.

<a id="TicketsLikeCondition"></a>

`TicketsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.hubspot.types.TicketsStringFilter`
    :   The type of the None singleton.

<a id="TicketsListParams"></a>

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

<a id="TicketsLtCondition"></a>

`TicketsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.hubspot.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsLteCondition"></a>

`TicketsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.hubspot.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsNeqCondition"></a>

`TicketsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.hubspot.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsNotCondition"></a>

`TicketsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.hubspot.types.TicketsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsInCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsAnyCondition`
    :   The type of the None singleton.

<a id="TicketsOrCondition"></a>

`TicketsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.hubspot.types.TicketsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsInCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketsSearchFilter"></a>

`TicketsSearchFilter(*args, **kwargs)`
:   Available fields for filtering tickets search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the ticket has been deleted and moved to the recycling bin

    `companies: list[typing.Any] | None`
    :   Collection of company records associated with the ticket

    `contacts: list[typing.Any] | None`
    :   Collection of contact records associated with the ticket

    `created_at: str | None`
    :   Timestamp when the ticket record was originally created

    `id: str | None`
    :   Unique identifier for the ticket record

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the ticket

    `properties_content: str | None`
    :   Ticket content/description

    `properties_createdate: str | None`
    :   Date the ticket was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the ticket

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_pipeline: str | None`
    :   Ticket pipeline

    `properties_hs_pipeline_stage: str | None`
    :   Current pipeline stage of the ticket

    `properties_hs_ticket_category: str | None`
    :   Ticket category

    `properties_hs_ticket_priority: str | None`
    :   Ticket priority level

    `properties_subject: str | None`
    :   Ticket subject line

    `updated_at: str | None`
    :   Timestamp when the ticket record was last modified

<a id="TicketsSearchQuery"></a>

`TicketsSearchQuery(*args, **kwargs)`
:   Search query for tickets entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.hubspot.types.TicketsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsInCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.TicketsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.hubspot.types.TicketsSortFilter]`
    :   The type of the None singleton.

<a id="TicketsSortFilter"></a>

`TicketsSortFilter(*args, **kwargs)`
:   Available fields for sorting tickets search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Indicates whether the ticket has been deleted and moved to the recycling bin

    `companies: Literal['asc', 'desc']`
    :   Collection of company records associated with the ticket

    `contacts: Literal['asc', 'desc']`
    :   Collection of contact records associated with the ticket

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the ticket record was originally created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the ticket record

    `properties: Literal['asc', 'desc']`
    :   Object containing all property values for the ticket

    `properties_content: Literal['asc', 'desc']`
    :   Ticket content/description

    `properties_createdate: Literal['asc', 'desc']`
    :   Date the ticket was created

    `properties_hs_lastmodifieddate: Literal['asc', 'desc']`
    :   Last modified date of the ticket

    `properties_hs_object_id: Literal['asc', 'desc']`
    :   HubSpot object ID

    `properties_hs_pipeline: Literal['asc', 'desc']`
    :   Ticket pipeline

    `properties_hs_pipeline_stage: Literal['asc', 'desc']`
    :   Current pipeline stage of the ticket

    `properties_hs_ticket_category: Literal['asc', 'desc']`
    :   Ticket category

    `properties_hs_ticket_priority: Literal['asc', 'desc']`
    :   Ticket priority level

    `properties_subject: Literal['asc', 'desc']`
    :   Ticket subject line

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the ticket record was last modified

<a id="TicketsStringFilter"></a>

`TicketsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Indicates whether the ticket has been deleted and moved to the recycling bin

    `companies: str`
    :   Collection of company records associated with the ticket

    `contacts: str`
    :   Collection of contact records associated with the ticket

    `created_at: str`
    :   Timestamp when the ticket record was originally created

    `id: str`
    :   Unique identifier for the ticket record

    `properties: str`
    :   Object containing all property values for the ticket

    `properties_content: str`
    :   Ticket content/description

    `properties_createdate: str`
    :   Date the ticket was created

    `properties_hs_lastmodifieddate: str`
    :   Last modified date of the ticket

    `properties_hs_object_id: str`
    :   HubSpot object ID

    `properties_hs_pipeline: str`
    :   Ticket pipeline

    `properties_hs_pipeline_stage: str`
    :   Current pipeline stage of the ticket

    `properties_hs_ticket_category: str`
    :   Ticket category

    `properties_hs_ticket_priority: str`
    :   Ticket priority level

    `properties_subject: str`
    :   Ticket subject line

    `updated_at: str`
    :   Timestamp when the ticket record was last modified