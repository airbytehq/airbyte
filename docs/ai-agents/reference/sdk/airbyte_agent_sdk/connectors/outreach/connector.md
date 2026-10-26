---
id: airbyte_agent_sdk-connectors-outreach-connector
title: airbyte_agent_sdk.connectors.outreach.connector
---

Module airbyte_agent_sdk.connectors.outreach.connector
======================================================
Outreach connector.

Classes
-------

<a id="AccountsQuery"></a>

`AccountsQuery(connector: OutreachConnector)`
:   Query class for Accounts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AccountsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[AccountsSearchData]`
    :   Search accounts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AccountsSearchFilter):
        - assigned_teams: Assigned teams
        - assigned_users: Assigned users
        - batches: Batches
        - buyer_intent_score: Buyer intent score
        - company_type: Company type
        - created_at: Created at
        - creator: Creator
        - custom1: Custom field 1
        - custom10: Custom field 10
        - custom100: Custom field 100
        - custom101: Custom field 101
        - custom102: Custom field 102
        - custom103: Custom field 103
        - custom104: Custom field 104
        - custom105: Custom field 105
        - custom106: Custom field 106
        - custom107: Custom field 107
        - custom108: Custom field 108
        - custom109: Custom field 109
        - custom11: Custom field 11
        - custom110: Custom field 110
        - custom111: Custom field 111
        - custom112: Custom field 112
        - custom113: Custom field 113
        - custom114: Custom field 114
        - custom115: Custom field 115
        - custom116: Custom field 116
        - custom117: Custom field 117
        - custom118: Custom field 118
        - custom119: Custom field 119
        - custom12: Custom field 12
        - custom120: Custom field 120
        - custom121: Custom field 121
        - custom122: Custom field 122
        - custom123: Custom field 123
        - custom124: Custom field 124
        - custom125: Custom field 125
        - custom126: Custom field 126
        - custom127: Custom field 127
        - custom128: Custom field 128
        - custom129: Custom field 129
        - custom13: Custom field 13
        - custom130: Custom field 130
        - custom131: Custom field 131
        - custom132: Custom field 132
        - custom133: Custom field 133
        - custom134: Custom field 134
        - custom135: Custom field 135
        - custom136: Custom field 136
        - custom137: Custom field 137
        - custom138: Custom field 138
        - custom139: Custom field 139
        - custom14: Custom field 14
        - custom140: Custom field 140
        - custom141: Custom field 141
        - custom142: Custom field 142
        - custom143: Custom field 143
        - custom144: Custom field 144
        - custom145: Custom field 145
        - custom146: Custom field 146
        - custom147: Custom field 147
        - custom148: Custom field 148
        - custom149: Custom field 149
        - custom15: Custom field 15
        - custom150: Custom field 150
        - custom16: Custom field 16
        - custom17: Custom field 17
        - custom18: Custom field 18
        - custom19: Custom field 19
        - custom2: Custom field 2
        - custom20: Custom field 20
        - custom21: Custom field 21
        - custom22: Custom field 22
        - custom23: Custom field 23
        - custom24: Custom field 24
        - custom25: Custom field 25
        - custom26: Custom field 26
        - custom27: Custom field 27
        - custom28: Custom field 28
        - custom29: Custom field 29
        - custom3: Custom field 3
        - custom30: Custom field 30
        - custom31: Custom field 31
        - custom32: Custom field 32
        - custom33: Custom field 33
        - custom34: Custom field 34
        - custom35: Custom field 35
        - custom36: Custom field 36
        - custom37: Custom field 37
        - custom38: Custom field 38
        - custom39: Custom field 39
        - custom4: Custom field 4
        - custom40: Custom field 40
        - custom41: Custom field 41
        - custom42: Custom field 42
        - custom43: Custom field 43
        - custom44: Custom field 44
        - custom45: Custom field 45
        - custom46: Custom field 46
        - custom47: Custom field 47
        - custom48: Custom field 48
        - custom49: Custom field 49
        - custom5: Custom field 5
        - custom50: Custom field 50
        - custom51: Custom field 51
        - custom52: Custom field 52
        - custom53: Custom field 53
        - custom54: Custom field 54
        - custom55: Custom field 55
        - custom56: Custom field 56
        - custom57: Custom field 57
        - custom58: Custom field 58
        - custom59: Custom field 59
        - custom6: Custom field 6
        - custom60: Custom field 60
        - custom61: Custom field 61
        - custom62: Custom field 62
        - custom63: Custom field 63
        - custom64: Custom field 64
        - custom65: Custom field 65
        - custom66: Custom field 66
        - custom67: Custom field 67
        - custom68: Custom field 68
        - custom69: Custom field 69
        - custom7: Custom field 7
        - custom70: Custom field 70
        - custom71: Custom field 71
        - custom72: Custom field 72
        - custom73: Custom field 73
        - custom74: Custom field 74
        - custom75: Custom field 75
        - custom76: Custom field 76
        - custom77: Custom field 77
        - custom78: Custom field 78
        - custom79: Custom field 79
        - custom8: Custom field 8
        - custom80: Custom field 80
        - custom81: Custom field 81
        - custom82: Custom field 82
        - custom83: Custom field 83
        - custom84: Custom field 84
        - custom85: Custom field 85
        - custom86: Custom field 86
        - custom87: Custom field 87
        - custom88: Custom field 88
        - custom89: Custom field 89
        - custom9: Custom field 9
        - custom90: Custom field 90
        - custom91: Custom field 91
        - custom92: Custom field 92
        - custom93: Custom field 93
        - custom94: Custom field 94
        - custom95: Custom field 95
        - custom96: Custom field 96
        - custom97: Custom field 97
        - custom98: Custom field 98
        - custom99: Custom field 99
        - custom_id: Custom id
        - default_plugin_mapping: Default plugin mapping
        - description: Description
        - domain: Domain
        - external_source: External source
        - favorites: Favorites
        - followers: Followers
        - founded_at: Founded at
        - id: Unique account identifier
        - industry: Industry
        - linked_in_employees: Linked in employees
        - linked_in_url: Linked in url
        - locality: Locality
        - name: Name
        - named: Named
        - natural_name: Natural name
        - number_of_employees: Number of employees
        - owner: Owner
        - prospects: Prospects
        - sharing_team_id: Sharing team id
        - tags: Tags
        - tasks: Tasks
        - touched_at: Touched at
        - trashed_at: Trashed at
        - updated_at: Updated at
        - updater: Updater
        - website_url: Website url
        
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

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against accounts records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.Account`
    :   Get a single account by ID
        
        Args:
            id: Account ID
            **kwargs: Additional parameters
        
        Returns:
            Account

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Account], AccountsListResultMeta]`
    :   Returns a paginated list of accounts
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            AccountsListResult

<a id="CallDispositionsQuery"></a>

`CallDispositionsQuery(connector: OutreachConnector)`
:   Query class for CallDispositions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CallDispositionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[CallDispositionsSearchData]`
    :   Search call_dispositions records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CallDispositionsSearchFilter):
        - calls: Calls
        - created_at: Created at
        - creator: Creator
        - default_for_outbound_voicemail: Default for outbound voicemail
        - id: Unique call disposition identifier
        - name: Name
        - order: Order
        - outcome: Outcome
        - updated_at: Updated at
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CallDispositionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against call_dispositions records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.CallDisposition`
    :   Get a single call disposition by ID
        
        Args:
            id: Call Disposition ID
            **kwargs: Additional parameters
        
        Returns:
            CallDisposition

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[CallDisposition], CallDispositionsListResultMeta]`
    :   Returns a paginated list of call dispositions
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            CallDispositionsListResult

