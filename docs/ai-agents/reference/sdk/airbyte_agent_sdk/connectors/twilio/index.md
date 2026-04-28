---
id: airbyte_agent_sdk-connectors-twilio-index
title: airbyte_agent_sdk.connectors.twilio.index
---

Module airbyte_agent_sdk.connectors.twilio
==========================================
Twilio connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.twilio.connector
* airbyte_agent_sdk.connectors.twilio.connector_model
* airbyte_agent_sdk.connectors.twilio.models
* airbyte_agent_sdk.connectors.twilio.types

Classes
-------

<a id="AccountsSearchData"></a>

`AccountsSearchData(**data: Any)`
:   Search result data for accounts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date_created: str | None`
    :   The timestamp when the account was created

    `date_updated: str | None`
    :   The timestamp when the account was last updated

    `friendly_name: str | None`
    :   A user-defined friendly name for the account

    `model_config`
    :   The type of the None singleton.

    `owner_account_sid: str | None`
    :   The SID of the owner account

    `sid: str | None`
    :   The unique identifier for the account

    `status: str | None`
    :   The current status of the account

    `type_: str | None`
    :   The type of the account

    `uri: str | None`
    :   The URI for accessing the account resource

<a id="AddressesSearchData"></a>

`AddressesSearchData(**data: Any)`
:   Search result data for addresses entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The account SID associated with this address

    `city: str | None`
    :   The city of the address

    `customer_name: str | None`
    :   The customer name associated with this address

    `friendly_name: str | None`
    :   A friendly name for the address

    `iso_country: str | None`
    :   The ISO 3166-1 alpha-2 country code

    `model_config`
    :   The type of the None singleton.

    `postal_code: str | None`
    :   The postal code

    `region: str | None`
    :   The region or state

    `sid: str | None`
    :   The unique identifier of the address

    `street: str | None`
    :   The street address

    `validated: bool | None`
    :   Whether the address has been validated

    `verified: bool | None`
    :   Whether the address has been verified

<a id="AirbyteAuthConfig"></a>

`AirbyteAuthConfig(**data: Any)`
:   Authentication configuration for Airbyte hosted mode execution.
    
    Pass this to the connector's `auth_config` parameter to use hosted mode,
    where API credentials are stored securely in Airbyte Cloud.
    
    For hosted mode execution, provide client credentials with either:
    - `connector_id`: Direct connector/source ID (skips lookup)
    - `workspace_name`: Workspace name for connector lookup
    
    Attributes:
        workspace_name: Workspace name for hosted mode connector lookup
        organization_id: Optional Airbyte organization ID for multi-org selection
        airbyte_client_id: Airbyte OAuth client ID (required for hosted mode)
        airbyte_client_secret: Airbyte OAuth client secret (required for hosted mode)
        connector_id: Specific connector/source ID (skips lookup if provided)
    
    Examples:
        # Hosted mode with connector_id (no lookup needed)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with workspace_name (lookup by workspace)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `airbyte_client_id: str | None`
    :   The type of the None singleton.

    `airbyte_client_secret: str | None`
    :   The type of the None singleton.

    `connector_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: str | None`
    :   The type of the None singleton.

    `workspace_name: str | None`
    :   The type of the None singleton.

<a id="AirbyteSearchMeta"></a>

`AirbyteSearchMeta(**data: Any)`
:   Pagination metadata for search responses.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   Cursor for fetching the next page of results.

    `has_more: bool`
    :   Whether more results are available.

    `model_config`
    :   The type of the None singleton.

    `took_ms: int | None`
    :   Time taken to execute the search in milliseconds.

<a id="AirbyteSearchResult"></a>

`AirbyteSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[AccountsSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[AddressesSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[CallsSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[ConferencesSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[IncomingPhoneNumbersSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[MessagesSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[OutgoingCallerIdsSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[QueuesSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[RecordingsSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[TranscriptionsSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[UsageRecordsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="AccountsSearchResult"></a>

`AccountsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AddressesSearchResult"></a>

`AddressesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CallsSearchResult"></a>

`CallsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ConferencesSearchResult"></a>

`ConferencesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="IncomingPhoneNumbersSearchResult"></a>

`IncomingPhoneNumbersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MessagesSearchResult"></a>

`MessagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="OutgoingCallerIdsSearchResult"></a>

`OutgoingCallerIdsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="QueuesSearchResult"></a>

`QueuesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="RecordingsSearchResult"></a>

`RecordingsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TranscriptionsSearchResult"></a>

`TranscriptionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="UsageRecordsSearchResult"></a>

`UsageRecordsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CallsSearchData"></a>

`CallsSearchData(**data: Any)`
:   Search result data for calls entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The unique identifier for the account associated with the call

    `date_created: str | None`
    :   The date and time when the call record was created

    `date_updated: str | None`
    :   The date and time when the call record was last updated

    `direction: str | None`
    :   The direction of the call (inbound or outbound)

    `duration: str | None`
    :   The duration of the call in seconds

    `end_time: str | None`
    :   The date and time when the call ended

    `from_: str | None`
    :   The phone number that made the call

    `model_config`
    :   The type of the None singleton.

    `price: str | None`
    :   The cost of the call

    `price_unit: str | None`
    :   The currency unit of the call cost

    `sid: str | None`
    :   The unique identifier for the call

    `start_time: str | None`
    :   The date and time when the call started

    `status: str | None`
    :   The current status of the call

    `to: str | None`
    :   The phone number that received the call

<a id="ConferencesSearchData"></a>

`ConferencesSearchData(**data: Any)`
:   Search result data for conferences entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The account SID associated with the conference

    `date_created: str | None`
    :   When the conference was created

    `date_updated: str | None`
    :   When the conference was last updated

    `friendly_name: str | None`
    :   A friendly name for the conference

    `model_config`
    :   The type of the None singleton.

    `region: str | None`
    :   The region where the conference is hosted

    `sid: str | None`
    :   The unique identifier of the conference

    `status: str | None`
    :   The current status of the conference

<a id="IncomingPhoneNumbersSearchData"></a>

`IncomingPhoneNumbersSearchData(**data: Any)`
:   Search result data for incoming_phone_numbers entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The SID of the account that owns this phone number

    `capabilities: dict[str, typing.Any] | None`
    :   Capabilities of this phone number

    `date_created: str | None`
    :   When the phone number was created

    `date_updated: str | None`
    :   When the phone number was last updated

    `friendly_name: str | None`
    :   A user-assigned friendly name for this phone number

    `model_config`
    :   The type of the None singleton.

    `phone_number: str | None`
    :   The phone number in E.164 format

    `sid: str | None`
    :   The SID of this phone number

    `status: str | None`
    :   Status of the phone number

<a id="MessagesSearchData"></a>

`MessagesSearchData(**data: Any)`
:   Search result data for messages entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The unique identifier for the account associated with this message

    `body: str | None`
    :   The text body of the message

    `date_created: str | None`
    :   The date and time when the message was created

    `date_sent: str | None`
    :   The date and time when the message was sent

    `direction: str | None`
    :   The direction of the message

    `error_code: str | None`
    :   The error code associated with the message if any

    `error_message: str | None`
    :   The error message description if the message failed

    `from_: str | None`
    :   The phone number or sender ID that sent the message

    `model_config`
    :   The type of the None singleton.

    `num_media: str | None`
    :   The number of media files included in the message

    `num_segments: str | None`
    :   The number of message segments

    `price: str | None`
    :   The cost of the message

    `price_unit: str | None`
    :   The currency unit used for pricing

    `sid: str | None`
    :   The unique identifier for this message

    `status: str | None`
    :   The status of the message

    `to: str | None`
    :   The phone number or recipient ID the message was sent to

<a id="OutgoingCallerIdsSearchData"></a>

`OutgoingCallerIdsSearchData(**data: Any)`
:   Search result data for outgoing_caller_ids entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The account SID

    `date_created: str | None`
    :   When the outgoing caller ID was created

    `date_updated: str | None`
    :   When the outgoing caller ID was last updated

    `friendly_name: str | None`
    :   A friendly name

    `model_config`
    :   The type of the None singleton.

    `phone_number: str | None`
    :   The phone number

    `sid: str | None`
    :   The unique identifier

<a id="QueuesSearchData"></a>

`QueuesSearchData(**data: Any)`
:   Search result data for queues entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The account SID that owns this queue

    `average_wait_time: int | None`
    :   Average wait time in seconds

    `current_size: int | None`
    :   Current number of callers waiting

    `date_created: str | None`
    :   When the queue was created

    `date_updated: str | None`
    :   When the queue was last updated

    `friendly_name: str | None`
    :   A friendly name for the queue

    `max_size: int | None`
    :   Maximum number of callers allowed

    `model_config`
    :   The type of the None singleton.

    `sid: str | None`
    :   The unique identifier for the queue

<a id="RecordingsSearchData"></a>

`RecordingsSearchData(**data: Any)`
:   Search result data for recordings entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The account SID that owns the recording

    `call_sid: str | None`
    :   The SID of the associated call

    `channels: int | None`
    :   Number of audio channels

    `date_created: str | None`
    :   When the recording was created

    `duration: str | None`
    :   Duration in seconds

    `model_config`
    :   The type of the None singleton.

    `price: str | None`
    :   The cost of storing the recording

    `price_unit: str | None`
    :   The currency unit

    `sid: str | None`
    :   The unique identifier of the recording

    `start_time: str | None`
    :   When the recording started

    `status: str | None`
    :   The status of the recording

<a id="TranscriptionsSearchData"></a>

`TranscriptionsSearchData(**data: Any)`
:   Search result data for transcriptions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The account SID

    `date_created: str | None`
    :   When the transcription was created

    `date_updated: str | None`
    :   When the transcription was last updated

    `duration: str | None`
    :   Duration of the audio recording in seconds

    `model_config`
    :   The type of the None singleton.

    `price: str | None`
    :   The cost of the transcription

    `price_unit: str | None`
    :   The currency unit

    `recording_sid: str | None`
    :   The SID of the associated recording

    `sid: str | None`
    :   The unique identifier for the transcription

    `status: str | None`
    :   The status of the transcription

<a id="TwilioAuthConfig"></a>

`TwilioAuthConfig(**data: Any)`
:   Twilio Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str`
    :   Your Twilio Account SID (starts with AC)

    `auth_token: str`
    :   Your Twilio Auth Token

    `model_config`
    :   The type of the None singleton.

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

<a id="TwilioReplicationConfig"></a>

`TwilioReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Twilio.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ. Any data before this date will not be replicated.

<a id="UsageRecordsSearchData"></a>

`UsageRecordsSearchData(**data: Any)`
:   Search result data for usage_records entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The account SID associated with this usage record

    `category: str | None`
    :   The usage category (calls, SMS, recordings, etc.)

    `count: str | None`
    :   The number of units consumed

    `count_unit: str | None`
    :   The unit of measurement for count

    `description: str | None`
    :   A description of the usage record

    `end_date: str | None`
    :   The end date of the usage period

    `model_config`
    :   The type of the None singleton.

    `price: str | None`
    :   The total price for consumed units

    `price_unit: str | None`
    :   The currency unit

    `start_date: str | None`
    :   The start date of the usage period

    `usage: str | None`
    :   The total usage value

    `usage_unit: str | None`
    :   The unit of measurement for usage