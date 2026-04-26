---
id: airbyte_agent_sdk-connectors-notion-models
title: airbyte_agent_sdk.connectors.notion.models
---

Module airbyte_agent_sdk.connectors.notion.models
=================================================
Pydantic models for notion connector.

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

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult[BlocksSearchData]
    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult[DataSourcesSearchData]
    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult[PagesSearchData]
    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.notion.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[BlocksSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BlocksSearchResult"></a>

`BlocksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[DataSourcesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DataSourcesSearchResult"></a>

`DataSourcesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[PagesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PagesSearchResult"></a>

`PagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Block"></a>

`Block(**data: Any)`
:   A Notion block object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any | None`
    :   The type of the None singleton.

    `bookmark: airbyte_agent_sdk.connectors.notion.models.BlockBookmark | Any | None`
    :   The type of the None singleton.

    `breadcrumb: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `bulleted_list_item: airbyte_agent_sdk.connectors.notion.models.BlockBulletedListItem | Any | None`
    :   The type of the None singleton.

    `callout: airbyte_agent_sdk.connectors.notion.models.BlockCallout | Any | None`
    :   The type of the None singleton.

    `child_database: airbyte_agent_sdk.connectors.notion.models.BlockChildDatabase | Any | None`
    :   The type of the None singleton.

    `child_page: airbyte_agent_sdk.connectors.notion.models.BlockChildPage | Any | None`
    :   The type of the None singleton.

    `code: airbyte_agent_sdk.connectors.notion.models.BlockCode | Any | None`
    :   The type of the None singleton.

    `column: airbyte_agent_sdk.connectors.notion.models.BlockColumn | Any | None`
    :   The type of the None singleton.

    `column_list: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `created_by: airbyte_agent_sdk.connectors.notion.models.BlockCreatedBy | Any | None`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `divider: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `embed: airbyte_agent_sdk.connectors.notion.models.BlockEmbed | Any | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockEquation | Any | None`
    :   The type of the None singleton.

    `file: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `has_children: bool | Any | None`
    :   The type of the None singleton.

    `heading_1: airbyte_agent_sdk.connectors.notion.models.BlockHeading1 | Any | None`
    :   The type of the None singleton.

    `heading_2: airbyte_agent_sdk.connectors.notion.models.BlockHeading2 | Any | None`
    :   The type of the None singleton.

    `heading_3: airbyte_agent_sdk.connectors.notion.models.BlockHeading3 | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `image: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `in_trash: bool | Any | None`
    :   The type of the None singleton.

    `last_edited_by: airbyte_agent_sdk.connectors.notion.models.BlockLastEditedBy | Any | None`
    :   The type of the None singleton.

    `last_edited_time: str | Any | None`
    :   The type of the None singleton.

    `link_preview: airbyte_agent_sdk.connectors.notion.models.BlockLinkPreview | Any | None`
    :   The type of the None singleton.

    `link_to_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `numbered_list_item: airbyte_agent_sdk.connectors.notion.models.BlockNumberedListItem | Any | None`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

    `paragraph: airbyte_agent_sdk.connectors.notion.models.BlockParagraph | Any | None`
    :   The type of the None singleton.

    `parent: Any`
    :   The type of the None singleton.

    `pdf: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `quote: airbyte_agent_sdk.connectors.notion.models.BlockQuote | Any | None`
    :   The type of the None singleton.

    `request_id: str | Any | None`
    :   The type of the None singleton.

    `synced_block: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `table: airbyte_agent_sdk.connectors.notion.models.BlockTable | Any | None`
    :   The type of the None singleton.

    `table_of_contents: airbyte_agent_sdk.connectors.notion.models.BlockTableOfContents | Any | None`
    :   The type of the None singleton.

    `table_row: airbyte_agent_sdk.connectors.notion.models.BlockTableRow | Any | None`
    :   The type of the None singleton.

    `template: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `to_do: airbyte_agent_sdk.connectors.notion.models.BlockToDo | Any | None`
    :   The type of the None singleton.

    `toggle: airbyte_agent_sdk.connectors.notion.models.BlockToggle | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `unsupported: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `video: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="BlockBookmark"></a>

`BlockBookmark(**data: Any)`
:   Bookmark block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `caption: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="BlockBulletedListItem"></a>

`BlockBulletedListItem(**data: Any)`
:   Bulleted list item content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

<a id="BlockCallout"></a>

`BlockCallout(**data: Any)`
:   Callout block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any | None`
    :   The type of the None singleton.

    `icon: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

<a id="BlockChildDatabase"></a>

`BlockChildDatabase(**data: Any)`
:   Child database block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

<a id="BlockChildPage"></a>

`BlockChildPage(**data: Any)`
:   Child page block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

<a id="BlockCode"></a>

`BlockCode(**data: Any)`
:   Code block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `caption: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

    `language: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

<a id="BlockColumn"></a>

`BlockColumn(**data: Any)`
:   Column block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `width_ratio: float | Any | None`
    :   The type of the None singleton.

<a id="BlockCreatedBy"></a>

`BlockCreatedBy(**data: Any)`
:   User who created the block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

<a id="BlockEmbed"></a>

`BlockEmbed(**data: Any)`
:   Embed block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="BlockEquation"></a>

`BlockEquation(**data: Any)`
:   Equation block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockHeading1"></a>

`BlockHeading1(**data: Any)`
:   Heading 1 block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any | None`
    :   The type of the None singleton.

    `is_toggleable: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

<a id="BlockHeading2"></a>

`BlockHeading2(**data: Any)`
:   Heading 2 block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any | None`
    :   The type of the None singleton.

    `is_toggleable: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

<a id="BlockHeading3"></a>

`BlockHeading3(**data: Any)`
:   Heading 3 block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any | None`
    :   The type of the None singleton.

    `is_toggleable: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

<a id="BlockLastEditedBy"></a>

`BlockLastEditedBy(**data: Any)`
:   User who last edited the block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

<a id="BlockLinkPreview"></a>

`BlockLinkPreview(**data: Any)`
:   Link preview block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="BlockNumberedListItem"></a>

`BlockNumberedListItem(**data: Any)`
:   Numbered list item content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

<a id="BlockParagraph"></a>

`BlockParagraph(**data: Any)`
:   Paragraph block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

<a id="BlockQuote"></a>

`BlockQuote(**data: Any)`
:   Quote block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

<a id="BlockTable"></a>

`BlockTable(**data: Any)`
:   Table block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_column_header: bool | Any | None`
    :   The type of the None singleton.

    `has_row_header: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `table_width: int | Any | None`
    :   The type of the None singleton.

<a id="BlockTableOfContents"></a>

`BlockTableOfContents(**data: Any)`
:   Table of contents block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockTableRow"></a>

`BlockTableRow(**data: Any)`
:   Table row block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cells: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockToDo"></a>

`BlockToDo(**data: Any)`
:   To-do block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checked: bool | Any | None`
    :   The type of the None singleton.

    `color: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

<a id="BlockToggle"></a>

`BlockToggle(**data: Any)`
:   Toggle block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

<a id="BlocksListResponse"></a>

`BlocksListResponse(**data: Any)`
:   Paginated list of blocks
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `block: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

    `request_id: str | Any | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.notion.models.Block] | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="BlocksListResultMeta"></a>

`BlocksListResultMeta(**data: Any)`
:   Metadata for blocks.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

<a id="BlocksSearchData"></a>

`BlocksSearchData(**data: Any)`
:   Search result data for blocks entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates if the block is archived or not.

    `bookmark: dict[str, typing.Any] | None`
    :   Represents a bookmark within the block

    `breadcrumb: dict[str, typing.Any] | None`
    :   Represents a breadcrumb block.

    `bulleted_list_item: dict[str, typing.Any] | None`
    :   Represents an item in a bulleted list.

    `callout: dict[str, typing.Any] | None`
    :   Describes a callout message or content in the block

    `child_database: dict[str, typing.Any] | None`
    :   Represents a child database block.

    `child_page: dict[str, typing.Any] | None`
    :   Represents a child page block.

    `code: dict[str, typing.Any] | None`
    :   Contains code snippets or blocks in the block content

    `column: dict[str, typing.Any] | None`
    :   Represents a column block.

    `column_list: dict[str, typing.Any] | None`
    :   Represents a list of columns.

    `created_by: dict[str, typing.Any] | None`
    :   The user who created the block.

    `created_time: str | None`
    :   The timestamp when the block was created.

    `divider: dict[str, typing.Any] | None`
    :   Represents a divider block.

    `embed: dict[str, typing.Any] | None`
    :   Contains embedded content such as videos, tweets, etc.

    `equation: dict[str, typing.Any] | None`
    :   Represents an equation or mathematical formula in the block

    `file: dict[str, typing.Any] | None`
    :   Represents a file block.

    `has_children: bool | None`
    :   Indicates if the block has children or not.

    `heading_1: dict[str, typing.Any] | None`
    :   Represents a level 1 heading.

    `heading_2: dict[str, typing.Any] | None`
    :   Represents a level 2 heading.

    `heading_3: dict[str, typing.Any] | None`
    :   Represents a level 3 heading.

    `id: str | None`
    :   The unique identifier of the block.

    `image: dict[str, typing.Any] | None`
    :   Represents an image block.

    `last_edited_by: dict[str, typing.Any] | None`
    :   The user who last edited the block.

    `last_edited_time: str | None`
    :   The timestamp when the block was last edited.

    `link_preview: dict[str, typing.Any] | None`
    :   Displays a preview of an external link within the block

    `link_to_page: dict[str, typing.Any] | None`
    :   Provides a link to another page within the block

    `model_config`
    :   The type of the None singleton.

    `numbered_list_item: dict[str, typing.Any] | None`
    :   Represents an item in a numbered list.

    `object_: dict[str, typing.Any] | None`
    :   Represents an object block.

    `paragraph: dict[str, typing.Any] | None`
    :   Represents a paragraph block.

    `parent: dict[str, typing.Any] | None`
    :   The parent block of the current block.

    `pdf: dict[str, typing.Any] | None`
    :   Represents a PDF document block.

    `quote: dict[str, typing.Any] | None`
    :   Represents a quote block.

    `synced_block: dict[str, typing.Any] | None`
    :   Represents a block synced from another source

    `table: dict[str, typing.Any] | None`
    :   Represents a table within the block

    `table_of_contents: dict[str, typing.Any] | None`
    :   Contains information regarding the table of contents

    `table_row: dict[str, typing.Any] | None`
    :   Represents a row in a table within the block

    `template: dict[str, typing.Any] | None`
    :   Specifies a template used within the block

    `to_do: dict[str, typing.Any] | None`
    :   Represents a to-do list or task content

    `toggle: dict[str, typing.Any] | None`
    :   Represents a toggle block.

    `type_: dict[str, typing.Any] | None`
    :   The type of the block.

    `unsupported: dict[str, typing.Any] | None`
    :   Represents an unsupported block.

    `video: dict[str, typing.Any] | None`
    :   Represents a video block.

<a id="Comment"></a>

`Comment(**data: Any)`
:   A Notion comment object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_by: airbyte_agent_sdk.connectors.notion.models.CommentCreatedBy | Any | None`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `discussion_id: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `last_edited_time: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

    `parent: Any`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

<a id="CommentCreatedBy"></a>

`CommentCreatedBy(**data: Any)`
:   User who created the comment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

<a id="CommentsListResponse"></a>

`CommentsListResponse(**data: Any)`
:   Paginated list of comments
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `comment: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

    `request_id: str | Any | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.notion.models.Comment] | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="CommentsListResultMeta"></a>

`CommentsListResultMeta(**data: Any)`
:   Metadata for comments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

<a id="DataSource"></a>

`DataSource(**data: Any)`
:   A Notion data source object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any | None`
    :   The type of the None singleton.

    `cover: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `created_by: airbyte_agent_sdk.connectors.notion.models.DataSourceCreatedBy | Any | None`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `database_parent: Any`
    :   The type of the None singleton.

    `description: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

    `icon: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `in_trash: bool | Any | None`
    :   The type of the None singleton.

    `is_archived: bool | Any | None`
    :   The type of the None singleton.

    `is_inline: bool | Any | None`
    :   The type of the None singleton.

    `is_locked: bool | Any | None`
    :   The type of the None singleton.

    `last_edited_by: airbyte_agent_sdk.connectors.notion.models.DataSourceLastEditedBy | Any | None`
    :   The type of the None singleton.

    `last_edited_time: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

    `parent: Any`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `public_url: str | Any | None`
    :   The type of the None singleton.

    `request_id: str | Any | None`
    :   The type of the None singleton.

    `title: list[airbyte_agent_sdk.connectors.notion.models.RichText] | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="DataSourceCreatedBy"></a>

`DataSourceCreatedBy(**data: Any)`
:   User who created the data source
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

<a id="DataSourceLastEditedBy"></a>

`DataSourceLastEditedBy(**data: Any)`
:   User who last edited the data source
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

<a id="DataSourcesListResponse"></a>

`DataSourcesListResponse(**data: Any)`
:   Paginated list of data sources
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

    `page_or_data_source: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `request_id: str | Any | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.notion.models.DataSource] | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="DataSourcesListResultMeta"></a>

`DataSourcesListResultMeta(**data: Any)`
:   Metadata for data_sources.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

<a id="DataSourcesSearchData"></a>

`DataSourcesSearchData(**data: Any)`
:   Search result data for data_sources entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates if the data source is archived or not.

    `cover: dict[str, typing.Any] | None`
    :   URL or reference to the cover image of the data source.

    `created_by: dict[str, typing.Any] | None`
    :   The user who created the data source.

    `created_time: str | None`
    :   The timestamp when the data source was created.

    `database_parent: dict[str, typing.Any] | None`
    :   The grandparent of the data source (parent of the database).

    `description: list[typing.Any] | None`
    :   Description text associated with the data source.

    `icon: dict[str, typing.Any] | None`
    :   URL or reference to the icon of the data source.

    `id: str | None`
    :   Unique identifier of the data source.

    `is_inline: bool | None`
    :   Indicates if the data source is displayed inline.

    `last_edited_by: dict[str, typing.Any] | None`
    :   The user who last edited the data source.

    `last_edited_time: str | None`
    :   The timestamp when the data source was last edited.

    `model_config`
    :   The type of the None singleton.

    `object_: dict[str, typing.Any] | None`
    :   The type of object (data_source).

    `parent: dict[str, typing.Any] | None`
    :   The parent database of the data source.

    `properties: list[typing.Any] | None`
    :   Schema of properties for the data source.

    `public_url: str | None`
    :   Public URL to access the data source.

    `title: list[typing.Any] | None`
    :   Title or name of the data source.

    `url: str | None`
    :   URL or reference to access the data source.

<a id="NotionAccessTokenAuthConfig"></a>

`NotionAccessTokenAuthConfig(**data: Any)`
:   Access Token
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `token: str`
    :   Notion internal integration token (starts with ntn_ or secret_)

<a id="NotionCheckResult"></a>

`NotionCheckResult(**data: Any)`
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

<a id="NotionExecuteResult"></a>

`NotionExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="NotionExecuteResultWithMeta"></a>

`NotionExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta[list[Block], BlocksListResultMeta]
    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta[list[Comment], CommentsListResultMeta]
    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta[list[DataSource], DataSourcesListResultMeta]
    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta[list[Page], PagesListResultMeta]
    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta[list[User], UsersListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`NotionExecuteResultWithMeta[list[Block], BlocksListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BlocksListResult"></a>

`BlocksListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`NotionExecuteResultWithMeta[list[Comment], CommentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CommentsListResult"></a>

`CommentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`NotionExecuteResultWithMeta[list[DataSource], DataSourcesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DataSourcesListResult"></a>

`DataSourcesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`NotionExecuteResultWithMeta[list[Page], PagesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PagesListResult"></a>

`PagesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`NotionExecuteResultWithMeta[list[User], UsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UsersListResult"></a>

`UsersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.notion.models.NotionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="NotionOAuthCredentials"></a>

`NotionOAuthCredentials(**data: Any)`
:   Notion OAuth App Credentials - Provide your own Notion OAuth app credentials to override the default Airbyte-managed ones.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   Your Notion OAuth integration's client ID

    `client_secret: str`
    :   Your Notion OAuth integration's client secret

    `model_config`
    :   The type of the None singleton.

<a id="NotionOauth20AuthConfig"></a>

`NotionOauth20AuthConfig(**data: Any)`
:   OAuth2.0
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   OAuth access token obtained through the Notion authorization flow

    `client_id: str`
    :   Your Notion OAuth integration's client ID

    `client_secret: str`
    :   Your Notion OAuth integration's client secret

    `model_config`
    :   The type of the None singleton.

<a id="Page"></a>

`Page(**data: Any)`
:   A Notion page object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any | None`
    :   The type of the None singleton.

    `cover: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `created_by: airbyte_agent_sdk.connectors.notion.models.PageCreatedBy | Any | None`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `icon: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `in_trash: bool | Any | None`
    :   The type of the None singleton.

    `is_archived: bool | Any | None`
    :   The type of the None singleton.

    `is_locked: bool | Any | None`
    :   The type of the None singleton.

    `last_edited_by: airbyte_agent_sdk.connectors.notion.models.PageLastEditedBy | Any | None`
    :   The type of the None singleton.

    `last_edited_time: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

    `parent: Any`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `public_url: str | Any | None`
    :   The type of the None singleton.

    `request_id: str | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="PageCreatedBy"></a>

`PageCreatedBy(**data: Any)`
:   User who created the page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

<a id="PageLastEditedBy"></a>

`PageLastEditedBy(**data: Any)`
:   User who last edited the page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

<a id="PagesListResponse"></a>

`PagesListResponse(**data: Any)`
:   Paginated list of pages
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

    `page_or_data_source: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `request_id: str | Any | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.notion.models.Page] | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="PagesListResultMeta"></a>

`PagesListResultMeta(**data: Any)`
:   Metadata for pages.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

<a id="PagesSearchData"></a>

`PagesSearchData(**data: Any)`
:   Search result data for pages entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the page is archived or not.

    `cover: dict[str, typing.Any] | None`
    :   URL or reference to the page cover image.

    `created_by: dict[str, typing.Any] | None`
    :   User ID or name of the creator of the page.

    `created_time: str | None`
    :   Date and time when the page was created.

    `icon: dict[str, typing.Any] | None`
    :   URL or reference to the page icon.

    `id: str | None`
    :   Unique identifier of the page.

    `in_trash: bool | None`
    :   Indicates whether the page is in trash or not.

    `last_edited_by: dict[str, typing.Any] | None`
    :   User ID or name of the last editor of the page.

    `last_edited_time: str | None`
    :   Date and time when the page was last edited.

    `model_config`
    :   The type of the None singleton.

    `object_: dict[str, typing.Any] | None`
    :   Type or category of the page object.

    `parent: dict[str, typing.Any] | None`
    :   ID or reference to the parent page.

    `properties: list[typing.Any] | None`
    :   Custom properties associated with the page.

    `public_url: str | None`
    :   Publicly accessible URL of the page.

    `url: str | None`
    :   URL of the page within the service.

<a id="Parent"></a>

`Parent(**data: Any)`
:   Parent object reference
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `block_id: str | Any | None`
    :   The type of the None singleton.

    `data_source_id: str | Any | None`
    :   The type of the None singleton.

    `database_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `page_id: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `workspace: bool | Any | None`
    :   The type of the None singleton.

<a id="RichText"></a>

`RichText(**data: Any)`
:   A rich text object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.RichTextAnnotations | Any | None`
    :   The type of the None singleton.

    `href: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `plain_text: str | Any | None`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.RichTextText | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="RichTextAnnotations"></a>

`RichTextAnnotations(**data: Any)`
:   Text annotations (bold, italic, etc.)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | Any | None`
    :   The type of the None singleton.

    `code: bool | Any | None`
    :   The type of the None singleton.

    `color: str | Any | None`
    :   The type of the None singleton.

    `italic: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | Any | None`
    :   The type of the None singleton.

    `underline: bool | Any | None`
    :   The type of the None singleton.

<a id="RichTextText"></a>

`RichTextText(**data: Any)`
:   Text content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | Any | None`
    :   Plain text content

    `link: dict[str, typing.Any] | Any | None`
    :   Link object

    `model_config`
    :   The type of the None singleton.

<a id="User"></a>

`User(**data: Any)`
:   A Notion user object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_url: str | Any | None`
    :   The type of the None singleton.

    `bot: airbyte_agent_sdk.connectors.notion.models.UserBot | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

    `person: airbyte_agent_sdk.connectors.notion.models.UserPerson | Any | None`
    :   The type of the None singleton.

    `request_id: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="UserBot"></a>

`UserBot(**data: Any)`
:   Bot-specific data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `owner: dict[str, typing.Any] | Any | None`
    :   Bot owner information

    `workspace_name: str | Any | None`
    :   Name of the workspace the bot belongs to

<a id="UserPerson"></a>

`UserPerson(**data: Any)`
:   Person-specific data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any | None`
    :   Person's email address

    `model_config`
    :   The type of the None singleton.

<a id="UsersListResponse"></a>

`UsersListResponse(**data: Any)`
:   Paginated list of users
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

    `object_: str | Any | None`
    :   The type of the None singleton.

    `request_id: str | Any | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.notion.models.User] | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `user: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="UsersListResultMeta"></a>

`UsersListResultMeta(**data: Any)`
:   Metadata for users.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

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

    `avatar_url: str | None`
    :   URL of the user's avatar

    `bot: dict[str, typing.Any] | None`
    :   Bot-specific data

    `id: str | None`
    :   Unique identifier for the user

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   User's display name

    `object_: dict[str, typing.Any] | None`
    :   Always user

    `person: dict[str, typing.Any] | None`
    :   Person-specific data

    `type_: dict[str, typing.Any] | None`
    :   Type of user (person or bot)