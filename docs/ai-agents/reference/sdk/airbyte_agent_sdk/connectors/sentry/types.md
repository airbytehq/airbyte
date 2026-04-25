---
id: airbyte_agent_sdk-connectors-sentry-types
title: airbyte_agent_sdk.connectors.sentry.types
---

Module airbyte_agent_sdk.connectors.sentry.types
================================================
Type definitions for sentry connector.

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

<a id="EventsAndCondition"></a>

`EventsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sentry.types.EventsEqCondition | airbyte_agent_sdk.connectors.sentry.types.EventsNeqCondition | airbyte_agent_sdk.connectors.sentry.types.EventsGtCondition | airbyte_agent_sdk.connectors.sentry.types.EventsGteCondition | airbyte_agent_sdk.connectors.sentry.types.EventsLtCondition | airbyte_agent_sdk.connectors.sentry.types.EventsLteCondition | airbyte_agent_sdk.connectors.sentry.types.EventsInCondition | airbyte_agent_sdk.connectors.sentry.types.EventsLikeCondition | airbyte_agent_sdk.connectors.sentry.types.EventsFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.EventsKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.EventsContainsCondition | airbyte_agent_sdk.connectors.sentry.types.EventsNotCondition | airbyte_agent_sdk.connectors.sentry.types.EventsAndCondition | airbyte_agent_sdk.connectors.sentry.types.EventsOrCondition | airbyte_agent_sdk.connectors.sentry.types.EventsAnyCondition]`
    :   The type of the None singleton.

<a id="EventsAnyCondition"></a>

`EventsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sentry.types.EventsAnyValueFilter`
    :   The type of the None singleton.

<a id="EventsAnyValueFilter"></a>

`EventsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `context: Any`
    :   Additional context data.

    `contexts: Any`
    :   Structured context information.

    `crash_file: Any`
    :   Crash file reference.

    `culprit: Any`
    :   The culprit (source) of the event.

    `date_created: Any`
    :   When the event was created.

    `date_received: Any`
    :   When the event was received by Sentry.

    `dist: Any`
    :   Distribution information.

    `entries: Any`
    :   Event entries (exception, breadcrumbs, request, etc.).

    `errors: Any`
    :   Processing errors.

    `event_id: Any`
    :   Event ID as reported by the client.

    `event_type: Any`
    :   The type of the event.

    `fingerprints: Any`
    :   Fingerprints used for grouping.

    `group_id: Any`
    :   ID of the issue group this event belongs to.

    `grouping_config: Any`
    :   Grouping configuration.

    `id: Any`
    :   Unique event identifier.

    `location: Any`
    :   Location in source code.

    `message: Any`
    :   Event message.

    `meta: Any`
    :   Meta information for data scrubbing.

    `metadata: Any`
    :   Event metadata.

    `occurrence: Any`
    :   Occurrence information for the event.

    `packages: Any`
    :   Package information.

    `platform: Any`
    :   Platform the event was generated on.

    `project_id: Any`
    :   Project ID this event belongs to.

    `sdk: Any`
    :   SDK information.

    `size: Any`
    :   Event payload size in bytes.

    `tags: Any`
    :   Tags associated with the event.

    `title: Any`
    :   Event title.

    `type_: Any`
    :   Event type.

    `user: Any`
    :   User associated with the event.

<a id="EventsContainsCondition"></a>

`EventsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sentry.types.EventsAnyValueFilter`
    :   The type of the None singleton.

<a id="EventsEqCondition"></a>

`EventsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sentry.types.EventsSearchFilter`
    :   The type of the None singleton.

<a id="EventsFuzzyCondition"></a>

`EventsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sentry.types.EventsStringFilter`
    :   The type of the None singleton.

<a id="EventsGetParams"></a>

`EventsGetParams(*args, **kwargs)`
:   Parameters for events.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `event_id: str`
    :   The type of the None singleton.

    `organization_slug: str`
    :   The type of the None singleton.

    `project_slug: str`
    :   The type of the None singleton.

<a id="EventsGtCondition"></a>

`EventsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sentry.types.EventsSearchFilter`
    :   The type of the None singleton.

<a id="EventsGteCondition"></a>

`EventsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sentry.types.EventsSearchFilter`
    :   The type of the None singleton.

<a id="EventsInCondition"></a>

`EventsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sentry.types.EventsInFilter`
    :   The type of the None singleton.

<a id="EventsInFilter"></a>

`EventsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `context: list[dict[str, typing.Any]]`
    :   Additional context data.

    `contexts: list[dict[str, typing.Any]]`
    :   Structured context information.

    `crash_file: list[str]`
    :   Crash file reference.

    `culprit: list[str]`
    :   The culprit (source) of the event.

    `date_created: list[str]`
    :   When the event was created.

    `date_received: list[str]`
    :   When the event was received by Sentry.

    `dist: list[str]`
    :   Distribution information.

    `entries: list[list[typing.Any]]`
    :   Event entries (exception, breadcrumbs, request, etc.).

    `errors: list[list[typing.Any]]`
    :   Processing errors.

    `event_id: list[str]`
    :   Event ID as reported by the client.

    `event_type: list[str]`
    :   The type of the event.

    `fingerprints: list[list[typing.Any]]`
    :   Fingerprints used for grouping.

    `group_id: list[str]`
    :   ID of the issue group this event belongs to.

    `grouping_config: list[dict[str, typing.Any]]`
    :   Grouping configuration.

    `id: list[str]`
    :   Unique event identifier.

    `location: list[str]`
    :   Location in source code.

    `message: list[str]`
    :   Event message.

    `meta: list[dict[str, typing.Any]]`
    :   Meta information for data scrubbing.

    `metadata: list[dict[str, typing.Any]]`
    :   Event metadata.

    `occurrence: list[str]`
    :   Occurrence information for the event.

    `packages: list[dict[str, typing.Any]]`
    :   Package information.

    `platform: list[str]`
    :   Platform the event was generated on.

    `project_id: list[str]`
    :   Project ID this event belongs to.

    `sdk: list[str]`
    :   SDK information.

    `size: list[int]`
    :   Event payload size in bytes.

    `tags: list[list[typing.Any]]`
    :   Tags associated with the event.

    `title: list[str]`
    :   Event title.

    `type_: list[str]`
    :   Event type.

    `user: list[dict[str, typing.Any]]`
    :   User associated with the event.

<a id="EventsKeywordCondition"></a>

`EventsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sentry.types.EventsStringFilter`
    :   The type of the None singleton.

<a id="EventsLikeCondition"></a>

`EventsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sentry.types.EventsStringFilter`
    :   The type of the None singleton.

<a id="EventsListParams"></a>

`EventsListParams(*args, **kwargs)`
:   Parameters for events.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `full: str`
    :   The type of the None singleton.

    `organization_slug: str`
    :   The type of the None singleton.

    `project_slug: str`
    :   The type of the None singleton.

<a id="EventsLtCondition"></a>

`EventsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sentry.types.EventsSearchFilter`
    :   The type of the None singleton.

<a id="EventsLteCondition"></a>

`EventsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sentry.types.EventsSearchFilter`
    :   The type of the None singleton.

<a id="EventsNeqCondition"></a>

`EventsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sentry.types.EventsSearchFilter`
    :   The type of the None singleton.

<a id="EventsNotCondition"></a>

`EventsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sentry.types.EventsEqCondition | airbyte_agent_sdk.connectors.sentry.types.EventsNeqCondition | airbyte_agent_sdk.connectors.sentry.types.EventsGtCondition | airbyte_agent_sdk.connectors.sentry.types.EventsGteCondition | airbyte_agent_sdk.connectors.sentry.types.EventsLtCondition | airbyte_agent_sdk.connectors.sentry.types.EventsLteCondition | airbyte_agent_sdk.connectors.sentry.types.EventsInCondition | airbyte_agent_sdk.connectors.sentry.types.EventsLikeCondition | airbyte_agent_sdk.connectors.sentry.types.EventsFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.EventsKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.EventsContainsCondition | airbyte_agent_sdk.connectors.sentry.types.EventsNotCondition | airbyte_agent_sdk.connectors.sentry.types.EventsAndCondition | airbyte_agent_sdk.connectors.sentry.types.EventsOrCondition | airbyte_agent_sdk.connectors.sentry.types.EventsAnyCondition`
    :   The type of the None singleton.

<a id="EventsOrCondition"></a>

`EventsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sentry.types.EventsEqCondition | airbyte_agent_sdk.connectors.sentry.types.EventsNeqCondition | airbyte_agent_sdk.connectors.sentry.types.EventsGtCondition | airbyte_agent_sdk.connectors.sentry.types.EventsGteCondition | airbyte_agent_sdk.connectors.sentry.types.EventsLtCondition | airbyte_agent_sdk.connectors.sentry.types.EventsLteCondition | airbyte_agent_sdk.connectors.sentry.types.EventsInCondition | airbyte_agent_sdk.connectors.sentry.types.EventsLikeCondition | airbyte_agent_sdk.connectors.sentry.types.EventsFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.EventsKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.EventsContainsCondition | airbyte_agent_sdk.connectors.sentry.types.EventsNotCondition | airbyte_agent_sdk.connectors.sentry.types.EventsAndCondition | airbyte_agent_sdk.connectors.sentry.types.EventsOrCondition | airbyte_agent_sdk.connectors.sentry.types.EventsAnyCondition]`
    :   The type of the None singleton.

<a id="EventsSearchFilter"></a>

`EventsSearchFilter(*args, **kwargs)`
:   Available fields for filtering events search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `context: dict[str, typing.Any] | None`
    :   Additional context data.

    `contexts: dict[str, typing.Any] | None`
    :   Structured context information.

    `crash_file: str | None`
    :   Crash file reference.

    `culprit: str | None`
    :   The culprit (source) of the event.

    `date_created: str | None`
    :   When the event was created.

    `date_received: str | None`
    :   When the event was received by Sentry.

    `dist: str | None`
    :   Distribution information.

    `entries: list[typing.Any] | None`
    :   Event entries (exception, breadcrumbs, request, etc.).

    `errors: list[typing.Any] | None`
    :   Processing errors.

    `event_id: str | None`
    :   Event ID as reported by the client.

    `event_type: str | None`
    :   The type of the event.

    `fingerprints: list[typing.Any] | None`
    :   Fingerprints used for grouping.

    `group_id: str | None`
    :   ID of the issue group this event belongs to.

    `grouping_config: dict[str, typing.Any] | None`
    :   Grouping configuration.

    `id: str | None`
    :   Unique event identifier.

    `location: str | None`
    :   Location in source code.

    `message: str | None`
    :   Event message.

    `meta: dict[str, typing.Any] | None`
    :   Meta information for data scrubbing.

    `metadata: dict[str, typing.Any] | None`
    :   Event metadata.

    `occurrence: str | None`
    :   Occurrence information for the event.

    `packages: dict[str, typing.Any] | None`
    :   Package information.

    `platform: str | None`
    :   Platform the event was generated on.

    `project_id: str | None`
    :   Project ID this event belongs to.

    `sdk: str | None`
    :   SDK information.

    `size: int | None`
    :   Event payload size in bytes.

    `tags: list[typing.Any] | None`
    :   Tags associated with the event.

    `title: str | None`
    :   Event title.

    `type_: str | None`
    :   Event type.

    `user: dict[str, typing.Any] | None`
    :   User associated with the event.

<a id="EventsSearchQuery"></a>

