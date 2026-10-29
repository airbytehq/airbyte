---
id: airbyte_agent_sdk-connectors-reddit_ads-types
title: airbyte_agent_sdk.connectors.reddit_ads.types
---

Module airbyte_agent_sdk.connectors.reddit_ads.types
====================================================
Type definitions for reddit-ads connector.

Classes
-------

<a id="AdAccountsGetParams"></a>

`AdAccountsGetParams(*args, **kwargs)`
:   Parameters for ad_accounts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

<a id="AdAccountsListParams"></a>

`AdAccountsListParams(*args, **kwargs)`
:   Parameters for ad_accounts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `business_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

<a id="AdGroupsGetParams"></a>

`AdGroupsGetParams(*args, **kwargs)`
:   Parameters for ad_groups.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_id: str`
    :   The type of the None singleton.

<a id="AdGroupsListParams"></a>

`AdGroupsListParams(*args, **kwargs)`
:   Parameters for ad_groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

    `campaign_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
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

    `and: list[airbyte_agent_sdk.connectors.reddit_ads.types.AdsEqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsNeqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsGtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsGteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsLtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsLteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsInCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsStartswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsEndswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsArrayContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsNotCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsAndCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsOrCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.reddit_ads.types.AdsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdsAnyValueFilter"></a>

`AdsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Any`
    :   The ad account this ad belongs to

    `ad_group_id: Any`
    :   The ad group this ad belongs to

    `campaign_id: Any`
    :   The campaign this ad belongs to

    `click_url: Any`
    :   Click destination URL

    `configured_status: Any`
    :   User-configured status

    `created_at: Any`
    :   Creation timestamp

    `effective_status: Any`
    :   Effective delivery status

    `id: Any`
    :   Unique ad identifier

    `modified_at: Any`
    :   Last modification timestamp

    `name: Any`
    :   Ad name

    `post_id: Any`
    :   Reddit post ID (t3_ prefix)

    `post_url: Any`
    :   Reddit post URL

    `preview_url: Any`
    :   Ad preview URL

    `rejection_reason: Any`
    :   Reason the ad was rejected

<a id="AdsArrayContainsCondition"></a>

`AdsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.reddit_ads.types.AdsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdsContainsCondition"></a>

`AdsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.reddit_ads.types.AdsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdsEndswithCondition"></a>

`AdsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.reddit_ads.types.AdsStringFilter`
    :   The type of the None singleton.

<a id="AdsEqCondition"></a>

`AdsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.reddit_ads.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsFuzzyCondition"></a>

`AdsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.reddit_ads.types.AdsStringFilter`
    :   The type of the None singleton.

<a id="AdsGetParams"></a>

`AdsGetParams(*args, **kwargs)`
:   Parameters for ads.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_id: str`
    :   The type of the None singleton.

<a id="AdsGtCondition"></a>

`AdsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.reddit_ads.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsGteCondition"></a>

`AdsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.reddit_ads.types.AdsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.reddit_ads.types.AdsInFilter`
    :   The type of the None singleton.

<a id="AdsInFilter"></a>

`AdsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: list[str]`
    :   The ad account this ad belongs to

    `ad_group_id: list[str]`
    :   The ad group this ad belongs to

    `campaign_id: list[str]`
    :   The campaign this ad belongs to

    `click_url: list[str]`
    :   Click destination URL

    `configured_status: list[str]`
    :   User-configured status

    `created_at: list[str]`
    :   Creation timestamp

    `effective_status: list[str]`
    :   Effective delivery status

    `id: list[str]`
    :   Unique ad identifier

    `modified_at: list[str]`
    :   Last modification timestamp

    `name: list[str]`
    :   Ad name

    `post_id: list[str]`
    :   Reddit post ID (t3_ prefix)

    `post_url: list[str]`
    :   Reddit post URL

    `preview_url: list[str]`
    :   Ad preview URL

    `rejection_reason: list[str]`
    :   Reason the ad was rejected

<a id="AdsKeywordCondition"></a>

`AdsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.reddit_ads.types.AdsStringFilter`
    :   The type of the None singleton.

<a id="AdsListParams"></a>

`AdsListParams(*args, **kwargs)`
:   Parameters for ads.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

    `ad_group_id: list[str]`
    :   The type of the None singleton.

    `campaign_id: list[str]`
    :   The type of the None singleton.

    `configured_status: list[str]`
    :   The type of the None singleton.

    `effective_status: list[str]`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

<a id="AdsLtCondition"></a>

`AdsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.reddit_ads.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsLteCondition"></a>

`AdsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.reddit_ads.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsNeqCondition"></a>

`AdsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.reddit_ads.types.AdsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.reddit_ads.types.AdsEqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsNeqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsGtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsGteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsLtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsLteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsInCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsStartswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsEndswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsArrayContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsNotCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsAndCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsOrCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.reddit_ads.types.AdsEqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsNeqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsGtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsGteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsLtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsLteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsInCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsStartswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsEndswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsArrayContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsNotCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsAndCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsOrCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsAnyCondition]`
    :   The type of the None singleton.

<a id="AdsSearchFilter"></a>

`AdsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ads search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str | None`
    :   The ad account this ad belongs to

    `ad_group_id: str | None`
    :   The ad group this ad belongs to

    `campaign_id: str | None`
    :   The campaign this ad belongs to

    `click_url: str | None`
    :   Click destination URL

    `configured_status: str | None`
    :   User-configured status

    `created_at: str | None`
    :   Creation timestamp

    `effective_status: str | None`
    :   Effective delivery status

    `id: str | None`
    :   Unique ad identifier

    `modified_at: str | None`
    :   Last modification timestamp

    `name: str | None`
    :   Ad name

    `post_id: str | None`
    :   Reddit post ID (t3_ prefix)

    `post_url: str | None`
    :   Reddit post URL

    `preview_url: str | None`
    :   Ad preview URL

    `rejection_reason: str | None`
    :   Reason the ad was rejected

<a id="AdsSearchQuery"></a>

`AdsSearchQuery(*args, **kwargs)`
:   Search query for ads entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.reddit_ads.types.AdsEqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsNeqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsGtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsGteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsLtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsLteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsInCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsStartswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsEndswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsArrayContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsNotCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsAndCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsOrCondition | airbyte_agent_sdk.connectors.reddit_ads.types.AdsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.reddit_ads.types.AdsSortFilter]`
    :   The type of the None singleton.

