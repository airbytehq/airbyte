---
id: airbyte_agent_sdk-connectors-zendesk_support-connector
title: airbyte_agent_sdk.connectors.zendesk_support.connector
---

Module airbyte_agent_sdk.connectors.zendesk_support.connector
=============================================================
Zendesk-Support connector.

Classes
-------

<a id="ArticleAttachmentsQuery"></a>

`ArticleAttachmentsQuery(connector: ZendeskSupportConnector)`
:   Query class for ArticleAttachments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `download(self, article_id: str, attachment_id: str, range_header: str | None = None, **kwargs) ‑> AsyncIterator[bytes]`
    :   Downloads the file content of a specific attachment
        
        Args:
            article_id: The unique ID of the article
            attachment_id: The unique ID of the attachment
            range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
            **kwargs: Additional parameters
        
        Returns:
            AsyncIterator[bytes]

    `download_local(self, article_id: str, attachment_id: str, path: str, range_header: str | None = None, **kwargs) ‑> Path`
    :   Downloads the file content of a specific attachment and save to file.
        
        Args:
            article_id: The unique ID of the article
            attachment_id: The unique ID of the attachment
            range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
            path: File path to save downloaded content
            **kwargs: Additional parameters
        
        Returns:
            str: Path to the downloaded file

    `get(self, article_id: str, attachment_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ArticleAttachment`
    :   Retrieves the metadata of a specific attachment for a specific article
        
        Args:
            article_id: The unique ID of the article
            attachment_id: The unique ID of the attachment
            **kwargs: Additional parameters
        
        Returns:
            ArticleAttachment

    `list(self, article_id: str, page: int | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[ArticleAttachment], ArticleAttachmentsListResultMeta]`
    :   Returns a list of all attachments for a specific article
        
        Args:
            article_id: The unique ID of the article
            page: Page number for pagination
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            ArticleAttachmentsListResult

<a id="ArticlesQuery"></a>

