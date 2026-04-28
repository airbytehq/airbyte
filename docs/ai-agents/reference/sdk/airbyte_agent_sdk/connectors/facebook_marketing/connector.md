---
id: airbyte_agent_sdk-connectors-facebook_marketing-connector
title: airbyte_agent_sdk.connectors.facebook_marketing.connector
---

Module airbyte_agent_sdk.connectors.facebook_marketing.connector
================================================================
Facebook-Marketing connector.

Classes
-------

<a id="AdAccountQuery"></a>

`AdAccountQuery(connector: FacebookMarketingConnector)`
:   Query class for AdAccount entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdAccountSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[AdAccountSearchData]`
    :   Search ad_account records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdAccountSearchFilter):
        - id: Ad account ID
        - account_id: Ad account ID (numeric)
        - name: Ad account name
        - balance: Current balance of the ad account
        - currency: Currency used by the ad account
        - account_status: Account status
        - amount_spent: Total amount spent
        - business_name: Business name
        - created_time: Account creation time
        - spend_cap: Spend cap
        - timezone_name: Timezone name
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdAccountSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, account_id: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.AdAccount`
    :   Returns information about the specified ad account including balance and currency
        
        Args:
            account_id: The Facebook Ad Account ID (without act_ prefix)
            fields: Comma-separated list of fields to return
            **kwargs: Additional parameters
        
        Returns:
            AdAccount

<a id="AdAccountsQuery"></a>

`AdAccountsQuery(connector: FacebookMarketingConnector)`
:   Query class for AdAccounts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdAccountsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[AdAccountsSearchData]`
    :   Search ad_accounts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdAccountsSearchFilter):
        - id: Ad account ID
        - account_id: Ad account ID (numeric)
        - name: Ad account name
        - balance: Current balance of the ad account
        - currency: Currency used by the ad account
        - account_status: Account status
        - amount_spent: Total amount spent
        - business_name: Business name
        - created_time: Account creation time
        - spend_cap: Spend cap
        - timezone_name: Timezone name
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdAccountsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, fields: str | None = None, limit: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[AdAccountListItem], AdAccountsListResultMeta]`
    :   Returns a list of ad accounts associated with the current user
        
        Args:
            fields: Comma-separated list of fields to return
            limit: Maximum number of results to return
            after: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            AdAccountsListResult

<a id="AdCreativesQuery"></a>

`AdCreativesQuery(connector: FacebookMarketingConnector)`
:   Query class for AdCreatives entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdCreativesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[AdCreativesSearchData]`
    :   Search ad_creatives records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdCreativesSearchFilter):
        - id: Ad Creative ID
        - name: Ad Creative name
        - account_id: Ad account ID
        - body: Ad body text
        - title: Ad title
        - status: Creative status
        - image_url: Image URL
        - thumbnail_url: Thumbnail URL
        - link_url: Link URL
        - call_to_action_type: Call to action type
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdCreativesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, account_id: str, fields: str | None = None, limit: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[AdCreative], AdCreativesListResultMeta]`
    :   Returns a list of ad creatives for the specified ad account
        
        Args:
            account_id: The Facebook Ad Account ID (without act_ prefix)
            fields: Comma-separated list of fields to return
            limit: Maximum number of results to return
            after: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            AdCreativesListResult

<a id="AdLibraryQuery"></a>

