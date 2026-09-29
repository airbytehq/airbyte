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

<a id="AccountCreateRequest"></a>

`AccountCreateRequest(**data: Any)`
:   Fields for creating an ad account
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `reference: str | None`
    :   The type of the None singleton.

    `test: bool | None`
    :   The type of the None singleton.

    `type_: str`
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

<a id="AccountUserUpsertRequest"></a>

`AccountUserUpsertRequest(**data: Any)`
:   Role grant for an ad account user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `role: str`
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

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.linkedin_ads.models.AccountUsersListPaging | None`
    :   The type of the None singleton.

<a id="AccountUsersListPaging"></a>

`AccountUsersListPaging(**data: Any)`
:   Nested schema for AccountUsersList.paging
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | None`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.linkedin_ads.models.AccountUsersListPagingLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: int | None`
    :   The type of the None singleton.

    `total: int | None`
    :   The type of the None singleton.

<a id="AccountUsersListPagingLinksItem"></a>

`AccountUsersListPagingLinksItem(**data: Any)`
:   Nested schema for AccountUsersListPaging.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

    `type_: str | None`
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

    `count: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: int | None`
    :   The type of the None singleton.

    `total: int | None`
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
    :   The account associated with the user

    `created: str | None`
    :   The date and time when the user account was created

    `last_modified: str | None`
    :   The date and time when the user account was last modified

    `model_config`
    :   The type of the None singleton.

    `role: str | None`
    :   The role assigned to the user in the account

    `user: str | None`
    :   The user details including name, email, etc.

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

<a id="AccountsCreateResultMeta"></a>

`AccountsCreateResultMeta(**data: Any)`
:   Metadata for accounts.Action.CREATE operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_id: str | None`
    :   The type of the None singleton.

    `model_config`
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

    `created: str | None`
    :   The timestamp indicating when the account was created.

    `currency: str | None`
    :   The currency used for financial transactions in the account.

    `id: int | None`
    :   The unique identifier for the account.

    `last_modified: str | None`
    :   The timestamp of the last modification made to the account.

    `model_config`
    :   The type of the None singleton.

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

    `links: list[airbyte_agent_sdk.connectors.linkedin_ads.models.AdAnalyticsResponsePagingLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: int | None`
    :   The type of the None singleton.

    `total: int | None`
    :   The type of the None singleton.

<a id="AdAnalyticsResponsePagingLinksItem"></a>

`AdAnalyticsResponsePagingLinksItem(**data: Any)`
:   Nested schema for AdAnalyticsResponsePaging.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

    `type_: str | None`
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

    `model_config`
    :   The type of the None singleton.

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AdImpressionDeviceAnalytics"></a>

`AdImpressionDeviceAnalytics(**data: Any)`
:   Ad analytics record pivoted by device type
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action_clicks: float | None`
    :   The type of the None singleton.

    `ad_unit_clicks: float | None`
    :   The type of the None singleton.

    `approximate_member_reach: float | None`
    :   The type of the None singleton.

    `card_clicks: float | None`
    :   The type of the None singleton.

    `card_impressions: float | None`
    :   The type of the None singleton.

    `clicks: float | None`
    :   The type of the None singleton.

    `comment_likes: float | None`
    :   The type of the None singleton.

    `comments: float | None`
    :   The type of the None singleton.

    `company_page_clicks: float | None`
    :   The type of the None singleton.

    `conversion_value_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_usd: float | None`
    :   The type of the None singleton.

    `document_completions: float | None`
    :   The type of the None singleton.

    `document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `download_clicks: float | None`
    :   The type of the None singleton.

    `end_date: str | None`
    :   The type of the None singleton.

    `external_website_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `follows: float | None`
    :   The type of the None singleton.

    `full_screen_plays: float | None`
    :   The type of the None singleton.

    `impressions: float | None`
    :   The type of the None singleton.

    `job_applications: float | None`
    :   The type of the None singleton.

    `job_apply_clicks: float | None`
    :   The type of the None singleton.

    `landing_page_clicks: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_contact_info_shares: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_interested_clicks: float | None`
    :   The type of the None singleton.

    `likes: float | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `one_click_leads: float | None`
    :   The type of the None singleton.

    `opens: float | None`
    :   The type of the None singleton.

    `other_engagements: float | None`
    :   The type of the None singleton.

    `pivot: str | None`
    :   The type of the None singleton.

    `pivot_values: list[typing.Any] | None`
    :   The type of the None singleton.

    `post_click_job_applications: float | None`
    :   The type of the None singleton.

    `post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_click_registrations: float | None`
    :   The type of the None singleton.

    `post_view_job_applications: float | None`
    :   The type of the None singleton.

    `post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_view_registrations: float | None`
    :   The type of the None singleton.

    `reactions: float | None`
    :   The type of the None singleton.

    `registrations: float | None`
    :   The type of the None singleton.

    `sends: float | None`
    :   The type of the None singleton.

    `shares: float | None`
    :   The type of the None singleton.

    `sponsored_campaign: str | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `string_of_pivot_values: str | None`
    :   The type of the None singleton.

    `talent_leads: float | None`
    :   The type of the None singleton.

    `text_url_clicks: float | None`
    :   The type of the None singleton.

    `total_engagements: float | None`
    :   The type of the None singleton.

    `valid_work_email_leads: float | None`
    :   The type of the None singleton.

    `video_completions: float | None`
    :   The type of the None singleton.

    `video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `video_starts: float | None`
    :   The type of the None singleton.

    `video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_views: float | None`
    :   The type of the None singleton.

    `viral_card_clicks: float | None`
    :   The type of the None singleton.

    `viral_card_impressions: float | None`
    :   The type of the None singleton.

    `viral_clicks: float | None`
    :   The type of the None singleton.

    `viral_comment_likes: float | None`
    :   The type of the None singleton.

    `viral_comments: float | None`
    :   The type of the None singleton.

    `viral_company_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_document_completions: float | None`
    :   The type of the None singleton.

    `viral_document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_download_clicks: float | None`
    :   The type of the None singleton.

    `viral_external_website_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `viral_follows: float | None`
    :   The type of the None singleton.

    `viral_full_screen_plays: float | None`
    :   The type of the None singleton.

    `viral_impressions: float | None`
    :   The type of the None singleton.

    `viral_job_applications: float | None`
    :   The type of the None singleton.

    `viral_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_landing_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_likes: float | None`
    :   The type of the None singleton.

    `viral_one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `viral_one_click_leads: float | None`
    :   The type of the None singleton.

    `viral_other_engagements: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_click_registrations: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_view_registrations: float | None`
    :   The type of the None singleton.

    `viral_reactions: float | None`
    :   The type of the None singleton.

    `viral_registrations: float | None`
    :   The type of the None singleton.

    `viral_shares: float | None`
    :   The type of the None singleton.

    `viral_total_engagements: float | None`
    :   The type of the None singleton.

    `viral_video_completions: float | None`
    :   The type of the None singleton.

    `viral_video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_video_starts: float | None`
    :   The type of the None singleton.

    `viral_video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_views: float | None`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsSearchData"></a>

`AdImpressionDeviceAnalyticsSearchData(**data: Any)`
:   Search result data for ad_impression_device_analytics entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AdMemberCompanyAnalytics"></a>

