---
id: airbyte_agent_sdk-connectors-zendesk_talk-types
title: airbyte_agent_sdk.connectors.zendesk_talk.types
---

Module airbyte_agent_sdk.connectors.zendesk_talk.types
======================================================
Type definitions for zendesk-talk connector.

Classes
-------

<a id="AccountOverviewAndCondition"></a>

`AccountOverviewAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewAnyCondition]`
    :   The type of the None singleton.

<a id="AccountOverviewAnyCondition"></a>

`AccountOverviewAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountOverviewAnyValueFilter"></a>

`AccountOverviewAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_call_duration: Any`
    :   Average call duration

    `average_callback_wait_time: Any`
    :   Average callback wait time

    `average_hold_time: Any`
    :   Average hold time per call

    `average_queue_wait_time: Any`
    :   Average queue wait time

    `average_time_to_answer: Any`
    :   Average time to answer

    `average_wrap_up_time: Any`
    :   Average wrap-up time

    `current_timestamp: Any`
    :   Current timestamp

    `max_calls_waiting: Any`
    :   Max calls waiting in queue

    `max_queue_wait_time: Any`
    :   Max queue wait time

    `total_call_duration: Any`
    :   Total call duration

    `total_callback_calls: Any`
    :   Total callback calls

    `total_calls: Any`
    :   Total calls

    `total_calls_abandoned_in_queue: Any`
    :   Total calls abandoned in queue

    `total_calls_outside_business_hours: Any`
    :   Total calls outside business hours

    `total_calls_with_exceeded_queue_wait_time: Any`
    :   Total calls exceeding max queue wait time

    `total_calls_with_requested_voicemail: Any`
    :   Total calls requesting voicemail

    `total_embeddable_callback_calls: Any`
    :   Total embeddable callback calls

    `total_hold_time: Any`
    :   Total hold time

    `total_inbound_calls: Any`
    :   Total inbound calls

    `total_outbound_calls: Any`
    :   Total outbound calls

    `total_textback_requests: Any`
    :   Total textback requests

    `total_voicemails: Any`
    :   Total voicemails

    `total_wrap_up_time: Any`
    :   Total wrap-up time

<a id="AccountOverviewContainsCondition"></a>

`AccountOverviewContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountOverviewEqCondition"></a>

`AccountOverviewEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewSearchFilter`
    :   The type of the None singleton.

<a id="AccountOverviewFuzzyCondition"></a>

`AccountOverviewFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewStringFilter`
    :   The type of the None singleton.

<a id="AccountOverviewGtCondition"></a>

`AccountOverviewGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewSearchFilter`
    :   The type of the None singleton.

<a id="AccountOverviewGteCondition"></a>

`AccountOverviewGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewSearchFilter`
    :   The type of the None singleton.

<a id="AccountOverviewInCondition"></a>

`AccountOverviewInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewInFilter`
    :   The type of the None singleton.

<a id="AccountOverviewInFilter"></a>

`AccountOverviewInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_call_duration: list[int]`
    :   Average call duration

    `average_callback_wait_time: list[int]`
    :   Average callback wait time

    `average_hold_time: list[int]`
    :   Average hold time per call

    `average_queue_wait_time: list[int]`
    :   Average queue wait time

    `average_time_to_answer: list[int]`
    :   Average time to answer

    `average_wrap_up_time: list[int]`
    :   Average wrap-up time

    `current_timestamp: list[int]`
    :   Current timestamp

    `max_calls_waiting: list[int]`
    :   Max calls waiting in queue

    `max_queue_wait_time: list[int]`
    :   Max queue wait time

    `total_call_duration: list[int]`
    :   Total call duration

    `total_callback_calls: list[int]`
    :   Total callback calls

    `total_calls: list[int]`
    :   Total calls

    `total_calls_abandoned_in_queue: list[int]`
    :   Total calls abandoned in queue

    `total_calls_outside_business_hours: list[int]`
    :   Total calls outside business hours

    `total_calls_with_exceeded_queue_wait_time: list[int]`
    :   Total calls exceeding max queue wait time

    `total_calls_with_requested_voicemail: list[int]`
    :   Total calls requesting voicemail

    `total_embeddable_callback_calls: list[int]`
    :   Total embeddable callback calls

    `total_hold_time: list[int]`
    :   Total hold time

    `total_inbound_calls: list[int]`
    :   Total inbound calls

    `total_outbound_calls: list[int]`
    :   Total outbound calls

    `total_textback_requests: list[int]`
    :   Total textback requests

    `total_voicemails: list[int]`
    :   Total voicemails

    `total_wrap_up_time: list[int]`
    :   Total wrap-up time

<a id="AccountOverviewKeywordCondition"></a>

`AccountOverviewKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewStringFilter`
    :   The type of the None singleton.

<a id="AccountOverviewLikeCondition"></a>

`AccountOverviewLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewStringFilter`
    :   The type of the None singleton.

<a id="AccountOverviewListParams"></a>

`AccountOverviewListParams(*args, **kwargs)`
:   Parameters for account_overview.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="AccountOverviewLtCondition"></a>

`AccountOverviewLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewSearchFilter`
    :   The type of the None singleton.

<a id="AccountOverviewLteCondition"></a>

`AccountOverviewLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewSearchFilter`
    :   The type of the None singleton.

<a id="AccountOverviewNeqCondition"></a>

`AccountOverviewNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewSearchFilter`
    :   The type of the None singleton.

<a id="AccountOverviewNotCondition"></a>

`AccountOverviewNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewAnyCondition`
    :   The type of the None singleton.

<a id="AccountOverviewOrCondition"></a>

`AccountOverviewOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewAnyCondition]`
    :   The type of the None singleton.

<a id="AccountOverviewSearchFilter"></a>

`AccountOverviewSearchFilter(*args, **kwargs)`
:   Available fields for filtering account_overview search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="AccountOverviewSearchQuery"></a>

`AccountOverviewSearchQuery(*args, **kwargs)`
:   Search query for account_overview entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_talk.types.AccountOverviewSortFilter]`
    :   The type of the None singleton.

<a id="AccountOverviewSortFilter"></a>

`AccountOverviewSortFilter(*args, **kwargs)`
:   Available fields for sorting account_overview search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_call_duration: Literal['asc', 'desc']`
    :   Average call duration

    `average_callback_wait_time: Literal['asc', 'desc']`
    :   Average callback wait time

    `average_hold_time: Literal['asc', 'desc']`
    :   Average hold time per call

    `average_queue_wait_time: Literal['asc', 'desc']`
    :   Average queue wait time

    `average_time_to_answer: Literal['asc', 'desc']`
    :   Average time to answer

    `average_wrap_up_time: Literal['asc', 'desc']`
    :   Average wrap-up time

    `current_timestamp: Literal['asc', 'desc']`
    :   Current timestamp

    `max_calls_waiting: Literal['asc', 'desc']`
    :   Max calls waiting in queue

    `max_queue_wait_time: Literal['asc', 'desc']`
    :   Max queue wait time

    `total_call_duration: Literal['asc', 'desc']`
    :   Total call duration

    `total_callback_calls: Literal['asc', 'desc']`
    :   Total callback calls

    `total_calls: Literal['asc', 'desc']`
    :   Total calls

    `total_calls_abandoned_in_queue: Literal['asc', 'desc']`
    :   Total calls abandoned in queue

    `total_calls_outside_business_hours: Literal['asc', 'desc']`
    :   Total calls outside business hours

    `total_calls_with_exceeded_queue_wait_time: Literal['asc', 'desc']`
    :   Total calls exceeding max queue wait time

    `total_calls_with_requested_voicemail: Literal['asc', 'desc']`
    :   Total calls requesting voicemail

    `total_embeddable_callback_calls: Literal['asc', 'desc']`
    :   Total embeddable callback calls

    `total_hold_time: Literal['asc', 'desc']`
    :   Total hold time

    `total_inbound_calls: Literal['asc', 'desc']`
    :   Total inbound calls

    `total_outbound_calls: Literal['asc', 'desc']`
    :   Total outbound calls

    `total_textback_requests: Literal['asc', 'desc']`
    :   Total textback requests

    `total_voicemails: Literal['asc', 'desc']`
    :   Total voicemails

    `total_wrap_up_time: Literal['asc', 'desc']`
    :   Total wrap-up time

<a id="AccountOverviewStringFilter"></a>

`AccountOverviewStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_call_duration: str`
    :   Average call duration

    `average_callback_wait_time: str`
    :   Average callback wait time

    `average_hold_time: str`
    :   Average hold time per call

    `average_queue_wait_time: str`
    :   Average queue wait time

    `average_time_to_answer: str`
    :   Average time to answer

    `average_wrap_up_time: str`
    :   Average wrap-up time

    `current_timestamp: str`
    :   Current timestamp

    `max_calls_waiting: str`
    :   Max calls waiting in queue

    `max_queue_wait_time: str`
    :   Max queue wait time

    `total_call_duration: str`
    :   Total call duration

    `total_callback_calls: str`
    :   Total callback calls

    `total_calls: str`
    :   Total calls

    `total_calls_abandoned_in_queue: str`
    :   Total calls abandoned in queue

    `total_calls_outside_business_hours: str`
    :   Total calls outside business hours

    `total_calls_with_exceeded_queue_wait_time: str`
    :   Total calls exceeding max queue wait time

    `total_calls_with_requested_voicemail: str`
    :   Total calls requesting voicemail

    `total_embeddable_callback_calls: str`
    :   Total embeddable callback calls

    `total_hold_time: str`
    :   Total hold time

    `total_inbound_calls: str`
    :   Total inbound calls

    `total_outbound_calls: str`
    :   Total outbound calls

    `total_textback_requests: str`
    :   Total textback requests

    `total_voicemails: str`
    :   Total voicemails

    `total_wrap_up_time: str`
    :   Total wrap-up time

<a id="AddressesAndCondition"></a>

`AddressesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesAnyCondition]`
    :   The type of the None singleton.

<a id="AddressesAnyCondition"></a>

`AddressesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesAnyValueFilter`
    :   The type of the None singleton.

<a id="AddressesAnyValueFilter"></a>

`AddressesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `city: Any`
    :   City of the address

    `country_code: Any`
    :   ISO country code

    `id: Any`
    :   Unique address identifier

    `name: Any`
    :   Name of the address

    `provider_reference: Any`
    :   Provider reference of the address

    `province: Any`
    :   Province of the address

    `state: Any`
    :   State of the address

    `street: Any`
    :   Street of the address

    `zip: Any`
    :   Zip code of the address

<a id="AddressesContainsCondition"></a>

`AddressesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesAnyValueFilter`
    :   The type of the None singleton.

<a id="AddressesEqCondition"></a>

`AddressesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesSearchFilter`
    :   The type of the None singleton.

<a id="AddressesFuzzyCondition"></a>

`AddressesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesStringFilter`
    :   The type of the None singleton.

<a id="AddressesGetParams"></a>

`AddressesGetParams(*args, **kwargs)`
:   Parameters for addresses.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address_id: str`
    :   The type of the None singleton.

