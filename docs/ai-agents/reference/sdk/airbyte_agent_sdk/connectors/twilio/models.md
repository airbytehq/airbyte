---
id: airbyte_agent_sdk-connectors-twilio-models
title: airbyte_agent_sdk.connectors.twilio.models
---

Module airbyte_agent_sdk.connectors.twilio.models
=================================================
Pydantic models for twilio connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

`Account(**data: Any)`
:   A Twilio account
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auth_token: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_updated: str | Any | None`
    :   The type of the None singleton.

    `friendly_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `owner_account_sid: str | Any | None`
    :   The type of the None singleton.

    `sid: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `subresource_uris: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`AccountsList(**data: Any)`
:   Paginated list of accounts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accounts: list[airbyte_agent_sdk.connectors.twilio.models.Account] | Any`
    :   The type of the None singleton.

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

    `previous_page_uri: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`AccountsListResultMeta(**data: Any)`
:   Metadata for accounts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

`AccountsSearchData(**data: Any)`
:   Search result data for accounts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date_created: str | None`
    :   The timestamp when the account was created

    `date_updated: str | None`
    :   The timestamp when the account was last updated

    `friendly_name: str | None`
    :   A user-defined friendly name for the account

    `model_config`
    :   The type of the None singleton.

    `owner_account_sid: str | None`
    :   The SID of the owner account

    `sid: str | None`
    :   The unique identifier for the account

    `status: str | None`
    :   The current status of the account

    `type_: str | None`
    :   The type of the account

    `uri: str | None`
    :   The URI for accessing the account resource

`Address(**data: Any)`
:   A Twilio address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `customer_name: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_updated: str | Any | None`
    :   The type of the None singleton.

    `emergency_enabled: bool | Any | None`
    :   The type of the None singleton.

    `friendly_name: str | Any | None`
    :   The type of the None singleton.

    `iso_country: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `postal_code: str | Any | None`
    :   The type of the None singleton.

    `region: str | Any | None`
    :   The type of the None singleton.

    `sid: str | Any | None`
    :   The type of the None singleton.

    `street: str | Any | None`
    :   The type of the None singleton.

    `street_secondary: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

    `validated: bool | Any | None`
    :   The type of the None singleton.

    `verified: bool | Any | None`
    :   The type of the None singleton.

`AddressesList(**data: Any)`
:   Paginated list of addresses
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `addresses: list[airbyte_agent_sdk.connectors.twilio.models.Address] | Any`
    :   The type of the None singleton.

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

    `previous_page_uri: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`AddressesListResultMeta(**data: Any)`
:   Metadata for addresses.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

