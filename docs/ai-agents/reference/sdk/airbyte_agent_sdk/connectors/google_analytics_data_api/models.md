---
id: airbyte_agent_sdk-connectors-google_analytics_data_api-models
title: airbyte_agent_sdk.connectors.google_analytics_data_api.models
---

Module airbyte_agent_sdk.connectors.google_analytics_data_api.models
====================================================================
Pydantic models for google-analytics-data-api connector.

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

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[DailyActiveUsersSearchData]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[DevicesSearchData]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[FourWeeklyActiveUsersSearchData]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[LocationsSearchData]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[PagesSearchData]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[TrafficSourcesSearchData]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[WebsiteOverviewSearchData]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[WeeklyActiveUsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[DailyActiveUsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DailyActiveUsersSearchResult"></a>

`DailyActiveUsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[DevicesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DevicesSearchResult"></a>

`DevicesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[FourWeeklyActiveUsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersSearchResult"></a>

`FourWeeklyActiveUsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[LocationsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="LocationsSearchResult"></a>

`LocationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[PagesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PagesSearchResult"></a>

`PagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TrafficSourcesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TrafficSourcesSearchResult"></a>

`TrafficSourcesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[WebsiteOverviewSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WebsiteOverviewSearchResult"></a>

`WebsiteOverviewSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[WeeklyActiveUsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersSearchResult"></a>

`WeeklyActiveUsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="DailyActiveUsersListResultMeta"></a>

`DailyActiveUsersListResultMeta(**data: Any)`
:   Metadata for daily_active_users.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `row_count: int | Any`
    :   The type of the None singleton.

<a id="DailyActiveUsersRequest"></a>

`DailyActiveUsersRequest(**data: Any)`
:   Request body for daily active users report
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.DailyActiveUsersRequestDaterangesItem] | Any`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.DailyActiveUsersRequestDimensionsItem] | Any`
    :   The type of the None singleton.

    `keep_empty_rows: bool | Any`
    :   The type of the None singleton.

    `limit: int | Any`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.DailyActiveUsersRequestMetricsItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `return_property_quota: bool | Any`
    :   The type of the None singleton.

<a id="DailyActiveUsersRequestDaterangesItem"></a>

`DailyActiveUsersRequestDaterangesItem(**data: Any)`
:   Nested schema for DailyActiveUsersRequest.dateRanges_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_date: str | Any`
    :   End date in YYYY-MM-DD format or relative (e.g., today)

    `model_config`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo)

<a id="DailyActiveUsersRequestDimensionsItem"></a>

`DailyActiveUsersRequestDimensionsItem(**data: Any)`
:   Nested schema for DailyActiveUsersRequest.dimensions_item
    
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

<a id="DailyActiveUsersRequestMetricsItem"></a>

`DailyActiveUsersRequestMetricsItem(**data: Any)`
:   Nested schema for DailyActiveUsersRequest.metrics_item
    
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

<a id="DailyActiveUsersSearchData"></a>

`DailyActiveUsersSearchData(**data: Any)`
:   Search result data for daily_active_users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active1_day_users: int | None`
    :   Number of distinct users active in the last 1 day

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `model_config`
    :   The type of the None singleton.

    `property_id: str`
    :   GA4 property ID

    `start_date: str | None`
    :   Start date of the reporting period

<a id="DevicesListResultMeta"></a>

`DevicesListResultMeta(**data: Any)`
:   Metadata for devices.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `row_count: int | Any`
    :   The type of the None singleton.

<a id="DevicesRequest"></a>

`DevicesRequest(**data: Any)`
:   Request body for devices report
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.DevicesRequestDaterangesItem] | Any`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.DevicesRequestDimensionsItem] | Any`
    :   The type of the None singleton.

    `keep_empty_rows: bool | Any`
    :   The type of the None singleton.

    `limit: int | Any`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.DevicesRequestMetricsItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `return_property_quota: bool | Any`
    :   The type of the None singleton.

<a id="DevicesRequestDaterangesItem"></a>

`DevicesRequestDaterangesItem(**data: Any)`
:   Nested schema for DevicesRequest.dateRanges_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_date: str | Any`
    :   End date in YYYY-MM-DD format or relative (e.g., today)

    `model_config`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo)

<a id="DevicesRequestDimensionsItem"></a>

`DevicesRequestDimensionsItem(**data: Any)`
:   Nested schema for DevicesRequest.dimensions_item
    
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

<a id="DevicesRequestMetricsItem"></a>

`DevicesRequestMetricsItem(**data: Any)`
:   Nested schema for DevicesRequest.metrics_item
    
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

<a id="DevicesSearchData"></a>

`DevicesSearchData(**data: Any)`
:   Search result data for devices entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `average_session_duration: float | None`
    :   Average duration of sessions in seconds

    `bounce_rate: float | None`
    :   Percentage of sessions that were single-page with no interaction

    `browser: str | None`
    :   The web browser used (e.g., Chrome, Safari, Firefox)

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `device_category: str | None`
    :   The device category (desktop, mobile, tablet)

    `end_date: str | None`
    :   End date of the reporting period

    `model_config`
    :   The type of the None singleton.

    `new_users: int | None`
    :   Number of first-time users

    `operating_system: str | None`
    :   The operating system used (e.g., Windows, iOS, Android)

    `property_id: str`
    :   GA4 property ID

    `screen_page_views: int | None`
    :   Total number of screen or page views

    `screen_page_views_per_session: float | None`
    :   Average page views per session

    `sessions: int | None`
    :   Total number of sessions

    `sessions_per_user: float | None`
    :   Average number of sessions per user

    `start_date: str | None`
    :   Start date of the reporting period

    `total_users: int | None`
    :   Total number of unique users

<a id="DimensionHeader"></a>

`DimensionHeader(**data: Any)`
:   DimensionHeader type definition
    
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

<a id="DimensionValue"></a>

`DimensionValue(**data: Any)`
:   DimensionValue type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `value: str | Any`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersListResultMeta"></a>

`FourWeeklyActiveUsersListResultMeta(**data: Any)`
:   Metadata for four_weekly_active_users.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `row_count: int | Any`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersRequest"></a>

`FourWeeklyActiveUsersRequest(**data: Any)`
:   Request body for four-weekly active users report
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.FourWeeklyActiveUsersRequestDaterangesItem] | Any`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.FourWeeklyActiveUsersRequestDimensionsItem] | Any`
    :   The type of the None singleton.

    `keep_empty_rows: bool | Any`
    :   The type of the None singleton.

    `limit: int | Any`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.FourWeeklyActiveUsersRequestMetricsItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `return_property_quota: bool | Any`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersRequestDaterangesItem"></a>

`FourWeeklyActiveUsersRequestDaterangesItem(**data: Any)`
:   Nested schema for FourWeeklyActiveUsersRequest.dateRanges_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_date: str | Any`
    :   End date in YYYY-MM-DD format or relative (e.g., today)

    `model_config`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo)

<a id="FourWeeklyActiveUsersRequestDimensionsItem"></a>

`FourWeeklyActiveUsersRequestDimensionsItem(**data: Any)`
:   Nested schema for FourWeeklyActiveUsersRequest.dimensions_item
    
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

<a id="FourWeeklyActiveUsersRequestMetricsItem"></a>

`FourWeeklyActiveUsersRequestMetricsItem(**data: Any)`
:   Nested schema for FourWeeklyActiveUsersRequest.metrics_item
    
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

<a id="FourWeeklyActiveUsersSearchData"></a>

`FourWeeklyActiveUsersSearchData(**data: Any)`
:   Search result data for four_weekly_active_users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active28_day_users: int | None`
    :   Number of distinct users active in the last 28 days

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `model_config`
    :   The type of the None singleton.

    `property_id: str`
    :   GA4 property ID

    `start_date: str | None`
    :   Start date of the reporting period

<a id="GoogleAnalyticsDataApiAuthConfig"></a>

`GoogleAnalyticsDataApiAuthConfig(**data: Any)`
:   OAuth 2.0 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   OAuth 2.0 Client ID from Google Cloud Console

    `client_secret: str`
    :   OAuth 2.0 Client Secret from Google Cloud Console

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   OAuth 2.0 Refresh Token for obtaining new access tokens

<a id="GoogleAnalyticsDataApiCheckResult"></a>

`GoogleAnalyticsDataApiCheckResult(**data: Any)`
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

<a id="GoogleAnalyticsDataApiExecuteResult"></a>

`GoogleAnalyticsDataApiExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="GoogleAnalyticsDataApiExecuteResultWithMeta"></a>

`GoogleAnalyticsDataApiExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], DailyActiveUsersListResultMeta]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], DevicesListResultMeta]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], FourWeeklyActiveUsersListResultMeta]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], LocationsListResultMeta]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], PagesListResultMeta]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], TrafficSourcesListResultMeta]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], WebsiteOverviewListResultMeta]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], WeeklyActiveUsersListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], DailyActiveUsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DailyActiveUsersListResult"></a>

`DailyActiveUsersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], DevicesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DevicesListResult"></a>

`DevicesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], FourWeeklyActiveUsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersListResult"></a>

`FourWeeklyActiveUsersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], LocationsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="LocationsListResult"></a>

`LocationsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], PagesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PagesListResult"></a>

`PagesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], TrafficSourcesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TrafficSourcesListResult"></a>

`TrafficSourcesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], WebsiteOverviewListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WebsiteOverviewListResult"></a>

`WebsiteOverviewListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], WeeklyActiveUsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersListResult"></a>

`WeeklyActiveUsersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GoogleAnalyticsDataApiReplicationConfig"></a>

`GoogleAnalyticsDataApiReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Google Analytics.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `property_ids: str`
    :   A list of GA4 Property IDs to replicate data from.

<a id="LocationsListResultMeta"></a>

`LocationsListResultMeta(**data: Any)`
:   Metadata for locations.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `row_count: int | Any`
    :   The type of the None singleton.

<a id="LocationsRequest"></a>

`LocationsRequest(**data: Any)`
:   Request body for locations report
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.LocationsRequestDaterangesItem] | Any`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.LocationsRequestDimensionsItem] | Any`
    :   The type of the None singleton.

    `keep_empty_rows: bool | Any`
    :   The type of the None singleton.

    `limit: int | Any`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.LocationsRequestMetricsItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `return_property_quota: bool | Any`
    :   The type of the None singleton.

