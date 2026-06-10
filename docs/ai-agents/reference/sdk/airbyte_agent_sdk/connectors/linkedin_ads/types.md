---
id: airbyte_agent_sdk-connectors-linkedin_ads-types
title: airbyte_agent_sdk.connectors.linkedin_ads.types
---

Module airbyte_agent_sdk.connectors.linkedin_ads.types
======================================================
Type definitions for linkedin-ads connector.

Classes
-------

<a id="AccountUsersAndCondition"></a>

`AccountUsersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAnyCondition]`
    :   The type of the None singleton.

<a id="AccountUsersAnyCondition"></a>

`AccountUsersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountUsersAnyValueFilter"></a>

`AccountUsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Any`
    :   Associated account URN

    `role: Any`
    :   User role in the account

    `user: Any`
    :   User URN

<a id="AccountUsersContainsCondition"></a>

`AccountUsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountUsersEqCondition"></a>

`AccountUsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersSearchFilter`
    :   The type of the None singleton.

<a id="AccountUsersFuzzyCondition"></a>

`AccountUsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersStringFilter`
    :   The type of the None singleton.

<a id="AccountUsersGtCondition"></a>

`AccountUsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersSearchFilter`
    :   The type of the None singleton.

<a id="AccountUsersGteCondition"></a>

`AccountUsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersSearchFilter`
    :   The type of the None singleton.

<a id="AccountUsersInCondition"></a>

`AccountUsersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersInFilter`
    :   The type of the None singleton.

<a id="AccountUsersInFilter"></a>

`AccountUsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: list[str]`
    :   Associated account URN

    `role: list[str]`
    :   User role in the account

    `user: list[str]`
    :   User URN

<a id="AccountUsersKeywordCondition"></a>

`AccountUsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersStringFilter`
    :   The type of the None singleton.

<a id="AccountUsersLikeCondition"></a>

`AccountUsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersStringFilter`
    :   The type of the None singleton.

<a id="AccountUsersListParams"></a>

`AccountUsersListParams(*args, **kwargs)`
:   Parameters for account_users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accounts: str`
    :   The type of the None singleton.

    `count: int`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

    `start: int`
    :   The type of the None singleton.

<a id="AccountUsersLtCondition"></a>

`AccountUsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersSearchFilter`
    :   The type of the None singleton.

<a id="AccountUsersLteCondition"></a>

`AccountUsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersSearchFilter`
    :   The type of the None singleton.

<a id="AccountUsersNeqCondition"></a>

`AccountUsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersSearchFilter`
    :   The type of the None singleton.

<a id="AccountUsersNotCondition"></a>

`AccountUsersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAnyCondition`
    :   The type of the None singleton.

<a id="AccountUsersOrCondition"></a>

`AccountUsersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAnyCondition]`
    :   The type of the None singleton.

<a id="AccountUsersSearchFilter"></a>

`AccountUsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering account_users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str | None`
    :   Associated account URN

    `role: str | None`
    :   User role in the account

    `user: str | None`
    :   User URN

<a id="AccountUsersSearchQuery"></a>

`AccountUsersSearchQuery(*args, **kwargs)`
:   Search query for account_users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersSortFilter]`
    :   The type of the None singleton.

<a id="AccountUsersSortFilter"></a>

`AccountUsersSortFilter(*args, **kwargs)`
:   Available fields for sorting account_users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Literal['asc', 'desc']`
    :   Associated account URN

    `role: Literal['asc', 'desc']`
    :   User role in the account

    `user: Literal['asc', 'desc']`
    :   User URN

<a id="AccountUsersStringFilter"></a>

`AccountUsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   Associated account URN

    `role: str`
    :   User role in the account

    `user: str`
    :   User URN

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

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountsAnyValueFilter"></a>

`AccountsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `currency: Any`
    :   Currency code used by the account

    `id: Any`
    :   Unique account identifier

    `name: Any`
    :   Account name

    `notified_on_campaign_optimization: Any`
    :   Flag for notifications on campaign optimization

    `notified_on_creative_approval: Any`
    :   Flag for notifications on creative approval

    `notified_on_creative_rejection: Any`
    :   Flag for notifications on creative rejection

    `notified_on_end_of_campaign: Any`
    :   Flag for notifications on end of campaign

    `notified_on_new_features_enabled: Any`
    :   Flag for notifications on new features

    `reference: Any`
    :   Reference organization URN

    `serving_statuses: Any`
    :   List of serving statuses

    `status: Any`
    :   Account status

    `test: Any`
    :   Whether this is a test account

    `type_: Any`
    :   Account type

    `version: Any`
    :   Version information

<a id="AccountsContainsCondition"></a>

`AccountsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountsEqCondition"></a>

`AccountsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsFuzzyCondition"></a>

`AccountsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsGetParams"></a>

`AccountsGetParams(*args, **kwargs)`
:   Parameters for accounts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="AccountsGtCondition"></a>

`AccountsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsGteCondition"></a>

`AccountsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsInFilter`
    :   The type of the None singleton.

<a id="AccountsInFilter"></a>

`AccountsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `currency: list[str]`
    :   Currency code used by the account

    `id: list[int]`
    :   Unique account identifier

    `name: list[str]`
    :   Account name

    `notified_on_campaign_optimization: list[bool]`
    :   Flag for notifications on campaign optimization

    `notified_on_creative_approval: list[bool]`
    :   Flag for notifications on creative approval

    `notified_on_creative_rejection: list[bool]`
    :   Flag for notifications on creative rejection

    `notified_on_end_of_campaign: list[bool]`
    :   Flag for notifications on end of campaign

    `notified_on_new_features_enabled: list[bool]`
    :   Flag for notifications on new features

    `reference: list[str]`
    :   Reference organization URN

    `serving_statuses: list[list[typing.Any]]`
    :   List of serving statuses

    `status: list[str]`
    :   Account status

    `test: list[bool]`
    :   Whether this is a test account

    `type_: list[str]`
    :   Account type

    `version: list[dict[str, typing.Any]]`
    :   Version information

<a id="AccountsKeywordCondition"></a>

`AccountsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsLikeCondition"></a>

`AccountsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsListParams"></a>

`AccountsListParams(*args, **kwargs)`
:   Parameters for accounts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

<a id="AccountsLtCondition"></a>

`AccountsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsLteCondition"></a>

`AccountsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsNeqCondition"></a>

`AccountsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAnyCondition]`
    :   The type of the None singleton.

<a id="AccountsSearchFilter"></a>

`AccountsSearchFilter(*args, **kwargs)`
:   Available fields for filtering accounts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `currency: str | None`
    :   Currency code used by the account

    `id: int | None`
    :   Unique account identifier

    `name: str | None`
    :   Account name

    `notified_on_campaign_optimization: bool | None`
    :   Flag for notifications on campaign optimization

    `notified_on_creative_approval: bool | None`
    :   Flag for notifications on creative approval

    `notified_on_creative_rejection: bool | None`
    :   Flag for notifications on creative rejection

    `notified_on_end_of_campaign: bool | None`
    :   Flag for notifications on end of campaign

    `notified_on_new_features_enabled: bool | None`
    :   Flag for notifications on new features

    `reference: str | None`
    :   Reference organization URN

    `serving_statuses: list[typing.Any] | None`
    :   List of serving statuses

    `status: str | None`
    :   Account status

    `test: bool | None`
    :   Whether this is a test account

    `type_: str | None`
    :   Account type

    `version: dict[str, typing.Any] | None`
    :   Version information

<a id="AccountsSearchQuery"></a>

