---
id: airbyte_agent_sdk-connectors-slack-types
title: airbyte_agent_sdk.connectors.slack.types
---

Module airbyte_agent_sdk.connectors.slack.types
===============================================
Type definitions for slack connector.

Classes
-------

<a id="AirbyteSearchParams"></a>

`AirbyteSearchParams(*args, **kwargs)`
:   Parameters for Airbyte cache search operations (generic, use entity-specific query types for better type hints).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `fields: list[list[str]]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `query: dict[str, typing.Any]`
    :   The type of the None singleton.

<a id="ChannelInvitesCreateParams"></a>

`ChannelInvitesCreateParams(*args, **kwargs)`
:   Parameters for channel_invites.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channel: str`
    :   The type of the None singleton.

    `force: bool`
    :   The type of the None singleton.

    `users: str`
    :   The type of the None singleton.

<a id="ChannelMessagesAndCondition"></a>

`ChannelMessagesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.slack.types.ChannelMessagesEqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesNeqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesGtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesGteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesLtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesLteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesInCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesLikeCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesKeywordCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesContainsCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesNotCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesAndCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesOrCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesAnyCondition]`
    :   The type of the None singleton.

<a id="ChannelMessagesAnyCondition"></a>

`ChannelMessagesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.slack.types.ChannelMessagesAnyValueFilter`
    :   The type of the None singleton.

<a id="ChannelMessagesAnyValueFilter"></a>

`ChannelMessagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: Any`
    :   Message attachments.

    `blocks: Any`
    :   Block kit blocks.

    `bot_id: Any`
    :   Bot ID if message was sent by a bot.

    `bot_profile: Any`
    :   Bot profile information.

    `is_locked: Any`
    :   Whether the thread is locked.

    `latest_reply: Any`
    :   Timestamp of latest reply.

    `reactions: Any`
    :   Reactions to the message.

    `reply_count: Any`
    :   Number of replies in thread.

    `reply_users: Any`
    :   User IDs who replied to the thread.

    `reply_users_count: Any`
    :   Number of unique users who replied.

    `subscribed: Any`
    :   Whether the user is subscribed to the thread.

    `subtype: Any`
    :   Message subtype.

    `team: Any`
    :   Team ID.

    `text: Any`
    :   Message text content.

    `thread_ts: Any`
    :   Thread parent timestamp.

    `ts: Any`
    :   Message timestamp (unique identifier).

    `type_: Any`
    :   Message type.

    `user: Any`
    :   User ID who sent the message.

<a id="ChannelMessagesContainsCondition"></a>

`ChannelMessagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.slack.types.ChannelMessagesAnyValueFilter`
    :   The type of the None singleton.

<a id="ChannelMessagesEqCondition"></a>

`ChannelMessagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.slack.types.ChannelMessagesSearchFilter`
    :   The type of the None singleton.

<a id="ChannelMessagesFuzzyCondition"></a>

`ChannelMessagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.slack.types.ChannelMessagesStringFilter`
    :   The type of the None singleton.

<a id="ChannelMessagesGtCondition"></a>

`ChannelMessagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.slack.types.ChannelMessagesSearchFilter`
    :   The type of the None singleton.

<a id="ChannelMessagesGteCondition"></a>

`ChannelMessagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.slack.types.ChannelMessagesSearchFilter`
    :   The type of the None singleton.

<a id="ChannelMessagesInCondition"></a>

`ChannelMessagesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.slack.types.ChannelMessagesInFilter`
    :   The type of the None singleton.

<a id="ChannelMessagesInFilter"></a>

`ChannelMessagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: list[list[typing.Any]]`
    :   Message attachments.

    `blocks: list[list[typing.Any]]`
    :   Block kit blocks.

    `bot_id: list[str]`
    :   Bot ID if message was sent by a bot.

    `bot_profile: list[dict[str, typing.Any]]`
    :   Bot profile information.

    `is_locked: list[bool]`
    :   Whether the thread is locked.

    `latest_reply: list[str]`
    :   Timestamp of latest reply.

    `reactions: list[list[typing.Any]]`
    :   Reactions to the message.

    `reply_count: list[int]`
    :   Number of replies in thread.

    `reply_users: list[list[typing.Any]]`
    :   User IDs who replied to the thread.

    `reply_users_count: list[int]`
    :   Number of unique users who replied.

    `subscribed: list[bool]`
    :   Whether the user is subscribed to the thread.

    `subtype: list[str]`
    :   Message subtype.

    `team: list[str]`
    :   Team ID.

    `text: list[str]`
    :   Message text content.

    `thread_ts: list[str]`
    :   Thread parent timestamp.

    `ts: list[str]`
    :   Message timestamp (unique identifier).

    `type_: list[str]`
    :   Message type.

    `user: list[str]`
    :   User ID who sent the message.

<a id="ChannelMessagesKeywordCondition"></a>

`ChannelMessagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.slack.types.ChannelMessagesStringFilter`
    :   The type of the None singleton.

<a id="ChannelMessagesLikeCondition"></a>

`ChannelMessagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.slack.types.ChannelMessagesStringFilter`
    :   The type of the None singleton.

<a id="ChannelMessagesListParams"></a>

`ChannelMessagesListParams(*args, **kwargs)`
:   Parameters for channel_messages.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channel: str`
    :   The type of the None singleton.

    `cursor: str`
    :   The type of the None singleton.

    `inclusive: bool`
    :   The type of the None singleton.

    `latest: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `oldest: str`
    :   The type of the None singleton.

<a id="ChannelMessagesLtCondition"></a>

`ChannelMessagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.slack.types.ChannelMessagesSearchFilter`
    :   The type of the None singleton.

<a id="ChannelMessagesLteCondition"></a>

`ChannelMessagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.slack.types.ChannelMessagesSearchFilter`
    :   The type of the None singleton.

