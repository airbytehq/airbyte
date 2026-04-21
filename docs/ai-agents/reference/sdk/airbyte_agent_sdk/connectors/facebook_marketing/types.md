---
id: airbyte_agent_sdk-connectors-facebook_marketing-types
title: airbyte_agent_sdk.connectors.facebook_marketing.types
---

Module airbyte_agent_sdk.connectors.facebook_marketing.types
============================================================
Type definitions for facebook-marketing connector.

Classes
-------

`AdAccountAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountAnyCondition]`
    :   The type of the None singleton.

`AdAccountAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountAnyValueFilter`
    :   The type of the None singleton.

`AdAccountAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   Ad account ID (numeric)

    `account_status: Any`
    :   Account status

    `amount_spent: Any`
    :   Total amount spent

    `balance: Any`
    :   Current balance of the ad account

    `business_name: Any`
    :   Business name

    `created_time: Any`
    :   Account creation time

    `currency: Any`
    :   Currency used by the ad account

    `id: Any`
    :   Ad account ID

    `name: Any`
    :   Ad account name

    `spend_cap: Any`
    :   Spend cap

    `timezone_name: Any`
    :   Timezone name

`AdAccountContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountAnyValueFilter`
    :   The type of the None singleton.

`AdAccountEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountSearchFilter`
    :   The type of the None singleton.

`AdAccountFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountStringFilter`
    :   The type of the None singleton.

`AdAccountGetParams(*args, **kwargs)`
:   Parameters for ad_account.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

`AdAccountGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountSearchFilter`
    :   The type of the None singleton.

`AdAccountGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountSearchFilter`
    :   The type of the None singleton.

`AdAccountInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountInFilter`
    :   The type of the None singleton.

`AdAccountInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   Ad account ID (numeric)

    `account_status: list[int]`
    :   Account status

    `amount_spent: list[str]`
    :   Total amount spent

    `balance: list[str]`
    :   Current balance of the ad account

    `business_name: list[str]`
    :   Business name

    `created_time: list[str]`
    :   Account creation time

    `currency: list[str]`
    :   Currency used by the ad account

    `id: list[str]`
    :   Ad account ID

    `name: list[str]`
    :   Ad account name

    `spend_cap: list[str]`
    :   Spend cap

    `timezone_name: list[str]`
    :   Timezone name

`AdAccountKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountStringFilter`
    :   The type of the None singleton.

`AdAccountLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountStringFilter`
    :   The type of the None singleton.

`AdAccountLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountSearchFilter`
    :   The type of the None singleton.

`AdAccountLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountSearchFilter`
    :   The type of the None singleton.

`AdAccountNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountSearchFilter`
    :   The type of the None singleton.

`AdAccountNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountAnyCondition`
    :   The type of the None singleton.

`AdAccountOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountAnyCondition]`
    :   The type of the None singleton.

`AdAccountSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_account search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   Ad account ID (numeric)

    `account_status: int | None`
    :   Account status

    `amount_spent: str | None`
    :   Total amount spent

    `balance: str | None`
    :   Current balance of the ad account

    `business_name: str | None`
    :   Business name

    `created_time: str | None`
    :   Account creation time

    `currency: str | None`
    :   Currency used by the ad account

    `id: str | None`
    :   Ad account ID

    `name: str | None`
    :   Ad account name

    `spend_cap: str | None`
    :   Spend cap

    `timezone_name: str | None`
    :   Timezone name

`AdAccountSearchQuery(*args, **kwargs)`
:   Search query for ad_account entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountSortFilter]`
    :   The type of the None singleton.

`AdAccountSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_account search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   Ad account ID (numeric)

    `account_status: Literal['asc', 'desc']`
    :   Account status

    `amount_spent: Literal['asc', 'desc']`
    :   Total amount spent

    `balance: Literal['asc', 'desc']`
    :   Current balance of the ad account

    `business_name: Literal['asc', 'desc']`
    :   Business name

    `created_time: Literal['asc', 'desc']`
    :   Account creation time

    `currency: Literal['asc', 'desc']`
    :   Currency used by the ad account

    `id: Literal['asc', 'desc']`
    :   Ad account ID

    `name: Literal['asc', 'desc']`
    :   Ad account name

    `spend_cap: Literal['asc', 'desc']`
    :   Spend cap

    `timezone_name: Literal['asc', 'desc']`
    :   Timezone name

`AdAccountStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   Ad account ID (numeric)

    `account_status: str`
    :   Account status

    `amount_spent: str`
    :   Total amount spent

    `balance: str`
    :   Current balance of the ad account

    `business_name: str`
    :   Business name

    `created_time: str`
    :   Account creation time

    `currency: str`
    :   Currency used by the ad account

    `id: str`
    :   Ad account ID

    `name: str`
    :   Ad account name

    `spend_cap: str`
    :   Spend cap

    `timezone_name: str`
    :   Timezone name

`AdAccountsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsAnyCondition]`
    :   The type of the None singleton.

`AdAccountsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsAnyValueFilter`
    :   The type of the None singleton.

`AdAccountsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   Ad account ID (numeric)

    `account_status: Any`
    :   Account status

    `amount_spent: Any`
    :   Total amount spent

    `balance: Any`
    :   Current balance of the ad account

    `business_name: Any`
    :   Business name

    `created_time: Any`
    :   Account creation time

    `currency: Any`
    :   Currency used by the ad account

    `id: Any`
    :   Ad account ID

    `name: Any`
    :   Ad account name

    `spend_cap: Any`
    :   Spend cap

    `timezone_name: Any`
    :   Timezone name

`AdAccountsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsAnyValueFilter`
    :   The type of the None singleton.

`AdAccountsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

`AdAccountsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsStringFilter`
    :   The type of the None singleton.

`AdAccountsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

`AdAccountsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

`AdAccountsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsInFilter`
    :   The type of the None singleton.

`AdAccountsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   Ad account ID (numeric)

    `account_status: list[int]`
    :   Account status

    `amount_spent: list[str]`
    :   Total amount spent

    `balance: list[str]`
    :   Current balance of the ad account

    `business_name: list[str]`
    :   Business name

    `created_time: list[str]`
    :   Account creation time

    `currency: list[str]`
    :   Currency used by the ad account

    `id: list[str]`
    :   Ad account ID

    `name: list[str]`
    :   Ad account name

    `spend_cap: list[str]`
    :   Spend cap

    `timezone_name: list[str]`
    :   Timezone name

`AdAccountsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsStringFilter`
    :   The type of the None singleton.

`AdAccountsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsStringFilter`
    :   The type of the None singleton.

`AdAccountsListParams(*args, **kwargs)`
:   Parameters for ad_accounts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`AdAccountsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

`AdAccountsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

`AdAccountsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

`AdAccountsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsAnyCondition`
    :   The type of the None singleton.

`AdAccountsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsAnyCondition]`
    :   The type of the None singleton.

`AdAccountsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_accounts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   Ad account ID (numeric)

    `account_status: int | None`
    :   Account status

    `amount_spent: str | None`
    :   Total amount spent

    `balance: str | None`
    :   Current balance of the ad account

    `business_name: str | None`
    :   Business name

    `created_time: str | None`
    :   Account creation time

    `currency: str | None`
    :   Currency used by the ad account

    `id: str | None`
    :   Ad account ID

    `name: str | None`
    :   Ad account name

    `spend_cap: str | None`
    :   Spend cap

    `timezone_name: str | None`
    :   Timezone name

`AdAccountsSearchQuery(*args, **kwargs)`
:   Search query for ad_accounts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsSortFilter]`
    :   The type of the None singleton.

`AdAccountsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_accounts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   Ad account ID (numeric)

    `account_status: Literal['asc', 'desc']`
    :   Account status

    `amount_spent: Literal['asc', 'desc']`
    :   Total amount spent

    `balance: Literal['asc', 'desc']`
    :   Current balance of the ad account

    `business_name: Literal['asc', 'desc']`
    :   Business name

    `created_time: Literal['asc', 'desc']`
    :   Account creation time

    `currency: Literal['asc', 'desc']`
    :   Currency used by the ad account

    `id: Literal['asc', 'desc']`
    :   Ad account ID

    `name: Literal['asc', 'desc']`
    :   Ad account name

    `spend_cap: Literal['asc', 'desc']`
    :   Spend cap

    `timezone_name: Literal['asc', 'desc']`
    :   Timezone name

`AdAccountsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   Ad account ID (numeric)

    `account_status: str`
    :   Account status

    `amount_spent: str`
    :   Total amount spent

    `balance: str`
    :   Current balance of the ad account

    `business_name: str`
    :   Business name

    `created_time: str`
    :   Account creation time

    `currency: str`
    :   Currency used by the ad account

    `id: str`
    :   Ad account ID

    `name: str`
    :   Ad account name

    `spend_cap: str`
    :   Spend cap

    `timezone_name: str`
    :   Timezone name

`AdCreativesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesAnyCondition]`
    :   The type of the None singleton.

`AdCreativesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesAnyValueFilter`
    :   The type of the None singleton.

`AdCreativesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   Ad account ID

    `body: Any`
    :   Ad body text

    `call_to_action_type: Any`
    :   Call to action type

    `id: Any`
    :   Ad Creative ID

    `image_url: Any`
    :   Image URL

    `link_url: Any`
    :   Link URL

    `name: Any`
    :   Ad Creative name

    `status: Any`
    :   Creative status

    `thumbnail_url: Any`
    :   Thumbnail URL

    `title: Any`
    :   Ad title

`AdCreativesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesAnyValueFilter`
    :   The type of the None singleton.

`AdCreativesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesSearchFilter`
    :   The type of the None singleton.

`AdCreativesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesStringFilter`
    :   The type of the None singleton.

`AdCreativesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesSearchFilter`
    :   The type of the None singleton.

`AdCreativesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesSearchFilter`
    :   The type of the None singleton.

`AdCreativesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesInFilter`
    :   The type of the None singleton.

`AdCreativesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   Ad account ID

    `body: list[str]`
    :   Ad body text

    `call_to_action_type: list[str]`
    :   Call to action type

    `id: list[str]`
    :   Ad Creative ID

    `image_url: list[str]`
    :   Image URL

    `link_url: list[str]`
    :   Link URL

    `name: list[str]`
    :   Ad Creative name

    `status: list[str]`
    :   Creative status

    `thumbnail_url: list[str]`
    :   Thumbnail URL

    `title: list[str]`
    :   Ad title

`AdCreativesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesStringFilter`
    :   The type of the None singleton.

`AdCreativesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesStringFilter`
    :   The type of the None singleton.

`AdCreativesListParams(*args, **kwargs)`
:   Parameters for ad_creatives.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `after: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`AdCreativesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesSearchFilter`
    :   The type of the None singleton.

`AdCreativesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesSearchFilter`
    :   The type of the None singleton.

`AdCreativesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesSearchFilter`
    :   The type of the None singleton.

`AdCreativesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesAnyCondition`
    :   The type of the None singleton.

`AdCreativesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesAnyCondition]`
    :   The type of the None singleton.

`AdCreativesSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_creatives search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   Ad account ID

    `body: str | None`
    :   Ad body text

    `call_to_action_type: str | None`
    :   Call to action type

    `id: str | None`
    :   Ad Creative ID

    `image_url: str | None`
    :   Image URL

    `link_url: str | None`
    :   Link URL

    `name: str | None`
    :   Ad Creative name

    `status: str | None`
    :   Creative status

    `thumbnail_url: str | None`
    :   Thumbnail URL

    `title: str | None`
    :   Ad title

