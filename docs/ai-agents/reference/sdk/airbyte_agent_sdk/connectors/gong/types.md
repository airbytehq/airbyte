---
id: airbyte_agent_sdk-connectors-gong-types
title: airbyte_agent_sdk.connectors.gong.types
---

Module airbyte_agent_sdk.connectors.gong.types
==============================================
Type definitions for gong connector.

Classes
-------

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

`CallAudioDownloadParams(*args, **kwargs)`
:   Parameters for call_audio.download operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content_selector: airbyte_agent_sdk.connectors.gong.types.CallAudioDownloadParamsContentselector`
    :   The type of the None singleton.

    `filter: airbyte_agent_sdk.connectors.gong.types.CallAudioDownloadParamsFilter`
    :   The type of the None singleton.

    `range_header: str`
    :   The type of the None singleton.

`CallAudioDownloadParamsContentselector(*args, **kwargs)`
:   Nested schema for CallAudioDownloadParams.contentSelector

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `exposedFields: airbyte_agent_sdk.connectors.gong.types.CallAudioDownloadParamsContentselectorExposedfields`
    :   The type of the None singleton.

`CallAudioDownloadParamsContentselectorExposedfields(*args, **kwargs)`
:   Nested schema for CallAudioDownloadParamsContentselector.exposedFields

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `media: bool`
    :   The type of the None singleton.

`CallAudioDownloadParamsFilter(*args, **kwargs)`
:   Nested schema for CallAudioDownloadParams.filter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `callIds: list[str]`
    :   The type of the None singleton.

`CallTranscriptsListParams(*args, **kwargs)`
:   Parameters for call_transcripts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `filter: airbyte_agent_sdk.connectors.gong.types.CallTranscriptsListParamsFilter`
    :   The type of the None singleton.

`CallTranscriptsListParamsFilter(*args, **kwargs)`
:   Nested schema for CallTranscriptsListParams.filter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `callIds: list[str]`
    :   The type of the None singleton.

    `fromDateTime: str`
    :   The type of the None singleton.

    `toDateTime: str`
    :   The type of the None singleton.

`CallVideoDownloadParams(*args, **kwargs)`
:   Parameters for call_video.download operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content_selector: airbyte_agent_sdk.connectors.gong.types.CallVideoDownloadParamsContentselector`
    :   The type of the None singleton.

    `filter: airbyte_agent_sdk.connectors.gong.types.CallVideoDownloadParamsFilter`
    :   The type of the None singleton.

    `range_header: str`
    :   The type of the None singleton.

`CallVideoDownloadParamsContentselector(*args, **kwargs)`
:   Nested schema for CallVideoDownloadParams.contentSelector

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `exposedFields: airbyte_agent_sdk.connectors.gong.types.CallVideoDownloadParamsContentselectorExposedfields`
    :   The type of the None singleton.

`CallVideoDownloadParamsContentselectorExposedfields(*args, **kwargs)`
:   Nested schema for CallVideoDownloadParamsContentselector.exposedFields

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `media: bool`
    :   The type of the None singleton.

`CallVideoDownloadParamsFilter(*args, **kwargs)`
:   Nested schema for CallVideoDownloadParams.filter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `callIds: list[str]`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.gong.types.CallsEqCondition | airbyte_agent_sdk.connectors.gong.types.CallsNeqCondition | airbyte_agent_sdk.connectors.gong.types.CallsGtCondition | airbyte_agent_sdk.connectors.gong.types.CallsGteCondition | airbyte_agent_sdk.connectors.gong.types.CallsLtCondition | airbyte_agent_sdk.connectors.gong.types.CallsLteCondition | airbyte_agent_sdk.connectors.gong.types.CallsInCondition | airbyte_agent_sdk.connectors.gong.types.CallsLikeCondition | airbyte_agent_sdk.connectors.gong.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.gong.types.CallsContainsCondition | airbyte_agent_sdk.connectors.gong.types.CallsNotCondition | airbyte_agent_sdk.connectors.gong.types.CallsAndCondition | airbyte_agent_sdk.connectors.gong.types.CallsOrCondition | airbyte_agent_sdk.connectors.gong.types.CallsAnyCondition]`
    :   The type of the None singleton.

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

    `any: airbyte_agent_sdk.connectors.gong.types.CallsAnyValueFilter`
    :   The type of the None singleton.

`CallsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `calendar_event_id: Any`
    :   Unique identifier for the calendar event associated with the call.

    `client_unique_id: Any`
    :   Unique identifier for the client related to the call.

    `custom_data: Any`
    :   Custom data associated with the call.

    `direction: Any`
    :   Direction of the call (inbound/outbound).

    `duration: Any`
    :   Duration of the call in seconds.

    `id: Any`
    :   Unique identifier for the call.

    `is_private: Any`
    :   Indicates if the call is private or not.

    `language: Any`
    :   Language used in the call.

    `media: Any`
    :   Media type used for communication (voice, video, etc.).

    `meeting_url: Any`
    :   URL for accessing the meeting associated with the call.

    `primary_user_id: Any`
    :   Unique identifier for the primary user involved in the call.

    `purpose: Any`
    :   Purpose or topic of the call.

    `scheduled: Any`
    :   Scheduled date and time of the call.

    `scope: Any`
    :   Scope or extent of the call.

    `sdr_disposition: Any`
    :   Disposition set by the sales development representative.

    `started: Any`
    :   Start date and time of the call.

    `system: Any`
    :   System information related to the call.

    `title: Any`
    :   Title or headline of the call.

    `url: Any`
    :   URL associated with the call.

    `workspace_id: Any`
    :   Identifier for the workspace to which the call belongs.

`CallsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gong.types.CallsAnyValueFilter`
    :   The type of the None singleton.

`CallsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gong.types.CallsSearchFilter`
    :   The type of the None singleton.

`CallsExtensiveAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.gong.types.CallsExtensiveEqCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveNeqCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveGtCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveGteCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveLtCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveLteCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveInCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveLikeCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveKeywordCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveContainsCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveNotCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveAndCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveOrCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveAnyCondition]`
    :   The type of the None singleton.

`CallsExtensiveAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveAnyValueFilter`
    :   The type of the None singleton.

`CallsExtensiveAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collaboration: Any`
    :   Collaboration information added to the call

    `content: Any`
    :   Analysis of the interaction content.

    `context: Any`
    :   A list of the agenda of each part of the call.

    `id: Any`
    :   Unique identifier for the call (from metaData.id).

    `interaction: Any`
    :   Metrics collected around the interaction during the call.

    `media: Any`
    :   The media urls of the call.

    `meta_data: Any`
    :   call's metadata.

    `parties: Any`
    :   A list of the call's participants

    `startdatetime: Any`
    :   Datetime for extensive calls.

`CallsExtensiveContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveAnyValueFilter`
    :   The type of the None singleton.

`CallsExtensiveEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveSearchFilter`
    :   The type of the None singleton.

`CallsExtensiveFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveStringFilter`
    :   The type of the None singleton.

`CallsExtensiveGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveSearchFilter`
    :   The type of the None singleton.

`CallsExtensiveGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveSearchFilter`
    :   The type of the None singleton.

`CallsExtensiveInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveInFilter`
    :   The type of the None singleton.

`CallsExtensiveInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collaboration: list[dict[str, typing.Any]]`
    :   Collaboration information added to the call

    `content: list[dict[str, typing.Any]]`
    :   Analysis of the interaction content.

    `context: list[dict[str, typing.Any]]`
    :   A list of the agenda of each part of the call.

    `id: list[int]`
    :   Unique identifier for the call (from metaData.id).

    `interaction: list[dict[str, typing.Any]]`
    :   Metrics collected around the interaction during the call.

    `media: list[dict[str, typing.Any]]`
    :   The media urls of the call.

    `meta_data: list[dict[str, typing.Any]]`
    :   call's metadata.

    `parties: list[list[typing.Any]]`
    :   A list of the call's participants

    `startdatetime: list[str]`
    :   Datetime for extensive calls.

`CallsExtensiveKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveStringFilter`
    :   The type of the None singleton.

`CallsExtensiveLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveStringFilter`
    :   The type of the None singleton.

`CallsExtensiveListParams(*args, **kwargs)`
:   Parameters for calls_extensive.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content_selector: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveListParamsContentselector`
    :   The type of the None singleton.

    `cursor: str`
    :   The type of the None singleton.

    `filter: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveListParamsFilter`
    :   The type of the None singleton.

`CallsExtensiveListParamsContentselector(*args, **kwargs)`
:   Select which content to include in the response

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `context: str`
    :   The type of the None singleton.

    `contextTiming: list[str]`
    :   The type of the None singleton.

    `exposedFields: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveListParamsContentselectorExposedfields`
    :   The type of the None singleton.

`CallsExtensiveListParamsContentselectorExposedfields(*args, **kwargs)`
:   Specify which fields to include in the response

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collaboration: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveListParamsContentselectorExposedfieldsCollaboration`
    :   The type of the None singleton.

    `content: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveListParamsContentselectorExposedfieldsContent`
    :   The type of the None singleton.

    `interaction: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveListParamsContentselectorExposedfieldsInteraction`
    :   The type of the None singleton.

    `media: bool`
    :   The type of the None singleton.

    `parties: bool`
    :   The type of the None singleton.

`CallsExtensiveListParamsContentselectorExposedfieldsCollaboration(*args, **kwargs)`
:   Nested schema for CallsExtensiveListParamsContentselectorExposedfields.collaboration

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `publicComments: bool`
    :   The type of the None singleton.

`CallsExtensiveListParamsContentselectorExposedfieldsContent(*args, **kwargs)`
:   Nested schema for CallsExtensiveListParamsContentselectorExposedfields.content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `brief: bool`
    :   The type of the None singleton.

    `callOutcome: bool`
    :   The type of the None singleton.

    `highlights: bool`
    :   The type of the None singleton.

    `keyPoints: bool`
    :   The type of the None singleton.

    `outline: bool`
    :   The type of the None singleton.

    `pointsOfInterest: bool`
    :   The type of the None singleton.

    `structure: bool`
    :   The type of the None singleton.

    `topics: bool`
    :   The type of the None singleton.

    `trackerOccurrences: bool`
    :   The type of the None singleton.

    `trackers: bool`
    :   The type of the None singleton.

`CallsExtensiveListParamsContentselectorExposedfieldsInteraction(*args, **kwargs)`
:   Nested schema for CallsExtensiveListParamsContentselectorExposedfields.interaction

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `personInteractionStats: bool`
    :   The type of the None singleton.

    `questions: bool`
    :   The type of the None singleton.

    `speakers: bool`
    :   The type of the None singleton.

    `video: bool`
    :   The type of the None singleton.

`CallsExtensiveListParamsFilter(*args, **kwargs)`
:   Nested schema for CallsExtensiveListParams.filter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `callIds: list[str]`
    :   The type of the None singleton.

    `fromDateTime: str`
    :   The type of the None singleton.

    `toDateTime: str`
    :   The type of the None singleton.

    `workspaceId: str`
    :   The type of the None singleton.

`CallsExtensiveLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveSearchFilter`
    :   The type of the None singleton.

`CallsExtensiveLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveSearchFilter`
    :   The type of the None singleton.

`CallsExtensiveNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveSearchFilter`
    :   The type of the None singleton.

`CallsExtensiveNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveEqCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveNeqCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveGtCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveGteCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveLtCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveLteCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveInCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveLikeCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveKeywordCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveContainsCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveNotCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveAndCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveOrCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveAnyCondition`
    :   The type of the None singleton.

`CallsExtensiveOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.gong.types.CallsExtensiveEqCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveNeqCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveGtCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveGteCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveLtCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveLteCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveInCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveLikeCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveKeywordCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveContainsCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveNotCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveAndCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveOrCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveAnyCondition]`
    :   The type of the None singleton.

`CallsExtensiveSearchFilter(*args, **kwargs)`
:   Available fields for filtering calls_extensive search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

    `parties: list[typing.Any] | None`
    :   A list of the call's participants

    `startdatetime: str | None`
    :   Datetime for extensive calls.

`CallsExtensiveSearchQuery(*args, **kwargs)`
:   Search query for calls_extensive entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gong.types.CallsExtensiveEqCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveNeqCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveGtCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveGteCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveLtCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveLteCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveInCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveLikeCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveKeywordCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveContainsCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveNotCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveAndCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveOrCondition | airbyte_agent_sdk.connectors.gong.types.CallsExtensiveAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gong.types.CallsExtensiveSortFilter]`
    :   The type of the None singleton.

`CallsExtensiveSortFilter(*args, **kwargs)`
:   Available fields for sorting calls_extensive search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collaboration: Literal['asc', 'desc']`
    :   Collaboration information added to the call

    `content: Literal['asc', 'desc']`
    :   Analysis of the interaction content.

    `context: Literal['asc', 'desc']`
    :   A list of the agenda of each part of the call.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the call (from metaData.id).

    `interaction: Literal['asc', 'desc']`
    :   Metrics collected around the interaction during the call.

    `media: Literal['asc', 'desc']`
    :   The media urls of the call.

    `meta_data: Literal['asc', 'desc']`
    :   call's metadata.

    `parties: Literal['asc', 'desc']`
    :   A list of the call's participants

    `startdatetime: Literal['asc', 'desc']`
    :   Datetime for extensive calls.

`CallsExtensiveStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collaboration: str`
    :   Collaboration information added to the call

    `content: str`
    :   Analysis of the interaction content.

    `context: str`
    :   A list of the agenda of each part of the call.

    `id: str`
    :   Unique identifier for the call (from metaData.id).

    `interaction: str`
    :   Metrics collected around the interaction during the call.

    `media: str`
    :   The media urls of the call.

    `meta_data: str`
    :   call's metadata.

    `parties: str`
    :   A list of the call's participants

    `startdatetime: str`
    :   Datetime for extensive calls.

`CallsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gong.types.CallsStringFilter`
    :   The type of the None singleton.

`CallsGetParams(*args, **kwargs)`
:   Parameters for calls.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`CallsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gong.types.CallsSearchFilter`
    :   The type of the None singleton.

`CallsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gong.types.CallsSearchFilter`
    :   The type of the None singleton.

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

    `in: airbyte_agent_sdk.connectors.gong.types.CallsInFilter`
    :   The type of the None singleton.

`CallsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `calendar_event_id: list[str]`
    :   Unique identifier for the calendar event associated with the call.

    `client_unique_id: list[str]`
    :   Unique identifier for the client related to the call.

    `custom_data: list[str]`
    :   Custom data associated with the call.

    `direction: list[str]`
    :   Direction of the call (inbound/outbound).

    `duration: list[int]`
    :   Duration of the call in seconds.

    `id: list[str]`
    :   Unique identifier for the call.

    `is_private: list[bool]`
    :   Indicates if the call is private or not.

    `language: list[str]`
    :   Language used in the call.

    `media: list[str]`
    :   Media type used for communication (voice, video, etc.).

    `meeting_url: list[str]`
    :   URL for accessing the meeting associated with the call.

    `primary_user_id: list[str]`
    :   Unique identifier for the primary user involved in the call.

    `purpose: list[str]`
    :   Purpose or topic of the call.

    `scheduled: list[str]`
    :   Scheduled date and time of the call.

    `scope: list[str]`
    :   Scope or extent of the call.

    `sdr_disposition: list[str]`
    :   Disposition set by the sales development representative.

    `started: list[str]`
    :   Start date and time of the call.

    `system: list[str]`
    :   System information related to the call.

    `title: list[str]`
    :   Title or headline of the call.

    `url: list[str]`
    :   URL associated with the call.

    `workspace_id: list[str]`
    :   Identifier for the workspace to which the call belongs.

`CallsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gong.types.CallsStringFilter`
    :   The type of the None singleton.

`CallsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gong.types.CallsStringFilter`
    :   The type of the None singleton.

`CallsListParams(*args, **kwargs)`
:   Parameters for calls.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `from_date_time: str`
    :   The type of the None singleton.

    `to_date_time: str`
    :   The type of the None singleton.

`CallsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gong.types.CallsSearchFilter`
    :   The type of the None singleton.

`CallsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gong.types.CallsSearchFilter`
    :   The type of the None singleton.

`CallsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gong.types.CallsSearchFilter`
    :   The type of the None singleton.

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

    `not: airbyte_agent_sdk.connectors.gong.types.CallsEqCondition | airbyte_agent_sdk.connectors.gong.types.CallsNeqCondition | airbyte_agent_sdk.connectors.gong.types.CallsGtCondition | airbyte_agent_sdk.connectors.gong.types.CallsGteCondition | airbyte_agent_sdk.connectors.gong.types.CallsLtCondition | airbyte_agent_sdk.connectors.gong.types.CallsLteCondition | airbyte_agent_sdk.connectors.gong.types.CallsInCondition | airbyte_agent_sdk.connectors.gong.types.CallsLikeCondition | airbyte_agent_sdk.connectors.gong.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.gong.types.CallsContainsCondition | airbyte_agent_sdk.connectors.gong.types.CallsNotCondition | airbyte_agent_sdk.connectors.gong.types.CallsAndCondition | airbyte_agent_sdk.connectors.gong.types.CallsOrCondition | airbyte_agent_sdk.connectors.gong.types.CallsAnyCondition`
    :   The type of the None singleton.

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

    `or: list[airbyte_agent_sdk.connectors.gong.types.CallsEqCondition | airbyte_agent_sdk.connectors.gong.types.CallsNeqCondition | airbyte_agent_sdk.connectors.gong.types.CallsGtCondition | airbyte_agent_sdk.connectors.gong.types.CallsGteCondition | airbyte_agent_sdk.connectors.gong.types.CallsLtCondition | airbyte_agent_sdk.connectors.gong.types.CallsLteCondition | airbyte_agent_sdk.connectors.gong.types.CallsInCondition | airbyte_agent_sdk.connectors.gong.types.CallsLikeCondition | airbyte_agent_sdk.connectors.gong.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.gong.types.CallsContainsCondition | airbyte_agent_sdk.connectors.gong.types.CallsNotCondition | airbyte_agent_sdk.connectors.gong.types.CallsAndCondition | airbyte_agent_sdk.connectors.gong.types.CallsOrCondition | airbyte_agent_sdk.connectors.gong.types.CallsAnyCondition]`
    :   The type of the None singleton.

`CallsSearchFilter(*args, **kwargs)`
:   Available fields for filtering calls search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

`CallsSearchQuery(*args, **kwargs)`
:   Search query for calls entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gong.types.CallsEqCondition | airbyte_agent_sdk.connectors.gong.types.CallsNeqCondition | airbyte_agent_sdk.connectors.gong.types.CallsGtCondition | airbyte_agent_sdk.connectors.gong.types.CallsGteCondition | airbyte_agent_sdk.connectors.gong.types.CallsLtCondition | airbyte_agent_sdk.connectors.gong.types.CallsLteCondition | airbyte_agent_sdk.connectors.gong.types.CallsInCondition | airbyte_agent_sdk.connectors.gong.types.CallsLikeCondition | airbyte_agent_sdk.connectors.gong.types.CallsFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.CallsKeywordCondition | airbyte_agent_sdk.connectors.gong.types.CallsContainsCondition | airbyte_agent_sdk.connectors.gong.types.CallsNotCondition | airbyte_agent_sdk.connectors.gong.types.CallsAndCondition | airbyte_agent_sdk.connectors.gong.types.CallsOrCondition | airbyte_agent_sdk.connectors.gong.types.CallsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gong.types.CallsSortFilter]`
    :   The type of the None singleton.

