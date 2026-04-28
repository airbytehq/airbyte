---
id: airbyte_agent_sdk-connectors-zendesk_talk-connector
title: airbyte_agent_sdk.connectors.zendesk_talk.connector
---

Module airbyte_agent_sdk.connectors.zendesk_talk.connector
==========================================================
Zendesk-Talk connector.

Classes
-------

<a id="AccountOverviewQuery"></a>

`AccountOverviewQuery(connector: ZendeskTalkConnector)`
:   Query class for AccountOverview entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AccountOverviewSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[AccountOverviewSearchData]`
    :   Search account_overview records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AccountOverviewSearchFilter):
        - average_call_duration: Average call duration
        - average_callback_wait_time: Average callback wait time
        - average_hold_time: Average hold time per call
        - average_queue_wait_time: Average queue wait time
        - average_time_to_answer: Average time to answer
        - average_wrap_up_time: Average wrap-up time
        - current_timestamp: Current timestamp
        - max_calls_waiting: Max calls waiting in queue
        - max_queue_wait_time: Max queue wait time
        - total_call_duration: Total call duration
        - total_callback_calls: Total callback calls
        - total_calls: Total calls
        - total_calls_abandoned_in_queue: Total calls abandoned in queue
        - total_calls_outside_business_hours: Total calls outside business hours
        - total_calls_with_exceeded_queue_wait_time: Total calls exceeding max queue wait time
        - total_calls_with_requested_voicemail: Total calls requesting voicemail
        - total_embeddable_callback_calls: Total embeddable callback calls
        - total_hold_time: Total hold time
        - total_inbound_calls: Total inbound calls
        - total_outbound_calls: Total outbound calls
        - total_textback_requests: Total textback requests
        - total_voicemails: Total voicemails
        - total_wrap_up_time: Total wrap-up time
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AccountOverviewSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult[AccountOverview]`
    :   Returns overview statistics for the account for the current day
        
        Returns:
            AccountOverviewListResult

<a id="AddressesQuery"></a>

