---
id: airbyte_agent_sdk-connectors-zoho_crm-connector
title: airbyte_agent_sdk.connectors.zoho_crm.connector
---

Module airbyte_agent_sdk.connectors.zoho_crm.connector
======================================================
Zoho-Crm connector.

Classes
-------

<a id="AccountsQuery"></a>

`AccountsQuery(connector: ZohoCrmConnector)`
:   Query class for Accounts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AccountsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[AccountsSearchData]`
    :   Search accounts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AccountsSearchFilter):
        - id: Unique record identifier
        - account_name: Name of the account or company
        - account_number: Account number
        - account_type: Type of account (e.g., Analyst, Competitor, Customer)
        - industry: Industry the account belongs to
        - annual_revenue: Annual revenue of the account
        - employees: Number of employees
        - phone: Account phone number
        - website: Account website URL
        - ownership: Ownership type (e.g., Public, Private)
        - rating: Account rating
        - billing_city: Billing address city
        - billing_state: Billing address state or province
        - billing_country: Billing address country
        - description: Description or notes about the account
        - created_time: Time the record was created
        - modified_time: Time the record was last modified
        
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

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single account by ID
        
        Args:
            id: Account ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, page: int | None = None, per_page: int | None = None, page_token: str | None = None, sort_by: str | None = None, sort_order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Account], AccountsListResultMeta]`
    :   Returns a paginated list of accounts
        
        Args:
            page: Page number
            per_page: Number of records per page
            page_token: Page token for fetching beyond 2000 records
            sort_by: Field to sort by
            sort_order: Sort order
            **kwargs: Additional parameters
        
        Returns:
            AccountsListResult

<a id="CallsQuery"></a>

`CallsQuery(connector: ZohoCrmConnector)`
:   Query class for Calls entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CallsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[CallsSearchData]`
    :   Search calls records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CallsSearchFilter):
        - id: Unique record identifier
        - subject: Subject of the call
        - call_type: Type of call (Inbound or Outbound)
        - call_start_time: Start time of the call
        - call_duration: Duration of the call as a formatted string
        - call_duration_in_seconds: Duration of the call in seconds
        - call_purpose: Purpose of the call
        - call_result: Result or outcome of the call
        - caller_id: Caller ID number
        - outgoing_call_status: Status of outgoing calls
        - description: Description or notes about the call
        - created_time: Time the record was created
        - modified_time: Time the record was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CallsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single call by ID
        
        Args:
            id: Call ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, page: int | None = None, per_page: int | None = None, page_token: str | None = None, sort_by: str | None = None, sort_order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Call], CallsListResultMeta]`
    :   Returns a paginated list of calls
        
        Args:
            page: Page number
            per_page: Number of records per page
            page_token: Page token for fetching beyond 2000 records
            sort_by: Field to sort by
            sort_order: Sort order
            **kwargs: Additional parameters
        
        Returns:
            CallsListResult

<a id="CampaignsQuery"></a>

`CampaignsQuery(connector: ZohoCrmConnector)`
:   Query class for Campaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[CampaignsSearchData]`
    :   Search campaigns records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignsSearchFilter):
        - id: Unique record identifier
        - campaign_name: Name of the campaign
        - type_: Type of campaign (e.g., Email, Webinar, Conference)
        - status: Current status of the campaign
        - start_date: Campaign start date
        - end_date: Campaign end date
        - expected_revenue: Expected revenue from the campaign
        - budgeted_cost: Budget allocated for the campaign
        - actual_cost: Actual cost incurred
        - num_sent: Number of campaign messages sent
        - expected_response: Expected response count
        - description: Description or notes about the campaign
        - created_time: Time the record was created
        - modified_time: Time the record was last modified
        
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

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single campaign by ID
        
        Args:
            id: Campaign ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, page: int | None = None, per_page: int | None = None, page_token: str | None = None, sort_by: str | None = None, sort_order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]`
    :   Returns a paginated list of campaigns
        
        Args:
            page: Page number
            per_page: Number of records per page
            page_token: Page token for fetching beyond 2000 records
            sort_by: Field to sort by
            sort_order: Sort order
            **kwargs: Additional parameters
        
        Returns:
            CampaignsListResult

