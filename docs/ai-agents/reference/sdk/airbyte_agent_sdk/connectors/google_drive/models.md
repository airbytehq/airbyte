---
id: airbyte_agent_sdk-connectors-google_drive-models
title: airbyte_agent_sdk.connectors.google_drive.models
---

Module airbyte_agent_sdk.connectors.google_drive.models
=======================================================
Pydantic models for google-drive connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="About"></a>

`About(**data: Any)`
:   Information about the user, the user's Drive, and system capabilities
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_installed: bool | None`
    :   The type of the None singleton.

    `can_create_drives: bool | None`
    :   The type of the None singleton.

    `can_create_team_drives: bool | None`
    :   The type of the None singleton.

    `drive_themes: list[airbyte_agent_sdk.connectors.google_drive.models.AboutDrivethemesItem] | None`
    :   The type of the None singleton.

    `export_formats: dict[str, list[str]] | None`
    :   The type of the None singleton.

    `folder_color_palette: list[str] | None`
    :   The type of the None singleton.

    `import_formats: dict[str, list[str]] | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `max_import_sizes: dict[str, str] | None`
    :   The type of the None singleton.

    `max_upload_size: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `storage_quota: airbyte_agent_sdk.connectors.google_drive.models.AboutStoragequota | None`
    :   The type of the None singleton.

    `team_drive_themes: list[airbyte_agent_sdk.connectors.google_drive.models.AboutTeamdrivethemesItem] | None`
    :   The type of the None singleton.

    `user: typing.Any | None`
    :   The type of the None singleton.

<a id="AboutDrivethemesItem"></a>

`AboutDrivethemesItem(**data: Any)`
:   Nested schema for About.driveThemes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `background_image_link: str | None`
    :   The type of the None singleton.

    `color_rgb: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AboutStoragequota"></a>

`AboutStoragequota(**data: Any)`
:   The user's storage quota limits and usage
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `limit: str | None`
    :   The usage limit, if applicable

    `model_config`
    :   The type of the None singleton.

    `usage: str | None`
    :   The total usage across all services

    `usage_in_drive: str | None`
    :   The usage by all files in Google Drive

    `usage_in_drive_trash: str | None`
    :   The usage by trashed files in Google Drive

<a id="AboutTeamdrivethemesItem"></a>

`AboutTeamdrivethemesItem(**data: Any)`
:   Nested schema for About.teamDriveThemes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `background_image_link: str | None`
    :   The type of the None singleton.

    `color_rgb: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Change"></a>

`Change(**data: Any)`
:   A change to a file or shared drive
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `change_type: str | None`
    :   The type of the None singleton.

    `drive: typing.Any | None`
    :   The type of the None singleton.

    `drive_id: str | None`
    :   The type of the None singleton.

    `file: typing.Any | None`
    :   The type of the None singleton.

    `file_id: str | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `removed: bool | None`
    :   The type of the None singleton.

    `time: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="ChangesListResponse"></a>

`ChangesListResponse(**data: Any)`
:   A list of changes for a user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `changes: list[airbyte_agent_sdk.connectors.google_drive.models.Change] | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `new_start_page_token: str | None`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="ChangesListResultMeta"></a>

`ChangesListResultMeta(**data: Any)`
:   Metadata for changes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `new_start_page_token: str | None`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="Comment"></a>

`Comment(**data: Any)`
:   A comment on a file
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `anchor: str | None`
    :   The type of the None singleton.

    `assignee_email_address: str | None`
    :   The type of the None singleton.

    `author: typing.Any | None`
    :   The type of the None singleton.

    `content: str | None`
    :   The type of the None singleton.

    `created_time: str | None`
    :   The type of the None singleton.

    `deleted: bool | None`
    :   The type of the None singleton.

    `html_content: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `mentioned_email_addresses: list[str] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   The type of the None singleton.

    `quoted_file_content: airbyte_agent_sdk.connectors.google_drive.models.CommentQuotedfilecontent | None`
    :   The type of the None singleton.

    `replies: list[airbyte_agent_sdk.connectors.google_drive.models.Reply] | None`
    :   The type of the None singleton.

    `resolved: bool | None`
    :   The type of the None singleton.

