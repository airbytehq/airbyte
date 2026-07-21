---
id: airbyte_agent_sdk-connectors-google_drive-types
title: airbyte_agent_sdk.connectors.google_drive.types
---

Module airbyte_agent_sdk.connectors.google_drive.types
======================================================
Type definitions for google-drive connector.

Classes
-------

<a id="AboutGetParams"></a>

`AboutGetParams(*args, **kwargs)`
:   Parameters for about.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

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

<a id="ChangesListParams"></a>

`ChangesListParams(*args, **kwargs)`
:   Parameters for changes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `drive_id: str`
    :   The type of the None singleton.

    `include_items_from_all_drives: bool`
    :   The type of the None singleton.

    `include_removed: bool`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `restrict_to_my_drive: bool`
    :   The type of the None singleton.

    `spaces: str`
    :   The type of the None singleton.

    `supports_all_drives: bool`
    :   The type of the None singleton.

<a id="ChangesStartPageTokenGetParams"></a>

`ChangesStartPageTokenGetParams(*args, **kwargs)`
:   Parameters for changes_start_page_token.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `drive_id: str`
    :   The type of the None singleton.

    `supports_all_drives: bool`
    :   The type of the None singleton.

<a id="CommentsGetParams"></a>

`CommentsGetParams(*args, **kwargs)`
:   Parameters for comments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `comment_id: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `file_id: str`
    :   The type of the None singleton.

    `include_deleted: bool`
    :   The type of the None singleton.

<a id="CommentsListParams"></a>

`CommentsListParams(*args, **kwargs)`
:   Parameters for comments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `file_id: str`
    :   The type of the None singleton.

    `include_deleted: bool`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `start_modified_time: str`
    :   The type of the None singleton.

<a id="DrivesGetParams"></a>

`DrivesGetParams(*args, **kwargs)`
:   Parameters for drives.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `drive_id: str`
    :   The type of the None singleton.

    `use_domain_admin_access: bool`
    :   The type of the None singleton.

<a id="DrivesListParams"></a>

`DrivesListParams(*args, **kwargs)`
:   Parameters for drives.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

    `use_domain_admin_access: bool`
    :   The type of the None singleton.

<a id="FilesAndCondition"></a>

`FilesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.google_drive.types.FilesEqCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesNeqCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesGtCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesGteCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesLtCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesLteCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesInCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesLikeCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesFuzzyCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesKeywordCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesContainsCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesNotCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesAndCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesOrCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesAnyCondition]`
    :   The type of the None singleton.

<a id="FilesAnyCondition"></a>

`FilesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.google_drive.types.FilesAnyValueFilter`
    :   The type of the None singleton.

<a id="FilesAnyValueFilter"></a>

`FilesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: Any`
    :   Extracted text content of the file.

    `file_name: Any`
    :   Name of the file.

    `file_path: Any`
    :   Full path of the file within the synced Drive folder.

    `id: Any`
    :   Unique identifier of the file in Google Drive.

    `mime_type: Any`
    :   MIME type of the file.

    `updated_at: Any`
    :   Timestamp of the last modification to the file.

<a id="FilesContainsCondition"></a>

`FilesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.google_drive.types.FilesAnyValueFilter`
    :   The type of the None singleton.

<a id="FilesCreateParams"></a>

`FilesCreateParams(*args, **kwargs)`
:   Parameters for files.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str`
    :   The type of the None singleton.

    `mime_type: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `parents: list[str]`
    :   The type of the None singleton.

<a id="FilesDeleteParams"></a>

`FilesDeleteParams(*args, **kwargs)`
:   Parameters for files.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `file_id: str`
    :   The type of the None singleton.

    `supports_all_drives: bool`
    :   The type of the None singleton.

<a id="FilesDownloadParams"></a>

`FilesDownloadParams(*args, **kwargs)`
:   Parameters for files.download operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `acknowledge_abuse: bool`
    :   The type of the None singleton.

    `alt: str`
    :   The type of the None singleton.

    `file_id: str`
    :   The type of the None singleton.

    `range_header: str`
    :   The type of the None singleton.

    `supports_all_drives: bool`
    :   The type of the None singleton.

<a id="FilesEqCondition"></a>

`FilesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.google_drive.types.FilesSearchFilter`
    :   The type of the None singleton.

<a id="FilesExportDownloadParams"></a>

`FilesExportDownloadParams(*args, **kwargs)`
:   Parameters for files_export.download operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `file_id: str`
    :   The type of the None singleton.

    `mime_type: str`
    :   The type of the None singleton.

    `range_header: str`
    :   The type of the None singleton.

<a id="FilesFuzzyCondition"></a>

`FilesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.google_drive.types.FilesStringFilter`
    :   The type of the None singleton.

<a id="FilesGetParams"></a>

`FilesGetParams(*args, **kwargs)`
:   Parameters for files.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `file_id: str`
    :   The type of the None singleton.

    `supports_all_drives: bool`
    :   The type of the None singleton.

<a id="FilesGtCondition"></a>

`FilesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.google_drive.types.FilesSearchFilter`
    :   The type of the None singleton.

<a id="FilesGteCondition"></a>

`FilesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.google_drive.types.FilesSearchFilter`
    :   The type of the None singleton.

<a id="FilesInCondition"></a>

`FilesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.google_drive.types.FilesInFilter`
    :   The type of the None singleton.

<a id="FilesInFilter"></a>

`FilesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: list[str]`
    :   Extracted text content of the file.

    `file_name: list[str]`
    :   Name of the file.

    `file_path: list[str]`
    :   Full path of the file within the synced Drive folder.

    `id: list[str]`
    :   Unique identifier of the file in Google Drive.

    `mime_type: list[str]`
    :   MIME type of the file.

    `updated_at: list[str]`
    :   Timestamp of the last modification to the file.

<a id="FilesKeywordCondition"></a>

`FilesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.google_drive.types.FilesStringFilter`
    :   The type of the None singleton.

<a id="FilesLikeCondition"></a>

`FilesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.google_drive.types.FilesStringFilter`
    :   The type of the None singleton.

<a id="FilesListParams"></a>

`FilesListParams(*args, **kwargs)`
:   Parameters for files.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `corpora: str`
    :   The type of the None singleton.

    `drive_id: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `include_items_from_all_drives: bool`
    :   The type of the None singleton.

    `order_by: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `q: str`
    :   The type of the None singleton.

    `spaces: str`
    :   The type of the None singleton.

    `supports_all_drives: bool`
    :   The type of the None singleton.

<a id="FilesLtCondition"></a>

`FilesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.google_drive.types.FilesSearchFilter`
    :   The type of the None singleton.

<a id="FilesLteCondition"></a>

`FilesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.google_drive.types.FilesSearchFilter`
    :   The type of the None singleton.

<a id="FilesNeqCondition"></a>

`FilesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.google_drive.types.FilesSearchFilter`
    :   The type of the None singleton.

<a id="FilesNotCondition"></a>

`FilesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.google_drive.types.FilesEqCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesNeqCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesGtCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesGteCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesLtCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesLteCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesInCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesLikeCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesFuzzyCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesKeywordCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesContainsCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesNotCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesAndCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesOrCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesAnyCondition`
    :   The type of the None singleton.

<a id="FilesOrCondition"></a>

`FilesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.google_drive.types.FilesEqCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesNeqCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesGtCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesGteCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesLtCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesLteCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesInCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesLikeCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesFuzzyCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesKeywordCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesContainsCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesNotCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesAndCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesOrCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesAnyCondition]`
    :   The type of the None singleton.

<a id="FilesSearchFilter"></a>

`FilesSearchFilter(*args, **kwargs)`
:   Available fields for filtering files search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str | None`
    :   Extracted text content of the file.

    `file_name: str | None`
    :   Name of the file.

    `file_path: str | None`
    :   Full path of the file within the synced Drive folder.

    `id: str | None`
    :   Unique identifier of the file in Google Drive.

    `mime_type: str | None`
    :   MIME type of the file.

    `updated_at: str | None`
    :   Timestamp of the last modification to the file.

