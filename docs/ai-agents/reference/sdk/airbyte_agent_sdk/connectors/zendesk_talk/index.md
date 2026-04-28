---
id: airbyte_agent_sdk-connectors-zendesk_talk-index
title: airbyte_agent_sdk.connectors.zendesk_talk.index
---

Module airbyte_agent_sdk.connectors.zendesk_talk
================================================
Zendesk-Talk connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.zendesk_talk.connector
* airbyte_agent_sdk.connectors.zendesk_talk.connector_model
* airbyte_agent_sdk.connectors.zendesk_talk.models
* airbyte_agent_sdk.connectors.zendesk_talk.types

Classes
-------

<a id="AccountOverviewSearchData"></a>

`AccountOverviewSearchData(**data: Any)`
:   Search result data for account_overview entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `average_call_duration: int | None`
    :   Average call duration

    `average_callback_wait_time: int | None`
    :   Average callback wait time

    `average_hold_time: int | None`
    :   Average hold time per call

    `average_queue_wait_time: int | None`
    :   Average queue wait time

    `average_time_to_answer: int | None`
    :   Average time to answer

    `average_wrap_up_time: int | None`
    :   Average wrap-up time

    `current_timestamp: int | None`
    :   Current timestamp

    `max_calls_waiting: int | None`
    :   Max calls waiting in queue

    `max_queue_wait_time: int | None`
    :   Max queue wait time

    `model_config`
    :   The type of the None singleton.

    `total_call_duration: int | None`
    :   Total call duration

    `total_callback_calls: int | None`
    :   Total callback calls

    `total_calls: int | None`
    :   Total calls

    `total_calls_abandoned_in_queue: int | None`
    :   Total calls abandoned in queue

    `total_calls_outside_business_hours: int | None`
    :   Total calls outside business hours

    `total_calls_with_exceeded_queue_wait_time: int | None`
    :   Total calls exceeding max queue wait time

    `total_calls_with_requested_voicemail: int | None`
    :   Total calls requesting voicemail

    `total_embeddable_callback_calls: int | None`
    :   Total embeddable callback calls

    `total_hold_time: int | None`
    :   Total hold time

    `total_inbound_calls: int | None`
    :   Total inbound calls

    `total_outbound_calls: int | None`
    :   Total outbound calls

    `total_textback_requests: int | None`
    :   Total textback requests

    `total_voicemails: int | None`
    :   Total voicemails

    `total_wrap_up_time: int | None`
    :   Total wrap-up time

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

    `city: str | None`
    :   City of the address

    `country_code: str | None`
    :   ISO country code

    `id: int | None`
    :   Unique address identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the address

    `provider_reference: str | None`
    :   Provider reference of the address

    `province: str | None`
    :   Province of the address

    `state: str | None`
    :   State of the address

    `street: str | None`
    :   Street of the address

    `zip: str | None`
    :   Zip code of the address

<a id="AgentsActivitySearchData"></a>