<a id="CommentQuotedfilecontent"></a>

`CommentQuotedfilecontent(**data: Any)`
:   The file content to which the comment refers
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `mime_type: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="CommentsListResponse"></a>

`CommentsListResponse(**data: Any)`
:   A list of comments on a file
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `comments: list[airbyte_agent_sdk.connectors.google_drive.models.Comment] | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
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

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="Drive"></a>

`Drive(**data: Any)`
:   Representation of a shared drive
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `background_image_file: airbyte_agent_sdk.connectors.google_drive.models.DriveBackgroundimagefile | None`
    :   The type of the None singleton.

    `background_image_link: str | None`
    :   The type of the None singleton.

    `capabilities: airbyte_agent_sdk.connectors.google_drive.models.DriveCapabilities | None`
    :   The type of the None singleton.

    `color_rgb: str | None`
    :   The type of the None singleton.

    `created_time: str | None`
    :   The type of the None singleton.

    `hidden: bool | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `org_unit_id: str | None`
    :   The type of the None singleton.

    `restrictions: airbyte_agent_sdk.connectors.google_drive.models.DriveRestrictions | None`
    :   The type of the None singleton.

    `theme_id: str | None`
    :   The type of the None singleton.

<a id="DriveBackgroundimagefile"></a>

`DriveBackgroundimagefile(**data: Any)`
:   An image file and cropping parameters for the background image
    
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

    `width: float | None`
    :   The type of the None singleton.

    `x_coordinate: float | None`
    :   The type of the None singleton.

    `y_coordinate: float | None`
    :   The type of the None singleton.

<a id="DriveCapabilities"></a>

`DriveCapabilities(**data: Any)`
:   Capabilities the current user has on this shared drive
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `can_add_children: bool | None`
    :   The type of the None singleton.

    `can_change_copy_requires_writer_permission_restriction: bool | None`
    :   The type of the None singleton.

    `can_change_domain_users_only_restriction: bool | None`
    :   The type of the None singleton.

    `can_change_drive_background: bool | None`
    :   The type of the None singleton.

    `can_change_drive_members_only_restriction: bool | None`
    :   The type of the None singleton.

    `can_change_sharing_folders_requires_organizer_permission_restriction: bool | None`
    :   The type of the None singleton.

    `can_comment: bool | None`
    :   The type of the None singleton.

    `can_copy: bool | None`
    :   The type of the None singleton.

    `can_delete_children: bool | None`
    :   The type of the None singleton.

    `can_delete_drive: bool | None`
    :   The type of the None singleton.

    `can_download: bool | None`
    :   The type of the None singleton.

    `can_edit: bool | None`
    :   The type of the None singleton.

    `can_list_children: bool | None`
    :   The type of the None singleton.

    `can_manage_members: bool | None`
    :   The type of the None singleton.

    `can_read_revisions: bool | None`
    :   The type of the None singleton.

    `can_rename: bool | None`
    :   The type of the None singleton.

    `can_rename_drive: bool | None`
    :   The type of the None singleton.

    `can_reset_drive_restrictions: bool | None`
    :   The type of the None singleton.

    `can_share: bool | None`
    :   The type of the None singleton.

    `can_trash_children: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DriveRestrictions"></a>

`DriveRestrictions(**data: Any)`
:   A set of restrictions that apply to this shared drive
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_managed_restrictions: bool | None`
    :   The type of the None singleton.

    `copy_requires_writer_permission: bool | None`
    :   The type of the None singleton.

    `domain_users_only: bool | None`
    :   The type of the None singleton.

    `drive_members_only: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `sharing_folders_requires_organizer_permission: bool | None`
    :   The type of the None singleton.

<a id="DrivesListResponse"></a>

