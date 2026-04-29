---
id: airbyte_agent_sdk-connectors-twilio-types
title: airbyte_agent_sdk.connectors.twilio.types
---

Module airbyte_agent_sdk.connectors.twilio.types
================================================
Type definitions for twilio connector.

Classes
-------

<a id="AccountsAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.twilio.types.AccountsEqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsInCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNotCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAndCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsOrCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAnyCondition]`
    :   The type of the None singleton.

<a id="AccountsAnyCondition"></a>

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

    `any: airbyte_agent_sdk.connectors.twilio.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountsAnyValueFilter"></a>

`AccountsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_created: Any`
    :   The timestamp when the account was created

    `date_updated: Any`
    :   The timestamp when the account was last updated

    `friendly_name: Any`
    :   A user-defined friendly name for the account

    `owner_account_sid: Any`
    :   The SID of the owner account

    `sid: Any`
    :   The unique identifier for the account

    `status: Any`
    :   The current status of the account

    `type_: Any`
    :   The type of the account

    `uri: Any`
    :   The URI for accessing the account resource

<a id="AccountsContainsCondition"></a>

`AccountsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountsEqCondition"></a>

`AccountsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsFuzzyCondition"></a>

`AccountsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsGetParams"></a>

`AccountsGetParams(*args, **kwargs)`
:   Parameters for accounts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `sid: str`
    :   The type of the None singleton.

<a id="AccountsGtCondition"></a>

`AccountsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsGteCondition"></a>

`AccountsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsInCondition"></a>

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

    `in: airbyte_agent_sdk.connectors.twilio.types.AccountsInFilter`
    :   The type of the None singleton.

<a id="AccountsInFilter"></a>

`AccountsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_created: list[str]`
    :   The timestamp when the account was created

    `date_updated: list[str]`
    :   The timestamp when the account was last updated

    `friendly_name: list[str]`
    :   A user-defined friendly name for the account

    `owner_account_sid: list[str]`
    :   The SID of the owner account

    `sid: list[str]`
    :   The unique identifier for the account

    `status: list[str]`
    :   The current status of the account

    `type_: list[str]`
    :   The type of the account

    `uri: list[str]`
    :   The URI for accessing the account resource

<a id="AccountsKeywordCondition"></a>

`AccountsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsLikeCondition"></a>

`AccountsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsListParams"></a>

`AccountsListParams(*args, **kwargs)`
:   Parameters for accounts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

<a id="AccountsLtCondition"></a>

`AccountsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsLteCondition"></a>

`AccountsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsNeqCondition"></a>

`AccountsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.twilio.types.AccountsEqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsInCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNotCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAndCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsOrCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAnyCondition`
    :   The type of the None singleton.

<a id="AccountsOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.twilio.types.AccountsEqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsInCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNotCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAndCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsOrCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAnyCondition]`
    :   The type of the None singleton.

<a id="AccountsSearchFilter"></a>

`AccountsSearchFilter(*args, **kwargs)`
:   Available fields for filtering accounts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_created: str | None`
    :   The timestamp when the account was created

    `date_updated: str | None`
    :   The timestamp when the account was last updated

    `friendly_name: str | None`
    :   A user-defined friendly name for the account

    `owner_account_sid: str | None`
    :   The SID of the owner account

    `sid: str | None`
    :   The unique identifier for the account

    `status: str | None`
    :   The current status of the account

    `type_: str | None`
    :   The type of the account

    `uri: str | None`
    :   The URI for accessing the account resource

<a id="AccountsSearchQuery"></a>

`AccountsSearchQuery(*args, **kwargs)`
:   Search query for accounts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.AccountsEqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsInCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNotCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAndCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsOrCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.AccountsSortFilter]`
    :   The type of the None singleton.

<a id="AccountsSortFilter"></a>

`AccountsSortFilter(*args, **kwargs)`
:   Available fields for sorting accounts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_created: Literal['asc', 'desc']`
    :   The timestamp when the account was created

    `date_updated: Literal['asc', 'desc']`
    :   The timestamp when the account was last updated

    `friendly_name: Literal['asc', 'desc']`
    :   A user-defined friendly name for the account

    `owner_account_sid: Literal['asc', 'desc']`
    :   The SID of the owner account

    `sid: Literal['asc', 'desc']`
    :   The unique identifier for the account

    `status: Literal['asc', 'desc']`
    :   The current status of the account

    `type_: Literal['asc', 'desc']`
    :   The type of the account

    `uri: Literal['asc', 'desc']`
    :   The URI for accessing the account resource

<a id="AccountsStringFilter"></a>

`AccountsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_created: str`
    :   The timestamp when the account was created

    `date_updated: str`
    :   The timestamp when the account was last updated

    `friendly_name: str`
    :   A user-defined friendly name for the account

    `owner_account_sid: str`
    :   The SID of the owner account

    `sid: str`
    :   The unique identifier for the account

    `status: str`
    :   The current status of the account

    `type_: str`
    :   The type of the account

    `uri: str`
    :   The URI for accessing the account resource

<a id="AddressesAndCondition"></a>

`AddressesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.twilio.types.AddressesEqCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesGtCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesGteCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLtCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLteCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesInCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesNotCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesAndCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesOrCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesAnyCondition]`
    :   The type of the None singleton.

<a id="AddressesAnyCondition"></a>

`AddressesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.twilio.types.AddressesAnyValueFilter`
    :   The type of the None singleton.

<a id="AddressesAnyValueFilter"></a>

`AddressesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Any`
    :   The account SID associated with this address

    `city: Any`
    :   The city of the address

    `customer_name: Any`
    :   The customer name associated with this address

    `friendly_name: Any`
    :   A friendly name for the address

    `iso_country: Any`
    :   The ISO 3166-1 alpha-2 country code

    `postal_code: Any`
    :   The postal code

    `region: Any`
    :   The region or state

    `sid: Any`
    :   The unique identifier of the address

    `street: Any`
    :   The street address

    `validated: Any`
    :   Whether the address has been validated

    `verified: Any`
    :   Whether the address has been verified

<a id="AddressesContainsCondition"></a>

`AddressesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.AddressesAnyValueFilter`
    :   The type of the None singleton.

<a id="AddressesEqCondition"></a>

`AddressesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.AddressesSearchFilter`
    :   The type of the None singleton.

<a id="AddressesFuzzyCondition"></a>

`AddressesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.AddressesStringFilter`
    :   The type of the None singleton.

<a id="AddressesGetParams"></a>

`AddressesGetParams(*args, **kwargs)`
:   Parameters for addresses.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

<a id="AddressesGtCondition"></a>

`AddressesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.AddressesSearchFilter`
    :   The type of the None singleton.

<a id="AddressesGteCondition"></a>

`AddressesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.AddressesSearchFilter`
    :   The type of the None singleton.

<a id="AddressesInCondition"></a>

`AddressesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.twilio.types.AddressesInFilter`
    :   The type of the None singleton.

<a id="AddressesInFilter"></a>

`AddressesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: list[str]`
    :   The account SID associated with this address

    `city: list[str]`
    :   The city of the address

    `customer_name: list[str]`
    :   The customer name associated with this address

    `friendly_name: list[str]`
    :   A friendly name for the address

    `iso_country: list[str]`
    :   The ISO 3166-1 alpha-2 country code

    `postal_code: list[str]`
    :   The postal code

    `region: list[str]`
    :   The region or state

    `sid: list[str]`
    :   The unique identifier of the address

    `street: list[str]`
    :   The street address

    `validated: list[bool]`
    :   Whether the address has been validated

    `verified: list[bool]`
    :   Whether the address has been verified

<a id="AddressesKeywordCondition"></a>

`AddressesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.AddressesStringFilter`
    :   The type of the None singleton.

<a id="AddressesLikeCondition"></a>

`AddressesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.AddressesStringFilter`
    :   The type of the None singleton.

<a id="AddressesListParams"></a>

`AddressesListParams(*args, **kwargs)`
:   Parameters for addresses.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="AddressesLtCondition"></a>

`AddressesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.AddressesSearchFilter`
    :   The type of the None singleton.

<a id="AddressesLteCondition"></a>

`AddressesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.AddressesSearchFilter`
    :   The type of the None singleton.

<a id="AddressesNeqCondition"></a>

`AddressesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.AddressesSearchFilter`
    :   The type of the None singleton.

<a id="AddressesNotCondition"></a>

`AddressesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.twilio.types.AddressesEqCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesGtCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesGteCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLtCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLteCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesInCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesNotCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesAndCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesOrCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesAnyCondition`
    :   The type of the None singleton.

<a id="AddressesOrCondition"></a>

`AddressesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.twilio.types.AddressesEqCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesGtCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesGteCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLtCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLteCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesInCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesNotCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesAndCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesOrCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesAnyCondition]`
    :   The type of the None singleton.

<a id="AddressesSearchFilter"></a>

`AddressesSearchFilter(*args, **kwargs)`
:   Available fields for filtering addresses search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str | None`
    :   The account SID associated with this address

    `city: str | None`
    :   The city of the address

    `customer_name: str | None`
    :   The customer name associated with this address

    `friendly_name: str | None`
    :   A friendly name for the address

    `iso_country: str | None`
    :   The ISO 3166-1 alpha-2 country code

    `postal_code: str | None`
    :   The postal code

    `region: str | None`
    :   The region or state

    `sid: str | None`
    :   The unique identifier of the address

    `street: str | None`
    :   The street address

    `validated: bool | None`
    :   Whether the address has been validated

    `verified: bool | None`
    :   Whether the address has been verified

