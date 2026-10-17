# Dropbox source

The Dropbox source connector synchronizes Dropbox file and folder metadata,
change events, File Properties, shared links, shared folders, and shared-folder
access relationships into Airbyte destinations.

This is a community-maintained Airbyte connector. It is not maintained,
sponsored, or endorsed by Dropbox.

## Prerequisites

- A Dropbox account with permission to create or authorize a Dropbox API app.
- A Dropbox app key and either a refresh token (recommended) or a short-lived
  access token for development.
- Access to the folders, shared resources, and Dropbox Business namespaces you
  intend to synchronize.

## Set up a Dropbox app

1. Open the [Dropbox App Console](https://www.dropbox.com/developers/apps) and
   create an app.
2. Select the API access type appropriate for the data you need. An app-folder
   app can access only its app folder; full Dropbox access is required to
   synchronize arbitrary account paths.
3. On the app's **Permissions** tab, enable the scopes required by the streams
   you plan to use:

   | Capability | Required scopes |
   | --- | --- |
   | Connection check, `entries`, `files`, `folders`, and `file_properties` | `account_info.read`, `files.metadata.read` |
   | `shared_links`, `shared_folders`, and `sharing_acl` | Core scopes plus `sharing.read` |
   | Dropbox Business `namespace_selection.mode=all_accessible` | The applicable scopes above plus `team_data.member` |

   Optional permissions remain capability-local. For example, credentials
   without `sharing.read` can still use the core metadata streams.
4. Save the app configuration before authorizing it. Adding a scope in the App
   Console does not add that scope to an already-issued refresh token; authorize
   the app again when its granted scopes change.

For Dropbox Business, use an app and authorization type that supports team
access. Only a team administrator can authorize team-linked access.

## Authentication

### Refresh token with PKCE (recommended)

The connector includes a headless PKCE helper. From the connector directory,
run:

```bash
poetry run python -m source_dropbox.oauth authorize --app-key <APP_KEY>
```

The default `core+sharing` preset requests all user scopes used by this
upstream connector:

```bash
poetry run python -m source_dropbox.oauth authorize \
  --app-key <APP_KEY> \
  --scope-preset core+sharing
```

Use `--scope-preset core` when you do not plan to sync sharing streams. The
helper prints a Dropbox authorization URL, accepts the one-time authorization
code, and returns an Airbyte configuration containing the app key and refresh
token. It does not require a client secret.

Copy the generated App Key and Refresh Token values into the Airbyte UI. The
generated JSON can also be used with the Airbyte API.

Team-linked authorization and `team_data.member` may require the Dropbox
Business authorization flow configured for your app rather than the user-scope
PKCE presets above.

### Access token (development only)

The connector also accepts a manually generated Dropbox access token. This is
intended for local testing because access tokens expire and require manual
replacement. Use refresh-token authentication for production connections.

To generate a development token for manual testing:

1. Open the [Dropbox App Console](https://www.dropbox.com/developers/apps) and
   select or create an app.
2. Enable the scopes required for the streams you plan to test.
3. Open the app's **Settings** or **OAuth** section and generate an access
   token for your own developer account.
4. Configure Airbyte with the generated token:

   ```json
   {
     "credentials": {
       "auth_type": "access_token",
       "access_token": "<TOKEN>"
     }
   }
   ```

This manual token flow is for development and local testing only. For
production or background synchronization, use refresh-token authentication.

## Configuration

| Field | Description | Default |
| --- | --- | --- |
| `credentials` | Dropbox refresh-token or development access-token credentials. | Required |
| `path` | Dropbox folder to synchronize. Use an empty string for the configured Dropbox root. | `""` |
| `recursive` | Include descendants of the configured path. | `true` |
| `include_deleted` | Include deletion events in `entries`. Snapshot streams always exclude deleted metadata. | `true` |
| `team_context` | Optional Dropbox Business member or admin selection. | `{"mode":"none"}` |
| `path_root` | Dropbox Path Root selection. | `{"mode":"default"}` |
| `namespace_selection` | Current, selected, or all accessible namespace traversal. | `{"mode":"current"}` |

## Supported streams

| Stream | Sync modes | Description |
| --- | --- | --- |
| `entries` | Full refresh, incremental | Canonical file, folder, and deletion change stream. |
| `files` | Full refresh | Current live file metadata snapshot. |
| `folders` | Full refresh | Current live folder metadata snapshot. |
| `file_properties` | Full refresh | One record per Dropbox File Property field attached to a file. |
| `shared_links` | Full refresh | In-scope shared-link metadata for file and folder targets. |
| `shared_folders` | Full refresh | Shared folders visible to the selected Dropbox context. |
| `sharing_acl` | Full refresh | Shared-folder user, group, and invitee access relationships. |

Snapshot streams exclude Dropbox `DeletedMetadata`. The `entries` stream emits
deletion records when `include_deleted` is enabled.

## Incremental synchronization

`entries` uses the opaque cursor returned by Dropbox `files/list_folder` and
`files/list_folder/continue`. The cursor is connector state only: it is not a
record field and is not present in the public stream schema.

The connector checkpoints at Dropbox page boundaries. State advances only
after every record in a page has been yielded. If a job fails before the next
state message is accepted by the destination, Airbyte retries from the previous
durable cursor and may replay records. Configure the destination using
`entry_key` as the primary key where deduplication is needed.

An incremental run consumes the saved cursor. A full-refresh run always starts
from the configured root and ignores incoming incremental cursor state. If
Dropbox invalidates a cursor, the connector safely restarts listing from the
root; this can replay the current snapshot.

In multi-namespace mode, `entries` keeps an independent cursor for each
namespace.

## Dropbox Business

### Team context

`team_context.mode` controls which Dropbox Business identity is used:

- `none`: use the current linked account.
- `user`: act as the member specified by `select_user`, using a Dropbox team
  member ID such as `dbmid:...`.
- `admin`: act as the administrator specified by `select_admin`, using a
  Dropbox team member ID such as `dbmid:...`.

The token must be authorized for the chosen team context and endpoint scopes.

### Path Root

`path_root.mode` determines how Dropbox resolves paths:

- `default`: use the SDK's default root behavior.
- `home`: use the selected account's home namespace.
- `root`: use the selected account's account or team root namespace.
- `namespace_id`: use the explicit `namespace_id`.

For `home` and `root`, state is bound to the effective namespace ID returned by
Dropbox, not only the configured mode. Incremental state fails closed if the
member, admin, Path Root mode, or resolved namespace changes.

### Namespace traversal

`namespace_selection.mode` supports:

- `current`: preserve personal-account and single-root behavior.
- `selected`: traverse only the provided `namespace_ids`.
- `all_accessible`: enumerate and traverse every namespace visible to the
  authorized Business context. This requires `team_data.member` and can be
  API-intensive for large teams.

Paths are evaluated relative to each selected namespace root. Records include
`namespace_id` and, when Dropbox returns them, `namespace_name` and
`namespace_type`. Switching between the single-root and multi-namespace state
models requires resetting the existing `entries` state.

## Deletion handling

Dropbox deletions are represented only by `entries`. With `include_deleted`
enabled, a deletion is emitted with its normalized path, an `entry_type` of
`deleted`, and an `operation` of `delete`. The full-refresh snapshot streams
represent current state and do not emit deleted entries.

The connector does not itself delete data in a destination. Destination sync
mode and normalization behavior determine how deletion records are applied.

## Known limitations

- This contribution synchronizes metadata and sharing information only. It does
  not transfer original file bytes or extract document contents.
- Sharing streams are snapshots; Dropbox does not provide a compatible
  incremental cursor for the records emitted by these streams.
- Shared-link URLs are sensitive bearer-like values. Restrict access to tables
  and logs containing them.
- Shared links without a safe Dropbox target path are skipped so records from
  outside the configured root are not leaked.
- Dropbox File Properties are app-scoped. Dropbox exposes property templates
  and associated values only to the app that created those templates. The
  `file_properties` stream therefore inventories properties visible to the
  configured app, not arbitrary properties created by other Dropbox apps.
- `all_accessible` namespace traversal can produce many API requests on large
  Dropbox Business teams.
- The connector does not use Airbyte-managed OAuth in this release.

## Troubleshooting

### Connection check fails

Verify the app key and refresh token, confirm the authorization has not been
revoked, and make sure `account_info.read` is enabled and granted. If you
changed scopes in the App Console, authorize the app again to obtain a token
with the updated grants.

### A sharing stream reports a missing scope

Enable `sharing.read`, authorize the app again, and update the stored refresh
token. Core streams do not require this optional permission.

### Namespace enumeration fails

For `all_accessible`, use a team-linked authorization with
`team_data.member`. Confirm that the selected member or administrator can see
the namespaces being traversed.

### State context does not match the configured root

The connector prevents reuse of Dropbox cursor state under a different member,
admin, Path Root, or namespace model. Reset the stream state only after
confirming the intended new scope; the next run starts a fresh listing.

### File Properties is empty

Confirm that the configured Dropbox app created the relevant property templates
and that values are attached to files inside the configured root. Properties
owned by another Dropbox app are not visible.

## Changelog

| Version | Date | Notes |
| --- | --- | --- |
| 0.1.0 | 2026-09-30 | Initial community release with Dropbox metadata, incremental entries, sharing inventory, File Properties, Dropbox Business context, Path Root, and namespace traversal. |
