---
id: airbyte_agent_sdk-connectors-google_analytics_data_api-types
title: airbyte_agent_sdk.connectors.google_analytics_data_api.types
---

Module airbyte_agent_sdk.connectors.google_analytics_data_api.types
===================================================================
Type definitions for google-analytics-data-api connector.

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

<a id="DailyActiveUsersAndCondition"></a>

`DailyActiveUsersAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersAnyCondition]`
    :   The type of the None singleton.

<a id="DailyActiveUsersAnyCondition"></a>

`DailyActiveUsersAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersAnyValueFilter`
    :   The type of the None singleton.

<a id="DailyActiveUsersAnyValueFilter"></a>

`DailyActiveUsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active1_day_users: Any`
    :   Number of distinct users active in the last 1 day

    `date: Any`
    :   Date of the report row in YYYYMMDD format

    `end_date: Any`
    :   End date of the reporting period

    `property_id: Any`
    :   GA4 property ID

    `start_date: Any`
    :   Start date of the reporting period

<a id="DailyActiveUsersContainsCondition"></a>

`DailyActiveUsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersAnyValueFilter`
    :   The type of the None singleton.

<a id="DailyActiveUsersEqCondition"></a>

`DailyActiveUsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="DailyActiveUsersFuzzyCondition"></a>

`DailyActiveUsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersStringFilter`
    :   The type of the None singleton.

<a id="DailyActiveUsersGtCondition"></a>

`DailyActiveUsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="DailyActiveUsersGteCondition"></a>

`DailyActiveUsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="DailyActiveUsersInCondition"></a>

`DailyActiveUsersInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersInFilter`
    :   The type of the None singleton.

<a id="DailyActiveUsersInFilter"></a>

`DailyActiveUsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active1_day_users: list[int]`
    :   Number of distinct users active in the last 1 day

    `date: list[str]`
    :   Date of the report row in YYYYMMDD format

    `end_date: list[str]`
    :   End date of the reporting period

    `property_id: list[str]`
    :   GA4 property ID

    `start_date: list[str]`
    :   Start date of the reporting period

<a id="DailyActiveUsersKeywordCondition"></a>

`DailyActiveUsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersStringFilter`
    :   The type of the None singleton.

<a id="DailyActiveUsersLikeCondition"></a>

`DailyActiveUsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersStringFilter`
    :   The type of the None singleton.

<a id="DailyActiveUsersListParams"></a>

`DailyActiveUsersListParams(*args, **kwargs)`
:   Parameters for daily_active_users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersListParamsDaterangesItem]`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersListParamsDimensionsItem]`
    :   The type of the None singleton.

    `keep_empty_rows: bool`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersListParamsMetricsItem]`
    :   The type of the None singleton.

    `property_id: str`
    :   The type of the None singleton.

    `return_property_quota: bool`
    :   The type of the None singleton.

<a id="DailyActiveUsersListParamsDaterangesItem"></a>

`DailyActiveUsersListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for DailyActiveUsersListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

<a id="DailyActiveUsersListParamsDimensionsItem"></a>

`DailyActiveUsersListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for DailyActiveUsersListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="DailyActiveUsersListParamsMetricsItem"></a>

`DailyActiveUsersListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for DailyActiveUsersListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="DailyActiveUsersLtCondition"></a>

`DailyActiveUsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="DailyActiveUsersLteCondition"></a>

`DailyActiveUsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="DailyActiveUsersNeqCondition"></a>

`DailyActiveUsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="DailyActiveUsersNotCondition"></a>

`DailyActiveUsersNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersAnyCondition`
    :   The type of the None singleton.

<a id="DailyActiveUsersOrCondition"></a>

`DailyActiveUsersOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersAnyCondition]`
    :   The type of the None singleton.

<a id="DailyActiveUsersSearchFilter"></a>

`DailyActiveUsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering daily_active_users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active1_day_users: int | None`
    :   Number of distinct users active in the last 1 day

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `property_id: str`
    :   GA4 property ID

    `start_date: str | None`
    :   Start date of the reporting period

<a id="DailyActiveUsersSearchQuery"></a>

`DailyActiveUsersSearchQuery(*args, **kwargs)`
:   Search query for daily_active_users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersSortFilter]`
    :   The type of the None singleton.

<a id="DailyActiveUsersSortFilter"></a>

`DailyActiveUsersSortFilter(*args, **kwargs)`
:   Available fields for sorting daily_active_users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active1_day_users: Literal['asc', 'desc']`
    :   Number of distinct users active in the last 1 day

    `date: Literal['asc', 'desc']`
    :   Date of the report row in YYYYMMDD format

    `end_date: Literal['asc', 'desc']`
    :   End date of the reporting period

    `property_id: Literal['asc', 'desc']`
    :   GA4 property ID

    `start_date: Literal['asc', 'desc']`
    :   Start date of the reporting period

<a id="DailyActiveUsersStringFilter"></a>

`DailyActiveUsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active1_day_users: str`
    :   Number of distinct users active in the last 1 day

    `date: str`
    :   Date of the report row in YYYYMMDD format

    `end_date: str`
    :   End date of the reporting period

    `property_id: str`
    :   GA4 property ID

    `start_date: str`
    :   Start date of the reporting period

<a id="DevicesAndCondition"></a>

`DevicesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesAnyCondition]`
    :   The type of the None singleton.

<a id="DevicesAnyCondition"></a>

`DevicesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesAnyValueFilter`
    :   The type of the None singleton.

<a id="DevicesAnyValueFilter"></a>

`DevicesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: Any`
    :   Average duration of sessions in seconds

    `bounce_rate: Any`
    :   Percentage of sessions that were single-page with no interaction

    `browser: Any`
    :   The web browser used (e.g., Chrome, Safari, Firefox)

    `date: Any`
    :   Date of the report row in YYYYMMDD format

    `device_category: Any`
    :   The device category (desktop, mobile, tablet)

    `end_date: Any`
    :   End date of the reporting period

    `new_users: Any`
    :   Number of first-time users

    `operating_system: Any`
    :   The operating system used (e.g., Windows, iOS, Android)

    `property_id: Any`
    :   GA4 property ID

    `screen_page_views: Any`
    :   Total number of screen or page views

    `screen_page_views_per_session: Any`
    :   Average page views per session

    `sessions: Any`
    :   Total number of sessions

    `sessions_per_user: Any`
    :   Average number of sessions per user

    `start_date: Any`
    :   Start date of the reporting period

    `total_users: Any`
    :   Total number of unique users

