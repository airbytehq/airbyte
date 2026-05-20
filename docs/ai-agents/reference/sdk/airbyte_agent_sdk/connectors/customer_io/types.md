---
id: airbyte_agent_sdk-connectors-customer_io-types
title: airbyte_agent_sdk.connectors.customer_io.types
---

Module airbyte_agent_sdk.connectors.customer_io.types
=====================================================
Type definitions for customer-io connector.

Classes
-------

<a id="ActivitiesListParams"></a>

`ActivitiesListParams(*args, **kwargs)`
:   Parameters for activities.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `start: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

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

<a id="BroadcastTriggerCreateParams"></a>

`BroadcastTriggerCreateParams(*args, **kwargs)`
:   Parameters for broadcast_trigger.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: str`
    :   The type of the None singleton.

    `data: dict[str, typing.Any]`
    :   The type of the None singleton.

    `data_file_url: str`
    :   The type of the None singleton.

    `email_add_duplicates: bool`
    :   The type of the None singleton.

    `email_ignore_missing: bool`
    :   The type of the None singleton.

    `emails: list[str]`
    :   The type of the None singleton.

    `id_ignore_missing: bool`
    :   The type of the None singleton.

    `ids: list[str]`
    :   The type of the None singleton.

    `per_user_data: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `recipients: dict[str, typing.Any]`
    :   The type of the None singleton.

<a id="CampaignActionsAndCondition"></a>

`CampaignActionsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsEqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsNeqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsGtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsGteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsLtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsLteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsInCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsLikeCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsFuzzyCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsKeywordCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsContainsCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsNotCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsAndCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsOrCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignActionsAnyCondition"></a>

`CampaignActionsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignActionsAnyValueFilter"></a>

`CampaignActionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bcc: Any`
    :   BCC addresses

    `body: Any`
    :   Action body content (HTML for emails)

    `campaign_id: Any`
    :   Parent campaign ID

    `created: Any`
    :   Creation timestamp (Unix)

    `deduplicate_id: Any`
    :   Deduplication identifier

    `editor: Any`
    :   Editor used to create the action

    `fake_bcc: Any`
    :   Whether to use fake BCC

    `from_: Any`
    :   From address

    `from_id: Any`
    :   Sender identity ID

    `headers: Any`
    :   Custom email headers as JSON

    `id: Any`
    :   Unique action identifier

    `language: Any`
    :   Language variant

    `layout: Any`
    :   Layout template used

    `name: Any`
    :   Action name

    `parent_action_id: Any`
    :   Parent action ID for language variants

    `preheader_text: Any`
    :   Email preheader/preview text

    `preprocessor: Any`
    :   CSS preprocessor setting

    `recipient: Any`
    :   Recipient address

    `recipient_environment_id: Any`
    :   Recipient environment ID

    `reply_to: Any`
    :   Reply-to address

    `reply_to_id: Any`
    :   Reply-to sender identity ID

    `request_method: Any`
    :   HTTP request method for webhook actions

    `sending_state: Any`
    :   Sending behavior (automatic or draft)

    `subject: Any`
    :   Email subject line

    `type_: Any`
    :   Action type (email, webhook, twilio, push, slack, in_app, whatsapp)

    `updated: Any`
    :   Last update timestamp (Unix)

    `url: Any`
    :   Webhook URL (for webhook actions)

<a id="CampaignActionsContainsCondition"></a>

`CampaignActionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignActionsEqCondition"></a>

`CampaignActionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignActionsFuzzyCondition"></a>

`CampaignActionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsStringFilter`
    :   The type of the None singleton.

<a id="CampaignActionsGetParams"></a>

`CampaignActionsGetParams(*args, **kwargs)`
:   Parameters for campaign_actions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action_id: str`
    :   The type of the None singleton.

    `campaign_id: str`
    :   The type of the None singleton.

<a id="CampaignActionsGtCondition"></a>

`CampaignActionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignActionsGteCondition"></a>

`CampaignActionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignActionsInCondition"></a>

`CampaignActionsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsInFilter`
    :   The type of the None singleton.

<a id="CampaignActionsInFilter"></a>

`CampaignActionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bcc: list[str]`
    :   BCC addresses

    `body: list[str]`
    :   Action body content (HTML for emails)

    `campaign_id: list[int]`
    :   Parent campaign ID

    `created: list[int]`
    :   Creation timestamp (Unix)

    `deduplicate_id: list[str]`
    :   Deduplication identifier

    `editor: list[str]`
    :   Editor used to create the action

    `fake_bcc: list[bool]`
    :   Whether to use fake BCC

    `from_: list[str]`
    :   From address

    `from_id: list[str]`
    :   Sender identity ID

    `headers: list[str]`
    :   Custom email headers as JSON

    `id: list[str]`
    :   Unique action identifier

    `language: list[str]`
    :   Language variant

    `layout: list[str]`
    :   Layout template used

    `name: list[str]`
    :   Action name

    `parent_action_id: list[int]`
    :   Parent action ID for language variants

    `preheader_text: list[str]`
    :   Email preheader/preview text

    `preprocessor: list[str]`
    :   CSS preprocessor setting

    `recipient: list[str]`
    :   Recipient address

    `recipient_environment_id: list[int]`
    :   Recipient environment ID

    `reply_to: list[str]`
    :   Reply-to address

    `reply_to_id: list[str]`
    :   Reply-to sender identity ID

    `request_method: list[str]`
    :   HTTP request method for webhook actions

    `sending_state: list[str]`
    :   Sending behavior (automatic or draft)

    `subject: list[str]`
    :   Email subject line

    `type_: list[str]`
    :   Action type (email, webhook, twilio, push, slack, in_app, whatsapp)

    `updated: list[int]`
    :   Last update timestamp (Unix)

    `url: list[str]`
    :   Webhook URL (for webhook actions)

<a id="CampaignActionsKeywordCondition"></a>

`CampaignActionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsStringFilter`
    :   The type of the None singleton.

<a id="CampaignActionsLikeCondition"></a>

`CampaignActionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsStringFilter`
    :   The type of the None singleton.

<a id="CampaignActionsListParams"></a>

`CampaignActionsListParams(*args, **kwargs)`
:   Parameters for campaign_actions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: str`
    :   The type of the None singleton.

    `start: str`
    :   The type of the None singleton.

<a id="CampaignActionsLtCondition"></a>

`CampaignActionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignActionsLteCondition"></a>

`CampaignActionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignActionsNeqCondition"></a>

`CampaignActionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignActionsNotCondition"></a>

`CampaignActionsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsEqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsNeqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsGtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsGteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsLtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsLteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsInCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsLikeCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsFuzzyCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsKeywordCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsContainsCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsNotCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsAndCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsOrCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsAnyCondition`
    :   The type of the None singleton.

<a id="CampaignActionsOrCondition"></a>

`CampaignActionsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsEqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsNeqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsGtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsGteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsLtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsLteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsInCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsLikeCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsFuzzyCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsKeywordCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsContainsCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsNotCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsAndCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsOrCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignActionsSearchFilter"></a>

`CampaignActionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaign_actions search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bcc: str | None`
    :   BCC addresses

    `body: str | None`
    :   Action body content (HTML for emails)

    `campaign_id: int | None`
    :   Parent campaign ID

    `created: int | None`
    :   Creation timestamp (Unix)

    `deduplicate_id: str | None`
    :   Deduplication identifier

    `editor: str | None`
    :   Editor used to create the action

    `fake_bcc: bool | None`
    :   Whether to use fake BCC

    `from_: str | None`
    :   From address

    `from_id: str | None`
    :   Sender identity ID

    `headers: str | None`
    :   Custom email headers as JSON

    `id: str | None`
    :   Unique action identifier

    `language: str | None`
    :   Language variant

    `layout: str | None`
    :   Layout template used

    `name: str | None`
    :   Action name

    `parent_action_id: int | None`
    :   Parent action ID for language variants

    `preheader_text: str | None`
    :   Email preheader/preview text

    `preprocessor: str | None`
    :   CSS preprocessor setting

    `recipient: str | None`
    :   Recipient address

    `recipient_environment_id: int | None`
    :   Recipient environment ID

    `reply_to: str | None`
    :   Reply-to address

    `reply_to_id: str | None`
    :   Reply-to sender identity ID

    `request_method: str | None`
    :   HTTP request method for webhook actions

    `sending_state: str | None`
    :   Sending behavior (automatic or draft)

    `subject: str | None`
    :   Email subject line

    `type_: str | None`
    :   Action type (email, webhook, twilio, push, slack, in_app, whatsapp)

    `updated: int | None`
    :   Last update timestamp (Unix)

    `url: str | None`
    :   Webhook URL (for webhook actions)

<a id="CampaignActionsSearchQuery"></a>

`CampaignActionsSearchQuery(*args, **kwargs)`
:   Search query for campaign_actions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsEqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsNeqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsGtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsGteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsLtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsLteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsInCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsLikeCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsFuzzyCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsKeywordCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsContainsCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsNotCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsAndCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsOrCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.customer_io.types.CampaignActionsSortFilter]`
    :   The type of the None singleton.

<a id="CampaignActionsSortFilter"></a>

`CampaignActionsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaign_actions search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bcc: Literal['asc', 'desc']`
    :   BCC addresses

    `body: Literal['asc', 'desc']`
    :   Action body content (HTML for emails)

    `campaign_id: Literal['asc', 'desc']`
    :   Parent campaign ID

    `created: Literal['asc', 'desc']`
    :   Creation timestamp (Unix)

    `deduplicate_id: Literal['asc', 'desc']`
    :   Deduplication identifier

    `editor: Literal['asc', 'desc']`
    :   Editor used to create the action

    `fake_bcc: Literal['asc', 'desc']`
    :   Whether to use fake BCC

    `from_: Literal['asc', 'desc']`
    :   From address

    `from_id: Literal['asc', 'desc']`
    :   Sender identity ID

    `headers: Literal['asc', 'desc']`
    :   Custom email headers as JSON

    `id: Literal['asc', 'desc']`
    :   Unique action identifier

    `language: Literal['asc', 'desc']`
    :   Language variant

    `layout: Literal['asc', 'desc']`
    :   Layout template used

    `name: Literal['asc', 'desc']`
    :   Action name

    `parent_action_id: Literal['asc', 'desc']`
    :   Parent action ID for language variants

    `preheader_text: Literal['asc', 'desc']`
    :   Email preheader/preview text

    `preprocessor: Literal['asc', 'desc']`
    :   CSS preprocessor setting

    `recipient: Literal['asc', 'desc']`
    :   Recipient address

    `recipient_environment_id: Literal['asc', 'desc']`
    :   Recipient environment ID

    `reply_to: Literal['asc', 'desc']`
    :   Reply-to address

    `reply_to_id: Literal['asc', 'desc']`
    :   Reply-to sender identity ID

    `request_method: Literal['asc', 'desc']`
    :   HTTP request method for webhook actions

    `sending_state: Literal['asc', 'desc']`
    :   Sending behavior (automatic or draft)

    `subject: Literal['asc', 'desc']`
    :   Email subject line

    `type_: Literal['asc', 'desc']`
    :   Action type (email, webhook, twilio, push, slack, in_app, whatsapp)

    `updated: Literal['asc', 'desc']`
    :   Last update timestamp (Unix)

    `url: Literal['asc', 'desc']`
    :   Webhook URL (for webhook actions)

<a id="CampaignActionsStringFilter"></a>

`CampaignActionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bcc: str`
    :   BCC addresses

    `body: str`
    :   Action body content (HTML for emails)

    `campaign_id: str`
    :   Parent campaign ID

    `created: str`
    :   Creation timestamp (Unix)

    `deduplicate_id: str`
    :   Deduplication identifier

    `editor: str`
    :   Editor used to create the action

    `fake_bcc: str`
    :   Whether to use fake BCC

    `from_: str`
    :   From address

    `from_id: str`
    :   Sender identity ID

    `headers: str`
    :   Custom email headers as JSON

    `id: str`
    :   Unique action identifier

    `language: str`
    :   Language variant

    `layout: str`
    :   Layout template used

    `name: str`
    :   Action name

    `parent_action_id: str`
    :   Parent action ID for language variants

    `preheader_text: str`
    :   Email preheader/preview text

    `preprocessor: str`
    :   CSS preprocessor setting

    `recipient: str`
    :   Recipient address

    `recipient_environment_id: str`
    :   Recipient environment ID

    `reply_to: str`
    :   Reply-to address

    `reply_to_id: str`
    :   Reply-to sender identity ID

    `request_method: str`
    :   HTTP request method for webhook actions

    `sending_state: str`
    :   Sending behavior (automatic or draft)

    `subject: str`
    :   Email subject line

    `type_: str`
    :   Action type (email, webhook, twilio, push, slack, in_app, whatsapp)

    `updated: str`
    :   Last update timestamp (Unix)

    `url: str`
    :   Webhook URL (for webhook actions)

<a id="CampaignsAndCondition"></a>

`CampaignsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.customer_io.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsInCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignsAnyCondition"></a>

`CampaignsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.customer_io.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsAnyValueFilter"></a>

`CampaignsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: Any`
    :   Actions defined in this campaign

    `active: Any`
    :   Whether the campaign is active

    `created: Any`
    :   Creation timestamp (Unix)

    `created_by: Any`
    :   Who created the campaign

    `date_attribute: Any`
    :   Date attribute used for date-triggered campaigns

    `deduplicate_id: Any`
    :   Deduplication identifier

    `event_name: Any`
    :   Event name that triggers the campaign

    `first_started: Any`
    :   When the campaign was first started (Unix)

    `frequency: Any`
    :   How frequently a person can receive this campaign

    `id: Any`
    :   Unique campaign identifier

    `msg_templates: Any`
    :   Message templates used in the campaign

    `name: Any`
    :   Campaign name

    `start_hour: Any`
    :   Hour of the day to trigger

    `start_minutes: Any`
    :   Minute of the hour to trigger

    `state: Any`
    :   Campaign status (draft, active, stopped)

    `tags: Any`
    :   Tags associated with the campaign

    `timezone: Any`
    :   Timezone for trigger scheduling

    `trigger_segment_ids: Any`
    :   Segment IDs that trigger this campaign

    `type_: Any`
    :   Campaign trigger type

    `updated: Any`
    :   Last update timestamp (Unix)

    `use_customer_timezone: Any`
    :   Whether to use the customer's timezone

