---
id: airbyte_agent_sdk-connectors-twilio-types
title: airbyte_agent_sdk.connectors.twilio.types
---

Module airbyte_agent_sdk.connectors.twilio.types
================================================
Type definitions for twilio connector.

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

    `and: list[airbyte_agent_sdk.connectors.twilio.types.AccountsEqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsInCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNotCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAndCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsOrCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.twilio.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

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

`AccountsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

`AccountsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.AccountsStringFilter`
    :   The type of the None singleton.

`AccountsGetParams(*args, **kwargs)`
:   Parameters for accounts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `sid: str`
    :   The type of the None singleton.

`AccountsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.AccountsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.twilio.types.AccountsInFilter`
    :   The type of the None singleton.

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

`AccountsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.AccountsStringFilter`
    :   The type of the None singleton.

`AccountsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.AccountsStringFilter`
    :   The type of the None singleton.

`AccountsListParams(*args, **kwargs)`
:   Parameters for accounts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

`AccountsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.AccountsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.twilio.types.AccountsEqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsInCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNotCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAndCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsOrCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.twilio.types.AccountsEqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsInCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNotCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAndCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsOrCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAnyCondition]`
    :   The type of the None singleton.

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

`AccountsSearchQuery(*args, **kwargs)`
:   Search query for accounts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.AccountsEqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsGteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLtCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLteCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsInCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsNotCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAndCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsOrCondition | airbyte_agent_sdk.connectors.twilio.types.AccountsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.AccountsSortFilter]`
    :   The type of the None singleton.

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

`AddressesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.AddressesAnyValueFilter`
    :   The type of the None singleton.

`AddressesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.AddressesSearchFilter`
    :   The type of the None singleton.

`AddressesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.AddressesStringFilter`
    :   The type of the None singleton.

`AddressesGetParams(*args, **kwargs)`
:   Parameters for addresses.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

`AddressesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.AddressesSearchFilter`
    :   The type of the None singleton.

`AddressesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.AddressesSearchFilter`
    :   The type of the None singleton.

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

`AddressesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.AddressesStringFilter`
    :   The type of the None singleton.

`AddressesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.AddressesStringFilter`
    :   The type of the None singleton.

`AddressesListParams(*args, **kwargs)`
:   Parameters for addresses.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`AddressesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.AddressesSearchFilter`
    :   The type of the None singleton.

`AddressesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.AddressesSearchFilter`
    :   The type of the None singleton.

`AddressesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.AddressesSearchFilter`
    :   The type of the None singleton.

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

`AddressesSearchQuery(*args, **kwargs)`
:   Search query for addresses entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.AddressesEqCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesGtCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesGteCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLtCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLteCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesInCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesNotCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesAndCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesOrCondition | airbyte_agent_sdk.connectors.twilio.types.AddressesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.AddressesSortFilter]`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.twilio.types.CallsEqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsInCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.CallsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNotCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAndCondition | airbyte_agent_sdk.connectors.twilio.types.CallsOrCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.twilio.types.CallsAnyValueFilter`
    :   The type of the None singleton.

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

`CallsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.CallsAnyValueFilter`
    :   The type of the None singleton.

`CallsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.CallsSearchFilter`
    :   The type of the None singleton.

`CallsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.CallsStringFilter`
    :   The type of the None singleton.

`CallsGetParams(*args, **kwargs)`
:   Parameters for calls.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

`CallsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.CallsSearchFilter`
    :   The type of the None singleton.

`CallsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.CallsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.twilio.types.CallsInFilter`
    :   The type of the None singleton.

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

`CallsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.CallsStringFilter`
    :   The type of the None singleton.

`CallsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.CallsStringFilter`
    :   The type of the None singleton.

`CallsListParams(*args, **kwargs)`
:   Parameters for calls.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`CallsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.CallsSearchFilter`
    :   The type of the None singleton.

`CallsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.CallsSearchFilter`
    :   The type of the None singleton.

`CallsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.CallsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.twilio.types.CallsEqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsInCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.CallsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNotCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAndCondition | airbyte_agent_sdk.connectors.twilio.types.CallsOrCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.twilio.types.CallsEqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsInCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.CallsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNotCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAndCondition | airbyte_agent_sdk.connectors.twilio.types.CallsOrCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAnyCondition]`
    :   The type of the None singleton.

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

`CallsSearchQuery(*args, **kwargs)`
:   Search query for calls entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.CallsEqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsGteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLtCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLteCondition | airbyte_agent_sdk.connectors.twilio.types.CallsInCondition | airbyte_agent_sdk.connectors.twilio.types.CallsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.CallsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.CallsNotCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAndCondition | airbyte_agent_sdk.connectors.twilio.types.CallsOrCondition | airbyte_agent_sdk.connectors.twilio.types.CallsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.CallsSortFilter]`
    :   The type of the None singleton.

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

`ConferencesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.ConferencesAnyValueFilter`
    :   The type of the None singleton.

`ConferencesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.ConferencesSearchFilter`
    :   The type of the None singleton.

`ConferencesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.ConferencesStringFilter`
    :   The type of the None singleton.

`ConferencesGetParams(*args, **kwargs)`
:   Parameters for conferences.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

`ConferencesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.ConferencesSearchFilter`
    :   The type of the None singleton.

`ConferencesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.ConferencesSearchFilter`
    :   The type of the None singleton.

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

`ConferencesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.ConferencesStringFilter`
    :   The type of the None singleton.

`ConferencesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.ConferencesStringFilter`
    :   The type of the None singleton.

`ConferencesListParams(*args, **kwargs)`
:   Parameters for conferences.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`ConferencesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.ConferencesSearchFilter`
    :   The type of the None singleton.

`ConferencesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.ConferencesSearchFilter`
    :   The type of the None singleton.

`ConferencesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.ConferencesSearchFilter`
    :   The type of the None singleton.

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

`ConferencesSearchQuery(*args, **kwargs)`
:   Search query for conferences entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.ConferencesEqCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesGtCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesGteCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLtCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLteCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesInCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesNotCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesAndCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesOrCondition | airbyte_agent_sdk.connectors.twilio.types.ConferencesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.ConferencesSortFilter]`
    :   The type of the None singleton.

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

`IncomingPhoneNumbersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersAnyValueFilter`
    :   The type of the None singleton.

`IncomingPhoneNumbersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersSearchFilter`
    :   The type of the None singleton.

`IncomingPhoneNumbersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersStringFilter`
    :   The type of the None singleton.

`IncomingPhoneNumbersGetParams(*args, **kwargs)`
:   Parameters for incoming_phone_numbers.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

`IncomingPhoneNumbersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersSearchFilter`
    :   The type of the None singleton.

`IncomingPhoneNumbersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersSearchFilter`
    :   The type of the None singleton.

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

`IncomingPhoneNumbersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersStringFilter`
    :   The type of the None singleton.

`IncomingPhoneNumbersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersStringFilter`
    :   The type of the None singleton.

`IncomingPhoneNumbersListParams(*args, **kwargs)`
:   Parameters for incoming_phone_numbers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`IncomingPhoneNumbersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersSearchFilter`
    :   The type of the None singleton.

`IncomingPhoneNumbersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersSearchFilter`
    :   The type of the None singleton.

`IncomingPhoneNumbersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersSearchFilter`
    :   The type of the None singleton.

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

`IncomingPhoneNumbersSearchQuery(*args, **kwargs)`
:   Search query for incoming_phone_numbers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersEqCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersNeqCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersGtCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersGteCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLtCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLteCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersInCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersLikeCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersContainsCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersNotCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersAndCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersOrCondition | airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.IncomingPhoneNumbersSortFilter]`
    :   The type of the None singleton.

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

`MessagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.MessagesAnyValueFilter`
    :   The type of the None singleton.

`MessagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.MessagesSearchFilter`
    :   The type of the None singleton.

`MessagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.MessagesStringFilter`
    :   The type of the None singleton.

`MessagesGetParams(*args, **kwargs)`
:   Parameters for messages.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

`MessagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.MessagesSearchFilter`
    :   The type of the None singleton.

`MessagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.MessagesSearchFilter`
    :   The type of the None singleton.

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

`MessagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.MessagesStringFilter`
    :   The type of the None singleton.

`MessagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.MessagesStringFilter`
    :   The type of the None singleton.

`MessagesListParams(*args, **kwargs)`
:   Parameters for messages.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`MessagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.MessagesSearchFilter`
    :   The type of the None singleton.

`MessagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.MessagesSearchFilter`
    :   The type of the None singleton.

`MessagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.MessagesSearchFilter`
    :   The type of the None singleton.

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

`MessagesSearchQuery(*args, **kwargs)`
:   Search query for messages entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.MessagesEqCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesGtCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesGteCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLtCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLteCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesInCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesNotCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesAndCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesOrCondition | airbyte_agent_sdk.connectors.twilio.types.MessagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.MessagesSortFilter]`
    :   The type of the None singleton.

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

`OutgoingCallerIdsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsAnyValueFilter`
    :   The type of the None singleton.

`OutgoingCallerIdsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsSearchFilter`
    :   The type of the None singleton.

`OutgoingCallerIdsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsStringFilter`
    :   The type of the None singleton.

`OutgoingCallerIdsGetParams(*args, **kwargs)`
:   Parameters for outgoing_caller_ids.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

`OutgoingCallerIdsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsSearchFilter`
    :   The type of the None singleton.

`OutgoingCallerIdsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsSearchFilter`
    :   The type of the None singleton.

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

`OutgoingCallerIdsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsStringFilter`
    :   The type of the None singleton.

`OutgoingCallerIdsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsStringFilter`
    :   The type of the None singleton.

`OutgoingCallerIdsListParams(*args, **kwargs)`
:   Parameters for outgoing_caller_ids.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`OutgoingCallerIdsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsSearchFilter`
    :   The type of the None singleton.

`OutgoingCallerIdsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsSearchFilter`
    :   The type of the None singleton.

`OutgoingCallerIdsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsSearchFilter`
    :   The type of the None singleton.

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

`OutgoingCallerIdsSearchQuery(*args, **kwargs)`
:   Search query for outgoing_caller_ids entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsEqCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsGtCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsGteCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLtCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLteCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsInCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsNotCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsAndCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsOrCondition | airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.OutgoingCallerIdsSortFilter]`
    :   The type of the None singleton.

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

`QueuesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.QueuesAnyValueFilter`
    :   The type of the None singleton.

`QueuesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.QueuesSearchFilter`
    :   The type of the None singleton.

`QueuesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.QueuesStringFilter`
    :   The type of the None singleton.

`QueuesGetParams(*args, **kwargs)`
:   Parameters for queues.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

`QueuesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.QueuesSearchFilter`
    :   The type of the None singleton.

`QueuesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.QueuesSearchFilter`
    :   The type of the None singleton.

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

`QueuesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.QueuesStringFilter`
    :   The type of the None singleton.

`QueuesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.QueuesStringFilter`
    :   The type of the None singleton.

`QueuesListParams(*args, **kwargs)`
:   Parameters for queues.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`QueuesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.QueuesSearchFilter`
    :   The type of the None singleton.

`QueuesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.QueuesSearchFilter`
    :   The type of the None singleton.

`QueuesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.QueuesSearchFilter`
    :   The type of the None singleton.

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