`DrivesListResponse(**data: Any)`
:   A list of shared drives
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `drives: list[airbyte_agent_sdk.connectors.google_drive.models.Drive] | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="DrivesListResultMeta"></a>

`DrivesListResultMeta(**data: Any)`
:   Metadata for drives.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="File"></a>

`File(**data: Any)`
:   The metadata for a file
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_properties: dict[str, str] | None`
    :   The type of the None singleton.

    `capabilities: airbyte_agent_sdk.connectors.google_drive.models.FileCapabilities | None`
    :   The type of the None singleton.

    `content_restrictions: list[airbyte_agent_sdk.connectors.google_drive.models.FileContentrestrictionsItem] | None`
    :   The type of the None singleton.

    `copy_requires_writer_permission: bool | None`
    :   The type of the None singleton.

    `created_time: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `drive_id: str | None`
    :   The type of the None singleton.

    `explicitly_trashed: bool | None`
    :   The type of the None singleton.

    `export_links: dict[str, str] | None`
    :   The type of the None singleton.

    `file_extension: str | None`
    :   The type of the None singleton.

    `folder_color_rgb: str | None`
    :   The type of the None singleton.

    `full_file_extension: str | None`
    :   The type of the None singleton.

    `has_thumbnail: bool | None`
    :   The type of the None singleton.

    `head_revision_id: str | None`
    :   The type of the None singleton.

    `icon_link: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `image_media_metadata: airbyte_agent_sdk.connectors.google_drive.models.FileImagemediametadata | None`
    :   The type of the None singleton.

    `is_app_authorized: bool | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `label_info: airbyte_agent_sdk.connectors.google_drive.models.FileLabelinfo | None`
    :   The type of the None singleton.

    `last_modifying_user: typing.Any | None`
    :   The type of the None singleton.

    `link_share_metadata: airbyte_agent_sdk.connectors.google_drive.models.FileLinksharemetadata | None`
    :   The type of the None singleton.

    `md5_checksum: str | None`
    :   The type of the None singleton.

    `mime_type: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_by_me: bool | None`
    :   The type of the None singleton.

    `modified_by_me_time: str | None`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `original_filename: str | None`
    :   The type of the None singleton.

    `owned_by_me: bool | None`
    :   The type of the None singleton.

    `owners: list[airbyte_agent_sdk.connectors.google_drive.models.User] | None`
    :   The type of the None singleton.

    `parents: list[str] | None`
    :   The type of the None singleton.

    `permission_ids: list[str] | None`
    :   The type of the None singleton.

    `properties: dict[str, str] | None`
    :   The type of the None singleton.

    `quota_bytes_used: str | None`
    :   The type of the None singleton.

    `resource_key: str | None`
    :   The type of the None singleton.

    `sha1_checksum: str | None`
    :   The type of the None singleton.

    `sha256_checksum: str | None`
    :   The type of the None singleton.

    `shared: bool | None`
    :   The type of the None singleton.

    `shared_with_me_time: str | None`
    :   The type of the None singleton.

    `sharing_user: typing.Any | None`
    :   The type of the None singleton.

    `shortcut_details: airbyte_agent_sdk.connectors.google_drive.models.FileShortcutdetails | None`
    :   The type of the None singleton.

    `size: str | None`
    :   The type of the None singleton.

    `spaces: list[str] | None`
    :   The type of the None singleton.

    `starred: bool | None`
    :   The type of the None singleton.

    `thumbnail_link: str | None`
    :   The type of the None singleton.

    `thumbnail_version: str | None`
    :   The type of the None singleton.

    `trashed: bool | None`
    :   The type of the None singleton.

    `trashed_time: str | None`
    :   The type of the None singleton.

    `trashing_user: typing.Any | None`
    :   The type of the None singleton.

    `version: str | None`
    :   The type of the None singleton.

    `video_media_metadata: airbyte_agent_sdk.connectors.google_drive.models.FileVideomediametadata | None`
    :   The type of the None singleton.

    `viewed_by_me: bool | None`
    :   The type of the None singleton.

    `viewed_by_me_time: str | None`
    :   The type of the None singleton.

    `viewers_can_copy_content: bool | None`
    :   The type of the None singleton.

    `web_content_link: str | None`
    :   The type of the None singleton.

    `web_view_link: str | None`
    :   The type of the None singleton.

    `writers_can_share: bool | None`
    :   The type of the None singleton.

<a id="FileCapabilities"></a>

`FileCapabilities(**data: Any)`
:   Capabilities the current user has on this file
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `can_add_children: bool | None`
    :   The type of the None singleton.

    `can_comment: bool | None`
    :   The type of the None singleton.

    `can_copy: bool | None`
    :   The type of the None singleton.

    `can_delete: bool | None`
    :   The type of the None singleton.

    `can_download: bool | None`
    :   The type of the None singleton.

    `can_edit: bool | None`
    :   The type of the None singleton.

    `can_list_children: bool | None`
    :   The type of the None singleton.

    `can_read_revisions: bool | None`
    :   The type of the None singleton.

    `can_remove_children: bool | None`
    :   The type of the None singleton.

    `can_rename: bool | None`
    :   The type of the None singleton.

    `can_share: bool | None`
    :   The type of the None singleton.

    `can_trash: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FileContentrestrictionsItem"></a>

