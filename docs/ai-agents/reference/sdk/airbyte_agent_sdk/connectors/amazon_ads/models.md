---
id: airbyte_agent_sdk-connectors-amazon_ads-models
title: airbyte_agent_sdk.connectors.amazon_ads.models
---

Module airbyte_agent_sdk.connectors.amazon_ads.models
=====================================================
Pydantic models for amazon-ads connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="AccountInfo"></a>

`AccountInfo(**data: Any)`
:   Information about the advertiser's account associated with a profile
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `marketplace_string_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `sub_type: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `valid_payment_method: bool | Any | None`
    :   The type of the None singleton.

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

    * airbyte_agent_sdk.connectors.amazon_ads.models.AirbyteSearchResult[ProfilesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.amazon_ads.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[ProfilesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProfilesSearchResult"></a>

`ProfilesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AmazonAdsAuthConfig"></a>

`AmazonAdsAuthConfig(**data: Any)`
:   OAuth2 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str | None`
    :   The client ID of your Amazon Ads API application

    `client_secret: str | None`
    :   The client secret of your Amazon Ads API application

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   The refresh token obtained from the OAuth authorization flow

<a id="AmazonAdsCheckResult"></a>

`AmazonAdsCheckResult(**data: Any)`
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

<a id="AmazonAdsExecuteResult"></a>

`AmazonAdsExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult[list[Profile]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="AmazonAdsExecuteResultWithMeta"></a>

`AmazonAdsExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], PortfoliosListResultMeta]
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredBrandsAdGroupsListResultMeta]
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredBrandsCampaignsListResultMeta]
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductAdGroupsListResultMeta]
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductCampaignsListResultMeta]
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductKeywordsListResultMeta]
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductNegativeKeywordsListResultMeta]
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductNegativeTargetsListResultMeta]
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductProductAdsListResultMeta]
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductTargetsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`AmazonAdsExecuteResultWithMeta[dict[str, Any], PortfoliosListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PortfoliosListResult"></a>

`PortfoliosListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredBrandsAdGroupsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SponsoredBrandsAdGroupsListResult"></a>

`SponsoredBrandsAdGroupsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredBrandsCampaignsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SponsoredBrandsCampaignsListResult"></a>

`SponsoredBrandsCampaignsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductAdGroupsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SponsoredProductAdGroupsListResult"></a>

`SponsoredProductAdGroupsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductCampaignsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SponsoredProductCampaignsListResult"></a>

`SponsoredProductCampaignsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductKeywordsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SponsoredProductKeywordsListResult"></a>

`SponsoredProductKeywordsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductNegativeKeywordsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SponsoredProductNegativeKeywordsListResult"></a>

`SponsoredProductNegativeKeywordsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductNegativeTargetsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SponsoredProductNegativeTargetsListResult"></a>

`SponsoredProductNegativeTargetsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductProductAdsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SponsoredProductProductAdsListResult"></a>

`SponsoredProductProductAdsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductTargetsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SponsoredProductTargetsListResult"></a>

`SponsoredProductTargetsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonAdsExecuteResult[list[Profile]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProfilesListResult"></a>

`ProfilesListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CampaignBudget"></a>