`QueuesSearchQuery(*args, **kwargs)`
:   Search query for queues entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.QueuesEqCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesNeqCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesGtCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesGteCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLtCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLteCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesInCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesLikeCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesContainsCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesNotCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesAndCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesOrCondition | airbyte_agent_sdk.connectors.twilio.types.QueuesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.QueuesSortFilter]`
    :   The type of the None singleton.

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

`RecordingsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.RecordingsAnyValueFilter`
    :   The type of the None singleton.

`RecordingsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.RecordingsSearchFilter`
    :   The type of the None singleton.

`RecordingsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.RecordingsStringFilter`
    :   The type of the None singleton.

`RecordingsGetParams(*args, **kwargs)`
:   Parameters for recordings.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

`RecordingsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.RecordingsSearchFilter`
    :   The type of the None singleton.

`RecordingsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.RecordingsSearchFilter`
    :   The type of the None singleton.

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

`RecordingsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.RecordingsStringFilter`
    :   The type of the None singleton.

`RecordingsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.RecordingsStringFilter`
    :   The type of the None singleton.

`RecordingsListParams(*args, **kwargs)`
:   Parameters for recordings.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`RecordingsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.RecordingsSearchFilter`
    :   The type of the None singleton.

`RecordingsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.RecordingsSearchFilter`
    :   The type of the None singleton.

`RecordingsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.RecordingsSearchFilter`
    :   The type of the None singleton.

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

`RecordingsSearchQuery(*args, **kwargs)`
:   Search query for recordings entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.RecordingsEqCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsGtCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsGteCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLtCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLteCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsInCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsNotCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsAndCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsOrCondition | airbyte_agent_sdk.connectors.twilio.types.RecordingsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.RecordingsSortFilter]`
    :   The type of the None singleton.

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

`TranscriptionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsAnyValueFilter`
    :   The type of the None singleton.

`TranscriptionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsSearchFilter`
    :   The type of the None singleton.

`TranscriptionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsStringFilter`
    :   The type of the None singleton.

`TranscriptionsGetParams(*args, **kwargs)`
:   Parameters for transcriptions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `sid: str`
    :   The type of the None singleton.

`TranscriptionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsSearchFilter`
    :   The type of the None singleton.

`TranscriptionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsSearchFilter`
    :   The type of the None singleton.

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

`TranscriptionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsStringFilter`
    :   The type of the None singleton.

`TranscriptionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsStringFilter`
    :   The type of the None singleton.

`TranscriptionsListParams(*args, **kwargs)`
:   Parameters for transcriptions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`TranscriptionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsSearchFilter`
    :   The type of the None singleton.

`TranscriptionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsSearchFilter`
    :   The type of the None singleton.

`TranscriptionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsSearchFilter`
    :   The type of the None singleton.

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

`TranscriptionsSearchQuery(*args, **kwargs)`
:   Search query for transcriptions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.TranscriptionsEqCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsGtCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsGteCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLtCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLteCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsInCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsNotCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsAndCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsOrCondition | airbyte_agent_sdk.connectors.twilio.types.TranscriptionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.TranscriptionsSortFilter]`
    :   The type of the None singleton.

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

`UsageRecordsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsAnyValueFilter`
    :   The type of the None singleton.

`UsageRecordsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsSearchFilter`
    :   The type of the None singleton.

`UsageRecordsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsStringFilter`
    :   The type of the None singleton.

`UsageRecordsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsSearchFilter`
    :   The type of the None singleton.

`UsageRecordsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsSearchFilter`
    :   The type of the None singleton.

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

`UsageRecordsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsStringFilter`
    :   The type of the None singleton.

`UsageRecordsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsStringFilter`
    :   The type of the None singleton.

`UsageRecordsListParams(*args, **kwargs)`
:   Parameters for usage_records.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_sid: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`UsageRecordsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsSearchFilter`
    :   The type of the None singleton.

`UsageRecordsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsSearchFilter`
    :   The type of the None singleton.

`UsageRecordsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsSearchFilter`
    :   The type of the None singleton.

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

`UsageRecordsSearchQuery(*args, **kwargs)`
:   Search query for usage_records entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.twilio.types.UsageRecordsEqCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsNeqCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsGtCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsGteCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLtCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLteCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsInCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsLikeCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsFuzzyCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsKeywordCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsContainsCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsNotCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsAndCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsOrCondition | airbyte_agent_sdk.connectors.twilio.types.UsageRecordsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.twilio.types.UsageRecordsSortFilter]`
    :   The type of the None singleton.

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