`AdMemberCompanyAnalytics(**data: Any)`
:   Ad analytics record pivoted by member company
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action_clicks: float | None`
    :   The type of the None singleton.

    `ad_unit_clicks: float | None`
    :   The type of the None singleton.

    `approximate_member_reach: float | None`
    :   The type of the None singleton.

    `card_clicks: float | None`
    :   The type of the None singleton.

    `card_impressions: float | None`
    :   The type of the None singleton.

    `clicks: float | None`
    :   The type of the None singleton.

    `comment_likes: float | None`
    :   The type of the None singleton.

    `comments: float | None`
    :   The type of the None singleton.

    `company_page_clicks: float | None`
    :   The type of the None singleton.

    `conversion_value_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_usd: float | None`
    :   The type of the None singleton.

    `document_completions: float | None`
    :   The type of the None singleton.

    `document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `download_clicks: float | None`
    :   The type of the None singleton.

    `end_date: str | None`
    :   The type of the None singleton.

    `external_website_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `follows: float | None`
    :   The type of the None singleton.

    `full_screen_plays: float | None`
    :   The type of the None singleton.

    `impressions: float | None`
    :   The type of the None singleton.

    `job_applications: float | None`
    :   The type of the None singleton.

    `job_apply_clicks: float | None`
    :   The type of the None singleton.

    `landing_page_clicks: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_contact_info_shares: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_interested_clicks: float | None`
    :   The type of the None singleton.

    `likes: float | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `one_click_leads: float | None`
    :   The type of the None singleton.

    `opens: float | None`
    :   The type of the None singleton.

    `other_engagements: float | None`
    :   The type of the None singleton.

    `pivot: str | None`
    :   The type of the None singleton.

    `pivot_values: list[typing.Any] | None`
    :   The type of the None singleton.

    `post_click_job_applications: float | None`
    :   The type of the None singleton.

    `post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_click_registrations: float | None`
    :   The type of the None singleton.

    `post_view_job_applications: float | None`
    :   The type of the None singleton.

    `post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_view_registrations: float | None`
    :   The type of the None singleton.

    `reactions: float | None`
    :   The type of the None singleton.

    `registrations: float | None`
    :   The type of the None singleton.

    `sends: float | None`
    :   The type of the None singleton.

    `shares: float | None`
    :   The type of the None singleton.

    `sponsored_campaign: str | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `string_of_pivot_values: str | None`
    :   The type of the None singleton.

    `talent_leads: float | None`
    :   The type of the None singleton.

    `text_url_clicks: float | None`
    :   The type of the None singleton.

    `total_engagements: float | None`
    :   The type of the None singleton.

    `valid_work_email_leads: float | None`
    :   The type of the None singleton.

    `video_completions: float | None`
    :   The type of the None singleton.

    `video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `video_starts: float | None`
    :   The type of the None singleton.

    `video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_views: float | None`
    :   The type of the None singleton.

    `viral_card_clicks: float | None`
    :   The type of the None singleton.

    `viral_card_impressions: float | None`
    :   The type of the None singleton.

    `viral_clicks: float | None`
    :   The type of the None singleton.

    `viral_comment_likes: float | None`
    :   The type of the None singleton.

    `viral_comments: float | None`
    :   The type of the None singleton.

    `viral_company_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_document_completions: float | None`
    :   The type of the None singleton.

    `viral_document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_download_clicks: float | None`
    :   The type of the None singleton.

    `viral_external_website_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `viral_follows: float | None`
    :   The type of the None singleton.

    `viral_full_screen_plays: float | None`
    :   The type of the None singleton.

    `viral_impressions: float | None`
    :   The type of the None singleton.

    `viral_job_applications: float | None`
    :   The type of the None singleton.

    `viral_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_landing_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_likes: float | None`
    :   The type of the None singleton.

    `viral_one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `viral_one_click_leads: float | None`
    :   The type of the None singleton.

    `viral_other_engagements: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_click_registrations: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_view_registrations: float | None`
    :   The type of the None singleton.

    `viral_reactions: float | None`
    :   The type of the None singleton.

    `viral_registrations: float | None`
    :   The type of the None singleton.

    `viral_shares: float | None`
    :   The type of the None singleton.

    `viral_total_engagements: float | None`
    :   The type of the None singleton.

    `viral_video_completions: float | None`
    :   The type of the None singleton.

    `viral_video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_video_starts: float | None`
    :   The type of the None singleton.

    `viral_video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_views: float | None`
    :   The type of the None singleton.

<a id="AdMemberCompanyAnalyticsSearchData"></a>

`AdMemberCompanyAnalyticsSearchData(**data: Any)`
:   Search result data for ad_member_company_analytics entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AdMemberCompanySizeAnalytics"></a>

`AdMemberCompanySizeAnalytics(**data: Any)`
:   Ad analytics record pivoted by member company size
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action_clicks: float | None`
    :   The type of the None singleton.

    `ad_unit_clicks: float | None`
    :   The type of the None singleton.

    `approximate_member_reach: float | None`
    :   The type of the None singleton.

    `card_clicks: float | None`
    :   The type of the None singleton.

    `card_impressions: float | None`
    :   The type of the None singleton.

    `clicks: float | None`
    :   The type of the None singleton.

    `comment_likes: float | None`
    :   The type of the None singleton.

    `comments: float | None`
    :   The type of the None singleton.

    `company_page_clicks: float | None`
    :   The type of the None singleton.

    `conversion_value_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_usd: float | None`
    :   The type of the None singleton.

    `document_completions: float | None`
    :   The type of the None singleton.

    `document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `download_clicks: float | None`
    :   The type of the None singleton.

    `end_date: str | None`
    :   The type of the None singleton.

    `external_website_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `follows: float | None`
    :   The type of the None singleton.

    `full_screen_plays: float | None`
    :   The type of the None singleton.

    `impressions: float | None`
    :   The type of the None singleton.

    `job_applications: float | None`
    :   The type of the None singleton.

    `job_apply_clicks: float | None`
    :   The type of the None singleton.

    `landing_page_clicks: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_contact_info_shares: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_interested_clicks: float | None`
    :   The type of the None singleton.

    `likes: float | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `one_click_leads: float | None`
    :   The type of the None singleton.

    `opens: float | None`
    :   The type of the None singleton.

    `other_engagements: float | None`
    :   The type of the None singleton.

    `pivot: str | None`
    :   The type of the None singleton.

    `pivot_values: list[typing.Any] | None`
    :   The type of the None singleton.

    `post_click_job_applications: float | None`
    :   The type of the None singleton.

    `post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_click_registrations: float | None`
    :   The type of the None singleton.

    `post_view_job_applications: float | None`
    :   The type of the None singleton.

    `post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_view_registrations: float | None`
    :   The type of the None singleton.

    `reactions: float | None`
    :   The type of the None singleton.

    `registrations: float | None`
    :   The type of the None singleton.

    `sends: float | None`
    :   The type of the None singleton.

    `shares: float | None`
    :   The type of the None singleton.

    `sponsored_campaign: str | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `string_of_pivot_values: str | None`
    :   The type of the None singleton.

    `talent_leads: float | None`
    :   The type of the None singleton.

    `text_url_clicks: float | None`
    :   The type of the None singleton.

    `total_engagements: float | None`
    :   The type of the None singleton.

    `valid_work_email_leads: float | None`
    :   The type of the None singleton.

    `video_completions: float | None`
    :   The type of the None singleton.

    `video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `video_starts: float | None`
    :   The type of the None singleton.

    `video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_views: float | None`
    :   The type of the None singleton.

    `viral_card_clicks: float | None`
    :   The type of the None singleton.

    `viral_card_impressions: float | None`
    :   The type of the None singleton.

    `viral_clicks: float | None`
    :   The type of the None singleton.

    `viral_comment_likes: float | None`
    :   The type of the None singleton.

    `viral_comments: float | None`
    :   The type of the None singleton.

    `viral_company_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_document_completions: float | None`
    :   The type of the None singleton.

    `viral_document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_download_clicks: float | None`
    :   The type of the None singleton.

    `viral_external_website_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `viral_follows: float | None`
    :   The type of the None singleton.

    `viral_full_screen_plays: float | None`
    :   The type of the None singleton.

    `viral_impressions: float | None`
    :   The type of the None singleton.

    `viral_job_applications: float | None`
    :   The type of the None singleton.

    `viral_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_landing_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_likes: float | None`
    :   The type of the None singleton.

    `viral_one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `viral_one_click_leads: float | None`
    :   The type of the None singleton.

    `viral_other_engagements: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_click_registrations: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_view_registrations: float | None`
    :   The type of the None singleton.

    `viral_reactions: float | None`
    :   The type of the None singleton.

    `viral_registrations: float | None`
    :   The type of the None singleton.

    `viral_shares: float | None`
    :   The type of the None singleton.

    `viral_total_engagements: float | None`
    :   The type of the None singleton.

    `viral_video_completions: float | None`
    :   The type of the None singleton.

    `viral_video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_video_starts: float | None`
    :   The type of the None singleton.

    `viral_video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_views: float | None`
    :   The type of the None singleton.