`CampaignBudget(**data: Any)`
:   Budget configuration for a campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `budget: float | Any | None`
    :   The type of the None singleton.

    `budget_type: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DynamicBidding"></a>

`DynamicBidding(**data: Any)`
:   Dynamic bidding settings for a campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `placement_bidding: list[airbyte_agent_sdk.connectors.amazon_ads.models.DynamicBiddingPlacementbiddingItem] | Any | None`
    :   The type of the None singleton.

    `strategy: str | Any | None`
    :   The type of the None singleton.

<a id="DynamicBiddingPlacementbiddingItem"></a>

`DynamicBiddingPlacementbiddingItem(**data: Any)`
:   Nested schema for DynamicBidding.placementBidding_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `percentage: int | Any | None`
    :   The bid adjustment percentage

    `placement: str | Any | None`
    :   The placement type

<a id="Portfolio"></a>

`Portfolio(**data: Any)`
:   A portfolio is a container for grouping campaigns together for organizational
    and budget management purposes.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `budget: Any`
    :   The type of the None singleton.

    `creation_date: int | Any | None`
    :   The type of the None singleton.

    `in_budget: bool | Any | None`
    :   The type of the None singleton.

    `last_updated_date: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `portfolio_id: Any`
    :   The type of the None singleton.

    `serving_status: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

<a id="PortfolioBudget"></a>

`PortfolioBudget(**data: Any)`
:   Budget configuration for a portfolio
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: float | Any | None`
    :   The type of the None singleton.

    `currency_code: str | Any | None`
    :   The type of the None singleton.

    `end_date: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `policy: str | Any | None`
    :   The type of the None singleton.

    `start_date: str | Any | None`
    :   The type of the None singleton.

<a id="PortfoliosListResultMeta"></a>

`PortfoliosListResultMeta(**data: Any)`
:   Metadata for portfolios.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any | None`
    :   The type of the None singleton.

<a id="Profile"></a>

`Profile(**data: Any)`
:   An advertising profile represents an advertiser's account in a specific marketplace.
    Profiles are used to scope API calls and manage advertising campaigns.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_info: Any`
    :   The type of the None singleton.

    `country_code: str | Any | None`
    :   The type of the None singleton.

    `currency_code: str | Any | None`
    :   The type of the None singleton.

    `daily_budget: float | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `profile_id: int | Any`
    :   The type of the None singleton.

    `timezone: str | Any | None`
    :   The type of the None singleton.

<a id="ProfilesSearchData"></a>

`ProfilesSearchData(**data: Any)`
:   Search result data for profiles entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_info: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `country_code: str | None`
    :   The type of the None singleton.

    `currency_code: str | None`
    :   The type of the None singleton.

    `daily_budget: float | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `profile_id: int | None`
    :   The type of the None singleton.

    `timezone: str | None`
    :   The type of the None singleton.

<a id="SponsoredBrandsAdGroup"></a>

`SponsoredBrandsAdGroup(**data: Any)`
:   An ad group within a Sponsored Brands campaign. Ad groups organize ads and targeting
    within a campaign.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_group_id: Any`
    :   The type of the None singleton.

    `bid: float | Any | None`
    :   The type of the None singleton.

    `campaign_id: Any`
    :   The type of the None singleton.

    `extended_data: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

<a id="SponsoredBrandsAdGroupsListResultMeta"></a>

`SponsoredBrandsAdGroupsListResultMeta(**data: Any)`
:   Metadata for sponsored_brands_ad_groups.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any | None`
    :   The type of the None singleton.

<a id="SponsoredBrandsCampaign"></a>

`SponsoredBrandsCampaign(**data: Any)`
:   A Sponsored Brands campaign. Sponsored Brands campaigns help drive discovery and sales
    with creative ad experiences that appear in shopping results.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bid_multiplier: float | Any | None`
    :   The type of the None singleton.

    `bid_optimization: bool | Any | None`
    :   The type of the None singleton.

    `budget: float | Any | None`
    :   The type of the None singleton.

    `budget_type: str | Any | None`
    :   The type of the None singleton.

    `campaign_id: Any`
    :   The type of the None singleton.

    `cost_type: str | Any | None`
    :   The type of the None singleton.

    `end_date: str | Any | None`
    :   The type of the None singleton.

    `extended_data: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `portfolio_id: Any`
    :   The type of the None singleton.

    `product_location: str | Any | None`
    :   The type of the None singleton.

    `smart_default: str | Any | None`
    :   The type of the None singleton.

    `start_date: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

    `tags: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="SponsoredBrandsCampaignsListResultMeta"></a>

