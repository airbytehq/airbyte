# Config Database: connections and syncs

### `connection`

| Column Name            | Datatype  | Description                                        |
| ---------------------- | --------- | -------------------------------------------------- |
| id                     | UUID      | Primary key. Unique identifier for the connection. |
| namespace_definition  | ENUM      | Defines how the namespace is set.                  |
| namespace_format      | VARCHAR   | Format for the namespace when using `custom`.      |
| prefix                 | VARCHAR   | Prefix added to destination tables.                |
| source_id             | UUID      | Foreign key referencing `actor(id)`.               |
| destination_id        | UUID      | Foreign key referencing `actor(id)`.               |
| name                   | VARCHAR   | Name of the connection.                            |
| catalog                | JSONB     | JSON blob defining the connection catalog.         |
| status                 | ENUM      | Connection status (`active`, `inactive`, etc.).    |
| schedule               | JSONB     | JSON blob defining the connection schedule.        |
| manual                 | BOOLEAN   | Indicates if the connection runs manually.         |
| resource_requirements | JSONB     | Resource requirements for the connection.          |
| created_at            | TIMESTAMP | Timestamp when the record was created.             |
| updated_at            | TIMESTAMP | Timestamp when the record was last modified.       |

#### Indexes and Constraints
- Primary Key: (`id`)
- Foreign Key: `source_id` references `actor(id)`
- Foreign Key: `destination_id` references `actor(id)`
- Index: `connection_source_id_idx` on (`source_id`)
- Index: `connection_destination_id_idx` on (`destination_id`)

---


### `connection_operation`

| Column Name    | Datatype  | Description                                    |
| -------------- | --------- | ---------------------------------------------- |
| id             | UUID      | Primary key. Unique identifier for the record. |
| connection_id | UUID      | Foreign key referencing `connection(id)`.      |
| operation_id  | UUID      | Foreign key referencing `operation(id)`.       |
| created_at    | TIMESTAMP | Timestamp when the record was created.         |
| updated_at    | TIMESTAMP | Timestamp when the record was last modified.   |

#### Indexes and Constraints

- Primary Key: (`id`, `connection_id`, `operation_id`)
- Foreign Key: `connection_id` references `connection(id)`
- Foreign Key: `operation_id` references `operation(id)`
- Index: `connection_operation_connection_id_idx` on (`connection_id`)

---


### `connection_tag`

| Column Name    | Datatype  | Description                                      |
| -------------- | --------- | ------------------------------------------------ |
| id             | UUID      | Primary key. Unique identifier for the record.   |
| tag_id         | UUID      | Foreign key referencing `tag(id)`.               |
| connection_id  | UUID      | Foreign key referencing `connection(id)`.        |
| created_at     | TIMESTAMP | Timestamp when the record was created.           |
| updated_at     | TIMESTAMP | Timestamp when the record was last modified.     |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `tag_id` references `tag(id)`
- Foreign Key: `connection_id` references `connection(id)`
- Unique Constraint: (`tag_id`, `connection_id`)

---


### `connection_timeline_event`

| Column Name   | Datatype  | Description                                         |
| ------------- | --------- | --------------------------------------------------- |
| id            | UUID      | Primary key. Unique identifier for the event.       |
| connection_id | UUID      | Foreign key referencing `connection(id)`.           |
| user_id       | UUID      | Foreign key referencing `user(id)`.                 |
| event_type    | VARCHAR   | Type of event that occurred.                        |
| summary       | JSONB     | JSON blob containing event details.                 |
| created_at    | TIMESTAMP | Timestamp when the event occurred.                  |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `connection_id` references `connection(id)`
- Foreign Key: `user_id` references `user(id)`
- Index: `idx_connection_timeline_connection_id` on (`connection_id`, `created_at`, `event_type`)

---


### `notification_configuration`

| Column Name         | Datatype  | Description                                      |
| ------------------- | --------- | ------------------------------------------------ |
| id                 | UUID      | Primary key. Unique identifier for the notification configuration. |
| enabled            | BOOLEAN   | Indicates if the notification is enabled.        |
| notification_type  | ENUM      | Type of notification.                            |
| connection_id      | UUID      | Foreign key referencing `connection(id)`.        |
| created_at         | TIMESTAMP | Timestamp when the record was created.           |
| updated_at         | TIMESTAMP | Timestamp when the record was last modified.     |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `connection_id` references `connection(id)`