`CallsSortFilter(*args, **kwargs)`
:   Available fields for sorting calls search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `calendar_event_id: Literal['asc', 'desc']`
    :   Unique identifier for the calendar event associated with the call.

    `client_unique_id: Literal['asc', 'desc']`
    :   Unique identifier for the client related to the call.

    `custom_data: Literal['asc', 'desc']`
    :   Custom data associated with the call.

    `direction: Literal['asc', 'desc']`
    :   Direction of the call (inbound/outbound).

    `duration: Literal['asc', 'desc']`
    :   Duration of the call in seconds.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the call.

    `is_private: Literal['asc', 'desc']`
    :   Indicates if the call is private or not.

    `language: Literal['asc', 'desc']`
    :   Language used in the call.

    `media: Literal['asc', 'desc']`
    :   Media type used for communication (voice, video, etc.).

    `meeting_url: Literal['asc', 'desc']`
    :   URL for accessing the meeting associated with the call.

    `primary_user_id: Literal['asc', 'desc']`
    :   Unique identifier for the primary user involved in the call.

    `purpose: Literal['asc', 'desc']`
    :   Purpose or topic of the call.

    `scheduled: Literal['asc', 'desc']`
    :   Scheduled date and time of the call.

    `scope: Literal['asc', 'desc']`
    :   Scope or extent of the call.

    `sdr_disposition: Literal['asc', 'desc']`
    :   Disposition set by the sales development representative.

    `started: Literal['asc', 'desc']`
    :   Start date and time of the call.

    `system: Literal['asc', 'desc']`
    :   System information related to the call.

    `title: Literal['asc', 'desc']`
    :   Title or headline of the call.

    `url: Literal['asc', 'desc']`
    :   URL associated with the call.

    `workspace_id: Literal['asc', 'desc']`
    :   Identifier for the workspace to which the call belongs.

`CallsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `calendar_event_id: str`
    :   Unique identifier for the calendar event associated with the call.

    `client_unique_id: str`
    :   Unique identifier for the client related to the call.

    `custom_data: str`
    :   Custom data associated with the call.

    `direction: str`
    :   Direction of the call (inbound/outbound).

    `duration: str`
    :   Duration of the call in seconds.

    `id: str`
    :   Unique identifier for the call.

    `is_private: str`
    :   Indicates if the call is private or not.

    `language: str`
    :   Language used in the call.

    `media: str`
    :   Media type used for communication (voice, video, etc.).

    `meeting_url: str`
    :   URL for accessing the meeting associated with the call.

    `primary_user_id: str`
    :   Unique identifier for the primary user involved in the call.

    `purpose: str`
    :   Purpose or topic of the call.

    `scheduled: str`
    :   Scheduled date and time of the call.

    `scope: str`
    :   Scope or extent of the call.

    `sdr_disposition: str`
    :   Disposition set by the sales development representative.

    `started: str`
    :   Start date and time of the call.

    `system: str`
    :   System information related to the call.

    `title: str`
    :   Title or headline of the call.

    `url: str`
    :   URL associated with the call.

    `workspace_id: str`
    :   Identifier for the workspace to which the call belongs.

`CoachingListParams(*args, **kwargs)`
:   Parameters for coaching.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `from_: str`
    :   The type of the None singleton.

    `manager_id: str`
    :   The type of the None singleton.

    `to: str`
    :   The type of the None singleton.

    `workspace_id: str`
    :   The type of the None singleton.

`LibraryFolderContentListParams(*args, **kwargs)`
:   Parameters for library_folder_content.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `folder_id: str`
    :   The type of the None singleton.

`LibraryFoldersListParams(*args, **kwargs)`
:   Parameters for library_folders.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `workspace_id: str`
    :   The type of the None singleton.

`SettingsScorecardsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsEqCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsNeqCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsGtCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsGteCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsLtCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsLteCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsInCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsLikeCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsKeywordCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsContainsCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsNotCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsAndCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsOrCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsAnyCondition]`
    :   The type of the None singleton.

`SettingsScorecardsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsAnyValueFilter`
    :   The type of the None singleton.

`SettingsScorecardsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: Any`
    :   The timestamp when the scorecard was created

    `enabled: Any`
    :   Indicates if the scorecard is enabled or disabled

    `questions: Any`
    :   An array of questions related to the scorecard

    `scorecard_id: Any`
    :   The unique identifier of the scorecard

    `scorecard_name: Any`
    :   The name of the scorecard

    `updated: Any`
    :   The timestamp when the scorecard was last updated

    `updater_user_id: Any`
    :   The user ID of the person who last updated the scorecard

    `workspace_id: Any`
    :   The unique identifier of the workspace associated with the scorecard

`SettingsScorecardsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsAnyValueFilter`
    :   The type of the None singleton.

`SettingsScorecardsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsSearchFilter`
    :   The type of the None singleton.

`SettingsScorecardsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsStringFilter`
    :   The type of the None singleton.

`SettingsScorecardsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsSearchFilter`
    :   The type of the None singleton.

`SettingsScorecardsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsSearchFilter`
    :   The type of the None singleton.

`SettingsScorecardsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsInFilter`
    :   The type of the None singleton.

`SettingsScorecardsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: list[str]`
    :   The timestamp when the scorecard was created

    `enabled: list[bool]`
    :   Indicates if the scorecard is enabled or disabled

    `questions: list[list[typing.Any]]`
    :   An array of questions related to the scorecard

    `scorecard_id: list[str]`
    :   The unique identifier of the scorecard

    `scorecard_name: list[str]`
    :   The name of the scorecard

    `updated: list[str]`
    :   The timestamp when the scorecard was last updated

    `updater_user_id: list[str]`
    :   The user ID of the person who last updated the scorecard

    `workspace_id: list[str]`
    :   The unique identifier of the workspace associated with the scorecard

`SettingsScorecardsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsStringFilter`
    :   The type of the None singleton.

`SettingsScorecardsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsStringFilter`
    :   The type of the None singleton.

`SettingsScorecardsListParams(*args, **kwargs)`
:   Parameters for settings_scorecards.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `workspace_id: str`
    :   The type of the None singleton.

`SettingsScorecardsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsSearchFilter`
    :   The type of the None singleton.

`SettingsScorecardsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsSearchFilter`
    :   The type of the None singleton.

`SettingsScorecardsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsSearchFilter`
    :   The type of the None singleton.

`SettingsScorecardsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsEqCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsNeqCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsGtCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsGteCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsLtCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsLteCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsInCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsLikeCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsKeywordCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsContainsCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsNotCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsAndCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsOrCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsAnyCondition`
    :   The type of the None singleton.

`SettingsScorecardsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsEqCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsNeqCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsGtCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsGteCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsLtCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsLteCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsInCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsLikeCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsKeywordCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsContainsCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsNotCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsAndCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsOrCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsAnyCondition]`
    :   The type of the None singleton.

`SettingsScorecardsSearchFilter(*args, **kwargs)`
:   Available fields for filtering settings_scorecards search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: str | None`
    :   The timestamp when the scorecard was created

    `enabled: bool | None`
    :   Indicates if the scorecard is enabled or disabled

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

`SettingsScorecardsSearchQuery(*args, **kwargs)`
:   Search query for settings_scorecards entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsEqCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsNeqCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsGtCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsGteCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsLtCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsLteCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsInCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsLikeCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsKeywordCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsContainsCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsNotCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsAndCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsOrCondition | airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gong.types.SettingsScorecardsSortFilter]`
    :   The type of the None singleton.

`SettingsScorecardsSortFilter(*args, **kwargs)`
:   Available fields for sorting settings_scorecards search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: Literal['asc', 'desc']`
    :   The timestamp when the scorecard was created

    `enabled: Literal['asc', 'desc']`
    :   Indicates if the scorecard is enabled or disabled

    `questions: Literal['asc', 'desc']`
    :   An array of questions related to the scorecard

    `scorecard_id: Literal['asc', 'desc']`
    :   The unique identifier of the scorecard

    `scorecard_name: Literal['asc', 'desc']`
    :   The name of the scorecard

    `updated: Literal['asc', 'desc']`
    :   The timestamp when the scorecard was last updated

    `updater_user_id: Literal['asc', 'desc']`
    :   The user ID of the person who last updated the scorecard

    `workspace_id: Literal['asc', 'desc']`
    :   The unique identifier of the workspace associated with the scorecard

`SettingsScorecardsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: str`
    :   The timestamp when the scorecard was created

    `enabled: str`
    :   Indicates if the scorecard is enabled or disabled

    `questions: str`
    :   An array of questions related to the scorecard

    `scorecard_id: str`
    :   The unique identifier of the scorecard

    `scorecard_name: str`
    :   The name of the scorecard

    `updated: str`
    :   The timestamp when the scorecard was last updated

    `updater_user_id: str`
    :   The user ID of the person who last updated the scorecard

    `workspace_id: str`
    :   The unique identifier of the workspace associated with the scorecard

`SettingsTrackersListParams(*args, **kwargs)`
:   Parameters for settings_trackers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `workspace_id: str`
    :   The type of the None singleton.

`StatsActivityAggregateListParams(*args, **kwargs)`
:   Parameters for stats_activity_aggregate.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gong.types.StatsActivityAggregateListParamsFilter`
    :   The type of the None singleton.

`StatsActivityAggregateListParamsFilter(*args, **kwargs)`
:   Nested schema for StatsActivityAggregateListParams.filter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fromDate: str`
    :   The type of the None singleton.

    `toDate: str`
    :   The type of the None singleton.

    `userIds: list[str]`
    :   The type of the None singleton.

