---
id: airbyte_agent_sdk-connectors-exa-models
title: airbyte_agent_sdk.connectors.exa.models
---

Module airbyte_agent_sdk.connectors.exa.models
==============================================
Pydantic models for exa connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="ContentResult"></a>

`ContentResult(**data: Any)`
:   ContentResult type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: str | None`
    :   The type of the None singleton.

    `favicon: str | None`
    :   The type of the None singleton.

    `highlight_scores: list[float] | None`
    :   The type of the None singleton.

    `highlights: list[str] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `image: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `published_date: str | None`
    :   The type of the None singleton.

    `score: float | None`
    :   The type of the None singleton.

    `summary: str | None`
    :   The type of the None singleton.

    `text: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="ContentsRequest"></a>

`ContentsRequest(**data: Any)`
:   ContentsRequest type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `highlights: typing.Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `summary: airbyte_agent_sdk.connectors.exa.models.ContentsRequestSummary | None`
    :   The type of the None singleton.

    `text: typing.Any | None`
    :   The type of the None singleton.

    `urls: list[str]`
    :   The type of the None singleton.

<a id="ContentsRequestSummary"></a>

`ContentsRequestSummary(**data: Any)`
:   Summary generation options.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `query: str | None`
    :   Custom query for the LLM-generated summary.

<a id="ContentsResponse"></a>

`ContentsResponse(**data: Any)`
:   ContentsResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cost_dollars: airbyte_agent_sdk.connectors.exa.models.CostDollars | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.exa.models.SearchResult] | None`
    :   The type of the None singleton.

    `search_time: float | None`
    :   The type of the None singleton.

    `statuses: list[airbyte_agent_sdk.connectors.exa.models.ContentsResponseStatusesItem] | None`
    :   The type of the None singleton.

<a id="ContentsResponseStatusesItem"></a>

`ContentsResponseStatusesItem(**data: Any)`
:   Nested schema for ContentsResponse.statuses_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The URL or document ID that was requested.

    `model_config`
    :   The type of the None singleton.

    `source: str | None`
    :   Where the content was sourced from.

    `status: str | None`
    :   Status of the content fetch.

<a id="CostDollars"></a>

`CostDollars(**data: Any)`
:   Estimated cost breakdown for the request.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `contents: airbyte_agent_sdk.connectors.exa.models.CostDollarsContents | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `search: airbyte_agent_sdk.connectors.exa.models.CostDollarsSearch | None`
    :   The type of the None singleton.

    `total: float | None`
    :   The type of the None singleton.

<a id="CostDollarsContents"></a>

`CostDollarsContents(**data: Any)`
:   Cost breakdown for contents retrieval.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `text: float | None`
    :   Cost for text extraction.

<a id="CostDollarsSearch"></a>

`CostDollarsSearch(**data: Any)`
:   Nested schema for CostDollars.search
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `neural: float | None`
    :   Cost for neural search.

<a id="ExaAuthConfig"></a>

`ExaAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Exa API key from dashboard.exa.ai/api-keys

    `model_config`
    :   The type of the None singleton.

<a id="ExaCheckResult"></a>

`ExaCheckResult(**data: Any)`
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

<a id="ExaExecuteResult"></a>

`ExaExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.exa.models.ExaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.exa.models.ExaExecuteResult[list[SearchResult]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="ExaExecuteResultWithMeta"></a>

`ExaExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.exa.models.ExaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `meta: ~S | None`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`ExaExecuteResult[list[SearchResult]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.exa.models.ExaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchResultsListResult"></a>

`SearchResultsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.exa.models.ExaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ContentsListResult"></a>

`ContentsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.exa.models.ExaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SimilarResultsListResult"></a>

`SimilarResultsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.exa.models.ExaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="FindSimilarRequest"></a>

