---
id: airbyte_agent_sdk-connectors-google_ads-types
title: airbyte_agent_sdk.connectors.google_ads.types
---

Module airbyte_agent_sdk.connectors.google_ads.types
====================================================
Type definitions for google-ads connector.

Classes
-------

<a id="AccessibleCustomersListParams"></a>

`AccessibleCustomersListParams(*args, **kwargs)`
:   Parameters for accessible_customers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

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

    `and: list[airbyte_agent_sdk.connectors.google_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.google_ads.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountsAnyValueFilter"></a>

`AccountsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_auto_tagging_enabled: Any`
    :   Whether auto-tagging is enabled for the account

    `customer_call_reporting_setting_call_conversion_action: Any`
    :   Call conversion action resource name

    `customer_call_reporting_setting_call_conversion_reporting_enabled: Any`
    :   Whether call conversion reporting is enabled

    `customer_call_reporting_setting_call_reporting_enabled: Any`
    :   Whether call reporting is enabled

    `customer_conversion_tracking_setting_conversion_tracking_id: Any`
    :   Conversion tracking ID

    `customer_conversion_tracking_setting_cross_account_conversion_tracking_id: Any`
    :   Cross-account conversion tracking ID

    `customer_currency_code: Any`
    :   Currency code for the account (e.g., USD)

    `customer_descriptive_name: Any`
    :   Descriptive name of the customer account

    `customer_final_url_suffix: Any`
    :   URL suffix appended to final URLs

    `customer_has_partners_badge: Any`
    :   Whether the account has a Google Partners badge

    `customer_id: Any`
    :   Unique customer account ID

    `customer_manager: Any`
    :   Whether this is a manager (MCC) account

    `customer_optimization_score: Any`
    :   Optimization score for the account (0.0 to 1.0)

    `customer_optimization_score_weight: Any`
    :   Weight of the optimization score

    `customer_pay_per_conversion_eligibility_failure_reasons: Any`
    :   Reasons why pay-per-conversion is not eligible

    `customer_remarketing_setting_google_global_site_tag: Any`
    :   Google global site tag snippet

    `customer_resource_name: Any`
    :   Resource name of the customer

    `customer_test_account: Any`
    :   Whether this is a test account

    `customer_time_zone: Any`
    :   Time zone of the account

    `customer_tracking_url_template: Any`
    :   Tracking URL template for the account

    `segments_date: Any`
    :   Date segment for the report row

<a id="AccountsContainsCondition"></a>

`AccountsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_ads.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountsEqCondition"></a>

`AccountsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_ads.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsFuzzyCondition"></a>

`AccountsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_ads.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsGtCondition"></a>

`AccountsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_ads.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsGteCondition"></a>

`AccountsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_ads.types.AccountsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.google_ads.types.AccountsInFilter`
    :   The type of the None singleton.

<a id="AccountsInFilter"></a>

`AccountsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_auto_tagging_enabled: list[bool]`
    :   Whether auto-tagging is enabled for the account

    `customer_call_reporting_setting_call_conversion_action: list[str]`
    :   Call conversion action resource name

    `customer_call_reporting_setting_call_conversion_reporting_enabled: list[bool]`
    :   Whether call conversion reporting is enabled

    `customer_call_reporting_setting_call_reporting_enabled: list[bool]`
    :   Whether call reporting is enabled

    `customer_conversion_tracking_setting_conversion_tracking_id: list[int]`
    :   Conversion tracking ID

    `customer_conversion_tracking_setting_cross_account_conversion_tracking_id: list[int]`
    :   Cross-account conversion tracking ID

    `customer_currency_code: list[str]`
    :   Currency code for the account (e.g., USD)

    `customer_descriptive_name: list[str]`
    :   Descriptive name of the customer account

    `customer_final_url_suffix: list[str]`
    :   URL suffix appended to final URLs

    `customer_has_partners_badge: list[bool]`
    :   Whether the account has a Google Partners badge

    `customer_id: list[int]`
    :   Unique customer account ID

    `customer_manager: list[bool]`
    :   Whether this is a manager (MCC) account

    `customer_optimization_score: list[float]`
    :   Optimization score for the account (0.0 to 1.0)

    `customer_optimization_score_weight: list[float]`
    :   Weight of the optimization score

    `customer_pay_per_conversion_eligibility_failure_reasons: list[list[typing.Any]]`
    :   Reasons why pay-per-conversion is not eligible

    `customer_remarketing_setting_google_global_site_tag: list[str]`
    :   Google global site tag snippet

    `customer_resource_name: list[str]`
    :   Resource name of the customer

    `customer_test_account: list[bool]`
    :   Whether this is a test account

    `customer_time_zone: list[str]`
    :   Time zone of the account

    `customer_tracking_url_template: list[str]`
    :   Tracking URL template for the account

    `segments_date: list[str]`
    :   Date segment for the report row

<a id="AccountsKeywordCondition"></a>

`AccountsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_ads.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsLikeCondition"></a>

`AccountsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_ads.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsListParams"></a>

`AccountsListParams(*args, **kwargs)`
:   Parameters for accounts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="AccountsLtCondition"></a>

`AccountsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_ads.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsLteCondition"></a>

`AccountsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_ads.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsNeqCondition"></a>

`AccountsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_ads.types.AccountsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.google_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.google_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsAnyCondition]`
    :   The type of the None singleton.

<a id="AccountsSearchFilter"></a>

`AccountsSearchFilter(*args, **kwargs)`
:   Available fields for filtering accounts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_auto_tagging_enabled: bool | None`
    :   Whether auto-tagging is enabled for the account

    `customer_call_reporting_setting_call_conversion_action: str | None`
    :   Call conversion action resource name

    `customer_call_reporting_setting_call_conversion_reporting_enabled: bool | None`
    :   Whether call conversion reporting is enabled

    `customer_call_reporting_setting_call_reporting_enabled: bool | None`
    :   Whether call reporting is enabled

    `customer_conversion_tracking_setting_conversion_tracking_id: int | None`
    :   Conversion tracking ID

    `customer_conversion_tracking_setting_cross_account_conversion_tracking_id: int | None`
    :   Cross-account conversion tracking ID

    `customer_currency_code: str | None`
    :   Currency code for the account (e.g., USD)

    `customer_descriptive_name: str | None`
    :   Descriptive name of the customer account

    `customer_final_url_suffix: str | None`
    :   URL suffix appended to final URLs

    `customer_has_partners_badge: bool | None`
    :   Whether the account has a Google Partners badge

    `customer_id: int | None`
    :   Unique customer account ID

    `customer_manager: bool | None`
    :   Whether this is a manager (MCC) account

    `customer_optimization_score: float | None`
    :   Optimization score for the account (0.0 to 1.0)

    `customer_optimization_score_weight: float | None`
    :   Weight of the optimization score

    `customer_pay_per_conversion_eligibility_failure_reasons: list[typing.Any] | None`
    :   Reasons why pay-per-conversion is not eligible

    `customer_remarketing_setting_google_global_site_tag: str | None`
    :   Google global site tag snippet

    `customer_resource_name: str | None`
    :   Resource name of the customer

    `customer_test_account: bool | None`
    :   Whether this is a test account

    `customer_time_zone: str | None`
    :   Time zone of the account

    `customer_tracking_url_template: str | None`
    :   Tracking URL template for the account

    `segments_date: str | None`
    :   Date segment for the report row

<a id="AccountsSearchQuery"></a>