`StatsActivityDayByDayListParams(*args, **kwargs)`
:   Parameters for stats_activity_day_by_day.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gong.types.StatsActivityDayByDayListParamsFilter`
    :   The type of the None singleton.

`StatsActivityDayByDayListParamsFilter(*args, **kwargs)`
:   Nested schema for StatsActivityDayByDayListParams.filter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fromDate: str`
    :   The type of the None singleton.

    `toDate: str`
    :   The type of the None singleton.

    `userIds: list[str]`
    :   The type of the None singleton.

`StatsActivityScorecardsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsEqCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsNeqCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsGtCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsGteCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsLtCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsLteCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsInCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsLikeCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsKeywordCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsContainsCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsNotCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsAndCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsOrCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsAnyCondition]`
    :   The type of the None singleton.

`StatsActivityScorecardsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsAnyValueFilter`
    :   The type of the None singleton.

`StatsActivityScorecardsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answered_scorecard_id: Any`
    :   Unique identifier for the answered scorecard instance.

    `answers: Any`
    :   Contains the answered questions in the scorecards

    `call_id: Any`
    :   Unique identifier for the call associated with the answered scorecard.

    `call_start_time: Any`
    :   Timestamp indicating the start time of the call.

    `review_time: Any`
    :   Timestamp indicating when the review of the answered scorecard was completed.

    `reviewed_user_id: Any`
    :   Unique identifier for the user whose performance was reviewed.

    `reviewer_user_id: Any`
    :   Unique identifier for the user who performed the review.

    `scorecard_id: Any`
    :   Unique identifier for the scorecard template used.

    `scorecard_name: Any`
    :   Name or title of the scorecard template used.

    `visibility_type: Any`
    :   Type indicating the visibility permissions for the answered scorecard.

`StatsActivityScorecardsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsAnyValueFilter`
    :   The type of the None singleton.

`StatsActivityScorecardsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsSearchFilter`
    :   The type of the None singleton.

`StatsActivityScorecardsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsStringFilter`
    :   The type of the None singleton.

`StatsActivityScorecardsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsSearchFilter`
    :   The type of the None singleton.

`StatsActivityScorecardsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsSearchFilter`
    :   The type of the None singleton.

`StatsActivityScorecardsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsInFilter`
    :   The type of the None singleton.

`StatsActivityScorecardsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answered_scorecard_id: list[str]`
    :   Unique identifier for the answered scorecard instance.

    `answers: list[list[typing.Any]]`
    :   Contains the answered questions in the scorecards

    `call_id: list[str]`
    :   Unique identifier for the call associated with the answered scorecard.

    `call_start_time: list[str]`
    :   Timestamp indicating the start time of the call.

    `review_time: list[str]`
    :   Timestamp indicating when the review of the answered scorecard was completed.

    `reviewed_user_id: list[str]`
    :   Unique identifier for the user whose performance was reviewed.

    `reviewer_user_id: list[str]`
    :   Unique identifier for the user who performed the review.

    `scorecard_id: list[str]`
    :   Unique identifier for the scorecard template used.

    `scorecard_name: list[str]`
    :   Name or title of the scorecard template used.

    `visibility_type: list[str]`
    :   Type indicating the visibility permissions for the answered scorecard.

`StatsActivityScorecardsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsStringFilter`
    :   The type of the None singleton.

`StatsActivityScorecardsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsStringFilter`
    :   The type of the None singleton.

`StatsActivityScorecardsListParams(*args, **kwargs)`
:   Parameters for stats_activity_scorecards.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `filter: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsListParamsFilter`
    :   The type of the None singleton.

`StatsActivityScorecardsListParamsFilter(*args, **kwargs)`
:   Nested schema for StatsActivityScorecardsListParams.filter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `callIds: list[str]`
    :   The type of the None singleton.

    `fromDateTime: str`
    :   The type of the None singleton.

    `reviewedUserIds: list[str]`
    :   The type of the None singleton.

    `reviewerUserIds: list[str]`
    :   The type of the None singleton.

    `scorecardIds: list[str]`
    :   The type of the None singleton.

    `toDateTime: str`
    :   The type of the None singleton.

`StatsActivityScorecardsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsSearchFilter`
    :   The type of the None singleton.

`StatsActivityScorecardsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsSearchFilter`
    :   The type of the None singleton.

`StatsActivityScorecardsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsSearchFilter`
    :   The type of the None singleton.

`StatsActivityScorecardsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsEqCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsNeqCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsGtCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsGteCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsLtCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsLteCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsInCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsLikeCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsKeywordCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsContainsCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsNotCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsAndCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsOrCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsAnyCondition`
    :   The type of the None singleton.

`StatsActivityScorecardsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsEqCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsNeqCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsGtCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsGteCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsLtCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsLteCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsInCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsLikeCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsKeywordCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsContainsCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsNotCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsAndCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsOrCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsAnyCondition]`
    :   The type of the None singleton.

`StatsActivityScorecardsSearchFilter(*args, **kwargs)`
:   Available fields for filtering stats_activity_scorecards search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answered_scorecard_id: str | None`
    :   Unique identifier for the answered scorecard instance.

    `answers: list[typing.Any] | None`
    :   Contains the answered questions in the scorecards

    `call_id: str | None`
    :   Unique identifier for the call associated with the answered scorecard.

    `call_start_time: str | None`
    :   Timestamp indicating the start time of the call.

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

`StatsActivityScorecardsSearchQuery(*args, **kwargs)`
:   Search query for stats_activity_scorecards entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsEqCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsNeqCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsGtCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsGteCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsLtCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsLteCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsInCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsLikeCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsKeywordCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsContainsCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsNotCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsAndCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsOrCondition | airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gong.types.StatsActivityScorecardsSortFilter]`
    :   The type of the None singleton.