`AddressesQuery(connector: ZendeskTalkConnector)`
:   Query class for Addresses entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AddressesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[AddressesSearchData]`
    :   Search addresses records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AddressesSearchFilter):
        - city: City of the address
        - country_code: ISO country code
        - id: Unique address identifier
        - name: Name of the address
        - provider_reference: Provider reference of the address
        - province: Province of the address
        - state: State of the address
        - street: Street of the address
        - zip: Zip code of the address
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AddressesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, address_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.Address`
    :   Retrieves a single address by ID
        
        Args:
            address_id: ID of the address
            **kwargs: Additional parameters
        
        Returns:
            Address

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[Address], AddressesListResultMeta]`
    :   Returns a list of all addresses in the Zendesk Talk account
        
        Returns:
            AddressesListResult

<a id="AgentsActivityQuery"></a>

`AgentsActivityQuery(connector: ZendeskTalkConnector)`
:   Query class for AgentsActivity entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AgentsActivitySearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[AgentsActivitySearchData]`
    :   Search agents_activity records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AgentsActivitySearchFilter):
        - accepted_third_party_conferences: Accepted third party conferences
        - accepted_transfers: Total transfers accepted
        - agent_id: Agent ID
        - agent_state: Agent state: online, offline, away, or transfers_only
        - available_time: Total time agent was available to answer calls
        - avatar_url: URL to agent avatar
        - average_hold_time: Average hold time per call
        - average_talk_time: Average talk time per call
        - average_wrap_up_time: Average wrap-up time per call
        - away_time: Total time agent was set to away
        - call_status: Agent call status: on_call, wrap_up, or null
        - calls_accepted: Total calls accepted
        - calls_denied: Total calls denied
        - calls_missed: Total calls missed
        - calls_put_on_hold: Total calls placed on hold
        - forwarding_number: Forwarding number set by the agent
        - name: Agent name
        - online_time: Total online time
        - started_third_party_conferences: Started third party conferences
        - started_transfers: Total transfers started
        - total_call_duration: Total call duration
        - total_hold_time: Total hold time across all calls
        - total_talk_time: Total talk time (excludes hold)
        - total_wrap_up_time: Total wrap-up time
        - transfers_only_time: Total time in transfers-only mode
        - via: Channel the agent is registered on
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AgentsActivitySearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[AgentActivity], AgentsActivityListResultMeta]`
    :   Returns activity statistics for all agents for the current day
        
        Returns:
            AgentsActivityListResult

<a id="AgentsOverviewQuery"></a>

`AgentsOverviewQuery(connector: ZendeskTalkConnector)`
:   Query class for AgentsOverview entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AgentsOverviewSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[AgentsOverviewSearchData]`
    :   Search agents_overview records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AgentsOverviewSearchFilter):
        - average_accepted_transfers: Average accepted transfers
        - average_available_time: Average available time
        - average_away_time: Average away time
        - average_calls_accepted: Average calls accepted
        - average_calls_denied: Average calls denied
        - average_calls_missed: Average calls missed
        - average_calls_put_on_hold: Average calls put on hold
        - average_hold_time: Average hold time
        - average_online_time: Average online time
        - average_started_transfers: Average started transfers
        - average_talk_time: Average talk time
        - average_transfers_only_time: Average transfers-only time
        - average_wrap_up_time: Average wrap-up time
        - current_timestamp: Current timestamp
        - total_accepted_transfers: Total accepted transfers
        - total_calls_accepted: Total calls accepted
        - total_calls_denied: Total calls denied
        - total_calls_missed: Total calls missed
        - total_calls_put_on_hold: Total calls put on hold
        - total_hold_time: Total hold time
        - total_started_transfers: Total started transfers
        - total_talk_time: Total talk time
        - total_wrap_up_time: Total wrap-up time
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AgentsOverviewSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult[AgentsOverview]`
    :   Returns overview statistics for all agents for the current day
        
        Returns:
            AgentsOverviewListResult

<a id="CallLegsQuery"></a>

`CallLegsQuery(connector: ZendeskTalkConnector)`
:   Query class for CallLegs entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CallLegsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[CallLegsSearchData]`
    :   Search call_legs records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CallLegsSearchFilter):
        - agent_id: Agent ID
        - available_via: Channel agent was available through
        - call_charge: Call charge amount
        - call_id: Associated call ID
        - completion_status: Completion status
        - conference_from: Conference from time
        - conference_time: Conference duration
        - conference_to: Conference to time
        - consultation_from: Consultation from time
        - consultation_time: Consultation duration
        - consultation_to: Consultation to time
        - created_at: Creation timestamp
        - duration: Duration in seconds
        - forwarded_to: Number forwarded to
        - hold_time: Hold time in seconds
        - id: Call leg ID
        - minutes_billed: Minutes billed
        - quality_issues: Quality issues detected
        - talk_time: Talk time in seconds
        - transferred_from: Transferred from agent ID
        - transferred_to: Transferred to agent ID
        - type_: Type of call leg
        - updated_at: Last update timestamp
        - user_id: User ID
        - wrap_up_time: Wrap-up time in seconds
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CallLegsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, start_time: int, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[CallLeg], CallLegsListResultMeta]`
    :   Returns incremental call leg data. Requires a start_time parameter (Unix epoch timestamp).
        
        Args:
            start_time: Unix epoch time to start from (e.g. 1704067200 for 2024-01-01)
            **kwargs: Additional parameters
        
        Returns:
            CallLegsListResult

<a id="CallsQuery"></a>

`CallsQuery(connector: ZendeskTalkConnector)`
:   Query class for Calls entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CallsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[CallsSearchData]`
    :   Search calls records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CallsSearchFilter):
        - agent_id: Agent ID
        - call_charge: Call charge amount
        - call_group_id: Call group ID
        - call_recording_consent: Call recording consent status
        - call_recording_consent_action: Recording consent action
        - call_recording_consent_keypress: Recording consent keypress
        - callback: Whether this was a callback
        - callback_source: Source of the callback
        - completion_status: Call completion status
        - consultation_time: Consultation time
        - created_at: Creation timestamp
        - customer_requested_voicemail: Whether customer requested voicemail
        - default_group: Whether default group was used
        - direction: Call direction (inbound/outbound)
        - duration: Call duration in seconds
        - exceeded_queue_time: Whether queue time was exceeded
        - exceeded_queue_wait_time: Whether max queue wait time was exceeded
        - hold_time: Hold time in seconds
        - id: Call ID
        - ivr_action: IVR action taken
        - ivr_destination_group_name: IVR destination group name
        - ivr_hops: Number of IVR hops
        - ivr_routed_to: Where IVR routed the call
        - ivr_time_spent: Time spent in IVR
        - minutes_billed: Minutes billed
        - not_recording_time: Time not recording
        - outside_business_hours: Whether call was outside business hours
        - overflowed: Whether call overflowed
        - overflowed_to: Where call overflowed to
        - phone_number: Phone number used
        - phone_number_id: Phone number ID
        - quality_issues: Quality issues detected
        - recording_control_interactions: Recording control interactions count
        - recording_time: Recording time
        - talk_time: Talk time in seconds
        - ticket_id: Associated ticket ID
        - time_to_answer: Time to answer in seconds
        - updated_at: Last update timestamp
        - voicemail: Whether it was a voicemail
        - wait_time: Wait time in seconds
        - wrap_up_time: Wrap-up time in seconds
        
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

    `list(self, start_time: int, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[Call], CallsListResultMeta]`
    :   Returns incremental call data. Requires a start_time parameter (Unix epoch timestamp).
        
        Args:
            start_time: Unix epoch time to start from (e.g. 1704067200 for 2024-01-01)
            **kwargs: Additional parameters
        
        Returns:
            CallsListResult

