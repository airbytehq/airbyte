---
id: airbyte_agent_sdk-connectors-facebook_marketing-types
title: airbyte_agent_sdk.connectors.facebook_marketing.types
---

Module airbyte_agent_sdk.connectors.facebook_marketing.types
============================================================
Type definitions for facebook-marketing connector.

Classes
-------

<a id="AdAccountAndCondition"></a>

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

<a id="AdAccountAnyCondition"></a>

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

<a id="AdAccountAnyValueFilter"></a>

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

<a id="AdAccountContainsCondition"></a>

`AdAccountContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountAnyValueFilter`
    :   The type of the None singleton.

<a id="AdAccountEqCondition"></a>

`AdAccountEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountSearchFilter`
    :   The type of the None singleton.

<a id="AdAccountFuzzyCondition"></a>

`AdAccountFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountStringFilter`
    :   The type of the None singleton.

<a id="AdAccountGetParams"></a>

`AdAccountGetParams(*args, **kwargs)`
:   Parameters for ad_account.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

<a id="AdAccountGtCondition"></a>

`AdAccountGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountSearchFilter`
    :   The type of the None singleton.

<a id="AdAccountGteCondition"></a>

`AdAccountGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountSearchFilter`
    :   The type of the None singleton.

<a id="AdAccountInCondition"></a>

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

<a id="AdAccountInFilter"></a>

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

<a id="AdAccountKeywordCondition"></a>

`AdAccountKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountStringFilter`
    :   The type of the None singleton.

<a id="AdAccountLikeCondition"></a>

`AdAccountLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountStringFilter`
    :   The type of the None singleton.

<a id="AdAccountLtCondition"></a>

`AdAccountLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountSearchFilter`
    :   The type of the None singleton.

<a id="AdAccountLteCondition"></a>

`AdAccountLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountSearchFilter`
    :   The type of the None singleton.

<a id="AdAccountNeqCondition"></a>

`AdAccountNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountSearchFilter`
    :   The type of the None singleton.

<a id="AdAccountNotCondition"></a>

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

<a id="AdAccountOrCondition"></a>

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

<a id="AdAccountSearchFilter"></a>

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

<a id="AdAccountSearchQuery"></a>

`AdAccountSearchQuery(*args, **kwargs)`
:   Search query for ad_account entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountSortFilter]`
    :   The type of the None singleton.

<a id="AdAccountSortFilter"></a>

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

<a id="AdAccountStringFilter"></a>

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

<a id="AdAccountsAndCondition"></a>

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

<a id="AdAccountsAnyCondition"></a>

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

<a id="AdAccountsAnyValueFilter"></a>

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

<a id="AdAccountsContainsCondition"></a>

`AdAccountsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdAccountsEqCondition"></a>

`AdAccountsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

<a id="AdAccountsFuzzyCondition"></a>

`AdAccountsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsStringFilter`
    :   The type of the None singleton.

<a id="AdAccountsGtCondition"></a>

`AdAccountsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

<a id="AdAccountsGteCondition"></a>

`AdAccountsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

<a id="AdAccountsInCondition"></a>

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

<a id="AdAccountsInFilter"></a>

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

<a id="AdAccountsKeywordCondition"></a>

`AdAccountsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsStringFilter`
    :   The type of the None singleton.

<a id="AdAccountsLikeCondition"></a>

`AdAccountsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsStringFilter`
    :   The type of the None singleton.

<a id="AdAccountsListParams"></a>

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

<a id="AdAccountsLtCondition"></a>

`AdAccountsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

<a id="AdAccountsLteCondition"></a>

`AdAccountsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

<a id="AdAccountsNeqCondition"></a>

`AdAccountsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

<a id="AdAccountsNotCondition"></a>

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

<a id="AdAccountsOrCondition"></a>

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

<a id="AdAccountsSearchFilter"></a>

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

<a id="AdAccountsSearchQuery"></a>

