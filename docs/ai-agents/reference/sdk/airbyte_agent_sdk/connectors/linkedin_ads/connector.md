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
        - account: The account associated with the user
        - created: The date and time when the user account was created
        - last_modified: The date and time when the user account was last modified
        - role: The role assigned to the user in the account
        - user: The user details including name, email, etc.
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AccountUsersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against account_users records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `create(self, role: str, account: str, user: str, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.RestliCreateResponse`
    :   Grants a user a role on an ad account. Note the non-standard Rest.li compound-key shape: this is a PUT (not POST) keyed by both the account and user URNs. Pass the raw URNs as parameters; they are URL-encoded automatically. Requires the rw_ads OAuth scope and the ACCOUNT_BILLING_ADMIN or ACCOUNT_MANAGER role.
        
        
        Args:
            role: Role to grant on the ad account
            account: Sponsored account URN, e.g. urn:li:sponsoredAccount:123456
            user: Person URN, e.g. urn:li:person:abc123
            **kwargs: Additional parameters
        
        Returns:
            RestliCreateResponse

    `delete(self, account: str, user: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Removes a user's role from an ad account. Pass the raw account and user URNs as parameters; they are URL-encoded automatically. Requires the rw_ads OAuth scope and the ACCOUNT_BILLING_ADMIN or ACCOUNT_MANAGER role.
        
        
        Args:
            account: Sponsored account URN, e.g. urn:li:sponsoredAccount:123456
            user: Person URN, e.g. urn:li:person:abc123
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, q: str, accounts: str, count: int | None = None, start: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[AccountUser], AccountUsersListResultMeta]`
    :   Returns a list of users associated with ad accounts
        
        Args:
            q: LinkedIn API finder method for querying by account URN
            accounts: Account URN, e.g. urn:li:sponsoredAccount:123456
            count: Number of items per page
            start: Offset for pagination
            **kwargs: Additional parameters
        
        Returns:
            AccountUsersListResult

    `update(self, patch: AccountUsersUpdateParamsPatch, account: str, user: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Partially updates an account user's role using the Rest.li PARTIAL_UPDATE pattern: the body wraps the fields to change in patch.$set (e.g. \{"patch": \{"$set": \{"role": "CAMPAIGN_MANAGER"\}\}\}). Pass the raw account and user URNs as parameters; they are URL-encoded automatically. Requires the rw_ads OAuth scope and the ACCOUNT_BILLING_ADMIN or ACCOUNT_MANAGER role.
        
        
        Args:
            patch: Parameter patch
            account: Sponsored account URN, e.g. urn:li:sponsoredAccount:123456
            user: Person URN, e.g. urn:li:person:abc123
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
        - test: Flag indicating if the account is in a test mode.
        - notified_on_creative_rejection: Flag for notifications on creative rejection.
        - notified_on_new_features_enabled: Flag for notifications on new features being enabled.
        - notified_on_end_of_campaign: Flag for notifications on the end of campaign.
        - serving_statuses: The serving statuses associated with the account.
        - notified_on_campaign_optimization: Flag for notifications on campaign optimization.
        - type_: The type or category of the account.
        - version: The version information related to the account.
        - reference: A reference identifier for the account.
        - notified_on_creative_approval: Flag for notifications on creative approval.
        - created: The timestamp indicating when the account was created.
        - last_modified: The timestamp of the last modification made to the account.
        - name: The name of the account.
        - currency: The currency used for financial transactions in the account.
        - id: The unique identifier for the account.
        - status: The status of the account.
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AccountsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against accounts records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `create(self, name: str, type: str, currency: str | None = None, reference: str | None = None, test: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, AccountsCreateResultMeta]`
    :   Creates a new ad account. Only type BUSINESS can be created via the API (ENTERPRISE accounts cannot). Requires the rw_ads OAuth scope. The new account ID is returned in the x-restli-id response header.
        
        
        Args:
            name: Ad account name
            type: Account type; only BUSINESS accounts can be created via the API
            currency: ISO 4217 currency code, e.g. USD (defaults to USD)
            reference: Optional owning organization URN, e.g. urn:li:organization:123456
            test: Whether to create a test account
            **kwargs: Additional parameters
        
        Returns:
            AccountsCreateResult

    `delete(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Hard-deletes an ad account. Only accounts in DRAFT status accept a true DELETE; for non-DRAFT accounts use the update operation to set status to PENDING_DELETION. Both forms require the ACCOUNT_BILLING_ADMIN role and the rw_ads OAuth scope.
        
        
        Args:
            id: Ad account ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.Account`
    :   Get a single ad account by ID
        
        Args:
            id: Ad account ID
            **kwargs: Additional parameters
        
        Returns:
            Account

    `list(self, q: str, page_size: int | None = None, page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[dict[str, Any]], AccountsListResultMeta]`
    :   Returns a list of ad accounts the authenticated user has access to
        
        Args:
            q: LinkedIn API finder method for querying ad accounts
            page_size: Number of items per page
            page_token: Token for the next page of results
            **kwargs: Additional parameters
        
        Returns:
            AccountsListResult

    `update(self, patch: AccountsUpdateParamsPatch, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Partially updates an ad account using the Rest.li PARTIAL_UPDATE pattern: the body wraps the fields to change in patch.$set. Requires the rw_ads OAuth scope; most account fields require the ACCOUNT_BILLING_ADMIN role. To soft-delete a non-DRAFT account, set status to PENDING_DELETION here (billing admin only).
        
        
        Args:
            patch: Parameter patch
            id: Ad account ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
        - action_clicks: The number of clicks on action buttons in the ad.
        - ad_unit_clicks: The number of clicks on ad unit components.
        - approximate_member_reach: An approximation of unique ad impressions.
        - card_clicks: The number of clicks on interactive card elements.
        - card_impressions: The number of times interactive cards were displayed.
        - clicks: Total number of clicks on the ad.
        - comment_likes: The count of likes on comments related to the ad.
        - comments: The number of comments on the ad.
        - company_page_clicks: Clicks on the company page associated with the ad.
        - conversion_value_in_local_currency: Conversion value in the local currency.
        - cost_in_local_currency: Cost of ad campaign in the local currency.
        - cost_in_usd: Cost of ad campaign in USD.
        - document_completions: Number of completions for document views.
        - document_first_quartile_completions: Completions for first quartile of document views.
        - document_midpoint_completions: Completions for midpoint of document views.
        - document_third_quartile_completions: Completions for third quartile of document views.
        - download_clicks: Clicks on download links in the ad.
        - end_date: End date of the ad analytics data.
        - external_website_conversions: Conversions that lead to external websites.
        - external_website_post_click_conversions: Post-click conversions on external websites.
        - external_website_post_view_conversions: Post-view conversions on external websites.
        - follows: Number of follows generated by the ad.
        - full_screen_plays: Number of times videos were played in fullscreen mode.
        - impressions: Total number of times the ad was displayed.
        - job_applications: Number of job applications initiated through the ad.
        - job_apply_clicks: Clicks on apply job button in the ad.
        - landing_page_clicks: Clicks on the landing page associated with the ad.
        - lead_generation_mail_contact_info_shares: Shares of contact information through lead generation.
        - lead_generation_mail_interested_clicks: Clicks on expressing interest through lead generation mail.
        - likes: Total likes received on the ad.
        - one_click_lead_form_opens: Number of times lead forms were opened in one click.
        - one_click_leads: Leads generated in one click.
        - opens: The number of times the ad was opened or expanded.
        - other_engagements: Engagements other than clicks on the ad.
        - pivot_values: Values used for pivoting the analytics.
        - string_of_pivot_values: Comma-separated string of pivot values for this analytics record
        - post_click_job_applications: Job applications initiated post-clicking on the ad.
        - post_click_job_apply_clicks: Clicks on apply job button post-clicking on the ad.
        - post_click_registrations: Registrations completed post-clicking on the ad.
        - post_view_job_applications: Job applications initiated post-viewing the ad.
        - post_view_job_apply_clicks: Clicks on apply job button post-viewing the ad.
        - post_view_registrations: Registrations completed post-viewing the ad.
        - reactions: Total reactions (e.g., like, love, celebrate) on the ad.
        - registrations: Total registrations completed through the ad.
        - sends: Number of messages sent through the ad.
        - shares: Total shares generated by the ad.
        - start_date: Start date of the ad analytics data.
        - talent_leads: Number of leads related to talent acquisition.
        - text_url_clicks: Clicks on text URLs within the ad.
        - total_engagements: Total number of engagements on the ad.
        - valid_work_email_leads: Leads generated through valid work emails.
        - video_completions: Number of times videos were watched till completion.
        - video_first_quartile_completions: Completions for first quartile of video views.
        - video_midpoint_completions: Completions for midpoint of video views.
        - video_starts: Total video starts initiated by users.
        - video_third_quartile_completions: Completions for third quartile of video views.
        - video_views: Total views of videos in the ad.
        - viral_card_clicks: Clicks on interactive card components in viral distribution.
        - viral_card_impressions: Impressions of interactive cards in viral distribution.
        - viral_clicks: Total clicks in viral distribution of the ad.
        - viral_comment_likes: Likes received on comments in viral distribution.
        - viral_comments: Number of comments in viral distribution of the ad.
        - viral_company_page_clicks: Clicks on the company page in viral distribution.
        - viral_document_completions: Complete views of documents in viral distribution.
        - viral_document_first_quartile_completions: First quartile completions of documents in viral distribution.
        - viral_document_midpoint_completions: Midpoint completions of documents in viral distribution.
        - viral_document_third_quartile_completions: Third quartile completions of documents in viral distribution.
        - viral_download_clicks: Clicks on downloads in viral distribution of the ad.
        - viral_external_website_conversions: External website conversions in viral distribution.
        - viral_external_website_post_click_conversions: Post-click conversions on external websites in viral distribution.
        - viral_external_website_post_view_conversions: Post-view conversions on external websites in viral distribution.
        - viral_follows: Follows generated in viral distribution of the ad.
        - viral_full_screen_plays: Fullscreen video plays in viral distribution.
        - viral_impressions: Total impressions in viral distribution of the ad.
        - viral_job_applications: Job applications initiated in viral distribution.
        - viral_job_apply_clicks: Clicks on apply job button in viral distribution of the ad.
        - viral_landing_page_clicks: Clicks on landing page in viral distribution.
        - viral_likes: Total likes in viral distribution of the ad.
        - viral_one_click_lead_form_opens: One-click lead form opens in viral distribution.
        - viral_one_click_leads: Leads generated in one click in viral distribution.
        - viral_other_engagements: Other engagements in viral distribution of the ad.
        - viral_post_click_job_applications: Job applications initiated post-clicking in viral distribution.
        - viral_post_click_job_apply_clicks: Clicks on apply job button post-clicking in viral distribution.
        - viral_post_click_registrations: Registrations completed post-clicking in viral distribution.
        - viral_post_view_job_applications: Job applications initiated post-viewing in viral distribution.
        - viral_post_view_job_apply_clicks: Clicks on apply job button post-viewing in viral distribution.
        - viral_post_view_registrations: Registrations completed post-viewing in viral distribution.
        - viral_reactions: Total reactions in viral distribution of the ad.
        - viral_registrations: Total registrations in viral distribution of the ad.
        - viral_shares: Total shares in viral distribution of the ad.
        - viral_total_engagements: Total engagements in viral distribution of the ad.
        - viral_video_completions: Completions of videos in viral distribution.
        - viral_video_first_quartile_completions: First quartile completions of videos in viral distribution.
        - viral_video_midpoint_completions: Midpoint completions of videos in viral distribution.
        - viral_video_starts: Total video starts in viral distribution of the ad.
        - viral_video_third_quartile_completions: Third quartile completions of videos in viral distribution.
        - viral_video_views: Total views of videos in viral distribution of the ad.
        - pivot: Pivot dimension used for this analytics record
        - sponsored_campaign: URN of the sponsored campaign this analytics record belongs to
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdCampaignAnalyticsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against ad_campaign_analytics records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `list(self, q: str, pivot: str, time_granularity: str, date_range: str, campaigns: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult[list[AdAnalyticsRecord]]`
    :   Returns ad analytics data pivoted by campaign. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by campaign.
        
        
        Args:
            q: LinkedIn API finder method for querying ad analytics
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
        - action_clicks: The number of clicks on action buttons in the ad.
        - ad_unit_clicks: The number of clicks on ad unit components.
        - approximate_member_reach: An approximation of unique ad impressions.
        - card_clicks: The number of clicks on interactive card elements.
        - card_impressions: The number of times interactive cards were displayed.
        - clicks: Total number of clicks on the ad.
        - comment_likes: The count of likes on comments related to the ad.
        - comments: The number of comments on the ad.
        - company_page_clicks: Clicks on the company page associated with the ad.
        - conversion_value_in_local_currency: Conversion value in the local currency.
        - cost_in_local_currency: Cost of ad campaign in the local currency.
        - cost_in_usd: Cost of ad campaign in USD.
        - document_completions: Number of completions for document views.
        - document_first_quartile_completions: Completions for first quartile of document views.
        - document_midpoint_completions: Completions for midpoint of document views.
        - document_third_quartile_completions: Completions for third quartile of document views.
        - download_clicks: Clicks on download links in the ad.
        - end_date: End date of the ad analytics data.
        - external_website_conversions: Conversions that lead to external websites.
        - external_website_post_click_conversions: Post-click conversions on external websites.
        - external_website_post_view_conversions: Post-view conversions on external websites.
        - follows: Number of follows generated by the ad.
        - full_screen_plays: Number of times videos were played in fullscreen mode.
        - impressions: Total number of times the ad was displayed.
        - job_applications: Number of job applications initiated through the ad.
        - job_apply_clicks: Clicks on apply job button in the ad.
        - landing_page_clicks: Clicks on the landing page associated with the ad.
        - lead_generation_mail_contact_info_shares: Shares of contact information through lead generation.
        - lead_generation_mail_interested_clicks: Clicks on expressing interest through lead generation mail.
        - likes: Total likes received on the ad.
        - one_click_lead_form_opens: Number of times lead forms were opened in one click.
        - one_click_leads: Leads generated in one click.
        - opens: The number of times the ad was opened or expanded.
        - other_engagements: Engagements other than clicks on the ad.
        - pivot_values: Values used for pivoting the analytics.
        - string_of_pivot_values: Comma-separated string of pivot values for this analytics record
        - post_click_job_applications: Job applications initiated post-clicking on the ad.
        - post_click_job_apply_clicks: Clicks on apply job button post-clicking on the ad.
        - post_click_registrations: Registrations completed post-clicking on the ad.
        - post_view_job_applications: Job applications initiated post-viewing the ad.
        - post_view_job_apply_clicks: Clicks on apply job button post-viewing the ad.
        - post_view_registrations: Registrations completed post-viewing the ad.
        - reactions: Total reactions (e.g., like, love, celebrate) on the ad.
        - registrations: Total registrations completed through the ad.
        - sends: Number of messages sent through the ad.
        - shares: Total shares generated by the ad.
        - start_date: Start date of the ad analytics data.
        - talent_leads: Number of leads related to talent acquisition.
        - text_url_clicks: Clicks on text URLs within the ad.
        - total_engagements: Total number of engagements on the ad.
        - valid_work_email_leads: Leads generated through valid work emails.
        - video_completions: Number of times videos were watched till completion.
        - video_first_quartile_completions: Completions for first quartile of video views.
        - video_midpoint_completions: Completions for midpoint of video views.
        - video_starts: Total video starts initiated by users.
        - video_third_quartile_completions: Completions for third quartile of video views.
        - video_views: Total views of videos in the ad.
        - viral_card_clicks: Clicks on interactive card components in viral distribution.
        - viral_card_impressions: Impressions of interactive cards in viral distribution.
        - viral_clicks: Total clicks in viral distribution of the ad.
        - viral_comment_likes: Likes received on comments in viral distribution.
        - viral_comments: Number of comments in viral distribution of the ad.
        - viral_company_page_clicks: Clicks on the company page in viral distribution.
        - viral_document_completions: Complete views of documents in viral distribution.
        - viral_document_first_quartile_completions: First quartile completions of documents in viral distribution.
        - viral_document_midpoint_completions: Midpoint completions of documents in viral distribution.
        - viral_document_third_quartile_completions: Third quartile completions of documents in viral distribution.
        - viral_download_clicks: Clicks on downloads in viral distribution of the ad.
        - viral_external_website_conversions: External website conversions in viral distribution.
        - viral_external_website_post_click_conversions: Post-click conversions on external websites in viral distribution.
        - viral_external_website_post_view_conversions: Post-view conversions on external websites in viral distribution.
        - viral_follows: Follows generated in viral distribution of the ad.
        - viral_full_screen_plays: Fullscreen video plays in viral distribution.
        - viral_impressions: Total impressions in viral distribution of the ad.
        - viral_job_applications: Job applications initiated in viral distribution.
        - viral_job_apply_clicks: Clicks on apply job button in viral distribution of the ad.
        - viral_landing_page_clicks: Clicks on landing page in viral distribution.
        - viral_likes: Total likes in viral distribution of the ad.
        - viral_one_click_lead_form_opens: One-click lead form opens in viral distribution.
        - viral_one_click_leads: Leads generated in one click in viral distribution.
        - viral_other_engagements: Other engagements in viral distribution of the ad.
        - viral_post_click_job_applications: Job applications initiated post-clicking in viral distribution.
        - viral_post_click_job_apply_clicks: Clicks on apply job button post-clicking in viral distribution.
        - viral_post_click_registrations: Registrations completed post-clicking in viral distribution.
        - viral_post_view_job_applications: Job applications initiated post-viewing in viral distribution.
        - viral_post_view_job_apply_clicks: Clicks on apply job button post-viewing in viral distribution.
        - viral_post_view_registrations: Registrations completed post-viewing in viral distribution.
        - viral_reactions: Total reactions in viral distribution of the ad.
        - viral_registrations: Total registrations in viral distribution of the ad.
        - viral_shares: Total shares in viral distribution of the ad.
        - viral_total_engagements: Total engagements in viral distribution of the ad.
        - viral_video_completions: Completions of videos in viral distribution.
        - viral_video_first_quartile_completions: First quartile completions of videos in viral distribution.
        - viral_video_midpoint_completions: Midpoint completions of videos in viral distribution.
        - viral_video_starts: Total video starts in viral distribution of the ad.
        - viral_video_third_quartile_completions: Third quartile completions of videos in viral distribution.
        - viral_video_views: Total views of videos in viral distribution of the ad.
        - pivot: Pivot dimension used for this analytics record
        - sponsored_creative: Sponsored creative
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdCreativeAnalyticsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against ad_creative_analytics records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `list(self, q: str, pivot: str, time_granularity: str, date_range: str, creatives: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult[list[AdAnalyticsRecord]]`
    :   Returns ad analytics data pivoted by creative. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by creative.
        
        
        Args:
            q: LinkedIn API finder method for querying ad analytics
            pivot: Pivot dimension for analytics grouping
            time_granularity: Time granularity for analytics data
            date_range: Date range in LinkedIn format, e.g. (start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31))
            creatives: List of creative URNs, e.g. List(urn%3Ali%3AsponsoredCreative%3A123)
            fields: Comma-separated list of metric fields to return
            **kwargs: Additional parameters
        
        Returns:
            AdCreativeAnalyticsListResult

<a id="AdImpressionDeviceAnalyticsQuery"></a>

`AdImpressionDeviceAnalyticsQuery(connector: LinkedinAdsConnector)`
:   Query class for AdImpressionDeviceAnalytics entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdImpressionDeviceAnalyticsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdImpressionDeviceAnalyticsSearchData]`
    :   Search ad_impression_device_analytics records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdImpressionDeviceAnalyticsSearchFilter):
        - action_clicks: The number of clicks on action buttons in the ad.
        - ad_unit_clicks: The number of clicks on ad unit components.
        - approximate_member_reach: An approximation of unique ad impressions.
        - card_clicks: The number of clicks on interactive card elements.
        - card_impressions: The number of times interactive cards were displayed.
        - clicks: Total number of clicks on the ad.
        - comment_likes: The count of likes on comments related to the ad.
        - comments: The number of comments on the ad.
        - company_page_clicks: Clicks on the company page associated with the ad.
        - conversion_value_in_local_currency: Conversion value in the local currency.
        - cost_in_local_currency: Cost of ad campaign in the local currency.
        - cost_in_usd: Cost of ad campaign in USD.
        - document_completions: Number of completions for document views.
        - document_first_quartile_completions: Completions for first quartile of document views.
        - document_midpoint_completions: Completions for midpoint of document views.
        - document_third_quartile_completions: Completions for third quartile of document views.
        - download_clicks: Clicks on download links in the ad.
        - end_date: End date of the ad analytics data.
        - external_website_conversions: Conversions that lead to external websites.
        - external_website_post_click_conversions: Post-click conversions on external websites.
        - external_website_post_view_conversions: Post-view conversions on external websites.
        - follows: Number of follows generated by the ad.
        - full_screen_plays: Number of times videos were played in fullscreen mode.
        - impressions: Total number of times the ad was displayed.
        - job_applications: Number of job applications initiated through the ad.
        - job_apply_clicks: Clicks on apply job button in the ad.
        - landing_page_clicks: Clicks on the landing page associated with the ad.
        - lead_generation_mail_contact_info_shares: Shares of contact information through lead generation.
        - lead_generation_mail_interested_clicks: Clicks on expressing interest through lead generation mail.
        - likes: Total likes received on the ad.
        - one_click_lead_form_opens: Number of times lead forms were opened in one click.
        - one_click_leads: Leads generated in one click.
        - opens: The number of times the ad was opened or expanded.
        - other_engagements: Engagements other than clicks on the ad.
        - pivot_values: Values used for pivoting the analytics.
        - string_of_pivot_values: Comma-separated string of pivot values for this analytics record
        - post_click_job_applications: Job applications initiated post-clicking on the ad.
        - post_click_job_apply_clicks: Clicks on apply job button post-clicking on the ad.
        - post_click_registrations: Registrations completed post-clicking on the ad.
        - post_view_job_applications: Job applications initiated post-viewing the ad.
        - post_view_job_apply_clicks: Clicks on apply job button post-viewing the ad.
        - post_view_registrations: Registrations completed post-viewing the ad.
        - reactions: Total reactions (e.g., like, love, celebrate) on the ad.
        - registrations: Total registrations completed through the ad.
        - sends: Number of messages sent through the ad.
        - shares: Total shares generated by the ad.
        - start_date: Start date of the ad analytics data.
        - talent_leads: Number of leads related to talent acquisition.
        - text_url_clicks: Clicks on text URLs within the ad.
        - total_engagements: Total number of engagements on the ad.
        - valid_work_email_leads: Leads generated through valid work emails.
        - video_completions: Number of times videos were watched till completion.
        - video_first_quartile_completions: Completions for first quartile of video views.
        - video_midpoint_completions: Completions for midpoint of video views.
        - video_starts: Total video starts initiated by users.
        - video_third_quartile_completions: Completions for third quartile of video views.
        - video_views: Total views of videos in the ad.
        - viral_card_clicks: Clicks on interactive card components in viral distribution.
        - viral_card_impressions: Impressions of interactive cards in viral distribution.
        - viral_clicks: Total clicks in viral distribution of the ad.
        - viral_comment_likes: Likes received on comments in viral distribution.
        - viral_comments: Number of comments in viral distribution of the ad.
        - viral_company_page_clicks: Clicks on the company page in viral distribution.
        - viral_document_completions: Complete views of documents in viral distribution.
        - viral_document_first_quartile_completions: First quartile completions of documents in viral distribution.
        - viral_document_midpoint_completions: Midpoint completions of documents in viral distribution.
        - viral_document_third_quartile_completions: Third quartile completions of documents in viral distribution.
        - viral_download_clicks: Clicks on downloads in viral distribution of the ad.
        - viral_external_website_conversions: External website conversions in viral distribution.
        - viral_external_website_post_click_conversions: Post-click conversions on external websites in viral distribution.
        - viral_external_website_post_view_conversions: Post-view conversions on external websites in viral distribution.
        - viral_follows: Follows generated in viral distribution of the ad.
        - viral_full_screen_plays: Fullscreen video plays in viral distribution.
        - viral_impressions: Total impressions in viral distribution of the ad.
        - viral_job_applications: Job applications initiated in viral distribution.
        - viral_job_apply_clicks: Clicks on apply job button in viral distribution of the ad.
        - viral_landing_page_clicks: Clicks on landing page in viral distribution.
        - viral_likes: Total likes in viral distribution of the ad.
        - viral_one_click_lead_form_opens: One-click lead form opens in viral distribution.
        - viral_one_click_leads: Leads generated in one click in viral distribution.
        - viral_other_engagements: Other engagements in viral distribution of the ad.
        - viral_post_click_job_applications: Job applications initiated post-clicking in viral distribution.
        - viral_post_click_job_apply_clicks: Clicks on apply job button post-clicking in viral distribution.
        - viral_post_click_registrations: Registrations completed post-clicking in viral distribution.
        - viral_post_view_job_applications: Job applications initiated post-viewing in viral distribution.
        - viral_post_view_job_apply_clicks: Clicks on apply job button post-viewing in viral distribution.
        - viral_post_view_registrations: Registrations completed post-viewing in viral distribution.
        - viral_reactions: Total reactions in viral distribution of the ad.
        - viral_registrations: Total registrations in viral distribution of the ad.
        - viral_shares: Total shares in viral distribution of the ad.
        - viral_total_engagements: Total engagements in viral distribution of the ad.
        - viral_video_completions: Completions of videos in viral distribution.
        - viral_video_first_quartile_completions: First quartile completions of videos in viral distribution.
        - viral_video_midpoint_completions: Midpoint completions of videos in viral distribution.
        - viral_video_starts: Total video starts in viral distribution of the ad.
        - viral_video_third_quartile_completions: Third quartile completions of videos in viral distribution.
        - viral_video_views: Total views of videos in viral distribution of the ad.
        - pivot: Pivot dimension used for this analytics record
        - sponsored_campaign: URN of the sponsored campaign this analytics record belongs to
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdImpressionDeviceAnalyticsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against ad_impression_device_analytics records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `list(self, q: str, pivot: str, time_granularity: str, date_range: str, campaigns: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult[list[AdAnalyticsRecord]]`
    :   Returns ad analytics data pivoted by impression device type. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by impression device type.
        
        
        Args:
            q: LinkedIn API finder method for querying ad analytics
            pivot: Pivot dimension for analytics grouping
            time_granularity: Time granularity for analytics data
            date_range: Date range in LinkedIn format, e.g. (start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31))
            campaigns: List of campaign URNs, e.g. List(urn%3Ali%3AsponsoredCampaign%3A123)
            fields: Comma-separated list of metric fields to return
            **kwargs: Additional parameters
        
        Returns:
            AdImpressionDeviceAnalyticsListResult

<a id="AdMemberCompanyAnalyticsQuery"></a>

`AdMemberCompanyAnalyticsQuery(connector: LinkedinAdsConnector)`
:   Query class for AdMemberCompanyAnalytics entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdMemberCompanyAnalyticsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberCompanyAnalyticsSearchData]`
    :   Search ad_member_company_analytics records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdMemberCompanyAnalyticsSearchFilter):
        - action_clicks: The number of clicks on action buttons in the ad.
        - ad_unit_clicks: The number of clicks on ad unit components.
        - approximate_member_reach: An approximation of unique ad impressions.
        - card_clicks: The number of clicks on interactive card elements.
        - card_impressions: The number of times interactive cards were displayed.
        - clicks: Total number of clicks on the ad.
        - comment_likes: The count of likes on comments related to the ad.
        - comments: The number of comments on the ad.
        - company_page_clicks: Clicks on the company page associated with the ad.
        - conversion_value_in_local_currency: Conversion value in the local currency.
        - cost_in_local_currency: Cost of ad campaign in the local currency.
        - cost_in_usd: Cost of ad campaign in USD.
        - document_completions: Number of completions for document views.
        - document_first_quartile_completions: Completions for first quartile of document views.
        - document_midpoint_completions: Completions for midpoint of document views.
        - document_third_quartile_completions: Completions for third quartile of document views.
        - download_clicks: Clicks on download links in the ad.
        - end_date: End date of the ad analytics data.
        - external_website_conversions: Conversions that lead to external websites.
        - external_website_post_click_conversions: Post-click conversions on external websites.
        - external_website_post_view_conversions: Post-view conversions on external websites.
        - follows: Number of follows generated by the ad.
        - full_screen_plays: Number of times videos were played in fullscreen mode.
        - impressions: Total number of times the ad was displayed.
        - job_applications: Number of job applications initiated through the ad.
        - job_apply_clicks: Clicks on apply job button in the ad.
        - landing_page_clicks: Clicks on the landing page associated with the ad.
        - lead_generation_mail_contact_info_shares: Shares of contact information through lead generation.
        - lead_generation_mail_interested_clicks: Clicks on expressing interest through lead generation mail.
        - likes: Total likes received on the ad.
        - one_click_lead_form_opens: Number of times lead forms were opened in one click.
        - one_click_leads: Leads generated in one click.
        - opens: The number of times the ad was opened or expanded.
        - other_engagements: Engagements other than clicks on the ad.
        - pivot_values: Values used for pivoting the analytics.
        - string_of_pivot_values: Comma-separated string of pivot values for this analytics record
        - post_click_job_applications: Job applications initiated post-clicking on the ad.
        - post_click_job_apply_clicks: Clicks on apply job button post-clicking on the ad.
        - post_click_registrations: Registrations completed post-clicking on the ad.
        - post_view_job_applications: Job applications initiated post-viewing the ad.
        - post_view_job_apply_clicks: Clicks on apply job button post-viewing the ad.
        - post_view_registrations: Registrations completed post-viewing the ad.
        - reactions: Total reactions (e.g., like, love, celebrate) on the ad.
        - registrations: Total registrations completed through the ad.
        - sends: Number of messages sent through the ad.
        - shares: Total shares generated by the ad.
        - start_date: Start date of the ad analytics data.
        - talent_leads: Number of leads related to talent acquisition.
        - text_url_clicks: Clicks on text URLs within the ad.
        - total_engagements: Total number of engagements on the ad.
        - valid_work_email_leads: Leads generated through valid work emails.
        - video_completions: Number of times videos were watched till completion.
        - video_first_quartile_completions: Completions for first quartile of video views.
        - video_midpoint_completions: Completions for midpoint of video views.
        - video_starts: Total video starts initiated by users.
        - video_third_quartile_completions: Completions for third quartile of video views.
        - video_views: Total views of videos in the ad.
        - viral_card_clicks: Clicks on interactive card components in viral distribution.
        - viral_card_impressions: Impressions of interactive cards in viral distribution.
        - viral_clicks: Total clicks in viral distribution of the ad.
        - viral_comment_likes: Likes received on comments in viral distribution.
        - viral_comments: Number of comments in viral distribution of the ad.
        - viral_company_page_clicks: Clicks on the company page in viral distribution.
        - viral_document_completions: Complete views of documents in viral distribution.
        - viral_document_first_quartile_completions: First quartile completions of documents in viral distribution.
        - viral_document_midpoint_completions: Midpoint completions of documents in viral distribution.
        - viral_document_third_quartile_completions: Third quartile completions of documents in viral distribution.
        - viral_download_clicks: Clicks on downloads in viral distribution of the ad.
        - viral_external_website_conversions: External website conversions in viral distribution.
        - viral_external_website_post_click_conversions: Post-click conversions on external websites in viral distribution.
        - viral_external_website_post_view_conversions: Post-view conversions on external websites in viral distribution.
        - viral_follows: Follows generated in viral distribution of the ad.
        - viral_full_screen_plays: Fullscreen video plays in viral distribution.
        - viral_impressions: Total impressions in viral distribution of the ad.
        - viral_job_applications: Job applications initiated in viral distribution.
        - viral_job_apply_clicks: Clicks on apply job button in viral distribution of the ad.
        - viral_landing_page_clicks: Clicks on landing page in viral distribution.
        - viral_likes: Total likes in viral distribution of the ad.
        - viral_one_click_lead_form_opens: One-click lead form opens in viral distribution.
        - viral_one_click_leads: Leads generated in one click in viral distribution.
        - viral_other_engagements: Other engagements in viral distribution of the ad.
        - viral_post_click_job_applications: Job applications initiated post-clicking in viral distribution.
        - viral_post_click_job_apply_clicks: Clicks on apply job button post-clicking in viral distribution.
        - viral_post_click_registrations: Registrations completed post-clicking in viral distribution.
        - viral_post_view_job_applications: Job applications initiated post-viewing in viral distribution.
        - viral_post_view_job_apply_clicks: Clicks on apply job button post-viewing in viral distribution.
        - viral_post_view_registrations: Registrations completed post-viewing in viral distribution.
        - viral_reactions: Total reactions in viral distribution of the ad.
        - viral_registrations: Total registrations in viral distribution of the ad.
        - viral_shares: Total shares in viral distribution of the ad.
        - viral_total_engagements: Total engagements in viral distribution of the ad.
        - viral_video_completions: Completions of videos in viral distribution.
        - viral_video_first_quartile_completions: First quartile completions of videos in viral distribution.
        - viral_video_midpoint_completions: Midpoint completions of videos in viral distribution.
        - viral_video_starts: Total video starts in viral distribution of the ad.
        - viral_video_third_quartile_completions: Third quartile completions of videos in viral distribution.
        - viral_video_views: Total views of videos in viral distribution of the ad.
        - pivot: Pivot dimension used for this analytics record
        - sponsored_campaign: URN of the sponsored campaign this analytics record belongs to
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdMemberCompanyAnalyticsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against ad_member_company_analytics records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `list(self, q: str, pivot: str, time_granularity: str, date_range: str, campaigns: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult[list[AdAnalyticsRecord]]`
    :   Returns ad analytics data pivoted by member company. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member company.
        
        
        Args:
            q: LinkedIn API finder method for querying ad analytics
            pivot: Pivot dimension for analytics grouping
            time_granularity: Time granularity for analytics data
            date_range: Date range in LinkedIn format, e.g. (start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31))
            campaigns: List of campaign URNs, e.g. List(urn%3Ali%3AsponsoredCampaign%3A123)
            fields: Comma-separated list of metric fields to return
            **kwargs: Additional parameters
        
        Returns:
            AdMemberCompanyAnalyticsListResult

