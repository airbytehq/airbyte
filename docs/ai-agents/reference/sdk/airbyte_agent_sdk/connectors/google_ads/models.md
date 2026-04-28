---
id: airbyte_agent_sdk-connectors-google_ads-models
title: airbyte_agent_sdk.connectors.google_ads.models
---

Module airbyte_agent_sdk.connectors.google_ads.models
=====================================================
Pydantic models for google-ads connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="AccessibleCustomerResourceName"></a>

`AccessibleCustomerResourceName(**data: Any)`
:   Resource name of an accessible customer (e.g., customers/1234567890)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AccessibleCustomersList"></a>

`AccessibleCustomersList(**data: Any)`
:   List of accessible customer resource names
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `resource_names: list[airbyte_agent_sdk.connectors.google_ads.models.AccessibleCustomerResourceName] | Any`
    :   The type of the None singleton.

<a id="Account"></a>

`Account(**data: Any)`
:   Google Ads customer account
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `customer: airbyte_agent_sdk.connectors.google_ads.models.AccountCustomer | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AccountCustomer"></a>

`AccountCustomer(**data: Any)`
:   Nested schema for Account.customer
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auto_tagging_enabled: bool | Any`
    :   Whether auto-tagging is enabled

    `call_reporting_setting: airbyte_agent_sdk.connectors.google_ads.models.AccountCustomerCallreportingsetting | Any`
    :   The type of the None singleton.

    `conversion_tracking_setting: airbyte_agent_sdk.connectors.google_ads.models.AccountCustomerConversiontrackingsetting | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   Currency code (e.g., USD)

    `descriptive_name: str | Any`
    :   Account descriptive name

    `final_url_suffix: str | Any`
    :   The type of the None singleton.

    `has_partners_badge: bool | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   Customer ID

    `manager: bool | Any`
    :   Whether this is a manager account

    `model_config`
    :   The type of the None singleton.

    `optimization_score: float | Any`
    :   The type of the None singleton.

    `optimization_score_weight: float | Any`
    :   The type of the None singleton.

    `pay_per_conversion_eligibility_failure_reasons: list[str] | Any`
    :   The type of the None singleton.

    `remarketing_setting: airbyte_agent_sdk.connectors.google_ads.models.AccountCustomerRemarketingsetting | Any`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   Resource name of the customer

    `test_account: bool | Any`
    :   The type of the None singleton.

    `time_zone: str | Any`
    :   The type of the None singleton.

    `tracking_url_template: str | Any`
    :   The type of the None singleton.

<a id="AccountCustomerCallreportingsetting"></a>

`AccountCustomerCallreportingsetting(**data: Any)`
:   Nested schema for AccountCustomer.callReportingSetting
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `call_conversion_action: str | Any`
    :   The type of the None singleton.

    `call_conversion_reporting_enabled: bool | Any`
    :   The type of the None singleton.

    `call_reporting_enabled: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AccountCustomerConversiontrackingsetting"></a>

`AccountCustomerConversiontrackingsetting(**data: Any)`
:   Nested schema for AccountCustomer.conversionTrackingSetting
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `conversion_tracking_id: str | Any`
    :   The type of the None singleton.

    `cross_account_conversion_tracking_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AccountCustomerRemarketingsetting"></a>

`AccountCustomerRemarketingsetting(**data: Any)`
:   Nested schema for AccountCustomer.remarketingSetting
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `google_global_site_tag: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AccountSearchResponse"></a>

`AccountSearchResponse(**data: Any)`
:   Search response containing account data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_mask: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any`
    :   The type of the None singleton.

    `query_resource_consumption: str | Any`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.google_ads.models.Account] | Any`
    :   The type of the None singleton.

<a id="AccountsListResultMeta"></a>

`AccountsListResultMeta(**data: Any)`
:   Metadata for accounts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any`
    :   The type of the None singleton.

<a id="AccountsSearchData"></a>

`AccountsSearchData(**data: Any)`
:   Search result data for accounts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

    `segments_date: str | None`
    :   Date segment for the report row

