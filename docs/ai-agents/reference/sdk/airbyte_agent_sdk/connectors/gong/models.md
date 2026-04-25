---
id: airbyte_agent_sdk-connectors-gong-models
title: airbyte_agent_sdk.connectors.gong.models
---

Module airbyte_agent_sdk.connectors.gong.models
===============================================
Pydantic models for gong connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="ActivityAggregateResponse"></a>

`ActivityAggregateResponse(**data: Any)`
:   Response containing aggregated activity statistics
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `from_date_time: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `records: airbyte_agent_sdk.connectors.gong.models.PaginationRecords | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

    `time_zone: str | Any`
    :   The type of the None singleton.

    `to_date_time: str | Any`
    :   The type of the None singleton.

    `users_aggregate_activity_stats: list[airbyte_agent_sdk.connectors.gong.models.UserAggregateActivity] | Any`
    :   The type of the None singleton.

<a id="ActivityDayByDayResponse"></a>

`ActivityDayByDayResponse(**data: Any)`
:   Response containing daily activity statistics
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `records: airbyte_agent_sdk.connectors.gong.models.PaginationRecords | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

    `users_detailed_activities: list[airbyte_agent_sdk.connectors.gong.models.UserDetailedActivity] | Any`
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

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[CallsExtensiveSearchData]
    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[CallsSearchData]
    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[SettingsScorecardsSearchData]
    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[StatsActivityScorecardsSearchData]
    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.gong.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[CallsExtensiveSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CallsExtensiveSearchResult"></a>

`CallsExtensiveSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CallsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SettingsScorecardsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SettingsScorecardsSearchResult"></a>

`SettingsScorecardsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[StatsActivityScorecardsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="StatsActivityScorecardsSearchResult"></a>

`StatsActivityScorecardsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AnsweredScorecard"></a>

`AnsweredScorecard(**data: Any)`
:   A completed scorecard
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answered_date_time: str | Any`
    :   The type of the None singleton.

    `answered_scorecard_id: str | Any`
    :   The type of the None singleton.

    `answers: list[airbyte_agent_sdk.connectors.gong.models.AnsweredScorecardAnswer] | Any`
    :   The type of the None singleton.

    `call_id: str | Any`
    :   The type of the None singleton.

    `call_start_time: str | Any`
    :   The type of the None singleton.

    `editor_user_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `overall_score: float | Any`
    :   The type of the None singleton.

    `review_method: str | Any`
    :   The type of the None singleton.

    `review_time: str | Any`
    :   The type of the None singleton.

    `reviewed_user_id: str | Any`
    :   The type of the None singleton.

    `reviewer_user_id: str | Any`
    :   The type of the None singleton.

    `scorecard_id: str | Any`
    :   The type of the None singleton.

    `scorecard_name: str | Any`
    :   The type of the None singleton.

    `visibility: str | Any`
    :   The type of the None singleton.

    `visibility_type: str | Any`
    :   The type of the None singleton.

<a id="AnsweredScorecardAnswer"></a>

`AnsweredScorecardAnswer(**data: Any)`
:   An answer to a scorecard question
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answer: str | Any`
    :   The type of the None singleton.

    `answer_text: str | Any | None`
    :   The type of the None singleton.

    `is_overall: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `not_applicable: bool | Any`
    :   The type of the None singleton.

    `question_id: str | Any`
    :   The type of the None singleton.

    `question_revision_id: str | Any`
    :   The type of the None singleton.

    `score: float | Any`
    :   The type of the None singleton.

    `selected_options: list[str] | Any | None`
    :   The type of the None singleton.

<a id="AnsweredScorecardsResponse"></a>

`AnsweredScorecardsResponse(**data: Any)`
:   Response containing answered scorecards
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answered_scorecards: list[airbyte_agent_sdk.connectors.gong.models.AnsweredScorecard] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `records: airbyte_agent_sdk.connectors.gong.models.PaginationRecords | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

<a id="Call"></a>

`Call(**data: Any)`
:   Call object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `calendar_event_id: str | Any | None`
    :   The type of the None singleton.

    `client_unique_id: str | Any | None`
    :   The type of the None singleton.

    `custom_data: str | Any | None`
    :   The type of the None singleton.

    `direction: str | Any`
    :   The type of the None singleton.

    `duration: int | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_private: bool | Any`
    :   The type of the None singleton.

    `language: str | Any`
    :   The type of the None singleton.

    `media: str | Any`
    :   The type of the None singleton.

    `meeting_url: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `primary_user_id: str | Any`
    :   The type of the None singleton.

    `purpose: str | Any | None`
    :   The type of the None singleton.

    `scheduled: str | Any`
    :   The type of the None singleton.

    `scope: str | Any`
    :   The type of the None singleton.

    `sdr_disposition: str | Any | None`
    :   The type of the None singleton.

    `started: str | Any`
    :   The type of the None singleton.

    `system: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

    `workspace_id: str | Any`
    :   The type of the None singleton.

<a id="CallResponse"></a>

`CallResponse(**data: Any)`
:   Response containing single call
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `call: airbyte_agent_sdk.connectors.gong.models.Call | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