`FindSimilarRequest(**data: Any)`
:   FindSimilarRequest type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `contents: airbyte_agent_sdk.connectors.exa.models.FindSimilarRequestContents | None`
    :   The type of the None singleton.

    `end_crawl_date: str | None`
    :   The type of the None singleton.

    `end_published_date: str | None`
    :   The type of the None singleton.

    `exclude_domains: list[str] | None`
    :   The type of the None singleton.

    `include_domains: list[str] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `num_results: int | None`
    :   The type of the None singleton.

    `start_crawl_date: str | None`
    :   The type of the None singleton.

    `start_published_date: str | None`
    :   The type of the None singleton.

    `url: str`
    :   The type of the None singleton.

<a id="FindSimilarRequestContents"></a>

`FindSimilarRequestContents(**data: Any)`
:   Options for requesting page contents inline with similar page results.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `highlights: typing.Any | None`
    :   Highlight extraction options. Pass true for defaults or an object for advanced options.

    `model_config`
    :   The type of the None singleton.

    `summary: airbyte_agent_sdk.connectors.exa.models.FindSimilarRequestContentsSummary | None`
    :   Summary generation options.

    `text: typing.Any | None`
    :   Text extraction options. Pass true for defaults or an object for advanced options.

<a id="FindSimilarRequestContentsSummary"></a>

`FindSimilarRequestContentsSummary(**data: Any)`
:   Summary generation options.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `query: str | None`
    :   Custom query for the LLM-generated summary.

<a id="FindSimilarResponse"></a>

`FindSimilarResponse(**data: Any)`
:   FindSimilarResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cost_dollars: airbyte_agent_sdk.connectors.exa.models.CostDollars | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.exa.models.SearchResult] | None`
    :   The type of the None singleton.

    `search_time: float | None`
    :   The type of the None singleton.

<a id="SearchRequest"></a>

`SearchRequest(**data: Any)`
:   SearchRequest type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category: str | None`
    :   The type of the None singleton.

    `contents: airbyte_agent_sdk.connectors.exa.models.SearchRequestContents | None`
    :   The type of the None singleton.

    `end_crawl_date: str | None`
    :   The type of the None singleton.

    `end_published_date: str | None`
    :   The type of the None singleton.

    `exclude_domains: list[str] | None`
    :   The type of the None singleton.

    `include_domains: list[str] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `moderation: bool | None`
    :   The type of the None singleton.

    `num_results: int | None`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

    `start_crawl_date: str | None`
    :   The type of the None singleton.

    `start_published_date: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="SearchRequestContents"></a>

`SearchRequestContents(**data: Any)`
:   Options for requesting page contents inline with search results.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `highlights: typing.Any | None`
    :   Highlight extraction options. Pass true for defaults or an object for advanced options.

    `model_config`
    :   The type of the None singleton.

    `summary: airbyte_agent_sdk.connectors.exa.models.SearchRequestContentsSummary | None`
    :   Summary generation options.

    `text: typing.Any | None`
    :   Text extraction options. Pass true for defaults or an object for advanced options.

<a id="SearchRequestContentsSummary"></a>

`SearchRequestContentsSummary(**data: Any)`
:   Summary generation options.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `query: str | None`
    :   Custom query for the LLM-generated summary.

<a id="SearchResponse"></a>

`SearchResponse(**data: Any)`
:   SearchResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cost_dollars: airbyte_agent_sdk.connectors.exa.models.CostDollars | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `resolved_search_type: str | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.exa.models.SearchResult] | None`
    :   The type of the None singleton.

    `search_time: float | None`
    :   The type of the None singleton.

<a id="SearchResult"></a>

`SearchResult(**data: Any)`
:   SearchResult type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: str | None`
    :   The type of the None singleton.

    `favicon: str | None`
    :   The type of the None singleton.

    `highlight_scores: list[float] | None`
    :   The type of the None singleton.

    `highlights: list[str] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `image: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `published_date: str | None`
    :   The type of the None singleton.

    `score: float | None`
    :   The type of the None singleton.

    `summary: str | None`
    :   The type of the None singleton.

    `text: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="SimilarResult"></a>

`SimilarResult(**data: Any)`
:   SimilarResult type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: str | None`
    :   The type of the None singleton.

    `favicon: str | None`
    :   The type of the None singleton.

    `highlight_scores: list[float] | None`
    :   The type of the None singleton.

    `highlights: list[str] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `image: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `published_date: str | None`
    :   The type of the None singleton.

    `score: float | None`
    :   The type of the None singleton.

    `summary: str | None`
    :   The type of the None singleton.

    `text: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.