<a id="AddressesSearchQuery"></a>

`AddressesSearchQuery(*args, **kwargs)`
:   Search query for addresses entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.AddressesEqCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesGtCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesGteCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLtCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLteCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesInCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesNotCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesAndCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesOrCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.AddressesSortFilter]`
    :   The type of the None singleton.

<a id="AddressesSortFilter"></a>

`AddressesSortFilter(*args, **kwargs)`
:   Available fields for sorting addresses search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Literal['asc', 'desc']`
    :   The account SID associated with this address

    `city: Literal['asc', 'desc']`
    :   The city of the address

    `customer_name: Literal['asc', 'desc']`
    :   The customer name associated with this address

    `friendly_name: Literal['asc', 'desc']`
    :   A friendly name for the address

    `iso_country: Literal['asc', 'desc']`
    :   The ISO 3166-1 alpha-2 country code

    `postal_code: Literal['asc', 'desc']`
    :   The postal code

    `region: Literal['asc', 'desc']`
    :   The region or state

    `sid: Literal['asc', 'desc']`
    :   The unique identifier of the address

    `street: Literal['asc', 'desc']`
    :   The street address

    `validated: Literal['asc', 'desc']`
    :   Whether the address has been validated

    `verified: Literal['asc', 'desc']`
    :   Whether the address has been verified

<a id="AddressesStringFilter"></a>

`AddressesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The account SID associated with this address

    `city: str`
    :   The city of the address

    `customer_name: str`
    :   The customer name associated with this address

    `friendly_name: str`
    :   A friendly name for the address

    `iso_country: str`
    :   The ISO 3166-1 alpha-2 country code

    `postal_code: str`
    :   The postal code

    `region: str`
    :   The region or state

    `sid: str`
    :   The unique identifier of the address

    `street: str`
    :   The street address

    `validated: str`
    :   Whether the address has been validated

    `verified: str`
    :   Whether the address has been verified

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

    `and: list[airbyte_agent_sdk.connectors.twilio.types.CallsEqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsInCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.CallsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNotCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAndCondition | airbyte_agent_sdk.connectors.twilio.types.CallsOrCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.twilio.types.CallsAnyValueFilter`
    :   The type of the None singleton.

<a id="CallsAnyValueFilter"></a>

`CallsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Any`
    :   The unique identifier for the account associated with the call

    `date_created: Any`
    :   The date and time when the call record was created

    `date_updated: Any`
    :   The date and time when the call record was last updated

    `direction: Any`
    :   The direction of the call (inbound or outbound)

    `duration: Any`
    :   The duration of the call in seconds

    `end_time: Any`
    :   The date and time when the call ended

    `from_: Any`
    :   The phone number that made the call

    `price: Any`
    :   The cost of the call

    `price_unit: Any`
    :   The currency unit of the call cost

    `sid: Any`
    :   The unique identifier for the call

    `start_time: Any`
    :   The date and time when the call started

    `status: Any`
    :   The current status of the call

    `to: Any`
    :   The phone number that received the call

<a id="CallsContainsCondition"></a>

`CallsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.CallsAnyValueFilter`
    :   The type of the None singleton.

<a id="CallsEqCondition"></a>

`CallsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsFuzzyCondition"></a>

`CallsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.CallsStringFilter`
    :   The type of the None singleton.

<a id="CallsGetParams"></a>

`CallsGetParams(*args, **kwargs)`
:   Parameters for calls.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

<a id="CallsGtCondition"></a>

`CallsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsGteCondition"></a>

`CallsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.CallsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.twilio.types.CallsInFilter`
    :   The type of the None singleton.

<a id="CallsInFilter"></a>

`CallsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: list[str]`
    :   The unique identifier for the account associated with the call

    `date_created: list[str]`
    :   The date and time when the call record was created

    `date_updated: list[str]`
    :   The date and time when the call record was last updated

    `direction: list[str]`
    :   The direction of the call (inbound or outbound)

    `duration: list[str]`
    :   The duration of the call in seconds

    `end_time: list[str]`
    :   The date and time when the call ended

    `from_: list[str]`
    :   The phone number that made the call

    `price: list[str]`
    :   The cost of the call

    `price_unit: list[str]`
    :   The currency unit of the call cost

    `sid: list[str]`
    :   The unique identifier for the call

    `start_time: list[str]`
    :   The date and time when the call started

    `status: list[str]`
    :   The current status of the call

    `to: list[str]`
    :   The phone number that received the call

<a id="CallsKeywordCondition"></a>

`CallsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.CallsStringFilter`
    :   The type of the None singleton.

<a id="CallsLikeCondition"></a>

`CallsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.CallsStringFilter`
    :   The type of the None singleton.

<a id="CallsListParams"></a>

`CallsListParams(*args, **kwargs)`
:   Parameters for calls.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="CallsLtCondition"></a>

`CallsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsLteCondition"></a>

`CallsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsNeqCondition"></a>

`CallsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.CallsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.twilio.types.CallsEqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsInCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.CallsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNotCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAndCondition | airbyte_agent_sdk.connectors.twilio.types.CallsOrCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.twilio.types.CallsEqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsInCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.CallsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNotCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAndCondition | airbyte_agent_sdk.connectors.twilio.types.CallsOrCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAnyCondition]`
    :   The type of the None singleton.

<a id="CallsSearchFilter"></a>

`CallsSearchFilter(*args, **kwargs)`
:   Available fields for filtering calls search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str | None`
    :   The unique identifier for the account associated with the call

    `date_created: str | None`
    :   The date and time when the call record was created

    `date_updated: str | None`
    :   The date and time when the call record was last updated

    `direction: str | None`
    :   The direction of the call (inbound or outbound)

    `duration: str | None`
    :   The duration of the call in seconds

    `end_time: str | None`
    :   The date and time when the call ended

    `from_: str | None`
    :   The phone number that made the call

    `price: str | None`
    :   The cost of the call

    `price_unit: str | None`
    :   The currency unit of the call cost

    `sid: str | None`
    :   The unique identifier for the call

    `start_time: str | None`
    :   The date and time when the call started

    `status: str | None`
    :   The current status of the call

    `to: str | None`
    :   The phone number that received the call

<a id="CallsSearchQuery"></a>