<a id="CallPurposesQuery"></a>

`CallPurposesQuery(connector: OutreachConnector)`
:   Query class for CallPurposes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CallPurposesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[CallPurposesSearchData]`
    :   Search call_purposes records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CallPurposesSearchFilter):
        - calls: Calls
        - created_at: Created at
        - creator: Creator
        - id: Unique call purpose identifier
        - name: Name
        - order: Order
        - updated_at: Updated at
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CallPurposesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against call_purposes records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.CallPurpose`
    :   Get a single call purpose by ID
        
        Args:
            id: Call Purpose ID
            **kwargs: Additional parameters
        
        Returns:
            CallPurpose

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[CallPurpose], CallPurposesListResultMeta]`
    :   Returns a paginated list of call purposes
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            CallPurposesListResult

<a id="CallsQuery"></a>

`CallsQuery(connector: OutreachConnector)`
:   Query class for Calls entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CallsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[CallsSearchData]`
    :   Search calls records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CallsSearchFilter):
        - answered_at: Answered at
        - batches: Batches
        - call_disposition: Call disposition
        - call_purpose: Call purpose
        - completed_at: Completed at
        - created_at: Created at
        - dialed_at: Dialed at
        - direction: Direction
        - external_vendor: External vendor
        - from_: From
        - id: Unique call identifier
        - note: Note
        - opportunity: Opportunity
        - outbound_voicemail: Outbound voicemail
        - outcome: Outcome
        - phone: Phone
        - phone_number: Phone number
        - prospect: Prospect
        - recording_deletion_reason: Recording deletion reason
        - recording_url: Recording url
        - returned_at: Returned at
        - sequence: Sequence
        - sequence_action: Sequence action
        - sequence_state: Sequence state
        - sequence_step: Sequence step
        - should_record_call: Should record call
        - state: State
        - state_changed_at: State changed at
        - tags: Tags
        - task: Task
        - to: To
        - uid: Uid
        - updated_at: Updated at
        - user: User
        - user_call_type: User call type
        - vendor_call_id: Vendor call id
        - voicemail_recording_url: Voicemail recording url
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CallsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against calls records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.Call`
    :   Get a single call by ID
        
        Args:
            id: Call ID
            **kwargs: Additional parameters
        
        Returns:
            Call

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Call], CallsListResultMeta]`
    :   Returns a paginated list of calls
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            CallsListResult

<a id="MailboxesQuery"></a>

`MailboxesQuery(connector: OutreachConnector)`
:   Query class for Mailboxes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MailboxesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[MailboxesSearchData]`
    :   Search mailboxes records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MailboxesSearchFilter):
        - auth_id: Auth id
        - created_at: Created at
        - creator: Creator
        - editable: Editable
        - email: Email
        - email_hash: Email hash
        - email_provider: Email provider
        - email_signature: Email signature
        - ews_custom_search_folder: Ews custom search folder
        - ews_delegate_sync: Ews delegate sync
        - ews_endpoint: Ews endpoint
        - ews_impersonation: Ews impersonation
        - ews_ssl_verify_mode: Ews ssl verify mode
        - exchange_version: Exchange version
        - id: Unique mailbox identifier
        - imap_host: Imap host
        - imap_port: Imap port
        - imap_ssl: Imap ssl
        - mail_aliases: Mail aliases
        - mailings: Mailings
        - max_emails_per_day: Max emails per day
        - max_mailings_per_day: Max mailings per day
        - max_mailings_per_week: Max mailings per week
        - opt_out_message: Opt out message
        - opt_out_signature: Opt out signature
        - prospect_email_exclusions: Prospect email exclusions
        - provider_id: Provider id
        - provider_type: Provider type
        - send_disabled: Send disabled
        - send_errored_at: Send errored at
        - send_max_retries: Send max retries
        - send_method: Send method
        - send_period: Send period
        - send_permanent_error_at: Send permanent error at
        - send_requires_sync: Send requires sync
        - send_success_at: Send success at
        - send_threshold: Send threshold
        - sendgrid_webhook_url: Sendgrid webhook url
        - smtp_host: Smtp host
        - smtp_port: Smtp port
        - smtp_ssl: Smtp ssl
        - smtp_username: Smtp username
        - sync_active_frequency: Sync active frequency
        - sync_disabled: Sync disabled
        - sync_errored_at: Sync errored at
        - sync_finished_at: Sync finished at
        - sync_method: Sync method
        - sync_outreach_folder: Sync outreach folder
        - sync_passive_frequency: Sync passive frequency
        - sync_permanent_error_at: Sync permanent error at
        - sync_success_at: Sync success at
        - updated_at: Updated at
        - updater: Updater
        - user: User
        - user_id: User id
        - username: Username
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MailboxesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against mailboxes records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.Mailbox`
    :   Get a single mailbox by ID
        
        Args:
            id: Mailbox ID
            **kwargs: Additional parameters
        
        Returns:
            Mailbox

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Mailbox], MailboxesListResultMeta]`
    :   Returns a paginated list of mailboxes
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            MailboxesListResult

<a id="MailingsQuery"></a>

`MailingsQuery(connector: OutreachConnector)`
:   Query class for Mailings entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MailingsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[MailingsSearchData]`
    :   Search mailings records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MailingsSearchFilter):
        - attachments: Attachments
        - attributable_sequence_id: Attributable sequence id
        - attributable_sequence_name: Attributable sequence name
        - body_html: Body html
        - body_text: Body text
        - bounced_at: Bounced at
        - calendar: Calendar
        - click_count: Click count
        - clicked_at: Clicked at
        - created_at: Created at
        - delivered_at: Delivered at
        - desired_at: Desired at
        - error_backtrace: Error backtrace
        - error_reason: Error reason
        - follow_up_sequence: Follow up sequence
        - follow_up_sequence_id: Follow up sequence id
        - follow_up_sequence_name: Follow up sequence name
        - follow_up_sequence_starting_date: Follow up sequence starting date
        - follow_up_task_scheduled_at: Follow up task scheduled at
        - follow_up_task_type: Follow up task type
        - id: Unique mailing identifier
        - mailbox: Mailbox
        - mailbox_address: Mailbox address
        - mailing_type: Mailing type
        - marked_as_spam_at: Marked as spam at
        - meeting_description: Meeting description
        - meeting_duration: Meeting duration
        - meeting_location: Meeting location
        - meeting_title: Meeting title
        - message_id: Message id
        - notify_thread_condition: Notify thread condition
        - notify_thread_scheduled_at: Notify thread scheduled at
        - notify_thread_status: Notify thread status
        - open_count: Open count
        - opened_at: Opened at
        - opportunity: Opportunity
        - optimized_scheduled_at: Optimized scheduled at
        - override_safety_settings: Override safety settings
        - prospect: Prospect
        - recipients: Recipients
        - references: References
        - replied_at: Replied at
        - reply_sentiment: Reply sentiment
        - retry_at: Retry at
        - retry_count: Retry count
        - retry_interval: Retry interval
        - schedule: Schedule
        - schedule_id: Schedule id
        - scheduled_at: Scheduled at
        - sequence: Sequence
        - sequence_state: Sequence state
        - sequence_step: Sequence step
        - state: State
        - state_changed_at: State changed at
        - subject: Subject
        - task: Task
        - tasks: Tasks
        - template: Template
        - track_links: Track links
        - track_opens: Track opens
        - unsubscribed_at: Unsubscribed at
        - updated_at: Updated at
        - user: User
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MailingsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against mailings records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.Mailing`
    :   Get a single mailing by ID
        
        Args:
            id: Mailing ID
            **kwargs: Additional parameters
        
        Returns:
            Mailing

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Mailing], MailingsListResultMeta]`
    :   Returns a paginated list of mailings
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            MailingsListResult

