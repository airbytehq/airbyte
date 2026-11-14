import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Todoist Migration Guide

## Upgrading to 0.4.0

Todoist retired its REST API v2 (`https://api.todoist.com/rest/v2`). Every request to it now returns `HTTP 410 Gone` with the body "This endpoint is deprecated", so all versions of this connector before 0.4.0 fail on every sync and on every connection test.

Version 0.4.0 reads the `tasks` and `projects` streams from the [Todoist API v1](https://developer.todoist.com/api/v1/) (`https://api.todoist.com/api/v1`) instead, using its cursor-based pagination. Your existing API token keeps working; no configuration change is needed.

This is a breaking change because Todoist API v1 returns the records in a different shape:

- **New ID format.** `id`, `project_id`, `section_id`, `parent_id` and user IDs are the new Todoist v1 identifiers, which are different values from the numeric-string IDs returned by REST API v2. Rows synced before the upgrade cannot be joined to rows synced after it. Todoist offers an [ID mappings endpoint](https://developer.todoist.com/api/v1/#tag/Ids) to translate old IDs to new ones if you need to reconcile historical data.
- **Renamed and removed fields** (listed below).

### Field changes in `tasks`

| REST API v2 field | API v1 field |
| :-- | :-- |
| `is_completed` | `checked` |
| `comment_count` | `note_count` |
| `created_at` | `added_at` |
| `creator_id` | `added_by_uid` |
| `assignee_id` | `responsible_uid` |
| `assigner_id` | `assigned_by_uid` |
| `order` | `child_order` |
| `duration` (string) | `duration` (object with `amount` and `unit`) |
| `url` | removed |

New fields: `user_id`, `deadline`, `is_deleted`, `is_collapsed`, `completed_at`, `completed_by_uid`, `updated_at`, `order_key`, `day_order`, `completed_count`, `postponed_count`.

### Field changes in `projects`

| REST API v2 field | API v1 field |
| :-- | :-- |
| `is_inbox_project` | `inbox_project` |
| `order` | `child_order` |
| `comment_count` | removed |
| `is_team_inbox` | removed |
| `url` | removed |

New fields: `description`, `order_key`, `is_collapsed`, `is_archived`, `is_deleted`, `is_frozen`, `can_assign_tasks`, `can_comment`, `creator_uid`, `created_at`, `updated_at`, `default_order`, `default_order_key`, `public_key`, `access`, `role`, and, for workspace projects, `workspace_id`, `folder_id`, `status`, `collaborator_role_default`, `is_invite_only`, `is_link_sharing_enabled`, `is_pending_default_collaborator_invites`, `is_project_insights_enabled`.

### Who is affected

All users of this connector. Both streams are affected, and syncs on versions before 0.4.0 are already failing because the upstream API no longer exists.

### Migration steps

1. Upgrade the connector to 0.4.0.
2. Open each Todoist connection, go to **Schema** and click **Refresh source schema**, then save the connection.
3. Clear the `tasks` and `projects` streams so the destination tables are rebuilt with the new schema and IDs.
4. Run a sync.
5. Update downstream queries that reference renamed or removed columns (see the tables above) or that join on Todoist IDs.

## Connector upgrade guide

<MigrationGuide />