---


### `operation`

| Column Name           | Datatype  | Description                                      |
| --------------------- | --------- | ------------------------------------------------ |
| id                    | UUID      | Primary key. Unique identifier for the operation. |
| workspace_id          | UUID      | Foreign key referencing `workspace(id)`.         |
| name                  | VARCHAR   | Name of the operation.                           |
| operator_type         | ENUM      | Type of operator (`dbt`, `normalization`, etc.).|
| operator_normalization | JSONB     | JSON blob defining normalization settings.       |
| operator_dbt          | JSONB     | JSON blob defining dbt settings.                 |
| tombstone             | BOOLEAN   | Indicates if the operation is deleted.           |
| created_at            | TIMESTAMP | Timestamp when the record was created.           |
| updated_at            | TIMESTAMP | Timestamp when the record was last modified.     |
| operator_webhook      | JSONB     | JSON blob defining webhook settings.             |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `workspace_id` references `workspace(id)`

---


### `schema_management`

| Column Name                 | Datatype  | Description                                       |
| --------------------------- | --------- | ------------------------------------------------- |
| id                          | UUID      | Primary key. Unique identifier for schema management. |
| connection_id               | UUID      | Foreign key referencing `connection(id)`.        |
| created_at                  | TIMESTAMP | Timestamp when the record was created.           |
| updated_at                  | TIMESTAMP | Timestamp when the record was last modified.     |
| auto_propagation_status     | ENUM      | Status of automatic schema propagation.          |
| backfill_preference         | ENUM      | User preference for backfill operations.         |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `connection_id` references `connection(id)`
- Index: `connection_idx` on (`connection_id`)

---


### `state`

| Column Name    | Datatype  | Description                                       |
| ------------- | --------- | ------------------------------------------------- |
| id            | UUID      | Primary key. Unique identifier for the state record. |
| connection_id | UUID      | Foreign key referencing `connection(id)`.        |
| state         | JSONB     | JSON blob storing the state information.         |
| created_at    | TIMESTAMP | Timestamp when the record was created.           |
| updated_at    | TIMESTAMP | Timestamp when the record was last modified.     |
| stream_name   | TEXT      | Name of the stream associated with this state.   |
| namespace     | TEXT      | Namespace of the stream.                         |
| type          | ENUM      | Type of state (`STREAM`, `GLOBAL`, `LEGACY`).    |

#### Indexes and Constraints

- Primary Key: (`id`, `connection_id`)
- Foreign Key: `connection_id` references `connection(id)`
- Unique Constraint: (`connection_id`, `stream_name`, `namespace`)

---


### `stream_generation`

| Column Name       | Datatype  | Description                                    |
| ---------------- | --------- | ---------------------------------------------- |
| id              | UUID      | Primary key. Unique identifier for the stream generation record. |
| connection_id   | UUID      | Foreign key referencing `connection(id)`.      |
| stream_name    | VARCHAR   | Name of the stream.                           |
| stream_namespace | VARCHAR | Namespace of the stream.                      |
| generation_id  | BIGINT    | Identifier for the stream generation.         |
| start_job_id   | BIGINT    | Job ID that started this stream generation.   |
| created_at     | TIMESTAMP | Timestamp when the record was created.        |
| updated_at     | TIMESTAMP | Timestamp when the record was last modified.  |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `connection_id` references `connection(id)`
- Index: `stream_generation_connection_id_stream_name_generation_id_idx` on (`connection_id`, `stream_name`, `generation_id`)
- Index: `stream_generation_connection_id_stream_name_stream_namespace_idx` on (`connection_id`, `stream_name`, `stream_namespace`, `generation_id`)

---


### `stream_refreshes`

| Column Name       | Datatype  | Description                                    |
| ---------------- | --------- | ---------------------------------------------- |
| id              | UUID      | Primary key. Unique identifier for the stream refresh record. |
| connection_id   | UUID      | Foreign key referencing `connection(id)`.      |
| stream_name    | VARCHAR   | Name of the stream.                           |
| stream_namespace | VARCHAR | Namespace of the stream.                      |
| created_at     | TIMESTAMP | Timestamp when the record was created.        |
| refresh_type   | ENUM      | Type of refresh operation performed.          |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `connection_id` references `connection(id)`
- Index: `stream_refreshes_connection_id_idx` on (`connection_id`)
- Index: `stream_refreshes_connection_id_stream_name_idx` on (`connection_id`, `stream_name`)
- Index: `stream_refreshes_connection_id_stream_name_stream_namespace_idx` on (`connection_id`, `stream_name`, `stream_namespace`)