<a id="OpportunitiesQuery"></a>

`OpportunitiesQuery(connector: OutreachConnector)`
:   Query class for Opportunities entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OpportunitiesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[OpportunitiesSearchData]`
    :   Search opportunities records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OpportunitiesSearchFilter):
        - account: Account
        - amount: Amount
        - assigned_teams: Assigned teams
        - assigned_users: Assigned users
        - close_date: Close date
        - created_at: Created at
        - creator: Creator
        - currency_type: Currency type
        - custom1: Custom field 1
        - custom10: Custom field 10
        - custom100: Custom field 100
        - custom101: Custom field 101
        - custom102: Custom field 102
        - custom103: Custom field 103
        - custom104: Custom field 104
        - custom105: Custom field 105
        - custom106: Custom field 106
        - custom107: Custom field 107
        - custom108: Custom field 108
        - custom109: Custom field 109
        - custom11: Custom field 11
        - custom110: Custom field 110
        - custom111: Custom field 111
        - custom112: Custom field 112
        - custom113: Custom field 113
        - custom114: Custom field 114
        - custom115: Custom field 115
        - custom116: Custom field 116
        - custom117: Custom field 117
        - custom118: Custom field 118
        - custom119: Custom field 119
        - custom12: Custom field 12
        - custom120: Custom field 120
        - custom121: Custom field 121
        - custom122: Custom field 122
        - custom123: Custom field 123
        - custom124: Custom field 124
        - custom125: Custom field 125
        - custom126: Custom field 126
        - custom127: Custom field 127
        - custom128: Custom field 128
        - custom129: Custom field 129
        - custom13: Custom field 13
        - custom130: Custom field 130
        - custom131: Custom field 131
        - custom132: Custom field 132
        - custom133: Custom field 133
        - custom134: Custom field 134
        - custom135: Custom field 135
        - custom136: Custom field 136
        - custom137: Custom field 137
        - custom138: Custom field 138
        - custom139: Custom field 139
        - custom14: Custom field 14
        - custom140: Custom field 140
        - custom141: Custom field 141
        - custom142: Custom field 142
        - custom143: Custom field 143
        - custom144: Custom field 144
        - custom145: Custom field 145
        - custom146: Custom field 146
        - custom147: Custom field 147
        - custom148: Custom field 148
        - custom149: Custom field 149
        - custom15: Custom field 15
        - custom150: Custom field 150
        - custom16: Custom field 16
        - custom17: Custom field 17
        - custom18: Custom field 18
        - custom19: Custom field 19
        - custom2: Custom field 2
        - custom20: Custom field 20
        - custom21: Custom field 21
        - custom22: Custom field 22
        - custom23: Custom field 23
        - custom24: Custom field 24
        - custom25: Custom field 25
        - custom26: Custom field 26
        - custom27: Custom field 27
        - custom28: Custom field 28
        - custom29: Custom field 29
        - custom3: Custom field 3
        - custom30: Custom field 30
        - custom31: Custom field 31
        - custom32: Custom field 32
        - custom33: Custom field 33
        - custom34: Custom field 34
        - custom35: Custom field 35
        - custom36: Custom field 36
        - custom37: Custom field 37
        - custom38: Custom field 38
        - custom39: Custom field 39
        - custom4: Custom field 4
        - custom40: Custom field 40
        - custom41: Custom field 41
        - custom42: Custom field 42
        - custom43: Custom field 43
        - custom44: Custom field 44
        - custom45: Custom field 45
        - custom46: Custom field 46
        - custom47: Custom field 47
        - custom48: Custom field 48
        - custom49: Custom field 49
        - custom5: Custom field 5
        - custom50: Custom field 50
        - custom51: Custom field 51
        - custom52: Custom field 52
        - custom53: Custom field 53
        - custom54: Custom field 54
        - custom55: Custom field 55
        - custom56: Custom field 56
        - custom57: Custom field 57
        - custom58: Custom field 58
        - custom59: Custom field 59
        - custom6: Custom field 6
        - custom60: Custom field 60
        - custom61: Custom field 61
        - custom62: Custom field 62
        - custom63: Custom field 63
        - custom64: Custom field 64
        - custom65: Custom field 65
        - custom66: Custom field 66
        - custom67: Custom field 67
        - custom68: Custom field 68
        - custom69: Custom field 69
        - custom7: Custom field 7
        - custom70: Custom field 70
        - custom71: Custom field 71
        - custom72: Custom field 72
        - custom73: Custom field 73
        - custom74: Custom field 74
        - custom75: Custom field 75
        - custom76: Custom field 76
        - custom77: Custom field 77
        - custom78: Custom field 78
        - custom79: Custom field 79
        - custom8: Custom field 8
        - custom80: Custom field 80
        - custom81: Custom field 81
        - custom82: Custom field 82
        - custom83: Custom field 83
        - custom84: Custom field 84
        - custom85: Custom field 85
        - custom86: Custom field 86
        - custom87: Custom field 87
        - custom88: Custom field 88
        - custom89: Custom field 89
        - custom9: Custom field 9
        - custom90: Custom field 90
        - custom91: Custom field 91
        - custom92: Custom field 92
        - custom93: Custom field 93
        - custom94: Custom field 94
        - custom95: Custom field 95
        - custom96: Custom field 96
        - custom97: Custom field 97
        - custom98: Custom field 98
        - custom99: Custom field 99
        - default_plugin_mapping: Default plugin mapping
        - description: Description
        - external_created_at: External created at
        - external_creator: External creator
        - favorites: Favorites
        - health_category: Health category
        - health_score: Health score
        - id: Unique opportunity identifier
        - map_link: Map link
        - map_next_steps: Map next steps
        - map_number_of_overdue_tasks: Map number of overdue tasks
        - map_status: Map status
        - name: Name
        - next_step: Next step
        - opportunity_health_factors: Opportunity health factors
        - opportunity_stage: Opportunity stage
        - opportunity_type: Opportunity type
        - owner: Owner
        - primary_prospect: Primary prospect
        - probability: Probability
        - prospecting_rep_id: Prospecting rep id
        - prospects: Prospects
        - sharing_team_id: Sharing team id
        - stage: Stage
        - tags: Tags
        - touched_at: Touched at
        - updated_at: Updated at
        - updater: Updater
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OpportunitiesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against opportunities records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.Opportunity`
    :   Get a single opportunity by ID
        
        Args:
            id: Opportunity ID
            **kwargs: Additional parameters
        
        Returns:
            Opportunity

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Opportunity], OpportunitiesListResultMeta]`
    :   Returns a paginated list of opportunities
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            OpportunitiesListResult

<a id="OutreachConnector"></a>

`OutreachConnector(auth_config: OutreachAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Outreach API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new outreach connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., OutreachAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = OutreachConnector(auth_config=OutreachAuthConfig(client_id="...", client_secret="...", refresh_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = OutreachConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = OutreachConnector(
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
    :   Decorator for new user-written connector tool functions.
        
        Use this when a tool needs a custom body or the framework lacks a
        native strategy. Instead of baking the full entity/action reference
        into the docstring, it instructs the agent to call this connector's
        inspect and docs tools before executing. Tool failures raise
        :class:`airbyte_agent_sdk.AirbyteToolError` by default
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
            connector = OutreachConnector(...)
        
            @OutreachConnector.agent_tool()
            async def execute(entity: str, action: str, params: dict | None = None):
                return await connector.execute(entity=entity, action=action, params=params or \{\})
        
            @OutreachConnector.agent_tool()
            async def inspect_connector():
                return await connector.inspect_connector()
        
            @OutreachConnector.agent_tool()
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
    :   Deprecated. Add connector-specific documentation and runtime safeguards to one tool.
        
        Kept for backwards compatibility with existing single-tool
        integrations; it is not removed and does not warn at runtime, but new
        code should use `build_connector_tools` or `agent_tool` below.
        
        For new agents, prefer `build_connector_tools`. It returns progressive
        `inspect_connector`, `read_skill_docs`, and `execute` tools so the agent
        can load only the connector guidance it needs:
        
        ```python
        from airbyte_agent_sdk import build_connector_tools
        from pydantic_ai import Agent
        
        tools = build_connector_tools(connector, framework="pydantic_ai")
        agent = Agent("openai:gpt-4o", tools=tools.as_list())
        ```
        
        When a new integration needs custom tool bodies or a framework
        without native support, use `agent_tool` instead.
        
        ### Legacy: one generated-description tool
        
        Existing integrations can keep using `tool_utils` for one broad
        `execute` tool with the connector's full generated catalog in its
        description:
        
        ```python
        from fastmcp import FastMCP
        
        connector = OutreachConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @OutreachConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @OutreachConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @OutreachConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        This decorator composes `translate_exceptions` for runtime wrapping,
        output-size checks, framework signal translation, and optional internal
        retries, then adds connector-specific docstring augmentation.
        
        Args:
            update_docstring: When True, append connector capabilities to `__doc__`.
            max_output_chars: Max serialized output size before raising. Use `None` to disable.
            framework: One of `"pydantic_ai" | "langchain" | "openai_agents" | "mcp" | "none"`.
                Defaults to `None`, which auto-detects each framework's canonical
                import in order and falls back to `"none"` with a warning when no
                supported framework is installed. Explicit always wins, and an
                explicit framework whose package is missing raises `RuntimeError`.
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

    `check(self) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            OutreachCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'context_store_search', 'context_store_sql_query']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
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

<a id="PersonasQuery"></a>

`PersonasQuery(connector: OutreachConnector)`
:   Query class for Personas entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: PersonasSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[PersonasSearchData]`
    :   Search personas records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (PersonasSearchFilter):
        - created_at: Created at
        - description: Description
        - id: Unique persona identifier
        - name: Name
        - prospects: Prospects
        - updated_at: Updated at
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            PersonasSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against personas records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.Persona`
    :   Get a single persona by ID
        
        Args:
            id: Persona ID
            **kwargs: Additional parameters
        
        Returns:
            Persona

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Persona], PersonasListResultMeta]`
    :   Returns a paginated list of personas
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            PersonasListResult

<a id="ProspectsQuery"></a>

`ProspectsQuery(connector: OutreachConnector)`
:   Query class for Prospects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProspectsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[ProspectsSearchData]`
    :   Search prospects records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProspectsSearchFilter):
        - account: Account
        - account_name: Account name
        - active_sequence_states: Active sequence states
        - added_at: Added at
        - address_city: Address city
        - address_country: Address country
        - address_state: Address state
        - address_street: Address street
        - address_street2: Address street2
        - address_zip: Address zip
        - angel_list_url: Angel list url
        - assigned_teams: Assigned teams
        - assigned_users: Assigned users
        - available_at: Available at
        - batches: Batches
        - call_opted_out: Call opted out
        - calls: Calls
        - calls_opt_status: Calls opt status
        - calls_opted_at: Calls opted at
        - campaign_name: Campaign name
        - click_count: Click count
        - company: Company
        - company_followers: Company followers
        - company_founded_at: Company founded at
        - company_industry: Company industry
        - company_linked_in: Company linked in
        - company_linked_in_employees: Company linked in employees
        - company_locality: Company locality
        - company_natural: Company natural
        - company_size: Company size
        - company_start_date: Company start date
        - company_type: Company type
        - contact_histogram: Contact histogram
        - created_at: Created at
        - creator: Creator
        - custom1: Custom field 1
        - custom10: Custom field 10
        - custom100: Custom field 100
        - custom101: Custom field 101
        - custom102: Custom field 102
        - custom103: Custom field 103
        - custom104: Custom field 104
        - custom105: Custom field 105
        - custom106: Custom field 106
        - custom107: Custom field 107
        - custom108: Custom field 108
        - custom109: Custom field 109
        - custom11: Custom field 11
        - custom110: Custom field 110
        - custom111: Custom field 111
        - custom112: Custom field 112
        - custom113: Custom field 113
        - custom114: Custom field 114
        - custom115: Custom field 115
        - custom116: Custom field 116
        - custom117: Custom field 117
        - custom118: Custom field 118
        - custom119: Custom field 119
        - custom12: Custom field 12
        - custom120: Custom field 120
        - custom121: Custom field 121
        - custom122: Custom field 122
        - custom123: Custom field 123
        - custom124: Custom field 124
        - custom125: Custom field 125
        - custom126: Custom field 126
        - custom127: Custom field 127
        - custom128: Custom field 128
        - custom129: Custom field 129
        - custom13: Custom field 13
        - custom130: Custom field 130
        - custom131: Custom field 131
        - custom132: Custom field 132
        - custom133: Custom field 133
        - custom134: Custom field 134
        - custom135: Custom field 135
        - custom136: Custom field 136
        - custom137: Custom field 137
        - custom138: Custom field 138
        - custom139: Custom field 139
        - custom14: Custom field 14
        - custom140: Custom field 140
        - custom141: Custom field 141
        - custom142: Custom field 142
        - custom143: Custom field 143
        - custom144: Custom field 144
        - custom145: Custom field 145
        - custom146: Custom field 146
        - custom147: Custom field 147
        - custom148: Custom field 148
        - custom149: Custom field 149
        - custom15: Custom field 15
        - custom150: Custom field 150
        - custom16: Custom field 16
        - custom17: Custom field 17
        - custom18: Custom field 18
        - custom19: Custom field 19
        - custom2: Custom field 2
        - custom20: Custom field 20
        - custom21: Custom field 21
        - custom22: Custom field 22
        - custom23: Custom field 23
        - custom24: Custom field 24
        - custom25: Custom field 25
        - custom26: Custom field 26
        - custom27: Custom field 27
        - custom28: Custom field 28
        - custom29: Custom field 29
        - custom3: Custom field 3
        - custom30: Custom field 30
        - custom31: Custom field 31
        - custom32: Custom field 32
        - custom33: Custom field 33
        - custom34: Custom field 34
        - custom35: Custom field 35
        - custom36: Custom field 36
        - custom37: Custom field 37
        - custom38: Custom field 38
        - custom39: Custom field 39
        - custom4: Custom field 4
        - custom40: Custom field 40
        - custom41: Custom field 41
        - custom42: Custom field 42
        - custom43: Custom field 43
        - custom44: Custom field 44
        - custom45: Custom field 45
        - custom46: Custom field 46
        - custom47: Custom field 47
        - custom48: Custom field 48
        - custom49: Custom field 49
        - custom5: Custom field 5
        - custom50: Custom field 50
        - custom51: Custom field 51
        - custom52: Custom field 52
        - custom53: Custom field 53
        - custom54: Custom field 54
        - custom55: Custom field 55
        - custom56: Custom field 56
        - custom57: Custom field 57
        - custom58: Custom field 58
        - custom59: Custom field 59
        - custom6: Custom field 6
        - custom60: Custom field 60
        - custom61: Custom field 61
        - custom62: Custom field 62
        - custom63: Custom field 63
        - custom64: Custom field 64
        - custom65: Custom field 65
        - custom66: Custom field 66
        - custom67: Custom field 67
        - custom68: Custom field 68
        - custom69: Custom field 69
        - custom7: Custom field 7
        - custom70: Custom field 70
        - custom71: Custom field 71
        - custom72: Custom field 72
        - custom73: Custom field 73
        - custom74: Custom field 74
        - custom75: Custom field 75
        - custom76: Custom field 76
        - custom77: Custom field 77
        - custom78: Custom field 78
        - custom79: Custom field 79
        - custom8: Custom field 8
        - custom80: Custom field 80
        - custom81: Custom field 81
        - custom82: Custom field 82
        - custom83: Custom field 83
        - custom84: Custom field 84
        - custom85: Custom field 85
        - custom86: Custom field 86
        - custom87: Custom field 87
        - custom88: Custom field 88
        - custom89: Custom field 89
        - custom9: Custom field 9
        - custom90: Custom field 90
        - custom91: Custom field 91
        - custom92: Custom field 92
        - custom93: Custom field 93
        - custom94: Custom field 94
        - custom95: Custom field 95
        - custom96: Custom field 96
        - custom97: Custom field 97
        - custom98: Custom field 98
        - custom99: Custom field 99
        - date_of_birth: Date of birth
        - default_plugin_mapping: Default plugin mapping
        - degree: Degree
        - email_addresses: Email addresses
        - email_contacts: Email contacts
        - email_opted_out: Email opted out
        - emails: Emails
        - emails_opt_status: Emails opt status
        - emails_opted_at: Emails opted at
        - engaged_at: Engaged at
        - engaged_score: Engaged score
        - event_name: Event name
        - external_id: External id
        - external_owner: External owner
        - external_source: External source
        - facebook_url: Facebook url
        - favorites: Favorites
        - first_name: First name
        - gender: Gender
        - github_url: Github url
        - github_username: Github username
        - google_plus_url: Google plus url
        - graduation_date: Graduation date
        - home_phones: Home phones
        - id: Unique prospect identifier
        - job_start_date: Job start date
        - last_name: Last name
        - linked_in_connections: Linked in connections
        - linked_in_id: Linked in id
        - linked_in_slug: Linked in slug
        - linked_in_url: Linked in url
        - mailings: Mailings
        - middle_name: Middle name
        - mobile_phones: Mobile phones
        - name: Name
        - nickname: Nickname
        - occupation: Occupation
        - open_count: Open count
        - opportunities: Opportunities
        - opportunity_prospect_roles: Opportunity prospect roles
        - opted_out: Opted out
        - opted_out_at: Opted out at
        - other_phones: Other phones
        - owner: Owner
        - persona: Persona
        - persona_name: Persona name
        - personal_note1: Personal note1
        - personal_note2: Personal note2
        - phone_numbers: Phone numbers
        - preferred_contact: Preferred contact
        - quora_url: Quora url
        - region: Region
        - reply_count: Reply count
        - school: School
        - score: Score
        - sequence_states: Sequence states
        - sharing_team_id: Sharing team id
        - sms_opt_status: Sms opt status
        - sms_opted_at: Sms opted at
        - sms_opted_out: Sms opted out
        - source: Source
        - specialties: Specialties
        - stack_overflow_id: Stack overflow id
        - stack_overflow_url: Stack overflow url
        - stage: Stage
        - stage_name: Stage name
        - tags: Tags
        - tasks: Tasks
        - time_zone: Time zone
        - time_zone_iana: Time zone iana
        - time_zone_inferred: Time zone inferred
        - title: Title
        - touched_at: Touched at
        - trashed_at: Trashed at
        - trashed_by_account: Trashed by account
        - twitter_url: Twitter url
        - twitter_username: Twitter username
        - updated_at: Updated at
        - updater: Updater
        - updater_id: Updater id
        - updater_type: Updater type
        - voip_phones: Voip phones
        - website_url1: Website url1
        - website_url2: Website url2
        - website_url3: Website url3
        - work_phones: Work phones
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProspectsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against prospects records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.Prospect`
    :   Get a single prospect by ID
        
        Args:
            id: Prospect ID
            **kwargs: Additional parameters
        
        Returns:
            Prospect

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Prospect], ProspectsListResultMeta]`
    :   Returns a paginated list of prospects (contacts) in Outreach
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            ProspectsListResult

