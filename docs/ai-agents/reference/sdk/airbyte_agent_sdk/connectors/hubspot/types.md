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

<a id="CallsAndCondition"></a>

`CallsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.hubspot.types.CallsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsInCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsAnyCondition]`
    :   The type of the None singleton.

<a id="CallsAnyCondition"></a>

`CallsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.hubspot.types.CallsAnyValueFilter`
    :   The type of the None singleton.

<a id="CallsAnyValueFilter"></a>

`CallsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Indicates whether the call has been archived

    `created_at: Any`
    :   Timestamp when the call was created

    `id: Any`
    :   Unique identifier for the call record

    `properties: Any`
    :   Object containing all property values for the call

    `properties_hs_call_body: Any`
    :   Description or notes about the call

    `properties_hs_call_direction: Any`
    :   Direction of the call (INBOUND or OUTBOUND)

    `properties_hs_call_duration: Any`
    :   Duration of the call in milliseconds

    `properties_hs_call_status: Any`
    :   Status of the call (e.g., COMPLETED, BUSY, NO_ANSWER)

    `properties_hs_call_title: Any`
    :   Title or subject of the call

    `properties_hs_createdate: Any`
    :   Date the call was created

    `properties_hs_lastmodifieddate: Any`
    :   Last modified date of the call

    `properties_hs_object_id: Any`
    :   HubSpot object ID

    `properties_hs_timestamp: Any`
    :   Timestamp when the call activity occurred

    `properties_hubspot_owner_id: Any`
    :   ID of the call owner

    `updated_at: Any`
    :   Timestamp when the call record was last modified

<a id="CallsContainsCondition"></a>

`CallsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.hubspot.types.CallsAnyValueFilter`
    :   The type of the None singleton.

<a id="CallsCreateParams"></a>

`CallsCreateParams(*args, **kwargs)`
:   Parameters for calls.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associations: list[airbyte_agent_sdk.connectors.hubspot.types.CallsCreateParamsAssociationsItem]`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.types.CallsCreateParamsProperties`
    :   The type of the None singleton.

<a id="CallsCreateParamsAssociationsItem"></a>

`CallsCreateParamsAssociationsItem(*args, **kwargs)`
:   Nested schema for CallsCreateParams.associations_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `to: airbyte_agent_sdk.connectors.hubspot.types.CallsCreateParamsAssociationsItemTo`
    :   The type of the None singleton.

    `types: list[airbyte_agent_sdk.connectors.hubspot.types.CallsCreateParamsAssociationsItemTypesItem]`
    :   The type of the None singleton.

<a id="CallsCreateParamsAssociationsItemTo"></a>

`CallsCreateParamsAssociationsItemTo(*args, **kwargs)`
:   Nested schema for CallsCreateParamsAssociationsItem.to

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CallsCreateParamsAssociationsItemTypesItem"></a>

`CallsCreateParamsAssociationsItemTypesItem(*args, **kwargs)`
:   Nested schema for CallsCreateParamsAssociationsItem.types_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associationCategory: str`
    :   The type of the None singleton.

    `associationTypeId: int`
    :   The type of the None singleton.

<a id="CallsCreateParamsProperties"></a>

`CallsCreateParamsProperties(*args, **kwargs)`
:   Call properties to set

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hs_call_body: str`
    :   The type of the None singleton.

    `hs_call_direction: str`
    :   The type of the None singleton.

    `hs_call_disposition: str`
    :   The type of the None singleton.

    `hs_call_duration: str`
    :   The type of the None singleton.

    `hs_call_from_number: str`
    :   The type of the None singleton.

    `hs_call_status: str`
    :   The type of the None singleton.

    `hs_call_title: str`
    :   The type of the None singleton.

    `hs_call_to_number: str`
    :   The type of the None singleton.

    `hs_timestamp: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

<a id="CallsDeleteParams"></a>

`CallsDeleteParams(*args, **kwargs)`
:   Parameters for calls.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `call_id: str`
    :   The type of the None singleton.

<a id="CallsEqCondition"></a>

`CallsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.hubspot.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsFuzzyCondition"></a>

`CallsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.hubspot.types.CallsStringFilter`
    :   The type of the None singleton.

<a id="CallsGetParams"></a>

`CallsGetParams(*args, **kwargs)`
:   Parameters for calls.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `associations: str`
    :   The type of the None singleton.

    `call_id: str`
    :   The type of the None singleton.

    `id_property: str`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `properties_with_history: str`
    :   The type of the None singleton.

<a id="CallsGtCondition"></a>

`CallsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.hubspot.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsGteCondition"></a>

`CallsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.hubspot.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsInCondition"></a>

`CallsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.hubspot.types.CallsInFilter`
    :   The type of the None singleton.

<a id="CallsInFilter"></a>

`CallsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Indicates whether the call has been archived

    `created_at: list[str]`
    :   Timestamp when the call was created

    `id: list[str]`
    :   Unique identifier for the call record

    `properties: list[dict[str, typing.Any]]`
    :   Object containing all property values for the call

    `properties_hs_call_body: list[str]`
    :   Description or notes about the call

    `properties_hs_call_direction: list[str]`
    :   Direction of the call (INBOUND or OUTBOUND)

    `properties_hs_call_duration: list[str]`
    :   Duration of the call in milliseconds

    `properties_hs_call_status: list[str]`
    :   Status of the call (e.g., COMPLETED, BUSY, NO_ANSWER)

    `properties_hs_call_title: list[str]`
    :   Title or subject of the call

    `properties_hs_createdate: list[str]`
    :   Date the call was created

    `properties_hs_lastmodifieddate: list[str]`
    :   Last modified date of the call

    `properties_hs_object_id: list[str]`
    :   HubSpot object ID

    `properties_hs_timestamp: list[str]`
    :   Timestamp when the call activity occurred

    `properties_hubspot_owner_id: list[str]`
    :   ID of the call owner

    `updated_at: list[str]`
    :   Timestamp when the call record was last modified

<a id="CallsKeywordCondition"></a>

`CallsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.hubspot.types.CallsStringFilter`
    :   The type of the None singleton.

<a id="CallsLikeCondition"></a>

`CallsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.hubspot.types.CallsStringFilter`
    :   The type of the None singleton.

<a id="CallsListParams"></a>

`CallsListParams(*args, **kwargs)`
:   Parameters for calls.list operation

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

<a id="CallsLtCondition"></a>

`CallsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.hubspot.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsLteCondition"></a>

`CallsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.hubspot.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsNeqCondition"></a>

`CallsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.hubspot.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsNotCondition"></a>

`CallsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.hubspot.types.CallsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsInCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsAnyCondition`
    :   The type of the None singleton.

<a id="CallsOrCondition"></a>

`CallsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.hubspot.types.CallsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsInCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsAnyCondition]`
    :   The type of the None singleton.

<a id="CallsSearchFilter"></a>

`CallsSearchFilter(*args, **kwargs)`
:   Available fields for filtering calls search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the call has been archived

    `created_at: str | None`
    :   Timestamp when the call was created

    `id: str | None`
    :   Unique identifier for the call record

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the call

    `properties_hs_call_body: str | None`
    :   Description or notes about the call

    `properties_hs_call_direction: str | None`
    :   Direction of the call (INBOUND or OUTBOUND)

    `properties_hs_call_duration: str | None`
    :   Duration of the call in milliseconds

    `properties_hs_call_status: str | None`
    :   Status of the call (e.g., COMPLETED, BUSY, NO_ANSWER)

    `properties_hs_call_title: str | None`
    :   Title or subject of the call

    `properties_hs_createdate: str | None`
    :   Date the call was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the call

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_timestamp: str | None`
    :   Timestamp when the call activity occurred

    `properties_hubspot_owner_id: str | None`
    :   ID of the call owner

    `updated_at: str | None`
    :   Timestamp when the call record was last modified

<a id="CallsSearchQuery"></a>

