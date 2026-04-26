---
id: airbyte_agent_sdk-connectors-google_ads-connector
title: airbyte_agent_sdk.connectors.google_ads.connector
---

Module airbyte_agent_sdk.connectors.google_ads.connector
========================================================
Google-Ads connector.

Classes
-------

<a id="AccessibleCustomersQuery"></a>

`AccessibleCustomersQuery(connector: GoogleAdsConnector)`
:   Query class for AccessibleCustomers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResult[AccessibleCustomersList]`
    :   Returns resource names of customers directly accessible by the user authenticating the call. No customer_id is required for this endpoint.
        
        Returns:
            AccessibleCustomersListResult

<a id="AccountsQuery"></a>

`AccountsQuery(connector: GoogleAdsConnector)`
:   Query class for Accounts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AccountsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult[AccountsSearchData]`
    :   Search accounts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AccountsSearchFilter):
        - customer_auto_tagging_enabled: Whether auto-tagging is enabled for the account
        - customer_call_reporting_setting_call_conversion_action: Call conversion action resource name
        - customer_call_reporting_setting_call_conversion_reporting_enabled: Whether call conversion reporting is enabled
        - customer_call_reporting_setting_call_reporting_enabled: Whether call reporting is enabled
        - customer_conversion_tracking_setting_conversion_tracking_id: Conversion tracking ID
        - customer_conversion_tracking_setting_cross_account_conversion_tracking_id: Cross-account conversion tracking ID
        - customer_currency_code: Currency code for the account (e.g., USD)
        - customer_descriptive_name: Descriptive name of the customer account
        - customer_final_url_suffix: URL suffix appended to final URLs
        - customer_has_partners_badge: Whether the account has a Google Partners badge
        - customer_id: Unique customer account ID
        - customer_manager: Whether this is a manager (MCC) account
        - customer_optimization_score: Optimization score for the account (0.0 to 1.0)
        - customer_optimization_score_weight: Weight of the optimization score
        - customer_pay_per_conversion_eligibility_failure_reasons: Reasons why pay-per-conversion is not eligible
        - customer_remarketing_setting_google_global_site_tag: Google global site tag snippet
        - customer_resource_name: Resource name of the customer
        - customer_test_account: Whether this is a test account
        - customer_time_zone: Time zone of the account
        - customer_tracking_url_template: Tracking URL template for the account
        - segments_date: Date segment for the report row
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AccountsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, customer_id: str, query: str | None = None, page_token: str | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta[list[Account], AccountsListResultMeta]`
    :   Retrieves customer account details using GAQL query.
        
        Args:
            query: Google Ads Query Language (GAQL) query
            page_token: Token for pagination
            page_size: Number of results per page (max 10000)
            customer_id: Google Ads customer ID (10 digits, no dashes)
            **kwargs: Additional parameters
        
        Returns:
            AccountsListResult

<a id="AdGroupAdLabelsQuery"></a>

`AdGroupAdLabelsQuery(connector: GoogleAdsConnector)`
:   Query class for AdGroupAdLabels entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdGroupAdLabelsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult[AdGroupAdLabelsSearchData]`
    :   Search ad_group_ad_labels records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdGroupAdLabelsSearchFilter):
        - ad_group_ad_ad_id: Ad ID
        - ad_group_ad_label_resource_name: Resource name of the ad group ad label
        - label_id: Label ID
        - label_name: Label name
        - label_resource_name: Resource name of the label
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdGroupAdLabelsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, customer_id: str, query: str | None = None, page_token: str | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta[list[AdGroupAdLabel], AdGroupAdLabelsListResultMeta]`
    :   Retrieves ad group ad label associations using GAQL query.
        
        Args:
            query: GAQL query for ad group ad labels
            page_token: Token for pagination
            page_size: Number of results per page (max 10000)
            customer_id: Google Ads customer ID (10 digits, no dashes)
            **kwargs: Additional parameters
        
        Returns:
            AdGroupAdLabelsListResult

<a id="AdGroupAdsQuery"></a>

`AdGroupAdsQuery(connector: GoogleAdsConnector)`
:   Query class for AdGroupAds entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdGroupAdsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult[AdGroupAdsSearchData]`
    :   Search ad_group_ads records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdGroupAdsSearchFilter):
        - ad_group_id: Parent ad group ID
        - ad_group_ad_ad_id: Ad ID
        - ad_group_ad_ad_name: Ad name
        - ad_group_ad_ad_type: Ad type
        - ad_group_ad_status: Ad group ad status (ENABLED, PAUSED, REMOVED)
        - ad_group_ad_ad_strength: Ad strength rating
        - ad_group_ad_ad_display_url: Display URL of the ad
        - ad_group_ad_ad_final_urls: Final URLs for the ad
        - ad_group_ad_ad_final_mobile_urls: Final mobile URLs for the ad
        - ad_group_ad_ad_final_url_suffix: Final URL suffix
        - ad_group_ad_ad_tracking_url_template: Tracking URL template
        - ad_group_ad_ad_resource_name: Resource name of the ad
        - ad_group_ad_ad_group: Ad group resource name
        - ad_group_ad_resource_name: Resource name of the ad group ad
        - ad_group_ad_labels: Labels applied to the ad group ad
        - ad_group_ad_policy_summary_approval_status: Policy approval status
        - ad_group_ad_policy_summary_review_status: Policy review status
        - segments_date: Date segment for the report row
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdGroupAdsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, customer_id: str, query: str | None = None, page_token: str | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta[list[AdGroupAd], AdGroupAdsListResultMeta]`
    :   Retrieves ad group ad data using GAQL query.
        
        Args:
            query: GAQL query for ad group ads
            page_token: Token for pagination
            page_size: Number of results per page (max 10000)
            customer_id: Google Ads customer ID (10 digits, no dashes)
            **kwargs: Additional parameters
        
        Returns:
            AdGroupAdsListResult

<a id="AdGroupLabelsQuery"></a>

`AdGroupLabelsQuery(connector: GoogleAdsConnector)`
:   Query class for AdGroupLabels entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdGroupLabelsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult[AdGroupLabelsSearchData]`
    :   Search ad_group_labels records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdGroupLabelsSearchFilter):
        - ad_group_id: Ad group ID
        - ad_group_label_resource_name: Resource name of the ad group label
        - label_id: Label ID
        - label_name: Label name
        - label_resource_name: Resource name of the label
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdGroupLabelsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, operations: list[AdGroupLabelsCreateParamsOperationsItem], customer_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.google_ads.models.AdGroupLabelMutateResponse`
    :   Creates an ad group-label association, applying an existing label to an ad group for organization and filtering.
        
        Args:
            operations: List of ad group label operations to perform
            customer_id: Google Ads customer ID (10 digits, no dashes)
            **kwargs: Additional parameters
        
        Returns:
            AdGroupLabelMutateResponse

    `list(self, customer_id: str, query: str | None = None, page_token: str | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta[list[AdGroupLabel], AdGroupLabelsListResultMeta]`
    :   Retrieves ad group label associations using GAQL query.
        
        Args:
            query: GAQL query for ad group labels
            page_token: Token for pagination
            page_size: Number of results per page (max 10000)
            customer_id: Google Ads customer ID (10 digits, no dashes)
            **kwargs: Additional parameters
        
        Returns:
            AdGroupLabelsListResult

<a id="AdGroupsQuery"></a>

`AdGroupsQuery(connector: GoogleAdsConnector)`
:   Query class for AdGroups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdGroupsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult[AdGroupsSearchData]`
    :   Search ad_groups records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdGroupsSearchFilter):
        - campaign_id: Parent campaign ID
        - ad_group_id: Ad group ID
        - ad_group_name: Ad group name
        - ad_group_status: Ad group status (ENABLED, PAUSED, REMOVED)
        - ad_group_type: Ad group type
        - ad_group_ad_rotation_mode: Ad rotation mode
        - ad_group_base_ad_group: Base ad group resource name
        - ad_group_campaign: Parent campaign resource name
        - ad_group_cpc_bid_micros: CPC bid in micros
        - ad_group_cpm_bid_micros: CPM bid in micros
        - ad_group_cpv_bid_micros: CPV bid in micros
        - ad_group_effective_target_cpa_micros: Effective target CPA in micros
        - ad_group_effective_target_cpa_source: Source of the effective target CPA
        - ad_group_effective_target_roas: Effective target ROAS
        - ad_group_effective_target_roas_source: Source of the effective target ROAS
        - ad_group_labels: Labels applied to the ad group
        - ad_group_resource_name: Resource name of the ad group
        - ad_group_target_cpa_micros: Target CPA in micros
        - ad_group_target_roas: Target ROAS
        - ad_group_tracking_url_template: Tracking URL template
        - metrics_cost_micros: Cost in micros
        - segments_date: Date segment for the report row
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdGroupsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, customer_id: str, query: str | None = None, page_token: str | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta[list[AdGroup], AdGroupsListResultMeta]`
    :   Retrieves ad group data using GAQL query.
        
        Args:
            query: GAQL query for ad groups
            page_token: Token for pagination
            page_size: Number of results per page (max 10000)
            customer_id: Google Ads customer ID (10 digits, no dashes)
            **kwargs: Additional parameters
        
        Returns:
            AdGroupsListResult

    `update(self, operations: list[AdGroupsUpdateParamsOperationsItem], customer_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.google_ads.models.AdGroupMutateResponse`
    :   Updates ad group properties such as status (enable/pause), name, or bid amounts using the Google Ads AdGroupService mutate endpoint.
        
        Args:
            operations: List of ad group operations to perform
            customer_id: Google Ads customer ID (10 digits, no dashes)
            **kwargs: Additional parameters
        
        Returns:
            AdGroupMutateResponse

<a id="CampaignLabelsQuery"></a>

`CampaignLabelsQuery(connector: GoogleAdsConnector)`
:   Query class for CampaignLabels entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignLabelsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult[CampaignLabelsSearchData]`
    :   Search campaign_labels records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignLabelsSearchFilter):
        - campaign_id: Campaign ID
        - campaign_label_resource_name: Resource name of the campaign label
        - label_id: Label ID
        - label_name: Label name
        - label_resource_name: Resource name of the label
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CampaignLabelsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, operations: list[CampaignLabelsCreateParamsOperationsItem], customer_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.google_ads.models.CampaignLabelMutateResponse`
    :   Creates a campaign-label association, applying an existing label to a campaign for organization and filtering.
        
        Args:
            operations: List of campaign label operations to perform
            customer_id: Google Ads customer ID (10 digits, no dashes)
            **kwargs: Additional parameters
        
        Returns:
            CampaignLabelMutateResponse

    `list(self, customer_id: str, query: str | None = None, page_token: str | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta[list[CampaignLabel], CampaignLabelsListResultMeta]`
    :   Retrieves campaign label associations using GAQL query.
        
        Args:
            query: GAQL query for campaign labels
            page_token: Token for pagination
            page_size: Number of results per page (max 10000)
            customer_id: Google Ads customer ID (10 digits, no dashes)
            **kwargs: Additional parameters
        
        Returns:
            CampaignLabelsListResult

<a id="CampaignsQuery"></a>

`CampaignsQuery(connector: GoogleAdsConnector)`
:   Query class for Campaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_ads.models.AirbyteSearchResult[CampaignsSearchData]`
    :   Search campaigns records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignsSearchFilter):
        - campaign_id: Campaign ID
        - campaign_name: Campaign name
        - campaign_status: Campaign status (ENABLED, PAUSED, REMOVED)
        - campaign_advertising_channel_type: Advertising channel type (SEARCH, DISPLAY, etc.)
        - campaign_advertising_channel_sub_type: Advertising channel sub-type
        - campaign_bidding_strategy: Bidding strategy resource name
        - campaign_bidding_strategy_type: Bidding strategy type
        - campaign_campaign_budget: Campaign budget resource name
        - campaign_budget_amount_micros: Campaign budget amount in micros
        - campaign_start_date: Campaign start date
        - campaign_end_date: Campaign end date
        - campaign_serving_status: Campaign serving status
        - campaign_resource_name: Resource name of the campaign
        - campaign_labels: Labels applied to the campaign
        - campaign_network_settings_target_google_search: Whether targeting Google Search
        - campaign_network_settings_target_search_network: Whether targeting search network
        - campaign_network_settings_target_content_network: Whether targeting content network
        - campaign_network_settings_target_partner_search_network: Whether targeting partner search network
        - metrics_clicks: Number of clicks
        - metrics_ctr: Click-through rate
        - metrics_conversions: Number of conversions
        - metrics_conversions_value: Total conversions value
        - metrics_cost_micros: Cost in micros
        - metrics_impressions: Number of impressions
        - metrics_average_cpc: Average cost per click
        - metrics_average_cpm: Average cost per thousand impressions
        - metrics_interactions: Number of interactions
        - segments_date: Date segment for the report row
        - segments_hour: Hour segment
        - segments_ad_network_type: Ad network type segment
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CampaignsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, customer_id: str, query: str | None = None, page_token: str | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_ads.models.GoogleAdsExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]`
    :   Retrieves campaign data using GAQL query.
        
        Args:
            query: GAQL query for campaigns
            page_token: Token for pagination
            page_size: Number of results per page (max 10000)
            customer_id: Google Ads customer ID (10 digits, no dashes)
            **kwargs: Additional parameters
        
        Returns:
            CampaignsListResult

    `update(self, operations: list[CampaignsUpdateParamsOperationsItem], customer_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.google_ads.models.CampaignMutateResponse`
    :   Updates campaign properties such as status (enable/pause), name, or other mutable fields using the Google Ads CampaignService mutate endpoint.
        
        Args:
            operations: List of campaign operations to perform
            customer_id: Google Ads customer ID (10 digits, no dashes)
            **kwargs: Additional parameters
        
        Returns:
            CampaignMutateResponse

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

<a id="LabelsQuery"></a>

`LabelsQuery(connector: GoogleAdsConnector)`
:   Query class for Labels entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, operations: list[LabelsCreateParamsOperationsItem], customer_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.google_ads.models.LabelMutateResponse`
    :   Creates a new label that can be applied to campaigns, ad groups, or ads for organization and reporting purposes.
        
        Args:
            operations: List of label operations to perform
            customer_id: Google Ads customer ID (10 digits, no dashes)
            **kwargs: Additional parameters
        
        Returns:
            LabelMutateResponse