<a id="ContactsQuery"></a>

`ContactsQuery(connector: ZohoCrmConnector)`
:   Query class for Contacts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ContactsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[ContactsSearchData]`
    :   Search contacts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ContactsSearchFilter):
        - id: Unique record identifier
        - first_name: Contact's first name
        - last_name: Contact's last name
        - full_name: Contact's full name
        - email: Contact's email address
        - phone: Contact's phone number
        - mobile: Contact's mobile number
        - title: Contact's job title
        - department: Department the contact belongs to
        - lead_source: Source from which the contact was generated
        - date_of_birth: Contact's date of birth
        - mailing_city: Mailing address city
        - mailing_state: Mailing address state or province
        - mailing_country: Mailing address country
        - description: Description or notes about the contact
        - created_time: Time the record was created
        - modified_time: Time the record was last modified
        
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

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single contact by ID
        
        Args:
            id: Contact ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, page: int | None = None, per_page: int | None = None, page_token: str | None = None, sort_by: str | None = None, sort_order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Contact], ContactsListResultMeta]`
    :   Returns a paginated list of contacts
        
        Args:
            page: Page number
            per_page: Number of records per page
            page_token: Page token for fetching beyond 2000 records
            sort_by: Field to sort by
            sort_order: Sort order
            **kwargs: Additional parameters
        
        Returns:
            ContactsListResult

<a id="DealsQuery"></a>

`DealsQuery(connector: ZohoCrmConnector)`
:   Query class for Deals entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: DealsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[DealsSearchData]`
    :   Search deals records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (DealsSearchFilter):
        - id: Unique record identifier
        - deal_name: Name of the deal
        - amount: Monetary value of the deal
        - stage: Current stage of the deal in the pipeline
        - probability: Probability of closing the deal (percentage)
        - closing_date: Expected closing date
        - type_: Type of deal (e.g., New Business, Existing Business)
        - next_step: Next step in the deal process
        - lead_source: Source from which the deal originated
        - description: Description or notes about the deal
        - created_time: Time the record was created
        - modified_time: Time the record was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            DealsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single deal by ID
        
        Args:
            id: Deal ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, page: int | None = None, per_page: int | None = None, page_token: str | None = None, sort_by: str | None = None, sort_order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Deal], DealsListResultMeta]`
    :   Returns a paginated list of deals
        
        Args:
            page: Page number
            per_page: Number of records per page
            page_token: Page token for fetching beyond 2000 records
            sort_by: Field to sort by
            sort_order: Sort order
            **kwargs: Additional parameters
        
        Returns:
            DealsListResult

<a id="EventsQuery"></a>

`EventsQuery(connector: ZohoCrmConnector)`
:   Query class for Events entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: EventsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[EventsSearchData]`
    :   Search events records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (EventsSearchFilter):
        - id: Unique record identifier
        - event_title: Title of the event
        - start_date_time: Event start date and time
        - end_date_time: Event end date and time
        - all_day: Whether this is an all-day event
        - location: Event location
        - description: Description or notes about the event
        - created_time: Time the record was created
        - modified_time: Time the record was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            EventsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single event by ID
        
        Args:
            id: Event ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, page: int | None = None, per_page: int | None = None, page_token: str | None = None, sort_by: str | None = None, sort_order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Event], EventsListResultMeta]`
    :   Returns a paginated list of events (meetings/calendar events)
        
        Args:
            page: Page number
            per_page: Number of records per page
            page_token: Page token for fetching beyond 2000 records
            sort_by: Field to sort by
            sort_order: Sort order
            **kwargs: Additional parameters
        
        Returns:
            EventsListResult