`CallsSearchQuery(*args, **kwargs)`
:   Search query for calls entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.hubspot.types.CallsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsInCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.CallsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.hubspot.types.CallsSortFilter]`
    :   The type of the None singleton.

<a id="CallsSortFilter"></a>

`CallsSortFilter(*args, **kwargs)`
:   Available fields for sorting calls search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Indicates whether the call has been archived

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the call was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the call record

    `properties: Literal['asc', 'desc']`
    :   Object containing all property values for the call

    `properties_hs_call_body: Literal['asc', 'desc']`
    :   Description or notes about the call

    `properties_hs_call_direction: Literal['asc', 'desc']`
    :   Direction of the call (INBOUND or OUTBOUND)

    `properties_hs_call_duration: Literal['asc', 'desc']`
    :   Duration of the call in milliseconds

    `properties_hs_call_status: Literal['asc', 'desc']`
    :   Status of the call (e.g., COMPLETED, BUSY, NO_ANSWER)

    `properties_hs_call_title: Literal['asc', 'desc']`
    :   Title or subject of the call

    `properties_hs_createdate: Literal['asc', 'desc']`
    :   Date the call was created

    `properties_hs_lastmodifieddate: Literal['asc', 'desc']`
    :   Last modified date of the call

    `properties_hs_object_id: Literal['asc', 'desc']`
    :   HubSpot object ID

    `properties_hs_timestamp: Literal['asc', 'desc']`
    :   Timestamp when the call activity occurred

    `properties_hubspot_owner_id: Literal['asc', 'desc']`
    :   ID of the call owner

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the call record was last modified

<a id="CallsStringFilter"></a>

`CallsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Indicates whether the call has been archived

    `created_at: str`
    :   Timestamp when the call was created

    `id: str`
    :   Unique identifier for the call record

    `properties: str`
    :   Object containing all property values for the call

    `properties_hs_call_body: str`
    :   Description or notes about the call

    `properties_hs_call_direction: str`
    :   Direction of the call (INBOUND or OUTBOUND)

    `properties_hs_call_duration: str`
    :   Duration of the call in milliseconds

    `properties_hs_call_status: str`
    :   Status of the call (e.g., COMPLETED, BUSY, NO_ANSWER)

    `properties_hs_call_title: str`
    :   Title or subject of the call

    `properties_hs_createdate: str`
    :   Date the call was created

    `properties_hs_lastmodifieddate: str`
    :   Last modified date of the call

    `properties_hs_object_id: str`
    :   HubSpot object ID

    `properties_hs_timestamp: str`
    :   Timestamp when the call activity occurred

    `properties_hubspot_owner_id: str`
    :   ID of the call owner

    `updated_at: str`
    :   Timestamp when the call record was last modified

<a id="CallsUpdateParams"></a>

`CallsUpdateParams(*args, **kwargs)`
:   Parameters for calls.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `call_id: str`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.types.CallsUpdateParamsProperties`
    :   The type of the None singleton.

<a id="CallsUpdateParamsProperties"></a>

`CallsUpdateParamsProperties(*args, **kwargs)`
:   Call properties to update

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hs_call_body: str`
    :   The type of the None singleton.

    `hs_call_direction: str`
    :   The type of the None singleton.

    `hs_call_disposition: str`
    :   The type of the None singleton.

    `hs_call_duration: str`
    :   The type of the None singleton.

    `hs_call_from_number: str`
    :   The type of the None singleton.

    `hs_call_status: str`
    :   The type of the None singleton.

    `hs_call_title: str`
    :   The type of the None singleton.

    `hs_call_to_number: str`
    :   The type of the None singleton.

    `hs_timestamp: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
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

<a id="CompaniesCreateParams"></a>

`CompaniesCreateParams(*args, **kwargs)`
:   Parameters for companies.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `properties: airbyte_agent_sdk.connectors.hubspot.types.CompaniesCreateParamsProperties`
    :   The type of the None singleton.

<a id="CompaniesCreateParamsProperties"></a>

`CompaniesCreateParamsProperties(*args, **kwargs)`
:   Company properties to set

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annualrevenue: str`
    :   The type of the None singleton.

    `city: str`
    :   The type of the None singleton.

    `country: str`
    :   The type of the None singleton.

    `description: str`
    :   The type of the None singleton.

    `domain: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

    `industry: str`
    :   The type of the None singleton.

    `lifecyclestage: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `numberofemployees: str`
    :   The type of the None singleton.

    `phone: str`
    :   The type of the None singleton.

    `state: str`
    :   The type of the None singleton.

    `website: str`
    :   The type of the None singleton.

    `zip: str`
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

<a id="CompaniesUpdateParams"></a>

`CompaniesUpdateParams(*args, **kwargs)`
:   Parameters for companies.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `company_id: str`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.types.CompaniesUpdateParamsProperties`
    :   The type of the None singleton.

<a id="CompaniesUpdateParamsProperties"></a>

`CompaniesUpdateParamsProperties(*args, **kwargs)`
:   Company properties to update

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annualrevenue: str`
    :   The type of the None singleton.

    `city: str`
    :   The type of the None singleton.

    `country: str`
    :   The type of the None singleton.

    `description: str`
    :   The type of the None singleton.

    `domain: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

    `industry: str`
    :   The type of the None singleton.

    `lifecyclestage: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `numberofemployees: str`
    :   The type of the None singleton.

    `phone: str`
    :   The type of the None singleton.

    `state: str`
    :   The type of the None singleton.

    `website: str`
    :   The type of the None singleton.

    `zip: str`
    :   The type of the None singleton.

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

<a id="ContactsCreateParams"></a>

`ContactsCreateParams(*args, **kwargs)`
:   Parameters for contacts.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `properties: airbyte_agent_sdk.connectors.hubspot.types.ContactsCreateParamsProperties`
    :   The type of the None singleton.

<a id="ContactsCreateParamsProperties"></a>

`ContactsCreateParamsProperties(*args, **kwargs)`
:   Contact properties to set

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `company: str`
    :   The type of the None singleton.

    `email: str`
    :   The type of the None singleton.

    `firstname: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

    `jobtitle: str`
    :   The type of the None singleton.

    `lastname: str`
    :   The type of the None singleton.

    `lifecyclestage: str`
    :   The type of the None singleton.

    `phone: str`
    :   The type of the None singleton.

    `website: str`
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

<a id="ContactsUpdateParams"></a>

`ContactsUpdateParams(*args, **kwargs)`
:   Parameters for contacts.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contact_id: str`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.types.ContactsUpdateParamsProperties`
    :   The type of the None singleton.

<a id="ContactsUpdateParamsProperties"></a>

`ContactsUpdateParamsProperties(*args, **kwargs)`
:   Contact properties to update

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `company: str`
    :   The type of the None singleton.

    `email: str`
    :   The type of the None singleton.

    `firstname: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

    `jobtitle: str`
    :   The type of the None singleton.

    `lastname: str`
    :   The type of the None singleton.

    `lifecyclestage: str`
    :   The type of the None singleton.

    `phone: str`
    :   The type of the None singleton.

    `website: str`
    :   The type of the None singleton.

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

<a id="DealsCreateParams"></a>

`DealsCreateParams(*args, **kwargs)`
:   Parameters for deals.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `properties: airbyte_agent_sdk.connectors.hubspot.types.DealsCreateParamsProperties`
    :   The type of the None singleton.

<a id="DealsCreateParamsProperties"></a>

`DealsCreateParamsProperties(*args, **kwargs)`
:   Deal properties to set

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   The type of the None singleton.

    `closedate: str`
    :   The type of the None singleton.

    `dealname: str`
    :   The type of the None singleton.

    `dealstage: str`
    :   The type of the None singleton.

    `dealtype: str`
    :   The type of the None singleton.

    `description: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

    `pipeline: str`
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

<a id="DealsUpdateParams"></a>

`DealsUpdateParams(*args, **kwargs)`
:   Parameters for deals.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `deal_id: str`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.types.DealsUpdateParamsProperties`
    :   The type of the None singleton.

<a id="DealsUpdateParamsProperties"></a>