`AdAccountsSearchQuery(*args, **kwargs)`
:   Search query for ad_accounts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdAccountsSortFilter]`
    :   The type of the None singleton.

<a id="AdAccountsSortFilter"></a>

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

<a id="AdAccountsStringFilter"></a>

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

<a id="AdCreativesAndCondition"></a>

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

<a id="AdCreativesAnyCondition"></a>

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

<a id="AdCreativesAnyValueFilter"></a>

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

<a id="AdCreativesContainsCondition"></a>

`AdCreativesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesAnyValueFilter`
    :   The type of the None singleton.

<a id="AdCreativesEqCondition"></a>

`AdCreativesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesSearchFilter`
    :   The type of the None singleton.

<a id="AdCreativesFuzzyCondition"></a>

`AdCreativesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesStringFilter`
    :   The type of the None singleton.

<a id="AdCreativesGtCondition"></a>

`AdCreativesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesSearchFilter`
    :   The type of the None singleton.

<a id="AdCreativesGteCondition"></a>

`AdCreativesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesSearchFilter`
    :   The type of the None singleton.

<a id="AdCreativesInCondition"></a>

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

<a id="AdCreativesInFilter"></a>

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

<a id="AdCreativesKeywordCondition"></a>

`AdCreativesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesStringFilter`
    :   The type of the None singleton.

<a id="AdCreativesLikeCondition"></a>

`AdCreativesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesStringFilter`
    :   The type of the None singleton.

<a id="AdCreativesListParams"></a>

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

<a id="AdCreativesLtCondition"></a>

`AdCreativesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesSearchFilter`
    :   The type of the None singleton.

<a id="AdCreativesLteCondition"></a>

`AdCreativesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesSearchFilter`
    :   The type of the None singleton.

<a id="AdCreativesNeqCondition"></a>

`AdCreativesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesSearchFilter`
    :   The type of the None singleton.

<a id="AdCreativesNotCondition"></a>

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

<a id="AdCreativesOrCondition"></a>

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

<a id="AdCreativesSearchFilter"></a>

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

<a id="AdCreativesSearchQuery"></a>

`AdCreativesSearchQuery(*args, **kwargs)`
:   Search query for ad_creatives entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdCreativesSortFilter]`
    :   The type of the None singleton.

<a id="AdCreativesSortFilter"></a>

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

<a id="AdCreativesStringFilter"></a>

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

<a id="AdLibraryListParams"></a>

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

<a id="AdSetsAndCondition"></a>

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

<a id="AdSetsAnyCondition"></a>

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

<a id="AdSetsAnyValueFilter"></a>

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

<a id="AdSetsContainsCondition"></a>

`AdSetsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdSetsCreateParams"></a>

`AdSetsCreateParams(*args, **kwargs)`
:   Parameters for ad_sets.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

<a id="AdSetsEqCondition"></a>

`AdSetsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsSearchFilter`
    :   The type of the None singleton.

<a id="AdSetsFuzzyCondition"></a>

`AdSetsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsStringFilter`
    :   The type of the None singleton.

<a id="AdSetsGetParams"></a>

`AdSetsGetParams(*args, **kwargs)`
:   Parameters for ad_sets.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adset_id: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

<a id="AdSetsGtCondition"></a>

`AdSetsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsSearchFilter`
    :   The type of the None singleton.

<a id="AdSetsGteCondition"></a>

`AdSetsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsSearchFilter`
    :   The type of the None singleton.

<a id="AdSetsInCondition"></a>

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

<a id="AdSetsInFilter"></a>

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

<a id="AdSetsKeywordCondition"></a>

`AdSetsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsStringFilter`
    :   The type of the None singleton.

<a id="AdSetsLikeCondition"></a>

`AdSetsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsStringFilter`
    :   The type of the None singleton.

<a id="AdSetsListParams"></a>

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

<a id="AdSetsLtCondition"></a>

`AdSetsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsSearchFilter`
    :   The type of the None singleton.

<a id="AdSetsLteCondition"></a>

`AdSetsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsSearchFilter`
    :   The type of the None singleton.

<a id="AdSetsNeqCondition"></a>

`AdSetsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsSearchFilter`
    :   The type of the None singleton.

<a id="AdSetsNotCondition"></a>

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

<a id="AdSetsOrCondition"></a>

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

<a id="AdSetsSearchFilter"></a>

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

<a id="AdSetsSearchQuery"></a>

`AdSetsSearchQuery(*args, **kwargs)`
:   Search query for ad_sets entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdSetsSortFilter]`
    :   The type of the None singleton.

