---
id: airbyte_agent_sdk-connectors-zoho_crm-types
title: airbyte_agent_sdk.connectors.zoho_crm.types
---

Module airbyte_agent_sdk.connectors.zoho_crm.types
==================================================
Type definitions for zoho-crm connector.

Classes
-------

`AccountsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zoho_crm.types.AccountsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsAnyCondition]`
    :   The type of the None singleton.

`AccountsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zoho_crm.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

`AccountsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_name: Any`
    :   Name of the account or company

    `account_number: Any`
    :   Account number

    `account_type: Any`
    :   Type of account (e.g., Analyst, Competitor, Customer)

    `annual_revenue: Any`
    :   Annual revenue of the account

    `billing_city: Any`
    :   Billing address city

    `billing_country: Any`
    :   Billing address country

    `billing_state: Any`
    :   Billing address state or province

    `created_time: Any`
    :   Time the record was created

    `description: Any`
    :   Description or notes about the account

    `employees: Any`
    :   Number of employees

    `id: Any`
    :   Unique record identifier

    `industry: Any`
    :   Industry the account belongs to

    `modified_time: Any`
    :   Time the record was last modified

    `ownership: Any`
    :   Ownership type (e.g., Public, Private)

    `phone: Any`
    :   Account phone number

    `rating: Any`
    :   Account rating

    `website: Any`
    :   Account website URL

`AccountsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zoho_crm.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

`AccountsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zoho_crm.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zoho_crm.types.AccountsStringFilter`
    :   The type of the None singleton.

`AccountsGetParams(*args, **kwargs)`
:   Parameters for accounts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`AccountsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zoho_crm.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zoho_crm.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zoho_crm.types.AccountsInFilter`
    :   The type of the None singleton.

`AccountsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_name: list[str]`
    :   Name of the account or company

    `account_number: list[str]`
    :   Account number

    `account_type: list[str]`
    :   Type of account (e.g., Analyst, Competitor, Customer)

    `annual_revenue: list[float]`
    :   Annual revenue of the account

    `billing_city: list[str]`
    :   Billing address city

    `billing_country: list[str]`
    :   Billing address country

    `billing_state: list[str]`
    :   Billing address state or province

    `created_time: list[str]`
    :   Time the record was created

    `description: list[str]`
    :   Description or notes about the account

    `employees: list[int]`
    :   Number of employees

    `id: list[str]`
    :   Unique record identifier

    `industry: list[str]`
    :   Industry the account belongs to

    `modified_time: list[str]`
    :   Time the record was last modified

    `ownership: list[str]`
    :   Ownership type (e.g., Public, Private)

    `phone: list[str]`
    :   Account phone number

    `rating: list[str]`
    :   Account rating

    `website: list[str]`
    :   Account website URL

`AccountsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zoho_crm.types.AccountsStringFilter`
    :   The type of the None singleton.

`AccountsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zoho_crm.types.AccountsStringFilter`
    :   The type of the None singleton.

`AccountsListParams(*args, **kwargs)`
:   Parameters for accounts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

`AccountsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zoho_crm.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zoho_crm.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zoho_crm.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zoho_crm.types.AccountsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsAnyCondition`
    :   The type of the None singleton.

`AccountsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zoho_crm.types.AccountsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsAnyCondition]`
    :   The type of the None singleton.

`AccountsSearchFilter(*args, **kwargs)`
:   Available fields for filtering accounts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_name: str | None`
    :   Name of the account or company

    `account_number: str | None`
    :   Account number

    `account_type: str | None`
    :   Type of account (e.g., Analyst, Competitor, Customer)

    `annual_revenue: float | None`
    :   Annual revenue of the account

    `billing_city: str | None`
    :   Billing address city

    `billing_country: str | None`
    :   Billing address country

    `billing_state: str | None`
    :   Billing address state or province

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the account

    `employees: int | None`
    :   Number of employees

    `id: str`
    :   Unique record identifier

    `industry: str | None`
    :   Industry the account belongs to

    `modified_time: str | None`
    :   Time the record was last modified

    `ownership: str | None`
    :   Ownership type (e.g., Public, Private)

    `phone: str | None`
    :   Account phone number

    `rating: str | None`
    :   Account rating

    `website: str | None`
    :   Account website URL

`AccountsSearchQuery(*args, **kwargs)`
:   Search query for accounts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zoho_crm.types.AccountsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.AccountsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zoho_crm.types.AccountsSortFilter]`
    :   The type of the None singleton.

`AccountsSortFilter(*args, **kwargs)`
:   Available fields for sorting accounts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_name: Literal['asc', 'desc']`
    :   Name of the account or company

    `account_number: Literal['asc', 'desc']`
    :   Account number

    `account_type: Literal['asc', 'desc']`
    :   Type of account (e.g., Analyst, Competitor, Customer)

    `annual_revenue: Literal['asc', 'desc']`
    :   Annual revenue of the account

    `billing_city: Literal['asc', 'desc']`
    :   Billing address city

    `billing_country: Literal['asc', 'desc']`
    :   Billing address country

    `billing_state: Literal['asc', 'desc']`
    :   Billing address state or province

    `created_time: Literal['asc', 'desc']`
    :   Time the record was created

    `description: Literal['asc', 'desc']`
    :   Description or notes about the account

    `employees: Literal['asc', 'desc']`
    :   Number of employees

    `id: Literal['asc', 'desc']`
    :   Unique record identifier

    `industry: Literal['asc', 'desc']`
    :   Industry the account belongs to

    `modified_time: Literal['asc', 'desc']`
    :   Time the record was last modified

    `ownership: Literal['asc', 'desc']`
    :   Ownership type (e.g., Public, Private)

    `phone: Literal['asc', 'desc']`
    :   Account phone number

    `rating: Literal['asc', 'desc']`
    :   Account rating

    `website: Literal['asc', 'desc']`
    :   Account website URL

`AccountsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_name: str`
    :   Name of the account or company

    `account_number: str`
    :   Account number

    `account_type: str`
    :   Type of account (e.g., Analyst, Competitor, Customer)

    `annual_revenue: str`
    :   Annual revenue of the account

    `billing_city: str`
    :   Billing address city

    `billing_country: str`
    :   Billing address country

    `billing_state: str`
    :   Billing address state or province

    `created_time: str`
    :   Time the record was created

    `description: str`
    :   Description or notes about the account

    `employees: str`
    :   Number of employees

    `id: str`
    :   Unique record identifier

    `industry: str`
    :   Industry the account belongs to

    `modified_time: str`
    :   Time the record was last modified

    `ownership: str`
    :   Ownership type (e.g., Public, Private)

    `phone: str`
    :   Account phone number

    `rating: str`
    :   Account rating

    `website: str`
    :   Account website URL

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

    `and: list[airbyte_agent_sdk.connectors.zoho_crm.types.CallsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsAnyCondition]`
    :   The type of the None singleton.

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

    `any: airbyte_agent_sdk.connectors.zoho_crm.types.CallsAnyValueFilter`
    :   The type of the None singleton.

`CallsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `call_duration: Any`
    :   Duration of the call as a formatted string

    `call_duration_in_seconds: Any`
    :   Duration of the call in seconds

    `call_purpose: Any`
    :   Purpose of the call

    `call_result: Any`
    :   Result or outcome of the call

    `call_start_time: Any`
    :   Start time of the call

    `call_type: Any`
    :   Type of call (Inbound or Outbound)

    `caller_id: Any`
    :   Caller ID number

    `created_time: Any`
    :   Time the record was created

    `description: Any`
    :   Description or notes about the call

    `id: Any`
    :   Unique record identifier

    `modified_time: Any`
    :   Time the record was last modified

    `outgoing_call_status: Any`
    :   Status of outgoing calls

    `subject: Any`
    :   Subject of the call

`CallsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zoho_crm.types.CallsAnyValueFilter`
    :   The type of the None singleton.

`CallsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zoho_crm.types.CallsSearchFilter`
    :   The type of the None singleton.

`CallsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zoho_crm.types.CallsStringFilter`
    :   The type of the None singleton.

`CallsGetParams(*args, **kwargs)`
:   Parameters for calls.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`CallsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zoho_crm.types.CallsSearchFilter`
    :   The type of the None singleton.

`CallsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zoho_crm.types.CallsSearchFilter`
    :   The type of the None singleton.

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

    `in: airbyte_agent_sdk.connectors.zoho_crm.types.CallsInFilter`
    :   The type of the None singleton.

`CallsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `call_duration: list[str]`
    :   Duration of the call as a formatted string

    `call_duration_in_seconds: list[float]`
    :   Duration of the call in seconds

    `call_purpose: list[str]`
    :   Purpose of the call

    `call_result: list[str]`
    :   Result or outcome of the call

    `call_start_time: list[str]`
    :   Start time of the call

    `call_type: list[str]`
    :   Type of call (Inbound or Outbound)

    `caller_id: list[str]`
    :   Caller ID number

    `created_time: list[str]`
    :   Time the record was created

    `description: list[str]`
    :   Description or notes about the call

    `id: list[str]`
    :   Unique record identifier

    `modified_time: list[str]`
    :   Time the record was last modified

    `outgoing_call_status: list[str]`
    :   Status of outgoing calls

    `subject: list[str]`
    :   Subject of the call

`CallsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zoho_crm.types.CallsStringFilter`
    :   The type of the None singleton.

`CallsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zoho_crm.types.CallsStringFilter`
    :   The type of the None singleton.

`CallsListParams(*args, **kwargs)`
:   Parameters for calls.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

`CallsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zoho_crm.types.CallsSearchFilter`
    :   The type of the None singleton.

`CallsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zoho_crm.types.CallsSearchFilter`
    :   The type of the None singleton.

`CallsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zoho_crm.types.CallsSearchFilter`
    :   The type of the None singleton.

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

    `not: airbyte_agent_sdk.connectors.zoho_crm.types.CallsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsAnyCondition`
    :   The type of the None singleton.

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

    `or: list[airbyte_agent_sdk.connectors.zoho_crm.types.CallsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsAnyCondition]`
    :   The type of the None singleton.

`CallsSearchFilter(*args, **kwargs)`
:   Available fields for filtering calls search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `call_duration: str | None`
    :   Duration of the call as a formatted string

    `call_duration_in_seconds: float | None`
    :   Duration of the call in seconds

    `call_purpose: str | None`
    :   Purpose of the call

    `call_result: str | None`
    :   Result or outcome of the call

    `call_start_time: str | None`
    :   Start time of the call

    `call_type: str | None`
    :   Type of call (Inbound or Outbound)

    `caller_id: str | None`
    :   Caller ID number

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the call

    `id: str`
    :   Unique record identifier

    `modified_time: str | None`
    :   Time the record was last modified

    `outgoing_call_status: str | None`
    :   Status of outgoing calls

    `subject: str | None`
    :   Subject of the call

`CallsSearchQuery(*args, **kwargs)`
:   Search query for calls entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zoho_crm.types.CallsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CallsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zoho_crm.types.CallsSortFilter]`
    :   The type of the None singleton.

`CallsSortFilter(*args, **kwargs)`
:   Available fields for sorting calls search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `call_duration: Literal['asc', 'desc']`
    :   Duration of the call as a formatted string

    `call_duration_in_seconds: Literal['asc', 'desc']`
    :   Duration of the call in seconds

    `call_purpose: Literal['asc', 'desc']`
    :   Purpose of the call

    `call_result: Literal['asc', 'desc']`
    :   Result or outcome of the call

    `call_start_time: Literal['asc', 'desc']`
    :   Start time of the call

    `call_type: Literal['asc', 'desc']`
    :   Type of call (Inbound or Outbound)

    `caller_id: Literal['asc', 'desc']`
    :   Caller ID number

    `created_time: Literal['asc', 'desc']`
    :   Time the record was created

    `description: Literal['asc', 'desc']`
    :   Description or notes about the call

    `id: Literal['asc', 'desc']`
    :   Unique record identifier

    `modified_time: Literal['asc', 'desc']`
    :   Time the record was last modified

    `outgoing_call_status: Literal['asc', 'desc']`
    :   Status of outgoing calls

    `subject: Literal['asc', 'desc']`
    :   Subject of the call

`CallsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `call_duration: str`
    :   Duration of the call as a formatted string

    `call_duration_in_seconds: str`
    :   Duration of the call in seconds

    `call_purpose: str`
    :   Purpose of the call

    `call_result: str`
    :   Result or outcome of the call

    `call_start_time: str`
    :   Start time of the call

    `call_type: str`
    :   Type of call (Inbound or Outbound)

    `caller_id: str`
    :   Caller ID number

    `created_time: str`
    :   Time the record was created

    `description: str`
    :   Description or notes about the call

    `id: str`
    :   Unique record identifier

    `modified_time: str`
    :   Time the record was last modified

    `outgoing_call_status: str`
    :   Status of outgoing calls

    `subject: str`
    :   Subject of the call

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

    `and: list[airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

`CampaignsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actual_cost: Any`
    :   Actual cost incurred

    `budgeted_cost: Any`
    :   Budget allocated for the campaign

    `campaign_name: Any`
    :   Name of the campaign

    `created_time: Any`
    :   Time the record was created

    `description: Any`
    :   Description or notes about the campaign

    `end_date: Any`
    :   Campaign end date

    `expected_response: Any`
    :   Expected response count

    `expected_revenue: Any`
    :   Expected revenue from the campaign

    `id: Any`
    :   Unique record identifier

    `modified_time: Any`
    :   Time the record was last modified

    `num_sent: Any`
    :   Number of campaign messages sent

    `start_date: Any`
    :   Campaign start date

    `status: Any`
    :   Current status of the campaign

    `type_: Any`
    :   Type of campaign (e.g., Email, Webinar, Conference)

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsInFilter`
    :   The type of the None singleton.

`CampaignsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actual_cost: list[float]`
    :   Actual cost incurred

    `budgeted_cost: list[float]`
    :   Budget allocated for the campaign

    `campaign_name: list[str]`
    :   Name of the campaign

    `created_time: list[str]`
    :   Time the record was created

    `description: list[str]`
    :   Description or notes about the campaign

    `end_date: list[str]`
    :   Campaign end date

    `expected_response: list[int]`
    :   Expected response count

    `expected_revenue: list[float]`
    :   Expected revenue from the campaign

    `id: list[str]`
    :   Unique record identifier

    `modified_time: list[str]`
    :   Time the record was last modified

    `num_sent: list[str]`
    :   Number of campaign messages sent

    `start_date: list[str]`
    :   Campaign start date

    `status: list[str]`
    :   Current status of the campaign

    `type_: list[str]`
    :   Type of campaign (e.g., Email, Webinar, Conference)

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsListParams(*args, **kwargs)`
:   Parameters for campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

`CampaignsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaigns search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actual_cost: float | None`
    :   Actual cost incurred

    `budgeted_cost: float | None`
    :   Budget allocated for the campaign

    `campaign_name: str | None`
    :   Name of the campaign

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the campaign

    `end_date: str | None`
    :   Campaign end date

    `expected_response: int | None`
    :   Expected response count

    `expected_revenue: float | None`
    :   Expected revenue from the campaign

    `id: str`
    :   Unique record identifier

    `modified_time: str | None`
    :   Time the record was last modified

    `num_sent: str | None`
    :   Number of campaign messages sent

    `start_date: str | None`
    :   Campaign start date

    `status: str | None`
    :   Current status of the campaign

    `type_: str | None`
    :   Type of campaign (e.g., Email, Webinar, Conference)

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zoho_crm.types.CampaignsSortFilter]`
    :   The type of the None singleton.

`CampaignsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaigns search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actual_cost: Literal['asc', 'desc']`
    :   Actual cost incurred

    `budgeted_cost: Literal['asc', 'desc']`
    :   Budget allocated for the campaign

    `campaign_name: Literal['asc', 'desc']`
    :   Name of the campaign

    `created_time: Literal['asc', 'desc']`
    :   Time the record was created

    `description: Literal['asc', 'desc']`
    :   Description or notes about the campaign

    `end_date: Literal['asc', 'desc']`
    :   Campaign end date

    `expected_response: Literal['asc', 'desc']`
    :   Expected response count

    `expected_revenue: Literal['asc', 'desc']`
    :   Expected revenue from the campaign

    `id: Literal['asc', 'desc']`
    :   Unique record identifier

    `modified_time: Literal['asc', 'desc']`
    :   Time the record was last modified

    `num_sent: Literal['asc', 'desc']`
    :   Number of campaign messages sent

    `start_date: Literal['asc', 'desc']`
    :   Campaign start date

    `status: Literal['asc', 'desc']`
    :   Current status of the campaign

    `type_: Literal['asc', 'desc']`
    :   Type of campaign (e.g., Email, Webinar, Conference)

`CampaignsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actual_cost: str`
    :   Actual cost incurred

    `budgeted_cost: str`
    :   Budget allocated for the campaign

    `campaign_name: str`
    :   Name of the campaign

    `created_time: str`
    :   Time the record was created

    `description: str`
    :   Description or notes about the campaign

    `end_date: str`
    :   Campaign end date

    `expected_response: str`
    :   Expected response count

    `expected_revenue: str`
    :   Expected revenue from the campaign

    `id: str`
    :   Unique record identifier

    `modified_time: str`
    :   Time the record was last modified

    `num_sent: str`
    :   Number of campaign messages sent

    `start_date: str`
    :   Campaign start date

    `status: str`
    :   Current status of the campaign

    `type_: str`
    :   Type of campaign (e.g., Email, Webinar, Conference)

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

    `and: list[airbyte_agent_sdk.connectors.zoho_crm.types.ContactsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.zoho_crm.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

`ContactsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_time: Any`
    :   Time the record was created

    `date_of_birth: Any`
    :   Contact's date of birth

    `department: Any`
    :   Department the contact belongs to

    `description: Any`
    :   Description or notes about the contact

    `email: Any`
    :   Contact's email address

    `first_name: Any`
    :   Contact's first name

    `full_name: Any`
    :   Contact's full name

    `id: Any`
    :   Unique record identifier

    `last_name: Any`
    :   Contact's last name

    `lead_source: Any`
    :   Source from which the contact was generated

    `mailing_city: Any`
    :   Mailing address city

    `mailing_country: Any`
    :   Mailing address country

    `mailing_state: Any`
    :   Mailing address state or province

    `mobile: Any`
    :   Contact's mobile number

    `modified_time: Any`
    :   Time the record was last modified

    `phone: Any`
    :   Contact's phone number

    `title: Any`
    :   Contact's job title

`ContactsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zoho_crm.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

`ContactsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zoho_crm.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zoho_crm.types.ContactsStringFilter`
    :   The type of the None singleton.

`ContactsGetParams(*args, **kwargs)`
:   Parameters for contacts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`ContactsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zoho_crm.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zoho_crm.types.ContactsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.zoho_crm.types.ContactsInFilter`
    :   The type of the None singleton.

`ContactsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_time: list[str]`
    :   Time the record was created

    `date_of_birth: list[str]`
    :   Contact's date of birth

    `department: list[str]`
    :   Department the contact belongs to

    `description: list[str]`
    :   Description or notes about the contact

    `email: list[str]`
    :   Contact's email address

    `first_name: list[str]`
    :   Contact's first name

    `full_name: list[str]`
    :   Contact's full name

    `id: list[str]`
    :   Unique record identifier

    `last_name: list[str]`
    :   Contact's last name

    `lead_source: list[str]`
    :   Source from which the contact was generated

    `mailing_city: list[str]`
    :   Mailing address city

    `mailing_country: list[str]`
    :   Mailing address country

    `mailing_state: list[str]`
    :   Mailing address state or province

    `mobile: list[str]`
    :   Contact's mobile number

    `modified_time: list[str]`
    :   Time the record was last modified

    `phone: list[str]`
    :   Contact's phone number

    `title: list[str]`
    :   Contact's job title

`ContactsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zoho_crm.types.ContactsStringFilter`
    :   The type of the None singleton.

`ContactsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zoho_crm.types.ContactsStringFilter`
    :   The type of the None singleton.

`ContactsListParams(*args, **kwargs)`
:   Parameters for contacts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

`ContactsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zoho_crm.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zoho_crm.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zoho_crm.types.ContactsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.zoho_crm.types.ContactsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.zoho_crm.types.ContactsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsAnyCondition]`
    :   The type of the None singleton.

`ContactsSearchFilter(*args, **kwargs)`
:   Available fields for filtering contacts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_time: str | None`
    :   Time the record was created

    `date_of_birth: str | None`
    :   Contact's date of birth

    `department: str | None`
    :   Department the contact belongs to

    `description: str | None`
    :   Description or notes about the contact

    `email: str | None`
    :   Contact's email address

    `first_name: str | None`
    :   Contact's first name

    `full_name: str | None`
    :   Contact's full name

    `id: str`
    :   Unique record identifier

    `last_name: str | None`
    :   Contact's last name

    `lead_source: str | None`
    :   Source from which the contact was generated

    `mailing_city: str | None`
    :   Mailing address city

    `mailing_country: str | None`
    :   Mailing address country

    `mailing_state: str | None`
    :   Mailing address state or province

    `mobile: str | None`
    :   Contact's mobile number

    `modified_time: str | None`
    :   Time the record was last modified

    `phone: str | None`
    :   Contact's phone number

    `title: str | None`
    :   Contact's job title

`ContactsSearchQuery(*args, **kwargs)`
:   Search query for contacts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zoho_crm.types.ContactsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ContactsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zoho_crm.types.ContactsSortFilter]`
    :   The type of the None singleton.

`ContactsSortFilter(*args, **kwargs)`
:   Available fields for sorting contacts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_time: Literal['asc', 'desc']`
    :   Time the record was created

    `date_of_birth: Literal['asc', 'desc']`
    :   Contact's date of birth

    `department: Literal['asc', 'desc']`
    :   Department the contact belongs to

    `description: Literal['asc', 'desc']`
    :   Description or notes about the contact

    `email: Literal['asc', 'desc']`
    :   Contact's email address

    `first_name: Literal['asc', 'desc']`
    :   Contact's first name

    `full_name: Literal['asc', 'desc']`
    :   Contact's full name

    `id: Literal['asc', 'desc']`
    :   Unique record identifier

    `last_name: Literal['asc', 'desc']`
    :   Contact's last name

    `lead_source: Literal['asc', 'desc']`
    :   Source from which the contact was generated

    `mailing_city: Literal['asc', 'desc']`
    :   Mailing address city

    `mailing_country: Literal['asc', 'desc']`
    :   Mailing address country

    `mailing_state: Literal['asc', 'desc']`
    :   Mailing address state or province

    `mobile: Literal['asc', 'desc']`
    :   Contact's mobile number

    `modified_time: Literal['asc', 'desc']`
    :   Time the record was last modified

    `phone: Literal['asc', 'desc']`
    :   Contact's phone number

    `title: Literal['asc', 'desc']`
    :   Contact's job title

`ContactsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_time: str`
    :   Time the record was created

    `date_of_birth: str`
    :   Contact's date of birth

    `department: str`
    :   Department the contact belongs to

    `description: str`
    :   Description or notes about the contact

    `email: str`
    :   Contact's email address

    `first_name: str`
    :   Contact's first name

    `full_name: str`
    :   Contact's full name

    `id: str`
    :   Unique record identifier

    `last_name: str`
    :   Contact's last name

    `lead_source: str`
    :   Source from which the contact was generated

    `mailing_city: str`
    :   Mailing address city

    `mailing_country: str`
    :   Mailing address country

    `mailing_state: str`
    :   Mailing address state or province

    `mobile: str`
    :   Contact's mobile number

    `modified_time: str`
    :   Time the record was last modified

    `phone: str`
    :   Contact's phone number

    `title: str`
    :   Contact's job title

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

    `and: list[airbyte_agent_sdk.connectors.zoho_crm.types.DealsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.zoho_crm.types.DealsAnyValueFilter`
    :   The type of the None singleton.

`DealsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Any`
    :   Monetary value of the deal

    `closing_date: Any`
    :   Expected closing date

    `created_time: Any`
    :   Time the record was created

    `deal_name: Any`
    :   Name of the deal

    `description: Any`
    :   Description or notes about the deal

    `id: Any`
    :   Unique record identifier

    `lead_source: Any`
    :   Source from which the deal originated

    `modified_time: Any`
    :   Time the record was last modified

    `next_step: Any`
    :   Next step in the deal process

    `probability: Any`
    :   Probability of closing the deal (percentage)

    `stage: Any`
    :   Current stage of the deal in the pipeline

    `type_: Any`
    :   Type of deal (e.g., New Business, Existing Business)

`DealsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zoho_crm.types.DealsAnyValueFilter`
    :   The type of the None singleton.

`DealsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zoho_crm.types.DealsSearchFilter`
    :   The type of the None singleton.

`DealsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zoho_crm.types.DealsStringFilter`
    :   The type of the None singleton.

`DealsGetParams(*args, **kwargs)`
:   Parameters for deals.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`DealsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zoho_crm.types.DealsSearchFilter`
    :   The type of the None singleton.

`DealsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zoho_crm.types.DealsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.zoho_crm.types.DealsInFilter`
    :   The type of the None singleton.

`DealsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: list[float]`
    :   Monetary value of the deal

    `closing_date: list[str]`
    :   Expected closing date

    `created_time: list[str]`
    :   Time the record was created

    `deal_name: list[str]`
    :   Name of the deal

    `description: list[str]`
    :   Description or notes about the deal

    `id: list[str]`
    :   Unique record identifier

    `lead_source: list[str]`
    :   Source from which the deal originated

    `modified_time: list[str]`
    :   Time the record was last modified

    `next_step: list[str]`
    :   Next step in the deal process

    `probability: list[int]`
    :   Probability of closing the deal (percentage)

    `stage: list[str]`
    :   Current stage of the deal in the pipeline

    `type_: list[str]`
    :   Type of deal (e.g., New Business, Existing Business)

`DealsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zoho_crm.types.DealsStringFilter`
    :   The type of the None singleton.

`DealsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zoho_crm.types.DealsStringFilter`
    :   The type of the None singleton.

`DealsListParams(*args, **kwargs)`
:   Parameters for deals.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

`DealsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zoho_crm.types.DealsSearchFilter`
    :   The type of the None singleton.

`DealsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zoho_crm.types.DealsSearchFilter`
    :   The type of the None singleton.

`DealsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zoho_crm.types.DealsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.zoho_crm.types.DealsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.zoho_crm.types.DealsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsAnyCondition]`
    :   The type of the None singleton.

`DealsSearchFilter(*args, **kwargs)`
:   Available fields for filtering deals search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: float | None`
    :   Monetary value of the deal

    `closing_date: str | None`
    :   Expected closing date

    `created_time: str | None`
    :   Time the record was created

    `deal_name: str | None`
    :   Name of the deal

    `description: str | None`
    :   Description or notes about the deal

    `id: str`
    :   Unique record identifier

    `lead_source: str | None`
    :   Source from which the deal originated

    `modified_time: str | None`
    :   Time the record was last modified

    `next_step: str | None`
    :   Next step in the deal process

    `probability: int | None`
    :   Probability of closing the deal (percentage)

    `stage: str | None`
    :   Current stage of the deal in the pipeline

    `type_: str | None`
    :   Type of deal (e.g., New Business, Existing Business)

`DealsSearchQuery(*args, **kwargs)`
:   Search query for deals entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zoho_crm.types.DealsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.DealsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zoho_crm.types.DealsSortFilter]`
    :   The type of the None singleton.

`DealsSortFilter(*args, **kwargs)`
:   Available fields for sorting deals search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Literal['asc', 'desc']`
    :   Monetary value of the deal

    `closing_date: Literal['asc', 'desc']`
    :   Expected closing date

    `created_time: Literal['asc', 'desc']`
    :   Time the record was created

    `deal_name: Literal['asc', 'desc']`
    :   Name of the deal

    `description: Literal['asc', 'desc']`
    :   Description or notes about the deal

    `id: Literal['asc', 'desc']`
    :   Unique record identifier

    `lead_source: Literal['asc', 'desc']`
    :   Source from which the deal originated

    `modified_time: Literal['asc', 'desc']`
    :   Time the record was last modified

    `next_step: Literal['asc', 'desc']`
    :   Next step in the deal process

    `probability: Literal['asc', 'desc']`
    :   Probability of closing the deal (percentage)

    `stage: Literal['asc', 'desc']`
    :   Current stage of the deal in the pipeline

    `type_: Literal['asc', 'desc']`
    :   Type of deal (e.g., New Business, Existing Business)

`DealsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   Monetary value of the deal

    `closing_date: str`
    :   Expected closing date

    `created_time: str`
    :   Time the record was created

    `deal_name: str`
    :   Name of the deal

    `description: str`
    :   Description or notes about the deal

    `id: str`
    :   Unique record identifier

    `lead_source: str`
    :   Source from which the deal originated

    `modified_time: str`
    :   Time the record was last modified

    `next_step: str`
    :   Next step in the deal process

    `probability: str`
    :   Probability of closing the deal (percentage)

    `stage: str`
    :   Current stage of the deal in the pipeline

    `type_: str`
    :   Type of deal (e.g., New Business, Existing Business)

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

    `and: list[airbyte_agent_sdk.connectors.zoho_crm.types.EventsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.zoho_crm.types.EventsAnyValueFilter`
    :   The type of the None singleton.

`EventsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `all_day: Any`
    :   Whether this is an all-day event

    `created_time: Any`
    :   Time the record was created

    `description: Any`
    :   Description or notes about the event

    `end_date_time: Any`
    :   Event end date and time

    `event_title: Any`
    :   Title of the event

    `id: Any`
    :   Unique record identifier

    `location: Any`
    :   Event location

    `modified_time: Any`
    :   Time the record was last modified

    `start_date_time: Any`
    :   Event start date and time

`EventsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zoho_crm.types.EventsAnyValueFilter`
    :   The type of the None singleton.

`EventsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zoho_crm.types.EventsSearchFilter`
    :   The type of the None singleton.

`EventsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zoho_crm.types.EventsStringFilter`
    :   The type of the None singleton.

`EventsGetParams(*args, **kwargs)`
:   Parameters for events.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`EventsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zoho_crm.types.EventsSearchFilter`
    :   The type of the None singleton.

`EventsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zoho_crm.types.EventsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.zoho_crm.types.EventsInFilter`
    :   The type of the None singleton.

`EventsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `all_day: list[bool]`
    :   Whether this is an all-day event

    `created_time: list[str]`
    :   Time the record was created

    `description: list[str]`
    :   Description or notes about the event

    `end_date_time: list[str]`
    :   Event end date and time

    `event_title: list[str]`
    :   Title of the event

    `id: list[str]`
    :   Unique record identifier

    `location: list[str]`
    :   Event location

    `modified_time: list[str]`
    :   Time the record was last modified

    `start_date_time: list[str]`
    :   Event start date and time

`EventsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zoho_crm.types.EventsStringFilter`
    :   The type of the None singleton.

`EventsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zoho_crm.types.EventsStringFilter`
    :   The type of the None singleton.

`EventsListParams(*args, **kwargs)`
:   Parameters for events.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

`EventsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zoho_crm.types.EventsSearchFilter`
    :   The type of the None singleton.

`EventsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zoho_crm.types.EventsSearchFilter`
    :   The type of the None singleton.

`EventsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zoho_crm.types.EventsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.zoho_crm.types.EventsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.zoho_crm.types.EventsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsAnyCondition]`
    :   The type of the None singleton.

`EventsSearchFilter(*args, **kwargs)`
:   Available fields for filtering events search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `all_day: bool | None`
    :   Whether this is an all-day event

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the event

    `end_date_time: str | None`
    :   Event end date and time

    `event_title: str | None`
    :   Title of the event

    `id: str`
    :   Unique record identifier

    `location: str | None`
    :   Event location

    `modified_time: str | None`
    :   Time the record was last modified

    `start_date_time: str | None`
    :   Event start date and time

`EventsSearchQuery(*args, **kwargs)`
:   Search query for events entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zoho_crm.types.EventsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.EventsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zoho_crm.types.EventsSortFilter]`
    :   The type of the None singleton.

`EventsSortFilter(*args, **kwargs)`
:   Available fields for sorting events search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `all_day: Literal['asc', 'desc']`
    :   Whether this is an all-day event

    `created_time: Literal['asc', 'desc']`
    :   Time the record was created

    `description: Literal['asc', 'desc']`
    :   Description or notes about the event

    `end_date_time: Literal['asc', 'desc']`
    :   Event end date and time

    `event_title: Literal['asc', 'desc']`
    :   Title of the event

    `id: Literal['asc', 'desc']`
    :   Unique record identifier

    `location: Literal['asc', 'desc']`
    :   Event location

    `modified_time: Literal['asc', 'desc']`
    :   Time the record was last modified

    `start_date_time: Literal['asc', 'desc']`
    :   Event start date and time

`EventsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `all_day: str`
    :   Whether this is an all-day event

    `created_time: str`
    :   Time the record was created

    `description: str`
    :   Description or notes about the event

    `end_date_time: str`
    :   Event end date and time

    `event_title: str`
    :   Title of the event

    `id: str`
    :   Unique record identifier

    `location: str`
    :   Event location

    `modified_time: str`
    :   Time the record was last modified

    `start_date_time: str`
    :   Event start date and time

`InvoicesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesAnyCondition]`
    :   The type of the None singleton.

`InvoicesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesAnyValueFilter`
    :   The type of the None singleton.

`InvoicesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adjustment: Any`
    :   Adjustment amount

    `created_time: Any`
    :   Time the record was created

    `description: Any`
    :   Description or notes about the invoice

    `discount: Any`
    :   Discount amount

    `due_date: Any`
    :   Payment due date

    `excise_duty: Any`
    :   Excise duty amount

    `grand_total: Any`
    :   Total amount including tax and adjustments

    `id: Any`
    :   Unique record identifier

    `invoice_date: Any`
    :   Date the invoice was issued

    `invoice_number: Any`
    :   Invoice number

    `modified_time: Any`
    :   Time the record was last modified

    `purchase_order: Any`
    :   Associated purchase order number

    `status: Any`
    :   Current status of the invoice

    `sub_total: Any`
    :   Subtotal before tax and adjustments

    `subject: Any`
    :   Subject or title of the invoice

    `tax: Any`
    :   Tax amount

    `terms_and_conditions: Any`
    :   Terms and conditions text

`InvoicesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesAnyValueFilter`
    :   The type of the None singleton.

`InvoicesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesStringFilter`
    :   The type of the None singleton.

`InvoicesGetParams(*args, **kwargs)`
:   Parameters for invoices.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`InvoicesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesInFilter`
    :   The type of the None singleton.

`InvoicesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adjustment: list[float]`
    :   Adjustment amount

    `created_time: list[str]`
    :   Time the record was created

    `description: list[str]`
    :   Description or notes about the invoice

    `discount: list[float]`
    :   Discount amount

    `due_date: list[str]`
    :   Payment due date

    `excise_duty: list[float]`
    :   Excise duty amount

    `grand_total: list[float]`
    :   Total amount including tax and adjustments

    `id: list[str]`
    :   Unique record identifier

    `invoice_date: list[str]`
    :   Date the invoice was issued

    `invoice_number: list[str]`
    :   Invoice number

    `modified_time: list[str]`
    :   Time the record was last modified

    `purchase_order: list[str]`
    :   Associated purchase order number

    `status: list[str]`
    :   Current status of the invoice

    `sub_total: list[float]`
    :   Subtotal before tax and adjustments

    `subject: list[str]`
    :   Subject or title of the invoice

    `tax: list[float]`
    :   Tax amount

    `terms_and_conditions: list[str]`
    :   Terms and conditions text

`InvoicesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesStringFilter`
    :   The type of the None singleton.

`InvoicesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesStringFilter`
    :   The type of the None singleton.

`InvoicesListParams(*args, **kwargs)`
:   Parameters for invoices.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

`InvoicesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesAnyCondition`
    :   The type of the None singleton.

`InvoicesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesAnyCondition]`
    :   The type of the None singleton.

`InvoicesSearchFilter(*args, **kwargs)`
:   Available fields for filtering invoices search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adjustment: float | None`
    :   Adjustment amount

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the invoice

    `discount: float | None`
    :   Discount amount

    `due_date: str | None`
    :   Payment due date

    `excise_duty: float | None`
    :   Excise duty amount

    `grand_total: float | None`
    :   Total amount including tax and adjustments

    `id: str`
    :   Unique record identifier

    `invoice_date: str | None`
    :   Date the invoice was issued

    `invoice_number: str | None`
    :   Invoice number

    `modified_time: str | None`
    :   Time the record was last modified

    `purchase_order: str | None`
    :   Associated purchase order number

    `status: str | None`
    :   Current status of the invoice

    `sub_total: float | None`
    :   Subtotal before tax and adjustments

    `subject: str | None`
    :   Subject or title of the invoice

    `tax: float | None`
    :   Tax amount

    `terms_and_conditions: str | None`
    :   Terms and conditions text

`InvoicesSearchQuery(*args, **kwargs)`
:   Search query for invoices entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zoho_crm.types.InvoicesSortFilter]`
    :   The type of the None singleton.

`InvoicesSortFilter(*args, **kwargs)`
:   Available fields for sorting invoices search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adjustment: Literal['asc', 'desc']`
    :   Adjustment amount

    `created_time: Literal['asc', 'desc']`
    :   Time the record was created

    `description: Literal['asc', 'desc']`
    :   Description or notes about the invoice

    `discount: Literal['asc', 'desc']`
    :   Discount amount

    `due_date: Literal['asc', 'desc']`
    :   Payment due date

    `excise_duty: Literal['asc', 'desc']`
    :   Excise duty amount

    `grand_total: Literal['asc', 'desc']`
    :   Total amount including tax and adjustments

    `id: Literal['asc', 'desc']`
    :   Unique record identifier

    `invoice_date: Literal['asc', 'desc']`
    :   Date the invoice was issued

    `invoice_number: Literal['asc', 'desc']`
    :   Invoice number

    `modified_time: Literal['asc', 'desc']`
    :   Time the record was last modified

    `purchase_order: Literal['asc', 'desc']`
    :   Associated purchase order number

    `status: Literal['asc', 'desc']`
    :   Current status of the invoice

    `sub_total: Literal['asc', 'desc']`
    :   Subtotal before tax and adjustments

    `subject: Literal['asc', 'desc']`
    :   Subject or title of the invoice

    `tax: Literal['asc', 'desc']`
    :   Tax amount

    `terms_and_conditions: Literal['asc', 'desc']`
    :   Terms and conditions text

`InvoicesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adjustment: str`
    :   Adjustment amount

    `created_time: str`
    :   Time the record was created

    `description: str`
    :   Description or notes about the invoice

    `discount: str`
    :   Discount amount

    `due_date: str`
    :   Payment due date

    `excise_duty: str`
    :   Excise duty amount

    `grand_total: str`
    :   Total amount including tax and adjustments

    `id: str`
    :   Unique record identifier

    `invoice_date: str`
    :   Date the invoice was issued

    `invoice_number: str`
    :   Invoice number

    `modified_time: str`
    :   Time the record was last modified

    `purchase_order: str`
    :   Associated purchase order number

    `status: str`
    :   Current status of the invoice

    `sub_total: str`
    :   Subtotal before tax and adjustments

    `subject: str`
    :   Subject or title of the invoice

    `tax: str`
    :   Tax amount

    `terms_and_conditions: str`
    :   Terms and conditions text

`LeadsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zoho_crm.types.LeadsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsAnyCondition]`
    :   The type of the None singleton.

`LeadsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zoho_crm.types.LeadsAnyValueFilter`
    :   The type of the None singleton.

`LeadsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annual_revenue: Any`
    :   Annual revenue of the lead's company

    `city: Any`
    :   Lead's city

    `company: Any`
    :   Company the lead is associated with

    `country: Any`
    :   Lead's country

    `created_time: Any`
    :   Time the record was created

    `description: Any`
    :   Description or notes about the lead

    `email: Any`
    :   Lead's email address

    `first_name: Any`
    :   Lead's first name

    `full_name: Any`
    :   Lead's full name

    `id: Any`
    :   Unique record identifier

    `industry: Any`
    :   Industry the lead belongs to

    `last_name: Any`
    :   Lead's last name

    `lead_source: Any`
    :   Source from which the lead was generated

    `lead_status: Any`
    :   Current status of the lead

    `mobile: Any`
    :   Lead's mobile number

    `modified_time: Any`
    :   Time the record was last modified

    `no_of_employees: Any`
    :   Number of employees in the lead's company

    `phone: Any`
    :   Lead's phone number

    `rating: Any`
    :   Lead rating

    `state: Any`
    :   Lead's state or province

    `title: Any`
    :   Lead's job title

    `website: Any`
    :   Lead's website URL

`LeadsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zoho_crm.types.LeadsAnyValueFilter`
    :   The type of the None singleton.

`LeadsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zoho_crm.types.LeadsSearchFilter`
    :   The type of the None singleton.

`LeadsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zoho_crm.types.LeadsStringFilter`
    :   The type of the None singleton.

`LeadsGetParams(*args, **kwargs)`
:   Parameters for leads.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`LeadsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zoho_crm.types.LeadsSearchFilter`
    :   The type of the None singleton.

`LeadsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zoho_crm.types.LeadsSearchFilter`
    :   The type of the None singleton.

`LeadsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zoho_crm.types.LeadsInFilter`
    :   The type of the None singleton.

`LeadsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annual_revenue: list[float]`
    :   Annual revenue of the lead's company

    `city: list[str]`
    :   Lead's city

    `company: list[str]`
    :   Company the lead is associated with

    `country: list[str]`
    :   Lead's country

    `created_time: list[str]`
    :   Time the record was created

    `description: list[str]`
    :   Description or notes about the lead

    `email: list[str]`
    :   Lead's email address

    `first_name: list[str]`
    :   Lead's first name

    `full_name: list[str]`
    :   Lead's full name

    `id: list[str]`
    :   Unique record identifier

    `industry: list[str]`
    :   Industry the lead belongs to

    `last_name: list[str]`
    :   Lead's last name

    `lead_source: list[str]`
    :   Source from which the lead was generated

    `lead_status: list[str]`
    :   Current status of the lead

    `mobile: list[str]`
    :   Lead's mobile number

    `modified_time: list[str]`
    :   Time the record was last modified

    `no_of_employees: list[int]`
    :   Number of employees in the lead's company

    `phone: list[str]`
    :   Lead's phone number

    `rating: list[str]`
    :   Lead rating

    `state: list[str]`
    :   Lead's state or province

    `title: list[str]`
    :   Lead's job title

    `website: list[str]`
    :   Lead's website URL

`LeadsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zoho_crm.types.LeadsStringFilter`
    :   The type of the None singleton.

`LeadsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zoho_crm.types.LeadsStringFilter`
    :   The type of the None singleton.

`LeadsListParams(*args, **kwargs)`
:   Parameters for leads.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

`LeadsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zoho_crm.types.LeadsSearchFilter`
    :   The type of the None singleton.

`LeadsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zoho_crm.types.LeadsSearchFilter`
    :   The type of the None singleton.

`LeadsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zoho_crm.types.LeadsSearchFilter`
    :   The type of the None singleton.

`LeadsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zoho_crm.types.LeadsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsAnyCondition`
    :   The type of the None singleton.

`LeadsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zoho_crm.types.LeadsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsAnyCondition]`
    :   The type of the None singleton.

`LeadsSearchFilter(*args, **kwargs)`
:   Available fields for filtering leads search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annual_revenue: float | None`
    :   Annual revenue of the lead's company

    `city: str | None`
    :   Lead's city

    `company: str | None`
    :   Company the lead is associated with

    `country: str | None`
    :   Lead's country

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the lead

    `email: str | None`
    :   Lead's email address

    `first_name: str | None`
    :   Lead's first name

    `full_name: str | None`
    :   Lead's full name

    `id: str`
    :   Unique record identifier

    `industry: str | None`
    :   Industry the lead belongs to

    `last_name: str | None`
    :   Lead's last name

    `lead_source: str | None`
    :   Source from which the lead was generated

    `lead_status: str | None`
    :   Current status of the lead

    `mobile: str | None`
    :   Lead's mobile number

    `modified_time: str | None`
    :   Time the record was last modified

    `no_of_employees: int | None`
    :   Number of employees in the lead's company

    `phone: str | None`
    :   Lead's phone number

    `rating: str | None`
    :   Lead rating

    `state: str | None`
    :   Lead's state or province

    `title: str | None`
    :   Lead's job title

    `website: str | None`
    :   Lead's website URL