`DealsUpdateParamsProperties(*args, **kwargs)`
:   Deal properties to update

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   The type of the None singleton.

    `closedate: str`
    :   The type of the None singleton.

    `dealname: str`
    :   The type of the None singleton.

    `dealstage: str`
    :   The type of the None singleton.

    `dealtype: str`
    :   The type of the None singleton.

    `description: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

    `pipeline: str`
    :   The type of the None singleton.

<a id="EmailsAndCondition"></a>

`EmailsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.hubspot.types.EmailsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsInCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsAnyCondition]`
    :   The type of the None singleton.

<a id="EmailsAnyCondition"></a>

`EmailsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.hubspot.types.EmailsAnyValueFilter`
    :   The type of the None singleton.

<a id="EmailsAnyValueFilter"></a>

`EmailsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Indicates whether the email has been archived

    `created_at: Any`
    :   Timestamp when the email was created

    `id: Any`
    :   Unique identifier for the email record

    `properties: Any`
    :   Object containing all property values for the email

    `properties_hs_createdate: Any`
    :   Date the email was created

    `properties_hs_email_direction: Any`
    :   Direction of the email (EMAIL, INCOMING_EMAIL, FORWARDED_EMAIL)

    `properties_hs_email_status: Any`
    :   Status of the email (BOUNCED, FAILED, SCHEDULED, SENDING, SENT, DRAFT)

    `properties_hs_email_subject: Any`
    :   Subject line of the email

    `properties_hs_email_text: Any`
    :   Plain text body of the email

    `properties_hs_lastmodifieddate: Any`
    :   Last modified date of the email

    `properties_hs_object_id: Any`
    :   HubSpot object ID

    `properties_hs_timestamp: Any`
    :   Timestamp when the email activity occurred

    `properties_hubspot_owner_id: Any`
    :   ID of the email owner

    `updated_at: Any`
    :   Timestamp when the email record was last modified

<a id="EmailsContainsCondition"></a>

`EmailsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.hubspot.types.EmailsAnyValueFilter`
    :   The type of the None singleton.

<a id="EmailsCreateParams"></a>

`EmailsCreateParams(*args, **kwargs)`
:   Parameters for emails.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associations: list[airbyte_agent_sdk.connectors.hubspot.types.EmailsCreateParamsAssociationsItem]`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.types.EmailsCreateParamsProperties`
    :   The type of the None singleton.

<a id="EmailsCreateParamsAssociationsItem"></a>

`EmailsCreateParamsAssociationsItem(*args, **kwargs)`
:   Nested schema for EmailsCreateParams.associations_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `to: airbyte_agent_sdk.connectors.hubspot.types.EmailsCreateParamsAssociationsItemTo`
    :   The type of the None singleton.

    `types: list[airbyte_agent_sdk.connectors.hubspot.types.EmailsCreateParamsAssociationsItemTypesItem]`
    :   The type of the None singleton.

<a id="EmailsCreateParamsAssociationsItemTo"></a>

`EmailsCreateParamsAssociationsItemTo(*args, **kwargs)`
:   Nested schema for EmailsCreateParamsAssociationsItem.to

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="EmailsCreateParamsAssociationsItemTypesItem"></a>

`EmailsCreateParamsAssociationsItemTypesItem(*args, **kwargs)`
:   Nested schema for EmailsCreateParamsAssociationsItem.types_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associationCategory: str`
    :   The type of the None singleton.

    `associationTypeId: int`
    :   The type of the None singleton.

<a id="EmailsCreateParamsProperties"></a>

`EmailsCreateParamsProperties(*args, **kwargs)`
:   Email properties to set

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hs_email_direction: str`
    :   The type of the None singleton.

    `hs_email_html: str`
    :   The type of the None singleton.

    `hs_email_sender_email: str`
    :   The type of the None singleton.

    `hs_email_status: str`
    :   The type of the None singleton.

    `hs_email_subject: str`
    :   The type of the None singleton.

    `hs_email_text: str`
    :   The type of the None singleton.

    `hs_email_to_email: str`
    :   The type of the None singleton.

    `hs_timestamp: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

<a id="EmailsDeleteParams"></a>

`EmailsDeleteParams(*args, **kwargs)`
:   Parameters for emails.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email_id: str`
    :   The type of the None singleton.

<a id="EmailsEqCondition"></a>

`EmailsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.hubspot.types.EmailsSearchFilter`
    :   The type of the None singleton.

<a id="EmailsFuzzyCondition"></a>

`EmailsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.hubspot.types.EmailsStringFilter`
    :   The type of the None singleton.

<a id="EmailsGetParams"></a>

`EmailsGetParams(*args, **kwargs)`
:   Parameters for emails.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `associations: str`
    :   The type of the None singleton.

    `email_id: str`
    :   The type of the None singleton.

    `id_property: str`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `properties_with_history: str`
    :   The type of the None singleton.

<a id="EmailsGtCondition"></a>

`EmailsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.hubspot.types.EmailsSearchFilter`
    :   The type of the None singleton.

<a id="EmailsGteCondition"></a>

`EmailsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.hubspot.types.EmailsSearchFilter`
    :   The type of the None singleton.

<a id="EmailsInCondition"></a>

`EmailsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.hubspot.types.EmailsInFilter`
    :   The type of the None singleton.

<a id="EmailsInFilter"></a>

`EmailsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Indicates whether the email has been archived

    `created_at: list[str]`
    :   Timestamp when the email was created

    `id: list[str]`
    :   Unique identifier for the email record

    `properties: list[dict[str, typing.Any]]`
    :   Object containing all property values for the email

    `properties_hs_createdate: list[str]`
    :   Date the email was created

    `properties_hs_email_direction: list[str]`
    :   Direction of the email (EMAIL, INCOMING_EMAIL, FORWARDED_EMAIL)

    `properties_hs_email_status: list[str]`
    :   Status of the email (BOUNCED, FAILED, SCHEDULED, SENDING, SENT, DRAFT)

    `properties_hs_email_subject: list[str]`
    :   Subject line of the email

    `properties_hs_email_text: list[str]`
    :   Plain text body of the email

    `properties_hs_lastmodifieddate: list[str]`
    :   Last modified date of the email

    `properties_hs_object_id: list[str]`
    :   HubSpot object ID

    `properties_hs_timestamp: list[str]`
    :   Timestamp when the email activity occurred

    `properties_hubspot_owner_id: list[str]`
    :   ID of the email owner

    `updated_at: list[str]`
    :   Timestamp when the email record was last modified

<a id="EmailsKeywordCondition"></a>

`EmailsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.hubspot.types.EmailsStringFilter`
    :   The type of the None singleton.

<a id="EmailsLikeCondition"></a>

`EmailsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.hubspot.types.EmailsStringFilter`
    :   The type of the None singleton.

<a id="EmailsListParams"></a>

`EmailsListParams(*args, **kwargs)`
:   Parameters for emails.list operation

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

<a id="EmailsLtCondition"></a>

`EmailsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.hubspot.types.EmailsSearchFilter`
    :   The type of the None singleton.

<a id="EmailsLteCondition"></a>

`EmailsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.hubspot.types.EmailsSearchFilter`
    :   The type of the None singleton.

<a id="EmailsNeqCondition"></a>

`EmailsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.hubspot.types.EmailsSearchFilter`
    :   The type of the None singleton.

<a id="EmailsNotCondition"></a>

`EmailsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.hubspot.types.EmailsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsInCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsAnyCondition`
    :   The type of the None singleton.

<a id="EmailsOrCondition"></a>

`EmailsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.hubspot.types.EmailsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsInCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsAnyCondition]`
    :   The type of the None singleton.

<a id="EmailsSearchFilter"></a>

`EmailsSearchFilter(*args, **kwargs)`
:   Available fields for filtering emails search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the email has been archived

    `created_at: str | None`
    :   Timestamp when the email was created

    `id: str | None`
    :   Unique identifier for the email record

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the email

    `properties_hs_createdate: str | None`
    :   Date the email was created

    `properties_hs_email_direction: str | None`
    :   Direction of the email (EMAIL, INCOMING_EMAIL, FORWARDED_EMAIL)

    `properties_hs_email_status: str | None`
    :   Status of the email (BOUNCED, FAILED, SCHEDULED, SENDING, SENT, DRAFT)

    `properties_hs_email_subject: str | None`
    :   Subject line of the email

    `properties_hs_email_text: str | None`
    :   Plain text body of the email

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the email

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_timestamp: str | None`
    :   Timestamp when the email activity occurred

    `properties_hubspot_owner_id: str | None`
    :   ID of the email owner

    `updated_at: str | None`
    :   Timestamp when the email record was last modified