<a id="AdMemberCompanySizeAnalyticsSearchData"></a>

`AdMemberCompanySizeAnalyticsSearchData(**data: Any)`
:   Search result data for ad_member_company_size_analytics entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AdMemberCountryAnalytics"></a>

`AdMemberCountryAnalytics(**data: Any)`
:   Ad analytics record pivoted by member country
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action_clicks: float | None`
    :   The type of the None singleton.

    `ad_unit_clicks: float | None`
    :   The type of the None singleton.

    `approximate_member_reach: float | None`
    :   The type of the None singleton.

    `card_clicks: float | None`
    :   The type of the None singleton.

    `card_impressions: float | None`
    :   The type of the None singleton.

    `clicks: float | None`
    :   The type of the None singleton.

    `comment_likes: float | None`
    :   The type of the None singleton.

    `comments: float | None`
    :   The type of the None singleton.

    `company_page_clicks: float | None`
    :   The type of the None singleton.

    `conversion_value_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_usd: float | None`
    :   The type of the None singleton.

    `document_completions: float | None`
    :   The type of the None singleton.

    `document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `download_clicks: float | None`
    :   The type of the None singleton.

    `end_date: str | None`
    :   The type of the None singleton.

    `external_website_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `follows: float | None`
    :   The type of the None singleton.

    `full_screen_plays: float | None`
    :   The type of the None singleton.

    `impressions: float | None`
    :   The type of the None singleton.

    `job_applications: float | None`
    :   The type of the None singleton.

    `job_apply_clicks: float | None`
    :   The type of the None singleton.

    `landing_page_clicks: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_contact_info_shares: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_interested_clicks: float | None`
    :   The type of the None singleton.

    `likes: float | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `one_click_leads: float | None`
    :   The type of the None singleton.

    `opens: float | None`
    :   The type of the None singleton.

    `other_engagements: float | None`
    :   The type of the None singleton.

    `pivot: str | None`
    :   The type of the None singleton.

    `pivot_values: list[typing.Any] | None`
    :   The type of the None singleton.

    `post_click_job_applications: float | None`
    :   The type of the None singleton.

    `post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_click_registrations: float | None`
    :   The type of the None singleton.

    `post_view_job_applications: float | None`
    :   The type of the None singleton.

    `post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_view_registrations: float | None`
    :   The type of the None singleton.

    `reactions: float | None`
    :   The type of the None singleton.

    `registrations: float | None`
    :   The type of the None singleton.

    `sends: float | None`
    :   The type of the None singleton.

    `shares: float | None`
    :   The type of the None singleton.

    `sponsored_campaign: str | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `string_of_pivot_values: str | None`
    :   The type of the None singleton.

    `talent_leads: float | None`
    :   The type of the None singleton.

    `text_url_clicks: float | None`
    :   The type of the None singleton.

    `total_engagements: float | None`
    :   The type of the None singleton.

    `valid_work_email_leads: float | None`
    :   The type of the None singleton.

    `video_completions: float | None`
    :   The type of the None singleton.

    `video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `video_starts: float | None`
    :   The type of the None singleton.

    `video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_views: float | None`
    :   The type of the None singleton.

    `viral_card_clicks: float | None`
    :   The type of the None singleton.

    `viral_card_impressions: float | None`
    :   The type of the None singleton.

    `viral_clicks: float | None`
    :   The type of the None singleton.

    `viral_comment_likes: float | None`
    :   The type of the None singleton.

    `viral_comments: float | None`
    :   The type of the None singleton.

    `viral_company_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_document_completions: float | None`
    :   The type of the None singleton.

    `viral_document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_download_clicks: float | None`
    :   The type of the None singleton.

    `viral_external_website_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `viral_follows: float | None`
    :   The type of the None singleton.

    `viral_full_screen_plays: float | None`
    :   The type of the None singleton.

    `viral_impressions: float | None`
    :   The type of the None singleton.

    `viral_job_applications: float | None`
    :   The type of the None singleton.

    `viral_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_landing_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_likes: float | None`
    :   The type of the None singleton.

    `viral_one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `viral_one_click_leads: float | None`
    :   The type of the None singleton.

    `viral_other_engagements: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_click_registrations: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_view_registrations: float | None`
    :   The type of the None singleton.

    `viral_reactions: float | None`
    :   The type of the None singleton.

    `viral_registrations: float | None`
    :   The type of the None singleton.

    `viral_shares: float | None`
    :   The type of the None singleton.

    `viral_total_engagements: float | None`
    :   The type of the None singleton.

    `viral_video_completions: float | None`
    :   The type of the None singleton.

    `viral_video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_video_starts: float | None`
    :   The type of the None singleton.

    `viral_video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_views: float | None`
    :   The type of the None singleton.

<a id="AdMemberCountryAnalyticsSearchData"></a>

`AdMemberCountryAnalyticsSearchData(**data: Any)`
:   Search result data for ad_member_country_analytics entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AdMemberIndustryAnalytics"></a>

`AdMemberIndustryAnalytics(**data: Any)`
:   Ad analytics record pivoted by member industry
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action_clicks: float | None`
    :   The type of the None singleton.

    `ad_unit_clicks: float | None`
    :   The type of the None singleton.

    `approximate_member_reach: float | None`
    :   The type of the None singleton.

    `card_clicks: float | None`
    :   The type of the None singleton.

    `card_impressions: float | None`
    :   The type of the None singleton.

    `clicks: float | None`
    :   The type of the None singleton.

    `comment_likes: float | None`
    :   The type of the None singleton.

    `comments: float | None`
    :   The type of the None singleton.

    `company_page_clicks: float | None`
    :   The type of the None singleton.

    `conversion_value_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_usd: float | None`
    :   The type of the None singleton.

    `document_completions: float | None`
    :   The type of the None singleton.

    `document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `download_clicks: float | None`
    :   The type of the None singleton.

    `end_date: str | None`
    :   The type of the None singleton.

    `external_website_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `follows: float | None`
    :   The type of the None singleton.

    `full_screen_plays: float | None`
    :   The type of the None singleton.

    `impressions: float | None`
    :   The type of the None singleton.

    `job_applications: float | None`
    :   The type of the None singleton.

    `job_apply_clicks: float | None`
    :   The type of the None singleton.

    `landing_page_clicks: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_contact_info_shares: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_interested_clicks: float | None`
    :   The type of the None singleton.

    `likes: float | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `one_click_leads: float | None`
    :   The type of the None singleton.

    `opens: float | None`
    :   The type of the None singleton.

    `other_engagements: float | None`
    :   The type of the None singleton.

    `pivot: str | None`
    :   The type of the None singleton.

    `pivot_values: list[typing.Any] | None`
    :   The type of the None singleton.

    `post_click_job_applications: float | None`
    :   The type of the None singleton.

    `post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_click_registrations: float | None`
    :   The type of the None singleton.

    `post_view_job_applications: float | None`
    :   The type of the None singleton.

    `post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_view_registrations: float | None`
    :   The type of the None singleton.

    `reactions: float | None`
    :   The type of the None singleton.

    `registrations: float | None`
    :   The type of the None singleton.

    `sends: float | None`
    :   The type of the None singleton.

    `shares: float | None`
    :   The type of the None singleton.

    `sponsored_campaign: str | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `string_of_pivot_values: str | None`
    :   The type of the None singleton.

    `talent_leads: float | None`
    :   The type of the None singleton.

    `text_url_clicks: float | None`
    :   The type of the None singleton.

    `total_engagements: float | None`
    :   The type of the None singleton.

    `valid_work_email_leads: float | None`
    :   The type of the None singleton.

    `video_completions: float | None`
    :   The type of the None singleton.

    `video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `video_starts: float | None`
    :   The type of the None singleton.

    `video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_views: float | None`
    :   The type of the None singleton.

    `viral_card_clicks: float | None`
    :   The type of the None singleton.

    `viral_card_impressions: float | None`
    :   The type of the None singleton.

    `viral_clicks: float | None`
    :   The type of the None singleton.

    `viral_comment_likes: float | None`
    :   The type of the None singleton.

    `viral_comments: float | None`
    :   The type of the None singleton.

    `viral_company_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_document_completions: float | None`
    :   The type of the None singleton.

    `viral_document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_download_clicks: float | None`
    :   The type of the None singleton.

    `viral_external_website_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `viral_follows: float | None`
    :   The type of the None singleton.

    `viral_full_screen_plays: float | None`
    :   The type of the None singleton.

    `viral_impressions: float | None`
    :   The type of the None singleton.

    `viral_job_applications: float | None`
    :   The type of the None singleton.

    `viral_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_landing_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_likes: float | None`
    :   The type of the None singleton.

    `viral_one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `viral_one_click_leads: float | None`
    :   The type of the None singleton.

    `viral_other_engagements: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_click_registrations: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_view_registrations: float | None`
    :   The type of the None singleton.

    `viral_reactions: float | None`
    :   The type of the None singleton.

    `viral_registrations: float | None`
    :   The type of the None singleton.

    `viral_shares: float | None`
    :   The type of the None singleton.

    `viral_total_engagements: float | None`
    :   The type of the None singleton.

    `viral_video_completions: float | None`
    :   The type of the None singleton.

    `viral_video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_video_starts: float | None`
    :   The type of the None singleton.

    `viral_video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_views: float | None`
    :   The type of the None singleton.

