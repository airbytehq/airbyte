---
id: airbyte_agent_sdk-connectors-notion-types
title: airbyte_agent_sdk.connectors.notion.types
---

Module airbyte_agent_sdk.connectors.notion.types
================================================
Type definitions for notion connector.

Classes
-------

<a id="AirbyteSearchParams"></a>

`AirbyteSearchParams(*args, **kwargs)`
:   Parameters for Airbyte cache search operations (generic, use entity-specific query types for better type hints).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `fields: list[list[str]]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `query: dict[str, typing.Any]`
    :   The type of the None singleton.

<a id="BlocksAndCondition"></a>

`BlocksAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.notion.types.BlocksEqCondition | airbyte_agent_sdk.connectors.notion.types.BlocksNeqCondition | airbyte_agent_sdk.connectors.notion.types.BlocksGtCondition | airbyte_agent_sdk.connectors.notion.types.BlocksGteCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLtCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLteCondition | airbyte_agent_sdk.connectors.notion.types.BlocksInCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLikeCondition | airbyte_agent_sdk.connectors.notion.types.BlocksFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.BlocksKeywordCondition | airbyte_agent_sdk.connectors.notion.types.BlocksContainsCondition | airbyte_agent_sdk.connectors.notion.types.BlocksNotCondition | airbyte_agent_sdk.connectors.notion.types.BlocksAndCondition | airbyte_agent_sdk.connectors.notion.types.BlocksOrCondition | airbyte_agent_sdk.connectors.notion.types.BlocksAnyCondition]`
    :   The type of the None singleton.

<a id="BlocksAnyCondition"></a>

`BlocksAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.notion.types.BlocksAnyValueFilter`
    :   The type of the None singleton.

<a id="BlocksAnyValueFilter"></a>

`BlocksAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Indicates if the block is archived or not.

    `bookmark: Any`
    :   Represents a bookmark within the block

    `breadcrumb: Any`
    :   Represents a breadcrumb block.

    `bulleted_list_item: Any`
    :   Represents an item in a bulleted list.

    `callout: Any`
    :   Describes a callout message or content in the block

    `child_database: Any`
    :   Represents a child database block.

    `child_page: Any`
    :   Represents a child page block.

    `code: Any`
    :   Contains code snippets or blocks in the block content

    `column: Any`
    :   Represents a column block.

    `column_list: Any`
    :   Represents a list of columns.

    `created_by: Any`
    :   The user who created the block.

    `created_time: Any`
    :   The timestamp when the block was created.

    `divider: Any`
    :   Represents a divider block.

    `embed: Any`
    :   Contains embedded content such as videos, tweets, etc.

    `equation: Any`
    :   Represents an equation or mathematical formula in the block

    `file: Any`
    :   Represents a file block.

    `has_children: Any`
    :   Indicates if the block has children or not.

    `heading_1: Any`
    :   Represents a level 1 heading.

    `heading_2: Any`
    :   Represents a level 2 heading.

    `heading_3: Any`
    :   Represents a level 3 heading.

    `id: Any`
    :   The unique identifier of the block.

    `image: Any`
    :   Represents an image block.

    `last_edited_by: Any`
    :   The user who last edited the block.

    `last_edited_time: Any`
    :   The timestamp when the block was last edited.

    `link_preview: Any`
    :   Displays a preview of an external link within the block

    `link_to_page: Any`
    :   Provides a link to another page within the block

    `numbered_list_item: Any`
    :   Represents an item in a numbered list.

    `object_: Any`
    :   Represents an object block.

    `paragraph: Any`
    :   Represents a paragraph block.

    `parent: Any`
    :   The parent block of the current block.

    `pdf: Any`
    :   Represents a PDF document block.

    `quote: Any`
    :   Represents a quote block.

    `synced_block: Any`
    :   Represents a block synced from another source

    `table: Any`
    :   Represents a table within the block

    `table_of_contents: Any`
    :   Contains information regarding the table of contents

    `table_row: Any`
    :   Represents a row in a table within the block

    `template: Any`
    :   Specifies a template used within the block

    `to_do: Any`
    :   Represents a to-do list or task content

    `toggle: Any`
    :   Represents a toggle block.

    `type_: Any`
    :   The type of the block.

    `unsupported: Any`
    :   Represents an unsupported block.

    `video: Any`
    :   Represents a video block.

<a id="BlocksContainsCondition"></a>

`BlocksContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.notion.types.BlocksAnyValueFilter`
    :   The type of the None singleton.

<a id="BlocksCreateParams"></a>

`BlocksCreateParams(*args, **kwargs)`
:   Parameters for blocks.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `block_id: str`
    :   The type of the None singleton.

    `children: list[airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItem]`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItem"></a>

`BlocksCreateParamsChildrenItem(*args, **kwargs)`
:   A block object. Set type to the block kind and include matching content.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `audio: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemAudio`
    :   The type of the None singleton.

    `bookmark: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemBookmark`
    :   The type of the None singleton.

    `bulleted_list_item: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemBulletedListItem`
    :   The type of the None singleton.

    `callout: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemCallout`
    :   The type of the None singleton.

    `code: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemCode`
    :   The type of the None singleton.

    `divider: dict[str, typing.Any]`
    :   The type of the None singleton.

    `embed: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemEmbed`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemEquation`
    :   The type of the None singleton.

    `file: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemFile`
    :   The type of the None singleton.

    `heading_1: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading1`
    :   The type of the None singleton.

    `heading_2: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading2`
    :   The type of the None singleton.

    `heading_3: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading3`
    :   The type of the None singleton.

    `image: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemImage`
    :   The type of the None singleton.

    `numbered_list_item: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemNumberedListItem`
    :   The type of the None singleton.

    `paragraph: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemParagraph`
    :   The type of the None singleton.

    `pdf: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemPdf`
    :   The type of the None singleton.

    `quote: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemQuote`
    :   The type of the None singleton.

    `table_of_contents: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemTableOfContents`
    :   The type of the None singleton.

    `to_do: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemToDo`
    :   The type of the None singleton.

    `toggle: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemToggle`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

    `video: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemVideo`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemAudio"></a>

`BlocksCreateParamsChildrenItemAudio(*args, **kwargs)`
:   Media file. Use external URL or file upload.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemAudioExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemAudioFileUpload`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemAudioExternal"></a>