<a id="LocationsRequestDaterangesItem"></a>

`LocationsRequestDaterangesItem(**data: Any)`
:   Nested schema for LocationsRequest.dateRanges_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_date: str | Any`
    :   End date in YYYY-MM-DD format or relative (e.g., today)

    `model_config`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo)

<a id="LocationsRequestDimensionsItem"></a>

`LocationsRequestDimensionsItem(**data: Any)`
:   Nested schema for LocationsRequest.dimensions_item
    
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

<a id="LocationsRequestMetricsItem"></a>

`LocationsRequestMetricsItem(**data: Any)`
:   Nested schema for LocationsRequest.metrics_item
    
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

<a id="LocationsSearchData"></a>

`LocationsSearchData(**data: Any)`
:   Search result data for locations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `average_session_duration: float | None`
    :   Average duration of sessions in seconds

    `bounce_rate: float | None`
    :   Percentage of sessions that were single-page with no interaction

    `city: str | None`
    :   The city of the user

    `country: str | None`
    :   The country of the user

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `model_config`
    :   The type of the None singleton.

    `new_users: int | None`
    :   Number of first-time users

    `property_id: str`
    :   GA4 property ID

    `region: str | None`
    :   The region (state/province) of the user

    `screen_page_views: int | None`
    :   Total number of screen or page views

    `screen_page_views_per_session: float | None`
    :   Average page views per session

    `sessions: int | None`
    :   Total number of sessions

    `sessions_per_user: float | None`
    :   Average number of sessions per user

    `start_date: str | None`
    :   Start date of the reporting period

    `total_users: int | None`
    :   Total number of unique users

<a id="MetricHeader"></a>

`MetricHeader(**data: Any)`
:   MetricHeader type definition
    
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

    `type_: str | Any`
    :   The type of the None singleton.

<a id="MetricValue"></a>

`MetricValue(**data: Any)`
:   MetricValue type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `value: str | Any`
    :   The type of the None singleton.

<a id="PagesListResultMeta"></a>

`PagesListResultMeta(**data: Any)`
:   Metadata for pages.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `row_count: int | Any`
    :   The type of the None singleton.

<a id="PagesRequest"></a>

`PagesRequest(**data: Any)`
:   Request body for pages report
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.PagesRequestDaterangesItem] | Any`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.PagesRequestDimensionsItem] | Any`
    :   The type of the None singleton.

    `keep_empty_rows: bool | Any`
    :   The type of the None singleton.

    `limit: int | Any`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.PagesRequestMetricsItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `return_property_quota: bool | Any`
    :   The type of the None singleton.

<a id="PagesRequestDaterangesItem"></a>

`PagesRequestDaterangesItem(**data: Any)`
:   Nested schema for PagesRequest.dateRanges_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_date: str | Any`
    :   End date in YYYY-MM-DD format or relative (e.g., today)

    `model_config`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo)

