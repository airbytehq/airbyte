---
id: airbyte_agent_sdk-connectors-google_drive-types
title: airbyte_agent_sdk.connectors.google_drive.types
---

Module airbyte_agent_sdk.connectors.google_drive.types
======================================================
Type definitions for google-drive connector.

Classes
-------

`AboutGetParams(*args, **kwargs)`
:   Parameters for about.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

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

`ChangesStartPageTokenGetParams(*args, **kwargs)`
:   Parameters for changes_start_page_token.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `drive_id: str`
    :   The type of the None singleton.

    `supports_all_drives: bool`
    :   The type of the None singleton.

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

`DrivesGetParams(*args, **kwargs)`
:   Parameters for drives.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `drive_id: str`
    :   The type of the None singleton.

    `use_domain_admin_access: bool`
    :   The type of the None singleton.

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

`FilesDeleteParams(*args, **kwargs)`
:   Parameters for files.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `file_id: str`
    :   The type of the None singleton.

    `supports_all_drives: bool`
    :   The type of the None singleton.

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

`RevisionsGetParams(*args, **kwargs)`
:   Parameters for revisions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `file_id: str`
    :   The type of the None singleton.

    `revision_id: str`
    :   The type of the None singleton.

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