`CallsSearchQuery(*args, **kwargs)`
:   Search query for calls entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.CallsEqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsInCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.CallsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNotCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAndCondition | airbyte_agent_sdk.connectors.twilio.types.CallsOrCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.CallsSortFilter]`
    :   The type of the None singleton.

<a id="CallsSortFilter"></a>

`CallsSortFilter(*args, **kwargs)`
:   Available fields for sorting calls search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Literal['asc', 'desc']`
    :   The unique identifier for the account associated with the call

    `date_created: Literal['asc', 'desc']`
    :   The date and time when the call record was created

    `date_updated: Literal['asc', 'desc']`
    :   The date and time when the call record was last updated

    `direction: Literal['asc', 'desc']`
    :   The direction of the call (inbound or outbound)

    `duration: Literal['asc', 'desc']`
    :   The duration of the call in seconds

    `end_time: Literal['asc', 'desc']`
    :   The date and time when the call ended

    `from_: Literal['asc', 'desc']`
    :   The phone number that made the call

    `price: Literal['asc', 'desc']`
    :   The cost of the call

    `price_unit: Literal['asc', 'desc']`
    :   The currency unit of the call cost

    `sid: Literal['asc', 'desc']`
    :   The unique identifier for the call

    `start_time: Literal['asc', 'desc']`
    :   The date and time when the call started

    `status: Literal['asc', 'desc']`
    :   The current status of the call

    `to: Literal['asc', 'desc']`
    :   The phone number that received the call

<a id="CallsStringFilter"></a>

`CallsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The unique identifier for the account associated with the call

    `date_created: str`
    :   The date and time when the call record was created

    `date_updated: str`
    :   The date and time when the call record was last updated

    `direction: str`
    :   The direction of the call (inbound or outbound)

    `duration: str`
    :   The duration of the call in seconds

    `end_time: str`
    :   The date and time when the call ended

    `from_: str`
    :   The phone number that made the call

    `price: str`
    :   The cost of the call

    `price_unit: str`
    :   The currency unit of the call cost

    `sid: str`
    :   The unique identifier for the call

    `start_time: str`
    :   The date and time when the call started

    `status: str`
    :   The current status of the call

    `to: str`
    :   The phone number that received the call

<a id="ConferencesAndCondition"></a>

`ConferencesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.twilio.types.ConferencesEqCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesGtCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesGteCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLtCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLteCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesInCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesNotCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesAndCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesOrCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesAnyCondition]`
    :   The type of the None singleton.

<a id="ConferencesAnyCondition"></a>

`ConferencesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.twilio.types.ConferencesAnyValueFilter`
    :   The type of the None singleton.

<a id="ConferencesAnyValueFilter"></a>

`ConferencesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Any`
    :   The account SID associated with the conference

    `date_created: Any`
    :   When the conference was created

    `date_updated: Any`
    :   When the conference was last updated

    `friendly_name: Any`
    :   A friendly name for the conference

    `region: Any`
    :   The region where the conference is hosted

    `sid: Any`
    :   The unique identifier of the conference

    `status: Any`
    :   The current status of the conference

<a id="ConferencesContainsCondition"></a>

`ConferencesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.ConferencesAnyValueFilter`
    :   The type of the None singleton.

<a id="ConferencesEqCondition"></a>

`ConferencesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.ConferencesSearchFilter`
    :   The type of the None singleton.

<a id="ConferencesFuzzyCondition"></a>

`ConferencesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.ConferencesStringFilter`
    :   The type of the None singleton.

<a id="ConferencesGetParams"></a>

`ConferencesGetParams(*args, **kwargs)`
:   Parameters for conferences.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

<a id="ConferencesGtCondition"></a>

`ConferencesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.ConferencesSearchFilter`
    :   The type of the None singleton.

<a id="ConferencesGteCondition"></a>

`ConferencesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.ConferencesSearchFilter`
    :   The type of the None singleton.

<a id="ConferencesInCondition"></a>

`ConferencesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.twilio.types.ConferencesInFilter`
    :   The type of the None singleton.

<a id="ConferencesInFilter"></a>

`ConferencesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: list[str]`
    :   The account SID associated with the conference

    `date_created: list[str]`
    :   When the conference was created

    `date_updated: list[str]`
    :   When the conference was last updated

    `friendly_name: list[str]`
    :   A friendly name for the conference

    `region: list[str]`
    :   The region where the conference is hosted

    `sid: list[str]`
    :   The unique identifier of the conference

    `status: list[str]`
    :   The current status of the conference

<a id="ConferencesKeywordCondition"></a>

`ConferencesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.ConferencesStringFilter`
    :   The type of the None singleton.

<a id="ConferencesLikeCondition"></a>

`ConferencesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.ConferencesStringFilter`
    :   The type of the None singleton.

<a id="ConferencesListParams"></a>

`ConferencesListParams(*args, **kwargs)`
:   Parameters for conferences.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="ConferencesLtCondition"></a>

`ConferencesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.ConferencesSearchFilter`
    :   The type of the None singleton.

<a id="ConferencesLteCondition"></a>

`ConferencesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.ConferencesSearchFilter`
    :   The type of the None singleton.

<a id="ConferencesNeqCondition"></a>

`ConferencesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.ConferencesSearchFilter`
    :   The type of the None singleton.

<a id="ConferencesNotCondition"></a>

`ConferencesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.twilio.types.ConferencesEqCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesGtCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesGteCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLtCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLteCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesInCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesNotCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesAndCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesOrCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesAnyCondition`
    :   The type of the None singleton.

<a id="ConferencesOrCondition"></a>

`ConferencesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.twilio.types.ConferencesEqCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesGtCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesGteCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLtCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLteCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesInCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesNotCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesAndCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesOrCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesAnyCondition]`
    :   The type of the None singleton.

<a id="ConferencesSearchFilter"></a>

`ConferencesSearchFilter(*args, **kwargs)`
:   Available fields for filtering conferences search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str | None`
    :   The account SID associated with the conference

    `date_created: str | None`
    :   When the conference was created

    `date_updated: str | None`
    :   When the conference was last updated

    `friendly_name: str | None`
    :   A friendly name for the conference

    `region: str | None`
    :   The region where the conference is hosted

    `sid: str | None`
    :   The unique identifier of the conference

    `status: str | None`
    :   The current status of the conference

<a id="ConferencesSearchQuery"></a>

`ConferencesSearchQuery(*args, **kwargs)`
:   Search query for conferences entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.ConferencesEqCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesGtCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesGteCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLtCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLteCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesInCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesNotCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesAndCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesOrCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.ConferencesSortFilter]`
    :   The type of the None singleton.

<a id="ConferencesSortFilter"></a>

`ConferencesSortFilter(*args, **kwargs)`
:   Available fields for sorting conferences search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Literal['asc', 'desc']`
    :   The account SID associated with the conference

    `date_created: Literal['asc', 'desc']`
    :   When the conference was created

    `date_updated: Literal['asc', 'desc']`
    :   When the conference was last updated

    `friendly_name: Literal['asc', 'desc']`
    :   A friendly name for the conference

    `region: Literal['asc', 'desc']`
    :   The region where the conference is hosted

    `sid: Literal['asc', 'desc']`
    :   The unique identifier of the conference

    `status: Literal['asc', 'desc']`
    :   The current status of the conference

<a id="ConferencesStringFilter"></a>

`ConferencesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The account SID associated with the conference

    `date_created: str`
    :   When the conference was created

    `date_updated: str`
    :   When the conference was last updated

    `friendly_name: str`
    :   A friendly name for the conference

    `region: str`
    :   The region where the conference is hosted

    `sid: str`
    :   The unique identifier of the conference

    `status: str`
    :   The current status of the conference

<a id="IncomingPhoneNumbersAndCondition"></a>

`IncomingPhoneNumbersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersEqCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersNeqCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersGtCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersGteCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLtCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLteCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersInCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLikeCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersContainsCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersNotCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersAndCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersOrCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersAnyCondition]`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersAnyCondition"></a>

`IncomingPhoneNumbersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersAnyValueFilter`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersAnyValueFilter"></a>

`IncomingPhoneNumbersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Any`
    :   The SID of the account that owns this phone number

    `capabilities: Any`
    :   Capabilities of this phone number

    `date_created: Any`
    :   When the phone number was created

    `date_updated: Any`
    :   When the phone number was last updated

    `friendly_name: Any`
    :   A user-assigned friendly name for this phone number

    `phone_number: Any`
    :   The phone number in E.164 format

    `sid: Any`
    :   The SID of this phone number

    `status: Any`
    :   Status of the phone number

<a id="IncomingPhoneNumbersContainsCondition"></a>

`IncomingPhoneNumbersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersAnyValueFilter`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersEqCondition"></a>

`IncomingPhoneNumbersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersSearchFilter`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersFuzzyCondition"></a>

`IncomingPhoneNumbersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersStringFilter`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersGetParams"></a>

`IncomingPhoneNumbersGetParams(*args, **kwargs)`
:   Parameters for incoming_phone_numbers.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersGtCondition"></a>

`IncomingPhoneNumbersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersSearchFilter`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersGteCondition"></a>

`IncomingPhoneNumbersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersSearchFilter`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersInCondition"></a>

`IncomingPhoneNumbersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersInFilter`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersInFilter"></a>

`IncomingPhoneNumbersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: list[str]`
    :   The SID of the account that owns this phone number

    `capabilities: list[dict[str, typing.Any]]`
    :   Capabilities of this phone number

    `date_created: list[str]`
    :   When the phone number was created

    `date_updated: list[str]`
    :   When the phone number was last updated

    `friendly_name: list[str]`
    :   A user-assigned friendly name for this phone number

    `phone_number: list[str]`
    :   The phone number in E.164 format

    `sid: list[str]`
    :   The SID of this phone number

    `status: list[str]`
    :   Status of the phone number

<a id="IncomingPhoneNumbersKeywordCondition"></a>

`IncomingPhoneNumbersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersStringFilter`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersLikeCondition"></a>

`IncomingPhoneNumbersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersStringFilter`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersListParams"></a>

`IncomingPhoneNumbersListParams(*args, **kwargs)`
:   Parameters for incoming_phone_numbers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersLtCondition"></a>

`IncomingPhoneNumbersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersSearchFilter`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersLteCondition"></a>

`IncomingPhoneNumbersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersSearchFilter`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersNeqCondition"></a>

`IncomingPhoneNumbersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersSearchFilter`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersNotCondition"></a>

`IncomingPhoneNumbersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersEqCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersNeqCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersGtCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersGteCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLtCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLteCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersInCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLikeCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersContainsCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersNotCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersAndCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersOrCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersAnyCondition`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersOrCondition"></a>

`IncomingPhoneNumbersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersEqCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersNeqCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersGtCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersGteCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLtCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLteCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersInCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLikeCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersContainsCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersNotCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersAndCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersOrCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersAnyCondition]`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersSearchFilter"></a>

`IncomingPhoneNumbersSearchFilter(*args, **kwargs)`
:   Available fields for filtering incoming_phone_numbers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str | None`
    :   The SID of the account that owns this phone number

    `capabilities: dict[str, typing.Any] | None`
    :   Capabilities of this phone number

    `date_created: str | None`
    :   When the phone number was created

    `date_updated: str | None`
    :   When the phone number was last updated

    `friendly_name: str | None`
    :   A user-assigned friendly name for this phone number

    `phone_number: str | None`
    :   The phone number in E.164 format

    `sid: str | None`
    :   The SID of this phone number

    `status: str | None`
    :   Status of the phone number

<a id="IncomingPhoneNumbersSearchQuery"></a>

`IncomingPhoneNumbersSearchQuery(*args, **kwargs)`
:   Search query for incoming_phone_numbers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersEqCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersNeqCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersGtCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersGteCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLtCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLteCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersInCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLikeCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersContainsCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersNotCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersAndCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersOrCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersSortFilter]`
    :   The type of the None singleton.

<a id="IncomingPhoneNumbersSortFilter"></a>

`IncomingPhoneNumbersSortFilter(*args, **kwargs)`
:   Available fields for sorting incoming_phone_numbers search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Literal['asc', 'desc']`
    :   The SID of the account that owns this phone number

    `capabilities: Literal['asc', 'desc']`
    :   Capabilities of this phone number

    `date_created: Literal['asc', 'desc']`
    :   When the phone number was created

    `date_updated: Literal['asc', 'desc']`
    :   When the phone number was last updated

    `friendly_name: Literal['asc', 'desc']`
    :   A user-assigned friendly name for this phone number

    `phone_number: Literal['asc', 'desc']`
    :   The phone number in E.164 format

    `sid: Literal['asc', 'desc']`
    :   The SID of this phone number

    `status: Literal['asc', 'desc']`
    :   Status of the phone number

<a id="IncomingPhoneNumbersStringFilter"></a>

`IncomingPhoneNumbersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The SID of the account that owns this phone number

    `capabilities: str`
    :   Capabilities of this phone number

    `date_created: str`
    :   When the phone number was created

    `date_updated: str`
    :   When the phone number was last updated

    `friendly_name: str`
    :   A user-assigned friendly name for this phone number

    `phone_number: str`
    :   The phone number in E.164 format

    `sid: str`
    :   The SID of this phone number

    `status: str`
    :   Status of the phone number

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

    `and: list[airbyte_agent_sdk.connectors.twilio.types.MessagesEqCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesGtCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesGteCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLtCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLteCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesInCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesNotCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesAndCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesOrCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.twilio.types.MessagesAnyValueFilter`
    :   The type of the None singleton.

<a id="MessagesAnyValueFilter"></a>

`MessagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Any`
    :   The unique identifier for the account associated with this message

    `body: Any`
    :   The text body of the message

    `date_created: Any`
    :   The date and time when the message was created

    `date_sent: Any`
    :   The date and time when the message was sent

    `direction: Any`
    :   The direction of the message

    `error_code: Any`
    :   The error code associated with the message if any

    `error_message: Any`
    :   The error message description if the message failed

    `from_: Any`
    :   The phone number or sender ID that sent the message

    `num_media: Any`
    :   The number of media files included in the message

    `num_segments: Any`
    :   The number of message segments

    `price: Any`
    :   The cost of the message

    `price_unit: Any`
    :   The currency unit used for pricing

    `sid: Any`
    :   The unique identifier for this message

    `status: Any`
    :   The status of the message

    `to: Any`
    :   The phone number or recipient ID the message was sent to

<a id="MessagesContainsCondition"></a>

`MessagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.MessagesAnyValueFilter`
    :   The type of the None singleton.

<a id="MessagesEqCondition"></a>

`MessagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesFuzzyCondition"></a>

`MessagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.MessagesStringFilter`
    :   The type of the None singleton.

<a id="MessagesGetParams"></a>

`MessagesGetParams(*args, **kwargs)`
:   Parameters for messages.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

<a id="MessagesGtCondition"></a>

`MessagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesGteCondition"></a>

`MessagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.MessagesSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.twilio.types.MessagesInFilter`
    :   The type of the None singleton.

<a id="MessagesInFilter"></a>

`MessagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: list[str]`
    :   The unique identifier for the account associated with this message

    `body: list[str]`
    :   The text body of the message

    `date_created: list[str]`
    :   The date and time when the message was created

    `date_sent: list[str]`
    :   The date and time when the message was sent

    `direction: list[str]`
    :   The direction of the message

    `error_code: list[str]`
    :   The error code associated with the message if any

    `error_message: list[str]`
    :   The error message description if the message failed

    `from_: list[str]`
    :   The phone number or sender ID that sent the message

    `num_media: list[str]`
    :   The number of media files included in the message

    `num_segments: list[str]`
    :   The number of message segments

    `price: list[str]`
    :   The cost of the message

    `price_unit: list[str]`
    :   The currency unit used for pricing

    `sid: list[str]`
    :   The unique identifier for this message

    `status: list[str]`
    :   The status of the message

    `to: list[str]`
    :   The phone number or recipient ID the message was sent to

<a id="MessagesKeywordCondition"></a>

`MessagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.MessagesStringFilter`
    :   The type of the None singleton.

<a id="MessagesLikeCondition"></a>

`MessagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.MessagesStringFilter`
    :   The type of the None singleton.

<a id="MessagesListParams"></a>

`MessagesListParams(*args, **kwargs)`
:   Parameters for messages.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="MessagesLtCondition"></a>

`MessagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesLteCondition"></a>

`MessagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesNeqCondition"></a>

`MessagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.MessagesSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.twilio.types.MessagesEqCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesGtCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesGteCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLtCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLteCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesInCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesNotCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesAndCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesOrCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.twilio.types.MessagesEqCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesGtCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesGteCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLtCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLteCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesInCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesNotCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesAndCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesOrCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesAnyCondition]`
    :   The type of the None singleton.

<a id="MessagesSearchFilter"></a>

`MessagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering messages search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str | None`
    :   The unique identifier for the account associated with this message

    `body: str | None`
    :   The text body of the message

    `date_created: str | None`
    :   The date and time when the message was created

    `date_sent: str | None`
    :   The date and time when the message was sent

    `direction: str | None`
    :   The direction of the message

    `error_code: str | None`
    :   The error code associated with the message if any

    `error_message: str | None`
    :   The error message description if the message failed

    `from_: str | None`
    :   The phone number or sender ID that sent the message

    `num_media: str | None`
    :   The number of media files included in the message

    `num_segments: str | None`
    :   The number of message segments

    `price: str | None`
    :   The cost of the message

    `price_unit: str | None`
    :   The currency unit used for pricing

    `sid: str | None`
    :   The unique identifier for this message

    `status: str | None`
    :   The status of the message

    `to: str | None`
    :   The phone number or recipient ID the message was sent to

<a id="MessagesSearchQuery"></a>

`MessagesSearchQuery(*args, **kwargs)`
:   Search query for messages entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.MessagesEqCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesGtCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesGteCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLtCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLteCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesInCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesNotCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesAndCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesOrCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.MessagesSortFilter]`
    :   The type of the None singleton.