<a id="PagesRequestDimensionsItem"></a>

`PagesRequestDimensionsItem(**data: Any)`
:   Nested schema for PagesRequest.dimensions_item
    
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

<a id="PagesRequestMetricsItem"></a>

`PagesRequestMetricsItem(**data: Any)`
:   Nested schema for PagesRequest.metrics_item
    
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

<a id="PagesSearchData"></a>

`PagesSearchData(**data: Any)`
:   Search result data for pages entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bounce_rate: float | None`
    :   Percentage of sessions that were single-page with no interaction

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `host_name: str | None`
    :   The hostname of the page

    `model_config`
    :   The type of the None singleton.

    `page_path_plus_query_string: str | None`
    :   The page path and query string

    `property_id: str`
    :   GA4 property ID

    `screen_page_views: int | None`
    :   Total number of screen or page views

    `start_date: str | None`
    :   Start date of the reporting period

<a id="Row"></a>

`Row(**data: Any)`
:   Row type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `dimension_values: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.DimensionValue] | Any`
    :   The type of the None singleton.

    `metric_values: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.MetricValue] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="RunReportResponse"></a>

`RunReportResponse(**data: Any)`
:   Response from the runReport endpoint
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `dimension_headers: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.DimensionHeader] | Any`
    :   The type of the None singleton.

    `kind: str | Any`
    :   The type of the None singleton.

    `metadata: airbyte_agent_sdk.connectors.google_analytics_data_api.models.RunReportResponseMetadata | Any`
    :   The type of the None singleton.

    `metric_headers: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.MetricHeader] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `property_quota: airbyte_agent_sdk.connectors.google_analytics_data_api.models.RunReportResponsePropertyquota | Any`
    :   The type of the None singleton.

    `row_count: int | Any`
    :   The type of the None singleton.

    `rows: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.Row] | Any`
    :   The type of the None singleton.

<a id="RunReportResponseMetadata"></a>

`RunReportResponseMetadata(**data: Any)`
:   Nested schema for RunReportResponse.metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency_code: str | Any`
    :   The currency code used in this report

    `model_config`
    :   The type of the None singleton.

    `time_zone: str | Any`
    :   The property's current timezone

<a id="RunReportResponsePropertyquota"></a>

`RunReportResponsePropertyquota(**data: Any)`
:   Quota status for this Analytics property
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `concurrent_requests: airbyte_agent_sdk.connectors.google_analytics_data_api.models.RunReportResponsePropertyquotaConcurrentrequests | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `potentially_thresholded_requests_per_hour: airbyte_agent_sdk.connectors.google_analytics_data_api.models.RunReportResponsePropertyquotaPotentiallythresholdedrequestsperhour | Any`
    :   The type of the None singleton.

    `server_errors_per_project_per_hour: airbyte_agent_sdk.connectors.google_analytics_data_api.models.RunReportResponsePropertyquotaServererrorsperprojectperhour | Any`
    :   The type of the None singleton.

    `tokens_per_day: airbyte_agent_sdk.connectors.google_analytics_data_api.models.RunReportResponsePropertyquotaTokensperday | Any`
    :   The type of the None singleton.

    `tokens_per_hour: airbyte_agent_sdk.connectors.google_analytics_data_api.models.RunReportResponsePropertyquotaTokensperhour | Any`
    :   The type of the None singleton.

    `tokens_per_project_per_hour: airbyte_agent_sdk.connectors.google_analytics_data_api.models.RunReportResponsePropertyquotaTokensperprojectperhour | Any`
    :   The type of the None singleton.

<a id="RunReportResponsePropertyquotaConcurrentrequests"></a>

`RunReportResponsePropertyquotaConcurrentrequests(**data: Any)`
:   Nested schema for RunReportResponsePropertyquota.concurrentRequests
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `consumed: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `remaining: int | Any`
    :   The type of the None singleton.

