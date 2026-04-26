---
id: airbyte_agent_sdk-connectors-tiktok_marketing-connector
title: airbyte_agent_sdk.connectors.tiktok_marketing.connector
---

Module airbyte_agent_sdk.connectors.tiktok_marketing.connector
==============================================================
Tiktok-Marketing connector.

Classes
-------

<a id="AdGroupsQuery"></a>

`AdGroupsQuery(connector: TiktokMarketingConnector)`
:   Query class for AdGroups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdGroupsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdGroupsSearchData]`
    :   Search ad_groups records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdGroupsSearchFilter):
        - adgroup_id: The unique identifier of the ad group
        - adgroup_name: The name of the ad group
        - advertiser_id: The unique identifier of the advertiser
        - budget: The allocated budget for the ad group
        - budget_mode: The mode for managing the budget
        - campaign_id: The unique identifier of the campaign
        - create_time: The timestamp for when the ad group was created
        - modify_time: The timestamp for when the ad group was last modified
        - operation_status: The status of the operation
        - optimization_goal: The goal set for optimization
        - placement_type: The type of ad placement
        - promotion_type: The type of promotion
        - secondary_status: The secondary status of the ad group
        
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

    `list(self, advertiser_id: str, page: int | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[AdGroup], AdGroupsListResultMeta]`
    :   Get ad groups for an advertiser
        
        Args:
            advertiser_id: Advertiser ID
            page: Page number
            page_size: Number of items per page
            **kwargs: Additional parameters
        
        Returns:
            AdGroupsListResult

<a id="AdGroupsReportsDailyQuery"></a>

`AdGroupsReportsDailyQuery(connector: TiktokMarketingConnector)`
:   Query class for AdGroupsReportsDaily entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdGroupsReportsDailySearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdGroupsReportsDailySearchData]`
    :   Search ad_groups_reports_daily records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdGroupsReportsDailySearchFilter):
        - adgroup_id: The unique identifier for the ad group.
        - stat_time_day: The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).
        - campaign_name: The name of the marketing campaign.
        - campaign_id: The unique identifier for the campaign.
        - adgroup_name: The name of the ad group.
        - placement_type: Type of ad placement.
        - spend: Total amount of money spent.
        - cpc: Cost per click.
        - cpm: Cost per thousand impressions.
        - impressions: Number of times the ad was displayed.
        - clicks: Number of clicks on the ad.
        - ctr: Click-through rate.
        - reach: Total number of unique users reached.
        - cost_per_1000_reached: Cost per 1000 unique users reached.
        - conversion: Number of conversions.
        - cost_per_conversion: Cost per conversion.
        - conversion_rate: Rate of conversions.
        - real_time_conversion: Real-time conversions.
        - real_time_cost_per_conversion: Real-time cost per conversion.
        - real_time_conversion_rate: Real-time conversion rate.
        - result: Number of results.
        - cost_per_result: Cost per result.
        - result_rate: Rate of results.
        - real_time_result: Real-time results.
        - real_time_cost_per_result: Real-time cost per result.
        - real_time_result_rate: Real-time result rate.
        - secondary_goal_result: Results for secondary goals.
        - cost_per_secondary_goal_result: Cost per secondary goal result.
        - secondary_goal_result_rate: Rate of secondary goal results.
        - frequency: Average number of times each person saw the ad.
        - video_play_actions: Number of video play actions.
        - video_watched_2s: Number of times video was watched for at least 2 seconds.
        - video_watched_6s: Number of times video was watched for at least 6 seconds.
        - average_video_play: Average video play duration.
        - average_video_play_per_user: Average video play duration per user.
        - video_views_p25: Number of times video was watched to 25%.
        - video_views_p50: Number of times video was watched to 50%.
        - video_views_p75: Number of times video was watched to 75%.
        - video_views_p100: Number of times video was watched to 100%.
        - profile_visits: Number of profile visits.
        - likes: Number of likes.
        - comments: Number of comments.
        - shares: Number of shares.
        - follows: Number of follows.
        - clicks_on_music_disc: Number of clicks on the music disc.
        - real_time_app_install: Real-time app installations.
        - real_time_app_install_cost: Cost of real-time app installations.
        - app_install: Number of app installations.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdGroupsReportsDailySearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, advertiser_id: str, service_type: str, report_type: str, data_level: str, dimensions: str, metrics: str, start_date: str, end_date: str, page: int | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[AdGroupsReportDaily], AdGroupsReportsDailyListResultMeta]`
    :   Get daily performance reports at the ad group level
        
        Args:
            advertiser_id: Advertiser ID
            service_type: Service type
            report_type: Report type
            data_level: Data level for the report
            dimensions: Dimensions for the report (JSON array)
            metrics: Metrics to retrieve (JSON array)
            start_date: Report start date (YYYY-MM-DD)
            end_date: Report end date (YYYY-MM-DD)
            page: Page number
            page_size: Number of items per page
            **kwargs: Additional parameters
        
        Returns:
            AdGroupsReportsDailyListResult

<a id="AdsQuery"></a>

`AdsQuery(connector: TiktokMarketingConnector)`
:   Query class for Ads entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdsSearchData]`
    :   Search ads records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdsSearchFilter):
        - ad_format: The format of the ad
        - ad_id: The unique identifier of the ad
        - ad_name: The name of the ad
        - ad_text: The text content of the ad
        - adgroup_id: The unique identifier of the ad group
        - adgroup_name: The name of the ad group
        - advertiser_id: The unique identifier of the advertiser
        - campaign_id: The unique identifier of the campaign
        - campaign_name: The name of the campaign
        - create_time: The timestamp when the ad was created
        - landing_page_url: The URL of the landing page for the ad
        - modify_time: The timestamp when the ad was last modified
        - operation_status: The operational status of the ad
        - secondary_status: The secondary status of the ad
        - video_id: The unique identifier of the video
        
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

    `list(self, advertiser_id: str, page: int | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[Ad], AdsListResultMeta]`
    :   Get ads for an advertiser
        
        Args:
            advertiser_id: Advertiser ID
            page: Page number
            page_size: Number of items per page
            **kwargs: Additional parameters
        
        Returns:
            AdsListResult