<a id="SequenceStatesQuery"></a>

`SequenceStatesQuery(connector: OutreachConnector)`
:   Query class for SequenceStates entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SequenceStatesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[SequenceStatesSearchData]`
    :   Search sequence_states records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SequenceStatesSearchFilter):
        - account: Account
        - active_at: Active at
        - active_step_mailings: Active step mailings
        - active_step_tasks: Active step tasks
        - bounce_count: Bounce count
        - call_completed_at: Call completed at
        - calls: Calls
        - click_count: Click count
        - created_at: Created at
        - creator: Creator
        - deliver_count: Deliver count
        - error_reason: Error reason
        - failure_count: Failure count
        - id: Unique sequence state identifier
        - mailbox: Mailbox
        - mailings: Mailings
        - negative_reply_count: Negative reply count
        - neutral_reply_count: Neutral reply count
        - open_count: Open count
        - opportunity: Opportunity
        - opt_out_count: Opt out count
        - pause_reason: Pause reason
        - positive_reply_count: Positive reply count
        - prospect: Prospect
        - replied_at: Replied at
        - reply_count: Reply count
        - schedule_count: Schedule count
        - sequence: Sequence
        - sequence_step: Sequence step
        - state: State
        - state_changed_at: State changed at
        - tasks: Tasks
        - updated_at: Updated at
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SequenceStatesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against sequence_states records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.SequenceState`
    :   Get a single sequence state by ID
        
        Args:
            id: Sequence State ID
            **kwargs: Additional parameters
        
        Returns:
            SequenceState

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[SequenceState], SequenceStatesListResultMeta]`
    :   Returns a paginated list of sequence states (prospect-in-sequence associations)
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            SequenceStatesListResult

<a id="SequenceStepsQuery"></a>

`SequenceStepsQuery(connector: OutreachConnector)`
:   Query class for SequenceSteps entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SequenceStepsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[SequenceStepsSearchData]`
    :   Search sequence_steps records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SequenceStepsSearchFilter):
        - bounce_count: Bounce count
        - call_purpose: Call purpose
        - calls: Calls
        - click_count: Click count
        - created_at: Created at
        - creator: Creator
        - date: Date
        - deliver_count: Deliver count
        - display_name: Display name
        - failure_count: Failure count
        - id: Unique sequence step identifier
        - interval: Interval
        - mailings: Mailings
        - negative_reply_count: Negative reply count
        - neutral_reply_count: Neutral reply count
        - open_count: Open count
        - opt_out_count: Opt out count
        - order: Order
        - positive_reply_count: Positive reply count
        - reply_count: Reply count
        - schedule_count: Schedule count
        - sequence: Sequence
        - sequence_templates: Sequence templates
        - step_type: Step type
        - task_auto_display: Task auto display
        - task_priority: Task priority
        - tasks: Tasks
        - updated_at: Updated at
        - updater: Updater
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SequenceStepsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against sequence_steps records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.SequenceStep`
    :   Get a single sequence step by ID
        
        Args:
            id: Sequence Step ID
            **kwargs: Additional parameters
        
        Returns:
            SequenceStep

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[SequenceStep], SequenceStepsListResultMeta]`
    :   Returns a paginated list of sequence steps
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            SequenceStepsListResult

