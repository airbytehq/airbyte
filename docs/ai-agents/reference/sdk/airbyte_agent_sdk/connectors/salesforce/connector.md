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

    `create(self, name: str, account_number: str | None = None, type: str | None = None, industry: str | None = None, phone: str | None = None, website: str | None = None, billing_street: str | None = None, billing_city: str | None = None, billing_state: str | None = None, billing_postal_code: str | None = None, billing_country: str | None = None, annual_revenue: float | None = None, number_of_employees: int | None = None, description: str | None = None, owner_id: str | None = None, parent_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SObjectCreateResponse`
    :   Create an account
        
        Args:
            name: Account name.
            account_number: Parameter AccountNumber
            type: Parameter Type
            industry: Parameter Industry
            phone: Parameter Phone
            website: Parameter Website
            billing_street: Parameter BillingStreet
            billing_city: Parameter BillingCity
            billing_state: Parameter BillingState
            billing_postal_code: Parameter BillingPostalCode
            billing_country: Parameter BillingCountry
            annual_revenue: Parameter AnnualRevenue
            number_of_employees: Parameter NumberOfEmployees
            description: Parameter Description
            owner_id: Parameter OwnerId
            parent_id: Parameter ParentId
            **kwargs: Additional parameters
        
        Returns:
            SObjectCreateResponse

    `delete(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Delete an account
        
        Args:
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
        For "top", "largest", or "highest-value" account requests, rank by a financial account value field
        such as ARR, annual recurring revenue, revenue, annual revenue, amount, or value. ARR is often a
        Salesforce custom field, so prefer the customer's org-specific ARR or account value field when
        available. If no better org-specific field is visible, `AnnualRevenue` is the standard Account
        fallback. Do not use `NumberOfEmployees` unless the user asks for employee count, headcount,
        company size, or largest employer.
        
        
                Args:
                    q: SOQL query for accounts. Default returns up to 200 records.
        To change the limit, provide your own query with a LIMIT clause.
        
        Examples:
          SELECT FIELDS(STANDARD) FROM Account ORDER BY LastModifiedDate DESC LIMIT 50
          SELECT Id, Name, Owner.Name, Owner.Email FROM Account LIMIT 50
          SELECT Id, Name, Parent.Name, Owner.Name FROM Account WHERE Industry = 'Technology' LIMIT 50
          SELECT Id, Name, AnnualRevenue FROM Account ORDER BY AnnualRevenue DESC LIMIT 10
          SELECT Id, Name, NumberOfEmployees FROM Account ORDER BY NumberOfEmployees DESC LIMIT 10
        
        Use dot-path traversal (Owner.Name, Parent.Name) to resolve relationship
        fields inline instead of returning raw IDs.
        
                    **kwargs: Additional parameters
        
                Returns:
                    AccountsListResult

    `update(self, name: str, account_number: str | None = None, type: str | None = None, industry: str | None = None, phone: str | None = None, website: str | None = None, billing_street: str | None = None, billing_city: str | None = None, billing_state: str | None = None, billing_postal_code: str | None = None, billing_country: str | None = None, annual_revenue: float | None = None, number_of_employees: int | None = None, description: str | None = None, owner_id: str | None = None, parent_id: str | None = None, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Update an account
        
        Args:
            name: Account name.
            account_number: Parameter AccountNumber
            type: Parameter Type
            industry: Parameter Industry
            phone: Parameter Phone
            website: Parameter Website
            billing_street: Parameter BillingStreet
            billing_city: Parameter BillingCity
            billing_state: Parameter BillingState
            billing_postal_code: Parameter BillingPostalCode
            billing_country: Parameter BillingCountry
            annual_revenue: Parameter AnnualRevenue
            number_of_employees: Parameter NumberOfEmployees
            description: Parameter Description
            owner_id: Parameter OwnerId
            parent_id: Parameter ParentId
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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

    `download_base64(self, id: str | None = None, range_header: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Downloads the binary file content of an attachment (legacy).
        First use the list or get action to retrieve the Attachment ID and file metadata,
        then use this action to download the actual file content.
        Note: Attachments are a legacy feature; consider using ContentVersion for new implementations.
         and return a JSON-safe base64 chunk.

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

    `download_text(self, id: str | None = None, range_header: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Downloads the binary file content of an attachment (legacy).
        First use the list or get action to retrieve the Attachment ID and file metadata,
        then use this action to download the actual file content.
        Note: Attachments are a legacy feature; consider using ContentVersion for new implementations.
         and return a JSON-safe UTF-8 text chunk.

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

    `create(self, name: str, type: str | None = None, status: str | None = None, start_date: str | None = None, end_date: str | None = None, is_active: bool | None = None, description: str | None = None, expected_revenue: float | None = None, budgeted_cost: float | None = None, actual_cost: float | None = None, expected_response: float | None = None, number_sent: float | None = None, parent_id: str | None = None, owner_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SObjectCreateResponse`
    :   Create a campaign
        
        Args:
            name: Parameter Name
            type: Parameter Type
            status: Parameter Status
            start_date: Parameter StartDate
            end_date: Parameter EndDate
            is_active: Parameter IsActive
            description: Parameter Description
            expected_revenue: Parameter ExpectedRevenue
            budgeted_cost: Parameter BudgetedCost
            actual_cost: Parameter ActualCost
            expected_response: Parameter ExpectedResponse
            number_sent: Parameter NumberSent
            parent_id: Parameter ParentId
            owner_id: Parameter OwnerId
            **kwargs: Additional parameters
        
        Returns:
            SObjectCreateResponse

    `delete(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Delete a campaign
        
        Args:
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
        
        Examples:
          SELECT FIELDS(STANDARD) FROM Campaign WHERE IsActive = true LIMIT 50
          SELECT Id, Name, Type, Status, Owner.Name FROM Campaign LIMIT 50
          SELECT Id, Name, Owner.Name, Owner.Email, StartDate FROM Campaign WHERE IsActive = true LIMIT 50
        
        Use dot-path traversal (Owner.Name) to resolve relationship fields inline
        instead of returning raw IDs.
        
                    **kwargs: Additional parameters
        
                Returns:
                    CampaignsListResult

    `update(self, name: str, type: str | None = None, status: str | None = None, start_date: str | None = None, end_date: str | None = None, is_active: bool | None = None, description: str | None = None, expected_revenue: float | None = None, budgeted_cost: float | None = None, actual_cost: float | None = None, expected_response: float | None = None, number_sent: float | None = None, parent_id: str | None = None, owner_id: str | None = None, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Update a campaign
        
        Args:
            name: Parameter Name
            type: Parameter Type
            status: Parameter Status
            start_date: Parameter StartDate
            end_date: Parameter EndDate
            is_active: Parameter IsActive
            description: Parameter Description
            expected_revenue: Parameter ExpectedRevenue
            budgeted_cost: Parameter BudgetedCost
            actual_cost: Parameter ActualCost
            expected_response: Parameter ExpectedResponse
            number_sent: Parameter NumberSent
            parent_id: Parameter ParentId
            owner_id: Parameter OwnerId
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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

    `create(self, subject: str | None = None, status: str | None = None, priority: str | None = None, origin: str | None = None, type: str | None = None, reason: str | None = None, description: str | None = None, account_id: str | None = None, contact_id: str | None = None, supplied_name: str | None = None, supplied_email: str | None = None, supplied_phone: str | None = None, supplied_company: str | None = None, owner_id: str | None = None, parent_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SObjectCreateResponse`
    :   Create a case
        
        Args:
            subject: Parameter Subject
            status: Parameter Status
            priority: Parameter Priority
            origin: Parameter Origin
            type: Parameter Type
            reason: Parameter Reason
            description: Parameter Description
            account_id: Parameter AccountId
            contact_id: Parameter ContactId
            supplied_name: Parameter SuppliedName
            supplied_email: Parameter SuppliedEmail
            supplied_phone: Parameter SuppliedPhone
            supplied_company: Parameter SuppliedCompany
            owner_id: Parameter OwnerId
            parent_id: Parameter ParentId
            **kwargs: Additional parameters
        
        Returns:
            SObjectCreateResponse

    `delete(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Delete a case
        
        Args:
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
        
        Examples:
          SELECT FIELDS(STANDARD) FROM Case WHERE Status = 'New' LIMIT 100
          SELECT Id, CaseNumber, Subject, Account.Name, Owner.Name, Contact.Name FROM Case LIMIT 50
          SELECT Id, CaseNumber, Subject, Status, Account.Name, Owner.Name FROM Case WHERE Status = 'Escalated' LIMIT 50
        
        Use dot-path traversal (Account.Name, Owner.Name, Contact.Name) to resolve
        relationship fields inline instead of returning raw IDs.
        
                    **kwargs: Additional parameters
        
                Returns:
                    CasesListResult

    `update(self, subject: str | None = None, status: str | None = None, priority: str | None = None, origin: str | None = None, type: str | None = None, reason: str | None = None, description: str | None = None, account_id: str | None = None, contact_id: str | None = None, supplied_name: str | None = None, supplied_email: str | None = None, supplied_phone: str | None = None, supplied_company: str | None = None, owner_id: str | None = None, parent_id: str | None = None, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Update a case
        
        Args:
            subject: Parameter Subject
            status: Parameter Status
            priority: Parameter Priority
            origin: Parameter Origin
            type: Parameter Type
            reason: Parameter Reason
            description: Parameter Description
            account_id: Parameter AccountId
            contact_id: Parameter ContactId
            supplied_name: Parameter SuppliedName
            supplied_email: Parameter SuppliedEmail
            supplied_phone: Parameter SuppliedPhone
            supplied_company: Parameter SuppliedCompany
            owner_id: Parameter OwnerId
            parent_id: Parameter ParentId
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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

    `create(self, last_name: str, first_name: str | None = None, email: str | None = None, phone: str | None = None, mobile_phone: str | None = None, title: str | None = None, department: str | None = None, account_id: str | None = None, mailing_street: str | None = None, mailing_city: str | None = None, mailing_state: str | None = None, mailing_postal_code: str | None = None, mailing_country: str | None = None, description: str | None = None, owner_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SObjectCreateResponse`
    :   Create a contact
        
        Args:
            first_name: Parameter FirstName
            last_name: Parameter LastName
            email: Parameter Email
            phone: Parameter Phone
            mobile_phone: Parameter MobilePhone
            title: Parameter Title
            department: Parameter Department
            account_id: Parameter AccountId
            mailing_street: Parameter MailingStreet
            mailing_city: Parameter MailingCity
            mailing_state: Parameter MailingState
            mailing_postal_code: Parameter MailingPostalCode
            mailing_country: Parameter MailingCountry
            description: Parameter Description
            owner_id: Parameter OwnerId
            **kwargs: Additional parameters
        
        Returns:
            SObjectCreateResponse

    `delete(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Delete a contact
        
        Args:
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
        
        Examples:
          SELECT FIELDS(STANDARD) FROM Contact WHERE AccountId = '001xx...' LIMIT 50
          SELECT Id, FirstName, LastName, Account.Name, Owner.Name FROM Contact LIMIT 50
          SELECT Id, Name, Email, Account.Name, ReportsTo.Name FROM Contact WHERE AccountId != null LIMIT 50
        
        Use dot-path traversal (Account.Name, Owner.Name, ReportsTo.Name) to resolve
        relationship fields inline instead of returning raw IDs.
        
                    **kwargs: Additional parameters
        
                Returns:
                    ContactsListResult

    `update(self, last_name: str, first_name: str | None = None, email: str | None = None, phone: str | None = None, mobile_phone: str | None = None, title: str | None = None, department: str | None = None, account_id: str | None = None, mailing_street: str | None = None, mailing_city: str | None = None, mailing_state: str | None = None, mailing_postal_code: str | None = None, mailing_country: str | None = None, description: str | None = None, owner_id: str | None = None, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Update a contact
        
        Args:
            first_name: Parameter FirstName
            last_name: Parameter LastName
            email: Parameter Email
            phone: Parameter Phone
            mobile_phone: Parameter MobilePhone
            title: Parameter Title
            department: Parameter Department
            account_id: Parameter AccountId
            mailing_street: Parameter MailingStreet
            mailing_city: Parameter MailingCity
            mailing_state: Parameter MailingState
            mailing_postal_code: Parameter MailingPostalCode
            mailing_country: Parameter MailingCountry
            description: Parameter Description
            owner_id: Parameter OwnerId
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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

    `download_base64(self, id: str | None = None, range_header: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Downloads the binary file content of a content version.
        First use the list or get action to retrieve the ContentVersion ID and file metadata (size, type, etc.),
        then use this action to download the actual file content.
        The response is the raw binary file data.
         and return a JSON-safe base64 chunk.

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

    `download_text(self, id: str | None = None, range_header: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Downloads the binary file content of a content version.
        First use the list or get action to retrieve the ContentVersion ID and file metadata (size, type, etc.),
        then use this action to download the actual file content.
        The response is the raw binary file data.
         and return a JSON-safe UTF-8 text chunk.

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

    `create(self, subject: str, start_date_time: str, duration_in_minutes: int, end_date_time: str | None = None, location: str | None = None, description: str | None = None, who_id: str | None = None, what_id: str | None = None, is_all_day_event: bool | None = None, show_as: str | None = None, owner_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SObjectCreateResponse`
    :   Create an event
        
        Args:
            subject: Parameter Subject
            start_date_time: Parameter StartDateTime
            end_date_time: Parameter EndDateTime
            duration_in_minutes: Parameter DurationInMinutes
            location: Parameter Location
            description: Parameter Description
            who_id: Parameter WhoId
            what_id: Parameter WhatId
            is_all_day_event: Parameter IsAllDayEvent
            show_as: Parameter ShowAs
            owner_id: Parameter OwnerId
            **kwargs: Additional parameters
        
        Returns:
            SObjectCreateResponse

    `delete(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Delete an event
        
        Args:
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
        
        Examples:
          SELECT FIELDS(STANDARD) FROM Event WHERE StartDateTime > TODAY LIMIT 50
          SELECT Id, Subject, StartDateTime, Owner.Name, Account.Name FROM Event LIMIT 50
          SELECT Id, Subject, StartDateTime, Owner.Name, Who.Name, What.Name FROM Event WHERE StartDateTime = THIS_WEEK LIMIT 50
        
        Use dot-path traversal (Owner.Name, Account.Name) to resolve relationship
        fields inline instead of returning raw IDs. Who.Name and What.Name resolve
        polymorphic WhoId/WhatId references to the related record's name.
        
                    **kwargs: Additional parameters
        
                Returns:
                    EventsListResult

    `update(self, subject: str, start_date_time: str, duration_in_minutes: int, end_date_time: str | None = None, location: str | None = None, description: str | None = None, who_id: str | None = None, what_id: str | None = None, is_all_day_event: bool | None = None, show_as: str | None = None, owner_id: str | None = None, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Update an event
        
        Args:
            subject: Parameter Subject
            start_date_time: Parameter StartDateTime
            end_date_time: Parameter EndDateTime
            duration_in_minutes: Parameter DurationInMinutes
            location: Parameter Location
            description: Parameter Description
            who_id: Parameter WhoId
            what_id: Parameter WhatId
            is_all_day_event: Parameter IsAllDayEvent
            show_as: Parameter ShowAs
            owner_id: Parameter OwnerId
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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

    `create(self, last_name: str, company: str, first_name: str | None = None, title: str | None = None, email: str | None = None, phone: str | None = None, mobile_phone: str | None = None, website: str | None = None, status: str | None = None, lead_source: str | None = None, industry: str | None = None, rating: str | None = None, annual_revenue: float | None = None, number_of_employees: int | None = None, street: str | None = None, city: str | None = None, state: str | None = None, postal_code: str | None = None, country: str | None = None, description: str | None = None, owner_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SObjectCreateResponse`
    :   Create a lead
        
        Args:
            first_name: Parameter FirstName
            last_name: Parameter LastName
            company: Parameter Company
            title: Parameter Title
            email: Parameter Email
            phone: Parameter Phone
            mobile_phone: Parameter MobilePhone
            website: Parameter Website
            status: Parameter Status
            lead_source: Parameter LeadSource
            industry: Parameter Industry
            rating: Parameter Rating
            annual_revenue: Parameter AnnualRevenue
            number_of_employees: Parameter NumberOfEmployees
            street: Parameter Street
            city: Parameter City
            state: Parameter State
            postal_code: Parameter PostalCode
            country: Parameter Country
            description: Parameter Description
            owner_id: Parameter OwnerId
            **kwargs: Additional parameters
        
        Returns:
            SObjectCreateResponse

    `delete(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Delete a lead
        
        Args:
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
        
        Examples:
          SELECT FIELDS(STANDARD) FROM Lead WHERE Status = 'Open' LIMIT 100
          SELECT Id, Name, Company, Owner.Name FROM Lead LIMIT 50
          SELECT Id, Name, Owner.Name, ConvertedAccount.Name, ConvertedContact.Name, ConvertedOpportunity.Name FROM Lead WHERE IsConverted = true LIMIT 50
        
        Use dot-path traversal (Owner.Name, ConvertedAccount.Name, ConvertedContact.Name,
        ConvertedOpportunity.Name) to resolve relationship fields inline instead of returning raw IDs.
        
                    **kwargs: Additional parameters
        
                Returns:
                    LeadsListResult

    `update(self, last_name: str, company: str, first_name: str | None = None, title: str | None = None, email: str | None = None, phone: str | None = None, mobile_phone: str | None = None, website: str | None = None, status: str | None = None, lead_source: str | None = None, industry: str | None = None, rating: str | None = None, annual_revenue: float | None = None, number_of_employees: int | None = None, street: str | None = None, city: str | None = None, state: str | None = None, postal_code: str | None = None, country: str | None = None, description: str | None = None, owner_id: str | None = None, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Update a lead
        
        Args:
            first_name: Parameter FirstName
            last_name: Parameter LastName
            company: Parameter Company
            title: Parameter Title
            email: Parameter Email
            phone: Parameter Phone
            mobile_phone: Parameter MobilePhone
            website: Parameter Website
            status: Parameter Status
            lead_source: Parameter LeadSource
            industry: Parameter Industry
            rating: Parameter Rating
            annual_revenue: Parameter AnnualRevenue
            number_of_employees: Parameter NumberOfEmployees
            street: Parameter Street
            city: Parameter City
            state: Parameter State
            postal_code: Parameter PostalCode
            country: Parameter Country
            description: Parameter Description
            owner_id: Parameter OwnerId
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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

    `create(self, title: str, parent_id: str, body: str | None = None, is_private: bool | None = None, owner_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SObjectCreateResponse`
    :   Create a classic Salesforce Note attached to a parent record (Account, Contact,
        Lead, Opportunity, Case, custom object, etc.). `Title` and `ParentId` are required.
        
        
                Args:
                    title: Note title, up to 80 characters.
                    body: Note body content (up to ~32,000 characters).
                    parent_id: Id of the parent record this note is attached to (Account, Contact, Lead, Opportunity, Case, custom object, etc.).
                    is_private: When true, the note is visible only to its owner and admins.
                    owner_id: Parameter OwnerId
                    **kwargs: Additional parameters
        
                Returns:
                    SObjectCreateResponse

    `delete(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Delete a note
        
        Args:
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
        
        Examples:
          SELECT FIELDS(STANDARD) FROM Note WHERE ParentId = '001xx...' LIMIT 50
          SELECT Id, Title, Body, Owner.Name FROM Note LIMIT 50
          SELECT Id, Title, Owner.Name, CreatedDate FROM Note ORDER BY CreatedDate DESC LIMIT 50
        
        Use dot-path traversal (Owner.Name) to resolve relationship fields inline
        instead of returning raw IDs.
        
                    **kwargs: Additional parameters
        
                Returns:
                    NotesListResult

    `update(self, title: str | None = None, body: str | None = None, is_private: bool | None = None, owner_id: str | None = None, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Update a note
        
        Args:
            title: Note title, up to 80 characters.
            body: Note body content (up to ~32,000 characters).
            is_private: When true, the note is visible only to its owner and admins.
            owner_id: Parameter OwnerId
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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

    `create(self, name: str, stage_name: str, close_date: str, account_id: str | None = None, amount: float | None = None, probability: float | None = None, type: str | None = None, lead_source: str | None = None, next_step: str | None = None, campaign_id: str | None = None, forecast_category_name: str | None = None, description: str | None = None, owner_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SObjectCreateResponse`
    :   Create an opportunity
        
        Args:
            name: Parameter Name
            account_id: Parameter AccountId
            stage_name: Opportunity stage (e.g., Prospecting, Qualification, Closed Won).
            close_date: Parameter CloseDate
            amount: Parameter Amount
            probability: Parameter Probability
            type: Parameter Type
            lead_source: Parameter LeadSource
            next_step: Parameter NextStep
            campaign_id: Parameter CampaignId
            forecast_category_name: Parameter ForecastCategoryName
            description: Parameter Description
            owner_id: Parameter OwnerId
            **kwargs: Additional parameters
        
        Returns:
            SObjectCreateResponse

    `delete(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Delete an opportunity
        
        Args:
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
        For "top", "largest", or "highest-value" opportunity requests, first choose a
        visible financial opportunity field. Standard candidates include `Amount` for
        total deal value and `ExpectedRevenue` for expected, weighted, or forecast revenue.
        
        
                Args:
                    q: SOQL query for opportunities. Default returns up to 200 records.
        To change the limit, provide your own query with a LIMIT clause.
        
        Examples:
          SELECT FIELDS(STANDARD) FROM Opportunity WHERE StageName = 'Closed Won' LIMIT 50
          SELECT Id, Name, Amount, Account.Name, Owner.Name FROM Opportunity LIMIT 50
          SELECT Id, Name, Amount, StageName, Account.Name FROM Opportunity ORDER BY Amount DESC LIMIT 10
          SELECT Id, Name, ExpectedRevenue, Probability, Amount FROM Opportunity ORDER BY ExpectedRevenue DESC LIMIT 10
          SELECT Id, Name, StageName, Account.Name, Account.Industry, Owner.Name, Campaign.Name FROM Opportunity WHERE CloseDate = THIS_QUARTER LIMIT 50
        
        Use dot-path traversal (Account.Name, Owner.Name, Campaign.Name) to resolve
        relationship fields inline instead of returning raw IDs.
        
                    **kwargs: Additional parameters
        
                Returns:
                    OpportunitiesListResult

    `update(self, name: str, stage_name: str, close_date: str, account_id: str | None = None, amount: float | None = None, probability: float | None = None, type: str | None = None, lead_source: str | None = None, next_step: str | None = None, campaign_id: str | None = None, forecast_category_name: str | None = None, description: str | None = None, owner_id: str | None = None, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Update an opportunity
        
        Args:
            name: Parameter Name
            account_id: Parameter AccountId
            stage_name: Opportunity stage (e.g., Prospecting, Qualification, Closed Won).
            close_date: Parameter CloseDate
            amount: Parameter Amount
            probability: Parameter Probability
            type: Parameter Type
            lead_source: Parameter LeadSource
            next_step: Parameter NextStep
            campaign_id: Parameter CampaignId
            forecast_category_name: Parameter ForecastCategoryName
            description: Parameter Description
            owner_id: Parameter OwnerId
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

<a id="OpportunityStagesQuery"></a>

`OpportunityStagesQuery(connector: SalesforceConnector)`
:   Query class for OpportunityStages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OpportunityStagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[OpportunityStagesSearchData]`
    :   Search opportunity_stages records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OpportunityStagesSearchFilter):
        - id: Unique identifier for the opportunity stage record
        - api_name: API name of the stage used in code and integrations
        - created_by_id: ID of the user who created this stage
        - created_date: Date and time when the stage was created
        - default_probability: Default probability percentage for opportunities at this stage
        - description: Description of the stage
        - forecast_category: Forecast category for opportunities at this stage
        - forecast_category_name: Display name of the forecast category
        - is_active: Whether the stage is currently active and can be used
        - is_closed: Whether opportunities at this stage are considered closed
        - is_won: Whether opportunities at this stage are considered won
        - last_modified_by_id: ID of the user who last modified this stage
        - last_modified_date: Date and time when the stage was last modified
        - master_label: Display label for the stage
        - sort_order: Order in which the stage appears in the sales process
        - system_modstamp: System timestamp when the record was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OpportunityStagesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.OpportunityStage`
    :   Get a single opportunity stage by ID. Returns all accessible fields by default.
        Use the `fields` parameter to retrieve only specific fields for better performance.
        
        
                Args:
                    id: Salesforce OpportunityStage ID
                    fields: Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
        Example: "Id,MasterLabel,ApiName,DefaultProbability,IsClosed,IsWon,IsActive"
        
                    **kwargs: Additional parameters
        
                Returns:
                    OpportunityStage

    `list(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[OpportunityStage], OpportunityStagesListResultMeta]`
    :   Returns a list of opportunity stages via SOQL query. Default returns all stages.
        OpportunityStage defines the sales process stages that opportunities move through.
        
        
                Args:
                    q: SOQL query for opportunity stages. Default returns all stages.
        
        Examples:
          SELECT FIELDS(STANDARD) FROM OpportunityStage ORDER BY SortOrder ASC
          SELECT Id, MasterLabel, ApiName, DefaultProbability, IsClosed, IsWon, IsActive, ForecastCategoryName FROM OpportunityStage WHERE IsActive = true ORDER BY SortOrder ASC
          SELECT Id, MasterLabel, DefaultProbability, CreatedBy.Name FROM OpportunityStage ORDER BY SortOrder ASC
        
        Use dot-path traversal (CreatedBy.Name, LastModifiedBy.Name) to resolve
        relationship fields inline instead of returning raw IDs.
        
                    **kwargs: Additional parameters
        
                Returns:
                    OpportunityStagesListResult

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
        - "SELECT Id, Name, Account.Name, Owner.Name FROM Opportunity LIMIT 50"
        
        Use dot-path traversal (e.g. Owner.Name, Account.Name) to resolve relationship
        fields inline instead of returning raw IDs.
        
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
            connector = SalesforceConnector(...)
        
            @SalesforceConnector.agent_tool()
            async def execute(entity: str, action: str, params: dict | None = None):
                return await connector.execute(entity=entity, action=action, params=params or \{\})
        
            @SalesforceConnector.agent_tool()
            async def inspect_connector():
                return await connector.inspect_connector()
        
            @SalesforceConnector.agent_tool()
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
        
        connector = SalesforceConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @SalesforceConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @SalesforceConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @SalesforceConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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

    `execute(self, entity: str, action: "Literal['list', 'create', 'get', 'update', 'delete', 'api_search', 'download', 'context_store_search']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
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

<a id="SobjectsQuery"></a>

`SobjectsQuery(connector: SalesforceConnector)`
:   Query class for Sobjects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, sobject_type: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Create a record for any Salesforce SObject by name. Works for standard
        objects (Account, Contact, ...) and custom objects (e.g. `MyObject__c`).
        Pass the SObject's API name in the `sobjectType` path parameter and the
        field values as a free-form JSON body.
        
        
                Args:
                    sobject_type: SObject API name (e.g., `Account`, `MyCustomObject__c`).
                    **kwargs: Additional parameters
        
                Returns:
                    dict[str, Any]

    `delete(self, sobject_type: str, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Delete a record by id. Salesforce moves the record to the Recycle Bin
        (15-day retention) for most objects.
        
        
                Args:
                    sobject_type: SObject API name.
                    id: Salesforce record Id.
                    **kwargs: Additional parameters
        
                Returns:
                    dict[str, Any]

    `get(self, sobject_type: str, id: str | None = None, fields: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Fetch a single record from any SObject by id. Works for standard and
        custom objects.
        
        
                Args:
                    sobject_type: SObject API name.
                    id: Salesforce record Id.
                    fields: Comma-separated field names to return. Omit for default fields.
                    **kwargs: Additional parameters
        
                Returns:
                    dict[str, Any]

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[list[SObject]]`
    :   Returns a list of all available Salesforce objects (sObjects) in the organization.
        This endpoint is used for health checks to verify authentication and connectivity.
        
        
                Returns:
                    SobjectsListResult

    `update(self, sobject_type: str, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Update fields on an existing record. Pass only the fields you want to
        change in the JSON body; Salesforce leaves the rest untouched.
        
        
                Args:
                    sobject_type: SObject API name.
                    id: Salesforce record Id.
                    **kwargs: Additional parameters
        
                Returns:
                    dict[str, Any]

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

    `create(self, subject: str, status: str | None = None, priority: str | None = None, activity_date: str | None = None, who_id: str | None = None, what_id: str | None = None, description: str | None = None, type: str | None = None, is_reminder_set: bool | None = None, reminder_date_time: str | None = None, owner_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SObjectCreateResponse`
    :   Create a task
        
        Args:
            subject: Parameter Subject
            status: Task status (e.g., Not Started, In Progress, Completed).
            priority: Parameter Priority
            activity_date: Parameter ActivityDate
            who_id: Related contact or lead Id.
            what_id: Related Account, Opportunity, or other object Id.
            description: Parameter Description
            type: Parameter Type
            is_reminder_set: Parameter IsReminderSet
            reminder_date_time: Parameter ReminderDateTime
            owner_id: Parameter OwnerId
            **kwargs: Additional parameters
        
        Returns:
            SObjectCreateResponse

    `delete(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Delete a task
        
        Args:
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

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
        
        Examples:
          SELECT FIELDS(STANDARD) FROM Task WHERE Status = 'Not Started' LIMIT 100
          SELECT Id, Subject, Status, Owner.Name, Account.Name FROM Task LIMIT 50
          SELECT Id, Subject, Status, Owner.Name, Who.Name, What.Name FROM Task WHERE ActivityDate = THIS_WEEK LIMIT 50
        
        Use dot-path traversal (Owner.Name, Account.Name) to resolve relationship
        fields inline instead of returning raw IDs. Who.Name and What.Name resolve
        polymorphic WhoId/WhatId references to the related record's name.
        
                    **kwargs: Additional parameters
        
                Returns:
                    TasksListResult

    `update(self, subject: str, status: str | None = None, priority: str | None = None, activity_date: str | None = None, who_id: str | None = None, what_id: str | None = None, description: str | None = None, type: str | None = None, is_reminder_set: bool | None = None, reminder_date_time: str | None = None, owner_id: str | None = None, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Update a task
        
        Args:
            subject: Parameter Subject
            status: Task status (e.g., Not Started, In Progress, Completed).
            priority: Parameter Priority
            activity_date: Parameter ActivityDate
            who_id: Related contact or lead Id.
            what_id: Related Account, Opportunity, or other object Id.
            description: Parameter Description
            type: Parameter Type
            is_reminder_set: Parameter IsReminderSet
            reminder_date_time: Parameter ReminderDateTime
            owner_id: Parameter OwnerId
            id: Parameter id
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

<a id="UsersQuery"></a>

`UsersQuery(connector: SalesforceConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - id: Unique identifier for the user record
        - account_id: ID of the account associated with this user (for portal users)
        - alias: Short name used to identify the user in list views and reports
        - city: City portion of the user's address
        - company_name: Name of the user's company
        - contact_id: ID of the contact associated with this user (for portal users)
        - country: Country portion of the user's address
        - created_by_id: ID of the user who created this user record
        - created_date: Date and time when the user was created
        - department: Department within the organization
        - division: Division within the organization
        - email: Email address of the user
        - employee_number: Employee number or ID assigned by the organization
        - first_name: First name of the user
        - is_active: Whether the user is active and can log in
        - last_login_date: Date and time of the user's most recent login
        - last_modified_by_id: ID of the user who last modified this user record
        - last_modified_date: Date and time when the user was last modified
        - last_name: Last name of the user
        - manager_id: ID of the user's manager
        - mobile_phone: Mobile phone number of the user
        - name: Full name of the user
        - phone: Business phone number of the user
        - postal_code: Postal code portion of the user's address
        - profile_id: ID of the user's profile
        - state: State or province portion of the user's address
        - street: Street address of the user
        - title: Job title of the user
        - user_role_id: ID of the user's role in the organization
        - user_type: Type of user license (e.g., Standard, PowerPartner)
        - username: Username for logging into Salesforce (unique across all orgs)
        - system_modstamp: System timestamp when the record was last modified
        
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

    `create(self, username: str, last_name: str, email: str, alias: str, profile_id: str, time_zone_sid_key: str, locale_sid_key: str, email_encoding_key: str, language_locale_key: str, first_name: str | None = None, user_role_id: str | None = None, manager_id: str | None = None, is_active: bool | None = None, title: str | None = None, department: str | None = None, phone: str | None = None, mobile_phone: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SObjectCreateResponse`
    :   Create a Salesforce User. Consumes a paid user-license seat. Requires the
        "Manage Internal Users" permission on the running OAuth identity.
        
        
                Args:
                    username: Login name (email-format, must be unique across all Salesforce orgs).
                    first_name: Parameter FirstName
                    last_name: Parameter LastName
                    email: Parameter Email
                    alias: 1-8 character alias.
                    profile_id: Salesforce profile that determines the user's base permissions.
                    user_role_id: Parameter UserRoleId
                    manager_id: Parameter ManagerId
                    time_zone_sid_key: e.g., "America/Los_Angeles".
                    locale_sid_key: e.g., "en_US".
                    email_encoding_key: e.g., "UTF-8".
                    language_locale_key: e.g., "en_US".
                    is_active: Set to false to deactivate the user (Salesforce does not support delete).
                    title: Parameter Title
                    department: Parameter Department
                    phone: Parameter Phone
                    mobile_phone: Parameter MobilePhone
                    **kwargs: Additional parameters
        
                Returns:
                    SObjectCreateResponse

    `get(self, id: str | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.User`
    :   Get a single user by ID. Returns all accessible fields by default.
        Use the `fields` parameter to retrieve only specific fields for better performance.
        
        
                Args:
                    id: Salesforce User ID (18-character ID starting with '005')
                    fields: Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
        Example: "Id,Name,Email,Username,IsActive,ProfileId,UserRoleId"
        
                    **kwargs: Additional parameters
        
                Returns:
                    User

    `list(self, q: str, **kwargs) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[User], UsersListResultMeta]`
    :   Returns a list of users via SOQL query. Default returns up to 200 records.
        For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
        
        
                Args:
                    q: SOQL query for users. Default returns up to 200 records.
        To change the limit, provide your own query with a LIMIT clause.
        
        Examples:
          SELECT FIELDS(STANDARD) FROM User WHERE IsActive = true ORDER BY LastModifiedDate DESC LIMIT 50
          SELECT Id, Name, Email, Manager.Name, Profile.Name FROM User WHERE IsActive = true LIMIT 50
          SELECT Id, Name, Email, Department, UserRole.Name FROM User LIMIT 50
        
        Use dot-path traversal (Manager.Name, Profile.Name, UserRole.Name) to resolve
        relationship fields inline instead of returning raw IDs.
        
                    **kwargs: Additional parameters
        
                Returns:
                    UsersListResult

    `update(self, username: str | None = None, first_name: str | None = None, last_name: str | None = None, email: str | None = None, alias: str | None = None, profile_id: str | None = None, user_role_id: str | None = None, manager_id: str | None = None, time_zone_sid_key: str | None = None, locale_sid_key: str | None = None, email_encoding_key: str | None = None, language_locale_key: str | None = None, is_active: bool | None = None, title: str | None = None, department: str | None = None, phone: str | None = None, mobile_phone: str | None = None, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Update a Salesforce User. To deactivate a user (Salesforce does not allow
        delete), send `{ "IsActive": false }`.
        
        
                Args:
                    username: Login name (email-format, must be unique across all Salesforce orgs).
                    first_name: Parameter FirstName
                    last_name: Parameter LastName
                    email: Parameter Email
                    alias: 1-8 character alias.
                    profile_id: Salesforce profile that determines the user's base permissions.
                    user_role_id: Parameter UserRoleId
                    manager_id: Parameter ManagerId
                    time_zone_sid_key: e.g., "America/Los_Angeles".
                    locale_sid_key: e.g., "en_US".
                    email_encoding_key: e.g., "UTF-8".
                    language_locale_key: e.g., "en_US".
                    is_active: Set to false to deactivate the user (Salesforce does not support delete).
                    title: Parameter Title
                    department: Parameter Department
                    phone: Parameter Phone
                    mobile_phone: Parameter MobilePhone
                    id: Parameter id
                    **kwargs: Additional parameters
        
                Returns:
                    dict[str, Any]