<a id="CampaignsContainsCondition"></a>

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.customer_io.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsEqCondition"></a>

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.customer_io.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsFuzzyCondition"></a>

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.customer_io.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsGetParams"></a>

`CampaignsGetParams(*args, **kwargs)`
:   Parameters for campaigns.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: str`
    :   The type of the None singleton.

<a id="CampaignsGtCondition"></a>

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.customer_io.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsGteCondition"></a>

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.customer_io.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsInCondition"></a>

`CampaignsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.customer_io.types.CampaignsInFilter`
    :   The type of the None singleton.

<a id="CampaignsInFilter"></a>

`CampaignsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: list[list[typing.Any]]`
    :   Actions defined in this campaign

    `active: list[bool]`
    :   Whether the campaign is active

    `created: list[int]`
    :   Creation timestamp (Unix)

    `created_by: list[str]`
    :   Who created the campaign

    `date_attribute: list[str]`
    :   Date attribute used for date-triggered campaigns

    `deduplicate_id: list[str]`
    :   Deduplication identifier

    `event_name: list[str]`
    :   Event name that triggers the campaign

    `first_started: list[int]`
    :   When the campaign was first started (Unix)

    `frequency: list[str]`
    :   How frequently a person can receive this campaign

    `id: list[int]`
    :   Unique campaign identifier

    `msg_templates: list[list[typing.Any]]`
    :   Message templates used in the campaign

    `name: list[str]`
    :   Campaign name

    `start_hour: list[int]`
    :   Hour of the day to trigger

    `start_minutes: list[int]`
    :   Minute of the hour to trigger

    `state: list[str]`
    :   Campaign status (draft, active, stopped)

    `tags: list[list[typing.Any]]`
    :   Tags associated with the campaign

    `timezone: list[str]`
    :   Timezone for trigger scheduling

    `trigger_segment_ids: list[list[typing.Any]]`
    :   Segment IDs that trigger this campaign

    `type_: list[str]`
    :   Campaign trigger type

    `updated: list[int]`
    :   Last update timestamp (Unix)

    `use_customer_timezone: list[bool]`
    :   Whether to use the customer's timezone

<a id="CampaignsKeywordCondition"></a>

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.customer_io.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsLikeCondition"></a>

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.customer_io.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsListParams"></a>

`CampaignsListParams(*args, **kwargs)`
:   Parameters for campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="CampaignsLtCondition"></a>

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.customer_io.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsLteCondition"></a>

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.customer_io.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsNeqCondition"></a>

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.customer_io.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsNotCondition"></a>

`CampaignsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.customer_io.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsInCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsAnyCondition`
    :   The type of the None singleton.

<a id="CampaignsOrCondition"></a>

`CampaignsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.customer_io.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsInCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignsSearchFilter"></a>

`CampaignsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaigns search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: list[typing.Any] | None`
    :   Actions defined in this campaign

    `active: bool | None`
    :   Whether the campaign is active

    `created: int | None`
    :   Creation timestamp (Unix)

    `created_by: str | None`
    :   Who created the campaign

    `date_attribute: str | None`
    :   Date attribute used for date-triggered campaigns

    `deduplicate_id: str | None`
    :   Deduplication identifier

    `event_name: str | None`
    :   Event name that triggers the campaign

    `first_started: int | None`
    :   When the campaign was first started (Unix)

    `frequency: str | None`
    :   How frequently a person can receive this campaign

    `id: int | None`
    :   Unique campaign identifier

    `msg_templates: list[typing.Any] | None`
    :   Message templates used in the campaign

    `name: str | None`
    :   Campaign name

    `start_hour: int | None`
    :   Hour of the day to trigger

    `start_minutes: int | None`
    :   Minute of the hour to trigger

    `state: str | None`
    :   Campaign status (draft, active, stopped)

    `tags: list[typing.Any] | None`
    :   Tags associated with the campaign

    `timezone: str | None`
    :   Timezone for trigger scheduling

    `trigger_segment_ids: list[typing.Any] | None`
    :   Segment IDs that trigger this campaign

    `type_: str | None`
    :   Campaign trigger type

    `updated: int | None`
    :   Last update timestamp (Unix)

    `use_customer_timezone: bool | None`
    :   Whether to use the customer's timezone