`AccountsSearchQuery(*args, **kwargs)`
:   Search query for accounts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsSortFilter]`
    :   The type of the None singleton.

<a id="AccountsSortFilter"></a>

`AccountsSortFilter(*args, **kwargs)`
:   Available fields for sorting accounts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `currency: Literal['asc', 'desc']`
    :   Currency code used by the account

    `id: Literal['asc', 'desc']`
    :   Unique account identifier

    `name: Literal['asc', 'desc']`
    :   Account name

    `notified_on_campaign_optimization: Literal['asc', 'desc']`
    :   Flag for notifications on campaign optimization

    `notified_on_creative_approval: Literal['asc', 'desc']`
    :   Flag for notifications on creative approval

    `notified_on_creative_rejection: Literal['asc', 'desc']`
    :   Flag for notifications on creative rejection

    `notified_on_end_of_campaign: Literal['asc', 'desc']`
    :   Flag for notifications on end of campaign

    `notified_on_new_features_enabled: Literal['asc', 'desc']`
    :   Flag for notifications on new features

    `reference: Literal['asc', 'desc']`
    :   Reference organization URN

    `serving_statuses: Literal['asc', 'desc']`
    :   List of serving statuses

    `status: Literal['asc', 'desc']`
    :   Account status

    `test: Literal['asc', 'desc']`
    :   Whether this is a test account

    `type_: Literal['asc', 'desc']`
    :   Account type

    `version: Literal['asc', 'desc']`
    :   Version information

<a id="AccountsStringFilter"></a>

`AccountsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `currency: str`
    :   Currency code used by the account

    `id: str`
    :   Unique account identifier

    `name: str`
    :   Account name

    `notified_on_campaign_optimization: str`
    :   Flag for notifications on campaign optimization

    `notified_on_creative_approval: str`
    :   Flag for notifications on creative approval

    `notified_on_creative_rejection: str`
    :   Flag for notifications on creative rejection

    `notified_on_end_of_campaign: str`
    :   Flag for notifications on end of campaign

    `notified_on_new_features_enabled: str`
    :   Flag for notifications on new features

    `reference: str`
    :   Reference organization URN

    `serving_statuses: str`
    :   List of serving statuses

    `status: str`
    :   Account status

    `test: str`
    :   Whether this is a test account

    `type_: str`
    :   Account type

    `version: str`
    :   Version information

<a id="AdCampaignAnalyticsAndCondition"></a>

`AdCampaignAnalyticsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsAnyCondition"></a>

`AdCampaignAnalyticsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsAnyValueFilter"></a>

`AdCampaignAnalyticsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Any`
    :   Number of action clicks

    `ad_unit_clicks: Any`
    :   Number of ad unit clicks

    `approximate_member_reach: Any`
    :   Approximate unique member reach

    `card_clicks: Any`
    :   Number of carousel card clicks

    `card_impressions: Any`
    :   Number of carousel card impressions

    `clicks: Any`
    :   Number of clicks on the ad

    `comment_likes: Any`
    :   Number of comment likes

    `comments: Any`
    :   Number of comments

    `company_page_clicks: Any`
    :   Number of company page clicks

    `conversion_value_in_local_currency: Any`
    :   Conversion value in local currency

    `cost_in_local_currency: Any`
    :   Total cost in the accounts local currency

    `cost_in_usd: Any`
    :   Total cost in USD

    `download_clicks: Any`
    :   Number of download clicks

    `end_date: Any`
    :   End date of the ad analytics data

    `external_website_conversions: Any`
    :   Number of conversions on external websites

    `external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites

    `external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites

    `follows: Any`
    :   Number of follows

    `full_screen_plays: Any`
    :   Number of full screen video plays

    `impressions: Any`
    :   Number of times the ad was shown

    `landing_page_clicks: Any`
    :   Number of landing page clicks

    `likes: Any`
    :   Number of likes

    `one_click_lead_form_opens: Any`
    :   Number of one-click lead form opens

    `one_click_leads: Any`
    :   Number of one-click leads

    `opens: Any`
    :   Number of opens (InMail)

    `other_engagements: Any`
    :   Number of other engagements

    `pivot_values: Any`
    :   Pivot values (URNs) for this analytics record

    `reactions: Any`
    :   Number of reactions

    `sends: Any`
    :   Number of sends (InMail)

    `shares: Any`
    :   Number of shares

    `start_date: Any`
    :   Start date of the ad analytics data

    `text_url_clicks: Any`
    :   Number of text URL clicks

    `total_engagements: Any`
    :   Total number of engagements

    `video_completions: Any`
    :   Number of times video played to 100%

    `video_first_quartile_completions: Any`
    :   Number of times video played to 25%

    `video_midpoint_completions: Any`
    :   Number of times video played to 50%

    `video_starts: Any`
    :   Number of video starts

    `video_third_quartile_completions: Any`
    :   Number of times video played to 75%

    `video_views: Any`
    :   Number of video views

<a id="AdCampaignAnalyticsContainsCondition"></a>

`AdCampaignAnalyticsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsEqCondition"></a>

`AdCampaignAnalyticsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsFuzzyCondition"></a>

`AdCampaignAnalyticsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsGtCondition"></a>

`AdCampaignAnalyticsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsGteCondition"></a>

`AdCampaignAnalyticsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsInCondition"></a>

`AdCampaignAnalyticsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsInFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsInFilter"></a>

`AdCampaignAnalyticsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: list[float]`
    :   Number of action clicks

    `ad_unit_clicks: list[float]`
    :   Number of ad unit clicks

    `approximate_member_reach: list[float]`
    :   Approximate unique member reach

    `card_clicks: list[float]`
    :   Number of carousel card clicks

    `card_impressions: list[float]`
    :   Number of carousel card impressions

    `clicks: list[float]`
    :   Number of clicks on the ad

    `comment_likes: list[float]`
    :   Number of comment likes

    `comments: list[float]`
    :   Number of comments

    `company_page_clicks: list[float]`
    :   Number of company page clicks

    `conversion_value_in_local_currency: list[float]`
    :   Conversion value in local currency

    `cost_in_local_currency: list[float]`
    :   Total cost in the accounts local currency

    `cost_in_usd: list[float]`
    :   Total cost in USD

    `download_clicks: list[float]`
    :   Number of download clicks

    `end_date: list[str]`
    :   End date of the ad analytics data

    `external_website_conversions: list[float]`
    :   Number of conversions on external websites

    `external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites

    `external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites

    `follows: list[float]`
    :   Number of follows

    `full_screen_plays: list[float]`
    :   Number of full screen video plays

    `impressions: list[float]`
    :   Number of times the ad was shown

    `landing_page_clicks: list[float]`
    :   Number of landing page clicks

    `likes: list[float]`
    :   Number of likes

    `one_click_lead_form_opens: list[float]`
    :   Number of one-click lead form opens

    `one_click_leads: list[float]`
    :   Number of one-click leads

    `opens: list[float]`
    :   Number of opens (InMail)

    `other_engagements: list[float]`
    :   Number of other engagements

    `pivot_values: list[list[typing.Any]]`
    :   Pivot values (URNs) for this analytics record

    `reactions: list[float]`
    :   Number of reactions

    `sends: list[float]`
    :   Number of sends (InMail)

    `shares: list[float]`
    :   Number of shares

    `start_date: list[str]`
    :   Start date of the ad analytics data

    `text_url_clicks: list[float]`
    :   Number of text URL clicks

    `total_engagements: list[float]`
    :   Total number of engagements

    `video_completions: list[float]`
    :   Number of times video played to 100%

    `video_first_quartile_completions: list[float]`
    :   Number of times video played to 25%

    `video_midpoint_completions: list[float]`
    :   Number of times video played to 50%

    `video_starts: list[float]`
    :   Number of video starts

    `video_third_quartile_completions: list[float]`
    :   Number of times video played to 75%

    `video_views: list[float]`
    :   Number of video views

<a id="AdCampaignAnalyticsKeywordCondition"></a>

`AdCampaignAnalyticsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsLikeCondition"></a>

`AdCampaignAnalyticsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsListParams"></a>

`AdCampaignAnalyticsListParams(*args, **kwargs)`
:   Parameters for ad_campaign_analytics.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaigns: str`
    :   The type of the None singleton.

    `date_range: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `pivot: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

    `time_granularity: str`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsLtCondition"></a>

`AdCampaignAnalyticsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsLteCondition"></a>

`AdCampaignAnalyticsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsNeqCondition"></a>

`AdCampaignAnalyticsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsNotCondition"></a>

`AdCampaignAnalyticsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAnyCondition`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsOrCondition"></a>

`AdCampaignAnalyticsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsSearchFilter"></a>

`AdCampaignAnalyticsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_campaign_analytics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: float | None`
    :   Number of action clicks

    `ad_unit_clicks: float | None`
    :   Number of ad unit clicks

    `approximate_member_reach: float | None`
    :   Approximate unique member reach

    `card_clicks: float | None`
    :   Number of carousel card clicks

    `card_impressions: float | None`
    :   Number of carousel card impressions

    `clicks: float | None`
    :   Number of clicks on the ad

    `comment_likes: float | None`
    :   Number of comment likes

    `comments: float | None`
    :   Number of comments

    `company_page_clicks: float | None`
    :   Number of company page clicks

    `conversion_value_in_local_currency: float | None`
    :   Conversion value in local currency

    `cost_in_local_currency: float | None`
    :   Total cost in the accounts local currency

    `cost_in_usd: float | None`
    :   Total cost in USD

    `download_clicks: float | None`
    :   Number of download clicks

    `end_date: str | None`
    :   End date of the ad analytics data

    `external_website_conversions: float | None`
    :   Number of conversions on external websites

    `external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites

    `external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites

    `follows: float | None`
    :   Number of follows

    `full_screen_plays: float | None`
    :   Number of full screen video plays

    `impressions: float | None`
    :   Number of times the ad was shown

    `landing_page_clicks: float | None`
    :   Number of landing page clicks

    `likes: float | None`
    :   Number of likes

    `one_click_lead_form_opens: float | None`
    :   Number of one-click lead form opens

    `one_click_leads: float | None`
    :   Number of one-click leads

    `opens: float | None`
    :   Number of opens (InMail)

    `other_engagements: float | None`
    :   Number of other engagements

    `pivot_values: list[typing.Any] | None`
    :   Pivot values (URNs) for this analytics record

    `reactions: float | None`
    :   Number of reactions

    `sends: float | None`
    :   Number of sends (InMail)

    `shares: float | None`
    :   Number of shares

    `start_date: str | None`
    :   Start date of the ad analytics data

    `text_url_clicks: float | None`
    :   Number of text URL clicks

    `total_engagements: float | None`
    :   Total number of engagements

    `video_completions: float | None`
    :   Number of times video played to 100%

    `video_first_quartile_completions: float | None`
    :   Number of times video played to 25%

    `video_midpoint_completions: float | None`
    :   Number of times video played to 50%

    `video_starts: float | None`
    :   Number of video starts

    `video_third_quartile_completions: float | None`
    :   Number of times video played to 75%

    `video_views: float | None`
    :   Number of video views

<a id="AdCampaignAnalyticsSearchQuery"></a>

`AdCampaignAnalyticsSearchQuery(*args, **kwargs)`
:   Search query for ad_campaign_analytics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsSortFilter]`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsSortFilter"></a>

`AdCampaignAnalyticsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_campaign_analytics search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Literal['asc', 'desc']`
    :   Number of action clicks

    `ad_unit_clicks: Literal['asc', 'desc']`
    :   Number of ad unit clicks

    `approximate_member_reach: Literal['asc', 'desc']`
    :   Approximate unique member reach

    `card_clicks: Literal['asc', 'desc']`
    :   Number of carousel card clicks

    `card_impressions: Literal['asc', 'desc']`
    :   Number of carousel card impressions

    `clicks: Literal['asc', 'desc']`
    :   Number of clicks on the ad

    `comment_likes: Literal['asc', 'desc']`
    :   Number of comment likes

    `comments: Literal['asc', 'desc']`
    :   Number of comments

    `company_page_clicks: Literal['asc', 'desc']`
    :   Number of company page clicks

    `conversion_value_in_local_currency: Literal['asc', 'desc']`
    :   Conversion value in local currency

    `cost_in_local_currency: Literal['asc', 'desc']`
    :   Total cost in the accounts local currency

    `cost_in_usd: Literal['asc', 'desc']`
    :   Total cost in USD

    `download_clicks: Literal['asc', 'desc']`
    :   Number of download clicks

    `end_date: Literal['asc', 'desc']`
    :   End date of the ad analytics data

    `external_website_conversions: Literal['asc', 'desc']`
    :   Number of conversions on external websites

    `external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites

    `external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites

    `follows: Literal['asc', 'desc']`
    :   Number of follows

    `full_screen_plays: Literal['asc', 'desc']`
    :   Number of full screen video plays

    `impressions: Literal['asc', 'desc']`
    :   Number of times the ad was shown

    `landing_page_clicks: Literal['asc', 'desc']`
    :   Number of landing page clicks

    `likes: Literal['asc', 'desc']`
    :   Number of likes

    `one_click_lead_form_opens: Literal['asc', 'desc']`
    :   Number of one-click lead form opens

    `one_click_leads: Literal['asc', 'desc']`
    :   Number of one-click leads

    `opens: Literal['asc', 'desc']`
    :   Number of opens (InMail)

    `other_engagements: Literal['asc', 'desc']`
    :   Number of other engagements

    `pivot_values: Literal['asc', 'desc']`
    :   Pivot values (URNs) for this analytics record

    `reactions: Literal['asc', 'desc']`
    :   Number of reactions

    `sends: Literal['asc', 'desc']`
    :   Number of sends (InMail)

    `shares: Literal['asc', 'desc']`
    :   Number of shares

    `start_date: Literal['asc', 'desc']`
    :   Start date of the ad analytics data

    `text_url_clicks: Literal['asc', 'desc']`
    :   Number of text URL clicks

    `total_engagements: Literal['asc', 'desc']`
    :   Total number of engagements

    `video_completions: Literal['asc', 'desc']`
    :   Number of times video played to 100%

    `video_first_quartile_completions: Literal['asc', 'desc']`
    :   Number of times video played to 25%

    `video_midpoint_completions: Literal['asc', 'desc']`
    :   Number of times video played to 50%

    `video_starts: Literal['asc', 'desc']`
    :   Number of video starts

    `video_third_quartile_completions: Literal['asc', 'desc']`
    :   Number of times video played to 75%

    `video_views: Literal['asc', 'desc']`
    :   Number of video views

<a id="AdCampaignAnalyticsStringFilter"></a>

`AdCampaignAnalyticsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: str`
    :   Number of action clicks

    `ad_unit_clicks: str`
    :   Number of ad unit clicks

    `approximate_member_reach: str`
    :   Approximate unique member reach

    `card_clicks: str`
    :   Number of carousel card clicks

    `card_impressions: str`
    :   Number of carousel card impressions

    `clicks: str`
    :   Number of clicks on the ad

    `comment_likes: str`
    :   Number of comment likes

    `comments: str`
    :   Number of comments

    `company_page_clicks: str`
    :   Number of company page clicks

    `conversion_value_in_local_currency: str`
    :   Conversion value in local currency

    `cost_in_local_currency: str`
    :   Total cost in the accounts local currency

    `cost_in_usd: str`
    :   Total cost in USD

    `download_clicks: str`
    :   Number of download clicks

    `end_date: str`
    :   End date of the ad analytics data

    `external_website_conversions: str`
    :   Number of conversions on external websites

    `external_website_post_click_conversions: str`
    :   Post-click conversions on external websites

    `external_website_post_view_conversions: str`
    :   Post-view conversions on external websites

    `follows: str`
    :   Number of follows

    `full_screen_plays: str`
    :   Number of full screen video plays

    `impressions: str`
    :   Number of times the ad was shown

    `landing_page_clicks: str`
    :   Number of landing page clicks

    `likes: str`
    :   Number of likes

    `one_click_lead_form_opens: str`
    :   Number of one-click lead form opens

    `one_click_leads: str`
    :   Number of one-click leads

    `opens: str`
    :   Number of opens (InMail)

    `other_engagements: str`
    :   Number of other engagements

    `pivot_values: str`
    :   Pivot values (URNs) for this analytics record

    `reactions: str`
    :   Number of reactions

    `sends: str`
    :   Number of sends (InMail)

    `shares: str`
    :   Number of shares

    `start_date: str`
    :   Start date of the ad analytics data

    `text_url_clicks: str`
    :   Number of text URL clicks

    `total_engagements: str`
    :   Total number of engagements

    `video_completions: str`
    :   Number of times video played to 100%

    `video_first_quartile_completions: str`
    :   Number of times video played to 25%

    `video_midpoint_completions: str`
    :   Number of times video played to 50%

    `video_starts: str`
    :   Number of video starts

    `video_third_quartile_completions: str`
    :   Number of times video played to 75%

    `video_views: str`
    :   Number of video views

<a id="AdCreativeAnalyticsAndCondition"></a>

`AdCreativeAnalyticsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsAnyCondition"></a>

`AdCreativeAnalyticsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsAnyValueFilter"></a>

`AdCreativeAnalyticsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Any`
    :   Number of action clicks

    `ad_unit_clicks: Any`
    :   Number of ad unit clicks

    `approximate_member_reach: Any`
    :   Approximate unique member reach

    `card_clicks: Any`
    :   Number of carousel card clicks

    `card_impressions: Any`
    :   Number of carousel card impressions

    `clicks: Any`
    :   Number of clicks on the ad

    `comment_likes: Any`
    :   Number of comment likes

    `comments: Any`
    :   Number of comments

    `company_page_clicks: Any`
    :   Number of company page clicks

    `conversion_value_in_local_currency: Any`
    :   Conversion value in local currency

    `cost_in_local_currency: Any`
    :   Total cost in the accounts local currency

    `cost_in_usd: Any`
    :   Total cost in USD

    `download_clicks: Any`
    :   Number of download clicks

    `end_date: Any`
    :   End date of the ad analytics data

    `external_website_conversions: Any`
    :   Number of conversions on external websites

    `external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites

    `external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites

    `follows: Any`
    :   Number of follows

    `full_screen_plays: Any`
    :   Number of full screen video plays

    `impressions: Any`
    :   Number of times the ad was shown

    `landing_page_clicks: Any`
    :   Number of landing page clicks

    `likes: Any`
    :   Number of likes

    `one_click_lead_form_opens: Any`
    :   Number of one-click lead form opens

    `one_click_leads: Any`
    :   Number of one-click leads

    `opens: Any`
    :   Number of opens (InMail)

    `other_engagements: Any`
    :   Number of other engagements

    `pivot_values: Any`
    :   Pivot values (URNs) for this analytics record

    `reactions: Any`
    :   Number of reactions

    `sends: Any`
    :   Number of sends (InMail)

    `shares: Any`
    :   Number of shares

    `start_date: Any`
    :   Start date of the ad analytics data

    `text_url_clicks: Any`
    :   Number of text URL clicks

    `total_engagements: Any`
    :   Total number of engagements

    `video_completions: Any`
    :   Number of times video played to 100%

    `video_first_quartile_completions: Any`
    :   Number of times video played to 25%

    `video_midpoint_completions: Any`
    :   Number of times video played to 50%

    `video_starts: Any`
    :   Number of video starts

    `video_third_quartile_completions: Any`
    :   Number of times video played to 75%

    `video_views: Any`
    :   Number of video views

<a id="AdCreativeAnalyticsContainsCondition"></a>

`AdCreativeAnalyticsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsEqCondition"></a>

`AdCreativeAnalyticsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsFuzzyCondition"></a>

`AdCreativeAnalyticsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsGtCondition"></a>

`AdCreativeAnalyticsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsGteCondition"></a>

`AdCreativeAnalyticsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsInCondition"></a>

`AdCreativeAnalyticsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsInFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsInFilter"></a>

`AdCreativeAnalyticsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: list[float]`
    :   Number of action clicks

    `ad_unit_clicks: list[float]`
    :   Number of ad unit clicks

    `approximate_member_reach: list[float]`
    :   Approximate unique member reach

    `card_clicks: list[float]`
    :   Number of carousel card clicks

    `card_impressions: list[float]`
    :   Number of carousel card impressions

    `clicks: list[float]`
    :   Number of clicks on the ad

    `comment_likes: list[float]`
    :   Number of comment likes

    `comments: list[float]`
    :   Number of comments

    `company_page_clicks: list[float]`
    :   Number of company page clicks

    `conversion_value_in_local_currency: list[float]`
    :   Conversion value in local currency

    `cost_in_local_currency: list[float]`
    :   Total cost in the accounts local currency

    `cost_in_usd: list[float]`
    :   Total cost in USD

    `download_clicks: list[float]`
    :   Number of download clicks

    `end_date: list[str]`
    :   End date of the ad analytics data

    `external_website_conversions: list[float]`
    :   Number of conversions on external websites

    `external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites

    `external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites

    `follows: list[float]`
    :   Number of follows

    `full_screen_plays: list[float]`
    :   Number of full screen video plays

    `impressions: list[float]`
    :   Number of times the ad was shown

    `landing_page_clicks: list[float]`
    :   Number of landing page clicks

    `likes: list[float]`
    :   Number of likes

    `one_click_lead_form_opens: list[float]`
    :   Number of one-click lead form opens

    `one_click_leads: list[float]`
    :   Number of one-click leads

    `opens: list[float]`
    :   Number of opens (InMail)

    `other_engagements: list[float]`
    :   Number of other engagements

    `pivot_values: list[list[typing.Any]]`
    :   Pivot values (URNs) for this analytics record

    `reactions: list[float]`
    :   Number of reactions

    `sends: list[float]`
    :   Number of sends (InMail)

    `shares: list[float]`
    :   Number of shares

    `start_date: list[str]`
    :   Start date of the ad analytics data

    `text_url_clicks: list[float]`
    :   Number of text URL clicks

    `total_engagements: list[float]`
    :   Total number of engagements

    `video_completions: list[float]`
    :   Number of times video played to 100%

    `video_first_quartile_completions: list[float]`
    :   Number of times video played to 25%

    `video_midpoint_completions: list[float]`
    :   Number of times video played to 50%

    `video_starts: list[float]`
    :   Number of video starts

    `video_third_quartile_completions: list[float]`
    :   Number of times video played to 75%

    `video_views: list[float]`
    :   Number of video views

<a id="AdCreativeAnalyticsKeywordCondition"></a>

`AdCreativeAnalyticsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsLikeCondition"></a>

`AdCreativeAnalyticsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsListParams"></a>

`AdCreativeAnalyticsListParams(*args, **kwargs)`
:   Parameters for ad_creative_analytics.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `creatives: str`
    :   The type of the None singleton.

    `date_range: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `pivot: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

    `time_granularity: str`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsLtCondition"></a>

`AdCreativeAnalyticsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsLteCondition"></a>

`AdCreativeAnalyticsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsNeqCondition"></a>

`AdCreativeAnalyticsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsNotCondition"></a>

`AdCreativeAnalyticsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAnyCondition`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsOrCondition"></a>

`AdCreativeAnalyticsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsSearchFilter"></a>

`AdCreativeAnalyticsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_creative_analytics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: float | None`
    :   Number of action clicks

    `ad_unit_clicks: float | None`
    :   Number of ad unit clicks

    `approximate_member_reach: float | None`
    :   Approximate unique member reach

    `card_clicks: float | None`
    :   Number of carousel card clicks

    `card_impressions: float | None`
    :   Number of carousel card impressions

    `clicks: float | None`
    :   Number of clicks on the ad

    `comment_likes: float | None`
    :   Number of comment likes

    `comments: float | None`
    :   Number of comments

    `company_page_clicks: float | None`
    :   Number of company page clicks

    `conversion_value_in_local_currency: float | None`
    :   Conversion value in local currency

    `cost_in_local_currency: float | None`
    :   Total cost in the accounts local currency

    `cost_in_usd: float | None`
    :   Total cost in USD

    `download_clicks: float | None`
    :   Number of download clicks

    `end_date: str | None`
    :   End date of the ad analytics data

    `external_website_conversions: float | None`
    :   Number of conversions on external websites

    `external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites

    `external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites

    `follows: float | None`
    :   Number of follows

    `full_screen_plays: float | None`
    :   Number of full screen video plays

    `impressions: float | None`
    :   Number of times the ad was shown

    `landing_page_clicks: float | None`
    :   Number of landing page clicks

    `likes: float | None`
    :   Number of likes

    `one_click_lead_form_opens: float | None`
    :   Number of one-click lead form opens

    `one_click_leads: float | None`
    :   Number of one-click leads

    `opens: float | None`
    :   Number of opens (InMail)

    `other_engagements: float | None`
    :   Number of other engagements

    `pivot_values: list[typing.Any] | None`
    :   Pivot values (URNs) for this analytics record

    `reactions: float | None`
    :   Number of reactions

    `sends: float | None`
    :   Number of sends (InMail)

    `shares: float | None`
    :   Number of shares

    `start_date: str | None`
    :   Start date of the ad analytics data

    `text_url_clicks: float | None`
    :   Number of text URL clicks

    `total_engagements: float | None`
    :   Total number of engagements

    `video_completions: float | None`
    :   Number of times video played to 100%

    `video_first_quartile_completions: float | None`
    :   Number of times video played to 25%

    `video_midpoint_completions: float | None`
    :   Number of times video played to 50%

    `video_starts: float | None`
    :   Number of video starts

    `video_third_quartile_completions: float | None`
    :   Number of times video played to 75%

    `video_views: float | None`
    :   Number of video views

<a id="AdCreativeAnalyticsSearchQuery"></a>

