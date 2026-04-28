---
id: airbyte_agent_sdk-connectors-zendesk_talk-models
title: airbyte_agent_sdk.connectors.zendesk_talk.models
---

Module airbyte_agent_sdk.connectors.zendesk_talk.models
=======================================================
Pydantic models for zendesk-talk connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="AccountOverview"></a>

`AccountOverview(**data: Any)`
:   AccountOverview type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `average_call_duration: int | Any | None`
    :   The type of the None singleton.

    `average_callback_wait_time: int | Any | None`
    :   The type of the None singleton.

    `average_hold_time: int | Any | None`
    :   The type of the None singleton.

    `average_queue_wait_time: int | Any | None`
    :   The type of the None singleton.

    `average_time_to_answer: int | Any | None`
    :   The type of the None singleton.

    `average_wrap_up_time: int | Any | None`
    :   The type of the None singleton.

    `current_timestamp: int | Any | None`
    :   The type of the None singleton.

    `max_calls_waiting: int | Any | None`
    :   The type of the None singleton.

    `max_queue_wait_time: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_call_duration: int | Any | None`
    :   The type of the None singleton.

    `total_callback_calls: int | Any | None`
    :   The type of the None singleton.

    `total_calls: int | Any | None`
    :   The type of the None singleton.

    `total_calls_abandoned_in_queue: int | Any | None`
    :   The type of the None singleton.

    `total_calls_outside_business_hours: int | Any | None`
    :   The type of the None singleton.

    `total_calls_with_exceeded_queue_wait_time: int | Any | None`
    :   The type of the None singleton.

    `total_calls_with_requested_voicemail: int | Any | None`
    :   The type of the None singleton.

    `total_embeddable_callback_calls: int | Any | None`
    :   The type of the None singleton.

    `total_hold_time: int | Any | None`
    :   The type of the None singleton.

    `total_inbound_calls: int | Any | None`
    :   The type of the None singleton.

    `total_outbound_calls: int | Any | None`
    :   The type of the None singleton.

    `total_textback_requests: int | Any | None`
    :   The type of the None singleton.

    `total_voicemails: int | Any | None`
    :   The type of the None singleton.

    `total_wrap_up_time: int | Any | None`
    :   The type of the None singleton.

<a id="AccountOverviewResponse"></a>

`AccountOverviewResponse(**data: Any)`
:   AccountOverviewResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_overview: airbyte_agent_sdk.connectors.zendesk_talk.models.AccountOverview | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

<a id="Address"></a>

`Address(**data: Any)`
:   Address type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `city: str | Any | None`
    :   The type of the None singleton.

    `country_code: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `provider_reference: str | Any | None`
    :   The type of the None singleton.

    `province: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

    `street: str | Any | None`
    :   The type of the None singleton.

    `zip: str | Any | None`
    :   The type of the None singleton.

<a id="AddressWrapper"></a>

`AddressWrapper(**data: Any)`
:   AddressWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: airbyte_agent_sdk.connectors.zendesk_talk.models.Address | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AddressesList"></a>