<a id="AdGroup"></a>

`AdGroup(**data: Any)`
:   Google Ads ad group
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_group: airbyte_agent_sdk.connectors.google_ads.models.AdGroupAdgroup | Any`
    :   The type of the None singleton.

    `campaign: airbyte_agent_sdk.connectors.google_ads.models.AdGroupCampaign | Any`
    :   The type of the None singleton.

    `metrics: airbyte_agent_sdk.connectors.google_ads.models.AdGroupMetrics | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `segments: airbyte_agent_sdk.connectors.google_ads.models.AdGroupSegments | Any`
    :   The type of the None singleton.

<a id="AdGroupAd"></a>

`AdGroupAd(**data: Any)`
:   Google Ads ad group ad
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_group: airbyte_agent_sdk.connectors.google_ads.models.AdGroupAdAdgroup | Any`
    :   The type of the None singleton.

    `ad_group_ad: airbyte_agent_sdk.connectors.google_ads.models.AdGroupAdAdgroupad | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `segments: airbyte_agent_sdk.connectors.google_ads.models.AdGroupAdSegments | Any`
    :   The type of the None singleton.

<a id="AdGroupAdAdgroup"></a>

`AdGroupAdAdgroup(**data: Any)`
:   Nested schema for AdGroupAd.adGroup
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   Parent ad group ID

    `model_config`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   Parent ad group resource name

<a id="AdGroupAdAdgroupad"></a>

