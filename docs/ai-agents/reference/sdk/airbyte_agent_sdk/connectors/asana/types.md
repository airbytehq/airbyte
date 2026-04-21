---
id: airbyte_agent_sdk-connectors-asana-types
title: airbyte_agent_sdk.connectors.asana.types
---

Module airbyte_agent_sdk.connectors.asana.types
===============================================
Type definitions for asana connector.

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

`AttachmentsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.asana.types.AttachmentsEqCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsNeqCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsGtCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsGteCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsLtCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsLteCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsInCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsLikeCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsContainsCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsNotCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsAndCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsOrCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsAnyCondition]`
    :   The type of the None singleton.

`AttachmentsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.asana.types.AttachmentsAnyValueFilter`
    :   The type of the None singleton.

`AttachmentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `connected_to_app: Any`
    :   The type of the None singleton.

    `created_at: Any`
    :   The type of the None singleton.

    `download_url: Any`
    :   The type of the None singleton.

    `gid: Any`
    :   The type of the None singleton.

    `host: Any`
    :   The type of the None singleton.

    `name: Any`
    :   The type of the None singleton.

    `parent: Any`
    :   The type of the None singleton.

    `permanent_url: Any`
    :   The type of the None singleton.

    `resource_subtype: Any`
    :   The type of the None singleton.

    `resource_type: Any`
    :   The type of the None singleton.

    `size: Any`
    :   The type of the None singleton.

    `view_url: Any`
    :   The type of the None singleton.

`AttachmentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.asana.types.AttachmentsAnyValueFilter`
    :   The type of the None singleton.

`AttachmentsDownloadParams(*args, **kwargs)`
:   Parameters for attachments.download operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachment_gid: str`
    :   The type of the None singleton.

    `range_header: str`
    :   The type of the None singleton.

`AttachmentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.asana.types.AttachmentsSearchFilter`
    :   The type of the None singleton.

`AttachmentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.asana.types.AttachmentsStringFilter`
    :   The type of the None singleton.

`AttachmentsGetParams(*args, **kwargs)`
:   Parameters for attachments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachment_gid: str`
    :   The type of the None singleton.

`AttachmentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.asana.types.AttachmentsSearchFilter`
    :   The type of the None singleton.

`AttachmentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.asana.types.AttachmentsSearchFilter`
    :   The type of the None singleton.

`AttachmentsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.asana.types.AttachmentsInFilter`
    :   The type of the None singleton.

`AttachmentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `connected_to_app: list[bool]`
    :   The type of the None singleton.

    `created_at: list[str]`
    :   The type of the None singleton.

    `download_url: list[str]`
    :   The type of the None singleton.

    `gid: list[str]`
    :   The type of the None singleton.

    `host: list[str]`
    :   The type of the None singleton.

    `name: list[str]`
    :   The type of the None singleton.

    `parent: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `permanent_url: list[str]`
    :   The type of the None singleton.

    `resource_subtype: list[str]`
    :   The type of the None singleton.

    `resource_type: list[str]`
    :   The type of the None singleton.

    `size: list[int]`
    :   The type of the None singleton.

    `view_url: list[str]`
    :   The type of the None singleton.

`AttachmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.asana.types.AttachmentsStringFilter`
    :   The type of the None singleton.

`AttachmentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.asana.types.AttachmentsStringFilter`
    :   The type of the None singleton.

`AttachmentsListParams(*args, **kwargs)`
:   Parameters for attachments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `parent: str`
    :   The type of the None singleton.

`AttachmentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.asana.types.AttachmentsSearchFilter`
    :   The type of the None singleton.

`AttachmentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.asana.types.AttachmentsSearchFilter`
    :   The type of the None singleton.

`AttachmentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.asana.types.AttachmentsSearchFilter`
    :   The type of the None singleton.

`AttachmentsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.asana.types.AttachmentsEqCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsNeqCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsGtCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsGteCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsLtCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsLteCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsInCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsLikeCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsContainsCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsNotCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsAndCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsOrCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsAnyCondition`
    :   The type of the None singleton.

`AttachmentsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.asana.types.AttachmentsEqCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsNeqCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsGtCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsGteCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsLtCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsLteCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsInCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsLikeCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsContainsCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsNotCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsAndCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsOrCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsAnyCondition]`
    :   The type of the None singleton.

`AttachmentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering attachments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `connected_to_app: bool | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `download_url: str | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `host: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `parent: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `permanent_url: str | None`
    :   The type of the None singleton.

    `resource_subtype: str | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

    `size: int | None`
    :   The type of the None singleton.

    `view_url: str | None`
    :   The type of the None singleton.

`AttachmentsSearchQuery(*args, **kwargs)`
:   Search query for attachments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.asana.types.AttachmentsEqCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsNeqCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsGtCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsGteCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsLtCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsLteCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsInCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsLikeCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsContainsCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsNotCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsAndCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsOrCondition | airbyte_agent_sdk.connectors.asana.types.AttachmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.asana.types.AttachmentsSortFilter]`
    :   The type of the None singleton.

`AttachmentsSortFilter(*args, **kwargs)`
:   Available fields for sorting attachments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `connected_to_app: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `created_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `download_url: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `gid: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `host: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `name: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `parent: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `permanent_url: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `resource_subtype: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `resource_type: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `size: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `view_url: Literal['asc', 'desc']`
    :   The type of the None singleton.

`AttachmentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `connected_to_app: str`
    :   The type of the None singleton.

    `created_at: str`
    :   The type of the None singleton.

    `download_url: str`
    :   The type of the None singleton.

    `gid: str`
    :   The type of the None singleton.

    `host: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `parent: str`
    :   The type of the None singleton.

    `permanent_url: str`
    :   The type of the None singleton.

    `resource_subtype: str`
    :   The type of the None singleton.

    `resource_type: str`
    :   The type of the None singleton.

    `size: str`
    :   The type of the None singleton.

    `view_url: str`
    :   The type of the None singleton.

`ProjectSectionsCreateParams(*args, **kwargs)`
:   Parameters for project_sections.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.types.ProjectSectionsCreateParamsData`
    :   The type of the None singleton.

    `project_gid: str`
    :   The type of the None singleton.

`ProjectSectionsCreateParamsData(*args, **kwargs)`
:   Nested schema for ProjectSectionsCreateParams.data

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `insert_after: str`
    :   The type of the None singleton.

    `insert_before: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

`ProjectSectionsListParams(*args, **kwargs)`
:   Parameters for project_sections.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `project_gid: str`
    :   The type of the None singleton.

`ProjectTasksListParams(*args, **kwargs)`
:   Parameters for project_tasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `completed_since: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `project_gid: str`
    :   The type of the None singleton.

`ProjectsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.asana.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsInCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsAnyCondition]`
    :   The type of the None singleton.

`ProjectsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.asana.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

`ProjectsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   The type of the None singleton.

    `color: Any`
    :   The type of the None singleton.

    `created_at: Any`
    :   The type of the None singleton.

    `current_status: Any`
    :   The type of the None singleton.

    `custom_field_settings: Any`
    :   The type of the None singleton.

    `custom_fields: Any`
    :   The type of the None singleton.

    `default_view: Any`
    :   The type of the None singleton.

    `due_date: Any`
    :   The type of the None singleton.

    `due_on: Any`
    :   The type of the None singleton.

    `followers: Any`
    :   The type of the None singleton.

    `gid: Any`
    :   The type of the None singleton.

    `html_notes: Any`
    :   The type of the None singleton.

    `icon: Any`
    :   The type of the None singleton.

    `is_template: Any`
    :   The type of the None singleton.

    `members: Any`
    :   The type of the None singleton.

    `modified_at: Any`
    :   The type of the None singleton.

    `name: Any`
    :   The type of the None singleton.

    `notes: Any`
    :   The type of the None singleton.

    `owner: Any`
    :   The type of the None singleton.

    `permalink_url: Any`
    :   The type of the None singleton.

    `public: Any`
    :   The type of the None singleton.

    `resource_type: Any`
    :   The type of the None singleton.

    `start_on: Any`
    :   The type of the None singleton.

    `team: Any`
    :   The type of the None singleton.

    `workspace: Any`
    :   The type of the None singleton.

`ProjectsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.asana.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

`ProjectsCreateParams(*args, **kwargs)`
:   Parameters for projects.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.types.ProjectsCreateParamsData`
    :   The type of the None singleton.

`ProjectsCreateParamsData(*args, **kwargs)`
:   Nested schema for ProjectsCreateParams.data

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `default_view: str`
    :   The type of the None singleton.

    `due_on: str`
    :   The type of the None singleton.

    `html_notes: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `notes: str`
    :   The type of the None singleton.

    `privacy_setting: str`
    :   The type of the None singleton.

    `start_on: str`
    :   The type of the None singleton.

    `team: str`
    :   The type of the None singleton.

    `workspace: str`
    :   The type of the None singleton.

`ProjectsDeleteParams(*args, **kwargs)`
:   Parameters for projects.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `project_gid: str`
    :   The type of the None singleton.

`ProjectsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.asana.types.ProjectsSearchFilter`
    :   The type of the None singleton.

`ProjectsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.asana.types.ProjectsStringFilter`
    :   The type of the None singleton.

`ProjectsGetParams(*args, **kwargs)`
:   Parameters for projects.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `project_gid: str`
    :   The type of the None singleton.

`ProjectsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.asana.types.ProjectsSearchFilter`
    :   The type of the None singleton.

`ProjectsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.asana.types.ProjectsSearchFilter`
    :   The type of the None singleton.

`ProjectsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.asana.types.ProjectsInFilter`
    :   The type of the None singleton.

`ProjectsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   The type of the None singleton.

    `color: list[str]`
    :   The type of the None singleton.

    `created_at: list[str]`
    :   The type of the None singleton.

    `current_status: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `custom_field_settings: list[list[typing.Any]]`
    :   The type of the None singleton.

    `custom_fields: list[list[typing.Any]]`
    :   The type of the None singleton.

    `default_view: list[str]`
    :   The type of the None singleton.

    `due_date: list[str]`
    :   The type of the None singleton.

    `due_on: list[str]`
    :   The type of the None singleton.

    `followers: list[list[typing.Any]]`
    :   The type of the None singleton.

    `gid: list[str]`
    :   The type of the None singleton.

    `html_notes: list[str]`
    :   The type of the None singleton.

    `icon: list[str]`
    :   The type of the None singleton.

    `is_template: list[bool]`
    :   The type of the None singleton.

    `members: list[list[typing.Any]]`
    :   The type of the None singleton.

    `modified_at: list[str]`
    :   The type of the None singleton.

    `name: list[str]`
    :   The type of the None singleton.

    `notes: list[str]`
    :   The type of the None singleton.

    `owner: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `permalink_url: list[str]`
    :   The type of the None singleton.

    `public: list[bool]`
    :   The type of the None singleton.

    `resource_type: list[str]`
    :   The type of the None singleton.

    `start_on: list[str]`
    :   The type of the None singleton.

    `team: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `workspace: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

`ProjectsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.asana.types.ProjectsStringFilter`
    :   The type of the None singleton.

`ProjectsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.asana.types.ProjectsStringFilter`
    :   The type of the None singleton.

`ProjectsListParams(*args, **kwargs)`
:   Parameters for projects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `team: str`
    :   The type of the None singleton.

    `workspace: str`
    :   The type of the None singleton.

`ProjectsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.asana.types.ProjectsSearchFilter`
    :   The type of the None singleton.

`ProjectsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.asana.types.ProjectsSearchFilter`
    :   The type of the None singleton.

`ProjectsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.asana.types.ProjectsSearchFilter`
    :   The type of the None singleton.

`ProjectsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.asana.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsInCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsAnyCondition`
    :   The type of the None singleton.

`ProjectsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.asana.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsInCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsAnyCondition]`
    :   The type of the None singleton.

`ProjectsSearchFilter(*args, **kwargs)`
:   Available fields for filtering projects search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `current_status: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `custom_field_settings: list[typing.Any] | None`
    :   The type of the None singleton.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `default_view: str | None`
    :   The type of the None singleton.

    `due_date: str | None`
    :   The type of the None singleton.

    `due_on: str | None`
    :   The type of the None singleton.

    `followers: list[typing.Any] | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `html_notes: str | None`
    :   The type of the None singleton.

    `icon: str | None`
    :   The type of the None singleton.

    `is_template: bool | None`
    :   The type of the None singleton.

    `members: list[typing.Any] | None`
    :   The type of the None singleton.

    `modified_at: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `notes: str | None`
    :   The type of the None singleton.

    `owner: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `permalink_url: str | None`
    :   The type of the None singleton.

    `public: bool | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

    `start_on: str | None`
    :   The type of the None singleton.

    `team: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `workspace: dict[str, typing.Any] | None`
    :   The type of the None singleton.

`ProjectsSearchQuery(*args, **kwargs)`
:   Search query for projects entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.asana.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsInCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.asana.types.ProjectsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.asana.types.ProjectsSortFilter]`
    :   The type of the None singleton.

`ProjectsSortFilter(*args, **kwargs)`
:   Available fields for sorting projects search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `color: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `created_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `current_status: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `custom_field_settings: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `custom_fields: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `default_view: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `due_date: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `due_on: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `followers: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `gid: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `html_notes: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `icon: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `is_template: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `members: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `modified_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `name: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `notes: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `owner: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `permalink_url: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `public: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `resource_type: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `start_on: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `team: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `workspace: Literal['asc', 'desc']`
    :   The type of the None singleton.

`ProjectsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `created_at: str`
    :   The type of the None singleton.

    `current_status: str`
    :   The type of the None singleton.

    `custom_field_settings: str`
    :   The type of the None singleton.

    `custom_fields: str`
    :   The type of the None singleton.

    `default_view: str`
    :   The type of the None singleton.

    `due_date: str`
    :   The type of the None singleton.

    `due_on: str`
    :   The type of the None singleton.

    `followers: str`
    :   The type of the None singleton.

    `gid: str`
    :   The type of the None singleton.

    `html_notes: str`
    :   The type of the None singleton.

    `icon: str`
    :   The type of the None singleton.

    `is_template: str`
    :   The type of the None singleton.

    `members: str`
    :   The type of the None singleton.

    `modified_at: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `notes: str`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `permalink_url: str`
    :   The type of the None singleton.

    `public: str`
    :   The type of the None singleton.

    `resource_type: str`
    :   The type of the None singleton.

    `start_on: str`
    :   The type of the None singleton.

    `team: str`
    :   The type of the None singleton.

    `workspace: str`
    :   The type of the None singleton.

`ProjectsUpdateParams(*args, **kwargs)`
:   Parameters for projects.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.types.ProjectsUpdateParamsData`
    :   The type of the None singleton.

    `project_gid: str`
    :   The type of the None singleton.

`ProjectsUpdateParamsData(*args, **kwargs)`
:   Nested schema for ProjectsUpdateParams.data

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `default_view: str`
    :   The type of the None singleton.

    `due_on: str`
    :   The type of the None singleton.

    `html_notes: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `notes: str`
    :   The type of the None singleton.

    `start_on: str`
    :   The type of the None singleton.

`SectionTasksCreateParams(*args, **kwargs)`
:   Parameters for section_tasks.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.types.SectionTasksCreateParamsData`
    :   The type of the None singleton.

    `section_gid: str`
    :   The type of the None singleton.

`SectionTasksCreateParamsData(*args, **kwargs)`
:   Nested schema for SectionTasksCreateParams.data

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `insert_after: str`
    :   The type of the None singleton.

    `insert_before: str`
    :   The type of the None singleton.

    `task: str`
    :   The type of the None singleton.

`SectionTasksListParams(*args, **kwargs)`
:   Parameters for section_tasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `completed_since: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `section_gid: str`
    :   The type of the None singleton.

`SectionsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.asana.types.SectionsEqCondition | airbyte_agent_sdk.connectors.asana.types.SectionsNeqCondition | airbyte_agent_sdk.connectors.asana.types.SectionsGtCondition | airbyte_agent_sdk.connectors.asana.types.SectionsGteCondition | airbyte_agent_sdk.connectors.asana.types.SectionsLtCondition | airbyte_agent_sdk.connectors.asana.types.SectionsLteCondition | airbyte_agent_sdk.connectors.asana.types.SectionsInCondition | airbyte_agent_sdk.connectors.asana.types.SectionsLikeCondition | airbyte_agent_sdk.connectors.asana.types.SectionsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.SectionsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.SectionsContainsCondition | airbyte_agent_sdk.connectors.asana.types.SectionsNotCondition | airbyte_agent_sdk.connectors.asana.types.SectionsAndCondition | airbyte_agent_sdk.connectors.asana.types.SectionsOrCondition | airbyte_agent_sdk.connectors.asana.types.SectionsAnyCondition]`
    :   The type of the None singleton.

`SectionsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.asana.types.SectionsAnyValueFilter`
    :   The type of the None singleton.

`SectionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   The type of the None singleton.

    `gid: Any`
    :   The type of the None singleton.

    `name: Any`
    :   The type of the None singleton.

    `project: Any`
    :   The type of the None singleton.

    `resource_type: Any`
    :   The type of the None singleton.

`SectionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.asana.types.SectionsAnyValueFilter`
    :   The type of the None singleton.

`SectionsDeleteParams(*args, **kwargs)`
:   Parameters for sections.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `section_gid: str`
    :   The type of the None singleton.

`SectionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.asana.types.SectionsSearchFilter`
    :   The type of the None singleton.

`SectionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.asana.types.SectionsStringFilter`
    :   The type of the None singleton.

`SectionsGetParams(*args, **kwargs)`
:   Parameters for sections.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `section_gid: str`
    :   The type of the None singleton.

`SectionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.asana.types.SectionsSearchFilter`
    :   The type of the None singleton.

`SectionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.asana.types.SectionsSearchFilter`
    :   The type of the None singleton.

`SectionsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.asana.types.SectionsInFilter`
    :   The type of the None singleton.

`SectionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   The type of the None singleton.

    `gid: list[str]`
    :   The type of the None singleton.

    `name: list[str]`
    :   The type of the None singleton.

    `project: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `resource_type: list[str]`
    :   The type of the None singleton.

`SectionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.asana.types.SectionsStringFilter`
    :   The type of the None singleton.

`SectionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.asana.types.SectionsStringFilter`
    :   The type of the None singleton.

`SectionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.asana.types.SectionsSearchFilter`
    :   The type of the None singleton.

`SectionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.asana.types.SectionsSearchFilter`
    :   The type of the None singleton.

`SectionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.asana.types.SectionsSearchFilter`
    :   The type of the None singleton.

`SectionsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.asana.types.SectionsEqCondition | airbyte_agent_sdk.connectors.asana.types.SectionsNeqCondition | airbyte_agent_sdk.connectors.asana.types.SectionsGtCondition | airbyte_agent_sdk.connectors.asana.types.SectionsGteCondition | airbyte_agent_sdk.connectors.asana.types.SectionsLtCondition | airbyte_agent_sdk.connectors.asana.types.SectionsLteCondition | airbyte_agent_sdk.connectors.asana.types.SectionsInCondition | airbyte_agent_sdk.connectors.asana.types.SectionsLikeCondition | airbyte_agent_sdk.connectors.asana.types.SectionsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.SectionsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.SectionsContainsCondition | airbyte_agent_sdk.connectors.asana.types.SectionsNotCondition | airbyte_agent_sdk.connectors.asana.types.SectionsAndCondition | airbyte_agent_sdk.connectors.asana.types.SectionsOrCondition | airbyte_agent_sdk.connectors.asana.types.SectionsAnyCondition`
    :   The type of the None singleton.

`SectionsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.asana.types.SectionsEqCondition | airbyte_agent_sdk.connectors.asana.types.SectionsNeqCondition | airbyte_agent_sdk.connectors.asana.types.SectionsGtCondition | airbyte_agent_sdk.connectors.asana.types.SectionsGteCondition | airbyte_agent_sdk.connectors.asana.types.SectionsLtCondition | airbyte_agent_sdk.connectors.asana.types.SectionsLteCondition | airbyte_agent_sdk.connectors.asana.types.SectionsInCondition | airbyte_agent_sdk.connectors.asana.types.SectionsLikeCondition | airbyte_agent_sdk.connectors.asana.types.SectionsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.SectionsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.SectionsContainsCondition | airbyte_agent_sdk.connectors.asana.types.SectionsNotCondition | airbyte_agent_sdk.connectors.asana.types.SectionsAndCondition | airbyte_agent_sdk.connectors.asana.types.SectionsOrCondition | airbyte_agent_sdk.connectors.asana.types.SectionsAnyCondition]`
    :   The type of the None singleton.

`SectionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering sections search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `project: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

`SectionsSearchQuery(*args, **kwargs)`
:   Search query for sections entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.asana.types.SectionsEqCondition | airbyte_agent_sdk.connectors.asana.types.SectionsNeqCondition | airbyte_agent_sdk.connectors.asana.types.SectionsGtCondition | airbyte_agent_sdk.connectors.asana.types.SectionsGteCondition | airbyte_agent_sdk.connectors.asana.types.SectionsLtCondition | airbyte_agent_sdk.connectors.asana.types.SectionsLteCondition | airbyte_agent_sdk.connectors.asana.types.SectionsInCondition | airbyte_agent_sdk.connectors.asana.types.SectionsLikeCondition | airbyte_agent_sdk.connectors.asana.types.SectionsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.SectionsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.SectionsContainsCondition | airbyte_agent_sdk.connectors.asana.types.SectionsNotCondition | airbyte_agent_sdk.connectors.asana.types.SectionsAndCondition | airbyte_agent_sdk.connectors.asana.types.SectionsOrCondition | airbyte_agent_sdk.connectors.asana.types.SectionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.asana.types.SectionsSortFilter]`
    :   The type of the None singleton.

`SectionsSortFilter(*args, **kwargs)`
:   Available fields for sorting sections search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `gid: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `name: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `project: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `resource_type: Literal['asc', 'desc']`
    :   The type of the None singleton.

`SectionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   The type of the None singleton.

    `gid: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `project: str`
    :   The type of the None singleton.

    `resource_type: str`
    :   The type of the None singleton.

`SectionsUpdateParams(*args, **kwargs)`
:   Parameters for sections.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.types.SectionsUpdateParamsData`
    :   The type of the None singleton.

    `section_gid: str`
    :   The type of the None singleton.

`SectionsUpdateParamsData(*args, **kwargs)`
:   Nested schema for SectionsUpdateParams.data

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

`TagTasksListParams(*args, **kwargs)`
:   Parameters for tag_tasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `tag_gid: str`
    :   The type of the None singleton.

`TagsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.asana.types.TagsEqCondition | airbyte_agent_sdk.connectors.asana.types.TagsNeqCondition | airbyte_agent_sdk.connectors.asana.types.TagsGtCondition | airbyte_agent_sdk.connectors.asana.types.TagsGteCondition | airbyte_agent_sdk.connectors.asana.types.TagsLtCondition | airbyte_agent_sdk.connectors.asana.types.TagsLteCondition | airbyte_agent_sdk.connectors.asana.types.TagsInCondition | airbyte_agent_sdk.connectors.asana.types.TagsLikeCondition | airbyte_agent_sdk.connectors.asana.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.TagsContainsCondition | airbyte_agent_sdk.connectors.asana.types.TagsNotCondition | airbyte_agent_sdk.connectors.asana.types.TagsAndCondition | airbyte_agent_sdk.connectors.asana.types.TagsOrCondition | airbyte_agent_sdk.connectors.asana.types.TagsAnyCondition]`
    :   The type of the None singleton.

`TagsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.asana.types.TagsAnyValueFilter`
    :   The type of the None singleton.

`TagsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: Any`
    :   The type of the None singleton.

    `followers: Any`
    :   The type of the None singleton.

    `gid: Any`
    :   The type of the None singleton.

    `name: Any`
    :   The type of the None singleton.

    `permalink_url: Any`
    :   The type of the None singleton.

    `resource_type: Any`
    :   The type of the None singleton.

    `workspace: Any`
    :   The type of the None singleton.

`TagsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.asana.types.TagsAnyValueFilter`
    :   The type of the None singleton.

`TagsDeleteParams(*args, **kwargs)`
:   Parameters for tags.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `tag_gid: str`
    :   The type of the None singleton.

`TagsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.asana.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.asana.types.TagsStringFilter`
    :   The type of the None singleton.

`TagsGetParams(*args, **kwargs)`
:   Parameters for tags.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `tag_gid: str`
    :   The type of the None singleton.

`TagsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.asana.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.asana.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.asana.types.TagsInFilter`
    :   The type of the None singleton.

`TagsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: list[str]`
    :   The type of the None singleton.

    `followers: list[list[typing.Any]]`
    :   The type of the None singleton.

    `gid: list[str]`
    :   The type of the None singleton.

    `name: list[str]`
    :   The type of the None singleton.

    `permalink_url: list[str]`
    :   The type of the None singleton.

    `resource_type: list[str]`
    :   The type of the None singleton.

    `workspace: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

`TagsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.asana.types.TagsStringFilter`
    :   The type of the None singleton.

`TagsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.asana.types.TagsStringFilter`
    :   The type of the None singleton.

`TagsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.asana.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.asana.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.asana.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.asana.types.TagsEqCondition | airbyte_agent_sdk.connectors.asana.types.TagsNeqCondition | airbyte_agent_sdk.connectors.asana.types.TagsGtCondition | airbyte_agent_sdk.connectors.asana.types.TagsGteCondition | airbyte_agent_sdk.connectors.asana.types.TagsLtCondition | airbyte_agent_sdk.connectors.asana.types.TagsLteCondition | airbyte_agent_sdk.connectors.asana.types.TagsInCondition | airbyte_agent_sdk.connectors.asana.types.TagsLikeCondition | airbyte_agent_sdk.connectors.asana.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.TagsContainsCondition | airbyte_agent_sdk.connectors.asana.types.TagsNotCondition | airbyte_agent_sdk.connectors.asana.types.TagsAndCondition | airbyte_agent_sdk.connectors.asana.types.TagsOrCondition | airbyte_agent_sdk.connectors.asana.types.TagsAnyCondition`
    :   The type of the None singleton.

`TagsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.asana.types.TagsEqCondition | airbyte_agent_sdk.connectors.asana.types.TagsNeqCondition | airbyte_agent_sdk.connectors.asana.types.TagsGtCondition | airbyte_agent_sdk.connectors.asana.types.TagsGteCondition | airbyte_agent_sdk.connectors.asana.types.TagsLtCondition | airbyte_agent_sdk.connectors.asana.types.TagsLteCondition | airbyte_agent_sdk.connectors.asana.types.TagsInCondition | airbyte_agent_sdk.connectors.asana.types.TagsLikeCondition | airbyte_agent_sdk.connectors.asana.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.TagsContainsCondition | airbyte_agent_sdk.connectors.asana.types.TagsNotCondition | airbyte_agent_sdk.connectors.asana.types.TagsAndCondition | airbyte_agent_sdk.connectors.asana.types.TagsOrCondition | airbyte_agent_sdk.connectors.asana.types.TagsAnyCondition]`
    :   The type of the None singleton.

`TagsSearchFilter(*args, **kwargs)`
:   Available fields for filtering tags search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `followers: list[typing.Any] | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `permalink_url: str | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

    `workspace: dict[str, typing.Any] | None`
    :   The type of the None singleton.

`TagsSearchQuery(*args, **kwargs)`
:   Search query for tags entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.asana.types.TagsEqCondition | airbyte_agent_sdk.connectors.asana.types.TagsNeqCondition | airbyte_agent_sdk.connectors.asana.types.TagsGtCondition | airbyte_agent_sdk.connectors.asana.types.TagsGteCondition | airbyte_agent_sdk.connectors.asana.types.TagsLtCondition | airbyte_agent_sdk.connectors.asana.types.TagsLteCondition | airbyte_agent_sdk.connectors.asana.types.TagsInCondition | airbyte_agent_sdk.connectors.asana.types.TagsLikeCondition | airbyte_agent_sdk.connectors.asana.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.TagsContainsCondition | airbyte_agent_sdk.connectors.asana.types.TagsNotCondition | airbyte_agent_sdk.connectors.asana.types.TagsAndCondition | airbyte_agent_sdk.connectors.asana.types.TagsOrCondition | airbyte_agent_sdk.connectors.asana.types.TagsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.asana.types.TagsSortFilter]`
    :   The type of the None singleton.

`TagsSortFilter(*args, **kwargs)`
:   Available fields for sorting tags search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `followers: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `gid: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `name: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `permalink_url: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `resource_type: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `workspace: Literal['asc', 'desc']`
    :   The type of the None singleton.

`TagsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `followers: str`
    :   The type of the None singleton.

    `gid: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `permalink_url: str`
    :   The type of the None singleton.

    `resource_type: str`
    :   The type of the None singleton.

    `workspace: str`
    :   The type of the None singleton.

`TagsUpdateParams(*args, **kwargs)`
:   Parameters for tags.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.types.TagsUpdateParamsData`
    :   The type of the None singleton.

    `tag_gid: str`
    :   The type of the None singleton.

`TagsUpdateParamsData(*args, **kwargs)`
:   Nested schema for TagsUpdateParams.data

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `notes: str`
    :   The type of the None singleton.

`TaskDependenciesListParams(*args, **kwargs)`
:   Parameters for task_dependencies.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `task_gid: str`
    :   The type of the None singleton.

`TaskDependentsListParams(*args, **kwargs)`
:   Parameters for task_dependents.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `task_gid: str`
    :   The type of the None singleton.

`TaskProjectsListParams(*args, **kwargs)`
:   Parameters for task_projects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `task_gid: str`
    :   The type of the None singleton.

`TaskStoriesCreateParams(*args, **kwargs)`
:   Parameters for task_stories.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.types.TaskStoriesCreateParamsData`
    :   The type of the None singleton.

    `task_gid: str`
    :   The type of the None singleton.

`TaskStoriesCreateParamsData(*args, **kwargs)`
:   Nested schema for TaskStoriesCreateParams.data

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `html_text: str`
    :   The type of the None singleton.

    `is_pinned: bool`
    :   The type of the None singleton.

    `text: str`
    :   The type of the None singleton.

`TaskSubtasksListParams(*args, **kwargs)`
:   Parameters for task_subtasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `task_gid: str`
    :   The type of the None singleton.

`TaskTagsCreateParams(*args, **kwargs)`
:   Parameters for task_tags.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.types.TaskTagsCreateParamsData`
    :   The type of the None singleton.

    `task_gid: str`
    :   The type of the None singleton.

`TaskTagsCreateParamsData(*args, **kwargs)`
:   Nested schema for TaskTagsCreateParams.data

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `tag: str`
    :   The type of the None singleton.

