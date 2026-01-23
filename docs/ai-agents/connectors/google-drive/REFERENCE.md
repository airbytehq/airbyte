# Google-Drive full reference

This is the full reference documentation for the Google-Drive agent connector.

## Supported entities and actions

The Google-Drive connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Files | [List](#files-list), [Get](#files-get), [Download](#files-download) |
| Files Export | [Download](#files-export-download) |
| Drives | [List](#drives-list), [Get](#drives-get) |
| Permissions | [List](#permissions-list), [Get](#permissions-get) |
| Comments | [List](#comments-list), [Get](#comments-get) |
| Replies | [List](#replies-list), [Get](#replies-get) |
| Revisions | [List](#revisions-list), [Get](#revisions-get) |
| Changes | [List](#changes-list) |
| Changes Start Page Token | [Get](#changes-start-page-token-get) |
| About | [Get](#about-get) |

## Files

### Files List

Lists the user's files. Returns a paginated list of files.

#### Python SDK

```python
await google_drive.files.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "files",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `pageSize` | `integer` | No | Maximum number of files to return per page (1-1000) |
| `pageToken` | `string` | No | Token for continuing a previous list request |
| `q` | `string` | No | Query string for searching files |
| `orderBy` | `string` | No | Sort order (e.g., 'modifiedTime desc', 'name') |
| `fields` | `string` | No | Fields to include in the response |
| `spaces` | `string` | No | Comma-separated list of spaces to query (drive, appDataFolder) |
| `corpora` | `string` | No | Bodies of items to search (user, drive, allDrives) |
| `driveId` | `string` | No | ID of the shared drive to search |
| `includeItemsFromAllDrives` | `boolean` | No | Whether to include items from all drives |
| `supportsAllDrives` | `boolean` | No | Whether the requesting application supports both My Drives and shared drives |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `mimeType` | `string \| null` |  |
| `description` | `string \| null` |  |
| `starred` | `boolean \| null` |  |
| `trashed` | `boolean \| null` |  |
| `explicitlyTrashed` | `boolean \| null` |  |
| `parents` | `array \| null` |  |
| `properties` | `object \| null` |  |
| `appProperties` | `object \| null` |  |
| `spaces` | `array \| null` |  |
| `version` | `string \| null` |  |
| `webContentLink` | `string \| null` |  |
| `webViewLink` | `string \| null` |  |
| `iconLink` | `string \| null` |  |
| `hasThumbnail` | `boolean \| null` |  |
| `thumbnailLink` | `string \| null` |  |
| `thumbnailVersion` | `string \| null` |  |
| `viewedByMe` | `boolean \| null` |  |
| `viewedByMeTime` | `string \| null` |  |
| `createdTime` | `string \| null` |  |
| `modifiedTime` | `string \| null` |  |
| `modifiedByMeTime` | `string \| null` |  |
| `modifiedByMe` | `boolean \| null` |  |
| `sharedWithMeTime` | `string \| null` |  |
| `sharingUser` | `object \| any` |  |
| `owners` | `array \| null` |  |
| `owners[].kind` | `string \| null` |  |
| `owners[].displayName` | `string \| null` |  |
| `owners[].photoLink` | `string \| null` |  |
| `owners[].me` | `boolean \| null` |  |
| `owners[].permissionId` | `string \| null` |  |
| `owners[].emailAddress` | `string \| null` |  |
| `driveId` | `string \| null` |  |
| `lastModifyingUser` | `object \| any` |  |
| `shared` | `boolean \| null` |  |
| `ownedByMe` | `boolean \| null` |  |
| `capabilities` | `object \| null` |  |
| `viewersCanCopyContent` | `boolean \| null` |  |
| `copyRequiresWriterPermission` | `boolean \| null` |  |
| `writersCanShare` | `boolean \| null` |  |
| `permissionIds` | `array \| null` |  |
| `folderColorRgb` | `string \| null` |  |
| `originalFilename` | `string \| null` |  |
| `fullFileExtension` | `string \| null` |  |
| `fileExtension` | `string \| null` |  |
| `md5Checksum` | `string \| null` |  |
| `sha1Checksum` | `string \| null` |  |
| `sha256Checksum` | `string \| null` |  |
| `size` | `string \| null` |  |
| `quotaBytesUsed` | `string \| null` |  |
| `headRevisionId` | `string \| null` |  |
| `isAppAuthorized` | `boolean \| null` |  |
| `exportLinks` | `object \| null` |  |
| `shortcutDetails` | `object \| null` |  |
| `contentRestrictions` | `array \| null` |  |
| `resourceKey` | `string \| null` |  |
| `linkShareMetadata` | `object \| null` |  |
| `labelInfo` | `object \| null` |  |
| `trashedTime` | `string \| null` |  |
| `trashingUser` | `object \| any` |  |
| `imageMediaMetadata` | `object \| null` |  |
| `videoMediaMetadata` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string \| null` |  |
| `incompleteSearch` | `boolean \| null` |  |

</details>

### Files Get

Gets a file's metadata by ID

#### Python SDK

```python
await google_drive.files.get(
    file_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "files",
    "action": "get",
    "params": {
        "fileId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fileId` | `string` | Yes | The ID of the file |
| `fields` | `string` | No | Fields to include in the response |
| `supportsAllDrives` | `boolean` | No | Whether the requesting application supports both My Drives and shared drives |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `mimeType` | `string \| null` |  |
| `description` | `string \| null` |  |
| `starred` | `boolean \| null` |  |
| `trashed` | `boolean \| null` |  |
| `explicitlyTrashed` | `boolean \| null` |  |
| `parents` | `array \| null` |  |
| `properties` | `object \| null` |  |
| `appProperties` | `object \| null` |  |
| `spaces` | `array \| null` |  |
| `version` | `string \| null` |  |
| `webContentLink` | `string \| null` |  |
| `webViewLink` | `string \| null` |  |
| `iconLink` | `string \| null` |  |
| `hasThumbnail` | `boolean \| null` |  |
| `thumbnailLink` | `string \| null` |  |
| `thumbnailVersion` | `string \| null` |  |
| `viewedByMe` | `boolean \| null` |  |
| `viewedByMeTime` | `string \| null` |  |
| `createdTime` | `string \| null` |  |
| `modifiedTime` | `string \| null` |  |
| `modifiedByMeTime` | `string \| null` |  |
| `modifiedByMe` | `boolean \| null` |  |
| `sharedWithMeTime` | `string \| null` |  |
| `sharingUser` | `object \| any` |  |
| `owners` | `array \| null` |  |
| `owners[].kind` | `string \| null` |  |
| `owners[].displayName` | `string \| null` |  |
| `owners[].photoLink` | `string \| null` |  |
| `owners[].me` | `boolean \| null` |  |
| `owners[].permissionId` | `string \| null` |  |
| `owners[].emailAddress` | `string \| null` |  |
| `driveId` | `string \| null` |  |
| `lastModifyingUser` | `object \| any` |  |
| `shared` | `boolean \| null` |  |
| `ownedByMe` | `boolean \| null` |  |
| `capabilities` | `object \| null` |  |
| `viewersCanCopyContent` | `boolean \| null` |  |
| `copyRequiresWriterPermission` | `boolean \| null` |  |
| `writersCanShare` | `boolean \| null` |  |
| `permissionIds` | `array \| null` |  |
| `folderColorRgb` | `string \| null` |  |
| `originalFilename` | `string \| null` |  |
| `fullFileExtension` | `string \| null` |  |
| `fileExtension` | `string \| null` |  |
| `md5Checksum` | `string \| null` |  |
| `sha1Checksum` | `string \| null` |  |
| `sha256Checksum` | `string \| null` |  |
| `size` | `string \| null` |  |
| `quotaBytesUsed` | `string \| null` |  |
| `headRevisionId` | `string \| null` |  |
| `isAppAuthorized` | `boolean \| null` |  |
| `exportLinks` | `object \| null` |  |
| `shortcutDetails` | `object \| null` |  |
| `contentRestrictions` | `array \| null` |  |
| `resourceKey` | `string \| null` |  |
| `linkShareMetadata` | `object \| null` |  |
| `labelInfo` | `object \| null` |  |
| `trashedTime` | `string \| null` |  |
| `trashingUser` | `object \| any` |  |
| `imageMediaMetadata` | `object \| null` |  |
| `videoMediaMetadata` | `object \| null` |  |


</details>

### Files Download

Downloads the binary content of a file. This works for non-Google Workspace files
(PDFs, images, zip files, etc.). For Google Docs, Sheets, Slides, or Drawings,
use the export action instead.


#### Python SDK

```python
async for chunk in google_drive.files.download(    file_id="<str>",    alt="<str>"):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "files",
    "action": "download",
    "params": {
        "fileId": "<str>",
        "alt": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fileId` | `string` | Yes | The ID of the file to download |
| `alt` | `"media"` | Yes | Must be set to 'media' to download file content |
| `acknowledgeAbuse` | `boolean` | No | Whether the user is acknowledging the risk of downloading known malware or other abusive files |
| `supportsAllDrives` | `boolean` | No | Whether the requesting application supports both My Drives and shared drives |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


## Files Export

### Files Export Download

Exports a Google Workspace file (Docs, Sheets, Slides, Drawings) to a specified format.
Common export formats:
- application/pdf (all types)
- text/plain (Docs)
- text/csv (Sheets)
- application/vnd.openxmlformats-officedocument.wordprocessingml.document (Docs to .docx)
- application/vnd.openxmlformats-officedocument.spreadsheetml.sheet (Sheets to .xlsx)
- application/vnd.openxmlformats-officedocument.presentationml.presentation (Slides to .pptx)
Note: Export has a 10MB limit. For larger files, use the Drive UI.


#### Python SDK

```python
async for chunk in google_drive.files_export.download(    file_id="<str>",    mime_type="<str>"):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "files_export",
    "action": "download",
    "params": {
        "fileId": "<str>",
        "mimeType": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fileId` | `string` | Yes | The ID of the Google Workspace file to export |
| `mimeType` | `string` | Yes | The MIME type of the format to export to. Common values:
- application/pdf
- text/plain
- text/csv
- application/vnd.openxmlformats-officedocument.wordprocessingml.document
- application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- application/vnd.openxmlformats-officedocument.presentationml.presentation
 |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


## Drives

### Drives List

Lists the user's shared drives

#### Python SDK

```python
await google_drive.drives.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "drives",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `pageSize` | `integer` | No | Maximum number of shared drives to return (1-100) |
| `pageToken` | `string` | No | Token for continuing a previous list request |
| `q` | `string` | No | Query string for searching shared drives |
| `useDomainAdminAccess` | `boolean` | No | Issue the request as a domain administrator |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `colorRgb` | `string \| null` |  |
| `backgroundImageLink` | `string \| null` |  |
| `backgroundImageFile` | `object \| null` |  |
| `capabilities` | `object \| null` |  |
| `themeId` | `string \| null` |  |
| `createdTime` | `string \| null` |  |
| `hidden` | `boolean \| null` |  |
| `restrictions` | `object \| null` |  |
| `orgUnitId` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string \| null` |  |

</details>

### Drives Get

Gets a shared drive's metadata by ID

#### Python SDK

```python
await google_drive.drives.get(
    drive_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "drives",
    "action": "get",
    "params": {
        "driveId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `driveId` | `string` | Yes | The ID of the shared drive |
| `useDomainAdminAccess` | `boolean` | No | Issue the request as a domain administrator |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `colorRgb` | `string \| null` |  |
| `backgroundImageLink` | `string \| null` |  |
| `backgroundImageFile` | `object \| null` |  |
| `capabilities` | `object \| null` |  |
| `themeId` | `string \| null` |  |
| `createdTime` | `string \| null` |  |
| `hidden` | `boolean \| null` |  |
| `restrictions` | `object \| null` |  |
| `orgUnitId` | `string \| null` |  |


</details>

## Permissions

### Permissions List

Lists a file's or shared drive's permissions

#### Python SDK

```python
await google_drive.permissions.list(
    file_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "permissions",
    "action": "list",
    "params": {
        "fileId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fileId` | `string` | Yes | The ID of the file or shared drive |
| `pageSize` | `integer` | No | Maximum number of permissions to return (1-100) |
| `pageToken` | `string` | No | Token for continuing a previous list request |
| `supportsAllDrives` | `boolean` | No | Whether the requesting application supports both My Drives and shared drives |
| `useDomainAdminAccess` | `boolean` | No | Issue the request as a domain administrator |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `emailAddress` | `string \| null` |  |
| `domain` | `string \| null` |  |
| `role` | `string \| null` |  |
| `view` | `string \| null` |  |
| `allowFileDiscovery` | `boolean \| null` |  |
| `displayName` | `string \| null` |  |
| `photoLink` | `string \| null` |  |
| `expirationTime` | `string \| null` |  |
| `teamDrivePermissionDetails` | `array \| null` |  |
| `permissionDetails` | `array \| null` |  |
| `deleted` | `boolean \| null` |  |
| `pendingOwner` | `boolean \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string \| null` |  |

</details>

### Permissions Get

Gets a permission by ID

#### Python SDK

```python
await google_drive.permissions.get(
    file_id="<str>",
    permission_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "permissions",
    "action": "get",
    "params": {
        "fileId": "<str>",
        "permissionId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fileId` | `string` | Yes | The ID of the file |
| `permissionId` | `string` | Yes | The ID of the permission |
| `supportsAllDrives` | `boolean` | No | Whether the requesting application supports both My Drives and shared drives |
| `useDomainAdminAccess` | `boolean` | No | Issue the request as a domain administrator |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `emailAddress` | `string \| null` |  |
| `domain` | `string \| null` |  |
| `role` | `string \| null` |  |
| `view` | `string \| null` |  |
| `allowFileDiscovery` | `boolean \| null` |  |
| `displayName` | `string \| null` |  |
| `photoLink` | `string \| null` |  |
| `expirationTime` | `string \| null` |  |
| `teamDrivePermissionDetails` | `array \| null` |  |
| `permissionDetails` | `array \| null` |  |
| `deleted` | `boolean \| null` |  |
| `pendingOwner` | `boolean \| null` |  |


</details>

## Comments

### Comments List

Lists a file's comments

#### Python SDK

```python
await google_drive.comments.list(
    file_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "list",
    "params": {
        "fileId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fileId` | `string` | Yes | The ID of the file |
| `pageSize` | `integer` | No | Maximum number of comments to return (1-100) |
| `pageToken` | `string` | No | Token for continuing a previous list request |
| `startModifiedTime` | `string` | No | Minimum value of modifiedTime to filter by (RFC 3339) |
| `includeDeleted` | `boolean` | No | Whether to include deleted comments |
| `fields` | `string` | No | Fields to include in the response (required for comments) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `id` | `string` |  |
| `createdTime` | `string \| null` |  |
| `modifiedTime` | `string \| null` |  |
| `author` | `object \| any` |  |
| `htmlContent` | `string \| null` |  |
| `content` | `string \| null` |  |
| `deleted` | `boolean \| null` |  |
| `resolved` | `boolean \| null` |  |
| `quotedFileContent` | `object \| null` |  |
| `anchor` | `string \| null` |  |
| `replies` | `array \| null` |  |
| `replies[].kind` | `string \| null` |  |
| `replies[].id` | `string` |  |
| `replies[].createdTime` | `string \| null` |  |
| `replies[].modifiedTime` | `string \| null` |  |
| `replies[].author` | `object \| any` |  |
| `replies[].htmlContent` | `string \| null` |  |
| `replies[].content` | `string \| null` |  |
| `replies[].deleted` | `boolean \| null` |  |
| `replies[].action` | `string \| null` |  |
| `mentionedEmailAddresses` | `array \| null` |  |
| `assigneeEmailAddress` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string \| null` |  |

</details>

### Comments Get

Gets a comment by ID

#### Python SDK

```python
await google_drive.comments.get(
    file_id="<str>",
    comment_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "get",
    "params": {
        "fileId": "<str>",
        "commentId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fileId` | `string` | Yes | The ID of the file |
| `commentId` | `string` | Yes | The ID of the comment |
| `includeDeleted` | `boolean` | No | Whether to return deleted comments |
| `fields` | `string` | No | Fields to include in the response (required for comments) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `id` | `string` |  |
| `createdTime` | `string \| null` |  |
| `modifiedTime` | `string \| null` |  |
| `author` | `object \| any` |  |
| `htmlContent` | `string \| null` |  |
| `content` | `string \| null` |  |
| `deleted` | `boolean \| null` |  |
| `resolved` | `boolean \| null` |  |
| `quotedFileContent` | `object \| null` |  |
| `anchor` | `string \| null` |  |
| `replies` | `array \| null` |  |
| `replies[].kind` | `string \| null` |  |
| `replies[].id` | `string` |  |
| `replies[].createdTime` | `string \| null` |  |
| `replies[].modifiedTime` | `string \| null` |  |
| `replies[].author` | `object \| any` |  |
| `replies[].htmlContent` | `string \| null` |  |
| `replies[].content` | `string \| null` |  |
| `replies[].deleted` | `boolean \| null` |  |
| `replies[].action` | `string \| null` |  |
| `mentionedEmailAddresses` | `array \| null` |  |
| `assigneeEmailAddress` | `string \| null` |  |


</details>

## Replies

### Replies List

Lists a comment's replies

#### Python SDK

```python
await google_drive.replies.list(
    file_id="<str>",
    comment_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "replies",
    "action": "list",
    "params": {
        "fileId": "<str>",
        "commentId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fileId` | `string` | Yes | The ID of the file |
| `commentId` | `string` | Yes | The ID of the comment |
| `pageSize` | `integer` | No | Maximum number of replies to return (1-100) |
| `pageToken` | `string` | No | Token for continuing a previous list request |
| `includeDeleted` | `boolean` | No | Whether to include deleted replies |
| `fields` | `string` | No | Fields to include in the response (required for replies) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `id` | `string` |  |
| `createdTime` | `string \| null` |  |
| `modifiedTime` | `string \| null` |  |
| `author` | `object \| any` |  |
| `htmlContent` | `string \| null` |  |
| `content` | `string \| null` |  |
| `deleted` | `boolean \| null` |  |
| `action` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string \| null` |  |

</details>

### Replies Get

Gets a reply by ID

#### Python SDK

```python
await google_drive.replies.get(
    file_id="<str>",
    comment_id="<str>",
    reply_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "replies",
    "action": "get",
    "params": {
        "fileId": "<str>",
        "commentId": "<str>",
        "replyId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fileId` | `string` | Yes | The ID of the file |
| `commentId` | `string` | Yes | The ID of the comment |
| `replyId` | `string` | Yes | The ID of the reply |
| `includeDeleted` | `boolean` | No | Whether to return deleted replies |
| `fields` | `string` | No | Fields to include in the response (required for replies) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `id` | `string` |  |
| `createdTime` | `string \| null` |  |
| `modifiedTime` | `string \| null` |  |
| `author` | `object \| any` |  |
| `htmlContent` | `string \| null` |  |
| `content` | `string \| null` |  |
| `deleted` | `boolean \| null` |  |
| `action` | `string \| null` |  |


</details>

## Revisions

### Revisions List

Lists a file's revisions

#### Python SDK

```python
await google_drive.revisions.list(
    file_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "revisions",
    "action": "list",
    "params": {
        "fileId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fileId` | `string` | Yes | The ID of the file |
| `pageSize` | `integer` | No | Maximum number of revisions to return (1-1000) |
| `pageToken` | `string` | No | Token for continuing a previous list request |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `id` | `string` |  |
| `mimeType` | `string \| null` |  |
| `modifiedTime` | `string \| null` |  |
| `keepForever` | `boolean \| null` |  |
| `published` | `boolean \| null` |  |
| `publishedLink` | `string \| null` |  |
| `publishAuto` | `boolean \| null` |  |
| `publishedOutsideDomain` | `boolean \| null` |  |
| `lastModifyingUser` | `object \| any` |  |
| `originalFilename` | `string \| null` |  |
| `md5Checksum` | `string \| null` |  |
| `size` | `string \| null` |  |
| `exportLinks` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string \| null` |  |

</details>

### Revisions Get

Gets a revision's metadata by ID

#### Python SDK

```python
await google_drive.revisions.get(
    file_id="<str>",
    revision_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "revisions",
    "action": "get",
    "params": {
        "fileId": "<str>",
        "revisionId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fileId` | `string` | Yes | The ID of the file |
| `revisionId` | `string` | Yes | The ID of the revision |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `id` | `string` |  |
| `mimeType` | `string \| null` |  |
| `modifiedTime` | `string \| null` |  |
| `keepForever` | `boolean \| null` |  |
| `published` | `boolean \| null` |  |
| `publishedLink` | `string \| null` |  |
| `publishAuto` | `boolean \| null` |  |
| `publishedOutsideDomain` | `boolean \| null` |  |
| `lastModifyingUser` | `object \| any` |  |
| `originalFilename` | `string \| null` |  |
| `md5Checksum` | `string \| null` |  |
| `size` | `string \| null` |  |
| `exportLinks` | `object \| null` |  |


</details>

## Changes

### Changes List

Lists the changes for a user or shared drive

#### Python SDK

```python
await google_drive.changes.list(
    page_token="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "changes",
    "action": "list",
    "params": {
        "pageToken": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `pageToken` | `string` | Yes | Token for the page of changes to retrieve (from changes.getStartPageToken or previous response) |
| `pageSize` | `integer` | No | Maximum number of changes to return (1-1000) |
| `driveId` | `string` | No | The shared drive from which changes are returned |
| `includeItemsFromAllDrives` | `boolean` | No | Whether to include changes from all drives |
| `supportsAllDrives` | `boolean` | No | Whether the requesting application supports both My Drives and shared drives |
| `spaces` | `string` | No | Comma-separated list of spaces to query |
| `includeRemoved` | `boolean` | No | Whether to include changes indicating that items have been removed |
| `restrictToMyDrive` | `boolean` | No | Whether to restrict the results to changes inside the My Drive hierarchy |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `removed` | `boolean \| null` |  |
| `file` | `object \| any` |  |
| `fileId` | `string \| null` |  |
| `driveId` | `string \| null` |  |
| `drive` | `object \| any` |  |
| `time` | `string \| null` |  |
| `type` | `string \| null` |  |
| `changeType` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string \| null` |  |
| `newStartPageToken` | `string \| null` |  |

</details>

## Changes Start Page Token

### Changes Start Page Token Get

Gets the starting pageToken for listing future changes

#### Python SDK

```python
await google_drive.changes_start_page_token.get()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "changes_start_page_token",
    "action": "get"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `driveId` | `string` | No | The ID of the shared drive for which the starting pageToken is returned |
| `supportsAllDrives` | `boolean` | No | Whether the requesting application supports both My Drives and shared drives |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `startPageToken` | `string` |  |


</details>

## About

### About Get

Gets information about the user, the user's Drive, and system capabilities

#### Python SDK

```python
await google_drive.about.get()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "about",
    "action": "get"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fields` | `string` | No | Fields to include in the response (use * for all fields) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `kind` | `string \| null` |  |
| `user` | `object \| any` |  |
| `storageQuota` | `object \| null` |  |
| `importFormats` | `object \| null` |  |
| `exportFormats` | `object \| null` |  |
| `maxImportSizes` | `object \| null` |  |
| `maxUploadSize` | `string \| null` |  |
| `appInstalled` | `boolean \| null` |  |
| `folderColorPalette` | `array \| null` |  |
| `driveThemes` | `array \| null` |  |
| `canCreateDrives` | `boolean \| null` |  |
| `canCreateTeamDrives` | `boolean \| null` |  |
| `teamDriveThemes` | `array \| null` |  |


</details>