`FileContentrestrictionsItem(**data: Any)`
:   Nested schema for File.contentRestrictions_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `read_only: bool | None`
    :   The type of the None singleton.

    `reason: str | None`
    :   The type of the None singleton.

    `restricting_user: typing.Any | None`
    :   The type of the None singleton.

    `restriction_time: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="FileCreateParams"></a>

`FileCreateParams(**data: Any)`
:   Parameters for creating a new file or folder
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | None`
    :   The type of the None singleton.

    `mime_type: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `parents: list[str] | None`
    :   The type of the None singleton.

<a id="FileImagemediametadata"></a>

`FileImagemediametadata(**data: Any)`
:   Additional metadata about image media
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `aperture: float | None`
    :   The type of the None singleton.

    `camera_make: str | None`
    :   The type of the None singleton.

    `camera_model: str | None`
    :   The type of the None singleton.

    `color_space: str | None`
    :   The type of the None singleton.

    `exposure_bias: float | None`
    :   The type of the None singleton.

    `exposure_mode: str | None`
    :   The type of the None singleton.

    `exposure_time: float | None`
    :   The type of the None singleton.

    `flash_used: bool | None`
    :   The type of the None singleton.

    `focal_length: float | None`
    :   The type of the None singleton.

    `height: int | None`
    :   The type of the None singleton.

    `iso_speed: int | None`
    :   The type of the None singleton.

    `lens: str | None`
    :   The type of the None singleton.

    `location: airbyte_agent_sdk.connectors.google_drive.models.FileImagemediametadataLocation | None`
    :   The type of the None singleton.

    `max_aperture_value: float | None`
    :   The type of the None singleton.

    `metering_mode: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rotation: int | None`
    :   The type of the None singleton.

    `sensor: str | None`
    :   The type of the None singleton.

    `subject_distance: int | None`
    :   The type of the None singleton.

    `time: str | None`
    :   The type of the None singleton.

    `white_balance: str | None`
    :   The type of the None singleton.

    `width: int | None`
    :   The type of the None singleton.

<a id="FileImagemediametadataLocation"></a>

`FileImagemediametadataLocation(**data: Any)`
:   Nested schema for FileImagemediametadata.location
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `altitude: float | None`
    :   The type of the None singleton.

    `latitude: float | None`
    :   The type of the None singleton.

    `longitude: float | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FileLabelinfo"></a>