<a id="AddressesGtCondition"></a>

`AddressesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesSearchFilter`
    :   The type of the None singleton.

<a id="AddressesGteCondition"></a>

`AddressesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesSearchFilter`
    :   The type of the None singleton.

<a id="AddressesInCondition"></a>

`AddressesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesInFilter`
    :   The type of the None singleton.

<a id="AddressesInFilter"></a>

`AddressesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `city: list[str]`
    :   City of the address

    `country_code: list[str]`
    :   ISO country code

    `id: list[int]`
    :   Unique address identifier

    `name: list[str]`
    :   Name of the address

    `provider_reference: list[str]`
    :   Provider reference of the address

    `province: list[str]`
    :   Province of the address

    `state: list[str]`
    :   State of the address

    `street: list[str]`
    :   Street of the address

    `zip: list[str]`
    :   Zip code of the address

<a id="AddressesKeywordCondition"></a>

`AddressesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesStringFilter`
    :   The type of the None singleton.

<a id="AddressesLikeCondition"></a>

`AddressesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesStringFilter`
    :   The type of the None singleton.

<a id="AddressesListParams"></a>

`AddressesListParams(*args, **kwargs)`
:   Parameters for addresses.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="AddressesLtCondition"></a>

`AddressesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesSearchFilter`
    :   The type of the None singleton.

<a id="AddressesLteCondition"></a>

`AddressesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesSearchFilter`
    :   The type of the None singleton.

<a id="AddressesNeqCondition"></a>

`AddressesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesSearchFilter`
    :   The type of the None singleton.

<a id="AddressesNotCondition"></a>

`AddressesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesAnyCondition`
    :   The type of the None singleton.

<a id="AddressesOrCondition"></a>

`AddressesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesAnyCondition]`
    :   The type of the None singleton.

<a id="AddressesSearchFilter"></a>

`AddressesSearchFilter(*args, **kwargs)`
:   Available fields for filtering addresses search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `city: str | None`
    :   City of the address

    `country_code: str | None`
    :   ISO country code

    `id: int | None`
    :   Unique address identifier

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

<a id="AddressesSearchQuery"></a>

`AddressesSearchQuery(*args, **kwargs)`
:   Search query for addresses entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_talk.types.AddressesSortFilter]`
    :   The type of the None singleton.

<a id="AddressesSortFilter"></a>

`AddressesSortFilter(*args, **kwargs)`
:   Available fields for sorting addresses search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `city: Literal['asc', 'desc']`
    :   City of the address

    `country_code: Literal['asc', 'desc']`
    :   ISO country code

    `id: Literal['asc', 'desc']`
    :   Unique address identifier

    `name: Literal['asc', 'desc']`
    :   Name of the address

    `provider_reference: Literal['asc', 'desc']`
    :   Provider reference of the address

    `province: Literal['asc', 'desc']`
    :   Province of the address

    `state: Literal['asc', 'desc']`
    :   State of the address

    `street: Literal['asc', 'desc']`
    :   Street of the address

    `zip: Literal['asc', 'desc']`
    :   Zip code of the address

<a id="AddressesStringFilter"></a>

`AddressesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `city: str`
    :   City of the address

    `country_code: str`
    :   ISO country code

    `id: str`
    :   Unique address identifier

    `name: str`
    :   Name of the address

    `provider_reference: str`
    :   Provider reference of the address

    `province: str`
    :   Province of the address

    `state: str`
    :   State of the address

    `street: str`
    :   Street of the address

    `zip: str`
    :   Zip code of the address

<a id="AgentsActivityAndCondition"></a>

`AgentsActivityAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityAnyCondition]`
    :   The type of the None singleton.

<a id="AgentsActivityAnyCondition"></a>

`AgentsActivityAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityAnyValueFilter`
    :   The type of the None singleton.

<a id="AgentsActivityAnyValueFilter"></a>

`AgentsActivityAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accepted_third_party_conferences: Any`
    :   Accepted third party conferences

    `accepted_transfers: Any`
    :   Total transfers accepted

    `agent_id: Any`
    :   Agent ID

    `agent_state: Any`
    :   Agent state: online, offline, away, or transfers_only

    `available_time: Any`
    :   Total time agent was available to answer calls

    `avatar_url: Any`
    :   URL to agent avatar

    `average_hold_time: Any`
    :   Average hold time per call

    `average_talk_time: Any`
    :   Average talk time per call

    `average_wrap_up_time: Any`
    :   Average wrap-up time per call

    `away_time: Any`
    :   Total time agent was set to away

    `call_status: Any`
    :   Agent call status: on_call, wrap_up, or null

    `calls_accepted: Any`
    :   Total calls accepted

    `calls_denied: Any`
    :   Total calls denied

    `calls_missed: Any`
    :   Total calls missed

    `calls_put_on_hold: Any`
    :   Total calls placed on hold

    `forwarding_number: Any`
    :   Forwarding number set by the agent

    `name: Any`
    :   Agent name

    `online_time: Any`
    :   Total online time

    `started_third_party_conferences: Any`
    :   Started third party conferences

    `started_transfers: Any`
    :   Total transfers started

    `total_call_duration: Any`
    :   Total call duration

    `total_hold_time: Any`
    :   Total hold time across all calls

    `total_talk_time: Any`
    :   Total talk time (excludes hold)

    `total_wrap_up_time: Any`
    :   Total wrap-up time

    `transfers_only_time: Any`
    :   Total time in transfers-only mode

    `via: Any`
    :   Channel the agent is registered on

<a id="AgentsActivityContainsCondition"></a>

`AgentsActivityContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityAnyValueFilter`
    :   The type of the None singleton.

<a id="AgentsActivityEqCondition"></a>

`AgentsActivityEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivitySearchFilter`
    :   The type of the None singleton.

<a id="AgentsActivityFuzzyCondition"></a>

`AgentsActivityFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityStringFilter`
    :   The type of the None singleton.

<a id="AgentsActivityGtCondition"></a>

`AgentsActivityGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivitySearchFilter`
    :   The type of the None singleton.

<a id="AgentsActivityGteCondition"></a>

`AgentsActivityGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivitySearchFilter`
    :   The type of the None singleton.

<a id="AgentsActivityInCondition"></a>

`AgentsActivityInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityInFilter`
    :   The type of the None singleton.

<a id="AgentsActivityInFilter"></a>

`AgentsActivityInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accepted_third_party_conferences: list[int]`
    :   Accepted third party conferences

    `accepted_transfers: list[int]`
    :   Total transfers accepted

    `agent_id: list[int]`
    :   Agent ID

    `agent_state: list[str]`
    :   Agent state: online, offline, away, or transfers_only

    `available_time: list[int]`
    :   Total time agent was available to answer calls

    `avatar_url: list[str]`
    :   URL to agent avatar

    `average_hold_time: list[int]`
    :   Average hold time per call

    `average_talk_time: list[int]`
    :   Average talk time per call

    `average_wrap_up_time: list[int]`
    :   Average wrap-up time per call

    `away_time: list[int]`
    :   Total time agent was set to away

    `call_status: list[str]`
    :   Agent call status: on_call, wrap_up, or null

    `calls_accepted: list[int]`
    :   Total calls accepted

    `calls_denied: list[int]`
    :   Total calls denied

    `calls_missed: list[int]`
    :   Total calls missed

    `calls_put_on_hold: list[int]`
    :   Total calls placed on hold

    `forwarding_number: list[str]`
    :   Forwarding number set by the agent

    `name: list[str]`
    :   Agent name

    `online_time: list[int]`
    :   Total online time

    `started_third_party_conferences: list[int]`
    :   Started third party conferences

    `started_transfers: list[int]`
    :   Total transfers started

    `total_call_duration: list[int]`
    :   Total call duration

    `total_hold_time: list[int]`
    :   Total hold time across all calls

    `total_talk_time: list[int]`
    :   Total talk time (excludes hold)

    `total_wrap_up_time: list[int]`
    :   Total wrap-up time

    `transfers_only_time: list[int]`
    :   Total time in transfers-only mode

    `via: list[str]`
    :   Channel the agent is registered on

<a id="AgentsActivityKeywordCondition"></a>

`AgentsActivityKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityStringFilter`
    :   The type of the None singleton.

<a id="AgentsActivityLikeCondition"></a>

`AgentsActivityLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityStringFilter`
    :   The type of the None singleton.

<a id="AgentsActivityListParams"></a>

`AgentsActivityListParams(*args, **kwargs)`
:   Parameters for agents_activity.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="AgentsActivityLtCondition"></a>

`AgentsActivityLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivitySearchFilter`
    :   The type of the None singleton.

<a id="AgentsActivityLteCondition"></a>

`AgentsActivityLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivitySearchFilter`
    :   The type of the None singleton.

<a id="AgentsActivityNeqCondition"></a>

`AgentsActivityNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivitySearchFilter`
    :   The type of the None singleton.

<a id="AgentsActivityNotCondition"></a>

`AgentsActivityNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityAnyCondition`
    :   The type of the None singleton.

<a id="AgentsActivityOrCondition"></a>

`AgentsActivityOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityAnyCondition]`
    :   The type of the None singleton.

<a id="AgentsActivitySearchFilter"></a>

`AgentsActivitySearchFilter(*args, **kwargs)`
:   Available fields for filtering agents_activity search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="AgentsActivitySearchQuery"></a>

`AgentsActivitySearchQuery(*args, **kwargs)`
:   Search query for agents_activity entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivityAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsActivitySortFilter]`
    :   The type of the None singleton.

<a id="AgentsActivitySortFilter"></a>

