---
id: airbyte_agent_sdk-connectors-google_search_console-models
title: airbyte_agent_sdk.connectors.google_search_console.models
---

Module airbyte_agent_sdk.connectors.google_search_console.models
================================================================
Pydantic models for google-search-console connector.

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

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsAllFieldsSearchData]
    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByCountrySearchData]
    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByDateSearchData]
    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByDeviceSearchData]
    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByPageSearchData]
    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByQuerySearchData]
    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SitemapsSearchData]
    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SitesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[SearchAnalyticsAllFieldsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsSearchResult"></a>

`SearchAnalyticsAllFieldsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SearchAnalyticsByCountrySearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountrySearchResult"></a>

`SearchAnalyticsByCountrySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SearchAnalyticsByDateSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateSearchResult"></a>

`SearchAnalyticsByDateSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SearchAnalyticsByDeviceSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceSearchResult"></a>

`SearchAnalyticsByDeviceSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SearchAnalyticsByPageSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageSearchResult"></a>

`SearchAnalyticsByPageSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SearchAnalyticsByQuerySearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQuerySearchResult"></a>

`SearchAnalyticsByQuerySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SitemapsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SitemapsSearchResult"></a>

`SitemapsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SitesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SitesSearchResult"></a>

`SitesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GoogleSearchConsoleAuthConfig"></a>

`GoogleSearchConsoleAuthConfig(**data: Any)`
:   OAuth2 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   The client ID of your Google Search Console developer application.

    `client_secret: str`
    :   The client secret of your Google Search Console developer application.

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   The refresh token for obtaining new access tokens.

<a id="GoogleSearchConsoleCheckResult"></a>

`GoogleSearchConsoleCheckResult(**data: Any)`
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

<a id="GoogleSearchConsoleExecuteResult"></a>

`GoogleSearchConsoleExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult[list[Site]]
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult[list[Sitemap]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="GoogleSearchConsoleExecuteResultWithMeta"></a>

`GoogleSearchConsoleExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsAllFieldsListResultMeta]
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByCountryListResultMeta]
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByDateListResultMeta]
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByDeviceListResultMeta]
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByPageListResultMeta]
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByQueryListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsAllFieldsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsListResult"></a>

`SearchAnalyticsAllFieldsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByCountryListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryListResult"></a>

`SearchAnalyticsByCountryListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByDateListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateListResult"></a>

`SearchAnalyticsByDateListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByDeviceListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceListResult"></a>

`SearchAnalyticsByDeviceListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByPageListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageListResult"></a>

`SearchAnalyticsByPageListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByQueryListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryListResult"></a>

`SearchAnalyticsByQueryListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleSearchConsoleExecuteResult[list[Site]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SitesListResult"></a>

`SitesListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleSearchConsoleExecuteResult[list[Sitemap]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SitemapsListResult"></a>

`SitemapsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GoogleSearchConsoleReplicationConfig"></a>

`GoogleSearchConsoleReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Google Search Console.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `site_urls: str`
    :   The URLs of the website property attached to your GSC account. Examples: https://example.com/ or sc-domain:example.com

    `start_date: str | None`
    :   UTC date in the format YYYY-MM-DD. Any data before this date will not be replicated.

<a id="SearchAnalyticsAllFieldsListResultMeta"></a>

`SearchAnalyticsAllFieldsListResultMeta(**data: Any)`
:   Metadata for search_analytics_all_fields.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `response_aggregation_type: str | Any | None`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsRequest"></a>

`SearchAnalyticsAllFieldsRequest(**data: Any)`
:   Request body for search analytics query grouped by all dimensions.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `aggregation_type: str | Any`
    :   The type of the None singleton.

    `data_state: str | Any`
    :   The type of the None singleton.

    `dimensions: list[str] | Any`
    :   The type of the None singleton.

    `end_date: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `row_limit: int | Any`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   The type of the None singleton.

    `start_row: int | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsSearchData"></a>

`SearchAnalyticsAllFieldsSearchData(**data: Any)`
:   Search result data for search_analytics_all_fields entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="SearchAnalyticsByCountryListResultMeta"></a>

`SearchAnalyticsByCountryListResultMeta(**data: Any)`
:   Metadata for search_analytics_by_country.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `response_aggregation_type: str | Any | None`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountryRequest"></a>

`SearchAnalyticsByCountryRequest(**data: Any)`
:   Request body for search analytics query grouped by date and country.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `aggregation_type: str | Any`
    :   The type of the None singleton.

    `data_state: str | Any`
    :   The type of the None singleton.

    `dimensions: list[str] | Any`
    :   The type of the None singleton.

    `end_date: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `row_limit: int | Any`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   The type of the None singleton.

    `start_row: int | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="SearchAnalyticsByCountrySearchData"></a>

`SearchAnalyticsByCountrySearchData(**data: Any)`
:   Search result data for search_analytics_by_country entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

    `position: float | None`
    :   The average position at which the site's search result appeared for a specific country

    `search_type: str | None`
    :   The type of search for which the data is being reported

    `site_url: str | None`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByDateListResultMeta"></a>

`SearchAnalyticsByDateListResultMeta(**data: Any)`
:   Metadata for search_analytics_by_date.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `response_aggregation_type: str | Any | None`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateRequest"></a>

`SearchAnalyticsByDateRequest(**data: Any)`
:   Request body for search analytics query grouped by date.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `aggregation_type: str | Any`
    :   The type of the None singleton.

    `data_state: str | Any`
    :   The type of the None singleton.

    `dimensions: list[str] | Any`
    :   The type of the None singleton.

    `end_date: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `row_limit: int | Any`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   The type of the None singleton.

    `start_row: int | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDateSearchData"></a>

`SearchAnalyticsByDateSearchData(**data: Any)`
:   Search result data for search_analytics_by_date entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clicks: int | None`
    :   The total number of clicks on the specific date

    `ctr: float | None`
    :   The click-through rate for the specific date

    `date: str | None`
    :   The date for which the search analytics data is being reported

    `impressions: int | None`
    :   The number of impressions on the specific date

    `model_config`
    :   The type of the None singleton.

    `position: float | None`
    :   The average position in search results for the specific date

    `search_type: str | None`
    :   The type of search query that generated the data

    `site_url: str | None`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByDeviceListResultMeta"></a>

`SearchAnalyticsByDeviceListResultMeta(**data: Any)`
:   Metadata for search_analytics_by_device.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `response_aggregation_type: str | Any | None`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceRequest"></a>

`SearchAnalyticsByDeviceRequest(**data: Any)`
:   Request body for search analytics query grouped by date and device.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `aggregation_type: str | Any`
    :   The type of the None singleton.

    `data_state: str | Any`
    :   The type of the None singleton.

    `dimensions: list[str] | Any`
    :   The type of the None singleton.

    `end_date: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `row_limit: int | Any`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   The type of the None singleton.

    `start_row: int | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="SearchAnalyticsByDeviceSearchData"></a>

`SearchAnalyticsByDeviceSearchData(**data: Any)`
:   Search result data for search_analytics_by_device entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

    `position: float | None`
    :   The average position in search results by device type

    `search_type: str | None`
    :   The type of search performed

    `site_url: str | None`
    :   The URL of the site for which search analytics data is being provided

<a id="SearchAnalyticsByPageListResultMeta"></a>

`SearchAnalyticsByPageListResultMeta(**data: Any)`
:   Metadata for search_analytics_by_page.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `response_aggregation_type: str | Any | None`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageRequest"></a>

`SearchAnalyticsByPageRequest(**data: Any)`
:   Request body for search analytics query grouped by date and page.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `aggregation_type: str | Any`
    :   The type of the None singleton.

    `data_state: str | Any`
    :   The type of the None singleton.

    `dimensions: list[str] | Any`
    :   The type of the None singleton.

    `end_date: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `row_limit: int | Any`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   The type of the None singleton.

    `start_row: int | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="SearchAnalyticsByPageSearchData"></a>

`SearchAnalyticsByPageSearchData(**data: Any)`
:   Search result data for search_analytics_by_page entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clicks: int | None`
    :   The number of clicks for a specific page

    `ctr: float | None`
    :   Click-through rate for the page

    `date: str | None`
    :   The date for which the search analytics data is reported

    `impressions: int | None`
    :   The number of impressions for the page

    `model_config`
    :   The type of the None singleton.

    `page: str | None`
    :   The URL of the specific page being analyzed

    `position: float | None`
    :   The average position at which the page appeared in search results

    `search_type: str | None`
    :   The type of search query that led to the page being displayed

    `site_url: str | None`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByQueryListResultMeta"></a>

`SearchAnalyticsByQueryListResultMeta(**data: Any)`
:   Metadata for search_analytics_by_query.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `response_aggregation_type: str | Any | None`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQueryRequest"></a>

`SearchAnalyticsByQueryRequest(**data: Any)`
:   Request body for search analytics query grouped by date and query.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `aggregation_type: str | Any`
    :   The type of the None singleton.

    `data_state: str | Any`
    :   The type of the None singleton.

    `dimensions: list[str] | Any`
    :   The type of the None singleton.

    `end_date: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `row_limit: int | Any`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   The type of the None singleton.

    `start_row: int | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="SearchAnalyticsByQuerySearchData"></a>

`SearchAnalyticsByQuerySearchData(**data: Any)`
:   Search result data for search_analytics_by_query entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clicks: int | None`
    :   The number of clicks for the specific query

    `ctr: float | None`
    :   The click-through rate for the specific query

    `date: str | None`
    :   The date for which the search analytics data is recorded

    `impressions: int | None`
    :   The number of impressions for the specific query

    `model_config`
    :   The type of the None singleton.

    `position: float | None`
    :   The average position for the specific query

    `query: str | None`
    :   The search query for which the data is recorded

    `search_type: str | None`
    :   The type of search result for the specific query

    `site_url: str | None`
    :   The URL of the site for which the search analytics data is captured

<a id="SearchAnalyticsResponse"></a>

`SearchAnalyticsResponse(**data: Any)`
:   Response containing search analytics data.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `response_aggregation_type: str | Any | None`
    :   The type of the None singleton.

    `rows: list[airbyte_agent_sdk.connectors.google_search_console.models.SearchAnalyticsRow] | Any`
    :   The type of the None singleton.

<a id="SearchAnalyticsRow"></a>

`SearchAnalyticsRow(**data: Any)`
:   A row of search analytics data.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clicks: float | Any | None`
    :   The type of the None singleton.

    `ctr: float | Any | None`
    :   The type of the None singleton.

    `impressions: float | Any | None`
    :   The type of the None singleton.

    `keys: list[str] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `position: float | Any | None`
    :   The type of the None singleton.

<a id="Site"></a>

`Site(**data: Any)`
:   A Search Console site resource.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `permission_level: str | Any | None`
    :   The type of the None singleton.

    `site_url: str | Any | None`
    :   The type of the None singleton.

<a id="Sitemap"></a>

`Sitemap(**data: Any)`
:   A sitemap resource with details about a submitted sitemap.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `contents: list[airbyte_agent_sdk.connectors.google_search_console.models.SitemapContent] | Any | None`
    :   The type of the None singleton.

    `errors: str | Any | None`
    :   The type of the None singleton.

    `is_pending: bool | Any | None`
    :   The type of the None singleton.

    `is_sitemaps_index: bool | Any | None`
    :   The type of the None singleton.

    `last_downloaded: str | Any | None`
    :   The type of the None singleton.

    `last_submitted: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `path: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `warnings: str | Any | None`
    :   The type of the None singleton.

<a id="SitemapContent"></a>

`SitemapContent(**data: Any)`
:   Information about a specific content type in a sitemap.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `indexed: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `submitted: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="SitemapsList"></a>

`SitemapsList(**data: Any)`
:   Response containing a list of sitemaps.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `sitemap: list[airbyte_agent_sdk.connectors.google_search_console.models.Sitemap] | Any`
    :   The type of the None singleton.

<a id="SitemapsSearchData"></a>

`SitemapsSearchData(**data: Any)`
:   Search result data for sitemaps entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

    `path: str | None`
    :   Path to the sitemap file

    `type_: str | None`
    :   Type of the sitemap

    `warnings: str | None`
    :   Warnings encountered while processing the sitemaps

<a id="SitesList"></a>

`SitesList(**data: Any)`
:   Response containing a list of sites.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `site_entry: list[airbyte_agent_sdk.connectors.google_search_console.models.Site] | Any`
    :   The type of the None singleton.

<a id="SitesSearchData"></a>

`SitesSearchData(**data: Any)`
:   Search result data for sites entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `permission_level: str | None`
    :   The user's permission level for the site (owner, full, restricted, etc.)

    `site_url: str | None`
    :   The URL of the site data being fetched