<a id="AdMemberCompanySizeAnalyticsQuery"></a>

`AdMemberCompanySizeAnalyticsQuery(connector: LinkedinAdsConnector)`
:   Query class for AdMemberCompanySizeAnalytics entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdMemberCompanySizeAnalyticsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberCompanySizeAnalyticsSearchData]`
    :   Search ad_member_company_size_analytics records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdMemberCompanySizeAnalyticsSearchFilter):
        - action_clicks: The number of clicks on action buttons in the ad.
        - ad_unit_clicks: The number of clicks on ad unit components.
        - approximate_member_reach: An approximation of unique ad impressions.
        - card_clicks: The number of clicks on interactive card elements.
        - card_impressions: The number of times interactive cards were displayed.
        - clicks: Total number of clicks on the ad.
        - comment_likes: The count of likes on comments related to the ad.
        - comments: The number of comments on the ad.
        - company_page_clicks: Clicks on the company page associated with the ad.
        - conversion_value_in_local_currency: Conversion value in the local currency.
        - cost_in_local_currency: Cost of ad campaign in the local currency.
        - cost_in_usd: Cost of ad campaign in USD.
        - document_completions: Number of completions for document views.
        - document_first_quartile_completions: Completions for first quartile of document views.
        - document_midpoint_completions: Completions for midpoint of document views.
        - document_third_quartile_completions: Completions for third quartile of document views.
        - download_clicks: Clicks on download links in the ad.
        - end_date: End date of the ad analytics data.
        - external_website_conversions: Conversions that lead to external websites.
        - external_website_post_click_conversions: Post-click conversions on external websites.
        - external_website_post_view_conversions: Post-view conversions on external websites.
        - follows: Number of follows generated by the ad.
        - full_screen_plays: Number of times videos were played in fullscreen mode.
        - impressions: Total number of times the ad was displayed.
        - job_applications: Number of job applications initiated through the ad.
        - job_apply_clicks: Clicks on apply job button in the ad.
        - landing_page_clicks: Clicks on the landing page associated with the ad.
        - lead_generation_mail_contact_info_shares: Shares of contact information through lead generation.
        - lead_generation_mail_interested_clicks: Clicks on expressing interest through lead generation mail.
        - likes: Total likes received on the ad.
        - one_click_lead_form_opens: Number of times lead forms were opened in one click.
        - one_click_leads: Leads generated in one click.
        - opens: The number of times the ad was opened or expanded.
        - other_engagements: Engagements other than clicks on the ad.
        - pivot_values: Values used for pivoting the analytics.
        - string_of_pivot_values: Comma-separated string of pivot values for this analytics record
        - post_click_job_applications: Job applications initiated post-clicking on the ad.
        - post_click_job_apply_clicks: Clicks on apply job button post-clicking on the ad.
        - post_click_registrations: Registrations completed post-clicking on the ad.
        - post_view_job_applications: Job applications initiated post-viewing the ad.
        - post_view_job_apply_clicks: Clicks on apply job button post-viewing the ad.
        - post_view_registrations: Registrations completed post-viewing the ad.
        - reactions: Total reactions (e.g., like, love, celebrate) on the ad.
        - registrations: Total registrations completed through the ad.
        - sends: Number of messages sent through the ad.
        - shares: Total shares generated by the ad.
        - start_date: Start date of the ad analytics data.
        - talent_leads: Number of leads related to talent acquisition.
        - text_url_clicks: Clicks on text URLs within the ad.
        - total_engagements: Total number of engagements on the ad.
        - valid_work_email_leads: Leads generated through valid work emails.
        - video_completions: Number of times videos were watched till completion.
        - video_first_quartile_completions: Completions for first quartile of video views.
        - video_midpoint_completions: Completions for midpoint of video views.
        - video_starts: Total video starts initiated by users.
        - video_third_quartile_completions: Completions for third quartile of video views.
        - video_views: Total views of videos in the ad.
        - viral_card_clicks: Clicks on interactive card components in viral distribution.
        - viral_card_impressions: Impressions of interactive cards in viral distribution.
        - viral_clicks: Total clicks in viral distribution of the ad.
        - viral_comment_likes: Likes received on comments in viral distribution.
        - viral_comments: Number of comments in viral distribution of the ad.
        - viral_company_page_clicks: Clicks on the company page in viral distribution.
        - viral_document_completions: Complete views of documents in viral distribution.
        - viral_document_first_quartile_completions: First quartile completions of documents in viral distribution.
        - viral_document_midpoint_completions: Midpoint completions of documents in viral distribution.
        - viral_document_third_quartile_completions: Third quartile completions of documents in viral distribution.
        - viral_download_clicks: Clicks on downloads in viral distribution of the ad.
        - viral_external_website_conversions: External website conversions in viral distribution.
        - viral_external_website_post_click_conversions: Post-click conversions on external websites in viral distribution.
        - viral_external_website_post_view_conversions: Post-view conversions on external websites in viral distribution.
        - viral_follows: Follows generated in viral distribution of the ad.
        - viral_full_screen_plays: Fullscreen video plays in viral distribution.
        - viral_impressions: Total impressions in viral distribution of the ad.
        - viral_job_applications: Job applications initiated in viral distribution.
        - viral_job_apply_clicks: Clicks on apply job button in viral distribution of the ad.
        - viral_landing_page_clicks: Clicks on landing page in viral distribution.
        - viral_likes: Total likes in viral distribution of the ad.
        - viral_one_click_lead_form_opens: One-click lead form opens in viral distribution.
        - viral_one_click_leads: Leads generated in one click in viral distribution.
        - viral_other_engagements: Other engagements in viral distribution of the ad.
        - viral_post_click_job_applications: Job applications initiated post-clicking in viral distribution.
        - viral_post_click_job_apply_clicks: Clicks on apply job button post-clicking in viral distribution.
        - viral_post_click_registrations: Registrations completed post-clicking in viral distribution.
        - viral_post_view_job_applications: Job applications initiated post-viewing in viral distribution.
        - viral_post_view_job_apply_clicks: Clicks on apply job button post-viewing in viral distribution.
        - viral_post_view_registrations: Registrations completed post-viewing in viral distribution.
        - viral_reactions: Total reactions in viral distribution of the ad.
        - viral_registrations: Total registrations in viral distribution of the ad.
        - viral_shares: Total shares in viral distribution of the ad.
        - viral_total_engagements: Total engagements in viral distribution of the ad.
        - viral_video_completions: Completions of videos in viral distribution.
        - viral_video_first_quartile_completions: First quartile completions of videos in viral distribution.
        - viral_video_midpoint_completions: Midpoint completions of videos in viral distribution.
        - viral_video_starts: Total video starts in viral distribution of the ad.
        - viral_video_third_quartile_completions: Third quartile completions of videos in viral distribution.
        - viral_video_views: Total views of videos in viral distribution of the ad.
        - pivot: Pivot dimension used for this analytics record
        - sponsored_campaign: URN of the sponsored campaign this analytics record belongs to
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdMemberCompanySizeAnalyticsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against ad_member_company_size_analytics records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `list(self, q: str, pivot: str, time_granularity: str, date_range: str, campaigns: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult[list[AdAnalyticsRecord]]`
    :   Returns ad analytics data pivoted by member company size. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member company size.
        
        
        Args:
            q: LinkedIn API finder method for querying ad analytics
            pivot: Pivot dimension for analytics grouping
            time_granularity: Time granularity for analytics data
            date_range: Date range in LinkedIn format, e.g. (start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31))
            campaigns: List of campaign URNs, e.g. List(urn%3Ali%3AsponsoredCampaign%3A123)
            fields: Comma-separated list of metric fields to return
            **kwargs: Additional parameters
        
        Returns:
            AdMemberCompanySizeAnalyticsListResult

<a id="AdMemberCountryAnalyticsQuery"></a>

`AdMemberCountryAnalyticsQuery(connector: LinkedinAdsConnector)`
:   Query class for AdMemberCountryAnalytics entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdMemberCountryAnalyticsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberCountryAnalyticsSearchData]`
    :   Search ad_member_country_analytics records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdMemberCountryAnalyticsSearchFilter):
        - action_clicks: The number of clicks on action buttons in the ad.
        - ad_unit_clicks: The number of clicks on ad unit components.
        - approximate_member_reach: An approximation of unique ad impressions.
        - card_clicks: The number of clicks on interactive card elements.
        - card_impressions: The number of times interactive cards were displayed.
        - clicks: Total number of clicks on the ad.
        - comment_likes: The count of likes on comments related to the ad.
        - comments: The number of comments on the ad.
        - company_page_clicks: Clicks on the company page associated with the ad.
        - conversion_value_in_local_currency: Conversion value in the local currency.
        - cost_in_local_currency: Cost of ad campaign in the local currency.
        - cost_in_usd: Cost of ad campaign in USD.
        - document_completions: Number of completions for document views.
        - document_first_quartile_completions: Completions for first quartile of document views.
        - document_midpoint_completions: Completions for midpoint of document views.
        - document_third_quartile_completions: Completions for third quartile of document views.
        - download_clicks: Clicks on download links in the ad.
        - end_date: End date of the ad analytics data.
        - external_website_conversions: Conversions that lead to external websites.
        - external_website_post_click_conversions: Post-click conversions on external websites.
        - external_website_post_view_conversions: Post-view conversions on external websites.
        - follows: Number of follows generated by the ad.
        - full_screen_plays: Number of times videos were played in fullscreen mode.
        - impressions: Total number of times the ad was displayed.
        - job_applications: Number of job applications initiated through the ad.
        - job_apply_clicks: Clicks on apply job button in the ad.
        - landing_page_clicks: Clicks on the landing page associated with the ad.
        - lead_generation_mail_contact_info_shares: Shares of contact information through lead generation.
        - lead_generation_mail_interested_clicks: Clicks on expressing interest through lead generation mail.
        - likes: Total likes received on the ad.
        - one_click_lead_form_opens: Number of times lead forms were opened in one click.
        - one_click_leads: Leads generated in one click.
        - opens: The number of times the ad was opened or expanded.
        - other_engagements: Engagements other than clicks on the ad.
        - pivot_values: Values used for pivoting the analytics.
        - string_of_pivot_values: Comma-separated string of pivot values for this analytics record
        - post_click_job_applications: Job applications initiated post-clicking on the ad.
        - post_click_job_apply_clicks: Clicks on apply job button post-clicking on the ad.
        - post_click_registrations: Registrations completed post-clicking on the ad.
        - post_view_job_applications: Job applications initiated post-viewing the ad.
        - post_view_job_apply_clicks: Clicks on apply job button post-viewing the ad.
        - post_view_registrations: Registrations completed post-viewing the ad.
        - reactions: Total reactions (e.g., like, love, celebrate) on the ad.
        - registrations: Total registrations completed through the ad.
        - sends: Number of messages sent through the ad.
        - shares: Total shares generated by the ad.
        - start_date: Start date of the ad analytics data.
        - talent_leads: Number of leads related to talent acquisition.
        - text_url_clicks: Clicks on text URLs within the ad.
        - total_engagements: Total number of engagements on the ad.
        - valid_work_email_leads: Leads generated through valid work emails.
        - video_completions: Number of times videos were watched till completion.
        - video_first_quartile_completions: Completions for first quartile of video views.
        - video_midpoint_completions: Completions for midpoint of video views.
        - video_starts: Total video starts initiated by users.
        - video_third_quartile_completions: Completions for third quartile of video views.
        - video_views: Total views of videos in the ad.
        - viral_card_clicks: Clicks on interactive card components in viral distribution.
        - viral_card_impressions: Impressions of interactive cards in viral distribution.
        - viral_clicks: Total clicks in viral distribution of the ad.
        - viral_comment_likes: Likes received on comments in viral distribution.
        - viral_comments: Number of comments in viral distribution of the ad.
        - viral_company_page_clicks: Clicks on the company page in viral distribution.
        - viral_document_completions: Complete views of documents in viral distribution.
        - viral_document_first_quartile_completions: First quartile completions of documents in viral distribution.
        - viral_document_midpoint_completions: Midpoint completions of documents in viral distribution.
        - viral_document_third_quartile_completions: Third quartile completions of documents in viral distribution.
        - viral_download_clicks: Clicks on downloads in viral distribution of the ad.
        - viral_external_website_conversions: External website conversions in viral distribution.
        - viral_external_website_post_click_conversions: Post-click conversions on external websites in viral distribution.
        - viral_external_website_post_view_conversions: Post-view conversions on external websites in viral distribution.
        - viral_follows: Follows generated in viral distribution of the ad.
        - viral_full_screen_plays: Fullscreen video plays in viral distribution.
        - viral_impressions: Total impressions in viral distribution of the ad.
        - viral_job_applications: Job applications initiated in viral distribution.
        - viral_job_apply_clicks: Clicks on apply job button in viral distribution of the ad.
        - viral_landing_page_clicks: Clicks on landing page in viral distribution.
        - viral_likes: Total likes in viral distribution of the ad.
        - viral_one_click_lead_form_opens: One-click lead form opens in viral distribution.
        - viral_one_click_leads: Leads generated in one click in viral distribution.
        - viral_other_engagements: Other engagements in viral distribution of the ad.
        - viral_post_click_job_applications: Job applications initiated post-clicking in viral distribution.
        - viral_post_click_job_apply_clicks: Clicks on apply job button post-clicking in viral distribution.
        - viral_post_click_registrations: Registrations completed post-clicking in viral distribution.
        - viral_post_view_job_applications: Job applications initiated post-viewing in viral distribution.
        - viral_post_view_job_apply_clicks: Clicks on apply job button post-viewing in viral distribution.
        - viral_post_view_registrations: Registrations completed post-viewing in viral distribution.
        - viral_reactions: Total reactions in viral distribution of the ad.
        - viral_registrations: Total registrations in viral distribution of the ad.
        - viral_shares: Total shares in viral distribution of the ad.
        - viral_total_engagements: Total engagements in viral distribution of the ad.
        - viral_video_completions: Completions of videos in viral distribution.
        - viral_video_first_quartile_completions: First quartile completions of videos in viral distribution.
        - viral_video_midpoint_completions: Midpoint completions of videos in viral distribution.
        - viral_video_starts: Total video starts in viral distribution of the ad.
        - viral_video_third_quartile_completions: Third quartile completions of videos in viral distribution.
        - viral_video_views: Total views of videos in viral distribution of the ad.
        - pivot: Pivot dimension used for this analytics record
        - sponsored_campaign: URN of the sponsored campaign this analytics record belongs to
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdMemberCountryAnalyticsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against ad_member_country_analytics records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `list(self, q: str, pivot: str, time_granularity: str, date_range: str, campaigns: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult[list[AdAnalyticsRecord]]`
    :   Returns ad analytics data pivoted by member country. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member country.
        
        
        Args:
            q: LinkedIn API finder method for querying ad analytics
            pivot: Pivot dimension for analytics grouping
            time_granularity: Time granularity for analytics data
            date_range: Date range in LinkedIn format, e.g. (start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31))
            campaigns: List of campaign URNs, e.g. List(urn%3Ali%3AsponsoredCampaign%3A123)
            fields: Comma-separated list of metric fields to return
            **kwargs: Additional parameters
        
        Returns:
            AdMemberCountryAnalyticsListResult