<a id="ChannelMessagesNeqCondition"></a>

`ChannelMessagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.slack.types.ChannelMessagesSearchFilter`
    :   The type of the None singleton.

<a id="ChannelMessagesNotCondition"></a>

`ChannelMessagesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.slack.types.ChannelMessagesEqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesNeqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesGtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesGteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesLtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesLteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesInCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesLikeCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesKeywordCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesContainsCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesNotCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesAndCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesOrCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesAnyCondition`
    :   The type of the None singleton.

<a id="ChannelMessagesOrCondition"></a>

`ChannelMessagesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.slack.types.ChannelMessagesEqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesNeqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesGtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesGteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesLtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesLteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesInCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesLikeCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesKeywordCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesContainsCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesNotCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesAndCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesOrCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesAnyCondition]`
    :   The type of the None singleton.

<a id="ChannelMessagesSearchFilter"></a>

`ChannelMessagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering channel_messages search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="ChannelMessagesSearchQuery"></a>

`ChannelMessagesSearchQuery(*args, **kwargs)`
:   Search query for channel_messages entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.slack.types.ChannelMessagesEqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesNeqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesGtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesGteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesLtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesLteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesInCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesLikeCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesKeywordCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesContainsCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesNotCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesAndCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesOrCondition | airbyte_agent_sdk.connectors.slack.types.ChannelMessagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.slack.types.ChannelMessagesSortFilter]`
    :   The type of the None singleton.

<a id="ChannelMessagesSortFilter"></a>

`ChannelMessagesSortFilter(*args, **kwargs)`
:   Available fields for sorting channel_messages search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: Literal['asc', 'desc']`
    :   Message attachments.

    `blocks: Literal['asc', 'desc']`
    :   Block kit blocks.

    `bot_id: Literal['asc', 'desc']`
    :   Bot ID if message was sent by a bot.

    `bot_profile: Literal['asc', 'desc']`
    :   Bot profile information.

    `is_locked: Literal['asc', 'desc']`
    :   Whether the thread is locked.

    `latest_reply: Literal['asc', 'desc']`
    :   Timestamp of latest reply.

    `reactions: Literal['asc', 'desc']`
    :   Reactions to the message.

    `reply_count: Literal['asc', 'desc']`
    :   Number of replies in thread.

    `reply_users: Literal['asc', 'desc']`
    :   User IDs who replied to the thread.

    `reply_users_count: Literal['asc', 'desc']`
    :   Number of unique users who replied.

    `subscribed: Literal['asc', 'desc']`
    :   Whether the user is subscribed to the thread.

    `subtype: Literal['asc', 'desc']`
    :   Message subtype.

    `team: Literal['asc', 'desc']`
    :   Team ID.

    `text: Literal['asc', 'desc']`
    :   Message text content.

    `thread_ts: Literal['asc', 'desc']`
    :   Thread parent timestamp.

    `ts: Literal['asc', 'desc']`
    :   Message timestamp (unique identifier).

    `type_: Literal['asc', 'desc']`
    :   Message type.

    `user: Literal['asc', 'desc']`
    :   User ID who sent the message.

<a id="ChannelMessagesStringFilter"></a>

`ChannelMessagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: str`
    :   Message attachments.

    `blocks: str`
    :   Block kit blocks.

    `bot_id: str`
    :   Bot ID if message was sent by a bot.

    `bot_profile: str`
    :   Bot profile information.

    `is_locked: str`
    :   Whether the thread is locked.

    `latest_reply: str`
    :   Timestamp of latest reply.

    `reactions: str`
    :   Reactions to the message.

    `reply_count: str`
    :   Number of replies in thread.

    `reply_users: str`
    :   User IDs who replied to the thread.

    `reply_users_count: str`
    :   Number of unique users who replied.

    `subscribed: str`
    :   Whether the user is subscribed to the thread.

    `subtype: str`
    :   Message subtype.

    `team: str`
    :   Team ID.

    `text: str`
    :   Message text content.

    `thread_ts: str`
    :   Thread parent timestamp.

    `ts: str`
    :   Message timestamp (unique identifier).

    `type_: str`
    :   Message type.

    `user: str`
    :   User ID who sent the message.

<a id="ChannelPurposesCreateParams"></a>

`ChannelPurposesCreateParams(*args, **kwargs)`
:   Parameters for channel_purposes.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channel: str`
    :   The type of the None singleton.

    `purpose: str`
    :   The type of the None singleton.

<a id="ChannelTopicsCreateParams"></a>