`AgentsActivitySortFilter(*args, **kwargs)`
:   Available fields for sorting agents_activity search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accepted_third_party_conferences: Literal['asc', 'desc']`
    :   Accepted third party conferences

    `accepted_transfers: Literal['asc', 'desc']`
    :   Total transfers accepted

    `agent_id: Literal['asc', 'desc']`
    :   Agent ID

    `agent_state: Literal['asc', 'desc']`
    :   Agent state: online, offline, away, or transfers_only

    `available_time: Literal['asc', 'desc']`
    :   Total time agent was available to answer calls

    `avatar_url: Literal['asc', 'desc']`
    :   URL to agent avatar

    `average_hold_time: Literal['asc', 'desc']`
    :   Average hold time per call

    `average_talk_time: Literal['asc', 'desc']`
    :   Average talk time per call

    `average_wrap_up_time: Literal['asc', 'desc']`
    :   Average wrap-up time per call

    `away_time: Literal['asc', 'desc']`
    :   Total time agent was set to away

    `call_status: Literal['asc', 'desc']`
    :   Agent call status: on_call, wrap_up, or null

    `calls_accepted: Literal['asc', 'desc']`
    :   Total calls accepted

    `calls_denied: Literal['asc', 'desc']`
    :   Total calls denied

    `calls_missed: Literal['asc', 'desc']`
    :   Total calls missed

    `calls_put_on_hold: Literal['asc', 'desc']`
    :   Total calls placed on hold

    `forwarding_number: Literal['asc', 'desc']`
    :   Forwarding number set by the agent

    `name: Literal['asc', 'desc']`
    :   Agent name

    `online_time: Literal['asc', 'desc']`
    :   Total online time

    `started_third_party_conferences: Literal['asc', 'desc']`
    :   Started third party conferences

    `started_transfers: Literal['asc', 'desc']`
    :   Total transfers started

    `total_call_duration: Literal['asc', 'desc']`
    :   Total call duration

    `total_hold_time: Literal['asc', 'desc']`
    :   Total hold time across all calls

    `total_talk_time: Literal['asc', 'desc']`
    :   Total talk time (excludes hold)

    `total_wrap_up_time: Literal['asc', 'desc']`
    :   Total wrap-up time

    `transfers_only_time: Literal['asc', 'desc']`
    :   Total time in transfers-only mode

    `via: Literal['asc', 'desc']`
    :   Channel the agent is registered on

<a id="AgentsActivityStringFilter"></a>

`AgentsActivityStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accepted_third_party_conferences: str`
    :   Accepted third party conferences

    `accepted_transfers: str`
    :   Total transfers accepted

    `agent_id: str`
    :   Agent ID

    `agent_state: str`
    :   Agent state: online, offline, away, or transfers_only

    `available_time: str`
    :   Total time agent was available to answer calls

    `avatar_url: str`
    :   URL to agent avatar

    `average_hold_time: str`
    :   Average hold time per call

    `average_talk_time: str`
    :   Average talk time per call

    `average_wrap_up_time: str`
    :   Average wrap-up time per call

    `away_time: str`
    :   Total time agent was set to away

    `call_status: str`
    :   Agent call status: on_call, wrap_up, or null

    `calls_accepted: str`
    :   Total calls accepted

    `calls_denied: str`
    :   Total calls denied

    `calls_missed: str`
    :   Total calls missed

    `calls_put_on_hold: str`
    :   Total calls placed on hold

    `forwarding_number: str`
    :   Forwarding number set by the agent

    `name: str`
    :   Agent name

    `online_time: str`
    :   Total online time

    `started_third_party_conferences: str`
    :   Started third party conferences

    `started_transfers: str`
    :   Total transfers started

    `total_call_duration: str`
    :   Total call duration

    `total_hold_time: str`
    :   Total hold time across all calls

    `total_talk_time: str`
    :   Total talk time (excludes hold)

    `total_wrap_up_time: str`
    :   Total wrap-up time

    `transfers_only_time: str`
    :   Total time in transfers-only mode

    `via: str`
    :   Channel the agent is registered on

<a id="AgentsOverviewAndCondition"></a>

`AgentsOverviewAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewAnyCondition]`
    :   The type of the None singleton.

<a id="AgentsOverviewAnyCondition"></a>

`AgentsOverviewAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewAnyValueFilter`
    :   The type of the None singleton.

<a id="AgentsOverviewAnyValueFilter"></a>

`AgentsOverviewAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_accepted_transfers: Any`
    :   Average accepted transfers

    `average_available_time: Any`
    :   Average available time

    `average_away_time: Any`
    :   Average away time

    `average_calls_accepted: Any`
    :   Average calls accepted

    `average_calls_denied: Any`
    :   Average calls denied

    `average_calls_missed: Any`
    :   Average calls missed

    `average_calls_put_on_hold: Any`
    :   Average calls put on hold

    `average_hold_time: Any`
    :   Average hold time

    `average_online_time: Any`
    :   Average online time

    `average_started_transfers: Any`
    :   Average started transfers

    `average_talk_time: Any`
    :   Average talk time

    `average_transfers_only_time: Any`
    :   Average transfers-only time

    `average_wrap_up_time: Any`
    :   Average wrap-up time

    `current_timestamp: Any`
    :   Current timestamp

    `total_accepted_transfers: Any`
    :   Total accepted transfers

    `total_calls_accepted: Any`
    :   Total calls accepted

    `total_calls_denied: Any`
    :   Total calls denied

    `total_calls_missed: Any`
    :   Total calls missed

    `total_calls_put_on_hold: Any`
    :   Total calls put on hold

    `total_hold_time: Any`
    :   Total hold time

    `total_started_transfers: Any`
    :   Total started transfers

    `total_talk_time: Any`
    :   Total talk time

    `total_wrap_up_time: Any`
    :   Total wrap-up time

<a id="AgentsOverviewContainsCondition"></a>

`AgentsOverviewContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewAnyValueFilter`
    :   The type of the None singleton.

<a id="AgentsOverviewEqCondition"></a>

`AgentsOverviewEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewSearchFilter`
    :   The type of the None singleton.

<a id="AgentsOverviewFuzzyCondition"></a>

`AgentsOverviewFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewStringFilter`
    :   The type of the None singleton.

<a id="AgentsOverviewGtCondition"></a>

`AgentsOverviewGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewSearchFilter`
    :   The type of the None singleton.

<a id="AgentsOverviewGteCondition"></a>

`AgentsOverviewGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewSearchFilter`
    :   The type of the None singleton.

<a id="AgentsOverviewInCondition"></a>

`AgentsOverviewInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewInFilter`
    :   The type of the None singleton.

<a id="AgentsOverviewInFilter"></a>

`AgentsOverviewInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_accepted_transfers: list[int]`
    :   Average accepted transfers

    `average_available_time: list[int]`
    :   Average available time

    `average_away_time: list[int]`
    :   Average away time

    `average_calls_accepted: list[int]`
    :   Average calls accepted

    `average_calls_denied: list[int]`
    :   Average calls denied

    `average_calls_missed: list[int]`
    :   Average calls missed

    `average_calls_put_on_hold: list[int]`
    :   Average calls put on hold

    `average_hold_time: list[int]`
    :   Average hold time

    `average_online_time: list[int]`
    :   Average online time

    `average_started_transfers: list[int]`
    :   Average started transfers

    `average_talk_time: list[int]`
    :   Average talk time

    `average_transfers_only_time: list[int]`
    :   Average transfers-only time

    `average_wrap_up_time: list[int]`
    :   Average wrap-up time

    `current_timestamp: list[int]`
    :   Current timestamp

    `total_accepted_transfers: list[int]`
    :   Total accepted transfers

    `total_calls_accepted: list[int]`
    :   Total calls accepted

    `total_calls_denied: list[int]`
    :   Total calls denied

    `total_calls_missed: list[int]`
    :   Total calls missed

    `total_calls_put_on_hold: list[int]`
    :   Total calls put on hold

    `total_hold_time: list[int]`
    :   Total hold time

    `total_started_transfers: list[int]`
    :   Total started transfers

    `total_talk_time: list[int]`
    :   Total talk time

    `total_wrap_up_time: list[int]`
    :   Total wrap-up time

<a id="AgentsOverviewKeywordCondition"></a>

`AgentsOverviewKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewStringFilter`
    :   The type of the None singleton.

<a id="AgentsOverviewLikeCondition"></a>

`AgentsOverviewLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewStringFilter`
    :   The type of the None singleton.

<a id="AgentsOverviewListParams"></a>

`AgentsOverviewListParams(*args, **kwargs)`
:   Parameters for agents_overview.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="AgentsOverviewLtCondition"></a>

`AgentsOverviewLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewSearchFilter`
    :   The type of the None singleton.

<a id="AgentsOverviewLteCondition"></a>

`AgentsOverviewLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewSearchFilter`
    :   The type of the None singleton.

<a id="AgentsOverviewNeqCondition"></a>

`AgentsOverviewNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewSearchFilter`
    :   The type of the None singleton.

<a id="AgentsOverviewNotCondition"></a>

`AgentsOverviewNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewAnyCondition`
    :   The type of the None singleton.

<a id="AgentsOverviewOrCondition"></a>

`AgentsOverviewOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewAnyCondition]`
    :   The type of the None singleton.

<a id="AgentsOverviewSearchFilter"></a>

`AgentsOverviewSearchFilter(*args, **kwargs)`
:   Available fields for filtering agents_overview search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="AgentsOverviewSearchQuery"></a>

`AgentsOverviewSearchQuery(*args, **kwargs)`
:   Search query for agents_overview entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_talk.types.AgentsOverviewSortFilter]`
    :   The type of the None singleton.

<a id="AgentsOverviewSortFilter"></a>