`AddressesList(**data: Any)`
:   AddressesList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `addresses: list[airbyte_agent_sdk.connectors.zendesk_talk.models.Address] | Any`
    :   The type of the None singleton.

    `count: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="AddressesListResultMeta"></a>

`AddressesListResultMeta(**data: Any)`
:   Metadata for addresses.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

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

<a id="AgentActivity"></a>

`AgentActivity(**data: Any)`
:   AgentActivity type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accepted_third_party_conferences: int | Any | None`
    :   The type of the None singleton.

    `accepted_transfers: int | Any | None`
    :   The type of the None singleton.

    `agent_id: int | Any | None`
    :   The type of the None singleton.

    `agent_state: str | Any | None`
    :   The type of the None singleton.

    `available_time: int | Any | None`
    :   The type of the None singleton.

    `avatar_url: str | Any | None`
    :   The type of the None singleton.

    `average_hold_time: int | Any | None`
    :   The type of the None singleton.

    `average_talk_time: int | Any | None`
    :   The type of the None singleton.

    `average_wrap_up_time: int | Any | None`
    :   The type of the None singleton.

    `away_time: int | Any | None`
    :   The type of the None singleton.

    `call_status: str | Any | None`
    :   The type of the None singleton.

    `calls_accepted: int | Any | None`
    :   The type of the None singleton.

    `calls_denied: int | Any | None`
    :   The type of the None singleton.

    `calls_missed: int | Any | None`
    :   The type of the None singleton.

    `calls_put_on_hold: int | Any | None`
    :   The type of the None singleton.

    `forwarding_number: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `online_time: int | Any | None`
    :   The type of the None singleton.

    `started_third_party_conferences: int | Any | None`
    :   The type of the None singleton.

    `started_transfers: int | Any | None`
    :   The type of the None singleton.

    `total_call_duration: int | Any | None`
    :   The type of the None singleton.

    `total_hold_time: int | Any | None`
    :   The type of the None singleton.

    `total_talk_time: int | Any | None`
    :   The type of the None singleton.

    `total_wrap_up_time: int | Any | None`
    :   The type of the None singleton.

    `transfers_only_time: int | Any | None`
    :   The type of the None singleton.

    `via: str | Any | None`
    :   The type of the None singleton.

<a id="AgentsActivityList"></a>

`AgentsActivityList(**data: Any)`
:   AgentsActivityList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agents_activity: list[airbyte_agent_sdk.connectors.zendesk_talk.models.AgentActivity] | Any`
    :   The type of the None singleton.

    `count: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="AgentsActivityListResultMeta"></a>

`AgentsActivityListResultMeta(**data: Any)`
:   Metadata for agents_activity.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

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

<a id="AgentsOverview"></a>

`AgentsOverview(**data: Any)`
:   AgentsOverview type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `average_accepted_transfers: int | Any | None`
    :   The type of the None singleton.

    `average_available_time: int | Any | None`
    :   The type of the None singleton.

    `average_away_time: int | Any | None`
    :   The type of the None singleton.

    `average_calls_accepted: int | Any | None`
    :   The type of the None singleton.

    `average_calls_denied: int | Any | None`
    :   The type of the None singleton.

    `average_calls_missed: int | Any | None`
    :   The type of the None singleton.

    `average_calls_put_on_hold: int | Any | None`
    :   The type of the None singleton.

    `average_hold_time: int | Any | None`
    :   The type of the None singleton.

    `average_online_time: int | Any | None`
    :   The type of the None singleton.

    `average_started_transfers: int | Any | None`
    :   The type of the None singleton.

    `average_talk_time: int | Any | None`
    :   The type of the None singleton.

    `average_transfers_only_time: int | Any | None`
    :   The type of the None singleton.

    `average_wrap_up_time: int | Any | None`
    :   The type of the None singleton.

    `current_timestamp: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_accepted_transfers: int | Any | None`
    :   The type of the None singleton.

    `total_calls_accepted: int | Any | None`
    :   The type of the None singleton.

    `total_calls_denied: int | Any | None`
    :   The type of the None singleton.

    `total_calls_missed: int | Any | None`
    :   The type of the None singleton.

    `total_calls_put_on_hold: int | Any | None`
    :   The type of the None singleton.

    `total_hold_time: int | Any | None`
    :   The type of the None singleton.

    `total_started_transfers: int | Any | None`
    :   The type of the None singleton.

    `total_talk_time: int | Any | None`
    :   The type of the None singleton.

    `total_wrap_up_time: int | Any | None`
    :   The type of the None singleton.

<a id="AgentsOverviewResponse"></a>

`AgentsOverviewResponse(**data: Any)`
:   AgentsOverviewResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agents_overview: airbyte_agent_sdk.connectors.zendesk_talk.models.AgentsOverview | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[AccountOverviewSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

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

`AirbyteSearchResult[AddressesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[AgentsActivitySearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[AgentsOverviewSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[CallLegsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[CallsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[CurrentQueueActivitySearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[GreetingCategoriesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[GreetingsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[IvrsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[PhoneNumbersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

<a id="Call"></a>

`Call(**data: Any)`
:   Call type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_id: int | Any | None`
    :   The type of the None singleton.

    `call_channel: str | Any | None`
    :   The type of the None singleton.

    `call_charge: str | Any | None`
    :   The type of the None singleton.

    `call_group_id: int | Any | None`
    :   The type of the None singleton.

    `call_recording_consent: str | Any | None`
    :   The type of the None singleton.

    `call_recording_consent_action: str | Any | None`
    :   The type of the None singleton.

    `call_recording_consent_keypress: str | Any | None`
    :   The type of the None singleton.

    `callback: bool | Any | None`
    :   The type of the None singleton.

    `callback_source: str | Any | None`
    :   The type of the None singleton.

    `completion_status: str | Any | None`
    :   The type of the None singleton.

    `consultation_time: int | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `customer_id: int | Any | None`
    :   The type of the None singleton.

    `customer_requested_voicemail: bool | Any | None`
    :   The type of the None singleton.

    `default_group: bool | Any | None`
    :   The type of the None singleton.

    `direction: str | Any | None`
    :   The type of the None singleton.

    `duration: int | Any | None`
    :   The type of the None singleton.

    `exceeded_queue_time: bool | Any | None`
    :   The type of the None singleton.

    `exceeded_queue_wait_time: bool | Any | None`
    :   The type of the None singleton.

    `hold_time: int | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `ivr_action: str | Any | None`
    :   The type of the None singleton.

    `ivr_destination_group_name: str | Any | None`
    :   The type of the None singleton.

    `ivr_hops: int | Any | None`
    :   The type of the None singleton.

    `ivr_routed_to: str | Any | None`
    :   The type of the None singleton.

    `ivr_time_spent: int | Any | None`
    :   The type of the None singleton.

    `line: str | Any | None`
    :   The type of the None singleton.

    `line_id: int | Any | None`
    :   The type of the None singleton.

    `line_type: str | Any | None`
    :   The type of the None singleton.

    `minutes_billed: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `not_recording_time: int | Any | None`
    :   The type of the None singleton.

    `outside_business_hours: bool | Any | None`
    :   The type of the None singleton.

    `overflowed: bool | Any | None`
    :   The type of the None singleton.

    `overflowed_to: str | Any | None`
    :   The type of the None singleton.

    `phone_number: str | Any | None`
    :   The type of the None singleton.

    `phone_number_id: int | Any | None`
    :   The type of the None singleton.

    `post_call_summary_created: bool | Any | None`
    :   The type of the None singleton.

    `post_call_transcription_created: bool | Any | None`
    :   The type of the None singleton.

    `quality_issues: list[str] | Any | None`
    :   The type of the None singleton.

    `recording_control_interactions: int | Any | None`
    :   The type of the None singleton.

    `recording_time: int | Any | None`
    :   The type of the None singleton.

    `talk_time: int | Any | None`
    :   The type of the None singleton.

    `ticket_id: int | Any | None`
    :   The type of the None singleton.

    `time_to_answer: int | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `voicemail: bool | Any | None`
    :   The type of the None singleton.

    `wait_time: int | Any | None`
    :   The type of the None singleton.

    `wrap_up_time: int | Any | None`
    :   The type of the None singleton.

<a id="CallLeg"></a>

`CallLeg(**data: Any)`
:   CallLeg type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_id: int | Any | None`
    :   The type of the None singleton.

    `available_via: str | Any | None`
    :   The type of the None singleton.

    `call_charge: str | Any | None`
    :   The type of the None singleton.

    `call_id: int | Any | None`
    :   The type of the None singleton.

    `completion_status: str | Any | None`
    :   The type of the None singleton.

    `conference_from: int | Any | None`
    :   The type of the None singleton.

    `conference_time: int | Any | None`
    :   The type of the None singleton.

    `conference_to: int | Any | None`
    :   The type of the None singleton.

    `consultation_from: int | Any | None`
    :   The type of the None singleton.

    `consultation_time: int | Any | None`
    :   The type of the None singleton.

    `consultation_to: int | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `duration: int | Any | None`
    :   The type of the None singleton.

    `forwarded_to: str | Any | None`
    :   The type of the None singleton.

    `hold_time: int | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `minutes_billed: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `quality_issues: list[str] | Any | None`
    :   The type of the None singleton.

    `talk_time: int | Any | None`
    :   The type of the None singleton.

    `transferred_from: int | Any | None`
    :   The type of the None singleton.

    `transferred_to: int | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `user_id: int | Any | None`
    :   The type of the None singleton.

    `wrap_up_time: int | Any | None`
    :   The type of the None singleton.

<a id="CallLegsList"></a>

`CallLegsList(**data: Any)`
:   CallLegsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any | None`
    :   The type of the None singleton.

    `end_time: int | Any | None`
    :   The type of the None singleton.

    `legs: list[airbyte_agent_sdk.connectors.zendesk_talk.models.CallLeg] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

<a id="CallLegsListResultMeta"></a>

`CallLegsListResultMeta(**data: Any)`
:   Metadata for call_legs.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

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

<a id="CallsList"></a>

`CallsList(**data: Any)`
:   CallsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `calls: list[airbyte_agent_sdk.connectors.zendesk_talk.models.Call] | Any`
    :   The type of the None singleton.

    `count: int | Any | None`
    :   The type of the None singleton.

    `end_time: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

<a id="CallsListResultMeta"></a>

`CallsListResultMeta(**data: Any)`
:   Metadata for calls.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

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

<a id="CurrentQueueActivity"></a>

`CurrentQueueActivity(**data: Any)`
:   CurrentQueueActivity type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agents_online: int | Any | None`
    :   The type of the None singleton.

    `ai_agent_calls: int | Any | None`
    :   The type of the None singleton.

    `average_wait_time: int | Any | None`
    :   The type of the None singleton.

    `callbacks_waiting: int | Any | None`
    :   The type of the None singleton.

    `calls_waiting: int | Any | None`
    :   The type of the None singleton.

    `current_timestamp: int | Any | None`
    :   The type of the None singleton.

    `embeddable_callbacks_waiting: int | Any | None`
    :   The type of the None singleton.

    `longest_wait_time: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CurrentQueueActivityResponse"></a>

`CurrentQueueActivityResponse(**data: Any)`
:   CurrentQueueActivityResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `current_queue_activity: airbyte_agent_sdk.connectors.zendesk_talk.models.CurrentQueueActivity | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

<a id="Greeting"></a>

`Greeting(**data: Any)`
:   Greeting type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any | None`
    :   The type of the None singleton.

    `audio_name: str | Any | None`
    :   The type of the None singleton.

    `audio_url: str | Any | None`
    :   The type of the None singleton.

    `category_id: int | Any | None`
    :   The type of the None singleton.

    `default: bool | Any | None`
    :   The type of the None singleton.

    `default_lang: bool | Any | None`
    :   The type of the None singleton.

    `has_sub_settings: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `ivr_ids: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `pending: bool | Any | None`
    :   The type of the None singleton.

    `phone_number_ids: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `upload_id: int | Any | None`
    :   The type of the None singleton.

<a id="GreetingCategoriesList"></a>

`GreetingCategoriesList(**data: Any)`
:   GreetingCategoriesList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any | None`
    :   The type of the None singleton.

    `greeting_categories: list[airbyte_agent_sdk.connectors.zendesk_talk.models.GreetingCategory] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="GreetingCategoriesListResultMeta"></a>

`GreetingCategoriesListResultMeta(**data: Any)`
:   Metadata for greeting_categories.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
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

<a id="GreetingCategory"></a>

`GreetingCategory(**data: Any)`
:   GreetingCategory type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

<a id="GreetingCategoryWrapper"></a>

`GreetingCategoryWrapper(**data: Any)`
:   GreetingCategoryWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `greeting_category: airbyte_agent_sdk.connectors.zendesk_talk.models.GreetingCategory | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="GreetingWrapper"></a>

`GreetingWrapper(**data: Any)`
:   GreetingWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `greeting: airbyte_agent_sdk.connectors.zendesk_talk.models.Greeting | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="GreetingsList"></a>

`GreetingsList(**data: Any)`
:   GreetingsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any | None`
    :   The type of the None singleton.

    `greetings: list[airbyte_agent_sdk.connectors.zendesk_talk.models.Greeting] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="GreetingsListResultMeta"></a>

`GreetingsListResultMeta(**data: Any)`
:   Metadata for greetings.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

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

<a id="Ivr"></a>

`Ivr(**data: Any)`
:   Ivr type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The type of the None singleton.

    `menus: list[airbyte_agent_sdk.connectors.zendesk_talk.models.IvrMenusItem] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `phone_number_ids: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `phone_number_names: list[typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="IvrMenusItem"></a>

`IvrMenusItem(**data: Any)`
:   Nested schema for Ivr.menus_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `default: bool | Any | None`
    :   The type of the None singleton.

    `greeting_id: int | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `routes: list[airbyte_agent_sdk.connectors.zendesk_talk.models.IvrMenusItemRoutesItem] | Any | None`
    :   The type of the None singleton.

<a id="IvrMenusItemRoutesItem"></a>

`IvrMenusItemRoutesItem(**data: Any)`
:   Nested schema for IvrMenusItem.routes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action: str | Any | None`
    :   The type of the None singleton.

    `greeting: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `keypress: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `option_text: str | Any | None`
    :   The type of the None singleton.

    `options: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `overflow_options: list[typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="IvrWrapper"></a>

`IvrWrapper(**data: Any)`
:   IvrWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ivr: airbyte_agent_sdk.connectors.zendesk_talk.models.Ivr | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="IvrsList"></a>

`IvrsList(**data: Any)`
:   IvrsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any | None`
    :   The type of the None singleton.

    `ivrs: list[airbyte_agent_sdk.connectors.zendesk_talk.models.Ivr] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="IvrsListResultMeta"></a>

`IvrsListResultMeta(**data: Any)`
:   Metadata for ivrs.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

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

<a id="PhoneNumber"></a>

`PhoneNumber(**data: Any)`
:   PhoneNumber type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `brand_id: int | Any | None`
    :   The type of the None singleton.

    `call_recording_consent: str | Any | None`
    :   The type of the None singleton.

    `capabilities: airbyte_agent_sdk.connectors.zendesk_talk.models.PhoneNumberCapabilities | Any | None`
    :   The type of the None singleton.

    `categorised_greetings: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `categorised_greetings_with_sub_settings: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `country_code: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `default_greeting_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `default_group_id: int | Any | None`
    :   The type of the None singleton.

    `display_number: str | Any | None`
    :   The type of the None singleton.

    `external: bool | Any | None`
    :   The type of the None singleton.

    `failover_number: str | Any | None`
    :   The type of the None singleton.

    `greeting_ids: list[int] | Any | None`
    :   The type of the None singleton.

    `group_ids: list[int] | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `ivr_id: int | Any | None`
    :   The type of the None singleton.

    `line_type: str | Any | None`
    :   The type of the None singleton.

    `location: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `nickname: str | Any | None`
    :   The type of the None singleton.

    `number: str | Any | None`
    :   The type of the None singleton.

    `outbound_enabled: bool | Any | None`
    :   The type of the None singleton.

    `priority: int | Any | None`
    :   The type of the None singleton.

    `recorded: bool | Any | None`
    :   The type of the None singleton.

    `schedule_id: int | Any | None`
    :   The type of the None singleton.

    `sms_enabled: bool | Any | None`
    :   The type of the None singleton.

    `sms_group_id: int | Any | None`
    :   The type of the None singleton.

    `token: str | Any | None`
    :   The type of the None singleton.

    `toll_free: bool | Any | None`
    :   The type of the None singleton.

    `transcription: bool | Any | None`
    :   The type of the None singleton.

    `voice_enabled: bool | Any | None`
    :   The type of the None singleton.

<a id="PhoneNumberCapabilities"></a>

`PhoneNumberCapabilities(**data: Any)`
:   Phone number capabilities (sms, mms, voice)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `emergency_address: bool | Any | None`
    :   The type of the None singleton.

    `mms: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `sms: bool | Any | None`
    :   The type of the None singleton.

    `voice: bool | Any | None`
    :   The type of the None singleton.

<a id="PhoneNumberWrapper"></a>

`PhoneNumberWrapper(**data: Any)`
:   PhoneNumberWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `phone_number: airbyte_agent_sdk.connectors.zendesk_talk.models.PhoneNumber | Any`
    :   The type of the None singleton.

<a id="PhoneNumbersList"></a>

`PhoneNumbersList(**data: Any)`
:   PhoneNumbersList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `phone_numbers: list[airbyte_agent_sdk.connectors.zendesk_talk.models.PhoneNumber] | Any`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="PhoneNumbersListResultMeta"></a>

`PhoneNumbersListResultMeta(**data: Any)`
:   Metadata for phone_numbers.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

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

<a id="ZendeskTalkApiTokenAuthConfig"></a>

`ZendeskTalkApiTokenAuthConfig(**data: Any)`
:   API Token - Authenticate using email and API token
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_token: str`
    :   Your Zendesk API token from Admin Center

    `email: str`
    :   Your Zendesk account email address

    `model_config`
    :   The type of the None singleton.

<a id="ZendeskTalkCheckResult"></a>

`ZendeskTalkCheckResult(**data: Any)`
:   Result of a health check operation.
    
    Returned by the check() method to indicate connectivity and credential status.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checked_action: str | None`
    :   Action name used for the health check.

    `checked_entity: str | None`
    :   Entity name used for the health check.

    `error: str | None`
    :   Error message if status is 'unhealthy', None otherwise.

    `model_config`
    :   The type of the None singleton.

    `status: str`
    :   Health check status: 'healthy' or 'unhealthy'.

<a id="ZendeskTalkExecuteResult"></a>

`ZendeskTalkExecuteResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult[AccountOverview]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult[AgentsOverview]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult[CurrentQueueActivity]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="ZendeskTalkExecuteResultWithMeta"></a>

`ZendeskTalkExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[Address], AddressesListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[AgentActivity], AgentsActivityListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[CallLeg], CallLegsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[Call], CallsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[GreetingCategory], GreetingCategoriesListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[Greeting], GreetingsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[Ivr], IvrsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta[list[PhoneNumber], PhoneNumbersListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`ZendeskTalkExecuteResultWithMeta[list[Address], AddressesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AddressesListResult"></a>

`AddressesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskTalkExecuteResultWithMeta[list[AgentActivity], AgentsActivityListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AgentsActivityListResult"></a>

`AgentsActivityListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskTalkExecuteResultWithMeta[list[CallLeg], CallLegsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CallLegsListResult"></a>

`CallLegsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskTalkExecuteResultWithMeta[list[Call], CallsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CallsListResult"></a>

`CallsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskTalkExecuteResultWithMeta[list[GreetingCategory], GreetingCategoriesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="GreetingCategoriesListResult"></a>

`GreetingCategoriesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskTalkExecuteResultWithMeta[list[Greeting], GreetingsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="GreetingsListResult"></a>

`GreetingsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskTalkExecuteResultWithMeta[list[Ivr], IvrsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="IvrsListResult"></a>

`IvrsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskTalkExecuteResultWithMeta[list[PhoneNumber], PhoneNumbersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PhoneNumbersListResult"></a>

`PhoneNumbersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskTalkExecuteResult[AccountOverview](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AccountOverviewListResult"></a>

`AccountOverviewListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskTalkExecuteResult[AgentsOverview](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AgentsOverviewListResult"></a>

`AgentsOverviewListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskTalkExecuteResult[CurrentQueueActivity](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CurrentQueueActivityListResult"></a>

`CurrentQueueActivityListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_talk.models.ZendeskTalkExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ZendeskTalkOauth20AuthConfig"></a>

`ZendeskTalkOauth20AuthConfig(**data: Any)`
:   OAuth 2.0 - Zendesk OAuth 2.0 authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   OAuth 2.0 access token

    `client_id: str | None`
    :   OAuth client ID

    `client_secret: str | None`
    :   OAuth client secret

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str | None`
    :   OAuth 2.0 refresh token (optional)

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