<a id="CallTranscript"></a>

`CallTranscript(**data: Any)`
:   Call transcript object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `call_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `transcript: list[airbyte_agent_sdk.connectors.gong.models.CallTranscriptTranscriptItem] | Any`
    :   The type of the None singleton.

<a id="CallTranscriptTranscriptItem"></a>

`CallTranscriptTranscriptItem(**data: Any)`
:   Nested schema for CallTranscript.transcript_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `sentences: list[airbyte_agent_sdk.connectors.gong.models.CallTranscriptTranscriptItemSentencesItem] | Any`
    :   The type of the None singleton.

    `speaker_id: str | Any`
    :   Speaker identifier

    `topic: str | Any | None`
    :   Topic

<a id="CallTranscriptTranscriptItemSentencesItem"></a>

`CallTranscriptTranscriptItemSentencesItem(**data: Any)`
:   Nested schema for CallTranscriptTranscriptItem.sentences_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end: int | Any`
    :   End time in seconds

    `model_config`
    :   The type of the None singleton.

    `start: int | Any`
    :   Start time in seconds

    `text: str | Any`
    :   Sentence text

<a id="CallTranscriptsListResultMeta"></a>

`CallTranscriptsListResultMeta(**data: Any)`
:   Metadata for call_transcripts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `current_page_number: int | Any`
    :   The type of the None singleton.

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_records: int | Any`
    :   The type of the None singleton.

<a id="CallsExtensiveListResultMeta"></a>

`CallsExtensiveListResultMeta(**data: Any)`
:   Metadata for calls_extensive.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `current_page_number: int | Any`
    :   The type of the None singleton.

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_records: int | Any`
    :   The type of the None singleton.

<a id="CallsExtensiveSearchData"></a>

`CallsExtensiveSearchData(**data: Any)`
:   Search result data for calls_extensive entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `collaboration: dict[str, typing.Any] | None`
    :   Collaboration information added to the call

    `content: dict[str, typing.Any] | None`
    :   Analysis of the interaction content.

    `context: dict[str, typing.Any] | None`
    :   A list of the agenda of each part of the call.

    `id: int | None`
    :   Unique identifier for the call (from metaData.id).

    `interaction: dict[str, typing.Any] | None`
    :   Metrics collected around the interaction during the call.

    `media: dict[str, typing.Any] | None`
    :   The media urls of the call.

    `meta_data: dict[str, typing.Any] | None`
    :   call's metadata.

    `model_config`
    :   The type of the None singleton.

    `parties: list[typing.Any] | None`
    :   A list of the call's participants

    `startdatetime: str | None`
    :   Datetime for extensive calls.

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

    `current_page_number: int | Any`
    :   The type of the None singleton.

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_records: int | Any`
    :   The type of the None singleton.

<a id="CallsResponse"></a>

`CallsResponse(**data: Any)`
:   Response containing list of calls
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `calls: list[airbyte_agent_sdk.connectors.gong.models.Call] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `records: airbyte_agent_sdk.connectors.gong.models.PaginationRecords | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `calendar_event_id: str | None`
    :   Unique identifier for the calendar event associated with the call.

    `client_unique_id: str | None`
    :   Unique identifier for the client related to the call.

    `custom_data: str | None`
    :   Custom data associated with the call.

    `direction: str | None`
    :   Direction of the call (inbound/outbound).

    `duration: int | None`
    :   Duration of the call in seconds.

    `id: str | None`
    :   Unique identifier for the call.

    `is_private: bool | None`
    :   Indicates if the call is private or not.

    `language: str | None`
    :   Language used in the call.

    `media: str | None`
    :   Media type used for communication (voice, video, etc.).

    `meeting_url: str | None`
    :   URL for accessing the meeting associated with the call.

    `model_config`
    :   The type of the None singleton.

    `primary_user_id: str | None`
    :   Unique identifier for the primary user involved in the call.

    `purpose: str | None`
    :   Purpose or topic of the call.

    `scheduled: str | None`
    :   Scheduled date and time of the call.

    `scope: str | None`
    :   Scope or extent of the call.

    `sdr_disposition: str | None`
    :   Disposition set by the sales development representative.

    `started: str | None`
    :   Start date and time of the call.

    `system: str | None`
    :   System information related to the call.

    `title: str | None`
    :   Title or headline of the call.

    `url: str | None`
    :   URL associated with the call.

    `workspace_id: str | None`
    :   Identifier for the workspace to which the call belongs.

<a id="CoachingData"></a>

`CoachingData(**data: Any)`
:   Coaching data for a user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `coaching_metrics: airbyte_agent_sdk.connectors.gong.models.CoachingMetrics | Any`
    :   The type of the None singleton.

    `is_manager: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_email_address: str | Any`
    :   The type of the None singleton.

    `user_id: str | Any`
    :   The type of the None singleton.

    `user_name: str | Any`
    :   The type of the None singleton.

<a id="CoachingMetrics"></a>

`CoachingMetrics(**data: Any)`
:   Coaching metrics for a user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `calls_attended: int | Any`
    :   The type of the None singleton.

    `calls_listened: int | Any`
    :   The type of the None singleton.

    `calls_with_comments: int | Any`
    :   The type of the None singleton.

    `calls_with_feedback: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `scorecards_filled: int | Any`
    :   The type of the None singleton.