`EventsSearchQuery(*args, **kwargs)`
:   Search query for events entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sentry.types.EventsEqCondition | airbyte_agent_sdk.connectors.sentry.types.EventsNeqCondition | airbyte_agent_sdk.connectors.sentry.types.EventsGtCondition | airbyte_agent_sdk.connectors.sentry.types.EventsGteCondition | airbyte_agent_sdk.connectors.sentry.types.EventsLtCondition | airbyte_agent_sdk.connectors.sentry.types.EventsLteCondition | airbyte_agent_sdk.connectors.sentry.types.EventsInCondition | airbyte_agent_sdk.connectors.sentry.types.EventsLikeCondition | airbyte_agent_sdk.connectors.sentry.types.EventsFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.EventsKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.EventsContainsCondition | airbyte_agent_sdk.connectors.sentry.types.EventsNotCondition | airbyte_agent_sdk.connectors.sentry.types.EventsAndCondition | airbyte_agent_sdk.connectors.sentry.types.EventsOrCondition | airbyte_agent_sdk.connectors.sentry.types.EventsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sentry.types.EventsSortFilter]`
    :   The type of the None singleton.

<a id="EventsSortFilter"></a>

`EventsSortFilter(*args, **kwargs)`
:   Available fields for sorting events search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `context: Literal['asc', 'desc']`
    :   Additional context data.

    `contexts: Literal['asc', 'desc']`
    :   Structured context information.

    `crash_file: Literal['asc', 'desc']`
    :   Crash file reference.

    `culprit: Literal['asc', 'desc']`
    :   The culprit (source) of the event.

    `date_created: Literal['asc', 'desc']`
    :   When the event was created.

    `date_received: Literal['asc', 'desc']`
    :   When the event was received by Sentry.

    `dist: Literal['asc', 'desc']`
    :   Distribution information.

    `entries: Literal['asc', 'desc']`
    :   Event entries (exception, breadcrumbs, request, etc.).

    `errors: Literal['asc', 'desc']`
    :   Processing errors.

    `event_id: Literal['asc', 'desc']`
    :   Event ID as reported by the client.

    `event_type: Literal['asc', 'desc']`
    :   The type of the event.

    `fingerprints: Literal['asc', 'desc']`
    :   Fingerprints used for grouping.

    `group_id: Literal['asc', 'desc']`
    :   ID of the issue group this event belongs to.

    `grouping_config: Literal['asc', 'desc']`
    :   Grouping configuration.

    `id: Literal['asc', 'desc']`
    :   Unique event identifier.

    `location: Literal['asc', 'desc']`
    :   Location in source code.

    `message: Literal['asc', 'desc']`
    :   Event message.

    `meta: Literal['asc', 'desc']`
    :   Meta information for data scrubbing.

    `metadata: Literal['asc', 'desc']`
    :   Event metadata.

    `occurrence: Literal['asc', 'desc']`
    :   Occurrence information for the event.

    `packages: Literal['asc', 'desc']`
    :   Package information.

    `platform: Literal['asc', 'desc']`
    :   Platform the event was generated on.

    `project_id: Literal['asc', 'desc']`
    :   Project ID this event belongs to.

    `sdk: Literal['asc', 'desc']`
    :   SDK information.

    `size: Literal['asc', 'desc']`
    :   Event payload size in bytes.

    `tags: Literal['asc', 'desc']`
    :   Tags associated with the event.

    `title: Literal['asc', 'desc']`
    :   Event title.

    `type_: Literal['asc', 'desc']`
    :   Event type.

    `user: Literal['asc', 'desc']`
    :   User associated with the event.

<a id="EventsStringFilter"></a>

`EventsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `context: str`
    :   Additional context data.

    `contexts: str`
    :   Structured context information.

    `crash_file: str`
    :   Crash file reference.

    `culprit: str`
    :   The culprit (source) of the event.

    `date_created: str`
    :   When the event was created.

    `date_received: str`
    :   When the event was received by Sentry.

    `dist: str`
    :   Distribution information.

    `entries: str`
    :   Event entries (exception, breadcrumbs, request, etc.).

    `errors: str`
    :   Processing errors.

    `event_id: str`
    :   Event ID as reported by the client.

    `event_type: str`
    :   The type of the event.

    `fingerprints: str`
    :   Fingerprints used for grouping.

    `group_id: str`
    :   ID of the issue group this event belongs to.

    `grouping_config: str`
    :   Grouping configuration.

    `id: str`
    :   Unique event identifier.

    `location: str`
    :   Location in source code.

    `message: str`
    :   Event message.

    `meta: str`
    :   Meta information for data scrubbing.

    `metadata: str`
    :   Event metadata.

    `occurrence: str`
    :   Occurrence information for the event.

    `packages: str`
    :   Package information.

    `platform: str`
    :   Platform the event was generated on.

    `project_id: str`
    :   Project ID this event belongs to.

    `sdk: str`
    :   SDK information.

    `size: str`
    :   Event payload size in bytes.

    `tags: str`
    :   Tags associated with the event.

    `title: str`
    :   Event title.

    `type_: str`
    :   Event type.

    `user: str`
    :   User associated with the event.

<a id="IssuesAndCondition"></a>

`IssuesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sentry.types.IssuesEqCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesGtCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesGteCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesLtCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesLteCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesInCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesNotCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesAndCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesOrCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesAnyCondition]`
    :   The type of the None singleton.

<a id="IssuesAnyCondition"></a>

`IssuesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sentry.types.IssuesAnyValueFilter`
    :   The type of the None singleton.

<a id="IssuesAnyValueFilter"></a>

`IssuesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: Any`
    :   Annotations on the issue.

    `assigned_to: Any`
    :   User or team assigned to this issue.

    `count: Any`
    :   Number of events for this issue.

    `culprit: Any`
    :   The culprit (source) of the issue.

    `first_seen: Any`
    :   When the issue was first seen.

    `has_seen: Any`
    :   Whether the authenticated user has seen the issue.

    `id: Any`
    :   Unique issue identifier.

    `is_bookmarked: Any`
    :   Whether the issue is bookmarked.

    `is_public: Any`
    :   Whether the issue is public.

    `is_subscribed: Any`
    :   Whether the user is subscribed to the issue.

    `is_unhandled: Any`
    :   Whether the issue is from an unhandled error.

    `issue_category: Any`
    :   The category classification of the issue.

    `issue_type: Any`
    :   The type classification of the issue.

    `last_seen: Any`
    :   When the issue was last seen.

    `level: Any`
    :   Issue severity level.

    `logger: Any`
    :   Logger that generated the issue.

    `metadata: Any`
    :   Issue metadata.

    `num_comments: Any`
    :   Number of comments on the issue.

    `permalink: Any`
    :   Permalink to the issue in the Sentry UI.

    `platform: Any`
    :   Platform for this issue.

    `project: Any`
    :   Project this issue belongs to.

    `share_id: Any`
    :   Share ID if the issue is shared.

    `short_id: Any`
    :   Short human-readable identifier.

    `stats: Any`
    :   Issue event statistics.

    `status: Any`
    :   Issue status (resolved, unresolved, ignored).

    `status_details: Any`
    :   Status detail information.

    `subscription_details: Any`
    :   Subscription details.

    `substatus: Any`
    :   Issue substatus.

    `title: Any`
    :   Issue title.

    `type_: Any`
    :   Issue type.

    `user_count: Any`
    :   Number of users affected.

<a id="IssuesContainsCondition"></a>

`IssuesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sentry.types.IssuesAnyValueFilter`
    :   The type of the None singleton.

<a id="IssuesEqCondition"></a>

`IssuesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sentry.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesFuzzyCondition"></a>

`IssuesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sentry.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesGetParams"></a>

`IssuesGetParams(*args, **kwargs)`
:   Parameters for issues.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `issue_id: str`
    :   The type of the None singleton.

    `organization_slug: str`
    :   The type of the None singleton.

<a id="IssuesGtCondition"></a>

`IssuesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sentry.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesGteCondition"></a>

`IssuesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sentry.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesInCondition"></a>

`IssuesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sentry.types.IssuesInFilter`
    :   The type of the None singleton.

<a id="IssuesInFilter"></a>

`IssuesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: list[list[typing.Any]]`
    :   Annotations on the issue.

    `assigned_to: list[dict[str, typing.Any]]`
    :   User or team assigned to this issue.

    `count: list[str]`
    :   Number of events for this issue.

    `culprit: list[str]`
    :   The culprit (source) of the issue.

    `first_seen: list[str]`
    :   When the issue was first seen.

    `has_seen: list[bool]`
    :   Whether the authenticated user has seen the issue.

    `id: list[str]`
    :   Unique issue identifier.

    `is_bookmarked: list[bool]`
    :   Whether the issue is bookmarked.

    `is_public: list[bool]`
    :   Whether the issue is public.

    `is_subscribed: list[bool]`
    :   Whether the user is subscribed to the issue.

    `is_unhandled: list[bool]`
    :   Whether the issue is from an unhandled error.

    `issue_category: list[str]`
    :   The category classification of the issue.

    `issue_type: list[str]`
    :   The type classification of the issue.

    `last_seen: list[str]`
    :   When the issue was last seen.

    `level: list[str]`
    :   Issue severity level.

    `logger: list[str]`
    :   Logger that generated the issue.

    `metadata: list[dict[str, typing.Any]]`
    :   Issue metadata.

    `num_comments: list[int]`
    :   Number of comments on the issue.

    `permalink: list[str]`
    :   Permalink to the issue in the Sentry UI.

    `platform: list[str]`
    :   Platform for this issue.

    `project: list[dict[str, typing.Any]]`
    :   Project this issue belongs to.

    `share_id: list[str]`
    :   Share ID if the issue is shared.

    `short_id: list[str]`
    :   Short human-readable identifier.

    `stats: list[dict[str, typing.Any]]`
    :   Issue event statistics.

    `status: list[str]`
    :   Issue status (resolved, unresolved, ignored).

    `status_details: list[dict[str, typing.Any]]`
    :   Status detail information.

    `subscription_details: list[dict[str, typing.Any]]`
    :   Subscription details.

    `substatus: list[str]`
    :   Issue substatus.

    `title: list[str]`
    :   Issue title.

    `type_: list[str]`
    :   Issue type.

    `user_count: list[int]`
    :   Number of users affected.

<a id="IssuesKeywordCondition"></a>

`IssuesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sentry.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesLikeCondition"></a>

`IssuesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sentry.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesListParams"></a>

`IssuesListParams(*args, **kwargs)`
:   Parameters for issues.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `organization_slug: str`
    :   The type of the None singleton.

    `project_slug: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

    `stats_period: str`
    :   The type of the None singleton.

<a id="IssuesLtCondition"></a>

`IssuesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sentry.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesLteCondition"></a>

`IssuesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sentry.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesNeqCondition"></a>

`IssuesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sentry.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesNotCondition"></a>

`IssuesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sentry.types.IssuesEqCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesGtCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesGteCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesLtCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesLteCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesInCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesNotCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesAndCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesOrCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesAnyCondition`
    :   The type of the None singleton.

<a id="IssuesOrCondition"></a>

`IssuesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sentry.types.IssuesEqCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesGtCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesGteCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesLtCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesLteCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesInCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesNotCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesAndCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesOrCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesAnyCondition]`
    :   The type of the None singleton.

<a id="IssuesSearchFilter"></a>

`IssuesSearchFilter(*args, **kwargs)`
:   Available fields for filtering issues search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: list[typing.Any] | None`
    :   Annotations on the issue.

    `assigned_to: dict[str, typing.Any] | None`
    :   User or team assigned to this issue.

    `count: str | None`
    :   Number of events for this issue.

    `culprit: str | None`
    :   The culprit (source) of the issue.

    `first_seen: str | None`
    :   When the issue was first seen.

    `has_seen: bool | None`
    :   Whether the authenticated user has seen the issue.

    `id: str | None`
    :   Unique issue identifier.

    `is_bookmarked: bool | None`
    :   Whether the issue is bookmarked.

    `is_public: bool | None`
    :   Whether the issue is public.

    `is_subscribed: bool | None`
    :   Whether the user is subscribed to the issue.

    `is_unhandled: bool | None`
    :   Whether the issue is from an unhandled error.

    `issue_category: str | None`
    :   The category classification of the issue.

    `issue_type: str | None`
    :   The type classification of the issue.

    `last_seen: str | None`
    :   When the issue was last seen.

    `level: str | None`
    :   Issue severity level.

    `logger: str | None`
    :   Logger that generated the issue.

    `metadata: dict[str, typing.Any] | None`
    :   Issue metadata.

    `num_comments: int | None`
    :   Number of comments on the issue.

    `permalink: str | None`
    :   Permalink to the issue in the Sentry UI.

    `platform: str | None`
    :   Platform for this issue.

    `project: dict[str, typing.Any] | None`
    :   Project this issue belongs to.

    `share_id: str | None`
    :   Share ID if the issue is shared.

    `short_id: str | None`
    :   Short human-readable identifier.

    `stats: dict[str, typing.Any] | None`
    :   Issue event statistics.

    `status: str | None`
    :   Issue status (resolved, unresolved, ignored).

    `status_details: dict[str, typing.Any] | None`
    :   Status detail information.

    `subscription_details: dict[str, typing.Any] | None`
    :   Subscription details.

    `substatus: str | None`
    :   Issue substatus.

    `title: str | None`
    :   Issue title.

    `type_: str | None`
    :   Issue type.

    `user_count: int | None`
    :   Number of users affected.

<a id="IssuesSearchQuery"></a>

`IssuesSearchQuery(*args, **kwargs)`
:   Search query for issues entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sentry.types.IssuesEqCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesGtCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesGteCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesLtCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesLteCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesInCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesNotCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesAndCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesOrCondition | airbyte_agent_sdk.connectors.sentry.types.IssuesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sentry.types.IssuesSortFilter]`
    :   The type of the None singleton.

<a id="IssuesSortFilter"></a>

