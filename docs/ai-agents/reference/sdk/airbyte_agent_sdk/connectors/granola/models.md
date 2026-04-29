---
id: airbyte_agent_sdk-connectors-granola-models
title: airbyte_agent_sdk.connectors.granola.models
---

Module airbyte_agent_sdk.connectors.granola.models
==================================================
Pydantic models for granola connector.

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

    * airbyte_agent_sdk.connectors.granola.models.AirbyteSearchResult[NotesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.granola.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[NotesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.granola.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="NotesSearchResult"></a>

`NotesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.granola.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Attendee"></a>

`Attendee(**data: Any)`
:   A meeting attendee
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

<a id="CalendarEvent"></a>

`CalendarEvent(**data: Any)`
:   Associated calendar event details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `calendar_event_id: str | Any | None`
    :   The type of the None singleton.

    `event_title: str | Any | None`
    :   The type of the None singleton.

    `invitees: list[airbyte_agent_sdk.connectors.granola.models.CalendarEventInvitee] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organiser: str | Any | None`
    :   The type of the None singleton.

    `scheduled_end_time: str | Any | None`
    :   The type of the None singleton.

    `scheduled_start_time: str | Any | None`
    :   The type of the None singleton.

<a id="CalendarEventInvitee"></a>

`CalendarEventInvitee(**data: Any)`
:   A calendar event invitee
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FolderMembership"></a>

`FolderMembership(**data: Any)`
:   Folder the note belongs to
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

<a id="GranolaAuthConfig"></a>

`GranolaAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Granola Enterprise API key generated from Settings > Workspaces > API tab

    `model_config`
    :   The type of the None singleton.

<a id="GranolaCheckResult"></a>

`GranolaCheckResult(**data: Any)`
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

<a id="GranolaExecuteResult"></a>

`GranolaExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.granola.models.GranolaExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="GranolaExecuteResultWithMeta"></a>

`GranolaExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.granola.models.GranolaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.granola.models.GranolaExecuteResultWithMeta[list[Note], NotesListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`GranolaExecuteResultWithMeta[list[Note], NotesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.granola.models.GranolaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.granola.models.GranolaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="NotesListResult"></a>

`NotesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.granola.models.GranolaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.granola.models.GranolaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Note"></a>

`Note(**data: Any)`
:   A Granola meeting note
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attendees: list[airbyte_agent_sdk.connectors.granola.models.Attendee] | Any | None`
    :   The type of the None singleton.

    `calendar_event: Any`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `folder_membership: list[airbyte_agent_sdk.connectors.granola.models.FolderMembership] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

    `owner: Any`
    :   The type of the None singleton.

    `summary_markdown: str | Any | None`
    :   The type of the None singleton.

    `summary_text: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `transcript: list[airbyte_agent_sdk.connectors.granola.models.TranscriptEntry] | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

<a id="NotesList"></a>

`NotesList(**data: Any)`
:   Paginated list of notes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `notes: list[airbyte_agent_sdk.connectors.granola.models.Note] | Any`
    :   The type of the None singleton.

<a id="NotesListResultMeta"></a>

`NotesListResultMeta(**data: Any)`
:   Metadata for notes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="NotesSearchData"></a>

`NotesSearchData(**data: Any)`
:   Search result data for notes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="Owner"></a>

`Owner(**data: Any)`
:   The owner of the note
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

<a id="TranscriptEntry"></a>

`TranscriptEntry(**data: Any)`
:   A single transcript entry
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_time: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `speaker: Any`
    :   The type of the None singleton.

    `start_time: str | Any | None`
    :   The type of the None singleton.

    `text: str | Any | None`
    :   The type of the None singleton.

<a id="TranscriptSpeaker"></a>

`TranscriptSpeaker(**data: Any)`
:   Speaker information in transcript
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `source: str | Any | None`
    :   The type of the None singleton.