`AccountsSearchQuery(*args, **kwargs)`
:   Search query for accounts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_ads.types.AccountsSortFilter]`
    :   The type of the None singleton.

<a id="AccountsSortFilter"></a>

`AccountsSortFilter(*args, **kwargs)`
:   Available fields for sorting accounts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_auto_tagging_enabled: Literal['asc', 'desc']`
    :   Whether auto-tagging is enabled for the account

    `customer_call_reporting_setting_call_conversion_action: Literal['asc', 'desc']`
    :   Call conversion action resource name

    `customer_call_reporting_setting_call_conversion_reporting_enabled: Literal['asc', 'desc']`
    :   Whether call conversion reporting is enabled

    `customer_call_reporting_setting_call_reporting_enabled: Literal['asc', 'desc']`
    :   Whether call reporting is enabled

    `customer_conversion_tracking_setting_conversion_tracking_id: Literal['asc', 'desc']`
    :   Conversion tracking ID

    `customer_conversion_tracking_setting_cross_account_conversion_tracking_id: Literal['asc', 'desc']`
    :   Cross-account conversion tracking ID

    `customer_currency_code: Literal['asc', 'desc']`
    :   Currency code for the account (e.g., USD)

    `customer_descriptive_name: Literal['asc', 'desc']`
    :   Descriptive name of the customer account

    `customer_final_url_suffix: Literal['asc', 'desc']`
    :   URL suffix appended to final URLs

    `customer_has_partners_badge: Literal['asc', 'desc']`
    :   Whether the account has a Google Partners badge

    `customer_id: Literal['asc', 'desc']`
    :   Unique customer account ID

    `customer_manager: Literal['asc', 'desc']`
    :   Whether this is a manager (MCC) account

    `customer_optimization_score: Literal['asc', 'desc']`
    :   Optimization score for the account (0.0 to 1.0)

    `customer_optimization_score_weight: Literal['asc', 'desc']`
    :   Weight of the optimization score

    `customer_pay_per_conversion_eligibility_failure_reasons: Literal['asc', 'desc']`
    :   Reasons why pay-per-conversion is not eligible

    `customer_remarketing_setting_google_global_site_tag: Literal['asc', 'desc']`
    :   Google global site tag snippet

    `customer_resource_name: Literal['asc', 'desc']`
    :   Resource name of the customer

    `customer_test_account: Literal['asc', 'desc']`
    :   Whether this is a test account

    `customer_time_zone: Literal['asc', 'desc']`
    :   Time zone of the account

    `customer_tracking_url_template: Literal['asc', 'desc']`
    :   Tracking URL template for the account

    `segments_date: Literal['asc', 'desc']`
    :   Date segment for the report row

<a id="AccountsStringFilter"></a>

`AccountsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_auto_tagging_enabled: str`
    :   Whether auto-tagging is enabled for the account

    `customer_call_reporting_setting_call_conversion_action: str`
    :   Call conversion action resource name

    `customer_call_reporting_setting_call_conversion_reporting_enabled: str`
    :   Whether call conversion reporting is enabled

    `customer_call_reporting_setting_call_reporting_enabled: str`
    :   Whether call reporting is enabled

    `customer_conversion_tracking_setting_conversion_tracking_id: str`
    :   Conversion tracking ID

    `customer_conversion_tracking_setting_cross_account_conversion_tracking_id: str`
    :   Cross-account conversion tracking ID

    `customer_currency_code: str`
    :   Currency code for the account (e.g., USD)

    `customer_descriptive_name: str`
    :   Descriptive name of the customer account

    `customer_final_url_suffix: str`
    :   URL suffix appended to final URLs

    `customer_has_partners_badge: str`
    :   Whether the account has a Google Partners badge

    `customer_id: str`
    :   Unique customer account ID

    `customer_manager: str`
    :   Whether this is a manager (MCC) account

    `customer_optimization_score: str`
    :   Optimization score for the account (0.0 to 1.0)

    `customer_optimization_score_weight: str`
    :   Weight of the optimization score

    `customer_pay_per_conversion_eligibility_failure_reasons: str`
    :   Reasons why pay-per-conversion is not eligible

    `customer_remarketing_setting_google_global_site_tag: str`
    :   Google global site tag snippet

    `customer_resource_name: str`
    :   Resource name of the customer

    `customer_test_account: str`
    :   Whether this is a test account

    `customer_time_zone: str`
    :   Time zone of the account

    `customer_tracking_url_template: str`
    :   Tracking URL template for the account

    `segments_date: str`
    :   Date segment for the report row

<a id="AdGroupAdLabelsAndCondition"></a>

`AdGroupAdLabelsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsAnyCondition]`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsAnyCondition"></a>

`AdGroupAdLabelsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsAnyValueFilter"></a>

`AdGroupAdLabelsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_ad_id: Any`
    :   Ad ID

    `ad_group_ad_label_resource_name: Any`
    :   Resource name of the ad group ad label

    `label_id: Any`
    :   Label ID

    `label_name: Any`
    :   Label name

    `label_resource_name: Any`
    :   Resource name of the label

<a id="AdGroupAdLabelsContainsCondition"></a>

`AdGroupAdLabelsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsEqCondition"></a>

`AdGroupAdLabelsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsFuzzyCondition"></a>

`AdGroupAdLabelsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsStringFilter`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsGtCondition"></a>

`AdGroupAdLabelsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsGteCondition"></a>

`AdGroupAdLabelsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsInCondition"></a>

`AdGroupAdLabelsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsInFilter`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsInFilter"></a>

`AdGroupAdLabelsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_ad_id: list[int]`
    :   Ad ID

    `ad_group_ad_label_resource_name: list[str]`
    :   Resource name of the ad group ad label

    `label_id: list[int]`
    :   Label ID

    `label_name: list[str]`
    :   Label name

    `label_resource_name: list[str]`
    :   Resource name of the label

<a id="AdGroupAdLabelsKeywordCondition"></a>

`AdGroupAdLabelsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsStringFilter`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsLikeCondition"></a>

`AdGroupAdLabelsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsStringFilter`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsListParams"></a>

`AdGroupAdLabelsListParams(*args, **kwargs)`
:   Parameters for ad_group_ad_labels.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsLtCondition"></a>

`AdGroupAdLabelsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsLteCondition"></a>

`AdGroupAdLabelsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsNeqCondition"></a>

`AdGroupAdLabelsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsNotCondition"></a>

`AdGroupAdLabelsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsAnyCondition`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsOrCondition"></a>

`AdGroupAdLabelsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsAnyCondition]`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsSearchFilter"></a>

`AdGroupAdLabelsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_group_ad_labels search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_ad_id: int | None`
    :   Ad ID

    `ad_group_ad_label_resource_name: str | None`
    :   Resource name of the ad group ad label

    `label_id: int | None`
    :   Label ID

    `label_name: str | None`
    :   Label name

    `label_resource_name: str | None`
    :   Resource name of the label

<a id="AdGroupAdLabelsSearchQuery"></a>

`AdGroupAdLabelsSearchQuery(*args, **kwargs)`
:   Search query for ad_group_ad_labels entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsSortFilter]`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsSortFilter"></a>

`AdGroupAdLabelsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_group_ad_labels search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_ad_id: Literal['asc', 'desc']`
    :   Ad ID

    `ad_group_ad_label_resource_name: Literal['asc', 'desc']`
    :   Resource name of the ad group ad label

    `label_id: Literal['asc', 'desc']`
    :   Label ID

    `label_name: Literal['asc', 'desc']`
    :   Label name

    `label_resource_name: Literal['asc', 'desc']`
    :   Resource name of the label

<a id="AdGroupAdLabelsStringFilter"></a>

`AdGroupAdLabelsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_ad_id: str`
    :   Ad ID

    `ad_group_ad_label_resource_name: str`
    :   Resource name of the ad group ad label

    `label_id: str`
    :   Label ID

    `label_name: str`
    :   Label name

    `label_resource_name: str`
    :   Resource name of the label

<a id="AdGroupAdsAndCondition"></a>

`AdGroupAdsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsAnyCondition]`
    :   The type of the None singleton.

<a id="AdGroupAdsAnyCondition"></a>

`AdGroupAdsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdGroupAdsAnyValueFilter"></a>

`AdGroupAdsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_ad_display_url: Any`
    :   Display URL of the ad

    `ad_group_ad_ad_final_mobile_urls: Any`
    :   Final mobile URLs for the ad

    `ad_group_ad_ad_final_url_suffix: Any`
    :   Final URL suffix

    `ad_group_ad_ad_final_urls: Any`
    :   Final URLs for the ad

    `ad_group_ad_ad_group: Any`
    :   Ad group resource name

    `ad_group_ad_ad_id: Any`
    :   Ad ID

    `ad_group_ad_ad_name: Any`
    :   Ad name

    `ad_group_ad_ad_resource_name: Any`
    :   Resource name of the ad

    `ad_group_ad_ad_strength: Any`
    :   Ad strength rating

    `ad_group_ad_ad_tracking_url_template: Any`
    :   Tracking URL template

    `ad_group_ad_ad_type: Any`
    :   Ad type

    `ad_group_ad_labels: Any`
    :   Labels applied to the ad group ad

    `ad_group_ad_policy_summary_approval_status: Any`
    :   Policy approval status

    `ad_group_ad_policy_summary_review_status: Any`
    :   Policy review status

    `ad_group_ad_resource_name: Any`
    :   Resource name of the ad group ad

    `ad_group_ad_status: Any`
    :   Ad group ad status (ENABLED, PAUSED, REMOVED)

    `ad_group_id: Any`
    :   Parent ad group ID

    `segments_date: Any`
    :   Date segment for the report row

<a id="AdGroupAdsContainsCondition"></a>

`AdGroupAdsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdGroupAdsEqCondition"></a>

`AdGroupAdsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupAdsFuzzyCondition"></a>

`AdGroupAdsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsStringFilter`
    :   The type of the None singleton.

<a id="AdGroupAdsGtCondition"></a>

`AdGroupAdsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupAdsGteCondition"></a>

`AdGroupAdsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupAdsInCondition"></a>

`AdGroupAdsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsInFilter`
    :   The type of the None singleton.

<a id="AdGroupAdsInFilter"></a>

`AdGroupAdsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_ad_display_url: list[str]`
    :   Display URL of the ad

    `ad_group_ad_ad_final_mobile_urls: list[list[typing.Any]]`
    :   Final mobile URLs for the ad

    `ad_group_ad_ad_final_url_suffix: list[str]`
    :   Final URL suffix

    `ad_group_ad_ad_final_urls: list[list[typing.Any]]`
    :   Final URLs for the ad

    `ad_group_ad_ad_group: list[str]`
    :   Ad group resource name

    `ad_group_ad_ad_id: list[int]`
    :   Ad ID

    `ad_group_ad_ad_name: list[str]`
    :   Ad name

    `ad_group_ad_ad_resource_name: list[str]`
    :   Resource name of the ad

    `ad_group_ad_ad_strength: list[str]`
    :   Ad strength rating

    `ad_group_ad_ad_tracking_url_template: list[str]`
    :   Tracking URL template

    `ad_group_ad_ad_type: list[str]`
    :   Ad type

    `ad_group_ad_labels: list[list[typing.Any]]`
    :   Labels applied to the ad group ad

    `ad_group_ad_policy_summary_approval_status: list[str]`
    :   Policy approval status

    `ad_group_ad_policy_summary_review_status: list[str]`
    :   Policy review status

    `ad_group_ad_resource_name: list[str]`
    :   Resource name of the ad group ad

    `ad_group_ad_status: list[str]`
    :   Ad group ad status (ENABLED, PAUSED, REMOVED)

    `ad_group_id: list[int]`
    :   Parent ad group ID

    `segments_date: list[str]`
    :   Date segment for the report row

<a id="AdGroupAdsKeywordCondition"></a>

`AdGroupAdsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsStringFilter`
    :   The type of the None singleton.

<a id="AdGroupAdsLikeCondition"></a>

`AdGroupAdsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsStringFilter`
    :   The type of the None singleton.

<a id="AdGroupAdsListParams"></a>

`AdGroupAdsListParams(*args, **kwargs)`
:   Parameters for ad_group_ads.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="AdGroupAdsLtCondition"></a>

`AdGroupAdsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupAdsLteCondition"></a>

`AdGroupAdsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupAdsNeqCondition"></a>

`AdGroupAdsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupAdsNotCondition"></a>

`AdGroupAdsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsAnyCondition`
    :   The type of the None singleton.

<a id="AdGroupAdsOrCondition"></a>

`AdGroupAdsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsAnyCondition]`
    :   The type of the None singleton.

<a id="AdGroupAdsSearchFilter"></a>

`AdGroupAdsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_group_ads search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_ad_display_url: str | None`
    :   Display URL of the ad

    `ad_group_ad_ad_final_mobile_urls: list[typing.Any] | None`
    :   Final mobile URLs for the ad

    `ad_group_ad_ad_final_url_suffix: str | None`
    :   Final URL suffix

    `ad_group_ad_ad_final_urls: list[typing.Any] | None`
    :   Final URLs for the ad

    `ad_group_ad_ad_group: str | None`
    :   Ad group resource name

    `ad_group_ad_ad_id: int | None`
    :   Ad ID

    `ad_group_ad_ad_name: str | None`
    :   Ad name

    `ad_group_ad_ad_resource_name: str | None`
    :   Resource name of the ad

    `ad_group_ad_ad_strength: str | None`
    :   Ad strength rating

    `ad_group_ad_ad_tracking_url_template: str | None`
    :   Tracking URL template

    `ad_group_ad_ad_type: str | None`
    :   Ad type

    `ad_group_ad_labels: list[typing.Any] | None`
    :   Labels applied to the ad group ad

    `ad_group_ad_policy_summary_approval_status: str | None`
    :   Policy approval status

    `ad_group_ad_policy_summary_review_status: str | None`
    :   Policy review status

    `ad_group_ad_resource_name: str | None`
    :   Resource name of the ad group ad

    `ad_group_ad_status: str | None`
    :   Ad group ad status (ENABLED, PAUSED, REMOVED)

    `ad_group_id: int | None`
    :   Parent ad group ID

    `segments_date: str | None`
    :   Date segment for the report row

<a id="AdGroupAdsSearchQuery"></a>

`AdGroupAdsSearchQuery(*args, **kwargs)`
:   Search query for ad_group_ads entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsSortFilter]`
    :   The type of the None singleton.

<a id="AdGroupAdsSortFilter"></a>

`AdGroupAdsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_group_ads search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_ad_display_url: Literal['asc', 'desc']`
    :   Display URL of the ad

    `ad_group_ad_ad_final_mobile_urls: Literal['asc', 'desc']`
    :   Final mobile URLs for the ad

    `ad_group_ad_ad_final_url_suffix: Literal['asc', 'desc']`
    :   Final URL suffix

    `ad_group_ad_ad_final_urls: Literal['asc', 'desc']`
    :   Final URLs for the ad

    `ad_group_ad_ad_group: Literal['asc', 'desc']`
    :   Ad group resource name

    `ad_group_ad_ad_id: Literal['asc', 'desc']`
    :   Ad ID

    `ad_group_ad_ad_name: Literal['asc', 'desc']`
    :   Ad name

    `ad_group_ad_ad_resource_name: Literal['asc', 'desc']`
    :   Resource name of the ad

    `ad_group_ad_ad_strength: Literal['asc', 'desc']`
    :   Ad strength rating

    `ad_group_ad_ad_tracking_url_template: Literal['asc', 'desc']`
    :   Tracking URL template

    `ad_group_ad_ad_type: Literal['asc', 'desc']`
    :   Ad type

    `ad_group_ad_labels: Literal['asc', 'desc']`
    :   Labels applied to the ad group ad

    `ad_group_ad_policy_summary_approval_status: Literal['asc', 'desc']`
    :   Policy approval status

    `ad_group_ad_policy_summary_review_status: Literal['asc', 'desc']`
    :   Policy review status

    `ad_group_ad_resource_name: Literal['asc', 'desc']`
    :   Resource name of the ad group ad

    `ad_group_ad_status: Literal['asc', 'desc']`
    :   Ad group ad status (ENABLED, PAUSED, REMOVED)

    `ad_group_id: Literal['asc', 'desc']`
    :   Parent ad group ID

    `segments_date: Literal['asc', 'desc']`
    :   Date segment for the report row

