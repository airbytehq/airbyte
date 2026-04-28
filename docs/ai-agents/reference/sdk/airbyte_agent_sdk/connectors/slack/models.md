---
id: airbyte_agent_sdk-connectors-slack-models
title: airbyte_agent_sdk.connectors.slack.models
---

Module airbyte_agent_sdk.connectors.slack.models
================================================
Pydantic models for slack connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

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

    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult[ChannelMessagesSearchData]
    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult[ChannelsSearchData]
    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult[ThreadsSearchData]
    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.slack.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[ChannelMessagesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ChannelMessagesSearchResult"></a>

`ChannelMessagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ChannelsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ChannelsSearchResult"></a>

`ChannelsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ThreadsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ThreadsSearchResult"></a>

`ThreadsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UsersSearchResult"></a>

`UsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Attachment"></a>

`Attachment(**data: Any)`
:   Message attachment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_icon: str | Any | None`
    :   The type of the None singleton.

    `author_link: str | Any | None`
    :   The type of the None singleton.

    `author_name: str | Any | None`
    :   The type of the None singleton.

    `color: str | Any | None`
    :   The type of the None singleton.

    `fallback: str | Any | None`
    :   The type of the None singleton.

    `fields: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `footer: str | Any | None`
    :   The type of the None singleton.

    `footer_icon: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `image_url: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pretext: str | Any | None`
    :   The type of the None singleton.

    `text: str | Any | None`
    :   The type of the None singleton.

    `thumb_url: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `title_link: str | Any | None`
    :   The type of the None singleton.

    `ts: Any`
    :   The type of the None singleton.

<a id="BotProfile"></a>

`BotProfile(**data: Any)`
:   Bot profile information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_id: str | Any | None`
    :   The type of the None singleton.

    `deleted: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `team_id: str | Any | None`
    :   The type of the None singleton.

    `updated: int | Any | None`
    :   The type of the None singleton.

<a id="Channel"></a>

`Channel(**data: Any)`
:   Slack channel object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `context_team_id: str | Any | None`
    :   The type of the None singleton.

    `created: int | Any | None`
    :   The type of the None singleton.

    `creator: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_archived: bool | Any | None`
    :   The type of the None singleton.

    `is_channel: bool | Any | None`
    :   The type of the None singleton.

    `is_ext_shared: bool | Any | None`
    :   The type of the None singleton.

    `is_general: bool | Any | None`
    :   The type of the None singleton.

    `is_group: bool | Any | None`
    :   The type of the None singleton.

    `is_im: bool | Any | None`
    :   The type of the None singleton.

    `is_member: bool | Any | None`
    :   The type of the None singleton.

    `is_mpim: bool | Any | None`
    :   The type of the None singleton.

    `is_org_shared: bool | Any | None`
    :   The type of the None singleton.

    `is_pending_ext_shared: bool | Any | None`
    :   The type of the None singleton.

    `is_private: bool | Any | None`
    :   The type of the None singleton.

    `is_read_only: bool | Any | None`
    :   The type of the None singleton.

    `is_shared: bool | Any | None`
    :   The type of the None singleton.

    `is_thread_only: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `name_normalized: str | Any | None`
    :   The type of the None singleton.

    `num_members: int | Any | None`
    :   The type of the None singleton.

    `parent_conversation: str | Any | None`
    :   The type of the None singleton.

    `pending_connected_team_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `pending_shared: list[str] | Any | None`
    :   The type of the None singleton.

    `previous_names: list[str] | Any | None`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `purpose: Any`
    :   The type of the None singleton.

    `shared_team_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `topic: Any`
    :   The type of the None singleton.

    `unlinked: int | Any | None`
    :   The type of the None singleton.

    `updated: int | Any | None`
    :   The type of the None singleton.

<a id="ChannelCreateParams"></a>

`ChannelCreateParams(**data: Any)`
:   Parameters for creating a channel
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `is_private: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="ChannelCreateResponse"></a>

`ChannelCreateResponse(**data: Any)`
:   Response from creating a channel
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: airbyte_agent_sdk.connectors.slack.models.Channel | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ok: bool | Any`
    :   The type of the None singleton.

<a id="ChannelInviteParams"></a>

`ChannelInviteParams(**data: Any)`
:   Parameters for inviting users to a channel
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: str | Any`
    :   The type of the None singleton.

    `force: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `users: str | Any`
    :   The type of the None singleton.

<a id="ChannelInviteResponse"></a>

`ChannelInviteResponse(**data: Any)`
:   Response from inviting users to a channel
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: airbyte_agent_sdk.connectors.slack.models.Channel | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ok: bool | Any`
    :   The type of the None singleton.

<a id="ChannelMessagesListResultMeta"></a>

`ChannelMessagesListResultMeta(**data: Any)`
:   Metadata for channel_messages.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

<a id="ChannelMessagesSearchData"></a>

`ChannelMessagesSearchData(**data: Any)`
:   Search result data for channel_messages entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachments: list[typing.Any] | None`
    :   Message attachments.

    `blocks: list[typing.Any] | None`
    :   Block kit blocks.

    `bot_id: str | None`
    :   Bot ID if message was sent by a bot.

    `bot_profile: dict[str, typing.Any] | None`
    :   Bot profile information.

    `is_locked: bool | None`
    :   Whether the thread is locked.

    `latest_reply: str | None`
    :   Timestamp of latest reply.

    `model_config`
    :   The type of the None singleton.

    `reactions: list[typing.Any] | None`
    :   Reactions to the message.

    `reply_count: int | None`
    :   Number of replies in thread.

    `reply_users: list[typing.Any] | None`
    :   User IDs who replied to the thread.

    `reply_users_count: int | None`
    :   Number of unique users who replied.

    `subscribed: bool | None`
    :   Whether the user is subscribed to the thread.

    `subtype: str | None`
    :   Message subtype.

    `team: str | None`
    :   Team ID.

    `text: str | None`
    :   Message text content.

    `thread_ts: str | None`
    :   Thread parent timestamp.

    `ts: str | None`
    :   Message timestamp (unique identifier).

    `type_: str | None`
    :   Message type.

    `user: str | None`
    :   User ID who sent the message.

<a id="ChannelPurpose"></a>

`ChannelPurpose(**data: Any)`
:   Channel purpose information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `creator: str | Any | None`
    :   The type of the None singleton.

    `last_set: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: str | Any | None`
    :   The type of the None singleton.

<a id="ChannelPurposeParams"></a>

`ChannelPurposeParams(**data: Any)`
:   Parameters for setting channel purpose
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `purpose: str | Any`
    :   The type of the None singleton.

<a id="ChannelPurposeResponse"></a>

`ChannelPurposeResponse(**data: Any)`
:   Response from setting channel purpose
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: airbyte_agent_sdk.connectors.slack.models.Channel | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ok: bool | Any`
    :   The type of the None singleton.

<a id="ChannelRenameParams"></a>

`ChannelRenameParams(**data: Any)`
:   Parameters for renaming a channel
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="ChannelRenameResponse"></a>

`ChannelRenameResponse(**data: Any)`
:   Response from renaming a channel
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: airbyte_agent_sdk.connectors.slack.models.Channel | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ok: bool | Any`
    :   The type of the None singleton.

<a id="ChannelResponse"></a>

`ChannelResponse(**data: Any)`
:   Response containing single channel
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: airbyte_agent_sdk.connectors.slack.models.Channel | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ok: bool | Any`
    :   The type of the None singleton.

<a id="ChannelTopic"></a>

`ChannelTopic(**data: Any)`
:   Channel topic information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `creator: str | Any | None`
    :   The type of the None singleton.

    `last_set: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: str | Any | None`
    :   The type of the None singleton.

<a id="ChannelTopicParams"></a>

`ChannelTopicParams(**data: Any)`
:   Parameters for setting channel topic
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `topic: str | Any`
    :   The type of the None singleton.

<a id="ChannelTopicResponse"></a>

`ChannelTopicResponse(**data: Any)`
:   Response from setting channel topic
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: airbyte_agent_sdk.connectors.slack.models.Channel | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ok: bool | Any`
    :   The type of the None singleton.

<a id="ChannelsListResponse"></a>

`ChannelsListResponse(**data: Any)`
:   Response containing list of channels
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channels: list[airbyte_agent_sdk.connectors.slack.models.Channel] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ok: bool | Any`
    :   The type of the None singleton.

    `response_metadata: airbyte_agent_sdk.connectors.slack.models.ResponseMetadata | Any`
    :   The type of the None singleton.

<a id="ChannelsListResultMeta"></a>

`ChannelsListResultMeta(**data: Any)`
:   Metadata for channels.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

<a id="ChannelsSearchData"></a>

`ChannelsSearchData(**data: Any)`
:   Search result data for channels entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `context_team_id: str | None`
    :   The unique identifier of the team context in which the channel exists.

    `created: int | None`
    :   The timestamp when the channel was created.

    `creator: str | None`
    :   The ID of the user who created the channel.

    `id: str | None`
    :   The unique identifier of the channel.

    `is_archived: bool | None`
    :   Indicates if the channel is archived.

    `is_channel: bool | None`
    :   Indicates if the entity is a channel.

    `is_ext_shared: bool | None`
    :   Indicates if the channel is externally shared.

    `is_general: bool | None`
    :   Indicates if the channel is a general channel in the workspace.

    `is_group: bool | None`
    :   Indicates if the channel is a group (private channel) rather than a regular channel.

    `is_im: bool | None`
    :   Indicates if the entity is a direct message (IM) channel.

    `is_member: bool | None`
    :   Indicates if the calling user is a member of the channel.

    `is_mpim: bool | None`
    :   Indicates if the entity is a multiple person direct message (MPIM) channel.

    `is_org_shared: bool | None`
    :   Indicates if the channel is organization-wide shared.

    `is_pending_ext_shared: bool | None`
    :   Indicates if the channel is pending external shared.

    `is_private: bool | None`
    :   Indicates if the channel is a private channel.

    `is_read_only: bool | None`
    :   Indicates if the channel is read-only.

    `is_shared: bool | None`
    :   Indicates if the channel is shared.

    `last_read: str | None`
    :   The timestamp of the user's last read message in the channel.

    `locale: str | None`
    :   The locale of the channel.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the channel.

    `name_normalized: str | None`
    :   The normalized name of the channel.

    `num_members: int | None`
    :   The number of members in the channel.

    `parent_conversation: str | None`
    :   The parent conversation of the channel.

    `pending_connected_team_ids: list[typing.Any] | None`
    :   The IDs of teams that are pending to be connected to the channel.

    `pending_shared: list[typing.Any] | None`
    :   The list of pending shared items of the channel.

    `previous_names: list[typing.Any] | None`
    :   The previous names of the channel.

    `purpose: dict[str, typing.Any] | None`
    :   The purpose of the channel.

    `shared_team_ids: list[typing.Any] | None`
    :   The IDs of teams with which the channel is shared.

    `topic: dict[str, typing.Any] | None`
    :   The topic of the channel.

    `unlinked: int | None`
    :   Indicates if the channel is unlinked.

    `updated: int | None`
    :   The timestamp when the channel was last updated.

<a id="CreatedMessage"></a>

`CreatedMessage(**data: Any)`
:   A message object returned from create/update operations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_id: str | Any | None`
    :   The type of the None singleton.

    `bot_id: str | Any | None`
    :   The type of the None singleton.

    `bot_profile: Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `subtype: str | Any | None`
    :   The type of the None singleton.

    `team: str | Any | None`
    :   The type of the None singleton.

    `text: str | Any | None`
    :   The type of the None singleton.

    `ts: str | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `user: str | Any | None`
    :   The type of the None singleton.

<a id="EditedInfo"></a>

`EditedInfo(**data: Any)`
:   Message edit information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `ts: str | Any | None`
    :   The type of the None singleton.

    `user: str | Any | None`
    :   The type of the None singleton.

<a id="File"></a>

`File(**data: Any)`
:   File object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: int | Any | None`
    :   The type of the None singleton.

    `external_type: str | Any | None`
    :   The type of the None singleton.

    `filetype: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `is_external: bool | Any | None`
    :   The type of the None singleton.

    `is_public: bool | Any | None`
    :   The type of the None singleton.

    `mimetype: str | Any | None`
    :   The type of the None singleton.

    `mode: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `permalink: str | Any | None`
    :   The type of the None singleton.

    `permalink_public: str | Any | None`
    :   The type of the None singleton.

    `pretty_type: str | Any | None`
    :   The type of the None singleton.

    `public_url_shared: bool | Any | None`
    :   The type of the None singleton.

    `size: int | Any | None`
    :   The type of the None singleton.

    `timestamp: int | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `url_private: str | Any | None`
    :   The type of the None singleton.

    `url_private_download: str | Any | None`
    :   The type of the None singleton.

    `user: str | Any | None`
    :   The type of the None singleton.

<a id="Message"></a>

`Message(**data: Any)`
:   Slack message object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_id: str | Any | None`
    :   The type of the None singleton.

    `attachments: list[airbyte_agent_sdk.connectors.slack.models.Attachment] | Any | None`
    :   The type of the None singleton.

    `blocks: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `bot_id: str | Any | None`
    :   The type of the None singleton.

    `bot_profile: Any`
    :   The type of the None singleton.

    `edited: Any`
    :   The type of the None singleton.

    `files: list[airbyte_agent_sdk.connectors.slack.models.File] | Any | None`
    :   The type of the None singleton.

    `is_locked: bool | Any | None`
    :   The type of the None singleton.

    `latest_reply: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reactions: list[airbyte_agent_sdk.connectors.slack.models.Reaction] | Any | None`
    :   The type of the None singleton.

    `reply_count: int | Any | None`
    :   The type of the None singleton.

    `reply_users: list[str] | Any | None`
    :   The type of the None singleton.

    `reply_users_count: int | Any | None`
    :   The type of the None singleton.

    `subscribed: bool | Any | None`
    :   The type of the None singleton.

    `subtype: str | Any | None`
    :   The type of the None singleton.

    `team: str | Any | None`
    :   The type of the None singleton.

    `text: str | Any | None`
    :   The type of the None singleton.

    `thread_ts: str | Any | None`
    :   The type of the None singleton.

    `ts: str | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `user: str | Any | None`
    :   The type of the None singleton.

<a id="MessageCreateParams"></a>

`MessageCreateParams(**data: Any)`
:   Parameters for creating a message
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reply_broadcast: bool | Any`
    :   The type of the None singleton.

    `text: str | Any`
    :   The type of the None singleton.

    `thread_ts: str | Any`
    :   The type of the None singleton.

    `unfurl_links: bool | Any`
    :   The type of the None singleton.

    `unfurl_media: bool | Any`
    :   The type of the None singleton.

<a id="MessageCreateResponse"></a>

`MessageCreateResponse(**data: Any)`
:   Response from creating a message
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: str | Any | None`
    :   The type of the None singleton.

    `message: airbyte_agent_sdk.connectors.slack.models.CreatedMessage | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ok: bool | Any`
    :   The type of the None singleton.

    `ts: str | Any | None`
    :   The type of the None singleton.

<a id="MessageUpdateParams"></a>

`MessageUpdateParams(**data: Any)`
:   Parameters for updating a message
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: str | Any`
    :   The type of the None singleton.

    `ts: str | Any`
    :   The type of the None singleton.

<a id="MessageUpdateResponse"></a>

`MessageUpdateResponse(**data: Any)`
:   Response from updating a message
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: str | Any | None`
    :   The type of the None singleton.

    `message: airbyte_agent_sdk.connectors.slack.models.CreatedMessage | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ok: bool | Any`
    :   The type of the None singleton.

    `text: str | Any | None`
    :   The type of the None singleton.

    `ts: str | Any | None`
    :   The type of the None singleton.

<a id="MessagesListResponse"></a>

`MessagesListResponse(**data: Any)`
:   Response containing list of messages
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `messages: list[airbyte_agent_sdk.connectors.slack.models.Message] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ok: bool | Any`
    :   The type of the None singleton.

    `pin_count: int | Any | None`
    :   The type of the None singleton.

    `response_metadata: airbyte_agent_sdk.connectors.slack.models.ResponseMetadata | Any`
    :   The type of the None singleton.

<a id="Reaction"></a>

`Reaction(**data: Any)`
:   Message reaction
    
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

    `name: str | Any | None`
    :   The type of the None singleton.

    `users: list[str] | Any | None`
    :   The type of the None singleton.

<a id="ReactionAddParams"></a>

`ReactionAddParams(**data: Any)`
:   Parameters for adding a reaction
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `timestamp: str | Any`
    :   The type of the None singleton.

<a id="ReactionAddResponse"></a>

`ReactionAddResponse(**data: Any)`
:   Response from adding a reaction
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `ok: bool | Any`
    :   The type of the None singleton.

<a id="ResponseMetadata"></a>

`ResponseMetadata(**data: Any)`
:   Response metadata including pagination
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

<a id="SlackCheckResult"></a>

`SlackCheckResult(**data: Any)`
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

<a id="SlackExecuteResult"></a>

`SlackExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="SlackExecuteResultWithMeta"></a>

`SlackExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta[list[Channel], ChannelsListResultMeta]
    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta[list[Message], ChannelMessagesListResultMeta]
    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta[list[Thread], ThreadsListResultMeta]
    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta[list[User], UsersListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`SlackExecuteResultWithMeta[list[Channel], ChannelsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ChannelsListResult"></a>

`ChannelsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SlackExecuteResultWithMeta[list[Message], ChannelMessagesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ChannelMessagesListResult"></a>

`ChannelMessagesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SlackExecuteResultWithMeta[list[Thread], ThreadsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ThreadsListResult"></a>

`ThreadsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SlackExecuteResultWithMeta[list[User], UsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UsersListResult"></a>

`UsersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.slack.models.SlackExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SlackOauth20AuthenticationAuthConfig"></a>

`SlackOauth20AuthenticationAuthConfig(**data: Any)`
:   OAuth 2.0 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   OAuth access token (bot token from oauth.v2.access response)

    `client_id: str | None`
    :   Your Slack App's Client ID

    `client_secret: str | None`
    :   Your Slack App's Client Secret

    `model_config`
    :   The type of the None singleton.

<a id="SlackReplicationConfig"></a>

`SlackReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Slack.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `join_channels: bool`
    :   Whether to automatically join public channels to sync messages.

    `lookback_window: int`
    :   Number of days to look back when syncing data (0-365).

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data.

<a id="SlackTokenAuthenticationAuthConfig"></a>

`SlackTokenAuthenticationAuthConfig(**data: Any)`
:   Token Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bot_key: str`
    :   Your Slack Bot Key (xoxb-) or User Token (xoxp-)

    `model_config`
    :   The type of the None singleton.

<a id="Thread"></a>

`Thread(**data: Any)`
:   Slack thread reply message object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_id: str | Any | None`
    :   The type of the None singleton.

    `attachments: list[airbyte_agent_sdk.connectors.slack.models.Attachment] | Any | None`
    :   The type of the None singleton.

    `blocks: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `bot_id: str | Any | None`
    :   The type of the None singleton.

    `bot_profile: Any`
    :   The type of the None singleton.

    `edited: Any`
    :   The type of the None singleton.

    `files: list[airbyte_agent_sdk.connectors.slack.models.File] | Any | None`
    :   The type of the None singleton.

    `is_locked: bool | Any | None`
    :   The type of the None singleton.

    `latest_reply: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `parent_user_id: str | Any | None`
    :   The type of the None singleton.

    `reactions: list[airbyte_agent_sdk.connectors.slack.models.Reaction] | Any | None`
    :   The type of the None singleton.

    `reply_count: int | Any | None`
    :   The type of the None singleton.

    `reply_users: list[str] | Any | None`
    :   The type of the None singleton.

    `reply_users_count: int | Any | None`
    :   The type of the None singleton.

    `subscribed: bool | Any | None`
    :   The type of the None singleton.

    `subtype: str | Any | None`
    :   The type of the None singleton.

    `team: str | Any | None`
    :   The type of the None singleton.

    `text: str | Any | None`
    :   The type of the None singleton.

    `thread_ts: str | Any | None`
    :   The type of the None singleton.

    `ts: str | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `user: str | Any | None`
    :   The type of the None singleton.

<a id="ThreadRepliesResponse"></a>

`ThreadRepliesResponse(**data: Any)`
:   Response containing thread replies
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `messages: list[airbyte_agent_sdk.connectors.slack.models.Thread] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ok: bool | Any`
    :   The type of the None singleton.

    `response_metadata: airbyte_agent_sdk.connectors.slack.models.ResponseMetadata | Any`
    :   The type of the None singleton.

<a id="ThreadsListResultMeta"></a>

`ThreadsListResultMeta(**data: Any)`
:   Metadata for threads.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

<a id="ThreadsSearchData"></a>

`ThreadsSearchData(**data: Any)`
:   Search result data for threads entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `blocks: list[typing.Any] | None`
    :   Block kit blocks.

    `bot_id: str | None`
    :   Bot ID if message was sent by a bot.

    `is_locked: bool | None`
    :   Whether the thread is locked.

    `latest_reply: str | None`
    :   Timestamp of latest reply.

    `model_config`
    :   The type of the None singleton.

    `parent_user_id: str | None`
    :   User ID of the parent message author (present in thread replies).

    `reply_count: int | None`
    :   Number of replies in thread.

    `reply_users: list[typing.Any] | None`
    :   User IDs who replied to the thread.

    `reply_users_count: int | None`
    :   Number of unique users who replied.

    `subscribed: bool | None`
    :   Whether the user is subscribed to the thread.

    `subtype: str | None`
    :   Message subtype.

    `team: str | None`
    :   Team ID.

    `text: str | None`
    :   Message text content.

    `thread_ts: str | None`
    :   Thread parent timestamp.

    `ts: str | None`
    :   Message timestamp (unique identifier).

    `type_: str | None`
    :   Message type.

    `user: str | None`
    :   User ID who sent the message.

<a id="User"></a>

`User(**data: Any)`
:   Slack user object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any | None`
    :   The type of the None singleton.

    `deleted: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_admin: bool | Any | None`
    :   The type of the None singleton.

    `is_app_user: bool | Any | None`
    :   The type of the None singleton.

    `is_bot: bool | Any | None`
    :   The type of the None singleton.

    `is_email_confirmed: bool | Any | None`
    :   The type of the None singleton.

    `is_owner: bool | Any | None`
    :   The type of the None singleton.

    `is_primary_owner: bool | Any | None`
    :   The type of the None singleton.

    `is_restricted: bool | Any | None`
    :   The type of the None singleton.

    `is_ultra_restricted: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `profile: Any`
    :   The type of the None singleton.

    `real_name: str | Any | None`
    :   The type of the None singleton.

    `team_id: str | Any | None`
    :   The type of the None singleton.

    `tz: str | Any | None`
    :   The type of the None singleton.

    `tz_label: str | Any | None`
    :   The type of the None singleton.

    `tz_offset: int | Any | None`
    :   The type of the None singleton.

    `updated: int | Any | None`
    :   The type of the None singleton.

    `who_can_share_contact_card: str | Any | None`
    :   The type of the None singleton.

<a id="UserProfile"></a>

`UserProfile(**data: Any)`
:   User profile information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_hash: str | Any | None`
    :   The type of the None singleton.

    `display_name: str | Any | None`
    :   The type of the None singleton.

    `display_name_normalized: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `image_192: str | Any | None`
    :   The type of the None singleton.

    `image_24: str | Any | None`
    :   The type of the None singleton.

    `image_32: str | Any | None`
    :   The type of the None singleton.

    `image_48: str | Any | None`
    :   The type of the None singleton.

    `image_512: str | Any | None`
    :   The type of the None singleton.

    `image_72: str | Any | None`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `real_name: str | Any | None`
    :   The type of the None singleton.

    `real_name_normalized: str | Any | None`
    :   The type of the None singleton.

    `skype: str | Any | None`
    :   The type of the None singleton.

    `status_emoji: str | Any | None`
    :   The type of the None singleton.

    `status_expiration: int | Any | None`
    :   The type of the None singleton.

    `status_text: str | Any | None`
    :   The type of the None singleton.

    `team: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

<a id="UserResponse"></a>

`UserResponse(**data: Any)`
:   Response containing single user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `ok: bool | Any`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.slack.models.User | Any`
    :   The type of the None singleton.

<a id="UsersListResponse"></a>

`UsersListResponse(**data: Any)`
:   Response containing list of users
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cache_ts: int | Any | None`
    :   The type of the None singleton.

    `members: list[airbyte_agent_sdk.connectors.slack.models.User] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ok: bool | Any`
    :   The type of the None singleton.

    `response_metadata: airbyte_agent_sdk.connectors.slack.models.ResponseMetadata | Any`
    :   The type of the None singleton.

<a id="UsersListResultMeta"></a>

`UsersListResultMeta(**data: Any)`
:   Metadata for users.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

<a id="UsersSearchData"></a>

`UsersSearchData(**data: Any)`
:   Search result data for users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The color assigned to the user for visual purposes.

    `deleted: bool | None`
    :   Indicates if the user is deleted or not.

    `has_2fa: bool | None`
    :   Flag indicating if the user has two-factor authentication enabled.

    `id: str | None`
    :   Unique identifier for the user.

    `is_admin: bool | None`
    :   Flag specifying if the user is an admin or not.

    `is_app_user: bool | None`
    :   Specifies if the user is an app user.

    `is_bot: bool | None`
    :   Indicates if the user is a bot account.

    `is_email_confirmed: bool | None`
    :   Flag indicating if the user's email is confirmed.

    `is_forgotten: bool | None`
    :   Specifies if the user is marked as forgotten.

    `is_invited_user: bool | None`
    :   Indicates if the user is invited or not.

    `is_owner: bool | None`
    :   Flag indicating if the user is an owner.

    `is_primary_owner: bool | None`
    :   Specifies if the user is the primary owner.

    `is_restricted: bool | None`
    :   Flag specifying if the user is restricted.

    `is_ultra_restricted: bool | None`
    :   Indicates if the user has ultra-restricted access.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The username of the user.

    `profile: dict[str, typing.Any] | None`
    :   User's profile information containing detailed details.

    `real_name: str | None`
    :   The real name of the user.

    `team_id: str | None`
    :   Unique identifier for the team the user belongs to.

    `tz: str | None`
    :   Timezone of the user.

    `tz_label: str | None`
    :   Label representing the timezone of the user.

    `tz_offset: int | None`
    :   Offset of the user's timezone.

    `updated: int | None`
    :   Timestamp of when the user's information was last updated.

    `who_can_share_contact_card: str | None`
    :   Specifies who can share the user's contact card.