`SponsoredBrandsCampaignsListResultMeta(**data: Any)`
:   Metadata for sponsored_brands_campaigns.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any | None`
    :   The type of the None singleton.

<a id="SponsoredProductAdGroup"></a>

`SponsoredProductAdGroup(**data: Any)`
:   An ad group within a Sponsored Products campaign. Ad groups contain ads and targeting
    settings and have a default bid that applies to all ads in the group.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_group_id: Any`
    :   The type of the None singleton.

    `campaign_id: Any`
    :   The type of the None singleton.

    `default_bid: float | Any | None`
    :   The type of the None singleton.

    `extended_data: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

<a id="SponsoredProductAdGroupsListResultMeta"></a>

`SponsoredProductAdGroupsListResultMeta(**data: Any)`
:   Metadata for sponsored_product_ad_groups.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any | None`
    :   The type of the None singleton.

<a id="SponsoredProductCampaign"></a>

`SponsoredProductCampaign(**data: Any)`
:   A Sponsored Products campaign promotes individual product listings on Amazon.
    Campaigns contain ad groups, which contain ads and targeting settings.
    Note: The list endpoint (v3) and get endpoint (v2) return slightly different field formats.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bidding: Any`
    :   The type of the None singleton.

    `budget: Any`
    :   The type of the None singleton.

    `campaign_id: Any`
    :   The type of the None singleton.

    `campaign_type: str | Any | None`
    :   The type of the None singleton.

    `daily_budget: float | Any | None`
    :   The type of the None singleton.

    `dynamic_bidding: Any`
    :   The type of the None singleton.

    `end_date: str | Any | None`
    :   The type of the None singleton.

    `extended_data: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `marketplace_budget_allocation: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `off_amazon_settings: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `portfolio_id: Any`
    :   The type of the None singleton.

    `premium_bid_adjustment: bool | Any | None`
    :   The type of the None singleton.

    `start_date: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

    `tags: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `targeting_type: str | Any | None`
    :   The type of the None singleton.

<a id="SponsoredProductCampaignsListResultMeta"></a>

`SponsoredProductCampaignsListResultMeta(**data: Any)`
:   Metadata for sponsored_product_campaigns.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any | None`
    :   The type of the None singleton.

<a id="SponsoredProductKeyword"></a>

`SponsoredProductKeyword(**data: Any)`
:   A keyword within a Sponsored Products ad group. Keywords are used in manual targeting
    campaigns to match shopper search queries.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_group_id: Any`
    :   The type of the None singleton.

    `bid: float | Any | None`
    :   The type of the None singleton.

    `campaign_id: Any`
    :   The type of the None singleton.

    `extended_data: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `keyword_id: Any`
    :   The type of the None singleton.

    `keyword_text: str | Any | None`
    :   The type of the None singleton.

    `match_type: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

<a id="SponsoredProductKeywordsListResultMeta"></a>

`SponsoredProductKeywordsListResultMeta(**data: Any)`
:   Metadata for sponsored_product_keywords.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any | None`
    :   The type of the None singleton.

<a id="SponsoredProductNegativeKeyword"></a>

`SponsoredProductNegativeKeyword(**data: Any)`
:   A negative keyword within a Sponsored Products ad group. Negative keywords prevent
    ads from showing for specific search terms.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_group_id: Any`
    :   The type of the None singleton.

    `campaign_id: Any`
    :   The type of the None singleton.

    `extended_data: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `keyword_id: Any`
    :   The type of the None singleton.

    `keyword_text: str | Any | None`
    :   The type of the None singleton.

    `match_type: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

<a id="SponsoredProductNegativeKeywordsListResultMeta"></a>