<a id="MessagesSortFilter"></a>

`MessagesSortFilter(*args, **kwargs)`
:   Available fields for sorting messages search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Literal['asc', 'desc']`
    :   The unique identifier for the account associated with this message

    `body: Literal['asc', 'desc']`
    :   The text body of the message

    `date_created: Literal['asc', 'desc']`
    :   The date and time when the message was created

    `date_sent: Literal['asc', 'desc']`
    :   The date and time when the message was sent

    `direction: Literal['asc', 'desc']`
    :   The direction of the message

    `error_code: Literal['asc', 'desc']`
    :   The error code associated with the message if any

    `error_message: Literal['asc', 'desc']`
    :   The error message description if the message failed

    `from_: Literal['asc', 'desc']`
    :   The phone number or sender ID that sent the message

    `num_media: Literal['asc', 'desc']`
    :   The number of media files included in the message

    `num_segments: Literal['asc', 'desc']`
    :   The number of message segments

    `price: Literal['asc', 'desc']`
    :   The cost of the message

    `price_unit: Literal['asc', 'desc']`
    :   The currency unit used for pricing

    `sid: Literal['asc', 'desc']`
    :   The unique identifier for this message

    `status: Literal['asc', 'desc']`
    :   The status of the message

    `to: Literal['asc', 'desc']`
    :   The phone number or recipient ID the message was sent to

<a id="MessagesStringFilter"></a>

`MessagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The unique identifier for the account associated with this message

    `body: str`
    :   The text body of the message

    `date_created: str`
    :   The date and time when the message was created

    `date_sent: str`
    :   The date and time when the message was sent

    `direction: str`
    :   The direction of the message

    `error_code: str`
    :   The error code associated with the message if any

    `error_message: str`
    :   The error message description if the message failed

    `from_: str`
    :   The phone number or sender ID that sent the message

    `num_media: str`
    :   The number of media files included in the message

    `num_segments: str`
    :   The number of message segments

    `price: str`
    :   The cost of the message

    `price_unit: str`
    :   The currency unit used for pricing

    `sid: str`
    :   The unique identifier for this message

    `status: str`
    :   The status of the message

    `to: str`
    :   The phone number or recipient ID the message was sent to

<a id="OutgoingCallerIdsAndCondition"></a>

`OutgoingCallerIdsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsEqCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsGtCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsGteCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLtCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLteCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsInCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsNotCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsAndCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsOrCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsAnyCondition]`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsAnyCondition"></a>

`OutgoingCallerIdsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsAnyValueFilter`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsAnyValueFilter"></a>

`OutgoingCallerIdsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Any`
    :   The account SID

    `date_created: Any`
    :   When the outgoing caller ID was created

    `date_updated: Any`
    :   When the outgoing caller ID was last updated

    `friendly_name: Any`
    :   A friendly name

    `phone_number: Any`
    :   The phone number

    `sid: Any`
    :   The unique identifier

<a id="OutgoingCallerIdsContainsCondition"></a>

`OutgoingCallerIdsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsAnyValueFilter`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsEqCondition"></a>

`OutgoingCallerIdsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsSearchFilter`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsFuzzyCondition"></a>

`OutgoingCallerIdsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsStringFilter`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsGetParams"></a>

`OutgoingCallerIdsGetParams(*args, **kwargs)`
:   Parameters for outgoing_caller_ids.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsGtCondition"></a>

`OutgoingCallerIdsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsSearchFilter`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsGteCondition"></a>

`OutgoingCallerIdsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsSearchFilter`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsInCondition"></a>

`OutgoingCallerIdsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsInFilter`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsInFilter"></a>

`OutgoingCallerIdsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: list[str]`
    :   The account SID

    `date_created: list[str]`
    :   When the outgoing caller ID was created

    `date_updated: list[str]`
    :   When the outgoing caller ID was last updated

    `friendly_name: list[str]`
    :   A friendly name

    `phone_number: list[str]`
    :   The phone number

    `sid: list[str]`
    :   The unique identifier

<a id="OutgoingCallerIdsKeywordCondition"></a>

`OutgoingCallerIdsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsStringFilter`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsLikeCondition"></a>

`OutgoingCallerIdsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsStringFilter`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsListParams"></a>

`OutgoingCallerIdsListParams(*args, **kwargs)`
:   Parameters for outgoing_caller_ids.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsLtCondition"></a>

`OutgoingCallerIdsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsSearchFilter`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsLteCondition"></a>

`OutgoingCallerIdsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsSearchFilter`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsNeqCondition"></a>

`OutgoingCallerIdsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsSearchFilter`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsNotCondition"></a>

`OutgoingCallerIdsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsEqCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsGtCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsGteCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLtCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLteCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsInCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsNotCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsAndCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsOrCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsAnyCondition`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsOrCondition"></a>

`OutgoingCallerIdsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsEqCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsGtCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsGteCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLtCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLteCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsInCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsNotCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsAndCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsOrCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsAnyCondition]`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsSearchFilter"></a>

`OutgoingCallerIdsSearchFilter(*args, **kwargs)`
:   Available fields for filtering outgoing_caller_ids search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str | None`
    :   The account SID

    `date_created: str | None`
    :   When the outgoing caller ID was created

    `date_updated: str | None`
    :   When the outgoing caller ID was last updated

    `friendly_name: str | None`
    :   A friendly name

    `phone_number: str | None`
    :   The phone number

    `sid: str | None`
    :   The unique identifier

<a id="OutgoingCallerIdsSearchQuery"></a>

`OutgoingCallerIdsSearchQuery(*args, **kwargs)`
:   Search query for outgoing_caller_ids entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsEqCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsGtCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsGteCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLtCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLteCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsInCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsNotCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsAndCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsOrCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsSortFilter]`
    :   The type of the None singleton.

<a id="OutgoingCallerIdsSortFilter"></a>

`OutgoingCallerIdsSortFilter(*args, **kwargs)`
:   Available fields for sorting outgoing_caller_ids search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Literal['asc', 'desc']`
    :   The account SID

    `date_created: Literal['asc', 'desc']`
    :   When the outgoing caller ID was created

    `date_updated: Literal['asc', 'desc']`
    :   When the outgoing caller ID was last updated

    `friendly_name: Literal['asc', 'desc']`
    :   A friendly name

    `phone_number: Literal['asc', 'desc']`
    :   The phone number

    `sid: Literal['asc', 'desc']`
    :   The unique identifier

<a id="OutgoingCallerIdsStringFilter"></a>

`OutgoingCallerIdsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The account SID

    `date_created: str`
    :   When the outgoing caller ID was created

    `date_updated: str`
    :   When the outgoing caller ID was last updated

    `friendly_name: str`
    :   A friendly name

    `phone_number: str`
    :   The phone number

    `sid: str`
    :   The unique identifier

