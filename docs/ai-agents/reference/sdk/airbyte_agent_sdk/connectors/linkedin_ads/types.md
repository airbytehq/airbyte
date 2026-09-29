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

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAnyCondition]`
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
    :   The account associated with the user

    `created: Any`
    :   The date and time when the user account was created

    `last_modified: Any`
    :   The date and time when the user account was last modified

    `role: Any`
    :   The role assigned to the user in the account

    `user: Any`
    :   The user details including name, email, etc.

<a id="AccountUsersArrayContainsCondition"></a>

`AccountUsersArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountUsersContainsCondition"></a>

`AccountUsersContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountUsersCreateParams"></a>

`AccountUsersCreateParams(*args, **kwargs)`
:   Parameters for account_users.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `user: str`
    :   The type of the None singleton.

<a id="AccountUsersDeleteParams"></a>

`AccountUsersDeleteParams(*args, **kwargs)`
:   Parameters for account_users.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   The type of the None singleton.

    `user: str`
    :   The type of the None singleton.

<a id="AccountUsersEndswithCondition"></a>

`AccountUsersEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersStringFilter`
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
    :   The account associated with the user

    `created: list[str]`
    :   The date and time when the user account was created

    `last_modified: list[str]`
    :   The date and time when the user account was last modified

    `role: list[str]`
    :   The role assigned to the user in the account

    `user: list[str]`
    :   The user details including name, email, etc.

<a id="AccountUsersKeywordCondition"></a>

`AccountUsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersStringFilter`
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

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAnyCondition]`
    :   The type of the None singleton.

<a id="AccountUsersSearchFilter"></a>

`AccountUsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering account_users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str | None`
    :   The account associated with the user

    `created: str | None`
    :   The date and time when the user account was created

    `last_modified: str | None`
    :   The date and time when the user account was last modified

    `role: str | None`
    :   The role assigned to the user in the account

    `user: str | None`
    :   The user details including name, email, etc.

<a id="AccountUsersSearchQuery"></a>

`AccountUsersSearchQuery(*args, **kwargs)`
:   Search query for account_users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersAnyCondition`
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
    :   The account associated with the user

    `created: Literal['asc', 'desc']`
    :   The date and time when the user account was created

    `last_modified: Literal['asc', 'desc']`
    :   The date and time when the user account was last modified

    `role: Literal['asc', 'desc']`
    :   The role assigned to the user in the account

    `user: Literal['asc', 'desc']`
    :   The user details including name, email, etc.

<a id="AccountUsersStartswithCondition"></a>

`AccountUsersStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersStringFilter`
    :   The type of the None singleton.

<a id="AccountUsersStringFilter"></a>

`AccountUsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   The account associated with the user

    `created: str`
    :   The date and time when the user account was created

    `last_modified: str`
    :   The date and time when the user account was last modified

    `role: str`
    :   The role assigned to the user in the account

    `user: str`
    :   The user details including name, email, etc.

<a id="AccountUsersUpdateParams"></a>

`AccountUsersUpdateParams(*args, **kwargs)`
:   Parameters for account_users.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   The type of the None singleton.

    `patch: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountUsersUpdateParamsPatch`
    :   The type of the None singleton.

    `user: str`
    :   The type of the None singleton.

<a id="AccountUsersUpdateParamsPatch"></a>

`AccountUsersUpdateParamsPatch(*args, **kwargs)`
:   Nested schema for AccountUsersUpdateParams.patch

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `set_: dict[str, typing.Any]`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAnyCondition]`
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

    `created: Any`
    :   The timestamp indicating when the account was created.

    `currency: Any`
    :   The currency used for financial transactions in the account.

    `id: Any`
    :   The unique identifier for the account.

    `last_modified: Any`
    :   The timestamp of the last modification made to the account.

    `name: Any`
    :   The name of the account.

    `notified_on_campaign_optimization: Any`
    :   Flag for notifications on campaign optimization.

    `notified_on_creative_approval: Any`
    :   Flag for notifications on creative approval.

    `notified_on_creative_rejection: Any`
    :   Flag for notifications on creative rejection.

    `notified_on_end_of_campaign: Any`
    :   Flag for notifications on the end of campaign.

    `notified_on_new_features_enabled: Any`
    :   Flag for notifications on new features being enabled.

    `reference: Any`
    :   A reference identifier for the account.

    `serving_statuses: Any`
    :   The serving statuses associated with the account.

    `status: Any`
    :   The status of the account.

    `test: Any`
    :   Flag indicating if the account is in a test mode.

    `type_: Any`
    :   The type or category of the account.

    `version: Any`
    :   The version information related to the account.

<a id="AccountsArrayContainsCondition"></a>

`AccountsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountsContainsCondition"></a>

`AccountsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountsCreateParams"></a>

`AccountsCreateParams(*args, **kwargs)`
:   Parameters for accounts.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `currency: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `reference: str`
    :   The type of the None singleton.

    `test: bool`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="AccountsDeleteParams"></a>

`AccountsDeleteParams(*args, **kwargs)`
:   Parameters for accounts.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="AccountsEndswithCondition"></a>

`AccountsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsStringFilter`
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

    `created: list[str]`
    :   The timestamp indicating when the account was created.

    `currency: list[str]`
    :   The currency used for financial transactions in the account.

    `id: list[int]`
    :   The unique identifier for the account.

    `last_modified: list[str]`
    :   The timestamp of the last modification made to the account.

    `name: list[str]`
    :   The name of the account.

    `notified_on_campaign_optimization: list[bool]`
    :   Flag for notifications on campaign optimization.

    `notified_on_creative_approval: list[bool]`
    :   Flag for notifications on creative approval.

    `notified_on_creative_rejection: list[bool]`
    :   Flag for notifications on creative rejection.

    `notified_on_end_of_campaign: list[bool]`
    :   Flag for notifications on the end of campaign.

    `notified_on_new_features_enabled: list[bool]`
    :   Flag for notifications on new features being enabled.

    `reference: list[str]`
    :   A reference identifier for the account.

    `serving_statuses: list[list[typing.Any]]`
    :   The serving statuses associated with the account.

    `status: list[str]`
    :   The status of the account.

    `test: list[bool]`
    :   Flag indicating if the account is in a test mode.

    `type_: list[str]`
    :   The type or category of the account.

    `version: list[dict[str, typing.Any]]`
    :   The version information related to the account.

<a id="AccountsKeywordCondition"></a>

`AccountsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsStringFilter`
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

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAnyCondition]`
    :   The type of the None singleton.

<a id="AccountsSearchFilter"></a>

`AccountsSearchFilter(*args, **kwargs)`
:   Available fields for filtering accounts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: str | None`
    :   The timestamp indicating when the account was created.

    `currency: str | None`
    :   The currency used for financial transactions in the account.

    `id: int | None`
    :   The unique identifier for the account.

    `last_modified: str | None`
    :   The timestamp of the last modification made to the account.

    `name: str | None`
    :   The name of the account.

    `notified_on_campaign_optimization: bool | None`
    :   Flag for notifications on campaign optimization.

    `notified_on_creative_approval: bool | None`
    :   Flag for notifications on creative approval.

    `notified_on_creative_rejection: bool | None`
    :   Flag for notifications on creative rejection.

    `notified_on_end_of_campaign: bool | None`
    :   Flag for notifications on the end of campaign.

    `notified_on_new_features_enabled: bool | None`
    :   Flag for notifications on new features being enabled.

    `reference: str | None`
    :   A reference identifier for the account.

    `serving_statuses: list[typing.Any] | None`
    :   The serving statuses associated with the account.

    `status: str | None`
    :   The status of the account.

    `test: bool | None`
    :   Flag indicating if the account is in a test mode.

    `type_: str | None`
    :   The type or category of the account.

    `version: dict[str, typing.Any] | None`
    :   The version information related to the account.

<a id="AccountsSearchQuery"></a>

`AccountsSearchQuery(*args, **kwargs)`
:   Search query for accounts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsSortFilter]`
    :   The type of the None singleton.

<a id="AccountsSortFilter"></a>

`AccountsSortFilter(*args, **kwargs)`
:   Available fields for sorting accounts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: Literal['asc', 'desc']`
    :   The timestamp indicating when the account was created.

    `currency: Literal['asc', 'desc']`
    :   The currency used for financial transactions in the account.

    `id: Literal['asc', 'desc']`
    :   The unique identifier for the account.

    `last_modified: Literal['asc', 'desc']`
    :   The timestamp of the last modification made to the account.

    `name: Literal['asc', 'desc']`
    :   The name of the account.

    `notified_on_campaign_optimization: Literal['asc', 'desc']`
    :   Flag for notifications on campaign optimization.

    `notified_on_creative_approval: Literal['asc', 'desc']`
    :   Flag for notifications on creative approval.

    `notified_on_creative_rejection: Literal['asc', 'desc']`
    :   Flag for notifications on creative rejection.

    `notified_on_end_of_campaign: Literal['asc', 'desc']`
    :   Flag for notifications on the end of campaign.

    `notified_on_new_features_enabled: Literal['asc', 'desc']`
    :   Flag for notifications on new features being enabled.

    `reference: Literal['asc', 'desc']`
    :   A reference identifier for the account.

    `serving_statuses: Literal['asc', 'desc']`
    :   The serving statuses associated with the account.

    `status: Literal['asc', 'desc']`
    :   The status of the account.

    `test: Literal['asc', 'desc']`
    :   Flag indicating if the account is in a test mode.

    `type_: Literal['asc', 'desc']`
    :   The type or category of the account.

    `version: Literal['asc', 'desc']`
    :   The version information related to the account.

<a id="AccountsStartswithCondition"></a>

`AccountsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsStringFilter"></a>

`AccountsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: str`
    :   The timestamp indicating when the account was created.

    `currency: str`
    :   The currency used for financial transactions in the account.

    `id: str`
    :   The unique identifier for the account.

    `last_modified: str`
    :   The timestamp of the last modification made to the account.

    `name: str`
    :   The name of the account.

    `notified_on_campaign_optimization: str`
    :   Flag for notifications on campaign optimization.

    `notified_on_creative_approval: str`
    :   Flag for notifications on creative approval.

    `notified_on_creative_rejection: str`
    :   Flag for notifications on creative rejection.

    `notified_on_end_of_campaign: str`
    :   Flag for notifications on the end of campaign.

    `notified_on_new_features_enabled: str`
    :   Flag for notifications on new features being enabled.

    `reference: str`
    :   A reference identifier for the account.

    `serving_statuses: str`
    :   The serving statuses associated with the account.

    `status: str`
    :   The status of the account.

    `test: str`
    :   Flag indicating if the account is in a test mode.

    `type_: str`
    :   The type or category of the account.

    `version: str`
    :   The version information related to the account.

<a id="AccountsUpdateParams"></a>

`AccountsUpdateParams(*args, **kwargs)`
:   Parameters for accounts.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `patch: airbyte_agent_sdk.connectors.linkedin_ads.types.AccountsUpdateParamsPatch`
    :   The type of the None singleton.

<a id="AccountsUpdateParamsPatch"></a>

`AccountsUpdateParamsPatch(*args, **kwargs)`
:   Nested schema for AccountsUpdateParams.patch

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `set_: dict[str, typing.Any]`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAnyCondition]`
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
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Any`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Any`
    :   An approximation of unique ad impressions.

    `card_clicks: Any`
    :   The number of clicks on interactive card elements.

    `card_impressions: Any`
    :   The number of times interactive cards were displayed.

    `clicks: Any`
    :   Total number of clicks on the ad.

    `comment_likes: Any`
    :   The count of likes on comments related to the ad.

    `comments: Any`
    :   The number of comments on the ad.

    `company_page_clicks: Any`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Any`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Any`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Any`
    :   Cost of ad campaign in USD.

    `document_completions: Any`
    :   Number of completions for document views.

    `document_first_quartile_completions: Any`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Any`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Any`
    :   Completions for third quartile of document views.

    `download_clicks: Any`
    :   Clicks on download links in the ad.

    `end_date: Any`
    :   End date of the ad analytics data.

    `external_website_conversions: Any`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites.

    `follows: Any`
    :   Number of follows generated by the ad.

    `full_screen_plays: Any`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Any`
    :   Total number of times the ad was displayed.

    `job_applications: Any`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Any`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Any`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Any`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Any`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Any`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Any`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Any`
    :   Leads generated in one click.

    `opens: Any`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Any`
    :   Engagements other than clicks on the ad.

    `pivot: Any`
    :   Pivot dimension used for this analytics record

    `pivot_values: Any`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Any`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Any`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Any`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Any`
    :   Registrations completed post-viewing the ad.

    `reactions: Any`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Any`
    :   Total registrations completed through the ad.

    `sends: Any`
    :   Number of messages sent through the ad.

    `shares: Any`
    :   Total shares generated by the ad.

    `sponsored_campaign: Any`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Any`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Any`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Any`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Any`
    :   Clicks on text URLs within the ad.

    `total_engagements: Any`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Any`
    :   Leads generated through valid work emails.

    `video_completions: Any`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Any`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Any`
    :   Completions for midpoint of video views.

    `video_starts: Any`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Any`
    :   Completions for third quartile of video views.

    `video_views: Any`
    :   Total views of videos in the ad.

    `viral_card_clicks: Any`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Any`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Any`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Any`
    :   Likes received on comments in viral distribution.

    `viral_comments: Any`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Any`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Any`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Any`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Any`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Any`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Any`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Any`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Any`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Any`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Any`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Any`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Any`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Any`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Any`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Any`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Any`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Any`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Any`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Any`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Any`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Any`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Any`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Any`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Any`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Any`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Any`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Any`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Any`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Any`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Any`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Any`
    :   Total views of videos in viral distribution of the ad.

<a id="AdCampaignAnalyticsArrayContainsCondition"></a>

`AdCampaignAnalyticsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsContainsCondition"></a>

`AdCampaignAnalyticsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsEndswithCondition"></a>

`AdCampaignAnalyticsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsStringFilter`
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
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: list[float]`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: list[float]`
    :   An approximation of unique ad impressions.

    `card_clicks: list[float]`
    :   The number of clicks on interactive card elements.

    `card_impressions: list[float]`
    :   The number of times interactive cards were displayed.

    `clicks: list[float]`
    :   Total number of clicks on the ad.

    `comment_likes: list[float]`
    :   The count of likes on comments related to the ad.

    `comments: list[float]`
    :   The number of comments on the ad.

    `company_page_clicks: list[float]`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: list[float]`
    :   Conversion value in the local currency.

    `cost_in_local_currency: list[float]`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: list[float]`
    :   Cost of ad campaign in USD.

    `document_completions: list[float]`
    :   Number of completions for document views.

    `document_first_quartile_completions: list[float]`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: list[float]`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: list[float]`
    :   Completions for third quartile of document views.

    `download_clicks: list[float]`
    :   Clicks on download links in the ad.

    `end_date: list[str]`
    :   End date of the ad analytics data.

    `external_website_conversions: list[float]`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites.

    `follows: list[float]`
    :   Number of follows generated by the ad.

    `full_screen_plays: list[float]`
    :   Number of times videos were played in fullscreen mode.

    `impressions: list[float]`
    :   Total number of times the ad was displayed.

    `job_applications: list[float]`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: list[float]`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: list[float]`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: list[float]`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: list[float]`
    :   Clicks on expressing interest through lead generation mail.

    `likes: list[float]`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: list[float]`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: list[float]`
    :   Leads generated in one click.

    `opens: list[float]`
    :   The number of times the ad was opened or expanded.

    `other_engagements: list[float]`
    :   Engagements other than clicks on the ad.

    `pivot: list[str]`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[list[typing.Any]]`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: list[float]`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: list[float]`
    :   Registrations completed post-viewing the ad.

    `reactions: list[float]`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: list[float]`
    :   Total registrations completed through the ad.

    `sends: list[float]`
    :   Number of messages sent through the ad.

    `shares: list[float]`
    :   Total shares generated by the ad.

    `sponsored_campaign: list[str]`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: list[str]`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: list[str]`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: list[float]`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: list[float]`
    :   Clicks on text URLs within the ad.

    `total_engagements: list[float]`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: list[float]`
    :   Leads generated through valid work emails.

    `video_completions: list[float]`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: list[float]`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: list[float]`
    :   Completions for midpoint of video views.

    `video_starts: list[float]`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: list[float]`
    :   Completions for third quartile of video views.

    `video_views: list[float]`
    :   Total views of videos in the ad.

    `viral_card_clicks: list[float]`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: list[float]`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: list[float]`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: list[float]`
    :   Likes received on comments in viral distribution.

    `viral_comments: list[float]`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: list[float]`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: list[float]`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: list[float]`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: list[float]`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: list[float]`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: list[float]`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: list[float]`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: list[float]`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: list[float]`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: list[float]`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: list[float]`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: list[float]`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: list[float]`
    :   Clicks on landing page in viral distribution.

    `viral_likes: list[float]`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: list[float]`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: list[float]`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: list[float]`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: list[float]`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: list[float]`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: list[float]`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: list[float]`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: list[float]`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: list[float]`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: list[float]`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: list[float]`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: list[float]`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: list[float]`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: list[float]`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: list[float]`
    :   Total views of videos in viral distribution of the ad.

<a id="AdCampaignAnalyticsKeywordCondition"></a>

`AdCampaignAnalyticsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsStringFilter`
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

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsSearchFilter"></a>

`AdCampaignAnalyticsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_campaign_analytics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: float | None`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: float | None`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: float | None`
    :   An approximation of unique ad impressions.

    `card_clicks: float | None`
    :   The number of clicks on interactive card elements.

    `card_impressions: float | None`
    :   The number of times interactive cards were displayed.

    `clicks: float | None`
    :   Total number of clicks on the ad.

    `comment_likes: float | None`
    :   The count of likes on comments related to the ad.

    `comments: float | None`
    :   The number of comments on the ad.

    `company_page_clicks: float | None`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: float | None`
    :   Conversion value in the local currency.

    `cost_in_local_currency: float | None`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: float | None`
    :   Cost of ad campaign in USD.

    `document_completions: float | None`
    :   Number of completions for document views.

    `document_first_quartile_completions: float | None`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: float | None`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: float | None`
    :   Completions for third quartile of document views.

    `download_clicks: float | None`
    :   Clicks on download links in the ad.

    `end_date: str | None`
    :   End date of the ad analytics data.

    `external_website_conversions: float | None`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites.

    `follows: float | None`
    :   Number of follows generated by the ad.

    `full_screen_plays: float | None`
    :   Number of times videos were played in fullscreen mode.

    `impressions: float | None`
    :   Total number of times the ad was displayed.

    `job_applications: float | None`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: float | None`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: float | None`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: float | None`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: float | None`
    :   Clicks on expressing interest through lead generation mail.

    `likes: float | None`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: float | None`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: float | None`
    :   Leads generated in one click.

    `opens: float | None`
    :   The number of times the ad was opened or expanded.

    `other_engagements: float | None`
    :   Engagements other than clicks on the ad.

    `pivot: str | None`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[typing.Any] | None`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: float | None`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: float | None`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: float | None`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: float | None`
    :   Registrations completed post-viewing the ad.

    `reactions: float | None`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: float | None`
    :   Total registrations completed through the ad.

    `sends: float | None`
    :   Number of messages sent through the ad.

    `shares: float | None`
    :   Total shares generated by the ad.

    `sponsored_campaign: str | None`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str | None`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str | None`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: float | None`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: float | None`
    :   Clicks on text URLs within the ad.

    `total_engagements: float | None`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: float | None`
    :   Leads generated through valid work emails.

    `video_completions: float | None`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: float | None`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: float | None`
    :   Completions for midpoint of video views.

    `video_starts: float | None`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: float | None`
    :   Completions for third quartile of video views.

    `video_views: float | None`
    :   Total views of videos in the ad.

    `viral_card_clicks: float | None`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: float | None`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: float | None`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: float | None`
    :   Likes received on comments in viral distribution.

    `viral_comments: float | None`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: float | None`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: float | None`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: float | None`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: float | None`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: float | None`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: float | None`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: float | None`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: float | None`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: float | None`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: float | None`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: float | None`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: float | None`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: float | None`
    :   Clicks on landing page in viral distribution.

    `viral_likes: float | None`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: float | None`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: float | None`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: float | None`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: float | None`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: float | None`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: float | None`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: float | None`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: float | None`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: float | None`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: float | None`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: float | None`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: float | None`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: float | None`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: float | None`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: float | None`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: float | None`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: float | None`
    :   Total views of videos in viral distribution of the ad.

<a id="AdCampaignAnalyticsSearchQuery"></a>

`AdCampaignAnalyticsSearchQuery(*args, **kwargs)`
:   Search query for ad_campaign_analytics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsAnyCondition`
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
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Literal['asc', 'desc']`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Literal['asc', 'desc']`
    :   An approximation of unique ad impressions.

    `card_clicks: Literal['asc', 'desc']`
    :   The number of clicks on interactive card elements.

    `card_impressions: Literal['asc', 'desc']`
    :   The number of times interactive cards were displayed.

    `clicks: Literal['asc', 'desc']`
    :   Total number of clicks on the ad.

    `comment_likes: Literal['asc', 'desc']`
    :   The count of likes on comments related to the ad.

    `comments: Literal['asc', 'desc']`
    :   The number of comments on the ad.

    `company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Literal['asc', 'desc']`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Literal['asc', 'desc']`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Literal['asc', 'desc']`
    :   Cost of ad campaign in USD.

    `document_completions: Literal['asc', 'desc']`
    :   Number of completions for document views.

    `document_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of document views.

    `download_clicks: Literal['asc', 'desc']`
    :   Clicks on download links in the ad.

    `end_date: Literal['asc', 'desc']`
    :   End date of the ad analytics data.

    `external_website_conversions: Literal['asc', 'desc']`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites.

    `follows: Literal['asc', 'desc']`
    :   Number of follows generated by the ad.

    `full_screen_plays: Literal['asc', 'desc']`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Literal['asc', 'desc']`
    :   Total number of times the ad was displayed.

    `job_applications: Literal['asc', 'desc']`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Literal['asc', 'desc']`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Literal['asc', 'desc']`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Literal['asc', 'desc']`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Literal['asc', 'desc']`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click.

    `opens: Literal['asc', 'desc']`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Literal['asc', 'desc']`
    :   Engagements other than clicks on the ad.

    `pivot: Literal['asc', 'desc']`
    :   Pivot dimension used for this analytics record

    `pivot_values: Literal['asc', 'desc']`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing the ad.

    `reactions: Literal['asc', 'desc']`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Literal['asc', 'desc']`
    :   Total registrations completed through the ad.

    `sends: Literal['asc', 'desc']`
    :   Number of messages sent through the ad.

    `shares: Literal['asc', 'desc']`
    :   Total shares generated by the ad.

    `sponsored_campaign: Literal['asc', 'desc']`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Literal['asc', 'desc']`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Literal['asc', 'desc']`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Literal['asc', 'desc']`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Literal['asc', 'desc']`
    :   Clicks on text URLs within the ad.

    `total_engagements: Literal['asc', 'desc']`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Literal['asc', 'desc']`
    :   Leads generated through valid work emails.

    `video_completions: Literal['asc', 'desc']`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of video views.

    `video_starts: Literal['asc', 'desc']`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of video views.

    `video_views: Literal['asc', 'desc']`
    :   Total views of videos in the ad.

    `viral_card_clicks: Literal['asc', 'desc']`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Literal['asc', 'desc']`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Literal['asc', 'desc']`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Literal['asc', 'desc']`
    :   Likes received on comments in viral distribution.

    `viral_comments: Literal['asc', 'desc']`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Literal['asc', 'desc']`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Literal['asc', 'desc']`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Literal['asc', 'desc']`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Literal['asc', 'desc']`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Literal['asc', 'desc']`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Literal['asc', 'desc']`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Literal['asc', 'desc']`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Literal['asc', 'desc']`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Literal['asc', 'desc']`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Literal['asc', 'desc']`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Literal['asc', 'desc']`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Literal['asc', 'desc']`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Literal['asc', 'desc']`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Literal['asc', 'desc']`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Literal['asc', 'desc']`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Literal['asc', 'desc']`
    :   Total views of videos in viral distribution of the ad.

<a id="AdCampaignAnalyticsStartswithCondition"></a>

`AdCampaignAnalyticsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCampaignAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsStringFilter"></a>

`AdCampaignAnalyticsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: str`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: str`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: str`
    :   An approximation of unique ad impressions.

    `card_clicks: str`
    :   The number of clicks on interactive card elements.

    `card_impressions: str`
    :   The number of times interactive cards were displayed.

    `clicks: str`
    :   Total number of clicks on the ad.

    `comment_likes: str`
    :   The count of likes on comments related to the ad.

    `comments: str`
    :   The number of comments on the ad.

    `company_page_clicks: str`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: str`
    :   Conversion value in the local currency.

    `cost_in_local_currency: str`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: str`
    :   Cost of ad campaign in USD.

    `document_completions: str`
    :   Number of completions for document views.

    `document_first_quartile_completions: str`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: str`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: str`
    :   Completions for third quartile of document views.

    `download_clicks: str`
    :   Clicks on download links in the ad.

    `end_date: str`
    :   End date of the ad analytics data.

    `external_website_conversions: str`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: str`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: str`
    :   Post-view conversions on external websites.

    `follows: str`
    :   Number of follows generated by the ad.

    `full_screen_plays: str`
    :   Number of times videos were played in fullscreen mode.

    `impressions: str`
    :   Total number of times the ad was displayed.

    `job_applications: str`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: str`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: str`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: str`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: str`
    :   Clicks on expressing interest through lead generation mail.

    `likes: str`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: str`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: str`
    :   Leads generated in one click.

    `opens: str`
    :   The number of times the ad was opened or expanded.

    `other_engagements: str`
    :   Engagements other than clicks on the ad.

    `pivot: str`
    :   Pivot dimension used for this analytics record

    `pivot_values: str`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: str`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: str`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: str`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: str`
    :   Registrations completed post-viewing the ad.

    `reactions: str`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: str`
    :   Total registrations completed through the ad.

    `sends: str`
    :   Number of messages sent through the ad.

    `shares: str`
    :   Total shares generated by the ad.

    `sponsored_campaign: str`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: str`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: str`
    :   Clicks on text URLs within the ad.

    `total_engagements: str`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: str`
    :   Leads generated through valid work emails.

    `video_completions: str`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: str`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: str`
    :   Completions for midpoint of video views.

    `video_starts: str`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: str`
    :   Completions for third quartile of video views.

    `video_views: str`
    :   Total views of videos in the ad.

    `viral_card_clicks: str`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: str`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: str`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: str`
    :   Likes received on comments in viral distribution.

    `viral_comments: str`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: str`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: str`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: str`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: str`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: str`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: str`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: str`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: str`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: str`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: str`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: str`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: str`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: str`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: str`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: str`
    :   Clicks on landing page in viral distribution.

    `viral_likes: str`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: str`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: str`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: str`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: str`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: str`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: str`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: str`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: str`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: str`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: str`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: str`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: str`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: str`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: str`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: str`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: str`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: str`
    :   Total views of videos in viral distribution of the ad.

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

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAnyCondition]`
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
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Any`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Any`
    :   An approximation of unique ad impressions.

    `card_clicks: Any`
    :   The number of clicks on interactive card elements.

    `card_impressions: Any`
    :   The number of times interactive cards were displayed.

    `clicks: Any`
    :   Total number of clicks on the ad.

    `comment_likes: Any`
    :   The count of likes on comments related to the ad.

    `comments: Any`
    :   The number of comments on the ad.

    `company_page_clicks: Any`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Any`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Any`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Any`
    :   Cost of ad campaign in USD.

    `document_completions: Any`
    :   Number of completions for document views.

    `document_first_quartile_completions: Any`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Any`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Any`
    :   Completions for third quartile of document views.

    `download_clicks: Any`
    :   Clicks on download links in the ad.

    `end_date: Any`
    :   End date of the ad analytics data.

    `external_website_conversions: Any`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites.

    `follows: Any`
    :   Number of follows generated by the ad.

    `full_screen_plays: Any`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Any`
    :   Total number of times the ad was displayed.

    `job_applications: Any`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Any`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Any`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Any`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Any`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Any`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Any`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Any`
    :   Leads generated in one click.

    `opens: Any`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Any`
    :   Engagements other than clicks on the ad.

    `pivot: Any`
    :   Pivot dimension used for this analytics record

    `pivot_values: Any`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Any`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Any`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Any`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Any`
    :   Registrations completed post-viewing the ad.

    `reactions: Any`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Any`
    :   Total registrations completed through the ad.

    `sends: Any`
    :   Number of messages sent through the ad.

    `shares: Any`
    :   Total shares generated by the ad.

    `sponsored_creative: Any`
    :   Sponsored creative

    `start_date: Any`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Any`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Any`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Any`
    :   Clicks on text URLs within the ad.

    `total_engagements: Any`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Any`
    :   Leads generated through valid work emails.

    `video_completions: Any`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Any`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Any`
    :   Completions for midpoint of video views.

    `video_starts: Any`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Any`
    :   Completions for third quartile of video views.

    `video_views: Any`
    :   Total views of videos in the ad.

    `viral_card_clicks: Any`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Any`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Any`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Any`
    :   Likes received on comments in viral distribution.

    `viral_comments: Any`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Any`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Any`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Any`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Any`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Any`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Any`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Any`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Any`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Any`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Any`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Any`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Any`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Any`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Any`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Any`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Any`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Any`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Any`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Any`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Any`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Any`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Any`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Any`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Any`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Any`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Any`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Any`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Any`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Any`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Any`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Any`
    :   Total views of videos in viral distribution of the ad.

<a id="AdCreativeAnalyticsArrayContainsCondition"></a>

`AdCreativeAnalyticsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsContainsCondition"></a>

`AdCreativeAnalyticsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsEndswithCondition"></a>

`AdCreativeAnalyticsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsStringFilter`
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
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: list[float]`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: list[float]`
    :   An approximation of unique ad impressions.

    `card_clicks: list[float]`
    :   The number of clicks on interactive card elements.

    `card_impressions: list[float]`
    :   The number of times interactive cards were displayed.

    `clicks: list[float]`
    :   Total number of clicks on the ad.

    `comment_likes: list[float]`
    :   The count of likes on comments related to the ad.

    `comments: list[float]`
    :   The number of comments on the ad.

    `company_page_clicks: list[float]`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: list[float]`
    :   Conversion value in the local currency.

    `cost_in_local_currency: list[float]`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: list[float]`
    :   Cost of ad campaign in USD.

    `document_completions: list[float]`
    :   Number of completions for document views.

    `document_first_quartile_completions: list[float]`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: list[float]`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: list[float]`
    :   Completions for third quartile of document views.

    `download_clicks: list[float]`
    :   Clicks on download links in the ad.

    `end_date: list[str]`
    :   End date of the ad analytics data.

    `external_website_conversions: list[float]`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites.

    `follows: list[float]`
    :   Number of follows generated by the ad.

    `full_screen_plays: list[float]`
    :   Number of times videos were played in fullscreen mode.

    `impressions: list[float]`
    :   Total number of times the ad was displayed.

    `job_applications: list[float]`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: list[float]`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: list[float]`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: list[float]`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: list[float]`
    :   Clicks on expressing interest through lead generation mail.

    `likes: list[float]`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: list[float]`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: list[float]`
    :   Leads generated in one click.

    `opens: list[float]`
    :   The number of times the ad was opened or expanded.

    `other_engagements: list[float]`
    :   Engagements other than clicks on the ad.

    `pivot: list[str]`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[list[typing.Any]]`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: list[float]`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: list[float]`
    :   Registrations completed post-viewing the ad.

    `reactions: list[float]`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: list[float]`
    :   Total registrations completed through the ad.

    `sends: list[float]`
    :   Number of messages sent through the ad.

    `shares: list[float]`
    :   Total shares generated by the ad.

    `sponsored_creative: list[str]`
    :   Sponsored creative

    `start_date: list[str]`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: list[str]`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: list[float]`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: list[float]`
    :   Clicks on text URLs within the ad.

    `total_engagements: list[float]`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: list[float]`
    :   Leads generated through valid work emails.

    `video_completions: list[float]`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: list[float]`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: list[float]`
    :   Completions for midpoint of video views.

    `video_starts: list[float]`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: list[float]`
    :   Completions for third quartile of video views.

    `video_views: list[float]`
    :   Total views of videos in the ad.

    `viral_card_clicks: list[float]`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: list[float]`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: list[float]`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: list[float]`
    :   Likes received on comments in viral distribution.

    `viral_comments: list[float]`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: list[float]`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: list[float]`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: list[float]`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: list[float]`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: list[float]`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: list[float]`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: list[float]`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: list[float]`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: list[float]`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: list[float]`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: list[float]`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: list[float]`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: list[float]`
    :   Clicks on landing page in viral distribution.

    `viral_likes: list[float]`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: list[float]`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: list[float]`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: list[float]`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: list[float]`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: list[float]`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: list[float]`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: list[float]`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: list[float]`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: list[float]`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: list[float]`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: list[float]`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: list[float]`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: list[float]`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: list[float]`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: list[float]`
    :   Total views of videos in viral distribution of the ad.

<a id="AdCreativeAnalyticsKeywordCondition"></a>

`AdCreativeAnalyticsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsStringFilter`
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

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsSearchFilter"></a>

`AdCreativeAnalyticsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_creative_analytics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: float | None`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: float | None`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: float | None`
    :   An approximation of unique ad impressions.

    `card_clicks: float | None`
    :   The number of clicks on interactive card elements.

    `card_impressions: float | None`
    :   The number of times interactive cards were displayed.

    `clicks: float | None`
    :   Total number of clicks on the ad.

    `comment_likes: float | None`
    :   The count of likes on comments related to the ad.

    `comments: float | None`
    :   The number of comments on the ad.

    `company_page_clicks: float | None`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: float | None`
    :   Conversion value in the local currency.

    `cost_in_local_currency: float | None`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: float | None`
    :   Cost of ad campaign in USD.

    `document_completions: float | None`
    :   Number of completions for document views.

    `document_first_quartile_completions: float | None`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: float | None`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: float | None`
    :   Completions for third quartile of document views.

    `download_clicks: float | None`
    :   Clicks on download links in the ad.

    `end_date: str | None`
    :   End date of the ad analytics data.

    `external_website_conversions: float | None`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites.

    `follows: float | None`
    :   Number of follows generated by the ad.

    `full_screen_plays: float | None`
    :   Number of times videos were played in fullscreen mode.

    `impressions: float | None`
    :   Total number of times the ad was displayed.

    `job_applications: float | None`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: float | None`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: float | None`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: float | None`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: float | None`
    :   Clicks on expressing interest through lead generation mail.

    `likes: float | None`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: float | None`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: float | None`
    :   Leads generated in one click.

    `opens: float | None`
    :   The number of times the ad was opened or expanded.

    `other_engagements: float | None`
    :   Engagements other than clicks on the ad.

    `pivot: str | None`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[typing.Any] | None`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: float | None`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: float | None`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: float | None`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: float | None`
    :   Registrations completed post-viewing the ad.

    `reactions: float | None`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: float | None`
    :   Total registrations completed through the ad.

    `sends: float | None`
    :   Number of messages sent through the ad.

    `shares: float | None`
    :   Total shares generated by the ad.

    `sponsored_creative: str | None`
    :   Sponsored creative

    `start_date: str | None`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str | None`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: float | None`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: float | None`
    :   Clicks on text URLs within the ad.

    `total_engagements: float | None`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: float | None`
    :   Leads generated through valid work emails.

    `video_completions: float | None`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: float | None`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: float | None`
    :   Completions for midpoint of video views.

    `video_starts: float | None`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: float | None`
    :   Completions for third quartile of video views.

    `video_views: float | None`
    :   Total views of videos in the ad.

    `viral_card_clicks: float | None`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: float | None`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: float | None`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: float | None`
    :   Likes received on comments in viral distribution.

    `viral_comments: float | None`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: float | None`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: float | None`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: float | None`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: float | None`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: float | None`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: float | None`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: float | None`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: float | None`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: float | None`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: float | None`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: float | None`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: float | None`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: float | None`
    :   Clicks on landing page in viral distribution.

    `viral_likes: float | None`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: float | None`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: float | None`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: float | None`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: float | None`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: float | None`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: float | None`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: float | None`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: float | None`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: float | None`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: float | None`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: float | None`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: float | None`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: float | None`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: float | None`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: float | None`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: float | None`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: float | None`
    :   Total views of videos in viral distribution of the ad.

<a id="AdCreativeAnalyticsSearchQuery"></a>

`AdCreativeAnalyticsSearchQuery(*args, **kwargs)`
:   Search query for ad_creative_analytics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsAnyCondition`
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
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Literal['asc', 'desc']`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Literal['asc', 'desc']`
    :   An approximation of unique ad impressions.

    `card_clicks: Literal['asc', 'desc']`
    :   The number of clicks on interactive card elements.

    `card_impressions: Literal['asc', 'desc']`
    :   The number of times interactive cards were displayed.

    `clicks: Literal['asc', 'desc']`
    :   Total number of clicks on the ad.

    `comment_likes: Literal['asc', 'desc']`
    :   The count of likes on comments related to the ad.

    `comments: Literal['asc', 'desc']`
    :   The number of comments on the ad.

    `company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Literal['asc', 'desc']`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Literal['asc', 'desc']`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Literal['asc', 'desc']`
    :   Cost of ad campaign in USD.

    `document_completions: Literal['asc', 'desc']`
    :   Number of completions for document views.

    `document_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of document views.

    `download_clicks: Literal['asc', 'desc']`
    :   Clicks on download links in the ad.

    `end_date: Literal['asc', 'desc']`
    :   End date of the ad analytics data.

    `external_website_conversions: Literal['asc', 'desc']`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites.

    `follows: Literal['asc', 'desc']`
    :   Number of follows generated by the ad.

    `full_screen_plays: Literal['asc', 'desc']`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Literal['asc', 'desc']`
    :   Total number of times the ad was displayed.

    `job_applications: Literal['asc', 'desc']`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Literal['asc', 'desc']`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Literal['asc', 'desc']`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Literal['asc', 'desc']`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Literal['asc', 'desc']`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click.

    `opens: Literal['asc', 'desc']`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Literal['asc', 'desc']`
    :   Engagements other than clicks on the ad.

    `pivot: Literal['asc', 'desc']`
    :   Pivot dimension used for this analytics record

    `pivot_values: Literal['asc', 'desc']`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing the ad.

    `reactions: Literal['asc', 'desc']`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Literal['asc', 'desc']`
    :   Total registrations completed through the ad.

    `sends: Literal['asc', 'desc']`
    :   Number of messages sent through the ad.

    `shares: Literal['asc', 'desc']`
    :   Total shares generated by the ad.

    `sponsored_creative: Literal['asc', 'desc']`
    :   Sponsored creative

    `start_date: Literal['asc', 'desc']`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Literal['asc', 'desc']`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Literal['asc', 'desc']`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Literal['asc', 'desc']`
    :   Clicks on text URLs within the ad.

    `total_engagements: Literal['asc', 'desc']`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Literal['asc', 'desc']`
    :   Leads generated through valid work emails.

    `video_completions: Literal['asc', 'desc']`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of video views.

    `video_starts: Literal['asc', 'desc']`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of video views.

    `video_views: Literal['asc', 'desc']`
    :   Total views of videos in the ad.

    `viral_card_clicks: Literal['asc', 'desc']`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Literal['asc', 'desc']`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Literal['asc', 'desc']`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Literal['asc', 'desc']`
    :   Likes received on comments in viral distribution.

    `viral_comments: Literal['asc', 'desc']`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Literal['asc', 'desc']`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Literal['asc', 'desc']`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Literal['asc', 'desc']`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Literal['asc', 'desc']`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Literal['asc', 'desc']`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Literal['asc', 'desc']`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Literal['asc', 'desc']`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Literal['asc', 'desc']`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Literal['asc', 'desc']`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Literal['asc', 'desc']`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Literal['asc', 'desc']`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Literal['asc', 'desc']`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Literal['asc', 'desc']`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Literal['asc', 'desc']`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Literal['asc', 'desc']`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Literal['asc', 'desc']`
    :   Total views of videos in viral distribution of the ad.

<a id="AdCreativeAnalyticsStartswithCondition"></a>

`AdCreativeAnalyticsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdCreativeAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsStringFilter"></a>

`AdCreativeAnalyticsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: str`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: str`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: str`
    :   An approximation of unique ad impressions.

    `card_clicks: str`
    :   The number of clicks on interactive card elements.

    `card_impressions: str`
    :   The number of times interactive cards were displayed.

    `clicks: str`
    :   Total number of clicks on the ad.

    `comment_likes: str`
    :   The count of likes on comments related to the ad.

    `comments: str`
    :   The number of comments on the ad.

    `company_page_clicks: str`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: str`
    :   Conversion value in the local currency.

    `cost_in_local_currency: str`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: str`
    :   Cost of ad campaign in USD.

    `document_completions: str`
    :   Number of completions for document views.

    `document_first_quartile_completions: str`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: str`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: str`
    :   Completions for third quartile of document views.

    `download_clicks: str`
    :   Clicks on download links in the ad.

    `end_date: str`
    :   End date of the ad analytics data.

    `external_website_conversions: str`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: str`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: str`
    :   Post-view conversions on external websites.

    `follows: str`
    :   Number of follows generated by the ad.

    `full_screen_plays: str`
    :   Number of times videos were played in fullscreen mode.

    `impressions: str`
    :   Total number of times the ad was displayed.

    `job_applications: str`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: str`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: str`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: str`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: str`
    :   Clicks on expressing interest through lead generation mail.

    `likes: str`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: str`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: str`
    :   Leads generated in one click.

    `opens: str`
    :   The number of times the ad was opened or expanded.

    `other_engagements: str`
    :   Engagements other than clicks on the ad.

    `pivot: str`
    :   Pivot dimension used for this analytics record

    `pivot_values: str`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: str`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: str`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: str`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: str`
    :   Registrations completed post-viewing the ad.

    `reactions: str`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: str`
    :   Total registrations completed through the ad.

    `sends: str`
    :   Number of messages sent through the ad.

    `shares: str`
    :   Total shares generated by the ad.

    `sponsored_creative: str`
    :   Sponsored creative

    `start_date: str`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: str`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: str`
    :   Clicks on text URLs within the ad.

    `total_engagements: str`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: str`
    :   Leads generated through valid work emails.

    `video_completions: str`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: str`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: str`
    :   Completions for midpoint of video views.

    `video_starts: str`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: str`
    :   Completions for third quartile of video views.

    `video_views: str`
    :   Total views of videos in the ad.

    `viral_card_clicks: str`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: str`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: str`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: str`
    :   Likes received on comments in viral distribution.

    `viral_comments: str`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: str`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: str`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: str`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: str`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: str`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: str`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: str`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: str`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: str`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: str`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: str`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: str`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: str`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: str`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: str`
    :   Clicks on landing page in viral distribution.

    `viral_likes: str`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: str`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: str`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: str`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: str`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: str`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: str`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: str`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: str`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: str`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: str`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: str`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: str`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: str`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: str`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: str`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: str`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: str`
    :   Total views of videos in viral distribution of the ad.

<a id="AdImpressionDeviceAnalyticsAndCondition"></a>

`AdImpressionDeviceAnalyticsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsAnyCondition"></a>

`AdImpressionDeviceAnalyticsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsAnyValueFilter"></a>

`AdImpressionDeviceAnalyticsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Any`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Any`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Any`
    :   An approximation of unique ad impressions.

    `card_clicks: Any`
    :   The number of clicks on interactive card elements.

    `card_impressions: Any`
    :   The number of times interactive cards were displayed.

    `clicks: Any`
    :   Total number of clicks on the ad.

    `comment_likes: Any`
    :   The count of likes on comments related to the ad.

    `comments: Any`
    :   The number of comments on the ad.

    `company_page_clicks: Any`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Any`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Any`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Any`
    :   Cost of ad campaign in USD.

    `document_completions: Any`
    :   Number of completions for document views.

    `document_first_quartile_completions: Any`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Any`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Any`
    :   Completions for third quartile of document views.

    `download_clicks: Any`
    :   Clicks on download links in the ad.

    `end_date: Any`
    :   End date of the ad analytics data.

    `external_website_conversions: Any`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites.

    `follows: Any`
    :   Number of follows generated by the ad.

    `full_screen_plays: Any`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Any`
    :   Total number of times the ad was displayed.

    `job_applications: Any`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Any`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Any`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Any`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Any`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Any`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Any`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Any`
    :   Leads generated in one click.

    `opens: Any`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Any`
    :   Engagements other than clicks on the ad.

    `pivot: Any`
    :   Pivot dimension used for this analytics record

    `pivot_values: Any`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Any`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Any`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Any`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Any`
    :   Registrations completed post-viewing the ad.

    `reactions: Any`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Any`
    :   Total registrations completed through the ad.

    `sends: Any`
    :   Number of messages sent through the ad.

    `shares: Any`
    :   Total shares generated by the ad.

    `sponsored_campaign: Any`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Any`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Any`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Any`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Any`
    :   Clicks on text URLs within the ad.

    `total_engagements: Any`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Any`
    :   Leads generated through valid work emails.

    `video_completions: Any`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Any`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Any`
    :   Completions for midpoint of video views.

    `video_starts: Any`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Any`
    :   Completions for third quartile of video views.

    `video_views: Any`
    :   Total views of videos in the ad.

    `viral_card_clicks: Any`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Any`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Any`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Any`
    :   Likes received on comments in viral distribution.

    `viral_comments: Any`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Any`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Any`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Any`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Any`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Any`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Any`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Any`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Any`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Any`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Any`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Any`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Any`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Any`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Any`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Any`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Any`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Any`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Any`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Any`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Any`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Any`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Any`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Any`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Any`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Any`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Any`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Any`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Any`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Any`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Any`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Any`
    :   Total views of videos in viral distribution of the ad.

<a id="AdImpressionDeviceAnalyticsArrayContainsCondition"></a>

`AdImpressionDeviceAnalyticsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsContainsCondition"></a>

`AdImpressionDeviceAnalyticsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsEndswithCondition"></a>

`AdImpressionDeviceAnalyticsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsEqCondition"></a>

`AdImpressionDeviceAnalyticsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsFuzzyCondition"></a>

`AdImpressionDeviceAnalyticsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsGtCondition"></a>

`AdImpressionDeviceAnalyticsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsGteCondition"></a>

`AdImpressionDeviceAnalyticsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsInCondition"></a>

`AdImpressionDeviceAnalyticsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsInFilter`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsInFilter"></a>

`AdImpressionDeviceAnalyticsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: list[float]`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: list[float]`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: list[float]`
    :   An approximation of unique ad impressions.

    `card_clicks: list[float]`
    :   The number of clicks on interactive card elements.

    `card_impressions: list[float]`
    :   The number of times interactive cards were displayed.

    `clicks: list[float]`
    :   Total number of clicks on the ad.

    `comment_likes: list[float]`
    :   The count of likes on comments related to the ad.

    `comments: list[float]`
    :   The number of comments on the ad.

    `company_page_clicks: list[float]`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: list[float]`
    :   Conversion value in the local currency.

    `cost_in_local_currency: list[float]`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: list[float]`
    :   Cost of ad campaign in USD.

    `document_completions: list[float]`
    :   Number of completions for document views.

    `document_first_quartile_completions: list[float]`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: list[float]`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: list[float]`
    :   Completions for third quartile of document views.

    `download_clicks: list[float]`
    :   Clicks on download links in the ad.

    `end_date: list[str]`
    :   End date of the ad analytics data.

    `external_website_conversions: list[float]`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites.

    `follows: list[float]`
    :   Number of follows generated by the ad.

    `full_screen_plays: list[float]`
    :   Number of times videos were played in fullscreen mode.

    `impressions: list[float]`
    :   Total number of times the ad was displayed.

    `job_applications: list[float]`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: list[float]`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: list[float]`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: list[float]`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: list[float]`
    :   Clicks on expressing interest through lead generation mail.

    `likes: list[float]`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: list[float]`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: list[float]`
    :   Leads generated in one click.

    `opens: list[float]`
    :   The number of times the ad was opened or expanded.

    `other_engagements: list[float]`
    :   Engagements other than clicks on the ad.

    `pivot: list[str]`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[list[typing.Any]]`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: list[float]`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: list[float]`
    :   Registrations completed post-viewing the ad.

    `reactions: list[float]`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: list[float]`
    :   Total registrations completed through the ad.

    `sends: list[float]`
    :   Number of messages sent through the ad.

    `shares: list[float]`
    :   Total shares generated by the ad.

    `sponsored_campaign: list[str]`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: list[str]`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: list[str]`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: list[float]`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: list[float]`
    :   Clicks on text URLs within the ad.

    `total_engagements: list[float]`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: list[float]`
    :   Leads generated through valid work emails.

    `video_completions: list[float]`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: list[float]`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: list[float]`
    :   Completions for midpoint of video views.

    `video_starts: list[float]`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: list[float]`
    :   Completions for third quartile of video views.

    `video_views: list[float]`
    :   Total views of videos in the ad.

    `viral_card_clicks: list[float]`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: list[float]`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: list[float]`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: list[float]`
    :   Likes received on comments in viral distribution.

    `viral_comments: list[float]`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: list[float]`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: list[float]`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: list[float]`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: list[float]`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: list[float]`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: list[float]`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: list[float]`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: list[float]`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: list[float]`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: list[float]`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: list[float]`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: list[float]`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: list[float]`
    :   Clicks on landing page in viral distribution.

    `viral_likes: list[float]`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: list[float]`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: list[float]`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: list[float]`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: list[float]`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: list[float]`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: list[float]`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: list[float]`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: list[float]`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: list[float]`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: list[float]`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: list[float]`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: list[float]`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: list[float]`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: list[float]`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: list[float]`
    :   Total views of videos in viral distribution of the ad.

<a id="AdImpressionDeviceAnalyticsKeywordCondition"></a>

`AdImpressionDeviceAnalyticsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsListParams"></a>

`AdImpressionDeviceAnalyticsListParams(*args, **kwargs)`
:   Parameters for ad_impression_device_analytics.list operation

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

<a id="AdImpressionDeviceAnalyticsLtCondition"></a>

`AdImpressionDeviceAnalyticsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsLteCondition"></a>

`AdImpressionDeviceAnalyticsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsNeqCondition"></a>

`AdImpressionDeviceAnalyticsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsNotCondition"></a>

`AdImpressionDeviceAnalyticsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsAnyCondition`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsOrCondition"></a>

`AdImpressionDeviceAnalyticsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsSearchFilter"></a>

`AdImpressionDeviceAnalyticsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_impression_device_analytics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: float | None`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: float | None`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: float | None`
    :   An approximation of unique ad impressions.

    `card_clicks: float | None`
    :   The number of clicks on interactive card elements.

    `card_impressions: float | None`
    :   The number of times interactive cards were displayed.

    `clicks: float | None`
    :   Total number of clicks on the ad.

    `comment_likes: float | None`
    :   The count of likes on comments related to the ad.

    `comments: float | None`
    :   The number of comments on the ad.

    `company_page_clicks: float | None`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: float | None`
    :   Conversion value in the local currency.

    `cost_in_local_currency: float | None`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: float | None`
    :   Cost of ad campaign in USD.

    `document_completions: float | None`
    :   Number of completions for document views.

    `document_first_quartile_completions: float | None`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: float | None`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: float | None`
    :   Completions for third quartile of document views.

    `download_clicks: float | None`
    :   Clicks on download links in the ad.

    `end_date: str | None`
    :   End date of the ad analytics data.

    `external_website_conversions: float | None`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites.

    `follows: float | None`
    :   Number of follows generated by the ad.

    `full_screen_plays: float | None`
    :   Number of times videos were played in fullscreen mode.

    `impressions: float | None`
    :   Total number of times the ad was displayed.

    `job_applications: float | None`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: float | None`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: float | None`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: float | None`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: float | None`
    :   Clicks on expressing interest through lead generation mail.

    `likes: float | None`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: float | None`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: float | None`
    :   Leads generated in one click.

    `opens: float | None`
    :   The number of times the ad was opened or expanded.

    `other_engagements: float | None`
    :   Engagements other than clicks on the ad.

    `pivot: str | None`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[typing.Any] | None`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: float | None`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: float | None`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: float | None`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: float | None`
    :   Registrations completed post-viewing the ad.

    `reactions: float | None`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: float | None`
    :   Total registrations completed through the ad.

    `sends: float | None`
    :   Number of messages sent through the ad.

    `shares: float | None`
    :   Total shares generated by the ad.

    `sponsored_campaign: str | None`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str | None`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str | None`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: float | None`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: float | None`
    :   Clicks on text URLs within the ad.

    `total_engagements: float | None`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: float | None`
    :   Leads generated through valid work emails.

    `video_completions: float | None`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: float | None`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: float | None`
    :   Completions for midpoint of video views.

    `video_starts: float | None`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: float | None`
    :   Completions for third quartile of video views.

    `video_views: float | None`
    :   Total views of videos in the ad.

    `viral_card_clicks: float | None`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: float | None`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: float | None`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: float | None`
    :   Likes received on comments in viral distribution.

    `viral_comments: float | None`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: float | None`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: float | None`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: float | None`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: float | None`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: float | None`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: float | None`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: float | None`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: float | None`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: float | None`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: float | None`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: float | None`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: float | None`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: float | None`
    :   Clicks on landing page in viral distribution.

    `viral_likes: float | None`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: float | None`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: float | None`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: float | None`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: float | None`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: float | None`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: float | None`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: float | None`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: float | None`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: float | None`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: float | None`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: float | None`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: float | None`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: float | None`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: float | None`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: float | None`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: float | None`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: float | None`
    :   Total views of videos in viral distribution of the ad.

<a id="AdImpressionDeviceAnalyticsSearchQuery"></a>

`AdImpressionDeviceAnalyticsSearchQuery(*args, **kwargs)`
:   Search query for ad_impression_device_analytics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsSortFilter]`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsSortFilter"></a>

`AdImpressionDeviceAnalyticsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_impression_device_analytics search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Literal['asc', 'desc']`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Literal['asc', 'desc']`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Literal['asc', 'desc']`
    :   An approximation of unique ad impressions.

    `card_clicks: Literal['asc', 'desc']`
    :   The number of clicks on interactive card elements.

    `card_impressions: Literal['asc', 'desc']`
    :   The number of times interactive cards were displayed.

    `clicks: Literal['asc', 'desc']`
    :   Total number of clicks on the ad.

    `comment_likes: Literal['asc', 'desc']`
    :   The count of likes on comments related to the ad.

    `comments: Literal['asc', 'desc']`
    :   The number of comments on the ad.

    `company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Literal['asc', 'desc']`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Literal['asc', 'desc']`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Literal['asc', 'desc']`
    :   Cost of ad campaign in USD.

    `document_completions: Literal['asc', 'desc']`
    :   Number of completions for document views.

    `document_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of document views.

    `download_clicks: Literal['asc', 'desc']`
    :   Clicks on download links in the ad.

    `end_date: Literal['asc', 'desc']`
    :   End date of the ad analytics data.

    `external_website_conversions: Literal['asc', 'desc']`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites.

    `follows: Literal['asc', 'desc']`
    :   Number of follows generated by the ad.

    `full_screen_plays: Literal['asc', 'desc']`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Literal['asc', 'desc']`
    :   Total number of times the ad was displayed.

    `job_applications: Literal['asc', 'desc']`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Literal['asc', 'desc']`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Literal['asc', 'desc']`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Literal['asc', 'desc']`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Literal['asc', 'desc']`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click.

    `opens: Literal['asc', 'desc']`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Literal['asc', 'desc']`
    :   Engagements other than clicks on the ad.

    `pivot: Literal['asc', 'desc']`
    :   Pivot dimension used for this analytics record

    `pivot_values: Literal['asc', 'desc']`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing the ad.

    `reactions: Literal['asc', 'desc']`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Literal['asc', 'desc']`
    :   Total registrations completed through the ad.

    `sends: Literal['asc', 'desc']`
    :   Number of messages sent through the ad.

    `shares: Literal['asc', 'desc']`
    :   Total shares generated by the ad.

    `sponsored_campaign: Literal['asc', 'desc']`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Literal['asc', 'desc']`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Literal['asc', 'desc']`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Literal['asc', 'desc']`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Literal['asc', 'desc']`
    :   Clicks on text URLs within the ad.

    `total_engagements: Literal['asc', 'desc']`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Literal['asc', 'desc']`
    :   Leads generated through valid work emails.

    `video_completions: Literal['asc', 'desc']`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of video views.

    `video_starts: Literal['asc', 'desc']`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of video views.

    `video_views: Literal['asc', 'desc']`
    :   Total views of videos in the ad.

    `viral_card_clicks: Literal['asc', 'desc']`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Literal['asc', 'desc']`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Literal['asc', 'desc']`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Literal['asc', 'desc']`
    :   Likes received on comments in viral distribution.

    `viral_comments: Literal['asc', 'desc']`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Literal['asc', 'desc']`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Literal['asc', 'desc']`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Literal['asc', 'desc']`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Literal['asc', 'desc']`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Literal['asc', 'desc']`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Literal['asc', 'desc']`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Literal['asc', 'desc']`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Literal['asc', 'desc']`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Literal['asc', 'desc']`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Literal['asc', 'desc']`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Literal['asc', 'desc']`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Literal['asc', 'desc']`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Literal['asc', 'desc']`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Literal['asc', 'desc']`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Literal['asc', 'desc']`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Literal['asc', 'desc']`
    :   Total views of videos in viral distribution of the ad.

<a id="AdImpressionDeviceAnalyticsStartswithCondition"></a>

`AdImpressionDeviceAnalyticsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdImpressionDeviceAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsStringFilter"></a>

`AdImpressionDeviceAnalyticsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: str`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: str`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: str`
    :   An approximation of unique ad impressions.

    `card_clicks: str`
    :   The number of clicks on interactive card elements.

    `card_impressions: str`
    :   The number of times interactive cards were displayed.

    `clicks: str`
    :   Total number of clicks on the ad.

    `comment_likes: str`
    :   The count of likes on comments related to the ad.

    `comments: str`
    :   The number of comments on the ad.

    `company_page_clicks: str`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: str`
    :   Conversion value in the local currency.

    `cost_in_local_currency: str`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: str`
    :   Cost of ad campaign in USD.

    `document_completions: str`
    :   Number of completions for document views.

    `document_first_quartile_completions: str`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: str`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: str`
    :   Completions for third quartile of document views.

    `download_clicks: str`
    :   Clicks on download links in the ad.

    `end_date: str`
    :   End date of the ad analytics data.

    `external_website_conversions: str`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: str`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: str`
    :   Post-view conversions on external websites.

    `follows: str`
    :   Number of follows generated by the ad.

    `full_screen_plays: str`
    :   Number of times videos were played in fullscreen mode.

    `impressions: str`
    :   Total number of times the ad was displayed.

    `job_applications: str`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: str`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: str`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: str`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: str`
    :   Clicks on expressing interest through lead generation mail.

    `likes: str`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: str`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: str`
    :   Leads generated in one click.

    `opens: str`
    :   The number of times the ad was opened or expanded.

    `other_engagements: str`
    :   Engagements other than clicks on the ad.

    `pivot: str`
    :   Pivot dimension used for this analytics record

    `pivot_values: str`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: str`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: str`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: str`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: str`
    :   Registrations completed post-viewing the ad.

    `reactions: str`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: str`
    :   Total registrations completed through the ad.

    `sends: str`
    :   Number of messages sent through the ad.

    `shares: str`
    :   Total shares generated by the ad.

    `sponsored_campaign: str`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: str`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: str`
    :   Clicks on text URLs within the ad.

    `total_engagements: str`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: str`
    :   Leads generated through valid work emails.

    `video_completions: str`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: str`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: str`
    :   Completions for midpoint of video views.

    `video_starts: str`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: str`
    :   Completions for third quartile of video views.

    `video_views: str`
    :   Total views of videos in the ad.

    `viral_card_clicks: str`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: str`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: str`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: str`
    :   Likes received on comments in viral distribution.

    `viral_comments: str`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: str`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: str`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: str`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: str`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: str`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: str`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: str`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: str`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: str`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: str`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: str`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: str`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: str`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: str`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: str`
    :   Clicks on landing page in viral distribution.

    `viral_likes: str`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: str`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: str`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: str`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: str`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: str`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: str`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: str`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: str`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: str`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: str`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: str`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: str`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: str`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: str`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: str`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: str`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: str`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCompanyAnalyticsAndCondition"></a>

`AdMemberCompanyAnalyticsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsAnyCondition"></a>

`AdMemberCompanyAnalyticsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsAnyValueFilter"></a>

`AdMemberCompanyAnalyticsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Any`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Any`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Any`
    :   An approximation of unique ad impressions.

    `card_clicks: Any`
    :   The number of clicks on interactive card elements.

    `card_impressions: Any`
    :   The number of times interactive cards were displayed.

    `clicks: Any`
    :   Total number of clicks on the ad.

    `comment_likes: Any`
    :   The count of likes on comments related to the ad.

    `comments: Any`
    :   The number of comments on the ad.

    `company_page_clicks: Any`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Any`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Any`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Any`
    :   Cost of ad campaign in USD.

    `document_completions: Any`
    :   Number of completions for document views.

    `document_first_quartile_completions: Any`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Any`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Any`
    :   Completions for third quartile of document views.

    `download_clicks: Any`
    :   Clicks on download links in the ad.

    `end_date: Any`
    :   End date of the ad analytics data.

    `external_website_conversions: Any`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites.

    `follows: Any`
    :   Number of follows generated by the ad.

    `full_screen_plays: Any`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Any`
    :   Total number of times the ad was displayed.

    `job_applications: Any`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Any`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Any`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Any`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Any`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Any`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Any`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Any`
    :   Leads generated in one click.

    `opens: Any`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Any`
    :   Engagements other than clicks on the ad.

    `pivot: Any`
    :   Pivot dimension used for this analytics record

    `pivot_values: Any`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Any`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Any`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Any`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Any`
    :   Registrations completed post-viewing the ad.

    `reactions: Any`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Any`
    :   Total registrations completed through the ad.

    `sends: Any`
    :   Number of messages sent through the ad.

    `shares: Any`
    :   Total shares generated by the ad.

    `sponsored_campaign: Any`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Any`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Any`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Any`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Any`
    :   Clicks on text URLs within the ad.

    `total_engagements: Any`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Any`
    :   Leads generated through valid work emails.

    `video_completions: Any`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Any`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Any`
    :   Completions for midpoint of video views.

    `video_starts: Any`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Any`
    :   Completions for third quartile of video views.

    `video_views: Any`
    :   Total views of videos in the ad.

    `viral_card_clicks: Any`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Any`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Any`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Any`
    :   Likes received on comments in viral distribution.

    `viral_comments: Any`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Any`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Any`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Any`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Any`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Any`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Any`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Any`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Any`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Any`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Any`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Any`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Any`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Any`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Any`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Any`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Any`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Any`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Any`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Any`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Any`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Any`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Any`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Any`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Any`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Any`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Any`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Any`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Any`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Any`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Any`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Any`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCompanyAnalyticsArrayContainsCondition"></a>

`AdMemberCompanyAnalyticsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsContainsCondition"></a>

`AdMemberCompanyAnalyticsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsEndswithCondition"></a>

`AdMemberCompanyAnalyticsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsEqCondition"></a>

`AdMemberCompanyAnalyticsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsFuzzyCondition"></a>

`AdMemberCompanyAnalyticsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsGtCondition"></a>

`AdMemberCompanyAnalyticsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsGteCondition"></a>

`AdMemberCompanyAnalyticsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsInCondition"></a>

`AdMemberCompanyAnalyticsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsInFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsInFilter"></a>

`AdMemberCompanyAnalyticsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: list[float]`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: list[float]`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: list[float]`
    :   An approximation of unique ad impressions.

    `card_clicks: list[float]`
    :   The number of clicks on interactive card elements.

    `card_impressions: list[float]`
    :   The number of times interactive cards were displayed.

    `clicks: list[float]`
    :   Total number of clicks on the ad.

    `comment_likes: list[float]`
    :   The count of likes on comments related to the ad.

    `comments: list[float]`
    :   The number of comments on the ad.

    `company_page_clicks: list[float]`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: list[float]`
    :   Conversion value in the local currency.

    `cost_in_local_currency: list[float]`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: list[float]`
    :   Cost of ad campaign in USD.

    `document_completions: list[float]`
    :   Number of completions for document views.

    `document_first_quartile_completions: list[float]`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: list[float]`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: list[float]`
    :   Completions for third quartile of document views.

    `download_clicks: list[float]`
    :   Clicks on download links in the ad.

    `end_date: list[str]`
    :   End date of the ad analytics data.

    `external_website_conversions: list[float]`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites.

    `follows: list[float]`
    :   Number of follows generated by the ad.

    `full_screen_plays: list[float]`
    :   Number of times videos were played in fullscreen mode.

    `impressions: list[float]`
    :   Total number of times the ad was displayed.

    `job_applications: list[float]`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: list[float]`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: list[float]`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: list[float]`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: list[float]`
    :   Clicks on expressing interest through lead generation mail.

    `likes: list[float]`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: list[float]`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: list[float]`
    :   Leads generated in one click.

    `opens: list[float]`
    :   The number of times the ad was opened or expanded.

    `other_engagements: list[float]`
    :   Engagements other than clicks on the ad.

    `pivot: list[str]`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[list[typing.Any]]`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: list[float]`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: list[float]`
    :   Registrations completed post-viewing the ad.

    `reactions: list[float]`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: list[float]`
    :   Total registrations completed through the ad.

    `sends: list[float]`
    :   Number of messages sent through the ad.

    `shares: list[float]`
    :   Total shares generated by the ad.

    `sponsored_campaign: list[str]`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: list[str]`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: list[str]`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: list[float]`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: list[float]`
    :   Clicks on text URLs within the ad.

    `total_engagements: list[float]`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: list[float]`
    :   Leads generated through valid work emails.

    `video_completions: list[float]`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: list[float]`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: list[float]`
    :   Completions for midpoint of video views.

    `video_starts: list[float]`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: list[float]`
    :   Completions for third quartile of video views.

    `video_views: list[float]`
    :   Total views of videos in the ad.

    `viral_card_clicks: list[float]`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: list[float]`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: list[float]`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: list[float]`
    :   Likes received on comments in viral distribution.

    `viral_comments: list[float]`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: list[float]`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: list[float]`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: list[float]`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: list[float]`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: list[float]`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: list[float]`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: list[float]`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: list[float]`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: list[float]`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: list[float]`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: list[float]`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: list[float]`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: list[float]`
    :   Clicks on landing page in viral distribution.

    `viral_likes: list[float]`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: list[float]`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: list[float]`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: list[float]`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: list[float]`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: list[float]`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: list[float]`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: list[float]`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: list[float]`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: list[float]`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: list[float]`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: list[float]`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: list[float]`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: list[float]`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: list[float]`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: list[float]`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCompanyAnalyticsKeywordCondition"></a>

`AdMemberCompanyAnalyticsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsListParams"></a>

`AdMemberCompanyAnalyticsListParams(*args, **kwargs)`
:   Parameters for ad_member_company_analytics.list operation

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

<a id="AdMemberCompanyAnalyticsLtCondition"></a>

`AdMemberCompanyAnalyticsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsLteCondition"></a>

`AdMemberCompanyAnalyticsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsNeqCondition"></a>

`AdMemberCompanyAnalyticsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsNotCondition"></a>

`AdMemberCompanyAnalyticsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsAnyCondition`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsOrCondition"></a>

`AdMemberCompanyAnalyticsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsSearchFilter"></a>

`AdMemberCompanyAnalyticsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_member_company_analytics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: float | None`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: float | None`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: float | None`
    :   An approximation of unique ad impressions.

    `card_clicks: float | None`
    :   The number of clicks on interactive card elements.

    `card_impressions: float | None`
    :   The number of times interactive cards were displayed.

    `clicks: float | None`
    :   Total number of clicks on the ad.

    `comment_likes: float | None`
    :   The count of likes on comments related to the ad.

    `comments: float | None`
    :   The number of comments on the ad.

    `company_page_clicks: float | None`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: float | None`
    :   Conversion value in the local currency.

    `cost_in_local_currency: float | None`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: float | None`
    :   Cost of ad campaign in USD.

    `document_completions: float | None`
    :   Number of completions for document views.

    `document_first_quartile_completions: float | None`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: float | None`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: float | None`
    :   Completions for third quartile of document views.

    `download_clicks: float | None`
    :   Clicks on download links in the ad.

    `end_date: str | None`
    :   End date of the ad analytics data.

    `external_website_conversions: float | None`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites.

    `follows: float | None`
    :   Number of follows generated by the ad.

    `full_screen_plays: float | None`
    :   Number of times videos were played in fullscreen mode.

    `impressions: float | None`
    :   Total number of times the ad was displayed.

    `job_applications: float | None`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: float | None`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: float | None`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: float | None`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: float | None`
    :   Clicks on expressing interest through lead generation mail.

    `likes: float | None`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: float | None`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: float | None`
    :   Leads generated in one click.

    `opens: float | None`
    :   The number of times the ad was opened or expanded.

    `other_engagements: float | None`
    :   Engagements other than clicks on the ad.

    `pivot: str | None`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[typing.Any] | None`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: float | None`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: float | None`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: float | None`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: float | None`
    :   Registrations completed post-viewing the ad.

    `reactions: float | None`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: float | None`
    :   Total registrations completed through the ad.

    `sends: float | None`
    :   Number of messages sent through the ad.

    `shares: float | None`
    :   Total shares generated by the ad.

    `sponsored_campaign: str | None`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str | None`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str | None`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: float | None`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: float | None`
    :   Clicks on text URLs within the ad.

    `total_engagements: float | None`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: float | None`
    :   Leads generated through valid work emails.

    `video_completions: float | None`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: float | None`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: float | None`
    :   Completions for midpoint of video views.

    `video_starts: float | None`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: float | None`
    :   Completions for third quartile of video views.

    `video_views: float | None`
    :   Total views of videos in the ad.

    `viral_card_clicks: float | None`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: float | None`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: float | None`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: float | None`
    :   Likes received on comments in viral distribution.

    `viral_comments: float | None`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: float | None`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: float | None`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: float | None`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: float | None`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: float | None`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: float | None`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: float | None`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: float | None`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: float | None`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: float | None`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: float | None`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: float | None`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: float | None`
    :   Clicks on landing page in viral distribution.

    `viral_likes: float | None`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: float | None`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: float | None`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: float | None`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: float | None`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: float | None`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: float | None`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: float | None`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: float | None`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: float | None`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: float | None`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: float | None`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: float | None`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: float | None`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: float | None`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: float | None`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: float | None`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: float | None`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCompanyAnalyticsSearchQuery"></a>

`AdMemberCompanyAnalyticsSearchQuery(*args, **kwargs)`
:   Search query for ad_member_company_analytics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsSortFilter]`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsSortFilter"></a>

`AdMemberCompanyAnalyticsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_member_company_analytics search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Literal['asc', 'desc']`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Literal['asc', 'desc']`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Literal['asc', 'desc']`
    :   An approximation of unique ad impressions.

    `card_clicks: Literal['asc', 'desc']`
    :   The number of clicks on interactive card elements.

    `card_impressions: Literal['asc', 'desc']`
    :   The number of times interactive cards were displayed.

    `clicks: Literal['asc', 'desc']`
    :   Total number of clicks on the ad.

    `comment_likes: Literal['asc', 'desc']`
    :   The count of likes on comments related to the ad.

    `comments: Literal['asc', 'desc']`
    :   The number of comments on the ad.

    `company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Literal['asc', 'desc']`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Literal['asc', 'desc']`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Literal['asc', 'desc']`
    :   Cost of ad campaign in USD.

    `document_completions: Literal['asc', 'desc']`
    :   Number of completions for document views.

    `document_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of document views.

    `download_clicks: Literal['asc', 'desc']`
    :   Clicks on download links in the ad.

    `end_date: Literal['asc', 'desc']`
    :   End date of the ad analytics data.

    `external_website_conversions: Literal['asc', 'desc']`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites.

    `follows: Literal['asc', 'desc']`
    :   Number of follows generated by the ad.

    `full_screen_plays: Literal['asc', 'desc']`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Literal['asc', 'desc']`
    :   Total number of times the ad was displayed.

    `job_applications: Literal['asc', 'desc']`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Literal['asc', 'desc']`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Literal['asc', 'desc']`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Literal['asc', 'desc']`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Literal['asc', 'desc']`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click.

    `opens: Literal['asc', 'desc']`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Literal['asc', 'desc']`
    :   Engagements other than clicks on the ad.

    `pivot: Literal['asc', 'desc']`
    :   Pivot dimension used for this analytics record

    `pivot_values: Literal['asc', 'desc']`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing the ad.

    `reactions: Literal['asc', 'desc']`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Literal['asc', 'desc']`
    :   Total registrations completed through the ad.

    `sends: Literal['asc', 'desc']`
    :   Number of messages sent through the ad.

    `shares: Literal['asc', 'desc']`
    :   Total shares generated by the ad.

    `sponsored_campaign: Literal['asc', 'desc']`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Literal['asc', 'desc']`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Literal['asc', 'desc']`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Literal['asc', 'desc']`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Literal['asc', 'desc']`
    :   Clicks on text URLs within the ad.

    `total_engagements: Literal['asc', 'desc']`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Literal['asc', 'desc']`
    :   Leads generated through valid work emails.

    `video_completions: Literal['asc', 'desc']`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of video views.

    `video_starts: Literal['asc', 'desc']`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of video views.

    `video_views: Literal['asc', 'desc']`
    :   Total views of videos in the ad.

    `viral_card_clicks: Literal['asc', 'desc']`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Literal['asc', 'desc']`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Literal['asc', 'desc']`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Literal['asc', 'desc']`
    :   Likes received on comments in viral distribution.

    `viral_comments: Literal['asc', 'desc']`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Literal['asc', 'desc']`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Literal['asc', 'desc']`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Literal['asc', 'desc']`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Literal['asc', 'desc']`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Literal['asc', 'desc']`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Literal['asc', 'desc']`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Literal['asc', 'desc']`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Literal['asc', 'desc']`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Literal['asc', 'desc']`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Literal['asc', 'desc']`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Literal['asc', 'desc']`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Literal['asc', 'desc']`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Literal['asc', 'desc']`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Literal['asc', 'desc']`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Literal['asc', 'desc']`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Literal['asc', 'desc']`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCompanyAnalyticsStartswithCondition"></a>

`AdMemberCompanyAnalyticsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanyAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsStringFilter"></a>

`AdMemberCompanyAnalyticsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: str`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: str`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: str`
    :   An approximation of unique ad impressions.

    `card_clicks: str`
    :   The number of clicks on interactive card elements.

    `card_impressions: str`
    :   The number of times interactive cards were displayed.

    `clicks: str`
    :   Total number of clicks on the ad.

    `comment_likes: str`
    :   The count of likes on comments related to the ad.

    `comments: str`
    :   The number of comments on the ad.

    `company_page_clicks: str`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: str`
    :   Conversion value in the local currency.

    `cost_in_local_currency: str`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: str`
    :   Cost of ad campaign in USD.

    `document_completions: str`
    :   Number of completions for document views.

    `document_first_quartile_completions: str`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: str`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: str`
    :   Completions for third quartile of document views.

    `download_clicks: str`
    :   Clicks on download links in the ad.

    `end_date: str`
    :   End date of the ad analytics data.

    `external_website_conversions: str`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: str`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: str`
    :   Post-view conversions on external websites.

    `follows: str`
    :   Number of follows generated by the ad.

    `full_screen_plays: str`
    :   Number of times videos were played in fullscreen mode.

    `impressions: str`
    :   Total number of times the ad was displayed.

    `job_applications: str`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: str`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: str`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: str`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: str`
    :   Clicks on expressing interest through lead generation mail.

    `likes: str`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: str`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: str`
    :   Leads generated in one click.

    `opens: str`
    :   The number of times the ad was opened or expanded.

    `other_engagements: str`
    :   Engagements other than clicks on the ad.

    `pivot: str`
    :   Pivot dimension used for this analytics record

    `pivot_values: str`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: str`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: str`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: str`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: str`
    :   Registrations completed post-viewing the ad.

    `reactions: str`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: str`
    :   Total registrations completed through the ad.

    `sends: str`
    :   Number of messages sent through the ad.

    `shares: str`
    :   Total shares generated by the ad.

    `sponsored_campaign: str`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: str`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: str`
    :   Clicks on text URLs within the ad.

    `total_engagements: str`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: str`
    :   Leads generated through valid work emails.

    `video_completions: str`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: str`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: str`
    :   Completions for midpoint of video views.

    `video_starts: str`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: str`
    :   Completions for third quartile of video views.

    `video_views: str`
    :   Total views of videos in the ad.

    `viral_card_clicks: str`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: str`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: str`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: str`
    :   Likes received on comments in viral distribution.

    `viral_comments: str`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: str`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: str`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: str`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: str`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: str`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: str`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: str`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: str`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: str`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: str`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: str`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: str`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: str`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: str`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: str`
    :   Clicks on landing page in viral distribution.

    `viral_likes: str`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: str`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: str`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: str`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: str`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: str`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: str`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: str`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: str`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: str`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: str`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: str`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: str`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: str`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: str`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: str`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: str`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: str`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCompanySizeAnalyticsAndCondition"></a>

`AdMemberCompanySizeAnalyticsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsAnyCondition"></a>

`AdMemberCompanySizeAnalyticsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsAnyValueFilter"></a>

`AdMemberCompanySizeAnalyticsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Any`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Any`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Any`
    :   An approximation of unique ad impressions.

    `card_clicks: Any`
    :   The number of clicks on interactive card elements.

    `card_impressions: Any`
    :   The number of times interactive cards were displayed.

    `clicks: Any`
    :   Total number of clicks on the ad.

    `comment_likes: Any`
    :   The count of likes on comments related to the ad.

    `comments: Any`
    :   The number of comments on the ad.

    `company_page_clicks: Any`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Any`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Any`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Any`
    :   Cost of ad campaign in USD.

    `document_completions: Any`
    :   Number of completions for document views.

    `document_first_quartile_completions: Any`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Any`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Any`
    :   Completions for third quartile of document views.

    `download_clicks: Any`
    :   Clicks on download links in the ad.

    `end_date: Any`
    :   End date of the ad analytics data.

    `external_website_conversions: Any`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites.

    `follows: Any`
    :   Number of follows generated by the ad.

    `full_screen_plays: Any`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Any`
    :   Total number of times the ad was displayed.

    `job_applications: Any`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Any`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Any`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Any`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Any`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Any`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Any`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Any`
    :   Leads generated in one click.

    `opens: Any`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Any`
    :   Engagements other than clicks on the ad.

    `pivot: Any`
    :   Pivot dimension used for this analytics record

    `pivot_values: Any`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Any`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Any`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Any`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Any`
    :   Registrations completed post-viewing the ad.

    `reactions: Any`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Any`
    :   Total registrations completed through the ad.

    `sends: Any`
    :   Number of messages sent through the ad.

    `shares: Any`
    :   Total shares generated by the ad.

    `sponsored_campaign: Any`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Any`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Any`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Any`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Any`
    :   Clicks on text URLs within the ad.

    `total_engagements: Any`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Any`
    :   Leads generated through valid work emails.

    `video_completions: Any`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Any`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Any`
    :   Completions for midpoint of video views.

    `video_starts: Any`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Any`
    :   Completions for third quartile of video views.

    `video_views: Any`
    :   Total views of videos in the ad.

    `viral_card_clicks: Any`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Any`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Any`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Any`
    :   Likes received on comments in viral distribution.

    `viral_comments: Any`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Any`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Any`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Any`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Any`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Any`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Any`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Any`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Any`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Any`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Any`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Any`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Any`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Any`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Any`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Any`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Any`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Any`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Any`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Any`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Any`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Any`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Any`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Any`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Any`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Any`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Any`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Any`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Any`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Any`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Any`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Any`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCompanySizeAnalyticsArrayContainsCondition"></a>

`AdMemberCompanySizeAnalyticsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsContainsCondition"></a>

`AdMemberCompanySizeAnalyticsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsEndswithCondition"></a>

`AdMemberCompanySizeAnalyticsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsEqCondition"></a>

`AdMemberCompanySizeAnalyticsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsFuzzyCondition"></a>

`AdMemberCompanySizeAnalyticsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsGtCondition"></a>

`AdMemberCompanySizeAnalyticsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsGteCondition"></a>

`AdMemberCompanySizeAnalyticsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsInCondition"></a>

`AdMemberCompanySizeAnalyticsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsInFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsInFilter"></a>

`AdMemberCompanySizeAnalyticsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: list[float]`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: list[float]`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: list[float]`
    :   An approximation of unique ad impressions.

    `card_clicks: list[float]`
    :   The number of clicks on interactive card elements.

    `card_impressions: list[float]`
    :   The number of times interactive cards were displayed.

    `clicks: list[float]`
    :   Total number of clicks on the ad.

    `comment_likes: list[float]`
    :   The count of likes on comments related to the ad.

    `comments: list[float]`
    :   The number of comments on the ad.

    `company_page_clicks: list[float]`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: list[float]`
    :   Conversion value in the local currency.

    `cost_in_local_currency: list[float]`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: list[float]`
    :   Cost of ad campaign in USD.

    `document_completions: list[float]`
    :   Number of completions for document views.

    `document_first_quartile_completions: list[float]`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: list[float]`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: list[float]`
    :   Completions for third quartile of document views.

    `download_clicks: list[float]`
    :   Clicks on download links in the ad.

    `end_date: list[str]`
    :   End date of the ad analytics data.

    `external_website_conversions: list[float]`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites.

    `follows: list[float]`
    :   Number of follows generated by the ad.

    `full_screen_plays: list[float]`
    :   Number of times videos were played in fullscreen mode.

    `impressions: list[float]`
    :   Total number of times the ad was displayed.

    `job_applications: list[float]`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: list[float]`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: list[float]`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: list[float]`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: list[float]`
    :   Clicks on expressing interest through lead generation mail.

    `likes: list[float]`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: list[float]`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: list[float]`
    :   Leads generated in one click.

    `opens: list[float]`
    :   The number of times the ad was opened or expanded.

    `other_engagements: list[float]`
    :   Engagements other than clicks on the ad.

    `pivot: list[str]`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[list[typing.Any]]`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: list[float]`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: list[float]`
    :   Registrations completed post-viewing the ad.

    `reactions: list[float]`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: list[float]`
    :   Total registrations completed through the ad.

    `sends: list[float]`
    :   Number of messages sent through the ad.

    `shares: list[float]`
    :   Total shares generated by the ad.

    `sponsored_campaign: list[str]`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: list[str]`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: list[str]`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: list[float]`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: list[float]`
    :   Clicks on text URLs within the ad.

    `total_engagements: list[float]`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: list[float]`
    :   Leads generated through valid work emails.

    `video_completions: list[float]`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: list[float]`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: list[float]`
    :   Completions for midpoint of video views.

    `video_starts: list[float]`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: list[float]`
    :   Completions for third quartile of video views.

    `video_views: list[float]`
    :   Total views of videos in the ad.

    `viral_card_clicks: list[float]`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: list[float]`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: list[float]`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: list[float]`
    :   Likes received on comments in viral distribution.

    `viral_comments: list[float]`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: list[float]`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: list[float]`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: list[float]`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: list[float]`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: list[float]`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: list[float]`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: list[float]`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: list[float]`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: list[float]`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: list[float]`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: list[float]`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: list[float]`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: list[float]`
    :   Clicks on landing page in viral distribution.

    `viral_likes: list[float]`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: list[float]`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: list[float]`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: list[float]`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: list[float]`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: list[float]`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: list[float]`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: list[float]`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: list[float]`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: list[float]`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: list[float]`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: list[float]`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: list[float]`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: list[float]`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: list[float]`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: list[float]`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCompanySizeAnalyticsKeywordCondition"></a>

`AdMemberCompanySizeAnalyticsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsListParams"></a>

`AdMemberCompanySizeAnalyticsListParams(*args, **kwargs)`
:   Parameters for ad_member_company_size_analytics.list operation

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

<a id="AdMemberCompanySizeAnalyticsLtCondition"></a>

`AdMemberCompanySizeAnalyticsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsLteCondition"></a>

`AdMemberCompanySizeAnalyticsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsNeqCondition"></a>

`AdMemberCompanySizeAnalyticsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsNotCondition"></a>

`AdMemberCompanySizeAnalyticsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsAnyCondition`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsOrCondition"></a>

`AdMemberCompanySizeAnalyticsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsSearchFilter"></a>

`AdMemberCompanySizeAnalyticsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_member_company_size_analytics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: float | None`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: float | None`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: float | None`
    :   An approximation of unique ad impressions.

    `card_clicks: float | None`
    :   The number of clicks on interactive card elements.

    `card_impressions: float | None`
    :   The number of times interactive cards were displayed.

    `clicks: float | None`
    :   Total number of clicks on the ad.

    `comment_likes: float | None`
    :   The count of likes on comments related to the ad.

    `comments: float | None`
    :   The number of comments on the ad.

    `company_page_clicks: float | None`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: float | None`
    :   Conversion value in the local currency.

    `cost_in_local_currency: float | None`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: float | None`
    :   Cost of ad campaign in USD.

    `document_completions: float | None`
    :   Number of completions for document views.

    `document_first_quartile_completions: float | None`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: float | None`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: float | None`
    :   Completions for third quartile of document views.

    `download_clicks: float | None`
    :   Clicks on download links in the ad.

    `end_date: str | None`
    :   End date of the ad analytics data.

    `external_website_conversions: float | None`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites.

    `follows: float | None`
    :   Number of follows generated by the ad.

    `full_screen_plays: float | None`
    :   Number of times videos were played in fullscreen mode.

    `impressions: float | None`
    :   Total number of times the ad was displayed.

    `job_applications: float | None`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: float | None`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: float | None`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: float | None`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: float | None`
    :   Clicks on expressing interest through lead generation mail.

    `likes: float | None`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: float | None`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: float | None`
    :   Leads generated in one click.

    `opens: float | None`
    :   The number of times the ad was opened or expanded.

    `other_engagements: float | None`
    :   Engagements other than clicks on the ad.

    `pivot: str | None`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[typing.Any] | None`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: float | None`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: float | None`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: float | None`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: float | None`
    :   Registrations completed post-viewing the ad.

    `reactions: float | None`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: float | None`
    :   Total registrations completed through the ad.

    `sends: float | None`
    :   Number of messages sent through the ad.

    `shares: float | None`
    :   Total shares generated by the ad.

    `sponsored_campaign: str | None`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str | None`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str | None`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: float | None`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: float | None`
    :   Clicks on text URLs within the ad.

    `total_engagements: float | None`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: float | None`
    :   Leads generated through valid work emails.

    `video_completions: float | None`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: float | None`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: float | None`
    :   Completions for midpoint of video views.

    `video_starts: float | None`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: float | None`
    :   Completions for third quartile of video views.

    `video_views: float | None`
    :   Total views of videos in the ad.

    `viral_card_clicks: float | None`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: float | None`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: float | None`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: float | None`
    :   Likes received on comments in viral distribution.

    `viral_comments: float | None`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: float | None`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: float | None`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: float | None`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: float | None`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: float | None`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: float | None`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: float | None`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: float | None`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: float | None`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: float | None`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: float | None`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: float | None`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: float | None`
    :   Clicks on landing page in viral distribution.

    `viral_likes: float | None`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: float | None`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: float | None`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: float | None`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: float | None`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: float | None`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: float | None`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: float | None`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: float | None`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: float | None`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: float | None`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: float | None`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: float | None`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: float | None`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: float | None`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: float | None`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: float | None`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: float | None`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCompanySizeAnalyticsSearchQuery"></a>

`AdMemberCompanySizeAnalyticsSearchQuery(*args, **kwargs)`
:   Search query for ad_member_company_size_analytics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsSortFilter]`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsSortFilter"></a>

`AdMemberCompanySizeAnalyticsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_member_company_size_analytics search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Literal['asc', 'desc']`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Literal['asc', 'desc']`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Literal['asc', 'desc']`
    :   An approximation of unique ad impressions.

    `card_clicks: Literal['asc', 'desc']`
    :   The number of clicks on interactive card elements.

    `card_impressions: Literal['asc', 'desc']`
    :   The number of times interactive cards were displayed.

    `clicks: Literal['asc', 'desc']`
    :   Total number of clicks on the ad.

    `comment_likes: Literal['asc', 'desc']`
    :   The count of likes on comments related to the ad.

    `comments: Literal['asc', 'desc']`
    :   The number of comments on the ad.

    `company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Literal['asc', 'desc']`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Literal['asc', 'desc']`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Literal['asc', 'desc']`
    :   Cost of ad campaign in USD.

    `document_completions: Literal['asc', 'desc']`
    :   Number of completions for document views.

    `document_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of document views.

    `download_clicks: Literal['asc', 'desc']`
    :   Clicks on download links in the ad.

    `end_date: Literal['asc', 'desc']`
    :   End date of the ad analytics data.

    `external_website_conversions: Literal['asc', 'desc']`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites.

    `follows: Literal['asc', 'desc']`
    :   Number of follows generated by the ad.

    `full_screen_plays: Literal['asc', 'desc']`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Literal['asc', 'desc']`
    :   Total number of times the ad was displayed.

    `job_applications: Literal['asc', 'desc']`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Literal['asc', 'desc']`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Literal['asc', 'desc']`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Literal['asc', 'desc']`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Literal['asc', 'desc']`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click.

    `opens: Literal['asc', 'desc']`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Literal['asc', 'desc']`
    :   Engagements other than clicks on the ad.

    `pivot: Literal['asc', 'desc']`
    :   Pivot dimension used for this analytics record

    `pivot_values: Literal['asc', 'desc']`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing the ad.

    `reactions: Literal['asc', 'desc']`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Literal['asc', 'desc']`
    :   Total registrations completed through the ad.

    `sends: Literal['asc', 'desc']`
    :   Number of messages sent through the ad.

    `shares: Literal['asc', 'desc']`
    :   Total shares generated by the ad.

    `sponsored_campaign: Literal['asc', 'desc']`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Literal['asc', 'desc']`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Literal['asc', 'desc']`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Literal['asc', 'desc']`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Literal['asc', 'desc']`
    :   Clicks on text URLs within the ad.

    `total_engagements: Literal['asc', 'desc']`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Literal['asc', 'desc']`
    :   Leads generated through valid work emails.

    `video_completions: Literal['asc', 'desc']`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of video views.

    `video_starts: Literal['asc', 'desc']`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of video views.

    `video_views: Literal['asc', 'desc']`
    :   Total views of videos in the ad.

    `viral_card_clicks: Literal['asc', 'desc']`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Literal['asc', 'desc']`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Literal['asc', 'desc']`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Literal['asc', 'desc']`
    :   Likes received on comments in viral distribution.

    `viral_comments: Literal['asc', 'desc']`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Literal['asc', 'desc']`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Literal['asc', 'desc']`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Literal['asc', 'desc']`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Literal['asc', 'desc']`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Literal['asc', 'desc']`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Literal['asc', 'desc']`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Literal['asc', 'desc']`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Literal['asc', 'desc']`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Literal['asc', 'desc']`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Literal['asc', 'desc']`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Literal['asc', 'desc']`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Literal['asc', 'desc']`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Literal['asc', 'desc']`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Literal['asc', 'desc']`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Literal['asc', 'desc']`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Literal['asc', 'desc']`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCompanySizeAnalyticsStartswithCondition"></a>

`AdMemberCompanySizeAnalyticsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCompanySizeAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsStringFilter"></a>

`AdMemberCompanySizeAnalyticsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: str`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: str`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: str`
    :   An approximation of unique ad impressions.

    `card_clicks: str`
    :   The number of clicks on interactive card elements.

    `card_impressions: str`
    :   The number of times interactive cards were displayed.

    `clicks: str`
    :   Total number of clicks on the ad.

    `comment_likes: str`
    :   The count of likes on comments related to the ad.

    `comments: str`
    :   The number of comments on the ad.

    `company_page_clicks: str`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: str`
    :   Conversion value in the local currency.

    `cost_in_local_currency: str`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: str`
    :   Cost of ad campaign in USD.

    `document_completions: str`
    :   Number of completions for document views.

    `document_first_quartile_completions: str`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: str`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: str`
    :   Completions for third quartile of document views.

    `download_clicks: str`
    :   Clicks on download links in the ad.

    `end_date: str`
    :   End date of the ad analytics data.

    `external_website_conversions: str`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: str`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: str`
    :   Post-view conversions on external websites.

    `follows: str`
    :   Number of follows generated by the ad.

    `full_screen_plays: str`
    :   Number of times videos were played in fullscreen mode.

    `impressions: str`
    :   Total number of times the ad was displayed.

    `job_applications: str`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: str`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: str`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: str`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: str`
    :   Clicks on expressing interest through lead generation mail.

    `likes: str`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: str`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: str`
    :   Leads generated in one click.

    `opens: str`
    :   The number of times the ad was opened or expanded.

    `other_engagements: str`
    :   Engagements other than clicks on the ad.

    `pivot: str`
    :   Pivot dimension used for this analytics record

    `pivot_values: str`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: str`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: str`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: str`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: str`
    :   Registrations completed post-viewing the ad.

    `reactions: str`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: str`
    :   Total registrations completed through the ad.

    `sends: str`
    :   Number of messages sent through the ad.

    `shares: str`
    :   Total shares generated by the ad.

    `sponsored_campaign: str`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: str`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: str`
    :   Clicks on text URLs within the ad.

    `total_engagements: str`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: str`
    :   Leads generated through valid work emails.

    `video_completions: str`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: str`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: str`
    :   Completions for midpoint of video views.

    `video_starts: str`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: str`
    :   Completions for third quartile of video views.

    `video_views: str`
    :   Total views of videos in the ad.

    `viral_card_clicks: str`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: str`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: str`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: str`
    :   Likes received on comments in viral distribution.

    `viral_comments: str`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: str`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: str`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: str`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: str`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: str`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: str`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: str`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: str`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: str`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: str`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: str`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: str`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: str`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: str`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: str`
    :   Clicks on landing page in viral distribution.

    `viral_likes: str`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: str`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: str`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: str`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: str`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: str`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: str`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: str`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: str`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: str`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: str`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: str`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: str`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: str`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: str`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: str`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: str`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: str`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCountryAnalyticsAndCondition"></a>

`AdMemberCountryAnalyticsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsAnyCondition"></a>

`AdMemberCountryAnalyticsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsAnyValueFilter"></a>

`AdMemberCountryAnalyticsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Any`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Any`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Any`
    :   An approximation of unique ad impressions.

    `card_clicks: Any`
    :   The number of clicks on interactive card elements.

    `card_impressions: Any`
    :   The number of times interactive cards were displayed.

    `clicks: Any`
    :   Total number of clicks on the ad.

    `comment_likes: Any`
    :   The count of likes on comments related to the ad.

    `comments: Any`
    :   The number of comments on the ad.

    `company_page_clicks: Any`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Any`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Any`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Any`
    :   Cost of ad campaign in USD.

    `document_completions: Any`
    :   Number of completions for document views.

    `document_first_quartile_completions: Any`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Any`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Any`
    :   Completions for third quartile of document views.

    `download_clicks: Any`
    :   Clicks on download links in the ad.

    `end_date: Any`
    :   End date of the ad analytics data.

    `external_website_conversions: Any`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites.

    `follows: Any`
    :   Number of follows generated by the ad.

    `full_screen_plays: Any`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Any`
    :   Total number of times the ad was displayed.

    `job_applications: Any`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Any`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Any`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Any`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Any`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Any`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Any`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Any`
    :   Leads generated in one click.

    `opens: Any`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Any`
    :   Engagements other than clicks on the ad.

    `pivot: Any`
    :   Pivot dimension used for this analytics record

    `pivot_values: Any`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Any`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Any`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Any`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Any`
    :   Registrations completed post-viewing the ad.

    `reactions: Any`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Any`
    :   Total registrations completed through the ad.

    `sends: Any`
    :   Number of messages sent through the ad.

    `shares: Any`
    :   Total shares generated by the ad.

    `sponsored_campaign: Any`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Any`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Any`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Any`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Any`
    :   Clicks on text URLs within the ad.

    `total_engagements: Any`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Any`
    :   Leads generated through valid work emails.

    `video_completions: Any`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Any`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Any`
    :   Completions for midpoint of video views.

    `video_starts: Any`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Any`
    :   Completions for third quartile of video views.

    `video_views: Any`
    :   Total views of videos in the ad.

    `viral_card_clicks: Any`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Any`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Any`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Any`
    :   Likes received on comments in viral distribution.

    `viral_comments: Any`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Any`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Any`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Any`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Any`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Any`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Any`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Any`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Any`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Any`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Any`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Any`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Any`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Any`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Any`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Any`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Any`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Any`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Any`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Any`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Any`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Any`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Any`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Any`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Any`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Any`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Any`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Any`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Any`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Any`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Any`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Any`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCountryAnalyticsArrayContainsCondition"></a>

`AdMemberCountryAnalyticsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsContainsCondition"></a>

`AdMemberCountryAnalyticsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsEndswithCondition"></a>

`AdMemberCountryAnalyticsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsEqCondition"></a>

`AdMemberCountryAnalyticsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsFuzzyCondition"></a>

`AdMemberCountryAnalyticsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsGtCondition"></a>

`AdMemberCountryAnalyticsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsGteCondition"></a>

`AdMemberCountryAnalyticsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsInCondition"></a>

`AdMemberCountryAnalyticsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsInFilter`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsInFilter"></a>

`AdMemberCountryAnalyticsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: list[float]`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: list[float]`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: list[float]`
    :   An approximation of unique ad impressions.

    `card_clicks: list[float]`
    :   The number of clicks on interactive card elements.

    `card_impressions: list[float]`
    :   The number of times interactive cards were displayed.

    `clicks: list[float]`
    :   Total number of clicks on the ad.

    `comment_likes: list[float]`
    :   The count of likes on comments related to the ad.

    `comments: list[float]`
    :   The number of comments on the ad.

    `company_page_clicks: list[float]`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: list[float]`
    :   Conversion value in the local currency.

    `cost_in_local_currency: list[float]`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: list[float]`
    :   Cost of ad campaign in USD.

    `document_completions: list[float]`
    :   Number of completions for document views.

    `document_first_quartile_completions: list[float]`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: list[float]`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: list[float]`
    :   Completions for third quartile of document views.

    `download_clicks: list[float]`
    :   Clicks on download links in the ad.

    `end_date: list[str]`
    :   End date of the ad analytics data.

    `external_website_conversions: list[float]`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites.

    `follows: list[float]`
    :   Number of follows generated by the ad.

    `full_screen_plays: list[float]`
    :   Number of times videos were played in fullscreen mode.

    `impressions: list[float]`
    :   Total number of times the ad was displayed.

    `job_applications: list[float]`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: list[float]`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: list[float]`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: list[float]`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: list[float]`
    :   Clicks on expressing interest through lead generation mail.

    `likes: list[float]`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: list[float]`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: list[float]`
    :   Leads generated in one click.

    `opens: list[float]`
    :   The number of times the ad was opened or expanded.

    `other_engagements: list[float]`
    :   Engagements other than clicks on the ad.

    `pivot: list[str]`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[list[typing.Any]]`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: list[float]`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: list[float]`
    :   Registrations completed post-viewing the ad.

    `reactions: list[float]`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: list[float]`
    :   Total registrations completed through the ad.

    `sends: list[float]`
    :   Number of messages sent through the ad.

    `shares: list[float]`
    :   Total shares generated by the ad.

    `sponsored_campaign: list[str]`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: list[str]`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: list[str]`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: list[float]`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: list[float]`
    :   Clicks on text URLs within the ad.

    `total_engagements: list[float]`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: list[float]`
    :   Leads generated through valid work emails.

    `video_completions: list[float]`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: list[float]`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: list[float]`
    :   Completions for midpoint of video views.

    `video_starts: list[float]`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: list[float]`
    :   Completions for third quartile of video views.

    `video_views: list[float]`
    :   Total views of videos in the ad.

    `viral_card_clicks: list[float]`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: list[float]`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: list[float]`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: list[float]`
    :   Likes received on comments in viral distribution.

    `viral_comments: list[float]`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: list[float]`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: list[float]`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: list[float]`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: list[float]`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: list[float]`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: list[float]`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: list[float]`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: list[float]`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: list[float]`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: list[float]`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: list[float]`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: list[float]`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: list[float]`
    :   Clicks on landing page in viral distribution.

    `viral_likes: list[float]`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: list[float]`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: list[float]`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: list[float]`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: list[float]`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: list[float]`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: list[float]`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: list[float]`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: list[float]`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: list[float]`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: list[float]`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: list[float]`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: list[float]`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: list[float]`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: list[float]`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: list[float]`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCountryAnalyticsKeywordCondition"></a>

`AdMemberCountryAnalyticsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsListParams"></a>