`AdCreativeAnalyticsSearchQuery(*args, **kwargs)`
:   Search query for ad_creative_analytics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsSortFilter]`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsSortFilter"></a>

`AdCreativeAnalyticsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_creative_analytics search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Literal['asc', 'desc']`
    :   Number of action clicks

    `ad_unit_clicks: Literal['asc', 'desc']`
    :   Number of ad unit clicks

    `approximate_member_reach: Literal['asc', 'desc']`
    :   Approximate unique member reach

    `card_clicks: Literal['asc', 'desc']`
    :   Number of carousel card clicks

    `card_impressions: Literal['asc', 'desc']`
    :   Number of carousel card impressions

    `clicks: Literal['asc', 'desc']`
    :   Number of clicks on the ad

    `comment_likes: Literal['asc', 'desc']`
    :   Number of comment likes

    `comments: Literal['asc', 'desc']`
    :   Number of comments

    `company_page_clicks: Literal['asc', 'desc']`
    :   Number of company page clicks

    `conversion_value_in_local_currency: Literal['asc', 'desc']`
    :   Conversion value in local currency

    `cost_in_local_currency: Literal['asc', 'desc']`
    :   Total cost in the accounts local currency

    `cost_in_usd: Literal['asc', 'desc']`
    :   Total cost in USD

    `download_clicks: Literal['asc', 'desc']`
    :   Number of download clicks

    `end_date: Literal['asc', 'desc']`
    :   End date of the ad analytics data

    `external_website_conversions: Literal['asc', 'desc']`
    :   Number of conversions on external websites

    `external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites

    `external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites

    `follows: Literal['asc', 'desc']`
    :   Number of follows

    `full_screen_plays: Literal['asc', 'desc']`
    :   Number of full screen video plays

    `impressions: Literal['asc', 'desc']`
    :   Number of times the ad was shown

    `landing_page_clicks: Literal['asc', 'desc']`
    :   Number of landing page clicks

    `likes: Literal['asc', 'desc']`
    :   Number of likes

    `one_click_lead_form_opens: Literal['asc', 'desc']`
    :   Number of one-click lead form opens

    `one_click_leads: Literal['asc', 'desc']`
    :   Number of one-click leads

    `opens: Literal['asc', 'desc']`
    :   Number of opens (InMail)

    `other_engagements: Literal['asc', 'desc']`
    :   Number of other engagements

    `pivot_values: Literal['asc', 'desc']`
    :   Pivot values (URNs) for this analytics record

    `reactions: Literal['asc', 'desc']`
    :   Number of reactions

    `sends: Literal['asc', 'desc']`
    :   Number of sends (InMail)

    `shares: Literal['asc', 'desc']`
    :   Number of shares

    `start_date: Literal['asc', 'desc']`
    :   Start date of the ad analytics data

    `text_url_clicks: Literal['asc', 'desc']`
    :   Number of text URL clicks

    `total_engagements: Literal['asc', 'desc']`
    :   Total number of engagements

    `video_completions: Literal['asc', 'desc']`
    :   Number of times video played to 100%

    `video_first_quartile_completions: Literal['asc', 'desc']`
    :   Number of times video played to 25%

    `video_midpoint_completions: Literal['asc', 'desc']`
    :   Number of times video played to 50%

    `video_starts: Literal['asc', 'desc']`
    :   Number of video starts

    `video_third_quartile_completions: Literal['asc', 'desc']`
    :   Number of times video played to 75%

    `video_views: Literal['asc', 'desc']`
    :   Number of video views

<a id="AdCreativeAnalyticsStringFilter"></a>

`AdCreativeAnalyticsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: str`
    :   Number of action clicks

    `ad_unit_clicks: str`
    :   Number of ad unit clicks

    `approximate_member_reach: str`
    :   Approximate unique member reach

    `card_clicks: str`
    :   Number of carousel card clicks

    `card_impressions: str`
    :   Number of carousel card impressions

    `clicks: str`
    :   Number of clicks on the ad

    `comment_likes: str`
    :   Number of comment likes

    `comments: str`
    :   Number of comments

    `company_page_clicks: str`
    :   Number of company page clicks

    `conversion_value_in_local_currency: str`
    :   Conversion value in local currency

    `cost_in_local_currency: str`
    :   Total cost in the accounts local currency

    `cost_in_usd: str`
    :   Total cost in USD

    `download_clicks: str`
    :   Number of download clicks

    `end_date: str`
    :   End date of the ad analytics data

    `external_website_conversions: str`
    :   Number of conversions on external websites

    `external_website_post_click_conversions: str`
    :   Post-click conversions on external websites

    `external_website_post_view_conversions: str`
    :   Post-view conversions on external websites

    `follows: str`
    :   Number of follows

    `full_screen_plays: str`
    :   Number of full screen video plays

    `impressions: str`
    :   Number of times the ad was shown

    `landing_page_clicks: str`
    :   Number of landing page clicks

    `likes: str`
    :   Number of likes

    `one_click_lead_form_opens: str`
    :   Number of one-click lead form opens

    `one_click_leads: str`
    :   Number of one-click leads

    `opens: str`
    :   Number of opens (InMail)

    `other_engagements: str`
    :   Number of other engagements

    `pivot_values: str`
    :   Pivot values (URNs) for this analytics record

    `reactions: str`
    :   Number of reactions

    `sends: str`
    :   Number of sends (InMail)

    `shares: str`
    :   Number of shares

    `start_date: str`
    :   Start date of the ad analytics data

    `text_url_clicks: str`
    :   Number of text URL clicks

    `total_engagements: str`
    :   Total number of engagements

    `video_completions: str`
    :   Number of times video played to 100%

    `video_first_quartile_completions: str`
    :   Number of times video played to 25%

    `video_midpoint_completions: str`
    :   Number of times video played to 50%

    `video_starts: str`
    :   Number of video starts

    `video_third_quartile_completions: str`
    :   Number of times video played to 75%

    `video_views: str`
    :   Number of video views

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

<a id="CampaignGroupsAndCondition"></a>

`CampaignGroupsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignGroupsAnyCondition"></a>

`CampaignGroupsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsAnyValueFilter"></a>

`CampaignGroupsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Any`
    :   Associated account URN

    `allowed_campaign_types: Any`
    :   Types of campaigns allowed in this group

    `backfilled: Any`
    :   Whether the campaign group is backfilled

    `id: Any`
    :   Unique campaign group identifier

    `name: Any`
    :   Campaign group name

    `run_schedule: Any`
    :   Campaign group run schedule

    `serving_statuses: Any`
    :   List of serving statuses

    `status: Any`
    :   Campaign group status

    `test: Any`
    :   Whether this is a test campaign group

    `total_budget: Any`
    :   Total budget for the campaign group

<a id="CampaignGroupsContainsCondition"></a>

`CampaignGroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsEqCondition"></a>

`CampaignGroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsFuzzyCondition"></a>

`CampaignGroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsStringFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsGetParams"></a>

`CampaignGroupsGetParams(*args, **kwargs)`
:   Parameters for campaign_groups.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

<a id="CampaignGroupsGtCondition"></a>

`CampaignGroupsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsGteCondition"></a>

`CampaignGroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsInCondition"></a>

`CampaignGroupsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsInFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsInFilter"></a>

`CampaignGroupsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: list[str]`
    :   Associated account URN

    `allowed_campaign_types: list[list[typing.Any]]`
    :   Types of campaigns allowed in this group

    `backfilled: list[bool]`
    :   Whether the campaign group is backfilled

    `id: list[int]`
    :   Unique campaign group identifier

    `name: list[str]`
    :   Campaign group name

    `run_schedule: list[dict[str, typing.Any]]`
    :   Campaign group run schedule

    `serving_statuses: list[list[typing.Any]]`
    :   List of serving statuses

    `status: list[str]`
    :   Campaign group status

    `test: list[bool]`
    :   Whether this is a test campaign group

    `total_budget: list[dict[str, typing.Any]]`
    :   Total budget for the campaign group

<a id="CampaignGroupsKeywordCondition"></a>

`CampaignGroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsStringFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsLikeCondition"></a>

`CampaignGroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsStringFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsListParams"></a>

`CampaignGroupsListParams(*args, **kwargs)`
:   Parameters for campaign_groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

<a id="CampaignGroupsLtCondition"></a>

`CampaignGroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsLteCondition"></a>

`CampaignGroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsNeqCondition"></a>

`CampaignGroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsNotCondition"></a>

`CampaignGroupsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAnyCondition`
    :   The type of the None singleton.

<a id="CampaignGroupsOrCondition"></a>

`CampaignGroupsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignGroupsSearchFilter"></a>

`CampaignGroupsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaign_groups search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str | None`
    :   Associated account URN

    `allowed_campaign_types: list[typing.Any] | None`
    :   Types of campaigns allowed in this group

    `backfilled: bool | None`
    :   Whether the campaign group is backfilled

    `id: int | None`
    :   Unique campaign group identifier

    `name: str | None`
    :   Campaign group name

    `run_schedule: dict[str, typing.Any] | None`
    :   Campaign group run schedule

    `serving_statuses: list[typing.Any] | None`
    :   List of serving statuses

    `status: str | None`
    :   Campaign group status

    `test: bool | None`
    :   Whether this is a test campaign group

    `total_budget: dict[str, typing.Any] | None`
    :   Total budget for the campaign group

<a id="CampaignGroupsSearchQuery"></a>

`CampaignGroupsSearchQuery(*args, **kwargs)`
:   Search query for campaign_groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsSortFilter]`
    :   The type of the None singleton.

