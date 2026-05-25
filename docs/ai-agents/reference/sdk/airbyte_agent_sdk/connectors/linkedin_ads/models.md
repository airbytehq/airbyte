---
id: airbyte_agent_sdk-connectors-linkedin_ads-models
title: airbyte_agent_sdk.connectors.linkedin_ads.models
---

Module airbyte_agent_sdk.connectors.linkedin_ads.models
=======================================================
Pydantic models for linkedin-ads connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Account"></a>

`Account(**data: Any)`
:   LinkedIn ad account object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `change_audit_stamps: airbyte_agent_sdk.connectors.linkedin_ads.models.AccountChangeauditstamps | None`
    :   The type of the None singleton.

    `currency: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `notified_on_campaign_optimization: bool | None`
    :   The type of the None singleton.

    `notified_on_creative_approval: bool | None`
    :   The type of the None singleton.

    `notified_on_creative_rejection: bool | None`
    :   The type of the None singleton.

    `notified_on_end_of_campaign: bool | None`
    :   The type of the None singleton.

    `notified_on_new_features_enabled: bool | None`
    :   The type of the None singleton.

    `reference: str | None`
    :   The type of the None singleton.

    `serving_statuses: list[str] | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `test: bool | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `version: airbyte_agent_sdk.connectors.linkedin_ads.models.AccountVersion | None`
    :   The type of the None singleton.

<a id="AccountChangeauditstamps"></a>

`AccountChangeauditstamps(**data: Any)`
:   Creation and last modification audit stamps
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: airbyte_agent_sdk.connectors.linkedin_ads.models.AccountChangeauditstampsCreated | None`
    :   The type of the None singleton.

    `last_modified: airbyte_agent_sdk.connectors.linkedin_ads.models.AccountChangeauditstampsLastmodified | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AccountChangeauditstampsCreated"></a>

`AccountChangeauditstampsCreated(**data: Any)`
:   Nested schema for AccountChangeauditstamps.created
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actor: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `time: int | None`
    :   The type of the None singleton.

<a id="AccountChangeauditstampsLastmodified"></a>

`AccountChangeauditstampsLastmodified(**data: Any)`
:   Nested schema for AccountChangeauditstamps.lastModified
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actor: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `time: int | None`
    :   The type of the None singleton.

<a id="AccountUser"></a>

`AccountUser(**data: Any)`
:   LinkedIn ad account user object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str | None`
    :   The type of the None singleton.

    `change_audit_stamps: airbyte_agent_sdk.connectors.linkedin_ads.models.AccountUserChangeauditstamps | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `role: str | None`
    :   The type of the None singleton.

    `user: str | None`
    :   The type of the None singleton.

<a id="AccountUserChangeauditstamps"></a>

`AccountUserChangeauditstamps(**data: Any)`
:   Creation and last modification audit stamps
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: airbyte_agent_sdk.connectors.linkedin_ads.models.AccountUserChangeauditstampsCreated | None`
    :   The type of the None singleton.

    `last_modified: airbyte_agent_sdk.connectors.linkedin_ads.models.AccountUserChangeauditstampsLastmodified | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AccountUserChangeauditstampsCreated"></a>

`AccountUserChangeauditstampsCreated(**data: Any)`
:   Nested schema for AccountUserChangeauditstamps.created
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actor: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `time: int | None`
    :   The type of the None singleton.

<a id="AccountUserChangeauditstampsLastmodified"></a>

`AccountUserChangeauditstampsLastmodified(**data: Any)`
:   Nested schema for AccountUserChangeauditstamps.lastModified
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actor: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `time: int | None`
    :   The type of the None singleton.

<a id="AccountUsersList"></a>

`AccountUsersList(**data: Any)`
:   Paginated list of account users
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `elements: list[airbyte_agent_sdk.connectors.linkedin_ads.models.AccountUser] | None`
    :   The type of the None singleton.

    `metadata: airbyte_agent_sdk.connectors.linkedin_ads.models.AccountUsersListMetadata | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AccountUsersListMetadata"></a>

`AccountUsersListMetadata(**data: Any)`
:   Nested schema for AccountUsersList.metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="AccountUsersListResultMeta"></a>