<a id="AdSetsSortFilter"></a>

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

<a id="AdSetsStringFilter"></a>

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

<a id="AdSetsUpdateParams"></a>

`AdSetsUpdateParams(*args, **kwargs)`
:   Parameters for ad_sets.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adset_id: str`
    :   The type of the None singleton.

<a id="AdsAndCondition"></a>

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

<a id="AdsAnyCondition"></a>

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

<a id="AdsAnyValueFilter"></a>

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

<a id="AdsContainsCondition"></a>

`AdsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdsCreateParams"></a>

`AdsCreateParams(*args, **kwargs)`
:   Parameters for ads.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

<a id="AdsEqCondition"></a>

`AdsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsFuzzyCondition"></a>

`AdsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsStringFilter`
    :   The type of the None singleton.

<a id="AdsGetParams"></a>

`AdsGetParams(*args, **kwargs)`
:   Parameters for ads.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_id: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

<a id="AdsGtCondition"></a>

`AdsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsGteCondition"></a>

`AdsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsInCondition"></a>

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

<a id="AdsInFilter"></a>

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

<a id="AdsInsightsAndCondition"></a>

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

<a id="AdsInsightsAnyCondition"></a>

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

<a id="AdsInsightsAnyValueFilter"></a>

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

<a id="AdsInsightsContainsCondition"></a>

`AdsInsightsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdsInsightsEqCondition"></a>

`AdsInsightsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsSearchFilter`
    :   The type of the None singleton.

<a id="AdsInsightsFuzzyCondition"></a>

`AdsInsightsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsStringFilter`
    :   The type of the None singleton.

<a id="AdsInsightsGtCondition"></a>

`AdsInsightsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsSearchFilter`
    :   The type of the None singleton.

<a id="AdsInsightsGteCondition"></a>

`AdsInsightsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsSearchFilter`
    :   The type of the None singleton.

<a id="AdsInsightsInCondition"></a>

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

<a id="AdsInsightsInFilter"></a>

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

<a id="AdsInsightsKeywordCondition"></a>

`AdsInsightsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsStringFilter`
    :   The type of the None singleton.

<a id="AdsInsightsLikeCondition"></a>

`AdsInsightsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsStringFilter`
    :   The type of the None singleton.

<a id="AdsInsightsListParams"></a>

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

<a id="AdsInsightsLtCondition"></a>

`AdsInsightsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsSearchFilter`
    :   The type of the None singleton.

<a id="AdsInsightsLteCondition"></a>

`AdsInsightsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsSearchFilter`
    :   The type of the None singleton.

<a id="AdsInsightsNeqCondition"></a>

`AdsInsightsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsSearchFilter`
    :   The type of the None singleton.

<a id="AdsInsightsNotCondition"></a>

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

<a id="AdsInsightsOrCondition"></a>

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

<a id="AdsInsightsSearchFilter"></a>

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

<a id="AdsInsightsSearchQuery"></a>

`AdsInsightsSearchQuery(*args, **kwargs)`
:   Search query for ads_insights entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInsightsSortFilter]`
    :   The type of the None singleton.

<a id="AdsInsightsSortFilter"></a>

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

<a id="AdsInsightsStringFilter"></a>

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

<a id="AdsKeywordCondition"></a>

`AdsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsStringFilter`
    :   The type of the None singleton.

<a id="AdsLikeCondition"></a>

`AdsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsStringFilter`
    :   The type of the None singleton.

<a id="AdsListParams"></a>

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

<a id="AdsLtCondition"></a>

`AdsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsLteCondition"></a>

`AdsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsNeqCondition"></a>

`AdsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsNotCondition"></a>

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

<a id="AdsOrCondition"></a>

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

<a id="AdsSearchFilter"></a>

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

<a id="AdsSearchQuery"></a>