<a id="EmailsSearchQuery"></a>

`EmailsSearchQuery(*args, **kwargs)`
:   Search query for emails entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.hubspot.types.EmailsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsInCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.EmailsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.hubspot.types.EmailsSortFilter]`
    :   The type of the None singleton.

<a id="EmailsSortFilter"></a>

`EmailsSortFilter(*args, **kwargs)`
:   Available fields for sorting emails search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Indicates whether the email has been archived

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the email was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the email record

    `properties: Literal['asc', 'desc']`
    :   Object containing all property values for the email

    `properties_hs_createdate: Literal['asc', 'desc']`
    :   Date the email was created

    `properties_hs_email_direction: Literal['asc', 'desc']`
    :   Direction of the email (EMAIL, INCOMING_EMAIL, FORWARDED_EMAIL)

    `properties_hs_email_status: Literal['asc', 'desc']`
    :   Status of the email (BOUNCED, FAILED, SCHEDULED, SENDING, SENT, DRAFT)

    `properties_hs_email_subject: Literal['asc', 'desc']`
    :   Subject line of the email

    `properties_hs_email_text: Literal['asc', 'desc']`
    :   Plain text body of the email

    `properties_hs_lastmodifieddate: Literal['asc', 'desc']`
    :   Last modified date of the email

    `properties_hs_object_id: Literal['asc', 'desc']`
    :   HubSpot object ID

    `properties_hs_timestamp: Literal['asc', 'desc']`
    :   Timestamp when the email activity occurred

    `properties_hubspot_owner_id: Literal['asc', 'desc']`
    :   ID of the email owner

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the email record was last modified

<a id="EmailsStringFilter"></a>

`EmailsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Indicates whether the email has been archived

    `created_at: str`
    :   Timestamp when the email was created

    `id: str`
    :   Unique identifier for the email record

    `properties: str`
    :   Object containing all property values for the email

    `properties_hs_createdate: str`
    :   Date the email was created

    `properties_hs_email_direction: str`
    :   Direction of the email (EMAIL, INCOMING_EMAIL, FORWARDED_EMAIL)

    `properties_hs_email_status: str`
    :   Status of the email (BOUNCED, FAILED, SCHEDULED, SENDING, SENT, DRAFT)

    `properties_hs_email_subject: str`
    :   Subject line of the email

    `properties_hs_email_text: str`
    :   Plain text body of the email

    `properties_hs_lastmodifieddate: str`
    :   Last modified date of the email

    `properties_hs_object_id: str`
    :   HubSpot object ID

    `properties_hs_timestamp: str`
    :   Timestamp when the email activity occurred

    `properties_hubspot_owner_id: str`
    :   ID of the email owner

    `updated_at: str`
    :   Timestamp when the email record was last modified

<a id="EmailsUpdateParams"></a>

`EmailsUpdateParams(*args, **kwargs)`
:   Parameters for emails.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email_id: str`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.types.EmailsUpdateParamsProperties`
    :   The type of the None singleton.

<a id="EmailsUpdateParamsProperties"></a>

`EmailsUpdateParamsProperties(*args, **kwargs)`
:   Email properties to update

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hs_email_direction: str`
    :   The type of the None singleton.

    `hs_email_html: str`
    :   The type of the None singleton.

    `hs_email_status: str`
    :   The type of the None singleton.

    `hs_email_subject: str`
    :   The type of the None singleton.

    `hs_email_text: str`
    :   The type of the None singleton.

    `hs_timestamp: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

<a id="MeetingsAndCondition"></a>

`MeetingsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.hubspot.types.MeetingsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsInCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsAnyCondition]`
    :   The type of the None singleton.

<a id="MeetingsAnyCondition"></a>

`MeetingsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.hubspot.types.MeetingsAnyValueFilter`
    :   The type of the None singleton.

<a id="MeetingsAnyValueFilter"></a>

`MeetingsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Indicates whether the meeting has been archived

    `created_at: Any`
    :   Timestamp when the meeting was created

    `id: Any`
    :   Unique identifier for the meeting record

    `properties: Any`
    :   Object containing all property values for the meeting

    `properties_hs_createdate: Any`
    :   Date the meeting was created

    `properties_hs_lastmodifieddate: Any`
    :   Last modified date of the meeting

    `properties_hs_meeting_body: Any`
    :   Description or notes about the meeting

    `properties_hs_meeting_end_time: Any`
    :   End time of the meeting

    `properties_hs_meeting_location: Any`
    :   Location of the meeting

    `properties_hs_meeting_outcome: Any`
    :   Outcome of the meeting (e.g., SCHEDULED, COMPLETED, NO_SHOW, CANCELED)

    `properties_hs_meeting_start_time: Any`
    :   Start time of the meeting

    `properties_hs_meeting_title: Any`
    :   Title of the meeting

    `properties_hs_object_id: Any`
    :   HubSpot object ID

    `properties_hs_timestamp: Any`
    :   Timestamp when the meeting activity occurred

    `properties_hubspot_owner_id: Any`
    :   ID of the meeting owner

    `updated_at: Any`
    :   Timestamp when the meeting record was last modified

<a id="MeetingsContainsCondition"></a>

`MeetingsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.hubspot.types.MeetingsAnyValueFilter`
    :   The type of the None singleton.

<a id="MeetingsCreateParams"></a>

`MeetingsCreateParams(*args, **kwargs)`
:   Parameters for meetings.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associations: list[airbyte_agent_sdk.connectors.hubspot.types.MeetingsCreateParamsAssociationsItem]`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.types.MeetingsCreateParamsProperties`
    :   The type of the None singleton.

<a id="MeetingsCreateParamsAssociationsItem"></a>

`MeetingsCreateParamsAssociationsItem(*args, **kwargs)`
:   Nested schema for MeetingsCreateParams.associations_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `to: airbyte_agent_sdk.connectors.hubspot.types.MeetingsCreateParamsAssociationsItemTo`
    :   The type of the None singleton.

    `types: list[airbyte_agent_sdk.connectors.hubspot.types.MeetingsCreateParamsAssociationsItemTypesItem]`
    :   The type of the None singleton.

<a id="MeetingsCreateParamsAssociationsItemTo"></a>

`MeetingsCreateParamsAssociationsItemTo(*args, **kwargs)`
:   Nested schema for MeetingsCreateParamsAssociationsItem.to

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="MeetingsCreateParamsAssociationsItemTypesItem"></a>

`MeetingsCreateParamsAssociationsItemTypesItem(*args, **kwargs)`
:   Nested schema for MeetingsCreateParamsAssociationsItem.types_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associationCategory: str`
    :   The type of the None singleton.

    `associationTypeId: int`
    :   The type of the None singleton.

<a id="MeetingsCreateParamsProperties"></a>

`MeetingsCreateParamsProperties(*args, **kwargs)`
:   Meeting properties to set

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hs_internal_meeting_notes: str`
    :   The type of the None singleton.

    `hs_meeting_body: str`
    :   The type of the None singleton.

    `hs_meeting_end_time: str`
    :   The type of the None singleton.

    `hs_meeting_location: str`
    :   The type of the None singleton.

    `hs_meeting_outcome: str`
    :   The type of the None singleton.

    `hs_meeting_start_time: str`
    :   The type of the None singleton.

    `hs_meeting_title: str`
    :   The type of the None singleton.

    `hs_timestamp: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

<a id="MeetingsDeleteParams"></a>

`MeetingsDeleteParams(*args, **kwargs)`
:   Parameters for meetings.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `meeting_id: str`
    :   The type of the None singleton.