`ArticlesQuery(connector: ZendeskSupportConnector)`
:   Query class for Articles entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.Article`
    :   Retrieves the details of a specific article
        
        Args:
            id: The unique ID of the article
            **kwargs: Additional parameters
        
        Returns:
            Article

    `list(self, page: int | None = None, sort_by: str | None = None, sort_order: str | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Article], ArticlesListResultMeta]`
    :   Returns a list of all articles in the Help Center
        
        Args:
            page: Page number for pagination
            sort_by: Sort articles by field
            sort_order: Sort order
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            ArticlesListResult

<a id="AttachmentsQuery"></a>

`AttachmentsQuery(connector: ZendeskSupportConnector)`
:   Query class for Attachments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `download(self, attachment_id: str, range_header: str | None = None, **kwargs) ‑> AsyncIterator[bytes]`
    :   Downloads the file content of a ticket attachment
        
        Args:
            attachment_id: The ID of the attachment
            range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
            **kwargs: Additional parameters
        
        Returns:
            AsyncIterator[bytes]

    `download_local(self, attachment_id: str, path: str, range_header: str | None = None, **kwargs) ‑> Path`
    :   Downloads the file content of a ticket attachment and save to file.
        
        Args:
            attachment_id: The ID of the attachment
            range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
            path: File path to save downloaded content
            **kwargs: Additional parameters
        
        Returns:
            str: Path to the downloaded file

    `get(self, attachment_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.Attachment`
    :   Returns an attachment by its ID
        
        Args:
            attachment_id: The ID of the attachment
            **kwargs: Additional parameters
        
        Returns:
            Attachment

<a id="AutomationsQuery"></a>

`AutomationsQuery(connector: ZendeskSupportConnector)`
:   Query class for Automations entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, automation_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.Automation`
    :   Returns an automation by its ID
        
        Args:
            automation_id: The ID of the automation
            **kwargs: Additional parameters
        
        Returns:
            Automation

    `list(self, page: int | None = None, active: bool | None = None, sort_by: str | None = None, sort_order: str | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Automation], AutomationsListResultMeta]`
    :   Returns a list of all automations for the account
        
        Args:
            page: Page number for pagination
            active: Filter by active status
            sort_by: Sort field for offset pagination
            sort_order: Sort order for offset pagination
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            AutomationsListResult

<a id="BrandsQuery"></a>

`BrandsQuery(connector: ZendeskSupportConnector)`
:   Query class for Brands entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BrandsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[BrandsSearchData]`
    :   Search brands records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BrandsSearchFilter):
        - active: Indicates whether the brand is set as active
        - brand_url: The public URL of the brand
        - created_at: Timestamp when the brand was created
        - default: Indicates whether the brand is the default brand for tickets generated from non-branded channels
        - has_help_center: Indicates whether the brand has a Help Center enabled
        - help_center_state: The state of the Help Center, with allowed values of enabled, disabled, or restricted
        - host_mapping: The host mapping configuration for the brand, visible only to administrators
        - id: Unique identifier automatically assigned when the brand is created
        - is_deleted: Indicates whether the brand has been deleted
        - logo: Brand logo image file represented as an Attachment object
        - name: The name of the brand
        - signature_template: The signature template used for the brand
        - subdomain: The subdomain associated with the brand
        - ticket_form_ids: Array of ticket form IDs that are available for use by this brand
        - updated_at: Timestamp when the brand was last updated
        - url: The API URL for accessing this brand resource
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BrandsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, brand_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.Brand`
    :   Returns a brand by its ID
        
        Args:
            brand_id: The ID of the brand
            **kwargs: Additional parameters
        
        Returns:
            Brand

    `list(self, page: int | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Brand], BrandsListResultMeta]`
    :   Returns a list of all brands for the account
        
        Args:
            page: Page number for pagination
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            BrandsListResult

<a id="DeletedTicketsQuery"></a>

`DeletedTicketsQuery(connector: ZendeskSupportConnector)`
:   Query class for DeletedTickets entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: DeletedTicketsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[DeletedTicketsSearchData]`
    :   Search deleted_tickets records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (DeletedTicketsSearchFilter):
        - id: The unique identifier of the deleted ticket
        - subject: The subject or title of the deleted ticket
        - description: Additional details or comments about the deleted ticket
        - deleted_at: The timestamp when the ticket was deleted
        - previous_state: The state of the ticket before it was deleted
        - actor: The user who performed the deletion action
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            DeletedTicketsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page: int | None = None, sort_by: str | None = None, sort_order: str | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[DeletedTicket], DeletedTicketsListResultMeta]`
    :   Returns a list of deleted tickets in your account. Only tickets deleted in the past 30 days are returned.
        
        Args:
            page: Page number for pagination
            sort_by: Sort tickets by field
            sort_order: Sort order
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            DeletedTicketsListResult

<a id="GroupMembershipsQuery"></a>

`GroupMembershipsQuery(connector: ZendeskSupportConnector)`
:   Query class for GroupMemberships entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, page: int | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[GroupMembership], GroupMembershipsListResultMeta]`
    :   Returns a list of all group memberships
        
        Args:
            page: Page number for pagination
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            GroupMembershipsListResult

<a id="GroupsQuery"></a>

`GroupsQuery(connector: ZendeskSupportConnector)`
:   Query class for Groups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: GroupsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[GroupsSearchData]`
    :   Search groups records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (GroupsSearchFilter):
        - created_at: Timestamp indicating when the group was created
        - default: Indicates if the group is the default one for the account
        - deleted: Indicates whether the group has been deleted
        - description: The description of the group
        - id: Unique identifier automatically assigned when creating groups
        - is_public: Indicates if the group is public (true) or private (false)
        - name: The name of the group
        - updated_at: Timestamp indicating when the group was last updated
        - url: The API URL of the group
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            GroupsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, group_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.Group`
    :   Returns a group by its ID
        
        Args:
            group_id: The ID of the group
            **kwargs: Additional parameters
        
        Returns:
            Group

    `list(self, page: int | None = None, exclude_deleted: bool | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Group], GroupsListResultMeta]`
    :   Returns a list of all groups in your account
        
        Args:
            page: Page number for pagination
            exclude_deleted: Exclude deleted groups
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            GroupsListResult

<a id="MacrosQuery"></a>

`MacrosQuery(connector: ZendeskSupportConnector)`
:   Query class for Macros entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, macro_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.Macro`
    :   Returns a macro by its ID
        
        Args:
            macro_id: The ID of the macro
            **kwargs: Additional parameters
        
        Returns:
            Macro

    `list(self, page: int | None = None, access: str | None = None, active: bool | None = None, category: int | None = None, group_id: int | None = None, only_viewable: bool | None = None, sort_by: str | None = None, sort_order: str | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Macro], MacrosListResultMeta]`
    :   Returns a list of all macros for the account
        
        Args:
            page: Page number for pagination
            access: Filter by access level
            active: Filter by active status
            category: Filter by category
            group_id: Filter by group ID
            only_viewable: Return only viewable macros
            sort_by: Sort results
            sort_order: Sort order
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            MacrosListResult