`AccountUsersListResultMeta(**data: Any)`
:   Metadata for account_users.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="AccountUsersSearchData"></a>

`AccountUsersSearchData(**data: Any)`
:   Search result data for account_users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str | None`
    :   Associated account URN

    `model_config`
    :   The type of the None singleton.

    `role: str | None`
    :   User role in the account

    `user: str | None`
    :   User URN

<a id="AccountVersion"></a>

`AccountVersion(**data: Any)`
:   Version information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `version_tag: str | None`
    :   The type of the None singleton.

<a id="AccountsList"></a>

`AccountsList(**data: Any)`
:   Paginated list of ad accounts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `elements: list[airbyte_agent_sdk.connectors.linkedin_ads.models.Account] | None`
    :   The type of the None singleton.

    `metadata: airbyte_agent_sdk.connectors.linkedin_ads.models.AccountsListMetadata | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AccountsListMetadata"></a>

`AccountsListMetadata(**data: Any)`
:   Nested schema for AccountsList.metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
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

    `next_page_token: str | None`
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

    `currency: str | None`
    :   Currency code used by the account

    `id: int | None`
    :   Unique account identifier

    `model_config`
    :   The type of the None singleton.

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

<a id="AdAnalyticsRecord"></a>

`AdAnalyticsRecord(**data: Any)`
:   Ad analytics data record with performance metrics
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action_clicks: int | None`
    :   The type of the None singleton.

    `ad_unit_clicks: int | None`
    :   The type of the None singleton.

    `approximate_member_reach: int | None`
    :   The type of the None singleton.

    `card_clicks: int | None`
    :   The type of the None singleton.

    `card_impressions: int | None`
    :   The type of the None singleton.

    `clicks: int | None`
    :   The type of the None singleton.

    `comment_likes: int | None`
    :   The type of the None singleton.

    `comments: int | None`
    :   The type of the None singleton.

    `company_page_clicks: int | None`
    :   The type of the None singleton.

    `conversion_value_in_local_currency: str | None`
    :   The type of the None singleton.

    `cost_in_local_currency: str | None`
    :   The type of the None singleton.

    `cost_in_usd: str | None`
    :   The type of the None singleton.

    `date_range: airbyte_agent_sdk.connectors.linkedin_ads.models.AdAnalyticsRecordDaterange | None`
    :   The type of the None singleton.

    `document_completions: int | None`
    :   The type of the None singleton.

    `document_first_quartile_completions: int | None`
    :   The type of the None singleton.

    `document_midpoint_completions: int | None`
    :   The type of the None singleton.

    `document_third_quartile_completions: int | None`
    :   The type of the None singleton.

    `download_clicks: int | None`
    :   The type of the None singleton.

    `external_website_conversions: int | None`
    :   The type of the None singleton.

    `external_website_post_click_conversions: int | None`
    :   The type of the None singleton.

    `external_website_post_view_conversions: int | None`
    :   The type of the None singleton.

    `follows: int | None`
    :   The type of the None singleton.

    `full_screen_plays: int | None`
    :   The type of the None singleton.

    `impressions: int | None`
    :   The type of the None singleton.

    `job_applications: int | None`
    :   The type of the None singleton.

    `job_apply_clicks: int | None`
    :   The type of the None singleton.

    `landing_page_clicks: int | None`
    :   The type of the None singleton.

    `lead_generation_mail_contact_info_shares: int | None`
    :   The type of the None singleton.

    `lead_generation_mail_interested_clicks: int | None`
    :   The type of the None singleton.

    `likes: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `one_click_lead_form_opens: int | None`
    :   The type of the None singleton.

    `one_click_leads: int | None`
    :   The type of the None singleton.

    `opens: int | None`
    :   The type of the None singleton.

    `other_engagements: int | None`
    :   The type of the None singleton.

    `pivot_values: list[str] | None`
    :   The type of the None singleton.

    `post_click_job_applications: int | None`
    :   The type of the None singleton.

    `post_click_job_apply_clicks: int | None`
    :   The type of the None singleton.

    `post_click_registrations: int | None`
    :   The type of the None singleton.

    `post_view_job_applications: int | None`
    :   The type of the None singleton.

    `post_view_job_apply_clicks: int | None`
    :   The type of the None singleton.

    `post_view_registrations: int | None`
    :   The type of the None singleton.

    `reactions: int | None`
    :   The type of the None singleton.

    `registrations: int | None`
    :   The type of the None singleton.

    `sends: int | None`
    :   The type of the None singleton.

    `shares: int | None`
    :   The type of the None singleton.

    `talent_leads: int | None`
    :   The type of the None singleton.

    `text_url_clicks: int | None`
    :   The type of the None singleton.

    `total_engagements: int | None`
    :   The type of the None singleton.

    `valid_work_email_leads: int | None`
    :   The type of the None singleton.

    `video_completions: int | None`
    :   The type of the None singleton.

    `video_first_quartile_completions: int | None`
    :   The type of the None singleton.

    `video_midpoint_completions: int | None`
    :   The type of the None singleton.

    `video_starts: int | None`
    :   The type of the None singleton.

    `video_third_quartile_completions: int | None`
    :   The type of the None singleton.

    `video_views: int | None`
    :   The type of the None singleton.