`IssuesSortFilter(*args, **kwargs)`
:   Available fields for sorting issues search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: Literal['asc', 'desc']`
    :   Annotations on the issue.

    `assigned_to: Literal['asc', 'desc']`
    :   User or team assigned to this issue.

    `count: Literal['asc', 'desc']`
    :   Number of events for this issue.

    `culprit: Literal['asc', 'desc']`
    :   The culprit (source) of the issue.

    `first_seen: Literal['asc', 'desc']`
    :   When the issue was first seen.

    `has_seen: Literal['asc', 'desc']`
    :   Whether the authenticated user has seen the issue.

    `id: Literal['asc', 'desc']`
    :   Unique issue identifier.

    `is_bookmarked: Literal['asc', 'desc']`
    :   Whether the issue is bookmarked.

    `is_public: Literal['asc', 'desc']`
    :   Whether the issue is public.

    `is_subscribed: Literal['asc', 'desc']`
    :   Whether the user is subscribed to the issue.

    `is_unhandled: Literal['asc', 'desc']`
    :   Whether the issue is from an unhandled error.

    `issue_category: Literal['asc', 'desc']`
    :   The category classification of the issue.

    `issue_type: Literal['asc', 'desc']`
    :   The type classification of the issue.

    `last_seen: Literal['asc', 'desc']`
    :   When the issue was last seen.

    `level: Literal['asc', 'desc']`
    :   Issue severity level.

    `logger: Literal['asc', 'desc']`
    :   Logger that generated the issue.

    `metadata: Literal['asc', 'desc']`
    :   Issue metadata.

    `num_comments: Literal['asc', 'desc']`
    :   Number of comments on the issue.

    `permalink: Literal['asc', 'desc']`
    :   Permalink to the issue in the Sentry UI.

    `platform: Literal['asc', 'desc']`
    :   Platform for this issue.

    `project: Literal['asc', 'desc']`
    :   Project this issue belongs to.

    `share_id: Literal['asc', 'desc']`
    :   Share ID if the issue is shared.

    `short_id: Literal['asc', 'desc']`
    :   Short human-readable identifier.

    `stats: Literal['asc', 'desc']`
    :   Issue event statistics.

    `status: Literal['asc', 'desc']`
    :   Issue status (resolved, unresolved, ignored).

    `status_details: Literal['asc', 'desc']`
    :   Status detail information.

    `subscription_details: Literal['asc', 'desc']`
    :   Subscription details.

    `substatus: Literal['asc', 'desc']`
    :   Issue substatus.

    `title: Literal['asc', 'desc']`
    :   Issue title.

    `type_: Literal['asc', 'desc']`
    :   Issue type.

    `user_count: Literal['asc', 'desc']`
    :   Number of users affected.

<a id="IssuesStringFilter"></a>

`IssuesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: str`
    :   Annotations on the issue.

    `assigned_to: str`
    :   User or team assigned to this issue.

    `count: str`
    :   Number of events for this issue.

    `culprit: str`
    :   The culprit (source) of the issue.

    `first_seen: str`
    :   When the issue was first seen.

    `has_seen: str`
    :   Whether the authenticated user has seen the issue.

    `id: str`
    :   Unique issue identifier.

    `is_bookmarked: str`
    :   Whether the issue is bookmarked.

    `is_public: str`
    :   Whether the issue is public.

    `is_subscribed: str`
    :   Whether the user is subscribed to the issue.

    `is_unhandled: str`
    :   Whether the issue is from an unhandled error.

    `issue_category: str`
    :   The category classification of the issue.

    `issue_type: str`
    :   The type classification of the issue.

    `last_seen: str`
    :   When the issue was last seen.

    `level: str`
    :   Issue severity level.

    `logger: str`
    :   Logger that generated the issue.

    `metadata: str`
    :   Issue metadata.

    `num_comments: str`
    :   Number of comments on the issue.

    `permalink: str`
    :   Permalink to the issue in the Sentry UI.

    `platform: str`
    :   Platform for this issue.

    `project: str`
    :   Project this issue belongs to.

    `share_id: str`
    :   Share ID if the issue is shared.

    `short_id: str`
    :   Short human-readable identifier.

    `stats: str`
    :   Issue event statistics.

    `status: str`
    :   Issue status (resolved, unresolved, ignored).

    `status_details: str`
    :   Status detail information.

    `subscription_details: str`
    :   Subscription details.

    `substatus: str`
    :   Issue substatus.

    `title: str`
    :   Issue title.

    `type_: str`
    :   Issue type.

    `user_count: str`
    :   Number of users affected.

<a id="ProjectDetailGetParams"></a>

`ProjectDetailGetParams(*args, **kwargs)`
:   Parameters for project_detail.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `organization_slug: str`
    :   The type of the None singleton.

    `project_slug: str`
    :   The type of the None singleton.

<a id="ProjectsAndCondition"></a>

`ProjectsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sentry.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsInCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsAnyCondition]`
    :   The type of the None singleton.

<a id="ProjectsAnyCondition"></a>

`ProjectsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sentry.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectsAnyValueFilter"></a>

`ProjectsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access: Any`
    :   List of access permissions for the authenticated user.

    `avatar: Any`
    :   Project avatar information.

    `color: Any`
    :   Project color code.

    `date_created: Any`
    :   Date the project was created.

    `features: Any`
    :   List of enabled features.

    `first_event: Any`
    :   Timestamp of the first event.

    `first_transaction_event: Any`
    :   Whether a transaction event has been received.

    `has_access: Any`
    :   Whether the user has access to this project.

    `has_custom_metrics: Any`
    :   Whether the project has custom metrics.

    `has_feedbacks: Any`
    :   Whether the project has user feedback.

    `has_minified_stack_trace: Any`
    :   Whether the project has minified stack traces.

    `has_monitors: Any`
    :   Whether the project has cron monitors.

    `has_new_feedbacks: Any`
    :   Whether the project has new user feedback.

    `has_profiles: Any`
    :   Whether the project has profiling data.

    `has_replays: Any`
    :   Whether the project has session replays.

    `has_sessions: Any`
    :   Whether the project has session data.

    `id: Any`
    :   Unique project identifier.

    `is_bookmarked: Any`
    :   Whether the project is bookmarked.

    `is_internal: Any`
    :   Whether the project is internal.

    `is_member: Any`
    :   Whether the authenticated user is a member.

    `is_public: Any`
    :   Whether the project is public.

    `name: Any`
    :   Human-readable project name.

    `organization: Any`
    :   Organization this project belongs to.

    `platform: Any`
    :   The platform for this project.

    `slug: Any`
    :   URL-friendly project identifier.

    `status: Any`
    :   Project status.

<a id="ProjectsContainsCondition"></a>

`ProjectsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sentry.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectsEqCondition"></a>

`ProjectsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sentry.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsFuzzyCondition"></a>

`ProjectsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sentry.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsGetParams"></a>

`ProjectsGetParams(*args, **kwargs)`
:   Parameters for projects.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `organization_slug: str`
    :   The type of the None singleton.

    `project_slug: str`
    :   The type of the None singleton.

<a id="ProjectsGtCondition"></a>

`ProjectsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sentry.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsGteCondition"></a>

`ProjectsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sentry.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsInCondition"></a>

`ProjectsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sentry.types.ProjectsInFilter`
    :   The type of the None singleton.

<a id="ProjectsInFilter"></a>

`ProjectsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access: list[list[typing.Any]]`
    :   List of access permissions for the authenticated user.

    `avatar: list[dict[str, typing.Any]]`
    :   Project avatar information.

    `color: list[str]`
    :   Project color code.

    `date_created: list[str]`
    :   Date the project was created.

    `features: list[list[typing.Any]]`
    :   List of enabled features.

    `first_event: list[str]`
    :   Timestamp of the first event.

    `first_transaction_event: list[bool]`
    :   Whether a transaction event has been received.

    `has_access: list[bool]`
    :   Whether the user has access to this project.

    `has_custom_metrics: list[bool]`
    :   Whether the project has custom metrics.

    `has_feedbacks: list[bool]`
    :   Whether the project has user feedback.

    `has_minified_stack_trace: list[bool]`
    :   Whether the project has minified stack traces.

    `has_monitors: list[bool]`
    :   Whether the project has cron monitors.

    `has_new_feedbacks: list[bool]`
    :   Whether the project has new user feedback.

    `has_profiles: list[bool]`
    :   Whether the project has profiling data.

    `has_replays: list[bool]`
    :   Whether the project has session replays.

    `has_sessions: list[bool]`
    :   Whether the project has session data.

    `id: list[str]`
    :   Unique project identifier.

    `is_bookmarked: list[bool]`
    :   Whether the project is bookmarked.

    `is_internal: list[bool]`
    :   Whether the project is internal.

    `is_member: list[bool]`
    :   Whether the authenticated user is a member.

    `is_public: list[bool]`
    :   Whether the project is public.

    `name: list[str]`
    :   Human-readable project name.

    `organization: list[dict[str, typing.Any]]`
    :   Organization this project belongs to.

    `platform: list[str]`
    :   The platform for this project.

    `slug: list[str]`
    :   URL-friendly project identifier.

    `status: list[str]`
    :   Project status.

<a id="ProjectsKeywordCondition"></a>

`ProjectsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sentry.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsLikeCondition"></a>

`ProjectsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sentry.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsListParams"></a>

`ProjectsListParams(*args, **kwargs)`
:   Parameters for projects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

<a id="ProjectsLtCondition"></a>

`ProjectsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sentry.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsLteCondition"></a>

`ProjectsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sentry.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsNeqCondition"></a>

`ProjectsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sentry.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsNotCondition"></a>

`ProjectsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sentry.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsInCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsAnyCondition`
    :   The type of the None singleton.

<a id="ProjectsOrCondition"></a>

`ProjectsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sentry.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsInCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsAnyCondition]`
    :   The type of the None singleton.

<a id="ProjectsSearchFilter"></a>

`ProjectsSearchFilter(*args, **kwargs)`
:   Available fields for filtering projects search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access: list[typing.Any] | None`
    :   List of access permissions for the authenticated user.

    `avatar: dict[str, typing.Any] | None`
    :   Project avatar information.

    `color: str | None`
    :   Project color code.

    `date_created: str | None`
    :   Date the project was created.

    `features: list[typing.Any] | None`
    :   List of enabled features.

    `first_event: str | None`
    :   Timestamp of the first event.

    `first_transaction_event: bool | None`
    :   Whether a transaction event has been received.

    `has_access: bool | None`
    :   Whether the user has access to this project.

    `has_custom_metrics: bool | None`
    :   Whether the project has custom metrics.

    `has_feedbacks: bool | None`
    :   Whether the project has user feedback.

    `has_minified_stack_trace: bool | None`
    :   Whether the project has minified stack traces.

    `has_monitors: bool | None`
    :   Whether the project has cron monitors.

    `has_new_feedbacks: bool | None`
    :   Whether the project has new user feedback.

    `has_profiles: bool | None`
    :   Whether the project has profiling data.

    `has_replays: bool | None`
    :   Whether the project has session replays.

    `has_sessions: bool | None`
    :   Whether the project has session data.

    `id: str | None`
    :   Unique project identifier.

    `is_bookmarked: bool | None`
    :   Whether the project is bookmarked.

    `is_internal: bool | None`
    :   Whether the project is internal.

    `is_member: bool | None`
    :   Whether the authenticated user is a member.

    `is_public: bool | None`
    :   Whether the project is public.

    `name: str | None`
    :   Human-readable project name.

    `organization: dict[str, typing.Any] | None`
    :   Organization this project belongs to.

    `platform: str | None`
    :   The platform for this project.

    `slug: str | None`
    :   URL-friendly project identifier.

    `status: str | None`
    :   Project status.

<a id="ProjectsSearchQuery"></a>

`ProjectsSearchQuery(*args, **kwargs)`
:   Search query for projects entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sentry.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsInCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.sentry.types.ProjectsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sentry.types.ProjectsSortFilter]`
    :   The type of the None singleton.

<a id="ProjectsSortFilter"></a>