`StatsActivityScorecardsSortFilter(*args, **kwargs)`
:   Available fields for sorting stats_activity_scorecards search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answered_scorecard_id: Literal['asc', 'desc']`
    :   Unique identifier for the answered scorecard instance.

    `answers: Literal['asc', 'desc']`
    :   Contains the answered questions in the scorecards

    `call_id: Literal['asc', 'desc']`
    :   Unique identifier for the call associated with the answered scorecard.

    `call_start_time: Literal['asc', 'desc']`
    :   Timestamp indicating the start time of the call.

    `review_time: Literal['asc', 'desc']`
    :   Timestamp indicating when the review of the answered scorecard was completed.

    `reviewed_user_id: Literal['asc', 'desc']`
    :   Unique identifier for the user whose performance was reviewed.

    `reviewer_user_id: Literal['asc', 'desc']`
    :   Unique identifier for the user who performed the review.

    `scorecard_id: Literal['asc', 'desc']`
    :   Unique identifier for the scorecard template used.

    `scorecard_name: Literal['asc', 'desc']`
    :   Name or title of the scorecard template used.

    `visibility_type: Literal['asc', 'desc']`
    :   Type indicating the visibility permissions for the answered scorecard.

`StatsActivityScorecardsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answered_scorecard_id: str`
    :   Unique identifier for the answered scorecard instance.

    `answers: str`
    :   Contains the answered questions in the scorecards

    `call_id: str`
    :   Unique identifier for the call associated with the answered scorecard.

    `call_start_time: str`
    :   Timestamp indicating the start time of the call.

    `review_time: str`
    :   Timestamp indicating when the review of the answered scorecard was completed.

    `reviewed_user_id: str`
    :   Unique identifier for the user whose performance was reviewed.

    `reviewer_user_id: str`
    :   Unique identifier for the user who performed the review.

    `scorecard_id: str`
    :   Unique identifier for the scorecard template used.

    `scorecard_name: str`
    :   Name or title of the scorecard template used.

    `visibility_type: str`
    :   Type indicating the visibility permissions for the answered scorecard.

`StatsInteractionListParams(*args, **kwargs)`
:   Parameters for stats_interaction.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gong.types.StatsInteractionListParamsFilter`
    :   The type of the None singleton.