<a id="AdAnalyticsRecordDaterange"></a>

`AdAnalyticsRecordDaterange(**data: Any)`
:   Date range for this analytics record
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end: airbyte_agent_sdk.connectors.linkedin_ads.models.AdAnalyticsRecordDaterangeEnd | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: airbyte_agent_sdk.connectors.linkedin_ads.models.AdAnalyticsRecordDaterangeStart | None`
    :   The type of the None singleton.

<a id="AdAnalyticsRecordDaterangeEnd"></a>

`AdAnalyticsRecordDaterangeEnd(**data: Any)`
:   Nested schema for AdAnalyticsRecordDaterange.end
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `day: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `month: int | None`
    :   The type of the None singleton.

    `year: int | None`
    :   The type of the None singleton.

<a id="AdAnalyticsRecordDaterangeStart"></a>

`AdAnalyticsRecordDaterangeStart(**data: Any)`
:   Nested schema for AdAnalyticsRecordDaterange.start
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `day: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `month: int | None`
    :   The type of the None singleton.

    `year: int | None`
    :   The type of the None singleton.

<a id="AdAnalyticsResponse"></a>

`AdAnalyticsResponse(**data: Any)`
:   Ad analytics API response
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `elements: list[airbyte_agent_sdk.connectors.linkedin_ads.models.AdAnalyticsRecord] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.linkedin_ads.models.AdAnalyticsResponsePaging | None`
    :   The type of the None singleton.

<a id="AdAnalyticsResponsePaging"></a>

`AdAnalyticsResponsePaging(**data: Any)`
:   Nested schema for AdAnalyticsResponse.paging
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: int | None`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsSearchData"></a>

`AdCampaignAnalyticsSearchData(**data: Any)`
:   Search result data for ad_campaign_analytics entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AdCreativeAnalyticsSearchData"></a>