<a id="QueuesAndCondition"></a>

`QueuesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.twilio.types.QueuesEqCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesGtCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesGteCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLtCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLteCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesInCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesNotCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesAndCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesOrCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesAnyCondition]`
    :   The type of the None singleton.

<a id="QueuesAnyCondition"></a>

`QueuesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.twilio.types.QueuesAnyValueFilter`
    :   The type of the None singleton.

<a id="QueuesAnyValueFilter"></a>

`QueuesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Any`
    :   The account SID that owns this queue

    `average_wait_time: Any`
    :   Average wait time in seconds

    `current_size: Any`
    :   Current number of callers waiting

    `date_created: Any`
    :   When the queue was created

    `date_updated: Any`
    :   When the queue was last updated

    `friendly_name: Any`
    :   A friendly name for the queue

    `max_size: Any`
    :   Maximum number of callers allowed

    `sid: Any`
    :   The unique identifier for the queue

<a id="QueuesContainsCondition"></a>

`QueuesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.QueuesAnyValueFilter`
    :   The type of the None singleton.

<a id="QueuesEqCondition"></a>

`QueuesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.QueuesSearchFilter`
    :   The type of the None singleton.

<a id="QueuesFuzzyCondition"></a>

`QueuesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.QueuesStringFilter`
    :   The type of the None singleton.

<a id="QueuesGetParams"></a>

`QueuesGetParams(*args, **kwargs)`
:   Parameters for queues.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

<a id="QueuesGtCondition"></a>

`QueuesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.QueuesSearchFilter`
    :   The type of the None singleton.

<a id="QueuesGteCondition"></a>

`QueuesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.QueuesSearchFilter`
    :   The type of the None singleton.

<a id="QueuesInCondition"></a>

`QueuesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.twilio.types.QueuesInFilter`
    :   The type of the None singleton.

<a id="QueuesInFilter"></a>

`QueuesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: list[str]`
    :   The account SID that owns this queue

    `average_wait_time: list[int]`
    :   Average wait time in seconds

    `current_size: list[int]`
    :   Current number of callers waiting

    `date_created: list[str]`
    :   When the queue was created

    `date_updated: list[str]`
    :   When the queue was last updated

    `friendly_name: list[str]`
    :   A friendly name for the queue

    `max_size: list[int]`
    :   Maximum number of callers allowed

    `sid: list[str]`
    :   The unique identifier for the queue

<a id="QueuesKeywordCondition"></a>

`QueuesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.QueuesStringFilter`
    :   The type of the None singleton.

<a id="QueuesLikeCondition"></a>

`QueuesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.QueuesStringFilter`
    :   The type of the None singleton.

<a id="QueuesListParams"></a>

`QueuesListParams(*args, **kwargs)`
:   Parameters for queues.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="QueuesLtCondition"></a>

`QueuesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.QueuesSearchFilter`
    :   The type of the None singleton.

<a id="QueuesLteCondition"></a>

`QueuesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.QueuesSearchFilter`
    :   The type of the None singleton.

<a id="QueuesNeqCondition"></a>

`QueuesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.QueuesSearchFilter`
    :   The type of the None singleton.

<a id="QueuesNotCondition"></a>

`QueuesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.twilio.types.QueuesEqCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesGtCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesGteCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLtCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLteCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesInCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesNotCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesAndCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesOrCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesAnyCondition`
    :   The type of the None singleton.

<a id="QueuesOrCondition"></a>

`QueuesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.twilio.types.QueuesEqCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesGtCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesGteCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLtCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLteCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesInCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesNotCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesAndCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesOrCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesAnyCondition]`
    :   The type of the None singleton.

<a id="QueuesSearchFilter"></a>

`QueuesSearchFilter(*args, **kwargs)`
:   Available fields for filtering queues search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str | None`
    :   The account SID that owns this queue

    `average_wait_time: int | None`
    :   Average wait time in seconds

    `current_size: int | None`
    :   Current number of callers waiting

    `date_created: str | None`
    :   When the queue was created

    `date_updated: str | None`
    :   When the queue was last updated

    `friendly_name: str | None`
    :   A friendly name for the queue

    `max_size: int | None`
    :   Maximum number of callers allowed

    `sid: str | None`
    :   The unique identifier for the queue

<a id="QueuesSearchQuery"></a>

`QueuesSearchQuery(*args, **kwargs)`
:   Search query for queues entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.QueuesEqCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesGtCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesGteCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLtCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLteCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesInCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesNotCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesAndCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesOrCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.QueuesSortFilter]`
    :   The type of the None singleton.

<a id="QueuesSortFilter"></a>

`QueuesSortFilter(*args, **kwargs)`
:   Available fields for sorting queues search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Literal['asc', 'desc']`
    :   The account SID that owns this queue

    `average_wait_time: Literal['asc', 'desc']`
    :   Average wait time in seconds

    `current_size: Literal['asc', 'desc']`
    :   Current number of callers waiting

    `date_created: Literal['asc', 'desc']`
    :   When the queue was created

    `date_updated: Literal['asc', 'desc']`
    :   When the queue was last updated

    `friendly_name: Literal['asc', 'desc']`
    :   A friendly name for the queue

    `max_size: Literal['asc', 'desc']`
    :   Maximum number of callers allowed

    `sid: Literal['asc', 'desc']`
    :   The unique identifier for the queue

<a id="QueuesStringFilter"></a>

`QueuesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The account SID that owns this queue

    `average_wait_time: str`
    :   Average wait time in seconds

    `current_size: str`
    :   Current number of callers waiting

    `date_created: str`
    :   When the queue was created

    `date_updated: str`
    :   When the queue was last updated

    `friendly_name: str`
    :   A friendly name for the queue

    `max_size: str`
    :   Maximum number of callers allowed

    `sid: str`
    :   The unique identifier for the queue

<a id="RecordingsAndCondition"></a>

`RecordingsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.twilio.types.RecordingsEqCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsGtCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsGteCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLtCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLteCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsInCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsNotCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsAndCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsOrCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsAnyCondition]`
    :   The type of the None singleton.

<a id="RecordingsAnyCondition"></a>

`RecordingsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.twilio.types.RecordingsAnyValueFilter`
    :   The type of the None singleton.

<a id="RecordingsAnyValueFilter"></a>

`RecordingsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Any`
    :   The account SID that owns the recording

    `call_sid: Any`
    :   The SID of the associated call

    `channels: Any`
    :   Number of audio channels

    `date_created: Any`
    :   When the recording was created

    `duration: Any`
    :   Duration in seconds

    `price: Any`
    :   The cost of storing the recording

    `price_unit: Any`
    :   The currency unit

    `sid: Any`
    :   The unique identifier of the recording

    `start_time: Any`
    :   When the recording started

    `status: Any`
    :   The status of the recording

<a id="RecordingsContainsCondition"></a>

`RecordingsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.RecordingsAnyValueFilter`
    :   The type of the None singleton.

<a id="RecordingsEqCondition"></a>

`RecordingsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.RecordingsSearchFilter`
    :   The type of the None singleton.

<a id="RecordingsFuzzyCondition"></a>

`RecordingsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.RecordingsStringFilter`
    :   The type of the None singleton.

<a id="RecordingsGetParams"></a>

`RecordingsGetParams(*args, **kwargs)`
:   Parameters for recordings.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

<a id="RecordingsGtCondition"></a>

`RecordingsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.RecordingsSearchFilter`
    :   The type of the None singleton.

<a id="RecordingsGteCondition"></a>

`RecordingsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.RecordingsSearchFilter`
    :   The type of the None singleton.

<a id="RecordingsInCondition"></a>

`RecordingsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.twilio.types.RecordingsInFilter`
    :   The type of the None singleton.

<a id="RecordingsInFilter"></a>

`RecordingsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: list[str]`
    :   The account SID that owns the recording

    `call_sid: list[str]`
    :   The SID of the associated call

    `channels: list[int]`
    :   Number of audio channels

    `date_created: list[str]`
    :   When the recording was created

    `duration: list[str]`
    :   Duration in seconds

    `price: list[str]`
    :   The cost of storing the recording

    `price_unit: list[str]`
    :   The currency unit

    `sid: list[str]`
    :   The unique identifier of the recording

    `start_time: list[str]`
    :   When the recording started

    `status: list[str]`
    :   The status of the recording

