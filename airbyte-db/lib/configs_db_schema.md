# Configs Database Schema Draft

This is a temporarily file that documents the design of the new configs database. Currently everything lives in the `airbyte_configs` table. We want to normalize it to one table per config type. Relevant issue: [#5479](https://github.com/airbytehq/airbyte/issues/5479).

## Convention
- The tables are as similar to the YAML definition as possible.
  - Table names are in snake case and singular form.
  - Column names are in snake case.
- Use ANSI SQL as much as possible so that we are not locked in Postgres.
  - Each table has an `id` column as the primary key. Its type is `nchar(36)`. The `UUID` type is not used because UUID is not a standard SQL type.
  - String columns are `varchar(255)` by default.
  - Enum type is not used, because it is not a standard SQL type. It is replaced with `varchar(50)`.
    - Also modifying enum columns in Postgres requires a migration, and there is no easy way to check if an enum already exists.
    - We already maintain enums in Java. There is no need to go through all the trouble to do that in the database again.
- Assign default column values whenever possible.
- Foreign keys will be added to relevant tables.
  - The major benefit is that jOOQ can leverage that to generate convenient helper methods to create and query associated records.
  - The downside is that config import will be tricky. But the config import system will be broken as we add more Flyway migrations, and needs to be redesigned anyway.
  - Foreign key columns are named as `<parent_table_name>_id`. They are always indexed.
  - If the referenced table is polymorphic, the foreign key is broken down into two columns: `owner_type` and `owner_id`.
- For complex properties, the properties will be expanded to its own table.
  - The property table is named as `<parent_table_name>_<property_name>`. For example, `WORKSPACE_NOTIFICATION` specifies the notifications for a `WORKSPACE`.
- Use Table-per-Type to implement table inheritance.
  - Comparison with other approaches: https://stackoverflow.com/a/3579462
  - There is a `<base_table_name>_type` column in the base table so that it is easy to know which child table to query. This column is indexed.
  - The child table has 1:1 mapping with the base table. This is enforced by a unique index on the foreign key in the child table that references the base table.
- Each table has two timestamp columns: `created_at` and `updated_at`.
- Index
  - Single column index is marked with `index`.
  - Composite column index is marked with `composite index` and specified after column definition.

## Open Questions
- Should we keep the `standard` prefix in the table names?
  - Currently, it is removed.
  - Will we ever need non-standard models like custom workspace or custom connector definition?
- Most source and destination tables have exactly the same columns. For example, `SOURCE_DEFINITION` and `DESTINATION_DEFINITION`, `SOURCE_OAUTH_PARAM` and `DESTINATION_OAUTH_PARAM`. Should we merge these tables, and add a `type` column to distinguish the rows?
  - Things to consider
    - Dry-ness: one table is better
    - Query complexity: same
    - Add new columns
      - Separate tables: need to add new columns to both tables.
      - One table: add new columns to one table.
      - One table is better.
  - Do we expect the source and definition models to diverge in the future?
    - If we use one table for both source and definition models, and they diverge in the future, we can use the table-per-type strategy and simply add extra tables for the model that needs extra properties. Still one table is better
  - Based on the above dimensions, I am leaning towards merging the two tables.

## Common Columns
| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| id | char(36) | yes | | Primary key, UUID. |
| created_at | timestamp with time zone | yes | current_timestamp | `current_timestamp` is implemented in most databases. |
| updated_at | timestamp with time zone | yes | current_timestamp | `current_timestamp` is implemented in most databases. |

## Tables

### `STANDARD_WORKSPACE`

YAML [reference](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/StandardWorkspace.yaml)

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| customer_id | char(36) | | | Not a foreign key. |
| name | varchar(255) | yes | | |
| slug | varchar(255) | yes | | |
| email | varchar(255) | | | index |
| initial_setup_complete | boolean | yes | false | |
| anonymous_data_collection | boolean | | true | |
| news | boolean | | false | | |
| security_updates | boolean | | false | |
| display_setup_wizard | boolean | | true | Artem suggested to default this field to `true`. |
| tombstone | boolean | | false | index |

### `WORKSPACE_NOTIFICATION`

YAML reference:
- [Notification](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/Notification.yaml)

This table has many-to-one relationship with the `WORKSPACE` table. One workspace can have multiple notifications.

This is the base table for notifications. Each notification type will have its own child table (e.g. `SLACK_NOTIFICATION`).

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| workspace_id | char(36) | yes | | Foreign key. Index. |
| notification_type | varchar(50) | yes | | Index. String enum: "slack". |
| send_on_success | boolean | | false | index |
| send_on_failure | boolean | | false | index |

### `SLACK_WORKSPACE_NOTIFICATION`

YAML reference:
- [SlackNotificationConfiguration](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/SlackNotificationConfiguration.yaml)

This table has one-to-one relationship with the `WORKSPACE_NOTIFICATION` table. Each `SLACK_WORKSPACE_NOTIFICATION` belongs to one `WORKSPACE_NOTIFICATION`.

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| notification_id | char(36) | yes | | Foreign key. Unique index to enforce 1:1 mapping. |
| webhook | varchar(2048) | yes | | |

### `SOURCE_DEFINITION`

YAML reference:
- [StandardSourceDefinition](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/StandardSourceDefinition.yaml)

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| name | varchar(255) | yes | | |
| docker_repository | varchar(255) | yes | | Index (ideally this should be unique, but we have duplicates for marketing purpose). |
| docker_image_tag | varchar(50) | yes | | |
| documentation_url | varchar(255) | yes | | |
| icon | varchar(63) | | | |

### `SOURCE_CONNECTION`

YAML reference:
- [SourceConnection](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/SourceConnection.yaml)

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| name | varchar(255) | yes | |
| source_definition_id | char(36) | yes | | Foreign key. Index. |
| workspace_id | char(36) | yes | | Foreign key. Index. |
| configuration | jsonb | yes | | Must be a valid json string. |
| tombstone | boolean | | false | index | |

### `DESTINATION_DEFINITON`

YAML reference:
- [StandardDestinationDefinition](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/StandardDestinationDefinition.yaml)

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| name | varchar(255) | yes | | |
| docker_repository | varchar(36) | yes | | Index (ideally this should be unique, but we have duplicates for marketing purpose). |
| docker_image_tag | varchar(63) | yes | | |
| documentation_url | varchar(255) | yes | | |
| icon | varchar(63) | | | |

### `DESTINATION_CONNECTION`

YAML reference:
- [DestinationConnection](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/DestinationConnection.yaml)

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| name | varchar(255) | yes | |
| destination_definition_id | char(36) | yes | | Foreign key. Index. |
| workspace_id | char(36) | yes | | Foreign key. Index. |
| configuration | jsonb | yes | | Must be a valid json string. |
| tombstone | boolean | | false | index | |

### `SYNC`

YAML reference:
- [StandardSync](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/StandardSync.yaml)
- [NamespaceDefinitionType](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/NamespaceDefinitionType.yaml)

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| namespace_type | varchar(50) | yes | | String enum: "source", "destination", "customformat". |
| namespace_format | varchar(255) | | null | E.g. "${SOURCE_NAMESPACE}" |
| prefix | varchar(255) |
| source_id | char(36) | yes | | Foreign key. Index. |
| destination_id | char(36) | yes | | Foreign key. Index. |
| name | varchar(255) | yes | | |
| catalog | jsonb | yes | | |
| status | varchar(50) | yes | "inactive" | |
| schedule_type | varchar(50) | yes | "manual" | Index. String enum: "manual", "periodic_schedule". |

### `PERIODIC_SYNC_SCHEDULE`

- [StandardSync](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/StandardSync.yaml)

This table represents the periodic schedule for a `SYNC` (one-to-one mapping). Each `SYNC` has one `PERIODIC_SCHEDULE` if the `schedule_type` is `periodic_schedule`.

Its name is prefixed with `periodic` because we may have more types of schedules in the future (e.g. `CRON_SCHEDULE`).

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| sync_id | char(36) | yes | | Foreign key. Unique index to enforce 1:1 mapping. |
| time_unit | varchar(50) | yes | | String enum: "minutes", "hours", "days", "weeks", "month". |
| units | integer | yes | | |

### `RESOURCE_REQUIREMENT`

This table has one-to-one mapping with the resource owners: `SYNC`, `SYNC_INPUT`, `NORMALIZATION_INPUT`.

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| resource_owner_type | varchar(50) | yes | | String enum: "sync", "sync_input", "normalization_input". |
| resource_owner_id | char(36) | yes | | Foreign key. Unique composite index. |
| cpu_request | varchar(255) | | | |
| cpu_limit | varchar(255) | | | |
| memory_request | varchar(255) | | | |
| memory_limit | varchar(255) | | | |

Composite index: unique (resource_owner_type, resource_owner_id).

### `SYNC_OPERATION`

YAML reference:
- [StandardSyncOperation](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/StandardSyncOperation.yaml)

This table has many-to-one relationship with the `SYNC` table. Each `SYNC` can have multiple `SYNC_OPERATION`s.

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| workspace_id | char(36) | yes | | Foreign key. Index. |
| name | varchar(255) | yes | | |
| operator_type | varchar(50) | yes | | String enum: "normalization", "dbt". |
| tombstone | boolean | | false | index | |

### `NORMALIZATION_OPERATOR`

YAML reference:
- [OperatorNormalization](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/OperatorNormalization.yaml)

This table has a one-to-one relationship with the `SYNC_OPERATION` table. Each `SYNC_OPERATION` has at most one `NORMALIZATION_OPERATOR`.

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| normalization_type | string | varchar(50) | "basic" | String enum: "basic". |

### `DBT_OPERATOR`

YAML reference:
- [OperatorDbt](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/OperatorDbt.yaml)

This table has a one-to-one relationship with the `SYNC_OPERATION` table. Each `SYNC_OPERATION` has at most one `DBT_OPERATOR`.

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| git_repo_url | varchar(1024) | yes | | |
| git_repo_branch | varchar(255) | | | |
| docker_image | varchar(255) | | | |
| dbt_arguments | varchar(2048) | | | |

### `SOURCE_OAUTH_PARAM`

YAML reference:
- [DestinationOAuthParameter](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/DestinationOAuthParameter.yaml)

Many-to-one relationship with `SOURCE_DEFINITION`. Each `SOURCE_DEFINITION` can have multiple `SOURCE_OAUTH_PARAM`: global or workspace-specific.

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| source_definition_id | char(36) | yes | | Foreign key. Composite index. |
| workspace_id | char(36) | | | Foreign key. Composite index. |
| configuration | jsonb | yes | | |

Composite index: (source_definition_id, workspace_id).

### `DESTINATION_OAUTH_PARAMETER`

YAML reference:
- [DestinationOAuthParameter](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/DestinationOAuthParameter.yaml)

Many-to-one relationship with `DESTINATION_DEFINITION`. Each `DESTINATION_DEFINITION` can have multiple `DESTINATION_OAUTH_PARAM`: global or workspace-specific.

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| destination_definition_id | char(36) | yes | | Foreign key. Composite index. |
| workspace_id | char(36) | | | Foreign key. Composite index. |
| configuration | jsonb | yes | | |

Composite index: (source_definition_id, workspace_id).

### `SYNC_INPUT`

YAML reference:
- [StandardSyncInput](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/StandardSyncInput.yaml)
- [NamespaceDefinitionType](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/NamespaceDefinitionType.yaml)
- [State](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/State.yaml)

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| namespace_type | varchar(50) | yes | | String enum: "source", "destination", "customformat". |
| namespace_format | varchar(255) | | null | E.g. "${SOURCE_NAMESPACE}" |
| prefix | varchar(255) | | | |
| source_configuration | jsonb | yes | | |
| destination_configuration | jsonb | yes | | |
| catalog | jsonb | | | |
| state | jsonb | | | |

### `SYNC_INPUT_OPERATION_SEQUENCE`

YAML reference:
- [StandardSyncInput](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/StandardSyncInput.yaml)

This table specifies the one-to-many relationship between `SYNC_INPUT` and `SYNC_OPERATION`. Each `SYNC_INPUT` can have many `SYNC_OPERATIONS` with a specific order.

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| sync_input_id | char(36) | yes | | Foreign key. Index. |
| sync_operation_id | char(36) | yes | | Foreign key. Index. |
| sequence_order | integer | yes | | Unique composite index. Example: 10, 20, 30. |

Composite index: (sync_input_id, sync_operation_id, sequence_order)

Questions
- Will an operation inside the sequence ever be queried? If not, it may be fine to denormalize the sequence of operations and just store them as an array in `SYNC_INPUT`.

### `NORMALIZATION_INPUT`

YAML reference:
- [NormalizationInput](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/NormalizationInput.yaml)

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| destination_configuration | jsonb | yes | | |
| catalog | jsonb | yes | | |

Questions
- Should this table belong to a `NORMALIZATION_OPERATOR` and have a `normalization_operator_id`?
  - The code logic suggests so.
  - But this reference id property does not exist in `NormalizationInput.yaml`.
  - If it is the case, this table should also be named `NORMALIZATION_OPERATOR_INPUT`.

### `DBT_OPERATOR_INPUT`

YAML reference:
- [OperatorDbtInput](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/OperatorDbtInput.yaml)

Input for `DBT_OPERATOR`.

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| dbt_operator_id | char(36) | | | Foreign key. Unique index. |
| destination_configuration | jsonb | yes | | |

### `SYNC_OUTPUT`

YAML reference:
- Output
  - [StandardSyncOutput](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/StandardSyncOutput.yaml)
  - [ReplicationOutput](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/ReplicationOutput.yaml)
- Summary:
  - [StandardSyncSummary](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/StandardSyncSummary.yaml)
  - [ReplicationAttemptSummary](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/ReplicationAttemptSummary.yaml)
  - The above two models are identical, and merged into the output model.
- [ReplicationStatus](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/ReplicationStatus.yaml)

- This table combines two output config types: `STANDARD_SYNC_OUTPUT` and `REPLICATION_OUTPUT`, because these two types are identical.
- The `STANDARD_SYNC_OUTPUT_SUMMARY` and `REPLICATION_ATTEMPT_SUMMARY` are merged into the output model, since they are also identical, and the output and output summary have a strict one-to-one relationship.
- Questions
  - Currently, why is `STANDARD_SYNC_SUMMARY` defined separately from `STANDARD_SYNC_OUTPUT`? Should I not merge them?

| Column | Type  | Required | Default | Notes |
| ------ | :---: | :---:    | :---:   | ---   |
| output_type | varchar(50) | yes | "standard" | String enum: "standard", "replication". |
| state | jsonb | yes | | | |
| output_catalog | jsonb | yes | | | |
| status | varchar(50) | yes | | | String enum: "completed", "failed", "cancelled". |
| records_synced | bigint | yes | 0 | |
| bytes_synced | bigint | yes | 0 | |
| start_time | bigint | yes | | Timestamp in millis. |
| end_time | bigint | yes | | Timestamp in millis. |
