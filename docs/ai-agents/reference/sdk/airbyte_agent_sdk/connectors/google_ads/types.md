---
id: airbyte_agent_sdk-connectors-google_ads-types
title: airbyte_agent_sdk.connectors.google_ads.types
---

Module airbyte_agent_sdk.connectors.google_ads.types
====================================================
Type definitions for google-ads connector.

Classes
-------

`AccessibleCustomersListParams(*args, **kwargs)`
:   Parameters for accessible_customers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

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

`AccountsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_ads.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

`AccountsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_ads.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_ads.types.AccountsStringFilter`
    :   The type of the None singleton.

`AccountsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_ads.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_ads.types.AccountsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.google_ads.types.AccountsInFilter`
    :   The type of the None singleton.

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

`AccountsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_ads.types.AccountsStringFilter`
    :   The type of the None singleton.

`AccountsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_ads.types.AccountsStringFilter`
    :   The type of the None singleton.

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

`AccountsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_ads.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_ads.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_ads.types.AccountsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.google_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.google_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsAnyCondition]`
    :   The type of the None singleton.

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

`AccountsSearchQuery(*args, **kwargs)`
:   Search query for accounts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_ads.types.AccountsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AccountsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_ads.types.AccountsSortFilter]`
    :   The type of the None singleton.

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

`AdGroupAdLabelsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsAnyValueFilter`
    :   The type of the None singleton.

`AdGroupAdLabelsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsSearchFilter`
    :   The type of the None singleton.

`AdGroupAdLabelsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsStringFilter`
    :   The type of the None singleton.

`AdGroupAdLabelsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsSearchFilter`
    :   The type of the None singleton.

`AdGroupAdLabelsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsSearchFilter`
    :   The type of the None singleton.

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

`AdGroupAdLabelsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsStringFilter`
    :   The type of the None singleton.

`AdGroupAdLabelsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsStringFilter`
    :   The type of the None singleton.

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

`AdGroupAdLabelsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsSearchFilter`
    :   The type of the None singleton.

`AdGroupAdLabelsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsSearchFilter`
    :   The type of the None singleton.

`AdGroupAdLabelsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsSearchFilter`
    :   The type of the None singleton.

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

`AdGroupAdLabelsSearchQuery(*args, **kwargs)`
:   Search query for ad_group_ad_labels entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdLabelsSortFilter]`
    :   The type of the None singleton.

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

`AdGroupAdsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsAnyValueFilter`
    :   The type of the None singleton.

`AdGroupAdsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsSearchFilter`
    :   The type of the None singleton.

`AdGroupAdsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsStringFilter`
    :   The type of the None singleton.

`AdGroupAdsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsSearchFilter`
    :   The type of the None singleton.

`AdGroupAdsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsSearchFilter`
    :   The type of the None singleton.

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

`AdGroupAdsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsStringFilter`
    :   The type of the None singleton.

`AdGroupAdsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsStringFilter`
    :   The type of the None singleton.

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

`AdGroupAdsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsSearchFilter`
    :   The type of the None singleton.

`AdGroupAdsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsSearchFilter`
    :   The type of the None singleton.

`AdGroupAdsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsSearchFilter`
    :   The type of the None singleton.

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

`AdGroupAdsSearchQuery(*args, **kwargs)`
:   Search query for ad_group_ads entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupAdsSortFilter]`
    :   The type of the None singleton.

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

`AdGroupLabelsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsAnyValueFilter`
    :   The type of the None singleton.

`AdGroupLabelsCreateParams(*args, **kwargs)`
:   Parameters for ad_group_labels.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsCreateParamsOperationsItem]`
    :   The type of the None singleton.

`AdGroupLabelsCreateParamsOperationsItem(*args, **kwargs)`
:   Nested schema for AdGroupLabelsCreateParams.operations_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsCreateParamsOperationsItemCreate`
    :   The type of the None singleton.

