---
id: airbyte_agent_sdk-connectors-chargebee-models
title: airbyte_agent_sdk.connectors.chargebee.models
---

Module airbyte_agent_sdk.connectors.chargebee.models
====================================================
Pydantic models for chargebee connector.

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

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[CouponSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[CreditNoteSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[CustomerSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[EventSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[InvoiceSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[ItemPriceSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[ItemSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[OrderSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[PaymentSourceSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[SubscriptionSearchData]
    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult[TransactionSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[CouponSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CouponSearchResult"></a>

`CouponSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CreditNoteSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CreditNoteSearchResult"></a>

`CreditNoteSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CustomerSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomerSearchResult"></a>

`CustomerSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[EventSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="EventSearchResult"></a>

`EventSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[InvoiceSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="InvoiceSearchResult"></a>

`InvoiceSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ItemPriceSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ItemPriceSearchResult"></a>

`ItemPriceSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ItemSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ItemSearchResult"></a>

`ItemSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[OrderSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrderSearchResult"></a>

`OrderSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[PaymentSourceSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PaymentSourceSearchResult"></a>

`PaymentSourceSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SubscriptionSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SubscriptionSearchResult"></a>

`SubscriptionSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TransactionSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TransactionSearchResult"></a>

`TransactionSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ChargebeeAuthConfig"></a>

`ChargebeeAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Chargebee API key (used as the HTTP Basic username)

    `model_config`
    :   The type of the None singleton.

<a id="ChargebeeCheckResult"></a>

`ChargebeeCheckResult(**data: Any)`
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

<a id="ChargebeeExecuteResult"></a>

`ChargebeeExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="ChargebeeExecuteResultWithMeta"></a>

`ChargebeeExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Coupon], CouponListResultMeta]
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[CreditNote], CreditNoteListResultMeta]
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Customer], CustomerListResultMeta]
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Event], EventListResultMeta]
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Invoice], InvoiceListResultMeta]
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[ItemPrice], ItemPriceListResultMeta]
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Item], ItemListResultMeta]
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Order], OrderListResultMeta]
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[PaymentSource], PaymentSourceListResultMeta]
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Subscription], SubscriptionListResultMeta]
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta[list[Transaction], TransactionListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`ChargebeeExecuteResultWithMeta[list[Coupon], CouponListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CouponListResult"></a>

`CouponListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ChargebeeExecuteResultWithMeta[list[CreditNote], CreditNoteListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CreditNoteListResult"></a>

`CreditNoteListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ChargebeeExecuteResultWithMeta[list[Customer], CustomerListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomerListResult"></a>

`CustomerListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ChargebeeExecuteResultWithMeta[list[Event], EventListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="EventListResult"></a>

`EventListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ChargebeeExecuteResultWithMeta[list[Invoice], InvoiceListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="InvoiceListResult"></a>

`InvoiceListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ChargebeeExecuteResultWithMeta[list[ItemPrice], ItemPriceListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ItemPriceListResult"></a>

`ItemPriceListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ChargebeeExecuteResultWithMeta[list[Item], ItemListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ItemListResult"></a>

`ItemListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ChargebeeExecuteResultWithMeta[list[Order], OrderListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrderListResult"></a>

`OrderListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ChargebeeExecuteResultWithMeta[list[PaymentSource], PaymentSourceListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PaymentSourceListResult"></a>

`PaymentSourceListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ChargebeeExecuteResultWithMeta[list[Subscription], SubscriptionListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SubscriptionListResult"></a>

`SubscriptionListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ChargebeeExecuteResultWithMeta[list[Transaction], TransactionListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TransactionListResult"></a>

`TransactionListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.chargebee.models.ChargebeeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ChargebeeReplicationConfig"></a>

`ChargebeeReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Chargebee.
    
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
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ. Data before this date is excluded.

<a id="Coupon"></a>

`Coupon(**data: Any)`
:   Chargebee coupon object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `addon_constraint: str | Any`
    :   The type of the None singleton.

    `apply_discount_on: str | Any`
    :   The type of the None singleton.

    `apply_on: str | Any`
    :   The type of the None singleton.

    `archived_at: int | Any`
    :   The type of the None singleton.

    `coupon_constraints: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `created_at: int | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `custom_fields: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `deleted: bool | Any`
    :   The type of the None singleton.

    `discount_amount: int | Any`
    :   The type of the None singleton.

    `discount_percentage: float | Any`
    :   The type of the None singleton.

    `discount_quantity: int | Any`
    :   The type of the None singleton.

    `discount_type: str | Any`
    :   The type of the None singleton.

    `duration_month: int | Any`
    :   The type of the None singleton.

    `duration_type: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `invoice_name: str | Any`
    :   The type of the None singleton.

    `invoice_notes: str | Any`
    :   The type of the None singleton.

    `item_constraint_criteria: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `item_constraints: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `max_redemptions: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `period: int | Any`
    :   The type of the None singleton.

    `period_unit: str | Any`
    :   The type of the None singleton.

    `plan_constraint: str | Any`
    :   The type of the None singleton.

    `redemptions: int | Any`
    :   The type of the None singleton.

    `resource_version: int | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `updated_at: int | Any`
    :   The type of the None singleton.

    `valid_till: int | Any`
    :   The type of the None singleton.

<a id="CouponList"></a>

`CouponList(**data: Any)`
:   Paginated list of coupons
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `list_: list[airbyte_agent_sdk.connectors.chargebee.models.CouponListListItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="CouponListListItem"></a>

`CouponListListItem(**data: Any)`
:   Nested schema for CouponList.list_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `coupon: airbyte_agent_sdk.connectors.chargebee.models.Coupon | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CouponListResultMeta"></a>

`CouponListResultMeta(**data: Any)`
:   Metadata for coupon.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="CouponSearchData"></a>

`CouponSearchData(**data: Any)`
:   Search result data for coupon entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `apply_discount_on: str | None`
    :   Determines where the discount is applied on (e.g. subtotal, total).

    `apply_on: str | None`
    :   Specify on what type of items the coupon applies (e.g. subscription, addon).

    `archived_at: int | None`
    :   Timestamp when the coupon was archived.

    `coupon_constraints: list[typing.Any] | None`
    :   Represents the constraints associated with the coupon

    `created_at: int | None`
    :   Timestamp of the coupon creation.

    `currency_code: str | None`
    :   The currency code for the coupon (e.g. USD, EUR).

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `discount_amount: int | None`
    :   The fixed discount amount applied by the coupon.

    `discount_percentage: float | None`
    :   Percentage discount applied by the coupon.

    `discount_quantity: int | None`
    :   Specifies the number of free units provided for the item price, without affecting the total quantity sold. This parameter is applicable only when the discount_type is set to offer_quantity.

    `discount_type: str | None`
    :   Type of discount (e.g. fixed, percentage).

    `duration_month: int | None`
    :   Duration of the coupon in months.

    `duration_type: str | None`
    :   Type of duration (e.g. forever, one-time).

    `id: str | None`
    :   Unique identifier for the coupon.

    `invoice_name: str | None`
    :   Name displayed on invoices when the coupon is used.

    `invoice_notes: str | None`
    :   Additional notes displayed on invoices when the coupon is used.

    `item_constraint_criteria: list[typing.Any] | None`
    :   Criteria for item constraints

    `item_constraints: list[typing.Any] | None`
    :   Constraints related to the items

    `max_redemptions: int | None`
    :   Maximum number of times the coupon can be redeemed.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the coupon.

    `object_: str | None`
    :   Type of object (usually 'coupon').

    `period: int | None`
    :   Duration or frequency for which the coupon is valid.

    `period_unit: str | None`
    :   Unit of the period (e.g. days, weeks).

    `redemptions: int | None`
    :   Number of times the coupon has been redeemed.

    `resource_version: int | None`
    :   Version of the resource.

    `status: str | None`
    :   Current status of the coupon (e.g. active, inactive).

    `updated_at: int | None`
    :   Timestamp when the coupon was last updated.

    `valid_till: int | None`
    :   Date until which the coupon is valid for use.

<a id="CouponWrapper"></a>

`CouponWrapper(**data: Any)`
:   CouponWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `coupon: airbyte_agent_sdk.connectors.chargebee.models.Coupon | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CreditNote"></a>

`CreditNote(**data: Any)`
:   Chargebee credit note object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allocations: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `amount_allocated: int | Any`
    :   The type of the None singleton.

    `amount_available: int | Any`
    :   The type of the None singleton.

    `amount_refunded: int | Any`
    :   The type of the None singleton.

    `base_currency_code: str | Any`
    :   The type of the None singleton.

    `billing_address: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `business_entity_id: str | Any`
    :   The type of the None singleton.

    `channel: str | Any`
    :   The type of the None singleton.

    `create_reason_code: str | Any`
    :   The type of the None singleton.

    `created_at: int | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `custom_fields: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `customer_id: str | Any`
    :   The type of the None singleton.

    `date: int | Any`
    :   The type of the None singleton.

    `deleted: bool | Any`
    :   The type of the None singleton.

    `discounts: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `exchange_rate: float | Any`
    :   The type of the None singleton.

    `fractional_correction: int | Any`
    :   The type of the None singleton.

    `generated_at: int | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `line_item_discounts: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `line_item_taxes: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `line_item_tiers: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `line_items: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `linked_refunds: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `linked_tax_withheld_refunds: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `price_type: str | Any`
    :   The type of the None singleton.

    `reason_code: str | Any`
    :   The type of the None singleton.

    `reference_invoice_id: str | Any`
    :   The type of the None singleton.

    `refunded_at: int | Any`
    :   The type of the None singleton.

    `resource_version: int | Any`
    :   The type of the None singleton.

    `round_off_amount: int | Any`
    :   The type of the None singleton.

    `shipping_address: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `sub_total: int | Any`
    :   The type of the None singleton.

    `sub_total_in_local_currency: int | Any`
    :   The type of the None singleton.

    `subscription_id: str | Any`
    :   The type of the None singleton.

    `taxes: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

    `total_in_local_currency: int | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `updated_at: int | Any`
    :   The type of the None singleton.

    `void_reason_code: str | Any`
    :   The type of the None singleton.

    `voided_at: int | Any`
    :   The type of the None singleton.

<a id="CreditNoteList"></a>

`CreditNoteList(**data: Any)`
:   Paginated list of credit notes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `list_: list[airbyte_agent_sdk.connectors.chargebee.models.CreditNoteListListItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="CreditNoteListListItem"></a>

`CreditNoteListListItem(**data: Any)`
:   Nested schema for CreditNoteList.list_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `credit_note: airbyte_agent_sdk.connectors.chargebee.models.CreditNote | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CreditNoteListResultMeta"></a>

`CreditNoteListResultMeta(**data: Any)`
:   Metadata for credit_note.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="CreditNoteSearchData"></a>

`CreditNoteSearchData(**data: Any)`
:   Search result data for credit_note entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allocations: list[typing.Any] | None`
    :   Details of allocations associated with the credit note

    `amount_allocated: int | None`
    :   The amount of credits allocated.

    `amount_available: int | None`
    :   The amount of credits available.

    `amount_refunded: int | None`
    :   The amount of credits refunded.

    `base_currency_code: str | None`
    :   The base currency code for the credit note.

    `billing_address: dict[str, typing.Any] | None`
    :   Details of the billing address associated with the credit note

    `business_entity_id: str | None`
    :   The ID of the business entity associated with the credit note.

    `channel: str | None`
    :   The channel through which the credit note was created.

    `create_reason_code: str | None`
    :   The reason code for creating the credit note.

    `currency_code: str | None`
    :   The currency code for the credit note.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `customer_id: str | None`
    :   The ID of the customer associated with the credit note.

    `customer_notes: str | None`
    :   Notes provided by the customer for the credit note.

    `date: int | None`
    :   The date when the credit note was created.

    `deleted: bool | None`
    :   Indicates if the credit note has been deleted.

    `discounts: list[typing.Any] | None`
    :   Details of discounts applied to the credit note

    `exchange_rate: float | None`
    :   The exchange rate used for currency conversion.

    `fractional_correction: int | None`
    :   Fractional correction for rounding off decimals.

    `generated_at: int | None`
    :   The date when the credit note was generated.

    `id: str | None`
    :   The unique identifier for the credit note.

    `is_digital: bool | None`
    :   Indicates if the credit note is in digital format.

    `is_vat_moss_registered: bool | None`
    :   Indicates if VAT MOSS registration applies.

    `line_item_discounts: list[typing.Any] | None`
    :   Details of discounts applied at the line item level in the credit note

    `line_item_taxes: list[typing.Any] | None`
    :   Details of taxes applied at the line item level in the credit note

    `line_item_tiers: list[typing.Any] | None`
    :   Details of tiers applied to line items in the credit note

    `line_items: list[typing.Any] | None`
    :   Details of line items in the credit note

    `linked_refunds: list[typing.Any] | None`
    :   Details of linked refunds to the credit note

    `linked_tax_withheld_refunds: list[typing.Any] | None`
    :   Details of linked tax withheld refunds to the credit note

    `local_currency_code: str | None`
    :   The local currency code for the credit note.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   The object type of the credit note.

    `price_type: str | None`
    :   The type of pricing used for the credit note.

    `reason_code: str | None`
    :   The reason code for creating the credit note.

    `reference_invoice_id: str | None`
    :   The ID of the invoice this credit note references.

    `refunded_at: int | None`
    :   The date when the credit note was refunded.

    `resource_version: int | None`
    :   The version of the credit note resource.

    `round_off_amount: int | None`
    :   Amount rounded off for currency conversions.

    `shipping_address: dict[str, typing.Any] | None`
    :   Details of the shipping address associated with the credit note

    `status: str | None`
    :   The status of the credit note.

    `sub_total: int | None`
    :   The subtotal amount of the credit note.

    `sub_total_in_local_currency: int | None`
    :   The subtotal amount in local currency.

    `subscription_id: str | None`
    :   The ID of the subscription associated with the credit note.

    `taxes: list[typing.Any] | None`
    :   List of taxes applied to the credit note

    `total: int | None`
    :   The total amount of the credit note.

    `total_in_local_currency: int | None`
    :   The total amount in local currency.

    `type_: str | None`
    :   The type of credit note.

    `updated_at: int | None`
    :   The date when the credit note was last updated.

    `vat_number: str | None`
    :   VAT number associated with the credit note.

    `vat_number_prefix: str | None`
    :   Prefix for the VAT number.

    `voided_at: int | None`
    :   The date when the credit note was voided.

<a id="CreditNoteWrapper"></a>

`CreditNoteWrapper(**data: Any)`
:   CreditNoteWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `credit_note: airbyte_agent_sdk.connectors.chargebee.models.CreditNote | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Customer"></a>

`Customer(**data: Any)`
:   Chargebee customer object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allow_direct_debit: bool | Any`
    :   The type of the None singleton.

    `auto_close_invoices: bool | Any`
    :   The type of the None singleton.

    `auto_collection: str | Any`
    :   The type of the None singleton.

    `backup_payment_source_id: str | Any`
    :   The type of the None singleton.

    `balances: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `billing_address: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `billing_date: int | Any`
    :   The type of the None singleton.

    `billing_date_mode: str | Any`
    :   The type of the None singleton.

    `billing_day_of_week: str | Any`
    :   The type of the None singleton.

    `billing_day_of_week_mode: str | Any`
    :   The type of the None singleton.

    `billing_month: int | Any`
    :   The type of the None singleton.

    `business_customer_without_vat_number: bool | Any`
    :   The type of the None singleton.

    `business_entity_id: str | Any`
    :   The type of the None singleton.

    `card_status: str | Any`
    :   The type of the None singleton.

    `channel: str | Any`
    :   The type of the None singleton.

    `child_account_access: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `client_profile_id: str | Any`
    :   The type of the None singleton.

    `company: str | Any`
    :   The type of the None singleton.

    `consolidated_invoicing: bool | Any`
    :   The type of the None singleton.

    `contacts: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `created_at: int | Any`
    :   The type of the None singleton.

    `created_from_ip: str | Any`
    :   The type of the None singleton.

    `custom_fields: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `customer_type: str | Any`
    :   The type of the None singleton.

    `deleted: bool | Any`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `entity_code: str | Any`
    :   The type of the None singleton.

    `excess_payments: int | Any`
    :   The type of the None singleton.

    `exempt_number: str | Any`
    :   The type of the None singleton.

    `exemption_details: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `first_name: str | Any`
    :   The type of the None singleton.

    `fraud_flag: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `invoice_notes: str | Any`
    :   The type of the None singleton.

    `is_location_valid: bool | Any`
    :   The type of the None singleton.

    `last_name: str | Any`
    :   The type of the None singleton.

    `locale: str | Any`
    :   The type of the None singleton.

    `meta_data: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `mrr: int | Any`
    :   The type of the None singleton.

    `net_term_days: int | Any`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `offline_payment_method: str | Any`
    :   The type of the None singleton.

    `parent_account_access: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `payment_method: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `phone: str | Any`
    :   The type of the None singleton.

    `pii_cleared: str | Any`
    :   The type of the None singleton.

    `preferred_currency_code: str | Any`
    :   The type of the None singleton.

    `primary_payment_source_id: str | Any`
    :   The type of the None singleton.

    `promotional_credits: int | Any`
    :   The type of the None singleton.

    `referral_urls: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `refundable_credits: int | Any`
    :   The type of the None singleton.

    `registered_for_gst: bool | Any`
    :   The type of the None singleton.

    `relationship: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `resource_version: int | Any`
    :   The type of the None singleton.

    `tax_providers_fields: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `taxability: str | Any`
    :   The type of the None singleton.

    `unbilled_charges: int | Any`
    :   The type of the None singleton.

    `updated_at: int | Any`
    :   The type of the None singleton.

    `use_default_hierarchy_settings: bool | Any`
    :   The type of the None singleton.

    `vat_number: str | Any`
    :   The type of the None singleton.

    `vat_number_prefix: str | Any`
    :   The type of the None singleton.

    `vat_number_status: str | Any`
    :   The type of the None singleton.

    `vat_number_validated_time: int | Any`
    :   The type of the None singleton.

<a id="CustomerList"></a>

`CustomerList(**data: Any)`
:   Paginated list of customers
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `list_: list[airbyte_agent_sdk.connectors.chargebee.models.CustomerListListItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="CustomerListListItem"></a>

`CustomerListListItem(**data: Any)`
:   Nested schema for CustomerList.list_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `customer: airbyte_agent_sdk.connectors.chargebee.models.Customer | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomerListResultMeta"></a>

`CustomerListResultMeta(**data: Any)`
:   Metadata for customer.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="CustomerSearchData"></a>

`CustomerSearchData(**data: Any)`
:   Search result data for customer entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allow_direct_debit: bool | None`
    :   Indicates if direct debit is allowed for the customer.

    `auto_close_invoices: bool | None`
    :   Flag to automatically close invoices for the customer.

    `auto_collection: str | None`
    :   Configures the automatic collection settings for the customer.

    `backup_payment_source_id: str | None`
    :   ID of the backup payment source for the customer.

    `balances: list[typing.Any] | None`
    :   Customer's balance information related to their account.

    `billing_address: dict[str, typing.Any] | None`
    :   Customer's billing address details.

    `billing_date: int | None`
    :   Date for billing cycle.

    `billing_date_mode: str | None`
    :   Mode for billing date calculation.

    `billing_day_of_week: str | None`
    :   Day of the week for billing cycle.

    `billing_day_of_week_mode: str | None`
    :   Mode for billing day of the week calculation.

    `billing_month: int | None`
    :   Month for billing cycle.

    `business_customer_without_vat_number: bool | None`
    :   Flag indicating business customer without a VAT number.

    `business_entity_id: str | None`
    :   ID of the business entity.

    `card_status: str | None`
    :   Status of payment card associated with the customer.

    `channel: str | None`
    :   Channel through which the customer was acquired.

    `child_account_access: dict[str, typing.Any] | None`
    :   Information regarding the access rights of child accounts linked to the customer's account.

    `client_profile_id: str | None`
    :   Client profile ID of the customer.

    `company: str | None`
    :   Company or organization name.

    `consolidated_invoicing: bool | None`
    :   Flag for consolidated invoicing setting.

    `contacts: list[typing.Any] | None`
    :   List of contact details associated with the customer.

    `created_at: int | None`
    :   Date and time when the customer was created.

    `created_from_ip: str | None`
    :   IP address from which the customer was created.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `customer_type: str | None`
    :   Type of customer (e.g., individual, business).

    `deleted: bool | None`
    :   Flag indicating if the customer is deleted.

    `email: str | None`
    :   Email address of the customer.

    `entity_code: str | None`
    :   Code for the customer entity.

    `excess_payments: int | None`
    :   Total amount of excess payments by the customer.

    `exempt_number: str | None`
    :   Exemption number for tax purposes.

    `exemption_details: list[typing.Any] | None`
    :   Details about any exemptions applicable to the customer's account.

    `first_name: str | None`
    :   First name of the customer.

    `fraud_flag: str | None`
    :   Flag indicating if fraud is associated with the customer.

    `id: str | None`
    :   Unique ID of the customer.

    `invoice_notes: str | None`
    :   Notes added to the customer's invoices.

    `is_location_valid: bool | None`
    :   Flag indicating if the customer location is valid.

    `last_name: str | None`
    :   Last name of the customer.

    `locale: str | None`
    :   Locale setting for the customer.

    `meta_data: dict[str, typing.Any] | None`
    :   Additional metadata associated with the customer.

    `model_config`
    :   The type of the None singleton.

    `mrr: int | None`
    :   Monthly recurring revenue generated from the customer.

    `net_term_days: int | None`
    :   Number of days for net terms.

    `object_: str | None`
    :   Object type for the customer.

    `offline_payment_method: str | None`
    :   Offline payment method used by the customer.

    `parent_account_access: dict[str, typing.Any] | None`
    :   Information regarding the access rights of the parent account, if applicable.

    `payment_method: dict[str, typing.Any] | None`
    :   Customer's preferred payment method details.

    `phone: str | None`
    :   Phone number of the customer.

    `pii_cleared: str | None`
    :   Flag indicating if PII (Personally Identifiable Information) is cleared.

    `preferred_currency_code: str | None`
    :   Preferred currency code for transactions.

    `primary_payment_source_id: str | None`
    :   ID of the primary payment source for the customer.

    `promotional_credits: int | None`
    :   Total amount of promotional credits used.

    `referral_urls: list[typing.Any] | None`
    :   List of referral URLs associated with the customer.

    `refundable_credits: int | None`
    :   Total amount of refundable credits.

    `registered_for_gst: bool | None`
    :   Flag indicating if the customer is registered for GST.

    `relationship: dict[str, typing.Any] | None`
    :   Details about the relationship of the customer to other entities, if any.

    `resource_version: int | None`
    :   Version of the customer's resource.

    `tax_providers_fields: list[typing.Any] | None`
    :   Fields related to tax providers.

    `taxability: str | None`
    :   Taxability status of the customer.

    `unbilled_charges: int | None`
    :   Total amount of unbilled charges.

    `updated_at: int | None`
    :   Date and time when the customer record was last updated.

    `use_default_hierarchy_settings: bool | None`
    :   Flag indicating if default hierarchy settings are used.

    `vat_number: str | None`
    :   VAT number associated with the customer.

    `vat_number_prefix: str | None`
    :   Prefix for the VAT number.

    `vat_number_status: str | None`
    :   Status of the VAT number validation.

    `vat_number_validated_time: int | None`
    :   Date and time when the VAT number was validated.

<a id="CustomerWrapper"></a>

`CustomerWrapper(**data: Any)`
:   CustomerWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `customer: airbyte_agent_sdk.connectors.chargebee.models.Customer | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Event"></a>

`Event(**data: Any)`
:   Chargebee event object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_version: str | Any`
    :   The type of the None singleton.

    `content: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `custom_fields: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `event_type: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `occurred_at: int | Any`
    :   The type of the None singleton.

    `source: str | Any`
    :   The type of the None singleton.

    `user: str | Any`
    :   The type of the None singleton.

    `webhook_status: str | Any`
    :   The type of the None singleton.

    `webhooks: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

<a id="EventList"></a>

`EventList(**data: Any)`
:   Paginated list of events
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `list_: list[airbyte_agent_sdk.connectors.chargebee.models.EventListListItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="EventListListItem"></a>

`EventListListItem(**data: Any)`
:   Nested schema for EventList.list_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `event: airbyte_agent_sdk.connectors.chargebee.models.Event | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="EventListResultMeta"></a>

`EventListResultMeta(**data: Any)`
:   Metadata for event.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="EventSearchData"></a>

`EventSearchData(**data: Any)`
:   Search result data for event entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_version: str | None`
    :   The version of the Chargebee API being used to fetch the event data.

    `content: dict[str, typing.Any] | None`
    :   The specific content or information associated with the event.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `event_type: str | None`
    :   The type or category of the event.

    `id: str | None`
    :   Unique identifier for the event data record.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   The object or entity that the event is triggered for.

    `occurred_at: int | None`
    :   The datetime when the event occurred.

    `source: str | None`
    :   The source or origin of the event data.

    `user: str | None`
    :   Information about the user or entity associated with the event.

    `webhook_status: str | None`
    :   The status of the webhook execution for the event.

    `webhooks: list[typing.Any] | None`
    :   List of webhooks associated with the event.

<a id="EventWrapper"></a>

`EventWrapper(**data: Any)`
:   EventWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `event: airbyte_agent_sdk.connectors.chargebee.models.Event | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Invoice"></a>

`Invoice(**data: Any)`
:   Chargebee invoice object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `adjustment_credit_notes: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `amount_adjusted: int | Any`
    :   The type of the None singleton.

    `amount_due: int | Any`
    :   The type of the None singleton.

    `amount_paid: int | Any`
    :   The type of the None singleton.

    `amount_to_collect: int | Any`
    :   The type of the None singleton.

    `applied_credits: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `base_currency_code: str | Any`
    :   The type of the None singleton.

    `billing_address: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `business_entity_id: str | Any`
    :   The type of the None singleton.

    `channel: str | Any`
    :   The type of the None singleton.

    `created_at: int | Any`
    :   The type of the None singleton.

    `credits_applied: int | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `custom_fields: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `customer_id: str | Any`
    :   The type of the None singleton.

    `date: int | Any`
    :   The type of the None singleton.

    `deleted: bool | Any`
    :   The type of the None singleton.

    `discounts: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `due_date: int | Any`
    :   The type of the None singleton.

    `dunning_attempts: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `dunning_status: str | Any`
    :   The type of the None singleton.

    `exchange_rate: float | Any`
    :   The type of the None singleton.

    `expected_payment_date: int | Any`
    :   The type of the None singleton.

    `first_invoice: bool | Any`
    :   The type of the None singleton.

    `generated_at: int | Any`
    :   The type of the None singleton.

    `has_advance_charges: bool | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_gifted: bool | Any`
    :   The type of the None singleton.

    `issued_credit_notes: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `line_item_discounts: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `line_item_taxes: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `line_item_tiers: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `line_items: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `linked_orders: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `linked_payments: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `linked_taxes_withheld: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `net_term_days: int | Any`
    :   The type of the None singleton.

    `new_sales_amount: int | Any`
    :   The type of the None singleton.

    `notes: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `paid_at: int | Any`
    :   The type of the None singleton.

    `price_type: str | Any`
    :   The type of the None singleton.

    `recurring: bool | Any`
    :   The type of the None singleton.

    `resource_version: int | Any`
    :   The type of the None singleton.

    `round_off_amount: int | Any`
    :   The type of the None singleton.

    `shipping_address: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `sub_total: int | Any`
    :   The type of the None singleton.

    `sub_total_in_local_currency: int | Any`
    :   The type of the None singleton.

    `subscription_id: str | Any`
    :   The type of the None singleton.

    `tax: int | Any`
    :   The type of the None singleton.

    `taxes: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

    `total_in_local_currency: int | Any`
    :   The type of the None singleton.

    `updated_at: int | Any`
    :   The type of the None singleton.

    `void_reason_code: str | Any`
    :   The type of the None singleton.

    `voided_at: int | Any`
    :   The type of the None singleton.

    `write_off_amount: int | Any`
    :   The type of the None singleton.

<a id="InvoiceList"></a>

`InvoiceList(**data: Any)`
:   Paginated list of invoices
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `list_: list[airbyte_agent_sdk.connectors.chargebee.models.InvoiceListListItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="InvoiceListListItem"></a>

`InvoiceListListItem(**data: Any)`
:   Nested schema for InvoiceList.list_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `invoice: airbyte_agent_sdk.connectors.chargebee.models.Invoice | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InvoiceListResultMeta"></a>

`InvoiceListResultMeta(**data: Any)`
:   Metadata for invoice.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="InvoiceSearchData"></a>

`InvoiceSearchData(**data: Any)`
:   Search result data for invoice entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `adjustment_credit_notes: list[typing.Any] | None`
    :   Details of adjustment credit notes applied to the invoice

    `amount_adjusted: int | None`
    :   Total amount adjusted in the invoice

    `amount_due: int | None`
    :   Amount due for payment

    `amount_paid: int | None`
    :   Amount already paid

    `amount_to_collect: int | None`
    :   Amount yet to be collected

    `applied_credits: list[typing.Any] | None`
    :   Details of credits applied to the invoice

    `base_currency_code: str | None`
    :   Currency code used as base for the invoice

    `billing_address: dict[str, typing.Any] | None`
    :   Details of the billing address associated with the invoice

    `business_entity_id: str | None`
    :   ID of the business entity

    `channel: str | None`
    :   Channel through which the invoice was generated

    `credits_applied: int | None`
    :   Total credits applied to the invoice

    `currency_code: str | None`
    :   Currency code of the invoice

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `customer_id: str | None`
    :   ID of the customer

    `date: int | None`
    :   Date of the invoice

    `deleted: bool | None`
    :   Flag indicating if the invoice is deleted

    `discounts: list[typing.Any] | None`
    :   Discount details applied to the invoice

    `due_date: int | None`
    :   Due date for payment

    `dunning_attempts: list[typing.Any] | None`
    :   Details of dunning attempts made

    `dunning_status: str | None`
    :   Status of dunning for the invoice

    `einvoice: dict[str, typing.Any] | None`
    :   Details of electronic invoice

    `exchange_rate: float | None`
    :   Exchange rate used for currency conversion

    `expected_payment_date: int | None`
    :   Expected date of payment

    `first_invoice: bool | None`
    :   Flag indicating whether it's the first invoice

    `generated_at: int | None`
    :   Date when the invoice was generated

    `has_advance_charges: bool | None`
    :   Flag indicating if there are advance charges

    `id: str | None`
    :   Unique ID of the invoice

    `is_digital: bool | None`
    :   Flag indicating if the invoice is digital

    `is_gifted: bool | None`
    :   Flag indicating if the invoice is gifted

    `issued_credit_notes: list[typing.Any] | None`
    :   Details of credit notes issued

    `line_item_discounts: list[typing.Any] | None`
    :   Details of line item discounts

    `line_item_taxes: list[typing.Any] | None`
    :   Tax details applied to each line item in the invoice

    `line_item_tiers: list[typing.Any] | None`
    :   Tiers information for each line item in the invoice

    `line_items: list[typing.Any] | None`
    :   Details of individual line items in the invoice

    `linked_orders: list[typing.Any] | None`
    :   Details of linked orders to the invoice

    `linked_payments: list[typing.Any] | None`
    :   Details of linked payments

    `linked_taxes_withheld: list[typing.Any] | None`
    :   Details of linked taxes withheld on the invoice

    `local_currency_code: str | None`
    :   Local currency code of the invoice

    `local_currency_exchange_rate: float | None`
    :   Exchange rate for local currency conversion

    `model_config`
    :   The type of the None singleton.

    `net_term_days: int | None`
    :   Net term days for payment

    `new_sales_amount: int | None`
    :   New sales amount in the invoice

    `next_retry_at: int | None`
    :   Date of the next payment retry

    `notes: list[typing.Any] | None`
    :   Notes associated with the invoice

    `object_: str | None`
    :   Type of object

    `paid_at: int | None`
    :   Date when the invoice was paid

    `payment_owner: str | None`
    :   Owner of the payment

    `po_number: str | None`
    :   Purchase order number

    `price_type: str | None`
    :   Type of pricing

    `recurring: bool | None`
    :   Flag indicating if it's a recurring invoice

    `resource_version: int | None`
    :   Resource version of the invoice

    `round_off_amount: int | None`
    :   Amount rounded off

    `shipping_address: dict[str, typing.Any] | None`
    :   Details of the shipping address associated with the invoice

    `statement_descriptor: dict[str, typing.Any] | None`
    :   Descriptor for the statement

    `status: str | None`
    :   Status of the invoice

    `sub_total: int | None`
    :   Subtotal amount

    `sub_total_in_local_currency: int | None`
    :   Subtotal amount in local currency

    `subscription_id: str | None`
    :   ID of the subscription associated

    `tax: int | None`
    :   Total tax amount

    `tax_category: str | None`
    :   Tax category

    `taxes: list[typing.Any] | None`
    :   Details of taxes applied

    `term_finalized: bool | None`
    :   Flag indicating if the term is finalized

    `total: int | None`
    :   Total amount of the invoice

    `total_in_local_currency: int | None`
    :   Total amount in local currency

    `updated_at: int | None`
    :   Date of last update

    `vat_number: str | None`
    :   VAT number

    `vat_number_prefix: str | None`
    :   Prefix for the VAT number

    `void_reason_code: str | None`
    :   Reason code for voiding the invoice

    `voided_at: int | None`
    :   Date when the invoice was voided

    `write_off_amount: int | None`
    :   Amount written off

<a id="InvoiceWrapper"></a>

`InvoiceWrapper(**data: Any)`
:   InvoiceWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `invoice: airbyte_agent_sdk.connectors.chargebee.models.Invoice | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Item"></a>

`Item(**data: Any)`
:   Chargebee item object (Product Catalog 2.0)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `applicable_items: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `archived_at: int | Any`
    :   The type of the None singleton.

    `bundle_configuration: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `bundle_items: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `business_entity_id: str | Any`
    :   The type of the None singleton.

    `channel: str | Any`
    :   The type of the None singleton.

    `deleted: bool | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `enabled_for_checkout: bool | Any`
    :   The type of the None singleton.

    `enabled_in_portal: bool | Any`
    :   The type of the None singleton.

    `external_name: str | Any`
    :   The type of the None singleton.

    `gift_claim_redirect_url: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `included_in_mrr: bool | Any`
    :   The type of the None singleton.

    `is_giftable: bool | Any`
    :   The type of the None singleton.

    `is_percentage_pricing: bool | Any`
    :   The type of the None singleton.

    `is_shippable: bool | Any`
    :   The type of the None singleton.

    `item_applicability: str | Any`
    :   The type of the None singleton.

    `item_family_id: str | Any`
    :   The type of the None singleton.

    `metadata: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `metered: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `redirect_url: str | Any`
    :   The type of the None singleton.

    `resource_version: int | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `unit: str | Any`
    :   The type of the None singleton.

    `updated_at: int | Any`
    :   The type of the None singleton.

    `usage_calculation: str | Any`
    :   The type of the None singleton.

<a id="ItemList"></a>

`ItemList(**data: Any)`
:   Paginated list of items
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `list_: list[airbyte_agent_sdk.connectors.chargebee.models.ItemListListItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="ItemListListItem"></a>

`ItemListListItem(**data: Any)`
:   Nested schema for ItemList.list_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `item: airbyte_agent_sdk.connectors.chargebee.models.Item | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ItemListResultMeta"></a>

`ItemListResultMeta(**data: Any)`
:   Metadata for item.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="ItemPrice"></a>

`ItemPrice(**data: Any)`
:   Chargebee item price object (Product Catalog 2.0)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accounting_detail: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `archived_at: int | Any`
    :   The type of the None singleton.

    `billing_cycles: int | Any`
    :   The type of the None singleton.

    `business_entity_id: str | Any`
    :   The type of the None singleton.

    `channel: str | Any`
    :   The type of the None singleton.

    `created_at: int | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `deleted: bool | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `external_name: str | Any`
    :   The type of the None singleton.

    `free_quantity: int | Any`
    :   The type of the None singleton.

    `free_quantity_in_decimal: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `invoice_notes: str | Any`
    :   The type of the None singleton.

    `is_taxable: bool | Any`
    :   The type of the None singleton.

    `item_family_id: str | Any`
    :   The type of the None singleton.

    `item_id: str | Any`
    :   The type of the None singleton.

    `item_type: str | Any`
    :   The type of the None singleton.

    `metadata: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `period: int | Any`
    :   The type of the None singleton.

    `period_unit: str | Any`
    :   The type of the None singleton.

    `price: int | Any`
    :   The type of the None singleton.

    `price_in_decimal: str | Any`
    :   The type of the None singleton.

    `pricing_model: str | Any`
    :   The type of the None singleton.

    `resource_version: int | Any`
    :   The type of the None singleton.

    `shipping_period: int | Any`
    :   The type of the None singleton.

    `shipping_period_unit: str | Any`
    :   The type of the None singleton.

    `show_description_in_invoices: bool | Any`
    :   The type of the None singleton.

    `show_description_in_quotes: bool | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `tax_detail: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `tax_providers_fields: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `tiers: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `trial_end_action: str | Any`
    :   The type of the None singleton.

    `trial_period: int | Any`
    :   The type of the None singleton.

    `trial_period_unit: str | Any`
    :   The type of the None singleton.

    `updated_at: int | Any`
    :   The type of the None singleton.

<a id="ItemPriceList"></a>

`ItemPriceList(**data: Any)`
:   Paginated list of item prices
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `list_: list[airbyte_agent_sdk.connectors.chargebee.models.ItemPriceListListItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="ItemPriceListListItem"></a>

`ItemPriceListListItem(**data: Any)`
:   Nested schema for ItemPriceList.list_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `item_price: airbyte_agent_sdk.connectors.chargebee.models.ItemPrice | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ItemPriceListResultMeta"></a>

`ItemPriceListResultMeta(**data: Any)`
:   Metadata for item_price.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="ItemPriceSearchData"></a>

`ItemPriceSearchData(**data: Any)`
:   Search result data for item_price entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accounting_detail: dict[str, typing.Any] | None`
    :   Details related to accounting such as cost, revenue, expenses, etc.

    `archived_at: int | None`
    :   Date and time when the item was archived.

    `billing_cycles: int | None`
    :   Number of billing cycles for the item.

    `channel: str | None`
    :   The channel through which the item is sold.

    `created_at: int | None`
    :   Date and time when the item was created.

    `currency_code: str | None`
    :   The currency code used for pricing the item.

    `custom_fields: list[typing.Any] | None`
    :   Custom field entries for the item price.

    `description: str | None`
    :   Description of the item.

    `external_name: str | None`
    :   External name of the item.

    `free_quantity: int | None`
    :   Free quantity allowed for the item.

    `free_quantity_in_decimal: str | None`
    :   Free quantity allowed represented in decimal format.

    `id: str | None`
    :   Unique identifier for the item price.

    `invoice_notes: str | None`
    :   Notes to be included in the invoice for the item.

    `is_taxable: bool | None`
    :   Flag indicating whether the item is taxable.

    `item_family_id: str | None`
    :   Identifier for the item family to which the item belongs.

    `item_id: str | None`
    :   Unique identifier for the parent item.

    `item_type: str | None`
    :   Type of the item (e.g., product, service).

    `metadata: dict[str, typing.Any] | None`
    :   Additional metadata associated with the item.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the item price.

    `object_: str | None`
    :   Object type representing the item price.

    `period: int | None`
    :   Duration of the item's billing period.

    `period_unit: str | None`
    :   Unit of measurement for the billing period duration.

    `price: int | None`
    :   Price of the item.

    `price_in_decimal: str | None`
    :   Price of the item represented in decimal format.

    `pricing_model: str | None`
    :   The pricing model used for the item (e.g., flat fee, usage-based).

    `resource_version: int | None`
    :   Version of the item price resource.

    `shipping_period: int | None`
    :   Duration of the item's shipping period.

    `shipping_period_unit: str | None`
    :   Unit of measurement for the shipping period duration.

    `show_description_in_invoices: bool | None`
    :   Flag indicating whether to show the description in invoices.

    `show_description_in_quotes: bool | None`
    :   Flag indicating whether to show the description in quotes.

    `status: str | None`
    :   Current status of the item price (e.g., active, inactive).

    `tax_detail: dict[str, typing.Any] | None`
    :   Information about taxes associated with the item price.

    `tiers: list[typing.Any] | None`
    :   Different pricing tiers for the item.

    `trial_end_action: str | None`
    :   Action to be taken at the end of the trial period.

    `trial_period: int | None`
    :   Duration of the trial period.

    `trial_period_unit: str | None`
    :   Unit of measurement for the trial period duration.

    `updated_at: int | None`
    :   Date and time when the item price was last updated.

<a id="ItemPriceWrapper"></a>

`ItemPriceWrapper(**data: Any)`
:   ItemPriceWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `item_price: airbyte_agent_sdk.connectors.chargebee.models.ItemPrice | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ItemSearchData"></a>

`ItemSearchData(**data: Any)`
:   Search result data for item entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `applicable_items: list[typing.Any] | None`
    :   Items associated with the item

    `archived_at: int | None`
    :   Date and time when the item was archived

    `channel: str | None`
    :   Channel the item belongs to

    `custom_fields: list[typing.Any] | None`
    :   Custom field entries for the item

    `description: str | None`
    :   Description of the item

    `enabled_for_checkout: bool | None`
    :   Flag indicating if the item is enabled for checkout

    `enabled_in_portal: bool | None`
    :   Flag indicating if the item is enabled in the portal

    `external_name: str | None`
    :   Name of the item in an external system

    `gift_claim_redirect_url: str | None`
    :   URL to redirect for gift claim

    `id: str | None`
    :   Unique identifier for the item

    `included_in_mrr: bool | None`
    :   Flag indicating if the item is included in Monthly Recurring Revenue

    `is_giftable: bool | None`
    :   Flag indicating if the item is giftable

    `is_shippable: bool | None`
    :   Flag indicating if the item is shippable

    `item_applicability: str | None`
    :   Applicability of the item

    `item_family_id: str | None`
    :   ID of the item's family

    `metadata: dict[str, typing.Any] | None`
    :   Additional data associated with the item

    `metered: bool | None`
    :   Flag indicating if the item is metered

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the item

    `object_: str | None`
    :   Type of object

    `redirect_url: str | None`
    :   URL to redirect for the item

    `resource_version: int | None`
    :   Version of the resource

    `status: str | None`
    :   Status of the item

    `type_: str | None`
    :   Type of the item

    `unit: str | None`
    :   Unit associated with the item

    `updated_at: int | None`
    :   Date and time when the item was last updated

    `usage_calculation: str | None`
    :   Calculation method used for item usage

<a id="ItemWrapper"></a>

`ItemWrapper(**data: Any)`
:   ItemWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `item: airbyte_agent_sdk.connectors.chargebee.models.Item | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Order"></a>

`Order(**data: Any)`
:   Chargebee order object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount_adjusted: int | Any`
    :   The type of the None singleton.

    `amount_paid: int | Any`
    :   The type of the None singleton.

    `batch_id: str | Any`
    :   The type of the None singleton.

    `billing_address: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `business_entity_id: str | Any`
    :   The type of the None singleton.

    `cancellation_reason: str | Any`
    :   The type of the None singleton.

    `cancelled_at: int | Any`
    :   The type of the None singleton.

    `created_at: int | Any`
    :   The type of the None singleton.

    `created_by: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `custom_fields: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `customer_id: str | Any`
    :   The type of the None singleton.

    `deleted: bool | Any`
    :   The type of the None singleton.

    `delivered_at: int | Any`
    :   The type of the None singleton.

    `discount: int | Any`
    :   The type of the None singleton.

    `document_number: str | Any`
    :   The type of the None singleton.

    `fulfillment_status: str | Any`
    :   The type of the None singleton.

    `gift_id: str | Any`
    :   The type of the None singleton.

    `gift_note: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `invoice_id: str | Any`
    :   The type of the None singleton.

    `invoice_round_off_amount: int | Any`
    :   The type of the None singleton.

    `is_gifted: bool | Any`
    :   The type of the None singleton.

    `is_resent: bool | Any`
    :   The type of the None singleton.

    `line_item_discounts: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `line_item_taxes: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `linked_credit_notes: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `note: str | Any`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `order_date: int | Any`
    :   The type of the None singleton.

    `order_line_items: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `order_type: str | Any`
    :   The type of the None singleton.

    `original_order_id: str | Any`
    :   The type of the None singleton.

    `paid_on: int | Any`
    :   The type of the None singleton.

    `payment_status: str | Any`
    :   The type of the None singleton.

    `price_type: str | Any`
    :   The type of the None singleton.

    `reference_id: str | Any`
    :   The type of the None singleton.

    `refundable_credits: int | Any`
    :   The type of the None singleton.

    `refundable_credits_issued: int | Any`
    :   The type of the None singleton.

    `resend_reason: str | Any`
    :   The type of the None singleton.

    `resent_orders: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `resent_status: str | Any`
    :   The type of the None singleton.

    `resource_version: int | Any`
    :   The type of the None singleton.

    `rounding_adjustement: int | Any`
    :   The type of the None singleton.

    `shipment_carrier: str | Any`
    :   The type of the None singleton.

    `shipped_at: int | Any`
    :   The type of the None singleton.

    `shipping_address: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `shipping_cut_off_date: int | Any`
    :   The type of the None singleton.

    `shipping_date: int | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `status_update_at: int | Any`
    :   The type of the None singleton.

    `sub_total: int | Any`
    :   The type of the None singleton.

    `subscription_id: str | Any`
    :   The type of the None singleton.

    `tax: int | Any`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

    `tracking_id: str | Any`
    :   The type of the None singleton.

    `tracking_url: str | Any`
    :   The type of the None singleton.

    `updated_at: int | Any`
    :   The type of the None singleton.

<a id="OrderList"></a>

`OrderList(**data: Any)`
:   Paginated list of orders
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `list_: list[airbyte_agent_sdk.connectors.chargebee.models.OrderListListItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="OrderListListItem"></a>

`OrderListListItem(**data: Any)`
:   Nested schema for OrderList.list_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `order: airbyte_agent_sdk.connectors.chargebee.models.Order | Any`
    :   The type of the None singleton.

<a id="OrderListResultMeta"></a>

`OrderListResultMeta(**data: Any)`
:   Metadata for order.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="OrderSearchData"></a>

`OrderSearchData(**data: Any)`
:   Search result data for order entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount_adjusted: int | None`
    :   Adjusted amount for the order.

    `amount_paid: int | None`
    :   Amount paid for the order.

    `base_currency_code: str | None`
    :   The base currency code used for the order.

    `batch_id: str | None`
    :   Unique identifier for the batch the order belongs to.

    `billing_address: dict[str, typing.Any] | None`
    :   The billing address associated with the order

    `business_entity_id: str | None`
    :   Identifier for the business entity associated with the order.

    `cancellation_reason: str | None`
    :   Reason for order cancellation.

    `cancelled_at: int | None`
    :   Timestamp when the order was cancelled.

    `created_at: int | None`
    :   Timestamp when the order was created.

    `created_by: str | None`
    :   User or system that created the order.

    `currency_code: str | None`
    :   Currency code used for the order.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `customer_id: str | None`
    :   Identifier for the customer placing the order.

    `deleted: bool | None`
    :   Flag indicating if the order has been deleted.

    `delivered_at: int | None`
    :   Timestamp when the order was delivered.

    `discount: int | None`
    :   Discount amount applied to the order.

    `document_number: str | None`
    :   Unique document number associated with the order.

    `exchange_rate: float | None`
    :   Rate used for currency exchange in the order.

    `fulfillment_status: str | None`
    :   Status of fulfillment for the order.

    `gift_id: str | None`
    :   Identifier for any gift associated with the order.

    `gift_note: str | None`
    :   Note attached to any gift in the order.

    `id: str | None`
    :   Unique identifier for the order.

    `invoice_id: str | None`
    :   Identifier for the invoice associated with the order.

    `invoice_round_off_amount: int | None`
    :   Round-off amount applied to the invoice.

    `is_gifted: bool | None`
    :   Flag indicating if the order is a gift.

    `is_resent: bool | None`
    :   Flag indicating if the order has been resent.

    `line_item_discounts: list[typing.Any] | None`
    :   Discounts applied to individual line items

    `line_item_taxes: list[typing.Any] | None`
    :   Taxes applied to individual line items

    `linked_credit_notes: list[typing.Any] | None`
    :   Credit notes linked to the order

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   Additional notes or comments for the order.

    `object_: str | None`
    :   Type of object representing an order in the system.

    `order_date: int | None`
    :   Date when the order was created.

    `order_line_items: list[typing.Any] | None`
    :   List of line items in the order

    `order_type: str | None`
    :   Type of order such as purchase order or sales order.

    `original_order_id: str | None`
    :   Identifier for the original order if this is a modified order.

    `paid_on: int | None`
    :   Timestamp when the order was paid for.

    `payment_status: str | None`
    :   Status of payment for the order.

    `price_type: str | None`
    :   Type of pricing used for the order.

    `reference_id: str | None`
    :   Reference identifier for the order.

    `refundable_credits: int | None`
    :   Credits that can be refunded for the whole order.

    `refundable_credits_issued: int | None`
    :   Credits already issued for refund for the whole order.

    `resend_reason: str | None`
    :   Reason for resending the order.

    `resent_orders: list[typing.Any] | None`
    :   Orders that were resent to the customer

    `resent_status: str | None`
    :   Status of the resent order.

    `resource_version: int | None`
    :   Version of the resource or order data.

    `rounding_adjustement: int | None`
    :   Adjustment made for rounding off the order amount.

    `shipment_carrier: str | None`
    :   Carrier for shipping the order.

    `shipped_at: int | None`
    :   Timestamp when the order was shipped.

    `shipping_address: dict[str, typing.Any] | None`
    :   The shipping address for the order

    `shipping_cut_off_date: int | None`
    :   Date indicating the shipping cut-off for the order.

    `shipping_date: int | None`
    :   Date when the order is scheduled for shipping.

    `status: str | None`
    :   Current status of the order.

    `status_update_at: int | None`
    :   Timestamp when the status of the order was last updated.

    `sub_total: int | None`
    :   Sub-total amount for the order before applying taxes or discounts.

    `subscription_id: str | None`
    :   Identifier for the subscription associated with the order.

    `tax: int | None`
    :   Total tax amount for the order.

    `total: int | None`
    :   Total amount including taxes and discounts for the order.

    `tracking_id: str | None`
    :   Tracking identifier for the order shipment.

    `tracking_url: str | None`
    :   URL for tracking the order shipment.

    `updated_at: int | None`
    :   Timestamp when the order data was last updated.

<a id="OrderWrapper"></a>

`OrderWrapper(**data: Any)`
:   OrderWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `order: airbyte_agent_sdk.connectors.chargebee.models.Order | Any`
    :   The type of the None singleton.

<a id="PaymentSource"></a>

`PaymentSource(**data: Any)`
:   Chargebee payment source object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amazon_payment: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `bank_account: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `business_entity_id: str | Any`
    :   The type of the None singleton.

    `card: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `created_at: int | Any`
    :   The type of the None singleton.

    `custom_fields: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `customer_id: str | Any`
    :   The type of the None singleton.

    `deleted: bool | Any`
    :   The type of the None singleton.

    `gateway: str | Any`
    :   The type of the None singleton.

    `gateway_account_id: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `ip_address: str | Any`
    :   The type of the None singleton.

    `issuing_country: str | Any`
    :   The type of the None singleton.

    `mandates: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `paypal: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `reference_id: str | Any`
    :   The type of the None singleton.

    `resource_version: int | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `updated_at: int | Any`
    :   The type of the None singleton.

    `upi: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="PaymentSourceList"></a>

`PaymentSourceList(**data: Any)`
:   Paginated list of payment sources
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `list_: list[airbyte_agent_sdk.connectors.chargebee.models.PaymentSourceListListItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="PaymentSourceListListItem"></a>

`PaymentSourceListListItem(**data: Any)`
:   Nested schema for PaymentSourceList.list_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `payment_source: airbyte_agent_sdk.connectors.chargebee.models.PaymentSource | Any`
    :   The type of the None singleton.

<a id="PaymentSourceListResultMeta"></a>

`PaymentSourceListResultMeta(**data: Any)`
:   Metadata for payment_source.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="PaymentSourceSearchData"></a>

`PaymentSourceSearchData(**data: Any)`
:   Search result data for payment_source entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amazon_payment: dict[str, typing.Any] | None`
    :   Data related to Amazon Pay payment source

    `bank_account: dict[str, typing.Any] | None`
    :   Data related to bank account payment source

    `business_entity_id: str | None`
    :   Identifier for the business entity associated with the payment source

    `card: dict[str, typing.Any] | None`
    :   Data related to card payment source

    `created_at: int | None`
    :   Timestamp indicating when the payment source was created

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `customer_id: str | None`
    :   Unique identifier for the customer associated with the payment source

    `deleted: bool | None`
    :   Indicates if the payment source has been deleted

    `gateway: str | None`
    :   Name of the payment gateway used for the payment source

    `gateway_account_id: str | None`
    :   Identifier for the gateway account tied to the payment source

    `id: str | None`
    :   Unique identifier for the payment source

    `ip_address: str | None`
    :   IP address associated with the payment source

    `issuing_country: str | None`
    :   Country where the payment source was issued

    `mandates: dict[str, typing.Any] | None`
    :   Data related to mandates for payments

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   Type of object, e.g., payment_source

    `paypal: dict[str, typing.Any] | None`
    :   Data related to PayPal payment source

    `reference_id: str | None`
    :   Reference identifier for the payment source

    `resource_version: int | None`
    :   Version of the payment source resource

    `status: str | None`
    :   Status of the payment source, e.g., active or inactive

    `type_: str | None`
    :   Type of payment source, e.g., card, bank_account

    `updated_at: int | None`
    :   Timestamp indicating when the payment source was last updated

    `upi: dict[str, typing.Any] | None`
    :   Data related to UPI payment source

<a id="PaymentSourceWrapper"></a>

`PaymentSourceWrapper(**data: Any)`
:   PaymentSourceWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `payment_source: airbyte_agent_sdk.connectors.chargebee.models.PaymentSource | Any`
    :   The type of the None singleton.

<a id="Subscription"></a>

`Subscription(**data: Any)`
:   Chargebee subscription object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `activated_at: int | Any`
    :   The type of the None singleton.

    `addons: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `auto_close_invoices: bool | Any`
    :   The type of the None singleton.

    `auto_collection: str | Any`
    :   The type of the None singleton.

    `base_currency_code: str | Any`
    :   The type of the None singleton.

    `billing_period: int | Any`
    :   The type of the None singleton.

    `billing_period_unit: str | Any`
    :   The type of the None singleton.

    `business_entity_id: str | Any`
    :   The type of the None singleton.

    `cancel_reason: str | Any`
    :   The type of the None singleton.

    `cancelled_at: int | Any`
    :   The type of the None singleton.

    `cancelled_at_term_end: bool | Any`
    :   The type of the None singleton.

    `cf_mandate_id: str | Any`
    :   The type of the None singleton.

    `changes_scheduled_at: int | Any`
    :   The type of the None singleton.

    `channel: str | Any`
    :   The type of the None singleton.

    `charged_items: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `contract_term: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `coupons: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `created_at: int | Any`
    :   The type of the None singleton.

    `created_from_ip: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `current_term_end: int | Any`
    :   The type of the None singleton.

    `current_term_start: int | Any`
    :   The type of the None singleton.

    `custom_fields: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `customer_id: str | Any`
    :   The type of the None singleton.

    `deleted: bool | Any`
    :   The type of the None singleton.

    `discounts: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `due_invoices_count: int | Any`
    :   The type of the None singleton.

    `due_since: int | Any`
    :   The type of the None singleton.

    `exchange_rate: float | Any`
    :   The type of the None singleton.

    `free_period: int | Any`
    :   The type of the None singleton.

    `free_period_unit: str | Any`
    :   The type of the None singleton.

    `has_scheduled_advance_invoices: bool | Any`
    :   The type of the None singleton.

    `has_scheduled_changes: bool | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `invoice_notes: str | Any`
    :   The type of the None singleton.

    `item_tiers: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `meta_data: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `mrr: int | Any`
    :   The type of the None singleton.

    `next_billing_at: int | Any`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `offline_payment_method: str | Any`
    :   The type of the None singleton.

    `override_relationship: bool | Any`
    :   The type of the None singleton.

    `pause_date: int | Any`
    :   The type of the None singleton.

    `payment_source_id: str | Any`
    :   The type of the None singleton.

    `plan_amount: int | Any`
    :   The type of the None singleton.

    `plan_amount_in_decimal: str | Any`
    :   The type of the None singleton.

    `plan_free_quantity: int | Any`
    :   The type of the None singleton.

    `plan_free_quantity_in_decimal: str | Any`
    :   The type of the None singleton.

    `plan_id: str | Any`
    :   The type of the None singleton.

    `plan_quantity: int | Any`
    :   The type of the None singleton.

    `plan_quantity_in_decimal: str | Any`
    :   The type of the None singleton.

    `plan_unit_price: int | Any`
    :   The type of the None singleton.

    `plan_unit_price_in_decimal: str | Any`
    :   The type of the None singleton.

    `po_number: str | Any`
    :   The type of the None singleton.

    `remaining_billing_cycles: int | Any`
    :   The type of the None singleton.

    `resource_version: int | Any`
    :   The type of the None singleton.

    `resume_date: int | Any`
    :   The type of the None singleton.

    `shipping_address: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `started_at: int | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `subscription_items: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `total_dues: int | Any`
    :   The type of the None singleton.

    `trial_end: int | Any`
    :   The type of the None singleton.

    `trial_end_action: str | Any`
    :   The type of the None singleton.

    `trial_start: int | Any`
    :   The type of the None singleton.

    `updated_at: int | Any`
    :   The type of the None singleton.

<a id="SubscriptionList"></a>

`SubscriptionList(**data: Any)`
:   Paginated list of subscriptions
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `list_: list[airbyte_agent_sdk.connectors.chargebee.models.SubscriptionListListItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="SubscriptionListListItem"></a>

`SubscriptionListListItem(**data: Any)`
:   Nested schema for SubscriptionList.list_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `subscription: airbyte_agent_sdk.connectors.chargebee.models.Subscription | Any`
    :   The type of the None singleton.

<a id="SubscriptionListResultMeta"></a>

`SubscriptionListResultMeta(**data: Any)`
:   Metadata for subscription.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="SubscriptionSearchData"></a>

`SubscriptionSearchData(**data: Any)`
:   Search result data for subscription entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `activated_at: int | None`
    :   The date and time when the subscription was activated.

    `addons: list[typing.Any] | None`
    :   Represents any additional features or services added to the subscription

    `affiliate_token: str | None`
    :   The affiliate token associated with the subscription.

    `auto_close_invoices: bool | None`
    :   Defines if the invoices are automatically closed or not.

    `auto_collection: str | None`
    :   Indicates if auto-collection is enabled for the subscription.

    `base_currency_code: str | None`
    :   The base currency code used for the subscription.

    `billing_period: int | None`
    :   The billing period duration for the subscription.

    `billing_period_unit: str | None`
    :   The unit of the billing period.

    `business_entity_id: str | None`
    :   The ID of the business entity to which the subscription belongs.

    `cancel_reason: str | None`
    :   The reason for the cancellation of the subscription.

    `cancel_reason_code: str | None`
    :   The code associated with the cancellation reason.

    `cancel_schedule_created_at: int | None`
    :   The date and time when the cancellation schedule was created.

    `cancelled_at: int | None`
    :   The date and time when the subscription was cancelled.

    `channel: str | None`
    :   The channel through which the subscription was acquired.

    `charged_event_based_addons: list[typing.Any] | None`
    :   Details of addons charged based on events

    `charged_items: list[typing.Any] | None`
    :   Lists the items that have been charged as part of the subscription

    `contract_term: dict[str, typing.Any] | None`
    :   Contains details about the contract term of the subscription

    `contract_term_billing_cycle_on_renewal: int | None`
    :   Indicates if the contract term billing cycle is applied on renewal.

    `coupon: str | None`
    :   The coupon applied to the subscription.

    `coupons: list[typing.Any] | None`
    :   Details of applied coupons

    `create_pending_invoices: bool | None`
    :   Indicates if pending invoices are created.

    `created_at: int | None`
    :   The date and time of the creation of the subscription.

    `created_from_ip: str | None`
    :   The IP address from which the subscription was created.

    `currency_code: str | None`
    :   The currency code used for the subscription.

    `current_term_end: int | None`
    :   The end date of the current term for the subscription.

    `current_term_start: int | None`
    :   The start date of the current term for the subscription.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `customer_id: str | None`
    :   The ID of the customer associated with the subscription.

    `deleted: bool | None`
    :   Indicates if the subscription has been deleted.

    `discounts: list[typing.Any] | None`
    :   Includes any discounts applied to the subscription

    `due_invoices_count: int | None`
    :   The count of due invoices for the subscription.

    `due_since: int | None`
    :   The date since which the invoices are due.

    `event_based_addons: list[typing.Any] | None`
    :   Specifies any event-based addons associated with the subscription

    `exchange_rate: float | None`
    :   The exchange rate used for currency conversion.

    `free_period: int | None`
    :   The duration of the free period for the subscription.

    `free_period_unit: str | None`
    :   The unit of the free period duration.

    `gift_id: str | None`
    :   The ID of the gift associated with the subscription.

    `has_scheduled_advance_invoices: bool | None`
    :   Indicates if there are scheduled advance invoices for the subscription.

    `has_scheduled_changes: bool | None`
    :   Indicates if there are scheduled changes for the subscription.

    `id: str | None`
    :   The unique ID of the subscription.

    `invoice_notes: str | None`
    :   Any notes added to the invoices of the subscription.

    `item_tiers: list[typing.Any] | None`
    :   Provides information about tiers or levels for specific subscription items

    `meta_data: dict[str, typing.Any] | None`
    :   Additional metadata associated with subscription

    `metadata: dict[str, typing.Any] | None`
    :   Additional metadata associated with subscription

    `model_config`
    :   The type of the None singleton.

    `mrr: int | None`
    :   The monthly recurring revenue generated by the subscription.

    `next_billing_at: int | None`
    :   The date and time of the next billing event for the subscription.

    `object_: str | None`
    :   The type of object (subscription).

    `offline_payment_method: str | None`
    :   The offline payment method used for the subscription.

    `override_relationship: bool | None`
    :   Indicates if the existing relationship is overridden by this subscription.

    `pause_date: int | None`
    :   The date on which the subscription was paused.

    `payment_source_id: str | None`
    :   The ID of the payment source used for the subscription.

    `plan_amount: int | None`
    :   The total amount charged for the plan of the subscription.

    `plan_amount_in_decimal: str | None`
    :   The total amount charged for the plan in decimal format.

    `plan_free_quantity: int | None`
    :   The free quantity included in the plan of the subscription.

    `plan_free_quantity_in_decimal: str | None`
    :   The free quantity included in the plan in decimal format.

    `plan_id: str | None`
    :   The ID of the plan associated with the subscription.

    `plan_quantity: int | None`
    :   The quantity of the plan included in the subscription.

    `plan_quantity_in_decimal: str | None`
    :   The quantity of the plan in decimal format.

    `plan_unit_price: int | None`
    :   The unit price of the plan for the subscription.

    `plan_unit_price_in_decimal: str | None`
    :   The unit price of the plan in decimal format.

    `po_number: str | None`
    :   The purchase order number associated with the subscription.

    `referral_info: dict[str, typing.Any] | None`
    :   Contains details related to any referral information associated with the subscription

    `remaining_billing_cycles: int | None`
    :   The count of remaining billing cycles for the subscription.

    `resource_version: int | None`
    :   The version of the resource (subscription).

    `resume_date: int | None`
    :   The date on which the subscription was resumed.

    `setup_fee: int | None`
    :   The setup fee charged for the subscription.

    `shipping_address: dict[str, typing.Any] | None`
    :   Stores the shipping address related to the subscription

    `start_date: int | None`
    :   The start date of the subscription.

    `started_at: int | None`
    :   The date and time when the subscription started.

    `status: str | None`
    :   The current status of the subscription.

    `subscription_items: list[typing.Any] | None`
    :   Lists individual items included in the subscription

    `total_dues: int | None`
    :   The total amount of dues for the subscription.

    `trial_end: int | None`
    :   The end date of the trial period for the subscription.

    `trial_end_action: str | None`
    :   The action to be taken at the end of the trial period.

    `trial_start: int | None`
    :   The start date of the trial period for the subscription.

    `updated_at: int | None`
    :   The date and time when the subscription was last updated.

<a id="SubscriptionWrapper"></a>

`SubscriptionWrapper(**data: Any)`
:   SubscriptionWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `subscription: airbyte_agent_sdk.connectors.chargebee.models.Subscription | Any`
    :   The type of the None singleton.

<a id="Transaction"></a>

`Transaction(**data: Any)`
:   Chargebee transaction object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   The type of the None singleton.

    `amount_capturable: int | Any`
    :   The type of the None singleton.

    `amount_unused: int | Any`
    :   The type of the None singleton.

    `authorization_reason: str | Any`
    :   The type of the None singleton.

    `base_currency_code: str | Any`
    :   The type of the None singleton.

    `business_entity_id: str | Any`
    :   The type of the None singleton.

    `created_at: int | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `custom_fields: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `customer_id: str | Any`
    :   The type of the None singleton.

    `date: int | Any`
    :   The type of the None singleton.

    `deleted: bool | Any`
    :   The type of the None singleton.

    `error_code: str | Any`
    :   The type of the None singleton.

    `error_text: str | Any`
    :   The type of the None singleton.

    `exchange_rate: float | Any`
    :   The type of the None singleton.

    `fraud_flag: str | Any`
    :   The type of the None singleton.

    `fraud_reason: str | Any`
    :   The type of the None singleton.

    `gateway: str | Any`
    :   The type of the None singleton.

    `gateway_account_id: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `id_at_gateway: str | Any`
    :   The type of the None singleton.

    `iin: str | Any`
    :   The type of the None singleton.

    `initiator_type: str | Any`
    :   The type of the None singleton.

    `last4: str | Any`
    :   The type of the None singleton.

    `linked_credit_notes: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `linked_invoices: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `linked_payments: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `linked_refunds: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `masked_card_number: str | Any`
    :   The type of the None singleton.

    `merchant_reference_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `payment_method: str | Any`
    :   The type of the None singleton.

    `payment_method_details: Any`
    :   The type of the None singleton.

    `payment_source_id: str | Any`
    :   The type of the None singleton.

    `reference_authorization_id: str | Any`
    :   The type of the None singleton.

    `reference_number: str | Any`
    :   The type of the None singleton.

    `reference_transaction_id: str | Any`
    :   The type of the None singleton.

    `refunded_txn_id: str | Any`
    :   The type of the None singleton.

    `resource_version: int | Any`
    :   The type of the None singleton.

    `reversal_transaction_id: str | Any`
    :   The type of the None singleton.

    `settled_at: int | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `subscription_id: str | Any`
    :   The type of the None singleton.

    `three_d_secure: bool | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `updated_at: int | Any`
    :   The type of the None singleton.

    `voided_at: int | Any`
    :   The type of the None singleton.

<a id="TransactionList"></a>

`TransactionList(**data: Any)`
:   Paginated list of transactions
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `list_: list[airbyte_agent_sdk.connectors.chargebee.models.TransactionListListItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="TransactionListListItem"></a>

`TransactionListListItem(**data: Any)`
:   Nested schema for TransactionList.list_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `transaction: airbyte_agent_sdk.connectors.chargebee.models.Transaction | Any`
    :   The type of the None singleton.

<a id="TransactionListResultMeta"></a>

`TransactionListResultMeta(**data: Any)`
:   Metadata for transaction.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_offset: str | Any`
    :   The type of the None singleton.

<a id="TransactionSearchData"></a>

`TransactionSearchData(**data: Any)`
:   Search result data for transaction entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | None`
    :   The total amount of the transaction.

    `amount_capturable: int | None`
    :   The remaining amount that can be captured in the transaction.

    `amount_unused: int | None`
    :   The amount in the transaction that remains unused.

    `authorization_reason: str | None`
    :   Reason for authorization of the transaction.

    `base_currency_code: str | None`
    :   The base currency code of the transaction.

    `business_entity_id: str | None`
    :   The ID of the business entity related to the transaction.

    `cn_create_reason_code: str | None`
    :   Reason code for creating a credit note.

    `cn_date: int | None`
    :   Date of the credit note.

    `cn_reference_invoice_id: str | None`
    :   ID of the invoice referenced in the credit note.

    `cn_status: str | None`
    :   Status of the credit note.

    `cn_total: int | None`
    :   Total amount of the credit note.

    `currency_code: str | None`
    :   The currency code of the transaction.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `customer_id: str | None`
    :   The ID of the customer associated with the transaction.

    `date: int | None`
    :   Date of the transaction.

    `deleted: bool | None`
    :   Flag indicating if the transaction is deleted.

    `error_code: str | None`
    :   Error code associated with the transaction.

    `error_detail: str | None`
    :   Detailed error information related to the transaction.

    `error_text: str | None`
    :   Error message text of the transaction.

    `exchange_rate: float | None`
    :   Exchange rate used in the transaction.

    `fraud_flag: str | None`
    :   Flag indicating if the transaction is flagged for fraud.

    `fraud_reason: str | None`
    :   Reason for flagging the transaction as fraud.

    `gateway: str | None`
    :   The payment gateway used in the transaction.

    `gateway_account_id: str | None`
    :   ID of the gateway account used in the transaction.

    `id: str | None`
    :   Unique identifier of the transaction.

    `id_at_gateway: str | None`
    :   Transaction ID assigned by the gateway.

    `iin: str | None`
    :   Bank identification number of the transaction.

    `initiator_type: str | None`
    :   Type of initiator involved in the transaction.

    `last4: str | None`
    :   Last 4 digits of the card used in the transaction.

    `linked_credit_notes: list[typing.Any] | None`
    :   Linked credit notes associated with the transaction.

    `linked_invoices: list[typing.Any] | None`
    :   Linked invoices associated with the transaction.

    `linked_payments: list[typing.Any] | None`
    :   Linked payments associated with the transaction.

    `linked_refunds: list[typing.Any] | None`
    :   Linked refunds associated with the transaction.

    `masked_card_number: str | None`
    :   Masked card number used in the transaction.

    `merchant_reference_id: str | None`
    :   Merchant reference ID of the transaction.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   Type of object representing the transaction.

    `payment_method: str | None`
    :   Payment method used in the transaction.

    `payment_method_details: str | None`
    :   Details of the payment method used in the transaction.

    `payment_source_id: str | None`
    :   ID of the payment source used in the transaction.

    `reference_authorization_id: str | None`
    :   Reference authorization ID of the transaction.

    `reference_number: str | None`
    :   Reference number associated with the transaction.

    `reference_transaction_id: str | None`
    :   ID of the reference transaction.

    `refrence_number: str | None`
    :   Reference number of the transaction.

    `refunded_txn_id: str | None`
    :   ID of the refunded transaction.

    `resource_version: int | None`
    :   Resource version of the transaction.

    `reversal_transaction_id: str | None`
    :   ID of the reversal transaction, if any.

    `settled_at: int | None`
    :   Date when the transaction was settled.

    `status: str | None`
    :   Status of the transaction.

    `subscription_id: str | None`
    :   ID of the subscription related to the transaction.

    `three_d_secure: bool | None`
    :   Flag indicating if 3D secure was used in the transaction.

    `txn_amount: int | None`
    :   Amount of the transaction.

    `txn_date: int | None`
    :   Date of the transaction.

    `type_: str | None`
    :   Type of the transaction.

    `updated_at: int | None`
    :   Date when the transaction was last updated.

    `voided_at: int | None`
    :   Date when the transaction was voided.

<a id="TransactionWrapper"></a>

`TransactionWrapper(**data: Any)`
:   TransactionWrapper type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `transaction: airbyte_agent_sdk.connectors.chargebee.models.Transaction | Any`
    :   The type of the None singleton.