<a id="DevicesContainsCondition"></a>

`DevicesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesAnyValueFilter`
    :   The type of the None singleton.

<a id="DevicesEqCondition"></a>

`DevicesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesSearchFilter`
    :   The type of the None singleton.

<a id="DevicesFuzzyCondition"></a>

`DevicesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesStringFilter`
    :   The type of the None singleton.

<a id="DevicesGtCondition"></a>

`DevicesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesSearchFilter`
    :   The type of the None singleton.

<a id="DevicesGteCondition"></a>

`DevicesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesSearchFilter`
    :   The type of the None singleton.

<a id="DevicesInCondition"></a>

`DevicesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesInFilter`
    :   The type of the None singleton.

<a id="DevicesInFilter"></a>

`DevicesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: list[float]`
    :   Average duration of sessions in seconds

    `bounce_rate: list[float]`
    :   Percentage of sessions that were single-page with no interaction

    `browser: list[str]`
    :   The web browser used (e.g., Chrome, Safari, Firefox)

    `date: list[str]`
    :   Date of the report row in YYYYMMDD format

    `device_category: list[str]`
    :   The device category (desktop, mobile, tablet)

    `end_date: list[str]`
    :   End date of the reporting period

    `new_users: list[int]`
    :   Number of first-time users

    `operating_system: list[str]`
    :   The operating system used (e.g., Windows, iOS, Android)

    `property_id: list[str]`
    :   GA4 property ID

    `screen_page_views: list[int]`
    :   Total number of screen or page views

    `screen_page_views_per_session: list[float]`
    :   Average page views per session

    `sessions: list[int]`
    :   Total number of sessions

    `sessions_per_user: list[float]`
    :   Average number of sessions per user

    `start_date: list[str]`
    :   Start date of the reporting period

    `total_users: list[int]`
    :   Total number of unique users

<a id="DevicesKeywordCondition"></a>

`DevicesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesStringFilter`
    :   The type of the None singleton.

<a id="DevicesLikeCondition"></a>

`DevicesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesStringFilter`
    :   The type of the None singleton.

<a id="DevicesListParams"></a>

`DevicesListParams(*args, **kwargs)`
:   Parameters for devices.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesListParamsDaterangesItem]`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesListParamsDimensionsItem]`
    :   The type of the None singleton.

    `keep_empty_rows: bool`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesListParamsMetricsItem]`
    :   The type of the None singleton.

    `property_id: str`
    :   The type of the None singleton.

    `return_property_quota: bool`
    :   The type of the None singleton.

<a id="DevicesListParamsDaterangesItem"></a>

`DevicesListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for DevicesListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

<a id="DevicesListParamsDimensionsItem"></a>

`DevicesListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for DevicesListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="DevicesListParamsMetricsItem"></a>

`DevicesListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for DevicesListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="DevicesLtCondition"></a>

`DevicesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesSearchFilter`
    :   The type of the None singleton.

<a id="DevicesLteCondition"></a>

`DevicesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesSearchFilter`
    :   The type of the None singleton.

<a id="DevicesNeqCondition"></a>

`DevicesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesSearchFilter`
    :   The type of the None singleton.

<a id="DevicesNotCondition"></a>

`DevicesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesAnyCondition`
    :   The type of the None singleton.

<a id="DevicesOrCondition"></a>

`DevicesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesAnyCondition]`
    :   The type of the None singleton.

<a id="DevicesSearchFilter"></a>

`DevicesSearchFilter(*args, **kwargs)`
:   Available fields for filtering devices search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="DevicesSearchQuery"></a>

`DevicesSearchQuery(*args, **kwargs)`
:   Search query for devices entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesSortFilter]`
    :   The type of the None singleton.

<a id="DevicesSortFilter"></a>

`DevicesSortFilter(*args, **kwargs)`
:   Available fields for sorting devices search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: Literal['asc', 'desc']`
    :   Average duration of sessions in seconds

    `bounce_rate: Literal['asc', 'desc']`
    :   Percentage of sessions that were single-page with no interaction

    `browser: Literal['asc', 'desc']`
    :   The web browser used (e.g., Chrome, Safari, Firefox)

    `date: Literal['asc', 'desc']`
    :   Date of the report row in YYYYMMDD format

    `device_category: Literal['asc', 'desc']`
    :   The device category (desktop, mobile, tablet)

    `end_date: Literal['asc', 'desc']`
    :   End date of the reporting period

    `new_users: Literal['asc', 'desc']`
    :   Number of first-time users

    `operating_system: Literal['asc', 'desc']`
    :   The operating system used (e.g., Windows, iOS, Android)

    `property_id: Literal['asc', 'desc']`
    :   GA4 property ID

    `screen_page_views: Literal['asc', 'desc']`
    :   Total number of screen or page views

    `screen_page_views_per_session: Literal['asc', 'desc']`
    :   Average page views per session

    `sessions: Literal['asc', 'desc']`
    :   Total number of sessions

    `sessions_per_user: Literal['asc', 'desc']`
    :   Average number of sessions per user

    `start_date: Literal['asc', 'desc']`
    :   Start date of the reporting period

    `total_users: Literal['asc', 'desc']`
    :   Total number of unique users

<a id="DevicesStringFilter"></a>

`DevicesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: str`
    :   Average duration of sessions in seconds

    `bounce_rate: str`
    :   Percentage of sessions that were single-page with no interaction

    `browser: str`
    :   The web browser used (e.g., Chrome, Safari, Firefox)

    `date: str`
    :   Date of the report row in YYYYMMDD format

    `device_category: str`
    :   The device category (desktop, mobile, tablet)

    `end_date: str`
    :   End date of the reporting period

    `new_users: str`
    :   Number of first-time users

    `operating_system: str`
    :   The operating system used (e.g., Windows, iOS, Android)

    `property_id: str`
    :   GA4 property ID

    `screen_page_views: str`
    :   Total number of screen or page views

    `screen_page_views_per_session: str`
    :   Average page views per session

    `sessions: str`
    :   Total number of sessions

    `sessions_per_user: str`
    :   Average number of sessions per user

    `start_date: str`
    :   Start date of the reporting period

    `total_users: str`
    :   Total number of unique users

<a id="FourWeeklyActiveUsersAndCondition"></a>

`FourWeeklyActiveUsersAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersAnyCondition]`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersAnyCondition"></a>

`FourWeeklyActiveUsersAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersAnyValueFilter`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersAnyValueFilter"></a>

`FourWeeklyActiveUsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active28_day_users: Any`
    :   Number of distinct users active in the last 28 days

    `date: Any`
    :   Date of the report row in YYYYMMDD format

    `end_date: Any`
    :   End date of the reporting period

    `property_id: Any`
    :   GA4 property ID

    `start_date: Any`
    :   Start date of the reporting period

<a id="FourWeeklyActiveUsersContainsCondition"></a>

`FourWeeklyActiveUsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersAnyValueFilter`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersEqCondition"></a>

`FourWeeklyActiveUsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersFuzzyCondition"></a>

`FourWeeklyActiveUsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersStringFilter`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersGtCondition"></a>

`FourWeeklyActiveUsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersGteCondition"></a>

`FourWeeklyActiveUsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersInCondition"></a>

`FourWeeklyActiveUsersInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersInFilter`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersInFilter"></a>

`FourWeeklyActiveUsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active28_day_users: list[int]`
    :   Number of distinct users active in the last 28 days

    `date: list[str]`
    :   Date of the report row in YYYYMMDD format

    `end_date: list[str]`
    :   End date of the reporting period

    `property_id: list[str]`
    :   GA4 property ID

    `start_date: list[str]`
    :   Start date of the reporting period

<a id="FourWeeklyActiveUsersKeywordCondition"></a>

`FourWeeklyActiveUsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersStringFilter`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersLikeCondition"></a>

`FourWeeklyActiveUsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersStringFilter`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersListParams"></a>

`FourWeeklyActiveUsersListParams(*args, **kwargs)`
:   Parameters for four_weekly_active_users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersListParamsDaterangesItem]`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersListParamsDimensionsItem]`
    :   The type of the None singleton.

    `keep_empty_rows: bool`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersListParamsMetricsItem]`
    :   The type of the None singleton.

    `property_id: str`
    :   The type of the None singleton.

    `return_property_quota: bool`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersListParamsDaterangesItem"></a>

`FourWeeklyActiveUsersListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for FourWeeklyActiveUsersListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersListParamsDimensionsItem"></a>

`FourWeeklyActiveUsersListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for FourWeeklyActiveUsersListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersListParamsMetricsItem"></a>

`FourWeeklyActiveUsersListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for FourWeeklyActiveUsersListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersLtCondition"></a>

`FourWeeklyActiveUsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersLteCondition"></a>

`FourWeeklyActiveUsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersNeqCondition"></a>

`FourWeeklyActiveUsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersNotCondition"></a>

`FourWeeklyActiveUsersNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersAnyCondition`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersOrCondition"></a>

`FourWeeklyActiveUsersOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersAnyCondition]`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersSearchFilter"></a>

`FourWeeklyActiveUsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering four_weekly_active_users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active28_day_users: int | None`
    :   Number of distinct users active in the last 28 days

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `property_id: str`
    :   GA4 property ID

    `start_date: str | None`
    :   Start date of the reporting period

<a id="FourWeeklyActiveUsersSearchQuery"></a>

`FourWeeklyActiveUsersSearchQuery(*args, **kwargs)`
:   Search query for four_weekly_active_users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersSortFilter]`
    :   The type of the None singleton.

<a id="FourWeeklyActiveUsersSortFilter"></a>

`FourWeeklyActiveUsersSortFilter(*args, **kwargs)`
:   Available fields for sorting four_weekly_active_users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active28_day_users: Literal['asc', 'desc']`
    :   Number of distinct users active in the last 28 days

    `date: Literal['asc', 'desc']`
    :   Date of the report row in YYYYMMDD format

    `end_date: Literal['asc', 'desc']`
    :   End date of the reporting period

    `property_id: Literal['asc', 'desc']`
    :   GA4 property ID

    `start_date: Literal['asc', 'desc']`
    :   Start date of the reporting period

<a id="FourWeeklyActiveUsersStringFilter"></a>

`FourWeeklyActiveUsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active28_day_users: str`
    :   Number of distinct users active in the last 28 days

    `date: str`
    :   Date of the report row in YYYYMMDD format

    `end_date: str`
    :   End date of the reporting period

    `property_id: str`
    :   GA4 property ID

    `start_date: str`
    :   Start date of the reporting period

<a id="LocationsAndCondition"></a>

`LocationsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsAnyCondition]`
    :   The type of the None singleton.

<a id="LocationsAnyCondition"></a>

`LocationsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsAnyValueFilter`
    :   The type of the None singleton.

<a id="LocationsAnyValueFilter"></a>

`LocationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: Any`
    :   Average duration of sessions in seconds

    `bounce_rate: Any`
    :   Percentage of sessions that were single-page with no interaction

    `city: Any`
    :   The city of the user

    `country: Any`
    :   The country of the user

    `date: Any`
    :   Date of the report row in YYYYMMDD format

    `end_date: Any`
    :   End date of the reporting period

    `new_users: Any`
    :   Number of first-time users

    `property_id: Any`
    :   GA4 property ID

    `region: Any`
    :   The region (state/province) of the user

    `screen_page_views: Any`
    :   Total number of screen or page views

    `screen_page_views_per_session: Any`
    :   Average page views per session

    `sessions: Any`
    :   Total number of sessions

    `sessions_per_user: Any`
    :   Average number of sessions per user

    `start_date: Any`
    :   Start date of the reporting period

    `total_users: Any`
    :   Total number of unique users

