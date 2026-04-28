---
id: airbyte_agent_sdk-connectors-linkedin_ads-connector
title: airbyte_agent_sdk.connectors.linkedin_ads.connector
---

Module airbyte_agent_sdk.connectors.linkedin_ads.connector
==========================================================
Linkedin-Ads connector.

Classes
-------

<a id="AccountUsersQuery"></a>

`AccountUsersQuery(connector: LinkedinAdsConnector)`
:   Query class for AccountUsers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AccountUsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AccountUsersSearchData]`
    :   Search account_users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AccountUsersSearchFilter):
        - account: Associated account URN
        - user: User URN
        - role: User role in the account
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AccountUsersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, q: str, accounts: str, count: int | None = None, start: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[AccountUser], AccountUsersListResultMeta]`
    :   Returns a list of users associated with ad accounts
        
        Args:
            q: Parameter q
            accounts: Account URN, e.g. urn:li:sponsoredAccount:123456
            count: Number of items per page
            start: Offset for pagination
            **kwargs: Additional parameters
        
        Returns:
            AccountUsersListResult

<a id="AccountsQuery"></a>

`AccountsQuery(connector: LinkedinAdsConnector)`
:   Query class for Accounts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AccountsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AccountsSearchData]`
    :   Search accounts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AccountsSearchFilter):
        - id: Unique account identifier
        - name: Account name
        - currency: Currency code used by the account
        - status: Account status
        - type_: Account type
        - reference: Reference organization URN
        - test: Whether this is a test account
        - notified_on_campaign_optimization: Flag for notifications on campaign optimization
        - notified_on_creative_approval: Flag for notifications on creative approval
        - notified_on_creative_rejection: Flag for notifications on creative rejection
        - notified_on_end_of_campaign: Flag for notifications on end of campaign
        - notified_on_new_features_enabled: Flag for notifications on new features
        - serving_statuses: List of serving statuses
        - version: Version information
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.Account`
    :   Get a single ad account by ID
        
        Args:
            id: Ad account ID
            **kwargs: Additional parameters
        
        Returns:
            Account

    `list(self, q: str, page_size: int | None = None, page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[Account], AccountsListResultMeta]`
    :   Returns a list of ad accounts the authenticated user has access to
        
        Args:
            q: Parameter q
            page_size: Number of items per page
            page_token: Token for the next page of results
            **kwargs: Additional parameters
        
        Returns:
            AccountsListResult

<a id="AdCampaignAnalyticsQuery"></a>

`AdCampaignAnalyticsQuery(connector: LinkedinAdsConnector)`
:   Query class for AdCampaignAnalytics entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdCampaignAnalyticsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdCampaignAnalyticsSearchData]`
    :   Search ad_campaign_analytics records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdCampaignAnalyticsSearchFilter):
        - impressions: Number of times the ad was shown
        - clicks: Number of clicks on the ad
        - cost_in_local_currency: Total cost in the accounts local currency
        - cost_in_usd: Total cost in USD
        - likes: Number of likes
        - shares: Number of shares
        - comments: Number of comments
        - reactions: Number of reactions
        - follows: Number of follows
        - total_engagements: Total number of engagements
        - landing_page_clicks: Number of landing page clicks
        - company_page_clicks: Number of company page clicks
        - external_website_conversions: Number of conversions on external websites
        - external_website_post_click_conversions: Post-click conversions on external websites
        - external_website_post_view_conversions: Post-view conversions on external websites
        - conversion_value_in_local_currency: Conversion value in local currency
        - approximate_member_reach: Approximate unique member reach
        - card_clicks: Number of carousel card clicks
        - card_impressions: Number of carousel card impressions
        - video_starts: Number of video starts
        - video_views: Number of video views
        - video_first_quartile_completions: Number of times video played to 25%
        - video_midpoint_completions: Number of times video played to 50%
        - video_third_quartile_completions: Number of times video played to 75%
        - video_completions: Number of times video played to 100%
        - full_screen_plays: Number of full screen video plays
        - one_click_leads: Number of one-click leads
        - one_click_lead_form_opens: Number of one-click lead form opens
        - other_engagements: Number of other engagements
        - ad_unit_clicks: Number of ad unit clicks
        - action_clicks: Number of action clicks
        - text_url_clicks: Number of text URL clicks
        - comment_likes: Number of comment likes
        - sends: Number of sends (InMail)
        - opens: Number of opens (InMail)
        - download_clicks: Number of download clicks
        - pivot_values: Pivot values (URNs) for this analytics record
        - start_date: Start date of the ad analytics data
        - end_date: End date of the ad analytics data
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdCampaignAnalyticsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, q: str, pivot: str, time_granularity: str, date_range: str, campaigns: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult[list[AdAnalyticsRecord]]`
    :   Returns ad analytics data pivoted by campaign. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by campaign.
        
        
        Args:
            q: Parameter q
            pivot: Pivot dimension for analytics grouping
            time_granularity: Time granularity for analytics data
            date_range: Date range in LinkedIn format, e.g. (start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31))
            campaigns: List of campaign URNs, e.g. List(urn%3Ali%3AsponsoredCampaign%3A123)
            fields: Comma-separated list of metric fields to return
            **kwargs: Additional parameters
        
        Returns:
            AdCampaignAnalyticsListResult