<a id="AdGroupAdsStringFilter"></a>

`AdGroupAdsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_ad_display_url: str`
    :   Display URL of the ad

    `ad_group_ad_ad_final_mobile_urls: str`
    :   Final mobile URLs for the ad

    `ad_group_ad_ad_final_url_suffix: str`
    :   Final URL suffix

    `ad_group_ad_ad_final_urls: str`
    :   Final URLs for the ad

    `ad_group_ad_ad_group: str`
    :   Ad group resource name

    `ad_group_ad_ad_id: str`
    :   Ad ID

    `ad_group_ad_ad_name: str`
    :   Ad name

    `ad_group_ad_ad_resource_name: str`
    :   Resource name of the ad

    `ad_group_ad_ad_strength: str`
    :   Ad strength rating

    `ad_group_ad_ad_tracking_url_template: str`
    :   Tracking URL template

    `ad_group_ad_ad_type: str`
    :   Ad type

    `ad_group_ad_labels: str`
    :   Labels applied to the ad group ad

    `ad_group_ad_policy_summary_approval_status: str`
    :   Policy approval status

    `ad_group_ad_policy_summary_review_status: str`
    :   Policy review status

    `ad_group_ad_resource_name: str`
    :   Resource name of the ad group ad

    `ad_group_ad_status: str`
    :   Ad group ad status (ENABLED, PAUSED, REMOVED)

    `ad_group_id: str`
    :   Parent ad group ID

    `segments_date: str`
    :   Date segment for the report row

<a id="AdGroupLabelsAndCondition"></a>

`AdGroupLabelsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsAnyCondition]`
    :   The type of the None singleton.

<a id="AdGroupLabelsAnyCondition"></a>

`AdGroupLabelsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdGroupLabelsAnyValueFilter"></a>

`AdGroupLabelsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_id: Any`
    :   Ad group ID

    `ad_group_label_resource_name: Any`
    :   Resource name of the ad group label

    `label_id: Any`
    :   Label ID

    `label_name: Any`
    :   Label name

    `label_resource_name: Any`
    :   Resource name of the label

<a id="AdGroupLabelsContainsCondition"></a>

`AdGroupLabelsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdGroupLabelsCreateParams"></a>

`AdGroupLabelsCreateParams(*args, **kwargs)`
:   Parameters for ad_group_labels.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsCreateParamsOperationsItem]`
    :   The type of the None singleton.

<a id="AdGroupLabelsCreateParamsOperationsItem"></a>

`AdGroupLabelsCreateParamsOperationsItem(*args, **kwargs)`
:   Nested schema for AdGroupLabelsCreateParams.operations_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsCreateParamsOperationsItemCreate`
    :   The type of the None singleton.

<a id="AdGroupLabelsCreateParamsOperationsItemCreate"></a>

`AdGroupLabelsCreateParamsOperationsItemCreate(*args, **kwargs)`
:   Ad group label association to create

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adGroup: str`
    :   The type of the None singleton.

    `label: str`
    :   The type of the None singleton.

<a id="AdGroupLabelsEqCondition"></a>

`AdGroupLabelsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupLabelsFuzzyCondition"></a>

`AdGroupLabelsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsStringFilter`
    :   The type of the None singleton.

<a id="AdGroupLabelsGtCondition"></a>

`AdGroupLabelsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupLabelsGteCondition"></a>

`AdGroupLabelsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupLabelsInCondition"></a>

`AdGroupLabelsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsInFilter`
    :   The type of the None singleton.

<a id="AdGroupLabelsInFilter"></a>

`AdGroupLabelsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_id: list[int]`
    :   Ad group ID

    `ad_group_label_resource_name: list[str]`
    :   Resource name of the ad group label

    `label_id: list[int]`
    :   Label ID

    `label_name: list[str]`
    :   Label name

    `label_resource_name: list[str]`
    :   Resource name of the label

<a id="AdGroupLabelsKeywordCondition"></a>

`AdGroupLabelsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsStringFilter`
    :   The type of the None singleton.

<a id="AdGroupLabelsLikeCondition"></a>

`AdGroupLabelsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsStringFilter`
    :   The type of the None singleton.

<a id="AdGroupLabelsListParams"></a>

`AdGroupLabelsListParams(*args, **kwargs)`
:   Parameters for ad_group_labels.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="AdGroupLabelsLtCondition"></a>

`AdGroupLabelsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupLabelsLteCondition"></a>

`AdGroupLabelsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupLabelsNeqCondition"></a>

`AdGroupLabelsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupLabelsNotCondition"></a>

`AdGroupLabelsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsAnyCondition`
    :   The type of the None singleton.

<a id="AdGroupLabelsOrCondition"></a>

`AdGroupLabelsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsAnyCondition]`
    :   The type of the None singleton.

<a id="AdGroupLabelsSearchFilter"></a>

`AdGroupLabelsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_group_labels search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_id: int | None`
    :   Ad group ID

    `ad_group_label_resource_name: str | None`
    :   Resource name of the ad group label

    `label_id: int | None`
    :   Label ID

    `label_name: str | None`
    :   Label name

    `label_resource_name: str | None`
    :   Resource name of the label

<a id="AdGroupLabelsSearchQuery"></a>

`AdGroupLabelsSearchQuery(*args, **kwargs)`
:   Search query for ad_group_labels entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsSortFilter]`
    :   The type of the None singleton.

<a id="AdGroupLabelsSortFilter"></a>

`AdGroupLabelsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_group_labels search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_id: Literal['asc', 'desc']`
    :   Ad group ID

    `ad_group_label_resource_name: Literal['asc', 'desc']`
    :   Resource name of the ad group label

    `label_id: Literal['asc', 'desc']`
    :   Label ID

    `label_name: Literal['asc', 'desc']`
    :   Label name

    `label_resource_name: Literal['asc', 'desc']`
    :   Resource name of the label

<a id="AdGroupLabelsStringFilter"></a>

`AdGroupLabelsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_id: str`
    :   Ad group ID

    `ad_group_label_resource_name: str`
    :   Resource name of the ad group label

    `label_id: str`
    :   Label ID

    `label_name: str`
    :   Label name

    `label_resource_name: str`
    :   Resource name of the label

<a id="AdGroupsAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAnyCondition]`
    :   The type of the None singleton.