`AdMemberCountryAnalyticsListParams(*args, **kwargs)`
:   Parameters for ad_member_country_analytics.list operation

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

<a id="AdMemberCountryAnalyticsLtCondition"></a>

`AdMemberCountryAnalyticsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsLteCondition"></a>

`AdMemberCountryAnalyticsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsNeqCondition"></a>

`AdMemberCountryAnalyticsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsNotCondition"></a>

`AdMemberCountryAnalyticsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsAnyCondition`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsOrCondition"></a>

`AdMemberCountryAnalyticsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsSearchFilter"></a>

`AdMemberCountryAnalyticsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_member_country_analytics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: float | None`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: float | None`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: float | None`
    :   An approximation of unique ad impressions.

    `card_clicks: float | None`
    :   The number of clicks on interactive card elements.

    `card_impressions: float | None`
    :   The number of times interactive cards were displayed.

    `clicks: float | None`
    :   Total number of clicks on the ad.

    `comment_likes: float | None`
    :   The count of likes on comments related to the ad.

    `comments: float | None`
    :   The number of comments on the ad.

    `company_page_clicks: float | None`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: float | None`
    :   Conversion value in the local currency.

    `cost_in_local_currency: float | None`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: float | None`
    :   Cost of ad campaign in USD.

    `document_completions: float | None`
    :   Number of completions for document views.

    `document_first_quartile_completions: float | None`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: float | None`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: float | None`
    :   Completions for third quartile of document views.

    `download_clicks: float | None`
    :   Clicks on download links in the ad.

    `end_date: str | None`
    :   End date of the ad analytics data.

    `external_website_conversions: float | None`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites.

    `follows: float | None`
    :   Number of follows generated by the ad.

    `full_screen_plays: float | None`
    :   Number of times videos were played in fullscreen mode.

    `impressions: float | None`
    :   Total number of times the ad was displayed.

    `job_applications: float | None`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: float | None`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: float | None`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: float | None`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: float | None`
    :   Clicks on expressing interest through lead generation mail.

    `likes: float | None`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: float | None`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: float | None`
    :   Leads generated in one click.

    `opens: float | None`
    :   The number of times the ad was opened or expanded.

    `other_engagements: float | None`
    :   Engagements other than clicks on the ad.

    `pivot: str | None`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[typing.Any] | None`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: float | None`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: float | None`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: float | None`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: float | None`
    :   Registrations completed post-viewing the ad.

    `reactions: float | None`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: float | None`
    :   Total registrations completed through the ad.

    `sends: float | None`
    :   Number of messages sent through the ad.

    `shares: float | None`
    :   Total shares generated by the ad.

    `sponsored_campaign: str | None`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str | None`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str | None`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: float | None`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: float | None`
    :   Clicks on text URLs within the ad.

    `total_engagements: float | None`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: float | None`
    :   Leads generated through valid work emails.

    `video_completions: float | None`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: float | None`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: float | None`
    :   Completions for midpoint of video views.

    `video_starts: float | None`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: float | None`
    :   Completions for third quartile of video views.

    `video_views: float | None`
    :   Total views of videos in the ad.

    `viral_card_clicks: float | None`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: float | None`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: float | None`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: float | None`
    :   Likes received on comments in viral distribution.

    `viral_comments: float | None`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: float | None`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: float | None`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: float | None`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: float | None`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: float | None`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: float | None`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: float | None`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: float | None`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: float | None`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: float | None`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: float | None`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: float | None`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: float | None`
    :   Clicks on landing page in viral distribution.

    `viral_likes: float | None`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: float | None`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: float | None`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: float | None`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: float | None`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: float | None`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: float | None`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: float | None`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: float | None`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: float | None`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: float | None`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: float | None`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: float | None`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: float | None`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: float | None`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: float | None`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: float | None`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: float | None`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCountryAnalyticsSearchQuery"></a>

`AdMemberCountryAnalyticsSearchQuery(*args, **kwargs)`
:   Search query for ad_member_country_analytics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsSortFilter]`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsSortFilter"></a>

`AdMemberCountryAnalyticsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_member_country_analytics search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Literal['asc', 'desc']`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Literal['asc', 'desc']`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Literal['asc', 'desc']`
    :   An approximation of unique ad impressions.

    `card_clicks: Literal['asc', 'desc']`
    :   The number of clicks on interactive card elements.

    `card_impressions: Literal['asc', 'desc']`
    :   The number of times interactive cards were displayed.

    `clicks: Literal['asc', 'desc']`
    :   Total number of clicks on the ad.

    `comment_likes: Literal['asc', 'desc']`
    :   The count of likes on comments related to the ad.

    `comments: Literal['asc', 'desc']`
    :   The number of comments on the ad.

    `company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Literal['asc', 'desc']`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Literal['asc', 'desc']`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Literal['asc', 'desc']`
    :   Cost of ad campaign in USD.

    `document_completions: Literal['asc', 'desc']`
    :   Number of completions for document views.

    `document_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of document views.

    `download_clicks: Literal['asc', 'desc']`
    :   Clicks on download links in the ad.

    `end_date: Literal['asc', 'desc']`
    :   End date of the ad analytics data.

    `external_website_conversions: Literal['asc', 'desc']`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites.

    `follows: Literal['asc', 'desc']`
    :   Number of follows generated by the ad.

    `full_screen_plays: Literal['asc', 'desc']`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Literal['asc', 'desc']`
    :   Total number of times the ad was displayed.

    `job_applications: Literal['asc', 'desc']`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Literal['asc', 'desc']`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Literal['asc', 'desc']`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Literal['asc', 'desc']`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Literal['asc', 'desc']`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click.

    `opens: Literal['asc', 'desc']`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Literal['asc', 'desc']`
    :   Engagements other than clicks on the ad.

    `pivot: Literal['asc', 'desc']`
    :   Pivot dimension used for this analytics record

    `pivot_values: Literal['asc', 'desc']`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing the ad.

    `reactions: Literal['asc', 'desc']`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Literal['asc', 'desc']`
    :   Total registrations completed through the ad.

    `sends: Literal['asc', 'desc']`
    :   Number of messages sent through the ad.

    `shares: Literal['asc', 'desc']`
    :   Total shares generated by the ad.

    `sponsored_campaign: Literal['asc', 'desc']`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Literal['asc', 'desc']`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Literal['asc', 'desc']`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Literal['asc', 'desc']`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Literal['asc', 'desc']`
    :   Clicks on text URLs within the ad.

    `total_engagements: Literal['asc', 'desc']`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Literal['asc', 'desc']`
    :   Leads generated through valid work emails.

    `video_completions: Literal['asc', 'desc']`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of video views.

    `video_starts: Literal['asc', 'desc']`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of video views.

    `video_views: Literal['asc', 'desc']`
    :   Total views of videos in the ad.

    `viral_card_clicks: Literal['asc', 'desc']`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Literal['asc', 'desc']`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Literal['asc', 'desc']`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Literal['asc', 'desc']`
    :   Likes received on comments in viral distribution.

    `viral_comments: Literal['asc', 'desc']`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Literal['asc', 'desc']`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Literal['asc', 'desc']`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Literal['asc', 'desc']`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Literal['asc', 'desc']`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Literal['asc', 'desc']`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Literal['asc', 'desc']`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Literal['asc', 'desc']`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Literal['asc', 'desc']`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Literal['asc', 'desc']`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Literal['asc', 'desc']`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Literal['asc', 'desc']`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Literal['asc', 'desc']`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Literal['asc', 'desc']`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Literal['asc', 'desc']`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Literal['asc', 'desc']`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Literal['asc', 'desc']`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberCountryAnalyticsStartswithCondition"></a>

`AdMemberCountryAnalyticsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberCountryAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsStringFilter"></a>

`AdMemberCountryAnalyticsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: str`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: str`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: str`
    :   An approximation of unique ad impressions.

    `card_clicks: str`
    :   The number of clicks on interactive card elements.

    `card_impressions: str`
    :   The number of times interactive cards were displayed.

    `clicks: str`
    :   Total number of clicks on the ad.

    `comment_likes: str`
    :   The count of likes on comments related to the ad.

    `comments: str`
    :   The number of comments on the ad.

    `company_page_clicks: str`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: str`
    :   Conversion value in the local currency.

    `cost_in_local_currency: str`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: str`
    :   Cost of ad campaign in USD.

    `document_completions: str`
    :   Number of completions for document views.

    `document_first_quartile_completions: str`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: str`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: str`
    :   Completions for third quartile of document views.

    `download_clicks: str`
    :   Clicks on download links in the ad.

    `end_date: str`
    :   End date of the ad analytics data.

    `external_website_conversions: str`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: str`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: str`
    :   Post-view conversions on external websites.

    `follows: str`
    :   Number of follows generated by the ad.

    `full_screen_plays: str`
    :   Number of times videos were played in fullscreen mode.

    `impressions: str`
    :   Total number of times the ad was displayed.

    `job_applications: str`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: str`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: str`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: str`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: str`
    :   Clicks on expressing interest through lead generation mail.

    `likes: str`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: str`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: str`
    :   Leads generated in one click.

    `opens: str`
    :   The number of times the ad was opened or expanded.

    `other_engagements: str`
    :   Engagements other than clicks on the ad.

    `pivot: str`
    :   Pivot dimension used for this analytics record

    `pivot_values: str`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: str`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: str`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: str`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: str`
    :   Registrations completed post-viewing the ad.

    `reactions: str`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: str`
    :   Total registrations completed through the ad.

    `sends: str`
    :   Number of messages sent through the ad.

    `shares: str`
    :   Total shares generated by the ad.

    `sponsored_campaign: str`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: str`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: str`
    :   Clicks on text URLs within the ad.

    `total_engagements: str`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: str`
    :   Leads generated through valid work emails.

    `video_completions: str`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: str`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: str`
    :   Completions for midpoint of video views.

    `video_starts: str`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: str`
    :   Completions for third quartile of video views.

    `video_views: str`
    :   Total views of videos in the ad.

    `viral_card_clicks: str`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: str`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: str`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: str`
    :   Likes received on comments in viral distribution.

    `viral_comments: str`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: str`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: str`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: str`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: str`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: str`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: str`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: str`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: str`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: str`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: str`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: str`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: str`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: str`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: str`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: str`
    :   Clicks on landing page in viral distribution.

    `viral_likes: str`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: str`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: str`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: str`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: str`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: str`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: str`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: str`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: str`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: str`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: str`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: str`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: str`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: str`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: str`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: str`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: str`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: str`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberIndustryAnalyticsAndCondition"></a>

`AdMemberIndustryAnalyticsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsAnyCondition"></a>

`AdMemberIndustryAnalyticsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsAnyValueFilter"></a>

`AdMemberIndustryAnalyticsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Any`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Any`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Any`
    :   An approximation of unique ad impressions.

    `card_clicks: Any`
    :   The number of clicks on interactive card elements.

    `card_impressions: Any`
    :   The number of times interactive cards were displayed.

    `clicks: Any`
    :   Total number of clicks on the ad.

    `comment_likes: Any`
    :   The count of likes on comments related to the ad.

    `comments: Any`
    :   The number of comments on the ad.

    `company_page_clicks: Any`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Any`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Any`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Any`
    :   Cost of ad campaign in USD.

    `document_completions: Any`
    :   Number of completions for document views.

    `document_first_quartile_completions: Any`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Any`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Any`
    :   Completions for third quartile of document views.

    `download_clicks: Any`
    :   Clicks on download links in the ad.

    `end_date: Any`
    :   End date of the ad analytics data.

    `external_website_conversions: Any`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites.

    `follows: Any`
    :   Number of follows generated by the ad.

    `full_screen_plays: Any`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Any`
    :   Total number of times the ad was displayed.

    `job_applications: Any`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Any`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Any`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Any`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Any`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Any`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Any`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Any`
    :   Leads generated in one click.

    `opens: Any`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Any`
    :   Engagements other than clicks on the ad.

    `pivot: Any`
    :   Pivot dimension used for this analytics record

    `pivot_values: Any`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Any`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Any`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Any`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Any`
    :   Registrations completed post-viewing the ad.

    `reactions: Any`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Any`
    :   Total registrations completed through the ad.

    `sends: Any`
    :   Number of messages sent through the ad.

    `shares: Any`
    :   Total shares generated by the ad.

    `sponsored_campaign: Any`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Any`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Any`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Any`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Any`
    :   Clicks on text URLs within the ad.

    `total_engagements: Any`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Any`
    :   Leads generated through valid work emails.

    `video_completions: Any`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Any`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Any`
    :   Completions for midpoint of video views.

    `video_starts: Any`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Any`
    :   Completions for third quartile of video views.

    `video_views: Any`
    :   Total views of videos in the ad.

    `viral_card_clicks: Any`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Any`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Any`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Any`
    :   Likes received on comments in viral distribution.

    `viral_comments: Any`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Any`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Any`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Any`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Any`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Any`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Any`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Any`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Any`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Any`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Any`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Any`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Any`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Any`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Any`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Any`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Any`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Any`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Any`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Any`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Any`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Any`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Any`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Any`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Any`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Any`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Any`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Any`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Any`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Any`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Any`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Any`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberIndustryAnalyticsArrayContainsCondition"></a>

`AdMemberIndustryAnalyticsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsContainsCondition"></a>

`AdMemberIndustryAnalyticsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsEndswithCondition"></a>

`AdMemberIndustryAnalyticsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsEqCondition"></a>

`AdMemberIndustryAnalyticsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsFuzzyCondition"></a>

`AdMemberIndustryAnalyticsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsGtCondition"></a>

`AdMemberIndustryAnalyticsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsGteCondition"></a>

`AdMemberIndustryAnalyticsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsInCondition"></a>

`AdMemberIndustryAnalyticsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsInFilter`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsInFilter"></a>

`AdMemberIndustryAnalyticsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: list[float]`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: list[float]`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: list[float]`
    :   An approximation of unique ad impressions.

    `card_clicks: list[float]`
    :   The number of clicks on interactive card elements.

    `card_impressions: list[float]`
    :   The number of times interactive cards were displayed.

    `clicks: list[float]`
    :   Total number of clicks on the ad.

    `comment_likes: list[float]`
    :   The count of likes on comments related to the ad.

    `comments: list[float]`
    :   The number of comments on the ad.

    `company_page_clicks: list[float]`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: list[float]`
    :   Conversion value in the local currency.

    `cost_in_local_currency: list[float]`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: list[float]`
    :   Cost of ad campaign in USD.

    `document_completions: list[float]`
    :   Number of completions for document views.

    `document_first_quartile_completions: list[float]`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: list[float]`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: list[float]`
    :   Completions for third quartile of document views.

    `download_clicks: list[float]`
    :   Clicks on download links in the ad.

    `end_date: list[str]`
    :   End date of the ad analytics data.

    `external_website_conversions: list[float]`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites.

    `follows: list[float]`
    :   Number of follows generated by the ad.

    `full_screen_plays: list[float]`
    :   Number of times videos were played in fullscreen mode.

    `impressions: list[float]`
    :   Total number of times the ad was displayed.

    `job_applications: list[float]`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: list[float]`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: list[float]`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: list[float]`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: list[float]`
    :   Clicks on expressing interest through lead generation mail.

    `likes: list[float]`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: list[float]`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: list[float]`
    :   Leads generated in one click.

    `opens: list[float]`
    :   The number of times the ad was opened or expanded.

    `other_engagements: list[float]`
    :   Engagements other than clicks on the ad.

    `pivot: list[str]`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[list[typing.Any]]`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: list[float]`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: list[float]`
    :   Registrations completed post-viewing the ad.

    `reactions: list[float]`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: list[float]`
    :   Total registrations completed through the ad.

    `sends: list[float]`
    :   Number of messages sent through the ad.

    `shares: list[float]`
    :   Total shares generated by the ad.

    `sponsored_campaign: list[str]`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: list[str]`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: list[str]`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: list[float]`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: list[float]`
    :   Clicks on text URLs within the ad.

    `total_engagements: list[float]`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: list[float]`
    :   Leads generated through valid work emails.

    `video_completions: list[float]`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: list[float]`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: list[float]`
    :   Completions for midpoint of video views.

    `video_starts: list[float]`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: list[float]`
    :   Completions for third quartile of video views.

    `video_views: list[float]`
    :   Total views of videos in the ad.

    `viral_card_clicks: list[float]`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: list[float]`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: list[float]`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: list[float]`
    :   Likes received on comments in viral distribution.

    `viral_comments: list[float]`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: list[float]`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: list[float]`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: list[float]`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: list[float]`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: list[float]`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: list[float]`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: list[float]`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: list[float]`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: list[float]`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: list[float]`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: list[float]`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: list[float]`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: list[float]`
    :   Clicks on landing page in viral distribution.

    `viral_likes: list[float]`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: list[float]`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: list[float]`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: list[float]`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: list[float]`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: list[float]`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: list[float]`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: list[float]`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: list[float]`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: list[float]`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: list[float]`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: list[float]`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: list[float]`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: list[float]`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: list[float]`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: list[float]`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberIndustryAnalyticsKeywordCondition"></a>

`AdMemberIndustryAnalyticsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsListParams"></a>

`AdMemberIndustryAnalyticsListParams(*args, **kwargs)`
:   Parameters for ad_member_industry_analytics.list operation

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

<a id="AdMemberIndustryAnalyticsLtCondition"></a>

`AdMemberIndustryAnalyticsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsLteCondition"></a>

`AdMemberIndustryAnalyticsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsNeqCondition"></a>

`AdMemberIndustryAnalyticsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsNotCondition"></a>

`AdMemberIndustryAnalyticsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsAnyCondition`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsOrCondition"></a>

`AdMemberIndustryAnalyticsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsSearchFilter"></a>

`AdMemberIndustryAnalyticsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_member_industry_analytics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: float | None`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: float | None`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: float | None`
    :   An approximation of unique ad impressions.

    `card_clicks: float | None`
    :   The number of clicks on interactive card elements.

    `card_impressions: float | None`
    :   The number of times interactive cards were displayed.

    `clicks: float | None`
    :   Total number of clicks on the ad.

    `comment_likes: float | None`
    :   The count of likes on comments related to the ad.

    `comments: float | None`
    :   The number of comments on the ad.

    `company_page_clicks: float | None`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: float | None`
    :   Conversion value in the local currency.

    `cost_in_local_currency: float | None`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: float | None`
    :   Cost of ad campaign in USD.

    `document_completions: float | None`
    :   Number of completions for document views.

    `document_first_quartile_completions: float | None`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: float | None`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: float | None`
    :   Completions for third quartile of document views.

    `download_clicks: float | None`
    :   Clicks on download links in the ad.

    `end_date: str | None`
    :   End date of the ad analytics data.

    `external_website_conversions: float | None`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites.

    `follows: float | None`
    :   Number of follows generated by the ad.

    `full_screen_plays: float | None`
    :   Number of times videos were played in fullscreen mode.

    `impressions: float | None`
    :   Total number of times the ad was displayed.

    `job_applications: float | None`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: float | None`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: float | None`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: float | None`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: float | None`
    :   Clicks on expressing interest through lead generation mail.

    `likes: float | None`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: float | None`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: float | None`
    :   Leads generated in one click.

    `opens: float | None`
    :   The number of times the ad was opened or expanded.

    `other_engagements: float | None`
    :   Engagements other than clicks on the ad.

    `pivot: str | None`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[typing.Any] | None`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: float | None`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: float | None`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: float | None`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: float | None`
    :   Registrations completed post-viewing the ad.

    `reactions: float | None`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: float | None`
    :   Total registrations completed through the ad.

    `sends: float | None`
    :   Number of messages sent through the ad.

    `shares: float | None`
    :   Total shares generated by the ad.

    `sponsored_campaign: str | None`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str | None`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str | None`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: float | None`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: float | None`
    :   Clicks on text URLs within the ad.

    `total_engagements: float | None`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: float | None`
    :   Leads generated through valid work emails.

    `video_completions: float | None`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: float | None`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: float | None`
    :   Completions for midpoint of video views.

    `video_starts: float | None`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: float | None`
    :   Completions for third quartile of video views.

    `video_views: float | None`
    :   Total views of videos in the ad.

    `viral_card_clicks: float | None`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: float | None`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: float | None`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: float | None`
    :   Likes received on comments in viral distribution.

    `viral_comments: float | None`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: float | None`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: float | None`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: float | None`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: float | None`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: float | None`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: float | None`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: float | None`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: float | None`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: float | None`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: float | None`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: float | None`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: float | None`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: float | None`
    :   Clicks on landing page in viral distribution.

    `viral_likes: float | None`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: float | None`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: float | None`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: float | None`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: float | None`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: float | None`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: float | None`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: float | None`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: float | None`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: float | None`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: float | None`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: float | None`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: float | None`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: float | None`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: float | None`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: float | None`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: float | None`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: float | None`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberIndustryAnalyticsSearchQuery"></a>

`AdMemberIndustryAnalyticsSearchQuery(*args, **kwargs)`
:   Search query for ad_member_industry_analytics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsSortFilter]`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsSortFilter"></a>

`AdMemberIndustryAnalyticsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_member_industry_analytics search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Literal['asc', 'desc']`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Literal['asc', 'desc']`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Literal['asc', 'desc']`
    :   An approximation of unique ad impressions.

    `card_clicks: Literal['asc', 'desc']`
    :   The number of clicks on interactive card elements.

    `card_impressions: Literal['asc', 'desc']`
    :   The number of times interactive cards were displayed.

    `clicks: Literal['asc', 'desc']`
    :   Total number of clicks on the ad.

    `comment_likes: Literal['asc', 'desc']`
    :   The count of likes on comments related to the ad.

    `comments: Literal['asc', 'desc']`
    :   The number of comments on the ad.

    `company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Literal['asc', 'desc']`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Literal['asc', 'desc']`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Literal['asc', 'desc']`
    :   Cost of ad campaign in USD.

    `document_completions: Literal['asc', 'desc']`
    :   Number of completions for document views.

    `document_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of document views.

    `download_clicks: Literal['asc', 'desc']`
    :   Clicks on download links in the ad.

    `end_date: Literal['asc', 'desc']`
    :   End date of the ad analytics data.

    `external_website_conversions: Literal['asc', 'desc']`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites.

    `follows: Literal['asc', 'desc']`
    :   Number of follows generated by the ad.

    `full_screen_plays: Literal['asc', 'desc']`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Literal['asc', 'desc']`
    :   Total number of times the ad was displayed.

    `job_applications: Literal['asc', 'desc']`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Literal['asc', 'desc']`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Literal['asc', 'desc']`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Literal['asc', 'desc']`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Literal['asc', 'desc']`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click.

    `opens: Literal['asc', 'desc']`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Literal['asc', 'desc']`
    :   Engagements other than clicks on the ad.

    `pivot: Literal['asc', 'desc']`
    :   Pivot dimension used for this analytics record

    `pivot_values: Literal['asc', 'desc']`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing the ad.

    `reactions: Literal['asc', 'desc']`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Literal['asc', 'desc']`
    :   Total registrations completed through the ad.

    `sends: Literal['asc', 'desc']`
    :   Number of messages sent through the ad.

    `shares: Literal['asc', 'desc']`
    :   Total shares generated by the ad.

    `sponsored_campaign: Literal['asc', 'desc']`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Literal['asc', 'desc']`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Literal['asc', 'desc']`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Literal['asc', 'desc']`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Literal['asc', 'desc']`
    :   Clicks on text URLs within the ad.

    `total_engagements: Literal['asc', 'desc']`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Literal['asc', 'desc']`
    :   Leads generated through valid work emails.

    `video_completions: Literal['asc', 'desc']`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of video views.

    `video_starts: Literal['asc', 'desc']`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of video views.

    `video_views: Literal['asc', 'desc']`
    :   Total views of videos in the ad.

    `viral_card_clicks: Literal['asc', 'desc']`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Literal['asc', 'desc']`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Literal['asc', 'desc']`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Literal['asc', 'desc']`
    :   Likes received on comments in viral distribution.

    `viral_comments: Literal['asc', 'desc']`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Literal['asc', 'desc']`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Literal['asc', 'desc']`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Literal['asc', 'desc']`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Literal['asc', 'desc']`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Literal['asc', 'desc']`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Literal['asc', 'desc']`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Literal['asc', 'desc']`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Literal['asc', 'desc']`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Literal['asc', 'desc']`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Literal['asc', 'desc']`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Literal['asc', 'desc']`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Literal['asc', 'desc']`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Literal['asc', 'desc']`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Literal['asc', 'desc']`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Literal['asc', 'desc']`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Literal['asc', 'desc']`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberIndustryAnalyticsStartswithCondition"></a>

`AdMemberIndustryAnalyticsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberIndustryAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsStringFilter"></a>

`AdMemberIndustryAnalyticsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: str`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: str`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: str`
    :   An approximation of unique ad impressions.

    `card_clicks: str`
    :   The number of clicks on interactive card elements.

    `card_impressions: str`
    :   The number of times interactive cards were displayed.

    `clicks: str`
    :   Total number of clicks on the ad.

    `comment_likes: str`
    :   The count of likes on comments related to the ad.

    `comments: str`
    :   The number of comments on the ad.

    `company_page_clicks: str`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: str`
    :   Conversion value in the local currency.

    `cost_in_local_currency: str`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: str`
    :   Cost of ad campaign in USD.

    `document_completions: str`
    :   Number of completions for document views.

    `document_first_quartile_completions: str`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: str`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: str`
    :   Completions for third quartile of document views.

    `download_clicks: str`
    :   Clicks on download links in the ad.

    `end_date: str`
    :   End date of the ad analytics data.

    `external_website_conversions: str`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: str`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: str`
    :   Post-view conversions on external websites.

    `follows: str`
    :   Number of follows generated by the ad.

    `full_screen_plays: str`
    :   Number of times videos were played in fullscreen mode.

    `impressions: str`
    :   Total number of times the ad was displayed.

    `job_applications: str`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: str`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: str`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: str`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: str`
    :   Clicks on expressing interest through lead generation mail.

    `likes: str`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: str`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: str`
    :   Leads generated in one click.

    `opens: str`
    :   The number of times the ad was opened or expanded.

    `other_engagements: str`
    :   Engagements other than clicks on the ad.

    `pivot: str`
    :   Pivot dimension used for this analytics record

    `pivot_values: str`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: str`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: str`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: str`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: str`
    :   Registrations completed post-viewing the ad.

    `reactions: str`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: str`
    :   Total registrations completed through the ad.

    `sends: str`
    :   Number of messages sent through the ad.

    `shares: str`
    :   Total shares generated by the ad.

    `sponsored_campaign: str`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: str`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: str`
    :   Clicks on text URLs within the ad.

    `total_engagements: str`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: str`
    :   Leads generated through valid work emails.

    `video_completions: str`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: str`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: str`
    :   Completions for midpoint of video views.

    `video_starts: str`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: str`
    :   Completions for third quartile of video views.

    `video_views: str`
    :   Total views of videos in the ad.

    `viral_card_clicks: str`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: str`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: str`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: str`
    :   Likes received on comments in viral distribution.

    `viral_comments: str`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: str`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: str`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: str`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: str`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: str`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: str`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: str`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: str`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: str`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: str`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: str`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: str`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: str`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: str`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: str`
    :   Clicks on landing page in viral distribution.

    `viral_likes: str`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: str`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: str`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: str`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: str`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: str`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: str`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: str`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: str`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: str`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: str`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: str`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: str`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: str`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: str`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: str`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: str`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: str`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberJobFunctionAnalyticsAndCondition"></a>

`AdMemberJobFunctionAnalyticsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsAnyCondition"></a>

`AdMemberJobFunctionAnalyticsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsAnyValueFilter"></a>

`AdMemberJobFunctionAnalyticsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Any`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Any`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Any`
    :   An approximation of unique ad impressions.

    `card_clicks: Any`
    :   The number of clicks on interactive card elements.

    `card_impressions: Any`
    :   The number of times interactive cards were displayed.

    `clicks: Any`
    :   Total number of clicks on the ad.

    `comment_likes: Any`
    :   The count of likes on comments related to the ad.

    `comments: Any`
    :   The number of comments on the ad.

    `company_page_clicks: Any`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Any`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Any`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Any`
    :   Cost of ad campaign in USD.

    `document_completions: Any`
    :   Number of completions for document views.

    `document_first_quartile_completions: Any`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Any`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Any`
    :   Completions for third quartile of document views.

    `download_clicks: Any`
    :   Clicks on download links in the ad.

    `end_date: Any`
    :   End date of the ad analytics data.

    `external_website_conversions: Any`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites.

    `follows: Any`
    :   Number of follows generated by the ad.

    `full_screen_plays: Any`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Any`
    :   Total number of times the ad was displayed.

    `job_applications: Any`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Any`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Any`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Any`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Any`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Any`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Any`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Any`
    :   Leads generated in one click.

    `opens: Any`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Any`
    :   Engagements other than clicks on the ad.

    `pivot: Any`
    :   Pivot dimension used for this analytics record

    `pivot_values: Any`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Any`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Any`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Any`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Any`
    :   Registrations completed post-viewing the ad.

    `reactions: Any`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Any`
    :   Total registrations completed through the ad.

    `sends: Any`
    :   Number of messages sent through the ad.

    `shares: Any`
    :   Total shares generated by the ad.

    `sponsored_campaign: Any`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Any`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Any`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Any`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Any`
    :   Clicks on text URLs within the ad.

    `total_engagements: Any`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Any`
    :   Leads generated through valid work emails.

    `video_completions: Any`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Any`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Any`
    :   Completions for midpoint of video views.

    `video_starts: Any`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Any`
    :   Completions for third quartile of video views.

    `video_views: Any`
    :   Total views of videos in the ad.

    `viral_card_clicks: Any`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Any`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Any`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Any`
    :   Likes received on comments in viral distribution.

    `viral_comments: Any`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Any`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Any`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Any`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Any`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Any`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Any`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Any`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Any`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Any`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Any`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Any`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Any`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Any`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Any`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Any`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Any`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Any`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Any`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Any`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Any`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Any`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Any`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Any`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Any`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Any`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Any`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Any`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Any`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Any`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Any`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Any`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberJobFunctionAnalyticsArrayContainsCondition"></a>

`AdMemberJobFunctionAnalyticsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsContainsCondition"></a>

`AdMemberJobFunctionAnalyticsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsEndswithCondition"></a>

`AdMemberJobFunctionAnalyticsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsEqCondition"></a>

`AdMemberJobFunctionAnalyticsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsFuzzyCondition"></a>

`AdMemberJobFunctionAnalyticsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsGtCondition"></a>

`AdMemberJobFunctionAnalyticsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsGteCondition"></a>

`AdMemberJobFunctionAnalyticsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsInCondition"></a>

`AdMemberJobFunctionAnalyticsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsInFilter`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsInFilter"></a>

`AdMemberJobFunctionAnalyticsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: list[float]`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: list[float]`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: list[float]`
    :   An approximation of unique ad impressions.

    `card_clicks: list[float]`
    :   The number of clicks on interactive card elements.

    `card_impressions: list[float]`
    :   The number of times interactive cards were displayed.

    `clicks: list[float]`
    :   Total number of clicks on the ad.

    `comment_likes: list[float]`
    :   The count of likes on comments related to the ad.

    `comments: list[float]`
    :   The number of comments on the ad.

    `company_page_clicks: list[float]`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: list[float]`
    :   Conversion value in the local currency.

    `cost_in_local_currency: list[float]`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: list[float]`
    :   Cost of ad campaign in USD.

    `document_completions: list[float]`
    :   Number of completions for document views.

    `document_first_quartile_completions: list[float]`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: list[float]`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: list[float]`
    :   Completions for third quartile of document views.

    `download_clicks: list[float]`
    :   Clicks on download links in the ad.

    `end_date: list[str]`
    :   End date of the ad analytics data.

    `external_website_conversions: list[float]`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites.

    `follows: list[float]`
    :   Number of follows generated by the ad.

    `full_screen_plays: list[float]`
    :   Number of times videos were played in fullscreen mode.

    `impressions: list[float]`
    :   Total number of times the ad was displayed.

    `job_applications: list[float]`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: list[float]`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: list[float]`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: list[float]`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: list[float]`
    :   Clicks on expressing interest through lead generation mail.

    `likes: list[float]`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: list[float]`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: list[float]`
    :   Leads generated in one click.

    `opens: list[float]`
    :   The number of times the ad was opened or expanded.

    `other_engagements: list[float]`
    :   Engagements other than clicks on the ad.

    `pivot: list[str]`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[list[typing.Any]]`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: list[float]`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: list[float]`
    :   Registrations completed post-viewing the ad.

    `reactions: list[float]`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: list[float]`
    :   Total registrations completed through the ad.

    `sends: list[float]`
    :   Number of messages sent through the ad.

    `shares: list[float]`
    :   Total shares generated by the ad.

    `sponsored_campaign: list[str]`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: list[str]`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: list[str]`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: list[float]`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: list[float]`
    :   Clicks on text URLs within the ad.

    `total_engagements: list[float]`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: list[float]`
    :   Leads generated through valid work emails.

    `video_completions: list[float]`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: list[float]`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: list[float]`
    :   Completions for midpoint of video views.

    `video_starts: list[float]`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: list[float]`
    :   Completions for third quartile of video views.

    `video_views: list[float]`
    :   Total views of videos in the ad.

    `viral_card_clicks: list[float]`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: list[float]`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: list[float]`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: list[float]`
    :   Likes received on comments in viral distribution.

    `viral_comments: list[float]`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: list[float]`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: list[float]`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: list[float]`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: list[float]`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: list[float]`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: list[float]`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: list[float]`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: list[float]`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: list[float]`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: list[float]`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: list[float]`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: list[float]`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: list[float]`
    :   Clicks on landing page in viral distribution.

    `viral_likes: list[float]`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: list[float]`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: list[float]`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: list[float]`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: list[float]`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: list[float]`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: list[float]`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: list[float]`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: list[float]`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: list[float]`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: list[float]`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: list[float]`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: list[float]`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: list[float]`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: list[float]`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: list[float]`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberJobFunctionAnalyticsKeywordCondition"></a>

`AdMemberJobFunctionAnalyticsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsListParams"></a>