`AgentsActivitySearchData(**data: Any)`
:   Search result data for agents_activity entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accepted_third_party_conferences: int | None`
    :   Accepted third party conferences

    `accepted_transfers: int | None`
    :   Total transfers accepted

    `agent_id: int | None`
    :   Agent ID

    `agent_state: str | None`
    :   Agent state: online, offline, away, or transfers_only

    `available_time: int | None`
    :   Total time agent was available to answer calls

    `avatar_url: str | None`
    :   URL to agent avatar

    `average_hold_time: int | None`
    :   Average hold time per call

    `average_talk_time: int | None`
    :   Average talk time per call

    `average_wrap_up_time: int | None`
    :   Average wrap-up time per call

    `away_time: int | None`
    :   Total time agent was set to away

    `call_status: str | None`
    :   Agent call status: on_call, wrap_up, or null

    `calls_accepted: int | None`
    :   Total calls accepted

    `calls_denied: int | None`
    :   Total calls denied

    `calls_missed: int | None`
    :   Total calls missed

    `calls_put_on_hold: int | None`
    :   Total calls placed on hold

    `forwarding_number: str | None`
    :   Forwarding number set by the agent

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Agent name

    `online_time: int | None`
    :   Total online time

    `started_third_party_conferences: int | None`
    :   Started third party conferences

    `started_transfers: int | None`
    :   Total transfers started

    `total_call_duration: int | None`
    :   Total call duration

    `total_hold_time: int | None`
    :   Total hold time across all calls

    `total_talk_time: int | None`
    :   Total talk time (excludes hold)

    `total_wrap_up_time: int | None`
    :   Total wrap-up time

    `transfers_only_time: int | None`
    :   Total time in transfers-only mode

    `via: str | None`
    :   Channel the agent is registered on

<a id="AgentsOverviewSearchData"></a>

`AgentsOverviewSearchData(**data: Any)`
:   Search result data for agents_overview entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `average_accepted_transfers: int | None`
    :   Average accepted transfers

    `average_available_time: int | None`
    :   Average available time

    `average_away_time: int | None`
    :   Average away time

    `average_calls_accepted: int | None`
    :   Average calls accepted

    `average_calls_denied: int | None`
    :   Average calls denied

    `average_calls_missed: int | None`
    :   Average calls missed

    `average_calls_put_on_hold: int | None`
    :   Average calls put on hold

    `average_hold_time: int | None`
    :   Average hold time

    `average_online_time: int | None`
    :   Average online time

    `average_started_transfers: int | None`
    :   Average started transfers

    `average_talk_time: int | None`
    :   Average talk time

    `average_transfers_only_time: int | None`
    :   Average transfers-only time

    `average_wrap_up_time: int | None`
    :   Average wrap-up time

    `current_timestamp: int | None`
    :   Current timestamp

    `model_config`
    :   The type of the None singleton.

    `total_accepted_transfers: int | None`
    :   Total accepted transfers

    `total_calls_accepted: int | None`
    :   Total calls accepted

    `total_calls_denied: int | None`
    :   Total calls denied

    `total_calls_missed: int | None`
    :   Total calls missed

    `total_calls_put_on_hold: int | None`
    :   Total calls put on hold

    `total_hold_time: int | None`
    :   Total hold time

    `total_started_transfers: int | None`
    :   Total started transfers

    `total_talk_time: int | None`
    :   Total talk time

    `total_wrap_up_time: int | None`
    :   Total wrap-up time

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

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[AccountOverviewSearchData]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[AddressesSearchData]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[AgentsActivitySearchData]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[AgentsOverviewSearchData]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[CallLegsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[CallsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[CurrentQueueActivitySearchData]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[GreetingCategoriesSearchData]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[GreetingsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[IvrsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult[PhoneNumbersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="AccountOverviewSearchResult"></a>

`AccountOverviewSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AgentsActivitySearchResult"></a>

`AgentsActivitySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AgentsOverviewSearchResult"></a>

`AgentsOverviewSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CallLegsSearchResult"></a>

`CallLegsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CurrentQueueActivitySearchResult"></a>

`CurrentQueueActivitySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GreetingCategoriesSearchResult"></a>

`GreetingCategoriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GreetingsSearchResult"></a>

`GreetingsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="IvrsSearchResult"></a>

`IvrsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="PhoneNumbersSearchResult"></a>

`PhoneNumbersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CallLegsSearchData"></a>