<a id="MeetingsEqCondition"></a>

`MeetingsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.hubspot.types.MeetingsSearchFilter`
    :   The type of the None singleton.

<a id="MeetingsFuzzyCondition"></a>

`MeetingsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.hubspot.types.MeetingsStringFilter`
    :   The type of the None singleton.

<a id="MeetingsGetParams"></a>

`MeetingsGetParams(*args, **kwargs)`
:   Parameters for meetings.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `associations: str`
    :   The type of the None singleton.

    `id_property: str`
    :   The type of the None singleton.

    `meeting_id: str`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `properties_with_history: str`
    :   The type of the None singleton.

<a id="MeetingsGtCondition"></a>

`MeetingsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.hubspot.types.MeetingsSearchFilter`
    :   The type of the None singleton.

<a id="MeetingsGteCondition"></a>

`MeetingsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.hubspot.types.MeetingsSearchFilter`
    :   The type of the None singleton.

<a id="MeetingsInCondition"></a>

`MeetingsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.hubspot.types.MeetingsInFilter`
    :   The type of the None singleton.

<a id="MeetingsInFilter"></a>

`MeetingsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Indicates whether the meeting has been archived

    `created_at: list[str]`
    :   Timestamp when the meeting was created

    `id: list[str]`
    :   Unique identifier for the meeting record

    `properties: list[dict[str, typing.Any]]`
    :   Object containing all property values for the meeting

    `properties_hs_createdate: list[str]`
    :   Date the meeting was created

    `properties_hs_lastmodifieddate: list[str]`
    :   Last modified date of the meeting

    `properties_hs_meeting_body: list[str]`
    :   Description or notes about the meeting

    `properties_hs_meeting_end_time: list[str]`
    :   End time of the meeting

    `properties_hs_meeting_location: list[str]`
    :   Location of the meeting

    `properties_hs_meeting_outcome: list[str]`
    :   Outcome of the meeting (e.g., SCHEDULED, COMPLETED, NO_SHOW, CANCELED)

    `properties_hs_meeting_start_time: list[str]`
    :   Start time of the meeting

    `properties_hs_meeting_title: list[str]`
    :   Title of the meeting

    `properties_hs_object_id: list[str]`
    :   HubSpot object ID

    `properties_hs_timestamp: list[str]`
    :   Timestamp when the meeting activity occurred

    `properties_hubspot_owner_id: list[str]`
    :   ID of the meeting owner

    `updated_at: list[str]`
    :   Timestamp when the meeting record was last modified

<a id="MeetingsKeywordCondition"></a>

`MeetingsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.hubspot.types.MeetingsStringFilter`
    :   The type of the None singleton.

<a id="MeetingsLikeCondition"></a>

`MeetingsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.hubspot.types.MeetingsStringFilter`
    :   The type of the None singleton.

<a id="MeetingsListParams"></a>

`MeetingsListParams(*args, **kwargs)`
:   Parameters for meetings.list operation

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

<a id="MeetingsLtCondition"></a>

`MeetingsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.hubspot.types.MeetingsSearchFilter`
    :   The type of the None singleton.

<a id="MeetingsLteCondition"></a>

`MeetingsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.hubspot.types.MeetingsSearchFilter`
    :   The type of the None singleton.

<a id="MeetingsNeqCondition"></a>

`MeetingsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.hubspot.types.MeetingsSearchFilter`
    :   The type of the None singleton.

<a id="MeetingsNotCondition"></a>

`MeetingsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.hubspot.types.MeetingsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsInCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsAnyCondition`
    :   The type of the None singleton.

<a id="MeetingsOrCondition"></a>

`MeetingsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.hubspot.types.MeetingsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsInCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsAnyCondition]`
    :   The type of the None singleton.

<a id="MeetingsSearchFilter"></a>

`MeetingsSearchFilter(*args, **kwargs)`
:   Available fields for filtering meetings search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the meeting has been archived

    `created_at: str | None`
    :   Timestamp when the meeting was created

    `id: str | None`
    :   Unique identifier for the meeting record

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the meeting

    `properties_hs_createdate: str | None`
    :   Date the meeting was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the meeting

    `properties_hs_meeting_body: str | None`
    :   Description or notes about the meeting

    `properties_hs_meeting_end_time: str | None`
    :   End time of the meeting

    `properties_hs_meeting_location: str | None`
    :   Location of the meeting

    `properties_hs_meeting_outcome: str | None`
    :   Outcome of the meeting (e.g., SCHEDULED, COMPLETED, NO_SHOW, CANCELED)

    `properties_hs_meeting_start_time: str | None`
    :   Start time of the meeting

    `properties_hs_meeting_title: str | None`
    :   Title of the meeting

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_timestamp: str | None`
    :   Timestamp when the meeting activity occurred

    `properties_hubspot_owner_id: str | None`
    :   ID of the meeting owner

    `updated_at: str | None`
    :   Timestamp when the meeting record was last modified

<a id="MeetingsSearchQuery"></a>

`MeetingsSearchQuery(*args, **kwargs)`
:   Search query for meetings entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.hubspot.types.MeetingsEqCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsGtCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsGteCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsLtCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsLteCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsInCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsNotCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsAndCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsOrCondition | airbyte_agent_sdk.connectors.hubspot.types.MeetingsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.hubspot.types.MeetingsSortFilter]`
    :   The type of the None singleton.

<a id="MeetingsSortFilter"></a>

`MeetingsSortFilter(*args, **kwargs)`
:   Available fields for sorting meetings search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Indicates whether the meeting has been archived

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the meeting was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the meeting record

    `properties: Literal['asc', 'desc']`
    :   Object containing all property values for the meeting

    `properties_hs_createdate: Literal['asc', 'desc']`
    :   Date the meeting was created

    `properties_hs_lastmodifieddate: Literal['asc', 'desc']`
    :   Last modified date of the meeting

    `properties_hs_meeting_body: Literal['asc', 'desc']`
    :   Description or notes about the meeting

    `properties_hs_meeting_end_time: Literal['asc', 'desc']`
    :   End time of the meeting

    `properties_hs_meeting_location: Literal['asc', 'desc']`
    :   Location of the meeting

    `properties_hs_meeting_outcome: Literal['asc', 'desc']`
    :   Outcome of the meeting (e.g., SCHEDULED, COMPLETED, NO_SHOW, CANCELED)

    `properties_hs_meeting_start_time: Literal['asc', 'desc']`
    :   Start time of the meeting

    `properties_hs_meeting_title: Literal['asc', 'desc']`
    :   Title of the meeting

    `properties_hs_object_id: Literal['asc', 'desc']`
    :   HubSpot object ID

    `properties_hs_timestamp: Literal['asc', 'desc']`
    :   Timestamp when the meeting activity occurred

    `properties_hubspot_owner_id: Literal['asc', 'desc']`
    :   ID of the meeting owner

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the meeting record was last modified

<a id="MeetingsStringFilter"></a>

`MeetingsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Indicates whether the meeting has been archived

    `created_at: str`
    :   Timestamp when the meeting was created

    `id: str`
    :   Unique identifier for the meeting record

    `properties: str`
    :   Object containing all property values for the meeting

    `properties_hs_createdate: str`
    :   Date the meeting was created

    `properties_hs_lastmodifieddate: str`
    :   Last modified date of the meeting

    `properties_hs_meeting_body: str`
    :   Description or notes about the meeting

    `properties_hs_meeting_end_time: str`
    :   End time of the meeting

    `properties_hs_meeting_location: str`
    :   Location of the meeting

    `properties_hs_meeting_outcome: str`
    :   Outcome of the meeting (e.g., SCHEDULED, COMPLETED, NO_SHOW, CANCELED)

    `properties_hs_meeting_start_time: str`
    :   Start time of the meeting

    `properties_hs_meeting_title: str`
    :   Title of the meeting

    `properties_hs_object_id: str`
    :   HubSpot object ID

    `properties_hs_timestamp: str`
    :   Timestamp when the meeting activity occurred

    `properties_hubspot_owner_id: str`
    :   ID of the meeting owner

    `updated_at: str`
    :   Timestamp when the meeting record was last modified