<a id="CampaignGroupsSortFilter"></a>

`CampaignGroupsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaign_groups search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Literal['asc', 'desc']`
    :   Associated account URN

    `allowed_campaign_types: Literal['asc', 'desc']`
    :   Types of campaigns allowed in this group

    `backfilled: Literal['asc', 'desc']`
    :   Whether the campaign group is backfilled

    `id: Literal['asc', 'desc']`
    :   Unique campaign group identifier

    `name: Literal['asc', 'desc']`
    :   Campaign group name

    `run_schedule: Literal['asc', 'desc']`
    :   Campaign group run schedule

    `serving_statuses: Literal['asc', 'desc']`
    :   List of serving statuses

    `status: Literal['asc', 'desc']`
    :   Campaign group status

    `test: Literal['asc', 'desc']`
    :   Whether this is a test campaign group

    `total_budget: Literal['asc', 'desc']`
    :   Total budget for the campaign group

<a id="CampaignGroupsStringFilter"></a>

`CampaignGroupsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   Associated account URN

    `allowed_campaign_types: str`
    :   Types of campaigns allowed in this group

    `backfilled: str`
    :   Whether the campaign group is backfilled

    `id: str`
    :   Unique campaign group identifier

    `name: str`
    :   Campaign group name

    `run_schedule: str`
    :   Campaign group run schedule

    `serving_statuses: str`
    :   List of serving statuses

    `status: str`
    :   Campaign group status

    `test: str`
    :   Whether this is a test campaign group

    `total_budget: str`
    :   Total budget for the campaign group

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

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsAnyValueFilter"></a>

`CampaignsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Any`
    :   Associated account URN

    `associated_entity: Any`
    :   Associated entity URN

    `audience_expansion_enabled: Any`
    :   Whether audience expansion is enabled

    `campaign_group: Any`
    :   Parent campaign group URN

    `cost_type: Any`
    :   Cost type (CPC CPM etc)

    `creative_selection: Any`
    :   Creative selection mode

    `daily_budget: Any`
    :   Daily budget configuration

    `format: Any`
    :   Campaign ad format

    `id: Any`
    :   Unique campaign identifier

    `locale: Any`
    :   Campaign locale settings

    `name: Any`
    :   Campaign name

    `objective_type: Any`
    :   Campaign objective type

    `offsite_delivery_enabled: Any`
    :   Whether offsite delivery is enabled

    `optimization_target_type: Any`
    :   Optimization target type

    `pacing_strategy: Any`
    :   Budget pacing strategy

    `run_schedule: Any`
    :   Campaign run schedule

    `serving_statuses: Any`
    :   List of serving statuses

    `status: Any`
    :   Campaign status

    `story_delivery_enabled: Any`
    :   Whether story delivery is enabled

    `test: Any`
    :   Whether this is a test campaign

    `total_budget: Any`
    :   Total budget configuration

    `type_: Any`
    :   Campaign type

    `unit_cost: Any`
    :   Cost per unit (bid amount)

    `version: Any`
    :   Version information

<a id="CampaignsContainsCondition"></a>

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsEqCondition"></a>

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsFuzzyCondition"></a>

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsGetParams"></a>

`CampaignsGetParams(*args, **kwargs)`
:   Parameters for campaigns.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

<a id="CampaignsGtCondition"></a>

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsGteCondition"></a>

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsInFilter`
    :   The type of the None singleton.

<a id="CampaignsInFilter"></a>

`CampaignsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: list[str]`
    :   Associated account URN

    `associated_entity: list[str]`
    :   Associated entity URN

    `audience_expansion_enabled: list[bool]`
    :   Whether audience expansion is enabled

    `campaign_group: list[str]`
    :   Parent campaign group URN

    `cost_type: list[str]`
    :   Cost type (CPC CPM etc)

    `creative_selection: list[str]`
    :   Creative selection mode

    `daily_budget: list[dict[str, typing.Any]]`
    :   Daily budget configuration

    `format: list[str]`
    :   Campaign ad format

    `id: list[int]`
    :   Unique campaign identifier

    `locale: list[dict[str, typing.Any]]`
    :   Campaign locale settings

    `name: list[str]`
    :   Campaign name

    `objective_type: list[str]`
    :   Campaign objective type

    `offsite_delivery_enabled: list[bool]`
    :   Whether offsite delivery is enabled

    `optimization_target_type: list[str]`
    :   Optimization target type

    `pacing_strategy: list[str]`
    :   Budget pacing strategy

    `run_schedule: list[dict[str, typing.Any]]`
    :   Campaign run schedule

    `serving_statuses: list[list[typing.Any]]`
    :   List of serving statuses

    `status: list[str]`
    :   Campaign status

    `story_delivery_enabled: list[bool]`
    :   Whether story delivery is enabled

    `test: list[bool]`
    :   Whether this is a test campaign

    `total_budget: list[dict[str, typing.Any]]`
    :   Total budget configuration

    `type_: list[str]`
    :   Campaign type

    `unit_cost: list[dict[str, typing.Any]]`
    :   Cost per unit (bid amount)

    `version: list[dict[str, typing.Any]]`
    :   Version information

<a id="CampaignsKeywordCondition"></a>

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsLikeCondition"></a>

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsListParams"></a>

`CampaignsListParams(*args, **kwargs)`
:   Parameters for campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

<a id="CampaignsLtCondition"></a>

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsLteCondition"></a>

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsNeqCondition"></a>

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignsSearchFilter"></a>

`CampaignsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaigns search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str | None`
    :   Associated account URN

    `associated_entity: str | None`
    :   Associated entity URN

    `audience_expansion_enabled: bool | None`
    :   Whether audience expansion is enabled

    `campaign_group: str | None`
    :   Parent campaign group URN

    `cost_type: str | None`
    :   Cost type (CPC CPM etc)

    `creative_selection: str | None`
    :   Creative selection mode

    `daily_budget: dict[str, typing.Any] | None`
    :   Daily budget configuration

    `format: str | None`
    :   Campaign ad format

    `id: int | None`
    :   Unique campaign identifier

    `locale: dict[str, typing.Any] | None`
    :   Campaign locale settings

    `name: str | None`
    :   Campaign name

    `objective_type: str | None`
    :   Campaign objective type

    `offsite_delivery_enabled: bool | None`
    :   Whether offsite delivery is enabled

    `optimization_target_type: str | None`
    :   Optimization target type

    `pacing_strategy: str | None`
    :   Budget pacing strategy

    `run_schedule: dict[str, typing.Any] | None`
    :   Campaign run schedule

    `serving_statuses: list[typing.Any] | None`
    :   List of serving statuses

    `status: str | None`
    :   Campaign status

    `story_delivery_enabled: bool | None`
    :   Whether story delivery is enabled

    `test: bool | None`
    :   Whether this is a test campaign

    `total_budget: dict[str, typing.Any] | None`
    :   Total budget configuration

    `type_: str | None`
    :   Campaign type

    `unit_cost: dict[str, typing.Any] | None`
    :   Cost per unit (bid amount)

    `version: dict[str, typing.Any] | None`
    :   Version information