`AdCreativesSearchQuery(*args, **kwargs)`
:   Search query for ad_creatives entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesSortFilter]`
    :   The type of the None singleton.

`AdCreativesSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_creatives search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   Ad account ID

    `body: Literal['asc', 'desc']`
    :   Ad body text

    `call_to_action_type: Literal['asc', 'desc']`
    :   Call to action type

    `id: Literal['asc', 'desc']`
    :   Ad Creative ID

    `image_url: Literal['asc', 'desc']`
    :   Image URL

    `link_url: Literal['asc', 'desc']`
    :   Link URL

    `name: Literal['asc', 'desc']`
    :   Ad Creative name

    `status: Literal['asc', 'desc']`
    :   Creative status

    `thumbnail_url: Literal['asc', 'desc']`
    :   Thumbnail URL

    `title: Literal['asc', 'desc']`
    :   Ad title

`AdCreativesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   Ad account ID

    `body: str`
    :   Ad body text

    `call_to_action_type: str`
    :   Call to action type

    `id: str`
    :   Ad Creative ID

    `image_url: str`
    :   Image URL

    `link_url: str`
    :   Link URL

    `name: str`
    :   Ad Creative name

    `status: str`
    :   Creative status

    `thumbnail_url: str`
    :   Thumbnail URL

    `title: str`
    :   Ad title

`AdLibraryListParams(*args, **kwargs)`
:   Parameters for ad_library.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_active_status: str`
    :   The type of the None singleton.

    `ad_delivery_date_max: str`
    :   The type of the None singleton.

    `ad_delivery_date_min: str`
    :   The type of the None singleton.

    `ad_reached_countries: str`
    :   The type of the None singleton.

    `ad_type: str`
    :   The type of the None singleton.

    `after: str`
    :   The type of the None singleton.

    `bylines: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `languages: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `media_type: str`
    :   The type of the None singleton.

    `publisher_platforms: str`
    :   The type of the None singleton.

    `search_page_ids: str`
    :   The type of the None singleton.

    `search_terms: str`
    :   The type of the None singleton.

    `search_type: str`
    :   The type of the None singleton.

    `unmask_removed_content: bool`
    :   The type of the None singleton.

`AdSetsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsAnyCondition]`
    :   The type of the None singleton.

`AdSetsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsAnyValueFilter`
    :   The type of the None singleton.

`AdSetsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   Ad account ID

    `bid_amount: Any`
    :   Bid amount

    `bid_strategy: Any`
    :   Bid strategy

    `budget_remaining: Any`
    :   Remaining budget

    `campaign_id: Any`
    :   Parent campaign ID

    `created_time: Any`
    :   Ad set creation time

    `daily_budget: Any`
    :   Daily budget

    `effective_status: Any`
    :   Effective status

    `end_time: Any`
    :   Ad set end time

    `id: Any`
    :   Ad Set ID

    `lifetime_budget: Any`
    :   Lifetime budget

    `name: Any`
    :   Ad Set name

    `start_time: Any`
    :   Ad set start time

    `updated_time: Any`
    :   Last update time

`AdSetsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsAnyValueFilter`
    :   The type of the None singleton.

`AdSetsCreateParams(*args, **kwargs)`
:   Parameters for ad_sets.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

`AdSetsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsSearchFilter`
    :   The type of the None singleton.

`AdSetsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsStringFilter`
    :   The type of the None singleton.

`AdSetsGetParams(*args, **kwargs)`
:   Parameters for ad_sets.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adset_id: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

`AdSetsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsSearchFilter`
    :   The type of the None singleton.

`AdSetsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsSearchFilter`
    :   The type of the None singleton.

`AdSetsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsInFilter`
    :   The type of the None singleton.

`AdSetsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   Ad account ID

    `bid_amount: list[float]`
    :   Bid amount

    `bid_strategy: list[str]`
    :   Bid strategy

    `budget_remaining: list[float]`
    :   Remaining budget

    `campaign_id: list[str]`
    :   Parent campaign ID

    `created_time: list[str]`
    :   Ad set creation time

    `daily_budget: list[float]`
    :   Daily budget

    `effective_status: list[str]`
    :   Effective status

    `end_time: list[str]`
    :   Ad set end time

    `id: list[str]`
    :   Ad Set ID

    `lifetime_budget: list[float]`
    :   Lifetime budget

    `name: list[str]`
    :   Ad Set name

    `start_time: list[str]`
    :   Ad set start time

    `updated_time: list[str]`
    :   Last update time

`AdSetsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsStringFilter`
    :   The type of the None singleton.

`AdSetsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsStringFilter`
    :   The type of the None singleton.

`AdSetsListParams(*args, **kwargs)`
:   Parameters for ad_sets.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `after: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`AdSetsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsSearchFilter`
    :   The type of the None singleton.

`AdSetsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsSearchFilter`
    :   The type of the None singleton.

`AdSetsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsSearchFilter`
    :   The type of the None singleton.

`AdSetsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsAnyCondition`
    :   The type of the None singleton.

`AdSetsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsAnyCondition]`
    :   The type of the None singleton.

`AdSetsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_sets search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   Ad account ID

    `bid_amount: float | None`
    :   Bid amount

    `bid_strategy: str | None`
    :   Bid strategy

    `budget_remaining: float | None`
    :   Remaining budget

    `campaign_id: str | None`
    :   Parent campaign ID

    `created_time: str | None`
    :   Ad set creation time

    `daily_budget: float | None`
    :   Daily budget

    `effective_status: str | None`
    :   Effective status

    `end_time: str | None`
    :   Ad set end time

    `id: str | None`
    :   Ad Set ID

    `lifetime_budget: float | None`
    :   Lifetime budget

    `name: str | None`
    :   Ad Set name

    `start_time: str | None`
    :   Ad set start time

    `updated_time: str | None`
    :   Last update time