`AdGroupLabelsCreateParamsOperationsItemCreate(*args, **kwargs)`
:   Ad group label association to create

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adGroup: str`
    :   The type of the None singleton.

    `label: str`
    :   The type of the None singleton.

`AdGroupLabelsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsSearchFilter`
    :   The type of the None singleton.

`AdGroupLabelsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsStringFilter`
    :   The type of the None singleton.

`AdGroupLabelsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsSearchFilter`
    :   The type of the None singleton.

`AdGroupLabelsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsSearchFilter`
    :   The type of the None singleton.

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

`AdGroupLabelsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsStringFilter`
    :   The type of the None singleton.

`AdGroupLabelsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsStringFilter`
    :   The type of the None singleton.

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

`AdGroupLabelsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsSearchFilter`
    :   The type of the None singleton.

`AdGroupLabelsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsSearchFilter`
    :   The type of the None singleton.

`AdGroupLabelsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsSearchFilter`
    :   The type of the None singleton.

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

`AdGroupLabelsSearchQuery(*args, **kwargs)`
:   Search query for ad_group_labels entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupLabelsSortFilter]`
    :   The type of the None singleton.

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

`AdGroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAnyValueFilter`
    :   The type of the None singleton.

`AdGroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsStringFilter`
    :   The type of the None singleton.

`AdGroupsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsInFilter`
    :   The type of the None singleton.

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

`AdGroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsStringFilter`
    :   The type of the None singleton.

`AdGroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsStringFilter`
    :   The type of the None singleton.

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

`AdGroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAnyCondition]`
    :   The type of the None singleton.

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

`AdGroupsSearchQuery(*args, **kwargs)`
:   Search query for ad_groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_ads.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.AdGroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupsSortFilter]`
    :   The type of the None singleton.

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

`AdGroupsUpdateParams(*args, **kwargs)`
:   Parameters for ad_groups.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.types.AdGroupsUpdateParamsOperationsItem]`
    :   The type of the None singleton.

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

`CampaignLabelsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsAnyValueFilter`
    :   The type of the None singleton.

`CampaignLabelsCreateParams(*args, **kwargs)`
:   Parameters for campaign_labels.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsCreateParamsOperationsItem]`
    :   The type of the None singleton.

`CampaignLabelsCreateParamsOperationsItem(*args, **kwargs)`
:   Nested schema for CampaignLabelsCreateParams.operations_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsCreateParamsOperationsItemCreate`
    :   The type of the None singleton.

`CampaignLabelsCreateParamsOperationsItemCreate(*args, **kwargs)`
:   Campaign label association to create

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign: str`
    :   The type of the None singleton.

    `label: str`
    :   The type of the None singleton.

`CampaignLabelsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsSearchFilter`
    :   The type of the None singleton.

`CampaignLabelsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsStringFilter`
    :   The type of the None singleton.

`CampaignLabelsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsSearchFilter`
    :   The type of the None singleton.

`CampaignLabelsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsSearchFilter`
    :   The type of the None singleton.

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

`CampaignLabelsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsStringFilter`
    :   The type of the None singleton.

`CampaignLabelsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsStringFilter`
    :   The type of the None singleton.

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

`CampaignLabelsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsSearchFilter`
    :   The type of the None singleton.

`CampaignLabelsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsSearchFilter`
    :   The type of the None singleton.

`CampaignLabelsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsSearchFilter`
    :   The type of the None singleton.

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

`CampaignLabelsSearchQuery(*args, **kwargs)`
:   Search query for campaign_labels entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsInCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_ads.types.CampaignLabelsSortFilter]`
    :   The type of the None singleton.

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

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_ads.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_ads.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_ads.types.CampaignsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.google_ads.types.CampaignsInFilter`
    :   The type of the None singleton.

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

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_ads.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_ads.types.CampaignsStringFilter`
    :   The type of the None singleton.

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

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_ads.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_ads.types.CampaignsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.google_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.google_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

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

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_ads.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsInCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.google_ads.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_ads.types.CampaignsSortFilter]`
    :   The type of the None singleton.

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

`CampaignsUpdateParams(*args, **kwargs)`
:   Parameters for campaigns.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.types.CampaignsUpdateParamsOperationsItem]`
    :   The type of the None singleton.

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

`LabelsCreateParams(*args, **kwargs)`
:   Parameters for labels.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.types.LabelsCreateParamsOperationsItem]`
    :   The type of the None singleton.

`LabelsCreateParamsOperationsItem(*args, **kwargs)`
:   Nested schema for LabelsCreateParams.operations_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create: airbyte_agent_sdk.connectors.google_ads.types.LabelsCreateParamsOperationsItemCreate`
    :   The type of the None singleton.

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

`LabelsCreateParamsOperationsItemCreateTextlabel(*args, **kwargs)`
:   Text label styling

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `backgroundColor: str`
    :   The type of the None singleton.

    `description: str`
    :   The type of the None singleton.