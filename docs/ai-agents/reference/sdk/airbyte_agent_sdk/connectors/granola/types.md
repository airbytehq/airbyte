---
id: airbyte_agent_sdk-connectors-granola-types
title: airbyte_agent_sdk.connectors.granola.types
---

Module airbyte_agent_sdk.connectors.granola.types
=================================================
Type definitions for granola connector.

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

<a id="NotesAndCondition"></a>

`NotesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.granola.types.NotesEqCondition | airbyte_agent_sdk.connectors.granola.types.NotesNeqCondition | airbyte_agent_sdk.connectors.granola.types.NotesGtCondition | airbyte_agent_sdk.connectors.granola.types.NotesGteCondition | airbyte_agent_sdk.connectors.granola.types.NotesLtCondition | airbyte_agent_sdk.connectors.granola.types.NotesLteCondition | airbyte_agent_sdk.connectors.granola.types.NotesInCondition | airbyte_agent_sdk.connectors.granola.types.NotesLikeCondition | airbyte_agent_sdk.connectors.granola.types.NotesFuzzyCondition | airbyte_agent_sdk.connectors.granola.types.NotesKeywordCondition | airbyte_agent_sdk.connectors.granola.types.NotesContainsCondition | airbyte_agent_sdk.connectors.granola.types.NotesNotCondition | airbyte_agent_sdk.connectors.granola.types.NotesAndCondition | airbyte_agent_sdk.connectors.granola.types.NotesOrCondition | airbyte_agent_sdk.connectors.granola.types.NotesAnyCondition]`
    :   The type of the None singleton.

<a id="NotesAnyCondition"></a>

`NotesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.granola.types.NotesAnyValueFilter`
    :   The type of the None singleton.

<a id="NotesAnyValueFilter"></a>

`NotesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attendees: Any`
    :   The attendees of the meeting.

    `calendar_event: Any`
    :   Associated calendar event details.

    `created_at: Any`
    :   The creation time of the note in ISO 8601 format.

    `folder_membership: Any`
    :   The folder membership of the note.

    `id: Any`
    :   The unique identifier of the note.

    `object_: Any`
    :   The object type, always "note".

    `owner: Any`
    :   The owner of the note.

    `summary_markdown: Any`
    :   Markdown formatted summary of the note.

    `summary_text: Any`
    :   Plain text summary of the note.

    `title: Any`
    :   The title of the note.

    `transcript: Any`
    :   Transcript of the meeting.

    `updated_at: Any`
    :   The last update time of the note in ISO 8601 format.

<a id="NotesContainsCondition"></a>

`NotesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.granola.types.NotesAnyValueFilter`
    :   The type of the None singleton.

<a id="NotesEqCondition"></a>

`NotesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.granola.types.NotesSearchFilter`
    :   The type of the None singleton.

<a id="NotesFuzzyCondition"></a>

`NotesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.granola.types.NotesStringFilter`
    :   The type of the None singleton.

<a id="NotesGetParams"></a>