<a id="RunReportResponsePropertyquotaPotentiallythresholdedrequestsperhour"></a>

`RunReportResponsePropertyquotaPotentiallythresholdedrequestsperhour(**data: Any)`
:   Nested schema for RunReportResponsePropertyquota.potentiallyThresholdedRequestsPerHour
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `consumed: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `remaining: int | Any`
    :   The type of the None singleton.

<a id="RunReportResponsePropertyquotaServererrorsperprojectperhour"></a>

`RunReportResponsePropertyquotaServererrorsperprojectperhour(**data: Any)`
:   Nested schema for RunReportResponsePropertyquota.serverErrorsPerProjectPerHour
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `consumed: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `remaining: int | Any`
    :   The type of the None singleton.

<a id="RunReportResponsePropertyquotaTokensperday"></a>

`RunReportResponsePropertyquotaTokensperday(**data: Any)`
:   Nested schema for RunReportResponsePropertyquota.tokensPerDay
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `consumed: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `remaining: int | Any`
    :   The type of the None singleton.

<a id="RunReportResponsePropertyquotaTokensperhour"></a>

`RunReportResponsePropertyquotaTokensperhour(**data: Any)`
:   Nested schema for RunReportResponsePropertyquota.tokensPerHour
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `consumed: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `remaining: int | Any`
    :   The type of the None singleton.

<a id="RunReportResponsePropertyquotaTokensperprojectperhour"></a>

`RunReportResponsePropertyquotaTokensperprojectperhour(**data: Any)`
:   Nested schema for RunReportResponsePropertyquota.tokensPerProjectPerHour
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `consumed: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `remaining: int | Any`
    :   The type of the None singleton.

<a id="TrafficSourcesListResultMeta"></a>

`TrafficSourcesListResultMeta(**data: Any)`
:   Metadata for traffic_sources.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `row_count: int | Any`
    :   The type of the None singleton.

<a id="TrafficSourcesRequest"></a>

`TrafficSourcesRequest(**data: Any)`
:   Request body for traffic sources report
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.TrafficSourcesRequestDaterangesItem] | Any`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.TrafficSourcesRequestDimensionsItem] | Any`
    :   The type of the None singleton.

    `keep_empty_rows: bool | Any`
    :   The type of the None singleton.

    `limit: int | Any`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.TrafficSourcesRequestMetricsItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `return_property_quota: bool | Any`
    :   The type of the None singleton.

<a id="TrafficSourcesRequestDaterangesItem"></a>

`TrafficSourcesRequestDaterangesItem(**data: Any)`
:   Nested schema for TrafficSourcesRequest.dateRanges_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_date: str | Any`
    :   End date in YYYY-MM-DD format or relative (e.g., today)

    `model_config`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo)

<a id="TrafficSourcesRequestDimensionsItem"></a>

`TrafficSourcesRequestDimensionsItem(**data: Any)`
:   Nested schema for TrafficSourcesRequest.dimensions_item
    
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

<a id="TrafficSourcesRequestMetricsItem"></a>

`TrafficSourcesRequestMetricsItem(**data: Any)`
:   Nested schema for TrafficSourcesRequest.metrics_item
    
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

<a id="TrafficSourcesSearchData"></a>

`TrafficSourcesSearchData(**data: Any)`
:   Search result data for traffic_sources entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `average_session_duration: float | None`
    :   Average duration of sessions in seconds

    `bounce_rate: float | None`
    :   Percentage of sessions that were single-page with no interaction

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `model_config`
    :   The type of the None singleton.

    `new_users: int | None`
    :   Number of first-time users

    `property_id: str`
    :   GA4 property ID

    `screen_page_views: int | None`
    :   Total number of screen or page views

    `screen_page_views_per_session: float | None`
    :   Average page views per session

    `session_medium: str | None`
    :   The medium of the traffic source (e.g., organic, cpc, referral)

    `session_source: str | None`
    :   The source of the traffic (e.g., google, direct)

    `sessions: int | None`
    :   Total number of sessions

    `sessions_per_user: float | None`
    :   Average number of sessions per user

    `start_date: str | None`
    :   Start date of the reporting period

    `total_users: int | None`
    :   Total number of unique users