<a id="MeetingsUpdateParams"></a>

`MeetingsUpdateParams(*args, **kwargs)`
:   Parameters for meetings.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `meeting_id: str`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.types.MeetingsUpdateParamsProperties`
    :   The type of the None singleton.

<a id="MeetingsUpdateParamsProperties"></a>

`MeetingsUpdateParamsProperties(*args, **kwargs)`
:   Meeting properties to update

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hs_internal_meeting_notes: str`
    :   The type of the None singleton.

    `hs_meeting_body: str`
    :   The type of the None singleton.

    `hs_meeting_end_time: str`
    :   The type of the None singleton.

    `hs_meeting_location: str`
    :   The type of the None singleton.

    `hs_meeting_outcome: str`
    :   The type of the None singleton.

    `hs_meeting_start_time: str`
    :   The type of the None singleton.

    `hs_meeting_title: str`
    :   The type of the None singleton.

    `hs_timestamp: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

<a id="NotesAndCondition"></a>

`NotesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.hubspot.types.NotesEqCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesGtCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesGteCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesLtCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesLteCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesInCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesNotCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesAndCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesOrCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesAnyCondition]`
    :   The type of the None singleton.

<a id="NotesAnyCondition"></a>

`NotesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.hubspot.types.NotesAnyValueFilter`
    :   The type of the None singleton.

<a id="NotesAnyValueFilter"></a>

`NotesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Indicates whether the note has been archived

    `created_at: Any`
    :   Timestamp when the note was created

    `id: Any`
    :   Unique identifier for the note record

    `properties: Any`
    :   Object containing all property values for the note

    `properties_hs_createdate: Any`
    :   Date the note was created

    `properties_hs_lastmodifieddate: Any`
    :   Last modified date of the note

    `properties_hs_note_body: Any`
    :   The body content of the note (supports HTML)

    `properties_hs_object_id: Any`
    :   HubSpot object ID

    `properties_hs_timestamp: Any`
    :   Timestamp when the note activity occurred

    `properties_hubspot_owner_id: Any`
    :   ID of the note owner

    `updated_at: Any`
    :   Timestamp when the note record was last modified

<a id="NotesContainsCondition"></a>

`NotesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.hubspot.types.NotesAnyValueFilter`
    :   The type of the None singleton.

<a id="NotesCreateParams"></a>

`NotesCreateParams(*args, **kwargs)`
:   Parameters for notes.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associations: list[airbyte_agent_sdk.connectors.hubspot.types.NotesCreateParamsAssociationsItem]`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.types.NotesCreateParamsProperties`
    :   The type of the None singleton.

<a id="NotesCreateParamsAssociationsItem"></a>

`NotesCreateParamsAssociationsItem(*args, **kwargs)`
:   Nested schema for NotesCreateParams.associations_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `to: airbyte_agent_sdk.connectors.hubspot.types.NotesCreateParamsAssociationsItemTo`
    :   The type of the None singleton.

    `types: list[airbyte_agent_sdk.connectors.hubspot.types.NotesCreateParamsAssociationsItemTypesItem]`
    :   The type of the None singleton.

<a id="NotesCreateParamsAssociationsItemTo"></a>

`NotesCreateParamsAssociationsItemTo(*args, **kwargs)`
:   Nested schema for NotesCreateParamsAssociationsItem.to

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="NotesCreateParamsAssociationsItemTypesItem"></a>

`NotesCreateParamsAssociationsItemTypesItem(*args, **kwargs)`
:   Nested schema for NotesCreateParamsAssociationsItem.types_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associationCategory: str`
    :   The type of the None singleton.

    `associationTypeId: int`
    :   The type of the None singleton.

<a id="NotesCreateParamsProperties"></a>

`NotesCreateParamsProperties(*args, **kwargs)`
:   Note properties to set

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hs_note_body: str`
    :   The type of the None singleton.

    `hs_timestamp: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

<a id="NotesDeleteParams"></a>

`NotesDeleteParams(*args, **kwargs)`
:   Parameters for notes.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `note_id: str`
    :   The type of the None singleton.

<a id="NotesEqCondition"></a>

`NotesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.hubspot.types.NotesSearchFilter`
    :   The type of the None singleton.

<a id="NotesFuzzyCondition"></a>

`NotesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.hubspot.types.NotesStringFilter`
    :   The type of the None singleton.

<a id="NotesGetParams"></a>

`NotesGetParams(*args, **kwargs)`
:   Parameters for notes.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `associations: str`
    :   The type of the None singleton.

    `id_property: str`
    :   The type of the None singleton.

    `note_id: str`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `properties_with_history: str`
    :   The type of the None singleton.

<a id="NotesGtCondition"></a>

`NotesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.hubspot.types.NotesSearchFilter`
    :   The type of the None singleton.

<a id="NotesGteCondition"></a>

`NotesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.hubspot.types.NotesSearchFilter`
    :   The type of the None singleton.

<a id="NotesInCondition"></a>

`NotesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.hubspot.types.NotesInFilter`
    :   The type of the None singleton.

<a id="NotesInFilter"></a>

`NotesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Indicates whether the note has been archived

    `created_at: list[str]`
    :   Timestamp when the note was created

    `id: list[str]`
    :   Unique identifier for the note record

    `properties: list[dict[str, typing.Any]]`
    :   Object containing all property values for the note

    `properties_hs_createdate: list[str]`
    :   Date the note was created

    `properties_hs_lastmodifieddate: list[str]`
    :   Last modified date of the note

    `properties_hs_note_body: list[str]`
    :   The body content of the note (supports HTML)

    `properties_hs_object_id: list[str]`
    :   HubSpot object ID

    `properties_hs_timestamp: list[str]`
    :   Timestamp when the note activity occurred

    `properties_hubspot_owner_id: list[str]`
    :   ID of the note owner

    `updated_at: list[str]`
    :   Timestamp when the note record was last modified

<a id="NotesKeywordCondition"></a>

`NotesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.hubspot.types.NotesStringFilter`
    :   The type of the None singleton.

<a id="NotesLikeCondition"></a>

`NotesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.hubspot.types.NotesStringFilter`
    :   The type of the None singleton.

<a id="NotesListParams"></a>

`NotesListParams(*args, **kwargs)`
:   Parameters for notes.list operation

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

<a id="NotesLtCondition"></a>

`NotesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.hubspot.types.NotesSearchFilter`
    :   The type of the None singleton.

<a id="NotesLteCondition"></a>

`NotesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.hubspot.types.NotesSearchFilter`
    :   The type of the None singleton.

<a id="NotesNeqCondition"></a>

`NotesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.hubspot.types.NotesSearchFilter`
    :   The type of the None singleton.

<a id="NotesNotCondition"></a>

`NotesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.hubspot.types.NotesEqCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesGtCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesGteCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesLtCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesLteCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesInCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesNotCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesAndCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesOrCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesAnyCondition`
    :   The type of the None singleton.

<a id="NotesOrCondition"></a>

`NotesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.hubspot.types.NotesEqCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesGtCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesGteCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesLtCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesLteCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesInCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesNotCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesAndCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesOrCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesAnyCondition]`
    :   The type of the None singleton.

<a id="NotesSearchFilter"></a>

`NotesSearchFilter(*args, **kwargs)`
:   Available fields for filtering notes search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the note has been archived

    `created_at: str | None`
    :   Timestamp when the note was created

    `id: str | None`
    :   Unique identifier for the note record

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the note

    `properties_hs_createdate: str | None`
    :   Date the note was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the note

    `properties_hs_note_body: str | None`
    :   The body content of the note (supports HTML)

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_timestamp: str | None`
    :   Timestamp when the note activity occurred

    `properties_hubspot_owner_id: str | None`
    :   ID of the note owner

    `updated_at: str | None`
    :   Timestamp when the note record was last modified

<a id="NotesSearchQuery"></a>

`NotesSearchQuery(*args, **kwargs)`
:   Search query for notes entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.hubspot.types.NotesEqCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesGtCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesGteCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesLtCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesLteCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesInCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesNotCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesAndCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesOrCondition | airbyte_agent_sdk.connectors.hubspot.types.NotesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.hubspot.types.NotesSortFilter]`
    :   The type of the None singleton.