`FileLabelinfo(**data: Any)`
:   An overview of the labels on the file
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `labels: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FileLinksharemetadata"></a>

`FileLinksharemetadata(**data: Any)`
:   Contains details about the link URLs
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `security_update_eligible: bool | None`
    :   The type of the None singleton.

    `security_update_enabled: bool | None`
    :   The type of the None singleton.

<a id="FileShortcutdetails"></a>

`FileShortcutdetails(**data: Any)`
:   Shortcut file details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `target_id: str | None`
    :   The type of the None singleton.

    `target_mime_type: str | None`
    :   The type of the None singleton.

    `target_resource_key: str | None`
    :   The type of the None singleton.

<a id="FileUpdateParams"></a>

`FileUpdateParams(**data: Any)`
:   Parameters for updating file metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | None`
    :   The type of the None singleton.

    `mime_type: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

<a id="FileUploadParams"></a>

`FileUploadParams(**data: Any)`
:   Parameters for uploading a file with content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | None`
    :   The type of the None singleton.

    `file_content: str`
    :   The type of the None singleton.

    `file_mime_type: str | None`
    :   The type of the None singleton.

    `mime_type: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `parents: list[str] | None`
    :   The type of the None singleton.

<a id="FileVideomediametadata"></a>

`FileVideomediametadata(**data: Any)`
:   Additional metadata about video media
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `duration_millis: str | None`
    :   The type of the None singleton.

    `height: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `width: int | None`
    :   The type of the None singleton.

<a id="FilesListResponse"></a>

`FilesListResponse(**data: Any)`
:   A list of files
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `files: list[airbyte_agent_sdk.connectors.google_drive.models.File] | None`
    :   The type of the None singleton.

    `incomplete_search: bool | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="FilesListResultMeta"></a>

`FilesListResultMeta(**data: Any)`
:   Metadata for files.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `incomplete_search: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="GoogleDriveAuthConfig"></a>

`GoogleDriveAuthConfig(**data: Any)`
:   OAuth 2.0 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str | None`
    :   Your Google OAuth2 Access Token (optional, will be obtained via refresh)

    `client_id: str | None`
    :   Your Google OAuth2 Client ID

    `client_secret: str | None`
    :   Your Google OAuth2 Client Secret

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   Your Google OAuth2 Refresh Token

<a id="GoogleDriveCheckResult"></a>

`GoogleDriveCheckResult(**data: Any)`
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

<a id="GoogleDriveExecuteResult"></a>

`GoogleDriveExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="GoogleDriveExecuteResultWithMeta"></a>

`GoogleDriveExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[Change], ChangesListResultMeta]
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[Comment], CommentsListResultMeta]
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[Drive], DrivesListResultMeta]
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[File], FilesListResultMeta]
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[Permission], PermissionsListResultMeta]
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[Reply], RepliesListResultMeta]
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[Revision], RevisionsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`GoogleDriveExecuteResultWithMeta[list[Change], ChangesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ChangesListResult"></a>

`ChangesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleDriveExecuteResultWithMeta[list[Comment], CommentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
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

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleDriveExecuteResultWithMeta[list[Drive], DrivesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DrivesListResult"></a>

`DrivesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleDriveExecuteResultWithMeta[list[File], FilesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="FilesListResult"></a>

`FilesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleDriveExecuteResultWithMeta[list[Permission], PermissionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PermissionsListResult"></a>

`PermissionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleDriveExecuteResultWithMeta[list[Reply], RepliesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="RepliesListResult"></a>

`RepliesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GoogleDriveExecuteResultWithMeta[list[Revision], RevisionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="RevisionsListResult"></a>

`RevisionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GoogleDriveReplicationConfig"></a>

`GoogleDriveReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Google Drive.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `folder_url: str`
    :   URL for the Google Drive folder you want to sync (e.g., https://drive.google.com/drive/folders/YOUR-FOLDER-ID)

    `model_config`
    :   The type of the None singleton.

    `streams: str`
    :   Configuration for file streams to sync from Google Drive

<a id="Permission"></a>

`Permission(**data: Any)`
:   A permission for a file
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allow_file_discovery: bool | None`
    :   The type of the None singleton.

    `deleted: bool | None`
    :   The type of the None singleton.

    `display_name: str | None`
    :   The type of the None singleton.

    `domain: str | None`
    :   The type of the None singleton.

    `email_address: str | None`
    :   The type of the None singleton.

    `expiration_time: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pending_owner: bool | None`
    :   The type of the None singleton.

    `permission_details: list[airbyte_agent_sdk.connectors.google_drive.models.PermissionPermissiondetailsItem] | None`
    :   The type of the None singleton.

    `photo_link: str | None`
    :   The type of the None singleton.

    `role: str | None`
    :   The type of the None singleton.

    `team_drive_permission_details: list[airbyte_agent_sdk.connectors.google_drive.models.PermissionTeamdrivepermissiondetailsItem] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `view: str | None`
    :   The type of the None singleton.

<a id="PermissionPermissiondetailsItem"></a>

`PermissionPermissiondetailsItem(**data: Any)`
:   Nested schema for Permission.permissionDetails_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `inherited: bool | None`
    :   The type of the None singleton.

    `inherited_from: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `permission_type: str | None`
    :   The type of the None singleton.

    `role: str | None`
    :   The type of the None singleton.

<a id="PermissionTeamdrivepermissiondetailsItem"></a>

`PermissionTeamdrivepermissiondetailsItem(**data: Any)`
:   Nested schema for Permission.teamDrivePermissionDetails_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `inherited: bool | None`
    :   The type of the None singleton.

    `inherited_from: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `role: str | None`
    :   The type of the None singleton.

    `team_drive_permission_type: str | None`
    :   The type of the None singleton.

<a id="PermissionsListResponse"></a>

`PermissionsListResponse(**data: Any)`
:   A list of permissions for a file
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

    `permissions: list[airbyte_agent_sdk.connectors.google_drive.models.Permission] | None`
    :   The type of the None singleton.

<a id="PermissionsListResultMeta"></a>

`PermissionsListResultMeta(**data: Any)`
:   Metadata for permissions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="RepliesListResponse"></a>

`RepliesListResponse(**data: Any)`
:   A list of replies to a comment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

    `replies: list[airbyte_agent_sdk.connectors.google_drive.models.Reply] | None`
    :   The type of the None singleton.

<a id="RepliesListResultMeta"></a>

`RepliesListResultMeta(**data: Any)`
:   Metadata for replies.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="Reply"></a>

`Reply(**data: Any)`
:   A reply to a comment on a file
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action: str | None`
    :   The type of the None singleton.

    `author: typing.Any | None`
    :   The type of the None singleton.

    `content: str | None`
    :   The type of the None singleton.

    `created_time: str | None`
    :   The type of the None singleton.

    `deleted: bool | None`
    :   The type of the None singleton.

    `html_content: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   The type of the None singleton.

<a id="Revision"></a>

`Revision(**data: Any)`
:   The metadata for a revision to a file
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `export_links: dict[str, str] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `keep_forever: bool | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `last_modifying_user: typing.Any | None`
    :   The type of the None singleton.

    `md5_checksum: str | None`
    :   The type of the None singleton.

    `mime_type: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   The type of the None singleton.

    `original_filename: str | None`
    :   The type of the None singleton.

    `publish_auto: bool | None`
    :   The type of the None singleton.

    `published: bool | None`
    :   The type of the None singleton.

    `published_link: str | None`
    :   The type of the None singleton.

    `published_outside_domain: bool | None`
    :   The type of the None singleton.

    `size: str | None`
    :   The type of the None singleton.

<a id="RevisionsListResponse"></a>

`RevisionsListResponse(**data: Any)`
:   A list of revisions of a file
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

    `revisions: list[airbyte_agent_sdk.connectors.google_drive.models.Revision] | None`
    :   The type of the None singleton.

<a id="RevisionsListResultMeta"></a>

`RevisionsListResultMeta(**data: Any)`
:   Metadata for revisions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | None`
    :   The type of the None singleton.

<a id="StartPageToken"></a>

`StartPageToken(**data: Any)`
:   The starting page token for listing changes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `kind: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start_page_token: str | None`
    :   The type of the None singleton.

<a id="User"></a>

`User(**data: Any)`
:   Information about a Drive user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `display_name: str | None`
    :   The type of the None singleton.

    `email_address: str | None`
    :   The type of the None singleton.

    `kind: str | None`
    :   The type of the None singleton.

    `me: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `permission_id: str | None`
    :   The type of the None singleton.

    `photo_link: str | None`
    :   The type of the None singleton.