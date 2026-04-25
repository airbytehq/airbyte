---
id: airbyte_agent_sdk-connectors-twilio-connector
title: airbyte_agent_sdk.connectors.twilio.connector
---

Module airbyte_agent_sdk.connectors.twilio.connector
====================================================
Twilio connector.

Classes
-------

<a id="AccountsQuery"></a>

`AccountsQuery(connector: TwilioConnector)`
:   Query class for Accounts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AccountsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[AccountsSearchData]`
    :   Search accounts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AccountsSearchFilter):
        - sid: The unique identifier for the account
        - friendly_name: A user-defined friendly name for the account
        - status: The current status of the account
        - type_: The type of the account
        - owner_account_sid: The SID of the owner account
        - date_created: The timestamp when the account was created
        - date_updated: The timestamp when the account was last updated
        - uri: The URI for accessing the account resource
        
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

    `get(self, sid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.Account`
    :   Get a single account by SID
        
        Args:
            sid: Account SID
            **kwargs: Additional parameters
        
        Returns:
            Account

    `list(self, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Account], AccountsListResultMeta]`
    :   Returns a list of accounts associated with the authenticated account
        
        Args:
            page_size: Number of items to return per page
            **kwargs: Additional parameters
        
        Returns:
            AccountsListResult

<a id="AddressesQuery"></a>

`AddressesQuery(connector: TwilioConnector)`
:   Query class for Addresses entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AddressesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[AddressesSearchData]`
    :   Search addresses records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AddressesSearchFilter):
        - sid: The unique identifier of the address
        - account_sid: The account SID associated with this address
        - customer_name: The customer name associated with this address
        - friendly_name: A friendly name for the address
        - street: The street address
        - city: The city of the address
        - region: The region or state
        - postal_code: The postal code
        - iso_country: The ISO 3166-1 alpha-2 country code
        - validated: Whether the address has been validated
        - verified: Whether the address has been verified
        
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

    `get(self, account_sid: str, sid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.Address`
    :   Get a single address by SID
        
        Args:
            account_sid: Account SID
            sid: Address SID
            **kwargs: Additional parameters
        
        Returns:
            Address

    `list(self, account_sid: str, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Address], AddressesListResultMeta]`
    :   Returns a list of addresses for an account
        
        Args:
            account_sid: Account SID
            page_size: Number of items to return per page
            **kwargs: Additional parameters
        
        Returns:
            AddressesListResult

<a id="CallsQuery"></a>