<a id="AdMemberIndustryAnalyticsQuery"></a>

`AdMemberIndustryAnalyticsQuery(connector: LinkedinAdsConnector)`
:   Query class for AdMemberIndustryAnalytics entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdMemberIndustryAnalyticsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberIndustryAnalyticsSearchData]`
    :   Search ad_member_industry_analytics records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdMemberIndustryAnalyticsSearchFilter):
        - action_clicks: The number of clicks on action buttons in the ad.
        - ad_unit_clicks: The number of clicks on ad unit components.
        - approximate_member_reach: An approximation of unique ad impressions.
        - card_clicks: The number of clicks on interactive card elements.
        - card_impressions: The number of times interactive cards were displayed.
        - clicks: Total number of clicks on the ad.
        - comment_likes: The count of likes on comments related to the ad.
        - comments: The number of comments on the ad.
        - company_page_clicks: Clicks on the company page associated with the ad.
        - conversion_value_in_local_currency: Conversion value in the local currency.
        - cost_in_local_currency: Cost of ad campaign in the local currency.
        - cost_in_usd: Cost of ad campaign in USD.
        - document_completions: Number of completions for document views.
        - document_first_quartile_completions: Completions for first quartile of document views.
        - document_midpoint_completions: Completions for midpoint of document views.
        - document_third_quartile_completions: Completions for third quartile of document views.
        - download_clicks: Clicks on download links in the ad.
        - end_date: End date of the ad analytics data.
        - external_website_conversions: Conversions that lead to external websites.
        - external_website_post_click_conversions: Post-click conversions on external websites.
        - external_website_post_view_conversions: Post-view conversions on external websites.
        - follows: Number of follows generated by the ad.
        - full_screen_plays: Number of times videos were played in fullscreen mode.
        - impressions: Total number of times the ad was displayed.
        - job_applications: Number of job applications initiated through the ad.
        - job_apply_clicks: Clicks on apply job button in the ad.
        - landing_page_clicks: Clicks on the landing page associated with the ad.
        - lead_generation_mail_contact_info_shares: Shares of contact information through lead generation.
        - lead_generation_mail_interested_clicks: Clicks on expressing interest through lead generation mail.
        - likes: Total likes received on the ad.
        - one_click_lead_form_opens: Number of times lead forms were opened in one click.
        - one_click_leads: Leads generated in one click.
        - opens: The number of times the ad was opened or expanded.
        - other_engagements: Engagements other than clicks on the ad.
        - pivot_values: Values used for pivoting the analytics.
        - string_of_pivot_values: Comma-separated string of pivot values for this analytics record
        - post_click_job_applications: Job applications initiated post-clicking on the ad.
        - post_click_job_apply_clicks: Clicks on apply job button post-clicking on the ad.
        - post_click_registrations: Registrations completed post-clicking on the ad.
        - post_view_job_applications: Job applications initiated post-viewing the ad.
        - post_view_job_apply_clicks: Clicks on apply job button post-viewing the ad.
        - post_view_registrations: Registrations completed post-viewing the ad.
        - reactions: Total reactions (e.g., like, love, celebrate) on the ad.
        - registrations: Total registrations completed through the ad.
        - sends: Number of messages sent through the ad.
        - shares: Total shares generated by the ad.
        - start_date: Start date of the ad analytics data.
        - talent_leads: Number of leads related to talent acquisition.
        - text_url_clicks: Clicks on text URLs within the ad.
        - total_engagements: Total number of engagements on the ad.
        - valid_work_email_leads: Leads generated through valid work emails.
        - video_completions: Number of times videos were watched till completion.
        - video_first_quartile_completions: Completions for first quartile of video views.
        - video_midpoint_completions: Completions for midpoint of video views.
        - video_starts: Total video starts initiated by users.
        - video_third_quartile_completions: Completions for third quartile of video views.
        - video_views: Total views of videos in the ad.
        - viral_card_clicks: Clicks on interactive card components in viral distribution.
        - viral_card_impressions: Impressions of interactive cards in viral distribution.
        - viral_clicks: Total clicks in viral distribution of the ad.
        - viral_comment_likes: Likes received on comments in viral distribution.
        - viral_comments: Number of comments in viral distribution of the ad.
        - viral_company_page_clicks: Clicks on the company page in viral distribution.
        - viral_document_completions: Complete views of documents in viral distribution.
        - viral_document_first_quartile_completions: First quartile completions of documents in viral distribution.
        - viral_document_midpoint_completions: Midpoint completions of documents in viral distribution.
        - viral_document_third_quartile_completions: Third quartile completions of documents in viral distribution.
        - viral_download_clicks: Clicks on downloads in viral distribution of the ad.
        - viral_external_website_conversions: External website conversions in viral distribution.
        - viral_external_website_post_click_conversions: Post-click conversions on external websites in viral distribution.
        - viral_external_website_post_view_conversions: Post-view conversions on external websites in viral distribution.
        - viral_follows: Follows generated in viral distribution of the ad.
        - viral_full_screen_plays: Fullscreen video plays in viral distribution.
        - viral_impressions: Total impressions in viral distribution of the ad.
        - viral_job_applications: Job applications initiated in viral distribution.
        - viral_job_apply_clicks: Clicks on apply job button in viral distribution of the ad.
        - viral_landing_page_clicks: Clicks on landing page in viral distribution.
        - viral_likes: Total likes in viral distribution of the ad.
        - viral_one_click_lead_form_opens: One-click lead form opens in viral distribution.
        - viral_one_click_leads: Leads generated in one click in viral distribution.
        - viral_other_engagements: Other engagements in viral distribution of the ad.
        - viral_post_click_job_applications: Job applications initiated post-clicking in viral distribution.
        - viral_post_click_job_apply_clicks: Clicks on apply job button post-clicking in viral distribution.
        - viral_post_click_registrations: Registrations completed post-clicking in viral distribution.
        - viral_post_view_job_applications: Job applications initiated post-viewing in viral distribution.
        - viral_post_view_job_apply_clicks: Clicks on apply job button post-viewing in viral distribution.
        - viral_post_view_registrations: Registrations completed post-viewing in viral distribution.
        - viral_reactions: Total reactions in viral distribution of the ad.
        - viral_registrations: Total registrations in viral distribution of the ad.
        - viral_shares: Total shares in viral distribution of the ad.
        - viral_total_engagements: Total engagements in viral distribution of the ad.
        - viral_video_completions: Completions of videos in viral distribution.
        - viral_video_first_quartile_completions: First quartile completions of videos in viral distribution.
        - viral_video_midpoint_completions: Midpoint completions of videos in viral distribution.
        - viral_video_starts: Total video starts in viral distribution of the ad.
        - viral_video_third_quartile_completions: Third quartile completions of videos in viral distribution.
        - viral_video_views: Total views of videos in viral distribution of the ad.
        - pivot: Pivot dimension used for this analytics record
        - sponsored_campaign: URN of the sponsored campaign this analytics record belongs to
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdMemberIndustryAnalyticsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against ad_member_industry_analytics records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `list(self, q: str, pivot: str, time_granularity: str, date_range: str, campaigns: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult[list[AdAnalyticsRecord]]`
    :   Returns ad analytics data pivoted by member industry. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member industry.
        
        
        Args:
            q: LinkedIn API finder method for querying ad analytics
            pivot: Pivot dimension for analytics grouping
            time_granularity: Time granularity for analytics data
            date_range: Date range in LinkedIn format, e.g. (start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31))
            campaigns: List of campaign URNs, e.g. List(urn%3Ali%3AsponsoredCampaign%3A123)
            fields: Comma-separated list of metric fields to return
            **kwargs: Additional parameters
        
        Returns:
            AdMemberIndustryAnalyticsListResult

<a id="AdMemberJobFunctionAnalyticsQuery"></a>

`AdMemberJobFunctionAnalyticsQuery(connector: LinkedinAdsConnector)`
:   Query class for AdMemberJobFunctionAnalytics entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdMemberJobFunctionAnalyticsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberJobFunctionAnalyticsSearchData]`
    :   Search ad_member_job_function_analytics records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdMemberJobFunctionAnalyticsSearchFilter):
        - action_clicks: The number of clicks on action buttons in the ad.
        - ad_unit_clicks: The number of clicks on ad unit components.
        - approximate_member_reach: An approximation of unique ad impressions.
        - card_clicks: The number of clicks on interactive card elements.
        - card_impressions: The number of times interactive cards were displayed.
        - clicks: Total number of clicks on the ad.
        - comment_likes: The count of likes on comments related to the ad.
        - comments: The number of comments on the ad.
        - company_page_clicks: Clicks on the company page associated with the ad.
        - conversion_value_in_local_currency: Conversion value in the local currency.
        - cost_in_local_currency: Cost of ad campaign in the local currency.
        - cost_in_usd: Cost of ad campaign in USD.
        - document_completions: Number of completions for document views.
        - document_first_quartile_completions: Completions for first quartile of document views.
        - document_midpoint_completions: Completions for midpoint of document views.
        - document_third_quartile_completions: Completions for third quartile of document views.
        - download_clicks: Clicks on download links in the ad.
        - end_date: End date of the ad analytics data.
        - external_website_conversions: Conversions that lead to external websites.
        - external_website_post_click_conversions: Post-click conversions on external websites.
        - external_website_post_view_conversions: Post-view conversions on external websites.
        - follows: Number of follows generated by the ad.
        - full_screen_plays: Number of times videos were played in fullscreen mode.
        - impressions: Total number of times the ad was displayed.
        - job_applications: Number of job applications initiated through the ad.
        - job_apply_clicks: Clicks on apply job button in the ad.
        - landing_page_clicks: Clicks on the landing page associated with the ad.
        - lead_generation_mail_contact_info_shares: Shares of contact information through lead generation.
        - lead_generation_mail_interested_clicks: Clicks on expressing interest through lead generation mail.
        - likes: Total likes received on the ad.
        - one_click_lead_form_opens: Number of times lead forms were opened in one click.
        - one_click_leads: Leads generated in one click.
        - opens: The number of times the ad was opened or expanded.
        - other_engagements: Engagements other than clicks on the ad.
        - pivot_values: Values used for pivoting the analytics.
        - string_of_pivot_values: Comma-separated string of pivot values for this analytics record
        - post_click_job_applications: Job applications initiated post-clicking on the ad.
        - post_click_job_apply_clicks: Clicks on apply job button post-clicking on the ad.
        - post_click_registrations: Registrations completed post-clicking on the ad.
        - post_view_job_applications: Job applications initiated post-viewing the ad.
        - post_view_job_apply_clicks: Clicks on apply job button post-viewing the ad.
        - post_view_registrations: Registrations completed post-viewing the ad.
        - reactions: Total reactions (e.g., like, love, celebrate) on the ad.
        - registrations: Total registrations completed through the ad.
        - sends: Number of messages sent through the ad.
        - shares: Total shares generated by the ad.
        - start_date: Start date of the ad analytics data.
        - talent_leads: Number of leads related to talent acquisition.
        - text_url_clicks: Clicks on text URLs within the ad.
        - total_engagements: Total number of engagements on the ad.
        - valid_work_email_leads: Leads generated through valid work emails.
        - video_completions: Number of times videos were watched till completion.
        - video_first_quartile_completions: Completions for first quartile of video views.
        - video_midpoint_completions: Completions for midpoint of video views.
        - video_starts: Total video starts initiated by users.
        - video_third_quartile_completions: Completions for third quartile of video views.
        - video_views: Total views of videos in the ad.
        - viral_card_clicks: Clicks on interactive card components in viral distribution.
        - viral_card_impressions: Impressions of interactive cards in viral distribution.
        - viral_clicks: Total clicks in viral distribution of the ad.
        - viral_comment_likes: Likes received on comments in viral distribution.
        - viral_comments: Number of comments in viral distribution of the ad.
        - viral_company_page_clicks: Clicks on the company page in viral distribution.
        - viral_document_completions: Complete views of documents in viral distribution.
        - viral_document_first_quartile_completions: First quartile completions of documents in viral distribution.
        - viral_document_midpoint_completions: Midpoint completions of documents in viral distribution.
        - viral_document_third_quartile_completions: Third quartile completions of documents in viral distribution.
        - viral_download_clicks: Clicks on downloads in viral distribution of the ad.
        - viral_external_website_conversions: External website conversions in viral distribution.
        - viral_external_website_post_click_conversions: Post-click conversions on external websites in viral distribution.
        - viral_external_website_post_view_conversions: Post-view conversions on external websites in viral distribution.
        - viral_follows: Follows generated in viral distribution of the ad.
        - viral_full_screen_plays: Fullscreen video plays in viral distribution.
        - viral_impressions: Total impressions in viral distribution of the ad.
        - viral_job_applications: Job applications initiated in viral distribution.
        - viral_job_apply_clicks: Clicks on apply job button in viral distribution of the ad.
        - viral_landing_page_clicks: Clicks on landing page in viral distribution.
        - viral_likes: Total likes in viral distribution of the ad.
        - viral_one_click_lead_form_opens: One-click lead form opens in viral distribution.
        - viral_one_click_leads: Leads generated in one click in viral distribution.
        - viral_other_engagements: Other engagements in viral distribution of the ad.
        - viral_post_click_job_applications: Job applications initiated post-clicking in viral distribution.
        - viral_post_click_job_apply_clicks: Clicks on apply job button post-clicking in viral distribution.
        - viral_post_click_registrations: Registrations completed post-clicking in viral distribution.
        - viral_post_view_job_applications: Job applications initiated post-viewing in viral distribution.
        - viral_post_view_job_apply_clicks: Clicks on apply job button post-viewing in viral distribution.
        - viral_post_view_registrations: Registrations completed post-viewing in viral distribution.
        - viral_reactions: Total reactions in viral distribution of the ad.
        - viral_registrations: Total registrations in viral distribution of the ad.
        - viral_shares: Total shares in viral distribution of the ad.
        - viral_total_engagements: Total engagements in viral distribution of the ad.
        - viral_video_completions: Completions of videos in viral distribution.
        - viral_video_first_quartile_completions: First quartile completions of videos in viral distribution.
        - viral_video_midpoint_completions: Midpoint completions of videos in viral distribution.
        - viral_video_starts: Total video starts in viral distribution of the ad.
        - viral_video_third_quartile_completions: Third quartile completions of videos in viral distribution.
        - viral_video_views: Total views of videos in viral distribution of the ad.
        - pivot: Pivot dimension used for this analytics record
        - sponsored_campaign: URN of the sponsored campaign this analytics record belongs to
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdMemberJobFunctionAnalyticsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against ad_member_job_function_analytics records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `list(self, q: str, pivot: str, time_granularity: str, date_range: str, campaigns: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult[list[AdAnalyticsRecord]]`
    :   Returns ad analytics data pivoted by member job function. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member job function.
        
        
        Args:
            q: LinkedIn API finder method for querying ad analytics
            pivot: Pivot dimension for analytics grouping
            time_granularity: Time granularity for analytics data
            date_range: Date range in LinkedIn format, e.g. (start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31))
            campaigns: List of campaign URNs, e.g. List(urn%3Ali%3AsponsoredCampaign%3A123)
            fields: Comma-separated list of metric fields to return
            **kwargs: Additional parameters
        
        Returns:
            AdMemberJobFunctionAnalyticsListResult

