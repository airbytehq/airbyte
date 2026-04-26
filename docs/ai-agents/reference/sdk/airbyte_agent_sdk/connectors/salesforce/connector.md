---
id: airbyte_agent_sdk-connectors-salesforce-connector
title: airbyte_agent_sdk.connectors.salesforce.connector
---

Module airbyte_agent_sdk.connectors.salesforce.connector
========================================================
Salesforce connector.

Classes
-------

<a id="AccountsQuery"></a>

`AccountsQuery(connector: SalesforceConnector)`
:   Query class for Accounts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[SearchResult]`
    :   Search for accounts using SOSL (Salesforce Object Search Language).
        SOSL is optimized for text-based searches across multiple fields and objects.
        Use SOQL (list action) for structured queries with specific field conditions.
        
        
                Args:
                    q: SOSL search query. Format: FIND \{searchTerm\} IN scope RETURNING Object(fields) [LIMIT n]
        Examples:
        - "FIND \{Acme\} IN ALL FIELDS RETURNING Account(Id,Name)"
        - "FIND \{tech*\} IN NAME FIELDS RETURNING Account(Id,Name,Industry) LIMIT 50"
        - "FIND \{"exact phrase"\} RETURNING Account(Id,Name,Website)"
        
                    **kwargs: Additional parameters
        
                Returns:
                    AccountsApiSearchResult

    `context_store_search(self, query: AccountsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[AccountsSearchData]`
    :   Search accounts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AccountsSearchFilter):
        - id: Unique identifier for the account record
        - name: Name of the account or company
        - account_source: Source of the account record (e.g., Web, Referral)
        - billing_address: Complete billing address as a compound field
        - billing_city: City portion of the billing address
        - billing_country: Country portion of the billing address
        - billing_postal_code: Postal code portion of the billing address
        - billing_state: State or province portion of the billing address
        - billing_street: Street address portion of the billing address
        - created_by_id: ID of the user who created this account
        - created_date: Date and time when the account was created
        - description: Text description of the account
        - industry: Primary business industry of the account
        - is_deleted: Whether the account has been moved to the Recycle Bin
        - last_activity_date: Date of the last activity associated with this account
        - last_modified_by_id: ID of the user who last modified this account
        - last_modified_date: Date and time when the account was last modified
        - number_of_employees: Number of employees at the account
        - owner_id: ID of the user who owns this account
        - parent_id: ID of the parent account, if this is a subsidiary
        - phone: Primary phone number for the account
        - shipping_address: Complete shipping address as a compound field
        - shipping_city: City portion of the shipping address
        - shipping_country: Country portion of the shipping address
        - shipping_postal_code: Postal code portion of the shipping address
        - shipping_state: State or province portion of the shipping address
        - shipping_street: Street address portion of the shipping address
        - type_: Type of account (e.g., Customer, Partner, Competitor)
        - website: Website URL for the account
        - system_modstamp: System timestamp when the record was last modified
        
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

    `get(self, id: str | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.Account`
    :   Get a single account by ID. Returns all accessible fields by default.
        Use the `fields` parameter to retrieve only specific fields for better performance.
        
        
                Args:
                    id: Salesforce Account ID (18-character ID starting with '001')
                    fields: Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
        Example: "Id,Name,Industry,AnnualRevenue,Website"
        
                    **kwargs: Additional parameters
        
                Returns:
                    Account

    `list(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Account], AccountsListResultMeta]`
    :   Returns a list of accounts via SOQL query. Default returns up to 200 records.
        For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
        
        
                Args:
                    q: SOQL query for accounts. Default returns up to 200 records.
        To change the limit, provide your own query with a LIMIT clause.
        Example: "SELECT FIELDS(STANDARD) FROM Account ORDER BY LastModifiedDate DESC LIMIT 50"
        
                    **kwargs: Additional parameters
        
                Returns:
                    AccountsListResult

<a id="AttachmentsQuery"></a>

`AttachmentsQuery(connector: SalesforceConnector)`
:   Query class for Attachments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `download(self, id: str | None = None, range_header: str | None = None, **kwargs) ‑> AsyncIterator[bytes]`
    :   Downloads the binary file content of an attachment (legacy).
        First use the list or get action to retrieve the Attachment ID and file metadata,
        then use this action to download the actual file content.
        Note: Attachments are a legacy feature; consider using ContentVersion for new implementations.
        
        
                Args:
                    id: Salesforce Attachment ID (18-character ID starting with '00P').
        Obtain this ID from the list or get action.
        
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    **kwargs: Additional parameters
        
                Returns:
                    AsyncIterator[bytes]

    `download_local(self, path: str, id: str | None = None, range_header: str | None = None, **kwargs) ‑> Path`
    :   Downloads the binary file content of an attachment (legacy).
        First use the list or get action to retrieve the Attachment ID and file metadata,
        then use this action to download the actual file content.
        Note: Attachments are a legacy feature; consider using ContentVersion for new implementations.
         and save to file.
        
                Args:
                    id: Salesforce Attachment ID (18-character ID starting with '00P').
        Obtain this ID from the list or get action.
        
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    path: File path to save downloaded content
                    **kwargs: Additional parameters
        
                Returns:
                    str: Path to the downloaded file

    `get(self, id: str | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.Attachment`
    :   Get a single attachment's metadata by ID. Returns file metadata, not the file content.
        Use the download action to retrieve the actual file binary.
        Note: Attachments are a legacy feature; consider using ContentVersion for new implementations.
        
        
                Args:
                    id: Salesforce Attachment ID (18-character ID starting with '00P')
                    fields: Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
        Example: "Id,Name,ContentType,BodyLength,ParentId"
        
                    **kwargs: Additional parameters
        
                Returns:
                    Attachment

    `list(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Attachment], AttachmentsListResultMeta]`
    :   Returns a list of attachments (legacy) via SOQL query. Default returns up to 200 records.
        For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
        Note: Attachments are a legacy feature; consider using ContentVersion (Salesforce Files) for new implementations.
        
        
                Args:
                    q: SOQL query for attachments. Default returns up to 200 records.
        To change the limit, provide your own query with a LIMIT clause.
        Example: "SELECT Id, Name, ContentType, BodyLength, ParentId FROM Attachment WHERE ParentId = '001xx...' LIMIT 50"
        
                    **kwargs: Additional parameters
        
                Returns:
                    AttachmentsListResult

<a id="CampaignsQuery"></a>

`CampaignsQuery(connector: SalesforceConnector)`
:   Query class for Campaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[SearchResult]`
    :   Search for campaigns using SOSL (Salesforce Object Search Language).
        SOSL is optimized for text-based searches across multiple fields.
        
        
                Args:
                    q: SOSL search query. Format: FIND \{searchTerm\} RETURNING Campaign(fields) [LIMIT n]
        Examples:
        - "FIND \{webinar\} IN ALL FIELDS RETURNING Campaign(Id,Name,Type,Status)"
        - "FIND \{2024\} IN NAME FIELDS RETURNING Campaign(Id,Name,StartDate,IsActive) LIMIT 50"
        
                    **kwargs: Additional parameters
        
                Returns:
                    CampaignsApiSearchResult

    `get(self, id: str | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.Campaign`
    :   Get a single campaign by ID. Returns all accessible fields by default.
        Use the `fields` parameter to retrieve only specific fields for better performance.
        
        
                Args:
                    id: Salesforce Campaign ID (18-character ID starting with '701')
                    fields: Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
        Example: "Id,Name,Type,Status,StartDate,EndDate,IsActive"
        
                    **kwargs: Additional parameters
        
                Returns:
                    Campaign

    `list(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]`
    :   Returns a list of campaigns via SOQL query. Default returns up to 200 records.
        For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
        
        
                Args:
                    q: SOQL query for campaigns. Default returns up to 200 records.
        To change the limit, provide your own query with a LIMIT clause.
        Example: "SELECT FIELDS(STANDARD) FROM Campaign WHERE IsActive = true LIMIT 50"
        
                    **kwargs: Additional parameters
        
                Returns:
                    CampaignsListResult

<a id="CasesQuery"></a>

`CasesQuery(connector: SalesforceConnector)`
:   Query class for Cases entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[SearchResult]`
    :   Search for cases using SOSL (Salesforce Object Search Language).
        SOSL is optimized for text-based searches across multiple fields.
        
        
                Args:
                    q: SOSL search query. Format: FIND \{searchTerm\} RETURNING Case(fields) [LIMIT n]
        Examples:
        - "FIND \{login issue\} IN ALL FIELDS RETURNING Case(Id,CaseNumber,Subject,Status)"
        - "FIND \{urgent\} IN NAME FIELDS RETURNING Case(Id,Subject,Priority) LIMIT 25"
        
                    **kwargs: Additional parameters
        
                Returns:
                    CasesApiSearchResult

    `get(self, id: str | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.Case`
    :   Get a single case by ID. Returns all accessible fields by default.
        Use the `fields` parameter to retrieve only specific fields for better performance.
        
        
                Args:
                    id: Salesforce Case ID (18-character ID starting with '500')
                    fields: Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
        Example: "Id,CaseNumber,Subject,Status,Priority,ContactId,AccountId"
        
                    **kwargs: Additional parameters
        
                Returns:
                    Case

    `list(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Case], CasesListResultMeta]`
    :   Returns a list of cases via SOQL query. Default returns up to 200 records.
        For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
        
        
                Args:
                    q: SOQL query for cases. Default returns up to 200 records.
        To change the limit, provide your own query with a LIMIT clause.
        Example: "SELECT FIELDS(STANDARD) FROM Case WHERE Status = 'New' LIMIT 100"
        
                    **kwargs: Additional parameters
        
                Returns:
                    CasesListResult

<a id="ContactsQuery"></a>

`ContactsQuery(connector: SalesforceConnector)`
:   Query class for Contacts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[SearchResult]`
    :   Search for contacts using SOSL (Salesforce Object Search Language).
        SOSL is optimized for text-based searches across multiple fields.
        
        
                Args:
                    q: SOSL search query. Format: FIND \{searchTerm\} RETURNING Contact(fields) [LIMIT n]
        Examples:
        - "FIND \{John\} IN NAME FIELDS RETURNING Contact(Id,FirstName,LastName,Email)"
        - "FIND \{*@example.com\} IN EMAIL FIELDS RETURNING Contact(Id,Name,Email) LIMIT 25"
        
                    **kwargs: Additional parameters
        
                Returns:
                    ContactsApiSearchResult

    `context_store_search(self, query: ContactsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[ContactsSearchData]`
    :   Search contacts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ContactsSearchFilter):
        - id: Unique identifier for the contact record
        - account_id: ID of the account this contact is associated with
        - created_by_id: ID of the user who created this contact
        - created_date: Date and time when the contact was created
        - department: Department within the account where the contact works
        - email: Email address of the contact
        - first_name: First name of the contact
        - is_deleted: Whether the contact has been moved to the Recycle Bin
        - last_activity_date: Date of the last activity associated with this contact
        - last_modified_by_id: ID of the user who last modified this contact
        - last_modified_date: Date and time when the contact was last modified
        - last_name: Last name of the contact
        - lead_source: Source from which this contact originated
        - mailing_address: Complete mailing address as a compound field
        - mailing_city: City portion of the mailing address
        - mailing_country: Country portion of the mailing address
        - mailing_postal_code: Postal code portion of the mailing address
        - mailing_state: State or province portion of the mailing address
        - mailing_street: Street address portion of the mailing address
        - mobile_phone: Mobile phone number of the contact
        - name: Full name of the contact (read-only, concatenation of first and last name)
        - owner_id: ID of the user who owns this contact
        - phone: Business phone number of the contact
        - reports_to_id: ID of the contact this contact reports to
        - title: Job title of the contact
        - system_modstamp: System timestamp when the record was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ContactsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.Contact`
    :   Get a single contact by ID. Returns all accessible fields by default.
        Use the `fields` parameter to retrieve only specific fields for better performance.
        
        
                Args:
                    id: Salesforce Contact ID (18-character ID starting with '003')
                    fields: Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
        Example: "Id,FirstName,LastName,Email,Phone,AccountId"
        
                    **kwargs: Additional parameters
        
                Returns:
                    Contact

    `list(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Contact], ContactsListResultMeta]`
    :   Returns a list of contacts via SOQL query. Default returns up to 200 records.
        For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
        
        
                Args:
                    q: SOQL query for contacts. Default returns up to 200 records.
        To change the limit, provide your own query with a LIMIT clause.
        Example: "SELECT FIELDS(STANDARD) FROM Contact WHERE AccountId = '001xx...' LIMIT 50"
        
                    **kwargs: Additional parameters
        
                Returns:
                    ContactsListResult

<a id="ContentVersionsQuery"></a>

`ContentVersionsQuery(connector: SalesforceConnector)`
:   Query class for ContentVersions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `download(self, id: str | None = None, range_header: str | None = None, **kwargs) ‑> AsyncIterator[bytes]`
    :   Downloads the binary file content of a content version.
        First use the list or get action to retrieve the ContentVersion ID and file metadata (size, type, etc.),
        then use this action to download the actual file content.
        The response is the raw binary file data.
        
        
                Args:
                    id: Salesforce ContentVersion ID (18-character ID starting with '068').
        Obtain this ID from the list or get action.
        
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    **kwargs: Additional parameters
        
                Returns:
                    AsyncIterator[bytes]

    `download_local(self, path: str, id: str | None = None, range_header: str | None = None, **kwargs) ‑> Path`
    :   Downloads the binary file content of a content version.
        First use the list or get action to retrieve the ContentVersion ID and file metadata (size, type, etc.),
        then use this action to download the actual file content.
        The response is the raw binary file data.
         and save to file.
        
                Args:
                    id: Salesforce ContentVersion ID (18-character ID starting with '068').
        Obtain this ID from the list or get action.
        
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    path: File path to save downloaded content
                    **kwargs: Additional parameters
        
                Returns:
                    str: Path to the downloaded file

    `get(self, id: str | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.ContentVersion`
    :   Get a single content version's metadata by ID. Returns file metadata, not the file content.
        Use the download action to retrieve the actual file binary.
        
        
                Args:
                    id: Salesforce ContentVersion ID (18-character ID starting with '068')
                    fields: Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
        Example: "Id,Title,FileExtension,ContentSize,ContentDocumentId,IsLatest"
        
                    **kwargs: Additional parameters
        
                Returns:
                    ContentVersion

    `list(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[ContentVersion], ContentVersionsListResultMeta]`
    :   Returns a list of content versions (file metadata) via SOQL query. Default returns up to 200 records.
        For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
        Note: ContentVersion does not support FIELDS(STANDARD), so specific fields must be listed.
        
        
                Args:
                    q: SOQL query for content versions. Default returns up to 200 records.
        To change the limit, provide your own query with a LIMIT clause.
        Example: "SELECT Id, Title, FileExtension, ContentSize FROM ContentVersion WHERE IsLatest = true LIMIT 50"
        
                    **kwargs: Additional parameters
        
                Returns:
                    ContentVersionsListResult

<a id="EventsQuery"></a>

`EventsQuery(connector: SalesforceConnector)`
:   Query class for Events entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[SearchResult]`
    :   Search for events using SOSL (Salesforce Object Search Language).
        SOSL is optimized for text-based searches across multiple fields.
        
        
                Args:
                    q: SOSL search query. Format: FIND \{searchTerm\} RETURNING Event(fields) [LIMIT n]
        Examples:
        - "FIND \{meeting\} IN ALL FIELDS RETURNING Event(Id,Subject,StartDateTime,Location)"
        - "FIND \{demo\} IN NAME FIELDS RETURNING Event(Id,Subject,EndDateTime) LIMIT 25"
        
                    **kwargs: Additional parameters
        
                Returns:
                    EventsApiSearchResult

    `get(self, id: str | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.Event`
    :   Get a single event by ID. Returns all accessible fields by default.
        Use the `fields` parameter to retrieve only specific fields for better performance.
        
        
                Args:
                    id: Salesforce Event ID (18-character ID starting with '00U')
                    fields: Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
        Example: "Id,Subject,StartDateTime,EndDateTime,Location,WhoId,WhatId"
        
                    **kwargs: Additional parameters
        
                Returns:
                    Event

    `list(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Event], EventsListResultMeta]`
    :   Returns a list of events via SOQL query. Default returns up to 200 records.
        For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
        
        
                Args:
                    q: SOQL query for events. Default returns up to 200 records.
        To change the limit, provide your own query with a LIMIT clause.
        Example: "SELECT FIELDS(STANDARD) FROM Event WHERE StartDateTime > TODAY LIMIT 50"
        
                    **kwargs: Additional parameters
        
                Returns:
                    EventsListResult

<a id="LeadsQuery"></a>

`LeadsQuery(connector: SalesforceConnector)`
:   Query class for Leads entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[SearchResult]`
    :   Search for leads using SOSL (Salesforce Object Search Language).
        SOSL is optimized for text-based searches across multiple fields.
        
        
                Args:
                    q: SOSL search query. Format: FIND \{searchTerm\} RETURNING Lead(fields) [LIMIT n]
        Examples:
        - "FIND \{Smith\} IN NAME FIELDS RETURNING Lead(Id,FirstName,LastName,Company,Status)"
        - "FIND \{marketing\} IN ALL FIELDS RETURNING Lead(Id,Name,LeadSource) LIMIT 50"
        
                    **kwargs: Additional parameters
        
                Returns:
                    LeadsApiSearchResult

    `context_store_search(self, query: LeadsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[LeadsSearchData]`
    :   Search leads records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (LeadsSearchFilter):
        - id: Unique identifier for the lead record
        - address: Complete address as a compound field
        - city: City portion of the address
        - company: Company or organization the lead works for
        - converted_account_id: ID of the account created when lead was converted
        - converted_contact_id: ID of the contact created when lead was converted
        - converted_date: Date when the lead was converted
        - converted_opportunity_id: ID of the opportunity created when lead was converted
        - country: Country portion of the address
        - created_by_id: ID of the user who created this lead
        - created_date: Date and time when the lead was created
        - email: Email address of the lead
        - first_name: First name of the lead
        - industry: Industry the lead's company operates in
        - is_converted: Whether the lead has been converted to an account, contact, and opportunity
        - is_deleted: Whether the lead has been moved to the Recycle Bin
        - last_activity_date: Date of the last activity associated with this lead
        - last_modified_by_id: ID of the user who last modified this lead
        - last_modified_date: Date and time when the lead was last modified
        - last_name: Last name of the lead
        - lead_source: Source from which this lead originated
        - mobile_phone: Mobile phone number of the lead
        - name: Full name of the lead (read-only, concatenation of first and last name)
        - number_of_employees: Number of employees at the lead's company
        - owner_id: ID of the user who owns this lead
        - phone: Phone number of the lead
        - postal_code: Postal code portion of the address
        - rating: Rating of the lead (e.g., Hot, Warm, Cold)
        - state: State or province portion of the address
        - status: Current status of the lead in the sales process
        - street: Street address portion of the address
        - title: Job title of the lead
        - website: Website URL for the lead's company
        - system_modstamp: System timestamp when the record was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            LeadsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.Lead`
    :   Get a single lead by ID. Returns all accessible fields by default.
        Use the `fields` parameter to retrieve only specific fields for better performance.
        
        
                Args:
                    id: Salesforce Lead ID (18-character ID starting with '00Q')
                    fields: Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
        Example: "Id,FirstName,LastName,Email,Company,Status,LeadSource"
        
                    **kwargs: Additional parameters
        
                Returns:
                    Lead

    `list(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Lead], LeadsListResultMeta]`
    :   Returns a list of leads via SOQL query. Default returns up to 200 records.
        For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
        
        
                Args:
                    q: SOQL query for leads. Default returns up to 200 records.
        To change the limit, provide your own query with a LIMIT clause.
        Example: "SELECT FIELDS(STANDARD) FROM Lead WHERE Status = 'Open' LIMIT 100"
        
                    **kwargs: Additional parameters
        
                Returns:
                    LeadsListResult

<a id="NotesQuery"></a>

`NotesQuery(connector: SalesforceConnector)`
:   Query class for Notes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[SearchResult]`
    :   Search for notes using SOSL (Salesforce Object Search Language).
        SOSL is optimized for text-based searches across multiple fields.
        
        
                Args:
                    q: SOSL search query. Format: FIND \{searchTerm\} RETURNING Note(fields) [LIMIT n]
        Examples:
        - "FIND \{important\} IN ALL FIELDS RETURNING Note(Id,Title,ParentId)"
        - "FIND \{action items\} IN NAME FIELDS RETURNING Note(Id,Title,Body) LIMIT 50"
        
                    **kwargs: Additional parameters
        
                Returns:
                    NotesApiSearchResult

    `get(self, id: str | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.Note`
    :   Get a single note by ID. Returns all accessible fields by default.
        Use the `fields` parameter to retrieve only specific fields for better performance.
        
        
                Args:
                    id: Salesforce Note ID (18-character ID starting with '002')
                    fields: Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
        Example: "Id,Title,Body,ParentId,OwnerId"
        
                    **kwargs: Additional parameters
        
                Returns:
                    Note

    `list(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Note], NotesListResultMeta]`
    :   Returns a list of notes via SOQL query. Default returns up to 200 records.
        For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
        
        
                Args:
                    q: SOQL query for notes. Default returns up to 200 records.
        To change the limit, provide your own query with a LIMIT clause.
        Example: "SELECT FIELDS(STANDARD) FROM Note WHERE ParentId = '001xx...' LIMIT 50"
        
                    **kwargs: Additional parameters
        
                Returns:
                    NotesListResult

<a id="OpportunitiesQuery"></a>

`OpportunitiesQuery(connector: SalesforceConnector)`
:   Query class for Opportunities entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[SearchResult]`
    :   Search for opportunities using SOSL (Salesforce Object Search Language).
        SOSL is optimized for text-based searches across multiple fields.
        
        
                Args:
                    q: SOSL search query. Format: FIND \{searchTerm\} RETURNING Opportunity(fields) [LIMIT n]
        Examples:
        - "FIND \{Enterprise\} IN NAME FIELDS RETURNING Opportunity(Id,Name,Amount,StageName)"
        - "FIND \{renewal\} IN ALL FIELDS RETURNING Opportunity(Id,Name,CloseDate) LIMIT 25"
        
                    **kwargs: Additional parameters
        
                Returns:
                    OpportunitiesApiSearchResult

    `context_store_search(self, query: OpportunitiesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[OpportunitiesSearchData]`
    :   Search opportunities records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OpportunitiesSearchFilter):
        - id: Unique identifier for the opportunity record
        - account_id: ID of the account associated with this opportunity
        - amount: Estimated total sale amount
        - campaign_id: ID of the campaign that generated this opportunity
        - close_date: Expected close date for the opportunity
        - contact_id: ID of the primary contact for this opportunity
        - created_by_id: ID of the user who created this opportunity
        - created_date: Date and time when the opportunity was created
        - description: Text description of the opportunity
        - expected_revenue: Expected revenue based on amount and probability
        - forecast_category: Forecast category for this opportunity
        - forecast_category_name: Name of the forecast category
        - is_closed: Whether the opportunity is closed
        - is_deleted: Whether the opportunity has been moved to the Recycle Bin
        - is_won: Whether the opportunity was won
        - last_activity_date: Date of the last activity associated with this opportunity
        - last_modified_by_id: ID of the user who last modified this opportunity
        - last_modified_date: Date and time when the opportunity was last modified
        - lead_source: Source from which this opportunity originated
        - name: Name of the opportunity
        - next_step: Description of the next step in closing the opportunity
        - owner_id: ID of the user who owns this opportunity
        - probability: Likelihood of closing the opportunity (percentage)
        - stage_name: Current stage of the opportunity in the sales process
        - type_: Type of opportunity (e.g., New Business, Existing Business)
        - system_modstamp: System timestamp when the record was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OpportunitiesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.Opportunity`
    :   Get a single opportunity by ID. Returns all accessible fields by default.
        Use the `fields` parameter to retrieve only specific fields for better performance.
        
        
                Args:
                    id: Salesforce Opportunity ID (18-character ID starting with '006')
                    fields: Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
        Example: "Id,Name,Amount,StageName,CloseDate,AccountId"
        
                    **kwargs: Additional parameters
        
                Returns:
                    Opportunity

    `list(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Opportunity], OpportunitiesListResultMeta]`
    :   Returns a list of opportunities via SOQL query. Default returns up to 200 records.
        For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
        
        
                Args:
                    q: SOQL query for opportunities. Default returns up to 200 records.
        To change the limit, provide your own query with a LIMIT clause.
        Example: "SELECT FIELDS(STANDARD) FROM Opportunity WHERE StageName = 'Closed Won' LIMIT 50"
        
                    **kwargs: Additional parameters
        
                Returns:
                    OpportunitiesListResult

<a id="QueryQuery"></a>

`QueryQuery(connector: SalesforceConnector)`
:   Query class for Query entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[dict[str, Any]], QueryListResultMeta]`
    :   Execute a custom SOQL query and return results. Use this for querying any Salesforce object.
        For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
        
        
                Args:
                    q: SOQL query string. Include LIMIT clause to control the number of records returned.
        Examples:
        - "SELECT Id, Name FROM Account LIMIT 100"
        - "SELECT FIELDS(STANDARD) FROM Contact WHERE AccountId = '001xx...' LIMIT 50"
        - "SELECT Id, Subject, Status FROM Case WHERE CreatedDate = TODAY"
        
                    **kwargs: Additional parameters
        
                Returns:
                    QueryListResult