<a id="CampaignsSearchQuery"></a>

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.customer_io.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsInCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.customer_io.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.customer_io.types.CampaignsSortFilter]`
    :   The type of the None singleton.

<a id="CampaignsSortFilter"></a>

`CampaignsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaigns search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: Literal['asc', 'desc']`
    :   Actions defined in this campaign

    `active: Literal['asc', 'desc']`
    :   Whether the campaign is active

    `created: Literal['asc', 'desc']`
    :   Creation timestamp (Unix)

    `created_by: Literal['asc', 'desc']`
    :   Who created the campaign

    `date_attribute: Literal['asc', 'desc']`
    :   Date attribute used for date-triggered campaigns

    `deduplicate_id: Literal['asc', 'desc']`
    :   Deduplication identifier

    `event_name: Literal['asc', 'desc']`
    :   Event name that triggers the campaign

    `first_started: Literal['asc', 'desc']`
    :   When the campaign was first started (Unix)

    `frequency: Literal['asc', 'desc']`
    :   How frequently a person can receive this campaign

    `id: Literal['asc', 'desc']`
    :   Unique campaign identifier

    `msg_templates: Literal['asc', 'desc']`
    :   Message templates used in the campaign

    `name: Literal['asc', 'desc']`
    :   Campaign name

    `start_hour: Literal['asc', 'desc']`
    :   Hour of the day to trigger

    `start_minutes: Literal['asc', 'desc']`
    :   Minute of the hour to trigger

    `state: Literal['asc', 'desc']`
    :   Campaign status (draft, active, stopped)

    `tags: Literal['asc', 'desc']`
    :   Tags associated with the campaign

    `timezone: Literal['asc', 'desc']`
    :   Timezone for trigger scheduling

    `trigger_segment_ids: Literal['asc', 'desc']`
    :   Segment IDs that trigger this campaign

    `type_: Literal['asc', 'desc']`
    :   Campaign trigger type

    `updated: Literal['asc', 'desc']`
    :   Last update timestamp (Unix)

    `use_customer_timezone: Literal['asc', 'desc']`
    :   Whether to use the customer's timezone

<a id="CampaignsStringFilter"></a>

`CampaignsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: str`
    :   Actions defined in this campaign

    `active: str`
    :   Whether the campaign is active

    `created: str`
    :   Creation timestamp (Unix)

    `created_by: str`
    :   Who created the campaign

    `date_attribute: str`
    :   Date attribute used for date-triggered campaigns

    `deduplicate_id: str`
    :   Deduplication identifier

    `event_name: str`
    :   Event name that triggers the campaign

    `first_started: str`
    :   When the campaign was first started (Unix)

    `frequency: str`
    :   How frequently a person can receive this campaign

    `id: str`
    :   Unique campaign identifier

    `msg_templates: str`
    :   Message templates used in the campaign

    `name: str`
    :   Campaign name

    `start_hour: str`
    :   Hour of the day to trigger

    `start_minutes: str`
    :   Minute of the hour to trigger

    `state: str`
    :   Campaign status (draft, active, stopped)

    `tags: str`
    :   Tags associated with the campaign

    `timezone: str`
    :   Timezone for trigger scheduling

    `trigger_segment_ids: str`
    :   Segment IDs that trigger this campaign

    `type_: str`
    :   Campaign trigger type

    `updated: str`
    :   Last update timestamp (Unix)

    `use_customer_timezone: str`
    :   Whether to use the customer's timezone

<a id="CollectionsCreateParams"></a>

`CollectionsCreateParams(*args, **kwargs)`
:   Parameters for collections.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `url: str`
    :   The type of the None singleton.

<a id="CollectionsGetParams"></a>

`CollectionsGetParams(*args, **kwargs)`
:   Parameters for collections.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_id: str`
    :   The type of the None singleton.

<a id="CollectionsListParams"></a>

`CollectionsListParams(*args, **kwargs)`
:   Parameters for collections.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="CollectionsUpdateParams"></a>

`CollectionsUpdateParams(*args, **kwargs)`
:   Parameters for collections.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_id: str`
    :   The type of the None singleton.

    `data: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `url: str`
    :   The type of the None singleton.

<a id="ExportsCreateParams"></a>