`NotesGetParams(*args, **kwargs)`
:   Parameters for notes.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include: str`
    :   The type of the None singleton.

    `note_id: str`
    :   The type of the None singleton.

<a id="NotesGtCondition"></a>

`NotesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.granola.types.NotesSearchFilter`
    :   The type of the None singleton.

<a id="NotesGteCondition"></a>

`NotesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.granola.types.NotesSearchFilter`
    :   The type of the None singleton.

<a id="NotesInCondition"></a>

`NotesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.granola.types.NotesInFilter`
    :   The type of the None singleton.

<a id="NotesInFilter"></a>

`NotesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attendees: list[list[typing.Any]]`
    :   The attendees of the meeting.

    `calendar_event: list[dict[str, typing.Any]]`
    :   Associated calendar event details.

    `created_at: list[str]`
    :   The creation time of the note in ISO 8601 format.

    `folder_membership: list[list[typing.Any]]`
    :   The folder membership of the note.

    `id: list[str]`
    :   The unique identifier of the note.

    `object_: list[str]`
    :   The object type, always "note".

    `owner: list[dict[str, typing.Any]]`
    :   The owner of the note.

    `summary_markdown: list[str]`
    :   Markdown formatted summary of the note.

    `summary_text: list[str]`
    :   Plain text summary of the note.

    `title: list[str]`
    :   The title of the note.

    `transcript: list[list[typing.Any]]`
    :   Transcript of the meeting.

    `updated_at: list[str]`
    :   The last update time of the note in ISO 8601 format.

<a id="NotesKeywordCondition"></a>

`NotesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.granola.types.NotesStringFilter`
    :   The type of the None singleton.

<a id="NotesLikeCondition"></a>

`NotesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.granola.types.NotesStringFilter`
    :   The type of the None singleton.

<a id="NotesListParams"></a>

`NotesListParams(*args, **kwargs)`
:   Parameters for notes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_after: str`
    :   The type of the None singleton.

    `created_before: str`
    :   The type of the None singleton.

    `cursor: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="NotesLtCondition"></a>

`NotesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.granola.types.NotesSearchFilter`
    :   The type of the None singleton.

<a id="NotesLteCondition"></a>

`NotesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.granola.types.NotesSearchFilter`
    :   The type of the None singleton.

<a id="NotesNeqCondition"></a>

`NotesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.granola.types.NotesSearchFilter`
    :   The type of the None singleton.

<a id="NotesNotCondition"></a>

`NotesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.granola.types.NotesEqCondition | airbyte_agent_sdk.connectors.granola.types.NotesNeqCondition | airbyte_agent_sdk.connectors.granola.types.NotesGtCondition | airbyte_agent_sdk.connectors.granola.types.NotesGteCondition | airbyte_agent_sdk.connectors.granola.types.NotesLtCondition | airbyte_agent_sdk.connectors.granola.types.NotesLteCondition | airbyte_agent_sdk.connectors.granola.types.NotesInCondition | airbyte_agent_sdk.connectors.granola.types.NotesLikeCondition | airbyte_agent_sdk.connectors.granola.types.NotesFuzzyCondition | airbyte_agent_sdk.connectors.granola.types.NotesKeywordCondition | airbyte_agent_sdk.connectors.granola.types.NotesContainsCondition | airbyte_agent_sdk.connectors.granola.types.NotesNotCondition | airbyte_agent_sdk.connectors.granola.types.NotesAndCondition | airbyte_agent_sdk.connectors.granola.types.NotesOrCondition | airbyte_agent_sdk.connectors.granola.types.NotesAnyCondition`
    :   The type of the None singleton.

<a id="NotesOrCondition"></a>

`NotesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.granola.types.NotesEqCondition | airbyte_agent_sdk.connectors.granola.types.NotesNeqCondition | airbyte_agent_sdk.connectors.granola.types.NotesGtCondition | airbyte_agent_sdk.connectors.granola.types.NotesGteCondition | airbyte_agent_sdk.connectors.granola.types.NotesLtCondition | airbyte_agent_sdk.connectors.granola.types.NotesLteCondition | airbyte_agent_sdk.connectors.granola.types.NotesInCondition | airbyte_agent_sdk.connectors.granola.types.NotesLikeCondition | airbyte_agent_sdk.connectors.granola.types.NotesFuzzyCondition | airbyte_agent_sdk.connectors.granola.types.NotesKeywordCondition | airbyte_agent_sdk.connectors.granola.types.NotesContainsCondition | airbyte_agent_sdk.connectors.granola.types.NotesNotCondition | airbyte_agent_sdk.connectors.granola.types.NotesAndCondition | airbyte_agent_sdk.connectors.granola.types.NotesOrCondition | airbyte_agent_sdk.connectors.granola.types.NotesAnyCondition]`
    :   The type of the None singleton.

<a id="NotesSearchFilter"></a>

`NotesSearchFilter(*args, **kwargs)`
:   Available fields for filtering notes search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attendees: list[typing.Any] | None`
    :   The attendees of the meeting.

    `calendar_event: dict[str, typing.Any] | None`
    :   Associated calendar event details.

    `created_at: str | None`
    :   The creation time of the note in ISO 8601 format.

    `folder_membership: list[typing.Any] | None`
    :   The folder membership of the note.

    `id: str | None`
    :   The unique identifier of the note.

    `object_: str | None`
    :   The object type, always "note".

    `owner: dict[str, typing.Any] | None`
    :   The owner of the note.

    `summary_markdown: str | None`
    :   Markdown formatted summary of the note.

    `summary_text: str | None`
    :   Plain text summary of the note.

    `title: str | None`
    :   The title of the note.

    `transcript: list[typing.Any] | None`
    :   Transcript of the meeting.

    `updated_at: str | None`
    :   The last update time of the note in ISO 8601 format.