<a id="InvoicesQuery"></a>

`InvoicesQuery(connector: ZohoCrmConnector)`
:   Query class for Invoices entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: InvoicesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[InvoicesSearchData]`
    :   Search invoices records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (InvoicesSearchFilter):
        - id: Unique record identifier
        - subject: Subject or title of the invoice
        - invoice_number: Invoice number
        - invoice_date: Date the invoice was issued
        - due_date: Payment due date
        - status: Current status of the invoice
        - purchase_order: Associated purchase order number
        - sub_total: Subtotal before tax and adjustments
        - tax: Tax amount
        - adjustment: Adjustment amount
        - grand_total: Total amount including tax and adjustments
        - discount: Discount amount
        - excise_duty: Excise duty amount
        - terms_and_conditions: Terms and conditions text
        - description: Description or notes about the invoice
        - created_time: Time the record was created
        - modified_time: Time the record was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            InvoicesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single invoice by ID
        
        Args:
            id: Invoice ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, page: int | None = None, per_page: int | None = None, page_token: str | None = None, sort_by: str | None = None, sort_order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Invoice], InvoicesListResultMeta]`
    :   Returns a paginated list of invoices
        
        Args:
            page: Page number
            per_page: Number of records per page
            page_token: Page token for fetching beyond 2000 records
            sort_by: Field to sort by
            sort_order: Sort order
            **kwargs: Additional parameters
        
        Returns:
            InvoicesListResult

<a id="LeadsQuery"></a>

`LeadsQuery(connector: ZohoCrmConnector)`
:   Query class for Leads entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: LeadsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[LeadsSearchData]`
    :   Search leads records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (LeadsSearchFilter):
        - id: Unique record identifier
        - first_name: Lead's first name
        - last_name: Lead's last name
        - full_name: Lead's full name
        - email: Lead's email address
        - phone: Lead's phone number
        - mobile: Lead's mobile number
        - company: Company the lead is associated with
        - title: Lead's job title
        - lead_source: Source from which the lead was generated
        - industry: Industry the lead belongs to
        - annual_revenue: Annual revenue of the lead's company
        - no_of_employees: Number of employees in the lead's company
        - rating: Lead rating
        - lead_status: Current status of the lead
        - website: Lead's website URL
        - city: Lead's city
        - state: Lead's state or province
        - country: Lead's country
        - description: Description or notes about the lead
        - created_time: Time the record was created
        - modified_time: Time the record was last modified
        
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

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single lead by ID
        
        Args:
            id: Lead ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, page: int | None = None, per_page: int | None = None, page_token: str | None = None, sort_by: str | None = None, sort_order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Lead], LeadsListResultMeta]`
    :   Returns a paginated list of leads
        
        Args:
            page: Page number
            per_page: Number of records per page
            page_token: Page token for fetching beyond 2000 records
            sort_by: Field to sort by
            sort_order: Sort order
            **kwargs: Additional parameters
        
        Returns:
            LeadsListResult

<a id="ProductsQuery"></a>

`ProductsQuery(connector: ZohoCrmConnector)`
:   Query class for Products entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProductsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[ProductsSearchData]`
    :   Search products records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProductsSearchFilter):
        - id: Unique record identifier
        - product_name: Name of the product
        - product_code: Product code or SKU
        - product_category: Category of the product
        - product_active: Whether the product is active
        - unit_price: Unit price of the product
        - commission_rate: Commission rate for the product
        - manufacturer: Product manufacturer
        - sales_start_date: Date when sales begin
        - sales_end_date: Date when sales end
        - qty_in_stock: Quantity currently in stock
        - qty_in_demand: Quantity in demand
        - qty_ordered: Quantity on order
        - description: Description of the product
        - created_time: Time the record was created
        - modified_time: Time the record was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProductsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single product by ID
        
        Args:
            id: Product ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, page: int | None = None, per_page: int | None = None, page_token: str | None = None, sort_by: str | None = None, sort_order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Product], ProductsListResultMeta]`
    :   Returns a paginated list of products
        
        Args:
            page: Page number
            per_page: Number of records per page
            page_token: Page token for fetching beyond 2000 records
            sort_by: Field to sort by
            sort_order: Sort order
            **kwargs: Additional parameters
        
        Returns:
            ProductsListResult

