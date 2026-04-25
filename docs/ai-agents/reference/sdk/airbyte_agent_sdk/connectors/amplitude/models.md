---
id: airbyte_agent_sdk-connectors-amplitude-models
title: airbyte_agent_sdk.connectors.amplitude.models
---

Module airbyte_agent_sdk.connectors.amplitude.models
====================================================
Pydantic models for amplitude connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="ActiveUsersData"></a>

`ActiveUsersData(**data: Any)`
:   Active or new user count data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `series: list[list[float]] | Any | None`
    :   The type of the None singleton.

    `series_collapsed: list[list[float]] | Any | None`
    :   The type of the None singleton.

    `series_labels: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `series_meta: list[airbyte_agent_sdk.connectors.amplitude.models.ActiveUsersDataSeriesmetaItem] | Any | None`
    :   The type of the None singleton.

    `x_values: list[str] | Any | None`
    :   The type of the None singleton.

<a id="ActiveUsersDataSeriesmetaItem"></a>

`ActiveUsersDataSeriesmetaItem(**data: Any)`
:   Nested schema for ActiveUsersData.seriesMeta_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `segment_index: int | Any`
    :   The type of the None singleton.

<a id="ActiveUsersResponse"></a>

`ActiveUsersResponse(**data: Any)`
:   Active users response wrapper
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.amplitude.models.ActiveUsersData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ActiveUsersSearchData"></a>

`ActiveUsersSearchData(**data: Any)`
:   Search result data for active_users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date: str | None`
    :   The date for which the active user data is reported

    `model_config`
    :   The type of the None singleton.

    `statistics: dict[str, typing.Any] | None`
    :   The statistics related to the active users for the given date

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

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[ActiveUsersSearchData]
    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[AnnotationsSearchData]
    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[AverageSessionLengthSearchData]
    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[CohortsSearchData]
    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[EventsListSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[ActiveUsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ActiveUsersSearchResult"></a>

`ActiveUsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AnnotationsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AnnotationsSearchResult"></a>

`AnnotationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AverageSessionLengthSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AverageSessionLengthSearchResult"></a>

`AverageSessionLengthSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CohortsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CohortsSearchResult"></a>

`CohortsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[EventsListSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="EventsListSearchResult"></a>

`EventsListSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AmplitudeAuthConfig"></a>

`AmplitudeAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Amplitude project API key. Find it in Settings > Projects in your Amplitude account.

    `model_config`
    :   The type of the None singleton.

    `secret_key: str`
    :   Your Amplitude project secret key. Find it in Settings > Projects in your Amplitude account.

<a id="AmplitudeCheckResult"></a>

`AmplitudeCheckResult(**data: Any)`
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

<a id="AmplitudeExecuteResult"></a>

`AmplitudeExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult[ActiveUsersData]
    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult[AverageSessionLengthData]
    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult[list[Annotation]]
    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult[list[Cohort]]
    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult[list[EventType]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="AmplitudeExecuteResultWithMeta"></a>

`AmplitudeExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`AmplitudeExecuteResult[ActiveUsersData](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ActiveUsersListResult"></a>

`ActiveUsersListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmplitudeExecuteResult[AverageSessionLengthData](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AverageSessionLengthListResult"></a>

`AverageSessionLengthListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmplitudeExecuteResult[list[Annotation]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AnnotationsListResult"></a>

`AnnotationsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmplitudeExecuteResult[list[Cohort]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CohortsListResult"></a>

`CohortsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmplitudeExecuteResult[list[EventType]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="EventsListListResult"></a>

`EventsListListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AmplitudeReplicationConfig"></a>

`AmplitudeReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Amplitude.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ. Any data before this date will not be replicated.

<a id="Annotation"></a>

`Annotation(**data: Any)`
:   A chart annotation object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date: str | Any | None`
    :   The type of the None singleton.

    `details: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `label: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AnnotationGetResponse"></a>

`AnnotationGetResponse(**data: Any)`
:   Single annotation response
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.amplitude.models.AnnotationV3 | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AnnotationV3"></a>

`AnnotationV3(**data: Any)`
:   A chart annotation object (v3 API format)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category: airbyte_agent_sdk.connectors.amplitude.models.AnnotationV3Category | Any | None`
    :   The type of the None singleton.

    `chart_id: str | Any | None`
    :   The type of the None singleton.

    `details: str | Any | None`
    :   The type of the None singleton.

    `end: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `label: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: str | Any | None`
    :   The type of the None singleton.

<a id="AnnotationV3Category"></a>

`AnnotationV3Category(**data: Any)`
:   The annotation category
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category: str | Any`
    :   Category name

    `id: int | Any`
    :   Category ID

    `model_config`
    :   The type of the None singleton.

<a id="AnnotationsList"></a>

`AnnotationsList(**data: Any)`
:   List of annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.amplitude.models.Annotation] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AnnotationsSearchData"></a>

`AnnotationsSearchData(**data: Any)`
:   Search result data for annotations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date: str | None`
    :   The date when the annotation was made

    `details: str | None`
    :   Additional details or information related to the annotation

    `id: int | None`
    :   The unique identifier for the annotation

    `label: str | None`
    :   The label assigned to the annotation

    `model_config`
    :   The type of the None singleton.

<a id="AverageSessionLengthData"></a>

`AverageSessionLengthData(**data: Any)`
:   Average session length data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `series: list[list[float]] | Any | None`
    :   The type of the None singleton.

    `series_collapsed: list[list[airbyte_agent_sdk.connectors.amplitude.models.AverageSessionLengthDataSeriescollapsedItemItem]] | Any | None`
    :   The type of the None singleton.

    `series_meta: list[airbyte_agent_sdk.connectors.amplitude.models.AverageSessionLengthDataSeriesmetaItem] | Any | None`
    :   The type of the None singleton.

    `x_values: list[str] | Any | None`
    :   The type of the None singleton.

<a id="AverageSessionLengthDataSeriescollapsedItemItem"></a>

`AverageSessionLengthDataSeriescollapsedItemItem(**data: Any)`
:   Nested schema for AverageSessionLengthData.seriesCollapsed_item_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `set_id: str | Any`
    :   The type of the None singleton.

    `value: float | Any`
    :   The type of the None singleton.

<a id="AverageSessionLengthDataSeriesmetaItem"></a>

`AverageSessionLengthDataSeriesmetaItem(**data: Any)`
:   Nested schema for AverageSessionLengthData.seriesMeta_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `segment_index: int | Any`
    :   The type of the None singleton.

    `session_index: int | Any`
    :   The type of the None singleton.

<a id="AverageSessionLengthResponse"></a>

`AverageSessionLengthResponse(**data: Any)`
:   Average session length response wrapper
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.amplitude.models.AverageSessionLengthData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AverageSessionLengthSearchData"></a>

`AverageSessionLengthSearchData(**data: Any)`
:   Search result data for average_session_length entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date: str | None`
    :   The date on which the session occurred

    `length: float | None`
    :   The duration of the session in seconds

    `model_config`
    :   The type of the None singleton.

<a id="Cohort"></a>

`Cohort(**data: Any)`
:   A user cohort object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_id: int | Any | None`
    :   The type of the None singleton.

    `archived: bool | Any | None`
    :   The type of the None singleton.

    `chart_id: str | Any | None`
    :   The type of the None singleton.

    `cohort_definition_type: str | Any | None`
    :   The type of the None singleton.

    `cohort_output_type: str | Any | None`
    :   The type of the None singleton.

    `created_at: int | Any | None`
    :   The type of the None singleton.

    `definition: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `edit_id: str | Any | None`
    :   The type of the None singleton.

    `finished: bool | Any | None`
    :   The type of the None singleton.

    `hidden: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `include_data_app_types: list[str] | Any | None`
    :   The type of the None singleton.

    `is_generated_content: bool | Any | None`
    :   The type of the None singleton.

    `is_official_content: bool | Any | None`
    :   The type of the None singleton.

    `is_predictive: bool | Any | None`
    :   The type of the None singleton.

    `last_computed: int | Any | None`
    :   The type of the None singleton.

    `last_mod: int | Any | None`
    :   The type of the None singleton.

    `last_viewed: int | Any | None`
    :   The type of the None singleton.

    `location_id: str | Any | None`
    :   The type of the None singleton.

    `metadata: list[str] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `owners: list[str] | Any | None`
    :   The type of the None singleton.

    `per_app_metadata: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `popularity: int | Any | None`
    :   The type of the None singleton.

    `published: bool | Any | None`
    :   The type of the None singleton.

    `shortcut_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `size: int | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `view_count: int | Any | None`
    :   The type of the None singleton.

    `viewers: list[str] | Any | None`
    :   The type of the None singleton.

<a id="CohortGetResponse"></a>

`CohortGetResponse(**data: Any)`
:   Single cohort response wrapper
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cohort: airbyte_agent_sdk.connectors.amplitude.models.Cohort | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CohortsList"></a>

`CohortsList(**data: Any)`
:   List of cohorts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cohorts: list[airbyte_agent_sdk.connectors.amplitude.models.Cohort] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CohortsSearchData"></a>

`CohortsSearchData(**data: Any)`
:   Search result data for cohorts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_id: int | None`
    :   The unique identifier of the application

    `archived: bool | None`
    :   Indicates if the cohort data is archived

    `chart_id: str | None`
    :   The identifier of the chart associated with the cohort

    `created_at: int | None`
    :   The timestamp when the cohort was created

    `definition: dict[str, typing.Any] | None`
    :   The specific definition or criteria for the cohort

    `description: str | None`
    :   A brief explanation or summary of the cohort

    `edit_id: str | None`
    :   The ID for editing purposes or version control

    `finished: bool | None`
    :   Indicates if the cohort data has been finalized

    `hidden: bool | None`
    :   Flag to determine if the cohort is hidden from view

    `id: str | None`
    :   The unique identifier for the cohort

    `is_official_content: bool | None`
    :   Indicates if the cohort data is official content

    `is_predictive: bool | None`
    :   Flag to indicate if the cohort is predictive

    `last_computed: int | None`
    :   Timestamp of the last computation of cohort data

    `last_mod: int | None`
    :   Timestamp of the last modification made to the cohort

    `last_viewed: int | None`
    :   Timestamp when the cohort was last viewed

    `location_id: str | None`
    :   Identifier of the location associated with the cohort

    `metadata: list[typing.Any] | None`
    :   Additional information or data related to the cohort

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name or title of the cohort

    `owners: list[typing.Any] | None`
    :   The owners or administrators of the cohort

    `popularity: int | None`
    :   Popularity rank or score of the cohort

    `published: bool | None`
    :   Status indicating if the cohort data is published

    `shortcut_ids: list[typing.Any] | None`
    :   Identifiers of any shortcuts associated with the cohort

    `size: int | None`
    :   Size or scale of the cohort data

    `type_: str | None`
    :   The type or category of the cohort

    `view_count: int | None`
    :   The total count of views on the cohort data

    `viewers: list[typing.Any] | None`
    :   Users or viewers who have access to the cohort data

<a id="EventType"></a>

`EventType(**data: Any)`
:   An event type definition with weekly totals
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `autohidden: bool | Any | None`
    :   The type of the None singleton.

    `clusters_hidden: bool | Any | None`
    :   The type of the None singleton.

    `deleted: bool | Any | None`
    :   The type of the None singleton.

    `display: str | Any | None`
    :   The type of the None singleton.

    `flow_hidden: bool | Any | None`
    :   The type of the None singleton.

    `hidden: bool | Any | None`
    :   The type of the None singleton.

    `id: float | Any`
    :   The type of the None singleton.

    `in_waitroom: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `non_active: bool | Any | None`
    :   The type of the None singleton.

    `timeline_hidden: bool | Any | None`
    :   The type of the None singleton.

    `totals: float | Any | None`
    :   The type of the None singleton.

    `totals_delta: float | Any | None`
    :   The type of the None singleton.

    `value: str | Any | None`
    :   The type of the None singleton.

    `waitroom_approved: bool | Any | None`
    :   The type of the None singleton.

<a id="EventsListResponse"></a>

`EventsListResponse(**data: Any)`
:   List of event types
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.amplitude.models.EventType] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="EventsListSearchData"></a>

`EventsListSearchData(**data: Any)`
:   Search result data for events_list entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `autohidden: bool | None`
    :   Whether the event is auto-hidden

    `clusters_hidden: bool | None`
    :   Whether the event is hidden from clusters

    `deleted: bool | None`
    :   Whether the event is deleted

    `display: str | None`
    :   Display name of the event

    `flow_hidden: bool | None`
    :   Whether the event is hidden from Pathfinder

    `hidden: bool | None`
    :   Whether the event is hidden

    `id: float | None`
    :   Unique identifier for the event type

    `in_waitroom: bool | None`
    :   Whether the event is in the waitroom

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the event type

    `non_active: bool | None`
    :   Whether the event is marked as inactive

    `timeline_hidden: Any`
    :   Whether the event is hidden from the timeline

    `totals: float | None`
    :   Total number of times the event occurred this week

    `totals_delta: float | None`
    :   Change in totals from the previous period

    `value: str | None`
    :   Raw event name in the data