`ProjectsSortFilter(*args, **kwargs)`
:   Available fields for sorting projects search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access: Literal['asc', 'desc']`
    :   List of access permissions for the authenticated user.

    `avatar: Literal['asc', 'desc']`
    :   Project avatar information.

    `color: Literal['asc', 'desc']`
    :   Project color code.

    `date_created: Literal['asc', 'desc']`
    :   Date the project was created.

    `features: Literal['asc', 'desc']`
    :   List of enabled features.

    `first_event: Literal['asc', 'desc']`
    :   Timestamp of the first event.

    `first_transaction_event: Literal['asc', 'desc']`
    :   Whether a transaction event has been received.

    `has_access: Literal['asc', 'desc']`
    :   Whether the user has access to this project.

    `has_custom_metrics: Literal['asc', 'desc']`
    :   Whether the project has custom metrics.

    `has_feedbacks: Literal['asc', 'desc']`
    :   Whether the project has user feedback.

    `has_minified_stack_trace: Literal['asc', 'desc']`
    :   Whether the project has minified stack traces.

    `has_monitors: Literal['asc', 'desc']`
    :   Whether the project has cron monitors.

    `has_new_feedbacks: Literal['asc', 'desc']`
    :   Whether the project has new user feedback.

    `has_profiles: Literal['asc', 'desc']`
    :   Whether the project has profiling data.

    `has_replays: Literal['asc', 'desc']`
    :   Whether the project has session replays.

    `has_sessions: Literal['asc', 'desc']`
    :   Whether the project has session data.

    `id: Literal['asc', 'desc']`
    :   Unique project identifier.

    `is_bookmarked: Literal['asc', 'desc']`
    :   Whether the project is bookmarked.

    `is_internal: Literal['asc', 'desc']`
    :   Whether the project is internal.

    `is_member: Literal['asc', 'desc']`
    :   Whether the authenticated user is a member.

    `is_public: Literal['asc', 'desc']`
    :   Whether the project is public.

    `name: Literal['asc', 'desc']`
    :   Human-readable project name.

    `organization: Literal['asc', 'desc']`
    :   Organization this project belongs to.

    `platform: Literal['asc', 'desc']`
    :   The platform for this project.

    `slug: Literal['asc', 'desc']`
    :   URL-friendly project identifier.

    `status: Literal['asc', 'desc']`
    :   Project status.

<a id="ProjectsStringFilter"></a>

`ProjectsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access: str`
    :   List of access permissions for the authenticated user.

    `avatar: str`
    :   Project avatar information.

    `color: str`
    :   Project color code.

    `date_created: str`
    :   Date the project was created.

    `features: str`
    :   List of enabled features.

    `first_event: str`
    :   Timestamp of the first event.

    `first_transaction_event: str`
    :   Whether a transaction event has been received.

    `has_access: str`
    :   Whether the user has access to this project.

    `has_custom_metrics: str`
    :   Whether the project has custom metrics.

    `has_feedbacks: str`
    :   Whether the project has user feedback.

    `has_minified_stack_trace: str`
    :   Whether the project has minified stack traces.

    `has_monitors: str`
    :   Whether the project has cron monitors.

    `has_new_feedbacks: str`
    :   Whether the project has new user feedback.

    `has_profiles: str`
    :   Whether the project has profiling data.

    `has_replays: str`
    :   Whether the project has session replays.

    `has_sessions: str`
    :   Whether the project has session data.

    `id: str`
    :   Unique project identifier.

    `is_bookmarked: str`
    :   Whether the project is bookmarked.

    `is_internal: str`
    :   Whether the project is internal.

    `is_member: str`
    :   Whether the authenticated user is a member.

    `is_public: str`
    :   Whether the project is public.

    `name: str`
    :   Human-readable project name.

    `organization: str`
    :   Organization this project belongs to.

    `platform: str`
    :   The platform for this project.

    `slug: str`
    :   URL-friendly project identifier.

    `status: str`
    :   Project status.

<a id="ReleasesAndCondition"></a>

`ReleasesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sentry.types.ReleasesEqCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesNeqCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesGtCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesGteCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesLtCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesLteCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesInCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesLikeCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesContainsCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesNotCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesAndCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesOrCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesAnyCondition]`
    :   The type of the None singleton.

<a id="ReleasesAnyCondition"></a>

`ReleasesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sentry.types.ReleasesAnyValueFilter`
    :   The type of the None singleton.

<a id="ReleasesAnyValueFilter"></a>

`ReleasesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `authors: Any`
    :   Authors of commits in this release.

    `commit_count: Any`
    :   Number of commits in this release.

    `current_project_meta: Any`
    :   Metadata for the current project context.

    `data: Any`
    :   Additional release data.

    `date_created: Any`
    :   When the release was created.

    `date_released: Any`
    :   When the release was deployed.

    `deploy_count: Any`
    :   Number of deploys for this release.

    `first_event: Any`
    :   Timestamp of the first event in this release.

    `id: Any`
    :   Unique release identifier.

    `last_commit: Any`
    :   Last commit in this release.

    `last_deploy: Any`
    :   Last deploy of this release.

    `last_event: Any`
    :   Timestamp of the last event in this release.

    `new_groups: Any`
    :   Number of new issue groups in this release.

    `owner: Any`
    :   Owner of the release.

    `projects: Any`
    :   Projects associated with this release.

    `ref: Any`
    :   Git reference (commit SHA, tag, etc.).

    `short_version: Any`
    :   Short version string.

    `status: Any`
    :   Release status.

    `url: Any`
    :   URL associated with the release.

    `user_agent: Any`
    :   User agent that created the release.

    `version: Any`
    :   Release version string.

    `version_info: Any`
    :   Parsed version information.

<a id="ReleasesContainsCondition"></a>

`ReleasesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sentry.types.ReleasesAnyValueFilter`
    :   The type of the None singleton.

<a id="ReleasesEqCondition"></a>

`ReleasesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sentry.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesFuzzyCondition"></a>

`ReleasesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sentry.types.ReleasesStringFilter`
    :   The type of the None singleton.

<a id="ReleasesGetParams"></a>

`ReleasesGetParams(*args, **kwargs)`
:   Parameters for releases.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `organization_slug: str`
    :   The type of the None singleton.

    `version: str`
    :   The type of the None singleton.

<a id="ReleasesGtCondition"></a>

`ReleasesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sentry.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesGteCondition"></a>

`ReleasesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sentry.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesInCondition"></a>

`ReleasesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sentry.types.ReleasesInFilter`
    :   The type of the None singleton.

<a id="ReleasesInFilter"></a>

`ReleasesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `authors: list[list[typing.Any]]`
    :   Authors of commits in this release.

    `commit_count: list[int]`
    :   Number of commits in this release.

    `current_project_meta: list[dict[str, typing.Any]]`
    :   Metadata for the current project context.

    `data: list[dict[str, typing.Any]]`
    :   Additional release data.

    `date_created: list[str]`
    :   When the release was created.

    `date_released: list[str]`
    :   When the release was deployed.

    `deploy_count: list[int]`
    :   Number of deploys for this release.

    `first_event: list[str]`
    :   Timestamp of the first event in this release.

    `id: list[int]`
    :   Unique release identifier.

    `last_commit: list[dict[str, typing.Any]]`
    :   Last commit in this release.

    `last_deploy: list[dict[str, typing.Any]]`
    :   Last deploy of this release.

    `last_event: list[str]`
    :   Timestamp of the last event in this release.

    `new_groups: list[int]`
    :   Number of new issue groups in this release.

    `owner: list[str]`
    :   Owner of the release.

    `projects: list[list[typing.Any]]`
    :   Projects associated with this release.

    `ref: list[str]`
    :   Git reference (commit SHA, tag, etc.).

    `short_version: list[str]`
    :   Short version string.

    `status: list[str]`
    :   Release status.

    `url: list[str]`
    :   URL associated with the release.

    `user_agent: list[str]`
    :   User agent that created the release.

    `version: list[str]`
    :   Release version string.

    `version_info: list[dict[str, typing.Any]]`
    :   Parsed version information.

