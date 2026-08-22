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
    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult[CommentsSearchData]
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

`AirbyteSearchResult[CommentsSearchData](**data: Any)`
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

<a id="CommentsSearchResult"></a>

`CommentsSearchResult(**data: Any)`
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

    `archived: bool | None`
    :   The type of the None singleton.

    `bookmark: airbyte_agent_sdk.connectors.notion.models.BlockBookmark | None`
    :   The type of the None singleton.

    `breadcrumb: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `bulleted_list_item: airbyte_agent_sdk.connectors.notion.models.BlockBulletedListItem | None`
    :   The type of the None singleton.

    `callout: airbyte_agent_sdk.connectors.notion.models.BlockCallout | None`
    :   The type of the None singleton.

    `child_database: airbyte_agent_sdk.connectors.notion.models.BlockChildDatabase | None`
    :   The type of the None singleton.

    `child_page: airbyte_agent_sdk.connectors.notion.models.BlockChildPage | None`
    :   The type of the None singleton.

    `code: airbyte_agent_sdk.connectors.notion.models.BlockCode | None`
    :   The type of the None singleton.

    `column: airbyte_agent_sdk.connectors.notion.models.BlockColumn | None`
    :   The type of the None singleton.

    `column_list: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_by: airbyte_agent_sdk.connectors.notion.models.BlockCreatedBy | None`
    :   The type of the None singleton.

    `created_time: str | None`
    :   The type of the None singleton.

    `divider: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `embed: airbyte_agent_sdk.connectors.notion.models.BlockEmbed | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockEquation | None`
    :   The type of the None singleton.

    `file: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `has_children: bool | None`
    :   The type of the None singleton.

    `heading_1: airbyte_agent_sdk.connectors.notion.models.BlockHeading1 | None`
    :   The type of the None singleton.

    `heading_2: airbyte_agent_sdk.connectors.notion.models.BlockHeading2 | None`
    :   The type of the None singleton.

    `heading_3: airbyte_agent_sdk.connectors.notion.models.BlockHeading3 | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `image: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `in_trash: bool | None`
    :   The type of the None singleton.

    `last_edited_by: airbyte_agent_sdk.connectors.notion.models.BlockLastEditedBy | None`
    :   The type of the None singleton.

    `last_edited_time: str | None`
    :   The type of the None singleton.

    `link_preview: airbyte_agent_sdk.connectors.notion.models.BlockLinkPreview | None`
    :   The type of the None singleton.

    `link_to_page: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `numbered_list_item: airbyte_agent_sdk.connectors.notion.models.BlockNumberedListItem | None`
    :   The type of the None singleton.

    `object_: str | None`
    :   The type of the None singleton.

    `paragraph: airbyte_agent_sdk.connectors.notion.models.BlockParagraph | None`
    :   The type of the None singleton.

    `parent: typing.Any | None`
    :   The type of the None singleton.

    `pdf: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `quote: airbyte_agent_sdk.connectors.notion.models.BlockQuote | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `synced_block: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `table: airbyte_agent_sdk.connectors.notion.models.BlockTable | None`
    :   The type of the None singleton.

    `table_of_contents: airbyte_agent_sdk.connectors.notion.models.BlockTableOfContents | None`
    :   The type of the None singleton.

    `table_row: airbyte_agent_sdk.connectors.notion.models.BlockTableRow | None`
    :   The type of the None singleton.

    `template: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `to_do: airbyte_agent_sdk.connectors.notion.models.BlockToDo | None`
    :   The type of the None singleton.

    `toggle: airbyte_agent_sdk.connectors.notion.models.BlockToggle | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `unsupported: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `video: dict[str, typing.Any] | None`
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

    `caption: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
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

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
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

    `color: str | None`
    :   The type of the None singleton.

    `icon: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
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

    `title: str | None`
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

    `title: str | None`
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

    `caption: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
    :   The type of the None singleton.

    `language: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
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

    `width_ratio: float | None`
    :   The type of the None singleton.

<a id="BlockCreateParams"></a>

`BlockCreateParams(**data: Any)`
:   Parameters for appending child blocks to a parent block or page. The block_id path parameter specifies the parent.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `children: list[airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItem]`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItem"></a>

`BlockCreateParamsChildrenItem(**data: Any)`
:   A block object. Set type to the block kind and include matching content.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `audio: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemAudio | None`
    :   Media file. Use external URL or file upload.

    `bookmark: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemBookmark | None`
    :   Bookmark block

    `bulleted_list_item: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemBulletedListItem | None`
    :   Bulleted list item content

    `callout: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemCallout | None`
    :   Callout block content

    `code: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemCode | None`
    :   Code block content

    `divider: dict[str, typing.Any] | None`
    :   Divider block (empty object)

    `embed: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemEmbed | None`
    :   Embed block

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemEquation | None`
    :   Equation block

    `file: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemFile | None`
    :   Media file. Use external URL or file upload.

    `heading_1: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading1 | None`
    :   Heading 1 block content

    `heading_2: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading2 | None`
    :   Heading 2 block content

    `heading_3: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading3 | None`
    :   Heading 3 block content

    `image: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemImage | None`
    :   Media file. Use external URL or file upload.

    `model_config`
    :   The type of the None singleton.

    `numbered_list_item: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemNumberedListItem | None`
    :   Numbered list item content

    `paragraph: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemParagraph | None`
    :   Paragraph block content

    `pdf: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemPdf | None`
    :   Media file. Use external URL or file upload.

    `quote: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemQuote | None`
    :   Quote block content

    `table_of_contents: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemTableOfContents | None`
    :   Table of contents block

    `to_do: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemToDo | None`
    :   To-do block content

    `toggle: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemToggle | None`
    :   Toggle block content

    `type_: str | None`
    :   Block type: paragraph, heading_1, heading_2, heading_3, bulleted_list_item, numbered_list_item, to_do, toggle, code, quote, callout, divider, bookmark, embed, equation, table_of_contents, image, video, file, pdf, audio, column_list, column, table, synced_block, link_to_page, etc.

    `video: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemVideo | None`
    :   Media file. Use external URL or file upload.

<a id="BlockCreateParamsChildrenItemAudio"></a>

`BlockCreateParamsChildrenItemAudio(**data: Any)`
:   Media file. Use external URL or file upload.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemAudioExternal | None`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemAudioFileUpload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   File type: external or file_upload

<a id="BlockCreateParamsChildrenItemAudioExternal"></a>

