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
    :   Associated account URN

    `model_config`
    :   The type of the None singleton.

    `role: str | None`
    :   User role in the account

    `user: str | None`
    :   User URN

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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'LinkedinAdsAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'LinkedinAdsReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Supports two authentication modes:
        1. Direct credentials: Provide `auth_config` with typed credentials
        2. Server-side OAuth: Provide `server_side_oauth_secret_id` from OAuth flow
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config. Required unless using server_side_oauth_secret_id.
            server_side_oauth_secret_id: OAuth secret ID from get_consent_url redirect.
                When provided, auth_config is not required.
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Typed replication settings.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A LinkedinAdsConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await LinkedinAdsConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=LinkedinAdsAuthConfig(refresh_token="...", client_id="...", client_secret="..."),
            )
        
            # With replication config (required for this connector):
            connector = await LinkedinAdsConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=LinkedinAdsAuthConfig(refresh_token="...", client_id="...", client_secret="..."),
                replication_config=LinkedinAdsReplicationConfig(start_date="..."),
            )
        
            # With server-side OAuth:
            connector = await LinkedinAdsConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=LinkedinAdsReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'LinkedinAdsReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Initiate server-side OAuth flow with auto-source creation.
        
        Returns a consent URL where the end user should be redirected to grant access.
        After completing consent, the source is automatically created and the user is
        redirected to your redirect_url with a `connector_id` query parameter.
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            redirect_url: URL where users will be redirected after OAuth consent.
                After consent, user arrives at: redirect_url?connector_id=...
            name: Optional name for the source. Defaults to connector name + workspace_name.
            replication_config: Typed replication settings. Merged with OAuth credentials.
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            The OAuth consent URL
        
        Example:
            consent_url = await LinkedinAdsConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Linkedin-Ads Source",
                replication_config=LinkedinAdsReplicationConfig(start_date="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @LinkedinAdsConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @LinkedinAdsConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await LinkedinAdsConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

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

    `execute(self, entity: str, action: "Literal['list', 'get', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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