<a id="ReleasesKeywordCondition"></a>

`ReleasesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sentry.types.ReleasesStringFilter`
    :   The type of the None singleton.

<a id="ReleasesLikeCondition"></a>

`ReleasesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sentry.types.ReleasesStringFilter`
    :   The type of the None singleton.

<a id="ReleasesListParams"></a>

`ReleasesListParams(*args, **kwargs)`
:   Parameters for releases.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `organization_slug: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="ReleasesLtCondition"></a>

`ReleasesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sentry.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesLteCondition"></a>

`ReleasesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sentry.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesNeqCondition"></a>

`ReleasesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sentry.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesNotCondition"></a>

`ReleasesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sentry.types.ReleasesEqCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesNeqCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesGtCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesGteCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesLtCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesLteCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesInCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesLikeCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesContainsCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesNotCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesAndCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesOrCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesAnyCondition`
    :   The type of the None singleton.

<a id="ReleasesOrCondition"></a>

`ReleasesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sentry.types.ReleasesEqCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesNeqCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesGtCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesGteCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesLtCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesLteCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesInCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesLikeCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesContainsCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesNotCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesAndCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesOrCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesAnyCondition]`
    :   The type of the None singleton.

<a id="ReleasesSearchFilter"></a>

`ReleasesSearchFilter(*args, **kwargs)`
:   Available fields for filtering releases search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `authors: list[typing.Any] | None`
    :   Authors of commits in this release.

    `commit_count: int | None`
    :   Number of commits in this release.

    `current_project_meta: dict[str, typing.Any] | None`
    :   Metadata for the current project context.

    `data: dict[str, typing.Any] | None`
    :   Additional release data.

    `date_created: str | None`
    :   When the release was created.

    `date_released: str | None`
    :   When the release was deployed.

    `deploy_count: int | None`
    :   Number of deploys for this release.

    `first_event: str | None`
    :   Timestamp of the first event in this release.

    `id: int | None`
    :   Unique release identifier.

    `last_commit: dict[str, typing.Any] | None`
    :   Last commit in this release.

    `last_deploy: dict[str, typing.Any] | None`
    :   Last deploy of this release.

    `last_event: str | None`
    :   Timestamp of the last event in this release.

    `new_groups: int | None`
    :   Number of new issue groups in this release.

    `owner: str | None`
    :   Owner of the release.

    `projects: list[typing.Any] | None`
    :   Projects associated with this release.

    `ref: str | None`
    :   Git reference (commit SHA, tag, etc.).

    `short_version: str | None`
    :   Short version string.

    `status: str | None`
    :   Release status.

    `url: str | None`
    :   URL associated with the release.

    `user_agent: str | None`
    :   User agent that created the release.

    `version: str | None`
    :   Release version string.

    `version_info: dict[str, typing.Any] | None`
    :   Parsed version information.

<a id="ReleasesSearchQuery"></a>

`ReleasesSearchQuery(*args, **kwargs)`
:   Search query for releases entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sentry.types.ReleasesEqCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesNeqCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesGtCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesGteCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesLtCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesLteCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesInCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesLikeCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesFuzzyCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesKeywordCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesContainsCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesNotCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesAndCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesOrCondition | airbyte_agent_sdk.connectors.sentry.types.ReleasesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sentry.types.ReleasesSortFilter]`
    :   The type of the None singleton.

<a id="ReleasesSortFilter"></a>

`ReleasesSortFilter(*args, **kwargs)`
:   Available fields for sorting releases search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `authors: Literal['asc', 'desc']`
    :   Authors of commits in this release.

    `commit_count: Literal['asc', 'desc']`
    :   Number of commits in this release.

    `current_project_meta: Literal['asc', 'desc']`
    :   Metadata for the current project context.

    `data: Literal['asc', 'desc']`
    :   Additional release data.

    `date_created: Literal['asc', 'desc']`
    :   When the release was created.

    `date_released: Literal['asc', 'desc']`
    :   When the release was deployed.

    `deploy_count: Literal['asc', 'desc']`
    :   Number of deploys for this release.

    `first_event: Literal['asc', 'desc']`
    :   Timestamp of the first event in this release.

    `id: Literal['asc', 'desc']`
    :   Unique release identifier.

    `last_commit: Literal['asc', 'desc']`
    :   Last commit in this release.

    `last_deploy: Literal['asc', 'desc']`
    :   Last deploy of this release.

    `last_event: Literal['asc', 'desc']`
    :   Timestamp of the last event in this release.

    `new_groups: Literal['asc', 'desc']`
    :   Number of new issue groups in this release.

    `owner: Literal['asc', 'desc']`
    :   Owner of the release.

    `projects: Literal['asc', 'desc']`
    :   Projects associated with this release.

    `ref: Literal['asc', 'desc']`
    :   Git reference (commit SHA, tag, etc.).

    `short_version: Literal['asc', 'desc']`
    :   Short version string.

    `status: Literal['asc', 'desc']`
    :   Release status.

    `url: Literal['asc', 'desc']`
    :   URL associated with the release.

    `user_agent: Literal['asc', 'desc']`
    :   User agent that created the release.

    `version: Literal['asc', 'desc']`
    :   Release version string.

    `version_info: Literal['asc', 'desc']`
    :   Parsed version information.

<a id="ReleasesStringFilter"></a>

`ReleasesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `authors: str`
    :   Authors of commits in this release.

    `commit_count: str`
    :   Number of commits in this release.

    `current_project_meta: str`
    :   Metadata for the current project context.

    `data: str`
    :   Additional release data.

    `date_created: str`
    :   When the release was created.

    `date_released: str`
    :   When the release was deployed.

    `deploy_count: str`
    :   Number of deploys for this release.

    `first_event: str`
    :   Timestamp of the first event in this release.

    `id: str`
    :   Unique release identifier.

    `last_commit: str`
    :   Last commit in this release.

    `last_deploy: str`
    :   Last deploy of this release.

    `last_event: str`
    :   Timestamp of the last event in this release.

    `new_groups: str`
    :   Number of new issue groups in this release.

    `owner: str`
    :   Owner of the release.

    `projects: str`
    :   Projects associated with this release.

    `ref: str`
    :   Git reference (commit SHA, tag, etc.).

    `short_version: str`
    :   Short version string.

    `status: str`
    :   Release status.

    `url: str`
    :   URL associated with the release.

    `user_agent: str`
    :   User agent that created the release.

    `version: str`
    :   Release version string.

    `version_info: str`
    :   Parsed version information.