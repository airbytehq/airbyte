---
id: airbyte_agent_sdk-connectors-google_ads-index
title: airbyte_agent_sdk.connectors.google_ads.index
---

Module airbyte_agent_sdk.connectors.google_ads
==============================================
Google-Ads connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.google_ads.connector
* airbyte_agent_sdk.connectors.google_ads.connector_model
* airbyte_agent_sdk.connectors.google_ads.models
* airbyte_agent_sdk.connectors.google_ads.types

Classes
-------

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

<a id="GoogleAdsConnector"></a>

`GoogleAdsConnector(auth_config: GoogleAdsAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Google-Ads API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new google-ads connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., GoogleAdsAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = GoogleAdsConnector(auth_config=GoogleAdsAuthConfig(client_id="...", client_secret="...", refresh_token="...", developer_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = GoogleAdsConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = GoogleAdsConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'GoogleAdsAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'GoogleAdsReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A GoogleAdsConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await GoogleAdsConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GoogleAdsAuthConfig(client_id="...", client_secret="...", refresh_token="...", developer_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await GoogleAdsConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GoogleAdsAuthConfig(client_id="...", client_secret="...", refresh_token="...", developer_token="..."),
                replication_config=GoogleAdsReplicationConfig(customer_id="...", start_date="...", conversion_window_days="..."),
            )
        
            # With server-side OAuth:
            connector = await GoogleAdsConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=GoogleAdsReplicationConfig(customer_id="...", start_date="...", conversion_window_days="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'GoogleAdsReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await GoogleAdsConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Google-Ads Source",
                replication_config=GoogleAdsReplicationConfig(customer_id="...", start_date="...", conversion_window_days="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @GoogleAdsConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GoogleAdsConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await GoogleAdsConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            GoogleAdsCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'update', 'create', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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