<a id="AdsReportsDailyQuery"></a>

`AdsReportsDailyQuery(connector: TiktokMarketingConnector)`
:   Query class for AdsReportsDaily entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdsReportsDailySearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdsReportsDailySearchData]`
    :   Search ads_reports_daily records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdsReportsDailySearchFilter):
        - ad_id: The unique identifier for the ad.
        - stat_time_day: The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).
        - campaign_name: The name of the marketing campaign.
        - campaign_id: The unique identifier for the campaign.
        - adgroup_name: The name of the ad group.
        - adgroup_id: The unique identifier for the ad group.
        - ad_name: The name of the ad.
        - ad_text: The text content of the ad.
        - placement_type: Type of ad placement.
        - spend: Total amount of money spent.
        - cpc: Cost per click.
        - cpm: Cost per thousand impressions.
        - impressions: Number of times the ad was displayed.
        - clicks: Number of clicks on the ad.
        - ctr: Click-through rate.
        - reach: Total number of unique users reached.
        - cost_per_1000_reached: Cost per 1000 unique users reached.
        - conversion: Number of conversions.
        - cost_per_conversion: Cost per conversion.
        - conversion_rate: Rate of conversions.
        - real_time_conversion: Real-time conversions.
        - real_time_cost_per_conversion: Real-time cost per conversion.
        - real_time_conversion_rate: Real-time conversion rate.
        - result: Number of results.
        - cost_per_result: Cost per result.
        - result_rate: Rate of results.
        - real_time_result: Real-time results.
        - real_time_cost_per_result: Real-time cost per result.
        - real_time_result_rate: Real-time result rate.
        - secondary_goal_result: Results for secondary goals.
        - cost_per_secondary_goal_result: Cost per secondary goal result.
        - secondary_goal_result_rate: Rate of secondary goal results.
        - frequency: Average number of times each person saw the ad.
        - video_play_actions: Number of video play actions.
        - video_watched_2s: Number of times video was watched for at least 2 seconds.
        - video_watched_6s: Number of times video was watched for at least 6 seconds.
        - average_video_play: Average video play duration.
        - average_video_play_per_user: Average video play duration per user.
        - video_views_p25: Number of times video was watched to 25%.
        - video_views_p50: Number of times video was watched to 50%.
        - video_views_p75: Number of times video was watched to 75%.
        - video_views_p100: Number of times video was watched to 100%.
        - profile_visits: Number of profile visits.
        - likes: Number of likes.
        - comments: Number of comments.
        - shares: Number of shares.
        - follows: Number of follows.
        - clicks_on_music_disc: Number of clicks on the music disc.
        - real_time_app_install: Real-time app installations.
        - real_time_app_install_cost: Cost of real-time app installations.
        - app_install: Number of app installations.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdsReportsDailySearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, advertiser_id: str, service_type: str, report_type: str, data_level: str, dimensions: str, metrics: str, start_date: str, end_date: str, page: int | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[AdsReportDaily], AdsReportsDailyListResultMeta]`
    :   Get daily performance reports at the ad level
        
        Args:
            advertiser_id: Advertiser ID
            service_type: Service type
            report_type: Report type
            data_level: Data level for the report
            dimensions: Dimensions for the report (JSON array)
            metrics: Metrics to retrieve (JSON array)
            start_date: Report start date (YYYY-MM-DD)
            end_date: Report end date (YYYY-MM-DD)
            page: Page number
            page_size: Number of items per page
            **kwargs: Additional parameters
        
        Returns:
            AdsReportsDailyListResult