<a id="CurrentQueueActivityQuery"></a>

`CurrentQueueActivityQuery(connector: ZendeskTalkConnector)`
:   Query class for CurrentQueueActivity entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CurrentQueueActivitySearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[CurrentQueueActivitySearchData]`
    :   Search current_queue_activity records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CurrentQueueActivitySearchFilter):
        - agents_online: Current number of agents online
        - average_wait_time: Average wait time for callers in queue (seconds)
        - callbacks_waiting: Number of callers in callback queue
        - calls_waiting: Number of callers waiting in queue
        - current_timestamp: Current timestamp
        - embeddable_callbacks_waiting: Number of Web Widget callback requests waiting
        - longest_wait_time: Longest wait time for any caller (seconds)
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CurrentQueueActivitySearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult[CurrentQueueActivity]`
    :   Returns current queue activity statistics
        
        Returns:
            CurrentQueueActivityListResult

<a id="GreetingCategoriesQuery"></a>

`GreetingCategoriesQuery(connector: ZendeskTalkConnector)`
:   Query class for GreetingCategories entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: GreetingCategoriesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[GreetingCategoriesSearchData]`
    :   Search greeting_categories records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (GreetingCategoriesSearchFilter):
        - id: Greeting category ID
        - name: Name of the greeting category
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            GreetingCategoriesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, greeting_category_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.GreetingCategory`
    :   Retrieves a single greeting category by ID
        
        Args:
            greeting_category_id: ID of the greeting category
            **kwargs: Additional parameters
        
        Returns:
            GreetingCategory

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[GreetingCategory], GreetingCategoriesListResultMeta]`
    :   Returns a list of all greeting categories
        
        Returns:
            GreetingCategoriesListResult

<a id="GreetingsQuery"></a>

`GreetingsQuery(connector: ZendeskTalkConnector)`
:   Query class for Greetings entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: GreetingsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[GreetingsSearchData]`
    :   Search greetings records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (GreetingsSearchFilter):
        - active: Whether the greeting is associated with phone numbers
        - audio_name: Audio file name
        - audio_url: Path to the greeting sound file
        - category_id: ID of the greeting category
        - default: Whether this is a system default greeting
        - default_lang: Whether the greeting has a default language
        - has_sub_settings: Sub-settings for categorized greetings
        - id: Greeting ID
        - ivr_ids: IDs of IVRs associated with the greeting
        - name: Name of the greeting
        - pending: Whether the greeting is pending
        - phone_number_ids: IDs of phone numbers associated with the greeting
        - upload_id: Upload ID associated with the greeting
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            GreetingsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, greeting_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.Greeting`
    :   Retrieves a single greeting by ID
        
        Args:
            greeting_id: ID of the greeting
            **kwargs: Additional parameters
        
        Returns:
            Greeting

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[Greeting], GreetingsListResultMeta]`
    :   Returns a list of all greetings in the Zendesk Talk account
        
        Returns:
            GreetingsListResult

