---
id: airbyte_agent_sdk-connectors-google_analytics_data_api-types
title: airbyte_agent_sdk.connectors.google_analytics_data_api.types
---

Module airbyte_agent_sdk.connectors.google_analytics_data_api.types
===================================================================
Type definitions for google-analytics-data-api connector.

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

`DailyActiveUsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersAnyValueFilter`
    :   The type of the None singleton.

`DailyActiveUsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersSearchFilter`
    :   The type of the None singleton.

`DailyActiveUsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersStringFilter`
    :   The type of the None singleton.

`DailyActiveUsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersSearchFilter`
    :   The type of the None singleton.

`DailyActiveUsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersSearchFilter`
    :   The type of the None singleton.

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

`DailyActiveUsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersStringFilter`
    :   The type of the None singleton.

`DailyActiveUsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersStringFilter`
    :   The type of the None singleton.

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

`DailyActiveUsersListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for DailyActiveUsersListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

`DailyActiveUsersListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for DailyActiveUsersListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`DailyActiveUsersListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for DailyActiveUsersListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`DailyActiveUsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersSearchFilter`
    :   The type of the None singleton.

`DailyActiveUsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersSearchFilter`
    :   The type of the None singleton.

`DailyActiveUsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersSearchFilter`
    :   The type of the None singleton.

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

`DailyActiveUsersSearchQuery(*args, **kwargs)`
:   Search query for daily_active_users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.DailyActiveUsersSortFilter]`
    :   The type of the None singleton.

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

`DevicesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesAnyValueFilter`
    :   The type of the None singleton.

`DevicesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesSearchFilter`
    :   The type of the None singleton.

`DevicesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesStringFilter`
    :   The type of the None singleton.

`DevicesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesSearchFilter`
    :   The type of the None singleton.

`DevicesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesSearchFilter`
    :   The type of the None singleton.

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

`DevicesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesStringFilter`
    :   The type of the None singleton.

`DevicesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesStringFilter`
    :   The type of the None singleton.

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

`DevicesListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for DevicesListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

`DevicesListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for DevicesListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`DevicesListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for DevicesListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`DevicesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesSearchFilter`
    :   The type of the None singleton.

`DevicesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesSearchFilter`
    :   The type of the None singleton.

`DevicesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesSearchFilter`
    :   The type of the None singleton.

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

`DevicesSearchQuery(*args, **kwargs)`
:   Search query for devices entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.DevicesSortFilter]`
    :   The type of the None singleton.

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

`FourWeeklyActiveUsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersAnyValueFilter`
    :   The type of the None singleton.

`FourWeeklyActiveUsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

`FourWeeklyActiveUsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersStringFilter`
    :   The type of the None singleton.

`FourWeeklyActiveUsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

`FourWeeklyActiveUsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

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

`FourWeeklyActiveUsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersStringFilter`
    :   The type of the None singleton.

`FourWeeklyActiveUsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersStringFilter`
    :   The type of the None singleton.

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

`FourWeeklyActiveUsersListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for FourWeeklyActiveUsersListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

`FourWeeklyActiveUsersListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for FourWeeklyActiveUsersListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`FourWeeklyActiveUsersListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for FourWeeklyActiveUsersListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`FourWeeklyActiveUsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

`FourWeeklyActiveUsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

`FourWeeklyActiveUsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

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

`FourWeeklyActiveUsersSearchQuery(*args, **kwargs)`
:   Search query for four_weekly_active_users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.FourWeeklyActiveUsersSortFilter]`
    :   The type of the None singleton.

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

`LocationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsAnyValueFilter`
    :   The type of the None singleton.

`LocationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsSearchFilter`
    :   The type of the None singleton.

`LocationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsStringFilter`
    :   The type of the None singleton.

`LocationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsSearchFilter`
    :   The type of the None singleton.

`LocationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsSearchFilter`
    :   The type of the None singleton.

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

`LocationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsStringFilter`
    :   The type of the None singleton.

`LocationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsStringFilter`
    :   The type of the None singleton.

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

`LocationsListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for LocationsListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

`LocationsListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for LocationsListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`LocationsListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for LocationsListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`LocationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsSearchFilter`
    :   The type of the None singleton.

`LocationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsSearchFilter`
    :   The type of the None singleton.

`LocationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsSearchFilter`
    :   The type of the None singleton.

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

`LocationsSearchQuery(*args, **kwargs)`
:   Search query for locations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.LocationsSortFilter]`
    :   The type of the None singleton.

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

`PagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesAnyValueFilter`
    :   The type of the None singleton.

`PagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesSearchFilter`
    :   The type of the None singleton.

`PagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesStringFilter`
    :   The type of the None singleton.

`PagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesSearchFilter`
    :   The type of the None singleton.

`PagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesSearchFilter`
    :   The type of the None singleton.

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

`PagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesStringFilter`
    :   The type of the None singleton.

`PagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesStringFilter`
    :   The type of the None singleton.

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

`PagesListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for PagesListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

`PagesListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for PagesListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`PagesListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for PagesListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`PagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesSearchFilter`
    :   The type of the None singleton.

`PagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesSearchFilter`
    :   The type of the None singleton.

`PagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesSearchFilter`
    :   The type of the None singleton.

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

`PagesSearchQuery(*args, **kwargs)`
:   Search query for pages entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.PagesSortFilter]`
    :   The type of the None singleton.

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

`TrafficSourcesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesAnyValueFilter`
    :   The type of the None singleton.

`TrafficSourcesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesSearchFilter`
    :   The type of the None singleton.

`TrafficSourcesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesStringFilter`
    :   The type of the None singleton.

`TrafficSourcesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesSearchFilter`
    :   The type of the None singleton.

`TrafficSourcesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesSearchFilter`
    :   The type of the None singleton.

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

`TrafficSourcesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesStringFilter`
    :   The type of the None singleton.

`TrafficSourcesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesStringFilter`
    :   The type of the None singleton.

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

`TrafficSourcesListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for TrafficSourcesListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

`TrafficSourcesListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for TrafficSourcesListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`TrafficSourcesListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for TrafficSourcesListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`TrafficSourcesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesSearchFilter`
    :   The type of the None singleton.

`TrafficSourcesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesSearchFilter`
    :   The type of the None singleton.

`TrafficSourcesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesSearchFilter`
    :   The type of the None singleton.

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

`TrafficSourcesSearchQuery(*args, **kwargs)`
:   Search query for traffic_sources entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.TrafficSourcesSortFilter]`
    :   The type of the None singleton.

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

`WebsiteOverviewContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewAnyValueFilter`
    :   The type of the None singleton.

`WebsiteOverviewEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewSearchFilter`
    :   The type of the None singleton.

`WebsiteOverviewFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewStringFilter`
    :   The type of the None singleton.

`WebsiteOverviewGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewSearchFilter`
    :   The type of the None singleton.

`WebsiteOverviewGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewSearchFilter`
    :   The type of the None singleton.

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

`WebsiteOverviewKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewStringFilter`
    :   The type of the None singleton.

`WebsiteOverviewLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewStringFilter`
    :   The type of the None singleton.

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

`WebsiteOverviewListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for WebsiteOverviewListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

`WebsiteOverviewListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for WebsiteOverviewListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`WebsiteOverviewListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for WebsiteOverviewListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`WebsiteOverviewLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewSearchFilter`
    :   The type of the None singleton.

`WebsiteOverviewLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewSearchFilter`
    :   The type of the None singleton.

`WebsiteOverviewNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewSearchFilter`
    :   The type of the None singleton.

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

`WebsiteOverviewSearchQuery(*args, **kwargs)`
:   Search query for website_overview entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.WebsiteOverviewSortFilter]`
    :   The type of the None singleton.

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

`WeeklyActiveUsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersAnyValueFilter`
    :   The type of the None singleton.

`WeeklyActiveUsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

`WeeklyActiveUsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersStringFilter`
    :   The type of the None singleton.

`WeeklyActiveUsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

`WeeklyActiveUsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

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

`WeeklyActiveUsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersStringFilter`
    :   The type of the None singleton.

`WeeklyActiveUsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersStringFilter`
    :   The type of the None singleton.

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

`WeeklyActiveUsersListParamsDaterangesItem(*args, **kwargs)`
:   Nested schema for WeeklyActiveUsersListParams.dateRanges_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endDate: str`
    :   The type of the None singleton.

    `startDate: str`
    :   The type of the None singleton.

`WeeklyActiveUsersListParamsDimensionsItem(*args, **kwargs)`
:   Nested schema for WeeklyActiveUsersListParams.dimensions_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`WeeklyActiveUsersListParamsMetricsItem(*args, **kwargs)`
:   Nested schema for WeeklyActiveUsersListParams.metrics_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`WeeklyActiveUsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

`WeeklyActiveUsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

`WeeklyActiveUsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersSearchFilter`
    :   The type of the None singleton.

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

`WeeklyActiveUsersSearchQuery(*args, **kwargs)`
:   Search query for weekly_active_users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersEqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersNeqCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersGtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersGteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLtCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLteCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersInCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersLikeCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersContainsCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersNotCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersAndCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersOrCondition | airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_analytics_data_api.types.WeeklyActiveUsersSortFilter]`
    :   The type of the None singleton.

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