`AdMemberJobFunctionAnalyticsListParams(*args, **kwargs)`
:   Parameters for ad_member_job_function_analytics.list operation

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

<a id="AdMemberJobFunctionAnalyticsLtCondition"></a>

`AdMemberJobFunctionAnalyticsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsLteCondition"></a>

`AdMemberJobFunctionAnalyticsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsNeqCondition"></a>

`AdMemberJobFunctionAnalyticsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsNotCondition"></a>

`AdMemberJobFunctionAnalyticsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsAnyCondition`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsOrCondition"></a>

`AdMemberJobFunctionAnalyticsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsSearchFilter"></a>

`AdMemberJobFunctionAnalyticsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_member_job_function_analytics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: float | None`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: float | None`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: float | None`
    :   An approximation of unique ad impressions.

    `card_clicks: float | None`
    :   The number of clicks on interactive card elements.

    `card_impressions: float | None`
    :   The number of times interactive cards were displayed.

    `clicks: float | None`
    :   Total number of clicks on the ad.

    `comment_likes: float | None`
    :   The count of likes on comments related to the ad.

    `comments: float | None`
    :   The number of comments on the ad.

    `company_page_clicks: float | None`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: float | None`
    :   Conversion value in the local currency.

    `cost_in_local_currency: float | None`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: float | None`
    :   Cost of ad campaign in USD.

    `document_completions: float | None`
    :   Number of completions for document views.

    `document_first_quartile_completions: float | None`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: float | None`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: float | None`
    :   Completions for third quartile of document views.

    `download_clicks: float | None`
    :   Clicks on download links in the ad.

    `end_date: str | None`
    :   End date of the ad analytics data.

    `external_website_conversions: float | None`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites.

    `follows: float | None`
    :   Number of follows generated by the ad.

    `full_screen_plays: float | None`
    :   Number of times videos were played in fullscreen mode.

    `impressions: float | None`
    :   Total number of times the ad was displayed.

    `job_applications: float | None`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: float | None`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: float | None`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: float | None`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: float | None`
    :   Clicks on expressing interest through lead generation mail.

    `likes: float | None`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: float | None`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: float | None`
    :   Leads generated in one click.

    `opens: float | None`
    :   The number of times the ad was opened or expanded.

    `other_engagements: float | None`
    :   Engagements other than clicks on the ad.

    `pivot: str | None`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[typing.Any] | None`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: float | None`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: float | None`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: float | None`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: float | None`
    :   Registrations completed post-viewing the ad.

    `reactions: float | None`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: float | None`
    :   Total registrations completed through the ad.

    `sends: float | None`
    :   Number of messages sent through the ad.

    `shares: float | None`
    :   Total shares generated by the ad.

    `sponsored_campaign: str | None`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str | None`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str | None`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: float | None`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: float | None`
    :   Clicks on text URLs within the ad.

    `total_engagements: float | None`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: float | None`
    :   Leads generated through valid work emails.

    `video_completions: float | None`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: float | None`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: float | None`
    :   Completions for midpoint of video views.

    `video_starts: float | None`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: float | None`
    :   Completions for third quartile of video views.

    `video_views: float | None`
    :   Total views of videos in the ad.

    `viral_card_clicks: float | None`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: float | None`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: float | None`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: float | None`
    :   Likes received on comments in viral distribution.

    `viral_comments: float | None`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: float | None`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: float | None`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: float | None`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: float | None`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: float | None`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: float | None`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: float | None`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: float | None`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: float | None`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: float | None`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: float | None`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: float | None`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: float | None`
    :   Clicks on landing page in viral distribution.

    `viral_likes: float | None`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: float | None`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: float | None`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: float | None`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: float | None`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: float | None`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: float | None`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: float | None`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: float | None`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: float | None`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: float | None`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: float | None`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: float | None`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: float | None`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: float | None`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: float | None`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: float | None`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: float | None`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberJobFunctionAnalyticsSearchQuery"></a>

`AdMemberJobFunctionAnalyticsSearchQuery(*args, **kwargs)`
:   Search query for ad_member_job_function_analytics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsSortFilter]`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsSortFilter"></a>

`AdMemberJobFunctionAnalyticsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_member_job_function_analytics search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Literal['asc', 'desc']`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Literal['asc', 'desc']`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Literal['asc', 'desc']`
    :   An approximation of unique ad impressions.

    `card_clicks: Literal['asc', 'desc']`
    :   The number of clicks on interactive card elements.

    `card_impressions: Literal['asc', 'desc']`
    :   The number of times interactive cards were displayed.

    `clicks: Literal['asc', 'desc']`
    :   Total number of clicks on the ad.

    `comment_likes: Literal['asc', 'desc']`
    :   The count of likes on comments related to the ad.

    `comments: Literal['asc', 'desc']`
    :   The number of comments on the ad.

    `company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Literal['asc', 'desc']`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Literal['asc', 'desc']`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Literal['asc', 'desc']`
    :   Cost of ad campaign in USD.

    `document_completions: Literal['asc', 'desc']`
    :   Number of completions for document views.

    `document_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of document views.

    `download_clicks: Literal['asc', 'desc']`
    :   Clicks on download links in the ad.

    `end_date: Literal['asc', 'desc']`
    :   End date of the ad analytics data.

    `external_website_conversions: Literal['asc', 'desc']`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites.

    `follows: Literal['asc', 'desc']`
    :   Number of follows generated by the ad.

    `full_screen_plays: Literal['asc', 'desc']`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Literal['asc', 'desc']`
    :   Total number of times the ad was displayed.

    `job_applications: Literal['asc', 'desc']`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Literal['asc', 'desc']`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Literal['asc', 'desc']`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Literal['asc', 'desc']`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Literal['asc', 'desc']`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click.

    `opens: Literal['asc', 'desc']`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Literal['asc', 'desc']`
    :   Engagements other than clicks on the ad.

    `pivot: Literal['asc', 'desc']`
    :   Pivot dimension used for this analytics record

    `pivot_values: Literal['asc', 'desc']`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing the ad.

    `reactions: Literal['asc', 'desc']`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Literal['asc', 'desc']`
    :   Total registrations completed through the ad.

    `sends: Literal['asc', 'desc']`
    :   Number of messages sent through the ad.

    `shares: Literal['asc', 'desc']`
    :   Total shares generated by the ad.

    `sponsored_campaign: Literal['asc', 'desc']`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Literal['asc', 'desc']`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Literal['asc', 'desc']`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Literal['asc', 'desc']`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Literal['asc', 'desc']`
    :   Clicks on text URLs within the ad.

    `total_engagements: Literal['asc', 'desc']`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Literal['asc', 'desc']`
    :   Leads generated through valid work emails.

    `video_completions: Literal['asc', 'desc']`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of video views.

    `video_starts: Literal['asc', 'desc']`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of video views.

    `video_views: Literal['asc', 'desc']`
    :   Total views of videos in the ad.

    `viral_card_clicks: Literal['asc', 'desc']`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Literal['asc', 'desc']`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Literal['asc', 'desc']`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Literal['asc', 'desc']`
    :   Likes received on comments in viral distribution.

    `viral_comments: Literal['asc', 'desc']`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Literal['asc', 'desc']`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Literal['asc', 'desc']`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Literal['asc', 'desc']`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Literal['asc', 'desc']`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Literal['asc', 'desc']`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Literal['asc', 'desc']`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Literal['asc', 'desc']`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Literal['asc', 'desc']`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Literal['asc', 'desc']`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Literal['asc', 'desc']`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Literal['asc', 'desc']`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Literal['asc', 'desc']`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Literal['asc', 'desc']`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Literal['asc', 'desc']`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Literal['asc', 'desc']`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Literal['asc', 'desc']`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberJobFunctionAnalyticsStartswithCondition"></a>

`AdMemberJobFunctionAnalyticsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobFunctionAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsStringFilter"></a>

`AdMemberJobFunctionAnalyticsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: str`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: str`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: str`
    :   An approximation of unique ad impressions.

    `card_clicks: str`
    :   The number of clicks on interactive card elements.

    `card_impressions: str`
    :   The number of times interactive cards were displayed.

    `clicks: str`
    :   Total number of clicks on the ad.

    `comment_likes: str`
    :   The count of likes on comments related to the ad.

    `comments: str`
    :   The number of comments on the ad.

    `company_page_clicks: str`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: str`
    :   Conversion value in the local currency.

    `cost_in_local_currency: str`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: str`
    :   Cost of ad campaign in USD.

    `document_completions: str`
    :   Number of completions for document views.

    `document_first_quartile_completions: str`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: str`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: str`
    :   Completions for third quartile of document views.

    `download_clicks: str`
    :   Clicks on download links in the ad.

    `end_date: str`
    :   End date of the ad analytics data.

    `external_website_conversions: str`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: str`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: str`
    :   Post-view conversions on external websites.

    `follows: str`
    :   Number of follows generated by the ad.

    `full_screen_plays: str`
    :   Number of times videos were played in fullscreen mode.

    `impressions: str`
    :   Total number of times the ad was displayed.

    `job_applications: str`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: str`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: str`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: str`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: str`
    :   Clicks on expressing interest through lead generation mail.

    `likes: str`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: str`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: str`
    :   Leads generated in one click.

    `opens: str`
    :   The number of times the ad was opened or expanded.

    `other_engagements: str`
    :   Engagements other than clicks on the ad.

    `pivot: str`
    :   Pivot dimension used for this analytics record

    `pivot_values: str`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: str`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: str`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: str`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: str`
    :   Registrations completed post-viewing the ad.

    `reactions: str`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: str`
    :   Total registrations completed through the ad.

    `sends: str`
    :   Number of messages sent through the ad.

    `shares: str`
    :   Total shares generated by the ad.

    `sponsored_campaign: str`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: str`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: str`
    :   Clicks on text URLs within the ad.

    `total_engagements: str`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: str`
    :   Leads generated through valid work emails.

    `video_completions: str`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: str`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: str`
    :   Completions for midpoint of video views.

    `video_starts: str`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: str`
    :   Completions for third quartile of video views.

    `video_views: str`
    :   Total views of videos in the ad.

    `viral_card_clicks: str`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: str`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: str`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: str`
    :   Likes received on comments in viral distribution.

    `viral_comments: str`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: str`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: str`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: str`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: str`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: str`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: str`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: str`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: str`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: str`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: str`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: str`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: str`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: str`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: str`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: str`
    :   Clicks on landing page in viral distribution.

    `viral_likes: str`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: str`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: str`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: str`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: str`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: str`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: str`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: str`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: str`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: str`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: str`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: str`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: str`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: str`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: str`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: str`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: str`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: str`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberJobTitleAnalyticsAndCondition"></a>

`AdMemberJobTitleAnalyticsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsAnyCondition"></a>

`AdMemberJobTitleAnalyticsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsAnyValueFilter"></a>

`AdMemberJobTitleAnalyticsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Any`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Any`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Any`
    :   An approximation of unique ad impressions.

    `card_clicks: Any`
    :   The number of clicks on interactive card elements.

    `card_impressions: Any`
    :   The number of times interactive cards were displayed.

    `clicks: Any`
    :   Total number of clicks on the ad.

    `comment_likes: Any`
    :   The count of likes on comments related to the ad.

    `comments: Any`
    :   The number of comments on the ad.

    `company_page_clicks: Any`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Any`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Any`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Any`
    :   Cost of ad campaign in USD.

    `document_completions: Any`
    :   Number of completions for document views.

    `document_first_quartile_completions: Any`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Any`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Any`
    :   Completions for third quartile of document views.

    `download_clicks: Any`
    :   Clicks on download links in the ad.

    `end_date: Any`
    :   End date of the ad analytics data.

    `external_website_conversions: Any`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites.

    `follows: Any`
    :   Number of follows generated by the ad.

    `full_screen_plays: Any`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Any`
    :   Total number of times the ad was displayed.

    `job_applications: Any`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Any`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Any`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Any`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Any`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Any`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Any`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Any`
    :   Leads generated in one click.

    `opens: Any`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Any`
    :   Engagements other than clicks on the ad.

    `pivot: Any`
    :   Pivot dimension used for this analytics record

    `pivot_values: Any`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Any`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Any`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Any`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Any`
    :   Registrations completed post-viewing the ad.

    `reactions: Any`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Any`
    :   Total registrations completed through the ad.

    `sends: Any`
    :   Number of messages sent through the ad.

    `shares: Any`
    :   Total shares generated by the ad.

    `sponsored_campaign: Any`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Any`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Any`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Any`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Any`
    :   Clicks on text URLs within the ad.

    `total_engagements: Any`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Any`
    :   Leads generated through valid work emails.

    `video_completions: Any`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Any`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Any`
    :   Completions for midpoint of video views.

    `video_starts: Any`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Any`
    :   Completions for third quartile of video views.

    `video_views: Any`
    :   Total views of videos in the ad.

    `viral_card_clicks: Any`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Any`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Any`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Any`
    :   Likes received on comments in viral distribution.

    `viral_comments: Any`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Any`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Any`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Any`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Any`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Any`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Any`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Any`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Any`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Any`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Any`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Any`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Any`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Any`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Any`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Any`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Any`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Any`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Any`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Any`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Any`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Any`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Any`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Any`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Any`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Any`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Any`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Any`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Any`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Any`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Any`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Any`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberJobTitleAnalyticsArrayContainsCondition"></a>

`AdMemberJobTitleAnalyticsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsContainsCondition"></a>

`AdMemberJobTitleAnalyticsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsEndswithCondition"></a>

`AdMemberJobTitleAnalyticsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsEqCondition"></a>

`AdMemberJobTitleAnalyticsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsFuzzyCondition"></a>

`AdMemberJobTitleAnalyticsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsGtCondition"></a>

`AdMemberJobTitleAnalyticsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsGteCondition"></a>

`AdMemberJobTitleAnalyticsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsInCondition"></a>

`AdMemberJobTitleAnalyticsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsInFilter`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsInFilter"></a>

`AdMemberJobTitleAnalyticsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: list[float]`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: list[float]`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: list[float]`
    :   An approximation of unique ad impressions.

    `card_clicks: list[float]`
    :   The number of clicks on interactive card elements.

    `card_impressions: list[float]`
    :   The number of times interactive cards were displayed.

    `clicks: list[float]`
    :   Total number of clicks on the ad.

    `comment_likes: list[float]`
    :   The count of likes on comments related to the ad.

    `comments: list[float]`
    :   The number of comments on the ad.

    `company_page_clicks: list[float]`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: list[float]`
    :   Conversion value in the local currency.

    `cost_in_local_currency: list[float]`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: list[float]`
    :   Cost of ad campaign in USD.

    `document_completions: list[float]`
    :   Number of completions for document views.

    `document_first_quartile_completions: list[float]`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: list[float]`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: list[float]`
    :   Completions for third quartile of document views.

    `download_clicks: list[float]`
    :   Clicks on download links in the ad.

    `end_date: list[str]`
    :   End date of the ad analytics data.

    `external_website_conversions: list[float]`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites.

    `follows: list[float]`
    :   Number of follows generated by the ad.

    `full_screen_plays: list[float]`
    :   Number of times videos were played in fullscreen mode.

    `impressions: list[float]`
    :   Total number of times the ad was displayed.

    `job_applications: list[float]`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: list[float]`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: list[float]`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: list[float]`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: list[float]`
    :   Clicks on expressing interest through lead generation mail.

    `likes: list[float]`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: list[float]`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: list[float]`
    :   Leads generated in one click.

    `opens: list[float]`
    :   The number of times the ad was opened or expanded.

    `other_engagements: list[float]`
    :   Engagements other than clicks on the ad.

    `pivot: list[str]`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[list[typing.Any]]`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: list[float]`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: list[float]`
    :   Registrations completed post-viewing the ad.

    `reactions: list[float]`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: list[float]`
    :   Total registrations completed through the ad.

    `sends: list[float]`
    :   Number of messages sent through the ad.

    `shares: list[float]`
    :   Total shares generated by the ad.

    `sponsored_campaign: list[str]`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: list[str]`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: list[str]`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: list[float]`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: list[float]`
    :   Clicks on text URLs within the ad.

    `total_engagements: list[float]`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: list[float]`
    :   Leads generated through valid work emails.

    `video_completions: list[float]`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: list[float]`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: list[float]`
    :   Completions for midpoint of video views.

    `video_starts: list[float]`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: list[float]`
    :   Completions for third quartile of video views.

    `video_views: list[float]`
    :   Total views of videos in the ad.

    `viral_card_clicks: list[float]`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: list[float]`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: list[float]`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: list[float]`
    :   Likes received on comments in viral distribution.

    `viral_comments: list[float]`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: list[float]`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: list[float]`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: list[float]`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: list[float]`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: list[float]`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: list[float]`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: list[float]`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: list[float]`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: list[float]`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: list[float]`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: list[float]`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: list[float]`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: list[float]`
    :   Clicks on landing page in viral distribution.

    `viral_likes: list[float]`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: list[float]`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: list[float]`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: list[float]`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: list[float]`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: list[float]`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: list[float]`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: list[float]`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: list[float]`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: list[float]`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: list[float]`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: list[float]`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: list[float]`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: list[float]`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: list[float]`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: list[float]`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberJobTitleAnalyticsKeywordCondition"></a>

`AdMemberJobTitleAnalyticsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsListParams"></a>

`AdMemberJobTitleAnalyticsListParams(*args, **kwargs)`
:   Parameters for ad_member_job_title_analytics.list operation

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

<a id="AdMemberJobTitleAnalyticsLtCondition"></a>

`AdMemberJobTitleAnalyticsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsLteCondition"></a>

`AdMemberJobTitleAnalyticsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsNeqCondition"></a>

`AdMemberJobTitleAnalyticsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsNotCondition"></a>

`AdMemberJobTitleAnalyticsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsAnyCondition`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsOrCondition"></a>

`AdMemberJobTitleAnalyticsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsSearchFilter"></a>

`AdMemberJobTitleAnalyticsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_member_job_title_analytics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: float | None`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: float | None`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: float | None`
    :   An approximation of unique ad impressions.

    `card_clicks: float | None`
    :   The number of clicks on interactive card elements.

    `card_impressions: float | None`
    :   The number of times interactive cards were displayed.

    `clicks: float | None`
    :   Total number of clicks on the ad.

    `comment_likes: float | None`
    :   The count of likes on comments related to the ad.

    `comments: float | None`
    :   The number of comments on the ad.

    `company_page_clicks: float | None`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: float | None`
    :   Conversion value in the local currency.

    `cost_in_local_currency: float | None`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: float | None`
    :   Cost of ad campaign in USD.

    `document_completions: float | None`
    :   Number of completions for document views.

    `document_first_quartile_completions: float | None`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: float | None`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: float | None`
    :   Completions for third quartile of document views.

    `download_clicks: float | None`
    :   Clicks on download links in the ad.

    `end_date: str | None`
    :   End date of the ad analytics data.

    `external_website_conversions: float | None`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites.

    `follows: float | None`
    :   Number of follows generated by the ad.

    `full_screen_plays: float | None`
    :   Number of times videos were played in fullscreen mode.

    `impressions: float | None`
    :   Total number of times the ad was displayed.

    `job_applications: float | None`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: float | None`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: float | None`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: float | None`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: float | None`
    :   Clicks on expressing interest through lead generation mail.

    `likes: float | None`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: float | None`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: float | None`
    :   Leads generated in one click.

    `opens: float | None`
    :   The number of times the ad was opened or expanded.

    `other_engagements: float | None`
    :   Engagements other than clicks on the ad.

    `pivot: str | None`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[typing.Any] | None`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: float | None`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: float | None`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: float | None`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: float | None`
    :   Registrations completed post-viewing the ad.

    `reactions: float | None`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: float | None`
    :   Total registrations completed through the ad.

    `sends: float | None`
    :   Number of messages sent through the ad.

    `shares: float | None`
    :   Total shares generated by the ad.

    `sponsored_campaign: str | None`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str | None`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str | None`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: float | None`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: float | None`
    :   Clicks on text URLs within the ad.

    `total_engagements: float | None`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: float | None`
    :   Leads generated through valid work emails.

    `video_completions: float | None`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: float | None`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: float | None`
    :   Completions for midpoint of video views.

    `video_starts: float | None`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: float | None`
    :   Completions for third quartile of video views.

    `video_views: float | None`
    :   Total views of videos in the ad.

    `viral_card_clicks: float | None`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: float | None`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: float | None`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: float | None`
    :   Likes received on comments in viral distribution.

    `viral_comments: float | None`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: float | None`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: float | None`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: float | None`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: float | None`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: float | None`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: float | None`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: float | None`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: float | None`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: float | None`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: float | None`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: float | None`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: float | None`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: float | None`
    :   Clicks on landing page in viral distribution.

    `viral_likes: float | None`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: float | None`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: float | None`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: float | None`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: float | None`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: float | None`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: float | None`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: float | None`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: float | None`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: float | None`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: float | None`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: float | None`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: float | None`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: float | None`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: float | None`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: float | None`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: float | None`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: float | None`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberJobTitleAnalyticsSearchQuery"></a>

`AdMemberJobTitleAnalyticsSearchQuery(*args, **kwargs)`
:   Search query for ad_member_job_title_analytics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsSortFilter]`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsSortFilter"></a>

`AdMemberJobTitleAnalyticsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_member_job_title_analytics search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Literal['asc', 'desc']`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Literal['asc', 'desc']`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Literal['asc', 'desc']`
    :   An approximation of unique ad impressions.

    `card_clicks: Literal['asc', 'desc']`
    :   The number of clicks on interactive card elements.

    `card_impressions: Literal['asc', 'desc']`
    :   The number of times interactive cards were displayed.

    `clicks: Literal['asc', 'desc']`
    :   Total number of clicks on the ad.

    `comment_likes: Literal['asc', 'desc']`
    :   The count of likes on comments related to the ad.

    `comments: Literal['asc', 'desc']`
    :   The number of comments on the ad.

    `company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Literal['asc', 'desc']`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Literal['asc', 'desc']`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Literal['asc', 'desc']`
    :   Cost of ad campaign in USD.

    `document_completions: Literal['asc', 'desc']`
    :   Number of completions for document views.

    `document_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of document views.

    `download_clicks: Literal['asc', 'desc']`
    :   Clicks on download links in the ad.

    `end_date: Literal['asc', 'desc']`
    :   End date of the ad analytics data.

    `external_website_conversions: Literal['asc', 'desc']`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites.

    `follows: Literal['asc', 'desc']`
    :   Number of follows generated by the ad.

    `full_screen_plays: Literal['asc', 'desc']`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Literal['asc', 'desc']`
    :   Total number of times the ad was displayed.

    `job_applications: Literal['asc', 'desc']`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Literal['asc', 'desc']`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Literal['asc', 'desc']`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Literal['asc', 'desc']`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Literal['asc', 'desc']`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click.

    `opens: Literal['asc', 'desc']`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Literal['asc', 'desc']`
    :   Engagements other than clicks on the ad.

    `pivot: Literal['asc', 'desc']`
    :   Pivot dimension used for this analytics record

    `pivot_values: Literal['asc', 'desc']`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing the ad.

    `reactions: Literal['asc', 'desc']`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Literal['asc', 'desc']`
    :   Total registrations completed through the ad.

    `sends: Literal['asc', 'desc']`
    :   Number of messages sent through the ad.

    `shares: Literal['asc', 'desc']`
    :   Total shares generated by the ad.

    `sponsored_campaign: Literal['asc', 'desc']`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Literal['asc', 'desc']`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Literal['asc', 'desc']`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Literal['asc', 'desc']`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Literal['asc', 'desc']`
    :   Clicks on text URLs within the ad.

    `total_engagements: Literal['asc', 'desc']`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Literal['asc', 'desc']`
    :   Leads generated through valid work emails.

    `video_completions: Literal['asc', 'desc']`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of video views.

    `video_starts: Literal['asc', 'desc']`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of video views.

    `video_views: Literal['asc', 'desc']`
    :   Total views of videos in the ad.

    `viral_card_clicks: Literal['asc', 'desc']`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Literal['asc', 'desc']`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Literal['asc', 'desc']`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Literal['asc', 'desc']`
    :   Likes received on comments in viral distribution.

    `viral_comments: Literal['asc', 'desc']`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Literal['asc', 'desc']`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Literal['asc', 'desc']`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Literal['asc', 'desc']`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Literal['asc', 'desc']`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Literal['asc', 'desc']`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Literal['asc', 'desc']`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Literal['asc', 'desc']`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Literal['asc', 'desc']`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Literal['asc', 'desc']`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Literal['asc', 'desc']`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Literal['asc', 'desc']`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Literal['asc', 'desc']`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Literal['asc', 'desc']`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Literal['asc', 'desc']`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Literal['asc', 'desc']`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Literal['asc', 'desc']`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberJobTitleAnalyticsStartswithCondition"></a>

`AdMemberJobTitleAnalyticsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberJobTitleAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsStringFilter"></a>

`AdMemberJobTitleAnalyticsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: str`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: str`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: str`
    :   An approximation of unique ad impressions.

    `card_clicks: str`
    :   The number of clicks on interactive card elements.

    `card_impressions: str`
    :   The number of times interactive cards were displayed.

    `clicks: str`
    :   Total number of clicks on the ad.

    `comment_likes: str`
    :   The count of likes on comments related to the ad.

    `comments: str`
    :   The number of comments on the ad.

    `company_page_clicks: str`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: str`
    :   Conversion value in the local currency.

    `cost_in_local_currency: str`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: str`
    :   Cost of ad campaign in USD.

    `document_completions: str`
    :   Number of completions for document views.

    `document_first_quartile_completions: str`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: str`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: str`
    :   Completions for third quartile of document views.

    `download_clicks: str`
    :   Clicks on download links in the ad.

    `end_date: str`
    :   End date of the ad analytics data.

    `external_website_conversions: str`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: str`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: str`
    :   Post-view conversions on external websites.

    `follows: str`
    :   Number of follows generated by the ad.

    `full_screen_plays: str`
    :   Number of times videos were played in fullscreen mode.

    `impressions: str`
    :   Total number of times the ad was displayed.

    `job_applications: str`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: str`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: str`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: str`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: str`
    :   Clicks on expressing interest through lead generation mail.

    `likes: str`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: str`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: str`
    :   Leads generated in one click.

    `opens: str`
    :   The number of times the ad was opened or expanded.

    `other_engagements: str`
    :   Engagements other than clicks on the ad.

    `pivot: str`
    :   Pivot dimension used for this analytics record

    `pivot_values: str`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: str`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: str`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: str`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: str`
    :   Registrations completed post-viewing the ad.

    `reactions: str`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: str`
    :   Total registrations completed through the ad.

    `sends: str`
    :   Number of messages sent through the ad.

    `shares: str`
    :   Total shares generated by the ad.

    `sponsored_campaign: str`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: str`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: str`
    :   Clicks on text URLs within the ad.

    `total_engagements: str`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: str`
    :   Leads generated through valid work emails.

    `video_completions: str`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: str`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: str`
    :   Completions for midpoint of video views.

    `video_starts: str`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: str`
    :   Completions for third quartile of video views.

    `video_views: str`
    :   Total views of videos in the ad.

    `viral_card_clicks: str`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: str`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: str`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: str`
    :   Likes received on comments in viral distribution.

    `viral_comments: str`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: str`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: str`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: str`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: str`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: str`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: str`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: str`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: str`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: str`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: str`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: str`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: str`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: str`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: str`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: str`
    :   Clicks on landing page in viral distribution.

    `viral_likes: str`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: str`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: str`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: str`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: str`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: str`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: str`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: str`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: str`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: str`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: str`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: str`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: str`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: str`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: str`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: str`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: str`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: str`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberRegionAnalyticsAndCondition"></a>

`AdMemberRegionAnalyticsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsAnyCondition"></a>

`AdMemberRegionAnalyticsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsAnyValueFilter"></a>

`AdMemberRegionAnalyticsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Any`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Any`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Any`
    :   An approximation of unique ad impressions.

    `card_clicks: Any`
    :   The number of clicks on interactive card elements.

    `card_impressions: Any`
    :   The number of times interactive cards were displayed.

    `clicks: Any`
    :   Total number of clicks on the ad.

    `comment_likes: Any`
    :   The count of likes on comments related to the ad.

    `comments: Any`
    :   The number of comments on the ad.

    `company_page_clicks: Any`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Any`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Any`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Any`
    :   Cost of ad campaign in USD.

    `document_completions: Any`
    :   Number of completions for document views.

    `document_first_quartile_completions: Any`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Any`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Any`
    :   Completions for third quartile of document views.

    `download_clicks: Any`
    :   Clicks on download links in the ad.

    `end_date: Any`
    :   End date of the ad analytics data.

    `external_website_conversions: Any`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites.

    `follows: Any`
    :   Number of follows generated by the ad.

    `full_screen_plays: Any`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Any`
    :   Total number of times the ad was displayed.

    `job_applications: Any`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Any`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Any`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Any`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Any`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Any`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Any`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Any`
    :   Leads generated in one click.

    `opens: Any`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Any`
    :   Engagements other than clicks on the ad.

    `pivot: Any`
    :   Pivot dimension used for this analytics record

    `pivot_values: Any`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Any`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Any`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Any`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Any`
    :   Registrations completed post-viewing the ad.

    `reactions: Any`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Any`
    :   Total registrations completed through the ad.

    `sends: Any`
    :   Number of messages sent through the ad.

    `shares: Any`
    :   Total shares generated by the ad.

    `sponsored_campaign: Any`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Any`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Any`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Any`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Any`
    :   Clicks on text URLs within the ad.

    `total_engagements: Any`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Any`
    :   Leads generated through valid work emails.

    `video_completions: Any`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Any`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Any`
    :   Completions for midpoint of video views.

    `video_starts: Any`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Any`
    :   Completions for third quartile of video views.

    `video_views: Any`
    :   Total views of videos in the ad.

    `viral_card_clicks: Any`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Any`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Any`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Any`
    :   Likes received on comments in viral distribution.

    `viral_comments: Any`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Any`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Any`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Any`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Any`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Any`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Any`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Any`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Any`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Any`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Any`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Any`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Any`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Any`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Any`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Any`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Any`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Any`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Any`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Any`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Any`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Any`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Any`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Any`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Any`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Any`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Any`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Any`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Any`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Any`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Any`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Any`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberRegionAnalyticsArrayContainsCondition"></a>

`AdMemberRegionAnalyticsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsContainsCondition"></a>

`AdMemberRegionAnalyticsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsEndswithCondition"></a>

`AdMemberRegionAnalyticsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsEqCondition"></a>

`AdMemberRegionAnalyticsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsFuzzyCondition"></a>

`AdMemberRegionAnalyticsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsGtCondition"></a>

`AdMemberRegionAnalyticsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsGteCondition"></a>

`AdMemberRegionAnalyticsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsInCondition"></a>

`AdMemberRegionAnalyticsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsInFilter`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsInFilter"></a>

`AdMemberRegionAnalyticsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: list[float]`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: list[float]`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: list[float]`
    :   An approximation of unique ad impressions.

    `card_clicks: list[float]`
    :   The number of clicks on interactive card elements.

    `card_impressions: list[float]`
    :   The number of times interactive cards were displayed.

    `clicks: list[float]`
    :   Total number of clicks on the ad.

    `comment_likes: list[float]`
    :   The count of likes on comments related to the ad.

    `comments: list[float]`
    :   The number of comments on the ad.

    `company_page_clicks: list[float]`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: list[float]`
    :   Conversion value in the local currency.

    `cost_in_local_currency: list[float]`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: list[float]`
    :   Cost of ad campaign in USD.

    `document_completions: list[float]`
    :   Number of completions for document views.

    `document_first_quartile_completions: list[float]`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: list[float]`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: list[float]`
    :   Completions for third quartile of document views.

    `download_clicks: list[float]`
    :   Clicks on download links in the ad.

    `end_date: list[str]`
    :   End date of the ad analytics data.

    `external_website_conversions: list[float]`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites.

    `follows: list[float]`
    :   Number of follows generated by the ad.

    `full_screen_plays: list[float]`
    :   Number of times videos were played in fullscreen mode.

    `impressions: list[float]`
    :   Total number of times the ad was displayed.

    `job_applications: list[float]`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: list[float]`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: list[float]`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: list[float]`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: list[float]`
    :   Clicks on expressing interest through lead generation mail.

    `likes: list[float]`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: list[float]`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: list[float]`
    :   Leads generated in one click.

    `opens: list[float]`
    :   The number of times the ad was opened or expanded.

    `other_engagements: list[float]`
    :   Engagements other than clicks on the ad.

    `pivot: list[str]`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[list[typing.Any]]`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: list[float]`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: list[float]`
    :   Registrations completed post-viewing the ad.

    `reactions: list[float]`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: list[float]`
    :   Total registrations completed through the ad.

    `sends: list[float]`
    :   Number of messages sent through the ad.

    `shares: list[float]`
    :   Total shares generated by the ad.

    `sponsored_campaign: list[str]`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: list[str]`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: list[str]`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: list[float]`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: list[float]`
    :   Clicks on text URLs within the ad.

    `total_engagements: list[float]`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: list[float]`
    :   Leads generated through valid work emails.

    `video_completions: list[float]`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: list[float]`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: list[float]`
    :   Completions for midpoint of video views.

    `video_starts: list[float]`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: list[float]`
    :   Completions for third quartile of video views.

    `video_views: list[float]`
    :   Total views of videos in the ad.

    `viral_card_clicks: list[float]`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: list[float]`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: list[float]`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: list[float]`
    :   Likes received on comments in viral distribution.

    `viral_comments: list[float]`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: list[float]`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: list[float]`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: list[float]`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: list[float]`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: list[float]`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: list[float]`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: list[float]`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: list[float]`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: list[float]`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: list[float]`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: list[float]`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: list[float]`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: list[float]`
    :   Clicks on landing page in viral distribution.

    `viral_likes: list[float]`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: list[float]`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: list[float]`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: list[float]`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: list[float]`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: list[float]`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: list[float]`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: list[float]`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: list[float]`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: list[float]`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: list[float]`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: list[float]`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: list[float]`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: list[float]`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: list[float]`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: list[float]`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberRegionAnalyticsKeywordCondition"></a>

`AdMemberRegionAnalyticsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsListParams"></a>

`AdMemberRegionAnalyticsListParams(*args, **kwargs)`
:   Parameters for ad_member_region_analytics.list operation

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

<a id="AdMemberRegionAnalyticsLtCondition"></a>

`AdMemberRegionAnalyticsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsLteCondition"></a>

`AdMemberRegionAnalyticsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsNeqCondition"></a>

`AdMemberRegionAnalyticsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsNotCondition"></a>

`AdMemberRegionAnalyticsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsAnyCondition`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsOrCondition"></a>

`AdMemberRegionAnalyticsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsSearchFilter"></a>

`AdMemberRegionAnalyticsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_member_region_analytics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: float | None`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: float | None`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: float | None`
    :   An approximation of unique ad impressions.

    `card_clicks: float | None`
    :   The number of clicks on interactive card elements.

    `card_impressions: float | None`
    :   The number of times interactive cards were displayed.

    `clicks: float | None`
    :   Total number of clicks on the ad.

    `comment_likes: float | None`
    :   The count of likes on comments related to the ad.

    `comments: float | None`
    :   The number of comments on the ad.

    `company_page_clicks: float | None`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: float | None`
    :   Conversion value in the local currency.

    `cost_in_local_currency: float | None`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: float | None`
    :   Cost of ad campaign in USD.

    `document_completions: float | None`
    :   Number of completions for document views.

    `document_first_quartile_completions: float | None`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: float | None`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: float | None`
    :   Completions for third quartile of document views.

    `download_clicks: float | None`
    :   Clicks on download links in the ad.

    `end_date: str | None`
    :   End date of the ad analytics data.

    `external_website_conversions: float | None`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites.

    `follows: float | None`
    :   Number of follows generated by the ad.

    `full_screen_plays: float | None`
    :   Number of times videos were played in fullscreen mode.

    `impressions: float | None`
    :   Total number of times the ad was displayed.

    `job_applications: float | None`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: float | None`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: float | None`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: float | None`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: float | None`
    :   Clicks on expressing interest through lead generation mail.

    `likes: float | None`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: float | None`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: float | None`
    :   Leads generated in one click.

    `opens: float | None`
    :   The number of times the ad was opened or expanded.

    `other_engagements: float | None`
    :   Engagements other than clicks on the ad.

    `pivot: str | None`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[typing.Any] | None`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: float | None`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: float | None`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: float | None`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: float | None`
    :   Registrations completed post-viewing the ad.

    `reactions: float | None`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: float | None`
    :   Total registrations completed through the ad.

    `sends: float | None`
    :   Number of messages sent through the ad.

    `shares: float | None`
    :   Total shares generated by the ad.

    `sponsored_campaign: str | None`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str | None`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str | None`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: float | None`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: float | None`
    :   Clicks on text URLs within the ad.

    `total_engagements: float | None`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: float | None`
    :   Leads generated through valid work emails.

    `video_completions: float | None`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: float | None`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: float | None`
    :   Completions for midpoint of video views.

    `video_starts: float | None`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: float | None`
    :   Completions for third quartile of video views.

    `video_views: float | None`
    :   Total views of videos in the ad.

    `viral_card_clicks: float | None`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: float | None`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: float | None`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: float | None`
    :   Likes received on comments in viral distribution.

    `viral_comments: float | None`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: float | None`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: float | None`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: float | None`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: float | None`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: float | None`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: float | None`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: float | None`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: float | None`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: float | None`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: float | None`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: float | None`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: float | None`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: float | None`
    :   Clicks on landing page in viral distribution.

    `viral_likes: float | None`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: float | None`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: float | None`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: float | None`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: float | None`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: float | None`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: float | None`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: float | None`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: float | None`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: float | None`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: float | None`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: float | None`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: float | None`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: float | None`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: float | None`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: float | None`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: float | None`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: float | None`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberRegionAnalyticsSearchQuery"></a>

`AdMemberRegionAnalyticsSearchQuery(*args, **kwargs)`
:   Search query for ad_member_region_analytics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsSortFilter]`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsSortFilter"></a>

`AdMemberRegionAnalyticsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_member_region_analytics search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Literal['asc', 'desc']`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Literal['asc', 'desc']`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Literal['asc', 'desc']`
    :   An approximation of unique ad impressions.

    `card_clicks: Literal['asc', 'desc']`
    :   The number of clicks on interactive card elements.

    `card_impressions: Literal['asc', 'desc']`
    :   The number of times interactive cards were displayed.

    `clicks: Literal['asc', 'desc']`
    :   Total number of clicks on the ad.

    `comment_likes: Literal['asc', 'desc']`
    :   The count of likes on comments related to the ad.

    `comments: Literal['asc', 'desc']`
    :   The number of comments on the ad.

    `company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Literal['asc', 'desc']`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Literal['asc', 'desc']`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Literal['asc', 'desc']`
    :   Cost of ad campaign in USD.

    `document_completions: Literal['asc', 'desc']`
    :   Number of completions for document views.

    `document_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of document views.

    `download_clicks: Literal['asc', 'desc']`
    :   Clicks on download links in the ad.

    `end_date: Literal['asc', 'desc']`
    :   End date of the ad analytics data.

    `external_website_conversions: Literal['asc', 'desc']`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites.

    `follows: Literal['asc', 'desc']`
    :   Number of follows generated by the ad.

    `full_screen_plays: Literal['asc', 'desc']`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Literal['asc', 'desc']`
    :   Total number of times the ad was displayed.

    `job_applications: Literal['asc', 'desc']`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Literal['asc', 'desc']`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Literal['asc', 'desc']`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Literal['asc', 'desc']`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Literal['asc', 'desc']`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click.

    `opens: Literal['asc', 'desc']`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Literal['asc', 'desc']`
    :   Engagements other than clicks on the ad.

    `pivot: Literal['asc', 'desc']`
    :   Pivot dimension used for this analytics record

    `pivot_values: Literal['asc', 'desc']`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing the ad.

    `reactions: Literal['asc', 'desc']`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Literal['asc', 'desc']`
    :   Total registrations completed through the ad.

    `sends: Literal['asc', 'desc']`
    :   Number of messages sent through the ad.

    `shares: Literal['asc', 'desc']`
    :   Total shares generated by the ad.

    `sponsored_campaign: Literal['asc', 'desc']`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Literal['asc', 'desc']`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Literal['asc', 'desc']`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Literal['asc', 'desc']`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Literal['asc', 'desc']`
    :   Clicks on text URLs within the ad.

    `total_engagements: Literal['asc', 'desc']`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Literal['asc', 'desc']`
    :   Leads generated through valid work emails.

    `video_completions: Literal['asc', 'desc']`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of video views.

    `video_starts: Literal['asc', 'desc']`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of video views.

    `video_views: Literal['asc', 'desc']`
    :   Total views of videos in the ad.

    `viral_card_clicks: Literal['asc', 'desc']`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Literal['asc', 'desc']`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Literal['asc', 'desc']`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Literal['asc', 'desc']`
    :   Likes received on comments in viral distribution.

    `viral_comments: Literal['asc', 'desc']`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Literal['asc', 'desc']`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Literal['asc', 'desc']`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Literal['asc', 'desc']`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Literal['asc', 'desc']`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Literal['asc', 'desc']`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Literal['asc', 'desc']`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Literal['asc', 'desc']`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Literal['asc', 'desc']`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Literal['asc', 'desc']`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Literal['asc', 'desc']`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Literal['asc', 'desc']`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Literal['asc', 'desc']`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Literal['asc', 'desc']`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Literal['asc', 'desc']`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Literal['asc', 'desc']`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Literal['asc', 'desc']`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberRegionAnalyticsStartswithCondition"></a>

`AdMemberRegionAnalyticsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberRegionAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsStringFilter"></a>

`AdMemberRegionAnalyticsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: str`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: str`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: str`
    :   An approximation of unique ad impressions.

    `card_clicks: str`
    :   The number of clicks on interactive card elements.

    `card_impressions: str`
    :   The number of times interactive cards were displayed.

    `clicks: str`
    :   Total number of clicks on the ad.

    `comment_likes: str`
    :   The count of likes on comments related to the ad.

    `comments: str`
    :   The number of comments on the ad.

    `company_page_clicks: str`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: str`
    :   Conversion value in the local currency.

    `cost_in_local_currency: str`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: str`
    :   Cost of ad campaign in USD.

    `document_completions: str`
    :   Number of completions for document views.

    `document_first_quartile_completions: str`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: str`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: str`
    :   Completions for third quartile of document views.

    `download_clicks: str`
    :   Clicks on download links in the ad.

    `end_date: str`
    :   End date of the ad analytics data.

    `external_website_conversions: str`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: str`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: str`
    :   Post-view conversions on external websites.

    `follows: str`
    :   Number of follows generated by the ad.

    `full_screen_plays: str`
    :   Number of times videos were played in fullscreen mode.

    `impressions: str`
    :   Total number of times the ad was displayed.

    `job_applications: str`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: str`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: str`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: str`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: str`
    :   Clicks on expressing interest through lead generation mail.

    `likes: str`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: str`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: str`
    :   Leads generated in one click.

    `opens: str`
    :   The number of times the ad was opened or expanded.

    `other_engagements: str`
    :   Engagements other than clicks on the ad.

    `pivot: str`
    :   Pivot dimension used for this analytics record

    `pivot_values: str`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: str`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: str`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: str`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: str`
    :   Registrations completed post-viewing the ad.

    `reactions: str`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: str`
    :   Total registrations completed through the ad.

    `sends: str`
    :   Number of messages sent through the ad.

    `shares: str`
    :   Total shares generated by the ad.

    `sponsored_campaign: str`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: str`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: str`
    :   Clicks on text URLs within the ad.

    `total_engagements: str`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: str`
    :   Leads generated through valid work emails.

    `video_completions: str`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: str`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: str`
    :   Completions for midpoint of video views.

    `video_starts: str`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: str`
    :   Completions for third quartile of video views.

    `video_views: str`
    :   Total views of videos in the ad.

    `viral_card_clicks: str`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: str`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: str`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: str`
    :   Likes received on comments in viral distribution.

    `viral_comments: str`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: str`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: str`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: str`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: str`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: str`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: str`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: str`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: str`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: str`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: str`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: str`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: str`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: str`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: str`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: str`
    :   Clicks on landing page in viral distribution.

    `viral_likes: str`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: str`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: str`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: str`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: str`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: str`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: str`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: str`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: str`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: str`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: str`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: str`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: str`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: str`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: str`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: str`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: str`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: str`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberSeniorityAnalyticsAndCondition"></a>

`AdMemberSeniorityAnalyticsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsAnyCondition"></a>

`AdMemberSeniorityAnalyticsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsAnyValueFilter"></a>

`AdMemberSeniorityAnalyticsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Any`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Any`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Any`
    :   An approximation of unique ad impressions.

    `card_clicks: Any`
    :   The number of clicks on interactive card elements.

    `card_impressions: Any`
    :   The number of times interactive cards were displayed.

    `clicks: Any`
    :   Total number of clicks on the ad.

    `comment_likes: Any`
    :   The count of likes on comments related to the ad.

    `comments: Any`
    :   The number of comments on the ad.

    `company_page_clicks: Any`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Any`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Any`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Any`
    :   Cost of ad campaign in USD.

    `document_completions: Any`
    :   Number of completions for document views.

    `document_first_quartile_completions: Any`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Any`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Any`
    :   Completions for third quartile of document views.

    `download_clicks: Any`
    :   Clicks on download links in the ad.

    `end_date: Any`
    :   End date of the ad analytics data.

    `external_website_conversions: Any`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites.

    `follows: Any`
    :   Number of follows generated by the ad.

    `full_screen_plays: Any`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Any`
    :   Total number of times the ad was displayed.

    `job_applications: Any`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Any`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Any`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Any`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Any`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Any`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Any`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Any`
    :   Leads generated in one click.

    `opens: Any`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Any`
    :   Engagements other than clicks on the ad.

    `pivot: Any`
    :   Pivot dimension used for this analytics record

    `pivot_values: Any`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Any`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Any`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Any`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Any`
    :   Registrations completed post-viewing the ad.

    `reactions: Any`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Any`
    :   Total registrations completed through the ad.

    `sends: Any`
    :   Number of messages sent through the ad.

    `shares: Any`
    :   Total shares generated by the ad.

    `sponsored_campaign: Any`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Any`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Any`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Any`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Any`
    :   Clicks on text URLs within the ad.

    `total_engagements: Any`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Any`
    :   Leads generated through valid work emails.

    `video_completions: Any`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Any`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Any`
    :   Completions for midpoint of video views.

    `video_starts: Any`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Any`
    :   Completions for third quartile of video views.

    `video_views: Any`
    :   Total views of videos in the ad.

    `viral_card_clicks: Any`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Any`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Any`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Any`
    :   Likes received on comments in viral distribution.

    `viral_comments: Any`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Any`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Any`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Any`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Any`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Any`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Any`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Any`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Any`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Any`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Any`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Any`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Any`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Any`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Any`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Any`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Any`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Any`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Any`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Any`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Any`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Any`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Any`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Any`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Any`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Any`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Any`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Any`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Any`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Any`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Any`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Any`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Any`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Any`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Any`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Any`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberSeniorityAnalyticsArrayContainsCondition"></a>

`AdMemberSeniorityAnalyticsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsContainsCondition"></a>

`AdMemberSeniorityAnalyticsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsEndswithCondition"></a>

`AdMemberSeniorityAnalyticsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsEqCondition"></a>

`AdMemberSeniorityAnalyticsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsFuzzyCondition"></a>

`AdMemberSeniorityAnalyticsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsGtCondition"></a>

`AdMemberSeniorityAnalyticsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsGteCondition"></a>

`AdMemberSeniorityAnalyticsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsInCondition"></a>

`AdMemberSeniorityAnalyticsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsInFilter`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsInFilter"></a>

`AdMemberSeniorityAnalyticsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: list[float]`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: list[float]`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: list[float]`
    :   An approximation of unique ad impressions.

    `card_clicks: list[float]`
    :   The number of clicks on interactive card elements.

    `card_impressions: list[float]`
    :   The number of times interactive cards were displayed.

    `clicks: list[float]`
    :   Total number of clicks on the ad.

    `comment_likes: list[float]`
    :   The count of likes on comments related to the ad.

    `comments: list[float]`
    :   The number of comments on the ad.

    `company_page_clicks: list[float]`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: list[float]`
    :   Conversion value in the local currency.

    `cost_in_local_currency: list[float]`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: list[float]`
    :   Cost of ad campaign in USD.

    `document_completions: list[float]`
    :   Number of completions for document views.

    `document_first_quartile_completions: list[float]`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: list[float]`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: list[float]`
    :   Completions for third quartile of document views.

    `download_clicks: list[float]`
    :   Clicks on download links in the ad.

    `end_date: list[str]`
    :   End date of the ad analytics data.

    `external_website_conversions: list[float]`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites.

    `follows: list[float]`
    :   Number of follows generated by the ad.

    `full_screen_plays: list[float]`
    :   Number of times videos were played in fullscreen mode.

    `impressions: list[float]`
    :   Total number of times the ad was displayed.

    `job_applications: list[float]`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: list[float]`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: list[float]`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: list[float]`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: list[float]`
    :   Clicks on expressing interest through lead generation mail.

    `likes: list[float]`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: list[float]`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: list[float]`
    :   Leads generated in one click.

    `opens: list[float]`
    :   The number of times the ad was opened or expanded.

    `other_engagements: list[float]`
    :   Engagements other than clicks on the ad.

    `pivot: list[str]`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[list[typing.Any]]`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: list[float]`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: list[float]`
    :   Registrations completed post-viewing the ad.

    `reactions: list[float]`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: list[float]`
    :   Total registrations completed through the ad.

    `sends: list[float]`
    :   Number of messages sent through the ad.

    `shares: list[float]`
    :   Total shares generated by the ad.

    `sponsored_campaign: list[str]`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: list[str]`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: list[str]`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: list[float]`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: list[float]`
    :   Clicks on text URLs within the ad.

    `total_engagements: list[float]`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: list[float]`
    :   Leads generated through valid work emails.

    `video_completions: list[float]`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: list[float]`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: list[float]`
    :   Completions for midpoint of video views.

    `video_starts: list[float]`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: list[float]`
    :   Completions for third quartile of video views.

    `video_views: list[float]`
    :   Total views of videos in the ad.

    `viral_card_clicks: list[float]`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: list[float]`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: list[float]`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: list[float]`
    :   Likes received on comments in viral distribution.

    `viral_comments: list[float]`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: list[float]`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: list[float]`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: list[float]`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: list[float]`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: list[float]`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: list[float]`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: list[float]`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: list[float]`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: list[float]`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: list[float]`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: list[float]`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: list[float]`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: list[float]`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: list[float]`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: list[float]`
    :   Clicks on landing page in viral distribution.

    `viral_likes: list[float]`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: list[float]`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: list[float]`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: list[float]`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: list[float]`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: list[float]`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: list[float]`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: list[float]`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: list[float]`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: list[float]`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: list[float]`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: list[float]`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: list[float]`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: list[float]`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: list[float]`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: list[float]`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: list[float]`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: list[float]`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: list[float]`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberSeniorityAnalyticsKeywordCondition"></a>

`AdMemberSeniorityAnalyticsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsListParams"></a>

`AdMemberSeniorityAnalyticsListParams(*args, **kwargs)`
:   Parameters for ad_member_seniority_analytics.list operation

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

<a id="AdMemberSeniorityAnalyticsLtCondition"></a>

`AdMemberSeniorityAnalyticsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsLteCondition"></a>

`AdMemberSeniorityAnalyticsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsNeqCondition"></a>

`AdMemberSeniorityAnalyticsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsSearchFilter`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsNotCondition"></a>

`AdMemberSeniorityAnalyticsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsAnyCondition`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsOrCondition"></a>

`AdMemberSeniorityAnalyticsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsAnyCondition]`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsSearchFilter"></a>

`AdMemberSeniorityAnalyticsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_member_seniority_analytics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: float | None`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: float | None`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: float | None`
    :   An approximation of unique ad impressions.

    `card_clicks: float | None`
    :   The number of clicks on interactive card elements.

    `card_impressions: float | None`
    :   The number of times interactive cards were displayed.

    `clicks: float | None`
    :   Total number of clicks on the ad.

    `comment_likes: float | None`
    :   The count of likes on comments related to the ad.

    `comments: float | None`
    :   The number of comments on the ad.

    `company_page_clicks: float | None`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: float | None`
    :   Conversion value in the local currency.

    `cost_in_local_currency: float | None`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: float | None`
    :   Cost of ad campaign in USD.

    `document_completions: float | None`
    :   Number of completions for document views.

    `document_first_quartile_completions: float | None`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: float | None`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: float | None`
    :   Completions for third quartile of document views.

    `download_clicks: float | None`
    :   Clicks on download links in the ad.

    `end_date: str | None`
    :   End date of the ad analytics data.

    `external_website_conversions: float | None`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites.

    `follows: float | None`
    :   Number of follows generated by the ad.

    `full_screen_plays: float | None`
    :   Number of times videos were played in fullscreen mode.

    `impressions: float | None`
    :   Total number of times the ad was displayed.

    `job_applications: float | None`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: float | None`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: float | None`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: float | None`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: float | None`
    :   Clicks on expressing interest through lead generation mail.

    `likes: float | None`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: float | None`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: float | None`
    :   Leads generated in one click.

    `opens: float | None`
    :   The number of times the ad was opened or expanded.

    `other_engagements: float | None`
    :   Engagements other than clicks on the ad.

    `pivot: str | None`
    :   Pivot dimension used for this analytics record

    `pivot_values: list[typing.Any] | None`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: float | None`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: float | None`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: float | None`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: float | None`
    :   Registrations completed post-viewing the ad.

    `reactions: float | None`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: float | None`
    :   Total registrations completed through the ad.

    `sends: float | None`
    :   Number of messages sent through the ad.

    `shares: float | None`
    :   Total shares generated by the ad.

    `sponsored_campaign: str | None`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str | None`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str | None`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: float | None`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: float | None`
    :   Clicks on text URLs within the ad.

    `total_engagements: float | None`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: float | None`
    :   Leads generated through valid work emails.

    `video_completions: float | None`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: float | None`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: float | None`
    :   Completions for midpoint of video views.

    `video_starts: float | None`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: float | None`
    :   Completions for third quartile of video views.

    `video_views: float | None`
    :   Total views of videos in the ad.

    `viral_card_clicks: float | None`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: float | None`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: float | None`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: float | None`
    :   Likes received on comments in viral distribution.

    `viral_comments: float | None`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: float | None`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: float | None`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: float | None`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: float | None`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: float | None`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: float | None`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: float | None`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: float | None`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: float | None`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: float | None`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: float | None`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: float | None`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: float | None`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: float | None`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: float | None`
    :   Clicks on landing page in viral distribution.

    `viral_likes: float | None`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: float | None`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: float | None`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: float | None`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: float | None`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: float | None`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: float | None`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: float | None`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: float | None`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: float | None`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: float | None`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: float | None`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: float | None`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: float | None`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: float | None`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: float | None`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: float | None`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: float | None`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: float | None`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: float | None`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberSeniorityAnalyticsSearchQuery"></a>

`AdMemberSeniorityAnalyticsSearchQuery(*args, **kwargs)`
:   Search query for ad_member_seniority_analytics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsSortFilter]`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsSortFilter"></a>

`AdMemberSeniorityAnalyticsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_member_seniority_analytics search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: Literal['asc', 'desc']`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: Literal['asc', 'desc']`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: Literal['asc', 'desc']`
    :   An approximation of unique ad impressions.

    `card_clicks: Literal['asc', 'desc']`
    :   The number of clicks on interactive card elements.

    `card_impressions: Literal['asc', 'desc']`
    :   The number of times interactive cards were displayed.

    `clicks: Literal['asc', 'desc']`
    :   Total number of clicks on the ad.

    `comment_likes: Literal['asc', 'desc']`
    :   The count of likes on comments related to the ad.

    `comments: Literal['asc', 'desc']`
    :   The number of comments on the ad.

    `company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: Literal['asc', 'desc']`
    :   Conversion value in the local currency.

    `cost_in_local_currency: Literal['asc', 'desc']`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: Literal['asc', 'desc']`
    :   Cost of ad campaign in USD.

    `document_completions: Literal['asc', 'desc']`
    :   Number of completions for document views.

    `document_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of document views.

    `download_clicks: Literal['asc', 'desc']`
    :   Clicks on download links in the ad.

    `end_date: Literal['asc', 'desc']`
    :   End date of the ad analytics data.

    `external_website_conversions: Literal['asc', 'desc']`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites.

    `follows: Literal['asc', 'desc']`
    :   Number of follows generated by the ad.

    `full_screen_plays: Literal['asc', 'desc']`
    :   Number of times videos were played in fullscreen mode.

    `impressions: Literal['asc', 'desc']`
    :   Total number of times the ad was displayed.

    `job_applications: Literal['asc', 'desc']`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: Literal['asc', 'desc']`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: Literal['asc', 'desc']`
    :   Clicks on expressing interest through lead generation mail.

    `likes: Literal['asc', 'desc']`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: Literal['asc', 'desc']`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click.

    `opens: Literal['asc', 'desc']`
    :   The number of times the ad was opened or expanded.

    `other_engagements: Literal['asc', 'desc']`
    :   Engagements other than clicks on the ad.

    `pivot: Literal['asc', 'desc']`
    :   Pivot dimension used for this analytics record

    `pivot_values: Literal['asc', 'desc']`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing the ad.

    `reactions: Literal['asc', 'desc']`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: Literal['asc', 'desc']`
    :   Total registrations completed through the ad.

    `sends: Literal['asc', 'desc']`
    :   Number of messages sent through the ad.

    `shares: Literal['asc', 'desc']`
    :   Total shares generated by the ad.

    `sponsored_campaign: Literal['asc', 'desc']`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: Literal['asc', 'desc']`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: Literal['asc', 'desc']`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: Literal['asc', 'desc']`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: Literal['asc', 'desc']`
    :   Clicks on text URLs within the ad.

    `total_engagements: Literal['asc', 'desc']`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: Literal['asc', 'desc']`
    :   Leads generated through valid work emails.

    `video_completions: Literal['asc', 'desc']`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: Literal['asc', 'desc']`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: Literal['asc', 'desc']`
    :   Completions for midpoint of video views.

    `video_starts: Literal['asc', 'desc']`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: Literal['asc', 'desc']`
    :   Completions for third quartile of video views.

    `video_views: Literal['asc', 'desc']`
    :   Total views of videos in the ad.

    `viral_card_clicks: Literal['asc', 'desc']`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: Literal['asc', 'desc']`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: Literal['asc', 'desc']`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: Literal['asc', 'desc']`
    :   Likes received on comments in viral distribution.

    `viral_comments: Literal['asc', 'desc']`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: Literal['asc', 'desc']`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: Literal['asc', 'desc']`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: Literal['asc', 'desc']`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: Literal['asc', 'desc']`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: Literal['asc', 'desc']`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: Literal['asc', 'desc']`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: Literal['asc', 'desc']`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: Literal['asc', 'desc']`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: Literal['asc', 'desc']`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: Literal['asc', 'desc']`
    :   Clicks on landing page in viral distribution.

    `viral_likes: Literal['asc', 'desc']`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: Literal['asc', 'desc']`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: Literal['asc', 'desc']`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: Literal['asc', 'desc']`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: Literal['asc', 'desc']`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: Literal['asc', 'desc']`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: Literal['asc', 'desc']`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: Literal['asc', 'desc']`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: Literal['asc', 'desc']`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: Literal['asc', 'desc']`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: Literal['asc', 'desc']`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: Literal['asc', 'desc']`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: Literal['asc', 'desc']`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: Literal['asc', 'desc']`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: Literal['asc', 'desc']`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: Literal['asc', 'desc']`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: Literal['asc', 'desc']`
    :   Total views of videos in viral distribution of the ad.

<a id="AdMemberSeniorityAnalyticsStartswithCondition"></a>

`AdMemberSeniorityAnalyticsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.AdMemberSeniorityAnalyticsStringFilter`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsStringFilter"></a>

`AdMemberSeniorityAnalyticsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_clicks: str`
    :   The number of clicks on action buttons in the ad.

    `ad_unit_clicks: str`
    :   The number of clicks on ad unit components.

    `approximate_member_reach: str`
    :   An approximation of unique ad impressions.

    `card_clicks: str`
    :   The number of clicks on interactive card elements.

    `card_impressions: str`
    :   The number of times interactive cards were displayed.

    `clicks: str`
    :   Total number of clicks on the ad.

    `comment_likes: str`
    :   The count of likes on comments related to the ad.

    `comments: str`
    :   The number of comments on the ad.

    `company_page_clicks: str`
    :   Clicks on the company page associated with the ad.

    `conversion_value_in_local_currency: str`
    :   Conversion value in the local currency.

    `cost_in_local_currency: str`
    :   Cost of ad campaign in the local currency.

    `cost_in_usd: str`
    :   Cost of ad campaign in USD.

    `document_completions: str`
    :   Number of completions for document views.

    `document_first_quartile_completions: str`
    :   Completions for first quartile of document views.

    `document_midpoint_completions: str`
    :   Completions for midpoint of document views.

    `document_third_quartile_completions: str`
    :   Completions for third quartile of document views.

    `download_clicks: str`
    :   Clicks on download links in the ad.

    `end_date: str`
    :   End date of the ad analytics data.

    `external_website_conversions: str`
    :   Conversions that lead to external websites.

    `external_website_post_click_conversions: str`
    :   Post-click conversions on external websites.

    `external_website_post_view_conversions: str`
    :   Post-view conversions on external websites.

    `follows: str`
    :   Number of follows generated by the ad.

    `full_screen_plays: str`
    :   Number of times videos were played in fullscreen mode.

    `impressions: str`
    :   Total number of times the ad was displayed.

    `job_applications: str`
    :   Number of job applications initiated through the ad.

    `job_apply_clicks: str`
    :   Clicks on apply job button in the ad.

    `landing_page_clicks: str`
    :   Clicks on the landing page associated with the ad.

    `lead_generation_mail_contact_info_shares: str`
    :   Shares of contact information through lead generation.

    `lead_generation_mail_interested_clicks: str`
    :   Clicks on expressing interest through lead generation mail.

    `likes: str`
    :   Total likes received on the ad.

    `one_click_lead_form_opens: str`
    :   Number of times lead forms were opened in one click.

    `one_click_leads: str`
    :   Leads generated in one click.

    `opens: str`
    :   The number of times the ad was opened or expanded.

    `other_engagements: str`
    :   Engagements other than clicks on the ad.

    `pivot: str`
    :   Pivot dimension used for this analytics record

    `pivot_values: str`
    :   Values used for pivoting the analytics.

    `post_click_job_applications: str`
    :   Job applications initiated post-clicking on the ad.

    `post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking on the ad.

    `post_click_registrations: str`
    :   Registrations completed post-clicking on the ad.

    `post_view_job_applications: str`
    :   Job applications initiated post-viewing the ad.

    `post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing the ad.

    `post_view_registrations: str`
    :   Registrations completed post-viewing the ad.

    `reactions: str`
    :   Total reactions (e.g., like, love, celebrate) on the ad.

    `registrations: str`
    :   Total registrations completed through the ad.

    `sends: str`
    :   Number of messages sent through the ad.

    `shares: str`
    :   Total shares generated by the ad.

    `sponsored_campaign: str`
    :   URN of the sponsored campaign this analytics record belongs to

    `start_date: str`
    :   Start date of the ad analytics data.

    `string_of_pivot_values: str`
    :   Comma-separated string of pivot values for this analytics record

    `talent_leads: str`
    :   Number of leads related to talent acquisition.

    `text_url_clicks: str`
    :   Clicks on text URLs within the ad.

    `total_engagements: str`
    :   Total number of engagements on the ad.

    `valid_work_email_leads: str`
    :   Leads generated through valid work emails.

    `video_completions: str`
    :   Number of times videos were watched till completion.

    `video_first_quartile_completions: str`
    :   Completions for first quartile of video views.

    `video_midpoint_completions: str`
    :   Completions for midpoint of video views.

    `video_starts: str`
    :   Total video starts initiated by users.

    `video_third_quartile_completions: str`
    :   Completions for third quartile of video views.

    `video_views: str`
    :   Total views of videos in the ad.

    `viral_card_clicks: str`
    :   Clicks on interactive card components in viral distribution.

    `viral_card_impressions: str`
    :   Impressions of interactive cards in viral distribution.

    `viral_clicks: str`
    :   Total clicks in viral distribution of the ad.

    `viral_comment_likes: str`
    :   Likes received on comments in viral distribution.

    `viral_comments: str`
    :   Number of comments in viral distribution of the ad.

    `viral_company_page_clicks: str`
    :   Clicks on the company page in viral distribution.

    `viral_document_completions: str`
    :   Complete views of documents in viral distribution.

    `viral_document_first_quartile_completions: str`
    :   First quartile completions of documents in viral distribution.

    `viral_document_midpoint_completions: str`
    :   Midpoint completions of documents in viral distribution.

    `viral_document_third_quartile_completions: str`
    :   Third quartile completions of documents in viral distribution.

    `viral_download_clicks: str`
    :   Clicks on downloads in viral distribution of the ad.

    `viral_external_website_conversions: str`
    :   External website conversions in viral distribution.

    `viral_external_website_post_click_conversions: str`
    :   Post-click conversions on external websites in viral distribution.

    `viral_external_website_post_view_conversions: str`
    :   Post-view conversions on external websites in viral distribution.

    `viral_follows: str`
    :   Follows generated in viral distribution of the ad.

    `viral_full_screen_plays: str`
    :   Fullscreen video plays in viral distribution.

    `viral_impressions: str`
    :   Total impressions in viral distribution of the ad.

    `viral_job_applications: str`
    :   Job applications initiated in viral distribution.

    `viral_job_apply_clicks: str`
    :   Clicks on apply job button in viral distribution of the ad.

    `viral_landing_page_clicks: str`
    :   Clicks on landing page in viral distribution.

    `viral_likes: str`
    :   Total likes in viral distribution of the ad.

    `viral_one_click_lead_form_opens: str`
    :   One-click lead form opens in viral distribution.

    `viral_one_click_leads: str`
    :   Leads generated in one click in viral distribution.

    `viral_other_engagements: str`
    :   Other engagements in viral distribution of the ad.

    `viral_post_click_job_applications: str`
    :   Job applications initiated post-clicking in viral distribution.

    `viral_post_click_job_apply_clicks: str`
    :   Clicks on apply job button post-clicking in viral distribution.

    `viral_post_click_registrations: str`
    :   Registrations completed post-clicking in viral distribution.

    `viral_post_view_job_applications: str`
    :   Job applications initiated post-viewing in viral distribution.

    `viral_post_view_job_apply_clicks: str`
    :   Clicks on apply job button post-viewing in viral distribution.

    `viral_post_view_registrations: str`
    :   Registrations completed post-viewing in viral distribution.

    `viral_reactions: str`
    :   Total reactions in viral distribution of the ad.

    `viral_registrations: str`
    :   Total registrations in viral distribution of the ad.

    `viral_shares: str`
    :   Total shares in viral distribution of the ad.

    `viral_total_engagements: str`
    :   Total engagements in viral distribution of the ad.

    `viral_video_completions: str`
    :   Completions of videos in viral distribution.

    `viral_video_first_quartile_completions: str`
    :   First quartile completions of videos in viral distribution.

    `viral_video_midpoint_completions: str`
    :   Midpoint completions of videos in viral distribution.

    `viral_video_starts: str`
    :   Total video starts in viral distribution of the ad.

    `viral_video_third_quartile_completions: str`
    :   Third quartile completions of videos in viral distribution.

    `viral_video_views: str`
    :   Total views of videos in viral distribution of the ad.

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