`AddressesSearchData(**data: Any)`
:   Search result data for addresses entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The account SID associated with this address

    `city: str | None`
    :   The city of the address

    `customer_name: str | None`
    :   The customer name associated with this address

    `friendly_name: str | None`
    :   A friendly name for the address

    `iso_country: str | None`
    :   The ISO 3166-1 alpha-2 country code

    `model_config`
    :   The type of the None singleton.

    `postal_code: str | None`
    :   The postal code

    `region: str | None`
    :   The region or state

    `sid: str | None`
    :   The unique identifier of the address

    `street: str | None`
    :   The street address

    `validated: bool | None`
    :   Whether the address has been validated

    `verified: bool | None`
    :   Whether the address has been verified

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

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[AccountsSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[AddressesSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[CallsSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[ConferencesSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[IncomingPhoneNumbersSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[MessagesSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[OutgoingCallerIdsSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[QueuesSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[RecordingsSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[TranscriptionsSearchData]
    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult[UsageRecordsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AccountsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`AccountsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AddressesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`AddressesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CallsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`CallsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ConferencesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`ConferencesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[IncomingPhoneNumbersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IncomingPhoneNumbersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[MessagesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`MessagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[OutgoingCallerIdsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`OutgoingCallerIdsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[QueuesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`QueuesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[RecordingsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`RecordingsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TranscriptionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TranscriptionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsageRecordsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`UsageRecordsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`Call(**data: Any)`
:   A Twilio call
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | Any | None`
    :   The type of the None singleton.

    `annotation: str | Any | None`
    :   The type of the None singleton.

    `answered_by: str | Any | None`
    :   The type of the None singleton.

    `api_version: str | Any | None`
    :   The type of the None singleton.

    `caller_name: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_updated: str | Any | None`
    :   The type of the None singleton.

    `direction: str | Any | None`
    :   The type of the None singleton.

    `duration: str | Any | None`
    :   The type of the None singleton.

    `end_time: str | Any | None`
    :   The type of the None singleton.

    `forwarded_from: str | Any | None`
    :   The type of the None singleton.

    `from_: str | Any | None`
    :   The type of the None singleton.

    `from_formatted: str | Any | None`
    :   The type of the None singleton.

    `group_sid: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `parent_call_sid: str | Any | None`
    :   The type of the None singleton.

    `phone_number_sid: str | Any | None`
    :   The type of the None singleton.

    `price: str | Any | None`
    :   The type of the None singleton.

    `price_unit: str | Any | None`
    :   The type of the None singleton.

    `queue_time: str | Any | None`
    :   The type of the None singleton.

    `sid: str | Any | None`
    :   The type of the None singleton.

    `start_time: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `subresource_uris: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `to: str | Any | None`
    :   The type of the None singleton.

    `to_formatted: str | Any | None`
    :   The type of the None singleton.

    `trunk_sid: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`CallsList(**data: Any)`
:   Paginated list of calls
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `calls: list[airbyte_agent_sdk.connectors.twilio.models.Call] | Any`
    :   The type of the None singleton.

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

    `previous_page_uri: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`CallsListResultMeta(**data: Any)`
:   Metadata for calls.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

`CallsSearchData(**data: Any)`
:   Search result data for calls entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The unique identifier for the account associated with the call

    `date_created: str | None`
    :   The date and time when the call record was created

    `date_updated: str | None`
    :   The date and time when the call record was last updated

    `direction: str | None`
    :   The direction of the call (inbound or outbound)

    `duration: str | None`
    :   The duration of the call in seconds

    `end_time: str | None`
    :   The date and time when the call ended

    `from_: str | None`
    :   The phone number that made the call

    `model_config`
    :   The type of the None singleton.

    `price: str | None`
    :   The cost of the call

    `price_unit: str | None`
    :   The currency unit of the call cost

    `sid: str | None`
    :   The unique identifier for the call

    `start_time: str | None`
    :   The date and time when the call started

    `status: str | None`
    :   The current status of the call

    `to: str | None`
    :   The phone number that received the call

`Conference(**data: Any)`
:   A Twilio conference
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | Any | None`
    :   The type of the None singleton.

    `api_version: str | Any | None`
    :   The type of the None singleton.

    `call_sid_ending_conference: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_updated: str | Any | None`
    :   The type of the None singleton.

    `friendly_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reason_conference_ended: str | Any | None`
    :   The type of the None singleton.

    `region: str | Any | None`
    :   The type of the None singleton.

    `sid: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `subresource_uris: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`ConferencesList(**data: Any)`
:   Paginated list of conferences
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `conferences: list[airbyte_agent_sdk.connectors.twilio.models.Conference] | Any`
    :   The type of the None singleton.

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

    `previous_page_uri: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`ConferencesListResultMeta(**data: Any)`
:   Metadata for conferences.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

`ConferencesSearchData(**data: Any)`
:   Search result data for conferences entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The account SID associated with the conference

    `date_created: str | None`
    :   When the conference was created

    `date_updated: str | None`
    :   When the conference was last updated

    `friendly_name: str | None`
    :   A friendly name for the conference

    `model_config`
    :   The type of the None singleton.

    `region: str | None`
    :   The region where the conference is hosted

    `sid: str | None`
    :   The unique identifier of the conference

    `status: str | None`
    :   The current status of the conference

`IncomingPhoneNumber(**data: Any)`
:   A Twilio incoming phone number
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | Any | None`
    :   The type of the None singleton.

    `address_requirements: str | Any | None`
    :   The type of the None singleton.

    `address_sid: str | Any | None`
    :   The type of the None singleton.

    `api_version: str | Any | None`
    :   The type of the None singleton.

    `beta: bool | Any | None`
    :   The type of the None singleton.

    `bundle_sid: str | Any | None`
    :   The type of the None singleton.

    `capabilities: airbyte_agent_sdk.connectors.twilio.models.IncomingPhoneNumberCapabilities | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_updated: str | Any | None`
    :   The type of the None singleton.

    `emergency_address_sid: str | Any | None`
    :   The type of the None singleton.

    `emergency_address_status: str | Any | None`
    :   The type of the None singleton.

    `emergency_status: str | Any | None`
    :   The type of the None singleton.

    `friendly_name: str | Any | None`
    :   The type of the None singleton.

    `identity_sid: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `origin: str | Any | None`
    :   The type of the None singleton.

    `phone_number: str | Any | None`
    :   The type of the None singleton.

    `sid: str | Any | None`
    :   The type of the None singleton.

    `sms_application_sid: str | Any | None`
    :   The type of the None singleton.

    `sms_fallback_method: str | Any | None`
    :   The type of the None singleton.

    `sms_fallback_url: str | Any | None`
    :   The type of the None singleton.

    `sms_method: str | Any | None`
    :   The type of the None singleton.

    `sms_url: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `status_callback: str | Any | None`
    :   The type of the None singleton.

    `status_callback_method: str | Any | None`
    :   The type of the None singleton.

    `subresource_uris: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `trunk_sid: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

    `voice_application_sid: str | Any | None`
    :   The type of the None singleton.

    `voice_caller_id_lookup: bool | Any | None`
    :   The type of the None singleton.

    `voice_fallback_method: str | Any | None`
    :   The type of the None singleton.

    `voice_fallback_url: str | Any | None`
    :   The type of the None singleton.

    `voice_method: str | Any | None`
    :   The type of the None singleton.

    `voice_receive_mode: str | Any | None`
    :   The type of the None singleton.

    `voice_url: str | Any | None`
    :   The type of the None singleton.

`IncomingPhoneNumberCapabilities(**data: Any)`
:   Capabilities of this phone number
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `fax: bool | Any | None`
    :   The type of the None singleton.

    `mms: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `sms: bool | Any | None`
    :   The type of the None singleton.

    `voice: bool | Any | None`
    :   The type of the None singleton.

`IncomingPhoneNumbersList(**data: Any)`
:   Paginated list of incoming phone numbers
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `incoming_phone_numbers: list[airbyte_agent_sdk.connectors.twilio.models.IncomingPhoneNumber] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

    `previous_page_uri: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`IncomingPhoneNumbersListResultMeta(**data: Any)`
:   Metadata for incoming_phone_numbers.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

`IncomingPhoneNumbersSearchData(**data: Any)`
:   Search result data for incoming_phone_numbers entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The SID of the account that owns this phone number

    `capabilities: dict[str, typing.Any] | None`
    :   Capabilities of this phone number

    `date_created: str | None`
    :   When the phone number was created

    `date_updated: str | None`
    :   When the phone number was last updated

    `friendly_name: str | None`
    :   A user-assigned friendly name for this phone number

    `model_config`
    :   The type of the None singleton.

    `phone_number: str | None`
    :   The phone number in E.164 format

    `sid: str | None`
    :   The SID of this phone number

    `status: str | None`
    :   Status of the phone number

`Message(**data: Any)`
:   A Twilio message
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | Any | None`
    :   The type of the None singleton.

    `api_version: str | Any | None`
    :   The type of the None singleton.

    `body: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_sent: str | Any | None`
    :   The type of the None singleton.

    `date_updated: str | Any | None`
    :   The type of the None singleton.

    `direction: str | Any | None`
    :   The type of the None singleton.

    `error_code: str | Any | None`
    :   The type of the None singleton.

    `error_message: str | Any | None`
    :   The type of the None singleton.

    `from_: str | Any | None`
    :   The type of the None singleton.

    `messaging_service_sid: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `num_media: str | Any | None`
    :   The type of the None singleton.

    `num_segments: str | Any | None`
    :   The type of the None singleton.

    `price: str | Any | None`
    :   The type of the None singleton.

    `price_unit: str | Any | None`
    :   The type of the None singleton.

    `sid: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `subresource_uris: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `to: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`MessagesList(**data: Any)`
:   Paginated list of messages
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `messages: list[airbyte_agent_sdk.connectors.twilio.models.Message] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

    `previous_page_uri: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`MessagesListResultMeta(**data: Any)`
:   Metadata for messages.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

`MessagesSearchData(**data: Any)`
:   Search result data for messages entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The unique identifier for the account associated with this message

    `body: str | None`
    :   The text body of the message

    `date_created: str | None`
    :   The date and time when the message was created

    `date_sent: str | None`
    :   The date and time when the message was sent

    `direction: str | None`
    :   The direction of the message

    `error_code: str | None`
    :   The error code associated with the message if any

    `error_message: str | None`
    :   The error message description if the message failed

    `from_: str | None`
    :   The phone number or sender ID that sent the message

    `model_config`
    :   The type of the None singleton.

    `num_media: str | None`
    :   The number of media files included in the message

    `num_segments: str | None`
    :   The number of message segments

    `price: str | None`
    :   The cost of the message

    `price_unit: str | None`
    :   The currency unit used for pricing

    `sid: str | None`
    :   The unique identifier for this message

    `status: str | None`
    :   The status of the message

    `to: str | None`
    :   The phone number or recipient ID the message was sent to

`OutgoingCallerId(**data: Any)`
:   A Twilio outgoing caller ID
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_updated: str | Any | None`
    :   The type of the None singleton.

    `friendly_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `phone_number: str | Any | None`
    :   The type of the None singleton.

    `sid: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`OutgoingCallerIdsList(**data: Any)`
:   Paginated list of outgoing caller IDs
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `outgoing_caller_ids: list[airbyte_agent_sdk.connectors.twilio.models.OutgoingCallerId] | Any`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

    `previous_page_uri: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`OutgoingCallerIdsListResultMeta(**data: Any)`
:   Metadata for outgoing_caller_ids.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

`OutgoingCallerIdsSearchData(**data: Any)`
:   Search result data for outgoing_caller_ids entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The account SID

    `date_created: str | None`
    :   When the outgoing caller ID was created

    `date_updated: str | None`
    :   When the outgoing caller ID was last updated

    `friendly_name: str | None`
    :   A friendly name

    `model_config`
    :   The type of the None singleton.

    `phone_number: str | None`
    :   The phone number

    `sid: str | None`
    :   The unique identifier

`Queue(**data: Any)`
:   A Twilio queue
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | Any | None`
    :   The type of the None singleton.

    `average_wait_time: int | Any | None`
    :   The type of the None singleton.

    `current_size: int | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_updated: str | Any | None`
    :   The type of the None singleton.

    `friendly_name: str | Any | None`
    :   The type of the None singleton.

    `max_size: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `sid: str | Any | None`
    :   The type of the None singleton.

    `subresource_uris: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`QueuesList(**data: Any)`
:   Paginated list of queues
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

    `previous_page_uri: str | Any | None`
    :   The type of the None singleton.

    `queues: list[airbyte_agent_sdk.connectors.twilio.models.Queue] | Any`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`QueuesListResultMeta(**data: Any)`
:   Metadata for queues.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

`QueuesSearchData(**data: Any)`
:   Search result data for queues entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The account SID that owns this queue

    `average_wait_time: int | None`
    :   Average wait time in seconds

    `current_size: int | None`
    :   Current number of callers waiting

    `date_created: str | None`
    :   When the queue was created

    `date_updated: str | None`
    :   When the queue was last updated

    `friendly_name: str | None`
    :   A friendly name for the queue

    `max_size: int | None`
    :   Maximum number of callers allowed

    `model_config`
    :   The type of the None singleton.

    `sid: str | None`
    :   The unique identifier for the queue

`Recording(**data: Any)`
:   A Twilio recording
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | Any | None`
    :   The type of the None singleton.

    `api_version: str | Any | None`
    :   The type of the None singleton.

    `call_sid: str | Any | None`
    :   The type of the None singleton.

    `channels: int | Any | None`
    :   The type of the None singleton.

    `conference_sid: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_updated: str | Any | None`
    :   The type of the None singleton.

    `duration: str | Any | None`
    :   The type of the None singleton.

    `encryption_details: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `error_code: str | Any | None`
    :   The type of the None singleton.

    `media_url: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `price: str | Any | None`
    :   The type of the None singleton.

    `price_unit: str | Any | None`
    :   The type of the None singleton.

    `sid: str | Any | None`
    :   The type of the None singleton.

    `source: str | Any | None`
    :   The type of the None singleton.

    `start_time: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `subresource_uris: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`RecordingsList(**data: Any)`
:   Paginated list of recordings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

    `previous_page_uri: str | Any | None`
    :   The type of the None singleton.

    `recordings: list[airbyte_agent_sdk.connectors.twilio.models.Recording] | Any`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`RecordingsListResultMeta(**data: Any)`
:   Metadata for recordings.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

`RecordingsSearchData(**data: Any)`
:   Search result data for recordings entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The account SID that owns the recording

    `call_sid: str | None`
    :   The SID of the associated call

    `channels: int | None`
    :   Number of audio channels

    `date_created: str | None`
    :   When the recording was created

    `duration: str | None`
    :   Duration in seconds

    `model_config`
    :   The type of the None singleton.

    `price: str | None`
    :   The cost of storing the recording

    `price_unit: str | None`
    :   The currency unit

    `sid: str | None`
    :   The unique identifier of the recording

    `start_time: str | None`
    :   When the recording started

    `status: str | None`
    :   The status of the recording

`Transcription(**data: Any)`
:   A Twilio transcription
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | Any | None`
    :   The type of the None singleton.

    `api_version: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_updated: str | Any | None`
    :   The type of the None singleton.

    `duration: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `price: str | Any | None`
    :   The type of the None singleton.

    `price_unit: str | Any | None`
    :   The type of the None singleton.

    `recording_sid: str | Any | None`
    :   The type of the None singleton.

    `sid: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `transcription_text: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`TranscriptionsList(**data: Any)`
:   Paginated list of transcriptions
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

    `previous_page_uri: str | Any | None`
    :   The type of the None singleton.

    `transcriptions: list[airbyte_agent_sdk.connectors.twilio.models.Transcription] | Any`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

`TranscriptionsListResultMeta(**data: Any)`
:   Metadata for transcriptions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

`TranscriptionsSearchData(**data: Any)`
:   Search result data for transcriptions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The account SID

    `date_created: str | None`
    :   When the transcription was created

    `date_updated: str | None`
    :   When the transcription was last updated

    `duration: str | None`
    :   Duration of the audio recording in seconds

    `model_config`
    :   The type of the None singleton.

    `price: str | None`
    :   The cost of the transcription

    `price_unit: str | None`
    :   The currency unit

    `recording_sid: str | None`
    :   The SID of the associated recording

    `sid: str | None`
    :   The unique identifier for the transcription

    `status: str | None`
    :   The status of the transcription

`TwilioAuthConfig(**data: Any)`
:   Twilio Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str`
    :   Your Twilio Account SID (starts with AC)

    `auth_token: str`
    :   Your Twilio Auth Token

    `model_config`
    :   The type of the None singleton.

`TwilioCheckResult(**data: Any)`
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

`TwilioExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

`TwilioExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Account], AccountsListResultMeta]
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Address], AddressesListResultMeta]
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Call], CallsListResultMeta]
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Conference], ConferencesListResultMeta]
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[IncomingPhoneNumber], IncomingPhoneNumbersListResultMeta]
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Message], MessagesListResultMeta]
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[OutgoingCallerId], OutgoingCallerIdsListResultMeta]
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Queue], QueuesListResultMeta]
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Recording], RecordingsListResultMeta]
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[Transcription], TranscriptionsListResultMeta]
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta[list[UsageRecord], UsageRecordsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`TwilioExecuteResultWithMeta[list[Account], AccountsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`AccountsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TwilioExecuteResultWithMeta[list[Address], AddressesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`AddressesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TwilioExecuteResultWithMeta[list[Call], CallsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`CallsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TwilioExecuteResultWithMeta[list[Conference], ConferencesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`ConferencesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TwilioExecuteResultWithMeta[list[IncomingPhoneNumber], IncomingPhoneNumbersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IncomingPhoneNumbersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TwilioExecuteResultWithMeta[list[Message], MessagesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`MessagesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TwilioExecuteResultWithMeta[list[OutgoingCallerId], OutgoingCallerIdsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`OutgoingCallerIdsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TwilioExecuteResultWithMeta[list[Queue], QueuesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`QueuesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TwilioExecuteResultWithMeta[list[Recording], RecordingsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`RecordingsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TwilioExecuteResultWithMeta[list[Transcription], TranscriptionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TranscriptionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TwilioExecuteResultWithMeta[list[UsageRecord], UsageRecordsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`UsageRecordsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.twilio.models.TwilioExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TwilioReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Twilio.
    
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

`UsageRecord(**data: Any)`
:   A Twilio usage record
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | Any | None`
    :   The type of the None singleton.

    `api_version: str | Any | None`
    :   The type of the None singleton.

    `as_of: str | Any | None`
    :   The type of the None singleton.

    `category: str | Any | None`
    :   The type of the None singleton.

    `count: str | Any | None`
    :   The type of the None singleton.

    `count_unit: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `end_date: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `price: str | Any | None`
    :   The type of the None singleton.

    `price_unit: str | Any | None`
    :   The type of the None singleton.

    `start_date: str | Any | None`
    :   The type of the None singleton.

    `subresource_uris: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

    `usage: str | Any | None`
    :   The type of the None singleton.

    `usage_unit: str | Any | None`
    :   The type of the None singleton.

`UsageRecordsList(**data: Any)`
:   Paginated list of usage records
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

    `previous_page_uri: str | Any | None`
    :   The type of the None singleton.

    `uri: str | Any | None`
    :   The type of the None singleton.

    `usage_records: list[airbyte_agent_sdk.connectors.twilio.models.UsageRecord] | Any`
    :   The type of the None singleton.

`UsageRecordsListResultMeta(**data: Any)`
:   Metadata for usage_records.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first_page_uri: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_uri: str | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

`UsageRecordsSearchData(**data: Any)`
:   Search result data for usage_records entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_sid: str | None`
    :   The account SID associated with this usage record

    `category: str | None`
    :   The usage category (calls, SMS, recordings, etc.)

    `count: str | None`
    :   The number of units consumed

    `count_unit: str | None`
    :   The unit of measurement for count

    `description: str | None`
    :   A description of the usage record

    `end_date: str | None`
    :   The end date of the usage period

    `model_config`
    :   The type of the None singleton.

    `price: str | None`
    :   The total price for consumed units

    `price_unit: str | None`
    :   The currency unit

    `start_date: str | None`
    :   The start date of the usage period

    `usage: str | None`
    :   The total usage value

    `usage_unit: str | None`
    :   The unit of measurement for usage