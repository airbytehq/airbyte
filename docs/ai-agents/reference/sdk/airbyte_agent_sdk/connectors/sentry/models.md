---
id: airbyte_agent_sdk-connectors-sentry-models
title: airbyte_agent_sdk.connectors.sentry.models
---

Module airbyte_agent_sdk.connectors.sentry.models
=================================================
Pydantic models for sentry connector.

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

    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult[EventsSearchData]
    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult[IssuesSearchData]
    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult[ProjectsSearchData]
    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult[ReleasesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[EventsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="EventsSearchResult"></a>

`EventsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[IssuesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="IssuesSearchResult"></a>

`IssuesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProjectsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProjectsSearchResult"></a>

`ProjectsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ReleasesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ReleasesSearchResult"></a>

`ReleasesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Event"></a>

`Event(**data: Any)`
:   A Sentry event (individual error occurrence).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `context: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `contexts: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `crash_file: str | Any | None`
    :   The type of the None singleton.

    `culprit: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_received: str | Any | None`
    :   The type of the None singleton.

    `dist: str | Any | None`
    :   The type of the None singleton.

    `entries: list[dict[str, typing.Any] | None] | Any | None`
    :   The type of the None singleton.

    `errors: list[str | None] | Any | None`
    :   The type of the None singleton.

    `event_id: str | Any | None`
    :   The type of the None singleton.

    `event_type: str | Any | None`
    :   The type of the None singleton.

    `fingerprints: list[str | None] | Any | None`
    :   The type of the None singleton.

    `group_id: str | Any | None`
    :   The type of the None singleton.

    `grouping_config: airbyte_agent_sdk.connectors.sentry.models.EventGroupingconfig | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `location: str | Any | None`
    :   The type of the None singleton.

    `message: str | Any | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `metadata: airbyte_agent_sdk.connectors.sentry.models.EventMetadata | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `packages: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `platform: str | Any | None`
    :   The type of the None singleton.

    `project_id: str | Any | None`
    :   The type of the None singleton.

    `sdk: str | Any | None`
    :   The type of the None singleton.

    `size: int | Any | None`
    :   The type of the None singleton.

    `tags: list[airbyte_agent_sdk.connectors.sentry.models.EventTagsItem | None] | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.sentry.models.EventUser | Any | None`
    :   The type of the None singleton.

<a id="EventGroupingconfig"></a>

`EventGroupingconfig(**data: Any)`
:   Grouping configuration.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enhancements: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="EventMetadata"></a>

`EventMetadata(**data: Any)`
:   Event metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

<a id="EventTagsItem"></a>

`EventTagsItem(**data: Any)`
:   Nested schema for Event.tags_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `key: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: str | Any | None`
    :   The type of the None singleton.

<a id="EventUser"></a>

`EventUser(**data: Any)`
:   User associated with the event.
    
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

    `ip_address: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `username: str | Any | None`
    :   The type of the None singleton.

<a id="EventsListResultMeta"></a>

`EventsListResultMeta(**data: Any)`
:   Metadata for events.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="EventsSearchData"></a>

`EventsSearchData(**data: Any)`
:   Search result data for events entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="Issue"></a>

`Issue(**data: Any)`
:   A Sentry issue (group of similar events).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: list[str | None] | Any | None`
    :   The type of the None singleton.

    `assigned_to: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `count: str | Any | None`
    :   The type of the None singleton.

    `culprit: str | Any | None`
    :   The type of the None singleton.

    `first_seen: str | Any | None`
    :   The type of the None singleton.

    `has_seen: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `is_bookmarked: bool | Any | None`
    :   The type of the None singleton.

    `is_public: bool | Any | None`
    :   The type of the None singleton.

    `is_subscribed: bool | Any | None`
    :   The type of the None singleton.

    `is_unhandled: bool | Any | None`
    :   The type of the None singleton.

    `issue_category: str | Any | None`
    :   The type of the None singleton.

    `issue_type: str | Any | None`
    :   The type of the None singleton.

    `last_seen: str | Any | None`
    :   The type of the None singleton.

    `level: str | Any | None`
    :   The type of the None singleton.

    `logger: str | Any | None`
    :   The type of the None singleton.

    `metadata: airbyte_agent_sdk.connectors.sentry.models.IssueMetadata | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `num_comments: int | Any | None`
    :   The type of the None singleton.

    `permalink: str | Any | None`
    :   The type of the None singleton.

    `platform: str | Any | None`
    :   The type of the None singleton.

    `project: airbyte_agent_sdk.connectors.sentry.models.IssueProject | Any | None`
    :   The type of the None singleton.

    `share_id: str | Any | None`
    :   The type of the None singleton.

    `short_id: str | Any | None`
    :   The type of the None singleton.

    `stats: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `status_details: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `subscription_details: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `substatus: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `user_count: int | Any | None`
    :   The type of the None singleton.

<a id="IssueMetadata"></a>

`IssueMetadata(**data: Any)`
:   Issue metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `filename: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `value: str | Any | None`
    :   The type of the None singleton.

<a id="IssueProject"></a>

`IssueProject(**data: Any)`
:   Project this issue belongs to.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

<a id="IssuesListResultMeta"></a>

`IssuesListResultMeta(**data: Any)`
:   Metadata for issues.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="IssuesSearchData"></a>

`IssuesSearchData(**data: Any)`
:   Search result data for issues entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="Project"></a>

`Project(**data: Any)`
:   A Sentry project (summary view from list endpoint).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access: list[str | None] | Any | None`
    :   The type of the None singleton.

    `avatar: airbyte_agent_sdk.connectors.sentry.models.ProjectAvatar | Any | None`
    :   The type of the None singleton.

    `color: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `features: list[str | None] | Any | None`
    :   The type of the None singleton.

    `first_event: str | Any | None`
    :   The type of the None singleton.

    `first_transaction_event: bool | Any | None`
    :   The type of the None singleton.

    `has_access: bool | Any | None`
    :   The type of the None singleton.

    `has_feedbacks: bool | Any | None`
    :   The type of the None singleton.

    `has_flags: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_agent_monitoring: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_app_start: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_assets: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_caches: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_db: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_http: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_mcp: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_queues: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_screen_load: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_vitals: bool | Any | None`
    :   The type of the None singleton.

    `has_logs: bool | Any | None`
    :   The type of the None singleton.

    `has_minified_stack_trace: bool | Any | None`
    :   The type of the None singleton.

    `has_monitors: bool | Any | None`
    :   The type of the None singleton.

    `has_new_feedbacks: bool | Any | None`
    :   The type of the None singleton.

    `has_profiles: bool | Any | None`
    :   The type of the None singleton.

    `has_replays: bool | Any | None`
    :   The type of the None singleton.

    `has_sessions: bool | Any | None`
    :   The type of the None singleton.

    `has_trace_metrics: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `is_bookmarked: bool | Any | None`
    :   The type of the None singleton.

    `is_internal: bool | Any | None`
    :   The type of the None singleton.

    `is_member: bool | Any | None`
    :   The type of the None singleton.

    `is_public: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `organization: airbyte_agent_sdk.connectors.sentry.models.ProjectOrganization | Any | None`
    :   The type of the None singleton.

    `platform: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

<a id="ProjectAvatar"></a>

`ProjectAvatar(**data: Any)`
:   Project avatar information.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_type: str | Any | None`
    :   The type of the None singleton.

    `avatar_url: str | Any | None`
    :   The type of the None singleton.

    `avatar_uuid: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProjectDetail"></a>

`ProjectDetail(**data: Any)`
:   Detailed project information.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access: list[str | None] | Any | None`
    :   The type of the None singleton.

    `allowed_domains: list[str | None] | Any | None`
    :   The type of the None singleton.

    `autofix_automation_tuning: str | Any | None`
    :   The type of the None singleton.

    `avatar: airbyte_agent_sdk.connectors.sentry.models.ProjectDetailAvatar | Any | None`
    :   The type of the None singleton.

    `builtin_symbol_sources: list[str | None] | Any | None`
    :   The type of the None singleton.

    `color: str | Any | None`
    :   The type of the None singleton.

    `data_scrubber: bool | Any | None`
    :   The type of the None singleton.

    `data_scrubber_defaults: bool | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `debug_files_role: str | Any | None`
    :   The type of the None singleton.

    `default_environment: str | Any | None`
    :   The type of the None singleton.

    `derived_grouping_enhancements: str | Any | None`
    :   The type of the None singleton.

    `digests_max_delay: int | Any | None`
    :   The type of the None singleton.

    `digests_min_delay: int | Any | None`
    :   The type of the None singleton.

    `dynamic_sampling_biases: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `features: list[str | None] | Any | None`
    :   The type of the None singleton.

    `fingerprinting_rules: str | Any | None`
    :   The type of the None singleton.

    `first_event: str | Any | None`
    :   The type of the None singleton.

    `first_transaction_event: bool | Any | None`
    :   The type of the None singleton.

    `grouping_config: str | Any | None`
    :   The type of the None singleton.

    `grouping_enhancements: str | Any | None`
    :   The type of the None singleton.

    `has_access: bool | Any | None`
    :   The type of the None singleton.

    `has_feedbacks: bool | Any | None`
    :   The type of the None singleton.

    `has_flags: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_agent_monitoring: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_app_start: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_assets: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_caches: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_db: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_http: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_mcp: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_queues: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_screen_load: bool | Any | None`
    :   The type of the None singleton.

    `has_insights_vitals: bool | Any | None`
    :   The type of the None singleton.

    `has_logs: bool | Any | None`
    :   The type of the None singleton.

    `has_minified_stack_trace: bool | Any | None`
    :   The type of the None singleton.

    `has_monitors: bool | Any | None`
    :   The type of the None singleton.

    `has_new_feedbacks: bool | Any | None`
    :   The type of the None singleton.

    `has_profiles: bool | Any | None`
    :   The type of the None singleton.

    `has_replays: bool | Any | None`
    :   The type of the None singleton.

    `has_sessions: bool | Any | None`
    :   The type of the None singleton.

    `has_trace_metrics: bool | Any | None`
    :   The type of the None singleton.

    `highlight_context: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `highlight_preset: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `highlight_tags: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `is_bookmarked: bool | Any | None`
    :   The type of the None singleton.

    `is_dynamically_sampled: bool | Any | None`
    :   The type of the None singleton.

    `is_internal: bool | Any | None`
    :   The type of the None singleton.

    `is_member: bool | Any | None`
    :   The type of the None singleton.

    `is_public: bool | Any | None`
    :   The type of the None singleton.

    `latest_release: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `options: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `organization: airbyte_agent_sdk.connectors.sentry.models.ProjectDetailOrganization | Any | None`
    :   The type of the None singleton.

    `platform: str | Any | None`
    :   The type of the None singleton.

    `platforms: list[str | None] | Any | None`
    :   The type of the None singleton.

    `plugins: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `processing_issues: int | Any | None`
    :   The type of the None singleton.

    `relay_pii_config: str | Any | None`
    :   The type of the None singleton.

    `resolve_age: int | Any | None`
    :   The type of the None singleton.

    `safe_fields: list[str | None] | Any | None`
    :   The type of the None singleton.

    `scrape_java_script: bool | Any | None`
    :   The type of the None singleton.

    `scrub_ip_addresses: bool | Any | None`
    :   The type of the None singleton.

    `secondary_grouping_config: str | Any | None`
    :   The type of the None singleton.

    `secondary_grouping_expiry: int | Any | None`
    :   The type of the None singleton.

    `security_token: str | Any | None`
    :   The type of the None singleton.

    `security_token_header: str | Any | None`
    :   The type of the None singleton.

    `seer_scanner_automation: bool | Any | None`
    :   The type of the None singleton.

    `sensitive_fields: list[str | None] | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `store_crash_reports: Any`
    :   The type of the None singleton.

    `subject_prefix: str | Any | None`
    :   The type of the None singleton.

    `subject_template: str | Any | None`
    :   The type of the None singleton.

    `symbol_sources: str | Any | None`
    :   The type of the None singleton.

    `team: airbyte_agent_sdk.connectors.sentry.models.ProjectDetailTeam | Any | None`
    :   The type of the None singleton.

    `teams: list[airbyte_agent_sdk.connectors.sentry.models.ProjectDetailTeamsItem | None] | Any | None`
    :   The type of the None singleton.

    `verify_ssl: bool | Any | None`
    :   The type of the None singleton.

<a id="ProjectDetailAvatar"></a>

`ProjectDetailAvatar(**data: Any)`
:   Project avatar information.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_type: str | Any | None`
    :   The type of the None singleton.

    `avatar_url: str | Any | None`
    :   The type of the None singleton.

    `avatar_uuid: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProjectDetailOrganization"></a>

`ProjectDetailOrganization(**data: Any)`
:   Organization this project belongs to.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

<a id="ProjectDetailTeam"></a>

`ProjectDetailTeam(**data: Any)`
:   Primary team for this project.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

<a id="ProjectDetailTeamsItem"></a>

`ProjectDetailTeamsItem(**data: Any)`
:   Nested schema for ProjectDetail.teams_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

<a id="ProjectOrganization"></a>

`ProjectOrganization(**data: Any)`
:   Organization this project belongs to.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

<a id="ProjectsListResultMeta"></a>

`ProjectsListResultMeta(**data: Any)`
:   Metadata for projects.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="ProjectsSearchData"></a>

`ProjectsSearchData(**data: Any)`
:   Search result data for projects entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="Release"></a>

`Release(**data: Any)`
:   A Sentry release.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `authors: list[airbyte_agent_sdk.connectors.sentry.models.ReleaseAuthorsItem | None] | Any | None`
    :   The type of the None singleton.

    `commit_count: int | Any | None`
    :   The type of the None singleton.

    `current_project_meta: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `data: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_released: str | Any | None`
    :   The type of the None singleton.

    `deploy_count: int | Any | None`
    :   The type of the None singleton.

    `first_event: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `last_commit: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `last_deploy: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `last_event: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `new_groups: int | Any | None`
    :   The type of the None singleton.

    `owner: str | Any | None`
    :   The type of the None singleton.

    `projects: list[airbyte_agent_sdk.connectors.sentry.models.ReleaseProjectsItem | None] | Any | None`
    :   The type of the None singleton.

    `ref: str | Any | None`
    :   The type of the None singleton.

    `short_version: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

    `user_agent: str | Any | None`
    :   The type of the None singleton.

    `version: str | Any | None`
    :   The type of the None singleton.

    `version_info: airbyte_agent_sdk.connectors.sentry.models.ReleaseVersioninfo | Any | None`
    :   The type of the None singleton.

<a id="ReleaseAuthorsItem"></a>

`ReleaseAuthorsItem(**data: Any)`
:   Nested schema for Release.authors_item
    
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

<a id="ReleaseProjectsItem"></a>

`ReleaseProjectsItem(**data: Any)`
:   Nested schema for Release.projects_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_health_data: bool | Any | None`
    :   The type of the None singleton.

    `id: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `new_groups: int | Any | None`
    :   The type of the None singleton.

    `platform: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

<a id="ReleaseVersioninfo"></a>

`ReleaseVersioninfo(**data: Any)`
:   Parsed version information.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `build_hash: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `package: str | Any | None`
    :   The type of the None singleton.

    `version: airbyte_agent_sdk.connectors.sentry.models.ReleaseVersioninfoVersion | Any | None`
    :   The type of the None singleton.

<a id="ReleaseVersioninfoVersion"></a>

`ReleaseVersioninfoVersion(**data: Any)`
:   Nested schema for ReleaseVersioninfo.version
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `build_code: str | Any | None`
    :   The type of the None singleton.

    `components: int | Any | None`
    :   The type of the None singleton.

    `major: int | Any | None`
    :   The type of the None singleton.

    `minor: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `patch: int | Any | None`
    :   The type of the None singleton.

    `pre: str | Any | None`
    :   The type of the None singleton.

    `raw: str | Any | None`
    :   The type of the None singleton.

<a id="ReleasesListResultMeta"></a>

`ReleasesListResultMeta(**data: Any)`
:   Metadata for releases.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="ReleasesSearchData"></a>

`ReleasesSearchData(**data: Any)`
:   Search result data for releases entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="SentryAuthConfig"></a>

`SentryAuthConfig(**data: Any)`
:   Authentication Token
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auth_token: str`
    :   Sentry authentication token. Log into Sentry and create one at Settings > Account > API > Auth Tokens.

    `model_config`
    :   The type of the None singleton.

<a id="SentryCheckResult"></a>

`SentryCheckResult(**data: Any)`
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

<a id="SentryExecuteResult"></a>

`SentryExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="SentryExecuteResultWithMeta"></a>

`SentryExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta[list[Event], EventsListResultMeta]
    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta[list[Issue], IssuesListResultMeta]
    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta[list[Project], ProjectsListResultMeta]
    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta[list[Release], ReleasesListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`SentryExecuteResultWithMeta[list[Event], EventsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="EventsListResult"></a>

`EventsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SentryExecuteResultWithMeta[list[Issue], IssuesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="IssuesListResult"></a>

`IssuesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SentryExecuteResultWithMeta[list[Project], ProjectsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProjectsListResult"></a>

`ProjectsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SentryExecuteResultWithMeta[list[Release], ReleasesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ReleasesListResult"></a>

`ReleasesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sentry.models.SentryExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SentryReplicationConfig"></a>

`SentryReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Sentry.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `organization: str`
    :   The slug of the organization to replicate data from.

    `project: str`
    :   The slug of the project to replicate data from.