<a id="CampaignConversionsCreateParams"></a>

`CampaignConversionsCreateParams(*args, **kwargs)`
:   Parameters for campaign_conversions.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign: str`
    :   The type of the None singleton.

    `campaign_urn: str`
    :   The type of the None singleton.

    `conversion: str`
    :   The type of the None singleton.

    `conversion_urn: str`
    :   The type of the None singleton.

<a id="CampaignConversionsDeleteParams"></a>

`CampaignConversionsDeleteParams(*args, **kwargs)`
:   Parameters for campaign_conversions.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_urn: str`
    :   The type of the None singleton.

    `conversion_urn: str`
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

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAnyCondition]`
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
    :   The account associated with the campaign group.

    `allowed_campaign_types: Any`
    :   List of campaign types allowed for this campaign group.

    `backfilled: Any`
    :   Indicates if the campaign group was backfilled.

    `created: Any`
    :   The date and time when the campaign group was created.

    `id: Any`
    :   Unique identifier for the campaign group.

    `last_modified: Any`
    :   The date and time when the campaign group was last modified.

    `name: Any`
    :   Name of the campaign group.

    `run_schedule: Any`
    :   Schedule for running the campaign group.

    `serving_statuses: Any`
    :   List of serving statuses for the campaign group.

    `status: Any`
    :   Current status of the campaign group.

    `test: Any`
    :   Indicates if the campaign group is a test campaign.

    `total_budget: Any`
    :   Total budget allocated for the campaign group.

<a id="CampaignGroupsArrayContainsCondition"></a>

`CampaignGroupsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsContainsCondition"></a>

`CampaignGroupsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsCreateParams"></a>

`CampaignGroupsCreateParams(*args, **kwargs)`
:   Parameters for campaign_groups.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   The type of the None singleton.

    `account_id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `objective_type: str`
    :   The type of the None singleton.

    `run_schedule: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsCreateParamsRunschedule`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `total_budget: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsCreateParamsTotalbudget`
    :   The type of the None singleton.

<a id="CampaignGroupsCreateParamsRunschedule"></a>

`CampaignGroupsCreateParamsRunschedule(*args, **kwargs)`
:   Scheduled run window (epoch milliseconds)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `end: int`
    :   The type of the None singleton.

    `start: int`
    :   The type of the None singleton.

<a id="CampaignGroupsCreateParamsTotalbudget"></a>

`CampaignGroupsCreateParamsTotalbudget(*args, **kwargs)`
:   Total budget across the group's lifetime

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   The type of the None singleton.

    `currency_code: str`
    :   The type of the None singleton.

<a id="CampaignGroupsDeleteParams"></a>

`CampaignGroupsDeleteParams(*args, **kwargs)`
:   Parameters for campaign_groups.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

<a id="CampaignGroupsEndswithCondition"></a>

`CampaignGroupsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsStringFilter`
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
    :   The account associated with the campaign group.

    `allowed_campaign_types: list[list[typing.Any]]`
    :   List of campaign types allowed for this campaign group.

    `backfilled: list[bool]`
    :   Indicates if the campaign group was backfilled.

    `created: list[str]`
    :   The date and time when the campaign group was created.

    `id: list[int]`
    :   Unique identifier for the campaign group.

    `last_modified: list[str]`
    :   The date and time when the campaign group was last modified.

    `name: list[str]`
    :   Name of the campaign group.

    `run_schedule: list[dict[str, typing.Any]]`
    :   Schedule for running the campaign group.

    `serving_statuses: list[list[typing.Any]]`
    :   List of serving statuses for the campaign group.

    `status: list[str]`
    :   Current status of the campaign group.

    `test: list[bool]`
    :   Indicates if the campaign group is a test campaign.

    `total_budget: list[dict[str, typing.Any]]`
    :   Total budget allocated for the campaign group.

<a id="CampaignGroupsKeywordCondition"></a>

`CampaignGroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsStringFilter`
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

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignGroupsSearchFilter"></a>

`CampaignGroupsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaign_groups search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str | None`
    :   The account associated with the campaign group.

    `allowed_campaign_types: list[typing.Any] | None`
    :   List of campaign types allowed for this campaign group.

    `backfilled: bool | None`
    :   Indicates if the campaign group was backfilled.

    `created: str | None`
    :   The date and time when the campaign group was created.

    `id: int | None`
    :   Unique identifier for the campaign group.

    `last_modified: str | None`
    :   The date and time when the campaign group was last modified.

    `name: str | None`
    :   Name of the campaign group.

    `run_schedule: dict[str, typing.Any] | None`
    :   Schedule for running the campaign group.

    `serving_statuses: list[typing.Any] | None`
    :   List of serving statuses for the campaign group.

    `status: str | None`
    :   Current status of the campaign group.

    `test: bool | None`
    :   Indicates if the campaign group is a test campaign.

    `total_budget: dict[str, typing.Any] | None`
    :   Total budget allocated for the campaign group.

<a id="CampaignGroupsSearchQuery"></a>

`CampaignGroupsSearchQuery(*args, **kwargs)`
:   Search query for campaign_groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsAnyCondition`
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
    :   The account associated with the campaign group.

    `allowed_campaign_types: Literal['asc', 'desc']`
    :   List of campaign types allowed for this campaign group.

    `backfilled: Literal['asc', 'desc']`
    :   Indicates if the campaign group was backfilled.

    `created: Literal['asc', 'desc']`
    :   The date and time when the campaign group was created.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the campaign group.

    `last_modified: Literal['asc', 'desc']`
    :   The date and time when the campaign group was last modified.

    `name: Literal['asc', 'desc']`
    :   Name of the campaign group.

    `run_schedule: Literal['asc', 'desc']`
    :   Schedule for running the campaign group.

    `serving_statuses: Literal['asc', 'desc']`
    :   List of serving statuses for the campaign group.

    `status: Literal['asc', 'desc']`
    :   Current status of the campaign group.

    `test: Literal['asc', 'desc']`
    :   Indicates if the campaign group is a test campaign.

    `total_budget: Literal['asc', 'desc']`
    :   Total budget allocated for the campaign group.

<a id="CampaignGroupsStartswithCondition"></a>

`CampaignGroupsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsStringFilter`
    :   The type of the None singleton.

<a id="CampaignGroupsStringFilter"></a>

`CampaignGroupsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   The account associated with the campaign group.

    `allowed_campaign_types: str`
    :   List of campaign types allowed for this campaign group.

    `backfilled: str`
    :   Indicates if the campaign group was backfilled.

    `created: str`
    :   The date and time when the campaign group was created.

    `id: str`
    :   Unique identifier for the campaign group.

    `last_modified: str`
    :   The date and time when the campaign group was last modified.

    `name: str`
    :   Name of the campaign group.

    `run_schedule: str`
    :   Schedule for running the campaign group.

    `serving_statuses: str`
    :   List of serving statuses for the campaign group.

    `status: str`
    :   Current status of the campaign group.

    `test: str`
    :   Indicates if the campaign group is a test campaign.

    `total_budget: str`
    :   Total budget allocated for the campaign group.

<a id="CampaignGroupsUpdateParams"></a>

`CampaignGroupsUpdateParams(*args, **kwargs)`
:   Parameters for campaign_groups.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `patch: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignGroupsUpdateParamsPatch`
    :   The type of the None singleton.

<a id="CampaignGroupsUpdateParamsPatch"></a>

`CampaignGroupsUpdateParamsPatch(*args, **kwargs)`
:   Nested schema for CampaignGroupsUpdateParams.patch

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `set_: dict[str, typing.Any]`
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

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAnyCondition]`
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
    :   The account associated with the campaign data.

    `associated_entity: Any`
    :   The entity associated with the campaign.

    `audience_expansion_enabled: Any`
    :   Indicates if audience expansion is enabled for this campaign.

    `campaign_group: Any`
    :   The group to which the campaign belongs.

    `cost_type: Any`
    :   The type of cost associated with the campaign.

    `created: Any`
    :   The date and time when the campaign was created.

    `creative_selection: Any`
    :   Information about the creative selection for the campaign.

    `daily_budget: Any`
    :   The daily budget set for the campaign.

    `format: Any`
    :   The format of the campaign.

    `id: Any`
    :   The unique identifier of the campaign.

    `last_modified: Any`
    :   The date and time when the campaign was last modified.

    `locale: Any`
    :   The locale settings for the campaign.

    `name: Any`
    :   The name of the campaign.

    `objective_type: Any`
    :   The type of objective for the campaign.

    `offsite_delivery_enabled: Any`
    :   Indicates if offsite delivery is enabled for the campaign.

    `offsite_preferences: Any`
    :   Preferences related to offsite delivery.

    `optimization_target_type: Any`
    :   The type of optimization target for the campaign.

    `pacing_strategy: Any`
    :   The pacing strategy for the campaign.

    `run_schedule: Any`
    :   The schedule for running the campaign.

    `serving_statuses: Any`
    :   The serving statuses of the campaign.

    `status: Any`
    :   The status of the campaign.

    `story_delivery_enabled: Any`
    :   Indicates if story delivery is enabled for the campaign.

    `targeting_criteria: Any`
    :   Criteria for targeting in the campaign.

    `test: Any`
    :   Indicates if the campaign is a test campaign.

    `total_budget: Any`
    :   The total budget amount for the campaign.

    `type_: Any`
    :   The type of campaign.

    `unit_cost: Any`
    :   The unit cost for the campaign.

    `version: Any`
    :   The version information for the campaign.

<a id="CampaignsArrayContainsCondition"></a>

`CampaignsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsContainsCondition"></a>

`CampaignsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsCreateParams"></a>

`CampaignsCreateParams(*args, **kwargs)`
:   Parameters for campaigns.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   The type of the None singleton.

    `account_id: str`
    :   The type of the None singleton.

    `audience_expansion_enabled: bool`
    :   The type of the None singleton.

    `campaign_group: str`
    :   The type of the None singleton.

    `cost_type: str`
    :   The type of the None singleton.

    `creative_selection: str`
    :   The type of the None singleton.

    `daily_budget: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsCreateParamsDailybudget`
    :   The type of the None singleton.

    `locale: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsCreateParamsLocale`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `objective_type: str`
    :   The type of the None singleton.

    `offsite_delivery_enabled: bool`
    :   The type of the None singleton.

    `political_intent: str`
    :   The type of the None singleton.

    `run_schedule: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsCreateParamsRunschedule`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `targeting_criteria: dict[str, typing.Any]`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

    `unit_cost: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsCreateParamsUnitcost`
    :   The type of the None singleton.

<a id="CampaignsCreateParamsDailybudget"></a>

`CampaignsCreateParamsDailybudget(*args, **kwargs)`
:   Daily budget

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   The type of the None singleton.

    `currency_code: str`
    :   The type of the None singleton.

<a id="CampaignsCreateParamsLocale"></a>

`CampaignsCreateParamsLocale(*args, **kwargs)`
:   Campaign locale

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country: str`
    :   The type of the None singleton.

    `language: str`
    :   The type of the None singleton.

<a id="CampaignsCreateParamsRunschedule"></a>

`CampaignsCreateParamsRunschedule(*args, **kwargs)`
:   Scheduled run window (epoch milliseconds)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `end: int`
    :   The type of the None singleton.

    `start: int`
    :   The type of the None singleton.

<a id="CampaignsCreateParamsUnitcost"></a>

`CampaignsCreateParamsUnitcost(*args, **kwargs)`
:   Bid amount per unit (per click, per impression, etc.)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   The type of the None singleton.

    `currency_code: str`
    :   The type of the None singleton.

<a id="CampaignsDeleteParams"></a>

`CampaignsDeleteParams(*args, **kwargs)`
:   Parameters for campaigns.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

<a id="CampaignsEndswithCondition"></a>

`CampaignsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsStringFilter`
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
    :   The account associated with the campaign data.

    `associated_entity: list[str]`
    :   The entity associated with the campaign.

    `audience_expansion_enabled: list[bool]`
    :   Indicates if audience expansion is enabled for this campaign.

    `campaign_group: list[str]`
    :   The group to which the campaign belongs.

    `cost_type: list[str]`
    :   The type of cost associated with the campaign.

    `created: list[str]`
    :   The date and time when the campaign was created.

    `creative_selection: list[str]`
    :   Information about the creative selection for the campaign.

    `daily_budget: list[dict[str, typing.Any]]`
    :   The daily budget set for the campaign.

    `format: list[str]`
    :   The format of the campaign.

    `id: list[int]`
    :   The unique identifier of the campaign.

    `last_modified: list[str]`
    :   The date and time when the campaign was last modified.

    `locale: list[dict[str, typing.Any]]`
    :   The locale settings for the campaign.

    `name: list[str]`
    :   The name of the campaign.

    `objective_type: list[str]`
    :   The type of objective for the campaign.

    `offsite_delivery_enabled: list[bool]`
    :   Indicates if offsite delivery is enabled for the campaign.

    `offsite_preferences: list[dict[str, typing.Any]]`
    :   Preferences related to offsite delivery.

    `optimization_target_type: list[str]`
    :   The type of optimization target for the campaign.

    `pacing_strategy: list[str]`
    :   The pacing strategy for the campaign.

    `run_schedule: list[dict[str, typing.Any]]`
    :   The schedule for running the campaign.

    `serving_statuses: list[list[typing.Any]]`
    :   The serving statuses of the campaign.

    `status: list[str]`
    :   The status of the campaign.

    `story_delivery_enabled: list[bool]`
    :   Indicates if story delivery is enabled for the campaign.

    `targeting_criteria: list[dict[str, typing.Any]]`
    :   Criteria for targeting in the campaign.

    `test: list[bool]`
    :   Indicates if the campaign is a test campaign.

    `total_budget: list[dict[str, typing.Any]]`
    :   The total budget amount for the campaign.

    `type_: list[str]`
    :   The type of campaign.

    `unit_cost: list[dict[str, typing.Any]]`
    :   The unit cost for the campaign.

    `version: list[dict[str, typing.Any]]`
    :   The version information for the campaign.

<a id="CampaignsKeywordCondition"></a>

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsStringFilter`
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

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignsSearchFilter"></a>

`CampaignsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaigns search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str | None`
    :   The account associated with the campaign data.

    `associated_entity: str | None`
    :   The entity associated with the campaign.

    `audience_expansion_enabled: bool | None`
    :   Indicates if audience expansion is enabled for this campaign.

    `campaign_group: str | None`
    :   The group to which the campaign belongs.

    `cost_type: str | None`
    :   The type of cost associated with the campaign.

    `created: str | None`
    :   The date and time when the campaign was created.

    `creative_selection: str | None`
    :   Information about the creative selection for the campaign.

    `daily_budget: dict[str, typing.Any] | None`
    :   The daily budget set for the campaign.

    `format: str | None`
    :   The format of the campaign.

    `id: int | None`
    :   The unique identifier of the campaign.

    `last_modified: str | None`
    :   The date and time when the campaign was last modified.

    `locale: dict[str, typing.Any] | None`
    :   The locale settings for the campaign.

    `name: str | None`
    :   The name of the campaign.

    `objective_type: str | None`
    :   The type of objective for the campaign.

    `offsite_delivery_enabled: bool | None`
    :   Indicates if offsite delivery is enabled for the campaign.

    `offsite_preferences: dict[str, typing.Any] | None`
    :   Preferences related to offsite delivery.

    `optimization_target_type: str | None`
    :   The type of optimization target for the campaign.

    `pacing_strategy: str | None`
    :   The pacing strategy for the campaign.

    `run_schedule: dict[str, typing.Any] | None`
    :   The schedule for running the campaign.

    `serving_statuses: list[typing.Any] | None`
    :   The serving statuses of the campaign.

    `status: str | None`
    :   The status of the campaign.

    `story_delivery_enabled: bool | None`
    :   Indicates if story delivery is enabled for the campaign.

    `targeting_criteria: dict[str, typing.Any] | None`
    :   Criteria for targeting in the campaign.

    `test: bool | None`
    :   Indicates if the campaign is a test campaign.

    `total_budget: dict[str, typing.Any] | None`
    :   The total budget amount for the campaign.

    `type_: str | None`
    :   The type of campaign.

    `unit_cost: dict[str, typing.Any] | None`
    :   The unit cost for the campaign.

    `version: dict[str, typing.Any] | None`
    :   The version information for the campaign.

<a id="CampaignsSearchQuery"></a>

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsAnyCondition`
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
    :   The account associated with the campaign data.

    `associated_entity: Literal['asc', 'desc']`
    :   The entity associated with the campaign.

    `audience_expansion_enabled: Literal['asc', 'desc']`
    :   Indicates if audience expansion is enabled for this campaign.

    `campaign_group: Literal['asc', 'desc']`
    :   The group to which the campaign belongs.

    `cost_type: Literal['asc', 'desc']`
    :   The type of cost associated with the campaign.

    `created: Literal['asc', 'desc']`
    :   The date and time when the campaign was created.

    `creative_selection: Literal['asc', 'desc']`
    :   Information about the creative selection for the campaign.

    `daily_budget: Literal['asc', 'desc']`
    :   The daily budget set for the campaign.

    `format: Literal['asc', 'desc']`
    :   The format of the campaign.

    `id: Literal['asc', 'desc']`
    :   The unique identifier of the campaign.

    `last_modified: Literal['asc', 'desc']`
    :   The date and time when the campaign was last modified.

    `locale: Literal['asc', 'desc']`
    :   The locale settings for the campaign.

    `name: Literal['asc', 'desc']`
    :   The name of the campaign.

    `objective_type: Literal['asc', 'desc']`
    :   The type of objective for the campaign.

    `offsite_delivery_enabled: Literal['asc', 'desc']`
    :   Indicates if offsite delivery is enabled for the campaign.

    `offsite_preferences: Literal['asc', 'desc']`
    :   Preferences related to offsite delivery.

    `optimization_target_type: Literal['asc', 'desc']`
    :   The type of optimization target for the campaign.

    `pacing_strategy: Literal['asc', 'desc']`
    :   The pacing strategy for the campaign.

    `run_schedule: Literal['asc', 'desc']`
    :   The schedule for running the campaign.

    `serving_statuses: Literal['asc', 'desc']`
    :   The serving statuses of the campaign.

    `status: Literal['asc', 'desc']`
    :   The status of the campaign.

    `story_delivery_enabled: Literal['asc', 'desc']`
    :   Indicates if story delivery is enabled for the campaign.

    `targeting_criteria: Literal['asc', 'desc']`
    :   Criteria for targeting in the campaign.

    `test: Literal['asc', 'desc']`
    :   Indicates if the campaign is a test campaign.

    `total_budget: Literal['asc', 'desc']`
    :   The total budget amount for the campaign.

    `type_: Literal['asc', 'desc']`
    :   The type of campaign.

    `unit_cost: Literal['asc', 'desc']`
    :   The unit cost for the campaign.

    `version: Literal['asc', 'desc']`
    :   The version information for the campaign.

<a id="CampaignsStartswithCondition"></a>

`CampaignsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsStringFilter"></a>

`CampaignsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   The account associated with the campaign data.

    `associated_entity: str`
    :   The entity associated with the campaign.

    `audience_expansion_enabled: str`
    :   Indicates if audience expansion is enabled for this campaign.

    `campaign_group: str`
    :   The group to which the campaign belongs.

    `cost_type: str`
    :   The type of cost associated with the campaign.

    `created: str`
    :   The date and time when the campaign was created.

    `creative_selection: str`
    :   Information about the creative selection for the campaign.

    `daily_budget: str`
    :   The daily budget set for the campaign.

    `format: str`
    :   The format of the campaign.

    `id: str`
    :   The unique identifier of the campaign.

    `last_modified: str`
    :   The date and time when the campaign was last modified.

    `locale: str`
    :   The locale settings for the campaign.

    `name: str`
    :   The name of the campaign.

    `objective_type: str`
    :   The type of objective for the campaign.

    `offsite_delivery_enabled: str`
    :   Indicates if offsite delivery is enabled for the campaign.

    `offsite_preferences: str`
    :   Preferences related to offsite delivery.

    `optimization_target_type: str`
    :   The type of optimization target for the campaign.

    `pacing_strategy: str`
    :   The pacing strategy for the campaign.

    `run_schedule: str`
    :   The schedule for running the campaign.

    `serving_statuses: str`
    :   The serving statuses of the campaign.

    `status: str`
    :   The status of the campaign.

    `story_delivery_enabled: str`
    :   Indicates if story delivery is enabled for the campaign.

    `targeting_criteria: str`
    :   Criteria for targeting in the campaign.

    `test: str`
    :   Indicates if the campaign is a test campaign.

    `total_budget: str`
    :   The total budget amount for the campaign.

    `type_: str`
    :   The type of campaign.

    `unit_cost: str`
    :   The unit cost for the campaign.

    `version: str`
    :   The version information for the campaign.

<a id="CampaignsUpdateParams"></a>

`CampaignsUpdateParams(*args, **kwargs)`
:   Parameters for campaigns.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `patch: airbyte_agent_sdk.connectors.linkedin_ads.types.CampaignsUpdateParamsPatch`
    :   The type of the None singleton.

<a id="CampaignsUpdateParamsPatch"></a>

`CampaignsUpdateParamsPatch(*args, **kwargs)`
:   Nested schema for CampaignsUpdateParams.patch

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `set_: dict[str, typing.Any]`
    :   The type of the None singleton.

<a id="ConversionEventsCreateParams"></a>

`ConversionEventsCreateParams(*args, **kwargs)`
:   Parameters for conversion_events.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `elements: list[airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionEventsCreateParamsElementsItem]`
    :   The type of the None singleton.

<a id="ConversionEventsCreateParamsElementsItem"></a>

`ConversionEventsCreateParamsElementsItem(*args, **kwargs)`
:   Nested schema for ConversionEventsCreateParams.elements_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `conversion: str`
    :   The type of the None singleton.

    `conversion_happened_at: int`
    :   The type of the None singleton.

    `conversion_value: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionEventsCreateParamsElementsItemConversionvalue`
    :   The type of the None singleton.

    `event_id: str`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionEventsCreateParamsElementsItemUser`
    :   The type of the None singleton.

<a id="ConversionEventsCreateParamsElementsItemConversionvalue"></a>

`ConversionEventsCreateParamsElementsItemConversionvalue(*args, **kwargs)`
:   Monetary value of this conversion

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   The type of the None singleton.

    `currency_code: str`
    :   The type of the None singleton.

<a id="ConversionEventsCreateParamsElementsItemUser"></a>

`ConversionEventsCreateParamsElementsItemUser(*args, **kwargs)`
:   Identifies the converting user (hashed email or other supported ID types)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `user_ids: list[airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionEventsCreateParamsElementsItemUserUseridsItem]`
    :   The type of the None singleton.

    `user_info: dict[str, typing.Any]`
    :   The type of the None singleton.

<a id="ConversionEventsCreateParamsElementsItemUserUseridsItem"></a>

`ConversionEventsCreateParamsElementsItemUserUseridsItem(*args, **kwargs)`
:   Nested schema for ConversionEventsCreateParamsElementsItemUser.userIds_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id_type: str`
    :   The type of the None singleton.

    `id_value: str`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAnyCondition]`
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
    :   The account associated with the conversion data.

    `associated_campaigns: Any`
    :   Campaigns associated with the conversion.

    `attribution_type: Any`
    :   The type of attribution for the conversion.

    `campaigns: Any`
    :   List of campaigns related to the conversion.

    `created: Any`
    :   Timestamp of when the conversion was created.

    `enabled: Any`
    :   Flag indicating if the conversion tracking is enabled.

    `id: Any`
    :   Unique identifier for the conversion.

    `image_pixel_tag: Any`
    :   Pixel tag used for tracking the conversion.

    `last_callback_at: Any`
    :   Timestamp of the last callback for the conversion.

    `last_modified: Any`
    :   Timestamp of the last modification made to the conversion.

    `latest_first_party_callback_at: Any`
    :   Timestamp of the latest first-party callback for the conversion.

    `name: Any`
    :   Name of the conversion.

    `post_click_attribution_window_size: Any`
    :   Window size for post-click attribution.

    `type_: Any`
    :   Type of conversion.

    `url_match_rule_expression: Any`
    :   Expression used for matching URLs for attribution.

    `url_rules: Any`
    :   Rules for URL matching in the conversion.

    `value: Any`
    :   Value associated with the conversion.

    `view_through_attribution_window_size: Any`
    :   Window size for view-through attribution.

<a id="ConversionsArrayContainsCondition"></a>

`ConversionsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAnyValueFilter`
    :   The type of the None singleton.

<a id="ConversionsContainsCondition"></a>

`ConversionsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAnyValueFilter`
    :   The type of the None singleton.

<a id="ConversionsCreateParams"></a>

`ConversionsCreateParams(*args, **kwargs)`
:   Parameters for conversions.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   The type of the None singleton.

    `attribution_type: str`
    :   The type of the None singleton.

    `auto_association_type: str`
    :   The type of the None singleton.

    `enabled: bool`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `post_click_attribution_window_size: int`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

    `url_match_rule_expression: list[list[dict[str, typing.Any]]]`
    :   The type of the None singleton.

    `value: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsCreateParamsValue`
    :   The type of the None singleton.

    `view_through_attribution_window_size: int`
    :   The type of the None singleton.

<a id="ConversionsCreateParamsValue"></a>

`ConversionsCreateParamsValue(*args, **kwargs)`
:   Monetary value assigned to each conversion

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   The type of the None singleton.

    `currency_code: str`
    :   The type of the None singleton.

<a id="ConversionsEndswithCondition"></a>

`ConversionsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsStringFilter`
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
    :   The account associated with the conversion data.

    `associated_campaigns: list[list[typing.Any]]`
    :   Campaigns associated with the conversion.

    `attribution_type: list[str]`
    :   The type of attribution for the conversion.

    `campaigns: list[list[typing.Any]]`
    :   List of campaigns related to the conversion.

    `created: list[int]`
    :   Timestamp of when the conversion was created.

    `enabled: list[bool]`
    :   Flag indicating if the conversion tracking is enabled.

    `id: list[int]`
    :   Unique identifier for the conversion.

    `image_pixel_tag: list[str]`
    :   Pixel tag used for tracking the conversion.

    `last_callback_at: list[int]`
    :   Timestamp of the last callback for the conversion.

    `last_modified: list[int]`
    :   Timestamp of the last modification made to the conversion.

    `latest_first_party_callback_at: list[int]`
    :   Timestamp of the latest first-party callback for the conversion.

    `name: list[str]`
    :   Name of the conversion.

    `post_click_attribution_window_size: list[int]`
    :   Window size for post-click attribution.

    `type_: list[str]`
    :   Type of conversion.

    `url_match_rule_expression: list[list[typing.Any]]`
    :   Expression used for matching URLs for attribution.

    `url_rules: list[list[typing.Any]]`
    :   Rules for URL matching in the conversion.

    `value: list[dict[str, typing.Any]]`
    :   Value associated with the conversion.

    `view_through_attribution_window_size: list[int]`
    :   Window size for view-through attribution.

<a id="ConversionsKeywordCondition"></a>

`ConversionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsStringFilter`
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

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAnyCondition]`
    :   The type of the None singleton.

<a id="ConversionsSearchFilter"></a>

`ConversionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering conversions search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str | None`
    :   The account associated with the conversion data.

    `associated_campaigns: list[typing.Any] | None`
    :   Campaigns associated with the conversion.

    `attribution_type: str | None`
    :   The type of attribution for the conversion.

    `campaigns: list[typing.Any] | None`
    :   List of campaigns related to the conversion.

    `created: int | None`
    :   Timestamp of when the conversion was created.

    `enabled: bool | None`
    :   Flag indicating if the conversion tracking is enabled.

    `id: int | None`
    :   Unique identifier for the conversion.

    `image_pixel_tag: str | None`
    :   Pixel tag used for tracking the conversion.

    `last_callback_at: int | None`
    :   Timestamp of the last callback for the conversion.

    `last_modified: int | None`
    :   Timestamp of the last modification made to the conversion.

    `latest_first_party_callback_at: int | None`
    :   Timestamp of the latest first-party callback for the conversion.

    `name: str | None`
    :   Name of the conversion.

    `post_click_attribution_window_size: int | None`
    :   Window size for post-click attribution.

    `type_: str | None`
    :   Type of conversion.

    `url_match_rule_expression: list[typing.Any] | None`
    :   Expression used for matching URLs for attribution.

    `url_rules: list[typing.Any] | None`
    :   Rules for URL matching in the conversion.

    `value: dict[str, typing.Any] | None`
    :   Value associated with the conversion.

    `view_through_attribution_window_size: int | None`
    :   Window size for view-through attribution.

<a id="ConversionsSearchQuery"></a>

`ConversionsSearchQuery(*args, **kwargs)`
:   Search query for conversions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsAnyCondition`
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
    :   The account associated with the conversion data.

    `associated_campaigns: Literal['asc', 'desc']`
    :   Campaigns associated with the conversion.

    `attribution_type: Literal['asc', 'desc']`
    :   The type of attribution for the conversion.

    `campaigns: Literal['asc', 'desc']`
    :   List of campaigns related to the conversion.

    `created: Literal['asc', 'desc']`
    :   Timestamp of when the conversion was created.

    `enabled: Literal['asc', 'desc']`
    :   Flag indicating if the conversion tracking is enabled.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the conversion.

    `image_pixel_tag: Literal['asc', 'desc']`
    :   Pixel tag used for tracking the conversion.

    `last_callback_at: Literal['asc', 'desc']`
    :   Timestamp of the last callback for the conversion.

    `last_modified: Literal['asc', 'desc']`
    :   Timestamp of the last modification made to the conversion.

    `latest_first_party_callback_at: Literal['asc', 'desc']`
    :   Timestamp of the latest first-party callback for the conversion.

    `name: Literal['asc', 'desc']`
    :   Name of the conversion.

    `post_click_attribution_window_size: Literal['asc', 'desc']`
    :   Window size for post-click attribution.

    `type_: Literal['asc', 'desc']`
    :   Type of conversion.

    `url_match_rule_expression: Literal['asc', 'desc']`
    :   Expression used for matching URLs for attribution.

    `url_rules: Literal['asc', 'desc']`
    :   Rules for URL matching in the conversion.

    `value: Literal['asc', 'desc']`
    :   Value associated with the conversion.

    `view_through_attribution_window_size: Literal['asc', 'desc']`
    :   Window size for view-through attribution.

<a id="ConversionsStartswithCondition"></a>

`ConversionsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsStringFilter`
    :   The type of the None singleton.

<a id="ConversionsStringFilter"></a>

`ConversionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   The account associated with the conversion data.

    `associated_campaigns: str`
    :   Campaigns associated with the conversion.

    `attribution_type: str`
    :   The type of attribution for the conversion.

    `campaigns: str`
    :   List of campaigns related to the conversion.

    `created: str`
    :   Timestamp of when the conversion was created.

    `enabled: str`
    :   Flag indicating if the conversion tracking is enabled.

    `id: str`
    :   Unique identifier for the conversion.

    `image_pixel_tag: str`
    :   Pixel tag used for tracking the conversion.

    `last_callback_at: str`
    :   Timestamp of the last callback for the conversion.

    `last_modified: str`
    :   Timestamp of the last modification made to the conversion.

    `latest_first_party_callback_at: str`
    :   Timestamp of the latest first-party callback for the conversion.

    `name: str`
    :   Name of the conversion.

    `post_click_attribution_window_size: str`
    :   Window size for post-click attribution.

    `type_: str`
    :   Type of conversion.

    `url_match_rule_expression: str`
    :   Expression used for matching URLs for attribution.

    `url_rules: str`
    :   Rules for URL matching in the conversion.

    `value: str`
    :   Value associated with the conversion.

    `view_through_attribution_window_size: str`
    :   Window size for view-through attribution.