<a id="AdsSortFilter"></a>

`AdsSortFilter(*args, **kwargs)`
:   Available fields for sorting ads search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Literal['asc', 'desc']`
    :   The ad account this ad belongs to

    `ad_group_id: Literal['asc', 'desc']`
    :   The ad group this ad belongs to

    `campaign_id: Literal['asc', 'desc']`
    :   The campaign this ad belongs to

    `click_url: Literal['asc', 'desc']`
    :   Click destination URL

    `configured_status: Literal['asc', 'desc']`
    :   User-configured status

    `created_at: Literal['asc', 'desc']`
    :   Creation timestamp

    `effective_status: Literal['asc', 'desc']`
    :   Effective delivery status

    `id: Literal['asc', 'desc']`
    :   Unique ad identifier

    `modified_at: Literal['asc', 'desc']`
    :   Last modification timestamp

    `name: Literal['asc', 'desc']`
    :   Ad name

    `post_id: Literal['asc', 'desc']`
    :   Reddit post ID (t3_ prefix)

    `post_url: Literal['asc', 'desc']`
    :   Reddit post URL

    `preview_url: Literal['asc', 'desc']`
    :   Ad preview URL

    `rejection_reason: Literal['asc', 'desc']`
    :   Reason the ad was rejected

<a id="AdsStartswithCondition"></a>

`AdsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.reddit_ads.types.AdsStringFilter`
    :   The type of the None singleton.

<a id="AdsStringFilter"></a>

`AdsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The ad account this ad belongs to

    `ad_group_id: str`
    :   The ad group this ad belongs to

    `campaign_id: str`
    :   The campaign this ad belongs to

    `click_url: str`
    :   Click destination URL

    `configured_status: str`
    :   User-configured status

    `created_at: str`
    :   Creation timestamp

    `effective_status: str`
    :   Effective delivery status

    `id: str`
    :   Unique ad identifier

    `modified_at: str`
    :   Last modification timestamp

    `name: str`
    :   Ad name

    `post_id: str`
    :   Reddit post ID (t3_ prefix)

    `post_url: str`
    :   Reddit post URL

    `preview_url: str`
    :   Ad preview URL

    `rejection_reason: str`
    :   Reason the ad was rejected

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

