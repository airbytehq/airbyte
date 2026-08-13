---
id: airbyte_agent_sdk-connectors-amazon_ads-types
title: airbyte_agent_sdk.connectors.amazon_ads.types
---

Module airbyte_agent_sdk.connectors.amazon_ads.types
====================================================
Type definitions for amazon-ads connector.

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

<a id="PortfoliosGetParams"></a>

`PortfoliosGetParams(*args, **kwargs)`
:   Parameters for portfolios.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `portfolio_id: str`
    :   The type of the None singleton.

<a id="PortfoliosListParams"></a>

`PortfoliosListParams(*args, **kwargs)`
:   Parameters for portfolios.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include_extended_data_fields: str`
    :   The type of the None singleton.

<a id="ProfilesAndCondition"></a>

`ProfilesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesEqCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesNeqCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesGtCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesGteCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesLtCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesLteCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesInCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesLikeCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesFuzzyCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesKeywordCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesContainsCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesNotCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesAndCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesOrCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesAnyCondition]`
    :   The type of the None singleton.

<a id="ProfilesAnyCondition"></a>

`ProfilesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesAnyValueFilter`
    :   The type of the None singleton.

<a id="ProfilesAnyValueFilter"></a>

`ProfilesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_info: Any`
    :   The type of the None singleton.

    `country_code: Any`
    :   The type of the None singleton.

    `currency_code: Any`
    :   The type of the None singleton.

    `daily_budget: Any`
    :   The type of the None singleton.

    `profile_id: Any`
    :   The type of the None singleton.

    `timezone: Any`
    :   The type of the None singleton.

<a id="ProfilesContainsCondition"></a>

`ProfilesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesAnyValueFilter`
    :   The type of the None singleton.

<a id="ProfilesEqCondition"></a>

`ProfilesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesSearchFilter`
    :   The type of the None singleton.

<a id="ProfilesFuzzyCondition"></a>

`ProfilesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesStringFilter`
    :   The type of the None singleton.

<a id="ProfilesGetParams"></a>

`ProfilesGetParams(*args, **kwargs)`
:   Parameters for profiles.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `profile_id: str`
    :   The type of the None singleton.

<a id="ProfilesGtCondition"></a>

`ProfilesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesSearchFilter`
    :   The type of the None singleton.

<a id="ProfilesGteCondition"></a>

`ProfilesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesSearchFilter`
    :   The type of the None singleton.

<a id="ProfilesInCondition"></a>

`ProfilesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesInFilter`
    :   The type of the None singleton.

<a id="ProfilesInFilter"></a>

`ProfilesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_info: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `country_code: list[str]`
    :   The type of the None singleton.

    `currency_code: list[str]`
    :   The type of the None singleton.

    `daily_budget: list[float]`
    :   The type of the None singleton.

    `profile_id: list[int]`
    :   The type of the None singleton.

    `timezone: list[str]`
    :   The type of the None singleton.

<a id="ProfilesKeywordCondition"></a>

`ProfilesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesStringFilter`
    :   The type of the None singleton.

<a id="ProfilesLikeCondition"></a>

`ProfilesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesStringFilter`
    :   The type of the None singleton.

<a id="ProfilesListParams"></a>

`ProfilesListParams(*args, **kwargs)`
:   Parameters for profiles.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `profile_type_filter: str`
    :   The type of the None singleton.

<a id="ProfilesLtCondition"></a>

`ProfilesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesSearchFilter`
    :   The type of the None singleton.

<a id="ProfilesLteCondition"></a>

`ProfilesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesSearchFilter`
    :   The type of the None singleton.

<a id="ProfilesNeqCondition"></a>

`ProfilesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesSearchFilter`
    :   The type of the None singleton.

<a id="ProfilesNotCondition"></a>

`ProfilesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesEqCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesNeqCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesGtCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesGteCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesLtCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesLteCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesInCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesLikeCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesFuzzyCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesKeywordCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesContainsCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesNotCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesAndCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesOrCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesAnyCondition`
    :   The type of the None singleton.

<a id="ProfilesOrCondition"></a>

`ProfilesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesEqCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesNeqCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesGtCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesGteCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesLtCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesLteCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesInCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesLikeCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesFuzzyCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesKeywordCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesContainsCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesNotCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesAndCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesOrCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesAnyCondition]`
    :   The type of the None singleton.

<a id="ProfilesSearchFilter"></a>