`AdsSearchQuery(*args, **kwargs)`
:   Search query for ads entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.AdsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.AdsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.AdsSortFilter]`
    :   The type of the None singleton.

<a id="AdsSortFilter"></a>

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

<a id="AdsStringFilter"></a>

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

<a id="AdsUpdateParams"></a>

`AdsUpdateParams(*args, **kwargs)`
:   Parameters for ads.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_id: str`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsAnyValueFilter"></a>

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

<a id="CampaignsContainsCondition"></a>

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsCreateParams"></a>

`CampaignsCreateParams(*args, **kwargs)`
:   Parameters for campaigns.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

<a id="CampaignsEqCondition"></a>

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsFuzzyCondition"></a>

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsGetParams"></a>

`CampaignsGetParams(*args, **kwargs)`
:   Parameters for campaigns.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

<a id="CampaignsGtCondition"></a>

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsGteCondition"></a>

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsInFilter`
    :   The type of the None singleton.

<a id="CampaignsInFilter"></a>

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

<a id="CampaignsKeywordCondition"></a>

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsLikeCondition"></a>

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsListParams"></a>

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

<a id="CampaignsLtCondition"></a>

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsLteCondition"></a>

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsNeqCondition"></a>

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignsSearchFilter"></a>

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

<a id="CampaignsSearchQuery"></a>

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.CampaignsSortFilter]`
    :   The type of the None singleton.

<a id="CampaignsSortFilter"></a>

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

<a id="CampaignsStringFilter"></a>

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

<a id="CampaignsUpdateParams"></a>

`CampaignsUpdateParams(*args, **kwargs)`
:   Parameters for campaigns.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: str`
    :   The type of the None singleton.

<a id="CurrentUserGetParams"></a>

`CurrentUserGetParams(*args, **kwargs)`
:   Parameters for current_user.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

<a id="CustomConversionsAndCondition"></a>

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

<a id="CustomConversionsAnyCondition"></a>

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

<a id="CustomConversionsAnyValueFilter"></a>

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

<a id="CustomConversionsContainsCondition"></a>

`CustomConversionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomConversionsEqCondition"></a>

`CustomConversionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsSearchFilter`
    :   The type of the None singleton.

<a id="CustomConversionsFuzzyCondition"></a>

`CustomConversionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsStringFilter`
    :   The type of the None singleton.

<a id="CustomConversionsGtCondition"></a>

`CustomConversionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsSearchFilter`
    :   The type of the None singleton.

<a id="CustomConversionsGteCondition"></a>

`CustomConversionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsSearchFilter`
    :   The type of the None singleton.

<a id="CustomConversionsInCondition"></a>

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

<a id="CustomConversionsInFilter"></a>

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

<a id="CustomConversionsKeywordCondition"></a>

`CustomConversionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsStringFilter`
    :   The type of the None singleton.

<a id="CustomConversionsLikeCondition"></a>

`CustomConversionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsStringFilter`
    :   The type of the None singleton.

<a id="CustomConversionsListParams"></a>

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

<a id="CustomConversionsLtCondition"></a>

`CustomConversionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsSearchFilter`
    :   The type of the None singleton.

<a id="CustomConversionsLteCondition"></a>

`CustomConversionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsSearchFilter`
    :   The type of the None singleton.

<a id="CustomConversionsNeqCondition"></a>

`CustomConversionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsSearchFilter`
    :   The type of the None singleton.

<a id="CustomConversionsNotCondition"></a>

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

<a id="CustomConversionsOrCondition"></a>

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

<a id="CustomConversionsSearchFilter"></a>

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

<a id="CustomConversionsSearchQuery"></a>

