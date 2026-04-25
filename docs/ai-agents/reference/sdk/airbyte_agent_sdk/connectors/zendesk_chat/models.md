---
id: airbyte_agent_sdk-connectors-zendesk_chat-models
title: airbyte_agent_sdk.connectors.zendesk_chat.models
---

Module airbyte_agent_sdk.connectors.zendesk_chat.models
=======================================================
Pydantic models for zendesk-chat connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Account"></a>

`Account(**data: Any)`
:   Zendesk Chat account information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_key: str | Any`
    :   The type of the None singleton.

    `billing: Any`
    :   The type of the None singleton.

    `create_date: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `plan: Any`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

<a id="Agent"></a>

`Agent(**data: Any)`
:   Zendesk Chat agent
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create_date: str | Any | None`
    :   The type of the None singleton.

    `departments: list[int] | Any | None`
    :   The type of the None singleton.

    `display_name: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `enabled: bool | Any | None`
    :   The type of the None singleton.

    `enabled_departments: list[int] | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `last_login: str | Any | None`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `login_count: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `role_id: int | Any | None`
    :   The type of the None singleton.

    `roles: Any`
    :   The type of the None singleton.

    `scope: str | Any | None`
    :   The type of the None singleton.

    `skills: list[int] | Any | None`
    :   The type of the None singleton.

<a id="AgentRoles"></a>