<a id="AdCreativeAnalyticsQuery"></a>

`AdCreativeAnalyticsQuery(connector: LinkedinAdsConnector)`
:   Query class for AdCreativeAnalytics entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdCreativeAnalyticsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdCreativeAnalyticsSearchData]`
    :   Search ad_creative_analytics records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdCreativeAnalyticsSearchFilter):
        - impressions: Number of times the ad was shown
        - clicks: Number of clicks on the ad
        - cost_in_local_currency: Total cost in the accounts local currency
        - cost_in_usd: Total cost in USD
        - likes: Number of likes
        - shares: Number of shares
        - comments: Number of comments
        - reactions: Number of reactions
        - follows: Number of follows
        - total_engagements: Total number of engagements
        - landing_page_clicks: Number of landing page clicks
        - company_page_clicks: Number of company page clicks
        - external_website_conversions: Number of conversions on external websites
        - external_website_post_click_conversions: Post-click conversions on external websites
        - external_website_post_view_conversions: Post-view conversions on external websites
        - conversion_value_in_local_currency: Conversion value in local currency
        - approximate_member_reach: Approximate unique member reach
        - card_clicks: Number of carousel card clicks
        - card_impressions: Number of carousel card impressions
        - video_starts: Number of video starts
        - video_views: Number of video views
        - video_first_quartile_completions: Number of times video played to 25%
        - video_midpoint_completions: Number of times video played to 50%
        - video_third_quartile_completions: Number of times video played to 75%
        - video_completions: Number of times video played to 100%
        - full_screen_plays: Number of full screen video plays
        - one_click_leads: Number of one-click leads
        - one_click_lead_form_opens: Number of one-click lead form opens
        - other_engagements: Number of other engagements
        - ad_unit_clicks: Number of ad unit clicks
        - action_clicks: Number of action clicks
        - text_url_clicks: Number of text URL clicks
        - comment_likes: Number of comment likes
        - sends: Number of sends (InMail)
        - opens: Number of opens (InMail)
        - download_clicks: Number of download clicks
        - pivot_values: Pivot values (URNs) for this analytics record
        - start_date: Start date of the ad analytics data
        - end_date: End date of the ad analytics data
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdCreativeAnalyticsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, q: str, pivot: str, time_granularity: str, date_range: str, creatives: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult[list[AdAnalyticsRecord]]`
    :   Returns ad analytics data pivoted by creative. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by creative.
        
        
        Args:
            q: Parameter q
            pivot: Pivot dimension for analytics grouping
            time_granularity: Time granularity for analytics data
            date_range: Date range in LinkedIn format, e.g. (start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31))
            creatives: List of creative URNs, e.g. List(urn%3Ali%3AsponsoredCreative%3A123)
            fields: Comma-separated list of metric fields to return
            **kwargs: Additional parameters
        
        Returns:
            AdCreativeAnalyticsListResult

<a id="CampaignGroupsQuery"></a>

`CampaignGroupsQuery(connector: LinkedinAdsConnector)`
:   Query class for CampaignGroups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignGroupsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[CampaignGroupsSearchData]`
    :   Search campaign_groups records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignGroupsSearchFilter):
        - id: Unique campaign group identifier
        - name: Campaign group name
        - account: Associated account URN
        - status: Campaign group status
        - test: Whether this is a test campaign group
        - backfilled: Whether the campaign group is backfilled
        - total_budget: Total budget for the campaign group
        - run_schedule: Campaign group run schedule
        - serving_statuses: List of serving statuses
        - allowed_campaign_types: Types of campaigns allowed in this group
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CampaignGroupsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, account_id: str, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.CampaignGroup`
    :   Get a single campaign group by ID
        
        Args:
            account_id: Ad account ID
            id: Campaign group ID
            **kwargs: Additional parameters
        
        Returns:
            CampaignGroup

    `list(self, account_id: str, q: str, page_size: int | None = None, page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[CampaignGroup], CampaignGroupsListResultMeta]`
    :   Returns a list of campaign groups for an ad account
        
        Args:
            account_id: Ad account ID
            q: Parameter q
            page_size: Number of items per page
            page_token: Token for the next page of results
            **kwargs: Additional parameters
        
        Returns:
            CampaignGroupsListResult