<a id="OrganizationMembershipsQuery"></a>

`OrganizationMembershipsQuery(connector: ZendeskSupportConnector)`
:   Query class for OrganizationMemberships entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, page: int | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[OrganizationMembership], OrganizationMembershipsListResultMeta]`
    :   Returns a list of all organization memberships
        
        Args:
            page: Page number for pagination
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            OrganizationMembershipsListResult

<a id="OrganizationsQuery"></a>

`OrganizationsQuery(connector: ZendeskSupportConnector)`
:   Query class for Organizations entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OrganizationsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[OrganizationsSearchData]`
    :   Search organizations records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OrganizationsSearchFilter):
        - created_at: Timestamp when the organization was created
        - deleted_at: Timestamp when the organization was deleted
        - details: Details about the organization, such as the address
        - domain_names: Array of domain names associated with this organization for automatic user assignment
        - external_id: Unique external identifier to associate the organization to an external record (case-insensitive)
        - group_id: ID of the group where new tickets from users in this organization are automatically assigned
        - id: Unique identifier automatically assigned when the organization is created
        - name: Unique name for the organization (mandatory field)
        - notes: Notes about the organization
        - organization_fields: Key-value object for custom organization fields
        - shared_comments: Boolean indicating whether end users in this organization can comment on each other's tickets
        - shared_tickets: Boolean indicating whether end users in this organization can see each other's tickets
        - tags: Array of tags associated with the organization
        - updated_at: Timestamp of the last update to the organization
        - url: The API URL of this organization
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OrganizationsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, organization_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.Organization`
    :   Returns an organization by its ID
        
        Args:
            organization_id: The ID of the organization
            **kwargs: Additional parameters
        
        Returns:
            Organization

    `list(self, page: int | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Organization], OrganizationsListResultMeta]`
    :   Returns a list of all organizations in your account
        
        Args:
            page: Page number for pagination
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            OrganizationsListResult

<a id="SatisfactionRatingsQuery"></a>

`SatisfactionRatingsQuery(connector: ZendeskSupportConnector)`
:   Query class for SatisfactionRatings entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SatisfactionRatingsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[SatisfactionRatingsSearchData]`
    :   Search satisfaction_ratings records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SatisfactionRatingsSearchFilter):
        - assignee_id: The identifier of the agent assigned to the ticket at the time the rating was submitted
        - comment: Optional comment provided by the requester with the rating
        - created_at: Timestamp indicating when the satisfaction rating was created
        - group_id: The identifier of the group assigned to the ticket at the time the rating was submitted
        - id: Unique identifier for the satisfaction rating, automatically assigned upon creation
        - reason: Free-text reason for a bad rating provided by the requester in a follow-up question
        - reason_id: Identifier for the predefined reason given for a negative rating
        - requester_id: The identifier of the ticket requester who submitted the satisfaction rating
        - score: The satisfaction rating value: 'offered', 'unoffered', 'good', or 'bad'
        - ticket_id: The identifier of the ticket being rated
        - updated_at: Timestamp indicating when the satisfaction rating was last updated
        - url: The API URL of this satisfaction rating resource
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SatisfactionRatingsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, satisfaction_rating_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.SatisfactionRating`
    :   Returns a satisfaction rating by its ID
        
        Args:
            satisfaction_rating_id: The ID of the satisfaction rating
            **kwargs: Additional parameters
        
        Returns:
            SatisfactionRating

    `list(self, page: int | None = None, score: str | None = None, start_time: int | None = None, end_time: int | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[SatisfactionRating], SatisfactionRatingsListResultMeta]`
    :   Returns a list of all satisfaction ratings
        
        Args:
            page: Page number for pagination
            score: Filter by score
            start_time: Start time (Unix epoch)
            end_time: End time (Unix epoch)
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            SatisfactionRatingsListResult

<a id="SlaPoliciesQuery"></a>

`SlaPoliciesQuery(connector: ZendeskSupportConnector)`
:   Query class for SlaPolicies entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, sla_policy_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.SLAPolicy`
    :   Returns an SLA policy by its ID
        
        Args:
            sla_policy_id: The ID of the SLA policy
            **kwargs: Additional parameters
        
        Returns:
            SLAPolicy

    `list(self, page: int | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[SLAPolicy], SlaPoliciesListResultMeta]`
    :   Returns a list of all SLA policies
        
        Args:
            page: Page number for pagination
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            SlaPoliciesListResult