`AdLibraryQuery(connector: FacebookMarketingConnector)`
:   Query class for AdLibrary entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, ad_reached_countries: str, search_terms: str | None = None, search_page_ids: str | None = None, ad_type: str | None = None, ad_active_status: str | None = None, ad_delivery_date_min: str | None = None, ad_delivery_date_max: str | None = None, bylines: str | None = None, languages: str | None = None, media_type: str | None = None, publisher_platforms: str | None = None, search_type: str | None = None, unmask_removed_content: bool | None = None, fields: str | None = None, limit: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[AdLibraryAd], AdLibraryListResultMeta]`
    :   Search the Facebook Ad Library for ads about social issues, elections or politics, and ads delivered to the UK or EU. Returns archived ads matching the specified search criteria including ad creative content, delivery dates, spend ranges, and demographic reach data.
        
        Args:
            ad_reached_countries: Search by ISO country code to return ads that reached specific countries. Use ALL to search all countries.
            search_terms: The terms to search for. Blank space is treated as logical AND. Limit of 100 characters.
            search_page_ids: Search for ads by specific Facebook Page IDs (comma-separated, up to 10)
            ad_type: Filter by ad type category
            ad_active_status: Filter by ad active status
            ad_delivery_date_min: Search for ads delivered after this date (inclusive, YYYY-MM-DD)
            ad_delivery_date_max: Search for ads delivered before this date (inclusive, YYYY-MM-DD)
            bylines: Filter by paid-for-by disclaimer byline (JSON array of strings). Available only for POLITICAL_AND_ISSUE_ADS.
            languages: Filter by language codes (ISO 639-1 JSON array, e.g. "['en','es']")
            media_type: Filter by media type in the ad
            publisher_platforms: Filter by Meta platform where the ad appeared (JSON array)
            search_type: Type of search to use for search_terms
            unmask_removed_content: Whether to reveal content removed for violating standards
            fields: Comma-separated list of fields to return
            limit: Maximum number of results to return
            after: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            AdLibraryListResult

<a id="AdSetsQuery"></a>

`AdSetsQuery(connector: FacebookMarketingConnector)`
:   Query class for AdSets entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdSetsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[AdSetsSearchData]`
    :   Search ad_sets records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdSetsSearchFilter):
        - id: Ad Set ID
        - name: Ad Set name
        - account_id: Ad account ID
        - campaign_id: Parent campaign ID
        - effective_status: Effective status
        - daily_budget: Daily budget
        - lifetime_budget: Lifetime budget
        - budget_remaining: Remaining budget
        - bid_amount: Bid amount
        - bid_strategy: Bid strategy
        - created_time: Ad set creation time
        - start_time: Ad set start time
        - end_time: Ad set end time
        - updated_time: Last update time
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdSetsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, account_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.AdSetCreateResponse`
    :   Creates a new ad set in the specified ad account
        
        Args:
            account_id: The Facebook Ad Account ID (without act_ prefix)
            **kwargs: Additional parameters
        
        Returns:
            AdSetCreateResponse

    `get(self, adset_id: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.AdSet`
    :   Returns a single ad set by ID
        
        Args:
            adset_id: The ad set ID
            fields: Comma-separated list of fields to return
            **kwargs: Additional parameters
        
        Returns:
            AdSet

    `list(self, account_id: str, fields: str | None = None, limit: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[AdSet], AdSetsListResultMeta]`
    :   Returns a list of ad sets for the specified ad account
        
        Args:
            account_id: The Facebook Ad Account ID (without act_ prefix)
            fields: Comma-separated list of fields to return
            limit: Maximum number of results to return
            after: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            AdSetsListResult

    `update(self, adset_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.UpdateResponse`
    :   Updates an existing ad set
        
        Args:
            adset_id: The ad set ID
            **kwargs: Additional parameters
        
        Returns:
            UpdateResponse

<a id="AdsInsightsQuery"></a>

`AdsInsightsQuery(connector: FacebookMarketingConnector)`
:   Query class for AdsInsights entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdsInsightsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[AdsInsightsSearchData]`
    :   Search ads_insights records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdsInsightsSearchFilter):
        - account_id: Ad account ID
        - account_name: Ad account name
        - campaign_id: Campaign ID
        - campaign_name: Campaign name
        - adset_id: Ad set ID
        - adset_name: Ad set name
        - ad_id: Ad ID
        - ad_name: Ad name
        - clicks: Number of clicks
        - impressions: Number of impressions
        - reach: Number of unique people reached
        - spend: Amount spent
        - cpc: Cost per click
        - cpm: Cost per 1000 impressions
        - ctr: Click-through rate
        - date_start: Start date of the reporting period
        - date_stop: End date of the reporting period
        - actions: Total number of actions taken
        - action_values: Action values taken on the ad
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdsInsightsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, account_id: str, fields: str | None = None, date_preset: str | None = None, time_range: str | None = None, level: str | None = None, time_increment: str | None = None, limit: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[AdsInsight], AdsInsightsListResultMeta]`
    :   Returns performance insights for the specified ad account
        
        Args:
            account_id: The Facebook Ad Account ID (without act_ prefix)
            fields: Comma-separated list of fields to return
            date_preset: Predefined date range
            time_range: Time range as JSON object with since and until dates (YYYY-MM-DD)
            level: Level of aggregation
            time_increment: Number of days (1-90) to aggregate data over, or 'monthly' for monthly aggregation, or 'all_days' for daily breakdown. Use time_increment=1 to get daily insights data.
            limit: Maximum number of results to return
            after: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            AdsInsightsListResult

<a id="AdsQuery"></a>

`AdsQuery(connector: FacebookMarketingConnector)`
:   Query class for Ads entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[AdsSearchData]`
    :   Search ads records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdsSearchFilter):
        - id: Ad ID
        - name: Ad name
        - account_id: Ad account ID
        - adset_id: Parent ad set ID
        - campaign_id: Parent campaign ID
        - status: Ad status
        - effective_status: Effective status
        - created_time: Ad creation time
        - updated_time: Last update time
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, account_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.AdCreateResponse`
    :   Creates a new ad in the specified ad account. Note - requires a Facebook Page to be connected to the ad account.
        
        Args:
            account_id: The Facebook Ad Account ID (without act_ prefix)
            **kwargs: Additional parameters
        
        Returns:
            AdCreateResponse

    `get(self, ad_id: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.Ad`
    :   Returns a single ad by ID
        
        Args:
            ad_id: The ad ID
            fields: Comma-separated list of fields to return
            **kwargs: Additional parameters
        
        Returns:
            Ad

    `list(self, account_id: str, fields: str | None = None, limit: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[Ad], AdsListResultMeta]`
    :   Returns a list of ads for the specified ad account
        
        Args:
            account_id: The Facebook Ad Account ID (without act_ prefix)
            fields: Comma-separated list of fields to return
            limit: Maximum number of results to return
            after: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            AdsListResult

    `update(self, ad_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.UpdateResponse`
    :   Updates an existing ad
        
        Args:
            ad_id: The ad ID
            **kwargs: Additional parameters
        
        Returns:
            UpdateResponse

<a id="CampaignsQuery"></a>

`CampaignsQuery(connector: FacebookMarketingConnector)`
:   Query class for Campaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[CampaignsSearchData]`
    :   Search campaigns records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignsSearchFilter):
        - id: Campaign ID
        - name: Campaign name
        - account_id: Ad account ID
        - status: Campaign status
        - effective_status: Effective status
        - objective: Campaign objective
        - daily_budget: Daily budget in account currency
        - lifetime_budget: Lifetime budget
        - budget_remaining: Remaining budget
        - created_time: Campaign creation time
        - start_time: Campaign start time
        - stop_time: Campaign stop time
        - updated_time: Last update time
        
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

    `create(self, account_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.CampaignCreateResponse`
    :   Creates a new ad campaign in the specified ad account
        
        Args:
            account_id: The Facebook Ad Account ID (without act_ prefix)
            **kwargs: Additional parameters
        
        Returns:
            CampaignCreateResponse

    `get(self, campaign_id: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.Campaign`
    :   Returns a single campaign by ID
        
        Args:
            campaign_id: The campaign ID
            fields: Comma-separated list of fields to return
            **kwargs: Additional parameters
        
        Returns:
            Campaign

    `list(self, account_id: str, fields: str | None = None, limit: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]`
    :   Returns a list of campaigns for the specified ad account
        
        Args:
            account_id: The Facebook Ad Account ID (without act_ prefix)
            fields: Comma-separated list of fields to return
            limit: Maximum number of results to return
            after: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            CampaignsListResult

    `update(self, campaign_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.UpdateResponse`
    :   Updates an existing ad campaign
        
        Args:
            campaign_id: The campaign ID
            **kwargs: Additional parameters
        
        Returns:
            UpdateResponse

<a id="CurrentUserQuery"></a>

`CurrentUserQuery(connector: FacebookMarketingConnector)`
:   Query class for CurrentUser entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.CurrentUser`
    :   Returns information about the current user associated with the access token
        
        Args:
            fields: Comma-separated list of fields to return
            **kwargs: Additional parameters
        
        Returns:
            CurrentUser

<a id="CustomConversionsQuery"></a>

`CustomConversionsQuery(connector: FacebookMarketingConnector)`
:   Query class for CustomConversions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CustomConversionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[CustomConversionsSearchData]`
    :   Search custom_conversions records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CustomConversionsSearchFilter):
        - id: Custom Conversion ID
        - name: Custom Conversion name
        - account_id: Ad account ID
        - description: Description
        - custom_event_type: Custom event type
        - creation_time: Creation time
        - first_fired_time: First fired time
        - last_fired_time: Last fired time
        - is_archived: Whether the conversion is archived
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CustomConversionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, account_id: str, fields: str | None = None, limit: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[CustomConversion], CustomConversionsListResultMeta]`
    :   Returns a list of custom conversions for the specified ad account
        
        Args:
            account_id: The Facebook Ad Account ID (without act_ prefix)
            fields: Comma-separated list of fields to return
            limit: Maximum number of results to return
            after: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            CustomConversionsListResult

<a id="FacebookMarketingConnector"></a>

`FacebookMarketingConnector(auth_config: FacebookMarketingAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Facebook-Marketing API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new facebook-marketing connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., FacebookMarketingAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = FacebookMarketingConnector(auth_config=FacebookMarketingAuthConfig(access_token="...", client_id="...", client_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = FacebookMarketingConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = FacebookMarketingConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'FacebookMarketingAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'FacebookMarketingReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A FacebookMarketingConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await FacebookMarketingConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=FacebookMarketingAuthConfig(access_token="...", client_id="...", client_secret="..."),
            )
        
            # With replication config (required for this connector):
            connector = await FacebookMarketingConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=FacebookMarketingAuthConfig(access_token="...", client_id="...", client_secret="..."),
                replication_config=FacebookMarketingReplicationConfig(account_ids="..."),
            )
        
            # With server-side OAuth:
            connector = await FacebookMarketingConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=FacebookMarketingReplicationConfig(account_ids="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'FacebookMarketingReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await FacebookMarketingConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Facebook-Marketing Source",
                replication_config=FacebookMarketingReplicationConfig(account_ids="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @FacebookMarketingConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @FacebookMarketingConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await FacebookMarketingConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            FacebookMarketingCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['get', 'list', 'create', 'update', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="ImagesQuery"></a>

`ImagesQuery(connector: FacebookMarketingConnector)`
:   Query class for Images entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ImagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[ImagesSearchData]`
    :   Search images records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ImagesSearchFilter):
        - id: Image ID
        - name: Image name
        - account_id: Ad account ID
        - hash: Image hash
        - url: Image URL
        - permalink_url: Permalink URL
        - width: Image width
        - height: Image height
        - status: Image status
        - created_time: Creation time
        - updated_time: Last update time
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ImagesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, account_id: str, fields: str | None = None, limit: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[Image], ImagesListResultMeta]`
    :   Returns a list of ad images for the specified ad account
        
        Args:
            account_id: The Facebook Ad Account ID (without act_ prefix)
            fields: Comma-separated list of fields to return
            limit: Maximum number of results to return
            after: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            ImagesListResult

<a id="PixelStatsQuery"></a>

`PixelStatsQuery(connector: FacebookMarketingConnector)`
:   Query class for PixelStats entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, pixel_id: str, start_time: str | None = None, end_time: str | None = None, aggregation: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult[list[PixelStat]]`
    :   Returns event quality and stats data for a Facebook pixel, including event counts, match quality scores, and deduplication metrics
        
        Args:
            pixel_id: The Facebook pixel ID
            start_time: Start time for stats period as Unix timestamp
            end_time: End time for stats period as Unix timestamp
            aggregation: Aggregation level for stats
            **kwargs: Additional parameters
        
        Returns:
            PixelStatsListResult

<a id="PixelsQuery"></a>

`PixelsQuery(connector: FacebookMarketingConnector)`
:   Query class for Pixels entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, pixel_id: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.Pixel`
    :   Returns details about a single Facebook pixel by ID
        
        Args:
            pixel_id: The Facebook pixel ID
            fields: Comma-separated list of fields to return
            **kwargs: Additional parameters
        
        Returns:
            Pixel

    `list(self, account_id: str, fields: str | None = None, limit: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[Pixel], PixelsListResultMeta]`
    :   Returns a list of Facebook pixels for the specified ad account, including pixel configuration and event quality data
        
        Args:
            account_id: The Facebook Ad Account ID (without act_ prefix)
            fields: Comma-separated list of fields to return
            limit: Maximum number of results to return
            after: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            PixelsListResult

<a id="VideosQuery"></a>

`VideosQuery(connector: FacebookMarketingConnector)`
:   Query class for Videos entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: VideosSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[VideosSearchData]`
    :   Search videos records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (VideosSearchFilter):
        - id: Video ID
        - title: Video title
        - account_id: Ad account ID
        - description: Video description
        - length: Video length in seconds
        - source: Video source URL
        - permalink_url: Permalink URL
        - views: Number of views
        - created_time: Creation time
        - updated_time: Last update time
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            VideosSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, account_id: str, fields: str | None = None, limit: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[Video], VideosListResultMeta]`
    :   Returns a list of ad videos for the specified ad account
        
        Args:
            account_id: The Facebook Ad Account ID (without act_ prefix)
            fields: Comma-separated list of fields to return
            limit: Maximum number of results to return
            after: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            VideosListResult