<a id="AdGroupsAnyCondition"></a>

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

    `any: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdGroupsAnyValueFilter"></a>

`AdGroupsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_rotation_mode: Any`
    :   Ad rotation mode

    `ad_group_base_ad_group: Any`
    :   Base ad group resource name

    `ad_group_campaign: Any`
    :   Parent campaign resource name

    `ad_group_cpc_bid_micros: Any`
    :   CPC bid in micros

    `ad_group_cpm_bid_micros: Any`
    :   CPM bid in micros

    `ad_group_cpv_bid_micros: Any`
    :   CPV bid in micros

    `ad_group_effective_target_cpa_micros: Any`
    :   Effective target CPA in micros

    `ad_group_effective_target_cpa_source: Any`
    :   Source of the effective target CPA

    `ad_group_effective_target_roas: Any`
    :   Effective target ROAS

    `ad_group_effective_target_roas_source: Any`
    :   Source of the effective target ROAS

    `ad_group_id: Any`
    :   Ad group ID

    `ad_group_labels: Any`
    :   Labels applied to the ad group

    `ad_group_name: Any`
    :   Ad group name

    `ad_group_resource_name: Any`
    :   Resource name of the ad group

    `ad_group_status: Any`
    :   Ad group status (ENABLED, PAUSED, REMOVED)

    `ad_group_target_cpa_micros: Any`
    :   Target CPA in micros

    `ad_group_target_roas: Any`
    :   Target ROAS

    `ad_group_tracking_url_template: Any`
    :   Tracking URL template

    `ad_group_type: Any`
    :   Ad group type

    `campaign_id: Any`
    :   Parent campaign ID

    `metrics_cost_micros: Any`
    :   Cost in micros

    `segments_date: Any`
    :   Date segment for the report row

<a id="AdGroupsContainsCondition"></a>

`AdGroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdGroupsEqCondition"></a>

`AdGroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupsFuzzyCondition"></a>

`AdGroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsStringFilter`
    :   The type of the None singleton.

<a id="AdGroupsGtCondition"></a>

`AdGroupsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupsGteCondition"></a>

`AdGroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupsInCondition"></a>

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

    `in: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsInFilter`
    :   The type of the None singleton.

<a id="AdGroupsInFilter"></a>

`AdGroupsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_rotation_mode: list[str]`
    :   Ad rotation mode

    `ad_group_base_ad_group: list[str]`
    :   Base ad group resource name

    `ad_group_campaign: list[str]`
    :   Parent campaign resource name

    `ad_group_cpc_bid_micros: list[int]`
    :   CPC bid in micros

    `ad_group_cpm_bid_micros: list[int]`
    :   CPM bid in micros

    `ad_group_cpv_bid_micros: list[int]`
    :   CPV bid in micros

    `ad_group_effective_target_cpa_micros: list[int]`
    :   Effective target CPA in micros

    `ad_group_effective_target_cpa_source: list[str]`
    :   Source of the effective target CPA

    `ad_group_effective_target_roas: list[float]`
    :   Effective target ROAS

    `ad_group_effective_target_roas_source: list[str]`
    :   Source of the effective target ROAS

    `ad_group_id: list[int]`
    :   Ad group ID

    `ad_group_labels: list[list[typing.Any]]`
    :   Labels applied to the ad group

    `ad_group_name: list[str]`
    :   Ad group name

    `ad_group_resource_name: list[str]`
    :   Resource name of the ad group

    `ad_group_status: list[str]`
    :   Ad group status (ENABLED, PAUSED, REMOVED)

    `ad_group_target_cpa_micros: list[int]`
    :   Target CPA in micros

    `ad_group_target_roas: list[float]`
    :   Target ROAS

    `ad_group_tracking_url_template: list[str]`
    :   Tracking URL template

    `ad_group_type: list[str]`
    :   Ad group type

    `campaign_id: list[int]`
    :   Parent campaign ID

    `metrics_cost_micros: list[int]`
    :   Cost in micros

    `segments_date: list[str]`
    :   Date segment for the report row

<a id="AdGroupsKeywordCondition"></a>

`AdGroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsStringFilter`
    :   The type of the None singleton.

<a id="AdGroupsLikeCondition"></a>

`AdGroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsStringFilter`
    :   The type of the None singleton.

<a id="AdGroupsListParams"></a>

`AdGroupsListParams(*args, **kwargs)`
:   Parameters for ad_groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="AdGroupsLtCondition"></a>

`AdGroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupsLteCondition"></a>

`AdGroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupsNeqCondition"></a>

`AdGroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

<a id="AdGroupsNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAnyCondition`
    :   The type of the None singleton.

<a id="AdGroupsOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAnyCondition]`
    :   The type of the None singleton.

<a id="AdGroupsSearchFilter"></a>

`AdGroupsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_groups search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_rotation_mode: str | None`
    :   Ad rotation mode

    `ad_group_base_ad_group: str | None`
    :   Base ad group resource name

    `ad_group_campaign: str | None`
    :   Parent campaign resource name

    `ad_group_cpc_bid_micros: int | None`
    :   CPC bid in micros

    `ad_group_cpm_bid_micros: int | None`
    :   CPM bid in micros

    `ad_group_cpv_bid_micros: int | None`
    :   CPV bid in micros

    `ad_group_effective_target_cpa_micros: int | None`
    :   Effective target CPA in micros

    `ad_group_effective_target_cpa_source: str | None`
    :   Source of the effective target CPA

    `ad_group_effective_target_roas: float | None`
    :   Effective target ROAS

    `ad_group_effective_target_roas_source: str | None`
    :   Source of the effective target ROAS

    `ad_group_id: int | None`
    :   Ad group ID

    `ad_group_labels: list[typing.Any] | None`
    :   Labels applied to the ad group

    `ad_group_name: str | None`
    :   Ad group name

    `ad_group_resource_name: str | None`
    :   Resource name of the ad group

    `ad_group_status: str | None`
    :   Ad group status (ENABLED, PAUSED, REMOVED)

    `ad_group_target_cpa_micros: int | None`
    :   Target CPA in micros

    `ad_group_target_roas: float | None`
    :   Target ROAS

    `ad_group_tracking_url_template: str | None`
    :   Tracking URL template

    `ad_group_type: str | None`
    :   Ad group type

    `campaign_id: int | None`
    :   Parent campaign ID

    `metrics_cost_micros: int | None`
    :   Cost in micros

    `segments_date: str | None`
    :   Date segment for the report row

<a id="AdGroupsSearchQuery"></a>