<a id="ReportsQuery"></a>

`ReportsQuery(connector: SalesforceConnector)`
:   Query class for Reports entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, id: str | None = None, include_details: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.ReportResults`
    :   Executes a report synchronously and returns the report data results.
        Returns both metadata and the executed data including fact maps, aggregates, and detail rows.
        First use the list action to find available reports, then use this action to run a report and get its data.
        Note: Large reports may be truncated. For reports with more than 2,000 detail rows, consider using async report runs.
        
        
                Args:
                    id: Salesforce Report ID (18-character ID starting with '00O').
        Obtain this ID from the list action.
        
                    include_details: Whether to include detail rows in the report results. Defaults to true.
        Set to false to get only summary/aggregate data.
        
                    **kwargs: Additional parameters
        
                Returns:
                    ReportResults

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[list[Report]]`
    :   Returns a list of reports available in the Salesforce org.
        Each report includes metadata such as Id, Name, Format, Description, and URL.
        This uses the Analytics REST API, not SOQL.
        
        
                Returns:
                    ReportsListResult

<a id="SalesforceConnector"></a>

`SalesforceConnector(auth_config: SalesforceAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, instance_url: str | None = None)`
:   Type-safe Salesforce API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new salesforce connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., SalesforceAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            instance_url: Your Salesforce instance URL (e.g., https://na1.salesforce.com)
    Examples:
        # Local mode (direct API calls)
        connector = SalesforceConnector(auth_config=SalesforceAuthConfig(refresh_token="...", client_id="...", client_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = SalesforceConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = SalesforceConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'SalesforceAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None)`
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
            A SalesforceConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await SalesforceConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=SalesforceAuthConfig(refresh_token="...", client_id="...", client_secret="..."),
            )
        
            # With server-side OAuth:
            connector = await SalesforceConnector.create(
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
            consent_url = await SalesforceConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Salesforce Source",
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @SalesforceConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @SalesforceConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await SalesforceConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            SalesforceCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'api_search', 'download', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="SobjectsQuery"></a>

`SobjectsQuery(connector: SalesforceConnector)`
:   Query class for Sobjects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[list[SObject]]`
    :   Returns a list of all available Salesforce objects (sObjects) in the organization.
        This endpoint is used for health checks to verify authentication and connectivity.
        
        
                Returns:
                    SobjectsListResult

<a id="TasksQuery"></a>

`TasksQuery(connector: SalesforceConnector)`
:   Query class for Tasks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[SearchResult]`
    :   Search for tasks using SOSL (Salesforce Object Search Language).
        SOSL is optimized for text-based searches across multiple fields.
        
        
                Args:
                    q: SOSL search query. Format: FIND \{searchTerm\} RETURNING Task(fields) [LIMIT n]
        Examples:
        - "FIND \{follow up\} IN ALL FIELDS RETURNING Task(Id,Subject,Status,Priority)"
        - "FIND \{call\} IN NAME FIELDS RETURNING Task(Id,Subject,ActivityDate) LIMIT 50"
        
                    **kwargs: Additional parameters
        
                Returns:
                    TasksApiSearchResult

    `context_store_search(self, query: TasksSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[TasksSearchData]`
    :   Search tasks records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TasksSearchFilter):
        - id: Unique identifier for the task record
        - account_id: ID of the account associated with this task
        - activity_date: Due date for the task
        - call_disposition: Result of the call, if this task represents a call
        - call_duration_in_seconds: Duration of the call in seconds
        - call_type: Type of call (Inbound, Outbound, Internal)
        - completed_date_time: Date and time when the task was completed
        - created_by_id: ID of the user who created this task
        - created_date: Date and time when the task was created
        - description: Text description or notes about the task
        - is_closed: Whether the task has been completed
        - is_deleted: Whether the task has been moved to the Recycle Bin
        - is_high_priority: Whether the task is marked as high priority
        - last_modified_by_id: ID of the user who last modified this task
        - last_modified_date: Date and time when the task was last modified
        - owner_id: ID of the user who owns this task
        - priority: Priority level of the task (High, Normal, Low)
        - status: Current status of the task
        - subject: Subject or title of the task
        - task_subtype: Subtype of the task (e.g., Call, Email, Task)
        - type_: Type of task
        - what_id: ID of the related object (Account, Opportunity, etc.)
        - who_id: ID of the related person (Contact or Lead)
        - system_modstamp: System timestamp when the record was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TasksSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.Task`
    :   Get a single task by ID. Returns all accessible fields by default.
        Use the `fields` parameter to retrieve only specific fields for better performance.
        
        
                Args:
                    id: Salesforce Task ID (18-character ID starting with '00T')
                    fields: Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
        Example: "Id,Subject,Status,Priority,ActivityDate,WhoId,WhatId"
        
                    **kwargs: Additional parameters
        
                Returns:
                    Task

    `list(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Task], TasksListResultMeta]`
    :   Returns a list of tasks via SOQL query. Default returns up to 200 records.
        For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
        
        
                Args:
                    q: SOQL query for tasks. Default returns up to 200 records.
        To change the limit, provide your own query with a LIMIT clause.
        Example: "SELECT FIELDS(STANDARD) FROM Task WHERE Status = 'Not Started' LIMIT 100"
        
                    **kwargs: Additional parameters
        
                Returns:
                    TasksListResult