---
id: airbyte_agent_sdk-connectors-pinterest-types
title: airbyte_agent_sdk.connectors.pinterest.types
---

Module airbyte_agent_sdk.connectors.pinterest.types
===================================================
Type definitions for pinterest connector.

Classes
-------

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

    `and: list[airbyte_agent_sdk.connectors.pinterest.types.AdAccountsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsInCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.pinterest.types.AdAccountsAnyValueFilter`
    :   The type of the None singleton.

`AdAccountsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country: Any`
    :   Country associated with the ad account

    `created_time: Any`
    :   Timestamp when the ad account was created (Unix seconds)

    `currency: Any`
    :   Currency used for billing

    `id: Any`
    :   Unique identifier for the ad account

    `name: Any`
    :   Name of the ad account

    `owner: Any`
    :   Owner details of the ad account

    `permissions: Any`
    :   Permissions assigned to the ad account

    `updated_time: Any`
    :   Timestamp when the ad account was last updated (Unix seconds)

`AdAccountsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pinterest.types.AdAccountsAnyValueFilter`
    :   The type of the None singleton.

`AdAccountsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pinterest.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

`AdAccountsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pinterest.types.AdAccountsStringFilter`
    :   The type of the None singleton.

`AdAccountsGetParams(*args, **kwargs)`
:   Parameters for ad_accounts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

`AdAccountsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pinterest.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

`AdAccountsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pinterest.types.AdAccountsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.pinterest.types.AdAccountsInFilter`
    :   The type of the None singleton.

`AdAccountsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country: list[str]`
    :   Country associated with the ad account

    `created_time: list[int]`
    :   Timestamp when the ad account was created (Unix seconds)

    `currency: list[str]`
    :   Currency used for billing

    `id: list[str]`
    :   Unique identifier for the ad account

    `name: list[str]`
    :   Name of the ad account

    `owner: list[dict[str, typing.Any]]`
    :   Owner details of the ad account

    `permissions: list[list[typing.Any]]`
    :   Permissions assigned to the ad account

    `updated_time: list[int]`
    :   Timestamp when the ad account was last updated (Unix seconds)

`AdAccountsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pinterest.types.AdAccountsStringFilter`
    :   The type of the None singleton.

`AdAccountsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pinterest.types.AdAccountsStringFilter`
    :   The type of the None singleton.

`AdAccountsListParams(*args, **kwargs)`
:   Parameters for ad_accounts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bookmark: str`
    :   The type of the None singleton.

    `include_shared_accounts: bool`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`AdAccountsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pinterest.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

`AdAccountsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pinterest.types.AdAccountsSearchFilter`
    :   The type of the None singleton.

`AdAccountsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pinterest.types.AdAccountsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.pinterest.types.AdAccountsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsInCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.pinterest.types.AdAccountsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsInCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsAnyCondition]`
    :   The type of the None singleton.

`AdAccountsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_accounts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country: str | None`
    :   Country associated with the ad account

    `created_time: int | None`
    :   Timestamp when the ad account was created (Unix seconds)

    `currency: str | None`
    :   Currency used for billing

    `id: str | None`
    :   Unique identifier for the ad account

    `name: str | None`
    :   Name of the ad account

    `owner: dict[str, typing.Any] | None`
    :   Owner details of the ad account

    `permissions: list[typing.Any] | None`
    :   Permissions assigned to the ad account

    `updated_time: int | None`
    :   Timestamp when the ad account was last updated (Unix seconds)

`AdAccountsSearchQuery(*args, **kwargs)`
:   Search query for ad_accounts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pinterest.types.AdAccountsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsInCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AdAccountsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pinterest.types.AdAccountsSortFilter]`
    :   The type of the None singleton.

`AdAccountsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_accounts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country: Literal['asc', 'desc']`
    :   Country associated with the ad account

    `created_time: Literal['asc', 'desc']`
    :   Timestamp when the ad account was created (Unix seconds)

    `currency: Literal['asc', 'desc']`
    :   Currency used for billing

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the ad account

    `name: Literal['asc', 'desc']`
    :   Name of the ad account

    `owner: Literal['asc', 'desc']`
    :   Owner details of the ad account

    `permissions: Literal['asc', 'desc']`
    :   Permissions assigned to the ad account

    `updated_time: Literal['asc', 'desc']`
    :   Timestamp when the ad account was last updated (Unix seconds)

`AdAccountsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `country: str`
    :   Country associated with the ad account

    `created_time: str`
    :   Timestamp when the ad account was created (Unix seconds)

    `currency: str`
    :   Currency used for billing

    `id: str`
    :   Unique identifier for the ad account

    `name: str`
    :   Name of the ad account

    `owner: str`
    :   Owner details of the ad account

    `permissions: str`
    :   Permissions assigned to the ad account

    `updated_time: str`
    :   Timestamp when the ad account was last updated (Unix seconds)

`AdGroupsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.pinterest.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsAnyCondition]`
    :   The type of the None singleton.

`AdGroupsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.pinterest.types.AdGroupsAnyValueFilter`
    :   The type of the None singleton.

`AdGroupsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Any`
    :   Ad account ID

    `auto_targeting_enabled: Any`
    :   Whether auto targeting is enabled

    `bid_in_micro_currency: Any`
    :   Bid in microcurrency

    `bid_strategy_type: Any`
    :   Bid strategy type

    `billable_event: Any`
    :   Billable event type

    `budget_in_micro_currency: Any`
    :   Budget in microcurrency

    `budget_type: Any`
    :   Budget type

    `campaign_id: Any`
    :   Parent campaign ID

    `conversion_learning_mode_type: Any`
    :   oCPM learn mode type

    `created_time: Any`
    :   Creation timestamp (Unix seconds)

    `end_time: Any`
    :   End time (Unix seconds)

    `feed_profile_id: Any`
    :   Feed profile ID

    `id: Any`
    :   Ad group ID

    `lifetime_frequency_cap: Any`
    :   Max impressions per user in 30 days

    `name: Any`
    :   Ad group name

    `optimization_goal_metadata: Any`
    :   Optimization goal metadata

    `pacing_delivery_type: Any`
    :   Pacing delivery type

    `placement_group: Any`
    :   Placement group

    `start_time: Any`
    :   Start time (Unix seconds)

    `status: Any`
    :   Entity status

    `summary_status: Any`
    :   Summary status

    `targeting_spec: Any`
    :   Targeting specifications

    `tracking_urls: Any`
    :   Third-party tracking URLs

    `type_: Any`
    :   Always 'adgroup'

    `updated_time: Any`
    :   Last update timestamp (Unix seconds)

`AdGroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pinterest.types.AdGroupsAnyValueFilter`
    :   The type of the None singleton.

`AdGroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pinterest.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pinterest.types.AdGroupsStringFilter`
    :   The type of the None singleton.

`AdGroupsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pinterest.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pinterest.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.pinterest.types.AdGroupsInFilter`
    :   The type of the None singleton.

`AdGroupsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: list[str]`
    :   Ad account ID

    `auto_targeting_enabled: list[bool]`
    :   Whether auto targeting is enabled

    `bid_in_micro_currency: list[float]`
    :   Bid in microcurrency

    `bid_strategy_type: list[str]`
    :   Bid strategy type

    `billable_event: list[str]`
    :   Billable event type

    `budget_in_micro_currency: list[float]`
    :   Budget in microcurrency

    `budget_type: list[str]`
    :   Budget type

    `campaign_id: list[str]`
    :   Parent campaign ID

    `conversion_learning_mode_type: list[str]`
    :   oCPM learn mode type

    `created_time: list[float]`
    :   Creation timestamp (Unix seconds)

    `end_time: list[float]`
    :   End time (Unix seconds)

    `feed_profile_id: list[str]`
    :   Feed profile ID

    `id: list[str]`
    :   Ad group ID

    `lifetime_frequency_cap: list[float]`
    :   Max impressions per user in 30 days

    `name: list[str]`
    :   Ad group name

    `optimization_goal_metadata: list[dict[str, typing.Any]]`
    :   Optimization goal metadata

    `pacing_delivery_type: list[str]`
    :   Pacing delivery type

    `placement_group: list[str]`
    :   Placement group

    `start_time: list[float]`
    :   Start time (Unix seconds)

    `status: list[str]`
    :   Entity status

    `summary_status: list[str]`
    :   Summary status

    `targeting_spec: list[dict[str, typing.Any]]`
    :   Targeting specifications

    `tracking_urls: list[dict[str, typing.Any]]`
    :   Third-party tracking URLs

    `type_: list[str]`
    :   Always 'adgroup'

    `updated_time: list[float]`
    :   Last update timestamp (Unix seconds)

`AdGroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pinterest.types.AdGroupsStringFilter`
    :   The type of the None singleton.

`AdGroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pinterest.types.AdGroupsStringFilter`
    :   The type of the None singleton.

`AdGroupsListParams(*args, **kwargs)`
:   Parameters for ad_groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

    `bookmark: str`
    :   The type of the None singleton.

    `entity_statuses: list[str]`
    :   The type of the None singleton.

    `order: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`AdGroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pinterest.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pinterest.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pinterest.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.pinterest.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsAnyCondition`
    :   The type of the None singleton.

`AdGroupsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.pinterest.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsAnyCondition]`
    :   The type of the None singleton.

`AdGroupsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_groups search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str | None`
    :   Ad account ID

    `auto_targeting_enabled: bool | None`
    :   Whether auto targeting is enabled

    `bid_in_micro_currency: float | None`
    :   Bid in microcurrency

    `bid_strategy_type: str | None`
    :   Bid strategy type

    `billable_event: str | None`
    :   Billable event type

    `budget_in_micro_currency: float | None`
    :   Budget in microcurrency

    `budget_type: str | None`
    :   Budget type

    `campaign_id: str | None`
    :   Parent campaign ID

    `conversion_learning_mode_type: str | None`
    :   oCPM learn mode type

    `created_time: float | None`
    :   Creation timestamp (Unix seconds)

    `end_time: float | None`
    :   End time (Unix seconds)

    `feed_profile_id: str | None`
    :   Feed profile ID

    `id: str | None`
    :   Ad group ID

    `lifetime_frequency_cap: float | None`
    :   Max impressions per user in 30 days

    `name: str | None`
    :   Ad group name

    `optimization_goal_metadata: dict[str, typing.Any] | None`
    :   Optimization goal metadata

    `pacing_delivery_type: str | None`
    :   Pacing delivery type

    `placement_group: str | None`
    :   Placement group

    `start_time: float | None`
    :   Start time (Unix seconds)

    `status: str | None`
    :   Entity status

    `summary_status: str | None`
    :   Summary status

    `targeting_spec: dict[str, typing.Any] | None`
    :   Targeting specifications

    `tracking_urls: dict[str, typing.Any] | None`
    :   Third-party tracking URLs

    `type_: str | None`
    :   Always 'adgroup'

    `updated_time: float | None`
    :   Last update timestamp (Unix seconds)

`AdGroupsSearchQuery(*args, **kwargs)`
:   Search query for ad_groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pinterest.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AdGroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pinterest.types.AdGroupsSortFilter]`
    :   The type of the None singleton.

`AdGroupsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_groups search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Literal['asc', 'desc']`
    :   Ad account ID

    `auto_targeting_enabled: Literal['asc', 'desc']`
    :   Whether auto targeting is enabled

    `bid_in_micro_currency: Literal['asc', 'desc']`
    :   Bid in microcurrency

    `bid_strategy_type: Literal['asc', 'desc']`
    :   Bid strategy type

    `billable_event: Literal['asc', 'desc']`
    :   Billable event type

    `budget_in_micro_currency: Literal['asc', 'desc']`
    :   Budget in microcurrency

    `budget_type: Literal['asc', 'desc']`
    :   Budget type

    `campaign_id: Literal['asc', 'desc']`
    :   Parent campaign ID

    `conversion_learning_mode_type: Literal['asc', 'desc']`
    :   oCPM learn mode type

    `created_time: Literal['asc', 'desc']`
    :   Creation timestamp (Unix seconds)

    `end_time: Literal['asc', 'desc']`
    :   End time (Unix seconds)

    `feed_profile_id: Literal['asc', 'desc']`
    :   Feed profile ID

    `id: Literal['asc', 'desc']`
    :   Ad group ID

    `lifetime_frequency_cap: Literal['asc', 'desc']`
    :   Max impressions per user in 30 days

    `name: Literal['asc', 'desc']`
    :   Ad group name

    `optimization_goal_metadata: Literal['asc', 'desc']`
    :   Optimization goal metadata

    `pacing_delivery_type: Literal['asc', 'desc']`
    :   Pacing delivery type

    `placement_group: Literal['asc', 'desc']`
    :   Placement group

    `start_time: Literal['asc', 'desc']`
    :   Start time (Unix seconds)

    `status: Literal['asc', 'desc']`
    :   Entity status

    `summary_status: Literal['asc', 'desc']`
    :   Summary status

    `targeting_spec: Literal['asc', 'desc']`
    :   Targeting specifications

    `tracking_urls: Literal['asc', 'desc']`
    :   Third-party tracking URLs

    `type_: Literal['asc', 'desc']`
    :   Always 'adgroup'

    `updated_time: Literal['asc', 'desc']`
    :   Last update timestamp (Unix seconds)

`AdGroupsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   Ad account ID

    `auto_targeting_enabled: str`
    :   Whether auto targeting is enabled

    `bid_in_micro_currency: str`
    :   Bid in microcurrency

    `bid_strategy_type: str`
    :   Bid strategy type

    `billable_event: str`
    :   Billable event type

    `budget_in_micro_currency: str`
    :   Budget in microcurrency

    `budget_type: str`
    :   Budget type

    `campaign_id: str`
    :   Parent campaign ID

    `conversion_learning_mode_type: str`
    :   oCPM learn mode type

    `created_time: str`
    :   Creation timestamp (Unix seconds)

    `end_time: str`
    :   End time (Unix seconds)

    `feed_profile_id: str`
    :   Feed profile ID

    `id: str`
    :   Ad group ID

    `lifetime_frequency_cap: str`
    :   Max impressions per user in 30 days

    `name: str`
    :   Ad group name

    `optimization_goal_metadata: str`
    :   Optimization goal metadata

    `pacing_delivery_type: str`
    :   Pacing delivery type

    `placement_group: str`
    :   Placement group

    `start_time: str`
    :   Start time (Unix seconds)

    `status: str`
    :   Entity status

    `summary_status: str`
    :   Summary status

    `targeting_spec: str`
    :   Targeting specifications

    `tracking_urls: str`
    :   Third-party tracking URLs

    `type_: str`
    :   Always 'adgroup'

    `updated_time: str`
    :   Last update timestamp (Unix seconds)

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

    `and: list[airbyte_agent_sdk.connectors.pinterest.types.AdsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsInCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.pinterest.types.AdsAnyValueFilter`
    :   The type of the None singleton.

`AdsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Any`
    :   Ad account ID

    `ad_group_id: Any`
    :   Ad group ID

    `android_deep_link: Any`
    :   Android deep link

    `campaign_id: Any`
    :   Campaign ID

    `carousel_android_deep_links: Any`
    :   Carousel Android deep links

    `carousel_destination_urls: Any`
    :   Carousel destination URLs

    `carousel_ios_deep_links: Any`
    :   Carousel iOS deep links

    `click_tracking_url: Any`
    :   Click tracking URL

    `collection_items_destination_url_template: Any`
    :   Template URL for collection items

    `created_time: Any`
    :   Creation timestamp (Unix seconds)

    `creative_type: Any`
    :   Creative type

    `destination_url: Any`
    :   Main destination URL

    `id: Any`
    :   Unique ad ID

    `ios_deep_link: Any`
    :   iOS deep link

    `is_pin_deleted: Any`
    :   Whether the original pin is deleted

    `is_removable: Any`
    :   Whether the ad is removable

    `lead_form_id: Any`
    :   Lead form ID

    `name: Any`
    :   Ad name

    `pin_id: Any`
    :   Associated pin ID

    `rejected_reasons: Any`
    :   Rejection reasons

    `rejection_labels: Any`
    :   Rejection text labels

    `review_status: Any`
    :   Review status

    `status: Any`
    :   Entity status

    `summary_status: Any`
    :   Summary status

    `tracking_urls: Any`
    :   Third-party tracking URLs

    `type_: Any`
    :   Always 'pinpromotion'

    `updated_time: Any`
    :   Last update timestamp (Unix seconds)

    `view_tracking_url: Any`
    :   View tracking URL

`AdsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pinterest.types.AdsAnyValueFilter`
    :   The type of the None singleton.

`AdsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pinterest.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pinterest.types.AdsStringFilter`
    :   The type of the None singleton.

`AdsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pinterest.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pinterest.types.AdsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.pinterest.types.AdsInFilter`
    :   The type of the None singleton.

`AdsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: list[str]`
    :   Ad account ID

    `ad_group_id: list[str]`
    :   Ad group ID

    `android_deep_link: list[str]`
    :   Android deep link

    `campaign_id: list[str]`
    :   Campaign ID

    `carousel_android_deep_links: list[list[typing.Any]]`
    :   Carousel Android deep links

    `carousel_destination_urls: list[list[typing.Any]]`
    :   Carousel destination URLs

    `carousel_ios_deep_links: list[list[typing.Any]]`
    :   Carousel iOS deep links

    `click_tracking_url: list[str]`
    :   Click tracking URL

    `collection_items_destination_url_template: list[str]`
    :   Template URL for collection items

    `created_time: list[int]`
    :   Creation timestamp (Unix seconds)

    `creative_type: list[str]`
    :   Creative type

    `destination_url: list[str]`
    :   Main destination URL

    `id: list[str]`
    :   Unique ad ID

    `ios_deep_link: list[str]`
    :   iOS deep link

    `is_pin_deleted: list[bool]`
    :   Whether the original pin is deleted

    `is_removable: list[bool]`
    :   Whether the ad is removable

    `lead_form_id: list[str]`
    :   Lead form ID

    `name: list[str]`
    :   Ad name

    `pin_id: list[str]`
    :   Associated pin ID

    `rejected_reasons: list[list[typing.Any]]`
    :   Rejection reasons

    `rejection_labels: list[list[typing.Any]]`
    :   Rejection text labels

    `review_status: list[str]`
    :   Review status

    `status: list[str]`
    :   Entity status

    `summary_status: list[str]`
    :   Summary status

    `tracking_urls: list[dict[str, typing.Any]]`
    :   Third-party tracking URLs

    `type_: list[str]`
    :   Always 'pinpromotion'

    `updated_time: list[int]`
    :   Last update timestamp (Unix seconds)

    `view_tracking_url: list[str]`
    :   View tracking URL

`AdsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pinterest.types.AdsStringFilter`
    :   The type of the None singleton.

`AdsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pinterest.types.AdsStringFilter`
    :   The type of the None singleton.

`AdsListParams(*args, **kwargs)`
:   Parameters for ads.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

    `bookmark: str`
    :   The type of the None singleton.

    `entity_statuses: list[str]`
    :   The type of the None singleton.

    `order: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`AdsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pinterest.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pinterest.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pinterest.types.AdsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.pinterest.types.AdsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsInCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.pinterest.types.AdsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsInCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsAnyCondition]`
    :   The type of the None singleton.

`AdsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ads search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str | None`
    :   Ad account ID

    `ad_group_id: str | None`
    :   Ad group ID

    `android_deep_link: str | None`
    :   Android deep link

    `campaign_id: str | None`
    :   Campaign ID

    `carousel_android_deep_links: list[typing.Any] | None`
    :   Carousel Android deep links

    `carousel_destination_urls: list[typing.Any] | None`
    :   Carousel destination URLs

    `carousel_ios_deep_links: list[typing.Any] | None`
    :   Carousel iOS deep links

    `click_tracking_url: str | None`
    :   Click tracking URL

    `collection_items_destination_url_template: str | None`
    :   Template URL for collection items

    `created_time: int | None`
    :   Creation timestamp (Unix seconds)

    `creative_type: str | None`
    :   Creative type

    `destination_url: str | None`
    :   Main destination URL

    `id: str | None`
    :   Unique ad ID

    `ios_deep_link: str | None`
    :   iOS deep link

    `is_pin_deleted: bool | None`
    :   Whether the original pin is deleted

    `is_removable: bool | None`
    :   Whether the ad is removable

    `lead_form_id: str | None`
    :   Lead form ID

    `name: str | None`
    :   Ad name

    `pin_id: str | None`
    :   Associated pin ID

    `rejected_reasons: list[typing.Any] | None`
    :   Rejection reasons

    `rejection_labels: list[typing.Any] | None`
    :   Rejection text labels

    `review_status: str | None`
    :   Review status

    `status: str | None`
    :   Entity status

    `summary_status: str | None`
    :   Summary status

    `tracking_urls: dict[str, typing.Any] | None`
    :   Third-party tracking URLs

    `type_: str | None`
    :   Always 'pinpromotion'

    `updated_time: int | None`
    :   Last update timestamp (Unix seconds)

    `view_tracking_url: str | None`
    :   View tracking URL

`AdsSearchQuery(*args, **kwargs)`
:   Search query for ads entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pinterest.types.AdsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsInCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AdsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pinterest.types.AdsSortFilter]`
    :   The type of the None singleton.

`AdsSortFilter(*args, **kwargs)`
:   Available fields for sorting ads search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Literal['asc', 'desc']`
    :   Ad account ID

    `ad_group_id: Literal['asc', 'desc']`
    :   Ad group ID

    `android_deep_link: Literal['asc', 'desc']`
    :   Android deep link

    `campaign_id: Literal['asc', 'desc']`
    :   Campaign ID

    `carousel_android_deep_links: Literal['asc', 'desc']`
    :   Carousel Android deep links

    `carousel_destination_urls: Literal['asc', 'desc']`
    :   Carousel destination URLs

    `carousel_ios_deep_links: Literal['asc', 'desc']`
    :   Carousel iOS deep links

    `click_tracking_url: Literal['asc', 'desc']`
    :   Click tracking URL

    `collection_items_destination_url_template: Literal['asc', 'desc']`
    :   Template URL for collection items

    `created_time: Literal['asc', 'desc']`
    :   Creation timestamp (Unix seconds)

    `creative_type: Literal['asc', 'desc']`
    :   Creative type

    `destination_url: Literal['asc', 'desc']`
    :   Main destination URL

    `id: Literal['asc', 'desc']`
    :   Unique ad ID

    `ios_deep_link: Literal['asc', 'desc']`
    :   iOS deep link

    `is_pin_deleted: Literal['asc', 'desc']`
    :   Whether the original pin is deleted

    `is_removable: Literal['asc', 'desc']`
    :   Whether the ad is removable

    `lead_form_id: Literal['asc', 'desc']`
    :   Lead form ID

    `name: Literal['asc', 'desc']`
    :   Ad name

    `pin_id: Literal['asc', 'desc']`
    :   Associated pin ID

    `rejected_reasons: Literal['asc', 'desc']`
    :   Rejection reasons

    `rejection_labels: Literal['asc', 'desc']`
    :   Rejection text labels

    `review_status: Literal['asc', 'desc']`
    :   Review status

    `status: Literal['asc', 'desc']`
    :   Entity status

    `summary_status: Literal['asc', 'desc']`
    :   Summary status

    `tracking_urls: Literal['asc', 'desc']`
    :   Third-party tracking URLs

    `type_: Literal['asc', 'desc']`
    :   Always 'pinpromotion'

    `updated_time: Literal['asc', 'desc']`
    :   Last update timestamp (Unix seconds)

    `view_tracking_url: Literal['asc', 'desc']`
    :   View tracking URL

`AdsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   Ad account ID

    `ad_group_id: str`
    :   Ad group ID

    `android_deep_link: str`
    :   Android deep link

    `campaign_id: str`
    :   Campaign ID

    `carousel_android_deep_links: str`
    :   Carousel Android deep links

    `carousel_destination_urls: str`
    :   Carousel destination URLs

    `carousel_ios_deep_links: str`
    :   Carousel iOS deep links

    `click_tracking_url: str`
    :   Click tracking URL

    `collection_items_destination_url_template: str`
    :   Template URL for collection items

    `created_time: str`
    :   Creation timestamp (Unix seconds)

    `creative_type: str`
    :   Creative type

    `destination_url: str`
    :   Main destination URL

    `id: str`
    :   Unique ad ID

    `ios_deep_link: str`
    :   iOS deep link

    `is_pin_deleted: str`
    :   Whether the original pin is deleted

    `is_removable: str`
    :   Whether the ad is removable

    `lead_form_id: str`
    :   Lead form ID

    `name: str`
    :   Ad name

    `pin_id: str`
    :   Associated pin ID

    `rejected_reasons: str`
    :   Rejection reasons

    `rejection_labels: str`
    :   Rejection text labels

    `review_status: str`
    :   Review status

    `status: str`
    :   Entity status

    `summary_status: str`
    :   Summary status

    `tracking_urls: str`
    :   Third-party tracking URLs

    `type_: str`
    :   Always 'pinpromotion'

    `updated_time: str`
    :   Last update timestamp (Unix seconds)

    `view_tracking_url: str`
    :   View tracking URL

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

`AudiencesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.pinterest.types.AudiencesEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesInCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesAnyCondition]`
    :   The type of the None singleton.

`AudiencesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.pinterest.types.AudiencesAnyValueFilter`
    :   The type of the None singleton.

`AudiencesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Any`
    :   Ad account ID

    `audience_type: Any`
    :   Audience type

    `created_timestamp: Any`
    :   Creation time (Unix seconds)

    `description: Any`
    :   Audience description

    `id: Any`
    :   Unique audience identifier

    `name: Any`
    :   Audience name

    `rule: Any`
    :   Audience targeting rules

    `size: Any`
    :   Estimated audience size

    `status: Any`
    :   Audience status

    `type_: Any`
    :   Always 'audience'

    `updated_timestamp: Any`
    :   Last update time (Unix seconds)

`AudiencesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pinterest.types.AudiencesAnyValueFilter`
    :   The type of the None singleton.

`AudiencesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pinterest.types.AudiencesSearchFilter`
    :   The type of the None singleton.

`AudiencesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pinterest.types.AudiencesStringFilter`
    :   The type of the None singleton.

`AudiencesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pinterest.types.AudiencesSearchFilter`
    :   The type of the None singleton.

`AudiencesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pinterest.types.AudiencesSearchFilter`
    :   The type of the None singleton.

`AudiencesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.pinterest.types.AudiencesInFilter`
    :   The type of the None singleton.

`AudiencesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: list[str]`
    :   Ad account ID

    `audience_type: list[str]`
    :   Audience type

    `created_timestamp: list[int]`
    :   Creation time (Unix seconds)

    `description: list[str]`
    :   Audience description

    `id: list[str]`
    :   Unique audience identifier

    `name: list[str]`
    :   Audience name

    `rule: list[dict[str, typing.Any]]`
    :   Audience targeting rules

    `size: list[int]`
    :   Estimated audience size

    `status: list[str]`
    :   Audience status

    `type_: list[str]`
    :   Always 'audience'

    `updated_timestamp: list[int]`
    :   Last update time (Unix seconds)

`AudiencesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pinterest.types.AudiencesStringFilter`
    :   The type of the None singleton.

`AudiencesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pinterest.types.AudiencesStringFilter`
    :   The type of the None singleton.

`AudiencesListParams(*args, **kwargs)`
:   Parameters for audiences.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

    `bookmark: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`AudiencesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pinterest.types.AudiencesSearchFilter`
    :   The type of the None singleton.

`AudiencesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pinterest.types.AudiencesSearchFilter`
    :   The type of the None singleton.

`AudiencesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pinterest.types.AudiencesSearchFilter`
    :   The type of the None singleton.

`AudiencesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.pinterest.types.AudiencesEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesInCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesAnyCondition`
    :   The type of the None singleton.

`AudiencesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.pinterest.types.AudiencesEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesInCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesAnyCondition]`
    :   The type of the None singleton.

`AudiencesSearchFilter(*args, **kwargs)`
:   Available fields for filtering audiences search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str | None`
    :   Ad account ID

    `audience_type: str | None`
    :   Audience type

    `created_timestamp: int | None`
    :   Creation time (Unix seconds)

    `description: str | None`
    :   Audience description

    `id: str | None`
    :   Unique audience identifier

    `name: str | None`
    :   Audience name

    `rule: dict[str, typing.Any] | None`
    :   Audience targeting rules

    `size: int | None`
    :   Estimated audience size

    `status: str | None`
    :   Audience status

    `type_: str | None`
    :   Always 'audience'

    `updated_timestamp: int | None`
    :   Last update time (Unix seconds)

`AudiencesSearchQuery(*args, **kwargs)`
:   Search query for audiences entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pinterest.types.AudiencesEqCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesGtCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesGteCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesLtCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesLteCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesInCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesNotCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesAndCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesOrCondition | airbyte_agent_sdk.connectors.pinterest.types.AudiencesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pinterest.types.AudiencesSortFilter]`
    :   The type of the None singleton.