<a id="SequencesQuery"></a>

`SequencesQuery(connector: OutreachConnector)`
:   Query class for Sequences entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SequencesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[SequencesSearchData]`
    :   Search sequences records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SequencesSearchFilter):
        - automation_percentage: Automation percentage
        - bounce_count: Bounce count
        - calls: Calls
        - click_count: Click count
        - content_category_memberships: Content category memberships
        - created_at: Created at
        - creator: Creator
        - deliver_count: Deliver count
        - description: Description
        - duration_in_days: Duration in days
        - enabled: Enabled
        - enabled_at: Enabled at
        - failure_count: Failure count
        - finish_on_reply: Finish on reply
        - id: Unique sequence identifier
        - last_used_at: Last used at
        - locked: Locked
        - locked_at: Locked at
        - mailings: Mailings
        - max_activations: Max activations
        - name: Name
        - negative_reply_count: Negative reply count
        - neutral_reply_count: Neutral reply count
        - num_contacted_prospects: Num contacted prospects
        - num_replied_prospects: Num replied prospects
        - open_count: Open count
        - opt_out_count: Opt out count
        - owner: Owner
        - positive_reply_count: Positive reply count
        - primary_reply_action: Primary reply action
        - primary_reply_pause_duration: Primary reply pause duration
        - reply_count: Reply count
        - ruleset: Ruleset
        - schedule: Schedule
        - schedule_count: Schedule count
        - schedule_interval_type: Schedule interval type
        - secondary_reply_action: Secondary reply action
        - secondary_reply_pause_duration: Secondary reply pause duration
        - sequence_states: Sequence states
        - sequence_step_count: Sequence step count
        - sequence_steps: Sequence steps
        - sequence_type: Sequence type
        - share_type: Share type
        - tags: Tags
        - tasks: Tasks
        - throttle_capacity: Throttle capacity
        - throttle_max_adds_per_day: Throttle max adds per day
        - throttle_paused: Throttle paused
        - throttle_paused_at: Throttle paused at
        - transactional: Transactional
        - updated_at: Updated at
        - updater: Updater
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SequencesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against sequences records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.Sequence`
    :   Get a single sequence by ID
        
        Args:
            id: Sequence ID
            **kwargs: Additional parameters
        
        Returns:
            Sequence

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Sequence], SequencesListResultMeta]`
    :   Returns a paginated list of sequences
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            SequencesListResult

<a id="SnippetsQuery"></a>

`SnippetsQuery(connector: OutreachConnector)`
:   Query class for Snippets entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SnippetsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[SnippetsSearchData]`
    :   Search snippets records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SnippetsSearchFilter):
        - body_html: Body html
        - body_text: Body text
        - content_category_memberships: Content category memberships
        - created_at: Created at
        - creator: Creator
        - id: Unique snippet identifier
        - name: Name
        - owner: Owner
        - share_type: Share type
        - tags: Tags
        - updated_at: Updated at
        - updater: Updater
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SnippetsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against snippets records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.Snippet`
    :   Get a single snippet by ID
        
        Args:
            id: Snippet ID
            **kwargs: Additional parameters
        
        Returns:
            Snippet

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Snippet], SnippetsListResultMeta]`
    :   Returns a paginated list of snippets
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            SnippetsListResult

