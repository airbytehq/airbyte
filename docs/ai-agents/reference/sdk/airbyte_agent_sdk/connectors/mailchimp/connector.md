---
id: airbyte_agent_sdk-connectors-mailchimp-connector
title: airbyte_agent_sdk.connectors.mailchimp.connector
---

Module airbyte_agent_sdk.connectors.mailchimp.connector
=======================================================
Mailchimp connector.

Classes
-------

<a id="AutomationsQuery"></a>

`AutomationsQuery(connector: MailchimpConnector)`
:   Query class for Automations entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, count: int | None = None, offset: int | None = None, before_create_time: str | None = None, since_create_time: str | None = None, before_start_time: str | None = None, since_start_time: str | None = None, status: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[Automation], AutomationsListResultMeta]`
    :   Get a summary of an account's classic automations
        
        Args:
            count: The number of records to return
            offset: Used for pagination
            before_create_time: Restrict the response to automations created before this time
            since_create_time: Restrict the response to automations created after this time
            before_start_time: Restrict the response to automations started before this time
            since_start_time: Restrict the response to automations started after this time
            status: Restrict the results to automations with the specified status
            **kwargs: Additional parameters
        
        Returns:
            AutomationsListResult

<a id="CampaignsQuery"></a>

`CampaignsQuery(connector: MailchimpConnector)`
:   Query class for Campaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[CampaignsSearchData]`
    :   Search campaigns records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignsSearchFilter):
        - ab_split_opts: [A/B Testing](https://mailchimp.com/help/about-ab-testing-campaigns/) options for a campaign.
        - archive_url: The link to the campaign's archive version in ISO 8601 format.
        - content_type: How the campaign's content is put together.
        - create_time: The date and time the campaign was created in ISO 8601 format.
        - delivery_status: Updates on campaigns in the process of sending.
        - emails_sent: The total number of emails sent for this campaign.
        - id: A string that uniquely identifies this campaign.
        - long_archive_url: The original link to the campaign's archive version.
        - needs_block_refresh: Determines if the campaign needs its blocks refreshed by opening the web-based campaign editor. D...
        - parent_campaign_id: If this campaign is the child of another campaign, this identifies the parent campaign. For Examp...
        - recipients: List settings for the campaign.
        - report_summary: For sent campaigns, a summary of opens, clicks, and e-commerce data.
        - resendable: Determines if the campaign qualifies to be resent to non-openers.
        - rss_opts: [RSS](https://mailchimp.com/help/share-your-blog-posts-with-mailchimp/) options for a campaign.
        - send_time: The date and time a campaign was sent.
        - settings: The settings for your campaign, including subject, from name, reply-to address, and more.
        - social_card: The preview for the campaign, rendered by social networks like Facebook and Twitter. [Learn more]...
        - status: The current status of the campaign.
        - tracking: The tracking options for a campaign.
        - type_: There are four types of [campaigns](https://mailchimp.com/help/getting-started-with-campaigns/) y...
        - variate_settings: The settings specific to A/B test campaigns.
        - web_id: The ID used in the Mailchimp web application. View this campaign in your Mailchimp account at `ht...
        
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

    `get(self, campaign_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.Campaign`
    :   Get information about a specific campaign
        
        Args:
            campaign_id: The unique id for the campaign
            **kwargs: Additional parameters
        
        Returns:
            Campaign

    `list(self, count: int | None = None, offset: int | None = None, type: str | None = None, status: str | None = None, before_send_time: str | None = None, since_send_time: str | None = None, before_create_time: str | None = None, since_create_time: str | None = None, list_id: str | None = None, folder_id: str | None = None, sort_field: str | None = None, sort_dir: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]`
    :   Get all campaigns in an account
        
        Args:
            count: The number of records to return. Default is 10. Maximum is 1000.
            offset: Used for pagination, this is the number of records from a collection to skip.
            type: The campaign type
            status: The status of the campaign
            before_send_time: Restrict the response to campaigns sent before the set time
            since_send_time: Restrict the response to campaigns sent after the set time
            before_create_time: Restrict the response to campaigns created before the set time
            since_create_time: Restrict the response to campaigns created after the set time
            list_id: The unique id for the list
            folder_id: The unique folder id
            sort_field: Returns files sorted by the specified field
            sort_dir: Determines the order direction for sorted results
            **kwargs: Additional parameters
        
        Returns:
            CampaignsListResult

<a id="EmailActivityQuery"></a>

`EmailActivityQuery(connector: MailchimpConnector)`
:   Query class for EmailActivity entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: EmailActivitySearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[EmailActivitySearchData]`
    :   Search email_activity records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (EmailActivitySearchFilter):
        - action: One of the following actions: 'open', 'click', or 'bounce'
        - campaign_id: The unique id for the campaign.
        - email_address: Email address for a subscriber.
        - email_id: The MD5 hash of the lowercase version of the list member's email address.
        - ip: The IP address recorded for the action.
        - list_id: The unique id for the list.
        - list_is_active: The status of the list used, namely if it's deleted or disabled.
        - timestamp: The date and time recorded for the action in ISO 8601 format.
        - type_: If the action is a 'bounce', the type of bounce received: 'hard', 'soft'.
        - url: If the action is a 'click', the URL on which the member clicked.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            EmailActivitySearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, campaign_id: str, count: int | None = None, offset: int | None = None, since: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[EmailActivity], EmailActivityListResultMeta]`
    :   Get a list of member's subscriber activity in a specific campaign
        
        Args:
            campaign_id: The unique id for the campaign
            count: The number of records to return
            offset: Used for pagination
            since: Restrict results to email activity events that occur after a specific time
            **kwargs: Additional parameters
        
        Returns:
            EmailActivityListResult

<a id="InterestCategoriesQuery"></a>

`InterestCategoriesQuery(connector: MailchimpConnector)`
:   Query class for InterestCategories entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, list_id: str, interest_category_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.InterestCategory`
    :   Get information about a specific interest category
        
        Args:
            list_id: The unique ID for the list
            interest_category_id: The unique ID for the interest category
            **kwargs: Additional parameters
        
        Returns:
            InterestCategory

    `list(self, list_id: str, count: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[InterestCategory], InterestCategoriesListResultMeta]`
    :   Get information about a list's interest categories
        
        Args:
            list_id: The unique ID for the list
            count: The number of records to return
            offset: Used for pagination
            **kwargs: Additional parameters
        
        Returns:
            InterestCategoriesListResult

<a id="InterestsQuery"></a>

`InterestsQuery(connector: MailchimpConnector)`
:   Query class for Interests entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, list_id: str, interest_category_id: str, interest_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.Interest`
    :   Get interests or group names for a specific category
        
        Args:
            list_id: The unique ID for the list
            interest_category_id: The unique ID for the interest category
            interest_id: The specific interest or group name
            **kwargs: Additional parameters
        
        Returns:
            Interest

    `list(self, list_id: str, interest_category_id: str, count: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[Interest], InterestsListResultMeta]`
    :   Get a list of this category's interests
        
        Args:
            list_id: The unique ID for the list
            interest_category_id: The unique ID for the interest category
            count: The number of records to return
            offset: Used for pagination
            **kwargs: Additional parameters
        
        Returns:
            InterestsListResult

<a id="ListMembersQuery"></a>

`ListMembersQuery(connector: MailchimpConnector)`
:   Query class for ListMembers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, list_id: str, subscriber_hash: str, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.ListMember`
    :   Get information about a specific list member
        
        Args:
            list_id: The unique ID for the list
            subscriber_hash: The MD5 hash of the lowercase version of the list member's email address
            **kwargs: Additional parameters
        
        Returns:
            ListMember

    `list(self, list_id: str, count: int | None = None, offset: int | None = None, email_type: str | None = None, status: str | None = None, since_timestamp_opt: str | None = None, before_timestamp_opt: str | None = None, since_last_changed: str | None = None, before_last_changed: str | None = None, unique_email_id: str | None = None, vip_only: bool | None = None, interest_category_id: str | None = None, interest_ids: str | None = None, interest_match: str | None = None, sort_field: str | None = None, sort_dir: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[ListMember], ListMembersListResultMeta]`
    :   Get information about members in a specific Mailchimp list
        
        Args:
            list_id: The unique ID for the list
            count: The number of records to return
            offset: Used for pagination
            email_type: The email type
            status: The subscriber's status
            since_timestamp_opt: Restrict results to subscribers who opted-in after the set timeframe
            before_timestamp_opt: Restrict results to subscribers who opted-in before the set timeframe
            since_last_changed: Restrict results to subscribers whose information changed after the set timeframe
            before_last_changed: Restrict results to subscribers whose information changed before the set timeframe
            unique_email_id: A unique identifier for the email address across all Mailchimp lists
            vip_only: A filter to return only the list's VIP members
            interest_category_id: The unique id for the interest category
            interest_ids: Used to filter list members by interests
            interest_match: Used to filter list members by interests
            sort_field: Returns files sorted by the specified field
            sort_dir: Determines the order direction for sorted results
            **kwargs: Additional parameters
        
        Returns:
            ListMembersListResult

<a id="ListsQuery"></a>

`ListsQuery(connector: MailchimpConnector)`
:   Query class for Lists entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ListsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[ListsSearchData]`
    :   Search lists records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ListsSearchFilter):
        - beamer_address: The list's Email Beamer address.
        - campaign_defaults: Default values for campaigns created for this list.
        - contact: Contact information displayed in campaign footers to comply with international spam laws.
        - date_created: The date and time that this list was created in ISO 8601 format.
        - double_optin: Whether or not to require the subscriber to confirm subscription via email.
        - email_type_option: Whether the list supports multiple formats for emails. When set to `true`, subscribers can choose...
        - has_welcome: Whether or not this list has a welcome automation connected.
        - id: A string that uniquely identifies this list.
        - list_rating: An auto-generated activity score for the list (0-5).
        - marketing_permissions: Whether or not the list has marketing permissions (eg. GDPR) enabled.
        - modules: Any list-specific modules installed for this list.
        - name: The name of the list.
        - notify_on_subscribe: The email address to send subscribe notifications to.
        - notify_on_unsubscribe: The email address to send unsubscribe notifications to.
        - permission_reminder: The permission reminder for the list.
        - stats: Stats for the list. Many of these are cached for at least five minutes.
        - subscribe_url_long: The full version of this list's subscribe form (host will vary).
        - subscribe_url_short: Our EepURL shortened version of this list's subscribe form.
        - use_archive_bar: Whether campaigns for this list use the Archive Bar in archives by default.
        - visibility: Whether this list is public or private.
        - web_id: The ID used in the Mailchimp web application. View this list in your Mailchimp account at `https:...
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ListsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, list_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.List`
    :   Get information about a specific list in your Mailchimp account
        
        Args:
            list_id: The unique ID for the list
            **kwargs: Additional parameters
        
        Returns:
            List

    `list(self, count: int | None = None, offset: int | None = None, before_date_created: str | None = None, since_date_created: str | None = None, before_campaign_last_sent: str | None = None, since_campaign_last_sent: str | None = None, email: str | None = None, sort_field: str | None = None, sort_dir: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[List], ListsListResultMeta]`
    :   Get information about all lists in the account
        
        Args:
            count: The number of records to return
            offset: Used for pagination
            before_date_created: Restrict response to lists created before the set date
            since_date_created: Restrict response to lists created after the set date
            before_campaign_last_sent: Restrict results to lists created before the last campaign send date
            since_campaign_last_sent: Restrict results to lists created after the last campaign send date
            email: Restrict results to lists that include a specific subscriber's email address
            sort_field: Returns files sorted by the specified field
            sort_dir: Determines the order direction for sorted results
            **kwargs: Additional parameters
        
        Returns:
            ListsListResult

<a id="MailchimpConnector"></a>

`MailchimpConnector(auth_config: MailchimpAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, data_center: str | None = None)`
:   Type-safe Mailchimp API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new mailchimp connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., MailchimpAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            data_center: The data center for your Mailchimp account (e.g., us1, us2, us6)
    Examples:
        # Local mode (direct API calls)
        connector = MailchimpConnector(auth_config=MailchimpAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = MailchimpConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = MailchimpConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'MailchimpAuthConfig'", name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> airbyte_agent_sdk.connectors.mailchimp.connector.MailchimpConnector`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config (same as local mode)
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Optional replication settings dict.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A MailchimpConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await MailchimpConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=MailchimpAuthConfig(api_key="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @MailchimpConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @MailchimpConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await MailchimpConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.mailchimp.models.MailchimpCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            MailchimpCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="ReportsQuery"></a>

`ReportsQuery(connector: MailchimpConnector)`
:   Query class for Reports entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ReportsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[ReportsSearchData]`
    :   Search reports records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ReportsSearchFilter):
        - ab_split: General stats about different groups of an A/B Split campaign. Does not return information about ...
        - abuse_reports: The number of abuse reports generated for this campaign.
        - bounces: An object describing the bounce summary for the campaign.
        - campaign_title: The title of the campaign.
        - clicks: An object describing the click activity for the campaign.
        - delivery_status: Updates on campaigns in the process of sending.
        - ecommerce: E-Commerce stats for a campaign.
        - emails_sent: The total number of emails sent for this campaign.
        - facebook_likes: An object describing campaign engagement on Facebook.
        - forwards: An object describing the forwards and forward activity for the campaign.
        - id: A string that uniquely identifies this campaign.
        - industry_stats: The average campaign statistics for your industry.
        - list_id: The unique list id.
        - list_is_active: The status of the list used, namely if it's deleted or disabled.
        - list_name: The name of the list.
        - list_stats: The average campaign statistics for your list. This won't be present if we haven't calculated i...
        - opens: An object describing the open activity for the campaign.
        - preview_text: The preview text for the campaign.
        - rss_last_send: For RSS campaigns, the date and time of the last send in ISO 8601 format.
        - send_time: The date and time a campaign was sent in ISO 8601 format.
        - share_report: The url and password for the VIP report.
        - subject_line: The subject line for the campaign.
        - timeseries: An hourly breakdown of the performance of the campaign over the first 24 hours.
        - timewarp: An hourly breakdown of sends, opens, and clicks if a campaign is sent using timewarp.
        - type_: The type of campaign (regular, plain-text, ab_split, rss, automation, variate, or auto).
        - unsubscribed: The total number of unsubscribed members for this campaign.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ReportsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, campaign_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.Report`
    :   Get report details for a specific sent campaign
        
        Args:
            campaign_id: The unique id for the campaign
            **kwargs: Additional parameters
        
        Returns:
            Report

    `list(self, count: int | None = None, offset: int | None = None, type: str | None = None, before_send_time: str | None = None, since_send_time: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[Report], ReportsListResultMeta]`
    :   Get campaign reports
        
        Args:
            count: The number of records to return
            offset: Used for pagination
            type: The campaign type
            before_send_time: Restrict the response to campaigns sent before the set time
            since_send_time: Restrict the response to campaigns sent after the set time
            **kwargs: Additional parameters
        
        Returns:
            ReportsListResult

<a id="SegmentMembersQuery"></a>

`SegmentMembersQuery(connector: MailchimpConnector)`
:   Query class for SegmentMembers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, list_id: str, segment_id: str, count: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[SegmentMember], SegmentMembersListResultMeta]`
    :   Get information about members in a saved segment
        
        Args:
            list_id: The unique ID for the list
            segment_id: The unique id for the segment
            count: The number of records to return
            offset: Used for pagination
            **kwargs: Additional parameters
        
        Returns:
            SegmentMembersListResult

<a id="SegmentsQuery"></a>

`SegmentsQuery(connector: MailchimpConnector)`
:   Query class for Segments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, list_id: str, segment_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.Segment`
    :   Get information about a specific segment
        
        Args:
            list_id: The unique ID for the list
            segment_id: The unique id for the segment
            **kwargs: Additional parameters
        
        Returns:
            Segment

    `list(self, list_id: str, count: int | None = None, offset: int | None = None, type: str | None = None, since_created_at: str | None = None, before_created_at: str | None = None, since_updated_at: str | None = None, before_updated_at: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[Segment], SegmentsListResultMeta]`
    :   Get information about all available segments for a specific list
        
        Args:
            list_id: The unique ID for the list
            count: The number of records to return
            offset: Used for pagination
            type: Limit results based on segment type
            since_created_at: Restrict results to segments created after the set time
            before_created_at: Restrict results to segments created before the set time
            since_updated_at: Restrict results to segments updated after the set time
            before_updated_at: Restrict results to segments updated before the set time
            **kwargs: Additional parameters
        
        Returns:
            SegmentsListResult

<a id="TagsQuery"></a>

`TagsQuery(connector: MailchimpConnector)`
:   Query class for Tags entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, list_id: str, name: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[Tag], TagsListResultMeta]`
    :   Search for tags on a list by name
        
        Args:
            list_id: The unique ID for the list
            name: The search query used to filter tags
            **kwargs: Additional parameters
        
        Returns:
            TagsListResult

<a id="UnsubscribesQuery"></a>

`UnsubscribesQuery(connector: MailchimpConnector)`
:   Query class for Unsubscribes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, campaign_id: str, count: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[Unsubscribe], UnsubscribesListResultMeta]`
    :   Get information about members who have unsubscribed from a specific campaign
        
        Args:
            campaign_id: The unique id for the campaign
            count: The number of records to return
            offset: Used for pagination
            **kwargs: Additional parameters
        
        Returns:
            UnsubscribesListResult