<a id="CampaignsSearchQuery"></a>

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsSortFilter]`
    :   The type of the None singleton.

<a id="CampaignsSortFilter"></a>

`CampaignsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaigns search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Literal['asc', 'desc']`
    :   Associated account URN

    `associated_entity: Literal['asc', 'desc']`
    :   Associated entity URN

    `audience_expansion_enabled: Literal['asc', 'desc']`
    :   Whether audience expansion is enabled

    `campaign_group: Literal['asc', 'desc']`
    :   Parent campaign group URN

    `cost_type: Literal['asc', 'desc']`
    :   Cost type (CPC CPM etc)

    `creative_selection: Literal['asc', 'desc']`
    :   Creative selection mode

    `daily_budget: Literal['asc', 'desc']`
    :   Daily budget configuration

    `format: Literal['asc', 'desc']`
    :   Campaign ad format

    `id: Literal['asc', 'desc']`
    :   Unique campaign identifier

    `locale: Literal['asc', 'desc']`
    :   Campaign locale settings

    `name: Literal['asc', 'desc']`
    :   Campaign name

    `objective_type: Literal['asc', 'desc']`
    :   Campaign objective type

    `offsite_delivery_enabled: Literal['asc', 'desc']`
    :   Whether offsite delivery is enabled

    `optimization_target_type: Literal['asc', 'desc']`
    :   Optimization target type

    `pacing_strategy: Literal['asc', 'desc']`
    :   Budget pacing strategy

    `run_schedule: Literal['asc', 'desc']`
    :   Campaign run schedule

    `serving_statuses: Literal['asc', 'desc']`
    :   List of serving statuses

    `status: Literal['asc', 'desc']`
    :   Campaign status

    `story_delivery_enabled: Literal['asc', 'desc']`
    :   Whether story delivery is enabled

    `test: Literal['asc', 'desc']`
    :   Whether this is a test campaign

    `total_budget: Literal['asc', 'desc']`
    :   Total budget configuration

    `type_: Literal['asc', 'desc']`
    :   Campaign type

    `unit_cost: Literal['asc', 'desc']`
    :   Cost per unit (bid amount)

    `version: Literal['asc', 'desc']`
    :   Version information

<a id="CampaignsStringFilter"></a>

`CampaignsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   Associated account URN

    `associated_entity: str`
    :   Associated entity URN

    `audience_expansion_enabled: str`
    :   Whether audience expansion is enabled

    `campaign_group: str`
    :   Parent campaign group URN

    `cost_type: str`
    :   Cost type (CPC CPM etc)

    `creative_selection: str`
    :   Creative selection mode

    `daily_budget: str`
    :   Daily budget configuration

    `format: str`
    :   Campaign ad format

    `id: str`
    :   Unique campaign identifier

    `locale: str`
    :   Campaign locale settings

    `name: str`
    :   Campaign name

    `objective_type: str`
    :   Campaign objective type

    `offsite_delivery_enabled: str`
    :   Whether offsite delivery is enabled

    `optimization_target_type: str`
    :   Optimization target type

    `pacing_strategy: str`
    :   Budget pacing strategy

    `run_schedule: str`
    :   Campaign run schedule

    `serving_statuses: str`
    :   List of serving statuses

    `status: str`
    :   Campaign status

    `story_delivery_enabled: str`
    :   Whether story delivery is enabled

    `test: str`
    :   Whether this is a test campaign

    `total_budget: str`
    :   Total budget configuration

    `type_: str`
    :   Campaign type

    `unit_cost: str`
    :   Cost per unit (bid amount)

    `version: str`
    :   Version information

<a id="ConversionsAndCondition"></a>

`ConversionsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAnyCondition]`
    :   The type of the None singleton.

<a id="ConversionsAnyCondition"></a>

`ConversionsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAnyValueFilter`
    :   The type of the None singleton.

<a id="ConversionsAnyValueFilter"></a>

`ConversionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Any`
    :   Associated account URN

    `associated_campaigns: Any`
    :   Associated campaigns

    `attribution_type: Any`
    :   Attribution type for the conversion

    `campaigns: Any`
    :   Related campaign URNs

    `created: Any`
    :   Creation timestamp (epoch milliseconds)

    `enabled: Any`
    :   Whether the conversion tracking is enabled

    `id: Any`
    :   Unique conversion identifier

    `image_pixel_tag: Any`
    :   Image pixel tracking tag

    `last_modified: Any`
    :   Last modification timestamp (epoch milliseconds)

    `name: Any`
    :   Conversion name

    `post_click_attribution_window_size: Any`
    :   Post-click attribution window size in days

    `type_: Any`
    :   Conversion type

    `value: Any`
    :   Conversion value

    `view_through_attribution_window_size: Any`
    :   View-through attribution window size in days

<a id="ConversionsContainsCondition"></a>

`ConversionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAnyValueFilter`
    :   The type of the None singleton.

<a id="ConversionsEqCondition"></a>

`ConversionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsSearchFilter`
    :   The type of the None singleton.

<a id="ConversionsFuzzyCondition"></a>

`ConversionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsStringFilter`
    :   The type of the None singleton.

<a id="ConversionsGetParams"></a>

`ConversionsGetParams(*args, **kwargs)`
:   Parameters for conversions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ConversionsGtCondition"></a>

`ConversionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsSearchFilter`
    :   The type of the None singleton.

<a id="ConversionsGteCondition"></a>

`ConversionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsSearchFilter`
    :   The type of the None singleton.

<a id="ConversionsInCondition"></a>

`ConversionsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsInFilter`
    :   The type of the None singleton.

<a id="ConversionsInFilter"></a>

`ConversionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: list[str]`
    :   Associated account URN

    `associated_campaigns: list[list[typing.Any]]`
    :   Associated campaigns

    `attribution_type: list[str]`
    :   Attribution type for the conversion

    `campaigns: list[list[typing.Any]]`
    :   Related campaign URNs

    `created: list[int]`
    :   Creation timestamp (epoch milliseconds)

    `enabled: list[bool]`
    :   Whether the conversion tracking is enabled

    `id: list[int]`
    :   Unique conversion identifier

    `image_pixel_tag: list[str]`
    :   Image pixel tracking tag

    `last_modified: list[int]`
    :   Last modification timestamp (epoch milliseconds)

    `name: list[str]`
    :   Conversion name

    `post_click_attribution_window_size: list[int]`
    :   Post-click attribution window size in days

    `type_: list[str]`
    :   Conversion type

    `value: list[dict[str, typing.Any]]`
    :   Conversion value

    `view_through_attribution_window_size: list[int]`
    :   View-through attribution window size in days

<a id="ConversionsKeywordCondition"></a>

`ConversionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsStringFilter`
    :   The type of the None singleton.

<a id="ConversionsLikeCondition"></a>

`ConversionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsStringFilter`
    :   The type of the None singleton.

<a id="ConversionsListParams"></a>

`ConversionsListParams(*args, **kwargs)`
:   Parameters for conversions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   The type of the None singleton.

    `count: int`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

    `start: int`
    :   The type of the None singleton.

<a id="ConversionsLtCondition"></a>

`ConversionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsSearchFilter`
    :   The type of the None singleton.

<a id="ConversionsLteCondition"></a>

`ConversionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsSearchFilter`
    :   The type of the None singleton.

<a id="ConversionsNeqCondition"></a>

`ConversionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsSearchFilter`
    :   The type of the None singleton.

<a id="ConversionsNotCondition"></a>

`ConversionsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAnyCondition`
    :   The type of the None singleton.

<a id="ConversionsOrCondition"></a>

`ConversionsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAnyCondition]`
    :   The type of the None singleton.

<a id="ConversionsSearchFilter"></a>

`ConversionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering conversions search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str | None`
    :   Associated account URN

    `associated_campaigns: list[typing.Any] | None`
    :   Associated campaigns

    `attribution_type: str | None`
    :   Attribution type for the conversion

    `campaigns: list[typing.Any] | None`
    :   Related campaign URNs

    `created: int | None`
    :   Creation timestamp (epoch milliseconds)

    `enabled: bool | None`
    :   Whether the conversion tracking is enabled

    `id: int | None`
    :   Unique conversion identifier

    `image_pixel_tag: str | None`
    :   Image pixel tracking tag

    `last_modified: int | None`
    :   Last modification timestamp (epoch milliseconds)

    `name: str | None`
    :   Conversion name

    `post_click_attribution_window_size: int | None`
    :   Post-click attribution window size in days

    `type_: str | None`
    :   Conversion type

    `value: dict[str, typing.Any] | None`
    :   Conversion value

    `view_through_attribution_window_size: int | None`
    :   View-through attribution window size in days

<a id="ConversionsSearchQuery"></a>

`ConversionsSearchQuery(*args, **kwargs)`
:   Search query for conversions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsSortFilter]`
    :   The type of the None singleton.

<a id="ConversionsSortFilter"></a>

`ConversionsSortFilter(*args, **kwargs)`
:   Available fields for sorting conversions search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Literal['asc', 'desc']`
    :   Associated account URN

    `associated_campaigns: Literal['asc', 'desc']`
    :   Associated campaigns

    `attribution_type: Literal['asc', 'desc']`
    :   Attribution type for the conversion

    `campaigns: Literal['asc', 'desc']`
    :   Related campaign URNs

    `created: Literal['asc', 'desc']`
    :   Creation timestamp (epoch milliseconds)

    `enabled: Literal['asc', 'desc']`
    :   Whether the conversion tracking is enabled

    `id: Literal['asc', 'desc']`
    :   Unique conversion identifier

    `image_pixel_tag: Literal['asc', 'desc']`
    :   Image pixel tracking tag

    `last_modified: Literal['asc', 'desc']`
    :   Last modification timestamp (epoch milliseconds)

    `name: Literal['asc', 'desc']`
    :   Conversion name

    `post_click_attribution_window_size: Literal['asc', 'desc']`
    :   Post-click attribution window size in days

    `type_: Literal['asc', 'desc']`
    :   Conversion type

    `value: Literal['asc', 'desc']`
    :   Conversion value

    `view_through_attribution_window_size: Literal['asc', 'desc']`
    :   View-through attribution window size in days