`ExportsCreateParams(*args, **kwargs)`
:   Parameters for exports.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filters: dict[str, typing.Any]`
    :   The type of the None singleton.

<a id="ExportsGetParams"></a>

`ExportsGetParams(*args, **kwargs)`
:   Parameters for exports.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `export_id: str`
    :   The type of the None singleton.

<a id="ExportsListParams"></a>

`ExportsListParams(*args, **kwargs)`
:   Parameters for exports.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="MessagesGetParams"></a>

`MessagesGetParams(*args, **kwargs)`
:   Parameters for messages.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `message_id: str`
    :   The type of the None singleton.

<a id="MessagesListParams"></a>

`MessagesListParams(*args, **kwargs)`
:   Parameters for messages.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: int`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `metric: str`
    :   The type of the None singleton.

    `newsletter_id: int`
    :   The type of the None singleton.

    `start: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="NewslettersAndCondition"></a>

`NewslettersAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.customer_io.types.NewslettersEqCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersNeqCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersGtCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersGteCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersLtCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersLteCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersInCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersLikeCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersFuzzyCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersKeywordCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersContainsCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersNotCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersAndCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersOrCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersAnyCondition]`
    :   The type of the None singleton.

<a id="NewslettersAnyCondition"></a>

`NewslettersAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.customer_io.types.NewslettersAnyValueFilter`
    :   The type of the None singleton.

<a id="NewslettersAnyValueFilter"></a>

`NewslettersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content_ids: Any`
    :   Content variant IDs for this newsletter

    `created: Any`
    :   Creation timestamp (Unix)

    `deduplicate_id: Any`
    :   Deduplication identifier

    `id: Any`
    :   Unique newsletter identifier

    `name: Any`
    :   Newsletter name

    `sent_at: Any`
    :   When the newsletter was last sent (Unix)

    `tags: Any`
    :   Tags associated with the newsletter

    `type_: Any`
    :   Channel type (email, webhook, twilio, push, in_app, inbox)

    `updated: Any`
    :   Last update timestamp (Unix)

<a id="NewslettersContainsCondition"></a>

`NewslettersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.customer_io.types.NewslettersAnyValueFilter`
    :   The type of the None singleton.

<a id="NewslettersEqCondition"></a>

`NewslettersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.customer_io.types.NewslettersSearchFilter`
    :   The type of the None singleton.

<a id="NewslettersFuzzyCondition"></a>

`NewslettersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.customer_io.types.NewslettersStringFilter`
    :   The type of the None singleton.

<a id="NewslettersGetParams"></a>

`NewslettersGetParams(*args, **kwargs)`
:   Parameters for newsletters.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `newsletter_id: str`
    :   The type of the None singleton.

<a id="NewslettersGtCondition"></a>

`NewslettersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.customer_io.types.NewslettersSearchFilter`
    :   The type of the None singleton.

<a id="NewslettersGteCondition"></a>

`NewslettersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.customer_io.types.NewslettersSearchFilter`
    :   The type of the None singleton.

<a id="NewslettersInCondition"></a>

`NewslettersInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.customer_io.types.NewslettersInFilter`
    :   The type of the None singleton.

<a id="NewslettersInFilter"></a>

`NewslettersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content_ids: list[list[typing.Any]]`
    :   Content variant IDs for this newsletter

    `created: list[int]`
    :   Creation timestamp (Unix)

    `deduplicate_id: list[str]`
    :   Deduplication identifier

    `id: list[int]`
    :   Unique newsletter identifier

    `name: list[str]`
    :   Newsletter name

    `sent_at: list[int]`
    :   When the newsletter was last sent (Unix)

    `tags: list[list[typing.Any]]`
    :   Tags associated with the newsletter

    `type_: list[str]`
    :   Channel type (email, webhook, twilio, push, in_app, inbox)

    `updated: list[int]`
    :   Last update timestamp (Unix)

<a id="NewslettersKeywordCondition"></a>

`NewslettersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.customer_io.types.NewslettersStringFilter`
    :   The type of the None singleton.

<a id="NewslettersLikeCondition"></a>

`NewslettersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.customer_io.types.NewslettersStringFilter`
    :   The type of the None singleton.

<a id="NewslettersListParams"></a>

`NewslettersListParams(*args, **kwargs)`
:   Parameters for newsletters.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

    `start: str`
    :   The type of the None singleton.

<a id="NewslettersLtCondition"></a>

`NewslettersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.customer_io.types.NewslettersSearchFilter`
    :   The type of the None singleton.

<a id="NewslettersLteCondition"></a>

`NewslettersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.customer_io.types.NewslettersSearchFilter`
    :   The type of the None singleton.

<a id="NewslettersNeqCondition"></a>

`NewslettersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.customer_io.types.NewslettersSearchFilter`
    :   The type of the None singleton.

<a id="NewslettersNotCondition"></a>

`NewslettersNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.customer_io.types.NewslettersEqCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersNeqCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersGtCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersGteCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersLtCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersLteCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersInCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersLikeCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersFuzzyCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersKeywordCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersContainsCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersNotCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersAndCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersOrCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersAnyCondition`
    :   The type of the None singleton.

<a id="NewslettersOrCondition"></a>

`NewslettersOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.customer_io.types.NewslettersEqCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersNeqCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersGtCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersGteCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersLtCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersLteCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersInCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersLikeCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersFuzzyCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersKeywordCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersContainsCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersNotCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersAndCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersOrCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersAnyCondition]`
    :   The type of the None singleton.

<a id="NewslettersSearchFilter"></a>

`NewslettersSearchFilter(*args, **kwargs)`
:   Available fields for filtering newsletters search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content_ids: list[typing.Any] | None`
    :   Content variant IDs for this newsletter

    `created: int | None`
    :   Creation timestamp (Unix)

    `deduplicate_id: str | None`
    :   Deduplication identifier

    `id: int | None`
    :   Unique newsletter identifier

    `name: str | None`
    :   Newsletter name

    `sent_at: int | None`
    :   When the newsletter was last sent (Unix)

    `tags: list[typing.Any] | None`
    :   Tags associated with the newsletter

    `type_: str | None`
    :   Channel type (email, webhook, twilio, push, in_app, inbox)

    `updated: int | None`
    :   Last update timestamp (Unix)