`AdGroupAdAdgroupad(**data: Any)`
:   Nested schema for AdGroupAd.adGroupAd
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad: airbyte_agent_sdk.connectors.google_ads.models.AdGroupAdAdgroupadAd | Any`
    :   The type of the None singleton.

    `ad_group: str | Any`
    :   The type of the None singleton.

    `ad_strength: str | Any`
    :   The type of the None singleton.

    `labels: list[str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `policy_summary: airbyte_agent_sdk.connectors.google_ads.models.AdGroupAdAdgroupadPolicysummary | Any`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

<a id="AdGroupAdAdgroupadAd"></a>

`AdGroupAdAdgroupadAd(**data: Any)`
:   Nested schema for AdGroupAdAdgroupad.ad
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `display_url: str | Any`
    :   The type of the None singleton.

    `final_mobile_urls: list[str] | Any`
    :   The type of the None singleton.

    `final_url_suffix: str | Any`
    :   The type of the None singleton.

    `final_urls: list[str] | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   Ad ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   The type of the None singleton.

    `tracking_url_template: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="AdGroupAdAdgroupadPolicysummary"></a>

`AdGroupAdAdgroupadPolicysummary(**data: Any)`
:   Nested schema for AdGroupAdAdgroupad.policySummary
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `approval_status: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `review_status: str | Any`
    :   The type of the None singleton.

<a id="AdGroupAdLabel"></a>

`AdGroupAdLabel(**data: Any)`
:   Ad group ad label association
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_group_ad: airbyte_agent_sdk.connectors.google_ads.models.AdGroupAdLabelAdgroupad | Any`
    :   The type of the None singleton.

    `ad_group_ad_label: airbyte_agent_sdk.connectors.google_ads.models.AdGroupAdLabelAdgroupadlabel | Any`
    :   The type of the None singleton.

    `label: airbyte_agent_sdk.connectors.google_ads.models.AdGroupAdLabelLabel | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupAdLabelAdgroupad"></a>

`AdGroupAdLabelAdgroupad(**data: Any)`
:   Nested schema for AdGroupAdLabel.adGroupAd
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad: airbyte_agent_sdk.connectors.google_ads.models.AdGroupAdLabelAdgroupadAd | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupAdLabelAdgroupadAd"></a>

`AdGroupAdLabelAdgroupadAd(**data: Any)`
:   Nested schema for AdGroupAdLabelAdgroupad.ad
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupAdLabelAdgroupadlabel"></a>

`AdGroupAdLabelAdgroupadlabel(**data: Any)`
:   Nested schema for AdGroupAdLabel.adGroupAdLabel
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_group_ad: str | Any`
    :   The type of the None singleton.

    `label: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   The type of the None singleton.

<a id="AdGroupAdLabelLabel"></a>

`AdGroupAdLabelLabel(**data: Any)`
:   Nested schema for AdGroupAdLabel.label
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   The type of the None singleton.

<a id="AdGroupAdLabelSearchResponse"></a>

`AdGroupAdLabelSearchResponse(**data: Any)`
:   Search response containing ad group ad label data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_mask: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any`
    :   The type of the None singleton.

    `query_resource_consumption: str | Any`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.google_ads.models.AdGroupAdLabel] | Any`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsListResultMeta"></a>

`AdGroupAdLabelsListResultMeta(**data: Any)`
:   Metadata for ad_group_ad_labels.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsSearchData"></a>

`AdGroupAdLabelsSearchData(**data: Any)`
:   Search result data for ad_group_ad_labels entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupAdSearchResponse"></a>

`AdGroupAdSearchResponse(**data: Any)`
:   Search response containing ad group ad data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_mask: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any`
    :   The type of the None singleton.

    `query_resource_consumption: str | Any`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.google_ads.models.AdGroupAd] | Any`
    :   The type of the None singleton.

<a id="AdGroupAdSegments"></a>

`AdGroupAdSegments(**data: Any)`
:   Nested schema for AdGroupAd.segments
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupAdgroup"></a>

`AdGroupAdgroup(**data: Any)`
:   Nested schema for AdGroup.adGroup
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_rotation_mode: str | Any`
    :   The type of the None singleton.

    `base_ad_group: str | Any`
    :   The type of the None singleton.

    `campaign: str | Any`
    :   Parent campaign resource name

    `cpc_bid_micros: str | Any`
    :   The type of the None singleton.

    `cpm_bid_micros: str | Any`
    :   The type of the None singleton.

    `cpv_bid_micros: str | Any`
    :   The type of the None singleton.

    `effective_target_cpa_micros: str | Any`
    :   The type of the None singleton.

    `effective_target_cpa_source: str | Any`
    :   The type of the None singleton.

    `effective_target_roas: float | Any`
    :   The type of the None singleton.

    `effective_target_roas_source: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   Ad group ID

    `labels: list[str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Ad group name

    `resource_name: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `target_cpa_micros: str | Any`
    :   The type of the None singleton.

    `target_roas: float | Any`
    :   The type of the None singleton.

    `tracking_url_template: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="AdGroupAdsListResultMeta"></a>

`AdGroupAdsListResultMeta(**data: Any)`
:   Metadata for ad_group_ads.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any`
    :   The type of the None singleton.

<a id="AdGroupAdsSearchData"></a>

`AdGroupAdsSearchData(**data: Any)`
:   Search result data for ad_group_ads entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

    `segments_date: str | None`
    :   Date segment for the report row

<a id="AdGroupCampaign"></a>

`AdGroupCampaign(**data: Any)`
:   Nested schema for AdGroup.campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   Parent campaign ID

    `model_config`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   Parent campaign resource name

<a id="AdGroupLabel"></a>

`AdGroupLabel(**data: Any)`
:   Ad group label association
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_group: airbyte_agent_sdk.connectors.google_ads.models.AdGroupLabelAdgroup | Any`
    :   The type of the None singleton.

    `ad_group_label: airbyte_agent_sdk.connectors.google_ads.models.AdGroupLabelAdgrouplabel | Any`
    :   The type of the None singleton.

    `label: airbyte_agent_sdk.connectors.google_ads.models.AdGroupLabelLabel | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupLabelAdgroup"></a>

`AdGroupLabelAdgroup(**data: Any)`
:   Nested schema for AdGroupLabel.adGroup
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupLabelAdgrouplabel"></a>

`AdGroupLabelAdgrouplabel(**data: Any)`
:   Nested schema for AdGroupLabel.adGroupLabel
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_group: str | Any`
    :   The type of the None singleton.

    `label: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   The type of the None singleton.

<a id="AdGroupLabelLabel"></a>

`AdGroupLabelLabel(**data: Any)`
:   Nested schema for AdGroupLabel.label
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   The type of the None singleton.

<a id="AdGroupLabelMutateRequest"></a>

`AdGroupLabelMutateRequest(**data: Any)`
:   Request to create ad group-label associations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.models.AdGroupLabelMutateRequestOperationsItem] | Any`
    :   The type of the None singleton.

<a id="AdGroupLabelMutateRequestOperationsItem"></a>

`AdGroupLabelMutateRequestOperationsItem(**data: Any)`
:   Nested schema for AdGroupLabelMutateRequest.operations_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create: airbyte_agent_sdk.connectors.google_ads.models.AdGroupLabelMutateRequestOperationsItemCreate | Any`
    :   Ad group label association to create

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupLabelMutateRequestOperationsItemCreate"></a>

`AdGroupLabelMutateRequestOperationsItemCreate(**data: Any)`
:   Ad group label association to create
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_group: str | Any`
    :   Resource name of the ad group (e.g., customers/1234567890/adGroups/111222333)

    `label: str | Any`
    :   Resource name of the label (e.g., customers/1234567890/labels/444555666)

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupLabelMutateResponse"></a>

`AdGroupLabelMutateResponse(**data: Any)`
:   Response from ad group label mutate operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.google_ads.models.AdGroupLabelMutateResponseResultsItem] | Any`
    :   The type of the None singleton.

<a id="AdGroupLabelMutateResponseResultsItem"></a>

`AdGroupLabelMutateResponseResultsItem(**data: Any)`
:   Nested schema for AdGroupLabelMutateResponse.results_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   Resource name of the created ad group label association

<a id="AdGroupLabelSearchResponse"></a>

`AdGroupLabelSearchResponse(**data: Any)`
:   Search response containing ad group label data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_mask: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any`
    :   The type of the None singleton.

    `query_resource_consumption: str | Any`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.google_ads.models.AdGroupLabel] | Any`
    :   The type of the None singleton.

<a id="AdGroupLabelsListResultMeta"></a>

`AdGroupLabelsListResultMeta(**data: Any)`
:   Metadata for ad_group_labels.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any`
    :   The type of the None singleton.