<a id="StagesQuery"></a>

`StagesQuery(connector: OutreachConnector)`
:   Query class for Stages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: StagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[StagesSearchData]`
    :   Search stages records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (StagesSearchFilter):
        - color: Color
        - created_at: Created at
        - creator: Creator
        - id: Unique stage identifier
        - name: Name
        - order: Order
        - prospects: Prospects
        - updated_at: Updated at
        - updater: Updater
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            StagesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against stages records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.Stage`
    :   Get a single stage by ID
        
        Args:
            id: Stage ID
            **kwargs: Additional parameters
        
        Returns:
            Stage

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Stage], StagesListResultMeta]`
    :   Returns a paginated list of opportunity stages
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            StagesListResult

<a id="TasksQuery"></a>

`TasksQuery(connector: OutreachConnector)`
:   Query class for Tasks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TasksSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[TasksSearchData]`
    :   Search tasks records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TasksSearchFilter):
        - account: Account
        - action: Action
        - autoskip_at: Autoskip at
        - call: Call
        - calls: Calls
        - compiled_sequence_template_html: Compiled sequence template html
        - completed: Completed
        - completed_at: Completed at
        - completer: Completer
        - created_at: Created at
        - creator: Creator
        - default_plugin_mapping: Default plugin mapping
        - due_at: Due at
        - id: Unique task identifier
        - mailing: Mailing
        - mailings: Mailings
        - note: Note
        - opportunity: Opportunity
        - opportunity_association: Opportunity association
        - owner: Owner
        - prospect: Prospect
        - prospect_account: Prospect account
        - prospect_contacts: Prospect contacts
        - prospect_owner: Prospect owner
        - prospect_phone_numbers: Prospect phone numbers
        - prospect_stage: Prospect stage
        - scheduled_at: Scheduled at
        - sequence: Sequence
        - sequence_sequence_steps: Sequence sequence steps
        - sequence_state: Sequence state
        - sequence_state_sequence_step: Sequence state sequence step
        - sequence_state_sequence_step_overrides: Sequence state sequence step overrides
        - sequence_state_starting_template: Sequence state starting template
        - sequence_step: Sequence step
        - sequence_step_override_templates: Sequence step override templates
        - sequence_template: Sequence template
        - sequence_template_template: Sequence template template
        - state: State
        - state_changed_at: State changed at
        - subject: Subject
        - task_priority: Task priority
        - task_theme: Task theme
        - task_type: Task type
        - template: Template
        - updated_at: Updated at
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TasksSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against tasks records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.Task`
    :   Get a single task by ID
        
        Args:
            id: Task ID
            **kwargs: Additional parameters
        
        Returns:
            Task

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Task], TasksListResultMeta]`
    :   Returns a paginated list of tasks
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            TasksListResult