`ChannelTopicsCreateParams(*args, **kwargs)`
:   Parameters for channel_topics.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channel: str`
    :   The type of the None singleton.

    `topic: str`
    :   The type of the None singleton.

<a id="ChannelsAndCondition"></a>

`ChannelsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.slack.types.ChannelsEqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsNeqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsGtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsGteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsLtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsLteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsInCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsLikeCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsKeywordCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsContainsCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsNotCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsAndCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsOrCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsAnyCondition]`
    :   The type of the None singleton.

<a id="ChannelsAnyCondition"></a>

`ChannelsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.slack.types.ChannelsAnyValueFilter`
    :   The type of the None singleton.

<a id="ChannelsAnyValueFilter"></a>

`ChannelsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `context_team_id: Any`
    :   The unique identifier of the team context in which the channel exists.

    `created: Any`
    :   The timestamp when the channel was created.

    `creator: Any`
    :   The ID of the user who created the channel.

    `id: Any`
    :   The unique identifier of the channel.

    `is_archived: Any`
    :   Indicates if the channel is archived.

    `is_channel: Any`
    :   Indicates if the entity is a channel.

    `is_ext_shared: Any`
    :   Indicates if the channel is externally shared.

    `is_general: Any`
    :   Indicates if the channel is a general channel in the workspace.

    `is_group: Any`
    :   Indicates if the channel is a group (private channel) rather than a regular channel.

    `is_im: Any`
    :   Indicates if the entity is a direct message (IM) channel.

    `is_member: Any`
    :   Indicates if the calling user is a member of the channel.

    `is_mpim: Any`
    :   Indicates if the entity is a multiple person direct message (MPIM) channel.

    `is_org_shared: Any`
    :   Indicates if the channel is organization-wide shared.

    `is_pending_ext_shared: Any`
    :   Indicates if the channel is pending external shared.

    `is_private: Any`
    :   Indicates if the channel is a private channel.

    `is_read_only: Any`
    :   Indicates if the channel is read-only.

    `is_shared: Any`
    :   Indicates if the channel is shared.

    `last_read: Any`
    :   The timestamp of the user's last read message in the channel.

    `locale: Any`
    :   The locale of the channel.

    `name: Any`
    :   The name of the channel.

    `name_normalized: Any`
    :   The normalized name of the channel.

    `num_members: Any`
    :   The number of members in the channel.

    `parent_conversation: Any`
    :   The parent conversation of the channel.

    `pending_connected_team_ids: Any`
    :   The IDs of teams that are pending to be connected to the channel.

    `pending_shared: Any`
    :   The list of pending shared items of the channel.

    `previous_names: Any`
    :   The previous names of the channel.

    `purpose: Any`
    :   The purpose of the channel.

    `shared_team_ids: Any`
    :   The IDs of teams with which the channel is shared.

    `topic: Any`
    :   The topic of the channel.

    `unlinked: Any`
    :   Indicates if the channel is unlinked.

    `updated: Any`
    :   The timestamp when the channel was last updated.

<a id="ChannelsContainsCondition"></a>

`ChannelsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.slack.types.ChannelsAnyValueFilter`
    :   The type of the None singleton.

<a id="ChannelsCreateParams"></a>

`ChannelsCreateParams(*args, **kwargs)`
:   Parameters for channels.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `is_private: bool`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="ChannelsEqCondition"></a>

`ChannelsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.slack.types.ChannelsSearchFilter`
    :   The type of the None singleton.

<a id="ChannelsFuzzyCondition"></a>

`ChannelsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.slack.types.ChannelsStringFilter`
    :   The type of the None singleton.

<a id="ChannelsGetParams"></a>

`ChannelsGetParams(*args, **kwargs)`
:   Parameters for channels.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channel: str`
    :   The type of the None singleton.

<a id="ChannelsGtCondition"></a>

`ChannelsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.slack.types.ChannelsSearchFilter`
    :   The type of the None singleton.

<a id="ChannelsGteCondition"></a>

`ChannelsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.slack.types.ChannelsSearchFilter`
    :   The type of the None singleton.

<a id="ChannelsInCondition"></a>

`ChannelsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.slack.types.ChannelsInFilter`
    :   The type of the None singleton.

<a id="ChannelsInFilter"></a>

`ChannelsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `context_team_id: list[str]`
    :   The unique identifier of the team context in which the channel exists.

    `created: list[int]`
    :   The timestamp when the channel was created.

    `creator: list[str]`
    :   The ID of the user who created the channel.

    `id: list[str]`
    :   The unique identifier of the channel.

    `is_archived: list[bool]`
    :   Indicates if the channel is archived.

    `is_channel: list[bool]`
    :   Indicates if the entity is a channel.

    `is_ext_shared: list[bool]`
    :   Indicates if the channel is externally shared.

    `is_general: list[bool]`
    :   Indicates if the channel is a general channel in the workspace.

    `is_group: list[bool]`
    :   Indicates if the channel is a group (private channel) rather than a regular channel.

    `is_im: list[bool]`
    :   Indicates if the entity is a direct message (IM) channel.

    `is_member: list[bool]`
    :   Indicates if the calling user is a member of the channel.

    `is_mpim: list[bool]`
    :   Indicates if the entity is a multiple person direct message (MPIM) channel.

    `is_org_shared: list[bool]`
    :   Indicates if the channel is organization-wide shared.

    `is_pending_ext_shared: list[bool]`
    :   Indicates if the channel is pending external shared.

    `is_private: list[bool]`
    :   Indicates if the channel is a private channel.

    `is_read_only: list[bool]`
    :   Indicates if the channel is read-only.

    `is_shared: list[bool]`
    :   Indicates if the channel is shared.

    `last_read: list[str]`
    :   The timestamp of the user's last read message in the channel.

    `locale: list[str]`
    :   The locale of the channel.

    `name: list[str]`
    :   The name of the channel.

    `name_normalized: list[str]`
    :   The normalized name of the channel.

    `num_members: list[int]`
    :   The number of members in the channel.

    `parent_conversation: list[str]`
    :   The parent conversation of the channel.

    `pending_connected_team_ids: list[list[typing.Any]]`
    :   The IDs of teams that are pending to be connected to the channel.

    `pending_shared: list[list[typing.Any]]`
    :   The list of pending shared items of the channel.

    `previous_names: list[list[typing.Any]]`
    :   The previous names of the channel.

    `purpose: list[dict[str, typing.Any]]`
    :   The purpose of the channel.

    `shared_team_ids: list[list[typing.Any]]`
    :   The IDs of teams with which the channel is shared.

    `topic: list[dict[str, typing.Any]]`
    :   The topic of the channel.

    `unlinked: list[int]`
    :   Indicates if the channel is unlinked.

    `updated: list[int]`
    :   The timestamp when the channel was last updated.

<a id="ChannelsKeywordCondition"></a>

`ChannelsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.slack.types.ChannelsStringFilter`
    :   The type of the None singleton.

<a id="ChannelsLikeCondition"></a>

`ChannelsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.slack.types.ChannelsStringFilter`
    :   The type of the None singleton.

<a id="ChannelsListParams"></a>