<a id="IvrsQuery"></a>

`IvrsQuery(connector: ZendeskTalkConnector)`
:   Query class for Ivrs entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: IvrsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[IvrsSearchData]`
    :   Search ivrs records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IvrsSearchFilter):
        - id: IVR ID
        - menus: List of IVR menus
        - name: Name of the IVR
        - phone_number_ids: IDs of phone numbers configured with this IVR
        - phone_number_names: Names of phone numbers configured with this IVR
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            IvrsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, ivr_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.Ivr`
    :   Retrieves a single IVR configuration by ID
        
        Args:
            ivr_id: ID of the IVR
            **kwargs: Additional parameters
        
        Returns:
            Ivr

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[Ivr], IvrsListResultMeta]`
    :   Returns a list of all IVR configurations
        
        Returns:
            IvrsListResult

<a id="PhoneNumbersQuery"></a>

`PhoneNumbersQuery(connector: ZendeskTalkConnector)`
:   Query class for PhoneNumbers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: PhoneNumbersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[PhoneNumbersSearchData]`
    :   Search phone_numbers records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (PhoneNumbersSearchFilter):
        - call_recording_consent: What call recording consent is set to
        - capabilities: Phone number capabilities (sms, mms, voice)
        - categorised_greetings: Greeting category IDs and names
        - categorised_greetings_with_sub_settings: Greeting categories with associated settings
        - country_code: ISO country code for the number
        - created_at: Date and time the phone number was created
        - default_greeting_ids: Names of default system greetings
        - default_group_id: Default group ID
        - display_number: Formatted phone number
        - external: Whether this is an external caller ID number
        - failover_number: Failover number associated with the phone number
        - greeting_ids: Custom greeting IDs associated with the phone number
        - group_ids: Array of associated group IDs
        - id: Unique phone number identifier
        - ivr_id: ID of IVR associated with the phone number
        - line_type: Type of line (phone or digital)
        - location: Geographical location of the number
        - name: Nickname if set, otherwise the display number
        - nickname: Nickname of the phone number
        - number: Phone number digits
        - outbound_enabled: Whether outbound calls are enabled
        - priority: Priority level of the phone number
        - recorded: Whether calls are recorded
        - schedule_id: ID of schedule associated with the phone number
        - sms_enabled: Whether SMS is enabled
        - sms_group_id: Group associated with SMS
        - token: Generated token unique for the phone number
        - toll_free: Whether the number is toll-free
        - transcription: Whether voicemail transcription is enabled
        - voice_enabled: Whether voice is enabled
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            PhoneNumbersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, phone_number_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.PhoneNumber`
    :   Retrieves a single phone number by ID
        
        Args:
            phone_number_id: ID of the phone number
            **kwargs: Additional parameters
        
        Returns:
            PhoneNumber

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[PhoneNumber], PhoneNumbersListResultMeta]`
    :   Returns a list of all phone numbers in the Zendesk Talk account
        
        Returns:
            PhoneNumbersListResult

<a id="ZendeskTalkConnector"></a>

`ZendeskTalkConnector(auth_config: ZendeskTalkAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, subdomain: str | None = None)`
:   Type-safe Zendesk-Talk API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new zendesk-talk connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., ZendeskTalkAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            subdomain: Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)
    Examples:
        # Local mode (direct API calls)
        connector = ZendeskTalkConnector(auth_config=ZendeskTalkAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = ZendeskTalkConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = ZendeskTalkConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'ZendeskTalkAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'ZendeskTalkReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A ZendeskTalkConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await ZendeskTalkConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ZendeskTalkAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."),
            )
        
            # With replication config (required for this connector):
            connector = await ZendeskTalkConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ZendeskTalkAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."),
                replication_config=ZendeskTalkReplicationConfig(start_date="..."),
            )
        
            # With server-side OAuth:
            connector = await ZendeskTalkConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=ZendeskTalkReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'ZendeskTalkReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await ZendeskTalkConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Zendesk-Talk Source",
                replication_config=ZendeskTalkReplicationConfig(start_date="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @ZendeskTalkConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ZendeskTalkConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await ZendeskTalkConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            ZendeskTalkCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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