`CallLegsSearchData(**data: Any)`
:   Search result data for call_legs entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_id: int | None`
    :   Agent ID

    `available_via: str | None`
    :   Channel agent was available through

    `call_charge: str | None`
    :   Call charge amount

    `call_id: int | None`
    :   Associated call ID

    `completion_status: str | None`
    :   Completion status

    `conference_from: int | None`
    :   Conference from time

    `conference_time: int | None`
    :   Conference duration

    `conference_to: int | None`
    :   Conference to time

    `consultation_from: int | None`
    :   Consultation from time

    `consultation_time: int | None`
    :   Consultation duration

    `consultation_to: int | None`
    :   Consultation to time

    `created_at: str | None`
    :   Creation timestamp

    `duration: int | None`
    :   Duration in seconds

    `forwarded_to: str | None`
    :   Number forwarded to

    `hold_time: int | None`
    :   Hold time in seconds

    `id: int | None`
    :   Call leg ID

    `minutes_billed: int | None`
    :   Minutes billed

    `model_config`
    :   The type of the None singleton.

    `quality_issues: list[typing.Any] | None`
    :   Quality issues detected

    `talk_time: int | None`
    :   Talk time in seconds

    `transferred_from: int | None`
    :   Transferred from agent ID

    `transferred_to: int | None`
    :   Transferred to agent ID

    `type_: str | None`
    :   Type of call leg

    `updated_at: str | None`
    :   Last update timestamp

    `user_id: int | None`
    :   User ID

    `wrap_up_time: int | None`
    :   Wrap-up time in seconds

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

    `agent_id: int | None`
    :   Agent ID

    `call_charge: str | None`
    :   Call charge amount

    `call_group_id: int | None`
    :   Call group ID

    `call_recording_consent: str | None`
    :   Call recording consent status

    `call_recording_consent_action: str | None`
    :   Recording consent action

    `call_recording_consent_keypress: str | None`
    :   Recording consent keypress

    `callback: bool | None`
    :   Whether this was a callback

    `callback_source: str | None`
    :   Source of the callback

    `completion_status: str | None`
    :   Call completion status

    `consultation_time: int | None`
    :   Consultation time

    `created_at: str | None`
    :   Creation timestamp

    `customer_requested_voicemail: bool | None`
    :   Whether customer requested voicemail

    `default_group: bool | None`
    :   Whether default group was used

    `direction: str | None`
    :   Call direction (inbound/outbound)

    `duration: int | None`
    :   Call duration in seconds

    `exceeded_queue_time: bool | None`
    :   Whether queue time was exceeded

    `exceeded_queue_wait_time: bool | None`
    :   Whether max queue wait time was exceeded

    `hold_time: int | None`
    :   Hold time in seconds

    `id: int | None`
    :   Call ID

    `ivr_action: str | None`
    :   IVR action taken

    `ivr_destination_group_name: str | None`
    :   IVR destination group name

    `ivr_hops: int | None`
    :   Number of IVR hops

    `ivr_routed_to: str | None`
    :   Where IVR routed the call

    `ivr_time_spent: int | None`
    :   Time spent in IVR

    `minutes_billed: int | None`
    :   Minutes billed

    `model_config`
    :   The type of the None singleton.

    `not_recording_time: int | None`
    :   Time not recording

    `outside_business_hours: bool | None`
    :   Whether call was outside business hours

    `overflowed: bool | None`
    :   Whether call overflowed

    `overflowed_to: str | None`
    :   Where call overflowed to

    `phone_number: str | None`
    :   Phone number used

    `phone_number_id: int | None`
    :   Phone number ID

    `quality_issues: list[typing.Any] | None`
    :   Quality issues detected

    `recording_control_interactions: int | None`
    :   Recording control interactions count

    `recording_time: int | None`
    :   Recording time

    `talk_time: int | None`
    :   Talk time in seconds

    `ticket_id: int | None`
    :   Associated ticket ID

    `time_to_answer: int | None`
    :   Time to answer in seconds

    `updated_at: str | None`
    :   Last update timestamp

    `voicemail: bool | None`
    :   Whether it was a voicemail

    `wait_time: int | None`
    :   Wait time in seconds

    `wrap_up_time: int | None`
    :   Wrap-up time in seconds

<a id="CurrentQueueActivitySearchData"></a>

`CurrentQueueActivitySearchData(**data: Any)`
:   Search result data for current_queue_activity entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agents_online: int | None`
    :   Current number of agents online

    `average_wait_time: int | None`
    :   Average wait time for callers in queue (seconds)

    `callbacks_waiting: int | None`
    :   Number of callers in callback queue

    `calls_waiting: int | None`
    :   Number of callers waiting in queue

    `current_timestamp: int | None`
    :   Current timestamp

    `embeddable_callbacks_waiting: int | None`
    :   Number of Web Widget callback requests waiting

    `longest_wait_time: int | None`
    :   Longest wait time for any caller (seconds)

    `model_config`
    :   The type of the None singleton.