<a id="AdvertisersQuery"></a>

`AdvertisersQuery(connector: TiktokMarketingConnector)`
:   Query class for Advertisers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdvertisersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdvertisersSearchData]`
    :   Search advertisers records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdvertisersSearchFilter):
        - address: The physical address of the advertiser.
        - advertiser_account_type: The type of advertiser's account (e.g., individual, business).
        - advertiser_id: Unique identifier for the advertiser.
        - balance: The current balance in the advertiser's account.
        - brand: The brand name associated with the advertiser.
        - cellphone_number: The cellphone number of the advertiser.
        - company: The name of the company associated with the advertiser.
        - contacter: The contact person for the advertiser.
        - country: The country where the advertiser is located.
        - create_time: The timestamp when the advertiser account was created.
        - currency: The currency used for transactions in the account.
        - description: A brief description or bio of the advertiser or company.
        - display_timezone: The timezone for display purposes.
        - email: The email address associated with the advertiser.
        - industry: The industry or sector the advertiser operates in.
        - language: The preferred language of communication for the advertiser.
        - license_city: The city where the advertiser's license is registered.
        - license_no: The license number of the advertiser.
        - license_province: The province or state where the advertiser's license is registered.
        - license_url: The URL link to the advertiser's license documentation.
        - name: The name of the advertiser or company.
        - promotion_area: The specific area or region where the advertiser focuses promotion.
        - promotion_center_city: The city at the center of the advertiser's promotion activities.
        - promotion_center_province: The province or state at the center of the advertiser's promotion activities.
        - rejection_reason: Reason for any advertisement rejection by the platform.
        - role: The role or position of the advertiser within the company.
        - status: The current status of the advertiser's account.
        - telephone_number: The telephone number of the advertiser.
        - timezone: The timezone setting for the advertiser's activities.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdvertisersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, advertiser_ids: str, page: int | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[Advertiser], AdvertisersListResultMeta]`
    :   Get advertiser account information
        
        Args:
            advertiser_ids: Advertiser IDs (JSON array of strings)
            page: Page number
            page_size: Number of items per page
            **kwargs: Additional parameters
        
        Returns:
            AdvertisersListResult

<a id="AdvertisersReportsDailyQuery"></a>

`AdvertisersReportsDailyQuery(connector: TiktokMarketingConnector)`
:   Query class for AdvertisersReportsDaily entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdvertisersReportsDailySearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdvertisersReportsDailySearchData]`
    :   Search advertisers_reports_daily records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdvertisersReportsDailySearchFilter):
        - advertiser_id: The unique identifier for the advertiser.
        - stat_time_day: The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).
        - spend: Total amount of money spent.
        - cash_spend: The amount of money spent in cash.
        - voucher_spend: Amount spent using vouchers.
        - cpc: Cost per click.
        - cpm: Cost per thousand impressions.
        - impressions: Number of times the ad was displayed.
        - clicks: Number of clicks on the ad.
        - ctr: Click-through rate.
        - reach: Total number of unique users reached.
        - cost_per_1000_reached: Cost per 1000 unique users reached.
        - frequency: Average number of times each person saw the ad.
        - video_play_actions: Number of video play actions.
        - video_watched_2s: Number of times video was watched for at least 2 seconds.
        - video_watched_6s: Number of times video was watched for at least 6 seconds.
        - average_video_play: Average video play duration.
        - average_video_play_per_user: Average video play duration per user.
        - video_views_p25: Number of times video was watched to 25%.
        - video_views_p50: Number of times video was watched to 50%.
        - video_views_p75: Number of times video was watched to 75%.
        - video_views_p100: Number of times video was watched to 100%.
        - profile_visits: Number of profile visits.
        - likes: Number of likes.
        - comments: Number of comments.
        - shares: Number of shares.
        - follows: Number of follows.
        - clicks_on_music_disc: Number of clicks on the music disc.
        - real_time_app_install: Real-time app installations.
        - real_time_app_install_cost: Cost of real-time app installations.
        - app_install: Number of app installations.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdvertisersReportsDailySearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, advertiser_id: str, service_type: str, report_type: str, data_level: str, dimensions: str, metrics: str, start_date: str, end_date: str, page: int | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[AdvertisersReportDaily], AdvertisersReportsDailyListResultMeta]`
    :   Get daily performance reports at the advertiser level
        
        Args:
            advertiser_id: Advertiser ID
            service_type: Service type
            report_type: Report type
            data_level: Data level for the report
            dimensions: Dimensions for the report (JSON array)
            metrics: Metrics to retrieve (JSON array)
            start_date: Report start date (YYYY-MM-DD)
            end_date: Report end date (YYYY-MM-DD)
            page: Page number
            page_size: Number of items per page
            **kwargs: Additional parameters
        
        Returns:
            AdvertisersReportsDailyListResult