`CustomConversionsSearchQuery(*args, **kwargs)`
:   Search query for custom_conversions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.CustomConversionsSortFilter]`
    :   The type of the None singleton.

<a id="CustomConversionsSortFilter"></a>

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

<a id="CustomConversionsStringFilter"></a>

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

<a id="ImagesAndCondition"></a>

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

<a id="ImagesAnyCondition"></a>

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

<a id="ImagesAnyValueFilter"></a>

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

<a id="ImagesContainsCondition"></a>

`ImagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesAnyValueFilter`
    :   The type of the None singleton.

<a id="ImagesEqCondition"></a>

`ImagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesSearchFilter`
    :   The type of the None singleton.

<a id="ImagesFuzzyCondition"></a>

`ImagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesStringFilter`
    :   The type of the None singleton.

<a id="ImagesGtCondition"></a>

`ImagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesSearchFilter`
    :   The type of the None singleton.

<a id="ImagesGteCondition"></a>

`ImagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesSearchFilter`
    :   The type of the None singleton.

<a id="ImagesInCondition"></a>

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

<a id="ImagesInFilter"></a>

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

<a id="ImagesKeywordCondition"></a>

`ImagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesStringFilter`
    :   The type of the None singleton.

<a id="ImagesLikeCondition"></a>

`ImagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesStringFilter`
    :   The type of the None singleton.

<a id="ImagesListParams"></a>

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

<a id="ImagesLtCondition"></a>

`ImagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesSearchFilter`
    :   The type of the None singleton.

<a id="ImagesLteCondition"></a>

`ImagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesSearchFilter`
    :   The type of the None singleton.

<a id="ImagesNeqCondition"></a>

`ImagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesSearchFilter`
    :   The type of the None singleton.

<a id="ImagesNotCondition"></a>

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

<a id="ImagesOrCondition"></a>

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

<a id="ImagesSearchFilter"></a>

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

<a id="ImagesSearchQuery"></a>

`ImagesSearchQuery(*args, **kwargs)`
:   Search query for images entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.ImagesSortFilter]`
    :   The type of the None singleton.

<a id="ImagesSortFilter"></a>

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

<a id="ImagesStringFilter"></a>

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

<a id="PixelStatsListParams"></a>

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

<a id="PixelsGetParams"></a>

`PixelsGetParams(*args, **kwargs)`
:   Parameters for pixels.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `pixel_id: str`
    :   The type of the None singleton.

<a id="PixelsListParams"></a>

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

<a id="VideosAndCondition"></a>

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

<a id="VideosAnyCondition"></a>

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

<a id="VideosAnyValueFilter"></a>

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

<a id="VideosContainsCondition"></a>

`VideosContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosAnyValueFilter`
    :   The type of the None singleton.

<a id="VideosEqCondition"></a>

`VideosEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosSearchFilter`
    :   The type of the None singleton.

<a id="VideosFuzzyCondition"></a>

`VideosFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosStringFilter`
    :   The type of the None singleton.

<a id="VideosGtCondition"></a>

`VideosGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosSearchFilter`
    :   The type of the None singleton.

<a id="VideosGteCondition"></a>

`VideosGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosSearchFilter`
    :   The type of the None singleton.

<a id="VideosInCondition"></a>

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

<a id="VideosInFilter"></a>

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

<a id="VideosKeywordCondition"></a>

`VideosKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosStringFilter`
    :   The type of the None singleton.

<a id="VideosLikeCondition"></a>

`VideosLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosStringFilter`
    :   The type of the None singleton.

<a id="VideosListParams"></a>

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

<a id="VideosLtCondition"></a>

`VideosLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosSearchFilter`
    :   The type of the None singleton.

<a id="VideosLteCondition"></a>

`VideosLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosSearchFilter`
    :   The type of the None singleton.

<a id="VideosNeqCondition"></a>

`VideosNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosSearchFilter`
    :   The type of the None singleton.

<a id="VideosNotCondition"></a>

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

<a id="VideosOrCondition"></a>

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

<a id="VideosSearchFilter"></a>

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

<a id="VideosSearchQuery"></a>

`VideosSearchQuery(*args, **kwargs)`
:   Search query for videos entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.facebook_marketing.types.VideosEqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosNeqCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosGtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosGteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLtCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLteCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosInCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosLikeCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosFuzzyCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosKeywordCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosContainsCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosNotCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosAndCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosOrCondition | airbyte_agent_sdk.connectors.facebook_marketing.types.VideosAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.facebook_marketing.types.VideosSortFilter]`
    :   The type of the None singleton.

<a id="VideosSortFilter"></a>

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

<a id="VideosStringFilter"></a>

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