<a id="AdMemberJobTitleAnalyticsQuery"></a>

`AdMemberJobTitleAnalyticsQuery(connector: LinkedinAdsConnector)`
:   Query class for AdMemberJobTitleAnalytics entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdMemberJobTitleAnalyticsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberJobTitleAnalyticsSearchData]`
    :   Search ad_member_job_title_analytics records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdMemberJobTitleAnalyticsSearchFilter):
        - action_clicks: The number of clicks on action buttons in the ad.
        - ad_unit_clicks: The number of clicks on ad unit components.
        - approximate_member_reach: An approximation of unique ad impressions.
        - card_clicks: The number of clicks on interactive card elements.
        - card_impressions: The number of times interactive cards were displayed.
        - clicks: Total number of clicks on the ad.
        - comment_likes: The count of likes on comments related to the ad.
        - comments: The number of comments on the ad.
        - company_page_clicks: Clicks on the company page associated with the ad.
        - conversion_value_in_local_currency: Conversion value in the local currency.
        - cost_in_local_currency: Cost of ad campaign in the local currency.
        - cost_in_usd: Cost of ad campaign in USD.
        - document_completions: Number of completions for document views.
        - document_first_quartile_completions: Completions for first quartile of document views.
        - document_midpoint_completions: Completions for midpoint of document views.
        - document_third_quartile_completions: Completions for third quartile of document views.
        - download_clicks: Clicks on download links in the ad.
        - end_date: End date of the ad analytics data.
        - external_website_conversions: Conversions that lead to external websites.
        - external_website_post_click_conversions: Post-click conversions on external websites.
        - external_website_post_view_conversions: Post-view conversions on external websites.
        - follows: Number of follows generated by the ad.
        - full_screen_plays: Number of times videos were played in fullscreen mode.
        - impressions: Total number of times the ad was displayed.
        - job_applications: Number of job applications initiated through the ad.
        - job_apply_clicks: Clicks on apply job button in the ad.
        - landing_page_clicks: Clicks on the landing page associated with the ad.
        - lead_generation_mail_contact_info_shares: Shares of contact information through lead generation.
        - lead_generation_mail_interested_clicks: Clicks on expressing interest through lead generation mail.
        - likes: Total likes received on the ad.
        - one_click_lead_form_opens: Number of times lead forms were opened in one click.
        - one_click_leads: Leads generated in one click.
        - opens: The number of times the ad was opened or expanded.
        - other_engagements: Engagements other than clicks on the ad.
        - pivot_values: Values used for pivoting the analytics.
        - string_of_pivot_values: Comma-separated string of pivot values for this analytics record
        - post_click_job_applications: Job applications initiated post-clicking on the ad.
        - post_click_job_apply_clicks: Clicks on apply job button post-clicking on the ad.
        - post_click_registrations: Registrations completed post-clicking on the ad.
        - post_view_job_applications: Job applications initiated post-viewing the ad.
        - post_view_job_apply_clicks: Clicks on apply job button post-viewing the ad.
        - post_view_registrations: Registrations completed post-viewing the ad.
        - reactions: Total reactions (e.g., like, love, celebrate) on the ad.
        - registrations: Total registrations completed through the ad.
        - sends: Number of messages sent through the ad.
        - shares: Total shares generated by the ad.
        - start_date: Start date of the ad analytics data.
        - talent_leads: Number of leads related to talent acquisition.
        - text_url_clicks: Clicks on text URLs within the ad.
        - total_engagements: Total number of engagements on the ad.
        - valid_work_email_leads: Leads generated through valid work emails.
        - video_completions: Number of times videos were watched till completion.
        - video_first_quartile_completions: Completions for first quartile of video views.
        - video_midpoint_completions: Completions for midpoint of video views.
        - video_starts: Total video starts initiated by users.
        - video_third_quartile_completions: Completions for third quartile of video views.
        - video_views: Total views of videos in the ad.
        - viral_card_clicks: Clicks on interactive card components in viral distribution.
        - viral_card_impressions: Impressions of interactive cards in viral distribution.
        - viral_clicks: Total clicks in viral distribution of the ad.
        - viral_comment_likes: Likes received on comments in viral distribution.
        - viral_comments: Number of comments in viral distribution of the ad.
        - viral_company_page_clicks: Clicks on the company page in viral distribution.
        - viral_document_completions: Complete views of documents in viral distribution.
        - viral_document_first_quartile_completions: First quartile completions of documents in viral distribution.
        - viral_document_midpoint_completions: Midpoint completions of documents in viral distribution.
        - viral_document_third_quartile_completions: Third quartile completions of documents in viral distribution.
        - viral_download_clicks: Clicks on downloads in viral distribution of the ad.
        - viral_external_website_conversions: External website conversions in viral distribution.
        - viral_external_website_post_click_conversions: Post-click conversions on external websites in viral distribution.
        - viral_external_website_post_view_conversions: Post-view conversions on external websites in viral distribution.
        - viral_follows: Follows generated in viral distribution of the ad.
        - viral_full_screen_plays: Fullscreen video plays in viral distribution.
        - viral_impressions: Total impressions in viral distribution of the ad.
        - viral_job_applications: Job applications initiated in viral distribution.
        - viral_job_apply_clicks: Clicks on apply job button in viral distribution of the ad.
        - viral_landing_page_clicks: Clicks on landing page in viral distribution.
        - viral_likes: Total likes in viral distribution of the ad.
        - viral_one_click_lead_form_opens: One-click lead form opens in viral distribution.
        - viral_one_click_leads: Leads generated in one click in viral distribution.
        - viral_other_engagements: Other engagements in viral distribution of the ad.
        - viral_post_click_job_applications: Job applications initiated post-clicking in viral distribution.
        - viral_post_click_job_apply_clicks: Clicks on apply job button post-clicking in viral distribution.
        - viral_post_click_registrations: Registrations completed post-clicking in viral distribution.
        - viral_post_view_job_applications: Job applications initiated post-viewing in viral distribution.
        - viral_post_view_job_apply_clicks: Clicks on apply job button post-viewing in viral distribution.
        - viral_post_view_registrations: Registrations completed post-viewing in viral distribution.
        - viral_reactions: Total reactions in viral distribution of the ad.
        - viral_registrations: Total registrations in viral distribution of the ad.
        - viral_shares: Total shares in viral distribution of the ad.
        - viral_total_engagements: Total engagements in viral distribution of the ad.
        - viral_video_completions: Completions of videos in viral distribution.
        - viral_video_first_quartile_completions: First quartile completions of videos in viral distribution.
        - viral_video_midpoint_completions: Midpoint completions of videos in viral distribution.
        - viral_video_starts: Total video starts in viral distribution of the ad.
        - viral_video_third_quartile_completions: Third quartile completions of videos in viral distribution.
        - viral_video_views: Total views of videos in viral distribution of the ad.
        - pivot: Pivot dimension used for this analytics record
        - sponsored_campaign: URN of the sponsored campaign this analytics record belongs to
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdMemberJobTitleAnalyticsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against ad_member_job_title_analytics records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `list(self, q: str, pivot: str, time_granularity: str, date_range: str, campaigns: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult[list[AdAnalyticsRecord]]`
    :   Returns ad analytics data pivoted by member job title. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member job title.
        
        
        Args:
            q: LinkedIn API finder method for querying ad analytics
            pivot: Pivot dimension for analytics grouping
            time_granularity: Time granularity for analytics data
            date_range: Date range in LinkedIn format, e.g. (start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31))
            campaigns: List of campaign URNs, e.g. List(urn%3Ali%3AsponsoredCampaign%3A123)
            fields: Comma-separated list of metric fields to return
            **kwargs: Additional parameters
        
        Returns:
            AdMemberJobTitleAnalyticsListResult

<a id="AdMemberRegionAnalyticsQuery"></a>

`AdMemberRegionAnalyticsQuery(connector: LinkedinAdsConnector)`
:   Query class for AdMemberRegionAnalytics entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdMemberRegionAnalyticsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberRegionAnalyticsSearchData]`
    :   Search ad_member_region_analytics records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdMemberRegionAnalyticsSearchFilter):
        - action_clicks: The number of clicks on action buttons in the ad.
        - ad_unit_clicks: The number of clicks on ad unit components.
        - approximate_member_reach: An approximation of unique ad impressions.
        - card_clicks: The number of clicks on interactive card elements.
        - card_impressions: The number of times interactive cards were displayed.
        - clicks: Total number of clicks on the ad.
        - comment_likes: The count of likes on comments related to the ad.
        - comments: The number of comments on the ad.
        - company_page_clicks: Clicks on the company page associated with the ad.
        - conversion_value_in_local_currency: Conversion value in the local currency.
        - cost_in_local_currency: Cost of ad campaign in the local currency.
        - cost_in_usd: Cost of ad campaign in USD.
        - document_completions: Number of completions for document views.
        - document_first_quartile_completions: Completions for first quartile of document views.
        - document_midpoint_completions: Completions for midpoint of document views.
        - document_third_quartile_completions: Completions for third quartile of document views.
        - download_clicks: Clicks on download links in the ad.
        - end_date: End date of the ad analytics data.
        - external_website_conversions: Conversions that lead to external websites.
        - external_website_post_click_conversions: Post-click conversions on external websites.
        - external_website_post_view_conversions: Post-view conversions on external websites.
        - follows: Number of follows generated by the ad.
        - full_screen_plays: Number of times videos were played in fullscreen mode.
        - impressions: Total number of times the ad was displayed.
        - job_applications: Number of job applications initiated through the ad.
        - job_apply_clicks: Clicks on apply job button in the ad.
        - landing_page_clicks: Clicks on the landing page associated with the ad.
        - lead_generation_mail_contact_info_shares: Shares of contact information through lead generation.
        - lead_generation_mail_interested_clicks: Clicks on expressing interest through lead generation mail.
        - likes: Total likes received on the ad.
        - one_click_lead_form_opens: Number of times lead forms were opened in one click.
        - one_click_leads: Leads generated in one click.
        - opens: The number of times the ad was opened or expanded.
        - other_engagements: Engagements other than clicks on the ad.
        - pivot_values: Values used for pivoting the analytics.
        - string_of_pivot_values: Comma-separated string of pivot values for this analytics record
        - post_click_job_applications: Job applications initiated post-clicking on the ad.
        - post_click_job_apply_clicks: Clicks on apply job button post-clicking on the ad.
        - post_click_registrations: Registrations completed post-clicking on the ad.
        - post_view_job_applications: Job applications initiated post-viewing the ad.
        - post_view_job_apply_clicks: Clicks on apply job button post-viewing the ad.
        - post_view_registrations: Registrations completed post-viewing the ad.
        - reactions: Total reactions (e.g., like, love, celebrate) on the ad.
        - registrations: Total registrations completed through the ad.
        - sends: Number of messages sent through the ad.
        - shares: Total shares generated by the ad.
        - start_date: Start date of the ad analytics data.
        - talent_leads: Number of leads related to talent acquisition.
        - text_url_clicks: Clicks on text URLs within the ad.
        - total_engagements: Total number of engagements on the ad.
        - valid_work_email_leads: Leads generated through valid work emails.
        - video_completions: Number of times videos were watched till completion.
        - video_first_quartile_completions: Completions for first quartile of video views.
        - video_midpoint_completions: Completions for midpoint of video views.
        - video_starts: Total video starts initiated by users.
        - video_third_quartile_completions: Completions for third quartile of video views.
        - video_views: Total views of videos in the ad.
        - viral_card_clicks: Clicks on interactive card components in viral distribution.
        - viral_card_impressions: Impressions of interactive cards in viral distribution.
        - viral_clicks: Total clicks in viral distribution of the ad.
        - viral_comment_likes: Likes received on comments in viral distribution.
        - viral_comments: Number of comments in viral distribution of the ad.
        - viral_company_page_clicks: Clicks on the company page in viral distribution.
        - viral_document_completions: Complete views of documents in viral distribution.
        - viral_document_first_quartile_completions: First quartile completions of documents in viral distribution.
        - viral_document_midpoint_completions: Midpoint completions of documents in viral distribution.
        - viral_document_third_quartile_completions: Third quartile completions of documents in viral distribution.
        - viral_download_clicks: Clicks on downloads in viral distribution of the ad.
        - viral_external_website_conversions: External website conversions in viral distribution.
        - viral_external_website_post_click_conversions: Post-click conversions on external websites in viral distribution.
        - viral_external_website_post_view_conversions: Post-view conversions on external websites in viral distribution.
        - viral_follows: Follows generated in viral distribution of the ad.
        - viral_full_screen_plays: Fullscreen video plays in viral distribution.
        - viral_impressions: Total impressions in viral distribution of the ad.
        - viral_job_applications: Job applications initiated in viral distribution.
        - viral_job_apply_clicks: Clicks on apply job button in viral distribution of the ad.
        - viral_landing_page_clicks: Clicks on landing page in viral distribution.
        - viral_likes: Total likes in viral distribution of the ad.
        - viral_one_click_lead_form_opens: One-click lead form opens in viral distribution.
        - viral_one_click_leads: Leads generated in one click in viral distribution.
        - viral_other_engagements: Other engagements in viral distribution of the ad.
        - viral_post_click_job_applications: Job applications initiated post-clicking in viral distribution.
        - viral_post_click_job_apply_clicks: Clicks on apply job button post-clicking in viral distribution.
        - viral_post_click_registrations: Registrations completed post-clicking in viral distribution.
        - viral_post_view_job_applications: Job applications initiated post-viewing in viral distribution.
        - viral_post_view_job_apply_clicks: Clicks on apply job button post-viewing in viral distribution.
        - viral_post_view_registrations: Registrations completed post-viewing in viral distribution.
        - viral_reactions: Total reactions in viral distribution of the ad.
        - viral_registrations: Total registrations in viral distribution of the ad.
        - viral_shares: Total shares in viral distribution of the ad.
        - viral_total_engagements: Total engagements in viral distribution of the ad.
        - viral_video_completions: Completions of videos in viral distribution.
        - viral_video_first_quartile_completions: First quartile completions of videos in viral distribution.
        - viral_video_midpoint_completions: Midpoint completions of videos in viral distribution.
        - viral_video_starts: Total video starts in viral distribution of the ad.
        - viral_video_third_quartile_completions: Third quartile completions of videos in viral distribution.
        - viral_video_views: Total views of videos in viral distribution of the ad.
        - pivot: Pivot dimension used for this analytics record
        - sponsored_campaign: URN of the sponsored campaign this analytics record belongs to
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdMemberRegionAnalyticsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against ad_member_region_analytics records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `list(self, q: str, pivot: str, time_granularity: str, date_range: str, campaigns: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult[list[AdAnalyticsRecord]]`
    :   Returns ad analytics data pivoted by member region. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member region.
        
        
        Args:
            q: LinkedIn API finder method for querying ad analytics
            pivot: Pivot dimension for analytics grouping
            time_granularity: Time granularity for analytics data
            date_range: Date range in LinkedIn format, e.g. (start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31))
            campaigns: List of campaign URNs, e.g. List(urn%3Ali%3AsponsoredCampaign%3A123)
            fields: Comma-separated list of metric fields to return
            **kwargs: Additional parameters
        
        Returns:
            AdMemberRegionAnalyticsListResult