<a id="LocationsContainsCondition"></a>

`LocationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsAnyValueFilter`
    :   The type of the None singleton.

<a id="LocationsEqCondition"></a>

`LocationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsSearchFilter`
    :   The type of the None singleton.

<a id="LocationsFuzzyCondition"></a>

`LocationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsStringFilter`
    :   The type of the None singleton.

<a id="LocationsGtCondition"></a>

`LocationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsSearchFilter`
    :   The type of the None singleton.

<a id="LocationsGteCondition"></a>

`LocationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsSearchFilter`
    :   The type of the None singleton.

<a id="LocationsInCondition"></a>

`LocationsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsInFilter`
    :   The type of the None singleton.

<a id="LocationsInFilter"></a>

`LocationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: list[float]`
    :   Average duration of sessions in seconds

    `bounce_rate: list[float]`
    :   Percentage of sessions that were single-page with no interaction

    `city: list[str]`
    :   The city of the user

    `country: list[str]`
    :   The country of the user

    `date: list[str]`
    :   Date of the report row in YYYYMMDD format

    `end_date: list[str]`
    :   End date of the reporting period

    `new_users: list[int]`
    :   Number of first-time users

    `property_id: list[str]`
    :   GA4 property ID

    `region: list[str]`
    :   The region (state/province) of the user

    `screen_page_views: list[int]`
    :   Total number of screen or page views

    `screen_page_views_per_session: list[float]`
    :   Average page views per session

    `sessions: list[int]`
    :   Total number of sessions

    `sessions_per_user: list[float]`
    :   Average number of sessions per user

    `start_date: list[str]`
    :   Start date of the reporting period

    `total_users: list[int]`
    :   Total number of unique users

<a id="LocationsKeywordCondition"></a>

`LocationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsStringFilter`
    :   The type of the None singleton.

<a id="LocationsLikeCondition"></a>

`LocationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsStringFilter`
    :   The type of the None singleton.

<a id="LocationsListParams"></a>

`LocationsListParams(*args, **kwargs)`
:   Parameters for locations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsListParamsDaterangesItem]`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsListParamsDimensionsItem]`
    :   The type of the None singleton.

    `keep_empty_rows: bool`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsListParamsMetricsItem]`
    :   The type of the None singleton.

    `property_id: str`
    :   The type of the None singleton.

    `return_property_quota: bool`
    :   The type of the None singleton.

<a id="LocationsListParamsDaterangesItem"></a>

`LocationsListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for LocationsListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

<a id="LocationsListParamsDimensionsItem"></a>

`LocationsListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for LocationsListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="LocationsListParamsMetricsItem"></a>

`LocationsListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for LocationsListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="LocationsLtCondition"></a>

`LocationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsSearchFilter`
    :   The type of the None singleton.

<a id="LocationsLteCondition"></a>

`LocationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsSearchFilter`
    :   The type of the None singleton.

<a id="LocationsNeqCondition"></a>

`LocationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsSearchFilter`
    :   The type of the None singleton.

<a id="LocationsNotCondition"></a>

`LocationsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsAnyCondition`
    :   The type of the None singleton.

<a id="LocationsOrCondition"></a>

`LocationsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsAnyCondition]`
    :   The type of the None singleton.

<a id="LocationsSearchFilter"></a>

`LocationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering locations search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="LocationsSearchQuery"></a>

`LocationsSearchQuery(*args, **kwargs)`
:   Search query for locations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsSortFilter]`
    :   The type of the None singleton.

<a id="LocationsSortFilter"></a>

`LocationsSortFilter(*args, **kwargs)`
:   Available fields for sorting locations search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: Literal['asc', 'desc']`
    :   Average duration of sessions in seconds

    `bounce_rate: Literal['asc', 'desc']`
    :   Percentage of sessions that were single-page with no interaction

    `city: Literal['asc', 'desc']`
    :   The city of the user

    `country: Literal['asc', 'desc']`
    :   The country of the user

    `date: Literal['asc', 'desc']`
    :   Date of the report row in YYYYMMDD format

    `end_date: Literal['asc', 'desc']`
    :   End date of the reporting period

    `new_users: Literal['asc', 'desc']`
    :   Number of first-time users

    `property_id: Literal['asc', 'desc']`
    :   GA4 property ID

    `region: Literal['asc', 'desc']`
    :   The region (state/province) of the user

    `screen_page_views: Literal['asc', 'desc']`
    :   Total number of screen or page views

    `screen_page_views_per_session: Literal['asc', 'desc']`
    :   Average page views per session

    `sessions: Literal['asc', 'desc']`
    :   Total number of sessions

    `sessions_per_user: Literal['asc', 'desc']`
    :   Average number of sessions per user

    `start_date: Literal['asc', 'desc']`
    :   Start date of the reporting period

    `total_users: Literal['asc', 'desc']`
    :   Total number of unique users

<a id="LocationsStringFilter"></a>

`LocationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: str`
    :   Average duration of sessions in seconds

    `bounce_rate: str`
    :   Percentage of sessions that were single-page with no interaction

    `city: str`
    :   The city of the user

    `country: str`
    :   The country of the user

    `date: str`
    :   Date of the report row in YYYYMMDD format

    `end_date: str`
    :   End date of the reporting period

    `new_users: str`
    :   Number of first-time users

    `property_id: str`
    :   GA4 property ID

    `region: str`
    :   The region (state/province) of the user

    `screen_page_views: str`
    :   Total number of screen or page views

    `screen_page_views_per_session: str`
    :   Average page views per session

    `sessions: str`
    :   Total number of sessions

    `sessions_per_user: str`
    :   Average number of sessions per user

    `start_date: str`
    :   Start date of the reporting period

    `total_users: str`
    :   Total number of unique users

<a id="PagesAndCondition"></a>

`PagesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesAnyCondition]`
    :   The type of the None singleton.

<a id="PagesAnyCondition"></a>

`PagesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesAnyValueFilter`
    :   The type of the None singleton.

<a id="PagesAnyValueFilter"></a>

`PagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bounce_rate: Any`
    :   Percentage of sessions that were single-page with no interaction

    `date: Any`
    :   Date of the report row in YYYYMMDD format

    `end_date: Any`
    :   End date of the reporting period

    `host_name: Any`
    :   The hostname of the page

    `page_path_plus_query_string: Any`
    :   The page path and query string

    `property_id: Any`
    :   GA4 property ID

    `screen_page_views: Any`
    :   Total number of screen or page views

    `start_date: Any`
    :   Start date of the reporting period

<a id="PagesContainsCondition"></a>

`PagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesAnyValueFilter`
    :   The type of the None singleton.

<a id="PagesEqCondition"></a>

`PagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesFuzzyCondition"></a>

`PagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesStringFilter`
    :   The type of the None singleton.

<a id="PagesGtCondition"></a>

`PagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesGteCondition"></a>

`PagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesInCondition"></a>

`PagesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesInFilter`
    :   The type of the None singleton.

<a id="PagesInFilter"></a>

`PagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bounce_rate: list[float]`
    :   Percentage of sessions that were single-page with no interaction

    `date: list[str]`
    :   Date of the report row in YYYYMMDD format

    `end_date: list[str]`
    :   End date of the reporting period

    `host_name: list[str]`
    :   The hostname of the page

    `page_path_plus_query_string: list[str]`
    :   The page path and query string

    `property_id: list[str]`
    :   GA4 property ID

    `screen_page_views: list[int]`
    :   Total number of screen or page views

    `start_date: list[str]`
    :   Start date of the reporting period

<a id="PagesKeywordCondition"></a>

`PagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesStringFilter`
    :   The type of the None singleton.

<a id="PagesLikeCondition"></a>

`PagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesStringFilter`
    :   The type of the None singleton.

<a id="PagesListParams"></a>

`PagesListParams(*args, **kwargs)`
:   Parameters for pages.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesListParamsDaterangesItem]`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesListParamsDimensionsItem]`
    :   The type of the None singleton.

    `keep_empty_rows: bool`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesListParamsMetricsItem]`
    :   The type of the None singleton.

    `property_id: str`
    :   The type of the None singleton.

    `return_property_quota: bool`
    :   The type of the None singleton.

<a id="PagesListParamsDaterangesItem"></a>

`PagesListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for PagesListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

<a id="PagesListParamsDimensionsItem"></a>

`PagesListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for PagesListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="PagesListParamsMetricsItem"></a>

`PagesListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for PagesListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="PagesLtCondition"></a>

`PagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesLteCondition"></a>

`PagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesNeqCondition"></a>

`PagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesNotCondition"></a>

`PagesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesAnyCondition`
    :   The type of the None singleton.

<a id="PagesOrCondition"></a>

`PagesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesAnyCondition]`
    :   The type of the None singleton.

<a id="PagesSearchFilter"></a>

`PagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering pages search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bounce_rate: float | None`
    :   Percentage of sessions that were single-page with no interaction

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `host_name: str | None`
    :   The hostname of the page

    `page_path_plus_query_string: str | None`
    :   The page path and query string

    `property_id: str`
    :   GA4 property ID

    `screen_page_views: int | None`
    :   Total number of screen or page views

    `start_date: str | None`
    :   Start date of the reporting period

<a id="PagesSearchQuery"></a>

`PagesSearchQuery(*args, **kwargs)`
:   Search query for pages entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesSortFilter]`
    :   The type of the None singleton.

<a id="PagesSortFilter"></a>