<a id="AdGroupLabelsSearchData"></a>

`AdGroupLabelsSearchData(**data: Any)`
:   Search result data for ad_group_labels entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupMetrics"></a>

`AdGroupMetrics(**data: Any)`
:   Nested schema for AdGroup.metrics
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cost_micros: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupMutateRequest"></a>

`AdGroupMutateRequest(**data: Any)`
:   Request to mutate (update) ad groups
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.models.AdGroupMutateRequestOperationsItem] | Any`
    :   The type of the None singleton.

<a id="AdGroupMutateRequestOperationsItem"></a>

`AdGroupMutateRequestOperationsItem(**data: Any)`
:   Nested schema for AdGroupMutateRequest.operations_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `update: airbyte_agent_sdk.connectors.google_ads.models.AdGroupMutateRequestOperationsItemUpdate | Any`
    :   Ad group fields to update

    `update_mask: str | Any`
    :   Comma-separated list of field paths to update (e.g., name,status,cpcBidMicros)

<a id="AdGroupMutateRequestOperationsItemUpdate"></a>

`AdGroupMutateRequestOperationsItemUpdate(**data: Any)`
:   Ad group fields to update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cpc_bid_micros: str | Any`
    :   CPC bid amount in micros (1,000,000 micros = 1 currency unit)

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   New ad group name

    `resource_name: str | Any`
    :   Resource name of the ad group to update (e.g., customers/1234567890/adGroups/111222333)

    `status: str | Any`
    :   Ad group status (ENABLED or PAUSED)

<a id="AdGroupMutateResponse"></a>