<a id="CoachingResponse"></a>

`CoachingResponse(**data: Any)`
:   Response containing coaching metrics
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `coaching_data: list[airbyte_agent_sdk.connectors.gong.models.CoachingData] | Any`
    :   The type of the None singleton.

    `from_date_time: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

    `to_date_time: str | Any`
    :   The type of the None singleton.

<a id="DailyActivityStats"></a>

`DailyActivityStats(**data: Any)`
:   Daily activity statistics with call IDs
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `calls_as_host: list[str] | Any`
    :   The type of the None singleton.

    `calls_attended: list[str] | Any`
    :   The type of the None singleton.

    `calls_comments_given: list[str] | Any`
    :   The type of the None singleton.

    `calls_comments_received: list[str] | Any`
    :   The type of the None singleton.

    `calls_gave_feedback: list[str] | Any`
    :   The type of the None singleton.

    `calls_marked_as_feedback_given: list[str] | Any`
    :   The type of the None singleton.

    `calls_marked_as_feedback_received: list[str] | Any`
    :   The type of the None singleton.

    `calls_received_feedback: list[str] | Any`
    :   The type of the None singleton.

    `calls_requested_feedback: list[str] | Any`
    :   The type of the None singleton.

    `calls_scorecards_filled: list[str] | Any`
    :   The type of the None singleton.

    `calls_scorecards_received: list[str] | Any`
    :   The type of the None singleton.

    `calls_shared_externally: list[str] | Any`
    :   The type of the None singleton.

    `calls_shared_internally: list[str] | Any`
    :   The type of the None singleton.

    `from_date: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `others_calls_listened_to: list[str] | Any`
    :   The type of the None singleton.

    `own_calls_listened_to: list[str] | Any`
    :   The type of the None singleton.

    `to_date: str | Any`
    :   The type of the None singleton.

<a id="ExtensiveCall"></a>

`ExtensiveCall(**data: Any)`
:   Detailed call object with extended information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `collaboration: airbyte_agent_sdk.connectors.gong.models.ExtensiveCallCollaboration | Any`
    :   The type of the None singleton.

    `content: airbyte_agent_sdk.connectors.gong.models.ExtensiveCallContent | Any`
    :   The type of the None singleton.

    `interaction: airbyte_agent_sdk.connectors.gong.models.ExtensiveCallInteraction | Any`
    :   The type of the None singleton.

    `media: airbyte_agent_sdk.connectors.gong.models.ExtensiveCallMedia | Any`
    :   The type of the None singleton.

    `meta_data: airbyte_agent_sdk.connectors.gong.models.ExtensiveCallMetadata | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `parties: list[airbyte_agent_sdk.connectors.gong.models.ExtensiveCallPartiesItem] | Any`
    :   The type of the None singleton.

<a id="ExtensiveCallCollaboration"></a>

`ExtensiveCallCollaboration(**data: Any)`
:   Collaboration data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `public_comments: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

<a id="ExtensiveCallContent"></a>

`ExtensiveCallContent(**data: Any)`
:   Content data including topics and trackers
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `points_of_interest: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `topics: list[airbyte_agent_sdk.connectors.gong.models.ExtensiveCallContentTopicsItem] | Any`
    :   The type of the None singleton.

    `trackers: list[airbyte_agent_sdk.connectors.gong.models.ExtensiveCallContentTrackersItem] | Any`
    :   The type of the None singleton.

<a id="ExtensiveCallContentTopicsItem"></a>

`ExtensiveCallContentTopicsItem(**data: Any)`
:   Nested schema for ExtensiveCallContent.topics_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `duration: float | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="ExtensiveCallContentTrackersItem"></a>

