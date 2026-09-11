---
id: airbyte_agent_sdk-connectors-exa-types
title: airbyte_agent_sdk.connectors.exa.types
---

Module airbyte_agent_sdk.connectors.exa.types
=============================================
Type definitions for exa connector.

Classes
-------

<a id="ContentsListParams"></a>

`ContentsListParams(*args, **kwargs)`
:   Parameters for contents.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `highlights: Any`
    :   The type of the None singleton.

    `summary: airbyte_agent_sdk.connectors.exa.types.ContentsListParamsSummary`
    :   The type of the None singleton.

    `text: Any`
    :   The type of the None singleton.

    `urls: list[str]`
    :   The type of the None singleton.

<a id="ContentsListParamsSummary"></a>

`ContentsListParamsSummary(*args, **kwargs)`
:   Summary generation options.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `query: str`
    :   The type of the None singleton.

<a id="SearchResultsListParams"></a>

`SearchResultsListParams(*args, **kwargs)`
:   Parameters for search_results.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `category: str`
    :   The type of the None singleton.

    `contents: airbyte_agent_sdk.connectors.exa.types.SearchResultsListParamsContents`
    :   The type of the None singleton.

    `end_crawl_date: str`
    :   The type of the None singleton.

    `end_published_date: str`
    :   The type of the None singleton.

    `exclude_domains: list[str]`
    :   The type of the None singleton.

    `include_domains: list[str]`
    :   The type of the None singleton.

    `moderation: bool`
    :   The type of the None singleton.

    `num_results: int`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

    `start_crawl_date: str`
    :   The type of the None singleton.

    `start_published_date: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="SearchResultsListParamsContents"></a>

`SearchResultsListParamsContents(*args, **kwargs)`
:   Options for requesting page contents inline with search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `highlights: Any`
    :   The type of the None singleton.

    `summary: airbyte_agent_sdk.connectors.exa.types.SearchResultsListParamsContentsSummary`
    :   The type of the None singleton.

    `text: Any`
    :   The type of the None singleton.

<a id="SearchResultsListParamsContentsSummary"></a>

`SearchResultsListParamsContentsSummary(*args, **kwargs)`
:   Summary generation options.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `query: str`
    :   The type of the None singleton.

<a id="SimilarResultsListParams"></a>

`SimilarResultsListParams(*args, **kwargs)`
:   Parameters for similar_results.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contents: airbyte_agent_sdk.connectors.exa.types.SimilarResultsListParamsContents`
    :   The type of the None singleton.

    `end_crawl_date: str`
    :   The type of the None singleton.

    `end_published_date: str`
    :   The type of the None singleton.

    `exclude_domains: list[str]`
    :   The type of the None singleton.

    `include_domains: list[str]`
    :   The type of the None singleton.

    `num_results: int`
    :   The type of the None singleton.

    `start_crawl_date: str`
    :   The type of the None singleton.

    `start_published_date: str`
    :   The type of the None singleton.

    `url: str`
    :   The type of the None singleton.

<a id="SimilarResultsListParamsContents"></a>

`SimilarResultsListParamsContents(*args, **kwargs)`
:   Options for requesting page contents inline with similar page results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `highlights: Any`
    :   The type of the None singleton.

    `summary: airbyte_agent_sdk.connectors.exa.types.SimilarResultsListParamsContentsSummary`
    :   The type of the None singleton.

    `text: Any`
    :   The type of the None singleton.

<a id="SimilarResultsListParamsContentsSummary"></a>

`SimilarResultsListParamsContentsSummary(*args, **kwargs)`
:   Summary generation options.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `query: str`
    :   The type of the None singleton.