<a id="FilesSearchQuery"></a>

`FilesSearchQuery(*args, **kwargs)`
:   Search query for files entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.google_drive.types.FilesEqCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesNeqCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesGtCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesGteCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesLtCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesLteCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesInCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesLikeCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesFuzzyCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesKeywordCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesContainsCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesNotCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesAndCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesOrCondition | airbyte_agent_sdk.connectors.google_drive.types.FilesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.google_drive.types.FilesSortFilter]`
    :   The type of the None singleton.

<a id="FilesSortFilter"></a>

`FilesSortFilter(*args, **kwargs)`
:   Available fields for sorting files search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: Literal['asc', 'desc']`
    :   Extracted text content of the file.

    `file_name: Literal['asc', 'desc']`
    :   Name of the file.

    `file_path: Literal['asc', 'desc']`
    :   Full path of the file within the synced Drive folder.

    `id: Literal['asc', 'desc']`
    :   Unique identifier of the file in Google Drive.

    `mime_type: Literal['asc', 'desc']`
    :   MIME type of the file.

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp of the last modification to the file.

<a id="FilesStringFilter"></a>

`FilesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: str`
    :   Extracted text content of the file.

    `file_name: str`
    :   Name of the file.

    `file_path: str`
    :   Full path of the file within the synced Drive folder.

    `id: str`
    :   Unique identifier of the file in Google Drive.

    `mime_type: str`
    :   MIME type of the file.

    `updated_at: str`
    :   Timestamp of the last modification to the file.