<a id="ConversionsUpdateParams"></a>

`ConversionsUpdateParams(*args, **kwargs)`
:   Parameters for conversions.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `patch: airbyte_agent_sdk.connectors.linkedin_ads.types.ConversionsUpdateParamsPatch`
    :   The type of the None singleton.

<a id="ConversionsUpdateParamsPatch"></a>

`ConversionsUpdateParamsPatch(*args, **kwargs)`
:   Nested schema for ConversionsUpdateParams.patch

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `set_: dict[str, typing.Any]`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAnyCondition]`
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
    :   The account associated with the creative.

    `campaign: Any`
    :   The campaign to which the creative belongs.

    `content: Any`
    :   The actual content of the creative.

    `created_at: Any`
    :   The timestamp when the creative was created.

    `created_by: Any`
    :   The user who created the creative.

    `id: Any`
    :   The unique identifier of the creative.

    `intended_status: Any`
    :   The intended status of the creative.

    `is_serving: Any`
    :   Boolean indicating if the creative is currently serving.

    `is_test: Any`
    :   Boolean indicating if the creative is a test creative.

    `last_modified_at: Any`
    :   The timestamp when the creative was last modified.

    `last_modified_by: Any`
    :   The user who last modified the creative.

    `leadgen_call_to_action: Any`
    :   Call-to-action information for lead generation purposes.

    `name: Any`
    :   The name of the creative.

    `review: Any`
    :   Review information for the creative.

    `serving_hold_reasons: Any`
    :   Reasons for holding the creative from serving.

<a id="CreativesArrayContainsCondition"></a>

`CreativesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAnyValueFilter`
    :   The type of the None singleton.

<a id="CreativesContainsCondition"></a>

`CreativesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAnyValueFilter`
    :   The type of the None singleton.

<a id="CreativesCreateParams"></a>

`CreativesCreateParams(*args, **kwargs)`
:   Parameters for creatives.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `campaign: str`
    :   The type of the None singleton.

    `content: dict[str, typing.Any]`
    :   The type of the None singleton.

    `intended_status: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="CreativesDeleteParams"></a>

`CreativesDeleteParams(*args, **kwargs)`
:   Parameters for creatives.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

<a id="CreativesEndswithCondition"></a>

`CreativesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesStringFilter`
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
    :   The account associated with the creative.

    `campaign: list[str]`
    :   The campaign to which the creative belongs.

    `content: list[dict[str, typing.Any]]`
    :   The actual content of the creative.

    `created_at: list[int]`
    :   The timestamp when the creative was created.

    `created_by: list[str]`
    :   The user who created the creative.

    `id: list[str]`
    :   The unique identifier of the creative.

    `intended_status: list[str]`
    :   The intended status of the creative.

    `is_serving: list[bool]`
    :   Boolean indicating if the creative is currently serving.

    `is_test: list[bool]`
    :   Boolean indicating if the creative is a test creative.

    `last_modified_at: list[int]`
    :   The timestamp when the creative was last modified.

    `last_modified_by: list[str]`
    :   The user who last modified the creative.

    `leadgen_call_to_action: list[dict[str, typing.Any]]`
    :   Call-to-action information for lead generation purposes.

    `name: list[str]`
    :   The name of the creative.

    `review: list[dict[str, typing.Any]]`
    :   Review information for the creative.

    `serving_hold_reasons: list[list[typing.Any]]`
    :   Reasons for holding the creative from serving.

<a id="CreativesKeywordCondition"></a>

`CreativesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesStringFilter`
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

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAnyCondition]`
    :   The type of the None singleton.

<a id="CreativesSearchFilter"></a>

`CreativesSearchFilter(*args, **kwargs)`
:   Available fields for filtering creatives search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str | None`
    :   The account associated with the creative.

    `campaign: str | None`
    :   The campaign to which the creative belongs.

    `content: dict[str, typing.Any] | None`
    :   The actual content of the creative.

    `created_at: int | None`
    :   The timestamp when the creative was created.

    `created_by: str | None`
    :   The user who created the creative.

    `id: str | None`
    :   The unique identifier of the creative.

    `intended_status: str | None`
    :   The intended status of the creative.

    `is_serving: bool | None`
    :   Boolean indicating if the creative is currently serving.

    `is_test: bool | None`
    :   Boolean indicating if the creative is a test creative.

    `last_modified_at: int | None`
    :   The timestamp when the creative was last modified.

    `last_modified_by: str | None`
    :   The user who last modified the creative.

    `leadgen_call_to_action: dict[str, typing.Any] | None`
    :   Call-to-action information for lead generation purposes.

    `name: str | None`
    :   The name of the creative.

    `review: dict[str, typing.Any] | None`
    :   Review information for the creative.

    `serving_hold_reasons: list[typing.Any] | None`
    :   Reasons for holding the creative from serving.

<a id="CreativesSearchQuery"></a>

`CreativesSearchQuery(*args, **kwargs)`
:   Search query for creatives entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesAnyCondition`
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
    :   The account associated with the creative.

    `campaign: Literal['asc', 'desc']`
    :   The campaign to which the creative belongs.

    `content: Literal['asc', 'desc']`
    :   The actual content of the creative.

    `created_at: Literal['asc', 'desc']`
    :   The timestamp when the creative was created.

    `created_by: Literal['asc', 'desc']`
    :   The user who created the creative.

    `id: Literal['asc', 'desc']`
    :   The unique identifier of the creative.

    `intended_status: Literal['asc', 'desc']`
    :   The intended status of the creative.

    `is_serving: Literal['asc', 'desc']`
    :   Boolean indicating if the creative is currently serving.

    `is_test: Literal['asc', 'desc']`
    :   Boolean indicating if the creative is a test creative.

    `last_modified_at: Literal['asc', 'desc']`
    :   The timestamp when the creative was last modified.

    `last_modified_by: Literal['asc', 'desc']`
    :   The user who last modified the creative.

    `leadgen_call_to_action: Literal['asc', 'desc']`
    :   Call-to-action information for lead generation purposes.

    `name: Literal['asc', 'desc']`
    :   The name of the creative.

    `review: Literal['asc', 'desc']`
    :   Review information for the creative.

    `serving_hold_reasons: Literal['asc', 'desc']`
    :   Reasons for holding the creative from serving.

<a id="CreativesStartswithCondition"></a>

`CreativesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesStringFilter`
    :   The type of the None singleton.

<a id="CreativesStringFilter"></a>

`CreativesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account: str`
    :   The account associated with the creative.

    `campaign: str`
    :   The campaign to which the creative belongs.

    `content: str`
    :   The actual content of the creative.

    `created_at: str`
    :   The timestamp when the creative was created.

    `created_by: str`
    :   The user who created the creative.

    `id: str`
    :   The unique identifier of the creative.

    `intended_status: str`
    :   The intended status of the creative.

    `is_serving: str`
    :   Boolean indicating if the creative is currently serving.

    `is_test: str`
    :   Boolean indicating if the creative is a test creative.

    `last_modified_at: str`
    :   The timestamp when the creative was last modified.

    `last_modified_by: str`
    :   The user who last modified the creative.

    `leadgen_call_to_action: str`
    :   Call-to-action information for lead generation purposes.

    `name: str`
    :   The name of the creative.

    `review: str`
    :   Review information for the creative.

    `serving_hold_reasons: str`
    :   Reasons for holding the creative from serving.

<a id="CreativesUpdateParams"></a>

`CreativesUpdateParams(*args, **kwargs)`
:   Parameters for creatives.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `patch: airbyte_agent_sdk.connectors.linkedin_ads.types.CreativesUpdateParamsPatch`
    :   The type of the None singleton.

<a id="CreativesUpdateParamsPatch"></a>

`CreativesUpdateParamsPatch(*args, **kwargs)`
:   Nested schema for CreativesUpdateParams.patch

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `set_: dict[str, typing.Any]`
    :   The type of the None singleton.

<a id="LeadFormResponsesAndCondition"></a>

`LeadFormResponsesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesAnyCondition]`
    :   The type of the None singleton.

<a id="LeadFormResponsesAnyCondition"></a>

`LeadFormResponsesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesAnyValueFilter`
    :   The type of the None singleton.

<a id="LeadFormResponsesAnyValueFilter"></a>

`LeadFormResponsesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associated_entity: Any`
    :   URN identifying which entity the lead is associated with. This field is optional for test leads and other use cases where leads don't have any associatedEntity. If there is no value, the field is not returned.

    `associated_entity_info: Any`
    :   Record containing useful fields (creative status, ugc reference etc.) resolved on demand from the associated entity object. If there is no value, an empty object is returned.

    `form: Any`
    :   URN identifying which form this FormResponse belongs to.

    `form_response: Any`
    :   Answers provided by the form submitter.

    `id: Any`
    :   Unique id to identify the Lead Form Response.

    `lead_metadata: Any`
    :   Metadata of a lead. This field is optional for test leads and other use cases where sponsored lead metadata (e.g. campaign) may not be relevant. If there is no value, the field is not returned.

    `lead_metadata_info: Any`
    :   Record containing a subset of fields resolved on demand from the lead metadata references (e.g. campaign name , campaign type). If there is no value, an empty object is returned.

    `lead_type: Any`
    :   Type of the lead representing the origination of the lead.

    `owner: Any`
    :   Owner of this Lead Form Response.
        It is a Union of sponsoredAccount and organization.
        sponsoredAccount is an URN of SponsoredAccountUrn that indicates the ad account of the advertiser.
        organization is an URN of OrganizationUrn that indicates the company page of the advertiser.

    `owner_info: Any`
    :   Record containing entity info that owns this Lead Form Response. It's a optional Union of sponsoredAccountInfo and organizationInfo.

    `response_id: Any`
    :   The unique identifier for the form response generated in the front-end when a submitter submits the response.

    `submitted_at: Any`
    :   An epoch timestamp that recording when the form response was submitted.

    `submitter: Any`
    :   From version 202408 onwards, Guest Leads (when a user submits a form without being logged in) submitted to lead forms, submitter field is treated as a null field and omitted from the JSON response.
        For non-guest leads, the submitter field will still be included in the response and will provide the person's URN. Ex: "submitter": "urn:li:person:MpGcnvaU_p". Yes

    `test_lead: Any`
    :   Whether this is a test lead created for testing purposes.

    `versioned_lead_gen_form_urn: Any`
    :   URN identifying which form this FormResponse belongs to.

<a id="LeadFormResponsesArrayContainsCondition"></a>

`LeadFormResponsesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesAnyValueFilter`
    :   The type of the None singleton.

<a id="LeadFormResponsesContainsCondition"></a>

`LeadFormResponsesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesAnyValueFilter`
    :   The type of the None singleton.

<a id="LeadFormResponsesEndswithCondition"></a>

`LeadFormResponsesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesStringFilter`
    :   The type of the None singleton.

<a id="LeadFormResponsesEqCondition"></a>

`LeadFormResponsesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesSearchFilter`
    :   The type of the None singleton.

<a id="LeadFormResponsesFuzzyCondition"></a>

`LeadFormResponsesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesStringFilter`
    :   The type of the None singleton.

<a id="LeadFormResponsesGtCondition"></a>

`LeadFormResponsesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesSearchFilter`
    :   The type of the None singleton.

<a id="LeadFormResponsesGteCondition"></a>

`LeadFormResponsesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesSearchFilter`
    :   The type of the None singleton.

<a id="LeadFormResponsesInCondition"></a>

`LeadFormResponsesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesInFilter`
    :   The type of the None singleton.

<a id="LeadFormResponsesInFilter"></a>

`LeadFormResponsesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associated_entity: list[dict[str, typing.Any]]`
    :   URN identifying which entity the lead is associated with. This field is optional for test leads and other use cases where leads don't have any associatedEntity. If there is no value, the field is not returned.

    `associated_entity_info: list[dict[str, typing.Any]]`
    :   Record containing useful fields (creative status, ugc reference etc.) resolved on demand from the associated entity object. If there is no value, an empty object is returned.

    `form: list[dict[str, typing.Any]]`
    :   URN identifying which form this FormResponse belongs to.

    `form_response: list[dict[str, typing.Any]]`
    :   Answers provided by the form submitter.

    `id: list[str]`
    :   Unique id to identify the Lead Form Response.

    `lead_metadata: list[dict[str, typing.Any]]`
    :   Metadata of a lead. This field is optional for test leads and other use cases where sponsored lead metadata (e.g. campaign) may not be relevant. If there is no value, the field is not returned.

    `lead_metadata_info: list[dict[str, typing.Any]]`
    :   Record containing a subset of fields resolved on demand from the lead metadata references (e.g. campaign name , campaign type). If there is no value, an empty object is returned.

    `lead_type: list[str]`
    :   Type of the lead representing the origination of the lead.

    `owner: list[dict[str, typing.Any]]`
    :   Owner of this Lead Form Response.
        It is a Union of sponsoredAccount and organization.
        sponsoredAccount is an URN of SponsoredAccountUrn that indicates the ad account of the advertiser.
        organization is an URN of OrganizationUrn that indicates the company page of the advertiser.

    `owner_info: list[dict[str, typing.Any]]`
    :   Record containing entity info that owns this Lead Form Response. It's a optional Union of sponsoredAccountInfo and organizationInfo.

    `response_id: list[dict[str, typing.Any]]`
    :   The unique identifier for the form response generated in the front-end when a submitter submits the response.

    `submitted_at: list[int]`
    :   An epoch timestamp that recording when the form response was submitted.

    `submitter: list[str]`
    :   From version 202408 onwards, Guest Leads (when a user submits a form without being logged in) submitted to lead forms, submitter field is treated as a null field and omitted from the JSON response.
        For non-guest leads, the submitter field will still be included in the response and will provide the person's URN. Ex: "submitter": "urn:li:person:MpGcnvaU_p". Yes

    `test_lead: list[bool]`
    :   Whether this is a test lead created for testing purposes.

    `versioned_lead_gen_form_urn: list[str]`
    :   URN identifying which form this FormResponse belongs to.

<a id="LeadFormResponsesKeywordCondition"></a>

`LeadFormResponsesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesStringFilter`
    :   The type of the None singleton.

<a id="LeadFormResponsesListParams"></a>

`LeadFormResponsesListParams(*args, **kwargs)`
:   Parameters for lead_form_responses.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: int`
    :   The type of the None singleton.

    `lead_type: str`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

    `start: int`
    :   The type of the None singleton.

<a id="LeadFormResponsesLtCondition"></a>

`LeadFormResponsesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesSearchFilter`
    :   The type of the None singleton.

<a id="LeadFormResponsesLteCondition"></a>

`LeadFormResponsesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesSearchFilter`
    :   The type of the None singleton.

<a id="LeadFormResponsesNeqCondition"></a>

`LeadFormResponsesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesSearchFilter`
    :   The type of the None singleton.

<a id="LeadFormResponsesNotCondition"></a>

`LeadFormResponsesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesAnyCondition`
    :   The type of the None singleton.

<a id="LeadFormResponsesOrCondition"></a>

`LeadFormResponsesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesAnyCondition]`
    :   The type of the None singleton.

<a id="LeadFormResponsesSearchFilter"></a>

`LeadFormResponsesSearchFilter(*args, **kwargs)`
:   Available fields for filtering lead_form_responses search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associated_entity: dict[str, typing.Any] | None`
    :   URN identifying which entity the lead is associated with. This field is optional for test leads and other use cases where leads don't have any associatedEntity. If there is no value, the field is not returned.

    `associated_entity_info: dict[str, typing.Any] | None`
    :   Record containing useful fields (creative status, ugc reference etc.) resolved on demand from the associated entity object. If there is no value, an empty object is returned.

    `form: dict[str, typing.Any] | None`
    :   URN identifying which form this FormResponse belongs to.

    `form_response: dict[str, typing.Any] | None`
    :   Answers provided by the form submitter.

    `id: str | None`
    :   Unique id to identify the Lead Form Response.

    `lead_metadata: dict[str, typing.Any] | None`
    :   Metadata of a lead. This field is optional for test leads and other use cases where sponsored lead metadata (e.g. campaign) may not be relevant. If there is no value, the field is not returned.

    `lead_metadata_info: dict[str, typing.Any] | None`
    :   Record containing a subset of fields resolved on demand from the lead metadata references (e.g. campaign name , campaign type). If there is no value, an empty object is returned.

    `lead_type: str | None`
    :   Type of the lead representing the origination of the lead.

    `owner: dict[str, typing.Any] | None`
    :   Owner of this Lead Form Response.
        It is a Union of sponsoredAccount and organization.
        sponsoredAccount is an URN of SponsoredAccountUrn that indicates the ad account of the advertiser.
        organization is an URN of OrganizationUrn that indicates the company page of the advertiser.

    `owner_info: dict[str, typing.Any] | None`
    :   Record containing entity info that owns this Lead Form Response. It's a optional Union of sponsoredAccountInfo and organizationInfo.

    `response_id: dict[str, typing.Any] | None`
    :   The unique identifier for the form response generated in the front-end when a submitter submits the response.

    `submitted_at: int | None`
    :   An epoch timestamp that recording when the form response was submitted.

    `submitter: str | None`
    :   From version 202408 onwards, Guest Leads (when a user submits a form without being logged in) submitted to lead forms, submitter field is treated as a null field and omitted from the JSON response.
        For non-guest leads, the submitter field will still be included in the response and will provide the person's URN. Ex: "submitter": "urn:li:person:MpGcnvaU_p". Yes

    `test_lead: bool | None`
    :   Whether this is a test lead created for testing purposes.

    `versioned_lead_gen_form_urn: str | None`
    :   URN identifying which form this FormResponse belongs to.

<a id="LeadFormResponsesSearchQuery"></a>

`LeadFormResponsesSearchQuery(*args, **kwargs)`
:   Search query for lead_form_responses entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesSortFilter]`
    :   The type of the None singleton.

<a id="LeadFormResponsesSortFilter"></a>

`LeadFormResponsesSortFilter(*args, **kwargs)`
:   Available fields for sorting lead_form_responses search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associated_entity: Literal['asc', 'desc']`
    :   URN identifying which entity the lead is associated with. This field is optional for test leads and other use cases where leads don't have any associatedEntity. If there is no value, the field is not returned.

    `associated_entity_info: Literal['asc', 'desc']`
    :   Record containing useful fields (creative status, ugc reference etc.) resolved on demand from the associated entity object. If there is no value, an empty object is returned.

    `form: Literal['asc', 'desc']`
    :   URN identifying which form this FormResponse belongs to.

    `form_response: Literal['asc', 'desc']`
    :   Answers provided by the form submitter.

    `id: Literal['asc', 'desc']`
    :   Unique id to identify the Lead Form Response.

    `lead_metadata: Literal['asc', 'desc']`
    :   Metadata of a lead. This field is optional for test leads and other use cases where sponsored lead metadata (e.g. campaign) may not be relevant. If there is no value, the field is not returned.

    `lead_metadata_info: Literal['asc', 'desc']`
    :   Record containing a subset of fields resolved on demand from the lead metadata references (e.g. campaign name , campaign type). If there is no value, an empty object is returned.

    `lead_type: Literal['asc', 'desc']`
    :   Type of the lead representing the origination of the lead.

    `owner: Literal['asc', 'desc']`
    :   Owner of this Lead Form Response.
        It is a Union of sponsoredAccount and organization.
        sponsoredAccount is an URN of SponsoredAccountUrn that indicates the ad account of the advertiser.
        organization is an URN of OrganizationUrn that indicates the company page of the advertiser.

    `owner_info: Literal['asc', 'desc']`
    :   Record containing entity info that owns this Lead Form Response. It's a optional Union of sponsoredAccountInfo and organizationInfo.

    `response_id: Literal['asc', 'desc']`
    :   The unique identifier for the form response generated in the front-end when a submitter submits the response.

    `submitted_at: Literal['asc', 'desc']`
    :   An epoch timestamp that recording when the form response was submitted.

    `submitter: Literal['asc', 'desc']`
    :   From version 202408 onwards, Guest Leads (when a user submits a form without being logged in) submitted to lead forms, submitter field is treated as a null field and omitted from the JSON response.
        For non-guest leads, the submitter field will still be included in the response and will provide the person's URN. Ex: "submitter": "urn:li:person:MpGcnvaU_p". Yes

    `test_lead: Literal['asc', 'desc']`
    :   Whether this is a test lead created for testing purposes.

    `versioned_lead_gen_form_urn: Literal['asc', 'desc']`
    :   URN identifying which form this FormResponse belongs to.

<a id="LeadFormResponsesStartswithCondition"></a>

`LeadFormResponsesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormResponsesStringFilter`
    :   The type of the None singleton.

<a id="LeadFormResponsesStringFilter"></a>

`LeadFormResponsesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associated_entity: str`
    :   URN identifying which entity the lead is associated with. This field is optional for test leads and other use cases where leads don't have any associatedEntity. If there is no value, the field is not returned.

    `associated_entity_info: str`
    :   Record containing useful fields (creative status, ugc reference etc.) resolved on demand from the associated entity object. If there is no value, an empty object is returned.

    `form: str`
    :   URN identifying which form this FormResponse belongs to.

    `form_response: str`
    :   Answers provided by the form submitter.

    `id: str`
    :   Unique id to identify the Lead Form Response.

    `lead_metadata: str`
    :   Metadata of a lead. This field is optional for test leads and other use cases where sponsored lead metadata (e.g. campaign) may not be relevant. If there is no value, the field is not returned.

    `lead_metadata_info: str`
    :   Record containing a subset of fields resolved on demand from the lead metadata references (e.g. campaign name , campaign type). If there is no value, an empty object is returned.

    `lead_type: str`
    :   Type of the lead representing the origination of the lead.

    `owner: str`
    :   Owner of this Lead Form Response.
        It is a Union of sponsoredAccount and organization.
        sponsoredAccount is an URN of SponsoredAccountUrn that indicates the ad account of the advertiser.
        organization is an URN of OrganizationUrn that indicates the company page of the advertiser.

    `owner_info: str`
    :   Record containing entity info that owns this Lead Form Response. It's a optional Union of sponsoredAccountInfo and organizationInfo.

    `response_id: str`
    :   The unique identifier for the form response generated in the front-end when a submitter submits the response.

    `submitted_at: str`
    :   An epoch timestamp that recording when the form response was submitted.

    `submitter: str`
    :   From version 202408 onwards, Guest Leads (when a user submits a form without being logged in) submitted to lead forms, submitter field is treated as a null field and omitted from the JSON response.
        For non-guest leads, the submitter field will still be included in the response and will provide the person's URN. Ex: "submitter": "urn:li:person:MpGcnvaU_p". Yes

    `test_lead: str`
    :   Whether this is a test lead created for testing purposes.

    `versioned_lead_gen_form_urn: str`
    :   URN identifying which form this FormResponse belongs to.

<a id="LeadFormsAndCondition"></a>

`LeadFormsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsAnyCondition]`
    :   The type of the None singleton.

<a id="LeadFormsAnyCondition"></a>

`LeadFormsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsAnyValueFilter`
    :   The type of the None singleton.

<a id="LeadFormsAnyValueFilter"></a>

`LeadFormsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: Any`
    :   Content of the Lead Form which will be displayed to the viewer.

    `created: Any`
    :   An epoch time corresponding to the creation of the form.

    `creation_locale: Any`
    :   Locale of the entity.
        This field serves as the preferred locale for all fields within the Lead Form with an object type that is capable of localization, such as MultiLocaleString.

    `hidden_fields: Any`
    :   Hidden fields used by the owner to track key attributes of the form that generated the lead.
        The field is empty if the owner chooses to not append any tracking attributes to the Lead Form.

    `id: Any`
    :   Numerical identifier for the form.

    `last_modified: Any`
    :   An epoch time corresponding to the last modified of of the form.

    `name: Any`
    :   Name of the Lead Form provided by the owner.

    `owner: Any`
    :   URN that identifies the owner of the Lead Form.
        It's a Union of sponsoredAccount and organization.
        sponsoredAccount is an URN of SponsoredAccountUrn that indicates the account of the advertiser.
        organization is an URN of OrganizationUrn that indicates the company account of the marketer.

    `review_info: Any`
    :   Latest information about the content review of the Lead Form.
        It will not be present if the form has not been reviewed by the review pipeline.

    `state: Any`
    :   Information about the current state of the Lead Form.

    `version_id: Any`
    :   The version ID of the form. This is a derived field and is generated on the server side.

    `version_tag: Any`
    :   The number of times the form has been modified.

<a id="LeadFormsArrayContainsCondition"></a>

`LeadFormsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsAnyValueFilter`
    :   The type of the None singleton.

<a id="LeadFormsContainsCondition"></a>

`LeadFormsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsAnyValueFilter`
    :   The type of the None singleton.

<a id="LeadFormsEndswithCondition"></a>

`LeadFormsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsStringFilter`
    :   The type of the None singleton.

<a id="LeadFormsEqCondition"></a>

`LeadFormsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsSearchFilter`
    :   The type of the None singleton.

<a id="LeadFormsFuzzyCondition"></a>

`LeadFormsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsStringFilter`
    :   The type of the None singleton.

<a id="LeadFormsGtCondition"></a>

`LeadFormsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsSearchFilter`
    :   The type of the None singleton.

<a id="LeadFormsGteCondition"></a>

`LeadFormsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsSearchFilter`
    :   The type of the None singleton.

<a id="LeadFormsInCondition"></a>

`LeadFormsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsInFilter`
    :   The type of the None singleton.

<a id="LeadFormsInFilter"></a>

`LeadFormsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: list[dict[str, typing.Any]]`
    :   Content of the Lead Form which will be displayed to the viewer.

    `created: list[int]`
    :   An epoch time corresponding to the creation of the form.

    `creation_locale: list[dict[str, typing.Any]]`
    :   Locale of the entity.
        This field serves as the preferred locale for all fields within the Lead Form with an object type that is capable of localization, such as MultiLocaleString.

    `hidden_fields: list[list[typing.Any]]`
    :   Hidden fields used by the owner to track key attributes of the form that generated the lead.
        The field is empty if the owner chooses to not append any tracking attributes to the Lead Form.

    `id: list[int]`
    :   Numerical identifier for the form.

    `last_modified: list[int]`
    :   An epoch time corresponding to the last modified of of the form.

    `name: list[str]`
    :   Name of the Lead Form provided by the owner.

    `owner: list[dict[str, typing.Any]]`
    :   URN that identifies the owner of the Lead Form.
        It's a Union of sponsoredAccount and organization.
        sponsoredAccount is an URN of SponsoredAccountUrn that indicates the account of the advertiser.
        organization is an URN of OrganizationUrn that indicates the company account of the marketer.

    `review_info: list[dict[str, typing.Any]]`
    :   Latest information about the content review of the Lead Form.
        It will not be present if the form has not been reviewed by the review pipeline.

    `state: list[str]`
    :   Information about the current state of the Lead Form.

    `version_id: list[int]`
    :   The version ID of the form. This is a derived field and is generated on the server side.

    `version_tag: list[str]`
    :   The number of times the form has been modified.

<a id="LeadFormsKeywordCondition"></a>

`LeadFormsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsStringFilter`
    :   The type of the None singleton.

<a id="LeadFormsListParams"></a>

`LeadFormsListParams(*args, **kwargs)`
:   Parameters for lead_forms.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: int`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

    `start: int`
    :   The type of the None singleton.

<a id="LeadFormsLtCondition"></a>

`LeadFormsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsSearchFilter`
    :   The type of the None singleton.

<a id="LeadFormsLteCondition"></a>

`LeadFormsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsSearchFilter`
    :   The type of the None singleton.

<a id="LeadFormsNeqCondition"></a>

`LeadFormsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsSearchFilter`
    :   The type of the None singleton.

<a id="LeadFormsNotCondition"></a>

`LeadFormsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsAnyCondition`
    :   The type of the None singleton.

<a id="LeadFormsOrCondition"></a>

`LeadFormsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsAnyCondition]`
    :   The type of the None singleton.

<a id="LeadFormsSearchFilter"></a>

`LeadFormsSearchFilter(*args, **kwargs)`
:   Available fields for filtering lead_forms search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: dict[str, typing.Any] | None`
    :   Content of the Lead Form which will be displayed to the viewer.

    `created: int | None`
    :   An epoch time corresponding to the creation of the form.

    `creation_locale: dict[str, typing.Any] | None`
    :   Locale of the entity.
        This field serves as the preferred locale for all fields within the Lead Form with an object type that is capable of localization, such as MultiLocaleString.

    `hidden_fields: list[typing.Any] | None`
    :   Hidden fields used by the owner to track key attributes of the form that generated the lead.
        The field is empty if the owner chooses to not append any tracking attributes to the Lead Form.

    `id: int`
    :   Numerical identifier for the form.

    `last_modified: int | None`
    :   An epoch time corresponding to the last modified of of the form.

    `name: str | None`
    :   Name of the Lead Form provided by the owner.

    `owner: dict[str, typing.Any] | None`
    :   URN that identifies the owner of the Lead Form.
        It's a Union of sponsoredAccount and organization.
        sponsoredAccount is an URN of SponsoredAccountUrn that indicates the account of the advertiser.
        organization is an URN of OrganizationUrn that indicates the company account of the marketer.

    `review_info: dict[str, typing.Any] | None`
    :   Latest information about the content review of the Lead Form.
        It will not be present if the form has not been reviewed by the review pipeline.

    `state: str | None`
    :   Information about the current state of the Lead Form.

    `version_id: int | None`
    :   The version ID of the form. This is a derived field and is generated on the server side.

    `version_tag: str | None`
    :   The number of times the form has been modified.

<a id="LeadFormsSearchQuery"></a>

`LeadFormsSearchQuery(*args, **kwargs)`
:   Search query for lead_forms entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsEqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsNeqCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsGtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsGteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsLtCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsLteCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsInCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsStartswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsEndswithCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsFuzzyCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsKeywordCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsArrayContainsCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsNotCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsAndCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsOrCondition | airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsSortFilter]`
    :   The type of the None singleton.

<a id="LeadFormsSortFilter"></a>

`LeadFormsSortFilter(*args, **kwargs)`
:   Available fields for sorting lead_forms search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: Literal['asc', 'desc']`
    :   Content of the Lead Form which will be displayed to the viewer.

    `created: Literal['asc', 'desc']`
    :   An epoch time corresponding to the creation of the form.

    `creation_locale: Literal['asc', 'desc']`
    :   Locale of the entity.
        This field serves as the preferred locale for all fields within the Lead Form with an object type that is capable of localization, such as MultiLocaleString.

    `hidden_fields: Literal['asc', 'desc']`
    :   Hidden fields used by the owner to track key attributes of the form that generated the lead.
        The field is empty if the owner chooses to not append any tracking attributes to the Lead Form.

    `id: Literal['asc', 'desc']`
    :   Numerical identifier for the form.

    `last_modified: Literal['asc', 'desc']`
    :   An epoch time corresponding to the last modified of of the form.

    `name: Literal['asc', 'desc']`
    :   Name of the Lead Form provided by the owner.

    `owner: Literal['asc', 'desc']`
    :   URN that identifies the owner of the Lead Form.
        It's a Union of sponsoredAccount and organization.
        sponsoredAccount is an URN of SponsoredAccountUrn that indicates the account of the advertiser.
        organization is an URN of OrganizationUrn that indicates the company account of the marketer.

    `review_info: Literal['asc', 'desc']`
    :   Latest information about the content review of the Lead Form.
        It will not be present if the form has not been reviewed by the review pipeline.

    `state: Literal['asc', 'desc']`
    :   Information about the current state of the Lead Form.

    `version_id: Literal['asc', 'desc']`
    :   The version ID of the form. This is a derived field and is generated on the server side.

    `version_tag: Literal['asc', 'desc']`
    :   The number of times the form has been modified.

<a id="LeadFormsStartswithCondition"></a>

`LeadFormsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.linkedin_ads.types.LeadFormsStringFilter`
    :   The type of the None singleton.

<a id="LeadFormsStringFilter"></a>

`LeadFormsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   Content of the Lead Form which will be displayed to the viewer.

    `created: str`
    :   An epoch time corresponding to the creation of the form.

    `creation_locale: str`
    :   Locale of the entity.
        This field serves as the preferred locale for all fields within the Lead Form with an object type that is capable of localization, such as MultiLocaleString.

    `hidden_fields: str`
    :   Hidden fields used by the owner to track key attributes of the form that generated the lead.
        The field is empty if the owner chooses to not append any tracking attributes to the Lead Form.

    `id: str`
    :   Numerical identifier for the form.

    `last_modified: str`
    :   An epoch time corresponding to the last modified of of the form.

    `name: str`
    :   Name of the Lead Form provided by the owner.

    `owner: str`
    :   URN that identifies the owner of the Lead Form.
        It's a Union of sponsoredAccount and organization.
        sponsoredAccount is an URN of SponsoredAccountUrn that indicates the account of the advertiser.
        organization is an URN of OrganizationUrn that indicates the company account of the marketer.

    `review_info: str`
    :   Latest information about the content review of the Lead Form.
        It will not be present if the form has not been reviewed by the review pipeline.

    `state: str`
    :   Information about the current state of the Lead Form.

    `version_id: str`
    :   The version ID of the form. This is a derived field and is generated on the server side.

    `version_tag: str`
    :   The number of times the form has been modified.