<a id="TagsQuery"></a>

`TagsQuery(connector: ZendeskSupportConnector)`
:   Query class for Tags entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TagsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[TagsSearchData]`
    :   Search tags records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TagsSearchFilter):
        - count: The number of times this tag has been used across resources
        - name: The tag name string used to label and categorize resources
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TagsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page: int | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Tag], TagsListResultMeta]`
    :   Returns a list of all tags used in the account
        
        Args:
            page: Page number for pagination
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            TagsListResult

<a id="TicketAuditsQuery"></a>

`TicketAuditsQuery(connector: ZendeskSupportConnector)`
:   Query class for TicketAudits entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TicketAuditsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[TicketAuditsSearchData]`
    :   Search ticket_audits records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TicketAuditsSearchFilter):
        - attachments: Files or documents attached to the audit
        - author_id: The unique identifier of the user who created the audit
        - created_at: Timestamp indicating when the audit was created
        - events: Array of events that occurred in this audit, such as field changes, comments, or tag updates
        - id: Unique identifier for the audit record, automatically assigned when the audit is created
        - metadata: Custom and system data associated with the audit
        - ticket_id: The unique identifier of the ticket associated with this audit
        - via: Describes how the audit was created, providing context about the creation source
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TicketAuditsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, ticket_id: str, page: int | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[TicketAudit], TicketAuditsListResultMeta]`
    :   Returns a list of audits for a specific ticket
        
        Args:
            ticket_id: The ID of the ticket
            page: Page number for pagination
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            TicketAuditsListResult

<a id="TicketCommentsQuery"></a>

`TicketCommentsQuery(connector: ZendeskSupportConnector)`
:   Query class for TicketComments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TicketCommentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[TicketCommentsSearchData]`
    :   Search ticket_comments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TicketCommentsSearchFilter):
        - attachments: List of files or media attached to the comment
        - audit_id: Identifier of the audit record associated with this comment event
        - author_id: Identifier of the user who created the comment
        - body: Content of the comment in its original format
        - created_at: Timestamp when the comment was created
        - event_type: Specific classification of the event within the ticket event stream
        - html_body: HTML-formatted content of the comment
        - id: Unique identifier for the comment event
        - metadata: Additional structured information about the comment not covered by standard fields
        - plain_body: Plain text content of the comment without formatting
        - public: Boolean indicating whether the comment is visible to end users or is an internal note
        - ticket_id: Identifier of the ticket to which this comment belongs
        - timestamp: Timestamp of when the event occurred in the incremental export stream
        - type_: Type of event, typically indicating this is a comment event
        - uploads: Array of upload tokens or identifiers for files being attached to the comment
        - via: Channel or method through which the comment was submitted
        - via_reference_id: Reference identifier for the channel through which the comment was created
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TicketCommentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, ticket_id: str, page: int | None = None, include_inline_images: bool | None = None, sort_order: str | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[TicketComment], TicketCommentsListResultMeta]`
    :   Returns a list of comments for a specific ticket
        
        Args:
            ticket_id: The ID of the ticket
            page: Page number for pagination
            include_inline_images: Include inline images in the response
            sort_order: Sort order for comments (always sorted by created_at)
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            TicketCommentsListResult