`AdGroupMutateResponse(**data: Any)`
:   Response from ad group mutate operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.google_ads.models.AdGroupMutateResponseResultsItem] | Any`
    :   The type of the None singleton.

<a id="AdGroupMutateResponseResultsItem"></a>

`AdGroupMutateResponseResultsItem(**data: Any)`
:   Nested schema for AdGroupMutateResponse.results_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   Resource name of the mutated ad group

<a id="AdGroupSearchResponse"></a>

`AdGroupSearchResponse(**data: Any)`
:   Search response containing ad group data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_mask: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any`
    :   The type of the None singleton.

    `query_resource_consumption: str | Any`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.google_ads.models.AdGroup] | Any`
    :   The type of the None singleton.

<a id="AdGroupSegments"></a>

`AdGroupSegments(**data: Any)`
:   Nested schema for AdGroup.segments
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupsListResultMeta"></a>

`AdGroupsListResultMeta(**data: Any)`
:   Metadata for ad_groups.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any`
    :   The type of the None singleton.

<a id="AdGroupsSearchData"></a>

`AdGroupsSearchData(**data: Any)`
:   Search result data for ad_groups entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

    `segments_date: str | None`
    :   Date segment for the report row

<a id="AirbyteSearchMeta"></a>

`AirbyteSearchMeta(**data: Any)`
:   Pagination metadata for search responses.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   Cursor for fetching the next page of results.

    `has_more: bool`
    :   Whether more results are available.

    `model_config`
    :   The type of the None singleton.

    `took_ms: int | None`
    :   Time taken to execute the search in milliseconds.

<a id="AirbyteSearchResult"></a>

`AirbyteSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult[AccountsSearchData]
    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult[AdGroupAdLabelsSearchData]
    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult[AdGroupAdsSearchData]
    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult[AdGroupLabelsSearchData]
    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult[AdGroupsSearchData]
    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult[CampaignLabelsSearchData]
    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult[CampaignsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AccountsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AccountsSearchResult"></a>

`AccountsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdGroupAdLabelsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsSearchResult"></a>

`AdGroupAdLabelsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdGroupAdsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupAdsSearchResult"></a>

`AdGroupAdsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdGroupLabelsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupLabelsSearchResult"></a>

`AdGroupLabelsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdGroupsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupsSearchResult"></a>

`AdGroupsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CampaignLabelsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignLabelsSearchResult"></a>

`CampaignLabelsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CampaignsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsSearchResult"></a>

`CampaignsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Campaign"></a>

