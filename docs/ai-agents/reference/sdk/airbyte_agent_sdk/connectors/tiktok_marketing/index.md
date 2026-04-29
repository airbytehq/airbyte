---
id: airbyte_agent_sdk-connectors-tiktok_marketing-index
title: airbyte_agent_sdk.connectors.tiktok_marketing.index
---

Module airbyte_agent_sdk.connectors.tiktok_marketing
====================================================
Tiktok-Marketing connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.tiktok_marketing.connector
* airbyte_agent_sdk.connectors.tiktok_marketing.connector_model
* airbyte_agent_sdk.connectors.tiktok_marketing.models
* airbyte_agent_sdk.connectors.tiktok_marketing.types

Classes
-------

<a id="AdGroupsReportsDailySearchData"></a>

`AdGroupsReportsDailySearchData(**data: Any)`
:   Search result data for ad_groups_reports_daily entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `adgroup_id: int | None`
    :   The unique identifier for the ad group.

    `adgroup_name: str | None`
    :   The name of the ad group.

    `app_install: float | None`
    :   Number of app installations.

    `average_video_play: float | None`
    :   Average video play duration.

    `average_video_play_per_user: float | None`
    :   Average video play duration per user.

    `campaign_id: int | None`
    :   The unique identifier for the campaign.

    `campaign_name: str | None`
    :   The name of the marketing campaign.

    `clicks: str | None`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: float | None`
    :   Number of clicks on the music disc.

    `comments: float | None`
    :   Number of comments.

    `conversion: str | None`
    :   Number of conversions.

    `conversion_rate: str | None`
    :   Rate of conversions.

    `cost_per_1000_reached: str | None`
    :   Cost per 1000 unique users reached.

    `cost_per_conversion: str | None`
    :   Cost per conversion.

    `cost_per_result: str | None`
    :   Cost per result.

    `cost_per_secondary_goal_result: str | None`
    :   Cost per secondary goal result.

    `cpc: str | None`
    :   Cost per click.

    `cpm: str | None`
    :   Cost per thousand impressions.

    `ctr: str | None`
    :   Click-through rate.

    `follows: float | None`
    :   Number of follows.

    `frequency: str | None`
    :   Average number of times each person saw the ad.

    `impressions: str | None`
    :   Number of times the ad was displayed.

    `likes: float | None`
    :   Number of likes.

    `model_config`
    :   The type of the None singleton.

    `placement_type: str | None`
    :   Type of ad placement.

    `profile_visits: float | None`
    :   Number of profile visits.

    `reach: str | None`
    :   Total number of unique users reached.

    `real_time_app_install: float | None`
    :   Real-time app installations.

    `real_time_app_install_cost: float | None`
    :   Cost of real-time app installations.

    `real_time_conversion: str | None`
    :   Real-time conversions.

    `real_time_conversion_rate: str | None`
    :   Real-time conversion rate.

    `real_time_cost_per_conversion: str | None`
    :   Real-time cost per conversion.

    `real_time_cost_per_result: str | None`
    :   Real-time cost per result.

    `real_time_result: str | None`
    :   Real-time results.

    `real_time_result_rate: str | None`
    :   Real-time result rate.

    `result: str | None`
    :   Number of results.

    `result_rate: str | None`
    :   Rate of results.

    `secondary_goal_result: str | None`
    :   Results for secondary goals.

    `secondary_goal_result_rate: str | None`
    :   Rate of secondary goal results.

    `shares: float | None`
    :   Number of shares.

    `spend: str | None`
    :   Total amount of money spent.

    `stat_time_day: str | None`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: float | None`
    :   Number of video play actions.

    `video_views_p100: float | None`
    :   Number of times video was watched to 100%.

    `video_views_p25: float | None`
    :   Number of times video was watched to 25%.

    `video_views_p50: float | None`
    :   Number of times video was watched to 50%.

    `video_views_p75: float | None`
    :   Number of times video was watched to 75%.

    `video_watched_2s: float | None`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: float | None`
    :   Number of times video was watched for at least 6 seconds.

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

    `adgroup_id: int | None`
    :   The unique identifier of the ad group

    `adgroup_name: str | None`
    :   The name of the ad group

    `advertiser_id: int | None`
    :   The unique identifier of the advertiser

    `budget: float | None`
    :   The allocated budget for the ad group

    `budget_mode: str | None`
    :   The mode for managing the budget

    `campaign_id: int | None`
    :   The unique identifier of the campaign

    `create_time: str | None`
    :   The timestamp for when the ad group was created

    `model_config`
    :   The type of the None singleton.

    `modify_time: str | None`
    :   The timestamp for when the ad group was last modified

    `operation_status: str | None`
    :   The status of the operation

    `optimization_goal: str | None`
    :   The goal set for optimization

    `placement_type: str | None`
    :   The type of ad placement

    `promotion_type: str | None`
    :   The type of promotion

    `secondary_status: str | None`
    :   The secondary status of the ad group

<a id="AdsReportsDailySearchData"></a>

`AdsReportsDailySearchData(**data: Any)`
:   Search result data for ads_reports_daily entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_id: int | None`
    :   The unique identifier for the ad.

    `ad_name: str | None`
    :   The name of the ad.

    `ad_text: str | None`
    :   The text content of the ad.

    `adgroup_id: int | None`
    :   The unique identifier for the ad group.

    `adgroup_name: str | None`
    :   The name of the ad group.

    `app_install: float | None`
    :   Number of app installations.

    `average_video_play: float | None`
    :   Average video play duration.

    `average_video_play_per_user: float | None`
    :   Average video play duration per user.

    `campaign_id: int | None`
    :   The unique identifier for the campaign.

    `campaign_name: str | None`
    :   The name of the marketing campaign.

    `clicks: str | None`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: float | None`
    :   Number of clicks on the music disc.

    `comments: float | None`
    :   Number of comments.

    `conversion: str | None`
    :   Number of conversions.

    `conversion_rate: str | None`
    :   Rate of conversions.

    `cost_per_1000_reached: str | None`
    :   Cost per 1000 unique users reached.

    `cost_per_conversion: str | None`
    :   Cost per conversion.

    `cost_per_result: str | None`
    :   Cost per result.

    `cost_per_secondary_goal_result: str | None`
    :   Cost per secondary goal result.

    `cpc: str | None`
    :   Cost per click.

    `cpm: str | None`
    :   Cost per thousand impressions.

    `ctr: str | None`
    :   Click-through rate.

    `follows: float | None`
    :   Number of follows.

    `frequency: str | None`
    :   Average number of times each person saw the ad.

    `impressions: str | None`
    :   Number of times the ad was displayed.

    `likes: float | None`
    :   Number of likes.

    `model_config`
    :   The type of the None singleton.

    `placement_type: str | None`
    :   Type of ad placement.

    `profile_visits: float | None`
    :   Number of profile visits.

    `reach: str | None`
    :   Total number of unique users reached.

    `real_time_app_install: float | None`
    :   Real-time app installations.

    `real_time_app_install_cost: float | None`
    :   Cost of real-time app installations.

    `real_time_conversion: str | None`
    :   Real-time conversions.

    `real_time_conversion_rate: str | None`
    :   Real-time conversion rate.

    `real_time_cost_per_conversion: str | None`
    :   Real-time cost per conversion.

    `real_time_cost_per_result: str | None`
    :   Real-time cost per result.

    `real_time_result: str | None`
    :   Real-time results.

    `real_time_result_rate: str | None`
    :   Real-time result rate.

    `result: str | None`
    :   Number of results.

    `result_rate: str | None`
    :   Rate of results.

    `secondary_goal_result: str | None`
    :   Results for secondary goals.

    `secondary_goal_result_rate: str | None`
    :   Rate of secondary goal results.

    `shares: float | None`
    :   Number of shares.

    `spend: str | None`
    :   Total amount of money spent.

    `stat_time_day: str | None`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: float | None`
    :   Number of video play actions.

    `video_views_p100: float | None`
    :   Number of times video was watched to 100%.

    `video_views_p25: float | None`
    :   Number of times video was watched to 25%.

    `video_views_p50: float | None`
    :   Number of times video was watched to 50%.

    `video_views_p75: float | None`
    :   Number of times video was watched to 75%.

    `video_watched_2s: float | None`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: float | None`
    :   Number of times video was watched for at least 6 seconds.

<a id="AdsSearchData"></a>

`AdsSearchData(**data: Any)`
:   Search result data for ads entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_format: str | None`
    :   The format of the ad

    `ad_id: int | None`
    :   The unique identifier of the ad

    `ad_name: str | None`
    :   The name of the ad

    `ad_text: str | None`
    :   The text content of the ad

    `adgroup_id: int | None`
    :   The unique identifier of the ad group

    `adgroup_name: str | None`
    :   The name of the ad group

    `advertiser_id: int | None`
    :   The unique identifier of the advertiser

    `campaign_id: int | None`
    :   The unique identifier of the campaign

    `campaign_name: str | None`
    :   The name of the campaign

    `create_time: str | None`
    :   The timestamp when the ad was created

    `landing_page_url: str | None`
    :   The URL of the landing page for the ad

    `model_config`
    :   The type of the None singleton.

    `modify_time: str | None`
    :   The timestamp when the ad was last modified

    `operation_status: str | None`
    :   The operational status of the ad

    `secondary_status: str | None`
    :   The secondary status of the ad

    `video_id: str | None`
    :   The unique identifier of the video