`AgentsOverviewSortFilter(*args, **kwargs)`
:   Available fields for sorting agents_overview search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_accepted_transfers: Literal['asc', 'desc']`
    :   Average accepted transfers

    `average_available_time: Literal['asc', 'desc']`
    :   Average available time

    `average_away_time: Literal['asc', 'desc']`
    :   Average away time

    `average_calls_accepted: Literal['asc', 'desc']`
    :   Average calls accepted

    `average_calls_denied: Literal['asc', 'desc']`
    :   Average calls denied

    `average_calls_missed: Literal['asc', 'desc']`
    :   Average calls missed

    `average_calls_put_on_hold: Literal['asc', 'desc']`
    :   Average calls put on hold

    `average_hold_time: Literal['asc', 'desc']`
    :   Average hold time

    `average_online_time: Literal['asc', 'desc']`
    :   Average online time

    `average_started_transfers: Literal['asc', 'desc']`
    :   Average started transfers

    `average_talk_time: Literal['asc', 'desc']`
    :   Average talk time

    `average_transfers_only_time: Literal['asc', 'desc']`
    :   Average transfers-only time

    `average_wrap_up_time: Literal['asc', 'desc']`
    :   Average wrap-up time

    `current_timestamp: Literal['asc', 'desc']`
    :   Current timestamp

    `total_accepted_transfers: Literal['asc', 'desc']`
    :   Total accepted transfers

    `total_calls_accepted: Literal['asc', 'desc']`
    :   Total calls accepted

    `total_calls_denied: Literal['asc', 'desc']`
    :   Total calls denied

    `total_calls_missed: Literal['asc', 'desc']`
    :   Total calls missed

    `total_calls_put_on_hold: Literal['asc', 'desc']`
    :   Total calls put on hold

    `total_hold_time: Literal['asc', 'desc']`
    :   Total hold time

    `total_started_transfers: Literal['asc', 'desc']`
    :   Total started transfers

    `total_talk_time: Literal['asc', 'desc']`
    :   Total talk time

    `total_wrap_up_time: Literal['asc', 'desc']`
    :   Total wrap-up time

<a id="AgentsOverviewStringFilter"></a>

`AgentsOverviewStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_accepted_transfers: str`
    :   Average accepted transfers

    `average_available_time: str`
    :   Average available time

    `average_away_time: str`
    :   Average away time

    `average_calls_accepted: str`
    :   Average calls accepted

    `average_calls_denied: str`
    :   Average calls denied

    `average_calls_missed: str`
    :   Average calls missed

    `average_calls_put_on_hold: str`
    :   Average calls put on hold

    `average_hold_time: str`
    :   Average hold time

    `average_online_time: str`
    :   Average online time

    `average_started_transfers: str`
    :   Average started transfers

    `average_talk_time: str`
    :   Average talk time

    `average_transfers_only_time: str`
    :   Average transfers-only time

    `average_wrap_up_time: str`
    :   Average wrap-up time

    `current_timestamp: str`
    :   Current timestamp

    `total_accepted_transfers: str`
    :   Total accepted transfers

    `total_calls_accepted: str`
    :   Total calls accepted

    `total_calls_denied: str`
    :   Total calls denied

    `total_calls_missed: str`
    :   Total calls missed

    `total_calls_put_on_hold: str`
    :   Total calls put on hold

    `total_hold_time: str`
    :   Total hold time

    `total_started_transfers: str`
    :   Total started transfers

    `total_talk_time: str`
    :   Total talk time

    `total_wrap_up_time: str`
    :   Total wrap-up time

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

<a id="CallLegsAndCondition"></a>

`CallLegsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsAnyCondition]`
    :   The type of the None singleton.

<a id="CallLegsAnyCondition"></a>

`CallLegsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsAnyValueFilter`
    :   The type of the None singleton.

<a id="CallLegsAnyValueFilter"></a>

`CallLegsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: Any`
    :   Agent ID

    `available_via: Any`
    :   Channel agent was available through

    `call_charge: Any`
    :   Call charge amount

    `call_id: Any`
    :   Associated call ID

    `completion_status: Any`
    :   Completion status

    `conference_from: Any`
    :   Conference from time

    `conference_time: Any`
    :   Conference duration

    `conference_to: Any`
    :   Conference to time

    `consultation_from: Any`
    :   Consultation from time

    `consultation_time: Any`
    :   Consultation duration

    `consultation_to: Any`
    :   Consultation to time

    `created_at: Any`
    :   Creation timestamp

    `duration: Any`
    :   Duration in seconds

    `forwarded_to: Any`
    :   Number forwarded to

    `hold_time: Any`
    :   Hold time in seconds

    `id: Any`
    :   Call leg ID

    `minutes_billed: Any`
    :   Minutes billed

    `quality_issues: Any`
    :   Quality issues detected

    `talk_time: Any`
    :   Talk time in seconds

    `transferred_from: Any`
    :   Transferred from agent ID

    `transferred_to: Any`
    :   Transferred to agent ID

    `type_: Any`
    :   Type of call leg

    `updated_at: Any`
    :   Last update timestamp

    `user_id: Any`
    :   User ID

    `wrap_up_time: Any`
    :   Wrap-up time in seconds

<a id="CallLegsContainsCondition"></a>

`CallLegsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsAnyValueFilter`
    :   The type of the None singleton.

<a id="CallLegsEqCondition"></a>

`CallLegsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsSearchFilter`
    :   The type of the None singleton.

<a id="CallLegsFuzzyCondition"></a>

`CallLegsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsStringFilter`
    :   The type of the None singleton.

<a id="CallLegsGtCondition"></a>

`CallLegsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsSearchFilter`
    :   The type of the None singleton.

<a id="CallLegsGteCondition"></a>

`CallLegsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsSearchFilter`
    :   The type of the None singleton.

<a id="CallLegsInCondition"></a>

`CallLegsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsInFilter`
    :   The type of the None singleton.

<a id="CallLegsInFilter"></a>

`CallLegsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: list[int]`
    :   Agent ID

    `available_via: list[str]`
    :   Channel agent was available through

    `call_charge: list[str]`
    :   Call charge amount

    `call_id: list[int]`
    :   Associated call ID

    `completion_status: list[str]`
    :   Completion status

    `conference_from: list[int]`
    :   Conference from time

    `conference_time: list[int]`
    :   Conference duration

    `conference_to: list[int]`
    :   Conference to time

    `consultation_from: list[int]`
    :   Consultation from time

    `consultation_time: list[int]`
    :   Consultation duration

    `consultation_to: list[int]`
    :   Consultation to time

    `created_at: list[str]`
    :   Creation timestamp

    `duration: list[int]`
    :   Duration in seconds

    `forwarded_to: list[str]`
    :   Number forwarded to

    `hold_time: list[int]`
    :   Hold time in seconds

    `id: list[int]`
    :   Call leg ID

    `minutes_billed: list[int]`
    :   Minutes billed

    `quality_issues: list[list[typing.Any]]`
    :   Quality issues detected

    `talk_time: list[int]`
    :   Talk time in seconds

    `transferred_from: list[int]`
    :   Transferred from agent ID

    `transferred_to: list[int]`
    :   Transferred to agent ID

    `type_: list[str]`
    :   Type of call leg

    `updated_at: list[str]`
    :   Last update timestamp

    `user_id: list[int]`
    :   User ID

    `wrap_up_time: list[int]`
    :   Wrap-up time in seconds

<a id="CallLegsKeywordCondition"></a>

`CallLegsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsStringFilter`
    :   The type of the None singleton.

<a id="CallLegsLikeCondition"></a>

`CallLegsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsStringFilter`
    :   The type of the None singleton.

<a id="CallLegsListParams"></a>

`CallLegsListParams(*args, **kwargs)`
:   Parameters for call_legs.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `start_time: int`
    :   The type of the None singleton.

<a id="CallLegsLtCondition"></a>

`CallLegsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsSearchFilter`
    :   The type of the None singleton.

<a id="CallLegsLteCondition"></a>

`CallLegsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsSearchFilter`
    :   The type of the None singleton.

<a id="CallLegsNeqCondition"></a>

`CallLegsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsSearchFilter`
    :   The type of the None singleton.

<a id="CallLegsNotCondition"></a>

`CallLegsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsAnyCondition`
    :   The type of the None singleton.

<a id="CallLegsOrCondition"></a>

`CallLegsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsAnyCondition]`
    :   The type of the None singleton.

<a id="CallLegsSearchFilter"></a>

`CallLegsSearchFilter(*args, **kwargs)`
:   Available fields for filtering call_legs search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CallLegsSearchQuery"></a>

`CallLegsSearchQuery(*args, **kwargs)`
:   Search query for call_legs entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_talk.types.CallLegsSortFilter]`
    :   The type of the None singleton.

<a id="CallLegsSortFilter"></a>

`CallLegsSortFilter(*args, **kwargs)`
:   Available fields for sorting call_legs search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: Literal['asc', 'desc']`
    :   Agent ID

    `available_via: Literal['asc', 'desc']`
    :   Channel agent was available through

    `call_charge: Literal['asc', 'desc']`
    :   Call charge amount

    `call_id: Literal['asc', 'desc']`
    :   Associated call ID

    `completion_status: Literal['asc', 'desc']`
    :   Completion status

    `conference_from: Literal['asc', 'desc']`
    :   Conference from time

    `conference_time: Literal['asc', 'desc']`
    :   Conference duration

    `conference_to: Literal['asc', 'desc']`
    :   Conference to time

    `consultation_from: Literal['asc', 'desc']`
    :   Consultation from time

    `consultation_time: Literal['asc', 'desc']`
    :   Consultation duration

    `consultation_to: Literal['asc', 'desc']`
    :   Consultation to time

    `created_at: Literal['asc', 'desc']`
    :   Creation timestamp

    `duration: Literal['asc', 'desc']`
    :   Duration in seconds

    `forwarded_to: Literal['asc', 'desc']`
    :   Number forwarded to

    `hold_time: Literal['asc', 'desc']`
    :   Hold time in seconds

    `id: Literal['asc', 'desc']`
    :   Call leg ID

    `minutes_billed: Literal['asc', 'desc']`
    :   Minutes billed

    `quality_issues: Literal['asc', 'desc']`
    :   Quality issues detected

    `talk_time: Literal['asc', 'desc']`
    :   Talk time in seconds

    `transferred_from: Literal['asc', 'desc']`
    :   Transferred from agent ID

    `transferred_to: Literal['asc', 'desc']`
    :   Transferred to agent ID

    `type_: Literal['asc', 'desc']`
    :   Type of call leg

    `updated_at: Literal['asc', 'desc']`
    :   Last update timestamp

    `user_id: Literal['asc', 'desc']`
    :   User ID

    `wrap_up_time: Literal['asc', 'desc']`
    :   Wrap-up time in seconds

<a id="CallLegsStringFilter"></a>

`CallLegsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: str`
    :   Agent ID

    `available_via: str`
    :   Channel agent was available through

    `call_charge: str`
    :   Call charge amount

    `call_id: str`
    :   Associated call ID

    `completion_status: str`
    :   Completion status

    `conference_from: str`
    :   Conference from time

    `conference_time: str`
    :   Conference duration

    `conference_to: str`
    :   Conference to time

    `consultation_from: str`
    :   Consultation from time

    `consultation_time: str`
    :   Consultation duration

    `consultation_to: str`
    :   Consultation to time

    `created_at: str`
    :   Creation timestamp

    `duration: str`
    :   Duration in seconds

    `forwarded_to: str`
    :   Number forwarded to

    `hold_time: str`
    :   Hold time in seconds

    `id: str`
    :   Call leg ID

    `minutes_billed: str`
    :   Minutes billed

    `quality_issues: str`
    :   Quality issues detected

    `talk_time: str`
    :   Talk time in seconds

    `transferred_from: str`
    :   Transferred from agent ID

    `transferred_to: str`
    :   Transferred to agent ID

    `type_: str`
    :   Type of call leg

    `updated_at: str`
    :   Last update timestamp

    `user_id: str`
    :   User ID

    `wrap_up_time: str`
    :   Wrap-up time in seconds

<a id="CallsAndCondition"></a>

`CallsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.zendesk_talk.types.CallsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsAnyCondition]`
    :   The type of the None singleton.

<a id="CallsAnyCondition"></a>

`CallsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.zendesk_talk.types.CallsAnyValueFilter`
    :   The type of the None singleton.

<a id="CallsAnyValueFilter"></a>

`CallsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: Any`
    :   Agent ID

    `call_charge: Any`
    :   Call charge amount

    `call_group_id: Any`
    :   Call group ID

    `call_recording_consent: Any`
    :   Call recording consent status

    `call_recording_consent_action: Any`
    :   Recording consent action

    `call_recording_consent_keypress: Any`
    :   Recording consent keypress

    `callback: Any`
    :   Whether this was a callback

    `callback_source: Any`
    :   Source of the callback

    `completion_status: Any`
    :   Call completion status

    `consultation_time: Any`
    :   Consultation time

    `created_at: Any`
    :   Creation timestamp

    `customer_requested_voicemail: Any`
    :   Whether customer requested voicemail

    `default_group: Any`
    :   Whether default group was used

    `direction: Any`
    :   Call direction (inbound/outbound)

    `duration: Any`
    :   Call duration in seconds

    `exceeded_queue_time: Any`
    :   Whether queue time was exceeded

    `exceeded_queue_wait_time: Any`
    :   Whether max queue wait time was exceeded

    `hold_time: Any`
    :   Hold time in seconds

    `id: Any`
    :   Call ID

    `ivr_action: Any`
    :   IVR action taken

    `ivr_destination_group_name: Any`
    :   IVR destination group name

    `ivr_hops: Any`
    :   Number of IVR hops

    `ivr_routed_to: Any`
    :   Where IVR routed the call

    `ivr_time_spent: Any`
    :   Time spent in IVR

    `minutes_billed: Any`
    :   Minutes billed

    `not_recording_time: Any`
    :   Time not recording

    `outside_business_hours: Any`
    :   Whether call was outside business hours

    `overflowed: Any`
    :   Whether call overflowed

    `overflowed_to: Any`
    :   Where call overflowed to

    `phone_number: Any`
    :   Phone number used

    `phone_number_id: Any`
    :   Phone number ID

    `quality_issues: Any`
    :   Quality issues detected

    `recording_control_interactions: Any`
    :   Recording control interactions count

    `recording_time: Any`
    :   Recording time

    `talk_time: Any`
    :   Talk time in seconds

    `ticket_id: Any`
    :   Associated ticket ID

    `time_to_answer: Any`
    :   Time to answer in seconds

    `updated_at: Any`
    :   Last update timestamp

    `voicemail: Any`
    :   Whether it was a voicemail

    `wait_time: Any`
    :   Wait time in seconds

    `wrap_up_time: Any`
    :   Wrap-up time in seconds

<a id="CallsContainsCondition"></a>

`CallsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_talk.types.CallsAnyValueFilter`
    :   The type of the None singleton.

<a id="CallsEqCondition"></a>

`CallsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_talk.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsFuzzyCondition"></a>

`CallsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_talk.types.CallsStringFilter`
    :   The type of the None singleton.

<a id="CallsGtCondition"></a>

`CallsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_talk.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsGteCondition"></a>

`CallsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_talk.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsInCondition"></a>

`CallsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.zendesk_talk.types.CallsInFilter`
    :   The type of the None singleton.

<a id="CallsInFilter"></a>

`CallsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: list[int]`
    :   Agent ID

    `call_charge: list[str]`
    :   Call charge amount

    `call_group_id: list[int]`
    :   Call group ID

    `call_recording_consent: list[str]`
    :   Call recording consent status

    `call_recording_consent_action: list[str]`
    :   Recording consent action

    `call_recording_consent_keypress: list[str]`
    :   Recording consent keypress

    `callback: list[bool]`
    :   Whether this was a callback

    `callback_source: list[str]`
    :   Source of the callback

    `completion_status: list[str]`
    :   Call completion status

    `consultation_time: list[int]`
    :   Consultation time

    `created_at: list[str]`
    :   Creation timestamp

    `customer_requested_voicemail: list[bool]`
    :   Whether customer requested voicemail

    `default_group: list[bool]`
    :   Whether default group was used

    `direction: list[str]`
    :   Call direction (inbound/outbound)

    `duration: list[int]`
    :   Call duration in seconds

    `exceeded_queue_time: list[bool]`
    :   Whether queue time was exceeded

    `exceeded_queue_wait_time: list[bool]`
    :   Whether max queue wait time was exceeded

    `hold_time: list[int]`
    :   Hold time in seconds

    `id: list[int]`
    :   Call ID

    `ivr_action: list[str]`
    :   IVR action taken

    `ivr_destination_group_name: list[str]`
    :   IVR destination group name

    `ivr_hops: list[int]`
    :   Number of IVR hops

    `ivr_routed_to: list[str]`
    :   Where IVR routed the call

    `ivr_time_spent: list[int]`
    :   Time spent in IVR

    `minutes_billed: list[int]`
    :   Minutes billed

    `not_recording_time: list[int]`
    :   Time not recording

    `outside_business_hours: list[bool]`
    :   Whether call was outside business hours

    `overflowed: list[bool]`
    :   Whether call overflowed

    `overflowed_to: list[str]`
    :   Where call overflowed to

    `phone_number: list[str]`
    :   Phone number used

    `phone_number_id: list[int]`
    :   Phone number ID

    `quality_issues: list[list[typing.Any]]`
    :   Quality issues detected

    `recording_control_interactions: list[int]`
    :   Recording control interactions count

    `recording_time: list[int]`
    :   Recording time

    `talk_time: list[int]`
    :   Talk time in seconds

    `ticket_id: list[int]`
    :   Associated ticket ID

    `time_to_answer: list[int]`
    :   Time to answer in seconds

    `updated_at: list[str]`
    :   Last update timestamp

    `voicemail: list[bool]`
    :   Whether it was a voicemail

    `wait_time: list[int]`
    :   Wait time in seconds

    `wrap_up_time: list[int]`
    :   Wrap-up time in seconds

<a id="CallsKeywordCondition"></a>

`CallsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_talk.types.CallsStringFilter`
    :   The type of the None singleton.

<a id="CallsLikeCondition"></a>

`CallsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_talk.types.CallsStringFilter`
    :   The type of the None singleton.

<a id="CallsListParams"></a>

`CallsListParams(*args, **kwargs)`
:   Parameters for calls.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `start_time: int`
    :   The type of the None singleton.

<a id="CallsLtCondition"></a>

`CallsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_talk.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsLteCondition"></a>

`CallsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_talk.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsNeqCondition"></a>

`CallsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_talk.types.CallsSearchFilter`
    :   The type of the None singleton.

<a id="CallsNotCondition"></a>

`CallsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.zendesk_talk.types.CallsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsAnyCondition`
    :   The type of the None singleton.

<a id="CallsOrCondition"></a>

`CallsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_talk.types.CallsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsAnyCondition]`
    :   The type of the None singleton.

<a id="CallsSearchFilter"></a>

`CallsSearchFilter(*args, **kwargs)`
:   Available fields for filtering calls search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CallsSearchQuery"></a>

`CallsSearchQuery(*args, **kwargs)`
:   Search query for calls entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_talk.types.CallsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CallsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_talk.types.CallsSortFilter]`
    :   The type of the None singleton.

<a id="CallsSortFilter"></a>

`CallsSortFilter(*args, **kwargs)`
:   Available fields for sorting calls search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: Literal['asc', 'desc']`
    :   Agent ID

    `call_charge: Literal['asc', 'desc']`
    :   Call charge amount

    `call_group_id: Literal['asc', 'desc']`
    :   Call group ID

    `call_recording_consent: Literal['asc', 'desc']`
    :   Call recording consent status

    `call_recording_consent_action: Literal['asc', 'desc']`
    :   Recording consent action

    `call_recording_consent_keypress: Literal['asc', 'desc']`
    :   Recording consent keypress

    `callback: Literal['asc', 'desc']`
    :   Whether this was a callback

    `callback_source: Literal['asc', 'desc']`
    :   Source of the callback

    `completion_status: Literal['asc', 'desc']`
    :   Call completion status

    `consultation_time: Literal['asc', 'desc']`
    :   Consultation time

    `created_at: Literal['asc', 'desc']`
    :   Creation timestamp

    `customer_requested_voicemail: Literal['asc', 'desc']`
    :   Whether customer requested voicemail

    `default_group: Literal['asc', 'desc']`
    :   Whether default group was used

    `direction: Literal['asc', 'desc']`
    :   Call direction (inbound/outbound)

    `duration: Literal['asc', 'desc']`
    :   Call duration in seconds

    `exceeded_queue_time: Literal['asc', 'desc']`
    :   Whether queue time was exceeded

    `exceeded_queue_wait_time: Literal['asc', 'desc']`
    :   Whether max queue wait time was exceeded

    `hold_time: Literal['asc', 'desc']`
    :   Hold time in seconds

    `id: Literal['asc', 'desc']`
    :   Call ID

    `ivr_action: Literal['asc', 'desc']`
    :   IVR action taken

    `ivr_destination_group_name: Literal['asc', 'desc']`
    :   IVR destination group name

    `ivr_hops: Literal['asc', 'desc']`
    :   Number of IVR hops

    `ivr_routed_to: Literal['asc', 'desc']`
    :   Where IVR routed the call

    `ivr_time_spent: Literal['asc', 'desc']`
    :   Time spent in IVR

    `minutes_billed: Literal['asc', 'desc']`
    :   Minutes billed

    `not_recording_time: Literal['asc', 'desc']`
    :   Time not recording

    `outside_business_hours: Literal['asc', 'desc']`
    :   Whether call was outside business hours

    `overflowed: Literal['asc', 'desc']`
    :   Whether call overflowed

    `overflowed_to: Literal['asc', 'desc']`
    :   Where call overflowed to

    `phone_number: Literal['asc', 'desc']`
    :   Phone number used

    `phone_number_id: Literal['asc', 'desc']`
    :   Phone number ID

    `quality_issues: Literal['asc', 'desc']`
    :   Quality issues detected

    `recording_control_interactions: Literal['asc', 'desc']`
    :   Recording control interactions count

    `recording_time: Literal['asc', 'desc']`
    :   Recording time

    `talk_time: Literal['asc', 'desc']`
    :   Talk time in seconds

    `ticket_id: Literal['asc', 'desc']`
    :   Associated ticket ID

    `time_to_answer: Literal['asc', 'desc']`
    :   Time to answer in seconds

    `updated_at: Literal['asc', 'desc']`
    :   Last update timestamp

    `voicemail: Literal['asc', 'desc']`
    :   Whether it was a voicemail

    `wait_time: Literal['asc', 'desc']`
    :   Wait time in seconds

    `wrap_up_time: Literal['asc', 'desc']`
    :   Wrap-up time in seconds

<a id="CallsStringFilter"></a>

`CallsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: str`
    :   Agent ID

    `call_charge: str`
    :   Call charge amount

    `call_group_id: str`
    :   Call group ID

    `call_recording_consent: str`
    :   Call recording consent status

    `call_recording_consent_action: str`
    :   Recording consent action

    `call_recording_consent_keypress: str`
    :   Recording consent keypress

    `callback: str`
    :   Whether this was a callback

    `callback_source: str`
    :   Source of the callback

    `completion_status: str`
    :   Call completion status

    `consultation_time: str`
    :   Consultation time

    `created_at: str`
    :   Creation timestamp

    `customer_requested_voicemail: str`
    :   Whether customer requested voicemail

    `default_group: str`
    :   Whether default group was used

    `direction: str`
    :   Call direction (inbound/outbound)

    `duration: str`
    :   Call duration in seconds

    `exceeded_queue_time: str`
    :   Whether queue time was exceeded

    `exceeded_queue_wait_time: str`
    :   Whether max queue wait time was exceeded

    `hold_time: str`
    :   Hold time in seconds

    `id: str`
    :   Call ID

    `ivr_action: str`
    :   IVR action taken

    `ivr_destination_group_name: str`
    :   IVR destination group name

    `ivr_hops: str`
    :   Number of IVR hops

    `ivr_routed_to: str`
    :   Where IVR routed the call

    `ivr_time_spent: str`
    :   Time spent in IVR

    `minutes_billed: str`
    :   Minutes billed

    `not_recording_time: str`
    :   Time not recording

    `outside_business_hours: str`
    :   Whether call was outside business hours

    `overflowed: str`
    :   Whether call overflowed

    `overflowed_to: str`
    :   Where call overflowed to

    `phone_number: str`
    :   Phone number used

    `phone_number_id: str`
    :   Phone number ID

    `quality_issues: str`
    :   Quality issues detected

    `recording_control_interactions: str`
    :   Recording control interactions count

    `recording_time: str`
    :   Recording time

    `talk_time: str`
    :   Talk time in seconds

    `ticket_id: str`
    :   Associated ticket ID

    `time_to_answer: str`
    :   Time to answer in seconds

    `updated_at: str`
    :   Last update timestamp

    `voicemail: str`
    :   Whether it was a voicemail

    `wait_time: str`
    :   Wait time in seconds

    `wrap_up_time: str`
    :   Wrap-up time in seconds

<a id="CurrentQueueActivityAndCondition"></a>

`CurrentQueueActivityAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityAnyCondition]`
    :   The type of the None singleton.

<a id="CurrentQueueActivityAnyCondition"></a>

`CurrentQueueActivityAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityAnyValueFilter`
    :   The type of the None singleton.

<a id="CurrentQueueActivityAnyValueFilter"></a>

`CurrentQueueActivityAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agents_online: Any`
    :   Current number of agents online

    `average_wait_time: Any`
    :   Average wait time for callers in queue (seconds)

    `callbacks_waiting: Any`
    :   Number of callers in callback queue

    `calls_waiting: Any`
    :   Number of callers waiting in queue

    `current_timestamp: Any`
    :   Current timestamp

    `embeddable_callbacks_waiting: Any`
    :   Number of Web Widget callback requests waiting

    `longest_wait_time: Any`
    :   Longest wait time for any caller (seconds)

<a id="CurrentQueueActivityContainsCondition"></a>

`CurrentQueueActivityContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityAnyValueFilter`
    :   The type of the None singleton.

<a id="CurrentQueueActivityEqCondition"></a>

`CurrentQueueActivityEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivitySearchFilter`
    :   The type of the None singleton.

<a id="CurrentQueueActivityFuzzyCondition"></a>

`CurrentQueueActivityFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityStringFilter`
    :   The type of the None singleton.

<a id="CurrentQueueActivityGtCondition"></a>

`CurrentQueueActivityGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivitySearchFilter`
    :   The type of the None singleton.

<a id="CurrentQueueActivityGteCondition"></a>

`CurrentQueueActivityGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivitySearchFilter`
    :   The type of the None singleton.

<a id="CurrentQueueActivityInCondition"></a>

`CurrentQueueActivityInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityInFilter`
    :   The type of the None singleton.

<a id="CurrentQueueActivityInFilter"></a>

`CurrentQueueActivityInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agents_online: list[int]`
    :   Current number of agents online

    `average_wait_time: list[int]`
    :   Average wait time for callers in queue (seconds)

    `callbacks_waiting: list[int]`
    :   Number of callers in callback queue

    `calls_waiting: list[int]`
    :   Number of callers waiting in queue

    `current_timestamp: list[int]`
    :   Current timestamp

    `embeddable_callbacks_waiting: list[int]`
    :   Number of Web Widget callback requests waiting

    `longest_wait_time: list[int]`
    :   Longest wait time for any caller (seconds)

<a id="CurrentQueueActivityKeywordCondition"></a>

`CurrentQueueActivityKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityStringFilter`
    :   The type of the None singleton.

<a id="CurrentQueueActivityLikeCondition"></a>

`CurrentQueueActivityLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityStringFilter`
    :   The type of the None singleton.

<a id="CurrentQueueActivityListParams"></a>

`CurrentQueueActivityListParams(*args, **kwargs)`
:   Parameters for current_queue_activity.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="CurrentQueueActivityLtCondition"></a>

`CurrentQueueActivityLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivitySearchFilter`
    :   The type of the None singleton.

<a id="CurrentQueueActivityLteCondition"></a>

`CurrentQueueActivityLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivitySearchFilter`
    :   The type of the None singleton.

<a id="CurrentQueueActivityNeqCondition"></a>

`CurrentQueueActivityNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivitySearchFilter`
    :   The type of the None singleton.

<a id="CurrentQueueActivityNotCondition"></a>

`CurrentQueueActivityNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityAnyCondition`
    :   The type of the None singleton.

<a id="CurrentQueueActivityOrCondition"></a>

`CurrentQueueActivityOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityAnyCondition]`
    :   The type of the None singleton.

<a id="CurrentQueueActivitySearchFilter"></a>

`CurrentQueueActivitySearchFilter(*args, **kwargs)`
:   Available fields for filtering current_queue_activity search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CurrentQueueActivitySearchQuery"></a>

`CurrentQueueActivitySearchQuery(*args, **kwargs)`
:   Search query for current_queue_activity entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivityAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_talk.types.CurrentQueueActivitySortFilter]`
    :   The type of the None singleton.

<a id="CurrentQueueActivitySortFilter"></a>

`CurrentQueueActivitySortFilter(*args, **kwargs)`
:   Available fields for sorting current_queue_activity search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agents_online: Literal['asc', 'desc']`
    :   Current number of agents online

    `average_wait_time: Literal['asc', 'desc']`
    :   Average wait time for callers in queue (seconds)

    `callbacks_waiting: Literal['asc', 'desc']`
    :   Number of callers in callback queue

    `calls_waiting: Literal['asc', 'desc']`
    :   Number of callers waiting in queue

    `current_timestamp: Literal['asc', 'desc']`
    :   Current timestamp

    `embeddable_callbacks_waiting: Literal['asc', 'desc']`
    :   Number of Web Widget callback requests waiting

    `longest_wait_time: Literal['asc', 'desc']`
    :   Longest wait time for any caller (seconds)

<a id="CurrentQueueActivityStringFilter"></a>

`CurrentQueueActivityStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agents_online: str`
    :   Current number of agents online

    `average_wait_time: str`
    :   Average wait time for callers in queue (seconds)

    `callbacks_waiting: str`
    :   Number of callers in callback queue

    `calls_waiting: str`
    :   Number of callers waiting in queue

    `current_timestamp: str`
    :   Current timestamp

    `embeddable_callbacks_waiting: str`
    :   Number of Web Widget callback requests waiting

    `longest_wait_time: str`
    :   Longest wait time for any caller (seconds)

<a id="GreetingCategoriesAndCondition"></a>

`GreetingCategoriesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesAnyCondition]`
    :   The type of the None singleton.

<a id="GreetingCategoriesAnyCondition"></a>

`GreetingCategoriesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="GreetingCategoriesAnyValueFilter"></a>

`GreetingCategoriesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Greeting category ID

    `name: Any`
    :   Name of the greeting category

<a id="GreetingCategoriesContainsCondition"></a>

`GreetingCategoriesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="GreetingCategoriesEqCondition"></a>

`GreetingCategoriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="GreetingCategoriesFuzzyCondition"></a>

`GreetingCategoriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesStringFilter`
    :   The type of the None singleton.

<a id="GreetingCategoriesGetParams"></a>

`GreetingCategoriesGetParams(*args, **kwargs)`
:   Parameters for greeting_categories.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `greeting_category_id: str`
    :   The type of the None singleton.

<a id="GreetingCategoriesGtCondition"></a>

`GreetingCategoriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="GreetingCategoriesGteCondition"></a>

`GreetingCategoriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="GreetingCategoriesInCondition"></a>

`GreetingCategoriesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesInFilter`
    :   The type of the None singleton.

<a id="GreetingCategoriesInFilter"></a>

`GreetingCategoriesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[int]`
    :   Greeting category ID

    `name: list[str]`
    :   Name of the greeting category

<a id="GreetingCategoriesKeywordCondition"></a>

`GreetingCategoriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesStringFilter`
    :   The type of the None singleton.

<a id="GreetingCategoriesLikeCondition"></a>

`GreetingCategoriesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesStringFilter`
    :   The type of the None singleton.

<a id="GreetingCategoriesListParams"></a>

`GreetingCategoriesListParams(*args, **kwargs)`
:   Parameters for greeting_categories.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="GreetingCategoriesLtCondition"></a>

`GreetingCategoriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="GreetingCategoriesLteCondition"></a>

`GreetingCategoriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="GreetingCategoriesNeqCondition"></a>

`GreetingCategoriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="GreetingCategoriesNotCondition"></a>

`GreetingCategoriesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesAnyCondition`
    :   The type of the None singleton.

<a id="GreetingCategoriesOrCondition"></a>

`GreetingCategoriesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesAnyCondition]`
    :   The type of the None singleton.

<a id="GreetingCategoriesSearchFilter"></a>

`GreetingCategoriesSearchFilter(*args, **kwargs)`
:   Available fields for filtering greeting_categories search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: int | None`
    :   Greeting category ID

    `name: str | None`
    :   Name of the greeting category

<a id="GreetingCategoriesSearchQuery"></a>

`GreetingCategoriesSearchQuery(*args, **kwargs)`
:   Search query for greeting_categories entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingCategoriesSortFilter]`
    :   The type of the None singleton.

<a id="GreetingCategoriesSortFilter"></a>

`GreetingCategoriesSortFilter(*args, **kwargs)`
:   Available fields for sorting greeting_categories search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Greeting category ID

    `name: Literal['asc', 'desc']`
    :   Name of the greeting category

<a id="GreetingCategoriesStringFilter"></a>

`GreetingCategoriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Greeting category ID

    `name: str`
    :   Name of the greeting category

<a id="GreetingsAndCondition"></a>

`GreetingsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsAnyCondition]`
    :   The type of the None singleton.

<a id="GreetingsAnyCondition"></a>

`GreetingsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsAnyValueFilter`
    :   The type of the None singleton.

<a id="GreetingsAnyValueFilter"></a>

`GreetingsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Any`
    :   Whether the greeting is associated with phone numbers

    `audio_name: Any`
    :   Audio file name

    `audio_url: Any`
    :   Path to the greeting sound file

    `category_id: Any`
    :   ID of the greeting category

    `default: Any`
    :   Whether this is a system default greeting

    `default_lang: Any`
    :   Whether the greeting has a default language

    `has_sub_settings: Any`
    :   Sub-settings for categorized greetings

    `id: Any`
    :   Greeting ID

    `ivr_ids: Any`
    :   IDs of IVRs associated with the greeting

    `name: Any`
    :   Name of the greeting

    `pending: Any`
    :   Whether the greeting is pending

    `phone_number_ids: Any`
    :   IDs of phone numbers associated with the greeting

    `upload_id: Any`
    :   Upload ID associated with the greeting