`AudiencesSortFilter(*args, **kwargs)`
:   Available fields for sorting audiences search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Literal['asc', 'desc']`
    :   Ad account ID

    `audience_type: Literal['asc', 'desc']`
    :   Audience type

    `created_timestamp: Literal['asc', 'desc']`
    :   Creation time (Unix seconds)

    `description: Literal['asc', 'desc']`
    :   Audience description

    `id: Literal['asc', 'desc']`
    :   Unique audience identifier

    `name: Literal['asc', 'desc']`
    :   Audience name

    `rule: Literal['asc', 'desc']`
    :   Audience targeting rules

    `size: Literal['asc', 'desc']`
    :   Estimated audience size

    `status: Literal['asc', 'desc']`
    :   Audience status

    `type_: Literal['asc', 'desc']`
    :   Always 'audience'

    `updated_timestamp: Literal['asc', 'desc']`
    :   Last update time (Unix seconds)

`AudiencesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   Ad account ID

    `audience_type: str`
    :   Audience type

    `created_timestamp: str`
    :   Creation time (Unix seconds)

    `description: str`
    :   Audience description

    `id: str`
    :   Unique audience identifier

    `name: str`
    :   Audience name

    `rule: str`
    :   Audience targeting rules

    `size: str`
    :   Estimated audience size

    `status: str`
    :   Audience status

    `type_: str`
    :   Always 'audience'

    `updated_timestamp: str`
    :   Last update time (Unix seconds)

`BoardPinsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.pinterest.types.BoardPinsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsInCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsAnyCondition]`
    :   The type of the None singleton.

`BoardPinsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.pinterest.types.BoardPinsAnyValueFilter`
    :   The type of the None singleton.

`BoardPinsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alt_text: Any`
    :   Alternate text for accessibility

    `board_id: Any`
    :   Board the pin belongs to

    `board_owner: Any`
    :   Board owner info

    `board_section_id: Any`
    :   Section within the board

    `created_at: Any`
    :   Timestamp when the pin was created

    `creative_type: Any`
    :   Creative type

    `description: Any`
    :   Pin description

    `dominant_color: Any`
    :   Dominant color from the pin image

    `has_been_promoted: Any`
    :   Whether the pin has been promoted

    `id: Any`
    :   Unique pin identifier

    `is_owner: Any`
    :   Whether the current user is the owner

    `is_standard: Any`
    :   Whether the pin is a standard pin

    `link: Any`
    :   URL link associated with the pin

    `media: Any`
    :   Media content

    `parent_pin_id: Any`
    :   Parent pin ID if this is a repin

    `pin_metrics: Any`
    :   Pin metrics data

    `title: Any`
    :   Pin title

`BoardPinsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pinterest.types.BoardPinsAnyValueFilter`
    :   The type of the None singleton.

`BoardPinsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pinterest.types.BoardPinsSearchFilter`
    :   The type of the None singleton.

`BoardPinsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pinterest.types.BoardPinsStringFilter`
    :   The type of the None singleton.

`BoardPinsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pinterest.types.BoardPinsSearchFilter`
    :   The type of the None singleton.

`BoardPinsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pinterest.types.BoardPinsSearchFilter`
    :   The type of the None singleton.

`BoardPinsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.pinterest.types.BoardPinsInFilter`
    :   The type of the None singleton.

`BoardPinsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alt_text: list[str]`
    :   Alternate text for accessibility

    `board_id: list[str]`
    :   Board the pin belongs to

    `board_owner: list[dict[str, typing.Any]]`
    :   Board owner info

    `board_section_id: list[str]`
    :   Section within the board

    `created_at: list[str]`
    :   Timestamp when the pin was created

    `creative_type: list[str]`
    :   Creative type

    `description: list[str]`
    :   Pin description

    `dominant_color: list[str]`
    :   Dominant color from the pin image

    `has_been_promoted: list[bool]`
    :   Whether the pin has been promoted

    `id: list[str]`
    :   Unique pin identifier

    `is_owner: list[bool]`
    :   Whether the current user is the owner

    `is_standard: list[bool]`
    :   Whether the pin is a standard pin

    `link: list[str]`
    :   URL link associated with the pin

    `media: list[dict[str, typing.Any]]`
    :   Media content

    `parent_pin_id: list[str]`
    :   Parent pin ID if this is a repin

    `pin_metrics: list[dict[str, typing.Any]]`
    :   Pin metrics data

    `title: list[str]`
    :   Pin title

`BoardPinsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pinterest.types.BoardPinsStringFilter`
    :   The type of the None singleton.

`BoardPinsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pinterest.types.BoardPinsStringFilter`
    :   The type of the None singleton.

`BoardPinsListParams(*args, **kwargs)`
:   Parameters for board_pins.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_id: str`
    :   The type of the None singleton.

    `bookmark: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`BoardPinsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pinterest.types.BoardPinsSearchFilter`
    :   The type of the None singleton.

`BoardPinsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pinterest.types.BoardPinsSearchFilter`
    :   The type of the None singleton.

`BoardPinsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pinterest.types.BoardPinsSearchFilter`
    :   The type of the None singleton.

`BoardPinsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.pinterest.types.BoardPinsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsInCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsAnyCondition`
    :   The type of the None singleton.

`BoardPinsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.pinterest.types.BoardPinsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsInCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsAnyCondition]`
    :   The type of the None singleton.

`BoardPinsSearchFilter(*args, **kwargs)`
:   Available fields for filtering board_pins search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alt_text: str | None`
    :   Alternate text for accessibility

    `board_id: str | None`
    :   Board the pin belongs to

    `board_owner: dict[str, typing.Any] | None`
    :   Board owner info

    `board_section_id: str | None`
    :   Section within the board

    `created_at: str | None`
    :   Timestamp when the pin was created

    `creative_type: str | None`
    :   Creative type

    `description: str | None`
    :   Pin description

    `dominant_color: str | None`
    :   Dominant color from the pin image

    `has_been_promoted: bool | None`
    :   Whether the pin has been promoted

    `id: str | None`
    :   Unique pin identifier

    `is_owner: bool | None`
    :   Whether the current user is the owner

    `is_standard: bool | None`
    :   Whether the pin is a standard pin

    `link: str | None`
    :   URL link associated with the pin

    `media: dict[str, typing.Any] | None`
    :   Media content

    `parent_pin_id: str | None`
    :   Parent pin ID if this is a repin

    `pin_metrics: dict[str, typing.Any] | None`
    :   Pin metrics data

    `title: str | None`
    :   Pin title

`BoardPinsSearchQuery(*args, **kwargs)`
:   Search query for board_pins entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pinterest.types.BoardPinsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsInCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardPinsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pinterest.types.BoardPinsSortFilter]`
    :   The type of the None singleton.

`BoardPinsSortFilter(*args, **kwargs)`
:   Available fields for sorting board_pins search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alt_text: Literal['asc', 'desc']`
    :   Alternate text for accessibility

    `board_id: Literal['asc', 'desc']`
    :   Board the pin belongs to

    `board_owner: Literal['asc', 'desc']`
    :   Board owner info

    `board_section_id: Literal['asc', 'desc']`
    :   Section within the board

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the pin was created

    `creative_type: Literal['asc', 'desc']`
    :   Creative type

    `description: Literal['asc', 'desc']`
    :   Pin description

    `dominant_color: Literal['asc', 'desc']`
    :   Dominant color from the pin image

    `has_been_promoted: Literal['asc', 'desc']`
    :   Whether the pin has been promoted

    `id: Literal['asc', 'desc']`
    :   Unique pin identifier

    `is_owner: Literal['asc', 'desc']`
    :   Whether the current user is the owner

    `is_standard: Literal['asc', 'desc']`
    :   Whether the pin is a standard pin

    `link: Literal['asc', 'desc']`
    :   URL link associated with the pin

    `media: Literal['asc', 'desc']`
    :   Media content

    `parent_pin_id: Literal['asc', 'desc']`
    :   Parent pin ID if this is a repin

    `pin_metrics: Literal['asc', 'desc']`
    :   Pin metrics data

    `title: Literal['asc', 'desc']`
    :   Pin title

`BoardPinsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alt_text: str`
    :   Alternate text for accessibility

    `board_id: str`
    :   Board the pin belongs to

    `board_owner: str`
    :   Board owner info

    `board_section_id: str`
    :   Section within the board

    `created_at: str`
    :   Timestamp when the pin was created

    `creative_type: str`
    :   Creative type

    `description: str`
    :   Pin description

    `dominant_color: str`
    :   Dominant color from the pin image

    `has_been_promoted: str`
    :   Whether the pin has been promoted

    `id: str`
    :   Unique pin identifier

    `is_owner: str`
    :   Whether the current user is the owner

    `is_standard: str`
    :   Whether the pin is a standard pin

    `link: str`
    :   URL link associated with the pin

    `media: str`
    :   Media content

    `parent_pin_id: str`
    :   Parent pin ID if this is a repin

    `pin_metrics: str`
    :   Pin metrics data

    `title: str`
    :   Pin title

`BoardSectionsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsInCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsAnyCondition]`
    :   The type of the None singleton.

`BoardSectionsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsAnyValueFilter`
    :   The type of the None singleton.

`BoardSectionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier for the board section

    `name: Any`
    :   Name of the board section

`BoardSectionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsAnyValueFilter`
    :   The type of the None singleton.

`BoardSectionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsSearchFilter`
    :   The type of the None singleton.

`BoardSectionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsStringFilter`
    :   The type of the None singleton.

`BoardSectionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsSearchFilter`
    :   The type of the None singleton.

`BoardSectionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsSearchFilter`
    :   The type of the None singleton.

`BoardSectionsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsInFilter`
    :   The type of the None singleton.

`BoardSectionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[str]`
    :   Unique identifier for the board section

    `name: list[str]`
    :   Name of the board section

`BoardSectionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsStringFilter`
    :   The type of the None singleton.

`BoardSectionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsStringFilter`
    :   The type of the None singleton.

`BoardSectionsListParams(*args, **kwargs)`
:   Parameters for board_sections.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_id: str`
    :   The type of the None singleton.

    `bookmark: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`BoardSectionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsSearchFilter`
    :   The type of the None singleton.

`BoardSectionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsSearchFilter`
    :   The type of the None singleton.

`BoardSectionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsSearchFilter`
    :   The type of the None singleton.

`BoardSectionsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsInCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsAnyCondition`
    :   The type of the None singleton.

`BoardSectionsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsInCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsAnyCondition]`
    :   The type of the None singleton.

`BoardSectionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering board_sections search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str | None`
    :   Unique identifier for the board section

    `name: str | None`
    :   Name of the board section