`AdSetsSearchQuery(*args, **kwargs)`
:   Search query for ad_sets entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsSortFilter]`
    :   The type of the None singleton.

`AdSetsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_sets search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   Ad account ID

    `bid_amount: Literal['asc', 'desc']`
    :   Bid amount

    `bid_strategy: Literal['asc', 'desc']`
    :   Bid strategy

    `budget_remaining: Literal['asc', 'desc']`
    :   Remaining budget

    `campaign_id: Literal['asc', 'desc']`
    :   Parent campaign ID

    `created_time: Literal['asc', 'desc']`
    :   Ad set creation time

    `daily_budget: Literal['asc', 'desc']`
    :   Daily budget

    `effective_status: Literal['asc', 'desc']`
    :   Effective status

    `end_time: Literal['asc', 'desc']`
    :   Ad set end time

    `id: Literal['asc', 'desc']`
    :   Ad Set ID

    `lifetime_budget: Literal['asc', 'desc']`
    :   Lifetime budget

    `name: Literal['asc', 'desc']`
    :   Ad Set name

    `start_time: Literal['asc', 'desc']`
    :   Ad set start time

    `updated_time: Literal['asc', 'desc']`
    :   Last update time

`AdSetsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   Ad account ID

    `bid_amount: str`
    :   Bid amount

    `bid_strategy: str`
    :   Bid strategy

    `budget_remaining: str`
    :   Remaining budget

    `campaign_id: str`
    :   Parent campaign ID

    `created_time: str`
    :   Ad set creation time

    `daily_budget: str`
    :   Daily budget

    `effective_status: str`
    :   Effective status

    `end_time: str`
    :   Ad set end time

    `id: str`
    :   Ad Set ID

    `lifetime_budget: str`
    :   Lifetime budget

    `name: str`
    :   Ad Set name

    `start_time: str`
    :   Ad set start time

    `updated_time: str`
    :   Last update time

`AdSetsUpdateParams(*args, **kwargs)`
:   Parameters for ad_sets.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adset_id: str`
    :   The type of the None singleton.

`AdsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsAnyCondition]`
    :   The type of the None singleton.

`AdsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsAnyValueFilter`
    :   The type of the None singleton.

`AdsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   Ad account ID

    `adset_id: Any`
    :   Parent ad set ID

    `campaign_id: Any`
    :   Parent campaign ID

    `created_time: Any`
    :   Ad creation time

    `effective_status: Any`
    :   Effective status

    `id: Any`
    :   Ad ID

    `name: Any`
    :   Ad name

    `status: Any`
    :   Ad status

    `updated_time: Any`
    :   Last update time

`AdsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsAnyValueFilter`
    :   The type of the None singleton.

`AdsCreateParams(*args, **kwargs)`
:   Parameters for ads.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

`AdsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsStringFilter`
    :   The type of the None singleton.

`AdsGetParams(*args, **kwargs)`
:   Parameters for ads.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_id: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

`AdsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInFilter`
    :   The type of the None singleton.

`AdsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   Ad account ID

    `adset_id: list[str]`
    :   Parent ad set ID

    `campaign_id: list[str]`
    :   Parent campaign ID

    `created_time: list[str]`
    :   Ad creation time

    `effective_status: list[str]`
    :   Effective status

    `id: list[str]`
    :   Ad ID

    `name: list[str]`
    :   Ad name

    `status: list[str]`
    :   Ad status

    `updated_time: list[str]`
    :   Last update time

`AdsInsightsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsAnyCondition]`
    :   The type of the None singleton.

`AdsInsightsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsAnyValueFilter`
    :   The type of the None singleton.

`AdsInsightsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   Ad account ID

    `account_name: Any`
    :   Ad account name

    `action_values: Any`
    :   Action values taken on the ad

    `actions: Any`
    :   Total number of actions taken

    `ad_id: Any`
    :   Ad ID

    `ad_name: Any`
    :   Ad name

    `adset_id: Any`
    :   Ad set ID

    `adset_name: Any`
    :   Ad set name

    `campaign_id: Any`
    :   Campaign ID

    `campaign_name: Any`
    :   Campaign name

    `clicks: Any`
    :   Number of clicks

    `cpc: Any`
    :   Cost per click

    `cpm: Any`
    :   Cost per 1000 impressions

    `ctr: Any`
    :   Click-through rate

    `date_start: Any`
    :   Start date of the reporting period

    `date_stop: Any`
    :   End date of the reporting period

    `impressions: Any`
    :   Number of impressions

    `reach: Any`
    :   Number of unique people reached

    `spend: Any`
    :   Amount spent

`AdsInsightsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsAnyValueFilter`
    :   The type of the None singleton.

`AdsInsightsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsSearchFilter`
    :   The type of the None singleton.

`AdsInsightsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsStringFilter`
    :   The type of the None singleton.

`AdsInsightsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsSearchFilter`
    :   The type of the None singleton.

`AdsInsightsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsSearchFilter`
    :   The type of the None singleton.

`AdsInsightsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsInFilter`
    :   The type of the None singleton.

`AdsInsightsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   Ad account ID

    `account_name: list[str]`
    :   Ad account name

    `action_values: list[list[typing.Any]]`
    :   Action values taken on the ad

    `actions: list[list[typing.Any]]`
    :   Total number of actions taken

    `ad_id: list[str]`
    :   Ad ID

    `ad_name: list[str]`
    :   Ad name

    `adset_id: list[str]`
    :   Ad set ID

    `adset_name: list[str]`
    :   Ad set name

    `campaign_id: list[str]`
    :   Campaign ID

    `campaign_name: list[str]`
    :   Campaign name

    `clicks: list[int]`
    :   Number of clicks

    `cpc: list[float]`
    :   Cost per click

    `cpm: list[float]`
    :   Cost per 1000 impressions

    `ctr: list[float]`
    :   Click-through rate

    `date_start: list[str]`
    :   Start date of the reporting period

    `date_stop: list[str]`
    :   End date of the reporting period

    `impressions: list[int]`
    :   Number of impressions

    `reach: list[int]`
    :   Number of unique people reached

    `spend: list[float]`
    :   Amount spent

`AdsInsightsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsStringFilter`
    :   The type of the None singleton.

`AdsInsightsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsStringFilter`
    :   The type of the None singleton.

`AdsInsightsListParams(*args, **kwargs)`
:   Parameters for ads_insights.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `after: str`
    :   The type of the None singleton.

    `date_preset: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `level: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `time_increment: str`
    :   The type of the None singleton.

    `time_range: str`
    :   The type of the None singleton.

`AdsInsightsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsSearchFilter`
    :   The type of the None singleton.

`AdsInsightsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsSearchFilter`
    :   The type of the None singleton.

`AdsInsightsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsSearchFilter`
    :   The type of the None singleton.

`AdsInsightsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsAnyCondition`
    :   The type of the None singleton.

`AdsInsightsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsAnyCondition]`
    :   The type of the None singleton.

`AdsInsightsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ads_insights search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   Ad account ID

    `account_name: str | None`
    :   Ad account name

    `action_values: list[typing.Any] | None`
    :   Action values taken on the ad

    `actions: list[typing.Any] | None`
    :   Total number of actions taken

    `ad_id: str | None`
    :   Ad ID

    `ad_name: str | None`
    :   Ad name

    `adset_id: str | None`
    :   Ad set ID

    `adset_name: str | None`
    :   Ad set name

    `campaign_id: str | None`
    :   Campaign ID

    `campaign_name: str | None`
    :   Campaign name

    `clicks: int | None`
    :   Number of clicks

    `cpc: float | None`
    :   Cost per click

    `cpm: float | None`
    :   Cost per 1000 impressions

    `ctr: float | None`
    :   Click-through rate

    `date_start: str | None`
    :   Start date of the reporting period

    `date_stop: str | None`
    :   End date of the reporting period

    `impressions: int | None`
    :   Number of impressions

    `reach: int | None`
    :   Number of unique people reached

    `spend: float | None`
    :   Amount spent

`AdsInsightsSearchQuery(*args, **kwargs)`
:   Search query for ads_insights entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsSortFilter]`
    :   The type of the None singleton.

`AdsInsightsSortFilter(*args, **kwargs)`
:   Available fields for sorting ads_insights search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   Ad account ID

    `account_name: Literal['asc', 'desc']`
    :   Ad account name

    `action_values: Literal['asc', 'desc']`
    :   Action values taken on the ad

    `actions: Literal['asc', 'desc']`
    :   Total number of actions taken

    `ad_id: Literal['asc', 'desc']`
    :   Ad ID

    `ad_name: Literal['asc', 'desc']`
    :   Ad name

    `adset_id: Literal['asc', 'desc']`
    :   Ad set ID

    `adset_name: Literal['asc', 'desc']`
    :   Ad set name

    `campaign_id: Literal['asc', 'desc']`
    :   Campaign ID

    `campaign_name: Literal['asc', 'desc']`
    :   Campaign name

    `clicks: Literal['asc', 'desc']`
    :   Number of clicks

    `cpc: Literal['asc', 'desc']`
    :   Cost per click

    `cpm: Literal['asc', 'desc']`
    :   Cost per 1000 impressions

    `ctr: Literal['asc', 'desc']`
    :   Click-through rate

    `date_start: Literal['asc', 'desc']`
    :   Start date of the reporting period

    `date_stop: Literal['asc', 'desc']`
    :   End date of the reporting period

    `impressions: Literal['asc', 'desc']`
    :   Number of impressions

    `reach: Literal['asc', 'desc']`
    :   Number of unique people reached

    `spend: Literal['asc', 'desc']`
    :   Amount spent

`AdsInsightsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   Ad account ID

    `account_name: str`
    :   Ad account name

    `action_values: str`
    :   Action values taken on the ad

    `actions: str`
    :   Total number of actions taken

    `ad_id: str`
    :   Ad ID

    `ad_name: str`
    :   Ad name

    `adset_id: str`
    :   Ad set ID

    `adset_name: str`
    :   Ad set name

    `campaign_id: str`
    :   Campaign ID

    `campaign_name: str`
    :   Campaign name

    `clicks: str`
    :   Number of clicks

    `cpc: str`
    :   Cost per click

    `cpm: str`
    :   Cost per 1000 impressions

    `ctr: str`
    :   Click-through rate

    `date_start: str`
    :   Start date of the reporting period

    `date_stop: str`
    :   End date of the reporting period

    `impressions: str`
    :   Number of impressions

    `reach: str`
    :   Number of unique people reached

    `spend: str`
    :   Amount spent

`AdsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsStringFilter`
    :   The type of the None singleton.

`AdsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsStringFilter`
    :   The type of the None singleton.

`AdsListParams(*args, **kwargs)`
:   Parameters for ads.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `after: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`AdsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsAnyCondition`
    :   The type of the None singleton.

`AdsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsAnyCondition]`
    :   The type of the None singleton.

`AdsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ads search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   Ad account ID

    `adset_id: str | None`
    :   Parent ad set ID

    `campaign_id: str | None`
    :   Parent campaign ID

    `created_time: str | None`
    :   Ad creation time

    `effective_status: str | None`
    :   Effective status

    `id: str | None`
    :   Ad ID

    `name: str | None`
    :   Ad name

    `status: str | None`
    :   Ad status

    `updated_time: str | None`
    :   Last update time

`AdsSearchQuery(*args, **kwargs)`
:   Search query for ads entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdsSortFilter]`
    :   The type of the None singleton.