`LeadsSearchQuery(*args, **kwargs)`
:   Search query for leads entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zoho_crm.types.LeadsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.LeadsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zoho_crm.types.LeadsSortFilter]`
    :   The type of the None singleton.

`LeadsSortFilter(*args, **kwargs)`
:   Available fields for sorting leads search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annual_revenue: Literal['asc', 'desc']`
    :   Annual revenue of the lead's company

    `city: Literal['asc', 'desc']`
    :   Lead's city

    `company: Literal['asc', 'desc']`
    :   Company the lead is associated with

    `country: Literal['asc', 'desc']`
    :   Lead's country

    `created_time: Literal['asc', 'desc']`
    :   Time the record was created

    `description: Literal['asc', 'desc']`
    :   Description or notes about the lead

    `email: Literal['asc', 'desc']`
    :   Lead's email address

    `first_name: Literal['asc', 'desc']`
    :   Lead's first name

    `full_name: Literal['asc', 'desc']`
    :   Lead's full name

    `id: Literal['asc', 'desc']`
    :   Unique record identifier

    `industry: Literal['asc', 'desc']`
    :   Industry the lead belongs to

    `last_name: Literal['asc', 'desc']`
    :   Lead's last name

    `lead_source: Literal['asc', 'desc']`
    :   Source from which the lead was generated

    `lead_status: Literal['asc', 'desc']`
    :   Current status of the lead

    `mobile: Literal['asc', 'desc']`
    :   Lead's mobile number

    `modified_time: Literal['asc', 'desc']`
    :   Time the record was last modified

    `no_of_employees: Literal['asc', 'desc']`
    :   Number of employees in the lead's company

    `phone: Literal['asc', 'desc']`
    :   Lead's phone number

    `rating: Literal['asc', 'desc']`
    :   Lead rating

    `state: Literal['asc', 'desc']`
    :   Lead's state or province

    `title: Literal['asc', 'desc']`
    :   Lead's job title

    `website: Literal['asc', 'desc']`
    :   Lead's website URL

`LeadsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annual_revenue: str`
    :   Annual revenue of the lead's company

    `city: str`
    :   Lead's city

    `company: str`
    :   Company the lead is associated with

    `country: str`
    :   Lead's country

    `created_time: str`
    :   Time the record was created

    `description: str`
    :   Description or notes about the lead

    `email: str`
    :   Lead's email address

    `first_name: str`
    :   Lead's first name

    `full_name: str`
    :   Lead's full name

    `id: str`
    :   Unique record identifier

    `industry: str`
    :   Industry the lead belongs to

    `last_name: str`
    :   Lead's last name

    `lead_source: str`
    :   Source from which the lead was generated

    `lead_status: str`
    :   Current status of the lead

    `mobile: str`
    :   Lead's mobile number

    `modified_time: str`
    :   Time the record was last modified

    `no_of_employees: str`
    :   Number of employees in the lead's company

    `phone: str`
    :   Lead's phone number

    `rating: str`
    :   Lead rating

    `state: str`
    :   Lead's state or province

    `title: str`
    :   Lead's job title

    `website: str`
    :   Lead's website URL

`ProductsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zoho_crm.types.ProductsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsAnyCondition]`
    :   The type of the None singleton.

`ProductsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zoho_crm.types.ProductsAnyValueFilter`
    :   The type of the None singleton.

`ProductsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `commission_rate: Any`
    :   Commission rate for the product

    `created_time: Any`
    :   Time the record was created

    `description: Any`
    :   Description of the product

    `id: Any`
    :   Unique record identifier

    `manufacturer: Any`
    :   Product manufacturer

    `modified_time: Any`
    :   Time the record was last modified

    `product_active: Any`
    :   Whether the product is active

    `product_category: Any`
    :   Category of the product

    `product_code: Any`
    :   Product code or SKU

    `product_name: Any`
    :   Name of the product

    `qty_in_demand: Any`
    :   Quantity in demand

    `qty_in_stock: Any`
    :   Quantity currently in stock

    `qty_ordered: Any`
    :   Quantity on order

    `sales_end_date: Any`
    :   Date when sales end

    `sales_start_date: Any`
    :   Date when sales begin

    `unit_price: Any`
    :   Unit price of the product

`ProductsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zoho_crm.types.ProductsAnyValueFilter`
    :   The type of the None singleton.

`ProductsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zoho_crm.types.ProductsSearchFilter`
    :   The type of the None singleton.

`ProductsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zoho_crm.types.ProductsStringFilter`
    :   The type of the None singleton.

`ProductsGetParams(*args, **kwargs)`
:   Parameters for products.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`ProductsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zoho_crm.types.ProductsSearchFilter`
    :   The type of the None singleton.

`ProductsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zoho_crm.types.ProductsSearchFilter`
    :   The type of the None singleton.

`ProductsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zoho_crm.types.ProductsInFilter`
    :   The type of the None singleton.

`ProductsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `commission_rate: list[float]`
    :   Commission rate for the product

    `created_time: list[str]`
    :   Time the record was created

    `description: list[str]`
    :   Description of the product

    `id: list[str]`
    :   Unique record identifier

    `manufacturer: list[str]`
    :   Product manufacturer

    `modified_time: list[str]`
    :   Time the record was last modified

    `product_active: list[bool]`
    :   Whether the product is active

    `product_category: list[str]`
    :   Category of the product

    `product_code: list[str]`
    :   Product code or SKU

    `product_name: list[str]`
    :   Name of the product

    `qty_in_demand: list[float]`
    :   Quantity in demand

    `qty_in_stock: list[float]`
    :   Quantity currently in stock

    `qty_ordered: list[float]`
    :   Quantity on order

    `sales_end_date: list[str]`
    :   Date when sales end

    `sales_start_date: list[str]`
    :   Date when sales begin

    `unit_price: list[float]`
    :   Unit price of the product

`ProductsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zoho_crm.types.ProductsStringFilter`
    :   The type of the None singleton.

`ProductsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zoho_crm.types.ProductsStringFilter`
    :   The type of the None singleton.

`ProductsListParams(*args, **kwargs)`
:   Parameters for products.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

`ProductsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zoho_crm.types.ProductsSearchFilter`
    :   The type of the None singleton.

`ProductsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zoho_crm.types.ProductsSearchFilter`
    :   The type of the None singleton.

`ProductsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zoho_crm.types.ProductsSearchFilter`
    :   The type of the None singleton.

`ProductsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zoho_crm.types.ProductsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsAnyCondition`
    :   The type of the None singleton.

`ProductsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zoho_crm.types.ProductsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsAnyCondition]`
    :   The type of the None singleton.

`ProductsSearchFilter(*args, **kwargs)`
:   Available fields for filtering products search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `commission_rate: float | None`
    :   Commission rate for the product

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description of the product

    `id: str`
    :   Unique record identifier

    `manufacturer: str | None`
    :   Product manufacturer

    `modified_time: str | None`
    :   Time the record was last modified

    `product_active: bool | None`
    :   Whether the product is active

    `product_category: str | None`
    :   Category of the product

    `product_code: str | None`
    :   Product code or SKU

    `product_name: str | None`
    :   Name of the product

    `qty_in_demand: float | None`
    :   Quantity in demand

    `qty_in_stock: float | None`
    :   Quantity currently in stock

    `qty_ordered: float | None`
    :   Quantity on order

    `sales_end_date: str | None`
    :   Date when sales end

    `sales_start_date: str | None`
    :   Date when sales begin

    `unit_price: float | None`
    :   Unit price of the product

`ProductsSearchQuery(*args, **kwargs)`
:   Search query for products entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zoho_crm.types.ProductsEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.ProductsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zoho_crm.types.ProductsSortFilter]`
    :   The type of the None singleton.

`ProductsSortFilter(*args, **kwargs)`
:   Available fields for sorting products search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `commission_rate: Literal['asc', 'desc']`
    :   Commission rate for the product

    `created_time: Literal['asc', 'desc']`
    :   Time the record was created

    `description: Literal['asc', 'desc']`
    :   Description of the product

    `id: Literal['asc', 'desc']`
    :   Unique record identifier

    `manufacturer: Literal['asc', 'desc']`
    :   Product manufacturer

    `modified_time: Literal['asc', 'desc']`
    :   Time the record was last modified

    `product_active: Literal['asc', 'desc']`
    :   Whether the product is active

    `product_category: Literal['asc', 'desc']`
    :   Category of the product

    `product_code: Literal['asc', 'desc']`
    :   Product code or SKU

    `product_name: Literal['asc', 'desc']`
    :   Name of the product

    `qty_in_demand: Literal['asc', 'desc']`
    :   Quantity in demand

    `qty_in_stock: Literal['asc', 'desc']`
    :   Quantity currently in stock

    `qty_ordered: Literal['asc', 'desc']`
    :   Quantity on order

    `sales_end_date: Literal['asc', 'desc']`
    :   Date when sales end

    `sales_start_date: Literal['asc', 'desc']`
    :   Date when sales begin

    `unit_price: Literal['asc', 'desc']`
    :   Unit price of the product

`ProductsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `commission_rate: str`
    :   Commission rate for the product

    `created_time: str`
    :   Time the record was created

    `description: str`
    :   Description of the product

    `id: str`
    :   Unique record identifier

    `manufacturer: str`
    :   Product manufacturer

    `modified_time: str`
    :   Time the record was last modified

    `product_active: str`
    :   Whether the product is active

    `product_category: str`
    :   Category of the product

    `product_code: str`
    :   Product code or SKU

    `product_name: str`
    :   Name of the product

    `qty_in_demand: str`
    :   Quantity in demand

    `qty_in_stock: str`
    :   Quantity currently in stock

    `qty_ordered: str`
    :   Quantity on order

    `sales_end_date: str`
    :   Date when sales end

    `sales_start_date: str`
    :   Date when sales begin

    `unit_price: str`
    :   Unit price of the product

`QuotesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zoho_crm.types.QuotesEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesAnyCondition]`
    :   The type of the None singleton.

`QuotesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zoho_crm.types.QuotesAnyValueFilter`
    :   The type of the None singleton.

`QuotesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adjustment: Any`
    :   Adjustment amount

    `carrier: Any`
    :   Shipping carrier

    `created_time: Any`
    :   Time the record was created

    `description: Any`
    :   Description or notes about the quote

    `discount: Any`
    :   Discount amount

    `grand_total: Any`
    :   Total amount including tax and adjustments

    `id: Any`
    :   Unique record identifier

    `modified_time: Any`
    :   Time the record was last modified

    `quote_stage: Any`
    :   Current stage of the quote

    `sub_total: Any`
    :   Subtotal before tax and adjustments

    `subject: Any`
    :   Subject or title of the quote

    `tax: Any`
    :   Tax amount

    `terms_and_conditions: Any`
    :   Terms and conditions text

    `valid_till: Any`
    :   Date until which the quote is valid

`QuotesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zoho_crm.types.QuotesAnyValueFilter`
    :   The type of the None singleton.

`QuotesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zoho_crm.types.QuotesSearchFilter`
    :   The type of the None singleton.

`QuotesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zoho_crm.types.QuotesStringFilter`
    :   The type of the None singleton.

`QuotesGetParams(*args, **kwargs)`
:   Parameters for quotes.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`QuotesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zoho_crm.types.QuotesSearchFilter`
    :   The type of the None singleton.

`QuotesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zoho_crm.types.QuotesSearchFilter`
    :   The type of the None singleton.

`QuotesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zoho_crm.types.QuotesInFilter`
    :   The type of the None singleton.

`QuotesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adjustment: list[float]`
    :   Adjustment amount

    `carrier: list[str]`
    :   Shipping carrier

    `created_time: list[str]`
    :   Time the record was created

    `description: list[str]`
    :   Description or notes about the quote

    `discount: list[float]`
    :   Discount amount

    `grand_total: list[float]`
    :   Total amount including tax and adjustments

    `id: list[str]`
    :   Unique record identifier

    `modified_time: list[str]`
    :   Time the record was last modified

    `quote_stage: list[str]`
    :   Current stage of the quote

    `sub_total: list[float]`
    :   Subtotal before tax and adjustments

    `subject: list[str]`
    :   Subject or title of the quote

    `tax: list[float]`
    :   Tax amount

    `terms_and_conditions: list[str]`
    :   Terms and conditions text

    `valid_till: list[str]`
    :   Date until which the quote is valid

`QuotesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zoho_crm.types.QuotesStringFilter`
    :   The type of the None singleton.

`QuotesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zoho_crm.types.QuotesStringFilter`
    :   The type of the None singleton.

`QuotesListParams(*args, **kwargs)`
:   Parameters for quotes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

`QuotesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zoho_crm.types.QuotesSearchFilter`
    :   The type of the None singleton.

`QuotesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zoho_crm.types.QuotesSearchFilter`
    :   The type of the None singleton.

`QuotesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zoho_crm.types.QuotesSearchFilter`
    :   The type of the None singleton.

`QuotesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zoho_crm.types.QuotesEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesAnyCondition`
    :   The type of the None singleton.

`QuotesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zoho_crm.types.QuotesEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesAnyCondition]`
    :   The type of the None singleton.