`AgentRoles(**data: Any)`
:   Agent role flags
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `administrator: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `owner: bool | Any | None`
    :   The type of the None singleton.

<a id="AgentTimeline"></a>

`AgentTimeline(**data: Any)`
:   Agent activity timeline entry
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_id: int | Any`
    :   The type of the None singleton.

    `duration: float | Any | None`
    :   The type of the None singleton.

    `engagement_count: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start_time: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

<a id="AgentTimelineListResultMeta"></a>

`AgentTimelineListResultMeta(**data: Any)`
:   Metadata for agent_timeline.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

<a id="AgentsSearchData"></a>

`AgentsSearchData(**data: Any)`
:   Search result data for agents entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create_date: str | None`
    :   When agent was created

    `departments: list[typing.Any] | None`
    :   Department IDs agent belongs to

    `display_name: str | None`
    :   Agent display name

    `email: str | None`
    :   Agent email address

    `enabled: bool | None`
    :   Whether agent is enabled

    `first_name: str | None`
    :   Agent first name

    `id: int`
    :   Unique agent identifier

    `last_name: str | None`
    :   Agent last name

    `model_config`
    :   The type of the None singleton.

    `role_id: int | None`
    :   Agent role ID

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

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[AgentsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[ChatsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[DepartmentsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[ShortcutsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[TriggersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AgentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AgentsSearchResult"></a>

`AgentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ChatsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ChatsSearchResult"></a>

`ChatsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[DepartmentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DepartmentsSearchResult"></a>

`DepartmentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ShortcutsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ShortcutsSearchResult"></a>

`ShortcutsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TriggersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TriggersSearchResult"></a>

`TriggersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Ban"></a>

`Ban(**data: Any)`
:   Banned visitor
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `ip_address: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reason: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `visitor_id: str | Any | None`
    :   The type of the None singleton.

    `visitor_name: str | Any | None`
    :   The type of the None singleton.

<a id="Billing"></a>

`Billing(**data: Any)`
:   Account billing information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `additional_info: str | Any | None`
    :   The type of the None singleton.

    `address1: str | Any | None`
    :   The type of the None singleton.

    `address2: str | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `company: str | Any | None`
    :   The type of the None singleton.

    `country_code: str | Any | None`
    :   The type of the None singleton.

    `cycle: int | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `postal_code: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

<a id="Chat"></a>

`Chat(**data: Any)`
:   Chat conversation transcript
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `agent_names: list[str] | Any | None`
    :   The type of the None singleton.

    `comment: str | Any | None`
    :   The type of the None singleton.

    `conversions: list[airbyte_agent_sdk.connectors.zendesk_chat.models.ChatConversion] | Any | None`
    :   The type of the None singleton.

    `count: Any`
    :   The type of the None singleton.

    `deleted: bool | Any | None`
    :   The type of the None singleton.

    `department_id: int | Any | None`
    :   The type of the None singleton.

    `department_name: str | Any | None`
    :   The type of the None singleton.

    `duration: int | Any | None`
    :   The type of the None singleton.

    `engagements: list[airbyte_agent_sdk.connectors.zendesk_chat.models.ChatEngagement] | Any | None`
    :   The type of the None singleton.

    `history: list[airbyte_agent_sdk.connectors.zendesk_chat.models.ChatHistoryItem] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `message: str | Any | None`
    :   The type of the None singleton.

    `missed: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rating: str | Any | None`
    :   The type of the None singleton.

    `response_time: Any`
    :   The type of the None singleton.

    `session: Any`
    :   The type of the None singleton.

    `started_by: str | Any | None`
    :   The type of the None singleton.

    `tags: list[str] | Any | None`
    :   The type of the None singleton.

    `timestamp: str | Any | None`
    :   The type of the None singleton.

    `triggered: bool | Any | None`
    :   The type of the None singleton.

    `triggered_response: bool | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `unread: bool | Any | None`
    :   The type of the None singleton.

    `update_timestamp: str | Any | None`
    :   The type of the None singleton.

    `visitor: Any`
    :   The type of the None singleton.

    `webpath: list[airbyte_agent_sdk.connectors.zendesk_chat.models.WebpathItem] | Any | None`
    :   The type of the None singleton.

    `zendesk_ticket_id: int | Any | None`
    :   The type of the None singleton.

<a id="ChatConversion"></a>

`ChatConversion(**data: Any)`
:   ChatConversion type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attribution: Any`
    :   The type of the None singleton.

    `goal_id: int | Any | None`
    :   The type of the None singleton.

    `goal_name: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `timestamp: str | Any | None`
    :   The type of the None singleton.

<a id="ChatEngagement"></a>

`ChatEngagement(**data: Any)`
:   ChatEngagement type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accepted: bool | Any | None`
    :   The type of the None singleton.

    `agent_full_name: str | Any | None`
    :   The type of the None singleton.

    `agent_id: str | Any | None`
    :   The type of the None singleton.

    `agent_name: str | Any | None`
    :   The type of the None singleton.

    `assigned: bool | Any | None`
    :   The type of the None singleton.

    `comment: str | Any | None`
    :   The type of the None singleton.

    `count: Any`
    :   The type of the None singleton.

    `department_id: int | Any | None`
    :   The type of the None singleton.

    `duration: float | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rating: str | Any | None`
    :   The type of the None singleton.

    `response_time: Any`
    :   The type of the None singleton.

    `skills_fulfilled: bool | Any | None`
    :   The type of the None singleton.

    `skills_requested: list[int] | Any | None`
    :   The type of the None singleton.

    `started_by: str | Any | None`
    :   The type of the None singleton.

    `timestamp: str | Any | None`
    :   The type of the None singleton.

<a id="ChatHistoryItem"></a>

`ChatHistoryItem(**data: Any)`
:   ChatHistoryItem type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: str | Any | None`
    :   The type of the None singleton.

    `department_id: int | Any | None`
    :   The type of the None singleton.

    `department_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `msg: str | Any | None`
    :   The type of the None singleton.

    `msg_id: str | Any | None`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `new_rating: str | Any | None`
    :   The type of the None singleton.

    `new_tags: list[str] | Any | None`
    :   The type of the None singleton.

    `nick: str | Any | None`
    :   The type of the None singleton.

    `options: str | Any | None`
    :   The type of the None singleton.

    `rating: str | Any | None`
    :   The type of the None singleton.

    `tags: list[str] | Any | None`
    :   The type of the None singleton.

    `timestamp: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="ChatSession"></a>

`ChatSession(**data: Any)`
:   ChatSession type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `browser: str | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `country_code: str | Any | None`
    :   The type of the None singleton.

    `country_name: str | Any | None`
    :   The type of the None singleton.

    `end_date: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `ip: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `platform: str | Any | None`
    :   The type of the None singleton.

    `region: str | Any | None`
    :   The type of the None singleton.

    `start_date: str | Any | None`
    :   The type of the None singleton.

    `user_agent: str | Any | None`
    :   The type of the None singleton.

<a id="ChatsListResultMeta"></a>

`ChatsListResultMeta(**data: Any)`
:   Metadata for chats.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

<a id="ChatsSearchData"></a>

`ChatsSearchData(**data: Any)`
:   Search result data for chats entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_ids: list[typing.Any] | None`
    :   IDs of agents in chat

    `department_id: int | None`
    :   Department ID

    `department_name: str | None`
    :   Department name

    `duration: int | None`
    :   Chat duration in seconds

    `id: str`
    :   Unique chat identifier

    `missed: bool | None`
    :   Whether chat was missed

    `model_config`
    :   The type of the None singleton.

    `rating: str | None`
    :   Satisfaction rating

    `timestamp: str | None`
    :   Chat start timestamp

    `update_timestamp: str | None`
    :   Last update timestamp

<a id="ConversionAttribution"></a>

`ConversionAttribution(**data: Any)`
:   ConversionAttribution type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_id: int | Any | None`
    :   The type of the None singleton.

    `agent_name: str | Any | None`
    :   The type of the None singleton.

    `chat_timestamp: str | Any | None`
    :   The type of the None singleton.

    `department_id: int | Any | None`
    :   The type of the None singleton.

    `department_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Department"></a>

`Department(**data: Any)`
:   Department type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | Any | None`
    :   The type of the None singleton.

    `enabled: bool | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `members: list[int] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `settings: Any`
    :   The type of the None singleton.

<a id="DepartmentSettings"></a>

`DepartmentSettings(**data: Any)`
:   DepartmentSettings type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `chat_limit: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DepartmentsSearchData"></a>

`DepartmentsSearchData(**data: Any)`
:   Search result data for departments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether department is enabled

    `id: int`
    :   Department ID

    `members: list[typing.Any] | None`
    :   Agent IDs in department

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Department name

<a id="Goal"></a>

`Goal(**data: Any)`
:   Goal type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attribution_model: str | Any | None`
    :   The type of the None singleton.

    `attribution_period: int | Any | None`
    :   The type of the None singleton.

    `attribution_window: int | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `enabled: bool | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `settings: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="MessageCount"></a>

`MessageCount(**data: Any)`
:   MessageCount type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total: int | Any | None`
    :   The type of the None singleton.

    `visitor: int | Any | None`
    :   The type of the None singleton.

<a id="Plan"></a>

`Plan(**data: Any)`
:   Account plan details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_leaderboard: bool | Any | None`
    :   The type of the None singleton.

    `agent_reports: bool | Any | None`
    :   The type of the None singleton.

    `analytics: bool | Any | None`
    :   The type of the None singleton.

    `chat_reports: bool | Any | None`
    :   The type of the None singleton.

    `daily_reports: bool | Any | None`
    :   The type of the None singleton.

    `email_reports: bool | Any | None`
    :   The type of the None singleton.

    `file_upload: bool | Any | None`
    :   The type of the None singleton.

    `goals: int | Any | None`
    :   The type of the None singleton.

    `high_load: bool | Any | None`
    :   The type of the None singleton.

    `integrations: bool | Any | None`
    :   The type of the None singleton.

    `ip_restriction: bool | Any | None`
    :   The type of the None singleton.

    `long_desc: str | Any | None`
    :   The type of the None singleton.

    `max_advanced_triggers: str | Any | None`
    :   The type of the None singleton.

    `max_agents: int | Any | None`
    :   The type of the None singleton.

    `max_basic_triggers: str | Any | None`
    :   The type of the None singleton.

    `max_concurrent_chats: str | Any | None`
    :   The type of the None singleton.

    `max_departments: str | Any | None`
    :   The type of the None singleton.

    `max_history_search_days: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `monitoring: bool | Any | None`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `operating_hours: bool | Any | None`
    :   The type of the None singleton.

    `price: float | Any | None`
    :   The type of the None singleton.

    `rest_api: bool | Any | None`
    :   The type of the None singleton.

    `short_desc: str | Any | None`
    :   The type of the None singleton.

    `sla: bool | Any | None`
    :   The type of the None singleton.

    `support: bool | Any | None`
    :   The type of the None singleton.

    `unbranding: bool | Any | None`
    :   The type of the None singleton.

    `widget_customization: str | Any | None`
    :   The type of the None singleton.

<a id="ResponseTime"></a>

`ResponseTime(**data: Any)`
:   ResponseTime type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avg: float | Any | None`
    :   The type of the None singleton.

    `first: int | Any | None`
    :   The type of the None singleton.

    `max: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Role"></a>

`Role(**data: Any)`
:   Role type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | Any | None`
    :   The type of the None singleton.

    `enabled: bool | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `members_count: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `permissions: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="RoutingSettings"></a>

`RoutingSettings(**data: Any)`
:   RoutingSettings type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auto_accept: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `auto_idle: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `chat_limit: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reassignment: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `routing_mode: str | Any | None`
    :   The type of the None singleton.

    `skill_routing: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="Shortcut"></a>

`Shortcut(**data: Any)`
:   Shortcut type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agents: list[int] | Any | None`
    :   The type of the None singleton.

    `departments: list[int] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `message: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `options: str | Any | None`
    :   The type of the None singleton.

    `scope: str | Any | None`
    :   The type of the None singleton.

    `tags: list[str] | Any | None`
    :   The type of the None singleton.

<a id="ShortcutsSearchData"></a>

`ShortcutsSearchData(**data: Any)`
:   Search result data for shortcuts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int`
    :   Shortcut ID

    `message: str | None`
    :   Shortcut message content

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Shortcut name/trigger

    `tags: list[typing.Any] | None`
    :   Tags applied when shortcut is used

<a id="Skill"></a>

`Skill(**data: Any)`
:   Skill type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | Any | None`
    :   The type of the None singleton.

    `enabled: bool | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `members: list[int] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

<a id="Trigger"></a>

`Trigger(**data: Any)`
:   Trigger type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actions: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `conditions: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `definition: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `departments: list[int] | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `enabled: bool | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `run_once: bool | Any | None`
    :   The type of the None singleton.

<a id="TriggersSearchData"></a>

`TriggersSearchData(**data: Any)`
:   Search result data for triggers entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether trigger is enabled

    `id: int`
    :   Trigger ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Trigger name

<a id="Visitor"></a>

`Visitor(**data: Any)`
:   Visitor type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `notes: str | Any | None`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

<a id="WebpathItem"></a>

`WebpathItem(**data: Any)`
:   WebpathItem type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `from_: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `timestamp: str | Any | None`
    :   The type of the None singleton.

<a id="ZendeskChatAuthConfig"></a>

`ZendeskChatAuthConfig(**data: Any)`
:   OAuth 2.0 Access Token - Authenticate using an OAuth 2.0 access token from Zendesk
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   Your Zendesk Chat OAuth 2.0 access token

    `model_config`
    :   The type of the None singleton.

<a id="ZendeskChatCheckResult"></a>

`ZendeskChatCheckResult(**data: Any)`
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

<a id="ZendeskChatExecuteResult"></a>

`ZendeskChatExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[dict[str, Any]]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[list[Agent]]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[list[Department]]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[list[Goal]]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[list[Role]]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[list[Shortcut]]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[list[Skill]]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[list[Trigger]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="ZendeskChatExecuteResultWithMeta"></a>

`ZendeskChatExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResultWithMeta[list[AgentTimeline], AgentTimelineListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResultWithMeta[list[Chat], ChatsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`ZendeskChatExecuteResultWithMeta[list[AgentTimeline], AgentTimelineListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AgentTimelineListResult"></a>

`AgentTimelineListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskChatExecuteResultWithMeta[list[Chat], ChatsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ChatsListResult"></a>

`ChatsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskChatExecuteResult[dict[str, Any]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BansListResult"></a>

`BansListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskChatExecuteResult[list[Agent]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AgentsListResult"></a>

`AgentsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskChatExecuteResult[list[Department]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DepartmentsListResult"></a>

`DepartmentsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskChatExecuteResult[list[Goal]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="GoalsListResult"></a>

`GoalsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskChatExecuteResult[list[Role]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="RolesListResult"></a>

`RolesListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskChatExecuteResult[list[Shortcut]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ShortcutsListResult"></a>

`ShortcutsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskChatExecuteResult[list[Skill]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SkillsListResult"></a>

`SkillsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskChatExecuteResult[list[Trigger]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TriggersListResult"></a>

`TriggersListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ZendeskChatReplicationConfig"></a>

`ZendeskChatReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Zendesk Chat.
    
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
    :   The date from which to start replicating data, in the format YYYY-MM-DDT00:00:00Z.