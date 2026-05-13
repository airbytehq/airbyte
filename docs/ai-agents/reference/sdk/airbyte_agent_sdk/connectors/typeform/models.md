---
id: airbyte_agent_sdk-connectors-typeform-models
title: airbyte_agent_sdk.connectors.typeform.models
---

Module airbyte_agent_sdk.connectors.typeform.models
===================================================
Pydantic models for typeform connector.

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

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[FormsSearchData]
    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[ImagesSearchData]
    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[ResponsesSearchData]
    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[ThemesSearchData]
    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[WebhooksSearchData]
    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[WorkspacesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[FormsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="FormsSearchResult"></a>

`FormsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ImagesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ImagesSearchResult"></a>

`ImagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ResponsesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ResponsesSearchResult"></a>

`ResponsesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ThemesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ThemesSearchResult"></a>

`ThemesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[WebhooksSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WebhooksSearchResult"></a>

`WebhooksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[WorkspacesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WorkspacesSearchResult"></a>

`WorkspacesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Form"></a>

`Form(**data: Any)`
:   A Typeform form with its fields, settings, and logic
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `fields: list[airbyte_agent_sdk.connectors.typeform.models.FormFieldsItem | None] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `last_updated_at: str | None`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.typeform.models.FormLinks | None`
    :   The type of the None singleton.

    `logic: list[airbyte_agent_sdk.connectors.typeform.models.FormLogicItem | None] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `published_at: str | None`
    :   The type of the None singleton.

    `self: airbyte_agent_sdk.connectors.typeform.models.FormSelf | None`
    :   The type of the None singleton.

    `settings: airbyte_agent_sdk.connectors.typeform.models.FormSettings | None`
    :   The type of the None singleton.

    `thankyou_screens: list[airbyte_agent_sdk.connectors.typeform.models.FormThankyouScreensItem | None] | None`
    :   The type of the None singleton.

    `theme: airbyte_agent_sdk.connectors.typeform.models.FormTheme | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `welcome_screens: list[airbyte_agent_sdk.connectors.typeform.models.FormWelcomeScreensItem | None] | None`
    :   The type of the None singleton.

    `workspace: airbyte_agent_sdk.connectors.typeform.models.FormWorkspace | None`
    :   The type of the None singleton.

<a id="FormFieldsItem"></a>

`FormFieldsItem(**data: Any)`
:   Nested schema for Form.fields_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachment: airbyte_agent_sdk.connectors.typeform.models.FormFieldsItemAttachment | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `layout: airbyte_agent_sdk.connectors.typeform.models.FormFieldsItemLayout | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.typeform.models.FormFieldsItemProperties | None`
    :   The type of the None singleton.

    `ref: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `validations: airbyte_agent_sdk.connectors.typeform.models.FormFieldsItemValidations | None`
    :   The type of the None singleton.

<a id="FormFieldsItemAttachment"></a>

`FormFieldsItemAttachment(**data: Any)`
:   Nested schema for FormFieldsItem.attachment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="FormFieldsItemLayout"></a>

`FormFieldsItemLayout(**data: Any)`
:   Nested schema for FormFieldsItem.layout
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachment: airbyte_agent_sdk.connectors.typeform.models.FormFieldsItemLayoutAttachment | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `placement: str | None`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.typeform.models.FormFieldsItemLayoutProperties | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="FormFieldsItemLayoutAttachment"></a>

`FormFieldsItemLayoutAttachment(**data: Any)`
:   Nested schema for FormFieldsItemLayout.attachment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `scale: float | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="FormFieldsItemLayoutProperties"></a>

`FormFieldsItemLayoutProperties(**data: Any)`
:   Nested schema for FormFieldsItemLayout.properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `brightness: float | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `focal_point: airbyte_agent_sdk.connectors.typeform.models.FormFieldsItemLayoutPropertiesFocalPoint | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FormFieldsItemLayoutPropertiesFocalPoint"></a>

`FormFieldsItemLayoutPropertiesFocalPoint(**data: Any)`
:   Nested schema for FormFieldsItemLayoutProperties.focal_point
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `x: float | None`
    :   The type of the None singleton.

    `y: float | None`
    :   The type of the None singleton.

<a id="FormFieldsItemProperties"></a>

`FormFieldsItemProperties(**data: Any)`
:   Nested schema for FormFieldsItem.properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allow_multiple_selection: bool | None`
    :   The type of the None singleton.

    `allow_other_choice: bool | None`
    :   The type of the None singleton.

    `choices: list[airbyte_agent_sdk.connectors.typeform.models.FormFieldsItemPropertiesChoicesItem | None] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `randomize: bool | None`
    :   The type of the None singleton.

    `vertical_alignment: bool | None`
    :   The type of the None singleton.

<a id="FormFieldsItemPropertiesChoicesItem"></a>

`FormFieldsItemPropertiesChoicesItem(**data: Any)`
:   Nested schema for FormFieldsItemProperties.choices_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `label: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ref: str | None`
    :   The type of the None singleton.

<a id="FormFieldsItemValidations"></a>

`FormFieldsItemValidations(**data: Any)`
:   Nested schema for FormFieldsItem.validations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `required: bool | None`
    :   The type of the None singleton.

<a id="FormLinks"></a>

`FormLinks(**data: Any)`
:   Links to related resources
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `display: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FormLogicItem"></a>

`FormLogicItem(**data: Any)`
:   Nested schema for Form.logic_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actions: list[airbyte_agent_sdk.connectors.typeform.models.FormLogicItemActionsItem | None] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ref: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="FormLogicItemActionsItem"></a>

`FormLogicItemActionsItem(**data: Any)`
:   Nested schema for FormLogicItem.actions_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action: str | None`
    :   The type of the None singleton.

    `condition: airbyte_agent_sdk.connectors.typeform.models.FormLogicItemActionsItemCondition | None`
    :   The type of the None singleton.

    `details: airbyte_agent_sdk.connectors.typeform.models.FormLogicItemActionsItemDetails | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FormLogicItemActionsItemCondition"></a>

`FormLogicItemActionsItemCondition(**data: Any)`
:   Nested schema for FormLogicItemActionsItem.condition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `op: str | None`
    :   The type of the None singleton.

    `vars: list[airbyte_agent_sdk.connectors.typeform.models.FormLogicItemActionsItemConditionVarsItem | None] | None`
    :   The type of the None singleton.

<a id="FormLogicItemActionsItemConditionVarsItem"></a>

`FormLogicItemActionsItemConditionVarsItem(**data: Any)`
:   Nested schema for FormLogicItemActionsItemCondition.vars_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="FormLogicItemActionsItemDetails"></a>

`FormLogicItemActionsItemDetails(**data: Any)`
:   Nested schema for FormLogicItemActionsItem.details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `target: airbyte_agent_sdk.connectors.typeform.models.FormLogicItemActionsItemDetailsTarget | None`
    :   The type of the None singleton.

    `to: airbyte_agent_sdk.connectors.typeform.models.FormLogicItemActionsItemDetailsTo | None`
    :   The type of the None singleton.

    `value: airbyte_agent_sdk.connectors.typeform.models.FormLogicItemActionsItemDetailsValue | None`
    :   The type of the None singleton.

<a id="FormLogicItemActionsItemDetailsTarget"></a>

`FormLogicItemActionsItemDetailsTarget(**data: Any)`
:   Nested schema for FormLogicItemActionsItemDetails.target
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="FormLogicItemActionsItemDetailsTo"></a>

`FormLogicItemActionsItemDetailsTo(**data: Any)`
:   Nested schema for FormLogicItemActionsItemDetails.to
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="FormLogicItemActionsItemDetailsValue"></a>

`FormLogicItemActionsItemDetailsValue(**data: Any)`
:   Nested schema for FormLogicItemActionsItemDetails.value
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="FormSelf"></a>

`FormSelf(**data: Any)`
:   Self-referential link to this form
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   URL of this form resource

    `model_config`
    :   The type of the None singleton.

<a id="FormSettings"></a>

`FormSettings(**data: Any)`
:   Settings and configurations for the form
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `are_uploads_public: bool | None`
    :   The type of the None singleton.

    `capabilities: airbyte_agent_sdk.connectors.typeform.models.FormSettingsCapabilities | None`
    :   The type of the None singleton.

    `cui_settings: airbyte_agent_sdk.connectors.typeform.models.FormSettingsCuiSettings | None`
    :   The type of the None singleton.

    `facebook_pixel: str | None`
    :   The type of the None singleton.

    `google_analytics: str | None`
    :   The type of the None singleton.

    `google_tag_manager: str | None`
    :   The type of the None singleton.

    `hide_navigation: bool | None`
    :   The type of the None singleton.

    `is_public: bool | None`
    :   The type of the None singleton.

    `is_trial: bool | None`
    :   The type of the None singleton.

    `language: str | None`
    :   Language of the form

    `meta: airbyte_agent_sdk.connectors.typeform.models.FormSettingsMeta | None`
    :   Meta information

    `model_config`
    :   The type of the None singleton.

    `notifications: airbyte_agent_sdk.connectors.typeform.models.FormSettingsNotifications | None`
    :   The type of the None singleton.

    `progress_bar: str | None`
    :   Progress bar settings

    `redirect_after_submit_url: str | None`
    :   The type of the None singleton.

    `show_progress_bar: bool | None`
    :   The type of the None singleton.

    `show_time_to_complete: bool | None`
    :   The type of the None singleton.

    `show_typeform_branding: bool | None`
    :   The type of the None singleton.

<a id="FormSettingsCapabilities"></a>

`FormSettingsCapabilities(**data: Any)`
:   Nested schema for FormSettings.capabilities
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `e2e_encryption: airbyte_agent_sdk.connectors.typeform.models.FormSettingsCapabilitiesE2eEncryption | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FormSettingsCapabilitiesE2eEncryption"></a>

`FormSettingsCapabilitiesE2eEncryption(**data: Any)`
:   Nested schema for FormSettingsCapabilities.e2e_encryption
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modifiable: bool | None`
    :   The type of the None singleton.

<a id="FormSettingsCuiSettings"></a>

`FormSettingsCuiSettings(**data: Any)`
:   Nested schema for FormSettings.cui_settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar: str | None`
    :   The type of the None singleton.

    `is_typing_emulation_disabled: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `typing_emulation_speed: str | None`
    :   The type of the None singleton.

<a id="FormSettingsMeta"></a>

`FormSettingsMeta(**data: Any)`
:   Meta information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allow_indexing: bool | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `image: airbyte_agent_sdk.connectors.typeform.models.FormSettingsMetaImage | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="FormSettingsMetaImage"></a>

`FormSettingsMetaImage(**data: Any)`
:   Nested schema for FormSettingsMeta.image
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FormSettingsNotifications"></a>

`FormSettingsNotifications(**data: Any)`
:   Nested schema for FormSettings.notifications
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `respondent: airbyte_agent_sdk.connectors.typeform.models.FormSettingsNotificationsRespondent | None`
    :   The type of the None singleton.

    `self: airbyte_agent_sdk.connectors.typeform.models.FormSettingsNotificationsSelf | None`
    :   The type of the None singleton.

<a id="FormSettingsNotificationsRespondent"></a>

`FormSettingsNotificationsRespondent(**data: Any)`
:   Nested schema for FormSettingsNotifications.respondent
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   The type of the None singleton.

    `message: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `recipients: list[str | None] | None`
    :   The type of the None singleton.

    `reply_to: str | None`
    :   The type of the None singleton.

    `subject: str | None`
    :   The type of the None singleton.

<a id="FormSettingsNotificationsSelf"></a>

`FormSettingsNotificationsSelf(**data: Any)`
:   Nested schema for FormSettingsNotifications.self
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   The type of the None singleton.

    `message: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `recipients: list[str | None] | None`
    :   The type of the None singleton.

    `reply_to: str | None`
    :   The type of the None singleton.

    `subject: str | None`
    :   The type of the None singleton.

<a id="FormThankyouScreensItem"></a>

`FormThankyouScreensItem(**data: Any)`
:   Nested schema for Form.thankyou_screens_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachment: airbyte_agent_sdk.connectors.typeform.models.FormThankyouScreensItemAttachment | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `layout: airbyte_agent_sdk.connectors.typeform.models.FormThankyouScreensItemLayout | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.typeform.models.FormThankyouScreensItemProperties | None`
    :   The type of the None singleton.

    `ref: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="FormThankyouScreensItemAttachment"></a>

`FormThankyouScreensItemAttachment(**data: Any)`
:   Nested schema for FormThankyouScreensItem.attachment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `placement: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="FormThankyouScreensItemLayout"></a>

`FormThankyouScreensItemLayout(**data: Any)`
:   Nested schema for FormThankyouScreensItem.layout
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachment: airbyte_agent_sdk.connectors.typeform.models.FormThankyouScreensItemLayoutAttachment | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `placement: str | None`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.typeform.models.FormThankyouScreensItemLayoutProperties | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="FormThankyouScreensItemLayoutAttachment"></a>

`FormThankyouScreensItemLayoutAttachment(**data: Any)`
:   Nested schema for FormThankyouScreensItemLayout.attachment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `scale: float | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="FormThankyouScreensItemLayoutProperties"></a>

`FormThankyouScreensItemLayoutProperties(**data: Any)`
:   Nested schema for FormThankyouScreensItemLayout.properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `brightness: float | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `focal_point: airbyte_agent_sdk.connectors.typeform.models.FormThankyouScreensItemLayoutPropertiesFocalPoint | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FormThankyouScreensItemLayoutPropertiesFocalPoint"></a>

`FormThankyouScreensItemLayoutPropertiesFocalPoint(**data: Any)`
:   Nested schema for FormThankyouScreensItemLayoutProperties.focal_point
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `x: float | None`
    :   The type of the None singleton.

    `y: float | None`
    :   The type of the None singleton.

<a id="FormThankyouScreensItemProperties"></a>

`FormThankyouScreensItemProperties(**data: Any)`
:   Nested schema for FormThankyouScreensItem.properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `button_mode: str | None`
    :   The type of the None singleton.

    `button_text: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `redirect_url: str | None`
    :   The type of the None singleton.

    `share_icons: bool | None`
    :   The type of the None singleton.

    `show_button: bool | None`
    :   The type of the None singleton.

<a id="FormTheme"></a>

`FormTheme(**data: Any)`
:   Theme settings for the form
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   URL of the theme

    `model_config`
    :   The type of the None singleton.

<a id="FormWelcomeScreensItem"></a>

`FormWelcomeScreensItem(**data: Any)`
:   Nested schema for Form.welcome_screens_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachment: airbyte_agent_sdk.connectors.typeform.models.FormWelcomeScreensItemAttachment | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `layout: airbyte_agent_sdk.connectors.typeform.models.FormWelcomeScreensItemLayout | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.typeform.models.FormWelcomeScreensItemProperties | None`
    :   The type of the None singleton.

    `ref: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="FormWelcomeScreensItemAttachment"></a>

`FormWelcomeScreensItemAttachment(**data: Any)`
:   Nested schema for FormWelcomeScreensItem.attachment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `placement: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="FormWelcomeScreensItemLayout"></a>

`FormWelcomeScreensItemLayout(**data: Any)`
:   Nested schema for FormWelcomeScreensItem.layout
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachment: airbyte_agent_sdk.connectors.typeform.models.FormWelcomeScreensItemLayoutAttachment | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `placement: str | None`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.typeform.models.FormWelcomeScreensItemLayoutProperties | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="FormWelcomeScreensItemLayoutAttachment"></a>

`FormWelcomeScreensItemLayoutAttachment(**data: Any)`
:   Nested schema for FormWelcomeScreensItemLayout.attachment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `scale: float | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="FormWelcomeScreensItemLayoutProperties"></a>

`FormWelcomeScreensItemLayoutProperties(**data: Any)`
:   Nested schema for FormWelcomeScreensItemLayout.properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `brightness: float | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `focal_point: airbyte_agent_sdk.connectors.typeform.models.FormWelcomeScreensItemLayoutPropertiesFocalPoint | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FormWelcomeScreensItemLayoutPropertiesFocalPoint"></a>

`FormWelcomeScreensItemLayoutPropertiesFocalPoint(**data: Any)`
:   Nested schema for FormWelcomeScreensItemLayoutProperties.focal_point
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `x: float | None`
    :   The type of the None singleton.

    `y: float | None`
    :   The type of the None singleton.

<a id="FormWelcomeScreensItemProperties"></a>

`FormWelcomeScreensItemProperties(**data: Any)`
:   Nested schema for FormWelcomeScreensItem.properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `button_mode: str | None`
    :   The type of the None singleton.

    `button_text: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `redirect_url: str | None`
    :   The type of the None singleton.

    `share_icons: bool | None`
    :   The type of the None singleton.

    `show_button: bool | None`
    :   The type of the None singleton.

<a id="FormWorkspace"></a>

`FormWorkspace(**data: Any)`
:   Workspace details where the form belongs
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   URL of the workspace

    `model_config`
    :   The type of the None singleton.

<a id="FormsList"></a>

`FormsList(**data: Any)`
:   Paginated list of forms
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `items: list[airbyte_agent_sdk.connectors.typeform.models.Form] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `page_count: int | None`
    :   The type of the None singleton.

    `total_items: int | None`
    :   The type of the None singleton.

<a id="FormsListResultMeta"></a>

`FormsListResultMeta(**data: Any)`
:   Metadata for forms.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_count: int | None`
    :   The type of the None singleton.

    `total_items: int | None`
    :   The type of the None singleton.

<a id="FormsSearchData"></a>

`FormsSearchData(**data: Any)`
:   Search result data for forms entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Date and time when the form was created

    `fields: list[typing.Any] | None`
    :   List of fields within the form

    `id: str | None`
    :   Unique identifier of the form

    `last_updated_at: str | None`
    :   Date and time when the form was last updated

    `links: dict[str, typing.Any] | None`
    :   Links to related resources

    `logic: list[typing.Any] | None`
    :   Logic rules or conditions applied to the form fields

    `model_config`
    :   The type of the None singleton.

    `published_at: str | None`
    :   Date and time when the form was published

    `settings: dict[str, typing.Any] | None`
    :   Settings and configurations for the form

    `thankyou_screens: list[typing.Any] | None`
    :   Thank you screen configurations

    `theme: dict[str, typing.Any] | None`
    :   Theme settings for the form

    `title: str | None`
    :   Title of the form

    `type_: str | None`
    :   Type of the form

    `welcome_screens: list[typing.Any] | None`
    :   Welcome screen configurations

    `workspace: dict[str, typing.Any] | None`
    :   Workspace details where the form belongs

<a id="Image"></a>

`Image(**data: Any)`
:   An image in the account
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avg_color: str | None`
    :   The type of the None singleton.

    `file_name: str | None`
    :   The type of the None singleton.

    `has_alpha: bool | None`
    :   The type of the None singleton.

    `height: int | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `media_type: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `src: str | None`
    :   The type of the None singleton.

    `upload_source: str | None`
    :   The type of the None singleton.

    `width: int | None`
    :   The type of the None singleton.

<a id="ImagesSearchData"></a>

`ImagesSearchData(**data: Any)`
:   Search result data for images entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avg_color: str | None`
    :   Average color of the image

    `file_name: str | None`
    :   Name of the image file

    `has_alpha: bool | None`
    :   Whether the image has an alpha channel

    `height: int | None`
    :   Height of the image in pixels

    `id: str | None`
    :   Unique identifier of the image

    `media_type: str | None`
    :   MIME type of the image

    `model_config`
    :   The type of the None singleton.

    `src: str | None`
    :   URL to access the image

    `width: int | None`
    :   Width of the image in pixels

<a id="Response"></a>

`Response(**data: Any)`
:   A single form response/submission
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answers: list[airbyte_agent_sdk.connectors.typeform.models.ResponseAnswersItem | None] | None`
    :   The type of the None singleton.

    `calculated: airbyte_agent_sdk.connectors.typeform.models.ResponseCalculated | None`
    :   The type of the None singleton.

    `form_id: str | None`
    :   The type of the None singleton.

    `hidden: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `landed_at: str | None`
    :   The type of the None singleton.

    `landing_id: str | None`
    :   The type of the None singleton.

    `metadata: airbyte_agent_sdk.connectors.typeform.models.ResponseMetadata | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `response_id: str | None`
    :   The type of the None singleton.

    `response_type: str | None`
    :   The type of the None singleton.

    `submitted_at: str | None`
    :   The type of the None singleton.

    `token: str | None`
    :   The type of the None singleton.

    `variables: list[airbyte_agent_sdk.connectors.typeform.models.ResponseVariablesItem | None] | None`
    :   The type of the None singleton.

<a id="ResponseAnswersItem"></a>

`ResponseAnswersItem(**data: Any)`
:   Nested schema for Response.answers_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `boolean: bool | None`
    :   The type of the None singleton.

    `choice: airbyte_agent_sdk.connectors.typeform.models.ResponseAnswersItemChoice | None`
    :   The type of the None singleton.

    `choices: airbyte_agent_sdk.connectors.typeform.models.ResponseAnswersItemChoices | None`
    :   The type of the None singleton.

    `date: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `field: airbyte_agent_sdk.connectors.typeform.models.ResponseAnswersItemField | None`
    :   The type of the None singleton.

    `file_url: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `number: float | None`
    :   The type of the None singleton.

    `payment: airbyte_agent_sdk.connectors.typeform.models.ResponseAnswersItemPayment | None`
    :   The type of the None singleton.

    `phone_number: str | None`
    :   The type of the None singleton.

    `text: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="ResponseAnswersItemChoice"></a>

`ResponseAnswersItemChoice(**data: Any)`
:   Nested schema for ResponseAnswersItem.choice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `label: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ResponseAnswersItemChoices"></a>

`ResponseAnswersItemChoices(**data: Any)`
:   Nested schema for ResponseAnswersItem.choices
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ids: list[str | None] | None`
    :   The type of the None singleton.

    `labels: list[str | None] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ResponseAnswersItemField"></a>

`ResponseAnswersItemField(**data: Any)`
:   Nested schema for ResponseAnswersItem.field
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ref: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="ResponseAnswersItemPayment"></a>

`ResponseAnswersItemPayment(**data: Any)`
:   Nested schema for ResponseAnswersItem.payment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   The type of the None singleton.

    `last4: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `success: bool | None`
    :   The type of the None singleton.

<a id="ResponseCalculated"></a>

`ResponseCalculated(**data: Any)`
:   Calculated data related to the response
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `score: int | None`
    :   The type of the None singleton.

<a id="ResponseMetadata"></a>

`ResponseMetadata(**data: Any)`
:   Metadata related to the response
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `network_id: str | None`
    :   The type of the None singleton.

    `platform: str | None`
    :   The type of the None singleton.

    `referer: str | None`
    :   The type of the None singleton.

    `user_agent: str | None`
    :   The type of the None singleton.

<a id="ResponseVariablesItem"></a>

`ResponseVariablesItem(**data: Any)`
:   Nested schema for Response.variables_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `key: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `number: float | None`
    :   The type of the None singleton.

    `text: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="ResponsesList"></a>

`ResponsesList(**data: Any)`
:   Paginated list of responses
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `items: list[airbyte_agent_sdk.connectors.typeform.models.Response] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `page_count: int | None`
    :   The type of the None singleton.

    `total_items: int | None`
    :   The type of the None singleton.

<a id="ResponsesListResultMeta"></a>

`ResponsesListResultMeta(**data: Any)`
:   Metadata for responses.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_count: int | None`
    :   The type of the None singleton.

    `total_items: int | None`
    :   The type of the None singleton.

<a id="ResponsesSearchData"></a>

`ResponsesSearchData(**data: Any)`
:   Search result data for responses entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answers: list[typing.Any] | None`
    :   Response data for each question in the form

    `calculated: dict[str, typing.Any] | None`
    :   Calculated data related to the response

    `form_id: str | None`
    :   ID of the form

    `hidden: dict[str, typing.Any] | None`
    :   Hidden fields in the response

    `landed_at: str | None`
    :   Timestamp when the respondent landed on the form

    `landing_id: str | None`
    :   ID of the landing page

    `metadata: dict[str, typing.Any] | None`
    :   Metadata related to the response

    `model_config`
    :   The type of the None singleton.

    `response_id: str | None`
    :   ID of the response

    `response_type: str | None`
    :   Type of the response

    `submitted_at: str | None`
    :   Timestamp when the response was submitted

    `token: str | None`
    :   Token associated with the response

    `variables: list[typing.Any] | None`
    :   Variables associated with the response

<a id="Theme"></a>

`Theme(**data: Any)`
:   A theme used for styling forms
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `background: airbyte_agent_sdk.connectors.typeform.models.ThemeBackground | None`
    :   The type of the None singleton.

    `colors: airbyte_agent_sdk.connectors.typeform.models.ThemeColors | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `fields: airbyte_agent_sdk.connectors.typeform.models.ThemeFields | None`
    :   The type of the None singleton.

    `font: str | None`
    :   The type of the None singleton.

    `has_transparent_button: bool | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `rounded_corners: str | None`
    :   The type of the None singleton.

    `screens: airbyte_agent_sdk.connectors.typeform.models.ThemeScreens | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `visibility: str | None`
    :   The type of the None singleton.

<a id="ThemeBackground"></a>

`ThemeBackground(**data: Any)`
:   Background settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `brightness: float | None`
    :   The type of the None singleton.

    `href: str | None`
    :   The type of the None singleton.

    `layout: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ThemeColors"></a>

`ThemeColors(**data: Any)`
:   Color settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answer: str | None`
    :   Color of answer text

    `background: str | None`
    :   Background color

    `button: str | None`
    :   Color of buttons

    `model_config`
    :   The type of the None singleton.

    `question: str | None`
    :   Color of question text

<a id="ThemeFields"></a>

`ThemeFields(**data: Any)`
:   Field display settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `alignment: str | None`
    :   The type of the None singleton.

    `font_size: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ThemeScreens"></a>

`ThemeScreens(**data: Any)`
:   Screen display settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `alignment: str | None`
    :   The type of the None singleton.

    `font_size: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ThemesList"></a>

`ThemesList(**data: Any)`
:   Paginated list of themes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `items: list[airbyte_agent_sdk.connectors.typeform.models.Theme] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `page_count: int | None`
    :   The type of the None singleton.

    `total_items: int | None`
    :   The type of the None singleton.

<a id="ThemesListResultMeta"></a>

`ThemesListResultMeta(**data: Any)`
:   Metadata for themes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_count: int | None`
    :   The type of the None singleton.

    `total_items: int | None`
    :   The type of the None singleton.

<a id="ThemesSearchData"></a>

`ThemesSearchData(**data: Any)`
:   Search result data for themes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `background: dict[str, typing.Any] | None`
    :   Background settings for the theme

    `colors: dict[str, typing.Any] | None`
    :   Color settings

    `created_at: str | None`
    :   Timestamp when the theme was created

    `fields: dict[str, typing.Any] | None`
    :   Field display settings

    `font: str | None`
    :   Font used in the theme

    `has_transparent_button: bool | None`
    :   Whether the theme has a transparent button

    `id: str | None`
    :   Unique identifier of the theme

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the theme

    `rounded_corners: str | None`
    :   Rounded corners setting

    `screens: dict[str, typing.Any] | None`
    :   Screen display settings

    `updated_at: str | None`
    :   Timestamp when the theme was last updated

    `visibility: str | None`
    :   Visibility setting of the theme

<a id="TypeformAuthConfig"></a>

`TypeformAuthConfig(**data: Any)`
:   Access Token Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   Personal access token from your Typeform account settings

    `model_config`
    :   The type of the None singleton.

<a id="TypeformCheckResult"></a>

`TypeformCheckResult(**data: Any)`
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

<a id="TypeformExecuteResult"></a>

`TypeformExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult[list[Image]]
    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult[list[Webhook]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="TypeformExecuteResultWithMeta"></a>

`TypeformExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta[list[Form], FormsListResultMeta]
    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta[list[Response], ResponsesListResultMeta]
    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta[list[Theme], ThemesListResultMeta]
    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta[list[Workspace], WorkspacesListResultMeta]

    ### Class variables

    `meta: ~S | None`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`TypeformExecuteResultWithMeta[list[Form], FormsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="FormsListResult"></a>

`FormsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TypeformExecuteResultWithMeta[list[Response], ResponsesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ResponsesListResult"></a>

`ResponsesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TypeformExecuteResultWithMeta[list[Theme], ThemesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ThemesListResult"></a>

`ThemesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TypeformExecuteResultWithMeta[list[Workspace], WorkspacesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WorkspacesListResult"></a>

`WorkspacesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TypeformExecuteResult[list[Image]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ImagesListResult"></a>

`ImagesListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TypeformExecuteResult[list[Webhook]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WebhooksListResult"></a>

`WebhooksListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TypeformReplicationConfig"></a>

`TypeformReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Typeform
    
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
    :   UTC date and time in the format YYYY-MM-DDT00:00:00Z from which to start replicating response data.

<a id="Webhook"></a>

`Webhook(**data: Any)`
:   A webhook configured for a form
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `enabled: bool | None`
    :   The type of the None singleton.

    `form_id: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `tag: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

    `verify_ssl: bool | None`
    :   The type of the None singleton.

<a id="WebhooksList"></a>

`WebhooksList(**data: Any)`
:   List of webhooks
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `items: list[airbyte_agent_sdk.connectors.typeform.models.Webhook] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="WebhooksSearchData"></a>

`WebhooksSearchData(**data: Any)`
:   Search result data for webhooks entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the webhook was created

    `enabled: bool | None`
    :   Whether the webhook is currently enabled

    `form_id: str | None`
    :   ID of the form associated with the webhook

    `id: str | None`
    :   Unique identifier of the webhook

    `model_config`
    :   The type of the None singleton.

    `tag: str | None`
    :   Tag to categorize or label the webhook

    `updated_at: str | None`
    :   Timestamp when the webhook was last updated

    `url: str | None`
    :   URL where webhook data is sent

    `verify_ssl: bool | None`
    :   Whether SSL verification is enforced

<a id="Workspace"></a>

`Workspace(**data: Any)`
:   A workspace containing forms
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   The type of the None singleton.

    `default: bool | None`
    :   The type of the None singleton.

    `forms: airbyte_agent_sdk.connectors.typeform.models.WorkspaceForms | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `self: airbyte_agent_sdk.connectors.typeform.models.WorkspaceSelf | None`
    :   The type of the None singleton.

    `shared: bool | None`
    :   The type of the None singleton.

<a id="WorkspaceForms"></a>

`WorkspaceForms(**data: Any)`
:   Information about forms in the workspace
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: float | None`
    :   Total number of forms in this workspace

    `href: str | None`
    :   URL to retrieve the forms

    `model_config`
    :   The type of the None singleton.

<a id="WorkspaceSelf"></a>

`WorkspaceSelf(**data: Any)`
:   Self-referential link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   URL to this workspace

    `model_config`
    :   The type of the None singleton.

<a id="WorkspacesList"></a>

`WorkspacesList(**data: Any)`
:   Paginated list of workspaces
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `items: list[airbyte_agent_sdk.connectors.typeform.models.Workspace] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `page_count: int | None`
    :   The type of the None singleton.

    `total_items: int | None`
    :   The type of the None singleton.

<a id="WorkspacesListResultMeta"></a>

`WorkspacesListResultMeta(**data: Any)`
:   Metadata for workspaces.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_count: int | None`
    :   The type of the None singleton.

    `total_items: int | None`
    :   The type of the None singleton.

<a id="WorkspacesSearchData"></a>

`WorkspacesSearchData(**data: Any)`
:   Search result data for workspaces entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   Account ID associated with the workspace

    `default: bool | None`
    :   Whether this is the default workspace

    `forms: dict[str, typing.Any] | None`
    :   Information about forms in the workspace

    `id: str | None`
    :   Unique identifier of the workspace

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the workspace

    `self: dict[str, typing.Any] | None`
    :   Self-referential link

    `shared: bool | None`
    :   Whether this workspace is shared