`PagesSortFilter(*args, **kwargs)`
:   Available fields for sorting pages search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bounce_rate: Literal['asc', 'desc']`
    :   Percentage of sessions that were single-page with no interaction

    `date: Literal['asc', 'desc']`
    :   Date of the report row in YYYYMMDD format

    `end_date: Literal['asc', 'desc']`
    :   End date of the reporting period

    `host_name: Literal['asc', 'desc']`
    :   The hostname of the page

    `page_path_plus_query_string: Literal['asc', 'desc']`
    :   The page path and query string

    `property_id: Literal['asc', 'desc']`
    :   GA4 property ID

    `screen_page_views: Literal['asc', 'desc']`
    :   Total number of screen or page views

    `start_date: Literal['asc', 'desc']`
    :   Start date of the reporting period

<a id="PagesStringFilter"></a>

`PagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bounce_rate: str`
    :   Percentage of sessions that were single-page with no interaction

    `date: str`
    :   Date of the report row in YYYYMMDD format

    `end_date: str`
    :   End date of the reporting period

    `host_name: str`
    :   The hostname of the page

    `page_path_plus_query_string: str`
    :   The page path and query string

    `property_id: str`
    :   GA4 property ID

    `screen_page_views: str`
    :   Total number of screen or page views

    `start_date: str`
    :   Start date of the reporting period

<a id="TrafficSourcesAndCondition"></a>

`TrafficSourcesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesAnyCondition]`
    :   The type of the None singleton.

<a id="TrafficSourcesAnyCondition"></a>

`TrafficSourcesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesAnyValueFilter`
    :   The type of the None singleton.

<a id="TrafficSourcesAnyValueFilter"></a>

`TrafficSourcesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: Any`
    :   Average duration of sessions in seconds

    `bounce_rate: Any`
    :   Percentage of sessions that were single-page with no interaction

    `date: Any`
    :   Date of the report row in YYYYMMDD format

    `end_date: Any`
    :   End date of the reporting period

    `new_users: Any`
    :   Number of first-time users

    `property_id: Any`
    :   GA4 property ID

    `screen_page_views: Any`
    :   Total number of screen or page views

    `screen_page_views_per_session: Any`
    :   Average page views per session

    `session_medium: Any`
    :   The medium of the traffic source (e.g., organic, cpc, referral)

    `session_source: Any`
    :   The source of the traffic (e.g., google, direct)

    `sessions: Any`
    :   Total number of sessions

    `sessions_per_user: Any`
    :   Average number of sessions per user

    `start_date: Any`
    :   Start date of the reporting period

    `total_users: Any`
    :   Total number of unique users

<a id="TrafficSourcesContainsCondition"></a>

`TrafficSourcesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesAnyValueFilter`
    :   The type of the None singleton.

<a id="TrafficSourcesEqCondition"></a>

`TrafficSourcesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesSearchFilter`
    :   The type of the None singleton.

<a id="TrafficSourcesFuzzyCondition"></a>

`TrafficSourcesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesStringFilter`
    :   The type of the None singleton.

<a id="TrafficSourcesGtCondition"></a>

`TrafficSourcesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesSearchFilter`
    :   The type of the None singleton.

<a id="TrafficSourcesGteCondition"></a>

`TrafficSourcesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesSearchFilter`
    :   The type of the None singleton.

<a id="TrafficSourcesInCondition"></a>

`TrafficSourcesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesInFilter`
    :   The type of the None singleton.

<a id="TrafficSourcesInFilter"></a>

`TrafficSourcesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: list[float]`
    :   Average duration of sessions in seconds

    `bounce_rate: list[float]`
    :   Percentage of sessions that were single-page with no interaction

    `date: list[str]`
    :   Date of the report row in YYYYMMDD format

    `end_date: list[str]`
    :   End date of the reporting period

    `new_users: list[int]`
    :   Number of first-time users

    `property_id: list[str]`
    :   GA4 property ID

    `screen_page_views: list[int]`
    :   Total number of screen or page views

    `screen_page_views_per_session: list[float]`
    :   Average page views per session

    `session_medium: list[str]`
    :   The medium of the traffic source (e.g., organic, cpc, referral)

    `session_source: list[str]`
    :   The source of the traffic (e.g., google, direct)

    `sessions: list[int]`
    :   Total number of sessions

    `sessions_per_user: list[float]`
    :   Average number of sessions per user

    `start_date: list[str]`
    :   Start date of the reporting period

    `total_users: list[int]`
    :   Total number of unique users

<a id="TrafficSourcesKeywordCondition"></a>

`TrafficSourcesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesStringFilter`
    :   The type of the None singleton.

<a id="TrafficSourcesLikeCondition"></a>

`TrafficSourcesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesStringFilter`
    :   The type of the None singleton.

<a id="TrafficSourcesListParams"></a>

`TrafficSourcesListParams(*args, **kwargs)`
:   Parameters for traffic_sources.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesListParamsDaterangesItem]`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesListParamsDimensionsItem]`
    :   The type of the None singleton.

    `keep_empty_rows: bool`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesListParamsMetricsItem]`
    :   The type of the None singleton.

    `property_id: str`
    :   The type of the None singleton.

    `return_property_quota: bool`
    :   The type of the None singleton.

<a id="TrafficSourcesListParamsDaterangesItem"></a>

`TrafficSourcesListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for TrafficSourcesListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

<a id="TrafficSourcesListParamsDimensionsItem"></a>

`TrafficSourcesListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for TrafficSourcesListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="TrafficSourcesListParamsMetricsItem"></a>

`TrafficSourcesListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for TrafficSourcesListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="TrafficSourcesLtCondition"></a>

`TrafficSourcesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesSearchFilter`
    :   The type of the None singleton.

<a id="TrafficSourcesLteCondition"></a>

`TrafficSourcesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesSearchFilter`
    :   The type of the None singleton.

<a id="TrafficSourcesNeqCondition"></a>

`TrafficSourcesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesSearchFilter`
    :   The type of the None singleton.

<a id="TrafficSourcesNotCondition"></a>

`TrafficSourcesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesAnyCondition`
    :   The type of the None singleton.

<a id="TrafficSourcesOrCondition"></a>

`TrafficSourcesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesAnyCondition]`
    :   The type of the None singleton.

<a id="TrafficSourcesSearchFilter"></a>

`TrafficSourcesSearchFilter(*args, **kwargs)`
:   Available fields for filtering traffic_sources search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: float | None`
    :   Average duration of sessions in seconds

    `bounce_rate: float | None`
    :   Percentage of sessions that were single-page with no interaction

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

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

<a id="TrafficSourcesSearchQuery"></a>

`TrafficSourcesSearchQuery(*args, **kwargs)`
:   Search query for traffic_sources entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesSortFilter]`
    :   The type of the None singleton.

<a id="TrafficSourcesSortFilter"></a>

`TrafficSourcesSortFilter(*args, **kwargs)`
:   Available fields for sorting traffic_sources search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: Literal['asc', 'desc']`
    :   Average duration of sessions in seconds

    `bounce_rate: Literal['asc', 'desc']`
    :   Percentage of sessions that were single-page with no interaction

    `date: Literal['asc', 'desc']`
    :   Date of the report row in YYYYMMDD format

    `end_date: Literal['asc', 'desc']`
    :   End date of the reporting period

    `new_users: Literal['asc', 'desc']`
    :   Number of first-time users

    `property_id: Literal['asc', 'desc']`
    :   GA4 property ID

    `screen_page_views: Literal['asc', 'desc']`
    :   Total number of screen or page views

    `screen_page_views_per_session: Literal['asc', 'desc']`
    :   Average page views per session

    `session_medium: Literal['asc', 'desc']`
    :   The medium of the traffic source (e.g., organic, cpc, referral)

    `session_source: Literal['asc', 'desc']`
    :   The source of the traffic (e.g., google, direct)

    `sessions: Literal['asc', 'desc']`
    :   Total number of sessions

    `sessions_per_user: Literal['asc', 'desc']`
    :   Average number of sessions per user

    `start_date: Literal['asc', 'desc']`
    :   Start date of the reporting period

    `total_users: Literal['asc', 'desc']`
    :   Total number of unique users

<a id="TrafficSourcesStringFilter"></a>

`TrafficSourcesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: str`
    :   Average duration of sessions in seconds

    `bounce_rate: str`
    :   Percentage of sessions that were single-page with no interaction

    `date: str`
    :   Date of the report row in YYYYMMDD format

    `end_date: str`
    :   End date of the reporting period

    `new_users: str`
    :   Number of first-time users

    `property_id: str`
    :   GA4 property ID

    `screen_page_views: str`
    :   Total number of screen or page views

    `screen_page_views_per_session: str`
    :   Average page views per session

    `session_medium: str`
    :   The medium of the traffic source (e.g., organic, cpc, referral)

    `session_source: str`
    :   The source of the traffic (e.g., google, direct)

    `sessions: str`
    :   Total number of sessions

    `sessions_per_user: str`
    :   Average number of sessions per user

    `start_date: str`
    :   Start date of the reporting period

    `total_users: str`
    :   Total number of unique users