<a id="AdMemberIndustryAnalyticsSearchData"></a>

`AdMemberIndustryAnalyticsSearchData(**data: Any)`
:   Search result data for ad_member_industry_analytics entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AdMemberJobFunctionAnalytics"></a>

`AdMemberJobFunctionAnalytics(**data: Any)`
:   Ad analytics record pivoted by member job function
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action_clicks: float | None`
    :   The type of the None singleton.

    `ad_unit_clicks: float | None`
    :   The type of the None singleton.

    `approximate_member_reach: float | None`
    :   The type of the None singleton.

    `card_clicks: float | None`
    :   The type of the None singleton.

    `card_impressions: float | None`
    :   The type of the None singleton.

    `clicks: float | None`
    :   The type of the None singleton.

    `comment_likes: float | None`
    :   The type of the None singleton.

    `comments: float | None`
    :   The type of the None singleton.

    `company_page_clicks: float | None`
    :   The type of the None singleton.

    `conversion_value_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_usd: float | None`
    :   The type of the None singleton.

    `document_completions: float | None`
    :   The type of the None singleton.

    `document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `download_clicks: float | None`
    :   The type of the None singleton.

    `end_date: str | None`
    :   The type of the None singleton.

    `external_website_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `follows: float | None`
    :   The type of the None singleton.

    `full_screen_plays: float | None`
    :   The type of the None singleton.

    `impressions: float | None`
    :   The type of the None singleton.

    `job_applications: float | None`
    :   The type of the None singleton.

    `job_apply_clicks: float | None`
    :   The type of the None singleton.

    `landing_page_clicks: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_contact_info_shares: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_interested_clicks: float | None`
    :   The type of the None singleton.

    `likes: float | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `one_click_leads: float | None`
    :   The type of the None singleton.

    `opens: float | None`
    :   The type of the None singleton.

    `other_engagements: float | None`
    :   The type of the None singleton.

    `pivot: str | None`
    :   The type of the None singleton.

    `pivot_values: list[typing.Any] | None`
    :   The type of the None singleton.

    `post_click_job_applications: float | None`
    :   The type of the None singleton.

    `post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_click_registrations: float | None`
    :   The type of the None singleton.

    `post_view_job_applications: float | None`
    :   The type of the None singleton.

    `post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_view_registrations: float | None`
    :   The type of the None singleton.

    `reactions: float | None`
    :   The type of the None singleton.

    `registrations: float | None`
    :   The type of the None singleton.

    `sends: float | None`
    :   The type of the None singleton.

    `shares: float | None`
    :   The type of the None singleton.

    `sponsored_campaign: str | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `string_of_pivot_values: str | None`
    :   The type of the None singleton.

    `talent_leads: float | None`
    :   The type of the None singleton.

    `text_url_clicks: float | None`
    :   The type of the None singleton.

    `total_engagements: float | None`
    :   The type of the None singleton.

    `valid_work_email_leads: float | None`
    :   The type of the None singleton.

    `video_completions: float | None`
    :   The type of the None singleton.

    `video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `video_starts: float | None`
    :   The type of the None singleton.

    `video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_views: float | None`
    :   The type of the None singleton.

    `viral_card_clicks: float | None`
    :   The type of the None singleton.

    `viral_card_impressions: float | None`
    :   The type of the None singleton.

    `viral_clicks: float | None`
    :   The type of the None singleton.

    `viral_comment_likes: float | None`
    :   The type of the None singleton.

    `viral_comments: float | None`
    :   The type of the None singleton.

    `viral_company_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_document_completions: float | None`
    :   The type of the None singleton.

    `viral_document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_download_clicks: float | None`
    :   The type of the None singleton.

    `viral_external_website_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `viral_follows: float | None`
    :   The type of the None singleton.

    `viral_full_screen_plays: float | None`
    :   The type of the None singleton.

    `viral_impressions: float | None`
    :   The type of the None singleton.

    `viral_job_applications: float | None`
    :   The type of the None singleton.

    `viral_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_landing_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_likes: float | None`
    :   The type of the None singleton.

    `viral_one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `viral_one_click_leads: float | None`
    :   The type of the None singleton.

    `viral_other_engagements: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_click_registrations: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_view_registrations: float | None`
    :   The type of the None singleton.

    `viral_reactions: float | None`
    :   The type of the None singleton.

    `viral_registrations: float | None`
    :   The type of the None singleton.

    `viral_shares: float | None`
    :   The type of the None singleton.

    `viral_total_engagements: float | None`
    :   The type of the None singleton.

    `viral_video_completions: float | None`
    :   The type of the None singleton.

    `viral_video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_video_starts: float | None`
    :   The type of the None singleton.

    `viral_video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_views: float | None`
    :   The type of the None singleton.

<a id="AdMemberJobFunctionAnalyticsSearchData"></a>

`AdMemberJobFunctionAnalyticsSearchData(**data: Any)`
:   Search result data for ad_member_job_function_analytics entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AdMemberJobTitleAnalytics"></a>