`TaskTagsDeleteParams(*args, **kwargs)`
:   Parameters for task_tags.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.types.TaskTagsDeleteParamsData`
    :   The type of the None singleton.

    `task_gid: str`
    :   The type of the None singleton.

`TaskTagsDeleteParamsData(*args, **kwargs)`
:   Nested schema for TaskTagsDeleteParams.data

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `tag: str`
    :   The type of the None singleton.

`TasksAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.asana.types.TasksEqCondition | airbyte_agent_sdk.connectors.asana.types.TasksNeqCondition | airbyte_agent_sdk.connectors.asana.types.TasksGtCondition | airbyte_agent_sdk.connectors.asana.types.TasksGteCondition | airbyte_agent_sdk.connectors.asana.types.TasksLtCondition | airbyte_agent_sdk.connectors.asana.types.TasksLteCondition | airbyte_agent_sdk.connectors.asana.types.TasksInCondition | airbyte_agent_sdk.connectors.asana.types.TasksLikeCondition | airbyte_agent_sdk.connectors.asana.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.asana.types.TasksContainsCondition | airbyte_agent_sdk.connectors.asana.types.TasksNotCondition | airbyte_agent_sdk.connectors.asana.types.TasksAndCondition | airbyte_agent_sdk.connectors.asana.types.TasksOrCondition | airbyte_agent_sdk.connectors.asana.types.TasksAnyCondition]`
    :   The type of the None singleton.

`TasksAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.asana.types.TasksAnyValueFilter`
    :   The type of the None singleton.

`TasksAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actual_time_minutes: Any`
    :   The actual time spent on the task in minutes

    `approval_status: Any`
    :   The type of the None singleton.

    `assignee: Any`
    :   The type of the None singleton.

    `completed: Any`
    :   The type of the None singleton.

    `completed_at: Any`
    :   The type of the None singleton.

    `completed_by: Any`
    :   The type of the None singleton.

    `created_at: Any`
    :   The type of the None singleton.

    `custom_fields: Any`
    :   The type of the None singleton.

    `dependencies: Any`
    :   The type of the None singleton.

    `dependents: Any`
    :   The type of the None singleton.

    `due_at: Any`
    :   The type of the None singleton.

    `due_on: Any`
    :   The type of the None singleton.

    `external: Any`
    :   The type of the None singleton.

    `followers: Any`
    :   The type of the None singleton.

    `gid: Any`
    :   The type of the None singleton.

    `hearted: Any`
    :   The type of the None singleton.

    `hearts: Any`
    :   The type of the None singleton.

    `html_notes: Any`
    :   The type of the None singleton.

    `is_rendered_as_separator: Any`
    :   The type of the None singleton.

    `liked: Any`
    :   The type of the None singleton.

    `likes: Any`
    :   The type of the None singleton.

    `memberships: Any`
    :   The type of the None singleton.

    `modified_at: Any`
    :   The type of the None singleton.

    `name: Any`
    :   The type of the None singleton.

    `notes: Any`
    :   The type of the None singleton.

    `num_hearts: Any`
    :   The type of the None singleton.

    `num_likes: Any`
    :   The type of the None singleton.

    `num_subtasks: Any`
    :   The type of the None singleton.

    `parent: Any`
    :   The type of the None singleton.

    `permalink_url: Any`
    :   The type of the None singleton.

    `projects: Any`
    :   The type of the None singleton.

    `resource_subtype: Any`
    :   The type of the None singleton.

    `resource_type: Any`
    :   The type of the None singleton.

    `start_on: Any`
    :   The type of the None singleton.

    `tags: Any`
    :   The type of the None singleton.

    `workspace: Any`
    :   The type of the None singleton.

`TasksContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.asana.types.TasksAnyValueFilter`
    :   The type of the None singleton.

`TasksCreateParams(*args, **kwargs)`
:   Parameters for tasks.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.types.TasksCreateParamsData`
    :   The type of the None singleton.

`TasksCreateParamsData(*args, **kwargs)`
:   Nested schema for TasksCreateParams.data

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: str`
    :   The type of the None singleton.

    `completed: bool`
    :   The type of the None singleton.

    `due_at: str`
    :   The type of the None singleton.

    `due_on: str`
    :   The type of the None singleton.

    `followers: list[str]`
    :   The type of the None singleton.

    `html_notes: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `notes: str`
    :   The type of the None singleton.

    `parent: str`
    :   The type of the None singleton.

    `projects: list[str]`
    :   The type of the None singleton.

    `resource_subtype: str`
    :   The type of the None singleton.

    `start_on: str`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

    `workspace: str`
    :   The type of the None singleton.

`TasksDeleteParams(*args, **kwargs)`
:   Parameters for tasks.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `task_gid: str`
    :   The type of the None singleton.

`TasksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.asana.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.asana.types.TasksStringFilter`
    :   The type of the None singleton.

`TasksGetParams(*args, **kwargs)`
:   Parameters for tasks.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `task_gid: str`
    :   The type of the None singleton.

`TasksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.asana.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.asana.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.asana.types.TasksInFilter`
    :   The type of the None singleton.

`TasksInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actual_time_minutes: list[int]`
    :   The actual time spent on the task in minutes

    `approval_status: list[str]`
    :   The type of the None singleton.

    `assignee: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `completed: list[bool]`
    :   The type of the None singleton.

    `completed_at: list[str]`
    :   The type of the None singleton.

    `completed_by: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `created_at: list[str]`
    :   The type of the None singleton.

    `custom_fields: list[list[typing.Any]]`
    :   The type of the None singleton.

    `dependencies: list[list[typing.Any]]`
    :   The type of the None singleton.

    `dependents: list[list[typing.Any]]`
    :   The type of the None singleton.

    `due_at: list[str]`
    :   The type of the None singleton.

    `due_on: list[str]`
    :   The type of the None singleton.

    `external: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `followers: list[list[typing.Any]]`
    :   The type of the None singleton.

    `gid: list[str]`
    :   The type of the None singleton.

    `hearted: list[bool]`
    :   The type of the None singleton.

    `hearts: list[list[typing.Any]]`
    :   The type of the None singleton.

    `html_notes: list[str]`
    :   The type of the None singleton.

    `is_rendered_as_separator: list[bool]`
    :   The type of the None singleton.

    `liked: list[bool]`
    :   The type of the None singleton.

    `likes: list[list[typing.Any]]`
    :   The type of the None singleton.

    `memberships: list[list[typing.Any]]`
    :   The type of the None singleton.

    `modified_at: list[str]`
    :   The type of the None singleton.

    `name: list[str]`
    :   The type of the None singleton.

    `notes: list[str]`
    :   The type of the None singleton.

    `num_hearts: list[int]`
    :   The type of the None singleton.

    `num_likes: list[int]`
    :   The type of the None singleton.

    `num_subtasks: list[int]`
    :   The type of the None singleton.

    `parent: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `permalink_url: list[str]`
    :   The type of the None singleton.

    `projects: list[list[typing.Any]]`
    :   The type of the None singleton.

    `resource_subtype: list[str]`
    :   The type of the None singleton.

    `resource_type: list[str]`
    :   The type of the None singleton.

    `start_on: list[str]`
    :   The type of the None singleton.

    `tags: list[list[typing.Any]]`
    :   The type of the None singleton.

    `workspace: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

`TasksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.asana.types.TasksStringFilter`
    :   The type of the None singleton.

`TasksLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.asana.types.TasksStringFilter`
    :   The type of the None singleton.

`TasksListParams(*args, **kwargs)`
:   Parameters for tasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: str`
    :   The type of the None singleton.

    `completed_since: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `modified_since: str`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `project: str`
    :   The type of the None singleton.

    `section: str`
    :   The type of the None singleton.

    `workspace: str`
    :   The type of the None singleton.

`TasksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.asana.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.asana.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.asana.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.asana.types.TasksEqCondition | airbyte_agent_sdk.connectors.asana.types.TasksNeqCondition | airbyte_agent_sdk.connectors.asana.types.TasksGtCondition | airbyte_agent_sdk.connectors.asana.types.TasksGteCondition | airbyte_agent_sdk.connectors.asana.types.TasksLtCondition | airbyte_agent_sdk.connectors.asana.types.TasksLteCondition | airbyte_agent_sdk.connectors.asana.types.TasksInCondition | airbyte_agent_sdk.connectors.asana.types.TasksLikeCondition | airbyte_agent_sdk.connectors.asana.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.asana.types.TasksContainsCondition | airbyte_agent_sdk.connectors.asana.types.TasksNotCondition | airbyte_agent_sdk.connectors.asana.types.TasksAndCondition | airbyte_agent_sdk.connectors.asana.types.TasksOrCondition | airbyte_agent_sdk.connectors.asana.types.TasksAnyCondition`
    :   The type of the None singleton.

`TasksOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.asana.types.TasksEqCondition | airbyte_agent_sdk.connectors.asana.types.TasksNeqCondition | airbyte_agent_sdk.connectors.asana.types.TasksGtCondition | airbyte_agent_sdk.connectors.asana.types.TasksGteCondition | airbyte_agent_sdk.connectors.asana.types.TasksLtCondition | airbyte_agent_sdk.connectors.asana.types.TasksLteCondition | airbyte_agent_sdk.connectors.asana.types.TasksInCondition | airbyte_agent_sdk.connectors.asana.types.TasksLikeCondition | airbyte_agent_sdk.connectors.asana.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.asana.types.TasksContainsCondition | airbyte_agent_sdk.connectors.asana.types.TasksNotCondition | airbyte_agent_sdk.connectors.asana.types.TasksAndCondition | airbyte_agent_sdk.connectors.asana.types.TasksOrCondition | airbyte_agent_sdk.connectors.asana.types.TasksAnyCondition]`
    :   The type of the None singleton.

`TasksSearchFilter(*args, **kwargs)`
:   Available fields for filtering tasks search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actual_time_minutes: int | None`
    :   The actual time spent on the task in minutes

    `approval_status: str | None`
    :   The type of the None singleton.

    `assignee: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `completed: bool | None`
    :   The type of the None singleton.

    `completed_at: str | None`
    :   The type of the None singleton.

    `completed_by: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `dependencies: list[typing.Any] | None`
    :   The type of the None singleton.

    `dependents: list[typing.Any] | None`
    :   The type of the None singleton.

    `due_at: str | None`
    :   The type of the None singleton.

    `due_on: str | None`
    :   The type of the None singleton.

    `external: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `followers: list[typing.Any] | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `hearted: bool | None`
    :   The type of the None singleton.

    `hearts: list[typing.Any] | None`
    :   The type of the None singleton.

    `html_notes: str | None`
    :   The type of the None singleton.

    `is_rendered_as_separator: bool | None`
    :   The type of the None singleton.

    `liked: bool | None`
    :   The type of the None singleton.

    `likes: list[typing.Any] | None`
    :   The type of the None singleton.

    `memberships: list[typing.Any] | None`
    :   The type of the None singleton.

    `modified_at: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `notes: str | None`
    :   The type of the None singleton.

    `num_hearts: int | None`
    :   The type of the None singleton.

    `num_likes: int | None`
    :   The type of the None singleton.

    `num_subtasks: int | None`
    :   The type of the None singleton.

    `parent: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `permalink_url: str | None`
    :   The type of the None singleton.

    `projects: list[typing.Any] | None`
    :   The type of the None singleton.

    `resource_subtype: str | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

    `start_on: str | None`
    :   The type of the None singleton.

    `tags: list[typing.Any] | None`
    :   The type of the None singleton.

    `workspace: dict[str, typing.Any] | None`
    :   The type of the None singleton.

`TasksSearchQuery(*args, **kwargs)`
:   Search query for tasks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.asana.types.TasksEqCondition | airbyte_agent_sdk.connectors.asana.types.TasksNeqCondition | airbyte_agent_sdk.connectors.asana.types.TasksGtCondition | airbyte_agent_sdk.connectors.asana.types.TasksGteCondition | airbyte_agent_sdk.connectors.asana.types.TasksLtCondition | airbyte_agent_sdk.connectors.asana.types.TasksLteCondition | airbyte_agent_sdk.connectors.asana.types.TasksInCondition | airbyte_agent_sdk.connectors.asana.types.TasksLikeCondition | airbyte_agent_sdk.connectors.asana.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.asana.types.TasksContainsCondition | airbyte_agent_sdk.connectors.asana.types.TasksNotCondition | airbyte_agent_sdk.connectors.asana.types.TasksAndCondition | airbyte_agent_sdk.connectors.asana.types.TasksOrCondition | airbyte_agent_sdk.connectors.asana.types.TasksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.asana.types.TasksSortFilter]`
    :   The type of the None singleton.

