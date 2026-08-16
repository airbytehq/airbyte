---
id: airbyte_agent_sdk-connectors-monday-models
title: airbyte_agent_sdk.connectors.monday.models
---

Module airbyte_agent_sdk.connectors.monday.models
=================================================
Pydantic models for monday connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="ActivityLog"></a>

`ActivityLog(**data: Any)`
:   Monday.com activity log entry
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `data: str | None`
    :   The type of the None singleton.

    `entity: str | None`
    :   The type of the None singleton.

    `event: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_id: str | None`
    :   The type of the None singleton.

<a id="ActivityLogsSearchData"></a>

`ActivityLogsSearchData(**data: Any)`
:   Search result data for activity_logs entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `board_id: int | None`
    :   Board ID the activity belongs to

    `created_at: str | None`
    :   When the activity occurred

    `created_at_int: int | None`
    :   When the activity occurred (Unix timestamp)

    `data: str | None`
    :   Event data (JSON string)

    `entity: str | None`
    :   Entity type that was affected

    `event: str | None`
    :   Event type

    `id: str | None`
    :   Unique activity log identifier

    `model_config`
    :   The type of the None singleton.

    `pulse_id: int | None`
    :   Item (pulse) ID the activity belongs to

    `user_id: str | None`
    :   ID of the user who performed the action

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

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[ActivityLogsSearchData]
    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[BoardsSearchData]
    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[ItemsSearchData]
    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[TagsSearchData]
    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[TeamsSearchData]
    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[UpdatesSearchData]
    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[UsersSearchData]
    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[WorkspacesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.monday.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[ActivityLogsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ActivityLogsSearchResult"></a>

`ActivityLogsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[BoardsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BoardsSearchResult"></a>

`BoardsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ItemsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ItemsSearchResult"></a>

`ItemsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TagsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TagsSearchResult"></a>

`TagsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TeamsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TeamsSearchResult"></a>

`TeamsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UpdatesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UpdatesSearchResult"></a>

`UpdatesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UsersSearchResult"></a>

`UsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[WorkspacesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Board"></a>

`Board(**data: Any)`
:   Monday.com board object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `board_kind: str | None`
    :   The type of the None singleton.

    `columns: list[airbyte_agent_sdk.connectors.monday.models.BoardColumnsItem | None] | None`
    :   The type of the None singleton.

    `creator: airbyte_agent_sdk.connectors.monday.models.BoardCreator | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `groups: list[airbyte_agent_sdk.connectors.monday.models.BoardGroupsItem | None] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `owners: list[airbyte_agent_sdk.connectors.monday.models.BoardOwnersItem | None] | None`
    :   The type of the None singleton.

    `permissions: str | None`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

    `subscribers: list[airbyte_agent_sdk.connectors.monday.models.BoardSubscribersItem | None] | None`
    :   The type of the None singleton.

    `tags: list[airbyte_agent_sdk.connectors.monday.models.BoardTagsItem | None] | None`
    :   The type of the None singleton.

    `top_group: airbyte_agent_sdk.connectors.monday.models.BoardTopGroup | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `views: list[airbyte_agent_sdk.connectors.monday.models.BoardViewsItem | None] | None`
    :   The type of the None singleton.

    `workspace: airbyte_agent_sdk.connectors.monday.models.BoardWorkspace | None`
    :   The type of the None singleton.

<a id="BoardColumnsItem"></a>

`BoardColumnsItem(**data: Any)`
:   Nested schema for Board.columns_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `settings_str: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `width: int | None`
    :   The type of the None singleton.

<a id="BoardCreator"></a>

`BoardCreator(**data: Any)`
:   Board creator
    
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

<a id="BoardGroupsItem"></a>

`BoardGroupsItem(**data: Any)`
:   Nested schema for Board.groups_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `deleted: bool | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `position: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="BoardOwnersItem"></a>

`BoardOwnersItem(**data: Any)`
:   Nested schema for Board.owners_item
    
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

<a id="BoardSubscribersItem"></a>

`BoardSubscribersItem(**data: Any)`
:   Nested schema for Board.subscribers_item
    
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

<a id="BoardTagsItem"></a>

`BoardTagsItem(**data: Any)`
:   Nested schema for Board.tags_item
    
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

<a id="BoardTopGroup"></a>

`BoardTopGroup(**data: Any)`
:   Top group on the board
    
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

<a id="BoardViewsItem"></a>

`BoardViewsItem(**data: Any)`
:   Nested schema for Board.views_item
    
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

    `name: str | None`
    :   The type of the None singleton.

    `settings_str: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `view_specific_data_str: str | None`
    :   The type of the None singleton.

<a id="BoardWorkspace"></a>

`BoardWorkspace(**data: Any)`
:   Workspace the board belongs to
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

<a id="BoardsSearchData"></a>

`BoardsSearchData(**data: Any)`
:   Search result data for boards entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `board_kind: str | None`
    :   Board kind (public, private, share)

    `columns: list[typing.Any] | None`
    :   Board columns

    `communication: str | None`
    :   Board communication value

    `creator: dict[str, typing.Any] | None`
    :   Board creator

    `description: str | None`
    :   Board description

    `groups: list[typing.Any] | None`
    :   Board groups

    `id: str | None`
    :   Unique board identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Board name

    `owners: list[typing.Any] | None`
    :   Board owners

    `permissions: str | None`
    :   Board permissions

    `state: str | None`
    :   Board state (active, archived, deleted)

    `subscribers: list[typing.Any] | None`
    :   Board subscribers

    `tags: list[typing.Any] | None`
    :   Board tags

    `top_group: dict[str, typing.Any] | None`
    :   Top group on the board

    `type_: str | None`
    :   Board type

    `updated_at: str | None`
    :   When the board was last updated

    `updated_at_int: int | None`
    :   When the board was last updated (Unix timestamp)

    `updates: list[typing.Any] | None`
    :   Board updates

    `views: list[typing.Any] | None`
    :   Board views

    `workspace: dict[str, typing.Any] | None`
    :   Workspace the board belongs to

<a id="Item"></a>

`Item(**data: Any)`
:   Monday.com item object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `board: airbyte_agent_sdk.connectors.monday.models.ItemBoard | None`
    :   The type of the None singleton.

    `column_values: list[airbyte_agent_sdk.connectors.monday.models.ItemColumnValuesItem | None] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `creator_id: str | None`
    :   The type of the None singleton.

    `group: airbyte_agent_sdk.connectors.monday.models.ItemGroup | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `parent_item: airbyte_agent_sdk.connectors.monday.models.ItemParentItem | None`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

    `subscribers: list[airbyte_agent_sdk.connectors.monday.models.ItemSubscribersItem | None] | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="ItemBoard"></a>

`ItemBoard(**data: Any)`
:   Board the item belongs to
    
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

    `name: str | None`
    :   The type of the None singleton.

<a id="ItemColumnValuesItem"></a>

`ItemColumnValuesItem(**data: Any)`
:   Nested schema for Item.column_values_item
    
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

    `text: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="ItemGroup"></a>

`ItemGroup(**data: Any)`
:   Group the item belongs to
    
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

<a id="ItemParentItem"></a>

`ItemParentItem(**data: Any)`
:   Parent item (for subitems)
    
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

<a id="ItemSubscribersItem"></a>

`ItemSubscribersItem(**data: Any)`
:   Nested schema for Item.subscribers_item
    
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

<a id="ItemsSearchData"></a>

`ItemsSearchData(**data: Any)`
:   Search result data for items entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assets: list[typing.Any] | None`
    :   Files attached to the item

    `board: dict[str, typing.Any] | None`
    :   Board the item belongs to

    `column_values: list[typing.Any] | None`
    :   Item column values

    `created_at: str | None`
    :   When the item was created

    `creator_id: str | None`
    :   ID of the user who created the item

    `group: dict[str, typing.Any] | None`
    :   Group the item belongs to

    `id: str | None`
    :   Unique item identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Item name

    `parent_item: dict[str, typing.Any] | None`
    :   Parent item (for subitems)

    `state: str | None`
    :   Item state (active, archived, deleted)

    `subscribers: list[typing.Any] | None`
    :   Item subscribers

    `updated_at: str | None`
    :   When the item was last updated

    `updated_at_int: int | None`
    :   When the item was last updated (Unix timestamp)

    `updates: list[typing.Any] | None`
    :   Item updates

<a id="MondayApiTokenAuthenticationAuthConfig"></a>

`MondayApiTokenAuthenticationAuthConfig(**data: Any)`
:   API Token Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Monday.com personal API token

    `model_config`
    :   The type of the None singleton.

<a id="MondayCheckResult"></a>

`MondayCheckResult(**data: Any)`
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

<a id="MondayExecuteResult"></a>

`MondayExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[ActivityLog]]
    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[Board]]
    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[Item]]
    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[Tag]]
    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[Team]]
    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[Update]]
    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[User]]
    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[Workspace]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="MondayExecuteResultWithMeta"></a>

`MondayExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `meta: ~S | None`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`MondayExecuteResult[list[ActivityLog]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ActivityLogsListResult"></a>

`ActivityLogsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MondayExecuteResult[list[Board]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BoardsListResult"></a>

`BoardsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MondayExecuteResult[list[Item]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ItemsListResult"></a>

`ItemsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MondayExecuteResult[list[Tag]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TagsListResult"></a>

`TagsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MondayExecuteResult[list[Team]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TeamsListResult"></a>

`TeamsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MondayExecuteResult[list[Update]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UpdatesListResult"></a>

`UpdatesListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MondayExecuteResult[list[User]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UsersListResult"></a>

`UsersListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MondayExecuteResult[list[Workspace]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WorkspacesListResult"></a>

`WorkspacesListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MondayOauth20AuthenticationAuthConfig"></a>

`MondayOauth20AuthenticationAuthConfig(**data: Any)`
:   OAuth 2.0 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   Access token obtained via OAuth 2.0 flow

    `client_id: str`
    :   The Client ID of your Monday.com OAuth application

    `client_secret: str`
    :   The Client Secret of your Monday.com OAuth application

    `model_config`
    :   The type of the None singleton.

<a id="Tag"></a>

`Tag(**data: Any)`
:   Monday.com tag object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

<a id="TagsSearchData"></a>

`TagsSearchData(**data: Any)`
:   Search result data for tags entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   Tag color

    `id: str | None`
    :   Unique tag identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Tag name

<a id="Team"></a>

`Team(**data: Any)`
:   Monday.com team object
    
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

    `name: str | None`
    :   The type of the None singleton.

    `picture_url: str | None`
    :   The type of the None singleton.

    `users: list[airbyte_agent_sdk.connectors.monday.models.TeamUsersItem | None] | None`
    :   The type of the None singleton.

<a id="TeamUsersItem"></a>

`TeamUsersItem(**data: Any)`
:   Nested schema for Team.users_item
    
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

<a id="TeamsSearchData"></a>

`TeamsSearchData(**data: Any)`
:   Search result data for teams entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | None`
    :   Unique team identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Team name

    `picture_url: str | None`
    :   Team picture URL

    `users: list[typing.Any] | None`
    :   Team members

<a id="Update"></a>

`Update(**data: Any)`
:   Monday.com update (comment/post) object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assets: list[airbyte_agent_sdk.connectors.monday.models.UpdateAssetsItem | None] | None`
    :   The type of the None singleton.

    `body: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `creator_id: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `item_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `replies: list[airbyte_agent_sdk.connectors.monday.models.UpdateRepliesItem | None] | None`
    :   The type of the None singleton.

    `text_body: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="UpdateAssetsItem"></a>

`UpdateAssetsItem(**data: Any)`
:   Nested schema for Update.assets_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `file_extension: str | None`
    :   The type of the None singleton.

    `file_size: int | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `original_geometry: str | None`
    :   The type of the None singleton.

    `public_url: str | None`
    :   The type of the None singleton.

    `uploaded_by: airbyte_agent_sdk.connectors.monday.models.UpdateAssetsItemUploadedBy | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

    `url_thumbnail: str | None`
    :   The type of the None singleton.

<a id="UpdateAssetsItemUploadedBy"></a>

`UpdateAssetsItemUploadedBy(**data: Any)`
:   Nested schema for UpdateAssetsItem.uploaded_by
    
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

<a id="UpdateRepliesItem"></a>

`UpdateRepliesItem(**data: Any)`
:   Nested schema for Update.replies_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `creator_id: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text_body: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="UpdatesSearchData"></a>

`UpdatesSearchData(**data: Any)`
:   Search result data for updates entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assets: list[typing.Any] | None`
    :   Files attached to this update

    `body: str | None`
    :   Update body (HTML)

    `created_at: str | None`
    :   When the update was created

    `creator_id: str | None`
    :   ID of the user who created the update

    `id: str | None`
    :   Unique update identifier

    `item_id: str | None`
    :   ID of the item this update belongs to

    `model_config`
    :   The type of the None singleton.

    `replies: list[typing.Any] | None`
    :   Replies to this update

    `text_body: str | None`
    :   Update body (plain text)

    `updated_at: str | None`
    :   When the update was last modified

<a id="User"></a>

`User(**data: Any)`
:   Monday.com user object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `became_active_at: str | None`
    :   The type of the None singleton.

    `birthday: str | None`
    :   The type of the None singleton.

    `country_code: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `is_email_confirmed: bool | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `location: str | None`
    :   The type of the None singleton.

    `mobile_phone: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `phone: str | None`
    :   The type of the None singleton.

    `photo_url: airbyte_agent_sdk.connectors.monday.models.UserPhotoUrl | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `time_zone_identifier: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

    `utc_hours_diff: float | None`
    :   The type of the None singleton.

<a id="UserPhotoUrl"></a>

`UserPhotoUrl(**data: Any)`
:   Nested object containing photo URLs at various sizes. Replaces the legacy photo_* scalar fields removed in API 2026-10.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `original: str | None`
    :   URL to original size photo

    `small: str | None`
    :   URL to small photo

    `thumb: str | None`
    :   URL to thumbnail photo

    `thumb_small: str | None`
    :   URL to small thumbnail photo

    `tiny: str | None`
    :   URL to tiny photo

<a id="UsersSearchData"></a>

`UsersSearchData(**data: Any)`
:   Search result data for users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `birthday: str | None`
    :   User's birthday

    `country_code: str | None`
    :   User's country code

    `created_at: str | None`
    :   When the user was created

    `email: str | None`
    :   User's email address

    `id: str | None`
    :   Unique user identifier

    `location: str | None`
    :   User's location

    `mobile_phone: str | None`
    :   User's mobile phone number

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   User's display name

    `phone: str | None`
    :   User's phone number

    `time_zone_identifier: str | None`
    :   User's timezone identifier

    `title: str | None`
    :   User's job title

    `url: str | None`
    :   User's Monday.com profile URL

    `utc_hours_diff: float | None`
    :   UTC hours difference for the user's timezone (Float under API 2026-07)

<a id="Workspace"></a>

`Workspace(**data: Any)`
:   Monday.com workspace object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_product: airbyte_agent_sdk.connectors.monday.models.WorkspaceAccountProduct | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `owners_subscribers: list[airbyte_agent_sdk.connectors.monday.models.WorkspaceOwnersSubscribersItem | None] | None`
    :   The type of the None singleton.

    `settings: airbyte_agent_sdk.connectors.monday.models.WorkspaceSettings | None`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

    `team_owners_subscribers: list[airbyte_agent_sdk.connectors.monday.models.WorkspaceTeamOwnersSubscribersItem | None] | None`
    :   The type of the None singleton.

    `teams_subscribers: list[airbyte_agent_sdk.connectors.monday.models.WorkspaceTeamsSubscribersItem | None] | None`
    :   The type of the None singleton.

    `users_subscribers: list[airbyte_agent_sdk.connectors.monday.models.WorkspaceUsersSubscribersItem | None] | None`
    :   The type of the None singleton.

<a id="WorkspaceAccountProduct"></a>

`WorkspaceAccountProduct(**data: Any)`
:   Account product info
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="WorkspaceOwnersSubscribersItem"></a>

`WorkspaceOwnersSubscribersItem(**data: Any)`
:   Nested schema for Workspace.owners_subscribers_item
    
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

<a id="WorkspaceSettings"></a>

`WorkspaceSettings(**data: Any)`
:   Workspace settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `icon: airbyte_agent_sdk.connectors.monday.models.WorkspaceSettingsIcon | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="WorkspaceSettingsIcon"></a>

`WorkspaceSettingsIcon(**data: Any)`
:   Nested schema for WorkspaceSettings.icon
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `image: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="WorkspaceTeamOwnersSubscribersItem"></a>

`WorkspaceTeamOwnersSubscribersItem(**data: Any)`
:   Nested schema for Workspace.team_owners_subscribers_item
    
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

    `name: str | None`
    :   The type of the None singleton.

<a id="WorkspaceTeamsSubscribersItem"></a>

`WorkspaceTeamsSubscribersItem(**data: Any)`
:   Nested schema for Workspace.teams_subscribers_item
    
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

    `name: str | None`
    :   The type of the None singleton.

<a id="WorkspaceUsersSubscribersItem"></a>

`WorkspaceUsersSubscribersItem(**data: Any)`
:   Nested schema for Workspace.users_subscribers_item
    
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

    `account_product: dict[str, typing.Any] | None`
    :   Account product info

    `created_at: str | None`
    :   When the workspace was created

    `description: str | None`
    :   Workspace description

    `id: str | None`
    :   Unique workspace identifier

    `kind: str | None`
    :   Workspace kind (open, closed)

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Workspace name

    `owners_subscribers: list[typing.Any] | None`
    :   Owner subscribers

    `settings: dict[str, typing.Any] | None`
    :   Workspace settings

    `state: str | None`
    :   Workspace state

    `team_owners_subscribers: list[typing.Any] | None`
    :   Team owner subscribers

    `teams_subscribers: list[typing.Any] | None`
    :   Team subscribers

    `users_subscribers: list[typing.Any] | None`
    :   User subscribers