`BoardSectionsSearchQuery(*args, **kwargs)`
:   Search query for board_sections entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsInCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pinterest.types.BoardSectionsSortFilter]`
    :   The type of the None singleton.

`BoardSectionsSortFilter(*args, **kwargs)`
:   Available fields for sorting board_sections search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the board section

    `name: Literal['asc', 'desc']`
    :   Name of the board section

`BoardSectionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the board section

    `name: str`
    :   Name of the board section

`BoardsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.pinterest.types.BoardsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsInCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsAnyCondition]`
    :   The type of the None singleton.

`BoardsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.pinterest.types.BoardsAnyValueFilter`
    :   The type of the None singleton.

`BoardsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_pins_modified_at: Any`
    :   Timestamp when pins on the board were last modified

    `collaborator_count: Any`
    :   Number of collaborators

    `created_at: Any`
    :   Timestamp when the board was created

    `description: Any`
    :   Board description

    `follower_count: Any`
    :   Number of followers

    `id: Any`
    :   Unique identifier for the board

    `media: Any`
    :   Media content for the board

    `name: Any`
    :   Board name

    `owner: Any`
    :   Board owner details

    `pin_count: Any`
    :   Number of pins on the board

    `privacy: Any`
    :   Board privacy setting

`BoardsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pinterest.types.BoardsAnyValueFilter`
    :   The type of the None singleton.

`BoardsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pinterest.types.BoardsSearchFilter`
    :   The type of the None singleton.

`BoardsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pinterest.types.BoardsStringFilter`
    :   The type of the None singleton.

`BoardsGetParams(*args, **kwargs)`
:   Parameters for boards.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_id: str`
    :   The type of the None singleton.

`BoardsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pinterest.types.BoardsSearchFilter`
    :   The type of the None singleton.

`BoardsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pinterest.types.BoardsSearchFilter`
    :   The type of the None singleton.

`BoardsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.pinterest.types.BoardsInFilter`
    :   The type of the None singleton.

`BoardsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_pins_modified_at: list[str]`
    :   Timestamp when pins on the board were last modified

    `collaborator_count: list[int]`
    :   Number of collaborators

    `created_at: list[str]`
    :   Timestamp when the board was created

    `description: list[str]`
    :   Board description

    `follower_count: list[int]`
    :   Number of followers

    `id: list[str]`
    :   Unique identifier for the board

    `media: list[dict[str, typing.Any]]`
    :   Media content for the board

    `name: list[str]`
    :   Board name

    `owner: list[dict[str, typing.Any]]`
    :   Board owner details

    `pin_count: list[int]`
    :   Number of pins on the board

    `privacy: list[str]`
    :   Board privacy setting

`BoardsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pinterest.types.BoardsStringFilter`
    :   The type of the None singleton.

`BoardsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pinterest.types.BoardsStringFilter`
    :   The type of the None singleton.

`BoardsListParams(*args, **kwargs)`
:   Parameters for boards.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bookmark: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `privacy: str`
    :   The type of the None singleton.

`BoardsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pinterest.types.BoardsSearchFilter`
    :   The type of the None singleton.

`BoardsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pinterest.types.BoardsSearchFilter`
    :   The type of the None singleton.

`BoardsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pinterest.types.BoardsSearchFilter`
    :   The type of the None singleton.

`BoardsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.pinterest.types.BoardsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsInCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsAnyCondition`
    :   The type of the None singleton.

`BoardsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.pinterest.types.BoardsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsInCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsAnyCondition]`
    :   The type of the None singleton.

`BoardsSearchFilter(*args, **kwargs)`
:   Available fields for filtering boards search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_pins_modified_at: str | None`
    :   Timestamp when pins on the board were last modified

    `collaborator_count: int | None`
    :   Number of collaborators

    `created_at: str | None`
    :   Timestamp when the board was created

    `description: str | None`
    :   Board description

    `follower_count: int | None`
    :   Number of followers

    `id: str | None`
    :   Unique identifier for the board

    `media: dict[str, typing.Any] | None`
    :   Media content for the board

    `name: str | None`
    :   Board name

    `owner: dict[str, typing.Any] | None`
    :   Board owner details

    `pin_count: int | None`
    :   Number of pins on the board

    `privacy: str | None`
    :   Board privacy setting

`BoardsSearchQuery(*args, **kwargs)`
:   Search query for boards entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pinterest.types.BoardsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsInCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.BoardsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pinterest.types.BoardsSortFilter]`
    :   The type of the None singleton.

`BoardsSortFilter(*args, **kwargs)`
:   Available fields for sorting boards search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_pins_modified_at: Literal['asc', 'desc']`
    :   Timestamp when pins on the board were last modified

    `collaborator_count: Literal['asc', 'desc']`
    :   Number of collaborators

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the board was created

    `description: Literal['asc', 'desc']`
    :   Board description

    `follower_count: Literal['asc', 'desc']`
    :   Number of followers

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the board

    `media: Literal['asc', 'desc']`
    :   Media content for the board

    `name: Literal['asc', 'desc']`
    :   Board name

    `owner: Literal['asc', 'desc']`
    :   Board owner details

    `pin_count: Literal['asc', 'desc']`
    :   Number of pins on the board

    `privacy: Literal['asc', 'desc']`
    :   Board privacy setting

`BoardsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_pins_modified_at: str`
    :   Timestamp when pins on the board were last modified

    `collaborator_count: str`
    :   Number of collaborators

    `created_at: str`
    :   Timestamp when the board was created

    `description: str`
    :   Board description

    `follower_count: str`
    :   Number of followers

    `id: str`
    :   Unique identifier for the board

    `media: str`
    :   Media content for the board

    `name: str`
    :   Board name

    `owner: str`
    :   Board owner details

    `pin_count: str`
    :   Number of pins on the board

    `privacy: str`
    :   Board privacy setting

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

    `and: list[airbyte_agent_sdk.connectors.pinterest.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.pinterest.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

`CampaignsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Any`
    :   Ad account ID

    `created_time: Any`
    :   Creation timestamp (Unix seconds)

    `daily_spend_cap: Any`
    :   Maximum daily spend in microcurrency

    `end_time: Any`
    :   End timestamp (Unix seconds)

    `id: Any`
    :   Campaign ID

    `is_campaign_budget_optimization: Any`
    :   Whether CBO is enabled

    `is_flexible_daily_budgets: Any`
    :   Whether flexible daily budgets are enabled

    `lifetime_spend_cap: Any`
    :   Maximum lifetime spend in microcurrency

    `name: Any`
    :   Campaign name

    `objective_type: Any`
    :   Campaign objective type

    `order_line_id: Any`
    :   Order line ID on invoice

    `start_time: Any`
    :   Start timestamp (Unix seconds)

    `status: Any`
    :   Entity status

    `summary_status: Any`
    :   Summary status

    `tracking_urls: Any`
    :   Third-party tracking URLs

    `type_: Any`
    :   Always 'campaign'

    `updated_time: Any`
    :   Last update timestamp (Unix seconds)

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pinterest.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pinterest.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pinterest.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pinterest.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pinterest.types.CampaignsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.pinterest.types.CampaignsInFilter`
    :   The type of the None singleton.

`CampaignsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: list[str]`
    :   Ad account ID

    `created_time: list[int]`
    :   Creation timestamp (Unix seconds)

    `daily_spend_cap: list[int]`
    :   Maximum daily spend in microcurrency

    `end_time: list[int]`
    :   End timestamp (Unix seconds)

    `id: list[str]`
    :   Campaign ID

    `is_campaign_budget_optimization: list[bool]`
    :   Whether CBO is enabled

    `is_flexible_daily_budgets: list[bool]`
    :   Whether flexible daily budgets are enabled

    `lifetime_spend_cap: list[int]`
    :   Maximum lifetime spend in microcurrency

    `name: list[str]`
    :   Campaign name

    `objective_type: list[str]`
    :   Campaign objective type

    `order_line_id: list[str]`
    :   Order line ID on invoice

    `start_time: list[int]`
    :   Start timestamp (Unix seconds)

    `status: list[str]`
    :   Entity status

    `summary_status: list[str]`
    :   Summary status

    `tracking_urls: list[dict[str, typing.Any]]`
    :   Third-party tracking URLs

    `type_: list[str]`
    :   Always 'campaign'

    `updated_time: list[int]`
    :   Last update timestamp (Unix seconds)

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pinterest.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pinterest.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsListParams(*args, **kwargs)`
:   Parameters for campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

    `bookmark: str`
    :   The type of the None singleton.

    `entity_statuses: list[str]`
    :   The type of the None singleton.

    `order: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pinterest.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pinterest.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pinterest.types.CampaignsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.pinterest.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.pinterest.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

`CampaignsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaigns search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str | None`
    :   Ad account ID

    `created_time: int | None`
    :   Creation timestamp (Unix seconds)

    `daily_spend_cap: int | None`
    :   Maximum daily spend in microcurrency

    `end_time: int | None`
    :   End timestamp (Unix seconds)

    `id: str | None`
    :   Campaign ID

    `is_campaign_budget_optimization: bool | None`
    :   Whether CBO is enabled

    `is_flexible_daily_budgets: bool | None`
    :   Whether flexible daily budgets are enabled

    `lifetime_spend_cap: int | None`
    :   Maximum lifetime spend in microcurrency

    `name: str | None`
    :   Campaign name

    `objective_type: str | None`
    :   Campaign objective type

    `order_line_id: str | None`
    :   Order line ID on invoice

    `start_time: int | None`
    :   Start timestamp (Unix seconds)

    `status: str | None`
    :   Entity status

    `summary_status: str | None`
    :   Summary status

    `tracking_urls: dict[str, typing.Any] | None`
    :   Third-party tracking URLs

    `type_: str | None`
    :   Always 'campaign'

    `updated_time: int | None`
    :   Last update timestamp (Unix seconds)

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pinterest.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pinterest.types.CampaignsSortFilter]`
    :   The type of the None singleton.

`CampaignsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaigns search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Literal['asc', 'desc']`
    :   Ad account ID

    `created_time: Literal['asc', 'desc']`
    :   Creation timestamp (Unix seconds)

    `daily_spend_cap: Literal['asc', 'desc']`
    :   Maximum daily spend in microcurrency

    `end_time: Literal['asc', 'desc']`
    :   End timestamp (Unix seconds)

    `id: Literal['asc', 'desc']`
    :   Campaign ID

    `is_campaign_budget_optimization: Literal['asc', 'desc']`
    :   Whether CBO is enabled

    `is_flexible_daily_budgets: Literal['asc', 'desc']`
    :   Whether flexible daily budgets are enabled

    `lifetime_spend_cap: Literal['asc', 'desc']`
    :   Maximum lifetime spend in microcurrency

    `name: Literal['asc', 'desc']`
    :   Campaign name

    `objective_type: Literal['asc', 'desc']`
    :   Campaign objective type

    `order_line_id: Literal['asc', 'desc']`
    :   Order line ID on invoice

    `start_time: Literal['asc', 'desc']`
    :   Start timestamp (Unix seconds)

    `status: Literal['asc', 'desc']`
    :   Entity status

    `summary_status: Literal['asc', 'desc']`
    :   Summary status

    `tracking_urls: Literal['asc', 'desc']`
    :   Third-party tracking URLs

    `type_: Literal['asc', 'desc']`
    :   Always 'campaign'

    `updated_time: Literal['asc', 'desc']`
    :   Last update timestamp (Unix seconds)

`CampaignsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   Ad account ID

    `created_time: str`
    :   Creation timestamp (Unix seconds)

    `daily_spend_cap: str`
    :   Maximum daily spend in microcurrency

    `end_time: str`
    :   End timestamp (Unix seconds)

    `id: str`
    :   Campaign ID

    `is_campaign_budget_optimization: str`
    :   Whether CBO is enabled

    `is_flexible_daily_budgets: str`
    :   Whether flexible daily budgets are enabled

    `lifetime_spend_cap: str`
    :   Maximum lifetime spend in microcurrency

    `name: str`
    :   Campaign name

    `objective_type: str`
    :   Campaign objective type

    `order_line_id: str`
    :   Order line ID on invoice

    `start_time: str`
    :   Start timestamp (Unix seconds)

    `status: str`
    :   Entity status

    `summary_status: str`
    :   Summary status

    `tracking_urls: str`
    :   Third-party tracking URLs

    `type_: str`
    :   Always 'campaign'

    `updated_time: str`
    :   Last update timestamp (Unix seconds)

`CatalogsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.pinterest.types.CatalogsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsAnyCondition]`
    :   The type of the None singleton.

`CatalogsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.pinterest.types.CatalogsAnyValueFilter`
    :   The type of the None singleton.

`CatalogsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `catalog_type: Any`
    :   Type of catalog

    `created_at: Any`
    :   Timestamp when the catalog was created

    `id: Any`
    :   Unique catalog identifier

    `name: Any`
    :   Catalog name

    `updated_at: Any`
    :   Timestamp when the catalog was last updated

`CatalogsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pinterest.types.CatalogsAnyValueFilter`
    :   The type of the None singleton.

`CatalogsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pinterest.types.CatalogsSearchFilter`
    :   The type of the None singleton.

`CatalogsFeedsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsAnyCondition]`
    :   The type of the None singleton.

`CatalogsFeedsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsAnyValueFilter`
    :   The type of the None singleton.

`CatalogsFeedsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `catalog_type: Any`
    :   Type of catalog

    `created_at: Any`
    :   Timestamp when the feed was created

    `default_availability: Any`
    :   Default availability status

    `default_country: Any`
    :   Default country

    `default_currency: Any`
    :   Default currency for pricing

    `default_locale: Any`
    :   Default locale

    `format: Any`
    :   Feed format

    `id: Any`
    :   Unique feed identifier

    `location: Any`
    :   URL where the feed is available

    `name: Any`
    :   Feed name

    `preferred_processing_schedule: Any`
    :   Preferred processing schedule

    `status: Any`
    :   Feed status

    `updated_at: Any`
    :   Timestamp when the feed was last updated

`CatalogsFeedsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsAnyValueFilter`
    :   The type of the None singleton.

`CatalogsFeedsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsSearchFilter`
    :   The type of the None singleton.

`CatalogsFeedsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsStringFilter`
    :   The type of the None singleton.

`CatalogsFeedsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsSearchFilter`
    :   The type of the None singleton.

`CatalogsFeedsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsSearchFilter`
    :   The type of the None singleton.

`CatalogsFeedsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsInFilter`
    :   The type of the None singleton.

`CatalogsFeedsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `catalog_type: list[str]`
    :   Type of catalog

    `created_at: list[str]`
    :   Timestamp when the feed was created

    `default_availability: list[str]`
    :   Default availability status

    `default_country: list[str]`
    :   Default country

    `default_currency: list[str]`
    :   Default currency for pricing

    `default_locale: list[str]`
    :   Default locale

    `format: list[str]`
    :   Feed format

    `id: list[str]`
    :   Unique feed identifier

    `location: list[str]`
    :   URL where the feed is available

    `name: list[str]`
    :   Feed name

    `preferred_processing_schedule: list[dict[str, typing.Any]]`
    :   Preferred processing schedule

    `status: list[str]`
    :   Feed status

    `updated_at: list[str]`
    :   Timestamp when the feed was last updated

`CatalogsFeedsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsStringFilter`
    :   The type of the None singleton.

`CatalogsFeedsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsStringFilter`
    :   The type of the None singleton.

`CatalogsFeedsListParams(*args, **kwargs)`
:   Parameters for catalogs_feeds.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bookmark: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`CatalogsFeedsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsSearchFilter`
    :   The type of the None singleton.

`CatalogsFeedsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsSearchFilter`
    :   The type of the None singleton.

`CatalogsFeedsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsSearchFilter`
    :   The type of the None singleton.

`CatalogsFeedsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsAnyCondition`
    :   The type of the None singleton.

`CatalogsFeedsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsAnyCondition]`
    :   The type of the None singleton.

`CatalogsFeedsSearchFilter(*args, **kwargs)`
:   Available fields for filtering catalogs_feeds search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `catalog_type: str | None`
    :   Type of catalog

    `created_at: str | None`
    :   Timestamp when the feed was created

    `default_availability: str | None`
    :   Default availability status

    `default_country: str | None`
    :   Default country

    `default_currency: str | None`
    :   Default currency for pricing

    `default_locale: str | None`
    :   Default locale

    `format: str | None`
    :   Feed format

    `id: str | None`
    :   Unique feed identifier

    `location: str | None`
    :   URL where the feed is available

    `name: str | None`
    :   Feed name

    `preferred_processing_schedule: dict[str, typing.Any] | None`
    :   Preferred processing schedule

    `status: str | None`
    :   Feed status

    `updated_at: str | None`
    :   Timestamp when the feed was last updated

`CatalogsFeedsSearchQuery(*args, **kwargs)`
:   Search query for catalogs_feeds entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pinterest.types.CatalogsFeedsSortFilter]`
    :   The type of the None singleton.

`CatalogsFeedsSortFilter(*args, **kwargs)`
:   Available fields for sorting catalogs_feeds search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `catalog_type: Literal['asc', 'desc']`
    :   Type of catalog

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the feed was created

    `default_availability: Literal['asc', 'desc']`
    :   Default availability status

    `default_country: Literal['asc', 'desc']`
    :   Default country

    `default_currency: Literal['asc', 'desc']`
    :   Default currency for pricing

    `default_locale: Literal['asc', 'desc']`
    :   Default locale

    `format: Literal['asc', 'desc']`
    :   Feed format

    `id: Literal['asc', 'desc']`
    :   Unique feed identifier

    `location: Literal['asc', 'desc']`
    :   URL where the feed is available

    `name: Literal['asc', 'desc']`
    :   Feed name

    `preferred_processing_schedule: Literal['asc', 'desc']`
    :   Preferred processing schedule

    `status: Literal['asc', 'desc']`
    :   Feed status

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the feed was last updated

`CatalogsFeedsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `catalog_type: str`
    :   Type of catalog

    `created_at: str`
    :   Timestamp when the feed was created

    `default_availability: str`
    :   Default availability status

    `default_country: str`
    :   Default country

    `default_currency: str`
    :   Default currency for pricing

    `default_locale: str`
    :   Default locale

    `format: str`
    :   Feed format

    `id: str`
    :   Unique feed identifier

    `location: str`
    :   URL where the feed is available

    `name: str`
    :   Feed name

    `preferred_processing_schedule: str`
    :   Preferred processing schedule

    `status: str`
    :   Feed status

    `updated_at: str`
    :   Timestamp when the feed was last updated

`CatalogsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pinterest.types.CatalogsStringFilter`
    :   The type of the None singleton.

`CatalogsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pinterest.types.CatalogsSearchFilter`
    :   The type of the None singleton.

`CatalogsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pinterest.types.CatalogsSearchFilter`
    :   The type of the None singleton.

`CatalogsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.pinterest.types.CatalogsInFilter`
    :   The type of the None singleton.

`CatalogsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `catalog_type: list[str]`
    :   Type of catalog

    `created_at: list[str]`
    :   Timestamp when the catalog was created

    `id: list[str]`
    :   Unique catalog identifier

    `name: list[str]`
    :   Catalog name

    `updated_at: list[str]`
    :   Timestamp when the catalog was last updated

`CatalogsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pinterest.types.CatalogsStringFilter`
    :   The type of the None singleton.

`CatalogsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pinterest.types.CatalogsStringFilter`
    :   The type of the None singleton.

`CatalogsListParams(*args, **kwargs)`
:   Parameters for catalogs.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bookmark: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`CatalogsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pinterest.types.CatalogsSearchFilter`
    :   The type of the None singleton.

`CatalogsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pinterest.types.CatalogsSearchFilter`
    :   The type of the None singleton.

`CatalogsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pinterest.types.CatalogsSearchFilter`
    :   The type of the None singleton.

`CatalogsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.pinterest.types.CatalogsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsAnyCondition`
    :   The type of the None singleton.

`CatalogsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.pinterest.types.CatalogsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsAnyCondition]`
    :   The type of the None singleton.

`CatalogsProductGroupsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsAnyCondition]`
    :   The type of the None singleton.

`CatalogsProductGroupsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsAnyValueFilter`
    :   The type of the None singleton.

`CatalogsProductGroupsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Creation timestamp (Unix seconds)

    `description: Any`
    :   Product group description

    `feed_id: Any`
    :   Associated feed ID

    `id: Any`
    :   Unique product group identifier

    `is_featured: Any`
    :   Whether the product group is featured

    `name: Any`
    :   Product group name

    `status: Any`
    :   Product group status

    `type_: Any`
    :   Product group type

    `updated_at: Any`
    :   Last update timestamp (Unix seconds)

`CatalogsProductGroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsAnyValueFilter`
    :   The type of the None singleton.

`CatalogsProductGroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsSearchFilter`
    :   The type of the None singleton.

`CatalogsProductGroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsStringFilter`
    :   The type of the None singleton.

`CatalogsProductGroupsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsSearchFilter`
    :   The type of the None singleton.

`CatalogsProductGroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsSearchFilter`
    :   The type of the None singleton.

`CatalogsProductGroupsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsInFilter`
    :   The type of the None singleton.

`CatalogsProductGroupsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[int]`
    :   Creation timestamp (Unix seconds)

    `description: list[str]`
    :   Product group description

    `feed_id: list[str]`
    :   Associated feed ID

    `id: list[str]`
    :   Unique product group identifier

    `is_featured: list[bool]`
    :   Whether the product group is featured

    `name: list[str]`
    :   Product group name

    `status: list[str]`
    :   Product group status

    `type_: list[str]`
    :   Product group type

    `updated_at: list[int]`
    :   Last update timestamp (Unix seconds)

`CatalogsProductGroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsStringFilter`
    :   The type of the None singleton.

`CatalogsProductGroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsStringFilter`
    :   The type of the None singleton.

`CatalogsProductGroupsListParams(*args, **kwargs)`
:   Parameters for catalogs_product_groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bookmark: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`CatalogsProductGroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsSearchFilter`
    :   The type of the None singleton.

`CatalogsProductGroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsSearchFilter`
    :   The type of the None singleton.

`CatalogsProductGroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsSearchFilter`
    :   The type of the None singleton.

`CatalogsProductGroupsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsAnyCondition`
    :   The type of the None singleton.

`CatalogsProductGroupsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsAnyCondition]`
    :   The type of the None singleton.

`CatalogsProductGroupsSearchFilter(*args, **kwargs)`
:   Available fields for filtering catalogs_product_groups search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: int | None`
    :   Creation timestamp (Unix seconds)

    `description: str | None`
    :   Product group description

    `feed_id: str | None`
    :   Associated feed ID

    `id: str | None`
    :   Unique product group identifier

    `is_featured: bool | None`
    :   Whether the product group is featured

    `name: str | None`
    :   Product group name

    `status: str | None`
    :   Product group status

    `type_: str | None`
    :   Product group type

    `updated_at: int | None`
    :   Last update timestamp (Unix seconds)

`CatalogsProductGroupsSearchQuery(*args, **kwargs)`
:   Search query for catalogs_product_groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pinterest.types.CatalogsProductGroupsSortFilter]`
    :   The type of the None singleton.

`CatalogsProductGroupsSortFilter(*args, **kwargs)`
:   Available fields for sorting catalogs_product_groups search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Creation timestamp (Unix seconds)

    `description: Literal['asc', 'desc']`
    :   Product group description

    `feed_id: Literal['asc', 'desc']`
    :   Associated feed ID

    `id: Literal['asc', 'desc']`
    :   Unique product group identifier

    `is_featured: Literal['asc', 'desc']`
    :   Whether the product group is featured

    `name: Literal['asc', 'desc']`
    :   Product group name

    `status: Literal['asc', 'desc']`
    :   Product group status

    `type_: Literal['asc', 'desc']`
    :   Product group type

    `updated_at: Literal['asc', 'desc']`
    :   Last update timestamp (Unix seconds)

`CatalogsProductGroupsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Creation timestamp (Unix seconds)

    `description: str`
    :   Product group description

    `feed_id: str`
    :   Associated feed ID

    `id: str`
    :   Unique product group identifier

    `is_featured: str`
    :   Whether the product group is featured

    `name: str`
    :   Product group name

    `status: str`
    :   Product group status

    `type_: str`
    :   Product group type

    `updated_at: str`
    :   Last update timestamp (Unix seconds)

`CatalogsSearchFilter(*args, **kwargs)`
:   Available fields for filtering catalogs search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `catalog_type: str | None`
    :   Type of catalog

    `created_at: str | None`
    :   Timestamp when the catalog was created

    `id: str | None`
    :   Unique catalog identifier

    `name: str | None`
    :   Catalog name

    `updated_at: str | None`
    :   Timestamp when the catalog was last updated

`CatalogsSearchQuery(*args, **kwargs)`
:   Search query for catalogs entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pinterest.types.CatalogsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CatalogsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pinterest.types.CatalogsSortFilter]`
    :   The type of the None singleton.

`CatalogsSortFilter(*args, **kwargs)`
:   Available fields for sorting catalogs search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `catalog_type: Literal['asc', 'desc']`
    :   Type of catalog

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the catalog was created

    `id: Literal['asc', 'desc']`
    :   Unique catalog identifier

    `name: Literal['asc', 'desc']`
    :   Catalog name

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the catalog was last updated

`CatalogsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `catalog_type: str`
    :   Type of catalog

    `created_at: str`
    :   Timestamp when the catalog was created

    `id: str`
    :   Unique catalog identifier

    `name: str`
    :   Catalog name

    `updated_at: str`
    :   Timestamp when the catalog was last updated

`ConversionTagsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsInCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsAnyCondition]`
    :   The type of the None singleton.

`ConversionTagsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsAnyValueFilter`
    :   The type of the None singleton.

`ConversionTagsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Any`
    :   Ad account ID

    `code_snippet: Any`
    :   JavaScript code snippet for tracking

    `configs: Any`
    :   Tag configurations

    `enhanced_match_status: Any`
    :   Enhanced match status

    `id: Any`
    :   Unique conversion tag identifier

    `last_fired_time_ms: Any`
    :   Timestamp of last event fired (milliseconds)

    `name: Any`
    :   Conversion tag name

    `status: Any`
    :   Status

    `version: Any`
    :   Version number

`ConversionTagsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsAnyValueFilter`
    :   The type of the None singleton.

`ConversionTagsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsSearchFilter`
    :   The type of the None singleton.

`ConversionTagsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsStringFilter`
    :   The type of the None singleton.

`ConversionTagsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsSearchFilter`
    :   The type of the None singleton.

`ConversionTagsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsSearchFilter`
    :   The type of the None singleton.

`ConversionTagsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsInFilter`
    :   The type of the None singleton.

`ConversionTagsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: list[str]`
    :   Ad account ID

    `code_snippet: list[str]`
    :   JavaScript code snippet for tracking

    `configs: list[dict[str, typing.Any]]`
    :   Tag configurations

    `enhanced_match_status: list[str]`
    :   Enhanced match status

    `id: list[str]`
    :   Unique conversion tag identifier

    `last_fired_time_ms: list[int]`
    :   Timestamp of last event fired (milliseconds)

    `name: list[str]`
    :   Conversion tag name

    `status: list[str]`
    :   Status

    `version: list[str]`
    :   Version number

`ConversionTagsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsStringFilter`
    :   The type of the None singleton.

`ConversionTagsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsStringFilter`
    :   The type of the None singleton.

`ConversionTagsListParams(*args, **kwargs)`
:   Parameters for conversion_tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

    `bookmark: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`ConversionTagsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsSearchFilter`
    :   The type of the None singleton.

`ConversionTagsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsSearchFilter`
    :   The type of the None singleton.

`ConversionTagsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsSearchFilter`
    :   The type of the None singleton.

`ConversionTagsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsInCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsAnyCondition`
    :   The type of the None singleton.

`ConversionTagsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsInCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsAnyCondition]`
    :   The type of the None singleton.

`ConversionTagsSearchFilter(*args, **kwargs)`
:   Available fields for filtering conversion_tags search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str | None`
    :   Ad account ID

    `code_snippet: str | None`
    :   JavaScript code snippet for tracking

    `configs: dict[str, typing.Any] | None`
    :   Tag configurations

    `enhanced_match_status: str | None`
    :   Enhanced match status

    `id: str | None`
    :   Unique conversion tag identifier

    `last_fired_time_ms: int | None`
    :   Timestamp of last event fired (milliseconds)

    `name: str | None`
    :   Conversion tag name

    `status: str | None`
    :   Status

    `version: str | None`
    :   Version number

`ConversionTagsSearchQuery(*args, **kwargs)`
:   Search query for conversion_tags entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsInCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pinterest.types.ConversionTagsSortFilter]`
    :   The type of the None singleton.

`ConversionTagsSortFilter(*args, **kwargs)`
:   Available fields for sorting conversion_tags search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Literal['asc', 'desc']`
    :   Ad account ID

    `code_snippet: Literal['asc', 'desc']`
    :   JavaScript code snippet for tracking

    `configs: Literal['asc', 'desc']`
    :   Tag configurations

    `enhanced_match_status: Literal['asc', 'desc']`
    :   Enhanced match status

    `id: Literal['asc', 'desc']`
    :   Unique conversion tag identifier

    `last_fired_time_ms: Literal['asc', 'desc']`
    :   Timestamp of last event fired (milliseconds)

    `name: Literal['asc', 'desc']`
    :   Conversion tag name

    `status: Literal['asc', 'desc']`
    :   Status

    `version: Literal['asc', 'desc']`
    :   Version number

`ConversionTagsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   Ad account ID

    `code_snippet: str`
    :   JavaScript code snippet for tracking

    `configs: str`
    :   Tag configurations

    `enhanced_match_status: str`
    :   Enhanced match status

    `id: str`
    :   Unique conversion tag identifier

    `last_fired_time_ms: str`
    :   Timestamp of last event fired (milliseconds)

    `name: str`
    :   Conversion tag name

    `status: str`
    :   Status

    `version: str`
    :   Version number

`CustomerListsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.pinterest.types.CustomerListsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsAnyCondition]`
    :   The type of the None singleton.

`CustomerListsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.pinterest.types.CustomerListsAnyValueFilter`
    :   The type of the None singleton.

`CustomerListsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Any`
    :   Associated ad account ID

    `created_time: Any`
    :   Creation time (Unix seconds)

    `id: Any`
    :   Unique customer list identifier

    `name: Any`
    :   Customer list name

    `num_batches: Any`
    :   Total number of list updates

    `num_removed_user_records: Any`
    :   Count of removed user records

    `num_uploaded_user_records: Any`
    :   Count of uploaded user records

    `status: Any`
    :   Status

    `type_: Any`
    :   Always 'customerlist'

    `updated_time: Any`
    :   Last update time (Unix seconds)

`CustomerListsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pinterest.types.CustomerListsAnyValueFilter`
    :   The type of the None singleton.

`CustomerListsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pinterest.types.CustomerListsSearchFilter`
    :   The type of the None singleton.

`CustomerListsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pinterest.types.CustomerListsStringFilter`
    :   The type of the None singleton.

`CustomerListsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pinterest.types.CustomerListsSearchFilter`
    :   The type of the None singleton.

`CustomerListsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pinterest.types.CustomerListsSearchFilter`
    :   The type of the None singleton.

`CustomerListsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.pinterest.types.CustomerListsInFilter`
    :   The type of the None singleton.

`CustomerListsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: list[str]`
    :   Associated ad account ID

    `created_time: list[int]`
    :   Creation time (Unix seconds)

    `id: list[str]`
    :   Unique customer list identifier

    `name: list[str]`
    :   Customer list name

    `num_batches: list[int]`
    :   Total number of list updates

    `num_removed_user_records: list[int]`
    :   Count of removed user records

    `num_uploaded_user_records: list[int]`
    :   Count of uploaded user records

    `status: list[str]`
    :   Status

    `type_: list[str]`
    :   Always 'customerlist'

    `updated_time: list[int]`
    :   Last update time (Unix seconds)

`CustomerListsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pinterest.types.CustomerListsStringFilter`
    :   The type of the None singleton.

`CustomerListsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pinterest.types.CustomerListsStringFilter`
    :   The type of the None singleton.

`CustomerListsListParams(*args, **kwargs)`
:   Parameters for customer_lists.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

    `bookmark: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`CustomerListsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pinterest.types.CustomerListsSearchFilter`
    :   The type of the None singleton.

`CustomerListsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pinterest.types.CustomerListsSearchFilter`
    :   The type of the None singleton.

`CustomerListsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pinterest.types.CustomerListsSearchFilter`
    :   The type of the None singleton.

`CustomerListsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.pinterest.types.CustomerListsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsAnyCondition`
    :   The type of the None singleton.

`CustomerListsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.pinterest.types.CustomerListsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsAnyCondition]`
    :   The type of the None singleton.

`CustomerListsSearchFilter(*args, **kwargs)`
:   Available fields for filtering customer_lists search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str | None`
    :   Associated ad account ID

    `created_time: int | None`
    :   Creation time (Unix seconds)

    `id: str | None`
    :   Unique customer list identifier

    `name: str | None`
    :   Customer list name

    `num_batches: int | None`
    :   Total number of list updates

    `num_removed_user_records: int | None`
    :   Count of removed user records

    `num_uploaded_user_records: int | None`
    :   Count of uploaded user records

    `status: str | None`
    :   Status

    `type_: str | None`
    :   Always 'customerlist'

    `updated_time: int | None`
    :   Last update time (Unix seconds)

`CustomerListsSearchQuery(*args, **kwargs)`
:   Search query for customer_lists entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pinterest.types.CustomerListsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsInCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.CustomerListsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pinterest.types.CustomerListsSortFilter]`
    :   The type of the None singleton.

`CustomerListsSortFilter(*args, **kwargs)`
:   Available fields for sorting customer_lists search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Literal['asc', 'desc']`
    :   Associated ad account ID

    `created_time: Literal['asc', 'desc']`
    :   Creation time (Unix seconds)

    `id: Literal['asc', 'desc']`
    :   Unique customer list identifier

    `name: Literal['asc', 'desc']`
    :   Customer list name

    `num_batches: Literal['asc', 'desc']`
    :   Total number of list updates

    `num_removed_user_records: Literal['asc', 'desc']`
    :   Count of removed user records

    `num_uploaded_user_records: Literal['asc', 'desc']`
    :   Count of uploaded user records

    `status: Literal['asc', 'desc']`
    :   Status

    `type_: Literal['asc', 'desc']`
    :   Always 'customerlist'

    `updated_time: Literal['asc', 'desc']`
    :   Last update time (Unix seconds)

`CustomerListsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   Associated ad account ID

    `created_time: str`
    :   Creation time (Unix seconds)

    `id: str`
    :   Unique customer list identifier

    `name: str`
    :   Customer list name

    `num_batches: str`
    :   Total number of list updates

    `num_removed_user_records: str`
    :   Count of removed user records

    `num_uploaded_user_records: str`
    :   Count of uploaded user records

    `status: str`
    :   Status

    `type_: str`
    :   Always 'customerlist'

    `updated_time: str`
    :   Last update time (Unix seconds)

`KeywordsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.pinterest.types.KeywordsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsInCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsAnyCondition]`
    :   The type of the None singleton.

`KeywordsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.pinterest.types.KeywordsAnyValueFilter`
    :   The type of the None singleton.

`KeywordsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Whether the keyword is archived

    `bid: Any`
    :   Bid value in microcurrency

    `id: Any`
    :   Unique keyword identifier

    `match_type: Any`
    :   Match type

    `parent_id: Any`
    :   Parent entity ID

    `parent_type: Any`
    :   Parent entity type

    `type_: Any`
    :   Always 'keyword'

    `value: Any`
    :   Keyword text value

`KeywordsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pinterest.types.KeywordsAnyValueFilter`
    :   The type of the None singleton.

`KeywordsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pinterest.types.KeywordsSearchFilter`
    :   The type of the None singleton.

`KeywordsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pinterest.types.KeywordsStringFilter`
    :   The type of the None singleton.

`KeywordsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pinterest.types.KeywordsSearchFilter`
    :   The type of the None singleton.

`KeywordsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pinterest.types.KeywordsSearchFilter`
    :   The type of the None singleton.

`KeywordsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.pinterest.types.KeywordsInFilter`
    :   The type of the None singleton.

`KeywordsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Whether the keyword is archived

    `bid: list[int]`
    :   Bid value in microcurrency

    `id: list[str]`
    :   Unique keyword identifier

    `match_type: list[str]`
    :   Match type

    `parent_id: list[str]`
    :   Parent entity ID

    `parent_type: list[str]`
    :   Parent entity type

    `type_: list[str]`
    :   Always 'keyword'

    `value: list[str]`
    :   Keyword text value

`KeywordsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pinterest.types.KeywordsStringFilter`
    :   The type of the None singleton.

`KeywordsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pinterest.types.KeywordsStringFilter`
    :   The type of the None singleton.

`KeywordsListParams(*args, **kwargs)`
:   Parameters for keywords.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

    `ad_group_id: str`
    :   The type of the None singleton.

    `bookmark: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`KeywordsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pinterest.types.KeywordsSearchFilter`
    :   The type of the None singleton.

`KeywordsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pinterest.types.KeywordsSearchFilter`
    :   The type of the None singleton.

`KeywordsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pinterest.types.KeywordsSearchFilter`
    :   The type of the None singleton.

`KeywordsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.pinterest.types.KeywordsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsInCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsAnyCondition`
    :   The type of the None singleton.

`KeywordsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.pinterest.types.KeywordsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsInCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsAnyCondition]`
    :   The type of the None singleton.

`KeywordsSearchFilter(*args, **kwargs)`
:   Available fields for filtering keywords search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool | None`
    :   Whether the keyword is archived

    `bid: int | None`
    :   Bid value in microcurrency

    `id: str | None`
    :   Unique keyword identifier

    `match_type: str | None`
    :   Match type

    `parent_id: str | None`
    :   Parent entity ID

    `parent_type: str | None`
    :   Parent entity type

    `type_: str | None`
    :   Always 'keyword'

    `value: str | None`
    :   Keyword text value

`KeywordsSearchQuery(*args, **kwargs)`
:   Search query for keywords entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pinterest.types.KeywordsEqCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsNeqCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsGtCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsGteCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsLtCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsLteCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsInCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsLikeCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsFuzzyCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsKeywordCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsContainsCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsNotCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsAndCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsOrCondition | airbyte_agent_sdk.connectors.pinterest.types.KeywordsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pinterest.types.KeywordsSortFilter]`
    :   The type of the None singleton.

`KeywordsSortFilter(*args, **kwargs)`
:   Available fields for sorting keywords search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Whether the keyword is archived

    `bid: Literal['asc', 'desc']`
    :   Bid value in microcurrency

    `id: Literal['asc', 'desc']`
    :   Unique keyword identifier

    `match_type: Literal['asc', 'desc']`
    :   Match type

    `parent_id: Literal['asc', 'desc']`
    :   Parent entity ID

    `parent_type: Literal['asc', 'desc']`
    :   Parent entity type

    `type_: Literal['asc', 'desc']`
    :   Always 'keyword'

    `value: Literal['asc', 'desc']`
    :   Keyword text value

`KeywordsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Whether the keyword is archived

    `bid: str`
    :   Bid value in microcurrency

    `id: str`
    :   Unique keyword identifier

    `match_type: str`
    :   Match type

    `parent_id: str`
    :   Parent entity ID

    `parent_type: str`
    :   Parent entity type

    `type_: str`
    :   Always 'keyword'

    `value: str`
    :   Keyword text value