<a id="TemplatesQuery"></a>

`TemplatesQuery(connector: OutreachConnector)`
:   Query class for Templates entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TemplatesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[TemplatesSearchData]`
    :   Search templates records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TemplatesSearchFilter):
        - archived: Archived
        - archived_at: Archived at
        - bcc_recipients: Bcc recipients
        - body_html: Body html
        - body_text: Body text
        - bounce_count: Bounce count
        - cc_recipients: Cc recipients
        - click_count: Click count
        - content_category_memberships: Content category memberships
        - created_at: Created at
        - creator: Creator
        - deliver_count: Deliver count
        - failure_count: Failure count
        - id: Unique template identifier
        - last_used_at: Last used at
        - name: Name
        - negative_reply_count: Negative reply count
        - neutral_reply_count: Neutral reply count
        - open_count: Open count
        - opt_out_count: Opt out count
        - owner: Owner
        - positive_reply_count: Positive reply count
        - recipients: Recipients
        - reply_count: Reply count
        - schedule_count: Schedule count
        - sequence_templates: Sequence templates
        - share_type: Share type
        - subject: Subject
        - tags: Tags
        - to_recipients: To recipients
        - track_links: Track links
        - track_opens: Track opens
        - updated_at: Updated at
        - updater: Updater
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TemplatesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against templates records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.Template`
    :   Get a single template by ID
        
        Args:
            id: Template ID
            **kwargs: Additional parameters
        
        Returns:
            Template

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[Template], TemplatesListResultMeta]`
    :   Returns a paginated list of email templates
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            TemplatesListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: OutreachConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - accounts_view_id: Accounts view id
        - active_prospects_count: Active prospects count
        - activity_notifications_disabled: Activity notifications disabled
        - batches: Batches
        - batches_view_id: Batches view id
        - bounce_warning_email_enabled: Bounce warning email enabled
        - bridge_phone: Bridge phone
        - bridge_phone_extension: Bridge phone extension
        - buyer_language_preference: Buyer language preference
        - calendar: Calendar
        - calendar_events_view_id: Calendar events view id
        - calls_view_id: Calls view id
        - content_categories: Content categories
        - content_category_ownerships: Content category ownerships
        - controlled_tab_default: Controlled tab default
        - created_at: Created at
        - creator: Creator
        - current_sign_in_at: Current sign in at
        - custom1: Custom field 1
        - custom2: Custom field 2
        - custom3: Custom field 3
        - custom4: Custom field 4
        - custom5: Custom field 5
        - daily_digest_email_enabled: Daily digest email enabled
        - default_ruleset_id: Default ruleset id
        - default_schedule_id: Default schedule id
        - duties: Duties
        - duties_set_at: Duties set at
        - email: Email
        - enable_voice_recordings: Enable voice recordings
        - engagement_emails_enabled: Engagement emails enabled
        - favorites: Favorites
        - first_name: First name
        - global_id: Global id
        - id: Unique user identifier
        - imports_view_id: Imports view id
        - inbound_bridge_phone: Inbound bridge phone
        - inbound_bridge_phone_extension: Inbound bridge phone extension
        - inbound_call_behavior: Inbound call behavior
        - inbound_phone_type: Inbound phone type
        - inbound_voicemail_custom_message_text: Inbound voicemail custom message text
        - inbound_voicemail_message_text_voice: Inbound voicemail message text voice
        - inbound_voicemail_prompt_type: Inbound voicemail prompt type
        - job_role: Job role
        - kaia_recordings_view_id: Kaia recordings view id
        - keep_bridge_phone_connected: Keep bridge phone connected
        - language_preference: Language preference
        - last_name: Last name
        - last_sign_in_at: Last sign in at
        - link_to_sequence_state_in_task_flow: Link to sequence state in task flow
        - live_listen_view_id: Live listen view id
        - locked: Locked
        - mailbox: Mailbox
        - mailbox_error_email_enabled: Mailbox error email enabled
        - mailboxes: Mailboxes
        - mailings_delivered_count: Mailings delivered count
        - mailings_replied_count: Mailings replied count
        - mailings_view_id: Mailings view id
        - meeting_engagement_notification_enabled: Meeting engagement notification enabled
        - meeting_types_view_id: Meeting types view id
        - name: Name
        - notifications_enabled: Notifications enabled
        - oce_click_to_dial_everywhere: Oce click to dial everywhere
        - oce_gmail_toolbar: Oce gmail toolbar
        - oce_gmail_tracking_state: Oce gmail tracking state
        - oce_salesforce_email_decorating: Oce salesforce email decorating
        - oce_salesforce_phone_decorating: Oce salesforce phone decorating
        - oce_universal_task_flow: Oce universal task flow
        - oce_window_mode: Oce window mode
        - onboarded_at: Onboarded at
        - opportunities_view_id: Opportunities view id
        - orca_standalone_enabled: Orca standalone enabled
        - outbound_voicemails: Outbound voicemails
        - password_expires_at: Password expires at
        - phone: Phone
        - phone_country_code: Phone country code
        - phone_number: Phone number
        - phone_type: Phone type
        - phones: Phones
        - phones_view_id: Phones view id
        - plugin_alert_notification_enabled: Plugin alert notification enabled
        - preferred_voice_region: Preferred voice region
        - prefers_local_presence: Prefers local presence
        - primary_timezone: Primary timezone
        - profile: Profile
        - prospect_detail_default: Prospect detail default
        - prospects_view_id: Prospects view id
        - recipients: Recipients
        - reports_sequence_performance_view_id: Reports sequence performance view id
        - reports_team_perf_view_id: Reports team perf view id
        - reports_team_performance_intraday_view_id: Reports team performance intraday view id
        - reports_team_performance_view_id: Reports team performance view id
        - reports_view_id: Reports view id
        - role: Role
        - scim_external_id: Scim external id
        - scim_source: Scim source
        - secondary_timezone: Secondary timezone
        - send_invite_fallback: Send invite fallback
        - sender_notifications_excluded: Sender notifications excluded
        - sequence_states_view_id: Sequence states view id
        - sequences_view_id: Sequences view id
        - sms_phone: Sms phone
        - snippets_view_id: Snippets view id
        - tasks_due_count: Tasks due count
        - tasks_view_id: Tasks view id
        - teams: Teams
        - teams_view_id: Teams view id
        - templates_view_id: Templates view id
        - tertiary_timezone: Tertiary timezone
        - texting_email_notifications: Texting email notifications
        - title: Title
        - unknown_reply_email_enabled: Unknown reply email enabled
        - updated_at: Updated at
        - updater: Updater
        - use_sales_navigator_for_linked_in_tasks: Use sales navigator for linked in tasks
        - user_guid: User guid
        - username: Username
        - users_view_id: Users view id
        - voicemail_notification_enabled: Voicemail notification enabled
        - voicemail_prompts: Voicemail prompts
        - weekly_digest_email_enabled: Weekly digest email enabled
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            UsersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.outreach.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against users records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.User`
    :   Get a single user by ID
        
        Args:
            id: User ID
            **kwargs: Additional parameters
        
        Returns:
            User

    `list(self, page_size: int | None = None, sort: str | None = None, count: str | None = None, page_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.outreach.models.OutreachExecuteResultWithMeta[list[User], UsersListResultMeta]`
    :   Returns a paginated list of users
        
        Args:
            page_size: Number of items per page
            sort: Sort field
            count: Include count
            page_after: Cursor for the next page; use the page[after] value from meta.next_link
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult