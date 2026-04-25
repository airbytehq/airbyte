---
id: airbyte_agent_sdk-connectors-google_search_console-types
title: airbyte_agent_sdk.connectors.google_search_console.types
---

Module airbyte_agent_sdk.connectors.google_search_console.types
===============================================================
Type definitions for google-search-console connector.

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

<a id="SearchAnalyticsAllFieldsAndCondition"></a>

`SearchAnalyticsAllFieldsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsAnyCondition]`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsAnyCondition"></a>

`SearchAnalyticsAllFieldsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsAnyValueFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsAnyValueFilter"></a>

`SearchAnalyticsAllFieldsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: Any`
    :   The number of times users clicked on the search result for a specific query

    `country: Any`
    :   The country from which the search query originated

    `ctr: Any`
    :   Click-through rate, calculated as clicks divided by impressions

    `date: Any`
    :   The date when the search query occurred

    `device: Any`
    :   The type of device used by the user (e.g., desktop, mobile)

    `impressions: Any`
    :   The number of times a search result appeared in response to a query

    `page: Any`
    :   The page URL that appeared in the search results

    `position: Any`
    :   The average position of the search result on the search engine results page

    `query: Any`
    :   The search query entered by the user

    `search_type: Any`
    :   The type of search (e.g., web, image, video) that triggered the search result

    `site_url: Any`
    :   The URL of the site from which the data originates

<a id="SearchAnalyticsAllFieldsContainsCondition"></a>

`SearchAnalyticsAllFieldsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsAnyValueFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsEqCondition"></a>

`SearchAnalyticsAllFieldsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsFuzzyCondition"></a>

`SearchAnalyticsAllFieldsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsGtCondition"></a>

`SearchAnalyticsAllFieldsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsGteCondition"></a>

`SearchAnalyticsAllFieldsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsInCondition"></a>

`SearchAnalyticsAllFieldsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsInFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsInFilter"></a>

`SearchAnalyticsAllFieldsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: list[int]`
    :   The number of times users clicked on the search result for a specific query

    `country: list[str]`
    :   The country from which the search query originated

    `ctr: list[float]`
    :   Click-through rate, calculated as clicks divided by impressions

    `date: list[str]`
    :   The date when the search query occurred

    `device: list[str]`
    :   The type of device used by the user (e.g., desktop, mobile)

    `impressions: list[int]`
    :   The number of times a search result appeared in response to a query

    `page: list[str]`
    :   The page URL that appeared in the search results

    `position: list[float]`
    :   The average position of the search result on the search engine results page

    `query: list[str]`
    :   The search query entered by the user

    `search_type: list[str]`
    :   The type of search (e.g., web, image, video) that triggered the search result

    `site_url: list[str]`
    :   The URL of the site from which the data originates

<a id="SearchAnalyticsAllFieldsKeywordCondition"></a>

`SearchAnalyticsAllFieldsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsLikeCondition"></a>

`SearchAnalyticsAllFieldsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsListParams"></a>

`SearchAnalyticsAllFieldsListParams(*args, **kwargs)`
:   Parameters for search_analytics_all_fields.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `aggregation_type: str`
    :   The type of the None singleton.

    `data_state: str`
    :   The type of the None singleton.

    `dimensions: list[str]`
    :   The type of the None singleton.

    `end_date: str`
    :   The type of the None singleton.

    `row_limit: int`
    :   The type of the None singleton.

    `site_url: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

    `start_row: int`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsLtCondition"></a>

`SearchAnalyticsAllFieldsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsLteCondition"></a>

`SearchAnalyticsAllFieldsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsNeqCondition"></a>

`SearchAnalyticsAllFieldsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsNotCondition"></a>

`SearchAnalyticsAllFieldsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsAnyCondition`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsOrCondition"></a>

`SearchAnalyticsAllFieldsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsAnyCondition]`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsSearchFilter"></a>

`SearchAnalyticsAllFieldsSearchFilter(*args, **kwargs)`
:   Available fields for filtering search_analytics_all_fields search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: int | None`
    :   The number of times users clicked on the search result for a specific query

    `country: str | None`
    :   The country from which the search query originated

    `ctr: float | None`
    :   Click-through rate, calculated as clicks divided by impressions

    `date: str | None`
    :   The date when the search query occurred

    `device: str | None`
    :   The type of device used by the user (e.g., desktop, mobile)

    `impressions: int | None`
    :   The number of times a search result appeared in response to a query

    `page: str | None`
    :   The page URL that appeared in the search results

    `position: float | None`
    :   The average position of the search result on the search engine results page

    `query: str | None`
    :   The search query entered by the user

    `search_type: str | None`
    :   The type of search (e.g., web, image, video) that triggered the search result

    `site_url: str | None`
    :   The URL of the site from which the data originates

<a id="SearchAnalyticsAllFieldsSearchQuery"></a>

`SearchAnalyticsAllFieldsSearchQuery(*args, **kwargs)`
:   Search query for search_analytics_all_fields entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsAllFieldsSortFilter]`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsSortFilter"></a>

`SearchAnalyticsAllFieldsSortFilter(*args, **kwargs)`
:   Available fields for sorting search_analytics_all_fields search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: Literal['asc', 'desc']`
    :   The number of times users clicked on the search result for a specific query

    `country: Literal['asc', 'desc']`
    :   The country from which the search query originated

    `ctr: Literal['asc', 'desc']`
    :   Click-through rate, calculated as clicks divided by impressions

    `date: Literal['asc', 'desc']`
    :   The date when the search query occurred

    `device: Literal['asc', 'desc']`
    :   The type of device used by the user (e.g., desktop, mobile)

    `impressions: Literal['asc', 'desc']`
    :   The number of times a search result appeared in response to a query

    `page: Literal['asc', 'desc']`
    :   The page URL that appeared in the search results

    `position: Literal['asc', 'desc']`
    :   The average position of the search result on the search engine results page

    `query: Literal['asc', 'desc']`
    :   The search query entered by the user

    `search_type: Literal['asc', 'desc']`
    :   The type of search (e.g., web, image, video) that triggered the search result

    `site_url: Literal['asc', 'desc']`
    :   The URL of the site from which the data originates

<a id="SearchAnalyticsAllFieldsStringFilter"></a>

`SearchAnalyticsAllFieldsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: str`
    :   The number of times users clicked on the search result for a specific query

    `country: str`
    :   The country from which the search query originated

    `ctr: str`
    :   Click-through rate, calculated as clicks divided by impressions

    `date: str`
    :   The date when the search query occurred

    `device: str`
    :   The type of device used by the user (e.g., desktop, mobile)

    `impressions: str`
    :   The number of times a search result appeared in response to a query

    `page: str`
    :   The page URL that appeared in the search results

    `position: str`
    :   The average position of the search result on the search engine results page

    `query: str`
    :   The search query entered by the user

    `search_type: str`
    :   The type of search (e.g., web, image, video) that triggered the search result

    `site_url: str`
    :   The URL of the site from which the data originates

<a id="SearchAnalyticsByCountryAndCondition"></a>

`SearchAnalyticsByCountryAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryAnyCondition]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryAnyCondition"></a>

`SearchAnalyticsByCountryAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryAnyValueFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryAnyValueFilter"></a>

`SearchAnalyticsByCountryAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: Any`
    :   The number of times users clicked on the search result for a specific country

    `country: Any`
    :   The country for which the search analytics data is being reported

    `ctr: Any`
    :   The click-through rate for a specific country

    `date: Any`
    :   The date for which the search analytics data is being reported

    `impressions: Any`
    :   The total number of times a search result was shown for a specific country

    `position: Any`
    :   The average position at which the site's search result appeared for a specific country

    `search_type: Any`
    :   The type of search for which the data is being reported

    `site_url: Any`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByCountryContainsCondition"></a>

`SearchAnalyticsByCountryContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryAnyValueFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryEqCondition"></a>

`SearchAnalyticsByCountryEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountrySearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryFuzzyCondition"></a>

`SearchAnalyticsByCountryFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryGtCondition"></a>

`SearchAnalyticsByCountryGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountrySearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryGteCondition"></a>

`SearchAnalyticsByCountryGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountrySearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryInCondition"></a>

`SearchAnalyticsByCountryInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryInFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryInFilter"></a>

`SearchAnalyticsByCountryInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: list[int]`
    :   The number of times users clicked on the search result for a specific country

    `country: list[str]`
    :   The country for which the search analytics data is being reported

    `ctr: list[float]`
    :   The click-through rate for a specific country

    `date: list[str]`
    :   The date for which the search analytics data is being reported

    `impressions: list[int]`
    :   The total number of times a search result was shown for a specific country

    `position: list[float]`
    :   The average position at which the site's search result appeared for a specific country

    `search_type: list[str]`
    :   The type of search for which the data is being reported

    `site_url: list[str]`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByCountryKeywordCondition"></a>

`SearchAnalyticsByCountryKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryLikeCondition"></a>

`SearchAnalyticsByCountryLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryListParams"></a>

`SearchAnalyticsByCountryListParams(*args, **kwargs)`
:   Parameters for search_analytics_by_country.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `aggregation_type: str`
    :   The type of the None singleton.

    `data_state: str`
    :   The type of the None singleton.

    `dimensions: list[str]`
    :   The type of the None singleton.

    `end_date: str`
    :   The type of the None singleton.

    `row_limit: int`
    :   The type of the None singleton.

    `site_url: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

    `start_row: int`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryLtCondition"></a>

`SearchAnalyticsByCountryLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountrySearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryLteCondition"></a>

`SearchAnalyticsByCountryLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountrySearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryNeqCondition"></a>

`SearchAnalyticsByCountryNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountrySearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryNotCondition"></a>

`SearchAnalyticsByCountryNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryAnyCondition`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryOrCondition"></a>

`SearchAnalyticsByCountryOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryAnyCondition]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountrySearchFilter"></a>

`SearchAnalyticsByCountrySearchFilter(*args, **kwargs)`
:   Available fields for filtering search_analytics_by_country search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: int | None`
    :   The number of times users clicked on the search result for a specific country

    `country: str | None`
    :   The country for which the search analytics data is being reported

    `ctr: float | None`
    :   The click-through rate for a specific country

    `date: str | None`
    :   The date for which the search analytics data is being reported

    `impressions: int | None`
    :   The total number of times a search result was shown for a specific country

    `position: float | None`
    :   The average position at which the site's search result appeared for a specific country

    `search_type: str | None`
    :   The type of search for which the data is being reported

    `site_url: str | None`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByCountrySearchQuery"></a>

`SearchAnalyticsByCountrySearchQuery(*args, **kwargs)`
:   Search query for search_analytics_by_country entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountryAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByCountrySortFilter]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountrySortFilter"></a>

`SearchAnalyticsByCountrySortFilter(*args, **kwargs)`
:   Available fields for sorting search_analytics_by_country search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: Literal['asc', 'desc']`
    :   The number of times users clicked on the search result for a specific country

    `country: Literal['asc', 'desc']`
    :   The country for which the search analytics data is being reported

    `ctr: Literal['asc', 'desc']`
    :   The click-through rate for a specific country

    `date: Literal['asc', 'desc']`
    :   The date for which the search analytics data is being reported

    `impressions: Literal['asc', 'desc']`
    :   The total number of times a search result was shown for a specific country

    `position: Literal['asc', 'desc']`
    :   The average position at which the site's search result appeared for a specific country

    `search_type: Literal['asc', 'desc']`
    :   The type of search for which the data is being reported

    `site_url: Literal['asc', 'desc']`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByCountryStringFilter"></a>

`SearchAnalyticsByCountryStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: str`
    :   The number of times users clicked on the search result for a specific country

    `country: str`
    :   The country for which the search analytics data is being reported

    `ctr: str`
    :   The click-through rate for a specific country

    `date: str`
    :   The date for which the search analytics data is being reported

    `impressions: str`
    :   The total number of times a search result was shown for a specific country

    `position: str`
    :   The average position at which the site's search result appeared for a specific country

    `search_type: str`
    :   The type of search for which the data is being reported

    `site_url: str`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByDateAndCondition"></a>

`SearchAnalyticsByDateAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateAnyCondition]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateAnyCondition"></a>

`SearchAnalyticsByDateAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateAnyValueFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateAnyValueFilter"></a>

`SearchAnalyticsByDateAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: Any`
    :   The total number of clicks on the specific date

    `ctr: Any`
    :   The click-through rate for the specific date

    `date: Any`
    :   The date for which the search analytics data is being reported

    `impressions: Any`
    :   The number of impressions on the specific date

    `position: Any`
    :   The average position in search results for the specific date

    `search_type: Any`
    :   The type of search query that generated the data

    `site_url: Any`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByDateContainsCondition"></a>

`SearchAnalyticsByDateContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateAnyValueFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateEqCondition"></a>

`SearchAnalyticsByDateEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateFuzzyCondition"></a>

`SearchAnalyticsByDateFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateGtCondition"></a>

`SearchAnalyticsByDateGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateGteCondition"></a>

`SearchAnalyticsByDateGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateInCondition"></a>

`SearchAnalyticsByDateInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateInFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateInFilter"></a>

`SearchAnalyticsByDateInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: list[int]`
    :   The total number of clicks on the specific date

    `ctr: list[float]`
    :   The click-through rate for the specific date

    `date: list[str]`
    :   The date for which the search analytics data is being reported

    `impressions: list[int]`
    :   The number of impressions on the specific date

    `position: list[float]`
    :   The average position in search results for the specific date

    `search_type: list[str]`
    :   The type of search query that generated the data

    `site_url: list[str]`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByDateKeywordCondition"></a>

`SearchAnalyticsByDateKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateLikeCondition"></a>

`SearchAnalyticsByDateLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateListParams"></a>

`SearchAnalyticsByDateListParams(*args, **kwargs)`
:   Parameters for search_analytics_by_date.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `aggregation_type: str`
    :   The type of the None singleton.

    `data_state: str`
    :   The type of the None singleton.

    `dimensions: list[str]`
    :   The type of the None singleton.

    `end_date: str`
    :   The type of the None singleton.

    `row_limit: int`
    :   The type of the None singleton.

    `site_url: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

    `start_row: int`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateLtCondition"></a>

`SearchAnalyticsByDateLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateLteCondition"></a>

`SearchAnalyticsByDateLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateNeqCondition"></a>

`SearchAnalyticsByDateNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateNotCondition"></a>

`SearchAnalyticsByDateNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateAnyCondition`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateOrCondition"></a>

`SearchAnalyticsByDateOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateAnyCondition]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateSearchFilter"></a>

`SearchAnalyticsByDateSearchFilter(*args, **kwargs)`
:   Available fields for filtering search_analytics_by_date search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: int | None`
    :   The total number of clicks on the specific date

    `ctr: float | None`
    :   The click-through rate for the specific date

    `date: str | None`
    :   The date for which the search analytics data is being reported

    `impressions: int | None`
    :   The number of impressions on the specific date

    `position: float | None`
    :   The average position in search results for the specific date

    `search_type: str | None`
    :   The type of search query that generated the data

    `site_url: str | None`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByDateSearchQuery"></a>

`SearchAnalyticsByDateSearchQuery(*args, **kwargs)`
:   Search query for search_analytics_by_date entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDateSortFilter]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateSortFilter"></a>

`SearchAnalyticsByDateSortFilter(*args, **kwargs)`
:   Available fields for sorting search_analytics_by_date search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: Literal['asc', 'desc']`
    :   The total number of clicks on the specific date

    `ctr: Literal['asc', 'desc']`
    :   The click-through rate for the specific date

    `date: Literal['asc', 'desc']`
    :   The date for which the search analytics data is being reported

    `impressions: Literal['asc', 'desc']`
    :   The number of impressions on the specific date

    `position: Literal['asc', 'desc']`
    :   The average position in search results for the specific date

    `search_type: Literal['asc', 'desc']`
    :   The type of search query that generated the data

    `site_url: Literal['asc', 'desc']`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByDateStringFilter"></a>

`SearchAnalyticsByDateStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: str`
    :   The total number of clicks on the specific date

    `ctr: str`
    :   The click-through rate for the specific date

    `date: str`
    :   The date for which the search analytics data is being reported

    `impressions: str`
    :   The number of impressions on the specific date

    `position: str`
    :   The average position in search results for the specific date

    `search_type: str`
    :   The type of search query that generated the data

    `site_url: str`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByDeviceAndCondition"></a>

`SearchAnalyticsByDeviceAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceAnyCondition]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceAnyCondition"></a>

`SearchAnalyticsByDeviceAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceAnyValueFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceAnyValueFilter"></a>

`SearchAnalyticsByDeviceAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: Any`
    :   The total number of clicks by device type

    `ctr: Any`
    :   Click-through rate by device type

    `date: Any`
    :   The date for which the search analytics data is provided

    `device: Any`
    :   The type of device used by the user (e.g., desktop, mobile)

    `impressions: Any`
    :   The total number of impressions by device type

    `position: Any`
    :   The average position in search results by device type

    `search_type: Any`
    :   The type of search performed

    `site_url: Any`
    :   The URL of the site for which search analytics data is being provided

<a id="SearchAnalyticsByDeviceContainsCondition"></a>

`SearchAnalyticsByDeviceContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceAnyValueFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceEqCondition"></a>

`SearchAnalyticsByDeviceEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceFuzzyCondition"></a>

`SearchAnalyticsByDeviceFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceGtCondition"></a>

`SearchAnalyticsByDeviceGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceGteCondition"></a>

`SearchAnalyticsByDeviceGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceInCondition"></a>

`SearchAnalyticsByDeviceInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceInFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceInFilter"></a>

`SearchAnalyticsByDeviceInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: list[int]`
    :   The total number of clicks by device type

    `ctr: list[float]`
    :   Click-through rate by device type

    `date: list[str]`
    :   The date for which the search analytics data is provided

    `device: list[str]`
    :   The type of device used by the user (e.g., desktop, mobile)

    `impressions: list[int]`
    :   The total number of impressions by device type

    `position: list[float]`
    :   The average position in search results by device type

    `search_type: list[str]`
    :   The type of search performed

    `site_url: list[str]`
    :   The URL of the site for which search analytics data is being provided

<a id="SearchAnalyticsByDeviceKeywordCondition"></a>

`SearchAnalyticsByDeviceKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceLikeCondition"></a>

`SearchAnalyticsByDeviceLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceListParams"></a>

`SearchAnalyticsByDeviceListParams(*args, **kwargs)`
:   Parameters for search_analytics_by_device.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `aggregation_type: str`
    :   The type of the None singleton.

    `data_state: str`
    :   The type of the None singleton.

    `dimensions: list[str]`
    :   The type of the None singleton.

    `end_date: str`
    :   The type of the None singleton.

    `row_limit: int`
    :   The type of the None singleton.

    `site_url: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

    `start_row: int`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceLtCondition"></a>

`SearchAnalyticsByDeviceLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceLteCondition"></a>

`SearchAnalyticsByDeviceLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceNeqCondition"></a>

`SearchAnalyticsByDeviceNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceNotCondition"></a>

`SearchAnalyticsByDeviceNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceAnyCondition`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceOrCondition"></a>

`SearchAnalyticsByDeviceOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceAnyCondition]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceSearchFilter"></a>

`SearchAnalyticsByDeviceSearchFilter(*args, **kwargs)`
:   Available fields for filtering search_analytics_by_device search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: int | None`
    :   The total number of clicks by device type

    `ctr: float | None`
    :   Click-through rate by device type

    `date: str | None`
    :   The date for which the search analytics data is provided

    `device: str | None`
    :   The type of device used by the user (e.g., desktop, mobile)

    `impressions: int | None`
    :   The total number of impressions by device type

    `position: float | None`
    :   The average position in search results by device type

    `search_type: str | None`
    :   The type of search performed

    `site_url: str | None`
    :   The URL of the site for which search analytics data is being provided

<a id="SearchAnalyticsByDeviceSearchQuery"></a>

`SearchAnalyticsByDeviceSearchQuery(*args, **kwargs)`
:   Search query for search_analytics_by_device entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByDeviceSortFilter]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceSortFilter"></a>

`SearchAnalyticsByDeviceSortFilter(*args, **kwargs)`
:   Available fields for sorting search_analytics_by_device search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: Literal['asc', 'desc']`
    :   The total number of clicks by device type

    `ctr: Literal['asc', 'desc']`
    :   Click-through rate by device type

    `date: Literal['asc', 'desc']`
    :   The date for which the search analytics data is provided

    `device: Literal['asc', 'desc']`
    :   The type of device used by the user (e.g., desktop, mobile)

    `impressions: Literal['asc', 'desc']`
    :   The total number of impressions by device type

    `position: Literal['asc', 'desc']`
    :   The average position in search results by device type

    `search_type: Literal['asc', 'desc']`
    :   The type of search performed

    `site_url: Literal['asc', 'desc']`
    :   The URL of the site for which search analytics data is being provided

<a id="SearchAnalyticsByDeviceStringFilter"></a>

`SearchAnalyticsByDeviceStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: str`
    :   The total number of clicks by device type

    `ctr: str`
    :   Click-through rate by device type

    `date: str`
    :   The date for which the search analytics data is provided

    `device: str`
    :   The type of device used by the user (e.g., desktop, mobile)

    `impressions: str`
    :   The total number of impressions by device type

    `position: str`
    :   The average position in search results by device type

    `search_type: str`
    :   The type of search performed

    `site_url: str`
    :   The URL of the site for which search analytics data is being provided

<a id="SearchAnalyticsByPageAndCondition"></a>

`SearchAnalyticsByPageAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageAnyCondition]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageAnyCondition"></a>

`SearchAnalyticsByPageAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageAnyValueFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageAnyValueFilter"></a>

`SearchAnalyticsByPageAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: Any`
    :   The number of clicks for a specific page

    `ctr: Any`
    :   Click-through rate for the page

    `date: Any`
    :   The date for which the search analytics data is reported

    `impressions: Any`
    :   The number of impressions for the page

    `page: Any`
    :   The URL of the specific page being analyzed

    `position: Any`
    :   The average position at which the page appeared in search results

    `search_type: Any`
    :   The type of search query that led to the page being displayed

    `site_url: Any`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByPageContainsCondition"></a>

`SearchAnalyticsByPageContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageAnyValueFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageEqCondition"></a>

`SearchAnalyticsByPageEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageFuzzyCondition"></a>

`SearchAnalyticsByPageFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageGtCondition"></a>

`SearchAnalyticsByPageGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageGteCondition"></a>

`SearchAnalyticsByPageGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageInCondition"></a>

`SearchAnalyticsByPageInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageInFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageInFilter"></a>

`SearchAnalyticsByPageInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: list[int]`
    :   The number of clicks for a specific page

    `ctr: list[float]`
    :   Click-through rate for the page

    `date: list[str]`
    :   The date for which the search analytics data is reported

    `impressions: list[int]`
    :   The number of impressions for the page

    `page: list[str]`
    :   The URL of the specific page being analyzed

    `position: list[float]`
    :   The average position at which the page appeared in search results

    `search_type: list[str]`
    :   The type of search query that led to the page being displayed

    `site_url: list[str]`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByPageKeywordCondition"></a>

`SearchAnalyticsByPageKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageLikeCondition"></a>

`SearchAnalyticsByPageLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageListParams"></a>

`SearchAnalyticsByPageListParams(*args, **kwargs)`
:   Parameters for search_analytics_by_page.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `aggregation_type: str`
    :   The type of the None singleton.

    `data_state: str`
    :   The type of the None singleton.

    `dimensions: list[str]`
    :   The type of the None singleton.

    `end_date: str`
    :   The type of the None singleton.

    `row_limit: int`
    :   The type of the None singleton.

    `site_url: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

    `start_row: int`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageLtCondition"></a>

`SearchAnalyticsByPageLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageLteCondition"></a>

`SearchAnalyticsByPageLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageNeqCondition"></a>

`SearchAnalyticsByPageNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageSearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageNotCondition"></a>

`SearchAnalyticsByPageNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageAnyCondition`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageOrCondition"></a>

`SearchAnalyticsByPageOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageAnyCondition]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageSearchFilter"></a>

`SearchAnalyticsByPageSearchFilter(*args, **kwargs)`
:   Available fields for filtering search_analytics_by_page search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: int | None`
    :   The number of clicks for a specific page

    `ctr: float | None`
    :   Click-through rate for the page

    `date: str | None`
    :   The date for which the search analytics data is reported

    `impressions: int | None`
    :   The number of impressions for the page

    `page: str | None`
    :   The URL of the specific page being analyzed

    `position: float | None`
    :   The average position at which the page appeared in search results

    `search_type: str | None`
    :   The type of search query that led to the page being displayed

    `site_url: str | None`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByPageSearchQuery"></a>

`SearchAnalyticsByPageSearchQuery(*args, **kwargs)`
:   Search query for search_analytics_by_page entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByPageSortFilter]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageSortFilter"></a>

`SearchAnalyticsByPageSortFilter(*args, **kwargs)`
:   Available fields for sorting search_analytics_by_page search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: Literal['asc', 'desc']`
    :   The number of clicks for a specific page

    `ctr: Literal['asc', 'desc']`
    :   Click-through rate for the page

    `date: Literal['asc', 'desc']`
    :   The date for which the search analytics data is reported

    `impressions: Literal['asc', 'desc']`
    :   The number of impressions for the page

    `page: Literal['asc', 'desc']`
    :   The URL of the specific page being analyzed

    `position: Literal['asc', 'desc']`
    :   The average position at which the page appeared in search results

    `search_type: Literal['asc', 'desc']`
    :   The type of search query that led to the page being displayed

    `site_url: Literal['asc', 'desc']`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByPageStringFilter"></a>

`SearchAnalyticsByPageStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: str`
    :   The number of clicks for a specific page

    `ctr: str`
    :   Click-through rate for the page

    `date: str`
    :   The date for which the search analytics data is reported

    `impressions: str`
    :   The number of impressions for the page

    `page: str`
    :   The URL of the specific page being analyzed

    `position: str`
    :   The average position at which the page appeared in search results

    `search_type: str`
    :   The type of search query that led to the page being displayed

    `site_url: str`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByQueryAndCondition"></a>

`SearchAnalyticsByQueryAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryAnyCondition]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryAnyCondition"></a>

`SearchAnalyticsByQueryAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryAnyValueFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryAnyValueFilter"></a>

`SearchAnalyticsByQueryAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: Any`
    :   The number of clicks for the specific query

    `ctr: Any`
    :   The click-through rate for the specific query

    `date: Any`
    :   The date for which the search analytics data is recorded

    `impressions: Any`
    :   The number of impressions for the specific query

    `position: Any`
    :   The average position for the specific query

    `query: Any`
    :   The search query for which the data is recorded

    `search_type: Any`
    :   The type of search result for the specific query

    `site_url: Any`
    :   The URL of the site for which the search analytics data is captured

<a id="SearchAnalyticsByQueryContainsCondition"></a>

`SearchAnalyticsByQueryContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryAnyValueFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryEqCondition"></a>

`SearchAnalyticsByQueryEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQuerySearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryFuzzyCondition"></a>

`SearchAnalyticsByQueryFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryGtCondition"></a>

`SearchAnalyticsByQueryGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQuerySearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryGteCondition"></a>

`SearchAnalyticsByQueryGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQuerySearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryInCondition"></a>

`SearchAnalyticsByQueryInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryInFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryInFilter"></a>

`SearchAnalyticsByQueryInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: list[int]`
    :   The number of clicks for the specific query

    `ctr: list[float]`
    :   The click-through rate for the specific query

    `date: list[str]`
    :   The date for which the search analytics data is recorded

    `impressions: list[int]`
    :   The number of impressions for the specific query

    `position: list[float]`
    :   The average position for the specific query

    `query: list[str]`
    :   The search query for which the data is recorded

    `search_type: list[str]`
    :   The type of search result for the specific query

    `site_url: list[str]`
    :   The URL of the site for which the search analytics data is captured

<a id="SearchAnalyticsByQueryKeywordCondition"></a>

`SearchAnalyticsByQueryKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryLikeCondition"></a>

`SearchAnalyticsByQueryLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryStringFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryListParams"></a>

`SearchAnalyticsByQueryListParams(*args, **kwargs)`
:   Parameters for search_analytics_by_query.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `aggregation_type: str`
    :   The type of the None singleton.

    `data_state: str`
    :   The type of the None singleton.

    `dimensions: list[str]`
    :   The type of the None singleton.

    `end_date: str`
    :   The type of the None singleton.

    `row_limit: int`
    :   The type of the None singleton.

    `site_url: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

    `start_row: int`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryLtCondition"></a>

`SearchAnalyticsByQueryLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQuerySearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryLteCondition"></a>

`SearchAnalyticsByQueryLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQuerySearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryNeqCondition"></a>

`SearchAnalyticsByQueryNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQuerySearchFilter`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryNotCondition"></a>

`SearchAnalyticsByQueryNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryAnyCondition`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryOrCondition"></a>

`SearchAnalyticsByQueryOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryAnyCondition]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQuerySearchFilter"></a>

`SearchAnalyticsByQuerySearchFilter(*args, **kwargs)`
:   Available fields for filtering search_analytics_by_query search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: int | None`
    :   The number of clicks for the specific query

    `ctr: float | None`
    :   The click-through rate for the specific query

    `date: str | None`
    :   The date for which the search analytics data is recorded

    `impressions: int | None`
    :   The number of impressions for the specific query

    `position: float | None`
    :   The average position for the specific query

    `query: str | None`
    :   The search query for which the data is recorded

    `search_type: str | None`
    :   The type of search result for the specific query

    `site_url: str | None`
    :   The URL of the site for which the search analytics data is captured

<a id="SearchAnalyticsByQuerySearchQuery"></a>

`SearchAnalyticsByQuerySearchQuery(*args, **kwargs)`
:   Search query for search_analytics_by_query entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQueryAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_search_console.types.SearchAnalyticsByQuerySortFilter]`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQuerySortFilter"></a>

`SearchAnalyticsByQuerySortFilter(*args, **kwargs)`
:   Available fields for sorting search_analytics_by_query search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: Literal['asc', 'desc']`
    :   The number of clicks for the specific query

    `ctr: Literal['asc', 'desc']`
    :   The click-through rate for the specific query

    `date: Literal['asc', 'desc']`
    :   The date for which the search analytics data is recorded

    `impressions: Literal['asc', 'desc']`
    :   The number of impressions for the specific query

    `position: Literal['asc', 'desc']`
    :   The average position for the specific query

    `query: Literal['asc', 'desc']`
    :   The search query for which the data is recorded

    `search_type: Literal['asc', 'desc']`
    :   The type of search result for the specific query

    `site_url: Literal['asc', 'desc']`
    :   The URL of the site for which the search analytics data is captured

<a id="SearchAnalyticsByQueryStringFilter"></a>

`SearchAnalyticsByQueryStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clicks: str`
    :   The number of clicks for the specific query

    `ctr: str`
    :   The click-through rate for the specific query

    `date: str`
    :   The date for which the search analytics data is recorded

    `impressions: str`
    :   The number of impressions for the specific query

    `position: str`
    :   The average position for the specific query

    `query: str`
    :   The search query for which the data is recorded

    `search_type: str`
    :   The type of search result for the specific query

    `site_url: str`
    :   The URL of the site for which the search analytics data is captured

<a id="SitemapsAndCondition"></a>

`SitemapsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_search_console.types.SitemapsEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsAnyCondition]`
    :   The type of the None singleton.

<a id="SitemapsAnyCondition"></a>

`SitemapsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_search_console.types.SitemapsAnyValueFilter`
    :   The type of the None singleton.

<a id="SitemapsAnyValueFilter"></a>

`SitemapsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contents: Any`
    :   Data related to the sitemap contents

    `errors: Any`
    :   Errors encountered while processing the sitemaps

    `is_pending: Any`
    :   Flag indicating if the sitemap is pending for processing

    `is_sitemaps_index: Any`
    :   Flag indicating if the data represents a sitemap index

    `last_downloaded: Any`
    :   Timestamp when the sitemap was last downloaded

    `last_submitted: Any`
    :   Timestamp when the sitemap was last submitted

    `path: Any`
    :   Path to the sitemap file

    `type_: Any`
    :   Type of the sitemap

    `warnings: Any`
    :   Warnings encountered while processing the sitemaps

<a id="SitemapsContainsCondition"></a>

`SitemapsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_search_console.types.SitemapsAnyValueFilter`
    :   The type of the None singleton.

<a id="SitemapsEqCondition"></a>

`SitemapsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_search_console.types.SitemapsSearchFilter`
    :   The type of the None singleton.

<a id="SitemapsFuzzyCondition"></a>

`SitemapsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_search_console.types.SitemapsStringFilter`
    :   The type of the None singleton.

<a id="SitemapsGetParams"></a>

`SitemapsGetParams(*args, **kwargs)`
:   Parameters for sitemaps.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `feedpath: str`
    :   The type of the None singleton.

    `site_url: str`
    :   The type of the None singleton.

<a id="SitemapsGtCondition"></a>

`SitemapsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_search_console.types.SitemapsSearchFilter`
    :   The type of the None singleton.

<a id="SitemapsGteCondition"></a>

`SitemapsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_search_console.types.SitemapsSearchFilter`
    :   The type of the None singleton.

<a id="SitemapsInCondition"></a>

`SitemapsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_search_console.types.SitemapsInFilter`
    :   The type of the None singleton.

<a id="SitemapsInFilter"></a>

`SitemapsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contents: list[list[typing.Any]]`
    :   Data related to the sitemap contents

    `errors: list[str]`
    :   Errors encountered while processing the sitemaps

    `is_pending: list[bool]`
    :   Flag indicating if the sitemap is pending for processing

    `is_sitemaps_index: list[bool]`
    :   Flag indicating if the data represents a sitemap index

    `last_downloaded: list[str]`
    :   Timestamp when the sitemap was last downloaded

    `last_submitted: list[str]`
    :   Timestamp when the sitemap was last submitted

    `path: list[str]`
    :   Path to the sitemap file

    `type_: list[str]`
    :   Type of the sitemap

    `warnings: list[str]`
    :   Warnings encountered while processing the sitemaps

<a id="SitemapsKeywordCondition"></a>

`SitemapsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_search_console.types.SitemapsStringFilter`
    :   The type of the None singleton.

<a id="SitemapsLikeCondition"></a>

`SitemapsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_search_console.types.SitemapsStringFilter`
    :   The type of the None singleton.

<a id="SitemapsListParams"></a>

`SitemapsListParams(*args, **kwargs)`
:   Parameters for sitemaps.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `site_url: str`
    :   The type of the None singleton.

<a id="SitemapsLtCondition"></a>

`SitemapsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_search_console.types.SitemapsSearchFilter`
    :   The type of the None singleton.

<a id="SitemapsLteCondition"></a>

`SitemapsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_search_console.types.SitemapsSearchFilter`
    :   The type of the None singleton.

<a id="SitemapsNeqCondition"></a>

`SitemapsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_search_console.types.SitemapsSearchFilter`
    :   The type of the None singleton.

<a id="SitemapsNotCondition"></a>

`SitemapsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_search_console.types.SitemapsEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsAnyCondition`
    :   The type of the None singleton.

<a id="SitemapsOrCondition"></a>

`SitemapsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_search_console.types.SitemapsEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsAnyCondition]`
    :   The type of the None singleton.

<a id="SitemapsSearchFilter"></a>

`SitemapsSearchFilter(*args, **kwargs)`
:   Available fields for filtering sitemaps search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contents: list[typing.Any] | None`
    :   Data related to the sitemap contents

    `errors: str | None`
    :   Errors encountered while processing the sitemaps

    `is_pending: bool | None`
    :   Flag indicating if the sitemap is pending for processing

    `is_sitemaps_index: bool | None`
    :   Flag indicating if the data represents a sitemap index

    `last_downloaded: str | None`
    :   Timestamp when the sitemap was last downloaded

    `last_submitted: str | None`
    :   Timestamp when the sitemap was last submitted

    `path: str | None`
    :   Path to the sitemap file

    `type_: str | None`
    :   Type of the sitemap

    `warnings: str | None`
    :   Warnings encountered while processing the sitemaps

<a id="SitemapsSearchQuery"></a>

`SitemapsSearchQuery(*args, **kwargs)`
:   Search query for sitemaps entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_search_console.types.SitemapsEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitemapsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_search_console.types.SitemapsSortFilter]`
    :   The type of the None singleton.

<a id="SitemapsSortFilter"></a>

`SitemapsSortFilter(*args, **kwargs)`
:   Available fields for sorting sitemaps search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contents: Literal['asc', 'desc']`
    :   Data related to the sitemap contents

    `errors: Literal['asc', 'desc']`
    :   Errors encountered while processing the sitemaps

    `is_pending: Literal['asc', 'desc']`
    :   Flag indicating if the sitemap is pending for processing

    `is_sitemaps_index: Literal['asc', 'desc']`
    :   Flag indicating if the data represents a sitemap index

    `last_downloaded: Literal['asc', 'desc']`
    :   Timestamp when the sitemap was last downloaded

    `last_submitted: Literal['asc', 'desc']`
    :   Timestamp when the sitemap was last submitted

    `path: Literal['asc', 'desc']`
    :   Path to the sitemap file

    `type_: Literal['asc', 'desc']`
    :   Type of the sitemap

    `warnings: Literal['asc', 'desc']`
    :   Warnings encountered while processing the sitemaps

<a id="SitemapsStringFilter"></a>

`SitemapsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contents: str`
    :   Data related to the sitemap contents

    `errors: str`
    :   Errors encountered while processing the sitemaps

    `is_pending: str`
    :   Flag indicating if the sitemap is pending for processing

    `is_sitemaps_index: str`
    :   Flag indicating if the data represents a sitemap index

    `last_downloaded: str`
    :   Timestamp when the sitemap was last downloaded

    `last_submitted: str`
    :   Timestamp when the sitemap was last submitted

    `path: str`
    :   Path to the sitemap file

    `type_: str`
    :   Type of the sitemap

    `warnings: str`
    :   Warnings encountered while processing the sitemaps

<a id="SitesAndCondition"></a>

`SitesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_search_console.types.SitesEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesAnyCondition]`
    :   The type of the None singleton.

<a id="SitesAnyCondition"></a>

`SitesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_search_console.types.SitesAnyValueFilter`
    :   The type of the None singleton.

<a id="SitesAnyValueFilter"></a>

`SitesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `permission_level: Any`
    :   The user's permission level for the site (owner, full, restricted, etc.)

    `site_url: Any`
    :   The URL of the site data being fetched

<a id="SitesContainsCondition"></a>

`SitesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_search_console.types.SitesAnyValueFilter`
    :   The type of the None singleton.

<a id="SitesEqCondition"></a>

`SitesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_search_console.types.SitesSearchFilter`
    :   The type of the None singleton.

<a id="SitesFuzzyCondition"></a>

`SitesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_search_console.types.SitesStringFilter`
    :   The type of the None singleton.

<a id="SitesGetParams"></a>

`SitesGetParams(*args, **kwargs)`
:   Parameters for sites.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `site_url: str`
    :   The type of the None singleton.

<a id="SitesGtCondition"></a>

`SitesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_search_console.types.SitesSearchFilter`
    :   The type of the None singleton.

<a id="SitesGteCondition"></a>

`SitesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_search_console.types.SitesSearchFilter`
    :   The type of the None singleton.

<a id="SitesInCondition"></a>

`SitesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_search_console.types.SitesInFilter`
    :   The type of the None singleton.

<a id="SitesInFilter"></a>

`SitesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `permission_level: list[str]`
    :   The user's permission level for the site (owner, full, restricted, etc.)

    `site_url: list[str]`
    :   The URL of the site data being fetched

<a id="SitesKeywordCondition"></a>

`SitesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_search_console.types.SitesStringFilter`
    :   The type of the None singleton.

<a id="SitesLikeCondition"></a>

`SitesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_search_console.types.SitesStringFilter`
    :   The type of the None singleton.

<a id="SitesListParams"></a>

`SitesListParams(*args, **kwargs)`
:   Parameters for sites.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="SitesLtCondition"></a>

`SitesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_search_console.types.SitesSearchFilter`
    :   The type of the None singleton.

<a id="SitesLteCondition"></a>

`SitesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_search_console.types.SitesSearchFilter`
    :   The type of the None singleton.

<a id="SitesNeqCondition"></a>

`SitesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_search_console.types.SitesSearchFilter`
    :   The type of the None singleton.

<a id="SitesNotCondition"></a>

`SitesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_search_console.types.SitesEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesAnyCondition`
    :   The type of the None singleton.

<a id="SitesOrCondition"></a>

`SitesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_search_console.types.SitesEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesAnyCondition]`
    :   The type of the None singleton.

<a id="SitesSearchFilter"></a>

`SitesSearchFilter(*args, **kwargs)`
:   Available fields for filtering sites search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `permission_level: str | None`
    :   The user's permission level for the site (owner, full, restricted, etc.)

    `site_url: str | None`
    :   The URL of the site data being fetched

<a id="SitesSearchQuery"></a>

`SitesSearchQuery(*args, **kwargs)`
:   Search query for sites entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_search_console.types.SitesEqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesNeqCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesGtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesGteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesLtCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesLteCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesInCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesLikeCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesFuzzyCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesKeywordCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesContainsCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesNotCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesAndCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesOrCondition | airbyte_agent_sdk.connectors.google_search_console.types.SitesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_search_console.types.SitesSortFilter]`
    :   The type of the None singleton.

<a id="SitesSortFilter"></a>

`SitesSortFilter(*args, **kwargs)`
:   Available fields for sorting sites search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `permission_level: Literal['asc', 'desc']`
    :   The user's permission level for the site (owner, full, restricted, etc.)

    `site_url: Literal['asc', 'desc']`
    :   The URL of the site data being fetched

<a id="SitesStringFilter"></a>

`SitesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `permission_level: str`
    :   The user's permission level for the site (owner, full, restricted, etc.)

    `site_url: str`
    :   The URL of the site data being fetched