`AdGroupsSearchQuery(*args, **kwargs)`
:   Search query for ad_groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupsSortFilter]`
    :   The type of the None singleton.

<a id="AdGroupsSortFilter"></a>

`AdGroupsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_groups search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_rotation_mode: Literal['asc', 'desc']`
    :   Ad rotation mode

    `ad_group_base_ad_group: Literal['asc', 'desc']`
    :   Base ad group resource name

    `ad_group_campaign: Literal['asc', 'desc']`
    :   Parent campaign resource name

    `ad_group_cpc_bid_micros: Literal['asc', 'desc']`
    :   CPC bid in micros

    `ad_group_cpm_bid_micros: Literal['asc', 'desc']`
    :   CPM bid in micros

    `ad_group_cpv_bid_micros: Literal['asc', 'desc']`
    :   CPV bid in micros

    `ad_group_effective_target_cpa_micros: Literal['asc', 'desc']`
    :   Effective target CPA in micros

    `ad_group_effective_target_cpa_source: Literal['asc', 'desc']`
    :   Source of the effective target CPA

    `ad_group_effective_target_roas: Literal['asc', 'desc']`
    :   Effective target ROAS

    `ad_group_effective_target_roas_source: Literal['asc', 'desc']`
    :   Source of the effective target ROAS

    `ad_group_id: Literal['asc', 'desc']`
    :   Ad group ID

    `ad_group_labels: Literal['asc', 'desc']`
    :   Labels applied to the ad group

    `ad_group_name: Literal['asc', 'desc']`
    :   Ad group name

    `ad_group_resource_name: Literal['asc', 'desc']`
    :   Resource name of the ad group

    `ad_group_status: Literal['asc', 'desc']`
    :   Ad group status (ENABLED, PAUSED, REMOVED)

    `ad_group_target_cpa_micros: Literal['asc', 'desc']`
    :   Target CPA in micros

    `ad_group_target_roas: Literal['asc', 'desc']`
    :   Target ROAS

    `ad_group_tracking_url_template: Literal['asc', 'desc']`
    :   Tracking URL template

    `ad_group_type: Literal['asc', 'desc']`
    :   Ad group type

    `campaign_id: Literal['asc', 'desc']`
    :   Parent campaign ID

    `metrics_cost_micros: Literal['asc', 'desc']`
    :   Cost in micros

    `segments_date: Literal['asc', 'desc']`
    :   Date segment for the report row

<a id="AdGroupsStringFilter"></a>

`AdGroupsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_group_ad_rotation_mode: str`
    :   Ad rotation mode

    `ad_group_base_ad_group: str`
    :   Base ad group resource name

    `ad_group_campaign: str`
    :   Parent campaign resource name

    `ad_group_cpc_bid_micros: str`
    :   CPC bid in micros

    `ad_group_cpm_bid_micros: str`
    :   CPM bid in micros

    `ad_group_cpv_bid_micros: str`
    :   CPV bid in micros

    `ad_group_effective_target_cpa_micros: str`
    :   Effective target CPA in micros

    `ad_group_effective_target_cpa_source: str`
    :   Source of the effective target CPA

    `ad_group_effective_target_roas: str`
    :   Effective target ROAS

    `ad_group_effective_target_roas_source: str`
    :   Source of the effective target ROAS

    `ad_group_id: str`
    :   Ad group ID

    `ad_group_labels: str`
    :   Labels applied to the ad group

    `ad_group_name: str`
    :   Ad group name

    `ad_group_resource_name: str`
    :   Resource name of the ad group

    `ad_group_status: str`
    :   Ad group status (ENABLED, PAUSED, REMOVED)

    `ad_group_target_cpa_micros: str`
    :   Target CPA in micros

    `ad_group_target_roas: str`
    :   Target ROAS

    `ad_group_tracking_url_template: str`
    :   Tracking URL template

    `ad_group_type: str`
    :   Ad group type

    `campaign_id: str`
    :   Parent campaign ID

    `metrics_cost_micros: str`
    :   Cost in micros

    `segments_date: str`
    :   Date segment for the report row

<a id="AdGroupsUpdateParams"></a>

`AdGroupsUpdateParams(*args, **kwargs)`
:   Parameters for ad_groups.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupsUpdateParamsOperationsItem]`
    :   The type of the None singleton.

<a id="AdGroupsUpdateParamsOperationsItem"></a>

`AdGroupsUpdateParamsOperationsItem(*args, **kwargs)`
:   Nested schema for AdGroupsUpdateParams.operations_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `updateMask: str`
    :   The type of the None singleton.

    ### Methods

    `update(...) ‑> airbyte_agent_sdk.connectors.google_ads.types.AdGroupsUpdateParamsOperationsItemUpdate`
    :   D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
        If E is present and has a .keys() method, then does:  for k in E.keys(): D[k] = E[k]
        If E is present and lacks a .keys() method, then does:  for k, v in E: D[k] = v
        In either case, this is followed by: for k in F:  D[k] = F[k]

<a id="AdGroupsUpdateParamsOperationsItemUpdate"></a>

`AdGroupsUpdateParamsOperationsItemUpdate(*args, **kwargs)`
:   Ad group fields to update

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cpcBidMicros: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `resourceName: str`
    :   The type of the None singleton.

    `status: str`
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

<a id="CampaignLabelsAndCondition"></a>

`CampaignLabelsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignLabelsAnyCondition"></a>

`CampaignLabelsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignLabelsAnyValueFilter"></a>

`CampaignLabelsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: Any`
    :   Campaign ID

    `campaign_label_resource_name: Any`
    :   Resource name of the campaign label

    `label_id: Any`
    :   Label ID

    `label_name: Any`
    :   Label name

    `label_resource_name: Any`
    :   Resource name of the label

<a id="CampaignLabelsContainsCondition"></a>

`CampaignLabelsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignLabelsCreateParams"></a>

`CampaignLabelsCreateParams(*args, **kwargs)`
:   Parameters for campaign_labels.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsCreateParamsOperationsItem]`
    :   The type of the None singleton.

<a id="CampaignLabelsCreateParamsOperationsItem"></a>

`CampaignLabelsCreateParamsOperationsItem(*args, **kwargs)`
:   Nested schema for CampaignLabelsCreateParams.operations_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsCreateParamsOperationsItemCreate`
    :   The type of the None singleton.

<a id="CampaignLabelsCreateParamsOperationsItemCreate"></a>

`CampaignLabelsCreateParamsOperationsItemCreate(*args, **kwargs)`
:   Campaign label association to create

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign: str`
    :   The type of the None singleton.

    `label: str`
    :   The type of the None singleton.

<a id="CampaignLabelsEqCondition"></a>

`CampaignLabelsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignLabelsFuzzyCondition"></a>

`CampaignLabelsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsStringFilter`
    :   The type of the None singleton.

<a id="CampaignLabelsGtCondition"></a>

`CampaignLabelsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignLabelsGteCondition"></a>

`CampaignLabelsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignLabelsInCondition"></a>

`CampaignLabelsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsInFilter`
    :   The type of the None singleton.

<a id="CampaignLabelsInFilter"></a>

`CampaignLabelsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: list[int]`
    :   Campaign ID

    `campaign_label_resource_name: list[str]`
    :   Resource name of the campaign label

    `label_id: list[int]`
    :   Label ID

    `label_name: list[str]`
    :   Label name

    `label_resource_name: list[str]`
    :   Resource name of the label

<a id="CampaignLabelsKeywordCondition"></a>

`CampaignLabelsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsStringFilter`
    :   The type of the None singleton.

<a id="CampaignLabelsLikeCondition"></a>

`CampaignLabelsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsStringFilter`
    :   The type of the None singleton.

<a id="CampaignLabelsListParams"></a>

`CampaignLabelsListParams(*args, **kwargs)`
:   Parameters for campaign_labels.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="CampaignLabelsLtCondition"></a>

`CampaignLabelsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignLabelsLteCondition"></a>

`CampaignLabelsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignLabelsNeqCondition"></a>

`CampaignLabelsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignLabelsNotCondition"></a>

`CampaignLabelsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsAnyCondition`
    :   The type of the None singleton.

<a id="CampaignLabelsOrCondition"></a>

`CampaignLabelsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignLabelsSearchFilter"></a>

`CampaignLabelsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaign_labels search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: int | None`
    :   Campaign ID

    `campaign_label_resource_name: str | None`
    :   Resource name of the campaign label

    `label_id: int | None`
    :   Label ID

    `label_name: str | None`
    :   Label name

    `label_resource_name: str | None`
    :   Resource name of the label

<a id="CampaignLabelsSearchQuery"></a>

`CampaignLabelsSearchQuery(*args, **kwargs)`
:   Search query for campaign_labels entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsSortFilter]`
    :   The type of the None singleton.

<a id="CampaignLabelsSortFilter"></a>

`CampaignLabelsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaign_labels search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: Literal['asc', 'desc']`
    :   Campaign ID

    `campaign_label_resource_name: Literal['asc', 'desc']`
    :   Resource name of the campaign label

    `label_id: Literal['asc', 'desc']`
    :   Label ID

    `label_name: Literal['asc', 'desc']`
    :   Label name

    `label_resource_name: Literal['asc', 'desc']`
    :   Resource name of the label

<a id="CampaignLabelsStringFilter"></a>

`CampaignLabelsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: str`
    :   Campaign ID

    `campaign_label_resource_name: str`
    :   Resource name of the campaign label

    `label_id: str`
    :   Label ID

    `label_name: str`
    :   Label name

    `label_resource_name: str`
    :   Resource name of the label

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

    `and: list[airbyte_agent_sdk.connectors.google_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.google_ads.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsAnyValueFilter"></a>

`CampaignsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_advertising_channel_sub_type: Any`
    :   Advertising channel sub-type

    `campaign_advertising_channel_type: Any`
    :   Advertising channel type (SEARCH, DISPLAY, etc.)

    `campaign_bidding_strategy: Any`
    :   Bidding strategy resource name

    `campaign_bidding_strategy_type: Any`
    :   Bidding strategy type

    `campaign_budget_amount_micros: Any`
    :   Campaign budget amount in micros

    `campaign_campaign_budget: Any`
    :   Campaign budget resource name

    `campaign_end_date: Any`
    :   Campaign end date

    `campaign_id: Any`
    :   Campaign ID

    `campaign_labels: Any`
    :   Labels applied to the campaign

    `campaign_name: Any`
    :   Campaign name

    `campaign_network_settings_target_content_network: Any`
    :   Whether targeting content network

    `campaign_network_settings_target_google_search: Any`
    :   Whether targeting Google Search

    `campaign_network_settings_target_partner_search_network: Any`
    :   Whether targeting partner search network

    `campaign_network_settings_target_search_network: Any`
    :   Whether targeting search network

    `campaign_resource_name: Any`
    :   Resource name of the campaign

    `campaign_serving_status: Any`
    :   Campaign serving status

    `campaign_start_date: Any`
    :   Campaign start date

    `campaign_status: Any`
    :   Campaign status (ENABLED, PAUSED, REMOVED)

    `metrics_average_cpc: Any`
    :   Average cost per click

    `metrics_average_cpm: Any`
    :   Average cost per thousand impressions

    `metrics_clicks: Any`
    :   Number of clicks

    `metrics_conversions: Any`
    :   Number of conversions

    `metrics_conversions_value: Any`
    :   Total conversions value

    `metrics_cost_micros: Any`
    :   Cost in micros

    `metrics_ctr: Any`
    :   Click-through rate

    `metrics_impressions: Any`
    :   Number of impressions

    `metrics_interactions: Any`
    :   Number of interactions

    `segments_ad_network_type: Any`
    :   Ad network type segment

    `segments_date: Any`
    :   Date segment for the report row

    `segments_hour: Any`
    :   Hour segment

<a id="CampaignsContainsCondition"></a>

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_ads.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsEqCondition"></a>

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsFuzzyCondition"></a>

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_ads.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsGtCondition"></a>

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsGteCondition"></a>

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_ads.types.CampaignsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.google_ads.types.CampaignsInFilter`
    :   The type of the None singleton.

<a id="CampaignsInFilter"></a>

`CampaignsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_advertising_channel_sub_type: list[str]`
    :   Advertising channel sub-type

    `campaign_advertising_channel_type: list[str]`
    :   Advertising channel type (SEARCH, DISPLAY, etc.)

    `campaign_bidding_strategy: list[str]`
    :   Bidding strategy resource name

    `campaign_bidding_strategy_type: list[str]`
    :   Bidding strategy type

    `campaign_budget_amount_micros: list[int]`
    :   Campaign budget amount in micros

    `campaign_campaign_budget: list[str]`
    :   Campaign budget resource name

    `campaign_end_date: list[str]`
    :   Campaign end date

    `campaign_id: list[int]`
    :   Campaign ID

    `campaign_labels: list[list[typing.Any]]`
    :   Labels applied to the campaign

    `campaign_name: list[str]`
    :   Campaign name

    `campaign_network_settings_target_content_network: list[bool]`
    :   Whether targeting content network

    `campaign_network_settings_target_google_search: list[bool]`
    :   Whether targeting Google Search

    `campaign_network_settings_target_partner_search_network: list[bool]`
    :   Whether targeting partner search network

    `campaign_network_settings_target_search_network: list[bool]`
    :   Whether targeting search network

    `campaign_resource_name: list[str]`
    :   Resource name of the campaign

    `campaign_serving_status: list[str]`
    :   Campaign serving status

    `campaign_start_date: list[str]`
    :   Campaign start date

    `campaign_status: list[str]`
    :   Campaign status (ENABLED, PAUSED, REMOVED)

    `metrics_average_cpc: list[float]`
    :   Average cost per click

    `metrics_average_cpm: list[float]`
    :   Average cost per thousand impressions

    `metrics_clicks: list[int]`
    :   Number of clicks

    `metrics_conversions: list[float]`
    :   Number of conversions

    `metrics_conversions_value: list[float]`
    :   Total conversions value

    `metrics_cost_micros: list[int]`
    :   Cost in micros

    `metrics_ctr: list[float]`
    :   Click-through rate

    `metrics_impressions: list[int]`
    :   Number of impressions

    `metrics_interactions: list[int]`
    :   Number of interactions

    `segments_ad_network_type: list[str]`
    :   Ad network type segment

    `segments_date: list[str]`
    :   Date segment for the report row

    `segments_hour: list[int]`
    :   Hour segment

<a id="CampaignsKeywordCondition"></a>

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_ads.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsLikeCondition"></a>

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_ads.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsListParams"></a>

`CampaignsListParams(*args, **kwargs)`
:   Parameters for campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="CampaignsLtCondition"></a>

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsLteCondition"></a>

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsNeqCondition"></a>

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_ads.types.CampaignsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.google_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.google_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignsSearchFilter"></a>

`CampaignsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaigns search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_advertising_channel_sub_type: str | None`
    :   Advertising channel sub-type

    `campaign_advertising_channel_type: str | None`
    :   Advertising channel type (SEARCH, DISPLAY, etc.)

    `campaign_bidding_strategy: str | None`
    :   Bidding strategy resource name

    `campaign_bidding_strategy_type: str | None`
    :   Bidding strategy type

    `campaign_budget_amount_micros: int | None`
    :   Campaign budget amount in micros

    `campaign_campaign_budget: str | None`
    :   Campaign budget resource name

    `campaign_end_date: str | None`
    :   Campaign end date

    `campaign_id: int | None`
    :   Campaign ID

    `campaign_labels: list[typing.Any] | None`
    :   Labels applied to the campaign

    `campaign_name: str | None`
    :   Campaign name

    `campaign_network_settings_target_content_network: bool | None`
    :   Whether targeting content network

    `campaign_network_settings_target_google_search: bool | None`
    :   Whether targeting Google Search

    `campaign_network_settings_target_partner_search_network: bool | None`
    :   Whether targeting partner search network

    `campaign_network_settings_target_search_network: bool | None`
    :   Whether targeting search network

    `campaign_resource_name: str | None`
    :   Resource name of the campaign

    `campaign_serving_status: str | None`
    :   Campaign serving status

    `campaign_start_date: str | None`
    :   Campaign start date

    `campaign_status: str | None`
    :   Campaign status (ENABLED, PAUSED, REMOVED)

    `metrics_average_cpc: float | None`
    :   Average cost per click

    `metrics_average_cpm: float | None`
    :   Average cost per thousand impressions

    `metrics_clicks: int | None`
    :   Number of clicks

    `metrics_conversions: float | None`
    :   Number of conversions

    `metrics_conversions_value: float | None`
    :   Total conversions value

    `metrics_cost_micros: int | None`
    :   Cost in micros

    `metrics_ctr: float | None`
    :   Click-through rate

    `metrics_impressions: int | None`
    :   Number of impressions

    `metrics_interactions: int | None`
    :   Number of interactions

    `segments_ad_network_type: str | None`
    :   Ad network type segment

    `segments_date: str | None`
    :   Date segment for the report row

    `segments_hour: int | None`
    :   Hour segment