<a id="TicketFieldsQuery"></a>

`TicketFieldsQuery(connector: ZendeskSupportConnector)`
:   Query class for TicketFields entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TicketFieldsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[TicketFieldsSearchData]`
    :   Search ticket_fields records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TicketFieldsSearchFilter):
        - active: Whether this field is currently available for use
        - agent_description: A description of the ticket field that only agents can see
        - collapsed_for_agents: If true, the field is shown to agents by default; if false, it is hidden alongside infrequently used fields
        - created_at: Timestamp when the custom ticket field was created
        - custom_field_options: Array of option objects for custom ticket fields of type multiselect or tagger
        - custom_statuses: List of customized ticket statuses, only present for system ticket fields of type custom_status
        - description: Text describing the purpose of the ticket field to users
        - editable_in_portal: Whether this field is editable by end users in Help Center
        - id: Unique identifier for the ticket field, automatically assigned when created
        - key: Internal identifier or reference key for the field
        - position: The relative position of the ticket field on a ticket, controlling display order
        - raw_description: The dynamic content placeholder if present, or the description value if not
        - raw_title: The dynamic content placeholder if present, or the title value if not
        - raw_title_in_portal: The dynamic content placeholder if present, or the title_in_portal value if not
        - regexp_for_validation: For regexp fields only, the validation pattern for a field value to be deemed valid
        - removable: If false, this field is a system field that must be present on all tickets
        - required: If true, agents must enter a value in the field to change the ticket status to solved
        - required_in_portal: If true, end users must enter a value in the field to create a request
        - sub_type_id: For system ticket fields of type priority and status, controlling available options
        - system_field_options: Array of options for system ticket fields of type tickettype, priority, or status
        - tag: For checkbox fields only, a tag added to tickets when the checkbox field is selected
        - title: The title of the ticket field displayed to agents
        - title_in_portal: The title of the ticket field displayed to end users in Help Center
        - type_: Field type such as text, textarea, checkbox, date, integer, decimal, regexp, multiselect, or tagger
        - updated_at: Timestamp when the custom ticket field was last updated
        - url: The API URL for this ticket field resource
        - visible_in_portal: Whether this field is visible to end users in Help Center
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TicketFieldsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, ticket_field_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.TicketField`
    :   Returns a ticket field by its ID
        
        Args:
            ticket_field_id: The ID of the ticket field
            **kwargs: Additional parameters
        
        Returns:
            TicketField

    `list(self, page: int | None = None, locale: str | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[TicketField], TicketFieldsListResultMeta]`
    :   Returns a list of all ticket fields
        
        Args:
            page: Page number for pagination
            locale: Locale for the results
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            TicketFieldsListResult

<a id="TicketFormsQuery"></a>

`TicketFormsQuery(connector: ZendeskSupportConnector)`
:   Query class for TicketForms entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TicketFormsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[TicketFormsSearchData]`
    :   Search ticket_forms records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TicketFormsSearchFilter):
        - active: Indicates if the form is set as active
        - agent_conditions: Array of condition sets for agent workspaces
        - created_at: Timestamp when the ticket form was created
        - default: Indicates if the form is the default form for this account
        - display_name: The name of the form that is displayed to an end user
        - end_user_conditions: Array of condition sets for end user products
        - end_user_visible: Indicates if the form is visible to the end user
        - id: Unique identifier for the ticket form, automatically assigned when creating the form
        - in_all_brands: Indicates if the form is available for use in all brands on this account
        - name: The name of the ticket form
        - position: The position of this form among other forms in the account, such as in a dropdown
        - raw_display_name: The dynamic content placeholder if present, or the display_name value if not
        - raw_name: The dynamic content placeholder if present, or the name value if not
        - restricted_brand_ids: IDs of all brands that this ticket form is restricted to
        - ticket_field_ids: IDs of all ticket fields included in this ticket form
        - updated_at: Timestamp of the last update to the ticket form
        - url: URL of the ticket form
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TicketFormsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, ticket_form_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.TicketForm`
    :   Returns a ticket form by its ID
        
        Args:
            ticket_form_id: The ID of the ticket form
            **kwargs: Additional parameters
        
        Returns:
            TicketForm

    `list(self, page: int | None = None, active: bool | None = None, end_user_visible: bool | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[TicketForm], TicketFormsListResultMeta]`
    :   Returns a list of all ticket forms for the account
        
        Args:
            page: Page number for pagination
            active: Filter by active status
            end_user_visible: Filter by end user visibility
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            TicketFormsListResult