`CallsQuery(connector: TwilioConnector)`
:   Query class for Calls entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CallsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[CallsSearchData]`
    :   Search calls records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CallsSearchFilter):
        - sid: The unique identifier for the call
        - account_sid: The unique identifier for the account associated with the call
        - to: The phone number that received the call
        - from_: The phone number that made the call
        - status: The current status of the call
        - direction: The direction of the call (inbound or outbound)
        - duration: The duration of the call in seconds
        - price: The cost of the call
        - price_unit: The currency unit of the call cost
        - start_time: The date and time when the call started
        - end_time: The date and time when the call ended
        - date_created: The date and time when the call record was created
        - date_updated: The date and time when the call record was last updated
        
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

    `get(self, account_sid: str, sid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.Call`
    :   Get a single call by SID
        
        Args:
            account_sid: Account SID
            sid: Call SID
            **kwargs: Additional parameters
        
        Returns:
            Call

    `list(self, account_sid: str, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Call], CallsListResultMeta]`
    :   Returns a list of calls made to and from an account
        
        Args:
            account_sid: Account SID
            page_size: Number of items to return per page
            **kwargs: Additional parameters
        
        Returns:
            CallsListResult

<a id="ConferencesQuery"></a>

`ConferencesQuery(connector: TwilioConnector)`
:   Query class for Conferences entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ConferencesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[ConferencesSearchData]`
    :   Search conferences records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ConferencesSearchFilter):
        - sid: The unique identifier of the conference
        - account_sid: The account SID associated with the conference
        - friendly_name: A friendly name for the conference
        - status: The current status of the conference
        - region: The region where the conference is hosted
        - date_created: When the conference was created
        - date_updated: When the conference was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ConferencesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, account_sid: str, sid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.Conference`
    :   Get a single conference by SID
        
        Args:
            account_sid: Account SID
            sid: Conference SID
            **kwargs: Additional parameters
        
        Returns:
            Conference

    `list(self, account_sid: str, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Conference], ConferencesListResultMeta]`
    :   Returns a list of conferences for an account
        
        Args:
            account_sid: Account SID
            page_size: Number of items to return per page
            **kwargs: Additional parameters
        
        Returns:
            ConferencesListResult

<a id="IncomingPhoneNumbersQuery"></a>

`IncomingPhoneNumbersQuery(connector: TwilioConnector)`
:   Query class for IncomingPhoneNumbers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: IncomingPhoneNumbersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[IncomingPhoneNumbersSearchData]`
    :   Search incoming_phone_numbers records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IncomingPhoneNumbersSearchFilter):
        - sid: The SID of this phone number
        - account_sid: The SID of the account that owns this phone number
        - phone_number: The phone number in E.164 format
        - friendly_name: A user-assigned friendly name for this phone number
        - status: Status of the phone number
        - capabilities: Capabilities of this phone number
        - date_created: When the phone number was created
        - date_updated: When the phone number was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            IncomingPhoneNumbersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, account_sid: str, sid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.IncomingPhoneNumber`
    :   Get a single incoming phone number by SID
        
        Args:
            account_sid: Account SID
            sid: Incoming phone number SID
            **kwargs: Additional parameters
        
        Returns:
            IncomingPhoneNumber

    `list(self, account_sid: str, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[IncomingPhoneNumber], IncomingPhoneNumbersListResultMeta]`
    :   Returns a list of incoming phone numbers for an account
        
        Args:
            account_sid: Account SID
            page_size: Number of items to return per page
            **kwargs: Additional parameters
        
        Returns:
            IncomingPhoneNumbersListResult

<a id="MessagesQuery"></a>

`MessagesQuery(connector: TwilioConnector)`
:   Query class for Messages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MessagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[MessagesSearchData]`
    :   Search messages records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MessagesSearchFilter):
        - sid: The unique identifier for this message
        - account_sid: The unique identifier for the account associated with this message
        - to: The phone number or recipient ID the message was sent to
        - from_: The phone number or sender ID that sent the message
        - body: The text body of the message
        - status: The status of the message
        - direction: The direction of the message
        - price: The cost of the message
        - price_unit: The currency unit used for pricing
        - date_created: The date and time when the message was created
        - date_sent: The date and time when the message was sent
        - error_code: The error code associated with the message if any
        - error_message: The error message description if the message failed
        - num_segments: The number of message segments
        - num_media: The number of media files included in the message
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MessagesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, account_sid: str, sid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.Message`
    :   Get a single message by SID
        
        Args:
            account_sid: Account SID
            sid: Message SID
            **kwargs: Additional parameters
        
        Returns:
            Message

    `list(self, account_sid: str, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Message], MessagesListResultMeta]`
    :   Returns a list of messages associated with an account
        
        Args:
            account_sid: Account SID
            page_size: Number of items to return per page
            **kwargs: Additional parameters
        
        Returns:
            MessagesListResult

<a id="OutgoingCallerIdsQuery"></a>

`OutgoingCallerIdsQuery(connector: TwilioConnector)`
:   Query class for OutgoingCallerIds entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OutgoingCallerIdsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[OutgoingCallerIdsSearchData]`
    :   Search outgoing_caller_ids records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OutgoingCallerIdsSearchFilter):
        - sid: The unique identifier
        - account_sid: The account SID
        - phone_number: The phone number
        - friendly_name: A friendly name
        - date_created: When the outgoing caller ID was created
        - date_updated: When the outgoing caller ID was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OutgoingCallerIdsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, account_sid: str, sid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.OutgoingCallerId`
    :   Get a single outgoing caller ID by SID
        
        Args:
            account_sid: Account SID
            sid: Outgoing caller ID SID
            **kwargs: Additional parameters
        
        Returns:
            OutgoingCallerId

    `list(self, account_sid: str, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[OutgoingCallerId], OutgoingCallerIdsListResultMeta]`
    :   Returns a list of outgoing caller IDs for an account
        
        Args:
            account_sid: Account SID
            page_size: Number of items to return per page
            **kwargs: Additional parameters
        
        Returns:
            OutgoingCallerIdsListResult

<a id="QueuesQuery"></a>

`QueuesQuery(connector: TwilioConnector)`
:   Query class for Queues entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: QueuesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[QueuesSearchData]`
    :   Search queues records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (QueuesSearchFilter):
        - sid: The unique identifier for the queue
        - account_sid: The account SID that owns this queue
        - friendly_name: A friendly name for the queue
        - current_size: Current number of callers waiting
        - max_size: Maximum number of callers allowed
        - average_wait_time: Average wait time in seconds
        - date_created: When the queue was created
        - date_updated: When the queue was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            QueuesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, account_sid: str, sid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.Queue`
    :   Get a single queue by SID
        
        Args:
            account_sid: Account SID
            sid: Queue SID
            **kwargs: Additional parameters
        
        Returns:
            Queue

    `list(self, account_sid: str, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Queue], QueuesListResultMeta]`
    :   Returns a list of queues for an account
        
        Args:
            account_sid: Account SID
            page_size: Number of items to return per page
            **kwargs: Additional parameters
        
        Returns:
            QueuesListResult

<a id="RecordingsQuery"></a>

`RecordingsQuery(connector: TwilioConnector)`
:   Query class for Recordings entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: RecordingsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[RecordingsSearchData]`
    :   Search recordings records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (RecordingsSearchFilter):
        - sid: The unique identifier of the recording
        - account_sid: The account SID that owns the recording
        - call_sid: The SID of the associated call
        - duration: Duration in seconds
        - status: The status of the recording
        - channels: Number of audio channels
        - price: The cost of storing the recording
        - price_unit: The currency unit
        - date_created: When the recording was created
        - start_time: When the recording started
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            RecordingsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, account_sid: str, sid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.Recording`
    :   Get a single recording by SID
        
        Args:
            account_sid: Account SID
            sid: Recording SID
            **kwargs: Additional parameters
        
        Returns:
            Recording

    `list(self, account_sid: str, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Recording], RecordingsListResultMeta]`
    :   Returns a list of recordings for an account
        
        Args:
            account_sid: Account SID
            page_size: Number of items to return per page
            **kwargs: Additional parameters
        
        Returns:
            RecordingsListResult

<a id="TranscriptionsQuery"></a>

`TranscriptionsQuery(connector: TwilioConnector)`
:   Query class for Transcriptions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TranscriptionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[TranscriptionsSearchData]`
    :   Search transcriptions records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TranscriptionsSearchFilter):
        - sid: The unique identifier for the transcription
        - account_sid: The account SID
        - recording_sid: The SID of the associated recording
        - status: The status of the transcription
        - duration: Duration of the audio recording in seconds
        - price: The cost of the transcription
        - price_unit: The currency unit
        - date_created: When the transcription was created
        - date_updated: When the transcription was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TranscriptionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, account_sid: str, sid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.Transcription`
    :   Get a single transcription by SID
        
        Args:
            account_sid: Account SID
            sid: Transcription SID
            **kwargs: Additional parameters
        
        Returns:
            Transcription

    `list(self, account_sid: str, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Transcription], TranscriptionsListResultMeta]`
    :   Returns a list of transcriptions for an account
        
        Args:
            account_sid: Account SID
            page_size: Number of items to return per page
            **kwargs: Additional parameters
        
        Returns:
            TranscriptionsListResult

<a id="TwilioConnector"></a>

`TwilioConnector(auth_config: TwilioAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Twilio API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new twilio connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., TwilioAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = TwilioConnector(auth_config=TwilioAuthConfig(account_sid="...", auth_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = TwilioConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = TwilioConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'TwilioAuthConfig'", name: str | None = None, replication_config: "'TwilioReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A TwilioConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await TwilioConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=TwilioAuthConfig(account_sid="...", auth_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await TwilioConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=TwilioAuthConfig(account_sid="...", auth_token="..."),
                replication_config=TwilioReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @TwilioConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @TwilioConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await TwilioConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.twilio.models.TwilioCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            TwilioCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="UsageRecordsQuery"></a>

`UsageRecordsQuery(connector: TwilioConnector)`
:   Query class for UsageRecords entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsageRecordsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[UsageRecordsSearchData]`
    :   Search usage_records records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsageRecordsSearchFilter):
        - account_sid: The account SID associated with this usage record
        - category: The usage category (calls, SMS, recordings, etc.)
        - description: A description of the usage record
        - usage: The total usage value
        - usage_unit: The unit of measurement for usage
        - count: The number of units consumed
        - count_unit: The unit of measurement for count
        - price: The total price for consumed units
        - price_unit: The currency unit
        - start_date: The start date of the usage period
        - end_date: The end date of the usage period
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            UsageRecordsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, account_sid: str, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[UsageRecord], UsageRecordsListResultMeta]`
    :   Returns a list of usage records for an account
        
        Args:
            account_sid: Account SID
            page_size: Number of items to return per page
            **kwargs: Additional parameters
        
        Returns:
            UsageRecordsListResult