`TasksSortFilter(*args, **kwargs)`
:   Available fields for sorting tasks search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actual_time_minutes: Literal['asc', 'desc']`
    :   The actual time spent on the task in minutes

    `approval_status: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `assignee: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `completed: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `completed_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `completed_by: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `created_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `custom_fields: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `dependencies: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `dependents: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `due_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `due_on: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `external: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `followers: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `gid: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `hearted: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `hearts: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `html_notes: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `is_rendered_as_separator: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `liked: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `likes: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `memberships: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `modified_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `name: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `notes: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `num_hearts: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `num_likes: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `num_subtasks: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `parent: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `permalink_url: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `projects: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `resource_subtype: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `resource_type: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `start_on: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `tags: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `workspace: Literal['asc', 'desc']`
    :   The type of the None singleton.

`TasksStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actual_time_minutes: str`
    :   The actual time spent on the task in minutes

    `approval_status: str`
    :   The type of the None singleton.

    `assignee: str`
    :   The type of the None singleton.

    `completed: str`
    :   The type of the None singleton.

    `completed_at: str`
    :   The type of the None singleton.

    `completed_by: str`
    :   The type of the None singleton.

    `created_at: str`
    :   The type of the None singleton.

    `custom_fields: str`
    :   The type of the None singleton.

    `dependencies: str`
    :   The type of the None singleton.

    `dependents: str`
    :   The type of the None singleton.

    `due_at: str`
    :   The type of the None singleton.

    `due_on: str`
    :   The type of the None singleton.

    `external: str`
    :   The type of the None singleton.

    `followers: str`
    :   The type of the None singleton.

    `gid: str`
    :   The type of the None singleton.

    `hearted: str`
    :   The type of the None singleton.

    `hearts: str`
    :   The type of the None singleton.

    `html_notes: str`
    :   The type of the None singleton.

    `is_rendered_as_separator: str`
    :   The type of the None singleton.

    `liked: str`
    :   The type of the None singleton.

    `likes: str`
    :   The type of the None singleton.

    `memberships: str`
    :   The type of the None singleton.

    `modified_at: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `notes: str`
    :   The type of the None singleton.

    `num_hearts: str`
    :   The type of the None singleton.

    `num_likes: str`
    :   The type of the None singleton.

    `num_subtasks: str`
    :   The type of the None singleton.

    `parent: str`
    :   The type of the None singleton.

    `permalink_url: str`
    :   The type of the None singleton.

    `projects: str`
    :   The type of the None singleton.

    `resource_subtype: str`
    :   The type of the None singleton.

    `resource_type: str`
    :   The type of the None singleton.

    `start_on: str`
    :   The type of the None singleton.

    `tags: str`
    :   The type of the None singleton.

    `workspace: str`
    :   The type of the None singleton.

`TasksUpdateParams(*args, **kwargs)`
:   Parameters for tasks.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.types.TasksUpdateParamsData`
    :   The type of the None singleton.

    `task_gid: str`
    :   The type of the None singleton.

`TasksUpdateParamsData(*args, **kwargs)`
:   Nested schema for TasksUpdateParams.data

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: str`
    :   The type of the None singleton.

    `completed: bool`
    :   The type of the None singleton.

    `due_at: str`
    :   The type of the None singleton.

    `due_on: str`
    :   The type of the None singleton.

    `html_notes: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `notes: str`
    :   The type of the None singleton.

    `start_on: str`
    :   The type of the None singleton.

`TeamProjectsListParams(*args, **kwargs)`
:   Parameters for team_projects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `team_gid: str`
    :   The type of the None singleton.

`TeamUsersListParams(*args, **kwargs)`
:   Parameters for team_users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `team_gid: str`
    :   The type of the None singleton.

`TeamsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.asana.types.TeamsEqCondition | airbyte_agent_sdk.connectors.asana.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.asana.types.TeamsGtCondition | airbyte_agent_sdk.connectors.asana.types.TeamsGteCondition | airbyte_agent_sdk.connectors.asana.types.TeamsLtCondition | airbyte_agent_sdk.connectors.asana.types.TeamsLteCondition | airbyte_agent_sdk.connectors.asana.types.TeamsInCondition | airbyte_agent_sdk.connectors.asana.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.asana.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.asana.types.TeamsNotCondition | airbyte_agent_sdk.connectors.asana.types.TeamsAndCondition | airbyte_agent_sdk.connectors.asana.types.TeamsOrCondition | airbyte_agent_sdk.connectors.asana.types.TeamsAnyCondition]`
    :   The type of the None singleton.

`TeamsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.asana.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

`TeamsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: Any`
    :   The type of the None singleton.

    `gid: Any`
    :   The type of the None singleton.

    `html_description: Any`
    :   The type of the None singleton.

    `name: Any`
    :   The type of the None singleton.

    `organization: Any`
    :   The type of the None singleton.

    `permalink_url: Any`
    :   The type of the None singleton.

    `resource_type: Any`
    :   The type of the None singleton.

`TeamsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.asana.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

`TeamsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.asana.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.asana.types.TeamsStringFilter`
    :   The type of the None singleton.

`TeamsGetParams(*args, **kwargs)`
:   Parameters for teams.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `team_gid: str`
    :   The type of the None singleton.

`TeamsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.asana.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.asana.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.asana.types.TeamsInFilter`
    :   The type of the None singleton.

`TeamsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: list[str]`
    :   The type of the None singleton.

    `gid: list[str]`
    :   The type of the None singleton.

    `html_description: list[str]`
    :   The type of the None singleton.

    `name: list[str]`
    :   The type of the None singleton.

    `organization: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `permalink_url: list[str]`
    :   The type of the None singleton.

    `resource_type: list[str]`
    :   The type of the None singleton.

`TeamsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.asana.types.TeamsStringFilter`
    :   The type of the None singleton.

`TeamsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.asana.types.TeamsStringFilter`
    :   The type of the None singleton.

`TeamsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.asana.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.asana.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.asana.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.asana.types.TeamsEqCondition | airbyte_agent_sdk.connectors.asana.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.asana.types.TeamsGtCondition | airbyte_agent_sdk.connectors.asana.types.TeamsGteCondition | airbyte_agent_sdk.connectors.asana.types.TeamsLtCondition | airbyte_agent_sdk.connectors.asana.types.TeamsLteCondition | airbyte_agent_sdk.connectors.asana.types.TeamsInCondition | airbyte_agent_sdk.connectors.asana.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.asana.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.asana.types.TeamsNotCondition | airbyte_agent_sdk.connectors.asana.types.TeamsAndCondition | airbyte_agent_sdk.connectors.asana.types.TeamsOrCondition | airbyte_agent_sdk.connectors.asana.types.TeamsAnyCondition`
    :   The type of the None singleton.

`TeamsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.asana.types.TeamsEqCondition | airbyte_agent_sdk.connectors.asana.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.asana.types.TeamsGtCondition | airbyte_agent_sdk.connectors.asana.types.TeamsGteCondition | airbyte_agent_sdk.connectors.asana.types.TeamsLtCondition | airbyte_agent_sdk.connectors.asana.types.TeamsLteCondition | airbyte_agent_sdk.connectors.asana.types.TeamsInCondition | airbyte_agent_sdk.connectors.asana.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.asana.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.asana.types.TeamsNotCondition | airbyte_agent_sdk.connectors.asana.types.TeamsAndCondition | airbyte_agent_sdk.connectors.asana.types.TeamsOrCondition | airbyte_agent_sdk.connectors.asana.types.TeamsAnyCondition]`
    :   The type of the None singleton.

`TeamsSearchFilter(*args, **kwargs)`
:   Available fields for filtering teams search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `html_description: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `organization: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `permalink_url: str | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

`TeamsSearchQuery(*args, **kwargs)`
:   Search query for teams entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.asana.types.TeamsEqCondition | airbyte_agent_sdk.connectors.asana.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.asana.types.TeamsGtCondition | airbyte_agent_sdk.connectors.asana.types.TeamsGteCondition | airbyte_agent_sdk.connectors.asana.types.TeamsLtCondition | airbyte_agent_sdk.connectors.asana.types.TeamsLteCondition | airbyte_agent_sdk.connectors.asana.types.TeamsInCondition | airbyte_agent_sdk.connectors.asana.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.asana.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.asana.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.asana.types.TeamsNotCondition | airbyte_agent_sdk.connectors.asana.types.TeamsAndCondition | airbyte_agent_sdk.connectors.asana.types.TeamsOrCondition | airbyte_agent_sdk.connectors.asana.types.TeamsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.asana.types.TeamsSortFilter]`
    :   The type of the None singleton.

`TeamsSortFilter(*args, **kwargs)`
:   Available fields for sorting teams search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `gid: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `html_description: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `name: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `organization: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `permalink_url: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `resource_type: Literal['asc', 'desc']`
    :   The type of the None singleton.

`TeamsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str`
    :   The type of the None singleton.

    `gid: str`
    :   The type of the None singleton.

    `html_description: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `organization: str`
    :   The type of the None singleton.

    `permalink_url: str`
    :   The type of the None singleton.

    `resource_type: str`
    :   The type of the None singleton.

`UserTeamsListParams(*args, **kwargs)`
:   Parameters for user_teams.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `organization: str`
    :   The type of the None singleton.

    `user_gid: str`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.asana.types.UsersEqCondition | airbyte_agent_sdk.connectors.asana.types.UsersNeqCondition | airbyte_agent_sdk.connectors.asana.types.UsersGtCondition | airbyte_agent_sdk.connectors.asana.types.UsersGteCondition | airbyte_agent_sdk.connectors.asana.types.UsersLtCondition | airbyte_agent_sdk.connectors.asana.types.UsersLteCondition | airbyte_agent_sdk.connectors.asana.types.UsersInCondition | airbyte_agent_sdk.connectors.asana.types.UsersLikeCondition | airbyte_agent_sdk.connectors.asana.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.asana.types.UsersContainsCondition | airbyte_agent_sdk.connectors.asana.types.UsersNotCondition | airbyte_agent_sdk.connectors.asana.types.UsersAndCondition | airbyte_agent_sdk.connectors.asana.types.UsersOrCondition | airbyte_agent_sdk.connectors.asana.types.UsersAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.asana.types.UsersAnyValueFilter`
    :   The type of the None singleton.

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: Any`
    :   The type of the None singleton.

    `gid: Any`
    :   The type of the None singleton.

    `name: Any`
    :   The type of the None singleton.

    `photo: Any`
    :   The type of the None singleton.

    `resource_type: Any`
    :   The type of the None singleton.

    `workspaces: Any`
    :   The type of the None singleton.

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.asana.types.UsersAnyValueFilter`
    :   The type of the None singleton.

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.asana.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.asana.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `user_gid: str`
    :   The type of the None singleton.

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.asana.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.asana.types.UsersSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.asana.types.UsersInFilter`
    :   The type of the None singleton.

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: list[str]`
    :   The type of the None singleton.

    `gid: list[str]`
    :   The type of the None singleton.

    `name: list[str]`
    :   The type of the None singleton.

    `photo: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `resource_type: list[str]`
    :   The type of the None singleton.

    `workspaces: list[list[typing.Any]]`
    :   The type of the None singleton.

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.asana.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.asana.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `team: str`
    :   The type of the None singleton.

    `workspace: str`
    :   The type of the None singleton.

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.asana.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.asana.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.asana.types.UsersSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.asana.types.UsersEqCondition | airbyte_agent_sdk.connectors.asana.types.UsersNeqCondition | airbyte_agent_sdk.connectors.asana.types.UsersGtCondition | airbyte_agent_sdk.connectors.asana.types.UsersGteCondition | airbyte_agent_sdk.connectors.asana.types.UsersLtCondition | airbyte_agent_sdk.connectors.asana.types.UsersLteCondition | airbyte_agent_sdk.connectors.asana.types.UsersInCondition | airbyte_agent_sdk.connectors.asana.types.UsersLikeCondition | airbyte_agent_sdk.connectors.asana.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.asana.types.UsersContainsCondition | airbyte_agent_sdk.connectors.asana.types.UsersNotCondition | airbyte_agent_sdk.connectors.asana.types.UsersAndCondition | airbyte_agent_sdk.connectors.asana.types.UsersOrCondition | airbyte_agent_sdk.connectors.asana.types.UsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.asana.types.UsersEqCondition | airbyte_agent_sdk.connectors.asana.types.UsersNeqCondition | airbyte_agent_sdk.connectors.asana.types.UsersGtCondition | airbyte_agent_sdk.connectors.asana.types.UsersGteCondition | airbyte_agent_sdk.connectors.asana.types.UsersLtCondition | airbyte_agent_sdk.connectors.asana.types.UsersLteCondition | airbyte_agent_sdk.connectors.asana.types.UsersInCondition | airbyte_agent_sdk.connectors.asana.types.UsersLikeCondition | airbyte_agent_sdk.connectors.asana.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.asana.types.UsersContainsCondition | airbyte_agent_sdk.connectors.asana.types.UsersNotCondition | airbyte_agent_sdk.connectors.asana.types.UsersAndCondition | airbyte_agent_sdk.connectors.asana.types.UsersOrCondition | airbyte_agent_sdk.connectors.asana.types.UsersAnyCondition]`
    :   The type of the None singleton.

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: str | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `photo: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

    `workspaces: list[typing.Any] | None`
    :   The type of the None singleton.

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.asana.types.UsersEqCondition | airbyte_agent_sdk.connectors.asana.types.UsersNeqCondition | airbyte_agent_sdk.connectors.asana.types.UsersGtCondition | airbyte_agent_sdk.connectors.asana.types.UsersGteCondition | airbyte_agent_sdk.connectors.asana.types.UsersLtCondition | airbyte_agent_sdk.connectors.asana.types.UsersLteCondition | airbyte_agent_sdk.connectors.asana.types.UsersInCondition | airbyte_agent_sdk.connectors.asana.types.UsersLikeCondition | airbyte_agent_sdk.connectors.asana.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.asana.types.UsersContainsCondition | airbyte_agent_sdk.connectors.asana.types.UsersNotCondition | airbyte_agent_sdk.connectors.asana.types.UsersAndCondition | airbyte_agent_sdk.connectors.asana.types.UsersOrCondition | airbyte_agent_sdk.connectors.asana.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.asana.types.UsersSortFilter]`
    :   The type of the None singleton.

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `gid: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `name: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `photo: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `resource_type: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `workspaces: Literal['asc', 'desc']`
    :   The type of the None singleton.

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: str`
    :   The type of the None singleton.

    `gid: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `photo: str`
    :   The type of the None singleton.

    `resource_type: str`
    :   The type of the None singleton.

    `workspaces: str`
    :   The type of the None singleton.

`WorkspaceMembershipsCreateParams(*args, **kwargs)`
:   Parameters for workspace_memberships.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.types.WorkspaceMembershipsCreateParamsData`
    :   The type of the None singleton.

    `workspace_gid: str`
    :   The type of the None singleton.