<a id="WebsiteOverviewAndCondition"></a>

`WebsiteOverviewAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewAnyCondition]`
    :   The type of the None singleton.

<a id="WebsiteOverviewAnyCondition"></a>

`WebsiteOverviewAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewAnyValueFilter`
    :   The type of the None singleton.

<a id="WebsiteOverviewAnyValueFilter"></a>

`WebsiteOverviewAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: Any`
    :   Average duration of sessions in seconds

    `bounce_rate: Any`
    :   Percentage of sessions that were single-page with no interaction

    `date: Any`
    :   Date of the report row in YYYYMMDD format

    `end_date: Any`
    :   End date of the reporting period

    `new_users: Any`
    :   Number of first-time users

    `property_id: Any`
    :   GA4 property ID

    `screen_page_views: Any`
    :   Total number of screen or page views

    `screen_page_views_per_session: Any`
    :   Average page views per session

    `sessions: Any`
    :   Total number of sessions

    `sessions_per_user: Any`
    :   Average number of sessions per user

    `start_date: Any`
    :   Start date of the reporting period

    `total_users: Any`
    :   Total number of unique users

<a id="WebsiteOverviewContainsCondition"></a>

`WebsiteOverviewContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewAnyValueFilter`
    :   The type of the None singleton.

<a id="WebsiteOverviewEqCondition"></a>

`WebsiteOverviewEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewSearchFilter`
    :   The type of the None singleton.

<a id="WebsiteOverviewFuzzyCondition"></a>

`WebsiteOverviewFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewStringFilter`
    :   The type of the None singleton.

<a id="WebsiteOverviewGtCondition"></a>

`WebsiteOverviewGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewSearchFilter`
    :   The type of the None singleton.

<a id="WebsiteOverviewGteCondition"></a>

`WebsiteOverviewGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewSearchFilter`
    :   The type of the None singleton.

<a id="WebsiteOverviewInCondition"></a>

`WebsiteOverviewInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewInFilter`
    :   The type of the None singleton.

<a id="WebsiteOverviewInFilter"></a>

`WebsiteOverviewInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: list[float]`
    :   Average duration of sessions in seconds

    `bounce_rate: list[float]`
    :   Percentage of sessions that were single-page with no interaction

    `date: list[str]`
    :   Date of the report row in YYYYMMDD format

    `end_date: list[str]`
    :   End date of the reporting period

    `new_users: list[int]`
    :   Number of first-time users

    `property_id: list[str]`
    :   GA4 property ID

    `screen_page_views: list[int]`
    :   Total number of screen or page views

    `screen_page_views_per_session: list[float]`
    :   Average page views per session

    `sessions: list[int]`
    :   Total number of sessions

    `sessions_per_user: list[float]`
    :   Average number of sessions per user

    `start_date: list[str]`
    :   Start date of the reporting period

    `total_users: list[int]`
    :   Total number of unique users

<a id="WebsiteOverviewKeywordCondition"></a>

`WebsiteOverviewKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewStringFilter`
    :   The type of the None singleton.

<a id="WebsiteOverviewLikeCondition"></a>

`WebsiteOverviewLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewStringFilter`
    :   The type of the None singleton.

<a id="WebsiteOverviewListParams"></a>

`WebsiteOverviewListParams(*args, **kwargs)`
:   Parameters for website_overview.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewListParamsDaterangesItem]`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewListParamsDimensionsItem]`
    :   The type of the None singleton.

    `keep_empty_rows: bool`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewListParamsMetricsItem]`
    :   The type of the None singleton.

    `property_id: str`
    :   The type of the None singleton.

    `return_property_quota: bool`
    :   The type of the None singleton.

<a id="WebsiteOverviewListParamsDaterangesItem"></a>

`WebsiteOverviewListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for WebsiteOverviewListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

<a id="WebsiteOverviewListParamsDimensionsItem"></a>

`WebsiteOverviewListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for WebsiteOverviewListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="WebsiteOverviewListParamsMetricsItem"></a>

`WebsiteOverviewListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for WebsiteOverviewListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="WebsiteOverviewLtCondition"></a>

`WebsiteOverviewLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewSearchFilter`
    :   The type of the None singleton.

<a id="WebsiteOverviewLteCondition"></a>

`WebsiteOverviewLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewSearchFilter`
    :   The type of the None singleton.

<a id="WebsiteOverviewNeqCondition"></a>

`WebsiteOverviewNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewSearchFilter`
    :   The type of the None singleton.

<a id="WebsiteOverviewNotCondition"></a>

`WebsiteOverviewNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewAnyCondition`
    :   The type of the None singleton.

<a id="WebsiteOverviewOrCondition"></a>

`WebsiteOverviewOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewAnyCondition]`
    :   The type of the None singleton.

<a id="WebsiteOverviewSearchFilter"></a>

`WebsiteOverviewSearchFilter(*args, **kwargs)`
:   Available fields for filtering website_overview search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: float | None`
    :   Average duration of sessions in seconds

    `bounce_rate: float | None`
    :   Percentage of sessions that were single-page with no interaction

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

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

<a id="WebsiteOverviewSearchQuery"></a>

`WebsiteOverviewSearchQuery(*args, **kwargs)`
:   Search query for website_overview entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewSortFilter]`
    :   The type of the None singleton.

<a id="WebsiteOverviewSortFilter"></a>