`ChannelsListParams(*args, **kwargs)`
:   Parameters for channels.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `exclude_archived: bool`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `types: str`
    :   The type of the None singleton.

<a id="ChannelsLtCondition"></a>

`ChannelsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.slack.types.ChannelsSearchFilter`
    :   The type of the None singleton.

<a id="ChannelsLteCondition"></a>

`ChannelsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.slack.types.ChannelsSearchFilter`
    :   The type of the None singleton.

<a id="ChannelsNeqCondition"></a>

`ChannelsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.slack.types.ChannelsSearchFilter`
    :   The type of the None singleton.

<a id="ChannelsNotCondition"></a>

`ChannelsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.slack.types.ChannelsEqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsNeqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsGtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsGteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsLtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsLteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsInCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsLikeCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsKeywordCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsContainsCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsNotCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsAndCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsOrCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsAnyCondition`
    :   The type of the None singleton.

<a id="ChannelsOrCondition"></a>

`ChannelsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.slack.types.ChannelsEqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsNeqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsGtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsGteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsLtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsLteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsInCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsLikeCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsKeywordCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsContainsCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsNotCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsAndCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsOrCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsAnyCondition]`
    :   The type of the None singleton.

<a id="ChannelsSearchFilter"></a>

`ChannelsSearchFilter(*args, **kwargs)`
:   Available fields for filtering channels search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="ChannelsSearchQuery"></a>

`ChannelsSearchQuery(*args, **kwargs)`
:   Search query for channels entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.slack.types.ChannelsEqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsNeqCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsGtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsGteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsLtCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsLteCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsInCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsLikeCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsKeywordCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsContainsCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsNotCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsAndCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsOrCondition | airbyte_agent_sdk.connectors.slack.types.ChannelsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.slack.types.ChannelsSortFilter]`
    :   The type of the None singleton.

<a id="ChannelsSortFilter"></a>

`ChannelsSortFilter(*args, **kwargs)`
:   Available fields for sorting channels search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `context_team_id: Literal['asc', 'desc']`
    :   The unique identifier of the team context in which the channel exists.

    `created: Literal['asc', 'desc']`
    :   The timestamp when the channel was created.

    `creator: Literal['asc', 'desc']`
    :   The ID of the user who created the channel.

    `id: Literal['asc', 'desc']`
    :   The unique identifier of the channel.

    `is_archived: Literal['asc', 'desc']`
    :   Indicates if the channel is archived.

    `is_channel: Literal['asc', 'desc']`
    :   Indicates if the entity is a channel.

    `is_ext_shared: Literal['asc', 'desc']`
    :   Indicates if the channel is externally shared.

    `is_general: Literal['asc', 'desc']`
    :   Indicates if the channel is a general channel in the workspace.

    `is_group: Literal['asc', 'desc']`
    :   Indicates if the channel is a group (private channel) rather than a regular channel.

    `is_im: Literal['asc', 'desc']`
    :   Indicates if the entity is a direct message (IM) channel.

    `is_member: Literal['asc', 'desc']`
    :   Indicates if the calling user is a member of the channel.

    `is_mpim: Literal['asc', 'desc']`
    :   Indicates if the entity is a multiple person direct message (MPIM) channel.

    `is_org_shared: Literal['asc', 'desc']`
    :   Indicates if the channel is organization-wide shared.

    `is_pending_ext_shared: Literal['asc', 'desc']`
    :   Indicates if the channel is pending external shared.

    `is_private: Literal['asc', 'desc']`
    :   Indicates if the channel is a private channel.

    `is_read_only: Literal['asc', 'desc']`
    :   Indicates if the channel is read-only.

    `is_shared: Literal['asc', 'desc']`
    :   Indicates if the channel is shared.

    `last_read: Literal['asc', 'desc']`
    :   The timestamp of the user's last read message in the channel.

    `locale: Literal['asc', 'desc']`
    :   The locale of the channel.

    `name: Literal['asc', 'desc']`
    :   The name of the channel.

    `name_normalized: Literal['asc', 'desc']`
    :   The normalized name of the channel.

    `num_members: Literal['asc', 'desc']`
    :   The number of members in the channel.

    `parent_conversation: Literal['asc', 'desc']`
    :   The parent conversation of the channel.

    `pending_connected_team_ids: Literal['asc', 'desc']`
    :   The IDs of teams that are pending to be connected to the channel.

    `pending_shared: Literal['asc', 'desc']`
    :   The list of pending shared items of the channel.

    `previous_names: Literal['asc', 'desc']`
    :   The previous names of the channel.

    `purpose: Literal['asc', 'desc']`
    :   The purpose of the channel.

    `shared_team_ids: Literal['asc', 'desc']`
    :   The IDs of teams with which the channel is shared.

    `topic: Literal['asc', 'desc']`
    :   The topic of the channel.

    `unlinked: Literal['asc', 'desc']`
    :   Indicates if the channel is unlinked.

    `updated: Literal['asc', 'desc']`
    :   The timestamp when the channel was last updated.

<a id="ChannelsStringFilter"></a>

`ChannelsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `context_team_id: str`
    :   The unique identifier of the team context in which the channel exists.

    `created: str`
    :   The timestamp when the channel was created.

    `creator: str`
    :   The ID of the user who created the channel.

    `id: str`
    :   The unique identifier of the channel.

    `is_archived: str`
    :   Indicates if the channel is archived.

    `is_channel: str`
    :   Indicates if the entity is a channel.

    `is_ext_shared: str`
    :   Indicates if the channel is externally shared.

    `is_general: str`
    :   Indicates if the channel is a general channel in the workspace.

    `is_group: str`
    :   Indicates if the channel is a group (private channel) rather than a regular channel.

    `is_im: str`
    :   Indicates if the entity is a direct message (IM) channel.

    `is_member: str`
    :   Indicates if the calling user is a member of the channel.

    `is_mpim: str`
    :   Indicates if the entity is a multiple person direct message (MPIM) channel.

    `is_org_shared: str`
    :   Indicates if the channel is organization-wide shared.

    `is_pending_ext_shared: str`
    :   Indicates if the channel is pending external shared.

    `is_private: str`
    :   Indicates if the channel is a private channel.

    `is_read_only: str`
    :   Indicates if the channel is read-only.

    `is_shared: str`
    :   Indicates if the channel is shared.

    `last_read: str`
    :   The timestamp of the user's last read message in the channel.

    `locale: str`
    :   The locale of the channel.

    `name: str`
    :   The name of the channel.

    `name_normalized: str`
    :   The normalized name of the channel.

    `num_members: str`
    :   The number of members in the channel.

    `parent_conversation: str`
    :   The parent conversation of the channel.

    `pending_connected_team_ids: str`
    :   The IDs of teams that are pending to be connected to the channel.

    `pending_shared: str`
    :   The list of pending shared items of the channel.

    `previous_names: str`
    :   The previous names of the channel.

    `purpose: str`
    :   The purpose of the channel.

    `shared_team_ids: str`
    :   The IDs of teams with which the channel is shared.

    `topic: str`
    :   The topic of the channel.

    `unlinked: str`
    :   Indicates if the channel is unlinked.

    `updated: str`
    :   The timestamp when the channel was last updated.