`Campaign(**data: Any)`
:   Google Ads campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `campaign: airbyte_agent_sdk.connectors.google_ads.models.CampaignCampaign | Any`
    :   The type of the None singleton.

    `campaign_budget: airbyte_agent_sdk.connectors.google_ads.models.CampaignCampaignbudget | Any`
    :   The type of the None singleton.

    `metrics: airbyte_agent_sdk.connectors.google_ads.models.CampaignMetrics | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `segments: airbyte_agent_sdk.connectors.google_ads.models.CampaignSegments | Any`
    :   The type of the None singleton.

<a id="CampaignCampaign"></a>

`CampaignCampaign(**data: Any)`
:   Nested schema for Campaign.campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `advertising_channel_sub_type: str | Any`
    :   The type of the None singleton.

    `advertising_channel_type: str | Any`
    :   Primary channel type

    `bidding_strategy: str | Any`
    :   The type of the None singleton.

    `bidding_strategy_type: str | Any`
    :   The type of the None singleton.

    `campaign_budget: str | Any`
    :   Campaign budget resource name

    `end_date: str | Any`
    :   Campaign end date

    `id: str | Any`
    :   Campaign ID

    `labels: list[str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Campaign name

    `network_settings: airbyte_agent_sdk.connectors.google_ads.models.CampaignCampaignNetworksettings | Any`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   The type of the None singleton.

    `serving_status: str | Any`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   Campaign start date

    `status: str | Any`
    :   Campaign status

<a id="CampaignCampaignNetworksettings"></a>

`CampaignCampaignNetworksettings(**data: Any)`
:   Nested schema for CampaignCampaign.networkSettings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `target_content_network: bool | Any`
    :   The type of the None singleton.

    `target_google_search: bool | Any`
    :   The type of the None singleton.

    `target_partner_search_network: bool | Any`
    :   The type of the None singleton.

    `target_search_network: bool | Any`
    :   The type of the None singleton.

<a id="CampaignCampaignbudget"></a>

`CampaignCampaignbudget(**data: Any)`
:   Nested schema for Campaign.campaignBudget
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount_micros: str | Any`
    :   Budget amount in micros

    `model_config`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   Resource name of the campaign budget

<a id="CampaignLabel"></a>

`CampaignLabel(**data: Any)`
:   Campaign label association
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `campaign: airbyte_agent_sdk.connectors.google_ads.models.CampaignLabelCampaign | Any`
    :   The type of the None singleton.

    `campaign_label: airbyte_agent_sdk.connectors.google_ads.models.CampaignLabelCampaignlabel | Any`
    :   The type of the None singleton.

    `label: airbyte_agent_sdk.connectors.google_ads.models.CampaignLabelLabel | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignLabelCampaign"></a>

`CampaignLabelCampaign(**data: Any)`
:   Nested schema for CampaignLabel.campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignLabelCampaignlabel"></a>

`CampaignLabelCampaignlabel(**data: Any)`
:   Nested schema for CampaignLabel.campaignLabel
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `campaign: str | Any`
    :   The type of the None singleton.

    `label: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   The type of the None singleton.

<a id="CampaignLabelLabel"></a>

`CampaignLabelLabel(**data: Any)`
:   Nested schema for CampaignLabel.label
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   The type of the None singleton.

<a id="CampaignLabelMutateRequest"></a>

`CampaignLabelMutateRequest(**data: Any)`
:   Request to create campaign-label associations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.models.CampaignLabelMutateRequestOperationsItem] | Any`
    :   The type of the None singleton.

<a id="CampaignLabelMutateRequestOperationsItem"></a>

`CampaignLabelMutateRequestOperationsItem(**data: Any)`
:   Nested schema for CampaignLabelMutateRequest.operations_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create: airbyte_agent_sdk.connectors.google_ads.models.CampaignLabelMutateRequestOperationsItemCreate | Any`
    :   Campaign label association to create

    `model_config`
    :   The type of the None singleton.

<a id="CampaignLabelMutateRequestOperationsItemCreate"></a>

`CampaignLabelMutateRequestOperationsItemCreate(**data: Any)`
:   Campaign label association to create
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `campaign: str | Any`
    :   Resource name of the campaign (e.g., customers/1234567890/campaigns/111222333)

    `label: str | Any`
    :   Resource name of the label (e.g., customers/1234567890/labels/444555666)

    `model_config`
    :   The type of the None singleton.

<a id="CampaignLabelMutateResponse"></a>

`CampaignLabelMutateResponse(**data: Any)`
:   Response from campaign label mutate operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.google_ads.models.CampaignLabelMutateResponseResultsItem] | Any`
    :   The type of the None singleton.

<a id="CampaignLabelMutateResponseResultsItem"></a>

`CampaignLabelMutateResponseResultsItem(**data: Any)`
:   Nested schema for CampaignLabelMutateResponse.results_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   Resource name of the created campaign label association

<a id="CampaignLabelSearchResponse"></a>

`CampaignLabelSearchResponse(**data: Any)`
:   Search response containing campaign label data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_mask: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any`
    :   The type of the None singleton.

    `query_resource_consumption: str | Any`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.google_ads.models.CampaignLabel] | Any`
    :   The type of the None singleton.

<a id="CampaignLabelsListResultMeta"></a>

`CampaignLabelsListResultMeta(**data: Any)`
:   Metadata for campaign_labels.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any`
    :   The type of the None singleton.

<a id="CampaignLabelsSearchData"></a>

`CampaignLabelsSearchData(**data: Any)`
:   Search result data for campaign_labels entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

<a id="CampaignMetrics"></a>

`CampaignMetrics(**data: Any)`
:   Nested schema for Campaign.metrics
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `average_cpc: float | Any`
    :   The type of the None singleton.

    `average_cpm: float | Any`
    :   The type of the None singleton.

    `clicks: str | Any`
    :   The type of the None singleton.

    `conversions: float | Any`
    :   The type of the None singleton.

    `conversions_value: float | Any`
    :   The type of the None singleton.

    `cost_micros: str | Any`
    :   The type of the None singleton.

    `ctr: float | Any`
    :   The type of the None singleton.

    `impressions: str | Any`
    :   The type of the None singleton.

    `interactions: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignMutateRequest"></a>

`CampaignMutateRequest(**data: Any)`
:   Request to mutate (update) campaigns
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.models.CampaignMutateRequestOperationsItem] | Any`
    :   The type of the None singleton.

<a id="CampaignMutateRequestOperationsItem"></a>

`CampaignMutateRequestOperationsItem(**data: Any)`
:   Nested schema for CampaignMutateRequest.operations_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `update: airbyte_agent_sdk.connectors.google_ads.models.CampaignMutateRequestOperationsItemUpdate | Any`
    :   Campaign fields to update

    `update_mask: str | Any`
    :   Comma-separated list of field paths to update (e.g., name,status)

<a id="CampaignMutateRequestOperationsItemUpdate"></a>

`CampaignMutateRequestOperationsItemUpdate(**data: Any)`
:   Campaign fields to update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   New campaign name

    `resource_name: str | Any`
    :   Resource name of the campaign to update (e.g., customers/1234567890/campaigns/111222333)

    `status: str | Any`
    :   Campaign status (ENABLED or PAUSED)

<a id="CampaignMutateResponse"></a>

`CampaignMutateResponse(**data: Any)`
:   Response from campaign mutate operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.google_ads.models.CampaignMutateResponseResultsItem] | Any`
    :   The type of the None singleton.