<a id="AdMemberSeniorityAnalyticsQuery"></a>

`AdMemberSeniorityAnalyticsQuery(connector: LinkedinAdsConnector)`
:   Query class for AdMemberSeniorityAnalytics entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdMemberSeniorityAnalyticsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[AdMemberSeniorityAnalyticsSearchData]`
    :   Search ad_member_seniority_analytics records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdMemberSeniorityAnalyticsSearchFilter):
        - action_clicks: The number of clicks on action buttons in the ad.
        - ad_unit_clicks: The number of clicks on ad unit components.
        - approximate_member_reach: An approximation of unique ad impressions.
        - card_clicks: The number of clicks on interactive card elements.
        - card_impressions: The number of times interactive cards were displayed.
        - clicks: Total number of clicks on the ad.
        - comment_likes: The count of likes on comments related to the ad.
        - comments: The number of comments on the ad.
        - company_page_clicks: Clicks on the company page associated with the ad.
        - conversion_value_in_local_currency: Conversion value in the local currency.
        - cost_in_local_currency: Cost of ad campaign in the local currency.
        - cost_in_usd: Cost of ad campaign in USD.
        - document_completions: Number of completions for document views.
        - document_first_quartile_completions: Completions for first quartile of document views.
        - document_midpoint_completions: Completions for midpoint of document views.
        - document_third_quartile_completions: Completions for third quartile of document views.
        - download_clicks: Clicks on download links in the ad.
        - end_date: End date of the ad analytics data.
        - external_website_conversions: Conversions that lead to external websites.
        - external_website_post_click_conversions: Post-click conversions on external websites.
        - external_website_post_view_conversions: Post-view conversions on external websites.
        - follows: Number of follows generated by the ad.
        - full_screen_plays: Number of times videos were played in fullscreen mode.
        - impressions: Total number of times the ad was displayed.
        - job_applications: Number of job applications initiated through the ad.
        - job_apply_clicks: Clicks on apply job button in the ad.
        - landing_page_clicks: Clicks on the landing page associated with the ad.
        - lead_generation_mail_contact_info_shares: Shares of contact information through lead generation.
        - lead_generation_mail_interested_clicks: Clicks on expressing interest through lead generation mail.
        - likes: Total likes received on the ad.
        - one_click_lead_form_opens: Number of times lead forms were opened in one click.
        - one_click_leads: Leads generated in one click.
        - opens: The number of times the ad was opened or expanded.
        - other_engagements: Engagements other than clicks on the ad.
        - pivot_values: Values used for pivoting the analytics.
        - string_of_pivot_values: Comma-separated string of pivot values for this analytics record
        - post_click_job_applications: Job applications initiated post-clicking on the ad.
        - post_click_job_apply_clicks: Clicks on apply job button post-clicking on the ad.
        - post_click_registrations: Registrations completed post-clicking on the ad.
        - post_view_job_applications: Job applications initiated post-viewing the ad.
        - post_view_job_apply_clicks: Clicks on apply job button post-viewing the ad.
        - post_view_registrations: Registrations completed post-viewing the ad.
        - reactions: Total reactions (e.g., like, love, celebrate) on the ad.
        - registrations: Total registrations completed through the ad.
        - sends: Number of messages sent through the ad.
        - shares: Total shares generated by the ad.
        - start_date: Start date of the ad analytics data.
        - talent_leads: Number of leads related to talent acquisition.
        - text_url_clicks: Clicks on text URLs within the ad.
        - total_engagements: Total number of engagements on the ad.
        - valid_work_email_leads: Leads generated through valid work emails.
        - video_completions: Number of times videos were watched till completion.
        - video_first_quartile_completions: Completions for first quartile of video views.
        - video_midpoint_completions: Completions for midpoint of video views.
        - video_starts: Total video starts initiated by users.
        - video_third_quartile_completions: Completions for third quartile of video views.
        - video_views: Total views of videos in the ad.
        - viral_card_clicks: Clicks on interactive card components in viral distribution.
        - viral_card_impressions: Impressions of interactive cards in viral distribution.
        - viral_clicks: Total clicks in viral distribution of the ad.
        - viral_comment_likes: Likes received on comments in viral distribution.
        - viral_comments: Number of comments in viral distribution of the ad.
        - viral_company_page_clicks: Clicks on the company page in viral distribution.
        - viral_document_completions: Complete views of documents in viral distribution.
        - viral_document_first_quartile_completions: First quartile completions of documents in viral distribution.
        - viral_document_midpoint_completions: Midpoint completions of documents in viral distribution.
        - viral_document_third_quartile_completions: Third quartile completions of documents in viral distribution.
        - viral_download_clicks: Clicks on downloads in viral distribution of the ad.
        - viral_external_website_conversions: External website conversions in viral distribution.
        - viral_external_website_post_click_conversions: Post-click conversions on external websites in viral distribution.
        - viral_external_website_post_view_conversions: Post-view conversions on external websites in viral distribution.
        - viral_follows: Follows generated in viral distribution of the ad.
        - viral_full_screen_plays: Fullscreen video plays in viral distribution.
        - viral_impressions: Total impressions in viral distribution of the ad.
        - viral_job_applications: Job applications initiated in viral distribution.
        - viral_job_apply_clicks: Clicks on apply job button in viral distribution of the ad.
        - viral_landing_page_clicks: Clicks on landing page in viral distribution.
        - viral_likes: Total likes in viral distribution of the ad.
        - viral_one_click_lead_form_opens: One-click lead form opens in viral distribution.
        - viral_one_click_leads: Leads generated in one click in viral distribution.
        - viral_other_engagements: Other engagements in viral distribution of the ad.
        - viral_post_click_job_applications: Job applications initiated post-clicking in viral distribution.
        - viral_post_click_job_apply_clicks: Clicks on apply job button post-clicking in viral distribution.
        - viral_post_click_registrations: Registrations completed post-clicking in viral distribution.
        - viral_post_view_job_applications: Job applications initiated post-viewing in viral distribution.
        - viral_post_view_job_apply_clicks: Clicks on apply job button post-viewing in viral distribution.
        - viral_post_view_registrations: Registrations completed post-viewing in viral distribution.
        - viral_reactions: Total reactions in viral distribution of the ad.
        - viral_registrations: Total registrations in viral distribution of the ad.
        - viral_shares: Total shares in viral distribution of the ad.
        - viral_total_engagements: Total engagements in viral distribution of the ad.
        - viral_video_completions: Completions of videos in viral distribution.
        - viral_video_first_quartile_completions: First quartile completions of videos in viral distribution.
        - viral_video_midpoint_completions: Midpoint completions of videos in viral distribution.
        - viral_video_starts: Total video starts in viral distribution of the ad.
        - viral_video_third_quartile_completions: Third quartile completions of videos in viral distribution.
        - viral_video_views: Total views of videos in viral distribution of the ad.
        - pivot: Pivot dimension used for this analytics record
        - sponsored_campaign: URN of the sponsored campaign this analytics record belongs to
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdMemberSeniorityAnalyticsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against ad_member_seniority_analytics records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `list(self, q: str, pivot: str, time_granularity: str, date_range: str, campaigns: str, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResult[list[AdAnalyticsRecord]]`
    :   Returns ad analytics data pivoted by member seniority. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member seniority.
        
        
        Args:
            q: LinkedIn API finder method for querying ad analytics
            pivot: Pivot dimension for analytics grouping
            time_granularity: Time granularity for analytics data
            date_range: Date range in LinkedIn format, e.g. (start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31))
            campaigns: List of campaign URNs, e.g. List(urn%3Ali%3AsponsoredCampaign%3A123)
            fields: Comma-separated list of metric fields to return
            **kwargs: Additional parameters
        
        Returns:
            AdMemberSeniorityAnalyticsListResult

<a id="CampaignConversionsQuery"></a>

`CampaignConversionsQuery(connector: LinkedinAdsConnector)`
:   Query class for CampaignConversions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, campaign_urn: str, conversion_urn: str, campaign: str | None = None, conversion: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.RestliCreateResponse`
    :   Creates a campaign-to-conversion association using the Rest.li compound-key PUT pattern. Pass the raw campaign URN (urn:li:sponsoredCampaign:\{id\}) and conversion URN (urn:lla:llaPartnerConversion:\{id\}); they are URL-encoded automatically. Conversions API access is gated behind a separate LinkedIn partner approval.
        
        
        Args:
            campaign: Campaign URN, e.g. urn:li:sponsoredCampaign:123456
            conversion: Conversion rule URN, e.g. urn:lla:llaPartnerConversion:123456
            campaign_urn: Campaign URN, e.g. urn:li:sponsoredCampaign:123456
            conversion_urn: Conversion rule URN, e.g. urn:lla:llaPartnerConversion:123456
            **kwargs: Additional parameters
        
        Returns:
            RestliCreateResponse

    `delete(self, campaign_urn: str, conversion_urn: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Deletes a campaign-to-conversion association by its compound key. Pass the raw campaign and conversion URNs; they are URL-encoded automatically. Conversions API access is gated behind a separate LinkedIn partner approval.
        
        
        Args:
            campaign_urn: Campaign URN, e.g. urn:li:sponsoredCampaign:123456
            conversion_urn: Conversion rule URN, e.g. urn:lla:llaPartnerConversion:123456
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
        - run_schedule: Schedule for running the campaign group.
        - created: The date and time when the campaign group was created.
        - last_modified: The date and time when the campaign group was last modified.
        - name: Name of the campaign group.
        - test: Indicates if the campaign group is a test campaign.
        - total_budget: Total budget allocated for the campaign group.
        - serving_statuses: List of serving statuses for the campaign group.
        - backfilled: Indicates if the campaign group was backfilled.
        - id: Unique identifier for the campaign group.
        - account: The account associated with the campaign group.
        - status: Current status of the campaign group.
        - allowed_campaign_types: List of campaign types allowed for this campaign group.
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CampaignGroupsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against campaign_groups records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `create(self, account: str, name: str, run_schedule: CampaignGroupsCreateParamsRunschedule, account_id: str, status: str | None = None, total_budget: CampaignGroupsCreateParamsTotalbudget | None = None, objective_type: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, CampaignGroupsCreateResultMeta]`
    :   Creates a new campaign group in the ad account. Requires the rw_ads OAuth scope and a CAMPAIGN_MANAGER or higher ad-account role. The new campaign group ID is returned in the x-restli-id response header. runSchedule.start is required when creating with ACTIVE status.
        
        
        Args:
            account: Sponsored account URN; must match the account_id path parameter, e.g. urn:li:sponsoredAccount:123456
            name: Campaign group name
            status: Initial status
            run_schedule: Scheduled run window (epoch milliseconds)
            total_budget: Total budget across the group's lifetime
            objective_type: Objective shared by campaigns in this group
            account_id: Ad account ID
            **kwargs: Additional parameters
        
        Returns:
            CampaignGroupsCreateResult

    `delete(self, account_id: str, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Hard-deletes a campaign group. Only campaign groups in DRAFT status accept a true DELETE; for non-DRAFT campaign groups LinkedIn requires a soft delete instead - use the update operation to set status to PENDING_DELETION. Requires the rw_ads OAuth scope and a CAMPAIGN_MANAGER or higher ad-account role.
        
        
        Args:
            account_id: Ad account ID
            id: Campaign group ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
            q: LinkedIn API finder method for querying campaign groups
            page_size: Number of items per page
            page_token: Token for the next page of results
            **kwargs: Additional parameters
        
        Returns:
            CampaignGroupsListResult

    `update(self, patch: CampaignGroupsUpdateParamsPatch, account_id: str, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Partially updates a campaign group using the Rest.li PARTIAL_UPDATE pattern: the body wraps the fields to change in patch.$set. Requires the rw_ads OAuth scope and a CAMPAIGN_MANAGER or higher ad-account role. $set on an array field replaces the whole array, so re-send all existing elements. To soft-delete a non-DRAFT campaign group, set status to PENDING_DELETION here.
        
        
        Args:
            patch: Parameter patch
            account_id: Ad account ID
            id: Campaign group ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
        - targeting_criteria: Criteria for targeting in the campaign.
        - serving_statuses: The serving statuses of the campaign.
        - type_: The type of campaign.
        - locale: The locale settings for the campaign.
        - version: The version information for the campaign.
        - associated_entity: The entity associated with the campaign.
        - run_schedule: The schedule for running the campaign.
        - optimization_target_type: The type of optimization target for the campaign.
        - created: The date and time when the campaign was created.
        - last_modified: The date and time when the campaign was last modified.
        - campaign_group: The group to which the campaign belongs.
        - daily_budget: The daily budget set for the campaign.
        - total_budget: The total budget amount for the campaign.
        - unit_cost: The unit cost for the campaign.
        - creative_selection: Information about the creative selection for the campaign.
        - cost_type: The type of cost associated with the campaign.
        - name: The name of the campaign.
        - offsite_delivery_enabled: Indicates if offsite delivery is enabled for the campaign.
        - id: The unique identifier of the campaign.
        - audience_expansion_enabled: Indicates if audience expansion is enabled for this campaign.
        - test: Indicates if the campaign is a test campaign.
        - account: The account associated with the campaign data.
        - status: The status of the campaign.
        - story_delivery_enabled: Indicates if story delivery is enabled for the campaign.
        - pacing_strategy: The pacing strategy for the campaign.
        - format: The format of the campaign.
        - objective_type: The type of objective for the campaign.
        - offsite_preferences: Preferences related to offsite delivery.
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CampaignsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against campaigns records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `create(self, account: str, name: str, political_intent: str, run_schedule: CampaignsCreateParamsRunschedule, offsite_delivery_enabled: bool, account_id: str, campaign_group: str | None = None, type: str | None = None, objective_type: str | None = None, status: str | None = None, cost_type: str | None = None, daily_budget: CampaignsCreateParamsDailybudget | None = None, unit_cost: CampaignsCreateParamsUnitcost | None = None, locale: CampaignsCreateParamsLocale | None = None, targeting_criteria: dict[str, Any] | None = None, audience_expansion_enabled: bool | None = None, creative_selection: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, CampaignsCreateResultMeta]`
    :   Creates a new campaign in the ad account. Requires the rw_ads OAuth scope and an ad-account role of CAMPAIGN_MANAGER or higher (VIEWER is read-only). The new campaign ID is returned in the x-restli-id response header. Commonly required fields beyond account and name include type, costType, unitCost or dailyBudget, locale, and targetingCriteria; LinkedIn returns a descriptive 400 when a required field is missing.
        
        
        Args:
            account: Sponsored account URN; must match the account_id path parameter, e.g. urn:li:sponsoredAccount:123456
            name: Campaign name
            political_intent: Whether the campaign contains political content; LinkedIn requires this on create
            campaign_group: Campaign group URN, e.g. urn:li:sponsoredCampaignGroup:123456
            type: Campaign format
            objective_type: Campaign objective, e.g. BRAND_AWARENESS, WEBSITE_VISIT, LEAD_GENERATION, WEBSITE_CONVERSION, VIDEO_VIEW, ENGAGEMENT, JOB_APPLICANT
            status: Initial campaign status
            cost_type: Bidding cost type, e.g. CPM, CPC, CPV
            daily_budget: Daily budget
            unit_cost: Bid amount per unit (per click, per impression, etc.)
            locale: Campaign locale
            run_schedule: Scheduled run window (epoch milliseconds)
            targeting_criteria: Audience targeting criteria (include/exclude clauses)
            audience_expansion_enabled: Whether audience expansion is enabled
            offsite_delivery_enabled: Whether ads may be served on the LinkedIn Audience Network
            creative_selection: Creative rotation strategy, e.g. ROUND_ROBIN, OPTIMIZED
            account_id: Ad account ID
            **kwargs: Additional parameters
        
        Returns:
            CampaignsCreateResult

    `delete(self, account_id: str, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Hard-deletes a campaign. Only campaigns in DRAFT status accept a true DELETE; for non-DRAFT campaigns LinkedIn requires a soft delete instead - use the update operation to set status to PENDING_DELETION. Requires the rw_ads OAuth scope and a CAMPAIGN_MANAGER or higher ad-account role.
        
        
        Args:
            account_id: Ad account ID
            id: Campaign ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `get(self, account_id: str, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.Campaign`
    :   Get a single campaign by ID
        
        Args:
            account_id: Ad account ID
            id: Campaign ID
            **kwargs: Additional parameters
        
        Returns:
            Campaign

    `list(self, account_id: str, q: str, page_size: int | None = None, page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[dict[str, Any]], CampaignsListResultMeta]`
    :   Returns a list of campaigns for an ad account
        
        Args:
            account_id: Ad account ID
            q: LinkedIn API finder method for querying campaigns
            page_size: Number of items per page
            page_token: Token for the next page of results
            **kwargs: Additional parameters
        
        Returns:
            CampaignsListResult

    `update(self, patch: CampaignsUpdateParamsPatch, account_id: str, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Partially updates a campaign using the Rest.li PARTIAL_UPDATE pattern: the body wraps the fields to change in patch.$set. Requires the rw_ads OAuth scope and a CAMPAIGN_MANAGER or higher ad-account role. Note that $set on an array field (e.g. targetingCriteria lists) replaces the whole array, so re-send all existing elements. To soft-delete a non-DRAFT campaign, set status to PENDING_DELETION here.
        
        
        Args:
            patch: Parameter patch
            account_id: Ad account ID
            id: Campaign ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

<a id="ConversionEventsQuery"></a>

`ConversionEventsQuery(connector: LinkedinAdsConnector)`
:   Query class for ConversionEvents entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, elements: list[ConversionEventsCreateParamsElementsItem], **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.RestliCreateResponse`
    :   Streams offline conversion events to LinkedIn (Conversions API event ingestion). This is a write-only Rest.li BATCH_CREATE: the body's elements array accepts up to 5,000 events per request. Each event references a conversion rule URN (urn:lla:llaPartnerConversion:\{id\}) and identifies the converting user by hashed email or other supported ID types. Conversions API access is gated behind a separate LinkedIn partner approval.
        
        
        Args:
            elements: Conversion events to ingest
            **kwargs: Additional parameters
        
        Returns:
            RestliCreateResponse

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
        - attribution_type: The type of attribution for the conversion.
        - account: The account associated with the conversion data.
        - campaigns: List of campaigns related to the conversion.
        - created: Timestamp of when the conversion was created.
        - enabled: Flag indicating if the conversion tracking is enabled.
        - id: Unique identifier for the conversion.
        - image_pixel_tag: Pixel tag used for tracking the conversion.
        - name: Name of the conversion.
        - type_: Type of conversion.
        - latest_first_party_callback_at: Timestamp of the latest first-party callback for the conversion.
        - post_click_attribution_window_size: Window size for post-click attribution.
        - view_through_attribution_window_size: Window size for view-through attribution.
        - last_callback_at: Timestamp of the last callback for the conversion.
        - last_modified: Timestamp of the last modification made to the conversion.
        - value: Value associated with the conversion.
        - associated_campaigns: Campaigns associated with the conversion.
        - url_match_rule_expression: Expression used for matching URLs for attribution.
        - url_rules: Rules for URL matching in the conversion.
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ConversionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against conversions records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `create(self, account: str, name: str, type: str, attribution_type: str | None = None, post_click_attribution_window_size: int | None = None, view_through_attribution_window_size: int | None = None, enabled: bool | None = None, url_match_rule_expression: list[list[dict[str, Any]]] | None = None, value: ConversionsCreateParamsValue | None = None, auto_association_type: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, ConversionsCreateResultMeta]`
    :   Creates a new conversion tracking rule. Conversions API write access is gated behind a separate LinkedIn partner approval - the rw_conversions OAuth scope alone is not sufficient until access is granted. The new conversion ID is returned in the x-restli-id response header. Set autoAssociationType to ALL_CAMPAIGNS to associate the rule with every campaign in the account automatically.
        
        
        Args:
            account: Sponsored account URN, e.g. urn:li:sponsoredAccount:123456
            name: Conversion rule name
            type: Conversion category, e.g. LEAD, PURCHASE, SIGN_UP, DOWNLOAD, ADD_TO_CART, INSTALL, KEY_PAGE_VIEW, OTHER
            attribution_type: How conversions are attributed to campaigns
            post_click_attribution_window_size: Post-click attribution window in days (1, 7, 30, or 90)
            view_through_attribution_window_size: View-through attribution window in days (1, 7, or 30)
            enabled: Whether the rule is active
            url_match_rule_expression: URL match rules for page-based conversion tracking
            value: Monetary value assigned to each conversion
            auto_association_type: Set to ALL_CAMPAIGNS to auto-associate with all campaigns in the account
            **kwargs: Additional parameters
        
        Returns:
            ConversionsCreateResult

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
            q: LinkedIn API finder method for querying conversions by account
            account: Account URN, e.g. urn:li:sponsoredAccount:123456
            count: Number of items per page
            start: Offset for pagination
            **kwargs: Additional parameters
        
        Returns:
            ConversionsListResult

    `update(self, patch: ConversionsUpdateParamsPatch, account: str, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Partially updates a conversion rule using the Rest.li PARTIAL_UPDATE pattern: the body wraps the fields to change in patch.$set. The account query parameter is required. Conversion rules have no hard delete - to retire one, soft-disable it here with \{"patch": \{"$set": \{"enabled": false\}\}\}. Conversions API write access is gated behind a separate LinkedIn partner approval.
        
        
        Args:
            patch: Parameter patch
            id: Conversion rule ID
            account: Sponsored account URN, e.g. urn:li:sponsoredAccount:123456
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
        - serving_hold_reasons: Reasons for holding the creative from serving.
        - last_modified_at: The timestamp when the creative was last modified.
        - last_modified_by: The user who last modified the creative.
        - content: The actual content of the creative.
        - created_at: The timestamp when the creative was created.
        - is_test: Boolean indicating if the creative is a test creative.
        - created_by: The user who created the creative.
        - review: Review information for the creative.
        - name: The name of the creative.
        - is_serving: Boolean indicating if the creative is currently serving.
        - campaign: The campaign to which the creative belongs.
        - id: The unique identifier of the creative.
        - intended_status: The intended status of the creative.
        - account: The account associated with the creative.
        - leadgen_call_to_action: Call-to-action information for lead generation purposes.
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CreativesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against creatives records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `create(self, campaign: str, account_id: str, content: dict[str, Any] | None = None, intended_status: str | None = None, name: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[RestliCreateResponse, CreativesCreateResultMeta]`
    :   Creates a new creative in the ad account. Requires the rw_ads OAuth scope and a CREATIVE_MANAGER or higher ad-account role. The new creative URN is returned in the x-restli-id response header. The creative's content must reference existing assets (e.g. a post URN in content.reference for sponsored content).
        
        
        Args:
            campaign: Campaign URN the creative belongs to, e.g. urn:li:sponsoredCampaign:123456
            content: Creative content. For sponsored content, reference an existing post URN via content.reference; other formats (textAd, spotlight, jobs) use their own sub-objects per the LinkedIn Creatives API documentation.
        
            intended_status: Desired serving status
            name: Creative name
            account_id: Ad account ID
            **kwargs: Additional parameters
        
        Returns:
            CreativesCreateResult

    `delete(self, account_id: str, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Hard-deletes a creative. Only creatives in DRAFT intendedStatus (or linked to a draft campaign, or with failed video uploads) accept a true DELETE; LinkedIn uniquely requires the X-RestLi-Method DELETE header on this call. For other creatives, soft-delete via the update operation by setting intendedStatus to PENDING_DELETION. Requires the rw_ads OAuth scope and a CREATIVE_MANAGER or higher ad-account role.
        
        
        Args:
            account_id: Ad account ID
            id: Creative URN, e.g. urn:li:sponsoredCreative:123456
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `get(self, account_id: str, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.Creative`
    :   Get a single creative by ID
        
        Args:
            account_id: Ad account ID
            id: Creative ID
            **kwargs: Additional parameters
        
        Returns:
            Creative

    `list(self, account_id: str, q: str, page_size: int | None = None, page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[dict[str, Any]], CreativesListResultMeta]`
    :   Returns a list of creatives for an ad account
        
        Args:
            account_id: Ad account ID
            q: LinkedIn API finder method for querying creatives
            page_size: Number of items per page
            page_token: Token for the next page of results
            **kwargs: Additional parameters
        
        Returns:
            CreativesListResult

    `update(self, patch: CreativesUpdateParamsPatch, account_id: str, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Partially updates a creative using the Rest.li PARTIAL_UPDATE pattern: the body wraps the fields to change in patch.$set. Only a limited set of creative fields is mutable (e.g. intendedStatus, name, leadgenCallToAction). Requires the rw_ads OAuth scope and a CREATIVE_MANAGER or higher ad-account role. To soft-delete a non-draft creative, set intendedStatus to PENDING_DELETION here.
        
        
        Args:
            patch: Parameter patch
            account_id: Ad account ID
            id: Creative URN, e.g. urn:li:sponsoredCreative:123456
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

<a id="LeadFormResponsesQuery"></a>

`LeadFormResponsesQuery(connector: LinkedinAdsConnector)`
:   Query class for LeadFormResponses entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: LeadFormResponsesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[LeadFormResponsesSearchData]`
    :   Search lead_form_responses records from Airbyte cache.
        
                This operation searches cached data from Airbyte syncs.
                Only available in hosted execution mode.
        
                Available filter fields (LeadFormResponsesSearchFilter):
                - id: Unique id to identify the Lead Form Response.
                - lead_type: Type of the lead representing the origination of the lead.
                - form: URN identifying which form this FormResponse belongs to.
                - owner: Owner of this Lead Form Response.
        It is a Union of sponsoredAccount and organization.
        sponsoredAccount is an URN of SponsoredAccountUrn that indicates the ad account of the advertiser.
        organization is an URN of OrganizationUrn that indicates the company page of the advertiser.
        
                - owner_info: Record containing entity info that owns this Lead Form Response. It's a optional Union of sponsoredAccountInfo and organizationInfo.
                - lead_metadata: Metadata of a lead. This field is optional for test leads and other use cases where sponsored lead metadata (e.g. campaign) may not be relevant. If there is no value, the field is not returned.
                - lead_metadata_info: Record containing a subset of fields resolved on demand from the lead metadata references (e.g. campaign name , campaign type). If there is no value, an empty object is returned.
                - associated_entity: URN identifying which entity the lead is associated with. This field is optional for test leads and other use cases where leads don't have any associatedEntity. If there is no value, the field is not returned.
                - associated_entity_info: Record containing useful fields (creative status, ugc reference etc.) resolved on demand from the associated entity object. If there is no value, an empty object is returned.
                - submitted_at: An epoch timestamp that recording when the form response was submitted.
                - response_id: The unique identifier for the form response generated in the front-end when a submitter submits the response.
                - form_response: Answers provided by the form submitter.
                - test_lead: Whether this is a test lead created for testing purposes.
                - submitter: From version 202408 onwards, Guest Leads (when a user submits a form without being logged in) submitted to lead forms, submitter field is treated as a null field and omitted from the JSON response.
        For non-guest leads, the submitter field will still be included in the response and will provide the person's URN. Ex: "submitter": "urn:li:person:MpGcnvaU_p". Yes
        
                - versioned_lead_gen_form_urn: URN identifying which form this FormResponse belongs to.
        
                Args:
                    query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                           in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                           Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
                    limit: Maximum results to return (default 1000)
                    cursor: Pagination cursor from previous response's meta.cursor
                    fields: Field paths to include in results. Each path is a list of keys for nested access.
                            Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
                Returns:
                    LeadFormResponsesSearchResult with typed records, pagination metadata, and optional search metadata
        
                Raises:
                    NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against lead_form_responses records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `list(self, q: str, owner: str, lead_type: str, count: int | None = None, start: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[LeadFormResponse], LeadFormResponsesListResultMeta]`
    :   Returns a list of lead form responses submitted to forms owned by a sponsored ad account
        
        Args:
            q: LinkedIn API finder method for querying lead form responses by owner
            owner: Owner of the lead form responses, e.g. (sponsoredAccount:urn%3Ali%3AsponsoredAccount%3A123456)
            lead_type: Type of leads to return, e.g. (leadType:SPONSORED)
            count: Number of items per page
            start: Offset for pagination
            **kwargs: Additional parameters
        
        Returns:
            LeadFormResponsesListResult

<a id="LeadFormsQuery"></a>

`LeadFormsQuery(connector: LinkedinAdsConnector)`
:   Query class for LeadForms entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: LeadFormsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[LeadFormsSearchData]`
    :   Search lead_forms records from Airbyte cache.
        
                This operation searches cached data from Airbyte syncs.
                Only available in hosted execution mode.
        
                Available filter fields (LeadFormsSearchFilter):
                - id: Numerical identifier for the form.
                - name: Name of the Lead Form provided by the owner.
                - owner: URN that identifies the owner of the Lead Form.
        It's a Union of sponsoredAccount and organization.
        sponsoredAccount is an URN of SponsoredAccountUrn that indicates the account of the advertiser.
        organization is an URN of OrganizationUrn that indicates the company account of the marketer.
        
                - state: Information about the current state of the Lead Form.
                - content: Content of the Lead Form which will be displayed to the viewer.
                - created: An epoch time corresponding to the creation of the form.
                - last_modified: An epoch time corresponding to the last modified of of the form.
                - creation_locale: Locale of the entity.
        This field serves as the preferred locale for all fields within the Lead Form with an object type that is capable of localization, such as MultiLocaleString.
        
                - hidden_fields: Hidden fields used by the owner to track key attributes of the form that generated the lead.
        The field is empty if the owner chooses to not append any tracking attributes to the Lead Form.
        
                - review_info: Latest information about the content review of the Lead Form.
        It will not be present if the form has not been reviewed by the review pipeline.
        
                - version_id: The version ID of the form. This is a derived field and is generated on the server side.
                - version_tag: The number of times the form has been modified.
        
                Args:
                    query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                           in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                           Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
                    limit: Maximum results to return (default 1000)
                    cursor: Pagination cursor from previous response's meta.cursor
                    fields: Field paths to include in results. Each path is a list of keys for nested access.
                            Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
                Returns:
                    LeadFormsSearchResult with typed records, pagination metadata, and optional search metadata
        
                Raises:
                    NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against lead_forms records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `list(self, q: str, owner: str, count: int | None = None, start: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linkedin_ads.models.LinkedinAdsExecuteResultWithMeta[list[LeadForm], LeadFormsListResultMeta]`
    :   Returns a list of lead generation forms owned by a sponsored ad account
        
        Args:
            q: LinkedIn API finder method for querying lead forms by owner
            owner: Owner of the lead forms, e.g. (sponsoredAccount:urn%3Ali%3AsponsoredAccount%3A123456)
            count: Number of items per page
            start: Offset for pagination
            **kwargs: Additional parameters
        
        Returns:
            LeadFormsListResult

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