---


### `stream_reset`

| Column Name       | Datatype  | Description                                    |
| ---------------- | --------- | ---------------------------------------------- |
| id              | UUID      | Primary key. Unique identifier for the stream reset record. |
| connection_id   | UUID      | Foreign key referencing `connection(id)`.      |
| stream_namespace | TEXT     | Namespace of the stream.                      |
| stream_name    | TEXT      | Name of the stream being reset.                |
| created_at     | TIMESTAMP | Timestamp when the record was created.        |
| updated_at     | TIMESTAMP | Timestamp when the record was last modified.  |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `connection_id` references `connection(id)`
- Unique Constraint: (`connection_id`, `stream_name`, `stream_namespace`)
- Index: `connection_id_stream_name_namespace_idx` on (`connection_id`, `stream_name`, `stream_namespace`)

---


### `tag`

| Column Name   | Datatype  | Description                                        |
| ------------ | --------- | -------------------------------------------------- |
| id           | UUID      | Primary key. Unique identifier for the tag.        |
| workspace_id | UUID      | Foreign key referencing `workspace(id)`.           |
| name         | VARCHAR   | Name of the tag.                                   |
| color        | CHAR(6)   | Hexadecimal color code for the tag.                |
| created_at   | TIMESTAMP | Timestamp when the record was created.             |
| updated_at   | TIMESTAMP | Timestamp when the record was last modified.       |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `workspace_id` references `workspace(id)`
- Unique Constraint: (`name`, `workspace_id`)
- Index: `tag_workspace_id_idx` on (`workspace_id`)

---


### `workload`

| Column Name         | Datatype  | Description                                     |
| ------------------ | --------- | ----------------------------------------------- |
| id                | VARCHAR   | Primary key. Unique identifier for the workload. |
| dataplane_id      | VARCHAR   | Identifier for the dataplane handling this workload. |
| status           | ENUM      | Status of the workload (`pending`, `running`, etc.). |
| created_at       | TIMESTAMP | Timestamp when the record was created.          |
| updated_at       | TIMESTAMP | Timestamp when the record was last modified.    |
| last_heartbeat_at | TIMESTAMP | Timestamp of the last heartbeat received.      |
| input_payload    | TEXT      | Payload associated with the workload.           |
| log_path        | TEXT      | Path to logs for the workload.                  |
| geography       | VARCHAR   | Geography associated with the workload.         |
| mutex_key       | VARCHAR   | Mutex key used for workload execution control.  |
| type            | ENUM      | Type of workload being processed.               |
| termination_source | VARCHAR | Source that terminated the workload.            |
| termination_reason | TEXT    | Reason for workload termination.                |
| auto_id         | UUID      | Auto-generated identifier for the workload.     |
| deadline        | TIMESTAMP | Deadline for workload execution.                |
| signal_input    | TEXT      | Signal input for the workload.                  |
| dataplane_group | VARCHAR   | Dataplane group associated with the workload.   |
| priority        | INT       | Priority level of the workload.                 |

#### Indexes and Constraints

- Primary Key: (`id`)
- Index: `active_workload_by_mutex_idx` on (`mutex_key`) where (`status` is active)
- Index: `workload_deadline_idx` on (`deadline`) where (`deadline IS NOT NULL`)
- Index: `workload_mutex_idx` on (`mutex_key`)
- Index: `workload_status_idx` on (`status`)

---


### `workload_label`

| Column Name    | Datatype  | Description                                    |
| -------------- | --------- | ---------------------------------------------- |
| id             | UUID      | Primary key. Unique identifier for the label. |
| workload_id    | VARCHAR   | Foreign key referencing `workload(id)`.       |
| key           | VARCHAR   | Label key.                                    |
| value         | VARCHAR   | Label value.                                  |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `workload_id` references `workload(id)`
- Unique Constraint: (`workload_id`, `key`)
- Index: `workload_label_workload_id_idx` on (`workload_id`)

---