`AdsSortFilter(*args, **kwargs)`
:   Available fields for sorting ads search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   Ad account ID

    `adset_id: Literal['asc', 'desc']`
    :   Parent ad set ID

    `campaign_id: Literal['asc', 'desc']`
    :   Parent campaign ID

    `created_time: Literal['asc', 'desc']`
    :   Ad creation time

    `effective_status: Literal['asc', 'desc']`
    :   Effective status

    `id: Literal['asc', 'desc']`
    :   Ad ID

    `name: Literal['asc', 'desc']`
    :   Ad name

    `status: Literal['asc', 'desc']`
    :   Ad status

    `updated_time: Literal['asc', 'desc']`
    :   Last update time

`AdsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   Ad account ID

    `adset_id: str`
    :   Parent ad set ID

    `campaign_id: str`
    :   Parent campaign ID

    `created_time: str`
    :   Ad creation time

    `effective_status: str`
    :   Effective status

    `id: str`
    :   Ad ID

    `name: str`
    :   Ad name

    `status: str`
    :   Ad status

    `updated_time: str`
    :   Last update time

`AdsUpdateParams(*args, **kwargs)`
:   Parameters for ads.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_id: str`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

`CampaignsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   Ad account ID

    `budget_remaining: Any`
    :   Remaining budget

    `created_time: Any`
    :   Campaign creation time

    `daily_budget: Any`
    :   Daily budget in account currency

    `effective_status: Any`
    :   Effective status

    `id: Any`
    :   Campaign ID

    `lifetime_budget: Any`
    :   Lifetime budget

    `name: Any`
    :   Campaign name

    `objective: Any`
    :   Campaign objective

    `start_time: Any`
    :   Campaign start time

    `status: Any`
    :   Campaign status

    `stop_time: Any`
    :   Campaign stop time

    `updated_time: Any`
    :   Last update time

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

`CampaignsCreateParams(*args, **kwargs)`
:   Parameters for campaigns.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsGetParams(*args, **kwargs)`
:   Parameters for campaigns.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsInFilter`
    :   The type of the None singleton.

`CampaignsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   Ad account ID

    `budget_remaining: list[float]`
    :   Remaining budget

    `created_time: list[str]`
    :   Campaign creation time

    `daily_budget: list[float]`
    :   Daily budget in account currency

    `effective_status: list[str]`
    :   Effective status

    `id: list[str]`
    :   Campaign ID

    `lifetime_budget: list[float]`
    :   Lifetime budget

    `name: list[str]`
    :   Campaign name

    `objective: list[str]`
    :   Campaign objective

    `start_time: list[str]`
    :   Campaign start time

    `status: list[str]`
    :   Campaign status

    `stop_time: list[str]`
    :   Campaign stop time

    `updated_time: list[str]`
    :   Last update time

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsListParams(*args, **kwargs)`
:   Parameters for campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `after: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

`CampaignsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaigns search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   Ad account ID

    `budget_remaining: float | None`
    :   Remaining budget

    `created_time: str | None`
    :   Campaign creation time

    `daily_budget: float | None`
    :   Daily budget in account currency

    `effective_status: str | None`
    :   Effective status

    `id: str | None`
    :   Campaign ID

    `lifetime_budget: float | None`
    :   Lifetime budget

    `name: str | None`
    :   Campaign name

    `objective: str | None`
    :   Campaign objective

    `start_time: str | None`
    :   Campaign start time

    `status: str | None`
    :   Campaign status

    `stop_time: str | None`
    :   Campaign stop time

    `updated_time: str | None`
    :   Last update time

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsSortFilter]`
    :   The type of the None singleton.

`CampaignsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaigns search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   Ad account ID

    `budget_remaining: Literal['asc', 'desc']`
    :   Remaining budget

    `created_time: Literal['asc', 'desc']`
    :   Campaign creation time

    `daily_budget: Literal['asc', 'desc']`
    :   Daily budget in account currency

    `effective_status: Literal['asc', 'desc']`
    :   Effective status

    `id: Literal['asc', 'desc']`
    :   Campaign ID

    `lifetime_budget: Literal['asc', 'desc']`
    :   Lifetime budget

    `name: Literal['asc', 'desc']`
    :   Campaign name

    `objective: Literal['asc', 'desc']`
    :   Campaign objective

    `start_time: Literal['asc', 'desc']`
    :   Campaign start time

    `status: Literal['asc', 'desc']`
    :   Campaign status

    `stop_time: Literal['asc', 'desc']`
    :   Campaign stop time

    `updated_time: Literal['asc', 'desc']`
    :   Last update time

`CampaignsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   Ad account ID

    `budget_remaining: str`
    :   Remaining budget

    `created_time: str`
    :   Campaign creation time

    `daily_budget: str`
    :   Daily budget in account currency

    `effective_status: str`
    :   Effective status

    `id: str`
    :   Campaign ID

    `lifetime_budget: str`
    :   Lifetime budget

    `name: str`
    :   Campaign name

    `objective: str`
    :   Campaign objective

    `start_time: str`
    :   Campaign start time

    `status: str`
    :   Campaign status

    `stop_time: str`
    :   Campaign stop time

    `updated_time: str`
    :   Last update time

`CampaignsUpdateParams(*args, **kwargs)`
:   Parameters for campaigns.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: str`
    :   The type of the None singleton.

`CurrentUserGetParams(*args, **kwargs)`
:   Parameters for current_user.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

`CustomConversionsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsAnyCondition]`
    :   The type of the None singleton.

`CustomConversionsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsAnyValueFilter`
    :   The type of the None singleton.

`CustomConversionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   Ad account ID

    `creation_time: Any`
    :   Creation time

    `custom_event_type: Any`
    :   Custom event type

    `description: Any`
    :   Description

    `first_fired_time: Any`
    :   First fired time

    `id: Any`
    :   Custom Conversion ID

    `is_archived: Any`
    :   Whether the conversion is archived

    `last_fired_time: Any`
    :   Last fired time

    `name: Any`
    :   Custom Conversion name

`CustomConversionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsAnyValueFilter`
    :   The type of the None singleton.

`CustomConversionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsSearchFilter`
    :   The type of the None singleton.

`CustomConversionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsStringFilter`
    :   The type of the None singleton.

`CustomConversionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsSearchFilter`
    :   The type of the None singleton.

`CustomConversionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsSearchFilter`
    :   The type of the None singleton.

`CustomConversionsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsInFilter`
    :   The type of the None singleton.

`CustomConversionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   Ad account ID

    `creation_time: list[str]`
    :   Creation time

    `custom_event_type: list[str]`
    :   Custom event type

    `description: list[str]`
    :   Description

    `first_fired_time: list[str]`
    :   First fired time

    `id: list[str]`
    :   Custom Conversion ID

    `is_archived: list[bool]`
    :   Whether the conversion is archived

    `last_fired_time: list[str]`
    :   Last fired time

    `name: list[str]`
    :   Custom Conversion name

`CustomConversionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsStringFilter`
    :   The type of the None singleton.

`CustomConversionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsStringFilter`
    :   The type of the None singleton.

`CustomConversionsListParams(*args, **kwargs)`
:   Parameters for custom_conversions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `after: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`CustomConversionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsSearchFilter`
    :   The type of the None singleton.

`CustomConversionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsSearchFilter`
    :   The type of the None singleton.

`CustomConversionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsSearchFilter`
    :   The type of the None singleton.

`CustomConversionsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsAnyCondition`
    :   The type of the None singleton.

`CustomConversionsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsAnyCondition]`
    :   The type of the None singleton.

`CustomConversionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering custom_conversions search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   Ad account ID

    `creation_time: str | None`
    :   Creation time

    `custom_event_type: str | None`
    :   Custom event type

    `description: str | None`
    :   Description

    `first_fired_time: str | None`
    :   First fired time

    `id: str | None`
    :   Custom Conversion ID

    `is_archived: bool | None`
    :   Whether the conversion is archived

    `last_fired_time: str | None`
    :   Last fired time

    `name: str | None`
    :   Custom Conversion name

`CustomConversionsSearchQuery(*args, **kwargs)`
:   Search query for custom_conversions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsSortFilter]`
    :   The type of the None singleton.

`CustomConversionsSortFilter(*args, **kwargs)`
:   Available fields for sorting custom_conversions search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   Ad account ID

    `creation_time: Literal['asc', 'desc']`
    :   Creation time

    `custom_event_type: Literal['asc', 'desc']`
    :   Custom event type

    `description: Literal['asc', 'desc']`
    :   Description

    `first_fired_time: Literal['asc', 'desc']`
    :   First fired time

    `id: Literal['asc', 'desc']`
    :   Custom Conversion ID

    `is_archived: Literal['asc', 'desc']`
    :   Whether the conversion is archived

    `last_fired_time: Literal['asc', 'desc']`
    :   Last fired time

    `name: Literal['asc', 'desc']`
    :   Custom Conversion name

`CustomConversionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   Ad account ID

    `creation_time: str`
    :   Creation time

    `custom_event_type: str`
    :   Custom event type

    `description: str`
    :   Description

    `first_fired_time: str`
    :   First fired time

    `id: str`
    :   Custom Conversion ID

    `is_archived: str`
    :   Whether the conversion is archived

    `last_fired_time: str`
    :   Last fired time

    `name: str`
    :   Custom Conversion name

`ImagesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesAnyCondition]`
    :   The type of the None singleton.

`ImagesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesAnyValueFilter`
    :   The type of the None singleton.

`ImagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   Ad account ID

    `created_time: Any`
    :   Creation time

    `hash: Any`
    :   Image hash

    `height: Any`
    :   Image height

    `id: Any`
    :   Image ID

    `name: Any`
    :   Image name

    `permalink_url: Any`
    :   Permalink URL

    `status: Any`
    :   Image status

    `updated_time: Any`
    :   Last update time

    `url: Any`
    :   Image URL

    `width: Any`
    :   Image width

`ImagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesAnyValueFilter`
    :   The type of the None singleton.

`ImagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesSearchFilter`
    :   The type of the None singleton.

`ImagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesStringFilter`
    :   The type of the None singleton.

`ImagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesSearchFilter`
    :   The type of the None singleton.

`ImagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesSearchFilter`
    :   The type of the None singleton.

`ImagesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesInFilter`
    :   The type of the None singleton.

`ImagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   Ad account ID

    `created_time: list[str]`
    :   Creation time

    `hash: list[str]`
    :   Image hash

    `height: list[int]`
    :   Image height

    `id: list[str]`
    :   Image ID

    `name: list[str]`
    :   Image name

    `permalink_url: list[str]`
    :   Permalink URL

    `status: list[str]`
    :   Image status

    `updated_time: list[str]`
    :   Last update time

    `url: list[str]`
    :   Image URL

    `width: list[int]`
    :   Image width

`ImagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesStringFilter`
    :   The type of the None singleton.

`ImagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesStringFilter`
    :   The type of the None singleton.

`ImagesListParams(*args, **kwargs)`
:   Parameters for images.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `after: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`ImagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesSearchFilter`
    :   The type of the None singleton.

`ImagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesSearchFilter`
    :   The type of the None singleton.

`ImagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesSearchFilter`
    :   The type of the None singleton.

`ImagesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesAnyCondition`
    :   The type of the None singleton.

`ImagesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesAnyCondition]`
    :   The type of the None singleton.

`ImagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering images search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   Ad account ID

    `created_time: str | None`
    :   Creation time

    `hash: str | None`
    :   Image hash

    `height: int | None`
    :   Image height

    `id: str | None`
    :   Image ID

    `name: str | None`
    :   Image name

    `permalink_url: str | None`
    :   Permalink URL

    `status: str | None`
    :   Image status

    `updated_time: str | None`
    :   Last update time

    `url: str | None`
    :   Image URL

    `width: int | None`
    :   Image width

`ImagesSearchQuery(*args, **kwargs)`
:   Search query for images entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesSortFilter]`
    :   The type of the None singleton.