`ExtensiveCallContentTrackersItem(**data: Any)`
:   Nested schema for ExtensiveCallContent.trackers_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `occurrences: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="ExtensiveCallInteraction"></a>

`ExtensiveCallInteraction(**data: Any)`
:   Interaction statistics
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `interaction_stats: list[airbyte_agent_sdk.connectors.gong.models.ExtensiveCallInteractionInteractionstatsItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `questions: airbyte_agent_sdk.connectors.gong.models.ExtensiveCallInteractionQuestions | Any`
    :   The type of the None singleton.

<a id="ExtensiveCallInteractionInteractionstatsItem"></a>

`ExtensiveCallInteractionInteractionstatsItem(**data: Any)`
:   Nested schema for ExtensiveCallInteraction.interactionStats_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Stat name

    `value: float | Any`
    :   Stat value

<a id="ExtensiveCallInteractionQuestions"></a>

`ExtensiveCallInteractionQuestions(**data: Any)`
:   Nested schema for ExtensiveCallInteraction.questions
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `company_count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `non_company_count: int | Any`
    :   The type of the None singleton.

<a id="ExtensiveCallMedia"></a>

`ExtensiveCallMedia(**data: Any)`
:   Media URLs
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `audio_url: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `video_url: str | Any`
    :   The type of the None singleton.

<a id="ExtensiveCallMetadata"></a>

`ExtensiveCallMetadata(**data: Any)`
:   Call metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `calendar_event_id: str | Any | None`
    :   Calendar event ID

    `client_unique_id: str | Any | None`
    :   Client unique identifier

    `custom_data: str | Any | None`
    :   Custom data

    `direction: str | Any`
    :   Call direction

    `duration: int | Any`
    :   Call duration in seconds

    `id: str | Any`
    :   Unique call identifier

    `is_private: bool | Any`
    :   Whether call is private

    `language: str | Any`
    :   Call language

    `media: str | Any`
    :   Media type (Audio/Video)

    `meeting_url: str | Any`
    :   Meeting URL

    `model_config`
    :   The type of the None singleton.

    `primary_user_id: str | Any`
    :   Primary user ID

    `purpose: str | Any | None`
    :   Call purpose

    `scheduled: str | Any`
    :   Scheduled time

    `scope: str | Any`
    :   Call scope

    `sdr_disposition: str | Any | None`
    :   SDR disposition

    `started: str | Any`
    :   Call start time

    `system: str | Any`
    :   System type

    `title: str | Any`
    :   Call title

    `url: str | Any`
    :   URL to call in Gong

    `workspace_id: str | Any`
    :   Workspace ID

<a id="ExtensiveCallPartiesItem"></a>

`ExtensiveCallPartiesItem(**data: Any)`
:   Nested schema for ExtensiveCall.parties_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `affiliation: str | Any`
    :   Internal or External

    `context: list[airbyte_agent_sdk.connectors.gong.models.ExtensiveCallPartiesItemContextItem] | Any`
    :   CRM context data linked to this participant

    `email_address: str | Any`
    :   Email address

    `id: str | Any`
    :   Party ID

    `methods: list[str] | Any`
    :   Contact methods

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Full name

    `phone_number: str | Any`
    :   Phone number

    `speaker_id: str | Any | None`
    :   Speaker ID for transcript matching

    `title: str | Any`
    :   Job title

    `user_id: str | Any`
    :   Gong user ID if internal

<a id="ExtensiveCallPartiesItemContextItem"></a>

`ExtensiveCallPartiesItemContextItem(**data: Any)`
:   Nested schema for ExtensiveCallPartiesItem.context_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `objects: list[airbyte_agent_sdk.connectors.gong.models.ExtensiveCallPartiesItemContextItemObjectsItem] | Any`
    :   CRM objects linked to this participant

    `system: str | Any`
    :   CRM system name (e.g., Salesforce, HubSpot)

<a id="ExtensiveCallPartiesItemContextItemObjectsItem"></a>

`ExtensiveCallPartiesItemContextItemObjectsItem(**data: Any)`
:   Nested schema for ExtensiveCallPartiesItemContextItem.objects_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `fields: list[airbyte_agent_sdk.connectors.gong.models.ExtensiveCallPartiesItemContextItemObjectsItemFieldsItem] | Any`
    :   CRM field values

    `model_config`
    :   The type of the None singleton.

    `object_id: str | Any`
    :   CRM record ID

    `object_type: str | Any`
    :   CRM object type (Account, Contact, Opportunity, Lead)

<a id="ExtensiveCallPartiesItemContextItemObjectsItemFieldsItem"></a>

`ExtensiveCallPartiesItemContextItemObjectsItemFieldsItem(**data: Any)`
:   Nested schema for ExtensiveCallPartiesItemContextItemObjectsItem.fields_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Field name

    `value: Any`
    :   Field value

<a id="ExtensiveCallsResponse"></a>

`ExtensiveCallsResponse(**data: Any)`
:   Response containing detailed call data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `calls: list[airbyte_agent_sdk.connectors.gong.models.ExtensiveCall] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `records: airbyte_agent_sdk.connectors.gong.models.PaginationRecords | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

<a id="FolderCall"></a>

`FolderCall(**data: Any)`
:   Call within a library folder
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `call_id: str | Any`
    :   The type of the None singleton.

    `duration: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `primary_user_id: str | Any`
    :   The type of the None singleton.

    `started: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="FolderContentResponse"></a>

`FolderContentResponse(**data: Any)`
:   Response containing calls in a folder
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `calls: list[airbyte_agent_sdk.connectors.gong.models.FolderCall] | Any`
    :   The type of the None singleton.

    `created_by: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `records: airbyte_agent_sdk.connectors.gong.models.PaginationRecords | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

    `updated: str | Any`
    :   The type of the None singleton.

<a id="GongAccessKeyAuthenticationAuthConfig"></a>

`GongAccessKeyAuthenticationAuthConfig(**data: Any)`
:   Access Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_key: str`
    :   Your Gong API Access Key

    `access_key_secret: str`
    :   Your Gong API Access Key Secret

    `model_config`
    :   The type of the None singleton.

<a id="GongCheckResult"></a>

`GongCheckResult(**data: Any)`
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

<a id="GongExecuteResult"></a>

`GongExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult[list[CoachingData]]
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult[list[LibraryFolder]]
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult[list[Scorecard]]
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult[list[Tracker]]
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult[list[Workspace]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="GongExecuteResultWithMeta"></a>

`GongExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[AnsweredScorecard], StatsActivityScorecardsListResultMeta]
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[CallTranscript], CallTranscriptsListResultMeta]
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[Call], CallsListResultMeta]
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[ExtensiveCall], CallsExtensiveListResultMeta]
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[FolderCall], LibraryFolderContentListResultMeta]
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[UserAggregateActivity], StatsActivityAggregateListResultMeta]
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[UserDetailedActivity], StatsActivityDayByDayListResultMeta]
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[UserInteractionStats], StatsInteractionListResultMeta]
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[User], UsersListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`GongExecuteResultWithMeta[list[AnsweredScorecard], StatsActivityScorecardsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="StatsActivityScorecardsListResult"></a>

`StatsActivityScorecardsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GongExecuteResultWithMeta[list[CallTranscript], CallTranscriptsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CallTranscriptsListResult"></a>

`CallTranscriptsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GongExecuteResultWithMeta[list[Call], CallsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
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

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GongExecuteResultWithMeta[list[ExtensiveCall], CallsExtensiveListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CallsExtensiveListResult"></a>

`CallsExtensiveListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GongExecuteResultWithMeta[list[FolderCall], LibraryFolderContentListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="LibraryFolderContentListResult"></a>

`LibraryFolderContentListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GongExecuteResultWithMeta[list[UserAggregateActivity], StatsActivityAggregateListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="StatsActivityAggregateListResult"></a>

`StatsActivityAggregateListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GongExecuteResultWithMeta[list[UserDetailedActivity], StatsActivityDayByDayListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="StatsActivityDayByDayListResult"></a>

`StatsActivityDayByDayListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GongExecuteResultWithMeta[list[UserInteractionStats], StatsInteractionListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="StatsInteractionListResult"></a>

`StatsInteractionListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GongExecuteResultWithMeta[list[User], UsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
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

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GongExecuteResult[list[CoachingData]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CoachingListResult"></a>

`CoachingListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GongExecuteResult[list[LibraryFolder]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="LibraryFoldersListResult"></a>

`LibraryFoldersListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GongExecuteResult[list[Scorecard]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SettingsScorecardsListResult"></a>

`SettingsScorecardsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GongExecuteResult[list[Tracker]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SettingsTrackersListResult"></a>

`SettingsTrackersListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GongExecuteResult[list[Workspace]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WorkspacesListResult"></a>

`WorkspacesListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.GongExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GongOauth20AuthenticationAuthConfig"></a>

`GongOauth20AuthenticationAuthConfig(**data: Any)`
:   OAuth 2.0 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str | None`
    :   Your Gong OAuth2 Access Token.

    `client_id: str | None`
    :   Your Gong OAuth App Client ID.

    `client_secret: str | None`
    :   Your Gong OAuth App Client Secret.

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   Your Gong OAuth2 Refresh Token. Note: Gong uses single-use refresh tokens.

<a id="InteractionStatsResponse"></a>

`InteractionStatsResponse(**data: Any)`
:   Response containing interaction statistics
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `from_date_time: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `people_interaction_stats: list[airbyte_agent_sdk.connectors.gong.models.UserInteractionStats] | Any`
    :   The type of the None singleton.

    `records: airbyte_agent_sdk.connectors.gong.models.PaginationRecords | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

    `time_zone: str | Any`
    :   The type of the None singleton.

    `to_date_time: str | Any`
    :   The type of the None singleton.

<a id="LibraryFolder"></a>

`LibraryFolder(**data: Any)`
:   Library folder structure
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_by: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `parent_folder_id: str | Any | None`
    :   The type of the None singleton.

    `updated: str | Any`
    :   The type of the None singleton.

<a id="LibraryFolderContentListResultMeta"></a>

`LibraryFolderContentListResultMeta(**data: Any)`
:   Metadata for library_folder_content.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `current_page_number: int | Any`
    :   The type of the None singleton.

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_records: int | Any`
    :   The type of the None singleton.

<a id="LibraryFoldersResponse"></a>

`LibraryFoldersResponse(**data: Any)`
:   Response containing library folder structure
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `folders: list[airbyte_agent_sdk.connectors.gong.models.LibraryFolder] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

<a id="PaginationRecords"></a>

`PaginationRecords(**data: Any)`
:   Pagination metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `current_page_number: int | Any`
    :   The type of the None singleton.

    `current_page_size: int | Any`
    :   The type of the None singleton.

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_records: int | Any`
    :   The type of the None singleton.

<a id="PersonInteractionStat"></a>

`PersonInteractionStat(**data: Any)`
:   Individual interaction statistic
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `value: float | Any`
    :   The type of the None singleton.

<a id="Scorecard"></a>

`Scorecard(**data: Any)`
:   Scorecard configuration
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: str | Any`
    :   The type of the None singleton.

    `enabled: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `questions: list[airbyte_agent_sdk.connectors.gong.models.ScorecardQuestion] | Any`
    :   The type of the None singleton.

    `review_method: str | Any`
    :   The type of the None singleton.

    `scorecard_id: str | Any`
    :   The type of the None singleton.

    `scorecard_name: str | Any`
    :   The type of the None singleton.

    `updated: str | Any`
    :   The type of the None singleton.

    `updater_user_id: str | Any`
    :   The type of the None singleton.

    `workspace_id: str | Any | None`
    :   The type of the None singleton.

<a id="ScorecardQuestion"></a>

`ScorecardQuestion(**data: Any)`
:   A question within a scorecard
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answer_guide: str | Any | None`
    :   The type of the None singleton.

    `answer_options: list[airbyte_agent_sdk.connectors.gong.models.ScorecardQuestionAnsweroptionsItem] | Any`
    :   The type of the None singleton.

    `created: str | Any`
    :   The type of the None singleton.

    `is_overall: bool | Any`
    :   The type of the None singleton.

    `is_required: bool | Any`
    :   The type of the None singleton.

    `max_range: str | Any | None`
    :   The type of the None singleton.

    `min_range: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `question_id: str | Any`
    :   The type of the None singleton.

    `question_revision_id: str | Any`
    :   The type of the None singleton.

    `question_text: str | Any`
    :   The type of the None singleton.

    `question_type: str | Any`
    :   The type of the None singleton.

    `updated: str | Any`
    :   The type of the None singleton.

    `updater_user_id: str | Any`
    :   The type of the None singleton.

<a id="ScorecardQuestionAnsweroptionsItem"></a>

`ScorecardQuestionAnsweroptionsItem(**data: Any)`
:   Nested schema for ScorecardQuestion.answerOptions_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `option_id: str | Any`
    :   The type of the None singleton.

    `option_text: str | Any`
    :   The type of the None singleton.

    `score: float | Any`
    :   The type of the None singleton.

<a id="ScorecardsResponse"></a>

`ScorecardsResponse(**data: Any)`
:   Response containing list of scorecards
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

    `scorecards: list[airbyte_agent_sdk.connectors.gong.models.Scorecard] | Any`
    :   The type of the None singleton.

<a id="SettingsScorecardsSearchData"></a>

`SettingsScorecardsSearchData(**data: Any)`
:   Search result data for settings_scorecards entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: str | None`
    :   The timestamp when the scorecard was created

    `enabled: bool | None`
    :   Indicates if the scorecard is enabled or disabled

    `model_config`
    :   The type of the None singleton.

    `questions: list[typing.Any] | None`
    :   An array of questions related to the scorecard

    `scorecard_id: str | None`
    :   The unique identifier of the scorecard

    `scorecard_name: str | None`
    :   The name of the scorecard

    `updated: str | None`
    :   The timestamp when the scorecard was last updated

    `updater_user_id: str | None`
    :   The user ID of the person who last updated the scorecard

    `workspace_id: str | None`
    :   The unique identifier of the workspace associated with the scorecard

<a id="StatsActivityAggregateListResultMeta"></a>

`StatsActivityAggregateListResultMeta(**data: Any)`
:   Metadata for stats_activity_aggregate.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `current_page_number: int | Any`
    :   The type of the None singleton.

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_records: int | Any`
    :   The type of the None singleton.

<a id="StatsActivityDayByDayListResultMeta"></a>

`StatsActivityDayByDayListResultMeta(**data: Any)`
:   Metadata for stats_activity_day_by_day.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `current_page_number: int | Any`
    :   The type of the None singleton.

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_records: int | Any`
    :   The type of the None singleton.

<a id="StatsActivityScorecardsListResultMeta"></a>

`StatsActivityScorecardsListResultMeta(**data: Any)`
:   Metadata for stats_activity_scorecards.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `current_page_number: int | Any`
    :   The type of the None singleton.

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_records: int | Any`
    :   The type of the None singleton.

<a id="StatsActivityScorecardsSearchData"></a>

`StatsActivityScorecardsSearchData(**data: Any)`
:   Search result data for stats_activity_scorecards entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answered_scorecard_id: str | None`
    :   Unique identifier for the answered scorecard instance.

    `answers: list[typing.Any] | None`
    :   Contains the answered questions in the scorecards

    `call_id: str | None`
    :   Unique identifier for the call associated with the answered scorecard.

    `call_start_time: str | None`
    :   Timestamp indicating the start time of the call.

    `model_config`
    :   The type of the None singleton.

    `review_time: str | None`
    :   Timestamp indicating when the review of the answered scorecard was completed.

    `reviewed_user_id: str | None`
    :   Unique identifier for the user whose performance was reviewed.

    `reviewer_user_id: str | None`
    :   Unique identifier for the user who performed the review.

    `scorecard_id: str | None`
    :   Unique identifier for the scorecard template used.

    `scorecard_name: str | None`
    :   Name or title of the scorecard template used.

    `visibility_type: str | None`
    :   Type indicating the visibility permissions for the answered scorecard.

<a id="StatsInteractionListResultMeta"></a>

`StatsInteractionListResultMeta(**data: Any)`
:   Metadata for stats_interaction.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `current_page_number: int | Any`
    :   The type of the None singleton.

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_records: int | Any`
    :   The type of the None singleton.

<a id="Tracker"></a>

`Tracker(**data: Any)`
:   Keyword tracker configuration
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `affiliation: str | Any`
    :   The type of the None singleton.

    `created: str | Any`
    :   The type of the None singleton.

    `creator_user_id: str | Any | None`
    :   The type of the None singleton.

    `filter_query: str | Any`
    :   The type of the None singleton.

    `language_keywords: list[airbyte_agent_sdk.connectors.gong.models.TrackerLanguagekeywordsItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `part_of_question: bool | Any`
    :   The type of the None singleton.

    `said_at: str | Any`
    :   The type of the None singleton.

    `said_at_interval: str | Any | None`
    :   The type of the None singleton.

    `said_at_unit: str | Any | None`
    :   The type of the None singleton.

    `said_in_topics: list[str] | Any`
    :   The type of the None singleton.

    `tracker_id: str | Any`
    :   The type of the None singleton.

    `tracker_name: str | Any`
    :   The type of the None singleton.

    `updated: str | Any`
    :   The type of the None singleton.

    `updater_user_id: str | Any | None`
    :   The type of the None singleton.

    `workspace_id: str | Any | None`
    :   The type of the None singleton.

<a id="TrackerLanguagekeywordsItem"></a>

`TrackerLanguagekeywordsItem(**data: Any)`
:   Nested schema for Tracker.languageKeywords_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `include_related_forms: bool | Any`
    :   Whether to include related word forms

    `keywords: list[str] | Any`
    :   List of keywords for this language

    `language: str | Any`
    :   Language code

    `model_config`
    :   The type of the None singleton.

<a id="TrackersResponse"></a>

`TrackersResponse(**data: Any)`
:   Response containing list of trackers
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `keyword_trackers: list[airbyte_agent_sdk.connectors.gong.models.Tracker] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

<a id="TranscriptsResponse"></a>

`TranscriptsResponse(**data: Any)`
:   Response containing call transcripts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `call_transcripts: list[airbyte_agent_sdk.connectors.gong.models.CallTranscript] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `records: airbyte_agent_sdk.connectors.gong.models.PaginationRecords | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

<a id="User"></a>

`User(**data: Any)`
:   User object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any`
    :   The type of the None singleton.

    `created: str | Any`
    :   The type of the None singleton.

    `email_address: str | Any`
    :   The type of the None singleton.

    `email_aliases: list[str] | Any`
    :   The type of the None singleton.

    `extension: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `last_name: str | Any`
    :   The type of the None singleton.

    `manager_id: str | Any | None`
    :   The type of the None singleton.

    `meeting_consent_page_url: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `personal_meeting_urls: list[str] | Any`
    :   The type of the None singleton.

    `phone_number: str | Any | None`
    :   The type of the None singleton.

    `settings: airbyte_agent_sdk.connectors.gong.models.UserSettings | Any`
    :   The type of the None singleton.

    `spoken_languages: list[airbyte_agent_sdk.connectors.gong.models.UserSpokenlanguagesItem] | Any`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `trusted_email_address: str | Any | None`
    :   The type of the None singleton.

<a id="UserAggregateActivity"></a>

`UserAggregateActivity(**data: Any)`
:   User with aggregated activity statistics
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `user_aggregate_activity_stats: airbyte_agent_sdk.connectors.gong.models.UserAggregateActivityStats | Any`
    :   The type of the None singleton.

    `user_email_address: str | Any`
    :   The type of the None singleton.

    `user_id: str | Any`
    :   The type of the None singleton.

<a id="UserAggregateActivityStats"></a>

`UserAggregateActivityStats(**data: Any)`
:   Aggregated activity statistics for a user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `calls_as_host: int | Any`
    :   The type of the None singleton.

    `calls_attended: int | Any`
    :   The type of the None singleton.

    `calls_comments_given: int | Any`
    :   The type of the None singleton.

    `calls_comments_received: int | Any`
    :   The type of the None singleton.

    `calls_gave_feedback: int | Any`
    :   The type of the None singleton.

    `calls_marked_as_feedback_given: int | Any`
    :   The type of the None singleton.

    `calls_marked_as_feedback_received: int | Any`
    :   The type of the None singleton.

    `calls_received_feedback: int | Any`
    :   The type of the None singleton.

    `calls_requested_feedback: int | Any`
    :   The type of the None singleton.

    `calls_scorecards_filled: int | Any`
    :   The type of the None singleton.

    `calls_scorecards_received: int | Any`
    :   The type of the None singleton.

    `calls_shared_externally: int | Any`
    :   The type of the None singleton.

    `calls_shared_internally: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `others_calls_listened_to: int | Any`
    :   The type of the None singleton.

    `own_calls_listened_to: int | Any`
    :   The type of the None singleton.

<a id="UserDetailedActivity"></a>

`UserDetailedActivity(**data: Any)`
:   User with detailed daily activity statistics
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `user_daily_activity_stats: list[airbyte_agent_sdk.connectors.gong.models.DailyActivityStats] | Any`
    :   The type of the None singleton.

    `user_email_address: str | Any`
    :   The type of the None singleton.

    `user_id: str | Any`
    :   The type of the None singleton.

<a id="UserInteractionStats"></a>

`UserInteractionStats(**data: Any)`
:   User with interaction statistics
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `person_interaction_stats: list[airbyte_agent_sdk.connectors.gong.models.PersonInteractionStat] | Any`
    :   The type of the None singleton.

    `user_email_address: str | Any`
    :   The type of the None singleton.

    `user_id: str | Any`
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

    `request_id: str | Any`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.gong.models.User | Any`
    :   The type of the None singleton.

<a id="UserSettings"></a>

`UserSettings(**data: Any)`
:   User settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `emails_imported: bool | Any`
    :   The type of the None singleton.

    `gong_connect_enabled: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `non_recorded_meetings_imported: bool | Any`
    :   The type of the None singleton.

    `prevent_email_import: bool | Any`
    :   The type of the None singleton.

    `prevent_web_conference_recording: bool | Any`
    :   The type of the None singleton.

    `telephony_calls_imported: bool | Any`
    :   The type of the None singleton.

    `web_conferences_recorded: bool | Any`
    :   The type of the None singleton.

<a id="UserSpokenlanguagesItem"></a>

`UserSpokenlanguagesItem(**data: Any)`
:   Nested schema for User.spokenLanguages_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `language: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `primary: bool | Any`
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

    `current_page_number: int | Any`
    :   The type of the None singleton.

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_records: int | Any`
    :   The type of the None singleton.

<a id="UsersResponse"></a>

`UsersResponse(**data: Any)`
:   Response containing list of users
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `records: airbyte_agent_sdk.connectors.gong.models.PaginationRecords | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

    `users: list[airbyte_agent_sdk.connectors.gong.models.User] | Any`
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

    `active: bool | None`
    :   Indicates if the user is currently active or not

    `created: str | None`
    :   The timestamp denoting when the user account was created

    `email_address: str | None`
    :   The primary email address associated with the user

    `email_aliases: list[typing.Any] | None`
    :   Additional email addresses that can be used to reach the user

    `extension: str | None`
    :   The phone extension number for the user

    `first_name: str | None`
    :   The first name of the user

    `id: str | None`
    :   Unique identifier for the user

    `last_name: str | None`
    :   The last name of the user

    `manager_id: str | None`
    :   The ID of the user's manager

    `meeting_consent_page_url: str | None`
    :   URL for the consent page related to meetings

    `model_config`
    :   The type of the None singleton.

    `personal_meeting_urls: list[typing.Any] | None`
    :   URLs for personal meeting rooms assigned to the user

    `phone_number: str | None`
    :   The phone number associated with the user

    `settings: dict[str, typing.Any] | None`
    :   User-specific settings and configurations

    `spoken_languages: list[typing.Any] | None`
    :   Languages spoken by the user

    `title: str | None`
    :   The job title or position of the user

    `trusted_email_address: str | None`
    :   An email address that is considered trusted for the user

<a id="Workspace"></a>

`Workspace(**data: Any)`
:   Workspace object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `workspace_id: str | Any`
    :   The type of the None singleton.

<a id="WorkspacesResponse"></a>

`WorkspacesResponse(**data: Any)`
:   Response containing list of workspaces
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

    `workspaces: list[airbyte_agent_sdk.connectors.gong.models.Workspace] | Any`
    :   The type of the None singleton.