`AdCreativeAnalyticsSearchData(**data: Any)`
:   Search result data for ad_creative_analytics entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AccountUsersSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AccountsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdCampaignAnalyticsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdCreativeAnalyticsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[CampaignGroupsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[ConversionsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[CreativesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AccountUsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AccountUsersSearchResult"></a>

`AccountUsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AccountsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdCampaignAnalyticsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsSearchResult"></a>

`AdCampaignAnalyticsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdCreativeAnalyticsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsSearchResult"></a>

`AdCreativeAnalyticsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CampaignGroupsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignGroupsSearchResult"></a>

`CampaignGroupsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CampaignsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ConversionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ConversionsSearchResult"></a>

`ConversionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CreativesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CreativesSearchResult"></a>

`CreativesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Campaign"></a>

`Campaign(**data: Any)`
:   LinkedIn ad campaign object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str | None`
    :   The type of the None singleton.

    `associated_entity: str | None`
    :   The type of the None singleton.

    `audience_expansion_enabled: bool | None`
    :   The type of the None singleton.

    `campaign_group: str | None`
    :   The type of the None singleton.

    `change_audit_stamps: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignChangeauditstamps | None`
    :   The type of the None singleton.

    `connected_television_only: bool | None`
    :   The type of the None singleton.

    `cost_type: str | None`
    :   The type of the None singleton.

    `creative_selection: str | None`
    :   The type of the None singleton.

    `daily_budget: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignDailybudget | None`
    :   The type of the None singleton.

    `format: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `locale: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignLocale | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `objective_type: str | None`
    :   The type of the None singleton.

    `offsite_delivery_enabled: bool | None`
    :   The type of the None singleton.

    `offsite_preferences: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `optimization_target_type: str | None`
    :   The type of the None singleton.

    `pacing_strategy: str | None`
    :   The type of the None singleton.

    `political_intent: str | None`
    :   The type of the None singleton.

    `run_schedule: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignRunschedule | None`
    :   The type of the None singleton.

    `serving_statuses: list[str] | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `story_delivery_enabled: bool | None`
    :   The type of the None singleton.

    `targeting_criteria: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `test: bool | None`
    :   The type of the None singleton.

    `total_budget: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignTotalbudget | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `unit_cost: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignUnitcost | None`
    :   The type of the None singleton.

    `version: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignVersion | None`
    :   The type of the None singleton.

<a id="CampaignChangeauditstamps"></a>

`CampaignChangeauditstamps(**data: Any)`
:   Creation and last modification audit stamps
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignChangeauditstampsCreated | None`
    :   The type of the None singleton.

    `last_modified: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignChangeauditstampsLastmodified | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignChangeauditstampsCreated"></a>

`CampaignChangeauditstampsCreated(**data: Any)`
:   Nested schema for CampaignChangeauditstamps.created
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actor: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `time: int | None`
    :   The type of the None singleton.

<a id="CampaignChangeauditstampsLastmodified"></a>

`CampaignChangeauditstampsLastmodified(**data: Any)`
:   Nested schema for CampaignChangeauditstamps.lastModified
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actor: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `time: int | None`
    :   The type of the None singleton.

<a id="CampaignDailybudget"></a>

`CampaignDailybudget(**data: Any)`
:   Daily budget configuration
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   The type of the None singleton.

    `currency_code: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignGroup"></a>

`CampaignGroup(**data: Any)`
:   LinkedIn ad campaign group object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str | None`
    :   The type of the None singleton.

    `allowed_campaign_types: list[str] | None`
    :   The type of the None singleton.

    `backfilled: bool | None`
    :   The type of the None singleton.

    `change_audit_stamps: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignGroupChangeauditstamps | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `run_schedule: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignGroupRunschedule | None`
    :   The type of the None singleton.

    `serving_statuses: list[str] | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `test: bool | None`
    :   The type of the None singleton.

    `total_budget: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignGroupTotalbudget | None`
    :   The type of the None singleton.

<a id="CampaignGroupChangeauditstamps"></a>

`CampaignGroupChangeauditstamps(**data: Any)`
:   Creation and last modification audit stamps
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignGroupChangeauditstampsCreated | None`
    :   The type of the None singleton.

    `last_modified: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignGroupChangeauditstampsLastmodified | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignGroupChangeauditstampsCreated"></a>

`CampaignGroupChangeauditstampsCreated(**data: Any)`
:   Nested schema for CampaignGroupChangeauditstamps.created
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actor: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `time: int | None`
    :   The type of the None singleton.

<a id="CampaignGroupChangeauditstampsLastmodified"></a>

`CampaignGroupChangeauditstampsLastmodified(**data: Any)`
:   Nested schema for CampaignGroupChangeauditstamps.lastModified
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actor: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `time: int | None`
    :   The type of the None singleton.

<a id="CampaignGroupRunschedule"></a>

`CampaignGroupRunschedule(**data: Any)`
:   Campaign group run schedule
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: int | None`
    :   The type of the None singleton.

<a id="CampaignGroupTotalbudget"></a>

`CampaignGroupTotalbudget(**data: Any)`
:   Total budget for the campaign group
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   The type of the None singleton.

    `currency_code: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignGroupsList"></a>

`CampaignGroupsList(**data: Any)`
:   Paginated list of campaign groups
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `elements: list[airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignGroup] | None`
    :   The type of the None singleton.

    `metadata: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignGroupsListMetadata | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignGroupsListMetadata"></a>

`CampaignGroupsListMetadata(**data: Any)`
:   Nested schema for CampaignGroupsList.metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="CampaignGroupsListResultMeta"></a>

`CampaignGroupsListResultMeta(**data: Any)`
:   Metadata for campaign_groups.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="CampaignGroupsSearchData"></a>

`CampaignGroupsSearchData(**data: Any)`
:   Search result data for campaign_groups entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str | None`
    :   Associated account URN

    `allowed_campaign_types: list[typing.Any] | None`
    :   Types of campaigns allowed in this group

    `backfilled: bool | None`
    :   Whether the campaign group is backfilled

    `id: int | None`
    :   Unique campaign group identifier

    `model_config`
    :   The type of the None singleton.

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

<a id="CampaignLocale"></a>

`CampaignLocale(**data: Any)`
:   Campaign locale settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `country: str | None`
    :   The type of the None singleton.

    `language: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignRunschedule"></a>

`CampaignRunschedule(**data: Any)`
:   Campaign run schedule
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: int | None`
    :   The type of the None singleton.

<a id="CampaignTotalbudget"></a>

`CampaignTotalbudget(**data: Any)`
:   Total budget configuration
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   The type of the None singleton.

    `currency_code: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignUnitcost"></a>

`CampaignUnitcost(**data: Any)`
:   Cost per unit (bid amount)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   The type of the None singleton.

    `currency_code: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignVersion"></a>

`CampaignVersion(**data: Any)`
:   Version information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `version_tag: str | None`
    :   The type of the None singleton.

<a id="CampaignsList"></a>

`CampaignsList(**data: Any)`
:   Paginated list of campaigns
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `elements: list[airbyte_agent_sdk.connectors.linkedin_ads.models.Campaign] | None`
    :   The type of the None singleton.

    `metadata: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignsListMetadata | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsListMetadata"></a>

`CampaignsListMetadata(**data: Any)`
:   Nested schema for CampaignsList.metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
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

    `next_page_token: str | None`
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

    `model_config`
    :   The type of the None singleton.

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

<a id="Conversion"></a>

`Conversion(**data: Any)`
:   LinkedIn ad conversion tracking rule
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str | None`
    :   The type of the None singleton.

    `associated_campaigns: list[typing.Any] | None`
    :   The type of the None singleton.

    `attribution_type: str | None`
    :   The type of the None singleton.

    `campaigns: list[str] | None`
    :   The type of the None singleton.

    `conversion_method: str | None`
    :   The type of the None singleton.

    `created: int | None`
    :   The type of the None singleton.

    `enabled: bool | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `image_pixel_tag: str | None`
    :   The type of the None singleton.

    `last_callback_at: int | None`
    :   The type of the None singleton.

    `last_modified: int | None`
    :   The type of the None singleton.

    `latest_first_party_callback_at: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `post_click_attribution_window_size: int | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `url_match_rule_expression: list[typing.Any] | None`
    :   The type of the None singleton.

    `url_rules: list[typing.Any] | None`
    :   The type of the None singleton.

    `value: airbyte_agent_sdk.connectors.linkedin_ads.models.ConversionValue | None`
    :   The type of the None singleton.

    `value_type: str | None`
    :   The type of the None singleton.

    `view_through_attribution_window_size: int | None`
    :   The type of the None singleton.

<a id="ConversionValue"></a>

`ConversionValue(**data: Any)`
:   Conversion value
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   The type of the None singleton.

    `currency_code: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ConversionsList"></a>

`ConversionsList(**data: Any)`
:   Paginated list of conversions
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `elements: list[airbyte_agent_sdk.connectors.linkedin_ads.models.Conversion] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.linkedin_ads.models.ConversionsListPaging | None`
    :   The type of the None singleton.

<a id="ConversionsListPaging"></a>

`ConversionsListPaging(**data: Any)`
:   Nested schema for ConversionsList.paging
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: int | None`
    :   The type of the None singleton.

    `total: int | None`
    :   The type of the None singleton.

<a id="ConversionsListResultMeta"></a>

`ConversionsListResultMeta(**data: Any)`
:   Metadata for conversions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `total: int | None`
    :   The type of the None singleton.

<a id="ConversionsSearchData"></a>

`ConversionsSearchData(**data: Any)`
:   Search result data for conversions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="Creative"></a>

`Creative(**data: Any)`
:   LinkedIn ad creative object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str | None`
    :   The type of the None singleton.

    `campaign: str | None`
    :   The type of the None singleton.

    `content: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_at: int | None`
    :   The type of the None singleton.

    `created_by: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `intended_status: str | None`
    :   The type of the None singleton.

    `is_serving: bool | None`
    :   The type of the None singleton.

    `is_test: bool | None`
    :   The type of the None singleton.

    `last_modified_at: int | None`
    :   The type of the None singleton.

    `last_modified_by: str | None`
    :   The type of the None singleton.

    `leadgen_call_to_action: airbyte_agent_sdk.connectors.linkedin_ads.models.CreativeLeadgencalltoaction | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `review: airbyte_agent_sdk.connectors.linkedin_ads.models.CreativeReview | None`
    :   The type of the None singleton.

    `serving_hold_reasons: list[str] | None`
    :   The type of the None singleton.

<a id="CreativeLeadgencalltoaction"></a>

`CreativeLeadgencalltoaction(**data: Any)`
:   Lead generation call to action
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `destination: str | None`
    :   The type of the None singleton.

    `label: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CreativeReview"></a>

`CreativeReview(**data: Any)`
:   Review status and rejection reasons
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `rejection_reasons: list[typing.Any] | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

<a id="CreativesList"></a>

`CreativesList(**data: Any)`
:   Paginated list of creatives
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `elements: list[airbyte_agent_sdk.connectors.linkedin_ads.models.Creative] | None`
    :   The type of the None singleton.

    `metadata: airbyte_agent_sdk.connectors.linkedin_ads.models.CreativesListMetadata | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CreativesListMetadata"></a>

`CreativesListMetadata(**data: Any)`
:   Nested schema for CreativesList.metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="CreativesListResultMeta"></a>

`CreativesListResultMeta(**data: Any)`
:   Metadata for creatives.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="CreativesSearchData"></a>

`CreativesSearchData(**data: Any)`
:   Search result data for creatives entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Creative name

    `serving_hold_reasons: list[typing.Any] | None`
    :   Reasons for holding creative from serving

<a id="LinkedinAdsAuthConfig"></a>

`LinkedinAdsAuthConfig(**data: Any)`
:   OAuth 2.0 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   OAuth 2.0 application client ID

    `client_secret: str`
    :   OAuth 2.0 application client secret

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   OAuth 2.0 refresh token for automatic renewal

<a id="LinkedinAdsCheckResult"></a>

`LinkedinAdsCheckResult(**data: Any)`
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

<a id="LinkedinAdsExecuteResult"></a>

`LinkedinAdsExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult[list[AdAnalyticsRecord]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="LinkedinAdsExecuteResultWithMeta"></a>

`LinkedinAdsExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[AccountUser], AccountUsersListResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[Account], AccountsListResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[CampaignGroup], CampaignGroupsListResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[Conversion], ConversionsListResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[Creative], CreativesListResultMeta]

    ### Class variables

    `meta: ~S | None`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`LinkedinAdsExecuteResultWithMeta[list[AccountUser], AccountUsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AccountUsersListResult"></a>

`AccountUsersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`LinkedinAdsExecuteResultWithMeta[list[Account], AccountsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
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

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`LinkedinAdsExecuteResultWithMeta[list[CampaignGroup], CampaignGroupsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignGroupsListResult"></a>

`CampaignGroupsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`LinkedinAdsExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
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

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`LinkedinAdsExecuteResultWithMeta[list[Conversion], ConversionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ConversionsListResult"></a>

`ConversionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`LinkedinAdsExecuteResultWithMeta[list[Creative], CreativesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CreativesListResult"></a>

`CreativesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`LinkedinAdsExecuteResult[list[AdAnalyticsRecord]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdCampaignAnalyticsListResult"></a>

`AdCampaignAnalyticsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdCreativeAnalyticsListResult"></a>

`AdCreativeAnalyticsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="LinkedinAdsReplicationConfig"></a>

`LinkedinAdsReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from LinkedIn Ads.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   UTC date in the format YYYY-MM-DD. Any data before this date will not be replicated.