`AdMemberJobTitleAnalytics(**data: Any)`
:   Ad analytics record pivoted by member job title
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action_clicks: float | None`
    :   The type of the None singleton.

    `ad_unit_clicks: float | None`
    :   The type of the None singleton.

    `approximate_member_reach: float | None`
    :   The type of the None singleton.

    `card_clicks: float | None`
    :   The type of the None singleton.

    `card_impressions: float | None`
    :   The type of the None singleton.

    `clicks: float | None`
    :   The type of the None singleton.

    `comment_likes: float | None`
    :   The type of the None singleton.

    `comments: float | None`
    :   The type of the None singleton.

    `company_page_clicks: float | None`
    :   The type of the None singleton.

    `conversion_value_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_usd: float | None`
    :   The type of the None singleton.

    `document_completions: float | None`
    :   The type of the None singleton.

    `document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `download_clicks: float | None`
    :   The type of the None singleton.

    `end_date: str | None`
    :   The type of the None singleton.

    `external_website_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `follows: float | None`
    :   The type of the None singleton.

    `full_screen_plays: float | None`
    :   The type of the None singleton.

    `impressions: float | None`
    :   The type of the None singleton.

    `job_applications: float | None`
    :   The type of the None singleton.

    `job_apply_clicks: float | None`
    :   The type of the None singleton.

    `landing_page_clicks: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_contact_info_shares: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_interested_clicks: float | None`
    :   The type of the None singleton.

    `likes: float | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `one_click_leads: float | None`
    :   The type of the None singleton.

    `opens: float | None`
    :   The type of the None singleton.

    `other_engagements: float | None`
    :   The type of the None singleton.

    `pivot: str | None`
    :   The type of the None singleton.

    `pivot_values: list[typing.Any] | None`
    :   The type of the None singleton.

    `post_click_job_applications: float | None`
    :   The type of the None singleton.

    `post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_click_registrations: float | None`
    :   The type of the None singleton.

    `post_view_job_applications: float | None`
    :   The type of the None singleton.

    `post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_view_registrations: float | None`
    :   The type of the None singleton.

    `reactions: float | None`
    :   The type of the None singleton.

    `registrations: float | None`
    :   The type of the None singleton.

    `sends: float | None`
    :   The type of the None singleton.

    `shares: float | None`
    :   The type of the None singleton.

    `sponsored_campaign: str | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `string_of_pivot_values: str | None`
    :   The type of the None singleton.

    `talent_leads: float | None`
    :   The type of the None singleton.

    `text_url_clicks: float | None`
    :   The type of the None singleton.

    `total_engagements: float | None`
    :   The type of the None singleton.

    `valid_work_email_leads: float | None`
    :   The type of the None singleton.

    `video_completions: float | None`
    :   The type of the None singleton.

    `video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `video_starts: float | None`
    :   The type of the None singleton.

    `video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_views: float | None`
    :   The type of the None singleton.

    `viral_card_clicks: float | None`
    :   The type of the None singleton.

    `viral_card_impressions: float | None`
    :   The type of the None singleton.

    `viral_clicks: float | None`
    :   The type of the None singleton.

    `viral_comment_likes: float | None`
    :   The type of the None singleton.

    `viral_comments: float | None`
    :   The type of the None singleton.

    `viral_company_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_document_completions: float | None`
    :   The type of the None singleton.

    `viral_document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_download_clicks: float | None`
    :   The type of the None singleton.

    `viral_external_website_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `viral_follows: float | None`
    :   The type of the None singleton.

    `viral_full_screen_plays: float | None`
    :   The type of the None singleton.

    `viral_impressions: float | None`
    :   The type of the None singleton.

    `viral_job_applications: float | None`
    :   The type of the None singleton.

    `viral_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_landing_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_likes: float | None`
    :   The type of the None singleton.

    `viral_one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `viral_one_click_leads: float | None`
    :   The type of the None singleton.

    `viral_other_engagements: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_click_registrations: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_view_registrations: float | None`
    :   The type of the None singleton.

    `viral_reactions: float | None`
    :   The type of the None singleton.

    `viral_registrations: float | None`
    :   The type of the None singleton.

    `viral_shares: float | None`
    :   The type of the None singleton.

    `viral_total_engagements: float | None`
    :   The type of the None singleton.

    `viral_video_completions: float | None`
    :   The type of the None singleton.

    `viral_video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_video_starts: float | None`
    :   The type of the None singleton.

    `viral_video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_views: float | None`
    :   The type of the None singleton.

<a id="AdMemberJobTitleAnalyticsSearchData"></a>

`AdMemberJobTitleAnalyticsSearchData(**data: Any)`
:   Search result data for ad_member_job_title_analytics entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AdMemberRegionAnalytics"></a>

`AdMemberRegionAnalytics(**data: Any)`
:   Ad analytics record pivoted by member region
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action_clicks: float | None`
    :   The type of the None singleton.

    `ad_unit_clicks: float | None`
    :   The type of the None singleton.

    `approximate_member_reach: float | None`
    :   The type of the None singleton.

    `card_clicks: float | None`
    :   The type of the None singleton.

    `card_impressions: float | None`
    :   The type of the None singleton.

    `clicks: float | None`
    :   The type of the None singleton.

    `comment_likes: float | None`
    :   The type of the None singleton.

    `comments: float | None`
    :   The type of the None singleton.

    `company_page_clicks: float | None`
    :   The type of the None singleton.

    `conversion_value_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_usd: float | None`
    :   The type of the None singleton.

    `document_completions: float | None`
    :   The type of the None singleton.

    `document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `download_clicks: float | None`
    :   The type of the None singleton.

    `end_date: str | None`
    :   The type of the None singleton.

    `external_website_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `follows: float | None`
    :   The type of the None singleton.

    `full_screen_plays: float | None`
    :   The type of the None singleton.

    `impressions: float | None`
    :   The type of the None singleton.

    `job_applications: float | None`
    :   The type of the None singleton.

    `job_apply_clicks: float | None`
    :   The type of the None singleton.

    `landing_page_clicks: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_contact_info_shares: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_interested_clicks: float | None`
    :   The type of the None singleton.

    `likes: float | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `one_click_leads: float | None`
    :   The type of the None singleton.

    `opens: float | None`
    :   The type of the None singleton.

    `other_engagements: float | None`
    :   The type of the None singleton.

    `pivot: str | None`
    :   The type of the None singleton.

    `pivot_values: list[typing.Any] | None`
    :   The type of the None singleton.

    `post_click_job_applications: float | None`
    :   The type of the None singleton.

    `post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_click_registrations: float | None`
    :   The type of the None singleton.

    `post_view_job_applications: float | None`
    :   The type of the None singleton.

    `post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_view_registrations: float | None`
    :   The type of the None singleton.

    `reactions: float | None`
    :   The type of the None singleton.

    `registrations: float | None`
    :   The type of the None singleton.

    `sends: float | None`
    :   The type of the None singleton.

    `shares: float | None`
    :   The type of the None singleton.

    `sponsored_campaign: str | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `string_of_pivot_values: str | None`
    :   The type of the None singleton.

    `talent_leads: float | None`
    :   The type of the None singleton.

    `text_url_clicks: float | None`
    :   The type of the None singleton.

    `total_engagements: float | None`
    :   The type of the None singleton.

    `valid_work_email_leads: float | None`
    :   The type of the None singleton.

    `video_completions: float | None`
    :   The type of the None singleton.

    `video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `video_starts: float | None`
    :   The type of the None singleton.

    `video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_views: float | None`
    :   The type of the None singleton.

    `viral_card_clicks: float | None`
    :   The type of the None singleton.

    `viral_card_impressions: float | None`
    :   The type of the None singleton.

    `viral_clicks: float | None`
    :   The type of the None singleton.

    `viral_comment_likes: float | None`
    :   The type of the None singleton.

    `viral_comments: float | None`
    :   The type of the None singleton.

    `viral_company_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_document_completions: float | None`
    :   The type of the None singleton.

    `viral_document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_download_clicks: float | None`
    :   The type of the None singleton.

    `viral_external_website_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `viral_follows: float | None`
    :   The type of the None singleton.

    `viral_full_screen_plays: float | None`
    :   The type of the None singleton.

    `viral_impressions: float | None`
    :   The type of the None singleton.

    `viral_job_applications: float | None`
    :   The type of the None singleton.

    `viral_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_landing_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_likes: float | None`
    :   The type of the None singleton.

    `viral_one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `viral_one_click_leads: float | None`
    :   The type of the None singleton.

    `viral_other_engagements: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_click_registrations: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_view_registrations: float | None`
    :   The type of the None singleton.

    `viral_reactions: float | None`
    :   The type of the None singleton.

    `viral_registrations: float | None`
    :   The type of the None singleton.

    `viral_shares: float | None`
    :   The type of the None singleton.

    `viral_total_engagements: float | None`
    :   The type of the None singleton.

    `viral_video_completions: float | None`
    :   The type of the None singleton.

    `viral_video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_video_starts: float | None`
    :   The type of the None singleton.

    `viral_video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_views: float | None`
    :   The type of the None singleton.

<a id="AdMemberRegionAnalyticsSearchData"></a>

`AdMemberRegionAnalyticsSearchData(**data: Any)`
:   Search result data for ad_member_region_analytics entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AdMemberSeniorityAnalytics"></a>