<a id="BusinessesListParams"></a>

`BusinessesListParams(*args, **kwargs)`
:   Parameters for businesses.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
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

    `and: list[airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsStartswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsEndswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsArrayContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsAnyValueFilter"></a>

`CampaignsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Any`
    :   The ad account this campaign belongs to

    `app_id: Any`
    :   App Store or Play Store ID

    `configured_status: Any`
    :   User-configured status (ACTIVE, ARCHIVED, DELETED, PAUSED)

    `created_at: Any`
    :   Creation timestamp in ISO 8601 format

    `effective_status: Any`
    :   Effective delivery status

    `funding_instrument_id: Any`
    :   Funding instrument ID

    `goal_type: Any`
    :   Goal type (LIFETIME_SPEND, DAILY_SPEND)

    `goal_value: Any`
    :   Goal value in microcurrency

    `id: Any`
    :   Unique campaign identifier

    `is_campaign_budget_optimization: Any`
    :   Whether campaign budget optimization is enabled

    `modified_at: Any`
    :   Last modification timestamp

    `name: Any`
    :   Campaign name

    `objective: Any`
    :   Campaign objective

    `spend_cap: Any`
    :   Spend cap in microcurrency

<a id="CampaignsArrayContainsCondition"></a>

`CampaignsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsContainsCondition"></a>

`CampaignsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsEndswithCondition"></a>

`CampaignsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsEqCondition"></a>

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsFuzzyCondition"></a>

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsGetParams"></a>

`CampaignsGetParams(*args, **kwargs)`
:   Parameters for campaigns.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: str`
    :   The type of the None singleton.

<a id="CampaignsGtCondition"></a>

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsGteCondition"></a>

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsInFilter`
    :   The type of the None singleton.

<a id="CampaignsInFilter"></a>

`CampaignsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: list[str]`
    :   The ad account this campaign belongs to

    `app_id: list[str]`
    :   App Store or Play Store ID

    `configured_status: list[str]`
    :   User-configured status (ACTIVE, ARCHIVED, DELETED, PAUSED)

    `created_at: list[str]`
    :   Creation timestamp in ISO 8601 format

    `effective_status: list[str]`
    :   Effective delivery status

    `funding_instrument_id: list[str]`
    :   Funding instrument ID

    `goal_type: list[str]`
    :   Goal type (LIFETIME_SPEND, DAILY_SPEND)

    `goal_value: list[int]`
    :   Goal value in microcurrency

    `id: list[str]`
    :   Unique campaign identifier

    `is_campaign_budget_optimization: list[bool]`
    :   Whether campaign budget optimization is enabled

    `modified_at: list[str]`
    :   Last modification timestamp

    `name: list[str]`
    :   Campaign name

    `objective: list[str]`
    :   Campaign objective

    `spend_cap: list[int]`
    :   Spend cap in microcurrency

<a id="CampaignsKeywordCondition"></a>

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsListParams"></a>

`CampaignsListParams(*args, **kwargs)`
:   Parameters for campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