`WorkspaceMembershipsCreateParamsData(*args, **kwargs)`
:   Nested schema for WorkspaceMembershipsCreateParams.data

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `user: str`
    :   The type of the None singleton.

`WorkspaceProjectsListParams(*args, **kwargs)`
:   Parameters for workspace_projects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `workspace_gid: str`
    :   The type of the None singleton.

`WorkspaceTagsCreateParams(*args, **kwargs)`
:   Parameters for workspace_tags.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.types.WorkspaceTagsCreateParamsData`
    :   The type of the None singleton.

    `workspace_gid: str`
    :   The type of the None singleton.

`WorkspaceTagsCreateParamsData(*args, **kwargs)`
:   Nested schema for WorkspaceTagsCreateParams.data

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `notes: str`
    :   The type of the None singleton.

`WorkspaceTagsListParams(*args, **kwargs)`
:   Parameters for workspace_tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `workspace_gid: str`
    :   The type of the None singleton.

`WorkspaceTaskSearchListParams(*args, **kwargs)`
:   Parameters for workspace_task_search.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee_any: str`
    :   The type of the None singleton.

    `completed: bool`
    :   The type of the None singleton.

    `created_at_after: str`
    :   The type of the None singleton.

    `created_at_before: str`
    :   The type of the None singleton.

    `due_on_after: str`
    :   The type of the None singleton.

    `due_on_before: str`
    :   The type of the None singleton.

    `followers_any: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `modified_at_after: str`
    :   The type of the None singleton.

    `modified_at_before: str`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `projects_any: str`
    :   The type of the None singleton.

    `resource_subtype: str`
    :   The type of the None singleton.

    `sections_any: str`
    :   The type of the None singleton.

    `sort_ascending: bool`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `teams_any: str`
    :   The type of the None singleton.

    `text: str`
    :   The type of the None singleton.

    `workspace_gid: str`
    :   The type of the None singleton.

`WorkspaceTeamsListParams(*args, **kwargs)`
:   Parameters for workspace_teams.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `workspace_gid: str`
    :   The type of the None singleton.

`WorkspaceUsersListParams(*args, **kwargs)`
:   Parameters for workspace_users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

    `workspace_gid: str`
    :   The type of the None singleton.

`WorkspacesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.asana.types.WorkspacesEqCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesNeqCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesGtCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesGteCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesLtCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesLteCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesInCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesLikeCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesKeywordCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesContainsCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesNotCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesAndCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesOrCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesAnyCondition]`
    :   The type of the None singleton.

`WorkspacesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.asana.types.WorkspacesAnyValueFilter`
    :   The type of the None singleton.

`WorkspacesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email_domains: Any`
    :   The type of the None singleton.

    `gid: Any`
    :   The type of the None singleton.

    `is_organization: Any`
    :   The type of the None singleton.

    `name: Any`
    :   The type of the None singleton.

    `resource_type: Any`
    :   The type of the None singleton.

`WorkspacesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.asana.types.WorkspacesAnyValueFilter`
    :   The type of the None singleton.

`WorkspacesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.asana.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.asana.types.WorkspacesStringFilter`
    :   The type of the None singleton.

`WorkspacesGetParams(*args, **kwargs)`
:   Parameters for workspaces.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `workspace_gid: str`
    :   The type of the None singleton.

`WorkspacesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.asana.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.asana.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.asana.types.WorkspacesInFilter`
    :   The type of the None singleton.

`WorkspacesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email_domains: list[list[typing.Any]]`
    :   The type of the None singleton.

    `gid: list[str]`
    :   The type of the None singleton.

    `is_organization: list[bool]`
    :   The type of the None singleton.

    `name: list[str]`
    :   The type of the None singleton.

    `resource_type: list[str]`
    :   The type of the None singleton.

`WorkspacesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.asana.types.WorkspacesStringFilter`
    :   The type of the None singleton.

`WorkspacesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.asana.types.WorkspacesStringFilter`
    :   The type of the None singleton.

`WorkspacesListParams(*args, **kwargs)`
:   Parameters for workspaces.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: str`
    :   The type of the None singleton.

`WorkspacesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.asana.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.asana.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.asana.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.asana.types.WorkspacesEqCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesNeqCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesGtCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesGteCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesLtCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesLteCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesInCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesLikeCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesKeywordCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesContainsCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesNotCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesAndCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesOrCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesAnyCondition`
    :   The type of the None singleton.

`WorkspacesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.asana.types.WorkspacesEqCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesNeqCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesGtCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesGteCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesLtCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesLteCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesInCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesLikeCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesKeywordCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesContainsCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesNotCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesAndCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesOrCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesAnyCondition]`
    :   The type of the None singleton.

`WorkspacesSearchFilter(*args, **kwargs)`
:   Available fields for filtering workspaces search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email_domains: list[typing.Any] | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `is_organization: bool | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

`WorkspacesSearchQuery(*args, **kwargs)`
:   Search query for workspaces entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.asana.types.WorkspacesEqCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesNeqCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesGtCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesGteCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesLtCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesLteCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesInCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesLikeCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesFuzzyCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesKeywordCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesContainsCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesNotCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesAndCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesOrCondition | airbyte_agent_sdk.connectors.asana.types.WorkspacesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.asana.types.WorkspacesSortFilter]`
    :   The type of the None singleton.

`WorkspacesSortFilter(*args, **kwargs)`
:   Available fields for sorting workspaces search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email_domains: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `gid: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `is_organization: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `name: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `resource_type: Literal['asc', 'desc']`
    :   The type of the None singleton.

`WorkspacesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email_domains: str`
    :   The type of the None singleton.

    `gid: str`
    :   The type of the None singleton.

    `is_organization: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `resource_type: str`
    :   The type of the None singleton.