<a id="NotesSearchQuery"></a>

`NotesSearchQuery(*args, **kwargs)`
:   Search query for notes entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.granola.types.NotesEqCondition | airbyte_agent_sdk.connectors.granola.types.NotesNeqCondition | airbyte_agent_sdk.connectors.granola.types.NotesGtCondition | airbyte_agent_sdk.connectors.granola.types.NotesGteCondition | airbyte_agent_sdk.connectors.granola.types.NotesLtCondition | airbyte_agent_sdk.connectors.granola.types.NotesLteCondition | airbyte_agent_sdk.connectors.granola.types.NotesInCondition | airbyte_agent_sdk.connectors.granola.types.NotesLikeCondition | airbyte_agent_sdk.connectors.granola.types.NotesFuzzyCondition | airbyte_agent_sdk.connectors.granola.types.NotesKeywordCondition | airbyte_agent_sdk.connectors.granola.types.NotesContainsCondition | airbyte_agent_sdk.connectors.granola.types.NotesNotCondition | airbyte_agent_sdk.connectors.granola.types.NotesAndCondition | airbyte_agent_sdk.connectors.granola.types.NotesOrCondition | airbyte_agent_sdk.connectors.granola.types.NotesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.granola.types.NotesSortFilter]`
    :   The type of the None singleton.

<a id="NotesSortFilter"></a>

`NotesSortFilter(*args, **kwargs)`
:   Available fields for sorting notes search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attendees: Literal['asc', 'desc']`
    :   The attendees of the meeting.

    `calendar_event: Literal['asc', 'desc']`
    :   Associated calendar event details.

    `created_at: Literal['asc', 'desc']`
    :   The creation time of the note in ISO 8601 format.

    `folder_membership: Literal['asc', 'desc']`
    :   The folder membership of the note.

    `id: Literal['asc', 'desc']`
    :   The unique identifier of the note.

    `object_: Literal['asc', 'desc']`
    :   The object type, always "note".

    `owner: Literal['asc', 'desc']`
    :   The owner of the note.

    `summary_markdown: Literal['asc', 'desc']`
    :   Markdown formatted summary of the note.

    `summary_text: Literal['asc', 'desc']`
    :   Plain text summary of the note.

    `title: Literal['asc', 'desc']`
    :   The title of the note.

    `transcript: Literal['asc', 'desc']`
    :   Transcript of the meeting.

    `updated_at: Literal['asc', 'desc']`
    :   The last update time of the note in ISO 8601 format.

<a id="NotesStringFilter"></a>

`NotesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attendees: str`
    :   The attendees of the meeting.

    `calendar_event: str`
    :   Associated calendar event details.

    `created_at: str`
    :   The creation time of the note in ISO 8601 format.

    `folder_membership: str`
    :   The folder membership of the note.

    `id: str`
    :   The unique identifier of the note.

    `object_: str`
    :   The object type, always "note".

    `owner: str`
    :   The owner of the note.

    `summary_markdown: str`
    :   Markdown formatted summary of the note.

    `summary_text: str`
    :   Plain text summary of the note.

    `title: str`
    :   The title of the note.

    `transcript: str`
    :   Transcript of the meeting.

    `updated_at: str`
    :   The last update time of the note in ISO 8601 format.