<a id="GreetingCategoriesSearchData"></a>

`GreetingCategoriesSearchData(**data: Any)`
:   Search result data for greeting_categories entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | None`
    :   Greeting category ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the greeting category

<a id="GreetingsSearchData"></a>

`GreetingsSearchData(**data: Any)`
:   Search result data for greetings entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | None`
    :   Whether the greeting is associated with phone numbers

    `audio_name: str | None`
    :   Audio file name

    `audio_url: str | None`
    :   Path to the greeting sound file

    `category_id: int | None`
    :   ID of the greeting category

    `default: bool | None`
    :   Whether this is a system default greeting

    `default_lang: bool | None`
    :   Whether the greeting has a default language

    `has_sub_settings: bool | None`
    :   Sub-settings for categorized greetings

    `id: str | None`
    :   Greeting ID

    `ivr_ids: list[typing.Any] | None`
    :   IDs of IVRs associated with the greeting

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the greeting

    `pending: bool | None`
    :   Whether the greeting is pending

    `phone_number_ids: list[typing.Any] | None`
    :   IDs of phone numbers associated with the greeting

    `upload_id: int | None`
    :   Upload ID associated with the greeting

<a id="IvrsSearchData"></a>

`IvrsSearchData(**data: Any)`
:   Search result data for ivrs entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | None`
    :   IVR ID

    `menus: list[typing.Any] | None`
    :   List of IVR menus

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the IVR

    `phone_number_ids: list[typing.Any] | None`
    :   IDs of phone numbers configured with this IVR

    `phone_number_names: list[typing.Any] | None`
    :   Names of phone numbers configured with this IVR

<a id="PhoneNumbersSearchData"></a>

`PhoneNumbersSearchData(**data: Any)`
:   Search result data for phone_numbers entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `call_recording_consent: str | None`
    :   What call recording consent is set to

    `capabilities: dict[str, typing.Any] | None`
    :   Phone number capabilities (sms, mms, voice)

    `categorised_greetings: dict[str, typing.Any] | None`
    :   Greeting category IDs and names

    `categorised_greetings_with_sub_settings: dict[str, typing.Any] | None`
    :   Greeting categories with associated settings

    `country_code: str | None`
    :   ISO country code for the number

    `created_at: str | None`
    :   Date and time the phone number was created

    `default_greeting_ids: list[typing.Any] | None`
    :   Names of default system greetings

    `default_group_id: int | None`
    :   Default group ID

    `display_number: str | None`
    :   Formatted phone number

    `external: bool | None`
    :   Whether this is an external caller ID number

    `failover_number: str | None`
    :   Failover number associated with the phone number

    `greeting_ids: list[typing.Any] | None`
    :   Custom greeting IDs associated with the phone number

    `group_ids: list[typing.Any] | None`
    :   Array of associated group IDs

    `id: int | None`
    :   Unique phone number identifier

    `ivr_id: int | None`
    :   ID of IVR associated with the phone number

    `line_type: str | None`
    :   Type of line (phone or digital)

    `location: str | None`
    :   Geographical location of the number

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Nickname if set, otherwise the display number

    `nickname: str | None`
    :   Nickname of the phone number

    `number: str | None`
    :   Phone number digits

    `outbound_enabled: bool | None`
    :   Whether outbound calls are enabled

    `priority: int | None`
    :   Priority level of the phone number

    `recorded: bool | None`
    :   Whether calls are recorded

    `schedule_id: int | None`
    :   ID of schedule associated with the phone number

    `sms_enabled: bool | None`
    :   Whether SMS is enabled

    `sms_group_id: int | None`
    :   Group associated with SMS

    `token: str | None`
    :   Generated token unique for the phone number

    `toll_free: bool | None`
    :   Whether the number is toll-free

    `transcription: bool | None`
    :   Whether voicemail transcription is enabled

    `voice_enabled: bool | None`
    :   Whether voice is enabled

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

<a id="ZendeskTalkReplicationConfig"></a>

`ZendeskTalkReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Zendesk Talk.
    
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
    :   UTC date and time in the format YYYY-MM-DDT00:00:00Z from which to start replicating data.