<a id="TicketMetricsQuery"></a>

`TicketMetricsQuery(connector: ZendeskSupportConnector)`
:   Query class for TicketMetrics entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TicketMetricsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[TicketMetricsSearchData]`
    :   Search ticket_metrics records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TicketMetricsSearchFilter):
        - agent_wait_time_in_minutes: Number of minutes the agent spent waiting during calendar and business hours
        - assigned_at: Timestamp when the ticket was assigned
        - assignee_stations: Number of assignees the ticket had
        - assignee_updated_at: Timestamp when the assignee last updated the ticket
        - created_at: Timestamp when the metric record was created
        - custom_status_updated_at: Timestamp when the ticket's custom status was last updated
        - first_resolution_time_in_minutes: Number of minutes to the first resolution time during calendar and business hours
        - full_resolution_time_in_minutes: Number of minutes to the full resolution during calendar and business hours
        - generated_timestamp: Timestamp of when record was last updated
        - group_stations: Number of groups the ticket passed through
        - id: Unique identifier for the ticket metric record
        - initially_assigned_at: Timestamp when the ticket was initially assigned
        - instance_id: ID of the Zendesk instance associated with the ticket
        - latest_comment_added_at: Timestamp when the latest comment was added
        - metric: Ticket metrics data
        - on_hold_time_in_minutes: Number of minutes on hold
        - reopens: Total number of times the ticket was reopened
        - replies: The number of public replies added to a ticket by an agent
        - reply_time_in_minutes: Number of minutes to the first reply during calendar and business hours
        - reply_time_in_seconds: Number of seconds to the first reply during calendar hours, only available for Messaging tickets
        - requester_updated_at: Timestamp when the requester last updated the ticket
        - requester_wait_time_in_minutes: Number of minutes the requester spent waiting during calendar and business hours
        - solved_at: Timestamp when the ticket was solved
        - status: The current status of the ticket (open, pending, solved, etc.).
        - status_updated_at: Timestamp when the status of the ticket was last updated
        - ticket_id: Identifier of the associated ticket
        - time: Time related to the ticket
        - type_: Type of ticket
        - updated_at: Timestamp when the metric record was last updated
        - url: The API url of the ticket metric
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TicketMetricsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page: int | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[TicketMetric], TicketMetricsListResultMeta]`
    :   Returns a list of all ticket metrics
        
        Args:
            page: Page number for pagination
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            TicketMetricsListResult

<a id="TicketsQuery"></a>