<a id="NewslettersSearchQuery"></a>

`NewslettersSearchQuery(*args, **kwargs)`
:   Search query for newsletters entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.customer_io.types.NewslettersEqCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersNeqCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersGtCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersGteCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersLtCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersLteCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersInCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersLikeCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersFuzzyCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersKeywordCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersContainsCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersNotCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersAndCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersOrCondition | airbyte_agent_sdk.connectors.customer_io.types.NewslettersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.customer_io.types.NewslettersSortFilter]`
    :   The type of the None singleton.

<a id="NewslettersSortFilter"></a>

`NewslettersSortFilter(*args, **kwargs)`
:   Available fields for sorting newsletters search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content_ids: Literal['asc', 'desc']`
    :   Content variant IDs for this newsletter

    `created: Literal['asc', 'desc']`
    :   Creation timestamp (Unix)

    `deduplicate_id: Literal['asc', 'desc']`
    :   Deduplication identifier

    `id: Literal['asc', 'desc']`
    :   Unique newsletter identifier

    `name: Literal['asc', 'desc']`
    :   Newsletter name

    `sent_at: Literal['asc', 'desc']`
    :   When the newsletter was last sent (Unix)

    `tags: Literal['asc', 'desc']`
    :   Tags associated with the newsletter

    `type_: Literal['asc', 'desc']`
    :   Channel type (email, webhook, twilio, push, in_app, inbox)

    `updated: Literal['asc', 'desc']`
    :   Last update timestamp (Unix)

<a id="NewslettersStringFilter"></a>

`NewslettersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content_ids: str`
    :   Content variant IDs for this newsletter

    `created: str`
    :   Creation timestamp (Unix)

    `deduplicate_id: str`
    :   Deduplication identifier

    `id: str`
    :   Unique newsletter identifier

    `name: str`
    :   Newsletter name

    `sent_at: str`
    :   When the newsletter was last sent (Unix)

    `tags: str`
    :   Tags associated with the newsletter

    `type_: str`
    :   Channel type (email, webhook, twilio, push, in_app, inbox)

    `updated: str`
    :   Last update timestamp (Unix)

<a id="ReportingWebhooksCreateParams"></a>

`ReportingWebhooksCreateParams(*args, **kwargs)`
:   Parameters for reporting_webhooks.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `disabled: bool`
    :   The type of the None singleton.

    `endpoint: str`
    :   The type of the None singleton.

    `events: list[str]`
    :   The type of the None singleton.

    `full_resolution: bool`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `with_content: bool`
    :   The type of the None singleton.

<a id="ReportingWebhooksGetParams"></a>

`ReportingWebhooksGetParams(*args, **kwargs)`
:   Parameters for reporting_webhooks.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `webhook_id: str`
    :   The type of the None singleton.

<a id="ReportingWebhooksListParams"></a>

`ReportingWebhooksListParams(*args, **kwargs)`
:   Parameters for reporting_webhooks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ReportingWebhooksUpdateParams"></a>

`ReportingWebhooksUpdateParams(*args, **kwargs)`
:   Parameters for reporting_webhooks.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `disabled: bool`
    :   The type of the None singleton.

    `endpoint: str`
    :   The type of the None singleton.

    `events: list[str]`
    :   The type of the None singleton.

    `full_resolution: bool`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `webhook_id: str`
    :   The type of the None singleton.

    `with_content: bool`
    :   The type of the None singleton.

<a id="SegmentsCreateParams"></a>

`SegmentsCreateParams(*args, **kwargs)`
:   Parameters for segments.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `segment: airbyte_agent_sdk.connectors.customer_io.types.SegmentsCreateParamsSegment`
    :   The type of the None singleton.