<a id="AudiencesQuery"></a>

`AudiencesQuery(connector: TiktokMarketingConnector)`
:   Query class for Audiences entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AudiencesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AudiencesSearchData]`
    :   Search audiences records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AudiencesSearchFilter):
        - audience_id: Unique identifier for the audience
        - audience_type: Type of audience
        - cover_num: Number of audience members covered
        - create_time: Timestamp indicating when the audience was created
        - is_valid: Flag indicating if the audience data is valid
        - name: Name of the audience
        - shared: Flag indicating if the audience is shared
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AudiencesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, advertiser_id: str, page: int | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[Audience], AudiencesListResultMeta]`
    :   Get custom audiences for an advertiser
        
        Args:
            advertiser_id: Advertiser ID
            page: Page number
            page_size: Number of items per page
            **kwargs: Additional parameters
        
        Returns:
            AudiencesListResult

<a id="CampaignsQuery"></a>

`CampaignsQuery(connector: TiktokMarketingConnector)`
:   Query class for Campaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[CampaignsSearchData]`
    :   Search campaigns records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignsSearchFilter):
        - advertiser_id: The unique identifier of the advertiser associated with the campaign
        - app_promotion_type: Type of app promotion being used in the campaign
        - bid_type: Type of bid strategy being used in the campaign
        - budget: Total budget allocated for the campaign
        - budget_mode: Mode in which the budget is being managed (e.g., daily, lifetime)
        - budget_optimize_on: The metric or event that the budget optimization is based on
        - campaign_id: The unique identifier of the campaign
        - campaign_name: Name of the campaign for easy identification
        - campaign_type: Type of campaign (e.g., awareness, conversion)
        - create_time: Timestamp when the campaign was created
        - deep_bid_type: Advanced bid type used for campaign optimization
        - is_new_structure: Flag indicating if the campaign utilizes a new campaign structure
        - is_search_campaign: Flag indicating if the campaign is a search campaign
        - is_smart_performance_campaign: Flag indicating if the campaign uses smart performance optimization
        - modify_time: Timestamp when the campaign was last modified
        - objective: The objective or goal of the campaign
        - objective_type: Type of objective selected for the campaign
        - operation_status: Current operational status of the campaign
        - optimization_goal: Specific goal to be optimized for in the campaign
        - rf_campaign_type: Type of RF (reach and frequency) campaign being run
        - roas_bid: Return on ad spend goal set for the campaign
        - secondary_status: Additional status information of the campaign
        - split_test_variable: Variable being tested in a split test campaign
        
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

    `list(self, advertiser_id: str, page: int | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]`
    :   Get campaigns for an advertiser
        
        Args:
            advertiser_id: Advertiser ID
            page: Page number
            page_size: Number of items per page
            **kwargs: Additional parameters
        
        Returns:
            CampaignsListResult

<a id="CampaignsReportsDailyQuery"></a>

`CampaignsReportsDailyQuery(connector: TiktokMarketingConnector)`
:   Query class for CampaignsReportsDaily entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignsReportsDailySearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[CampaignsReportsDailySearchData]`
    :   Search campaigns_reports_daily records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignsReportsDailySearchFilter):
        - campaign_id: The unique identifier for the campaign.
        - stat_time_day: The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).
        - campaign_name: The name of the marketing campaign.
        - spend: Total amount of money spent.
        - cpc: Cost per click.
        - cpm: Cost per thousand impressions.
        - impressions: Number of times the ad was displayed.
        - clicks: Number of clicks on the ad.
        - ctr: Click-through rate.
        - reach: Total number of unique users reached.
        - cost_per_1000_reached: Cost per 1000 unique users reached.
        - frequency: Average number of times each person saw the ad.
        - video_play_actions: Number of video play actions.
        - video_watched_2s: Number of times video was watched for at least 2 seconds.
        - video_watched_6s: Number of times video was watched for at least 6 seconds.
        - average_video_play: Average video play duration.
        - average_video_play_per_user: Average video play duration per user.
        - video_views_p25: Number of times video was watched to 25%.
        - video_views_p50: Number of times video was watched to 50%.
        - video_views_p75: Number of times video was watched to 75%.
        - video_views_p100: Number of times video was watched to 100%.
        - profile_visits: Number of profile visits.
        - likes: Number of likes.
        - comments: Number of comments.
        - shares: Number of shares.
        - follows: Number of follows.
        - clicks_on_music_disc: Number of clicks on the music disc.
        - real_time_app_install: Real-time app installations.
        - real_time_app_install_cost: Cost of real-time app installations.
        - app_install: Number of app installations.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CampaignsReportsDailySearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, advertiser_id: str, service_type: str, report_type: str, data_level: str, dimensions: str, metrics: str, start_date: str, end_date: str, page: int | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[CampaignsReportDaily], CampaignsReportsDailyListResultMeta]`
    :   Get daily performance reports at the campaign level
        
        Args:
            advertiser_id: Advertiser ID
            service_type: Service type
            report_type: Report type
            data_level: Data level for the report
            dimensions: Dimensions for the report (JSON array)
            metrics: Metrics to retrieve (JSON array)
            start_date: Report start date (YYYY-MM-DD)
            end_date: Report end date (YYYY-MM-DD)
            page: Page number
            page_size: Number of items per page
            **kwargs: Additional parameters
        
        Returns:
            CampaignsReportsDailyListResult

<a id="CreativeAssetsImagesQuery"></a>

`CreativeAssetsImagesQuery(connector: TiktokMarketingConnector)`
:   Query class for CreativeAssetsImages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CreativeAssetsImagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[CreativeAssetsImagesSearchData]`
    :   Search creative_assets_images records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CreativeAssetsImagesSearchFilter):
        - create_time: The timestamp when the image was created.
        - file_name: The name of the image file.
        - format: The format type of the image file.
        - height: The height dimension of the image.
        - image_id: The unique identifier for the image.
        - image_url: The URL to access the image.
        - modify_time: The timestamp when the image was last modified.
        - size: The size of the image file.
        - width: The width dimension of the image.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CreativeAssetsImagesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, advertiser_id: str, page: int | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[CreativeAssetImage], CreativeAssetsImagesListResultMeta]`
    :   Search creative asset images for an advertiser
        
        Args:
            advertiser_id: Advertiser ID
            page: Page number
            page_size: Number of items per page
            **kwargs: Additional parameters
        
        Returns:
            CreativeAssetsImagesListResult

<a id="CreativeAssetsVideosQuery"></a>

`CreativeAssetsVideosQuery(connector: TiktokMarketingConnector)`
:   Query class for CreativeAssetsVideos entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CreativeAssetsVideosSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[CreativeAssetsVideosSearchData]`
    :   Search creative_assets_videos records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CreativeAssetsVideosSearchFilter):
        - create_time: Timestamp when the video was created.
        - duration: Duration of the video in seconds.
        - file_name: Name of the video file.
        - format: Format of the video file.
        - height: Height of the video in pixels.
        - modify_time: Timestamp when the video was last modified.
        - size: Size of the video file in bytes.
        - video_cover_url: URL for the cover image of the video.
        - video_id: ID of the video.
        - width: Width of the video in pixels.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CreativeAssetsVideosSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, advertiser_id: str, page: int | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[CreativeAssetVideo], CreativeAssetsVideosListResultMeta]`
    :   Search creative asset videos for an advertiser
        
        Args:
            advertiser_id: Advertiser ID
            page: Page number
            page_size: Number of items per page
            **kwargs: Additional parameters
        
        Returns:
            CreativeAssetsVideosListResult

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