<a id="AdvertisersReportsDailySearchData"></a>

`AdvertisersReportsDailySearchData(**data: Any)`
:   Search result data for advertisers_reports_daily entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `advertiser_id: int | None`
    :   The unique identifier for the advertiser.

    `app_install: float | None`
    :   Number of app installations.

    `average_video_play: float | None`
    :   Average video play duration.

    `average_video_play_per_user: float | None`
    :   Average video play duration per user.

    `cash_spend: str | None`
    :   The amount of money spent in cash.

    `clicks: str | None`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: float | None`
    :   Number of clicks on the music disc.

    `comments: float | None`
    :   Number of comments.

    `cost_per_1000_reached: str | None`
    :   Cost per 1000 unique users reached.

    `cpc: str | None`
    :   Cost per click.

    `cpm: str | None`
    :   Cost per thousand impressions.

    `ctr: str | None`
    :   Click-through rate.

    `follows: float | None`
    :   Number of follows.

    `frequency: str | None`
    :   Average number of times each person saw the ad.

    `impressions: str | None`
    :   Number of times the ad was displayed.

    `likes: float | None`
    :   Number of likes.

    `model_config`
    :   The type of the None singleton.

    `profile_visits: float | None`
    :   Number of profile visits.

    `reach: str | None`
    :   Total number of unique users reached.

    `real_time_app_install: float | None`
    :   Real-time app installations.

    `real_time_app_install_cost: float | None`
    :   Cost of real-time app installations.

    `shares: float | None`
    :   Number of shares.

    `spend: str | None`
    :   Total amount of money spent.

    `stat_time_day: str | None`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: float | None`
    :   Number of video play actions.

    `video_views_p100: float | None`
    :   Number of times video was watched to 100%.

    `video_views_p25: float | None`
    :   Number of times video was watched to 25%.

    `video_views_p50: float | None`
    :   Number of times video was watched to 50%.

    `video_views_p75: float | None`
    :   Number of times video was watched to 75%.

    `video_watched_2s: float | None`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: float | None`
    :   Number of times video was watched for at least 6 seconds.

    `voucher_spend: str | None`
    :   Amount spent using vouchers.

<a id="AdvertisersSearchData"></a>

`AdvertisersSearchData(**data: Any)`
:   Search result data for advertisers entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: str | None`
    :   The physical address of the advertiser.

    `advertiser_account_type: str | None`
    :   The type of advertiser's account (e.g., individual, business).

    `advertiser_id: int | None`
    :   Unique identifier for the advertiser.

    `balance: float | None`
    :   The current balance in the advertiser's account.

    `brand: str | None`
    :   The brand name associated with the advertiser.

    `cellphone_number: str | None`
    :   The cellphone number of the advertiser.

    `company: str | None`
    :   The name of the company associated with the advertiser.

    `contacter: str | None`
    :   The contact person for the advertiser.

    `country: str | None`
    :   The country where the advertiser is located.

    `create_time: int | None`
    :   The timestamp when the advertiser account was created.

    `currency: str | None`
    :   The currency used for transactions in the account.

    `description: str | None`
    :   A brief description or bio of the advertiser or company.

    `display_timezone: str | None`
    :   The timezone for display purposes.

    `email: str | None`
    :   The email address associated with the advertiser.

    `industry: str | None`
    :   The industry or sector the advertiser operates in.

    `language: str | None`
    :   The preferred language of communication for the advertiser.

    `license_city: str | None`
    :   The city where the advertiser's license is registered.

    `license_no: str | None`
    :   The license number of the advertiser.

    `license_province: str | None`
    :   The province or state where the advertiser's license is registered.

    `license_url: str | None`
    :   The URL link to the advertiser's license documentation.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the advertiser or company.

    `promotion_area: str | None`
    :   The specific area or region where the advertiser focuses promotion.

    `promotion_center_city: str | None`
    :   The city at the center of the advertiser's promotion activities.

    `promotion_center_province: str | None`
    :   The province or state at the center of the advertiser's promotion activities.

    `rejection_reason: str | None`
    :   Reason for any advertisement rejection by the platform.

    `role: str | None`
    :   The role or position of the advertiser within the company.

    `status: str | None`
    :   The current status of the advertiser's account.

    `telephone_number: str | None`
    :   The telephone number of the advertiser.

    `timezone: str | None`
    :   The timezone setting for the advertiser's activities.

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

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdGroupsReportsDailySearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdGroupsSearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdsReportsDailySearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdsSearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdvertisersReportsDailySearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdvertisersSearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AudiencesSearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[CampaignsReportsDailySearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[CreativeAssetsImagesSearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[CreativeAssetsVideosSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupsReportsDailySearchResult"></a>

`AdGroupsReportsDailySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AdGroupsSearchResult"></a>

`AdGroupsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AdsReportsDailySearchResult"></a>

`AdsReportsDailySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AdsSearchResult"></a>

`AdsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AdvertisersReportsDailySearchResult"></a>

`AdvertisersReportsDailySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AdvertisersSearchResult"></a>

`AdvertisersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AudiencesSearchResult"></a>

`AudiencesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CampaignsReportsDailySearchResult"></a>

`CampaignsReportsDailySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CreativeAssetsImagesSearchResult"></a>

`CreativeAssetsImagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CreativeAssetsVideosSearchResult"></a>

`CreativeAssetsVideosSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AudiencesSearchData"></a>

`AudiencesSearchData(**data: Any)`
:   Search result data for audiences entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `audience_id: str | None`
    :   Unique identifier for the audience

    `audience_type: str | None`
    :   Type of audience

    `cover_num: int | None`
    :   Number of audience members covered

    `create_time: str | None`
    :   Timestamp indicating when the audience was created

    `is_valid: bool | None`
    :   Flag indicating if the audience data is valid

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the audience

    `shared: bool | None`
    :   Flag indicating if the audience is shared

<a id="CampaignsReportsDailySearchData"></a>

`CampaignsReportsDailySearchData(**data: Any)`
:   Search result data for campaigns_reports_daily entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_install: float | None`
    :   Number of app installations.

    `average_video_play: float | None`
    :   Average video play duration.

    `average_video_play_per_user: float | None`
    :   Average video play duration per user.

    `campaign_id: int | None`
    :   The unique identifier for the campaign.

    `campaign_name: str | None`
    :   The name of the marketing campaign.

    `clicks: str | None`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: float | None`
    :   Number of clicks on the music disc.

    `comments: float | None`
    :   Number of comments.

    `cost_per_1000_reached: str | None`
    :   Cost per 1000 unique users reached.

    `cpc: str | None`
    :   Cost per click.

    `cpm: str | None`
    :   Cost per thousand impressions.

    `ctr: str | None`
    :   Click-through rate.

    `follows: float | None`
    :   Number of follows.

    `frequency: str | None`
    :   Average number of times each person saw the ad.

    `impressions: str | None`
    :   Number of times the ad was displayed.

    `likes: float | None`
    :   Number of likes.

    `model_config`
    :   The type of the None singleton.

    `profile_visits: float | None`
    :   Number of profile visits.

    `reach: str | None`
    :   Total number of unique users reached.

    `real_time_app_install: float | None`
    :   Real-time app installations.

    `real_time_app_install_cost: float | None`
    :   Cost of real-time app installations.

    `shares: float | None`
    :   Number of shares.

    `spend: str | None`
    :   Total amount of money spent.

    `stat_time_day: str | None`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: float | None`
    :   Number of video play actions.

    `video_views_p100: float | None`
    :   Number of times video was watched to 100%.

    `video_views_p25: float | None`
    :   Number of times video was watched to 25%.

    `video_views_p50: float | None`
    :   Number of times video was watched to 50%.

    `video_views_p75: float | None`
    :   Number of times video was watched to 75%.

    `video_watched_2s: float | None`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: float | None`
    :   Number of times video was watched for at least 6 seconds.

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

    `advertiser_id: int | None`
    :   The unique identifier of the advertiser associated with the campaign

    `app_promotion_type: str | None`
    :   Type of app promotion being used in the campaign

    `bid_type: str | None`
    :   Type of bid strategy being used in the campaign

    `budget: float | None`
    :   Total budget allocated for the campaign

    `budget_mode: str | None`
    :   Mode in which the budget is being managed (e.g., daily, lifetime)

    `budget_optimize_on: bool | None`
    :   The metric or event that the budget optimization is based on

    `campaign_id: int | None`
    :   The unique identifier of the campaign

    `campaign_name: str | None`
    :   Name of the campaign for easy identification

    `campaign_type: str | None`
    :   Type of campaign (e.g., awareness, conversion)

    `create_time: str | None`
    :   Timestamp when the campaign was created

    `deep_bid_type: str | None`
    :   Advanced bid type used for campaign optimization

    `is_new_structure: bool | None`
    :   Flag indicating if the campaign utilizes a new campaign structure

    `is_search_campaign: bool | None`
    :   Flag indicating if the campaign is a search campaign

    `is_smart_performance_campaign: bool | None`
    :   Flag indicating if the campaign uses smart performance optimization

    `model_config`
    :   The type of the None singleton.

    `modify_time: str | None`
    :   Timestamp when the campaign was last modified

    `objective: str | None`
    :   The objective or goal of the campaign

    `objective_type: str | None`
    :   Type of objective selected for the campaign

    `operation_status: str | None`
    :   Current operational status of the campaign

    `optimization_goal: str | None`
    :   Specific goal to be optimized for in the campaign

    `rf_campaign_type: str | None`
    :   Type of RF (reach and frequency) campaign being run

    `roas_bid: float | None`
    :   Return on ad spend goal set for the campaign

    `secondary_status: str | None`
    :   Additional status information of the campaign

    `split_test_variable: str | None`
    :   Variable being tested in a split test campaign

<a id="CreativeAssetsImagesSearchData"></a>

`CreativeAssetsImagesSearchData(**data: Any)`
:   Search result data for creative_assets_images entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create_time: str | None`
    :   The timestamp when the image was created.

    `file_name: str | None`
    :   The name of the image file.

    `format: str | None`
    :   The format type of the image file.

    `height: int | None`
    :   The height dimension of the image.

    `image_id: str | None`
    :   The unique identifier for the image.

    `image_url: str | None`
    :   The URL to access the image.

    `model_config`
    :   The type of the None singleton.

    `modify_time: str | None`
    :   The timestamp when the image was last modified.

    `size: int | None`
    :   The size of the image file.

    `width: int | None`
    :   The width dimension of the image.

<a id="CreativeAssetsVideosSearchData"></a>

`CreativeAssetsVideosSearchData(**data: Any)`
:   Search result data for creative_assets_videos entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create_time: str | None`
    :   Timestamp when the video was created.

    `duration: float | None`
    :   Duration of the video in seconds.

    `file_name: str | None`
    :   Name of the video file.

    `format: str | None`
    :   Format of the video file.

    `height: int | None`
    :   Height of the video in pixels.

    `model_config`
    :   The type of the None singleton.

    `modify_time: str | None`
    :   Timestamp when the video was last modified.

    `size: int | None`
    :   Size of the video file in bytes.

    `video_cover_url: str | None`
    :   URL for the cover image of the video.

    `video_id: str | None`
    :   ID of the video.

    `width: int | None`
    :   Width of the video in pixels.

<a id="TiktokMarketingAuthConfig"></a>

`TiktokMarketingAuthConfig(**data: Any)`
:   OAuth Access Token
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   Your TikTok Marketing API access token

    `model_config`
    :   The type of the None singleton.

<a id="TiktokMarketingConnector"></a>

`TiktokMarketingConnector(auth_config: TiktokMarketingAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Tiktok-Marketing API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new tiktok-marketing connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., TiktokMarketingAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = TiktokMarketingConnector(auth_config=TiktokMarketingAuthConfig(access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = TiktokMarketingConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = TiktokMarketingConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'TiktokMarketingAuthConfig'", name: str | None = None, replication_config: "'TiktokMarketingReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config (same as local mode)
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Typed replication settings.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A TiktokMarketingConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await TiktokMarketingConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=TiktokMarketingAuthConfig(access_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await TiktokMarketingConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=TiktokMarketingAuthConfig(access_token="..."),
                replication_config=TiktokMarketingReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @TiktokMarketingConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @TiktokMarketingConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
        Args:
            update_docstring: When True, append connector capabilities to __doc__.
            max_output_chars: Max serialized output size before raising. Use None to disable.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.
        
        Example:
            connector = await TiktokMarketingConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            TiktokMarketingCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
        
        Returns:
            Typed response based on the operation
        
        Example:
            customer = await connector.execute(
                entity="customers",
                action="get",
                params=\{"id": "cus_123"\}
            )

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

<a id="TiktokMarketingReplicationConfig"></a>

`TiktokMarketingReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from TikTok Marketing.
    
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
    :   The start date in YYYY-MM-DD format. Any data before this date will not be replicated. If not set, defaults to 2016-09-01.