`QuotesSearchFilter(*args, **kwargs)`
:   Available fields for filtering quotes search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adjustment: float | None`
    :   Adjustment amount

    `carrier: str | None`
    :   Shipping carrier

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the quote

    `discount: float | None`
    :   Discount amount

    `grand_total: float | None`
    :   Total amount including tax and adjustments

    `id: str`
    :   Unique record identifier

    `modified_time: str | None`
    :   Time the record was last modified

    `quote_stage: str | None`
    :   Current stage of the quote

    `sub_total: float | None`
    :   Subtotal before tax and adjustments

    `subject: str | None`
    :   Subject or title of the quote

    `tax: float | None`
    :   Tax amount

    `terms_and_conditions: str | None`
    :   Terms and conditions text

    `valid_till: str | None`
    :   Date until which the quote is valid

`QuotesSearchQuery(*args, **kwargs)`
:   Search query for quotes entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zoho_crm.types.QuotesEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.QuotesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zoho_crm.types.QuotesSortFilter]`
    :   The type of the None singleton.

`QuotesSortFilter(*args, **kwargs)`
:   Available fields for sorting quotes search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adjustment: Literal['asc', 'desc']`
    :   Adjustment amount

    `carrier: Literal['asc', 'desc']`
    :   Shipping carrier

    `created_time: Literal['asc', 'desc']`
    :   Time the record was created

    `description: Literal['asc', 'desc']`
    :   Description or notes about the quote

    `discount: Literal['asc', 'desc']`
    :   Discount amount

    `grand_total: Literal['asc', 'desc']`
    :   Total amount including tax and adjustments

    `id: Literal['asc', 'desc']`
    :   Unique record identifier

    `modified_time: Literal['asc', 'desc']`
    :   Time the record was last modified

    `quote_stage: Literal['asc', 'desc']`
    :   Current stage of the quote

    `sub_total: Literal['asc', 'desc']`
    :   Subtotal before tax and adjustments

    `subject: Literal['asc', 'desc']`
    :   Subject or title of the quote

    `tax: Literal['asc', 'desc']`
    :   Tax amount

    `terms_and_conditions: Literal['asc', 'desc']`
    :   Terms and conditions text

    `valid_till: Literal['asc', 'desc']`
    :   Date until which the quote is valid

`QuotesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adjustment: str`
    :   Adjustment amount

    `carrier: str`
    :   Shipping carrier

    `created_time: str`
    :   Time the record was created

    `description: str`
    :   Description or notes about the quote

    `discount: str`
    :   Discount amount

    `grand_total: str`
    :   Total amount including tax and adjustments

    `id: str`
    :   Unique record identifier

    `modified_time: str`
    :   Time the record was last modified

    `quote_stage: str`
    :   Current stage of the quote

    `sub_total: str`
    :   Subtotal before tax and adjustments

    `subject: str`
    :   Subject or title of the quote

    `tax: str`
    :   Tax amount

    `terms_and_conditions: str`
    :   Terms and conditions text

    `valid_till: str`
    :   Date until which the quote is valid

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

    `and: list[airbyte_agent_sdk.connectors.zoho_crm.types.TasksEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksAnyCondition]`
    :   The type of the None singleton.

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

    `any: airbyte_agent_sdk.connectors.zoho_crm.types.TasksAnyValueFilter`
    :   The type of the None singleton.

`TasksAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_time: Any`
    :   Time the task was closed

    `created_time: Any`
    :   Time the record was created

    `description: Any`
    :   Description or notes about the task

    `due_date: Any`
    :   Due date for the task

    `id: Any`
    :   Unique record identifier

    `modified_time: Any`
    :   Time the record was last modified

    `priority: Any`
    :   Priority level (e.g., High, Highest, Low, Lowest, Normal)

    `send_notification_email: Any`
    :   Whether to send a notification email

    `status: Any`
    :   Current status (e.g., Not Started, In Progress, Completed)

    `subject: Any`
    :   Subject or title of the task

`TasksContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zoho_crm.types.TasksAnyValueFilter`
    :   The type of the None singleton.

`TasksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zoho_crm.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zoho_crm.types.TasksStringFilter`
    :   The type of the None singleton.

`TasksGetParams(*args, **kwargs)`
:   Parameters for tasks.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`TasksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zoho_crm.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zoho_crm.types.TasksSearchFilter`
    :   The type of the None singleton.

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

    `in: airbyte_agent_sdk.connectors.zoho_crm.types.TasksInFilter`
    :   The type of the None singleton.

`TasksInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_time: list[str]`
    :   Time the task was closed

    `created_time: list[str]`
    :   Time the record was created

    `description: list[str]`
    :   Description or notes about the task

    `due_date: list[str]`
    :   Due date for the task

    `id: list[str]`
    :   Unique record identifier

    `modified_time: list[str]`
    :   Time the record was last modified

    `priority: list[str]`
    :   Priority level (e.g., High, Highest, Low, Lowest, Normal)

    `send_notification_email: list[bool]`
    :   Whether to send a notification email

    `status: list[str]`
    :   Current status (e.g., Not Started, In Progress, Completed)

    `subject: list[str]`
    :   Subject or title of the task

`TasksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zoho_crm.types.TasksStringFilter`
    :   The type of the None singleton.

`TasksLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zoho_crm.types.TasksStringFilter`
    :   The type of the None singleton.

`TasksListParams(*args, **kwargs)`
:   Parameters for tasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

`TasksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zoho_crm.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zoho_crm.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zoho_crm.types.TasksSearchFilter`
    :   The type of the None singleton.

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

    `not: airbyte_agent_sdk.connectors.zoho_crm.types.TasksEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksAnyCondition`
    :   The type of the None singleton.

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

    `or: list[airbyte_agent_sdk.connectors.zoho_crm.types.TasksEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksAnyCondition]`
    :   The type of the None singleton.

`TasksSearchFilter(*args, **kwargs)`
:   Available fields for filtering tasks search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_time: str | None`
    :   Time the task was closed

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the task

    `due_date: str | None`
    :   Due date for the task

    `id: str`
    :   Unique record identifier

    `modified_time: str | None`
    :   Time the record was last modified

    `priority: str | None`
    :   Priority level (e.g., High, Highest, Low, Lowest, Normal)

    `send_notification_email: bool | None`
    :   Whether to send a notification email

    `status: str | None`
    :   Current status (e.g., Not Started, In Progress, Completed)

    `subject: str | None`
    :   Subject or title of the task

`TasksSearchQuery(*args, **kwargs)`
:   Search query for tasks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zoho_crm.types.TasksEqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksNeqCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksGtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksGteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksLtCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksLteCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksInCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksLikeCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksContainsCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksNotCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksAndCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksOrCondition | airbyte_agent_sdk.connectors.zoho_crm.types.TasksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zoho_crm.types.TasksSortFilter]`
    :   The type of the None singleton.

`TasksSortFilter(*args, **kwargs)`
:   Available fields for sorting tasks search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_time: Literal['asc', 'desc']`
    :   Time the task was closed

    `created_time: Literal['asc', 'desc']`
    :   Time the record was created

    `description: Literal['asc', 'desc']`
    :   Description or notes about the task

    `due_date: Literal['asc', 'desc']`
    :   Due date for the task

    `id: Literal['asc', 'desc']`
    :   Unique record identifier

    `modified_time: Literal['asc', 'desc']`
    :   Time the record was last modified

    `priority: Literal['asc', 'desc']`
    :   Priority level (e.g., High, Highest, Low, Lowest, Normal)

    `send_notification_email: Literal['asc', 'desc']`
    :   Whether to send a notification email

    `status: Literal['asc', 'desc']`
    :   Current status (e.g., Not Started, In Progress, Completed)

    `subject: Literal['asc', 'desc']`
    :   Subject or title of the task

`TasksStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_time: str`
    :   Time the task was closed

    `created_time: str`
    :   Time the record was created

    `description: str`
    :   Description or notes about the task

    `due_date: str`
    :   Due date for the task

    `id: str`
    :   Unique record identifier

    `modified_time: str`
    :   Time the record was last modified

    `priority: str`
    :   Priority level (e.g., High, Highest, Low, Lowest, Normal)

    `send_notification_email: str`
    :   Whether to send a notification email

    `status: str`
    :   Current status (e.g., Not Started, In Progress, Completed)

    `subject: str`
    :   Subject or title of the task