`ProfilesSearchFilter(*args, **kwargs)`
:   Available fields for filtering profiles search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_info: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `country_code: str | None`
    :   The type of the None singleton.

    `currency_code: str | None`
    :   The type of the None singleton.

    `daily_budget: float | None`
    :   The type of the None singleton.

    `profile_id: int | None`
    :   The type of the None singleton.

    `timezone: str | None`
    :   The type of the None singleton.

<a id="ProfilesSearchQuery"></a>

`ProfilesSearchQuery(*args, **kwargs)`
:   Search query for profiles entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesEqCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesNeqCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesGtCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesGteCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesLtCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesLteCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesInCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesLikeCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesFuzzyCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesKeywordCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesContainsCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesNotCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesAndCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesOrCondition | airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.amazon_ads.types.ProfilesSortFilter]`
    :   The type of the None singleton.

<a id="ProfilesSortFilter"></a>

`ProfilesSortFilter(*args, **kwargs)`
:   Available fields for sorting profiles search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_info: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `country_code: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `currency_code: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `daily_budget: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `profile_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `timezone: Literal['asc', 'desc']`
    :   The type of the None singleton.

<a id="ProfilesStringFilter"></a>

`ProfilesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_info: str`
    :   The type of the None singleton.

    `country_code: str`
    :   The type of the None singleton.

    `currency_code: str`
    :   The type of the None singleton.

    `daily_budget: str`
    :   The type of the None singleton.

    `profile_id: str`
    :   The type of the None singleton.

    `timezone: str`
    :   The type of the None singleton.

<a id="SponsoredBrandsAdGroupsListParams"></a>

`SponsoredBrandsAdGroupsListParams(*args, **kwargs)`
:   Parameters for sponsored_brands_ad_groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `max_results: int`
    :   The type of the None singleton.

    `next_token: str`
    :   The type of the None singleton.

    `state_filter: airbyte_agent_sdk.connectors.amazon_ads.types.SponsoredBrandsAdGroupsListParamsStatefilter`
    :   The type of the None singleton.

<a id="SponsoredBrandsAdGroupsListParamsStatefilter"></a>

`SponsoredBrandsAdGroupsListParamsStatefilter(*args, **kwargs)`
:   Nested schema for SponsoredBrandsAdGroupsListParams.stateFilter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include: str`
    :   The type of the None singleton.

<a id="SponsoredBrandsCampaignsListParams"></a>

`SponsoredBrandsCampaignsListParams(*args, **kwargs)`
:   Parameters for sponsored_brands_campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `max_results: int`
    :   The type of the None singleton.

    `next_token: str`
    :   The type of the None singleton.

    `state_filter: airbyte_agent_sdk.connectors.amazon_ads.types.SponsoredBrandsCampaignsListParamsStatefilter`
    :   The type of the None singleton.

<a id="SponsoredBrandsCampaignsListParamsStatefilter"></a>

`SponsoredBrandsCampaignsListParamsStatefilter(*args, **kwargs)`
:   Nested schema for SponsoredBrandsCampaignsListParams.stateFilter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include: str`
    :   The type of the None singleton.

<a id="SponsoredProductAdGroupsListParams"></a>

`SponsoredProductAdGroupsListParams(*args, **kwargs)`
:   Parameters for sponsored_product_ad_groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `max_results: int`
    :   The type of the None singleton.

    `next_token: str`
    :   The type of the None singleton.

    `state_filter: airbyte_agent_sdk.connectors.amazon_ads.types.SponsoredProductAdGroupsListParamsStatefilter`
    :   The type of the None singleton.

<a id="SponsoredProductAdGroupsListParamsStatefilter"></a>

`SponsoredProductAdGroupsListParamsStatefilter(*args, **kwargs)`
:   Nested schema for SponsoredProductAdGroupsListParams.stateFilter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include: str`
    :   The type of the None singleton.

<a id="SponsoredProductCampaignsGetParams"></a>