<a id="WebsiteOverviewListResultMeta"></a>

`WebsiteOverviewListResultMeta(**data: Any)`
:   Metadata for website_overview.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `row_count: int | Any`
    :   The type of the None singleton.

<a id="WebsiteOverviewRequest"></a>

`WebsiteOverviewRequest(**data: Any)`
:   Request body for website overview report
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.WebsiteOverviewRequestDaterangesItem] | Any`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.WebsiteOverviewRequestDimensionsItem] | Any`
    :   The type of the None singleton.

    `keep_empty_rows: bool | Any`
    :   The type of the None singleton.

    `limit: int | Any`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.WebsiteOverviewRequestMetricsItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `return_property_quota: bool | Any`
    :   The type of the None singleton.

<a id="WebsiteOverviewRequestDaterangesItem"></a>

`WebsiteOverviewRequestDaterangesItem(**data: Any)`
:   Nested schema for WebsiteOverviewRequest.dateRanges_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_date: str | Any`
    :   End date in YYYY-MM-DD format or relative (e.g., today)

    `model_config`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo)

<a id="WebsiteOverviewRequestDimensionsItem"></a>

`WebsiteOverviewRequestDimensionsItem(**data: Any)`
:   Nested schema for WebsiteOverviewRequest.dimensions_item
    
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

<a id="WebsiteOverviewRequestMetricsItem"></a>

`WebsiteOverviewRequestMetricsItem(**data: Any)`
:   Nested schema for WebsiteOverviewRequest.metrics_item
    
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

<a id="WebsiteOverviewSearchData"></a>

`WebsiteOverviewSearchData(**data: Any)`
:   Search result data for website_overview entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `average_session_duration: float | None`
    :   Average duration of sessions in seconds

    `bounce_rate: float | None`
    :   Percentage of sessions that were single-page with no interaction

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `model_config`
    :   The type of the None singleton.

    `new_users: int | None`
    :   Number of first-time users

    `property_id: str`
    :   GA4 property ID

    `screen_page_views: int | None`
    :   Total number of screen or page views

    `screen_page_views_per_session: float | None`
    :   Average page views per session

    `sessions: int | None`
    :   Total number of sessions

    `sessions_per_user: float | None`
    :   Average number of sessions per user

    `start_date: str | None`
    :   Start date of the reporting period

    `total_users: int | None`
    :   Total number of unique users

<a id="WeeklyActiveUsersListResultMeta"></a>

`WeeklyActiveUsersListResultMeta(**data: Any)`
:   Metadata for weekly_active_users.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `row_count: int | Any`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersRequest"></a>

`WeeklyActiveUsersRequest(**data: Any)`
:   Request body for weekly active users report
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.WeeklyActiveUsersRequestDaterangesItem] | Any`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.WeeklyActiveUsersRequestDimensionsItem] | Any`
    :   The type of the None singleton.

    `keep_empty_rows: bool | Any`
    :   The type of the None singleton.

    `limit: int | Any`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.models.WeeklyActiveUsersRequestMetricsItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `return_property_quota: bool | Any`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersRequestDaterangesItem"></a>

`WeeklyActiveUsersRequestDaterangesItem(**data: Any)`
:   Nested schema for WeeklyActiveUsersRequest.dateRanges_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_date: str | Any`
    :   End date in YYYY-MM-DD format or relative (e.g., today)

    `model_config`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo)

<a id="WeeklyActiveUsersRequestDimensionsItem"></a>

`WeeklyActiveUsersRequestDimensionsItem(**data: Any)`
:   Nested schema for WeeklyActiveUsersRequest.dimensions_item
    
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

<a id="WeeklyActiveUsersRequestMetricsItem"></a>

`WeeklyActiveUsersRequestMetricsItem(**data: Any)`
:   Nested schema for WeeklyActiveUsersRequest.metrics_item
    
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

<a id="WeeklyActiveUsersSearchData"></a>

`WeeklyActiveUsersSearchData(**data: Any)`
:   Search result data for weekly_active_users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active7_day_users: int | None`
    :   Number of distinct users active in the last 7 days

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `model_config`
    :   The type of the None singleton.

    `property_id: str`
    :   GA4 property ID

    `start_date: str | None`
    :   Start date of the reporting period