`WebsiteOverviewSortFilter(*args, **kwargs)`
:   Available fields for sorting website_overview search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: Literal['asc', 'desc']`
    :   Average duration of sessions in seconds

    `bounce_rate: Literal['asc', 'desc']`
    :   Percentage of sessions that were single-page with no interaction

    `date: Literal['asc', 'desc']`
    :   Date of the report row in YYYYMMDD format

    `end_date: Literal['asc', 'desc']`
    :   End date of the reporting period

    `new_users: Literal['asc', 'desc']`
    :   Number of first-time users

    `property_id: Literal['asc', 'desc']`
    :   GA4 property ID

    `screen_page_views: Literal['asc', 'desc']`
    :   Total number of screen or page views

    `screen_page_views_per_session: Literal['asc', 'desc']`
    :   Average page views per session

    `sessions: Literal['asc', 'desc']`
    :   Total number of sessions

    `sessions_per_user: Literal['asc', 'desc']`
    :   Average number of sessions per user

    `start_date: Literal['asc', 'desc']`
    :   Start date of the reporting period

    `total_users: Literal['asc', 'desc']`
    :   Total number of unique users

<a id="WebsiteOverviewStringFilter"></a>

`WebsiteOverviewStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `average_session_duration: str`
    :   Average duration of sessions in seconds

    `bounce_rate: str`
    :   Percentage of sessions that were single-page with no interaction

    `date: str`
    :   Date of the report row in YYYYMMDD format

    `end_date: str`
    :   End date of the reporting period

    `new_users: str`
    :   Number of first-time users

    `property_id: str`
    :   GA4 property ID

    `screen_page_views: str`
    :   Total number of screen or page views

    `screen_page_views_per_session: str`
    :   Average page views per session

    `sessions: str`
    :   Total number of sessions

    `sessions_per_user: str`
    :   Average number of sessions per user

    `start_date: str`
    :   Start date of the reporting period

    `total_users: str`
    :   Total number of unique users

<a id="WeeklyActiveUsersAndCondition"></a>

`WeeklyActiveUsersAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersAnyCondition]`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersAnyCondition"></a>

`WeeklyActiveUsersAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersAnyValueFilter`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersAnyValueFilter"></a>

`WeeklyActiveUsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active7_day_users: Any`
    :   Number of distinct users active in the last 7 days

    `date: Any`
    :   Date of the report row in YYYYMMDD format

    `end_date: Any`
    :   End date of the reporting period

    `property_id: Any`
    :   GA4 property ID

    `start_date: Any`
    :   Start date of the reporting period

<a id="WeeklyActiveUsersContainsCondition"></a>

`WeeklyActiveUsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersAnyValueFilter`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersEqCondition"></a>

`WeeklyActiveUsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersFuzzyCondition"></a>

`WeeklyActiveUsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersStringFilter`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersGtCondition"></a>

`WeeklyActiveUsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersGteCondition"></a>

`WeeklyActiveUsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersInCondition"></a>

`WeeklyActiveUsersInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersInFilter`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersInFilter"></a>

`WeeklyActiveUsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active7_day_users: list[int]`
    :   Number of distinct users active in the last 7 days

    `date: list[str]`
    :   Date of the report row in YYYYMMDD format

    `end_date: list[str]`
    :   End date of the reporting period

    `property_id: list[str]`
    :   GA4 property ID

    `start_date: list[str]`
    :   Start date of the reporting period

<a id="WeeklyActiveUsersKeywordCondition"></a>

`WeeklyActiveUsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersStringFilter`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersLikeCondition"></a>

`WeeklyActiveUsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersStringFilter`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersListParams"></a>

`WeeklyActiveUsersListParams(*args, **kwargs)`
:   Parameters for weekly_active_users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_ranges: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersListParamsDaterangesItem]`
    :   The type of the None singleton.

    `dimensions: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersListParamsDimensionsItem]`
    :   The type of the None singleton.

    `keep_empty_rows: bool`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `metrics: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersListParamsMetricsItem]`
    :   The type of the None singleton.

    `property_id: str`
    :   The type of the None singleton.

    `return_property_quota: bool`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersListParamsDaterangesItem"></a>

`WeeklyActiveUsersListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for WeeklyActiveUsersListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersListParamsDimensionsItem"></a>

`WeeklyActiveUsersListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for WeeklyActiveUsersListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersListParamsMetricsItem"></a>

`WeeklyActiveUsersListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for WeeklyActiveUsersListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersLtCondition"></a>

`WeeklyActiveUsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersLteCondition"></a>

`WeeklyActiveUsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersNeqCondition"></a>

`WeeklyActiveUsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersNotCondition"></a>

`WeeklyActiveUsersNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersAnyCondition`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersOrCondition"></a>

`WeeklyActiveUsersOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersAnyCondition]`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersSearchFilter"></a>

`WeeklyActiveUsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering weekly_active_users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active7_day_users: int | None`
    :   Number of distinct users active in the last 7 days

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `property_id: str`
    :   GA4 property ID

    `start_date: str | None`
    :   Start date of the reporting period

<a id="WeeklyActiveUsersSearchQuery"></a>

`WeeklyActiveUsersSearchQuery(*args, **kwargs)`
:   Search query for weekly_active_users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersSortFilter]`
    :   The type of the None singleton.

<a id="WeeklyActiveUsersSortFilter"></a>

`WeeklyActiveUsersSortFilter(*args, **kwargs)`
:   Available fields for sorting weekly_active_users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active7_day_users: Literal['asc', 'desc']`
    :   Number of distinct users active in the last 7 days

    `date: Literal['asc', 'desc']`
    :   Date of the report row in YYYYMMDD format

    `end_date: Literal['asc', 'desc']`
    :   End date of the reporting period

    `property_id: Literal['asc', 'desc']`
    :   GA4 property ID

    `start_date: Literal['asc', 'desc']`
    :   Start date of the reporting period

<a id="WeeklyActiveUsersStringFilter"></a>

`WeeklyActiveUsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active7_day_users: str`
    :   Number of distinct users active in the last 7 days

    `date: str`
    :   Date of the report row in YYYYMMDD format

    `end_date: str`
    :   End date of the reporting period

    `property_id: str`
    :   GA4 property ID

    `start_date: str`
    :   Start date of the reporting period