`StatsInteractionListParamsFilter(*args, **kwargs)`
:   Nested schema for StatsInteractionListParams.filter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fromDate: str`
    :   The type of the None singleton.

    `toDate: str`
    :   The type of the None singleton.

    `userIds: list[str]`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.gong.types.UsersEqCondition | airbyte_agent_sdk.connectors.gong.types.UsersNeqCondition | airbyte_agent_sdk.connectors.gong.types.UsersGtCondition | airbyte_agent_sdk.connectors.gong.types.UsersGteCondition | airbyte_agent_sdk.connectors.gong.types.UsersLtCondition | airbyte_agent_sdk.connectors.gong.types.UsersLteCondition | airbyte_agent_sdk.connectors.gong.types.UsersInCondition | airbyte_agent_sdk.connectors.gong.types.UsersLikeCondition | airbyte_agent_sdk.connectors.gong.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.gong.types.UsersContainsCondition | airbyte_agent_sdk.connectors.gong.types.UsersNotCondition | airbyte_agent_sdk.connectors.gong.types.UsersAndCondition | airbyte_agent_sdk.connectors.gong.types.UsersOrCondition | airbyte_agent_sdk.connectors.gong.types.UsersAnyCondition]`
    :   The type of the None singleton.

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

    `any: airbyte_agent_sdk.connectors.gong.types.UsersAnyValueFilter`
    :   The type of the None singleton.

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Any`
    :   Indicates if the user is currently active or not

    `created: Any`
    :   The timestamp denoting when the user account was created

    `email_address: Any`
    :   The primary email address associated with the user

    `email_aliases: Any`
    :   Additional email addresses that can be used to reach the user

    `extension: Any`
    :   The phone extension number for the user

    `first_name: Any`
    :   The first name of the user

    `id: Any`
    :   Unique identifier for the user

    `last_name: Any`
    :   The last name of the user

    `manager_id: Any`
    :   The ID of the user's manager

    `meeting_consent_page_url: Any`
    :   URL for the consent page related to meetings

    `personal_meeting_urls: Any`
    :   URLs for personal meeting rooms assigned to the user

    `phone_number: Any`
    :   The phone number associated with the user

    `settings: Any`
    :   User-specific settings and configurations

    `spoken_languages: Any`
    :   Languages spoken by the user

    `title: Any`
    :   The job title or position of the user

    `trusted_email_address: Any`
    :   An email address that is considered trusted for the user

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gong.types.UsersAnyValueFilter`
    :   The type of the None singleton.

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gong.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gong.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gong.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gong.types.UsersSearchFilter`
    :   The type of the None singleton.

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

    `in: airbyte_agent_sdk.connectors.gong.types.UsersInFilter`
    :   The type of the None singleton.

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: list[bool]`
    :   Indicates if the user is currently active or not

    `created: list[str]`
    :   The timestamp denoting when the user account was created

    `email_address: list[str]`
    :   The primary email address associated with the user

    `email_aliases: list[list[typing.Any]]`
    :   Additional email addresses that can be used to reach the user

    `extension: list[str]`
    :   The phone extension number for the user

    `first_name: list[str]`
    :   The first name of the user

    `id: list[str]`
    :   Unique identifier for the user

    `last_name: list[str]`
    :   The last name of the user

    `manager_id: list[str]`
    :   The ID of the user's manager

    `meeting_consent_page_url: list[str]`
    :   URL for the consent page related to meetings

    `personal_meeting_urls: list[list[typing.Any]]`
    :   URLs for personal meeting rooms assigned to the user

    `phone_number: list[str]`
    :   The phone number associated with the user

    `settings: list[dict[str, typing.Any]]`
    :   User-specific settings and configurations

    `spoken_languages: list[list[typing.Any]]`
    :   Languages spoken by the user

    `title: list[str]`
    :   The job title or position of the user

    `trusted_email_address: list[str]`
    :   An email address that is considered trusted for the user

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gong.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gong.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gong.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gong.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gong.types.UsersSearchFilter`
    :   The type of the None singleton.

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

    `not: airbyte_agent_sdk.connectors.gong.types.UsersEqCondition | airbyte_agent_sdk.connectors.gong.types.UsersNeqCondition | airbyte_agent_sdk.connectors.gong.types.UsersGtCondition | airbyte_agent_sdk.connectors.gong.types.UsersGteCondition | airbyte_agent_sdk.connectors.gong.types.UsersLtCondition | airbyte_agent_sdk.connectors.gong.types.UsersLteCondition | airbyte_agent_sdk.connectors.gong.types.UsersInCondition | airbyte_agent_sdk.connectors.gong.types.UsersLikeCondition | airbyte_agent_sdk.connectors.gong.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.gong.types.UsersContainsCondition | airbyte_agent_sdk.connectors.gong.types.UsersNotCondition | airbyte_agent_sdk.connectors.gong.types.UsersAndCondition | airbyte_agent_sdk.connectors.gong.types.UsersOrCondition | airbyte_agent_sdk.connectors.gong.types.UsersAnyCondition`
    :   The type of the None singleton.

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

    `or: list[airbyte_agent_sdk.connectors.gong.types.UsersEqCondition | airbyte_agent_sdk.connectors.gong.types.UsersNeqCondition | airbyte_agent_sdk.connectors.gong.types.UsersGtCondition | airbyte_agent_sdk.connectors.gong.types.UsersGteCondition | airbyte_agent_sdk.connectors.gong.types.UsersLtCondition | airbyte_agent_sdk.connectors.gong.types.UsersLteCondition | airbyte_agent_sdk.connectors.gong.types.UsersInCondition | airbyte_agent_sdk.connectors.gong.types.UsersLikeCondition | airbyte_agent_sdk.connectors.gong.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.gong.types.UsersContainsCondition | airbyte_agent_sdk.connectors.gong.types.UsersNotCondition | airbyte_agent_sdk.connectors.gong.types.UsersAndCondition | airbyte_agent_sdk.connectors.gong.types.UsersOrCondition | airbyte_agent_sdk.connectors.gong.types.UsersAnyCondition]`
    :   The type of the None singleton.

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gong.types.UsersEqCondition | airbyte_agent_sdk.connectors.gong.types.UsersNeqCondition | airbyte_agent_sdk.connectors.gong.types.UsersGtCondition | airbyte_agent_sdk.connectors.gong.types.UsersGteCondition | airbyte_agent_sdk.connectors.gong.types.UsersLtCondition | airbyte_agent_sdk.connectors.gong.types.UsersLteCondition | airbyte_agent_sdk.connectors.gong.types.UsersInCondition | airbyte_agent_sdk.connectors.gong.types.UsersLikeCondition | airbyte_agent_sdk.connectors.gong.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.gong.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.gong.types.UsersContainsCondition | airbyte_agent_sdk.connectors.gong.types.UsersNotCondition | airbyte_agent_sdk.connectors.gong.types.UsersAndCondition | airbyte_agent_sdk.connectors.gong.types.UsersOrCondition | airbyte_agent_sdk.connectors.gong.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gong.types.UsersSortFilter]`
    :   The type of the None singleton.

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Literal['asc', 'desc']`
    :   Indicates if the user is currently active or not

    `created: Literal['asc', 'desc']`
    :   The timestamp denoting when the user account was created

    `email_address: Literal['asc', 'desc']`
    :   The primary email address associated with the user

    `email_aliases: Literal['asc', 'desc']`
    :   Additional email addresses that can be used to reach the user

    `extension: Literal['asc', 'desc']`
    :   The phone extension number for the user

    `first_name: Literal['asc', 'desc']`
    :   The first name of the user

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the user

    `last_name: Literal['asc', 'desc']`
    :   The last name of the user

    `manager_id: Literal['asc', 'desc']`
    :   The ID of the user's manager

    `meeting_consent_page_url: Literal['asc', 'desc']`
    :   URL for the consent page related to meetings

    `personal_meeting_urls: Literal['asc', 'desc']`
    :   URLs for personal meeting rooms assigned to the user

    `phone_number: Literal['asc', 'desc']`
    :   The phone number associated with the user

    `settings: Literal['asc', 'desc']`
    :   User-specific settings and configurations

    `spoken_languages: Literal['asc', 'desc']`
    :   Languages spoken by the user

    `title: Literal['asc', 'desc']`
    :   The job title or position of the user

    `trusted_email_address: Literal['asc', 'desc']`
    :   An email address that is considered trusted for the user

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: str`
    :   Indicates if the user is currently active or not

    `created: str`
    :   The timestamp denoting when the user account was created

    `email_address: str`
    :   The primary email address associated with the user

    `email_aliases: str`
    :   Additional email addresses that can be used to reach the user

    `extension: str`
    :   The phone extension number for the user

    `first_name: str`
    :   The first name of the user

    `id: str`
    :   Unique identifier for the user

    `last_name: str`
    :   The last name of the user

    `manager_id: str`
    :   The ID of the user's manager

    `meeting_consent_page_url: str`
    :   URL for the consent page related to meetings

    `personal_meeting_urls: str`
    :   URLs for personal meeting rooms assigned to the user

    `phone_number: str`
    :   The phone number associated with the user

    `settings: str`
    :   User-specific settings and configurations

    `spoken_languages: str`
    :   Languages spoken by the user

    `title: str`
    :   The job title or position of the user

    `trusted_email_address: str`
    :   An email address that is considered trusted for the user

`WorkspacesListParams(*args, **kwargs)`
:   Parameters for workspaces.list operation

    ### Ancestors (in MRO)

    * builtins.dict