<a id="NotesSortFilter"></a>

`NotesSortFilter(*args, **kwargs)`
:   Available fields for sorting notes search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Indicates whether the note has been archived

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the note was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the note record

    `properties: Literal['asc', 'desc']`
    :   Object containing all property values for the note

    `properties_hs_createdate: Literal['asc', 'desc']`
    :   Date the note was created

    `properties_hs_lastmodifieddate: Literal['asc', 'desc']`
    :   Last modified date of the note

    `properties_hs_note_body: Literal['asc', 'desc']`
    :   The body content of the note (supports HTML)

    `properties_hs_object_id: Literal['asc', 'desc']`
    :   HubSpot object ID

    `properties_hs_timestamp: Literal['asc', 'desc']`
    :   Timestamp when the note activity occurred

    `properties_hubspot_owner_id: Literal['asc', 'desc']`
    :   ID of the note owner

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the note record was last modified

<a id="NotesStringFilter"></a>

`NotesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Indicates whether the note has been archived

    `created_at: str`
    :   Timestamp when the note was created

    `id: str`
    :   Unique identifier for the note record

    `properties: str`
    :   Object containing all property values for the note

    `properties_hs_createdate: str`
    :   Date the note was created

    `properties_hs_lastmodifieddate: str`
    :   Last modified date of the note

    `properties_hs_note_body: str`
    :   The body content of the note (supports HTML)

    `properties_hs_object_id: str`
    :   HubSpot object ID

    `properties_hs_timestamp: str`
    :   Timestamp when the note activity occurred

    `properties_hubspot_owner_id: str`
    :   ID of the note owner

    `updated_at: str`
    :   Timestamp when the note record was last modified

<a id="NotesUpdateParams"></a>

`NotesUpdateParams(*args, **kwargs)`
:   Parameters for notes.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `note_id: str`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.types.NotesUpdateParamsProperties`
    :   The type of the None singleton.

<a id="NotesUpdateParamsProperties"></a>

`NotesUpdateParamsProperties(*args, **kwargs)`
:   Note properties to update

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hs_note_body: str`
    :   The type of the None singleton.

    `hs_timestamp: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

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

<a id="TasksAndCondition"></a>

`TasksAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.hubspot.types.TasksEqCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksGtCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksGteCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksLtCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksLteCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksInCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksNotCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksAndCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksOrCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksAnyCondition]`
    :   The type of the None singleton.

<a id="TasksAnyCondition"></a>

`TasksAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.hubspot.types.TasksAnyValueFilter`
    :   The type of the None singleton.

<a id="TasksAnyValueFilter"></a>

`TasksAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Indicates whether the task has been archived

    `created_at: Any`
    :   Timestamp when the task was created

    `id: Any`
    :   Unique identifier for the task record

    `properties: Any`
    :   Object containing all property values for the task

    `properties_hs_createdate: Any`
    :   Date the task was created

    `properties_hs_lastmodifieddate: Any`
    :   Last modified date of the task

    `properties_hs_object_id: Any`
    :   HubSpot object ID

    `properties_hs_task_body: Any`
    :   Description or notes for the task

    `properties_hs_task_priority: Any`
    :   Priority of the task (LOW, MEDIUM, HIGH)

    `properties_hs_task_status: Any`
    :   Status of the task (NOT_STARTED, IN_PROGRESS, WAITING, COMPLETED, DEFERRED)

    `properties_hs_task_subject: Any`
    :   Subject or title of the task

    `properties_hs_task_type: Any`
    :   Type of the task (TODO, CALL, EMAIL)

    `properties_hs_timestamp: Any`
    :   Due date / timestamp for the task

    `properties_hubspot_owner_id: Any`
    :   ID of the task owner

    `updated_at: Any`
    :   Timestamp when the task record was last modified

<a id="TasksContainsCondition"></a>

`TasksContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.hubspot.types.TasksAnyValueFilter`
    :   The type of the None singleton.

<a id="TasksCreateParams"></a>

`TasksCreateParams(*args, **kwargs)`
:   Parameters for tasks.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associations: list[airbyte_agent_sdk.connectors.hubspot.types.TasksCreateParamsAssociationsItem]`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.types.TasksCreateParamsProperties`
    :   The type of the None singleton.

<a id="TasksCreateParamsAssociationsItem"></a>

`TasksCreateParamsAssociationsItem(*args, **kwargs)`
:   Nested schema for TasksCreateParams.associations_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `to: airbyte_agent_sdk.connectors.hubspot.types.TasksCreateParamsAssociationsItemTo`
    :   The type of the None singleton.

    `types: list[airbyte_agent_sdk.connectors.hubspot.types.TasksCreateParamsAssociationsItemTypesItem]`
    :   The type of the None singleton.

<a id="TasksCreateParamsAssociationsItemTo"></a>

`TasksCreateParamsAssociationsItemTo(*args, **kwargs)`
:   Nested schema for TasksCreateParamsAssociationsItem.to

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="TasksCreateParamsAssociationsItemTypesItem"></a>

`TasksCreateParamsAssociationsItemTypesItem(*args, **kwargs)`
:   Nested schema for TasksCreateParamsAssociationsItem.types_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associationCategory: str`
    :   The type of the None singleton.

    `associationTypeId: int`
    :   The type of the None singleton.

<a id="TasksCreateParamsProperties"></a>

`TasksCreateParamsProperties(*args, **kwargs)`
:   Task properties to set

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hs_task_body: str`
    :   The type of the None singleton.

    `hs_task_priority: str`
    :   The type of the None singleton.

    `hs_task_reminders: str`
    :   The type of the None singleton.

    `hs_task_status: str`
    :   The type of the None singleton.

    `hs_task_subject: str`
    :   The type of the None singleton.

    `hs_task_type: str`
    :   The type of the None singleton.

    `hs_timestamp: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

<a id="TasksDeleteParams"></a>

`TasksDeleteParams(*args, **kwargs)`
:   Parameters for tasks.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `task_id: str`
    :   The type of the None singleton.

<a id="TasksEqCondition"></a>

`TasksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.hubspot.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksFuzzyCondition"></a>

`TasksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.hubspot.types.TasksStringFilter`
    :   The type of the None singleton.

<a id="TasksGetParams"></a>

`TasksGetParams(*args, **kwargs)`
:   Parameters for tasks.get operation

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

    `task_id: str`
    :   The type of the None singleton.

<a id="TasksGtCondition"></a>

`TasksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.hubspot.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksGteCondition"></a>

`TasksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.hubspot.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksInCondition"></a>

`TasksInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.hubspot.types.TasksInFilter`
    :   The type of the None singleton.

<a id="TasksInFilter"></a>

`TasksInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Indicates whether the task has been archived

    `created_at: list[str]`
    :   Timestamp when the task was created

    `id: list[str]`
    :   Unique identifier for the task record

    `properties: list[dict[str, typing.Any]]`
    :   Object containing all property values for the task

    `properties_hs_createdate: list[str]`
    :   Date the task was created

    `properties_hs_lastmodifieddate: list[str]`
    :   Last modified date of the task

    `properties_hs_object_id: list[str]`
    :   HubSpot object ID

    `properties_hs_task_body: list[str]`
    :   Description or notes for the task

    `properties_hs_task_priority: list[str]`
    :   Priority of the task (LOW, MEDIUM, HIGH)

    `properties_hs_task_status: list[str]`
    :   Status of the task (NOT_STARTED, IN_PROGRESS, WAITING, COMPLETED, DEFERRED)

    `properties_hs_task_subject: list[str]`
    :   Subject or title of the task

    `properties_hs_task_type: list[str]`
    :   Type of the task (TODO, CALL, EMAIL)

    `properties_hs_timestamp: list[str]`
    :   Due date / timestamp for the task

    `properties_hubspot_owner_id: list[str]`
    :   ID of the task owner

    `updated_at: list[str]`
    :   Timestamp when the task record was last modified