<a id="ConversionsStringFilter"></a>

`ConversionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   Associated account URN

    `associated_campaigns: str`
    :   Associated campaigns

    `attribution_type: str`
    :   Attribution type for the conversion

    `campaigns: str`
    :   Related campaign URNs

    `created: str`
    :   Creation timestamp (epoch milliseconds)

    `enabled: str`
    :   Whether the conversion tracking is enabled

    `id: str`
    :   Unique conversion identifier

    `image_pixel_tag: str`
    :   Image pixel tracking tag

    `last_modified: str`
    :   Last modification timestamp (epoch milliseconds)

    `name: str`
    :   Conversion name

    `post_click_attribution_window_size: str`
    :   Post-click attribution window size in days

    `type_: str`
    :   Conversion type

    `value: str`
    :   Conversion value

    `view_through_attribution_window_size: str`
    :   View-through attribution window size in days

<a id="CreativesAndCondition"></a>

`CreativesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAnyCondition]`
    :   The type of the None singleton.

<a id="CreativesAnyCondition"></a>

`CreativesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAnyValueFilter`
    :   The type of the None singleton.

<a id="CreativesAnyValueFilter"></a>

`CreativesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Any`
    :   Associated account URN

    `campaign: Any`
    :   Parent campaign URN

    `content: Any`
    :   Creative content configuration

    `created_at: Any`
    :   Creation timestamp (epoch milliseconds)

    `created_by: Any`
    :   URN of the user who created the creative

    `id: Any`
    :   Unique creative identifier

    `intended_status: Any`
    :   Intended creative status

    `is_serving: Any`
    :   Whether the creative is currently serving

    `is_test: Any`
    :   Whether this is a test creative

    `last_modified_at: Any`
    :   Last modification timestamp (epoch milliseconds)

    `last_modified_by: Any`
    :   URN of the user who last modified the creative

    `name: Any`
    :   Creative name

    `serving_hold_reasons: Any`
    :   Reasons for holding creative from serving

<a id="CreativesContainsCondition"></a>

`CreativesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAnyValueFilter`
    :   The type of the None singleton.

<a id="CreativesEqCondition"></a>

`CreativesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesSearchFilter`
    :   The type of the None singleton.

<a id="CreativesFuzzyCondition"></a>

`CreativesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesStringFilter`
    :   The type of the None singleton.

<a id="CreativesGetParams"></a>

`CreativesGetParams(*args, **kwargs)`
:   Parameters for creatives.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

<a id="CreativesGtCondition"></a>

`CreativesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesSearchFilter`
    :   The type of the None singleton.

<a id="CreativesGteCondition"></a>

`CreativesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesSearchFilter`
    :   The type of the None singleton.

<a id="CreativesInCondition"></a>

`CreativesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesInFilter`
    :   The type of the None singleton.

<a id="CreativesInFilter"></a>

`CreativesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: list[str]`
    :   Associated account URN

    `campaign: list[str]`
    :   Parent campaign URN

    `content: list[dict[str, typing.Any]]`
    :   Creative content configuration

    `created_at: list[int]`
    :   Creation timestamp (epoch milliseconds)

    `created_by: list[str]`
    :   URN of the user who created the creative

    `id: list[str]`
    :   Unique creative identifier

    `intended_status: list[str]`
    :   Intended creative status

    `is_serving: list[bool]`
    :   Whether the creative is currently serving

    `is_test: list[bool]`
    :   Whether this is a test creative

    `last_modified_at: list[int]`
    :   Last modification timestamp (epoch milliseconds)

    `last_modified_by: list[str]`
    :   URN of the user who last modified the creative

    `name: list[str]`
    :   Creative name

    `serving_hold_reasons: list[list[typing.Any]]`
    :   Reasons for holding creative from serving

<a id="CreativesKeywordCondition"></a>

`CreativesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesStringFilter`
    :   The type of the None singleton.

<a id="CreativesLikeCondition"></a>

`CreativesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesStringFilter`
    :   The type of the None singleton.

<a id="CreativesListParams"></a>

`CreativesListParams(*args, **kwargs)`
:   Parameters for creatives.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

<a id="CreativesLtCondition"></a>

`CreativesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesSearchFilter`
    :   The type of the None singleton.

<a id="CreativesLteCondition"></a>

`CreativesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesSearchFilter`
    :   The type of the None singleton.

<a id="CreativesNeqCondition"></a>

`CreativesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesSearchFilter`
    :   The type of the None singleton.

<a id="CreativesNotCondition"></a>

`CreativesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAnyCondition`
    :   The type of the None singleton.

<a id="CreativesOrCondition"></a>

`CreativesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAnyCondition]`
    :   The type of the None singleton.

<a id="CreativesSearchFilter"></a>

`CreativesSearchFilter(*args, **kwargs)`
:   Available fields for filtering creatives search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str | None`
    :   Associated account URN

    `campaign: str | None`
    :   Parent campaign URN

    `content: dict[str, typing.Any] | None`
    :   Creative content configuration

    `created_at: int | None`
    :   Creation timestamp (epoch milliseconds)

    `created_by: str | None`
    :   URN of the user who created the creative

    `id: str | None`
    :   Unique creative identifier

    `intended_status: str | None`
    :   Intended creative status

    `is_serving: bool | None`
    :   Whether the creative is currently serving

    `is_test: bool | None`
    :   Whether this is a test creative

    `last_modified_at: int | None`
    :   Last modification timestamp (epoch milliseconds)

    `last_modified_by: str | None`
    :   URN of the user who last modified the creative

    `name: str | None`
    :   Creative name

    `serving_hold_reasons: list[typing.Any] | None`
    :   Reasons for holding creative from serving

<a id="CreativesSearchQuery"></a>

`CreativesSearchQuery(*args, **kwargs)`
:   Search query for creatives entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLikeCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesSortFilter]`
    :   The type of the None singleton.

<a id="CreativesSortFilter"></a>

`CreativesSortFilter(*args, **kwargs)`
:   Available fields for sorting creatives search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: Literal['asc', 'desc']`
    :   Associated account URN

    `campaign: Literal['asc', 'desc']`
    :   Parent campaign URN

    `content: Literal['asc', 'desc']`
    :   Creative content configuration

    `created_at: Literal['asc', 'desc']`
    :   Creation timestamp (epoch milliseconds)

    `created_by: Literal['asc', 'desc']`
    :   URN of the user who created the creative

    `id: Literal['asc', 'desc']`
    :   Unique creative identifier

    `intended_status: Literal['asc', 'desc']`
    :   Intended creative status

    `is_serving: Literal['asc', 'desc']`
    :   Whether the creative is currently serving

    `is_test: Literal['asc', 'desc']`
    :   Whether this is a test creative

    `last_modified_at: Literal['asc', 'desc']`
    :   Last modification timestamp (epoch milliseconds)

    `last_modified_by: Literal['asc', 'desc']`
    :   URN of the user who last modified the creative

    `name: Literal['asc', 'desc']`
    :   Creative name

    `serving_hold_reasons: Literal['asc', 'desc']`
    :   Reasons for holding creative from serving

<a id="CreativesStringFilter"></a>

`CreativesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   Associated account URN

    `campaign: str`
    :   Parent campaign URN

    `content: str`
    :   Creative content configuration

    `created_at: str`
    :   Creation timestamp (epoch milliseconds)

    `created_by: str`
    :   URN of the user who created the creative

    `id: str`
    :   Unique creative identifier

    `intended_status: str`
    :   Intended creative status

    `is_serving: str`
    :   Whether the creative is currently serving

    `is_test: str`
    :   Whether this is a test creative

    `last_modified_at: str`
    :   Last modification timestamp (epoch milliseconds)

    `last_modified_by: str`
    :   URN of the user who last modified the creative

    `name: str`
    :   Creative name

    `serving_hold_reasons: str`
    :   Reasons for holding creative from serving