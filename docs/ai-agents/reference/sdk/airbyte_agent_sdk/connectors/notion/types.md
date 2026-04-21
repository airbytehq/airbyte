---
id: airbyte_agent_sdk-connectors-notion-types
title: airbyte_agent_sdk.connectors.notion.types
---

Module airbyte_agent_sdk.connectors.notion.types
================================================
Type definitions for notion connector.

Classes
-------

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

`BlocksContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.notion.types.BlocksAnyValueFilter`
    :   The type of the None singleton.

`BlocksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.notion.types.BlocksSearchFilter`
    :   The type of the None singleton.

`BlocksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.notion.types.BlocksStringFilter`
    :   The type of the None singleton.

`BlocksGetParams(*args, **kwargs)`
:   Parameters for blocks.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `block_id: str`
    :   The type of the None singleton.

`BlocksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.notion.types.BlocksSearchFilter`
    :   The type of the None singleton.

`BlocksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.notion.types.BlocksSearchFilter`
    :   The type of the None singleton.

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

`BlocksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.notion.types.BlocksStringFilter`
    :   The type of the None singleton.

`BlocksLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.notion.types.BlocksStringFilter`
    :   The type of the None singleton.

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

`BlocksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.notion.types.BlocksSearchFilter`
    :   The type of the None singleton.

`BlocksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.notion.types.BlocksSearchFilter`
    :   The type of the None singleton.

`BlocksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.notion.types.BlocksSearchFilter`
    :   The type of the None singleton.

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

`BlocksSearchQuery(*args, **kwargs)`
:   Search query for blocks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.notion.types.BlocksEqCondition | airbyte_agent_sdk.connectors.notion.types.BlocksNeqCondition | airbyte_agent_sdk.connectors.notion.types.BlocksGtCondition | airbyte_agent_sdk.connectors.notion.types.BlocksGteCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLtCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLteCondition | airbyte_agent_sdk.connectors.notion.types.BlocksInCondition | airbyte_agent_sdk.connectors.notion.types.BlocksLikeCondition | airbyte_agent_sdk.connectors.notion.types.BlocksFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.BlocksKeywordCondition | airbyte_agent_sdk.connectors.notion.types.BlocksContainsCondition | airbyte_agent_sdk.connectors.notion.types.BlocksNotCondition | airbyte_agent_sdk.connectors.notion.types.BlocksAndCondition | airbyte_agent_sdk.connectors.notion.types.BlocksOrCondition | airbyte_agent_sdk.connectors.notion.types.BlocksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.notion.types.BlocksSortFilter]`
    :   The type of the None singleton.

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

`DataSourcesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.notion.types.DataSourcesAnyValueFilter`
    :   The type of the None singleton.

`DataSourcesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.notion.types.DataSourcesSearchFilter`
    :   The type of the None singleton.

`DataSourcesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.notion.types.DataSourcesStringFilter`
    :   The type of the None singleton.

`DataSourcesGetParams(*args, **kwargs)`
:   Parameters for data_sources.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data_source_id: str`
    :   The type of the None singleton.

`DataSourcesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.notion.types.DataSourcesSearchFilter`
    :   The type of the None singleton.

`DataSourcesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.notion.types.DataSourcesSearchFilter`
    :   The type of the None singleton.

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

`DataSourcesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.notion.types.DataSourcesStringFilter`
    :   The type of the None singleton.

`DataSourcesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.notion.types.DataSourcesStringFilter`
    :   The type of the None singleton.

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

`DataSourcesListParamsFilter(*args, **kwargs)`
:   Nested schema for DataSourcesListParams.filter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `property: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

`DataSourcesListParamsSort(*args, **kwargs)`
:   Nested schema for DataSourcesListParams.sort

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `direction: str`
    :   The type of the None singleton.

    `timestamp: str`
    :   The type of the None singleton.

`DataSourcesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.notion.types.DataSourcesSearchFilter`
    :   The type of the None singleton.

`DataSourcesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.notion.types.DataSourcesSearchFilter`
    :   The type of the None singleton.

`DataSourcesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.notion.types.DataSourcesSearchFilter`
    :   The type of the None singleton.

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

`DataSourcesSearchQuery(*args, **kwargs)`
:   Search query for data_sources entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.notion.types.DataSourcesEqCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesNeqCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesGtCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesGteCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLtCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLteCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesInCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesLikeCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesKeywordCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesContainsCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesNotCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesAndCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesOrCondition | airbyte_agent_sdk.connectors.notion.types.DataSourcesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.notion.types.DataSourcesSortFilter]`
    :   The type of the None singleton.

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

`PagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.notion.types.PagesAnyValueFilter`
    :   The type of the None singleton.

`PagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.notion.types.PagesSearchFilter`
    :   The type of the None singleton.

`PagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.notion.types.PagesStringFilter`
    :   The type of the None singleton.

`PagesGetParams(*args, **kwargs)`
:   Parameters for pages.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_id: str`
    :   The type of the None singleton.

`PagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.notion.types.PagesSearchFilter`
    :   The type of the None singleton.

`PagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.notion.types.PagesSearchFilter`
    :   The type of the None singleton.

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

`PagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.notion.types.PagesStringFilter`
    :   The type of the None singleton.

`PagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.notion.types.PagesStringFilter`
    :   The type of the None singleton.

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

`PagesListParamsFilter(*args, **kwargs)`
:   Nested schema for PagesListParams.filter

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `property: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

`PagesListParamsSort(*args, **kwargs)`
:   Nested schema for PagesListParams.sort

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `direction: str`
    :   The type of the None singleton.

    `timestamp: str`
    :   The type of the None singleton.

`PagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.notion.types.PagesSearchFilter`
    :   The type of the None singleton.

`PagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.notion.types.PagesSearchFilter`
    :   The type of the None singleton.

`PagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.notion.types.PagesSearchFilter`
    :   The type of the None singleton.

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

`PagesSearchQuery(*args, **kwargs)`
:   Search query for pages entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.notion.types.PagesEqCondition | airbyte_agent_sdk.connectors.notion.types.PagesNeqCondition | airbyte_agent_sdk.connectors.notion.types.PagesGtCondition | airbyte_agent_sdk.connectors.notion.types.PagesGteCondition | airbyte_agent_sdk.connectors.notion.types.PagesLtCondition | airbyte_agent_sdk.connectors.notion.types.PagesLteCondition | airbyte_agent_sdk.connectors.notion.types.PagesInCondition | airbyte_agent_sdk.connectors.notion.types.PagesLikeCondition | airbyte_agent_sdk.connectors.notion.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.notion.types.PagesContainsCondition | airbyte_agent_sdk.connectors.notion.types.PagesNotCondition | airbyte_agent_sdk.connectors.notion.types.PagesAndCondition | airbyte_agent_sdk.connectors.notion.types.PagesOrCondition | airbyte_agent_sdk.connectors.notion.types.PagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.notion.types.PagesSortFilter]`
    :   The type of the None singleton.

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

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.notion.types.UsersAnyValueFilter`
    :   The type of the None singleton.

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.notion.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.notion.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `user_id: str`
    :   The type of the None singleton.

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.notion.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.notion.types.UsersSearchFilter`
    :   The type of the None singleton.

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

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.notion.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.notion.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

    `start_cursor: str`
    :   The type of the None singleton.

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.notion.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.notion.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.notion.types.UsersSearchFilter`
    :   The type of the None singleton.

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

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.notion.types.UsersEqCondition | airbyte_agent_sdk.connectors.notion.types.UsersNeqCondition | airbyte_agent_sdk.connectors.notion.types.UsersGtCondition | airbyte_agent_sdk.connectors.notion.types.UsersGteCondition | airbyte_agent_sdk.connectors.notion.types.UsersLtCondition | airbyte_agent_sdk.connectors.notion.types.UsersLteCondition | airbyte_agent_sdk.connectors.notion.types.UsersInCondition | airbyte_agent_sdk.connectors.notion.types.UsersLikeCondition | airbyte_agent_sdk.connectors.notion.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.notion.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.notion.types.UsersContainsCondition | airbyte_agent_sdk.connectors.notion.types.UsersNotCondition | airbyte_agent_sdk.connectors.notion.types.UsersAndCondition | airbyte_agent_sdk.connectors.notion.types.UsersOrCondition | airbyte_agent_sdk.connectors.notion.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.notion.types.UsersSortFilter]`
    :   The type of the None singleton.

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