<a id="TasksKeywordCondition"></a>

`TasksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.hubspot.types.TasksStringFilter`
    :   The type of the None singleton.

<a id="TasksLikeCondition"></a>

`TasksLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.hubspot.types.TasksStringFilter`
    :   The type of the None singleton.

<a id="TasksListParams"></a>

`TasksListParams(*args, **kwargs)`
:   Parameters for tasks.list operation

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

<a id="TasksLtCondition"></a>

`TasksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.hubspot.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksLteCondition"></a>

`TasksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.hubspot.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksNeqCondition"></a>

`TasksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.hubspot.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksNotCondition"></a>

`TasksNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.hubspot.types.TasksEqCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksGtCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksGteCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksLtCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksLteCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksInCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksNotCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksAndCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksOrCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksAnyCondition`
    :   The type of the None singleton.

<a id="TasksOrCondition"></a>

`TasksOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.hubspot.types.TasksEqCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksGtCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksGteCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksLtCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksLteCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksInCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksNotCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksAndCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksOrCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksAnyCondition]`
    :   The type of the None singleton.

<a id="TasksSearchFilter"></a>

`TasksSearchFilter(*args, **kwargs)`
:   Available fields for filtering tasks search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the task has been archived

    `created_at: str | None`
    :   Timestamp when the task was created

    `id: str | None`
    :   Unique identifier for the task record

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the task

    `properties_hs_createdate: str | None`
    :   Date the task was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the task

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_task_body: str | None`
    :   Description or notes for the task

    `properties_hs_task_priority: str | None`
    :   Priority of the task (LOW, MEDIUM, HIGH)

    `properties_hs_task_status: str | None`
    :   Status of the task (NOT_STARTED, IN_PROGRESS, WAITING, COMPLETED, DEFERRED)

    `properties_hs_task_subject: str | None`
    :   Subject or title of the task

    `properties_hs_task_type: str | None`
    :   Type of the task (TODO, CALL, EMAIL)

    `properties_hs_timestamp: str | None`
    :   Due date / timestamp for the task

    `properties_hubspot_owner_id: str | None`
    :   ID of the task owner

    `updated_at: str | None`
    :   Timestamp when the task record was last modified

<a id="TasksSearchQuery"></a>

`TasksSearchQuery(*args, **kwargs)`
:   Search query for tasks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.hubspot.types.TasksEqCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksNeqCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksGtCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksGteCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksLtCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksLteCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksInCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksLikeCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksContainsCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksNotCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksAndCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksOrCondition | airbyte_agent_sdk.connectors.hubspot.types.TasksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.hubspot.types.TasksSortFilter]`
    :   The type of the None singleton.

<a id="TasksSortFilter"></a>

`TasksSortFilter(*args, **kwargs)`
:   Available fields for sorting tasks search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Indicates whether the task has been archived

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the task was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the task record

    `properties: Literal['asc', 'desc']`
    :   Object containing all property values for the task

    `properties_hs_createdate: Literal['asc', 'desc']`
    :   Date the task was created

    `properties_hs_lastmodifieddate: Literal['asc', 'desc']`
    :   Last modified date of the task

    `properties_hs_object_id: Literal['asc', 'desc']`
    :   HubSpot object ID

    `properties_hs_task_body: Literal['asc', 'desc']`
    :   Description or notes for the task

    `properties_hs_task_priority: Literal['asc', 'desc']`
    :   Priority of the task (LOW, MEDIUM, HIGH)

    `properties_hs_task_status: Literal['asc', 'desc']`
    :   Status of the task (NOT_STARTED, IN_PROGRESS, WAITING, COMPLETED, DEFERRED)

    `properties_hs_task_subject: Literal['asc', 'desc']`
    :   Subject or title of the task

    `properties_hs_task_type: Literal['asc', 'desc']`
    :   Type of the task (TODO, CALL, EMAIL)

    `properties_hs_timestamp: Literal['asc', 'desc']`
    :   Due date / timestamp for the task

    `properties_hubspot_owner_id: Literal['asc', 'desc']`
    :   ID of the task owner

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the task record was last modified

<a id="TasksStringFilter"></a>

`TasksStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Indicates whether the task has been archived

    `created_at: str`
    :   Timestamp when the task was created

    `id: str`
    :   Unique identifier for the task record

    `properties: str`
    :   Object containing all property values for the task

    `properties_hs_createdate: str`
    :   Date the task was created

    `properties_hs_lastmodifieddate: str`
    :   Last modified date of the task

    `properties_hs_object_id: str`
    :   HubSpot object ID

    `properties_hs_task_body: str`
    :   Description or notes for the task

    `properties_hs_task_priority: str`
    :   Priority of the task (LOW, MEDIUM, HIGH)

    `properties_hs_task_status: str`
    :   Status of the task (NOT_STARTED, IN_PROGRESS, WAITING, COMPLETED, DEFERRED)

    `properties_hs_task_subject: str`
    :   Subject or title of the task

    `properties_hs_task_type: str`
    :   Type of the task (TODO, CALL, EMAIL)

    `properties_hs_timestamp: str`
    :   Due date / timestamp for the task

    `properties_hubspot_owner_id: str`
    :   ID of the task owner

    `updated_at: str`
    :   Timestamp when the task record was last modified

<a id="TasksUpdateParams"></a>

`TasksUpdateParams(*args, **kwargs)`
:   Parameters for tasks.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `properties: airbyte_agent_sdk.connectors.hubspot.types.TasksUpdateParamsProperties`
    :   The type of the None singleton.

    `task_id: str`
    :   The type of the None singleton.

<a id="TasksUpdateParamsProperties"></a>

`TasksUpdateParamsProperties(*args, **kwargs)`
:   Task properties to update

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hs_task_body: str`
    :   The type of the None singleton.

    `hs_task_priority: str`
    :   The type of the None singleton.

    `hs_task_reminders: str`
    :   The type of the None singleton.

    `hs_task_status: str`
    :   The type of the None singleton.

    `hs_task_subject: str`
    :   The type of the None singleton.

    `hs_task_type: str`
    :   The type of the None singleton.

    `hs_timestamp: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
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

<a id="TicketsCreateParams"></a>

`TicketsCreateParams(*args, **kwargs)`
:   Parameters for tickets.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `properties: airbyte_agent_sdk.connectors.hubspot.types.TicketsCreateParamsProperties`
    :   The type of the None singleton.

<a id="TicketsCreateParamsProperties"></a>

`TicketsCreateParamsProperties(*args, **kwargs)`
:   Ticket properties to set

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `hs_pipeline: str`
    :   The type of the None singleton.

    `hs_pipeline_stage: str`
    :   The type of the None singleton.

    `hs_ticket_category: str`
    :   The type of the None singleton.

    `hs_ticket_priority: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

    `subject: str`
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

<a id="TicketsUpdateParams"></a>

`TicketsUpdateParams(*args, **kwargs)`
:   Parameters for tickets.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `properties: airbyte_agent_sdk.connectors.hubspot.types.TicketsUpdateParamsProperties`
    :   The type of the None singleton.

    `ticket_id: str`
    :   The type of the None singleton.

<a id="TicketsUpdateParamsProperties"></a>

`TicketsUpdateParamsProperties(*args, **kwargs)`
:   Ticket properties to update

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `hs_pipeline: str`
    :   The type of the None singleton.

    `hs_pipeline_stage: str`
    :   The type of the None singleton.

    `hs_ticket_category: str`
    :   The type of the None singleton.

    `hs_ticket_priority: str`
    :   The type of the None singleton.

    `hubspot_owner_id: str`
    :   The type of the None singleton.

    `subject: str`
    :   The type of the None singleton.