<a id="CampaignMutateResponseResultsItem"></a>

`CampaignMutateResponseResultsItem(**data: Any)`
:   Nested schema for CampaignMutateResponse.results_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   Resource name of the mutated campaign

<a id="CampaignSearchResponse"></a>

`CampaignSearchResponse(**data: Any)`
:   Search response containing campaign data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_mask: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any`
    :   The type of the None singleton.

    `query_resource_consumption: str | Any`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.google_ads.models.Campaign] | Any`
    :   The type of the None singleton.

<a id="CampaignSegments"></a>

`CampaignSegments(**data: Any)`
:   Nested schema for Campaign.segments
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date: str | Any`
    :   Date in YYYY-MM-DD format

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsListResultMeta"></a>

`CampaignsListResultMeta(**data: Any)`
:   Metadata for campaigns.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any`
    :   The type of the None singleton.

<a id="CampaignsSearchData"></a>

`CampaignsSearchData(**data: Any)`
:   Search result data for campaigns entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

    `segments_ad_network_type: str | None`
    :   Ad network type segment

    `segments_date: str | None`
    :   Date segment for the report row

    `segments_hour: int | None`
    :   Hour segment

<a id="GoogleAdsAuthConfig"></a>

`GoogleAdsAuthConfig(**data: Any)`
:   OAuth2 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   OAuth2 client ID from Google Cloud Console

    `client_secret: str`
    :   OAuth2 client secret from Google Cloud Console

    `developer_token: str`
    :   Google Ads API developer token

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   OAuth2 refresh token

<a id="GoogleAdsCheckResult"></a>

`GoogleAdsCheckResult(**data: Any)`
:   Result of a health check operation.
    
    Returned by the check() method to indicate connectivity and credential status.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checked_action: str | None`
    :   Action name used for the health check.

    `checked_entity: str | None`
    :   Entity name used for the health check.

    `error: str | None`
    :   Error message if status is 'unhealthy', None otherwise.

    `model_config`
    :   The type of the None singleton.

    `status: str`
    :   Health check status: 'healthy' or 'unhealthy'.

<a id="GoogleAdsExecuteResult"></a>

`GoogleAdsExecuteResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult[AccessibleCustomersList]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="GoogleAdsExecuteResultWithMeta"></a>

`GoogleAdsExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta[list[Account], AccountsListResultMeta]
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta[list[AdGroupAdLabel], AdGroupAdLabelsListResultMeta]
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta[list[AdGroupAd], AdGroupAdsListResultMeta]
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta[list[AdGroupLabel], AdGroupLabelsListResultMeta]
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta[list[AdGroup], AdGroupsListResultMeta]
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta[list[CampaignLabel], CampaignLabelsListResultMeta]
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`GoogleAdsExecuteResultWithMeta[list[Account], AccountsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AccountsListResult"></a>

`AccountsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleAdsExecuteResultWithMeta[list[AdGroupAdLabel], AdGroupAdLabelsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupAdLabelsListResult"></a>

`AdGroupAdLabelsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleAdsExecuteResultWithMeta[list[AdGroupAd], AdGroupAdsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupAdsListResult"></a>

`AdGroupAdsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleAdsExecuteResultWithMeta[list[AdGroupLabel], AdGroupLabelsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupLabelsListResult"></a>

`AdGroupLabelsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleAdsExecuteResultWithMeta[list[AdGroup], AdGroupsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupsListResult"></a>

`AdGroupsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleAdsExecuteResultWithMeta[list[CampaignLabel], CampaignLabelsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignLabelsListResult"></a>

`CampaignLabelsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleAdsExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsListResult"></a>

`CampaignsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleAdsExecuteResult[AccessibleCustomersList](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AccessibleCustomersListResult"></a>

`AccessibleCustomersListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GoogleAdsReplicationConfig"></a>

`GoogleAdsReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Google Ads.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `conversion_window_days: int | None`
    :   Number of days for the conversion attribution window. Default is 14.

    `customer_id: str`
    :   Comma-separated list of Google Ads customer IDs (10 digits each, no dashes).

    `model_config`
    :   The type of the None singleton.

    `start_date: str | None`
    :   UTC date in YYYY-MM-DD format from which to start replicating data. Defaults to 2 years ago if not specified.

<a id="LabelMutateRequest"></a>

`LabelMutateRequest(**data: Any)`
:   Request to create labels
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `operations: list[airbyte_agent_sdk.connectors.google_ads.models.LabelMutateRequestOperationsItem] | Any`
    :   The type of the None singleton.

<a id="LabelMutateRequestOperationsItem"></a>

`LabelMutateRequestOperationsItem(**data: Any)`
:   Nested schema for LabelMutateRequest.operations_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create: airbyte_agent_sdk.connectors.google_ads.models.LabelMutateRequestOperationsItemCreate | Any`
    :   Label to create

    `model_config`
    :   The type of the None singleton.

<a id="LabelMutateRequestOperationsItemCreate"></a>

`LabelMutateRequestOperationsItemCreate(**data: Any)`
:   Label to create
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | Any`
    :   Description for the label

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Name for the new label

    `text_label: airbyte_agent_sdk.connectors.google_ads.models.LabelMutateRequestOperationsItemCreateTextlabel | Any`
    :   Text label styling

<a id="LabelMutateRequestOperationsItemCreateTextlabel"></a>

`LabelMutateRequestOperationsItemCreateTextlabel(**data: Any)`
:   Text label styling
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `background_color: str | Any`
    :   Background color in hex format (e.g., #FF0000)

    `description: str | Any`
    :   Description of the text label

    `model_config`
    :   The type of the None singleton.

<a id="LabelMutateResponse"></a>

`LabelMutateResponse(**data: Any)`
:   Response from label mutate operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.google_ads.models.LabelMutateResponseResultsItem] | Any`
    :   The type of the None singleton.

<a id="LabelMutateResponseResultsItem"></a>

`LabelMutateResponseResultsItem(**data: Any)`
:   Nested schema for LabelMutateResponse.results_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `resource_name: str | Any`
    :   Resource name of the created label