<a id="QuotesQuery"></a>

`QuotesQuery(connector: ZohoCrmConnector)`
:   Query class for Quotes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: QuotesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[QuotesSearchData]`
    :   Search quotes records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (QuotesSearchFilter):
        - id: Unique record identifier
        - subject: Subject or title of the quote
        - quote_stage: Current stage of the quote
        - valid_till: Date until which the quote is valid
        - carrier: Shipping carrier
        - sub_total: Subtotal before tax and adjustments
        - tax: Tax amount
        - adjustment: Adjustment amount
        - grand_total: Total amount including tax and adjustments
        - discount: Discount amount
        - terms_and_conditions: Terms and conditions text
        - description: Description or notes about the quote
        - created_time: Time the record was created
        - modified_time: Time the record was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            QuotesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single quote by ID
        
        Args:
            id: Quote ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, page: int | None = None, per_page: int | None = None, page_token: str | None = None, sort_by: str | None = None, sort_order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Quote], QuotesListResultMeta]`
    :   Returns a paginated list of quotes
        
        Args:
            page: Page number
            per_page: Number of records per page
            page_token: Page token for fetching beyond 2000 records
            sort_by: Field to sort by
            sort_order: Sort order
            **kwargs: Additional parameters
        
        Returns:
            QuotesListResult

<a id="TasksQuery"></a>

`TasksQuery(connector: ZohoCrmConnector)`
:   Query class for Tasks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TasksSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[TasksSearchData]`
    :   Search tasks records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TasksSearchFilter):
        - id: Unique record identifier
        - subject: Subject or title of the task
        - due_date: Due date for the task
        - status: Current status (e.g., Not Started, In Progress, Completed)
        - priority: Priority level (e.g., High, Highest, Low, Lowest, Normal)
        - send_notification_email: Whether to send a notification email
        - description: Description or notes about the task
        - created_time: Time the record was created
        - modified_time: Time the record was last modified
        - closed_time: Time the task was closed
        
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

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single task by ID
        
        Args:
            id: Task ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, page: int | None = None, per_page: int | None = None, page_token: str | None = None, sort_by: str | None = None, sort_order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Task], TasksListResultMeta]`
    :   Returns a paginated list of tasks
        
        Args:
            page: Page number
            per_page: Number of records per page
            page_token: Page token for fetching beyond 2000 records
            sort_by: Field to sort by
            sort_order: Sort order
            **kwargs: Additional parameters
        
        Returns:
            TasksListResult

<a id="ZohoCrmConnector"></a>

`ZohoCrmConnector(auth_config: ZohoCrmAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, dc_region: str | None = None)`
:   Type-safe Zoho-Crm API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new zoho-crm connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., ZohoCrmAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            dc_region: The Zoho data center region domain suffix: - com (US) - com.au (AU) - eu (EU) - in (IN) - com.cn (CN) - jp (JP)
    
    Examples:
        # Local mode (direct API calls)
        connector = ZohoCrmConnector(auth_config=ZohoCrmAuthConfig(client_id="...", client_secret="...", refresh_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = ZohoCrmConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = ZohoCrmConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'ZohoCrmAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None)`
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
            A ZohoCrmConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await ZohoCrmConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ZohoCrmAuthConfig(client_id="...", client_secret="...", refresh_token="..."),
            )
        
            # With server-side OAuth:
            connector = await ZohoCrmConnector.create(
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
            consent_url = await ZohoCrmConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Zoho-Crm Source",
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @ZohoCrmConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ZohoCrmConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await ZohoCrmConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            ZohoCrmCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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