`ImagesSortFilter(*args, **kwargs)`
:   Available fields for sorting images search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   Ad account ID

    `created_time: Literal['asc', 'desc']`
    :   Creation time

    `hash: Literal['asc', 'desc']`
    :   Image hash

    `height: Literal['asc', 'desc']`
    :   Image height

    `id: Literal['asc', 'desc']`
    :   Image ID

    `name: Literal['asc', 'desc']`
    :   Image name

    `permalink_url: Literal['asc', 'desc']`
    :   Permalink URL

    `status: Literal['asc', 'desc']`
    :   Image status

    `updated_time: Literal['asc', 'desc']`
    :   Last update time

    `url: Literal['asc', 'desc']`
    :   Image URL

    `width: Literal['asc', 'desc']`
    :   Image width

`ImagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   Ad account ID

    `created_time: str`
    :   Creation time

    `hash: str`
    :   Image hash

    `height: str`
    :   Image height

    `id: str`
    :   Image ID

    `name: str`
    :   Image name

    `permalink_url: str`
    :   Permalink URL

    `status: str`
    :   Image status

    `updated_time: str`
    :   Last update time

    `url: str`
    :   Image URL

    `width: str`
    :   Image width

`PixelStatsListParams(*args, **kwargs)`
:   Parameters for pixel_stats.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `aggregation: str`
    :   The type of the None singleton.

    `end_time: str`
    :   The type of the None singleton.

    `pixel_id: str`
    :   The type of the None singleton.

    `start_time: str`
    :   The type of the None singleton.

`PixelsGetParams(*args, **kwargs)`
:   Parameters for pixels.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `pixel_id: str`
    :   The type of the None singleton.

`PixelsListParams(*args, **kwargs)`
:   Parameters for pixels.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `after: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`VideosAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.facebook_marketing.types.VideosEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosAnyCondition]`
    :   The type of the None singleton.

`VideosAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosAnyValueFilter`
    :   The type of the None singleton.

`VideosAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   Ad account ID

    `created_time: Any`
    :   Creation time

    `description: Any`
    :   Video description

    `id: Any`
    :   Video ID

    `length: Any`
    :   Video length in seconds

    `permalink_url: Any`
    :   Permalink URL

    `source: Any`
    :   Video source URL

    `title: Any`
    :   Video title

    `updated_time: Any`
    :   Last update time

    `views: Any`
    :   Number of views

`VideosContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosAnyValueFilter`
    :   The type of the None singleton.

`VideosEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosSearchFilter`
    :   The type of the None singleton.

`VideosFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosStringFilter`
    :   The type of the None singleton.

`VideosGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosSearchFilter`
    :   The type of the None singleton.

`VideosGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosSearchFilter`
    :   The type of the None singleton.

`VideosInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosInFilter`
    :   The type of the None singleton.

`VideosInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   Ad account ID

    `created_time: list[str]`
    :   Creation time

    `description: list[str]`
    :   Video description

    `id: list[str]`
    :   Video ID

    `length: list[float]`
    :   Video length in seconds

    `permalink_url: list[str]`
    :   Permalink URL

    `source: list[str]`
    :   Video source URL

    `title: list[str]`
    :   Video title

    `updated_time: list[str]`
    :   Last update time

    `views: list[int]`
    :   Number of views

`VideosKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosStringFilter`
    :   The type of the None singleton.

`VideosLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosStringFilter`
    :   The type of the None singleton.

`VideosListParams(*args, **kwargs)`
:   Parameters for videos.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `after: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`VideosLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosSearchFilter`
    :   The type of the None singleton.

`VideosLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosSearchFilter`
    :   The type of the None singleton.

`VideosNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosSearchFilter`
    :   The type of the None singleton.

`VideosNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosAnyCondition`
    :   The type of the None singleton.

`VideosOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.facebook_marketing.types.VideosEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosAnyCondition]`
    :   The type of the None singleton.

`VideosSearchFilter(*args, **kwargs)`
:   Available fields for filtering videos search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   Ad account ID

    `created_time: str | None`
    :   Creation time

    `description: str | None`
    :   Video description

    `id: str | None`
    :   Video ID

    `length: float | None`
    :   Video length in seconds

    `permalink_url: str | None`
    :   Permalink URL

    `source: str | None`
    :   Video source URL

    `title: str | None`
    :   Video title

    `updated_time: str | None`
    :   Last update time

    `views: int | None`
    :   Number of views

`VideosSearchQuery(*args, **kwargs)`
:   Search query for videos entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.VideosSortFilter]`
    :   The type of the None singleton.

`VideosSortFilter(*args, **kwargs)`
:   Available fields for sorting videos search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   Ad account ID

    `created_time: Literal['asc', 'desc']`
    :   Creation time

    `description: Literal['asc', 'desc']`
    :   Video description

    `id: Literal['asc', 'desc']`
    :   Video ID

    `length: Literal['asc', 'desc']`
    :   Video length in seconds

    `permalink_url: Literal['asc', 'desc']`
    :   Permalink URL

    `source: Literal['asc', 'desc']`
    :   Video source URL

    `title: Literal['asc', 'desc']`
    :   Video title

    `updated_time: Literal['asc', 'desc']`
    :   Last update time

    `views: Literal['asc', 'desc']`
    :   Number of views

`VideosStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   Ad account ID

    `created_time: str`
    :   Creation time

    `description: str`
    :   Video description

    `id: str`
    :   Video ID

    `length: str`
    :   Video length in seconds

    `permalink_url: str`
    :   Permalink URL

    `source: str`
    :   Video source URL

    `title: str`
    :   Video title

    `updated_time: str`
    :   Last update time

    `views: str`
    :   Number of views