<a id="CampaignsSearchQuery"></a>

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_ads.types.CampaignsSortFilter]`
    :   The type of the None singleton.

<a id="CampaignsSortFilter"></a>

`CampaignsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaigns search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_advertising_channel_sub_type: Literal['asc', 'desc']`
    :   Advertising channel sub-type

    `campaign_advertising_channel_type: Literal['asc', 'desc']`
    :   Advertising channel type (SEARCH, DISPLAY, etc.)

    `campaign_bidding_strategy: Literal['asc', 'desc']`
    :   Bidding strategy resource name

    `campaign_bidding_strategy_type: Literal['asc', 'desc']`
    :   Bidding strategy type

    `campaign_budget_amount_micros: Literal['asc', 'desc']`
    :   Campaign budget amount in micros

    `campaign_campaign_budget: Literal['asc', 'desc']`
    :   Campaign budget resource name

    `campaign_end_date: Literal['asc', 'desc']`
    :   Campaign end date

    `campaign_id: Literal['asc', 'desc']`
    :   Campaign ID

    `campaign_labels: Literal['asc', 'desc']`
    :   Labels applied to the campaign

    `campaign_name: Literal['asc', 'desc']`
    :   Campaign name

    `campaign_network_settings_target_content_network: Literal['asc', 'desc']`
    :   Whether targeting content network

    `campaign_network_settings_target_google_search: Literal['asc', 'desc']`
    :   Whether targeting Google Search

    `campaign_network_settings_target_partner_search_network: Literal['asc', 'desc']`
    :   Whether targeting partner search network

    `campaign_network_settings_target_search_network: Literal['asc', 'desc']`
    :   Whether targeting search network

    `campaign_resource_name: Literal['asc', 'desc']`
    :   Resource name of the campaign

    `campaign_serving_status: Literal['asc', 'desc']`
    :   Campaign serving status

    `campaign_start_date: Literal['asc', 'desc']`
    :   Campaign start date

    `campaign_status: Literal['asc', 'desc']`
    :   Campaign status (ENABLED, PAUSED, REMOVED)

    `metrics_average_cpc: Literal['asc', 'desc']`
    :   Average cost per click

    `metrics_average_cpm: Literal['asc', 'desc']`
    :   Average cost per thousand impressions

    `metrics_clicks: Literal['asc', 'desc']`
    :   Number of clicks

    `metrics_conversions: Literal['asc', 'desc']`
    :   Number of conversions

    `metrics_conversions_value: Literal['asc', 'desc']`
    :   Total conversions value

    `metrics_cost_micros: Literal['asc', 'desc']`
    :   Cost in micros

    `metrics_ctr: Literal['asc', 'desc']`
    :   Click-through rate

    `metrics_impressions: Literal['asc', 'desc']`
    :   Number of impressions

    `metrics_interactions: Literal['asc', 'desc']`
    :   Number of interactions

    `segments_ad_network_type: Literal['asc', 'desc']`
    :   Ad network type segment

    `segments_date: Literal['asc', 'desc']`
    :   Date segment for the report row

    `segments_hour: Literal['asc', 'desc']`
    :   Hour segment

<a id="CampaignsStringFilter"></a>

`CampaignsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_advertising_channel_sub_type: str`
    :   Advertising channel sub-type

    `campaign_advertising_channel_type: str`
    :   Advertising channel type (SEARCH, DISPLAY, etc.)

    `campaign_bidding_strategy: str`
    :   Bidding strategy resource name

    `campaign_bidding_strategy_type: str`
    :   Bidding strategy type

    `campaign_budget_amount_micros: str`
    :   Campaign budget amount in micros

    `campaign_campaign_budget: str`
    :   Campaign budget resource name

    `campaign_end_date: str`
    :   Campaign end date

    `campaign_id: str`
    :   Campaign ID

    `campaign_labels: str`
    :   Labels applied to the campaign

    `campaign_name: str`
    :   Campaign name

    `campaign_network_settings_target_content_network: str`
    :   Whether targeting content network

    `campaign_network_settings_target_google_search: str`
    :   Whether targeting Google Search

    `campaign_network_settings_target_partner_search_network: str`
    :   Whether targeting partner search network

    `campaign_network_settings_target_search_network: str`
    :   Whether targeting search network

    `campaign_resource_name: str`
    :   Resource name of the campaign

    `campaign_serving_status: str`
    :   Campaign serving status

    `campaign_start_date: str`
    :   Campaign start date

    `campaign_status: str`
    :   Campaign status (ENABLED, PAUSED, REMOVED)

    `metrics_average_cpc: str`
    :   Average cost per click

    `metrics_average_cpm: str`
    :   Average cost per thousand impressions

    `metrics_clicks: str`
    :   Number of clicks

    `metrics_conversions: str`
    :   Number of conversions

    `metrics_conversions_value: str`
    :   Total conversions value

    `metrics_cost_micros: str`
    :   Cost in micros

    `metrics_ctr: str`
    :   Click-through rate

    `metrics_impressions: str`
    :   Number of impressions

    `metrics_interactions: str`
    :   Number of interactions

    `segments_ad_network_type: str`
    :   Ad network type segment

    `segments_date: str`
    :   Date segment for the report row

    `segments_hour: str`
    :   Hour segment

<a id="CampaignsUpdateParams"></a>

`CampaignsUpdateParams(*args, **kwargs)`
:   Parameters for campaigns.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.types.CampaignsUpdateParamsOperationsItem]`
    :   The type of the None singleton.

<a id="CampaignsUpdateParamsOperationsItem"></a>

`CampaignsUpdateParamsOperationsItem(*args, **kwargs)`
:   Nested schema for CampaignsUpdateParams.operations_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `updateMask: str`
    :   The type of the None singleton.

    ### Methods

    `update(...) ‑> airbyte_agent_sdk.connectors.google_ads.types.CampaignsUpdateParamsOperationsItemUpdate`
    :   D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
        If E is present and has a .keys() method, then does:  for k in E.keys(): D[k] = E[k]
        If E is present and lacks a .keys() method, then does:  for k, v in E: D[k] = v
        In either case, this is followed by: for k in F:  D[k] = F[k]

<a id="CampaignsUpdateParamsOperationsItemUpdate"></a>

`CampaignsUpdateParamsOperationsItemUpdate(*args, **kwargs)`
:   Campaign fields to update

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

    `resourceName: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

<a id="LabelsCreateParams"></a>

`LabelsCreateParams(*args, **kwargs)`
:   Parameters for labels.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.types.LabelsCreateParamsOperationsItem]`
    :   The type of the None singleton.

<a id="LabelsCreateParamsOperationsItem"></a>

`LabelsCreateParamsOperationsItem(*args, **kwargs)`
:   Nested schema for LabelsCreateParams.operations_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create: airbyte_agent_sdk.connectors.google_ads.types.LabelsCreateParamsOperationsItemCreate`
    :   The type of the None singleton.

<a id="LabelsCreateParamsOperationsItemCreate"></a>

`LabelsCreateParamsOperationsItemCreate(*args, **kwargs)`
:   Label to create

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `textLabel: airbyte_agent_sdk.connectors.google_ads.types.LabelsCreateParamsOperationsItemCreateTextlabel`
    :   The type of the None singleton.

<a id="LabelsCreateParamsOperationsItemCreateTextlabel"></a>

`LabelsCreateParamsOperationsItemCreateTextlabel(*args, **kwargs)`
:   Text label styling

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `backgroundColor: str`
    :   The type of the None singleton.

    `description: str`
    :   The type of the None singleton.