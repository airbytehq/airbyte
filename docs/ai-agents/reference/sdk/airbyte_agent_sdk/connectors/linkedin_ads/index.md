---
id: airbyte_agent_sdk-connectors-linkedin_ads-index
title: airbyte_agent_sdk.connectors.linkedin_ads.index
---

Module airbyte_agent_sdk.connectors.linkedin_ads
================================================
Linkedin-Ads connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.linkedin_ads.connector
* airbyte_agent_sdk.connectors.linkedin_ads.connector_model
* airbyte_agent_sdk.connectors.linkedin_ads.models
* airbyte_agent_sdk.connectors.linkedin_ads.types

Classes
-------

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

<a id="AirbyteAuthConfig"></a>

`AirbyteAuthConfig(**data: Any)`
:   Authentication configuration for Airbyte hosted mode execution.
    
    Pass this to the connector's `auth_config` parameter to use hosted mode,
    where API credentials are stored securely in Airbyte Cloud.
    
    For hosted mode execution, provide client credentials with either:
    - `connector_id`: Direct connector/source ID (skips lookup)
    - `workspace_name`: Workspace name for connector lookup
    
    Attributes:
        workspace_name: Workspace name for hosted mode connector lookup
        organization_id: Optional Airbyte organization ID for multi-org selection
        airbyte_client_id: Airbyte OAuth client ID (required for hosted mode)
        airbyte_client_secret: Airbyte OAuth client secret (required for hosted mode)
        connector_id: Specific connector/source ID (skips lookup if provided)
    
    Examples:
        # Hosted mode with connector_id (no lookup needed)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with workspace_name (lookup by workspace)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `airbyte_client_id: str | None`
    :   The type of the None singleton.

    `airbyte_client_secret: str | None`
    :   The type of the None singleton.

    `connector_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: str | None`
    :   The type of the None singleton.

    `workspace_name: str | None`
    :   The type of the None singleton.

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

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchMeta`
    :   Pagination metadata.

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

<a id="LinkedinAdsConnector"></a>

`LinkedinAdsConnector(auth_config: LinkedinAdsAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Linkedin-Ads API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new linkedin-ads connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., LinkedinAdsAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = LinkedinAdsConnector(auth_config=LinkedinAdsAuthConfig(refresh_token="...", client_id="...", client_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = LinkedinAdsConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = LinkedinAdsConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )

    ### Class variables

    `connector_name`
    :   The type of the None singleton.

    `connector_version`
    :   The type of the None singleton.

    `sdk_version`
    :   The type of the None singleton.

    ### Static methods

    `agent_tool(role: AgentToolRole | None = None, *, inspect_tool: str | None = None, docs_tool: str | None = None, max_output_chars: int | None | Unset = UNSET, framework: FrameworkName = 'none', internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> Callable[[~_F], ~_F]`
    :   Framework-agnostic decorator for user-written connector tool functions.
        
        The progressive-docs sibling of tool_utils: instead of baking the full
        entity/action reference into the docstring, it instructs the agent to
        call this connector's inspect and docs tools before executing. Tool
        failures raise :class:`airbyte_agent_sdk.AirbyteToolError` by default
        (``framework="none"``, no auto-detection) — pass ``framework=...`` to
        translate to a supported framework's signal instead.
        
        Decorate three functions per connector — execute, inspect and docs.
        The role is inferred from each function's signature (extra parameters
        are allowed); a signature matching more than one role, a generic
        ``(*args, **kwargs)`` wrapper, or a callable whose signature cannot
        be read must pass the role explicitly:
        
        - ``(entity, action, ...)`` -> ``"execute"``
        - ``(section, ...)``        -> ``"read_skill_docs"``
        - ``()``                    -> ``"inspect_connector"``
        
        Usage:
            connector = LinkedinAdsConnector(...)
        
            @LinkedinAdsConnector.agent_tool()
            async def execute(entity: str, action: str, params: dict | None = None):
                return await connector.execute(entity=entity, action=action, params=params or \{\})
        
            @LinkedinAdsConnector.agent_tool()
            async def inspect_connector():
                return await connector.inspect_connector()
        
            @LinkedinAdsConnector.agent_tool()
            async def read_skill_docs(section: str | None = None):
                return await connector.read_skill_docs(section)
        
        Args:
            role: ``"execute" | "inspect_connector" | "read_skill_docs"``.
                None (default) infers the role from the decorated function's
                signature; an explicit role validates the canonical
                parameters are present (functions accepting ``**kwargs``, or
                callables whose signature cannot be read, pass validation).
            inspect_tool: Exact registered name of the sibling inspect tool,
                woven into the execute docstring for tighter steering.
                Defaults to generic phrasing.
            docs_tool: Exact registered name of the sibling docs tool (see
                inspect_tool).
            max_output_chars: Max serialized output size before failing.
                Defaults per role: execute -> DEFAULT_MAX_OUTPUT_CHARS, docs
                tools -> None.
            framework: Translation target for tool failures. Defaults to
                ``"none"`` (raise AirbyteToolError); never auto-detects.
            internal_retries: How many transient runtime failures (429/5xx,
                network, timeout) to retry silently before surfacing.
                Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate ``(error, args, kwargs)
                -> bool`` further restricting which retryable errors are safe
                for this specific tool. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback ``(error,
                args, kwargs) -> str | None`` invoked after internal retries
                are exhausted or skipped. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000, framework: FrameworkName | None = None, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Add connector-specific documentation and runtime safeguards to one tool.
        
        For new agents, prefer `build_connector_tools`. It returns progressive
        `inspect_connector`, `read_skill_docs`, and `execute` tools so the agent
        can load only the connector guidance it needs:
        
        ```python
        from airbyte_agent_sdk import build_connector_tools
        from pydantic_ai import Agent
        
        tools = build_connector_tools(connector, framework="pydantic_ai")
        agent = Agent("openai:gpt-4o", tools=tools.as_list())
        ```
        
        ### Legacy: one generated-description tool
        
        Existing integrations can keep using `tool_utils` for one broad
        `execute` tool with the connector's full generated catalog in its
        description:
        
        ```python
        from fastmcp import FastMCP
        
        connector = LinkedinAdsConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @LinkedinAdsConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @LinkedinAdsConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @LinkedinAdsConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        This decorator composes `translate_exceptions` for runtime wrapping,
        output-size checks, framework signal translation, and optional internal
        retries, then adds connector-specific docstring augmentation.
        
        Args:
            update_docstring: When True, append connector capabilities to `__doc__`.
            max_output_chars: Max serialized output size before raising. Use `None` to disable.
            framework: One of `"pydantic_ai" | "langchain" | "openai_agents" | "mcp"`.
                Defaults to `None`, which auto-detects each framework's canonical
                import in order. Explicit always wins.
            internal_retries: How many transient runtime failures (429/5xx, network,
                timeout) to retry silently before surfacing. Default 0. Forwarded to
                `airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate `(error, args, kwargs) -> bool`
                further restricting which retryable errors are safe for this specific
                tool. Forwarded to `airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback
                `(error, args, kwargs) -> str | None`. Invoked after internal retries
                are exhausted or were skipped because `should_internal_retry` returned
                `False`. Forwarded to `airbyte_agent_sdk.translation.translate_exceptions`.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            LinkedinAdsCheckResult with status ("healthy" or "unhealthy") and optional error message
        
        Example:
            result = await connector.check()
            if result.status == "healthy":
                print("Connection verified!")
            else:
                print(f"Check failed: \{result.error\}")

    `close(self)`
    :   Close the connector and release resources.

    `entity_schema(self, entity: str) ‑> dict[str, typing.Any] | None`
    :   Get the JSON schema for an entity.
        
        Args:
            entity: Entity name (e.g., "contacts", "companies")
        
        Returns:
            JSON schema dict describing the entity structure, or None if not found.
        
        Example:
            schema = connector.entity_schema("contacts")
            if schema:
                print(f"Contact properties: \{list(schema.get('properties', \{\}).keys())\}")

    `execute(self, entity: str, action: "Literal['list', 'create', 'get', 'update', 'delete', 'context_store_search', 'context_store_sql_query']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
            select_fields: Optional allowlist of dot-notation fields to include
            exclude_fields: Optional blocklist of dot-notation fields to remove
            skip_truncation: Disable long-text truncation for collection actions
        
        Returns:
            Typed response based on the operation
        
        Example:
            customer = await connector.execute(
                entity="customers",
                action="get",
                params=\{"id": "cus_123"\}
            )

    `inspect_connector(self) ‑> dict[str, typing.Any]`
    :   Inspect this connector's hosted metadata/readiness and resolve its docs skill id.
        
        Call this before read_skill_docs in the normal hosted flow. For
        local/offline connectors this returns a local-mode payload with a
        warning instead of a hosted inspection.
        
        Example:
            info = await connector.inspect_connector()
            print(info["docs_skill_id"])

    `list_entities(self) ‑> list[dict[str, typing.Any]]`
    :   Get structured data about available entities, actions, and parameters.
        
        Returns a list of entity descriptions with:
        - entity_name: Name of the entity (e.g., "contacts", "deals")
        - description: Entity description from the first endpoint
        - available_actions: List of actions (e.g., ["list", "get", "create"])
        - parameters: Dict mapping action -> list of parameter dicts
        
        Example:
            entities = connector.list_entities()
            for entity in entities:
                print(f"\{entity['entity_name']\}: \{entity['available_actions']\}")

    `read_skill_docs(self, section: str | None = None) ‑> str`
    :   Read this connector's usage docs, rendered to text.
        
        Omit section for the outline and general guidance; pass an exact
        section id from the outline for full details. For local/offline
        connectors the full generated docs are returned and section is
        ignored.
        
        Example:
            outline = await connector.read_skill_docs()
            details = await connector.read_skill_docs(section="entity:contacts")

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