<a id="GreetingsContainsCondition"></a>

`GreetingsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsAnyValueFilter`
    :   The type of the None singleton.

<a id="GreetingsEqCondition"></a>

`GreetingsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsSearchFilter`
    :   The type of the None singleton.

<a id="GreetingsFuzzyCondition"></a>

`GreetingsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsStringFilter`
    :   The type of the None singleton.

<a id="GreetingsGetParams"></a>

`GreetingsGetParams(*args, **kwargs)`
:   Parameters for greetings.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `greeting_id: str`
    :   The type of the None singleton.

<a id="GreetingsGtCondition"></a>

`GreetingsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsSearchFilter`
    :   The type of the None singleton.

<a id="GreetingsGteCondition"></a>

`GreetingsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsSearchFilter`
    :   The type of the None singleton.

<a id="GreetingsInCondition"></a>

`GreetingsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsInFilter`
    :   The type of the None singleton.

<a id="GreetingsInFilter"></a>

`GreetingsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: list[bool]`
    :   Whether the greeting is associated with phone numbers

    `audio_name: list[str]`
    :   Audio file name

    `audio_url: list[str]`
    :   Path to the greeting sound file

    `category_id: list[int]`
    :   ID of the greeting category

    `default: list[bool]`
    :   Whether this is a system default greeting

    `default_lang: list[bool]`
    :   Whether the greeting has a default language

    `has_sub_settings: list[bool]`
    :   Sub-settings for categorized greetings

    `id: list[str]`
    :   Greeting ID

    `ivr_ids: list[list[typing.Any]]`
    :   IDs of IVRs associated with the greeting

    `name: list[str]`
    :   Name of the greeting

    `pending: list[bool]`
    :   Whether the greeting is pending

    `phone_number_ids: list[list[typing.Any]]`
    :   IDs of phone numbers associated with the greeting

    `upload_id: list[int]`
    :   Upload ID associated with the greeting

<a id="GreetingsKeywordCondition"></a>

`GreetingsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsStringFilter`
    :   The type of the None singleton.

<a id="GreetingsLikeCondition"></a>

`GreetingsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsStringFilter`
    :   The type of the None singleton.

<a id="GreetingsListParams"></a>

`GreetingsListParams(*args, **kwargs)`
:   Parameters for greetings.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="GreetingsLtCondition"></a>

`GreetingsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsSearchFilter`
    :   The type of the None singleton.

<a id="GreetingsLteCondition"></a>

`GreetingsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsSearchFilter`
    :   The type of the None singleton.

<a id="GreetingsNeqCondition"></a>

`GreetingsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsSearchFilter`
    :   The type of the None singleton.

<a id="GreetingsNotCondition"></a>

`GreetingsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsAnyCondition`
    :   The type of the None singleton.

<a id="GreetingsOrCondition"></a>

`GreetingsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsAnyCondition]`
    :   The type of the None singleton.

<a id="GreetingsSearchFilter"></a>

`GreetingsSearchFilter(*args, **kwargs)`
:   Available fields for filtering greetings search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

    `name: str | None`
    :   Name of the greeting

    `pending: bool | None`
    :   Whether the greeting is pending

    `phone_number_ids: list[typing.Any] | None`
    :   IDs of phone numbers associated with the greeting

    `upload_id: int | None`
    :   Upload ID associated with the greeting

<a id="GreetingsSearchQuery"></a>

`GreetingsSearchQuery(*args, **kwargs)`
:   Search query for greetings entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_talk.types.GreetingsSortFilter]`
    :   The type of the None singleton.

<a id="GreetingsSortFilter"></a>

`GreetingsSortFilter(*args, **kwargs)`
:   Available fields for sorting greetings search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Literal['asc', 'desc']`
    :   Whether the greeting is associated with phone numbers

    `audio_name: Literal['asc', 'desc']`
    :   Audio file name

    `audio_url: Literal['asc', 'desc']`
    :   Path to the greeting sound file

    `category_id: Literal['asc', 'desc']`
    :   ID of the greeting category

    `default: Literal['asc', 'desc']`
    :   Whether this is a system default greeting

    `default_lang: Literal['asc', 'desc']`
    :   Whether the greeting has a default language

    `has_sub_settings: Literal['asc', 'desc']`
    :   Sub-settings for categorized greetings

    `id: Literal['asc', 'desc']`
    :   Greeting ID

    `ivr_ids: Literal['asc', 'desc']`
    :   IDs of IVRs associated with the greeting

    `name: Literal['asc', 'desc']`
    :   Name of the greeting

    `pending: Literal['asc', 'desc']`
    :   Whether the greeting is pending

    `phone_number_ids: Literal['asc', 'desc']`
    :   IDs of phone numbers associated with the greeting

    `upload_id: Literal['asc', 'desc']`
    :   Upload ID associated with the greeting

<a id="GreetingsStringFilter"></a>

`GreetingsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: str`
    :   Whether the greeting is associated with phone numbers

    `audio_name: str`
    :   Audio file name

    `audio_url: str`
    :   Path to the greeting sound file

    `category_id: str`
    :   ID of the greeting category

    `default: str`
    :   Whether this is a system default greeting

    `default_lang: str`
    :   Whether the greeting has a default language

    `has_sub_settings: str`
    :   Sub-settings for categorized greetings

    `id: str`
    :   Greeting ID

    `ivr_ids: str`
    :   IDs of IVRs associated with the greeting

    `name: str`
    :   Name of the greeting

    `pending: str`
    :   Whether the greeting is pending

    `phone_number_ids: str`
    :   IDs of phone numbers associated with the greeting

    `upload_id: str`
    :   Upload ID associated with the greeting

<a id="IvrsAndCondition"></a>

`IvrsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsAnyCondition]`
    :   The type of the None singleton.

<a id="IvrsAnyCondition"></a>

`IvrsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsAnyValueFilter`
    :   The type of the None singleton.

<a id="IvrsAnyValueFilter"></a>

`IvrsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   IVR ID

    `menus: Any`
    :   List of IVR menus

    `name: Any`
    :   Name of the IVR

    `phone_number_ids: Any`
    :   IDs of phone numbers configured with this IVR

    `phone_number_names: Any`
    :   Names of phone numbers configured with this IVR

<a id="IvrsContainsCondition"></a>

`IvrsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsAnyValueFilter`
    :   The type of the None singleton.

<a id="IvrsEqCondition"></a>

`IvrsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsSearchFilter`
    :   The type of the None singleton.

<a id="IvrsFuzzyCondition"></a>

`IvrsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsStringFilter`
    :   The type of the None singleton.

<a id="IvrsGetParams"></a>

`IvrsGetParams(*args, **kwargs)`
:   Parameters for ivrs.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ivr_id: str`
    :   The type of the None singleton.

<a id="IvrsGtCondition"></a>

`IvrsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsSearchFilter`
    :   The type of the None singleton.

<a id="IvrsGteCondition"></a>

`IvrsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsSearchFilter`
    :   The type of the None singleton.

<a id="IvrsInCondition"></a>

`IvrsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsInFilter`
    :   The type of the None singleton.

<a id="IvrsInFilter"></a>

`IvrsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[int]`
    :   IVR ID

    `menus: list[list[typing.Any]]`
    :   List of IVR menus

    `name: list[str]`
    :   Name of the IVR

    `phone_number_ids: list[list[typing.Any]]`
    :   IDs of phone numbers configured with this IVR

    `phone_number_names: list[list[typing.Any]]`
    :   Names of phone numbers configured with this IVR

<a id="IvrsKeywordCondition"></a>

`IvrsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsStringFilter`
    :   The type of the None singleton.

<a id="IvrsLikeCondition"></a>

`IvrsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsStringFilter`
    :   The type of the None singleton.

<a id="IvrsListParams"></a>

`IvrsListParams(*args, **kwargs)`
:   Parameters for ivrs.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="IvrsLtCondition"></a>

`IvrsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsSearchFilter`
    :   The type of the None singleton.

<a id="IvrsLteCondition"></a>

`IvrsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsSearchFilter`
    :   The type of the None singleton.

<a id="IvrsNeqCondition"></a>

`IvrsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsSearchFilter`
    :   The type of the None singleton.

<a id="IvrsNotCondition"></a>

`IvrsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsAnyCondition`
    :   The type of the None singleton.

<a id="IvrsOrCondition"></a>

`IvrsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsAnyCondition]`
    :   The type of the None singleton.

<a id="IvrsSearchFilter"></a>

`IvrsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ivrs search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: int | None`
    :   IVR ID

    `menus: list[typing.Any] | None`
    :   List of IVR menus

    `name: str | None`
    :   Name of the IVR

    `phone_number_ids: list[typing.Any] | None`
    :   IDs of phone numbers configured with this IVR

    `phone_number_names: list[typing.Any] | None`
    :   Names of phone numbers configured with this IVR

<a id="IvrsSearchQuery"></a>

`IvrsSearchQuery(*args, **kwargs)`
:   Search query for ivrs entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_talk.types.IvrsSortFilter]`
    :   The type of the None singleton.

<a id="IvrsSortFilter"></a>

`IvrsSortFilter(*args, **kwargs)`
:   Available fields for sorting ivrs search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   IVR ID

    `menus: Literal['asc', 'desc']`
    :   List of IVR menus

    `name: Literal['asc', 'desc']`
    :   Name of the IVR

    `phone_number_ids: Literal['asc', 'desc']`
    :   IDs of phone numbers configured with this IVR

    `phone_number_names: Literal['asc', 'desc']`
    :   Names of phone numbers configured with this IVR

<a id="IvrsStringFilter"></a>

`IvrsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   IVR ID

    `menus: str`
    :   List of IVR menus

    `name: str`
    :   Name of the IVR

    `phone_number_ids: str`
    :   IDs of phone numbers configured with this IVR

    `phone_number_names: str`
    :   Names of phone numbers configured with this IVR

<a id="PhoneNumbersAndCondition"></a>

`PhoneNumbersAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersAnyCondition]`
    :   The type of the None singleton.

<a id="PhoneNumbersAnyCondition"></a>

`PhoneNumbersAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersAnyValueFilter`
    :   The type of the None singleton.

<a id="PhoneNumbersAnyValueFilter"></a>

`PhoneNumbersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `call_recording_consent: Any`
    :   What call recording consent is set to

    `capabilities: Any`
    :   Phone number capabilities (sms, mms, voice)

    `categorised_greetings: Any`
    :   Greeting category IDs and names

    `categorised_greetings_with_sub_settings: Any`
    :   Greeting categories with associated settings

    `country_code: Any`
    :   ISO country code for the number

    `created_at: Any`
    :   Date and time the phone number was created

    `default_greeting_ids: Any`
    :   Names of default system greetings

    `default_group_id: Any`
    :   Default group ID

    `display_number: Any`
    :   Formatted phone number

    `external: Any`
    :   Whether this is an external caller ID number

    `failover_number: Any`
    :   Failover number associated with the phone number

    `greeting_ids: Any`
    :   Custom greeting IDs associated with the phone number

    `group_ids: Any`
    :   Array of associated group IDs

    `id: Any`
    :   Unique phone number identifier

    `ivr_id: Any`
    :   ID of IVR associated with the phone number

    `line_type: Any`
    :   Type of line (phone or digital)

    `location: Any`
    :   Geographical location of the number

    `name: Any`
    :   Nickname if set, otherwise the display number

    `nickname: Any`
    :   Nickname of the phone number

    `number: Any`
    :   Phone number digits

    `outbound_enabled: Any`
    :   Whether outbound calls are enabled

    `priority: Any`
    :   Priority level of the phone number

    `recorded: Any`
    :   Whether calls are recorded

    `schedule_id: Any`
    :   ID of schedule associated with the phone number

    `sms_enabled: Any`
    :   Whether SMS is enabled

    `sms_group_id: Any`
    :   Group associated with SMS

    `token: Any`
    :   Generated token unique for the phone number

    `toll_free: Any`
    :   Whether the number is toll-free

    `transcription: Any`
    :   Whether voicemail transcription is enabled

    `voice_enabled: Any`
    :   Whether voice is enabled

<a id="PhoneNumbersContainsCondition"></a>

`PhoneNumbersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersAnyValueFilter`
    :   The type of the None singleton.

<a id="PhoneNumbersEqCondition"></a>

`PhoneNumbersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersSearchFilter`
    :   The type of the None singleton.

<a id="PhoneNumbersFuzzyCondition"></a>

`PhoneNumbersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersStringFilter`
    :   The type of the None singleton.

<a id="PhoneNumbersGetParams"></a>

`PhoneNumbersGetParams(*args, **kwargs)`
:   Parameters for phone_numbers.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `phone_number_id: str`
    :   The type of the None singleton.

<a id="PhoneNumbersGtCondition"></a>

`PhoneNumbersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersSearchFilter`
    :   The type of the None singleton.

<a id="PhoneNumbersGteCondition"></a>

`PhoneNumbersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersSearchFilter`
    :   The type of the None singleton.

<a id="PhoneNumbersInCondition"></a>

`PhoneNumbersInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersInFilter`
    :   The type of the None singleton.

<a id="PhoneNumbersInFilter"></a>

`PhoneNumbersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `call_recording_consent: list[str]`
    :   What call recording consent is set to

    `capabilities: list[dict[str, typing.Any]]`
    :   Phone number capabilities (sms, mms, voice)

    `categorised_greetings: list[dict[str, typing.Any]]`
    :   Greeting category IDs and names

    `categorised_greetings_with_sub_settings: list[dict[str, typing.Any]]`
    :   Greeting categories with associated settings

    `country_code: list[str]`
    :   ISO country code for the number

    `created_at: list[str]`
    :   Date and time the phone number was created

    `default_greeting_ids: list[list[typing.Any]]`
    :   Names of default system greetings

    `default_group_id: list[int]`
    :   Default group ID

    `display_number: list[str]`
    :   Formatted phone number

    `external: list[bool]`
    :   Whether this is an external caller ID number

    `failover_number: list[str]`
    :   Failover number associated with the phone number

    `greeting_ids: list[list[typing.Any]]`
    :   Custom greeting IDs associated with the phone number

    `group_ids: list[list[typing.Any]]`
    :   Array of associated group IDs

    `id: list[int]`
    :   Unique phone number identifier

    `ivr_id: list[int]`
    :   ID of IVR associated with the phone number

    `line_type: list[str]`
    :   Type of line (phone or digital)

    `location: list[str]`
    :   Geographical location of the number

    `name: list[str]`
    :   Nickname if set, otherwise the display number

    `nickname: list[str]`
    :   Nickname of the phone number

    `number: list[str]`
    :   Phone number digits

    `outbound_enabled: list[bool]`
    :   Whether outbound calls are enabled

    `priority: list[int]`
    :   Priority level of the phone number

    `recorded: list[bool]`
    :   Whether calls are recorded

    `schedule_id: list[int]`
    :   ID of schedule associated with the phone number

    `sms_enabled: list[bool]`
    :   Whether SMS is enabled

    `sms_group_id: list[int]`
    :   Group associated with SMS

    `token: list[str]`
    :   Generated token unique for the phone number

    `toll_free: list[bool]`
    :   Whether the number is toll-free

    `transcription: list[bool]`
    :   Whether voicemail transcription is enabled

    `voice_enabled: list[bool]`
    :   Whether voice is enabled

<a id="PhoneNumbersKeywordCondition"></a>

`PhoneNumbersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersStringFilter`
    :   The type of the None singleton.

<a id="PhoneNumbersLikeCondition"></a>

`PhoneNumbersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersStringFilter`
    :   The type of the None singleton.

<a id="PhoneNumbersListParams"></a>

`PhoneNumbersListParams(*args, **kwargs)`
:   Parameters for phone_numbers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="PhoneNumbersLtCondition"></a>

`PhoneNumbersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersSearchFilter`
    :   The type of the None singleton.

<a id="PhoneNumbersLteCondition"></a>

`PhoneNumbersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersSearchFilter`
    :   The type of the None singleton.

<a id="PhoneNumbersNeqCondition"></a>

`PhoneNumbersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersSearchFilter`
    :   The type of the None singleton.

<a id="PhoneNumbersNotCondition"></a>

`PhoneNumbersNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersAnyCondition`
    :   The type of the None singleton.

<a id="PhoneNumbersOrCondition"></a>

`PhoneNumbersOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersAnyCondition]`
    :   The type of the None singleton.

<a id="PhoneNumbersSearchFilter"></a>

`PhoneNumbersSearchFilter(*args, **kwargs)`
:   Available fields for filtering phone_numbers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="PhoneNumbersSearchQuery"></a>

`PhoneNumbersSearchQuery(*args, **kwargs)`
:   Search query for phone_numbers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersEqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersNeqCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersGtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersGteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersLtCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersLteCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersInCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersLikeCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersContainsCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersNotCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersAndCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersOrCondition | airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_talk.types.PhoneNumbersSortFilter]`
    :   The type of the None singleton.

<a id="PhoneNumbersSortFilter"></a>

`PhoneNumbersSortFilter(*args, **kwargs)`
:   Available fields for sorting phone_numbers search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `call_recording_consent: Literal['asc', 'desc']`
    :   What call recording consent is set to

    `capabilities: Literal['asc', 'desc']`
    :   Phone number capabilities (sms, mms, voice)

    `categorised_greetings: Literal['asc', 'desc']`
    :   Greeting category IDs and names

    `categorised_greetings_with_sub_settings: Literal['asc', 'desc']`
    :   Greeting categories with associated settings

    `country_code: Literal['asc', 'desc']`
    :   ISO country code for the number

    `created_at: Literal['asc', 'desc']`
    :   Date and time the phone number was created

    `default_greeting_ids: Literal['asc', 'desc']`
    :   Names of default system greetings

    `default_group_id: Literal['asc', 'desc']`
    :   Default group ID

    `display_number: Literal['asc', 'desc']`
    :   Formatted phone number

    `external: Literal['asc', 'desc']`
    :   Whether this is an external caller ID number

    `failover_number: Literal['asc', 'desc']`
    :   Failover number associated with the phone number

    `greeting_ids: Literal['asc', 'desc']`
    :   Custom greeting IDs associated with the phone number

    `group_ids: Literal['asc', 'desc']`
    :   Array of associated group IDs

    `id: Literal['asc', 'desc']`
    :   Unique phone number identifier

    `ivr_id: Literal['asc', 'desc']`
    :   ID of IVR associated with the phone number

    `line_type: Literal['asc', 'desc']`
    :   Type of line (phone or digital)

    `location: Literal['asc', 'desc']`
    :   Geographical location of the number

    `name: Literal['asc', 'desc']`
    :   Nickname if set, otherwise the display number

    `nickname: Literal['asc', 'desc']`
    :   Nickname of the phone number

    `number: Literal['asc', 'desc']`
    :   Phone number digits

    `outbound_enabled: Literal['asc', 'desc']`
    :   Whether outbound calls are enabled

    `priority: Literal['asc', 'desc']`
    :   Priority level of the phone number

    `recorded: Literal['asc', 'desc']`
    :   Whether calls are recorded

    `schedule_id: Literal['asc', 'desc']`
    :   ID of schedule associated with the phone number

    `sms_enabled: Literal['asc', 'desc']`
    :   Whether SMS is enabled

    `sms_group_id: Literal['asc', 'desc']`
    :   Group associated with SMS

    `token: Literal['asc', 'desc']`
    :   Generated token unique for the phone number

    `toll_free: Literal['asc', 'desc']`
    :   Whether the number is toll-free

    `transcription: Literal['asc', 'desc']`
    :   Whether voicemail transcription is enabled

    `voice_enabled: Literal['asc', 'desc']`
    :   Whether voice is enabled

<a id="PhoneNumbersStringFilter"></a>

`PhoneNumbersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `call_recording_consent: str`
    :   What call recording consent is set to

    `capabilities: str`
    :   Phone number capabilities (sms, mms, voice)

    `categorised_greetings: str`
    :   Greeting category IDs and names

    `categorised_greetings_with_sub_settings: str`
    :   Greeting categories with associated settings

    `country_code: str`
    :   ISO country code for the number

    `created_at: str`
    :   Date and time the phone number was created

    `default_greeting_ids: str`
    :   Names of default system greetings

    `default_group_id: str`
    :   Default group ID

    `display_number: str`
    :   Formatted phone number

    `external: str`
    :   Whether this is an external caller ID number

    `failover_number: str`
    :   Failover number associated with the phone number

    `greeting_ids: str`
    :   Custom greeting IDs associated with the phone number

    `group_ids: str`
    :   Array of associated group IDs

    `id: str`
    :   Unique phone number identifier

    `ivr_id: str`
    :   ID of IVR associated with the phone number

    `line_type: str`
    :   Type of line (phone or digital)

    `location: str`
    :   Geographical location of the number

    `name: str`
    :   Nickname if set, otherwise the display number

    `nickname: str`
    :   Nickname of the phone number

    `number: str`
    :   Phone number digits

    `outbound_enabled: str`
    :   Whether outbound calls are enabled

    `priority: str`
    :   Priority level of the phone number

    `recorded: str`
    :   Whether calls are recorded

    `schedule_id: str`
    :   ID of schedule associated with the phone number

    `sms_enabled: str`
    :   Whether SMS is enabled

    `sms_group_id: str`
    :   Group associated with SMS

    `token: str`
    :   Generated token unique for the phone number

    `toll_free: str`
    :   Whether the number is toll-free

    `transcription: str`
    :   Whether voicemail transcription is enabled

    `voice_enabled: str`
    :   Whether voice is enabled