`TicketsQuery(connector: ZendeskSupportConnector)`
:   Query class for Tickets entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TicketsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[TicketsSearchData]`
    :   Search tickets records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TicketsSearchFilter):
        - allow_attachments: Boolean indicating whether attachments are allowed on the ticket
        - allow_channelback: Boolean indicating whether agents can reply to the ticket through the original channel
        - assignee_id: Unique identifier of the agent currently assigned to the ticket
        - brand_id: Unique identifier of the brand associated with the ticket in multi-brand accounts
        - collaborator_ids: Array of user identifiers who are collaborating on the ticket
        - created_at: Timestamp indicating when the ticket was created
        - custom_fields: Array of custom field values specific to the account's ticket configuration
        - custom_status_id: Unique identifier of the custom status applied to the ticket
        - deleted_ticket_form_id: The ID of the ticket form that was previously associated with this ticket but has since been deleted
        - description: Initial description or content of the ticket when it was created
        - due_at: Timestamp indicating when the ticket is due for completion or resolution
        - email_cc_ids: Array of user identifiers who are CC'd on ticket email notifications
        - external_id: External identifier for the ticket, used for integrations with other systems
        - fields: Array of ticket field values including both system and custom fields
        - follower_ids: Array of user identifiers who are following the ticket for updates
        - followup_ids: Array of identifiers for follow-up tickets related to this ticket
        - forum_topic_id: Unique identifier linking the ticket to a forum topic if applicable
        - from_messaging_channel: Boolean indicating whether the ticket originated from a messaging channel
        - generated_timestamp: Timestamp updated for all ticket updates including system changes, used for incremental export
        - group_id: Unique identifier of the agent group assigned to handle the ticket
        - has_incidents: Boolean indicating whether this problem ticket has related incident tickets
        - id: Unique identifier for the ticket
        - is_public: Boolean indicating whether the ticket is publicly visible
        - organization_id: Unique identifier of the organization associated with the ticket
        - priority: Priority level assigned to the ticket (e.g., urgent, high, normal, low)
        - problem_id: Unique identifier of the problem ticket if this is an incident ticket
        - raw_subject: Original unprocessed subject line before any system modifications
        - recipient: Email address or identifier of the ticket recipient
        - requester_id: Unique identifier of the user who requested or created the ticket
        - satisfaction_rating: Object containing customer satisfaction rating data for the ticket
        - sharing_agreement_ids: Array of sharing agreement identifiers if the ticket is shared across Zendesk instances
        - status: Current status of the ticket (e.g., new, open, pending, solved, closed)
        - subject: Subject line of the ticket describing the issue or request
        - submitter_id: Unique identifier of the user who submitted the ticket on behalf of the requester
        - tags: Array of tags applied to the ticket for categorization and filtering
        - ticket_form_id: Unique identifier of the ticket form used when creating the ticket
        - type_: Type of ticket (e.g., problem, incident, question, task)
        - updated_at: Timestamp indicating when the ticket was last updated with a ticket event
        - url: API URL to access the full ticket resource
        - result_type: The type of the search result (e.g. ticket) when returned from search endpoints
        - via: Object describing the channel and method through which the ticket was created
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TicketsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, ticket_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.Ticket`
    :   Returns a ticket by its ID
        
        Args:
            ticket_id: The ID of the ticket
            **kwargs: Additional parameters
        
        Returns:
            Ticket

    `list(self, page: int | None = None, external_id: str | None = None, sort_by: str | None = None, sort_order: str | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Ticket], TicketsListResultMeta]`
    :   Returns a list of all tickets in your account
        
        Args:
            page: Page number for pagination
            external_id: Lists tickets by external id
            sort_by: Sort field for offset pagination
            sort_order: Sort order for offset pagination
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            TicketsListResult

<a id="TriggersQuery"></a>