<a id="RecordingsKeywordCondition"></a>

`RecordingsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.RecordingsStringFilter`
    :   The type of the None singleton.

<a id="RecordingsLikeCondition"></a>

`RecordingsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.RecordingsStringFilter`
    :   The type of the None singleton.

<a id="RecordingsListParams"></a>

`RecordingsListParams(*args, **kwargs)`
:   Parameters for recordings.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="RecordingsLtCondition"></a>

`RecordingsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.RecordingsSearchFilter`
    :   The type of the None singleton.

<a id="RecordingsLteCondition"></a>

`RecordingsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.RecordingsSearchFilter`
    :   The type of the None singleton.

<a id="RecordingsNeqCondition"></a>

`RecordingsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.RecordingsSearchFilter`
    :   The type of the None singleton.

<a id="RecordingsNotCondition"></a>

`RecordingsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.twilio.types.RecordingsEqCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsGtCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsGteCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLtCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLteCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsInCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsNotCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsAndCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsOrCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsAnyCondition`
    :   The type of the None singleton.

<a id="RecordingsOrCondition"></a>

`RecordingsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.twilio.types.RecordingsEqCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsGtCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsGteCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLtCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLteCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsInCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsNotCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsAndCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsOrCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsAnyCondition]`
    :   The type of the None singleton.

<a id="RecordingsSearchFilter"></a>

`RecordingsSearchFilter(*args, **kwargs)`
:   Available fields for filtering recordings search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str | None`
    :   The account SID that owns the recording

    `call_sid: str | None`
    :   The SID of the associated call

    `channels: int | None`
    :   Number of audio channels

    `date_created: str | None`
    :   When the recording was created

    `duration: str | None`
    :   Duration in seconds

    `price: str | None`
    :   The cost of storing the recording

    `price_unit: str | None`
    :   The currency unit

    `sid: str | None`
    :   The unique identifier of the recording

    `start_time: str | None`
    :   When the recording started

    `status: str | None`
    :   The status of the recording

<a id="RecordingsSearchQuery"></a>

`RecordingsSearchQuery(*args, **kwargs)`
:   Search query for recordings entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.RecordingsEqCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsGtCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsGteCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLtCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLteCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsInCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsNotCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsAndCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsOrCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.RecordingsSortFilter]`
    :   The type of the None singleton.

<a id="RecordingsSortFilter"></a>

`RecordingsSortFilter(*args, **kwargs)`
:   Available fields for sorting recordings search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Literal['asc', 'desc']`
    :   The account SID that owns the recording

    `call_sid: Literal['asc', 'desc']`
    :   The SID of the associated call

    `channels: Literal['asc', 'desc']`
    :   Number of audio channels

    `date_created: Literal['asc', 'desc']`
    :   When the recording was created

    `duration: Literal['asc', 'desc']`
    :   Duration in seconds

    `price: Literal['asc', 'desc']`
    :   The cost of storing the recording

    `price_unit: Literal['asc', 'desc']`
    :   The currency unit

    `sid: Literal['asc', 'desc']`
    :   The unique identifier of the recording

    `start_time: Literal['asc', 'desc']`
    :   When the recording started

    `status: Literal['asc', 'desc']`
    :   The status of the recording

<a id="RecordingsStringFilter"></a>

`RecordingsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The account SID that owns the recording

    `call_sid: str`
    :   The SID of the associated call

    `channels: str`
    :   Number of audio channels

    `date_created: str`
    :   When the recording was created

    `duration: str`
    :   Duration in seconds

    `price: str`
    :   The cost of storing the recording

    `price_unit: str`
    :   The currency unit

    `sid: str`
    :   The unique identifier of the recording

    `start_time: str`
    :   When the recording started

    `status: str`
    :   The status of the recording

<a id="TranscriptionsAndCondition"></a>

`TranscriptionsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.twilio.types.TranscriptionsEqCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsGtCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsGteCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLtCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLteCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsInCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsNotCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsAndCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsOrCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsAnyCondition]`
    :   The type of the None singleton.

<a id="TranscriptionsAnyCondition"></a>

`TranscriptionsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsAnyValueFilter`
    :   The type of the None singleton.

<a id="TranscriptionsAnyValueFilter"></a>

`TranscriptionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Any`
    :   The account SID

    `date_created: Any`
    :   When the transcription was created

    `date_updated: Any`
    :   When the transcription was last updated

    `duration: Any`
    :   Duration of the audio recording in seconds

    `price: Any`
    :   The cost of the transcription

    `price_unit: Any`
    :   The currency unit

    `recording_sid: Any`
    :   The SID of the associated recording

    `sid: Any`
    :   The unique identifier for the transcription

    `status: Any`
    :   The status of the transcription

<a id="TranscriptionsContainsCondition"></a>

`TranscriptionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsAnyValueFilter`
    :   The type of the None singleton.

<a id="TranscriptionsEqCondition"></a>

`TranscriptionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsSearchFilter`
    :   The type of the None singleton.

<a id="TranscriptionsFuzzyCondition"></a>

`TranscriptionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsStringFilter`
    :   The type of the None singleton.

<a id="TranscriptionsGetParams"></a>

`TranscriptionsGetParams(*args, **kwargs)`
:   Parameters for transcriptions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

<a id="TranscriptionsGtCondition"></a>

`TranscriptionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsSearchFilter`
    :   The type of the None singleton.

<a id="TranscriptionsGteCondition"></a>

`TranscriptionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsSearchFilter`
    :   The type of the None singleton.

<a id="TranscriptionsInCondition"></a>

`TranscriptionsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsInFilter`
    :   The type of the None singleton.

<a id="TranscriptionsInFilter"></a>

`TranscriptionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: list[str]`
    :   The account SID

    `date_created: list[str]`
    :   When the transcription was created

    `date_updated: list[str]`
    :   When the transcription was last updated

    `duration: list[str]`
    :   Duration of the audio recording in seconds

    `price: list[str]`
    :   The cost of the transcription

    `price_unit: list[str]`
    :   The currency unit

    `recording_sid: list[str]`
    :   The SID of the associated recording

    `sid: list[str]`
    :   The unique identifier for the transcription

    `status: list[str]`
    :   The status of the transcription

<a id="TranscriptionsKeywordCondition"></a>

`TranscriptionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsStringFilter`
    :   The type of the None singleton.

<a id="TranscriptionsLikeCondition"></a>

`TranscriptionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsStringFilter`
    :   The type of the None singleton.

<a id="TranscriptionsListParams"></a>

`TranscriptionsListParams(*args, **kwargs)`
:   Parameters for transcriptions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="TranscriptionsLtCondition"></a>

`TranscriptionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsSearchFilter`
    :   The type of the None singleton.

<a id="TranscriptionsLteCondition"></a>

`TranscriptionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsSearchFilter`
    :   The type of the None singleton.

<a id="TranscriptionsNeqCondition"></a>

`TranscriptionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsSearchFilter`
    :   The type of the None singleton.

<a id="TranscriptionsNotCondition"></a>

`TranscriptionsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsEqCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsGtCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsGteCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLtCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLteCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsInCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsNotCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsAndCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsOrCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsAnyCondition`
    :   The type of the None singleton.

<a id="TranscriptionsOrCondition"></a>

`TranscriptionsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.twilio.types.TranscriptionsEqCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsGtCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsGteCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLtCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLteCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsInCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsNotCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsAndCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsOrCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsAnyCondition]`
    :   The type of the None singleton.

<a id="TranscriptionsSearchFilter"></a>

`TranscriptionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering transcriptions search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str | None`
    :   The account SID

    `date_created: str | None`
    :   When the transcription was created

    `date_updated: str | None`
    :   When the transcription was last updated

    `duration: str | None`
    :   Duration of the audio recording in seconds

    `price: str | None`
    :   The cost of the transcription

    `price_unit: str | None`
    :   The currency unit

    `recording_sid: str | None`
    :   The SID of the associated recording

    `sid: str | None`
    :   The unique identifier for the transcription

    `status: str | None`
    :   The status of the transcription

<a id="TranscriptionsSearchQuery"></a>