<a id="FilesUpdateParams"></a>

`FilesUpdateParams(*args, **kwargs)`
:   Parameters for files.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `add_parents: str`
    :   The type of the None singleton.

    `description: str`
    :   The type of the None singleton.

    `file_id: str`
    :   The type of the None singleton.

    `mime_type: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `remove_parents: str`
    :   The type of the None singleton.

    `supports_all_drives: bool`
    :   The type of the None singleton.

<a id="FilesUploadCreateParams"></a>

`FilesUploadCreateParams(*args, **kwargs)`
:   Parameters for files_upload.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str`
    :   The type of the None singleton.

    `file_content: str`
    :   The type of the None singleton.

    `file_mime_type: str`
    :   The type of the None singleton.

    `mime_type: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `parents: list[str]`
    :   The type of the None singleton.

    `supports_all_drives: bool`
    :   The type of the None singleton.

    `upload_type: str`
    :   The type of the None singleton.

<a id="PermissionsGetParams"></a>

`PermissionsGetParams(*args, **kwargs)`
:   Parameters for permissions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `file_id: str`
    :   The type of the None singleton.

    `permission_id: str`
    :   The type of the None singleton.

    `supports_all_drives: bool`
    :   The type of the None singleton.

    `use_domain_admin_access: bool`
    :   The type of the None singleton.

<a id="PermissionsListParams"></a>

`PermissionsListParams(*args, **kwargs)`
:   Parameters for permissions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `file_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

    `supports_all_drives: bool`
    :   The type of the None singleton.

    `use_domain_admin_access: bool`
    :   The type of the None singleton.

<a id="RepliesGetParams"></a>

`RepliesGetParams(*args, **kwargs)`
:   Parameters for replies.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `comment_id: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `file_id: str`
    :   The type of the None singleton.

    `include_deleted: bool`
    :   The type of the None singleton.

    `reply_id: str`
    :   The type of the None singleton.

<a id="RepliesListParams"></a>

`RepliesListParams(*args, **kwargs)`
:   Parameters for replies.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `comment_id: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `file_id: str`
    :   The type of the None singleton.

    `include_deleted: bool`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

<a id="RevisionsGetParams"></a>

`RevisionsGetParams(*args, **kwargs)`
:   Parameters for revisions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `file_id: str`
    :   The type of the None singleton.

    `revision_id: str`
    :   The type of the None singleton.

<a id="RevisionsListParams"></a>

`RevisionsListParams(*args, **kwargs)`
:   Parameters for revisions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `file_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.