`AdMemberSeniorityAnalytics(**data: Any)`
:   Ad analytics record pivoted by member seniority
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action_clicks: float | None`
    :   The type of the None singleton.

    `ad_unit_clicks: float | None`
    :   The type of the None singleton.

    `approximate_member_reach: float | None`
    :   The type of the None singleton.

    `card_clicks: float | None`
    :   The type of the None singleton.

    `card_impressions: float | None`
    :   The type of the None singleton.

    `clicks: float | None`
    :   The type of the None singleton.

    `comment_likes: float | None`
    :   The type of the None singleton.

    `comments: float | None`
    :   The type of the None singleton.

    `company_page_clicks: float | None`
    :   The type of the None singleton.

    `conversion_value_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_local_currency: float | None`
    :   The type of the None singleton.

    `cost_in_usd: float | None`
    :   The type of the None singleton.

    `document_completions: float | None`
    :   The type of the None singleton.

    `document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `download_clicks: float | None`
    :   The type of the None singleton.

    `end_date: str | None`
    :   The type of the None singleton.

    `external_website_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `follows: float | None`
    :   The type of the None singleton.

    `full_screen_plays: float | None`
    :   The type of the None singleton.

    `impressions: float | None`
    :   The type of the None singleton.

    `job_applications: float | None`
    :   The type of the None singleton.

    `job_apply_clicks: float | None`
    :   The type of the None singleton.

    `landing_page_clicks: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_contact_info_shares: float | None`
    :   The type of the None singleton.

    `lead_generation_mail_interested_clicks: float | None`
    :   The type of the None singleton.

    `likes: float | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `one_click_leads: float | None`
    :   The type of the None singleton.

    `opens: float | None`
    :   The type of the None singleton.

    `other_engagements: float | None`
    :   The type of the None singleton.

    `pivot: str | None`
    :   The type of the None singleton.

    `pivot_values: list[typing.Any] | None`
    :   The type of the None singleton.

    `post_click_job_applications: float | None`
    :   The type of the None singleton.

    `post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_click_registrations: float | None`
    :   The type of the None singleton.

    `post_view_job_applications: float | None`
    :   The type of the None singleton.

    `post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `post_view_registrations: float | None`
    :   The type of the None singleton.

    `reactions: float | None`
    :   The type of the None singleton.

    `registrations: float | None`
    :   The type of the None singleton.

    `sends: float | None`
    :   The type of the None singleton.

    `shares: float | None`
    :   The type of the None singleton.

    `sponsored_campaign: str | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `string_of_pivot_values: str | None`
    :   The type of the None singleton.

    `talent_leads: float | None`
    :   The type of the None singleton.

    `text_url_clicks: float | None`
    :   The type of the None singleton.

    `total_engagements: float | None`
    :   The type of the None singleton.

    `valid_work_email_leads: float | None`
    :   The type of the None singleton.

    `video_completions: float | None`
    :   The type of the None singleton.

    `video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `video_starts: float | None`
    :   The type of the None singleton.

    `video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `video_views: float | None`
    :   The type of the None singleton.

    `viral_card_clicks: float | None`
    :   The type of the None singleton.

    `viral_card_impressions: float | None`
    :   The type of the None singleton.

    `viral_clicks: float | None`
    :   The type of the None singleton.

    `viral_comment_likes: float | None`
    :   The type of the None singleton.

    `viral_comments: float | None`
    :   The type of the None singleton.

    `viral_company_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_document_completions: float | None`
    :   The type of the None singleton.

    `viral_document_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_document_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_document_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_download_clicks: float | None`
    :   The type of the None singleton.

    `viral_external_website_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_click_conversions: float | None`
    :   The type of the None singleton.

    `viral_external_website_post_view_conversions: float | None`
    :   The type of the None singleton.

    `viral_follows: float | None`
    :   The type of the None singleton.

    `viral_full_screen_plays: float | None`
    :   The type of the None singleton.

    `viral_impressions: float | None`
    :   The type of the None singleton.

    `viral_job_applications: float | None`
    :   The type of the None singleton.

    `viral_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_landing_page_clicks: float | None`
    :   The type of the None singleton.

    `viral_likes: float | None`
    :   The type of the None singleton.

    `viral_one_click_lead_form_opens: float | None`
    :   The type of the None singleton.

    `viral_one_click_leads: float | None`
    :   The type of the None singleton.

    `viral_other_engagements: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_click_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_click_registrations: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_applications: float | None`
    :   The type of the None singleton.

    `viral_post_view_job_apply_clicks: float | None`
    :   The type of the None singleton.

    `viral_post_view_registrations: float | None`
    :   The type of the None singleton.

    `viral_reactions: float | None`
    :   The type of the None singleton.

    `viral_registrations: float | None`
    :   The type of the None singleton.

    `viral_shares: float | None`
    :   The type of the None singleton.

    `viral_total_engagements: float | None`
    :   The type of the None singleton.

    `viral_video_completions: float | None`
    :   The type of the None singleton.

    `viral_video_first_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_midpoint_completions: float | None`
    :   The type of the None singleton.

    `viral_video_starts: float | None`
    :   The type of the None singleton.

    `viral_video_third_quartile_completions: float | None`
    :   The type of the None singleton.

    `viral_video_views: float | None`
    :   The type of the None singleton.

<a id="AdMemberSeniorityAnalyticsSearchData"></a>