`BlocksCreateParamsChildrenItemAudioExternal(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemAudio.external

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemAudioFileUpload"></a>

`BlocksCreateParamsChildrenItemAudioFileUpload(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemAudio.file_upload

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemBookmark"></a>

`BlocksCreateParamsChildrenItemBookmark(*args, **kwargs)`
:   Bookmark block

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `caption: list[airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemBookmarkCaptionItem]`
    :   The type of the None singleton.

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemBookmarkCaptionItem"></a>

`BlocksCreateParamsChildrenItemBookmarkCaptionItem(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemBookmark.caption_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemBookmarkCaptionItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemBookmarkCaptionItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemBookmarkCaptionItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemBookmarkCaptionItemAnnotations"></a>

`BlocksCreateParamsChildrenItemBookmarkCaptionItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemBookmarkCaptionItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemBookmarkCaptionItemEquation"></a>

`BlocksCreateParamsChildrenItemBookmarkCaptionItemEquation(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemBookmarkCaptionItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemBookmarkCaptionItemText"></a>

`BlocksCreateParamsChildrenItemBookmarkCaptionItemText(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemBookmarkCaptionItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemBookmarkCaptionItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemBookmarkCaptionItemTextLink"></a>

`BlocksCreateParamsChildrenItemBookmarkCaptionItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemBookmarkCaptionItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemBulletedListItem"></a>

`BlocksCreateParamsChildrenItemBulletedListItem(*args, **kwargs)`
:   Bulleted list item content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemBulletedListItemRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemBulletedListItemRichTextItem"></a>

`BlocksCreateParamsChildrenItemBulletedListItemRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemBulletedListItem.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemBulletedListItemRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemBulletedListItemRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemBulletedListItemRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemBulletedListItemRichTextItemAnnotations"></a>

`BlocksCreateParamsChildrenItemBulletedListItemRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemBulletedListItemRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemBulletedListItemRichTextItemEquation"></a>

`BlocksCreateParamsChildrenItemBulletedListItemRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemBulletedListItemRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemBulletedListItemRichTextItemText"></a>

`BlocksCreateParamsChildrenItemBulletedListItemRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemBulletedListItemRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemBulletedListItemRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemBulletedListItemRichTextItemTextLink"></a>

`BlocksCreateParamsChildrenItemBulletedListItemRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemBulletedListItemRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemCallout"></a>

`BlocksCreateParamsChildrenItemCallout(*args, **kwargs)`
:   Callout block content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `icon: dict[str, typing.Any]`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemCalloutRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemCalloutRichTextItem"></a>

`BlocksCreateParamsChildrenItemCalloutRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemCallout.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemCalloutRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemCalloutRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemCalloutRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemCalloutRichTextItemAnnotations"></a>

`BlocksCreateParamsChildrenItemCalloutRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemCalloutRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemCalloutRichTextItemEquation"></a>

`BlocksCreateParamsChildrenItemCalloutRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemCalloutRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemCalloutRichTextItemText"></a>

`BlocksCreateParamsChildrenItemCalloutRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemCalloutRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemCalloutRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemCalloutRichTextItemTextLink"></a>

`BlocksCreateParamsChildrenItemCalloutRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemCalloutRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemCode"></a>

`BlocksCreateParamsChildrenItemCode(*args, **kwargs)`
:   Code block content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `language: str`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemCodeRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemCodeRichTextItem"></a>

`BlocksCreateParamsChildrenItemCodeRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemCode.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemCodeRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemCodeRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemCodeRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemCodeRichTextItemAnnotations"></a>

`BlocksCreateParamsChildrenItemCodeRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemCodeRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemCodeRichTextItemEquation"></a>

`BlocksCreateParamsChildrenItemCodeRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemCodeRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemCodeRichTextItemText"></a>

`BlocksCreateParamsChildrenItemCodeRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemCodeRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemCodeRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemCodeRichTextItemTextLink"></a>

`BlocksCreateParamsChildrenItemCodeRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemCodeRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemEmbed"></a>

`BlocksCreateParamsChildrenItemEmbed(*args, **kwargs)`
:   Embed block

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemEquation"></a>

`BlocksCreateParamsChildrenItemEquation(*args, **kwargs)`
:   Equation block

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemFile"></a>

`BlocksCreateParamsChildrenItemFile(*args, **kwargs)`
:   Media file. Use external URL or file upload.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemFileExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemFileFileUpload`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemFileExternal"></a>

`BlocksCreateParamsChildrenItemFileExternal(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemFile.external

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemFileFileUpload"></a>

`BlocksCreateParamsChildrenItemFileFileUpload(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemFile.file_upload

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading1"></a>

`BlocksCreateParamsChildrenItemHeading1(*args, **kwargs)`
:   Heading 1 block content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `is_toggleable: bool`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading1RichTextItem]`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading1RichTextItem"></a>

`BlocksCreateParamsChildrenItemHeading1RichTextItem(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading1.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading1RichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading1RichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading1RichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading1RichTextItemAnnotations"></a>

`BlocksCreateParamsChildrenItemHeading1RichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading1RichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading1RichTextItemEquation"></a>

`BlocksCreateParamsChildrenItemHeading1RichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading1RichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading1RichTextItemText"></a>

`BlocksCreateParamsChildrenItemHeading1RichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading1RichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading1RichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading1RichTextItemTextLink"></a>

`BlocksCreateParamsChildrenItemHeading1RichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading1RichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading2"></a>

`BlocksCreateParamsChildrenItemHeading2(*args, **kwargs)`
:   Heading 2 block content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `is_toggleable: bool`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading2RichTextItem]`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading2RichTextItem"></a>

`BlocksCreateParamsChildrenItemHeading2RichTextItem(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading2.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading2RichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading2RichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading2RichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading2RichTextItemAnnotations"></a>

`BlocksCreateParamsChildrenItemHeading2RichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading2RichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading2RichTextItemEquation"></a>

`BlocksCreateParamsChildrenItemHeading2RichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading2RichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading2RichTextItemText"></a>

`BlocksCreateParamsChildrenItemHeading2RichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading2RichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading2RichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading2RichTextItemTextLink"></a>

`BlocksCreateParamsChildrenItemHeading2RichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading2RichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading3"></a>

`BlocksCreateParamsChildrenItemHeading3(*args, **kwargs)`
:   Heading 3 block content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `is_toggleable: bool`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading3RichTextItem]`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading3RichTextItem"></a>

`BlocksCreateParamsChildrenItemHeading3RichTextItem(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading3.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading3RichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading3RichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading3RichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading3RichTextItemAnnotations"></a>

`BlocksCreateParamsChildrenItemHeading3RichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading3RichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading3RichTextItemEquation"></a>

`BlocksCreateParamsChildrenItemHeading3RichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading3RichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading3RichTextItemText"></a>

`BlocksCreateParamsChildrenItemHeading3RichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading3RichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemHeading3RichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemHeading3RichTextItemTextLink"></a>

`BlocksCreateParamsChildrenItemHeading3RichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemHeading3RichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemImage"></a>

`BlocksCreateParamsChildrenItemImage(*args, **kwargs)`
:   Media file. Use external URL or file upload.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemImageExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemImageFileUpload`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemImageExternal"></a>

`BlocksCreateParamsChildrenItemImageExternal(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemImage.external

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemImageFileUpload"></a>

`BlocksCreateParamsChildrenItemImageFileUpload(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemImage.file_upload

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemNumberedListItem"></a>

`BlocksCreateParamsChildrenItemNumberedListItem(*args, **kwargs)`
:   Numbered list item content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemNumberedListItemRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemNumberedListItemRichTextItem"></a>

`BlocksCreateParamsChildrenItemNumberedListItemRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemNumberedListItem.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemNumberedListItemRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemNumberedListItemRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemNumberedListItemRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemNumberedListItemRichTextItemAnnotations"></a>

`BlocksCreateParamsChildrenItemNumberedListItemRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemNumberedListItemRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemNumberedListItemRichTextItemEquation"></a>

`BlocksCreateParamsChildrenItemNumberedListItemRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemNumberedListItemRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemNumberedListItemRichTextItemText"></a>

`BlocksCreateParamsChildrenItemNumberedListItemRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemNumberedListItemRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemNumberedListItemRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemNumberedListItemRichTextItemTextLink"></a>

`BlocksCreateParamsChildrenItemNumberedListItemRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemNumberedListItemRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemParagraph"></a>

`BlocksCreateParamsChildrenItemParagraph(*args, **kwargs)`
:   Paragraph block content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemParagraphRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemParagraphRichTextItem"></a>

`BlocksCreateParamsChildrenItemParagraphRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemParagraph.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemParagraphRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemParagraphRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemParagraphRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemParagraphRichTextItemAnnotations"></a>

`BlocksCreateParamsChildrenItemParagraphRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemParagraphRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemParagraphRichTextItemEquation"></a>

`BlocksCreateParamsChildrenItemParagraphRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemParagraphRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemParagraphRichTextItemText"></a>

`BlocksCreateParamsChildrenItemParagraphRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemParagraphRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemParagraphRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemParagraphRichTextItemTextLink"></a>

`BlocksCreateParamsChildrenItemParagraphRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemParagraphRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemPdf"></a>

`BlocksCreateParamsChildrenItemPdf(*args, **kwargs)`
:   Media file. Use external URL or file upload.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemPdfExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemPdfFileUpload`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemPdfExternal"></a>

`BlocksCreateParamsChildrenItemPdfExternal(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemPdf.external

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemPdfFileUpload"></a>

`BlocksCreateParamsChildrenItemPdfFileUpload(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemPdf.file_upload

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemQuote"></a>

`BlocksCreateParamsChildrenItemQuote(*args, **kwargs)`
:   Quote block content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemQuoteRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemQuoteRichTextItem"></a>

`BlocksCreateParamsChildrenItemQuoteRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemQuote.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemQuoteRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemQuoteRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemQuoteRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemQuoteRichTextItemAnnotations"></a>

`BlocksCreateParamsChildrenItemQuoteRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemQuoteRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemQuoteRichTextItemEquation"></a>

`BlocksCreateParamsChildrenItemQuoteRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemQuoteRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemQuoteRichTextItemText"></a>

`BlocksCreateParamsChildrenItemQuoteRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemQuoteRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemQuoteRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemQuoteRichTextItemTextLink"></a>

`BlocksCreateParamsChildrenItemQuoteRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemQuoteRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemTableOfContents"></a>

`BlocksCreateParamsChildrenItemTableOfContents(*args, **kwargs)`
:   Table of contents block

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemToDo"></a>

`BlocksCreateParamsChildrenItemToDo(*args, **kwargs)`
:   To-do block content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `checked: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemToDoRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemToDoRichTextItem"></a>

`BlocksCreateParamsChildrenItemToDoRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemToDo.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemToDoRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemToDoRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemToDoRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemToDoRichTextItemAnnotations"></a>

`BlocksCreateParamsChildrenItemToDoRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemToDoRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemToDoRichTextItemEquation"></a>

`BlocksCreateParamsChildrenItemToDoRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemToDoRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemToDoRichTextItemText"></a>

`BlocksCreateParamsChildrenItemToDoRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemToDoRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemToDoRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemToDoRichTextItemTextLink"></a>

`BlocksCreateParamsChildrenItemToDoRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemToDoRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemToggle"></a>

`BlocksCreateParamsChildrenItemToggle(*args, **kwargs)`
:   Toggle block content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemToggleRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemToggleRichTextItem"></a>

`BlocksCreateParamsChildrenItemToggleRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemToggle.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemToggleRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemToggleRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemToggleRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemToggleRichTextItemAnnotations"></a>

`BlocksCreateParamsChildrenItemToggleRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemToggleRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemToggleRichTextItemEquation"></a>

`BlocksCreateParamsChildrenItemToggleRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemToggleRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemToggleRichTextItemText"></a>

`BlocksCreateParamsChildrenItemToggleRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemToggleRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemToggleRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemToggleRichTextItemTextLink"></a>

`BlocksCreateParamsChildrenItemToggleRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemToggleRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemVideo"></a>

`BlocksCreateParamsChildrenItemVideo(*args, **kwargs)`
:   Media file. Use external URL or file upload.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemVideoExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.BlocksCreateParamsChildrenItemVideoFileUpload`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemVideoExternal"></a>

`BlocksCreateParamsChildrenItemVideoExternal(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemVideo.external

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksCreateParamsChildrenItemVideoFileUpload"></a>

`BlocksCreateParamsChildrenItemVideoFileUpload(*args, **kwargs)`
:   Nested schema for BlocksCreateParamsChildrenItemVideo.file_upload

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="BlocksEqCondition"></a>

`BlocksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.notion.types.BlocksSearchFilter`
    :   The type of the None singleton.

<a id="BlocksFuzzyCondition"></a>

`BlocksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.notion.types.BlocksStringFilter`
    :   The type of the None singleton.

<a id="BlocksGetParams"></a>

`BlocksGetParams(*args, **kwargs)`
:   Parameters for blocks.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `block_id: str`
    :   The type of the None singleton.

<a id="BlocksGtCondition"></a>

`BlocksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.notion.types.BlocksSearchFilter`
    :   The type of the None singleton.

<a id="BlocksGteCondition"></a>

`BlocksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.notion.types.BlocksSearchFilter`
    :   The type of the None singleton.

<a id="BlocksInCondition"></a>

`BlocksInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.notion.types.BlocksInFilter`
    :   The type of the None singleton.

<a id="BlocksInFilter"></a>

`BlocksInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Indicates if the block is archived or not.

    `bookmark: list[dict[str, typing.Any]]`
    :   Represents a bookmark within the block

    `breadcrumb: list[dict[str, typing.Any]]`
    :   Represents a breadcrumb block.

    `bulleted_list_item: list[dict[str, typing.Any]]`
    :   Represents an item in a bulleted list.

    `callout: list[dict[str, typing.Any]]`
    :   Describes a callout message or content in the block

    `child_database: list[dict[str, typing.Any]]`
    :   Represents a child database block.

    `child_page: list[dict[str, typing.Any]]`
    :   Represents a child page block.

    `code: list[dict[str, typing.Any]]`
    :   Contains code snippets or blocks in the block content

    `column: list[dict[str, typing.Any]]`
    :   Represents a column block.

    `column_list: list[dict[str, typing.Any]]`
    :   Represents a list of columns.

    `created_by: list[dict[str, typing.Any]]`
    :   The user who created the block.

    `created_time: list[str]`
    :   The timestamp when the block was created.

    `divider: list[dict[str, typing.Any]]`
    :   Represents a divider block.

    `embed: list[dict[str, typing.Any]]`
    :   Contains embedded content such as videos, tweets, etc.

    `equation: list[dict[str, typing.Any]]`
    :   Represents an equation or mathematical formula in the block

    `file: list[dict[str, typing.Any]]`
    :   Represents a file block.

    `has_children: list[bool]`
    :   Indicates if the block has children or not.

    `heading_1: list[dict[str, typing.Any]]`
    :   Represents a level 1 heading.

    `heading_2: list[dict[str, typing.Any]]`
    :   Represents a level 2 heading.

    `heading_3: list[dict[str, typing.Any]]`
    :   Represents a level 3 heading.

    `id: list[str]`
    :   The unique identifier of the block.

    `image: list[dict[str, typing.Any]]`
    :   Represents an image block.

    `last_edited_by: list[dict[str, typing.Any]]`
    :   The user who last edited the block.

    `last_edited_time: list[str]`
    :   The timestamp when the block was last edited.

    `link_preview: list[dict[str, typing.Any]]`
    :   Displays a preview of an external link within the block

    `link_to_page: list[dict[str, typing.Any]]`
    :   Provides a link to another page within the block

    `numbered_list_item: list[dict[str, typing.Any]]`
    :   Represents an item in a numbered list.

    `object_: list[dict[str, typing.Any]]`
    :   Represents an object block.

    `paragraph: list[dict[str, typing.Any]]`
    :   Represents a paragraph block.

    `parent: list[dict[str, typing.Any]]`
    :   The parent block of the current block.

    `pdf: list[dict[str, typing.Any]]`
    :   Represents a PDF document block.

    `quote: list[dict[str, typing.Any]]`
    :   Represents a quote block.

    `synced_block: list[dict[str, typing.Any]]`
    :   Represents a block synced from another source

    `table: list[dict[str, typing.Any]]`
    :   Represents a table within the block

    `table_of_contents: list[dict[str, typing.Any]]`
    :   Contains information regarding the table of contents

    `table_row: list[dict[str, typing.Any]]`
    :   Represents a row in a table within the block

    `template: list[dict[str, typing.Any]]`
    :   Specifies a template used within the block

    `to_do: list[dict[str, typing.Any]]`
    :   Represents a to-do list or task content

    `toggle: list[dict[str, typing.Any]]`
    :   Represents a toggle block.

    `type_: list[dict[str, typing.Any]]`
    :   The type of the block.

    `unsupported: list[dict[str, typing.Any]]`
    :   Represents an unsupported block.

    `video: list[dict[str, typing.Any]]`
    :   Represents a video block.

<a id="BlocksKeywordCondition"></a>

`BlocksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.notion.types.BlocksStringFilter`
    :   The type of the None singleton.

<a id="BlocksLikeCondition"></a>

`BlocksLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.notion.types.BlocksStringFilter`
    :   The type of the None singleton.

<a id="BlocksListParams"></a>

`BlocksListParams(*args, **kwargs)`
:   Parameters for blocks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `block_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `start_cursor: str`
    :   The type of the None singleton.

<a id="BlocksLtCondition"></a>

`BlocksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.notion.types.BlocksSearchFilter`
    :   The type of the None singleton.

<a id="BlocksLteCondition"></a>

`BlocksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.notion.types.BlocksSearchFilter`
    :   The type of the None singleton.

<a id="BlocksNeqCondition"></a>

`BlocksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.notion.types.BlocksSearchFilter`
    :   The type of the None singleton.

<a id="BlocksNotCondition"></a>

`BlocksNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.notion.types.BlocksEqCondition | airbyte_agent_sdk.connectors.notion.types.BlocksNeqCondition | airbyte_agent_sdk.connectors.notion.types.BlocksGtCondition | airbyte_agent_sdk.connectors.notion.types.BlocksGteCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLtCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLteCondition | airbyte_agent_sdk.connectors.notion.types.BlocksInCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLikeCondition | airbyte_agent_sdk.connectors.notion.types.BlocksFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.BlocksKeywordCondition | airbyte_agent_sdk.connectors.notion.types.BlocksContainsCondition | airbyte_agent_sdk.connectors.notion.types.BlocksNotCondition | airbyte_agent_sdk.connectors.notion.types.BlocksAndCondition | airbyte_agent_sdk.connectors.notion.types.BlocksOrCondition | airbyte_agent_sdk.connectors.notion.types.BlocksAnyCondition`
    :   The type of the None singleton.

<a id="BlocksOrCondition"></a>

`BlocksOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.notion.types.BlocksEqCondition | airbyte_agent_sdk.connectors.notion.types.BlocksNeqCondition | airbyte_agent_sdk.connectors.notion.types.BlocksGtCondition | airbyte_agent_sdk.connectors.notion.types.BlocksGteCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLtCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLteCondition | airbyte_agent_sdk.connectors.notion.types.BlocksInCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLikeCondition | airbyte_agent_sdk.connectors.notion.types.BlocksFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.BlocksKeywordCondition | airbyte_agent_sdk.connectors.notion.types.BlocksContainsCondition | airbyte_agent_sdk.connectors.notion.types.BlocksNotCondition | airbyte_agent_sdk.connectors.notion.types.BlocksAndCondition | airbyte_agent_sdk.connectors.notion.types.BlocksOrCondition | airbyte_agent_sdk.connectors.notion.types.BlocksAnyCondition]`
    :   The type of the None singleton.

<a id="BlocksSearchFilter"></a>

`BlocksSearchFilter(*args, **kwargs)`
:   Available fields for filtering blocks search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="BlocksSearchQuery"></a>

`BlocksSearchQuery(*args, **kwargs)`
:   Search query for blocks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.notion.types.BlocksEqCondition | airbyte_agent_sdk.connectors.notion.types.BlocksNeqCondition | airbyte_agent_sdk.connectors.notion.types.BlocksGtCondition | airbyte_agent_sdk.connectors.notion.types.BlocksGteCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLtCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLteCondition | airbyte_agent_sdk.connectors.notion.types.BlocksInCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLikeCondition | airbyte_agent_sdk.connectors.notion.types.BlocksFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.BlocksKeywordCondition | airbyte_agent_sdk.connectors.notion.types.BlocksContainsCondition | airbyte_agent_sdk.connectors.notion.types.BlocksNotCondition | airbyte_agent_sdk.connectors.notion.types.BlocksAndCondition | airbyte_agent_sdk.connectors.notion.types.BlocksOrCondition | airbyte_agent_sdk.connectors.notion.types.BlocksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.notion.types.BlocksSortFilter]`
    :   The type of the None singleton.

<a id="BlocksSortFilter"></a>

`BlocksSortFilter(*args, **kwargs)`
:   Available fields for sorting blocks search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Indicates if the block is archived or not.

    `bookmark: Literal['asc', 'desc']`
    :   Represents a bookmark within the block

    `breadcrumb: Literal['asc', 'desc']`
    :   Represents a breadcrumb block.

    `bulleted_list_item: Literal['asc', 'desc']`
    :   Represents an item in a bulleted list.

    `callout: Literal['asc', 'desc']`
    :   Describes a callout message or content in the block

    `child_database: Literal['asc', 'desc']`
    :   Represents a child database block.

    `child_page: Literal['asc', 'desc']`
    :   Represents a child page block.

    `code: Literal['asc', 'desc']`
    :   Contains code snippets or blocks in the block content

    `column: Literal['asc', 'desc']`
    :   Represents a column block.

    `column_list: Literal['asc', 'desc']`
    :   Represents a list of columns.

    `created_by: Literal['asc', 'desc']`
    :   The user who created the block.

    `created_time: Literal['asc', 'desc']`
    :   The timestamp when the block was created.

    `divider: Literal['asc', 'desc']`
    :   Represents a divider block.

    `embed: Literal['asc', 'desc']`
    :   Contains embedded content such as videos, tweets, etc.

    `equation: Literal['asc', 'desc']`
    :   Represents an equation or mathematical formula in the block

    `file: Literal['asc', 'desc']`
    :   Represents a file block.

    `has_children: Literal['asc', 'desc']`
    :   Indicates if the block has children or not.

    `heading_1: Literal['asc', 'desc']`
    :   Represents a level 1 heading.

    `heading_2: Literal['asc', 'desc']`
    :   Represents a level 2 heading.

    `heading_3: Literal['asc', 'desc']`
    :   Represents a level 3 heading.

    `id: Literal['asc', 'desc']`
    :   The unique identifier of the block.

    `image: Literal['asc', 'desc']`
    :   Represents an image block.

    `last_edited_by: Literal['asc', 'desc']`
    :   The user who last edited the block.

    `last_edited_time: Literal['asc', 'desc']`
    :   The timestamp when the block was last edited.

    `link_preview: Literal['asc', 'desc']`
    :   Displays a preview of an external link within the block

    `link_to_page: Literal['asc', 'desc']`
    :   Provides a link to another page within the block

    `numbered_list_item: Literal['asc', 'desc']`
    :   Represents an item in a numbered list.

    `object_: Literal['asc', 'desc']`
    :   Represents an object block.

    `paragraph: Literal['asc', 'desc']`
    :   Represents a paragraph block.

    `parent: Literal['asc', 'desc']`
    :   The parent block of the current block.

    `pdf: Literal['asc', 'desc']`
    :   Represents a PDF document block.

    `quote: Literal['asc', 'desc']`
    :   Represents a quote block.

    `synced_block: Literal['asc', 'desc']`
    :   Represents a block synced from another source

    `table: Literal['asc', 'desc']`
    :   Represents a table within the block

    `table_of_contents: Literal['asc', 'desc']`
    :   Contains information regarding the table of contents

    `table_row: Literal['asc', 'desc']`
    :   Represents a row in a table within the block

    `template: Literal['asc', 'desc']`
    :   Specifies a template used within the block

    `to_do: Literal['asc', 'desc']`
    :   Represents a to-do list or task content

    `toggle: Literal['asc', 'desc']`
    :   Represents a toggle block.

    `type_: Literal['asc', 'desc']`
    :   The type of the block.

    `unsupported: Literal['asc', 'desc']`
    :   Represents an unsupported block.

    `video: Literal['asc', 'desc']`
    :   Represents a video block.

<a id="BlocksStringFilter"></a>

`BlocksStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Indicates if the block is archived or not.

    `bookmark: str`
    :   Represents a bookmark within the block

    `breadcrumb: str`
    :   Represents a breadcrumb block.

    `bulleted_list_item: str`
    :   Represents an item in a bulleted list.

    `callout: str`
    :   Describes a callout message or content in the block

    `child_database: str`
    :   Represents a child database block.

    `child_page: str`
    :   Represents a child page block.

    `code: str`
    :   Contains code snippets or blocks in the block content

    `column: str`
    :   Represents a column block.

    `column_list: str`
    :   Represents a list of columns.

    `created_by: str`
    :   The user who created the block.

    `created_time: str`
    :   The timestamp when the block was created.

    `divider: str`
    :   Represents a divider block.

    `embed: str`
    :   Contains embedded content such as videos, tweets, etc.

    `equation: str`
    :   Represents an equation or mathematical formula in the block

    `file: str`
    :   Represents a file block.

    `has_children: str`
    :   Indicates if the block has children or not.

    `heading_1: str`
    :   Represents a level 1 heading.

    `heading_2: str`
    :   Represents a level 2 heading.

    `heading_3: str`
    :   Represents a level 3 heading.

    `id: str`
    :   The unique identifier of the block.

    `image: str`
    :   Represents an image block.

    `last_edited_by: str`
    :   The user who last edited the block.

    `last_edited_time: str`
    :   The timestamp when the block was last edited.

    `link_preview: str`
    :   Displays a preview of an external link within the block

    `link_to_page: str`
    :   Provides a link to another page within the block

    `numbered_list_item: str`
    :   Represents an item in a numbered list.

    `object_: str`
    :   Represents an object block.

    `paragraph: str`
    :   Represents a paragraph block.

    `parent: str`
    :   The parent block of the current block.

    `pdf: str`
    :   Represents a PDF document block.

    `quote: str`
    :   Represents a quote block.

    `synced_block: str`
    :   Represents a block synced from another source

    `table: str`
    :   Represents a table within the block

    `table_of_contents: str`
    :   Contains information regarding the table of contents

    `table_row: str`
    :   Represents a row in a table within the block

    `template: str`
    :   Specifies a template used within the block

    `to_do: str`
    :   Represents a to-do list or task content

    `toggle: str`
    :   Represents a toggle block.

    `type_: str`
    :   The type of the block.

    `unsupported: str`
    :   Represents an unsupported block.

    `video: str`
    :   Represents a video block.

<a id="BlocksUpdateParams"></a>

`BlocksUpdateParams(*args, **kwargs)`
:   Parameters for blocks.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `audio: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsAudio`
    :   The type of the None singleton.

    `block_id: str`
    :   The type of the None singleton.

    `bookmark: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsBookmark`
    :   The type of the None singleton.

    `bulleted_list_item: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsBulletedListItem`
    :   The type of the None singleton.

    `callout: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCallout`
    :   The type of the None singleton.

    `code: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCode`
    :   The type of the None singleton.

    `embed: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsEmbed`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsEquation`
    :   The type of the None singleton.

    `file: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsFile`
    :   The type of the None singleton.

    `heading_1: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading1`
    :   The type of the None singleton.

    `heading_2: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading2`
    :   The type of the None singleton.

    `heading_3: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading3`
    :   The type of the None singleton.

    `image: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsImage`
    :   The type of the None singleton.

    `numbered_list_item: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsNumberedListItem`
    :   The type of the None singleton.

    `paragraph: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsParagraph`
    :   The type of the None singleton.

    `pdf: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsPdf`
    :   The type of the None singleton.

    `quote: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsQuote`
    :   The type of the None singleton.

    `table: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsTable`
    :   The type of the None singleton.

    `to_do: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsToDo`
    :   The type of the None singleton.

    `toggle: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsToggle`
    :   The type of the None singleton.

    `video: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsVideo`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsAudio"></a>

`BlocksUpdateParamsAudio(*args, **kwargs)`
:   Media file. Use external URL or file upload.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsAudioExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsAudioFileUpload`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsAudioExternal"></a>

`BlocksUpdateParamsAudioExternal(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsAudio.external

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsAudioFileUpload"></a>

`BlocksUpdateParamsAudioFileUpload(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsAudio.file_upload

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsBookmark"></a>

`BlocksUpdateParamsBookmark(*args, **kwargs)`
:   Updated bookmark

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `caption: list[airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsBookmarkCaptionItem]`
    :   The type of the None singleton.

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsBookmarkCaptionItem"></a>

`BlocksUpdateParamsBookmarkCaptionItem(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsBookmark.caption_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsBookmarkCaptionItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsBookmarkCaptionItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsBookmarkCaptionItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsBookmarkCaptionItemAnnotations"></a>

`BlocksUpdateParamsBookmarkCaptionItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsBookmarkCaptionItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsBookmarkCaptionItemEquation"></a>

`BlocksUpdateParamsBookmarkCaptionItemEquation(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsBookmarkCaptionItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsBookmarkCaptionItemText"></a>

`BlocksUpdateParamsBookmarkCaptionItemText(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsBookmarkCaptionItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsBookmarkCaptionItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsBookmarkCaptionItemTextLink"></a>

`BlocksUpdateParamsBookmarkCaptionItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsBookmarkCaptionItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsBulletedListItem"></a>

`BlocksUpdateParamsBulletedListItem(*args, **kwargs)`
:   Updated bulleted list item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsBulletedListItemRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsBulletedListItemRichTextItem"></a>

`BlocksUpdateParamsBulletedListItemRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsBulletedListItem.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsBulletedListItemRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsBulletedListItemRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsBulletedListItemRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsBulletedListItemRichTextItemAnnotations"></a>

`BlocksUpdateParamsBulletedListItemRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsBulletedListItemRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsBulletedListItemRichTextItemEquation"></a>

`BlocksUpdateParamsBulletedListItemRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsBulletedListItemRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsBulletedListItemRichTextItemText"></a>

`BlocksUpdateParamsBulletedListItemRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsBulletedListItemRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsBulletedListItemRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsBulletedListItemRichTextItemTextLink"></a>

`BlocksUpdateParamsBulletedListItemRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsBulletedListItemRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCallout"></a>

`BlocksUpdateParamsCallout(*args, **kwargs)`
:   Updated callout content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `icon: dict[str, typing.Any]`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCalloutRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCalloutRichTextItem"></a>

`BlocksUpdateParamsCalloutRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCallout.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCalloutRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCalloutRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCalloutRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCalloutRichTextItemAnnotations"></a>

`BlocksUpdateParamsCalloutRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCalloutRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCalloutRichTextItemEquation"></a>

`BlocksUpdateParamsCalloutRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCalloutRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCalloutRichTextItemText"></a>

`BlocksUpdateParamsCalloutRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCalloutRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCalloutRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCalloutRichTextItemTextLink"></a>

`BlocksUpdateParamsCalloutRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCalloutRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCode"></a>

`BlocksUpdateParamsCode(*args, **kwargs)`
:   Updated code block content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `caption: list[airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCodeCaptionItem]`
    :   The type of the None singleton.

    `language: str`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCodeRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCodeCaptionItem"></a>

`BlocksUpdateParamsCodeCaptionItem(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCode.caption_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCodeCaptionItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCodeCaptionItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCodeCaptionItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCodeCaptionItemAnnotations"></a>

`BlocksUpdateParamsCodeCaptionItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCodeCaptionItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCodeCaptionItemEquation"></a>

`BlocksUpdateParamsCodeCaptionItemEquation(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCodeCaptionItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCodeCaptionItemText"></a>

`BlocksUpdateParamsCodeCaptionItemText(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCodeCaptionItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCodeCaptionItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCodeCaptionItemTextLink"></a>

`BlocksUpdateParamsCodeCaptionItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCodeCaptionItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCodeRichTextItem"></a>

`BlocksUpdateParamsCodeRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCode.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCodeRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCodeRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCodeRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCodeRichTextItemAnnotations"></a>

`BlocksUpdateParamsCodeRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCodeRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCodeRichTextItemEquation"></a>

`BlocksUpdateParamsCodeRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCodeRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCodeRichTextItemText"></a>

`BlocksUpdateParamsCodeRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCodeRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsCodeRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsCodeRichTextItemTextLink"></a>

`BlocksUpdateParamsCodeRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsCodeRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsEmbed"></a>

`BlocksUpdateParamsEmbed(*args, **kwargs)`
:   Updated embed

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsEquation"></a>

`BlocksUpdateParamsEquation(*args, **kwargs)`
:   Updated equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsFile"></a>

`BlocksUpdateParamsFile(*args, **kwargs)`
:   Media file. Use external URL or file upload.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsFileExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsFileFileUpload`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsFileExternal"></a>

`BlocksUpdateParamsFileExternal(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsFile.external

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsFileFileUpload"></a>

`BlocksUpdateParamsFileFileUpload(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsFile.file_upload

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading1"></a>

`BlocksUpdateParamsHeading1(*args, **kwargs)`
:   Updated heading 1 content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `is_toggleable: bool`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading1RichTextItem]`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading1RichTextItem"></a>

`BlocksUpdateParamsHeading1RichTextItem(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading1.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading1RichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading1RichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading1RichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading1RichTextItemAnnotations"></a>

`BlocksUpdateParamsHeading1RichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading1RichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading1RichTextItemEquation"></a>

`BlocksUpdateParamsHeading1RichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading1RichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading1RichTextItemText"></a>

`BlocksUpdateParamsHeading1RichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading1RichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading1RichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading1RichTextItemTextLink"></a>

`BlocksUpdateParamsHeading1RichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading1RichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading2"></a>

`BlocksUpdateParamsHeading2(*args, **kwargs)`
:   Updated heading 2 content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `is_toggleable: bool`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading2RichTextItem]`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading2RichTextItem"></a>

`BlocksUpdateParamsHeading2RichTextItem(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading2.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading2RichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading2RichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading2RichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading2RichTextItemAnnotations"></a>

`BlocksUpdateParamsHeading2RichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading2RichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading2RichTextItemEquation"></a>

`BlocksUpdateParamsHeading2RichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading2RichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading2RichTextItemText"></a>

`BlocksUpdateParamsHeading2RichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading2RichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading2RichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading2RichTextItemTextLink"></a>

`BlocksUpdateParamsHeading2RichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading2RichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading3"></a>

`BlocksUpdateParamsHeading3(*args, **kwargs)`
:   Updated heading 3 content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `is_toggleable: bool`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading3RichTextItem]`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading3RichTextItem"></a>

`BlocksUpdateParamsHeading3RichTextItem(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading3.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading3RichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading3RichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading3RichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading3RichTextItemAnnotations"></a>

`BlocksUpdateParamsHeading3RichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading3RichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading3RichTextItemEquation"></a>

`BlocksUpdateParamsHeading3RichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading3RichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading3RichTextItemText"></a>

`BlocksUpdateParamsHeading3RichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading3RichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsHeading3RichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsHeading3RichTextItemTextLink"></a>

`BlocksUpdateParamsHeading3RichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsHeading3RichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsImage"></a>

`BlocksUpdateParamsImage(*args, **kwargs)`
:   Media file. Use external URL or file upload.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsImageExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsImageFileUpload`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsImageExternal"></a>

`BlocksUpdateParamsImageExternal(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsImage.external

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsImageFileUpload"></a>

`BlocksUpdateParamsImageFileUpload(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsImage.file_upload

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsNumberedListItem"></a>

`BlocksUpdateParamsNumberedListItem(*args, **kwargs)`
:   Updated numbered list item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsNumberedListItemRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsNumberedListItemRichTextItem"></a>

`BlocksUpdateParamsNumberedListItemRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsNumberedListItem.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsNumberedListItemRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsNumberedListItemRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsNumberedListItemRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsNumberedListItemRichTextItemAnnotations"></a>

`BlocksUpdateParamsNumberedListItemRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsNumberedListItemRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsNumberedListItemRichTextItemEquation"></a>

`BlocksUpdateParamsNumberedListItemRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsNumberedListItemRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsNumberedListItemRichTextItemText"></a>

`BlocksUpdateParamsNumberedListItemRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsNumberedListItemRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsNumberedListItemRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsNumberedListItemRichTextItemTextLink"></a>

`BlocksUpdateParamsNumberedListItemRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsNumberedListItemRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsParagraph"></a>

`BlocksUpdateParamsParagraph(*args, **kwargs)`
:   Updated paragraph content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsParagraphRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsParagraphRichTextItem"></a>

`BlocksUpdateParamsParagraphRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsParagraph.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsParagraphRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsParagraphRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsParagraphRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsParagraphRichTextItemAnnotations"></a>

`BlocksUpdateParamsParagraphRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsParagraphRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsParagraphRichTextItemEquation"></a>

`BlocksUpdateParamsParagraphRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsParagraphRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsParagraphRichTextItemText"></a>

`BlocksUpdateParamsParagraphRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsParagraphRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsParagraphRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsParagraphRichTextItemTextLink"></a>

`BlocksUpdateParamsParagraphRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsParagraphRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsPdf"></a>

`BlocksUpdateParamsPdf(*args, **kwargs)`
:   Media file. Use external URL or file upload.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsPdfExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsPdfFileUpload`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsPdfExternal"></a>

`BlocksUpdateParamsPdfExternal(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsPdf.external

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsPdfFileUpload"></a>

`BlocksUpdateParamsPdfFileUpload(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsPdf.file_upload

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsQuote"></a>

`BlocksUpdateParamsQuote(*args, **kwargs)`
:   Updated quote content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsQuoteRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsQuoteRichTextItem"></a>

`BlocksUpdateParamsQuoteRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsQuote.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsQuoteRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsQuoteRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsQuoteRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsQuoteRichTextItemAnnotations"></a>

`BlocksUpdateParamsQuoteRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsQuoteRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsQuoteRichTextItemEquation"></a>

`BlocksUpdateParamsQuoteRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsQuoteRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsQuoteRichTextItemText"></a>

`BlocksUpdateParamsQuoteRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsQuoteRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsQuoteRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsQuoteRichTextItemTextLink"></a>

`BlocksUpdateParamsQuoteRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsQuoteRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsTable"></a>

`BlocksUpdateParamsTable(*args, **kwargs)`
:   Updated table properties

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `has_column_header: bool`
    :   The type of the None singleton.

    `has_row_header: bool`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsToDo"></a>

`BlocksUpdateParamsToDo(*args, **kwargs)`
:   Updated to-do content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `checked: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsToDoRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsToDoRichTextItem"></a>

`BlocksUpdateParamsToDoRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsToDo.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsToDoRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsToDoRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsToDoRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsToDoRichTextItemAnnotations"></a>

`BlocksUpdateParamsToDoRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsToDoRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsToDoRichTextItemEquation"></a>

`BlocksUpdateParamsToDoRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsToDoRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsToDoRichTextItemText"></a>

`BlocksUpdateParamsToDoRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsToDoRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsToDoRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsToDoRichTextItemTextLink"></a>

`BlocksUpdateParamsToDoRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsToDoRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsToggle"></a>

`BlocksUpdateParamsToggle(*args, **kwargs)`
:   Updated toggle content

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsToggleRichTextItem]`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsToggleRichTextItem"></a>

`BlocksUpdateParamsToggleRichTextItem(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsToggle.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsToggleRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsToggleRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsToggleRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsToggleRichTextItemAnnotations"></a>

`BlocksUpdateParamsToggleRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsToggleRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsToggleRichTextItemEquation"></a>

`BlocksUpdateParamsToggleRichTextItemEquation(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsToggleRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsToggleRichTextItemText"></a>

`BlocksUpdateParamsToggleRichTextItemText(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsToggleRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsToggleRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsToggleRichTextItemTextLink"></a>

`BlocksUpdateParamsToggleRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsToggleRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsVideo"></a>

`BlocksUpdateParamsVideo(*args, **kwargs)`
:   Media file. Use external URL or file upload.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsVideoExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.BlocksUpdateParamsVideoFileUpload`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsVideoExternal"></a>

`BlocksUpdateParamsVideoExternal(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsVideo.external

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="BlocksUpdateParamsVideoFileUpload"></a>

`BlocksUpdateParamsVideoFileUpload(*args, **kwargs)`
:   Nested schema for BlocksUpdateParamsVideo.file_upload

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CommentsAndCondition"></a>

`CommentsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.notion.types.CommentsEqCondition | airbyte_agent_sdk.connectors.notion.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.notion.types.CommentsGtCondition | airbyte_agent_sdk.connectors.notion.types.CommentsGteCondition | airbyte_agent_sdk.connectors.notion.types.CommentsLtCondition | airbyte_agent_sdk.connectors.notion.types.CommentsLteCondition | airbyte_agent_sdk.connectors.notion.types.CommentsInCondition | airbyte_agent_sdk.connectors.notion.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.notion.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.notion.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.notion.types.CommentsNotCondition | airbyte_agent_sdk.connectors.notion.types.CommentsAndCondition | airbyte_agent_sdk.connectors.notion.types.CommentsOrCondition | airbyte_agent_sdk.connectors.notion.types.CommentsAnyCondition]`
    :   The type of the None singleton.

<a id="CommentsAnyCondition"></a>

`CommentsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.notion.types.CommentsAnyValueFilter`
    :   The type of the None singleton.

<a id="CommentsAnyValueFilter"></a>

`CommentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_by: Any`
    :   User who created the comment.

    `created_time: Any`
    :   Date and time when the comment was created.

    `discussion_id: Any`
    :   Discussion thread ID.

    `id: Any`
    :   Unique identifier for the comment.

    `last_edited_time: Any`
    :   Date and time when the comment was last edited.

    `object_: Any`
    :   Always comment.

    `parent: Any`
    :   Parent of the comment.

    `rich_text: Any`
    :   Content of the comment as rich text.

<a id="CommentsContainsCondition"></a>

`CommentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.notion.types.CommentsAnyValueFilter`
    :   The type of the None singleton.

<a id="CommentsCreateParams"></a>

`CommentsCreateParams(*args, **kwargs)`
:   Parameters for comments.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `discussion_id: str`
    :   The type of the None singleton.

    `parent: dict[str, typing.Any]`
    :   The type of the None singleton.

    `rich_text: list[airbyte_agent_sdk.connectors.notion.types.CommentsCreateParamsRichTextItem]`
    :   The type of the None singleton.

<a id="CommentsCreateParamsRichTextItem"></a>

`CommentsCreateParamsRichTextItem(*args, **kwargs)`
:   Nested schema for CommentsCreateParams.rich_text_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.CommentsCreateParamsRichTextItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.CommentsCreateParamsRichTextItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.CommentsCreateParamsRichTextItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="CommentsCreateParamsRichTextItemAnnotations"></a>

`CommentsCreateParamsRichTextItemAnnotations(*args, **kwargs)`
:   Nested schema for CommentsCreateParamsRichTextItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="CommentsCreateParamsRichTextItemEquation"></a>

`CommentsCreateParamsRichTextItemEquation(*args, **kwargs)`
:   Nested schema for CommentsCreateParamsRichTextItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="CommentsCreateParamsRichTextItemText"></a>

`CommentsCreateParamsRichTextItemText(*args, **kwargs)`
:   Nested schema for CommentsCreateParamsRichTextItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.CommentsCreateParamsRichTextItemTextLink | None`
    :   The type of the None singleton.

<a id="CommentsCreateParamsRichTextItemTextLink"></a>

`CommentsCreateParamsRichTextItemTextLink(*args, **kwargs)`
:   Nested schema for CommentsCreateParamsRichTextItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="CommentsEqCondition"></a>

`CommentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.notion.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsFuzzyCondition"></a>

`CommentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.notion.types.CommentsStringFilter`
    :   The type of the None singleton.

<a id="CommentsGtCondition"></a>

`CommentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.notion.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsGteCondition"></a>

`CommentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.notion.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsInCondition"></a>

`CommentsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.notion.types.CommentsInFilter`
    :   The type of the None singleton.

<a id="CommentsInFilter"></a>

`CommentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_by: list[dict[str, typing.Any]]`
    :   User who created the comment.

    `created_time: list[str]`
    :   Date and time when the comment was created.

    `discussion_id: list[str]`
    :   Discussion thread ID.

    `id: list[str]`
    :   Unique identifier for the comment.

    `last_edited_time: list[str]`
    :   Date and time when the comment was last edited.

    `object_: list[str]`
    :   Always comment.

    `parent: list[dict[str, typing.Any]]`
    :   Parent of the comment.

    `rich_text: list[list[typing.Any]]`
    :   Content of the comment as rich text.

<a id="CommentsKeywordCondition"></a>

`CommentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.notion.types.CommentsStringFilter`
    :   The type of the None singleton.

<a id="CommentsLikeCondition"></a>

`CommentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.notion.types.CommentsStringFilter`
    :   The type of the None singleton.

<a id="CommentsListParams"></a>

`CommentsListParams(*args, **kwargs)`
:   Parameters for comments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `block_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `start_cursor: str`
    :   The type of the None singleton.

<a id="CommentsLtCondition"></a>

`CommentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.notion.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsLteCondition"></a>

`CommentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.notion.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsNeqCondition"></a>

`CommentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.notion.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsNotCondition"></a>

`CommentsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.notion.types.CommentsEqCondition | airbyte_agent_sdk.connectors.notion.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.notion.types.CommentsGtCondition | airbyte_agent_sdk.connectors.notion.types.CommentsGteCondition | airbyte_agent_sdk.connectors.notion.types.CommentsLtCondition | airbyte_agent_sdk.connectors.notion.types.CommentsLteCondition | airbyte_agent_sdk.connectors.notion.types.CommentsInCondition | airbyte_agent_sdk.connectors.notion.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.notion.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.notion.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.notion.types.CommentsNotCondition | airbyte_agent_sdk.connectors.notion.types.CommentsAndCondition | airbyte_agent_sdk.connectors.notion.types.CommentsOrCondition | airbyte_agent_sdk.connectors.notion.types.CommentsAnyCondition`
    :   The type of the None singleton.

<a id="CommentsOrCondition"></a>

`CommentsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.notion.types.CommentsEqCondition | airbyte_agent_sdk.connectors.notion.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.notion.types.CommentsGtCondition | airbyte_agent_sdk.connectors.notion.types.CommentsGteCondition | airbyte_agent_sdk.connectors.notion.types.CommentsLtCondition | airbyte_agent_sdk.connectors.notion.types.CommentsLteCondition | airbyte_agent_sdk.connectors.notion.types.CommentsInCondition | airbyte_agent_sdk.connectors.notion.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.notion.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.notion.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.notion.types.CommentsNotCondition | airbyte_agent_sdk.connectors.notion.types.CommentsAndCondition | airbyte_agent_sdk.connectors.notion.types.CommentsOrCondition | airbyte_agent_sdk.connectors.notion.types.CommentsAnyCondition]`
    :   The type of the None singleton.

<a id="CommentsSearchFilter"></a>

`CommentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering comments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

    `object_: str | None`
    :   Always comment.

    `parent: dict[str, typing.Any] | None`
    :   Parent of the comment.

    `rich_text: list[typing.Any] | None`
    :   Content of the comment as rich text.

<a id="CommentsSearchQuery"></a>

`CommentsSearchQuery(*args, **kwargs)`
:   Search query for comments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.notion.types.CommentsEqCondition | airbyte_agent_sdk.connectors.notion.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.notion.types.CommentsGtCondition | airbyte_agent_sdk.connectors.notion.types.CommentsGteCondition | airbyte_agent_sdk.connectors.notion.types.CommentsLtCondition | airbyte_agent_sdk.connectors.notion.types.CommentsLteCondition | airbyte_agent_sdk.connectors.notion.types.CommentsInCondition | airbyte_agent_sdk.connectors.notion.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.notion.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.notion.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.notion.types.CommentsNotCondition | airbyte_agent_sdk.connectors.notion.types.CommentsAndCondition | airbyte_agent_sdk.connectors.notion.types.CommentsOrCondition | airbyte_agent_sdk.connectors.notion.types.CommentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.notion.types.CommentsSortFilter]`
    :   The type of the None singleton.

<a id="CommentsSortFilter"></a>

`CommentsSortFilter(*args, **kwargs)`
:   Available fields for sorting comments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_by: Literal['asc', 'desc']`
    :   User who created the comment.

    `created_time: Literal['asc', 'desc']`
    :   Date and time when the comment was created.

    `discussion_id: Literal['asc', 'desc']`
    :   Discussion thread ID.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the comment.

    `last_edited_time: Literal['asc', 'desc']`
    :   Date and time when the comment was last edited.

    `object_: Literal['asc', 'desc']`
    :   Always comment.

    `parent: Literal['asc', 'desc']`
    :   Parent of the comment.

    `rich_text: Literal['asc', 'desc']`
    :   Content of the comment as rich text.

<a id="CommentsStringFilter"></a>

`CommentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_by: str`
    :   User who created the comment.

    `created_time: str`
    :   Date and time when the comment was created.

    `discussion_id: str`
    :   Discussion thread ID.

    `id: str`
    :   Unique identifier for the comment.

    `last_edited_time: str`
    :   Date and time when the comment was last edited.

    `object_: str`
    :   Always comment.

    `parent: str`
    :   Parent of the comment.

    `rich_text: str`
    :   Content of the comment as rich text.

<a id="DataSourcesAndCondition"></a>

`DataSourcesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.notion.types.DataSourcesEqCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesNeqCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesGtCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesGteCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLtCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLteCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesInCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLikeCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesKeywordCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesContainsCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesNotCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesAndCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesOrCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesAnyCondition]`
    :   The type of the None singleton.

<a id="DataSourcesAnyCondition"></a>

`DataSourcesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.notion.types.DataSourcesAnyValueFilter`
    :   The type of the None singleton.

<a id="DataSourcesAnyValueFilter"></a>

`DataSourcesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Indicates if the data source is archived or not.

    `cover: Any`
    :   URL or reference to the cover image of the data source.

    `created_by: Any`
    :   The user who created the data source.

    `created_time: Any`
    :   The timestamp when the data source was created.

    `database_parent: Any`
    :   The grandparent of the data source (parent of the database).

    `description: Any`
    :   Description text associated with the data source.

    `icon: Any`
    :   URL or reference to the icon of the data source.

    `id: Any`
    :   Unique identifier of the data source.

    `is_inline: Any`
    :   Indicates if the data source is displayed inline.

    `last_edited_by: Any`
    :   The user who last edited the data source.

    `last_edited_time: Any`
    :   The timestamp when the data source was last edited.

    `object_: Any`
    :   The type of object (data_source).

    `parent: Any`
    :   The parent database of the data source.

    `properties: Any`
    :   Schema of properties for the data source.

    `public_url: Any`
    :   Public URL to access the data source.

    `title: Any`
    :   Title or name of the data source.

    `url: Any`
    :   URL or reference to access the data source.

<a id="DataSourcesContainsCondition"></a>

`DataSourcesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.notion.types.DataSourcesAnyValueFilter`
    :   The type of the None singleton.

<a id="DataSourcesEqCondition"></a>

`DataSourcesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.notion.types.DataSourcesSearchFilter`
    :   The type of the None singleton.

<a id="DataSourcesFuzzyCondition"></a>

`DataSourcesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.notion.types.DataSourcesStringFilter`
    :   The type of the None singleton.

<a id="DataSourcesGetParams"></a>

`DataSourcesGetParams(*args, **kwargs)`
:   Parameters for data_sources.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data_source_id: str`
    :   The type of the None singleton.

<a id="DataSourcesGtCondition"></a>

`DataSourcesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.notion.types.DataSourcesSearchFilter`
    :   The type of the None singleton.

<a id="DataSourcesGteCondition"></a>

`DataSourcesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.notion.types.DataSourcesSearchFilter`
    :   The type of the None singleton.

<a id="DataSourcesInCondition"></a>

`DataSourcesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.notion.types.DataSourcesInFilter`
    :   The type of the None singleton.

<a id="DataSourcesInFilter"></a>

`DataSourcesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Indicates if the data source is archived or not.

    `cover: list[dict[str, typing.Any]]`
    :   URL or reference to the cover image of the data source.

    `created_by: list[dict[str, typing.Any]]`
    :   The user who created the data source.

    `created_time: list[str]`
    :   The timestamp when the data source was created.

    `database_parent: list[dict[str, typing.Any]]`
    :   The grandparent of the data source (parent of the database).

    `description: list[list[typing.Any]]`
    :   Description text associated with the data source.

    `icon: list[dict[str, typing.Any]]`
    :   URL or reference to the icon of the data source.

    `id: list[str]`
    :   Unique identifier of the data source.

    `is_inline: list[bool]`
    :   Indicates if the data source is displayed inline.

    `last_edited_by: list[dict[str, typing.Any]]`
    :   The user who last edited the data source.

    `last_edited_time: list[str]`
    :   The timestamp when the data source was last edited.

    `object_: list[dict[str, typing.Any]]`
    :   The type of object (data_source).

    `parent: list[dict[str, typing.Any]]`
    :   The parent database of the data source.

    `properties: list[list[typing.Any]]`
    :   Schema of properties for the data source.

    `public_url: list[str]`
    :   Public URL to access the data source.

    `title: list[list[typing.Any]]`
    :   Title or name of the data source.

    `url: list[str]`
    :   URL or reference to access the data source.

<a id="DataSourcesKeywordCondition"></a>

`DataSourcesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.notion.types.DataSourcesStringFilter`
    :   The type of the None singleton.

<a id="DataSourcesLikeCondition"></a>

`DataSourcesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.notion.types.DataSourcesStringFilter`
    :   The type of the None singleton.

<a id="DataSourcesListParams"></a>

`DataSourcesListParams(*args, **kwargs)`
:   Parameters for data_sources.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.notion.types.DataSourcesListParamsFilter`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: airbyte_agent_sdk.connectors.notion.types.DataSourcesListParamsSort`
    :   The type of the None singleton.

    `start_cursor: str`
    :   The type of the None singleton.

<a id="DataSourcesListParamsFilter"></a>

`DataSourcesListParamsFilter(*args, **kwargs)`
:   Nested schema for DataSourcesListParams.filter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `property: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="DataSourcesListParamsSort"></a>

`DataSourcesListParamsSort(*args, **kwargs)`
:   Nested schema for DataSourcesListParams.sort

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `direction: str`
    :   The type of the None singleton.

    `timestamp: str`
    :   The type of the None singleton.

<a id="DataSourcesLtCondition"></a>

`DataSourcesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.notion.types.DataSourcesSearchFilter`
    :   The type of the None singleton.

<a id="DataSourcesLteCondition"></a>

`DataSourcesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.notion.types.DataSourcesSearchFilter`
    :   The type of the None singleton.

<a id="DataSourcesNeqCondition"></a>

`DataSourcesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.notion.types.DataSourcesSearchFilter`
    :   The type of the None singleton.

<a id="DataSourcesNotCondition"></a>

`DataSourcesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.notion.types.DataSourcesEqCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesNeqCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesGtCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesGteCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLtCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLteCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesInCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLikeCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesKeywordCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesContainsCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesNotCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesAndCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesOrCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesAnyCondition`
    :   The type of the None singleton.

<a id="DataSourcesOrCondition"></a>

`DataSourcesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.notion.types.DataSourcesEqCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesNeqCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesGtCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesGteCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLtCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLteCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesInCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLikeCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesKeywordCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesContainsCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesNotCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesAndCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesOrCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesAnyCondition]`
    :   The type of the None singleton.

<a id="DataSourcesSearchFilter"></a>

`DataSourcesSearchFilter(*args, **kwargs)`
:   Available fields for filtering data_sources search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="DataSourcesSearchQuery"></a>

`DataSourcesSearchQuery(*args, **kwargs)`
:   Search query for data_sources entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.notion.types.DataSourcesEqCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesNeqCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesGtCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesGteCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLtCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLteCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesInCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLikeCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesKeywordCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesContainsCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesNotCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesAndCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesOrCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.notion.types.DataSourcesSortFilter]`
    :   The type of the None singleton.

<a id="DataSourcesSortFilter"></a>

`DataSourcesSortFilter(*args, **kwargs)`
:   Available fields for sorting data_sources search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Indicates if the data source is archived or not.

    `cover: Literal['asc', 'desc']`
    :   URL or reference to the cover image of the data source.

    `created_by: Literal['asc', 'desc']`
    :   The user who created the data source.

    `created_time: Literal['asc', 'desc']`
    :   The timestamp when the data source was created.

    `database_parent: Literal['asc', 'desc']`
    :   The grandparent of the data source (parent of the database).

    `description: Literal['asc', 'desc']`
    :   Description text associated with the data source.

    `icon: Literal['asc', 'desc']`
    :   URL or reference to the icon of the data source.

    `id: Literal['asc', 'desc']`
    :   Unique identifier of the data source.

    `is_inline: Literal['asc', 'desc']`
    :   Indicates if the data source is displayed inline.

    `last_edited_by: Literal['asc', 'desc']`
    :   The user who last edited the data source.

    `last_edited_time: Literal['asc', 'desc']`
    :   The timestamp when the data source was last edited.

    `object_: Literal['asc', 'desc']`
    :   The type of object (data_source).

    `parent: Literal['asc', 'desc']`
    :   The parent database of the data source.

    `properties: Literal['asc', 'desc']`
    :   Schema of properties for the data source.

    `public_url: Literal['asc', 'desc']`
    :   Public URL to access the data source.

    `title: Literal['asc', 'desc']`
    :   Title or name of the data source.

    `url: Literal['asc', 'desc']`
    :   URL or reference to access the data source.

<a id="DataSourcesStringFilter"></a>

`DataSourcesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Indicates if the data source is archived or not.

    `cover: str`
    :   URL or reference to the cover image of the data source.

    `created_by: str`
    :   The user who created the data source.

    `created_time: str`
    :   The timestamp when the data source was created.

    `database_parent: str`
    :   The grandparent of the data source (parent of the database).

    `description: str`
    :   Description text associated with the data source.

    `icon: str`
    :   URL or reference to the icon of the data source.

    `id: str`
    :   Unique identifier of the data source.

    `is_inline: str`
    :   Indicates if the data source is displayed inline.

    `last_edited_by: str`
    :   The user who last edited the data source.

    `last_edited_time: str`
    :   The timestamp when the data source was last edited.

    `object_: str`
    :   The type of object (data_source).

    `parent: str`
    :   The parent database of the data source.

    `properties: str`
    :   Schema of properties for the data source.

    `public_url: str`
    :   Public URL to access the data source.

    `title: str`
    :   Title or name of the data source.

    `url: str`
    :   URL or reference to access the data source.

<a id="DataSourcesUpdateParams"></a>

`DataSourcesUpdateParams(*args, **kwargs)`
:   Parameters for data_sources.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `cover: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsCover | None`
    :   The type of the None singleton.

    `data_source_id: str`
    :   The type of the None singleton.

    `description: list[airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsDescriptionItem]`
    :   The type of the None singleton.

    `icon: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsIcon | None`
    :   The type of the None singleton.

    `in_trash: bool`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   The type of the None singleton.

    `title: list[airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsTitleItem]`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsCover"></a>

`DataSourcesUpdateParamsCover(*args, **kwargs)`
:   Cover image. Supports external URL or file upload. Set to null to remove.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsCoverExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsCoverFileUpload`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsCoverExternal"></a>

`DataSourcesUpdateParamsCoverExternal(*args, **kwargs)`
:   External URL cover

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsCoverFileUpload"></a>

`DataSourcesUpdateParamsCoverFileUpload(*args, **kwargs)`
:   Uploaded file cover

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsDescriptionItem"></a>

`DataSourcesUpdateParamsDescriptionItem(*args, **kwargs)`
:   Nested schema for DataSourcesUpdateParams.description_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsDescriptionItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsDescriptionItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsDescriptionItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsDescriptionItemAnnotations"></a>

`DataSourcesUpdateParamsDescriptionItemAnnotations(*args, **kwargs)`
:   Nested schema for DataSourcesUpdateParamsDescriptionItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsDescriptionItemEquation"></a>

`DataSourcesUpdateParamsDescriptionItemEquation(*args, **kwargs)`
:   Nested schema for DataSourcesUpdateParamsDescriptionItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsDescriptionItemText"></a>

`DataSourcesUpdateParamsDescriptionItemText(*args, **kwargs)`
:   Nested schema for DataSourcesUpdateParamsDescriptionItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsDescriptionItemTextLink | None`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsDescriptionItemTextLink"></a>

`DataSourcesUpdateParamsDescriptionItemTextLink(*args, **kwargs)`
:   Nested schema for DataSourcesUpdateParamsDescriptionItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsIcon"></a>

`DataSourcesUpdateParamsIcon(*args, **kwargs)`
:   Icon. Supports emoji, external URL, file upload, custom emoji, and Notion native icons. Set to null to remove.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `custom_emoji: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsIconCustomEmoji`
    :   The type of the None singleton.

    `emoji: str`
    :   The type of the None singleton.

    `external: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsIconExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsIconFileUpload`
    :   The type of the None singleton.

    `icon: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsIconIcon`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsIconCustomEmoji"></a>

`DataSourcesUpdateParamsIconCustomEmoji(*args, **kwargs)`
:   Custom emoji icon (when type is custom_emoji)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsIconExternal"></a>

`DataSourcesUpdateParamsIconExternal(*args, **kwargs)`
:   External URL icon (when type is external)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsIconFileUpload"></a>

`DataSourcesUpdateParamsIconFileUpload(*args, **kwargs)`
:   Uploaded file icon (when type is file_upload)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsIconIcon"></a>

`DataSourcesUpdateParamsIconIcon(*args, **kwargs)`
:   Notion native icon (when type is icon)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsTitleItem"></a>

`DataSourcesUpdateParamsTitleItem(*args, **kwargs)`
:   Nested schema for DataSourcesUpdateParams.title_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsTitleItemAnnotations`
    :   The type of the None singleton.

    `equation: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsTitleItemEquation`
    :   The type of the None singleton.

    `mention: dict[str, typing.Any]`
    :   The type of the None singleton.

    `text: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsTitleItemText`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsTitleItemAnnotations"></a>

`DataSourcesUpdateParamsTitleItemAnnotations(*args, **kwargs)`
:   Nested schema for DataSourcesUpdateParamsTitleItem.annotations

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `bold: bool`
    :   The type of the None singleton.

    `code: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `italic: bool`
    :   The type of the None singleton.

    `strikethrough: bool`
    :   The type of the None singleton.

    `underline: bool`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsTitleItemEquation"></a>

`DataSourcesUpdateParamsTitleItemEquation(*args, **kwargs)`
:   Nested schema for DataSourcesUpdateParamsTitleItem.equation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expression: str`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsTitleItemText"></a>

`DataSourcesUpdateParamsTitleItemText(*args, **kwargs)`
:   Nested schema for DataSourcesUpdateParamsTitleItem.text

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   The type of the None singleton.

    `link: airbyte_agent_sdk.connectors.notion.types.DataSourcesUpdateParamsTitleItemTextLink | None`
    :   The type of the None singleton.

<a id="DataSourcesUpdateParamsTitleItemTextLink"></a>

`DataSourcesUpdateParamsTitleItemTextLink(*args, **kwargs)`
:   Nested schema for DataSourcesUpdateParamsTitleItemText.link

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="PagesAndCondition"></a>

`PagesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.notion.types.PagesEqCondition | airbyte_agent_sdk.connectors.notion.types.PagesNeqCondition | airbyte_agent_sdk.connectors.notion.types.PagesGtCondition | airbyte_agent_sdk.connectors.notion.types.PagesGteCondition | airbyte_agent_sdk.connectors.notion.types.PagesLtCondition | airbyte_agent_sdk.connectors.notion.types.PagesLteCondition | airbyte_agent_sdk.connectors.notion.types.PagesInCondition | airbyte_agent_sdk.connectors.notion.types.PagesLikeCondition | airbyte_agent_sdk.connectors.notion.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.notion.types.PagesContainsCondition | airbyte_agent_sdk.connectors.notion.types.PagesNotCondition | airbyte_agent_sdk.connectors.notion.types.PagesAndCondition | airbyte_agent_sdk.connectors.notion.types.PagesOrCondition | airbyte_agent_sdk.connectors.notion.types.PagesAnyCondition]`
    :   The type of the None singleton.

<a id="PagesAnyCondition"></a>

`PagesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.notion.types.PagesAnyValueFilter`
    :   The type of the None singleton.

<a id="PagesAnyValueFilter"></a>

`PagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Indicates whether the page is archived or not.

    `cover: Any`
    :   URL or reference to the page cover image.

    `created_by: Any`
    :   User ID or name of the creator of the page.

    `created_time: Any`
    :   Date and time when the page was created.

    `icon: Any`
    :   URL or reference to the page icon.

    `id: Any`
    :   Unique identifier of the page.

    `in_trash: Any`
    :   Indicates whether the page is in trash or not.

    `last_edited_by: Any`
    :   User ID or name of the last editor of the page.

    `last_edited_time: Any`
    :   Date and time when the page was last edited.

    `object_: Any`
    :   Type or category of the page object.

    `parent: Any`
    :   ID or reference to the parent page.

    `properties: Any`
    :   Custom properties associated with the page.

    `public_url: Any`
    :   Publicly accessible URL of the page.

    `url: Any`
    :   URL of the page within the service.

<a id="PagesContainsCondition"></a>

`PagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.notion.types.PagesAnyValueFilter`
    :   The type of the None singleton.

<a id="PagesCreateParams"></a>

`PagesCreateParams(*args, **kwargs)`
:   Parameters for pages.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `children: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `cover: airbyte_agent_sdk.connectors.notion.types.PagesCreateParamsCover | None`
    :   The type of the None singleton.

    `icon: airbyte_agent_sdk.connectors.notion.types.PagesCreateParamsIcon | None`
    :   The type of the None singleton.

    `parent: dict[str, typing.Any]`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   The type of the None singleton.

<a id="PagesCreateParamsCover"></a>

`PagesCreateParamsCover(*args, **kwargs)`
:   Cover image. Supports external URL or file upload. Set to null to remove.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.types.PagesCreateParamsCoverExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.PagesCreateParamsCoverFileUpload`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="PagesCreateParamsCoverExternal"></a>

`PagesCreateParamsCoverExternal(*args, **kwargs)`
:   External URL cover

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="PagesCreateParamsCoverFileUpload"></a>

`PagesCreateParamsCoverFileUpload(*args, **kwargs)`
:   Uploaded file cover

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="PagesCreateParamsIcon"></a>

`PagesCreateParamsIcon(*args, **kwargs)`
:   Icon. Supports emoji, external URL, file upload, custom emoji, and Notion native icons. Set to null to remove.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `custom_emoji: airbyte_agent_sdk.connectors.notion.types.PagesCreateParamsIconCustomEmoji`
    :   The type of the None singleton.

    `emoji: str`
    :   The type of the None singleton.

    `external: airbyte_agent_sdk.connectors.notion.types.PagesCreateParamsIconExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.PagesCreateParamsIconFileUpload`
    :   The type of the None singleton.

    `icon: airbyte_agent_sdk.connectors.notion.types.PagesCreateParamsIconIcon`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="PagesCreateParamsIconCustomEmoji"></a>

`PagesCreateParamsIconCustomEmoji(*args, **kwargs)`
:   Custom emoji icon (when type is custom_emoji)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="PagesCreateParamsIconExternal"></a>

`PagesCreateParamsIconExternal(*args, **kwargs)`
:   External URL icon (when type is external)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="PagesCreateParamsIconFileUpload"></a>

`PagesCreateParamsIconFileUpload(*args, **kwargs)`
:   Uploaded file icon (when type is file_upload)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="PagesCreateParamsIconIcon"></a>

`PagesCreateParamsIconIcon(*args, **kwargs)`
:   Notion native icon (when type is icon)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="PagesEqCondition"></a>

`PagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.notion.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesFuzzyCondition"></a>

`PagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.notion.types.PagesStringFilter`
    :   The type of the None singleton.

<a id="PagesGetParams"></a>

`PagesGetParams(*args, **kwargs)`
:   Parameters for pages.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_id: str`
    :   The type of the None singleton.

<a id="PagesGtCondition"></a>

`PagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.notion.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesGteCondition"></a>

`PagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.notion.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesInCondition"></a>

`PagesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.notion.types.PagesInFilter`
    :   The type of the None singleton.

<a id="PagesInFilter"></a>

`PagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Indicates whether the page is archived or not.

    `cover: list[dict[str, typing.Any]]`
    :   URL or reference to the page cover image.

    `created_by: list[dict[str, typing.Any]]`
    :   User ID or name of the creator of the page.

    `created_time: list[str]`
    :   Date and time when the page was created.

    `icon: list[dict[str, typing.Any]]`
    :   URL or reference to the page icon.

    `id: list[str]`
    :   Unique identifier of the page.

    `in_trash: list[bool]`
    :   Indicates whether the page is in trash or not.

    `last_edited_by: list[dict[str, typing.Any]]`
    :   User ID or name of the last editor of the page.

    `last_edited_time: list[str]`
    :   Date and time when the page was last edited.

    `object_: list[dict[str, typing.Any]]`
    :   Type or category of the page object.

    `parent: list[dict[str, typing.Any]]`
    :   ID or reference to the parent page.

    `properties: list[list[typing.Any]]`
    :   Custom properties associated with the page.

    `public_url: list[str]`
    :   Publicly accessible URL of the page.

    `url: list[str]`
    :   URL of the page within the service.

<a id="PagesKeywordCondition"></a>

`PagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.notion.types.PagesStringFilter`
    :   The type of the None singleton.

<a id="PagesLikeCondition"></a>

`PagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.notion.types.PagesStringFilter`
    :   The type of the None singleton.

<a id="PagesListParams"></a>

`PagesListParams(*args, **kwargs)`
:   Parameters for pages.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.notion.types.PagesListParamsFilter`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `sort: airbyte_agent_sdk.connectors.notion.types.PagesListParamsSort`
    :   The type of the None singleton.

    `start_cursor: str`
    :   The type of the None singleton.

<a id="PagesListParamsFilter"></a>

`PagesListParamsFilter(*args, **kwargs)`
:   Nested schema for PagesListParams.filter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `property: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="PagesListParamsSort"></a>

`PagesListParamsSort(*args, **kwargs)`
:   Nested schema for PagesListParams.sort

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `direction: str`
    :   The type of the None singleton.

    `timestamp: str`
    :   The type of the None singleton.

<a id="PagesLtCondition"></a>

`PagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.notion.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesLteCondition"></a>

`PagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.notion.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesNeqCondition"></a>

`PagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.notion.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesNotCondition"></a>

`PagesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.notion.types.PagesEqCondition | airbyte_agent_sdk.connectors.notion.types.PagesNeqCondition | airbyte_agent_sdk.connectors.notion.types.PagesGtCondition | airbyte_agent_sdk.connectors.notion.types.PagesGteCondition | airbyte_agent_sdk.connectors.notion.types.PagesLtCondition | airbyte_agent_sdk.connectors.notion.types.PagesLteCondition | airbyte_agent_sdk.connectors.notion.types.PagesInCondition | airbyte_agent_sdk.connectors.notion.types.PagesLikeCondition | airbyte_agent_sdk.connectors.notion.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.notion.types.PagesContainsCondition | airbyte_agent_sdk.connectors.notion.types.PagesNotCondition | airbyte_agent_sdk.connectors.notion.types.PagesAndCondition | airbyte_agent_sdk.connectors.notion.types.PagesOrCondition | airbyte_agent_sdk.connectors.notion.types.PagesAnyCondition`
    :   The type of the None singleton.

<a id="PagesOrCondition"></a>

`PagesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.notion.types.PagesEqCondition | airbyte_agent_sdk.connectors.notion.types.PagesNeqCondition | airbyte_agent_sdk.connectors.notion.types.PagesGtCondition | airbyte_agent_sdk.connectors.notion.types.PagesGteCondition | airbyte_agent_sdk.connectors.notion.types.PagesLtCondition | airbyte_agent_sdk.connectors.notion.types.PagesLteCondition | airbyte_agent_sdk.connectors.notion.types.PagesInCondition | airbyte_agent_sdk.connectors.notion.types.PagesLikeCondition | airbyte_agent_sdk.connectors.notion.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.notion.types.PagesContainsCondition | airbyte_agent_sdk.connectors.notion.types.PagesNotCondition | airbyte_agent_sdk.connectors.notion.types.PagesAndCondition | airbyte_agent_sdk.connectors.notion.types.PagesOrCondition | airbyte_agent_sdk.connectors.notion.types.PagesAnyCondition]`
    :   The type of the None singleton.

<a id="PagesSearchFilter"></a>

`PagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering pages search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="PagesSearchQuery"></a>

`PagesSearchQuery(*args, **kwargs)`
:   Search query for pages entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.notion.types.PagesEqCondition | airbyte_agent_sdk.connectors.notion.types.PagesNeqCondition | airbyte_agent_sdk.connectors.notion.types.PagesGtCondition | airbyte_agent_sdk.connectors.notion.types.PagesGteCondition | airbyte_agent_sdk.connectors.notion.types.PagesLtCondition | airbyte_agent_sdk.connectors.notion.types.PagesLteCondition | airbyte_agent_sdk.connectors.notion.types.PagesInCondition | airbyte_agent_sdk.connectors.notion.types.PagesLikeCondition | airbyte_agent_sdk.connectors.notion.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.notion.types.PagesContainsCondition | airbyte_agent_sdk.connectors.notion.types.PagesNotCondition | airbyte_agent_sdk.connectors.notion.types.PagesAndCondition | airbyte_agent_sdk.connectors.notion.types.PagesOrCondition | airbyte_agent_sdk.connectors.notion.types.PagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.notion.types.PagesSortFilter]`
    :   The type of the None singleton.

<a id="PagesSortFilter"></a>

`PagesSortFilter(*args, **kwargs)`
:   Available fields for sorting pages search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Indicates whether the page is archived or not.

    `cover: Literal['asc', 'desc']`
    :   URL or reference to the page cover image.

    `created_by: Literal['asc', 'desc']`
    :   User ID or name of the creator of the page.

    `created_time: Literal['asc', 'desc']`
    :   Date and time when the page was created.

    `icon: Literal['asc', 'desc']`
    :   URL or reference to the page icon.

    `id: Literal['asc', 'desc']`
    :   Unique identifier of the page.

    `in_trash: Literal['asc', 'desc']`
    :   Indicates whether the page is in trash or not.

    `last_edited_by: Literal['asc', 'desc']`
    :   User ID or name of the last editor of the page.

    `last_edited_time: Literal['asc', 'desc']`
    :   Date and time when the page was last edited.

    `object_: Literal['asc', 'desc']`
    :   Type or category of the page object.

    `parent: Literal['asc', 'desc']`
    :   ID or reference to the parent page.

    `properties: Literal['asc', 'desc']`
    :   Custom properties associated with the page.

    `public_url: Literal['asc', 'desc']`
    :   Publicly accessible URL of the page.

    `url: Literal['asc', 'desc']`
    :   URL of the page within the service.

<a id="PagesStringFilter"></a>

`PagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Indicates whether the page is archived or not.

    `cover: str`
    :   URL or reference to the page cover image.

    `created_by: str`
    :   User ID or name of the creator of the page.

    `created_time: str`
    :   Date and time when the page was created.

    `icon: str`
    :   URL or reference to the page icon.

    `id: str`
    :   Unique identifier of the page.

    `in_trash: str`
    :   Indicates whether the page is in trash or not.

    `last_edited_by: str`
    :   User ID or name of the last editor of the page.

    `last_edited_time: str`
    :   Date and time when the page was last edited.

    `object_: str`
    :   Type or category of the page object.

    `parent: str`
    :   ID or reference to the parent page.

    `properties: str`
    :   Custom properties associated with the page.

    `public_url: str`
    :   Publicly accessible URL of the page.

    `url: str`
    :   URL of the page within the service.

<a id="PagesUpdateParams"></a>

`PagesUpdateParams(*args, **kwargs)`
:   Parameters for pages.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `cover: airbyte_agent_sdk.connectors.notion.types.PagesUpdateParamsCover | None`
    :   The type of the None singleton.

    `icon: airbyte_agent_sdk.connectors.notion.types.PagesUpdateParamsIcon | None`
    :   The type of the None singleton.

    `in_trash: bool`
    :   The type of the None singleton.

    `page_id: str`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   The type of the None singleton.

<a id="PagesUpdateParamsCover"></a>

`PagesUpdateParamsCover(*args, **kwargs)`
:   Cover image. Supports external URL or file upload. Set to null to remove.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external: airbyte_agent_sdk.connectors.notion.types.PagesUpdateParamsCoverExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.PagesUpdateParamsCoverFileUpload`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="PagesUpdateParamsCoverExternal"></a>

`PagesUpdateParamsCoverExternal(*args, **kwargs)`
:   External URL cover

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="PagesUpdateParamsCoverFileUpload"></a>

`PagesUpdateParamsCoverFileUpload(*args, **kwargs)`
:   Uploaded file cover

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="PagesUpdateParamsIcon"></a>

`PagesUpdateParamsIcon(*args, **kwargs)`
:   Icon. Supports emoji, external URL, file upload, custom emoji, and Notion native icons. Set to null to remove.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `custom_emoji: airbyte_agent_sdk.connectors.notion.types.PagesUpdateParamsIconCustomEmoji`
    :   The type of the None singleton.

    `emoji: str`
    :   The type of the None singleton.

    `external: airbyte_agent_sdk.connectors.notion.types.PagesUpdateParamsIconExternal`
    :   The type of the None singleton.

    `file_upload: airbyte_agent_sdk.connectors.notion.types.PagesUpdateParamsIconFileUpload`
    :   The type of the None singleton.

    `icon: airbyte_agent_sdk.connectors.notion.types.PagesUpdateParamsIconIcon`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="PagesUpdateParamsIconCustomEmoji"></a>

`PagesUpdateParamsIconCustomEmoji(*args, **kwargs)`
:   Custom emoji icon (when type is custom_emoji)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="PagesUpdateParamsIconExternal"></a>

`PagesUpdateParamsIconExternal(*args, **kwargs)`
:   External URL icon (when type is external)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `url: str`
    :   The type of the None singleton.

<a id="PagesUpdateParamsIconFileUpload"></a>

`PagesUpdateParamsIconFileUpload(*args, **kwargs)`
:   Uploaded file icon (when type is file_upload)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="PagesUpdateParamsIconIcon"></a>

`PagesUpdateParamsIconIcon(*args, **kwargs)`
:   Notion native icon (when type is icon)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="UsersAndCondition"></a>

`UsersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.notion.types.UsersEqCondition | airbyte_agent_sdk.connectors.notion.types.UsersNeqCondition | airbyte_agent_sdk.connectors.notion.types.UsersGtCondition | airbyte_agent_sdk.connectors.notion.types.UsersGteCondition | airbyte_agent_sdk.connectors.notion.types.UsersLtCondition | airbyte_agent_sdk.connectors.notion.types.UsersLteCondition | airbyte_agent_sdk.connectors.notion.types.UsersInCondition | airbyte_agent_sdk.connectors.notion.types.UsersLikeCondition | airbyte_agent_sdk.connectors.notion.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.notion.types.UsersContainsCondition | airbyte_agent_sdk.connectors.notion.types.UsersNotCondition | airbyte_agent_sdk.connectors.notion.types.UsersAndCondition | airbyte_agent_sdk.connectors.notion.types.UsersOrCondition | airbyte_agent_sdk.connectors.notion.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersAnyCondition"></a>

`UsersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.notion.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersAnyValueFilter"></a>

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: Any`
    :   URL of the user's avatar

    `bot: Any`
    :   Bot-specific data

    `id: Any`
    :   Unique identifier for the user

    `name: Any`
    :   User's display name

    `object_: Any`
    :   Always user

    `person: Any`
    :   Person-specific data

    `type_: Any`
    :   Type of user (person or bot)

<a id="UsersContainsCondition"></a>

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.notion.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersEqCondition"></a>

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.notion.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersFuzzyCondition"></a>

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.notion.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersGetParams"></a>

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `user_id: str`
    :   The type of the None singleton.

<a id="UsersGtCondition"></a>

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.notion.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersGteCondition"></a>

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.notion.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersInCondition"></a>

`UsersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.notion.types.UsersInFilter`
    :   The type of the None singleton.

<a id="UsersInFilter"></a>

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: list[str]`
    :   URL of the user's avatar

    `bot: list[dict[str, typing.Any]]`
    :   Bot-specific data

    `id: list[str]`
    :   Unique identifier for the user

    `name: list[str]`
    :   User's display name

    `object_: list[dict[str, typing.Any]]`
    :   Always user

    `person: list[dict[str, typing.Any]]`
    :   Person-specific data

    `type_: list[dict[str, typing.Any]]`
    :   Type of user (person or bot)

<a id="UsersKeywordCondition"></a>

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.notion.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersLikeCondition"></a>

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.notion.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

    `start_cursor: str`
    :   The type of the None singleton.

<a id="UsersLtCondition"></a>

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.notion.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersLteCondition"></a>

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.notion.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNeqCondition"></a>

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.notion.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNotCondition"></a>

`UsersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.notion.types.UsersEqCondition | airbyte_agent_sdk.connectors.notion.types.UsersNeqCondition | airbyte_agent_sdk.connectors.notion.types.UsersGtCondition | airbyte_agent_sdk.connectors.notion.types.UsersGteCondition | airbyte_agent_sdk.connectors.notion.types.UsersLtCondition | airbyte_agent_sdk.connectors.notion.types.UsersLteCondition | airbyte_agent_sdk.connectors.notion.types.UsersInCondition | airbyte_agent_sdk.connectors.notion.types.UsersLikeCondition | airbyte_agent_sdk.connectors.notion.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.notion.types.UsersContainsCondition | airbyte_agent_sdk.connectors.notion.types.UsersNotCondition | airbyte_agent_sdk.connectors.notion.types.UsersAndCondition | airbyte_agent_sdk.connectors.notion.types.UsersOrCondition | airbyte_agent_sdk.connectors.notion.types.UsersAnyCondition`
    :   The type of the None singleton.

<a id="UsersOrCondition"></a>

`UsersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.notion.types.UsersEqCondition | airbyte_agent_sdk.connectors.notion.types.UsersNeqCondition | airbyte_agent_sdk.connectors.notion.types.UsersGtCondition | airbyte_agent_sdk.connectors.notion.types.UsersGteCondition | airbyte_agent_sdk.connectors.notion.types.UsersLtCondition | airbyte_agent_sdk.connectors.notion.types.UsersLteCondition | airbyte_agent_sdk.connectors.notion.types.UsersInCondition | airbyte_agent_sdk.connectors.notion.types.UsersLikeCondition | airbyte_agent_sdk.connectors.notion.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.notion.types.UsersContainsCondition | airbyte_agent_sdk.connectors.notion.types.UsersNotCondition | airbyte_agent_sdk.connectors.notion.types.UsersAndCondition | airbyte_agent_sdk.connectors.notion.types.UsersOrCondition | airbyte_agent_sdk.connectors.notion.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersSearchFilter"></a>

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: str | None`
    :   URL of the user's avatar

    `bot: dict[str, typing.Any] | None`
    :   Bot-specific data

    `id: str | None`
    :   Unique identifier for the user

    `name: str | None`
    :   User's display name

    `object_: dict[str, typing.Any] | None`
    :   Always user

    `person: dict[str, typing.Any] | None`
    :   Person-specific data

    `type_: dict[str, typing.Any] | None`
    :   Type of user (person or bot)

<a id="UsersSearchQuery"></a>

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.notion.types.UsersEqCondition | airbyte_agent_sdk.connectors.notion.types.UsersNeqCondition | airbyte_agent_sdk.connectors.notion.types.UsersGtCondition | airbyte_agent_sdk.connectors.notion.types.UsersGteCondition | airbyte_agent_sdk.connectors.notion.types.UsersLtCondition | airbyte_agent_sdk.connectors.notion.types.UsersLteCondition | airbyte_agent_sdk.connectors.notion.types.UsersInCondition | airbyte_agent_sdk.connectors.notion.types.UsersLikeCondition | airbyte_agent_sdk.connectors.notion.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.notion.types.UsersContainsCondition | airbyte_agent_sdk.connectors.notion.types.UsersNotCondition | airbyte_agent_sdk.connectors.notion.types.UsersAndCondition | airbyte_agent_sdk.connectors.notion.types.UsersOrCondition | airbyte_agent_sdk.connectors.notion.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.notion.types.UsersSortFilter]`
    :   The type of the None singleton.

<a id="UsersSortFilter"></a>

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: Literal['asc', 'desc']`
    :   URL of the user's avatar

    `bot: Literal['asc', 'desc']`
    :   Bot-specific data

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the user

    `name: Literal['asc', 'desc']`
    :   User's display name

    `object_: Literal['asc', 'desc']`
    :   Always user

    `person: Literal['asc', 'desc']`
    :   Person-specific data

    `type_: Literal['asc', 'desc']`
    :   Type of user (person or bot)

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: str`
    :   URL of the user's avatar

    `bot: str`
    :   Bot-specific data

    `id: str`
    :   Unique identifier for the user

    `name: str`
    :   User's display name

    `object_: str`
    :   Always user

    `person: str`
    :   Person-specific data

    `type_: str`
    :   Type of user (person or bot)