<a id="SegmentsCreateParamsSegment"></a>

`SegmentsCreateParamsSegment(*args, **kwargs)`
:   Nested schema for SegmentsCreateParams.segment

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="SegmentsGetParams"></a>

`SegmentsGetParams(*args, **kwargs)`
:   Parameters for segments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `segment_id: str`
    :   The type of the None singleton.

<a id="SegmentsListParams"></a>

`SegmentsListParams(*args, **kwargs)`
:   Parameters for segments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="SenderIdentitiesGetParams"></a>

`SenderIdentitiesGetParams(*args, **kwargs)`
:   Parameters for sender_identities.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `sender_id: str`
    :   The type of the None singleton.

<a id="SenderIdentitiesListParams"></a>

`SenderIdentitiesListParams(*args, **kwargs)`
:   Parameters for sender_identities.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

    `start: str`
    :   The type of the None singleton.

<a id="SnippetsCreateParams"></a>

`SnippetsCreateParams(*args, **kwargs)`
:   Parameters for snippets.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="SnippetsListParams"></a>

`SnippetsListParams(*args, **kwargs)`
:   Parameters for snippets.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="SnippetsUpdateParams"></a>

`SnippetsUpdateParams(*args, **kwargs)`
:   Parameters for snippets.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="TransactionalEmailCreateParams"></a>

`TransactionalEmailCreateParams(*args, **kwargs)`
:   Parameters for transactional_email.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: dict[str, typing.Any]`
    :   The type of the None singleton.

    `bcc: str`
    :   The type of the None singleton.

    `body: str`
    :   The type of the None singleton.

    `body_plain: str`
    :   The type of the None singleton.

    `disable_message_retention: bool`
    :   The type of the None singleton.

    `from_: str`
    :   The type of the None singleton.

    `headers: dict[str, typing.Any]`
    :   The type of the None singleton.

    `identifiers: dict[str, typing.Any]`
    :   The type of the None singleton.

    `message_data: dict[str, typing.Any]`
    :   The type of the None singleton.

    `preheader_text: str`
    :   The type of the None singleton.

    `queue_draft: bool`
    :   The type of the None singleton.

    `reply_to: str`
    :   The type of the None singleton.

    `send_at: int`
    :   The type of the None singleton.

    `send_to_unsubscribed: bool`
    :   The type of the None singleton.

    `subject: str`
    :   The type of the None singleton.

    `to: str`
    :   The type of the None singleton.

    `tracked: bool`
    :   The type of the None singleton.

    `transactional_message_id: Any`
    :   The type of the None singleton.

<a id="TransactionalInboxMessageCreateParams"></a>

`TransactionalInboxMessageCreateParams(*args, **kwargs)`
:   Parameters for transactional_inbox_message.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `identifiers: dict[str, typing.Any]`
    :   The type of the None singleton.

    `message_data: dict[str, typing.Any]`
    :   The type of the None singleton.

    `transactional_message_id: Any`
    :   The type of the None singleton.

<a id="TransactionalPushCreateParams"></a>

`TransactionalPushCreateParams(*args, **kwargs)`
:   Parameters for transactional_push.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `custom_data: dict[str, typing.Any]`
    :   The type of the None singleton.

    `custom_payload: dict[str, typing.Any]`
    :   The type of the None singleton.

    `disable_message_retention: bool`
    :   The type of the None singleton.

    `identifiers: dict[str, typing.Any]`
    :   The type of the None singleton.

    `image_url: str`
    :   The type of the None singleton.

    `link: str`
    :   The type of the None singleton.

    `message: str`
    :   The type of the None singleton.

    `message_data: dict[str, typing.Any]`
    :   The type of the None singleton.

    `queue_draft: bool`
    :   The type of the None singleton.

    `send_at: int`
    :   The type of the None singleton.

    `send_to_unsubscribed: bool`
    :   The type of the None singleton.

    `sound: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

    `to: str`
    :   The type of the None singleton.

    `transactional_message_id: Any`
    :   The type of the None singleton.

<a id="TransactionalSmsCreateParams"></a>

`TransactionalSmsCreateParams(*args, **kwargs)`
:   Parameters for transactional_sms.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `disable_message_retention: bool`
    :   The type of the None singleton.

    `from_: str`
    :   The type of the None singleton.

    `identifiers: dict[str, typing.Any]`
    :   The type of the None singleton.

    `message_data: dict[str, typing.Any]`
    :   The type of the None singleton.

    `queue_draft: bool`
    :   The type of the None singleton.

    `send_to_unsubscribed: bool`
    :   The type of the None singleton.

    `to: str`
    :   The type of the None singleton.

    `tracked: bool`
    :   The type of the None singleton.

    `transactional_message_id: Any`
    :   The type of the None singleton.