`AdMemberSeniorityAnalyticsSearchData(**data: Any)`
:   Search result data for ad_member_seniority_analytics entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdImpressionDeviceAnalyticsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberCompanyAnalyticsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberCompanySizeAnalyticsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberCountryAnalyticsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberIndustryAnalyticsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberJobFunctionAnalyticsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberJobTitleAnalyticsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberRegionAnalyticsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberSeniorityAnalyticsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[CampaignGroupsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[ConversionsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[CreativesSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[LeadFormResponsesSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[LeadFormsSearchData]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]

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

`AirbyteSearchResult[AdImpressionDeviceAnalyticsSearchData](**data: Any)`
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

<a id="AdImpressionDeviceAnalyticsSearchResult"></a>

`AdImpressionDeviceAnalyticsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdMemberCompanyAnalyticsSearchData](**data: Any)`
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

<a id="AdMemberCompanyAnalyticsSearchResult"></a>

`AdMemberCompanyAnalyticsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdMemberCompanySizeAnalyticsSearchData](**data: Any)`
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

<a id="AdMemberCompanySizeAnalyticsSearchResult"></a>

`AdMemberCompanySizeAnalyticsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdMemberCountryAnalyticsSearchData](**data: Any)`
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

<a id="AdMemberCountryAnalyticsSearchResult"></a>

`AdMemberCountryAnalyticsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdMemberIndustryAnalyticsSearchData](**data: Any)`
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

<a id="AdMemberIndustryAnalyticsSearchResult"></a>

`AdMemberIndustryAnalyticsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdMemberJobFunctionAnalyticsSearchData](**data: Any)`
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

<a id="AdMemberJobFunctionAnalyticsSearchResult"></a>

`AdMemberJobFunctionAnalyticsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdMemberJobTitleAnalyticsSearchData](**data: Any)`
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

<a id="AdMemberJobTitleAnalyticsSearchResult"></a>

`AdMemberJobTitleAnalyticsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdMemberRegionAnalyticsSearchData](**data: Any)`
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

<a id="AdMemberRegionAnalyticsSearchResult"></a>

`AdMemberRegionAnalyticsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdMemberSeniorityAnalyticsSearchData](**data: Any)`
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

<a id="AdMemberSeniorityAnalyticsSearchResult"></a>

`AdMemberSeniorityAnalyticsSearchResult(**data: Any)`
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

`AirbyteSearchResult[LeadFormResponsesSearchData](**data: Any)`
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

<a id="LeadFormResponsesSearchResult"></a>

`LeadFormResponsesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[LeadFormsSearchData](**data: Any)`
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

<a id="LeadFormsSearchResult"></a>

`LeadFormsSearchResult(**data: Any)`
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

<a id="CampaignConversionUpsertRequest"></a>

`CampaignConversionUpsertRequest(**data: Any)`
:   Campaign-to-conversion association record; may be empty since the key carries both URNs
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `campaign: str | None`
    :   The type of the None singleton.

    `conversion: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignCreateRequest"></a>

`CampaignCreateRequest(**data: Any)`
:   Fields for creating a campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str`
    :   The type of the None singleton.

    `audience_expansion_enabled: bool | None`
    :   The type of the None singleton.

    `campaign_group: str | None`
    :   The type of the None singleton.

    `cost_type: str | None`
    :   The type of the None singleton.

    `creative_selection: str | None`
    :   The type of the None singleton.

    `daily_budget: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignCreateRequestDailybudget | None`
    :   The type of the None singleton.

    `locale: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignCreateRequestLocale | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `objective_type: str | None`
    :   The type of the None singleton.

    `offsite_delivery_enabled: bool`
    :   The type of the None singleton.

    `political_intent: str`
    :   The type of the None singleton.

    `run_schedule: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignCreateRequestRunschedule`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `targeting_criteria: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `unit_cost: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignCreateRequestUnitcost | None`
    :   The type of the None singleton.

<a id="CampaignCreateRequestDailybudget"></a>

`CampaignCreateRequestDailybudget(**data: Any)`
:   Daily budget
    
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

<a id="CampaignCreateRequestLocale"></a>

`CampaignCreateRequestLocale(**data: Any)`
:   Campaign locale
    
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

<a id="CampaignCreateRequestRunschedule"></a>

`CampaignCreateRequestRunschedule(**data: Any)`
:   Scheduled run window (epoch milliseconds)
    
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

<a id="CampaignCreateRequestUnitcost"></a>

`CampaignCreateRequestUnitcost(**data: Any)`
:   Bid amount per unit (per click, per impression, etc.)
    
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

<a id="CampaignGroupCreateRequest"></a>

`CampaignGroupCreateRequest(**data: Any)`
:   Fields for creating a campaign group
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `objective_type: str | None`
    :   The type of the None singleton.

    `run_schedule: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignGroupCreateRequestRunschedule`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `total_budget: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignGroupCreateRequestTotalbudget | None`
    :   The type of the None singleton.

<a id="CampaignGroupCreateRequestRunschedule"></a>

`CampaignGroupCreateRequestRunschedule(**data: Any)`
:   Scheduled run window (epoch milliseconds)
    
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

<a id="CampaignGroupCreateRequestTotalbudget"></a>

`CampaignGroupCreateRequestTotalbudget(**data: Any)`
:   Total budget across the group's lifetime
    
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

<a id="CampaignGroupsCreateResultMeta"></a>

`CampaignGroupsCreateResultMeta(**data: Any)`
:   Metadata for campaign_groups.Action.CREATE operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_id: str | None`
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

    `paging: airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignGroupsListPaging | None`
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

<a id="CampaignGroupsListPaging"></a>

`CampaignGroupsListPaging(**data: Any)`
:   Nested schema for CampaignGroupsList.paging
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | None`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignGroupsListPagingLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: int | None`
    :   The type of the None singleton.

    `total: int | None`
    :   The type of the None singleton.

<a id="CampaignGroupsListPagingLinksItem"></a>

`CampaignGroupsListPagingLinksItem(**data: Any)`
:   Nested schema for CampaignGroupsListPaging.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

    `type_: str | None`
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

    `model_config`
    :   The type of the None singleton.

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

<a id="CampaignsCreateResultMeta"></a>

`CampaignsCreateResultMeta(**data: Any)`
:   Metadata for campaigns.Action.CREATE operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_id: str | None`
    :   The type of the None singleton.

    `model_config`
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

    `model_config`
    :   The type of the None singleton.

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

    `ownership_type: str | None`
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

<a id="ConversionCreateRequest"></a>

`ConversionCreateRequest(**data: Any)`
:   Fields for creating a conversion tracking rule
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str`
    :   The type of the None singleton.

    `attribution_type: str | None`
    :   The type of the None singleton.

    `enabled: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `post_click_attribution_window_size: int | None`
    :   The type of the None singleton.

    `type_: str`
    :   The type of the None singleton.

    `url_match_rule_expression: list[list[dict[str, typing.Any]]] | None`
    :   The type of the None singleton.

    `value: airbyte_agent_sdk.connectors.linkedin_ads.models.ConversionCreateRequestValue | None`
    :   The type of the None singleton.

    `view_through_attribution_window_size: int | None`
    :   The type of the None singleton.

<a id="ConversionCreateRequestValue"></a>

`ConversionCreateRequestValue(**data: Any)`
:   Monetary value assigned to each conversion
    
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

<a id="ConversionEventsBatchRequest"></a>

`ConversionEventsBatchRequest(**data: Any)`
:   Batch of offline conversion events (Rest.li BATCH_CREATE, max 5,000 per request)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `elements: list[airbyte_agent_sdk.connectors.linkedin_ads.models.ConversionEventsBatchRequestElementsItem]`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ConversionEventsBatchRequestElementsItem"></a>

`ConversionEventsBatchRequestElementsItem(**data: Any)`
:   Nested schema for ConversionEventsBatchRequest.elements_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `conversion: str`
    :   Conversion rule URN, e.g. urn:lla:llaPartnerConversion:123456

    `conversion_happened_at: int`
    :   Epoch milliseconds when the conversion occurred

    `conversion_value: airbyte_agent_sdk.connectors.linkedin_ads.models.ConversionEventsBatchRequestElementsItemConversionvalue | None`
    :   Monetary value of this conversion

    `event_id: str | None`
    :   Optional unique event ID for deduplication

    `model_config`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.linkedin_ads.models.ConversionEventsBatchRequestElementsItemUser | None`
    :   Identifies the converting user (hashed email or other supported ID types)

<a id="ConversionEventsBatchRequestElementsItemConversionvalue"></a>

`ConversionEventsBatchRequestElementsItemConversionvalue(**data: Any)`
:   Monetary value of this conversion
    
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

<a id="ConversionEventsBatchRequestElementsItemUser"></a>

`ConversionEventsBatchRequestElementsItemUser(**data: Any)`
:   Identifies the converting user (hashed email or other supported ID types)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `user_ids: list[airbyte_agent_sdk.connectors.linkedin_ads.models.ConversionEventsBatchRequestElementsItemUserUseridsItem] | None`
    :   The type of the None singleton.

    `user_info: dict[str, typing.Any] | None`
    :   The type of the None singleton.

<a id="ConversionEventsBatchRequestElementsItemUserUseridsItem"></a>

`ConversionEventsBatchRequestElementsItemUserUseridsItem(**data: Any)`
:   Nested schema for ConversionEventsBatchRequestElementsItemUser.userIds_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id_type: str | None`
    :   e.g. SHA256_EMAIL, LINKEDIN_FIRST_PARTY_ADS_TRACKING_UUID

    `id_value: str | None`
    :   The type of the None singleton.

    `model_config`
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

<a id="ConversionsCreateResultMeta"></a>

`ConversionsCreateResultMeta(**data: Any)`
:   Metadata for conversions.Action.CREATE operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_id: str | None`
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

    `links: list[airbyte_agent_sdk.connectors.linkedin_ads.models.ConversionsListPagingLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: int | None`
    :   The type of the None singleton.

    `total: int | None`
    :   The type of the None singleton.

<a id="ConversionsListPagingLinksItem"></a>

`ConversionsListPagingLinksItem(**data: Any)`
:   Nested schema for ConversionsListPaging.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

    `type_: str | None`
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

    `model_config`
    :   The type of the None singleton.

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

<a id="CreativeCreateRequest"></a>

`CreativeCreateRequest(**data: Any)`
:   Fields for creating a creative
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `campaign: str`
    :   The type of the None singleton.

    `content: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `intended_status: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
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

<a id="CreativesCreateResultMeta"></a>

`CreativesCreateResultMeta(**data: Any)`
:   Metadata for creatives.Action.CREATE operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_id: str | None`
    :   The type of the None singleton.

    `model_config`
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

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the creative.

    `review: dict[str, typing.Any] | None`
    :   Review information for the creative.

    `serving_hold_reasons: list[typing.Any] | None`
    :   Reasons for holding the creative from serving.

<a id="LeadForm"></a>

`LeadForm(**data: Any)`
:   LinkedIn lead generation form
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created: int | None`
    :   The type of the None singleton.

    `creation_locale: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `hidden_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `last_modified: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `owner: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `review_info: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

    `version_id: int | None`
    :   The type of the None singleton.

    `version_tag: str | None`
    :   The type of the None singleton.

<a id="LeadFormResponse"></a>

`LeadFormResponse(**data: Any)`
:   LinkedIn lead form response (submitted lead)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `associated_entity: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `associated_entity_info: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `form: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `form_response: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `lead_metadata: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `lead_metadata_info: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `lead_type: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `owner: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `owner_info: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `response_id: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `submitted_at: int | None`
    :   The type of the None singleton.

    `submitter: str | None`
    :   The type of the None singleton.

    `test_lead: bool | None`
    :   The type of the None singleton.

    `versioned_lead_gen_form_urn: str | None`
    :   The type of the None singleton.

<a id="LeadFormResponsesList"></a>

`LeadFormResponsesList(**data: Any)`
:   Paginated list of lead form responses
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `elements: list[airbyte_agent_sdk.connectors.linkedin_ads.models.LeadFormResponse] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.linkedin_ads.models.LeadFormResponsesListPaging | None`
    :   The type of the None singleton.

<a id="LeadFormResponsesListPaging"></a>

`LeadFormResponsesListPaging(**data: Any)`
:   Nested schema for LeadFormResponsesList.paging
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | None`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.linkedin_ads.models.LeadFormResponsesListPagingLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: int | None`
    :   The type of the None singleton.

    `total: int | None`
    :   The type of the None singleton.

<a id="LeadFormResponsesListPagingLinksItem"></a>

`LeadFormResponsesListPagingLinksItem(**data: Any)`
:   Nested schema for LeadFormResponsesListPaging.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="LeadFormResponsesListResultMeta"></a>

`LeadFormResponsesListResultMeta(**data: Any)`
:   Metadata for lead_form_responses.Action.LIST operation
    
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

<a id="LeadFormResponsesSearchData"></a>

`LeadFormResponsesSearchData(**data: Any)`
:   Search result data for lead_form_responses entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="LeadFormsList"></a>

`LeadFormsList(**data: Any)`
:   Paginated list of lead forms
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `elements: list[airbyte_agent_sdk.connectors.linkedin_ads.models.LeadForm] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.linkedin_ads.models.LeadFormsListPaging | None`
    :   The type of the None singleton.

<a id="LeadFormsListPaging"></a>

`LeadFormsListPaging(**data: Any)`
:   Nested schema for LeadFormsList.paging
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | None`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.linkedin_ads.models.LeadFormsListPagingLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: int | None`
    :   The type of the None singleton.

    `total: int | None`
    :   The type of the None singleton.

<a id="LeadFormsListPagingLinksItem"></a>

`LeadFormsListPagingLinksItem(**data: Any)`
:   Nested schema for LeadFormsListPaging.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="LeadFormsListResultMeta"></a>

`LeadFormsListResultMeta(**data: Any)`
:   Metadata for lead_forms.Action.LIST operation
    
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

<a id="LeadFormsSearchData"></a>

`LeadFormsSearchData(**data: Any)`
:   Search result data for lead_forms entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="LinkedinAdsAccessTokenAuthenticationAuthConfig"></a>

`LinkedinAdsAccessTokenAuthenticationAuthConfig(**data: Any)`
:   Access Token Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   The access token generated for your developer application

    `model_config`
    :   The type of the None singleton.

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

    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, AccountsCreateResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, CampaignGroupsCreateResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, CampaignsCreateResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, ConversionsCreateResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, CreativesCreateResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[AccountUser], AccountUsersListResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[CampaignGroup], CampaignGroupsListResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[Conversion], ConversionsListResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[LeadFormResponse], LeadFormResponsesListResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[LeadForm], LeadFormsListResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[dict[str, Any]], AccountsListResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[dict[str, Any]], CampaignsListResultMeta]
    * airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[dict[str, Any]], CreativesListResultMeta]

    ### Class variables

    `meta: ~S | None`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, AccountsCreateResultMeta](**data: Any)`
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

<a id="AccountsCreateResult"></a>

`AccountsCreateResult(**data: Any)`
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

`LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, CampaignGroupsCreateResultMeta](**data: Any)`
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

<a id="CampaignGroupsCreateResult"></a>

`CampaignGroupsCreateResult(**data: Any)`
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

`LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, CampaignsCreateResultMeta](**data: Any)`
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

<a id="CampaignsCreateResult"></a>

`CampaignsCreateResult(**data: Any)`
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

`LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, ConversionsCreateResultMeta](**data: Any)`
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

<a id="ConversionsCreateResult"></a>

`ConversionsCreateResult(**data: Any)`
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

`LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, CreativesCreateResultMeta](**data: Any)`
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

<a id="CreativesCreateResult"></a>

`CreativesCreateResult(**data: Any)`
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

`LinkedinAdsExecuteResultWithMeta[list[LeadFormResponse], LeadFormResponsesListResultMeta](**data: Any)`
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

<a id="LeadFormResponsesListResult"></a>

`LeadFormResponsesListResult(**data: Any)`
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

`LinkedinAdsExecuteResultWithMeta[list[LeadForm], LeadFormsListResultMeta](**data: Any)`
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

<a id="LeadFormsListResult"></a>

`LeadFormsListResult(**data: Any)`
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

`LinkedinAdsExecuteResultWithMeta[list[dict[str, Any]], AccountsListResultMeta](**data: Any)`
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

`LinkedinAdsExecuteResultWithMeta[list[dict[str, Any]], CampaignsListResultMeta](**data: Any)`
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

`LinkedinAdsExecuteResultWithMeta[list[dict[str, Any]], CreativesListResultMeta](**data: Any)`
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

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdImpressionDeviceAnalyticsListResult"></a>

`AdImpressionDeviceAnalyticsListResult(**data: Any)`
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

<a id="AdMemberCompanyAnalyticsListResult"></a>

`AdMemberCompanyAnalyticsListResult(**data: Any)`
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

<a id="AdMemberCompanySizeAnalyticsListResult"></a>

`AdMemberCompanySizeAnalyticsListResult(**data: Any)`
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

<a id="AdMemberCountryAnalyticsListResult"></a>

`AdMemberCountryAnalyticsListResult(**data: Any)`
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

<a id="AdMemberIndustryAnalyticsListResult"></a>

`AdMemberIndustryAnalyticsListResult(**data: Any)`
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

<a id="AdMemberJobFunctionAnalyticsListResult"></a>

`AdMemberJobFunctionAnalyticsListResult(**data: Any)`
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

<a id="AdMemberJobTitleAnalyticsListResult"></a>

`AdMemberJobTitleAnalyticsListResult(**data: Any)`
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

<a id="AdMemberRegionAnalyticsListResult"></a>

`AdMemberRegionAnalyticsListResult(**data: Any)`
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

<a id="AdMemberSeniorityAnalyticsListResult"></a>

`AdMemberSeniorityAnalyticsListResult(**data: Any)`
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

<a id="LinkedinAdsOauth20AuthenticationAuthConfig"></a>

`LinkedinAdsOauth20AuthenticationAuthConfig(**data: Any)`
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

    `account_ids: str | None`
    :   Specify the account IDs to pull data from, separated by a space. Leave this field empty if you want to pull the data from all accounts accessible by the authenticated user. See the LinkedIn docs to locate these IDs.

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   UTC date in the format YYYY-MM-DD. Any data before this date will not be replicated.

<a id="RestliCreateResponse"></a>

`RestliCreateResponse(**data: Any)`
:   Rest.li create responses have an empty JSON body; the created entity ID or URN is returned in the x-restli-id response header (surfaced via the operation's meta extractor as created_id).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="RestliPartialUpdateRequest"></a>

`RestliPartialUpdateRequest(**data: Any)`
:   Rest.li partial update envelope shared by all LinkedIn Ads update operations. Wrap the fields to change in patch.$set. Setting an array field replaces the entire array, so include all existing elements you want to keep.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `patch: airbyte_agent_sdk.connectors.linkedin_ads.models.RestliPartialUpdateRequestPatch`
    :   The type of the None singleton.

<a id="RestliPartialUpdateRequestPatch"></a>

`RestliPartialUpdateRequestPatch(**data: Any)`
:   Nested schema for RestliPartialUpdateRequest.patch
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `set_: dict[str, typing.Any]`
    :   Map of field names to their new values