<a id="CampaignsLtCondition"></a>

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsLteCondition"></a>

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsNeqCondition"></a>

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsStartswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsEndswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsArrayContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsStartswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsEndswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsArrayContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignsSearchFilter"></a>

`CampaignsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaigns search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str | None`
    :   The ad account this campaign belongs to

    `app_id: str | None`
    :   App Store or Play Store ID

    `configured_status: str | None`
    :   User-configured status (ACTIVE, ARCHIVED, DELETED, PAUSED)

    `created_at: str | None`
    :   Creation timestamp in ISO 8601 format

    `effective_status: str | None`
    :   Effective delivery status

    `funding_instrument_id: str | None`
    :   Funding instrument ID

    `goal_type: str | None`
    :   Goal type (LIFETIME_SPEND, DAILY_SPEND)

    `goal_value: int | None`
    :   Goal value in microcurrency

    `id: str | None`
    :   Unique campaign identifier

    `is_campaign_budget_optimization: bool | None`
    :   Whether campaign budget optimization is enabled

    `modified_at: str | None`
    :   Last modification timestamp

    `name: str | None`
    :   Campaign name

    `objective: str | None`
    :   Campaign objective

    `spend_cap: int | None`
    :   Spend cap in microcurrency

<a id="CampaignsSearchQuery"></a>

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsStartswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsEndswithCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsArrayContainsCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsSortFilter]`
    :   The type of the None singleton.

<a id="CampaignsSortFilter"></a>

`CampaignsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaigns search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Literal['asc', 'desc']`
    :   The ad account this campaign belongs to

    `app_id: Literal['asc', 'desc']`
    :   App Store or Play Store ID

    `configured_status: Literal['asc', 'desc']`
    :   User-configured status (ACTIVE, ARCHIVED, DELETED, PAUSED)

    `created_at: Literal['asc', 'desc']`
    :   Creation timestamp in ISO 8601 format

    `effective_status: Literal['asc', 'desc']`
    :   Effective delivery status

    `funding_instrument_id: Literal['asc', 'desc']`
    :   Funding instrument ID

    `goal_type: Literal['asc', 'desc']`
    :   Goal type (LIFETIME_SPEND, DAILY_SPEND)

    `goal_value: Literal['asc', 'desc']`
    :   Goal value in microcurrency

    `id: Literal['asc', 'desc']`
    :   Unique campaign identifier

    `is_campaign_budget_optimization: Literal['asc', 'desc']`
    :   Whether campaign budget optimization is enabled

    `modified_at: Literal['asc', 'desc']`
    :   Last modification timestamp

    `name: Literal['asc', 'desc']`
    :   Campaign name

    `objective: Literal['asc', 'desc']`
    :   Campaign objective

    `spend_cap: Literal['asc', 'desc']`
    :   Spend cap in microcurrency

<a id="CampaignsStartswithCondition"></a>

`CampaignsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.reddit_ads.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsStringFilter"></a>

`CampaignsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The ad account this campaign belongs to

    `app_id: str`
    :   App Store or Play Store ID

    `configured_status: str`
    :   User-configured status (ACTIVE, ARCHIVED, DELETED, PAUSED)

    `created_at: str`
    :   Creation timestamp in ISO 8601 format

    `effective_status: str`
    :   Effective delivery status

    `funding_instrument_id: str`
    :   Funding instrument ID

    `goal_type: str`
    :   Goal type (LIFETIME_SPEND, DAILY_SPEND)

    `goal_value: str`
    :   Goal value in microcurrency

    `id: str`
    :   Unique campaign identifier

    `is_campaign_budget_optimization: str`
    :   Whether campaign budget optimization is enabled

    `modified_at: str`
    :   Last modification timestamp

    `name: str`
    :   Campaign name

    `objective: str`
    :   Campaign objective

    `spend_cap: str`
    :   Spend cap in microcurrency