`SponsoredProductCampaignsGetParams(*args, **kwargs)`
:   Parameters for sponsored_product_campaigns.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: str`
    :   The type of the None singleton.

<a id="SponsoredProductCampaignsListParams"></a>

`SponsoredProductCampaignsListParams(*args, **kwargs)`
:   Parameters for sponsored_product_campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `max_results: int`
    :   The type of the None singleton.

    `next_token: str`
    :   The type of the None singleton.

    `state_filter: airbyte_agent_sdk.connectors.amazon_ads.types.SponsoredProductCampaignsListParamsStatefilter`
    :   The type of the None singleton.

<a id="SponsoredProductCampaignsListParamsStatefilter"></a>

`SponsoredProductCampaignsListParamsStatefilter(*args, **kwargs)`
:   Nested schema for SponsoredProductCampaignsListParams.stateFilter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include: str`
    :   The type of the None singleton.

<a id="SponsoredProductKeywordsListParams"></a>

`SponsoredProductKeywordsListParams(*args, **kwargs)`
:   Parameters for sponsored_product_keywords.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `max_results: int`
    :   The type of the None singleton.

    `next_token: str`
    :   The type of the None singleton.

    `state_filter: airbyte_agent_sdk.connectors.amazon_ads.types.SponsoredProductKeywordsListParamsStatefilter`
    :   The type of the None singleton.

<a id="SponsoredProductKeywordsListParamsStatefilter"></a>

`SponsoredProductKeywordsListParamsStatefilter(*args, **kwargs)`
:   Nested schema for SponsoredProductKeywordsListParams.stateFilter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include: str`
    :   The type of the None singleton.

<a id="SponsoredProductNegativeKeywordsListParams"></a>

`SponsoredProductNegativeKeywordsListParams(*args, **kwargs)`
:   Parameters for sponsored_product_negative_keywords.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `max_results: int`
    :   The type of the None singleton.

    `next_token: str`
    :   The type of the None singleton.

    `state_filter: airbyte_agent_sdk.connectors.amazon_ads.types.SponsoredProductNegativeKeywordsListParamsStatefilter`
    :   The type of the None singleton.

<a id="SponsoredProductNegativeKeywordsListParamsStatefilter"></a>

`SponsoredProductNegativeKeywordsListParamsStatefilter(*args, **kwargs)`
:   Nested schema for SponsoredProductNegativeKeywordsListParams.stateFilter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include: str`
    :   The type of the None singleton.

<a id="SponsoredProductNegativeTargetsListParams"></a>

`SponsoredProductNegativeTargetsListParams(*args, **kwargs)`
:   Parameters for sponsored_product_negative_targets.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `max_results: int`
    :   The type of the None singleton.

    `next_token: str`
    :   The type of the None singleton.

    `state_filter: airbyte_agent_sdk.connectors.amazon_ads.types.SponsoredProductNegativeTargetsListParamsStatefilter`
    :   The type of the None singleton.

<a id="SponsoredProductNegativeTargetsListParamsStatefilter"></a>

`SponsoredProductNegativeTargetsListParamsStatefilter(*args, **kwargs)`
:   Nested schema for SponsoredProductNegativeTargetsListParams.stateFilter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include: str`
    :   The type of the None singleton.

<a id="SponsoredProductProductAdsListParams"></a>

`SponsoredProductProductAdsListParams(*args, **kwargs)`
:   Parameters for sponsored_product_product_ads.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `max_results: int`
    :   The type of the None singleton.

    `next_token: str`
    :   The type of the None singleton.

    `state_filter: airbyte_agent_sdk.connectors.amazon_ads.types.SponsoredProductProductAdsListParamsStatefilter`
    :   The type of the None singleton.

<a id="SponsoredProductProductAdsListParamsStatefilter"></a>

`SponsoredProductProductAdsListParamsStatefilter(*args, **kwargs)`
:   Nested schema for SponsoredProductProductAdsListParams.stateFilter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include: str`
    :   The type of the None singleton.

<a id="SponsoredProductTargetsListParams"></a>

`SponsoredProductTargetsListParams(*args, **kwargs)`
:   Parameters for sponsored_product_targets.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `max_results: int`
    :   The type of the None singleton.

    `next_token: str`
    :   The type of the None singleton.

    `state_filter: airbyte_agent_sdk.connectors.amazon_ads.types.SponsoredProductTargetsListParamsStatefilter`
    :   The type of the None singleton.

<a id="SponsoredProductTargetsListParamsStatefilter"></a>

`SponsoredProductTargetsListParamsStatefilter(*args, **kwargs)`
:   Nested schema for SponsoredProductTargetsListParams.stateFilter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include: str`
    :   The type of the None singleton.