`BlockCreateParamsChildrenItemAudioExternal(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemAudio.external
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemAudioFileUpload"></a>

`BlockCreateParamsChildrenItemAudioFileUpload(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemAudio.file_upload
    
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

<a id="BlockCreateParamsChildrenItemBookmark"></a>

`BlockCreateParamsChildrenItemBookmark(**data: Any)`
:   Bookmark block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `caption: list[airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemBookmarkCaptionItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   URL to bookmark

<a id="BlockCreateParamsChildrenItemBookmarkCaptionItem"></a>

`BlockCreateParamsChildrenItemBookmarkCaptionItem(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemBookmark.caption_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemBookmarkCaptionItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemBookmarkCaptionItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemBookmarkCaptionItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemBookmarkCaptionItemAnnotations"></a>

`BlockCreateParamsChildrenItemBookmarkCaptionItemAnnotations(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemBookmarkCaptionItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemBookmarkCaptionItemEquation"></a>

`BlockCreateParamsChildrenItemBookmarkCaptionItemEquation(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemBookmarkCaptionItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemBookmarkCaptionItemText"></a>

`BlockCreateParamsChildrenItemBookmarkCaptionItemText(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemBookmarkCaptionItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemBookmarkCaptionItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemBookmarkCaptionItemTextLink"></a>

`BlockCreateParamsChildrenItemBookmarkCaptionItemTextLink(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemBookmarkCaptionItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemBulletedListItem"></a>

`BlockCreateParamsChildrenItemBulletedListItem(**data: Any)`
:   Bulleted list item content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemBulletedListItemRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemBulletedListItemRichTextItem"></a>

`BlockCreateParamsChildrenItemBulletedListItemRichTextItem(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemBulletedListItem.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemBulletedListItemRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemBulletedListItemRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemBulletedListItemRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemBulletedListItemRichTextItemAnnotations"></a>

`BlockCreateParamsChildrenItemBulletedListItemRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemBulletedListItemRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemBulletedListItemRichTextItemEquation"></a>

`BlockCreateParamsChildrenItemBulletedListItemRichTextItemEquation(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemBulletedListItemRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemBulletedListItemRichTextItemText"></a>

`BlockCreateParamsChildrenItemBulletedListItemRichTextItemText(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemBulletedListItemRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemBulletedListItemRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemBulletedListItemRichTextItemTextLink"></a>

`BlockCreateParamsChildrenItemBulletedListItemRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemBulletedListItemRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemCallout"></a>

`BlockCreateParamsChildrenItemCallout(**data: Any)`
:   Callout block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `icon: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemCalloutRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemCalloutRichTextItem"></a>

`BlockCreateParamsChildrenItemCalloutRichTextItem(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemCallout.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemCalloutRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemCalloutRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemCalloutRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemCalloutRichTextItemAnnotations"></a>

`BlockCreateParamsChildrenItemCalloutRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemCalloutRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemCalloutRichTextItemEquation"></a>

`BlockCreateParamsChildrenItemCalloutRichTextItemEquation(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemCalloutRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemCalloutRichTextItemText"></a>

`BlockCreateParamsChildrenItemCalloutRichTextItemText(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemCalloutRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemCalloutRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemCalloutRichTextItemTextLink"></a>

`BlockCreateParamsChildrenItemCalloutRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemCalloutRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemCode"></a>

`BlockCreateParamsChildrenItemCode(**data: Any)`
:   Code block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `language: str | None`
    :   Programming language for syntax highlighting

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemCodeRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemCodeRichTextItem"></a>

`BlockCreateParamsChildrenItemCodeRichTextItem(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemCode.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemCodeRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemCodeRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemCodeRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemCodeRichTextItemAnnotations"></a>

`BlockCreateParamsChildrenItemCodeRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemCodeRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemCodeRichTextItemEquation"></a>

`BlockCreateParamsChildrenItemCodeRichTextItemEquation(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemCodeRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemCodeRichTextItemText"></a>

`BlockCreateParamsChildrenItemCodeRichTextItemText(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemCodeRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemCodeRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemCodeRichTextItemTextLink"></a>

`BlockCreateParamsChildrenItemCodeRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemCodeRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemEmbed"></a>

`BlockCreateParamsChildrenItemEmbed(**data: Any)`
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

    `url: str | None`
    :   URL to embed

<a id="BlockCreateParamsChildrenItemEquation"></a>

`BlockCreateParamsChildrenItemEquation(**data: Any)`
:   Equation block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   LaTeX expression

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemFile"></a>

`BlockCreateParamsChildrenItemFile(**data: Any)`
:   Media file. Use external URL or file upload.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemFileExternal | None`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemFileFileUpload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   File type: external or file_upload

<a id="BlockCreateParamsChildrenItemFileExternal"></a>

`BlockCreateParamsChildrenItemFileExternal(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemFile.external
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemFileFileUpload"></a>

`BlockCreateParamsChildrenItemFileFileUpload(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemFile.file_upload
    
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

<a id="BlockCreateParamsChildrenItemHeading1"></a>

`BlockCreateParamsChildrenItemHeading1(**data: Any)`
:   Heading 1 block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `is_toggleable: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading1RichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading1RichTextItem"></a>

`BlockCreateParamsChildrenItemHeading1RichTextItem(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading1.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading1RichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading1RichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading1RichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading1RichTextItemAnnotations"></a>

`BlockCreateParamsChildrenItemHeading1RichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading1RichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading1RichTextItemEquation"></a>

`BlockCreateParamsChildrenItemHeading1RichTextItemEquation(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading1RichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading1RichTextItemText"></a>

`BlockCreateParamsChildrenItemHeading1RichTextItemText(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading1RichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading1RichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading1RichTextItemTextLink"></a>

`BlockCreateParamsChildrenItemHeading1RichTextItemTextLink(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading1RichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading2"></a>

`BlockCreateParamsChildrenItemHeading2(**data: Any)`
:   Heading 2 block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `is_toggleable: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading2RichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading2RichTextItem"></a>

`BlockCreateParamsChildrenItemHeading2RichTextItem(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading2.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading2RichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading2RichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading2RichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading2RichTextItemAnnotations"></a>

`BlockCreateParamsChildrenItemHeading2RichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading2RichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading2RichTextItemEquation"></a>

`BlockCreateParamsChildrenItemHeading2RichTextItemEquation(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading2RichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading2RichTextItemText"></a>

`BlockCreateParamsChildrenItemHeading2RichTextItemText(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading2RichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading2RichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading2RichTextItemTextLink"></a>

`BlockCreateParamsChildrenItemHeading2RichTextItemTextLink(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading2RichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading3"></a>

`BlockCreateParamsChildrenItemHeading3(**data: Any)`
:   Heading 3 block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `is_toggleable: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading3RichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading3RichTextItem"></a>

`BlockCreateParamsChildrenItemHeading3RichTextItem(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading3.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading3RichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading3RichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading3RichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading3RichTextItemAnnotations"></a>

`BlockCreateParamsChildrenItemHeading3RichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading3RichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading3RichTextItemEquation"></a>

`BlockCreateParamsChildrenItemHeading3RichTextItemEquation(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading3RichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading3RichTextItemText"></a>

`BlockCreateParamsChildrenItemHeading3RichTextItemText(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading3RichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemHeading3RichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemHeading3RichTextItemTextLink"></a>

`BlockCreateParamsChildrenItemHeading3RichTextItemTextLink(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemHeading3RichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemImage"></a>

`BlockCreateParamsChildrenItemImage(**data: Any)`
:   Media file. Use external URL or file upload.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemImageExternal | None`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemImageFileUpload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   File type: external or file_upload

<a id="BlockCreateParamsChildrenItemImageExternal"></a>

`BlockCreateParamsChildrenItemImageExternal(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemImage.external
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemImageFileUpload"></a>

`BlockCreateParamsChildrenItemImageFileUpload(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemImage.file_upload
    
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

<a id="BlockCreateParamsChildrenItemNumberedListItem"></a>

`BlockCreateParamsChildrenItemNumberedListItem(**data: Any)`
:   Numbered list item content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemNumberedListItemRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemNumberedListItemRichTextItem"></a>

`BlockCreateParamsChildrenItemNumberedListItemRichTextItem(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemNumberedListItem.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemNumberedListItemRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemNumberedListItemRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemNumberedListItemRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemNumberedListItemRichTextItemAnnotations"></a>

`BlockCreateParamsChildrenItemNumberedListItemRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemNumberedListItemRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemNumberedListItemRichTextItemEquation"></a>

`BlockCreateParamsChildrenItemNumberedListItemRichTextItemEquation(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemNumberedListItemRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemNumberedListItemRichTextItemText"></a>

`BlockCreateParamsChildrenItemNumberedListItemRichTextItemText(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemNumberedListItemRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemNumberedListItemRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemNumberedListItemRichTextItemTextLink"></a>

`BlockCreateParamsChildrenItemNumberedListItemRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemNumberedListItemRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemParagraph"></a>

`BlockCreateParamsChildrenItemParagraph(**data: Any)`
:   Paragraph block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemParagraphRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemParagraphRichTextItem"></a>

`BlockCreateParamsChildrenItemParagraphRichTextItem(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemParagraph.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemParagraphRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemParagraphRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemParagraphRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemParagraphRichTextItemAnnotations"></a>

`BlockCreateParamsChildrenItemParagraphRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemParagraphRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemParagraphRichTextItemEquation"></a>

`BlockCreateParamsChildrenItemParagraphRichTextItemEquation(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemParagraphRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemParagraphRichTextItemText"></a>

`BlockCreateParamsChildrenItemParagraphRichTextItemText(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemParagraphRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemParagraphRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemParagraphRichTextItemTextLink"></a>

`BlockCreateParamsChildrenItemParagraphRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemParagraphRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemPdf"></a>

`BlockCreateParamsChildrenItemPdf(**data: Any)`
:   Media file. Use external URL or file upload.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemPdfExternal | None`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemPdfFileUpload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   File type: external or file_upload

<a id="BlockCreateParamsChildrenItemPdfExternal"></a>

`BlockCreateParamsChildrenItemPdfExternal(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemPdf.external
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemPdfFileUpload"></a>

`BlockCreateParamsChildrenItemPdfFileUpload(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemPdf.file_upload
    
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

<a id="BlockCreateParamsChildrenItemQuote"></a>

`BlockCreateParamsChildrenItemQuote(**data: Any)`
:   Quote block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemQuoteRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemQuoteRichTextItem"></a>

`BlockCreateParamsChildrenItemQuoteRichTextItem(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemQuote.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemQuoteRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemQuoteRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemQuoteRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemQuoteRichTextItemAnnotations"></a>

`BlockCreateParamsChildrenItemQuoteRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemQuoteRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemQuoteRichTextItemEquation"></a>

`BlockCreateParamsChildrenItemQuoteRichTextItemEquation(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemQuoteRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemQuoteRichTextItemText"></a>

`BlockCreateParamsChildrenItemQuoteRichTextItemText(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemQuoteRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemQuoteRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemQuoteRichTextItemTextLink"></a>

`BlockCreateParamsChildrenItemQuoteRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemQuoteRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemTableOfContents"></a>

`BlockCreateParamsChildrenItemTableOfContents(**data: Any)`
:   Table of contents block
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemToDo"></a>

`BlockCreateParamsChildrenItemToDo(**data: Any)`
:   To-do block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checked: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemToDoRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemToDoRichTextItem"></a>

`BlockCreateParamsChildrenItemToDoRichTextItem(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemToDo.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemToDoRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemToDoRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemToDoRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemToDoRichTextItemAnnotations"></a>

`BlockCreateParamsChildrenItemToDoRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemToDoRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemToDoRichTextItemEquation"></a>

`BlockCreateParamsChildrenItemToDoRichTextItemEquation(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemToDoRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemToDoRichTextItemText"></a>

`BlockCreateParamsChildrenItemToDoRichTextItemText(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemToDoRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemToDoRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemToDoRichTextItemTextLink"></a>

`BlockCreateParamsChildrenItemToDoRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemToDoRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemToggle"></a>

`BlockCreateParamsChildrenItemToggle(**data: Any)`
:   Toggle block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemToggleRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemToggleRichTextItem"></a>

`BlockCreateParamsChildrenItemToggleRichTextItem(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemToggle.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemToggleRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemToggleRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemToggleRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemToggleRichTextItemAnnotations"></a>

`BlockCreateParamsChildrenItemToggleRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemToggleRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemToggleRichTextItemEquation"></a>

`BlockCreateParamsChildrenItemToggleRichTextItemEquation(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemToggleRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemToggleRichTextItemText"></a>

`BlockCreateParamsChildrenItemToggleRichTextItemText(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemToggleRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemToggleRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemToggleRichTextItemTextLink"></a>

`BlockCreateParamsChildrenItemToggleRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemToggleRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemVideo"></a>

`BlockCreateParamsChildrenItemVideo(**data: Any)`
:   Media file. Use external URL or file upload.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemVideoExternal | None`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.models.BlockCreateParamsChildrenItemVideoFileUpload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   File type: external or file_upload

<a id="BlockCreateParamsChildrenItemVideoExternal"></a>

`BlockCreateParamsChildrenItemVideoExternal(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemVideo.external
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockCreateParamsChildrenItemVideoFileUpload"></a>

`BlockCreateParamsChildrenItemVideoFileUpload(**data: Any)`
:   Nested schema for BlockCreateParamsChildrenItemVideo.file_upload
    
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

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
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

    `url: str | None`
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

    `expression: str | None`
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

    `color: str | None`
    :   The type of the None singleton.

    `is_toggleable: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
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

    `color: str | None`
    :   The type of the None singleton.

    `is_toggleable: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
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

    `color: str | None`
    :   The type of the None singleton.

    `is_toggleable: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
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

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
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

    `url: str | None`
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

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
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

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
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

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
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

    `has_column_header: bool | None`
    :   The type of the None singleton.

    `has_row_header: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `table_width: int | None`
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

    `color: str | None`
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

    `cells: list[typing.Any] | None`
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

    `checked: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
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

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
    :   The type of the None singleton.

<a id="BlockUpdateParams"></a>

`BlockUpdateParams(**data: Any)`
:   Parameters for updating a block. Include the block type and its updated content. Omitted fields within the type are unchanged.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `audio: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsAudio | None`
    :   The type of the None singleton.

    `bookmark: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsBookmark | None`
    :   The type of the None singleton.

    `bulleted_list_item: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsBulletedListItem | None`
    :   The type of the None singleton.

    `callout: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCallout | None`
    :   The type of the None singleton.

    `code: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCode | None`
    :   The type of the None singleton.

    `embed: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsEmbed | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsEquation | None`
    :   The type of the None singleton.

    `file: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsFile | None`
    :   The type of the None singleton.

    `heading_1: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading1 | None`
    :   The type of the None singleton.

    `heading_2: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading2 | None`
    :   The type of the None singleton.

    `heading_3: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading3 | None`
    :   The type of the None singleton.

    `image: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsImage | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `numbered_list_item: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsNumberedListItem | None`
    :   The type of the None singleton.

    `paragraph: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsParagraph | None`
    :   The type of the None singleton.

    `pdf: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsPdf | None`
    :   The type of the None singleton.

    `quote: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsQuote | None`
    :   The type of the None singleton.

    `table: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsTable | None`
    :   The type of the None singleton.

    `to_do: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsToDo | None`
    :   The type of the None singleton.

    `toggle: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsToggle | None`
    :   The type of the None singleton.

    `video: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsVideo | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsAudio"></a>

`BlockUpdateParamsAudio(**data: Any)`
:   Media file. Use external URL or file upload.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsAudioExternal | None`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsAudioFileUpload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   File type: external or file_upload

<a id="BlockUpdateParamsAudioExternal"></a>

`BlockUpdateParamsAudioExternal(**data: Any)`
:   Nested schema for BlockUpdateParamsAudio.external
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsAudioFileUpload"></a>

`BlockUpdateParamsAudioFileUpload(**data: Any)`
:   Nested schema for BlockUpdateParamsAudio.file_upload
    
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

<a id="BlockUpdateParamsBookmark"></a>

`BlockUpdateParamsBookmark(**data: Any)`
:   Updated bookmark
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `caption: list[airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsBookmarkCaptionItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsBookmarkCaptionItem"></a>

`BlockUpdateParamsBookmarkCaptionItem(**data: Any)`
:   Nested schema for BlockUpdateParamsBookmark.caption_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsBookmarkCaptionItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsBookmarkCaptionItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsBookmarkCaptionItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsBookmarkCaptionItemAnnotations"></a>

`BlockUpdateParamsBookmarkCaptionItemAnnotations(**data: Any)`
:   Nested schema for BlockUpdateParamsBookmarkCaptionItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsBookmarkCaptionItemEquation"></a>

`BlockUpdateParamsBookmarkCaptionItemEquation(**data: Any)`
:   Nested schema for BlockUpdateParamsBookmarkCaptionItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsBookmarkCaptionItemText"></a>

`BlockUpdateParamsBookmarkCaptionItemText(**data: Any)`
:   Nested schema for BlockUpdateParamsBookmarkCaptionItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsBookmarkCaptionItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsBookmarkCaptionItemTextLink"></a>

`BlockUpdateParamsBookmarkCaptionItemTextLink(**data: Any)`
:   Nested schema for BlockUpdateParamsBookmarkCaptionItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsBulletedListItem"></a>

`BlockUpdateParamsBulletedListItem(**data: Any)`
:   Updated bulleted list item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsBulletedListItemRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsBulletedListItemRichTextItem"></a>

`BlockUpdateParamsBulletedListItemRichTextItem(**data: Any)`
:   Nested schema for BlockUpdateParamsBulletedListItem.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsBulletedListItemRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsBulletedListItemRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsBulletedListItemRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsBulletedListItemRichTextItemAnnotations"></a>

`BlockUpdateParamsBulletedListItemRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockUpdateParamsBulletedListItemRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsBulletedListItemRichTextItemEquation"></a>

`BlockUpdateParamsBulletedListItemRichTextItemEquation(**data: Any)`
:   Nested schema for BlockUpdateParamsBulletedListItemRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsBulletedListItemRichTextItemText"></a>

`BlockUpdateParamsBulletedListItemRichTextItemText(**data: Any)`
:   Nested schema for BlockUpdateParamsBulletedListItemRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsBulletedListItemRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsBulletedListItemRichTextItemTextLink"></a>

`BlockUpdateParamsBulletedListItemRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockUpdateParamsBulletedListItemRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCallout"></a>

`BlockUpdateParamsCallout(**data: Any)`
:   Updated callout content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `icon: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCalloutRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCalloutRichTextItem"></a>

`BlockUpdateParamsCalloutRichTextItem(**data: Any)`
:   Nested schema for BlockUpdateParamsCallout.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCalloutRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCalloutRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCalloutRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCalloutRichTextItemAnnotations"></a>

`BlockUpdateParamsCalloutRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockUpdateParamsCalloutRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCalloutRichTextItemEquation"></a>

`BlockUpdateParamsCalloutRichTextItemEquation(**data: Any)`
:   Nested schema for BlockUpdateParamsCalloutRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCalloutRichTextItemText"></a>

`BlockUpdateParamsCalloutRichTextItemText(**data: Any)`
:   Nested schema for BlockUpdateParamsCalloutRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCalloutRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCalloutRichTextItemTextLink"></a>

`BlockUpdateParamsCalloutRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockUpdateParamsCalloutRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCode"></a>

`BlockUpdateParamsCode(**data: Any)`
:   Updated code block content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `caption: list[airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCodeCaptionItem] | None`
    :   The type of the None singleton.

    `language: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCodeRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCodeCaptionItem"></a>

`BlockUpdateParamsCodeCaptionItem(**data: Any)`
:   Nested schema for BlockUpdateParamsCode.caption_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCodeCaptionItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCodeCaptionItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCodeCaptionItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCodeCaptionItemAnnotations"></a>

`BlockUpdateParamsCodeCaptionItemAnnotations(**data: Any)`
:   Nested schema for BlockUpdateParamsCodeCaptionItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCodeCaptionItemEquation"></a>

`BlockUpdateParamsCodeCaptionItemEquation(**data: Any)`
:   Nested schema for BlockUpdateParamsCodeCaptionItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCodeCaptionItemText"></a>

`BlockUpdateParamsCodeCaptionItemText(**data: Any)`
:   Nested schema for BlockUpdateParamsCodeCaptionItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCodeCaptionItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCodeCaptionItemTextLink"></a>

`BlockUpdateParamsCodeCaptionItemTextLink(**data: Any)`
:   Nested schema for BlockUpdateParamsCodeCaptionItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCodeRichTextItem"></a>

`BlockUpdateParamsCodeRichTextItem(**data: Any)`
:   Nested schema for BlockUpdateParamsCode.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCodeRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCodeRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCodeRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCodeRichTextItemAnnotations"></a>

`BlockUpdateParamsCodeRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockUpdateParamsCodeRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCodeRichTextItemEquation"></a>

`BlockUpdateParamsCodeRichTextItemEquation(**data: Any)`
:   Nested schema for BlockUpdateParamsCodeRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCodeRichTextItemText"></a>

`BlockUpdateParamsCodeRichTextItemText(**data: Any)`
:   Nested schema for BlockUpdateParamsCodeRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsCodeRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsCodeRichTextItemTextLink"></a>

`BlockUpdateParamsCodeRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockUpdateParamsCodeRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsEmbed"></a>

`BlockUpdateParamsEmbed(**data: Any)`
:   Updated embed
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsEquation"></a>

`BlockUpdateParamsEquation(**data: Any)`
:   Updated equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsFile"></a>

`BlockUpdateParamsFile(**data: Any)`
:   Media file. Use external URL or file upload.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsFileExternal | None`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsFileFileUpload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   File type: external or file_upload

<a id="BlockUpdateParamsFileExternal"></a>

`BlockUpdateParamsFileExternal(**data: Any)`
:   Nested schema for BlockUpdateParamsFile.external
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsFileFileUpload"></a>

`BlockUpdateParamsFileFileUpload(**data: Any)`
:   Nested schema for BlockUpdateParamsFile.file_upload
    
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

<a id="BlockUpdateParamsHeading1"></a>

`BlockUpdateParamsHeading1(**data: Any)`
:   Updated heading 1 content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `is_toggleable: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading1RichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading1RichTextItem"></a>

`BlockUpdateParamsHeading1RichTextItem(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading1.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading1RichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading1RichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading1RichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading1RichTextItemAnnotations"></a>

`BlockUpdateParamsHeading1RichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading1RichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading1RichTextItemEquation"></a>

`BlockUpdateParamsHeading1RichTextItemEquation(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading1RichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading1RichTextItemText"></a>

`BlockUpdateParamsHeading1RichTextItemText(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading1RichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading1RichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading1RichTextItemTextLink"></a>

`BlockUpdateParamsHeading1RichTextItemTextLink(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading1RichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading2"></a>

`BlockUpdateParamsHeading2(**data: Any)`
:   Updated heading 2 content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `is_toggleable: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading2RichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading2RichTextItem"></a>

`BlockUpdateParamsHeading2RichTextItem(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading2.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading2RichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading2RichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading2RichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading2RichTextItemAnnotations"></a>

`BlockUpdateParamsHeading2RichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading2RichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading2RichTextItemEquation"></a>

`BlockUpdateParamsHeading2RichTextItemEquation(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading2RichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading2RichTextItemText"></a>

`BlockUpdateParamsHeading2RichTextItemText(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading2RichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading2RichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading2RichTextItemTextLink"></a>

`BlockUpdateParamsHeading2RichTextItemTextLink(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading2RichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading3"></a>

`BlockUpdateParamsHeading3(**data: Any)`
:   Updated heading 3 content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `is_toggleable: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading3RichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading3RichTextItem"></a>

`BlockUpdateParamsHeading3RichTextItem(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading3.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading3RichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading3RichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading3RichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading3RichTextItemAnnotations"></a>

`BlockUpdateParamsHeading3RichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading3RichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading3RichTextItemEquation"></a>

`BlockUpdateParamsHeading3RichTextItemEquation(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading3RichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading3RichTextItemText"></a>

`BlockUpdateParamsHeading3RichTextItemText(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading3RichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsHeading3RichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsHeading3RichTextItemTextLink"></a>

`BlockUpdateParamsHeading3RichTextItemTextLink(**data: Any)`
:   Nested schema for BlockUpdateParamsHeading3RichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsImage"></a>

`BlockUpdateParamsImage(**data: Any)`
:   Media file. Use external URL or file upload.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsImageExternal | None`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsImageFileUpload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   File type: external or file_upload

<a id="BlockUpdateParamsImageExternal"></a>

`BlockUpdateParamsImageExternal(**data: Any)`
:   Nested schema for BlockUpdateParamsImage.external
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsImageFileUpload"></a>

`BlockUpdateParamsImageFileUpload(**data: Any)`
:   Nested schema for BlockUpdateParamsImage.file_upload
    
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

<a id="BlockUpdateParamsNumberedListItem"></a>

`BlockUpdateParamsNumberedListItem(**data: Any)`
:   Updated numbered list item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsNumberedListItemRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsNumberedListItemRichTextItem"></a>

`BlockUpdateParamsNumberedListItemRichTextItem(**data: Any)`
:   Nested schema for BlockUpdateParamsNumberedListItem.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsNumberedListItemRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsNumberedListItemRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsNumberedListItemRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsNumberedListItemRichTextItemAnnotations"></a>

`BlockUpdateParamsNumberedListItemRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockUpdateParamsNumberedListItemRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsNumberedListItemRichTextItemEquation"></a>

`BlockUpdateParamsNumberedListItemRichTextItemEquation(**data: Any)`
:   Nested schema for BlockUpdateParamsNumberedListItemRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsNumberedListItemRichTextItemText"></a>

`BlockUpdateParamsNumberedListItemRichTextItemText(**data: Any)`
:   Nested schema for BlockUpdateParamsNumberedListItemRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsNumberedListItemRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsNumberedListItemRichTextItemTextLink"></a>

`BlockUpdateParamsNumberedListItemRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockUpdateParamsNumberedListItemRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsParagraph"></a>

`BlockUpdateParamsParagraph(**data: Any)`
:   Updated paragraph content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsParagraphRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsParagraphRichTextItem"></a>

`BlockUpdateParamsParagraphRichTextItem(**data: Any)`
:   Nested schema for BlockUpdateParamsParagraph.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsParagraphRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsParagraphRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsParagraphRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsParagraphRichTextItemAnnotations"></a>

`BlockUpdateParamsParagraphRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockUpdateParamsParagraphRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsParagraphRichTextItemEquation"></a>

`BlockUpdateParamsParagraphRichTextItemEquation(**data: Any)`
:   Nested schema for BlockUpdateParamsParagraphRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsParagraphRichTextItemText"></a>

`BlockUpdateParamsParagraphRichTextItemText(**data: Any)`
:   Nested schema for BlockUpdateParamsParagraphRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsParagraphRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsParagraphRichTextItemTextLink"></a>

`BlockUpdateParamsParagraphRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockUpdateParamsParagraphRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsPdf"></a>

`BlockUpdateParamsPdf(**data: Any)`
:   Media file. Use external URL or file upload.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsPdfExternal | None`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsPdfFileUpload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   File type: external or file_upload

<a id="BlockUpdateParamsPdfExternal"></a>

`BlockUpdateParamsPdfExternal(**data: Any)`
:   Nested schema for BlockUpdateParamsPdf.external
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsPdfFileUpload"></a>

`BlockUpdateParamsPdfFileUpload(**data: Any)`
:   Nested schema for BlockUpdateParamsPdf.file_upload
    
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

<a id="BlockUpdateParamsQuote"></a>

`BlockUpdateParamsQuote(**data: Any)`
:   Updated quote content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsQuoteRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsQuoteRichTextItem"></a>

`BlockUpdateParamsQuoteRichTextItem(**data: Any)`
:   Nested schema for BlockUpdateParamsQuote.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsQuoteRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsQuoteRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsQuoteRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsQuoteRichTextItemAnnotations"></a>

`BlockUpdateParamsQuoteRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockUpdateParamsQuoteRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsQuoteRichTextItemEquation"></a>

`BlockUpdateParamsQuoteRichTextItemEquation(**data: Any)`
:   Nested schema for BlockUpdateParamsQuoteRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsQuoteRichTextItemText"></a>

`BlockUpdateParamsQuoteRichTextItemText(**data: Any)`
:   Nested schema for BlockUpdateParamsQuoteRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsQuoteRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsQuoteRichTextItemTextLink"></a>

`BlockUpdateParamsQuoteRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockUpdateParamsQuoteRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsTable"></a>

`BlockUpdateParamsTable(**data: Any)`
:   Updated table properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_column_header: bool | None`
    :   The type of the None singleton.

    `has_row_header: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsToDo"></a>

`BlockUpdateParamsToDo(**data: Any)`
:   Updated to-do content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checked: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsToDoRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsToDoRichTextItem"></a>

`BlockUpdateParamsToDoRichTextItem(**data: Any)`
:   Nested schema for BlockUpdateParamsToDo.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsToDoRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsToDoRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsToDoRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsToDoRichTextItemAnnotations"></a>

`BlockUpdateParamsToDoRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockUpdateParamsToDoRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsToDoRichTextItemEquation"></a>

`BlockUpdateParamsToDoRichTextItemEquation(**data: Any)`
:   Nested schema for BlockUpdateParamsToDoRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsToDoRichTextItemText"></a>

`BlockUpdateParamsToDoRichTextItemText(**data: Any)`
:   Nested schema for BlockUpdateParamsToDoRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsToDoRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsToDoRichTextItemTextLink"></a>

`BlockUpdateParamsToDoRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockUpdateParamsToDoRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsToggle"></a>

`BlockUpdateParamsToggle(**data: Any)`
:   Updated toggle content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsToggleRichTextItem] | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsToggleRichTextItem"></a>

`BlockUpdateParamsToggleRichTextItem(**data: Any)`
:   Nested schema for BlockUpdateParamsToggle.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsToggleRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsToggleRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsToggleRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsToggleRichTextItemAnnotations"></a>

`BlockUpdateParamsToggleRichTextItemAnnotations(**data: Any)`
:   Nested schema for BlockUpdateParamsToggleRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsToggleRichTextItemEquation"></a>

`BlockUpdateParamsToggleRichTextItemEquation(**data: Any)`
:   Nested schema for BlockUpdateParamsToggleRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsToggleRichTextItemText"></a>

`BlockUpdateParamsToggleRichTextItemText(**data: Any)`
:   Nested schema for BlockUpdateParamsToggleRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsToggleRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BlockUpdateParamsToggleRichTextItemTextLink"></a>

`BlockUpdateParamsToggleRichTextItemTextLink(**data: Any)`
:   Nested schema for BlockUpdateParamsToggleRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsVideo"></a>

`BlockUpdateParamsVideo(**data: Any)`
:   Media file. Use external URL or file upload.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsVideoExternal | None`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.models.BlockUpdateParamsVideoFileUpload | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   File type: external or file_upload

<a id="BlockUpdateParamsVideoExternal"></a>

`BlockUpdateParamsVideoExternal(**data: Any)`
:   Nested schema for BlockUpdateParamsVideo.external
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="BlockUpdateParamsVideoFileUpload"></a>

`BlockUpdateParamsVideoFileUpload(**data: Any)`
:   Nested schema for BlockUpdateParamsVideo.file_upload
    
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

    `block: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

    `object_: str | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.notion.models.Block] | None`
    :   The type of the None singleton.

    `type_: str | None`
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

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
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

    `created_by: airbyte_agent_sdk.connectors.notion.models.CommentCreatedBy | None`
    :   The type of the None singleton.

    `created_time: str | None`
    :   The type of the None singleton.

    `discussion_id: str | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `last_edited_time: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   The type of the None singleton.

    `parent: typing.Any | None`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
    :   The type of the None singleton.

<a id="CommentCreateParams"></a>

`CommentCreateParams(**data: Any)`
:   Parameters for creating a comment. Provide either parent (with page_id or block_id) for a new comment, or discussion_id to reply to an existing thread. Exactly one of parent or discussion_id must be provided.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `discussion_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `parent: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.models.CommentCreateParamsRichTextItem]`
    :   The type of the None singleton.

<a id="CommentCreateParamsRichTextItem"></a>

`CommentCreateParamsRichTextItem(**data: Any)`
:   Nested schema for CommentCreateParams.rich_text_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.CommentCreateParamsRichTextItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.CommentCreateParamsRichTextItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.CommentCreateParamsRichTextItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="CommentCreateParamsRichTextItemAnnotations"></a>

`CommentCreateParamsRichTextItemAnnotations(**data: Any)`
:   Nested schema for CommentCreateParamsRichTextItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="CommentCreateParamsRichTextItemEquation"></a>

`CommentCreateParamsRichTextItemEquation(**data: Any)`
:   Nested schema for CommentCreateParamsRichTextItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CommentCreateParamsRichTextItemText"></a>

`CommentCreateParamsRichTextItemText(**data: Any)`
:   Nested schema for CommentCreateParamsRichTextItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.CommentCreateParamsRichTextItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CommentCreateParamsRichTextItemTextLink"></a>

`CommentCreateParamsRichTextItemTextLink(**data: Any)`
:   Nested schema for CommentCreateParamsRichTextItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
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

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
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

    `comment: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

    `object_: str | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.notion.models.Comment] | None`
    :   The type of the None singleton.

    `type_: str | None`
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

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

<a id="CommentsSearchData"></a>

`CommentsSearchData(**data: Any)`
:   Search result data for comments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_by: dict[str, typing.Any] | None`
    :   User who created the comment.

    `created_time: str | None`
    :   Date and time when the comment was created.

    `discussion_id: str | None`
    :   Discussion thread ID.

    `id: str | None`
    :   Unique identifier for the comment.

    `last_edited_time: str | None`
    :   Date and time when the comment was last edited.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   Always comment.

    `parent: dict[str, typing.Any] | None`
    :   Parent of the comment.

    `rich_text: list[typing.Any] | None`
    :   Content of the comment as rich text.

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

    `archived: bool | None`
    :   The type of the None singleton.

    `cover: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_by: airbyte_agent_sdk.connectors.notion.models.DataSourceCreatedBy | None`
    :   The type of the None singleton.

    `created_time: str | None`
    :   The type of the None singleton.

    `database_parent: typing.Any | None`
    :   The type of the None singleton.

    `description: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
    :   The type of the None singleton.

    `icon: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `in_trash: bool | None`
    :   The type of the None singleton.

    `is_archived: bool | None`
    :   The type of the None singleton.

    `is_inline: bool | None`
    :   The type of the None singleton.

    `is_locked: bool | None`
    :   The type of the None singleton.

    `last_edited_by: airbyte_agent_sdk.connectors.notion.models.DataSourceLastEditedBy | None`
    :   The type of the None singleton.

    `last_edited_time: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   The type of the None singleton.

    `parent: typing.Any | None`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `public_url: str | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `title: list[airbyte_agent_sdk.connectors.notion.models.RichText] | None`
    :   The type of the None singleton.

    `url: str | None`
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

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
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

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   The type of the None singleton.

<a id="DataSourceUpdateParams"></a>

`DataSourceUpdateParams(**data: Any)`
:   Parameters for updating a data source. All fields are optional.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `cover: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsCover | None`
    :   The type of the None singleton.

    `description: list[airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsDescriptionItem] | None`
    :   The type of the None singleton.

    `icon: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsIcon | None`
    :   The type of the None singleton.

    `in_trash: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `title: list[airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsTitleItem] | None`
    :   The type of the None singleton.

<a id="DataSourceUpdateParamsCover"></a>

`DataSourceUpdateParamsCover(**data: Any)`
:   Cover image. Supports external URL or file upload. Set to null to remove.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsCoverExternal | None`
    :   External URL cover

    `file_upload: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsCoverFileUpload | None`
    :   Uploaded file cover

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   Cover type: external or file_upload

<a id="DataSourceUpdateParamsCoverExternal"></a>

`DataSourceUpdateParamsCoverExternal(**data: Any)`
:   External URL cover
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="DataSourceUpdateParamsCoverFileUpload"></a>

`DataSourceUpdateParamsCoverFileUpload(**data: Any)`
:   Uploaded file cover
    
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

<a id="DataSourceUpdateParamsDescriptionItem"></a>

`DataSourceUpdateParamsDescriptionItem(**data: Any)`
:   Nested schema for DataSourceUpdateParams.description_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsDescriptionItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsDescriptionItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsDescriptionItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="DataSourceUpdateParamsDescriptionItemAnnotations"></a>

`DataSourceUpdateParamsDescriptionItemAnnotations(**data: Any)`
:   Nested schema for DataSourceUpdateParamsDescriptionItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="DataSourceUpdateParamsDescriptionItemEquation"></a>

`DataSourceUpdateParamsDescriptionItemEquation(**data: Any)`
:   Nested schema for DataSourceUpdateParamsDescriptionItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DataSourceUpdateParamsDescriptionItemText"></a>

`DataSourceUpdateParamsDescriptionItemText(**data: Any)`
:   Nested schema for DataSourceUpdateParamsDescriptionItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsDescriptionItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DataSourceUpdateParamsDescriptionItemTextLink"></a>

`DataSourceUpdateParamsDescriptionItemTextLink(**data: Any)`
:   Nested schema for DataSourceUpdateParamsDescriptionItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="DataSourceUpdateParamsIcon"></a>

`DataSourceUpdateParamsIcon(**data: Any)`
:   Icon. Supports emoji, external URL, file upload, custom emoji, and Notion native icons. Set to null to remove.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `custom_emoji: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsIconCustomEmoji | None`
    :   Custom emoji icon (when type is custom_emoji)

    `emoji: str | None`
    :   Emoji character (when type is emoji)

    `external: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsIconExternal | None`
    :   External URL icon (when type is external)

    `file_upload: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsIconFileUpload | None`
    :   Uploaded file icon (when type is file_upload)

    `icon: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsIconIcon | None`
    :   Notion native icon (when type is icon)

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   Icon type: emoji, external, file_upload, custom_emoji, or icon

<a id="DataSourceUpdateParamsIconCustomEmoji"></a>

`DataSourceUpdateParamsIconCustomEmoji(**data: Any)`
:   Custom emoji icon (when type is custom_emoji)
    
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

<a id="DataSourceUpdateParamsIconExternal"></a>

`DataSourceUpdateParamsIconExternal(**data: Any)`
:   External URL icon (when type is external)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="DataSourceUpdateParamsIconFileUpload"></a>

`DataSourceUpdateParamsIconFileUpload(**data: Any)`
:   Uploaded file icon (when type is file_upload)
    
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

<a id="DataSourceUpdateParamsIconIcon"></a>

`DataSourceUpdateParamsIconIcon(**data: Any)`
:   Notion native icon (when type is icon)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

<a id="DataSourceUpdateParamsTitleItem"></a>

`DataSourceUpdateParamsTitleItem(**data: Any)`
:   Nested schema for DataSourceUpdateParams.title_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsTitleItemAnnotations | None`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsTitleItemEquation | None`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsTitleItemText | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="DataSourceUpdateParamsTitleItemAnnotations"></a>

`DataSourceUpdateParamsTitleItemAnnotations(**data: Any)`
:   Nested schema for DataSourceUpdateParamsTitleItem.annotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
    :   The type of the None singleton.

<a id="DataSourceUpdateParamsTitleItemEquation"></a>

`DataSourceUpdateParamsTitleItemEquation(**data: Any)`
:   Nested schema for DataSourceUpdateParamsTitleItem.equation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expression: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DataSourceUpdateParamsTitleItemText"></a>

`DataSourceUpdateParamsTitleItemText(**data: Any)`
:   Nested schema for DataSourceUpdateParamsTitleItem.text
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.models.DataSourceUpdateParamsTitleItemTextLink | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DataSourceUpdateParamsTitleItemTextLink"></a>

`DataSourceUpdateParamsTitleItemTextLink(**data: Any)`
:   Nested schema for DataSourceUpdateParamsTitleItemText.link
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
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

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

    `object_: str | None`
    :   The type of the None singleton.

    `page_or_data_source: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.notion.models.DataSource] | None`
    :   The type of the None singleton.

    `type_: str | None`
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

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
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

    `meta: ~S | None`
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

    `archived: bool | None`
    :   The type of the None singleton.

    `cover: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_by: airbyte_agent_sdk.connectors.notion.models.PageCreatedBy | None`
    :   The type of the None singleton.

    `created_time: str | None`
    :   The type of the None singleton.

    `icon: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `in_trash: bool | None`
    :   The type of the None singleton.

    `is_archived: bool | None`
    :   The type of the None singleton.

    `is_locked: bool | None`
    :   The type of the None singleton.

    `last_edited_by: airbyte_agent_sdk.connectors.notion.models.PageLastEditedBy | None`
    :   The type of the None singleton.

    `last_edited_time: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   The type of the None singleton.

    `parent: typing.Any | None`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `public_url: str | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="PageCreateParams"></a>

`PageCreateParams(**data: Any)`
:   Parameters for creating a new page as a child of an existing page, data source, or at the workspace level.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `children: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `cover: airbyte_agent_sdk.connectors.notion.models.PageCreateParamsCover | None`
    :   The type of the None singleton.

    `icon: airbyte_agent_sdk.connectors.notion.models.PageCreateParamsIcon | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `parent: dict[str, typing.Any]`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any] | None`
    :   The type of the None singleton.

<a id="PageCreateParamsCover"></a>

`PageCreateParamsCover(**data: Any)`
:   Cover image. Supports external URL or file upload. Set to null to remove.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.models.PageCreateParamsCoverExternal | None`
    :   External URL cover

    `file_upload: airbyte_agent_sdk.connectors.notion.models.PageCreateParamsCoverFileUpload | None`
    :   Uploaded file cover

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   Cover type: external or file_upload

<a id="PageCreateParamsCoverExternal"></a>

`PageCreateParamsCoverExternal(**data: Any)`
:   External URL cover
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="PageCreateParamsCoverFileUpload"></a>

`PageCreateParamsCoverFileUpload(**data: Any)`
:   Uploaded file cover
    
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

<a id="PageCreateParamsIcon"></a>

`PageCreateParamsIcon(**data: Any)`
:   Icon. Supports emoji, external URL, file upload, custom emoji, and Notion native icons. Set to null to remove.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `custom_emoji: airbyte_agent_sdk.connectors.notion.models.PageCreateParamsIconCustomEmoji | None`
    :   Custom emoji icon (when type is custom_emoji)

    `emoji: str | None`
    :   Emoji character (when type is emoji)

    `external: airbyte_agent_sdk.connectors.notion.models.PageCreateParamsIconExternal | None`
    :   External URL icon (when type is external)

    `file_upload: airbyte_agent_sdk.connectors.notion.models.PageCreateParamsIconFileUpload | None`
    :   Uploaded file icon (when type is file_upload)

    `icon: airbyte_agent_sdk.connectors.notion.models.PageCreateParamsIconIcon | None`
    :   Notion native icon (when type is icon)

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   Icon type: emoji, external, file_upload, custom_emoji, or icon

<a id="PageCreateParamsIconCustomEmoji"></a>

`PageCreateParamsIconCustomEmoji(**data: Any)`
:   Custom emoji icon (when type is custom_emoji)
    
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

<a id="PageCreateParamsIconExternal"></a>

`PageCreateParamsIconExternal(**data: Any)`
:   External URL icon (when type is external)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="PageCreateParamsIconFileUpload"></a>

`PageCreateParamsIconFileUpload(**data: Any)`
:   Uploaded file icon (when type is file_upload)
    
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

<a id="PageCreateParamsIconIcon"></a>

`PageCreateParamsIconIcon(**data: Any)`
:   Notion native icon (when type is icon)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
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

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
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

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   The type of the None singleton.

<a id="PageUpdateParams"></a>

`PageUpdateParams(**data: Any)`
:   Parameters for updating a page. All fields are optional for partial updates.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `cover: airbyte_agent_sdk.connectors.notion.models.PageUpdateParamsCover | None`
    :   The type of the None singleton.

    `icon: airbyte_agent_sdk.connectors.notion.models.PageUpdateParamsIcon | None`
    :   The type of the None singleton.

    `in_trash: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any] | None`
    :   The type of the None singleton.

<a id="PageUpdateParamsCover"></a>

`PageUpdateParamsCover(**data: Any)`
:   Cover image. Supports external URL or file upload. Set to null to remove.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.models.PageUpdateParamsCoverExternal | None`
    :   External URL cover

    `file_upload: airbyte_agent_sdk.connectors.notion.models.PageUpdateParamsCoverFileUpload | None`
    :   Uploaded file cover

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   Cover type: external or file_upload

<a id="PageUpdateParamsCoverExternal"></a>

`PageUpdateParamsCoverExternal(**data: Any)`
:   External URL cover
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="PageUpdateParamsCoverFileUpload"></a>

`PageUpdateParamsCoverFileUpload(**data: Any)`
:   Uploaded file cover
    
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

<a id="PageUpdateParamsIcon"></a>

`PageUpdateParamsIcon(**data: Any)`
:   Icon. Supports emoji, external URL, file upload, custom emoji, and Notion native icons. Set to null to remove.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `custom_emoji: airbyte_agent_sdk.connectors.notion.models.PageUpdateParamsIconCustomEmoji | None`
    :   Custom emoji icon (when type is custom_emoji)

    `emoji: str | None`
    :   Emoji character (when type is emoji)

    `external: airbyte_agent_sdk.connectors.notion.models.PageUpdateParamsIconExternal | None`
    :   External URL icon (when type is external)

    `file_upload: airbyte_agent_sdk.connectors.notion.models.PageUpdateParamsIconFileUpload | None`
    :   Uploaded file icon (when type is file_upload)

    `icon: airbyte_agent_sdk.connectors.notion.models.PageUpdateParamsIconIcon | None`
    :   Notion native icon (when type is icon)

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   Icon type: emoji, external, file_upload, custom_emoji, or icon

<a id="PageUpdateParamsIconCustomEmoji"></a>

`PageUpdateParamsIconCustomEmoji(**data: Any)`
:   Custom emoji icon (when type is custom_emoji)
    
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

<a id="PageUpdateParamsIconExternal"></a>

`PageUpdateParamsIconExternal(**data: Any)`
:   External URL icon (when type is external)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="PageUpdateParamsIconFileUpload"></a>

`PageUpdateParamsIconFileUpload(**data: Any)`
:   Uploaded file icon (when type is file_upload)
    
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

<a id="PageUpdateParamsIconIcon"></a>

`PageUpdateParamsIconIcon(**data: Any)`
:   Notion native icon (when type is icon)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
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

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

    `object_: str | None`
    :   The type of the None singleton.

    `page_or_data_source: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.notion.models.Page] | None`
    :   The type of the None singleton.

    `type_: str | None`
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

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
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

    `block_id: str | None`
    :   The type of the None singleton.

    `data_source_id: str | None`
    :   The type of the None singleton.

    `database_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `page_id: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `workspace: bool | None`
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

    `annotations: airbyte_agent_sdk.connectors.notion.models.RichTextAnnotations | None`
    :   The type of the None singleton.

    `href: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `plain_text: str | None`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.models.RichTextText | None`
    :   The type of the None singleton.

    `type_: str | None`
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

    `bold: bool | None`
    :   The type of the None singleton.

    `code: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `italic: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `strikethrough: bool | None`
    :   The type of the None singleton.

    `underline: bool | None`
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

    `content: str | None`
    :   Plain text content

    `link: dict[str, typing.Any] | None`
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

    `avatar_url: str | None`
    :   The type of the None singleton.

    `bot: airbyte_agent_sdk.connectors.notion.models.UserBot | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `object_: str | None`
    :   The type of the None singleton.

    `person: airbyte_agent_sdk.connectors.notion.models.UserPerson | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `type_: str | None`
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

    `owner: dict[str, typing.Any] | None`
    :   Bot owner information

    `workspace_name: str | None`
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

    `email: str | None`
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

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

    `object_: str | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.notion.models.User] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `user: dict[str, typing.Any] | None`
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

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
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