`TriggersQuery(connector: ZendeskSupportConnector)`
:   Query class for Triggers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, trigger_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.Trigger`
    :   Returns a trigger by its ID
        
        Args:
            trigger_id: The ID of the trigger
            **kwargs: Additional parameters
        
        Returns:
            Trigger

    `list(self, page: int | None = None, active: bool | None = None, category_id: str | None = None, sort_by: str | None = None, sort_order: str | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Trigger], TriggersListResultMeta]`
    :   Returns a list of all triggers for the account
        
        Args:
            page: Page number for pagination
            active: Filter by active status
            category_id: Filter by category ID
            sort_by: Sort field for offset pagination
            sort_order: Sort order for offset pagination
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            TriggersListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: ZendeskSupportConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - active: Indicates if the user account is currently active
        - alias: Alternative name or nickname for the user
        - chat_only: Indicates if the user can only interact via chat
        - created_at: Timestamp indicating when the user was created
        - custom_role_id: Identifier for a custom role assigned to the user
        - default_group_id: Identifier of the default group assigned to the user
        - details: Additional descriptive information about the user
        - email: Email address of the user
        - external_id: External system identifier for the user, used for integrations
        - iana_time_zone: IANA standard time zone identifier for the user
        - id: Unique identifier for the user
        - last_login_at: Timestamp of the user's most recent login
        - locale: Locale setting determining language and regional format preferences
        - locale_id: Identifier for the user's locale preference
        - moderator: Indicates if the user has moderator privileges
        - name: Display name of the user
        - notes: Internal notes about the user, visible only to agents
        - only_private_comments: Indicates if the user can only make private comments on tickets
        - organization_id: Identifier of the organization the user belongs to
        - permanently_deleted: Indicates if the user has been permanently deleted from the system
        - phone: Phone number of the user
        - photo: Profile photo or avatar of the user
        - report_csv: Indicates if the user receives reports in CSV format
        - restricted_agent: Indicates if the agent has restricted access permissions
        - role: Role assigned to the user defining their permissions level
        - role_type: Type classification of the user's role
        - shared: Indicates if the user is shared across multiple accounts
        - shared_agent: Indicates if the user is a shared agent across multiple brands or accounts
        - shared_phone_number: Indicates if the phone number is shared with other users
        - signature: Email signature text for the user
        - suspended: Indicates if the user account is suspended
        - tags: Labels or tags associated with the user for categorization
        - ticket_restriction: Defines which tickets the user can access based on restrictions
        - time_zone: Time zone setting for the user
        - two_factor_auth_enabled: Indicates if two-factor authentication is enabled for the user
        - updated_at: Timestamp indicating when the user was last updated
        - url: API endpoint URL for accessing the user's detailed information
        - user_fields: Custom field values specific to the user, stored as key-value pairs
        - verified: Indicates if the user's identity has been verified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            UsersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, user_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.User`
    :   Returns a user by their ID
        
        Args:
            user_id: The ID of the user
            **kwargs: Additional parameters
        
        Returns:
            User

    `list(self, page: int | None = None, role: str | None = None, external_id: str | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[User], UsersListResultMeta]`
    :   Returns a list of all users in your account
        
        Args:
            page: Page number for pagination
            role: Filter by role
            external_id: Filter by external id
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult

<a id="ViewsQuery"></a>

`ViewsQuery(connector: ZendeskSupportConnector)`
:   Query class for Views entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, view_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.View`
    :   Returns a view by its ID
        
        Args:
            view_id: The ID of the view
            **kwargs: Additional parameters
        
        Returns:
            View

    `list(self, page: int | None = None, access: str | None = None, active: bool | None = None, group_id: int | None = None, sort_by: str | None = None, sort_order: str | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[View], ViewsListResultMeta]`
    :   Returns a list of all views for the account
        
        Args:
            page: Page number for pagination
            access: Filter by access level
            active: Filter by active status
            group_id: Filter by group ID
            sort_by: Sort results
            sort_order: Sort order
            per_page: Number of results per page
            **kwargs: Additional parameters
        
        Returns:
            ViewsListResult

<a id="ZendeskSupportConnector"></a>

`ZendeskSupportConnector(auth_config: ZendeskSupportAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, subdomain: str | None = None)`
:   Type-safe Zendesk-Support API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new zendesk-support connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., ZendeskSupportAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            subdomain: Your Zendesk subdomain
    Examples:
        # Local mode (direct API calls)
        connector = ZendeskSupportConnector(auth_config=ZendeskSupportAuthConfig(access_token="...", refresh_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = ZendeskSupportConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = ZendeskSupportConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'ZendeskSupportAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None)`
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
            replication_config: Optional replication settings dict.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A ZendeskSupportConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await ZendeskSupportConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ZendeskSupportAuthConfig(access_token="...", refresh_token="..."),
            )
        
            # With server-side OAuth:
            connector = await ZendeskSupportConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> str`
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
            replication_config: Optional replication settings dict. Merged with OAuth credentials.
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            The OAuth consent URL
        
        Example:
            consent_url = await ZendeskSupportConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Zendesk-Support Source",
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @ZendeskSupportConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ZendeskSupportConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await ZendeskSupportConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            ZendeskSupportCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'download', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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