<a id="CampaignsQuery"></a>

`CampaignsQuery(connector: LinkedinAdsConnector)`
:   Query class for Campaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[CampaignsSearchData]`
    :   Search campaigns records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignsSearchFilter):
        - id: Unique campaign identifier
        - name: Campaign name
        - account: Associated account URN
        - campaign_group: Parent campaign group URN
        - status: Campaign status
        - type_: Campaign type
        - cost_type: Cost type (CPC CPM etc)
        - format: Campaign ad format
        - objective_type: Campaign objective type
        - optimization_target_type: Optimization target type
        - creative_selection: Creative selection mode
        - pacing_strategy: Budget pacing strategy
        - audience_expansion_enabled: Whether audience expansion is enabled
        - offsite_delivery_enabled: Whether offsite delivery is enabled
        - story_delivery_enabled: Whether story delivery is enabled
        - test: Whether this is a test campaign
        - associated_entity: Associated entity URN
        - daily_budget: Daily budget configuration
        - total_budget: Total budget configuration
        - unit_cost: Cost per unit (bid amount)
        - run_schedule: Campaign run schedule
        - locale: Campaign locale settings
        - serving_statuses: List of serving statuses
        - version: Version information
        
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

    `get(self, account_id: str, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.Campaign`
    :   Get a single campaign by ID
        
        Args:
            account_id: Ad account ID
            id: Campaign ID
            **kwargs: Additional parameters
        
        Returns:
            Campaign

    `list(self, account_id: str, q: str, page_size: int | None = None, page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]`
    :   Returns a list of campaigns for an ad account
        
        Args:
            account_id: Ad account ID
            q: Parameter q
            page_size: Number of items per page
            page_token: Token for the next page of results
            **kwargs: Additional parameters
        
        Returns:
            CampaignsListResult

<a id="ConversionsQuery"></a>

`ConversionsQuery(connector: LinkedinAdsConnector)`
:   Query class for Conversions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ConversionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[ConversionsSearchData]`
    :   Search conversions records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ConversionsSearchFilter):
        - id: Unique conversion identifier
        - name: Conversion name
        - account: Associated account URN
        - type_: Conversion type
        - attribution_type: Attribution type for the conversion
        - enabled: Whether the conversion tracking is enabled
        - created: Creation timestamp (epoch milliseconds)
        - last_modified: Last modification timestamp (epoch milliseconds)
        - post_click_attribution_window_size: Post-click attribution window size in days
        - view_through_attribution_window_size: View-through attribution window size in days
        - campaigns: Related campaign URNs
        - associated_campaigns: Associated campaigns
        - image_pixel_tag: Image pixel tracking tag
        - value: Conversion value
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ConversionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.Conversion`
    :   Get a single conversion rule by ID
        
        Args:
            id: Conversion ID
            **kwargs: Additional parameters
        
        Returns:
            Conversion

    `list(self, q: str, account: str, count: int | None = None, start: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[Conversion], ConversionsListResultMeta]`
    :   Returns a list of conversion rules for an ad account
        
        Args:
            q: Parameter q
            account: Account URN, e.g. urn:li:sponsoredAccount:123456
            count: Number of items per page
            start: Offset for pagination
            **kwargs: Additional parameters
        
        Returns:
            ConversionsListResult

<a id="CreativesQuery"></a>

`CreativesQuery(connector: LinkedinAdsConnector)`
:   Query class for Creatives entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CreativesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[CreativesSearchData]`
    :   Search creatives records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CreativesSearchFilter):
        - id: Unique creative identifier
        - name: Creative name
        - account: Associated account URN
        - campaign: Parent campaign URN
        - intended_status: Intended creative status
        - is_serving: Whether the creative is currently serving
        - is_test: Whether this is a test creative
        - created_at: Creation timestamp (epoch milliseconds)
        - created_by: URN of the user who created the creative
        - last_modified_at: Last modification timestamp (epoch milliseconds)
        - last_modified_by: URN of the user who last modified the creative
        - content: Creative content configuration
        - serving_hold_reasons: Reasons for holding creative from serving
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CreativesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, account_id: str, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.Creative`
    :   Get a single creative by ID
        
        Args:
            account_id: Ad account ID
            id: Creative ID
            **kwargs: Additional parameters
        
        Returns:
            Creative

    `list(self, account_id: str, q: str, page_size: int | None = None, page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[Creative], CreativesListResultMeta]`
    :   Returns a list of creatives for an ad account
        
        Args:
            account_id: Ad account ID
            q: Parameter q
            page_size: Number of items per page
            page_token: Token for the next page of results
            **kwargs: Additional parameters
        
        Returns:
            CreativesListResult

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