`TranscriptionsSearchQuery(*args, **kwargs)`
:   Search query for transcriptions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsEqCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsGtCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsGteCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLtCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLteCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsInCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsNotCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsAndCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsOrCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.TranscriptionsSortFilter]`
    :   The type of the None singleton.

<a id="TranscriptionsSortFilter"></a>

`TranscriptionsSortFilter(*args, **kwargs)`
:   Available fields for sorting transcriptions search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Literal['asc', 'desc']`
    :   The account SID

    `date_created: Literal['asc', 'desc']`
    :   When the transcription was created

    `date_updated: Literal['asc', 'desc']`
    :   When the transcription was last updated

    `duration: Literal['asc', 'desc']`
    :   Duration of the audio recording in seconds

    `price: Literal['asc', 'desc']`
    :   The cost of the transcription

    `price_unit: Literal['asc', 'desc']`
    :   The currency unit

    `recording_sid: Literal['asc', 'desc']`
    :   The SID of the associated recording

    `sid: Literal['asc', 'desc']`
    :   The unique identifier for the transcription

    `status: Literal['asc', 'desc']`
    :   The status of the transcription

<a id="TranscriptionsStringFilter"></a>

`TranscriptionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The account SID

    `date_created: str`
    :   When the transcription was created

    `date_updated: str`
    :   When the transcription was last updated

    `duration: str`
    :   Duration of the audio recording in seconds

    `price: str`
    :   The cost of the transcription

    `price_unit: str`
    :   The currency unit

    `recording_sid: str`
    :   The SID of the associated recording

    `sid: str`
    :   The unique identifier for the transcription

    `status: str`
    :   The status of the transcription

<a id="UsageRecordsAndCondition"></a>

`UsageRecordsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.twilio.types.UsageRecordsEqCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsGtCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsGteCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLtCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLteCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsInCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsNotCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsAndCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsOrCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsAnyCondition]`
    :   The type of the None singleton.

<a id="UsageRecordsAnyCondition"></a>

`UsageRecordsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsAnyValueFilter`
    :   The type of the None singleton.

<a id="UsageRecordsAnyValueFilter"></a>

`UsageRecordsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Any`
    :   The account SID associated with this usage record

    `category: Any`
    :   The usage category (calls, SMS, recordings, etc.)

    `count: Any`
    :   The number of units consumed

    `count_unit: Any`
    :   The unit of measurement for count

    `description: Any`
    :   A description of the usage record

    `end_date: Any`
    :   The end date of the usage period

    `price: Any`
    :   The total price for consumed units

    `price_unit: Any`
    :   The currency unit

    `start_date: Any`
    :   The start date of the usage period

    `usage: Any`
    :   The total usage value

    `usage_unit: Any`
    :   The unit of measurement for usage

<a id="UsageRecordsContainsCondition"></a>

`UsageRecordsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsAnyValueFilter`
    :   The type of the None singleton.

<a id="UsageRecordsEqCondition"></a>

`UsageRecordsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsSearchFilter`
    :   The type of the None singleton.

<a id="UsageRecordsFuzzyCondition"></a>

`UsageRecordsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsStringFilter`
    :   The type of the None singleton.

<a id="UsageRecordsGtCondition"></a>

`UsageRecordsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsSearchFilter`
    :   The type of the None singleton.

<a id="UsageRecordsGteCondition"></a>

`UsageRecordsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsSearchFilter`
    :   The type of the None singleton.

<a id="UsageRecordsInCondition"></a>

`UsageRecordsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsInFilter`
    :   The type of the None singleton.

<a id="UsageRecordsInFilter"></a>

`UsageRecordsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: list[str]`
    :   The account SID associated with this usage record

    `category: list[str]`
    :   The usage category (calls, SMS, recordings, etc.)

    `count: list[str]`
    :   The number of units consumed

    `count_unit: list[str]`
    :   The unit of measurement for count

    `description: list[str]`
    :   A description of the usage record

    `end_date: list[str]`
    :   The end date of the usage period

    `price: list[str]`
    :   The total price for consumed units

    `price_unit: list[str]`
    :   The currency unit

    `start_date: list[str]`
    :   The start date of the usage period

    `usage: list[str]`
    :   The total usage value

    `usage_unit: list[str]`
    :   The unit of measurement for usage

<a id="UsageRecordsKeywordCondition"></a>

`UsageRecordsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsStringFilter`
    :   The type of the None singleton.

<a id="UsageRecordsLikeCondition"></a>

`UsageRecordsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsStringFilter`
    :   The type of the None singleton.

<a id="UsageRecordsListParams"></a>

`UsageRecordsListParams(*args, **kwargs)`
:   Parameters for usage_records.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="UsageRecordsLtCondition"></a>

`UsageRecordsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsSearchFilter`
    :   The type of the None singleton.

<a id="UsageRecordsLteCondition"></a>

`UsageRecordsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsSearchFilter`
    :   The type of the None singleton.

<a id="UsageRecordsNeqCondition"></a>

`UsageRecordsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsSearchFilter`
    :   The type of the None singleton.

<a id="UsageRecordsNotCondition"></a>

`UsageRecordsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsEqCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsGtCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsGteCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLtCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLteCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsInCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsNotCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsAndCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsOrCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsAnyCondition`
    :   The type of the None singleton.

<a id="UsageRecordsOrCondition"></a>

`UsageRecordsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.twilio.types.UsageRecordsEqCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsGtCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsGteCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLtCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLteCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsInCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsNotCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsAndCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsOrCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsAnyCondition]`
    :   The type of the None singleton.

<a id="UsageRecordsSearchFilter"></a>

`UsageRecordsSearchFilter(*args, **kwargs)`
:   Available fields for filtering usage_records search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str | None`
    :   The account SID associated with this usage record

    `category: str | None`
    :   The usage category (calls, SMS, recordings, etc.)

    `count: str | None`
    :   The number of units consumed

    `count_unit: str | None`
    :   The unit of measurement for count

    `description: str | None`
    :   A description of the usage record

    `end_date: str | None`
    :   The end date of the usage period

    `price: str | None`
    :   The total price for consumed units

    `price_unit: str | None`
    :   The currency unit

    `start_date: str | None`
    :   The start date of the usage period

    `usage: str | None`
    :   The total usage value

    `usage_unit: str | None`
    :   The unit of measurement for usage

<a id="UsageRecordsSearchQuery"></a>

`UsageRecordsSearchQuery(*args, **kwargs)`
:   Search query for usage_records entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsEqCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsGtCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsGteCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLtCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLteCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsInCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsNotCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsAndCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsOrCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.UsageRecordsSortFilter]`
    :   The type of the None singleton.

<a id="UsageRecordsSortFilter"></a>

`UsageRecordsSortFilter(*args, **kwargs)`
:   Available fields for sorting usage_records search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: Literal['asc', 'desc']`
    :   The account SID associated with this usage record

    `category: Literal['asc', 'desc']`
    :   The usage category (calls, SMS, recordings, etc.)

    `count: Literal['asc', 'desc']`
    :   The number of units consumed

    `count_unit: Literal['asc', 'desc']`
    :   The unit of measurement for count

    `description: Literal['asc', 'desc']`
    :   A description of the usage record

    `end_date: Literal['asc', 'desc']`
    :   The end date of the usage period

    `price: Literal['asc', 'desc']`
    :   The total price for consumed units

    `price_unit: Literal['asc', 'desc']`
    :   The currency unit

    `start_date: Literal['asc', 'desc']`
    :   The start date of the usage period

    `usage: Literal['asc', 'desc']`
    :   The total usage value

    `usage_unit: Literal['asc', 'desc']`
    :   The unit of measurement for usage

<a id="UsageRecordsStringFilter"></a>

`UsageRecordsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The account SID associated with this usage record

    `category: str`
    :   The usage category (calls, SMS, recordings, etc.)

    `count: str`
    :   The number of units consumed

    `count_unit: str`
    :   The unit of measurement for count

    `description: str`
    :   A description of the usage record

    `end_date: str`
    :   The end date of the usage period

    `price: str`
    :   The total price for consumed units

    `price_unit: str`
    :   The currency unit

    `start_date: str`
    :   The start date of the usage period

    `usage: str`
    :   The total usage value

    `usage_unit: str`
    :   The unit of measurement for usage