`SponsoredProductNegativeKeywordsListResultMeta(**data: Any)`
:   Metadata for sponsored_product_negative_keywords.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any | None`
    :   The type of the None singleton.

<a id="SponsoredProductNegativeTarget"></a>

`SponsoredProductNegativeTarget(**data: Any)`
:   A negative targeting clause within a Sponsored Products ad group. Negative targeting
    clauses exclude specific products or categories from targeting.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_group_id: Any`
    :   The type of the None singleton.

    `campaign_id: Any`
    :   The type of the None singleton.

    `expression: list[airbyte_agent_sdk.connectors.amazon_ads.models.SponsoredProductNegativeTargetExpressionItem] | Any | None`
    :   The type of the None singleton.

    `expression_type: str | Any | None`
    :   The type of the None singleton.

    `extended_data: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `resolved_expression: list[airbyte_agent_sdk.connectors.amazon_ads.models.SponsoredProductNegativeTargetResolvedexpressionItem] | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

    `target_id: Any`
    :   The type of the None singleton.

<a id="SponsoredProductNegativeTargetExpressionItem"></a>

`SponsoredProductNegativeTargetExpressionItem(**data: Any)`
:   Nested schema for SponsoredProductNegativeTarget.expression_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The expression type

    `value: str | Any | None`
    :   The expression value

<a id="SponsoredProductNegativeTargetResolvedexpressionItem"></a>

`SponsoredProductNegativeTargetResolvedexpressionItem(**data: Any)`
:   Nested schema for SponsoredProductNegativeTarget.resolvedExpression_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The resolved expression type

    `value: str | Any | None`
    :   The resolved expression value

<a id="SponsoredProductNegativeTargetsListResultMeta"></a>

`SponsoredProductNegativeTargetsListResultMeta(**data: Any)`
:   Metadata for sponsored_product_negative_targets.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any | None`
    :   The type of the None singleton.

<a id="SponsoredProductProductAd"></a>

`SponsoredProductProductAd(**data: Any)`
:   A product ad within a Sponsored Products ad group. Product ads associate an
    advertised product (identified by ASIN or SKU) with an ad group.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_group_id: Any`
    :   The type of the None singleton.

    `ad_id: Any`
    :   The type of the None singleton.

    `asin: str | Any | None`
    :   The type of the None singleton.

    `campaign_id: Any`
    :   The type of the None singleton.

    `extended_data: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `sku: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

<a id="SponsoredProductProductAdsListResultMeta"></a>

`SponsoredProductProductAdsListResultMeta(**data: Any)`
:   Metadata for sponsored_product_product_ads.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any | None`
    :   The type of the None singleton.

<a id="SponsoredProductTarget"></a>

`SponsoredProductTarget(**data: Any)`
:   A targeting clause within a Sponsored Products ad group. Targeting clauses define
    product or category targeting for the ad group.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_group_id: Any`
    :   The type of the None singleton.

    `bid: float | Any | None`
    :   The type of the None singleton.

    `campaign_id: Any`
    :   The type of the None singleton.

    `expression: list[airbyte_agent_sdk.connectors.amazon_ads.models.SponsoredProductTargetExpressionItem] | Any | None`
    :   The type of the None singleton.

    `expression_type: str | Any | None`
    :   The type of the None singleton.

    `extended_data: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `resolved_expression: list[airbyte_agent_sdk.connectors.amazon_ads.models.SponsoredProductTargetResolvedexpressionItem] | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

    `target_id: Any`
    :   The type of the None singleton.

<a id="SponsoredProductTargetExpressionItem"></a>

`SponsoredProductTargetExpressionItem(**data: Any)`
:   Nested schema for SponsoredProductTarget.expression_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The expression type

    `value: str | Any | None`
    :   The expression value

<a id="SponsoredProductTargetResolvedexpressionItem"></a>

`SponsoredProductTargetResolvedexpressionItem(**data: Any)`
:   Nested schema for SponsoredProductTarget.resolvedExpression_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The resolved expression type

    `value: str | Any | None`
    :   The resolved expression value

<a id="SponsoredProductTargetsListResultMeta"></a>

`SponsoredProductTargetsListResultMeta(**data: Any)`
:   Metadata for sponsored_product_targets.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any | None`
    :   The type of the None singleton.