<a id="ChannelsUpdateParams"></a>

`ChannelsUpdateParams(*args, **kwargs)`
:   Parameters for channels.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channel: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="MessagesCreateParams"></a>

`MessagesCreateParams(*args, **kwargs)`
:   Parameters for messages.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channel: str`
    :   The type of the None singleton.

    `reply_broadcast: bool`
    :   The type of the None singleton.

    `text: str`
    :   The type of the None singleton.

    `thread_ts: str`
    :   The type of the None singleton.

    `unfurl_links: bool`
    :   The type of the None singleton.

    `unfurl_media: bool`
    :   The type of the None singleton.

<a id="MessagesUpdateParams"></a>

`MessagesUpdateParams(*args, **kwargs)`
:   Parameters for messages.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channel: str`
    :   The type of the None singleton.

    `text: str`
    :   The type of the None singleton.

    `ts: str`
    :   The type of the None singleton.

<a id="ReactionsCreateParams"></a>

`ReactionsCreateParams(*args, **kwargs)`
:   Parameters for reactions.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channel: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `timestamp: str`
    :   The type of the None singleton.

<a id="ThreadsAndCondition"></a>

`ThreadsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.slack.types.ThreadsEqCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsNeqCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsGtCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsGteCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsLtCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsLteCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsInCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsLikeCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsKeywordCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsContainsCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsNotCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsAndCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsOrCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsAnyCondition]`
    :   The type of the None singleton.

<a id="ThreadsAnyCondition"></a>

`ThreadsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.slack.types.ThreadsAnyValueFilter`
    :   The type of the None singleton.

<a id="ThreadsAnyValueFilter"></a>

`ThreadsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `blocks: Any`
    :   Block kit blocks.

    `bot_id: Any`
    :   Bot ID if message was sent by a bot.

    `is_locked: Any`
    :   Whether the thread is locked.

    `latest_reply: Any`
    :   Timestamp of latest reply.

    `parent_user_id: Any`
    :   User ID of the parent message author (present in thread replies).

    `reply_count: Any`
    :   Number of replies in thread.

    `reply_users: Any`
    :   User IDs who replied to the thread.

    `reply_users_count: Any`
    :   Number of unique users who replied.

    `subscribed: Any`
    :   Whether the user is subscribed to the thread.

    `subtype: Any`
    :   Message subtype.

    `team: Any`
    :   Team ID.

    `text: Any`
    :   Message text content.

    `thread_ts: Any`
    :   Thread parent timestamp.

    `ts: Any`
    :   Message timestamp (unique identifier).

    `type_: Any`
    :   Message type.

    `user: Any`
    :   User ID who sent the message.

<a id="ThreadsContainsCondition"></a>

`ThreadsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.slack.types.ThreadsAnyValueFilter`
    :   The type of the None singleton.

<a id="ThreadsEqCondition"></a>

`ThreadsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.slack.types.ThreadsSearchFilter`
    :   The type of the None singleton.

<a id="ThreadsFuzzyCondition"></a>

`ThreadsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.slack.types.ThreadsStringFilter`
    :   The type of the None singleton.

<a id="ThreadsGtCondition"></a>

`ThreadsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.slack.types.ThreadsSearchFilter`
    :   The type of the None singleton.

<a id="ThreadsGteCondition"></a>

`ThreadsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.slack.types.ThreadsSearchFilter`
    :   The type of the None singleton.

<a id="ThreadsInCondition"></a>

`ThreadsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.slack.types.ThreadsInFilter`
    :   The type of the None singleton.

<a id="ThreadsInFilter"></a>

`ThreadsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `blocks: list[list[typing.Any]]`
    :   Block kit blocks.

    `bot_id: list[str]`
    :   Bot ID if message was sent by a bot.

    `is_locked: list[bool]`
    :   Whether the thread is locked.

    `latest_reply: list[str]`
    :   Timestamp of latest reply.

    `parent_user_id: list[str]`
    :   User ID of the parent message author (present in thread replies).

    `reply_count: list[int]`
    :   Number of replies in thread.

    `reply_users: list[list[typing.Any]]`
    :   User IDs who replied to the thread.

    `reply_users_count: list[int]`
    :   Number of unique users who replied.

    `subscribed: list[bool]`
    :   Whether the user is subscribed to the thread.

    `subtype: list[str]`
    :   Message subtype.

    `team: list[str]`
    :   Team ID.

    `text: list[str]`
    :   Message text content.

    `thread_ts: list[str]`
    :   Thread parent timestamp.

    `ts: list[str]`
    :   Message timestamp (unique identifier).

    `type_: list[str]`
    :   Message type.

    `user: list[str]`
    :   User ID who sent the message.

<a id="ThreadsKeywordCondition"></a>

`ThreadsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.slack.types.ThreadsStringFilter`
    :   The type of the None singleton.

<a id="ThreadsLikeCondition"></a>

`ThreadsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.slack.types.ThreadsStringFilter`
    :   The type of the None singleton.

<a id="ThreadsListParams"></a>

`ThreadsListParams(*args, **kwargs)`
:   Parameters for threads.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channel: str`
    :   The type of the None singleton.

    `cursor: str`
    :   The type of the None singleton.

    `inclusive: bool`
    :   The type of the None singleton.

    `latest: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `oldest: str`
    :   The type of the None singleton.

    `ts: str`
    :   The type of the None singleton.

<a id="ThreadsLtCondition"></a>

`ThreadsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.slack.types.ThreadsSearchFilter`
    :   The type of the None singleton.

<a id="ThreadsLteCondition"></a>

`ThreadsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.slack.types.ThreadsSearchFilter`
    :   The type of the None singleton.

<a id="ThreadsNeqCondition"></a>

`ThreadsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.slack.types.ThreadsSearchFilter`
    :   The type of the None singleton.

<a id="ThreadsNotCondition"></a>

`ThreadsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.slack.types.ThreadsEqCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsNeqCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsGtCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsGteCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsLtCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsLteCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsInCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsLikeCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsKeywordCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsContainsCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsNotCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsAndCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsOrCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsAnyCondition`
    :   The type of the None singleton.

<a id="ThreadsOrCondition"></a>

`ThreadsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.slack.types.ThreadsEqCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsNeqCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsGtCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsGteCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsLtCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsLteCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsInCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsLikeCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsKeywordCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsContainsCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsNotCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsAndCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsOrCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsAnyCondition]`
    :   The type of the None singleton.

<a id="ThreadsSearchFilter"></a>

`ThreadsSearchFilter(*args, **kwargs)`
:   Available fields for filtering threads search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `blocks: list[typing.Any] | None`
    :   Block kit blocks.

    `bot_id: str | None`
    :   Bot ID if message was sent by a bot.

    `is_locked: bool | None`
    :   Whether the thread is locked.

    `latest_reply: str | None`
    :   Timestamp of latest reply.

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

<a id="ThreadsSearchQuery"></a>

`ThreadsSearchQuery(*args, **kwargs)`
:   Search query for threads entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.slack.types.ThreadsEqCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsNeqCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsGtCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsGteCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsLtCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsLteCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsInCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsLikeCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsKeywordCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsContainsCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsNotCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsAndCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsOrCondition | airbyte_agent_sdk.connectors.slack.types.ThreadsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.slack.types.ThreadsSortFilter]`
    :   The type of the None singleton.

<a id="ThreadsSortFilter"></a>

`ThreadsSortFilter(*args, **kwargs)`
:   Available fields for sorting threads search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `blocks: Literal['asc', 'desc']`
    :   Block kit blocks.

    `bot_id: Literal['asc', 'desc']`
    :   Bot ID if message was sent by a bot.

    `is_locked: Literal['asc', 'desc']`
    :   Whether the thread is locked.

    `latest_reply: Literal['asc', 'desc']`
    :   Timestamp of latest reply.

    `parent_user_id: Literal['asc', 'desc']`
    :   User ID of the parent message author (present in thread replies).

    `reply_count: Literal['asc', 'desc']`
    :   Number of replies in thread.

    `reply_users: Literal['asc', 'desc']`
    :   User IDs who replied to the thread.

    `reply_users_count: Literal['asc', 'desc']`
    :   Number of unique users who replied.

    `subscribed: Literal['asc', 'desc']`
    :   Whether the user is subscribed to the thread.

    `subtype: Literal['asc', 'desc']`
    :   Message subtype.

    `team: Literal['asc', 'desc']`
    :   Team ID.

    `text: Literal['asc', 'desc']`
    :   Message text content.

    `thread_ts: Literal['asc', 'desc']`
    :   Thread parent timestamp.

    `ts: Literal['asc', 'desc']`
    :   Message timestamp (unique identifier).

    `type_: Literal['asc', 'desc']`
    :   Message type.

    `user: Literal['asc', 'desc']`
    :   User ID who sent the message.

<a id="ThreadsStringFilter"></a>

`ThreadsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `blocks: str`
    :   Block kit blocks.

    `bot_id: str`
    :   Bot ID if message was sent by a bot.

    `is_locked: str`
    :   Whether the thread is locked.

    `latest_reply: str`
    :   Timestamp of latest reply.

    `parent_user_id: str`
    :   User ID of the parent message author (present in thread replies).

    `reply_count: str`
    :   Number of replies in thread.

    `reply_users: str`
    :   User IDs who replied to the thread.

    `reply_users_count: str`
    :   Number of unique users who replied.

    `subscribed: str`
    :   Whether the user is subscribed to the thread.

    `subtype: str`
    :   Message subtype.

    `team: str`
    :   Team ID.

    `text: str`
    :   Message text content.

    `thread_ts: str`
    :   Thread parent timestamp.

    `ts: str`
    :   Message timestamp (unique identifier).

    `type_: str`
    :   Message type.

    `user: str`
    :   User ID who sent the message.

<a id="UsersAndCondition"></a>

`UsersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.slack.types.UsersEqCondition | airbyte_agent_sdk.connectors.slack.types.UsersNeqCondition | airbyte_agent_sdk.connectors.slack.types.UsersGtCondition | airbyte_agent_sdk.connectors.slack.types.UsersGteCondition | airbyte_agent_sdk.connectors.slack.types.UsersLtCondition | airbyte_agent_sdk.connectors.slack.types.UsersLteCondition | airbyte_agent_sdk.connectors.slack.types.UsersInCondition | airbyte_agent_sdk.connectors.slack.types.UsersLikeCondition | airbyte_agent_sdk.connectors.slack.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.slack.types.UsersContainsCondition | airbyte_agent_sdk.connectors.slack.types.UsersNotCondition | airbyte_agent_sdk.connectors.slack.types.UsersAndCondition | airbyte_agent_sdk.connectors.slack.types.UsersOrCondition | airbyte_agent_sdk.connectors.slack.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersAnyCondition"></a>

`UsersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.slack.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersAnyValueFilter"></a>

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: Any`
    :   The color assigned to the user for visual purposes.

    `deleted: Any`
    :   Indicates if the user is deleted or not.

    `has_2fa: Any`
    :   Flag indicating if the user has two-factor authentication enabled.

    `id: Any`
    :   Unique identifier for the user.

    `is_admin: Any`
    :   Flag specifying if the user is an admin or not.

    `is_app_user: Any`
    :   Specifies if the user is an app user.

    `is_bot: Any`
    :   Indicates if the user is a bot account.

    `is_email_confirmed: Any`
    :   Flag indicating if the user's email is confirmed.

    `is_forgotten: Any`
    :   Specifies if the user is marked as forgotten.

    `is_invited_user: Any`
    :   Indicates if the user is invited or not.

    `is_owner: Any`
    :   Flag indicating if the user is an owner.

    `is_primary_owner: Any`
    :   Specifies if the user is the primary owner.

    `is_restricted: Any`
    :   Flag specifying if the user is restricted.

    `is_ultra_restricted: Any`
    :   Indicates if the user has ultra-restricted access.

    `name: Any`
    :   The username of the user.

    `profile: Any`
    :   User's profile information containing detailed details.

    `real_name: Any`
    :   The real name of the user.

    `team_id: Any`
    :   Unique identifier for the team the user belongs to.

    `tz: Any`
    :   Timezone of the user.

    `tz_label: Any`
    :   Label representing the timezone of the user.

    `tz_offset: Any`
    :   Offset of the user's timezone.

    `updated: Any`
    :   Timestamp of when the user's information was last updated.

    `who_can_share_contact_card: Any`
    :   Specifies who can share the user's contact card.

<a id="UsersContainsCondition"></a>

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.slack.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersEqCondition"></a>

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.slack.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersFuzzyCondition"></a>

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.slack.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersGetParams"></a>

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `user: str`
    :   The type of the None singleton.

<a id="UsersGtCondition"></a>

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.slack.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersGteCondition"></a>

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.slack.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersInCondition"></a>

`UsersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.slack.types.UsersInFilter`
    :   The type of the None singleton.

<a id="UsersInFilter"></a>

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: list[str]`
    :   The color assigned to the user for visual purposes.

    `deleted: list[bool]`
    :   Indicates if the user is deleted or not.

    `has_2fa: list[bool]`
    :   Flag indicating if the user has two-factor authentication enabled.

    `id: list[str]`
    :   Unique identifier for the user.

    `is_admin: list[bool]`
    :   Flag specifying if the user is an admin or not.

    `is_app_user: list[bool]`
    :   Specifies if the user is an app user.

    `is_bot: list[bool]`
    :   Indicates if the user is a bot account.

    `is_email_confirmed: list[bool]`
    :   Flag indicating if the user's email is confirmed.

    `is_forgotten: list[bool]`
    :   Specifies if the user is marked as forgotten.

    `is_invited_user: list[bool]`
    :   Indicates if the user is invited or not.

    `is_owner: list[bool]`
    :   Flag indicating if the user is an owner.

    `is_primary_owner: list[bool]`
    :   Specifies if the user is the primary owner.

    `is_restricted: list[bool]`
    :   Flag specifying if the user is restricted.

    `is_ultra_restricted: list[bool]`
    :   Indicates if the user has ultra-restricted access.

    `name: list[str]`
    :   The username of the user.

    `profile: list[dict[str, typing.Any]]`
    :   User's profile information containing detailed details.

    `real_name: list[str]`
    :   The real name of the user.

    `team_id: list[str]`
    :   Unique identifier for the team the user belongs to.

    `tz: list[str]`
    :   Timezone of the user.

    `tz_label: list[str]`
    :   Label representing the timezone of the user.

    `tz_offset: list[int]`
    :   Offset of the user's timezone.

    `updated: list[int]`
    :   Timestamp of when the user's information was last updated.

    `who_can_share_contact_card: list[str]`
    :   Specifies who can share the user's contact card.

<a id="UsersKeywordCondition"></a>

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.slack.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersLikeCondition"></a>

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.slack.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

<a id="UsersLtCondition"></a>

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.slack.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersLteCondition"></a>

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.slack.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNeqCondition"></a>

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.slack.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNotCondition"></a>

`UsersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.slack.types.UsersEqCondition | airbyte_agent_sdk.connectors.slack.types.UsersNeqCondition | airbyte_agent_sdk.connectors.slack.types.UsersGtCondition | airbyte_agent_sdk.connectors.slack.types.UsersGteCondition | airbyte_agent_sdk.connectors.slack.types.UsersLtCondition | airbyte_agent_sdk.connectors.slack.types.UsersLteCondition | airbyte_agent_sdk.connectors.slack.types.UsersInCondition | airbyte_agent_sdk.connectors.slack.types.UsersLikeCondition | airbyte_agent_sdk.connectors.slack.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.slack.types.UsersContainsCondition | airbyte_agent_sdk.connectors.slack.types.UsersNotCondition | airbyte_agent_sdk.connectors.slack.types.UsersAndCondition | airbyte_agent_sdk.connectors.slack.types.UsersOrCondition | airbyte_agent_sdk.connectors.slack.types.UsersAnyCondition`
    :   The type of the None singleton.

<a id="UsersOrCondition"></a>

`UsersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.slack.types.UsersEqCondition | airbyte_agent_sdk.connectors.slack.types.UsersNeqCondition | airbyte_agent_sdk.connectors.slack.types.UsersGtCondition | airbyte_agent_sdk.connectors.slack.types.UsersGteCondition | airbyte_agent_sdk.connectors.slack.types.UsersLtCondition | airbyte_agent_sdk.connectors.slack.types.UsersLteCondition | airbyte_agent_sdk.connectors.slack.types.UsersInCondition | airbyte_agent_sdk.connectors.slack.types.UsersLikeCondition | airbyte_agent_sdk.connectors.slack.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.slack.types.UsersContainsCondition | airbyte_agent_sdk.connectors.slack.types.UsersNotCondition | airbyte_agent_sdk.connectors.slack.types.UsersAndCondition | airbyte_agent_sdk.connectors.slack.types.UsersOrCondition | airbyte_agent_sdk.connectors.slack.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersSearchFilter"></a>

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="UsersSearchQuery"></a>

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.slack.types.UsersEqCondition | airbyte_agent_sdk.connectors.slack.types.UsersNeqCondition | airbyte_agent_sdk.connectors.slack.types.UsersGtCondition | airbyte_agent_sdk.connectors.slack.types.UsersGteCondition | airbyte_agent_sdk.connectors.slack.types.UsersLtCondition | airbyte_agent_sdk.connectors.slack.types.UsersLteCondition | airbyte_agent_sdk.connectors.slack.types.UsersInCondition | airbyte_agent_sdk.connectors.slack.types.UsersLikeCondition | airbyte_agent_sdk.connectors.slack.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.slack.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.slack.types.UsersContainsCondition | airbyte_agent_sdk.connectors.slack.types.UsersNotCondition | airbyte_agent_sdk.connectors.slack.types.UsersAndCondition | airbyte_agent_sdk.connectors.slack.types.UsersOrCondition | airbyte_agent_sdk.connectors.slack.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.slack.types.UsersSortFilter]`
    :   The type of the None singleton.

<a id="UsersSortFilter"></a>

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: Literal['asc', 'desc']`
    :   The color assigned to the user for visual purposes.

    `deleted: Literal['asc', 'desc']`
    :   Indicates if the user is deleted or not.

    `has_2fa: Literal['asc', 'desc']`
    :   Flag indicating if the user has two-factor authentication enabled.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the user.

    `is_admin: Literal['asc', 'desc']`
    :   Flag specifying if the user is an admin or not.

    `is_app_user: Literal['asc', 'desc']`
    :   Specifies if the user is an app user.

    `is_bot: Literal['asc', 'desc']`
    :   Indicates if the user is a bot account.

    `is_email_confirmed: Literal['asc', 'desc']`
    :   Flag indicating if the user's email is confirmed.

    `is_forgotten: Literal['asc', 'desc']`
    :   Specifies if the user is marked as forgotten.

    `is_invited_user: Literal['asc', 'desc']`
    :   Indicates if the user is invited or not.

    `is_owner: Literal['asc', 'desc']`
    :   Flag indicating if the user is an owner.

    `is_primary_owner: Literal['asc', 'desc']`
    :   Specifies if the user is the primary owner.

    `is_restricted: Literal['asc', 'desc']`
    :   Flag specifying if the user is restricted.

    `is_ultra_restricted: Literal['asc', 'desc']`
    :   Indicates if the user has ultra-restricted access.

    `name: Literal['asc', 'desc']`
    :   The username of the user.

    `profile: Literal['asc', 'desc']`
    :   User's profile information containing detailed details.

    `real_name: Literal['asc', 'desc']`
    :   The real name of the user.

    `team_id: Literal['asc', 'desc']`
    :   Unique identifier for the team the user belongs to.

    `tz: Literal['asc', 'desc']`
    :   Timezone of the user.

    `tz_label: Literal['asc', 'desc']`
    :   Label representing the timezone of the user.

    `tz_offset: Literal['asc', 'desc']`
    :   Offset of the user's timezone.

    `updated: Literal['asc', 'desc']`
    :   Timestamp of when the user's information was last updated.

    `who_can_share_contact_card: Literal['asc', 'desc']`
    :   Specifies who can share the user's contact card.

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The color assigned to the user for visual purposes.

    `deleted: str`
    :   Indicates if the user is deleted or not.

    `has_2fa: str`
    :   Flag indicating if the user has two-factor authentication enabled.

    `id: str`
    :   Unique identifier for the user.

    `is_admin: str`
    :   Flag specifying if the user is an admin or not.

    `is_app_user: str`
    :   Specifies if the user is an app user.

    `is_bot: str`
    :   Indicates if the user is a bot account.

    `is_email_confirmed: str`
    :   Flag indicating if the user's email is confirmed.

    `is_forgotten: str`
    :   Specifies if the user is marked as forgotten.

    `is_invited_user: str`
    :   Indicates if the user is invited or not.

    `is_owner: str`
    :   Flag indicating if the user is an owner.

    `is_primary_owner: str`
    :   Specifies if the user is the primary owner.

    `is_restricted: str`
    :   Flag specifying if the user is restricted.

    `is_ultra_restricted: str`
    :   Indicates if the user has ultra-restricted access.

    `name: str`
    :   The username of the user.

    `profile: str`
    :   User's profile information containing detailed details.

    `real_name: str`
    :   The real name of the user.

    `team_id: str`
    :   Unique identifier for the team the user belongs to.

    `tz: str`
    :   Timezone of the user.

    `tz_label: str`
    :   Label representing the timezone of the user.

    `tz_offset: str`
    :   Offset of the user's timezone.

    `updated: str`
    :   Timestamp of when the user's information was last updated.

    `who_can_share_contact_card: str`
    :   Specifies who can share the user's contact card.